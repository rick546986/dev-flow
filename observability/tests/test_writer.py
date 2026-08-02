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


class TestWriterStatusOnly(unittest.TestCase):
    """6.4:新寫入路徑(writer API)一律只寫 status;result 為讀取相容別名,
    deprecated since 1.x, removed in 2.0。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.w = writer.EventWriter(os.path.join(self.tmp.name, "verifier"))
        self.addCleanup(self.w.close)

    def layer_event(self, **fields):
        e = {"event_type": "verification_layer_completed", "layer": "unit"}
        e.update(fields)
        return e

    def test_result_only_input_normalized_to_status(self):
        rec = self.w.append(self.layer_event(result="PASS"))
        self.assertEqual(rec["status"], "pass")
        self.assertNotIn("result", rec)
        rec2 = self.w.append(self.layer_event(result="FAIL"))
        self.assertEqual(rec2["status"], "fail")
        self.assertNotIn("result", rec2)

    def test_consistent_pair_drops_result(self):
        rec = self.w.append(self.layer_event(status="fail", result="FAIL"))
        self.assertEqual(rec["status"], "fail")
        self.assertNotIn("result", rec)

    def test_inconsistent_pair_refused(self):
        with self.assertRaises(ValueError):
            self.w.append(self.layer_event(status="pass", result="FAIL"))

    def test_unmappable_result_refused(self):
        with self.assertRaises(ValueError):
            self.w.append(self.layer_event(result="ABORTED"))

    def test_written_file_contains_no_result_on_layer_events(self):
        self.w.append(self.layer_event(result="PASS"))
        self.w.append(self.layer_event(status="n-a"))
        path = os.path.join(self.tmp.name, "verifier", "events.jsonl")
        with open(path) as f:
            events = [json.loads(l) for l in f.read().splitlines()]
        self.assertTrue(all("result" not in e for e in events))
        self.assertEqual([e["status"] for e in events], ["pass", "n-a"])

    def test_other_events_keep_result_untouched(self):
        rec = self.w.append({"event_type": "attempt_completed",
                             "attempt_id": "att_x", "result": "FAIL"})
        self.assertEqual(rec["result"], "FAIL")
        self.assertNotIn("status", rec)


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
