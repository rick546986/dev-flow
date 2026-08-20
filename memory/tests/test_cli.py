"""CLI 端對端(dev-setup 呼叫的介面):輸出可解析、路徑不外洩、無 init 入口。"""
import json
import os
import subprocess
import sys

from memtools import MemoryCase, commit_all, write

CLI = os.path.join("memory", "dev-memory.py")


class CliTest(MemoryCase):
    def run_cli(self, *args, expect=0):
        out = subprocess.run(
            [sys.executable, CLI, "--path", self.repo, *args],
            capture_output=True, text=True, env=dict(os.environ))
        self.assertEqual(out.returncode, expect,
                         "stdout={0}\nstderr={1}".format(out.stdout, out.stderr))
        return out

    def json_cli(self, *args, **kwargs):
        return json.loads(self.run_cli(*args, **kwargs).stdout)

    def test_no_init_subcommand_exists(self):
        """§12:dev-setup 是唯一 setup 入口 —— CLI 不得提供第二個安裝器。"""
        out = subprocess.run([sys.executable, CLI, "init"],
                             capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("invalid choice", out.stderr)

    def test_setup_then_status_then_doctor(self):
        report = self.json_cli("setup", "--name", "demo")
        self.assertTrue(report["project_created"])
        status = self.json_cli("status")
        self.assertEqual(status["project_id"], report["project_id"])
        doctor = self.json_cli("doctor")
        self.assertIn(doctor["verdict"], ("PASS", "WARN"))

    def test_commands_before_setup_fail_loud(self):
        out = subprocess.run(
            [sys.executable, CLI, "--path", self.repo, "status"],
            capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("dev-setup", out.stderr)

    def test_remember_reports_signal_gate_verdict(self):
        self.json_cli("setup", "--name", "demo")
        low = self.json_cli("remember", "--kind", "file_read", "--title", "讀檔")
        self.assertEqual(low["signal_gate"]["signal"], "low")
        self.assertFalse(low["signal_gate"]["durable_allowed"])
        high = self.json_cli("remember", "--kind", "schema_change",
                             "--title", "改名成 lab_order",
                             "--path-ref", "migrations/001.sql")
        self.assertEqual(high["signal_gate"]["signal"], "high")

    def test_fact_verify_roundtrip(self):
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        commit_all(self.repo, "seed")
        self.json_cli("setup", "--name", "demo")
        created = self.json_cli("fact", "--entity-type", "database",
                                "--entity-key", "lab-order",
                                "--fact-key", "current_table",
                                "--value", "lab_order", "--dep", "src/db.ts",
                                "--verified")
        self.assertEqual(created["status"], "VERIFIED")
        answer = self.json_cli("ask", "目前 lab-order 的 current_table 是什麼?",
                               "--json")
        self.assertEqual(answer["current_truth"]["value"], "lab_order")
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        stale = self.json_cli("ask", "目前 lab-order 的 current_table 是什麼?",
                              "--json")
        self.assertNotIn("current_truth", stale)
        outcome = self.json_cli("verify", "--entity-type", "database",
                                "--entity-key", "lab-order",
                                "--fact-key", "current_table",
                                "--observed", "orders")
        self.assertEqual(outcome["outcome"], "superseded")
        after = self.json_cli("ask", "目前 lab-order 的 current_table 是什麼?",
                              "--json")
        self.assertEqual(after["current_truth"]["value"], "orders")

    def test_ask_no_hit_is_reported_not_faked(self):
        self.json_cli("setup", "--name", "demo")
        answer = self.json_cli("ask", "咖啡機壞了要找誰修?", "--json")
        self.assertEqual(answer["retrieval_status"], "NO_RELIABLE_MATCH")
        self.assertEqual(answer["results"], [])

    def test_talk_flow_end_to_end(self):
        self.json_cli("setup", "--name", "demo")
        started = self.json_cli("talk", "start",
                                "我今天想聊聊 PGS 在真實世界的送檢流程")
        session = started["session_id"]
        self.assertIn("open_questions", started["brief"])
        self.json_cli("talk", "turn", session, "user", "院所會一次送一批")
        candidate = self.json_cli(
            "talk", "propose", session, "--kind", "domain",
            "--payload-json",
            json.dumps({"key": "submission",
                        "title": "submission = 院所的一批送檢"},
                       ensure_ascii=False),
            "--authority", "domain_expert")["candidate_id"]
        self.json_cli("talk", "confirm", candidate)
        result = self.json_cli("talk", "end", session)
        self.assertEqual(result["promoted"], 1)
        for path in result["written"]:
            self.assertFalse(os.path.isabs(path), path)
            self.assertTrue(path.startswith(".dev-flow/"), path)
        answer = self.json_cli("ask", "submission 是什麼意思?", "--json")
        self.assertEqual(answer["results"][0]["key"], "submission")

    def test_context_output_is_small_and_has_no_absolute_paths(self):
        self.json_cli("setup", "--name", "demo")
        text = self.run_cli("context").stdout
        self.assertIn("project_id", text)
        self.assertNotIn(self.repo, text)

    def test_migrate_legacy_dry_run_then_apply(self):
        write(self.repo, "CONTEXT.md",
              "# demo\n\n## Language\n\n**Registration(送檢紀錄)**:一個客戶的送檢。\n")
        self.json_cli("setup", "--name", "demo")
        dry = self.json_cli("migrate-legacy")
        self.assertEqual(dry["context_md"]["terms"], 1)
        self.assertFalse(dry["applied"])
        applied = self.json_cli("migrate-legacy", "--apply", "--promote")
        self.assertTrue(applied["applied"])
        for path in applied["written"]:
            self.assertTrue(path.startswith(".dev-flow/knowledge/domain/"), path)

    def test_eval_runs_and_passes(self):
        self.json_cli("setup", "--name", "demo")
        report = self.json_cli("eval", "--json")
        self.assertTrue(report["passed"], report["violations"])

    def test_reindex_reports_before_and_after(self):
        self.json_cli("setup", "--name", "demo")
        report = self.json_cli("reindex")
        self.assertEqual(report["after"]["mismatched"], 0)

    def test_know_refuses_low_authority_overwrite(self):
        self.json_cli("setup", "--name", "demo")
        self.json_cli("know", "--kind", "domain", "--key", "registration",
                      "--title", "registration = customer-level",
                      "--authority", "domain_expert")
        refused = self.json_cli("know", "--kind", "domain", "--key",
                                "registration", "--title",
                                "registration = embryo-level",
                                "--authority", "code_inference")
        self.assertEqual(refused["action"], "refused")

    def test_inventory_works_without_local_db(self):
        self.json_cli("setup", "--name", "demo")
        inventory = self.json_cli("inventory")
        self.assertIn("facts", inventory)
