#!/usr/bin/env python3
"""GPU Monitor - 读取 SSH config，查询远程主机 GPU 使用情况"""

import os
import re
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, jsonify, send_file
import paramiko

app = Flask(__name__)

SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
SSH_TIMEOUT = 8  # seconds
GPU_QUERY_CMD = "nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>/dev/null"

# Cache
cache = {"data": [], "last_update": 0}
cache_lock = threading.Lock()
CACHE_TTL = 30  # seconds


def parse_ssh_config(path):
    """解析 ~/.ssh/config，返回主机列表"""
    hosts = []
    current = None

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
                # 跳过通配符
                if "*" in value or "?" in value:
                    current = None
                    continue
                current = {"alias": value, "hostname": None, "user": None, "port": 22, "identity_file": None}
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
    """SSH 连接到主机并查询 GPU 信息"""
    alias = host_info["alias"]
    hostname = host_info["hostname"] or alias
    user = host_info["user"]
    port = host_info["port"]

    result = {
        "alias": alias,
        "hostname": hostname,
        "user": user,
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
        err_output = stderr.read().decode("utf-8").strip()

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
                    })
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
        result["error"] = f"SSH error: {str(e)}"
    except TimeoutError:
        result["error"] = "Connection timed out"
    except OSError as e:
        result["error"] = f"Connection failed: {str(e)}"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"

    return result


def fetch_all_gpu_info():
    """并发查询所有主机的 GPU 信息"""
    hosts = parse_ssh_config(SSH_CONFIG_PATH)
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(query_gpu, h): h for h in hosts}
        for future in as_completed(futures):
            results.append(future.result())

    # 按状态排序: ok > no_gpu > error
    order = {"ok": 0, "no_gpu": 1, "error": 2}
    results.sort(key=lambda x: (order.get(x["status"], 3), x["alias"]))
    return results


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/gpus")
def api_gpus():
    now = time.time()
    with cache_lock:
        if now - cache["last_update"] > CACHE_TTL:
            cache["data"] = fetch_all_gpu_info()
            cache["last_update"] = now
        return jsonify({"hosts": cache["data"], "updated_at": cache["last_update"]})


@app.route("/api/refresh")
def api_refresh():
    """强制刷新"""
    with cache_lock:
        cache["data"] = fetch_all_gpu_info()
        cache["last_update"] = time.time()
        return jsonify({"hosts": cache["data"], "updated_at": cache["last_update"]})


if __name__ == "__main__":
    print("GPU Monitor starting on http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
