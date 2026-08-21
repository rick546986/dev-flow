"""P0-1:一般開發(Stage 6 / dev-run)完成後也要真的長出 durable memory。

舊狀態:只有 `dev-talk` 那條路(`talk checkpoint`)能把記憶固化。一般開發做完
一個 schema change,Git 有 commit,**Memory 什麼都不知道** ——
「可以存、可以查」不等於「每做一次專案就更了解專案」。

修法:把 session/checkpoint 從 dev-talk 抽成通用概念(`session` 模組),
`dev-run` 不必假裝自己是 dev-talk 才能留記憶。仍然遵守 Signal Gate:
低訊號(讀檔/grep/一般成功指令)一律不進 Git。
"""
import json
import os
import shutil

from memtools import MemoryCase, commit_all, write
from agentmem import (durable, embedding, identity, query, retrieval, session,
                      store as store_mod, sync, truth)


class ImplementationSessionTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/db.ts", "export const table = 'pgs_intake'\n")
        self.head = commit_all(self.repo, "baseline")
        self.snapshot = identity.workspace_snapshot(self.repo)
        self.workspace = identity.workspace_key(self.project_id, self.repo)

    def observe(self, sid, *args, **kwargs):
        kwargs.setdefault("repo_root", self.repo)
        return session.observe(self.store, sid, *args, **kwargs)

    def start(self, slug="lab-order-merge"):
        return session.start(self.store, self.repo, mode=session.IMPLEMENTATION,
                             topic="Stage 6:{0}".format(slug),
                             feature_slug=slug, snapshot=self.snapshot)

    def durable_blob(self):
        parts = []
        for dirpath, _dirs, files in os.walk(durable.root(self.repo)):
            for name in files:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    parts.append(f.read())
        return "\n".join(parts)

    # ── 1:schema change 走完整條路 → durable 真的出現 ───────────────────────
    def test_schema_change_reaches_durable_memory(self):
        started = self.start()
        sid = started["session_id"]
        self.assertEqual(started["mode"], session.IMPLEMENTATION)
        self.assertEqual(started["feature_slug"], "lab-order-merge")
        self.assertEqual(started["starting_head"], self.head)

        write(self.repo, "src/db.ts", "export const table = 'lab_order'\n")
        write(self.repo, "migrations/20260820_rename.sql",
              "alter table pgs_intake rename to lab_order;\n")
        new_head = commit_all(self.repo, "rename pgs_intake to lab_order")

        self.observe(sid, "schema_change",
                        "pgs_intake 改名成 lab_order",
                        body="PGS 與 ECS 之後共用同一張 lab_order",
                        file_paths=["migrations/20260820_rename.sql"],
                        commit_sha=new_head)
        self.observe(sid, "fact",
                        "database.lab-order.current_table = lab_order",
                        fact={"entity_type": "database",
                              "entity_key": "lab-order",
                              "fact_key": "current_table",
                              "value": "lab_order",
                              "dependencies": ["src/db.ts"]},
                        commit_sha=new_head)
        result = session.checkpoint(self.store, self.repo, sid)
        self.assertEqual(result["promoted"], 2)

        events = list(durable.iter_events(self.repo))
        self.assertEqual([e["kind"] for e in events], ["schema_change"])
        state = durable.read_state(self.repo, "database", "lab-order")
        self.assertEqual(state["facts"][0]["value"], "lab_order")
        self.assertTrue(state["facts"][0]["fingerprints"])

    # ── 2:低訊號不得進 durable ─────────────────────────────────────────────
    def test_low_signal_activity_never_reaches_durable(self):
        sid = self.start()["session_id"]
        for kind, title in (("file_read", "讀了 src/db.ts"),
                            ("grep", "grep lab_order"),
                            ("list_directory", "ls src/"),
                            ("command_ok", "npm test 通過")):
            self.observe(sid, kind, title)
        result = session.checkpoint(self.store, self.repo, sid)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(list(durable.iter_events(self.repo)), [])
        # 但它們仍留在本機(可查、可稽核)
        self.assertGreaterEqual(len(self.store.events(limit=20)), 4)

    def test_low_signal_is_reported_not_silently_dropped(self):
        sid = self.start()["session_id"]
        self.observe(sid, "grep", "grep lab_order")
        report = session.status(self.store, sid)
        self.assertEqual(report["low_signal_observations"], 1)
        self.assertEqual(report["candidates"]["PENDING"], 0)

    # ── 3:architecture decision → durable ─────────────────────────────────
    def test_design_decision_reaches_durable(self):
        sid = self.start()["session_id"]
        session.observe(
            self.store, sid, "decision", "PGS 與 ECS 共用 lab_order",
            decision={"key": "share-lab-order",
                      "decision": "合併成單一 lab_order 表",
                      "alternatives": "各自維護一張表",
                      "reason": "兩邊欄位重疊九成",
                      "tradeoff": "查詢要多帶 order_type"})
        result = session.checkpoint(self.store, self.repo, sid)
        self.assertEqual(result["promoted"], 1)
        decisions = list(durable.iter_decisions(self.repo))
        self.assertEqual(decisions[0]["key"], "share-lab-order")
        self.assertEqual(decisions[0]["reason"], "兩邊欄位重疊九成")

    # ── 5:沒有高訊號 → 0 promoted,不製造垃圾 ─────────────────────────────
    def test_no_high_signal_yields_zero_promoted(self):
        sid = self.start()["session_id"]
        result = session.checkpoint(self.store, self.repo, sid)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(result["written"], [])
        self.assertFalse(os.path.isdir(
            os.path.join(durable.root(self.repo), "events")))

    def test_checkpoint_never_invents_a_completion_record(self):
        sid = self.start()["session_id"]
        session.checkpoint(self.store, self.repo, sid)
        session.end(self.store, self.repo, sid)
        self.assertEqual(list(durable.iter_events(self.repo)), [])
        self.assertNotIn("完成", self.durable_blob())

    # ── 6:敏感內容 → local only ────────────────────────────────────────────
    def test_sensitive_observation_stays_local(self):
        sid = self.start()["session_id"]
        self.observe(sid, "breaking_config_change",
                        "新增資料庫連線設定",
                        body='DB_PASSWORD = "hunter2000"')
        result = session.checkpoint(self.store, self.repo, sid)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(len(result["rejected"]), 1)
        self.assertNotIn("hunter2000", self.durable_blob())

    # ── F:provenance ───────────────────────────────────────────────────────
    def test_candidate_carries_full_provenance(self):
        sid = self.start()["session_id"]
        new_head = commit_all(self.repo, "noop", allow_empty=True)
        self.observe(sid, "schema_change", "改名",
                        body="細節", file_paths=["src/db.ts"],
                        commit_sha=new_head,
                        evidence=[{"type": "test", "ref": "tests/db.test.ts"}])
        candidate = self.store.candidates(
            sid, statuses=("CONFIRMED",))[0]
        payload = candidate["payload"]
        for field in ("branch", "commit_sha", "occurred_at", "paths",
                      "evidence", "feature_slug"):
            self.assertIn(field, payload, field)
        self.assertEqual(payload["commit_sha"], new_head)
        self.assertEqual(payload["branch"], self.snapshot["branch"])
        self.assertEqual(candidate["session_id"], sid)
        self.assertEqual(candidate["authority"], "current_code")

    # ── G:VERIFIED fact 必須有可重新驗證的依據 ────────────────────────────
    def test_verified_fact_without_dependencies_is_refused(self):
        sid = self.start()["session_id"]
        with self.assertRaises(session.SessionError):
            self.observe(sid, "fact", "沒有依據的事實",
                            fact={"entity_type": "database",
                                  "entity_key": "x", "fact_key": "y",
                                  "value": "z", "status": truth.VERIFIED,
                                  "dependencies": []})

    def test_fact_without_dependencies_may_still_be_a_candidate(self):
        sid = self.start()["session_id"]
        self.observe(sid, "fact", "尚未驗證的事實",
                        fact={"entity_type": "database", "entity_key": "x",
                              "fact_key": "y", "value": "z",
                              "status": truth.CANDIDATE, "dependencies": []})
        result = session.checkpoint(self.store, self.repo, sid)
        self.assertEqual(result["promoted"], 1)
        state = durable.read_state(self.repo, "database", "x")
        self.assertEqual(state["facts"][0]["status"], truth.CANDIDATE)

    def test_missing_dependency_file_is_refused_for_verified_fact(self):
        sid = self.start()["session_id"]
        with self.assertRaises(session.SessionError):
            self.observe(sid, "fact", "指向不存在的檔",
                            fact={"entity_type": "database", "entity_key": "x",
                                  "fact_key": "y", "value": "z",
                                  "status": truth.VERIFIED,
                                  "dependencies": ["src/does-not-exist.ts"]})

    # ── session 生命週期 ───────────────────────────────────────────────────
    def test_observe_requires_an_open_session(self):
        with self.assertRaises(session.SessionError):
            self.observe("ses_00000000000000000000000000",
                         "schema_change", "x")

    def test_observe_on_closed_session_fails_loud(self):
        sid = self.start()["session_id"]
        session.end(self.store, self.repo, sid)
        with self.assertRaises(session.SessionError):
            self.observe(sid, "schema_change", "x")

    def test_two_sessions_do_not_cross_contaminate(self):
        first = self.start("feature-a")["session_id"]
        second = self.start("feature-b")["session_id"]
        self.observe(first, "schema_change", "A 的變更")
        self.observe(second, "schema_change", "B 的變更")
        result = session.checkpoint(self.store, self.repo, first)
        self.assertEqual(result["promoted"], 1)
        titles = [e["title"] for e in durable.iter_events(self.repo)]
        self.assertEqual(titles, ["A 的變更"])
        self.assertEqual(
            len(self.store.candidates(second, statuses=("CONFIRMED",))), 1)

    def test_implementation_session_is_distinguishable_from_devtalk(self):
        sid = self.start()["session_id"]
        row = self.store.session(sid)
        self.assertEqual(row["mode"], session.IMPLEMENTATION)
        self.assertNotEqual(row["mode"], session.UNDERSTANDING)

    def test_abandoned_session_is_not_reported_as_closed(self):
        sid = self.start()["session_id"]
        self.assertEqual(self.store.session(sid)["status"], "OPEN")
        session.abort(self.store, sid, reason="使用者中斷")
        self.assertEqual(self.store.session(sid)["status"], "ABORTED")


class ImplementationRebuildTest(MemoryCase):
    """4:刪掉 local DB → rebuild → Stage 6 產生的記憶還查得到。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        write(self.repo, "src/db.ts", "export const table = 'pgs_intake'\n")
        commit_all(self.repo, "baseline")

    def observe(self, store, sid, *args, **kwargs):
        kwargs.setdefault("repo_root", self.repo)
        return session.observe(store, sid, *args, **kwargs)

    def build_feature(self):
        store = store_mod.open_for_root(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        sid = session.start(store, self.repo, mode=session.IMPLEMENTATION,
                            topic="Stage 6:lab-order-merge",
                            feature_slug="lab-order-merge",
                            snapshot=snapshot)["session_id"]
        write(self.repo, "src/db.ts", "export const table = 'lab_order'\n")
        write(self.repo, "migrations/20260820_rename.sql",
              "alter table pgs_intake rename to lab_order;\n")
        head = commit_all(self.repo, "rename pgs_intake to lab_order")
        self.observe(store, sid, "table_rename",
                        "pgs_intake 改名成 lab_order",
                        body="PGS 與 ECS 之後共用同一張 lab_order 表",
                        file_paths=["migrations/20260820_rename.sql"],
                        commit_sha=head)
        self.observe(store, sid, "fact",
                        "database.lab-order.current_table = lab_order",
                        fact={"entity_type": "database",
                              "entity_key": "lab-order",
                              "fact_key": "current_table",
                              "value": "lab_order",
                              "dependencies": ["src/db.ts"]},
                        commit_sha=head)
        self.observe(store, sid, "decision", "PGS 與 ECS 共用 lab_order",
                        decision={"key": "share-lab-order",
                                  "decision": "合併成單一 lab_order 表",
                                  "alternatives": "各自維護一張表",
                                  "reason": "兩邊欄位重疊九成,分開維護會讓 "
                                            "migration 永遠寫兩份",
                                  "tradeoff": "查詢要多帶 order_type"})
        session.end(store, self.repo, sid)
        store.close()

    def test_another_machine_learns_what_this_feature_did(self):
        self.build_feature()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        embedder = embedding.Embedder()
        embedder.reindex(fresh)
        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)

        history = query.execute(fresh, self.repo, "之前 lab_order 改過什麼?",
                                workspace, snapshot, embedder)
        self.assertEqual(history["retrieval_status"], retrieval.OK)
        self.assertIn("pgs_intake",
                      " ".join(h["title"] for h in history["results"]))

        current = query.execute(
            fresh, self.repo, "目前 lab-order 的 current_table 是什麼?",
            workspace, snapshot, embedder)
        self.assertEqual(current["retrieval_status"], retrieval.OK)
        self.assertEqual(current["current_truth"]["value"], "lab_order")

        why = query.execute(fresh, self.repo, "為什麼要共用 lab order?",
                            workspace, snapshot, embedder)
        self.assertEqual(why["retrieval_status"], retrieval.OK)
        self.assertEqual(why["results"][0]["item_type"], "decision")
        self.assertIn("欄位重疊", why["results"][0]["reason"])

    def test_why_without_decision_evidence_is_no_reliable_match(self):
        """沒有 decision 證據時,WHY 不得拿 event 硬猜理由。"""
        store = store_mod.open_for_root(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        sid = session.start(store, self.repo, mode=session.IMPLEMENTATION,
                            topic="Stage 6:no-decision",
                            feature_slug="no-decision",
                            snapshot=snapshot)["session_id"]
        self.observe(store, sid, "table_rename", "aaa_table 改名成 bbb_table",
                        body="只有事件,沒有任何 decision 記錄")
        session.end(store, self.repo, sid)
        store.close()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        embedder = embedding.Embedder()
        embedder.reindex(fresh)
        answer = query.execute(
            fresh, self.repo, "為什麼要把 aaa_table 改名成 bbb_table?",
            identity.workspace_key(self.project_id, self.repo),
            identity.workspace_snapshot(self.repo), embedder)
        self.assertEqual(answer["retrieval_status"],
                         retrieval.NO_RELIABLE_MATCH)
