"""十三節測試對應:stats aggregation、小樣本標示、Stage 6/7 verdict 關聯、
Prompt Version 成功率、Recommendation 只建議不改 Prompt(十節)。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import evtools  # noqa: E402
from devflow_obs import stats  # noqa: E402

RUN_A = evtools.mkid("run", 101)
RUN_B = evtools.mkid("run", 102)
OLD_PROMPT = {"id": "stage6-worker", "version": "3.0.0", "hash": evtools.SHA256}


def dataset():
    """RUN_A:6 個 T(4 first-pass;T-2 升階;T-3 升階+rework)+ scope violation
    + stage6 PASS + stage7 blocker + gauntlet 層。RUN_B:stage6 PASS、7 無 blocker。"""
    fac = evtools.EventFactory(RUN_A)
    events = [fac.ev("run_started", feature_slug="feat-a", base_sha="abc1234"),
              fac.ev("stage_started", stage="6-implementation")]
    plans = {
        "T-1": [("haiku", "PASS", None)],
        "T-2": [("haiku", "FAIL", "IMPL"), ("sonnet", "PASS", None)],
        "T-3": [("haiku", "FAIL", "IMPL"), ("sonnet", "FAIL", "IMPL"),
                ("sonnet", "PASS", None)],
        "T-4": [("haiku", "PASS", None)],
        "T-5": [("haiku", "PASS", None)],
        "T-6": [("haiku", "PASS", None)],
    }
    att_n, rev_n = 1, 1
    for task_id, plan in sorted(plans.items()):
        evs, _ = evtools.task_flow(fac, task_id, plan, att_n, rev_n)
        events += evs
        att_n += len(plan)
        rev_n += len(plan)
    # T-2 出過一次 scope violation(coordinator 轉錄 hook 偵測,帶 task 歸屬)
    events.append(fac.ev("mechanical_gate_completed", gate="postbash-detect",
                         stage="6-implementation", task_id="T-2",
                         result="FAIL", violation="scope"))
    events.append(fac.ev("stage_completed", stage="6-implementation",
                         verdict="PASS"))
    # Gauntlet 層(verifier 寫)
    for result in ("PASS", "PASS", "FAIL"):
        events.append(fac.ev("verification_layer_completed", writer="verifier",
                             stage="7-review", layer="unit", result=result))
    events.append(fac.ev("verification_layer_completed", writer="verifier",
                         stage="7-review", layer="mutation", result="FAIL"))
    # Stage 7:blocker finding → stage6 PASS 後 stage7 blocker 案例
    rev7 = evtools.mkid("rev", 700)
    events.append(fac.ev("review_started", stage="7-review", review_id=rev7,
                         agent_role="reviewer", model="opus"))
    events.append(fac.ev("finding_created", stage="7-review",
                         finding_id=evtools.mkid("fnd", 1), review_id=rev7,
                         severity="blocker", business_finding_id="F-1"))
    events.append(fac.ev("review_completed", stage="7-review", review_id=rev7,
                         review_verdict="FAIL", model="opus", findings_count=1))
    events.append(fac.ev("stage_completed", stage="7-review",
                         verdict="REQUEST_CHANGES"))
    events.append(fac.ev("run_completed", result="FAIL"))

    fac_b = evtools.EventFactory(RUN_B)
    events_b = [fac_b.ev("run_started", feature_slug="feat-b",
                         base_sha="def5678"),
                fac_b.ev("stage_started", stage="6-implementation")]
    evs, _ = evtools.task_flow(fac_b, "T-1", [("haiku", "PASS", None)], 1, 1)
    events_b += evs
    events_b.append(fac_b.ev("stage_completed", stage="6-implementation",
                             verdict="PASS"))
    events_b.append(fac_b.ev("stage_completed", stage="7-review",
                             verdict="PASS"))
    events_b.append(fac_b.ev("run_completed", result="PASS"))
    return {RUN_A: events, RUN_B: events_b}


class TestAggregation(unittest.TestCase):
    def setUp(self):
        self.agg = stats.aggregate_events(dataset(), min_n=5)

    def test_first_pass_success_rate(self):
        m = self.agg["first_pass_success_rate"]
        self.assertEqual(m["n"], 7)                      # 6 + RUN_B 1
        self.assertAlmostEqual(m["value"], 5 / 7)
        self.assertFalse(m["insufficient_sample"])

    def test_mean_attempts_to_acceptance(self):
        m = self.agg["mean_attempts_to_acceptance"]
        self.assertAlmostEqual(m["value"], (1 + 2 + 3 + 1 + 1 + 1 + 1) / 7)

    def test_rework_and_escalation_rate(self):
        self.assertAlmostEqual(self.agg["rework_rate"]["value"], 1 / 7)
        self.assertAlmostEqual(self.agg["escalation_rate"]["value"], 2 / 7)

    def test_failure_category_distribution(self):
        dist = self.agg["failure_category_distribution"]
        self.assertEqual(dist["counts"]["IMPL"], 3)
        self.assertEqual(dist["n"], 3)

    def test_scope_violation_rate(self):
        self.assertAlmostEqual(self.agg["scope_violation_rate"]["value"], 1 / 7)
        self.assertAlmostEqual(
            self.agg["test_integrity_violation_rate"]["value"], 0.0)

    def test_success_by_model(self):
        by_model = self.agg["success_by_model"]
        self.assertAlmostEqual(by_model["haiku"]["value"], 5 / 7)
        self.assertEqual(by_model["haiku"]["n"], 7)
        self.assertFalse(by_model["haiku"]["insufficient_sample"])
        self.assertAlmostEqual(by_model["sonnet"]["value"], 2 / 3)
        self.assertTrue(by_model["sonnet"]["insufficient_sample"])  # n=3 < 5

    def test_success_by_prompt_version(self):
        by_prompt = self.agg["success_by_prompt_version"]
        m = by_prompt["stage6-worker@3.1.0"]
        self.assertEqual(m["n"], 10)                     # 9 + RUN_B 1
        self.assertAlmostEqual(m["value"], 7 / 10)

    def test_stage6_pass_stage7_blocker_rate(self):
        m = self.agg["stage6_pass_stage7_blocker_rate"]
        self.assertEqual(m["n"], 2)
        self.assertAlmostEqual(m["value"], 1 / 2)
        self.assertTrue(m["insufficient_sample"])

    def test_gauntlet_layer_failure_rate(self):
        layers = self.agg["failure_rate_by_gauntlet_layer"]
        self.assertAlmostEqual(layers["unit"]["value"], 1 / 3)
        self.assertAlmostEqual(layers["mutation"]["value"], 1.0)
        self.assertTrue(layers["mutation"]["insufficient_sample"])

    def test_confound_dimensions_reported(self):
        # 九節:分析必須區分模型/Prompt/Context/Spec/環境/Reviewer 嚴格度/Task 風險
        self.assertIn("reviewer_strictness_by_model", self.agg)
        note = self.agg["confound_note"]
        for dim in ("模型", "Prompt", "Context", "Spec", "環境", "Reviewer", "Task"):
            self.assertIn(dim, note)


class TestSmallSample(unittest.TestCase):
    def test_small_dataset_flagged_insufficient(self):
        runs = dataset()
        small = {RUN_B: runs[RUN_B]}
        agg = stats.aggregate_events(small, min_n=5)
        self.assertTrue(agg["first_pass_success_rate"]["insufficient_sample"])
        self.assertEqual(agg["first_pass_success_rate"]["n"], 1)


class TestLegacyRows(unittest.TestCase):
    def test_legacy_rows_join_task_metrics_not_attempt_groups(self):
        legacy = [
            {"task_id": "T-1", "failure_category": None, "escalations": [],
             "rounds": 1, "reason": None, "run_id": None,
             "source": "markdown-legacy"},
            {"task_id": "T-2", "failure_category": "IMPL",
             "escalations": ["haiku", "sonnet"], "rounds": 2, "reason": None,
             "run_id": None, "source": "markdown-legacy"},
        ]
        agg = stats.aggregate_events({}, legacy_rows=legacy, min_n=1)
        self.assertEqual(agg["meta"]["legacy_tasks_n"], 2)
        self.assertEqual(agg["first_pass_success_rate"]["n"], 2)
        self.assertAlmostEqual(agg["first_pass_success_rate"]["value"], 1 / 2)
        self.assertAlmostEqual(agg["escalation_rate"]["value"], 1 / 2)
        self.assertEqual(agg["success_by_model"], {})  # legacy 不冒充 attempt 級

class TestRecommendations(unittest.TestCase):
    def build(self, n_bad, min_n):
        fac = evtools.EventFactory(RUN_A)
        events = [fac.ev("run_started", feature_slug="feat-a",
                         base_sha="abc1234")]
        att_n = 1
        # n_bad 個 T 用舊版 prompt 全 FAIL 後升階成功
        for i in range(n_bad):
            evs, _ = evtools.task_flow(
                fac, f"T-{i + 1}",
                [("haiku", "FAIL", "IMPL"), ("sonnet", "PASS", None)],
                att_n, att_n, prompt=OLD_PROMPT)
            events += evs
            att_n += 2
        agg = stats.aggregate_events({RUN_A: events}, min_n=min_n)
        return stats.recommendations(agg, success_threshold=0.6)

    def test_sufficient_bad_combo_yields_recommendation(self):
        recs = self.build(n_bad=5, min_n=5)
        bad = [r for r in recs["recommendations"]
               if r["prompt"] == "stage6-worker@3.0.0"]
        self.assertEqual(len(bad), 1)
        self.assertTrue(bad[0]["requires_human_approval"])
        self.assertNotIn("auto_apply", bad[0])

    def test_insufficient_sample_skipped_with_label(self):
        recs = self.build(n_bad=2, min_n=5)
        self.assertEqual(recs["recommendations"], [])
        self.assertIn("stage6-worker@3.0.0",
                      [s["prompt"] for s in recs["skipped_insufficient_sample"]])


if __name__ == "__main__":
    unittest.main()
