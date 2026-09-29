"""MR gate(`gates: MR:` + mr-gate)的牙:設定解析 fail-loud、pass／各 fail 條件／insufficient_data／off、
可設定的資料量地板、沒有 key 時 rerank 照原順序(不變)。零網路;fixture 分數是 synthetic。"""
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

from devflow_jev import JevError, gate, policy

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(SCRIPTS)
FIX = os.path.join(SCRIPTS, "fixtures", "devflow-jev")
RUNTIME = os.path.join(SCRIPTS, "devflow-jev.py")


def _load_runtime():
    spec = importlib.util.spec_from_file_location("devflow_jev_cli_mr", RUNTIME)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RT = _load_runtime()


def fixture(name):
    with open(os.path.join(FIX, name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


class MROptinParse(unittest.TestCase):
    def test_scalar_form(self):
        out = gate.parse_optin("mode: shadow\ngates:\n  J1: live\n  MR: shadow\n")
        self.assertEqual(out["mr"], {"level": "shadow", "min_queries": None})
        self.assertEqual(out["gates"], {"J1": "live"})             # MR 不進 J-gate dict

    def test_block_form_with_min_queries(self):
        out = gate.parse_optin("mode: live\ngates:\n  MR:\n    level: live\n    min_queries: 30\n  J5: shadow\n")
        self.assertEqual(out["mr"], {"level": "live", "min_queries": 30})
        self.assertEqual(out["gates"], {"J5": "shadow"})

    def test_block_level_only_and_block_then_top_level(self):
        out = gate.parse_optin("gates:\n  MR:\n    level: off\nmode: shadow\n")
        self.assertEqual((out["mode"], out["mr"]), ("shadow", {"level": "off", "min_queries": None}))

    def test_absent_is_none(self):
        self.assertIsNone(gate.parse_optin("mode: live\n")["mr"])
        self.assertIsNone(gate.parse_optin("mode: live\ngates:\n  J1: live\n")["mr"])

    def test_malformed_mr_config_fails_loud(self):
        bad = {
            "block without level": "mode: live\ngates:\n  MR:\n    min_queries: 20\n",
            "empty block at eof": "mode: live\ngates:\n  MR:\n",
            "empty block then J": "mode: live\ngates:\n  MR:\n  J1: live\n",
            "bad scalar level": "mode: live\ngates:\n  MR: on\n",
            "bad block level": "mode: live\ngates:\n  MR:\n    level: always\n",
            "unknown key": "mode: live\ngates:\n  MR:\n    level: shadow\n    threshold: 0.5\n",
            "min_queries zero": "mode: live\ngates:\n  MR:\n    level: shadow\n    min_queries: 0\n",
            "min_queries negative": "mode: live\ngates:\n  MR:\n    level: shadow\n    min_queries: -3\n",
            "min_queries float": "mode: live\ngates:\n  MR:\n    level: shadow\n    min_queries: 1.5\n",
            "min_queries text": "mode: live\ngates:\n  MR:\n    level: shadow\n    min_queries: twenty\n",
            "min_queries empty": "mode: live\ngates:\n  MR:\n    level: shadow\n    min_queries:\n",
            "duplicate MR": "mode: live\ngates:\n  MR: shadow\n  MR: live\n",
            "duplicate key": "mode: live\ngates:\n  MR:\n    level: shadow\n    level: live\n",
            "4-space key outside MR": "mode: live\ngates:\n  J1: live\n    level: shadow\n",
            "6-space indent": "mode: live\ngates:\n  MR:\n      level: shadow\n",
            "tab indent": "mode: live\ngates:\n  MR:\n\tlevel: shadow\n",
            "MR at top level": "mode: live\nMR: shadow\n",
        }
        for label, text in bad.items():
            with self.assertRaises(JevError, msg=label):
                gate.parse_optin(text)

    def test_existing_j_gate_parsing_unchanged(self):
        self.assertEqual(gate.parse_optin("mode: shadow\ngates:\n  J1: live\n  J5: live\n"),
                         {"mode": "shadow", "gates": {"J1": "live", "J5": "live"}, "mr": None})
        with self.assertRaises(JevError):
            gate.parse_optin("mode: live\ngates:\n  J9: live\n")
        self.assertEqual(gate.effective_level("J5", True, gate.parse_optin("mode: live\ngates:\n  J5: live\n"))[0],
                         "shadow")

    def test_template_parses_and_enables_nothing(self):
        with open(os.path.join(ROOT, "_templates", "jev.yaml"), encoding="utf-8") as fh:
            out = gate.parse_optin(fh.read())
        self.assertEqual(out["mode"], "off")
        # 範本不寫死 min_queries(未校準):不寫 = mr-gate 用預設,來源記 default
        self.assertEqual(out["mr"], {"level": "off", "min_queries": None})
        self.assertEqual(policy.mr_level(True, out)[0], "off")

    def test_template_min_queries_is_commented_not_hardcoded(self):
        with open(os.path.join(ROOT, "_templates", "jev.yaml"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertNotRegex(text, r"(?m)^\s*min_queries:\s*\d")
        self.assertRegex(text, r"(?m)^\s*#\s*min_queries:")

    def test_template_mr_only_minimal_example_parses(self):
        # 範本裡「只開 MR、J gate 全 off」那段取消註解後:J1–J5 全 off、MR shadow
        with open(os.path.join(ROOT, "_templates", "jev.yaml"), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        start = lines.index("# mode: shadow")
        block = []
        for line in lines[start:]:
            if line.strip() == "#":
                break
            block.append(line[2:])
        out = gate.parse_optin("\n".join(block) + "\n")
        for g in ("J1", "J2", "J3", "J4", "J5"):
            self.assertEqual(gate.effective_level(g, True, out)[0], "off", g)
        self.assertEqual(policy.mr_level(True, out)[0], "shadow")

    def test_inline_comment_after_value_is_fail_loud(self):
        # 文件範例不得寫 `MR: shadow  # 簡寫`:解析器不剝行尾註解 → exit 2
        with self.assertRaises(JevError):
            gate.parse_optin("mode: shadow\ngates:\n  MR: shadow            # 簡寫\n")

    def test_mode_off_makes_mr_off(self):
        out = gate.parse_optin("mode: off\ngates:\n  MR: shadow\n")
        self.assertEqual(policy.mr_level(True, out)[0], "off")

    def test_docs_describe_true_shadow(self):
        # owner 2026-09-29:shadow 不改回傳順序 —— 文件不得再說 shadow 會改排序,且要講到 shadow_top
        for rel in (("docs", "dev", "jev-gate", "w11-mr-rerank.md"), ("skills", "dev-flow", "SKILL.md"),
                    ("docs", "dev", "readme-contract-extract.md"), ("_templates", "jev.yaml")):
            with open(os.path.join(ROOT, *rel), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("會改排序", text, rel)
            self.assertNotIn("會照分數改排序", text, rel)
            self.assertIn("shadow_top", text, rel)

    def test_doc_examples_parse(self):
        # w11 §4.7 與 gate.py docstring 的 yaml 範例必須真的能解析(不是只看起來對)
        import re
        with open(os.path.join(ROOT, "docs", "dev", "jev-gate", "w11-mr-rerank.md"), encoding="utf-8") as fh:
            w11 = fh.read()
        sec = w11[w11.index("### 4.7"):]
        blocks = re.findall(r"```yaml\n(.*?)```", sec, re.S)
        self.assertGreaterEqual(len(blocks), 2)
        for blk in blocks:
            for part in textwrap.dedent(blk).split("# 或\n"):
                out = gate.parse_optin(part)
                self.assertIsNotNone(out["mr"], part)
        # §4.2 手寫最小 fixture:形狀對(不是 exit 2)、單條查詢 = insufficient_data(不是通過)
        sec42 = w11[w11.index("### 4.2"):w11.index("### 4.3")]
        fixture = json.loads(re.findall(r"```json\n(.*?)```", sec42, re.S)[1])
        report = policy.mr_eval(fixture)
        self.assertEqual(report["verdict"], "insufficient_data")
        self.assertTrue(any("min_queries" in r for r in report["insufficient"]), report["insufficient"])
        doc = gate.__doc__
        parts = doc[doc.index("    mode: shadow"):doc.index("註解一律自成一行")].split("    # 或")
        for part in parts:
            text = "\n".join(l[4:] for l in part.splitlines() if l.startswith("    ") and "區塊(" not in l)
            if not text.startswith("mode"):
                text = text[text.index("mode"):]
            self.assertIsNotNone(gate.parse_optin(text + "\n")["mr"], text)


class MRLevel(unittest.TestCase):
    def optin(self, mode, mr_level):
        return {"mode": mode, "gates": {}, "mr": {"level": mr_level, "min_queries": None}}

    def test_min_of_mode_and_mr_level(self):
        self.assertEqual(policy.mr_level(True, self.optin("live", "off"))[0], "off")
        self.assertEqual(policy.mr_level(True, self.optin("off", "live"))[0], "off")
        self.assertEqual(policy.mr_level(True, self.optin("shadow", "live"))[0], "shadow")

    def test_live_is_capped_to_shadow(self):
        level, reason = policy.mr_level(True, self.optin("live", "live"))
        self.assertEqual(level, "shadow")
        self.assertIn("mr_live_not_ratified", reason)
        self.assertIs(gate.MR_LIVE_RATIFIED, False)

    def test_dual_gate_unchanged(self):
        self.assertEqual(policy.mr_level(False, self.optin("live", "shadow")), ("off", "no_api_key"))
        self.assertEqual(policy.mr_level(True, None), ("off", "no_project_optin"))

    def test_legacy_without_mr_block_unchanged(self):
        self.assertEqual(policy.mr_level(True, {"mode": "off", "gates": {}, "mr": None}), ("off", "mode=off"))
        self.assertEqual(policy.mr_level(True, {"mode": "live", "gates": {}, "mr": None})[0], "shadow")


class MRGate(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="mr-gate-")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def optin(self, text):
        os.makedirs(os.path.join(self.root, ".dev-flow"), exist_ok=True)
        with open(os.path.join(self.root, ".dev-flow", "jev.yaml"), "w", encoding="utf-8") as fh:
            fh.write(text)

    def gate(self, name, text="mode: shadow\ngates:\n  MR: shadow\n", **kw):
        if text is not None:
            self.optin(text)
        return RT.run_mr_gate(self.root, fixture(name), **kw)

    def cli(self, *args):
        env = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run([sys.executable, RUNTIME, "--root", self.root, "mr-gate", *args],
                              capture_output=True, text=True, env=env)

    def test_pass(self):
        out = self.gate("mr-eval-pass")
        self.assertEqual((out["gate_result"], out["failed_conditions"]), ("pass", []))
        self.assertEqual(out["report"]["verdict"], "pass")
        self.assertEqual((out["min_queries"], out["min_queries_source"]), (20, "default"))

    def test_fail_recall(self):
        out = self.gate("mr-eval-neg-recall-drop")
        self.assertEqual((out["gate_result"], out["failed_conditions"]), ("fail", ["recall_at_5_not_lower"]))

    def test_fail_mrr(self):
        out = self.gate("mr-eval-neg-mrr-small")
        self.assertEqual((out["gate_result"], out["failed_conditions"]), ("fail", ["mrr_gain_at_least_0.05"]))

    def test_fail_mandatory(self):
        out = self.gate("mr-eval-neg-mandatory-overflow")
        self.assertEqual((out["gate_result"], out["failed_conditions"]), ("fail", ["mandatory_retention_100pct"]))

    def test_insufficient_data_is_not_pass_or_fail(self):
        out = self.gate("mr-eval-neg-insufficient")
        self.assertEqual(out["gate_result"], "insufficient_data")
        self.assertTrue(any("min_queries=20" in r for r in out["insufficient"]))
        self.assertEqual(out["failed_conditions"], [])

    def test_no_mandatory_in_pool_is_insufficient(self):
        fx = copy.deepcopy(fixture("mr-eval-pass"))
        for q in fx["queries"]:
            for c in q["candidates"]:
                c.pop("mandatory", None)
                c.pop("fast_path", None)
        self.optin("mode: shadow\ngates:\n  MR: shadow\n")
        out = RT.run_mr_gate(self.root, fx)
        self.assertEqual(out["gate_result"], "insufficient_data")

    def test_level_off_is_not_evaluated(self):
        out = self.gate("mr-eval-neg-recall-drop", "mode: shadow\ngates:\n  MR: off\n")
        self.assertEqual((out["gate_result"], out["report"]), ("off", None))
        out = self.gate("mr-eval-pass", "mode: off\ngates:\n  MR: live\n")
        self.assertEqual(out["gate_result"], "off")

    def test_live_capped_not_enforced_not_live_eligible(self):
        out = self.gate("mr-eval-pass", "mode: live\ngates:\n  MR: live\n")
        self.assertEqual((out["level"], out["requested_level"]), ("shadow", "live"))
        self.assertFalse(out["enforced"])
        self.assertFalse(out["live_eligible"])
        self.assertFalse(out["report"]["live_eligible"])
        self.assertEqual(out["report"]["score_source"], "synthetic")

    def test_missing_optin_fails_loud(self):
        with self.assertRaises(JevError):
            self.gate("mr-eval-pass", text=None)

    def test_missing_gates_mr_fails_loud(self):
        with self.assertRaises(JevError):
            self.gate("mr-eval-pass", "mode: shadow\ngates:\n  J1: live\n")
        with self.assertRaises(JevError):
            self.gate("mr-eval-pass", "mode: shadow\n")

    def test_malformed_gates_mr_fails_loud(self):
        with self.assertRaises(JevError):
            self.gate("mr-eval-pass", "mode: shadow\ngates:\n  MR:\n    min_queries: 5\n")

    def test_yaml_min_queries_takes_effect(self):
        out = self.gate("mr-eval-neg-insufficient", "mode: shadow\ngates:\n  MR:\n    level: shadow\n    min_queries: 5\n")
        self.assertEqual((out["gate_result"], out["min_queries"], out["min_queries_source"]), ("pass", 5, "jev.yaml"))

    def test_cli_min_queries_overrides_yaml(self):
        text = "mode: shadow\ngates:\n  MR:\n    level: shadow\n    min_queries: 5\n"
        out = self.gate("mr-eval-pass", text, min_queries=26)          # pass fixture 有 25 條
        self.assertEqual((out["gate_result"], out["min_queries_source"]), ("insufficient_data", "cli"))
        out = self.gate("mr-eval-pass", text, min_queries=25)
        self.assertEqual(out["gate_result"], "pass")

    def test_invalid_min_queries_param_fails_loud(self):
        for bad in (0, -1, True, 2.5, "20"):
            with self.assertRaises(JevError, msg=repr(bad)):
                self.gate("mr-eval-pass", min_queries=bad)
            with self.assertRaises(JevError, msg=repr(bad)):
                policy.mr_eval(fixture("mr-eval-pass"), min_queries=bad)

    def test_default_threshold_is_still_20_and_marked_uncalibrated(self):
        self.assertEqual(policy.MR_EVAL_MIN_QUERIES, 20)
        report = policy.mr_eval(fixture("mr-eval-pass"))
        self.assertEqual((report["min_queries"], report["min_queries_calibrated"]), (20, False))
        self.assertEqual(policy.mr_eval(fixture("mr-eval-neg-insufficient"), min_queries=5)["verdict"], "pass")

    def test_cli_exit_codes(self):
        self.optin("mode: shadow\ngates:\n  MR: shadow\n")
        for name, code in (("mr-eval-pass", 0), ("mr-eval-neg-recall-drop", 1), ("mr-eval-neg-mrr-small", 1),
                           ("mr-eval-neg-mandatory-overflow", 1), ("mr-eval-neg-insufficient", 3)):
            run = self.cli("--fixture", os.path.join(FIX, name + ".json"))
            self.assertEqual(run.returncode, code, (name, run.stderr))
        run = self.cli("--fixture", os.path.join(FIX, "mr-eval-neg-insufficient.json"), "--min-queries", "5")
        self.assertEqual(run.returncode, 0, run.stderr)
        run = self.cli("--fixture", os.path.join(FIX, "mr-eval-pass.json"), "--min-queries", "0")
        self.assertEqual(run.returncode, 2)
        self.optin("mode: shadow\ngates:\n  MR: sometimes\n")
        run = self.cli("--fixture", os.path.join(FIX, "mr-eval-pass.json"))
        self.assertEqual(run.returncode, 2)
        self.assertIn("gates.MR", run.stderr)
        os.remove(os.path.join(self.root, ".dev-flow", "jev.yaml"))
        run = self.cli("--fixture", os.path.join(FIX, "mr-eval-pass.json"))
        self.assertEqual(run.returncode, 2)

    def test_mr_eval_cli_min_queries(self):
        env = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
        base = [sys.executable, RUNTIME, "--root", self.root, "mr-eval", "--fixture",
                os.path.join(FIX, "mr-eval-neg-insufficient.json")]
        self.assertEqual(subprocess.run(base, capture_output=True, env=env).returncode, 1)
        self.assertEqual(subprocess.run(base + ["--min-queries", "5"], capture_output=True, env=env).returncode, 0)


class MRRerankUnchanged(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="mr-rr-")
        os.makedirs(os.path.join(self.root, ".dev-flow"))
        with open(os.path.join(self.root, ".dev-flow", "jev.yaml"), "w", encoding="utf-8") as fh:
            fh.write("mode: live\ngates:\n  MR:\n    level: live\n    min_queries: 5\n")
        q = fixture("mr-eval-pass")["queries"][0]
        self.payload = {"query": q.get("query", ""), "candidates": q["candidates"]}

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_no_key_falls_back_to_original_order(self):
        out = RT.run_mr_rerank(self.root, self.payload, environ={})
        self.assertEqual((out["mode"], out["fallback_reason"], out["network"]), ("fallback", "no_api_key", False))
        self.assertEqual(out["top"], out["original_top"][:len(out["top"])] if not out["mandatory"]["dropped"]
                         else out["top"])

    def test_mr_off_in_yaml_falls_back_even_with_key(self):
        with open(os.path.join(self.root, ".dev-flow", "jev.yaml"), "w", encoding="utf-8") as fh:
            fh.write("mode: live\ngates:\n  MR: off\n")

        def boom(*a, **k):
            raise AssertionError("gates.MR: off 不得建 transport")
        out = RT.run_mr_rerank(self.root, self.payload, environ={"TYPESAFE_API_KEY": "k"}, transport_factory=boom)
        self.assertEqual((out["mode"], out["network"]), ("fallback", False))
        self.assertIn("gates.MR=off", out["fallback_reason"])


class HardSwitchesStayOff(unittest.TestCase):
    def test_flags(self):
        self.assertIs(RT.GRADUATED, False)
        self.assertIs(gate.J5_LIVE_RATIFIED, False)
        self.assertIs(gate.MR_LIVE_RATIFIED, False)
        self.assertIs(policy.J2_WINDOW_RATIFIED, False)
        self.assertNotIn("MR", gate.GATES)


if __name__ == "__main__":
    unittest.main()
