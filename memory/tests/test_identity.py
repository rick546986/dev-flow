"""project identity:path-independent、不依賴 GitHub、重跑不換 ID(§3/§31)。"""
import os
import shutil

from memtools import MemoryCase, git, read_file, write
from agentmem import identity, ids, yamlmini


class ProjectIdTest(MemoryCase):
    def test_project_id_is_ulid_and_created_once(self):
        data, created = identity.ensure_project(self.repo, name="demo")
        self.assertTrue(created)
        self.assertTrue(ids.is_valid_id("project", data["project_id"]))
        again, created_again = identity.ensure_project(self.repo)
        self.assertFalse(created_again)
        self.assertEqual(data["project_id"], again["project_id"])

    def test_same_project_yaml_across_mac_windows_linux_paths(self):
        """三種平台路徑 clone 同一份 .dev-flow → 同一個 project_id。

        真正的判準不是「路徑長得像 Mac/Windows」,而是「project_id 來自 Git 裡的
        project.yaml,不來自路徑」—— 所以複製 .dev-flow 到任意路徑都必須同 ID。
        """
        origin = identity.ensure_project(self.repo, name="demo")[0]
        for name in ("Users-rick-dev-project", "D-dev-project", "home-rick-project"):
            clone = self.new_repo(name)
            shutil.copytree(identity.durable_root(self.repo),
                            identity.durable_root(clone))
            data, created = identity.ensure_project(clone)
            self.assertFalse(created, name)
            self.assertEqual(origin["project_id"], data["project_id"], name)

    def test_project_id_independent_of_git_remote(self):
        data = identity.ensure_project(self.repo, name="demo")[0]
        git(self.repo, "remote", "add", "origin",
            "https://example.invalid/other/name.git")
        after = identity.ensure_project(self.repo)[0]
        self.assertEqual(data["project_id"], after["project_id"])
        # remote 只能當 provenance:第一次建立時記下,但改 remote 不影響 identity
        self.assertNotIn("origin_provenance", after)

    def test_remote_recorded_as_provenance_only(self):
        git(self.repo, "remote", "add", "origin", "git@example.invalid:a/b.git")
        data = identity.ensure_project(self.repo, name="demo")[0]
        self.assertEqual(data["origin_provenance"], "git@example.invalid:a/b.git")
        self.assertTrue(ids.is_valid_id("project", data["project_id"]))
        self.assertNotIn("b", data["project_id"])

    def test_no_absolute_path_in_project_yaml(self):
        identity.ensure_project(self.repo, name="demo")
        text = read_file(identity.project_file(self.repo))
        self.assertNotIn(self.repo, text)
        self.assertNotIn(os.sep + "tmp", text)

    def test_corrupt_project_yaml_fails_loud(self):
        identity.ensure_project(self.repo, name="demo")
        write(self.repo, os.path.join(identity.memory_dir_name(), "project.yaml"),
              "project_id: not-a-ulid\nschema_version: 1\n")
        with self.assertRaises(identity.IdentityError):
            identity.read_project(self.repo)

    def test_missing_project_without_create_fails_loud(self):
        with self.assertRaises(identity.IdentityError):
            identity.ensure_project(self.repo, create=False)

    def test_memory_dir_override(self):
        self._set_env(identity.MEMORY_DIR_ENV, ".brain")
        identity.ensure_project(self.repo, name="demo")
        self.assertTrue(os.path.isfile(os.path.join(self.repo, ".brain",
                                                    "project.yaml")))

    def test_project_yaml_is_deterministic(self):
        data = identity.ensure_project(self.repo, name="demo")[0]
        first = read_file(identity.project_file(self.repo))
        identity.write_project(self.repo, data)
        second = read_file(identity.project_file(self.repo))
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)
        parsed = yamlmini.load(first)
        self.assertEqual(parsed["project_id"], data["project_id"])


class WorkspaceTest(MemoryCase):
    def test_snapshot_reports_branch_head_and_dirty(self):
        snapshot = identity.workspace_snapshot(self.repo)
        self.assertEqual(snapshot["local_path"], os.path.realpath(self.repo))
        self.assertTrue(snapshot["head_sha"])
        self.assertEqual(snapshot["worktree"], "main")
        write(self.repo, "src/db.ts", "export const backend = 'x'\n")
        dirty = identity.workspace_snapshot(self.repo)
        self.assertIn("src/db.ts", dirty["dirty_files"])

    def test_workspace_key_changes_with_path_but_project_id_does_not(self):
        data = identity.ensure_project(self.repo, name="demo")[0]
        other = self.new_repo("second-checkout")
        shutil.copytree(identity.durable_root(self.repo),
                        identity.durable_root(other))
        same = identity.ensure_project(other)[0]
        self.assertEqual(data["project_id"], same["project_id"])
        self.assertNotEqual(
            identity.workspace_key(data["project_id"], self.repo),
            identity.workspace_key(data["project_id"], other))
