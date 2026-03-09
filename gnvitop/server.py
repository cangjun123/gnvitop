#!/usr/bin/env python3
"""GPU Monitor - Flask server that reads SSH config and queries remote GPUs."""

import getpass
import os
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
GPU_QUERY_CMD = (
    "nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,"
    "utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>/dev/null"
)
PROCESS_QUERY_CMD = (
    r"nvidia-smi --query-compute-apps=pid,gpu_index,used_gpu_memory "
    r"--format=csv,noheader,nounits 2>/dev/null"
)
# Shell one-liner: for each process line, resolve PID to username via ps
PROCESS_WITH_USER_CMD = (
    PROCESS_QUERY_CMD
    + r" | while IFS=', ' read -r pid gpu mem; do"
    r" user=$(ps -o user= -p $pid 2>/dev/null | tr -d ' ');"
    r' printf "%s,%s,%s,%s\n" "$pid" "$gpu" "$mem" "$user"; done'
)

CURRENT_USER = getpass.getuser()

cache = {"data": [], "last_update": 0}
cache_lock = threading.Lock()
CACHE_TTL = 30


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


def query_gpu(host_info):
    """SSH into a host and query GPU information."""
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

        stdin, stdout, stderr = client.exec_command(GPU_QUERY_CMD, timeout=SSH_TIMEOUT)
        output = stdout.read().decode("utf-8").strip()

        if not output:
            result["status"] = "no_gpu"
            result["error"] = "No NVIDIA GPU found or nvidia-smi not available"
        else:
            gpus = []
            for line in output.split("\n"):
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

            # Query per-GPU processes with usernames
            try:
                _, p_stdout, _ = client.exec_command(
                    PROCESS_WITH_USER_CMD, timeout=SSH_TIMEOUT
                )
                proc_output = p_stdout.read().decode("utf-8").strip()
                if proc_output:
                    _attach_processes(gpus, proc_output)
            except Exception:
                pass  # process info is best-effort

            result["gpus"] = gpus
            if gpus:
                result["status"] = "ok"
            else:
                result["status"] = "no_gpu"
                result["error"] = "nvidia-smi returned no valid GPU data"

        client.close()

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
    """Parse process output and attach to matching GPUs."""
    gpu_by_index = {g["index"]: g for g in gpus}
    for line in proc_output.split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 4 and parts[0].isdigit():
            gpu_idx = int(parts[1])
            proc = {
                "pid": int(parts[0]),
                "gpu_memory_mb": float(parts[2]) if parts[2] else 0,
                "user": parts[3] if parts[3] else "unknown",
            }
            if gpu_idx in gpu_by_index:
                gpu_by_index[gpu_idx]["processes"].append(proc)


def query_local_gpu():
    """Query the local machine for GPU information."""
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
            GPU_QUERY_CMD, shell=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()

        if not output:
            result["status"] = "no_gpu"
            result["error"] = "No NVIDIA GPU found or nvidia-smi not available"
        else:
            gpus = []
            for line in output.split("\n"):
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

            # Query local processes
            try:
                proc_output = subprocess.run(
                    PROCESS_WITH_USER_CMD, shell=True, capture_output=True,
                    text=True, timeout=10
                ).stdout.strip()
                if proc_output:
                    _attach_processes(gpus, proc_output)
            except Exception:
                pass

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


def fetch_all_gpu_info():
    """Query all hosts (local + remote) concurrently."""
    hosts = parse_ssh_config(SSH_CONFIG_PATH)
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit local query
        futures = {executor.submit(query_local_gpu): None}
        # Submit remote queries
        for h in hosts:
            futures[executor.submit(query_gpu, h)] = h
        for future in as_completed(futures):
            results.append(future.result())

    order = {"ok": 0, "no_gpu": 1, "error": 2}
    # Local always first, then sort by status and alias
    results.sort(key=lambda x: (0 if x.get("is_local") else 1, order.get(x["status"], 3), x["alias"]))
    return results


@app.route("/")
def index():
    return Response(DASHBOARD_HTML, mimetype="text/html")


@app.route("/api/gpus")
def api_gpus():
    now = time.time()
    with cache_lock:
        if now - cache["last_update"] > CACHE_TTL:
            cache["data"] = fetch_all_gpu_info()
            cache["last_update"] = now
        return jsonify({
            "hosts": cache["data"],
            "updated_at": cache["last_update"],
            "current_user": CURRENT_USER,
        })


@app.route("/api/refresh")
def api_refresh():
    with cache_lock:
        cache["data"] = fetch_all_gpu_info()
        cache["last_update"] = time.time()
        return jsonify({
            "hosts": cache["data"],
            "updated_at": cache["last_update"],
            "current_user": CURRENT_USER,
        })
