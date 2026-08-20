"""dev-setup 的 memory 階段、doctor、legacy 遷移(§12/§13/§29)。"""
import os
import shutil

from memtools import MemoryCase, commit_all, git, read_file, write
from agentmem import durable, identity, legacy, setup, store as store_mod


class SetupTest(MemoryCase):
    def test_first_run_creates_identity_and_local_db(self):
        report = setup.run(self.repo, name="demo")
        self.assertTrue(report["project_created"])
        self.assertTrue(os.path.isfile(identity.project_file(self.repo)))
        self.assertTrue(os.path.isfile(report["local_db"]))
        self.assertEqual(report["workspace"]["local_path"],
                         os.path.realpath(self.repo))

    def test_rerun_is_idempotent_and_keeps_project_id(self):
        first = setup.run(self.repo, name="demo")
        second = setup.run(self.repo)
        third = setup.run(self.repo)
        self.assertEqual(first["project_id"], second["project_id"])
        self.assertEqual(second["project_id"], third["project_id"])
        self.assertFalse(second["project_created"])
        store = self.store_for(first["project_id"])
        self.assertEqual(len(store.workspaces()), 1)

    def test_setup_does_not_create_a_second_init_entrypoint(self):
        """§12:唯一 setup 入口是 dev-setup —— CLI 不得提供 init 子命令。"""
        import subprocess
        import sys
        out = subprocess.run(
            [sys.executable, os.path.join("memory", "dev-memory.py"), "--help"],
            capture_output=True, text=True)
        self.assertNotIn("init", out.stdout.split("{", 1)[-1].split("}", 1)[0])

    def test_setup_reports_capabilities_and_inventory(self):
        report = setup.run(self.repo, name="demo")
        self.assertIn("fts5", report["capabilities"])
        self.assertEqual(report["durable_inventory"]["facts"], 0)
        self.assertEqual(report["durable_dir"], ".dev-flow")

    def test_setup_outside_git_fails_loud(self):
        outside = os.path.join(self.work, "not-a-repo")
        os.makedirs(outside)
        with self.assertRaises(setup.SetupError):
            setup.run(outside)

    def test_clone_on_another_machine_rebuilds_same_memory(self):
        """§13 全流程:git clone → dev-setup → 同 project_id → 記憶一致。"""
        setup.run(self.repo, name="demo")
        store = self.store_for(identity.read_project(self.repo)["project_id"])
        durable.write_state(self.repo, "database", "lab-order", [{
            "fact_key": "current_table", "value": "lab_order",
            "status": "VERIFIED", "confidence": 0.99,
            "recorded_at": "2026-08-20T00:00:00Z",
            "dependencies": ["src/services/db.ts"],
            "fingerprints": {"src/services/db.ts": "sha256:aaa"}}])
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "registration",
            "title": "registration = customer-level",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})
        commit_all(self.repo, "add durable memory")
        store.close()

        clone = os.path.join(self.work, "windows-side")
        git(self.work, "clone", "-q", self.repo, clone)
        # 另一台機器:local DB 從零開始
        shutil.rmtree(os.path.join(self.home, "projects"), ignore_errors=True)
        report = setup.run(clone)
        self.assertFalse(report["project_created"])
        self.assertEqual(report["project_id"],
                         identity.read_project(self.repo)["project_id"])
        self.assertEqual(report["rebuilt"]["facts"], 1)
        self.assertEqual(report["rebuilt"]["knowledge"], 1)
        cloned = self.store_for(report["project_id"])
        self.assertEqual(cloned.facts()[0]["value"], "lab_order")
        self.assertEqual(cloned.knowledge()[0]["key"], "registration")
        # workspace 是新的一筆,project 仍是同一個
        self.assertEqual(len(cloned.workspaces()), 1)
        self.assertEqual(cloned.workspaces()[0]["local_path"],
                         os.path.realpath(clone))

    def test_deleting_local_db_then_setup_rebuilds(self):
        setup.run(self.repo, name="demo")
        project_id = identity.read_project(self.repo)["project_id"]
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "k", "title": "t",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})
        setup.run(self.repo)
        shutil.rmtree(os.path.join(self.home, "projects", project_id))
        report = setup.run(self.repo)
        self.assertEqual(report["rebuilt"]["knowledge"], 1)

    def test_stale_scan_runs_after_rebuild(self):
        write(self.repo, "src/services/db.ts", "export const t = 'lab_order'\n")
        commit_all(self.repo, "seed src")
        setup.run(self.repo, name="demo")
        durable.write_state(self.repo, "database", "lab-order", [{
            "fact_key": "current_table", "value": "lab_order",
            "status": "VERIFIED", "confidence": 0.99,
            "recorded_at": "2026-08-20T00:00:00Z",
            "dependencies": ["src/services/db.ts"],
            "fingerprints": {"src/services/db.ts": "sha256:stale"}}])
        report = setup.run(self.repo)
        self.assertEqual(report["stale_after_rebuild"], 1)


class DoctorTest(MemoryCase):
    def test_doctor_fails_before_setup(self):
        report = setup.doctor(self.repo)
        self.assertEqual(report["verdict"], "FAIL")
        self.assertTrue(any(f["check"] == "project-identity"
                            for f in report["findings"]))

    def test_doctor_passes_after_setup(self):
        setup.run(self.repo, name="demo")
        report = setup.doctor(self.repo)
        self.assertIn(report["verdict"], ("PASS", "WARN"))
        checks = {f["check"] for f in report["findings"]}
        self.assertIn("durable-relative-paths", checks)
        self.assertIn("embedding-version", checks)

    def test_doctor_flags_absolute_path_leak(self):
        setup.run(self.repo, name="demo")
        write(self.repo, os.path.join(".dev-flow", "knowledge", "domain",
                                      "leak.yaml"),
              'schema_version: 1\nkind: domain\nkey: leak\n'
              'title: "見 /Users/rick/proj/db.ts"\nauthority: domain_expert\n'
              'status: CONFIRMED\n')
        report = setup.doctor(self.repo)
        self.assertEqual(report["verdict"], "FAIL")
        leak = [f for f in report["findings"]
                if f["check"] == "durable-relative-paths"][0]
        self.assertEqual(leak["level"], "error")

    def test_doctor_outside_git_fails_closed(self):
        outside = os.path.join(self.work, "nope")
        os.makedirs(outside)
        self.assertEqual(setup.doctor(outside)["verdict"], "FAIL")


class LegacyTest(MemoryCase):
    CONTEXT = """# demo — CONTEXT(詞彙表 / Ubiquitous Language)

> 用途:團隊 + AI 共用的業務語言。

## Language

**Contract(合約)**:客戶與本公司簽署的服務協議,一筆 = contracts 表一列。
_Avoid_:Agreement、協議書

**Registration(送檢紀錄)**:一個客戶在 submission 內的送檢紀錄。
_Avoid_:報名

**<Term(中文)>**:<定義含邊界>
_Avoid_:<同義詞>
"""

    HISTORY = """# 改版歷史索引

> 只增不改。

## 2026-07-31 · methodology-corrections
- 做了什麼:拿掉對外部 harness 的依賴
- 為什麼:方法論有逃生門
- 落在哪:README、_templates/

## 2026-08-13 · single-plugin-merge · v3.0.0
- 做了什麼:併成單一 plugin
- 為什麼:兩個 plugin 要各裝一次
- 落在哪:.claude-plugin/
"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "CONTEXT.md", self.CONTEXT)
        write(self.repo, os.path.join("docs", "dev", "HISTORY.md"), self.HISTORY)

    def test_dry_run_writes_nothing(self):
        report = legacy.migrate(self.repo, self.store, apply_changes=False)
        self.assertEqual(report["context_md"]["terms"], 2)
        self.assertEqual(report["history_md"]["entries"], 2)
        self.assertEqual(self.store.knowledge(), [])
        self.assertEqual(self.store.events(), [])

    def test_placeholder_terms_are_skipped(self):
        report = legacy.migrate(self.repo, self.store)
        self.assertEqual(sorted(report["context_md"]["keys"]),
                         ["Contract", "Registration"])

    def test_apply_imports_glossary_as_unverified_candidates(self):
        legacy.migrate(self.repo, self.store, apply_changes=True)
        rows = self.store.knowledge(kind="domain", limit=10)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["status"], legacy.LEGACY_STATUS)
            self.assertEqual(row["authority"], legacy.LEGACY_AUTHORITY)
            self.assertEqual(row["legacy"], 1)
            self.assertEqual(row["durable"], 0)

    def test_avoid_list_is_preserved(self):
        legacy.migrate(self.repo, self.store, apply_changes=True)
        row = self.store.knowledge(kind="domain", key="Contract", limit=1)[0]
        self.assertIn("Agreement", row["body"])

    def test_promote_writes_durable_but_still_candidate(self):
        report = legacy.migrate(self.repo, self.store, apply_changes=True,
                                promote=True)
        self.assertEqual(len(report["written"]), 2)
        records = list(durable.iter_knowledge(self.repo))
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertEqual(record["status"], legacy.LEGACY_STATUS)
            self.assertEqual(record["evidence"][0]["ref"], "CONTEXT.md")

    def test_history_is_indexed_locally_not_duplicated_into_durable(self):
        legacy.migrate(self.repo, self.store, apply_changes=True)
        events = self.store.events(limit=10)
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertEqual(event["legacy"], 1)
            self.assertEqual(event["durable"], 0)
            self.assertEqual(event["source_ref"], "docs/dev/HISTORY.md")
        self.assertEqual(list(durable.iter_events(self.repo)), [])

    def test_history_entries_are_queryable_after_import(self):
        legacy.migrate(self.repo, self.store, apply_changes=True)
        from agentmem import embedding, query
        embedding.Embedder().reindex(self.store)
        answer = query.execute(
            self.store, self.repo, "之前 single-plugin-merge 做了什麼?",
            identity.workspace_key(self.project_id, self.repo),
            identity.workspace_snapshot(self.repo), embedding.Embedder())
        titles = " ".join(hit["title"] for hit in answer["results"])
        self.assertIn("single-plugin-merge", titles)

    def test_legacy_import_does_not_destroy_existing_rows(self):
        keep = self.store.add_event("schema_change", "既有事件", signal="high")
        self.store.upsert_knowledge({
            "kind": "domain", "key": "existing", "title": "既有知識",
            "authority": "domain_expert", "status": "CONFIRMED"})
        legacy.migrate(self.repo, self.store, apply_changes=True)
        self.assertIn(keep, {e["event_id"] for e in self.store.events(limit=20)})
        self.assertIn("existing",
                      {k["key"] for k in self.store.knowledge(limit=20)})

    def test_missing_legacy_files_report_none(self):
        os.remove(os.path.join(self.repo, "CONTEXT.md"))
        os.remove(os.path.join(self.repo, "docs", "dev", "HISTORY.md"))
        report = legacy.migrate(self.repo, self.store)
        self.assertIsNone(report["context_md"])
        self.assertIsNone(report["history_md"])

    def test_frozen_legacy_sample_parses(self):
        """對凍結樣本跑一次 —— 本 repo 已不散發 CONTEXT.md 模板,但採用專案的
        既有檔案還在,parser 必須繼續讀得懂它(樣本住 memory/fixtures/legacy/)。"""
        terms, unparsed = legacy.parse_context_md(
            read_file(os.path.join(os.getcwd(), "memory", "fixtures", "legacy",
                                   "CONTEXT.md")))
        self.assertEqual([t["key"] for t in terms], ["Contract", "Expiring"])
        self.assertEqual(unparsed, [])

    def test_real_history_index_parses(self):
        """對本 repo 真正的 docs/dev/HISTORY.md 跑一次(它留在原地給人看)。"""
        entries = legacy.parse_history_md(
            read_file(os.path.join(os.getcwd(), "docs", "dev", "HISTORY.md")))
        self.assertGreater(len(entries), 10)
        self.assertTrue(all(entry["date"] for entry in entries))
        self.assertTrue(all("做了什麼" in entry["fields"] for entry in entries))
