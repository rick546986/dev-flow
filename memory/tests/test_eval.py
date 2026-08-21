"""Eval harness:確定性、指標齊全、門檻會擋(§32)。"""
import copy
import json
import os

from memtools import MemoryCase
from agentmem import evalharness


class EvalTest(MemoryCase):
    def test_default_dataset_passes(self):
        report = evalharness.run()
        self.assertTrue(report["passed"],
                        [c for c in report["cases"] if not c["passed"]]
                        + report["violations"])

    def test_metrics_are_all_present(self):
        metrics = evalharness.run()["metrics"]
        for name in ("recall_at_5", "mrr", "current_truth_accuracy",
                     "stale_hit_rate", "wrong_branch_rate", "no_hit_precision",
                     "evidence_coverage", "context_size",
                     "retrieval_latency_ms"):
            self.assertIn(name, metrics)

    def test_dataset_covers_three_languages_and_six_kinds(self):
        dataset = evalharness.load_dataset()
        languages = {case.get("language") for case in dataset["cases"]}
        self.assertEqual(languages, {"zh", "en", "mixed"})
        kinds = {case.get("expect_kind") for case in dataset["cases"]}
        for kind in ("CURRENT", "HISTORY", "WHY", "HOW", "DOMAIN", "INTENT"):
            self.assertIn(kind, kinds)

    def test_run_is_deterministic(self):
        first = evalharness.run()["metrics"]
        second = evalharness.run()["metrics"]
        for name, value in first.items():
            if name == "retrieval_latency_ms":
                continue                       # 延遲本來就會抖動
            self.assertEqual(value, second[name], name)

    def test_stale_case_is_detected_not_served(self):
        report = evalharness.run()
        self.assertEqual(report["metrics"]["stale_hit_rate"], 0.0)
        case = [c for c in report["cases"] if c["id"] == "current-stale-port"][0]
        self.assertTrue(case["passed"])

    def test_threshold_violation_fails_the_run(self):
        dataset = copy.deepcopy(evalharness.load_dataset())
        dataset["thresholds"]["recall_at_5"] = 1.01
        path = os.path.join(self.work, "tight.json")
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(dataset, stream, ensure_ascii=False)
        report = evalharness.run(dataset_path=path)
        self.assertFalse(report["passed"])
        self.assertTrue(report["violations"])

    def test_regression_in_chinese_retrieval_is_caught(self):
        """把中文題的期望改成不可能命中 → harness 必須紅(它真的在量東西)。"""
        dataset = copy.deepcopy(evalharness.load_dataset())
        for case in dataset["cases"]:
            if case["id"] == "domain-zh":
                case["expect_refs"] = ["knowledge:does-not-exist"]
        path = os.path.join(self.work, "broken.json")
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(dataset, stream, ensure_ascii=False)
        self.assertFalse(evalharness.run(dataset_path=path)["passed"])

    def test_render_does_not_raise(self):
        evalharness.render(evalharness.run())
