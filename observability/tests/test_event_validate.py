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
        "schema": "devflow-agent-event/1.1",
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


class TestSchemaVersion11(unittest.TestCase):
    """1.1 版本鉤子:schema_version 與 devflow-contract.json 握手值一致;
    envelope schema 值收 1.x(舊 /1 = 1.0 讀取相容),拒異 major。"""

    HERE = os.path.dirname(os.path.abspath(__file__))
    SCHEMA = os.path.join(HERE, "..", "schema", "agent-event.schema.json")
    CONTRACT = os.path.join(HERE, "..", "..", "devflow-contract.json")

    def test_schema_version_is_1_1_and_matches_contract(self):
        import json
        with open(self.SCHEMA) as f:
            schema = json.load(f)
        with open(self.CONTRACT) as f:
            contract = json.load(f)
        self.assertEqual(schema["schema_version"], "1.1")
        self.assertEqual(contract["schema_versions"]["agent_event"], "1.1")

    def test_envelope_accepts_1_1_and_legacy_1(self):
        for value in ("devflow-agent-event/1.1", "devflow-agent-event/1"):
            e = attempt_completed(schema=value)
            self.assertEqual(ev.validate_event(e), [], msg=value)

    def test_envelope_rejects_other_major(self):
        e = attempt_completed(schema="devflow-agent-event/2")
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

    def test_x_prefix_cannot_bypass_forbidden_key(self):
        e = attempt_completed(x_transcript="full chat log")
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)))

    def test_double_x_prefix_cannot_bypass_forbidden_key(self):
        # #98 PR #110 回歸:剝一層時 x_x_transcript 對 forbidden_exact 免疫。
        e = attempt_completed(x_x_transcript="full chat log")
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)),
                      msg="x_ 前綴須剝到底,不是只剝一層")

    def test_nested_transcript_key_still_rejected(self):
        e = attempt_completed(x_meta={"transcript": "full chat log"})
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)))

    def test_double_underscore_x_prefix_cannot_bypass_forbidden_key(self):
        # r2-#98 F1:while low.startswith("x_") 一次只剝 2 個字元,遇
        # x__transcript(單 x、雙底線)剝出的是 "_transcript"(前面多一個底線),
        # 對 forbidden_exact 完全免疫。改成 regex 一次吃掉整段
        # (x + 1 個以上底線) 的重複前綴才擋得住。
        for key in ("x__transcript", "x___messages"):
            e = attempt_completed(**{key: "leak"})
            self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)),
                          msg=key)

    def test_mixed_x_underscore_prefix_strips_to_bare_key(self):
        # 同上,混合形(單 x_ 後接雙底線 x_):x_x__body 須剝到 "body"。
        e = attempt_completed(x_meta={"x_x__body": "leak"})
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)),
                      msg="x_x__body 須剝到底成 'body'(forbidden_exact 之一)")

    # ── value_leak:洩漏形狀,不是裸字比對 ─────────────────────

    def test_value_leak_assigned_secret_rejected(self):
        e = attempt_completed(x_meta={"note": "password=hunter2"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_underscore_compound_name_rejected(self):
        # r2-#98 F2:起頭用 \b 時,底線前後不成立詞界,access_token=/
        # refresh_token=/id_token=/client_secret: 這類複合詞完全不命中。
        # 改成 (?<![A-Za-z0-9]) 才擋得住。
        for note in ("access_token=abcdef123", "refresh_token=abcdef123",
                     "id_token=abcdef123", "client_secret: xyz12345"):
            e = attempt_completed(x_meta={"note": note})
            self.assertIn("privacy_value_leak", codes(ev.validate_event(e)), msg=note)

    def test_value_leak_fullwidth_colon_rejected(self):
        # r2-#98 F3:[:=] 不含全形冒號 ：,比照 _VALUE_LEAK_CONV_LINE 補上。
        e = attempt_completed(x_meta={"note": "password：hunter2"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_masked_marker_passes(self):
        # r2-#98 F4:賦值形抓到值後,若整段值只是已遮蔽的佔位符,不算外洩。
        # 找碴單上的字面案例是 "token=***"(3 星),但 \S{6,} 要求值至少 6 個
        # 非空白字元,3 星本來就構不成 _VALUE_LEAK_ASSIGN 的一個 match(修前
        # 就放行,不是本輪修的紅);仍原樣收進來當基準,另補 "token=******"
        # (6 星,修前確實誤判)驗證遮蔽排除規則真的生效,不是規則沒觸發而放行。
        for note in ("secret=redacted", "password=REDACTED",
                     "token=***", "token=******"):
            e = attempt_completed(x_meta={"note": note})
            self.assertEqual(ev.validate_event(e), [], msg=note)

    def test_value_leak_transcript_assign_form_rejected(self):
        # r2-#98 F5:值側對 transcript/conversation/messages 完全沒覆蓋。
        # 賦值形(transcript: <text>)才擋,裸字提及仍放行。
        # r3-#98:短的「transcript: user said hi…」(舊找碴單字面案例)已改由
        # _looks_like_transcript 放行(不夠長也不夠多詞、無引號無角色標記),
        # 換成真的長得像逐字稿內容的長版,見 test_value_leak_narrative_*
        # 三個必擋案例。
        e = attempt_completed(
            x_meta={"note": "transcript: user said hi and then asked about "
                             "the refund policy, the agent replied it takes "
                             "five days"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_transcript_bare_mention_passes(self):
        e = attempt_completed(x_meta={"note": "see the transcript for details"})
        self.assertEqual(ev.validate_event(e), [])

    def test_value_leak_narrative_short_status_passes(self):
        # r3-#98(major,兩個審查鏡頭同時抓到):v2 舊門檻只要 4 字元就擋,
        # 「messages: 3 pending」這類日常狀態敘述在 title/result_summary 等
        # 自由文字欄位很容易撞到,被誤判 privacy_value_leak。改成要「長得像
        # 逐字稿內容」才擋(長度+詞數 / 引號對話 / 角色標記),純狀態詞放行。
        for note in ("messages: 3 pending", "conversation: started",
                     "transcript: see attached", "messages: none",
                     "transcript: pending review",
                     "conversation: 2026-09-04 kickoff"):
            e = attempt_completed(x_meta={"note": note})
            self.assertEqual(ev.validate_event(e), [], msg=note)

    def test_value_leak_narrative_general_threshold_60_10_passes(self):
        # r3-#98 收斂:首版通用門檻 40 字元/6 詞會誤擋短的工程改名敘述
        # (「renamed "old field name" to "new field name"」44 字元 8 詞,
        # 引號內各段只有 3 詞,不吃引號路徑),裁定拉高到 60 字元/10 詞。
        for note in (
            'messages: renamed "old field name" to "new field name"',
            "conversation: moved the retry logic into the shared "
            "client module",
        ):
            e = attempt_completed(x_meta={"note": note})
            self.assertEqual(ev.validate_event(e), [], msg=note)

    def test_value_leak_narrative_quoted_dialogue_rejected(self):
        e = attempt_completed(x_meta={
            "note": 'conversation: "can you reset my password" '
                    '"sure, what is your account id"'})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_narrative_role_marker_rejected(self):
        # 值本身不夠長(<60 字元)、詞數也不到 10(6 詞),但含 user:/
        # assistant: 角色標記,要靠角色標記那條規則單獨擋下,不能只靠
        # 長度+詞數判斷。
        e = attempt_completed(x_meta={
            "note": "messages: user: hi assistant: hello user: bye"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_narrative_does_not_swallow_trailing_secret(self):
        # r3-#98:v2 若跟 v1 共用同一次 alternation match,greedy 的 v2 會把
        # 行尾的 password=... 一起吞掉,判完「不像逐字稿」就放行,導致藏在
        # v2 殘值裡的 v1 洩漏永遠掃不到。兩條正則已拆開各自獨立掃描 s。
        e = attempt_completed(x_meta={
            "note": "messages: 3 pending. password=hunter2"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_openai_style_key_rejected(self):
        e = attempt_completed(
            x_meta={"note": "leaked sk-abcdefghijklmnop1234567890 in log"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_stripe_style_hyphenated_key_rejected(self):
        # 驗收原文的字面案例:含連字號的金鑰格式(sk-live-...)。
        e = attempt_completed(x_meta={"note": "found sk-live-abcd1234efgh in diff"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_sk_prefix_does_not_catch_english_words(self):
        # 同型回歸:sk-[A-Za-z0-9]{8,} 沒鎖字界時會吃到 risk-assessment、
        # disk-encryption 這類合法英文字,誤判成金鑰洩漏。
        for note in ("risk-assessment completed for this feature",
                     "switched to disk-encryption for the volume"):
            e = attempt_completed(x_meta={"note": note})
            self.assertEqual(ev.validate_event(e), [], msg=note)

    def test_value_leak_aws_key_rejected(self):
        e = attempt_completed(
            x_meta={"note": "found AKIAIOSFODNN7EXAMPLE in commit"})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_conversation_structure_rejected(self):
        convo = "user: hi\nassistant: hello there\nuser: bye now"
        e = attempt_completed(x_meta={"note": convo})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)))

    def test_value_leak_scanned_inside_list(self):
        # #98 PR #110 回歸:值掃描只在 dict 分支,list 內字串完全不掃。
        e = attempt_completed(x_meta={"notes": ["ok", "password=hunter2"]})
        self.assertIn("privacy_value_leak", codes(ev.validate_event(e)),
                      msg="list 元素也要走 value_leak 掃描")

    def test_value_leak_word_in_engineering_prose_passes(self):
        # #98 PR #110 回歸:裸字比對把「移除了密碼欄位」的工程敘述誤判成外洩。
        e = attempt_completed(x_meta={
            "summary": "removed the password field from the login form"})
        self.assertEqual(ev.validate_event(e), [])

    def test_value_leak_token_mentioned_in_prose_passes(self):
        e = attempt_completed(x_meta={"note": "rotate the token weekly"})
        self.assertEqual(ev.validate_event(e), [])

    def test_value_leak_transcript_ref_value_passes(self):
        e = attempt_completed(x_meta={"note": "transcript_ref: abc"})
        self.assertEqual(ev.validate_event(e), [])

    def test_value_leak_bearer_token_rejected(self):
        # Bearer 後接像 token 的字串(至少含一位數字)才算洩漏。
        for note in ("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0",
                     "sent Bearer a1b2c3d4e5f6g7h8i9j0 to the API"):
            e = attempt_completed(x_meta={"note": note})
            self.assertIn("privacy_value_leak", codes(ev.validate_event(e)), msg=note)

    def test_value_leak_bearer_prose_passes(self):
        # 整合審查抓到的誤殺:Bearer 後接純字母連字號的工程敘述不是 token。
        for note in ("added Bearer authentication-middleware to the router",
                     "the Bearer scheme is documented in the auth spec"):
            e = attempt_completed(x_meta={"note": note})
            self.assertEqual(ev.validate_event(e), [], msg=note)


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

    def test_result_summary_must_be_one_line_within_2000(self):
        # 6.6:上限升為 2000(共享契約 §6 表);單行約束不變
        long = self.layer_completed(status="pass", result_summary="x" * 2500)
        self.assertIn("invalid_format", codes(ev.validate_event(long)))
        ok = self.layer_completed(status="pass", result_summary="x" * 500)
        self.assertEqual(ev.validate_event(ok), [])
        multiline = self.layer_completed(status="pass",
                                         result_summary="ok\nFAILED details...")
        self.assertIn("invalid_format", codes(ev.validate_event(multiline)))

    def test_privacy_scan_still_applies_to_gauntlet_events(self):
        e = self.layer_completed(status="pass", x_meta={"api_token": "sk-1"})
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)))


class TestFieldLengthLimits(unittest.TestCase):
    """6.6:欄位級長度上限(共享契約 §6 表)取代單一 2000 字上限;
    超限逐欄報錯,訊息含欄名與上限。"""

    def layer_completed(self, **over):
        e = base("verification_layer_completed", writer="verifier",
                 stage="7-review", layer="unit", status="pass",
                 source_sha="def5678")
        e.update(over)
        return e

    def limit_errs(self, event, field):
        return [err for err in ev.validate_event(event)
                if err["code"] == "invalid_format"
                and err["field"] == field]

    def assert_limit_error(self, event, field, limit):
        errs = self.limit_errs(event, field)
        self.assertTrue(errs, msg=f"{field} 超限未報錯")
        self.assertTrue(any(str(limit) in err["msg"] and field in err["msg"]
                            for err in errs),
                        msg=f"{field} 錯誤訊息須含欄名與上限 {limit}: {errs}")

    def test_model_le_100(self):
        self.assertEqual(ev.validate_event(attempt_completed(model="m" * 100)),
                         [])
        self.assert_limit_error(attempt_completed(model="m" * 120),
                                "model", 100)

    def test_from_to_model_le_100(self):
        e = base("task_escalated", stage="6-implementation", task_id="T-1",
                 attempt_id=ATT, from_model="m" * 120, to_model="n" * 120,
                 failure_category="IMPL")
        self.assert_limit_error(e, "from_model", 100)
        self.assert_limit_error(e, "to_model", 100)

    def test_prompt_id_le_100(self):
        ok = attempt_completed(prompt={"id": "a" * 100, "version": "3.1.0",
                                       "hash": SHA256})
        self.assertEqual(ev.validate_event(ok), [])
        bad = attempt_completed(prompt={"id": "a" * 120, "version": "3.1.0",
                                        "hash": SHA256})
        self.assert_limit_error(bad, "prompt.id", 100)

    def test_prompt_version_le_40(self):
        bad = attempt_completed(prompt={"id": "stage6-worker",
                                        "version": "1.0." + "0" * 50,
                                        "hash": SHA256})
        self.assert_limit_error(bad, "prompt.version", 40)

    def test_failure_reason_le_500(self):
        ok = base("agent_dispatched", stage="6-implementation", task_id="T-1",
                  attempt_id=ATT, agent_role="worker", model="haiku",
                  prompt=copy.deepcopy(PROMPT), reason="r" * 500)
        self.assertEqual(ev.validate_event(ok), [])
        bad = base("agent_dispatched", stage="6-implementation", task_id="T-1",
                   attempt_id=ATT, agent_role="worker", model="haiku",
                   prompt=copy.deepcopy(PROMPT), reason="r" * 600)
        self.assert_limit_error(bad, "reason", 500)

    def test_finding_summary_title_le_1000(self):
        ok = base("finding_created", stage="7-review", finding_id=FND,
                  review_id=REV, severity="blocker", title="t" * 1000)
        self.assertEqual(ev.validate_event(ok), [])
        bad = base("finding_created", stage="7-review", finding_id=FND,
                   review_id=REV, severity="blocker", title="t" * 1200)
        self.assert_limit_error(bad, "title", 1000)

    def test_command_reference_le_500(self):
        ok = self.layer_completed(command_ref="c" * 500)
        self.assertEqual(ev.validate_event(ok), [])
        self.assert_limit_error(self.layer_completed(command_ref="c" * 600),
                                "command_ref", 500)

    def test_artifact_reference_le_1000(self):
        ok = self.layer_completed(artifact_ref="a" * 1000)
        self.assertEqual(ev.validate_event(ok), [])
        self.assert_limit_error(self.layer_completed(artifact_ref="a" * 1200),
                                "artifact_ref", 1000)

    def test_result_summary_le_2000(self):
        ok = self.layer_completed(result_summary="s" * 2000)
        self.assertEqual(ev.validate_event(ok), [])
        self.assert_limit_error(self.layer_completed(result_summary="s" * 2500),
                                "result_summary", 2000)

    def test_privacy_blacklist_kept(self):
        # 6.6 只換長度機制,禁載欄位黑名單維持
        e = attempt_completed(x_meta={"api_token": "sk-1"})
        self.assertIn("privacy_forbidden_key", codes(ev.validate_event(e)))


class TestResultMigration(unittest.TestCase):
    """6.4 migration tests:result = deprecated since 1.x, removed in 2.0。
    1.x 讀 result-only 舊檔可過;status/result 並存不一致拒收;
    新寫入(writer API)一律只寫 status(見 test_writer)。"""

    SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "schema", "agent-event.schema.json")

    def test_schema_declares_removal_plan(self):
        import json
        with open(self.SCHEMA) as f:
            schema = json.load(f)
        dep = schema["deprecations"]["verification_layer_completed.result"]
        self.assertIn("deprecated since 1.x, removed in 2.0", dep)

    def test_1x_reads_result_only_legacy_file(self):
        e = base("verification_layer_completed", writer="verifier",
                 stage="7-review", layer="full-suite", result="PASS",
                 exit_code=0, evidence_ref="final-fresh-run.log")
        e["schema"] = "devflow-agent-event/1"        # 舊檔 envelope
        self.assertEqual(ev.validate_event(e), [])

    def test_status_result_coexist_inconsistent_rejected(self):
        e = base("verification_layer_completed", writer="verifier",
                 stage="7-review", layer="unit", status="pass", result="FAIL")
        self.assertIn("inconsistent_fields", codes(ev.validate_event(e)))


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
