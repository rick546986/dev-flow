"""測試共用治具(非測試檔)。

三件隔離,缺一個測試就會污染使用者真實環境:
①`AGENTMEM_HOME` 指到 mktemp —— 不碰真實 `~/.agentmem/`
②repo 用 mktemp 建的真 git repo —— `.dev-flow/` 落在暫存區
③`DEVFLOW_MEMORY_DIR` 保持預設 —— 但測完一律還原 env
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

MEMORY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if MEMORY_DIR not in sys.path:
    sys.path.insert(0, MEMORY_DIR)

from agentmem import identity, store  # noqa: E402


def git(root, *args, check=True):
    out = subprocess.run(["git", "-C", root, *args],
                         capture_output=True, text=True)
    if check and out.returncode != 0:
        raise AssertionError(
            "git {0} 失敗:{1}".format(" ".join(args), out.stderr.strip()))
    return out.stdout.strip()


def init_repo(root):
    """建一個可 commit 的 git repo(測試不依賴使用者 global git config)。"""
    os.makedirs(root, exist_ok=True)
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@dev-flow.local")
    git(root, "config", "user.name", "dev-flow test")
    git(root, "config", "commit.gpgsign", "false")
    write(root, "README.md", "# fixture\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "seed")
    return root


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def read_text(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as stream:
        return stream.read()


def read_file(path):
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def commit_all(root, message, allow_empty=False):
    git(root, "add", "-A")
    args = ["commit", "-q", "-m", message]
    if allow_empty:
        args.insert(1, "--allow-empty")
    git(root, *args)
    return git(root, "rev-parse", "HEAD")


class MemoryCase(unittest.TestCase):
    """自動建立隔離的 AGENTMEM_HOME + 一個真 git repo。"""

    def setUp(self):
        self.work = tempfile.mkdtemp(prefix="agentmem-test-")
        self.home = os.path.join(self.work, "home")
        self.repo = init_repo(os.path.join(self.work, "repo-mac"))
        self._env = {}
        self._set_env("AGENTMEM_HOME", self.home)
        self._set_env(identity.MEMORY_DIR_ENV, None)

    def tearDown(self):
        for key, old in self._env.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
        shutil.rmtree(self.work, ignore_errors=True)

    def _set_env(self, key, value):
        self._env.setdefault(key, os.environ.get(key))
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    # ── helpers ─────────────────────────────────────────────────────────────
    def new_repo(self, name):
        return init_repo(os.path.join(self.work, name))

    def project(self, root=None, name="fixture"):
        data, _created = identity.ensure_project(root or self.repo, name=name)
        return data

    def store_for(self, project_id, root=None):
        opened = store.open_for_root(project_id, root or self.repo)
        self.addCleanup(opened.close)
        return opened
