"""Project identity(path-independent)與 local workspace metadata。

**核心規則**:`project_path` 不再是 identity,只是 local workspace metadata。

    identity(進 Git,跨機器同一份)   → .dev-flow/project.yaml 的 project_id
    workspace(不進 Git,每台機器一份)→ local SQLite 的 workspaces 表
                                        (local_path / os / branch / head / worktree)

同一個 project 在 Mac 的 `/Users/rick/dev/proj`、Windows 的 `D:\\dev\\proj`、
Linux 的 `/home/rick/proj` 是**同一個 project_id** —— 因為 project_id 來自
commit 進 Git 的 `project.yaml`,而不是來自 filesystem path。

remote repository 只能當 metadata/provenance(`origin` 欄),不能當 identity:
沒有 remote、remote 改名、fork、鏡像、同一份 code 推到兩個 remote,project_id 都不變。
"""
import os
import platform
import subprocess

from . import DURABLE_SCHEMA_VERSION, ids, paths, yamlmini

MEMORY_DIR_ENV = "DEVFLOW_MEMORY_DIR"
DEFAULT_MEMORY_DIR = ".dev-flow"
PROJECT_FILE = "project.yaml"

_PROJECT_KEY_ORDER = ["schema_version", "project_id", "name", "created_at"]

_HEADER = """\
dev-flow durable Agent Memory —— project identity(進 Git,不要手改 project_id)。

project_id 是 path-independent 的 stable identity:
- 不含任何 filesystem path 成分 —— 換機器、改目錄名、換 worktree 都不變
- 不依賴 GitHub / remote URL —— origin 只是 provenance metadata
- dev-setup 重跑一律 reuse 既有值,不重新產生

本機的 local path / OS / branch / HEAD 屬 workspace metadata,住 local SQLite,
刻意不寫進這個檔(那些值每台機器不同,寫進 Git 只會製造無意義的 diff 與衝突)。"""


class IdentityError(RuntimeError):
    """identity 解析/建立失敗 —— 一律 fail-loud,不猜、不自動改寫既有 project_id。"""


def memory_dir_name():
    """durable memory 目錄名。預設 `.dev-flow`,可用 env 覆寫。

    為什麼留覆寫通道:本 repo 的 local runtime 目錄叫 `.devflow/`(無連字號、
    gitignored),durable 目錄叫 `.dev-flow/`(有連字號、進 Git)—— 兩者只差一個字元,
    是已知的命名風險。留一個單點覆寫,採用專案要改名時不必動程式碼。
    """
    return os.environ.get(MEMORY_DIR_ENV) or DEFAULT_MEMORY_DIR


def durable_root(repo_root_path):
    """durable memory 根目錄的絕對路徑(不建立目錄)。"""
    return os.path.join(repo_root_path, memory_dir_name())


def project_file(repo_root_path):
    return os.path.join(durable_root(repo_root_path), PROJECT_FILE)


def _git(root, *args):
    try:
        out = subprocess.run(["git", "-C", root, *args],
                             capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def read_project(repo_root_path):
    """讀 `.dev-flow/project.yaml`;不存在回 None。內容不合法丟 IdentityError。"""
    path = project_file(repo_root_path)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        text = stream.read()
    try:
        data = yamlmini.load(text)
    except yamlmini.YamlMiniError as exc:
        raise IdentityError(
            "{0} 解析失敗(不自動重建 —— 重建會換掉 project_id,"
            "等於讓這台機器變成另一個專案):{1}".format(path, exc))
    if not isinstance(data, dict):
        raise IdentityError("{0} 頂層必須是 mapping".format(path))
    pid = data.get("project_id")
    if not ids.is_valid_id("project", pid):
        raise IdentityError(
            "{0} 的 project_id 不合法({1!r});請人工修復,"
            "不要讓工具自動產生新的".format(path, pid))
    if data.get("schema_version") != DURABLE_SCHEMA_VERSION:
        # 不是錯誤:未來版本的檔案在舊工具上要能被辨識出「版本不同」而不是被誤讀。
        data["schema_version_mismatch"] = True
    return data


def ensure_project(repo_root_path, name=None, now=None, create=True):
    """回傳 (project_dict, created)。已存在一律 reuse(idempotent 的核心保證)。

    dev-setup 重跑不得產生新的 project_id —— 這是 §12 的硬條件,也是 §31 的測試案。
    """
    existing = read_project(repo_root_path)
    if existing is not None:
        return existing, False
    if not create:
        raise IdentityError(
            "{0} 不存在;請先跑 dev-setup(唯一 setup 入口)".format(
                project_file(repo_root_path)))
    data = {
        "schema_version": DURABLE_SCHEMA_VERSION,
        "project_id": ids.new_id("project"),
        "name": name or os.path.basename(os.path.realpath(repo_root_path)),
        "created_at": now or _utc_now(),
    }
    origin = _git(repo_root_path, "config", "--get", "remote.origin.url")
    if origin:
        # provenance only —— 讀取端不得用它做 identity 比對(見本檔頂註)。
        data["origin_provenance"] = origin
    write_project(repo_root_path, data)
    return data, True


def write_project(repo_root_path, data):
    """deterministic 寫入 project.yaml(atomic;同目錄 temp + rename)。"""
    root = durable_root(repo_root_path)
    os.makedirs(root, exist_ok=True)
    payload = {k: v for k, v in data.items() if k != "schema_version_mismatch"}
    text = yamlmini.dump(payload, key_order=_PROJECT_KEY_ORDER, header=_HEADER)
    _atomic_write_text(project_file(repo_root_path), text)


def _atomic_write_text(path, text):
    import tempfile
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _utc_now():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def workspace_snapshot(repo_root_path):
    """當前 local workspace 的狀態(branch / HEAD / worktree / dirty files)。

    Current Truth 的驗證基準是**當前 checkout**,不是 main —— 所以這裡拿到的
    branch/HEAD/dirty 會直接餵給 LVP invalidation(見 truth.py)。
    """
    root = os.path.realpath(repo_root_path)
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD") \
        or _git(root, "symbolic-ref", "--short", "HEAD")
    head = _git(root, "rev-parse", "HEAD")
    common = _git(root, "rev-parse", "--git-common-dir")
    git_dir = _git(root, "rev-parse", "--git-dir")
    is_worktree = bool(common and git_dir
                       and os.path.realpath(os.path.join(root, common))
                       != os.path.realpath(os.path.join(root, git_dir)))
    dirty = []
    # -uall:未追蹤的整個目錄會被 git 摺疊成 `src/` 一列,摺疊後對不上
    # fact 的 dependencies(那是逐檔路徑)—— 失效判定會整批漏掉。
    status = _git(root, "status", "--porcelain=v1", "-z", "-uall")
    if status:
        for entry in status.split("\0"):
            if len(entry) > 3:
                dirty.append(paths.to_posix(entry[3:]))
    return {
        "local_path": root,
        "os": platform.system().lower() or "unknown",
        "branch": branch or "(detached)",
        "head_sha": head or "",
        "worktree": "linked" if is_worktree else "main",
        "dirty_files": sorted(set(dirty)),
    }


def workspace_key(project_id, local_path):
    """同一台機器同一路徑 = 同一個 workspace。改路徑 = 新 workspace,project_id 不變。"""
    import hashlib
    material = "{0}\0{1}\0{2}".format(
        project_id, platform.node() or "unknown",
        paths.to_posix(os.path.realpath(local_path)))
    return "wsp_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
