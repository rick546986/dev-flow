"""LVP Current Truth:fast path / 失效 / 重驗 / supersede(§8/§9/§26/§31)。"""
import json

from memtools import MemoryCase, commit_all, write
from agentmem import identity, truth


class LvpTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/services/db.ts",
              "export const backend = 'sqlite-wasm'\n")
        write(self.repo, "package.json", '{"name":"demo"}\n')
        self.head = commit_all(self.repo, "add db")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.fact_id = truth.record_fact(
            self.store, self.repo, "database", "memory-store", "backend",
            "sqlite-wasm",
            dependencies=["src/services/db.ts", "package.json"],
            source_type="current_code", source_ref="src/services/db.ts",
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)

    def snapshot(self):
        return identity.workspace_snapshot(self.repo)

    def resolve(self):
        return truth.resolve_current(
            self.store, self.repo, "database", "memory-store", "backend",
            self.workspace, self.snapshot())

    # ── fast path ───────────────────────────────────────────────────────────
    def test_verified_with_unchanged_dependencies_is_fast_path(self):
        result = self.resolve()
        self.assertEqual(result["status"], truth.VERIFIED)
        self.assertTrue(result["fast_path"])
        self.assertFalse(result["needs_inspect"])
        self.assertEqual(result["value"], "sqlite-wasm")

    def test_unknown_fact_is_a_legal_answer(self):
        result = truth.resolve_current(
            self.store, self.repo, "database", "memory-store", "nope",
            self.workspace, self.snapshot())
        self.assertEqual(result["status"], truth.UNKNOWN)
        self.assertIsNone(result["value"])
        self.assertTrue(result["needs_inspect"])

    def test_verified_without_fingerprints_does_not_claim_fast_path(self):
        fact_id = self.store.upsert_fact({
            "entity_type": "worker", "entity_key": "main", "fact_key": "port",
            "value": "38888", "status": truth.VERIFIED, "confidence": 0.9})
        result = truth.resolve_current(self.store, self.repo, "worker", "main",
                                       "port", self.workspace, self.snapshot())
        self.assertFalse(result["fast_path"])
        self.assertEqual(result["status"], truth.CANDIDATE)
        self.assertEqual(result["fact_id"], fact_id)

    # ── invalidation ────────────────────────────────────────────────────────
    def test_modifying_dependency_creates_local_stale_overlay(self):
        write(self.repo, "src/services/db.ts",
              "export const backend = 'indexeddb'\n")
        result = self.resolve()
        self.assertEqual(result["status"], truth.STALE)
        self.assertTrue(result["needs_inspect"])
        # durable/shared 側不動:facts 表的 status 仍是 VERIFIED
        self.assertEqual(self.store.fact_row(self.fact_id)["status"],
                         truth.VERIFIED)
        overlay = self.store.overlay(self.fact_id, self.workspace)
        self.assertEqual(overlay["status"], truth.STALE)

    def test_uncommitted_dependency_change_goes_stale(self):
        """§26:工作樹有未提交改動就不能拿 main 的 verified 當當前答案。

        誠實說明本案實際咬住的是**指紋**那條(未提交的改動讓內容與驗證時不同)。
        「dirty 但指紋相符」與「dirty 且無指紋可比」兩種分工由
        test_workspace_status.DirtyVersusFingerprintTest 分開釘。"""
        write(self.repo, "package.json", '{"name":"demo","version":"2"}\n')
        result = self.resolve()
        self.assertEqual(result["status"], truth.STALE)

    def test_deleted_dependency_counts_as_change(self):
        import os
        os.remove(self.repo + "/package.json")
        self.assertEqual(self.resolve()["status"], truth.STALE)

    def test_overlay_is_per_workspace(self):
        write(self.repo, "src/services/db.ts", "changed\n")
        self.resolve()
        other = identity.workspace_key(self.project_id,
                                       self.new_repo("other-checkout"))
        self.assertIsNone(self.store.overlay(self.fact_id, other))

    def test_invalidate_for_changes_marks_only_dependent_facts(self):
        unrelated = truth.record_fact(
            self.store, self.repo, "worker", "main", "port", "38888",
            dependencies=["package.json"], status=truth.VERIFIED)
        touched = truth.invalidate_for_changes(
            self.store, self.workspace, ["src/services/db.ts"])
        self.assertIn(self.fact_id, touched)
        self.assertNotIn(unrelated, touched)

    def test_invalidate_from_snapshot_catches_committed_content_change(self):
        write(self.repo, "src/services/db.ts", "export const backend = 'x'\n")
        commit_all(self.repo, "change backend")
        snapshot = self.snapshot()
        self.assertEqual(snapshot["dirty_files"], [])
        touched = truth.invalidate_from_snapshot(
            self.store, self.repo, self.workspace, snapshot)
        self.assertIn(self.fact_id, touched)

    # ── recovery ────────────────────────────────────────────────────────────
    def test_reverify_same_value_returns_to_verified(self):
        write(self.repo, "src/services/db.ts",
              "export const backend = 'sqlite-wasm' // comment\n")
        self.assertEqual(self.resolve()["status"], truth.STALE)
        outcome = truth.reverify(self.store, self.repo, self.fact_id,
                                 self.workspace, "sqlite-wasm")
        self.assertEqual(outcome["outcome"], "reconfirmed")
        result = self.resolve()
        self.assertEqual(result["status"], truth.VERIFIED)
        self.assertTrue(result["fast_path"])
        self.assertEqual(self.store.fact_row(self.fact_id)["verification_count"], 2)

    def test_reverify_changed_value_supersedes_old_and_verifies_new(self):
        write(self.repo, "src/services/db.ts",
              "export const backend = 'indexeddb'\n")
        self.resolve()
        outcome = truth.reverify(self.store, self.repo, self.fact_id,
                                 self.workspace, "indexeddb")
        self.assertEqual(outcome["outcome"], "superseded")
        old = self.store.fact_row(self.fact_id)
        self.assertEqual(old["status"], truth.SUPERSEDED)
        self.assertEqual(old["superseded_by"], outcome["new_fact_id"])
        result = self.resolve()
        self.assertEqual(result["status"], truth.VERIFIED)
        self.assertEqual(result["value"], "indexeddb")
        self.assertTrue(result["fast_path"])

    def test_reverify_undetermined_keeps_stale_and_writes_no_value(self):
        write(self.repo, "src/services/db.ts", "??\n")
        self.resolve()
        outcome = truth.reverify(self.store, self.repo, self.fact_id,
                                 self.workspace, None)
        self.assertEqual(outcome["outcome"], "undetermined")
        self.assertEqual(self.store.fact_row(self.fact_id)["value"],
                         "sqlite-wasm")
        self.assertEqual(
            self.store.fact_row(self.fact_id)["contradiction_count"], 1)
        self.assertEqual(self.resolve()["status"], truth.STALE)

    def test_conflict_status_never_silently_picks_a_side(self):
        self.store.upsert_fact({
            "fact_id": self.fact_id, "entity_type": "database",
            "entity_key": "memory-store", "fact_key": "backend",
            "value": "sqlite-wasm", "status": truth.CONFLICT,
            "confidence": 0.5, "recorded_at": "2026-08-20T00:00:00Z"})
        result = self.resolve()
        self.assertEqual(result["status"], truth.CONFLICT)
        self.assertTrue(result["needs_inspect"])


class BranchTest(MemoryCase):
    """§26/§31:main 的 verified 不得被當成 feature branch 的當前真相。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/services/db.ts",
              "export const backend = 'sqlite-wasm'\n")
        self.head = commit_all(self.repo, "main baseline")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.fact_id = truth.record_fact(
            self.store, self.repo, "database", "memory-store", "backend",
            "sqlite-wasm", dependencies=["src/services/db.ts"],
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)

    def test_feature_branch_change_makes_current_truth_stale(self):
        from memtools import git
        snapshot = identity.workspace_snapshot(self.repo)
        self.store.register_workspace(self.workspace, snapshot)
        self.assertEqual(
            truth.resolve_current(self.store, self.repo, "database",
                                  "memory-store", "backend", self.workspace,
                                  snapshot)["status"], truth.VERIFIED)
        git(self.repo, "checkout", "-q", "-b", "feature/swap-backend")
        write(self.repo, "src/services/db.ts",
              "export const backend = 'indexeddb'\n")
        commit_all(self.repo, "swap backend on feature branch")
        branch_snapshot = identity.workspace_snapshot(self.repo)
        self.assertEqual(branch_snapshot["branch"], "feature/swap-backend")
        result = truth.resolve_current(self.store, self.repo, "database",
                                       "memory-store", "backend",
                                       self.workspace, branch_snapshot)
        self.assertEqual(result["status"], truth.STALE)
        self.assertTrue(result["needs_inspect"])
        # main 的答案還在 durable 側,只是不能當「當前 workspace 的答案」
        self.assertEqual(self.store.fact_row(self.fact_id)["status"],
                         truth.VERIFIED)


class AuthorityTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.store = self.store_for(self.project()["project_id"])

    def test_no_global_code_beats_everything_ranking(self):
        # implementation truth:程式碼贏過人的說法
        self.assertTrue(truth.can_override("implementation", "current_code",
                                           "user_claim"))
        # domain truth:人贏過程式碼推論
        self.assertFalse(truth.can_override("domain", "code_inference",
                                            "domain_expert"))
        self.assertTrue(truth.can_override("domain", "domain_expert",
                                           "code_inference"))
        # intent:產品/架構決策贏過程式碼推論
        self.assertFalse(truth.can_override("intent", "code_inference",
                                            "product_decision"))
        # decision:ADR 最高
        self.assertTrue(truth.can_override("decision", "adr",
                                           "explicit_discussion"))

    def test_unknown_authority_ranks_lowest(self):
        self.assertEqual(truth.authority_rank("domain", "made_up"), 0)
        self.assertFalse(truth.can_override("domain", "made_up",
                                            "agent_hypothesis"))

    def test_equal_authority_does_not_override(self):
        self.assertFalse(truth.can_override("domain", "domain_expert",
                                            "domain_expert"))

    def test_unknown_memory_type_fails_loud(self):
        with self.assertRaises(ValueError):
            truth.authority_rank("nonsense", "domain_expert")


class DomainTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/services/db.ts", "x\n")
        commit_all(self.repo, "seed src")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.knowledge_id, _action = truth.assert_knowledge(
            self.store, "domain", "registration",
            "registration 永遠代表一個 customer,不是 embryo",
            body="一個客戶在 submission 內的送檢紀錄",
            authority="domain_expert", status="CONFIRMED", confidence=0.95)

    def row(self):
        return self.store.knowledge_row(self.knowledge_id)

    def test_domain_truth_is_not_invalidated_by_unrelated_code_change(self):
        """§10 的核心:改一支不相關的 TypeScript 不能讓業務規則變 STALE。"""
        write(self.repo, "src/services/db.ts", "changed\n")
        truth.invalidate_from_snapshot(
            self.store, self.repo, self.workspace,
            identity.workspace_snapshot(self.repo))
        self.assertEqual(self.row()["status"], "CONFIRMED")
        self.assertEqual(self.store.overlays(self.workspace), [])

    def test_code_supporting_domain_raises_confidence_only(self):
        status, action = truth.reconcile_with_code(
            self.store, "domain", "registration",
            "src/models/registration.ts:12", "current_code", supports=True)
        self.assertEqual(action, "supported")
        self.assertEqual(status, "CONFIRMED")
        self.assertGreater(self.row()["confidence"], 0.95)

    def test_code_contradicting_domain_creates_conflict_without_overwriting(self):
        before = self.row()
        status, action = truth.reconcile_with_code(
            self.store, "domain", "registration",
            "src/models/registration.ts 看起來是 specimen-level",
            "current_code", supports=False)
        self.assertEqual(action, "conflicted")
        self.assertEqual(status, truth.CONFLICT)
        after = self.row()
        self.assertEqual(after["body"], before["body"])
        self.assertEqual(after["title"], before["title"])
        self.assertEqual(after["authority"], "domain_expert")
        conflicts = json.loads(after["conflicts_json"])
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["stance"], "contradicts")

    def test_lower_authority_cannot_overwrite_confirmed_domain_truth(self):
        knowledge_id, action = truth.assert_knowledge(
            self.store, "domain", "registration",
            "registration 是 embryo-level", authority="code_inference",
            status="CONFIRMED")
        self.assertEqual(action, "refused")
        self.assertEqual(knowledge_id, self.knowledge_id)
        self.assertIn("customer", self.row()["title"])

    def test_user_correction_supersedes_earlier_knowledge(self):
        _knowledge_id, action = truth.assert_knowledge(
            self.store, "domain", "registration",
            "registration 代表一個 customer 的一次參與(修正)",
            authority="domain_expert", status="CONFIRMED", confidence=0.97)
        self.assertEqual(action, "updated")
        self.assertIn("修正", self.row()["title"])

    def test_open_conflicts_are_reportable(self):
        truth.reconcile_with_code(self.store, "domain", "registration",
                                  "看起來是 specimen-level", "current_code",
                                  supports=False)
        conflicts = truth.open_conflicts(self.store)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["key"], "registration")


class IntentTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.store = self.store_for(self.project()["project_id"])

    def test_intent_is_marked_planned_not_implemented(self):
        knowledge_id, _ = truth.assert_knowledge(
            self.store, "intent", "shared-lab-order",
            "未來 PGS/ECS 共用 lab order 架構",
            authority="architecture_decision", status="CONFIRMED",
            implemented=False)
        row = self.store.knowledge_row(knowledge_id)
        self.assertEqual(row["implemented"], 0)
        self.assertEqual(row["kind"], "intent")

    def test_intent_never_answers_as_current_implementation(self):
        """planned intent 與 implementation truth 是兩張表,不會互相冒充。"""
        truth.assert_knowledge(
            self.store, "intent", "shared-lab-order",
            "未來共用 lab order", authority="architecture_decision",
            implemented=False)
        current = truth.resolve_current(
            self.store, self.repo, "architecture", "lab-order", "shared",
            identity.workspace_key(self.project()["project_id"], self.repo))
        self.assertEqual(current["status"], truth.UNKNOWN)
