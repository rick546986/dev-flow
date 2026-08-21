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
                      session as session_mod, store as store_mod, sync, truth)


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
        store = store_mod.open_for_root(self.project_id, self.repo)
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


class ReverifyNewValueIsDurableTest(MemoryCase):
    """`verify` 產出的新 Current Truth 必須自己走到 `.dev-flow/`。

    `reverify()` 回 VERIFIED 是**對外的斷言**:呼叫端(以及 SKILL、CLI)在那
    之後就把新值當現況用。但它只動 local facts 表 + 記一筆 pending revision,
    而 `checkpoint()` 只在有 **CONFIRMED fact 候選**進 `consolidate()` 時才把
    entity 加進 `entities_touched` → 才 `write_state()` 整檔寫回。

    所以沒有另一條路碰同一個 entity 時,durable 側的現況檔仍是 v1:

        durable v1 → 改依賴 → verify --observed v2 → local 說 VERIFIED/v2
        → checkpoint(只落了 revision 事件)→ 砍掉 SQLite → rebuild
        → **現況回到 v1**

    revision 是歷史,不是現況物化視圖的替代品。這一組刻意**不呼叫 observe
    fact** —— 補一次 observe 就等於用另一條路遮住這個缺口,而使用者不會知道
    自己必須那樣做。

    不變量:任何回傳 VERIFIED 新值的 API,要嘛已經有 durable 表示,要嘛留下
    一個**機械上看得見**的 pending durable 操作,擋住乾淨的收尾。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.store.register_workspace(
            self.workspace, identity.workspace_snapshot(self.repo))
        self.session = self.store.start_session("驗證一輪",
                                                mode="implementation")
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        head = commit_all(self.repo, "seed")
        self.fact_id = truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/db.ts"], source_commit=head,
            status=truth.VERIFIED, confidence=0.99)
        sync.promote_entity_facts(self.repo, self.store, "database",
                                  "lab-order")

    def durable_values(self):
        out = []
        for state in durable.iter_states(self.repo):
            for fact in state.get("facts") or []:
                if fact.get("fact_key") == "current_table":
                    out.append((fact["value"], fact.get("status")))
        return out

    def reverify_to_v2(self):
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        commit_all(self.repo, "rename")
        truth.resolve_current(self.store, self.repo, "database", "lab-order",
                              "current_table", self.workspace,
                              identity.workspace_snapshot(self.repo))
        outcome = truth.reverify(
            self.store, self.repo, self.fact_id, self.workspace, "orders",
            session_id=self.session, reason="表被改名了")
        self.assertEqual(outcome["outcome"], "superseded")
        return outcome

    def test_durable_current_state_moves_to_v2_after_checkpoint(self):
        self.reverify_to_v2()
        session_mod.checkpoint(self.store, self.repo, self.session)
        values = dict(self.durable_values())
        self.assertIn("orders", values,
                      "checkpoint 之後 `.dev-flow/` 的現況檔仍然沒有 v2 —— "
                      "revision 是歷史,不是現況物化視圖的替代品")
        self.assertEqual(values["orders"], truth.VERIFIED)

    def test_current_truth_is_v2_after_destructive_rebuild(self):
        """不補 observe:砍掉 local、只從 `.dev-flow/` 重建,現況必須是 v2。"""
        self.reverify_to_v2()
        session_mod.checkpoint(self.store, self.repo, self.session)
        self.store.close()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        resolved = truth.resolve_current(
            fresh, self.repo, "database", "lab-order", "current_table",
            self.workspace, identity.workspace_snapshot(self.repo))
        self.assertEqual(
            resolved["value"], "orders",
            "另一台機器 rebuild 之後現況回到 v1 —— 重新驗證過的值從來沒有離開"
            "這台機器,而 local 說它 VERIFIED")

    def test_history_still_contains_the_v1_to_v2_lineage(self):
        self.reverify_to_v2()
        session_mod.checkpoint(self.store, self.repo, self.session)
        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == lineage.FACT_SUPERSEDED]
        self.assertEqual(len(revisions), 1)
        self.assertEqual(revisions[0]["previous_value"], "lab_order")
        self.assertEqual(revisions[0]["new_value"], "orders")

    def test_old_value_is_superseded_not_deleted_in_durable(self):
        self.reverify_to_v2()
        session_mod.checkpoint(self.store, self.repo, self.session)
        values = dict(self.durable_values())
        self.assertEqual(values.get("lab_order"), truth.SUPERSEDED,
                         "舊值要留在 durable 側並標 SUPERSEDED,不是被刪掉")

    def test_durable_check_blocks_finalization_before_the_rewrite(self):
        """收尾前必須有一個**機械上看得見**的 pending durable 操作。

        「reverify 之後忘了 checkpoint」不能只是一句期望 —— 它要擋得住。
        """
        self.reverify_to_v2()
        verdict = sync.durable_check(self.repo, self.store)
        self.assertEqual(
            verdict["verdict"], "FAIL",
            "reverify 產生了還沒落地的新現況,durable-check 卻說可以收尾")
        self.assertTrue(
            any(sync.PENDING_FACT in p for p in verdict["problems"]),
            "理由裡沒有「現況檔還沒重寫」——「歷史沒落地」與「現況沒落地」"
            "是兩件事,只報前者的話後者是靜默的:{0}".format(verdict["problems"]))
