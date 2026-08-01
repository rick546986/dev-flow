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


if __name__ == "__main__":
    unittest.main()
