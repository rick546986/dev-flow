"""Project Understanding Mode:主動學習 / transcript 不進 Git / checkpoint(§14-§18)。"""
import json
import os

from memtools import MemoryCase, commit_all, write
from agentmem import devtalk, durable, identity, truth


class ProbeTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/models/registration.ts", "export class Registration {}\n")
        write(self.repo, "src/models/specimen.ts", "export class Specimen {}\n")
        write(self.repo, "migrations/20260701_pgs_submission.sql",
              "create table pgs_submission (id int);\n")
        write(self.repo, "docs/pgs-flow.md", "# PGS 送檢流程\n")
        commit_all(self.repo, "seed pgs files")

    def test_probe_finds_repo_signals_as_relative_paths(self):
        brief = devtalk.probe(self.store, self.repo, "PGS 送檢流程")
        self.assertTrue(brief["repo_signals"])
        for entry in brief["repo_signals"]:
            self.assertFalse(os.path.isabs(entry["path"]), entry)
            self.assertNotIn("\\", entry["path"])

    def test_probe_produces_concrete_open_questions(self):
        brief = devtalk.probe(self.store, self.repo, "pgs")
        self.assertTrue(brief["open_questions"])
        self.assertTrue(any("例外" in q for q in brief["open_questions"]))

    def test_probe_asks_about_entities_it_found(self):
        brief = devtalk.probe(self.store, self.repo, "pgs")
        self.assertTrue(brief["candidate_entities"])
        joined = " ".join(brief["open_questions"])
        self.assertTrue(any(entity in joined
                            for entity in brief["candidate_entities"][:6]))

    def test_probe_does_not_reask_confirmed_knowledge(self):
        truth.assert_knowledge(self.store, "domain", "submission",
                               "submission = 院所批次送檢",
                               authority="domain_expert", status="CONFIRMED")
        brief = devtalk.probe(self.store, self.repo, "submission")
        self.assertEqual([k["key"] for k in brief["known_knowledge"]],
                         ["submission"])
        self.assertNotIn("submission", brief["candidate_entities"])

    def test_probe_surfaces_unconfirmed_knowledge_for_confirmation(self):
        truth.assert_knowledge(self.store, "domain", "specimen",
                               "specimen = 單一 embryo",
                               authority="agent_hypothesis", status="CANDIDATE")
        brief = devtalk.probe(self.store, self.repo, "specimen")
        self.assertTrue(any("還沒確認過" in q for q in brief["open_questions"]))

    def test_probe_surfaces_existing_conflicts_first(self):
        truth.assert_knowledge(self.store, "domain", "registration",
                               "registration = customer-level",
                               authority="domain_expert", status="CONFIRMED")
        truth.reconcile_with_code(self.store, "domain", "registration",
                                  "看起來是 specimen-level", "current_code",
                                  supports=False)
        brief = devtalk.probe(self.store, self.repo, "registration")
        self.assertTrue(brief["conflicts"])
        self.assertIn("衝突狀態", brief["open_questions"][0])

    def test_probe_with_no_memory_asks_top_down(self):
        brief = devtalk.probe(self.store, self.repo, "完全沒碰過的主題 xyzzy")
        self.assertTrue(any("沒有任何記憶" in q for q in brief["open_questions"]))


class SessionTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        started = devtalk.start(self.store, self.repo,
                               "我今天想聊聊 PGS 在真實世界的送檢流程",
                               identity.workspace_snapshot(self.repo))
        self.session = started["session_id"]
        self.brief = started["brief"]

    def durable_blob(self):
        parts = []
        for dirpath, _dirs, files in os.walk(durable.root(self.repo)):
            for name in files:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    parts.append(f.read())
        return "\n".join(parts)

    def test_start_returns_brief(self):
        self.assertIn("open_questions", self.brief)
        self.assertEqual(self.store.session(self.session)["mode"],
                         devtalk.MODE)

    def test_turns_stay_local(self):
        devtalk.record_turn(self.store, self.session, "user",
                            "submission 是院所的一批送檢")
        devtalk.record_turn(self.store, self.session, "agent",
                            "那 registration 是 customer-level 嗎?")
        self.assertEqual(len(self.store.turns(self.session)), 2)
        self.assertNotIn("院所的一批送檢", self.durable_blob())

    def test_writing_to_closed_session_fails_loud(self):
        devtalk.end(self.store, self.repo, self.session)
        with self.assertRaises(devtalk.DevTalkError):
            devtalk.record_turn(self.store, self.session, "user", "再一句")

    def test_conversation_becomes_candidates_not_durable_writes(self):
        candidate = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "submission", "title": "submission = 院所的一批送檢"},
            "domain_expert")
        self.assertEqual(
            self.store.candidates(self.session)[0]["candidate_id"], candidate)
        self.assertFalse(os.path.isdir(
            os.path.join(durable.root(self.repo), "knowledge")))

    def test_checkpoint_writes_confirmed_candidates_only(self):
        confirmed = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "submission", "title": "submission = 院所的一批送檢"},
            "domain_expert")
        devtalk.propose(
            self.store, self.session, "domain",
            {"key": "specimen", "title": "specimen = 單一 embryo"},
            "domain_expert")
        devtalk.confirm(self.store, confirmed)
        result = devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(result["promoted"], 1)
        self.assertEqual([k["key"] for k in durable.iter_knowledge(self.repo)],
                         ["submission"])
        self.assertEqual(len(result["still_pending"]), 1)

    def test_checkpoint_result_paths_are_relative_after_cli_relativize(self):
        candidate = devtalk.propose(
            self.store, self.session, "invariant",
            {"key": "registration-level",
             "title": "registration 永遠是 customer-level"}, "domain_expert")
        devtalk.confirm(self.store, candidate)
        result = devtalk.checkpoint(self.store, self.repo, self.session)
        for path in result["written"]:
            self.assertTrue(path.startswith(self.repo), path)

    def test_rejected_candidate_is_not_written(self):
        candidate = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "wrong", "title": "錯的理解"}, "domain_expert")
        devtalk.reject(self.store, candidate, "使用者說不是這樣")
        result = devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(result["promoted"], 0)

    def test_sensitive_candidate_flagged_at_propose_time(self):
        candidate = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "conn", "title": "連線字串",
             "body": "postgres://user:secretpw@db.internal/app"},
            "domain_expert")
        row = self.store.candidates(self.session)[0]
        self.assertEqual(row["candidate_id"], candidate)
        self.assertEqual(row["sensitive"], 1)

    def test_correction_supersedes_earlier_knowledge(self):
        first = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "registration", "title": "registration = embryo-level"},
            "user_confirmed")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level(使用者更正)",
                        reason="使用者說 registration 永遠代表一個客戶")
        devtalk.checkpoint(self.store, self.repo, self.session)
        rows = self.store.knowledge(kind="domain", key="registration",
                                    statuses=("CONFIRMED", "SUPERSEDED"),
                                    limit=10)
        statuses = {r["status"] for r in rows}
        self.assertEqual(statuses, {"CONFIRMED", "SUPERSEDED"})
        current = [r for r in rows if r["status"] == "CONFIRMED"][0]
        self.assertIn("customer-level", current["title"])
        # durable 檔案跟著更新成新版本
        knowledge = [k for k in durable.iter_knowledge(self.repo)
                     if k["key"] == "registration"]
        self.assertEqual(len(knowledge), 1)
        self.assertIn("customer-level", knowledge[0]["title"])

    def test_end_closes_session_after_checkpoint(self):
        candidate = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "submission", "title": "submission = 院所批次"},
            "domain_expert")
        devtalk.confirm(self.store, candidate)
        result = devtalk.end(self.store, self.repo, self.session)
        self.assertEqual(result["promoted"], 1)
        self.assertEqual(self.store.session(self.session)["status"], "CLOSED")

    def test_status_reports_candidate_counts(self):
        candidate = devtalk.propose(
            self.store, self.session, "domain", {"key": "a", "title": "t"},
            "domain_expert")
        devtalk.confirm(self.store, candidate)
        status = devtalk.status(self.store, self.session)
        self.assertEqual(status["candidates"]["CONFIRMED"], 1)
        self.assertEqual(status["candidates"]["PENDING"], 0)

    def test_full_flow_leaves_no_transcript_in_git(self):
        for line in ("我今天想聊聊 PGS 的真實送檢流程",
                     "院所會一次送一批",
                     "registration 永遠代表一個客戶"):
            devtalk.record_turn(self.store, self.session, "user", line)
        candidate = devtalk.propose(
            self.store, self.session, "invariant",
            {"key": "registration-level",
             "title": "registration 永遠代表一個 customer",
             "body": "不是 embryo"}, "domain_expert")
        devtalk.confirm(self.store, candidate)
        devtalk.end(self.store, self.repo, self.session)
        blob = self.durable_blob()
        self.assertIn("registration 永遠代表一個 customer", blob)
        for line in ("我今天想聊聊", "院所會一次送一批"):
            self.assertNotIn(line, blob)
        payloads = json.dumps(self.store.candidates(
            self.session, statuses=("CONSOLIDATED",)), ensure_ascii=False)
        self.assertIn("registration", payloads)
