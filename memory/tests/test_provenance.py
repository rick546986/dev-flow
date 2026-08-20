"""P1-5:origin_provenance 不得把 credential / 本機路徑寫進 durable memory。

`.dev-flow/project.yaml` 進 Git、會被 push。`git config remote.origin.url` 的
原始值可能長成:

    https://user:ghp_xxxx@github.com/org/repo.git      ← 憑證
    file:///Users/rick/dev/project                      ← 本機絕對路徑
    /Users/rick/dev/mirror.git                          ← 本機絕對路徑
    \\\\server\\share\\repo.git                            ← UNC
    https://github.com/org/repo.git?token=abc#frag      ← query/fragment

這些一旦進 commit,砍檔案不等於砍歷史。provenance 是**選填**欄位 ——
判不安全就不要寫,不要 fail setup。
"""
import os

from memtools import MemoryCase, git, read_file
from agentmem import identity


class SanitizeTest(MemoryCase):
    SAFE = (
        ("https://github.com/org/repo.git", "https://github.com/org/repo.git"),
        ("https://github.com/org/repo", "https://github.com/org/repo"),
        ("http://gitlab.example.com/g/s/p.git",
         "http://gitlab.example.com/g/s/p.git"),
        # SSH scp-like:user 部分要丟掉
        ("git@github.com:org/repo.git", "github.com/org/repo.git"),
        ("git@gitlab.example.com:group/sub/proj.git",
         "gitlab.example.com/group/sub/proj.git"),
        # ssh:// 形式同樣去 userinfo
        ("ssh://git@github.com/org/repo.git", "ssh://github.com/org/repo.git"),
        ("ssh://github.com:2222/org/repo.git",
         "ssh://github.com:2222/org/repo.git"),
    )

    UNSAFE = (
        "https://user:ghp_abcdefghijklmnopqrstuvwxyz0123@github.com/org/repo.git",
        "https://ghp_abcdefghijklmnopqrstuvwxyz0123@github.com/org/repo.git",
        "https://rick:hunter2000@example.com/repo.git",
        "file:///Users/rick/dev/project",
        "file://C:/dev/project",
        "/Users/rick/dev/mirror.git",
        "/home/rick/mirror.git",
        "~/dev/mirror.git",
        "C:\\dev\\mirror.git",
        "D:/dev/mirror.git",
        "\\\\server\\share\\repo.git",
        "//server/share/repo.git",
        "../relative/mirror.git",
        "git@github.com:org/repo.git extra junk",
        # query / fragment:整條拒絕,不是剝掉後保留 —— 見 identity.py 的理由
        "https://github.com/org/repo.git?token=abc",
        "https://github.com/org/repo.git#frag",
        "ssh://git@github.com/org/repo.git?x=1",
        # 非 git 的 userinfo 一律拒絕(即使沒有密碼)
        "ssh://myuser@git.corp.example.com/org/repo.git",
        "myuser@github.com:org/repo.git",
        "",
        "   ",
    )

    def test_safe_remotes_are_normalized(self):
        for raw, expected in self.SAFE:
            self.assertEqual(identity.sanitize_origin_provenance(raw), expected,
                             raw)

    def test_unsafe_remotes_yield_none(self):
        for raw in self.UNSAFE:
            self.assertIsNone(identity.sanitize_origin_provenance(raw), raw)

    def test_none_input_is_none(self):
        self.assertIsNone(identity.sanitize_origin_provenance(None))

    def test_sanitized_output_never_contains_credential_or_local_path(self):
        from agentmem import paths, signal
        for raw, _expected in self.SAFE:
            value = identity.sanitize_origin_provenance(raw)
            self.assertEqual(signal.scan_sensitive(value), [], raw)
            self.assertEqual(paths.scan_absolute_paths(value), [], raw)
            self.assertNotIn("@", value, raw)


class ProjectFileTest(MemoryCase):
    def project_text(self):
        return read_file(identity.project_file(self.repo))

    def test_credential_remote_never_reaches_project_yaml(self):
        git(self.repo, "remote", "add", "origin",
            "https://rick:ghp_abcdefghijklmnopqrstuvwxyz0123@github.com/org/repo.git")
        identity.ensure_project(self.repo, name="demo")
        text = self.project_text()
        self.assertNotIn("ghp_", text)
        self.assertNotIn("rick:", text)
        self.assertNotIn("origin_provenance", text)

    def test_file_url_remote_never_reaches_project_yaml(self):
        git(self.repo, "remote", "add", "origin", "file:///Users/rick/dev/mirror")
        identity.ensure_project(self.repo, name="demo")
        text = self.project_text()
        self.assertNotIn("/Users/rick", text)
        self.assertNotIn("origin_provenance", text)

    def test_local_path_remote_never_reaches_project_yaml(self):
        other = self.new_repo("mirror-source")
        git(self.repo, "remote", "add", "origin", other)
        identity.ensure_project(self.repo, name="demo")
        text = self.project_text()
        self.assertNotIn(other, text)
        self.assertNotIn("origin_provenance", text)

    def test_safe_remote_is_recorded_sanitized(self):
        git(self.repo, "remote", "add", "origin",
            "git@github.com:org/repo.git")
        data = identity.ensure_project(self.repo, name="demo")[0]
        self.assertEqual(data["origin_provenance"], "github.com/org/repo.git")
        self.assertIn("github.com/org/repo.git", self.project_text())
        self.assertNotIn("git@", self.project_text())

    def test_missing_remote_omits_field(self):
        identity.ensure_project(self.repo, name="demo")
        self.assertNotIn("origin_provenance", self.project_text())

    def test_setup_still_succeeds_with_unsafe_remote(self):
        """provenance 判不安全時只是不寫,**不得**讓 setup 失敗。"""
        from agentmem import ids, setup
        git(self.repo, "remote", "add", "origin",
            "https://u:p@example.com/r.git")
        report = setup.run(self.repo, name="demo")
        self.assertTrue(ids.is_valid_id("project", report["project_id"]))

    def test_durable_tree_has_no_credentials_after_setup(self):
        from agentmem import signal
        git(self.repo, "remote", "add", "origin",
            "https://u:ghp_abcdefghijklmnopqrstuvwxyz0123@example.com/r.git")
        identity.ensure_project(self.repo, name="demo")
        for dirpath, _dirs, files in os.walk(identity.durable_root(self.repo)):
            for name in files:
                text = read_file(os.path.join(dirpath, name))
                self.assertEqual(signal.scan_sensitive(text), [],
                                 os.path.join(dirpath, name))
