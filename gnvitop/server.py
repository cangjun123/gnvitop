#!/usr/bin/env python3
"""GPU Monitor - Flask server that reads SSH config and queries remote GPUs."""

import base64
import binascii
import getpass
import hashlib
import hmac
import json
import math
import os
import re
import shlex
import socket
import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, request, Response
import paramiko

from . import __version__
from .dashboard import DASHBOARD_HTML
from .history import HistoryStore

app = Flask(__name__)

SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
SERVER_CONFIG_PATH = os.path.expanduser("~/.gnvitop/servers.json")
SECRET_KEY_PATH = os.path.expanduser("~/.gnvitop/.secret")
PASSWORD_ENC_PREFIX = "gnv1:"
HISTORY_PATH = os.path.expanduser("~/.gnvitop/history.jsonl")
SSH_TIMEOUT = 45
DEFAULT_DISK_PATH = "~"
DEFAULT_TUNNEL_PORT = 7890
HISTORY_RETENTION_SECONDS = 7 * 24 * 60 * 60
HISTORY_PRUNE_INTERVAL = 60 * 60
HISTORY_MAX_POINTS = 1200
HISTORY_RANGES = {
    "1h": 60 * 60,
    "6h": 6 * 60 * 60,
    "24h": 24 * 60 * 60,
    "7d": HISTORY_RETENTION_SECONDS,
}
DEFAULT_METRICS = {
    "gpu": True,
    "cpu": True,
    "memory": True,
    "disk": True,
}

# ── nvidia-smi queries ────────────────────────────────────────────────────────
_GPU_QUERY = (
    "nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,"
    "utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>/dev/null"
)
_PROC_QUERY = (
    r"nvidia-smi pmon -c 1 -s m 2>/dev/null | tail -n +3"
    r" | while read gpu pid type mem cmd; do"
    r' if [ "$pid" != "-" ]; then'
    r" user=$(ps -o user= -p $pid 2>/dev/null | tr -d ' ');"
    r" comm=$(ps -o comm= -p $pid 2>/dev/null | tr -d ' ');"
    r' [ "$mem" = "-" ] && mem=0;'
    r' printf "%s,%s,%s,%s,%s\n" "$pid" "$gpu" "$mem" "$user" "$comm";'
    r" fi; done"
)

# ── TPU queries (Google Cloud TPU) ───────────────────────────────────────────
_TPU_CHIP_QUERY = "ls /dev/accel* 2>/dev/null | wc -l"
_TPU_PROC_QUERY = (
    "ps -eo pid,user,comm 2>/dev/null"
    " | awk 'NR>1 && /python/ && !/awk/ {print $1\",0,0,\"$2\",\"$3}'"
    " | head -10"
)

# ── mx-smi queries (沐曦 MetaX GPUs) ─────────────────────────────────────────
_MX_PROC_QUERY = (
    r"mx-smi --show-all-process 2>/dev/null"
    r" | grep -E '^\|[[:space:]]+[0-9]'"
    r" | sed 's/|//g'"
    r" | awk '{print $1, $2, $NF}'"
    r" | while read gpu_idx pid mem; do"
    r' if [ -n "$pid" ]; then'
    r" user=$(ps -o user= -p $pid 2>/dev/null | tr -d ' ');"
    r' printf "%s,%s,%s,%s\n" "$gpu_idx" "$pid" "$mem" "$user";'
    r" fi; done"
)

# ── Auto-detect: try nvidia-smi first, fall back to mx-smi ───────────────────
# Output begins with "NVIDIA\n" or "MX\n" so the parser knows which format follows
COMBINED_CMD = (
    "if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then "
    "echo NVIDIA; " + _GPU_QUERY + "; echo '---SEP---'; " + _PROC_QUERY + "; "
    "elif command -v mx-smi >/dev/null 2>&1; then "
    "echo MX; mx-smi 2>/dev/null; echo '---SEP---'; " + _MX_PROC_QUERY + "; "
    "elif ls /dev/accel0 >/dev/null 2>&1; then "
    "echo TPU; " + _TPU_CHIP_QUERY + "; echo '---SEP---'; " + _TPU_PROC_QUERY + "; "
    "fi"
)

SYSTEM_CMD = r"""
read cpu a b c d e f g h i j < /proc/stat
total1=$((a+b+c+d+e+f+g+h+i+j)); idle1=$((d+e))
sleep 0.2
read cpu a b c d e f g h i j < /proc/stat
total2=$((a+b+c+d+e+f+g+h+i+j)); idle2=$((d+e))
dt=$((total2-total1)); di=$((idle2-idle1))
cpu_pct=$(awk -v dt="$dt" -v di="$di" 'BEGIN{ if (dt > 0) printf "%.1f", (1 - di/dt) * 100; else printf "0.0" }')
cores=$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 0)
read load1 load5 load15 rest < /proc/loadavg
mem_total=$(awk '/^MemTotal:/ {printf "%.0f", $2*1024}' /proc/meminfo)
mem_avail=$(awk '/^MemAvailable:/ {printf "%.0f", $2*1024}' /proc/meminfo)
mem_used=$((mem_total-mem_avail))
mem_pct=$(awk -v used="$mem_used" -v total="$mem_total" 'BEGIN{ if (total > 0) printf "%.1f", used/total*100; else printf "0.0" }')
json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
configured_disk_path="${GNVITOP_DISK_PATH:-~}"
home_dir=$(cd ~ 2>/dev/null && pwd || echo "$HOME")
case "$configured_disk_path" in
  ""|"~") disk_path="$home_dir" ;;
  "~/"*) disk_path="${home_dir}/${configured_disk_path#~/}" ;;
  *) disk_path="$configured_disk_path" ;;
esac
disk_line=$(df -B1 -P "$disk_path" 2>/dev/null | tail -1)
disk_total=$(echo "$disk_line" | awk '{print $2}')
disk_used=$(echo "$disk_line" | awk '{print $3}')
disk_free=$(echo "$disk_line" | awk '{print $4}')
disk_mount=$(echo "$disk_line" | awk '{print $6}')
[ -z "$disk_total" ] && disk_total=0
[ -z "$disk_used" ] && disk_used=0
[ -z "$disk_free" ] && disk_free=0
[ -z "$disk_mount" ] && disk_mount="$disk_path"
disk_pct=$(awk -v used="$disk_used" -v total="$disk_total" 'BEGIN{ if (total > 0) printf "%.1f", used/total*100; else printf "0.0" }')
disk_mount_json=$(json_escape "$disk_mount")
disk_path_json=$(json_escape "$disk_path")
printf '{"cpu":{"usage_pct":%s,"cores":%s,"load1":%s,"load5":%s,"load15":%s},"memory":{"total_bytes":%s,"used_bytes":%s,"available_bytes":%s,"usage_pct":%s},"disk":{"mount":"%s","path":"%s","total_bytes":%s,"used_bytes":%s,"free_bytes":%s,"usage_pct":%s}}\n' "$cpu_pct" "$cores" "$load1" "$load5" "$load15" "$mem_total" "$mem_used" "$mem_avail" "$mem_pct" "$disk_mount_json" "$disk_path_json" "$disk_total" "$disk_used" "$disk_free" "$disk_pct"
"""

CURRENT_USER = getpass.getuser()

# System users to filter out from GPU process list
SYSTEM_USERS = frozenset({
    "root", "gdm", "lightdm", "sddm", "nvidia-persistenced",
    "Xorg", "gnome-shell",
})

cache = {"data": [], "last_update": 0}
cache_lock = threading.Lock()
CACHE_TTL = 30
history_lock = threading.Lock()
_history_store = None

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
                    "proxy_jump": None,
                    "proxy_command": None,
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
                elif key.lower() == "proxyjump":
                    # Take only the first jump host (chained jumps not supported)
                    current["proxy_jump"] = value.split(",")[0].strip()
                elif key.lower() == "proxycommand":
                    current["proxy_command"] = value

    return hosts


def _normalize_disk_path(disk_path):
    value = str(disk_path or "").strip()
    return value or DEFAULT_DISK_PATH


def _normalize_host_config(host, default_disk_path=DEFAULT_DISK_PATH, default_metrics=None):
    """Return a sanitized host config dict with stable keys."""
    alias = str(host.get("alias") or "").strip()
    hostname = str(host.get("hostname") or alias).strip()
    if not alias:
        alias = hostname
    try:
        port = int(host.get("port") or 22)
    except (TypeError, ValueError):
        port = 22
    try:
        tunnel_port = int(host.get("tunnel_port") or DEFAULT_TUNNEL_PORT)
    except (TypeError, ValueError):
        tunnel_port = DEFAULT_TUNNEL_PORT
    tunnel_port = min(max(tunnel_port, 1), 65535)
    identity_file = host.get("identity_file") or None
    if identity_file:
        identity_file = os.path.expanduser(str(identity_file))
    host_metrics = host.get("metrics")
    return {
        "alias": alias,
        "hostname": hostname,
        "user": str(host.get("user") or "").strip() or None,
        "port": port,
        "identity_file": identity_file,
        "password": host.get("password") or None,
        "proxy_jump": str(host.get("proxy_jump") or "").strip() or None,
        "proxy_command": str(host.get("proxy_command") or "").strip() or None,
        "enabled": bool(host.get("enabled", True)),
        "disk_path": _normalize_disk_path(host.get("disk_path", default_disk_path)),
        "metrics": _normalize_metrics(host_metrics if host_metrics is not None else default_metrics),
        "tunnel_enabled": bool(host.get("tunnel_enabled", False)),
        "tunnel_port": tunnel_port,
    }


def _dedupe_hosts(hosts, default_disk_path=DEFAULT_DISK_PATH, default_metrics=None):
    deduped = []
    seen = set()
    for host in hosts:
        normalized = _normalize_host_config(host, default_disk_path, default_metrics)
        alias = normalized["alias"]
        if not alias or alias in seen:
            continue
        seen.add(alias)
        deduped.append(normalized)
    return deduped


def _normalize_metrics(metrics):
    source = metrics if isinstance(metrics, dict) else {}
    return {key: bool(source.get(key, default)) for key, default in DEFAULT_METRICS.items()}


def _load_secret_key():
    """Load (or create) the local key file used to encrypt stored passwords."""
    try:
        with open(SECRET_KEY_PATH, "rb") as f:
            key = f.read()
        if len(key) >= 32:
            return key
    except OSError:
        pass
    key = os.urandom(32)
    os.makedirs(os.path.dirname(SECRET_KEY_PATH), exist_ok=True)
    with open(SECRET_KEY_PATH, "wb") as f:
        f.write(key)
    try:
        os.chmod(SECRET_KEY_PATH, 0o600)
    except OSError:
        pass
    return key


def _encrypt_password(plain):
    """Encrypt a password for at-rest storage (stdlib-only, local key file)."""
    if not plain or plain.startswith(PASSWORD_ENC_PREFIX):
        return plain
    key = _load_secret_key()
    data = plain.encode("utf-8")
    nonce = os.urandom(16)
    stream = hashlib.pbkdf2_hmac("sha256", key, nonce, 1000, dklen=len(data))
    ciphertext = bytes(a ^ b for a, b in zip(data, stream))
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return (
        PASSWORD_ENC_PREFIX
        + base64.urlsafe_b64encode(nonce).decode() + ":"
        + base64.urlsafe_b64encode(ciphertext).decode() + ":"
        + base64.urlsafe_b64encode(tag).decode()
    )


def _decrypt_password(token):
    """Decrypt a stored password token; returns None if it cannot be recovered.

    Non-token input (plaintext from imports) is passed through unchanged.
    """
    if not token or not token.startswith(PASSWORD_ENC_PREFIX):
        return token or None
    try:
        _, nonce_b64, ciphertext_b64, tag_b64 = token.split(":")
        nonce = base64.urlsafe_b64decode(nonce_b64)
        ciphertext = base64.urlsafe_b64decode(ciphertext_b64)
        tag = base64.urlsafe_b64decode(tag_b64)
    except (ValueError, binascii.Error):
        return None
    key = _load_secret_key()
    expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, tag):
        return None
    stream = hashlib.pbkdf2_hmac("sha256", key, nonce, 1000, dklen=len(ciphertext))
    return bytes(a ^ b for a, b in zip(ciphertext, stream)).decode("utf-8", errors="replace")


def _config_payload(hosts, monitor_local=True, metrics=None, local_disk_path=DEFAULT_DISK_PATH):
    normalized_metrics = _normalize_metrics(metrics)
    return {
        "version": 1,
        "imported_from_ssh": True,
        "ssh_config_path": SSH_CONFIG_PATH,
        "monitor_local": bool(monitor_local),
        "metrics": normalized_metrics,
        "local_disk_path": _normalize_disk_path(local_disk_path),
        "hosts": _dedupe_hosts(hosts, default_metrics=normalized_metrics),
    }


def save_server_config(hosts, monitor_local=True, metrics=None, local_disk_path=DEFAULT_DISK_PATH):
    payload = _config_payload(hosts, monitor_local, metrics, local_disk_path)
    for host in payload["hosts"]:
        # Never write passwords to disk in plaintext.
        host["password"] = _encrypt_password(host.get("password"))
    os.makedirs(os.path.dirname(SERVER_CONFIG_PATH), exist_ok=True)
    with open(SERVER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def save_config_payload(payload):
    """Persist an imported config payload after normalization."""
    if not isinstance(payload, dict):
        raise ValueError("config payload must be an object")
    hosts = payload.get("hosts", [])
    if not isinstance(hosts, list):
        raise ValueError("hosts must be a list")
    monitor_local = bool(payload.get("monitor_local", True))
    metrics = _normalize_metrics(payload.get("metrics"))
    local_disk_path = _normalize_disk_path(
        payload.get("local_disk_path", payload.get("disk_path", DEFAULT_DISK_PATH))
    )
    save_server_config(hosts, monitor_local, metrics, local_disk_path)


def load_config_payload():
    """Load full managed config payload, importing ~/.ssh/config on first run."""
    if not os.path.exists(SERVER_CONFIG_PATH):
        hosts = parse_ssh_config(SSH_CONFIG_PATH)
        payload = _config_payload(
            hosts,
            monitor_local=True,
            metrics=DEFAULT_METRICS,
            local_disk_path=DEFAULT_DISK_PATH,
        )
        save_server_config(
            payload["hosts"],
            payload["monitor_local"],
            payload["metrics"],
            payload["local_disk_path"],
        )
        return payload

    try:
        with open(SERVER_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    legacy_disk_path = data.get("disk_path", DEFAULT_DISK_PATH)
    local_disk_path = data.get("local_disk_path", legacy_disk_path)
    metrics = _normalize_metrics(data.get("metrics"))
    hosts = _dedupe_hosts(
        data.get("hosts", []),
        default_disk_path=legacy_disk_path,
        default_metrics=metrics,
    )
    for host in hosts:
        if host.get("password"):
            # Decrypt into memory for use; returns None if unrecoverable.
            host["password"] = _decrypt_password(host["password"])
    return {
        "version": data.get("version", 1),
        "imported_from_ssh": data.get("imported_from_ssh", True),
        "ssh_config_path": data.get("ssh_config_path", SSH_CONFIG_PATH),
        "monitor_local": bool(data.get("monitor_local", True)),
        "metrics": metrics,
        "local_disk_path": _normalize_disk_path(local_disk_path),
        "hosts": hosts,
    }


def load_server_config():
    """Load managed server config, importing ~/.ssh/config on first run."""
    return load_config_payload()["hosts"]


def get_monitor_local():
    return load_config_payload()["monitor_local"]


def get_metric_config():
    return load_config_payload()["metrics"]


def get_local_disk_path_config():
    return load_config_payload()["local_disk_path"]


def _host_endpoint_key(host):
    normalized = _normalize_host_config(host)
    hostname = (normalized.get("hostname") or normalized.get("alias") or "").lower()
    return f"{hostname}:{normalized.get('port', 22)}"


def import_ssh_hosts(replace=False):
    """Import hosts from SSH config into managed config."""
    payload = load_config_payload()
    monitor_local = payload["monitor_local"]
    metrics = payload["metrics"]
    local_disk_path = payload["local_disk_path"]
    imported = _dedupe_hosts(parse_ssh_config(SSH_CONFIG_PATH), default_metrics=metrics)
    if replace:
        save_server_config(imported, monitor_local, metrics, local_disk_path)
        return imported

    existing = load_server_config()
    endpoints = {_host_endpoint_key(h) for h in existing}
    merged = existing + [h for h in imported if _host_endpoint_key(h) not in endpoints]
    save_server_config(merged, monitor_local, metrics, local_disk_path)
    return merged


def public_host_config(host):
    """Expose config to UI. Password is intentionally not returned."""
    data = dict(_normalize_host_config(host))
    data["has_password"] = bool(data.get("password"))
    data.pop("password", None)
    return data


def _invalidate_cache():
    """Mark cache stale without clearing it.

    Keeping the previous data means /api/gpus keeps returning a full host
    list (with stale readings) until the background refresh lands, instead
    of an empty list that would blank the dashboard.
    """
    with cache_lock:
        cache["last_update"] = 0


def _parse_combined_output(output):
    """Split combined command output into (gpu_part, proc_part, vendor).

    Output may begin with 'NVIDIA', 'MX', or 'TPU' to indicate accelerator vendor.
    Returns vendor as one of: 'nvidia', 'mx', 'tpu'.
    """
    vendor = "nvidia"
    lines = output.split("\n")
    if lines and lines[0].strip() == "MX":
        vendor = "mx"
        output = "\n".join(lines[1:])
    elif lines and lines[0].strip() == "NVIDIA":
        output = "\n".join(lines[1:])
    elif lines and lines[0].strip() == "TPU":
        vendor = "tpu"
        output = "\n".join(lines[1:])

    if "---SEP---" in output:
        gpu_part, proc_part = output.split("---SEP---", 1)
    else:
        gpu_part, proc_part = output, ""
    return gpu_part.strip(), proc_part.strip(), vendor


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


def _build_mx_gpus(output):
    """Parse default mx-smi table output into GPU dicts.

    Each GPU occupies two adjacent table rows, e.g.:
      | 0       MetaX C500  Off | 0000:0e:00.0 | 0%  Native |
      | 36C  56W / 350W  P0     | 858/65536 MiB | Available  |
    """
    import re
    gpus = []
    lines = output.split("\n")
    # Row 1: index, name, utilisation
    row1_re = re.compile(
        r"\|\s*(\d+)\s+([\w ]+?)\s+(?:Off|On)\s*\|[^|]+\|\s*(\d+)%"
    )
    # Row 2: temperature, mem_used / mem_total MiB
    row2_re = re.compile(
        r"\|\s*(\d+(?:\.\d+)?)C\s+[^|]+\|\s*(\d+)/(\d+)\s+MiB"
    )
    i = 0
    while i < len(lines):
        m1 = row1_re.search(lines[i])
        if m1 and i + 1 < len(lines):
            m2 = row2_re.search(lines[i + 1])
            if m2:
                mem_used = float(m2.group(2))
                mem_total = float(m2.group(3))
                gpus.append({
                    "index": int(m1.group(1)),
                    "name": m1.group(2).strip(),
                    "memory_total_mb": mem_total,
                    "memory_used_mb": mem_used,
                    "memory_free_mb": mem_total - mem_used,
                    "memory_usage_pct": round(mem_used / mem_total * 100, 1) if mem_total > 0 else 0,
                    "gpu_utilization_pct": float(m1.group(3)),
                    "temperature_c": float(m2.group(1)),
                    "processes": [],
                })
                i += 2
                continue
        i += 1
    return gpus


def _attach_mx_processes(gpus, proc_output):
    """Parse mx-smi process output (gpu_idx,pid,mem,user,exp) and attach to GPUs."""
    gpu_by_index = {g["index"]: g for g in gpus}
    for line in proc_output.split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 4 and parts[0].isdigit():
            user = parts[3] if parts[3] else "unknown"
            if user in SYSTEM_USERS:
                continue
            gpu_idx = int(parts[0])
            proc = {
                "pid": int(parts[1]),
                "gpu_memory_mb": float(parts[2]) if parts[2] else 0,
                "user": user,
                "command": "",
            }
            if gpu_idx in gpu_by_index:
                gpu_by_index[gpu_idx]["processes"].append(proc)


# ── TPU helpers ───────────────────────────────────────────────────────────────
_TPU_HBM_MB_PER_CHIP = {
    "v4": 32 * 1024,   # 32 GB HBM
    "v5e": 16 * 1024,  # 16 GB HBM
    "v6e": 32 * 1024,  # 32 GB HBM
}
_TPU_DEFAULT_HBM_MB = 32 * 1024


def _build_tpu_gpus(chip_count_output):
    """Build GPU-like dicts for each TPU chip.
    Memory is known spec; utilization is unknown until torch_xla is installed.
    Uses -1 as sentinel for 'unknown' in numeric fields.
    """
    try:
        num_chips = int(chip_count_output.strip().split()[0])
    except (ValueError, IndexError):
        num_chips = 4  # default for *-8 node
    hbm_mb = _TPU_DEFAULT_HBM_MB
    return [
        {
            "index": i,
            "name": "Google TPU v4",
            "memory_total_mb": hbm_mb,
            "memory_used_mb": -1,   # unknown without torch_xla
            "memory_free_mb": -1,
            "memory_usage_pct": -1,
            "gpu_utilization_pct": -1,
            "temperature_c": -1,
            "processes": [],
        }
        for i in range(num_chips)
    ]


def _attach_tpu_processes(gpus, proc_output):
    """Attach running Python processes to chip 0 (can't determine per-chip assignment)."""
    if not gpus or not proc_output.strip():
        return
    for line in proc_output.strip().split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            continue
        try:
            pid = int(parts[0])
        except ValueError:
            continue
        user = parts[3] if len(parts) > 3 else "unknown"
        if user in SYSTEM_USERS:
            continue
        proc = {
            "pid": pid,
            "gpu_memory_mb": 0,
            "user": user,
            "command": parts[4] if len(parts) > 4 else "",
        }
        gpus[0]["processes"].append(proc)


def _filter_system_metrics(system, metrics):
    if not system:
        return {}
    filtered = {}
    if metrics.get("cpu") and "cpu" in system:
        filtered["cpu"] = system["cpu"]
    if metrics.get("memory") and "memory" in system:
        filtered["memory"] = system["memory"]
    if metrics.get("disk") and "disk" in system:
        filtered["disk"] = system["disk"]
    return filtered


def _parse_system_output(output):
    try:
        data = json.loads(output.strip() or "{}")
    except json.JSONDecodeError:
        return {}
    return {
        key: data[key]
        for key in ("cpu", "memory", "disk")
        if isinstance(data.get(key), dict)
    }


def _query_remote_system(client, metrics, disk_path=DEFAULT_DISK_PATH):
    if not (metrics.get("cpu") or metrics.get("memory") or metrics.get("disk")):
        return {}
    command = (
        f"GNVITOP_DISK_PATH={shlex.quote(_normalize_disk_path(disk_path))} "
        f"bash -c {shlex.quote(SYSTEM_CMD)}"
    )
    _, stdout, _ = client.exec_command(command, timeout=SSH_TIMEOUT)
    return _filter_system_metrics(_parse_system_output(stdout.read().decode("utf-8")), metrics)


# ── Windows local helpers (Win32 APIs; no external dependencies) ───────────────
if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    class _FILETIME(ctypes.Structure):
        _fields_ = [("lo", wintypes.DWORD), ("hi", wintypes.DWORD)]

    class _MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    def _sample_system_times():
        idle, kernel, user = _FILETIME(), _FILETIME(), _FILETIME()
        if not ctypes.windll.kernel32.GetSystemTimes(
            ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
        ):
            raise OSError("GetSystemTimes failed")
        def value(ft):
            return (ft.hi << 32) | ft.lo
        return value(idle), value(kernel), value(user)

    def _read_local_cpu_windows():
        """CPU usage via GetSystemTimes (load averages don't exist on Windows)."""
        idle1, kernel1, user1 = _sample_system_times()
        time.sleep(0.2)
        idle2, kernel2, user2 = _sample_system_times()
        total = (kernel2 + user2) - (kernel1 + user1)
        idle = idle2 - idle1
        usage = 0 if total <= 0 else (1 - idle / total) * 100
        return {
            "usage_pct": round(usage, 1),
            "cores": os.cpu_count() or 0,
            "load1": None,
            "load5": None,
            "load15": None,
        }

    def _read_local_memory_windows():
        """Memory usage via GlobalMemoryStatusEx."""
        stat = _MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            raise OSError("GlobalMemoryStatusEx failed")
        total = stat.ullTotalPhys
        available = stat.ullAvailPhys
        used = max(total - available, 0)
        return {
            "total_bytes": total,
            "used_bytes": used,
            "available_bytes": available,
            "usage_pct": round(used / total * 100, 1) if total else 0,
        }

    def _win_task_users():
        """Return a pid -> username map via tasklist (local process owners)."""
        import csv as _csv
        users = {}
        try:
            output = subprocess.run(
                ["tasklist", "/V", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=60,
            ).stdout
            for line in output.splitlines():
                cols = next(_csv.reader([line]), [])
                if len(cols) > 6 and cols[1].isdigit() and cols[6]:
                    user = cols[6].split("\\")[-1]
                    if user and user != "N/A":
                        users[int(cols[1])] = user
        except Exception:
            pass
        return users

    def _win_pmon_csv(pmon_output):
        """Convert `nvidia-smi pmon` table output to pid,gpu,mem,user,cmd CSV."""
        users = _win_task_users()
        rows = []
        for line in pmon_output.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4 or not parts[1].isdigit():
                continue
            gpu_idx, pid, mem = parts[0], parts[1], parts[3]
            command = " ".join(parts[4:])
            if not mem.isdigit():
                mem = "0"
            user = users.get(int(pid)) or "unknown"
            rows.append(",".join([pid, gpu_idx, mem, user, command]))
        return "\n".join(rows)

    def _query_local_gpu_windows(result):
        """Windows local GPU query: call nvidia-smi directly (no POSIX shell)."""
        try:
            gpu_out = subprocess.run(
                ["nvidia-smi",
                 "--query-gpu=index,name,memory.total,memory.used,memory.free,"
                 "utilization.gpu,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=30,
            ).stdout.strip()
        except FileNotFoundError:
            result["status"] = "no_gpu"
            result["error"] = "nvidia-smi not found"
            return
        except subprocess.TimeoutExpired:
            result["error"] = "nvidia-smi timed out"
            return

        gpus = _build_gpus(gpu_out)
        if not gpus:
            result["status"] = "no_gpu"
            result["error"] = "No supported GPU found (nvidia-smi returned no data)"
            return
        try:
            pmon_out = subprocess.run(
                ["nvidia-smi", "pmon", "-c", "1", "-s", "m"],
                capture_output=True, text=True, timeout=30,
            ).stdout
            _attach_processes(gpus, _win_pmon_csv(pmon_out))
        except Exception:
            pass
        result["gpus"] = gpus
        result["status"] = "ok"


def _read_local_cpu():
    if os.name == "nt":
        return _read_local_cpu_windows()
    with open("/proc/stat", "r") as f:
        parts1 = [int(x) for x in f.readline().split()[1:]]
    time.sleep(0.2)
    with open("/proc/stat", "r") as f:
        parts2 = [int(x) for x in f.readline().split()[1:]]
    idle1 = parts1[3] + (parts1[4] if len(parts1) > 4 else 0)
    idle2 = parts2[3] + (parts2[4] if len(parts2) > 4 else 0)
    total1 = sum(parts1)
    total2 = sum(parts2)
    total_delta = total2 - total1
    idle_delta = idle2 - idle1
    usage = 0 if total_delta <= 0 else (1 - idle_delta / total_delta) * 100
    load1, load5, load15 = os.getloadavg()
    return {
        "usage_pct": round(usage, 1),
        "cores": os.cpu_count() or 0,
        "load1": round(load1, 2),
        "load5": round(load5, 2),
        "load15": round(load15, 2),
    }


def _read_local_memory():
    if os.name == "nt":
        return _read_local_memory_windows()
    vals = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            key, rest = line.split(":", 1)
            vals[key] = int(rest.strip().split()[0]) * 1024
    total = vals.get("MemTotal", 0)
    available = vals.get("MemAvailable", 0)
    used = max(total - available, 0)
    return {
        "total_bytes": total,
        "used_bytes": used,
        "available_bytes": available,
        "usage_pct": round(used / total * 100, 1) if total else 0,
    }


def _read_local_disk(disk_path=DEFAULT_DISK_PATH):
    import shutil
    path = os.path.expanduser(_normalize_disk_path(disk_path))
    usage = shutil.disk_usage(path)
    return {
        "mount": path,
        "path": path,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "usage_pct": round(usage.used / usage.total * 100, 1) if usage.total else 0,
    }


def query_local_system(metrics, disk_path=DEFAULT_DISK_PATH):
    system = {}
    if metrics.get("cpu"):
        try:
            system["cpu"] = _read_local_cpu()
        except Exception:
            pass
    if metrics.get("memory"):
        try:
            system["memory"] = _read_local_memory()
        except Exception:
            pass
    if metrics.get("disk"):
        try:
            system["disk"] = _read_local_disk(disk_path)
        except Exception:
            pass
    return system


def _win_ssh_exe():
    """Locate Windows' built-in OpenSSH binary, if present."""
    path = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                        "System32", "OpenSSH", "ssh.exe")
    return path if os.path.isfile(path) else None


class _NativeSshPipe:
    """Adapter that lets paramiko run over a native `ssh -W host:port` pipe.

    Some corporate VPN clients (observed with CorpLink) drop raw Python
    sockets mid-handshake while letting Windows' native ssh.exe through.
    Tunneling the SSH protocol over ssh.exe's stdio works around that.
    Password auth is fed to ssh.exe via a temp SSH_ASKPASS script.
    """

    def __init__(self, ssh_exe, hostname, port, user, identity_file, password):
        self._closed = False
        self._askpass_path = None
        env = dict(os.environ)
        if password:
            # ssh.exe (8.4+) can be forced to fetch the password from
            # SSH_ASKPASS instead of the tty-less stdin.
            import tempfile
            fd, self._askpass_path = tempfile.mkstemp(suffix=".bat", prefix="gnvitop_askpass_")
            with os.fdopen(fd, "w") as f:
                f.write("@echo " + password.replace("\n", "") + "\r\n")
            env["SSH_ASKPASS"] = self._askpass_path
            env["SSH_ASKPASS_REQUIRE"] = "force"
            env["DISPLAY"] = "gnvitop"
        cmd = [ssh_exe, "-o", "StrictHostKeyChecking=no",
               "-o", "ConnectTimeout=20"]
        if password:
            # BatchMode would disable password auth entirely.
            cmd += ["-o", "NumberOfPasswordPrompts=1", "-o", "PreferredAuthentications=password,keyboard-interactive"]
        else:
            cmd += ["-o", "BatchMode=yes"]
        if identity_file:
            cmd += ["-i", identity_file]
        if user:
            cmd += ["-l", user]
        cmd += ["-W", f"{hostname}:{port}", hostname]
        self.proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, env=env)

    def send(self, data):
        self.proc.stdin.write(data)
        self.proc.stdin.flush()
        return len(data)

    def recv(self, n):
        data = self.proc.stdout.read1(n)
        if not data:
            raise EOFError("native ssh pipe closed")
        return data

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.proc.terminate()
        except Exception:
            pass
        if self._askpass_path:
            try:
                os.remove(self._askpass_path)
            except OSError:
                pass

    def settimeout(self, *args):
        pass

    def setblocking(self, *args):
        pass


def _make_ssh_client(hostname, port, user, identity_file, password=None, sock=None):
    """Create and connect a paramiko SSHClient.

    On Windows, if the direct TCP connection fails with a banner/SSH error,
    retries the connection tunneled through the native ssh.exe (ssh -W).
    """
    def _connect(sock_to_use):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs = {
            "hostname": hostname,
            "port": port,
            "username": user,
            "timeout": SSH_TIMEOUT,
            "banner_timeout": SSH_TIMEOUT,
            "auth_timeout": SSH_TIMEOUT,
            "allow_agent": True,
            "look_for_keys": True,
        }
        if identity_file:
            kwargs["key_filename"] = identity_file
        if password:
            kwargs["password"] = password
            kwargs["look_for_keys"] = False
            kwargs["allow_agent"] = False
        if sock_to_use is not None:
            kwargs["sock"] = sock_to_use
        client.connect(**kwargs)
        return client

    if sock is not None:
        return _connect(sock)

    try:
        return _connect(None)
    except paramiko.AuthenticationException:
        # Auth failure means the transport itself works — retrying via
        # ssh.exe cannot help, and would mask the real (credential) error.
        raise
    except (paramiko.SSHException, EOFError, OSError) as original_error:
        # Windows corporate-VPN quirk: raw sockets get cut during the banner
        # exchange while native ssh.exe passes. Retry through it.
        if os.name == "nt":
            ssh_exe = _win_ssh_exe()
            if ssh_exe:
                pipe = None
                try:
                    pipe = _NativeSshPipe(ssh_exe, hostname, port, user, identity_file, password)
                    return _connect(pipe)
                except paramiko.AuthenticationException as fallback_error:
                    # The transport worked but credentials didn't — report
                    # that instead of the transport-level original error.
                    if pipe is not None:
                        pipe.close()
                    raise fallback_error
                except Exception:
                    # Fallback also failed at transport level — clean up the
                    # ssh.exe child so it doesn't linger as an orphan process.
                    if pipe is not None:
                        pipe.close()
        raise original_error


def query_gpu(host_info, hosts_by_alias=None, metrics=None):
    """SSH into a host and query GPU information (single round trip).

    hosts_by_alias: dict of alias -> host_info for resolving ProxyJump targets.
    """
    alias = host_info["alias"]
    hostname = host_info["hostname"] or alias
    user = host_info["user"]
    port = host_info["port"]
    metrics = _normalize_metrics(host_info.get("metrics", metrics))
    disk_path = host_info.get("disk_path", DEFAULT_DISK_PATH)

    result = {
        "alias": alias,
        "hostname": hostname,
        "user": user or "unknown",
        "port": port,
        "status": "error",
        "error": None,
        "gpus": [],
        "system": {},
    }

    jump_client = None
    try:
        sock = None
        proxy_alias = host_info.get("proxy_jump")
        proxy_cmd = host_info.get("proxy_command")
        if proxy_alias:
            # Resolve jump host info
            jump_info = (hosts_by_alias or {}).get(proxy_alias) or {
                "alias": proxy_alias,
                "hostname": proxy_alias,
                "user": None,
                "port": 22,
                "identity_file": None,
            }
            jump_host = jump_info.get("hostname") or proxy_alias
            jump_port = jump_info.get("port", 22)
            jump_user = jump_info.get("user")
            jump_key = jump_info.get("identity_file")
            jump_password = jump_info.get("password")
            jump_client = _make_ssh_client(jump_host, jump_port, jump_user, jump_key, jump_password)
            sock = jump_client.get_transport().open_channel(
                "direct-tcpip", (hostname, port), ("", 0)
            )
        elif proxy_cmd:
            # ProxyCommand: execute the command and use its stdio as socket
            cmd = proxy_cmd.replace("%h", hostname).replace("%p", str(port))
            sock = paramiko.ProxyCommand(cmd)

        client = _make_ssh_client(
            hostname, port, user, host_info.get("identity_file"),
            host_info.get("password"), sock=sock,
        )

        result["system"] = _query_remote_system(client, metrics, disk_path)
        if not metrics.get("gpu"):
            result["status"] = "ok"
            client.close()
            return result

        # Single exec_command for both GPU stats and process info
        # Wrap in bash -c to avoid issues with non-bash login shells (e.g. fish)
        _, stdout, _ = client.exec_command("bash -c " + shlex.quote(COMBINED_CMD), timeout=SSH_TIMEOUT)
        output = stdout.read().decode("utf-8").strip()
        client.close()

        gpu_part, proc_part, vendor = _parse_combined_output(output)

        if not gpu_part:
            result["status"] = "no_gpu"
            result["error"] = "No supported GPU found (tried nvidia-smi, mx-smi, and TPU)"
        else:
            if vendor == "mx":
                gpus = _build_mx_gpus(gpu_part)
                if proc_part:
                    _attach_mx_processes(gpus, proc_part)
            elif vendor == "tpu":
                gpus = _build_tpu_gpus(gpu_part)
                if proc_part:
                    _attach_tpu_processes(gpus, proc_part)
                result["is_tpu"] = True
            else:
                gpus = _build_gpus(gpu_part)
                if proc_part:
                    _attach_processes(gpus, proc_part)
            result["gpus"] = gpus
            if gpus:
                result["status"] = "ok"
            else:
                result["status"] = "no_gpu"
                result["error"] = "No valid accelerator data returned"

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
    finally:
        if jump_client:
            try:
                jump_client.close()
            except Exception:
                pass

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
                "command": parts[4] if len(parts) >= 5 else "",
            }
            if gpu_idx in gpu_by_index:
                gpu_by_index[gpu_idx]["processes"].append(proc)


def query_local_gpu(metrics=None, disk_path=DEFAULT_DISK_PATH):
    """Query the local machine for GPU information (single subprocess call)."""
    import socket

    metrics = _normalize_metrics(metrics)
    hostname = socket.gethostname()
    result = {
        "alias": "localhost",
        "hostname": hostname,
        "user": CURRENT_USER,
        "port": 0,
        "status": "error",
        "error": None,
        "gpus": [],
        "system": query_local_system(metrics, disk_path),
        "is_local": True,
    }

    if not metrics.get("gpu"):
        result["status"] = "ok"
        return result

    if os.name == "nt":
        # Windows has no POSIX shell for COMBINED_CMD — query nvidia-smi directly.
        _query_local_gpu_windows(result)
        return result

    try:
        output = subprocess.run(
            COMBINED_CMD, shell=True, capture_output=True, text=True, timeout=30
        ).stdout.strip()

        gpu_part, proc_part, vendor = _parse_combined_output(output)

        if not gpu_part:
            result["status"] = "no_gpu"
            result["error"] = "No supported GPU found (tried nvidia-smi, mx-smi, and TPU)"
        else:
            if vendor == "mx":
                gpus = _build_mx_gpus(gpu_part)
                if proc_part:
                    _attach_mx_processes(gpus, proc_part)
            elif vendor == "tpu":
                gpus = _build_tpu_gpus(gpu_part)
                if proc_part:
                    _attach_tpu_processes(gpus, proc_part)
                result["is_tpu"] = True
            else:
                gpus = _build_gpus(gpu_part)
                if proc_part:
                    _attach_processes(gpus, proc_part)
            result["gpus"] = gpus
            if gpus:
                result["status"] = "ok"
            else:
                result["status"] = "no_gpu"
                result["error"] = "No valid accelerator data returned"

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


def _as_float(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _round_or_none(value, digits=1):
    value = _as_float(value)
    return round(value, digits) if value is not None else None


def _history_sample(host, timestamp):
    gpus = host.get("gpus") or []
    gpu_utils = []
    gpu_temperatures = {}
    for gpu in gpus:
        util = _as_float(gpu.get("gpu_utilization_pct"))
        if util is not None and util >= 0:
            gpu_utils.append(util)
        temperature = _as_float(gpu.get("temperature_c"))
        index = gpu.get("index")
        if index is not None:
            gpu_temperatures[str(index)] = (
                round(temperature, 1) if temperature is not None and temperature >= 0 else None
            )
    mem_totals = [_as_float(g.get("memory_total_mb")) or 0 for g in gpus]
    mem_free = [_as_float(g.get("memory_free_mb")) for g in gpus]
    valid_mem_free = [v for v in mem_free if v is not None and v >= 0]
    gpu_memory_total = sum(v for v in mem_totals if v > 0)
    gpu_memory_free = sum(valid_mem_free)
    system = host.get("system") or {}
    cpu = system.get("cpu") or {}
    memory = system.get("memory") or {}
    disk = system.get("disk") or {}
    return {
        "timestamp": round(timestamp, 3),
        "alias": host.get("alias"),
        "hostname": host.get("hostname"),
        "status": host.get("status"),
        "is_local": bool(host.get("is_local")),
        "gpu_count": len(gpus),
        "gpu_util_avg": round(sum(gpu_utils) / len(gpu_utils), 1) if gpu_utils else None,
        "gpu_temperatures_c": gpu_temperatures,
        "gpu_memory_free_mb": round(gpu_memory_free, 1) if gpu_memory_total and valid_mem_free else None,
        "gpu_memory_free_pct": round(gpu_memory_free / gpu_memory_total * 100, 1) if gpu_memory_total and valid_mem_free else None,
        "cpu_pct": _round_or_none(cpu.get("usage_pct")),
        "memory_pct": _round_or_none(memory.get("usage_pct")),
        "disk_pct": _round_or_none(disk.get("usage_pct")),
    }


def _get_history_store():
    global _history_store
    with history_lock:
        if _history_store is None or _history_store.legacy_path != os.fspath(HISTORY_PATH):
            _history_store = HistoryStore(HISTORY_PATH, HISTORY_RETENTION_SECONDS, HISTORY_PRUNE_INTERVAL)
        return _history_store


def record_history(results, timestamp=None):
    """Append compact host samples to persistent history and retain seven days."""
    if not results:
        return
    now = time.time() if timestamp is None else timestamp
    samples = [
        _history_sample(host, now)
        for host in results
        if host.get("alias")
    ]
    if not samples:
        return
    _get_history_store().record(samples, now)


def load_history(alias, range_key):
    seconds = HISTORY_RANGES.get(range_key, HISTORY_RANGES["1h"])
    cutoff = time.time() - seconds
    return _get_history_store().load(alias, cutoff, HISTORY_MAX_POINTS)


def discover_gadi_nodes(hosts_by_alias):
    """SSH to each gadi-like login node and discover allocated GPU compute nodes via qstat.

    Returns a list of host_info dicts for any active job nodes found.
    A host is treated as a Gadi login node if its HostName ends with '.nci.org.au'
    and it has no ProxyJump (i.e. it is itself the jump host).
    """
    discovered = []
    for alias, info in hosts_by_alias.items():
        hostname = info.get("hostname") or alias
        if not hostname.endswith(".nci.org.au"):
            continue
        if info.get("proxy_jump"):
            continue  # skip compute nodes, only query login nodes
        # SSH to login node and run qstat to find allocated nodes
        try:
            client = _make_ssh_client(
                hostname, info.get("port", 22),
                info.get("user"), info.get("identity_file"),
                info.get("password"),
            )
            _, stdout, _ = client.exec_command(
                "qstat -u $(whoami) -n 2>/dev/null | grep -oE 'gadi-gpu-[a-z0-9-]+' | sort -u",
                timeout=SSH_TIMEOUT,
            )
            node_names = [n.strip() for n in stdout.read().decode().splitlines() if n.strip()]
            client.close()
        except Exception:
            continue

        for node in node_names:
            node_hostname = f"{node}.gadi.nci.org.au"
            discovered.append({
                "alias": node,
                "hostname": node_hostname,
                "user": info.get("user"),
                "port": 22,
                "identity_file": info.get("identity_file"),
                "password": info.get("password"),
                "proxy_jump": alias,
                "disk_path": info.get("disk_path", DEFAULT_DISK_PATH),
                "metrics": info.get("metrics", DEFAULT_METRICS),
            })

    return discovered


def _collect_query_hosts():
    """Load enabled hosts (plus discovered Gadi nodes) for one query pass."""
    payload = load_config_payload()
    hosts = [h for h in payload["hosts"] if h.get("enabled", True)]
    hosts_by_alias = {h["alias"]: h for h in hosts}
    for h in discover_gadi_nodes(hosts_by_alias):
        if h["alias"] not in hosts_by_alias:
            hosts.append(h)
            hosts_by_alias[h["alias"]] = h
    return payload["monitor_local"], payload["metrics"], payload["local_disk_path"], hosts, hosts_by_alias


def iter_gpu_results():
    """Query all hosts concurrently, yielding each host result as it arrives.

    Single code path shared by the cached fetch and the SSE stream. When fully
    consumed, records history for the pass.
    """
    monitor_local, metrics, local_disk_path, hosts, hosts_by_alias = _collect_query_hosts()
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {}
        if monitor_local:
            futures[executor.submit(query_local_gpu, metrics, local_disk_path)] = None
        for h in hosts:
            futures[executor.submit(query_gpu, h, hosts_by_alias, metrics)] = h
        for future in as_completed(futures):
            host_result = future.result()
            results.append(host_result)
            yield host_result
    record_history(results)


def fetch_all_gpu_info():
    """Query all hosts (local + remote) concurrently and return sorted results."""
    return _sort_results(list(iter_gpu_results()))


def _tunnel_signature(host):
    """Connection-relevant fields of a host config; changes force a restart."""
    return (
        host.get("hostname") or host.get("alias"),
        host.get("port", 22),
        host.get("user"),
        host.get("tunnel_port") or DEFAULT_TUNNEL_PORT,
        host.get("identity_file"),
        bool(host.get("password")),
    )


def _bridge_channel(chan, target):
    """Bridge a reverse-forwarded SSH channel to a local TCP socket."""
    try:
        sock = socket.create_connection(target, timeout=15)
    except OSError:
        try:
            chan.close()
        except Exception:
            pass
        return

    def relay(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except Exception:
            pass
        finally:
            try:
                dst.shutdown(socket.SHUT_WR)
            except Exception:
                pass

    def wait_and_close():
        for t in threads:
            t.join()
        try:
            chan.close()
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass

    threads = [
        threading.Thread(target=relay, args=(chan, sock), daemon=True),
        threading.Thread(target=relay, args=(sock, chan), daemon=True),
    ]
    for t in threads:
        t.start()
    threading.Thread(target=wait_and_close, daemon=True).start()


class TunnelManager:
    """Maintains persistent reverse SSH tunnels (server:port -> local:port).

    Equivalent to `ssh -R <port>:127.0.0.1:<port>` per host: the server
    listens on the port and traffic is forwarded to the same port on the
    machine running gnvitop (e.g. a local proxy on 7890).
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._tunnels = {}  # alias -> state dict

    def sync(self, hosts):
        """Start tunnels for enabled hosts with tunnel_enabled; stop the rest."""
        wanted = {}
        for h in hosts:
            if h.get("enabled", True) and h.get("tunnel_enabled"):
                wanted[h["alias"]] = h
        with self._lock:
            for alias, state in list(self._tunnels.items()):
                host = wanted.get(alias)
                if host is None or state["signature"] != _tunnel_signature(host):
                    self._stop_locked(alias)
            for alias, host in wanted.items():
                if alias not in self._tunnels:
                    state = {
                        "host": dict(host),
                        "signature": _tunnel_signature(host),
                        "stop": threading.Event(),
                        "client": None,
                        "thread": None,
                        "status": "starting",
                        "error": None,
                    }
                    state["thread"] = threading.Thread(
                        target=self._run, args=(state,), daemon=True)
                    self._tunnels[alias] = state
                    state["thread"].start()

    def _stop_locked(self, alias):
        state = self._tunnels.pop(alias)
        state["stop"].set()
        client = state.get("client")
        if client is not None:
            try:
                client.close()
            except Exception:
                pass

    def _run(self, state):
        backoff = 5
        while not state["stop"].is_set():
            host = state["host"]
            port = host.get("tunnel_port") or DEFAULT_TUNNEL_PORT
            client = None
            try:
                client = _make_ssh_client(
                    host.get("hostname") or host.get("alias"),
                    host.get("port", 22),
                    host.get("user"),
                    host.get("identity_file"),
                    host.get("password"),
                )
                state["client"] = client
                transport = client.get_transport()
                transport.set_keepalive(30)
                transport.request_port_forward("127.0.0.1", port)
                state["status"] = "running"
                state["error"] = None
                while not state["stop"].is_set() and transport.is_active():
                    chan = transport.accept(1.0)
                    if chan is None:
                        continue
                    threading.Thread(
                        target=_bridge_channel,
                        args=(chan, ("127.0.0.1", port)),
                        daemon=True,
                    ).start()
                if not state["stop"].is_set():
                    state["status"] = "reconnecting"
                    state["error"] = "连接断开"
            except Exception as e:
                state["status"] = "reconnecting"
                state["error"] = f"{type(e).__name__}: {e}"
                if "forwarding request denied" in str(e):
                    state["error"] += f"（端口 {port} 可能已被占用，例如手动开启的 SSH 会话）"
            finally:
                state["client"] = None
                if client is not None:
                    try:
                        transport = client.get_transport()
                        if transport is not None:
                            transport.cancel_port_forward("127.0.0.1", port)
                    except Exception:
                        pass
                    try:
                        client.close()
                    except Exception:
                        pass
            if state["stop"].wait(backoff):
                break
            backoff = min(backoff * 2, 60)
        state["status"] = "stopped"

    def statuses(self):
        with self._lock:
            return {
                alias: {
                    "status": st["status"],
                    "port": st["host"].get("tunnel_port") or DEFAULT_TUNNEL_PORT,
                    "error": st["error"],
                }
                for alias, st in self._tunnels.items()
            }


tunnel_manager = TunnelManager()


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
    def _prepare_history():
        try:
            _get_history_store().prepare()
        except Exception:
            app.logger.exception("Could not prepare history storage")

    threading.Thread(target=_prepare_history, daemon=True).start()

    def _warmer():
        # Initial warm-up: start immediately so first page load hits cached data
        _do_background_refresh()
        while True:
            time.sleep(CACHE_TTL)
            _do_background_refresh()

    t = threading.Thread(target=_warmer, daemon=True)
    t.start()


@app.route("/")
def index():
    import socket
    host_info = f"{getpass.getuser()}@{socket.gethostname()}"
    html = DASHBOARD_HTML.replace("{{GNVITOP_HOST_INFO}}", host_info).replace("{{GNVITOP_VERSION}}", __version__)
    return Response(html, mimetype="text/html")


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


@app.route("/api/config/hosts", methods=["GET"])
def api_config_hosts():
    payload = load_config_payload()
    hosts = [public_host_config(h) for h in payload["hosts"]]
    return jsonify({
        "hosts": hosts,
        "monitor_local": payload["monitor_local"],
        "metrics": payload["metrics"],
        "local_disk_path": payload["local_disk_path"],
        "config_path": SERVER_CONFIG_PATH,
        "ssh_config_path": SSH_CONFIG_PATH,
    })


@app.route("/api/config/hosts", methods=["POST"])
def api_save_config_hosts():
    payload = request.get_json(silent=True) or {}
    hosts = payload.get("hosts", [])
    if not isinstance(hosts, list):
        return jsonify({"error": "hosts must be a list"}), 400

    monitor_local = bool(payload.get("monitor_local", True))
    metrics = _normalize_metrics(payload.get("metrics"))
    local_disk_path = _normalize_disk_path(
        payload.get("local_disk_path", payload.get("disk_path", DEFAULT_DISK_PATH))
    )
    existing_passwords = {
        h["alias"]: h.get("password")
        for h in load_server_config()
        if h.get("password")
    }
    normalized = []
    for host in hosts:
        if not isinstance(host, dict):
            continue
        merged = dict(host)
        if merged.get("password") == "__KEEP__":
            merged["password"] = existing_passwords.get(str(merged.get("alias") or "").strip())
        normalized.append(_normalize_host_config(merged, default_metrics=metrics))

    save_server_config(normalized, monitor_local, metrics, local_disk_path)
    _invalidate_cache()
    tunnel_manager.sync(load_server_config())
    return jsonify({
        "hosts": [public_host_config(h) for h in load_server_config()],
        "monitor_local": get_monitor_local(),
        "metrics": get_metric_config(),
        "local_disk_path": get_local_disk_path_config(),
        "config_path": SERVER_CONFIG_PATH,
    })


@app.route("/api/tunnels")
def api_tunnels():
    return jsonify({"tunnels": tunnel_manager.statuses()})


@app.route("/api/config/export", methods=["GET"])
def api_export_config():
    payload = load_config_payload()
    body = json.dumps(payload, indent=2)
    return Response(
        body,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=gnvitop-config.json"},
    )


@app.route("/api/config/import", methods=["POST"])
def api_import_config():
    payload = request.get_json(silent=True)
    try:
        save_config_payload(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    _invalidate_cache()
    tunnel_manager.sync(load_server_config())
    saved = load_config_payload()
    return jsonify({
        "hosts": [public_host_config(h) for h in saved["hosts"]],
        "monitor_local": saved["monitor_local"],
        "metrics": saved["metrics"],
        "local_disk_path": saved["local_disk_path"],
        "config_path": SERVER_CONFIG_PATH,
    })


@app.route("/api/config/import-ssh", methods=["POST"])
def api_import_ssh_config():
    payload = request.get_json(silent=True) or {}
    hosts = import_ssh_hosts(replace=bool(payload.get("replace")))
    _invalidate_cache()
    tunnel_manager.sync(load_server_config())
    return jsonify({
        "hosts": [public_host_config(h) for h in hosts],
        "monitor_local": get_monitor_local(),
        "metrics": get_metric_config(),
        "local_disk_path": get_local_disk_path_config(),
        "config_path": SERVER_CONFIG_PATH,
        "ssh_config_path": SSH_CONFIG_PATH,
    })


@app.route("/api/config/test", methods=["POST"])
def api_test_host():
    """Test SSH connectivity and GPU detection for a single (possibly unsaved) host."""
    payload = request.get_json(silent=True) or {}
    host = payload.get("host")
    if not isinstance(host, dict):
        return jsonify({"error": "host is required"}), 400

    merged = dict(host)
    if merged.get("password") == "__KEEP__":
        saved = load_server_config()
        by_endpoint = {_host_endpoint_key(h): h for h in saved}
        by_alias = {h["alias"]: h for h in saved}
        saved_host = by_endpoint.get(_host_endpoint_key(merged)) or by_alias.get(
            str(merged.get("alias") or "").strip()
        )
        merged["password"] = (saved_host or {}).get("password")

    normalized = _normalize_host_config(merged)
    # A test always probes GPUs, even if the host's GPU metric is disabled.
    normalized["metrics"] = {**_normalize_metrics(normalized.get("metrics")), "gpu": True}
    hosts_by_alias = {h["alias"]: h for h in load_server_config()}
    return jsonify(query_gpu(normalized, hosts_by_alias))


@app.route("/api/history")
def api_history():
    alias = str(request.args.get("host") or "").strip()
    range_key = str(request.args.get("range") or "1h").strip()
    if not alias:
        return jsonify({"error": "host is required"}), 400
    if range_key not in HISTORY_RANGES:
        range_key = "1h"
    return jsonify({
        "host": alias,
        "range": range_key,
        "retention_seconds": HISTORY_RETENTION_SECONDS,
        "points": load_history(alias, range_key),
    })


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
        results = []
        for host_result in iter_gpu_results():
            results.append(host_result)
            yield f"data: {json.dumps({'host': host_result})}\n\n"

        # Update cache with fresh streamed data
        sorted_results = _sort_results(results)
        updated_at = time.time()
        with cache_lock:
            cache["data"] = sorted_results
            cache["last_update"] = updated_at

        yield f"data: {json.dumps({'done': True, 'updated_at': updated_at})}\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
