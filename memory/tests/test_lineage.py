"""P0-3:修正的歷史必須跨機器保留。

問題:`.dev-flow/knowledge/domain/registration.*.yaml` 是**現況物化視圖**,
correct() 之後它只剩 v2。另一台機器 clone → 沒有 local DB → rebuild,
只重建得出 v2 ——「以前 agent 以為 registration 是 embryo-level,後來使用者
更正成 customer-level」這段 lineage 就消失了。Git commit history 也許看得到,
但 **Agent Memory 自己查不到**,而查得到才是 durable memory 的目的。

解法:current materialized view + **append-only revision event**。
三種 supersede 語意必須一致:
    knowledge_corrected / fact_superseded / decision_superseded
"""
import json
import os
import shutil

from memtools import MemoryCase, commit_all, write
from agentmem import (devtalk, durable, embedding, identity, lineage, query,
                      store as store_mod, sync, truth)


class LineageEventTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("registration 語意")

    def durable_events(self):
        return list(durable.iter_events(self.repo))

    def test_knowledge_correction_writes_durable_revision_event(self):
        first = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "registration", "title": "registration = embryo-level",
             "body": "每個 embryo 一筆"}, "agent_hypothesis")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)

        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level",
                        body="一個客戶在 submission 內的送檢紀錄",
                        reason="使用者更正:registration 永遠代表一個客戶")
        devtalk.checkpoint(self.store, self.repo, self.session)

        revisions = [e for e in self.durable_events()
                     if e.get("kind") == lineage.KNOWLEDGE_CORRECTED]
        self.assertEqual(len(revisions), 1)
        record = revisions[0]
        self.assertEqual(record["memory_kind"], "domain")
        self.assertEqual(record["key"], "registration")
        self.assertIn("embryo-level", record["previous_title"])
        self.assertIn("customer-level", record["new_title"])
        self.assertIn("使用者更正", record["reason"])
        self.assertEqual(record["previous_status"], "SUPERSEDED")
        self.assertEqual(record["new_status"], "CONFIRMED")
        self.assertEqual(record["previous_authority"], "agent_hypothesis")
        self.assertEqual(record["new_authority"], "user_confirmed")
        self.assertTrue(record["previous_id"])
        self.assertTrue(record["occurred_at"])

    def test_current_materialized_view_stays_single(self):
        first = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "registration", "title": "v1"}, "agent_hypothesis")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "v2", reason="更正")
        devtalk.checkpoint(self.store, self.repo, self.session)
        records = [k for k in durable.iter_knowledge(self.repo)
                   if k["key"] == "registration"]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "v2")

    def test_no_revision_event_when_nothing_was_superseded(self):
        candidate = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "brand-new", "title": "第一次記錄"}, "domain_expert")
        devtalk.confirm(self.store, candidate)
        devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(
            [e for e in self.durable_events()
             if e.get("kind") == lineage.KNOWLEDGE_CORRECTED], [])

    def test_fact_supersede_writes_durable_revision_event(self):
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        head = commit_all(self.repo, "seed")
        workspace = identity.workspace_key(self.project_id, self.repo)
        fact_id = truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/db.ts"], source_commit=head,
            status=truth.VERIFIED, confidence=0.99)
        sync.promote_entity_facts(self.repo, self.store, "database", "lab-order")
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        truth.resolve_current(self.store, self.repo, "database", "lab-order",
                              "current_table", workspace,
                              identity.workspace_snapshot(self.repo))
        outcome = truth.reverify(self.store, self.repo, fact_id, workspace,
                                 "orders", session_id=self.session)
        self.assertEqual(outcome["outcome"], "superseded")
        # revision 先落 local,由 consolidation 刷成 durable
        sync.consolidate(self.repo, self.store, self.session)
        revisions = [e for e in self.durable_events()
                     if e.get("kind") == lineage.FACT_SUPERSEDED]
        self.assertEqual(len(revisions), 1)
        record = revisions[0]
        self.assertEqual(record["previous_value"], "lab_order")
        self.assertEqual(record["new_value"], "orders")
        self.assertEqual(record["key"], "database.lab-order.current_table")

    def test_decision_supersede_writes_durable_revision_event(self):
        first = devtalk.propose(
            self.store, self.session, "decision",
            {"key": "table-strategy", "title": "各自維護一張表",
             "decision": "PGS 與 ECS 各自一張", "reason": "耦合最小"},
            "architecture_decision")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)
        second = devtalk.propose(
            self.store, self.session, "decision",
            {"key": "table-strategy", "title": "共用 lab_order",
             "decision": "合併成 lab_order", "reason": "欄位重疊九成",
             "supersedes_reason": "維護兩份 migration 的成本超過耦合"},
            "architecture_decision")
        devtalk.confirm(self.store, second)
        devtalk.checkpoint(self.store, self.repo, self.session)
        revisions = [e for e in self.durable_events()
                     if e.get("kind") == lineage.DECISION_SUPERSEDED]
        self.assertEqual(len(revisions), 1)
        self.assertIn("各自維護", revisions[0]["previous_title"])
        self.assertIn("共用", revisions[0]["new_title"])

    def test_revision_events_pass_the_same_durable_gates(self):
        """lineage event 一樣要過敏感/絕對路徑守衛 —— 不得因為是系統產生就放行。"""
        first = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "creds", "title": "連線設定 v1"}, "domain_expert")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)
        devtalk.correct(self.store, self.session, "domain", "creds",
                        "連線設定 v2",
                        body='DB_PASSWORD = "hunter2000"',
                        reason="補上連線資訊")
        result = devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(result["promoted"], 0)
        blob = "\n".join(
            json.dumps(e, ensure_ascii=False) for e in self.durable_events())
        self.assertNotIn("hunter2000", blob)


class DestructiveRebuildTest(MemoryCase):
    """完整的破壞性重建:刪掉整個 local project 目錄後,lineage 仍查得到。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]

    def build_history(self):
        store = store_mod.Store.open(self.project_id)
        session = store.start_session("registration 語意")
        first = devtalk.propose(
            store, session, "domain",
            {"key": "registration",
             "title": "registration = embryo-level 的送檢紀錄",
             "body": "每個 embryo 一筆"}, "agent_hypothesis")
        devtalk.confirm(store, first)
        devtalk.checkpoint(store, self.repo, session)
        devtalk.correct(
            store, session, "domain", "registration",
            "registration = customer-level 的送檢紀錄",
            body="一個客戶在 submission 內的送檢紀錄,不是 embryo",
            reason="使用者更正:registration 永遠代表一個客戶")
        devtalk.checkpoint(store, self.repo, session)
        rows = store.knowledge(kind="domain", key="registration",
                               statuses=("CONFIRMED", "SUPERSEDED"), limit=10)
        statuses = {r["status"] for r in rows}
        store.close()
        return statuses

    def test_correction_history_survives_deleting_local_db(self):
        self.assertEqual(self.build_history(), {"CONFIRMED", "SUPERSEDED"})

        # 整包刪掉 local project(不是只刪 DB 檔)
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        self.assertFalse(os.path.isdir(
            os.path.join(self.home, "projects", self.project_id)))

        fresh = self.store_for(self.project_id)
        counts = sync.rebuild_local(self.repo, fresh)
        self.assertGreaterEqual(counts["events"], 1)

        # 現況:v2
        current = fresh.knowledge(kind="domain", key="registration",
                                  statuses=("CONFIRMED",), limit=5)
        self.assertEqual(len(current), 1)
        self.assertIn("customer-level", current[0]["title"])

        # 歷史:找得到 v1 → v2 的更正,理由還在
        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == lineage.KNOWLEDGE_CORRECTED]
        self.assertEqual(len(revisions), 1)
        self.assertIn("embryo-level", revisions[0]["previous_title"])
        self.assertIn("使用者更正", revisions[0]["reason"])

    def test_correction_history_is_retrievable_after_rebuild(self):
        """不只檔案裡有 —— 重建之後要能**查得到**。"""
        self.build_history()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        embedder = embedding.Embedder()
        embedder.reindex(fresh)

        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)

        history = query.execute(fresh, self.repo,
                                "之前 registration 改過什麼?", workspace,
                                snapshot, embedder)
        blob = " ".join(
            "{0} {1}".format(hit.get("title", ""), hit.get("text", ""))
            for hit in history["results"])
        self.assertIn("embryo-level", blob,
                      "重建之後查不到舊理解 = lineage 沒有真的 durable")
        self.assertIn("customer-level", blob)

        current = query.execute(fresh, self.repo, "registration 是什麼意思?",
                                workspace, snapshot, embedder)
        self.assertEqual(current["results"][0]["key"], "registration")
        self.assertIn("customer-level", current["results"][0]["title"])

    def test_rebuild_does_not_duplicate_revision_events(self):
        self.build_history()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        first = len(fresh.events(limit=100))
        sync.rebuild_local(self.repo, fresh)
        self.assertEqual(len(fresh.events(limit=100)), first)
