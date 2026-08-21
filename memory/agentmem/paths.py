"""路徑正規化與絕對路徑守衛。

durable memory 會被 push 到 Git、再被另一台機器 clone 回來。任何寫進
`.dev-flow/` 的檔案引用因此**只能是 repo-root-relative 的 POSIX 路徑**:

    對: src/services/db.ts / package.json / migrations/20260820_x.sql
    錯: /Users/rick/project/src/services/db.ts
    錯: D:\\project\\src\\services\\db.ts
    錯: ../outside/file.ts

理由與 issue #7(路徑分隔符一律正斜線)同源:讓平台決定寫出什麼形狀,等於在寫入
當下就種下跨機器對不起來的不一致 —— 而且這種不一致不會報錯,只會讓查詢在另一台
機器上靜默查不到。故本檔提供**單一正規化入口**與**fail-loud 的守衛**,
durable 寫入路徑一律先過 `assert_portable()`。
"""
import os
import re
import subprocess

_WIN_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_UNC = re.compile(r"^\\\\")


class NonPortablePath(ValueError):
    """路徑不可攜(絕對路徑 / 反斜線 / 逃出 repo root)—— durable 寫入必須擋。"""


def repo_root(start=None):
    """解析 repo root。git toplevel 優先,失敗則往上找 `.git`;都沒有回 None。

    不用「自身位置/..」推導 —— 那是 G1 教訓(散發到子目錄後預設輸出靜默巢狀)。
    """
    start = os.path.abspath(start or os.getcwd())
    try:
        out = subprocess.run(
            ["git", "-C", start, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            return os.path.realpath(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    cur = start
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return os.path.realpath(cur)
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def looks_absolute(value):
    """字串看起來像絕對路徑嗎?(POSIX / Windows drive / UNC / `~`)

    用於守衛而非解析:寧可對 `~/x` 這種也判 True,也不要讓它進 durable memory。
    """
    if not isinstance(value, str) or not value:
        return False
    return bool(value.startswith("/") or value.startswith("~")
                or _WIN_DRIVE.match(value) or _UNC.match(value))


def to_posix(value):
    """反斜線一律轉正斜線,並收掉重複分隔符。不做 realpath、不碰檔案系統。"""
    if not isinstance(value, str):
        raise NonPortablePath("path must be str, got {0!r}".format(type(value)))
    normalized = value.replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized


def to_repo_relative(path, root):
    """把任意路徑轉成 repo-root-relative POSIX 路徑;逃出 root 則丟例外。

    不要求檔案存在(durable memory 可以引用已被刪除的檔 —— 那正是 STALE 的證據)。
    """
    if root is None:
        raise NonPortablePath("repo root 未知,無法產生 repo-relative 路徑")
    root_real = os.path.realpath(root)
    candidate = path if os.path.isabs(path) else os.path.join(root_real, path)
    # realpath 只用於解析 symlink 與 `..`;不要求存在。
    resolved = os.path.realpath(candidate)
    rel = os.path.relpath(resolved, root_real)
    rel = to_posix(rel)
    if rel == ".":
        return ""
    if rel.startswith("../"):
        raise NonPortablePath(
            "路徑逃出 repo root,不可寫入 durable memory:{0}".format(path))
    return rel


def assert_portable(rel):
    """durable 寫入守衛:只接受 repo-relative POSIX 相對路徑。

    擋四種形狀:絕對路徑、Windows drive/UNC、反斜線、`..` 段。
    """
    if not isinstance(rel, str) or not rel:
        raise NonPortablePath("空路徑不可寫入 durable memory")
    if looks_absolute(rel):
        raise NonPortablePath(
            "durable memory 禁止絕對路徑(跨機器一定對不上):{0}".format(rel))
    if "\\" in rel:
        raise NonPortablePath(
            "durable memory 禁止反斜線(Windows 寫出的形狀在 Mac 查不到):{0}".format(rel))
    if rel.split("/")[0] == ".." or "/../" in rel or rel.endswith("/.."):
        raise NonPortablePath("durable memory 禁止 `..` 逃出 repo root:{0}".format(rel))
    return rel


def scan_absolute_paths(text):
    """在自由文字裡找出疑似絕對路徑(durable 寫入前的內容面守衛)。

    回傳命中清單。用於「知識內容誤貼了本機路徑」這種 leak —— 光擋 path 欄位不夠,
    敘述文字裡貼一條 `/Users/rick/...` 一樣會把本機資訊送進 Git。
    """
    if not isinstance(text, str):
        return []
    hits = []
    for m in re.finditer(r"(?:(?<=^)|(?<=[\s\"'`(\[]))"
                         r"(?:/(?:Users|home|var|opt|etc|private|tmp|root)/[^\s\"'`)\]]+"
                         r"|~/[^\s\"'`)\]]+"
                         r"|[A-Za-z]:[\\/][^\s\"'`)\]]+"
                         r"|\\\\[^\s\"'`)\]]+)", text):
        hits.append(m.group(0))
    return hits
