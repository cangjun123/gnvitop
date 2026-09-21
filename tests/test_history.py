import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from gnvitop import server
from gnvitop.history import HistoryStore


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.legacy = Path(self.temp.name) / "history.jsonl"
        self.now = time.time()
        self.store = HistoryStore(self.legacy, 7 * 86400, 3600)

    def sample(self, timestamp=None, alias="host-a", **values):
        return {"alias": alias, "timestamp": self.now if timestamp is None else timestamp, **values}

    def test_import_preserves_original_and_runs_once_across_restarts(self):
        samples = [self.sample(self.now - 10), self.sample(self.now - 20),
                   self.sample(alias="host-b"), self.sample(self.now - 8 * 86400)]
        contents = "\n".join(json.dumps(s) for s in samples)
        contents += '\ninvalid\nnull\n[]\n{"alias":"host-a","timestamp":"nan"}\n'
        self.legacy.write_text(contents, encoding="utf-8")
        points = self.store.load("host-a", self.now - 3600, 1200)
        self.assertEqual([p["timestamp"] for p in points], [self.now - 20, self.now - 10])
        self.assertEqual(self.legacy.read_text(encoding="utf-8"), contents)
        restarted = HistoryStore(self.legacy, 7 * 86400, 3600)
        with patch("gnvitop.history.open", side_effect=AssertionError("must not rescan JSONL")):
            self.assertEqual(restarted.load("host-a", self.now - 3600, 1200), points)
        with sqlite3.connect(self.store.path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0], 3)

    def test_failed_import_rolls_back_and_can_retry_without_duplicates(self):
        self.legacy.write_text(json.dumps(self.sample()) + "\n", encoding="utf-8")
        original_import = self.store._import_legacy

        def fail_after_import(conn):
            original_import(conn)
            raise OSError("interrupted import")

        with patch.object(self.store, "_import_legacy", side_effect=fail_after_import):
            with self.assertRaises(OSError):
                self.store.prepare()
        self.assertEqual(len(self.store.load("host-a", self.now - 3600, 1200)), 1)

    def test_query_uses_index_and_only_decodes_bounded_results(self):
        samples = [self.sample(self.now - i, gpu_temperatures_c={"0": 55 + i % 20, "2": 70}) for i in range(3000)]
        samples += [self.sample(self.now - i, alias="host-b") for i in range(3000)]
        self.store.record(samples, self.now)
        with patch("gnvitop.history.json.loads", wraps=json.loads) as decode:
            points = self.store.load("host-a", self.now - 3600, 1200)
        self.assertEqual(len(points), 1200)
        self.assertEqual(decode.call_count, 1200)
        self.assertEqual(points[0]["timestamp"], self.now - 2999)
        self.assertEqual(points[-1]["timestamp"], self.now)
        self.assertEqual(points[-1]["gpu_temperatures_c"], {"0": 55, "2": 70})
        self.assertEqual(points, sorted(points, key=lambda p: p["timestamp"]))
        self.assertEqual({p["alias"] for p in points}, {"host-a"})
        self.assertEqual(len(self.store.load("host-a", self.now - 10, 1200)), 11)
        with sqlite3.connect(self.store.path) as conn:
            plan = conn.execute(
                "EXPLAIN QUERY PLAN SELECT id FROM samples WHERE alias = ? AND timestamp >= ? ORDER BY timestamp, id",
                ("host-a", self.now - 3600),
            ).fetchall()
        self.assertTrue(any("COVERING INDEX samples_host_time" in row[-1] for row in plan))

    def test_readers_do_not_wait_for_a_writer_transaction(self):
        self.store.record([self.sample(gpu_temperatures_c={"0": 50})], self.now)
        with sqlite3.connect(self.store.path) as writer:
            writer.execute("BEGIN IMMEDIATE")
            writer.execute("DELETE FROM samples")
            with ThreadPoolExecutor(max_workers=1) as pool:
                points = pool.submit(self.store.load, "host-a", self.now - 3600, 1200).result(timeout=3)
        self.assertEqual(len(points), 1)

    def test_concurrent_initialization_reads_and_writes(self):
        self.legacy.write_text(json.dumps(self.sample(self.now - 1)) + "\n", encoding="utf-8")
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = []
            for i in range(12):
                futures.append(pool.submit(self.store.record, [self.sample(self.now + i)], self.now))
                futures.append(pool.submit(self.store.load, "host-a", self.now - 3600, 1200))
            for future in futures:
                future.result(timeout=5)
        self.assertEqual(len(self.store.load("host-a", self.now - 3600, 1200)), 13)

    def test_retention_and_empty_store(self):
        self.assertEqual(self.store.load("host-a", 0, 1200), [])
        self.store.record([self.sample(self.now - 8 * 86400), self.sample()], self.now)
        self.assertEqual(len(self.store.load("host-a", 0, 1200)), 1)
        self.store.record([self.sample(self.now + 8 * 86400)], self.now + 8 * 86400)
        self.assertEqual(len(self.store.load("host-a", 0, 1200)), 1)

    def test_temperature_sampling_and_api_ranges(self):
        host = {"alias": "host-a", "status": "ok", "gpus": [
            {"index": index, "temperature_c": value}
            for index, value in enumerate([50, "70.4", None, -1, "N/A", float("nan"), float("inf"), 0])
        ]}
        with patch.object(server, "HISTORY_PATH", str(self.legacy)), patch.object(server, "_history_store", None):
            server.record_history([host], self.now - 7200)
            server.record_history([host], self.now)
            client = server.app.test_client()
            self.assertEqual(client.get("/api/history").status_code, 400)
            for key, count in [("1h", 1), ("6h", 2), ("24h", 2), ("7d", 2), ("invalid", 1)]:
                response = client.get("/api/history", query_string={"host": "host-a", "range": key})
                self.assertEqual(response.status_code, 200)
                points = response.get_json()["points"]
                self.assertEqual(len(points), count)
                self.assertEqual(points[-1]["gpu_temperatures_c"], {
                    "0": 50, "1": 70.4, "2": None, "3": None, "4": None, "5": None, "6": None, "7": 0,
                })
                self.assertNotIn("gpu_temp_avg_c", points[-1])
                self.assertNotIn("gpu_temp_max_c", points[-1])
            self.assertEqual(client.get("/api/history?host=unknown").get_json()["points"], [])
        for values in [[], [None, -1, "N/A"]]:
            sample = server._history_sample({"gpus": [
                {"index": i, "temperature_c": v} for i, v in enumerate(values)
            ]}, self.now)
            self.assertEqual(sample["gpu_temperatures_c"], {str(i): None for i in range(len(values))})

    def test_temperatures_stay_with_gpu_index_when_cards_reorder_or_disappear(self):
        def host(gpus):
            return {"alias": "host-a", "gpus": [{"index": i, "temperature_c": t} for i, t in gpus]}

        with patch.object(server, "HISTORY_PATH", str(self.legacy)), patch.object(server, "_history_store", None):
            server.record_history([host([(2, 72), (0, 50)])], self.now - 30)
            server.record_history([host([(0, 51), (2, 73)])], self.now - 20)
            server.record_history([host([(2, 74)])], self.now - 10)
            server.record_history([host([])], self.now)
            server._history_store = None  # Reopen the persisted store.
            points = server.app.test_client().get("/api/history?host=host-a").get_json()["points"]
        self.assertEqual([point["gpu_temperatures_c"] for point in points], [
            {"0": 50, "2": 72}, {"0": 51, "2": 73}, {"2": 74}, {},
        ])


if __name__ == "__main__":
    unittest.main()
