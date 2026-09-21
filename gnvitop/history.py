"""Indexed dashboard history with a one-time import of legacy JSONL samples."""

from contextlib import closing
import json
import math
import os
import sqlite3
import threading
import time


class HistoryStore:
    def __init__(self, legacy_path, retention_seconds, prune_interval):
        self.legacy_path = os.fspath(legacy_path)
        self.path = os.path.splitext(self.legacy_path)[0] + ".sqlite3"
        self.retention_seconds = retention_seconds
        self.prune_interval = prune_interval
        self._ready = False
        self._init_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._last_prune = 0

    def _connect(self):
        return sqlite3.connect(self.path, timeout=60)

    def prepare(self):
        """Import once, atomically, leaving the original history file untouched."""
        if self._ready:
            return
        with self._init_lock:
            if self._ready:
                return
            os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
            with closing(self._connect()) as conn, conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("""CREATE TABLE IF NOT EXISTS samples (
                    id INTEGER PRIMARY KEY,
                    alias TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    data TEXT NOT NULL
                )""")
                conn.execute("CREATE INDEX IF NOT EXISTS samples_host_time ON samples(alias, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS samples_time ON samples(timestamp)")
                conn.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
                conn.execute("BEGIN IMMEDIATE")
                imported = conn.execute("SELECT value FROM metadata WHERE key = 'legacy_imported'").fetchone()
                if not imported:
                    self._import_legacy(conn)
                    conn.execute("INSERT INTO metadata VALUES ('legacy_imported', '1')")
            self._ready = True

    def _import_legacy(self, conn):
        cutoff = time.time() - self.retention_seconds
        try:
            source = open(self.legacy_path, "r", encoding="utf-8")
        except FileNotFoundError:
            return
        with source:
            batch = []
            for line in source:
                try:
                    item = json.loads(line)
                    if not isinstance(item, dict):
                        continue
                    alias = item.get("alias")
                    timestamp = float(item.get("timestamp"))
                except (ValueError, TypeError):
                    continue
                if not isinstance(alias, str) or not alias or not math.isfinite(timestamp) or timestamp < cutoff:
                    continue
                item["timestamp"] = timestamp
                batch.append((alias, timestamp, json.dumps(item, separators=(",", ":"))))
                if len(batch) >= 1000:
                    conn.executemany("INSERT INTO samples(alias, timestamp, data) VALUES (?, ?, ?)", batch)
                    batch.clear()
            conn.executemany("INSERT INTO samples(alias, timestamp, data) VALUES (?, ?, ?)", batch)

    def record(self, samples, now):
        self.prepare()
        rows = [(s["alias"], s["timestamp"], json.dumps(s, separators=(",", ":"))) for s in samples]
        with self._write_lock:
            prune = now - self._last_prune > self.prune_interval
            with closing(self._connect()) as conn, conn:
                conn.executemany("INSERT INTO samples(alias, timestamp, data) VALUES (?, ?, ?)", rows)
                if prune:
                    conn.execute("DELETE FROM samples WHERE timestamp < ?", (now - self.retention_seconds,))
            if prune:
                self._last_prune = now

    def load(self, alias, cutoff, max_points):
        self.prepare()
        with closing(self._connect()) as conn, conn:
            # Keep IDs and their payloads in the same snapshot even during pruning.
            conn.execute("BEGIN")
            ids = [row[0] for row in conn.execute(
                "SELECT id FROM samples WHERE alias = ? AND timestamp >= ? ORDER BY timestamp, id",
                (alias, cutoff),
            )]
            if len(ids) > max_points:
                # Select from the covering index before reading/parsing JSON.
                # Include both endpoints and keep the response strictly bounded.
                ids = [ids[i * (len(ids) - 1) // (max_points - 1)] for i in range(max_points)]
            payloads = {}
            for start in range(0, len(ids), 500):
                batch = ids[start:start + 500]
                placeholders = ",".join("?" for _ in batch)
                payloads.update(conn.execute(
                    "SELECT id, data FROM samples WHERE id IN (" + placeholders + ")", batch,
                ))
            return [json.loads(payloads[row_id]) for row_id in ids]
