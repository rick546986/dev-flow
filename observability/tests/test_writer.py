"""十三節測試對應:atomic write(temp+rename)、單一寫入者鎖、seq 連續性。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from devflow_obs import writer  # noqa: E402


class TestAtomicWriteJson(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_writes_and_leaves_no_temp(self):
        p = os.path.join(self.tmp.name, "result.json")
        writer.atomic_write_json(p, {"result": "PASS"})
        with open(p) as f:
            self.assertEqual(json.load(f), {"result": "PASS"})
        leftovers = [f for f in os.listdir(self.tmp.name) if f != "result.json"]
        self.assertEqual(leftovers, [])

    def test_failed_replace_keeps_original(self):
        p = os.path.join(self.tmp.name, "result.json")
        writer.atomic_write_json(p, {"v": 1})
        real_replace = os.replace

        def boom(src, dst):
            raise OSError("simulated crash")

        os.replace = boom
        try:
            with self.assertRaises(OSError):
                writer.atomic_write_json(p, {"v": 2})
        finally:
            os.replace = real_replace
        with open(p) as f:
            self.assertEqual(json.load(f), {"v": 1})


class TestEventWriter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.attempt_dir = os.path.join(self.tmp.name, "attempts", "att_x")

    def test_appends_jsonl_with_auto_seq(self):
        w = writer.EventWriter(self.attempt_dir)
        w.append({"event_type": "attempt_started", "run_id": "run_x"})
        w.append({"event_type": "attempt_completed", "run_id": "run_x"})
        w.close()
        with open(os.path.join(self.attempt_dir, "events.jsonl")) as f:
            lines = f.read().splitlines()
        events = [json.loads(l) for l in lines]
        self.assertEqual([e["seq"] for e in events], [1, 2])
        self.assertEqual(events[0]["event_type"], "attempt_started")

    def test_second_writer_on_same_file_rejected(self):
        w = writer.EventWriter(self.attempt_dir)
        self.addCleanup(w.close)
        with self.assertRaises(writer.AlreadyLocked):
            writer.EventWriter(self.attempt_dir)

    def test_reopen_after_close_continues_seq(self):
        w = writer.EventWriter(self.attempt_dir)
        w.append({"event_type": "attempt_started"})
        w.close()
        w2 = writer.EventWriter(self.attempt_dir)
        w2.append({"event_type": "attempt_completed"})
        w2.close()
        with open(os.path.join(self.attempt_dir, "events.jsonl")) as f:
            lines = f.read().splitlines()
        self.assertEqual([json.loads(l)["seq"] for l in lines], [1, 2])

    def test_stale_lock_detectable(self):
        w = writer.EventWriter(self.attempt_dir)
        # 模擬 crash:不走 close()(鎖檔留存);僅收檔柄免 ResourceWarning
        w._fh.close()
        del w
        self.assertTrue(writer.has_stale_lock(self.attempt_dir))


if __name__ == "__main__":
    unittest.main()
