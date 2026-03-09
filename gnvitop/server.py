#!/usr/bin/env python3
"""GPU Monitor - Flask server that reads SSH config and queries remote GPUs."""

import getpass
import json
import os
import queue
import re
import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, Response
import paramiko

from . import __version__
from .dashboard import DASHBOARD_HTML

app = Flask(__name__)

SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
SSH_TIMEOUT = 8

# Single combined command: GPU stats + separator + per-process info
# Splitting on ---SEP--- lets us parse both in one SSH round trip
_GPU_QUERY = (
    "nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,"
    "utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>/dev/null"
)
_PROC_QUERY = (
    r"nvidia-smi pmon -c 1 -s m 2>/dev/null | tail -n +3"
    r" | while read gpu pid type mem cmd; do"
    r' if [ "$pid" != "-" ]; then'
    r" user=$(ps -o user= -p $pid 2>/dev/null | tr -d ' ');"
    r' [ "$mem" = "-" ] && mem=0;'
    r' printf "%s,%s,%s,%s\n" "$pid" "$gpu" "$mem" "$user";'
    r" fi; done"
)
COMBINED_CMD = f"{_GPU_QUERY}; echo '---SEP---'; {_PROC_QUERY}"

CURRENT_USER = getpass.getuser()

# System users to filter out from GPU process list
SYSTEM_USERS = frozenset({
    "root", "gdm", "lightdm", "sddm", "nvidia-persistenced",
    "Xorg", "gnome-shell",
})

cache = {"data": [], "last_update": 0}
cache_lock = threading.Lock()
CACHE_TTL = 30

# Background refresh state
_bg_refresh_running = False
_bg_refresh_lock = threading.Lock()


def parse_ssh_config(path):
    """Parse ~/.ssh/config and return a list of hosts."""
    hosts = []
    current = None

    if not os.path.exists(path):
        return hosts

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key_match = re.match(r"^(\w+)\s+(.+)$", line)
            if not key_match:
                continue

            key, value = key_match.group(1), key_match.group(2)

            if key.lower() == "host":
                if "*" in value or "?" in value:
                    current = None
                    continue
                current = {
                    "alias": value,
                    "hostname": None,
                    "user": None,
                    "port": 22,
                    "identity_file": None,
                }
                hosts.append(current)
            elif current is not None:
                if key.lower() == "hostname":
                    current["hostname"] = value
                elif key.lower() == "user":
                    current["user"] = value
                elif key.lower() == "port":
                    current["port"] = int(value)
                elif key.lower() == "identityfile":
                    current["identity_file"] = os.path.expanduser(value)

    return hosts


def _parse_combined_output(output):
    """Split combined command output into GPU lines and process lines."""
    if "---SEP---" in output:
        gpu_part, proc_part = output.split("---SEP---", 1)
    else:
        gpu_part, proc_part = output, ""
    return gpu_part.strip(), proc_part.strip()


def _build_gpus(gpu_part):
    """Parse GPU stats section into a list of GPU dicts."""
    gpus = []
    for line in gpu_part.split("\n"):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 7:
            mem_total = float(parts[2])
            mem_used = float(parts[3])
            mem_free = float(parts[4])
            utilization = float(parts[5])
            gpus.append({
                "index": int(parts[0]),
                "name": parts[1],
                "memory_total_mb": mem_total,
                "memory_used_mb": mem_used,
                "memory_free_mb": mem_free,
                "memory_usage_pct": round(mem_used / mem_total * 100, 1) if mem_total > 0 else 0,
                "gpu_utilization_pct": utilization,
                "temperature_c": float(parts[6]),
                "processes": [],
            })
    return gpus


def query_gpu(host_info):
    """SSH into a host and query GPU information (single round trip)."""
    alias = host_info["alias"]
    hostname = host_info["hostname"] or alias
    user = host_info["user"]
    port = host_info["port"]

    result = {
        "alias": alias,
        "hostname": hostname,
        "user": user or "unknown",
        "port": port,
        "status": "error",
        "error": None,
        "gpus": [],
    }

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": hostname,
            "port": port,
            "username": user,
            "timeout": SSH_TIMEOUT,
            "banner_timeout": SSH_TIMEOUT,
            "auth_timeout": SSH_TIMEOUT,
            "allow_agent": True,
            "look_for_keys": True,
        }
        if host_info.get("identity_file"):
            connect_kwargs["key_filename"] = host_info["identity_file"]

        client.connect(**connect_kwargs)

        # Single exec_command for both GPU stats and process info
        _, stdout, _ = client.exec_command(COMBINED_CMD, timeout=SSH_TIMEOUT)
        output = stdout.read().decode("utf-8").strip()
        client.close()

        gpu_part, proc_part = _parse_combined_output(output)

        if not gpu_part:
            result["status"] = "no_gpu"
            result["error"] = "No NVIDIA GPU found or nvidia-smi not available"
        else:
            gpus = _build_gpus(gpu_part)
            if proc_part:
                _attach_processes(gpus, proc_part)
            result["gpus"] = gpus
            if gpus:
                result["status"] = "ok"
            else:
                result["status"] = "no_gpu"
                result["error"] = "nvidia-smi returned no valid GPU data"

    except paramiko.AuthenticationException:
        result["error"] = "Authentication failed"
    except paramiko.SSHException as e:
        result["error"] = f"SSH error: {e}"
    except TimeoutError:
        result["error"] = "Connection timed out"
    except OSError as e:
        result["error"] = f"Connection failed: {e}"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    return result


def _attach_processes(gpus, proc_output):
    """Parse process output and attach to matching GPUs (skip system users)."""
    gpu_by_index = {g["index"]: g for g in gpus}
    for line in proc_output.split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 4 and parts[0].isdigit():
            user = parts[3] if parts[3] else "unknown"
            if user in SYSTEM_USERS:
                continue
            gpu_idx = int(parts[1])
            proc = {
                "pid": int(parts[0]),
                "gpu_memory_mb": float(parts[2]) if parts[2] else 0,
                "user": user,
            }
            if gpu_idx in gpu_by_index:
                gpu_by_index[gpu_idx]["processes"].append(proc)


def query_local_gpu():
    """Query the local machine for GPU information (single subprocess call)."""
    import socket

    hostname = socket.gethostname()
    result = {
        "alias": "localhost",
        "hostname": hostname,
        "user": CURRENT_USER,
        "port": 0,
        "status": "error",
        "error": None,
        "gpus": [],
        "is_local": True,
    }

    try:
        output = subprocess.run(
            COMBINED_CMD, shell=True, capture_output=True, text=True, timeout=15
        ).stdout.strip()

        gpu_part, proc_part = _parse_combined_output(output)

        if not gpu_part:
            result["status"] = "no_gpu"
            result["error"] = "No NVIDIA GPU found or nvidia-smi not available"
        else:
            gpus = _build_gpus(gpu_part)
            if proc_part:
                _attach_processes(gpus, proc_part)
            result["gpus"] = gpus
            if gpus:
                result["status"] = "ok"
            else:
                result["status"] = "no_gpu"
                result["error"] = "nvidia-smi returned no valid GPU data"

    except FileNotFoundError:
        result["status"] = "no_gpu"
        result["error"] = "nvidia-smi not found"
    except subprocess.TimeoutExpired:
        result["error"] = "nvidia-smi timed out"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    return result


def _sort_results(results):
    order = {"ok": 0, "no_gpu": 1, "error": 2}
    results.sort(key=lambda x: (
        0 if x.get("is_local") else 1,
        order.get(x["status"], 3),
        -len(x.get("gpus", [])),
        x["alias"],
    ))
    return results


def fetch_all_gpu_info():
    """Query all hosts (local + remote) concurrently and return sorted results."""
    hosts = parse_ssh_config(SSH_CONFIG_PATH)
    results = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(query_local_gpu): None}
        for h in hosts:
            futures[executor.submit(query_gpu, h)] = h
        for future in as_completed(futures):
            results.append(future.result())

    return _sort_results(results)


def _do_background_refresh():
    """Run fetch_all_gpu_info and update cache; reset _bg_refresh_running flag when done."""
    global _bg_refresh_running
    try:
        data = fetch_all_gpu_info()
        with cache_lock:
            cache["data"] = data
            cache["last_update"] = time.time()
    finally:
        with _bg_refresh_lock:
            _bg_refresh_running = False


def _trigger_background_refresh():
    """Spawn a background refresh thread if one isn't already running."""
    global _bg_refresh_running
    with _bg_refresh_lock:
        if _bg_refresh_running:
            return
        _bg_refresh_running = True
    t = threading.Thread(target=_do_background_refresh, daemon=True)
    t.start()


def _start_background_warmer():
    """Background thread that keeps cache warm by refreshing every CACHE_TTL seconds."""
    def _warmer():
        # Initial warm-up: start immediately so first page load hits cached data
        _do_background_refresh()
        while True:
            time.sleep(CACHE_TTL)
            _do_background_refresh()

    t = threading.Thread(target=_warmer, daemon=True)
    t.start()


# Start background cache warmer when module is imported
_start_background_warmer()


@app.route("/")
def index():
    return Response(DASHBOARD_HTML, mimetype="text/html")


@app.route("/api/gpus")
def api_gpus():
    """Return cached data immediately; trigger background refresh if cache is stale."""
    now = time.time()
    with cache_lock:
        data = cache["data"]
        last_update = cache["last_update"]

    if now - last_update > CACHE_TTL:
        _trigger_background_refresh()

    return jsonify({"hosts": data, "updated_at": last_update})


@app.route("/api/refresh")
def api_refresh():
    """Force a synchronous refresh and return fresh data."""
    with cache_lock:
        cache["data"] = fetch_all_gpu_info()
        cache["last_update"] = time.time()
        return jsonify({"hosts": cache["data"], "updated_at": cache["last_update"]})


@app.route("/api/stream")
def api_stream():
    """SSE endpoint: streams each host result as it arrives, then a 'done' event."""
    def generate():
        hosts = parse_ssh_config(SSH_CONFIG_PATH)
        results = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(query_local_gpu): None}
            for h in hosts:
                futures[executor.submit(query_gpu, h)] = h

            for future in as_completed(futures):
                host_result = future.result()
                results.append(host_result)
                payload = json.dumps({"host": host_result})
                yield f"data: {payload}\n\n"

        # Update cache with fresh streamed data
        sorted_results = _sort_results(results)
        with cache_lock:
            cache["data"] = sorted_results
            cache["last_update"] = time.time()

        yield f"data: {json.dumps({'done': True, 'updated_at': cache['last_update']})}\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
