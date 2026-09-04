"""CLI 煙霧測試 + 靜態 fixture 完整性(fixture 即 schema 的活文件)。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "devflow-obs.py")
FIXTURES = os.path.join(HERE, "..", "fixtures")
R1 = os.path.join(FIXTURES, "runs", "run_01JG8C4V2M0000000000000R01")
R2 = os.path.join(FIXTURES, "runs", "run_01JG8C4V2M0000000000000R02")
LEGACY = os.path.join(FIXTURES, "legacy", "6-implementation-notes-sample.md")
REGISTRY = os.path.join(FIXTURES, "prompt-registry.json")


def run_cli(*args):
    return subprocess.run([sys.executable, CLI, *args],
                          capture_output=True, text=True)


class TestCli(unittest.TestCase):
    def test_validate_fixture_runs_clean(self):
        p = run_cli("validate", R1, R2)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_validate_registry_clean(self):
        p = run_cli("validate-registry", REGISTRY)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_incomplete_lists_crashed_attempt(self):
        p = run_cli("incomplete", R1)
        self.assertEqual(p.returncode, 0)
        out = json.loads(p.stdout)
        self.assertEqual(out[os.path.basename(R1)],
                         ["att_01JG8C4V2M0000000000000A03"])

    def test_derive_in_copied_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = os.path.join(tmp, "r2")
            shutil.copytree(R2, dst)
            p = run_cli("derive", dst)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            derived = os.path.join(dst, "derived", "run-events.jsonl")
            self.assertTrue(os.path.exists(derived))
            with open(derived) as f:
                lines = f.read().splitlines()
            self.assertTrue(all(json.loads(l) for l in lines))

    def test_stats_over_fixtures_and_legacy(self):
        p = run_cli("stats", "--run", R1, "--run", R2, "--legacy-md", LEGACY,
                    "--min-n", "5")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        agg = json.loads(p.stdout)
        self.assertEqual(agg["meta"]["legacy_tasks_n"], 3)
        self.assertEqual(agg["first_pass_success_rate"]["n"], 6)
        self.assertIn("stage6_pass_stage7_blocker_rate", agg)

    def test_recommend_smoke(self):
        p = run_cli("recommend", "--run", R1, "--run", R2, "--min-n", "5")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        out = json.loads(p.stdout)
        self.assertIn("recommendations", out)
        self.assertIn("skipped_insufficient_sample", out)

    def test_repair_dry_run_then_apply_on_corrupted_copy(self):
        # #103:壞 run 有出口。複製一份乾淨 fixture,中間插一行壞 JSON(非
        # 截尾),經真正的 CLI subprocess 跑 dry-run(不動檔案)→ --apply
        # (隔離壞行、原檔留乾淨前綴)→ validate 轉綠。
        with tempfile.TemporaryDirectory() as tmp:
            dst = os.path.join(tmp, "r2")
            shutil.copytree(R2, dst)
            coord = os.path.join(dst, "coordinator", "events.jsonl")
            with open(coord) as f:
                lines = f.read().splitlines()
            self.assertGreaterEqual(len(lines), 2)
            with open(coord, "w") as f:
                f.write(lines[0] + "\n")
                f.write("{this is not valid json\n")
                f.write("\n".join(lines[1:]) + "\n")
            with open(coord, "rb") as f:
                before = f.read()

            p = run_cli("validate", dst)
            self.assertEqual(p.returncode, 1)
            self.assertIn("run_error", p.stdout)

            p = run_cli("repair", dst)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            plan = json.loads(p.stdout)
            self.assertFalse(plan["apply"])
            self.assertTrue(plan["corrupt_found"])
            self.assertEqual(plan["items"][0]["code"], "would_repair")
            with open(coord, "rb") as f:
                self.assertEqual(f.read(), before)  # dry-run 沒動檔案

            p = run_cli("repair", dst, "--apply")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            result = json.loads(p.stdout)
            self.assertTrue(result["apply"])
            item = result["items"][0]
            self.assertEqual(item["code"], "repaired")
            self.assertTrue(os.path.exists(item["quarantined_to"]))
            with open(item["quarantined_to"], "rb") as f:
                self.assertEqual(f.read(), before)  # 隔離檔含原始全部 bytes

            p = run_cli("validate", dst)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
