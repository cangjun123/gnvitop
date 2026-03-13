"""SQLite database for GPU usage history."""

import os
import sqlite3
import threading
import time

_DB_PATH = os.path.expanduser("~/.gnvitop.db")
_db_lock = threading.Lock()


def set_db_path(path):
    global _DB_PATH
    _DB_PATH = path


def init_db():
    with _db_lock:
        with sqlite3.connect(_DB_PATH) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS gpu_snapshots (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   INTEGER NOT NULL,
                    host_alias  TEXT    NOT NULL,
                    hostname    TEXT,
                    gpu_index   INTEGER NOT NULL,
                    gpu_name    TEXT,
                    mem_total_mb  REAL,
                    mem_used_mb   REAL,
                    mem_free_mb   REAL,
                    gpu_util_pct  REAL,
                    temp_c        REAL
                );
                CREATE TABLE IF NOT EXISTS gpu_processes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER NOT NULL REFERENCES gpu_snapshots(id),
                    pid         INTEGER,
                    user        TEXT,
                    command     TEXT,
                    gpu_mem_mb  REAL
                );
                CREATE INDEX IF NOT EXISTS idx_snapshots_ts   ON gpu_snapshots(timestamp);
                CREATE INDEX IF NOT EXISTS idx_processes_snap ON gpu_processes(snapshot_id);
            """)


def record_snapshot(hosts_data):
    """Persist a full fetch_all_gpu_info() result to the database."""
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


def start_sampler(interval_seconds, fetch_fn):
    """Background thread: call fetch_fn() and record_snapshot() every interval_seconds."""
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
