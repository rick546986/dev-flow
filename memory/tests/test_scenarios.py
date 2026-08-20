"""端對端情境測試(走 CLI,不是直接呼叫 Python 函式)。

既有的 300+ 測試多半直接呼叫函式 —— 那證明得了元件對,證明不了 **agent 照
SKILL 敲那些指令會得到正確結果**。這一支從 CLI 進、從 CLI 出,連參數名打錯
都會紅。

    Scenario A  dev-talk:聊 → 候選 → 確認 → 收尾 → 砍 DB → 重建 → 查得到
    Scenario B  dev-run:實作 → 觀察 → checkpoint → 砍 DB → 重建 →
                current / history / why 各自正確,且沒有 decision 時 why 不硬猜
    Scenario C  stale current truth:OK → 改依賴 → NEEDS_VERIFICATION → verify → OK
"""
import json
import os
import shutil
import subprocess
import sys

from memtools import MemoryCase, commit_all, write


class ScenarioCase(MemoryCase):
    def cli(self, *args, expect=0):
        out = subprocess.run(
            [sys.executable, os.path.join("memory", "dev-memory.py"),
             "--path", self.repo, *args],
            capture_output=True, text=True, env=dict(os.environ))
        self.assertEqual(out.returncode, expect,
                         "args={0}\nstdout={1}\nstderr={2}".format(
                             args, out.stdout, out.stderr))
        return out

    def js(self, *args, **kwargs):
        return json.loads(self.cli(*args, **kwargs).stdout)

    def wipe_local_db(self):
        project_id = self.js("status")["project_id"]
        shutil.rmtree(os.path.join(self.home, "projects", project_id))
        self.assertFalse(os.path.isdir(
            os.path.join(self.home, "projects", project_id)))
        return project_id

    def durable_blob(self):
        from agentmem import identity
        parts = []
        for dirpath, _dirs, files in os.walk(identity.durable_root(self.repo)):
            for name in files:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    parts.append(f.read())
        return "\n".join(parts)


class ScenarioADevTalkTest(ScenarioCase):
    """A:「dev-talk,我想聊 PGS registration」的完整一輪。"""

    def test_full_devtalk_round_trip(self):
        self.js("setup", "--name", "demo")
        started = self.js("talk", "start", "我想聊 PGS registration")
        sid = started["session_id"]
        self.assertEqual(started["mode"], "understanding")
        self.assertIn("open_questions", started["brief"])

        self.js("talk", "turn", sid, "agent",
                "我的理解是 registration 是 customer-level,這樣對嗎?")
        self.js("talk", "turn", sid, "user",
                "對,registration 永遠代表一個客戶,不是 embryo")

        candidate = self.js(
            "talk", "propose", sid, "--kind", "domain", "--payload-json",
            json.dumps({"key": "registration",
                        "title": "registration = 一個客戶在 submission 內的送檢紀錄",
                        "body": "customer-level,不是 embryo-level"},
                       ensure_ascii=False),
            "--authority", "domain_expert")["candidate_id"]
        self.js("talk", "confirm", candidate)
        result = self.js("talk", "end", sid)
        self.assertEqual(result["promoted"], 1)
        self.assertEqual(result["session_status"], "CLOSED")

        blob = self.durable_blob()
        self.assertIn("customer-level", blob)
        self.assertNotIn("我想聊 PGS registration", blob)
        self.assertNotIn("這樣對嗎", blob)

        # 砍掉 local DB → 重建 → 查得到
        self.wipe_local_db()
        self.js("setup")
        answer = self.js("ask", "registration 是什麼意思?", "--json")
        self.assertEqual(answer["retrieval_status"], "OK")
        self.assertEqual(answer["results"][0]["key"], "registration")
        self.assertIn("customer-level", answer["results"][0]["body"])

    def test_propose_without_start_is_refused(self):
        self.js("setup", "--name", "demo")
        out = self.cli("talk", "propose", "ses_00000000000000000000000000",
                       "--kind", "domain", "--payload-json",
                       '{"key":"x","title":"y"}', expect=1)
        self.assertIn("session", out.stderr)

    def test_turn_on_closed_session_is_refused(self):
        self.js("setup", "--name", "demo")
        sid = self.js("talk", "start", "主題")["session_id"]
        self.js("talk", "end", sid)
        out = self.cli("talk", "turn", sid, "user", "再一句", expect=1)
        self.assertIn("已是", out.stderr)

    def test_rejected_candidate_never_reaches_durable(self):
        self.js("setup", "--name", "demo")
        sid = self.js("talk", "start", "主題")["session_id"]
        candidate = self.js(
            "talk", "propose", sid, "--kind", "domain", "--payload-json",
            json.dumps({"key": "wrong", "title": "錯的理解"},
                       ensure_ascii=False))["candidate_id"]
        self.js("talk", "reject", candidate, "--reason", "使用者說不是這樣")
        self.assertEqual(self.js("talk", "end", sid)["promoted"], 0)
        self.assertNotIn("錯的理解", self.durable_blob())

    def test_two_concurrent_sessions_do_not_cross(self):
        self.js("setup", "--name", "demo")
        first = self.js("talk", "start", "主題 A")["session_id"]
        second = self.js("talk", "start", "主題 B")["session_id"]
        candidate = self.js(
            "talk", "propose", second, "--kind", "domain", "--payload-json",
            json.dumps({"key": "b-key", "title": "B 的知識"},
                       ensure_ascii=False))["candidate_id"]
        self.js("talk", "confirm", candidate)
        self.assertEqual(self.js("talk", "end", first)["promoted"], 0)
        self.assertNotIn("B 的知識", self.durable_blob())
        self.assertEqual(self.js("talk", "end", second)["promoted"], 1)
        self.assertIn("B 的知識", self.durable_blob())

    def test_abort_leaves_session_visibly_aborted(self):
        self.js("setup", "--name", "demo")
        sid = self.js("talk", "start", "主題")["session_id"]
        self.js("talk", "abort", sid, "--reason", "使用者中斷")
        self.assertEqual(self.js("talk", "status", sid)["session"]["status"],
                         "ABORTED")

    def test_correction_round_trip_keeps_history(self):
        self.js("setup", "--name", "demo")
        sid = self.js("talk", "start", "registration 語意")["session_id"]
        first = self.js(
            "talk", "propose", sid, "--kind", "domain", "--payload-json",
            json.dumps({"key": "registration",
                        "title": "registration = embryo-level"},
                       ensure_ascii=False),
            "--authority", "agent_hypothesis")["candidate_id"]
        self.js("talk", "confirm", first)
        self.js("talk", "checkpoint", sid)
        self.js("talk", "correct", sid, "--kind", "domain", "--key",
                "registration", "--title", "registration = customer-level",
                "--reason", "使用者更正")
        self.js("talk", "end", sid)

        self.wipe_local_db()
        self.js("setup")
        current = self.js("ask", "registration 是什麼意思?", "--json")
        self.assertIn("customer-level", current["results"][0]["title"])
        history = self.js("ask", "之前 registration 改過什麼?", "--json")
        self.assertEqual(history["retrieval_status"], "OK")
        blob = " ".join(hit["title"] + hit.get("text", "")
                        for hit in history["results"])
        self.assertIn("embryo-level", blob)
        self.assertIn("使用者更正", blob)


class ScenarioBDevRunTest(ScenarioCase):
    """B:一次 Stage 6 實作之後,另一台機器要知道發生過什麼。"""

    def setUp(self):
        super().setUp()
        write(self.repo, "src/db.ts", "export const table = 'pgs_intake'\n")
        commit_all(self.repo, "baseline")

    def run_feature(self, with_decision=True):
        self.js("setup", "--name", "demo")
        started = self.js("session", "start", "--mode", "implementation",
                          "--slug", "lab-order-merge")
        sid = started["session_id"]
        self.assertEqual(started["feature_slug"], "lab-order-merge")

        write(self.repo, "src/db.ts", "export const table = 'lab_order'\n")
        write(self.repo, "migrations/20260820_rename.sql",
              "alter table pgs_intake rename to lab_order;\n")
        head = commit_all(self.repo, "rename pgs_intake to lab_order")

        # 低訊號:不進 Git
        self.js("session", "observe", sid, "--kind", "grep",
                "--title", "grep pgs_intake")
        self.js("session", "observe", sid, "--kind", "file_read",
                "--title", "讀 src/db.ts")
        # 高訊號
        self.js("session", "observe", sid, "--kind", "table_rename",
                "--title", "pgs_intake 改名成 lab_order",
                "--body", "PGS 與 ECS 之後共用同一張 lab_order 表",
                "--path-ref", "migrations/20260820_rename.sql",
                "--commit", head)
        self.js("session", "observe", sid, "--kind", "fact",
                "--title", "current_table", "--commit", head,
                "--fact-json", json.dumps(
                    {"entity_type": "database", "entity_key": "lab-order",
                     "fact_key": "current_table", "value": "lab_order",
                     "dependencies": ["src/db.ts"]}))
        if with_decision:
            self.js("session", "observe", sid, "--kind", "decision",
                    "--title", "PGS 與 ECS 共用 lab_order",
                    "--decision-json", json.dumps(
                        {"key": "share-lab-order",
                         "decision": "合併成單一 lab_order 表",
                         "alternatives": "各自維護一張表",
                         "reason": "兩邊欄位重疊九成,分開維護會讓 migration 寫兩份",
                         "tradeoff": "查詢要多帶 order_type"},
                        ensure_ascii=False))
        report = self.js("session", "status", sid)
        self.assertEqual(report["low_signal_observations"], 2)
        return self.js("checkpoint", sid, "--end")

    def test_another_machine_learns_the_feature(self):
        result = self.run_feature()
        self.assertEqual(result["promoted"], 3)
        self.wipe_local_db()
        self.js("setup")

        history = self.js("ask", "之前 lab_order 改過什麼?", "--json")
        self.assertEqual(history["retrieval_status"], "OK")
        self.assertIn("pgs_intake",
                      " ".join(h["title"] for h in history["results"]))
        self.assertNotIn("grep",
                         " ".join(h["title"] for h in history["results"]))

        current = self.js("ask", "目前 lab-order 的 current_table 是什麼?",
                          "--json")
        self.assertEqual(current["retrieval_status"], "OK")
        self.assertEqual(current["current_truth"]["value"], "lab_order")

        why = self.js("ask", "為什麼要共用 lab order?", "--json")
        self.assertEqual(why["retrieval_status"], "OK")
        self.assertEqual(why["results"][0]["item_type"], "decision")
        self.assertIn("欄位重疊", why["results"][0]["reason"])

    def test_low_signal_never_reaches_durable(self):
        self.run_feature()
        blob = self.durable_blob()
        self.assertNotIn("grep pgs_intake", blob)
        self.assertNotIn("讀 src/db.ts", blob)

    def test_why_without_decision_refuses_to_guess(self):
        self.run_feature(with_decision=False)
        self.wipe_local_db()
        self.js("setup")
        why = self.js("ask", "為什麼要把 pgs_intake 改名成 lab_order?", "--json")
        self.assertEqual(why["retrieval_status"], "NO_RELIABLE_MATCH")
        self.assertEqual(why["results"], [])
        self.assertTrue(why["uncertainty"])

    def test_feature_with_no_high_signal_writes_nothing(self):
        self.js("setup", "--name", "demo")
        sid = self.js("session", "start", "--mode", "implementation",
                      "--slug", "tidy-up")["session_id"]
        self.js("session", "observe", sid, "--kind", "command_ok",
                "--title", "npm test 通過")
        result = self.js("checkpoint", sid, "--end")
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(result["written"], [])

    def test_sensitive_observation_never_reaches_durable(self):
        self.js("setup", "--name", "demo")
        sid = self.js("session", "start", "--mode", "implementation",
                      "--slug", "config")["session_id"]
        self.js("session", "observe", sid, "--kind", "breaking_config_change",
                "--title", "新增連線設定",
                "--body", 'DB_PASSWORD = "hunter2000"')
        result = self.js("checkpoint", sid, "--end")
        self.assertEqual(result["promoted"], 0)
        self.assertNotIn("hunter2000", self.durable_blob())


class ScenarioCStaleTruthTest(ScenarioCase):
    """C:VERIFIED → 改依賴 → NEEDS_VERIFICATION → verify → OK。"""

    def setUp(self):
        super().setUp()
        write(self.repo, "src/db.ts", "export const table = 'lab_order'\n")
        commit_all(self.repo, "baseline")

    def ask_current(self):
        return self.js("ask", "目前 lab-order 的 current_table 是什麼?", "--json")

    def test_stale_never_reports_ok(self):
        self.js("setup", "--name", "demo")
        self.js("fact", "--entity-type", "database", "--entity-key",
                "lab-order", "--fact-key", "current_table", "--value",
                "lab_order", "--dep", "src/db.ts", "--verified")
        first = self.ask_current()
        self.assertEqual(first["retrieval_status"], "OK")
        self.assertEqual(first["current_truth"]["value"], "lab_order")

        write(self.repo, "src/db.ts", "export const table = 'orders'\n")
        stale = self.ask_current()
        self.assertEqual(stale["retrieval_status"], "NEEDS_VERIFICATION")
        self.assertNotEqual(stale["retrieval_status"], "OK")
        self.assertNotIn("current_truth", stale)

        commit_all(self.repo, "change table")
        still_stale = self.ask_current()
        self.assertEqual(still_stale["retrieval_status"], "NEEDS_VERIFICATION")

        self.js("verify", "--entity-type", "database", "--entity-key",
                "lab-order", "--fact-key", "current_table",
                "--observed", "orders")
        after = self.ask_current()
        self.assertEqual(after["retrieval_status"], "OK")
        self.assertEqual(after["current_truth"]["value"], "orders")

    def test_cli_text_output_shows_the_status(self):
        self.js("setup", "--name", "demo")
        self.js("fact", "--entity-type", "database", "--entity-key",
                "lab-order", "--fact-key", "current_table", "--value",
                "lab_order", "--dep", "src/db.ts", "--verified")
        write(self.repo, "src/db.ts", "export const table = 'orders'\n")
        text = self.cli("ask", "目前 lab-order 的 current_table 是什麼?").stdout
        self.assertIn("NEEDS_VERIFICATION", text)

    def test_verify_lineage_survives_rebuild(self):
        """verify 造成的 supersede,checkpoint 之後也要跨重建保留。"""
        self.js("setup", "--name", "demo")
        self.js("fact", "--entity-type", "database", "--entity-key",
                "lab-order", "--fact-key", "current_table", "--value",
                "lab_order", "--dep", "src/db.ts", "--verified")
        sid = self.js("session", "start", "--mode", "implementation",
                      "--slug", "swap")["session_id"]
        write(self.repo, "src/db.ts", "export const table = 'orders'\n")
        commit_all(self.repo, "swap")
        self.js("verify", "--entity-type", "database", "--entity-key",
                "lab-order", "--fact-key", "current_table",
                "--observed", "orders")
        self.js("session", "observe", sid, "--kind", "fact",
                "--title", "current_table", "--fact-json", json.dumps(
                    {"entity_type": "database", "entity_key": "lab-order",
                     "fact_key": "current_table", "value": "orders",
                     "dependencies": ["src/db.ts"]}))
        result = self.js("checkpoint", sid, "--end")
        self.assertGreaterEqual(result["revisions"], 1)

        self.wipe_local_db()
        self.js("setup")
        history = self.js("ask", "之前 current_table 改過什麼?", "--json")
        blob = " ".join(h["title"] + h.get("text", "")
                        for h in history["results"])
        self.assertIn("lab_order", blob)
        self.assertIn("orders", blob)
