"""relative path 紀律:durable memory 只收 repo-relative POSIX 路徑(§4/§31)。"""
import os

from memtools import MemoryCase, write
from agentmem import paths


class PortabilityTest(MemoryCase):
    def test_repo_root_resolves_from_subdirectory(self):
        sub = os.path.join(self.repo, "src", "services")
        os.makedirs(sub)
        self.assertEqual(paths.repo_root(sub), os.path.realpath(self.repo))

    def test_to_repo_relative_normalizes_to_posix(self):
        write(self.repo, "src/services/db.ts", "x\n")
        absolute = os.path.join(self.repo, "src", "services", "db.ts")
        self.assertEqual(paths.to_repo_relative(absolute, self.repo),
                         "src/services/db.ts")
        self.assertEqual(
            paths.to_repo_relative("src/services/db.ts", self.repo),
            "src/services/db.ts")

    def test_escape_from_root_is_rejected(self):
        with self.assertRaises(paths.NonPortablePath):
            paths.to_repo_relative("../outside.ts", self.repo)

    def test_assert_portable_rejects_four_shapes(self):
        for bad in ("/Users/rick/project/src/db.ts", "D:\\project\\src\\db.ts",
                    "src\\services\\db.ts", "../outside/db.ts",
                    "~/project/db.ts", "\\\\server\\share\\db.ts"):
            with self.assertRaises(paths.NonPortablePath, msg=bad):
                paths.assert_portable(bad)

    def test_assert_portable_accepts_repo_relative(self):
        for good in ("src/services/db.ts", "package.json",
                     "migrations/20260820_x.sql", "docs/dev/README.md"):
            self.assertEqual(paths.assert_portable(good), good)

    def test_scan_absolute_paths_finds_machine_local_leaks(self):
        text = ("backend 定義在 /Users/rick/dev/proj/src/db.ts,"
                "Windows 側是 D:\\dev\\proj\\src\\db.ts,家目錄 ~/notes.md")
        hits = paths.scan_absolute_paths(text)
        self.assertEqual(len(hits), 3, hits)

    def test_scan_absolute_paths_ignores_relative(self):
        self.assertEqual(
            paths.scan_absolute_paths("見 src/services/db.ts 與 package.json"), [])

    def test_looks_absolute(self):
        self.assertTrue(paths.looks_absolute("/etc/hosts"))
        self.assertTrue(paths.looks_absolute("C:/x"))
        self.assertFalse(paths.looks_absolute("src/x.ts"))
