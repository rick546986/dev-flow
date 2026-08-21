"""P0-4:retrieval status contract —— STALE / CONFLICT 絕不得回 OK。

上層 agent 很容易只看 `retrieval_status`。舊實作在 CURRENT 查詢裡,只要
`resolved` 非空就回 OK,再把「其實是 STALE」塞進 `uncertainty` 文字裡 ——
那等於把一個**狀態**降級成一句**註解**,而註解不會被程式讀。

四態(嚴重度由高到低):

    CONFLICT            > NEEDS_VERIFICATION > OK
    NO_RELIABLE_MATCH   完全沒有可信命中(不是「比較差的 OK」)
"""
from memtools import MemoryCase, commit_all, write
from agentmem import embedding, identity, query, retrieval, truth


class StatusContractTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.embedder = embedding.Embedder()
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        write(self.repo, "src/worker.ts", "export const port = 38888\n")
        self.head = commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)

    def fact(self, entity_key, fact_key, value, deps, status=truth.VERIFIED):
        return truth.record_fact(
            self.store, self.repo, "database", entity_key, fact_key, value,
            dependencies=deps, source_commit=self.head, status=status,
            confidence=0.99)

    def ask(self, text):
        return query.execute(self.store, self.repo, text, self.workspace,
                             identity.workspace_snapshot(self.repo),
                             self.embedder)

    # ── A:verified + 指紋有效 → OK ──────────────────────────────────────────
    def test_verified_current_fact_is_ok(self):
        self.fact("lab-order", "current_table", "lab_order", ["src/db.ts"])
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["current_truth"]["value"], "lab_order")

    # ── B:依賴改動 → NEEDS_VERIFICATION ─────────────────────────────────────
    def test_modified_dependency_needs_verification(self):
        self.fact("lab-order", "current_table", "lab_order", ["src/db.ts"])
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], query.NEEDS_VERIFICATION)
        self.assertNotEqual(answer["retrieval_status"], retrieval.OK)

    def test_committed_dependency_change_needs_verification(self):
        self.fact("lab-order", "current_table", "lab_order", ["src/db.ts"])
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        commit_all(self.repo, "change table")
        self.assertEqual(
            self.ask("目前 lab-order 的 current_table 是什麼?")["retrieval_status"],
            query.NEEDS_VERIFICATION)

    def test_deleted_dependency_needs_verification(self):
        import os
        self.fact("lab-order", "current_table", "lab_order", ["src/db.ts"])
        os.remove(self.repo + "/src/db.ts")
        self.assertEqual(
            self.ask("目前 lab-order 的 current_table 是什麼?")["retrieval_status"],
            query.NEEDS_VERIFICATION)

    # ── C:CONFLICT ─────────────────────────────────────────────────────────
    def test_conflicting_fact_is_conflict_not_ok(self):
        fact_id = self.fact("lab-order", "current_table", "lab_order",
                            ["src/db.ts"])
        row = self.store.fact_row(fact_id)
        self.store.upsert_fact({
            "fact_id": fact_id, "entity_type": "database",
            "entity_key": "lab-order", "fact_key": "current_table",
            "value": row["value"], "status": truth.CONFLICT,
            "confidence": 0.5, "recorded_at": row["recorded_at"],
            "dependencies": ["src/db.ts"]})
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], query.CONFLICT)

    def test_domain_conflict_is_conflict_not_ok(self):
        truth.assert_knowledge(self.store, "domain", "registration",
                               "registration = customer-level",
                               authority="domain_expert", status="CONFIRMED")
        truth.reconcile_with_code(self.store, "domain", "registration",
                                  "src/models/x.ts 看起來是 specimen-level",
                                  "current_code", supports=False)
        self.embedder.reindex(self.store)
        answer = self.ask("registration 是什麼意思?")
        self.assertEqual(answer["retrieval_status"], query.CONFLICT)

    # ── D:NO_RELIABLE_MATCH ────────────────────────────────────────────────
    def test_no_memory_is_no_reliable_match(self):
        self.assertEqual(self.ask("咖啡機壞了要找誰修?")["retrieval_status"],
                         retrieval.NO_RELIABLE_MATCH)

    def test_unknown_fact_is_no_reliable_match(self):
        self.assertEqual(
            self.ask("目前 lab-order 的 current_table 是什麼?")["retrieval_status"],
            retrieval.NO_RELIABLE_MATCH)

    # ── E:STALE + 有 lexical 命中 仍不得 OK ────────────────────────────────
    def test_stale_with_lexical_evidence_still_needs_verification(self):
        """STALE 之後即使檢索撈到相關文字,沒 reverify 就不能宣稱 OK。"""
        self.fact("lab-order", "current_table", "lab_order", ["src/db.ts"])
        self.store.add_event(
            "table_rename", "lab-order current_table 相關討論",
            "lab_order 這張表最近被討論過", occurred_at="2026-08-01T00:00:00Z",
            signal="high")
        self.embedder.reindex(self.store)
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], query.NEEDS_VERIFICATION)
        self.assertTrue(answer["results"] or answer["resolved"],
                        "證據仍要回傳,只是狀態不得是 OK")

    # ── 重新驗證後回 OK ─────────────────────────────────────────────────────
    def test_reverify_restores_ok(self):
        fact_id = self.fact("lab-order", "current_table", "lab_order",
                            ["src/db.ts"])
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        self.assertEqual(
            self.ask("目前 lab-order 的 current_table 是什麼?")["retrieval_status"],
            query.NEEDS_VERIFICATION)
        truth.reverify(self.store, self.repo, fact_id, self.workspace, "orders")
        answer = self.ask("目前 lab-order 的 current_table 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(answer["current_truth"]["value"], "orders")

    # ── F:多 fact 混合 → 取最嚴重 ──────────────────────────────────────────
    def test_mixed_verified_and_stale_is_needs_verification(self):
        self.fact("shared", "current_table", "lab_order", ["src/db.ts"])
        self.fact("shared", "port", "38888", ["src/worker.ts"])
        answer = self.ask("目前 shared 的 current_table 與 port 是什麼?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        write(self.repo, "src/worker.ts", "export const port = 39999\n")
        answer = self.ask("目前 shared 的 current_table 與 port 是什麼?")
        self.assertEqual(answer["retrieval_status"], query.NEEDS_VERIFICATION,
                         "只要有一筆 STALE,整體就不能是 OK")

    def test_conflict_outranks_needs_verification(self):
        conflicted = self.fact("shared", "current_table", "lab_order",
                               ["src/db.ts"])
        self.fact("shared", "port", "38888", ["src/worker.ts"])
        row = self.store.fact_row(conflicted)
        self.store.upsert_fact({
            "fact_id": conflicted, "entity_type": "database",
            "entity_key": "shared", "fact_key": "current_table",
            "value": row["value"], "status": truth.CONFLICT, "confidence": 0.5,
            "recorded_at": row["recorded_at"], "dependencies": ["src/db.ts"]})
        write(self.repo, "src/worker.ts", "export const port = 39999\n")
        answer = self.ask("目前 shared 的 current_table 與 port 是什麼?")
        self.assertEqual(answer["retrieval_status"], query.CONFLICT)

    # ── 契約本身 ────────────────────────────────────────────────────────────
    def test_status_severity_ordering_is_defined(self):
        self.assertGreater(query.severity(query.CONFLICT),
                           query.severity(query.NEEDS_VERIFICATION))
        self.assertGreater(query.severity(query.NEEDS_VERIFICATION),
                           query.severity(retrieval.OK))

    def test_every_status_is_in_the_declared_set(self):
        self.assertEqual(
            set(query.RETRIEVAL_STATUSES),
            {retrieval.OK, query.NEEDS_VERIFICATION, query.CONFLICT,
             retrieval.NO_RELIABLE_MATCH})

    def test_non_current_intents_keep_ok_semantics(self):
        """只有 CURRENT 這一層有驗證語意;DOMAIN/HOW 等維持 OK/NO_RELIABLE_MATCH。"""
        self.store.upsert_skill({"key": "deploy", "title": "部署流程",
                                 "steps": ["build"], "status": "VERIFIED"})
        self.embedder.reindex(self.store)
        answer = self.ask("怎麼部署?")
        self.assertIn(answer["retrieval_status"],
                      (retrieval.OK, retrieval.NO_RELIABLE_MATCH))


class CliStatusTest(MemoryCase):
    """CLI 輸出必須把狀態印出來,不能只印 OK 再把 STALE 藏在提示文字裡。"""

    def setUp(self):
        super().setUp()
        import json
        import os
        import subprocess
        import sys
        self.json = json
        self.subprocess = subprocess
        self.sys = sys
        self.os = os
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        commit_all(self.repo, "seed")

    def run_cli(self, *args):
        out = self.subprocess.run(
            [self.sys.executable, self.os.path.join("memory", "dev-memory.py"),
             "--path", self.repo, *args],
            capture_output=True, text=True, env=dict(self.os.environ))
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def test_cli_prints_needs_verification(self):
        self.run_cli("setup", "--name", "demo")
        self.run_cli("fact", "--entity-type", "database", "--entity-key",
                     "lab-order", "--fact-key", "current_table", "--value",
                     "lab_order", "--dep", "src/db.ts", "--verified")
        ok_text = self.run_cli("ask", "目前 lab-order 的 current_table 是什麼?")
        self.assertIn("OK", ok_text)
        self.assertNotIn("NEEDS_VERIFICATION", ok_text)
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        stale_text = self.run_cli("ask", "目前 lab-order 的 current_table 是什麼?")
        self.assertIn("NEEDS_VERIFICATION", stale_text)

    def test_cli_json_status_matches_rendered_status(self):
        self.run_cli("setup", "--name", "demo")
        self.run_cli("fact", "--entity-type", "database", "--entity-key",
                     "lab-order", "--fact-key", "current_table", "--value",
                     "lab_order", "--dep", "src/db.ts", "--verified")
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        payload = self.json.loads(
            self.run_cli("ask", "目前 lab-order 的 current_table 是什麼?", "--json"))
        self.assertEqual(payload["retrieval_status"], "NEEDS_VERIFICATION")
