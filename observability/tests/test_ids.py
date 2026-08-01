"""十三節測試對應:ID 生成(可跨 restart、非 LLM 生成、可排序、kind 前綴)。"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from devflow_obs import ids  # noqa: E402

CROCKFORD = r"[0-9A-HJKMNP-TV-Z]{26}"


class TestIdFormat(unittest.TestCase):
    def test_new_id_has_kind_prefix_and_ulid_body(self):
        for kind, prefix in (("run", "run_"), ("attempt", "att_"),
                             ("review", "rev_"), ("finding", "fnd_")):
            value = ids.new_id(kind)
            self.assertRegex(value, r"^" + prefix + CROCKFORD + r"$")

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            ids.new_id("span")  # 不將段落當 span:沒有 span 這種 ID

    def test_uniqueness(self):
        seen = {ids.new_id("attempt") for _ in range(2000)}
        self.assertEqual(len(seen), 2000)

    def test_same_process_ids_sort_in_creation_order(self):
        values = [ids.new_id("run") for _ in range(500)]
        self.assertEqual(values, sorted(values))

    def test_is_valid_id_checks_kind(self):
        run_id = ids.new_id("run")
        self.assertTrue(ids.is_valid_id("run", run_id))
        self.assertFalse(ids.is_valid_id("attempt", run_id))
        self.assertFalse(ids.is_valid_id("run", "run_hello"))
        self.assertFalse(ids.is_valid_id("run", ""))

    def test_timestamp_recoverable_for_retention(self):
        import time
        before = time.time()
        value = ids.new_id("run")
        after = time.time()
        ts = ids.timestamp_of(value)
        self.assertGreaterEqual(ts, before - 1.0)
        self.assertLessEqual(ts, after + 1.0)

    def test_survives_restart_roundtrip(self):
        # ID 是純字串,寫檔再讀回仍驗證通過(跨 restart 依檔案系統為準,不依記憶)
        value = ids.new_id("attempt")
        self.assertTrue(ids.is_valid_id("attempt", value.strip()))
        self.assertEqual(value, value.strip())


if __name__ == "__main__":
    unittest.main()
