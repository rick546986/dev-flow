"""rebuild(durable → local)與 consolidate(local → durable)(§5/§13/§17/§29)。"""
import os
import shutil

from memtools import MemoryCase
from agentmem import durable, identity, sync


class RebuildTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        durable.write_state(self.repo, "database", "memory-store", [{
            "fact_key": "backend", "value": "sqlite-wasm", "status": "VERIFIED",
            "confidence": 0.99, "recorded_at": "2026-08-20T00:00:00Z",
            "dependencies": ["src/services/db.ts"],
            "fingerprints": {"src/services/db.ts": "sha256:aaa"}}])
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "registration",
            "title": "registration = customer-level 送檢紀錄",
            "body": "一個客戶在 submission 內的送檢紀錄",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})
        durable.write_decision(self.repo, {
            "key": "memory-backend", "title": "用 sqlite-wasm",
            "status": "ACCEPTED", "decided_at": "2026-08-20",
            "decision": "選 sqlite-wasm", "reason": "跨平台"})
        durable.write_skill(self.repo, {"key": "deploy", "title": "部署流程",
                                        "steps": ["build"],
                                        "recorded_at": "2026-08-20T00:00:00Z"})
        durable.append_events(self.repo, "ses_a", [{
            "kind": "schema_change", "title": "改名 pgs_intake → lab_order",
            "occurred_at": "2026-08-20T01:00:00Z", "branch": "main",
            "paths": ["migrations/001.sql"]}])

    def test_rebuild_from_durable_populates_everything(self):
        store = self.store_for(self.project_id)
        counts = sync.rebuild_local(self.repo, store)
        self.assertEqual(counts["facts"], 1)
        self.assertEqual(counts["knowledge"], 1)
        self.assertEqual(counts["decisions"], 1)
        self.assertEqual(counts["skills"], 1)
        self.assertEqual(counts["events"], 1)
        self.assertGreaterEqual(store.item_count(), 5)

    def test_rebuild_is_idempotent(self):
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        first = (len(store.facts()), len(store.knowledge()), store.item_count())
        sync.rebuild_local(self.repo, store)
        self.assertEqual(
            (len(store.facts()), len(store.knowledge()), store.item_count()),
            first)

    def test_deleting_local_db_loses_nothing_durable(self):
        """§13 的核心測試:砍掉 local DB → rebuild → 記憶內容一致。"""
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        before = {
            "facts": [(f["entity_key"], f["fact_key"], f["value"], f["status"])
                      for f in store.facts()],
            "knowledge": [(k["kind"], k["key"], k["status"])
                          for k in store.knowledge()],
        }
        store.close()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        after = {
            "facts": [(f["entity_key"], f["fact_key"], f["value"], f["status"])
                      for f in fresh.facts()],
            "knowledge": [(k["kind"], k["key"], k["status"])
                          for k in fresh.knowledge()],
        }
        self.assertEqual(before, after)

    def test_rebuild_preserves_local_only_and_legacy_rows(self):
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        legacy = store.add_event("important_discovery", "legacy 觀察",
                                 signal="high", legacy=True)
        local_session = store.start_session("local 對話")
        store.add_turn(local_session, "user", "只住 local 的一句話")
        sync.rebuild_local(self.repo, store)
        self.assertIn(legacy, {e["event_id"] for e in store.events(limit=50)})
        self.assertEqual(len(store.turns(local_session)), 1)

    def test_clone_to_another_path_yields_same_memory(self):
        """Mac/Windows/Linux 路徑不同、project_id 相同、記憶內容相同(§13)。"""
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        clone = self.new_repo("D-dev-project")
        shutil.copytree(durable.root(self.repo), durable.root(clone))
        cloned_id = identity.ensure_project(clone)[0]["project_id"]
        self.assertEqual(cloned_id, self.project_id)
        counts = sync.rebuild_local(clone, store)
        self.assertEqual(counts["facts"], 1)
        self.assertEqual(counts["knowledge"], 1)


class ConsolidateTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("PGS 真實送檢流程")

    def test_only_confirmed_candidates_are_written(self):
        pending = self.store.add_candidate(
            self.session, "domain",
            {"key": "specimen", "title": "specimen = 單一 embryo"},
            "domain_expert")
        confirmed = self.store.add_candidate(
            self.session, "domain",
            {"key": "registration", "title": "registration = customer-level"},
            "domain_expert")
        self.store.set_candidate_status(confirmed, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertEqual(result["promoted"], 1)
        keys = [k["key"] for k in durable.iter_knowledge(self.repo)]
        self.assertEqual(keys, ["registration"])
        self.assertEqual(
            self.store.candidates(self.session, statuses=("PENDING",))[0][
                "candidate_id"], pending)

    def test_sensitive_candidate_is_kept_local_with_reason(self):
        candidate = self.store.add_candidate(
            self.session, "domain",
            {"key": "creds", "title": "連線設定",
             "body": 'DB_PASSWORD = "hunter2000"'}, "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(len(result["rejected"]), 1)
        self.assertFalse(os.path.isdir(
            os.path.join(durable.root(self.repo), "knowledge")))
        row = self.store.candidates(self.session, statuses=("LOCAL_ONLY",))[0]
        self.assertIn("敏感", row["note"])

    def test_raw_transcript_never_reaches_durable(self):
        self.store.add_turn(self.session, "user",
                            "我今天想聊聊 PGS 在真實世界的送檢流程")
        self.store.add_turn(self.session, "agent", "submission 是院所批次嗎?")
        candidate = self.store.add_candidate(
            self.session, "domain",
            {"key": "submission", "title": "submission = 院所批次送檢"},
            "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)
        blob = []
        for dirpath, _dirs, files in os.walk(durable.root(self.repo)):
            for name in files:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    blob.append(f.read())
        joined = "\n".join(blob)
        self.assertIn("submission = 院所批次送檢", joined)
        self.assertNotIn("我今天想聊聊", joined)
        self.assertNotIn("submission 是院所批次嗎?", joined)

    def test_fact_candidate_promotes_whole_entity_file(self):
        candidate = self.store.add_candidate(
            self.session, "fact",
            {"entity_type": "database", "entity_key": "memory-store",
             "fact_key": "backend", "value": "sqlite-wasm", "status": "VERIFIED",
             "title": "backend = sqlite-wasm",
             "dependencies": ["src/services/db.ts"]}, "code_inference")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertTrue(result["written"])
        data = durable.read_state(self.repo, "database", "memory-store")
        self.assertEqual(data["facts"][0]["value"], "sqlite-wasm")

    def test_event_candidate_lands_in_session_scoped_file(self):
        candidate = self.store.add_candidate(
            self.session, "event",
            {"kind": "table_rename", "title": "pgs_intake → lab_order",
             "occurred_at": "2026-08-20T05:00:00Z",
             "paths": ["migrations/001.sql"]}, "code_inference")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)
        events = list(durable.iter_events(self.repo))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "table_rename")
        self.assertIn(self.session, os.listdir(
            os.path.join(durable.root(self.repo), "events", "2026", "08"))[0])

    def test_unknown_target_kind_is_refused_not_guessed(self):
        candidate = self.store.add_candidate(
            self.session, "nonsense", {"key": "x", "title": "y"}, "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(result["rejected"][0]["target_kind"], "nonsense")


class FactConsolidationTest(MemoryCase):
    """fact 候選只宣告依賴、沒帶指紋時,固化當下要對當前 checkout 現算。

    這條是實際踩到的缺陷:少了現算,fact 會以「VERIFIED 但沒有任何指紋」落地,
    查詢時只能降級成 CANDIDATE(無從驗證)—— 宣告了依賴卻等於沒宣告,
    而且 durable 檔看起來完全正常。
    """

    def setUp(self):
        super().setUp()
        from memtools import commit_all, write
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/services/db.ts", "export const t = 'lab_order'\n")
        commit_all(self.repo, "seed src")
        self.session = self.store.start_session("記錄現況事實")

    def test_fingerprints_are_computed_at_consolidation(self):
        import json
        from agentmem import identity, truth
        candidate = self.store.add_candidate(
            self.session, "fact",
            {"entity_type": "database", "entity_key": "lab-order",
             "fact_key": "current_table", "value": "lab_order",
             "title": "current_table = lab_order", "status": "VERIFIED",
             "confidence": 0.99, "dependencies": ["src/services/db.ts"]},
            "current_code")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)

        row = self.store.facts(entity_type="database", entity_key="lab-order",
                               fact_key="current_table", limit=1)[0]
        fingerprints = json.loads(row["fingerprints_json"])
        self.assertEqual(sorted(fingerprints), ["src/services/db.ts"])
        self.assertTrue(fingerprints["src/services/db.ts"].startswith("sha256:"))

        # 有指紋才拿得到 fast path(沒有指紋會被降級成 CANDIDATE)
        workspace = identity.workspace_key(self.project_id, self.repo)
        resolved = truth.resolve_current(
            self.store, self.repo, "database", "lab-order", "current_table",
            workspace, identity.workspace_snapshot(self.repo))
        self.assertEqual(resolved["status"], truth.VERIFIED)
        self.assertTrue(resolved["fast_path"])

        # durable 檔也帶著指紋(換一台機器 rebuild 回來才驗得住)
        data = durable.read_state(self.repo, "database", "lab-order")
        self.assertIn("fingerprints", data["facts"][0])

    def test_explicit_fingerprints_are_not_overwritten(self):
        import json
        candidate = self.store.add_candidate(
            self.session, "fact",
            {"entity_type": "database", "entity_key": "lab-order",
             "fact_key": "current_table", "value": "lab_order",
             "title": "t", "status": "VERIFIED",
             "dependencies": ["src/services/db.ts"],
             "fingerprints": {"src/services/db.ts": "sha256:supplied"}},
            "current_code")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)
        row = self.store.facts(fact_key="current_table", limit=1)[0]
        self.assertEqual(json.loads(row["fingerprints_json"]),
                         {"src/services/db.ts": "sha256:supplied"})
