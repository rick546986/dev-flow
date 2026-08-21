"""D-1: runtime SQLite 是 per-worktree,兩個 worktree 不得共用可變檔。

owner 裁決 D-1(選項 a):記憶內容的共用走 `.dev-flow/` + git,不靠同一份
SQLite。GPT 1704 的驗收契約要求**真的 `git worktree add`**,mock 兩個
workspace_id 卻仍寫進同一檔不算。
"""
import os
import shutil

from memtools import MemoryCase, commit_all, git, write
from agentmem import durable, identity, session, setup, store as store_mod, sync


class WorktreeStoreIsolationTest(MemoryCase):
    """一條情境一次證明 D1-A~D1-H 的可觀察不變量。"""

    def _commit_identity(self):
        report = setup.run(self.repo, name="demo")
        commit_all(self.repo, "seed durable identity")
        return report

    def _add_linked_worktree(self, name, branch):
        git(self.repo, "branch", branch)
        path = os.path.join(self.work, name)
        git(self.repo, "worktree", "add", "-q", path, branch)
        self.assertTrue(os.path.isdir(path))
        self.assertTrue(os.path.isfile(os.path.join(path, ".dev-flow",
                                                    "project.yaml")))
        return path

    def _open(self, project_id, root):
        opened = store_mod.open_for_root(project_id, root)
        self.addCleanup(opened.close)
        return opened

    def test_two_real_worktrees_are_physically_isolated(self):
        report_a = self._commit_identity()
        project_id = report_a["project_id"]
        wt_b = self._add_linked_worktree("repo-wt-b", "other")
        report_b = setup.run(wt_b)

        self.assertEqual(report_b["project_id"], project_id)
        self.assertNotEqual(os.path.realpath(report_a["local_db"]),
                            os.path.realpath(report_b["local_db"]))
        self.assertIn("/worktrees/",
                      report_a["local_db"].replace("\\", "/"))
        self.assertTrue(os.path.isfile(report_a["local_db"]))
        self.assertTrue(os.path.isfile(report_b["local_db"]))
        self.assertNotEqual(report_a["workspace_id"], report_b["workspace_id"])

        store_a = self._open(project_id, self.repo)
        store_b = self._open(project_id, wt_b)
        sid_a = session.start(store_a, self.repo, mode=session.IMPLEMENTATION,
                              topic="A only")["session_id"]
        sid_b = session.start(store_b, wt_b, mode=session.IMPLEMENTATION,
                              topic="B only")["session_id"]
        store_a.add_candidate(sid_a, "knowledge",
                              {"kind": "domain", "key": "only-a",
                               "title": "A candidate"},
                              "current_code")
        store_b.add_candidate(sid_b, "knowledge",
                              {"kind": "domain", "key": "only-b",
                               "title": "B candidate"},
                              "current_code")

        a_sessions = {row["session_id"] for row in store_a.sessions()}
        b_sessions = {row["session_id"] for row in store_b.sessions()}
        self.assertEqual(a_sessions, {sid_a})
        self.assertEqual(b_sessions, {sid_b})
        self.assertEqual(
            [row["payload"]["key"] for row in store_a.candidates(sid_a)],
            ["only-a"])
        self.assertEqual(
            [row["payload"]["key"] for row in store_b.candidates(sid_b)],
            ["only-b"])

        session.checkpoint(store_a, self.repo, sid_a)
        self.assertEqual(store_b.session(sid_b)["status"], session.OPEN)
        self.assertIsNone(store_b.session(sid_a))
        self.assertEqual(len(store_b.candidates(sid_b)), 1)

        session.end(store_a, self.repo, sid_a)
        self.assertEqual(store_a.session(sid_a)["status"], session.CLOSED)
        self.assertEqual(store_b.session(sid_b)["status"], session.OPEN)

        setup.run(self.repo)
        store_b_after = self._open(project_id, wt_b)
        self.assertEqual(store_b_after.session(sid_b)["status"], session.OPEN)
        self.assertEqual(len(store_b_after.candidates(sid_b)), 1)

        before_switch = report_a["local_db"]
        git(self.repo, "checkout", "-q", "-b", "switched-in-a")
        report_switched = setup.run(self.repo, rebuild=False)
        self.assertEqual(os.path.realpath(report_switched["local_db"]),
                         os.path.realpath(before_switch))
        self.assertEqual(report_switched["project_id"], project_id)

        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "only-in-a",
            "title": "A 剛寫進 durable 的知識",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-21T00:00:00Z"})
        setup.run(self.repo)
        store_a_after = self._open(project_id, self.repo)
        self.assertTrue(any(row["key"] == "only-in-a"
                            for row in store_a_after.knowledge()))
        store_b_before_git = self._open(project_id, wt_b)
        self.assertFalse(any(row["key"] == "only-in-a"
                             for row in store_b_before_git.knowledge()))
        setup.run(wt_b)
        store_b_after_rebuild = self._open(project_id, wt_b)
        self.assertFalse(
            any(row["key"] == "only-in-a"
                for row in store_b_after_rebuild.knowledge()),
            "B 不得只因為 A 寫了本機 SQLite 就看到 A 的 durable 知識")

        commit_all(self.repo, "A durable knowledge")
        git(wt_b, "merge", "-q", "--no-edit", "switched-in-a")
        setup.run(wt_b)
        store_b_synced = self._open(project_id, wt_b)
        self.assertTrue(any(row["key"] == "only-in-a"
                            for row in store_b_synced.knowledge()))

        db_a = report_switched["local_db"]
        db_b = report_b["local_db"]
        os.remove(db_a)
        for extra in (db_a + "-wal", db_a + "-shm"):
            if os.path.isfile(extra):
                os.remove(extra)
        self.assertTrue(os.path.isfile(db_b))
        setup.run(self.repo)
        self.assertTrue(os.path.isfile(db_b))
        store_b_after_a_rebuild = self._open(project_id, wt_b)
        self.assertEqual(store_b_after_a_rebuild.session(sid_b)["status"],
                         session.OPEN)

    def test_legacy_shared_db_is_not_copied_into_worktrees(self):
        project_id = self.project()["project_id"]
        legacy = store_mod.legacy_shared_db_path(project_id)
        leaked = store_mod.Store.open(project_id, path=legacy)
        sid = leaked.start_session("should stay in archive",
                                   mode=session.IMPLEMENTATION)
        leaked.add_candidate(sid, "knowledge",
                             {"kind": "domain", "key": "legacy-open",
                              "title": "old shared session"},
                             "current_code")
        leaked.close()
        self.assertTrue(os.path.isfile(legacy))

        report = setup.run(self.repo, name="demo")
        self.assertNotEqual(os.path.realpath(report["local_db"]),
                            os.path.realpath(legacy))
        self.assertFalse(os.path.isfile(legacy),
                         "舊共用 DB 必須被 archive,不能繼續當 runtime 入口")
        fresh = self._open(project_id, self.repo)
        self.assertEqual(fresh.sessions(), [])
        archived = store_mod.legacy_shared_db_path(project_id) + ".legacy-shared"
        self.assertTrue(os.path.isfile(archived))
        self.assertEqual(
            [row["payload"].get("key") for row in fresh.candidates()], [])

    def test_store_open_without_worktree_key_fails_loud(self):
        project_id = self.project()["project_id"]
        with self.assertRaises(ValueError):
            store_mod.Store.open(project_id)

    def test_agentmem_home_still_owns_the_layout(self):
        other = os.path.join(self.work, "alt-home")
        self._set_env("AGENTMEM_HOME", other)
        report = setup.run(self.repo, name="demo")
        # 兩邊都要 realpath:macOS 的 TMPDIR 走 /var/folders,而 /var 是
        # /private/var 的 symlink,只正規化其中一邊會永遠不相等(Linux CI 上
        # /tmp 不是 symlink 所以照樣綠,這種紅只在 macOS 出現)。
        self.assertTrue(os.path.realpath(report["local_db"]).startswith(
            os.path.realpath(other)))
        self.assertIn(os.path.join("projects", report["project_id"],
                                   "worktrees"),
                      report["local_db"].replace("\\", "/"))


class TwoWorktreeRebuildIsolationTest(MemoryCase):
    """D1-D:不同 checkout 的 durable 狀態,後重建的不得蓋掉先重建的。"""

    def test_rebuild_b_does_not_repopulate_a(self):
        setup.run(self.repo, name="demo")
        write(self.repo, "src/a.ts", "export const a = 1\n")
        durable.write_state(self.repo, "database", "alpha", [{
            "fact_key": "current_table", "value": "alpha_table",
            "status": "VERIFIED", "confidence": 0.99,
            "recorded_at": "2026-08-21T00:00:00Z",
            "dependencies": ["src/a.ts"],
            "fingerprints": {"src/a.ts": "sha256:aaa"}}])
        commit_all(self.repo, "A durable state")

        git(self.repo, "branch", "b-side")
        wt_b = os.path.join(self.work, "repo-wt-b-state")
        git(self.repo, "worktree", "add", "-q", wt_b, "b-side")
        write(wt_b, "src/b.ts", "export const b = 1\n")
        durable.write_state(wt_b, "database", "beta", [{
            "fact_key": "current_table", "value": "beta_table",
            "status": "VERIFIED", "confidence": 0.99,
            "recorded_at": "2026-08-21T00:00:00Z",
            "dependencies": ["src/b.ts"],
            "fingerprints": {"src/b.ts": "sha256:bbb"}}])
        # B 的 durable 只存在於 B 的工作樹,尚未進 A 的 checkout
        setup.run(self.repo)
        setup.run(wt_b)

        project_id = identity.read_project(self.repo)["project_id"]
        store_a = store_mod.open_for_root(project_id, self.repo)
        self.addCleanup(store_a.close)
        keys_a = {(row["entity_key"], row["fact_key"], row["value"])
                  for row in store_a.facts()}
        self.assertIn(("alpha", "current_table", "alpha_table"), keys_a)
        self.assertNotIn(("beta", "current_table", "beta_table"), keys_a)

        setup.run(wt_b)
        store_a_again = store_mod.open_for_root(project_id, self.repo)
        self.addCleanup(store_a_again.close)
        keys_a_again = {(row["entity_key"], row["fact_key"], row["value"])
                        for row in store_a_again.facts()}
        self.assertEqual(keys_a, keys_a_again)
