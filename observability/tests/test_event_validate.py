"""十三節測試對應:event schema 驗證、Prompt Version、隱私欄位禁止、
parent attempt 關聯格式、hook 寫入者欄位限制。"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from devflow_obs import event_validate as ev  # noqa: E402

RUN = "run_01JG8C4V2M0000000000000001"
ATT = "att_01JG8C4V2M0000000000000002"
ATT2 = "att_01JG8C4V2M0000000000000003"
REV = "rev_01JG8C4V2M0000000000000004"
FND = "fnd_01JG8C4V2M0000000000000005"
SHA256 = "sha256:" + "a" * 64

PROMPT = {"id": "stage6-worker", "version": "3.1.0", "hash": SHA256}


def base(event_type, **extra):
    e = {
        "schema": "devflow-agent-event/1",
        "seq": 1,
        "timestamp": "2026-08-02T01:00:00+08:00",
        "run_id": RUN,
        "event_type": event_type,
        "writer": "coordinator",
    }
    e.update(extra)
    return e


def attempt_completed(**over):
    e = base("attempt_completed",
             stage="6-implementation", task_id="T-2",
             attempt_id=ATT, agent_role="worker", model="haiku",
             prompt=copy.deepcopy(PROMPT),
             context_manifest_hash=SHA256,
             base_sha="abc1234", candidate_sha="def5678",
             result="FAIL", failure_category="IMPL", verify_exit_code=1)
    e.update(over)
    return e


def codes(errors):
    return {err["code"] for err in errors}


class TestEnvelope(unittest.TestCase):
    def test_valid_sample_event_passes(self):
        self.assertEqual(ev.validate_event(attempt_completed()), [])

    def test_missing_common_field(self):
        e = attempt_completed()
        del e["timestamp"]
        self.assertIn("missing_field", codes(ev.validate_event(e)))

    def test_unknown_event_type(self):
        e = base("paragraph_span_started")
        self.assertIn("unknown_event_type", codes(ev.validate_event(e)))

    def test_timestamp_requires_timezone_offset(self):
        e = attempt_completed(timestamp="2026-08-02T01:00:00")
        self.assertIn("invalid_format", codes(ev.validate_event(e)))

    def test_run_id_pattern_enforced(self):
        e = attempt_completed(run_id="run-123")
        self.assertIn("invalid_format", codes(ev.validate_event(e)))

    def test_unknown_top_level_field_rejected_unless_x_prefixed(self):
        e = attempt_completed(surprise="hello")
        self.assertIn("unknown_field", codes(ev.validate_event(e)))
        e2 = attempt_completed(x_experiment="wave-2")
        self.assertEqual(ev.validate_event(e2), [])

    def test_non_dict_rejected(self):
        self.assertIn("bad_json", codes(ev.validate_event("not a dict")))


class TestPerEventRequirements(unittest.TestCase):
    def test_attempt_started_requires_prompt_and_model(self):
        e = base("attempt_started", stage="6-implementation", task_id="T-1",
                 attempt_id=ATT, agent_role="worker", base_sha="abc1234")
        got = codes(ev.validate_event(e))
        self.assertIn("missing_field", got)

    def test_attempt_started_full_passes(self):
        e = base("attempt_started", stage="6-implementation", task_id="T-1",
                 attempt_id=ATT, agent_role="worker", model="haiku",
                 prompt=copy.deepcopy(PROMPT), base_sha="abc1234",
                 context_manifest_hash=SHA256)
        self.assertEqual(ev.validate_event(e), [])

    def test_parent_attempt_id_pattern(self):
        e = base("attempt_started", stage="6-implementation", task_id="T-1",
                 attempt_id=ATT2, parent_attempt_id="T-1-retry",
                 agent_role="worker", model="sonnet",
                 prompt=copy.deepcopy(PROMPT), base_sha="abc1234")
        self.assertIn("invalid_format", codes(ev.validate_event(e)))

    def test_fail_without_failure_category_rejected(self):
        e = attempt_completed()
        del e["failure_category"]
        self.assertIn("missing_field", codes(ev.validate_event(e)))

    def test_pass_without_failure_category_ok(self):
        e = attempt_completed(result="PASS")
        del e["failure_category"]
        del e["verify_exit_code"]
        self.assertEqual(ev.validate_event(e), [])

    def test_failure_category_enum(self):
        e = attempt_completed(failure_category="OOPS")
        self.assertIn("invalid_enum", codes(ev.validate_event(e)))

    def test_task_escalated_requires_models_and_category(self):
        e = base("task_escalated", stage="6-implementation", task_id="T-1",
                 attempt_id=ATT, from_model="haiku")
        self.assertIn("missing_field", codes(ev.validate_event(e)))
        e.update(to_model="sonnet", failure_category="IMPL")
        self.assertEqual(ev.validate_event(e), [])

    def test_review_completed_requires_verdict(self):
        e = base("review_completed", stage="6-implementation",
                 review_id=REV, attempt_id=ATT, round=1)
        self.assertIn("missing_field", codes(ev.validate_event(e)))
        e["review_verdict"] = "PASS"
        self.assertEqual(ev.validate_event(e), [])

    def test_finding_created_requires_severity(self):
        e = base("finding_created", stage="7-review", finding_id=FND,
                 review_id=REV, severity="blocker",
                 task_id="T-2", scenario_ids=["S-3"])
        self.assertEqual(ev.validate_event(e), [])
        e2 = base("finding_created", stage="7-review", finding_id=FND,
                  review_id=REV)
        self.assertIn("missing_field", codes(ev.validate_event(e2)))

    def test_verification_layer_completed(self):
        e = base("verification_layer_completed", stage="7-review",
                 layer="gauntlet-mutation", result="FAIL", exit_code=1)
        self.assertEqual(ev.validate_event(e), [])

    def test_mechanical_gate_completed_violation_enum(self):
        e = base("mechanical_gate_completed", writer="hook",
                 gate="postbash-detect", result="FAIL", violation="scope")
        self.assertEqual(ev.validate_event(e), [])
        e2 = base("mechanical_gate_completed", writer="hook",
                  gate="postbash-detect", result="FAIL", violation="vibes")
        self.assertIn("invalid_enum", codes(ev.validate_event(e2)))


class TestPromptVersion(unittest.TestCase):
    def test_prompt_requires_id_version_hash(self):
        e = attempt_completed(prompt={"id": "stage6-worker"})
        self.assertIn("missing_field", codes(ev.validate_event(e)))

    def test_prompt_version_must_be_semver(self):
        e = attempt_completed(prompt={"id": "stage6-worker", "version": "v3",
                                      "hash": SHA256})
        self.assertIn("invalid_format", codes(ev.validate_event(e)))

    def test_prompt_hash_must_be_sha256(self):
        e = attempt_completed(prompt={"id": "stage6-worker", "version": "3.1.0",
                                      "hash": "md5:abc"})
        self.assertIn("invalid_format", codes(ev.validate_event(e)))

    def test_prompt_id_slug_pattern(self):
        e = attempt_completed(prompt={"id": "Stage 6 Worker!", "version": "3.1.0",
                                      "hash": SHA256})
        self.assertIn("invalid_format", codes(ev.validate_event(e)))


class TestTaskTags(unittest.TestCase):
    """6.3:task_tags 受控 enum(正本 = repo 根 devflow-contract.json,12 值),
    多選陣列,非 enum 拒收,每值 ≤50。"""

    CONTRACT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "devflow-contract.json")

    def contract_tags(self):
        import json
        with open(self.CONTRACT) as f:
            return json.load(f)["task_tags"]

    def test_valid_multi_select_passes_on_attempt_events(self):
        started = base("attempt_started", stage="6-implementation",
                       task_id="T-1", attempt_id=ATT, agent_role="worker",
                       model="haiku", prompt=copy.deepcopy(PROMPT),
                       base_sha="abc1234", task_tags=["api", "test"])
        self.assertEqual(ev.validate_event(started), [])
        dispatched = base("agent_dispatched", stage="6-implementation",
                          task_id="T-1", attempt_id=ATT, agent_role="worker",
                          model="haiku", prompt=copy.deepcopy(PROMPT),
                          task_tags=["security"])
        self.assertEqual(ev.validate_event(dispatched), [])
        completed = attempt_completed(task_tags=["database", "migration"])
        self.assertEqual(ev.validate_event(completed), [])

    def test_all_contract_values_accepted_and_are_twelve(self):
        tags = self.contract_tags()
        self.assertEqual(len(tags), 12)
        for tag in tags:
            e = attempt_completed(task_tags=[tag])
            self.assertEqual(ev.validate_event(e), [], msg=tag)

    def test_non_enum_value_rejected(self):
        e = attempt_completed(task_tags=["vibes"])
        errors = ev.validate_event(e)
        self.assertIn("invalid_enum", codes(errors))

    def test_free_string_not_array_rejected(self):
        e = attempt_completed(task_tags="api")
        self.assertIn("invalid_format", codes(ev.validate_event(e)))

    def test_overlong_tag_rejected_with_field_and_limit(self):
        e = attempt_completed(task_tags=["z" * 60])
        errors = ev.validate_event(e)
        hits = [err for err in errors if err["field"].startswith("task_tags")]
        self.assertTrue(hits)
        self.assertTrue(any("50" in err["msg"] for err in hits
                            if err["code"] == "invalid_format"))

    def test_enum_source_is_contract_file(self):
        # 正本防漂移:schema 解析出的 enum 必須 == devflow-contract.json 的 12 值
        self.assertEqual(ev.task_tags_enum(), self.contract_tags())


class TestHookWriterRestrictions(unittest.TestCase):
    """§7:不要求 hooks 推測 Agent Role 或 Prompt Version → 機械禁止其填寫。"""

    def test_hook_may_not_claim_agent_role_or_prompt(self):
        e = base("tool_completed", writer="hook", tool_name="Bash", exit_code=0,
                 agent_role="worker")
        self.assertIn("hook_forbidden_field", codes(ev.validate_event(e)))
        e2 = base("tool_completed", writer="hook", tool_name="Bash", exit_code=0,
                  prompt=copy.deepcopy(PROMPT))
        self.assertIn("hook_forbidden_field", codes(ev.validate_event(e2)))

    def test_hook_tool_event_ok_without_attribution(self):
        e = base("tool_completed", writer="hook", tool_name="Bash", exit_code=2,
                 session_ref="sess-9f2c")
        self.assertEqual(ev.validate_event(e), [])


class TestPrivacy(unittest.TestCase):
    """六節:schema 要能拒絕禁載欄位。"""

    def test_forbidden_exact_keys_rejected(self):
        for key in ("prompt_body", "prompt_text", "transcript", "messages",
                    "source_code", "production_log"):
            e = attempt_completed(**{"x_meta": {key: "leak"}})
            self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)),
                          msg=key)

    def test_forbidden_substring_keys_rejected(self):
        for key in ("api_token", "client_secret", "db_password",
                    "authorization_header", "patient_name"):
            e = attempt_completed(**{"x_meta": {key: "leak"}})
            self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)),
                          msg=key)

    def test_allowlisted_keys_pass(self):
        e = attempt_completed(x_meta={"estimated_tokens": 1234,
                                      "transcript_ref": SHA256})
        self.assertEqual(ev.validate_event(e), [])

    def test_overlong_string_value_rejected(self):
        e = attempt_completed(x_meta={"note": "x" * 5000})
        self.assertIn("privacy_value_too_long", codes(ev.validate_event(e)))


class TestGauntletContract(unittest.TestCase):
    """ID-10:D/C 事件契約合流 —— final_fresh_run_* 兩事件 + 四值 status。
    相容方案(測試釘住):status 為正式欄;舊 result(PASS|FAIL)保留為相容
    別名(Wave2 fixture 形狀);至少擇一,兩者並存必須一致。"""

    def layer_completed(self, **over):
        e = base("verification_layer_completed", writer="verifier",
                 stage="7-review", layer="unit",
                 command_ref="pytest -q", result_summary="17 passed, 0 failed",
                 artifact_ref="derived/unit-report.txt", source_sha="def5678")
        e.update(over)
        return e

    def test_final_fresh_run_started_valid(self):
        e = base("final_fresh_run_started", writer="verifier", stage="7-review",
                 source_sha="def5678", round=1)
        self.assertEqual(ev.validate_event(e), [])

    def test_final_fresh_run_started_requires_source_sha(self):
        e = base("final_fresh_run_started", writer="verifier", stage="7-review")
        self.assertIn("missing_field", codes(ev.validate_event(e)))

    def test_final_fresh_run_completed_valid(self):
        e = base("final_fresh_run_completed", writer="verifier", stage="7-review",
                 verdict="FAIL", layers_total=5, layers_failed=1,
                 source_sha="def5678")
        self.assertEqual(ev.validate_event(e), [])

    def test_final_fresh_run_completed_requires_layer_counts(self):
        e = base("final_fresh_run_completed", writer="verifier", stage="7-review",
                 verdict="PASS", source_sha="def5678")
        self.assertIn("missing_field", codes(ev.validate_event(e)))

    def test_four_status_values_valid(self):
        for status in ("pass", "fail", "unverified", "n-a"):
            e = self.layer_completed(status=status)
            self.assertEqual(ev.validate_event(e), [], msg=status)

    def test_unknown_status_rejected(self):
        e = self.layer_completed(status="maybe")
        self.assertIn("invalid_enum", codes(ev.validate_event(e)))

    def test_missing_both_status_and_result_rejected(self):
        e = self.layer_completed()
        self.assertIn("missing_field", codes(ev.validate_event(e)))

    def test_legacy_result_only_still_valid(self):
        # Wave2 fixture 形狀(scripts/fixtures/vnext-integration):不得破壞
        e = base("verification_layer_completed", writer="verifier",
                 stage="7-review", layer="full-suite", result="PASS",
                 exit_code=0, evidence_ref="final-fresh-run.log")
        self.assertEqual(ev.validate_event(e), [])

    def test_status_result_agreement(self):
        ok = self.layer_completed(status="fail", result="FAIL")
        self.assertEqual(ev.validate_event(ok), [])
        bad = self.layer_completed(status="pass", result="FAIL")
        self.assertIn("inconsistent_fields", codes(ev.validate_event(bad)))
        bad2 = self.layer_completed(status="unverified", result="PASS")
        self.assertIn("inconsistent_fields", codes(ev.validate_event(bad2)))

    def test_result_summary_must_be_one_short_line(self):
        long = self.layer_completed(status="pass", result_summary="x" * 500)
        self.assertIn("invalid_format", codes(ev.validate_event(long)))
        multiline = self.layer_completed(status="pass",
                                         result_summary="ok\nFAILED details...")
        self.assertIn("invalid_format", codes(ev.validate_event(multiline)))

    def test_privacy_scan_still_applies_to_gauntlet_events(self):
        e = self.layer_completed(status="pass", x_meta={"api_token": "sk-1"})
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)))


class TestContextManifest(unittest.TestCase):
    def good(self):
        return {
            "schema": "devflow-context-manifest/1",
            "context_packet_version": "1.0.0",
            "files_count": 4,
            "scenario_count": 3,
            "estimated_tokens": 5200,
            "included_artifacts": ["docs/dev/foo/4-spec.md",
                                   "docs/dev/foo/5-tasks.md"],
            "contract_hash": SHA256,
            "living_spec_hash": SHA256,
        }

    def test_good_manifest_passes(self):
        self.assertEqual(ev.validate_context_manifest(self.good()), [])

    def test_missing_counts_rejected(self):
        m = self.good()
        del m["files_count"]
        self.assertIn("missing_field", codes(ev.validate_context_manifest(m)))

    def test_privacy_scan_applies(self):
        m = self.good()
        m["x_extra"] = {"api_token": "sk-123"}
        self.assertIn("privacy_forbidden_key",
                      codes(ev.validate_context_manifest(m)))

    def test_manifest_hash_stable(self):
        h1 = ev.context_manifest_hash(self.good())
        h2 = ev.context_manifest_hash(dict(reversed(list(self.good().items()))))
        self.assertEqual(h1, h2)
        self.assertRegex(h1, r"^sha256:[0-9a-f]{64}$")


class TestPromptRegistry(unittest.TestCase):
    def good(self):
        return {
            "schema": "devflow-prompt-registry/1",
            "prompts": {
                "stage6-worker": {
                    "current_version": "3.1.0",
                    "versions": [
                        {"version": "3.0.0", "prompt_hash": SHA256,
                         "source_sha": "abc1234", "change_class": "major",
                         "changed": "初版", "approved_by": "rick"},
                        {"version": "3.1.0", "prompt_hash": SHA256,
                         "source_sha": "abc1235", "change_class": "minor",
                         "changed": "新增回報欄位", "approved_by": "rick"},
                    ],
                }
            },
        }

    def test_good_registry_passes(self):
        self.assertEqual(ev.validate_prompt_registry(self.good()), [])

    def test_current_version_must_exist(self):
        r = self.good()
        r["prompts"]["stage6-worker"]["current_version"] = "9.9.9"
        self.assertIn("registry_inconsistent",
                      codes(ev.validate_prompt_registry(r)))

    def test_duplicate_version_rejected(self):
        r = self.good()
        vs = r["prompts"]["stage6-worker"]["versions"]
        vs.append(dict(vs[-1]))
        self.assertIn("registry_inconsistent",
                      codes(ev.validate_prompt_registry(r)))

    def test_change_class_enum(self):
        r = self.good()
        r["prompts"]["stage6-worker"]["versions"][0]["change_class"] = "huge"
        self.assertIn("invalid_enum", codes(ev.validate_prompt_registry(r)))


if __name__ == "__main__":
    unittest.main()
