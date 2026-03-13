"""GPU usage history — Supabase (preferred) or local SQLite fallback."""

import os
import sqlite3
import threading
import time

# ---------------------------------------------------------------------------
# Supabase backend
# ---------------------------------------------------------------------------

def _get_supabase_client():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except ImportError:
        print("Warning: SUPABASE_URL/KEY set but 'supabase' package not installed.")
        print("  Run: pip install supabase")
        return None


def _record_supabase(client, hosts_data):
    ts = int(time.time())
    for host in hosts_data:
        if host.get("status") != "ok":
            continue
        alias = host["alias"]
        hostname = host.get("hostname", "")
        for gpu in host.get("gpus", []):
            snap = client.table("gpu_snapshots").insert({
                "timestamp": ts,
                "host_alias": alias,
                "hostname": hostname,
                "gpu_index": gpu["index"],
                "gpu_name": gpu["name"],
                "mem_total_mb": gpu["memory_total_mb"],
                "mem_used_mb": gpu["memory_used_mb"],
                "mem_free_mb": gpu["memory_free_mb"],
                "gpu_util_pct": gpu["gpu_utilization_pct"],
                "temp_c": gpu["temperature_c"],
            }).execute()
            snap_id = snap.data[0]["id"]
            for proc in gpu.get("processes", []):
                client.table("gpu_processes").insert({
                    "snapshot_id": snap_id,
                    "pid": proc["pid"],
                    "user": proc["user"],
                    "command": proc.get("command", ""),
                    "gpu_mem_mb": proc["gpu_memory_mb"],
                }).execute()


# ---------------------------------------------------------------------------
# SQLite backend (fallback)
# ---------------------------------------------------------------------------

_DB_PATH = os.path.expanduser("~/.gnvitop.db")
_db_lock = threading.Lock()


def set_db_path(path):
    global _DB_PATH
    _DB_PATH = path


def _sqlite_init():
    with _db_lock:
        with sqlite3.connect(_DB_PATH) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS gpu_snapshots (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp     INTEGER NOT NULL,
                    host_alias    TEXT    NOT NULL,
                    hostname      TEXT,
                    gpu_index     INTEGER NOT NULL,
                    gpu_name      TEXT,
                    mem_total_mb  REAL,
                    mem_used_mb   REAL,
                    mem_free_mb   REAL,
                    gpu_util_pct  REAL,
                    temp_c        REAL
                );
                CREATE TABLE IF NOT EXISTS gpu_processes (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id  INTEGER NOT NULL REFERENCES gpu_snapshots(id),
                    pid          INTEGER,
                    user         TEXT,
                    command      TEXT,
                    gpu_mem_mb   REAL
                );
                CREATE INDEX IF NOT EXISTS idx_snapshots_ts   ON gpu_snapshots(timestamp);
                CREATE INDEX IF NOT EXISTS idx_processes_snap ON gpu_processes(snapshot_id);
            """)


def _record_sqlite(hosts_data):
    ts = int(time.time())
    with _db_lock:
        with sqlite3.connect(_DB_PATH) as conn:
            for host in hosts_data:
                if host.get("status") != "ok":
                    continue
                alias = host["alias"]
                hostname = host.get("hostname", "")
                for gpu in host.get("gpus", []):
                    cur = conn.execute(
                        """INSERT INTO gpu_snapshots
                               (timestamp, host_alias, hostname, gpu_index, gpu_name,
                                mem_total_mb, mem_used_mb, mem_free_mb, gpu_util_pct, temp_c)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (ts, alias, hostname, gpu["index"], gpu["name"],
                         gpu["memory_total_mb"], gpu["memory_used_mb"], gpu["memory_free_mb"],
                         gpu["gpu_utilization_pct"], gpu["temperature_c"]),
                    )
                    snap_id = cur.lastrowid
                    for proc in gpu.get("processes", []):
                        conn.execute(
                            """INSERT INTO gpu_processes
                                   (snapshot_id, pid, user, command, gpu_mem_mb)
                               VALUES (?, ?, ?, ?, ?)""",
                            (snap_id, proc["pid"], proc["user"],
                             proc.get("command", ""), proc["gpu_memory_mb"]),
                        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_supabase_client = None   # resolved once at init_db()
_use_supabase = False


def init_db():
    global _supabase_client, _use_supabase
    _supabase_client = _get_supabase_client()
    if _supabase_client:
        _use_supabase = True
        print("  DB: Supabase")
    else:
        _use_supabase = False
        _sqlite_init()
        print(f"  DB: SQLite → {_DB_PATH}")


def record_snapshot(hosts_data):
    if _use_supabase:
        _record_supabase(_supabase_client, hosts_data)
    else:
        _record_sqlite(hosts_data)


def start_sampler(interval_seconds, fetch_fn):
    """Background thread: sample GPU data and persist every interval_seconds."""
    def _loop():
        while True:
            try:
                data = fetch_fn()
                record_snapshot(data)
            except Exception:
                pass
            time.sleep(interval_seconds)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
