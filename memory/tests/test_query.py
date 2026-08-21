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

    def test_current_target_beyond_row_window_still_resolves(self):
        """GPT-P1-CURRENT-500:exact CURRENT target 不得被列數窗口擋在相關性
        比對之前 —— 插 500 筆比它新的 live fact(把它擠出前 500 筆)之後,
        對它的精確查詢仍要正常解出,不能因為它被排在視窗外就變成查不到。"""
        for i in range(500):
            truth.record_fact(
                self.store, self.repo, "filler", "filler-{0}".format(i),
                "noise", "value", status=truth.CANDIDATE, confidence=0.1,
                now="2030-01-01T00:00:00Z")
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertTrue(answer["current_truth"]["fast_path"])
        self.assertEqual(answer["current_truth"]["value"], "lab_order")

    def test_current_target_scope_excludes_unnamed_entity_with_same_fact_key(self):
        """GPT-P1-CURRENT-TARGET-SCOPE:不同 entity 共用同一個 fact_key
        (兩個都有 `current_table`)時,查詢只指名其中一個 entity,不能因為
        另一個 entity 剛好共用 fact_key 就把它也拉進同一筆聚合查詢——它的
        CANDIDATE 狀態不該去拖累被指名 entity 的 VERIFIED 精確答案。"""
        truth.record_fact(
            self.store, self.repo, "database", "audit", "current_table",
            "audit_log", status=truth.CANDIDATE, confidence=0.3)
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertTrue(answer["current_truth"]["fast_path"])
        self.assertEqual(answer["current_truth"]["value"], "lab_order")
        resolved_keys = {(r["entity_key"], r["fact_key"])
                         for r in answer["resolved"]}
        self.assertEqual(resolved_keys, {("lab-order", "current_table")})

    def test_current_target_scope_excludes_unnamed_entity_when_stale(self):
        """同上,另一個沒被指名的 entity 是 STALE 而不是 CANDIDATE —— 一樣
        不能被拉進同一筆聚合查詢去拖累被指名 entity 的答案。"""
        truth.record_fact(
            self.store, self.repo, "database", "audit", "current_table",
            "audit_log", status=truth.STALE, confidence=0.3)
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["current_truth"]["value"], "lab_order")

    def test_current_target_scope_ambiguous_fact_key_without_entity(self):
        """查詢完全沒有指名任何 entity,只給了一個兩個 entity 都有的
        fact_key —— 不能悄悄選一個當成唯一 CURRENT 答案;必須不是
        fast-path OK(落到 NEEDS_VERIFICATION 或更嚴重)。"""
        truth.record_fact(
            self.store, self.repo, "database", "audit", "current_table",
            "audit_log", status=truth.VERIFIED, confidence=0.9)
        answer = self.ask("current_table 現在是什麼?")
        self.assertNotEqual(answer["retrieval_status"], retrieval.OK)
        self.assertNotIn("current_truth", answer)

    def test_current_fact_scope_excludes_unnamed_fact_on_named_entity(self):
        """GPT-P1-CURRENT-FACT-SCOPE:查詢同時指名 entity 與 fact_key 時,
        同一個 entity 底下**沒被指名**的其他 fact 不得進候選 —— 否則它的
        CANDIDATE 狀態會把精確答案從 OK 拖成 NEEDS_VERIFICATION。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.CANDIDATE, confidence=0.3)
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertTrue(answer["current_truth"]["fast_path"])
        self.assertEqual(answer["current_truth"]["value"], "lab_order")
        resolved_keys = {(r["entity_key"], r["fact_key"])
                         for r in answer["resolved"]}
        self.assertEqual(resolved_keys, {("lab-order", "current_table")})

    def test_current_fact_scope_unnamed_stale_fact_does_not_downgrade(self):
        """同上,沒被指名的同 entity fact 是 STALE —— 一樣不得拖累精確答案。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.STALE, confidence=0.3)
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["current_truth"]["value"], "lab_order")

    def test_current_fact_scope_unnamed_conflict_fact_does_not_escalate(self):
        """沒被指名的同 entity fact 是 CONFLICT —— 不得把精確查詢升級成
        CONFLICT。CONFLICT 是最嚴重狀態,誤報的代價比 NEEDS_VERIFICATION 更高:
        呼叫端會以為「兩個來源互相矛盾」,而實際上被問的那個座標沒有矛盾。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.CONFLICT, confidence=0.3)
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["current_truth"]["value"], "lab_order")

    def test_current_entity_only_query_still_aggregates_all_facts(self):
        """查詢只指名 entity、沒指名任何 fact_key 時,**刻意保留**「回傳這個
        entity 底下全部 fact」的既有語意 —— 被問的座標就是 entity 本身,所以
        每一筆都在範圍內,整體降級是對的而不是污染。這一案把這個語意明寫成
        斷言(GPT 要求「explicitly verify the intended product behavior」),
        免得它只是實作的副作用、被下一次重構默默改掉。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.CANDIDATE, confidence=0.3)
        answer = self.ask("目前 lab-order 是什麼狀況?")
        self.assertEqual(answer["retrieval_status"], query.NEEDS_VERIFICATION)
        resolved_keys = {(r["entity_key"], r["fact_key"])
                         for r in answer["resolved"]}
        self.assertEqual(resolved_keys, {("lab-order", "current_table"),
                                         ("lab-order", "migration_state")})

    def test_envelope_always_has_per_coordinate(self):
        """D-4: `per_coordinate` 必填,所有 query kind 都在,不得省略。
        選填加 `.get()` 等於讓 None 靜默當成空 —— owner 裁決明文禁止。"""
        for text in ("目前 lab-order 的 current_table 是什麼?",
                     "目前 lab-order 是什麼狀況?",
                     "為什麼改?", "怎麼部署?",
                     "registration 是什麼意思?",
                     "咖啡機壞了要找誰修?",
                     "之前發生過什麼事?",
                     "我們未來打算怎麼做 lab order?"):
            answer = self.ask(text)
            self.assertIn("per_coordinate", answer, text)
            self.assertIsInstance(answer["per_coordinate"], list, text)
            self.assertIsNotNone(answer["per_coordinate"], text)

    def test_entity_only_mixed_state_per_coordinate_identifies_downgrade(self):
        """D-4 驗收 9:lab-order.current_table=VERIFIED +
        lab-order.migration_state=CANDIDATE。既有聚合仍是
        NEEDS_VERIFICATION;`per_coordinate` 指出是哪一座標造成降級。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.CANDIDATE, confidence=0.3)
        answer = self.ask("目前 lab-order 是什麼狀況?")
        self.assertEqual(answer["retrieval_status"], query.NEEDS_VERIFICATION)
        self.assertNotIn("current_truth", answer)
        by_key = {(row["entity_key"], row["fact_key"]): row
                  for row in answer["per_coordinate"]}
        self.assertEqual(set(by_key), {("lab-order", "current_table"),
                                       ("lab-order", "migration_state")})
        table = by_key[("lab-order", "current_table")]
        mig = by_key[("lab-order", "migration_state")]
        self.assertEqual(table["entity_type"], "database")
        self.assertEqual(table["truth_status"], truth.VERIFIED)
        self.assertEqual(table["retrieval_status"], retrieval.OK)
        self.assertEqual(table["value"], "lab_order")
        self.assertEqual(mig["truth_status"], truth.CANDIDATE)
        self.assertEqual(mig["retrieval_status"], query.NEEDS_VERIFICATION)
        self.assertEqual(mig["value"], "pending")

    def test_per_coordinate_distinguishes_stale_and_conflict(self):
        """D-4 驗收 3:同一 entity 底下 STALE / CONFLICT 必須能從
        `per_coordinate` 分開讀出來,不能只剩頂層一個嚴重狀態。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.STALE, confidence=0.3)
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "owner_team",
            "platform", status=truth.CONFLICT, confidence=0.2)
        answer = self.ask("目前 lab-order 是什麼狀況?")
        self.assertEqual(answer["retrieval_status"], query.CONFLICT)
        by_key = {(row["entity_key"], row["fact_key"]): row
                  for row in answer["per_coordinate"]}
        self.assertEqual(by_key[("lab-order", "current_table")]["truth_status"],
                         truth.VERIFIED)
        self.assertEqual(by_key[("lab-order", "current_table")]["retrieval_status"],
                         retrieval.OK)
        self.assertEqual(by_key[("lab-order", "migration_state")]["truth_status"],
                         truth.STALE)
        self.assertEqual(by_key[("lab-order", "migration_state")]["retrieval_status"],
                         query.NEEDS_VERIFICATION)
        self.assertEqual(by_key[("lab-order", "owner_team")]["truth_status"],
                         truth.CONFLICT)
        self.assertEqual(by_key[("lab-order", "owner_team")]["retrieval_status"],
                         query.CONFLICT)

    def test_named_fact_per_coordinate_does_not_reintroduce_fact_scope(self):
        """D-4 驗收 6:指名 entity + fact_key 時,`per_coordinate` 仍只含
        那個座標,不得把同 entity 底下沒被問的 CANDIDATE 拉回來。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.CANDIDATE, confidence=0.3)
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["current_truth"]["value"], "lab_order")
        keys = {(row["entity_key"], row["fact_key"])
                for row in answer["per_coordinate"]}
        self.assertEqual(keys, {("lab-order", "current_table")})
        self.assertEqual(answer["per_coordinate"][0]["truth_status"],
                         truth.VERIFIED)
        self.assertEqual(answer["per_coordinate"][0]["retrieval_status"],
                         retrieval.OK)

    def test_per_coordinate_covers_every_resolved_coordinate(self):
        """D-4 驗收 8:漏掉任一已解析座標必須被抓到。`per_coordinate`
        與 `resolved` 的座標集合必須相等 —— 一邊有、一邊沒有就是資訊損失。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "migration_state",
            "pending", status=truth.CANDIDATE, confidence=0.3)
        answer = self.ask("目前 lab-order 是什麼狀況?")
        resolved_keys = {(r["entity_key"], r["fact_key"])
                         for r in answer["resolved"]}
        coord_keys = {(r["entity_key"], r["fact_key"])
                      for r in answer["per_coordinate"]}
        self.assertEqual(coord_keys, resolved_keys)

    def test_current_named_fact_key_absent_on_named_entity_is_not_ok(self):
        """查詢指名的 fact_key 在被指名的 entity 底下不存在(它屬於別的
        entity)—— 不得退回「那就把這個 entity 全部 fact 都給你」,那會拿一個
        沒被問的座標當答案。空候選 → 上層落到模糊檢索,狀態不得是 OK。"""
        truth.record_fact(
            self.store, self.repo, "database", "audit", "retention_days",
            "90", status=truth.VERIFIED, confidence=0.9)
        answer = self.ask("目前 lab-order 的 retention_days 是什麼?")
        self.assertNotEqual(answer["retrieval_status"], retrieval.OK)
        self.assertNotIn("current_truth", answer)

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


class HydrationIsByPrimaryKeyTest(MemoryCase):
    """檢索命中之後,答案的**內容**必須用主鍵撈回來,不能靠「最近 N 筆」列表。

    WHY 的答案不是「有一筆 decision」,而是它的 `reason` / `alternatives` /
    `tradeoff`;HOW 的答案是 `steps` / `verification`。原本的實作是

        row = next((d for d in store.decisions(limit=200)
                    if d["decision_id"] == hit["item_id"]), None)

    也就是拿一個**已知的主鍵**去掃「最近 200 筆」。檢索索引沒有那個視窗,
    所以命中一筆更舊的 decision 時 `row` 是 None —— 而 `_why()` 仍然把它算成
    decision、仍然回 `OK`。系統於是聲稱「我有可靠的 WHY 答案」,卻沒有附上
    構成那個答案的欄位。這比查不到更糟:查不到會回 NO_RELIABLE_MATCH,
    呼叫端知道要去問人。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.embedder = embedding.Embedder()
        commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.snapshot = identity.workspace_snapshot(self.repo)

    def ask(self, text):
        return query.execute(self.store, self.repo, text, self.workspace,
                             self.snapshot, self.embedder)

    def bury(self, kind, count=260):
        """在目標之後再塞 count 筆**更新**的同類紀錄,把目標推出視窗外。"""
        for n in range(count):
            stamp = "2026-07-{0:02d}T{1:02d}:00:00Z".format(
                1 + n // 24, n % 24)
            if kind == "decision":
                self.store.upsert_decision({
                    "key": "unrelated-{0}".format(n),
                    "title": "無關決策 {0}".format(n),
                    "decision": "無關內容 {0}".format(n),
                    "reason": "與查詢無關", "status": "ACCEPTED",
                    "recorded_at": stamp})
            else:
                self.store.upsert_skill({
                    "key": "unrelated-{0}".format(n),
                    "title": "無關流程 {0}".format(n),
                    "steps": ["無關步驟"], "status": "VERIFIED",
                    "verification": "無關驗證", "recorded_at": stamp})

    def test_why_hydrates_a_decision_outside_the_recent_window(self):
        decision_id = self.store.upsert_decision({
            "key": "share-lab-order", "title": "PGS/ECS 共用 lab order 表",
            "decision": "合併成 lab_order", "reason": "兩邊欄位重疊九成",
            "alternatives": "各自維護", "tradeoff": "查詢要多一個 join",
            "status": "ACCEPTED", "recorded_at": "2026-01-01T00:00:00Z"})
        self.bury("decision")
        self.embedder.reindex(self.store)
        answer = self.ask("為什麼要共用 lab order?")
        hit = next((r for r in answer["results"]
                    if r["item_id"] == decision_id), None)
        self.assertIsNotNone(hit, "檢索本身要能命中它,否則這個測試沒在測東西")
        self.assertEqual(hit.get("reason"), "兩邊欄位重疊九成")
        self.assertEqual(hit.get("alternatives"), "各自維護")
        self.assertEqual(hit.get("tradeoff"), "查詢要多一個 join")

    def test_why_ok_always_carries_the_reason_fields(self):
        """回 OK 就必須附上構成答案的欄位 —— 不得只回一個 decision 的殼。"""
        self.store.upsert_decision({
            "key": "share-lab-order", "title": "PGS/ECS 共用 lab order 表",
            "decision": "合併成 lab_order", "reason": "兩邊欄位重疊九成",
            "status": "ACCEPTED", "recorded_at": "2026-01-01T00:00:00Z"})
        self.bury("decision")
        self.embedder.reindex(self.store)
        answer = self.ask("為什麼要共用 lab order?")
        if answer["retrieval_status"] != retrieval.OK:
            self.skipTest("這一案只約束 OK 的情況")
        for hit in answer["results"]:
            if hit["item_type"] != "decision":
                continue
            self.assertIn("reason", hit,
                          "回 OK 的 decision 一定要帶 reason")

    def test_why_evidence_comes_from_the_hit_row(self):
        self.store.upsert_decision({
            "key": "share-lab-order", "title": "PGS/ECS 共用 lab order 表",
            "decision": "合併成 lab_order", "reason": "兩邊欄位重疊九成",
            "status": "ACCEPTED", "recorded_at": "2026-01-01T00:00:00Z",
            "evidence": [{"type": "adr", "ref": "docs/adr/0007.md"}]})
        self.bury("decision")
        self.embedder.reindex(self.store)
        answer = self.ask("為什麼要共用 lab order?")
        self.assertIn({"type": "adr", "ref": "docs/adr/0007.md"},
                      answer["evidence"])

    def test_how_hydrates_a_skill_outside_the_recent_window(self):
        skill_id = self.store.upsert_skill({
            "key": "deploy-worker", "title": "部署 worker 的流程",
            "steps": ["跑 migration", "重啟 worker"], "status": "VERIFIED",
            "verification": "打 /health 回 200",
            "recorded_at": "2026-01-01T00:00:00Z"})
        self.bury("skill")
        self.embedder.reindex(self.store)
        answer = self.ask("怎麼部署 worker?")
        hit = next((r for r in answer["results"]
                    if r["item_id"] == skill_id), None)
        self.assertIsNotNone(hit, "檢索本身要能命中它,否則這個測試沒在測東西")
        self.assertEqual(hit.get("steps"), ["跑 migration", "重啟 worker"])
        self.assertEqual(hit.get("verification"), "打 /health 回 200")
        self.assertEqual(hit.get("skill_status"), "VERIFIED")

    def test_row_lookup_by_primary_key_does_not_depend_on_recency(self):
        """store 層面的直接證據:主鍵查詢不受「最近 N 筆」影響。"""
        decision_id = self.store.upsert_decision({
            "key": "old", "title": "很舊的決策", "decision": "x",
            "reason": "r", "status": "ACCEPTED",
            "recorded_at": "2026-01-01T00:00:00Z"})
        skill_id = self.store.upsert_skill({
            "key": "old", "title": "很舊的流程", "steps": ["s"],
            "status": "VERIFIED", "recorded_at": "2026-01-01T00:00:00Z"})
        self.bury("decision")
        self.bury("skill")
        self.assertIsNone(
            next((d for d in self.store.decisions(limit=200)
                  if d["decision_id"] == decision_id), None),
            "前置條件:目標必須真的在視窗外,否則這組測試沒在測東西")
        self.assertEqual(
            self.store.decision_row(decision_id)["reason"], "r")
        self.assertEqual(
            self.store.skill_row(skill_id)["title"], "很舊的流程")
        self.assertIsNone(self.store.decision_row("no-such-id"))
        self.assertIsNone(self.store.skill_row("no-such-id"))
