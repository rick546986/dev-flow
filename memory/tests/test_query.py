"""Query Planning 與 Execution Engine(§20/§25/§31)。"""
from memtools import MemoryCase, commit_all, write
from agentmem import embedding, identity, query, retrieval, truth


class PlannerTest(MemoryCase):
    CASES = (
        ("目前 lab_order 使用哪張 table?", query.CURRENT),
        ("現在使用哪一張資料表?", query.CURRENT),
        ("what is the current table for lab orders?", query.CURRENT),
        ("之前為什麼修改 registration?", query.WHY),
        ("為什麼選 sqlite-wasm?", query.WHY),
        ("why did we rename the table?", query.WHY),
        ("之前發生過什麼事?", query.HISTORY),
        ("registration 是什麼意思?", query.DOMAIN),
        ("what does registration mean?", query.DOMAIN),
        ("怎麼部署?", query.HOW),
        ("how to run the migration?", query.HOW),
        ("我們未來打算怎麼做 lab order?", query.INTENT),
        ("roadmap 上有什麼?", query.INTENT),
        ("列出所有 domain 規則", query.DISCOVERY),
    )

    def test_intent_classification(self):
        for text, expected in self.CASES:
            self.assertEqual(query.plan(text)["primary"], expected, text)

    def test_why_beats_history_on_tie(self):
        plan = query.plan("之前為什麼修改 registration?")
        self.assertEqual(plan["primary"], query.WHY)
        self.assertIn(query.HISTORY, plan["secondary"])
        self.assertEqual(plan["kind"], query.MIXED)

    def test_entities_extracted_from_query(self):
        plan = query.plan("pgs_intake_registration 現在還在用嗎?")
        self.assertIn("pgs_intake_registration", plan["entities"])

    def test_as_of_and_branch_parsed(self):
        plan = query.plan("2026-07-01 之前 branch: feature/x 改了什麼?")
        self.assertEqual(plan["as_of"], "2026-07-01T23:59:59Z")
        self.assertEqual(plan["branch"], "feature/x")

    def test_current_requires_verification(self):
        self.assertTrue(query.plan("目前用哪張表?")["requires_verification"])
        self.assertFalse(query.plan("之前發生什麼?")["requires_verification"])

    def test_no_cue_falls_back_to_discovery(self):
        self.assertEqual(query.plan("registration")["primary"], query.DISCOVERY)


class ExecutionTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.embedder = embedding.Embedder()
        write(self.repo, "src/services/db.ts",
              "export const table = 'lab_order'\n")
        self.head = commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.snapshot = identity.workspace_snapshot(self.repo)
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/services/db.ts"],
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)
        self.store.upsert_knowledge({
            "kind": "domain", "key": "registration",
            "title": "registration = 一個客戶在 submission 內的送檢紀錄",
            "body": "customer-level,不是 embryo", "authority": "domain_expert",
            "status": "CONFIRMED", "confidence": 0.95})
        self.store.upsert_knowledge({
            "kind": "intent", "key": "shared-lab-order",
            "title": "未來 PGS 與 ECS 共用 lab order 架構",
            "authority": "architecture_decision", "status": "CONFIRMED",
            "confidence": 0.9, "implemented": False})
        self.store.upsert_decision({
            "key": "share-lab-order", "title": "PGS/ECS 共用 lab order 表",
            "decision": "合併成 lab_order", "reason": "兩邊欄位重疊九成",
            "alternatives": "各自維護", "status": "ACCEPTED"})
        self.store.add_event(
            "table_rename", "registration 欄位改名",
            "把 registration 從 specimen-level 改成 customer-level",
            occurred_at="2026-06-01T00:00:00Z", branch="main", signal="high")
        self.store.upsert_skill({
            "key": "deploy", "title": "部署流程",
            "steps": ["跑 migration", "重啟 worker"], "status": "VERIFIED",
            "verification": "打 /health 回 200"})
        self.embedder.reindex(self.store)

    def ask(self, text):
        return query.execute(self.store, self.repo, text, self.workspace,
                             self.snapshot, self.embedder)

    def test_current_uses_fast_path(self):
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertTrue(answer["current_truth"]["fast_path"])
        self.assertEqual(answer["current_truth"]["value"], "lab_order")

    def test_current_goes_stale_when_dependency_changes(self):
        write(self.repo, "src/services/db.ts", "export const table = 'x'\n")
        snapshot = identity.workspace_snapshot(self.repo)
        answer = query.execute(self.store, self.repo,
                               "目前 lab-order 的 current_table 是什麼?",
                               self.workspace, snapshot, self.embedder)
        self.assertNotIn("current_truth", answer)
        self.assertTrue(answer["needs_inspect"])
        self.assertTrue(any("STALE" in u for u in answer["uncertainty"]))

    def test_domain_answer_comes_from_confirmed_knowledge(self):
        answer = self.ask("registration 是什麼意思?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["results"][0]["key"], "registration")
        self.assertEqual(answer["results"][0]["authority"], "domain_expert")

    def test_domain_conflict_is_surfaced_not_resolved(self):
        truth.reconcile_with_code(self.store, "domain", "registration",
                                  "src/models/x.ts 看起來是 specimen-level",
                                  "current_code", supports=False)
        self.embedder.reindex(self.store)
        answer = self.ask("registration 是什麼意思?")
        self.assertEqual(answer["results"][0]["status"], truth.CONFLICT)
        self.assertTrue(any("CONFLICT" in u for u in answer["uncertainty"]))

    def test_intent_is_labelled_planned(self):
        answer = self.ask("我們未來打算怎麼做 lab order?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["results"][0]["implementation_state"], "planned")
        self.assertTrue(any("尚未實作" in u for u in answer["uncertainty"]))

    def test_intent_query_does_not_return_implementation_facts(self):
        answer = self.ask("我們未來打算怎麼做 lab order?")
        for hit in answer["results"]:
            self.assertEqual(hit["item_type"], "knowledge")
            self.assertEqual(hit["kind"], "intent")

    def test_why_prefers_decision(self):
        answer = self.ask("為什麼要共用 lab order?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["results"][0]["item_type"], "decision")
        self.assertEqual(answer["results"][0]["reason"], "兩邊欄位重疊九成")

    def test_how_returns_skill_steps(self):
        answer = self.ask("怎麼部署?")
        self.assertEqual(answer["results"][0]["steps"],
                         ["跑 migration", "重啟 worker"])

    def test_history_returns_events_newest_first(self):
        self.store.add_event("table_rename", "registration 再次調整",
                             occurred_at="2026-07-01T00:00:00Z", branch="main",
                             signal="high")
        self.embedder.reindex(self.store)
        answer = self.ask("之前 registration 改過什麼?")
        stamps = [r["occurred_at"] for r in answer["results"]]
        self.assertEqual(stamps, sorted(stamps, reverse=True))

    def test_no_reliable_match_envelope(self):
        answer = self.ask("咖啡機壞了要找誰修?")
        self.assertEqual(answer["retrieval_status"], retrieval.NO_RELIABLE_MATCH)
        self.assertEqual(answer["results"], [])
        self.assertEqual(answer["confidence"], 0.0)
        self.assertTrue(answer["uncertainty"])

    def test_envelope_always_has_four_fields(self):
        for text in ("目前用哪張表?", "為什麼改?", "怎麼部署?",
                     "registration 是什麼意思?", "咖啡機壞了要找誰修?"):
            answer = self.ask(text)
            for field in ("retrieval_status", "confidence", "evidence",
                          "uncertainty"):
                self.assertIn(field, answer, (text, field))

    def test_metrics_are_recorded(self):
        self.ask("目前用哪張表?")
        rows = self.store.conn.execute(
            "SELECT query_kind, status FROM retrieval_metrics").fetchall()
        self.assertEqual(len(rows), 1)

    def test_unknown_fact_reports_unknown_not_a_guess(self):
        answer = self.ask("目前 worker 的 port 是什麼?")
        self.assertTrue(answer["retrieval_status"] == retrieval.NO_RELIABLE_MATCH
                        or not answer.get("current_truth"))


class ContextBuilderTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/services/db.ts", "export const t = 'lab_order'\n")
        self.head = commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        truth.record_fact(self.store, self.repo, "database", "lab-order",
                          "current_table", "lab_order",
                          dependencies=["src/services/db.ts"],
                          source_commit=self.head, status=truth.VERIFIED,
                          confidence=0.99)
        truth.assert_knowledge(self.store, "invariant", "registration-level",
                               "registration 永遠是 customer-level",
                               authority="domain_expert", status="CONFIRMED")
        truth.assert_knowledge(self.store, "intent", "shared-lab-order",
                               "未來共用 lab order",
                               authority="architecture_decision",
                               status="CONFIRMED", implemented=False)
        self.store.add_event("schema_change", "改名成 lab_order",
                             occurred_at="2026-07-01T00:00:00Z", branch="main",
                             signal="high")

    def build(self, **kwargs):
        from agentmem import context
        return context.build(self.store, self.repo, self.workspace,
                             identity.workspace_snapshot(self.repo), **kwargs)

    def test_startup_context_is_small_and_structured(self):
        payload = self.build()
        self.assertLessEqual(payload["size"], payload["budget"])
        self.assertIn("project_id", payload["text"])
        self.assertIn("lab_order", payload["text"])
        self.assertIn("registration 永遠是 customer-level", payload["text"])

    def test_planned_intent_is_marked_in_context(self):
        self.assertIn("PLANNED", self.build()["text"])

    def test_context_does_not_read_context_md(self):
        """§27:startup context 不依賴 CONTEXT.md —— 檔案存在也不讀。"""
        write(self.repo, "CONTEXT.md", "# 舊詞彙表\n\n**不該被注入的內容**\n")
        payload = self.build()
        self.assertNotIn("不該被注入的內容", payload["text"])
        self.assertNotIn("舊詞彙表", payload["text"])

    def test_dirty_workspace_is_flagged(self):
        write(self.repo, "src/services/db.ts", "changed\n")
        payload = self.build()
        self.assertIn("STALE", payload["text"])

    def test_open_conflict_appears_in_context(self):
        truth.assert_knowledge(self.store, "domain", "registration",
                               "registration = customer-level",
                               authority="domain_expert", status="CONFIRMED")
        truth.reconcile_with_code(self.store, "domain", "registration",
                                  "看起來是 specimen-level", "current_code",
                                  supports=False)
        self.assertIn("Open conflicts", self.build()["text"])

    def test_budget_truncates_sections_but_keeps_instructions(self):
        payload = self.build(budget=400)
        self.assertIn("Memory", payload["text"])
        self.assertTrue(payload["truncated"])

    def test_query_instructions_are_always_present(self):
        self.assertIn("NO_RELIABLE_MATCH", self.build()["text"])
