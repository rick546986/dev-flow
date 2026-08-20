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

    def test_remote_recorded_as_sanitized_provenance_only(self):
        """provenance 一律先過 sanitize:`git@` 的 user 部分不留(P1-5)。"""
        git(self.repo, "remote", "add", "origin", "git@example.invalid:a/b.git")
        data = identity.ensure_project(self.repo, name="demo")[0]
        self.assertEqual(data["origin_provenance"], "example.invalid/a/b.git")
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


class RemoteIsOffMachineTest(MemoryCase):
    """「這個 remote 在另一台機器上嗎」—— `durable-check` 唯一的問句需要它。

    一個 git remote 不必然在別台機器上。`/Volumes/backup/mirror.git`、
    `file:///…`、`ssh://git@localhost/…` 都通得過 `ls-remote`,而硬碟壞掉時
    它們跟工作樹一起消失。判不出來一律 False:**判不出來不得當成證據**。
    """

    OFF_MACHINE = (
        "https://github.com/org/repo.git",
        "http://git.internal.example/org/repo.git",
        "ssh://git@github.com/org/repo.git",
        "ssh://git@git.example.com:2222/org/repo.git",
        "git://git.example.com/repo.git",
        "git@github.com:org/repo.git",
        "github.com:org/repo.git",
        "https://user:token@github.com/org/repo.git",
    )

    LOCAL_OR_UNKNOWN = (
        "/Volumes/backup/mirror.git",
        "/tmp/origin.git",
        "~/mirror.git",
        "file:///Users/rick/mirror.git",
        "file://localhost/Users/rick/mirror.git",
        "../sibling.git",
        "./mirror.git",
        "sibling.git",
        "C:\\repos\\mirror.git",
        "\\\\server\\share\\repo.git",
        "ssh://git@localhost/repo.git",
        "ssh://git@localhost.localdomain/repo.git",
        "https://127.0.0.1/repo.git",
        "https://127.1.2.3:8080/repo.git",
        "http://[::1]/repo.git",
        "https://0.0.0.0/repo.git",
        "ssh://git@internalhost/repo.git",
        "ext::sh -c 'cat /tmp/x'",
        "",
        "   ",
        None,
        123,
    )

    def test_network_remotes_are_off_machine(self):
        for url in self.OFF_MACHINE:
            self.assertTrue(identity.remote_is_offmachine(url), url)

    def test_local_or_undecidable_remotes_are_not_off_machine(self):
        for url in self.LOCAL_OR_UNKNOWN:
            self.assertFalse(identity.remote_is_offmachine(url), url)

    def test_it_never_returns_a_truthy_non_bool(self):
        """回傳值會被當成「有沒有證據」的判定,不得是一個 re.Match。"""
        for url in self.OFF_MACHINE + ("/tmp/x.git",):
            self.assertIsInstance(identity.remote_is_offmachine(url), bool)


class HostEndpointIsOffMachineTest(MemoryCase):
    """`remote_is_offmachine` 判的是 URL **形狀**。一個具名的非 loopback 主機
    仍然可能解析回這台機器 —— `remote.example.test` 被 `/etc/hosts` 或 DNS
    重映到 `127.0.0.1`,或映到這台機器自己的一個介面位址,`ls-remote` 一樣會
    回報正確的 SHA。這裡測的是解析後的位址,不是主機名字面。
    """

    def test_loopback_address_is_not_off_machine(self):
        for ip in ("127.0.0.1", "127.5.6.7", "::1"):
            self.assertFalse(identity.ip_is_offmachine(ip, local_ips=frozenset()),
                             ip)

    def test_link_local_address_is_not_off_machine(self):
        for ip in ("169.254.1.1", "fe80::1"):
            self.assertFalse(identity.ip_is_offmachine(ip, local_ips=frozenset()),
                             ip)

    def test_unspecified_address_is_not_off_machine(self):
        for ip in ("0.0.0.0", "::"):
            self.assertFalse(identity.ip_is_offmachine(ip, local_ips=frozenset()),
                             ip)

    def test_address_matching_a_local_interface_is_not_off_machine(self):
        """主機名字面不是 loopback,但解析後等於這台機器自己的介面位址 ——
        `ssh://git@remote.example.test/…` 映到本機 LAN 位址就是這個情境。"""
        self.assertFalse(
            identity.ip_is_offmachine("192.168.1.50",
                                      local_ips=frozenset({"192.168.1.50"})))

    def test_unrelated_address_is_off_machine(self):
        """不是 loopback / link-local / unspecified,也不等於本機任何介面位址
        —— 這才是真正「別台機器」的證據。"""
        self.assertTrue(
            identity.ip_is_offmachine("192.0.2.10",
                                      local_ips=frozenset({"192.168.1.50"})))

    def test_unparseable_address_is_not_off_machine(self):
        """解析不出來的字串不是合法 IP —— 分不出來不得當成證據。"""
        for bad in ("not-an-ip", "", None):
            self.assertFalse(identity.ip_is_offmachine(bad, local_ips=frozenset()),
                             bad)

    def test_resolve_host_ips_fails_closed_on_unresolvable_host(self):
        """解析不到位址(host 不存在、離線、或其實是 SSH config 別名而非可解析
        的名稱)回 None —— 呼叫端必須把它當成沒有證據,不是當成 off-machine。"""
        self.assertIsNone(
            identity.resolve_host_ips(
                "this-host-does-not-resolve.invalid.example.test-devflow"))

    def test_local_machine_ips_never_raises_and_returns_a_frozenset(self):
        """盡力而為的偵測 —— 任何一種探測手法失敗都不得讓呼叫端整個炸掉。"""
        result = identity._local_machine_ips()
        self.assertIsInstance(result, frozenset)
