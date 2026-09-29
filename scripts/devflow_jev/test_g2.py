"""G2 自動審查上線的牙(契約 §7「G2 自動放行」「G2 轉人條件」「G2 provenance」)。

零外部網路:Jev 一律走 FakeTransport;機械檢查真的跑 scripts/check-spec-gate.sh 與 hooks/_stage3_impl.py。
治具 4-spec 取自 example/contract-expiry-reminder(check-spec-gate 全過、Risk: high、full lane)。
"""
import importlib.util
import json
import os
import re
import shutil
import tempfile
import unittest

from devflow_jev import JevError, g2auto, gate, policy
from devflow_jev.transport import FakeClock, FakeTransport, canned_response

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(SCRIPTS)
EXAMPLE_SPEC = os.path.join(ROOT, "example", "contract-expiry-reminder", "4-spec.md")
SLUG = "demo"
GOOD_PATHS = "src/contracts/handler.go, tests/contracts/"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


JEV = _load("devflow_jev_cli", os.path.join(SCRIPTS, "devflow-jev.py"))
GATE = _load("devflow_gate_mod", os.path.join(SCRIPTS, "devflow_gate.py"))
HOOKLIB = _load("devflow_hooklib", os.path.join(ROOT, "hooks", "devflow-lib.py"))


def jev_answers(choice="AUTO_PASS", p_auto=0.9, risk=1):
    """合法的 G2R Jev 回應:AUTO_PASS 機率 = p_auto,其餘分給另外兩個選項(和 = 1)。"""
    rest = 1.0 - p_auto
    if choice == "AUTO_PASS":
        probs = {"AUTO_PASS": p_auto, "HUMAN_REVIEW": rest * 2 / 3, "REQUEST_CHANGES": rest / 3}
    else:
        probs = {c: 0.0 for c in policy.G2R_JEV_CHOICES}
        probs.update({"AUTO_PASS": p_auto, choice: rest})
    return canned_response(policy.G2R_QUESTIONS, {
        "g2_route": {"choice": choice, "probabilities": probs},
        "risk": {"score": risk}})


def base_case(**over):
    case = {"slug": SLUG, "declared_paths": ["src/app/handler.py"], "spec_risk": "normal",
            "owner_calls_unresolved": 0, "demo_verdict_required": False, "authored_by_present": True,
            "jev": {"g2_route": {"choice": "AUTO_PASS", "probabilities": {"AUTO_PASS": 0.9}}, "risk": {"score": 1}},
            "jev_status": "ok"}
    case.update(over)
    return case


class Repo(object):
    """臨時專案根:docs/dev/demo/4-spec.md(+ 選配 2-decision／Stage 3 檔)+ .dev-flow/jev.yaml。"""

    def __init__(self, paths=GOOD_PATHS, authored="agent:author-1", owner="dev-a", mode="live", risk_line=None):
        self.root = tempfile.mkdtemp(prefix="g2auto-")
        self.dir = os.path.join(self.root, "docs", "dev", SLUG)
        os.makedirs(self.dir)
        with open(EXAMPLE_SPEC, encoding="utf-8") as fh:
            text = fh.read()
        head = "owner: %s\n" % owner + ("authored_by: %s\n" % authored if authored else "")
        text = text.replace("feature: contract-expiry-reminder", "feature: %s" % SLUG, 1)
        text = text.replace("owner: <owner>\n", head, 1)
        if paths is not None:
            text = text.replace("## Diff Budget\n", "## Diff Budget\n- Paths: %s\n" % paths, 1)
        if risk_line is not None:
            text = re.sub(r"^- Risk: high\(", risk_line + "(", text, count=1, flags=re.M)
        self.write("4-spec.md", text)
        if mode is not None:
            os.makedirs(os.path.join(self.root, ".dev-flow"))
            with open(os.path.join(self.root, ".dev-flow", "jev.yaml"), "w", encoding="utf-8") as fh:
                fh.write("mode: %s\n" % mode)
        self.env = {"TYPESAFE_API_KEY": "test-key", "DEVFLOW_PLUGIN": ROOT}

    def write(self, name, text):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, name="4-spec.md"):
        with open(os.path.join(self.dir, name), encoding="utf-8") as fh:
            return fh.read()

    def fm(self, name="4-spec.md"):
        from devflow_jev import attestation
        return attestation.parse_frontmatter(self.read(name))

    def jsonl(self, rel):
        path = os.path.join(self.root, rel)
        if not os.path.isfile(path):
            return []
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def set_mode(self, mode):
        with open(os.path.join(self.root, ".dev-flow", "jev.yaml"), "w", encoding="utf-8") as fh:
            fh.write("mode: %s\n" % mode)

    def g2r(self, script=None, env=None, clock=None):
        transport = FakeTransport(script if script is not None else [{"response": jev_answers()}],
                                  clock=clock)
        self.transport = transport
        return JEV.run_g2r(self.root, SLUG, environ=self.env if env is None else env,
                           transport_factory=lambda *a: transport, clock=clock or FakeClock(),
                           now="2026-09-27T00:00:00Z")

    def release(self, reviewer="agent:reviewer-9"):
        return GATE.write_g2_auto(__import__("pathlib").Path(self.root), SLUG, reviewer,
                                  "docs/dev/demo/g2-agent-review.md", sidecar=False)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


# ───────────────────────────── route_g2(純函式)─────────────────────────────
class RouteG2(unittest.TestCase):
    def test_clean_case_routes_auto_and_auto_is_not_a_pass(self):
        out = policy.route_g2(base_case())
        self.assertEqual(out["route"], "AUTO")
        self.assertEqual(out["reasons"], ["no_human_condition_hit"])
        self.assertFalse(out["is_pass"])
        self.assertFalse(out["writes_verdict"])
        self.assertEqual(out["jev_role"], "router_only")

    def test_jev_human_routes_human(self):
        case = base_case(jev={"g2_route": {"choice": "HUMAN_REVIEW", "probabilities": {"AUTO_PASS": 0.9}},
                              "risk": {"score": 0}})
        self.assertIn("jev_g2_route=HUMAN_REVIEW", policy.route_g2(case)["reasons"])

    def test_jev_request_changes_only_routes_human(self):
        case = base_case(jev={"g2_route": {"choice": "REQUEST_CHANGES", "probabilities": {"AUTO_PASS": 0.9}},
                              "risk": {"score": 0}})
        out = policy.route_g2(case)
        self.assertEqual(out["route"], "HUMAN")
        self.assertFalse(out["writes_verdict"])

    def test_p_exactly_085_goes_to_agent(self):
        case = base_case(jev={"g2_route": {"choice": "AUTO_PASS", "probabilities": {"AUTO_PASS": 0.85}},
                              "risk": {"score": 1}})
        self.assertEqual(policy.route_g2(case)["route"], "AUTO")

    def test_p_08499_goes_to_human(self):
        case = base_case(jev={"g2_route": {"choice": "AUTO_PASS", "probabilities": {"AUTO_PASS": 0.8499}},
                              "risk": {"score": 1}})
        out = policy.route_g2(case)
        self.assertEqual(out["route"], "HUMAN")
        self.assertTrue(any(r.startswith("jev_p_auto_pass_below_threshold") for r in out["reasons"]))

    def test_p_nan_or_missing_goes_to_human(self):
        for p in (float("nan"), None, True):
            case = base_case(jev={"g2_route": {"choice": "AUTO_PASS", "probabilities": {"AUTO_PASS": p}},
                                  "risk": {"score": 1}})
            self.assertEqual(policy.route_g2(case)["route"], "HUMAN", p)

    def test_risk_paths_hit_routes_human(self):
        out = policy.route_g2(base_case(declared_paths=["db/migrations/0001.sql", "src/app.py"]))
        self.assertIn("risk_paths_hit:db/migrations/0001.sql", out["reasons"])

    def test_no_declared_paths_routes_human(self):
        for paths in ([], ["  ", ""]):
            self.assertIn("spec_declares_no_paths", policy.route_g2(base_case(declared_paths=paths))["reasons"])

    def test_jev_risk_2_routes_human(self):
        case = base_case(jev={"g2_route": {"choice": "AUTO_PASS", "probabilities": {"AUTO_PASS": 0.95}},
                              "risk": {"score": 2}})
        self.assertIn("risk>=2(jev=2)", policy.route_g2(case)["reasons"])

    def test_with_jev_spec_risk_high_does_not_raise_risk(self):
        out = policy.route_g2(base_case(spec_risk="high"))
        self.assertEqual(out["route"], "AUTO")
        self.assertEqual(out["signals"]["risk_source"], "jev")

    def test_without_jev_spec_risk_high_counts_as_risk_2(self):
        out = policy.route_g2(base_case(spec_risk="high", jev=None, jev_status="no_jev"))
        self.assertEqual(out["reasons"], ["risk>=2(spec_risk=high)"])
        self.assertEqual(out["signals"]["risk_source"], "spec")

    def test_without_jev_is_noop_clean_case_still_auto(self):
        # ADR 0004 §2:沒有 Jev = no-op,不擋也不放寬 —— 其餘條件都沒命中就交給 agent(+機械檢查)
        out = policy.route_g2(base_case(jev=None, jev_status="no_jev"))
        self.assertEqual(out["route"], "AUTO")
        self.assertFalse(any("jev" in r for r in out["reasons"]))

    def test_without_jev_other_conditions_still_apply(self):
        out = policy.route_g2(base_case(jev=None, jev_status="no_jev", declared_paths=["auth/x.py"]))
        self.assertEqual(out["reasons"], ["risk_paths_hit:auth/x.py"])

    def test_without_jev_spec_risk_medium_is_below_2(self):
        self.assertEqual(policy.route_g2(base_case(spec_risk="medium", jev=None, jev_status="no_jev"))["route"], "AUTO")

    def test_jev_runtime_changed_routes_human(self):
        for path in ("scripts/devflow_jev/policy.py", "scripts/devflow-jev.py", ".dev-flow/jev.yaml",
                     "docs/dev/tools/devflow_jev/gate.py", "scripts/devflow_jev/jev-questions.json"):
            out = policy.route_g2(base_case(declared_paths=["src/app.py", path]))
            self.assertIn("jev_runtime_changed:%s" % path, out["reasons"], path)

    def test_jev_runtime_not_touched_does_not_route_human(self):
        for path in ("src/app.py", "docs/jev-notes.md", "scripts/devflow_gate.py", "hooks/devflow-lib.py"):
            out = policy.route_g2(base_case(declared_paths=[path]))
            self.assertEqual(out["route"], "AUTO", (path, out["reasons"]))

    def test_authored_by_present_does_not_route_human(self):
        self.assertNotIn("authored_by_missing", policy.route_g2(base_case(authored_by_present=True))["reasons"])

    def test_authored_by_missing_routes_human(self):
        self.assertIn("authored_by_missing", policy.route_g2(base_case(authored_by_present=False))["reasons"])

    def test_jev_risk_missing_routes_human(self):
        case = base_case(jev={"g2_route": {"choice": "AUTO_PASS", "probabilities": {"AUTO_PASS": 0.95}}, "risk": {}})
        self.assertIn("jev_risk_missing", policy.route_g2(case)["reasons"])

    def test_owner_call_unresolved_routes_human(self):
        self.assertIn("owner_calls_unresolved=1", policy.route_g2(base_case(owner_calls_unresolved=1))["reasons"])

    def test_demo_verdict_required_routes_human(self):
        self.assertIn("demo_verdict_required", policy.route_g2(base_case(demo_verdict_required=True))["reasons"])

    def test_all_hit_reasons_listed_not_just_first(self):
        out = policy.route_g2(base_case(declared_paths=[], owner_calls_unresolved=2, demo_verdict_required=True,
                                        authored_by_present=False, spec_risk="high", jev=None, jev_status="no_jev"))
        self.assertEqual(len(out["reasons"]), 5)

    def test_case_shape_is_fail_loud(self):
        with self.assertRaises(JevError):
            policy.route_g2({k: v for k, v in base_case().items() if k != "jev_status"})
        with self.assertRaises(JevError):
            policy.route_g2(base_case(jev=None, jev_status="ok"))
        with self.assertRaises(JevError):
            policy.route_g2(base_case(jev=None, jev_status="transport:timeout"))
        with self.assertRaises(JevError):
            policy.route_g2(base_case(spec_risk="High"))


# ───────────────────────────── Risk 欄位(policy 與 hooks 同一規則)─────────────────────────────
RISK_CASES = [
    ("- Risk: high\n", "high"), ("- Risk: High\n", "high"), ("- Risk: HIGH(涉金流)\n", "high"),
    ("- Risk: normal | high(缺省 normal)\n", "normal"), ("- Risk: Medium\n", "medium"), ("- Risk: low\n", "low"),
    ("沒有 Risk 行\n", None),
]
RISK_ERRORS = ["- Risk: hgih\n", "- Risk:\n", "- Risk:   \n", "- Risk: —\n", "- Risk: critical\n", "- Risk: 高\n"]


class SpecRisk(unittest.TestCase):
    def test_policy_case_insensitive(self):
        for text, want in RISK_CASES:
            self.assertEqual(policy.spec_risk_of(text), want, text)

    def test_policy_invalid_or_empty_raises(self):
        for text in RISK_ERRORS:
            with self.assertRaises(JevError, msg=text):
                policy.spec_risk_of(text)

    def test_hooks_case_insensitive_same_as_policy(self):
        for text, want in RISK_CASES:
            self.assertEqual(HOOKLIB.spec_risk_value(text), (want, None), text)
            self.assertEqual(HOOKLIB.spec_profile(text)["risk"], want, text)

    def test_hooks_invalid_or_empty_is_error_not_low(self):
        for text in RISK_ERRORS:
            risk, err = HOOKLIB.spec_risk_value(text)
            self.assertIsNone(risk, text)
            self.assertTrue(err, text)
            self.assertTrue(HOOKLIB.spec_profile(text)["risk_error"], text)

    def test_value_sets_identical(self):
        self.assertEqual(tuple(sorted(HOOKLIB.SPEC_RISK_VALUES)), policy.SPEC_RISK_VALUES)

    def test_first_risk_line_wins(self):
        self.assertEqual(policy.spec_risk_of("- Risk: High\n- Risk: normal\n"), "high")
        self.assertEqual(HOOKLIB.spec_risk_value("- Risk: High\n- Risk: normal\n")[0], "high")

    def test_fast_lane_with_capital_high_is_caught_by_oc4(self):
        prof = HOOKLIB.spec_profile("- lane: fast\n- Risk: HIGH\n")
        self.assertEqual((prof["lane"], prof["risk"]), ("fast", "high"))

    def test_check_spec_gate_red_on_invalid_risk(self):
        repo = Repo(risk_line="- Risk: hgih")
        try:
            code, out, _ = g2auto._run(["bash", os.path.join(ROOT, "scripts", "check-spec-gate.sh"),
                                        os.path.join(repo.dir, "4-spec.md")], repo.root)
            self.assertEqual(code, 1)
            self.assertIn("hgih", out)
        finally:
            repo.cleanup()


# ───────────────────────────── G2R CLI(雙閘門 + Jev 失敗 → HUMAN)─────────────────────────────
class G2RRun(unittest.TestCase):
    """沒有 Jev 的每一種原因 → no-op:routed_by=none、case.jev=None;Risk: normal 的乾淨 spec 仍判 AUTO(不擋)。"""

    def setUp(self):
        self.repo = Repo(risk_line="- Risk: normal")

    def tearDown(self):
        self.repo.cleanup()

    def assertNoJev(self, out, reason_prefix):
        self.assertTrue(str(out["jev_reason"]).startswith(reason_prefix), out["jev_reason"])
        self.assertEqual(out["routed_by"], "none")
        self.assertIsNone(out["case"]["jev"])
        self.assertEqual(out["case"]["jev_status"], "no_jev")
        self.assertEqual(out["route"], "AUTO", out["reasons"])      # 不擋:其餘條件都沒命中
        self.assertIsNone(out["jev_snapshot"])

    def test_live_jev_auto_routes_auto_and_records(self):
        out = self.repo.g2r()
        self.assertEqual(out["route"], "AUTO", out["reasons"])
        self.assertEqual(out["level"], "live")
        self.assertEqual(out["routed_by"], "jev:" + out["evaluation_id"])
        self.assertEqual(self.repo.jsonl(g2auto.G2R_LOG)[-1]["case_hash"], out["case_hash"])

    def test_live_jev_human_routes_human(self):
        out = self.repo.g2r(script=[{"response": jev_answers(choice="HUMAN_REVIEW", p_auto=0.2)}])
        self.assertEqual(out["route"], "HUMAN")
        self.assertTrue(out["routed_by"].startswith("jev:"))

    def test_no_api_key_is_noop_without_network(self):
        out = self.repo.g2r(env={"DEVFLOW_PLUGIN": ROOT})
        self.assertNoJev(out, "no_api_key")
        self.assertFalse(out["network"])
        self.assertEqual(self.repo.transport.calls, [])

    def test_no_api_key_with_spec_risk_high_routes_human(self):
        self.repo.cleanup()
        self.repo = Repo(risk_line="- Risk: HIGH")
        out = self.repo.g2r(env={"DEVFLOW_PLUGIN": ROOT})
        self.assertEqual(out["reasons"], ["risk>=2(spec_risk=high)"])
        self.assertEqual(out["routed_by"], "none")

    def test_no_optin_is_noop(self):
        os.remove(os.path.join(self.repo.root, ".dev-flow", "jev.yaml"))
        self.assertNoJev(self.repo.g2r(), "no_project_optin")
        self.assertEqual(self.repo.transport.calls, [])

    def test_mode_off_is_noop(self):
        self.repo.set_mode("off")
        self.assertNoJev(self.repo.g2r(), "mode=off")

    def test_mode_shadow_calls_but_is_noop_for_routing(self):
        self.repo.set_mode("shadow")
        out = self.repo.g2r(script=[{"response": jev_answers(choice="HUMAN_REVIEW", p_auto=0.1)}])
        self.assertNoJev(out, "level=shadow")
        self.assertEqual(len(self.repo.transport.calls), 1)
        self.assertEqual(out["jev_shadow_answers"]["g2_route"]["choice"], "HUMAN_REVIEW")

    def test_broken_optin_is_noop(self):
        self.repo.set_mode("turbo")
        self.assertNoJev(self.repo.g2r(), "optin_error")

    def test_transport_failure_is_noop(self):
        self.assertNoJev(self.repo.g2r(script=[{"error": "network"}]), "transport:network")

    def test_transport_timeout_is_noop(self):
        self.assertNoJev(self.repo.g2r(script=[{"error": "timeout"}]), "transport:timeout")

    def test_deadline_exceeded_is_noop(self):
        out = self.repo.g2r(script=[{"response": jev_answers(), "latency_s": policy.G2R_DEADLINE_S + 1}],
                            clock=FakeClock())
        self.assertNoJev(out, "deadline_exceeded")

    def test_malformed_response_is_noop(self):
        bad = jev_answers()
        bad["answers"]["g2_route"]["choice"] = "SHIP_IT"
        self.assertNoJev(self.repo.g2r(script=[{"response": bad}]), "transport:schema")

    def test_non_json_response_is_noop(self):
        self.assertNoJev(self.repo.g2r(script=[{"raw_text": "x"}]), "transport:malformed_json")

    def test_breaker_open_is_noop_and_does_not_call(self):
        from devflow_jev.state import StateStore
        store = StateStore(self.repo.root)
        breaker = store.load_breaker()
        breaker.failures["G2R"] = policy.BREAKER_THRESHOLD
        store.save_breaker(breaker)
        self.assertNoJev(self.repo.g2r(), "breaker_open")
        self.assertEqual(self.repo.transport.calls, [])

    def test_consecutive_failures_open_breaker(self):
        for _ in range(policy.BREAKER_THRESHOLD):
            self.repo.g2r(script=[{"error": "http_529"}])
        self.assertNoJev(self.repo.g2r(), "breaker_open")

    def test_budget_exhausted_is_noop_and_does_not_call(self):
        from devflow_jev.state import StateStore, utc_day
        store = StateStore(self.repo.root)
        budget = store.load_budget(utc_day())
        budget.attempts = budget.attempts_cap
        store.save_budget(budget, utc_day())
        self.assertNoJev(self.repo.g2r(), "budget_exhausted")
        self.assertEqual(self.repo.transport.calls, [])

    def test_privacy_hit_does_not_send_and_is_noop(self):
        text = self.repo.read().replace("## Out of Scope", "## Out of Scope\napi_key = abcdefghijkl\n", 1)
        self.repo.write("4-spec.md", text)
        self.assertNoJev(self.repo.g2r(), "privacy_blocked")
        self.assertEqual(self.repo.transport.calls, [])

    def test_invalid_spec_risk_is_fail_loud(self):
        self.repo.write("4-spec.md", self.repo.read().replace("- Risk: normal(", "- Risk: hgih(", 1))
        with self.assertRaises(JevError):
            self.repo.g2r()

    def test_cli_off_path_exit_0_and_no_key_leak(self):
        import subprocess
        env = dict(os.environ, DEVFLOW_PLUGIN=ROOT, PYTHONDONTWRITEBYTECODE="1")
        env.pop("TYPESAFE_API_KEY", None)
        run = subprocess.run(["python3", os.path.join(SCRIPTS, "devflow-jev.py"), "--root", self.repo.root, "g2r",
                              "--slug", SLUG, "--no-record"], capture_output=True, text=True, env=env)
        self.assertEqual(run.returncode, 0, run.stderr)
        out = json.loads(run.stdout)
        self.assertEqual((out["routed_by"], out["jev_reason"], out["network"]), ("none", "no_api_key", False))


# ───────────────────────────── write-g2-auto(agent PASS + 機械檢查 + 未命中轉人條件)─────────────────────────────
class G2AutoRelease(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.cleanup()

    def assertBlocked(self, fragment, reviewer="agent:reviewer-9"):
        before = self.repo.read()
        with self.assertRaises(ValueError) as ctx:
            self.repo.release(reviewer)
        self.assertIn(fragment, str(ctx.exception))
        self.assertEqual(self.repo.read(), before, "被擋下時 md 不得改")
        self.assertEqual(self.repo.jsonl(JEV.G2M_RELEASE_LOG), [], "被擋下時不得記 agent 放行")

    def test_agent_pass_plus_mechanical_releases_and_records_misrelease_denominator(self):
        routed = self.repo.g2r()
        out = self.repo.release()
        fm = self.repo.fm()
        self.assertEqual(fm["verdict"], "PASS")
        self.assertEqual(fm["verdict_source"], "fresh_agent_reviewer")
        self.assertEqual(fm["attested_by"], "agent:reviewer-9")
        self.assertEqual(fm["g2_mode"], "auto")
        self.assertEqual(fm["routed_by"], "jev:" + routed["evaluation_id"])
        self.assertEqual(fm["g2r_case"], routed["case_hash"])
        self.assertTrue(fm["mechanical"].startswith("sha256:"))
        releases = self.repo.jsonl(JEV.G2M_RELEASE_LOG)
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]["case_hash"], routed["case_hash"])
        self.assertEqual(releases[0]["reported_by"], "agent:reviewer-9")
        self.assertEqual(out["g2_misrelease_release"], [JEV.G2M_RELEASE_LOG.replace(os.sep, "/")])
        report = JEV.run_g2_misrelease_report(self.repo.root)
        self.assertEqual((report["agent_released"], report["misreleased"], report["misrelease_rate"]), (1, 0, 0.0))
        self.assertIsNone(report["threshold"])
        self.assertFalse(report["auto_revert"])

    def test_released_doc_passes_static_recheck_without_local_log(self):
        self.repo.g2r()
        self.repo.release()
        shutil.rmtree(os.path.join(self.repo.root, ".devflow"))
        kind, problems = g2auto.classify_gate_doc("4-spec", self.repo.fm())
        self.assertEqual((kind, problems), ("auto", []))
        self.assertEqual(g2auto.auto_release_problems(self.repo.root, SLUG, self.repo.fm(),
                                                      environ=self.repo.env), [])

    def test_no_g2r_record_blocks(self):
        self.assertBlocked("沒有 G2R 分流紀錄")

    def test_jev_human_blocks_agent_verdict(self):
        self.repo.g2r(script=[{"response": jev_answers(choice="HUMAN_REVIEW", p_auto=0.1)}])
        self.assertBlocked("jev_g2_route=HUMAN_REVIEW")

    def test_p_08499_blocks_agent_verdict(self):
        self.repo.g2r(script=[{"response": jev_answers(p_auto=0.8499)}])
        self.assertBlocked("jev_p_auto_pass_below_threshold")

    def test_p_085_is_released_to_agent(self):
        self.repo.g2r(script=[{"response": jev_answers(p_auto=0.85)}])
        self.assertEqual(self.repo.release()["g2_mode"], "auto")

    def test_risk_paths_hit_blocks_agent_verdict(self):
        self.repo.write("4-spec.md", self.repo.read().replace(GOOD_PATHS, "db/migrations/0003.sql, src/app.py", 1))
        self.repo.g2r()
        self.assertBlocked("risk_paths_hit:db/migrations/0003.sql")

    def test_no_declared_paths_blocks_agent_verdict(self):
        self.repo.write("4-spec.md", self.repo.read().replace("- Paths: %s\n" % GOOD_PATHS, "", 1))
        self.repo.g2r()
        self.assertBlocked("spec_declares_no_paths")

    def test_placeholder_paths_count_as_not_declared(self):
        self.repo.write("4-spec.md", self.repo.read().replace(GOOD_PATHS, "<逗號分隔,如 src/app/handler.py>", 1))
        self.repo.g2r()
        self.assertBlocked("spec_declares_no_paths")

    def test_jev_risk_2_blocks_agent_verdict(self):
        self.repo.g2r(script=[{"response": jev_answers(risk=2)}])
        self.assertBlocked("risk>=2(jev=2)")

    def test_with_jev_spec_risk_high_does_not_block(self):
        self.assertEqual(policy.spec_risk_of(self.repo.read()), "high")
        self.repo.g2r(script=[{"response": jev_answers(risk=1)}])
        self.assertEqual(self.repo.release()["g2_mode"], "auto")

    def test_owner_call_unresolved_blocks_agent_verdict(self):
        self.repo.write("2-decision.md", "---\nstatus: approved\n---\n## Owner Calls\n"
                        "| OC | 決定了什麼 | 為什麼 | 依據 | 若被推翻 | 狀態 |\n|---|---|---|---|---|---|\n"
                        "| OC-1 | 卡片只顯示 10 筆 | 防過長 | [Assumption] | UI 改 | 待人審 |\n## 下一節\n")
        self.repo.g2r()
        self.assertBlocked("owner_calls_unresolved=1")

    def test_resolved_owner_calls_do_not_block(self):
        self.repo.write("2-decision.md", "---\nstatus: approved\n---\n## Owner Calls\n"
                        "| OC | 決定了什麼 | 為什麼 | 依據 | 若被推翻 | 狀態 |\n|---|---|---|---|---|---|\n"
                        "| OC-1 | 卡片只顯示 10 筆 | 防過長 | [Assumption] | UI 改 | ✅ |\n"
                        "| OC-2 |  |  |  |  |  |\n## 下一節\n")
        self.repo.g2r()
        self.assertEqual(self.repo.release()["g2_mode"], "auto")

    def test_demo_verdict_required_blocks_agent_verdict(self):
        self.repo.write("1-discussion.md", "---\nstatus: approved\n---\n## Real-world Context\n- 人要操作\n")
        self.repo.write("3-prototype.md", "---\nstatus: approved\n---\n## Stage 3 觸發判定\n"
                        "- [x] 新前端流程\n- [ ] 改變下一步\n## User Demo Feedback\n"
                        "- Human verdict: ACCEPTED\n- Verdict attestation: human:ada @ 2026-09-27\n")
        self.repo.g2r()
        self.assertBlocked("demo_verdict_required")

    def test_no_jev_releases_with_routed_by_none(self):
        # ADR 0004 §2:沒有 key → 只靠 fresh agent PASS + 機械檢查;例子 spec 的 Risk 改成 normal 才不命中 risk ≥ 2
        self.repo.cleanup()
        self.repo = Repo(risk_line="- Risk: normal")
        self.repo.g2r(env={"DEVFLOW_PLUGIN": ROOT})
        self.assertEqual(self.repo.release()["routed_by"], "none")
        fm = self.repo.fm()
        self.assertEqual((fm["routed_by"], fm["g2r_jev"], fm["g2_mode"]), ("none", "none", "auto"))
        self.assertEqual(self.repo.jsonl(JEV.G2M_RELEASE_LOG)[0]["routed_by"], "none")
        shutil.rmtree(os.path.join(self.repo.root, ".devflow"))
        self.assertEqual(g2auto.auto_release_problems(self.repo.root, SLUG, self.repo.fm(), environ=self.repo.env), [])

    def test_no_jev_spec_risk_high_blocks_agent_verdict(self):
        self.repo.g2r(env={"DEVFLOW_PLUGIN": ROOT})
        self.assertBlocked("risk>=2(spec_risk=high)")

    def test_no_jev_spec_risk_capital_high_blocks_agent_verdict(self):
        self.repo.write("4-spec.md", self.repo.read().replace("- Risk: high(", "- Risk: High(", 1))
        self.repo.g2r(env={"DEVFLOW_PLUGIN": ROOT})
        self.assertBlocked("risk>=2(spec_risk=high)")

    def test_jev_failure_is_noop_not_a_block(self):
        self.repo.cleanup()
        self.repo = Repo(risk_line="- Risk: normal")
        self.repo.g2r(script=[{"error": "timeout"}])
        self.assertEqual(self.repo.release()["routed_by"], "none")

    def test_jev_failure_does_not_relax_other_conditions(self):
        self.repo.write("4-spec.md", self.repo.read().replace(GOOD_PATHS, "payments/charge.go", 1))
        self.repo.g2r(script=[{"raw_text": "not json"}])
        self.assertBlocked("risk_paths_hit:payments/charge.go")

    def test_no_jev_invalid_spec_risk_is_error_not_release(self):
        self.repo.write("4-spec.md", self.repo.read().replace("- Risk: high(", "- Risk: hgih(", 1))
        with self.assertRaises(JevError):
            self.repo.g2r(env={"DEVFLOW_PLUGIN": ROOT})
        self.assertBlocked("沒有 G2R 分流紀錄")

    def test_jev_runtime_changed_blocks_agent_verdict(self):
        self.repo.write("4-spec.md", self.repo.read().replace(GOOD_PATHS, "scripts/devflow_jev/policy.py, src/app.py", 1))
        self.repo.g2r()
        self.assertBlocked("jev_runtime_changed:scripts/devflow_jev/policy.py")

    def test_author_equals_approver_blocks(self):
        self.repo.g2r()
        self.assertBlocked("author == approver", reviewer="agent:author-1")

    def test_author_equals_approver_case_insensitive(self):
        self.repo.g2r()
        self.assertBlocked("author == approver", reviewer="agent:Author-1")

    def test_owner_as_approver_blocks(self):
        self.repo.g2r()
        self.assertBlocked("approver 是本檔 owner", reviewer="agent:dev-a")

    def test_missing_authored_by_blocks(self):
        self.repo.cleanup()
        self.repo = Repo(authored=None)
        routed = self.repo.g2r()
        self.assertIn("authored_by_missing", routed["reasons"])
        self.assertBlocked("缺 authored_by")

    def test_jev_as_reviewer_blocks(self):
        self.repo.g2r()
        self.assertBlocked("Jev 只分流", reviewer="agent:jev-1")

    def test_human_reviewer_rejected_on_agent_path(self):
        self.repo.g2r()
        self.assertBlocked("只收 agent:<id>", reviewer="human:ada")

    def test_spec_changed_after_routing_blocks(self):
        self.repo.g2r()
        self.repo.write("4-spec.md", self.repo.read().replace(GOOD_PATHS, "src/contracts/other.go", 1))
        self.assertBlocked("g2r_case 與現在的 spec 重算結果不同")

    def test_mechanical_check_failure_blocks(self):
        self.repo.g2r()
        text = re.sub(r"^- 觀測:.*\n", "", self.repo.read(), count=1, flags=re.M)
        self.repo.write("4-spec.md", text)
        self.assertBlocked("機械檢查 check-spec-gate 沒過")

    def test_global_kill_switch_blocks(self):
        self.repo.g2r()
        old = g2auto.G2_AUTO_LIVE
        g2auto.G2_AUTO_LIVE = False
        try:
            self.assertBlocked("G2_AUTO_LIVE=False")
        finally:
            g2auto.G2_AUTO_LIVE = old

    def test_kill_switch_does_not_retro_flag_released_spec(self):
        # 退回人審只擋之後的 write-g2-auto;已放行的 4-spec 事後掃描照舊過(不回頭打紅)
        self.repo.g2r()
        self.repo.release()
        old = g2auto.G2_AUTO_LIVE
        g2auto.G2_AUTO_LIVE = False
        try:
            self.assertEqual(g2auto.classify_gate_doc("4-spec", self.repo.fm())[0], "auto")
            self.assertEqual(g2auto.auto_release_problems(self.repo.root, SLUG, self.repo.fm(),
                                                          environ=self.repo.env), [])
        finally:
            g2auto.G2_AUTO_LIVE = old

    def test_second_release_of_same_case_rejected(self):
        self.repo.g2r()
        self.repo.release()
        with self.assertRaises(ValueError):
            self.repo.release("agent:reviewer-10")
        self.assertEqual(len(self.repo.jsonl(JEV.G2M_RELEASE_LOG)), 1)


# ───────────────────────────── 事後掃描:手改頂欄繞過寫入器 ─────────────────────────────
class StaticRecheck(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.cleanup()

    def forge(self, **over):
        fm = {"verdict": "PASS", "verdict_source": "fresh_agent_reviewer", "attested_by": "agent:reviewer-9",
              "authored_by": "agent:author-1", "owner": "dev-a", "g2_mode": "auto",
              "routed_by": "jev:g2r-20260927T000000Z-deadbeef", "mechanical": "sha256:" + "0" * 64,
              "g2r_jev": "AUTO_PASS p=0.9 risk=1"}
        case = g2auto.build_case(self.repo.root, SLUG, jev=g2auto.parse_jev_snapshot(fm["g2r_jev"]),
                                 environ=self.repo.env)
        fm["g2r_case"] = policy.g2r_case_hash(case)
        fm.update(over)
        return g2auto.auto_release_problems(self.repo.root, SLUG, fm, environ=self.repo.env)

    def test_forged_clean_auto_passes_static(self):
        self.assertEqual(self.forge(), [])

    def test_forged_auto_on_risk_path_spec_is_red(self):
        self.repo.write("4-spec.md", self.repo.read().replace(GOOD_PATHS, "auth/login.py", 1))
        self.assertTrue(any("risk_paths_hit" in p for p in self.forge()))

    def test_forged_auto_with_low_jev_confidence_is_red(self):
        self.assertTrue(any("jev_p_auto_pass_below_threshold" in p for p in self.forge(g2r_jev="AUTO_PASS p=0.8499 risk=1")))

    def test_forged_auto_without_jev_on_high_risk_spec_is_red(self):
        problems = self.forge(routed_by="none", g2r_jev="none")
        self.assertTrue(any("risk>=2(spec_risk=high)" in p for p in problems), problems)

    def test_forged_routed_by_jev_without_snapshot_is_red(self):
        self.assertTrue(any("沒有 g2r_jev 快照" in p for p in self.forge(g2r_jev="none")))

    def test_forged_routed_by_missing_is_red(self):
        self.assertTrue(any("routed_by" in p for p in self.forge(routed_by="")))

    def test_g2_mode_auto_with_human_source_is_invalid(self):
        kind, _ = g2auto.classify_gate_doc("4-spec", {"verdict": "PASS", "verdict_source": "human_attested",
                                                       "attested_by": "human:ada", "g2_mode": "auto"})
        self.assertEqual(kind, "auto")          # 走 auto 判定 → 下面必紅
        self.assertTrue(any("verdict_source" in p for p in self.forge(verdict_source="human_attested",
                                                                       attested_by="human:ada")))

    def test_g2_mode_auto_with_human_attested_by_is_invalid(self):
        self.assertTrue(any("不是 agent:<id>" in p for p in self.forge(attested_by="human:ada")))

    def test_forged_author_equals_approver_is_red(self):
        self.assertTrue(any("author == approver" in p for p in self.forge(attested_by="agent:author-1")))

    def test_owner_self_review_agent_with_auto_mode_is_red(self):
        # 冒人簽 + g2_mode: auto:classify 先判 bad(不走 auto),auto_release_problems 也不放行
        fm = {"verdict": "PASS", "verdict_source": "owner_self_review", "attested_by": "agent:reviewer-9",
              "g2_mode": "auto"}
        self.assertEqual(g2auto.classify_gate_doc("4-spec", fm)[0], "bad")
        self.assertTrue(any("verdict_source" in p for p in self.forge(verdict_source="owner_self_review")))

    def test_agent_verdict_without_auto_mode_is_red(self):
        self.assertTrue(any("g2_mode" in p for p in self.forge(g2_mode="human")))


# ───────────────────────────── G1/G3 只收人寫的 verdict ─────────────────────────────
class HumanOnlyG1G3(unittest.TestCase):
    def test_g1_g3_agent_verdict_source_is_red(self):
        for stage in ("2-decision", "7-review"):
            kind, problems = g2auto.classify_gate_doc(stage, {"verdict": "PASS", "verdict_source": "fresh_agent_reviewer",
                                                              "attested_by": "agent:reviewer-9"})
            self.assertEqual(kind, "bad", stage)
            self.assertTrue(problems, stage)

    def test_g1_g3_g2_mode_is_red(self):
        kind, _ = g2auto.classify_gate_doc("7-review", {"verdict": "PASS", "verdict_source": "human_attested",
                                                         "attested_by": "human:ada", "g2_mode": "auto"})
        self.assertEqual(kind, "bad")

    def test_g1_g3_human_verdict_ok(self):
        for stage in ("2-decision", "7-review"):
            kind, problems = g2auto.classify_gate_doc(stage, {"verdict": "PASS", "verdict_source": "human_attested",
                                                              "attested_by": "human:ada"})
            self.assertEqual((kind, problems), ("human", []), stage)

    def test_human_sources_with_agent_attested_by_are_red_on_every_stage(self):
        # 人簽冒充:owner_self_review／human_attested + attested_by: agent:… 不得被當 human(G1/G2/G3 皆然)
        for stage in ("2-decision", "4-spec", "7-review"):
            for src in g2auto.HUMAN_SOURCES:
                for by in ("agent:some-agent", "agent:reviewer-9"):
                    kind, problems = g2auto.classify_gate_doc(stage, {"verdict": "PASS", "verdict_source": src,
                                                                      "attested_by": by})
                    self.assertEqual(kind, "bad", (stage, src, by))
                    self.assertTrue(any("human:" in p for p in problems), problems)

    def test_owner_self_review_with_human_prefix_still_human(self):
        for stage in ("2-decision", "4-spec", "7-review"):
            kind, problems = g2auto.classify_gate_doc(stage, {"verdict": "PASS", "verdict_source": "owner_self_review",
                                                              "attested_by": "human:ada"})
            self.assertEqual((kind, problems), ("human", []), stage)

    def test_gate_writer_rejects_agent_reviewer_for_every_stage(self):
        import pathlib
        tmp = tempfile.mkdtemp()
        try:
            for stage in ("2-decision", "4-spec", "7-review"):
                d = os.path.join(tmp, "docs", "dev", "s")
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, stage + ".md"), "w") as fh:
                    fh.write("---\nstatus: in-review\nverdict:\n---\n# x\n")
                for who in ("agent:reviewer-9", "jev-1"):
                    with self.assertRaises(ValueError, msg=(stage, who)):
                        GATE.write_verdict(pathlib.Path(tmp), "s", stage, "PASS", reviewer=who, sidecar=False)
                    with open(os.path.join(d, stage + ".md"), encoding="utf-8") as fh:
                        self.assertEqual(GATE.read_canonical_verdict(fh.read()), "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_gate_writer_marks_human_source(self):
        import pathlib
        tmp = tempfile.mkdtemp()
        try:
            d = os.path.join(tmp, "docs", "dev", "s")
            os.makedirs(d)
            with open(os.path.join(d, "7-review.md"), "w") as fh:
                fh.write("---\nstatus: in-review\nverdict:\n---\n# x\n")
            GATE.write_verdict(pathlib.Path(tmp), "s", "7-review", "PASS", reviewer="ada", sidecar=False)
            with open(os.path.join(d, "7-review.md"), encoding="utf-8") as fh:
                text = fh.read()
            self.assertRegex(text, r"(?m)^verdict_source: human_attested$")
            self.assertRegex(text, r"(?m)^attested_by: human:ada$")
            self.assertNotIn("g2_mode", text)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_agent_writer_only_takes_4_spec(self):
        self.assertNotIn("stage", GATE.write_g2_auto.__code__.co_varnames[:GATE.write_g2_auto.__code__.co_argcount])


# ───────────────────────────── g2-misrelease(只記錄)─────────────────────────────
class Misrelease(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.routed = self.repo.g2r()
        self.repo.release()

    def tearDown(self):
        self.repo.cleanup()

    def test_g3_root_cause_spec_record_counts_and_rate_only_reported(self):
        JEV.run_g2_misrelease_record(self.repo.root, SLUG, self.routed["case_hash"], "G3", "g3_request_changes",
                                     "docs/dev/demo/7-review.md", "fresh_agent_reviewer", "human:ada")
        report = JEV.run_g2_misrelease_report(self.repo.root)
        self.assertTrue(report["consistent"])
        self.assertEqual((report["misreleased"], report["agent_released"], report["misrelease_rate"]), (1, 1, 1.0))
        self.assertFalse(report["blocks_anything"])
        self.assertEqual(report["gate_effect"], "none")
        self.assertEqual(report["agent_released_by_routed"], {"jev": 1, "none": 0})
        self.assertEqual(report["misreleased_by_routed"], {"jev": 1, "none": 0})

    def test_g3_record_by_agent_rejected(self):
        with self.assertRaises(JevError):
            JEV.run_g2_misrelease_record(self.repo.root, SLUG, self.routed["case_hash"], "G3", "g3_hold",
                                         "docs/dev/demo/7-review.md", "fresh_agent_reviewer", "agent:x")

    def test_record_without_auto_route_rejected(self):
        with self.assertRaises(JevError):
            JEV.run_g2_misrelease_record(self.repo.root, SLUG, "sha256:" + "1" * 64, "implementation", "reverted",
                                         "abc123", "fresh_agent_reviewer", "agent:x")

    def test_release_cli_is_what_the_writer_calls(self):
        with open(os.path.join(SCRIPTS, "devflow_gate.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn('"g2-misrelease", "release"', src)


class G2RQuestionsZhTW(unittest.TestCase):
    """owner 2026-09-29:送 Jev 的 G2R 題目改成繁體中文;只換人讀的文字,結構一個都不動。"""

    def test_structure_unchanged(self):
        q = policy.G2R_QUESTIONS
        self.assertEqual(list(q), ["g2_route", "risk"])
        self.assertEqual((q["g2_route"]["type"], q["risk"]["type"]), ("choice", "score"))
        self.assertEqual(list(q["g2_route"]["criteria"]), list(policy.G2R_JEV_CHOICES))
        self.assertEqual(list(policy.G2R_JEV_CHOICES), ["AUTO_PASS", "HUMAN_REVIEW", "REQUEST_CHANGES"])
        crit = q["risk"]["criteria"]
        self.assertEqual(len(crit), 4)                              # 位置 = level 0–3
        self.assertEqual([c.split(": ", 1)[0] for c in crit], ["cosmetic", "contained", "sensitive", "critical"])
        self.assertEqual(policy.G2R_THRESHOLDS, {"auto_pass_min": 0.85, "risk_human_min": 2})

    def test_text_is_traditional_chinese(self):
        q = policy.G2R_QUESTIONS
        self.assertEqual(q["g2_route"]["text"],
                         "只根據這份變更規格（4-spec）和它宣告的路徑，判斷它適合哪一種 G2 處理方式。"
                         "你只負責分流，不是審查者，你的答案也不是審查結論。")
        self.assertEqual(q["risk"]["text"], "這份規格描述的是哪一種改動？")
        prefixes = {"AUTO_PASS": "自動放行：", "HUMAN_REVIEW": "轉人工：", "REQUEST_CHANGES": "退回修改："}
        for key, prefix in prefixes.items():
            self.assertTrue(q["g2_route"]["criteria"][key].startswith(prefix), key)
        for tag, label in zip(("cosmetic", "contained", "sensitive", "critical"), ("外觀", "局部", "敏感", "關鍵")):
            self.assertTrue(any(c.startswith("%s: %s：" % (tag, label)) for c in q["risk"]["criteria"]), tag)
        texts = [q["g2_route"]["text"], q["risk"]["text"]] + list(q["g2_route"]["criteria"].values()) \
            + list(q["risk"]["criteria"])
        for t in texts:                                             # 不能殘留舊的英文句子
            self.assertIsNone(re.search(r"[A-Za-z]{4,} [A-Za-z]{4,}", t), t)


class LiveSwitchesStayOff(unittest.TestCase):
    def test_flags(self):
        self.assertIs(JEV.GRADUATED, False)
        self.assertIs(gate.J5_LIVE_RATIFIED, False)
        self.assertIs(policy.J2_WINDOW_RATIFIED, False)

    def test_dual_gate_semantics_unchanged(self):
        self.assertEqual(gate.effective_level("J5", False, {"mode": "live", "gates": {}})[0], "off")
        self.assertEqual(gate.effective_level("J5", True, None)[0], "off")
        self.assertEqual(gate.effective_level("J5", True, {"mode": "live", "gates": {"J5": "live"}})[0], "shadow")
        self.assertEqual(JEV.g2r_level(False, {"mode": "live", "gates": {}})[0], "off")
        self.assertEqual(JEV.g2r_level(True, None)[0], "off")
        self.assertEqual(JEV.g2r_level(True, {"mode": "live", "gates": {}})[0], "live")

    def test_g2r_not_in_jev_yaml_gates(self):
        self.assertNotIn("G2R", gate.GATES)
        with self.assertRaises(JevError):
            gate.parse_optin("mode: live\ngates:\n  G2R: live\n")


if __name__ == "__main__":
    unittest.main()
