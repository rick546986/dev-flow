#!/bin/bash
# check-integration-regression-guard.sh — 整合回歸工具的母版自檢 wrapper(Repo-local)。
#
# 為什麼需要:devflow-integration-regression.sh 的前身(模板內嵌演算法)在合併之後
# 才算交集,兩個座標都被污染 —— 要嘛交集灌水、要嘛判 n-a 假綠,六輪審查都沒抓到
# (規格正本 notes/dispatch-v380-blockers.md H-1)。本 wrapper 把行為釘成常設測試:
#   ①八個情境(A–H):在拋棄式 git repo 建圖,跑**正式工具本體**(不重寫演算法 ——
#     斷言釘在副本上就是第 3 型假綠),驗狀態字串+exit code+共同戰場清單
#   ②五個 mutant(M-a~M-e):把工具的臨時複本改壞,對應情境必須給出錯誤答案;
#     壞複本也給正確答案 = 情境沒有鑑別力,一樣 FAIL
#   ③模板順序:7-review Exit Checklist 那條裡「跑工具」必須出現在「合併」與
#     「全套測試」之前(順序寫反正是原始 bug 的形狀)
#   ④正本/散發副本 parity:expected set 取自檔案地圖標「散發面:docs/dev/tools/」
#     的列(不只掃副本目錄 —— 正副本同時被刪時,掃目錄的清單會少一項而全綠,
#     第 4 型假綠);雙向比對存在性+內容+可執行位元,並含負向 fixture 驗證
#
# 掛載:scripts/devflow-check.sh group_architecture()。
# 注意:受測工具吐出的 10/11 是測試資料,不是本 wrapper 的退出碼。
#
# 用法:scripts/check-integration-regression-guard.sh   # 無參數
# exit:0 = 全部 assertion 通過 / 1 = 情境/mutant/parity/模板順序任一不對 /
#      2 = 環境問題或用法錯(缺 python3、不在 repo、正式工具檔不存在)
set -uo pipefail

[ $# -eq 0 ] || { echo "usage: $0(無參數)" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "FATAL: 缺 python3" >&2; exit 2; }
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
[ -f "$ROOT/scripts/devflow-integration-regression.sh" ] || {
  echo "FATAL: 正式工具 scripts/devflow-integration-regression.sh 不存在" >&2; exit 2; }

DEVFLOW_ROOT="$ROOT" python3 - <<'PY'
import html
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = os.environ["DEVFLOW_ROOT"]
TOOL = os.path.join(ROOT, "scripts", "devflow-integration-regression.sh")
TOOL_TEXT = open(TOOL, encoding="utf-8").read()

FAILED = 0
CHECKS = 0


def check(cond, label, detail=""):
    global FAILED, CHECKS
    CHECKS += 1
    if cond:
        print(f"  ✓ {label}")
    else:
        FAILED += 1
        print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))


def sh(args, cwd, env_extra=None):
    env = dict(os.environ)
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
    if env_extra:
        env.update(env_extra)
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


def must(proc, what):
    if proc.returncode != 0:
        print(f"FATAL: 建情境失敗({what}):{proc.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return proc


def write_commit(repo, files, msg):
    for name, content in files.items():
        with open(os.path.join(repo, name), "w", encoding="utf-8") as fh:
            fh.write(content)
    must(sh(["git", "add", "-A"], repo), "add")
    must(sh(["git", "commit", "-qm", msg], repo), "commit")


class Scenario:
    """拋棄式雙 clone 情境:origin(bare)+ work(feature)+ other(推 trunk 用)。"""

    def __init__(self, tmp):
        self.tmp = tmp
        origin = os.path.join(tmp, "origin.git")
        must(sh(["git", "init", "-q", "--bare", origin], tmp), "init bare")
        self.work = os.path.join(tmp, "work")
        must(sh(["git", "clone", "-q", origin, self.work], tmp), "clone work")

    def seed(self, base_files):
        write_commit(self.work, base_files, "base")
        must(sh(["git", "push", "-q", "origin", "HEAD:trunk"], self.work), "push trunk")
        must(sh(["git", "fetch", "-q", "origin"], self.work), "fetch")
        self.fork = must(sh(["git", "rev-parse", "origin/trunk"], self.work),
                         "rev-parse fork").stdout.strip()
        must(sh(["git", "switch", "-qc", "feat/a", self.fork], self.work), "switch feat")

    def feature_commit(self, files, msg="feat"):
        write_commit(self.work, files, msg)

    def trunk_commit(self, files, msg="trunk", rename=None):
        other = os.path.join(self.tmp, "other")
        if not os.path.isdir(other):
            must(sh(["git", "clone", "-q", os.path.join(self.tmp, "origin.git"), other],
                    self.tmp), "clone other")
            must(sh(["git", "switch", "-qc", "trunk", "origin/trunk"], other), "switch trunk")
        if rename:
            must(sh(["git", "mv", rename[0], rename[1]], other), "mv")
        if files:
            write_commit(other, files, msg)
        else:
            must(sh(["git", "commit", "-qam", msg], other), "commit")
        must(sh(["git", "push", "-q", "origin", "trunk"], other), "push trunk")

    def run_tool(self, tool_path=None, fork=None, integration="origin/trunk", extra=()):
        args = ["bash", tool_path or TOOL]
        if integration is not None:
            args += ["--integration", integration]
        if fork is not None:
            args += ["--fork-sha", fork]
        args += list(extra)
        proc = sh(args, self.work)
        out = proc.stdout + proc.stderr
        m = re.search(r"^STATUS: (\S+)$", out, re.M)
        status = m.group(1) if m else None
        overlap = []
        m = re.search(r"^共同戰場:\n((?:.+\n)*?)fetch:", out, re.M)
        if m:
            overlap = [line for line in m.group(1).splitlines() if line]
        return proc.returncode, status, overlap, out


def scenario(builder):
    tmp = tempfile.mkdtemp(prefix="irguard.")
    try:
        s = Scenario(tmp)
        return builder(s)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build_A(s):
    s.seed({"base.txt": "base\n"})
    s.feature_commit({"a1.txt": "a1\n", "a2.txt": "a2\n"})
    s.trunk_commit({"b1.txt": "b1\n", "b2.txt": "b2\n"})
    return s


print("-- 情境 A–H:正式工具行為 --")

def case_A(s):
    build_A(s)
    rc, status, overlap, _ = s.run_tool(fork=s.fork)
    check(rc == 10 and status == "SYNC_REQUIRED_NO_OVERLAP" and overlap == [],
          "A 有 incoming、零重疊 → SYNC_REQUIRED_NO_OVERLAP / exit 10 / 共同戰場無",
          f"rc={rc} status={status} overlap={overlap}")
scenario(case_A)

def case_B(s):
    s.seed({"base.txt": "base\n", "shared.txt": "v0\n"})
    s.feature_commit({"shared.txt": "feature 改\n", "a1.txt": "a1\n"})
    s.trunk_commit({"shared.txt": "trunk 改\n", "b1.txt": "b1\n"})
    rc, status, overlap, _ = s.run_tool(fork=s.fork)
    check(rc == 11 and status == "SYNC_REQUIRED_WITH_OVERLAP" and overlap == ["shared.txt"],
          "B 有共同檔 → SYNC_REQUIRED_WITH_OVERLAP / exit 11 / 交集只有 shared.txt(不混入 b1.txt)",
          f"rc={rc} status={status} overlap={overlap}")
scenario(case_B)

def case_C(s):
    s.seed({"base.txt": "base\n"})
    s.feature_commit({"a1.txt": "a1\n"})
    rc, status, overlap, _ = s.run_tool(fork=s.fork)
    check(rc == 0 and status == "N_A_NO_INCOMING",
          "C 對方零新 commit → N_A_NO_INCOMING / exit 0",
          f"rc={rc} status={status}")
scenario(case_C)

def case_D(s):
    build_A(s)
    must(sh(["git", "fetch", "-q", "origin"], s.work), "fetch")
    must(sh(["git", "merge", "-q", "--no-edit", "origin/trunk"], s.work), "merge")
    rc, status, _, _ = s.run_tool(fork=s.fork)
    check(rc == 2 and status == "ALREADY_SYNCED",
          "D 已 merge → ALREADY_SYNCED / exit 2(不准輸出 N_A_NO_INCOMING)",
          f"rc={rc} status={status}")
scenario(case_D)

def case_G(s):
    build_A(s)
    must(sh(["git", "fetch", "-q", "origin"], s.work), "fetch")
    must(sh(["git", "rebase", "-q", "origin/trunk"], s.work), "rebase")
    rc, status, _, _ = s.run_tool(fork=s.fork)
    check(rc == 2 and status == "ALREADY_SYNCED",
          "G 已 rebase(完全線性,無 merge commit)→ ALREADY_SYNCED / exit 2",
          f"rc={rc} status={status}")
scenario(case_G)

def case_E(s):
    build_A(s)
    with open(os.path.join(s.work, "dirty.txt"), "w") as fh:
        fh.write("未提交\n")
    rc, status, _, out = s.run_tool(fork=s.fork)
    check(rc == 2 and status is None and "工作樹不乾淨" in out,
          "E 工作樹髒 → exit 2,不帶著算(無 STATUS 輸出)",
          f"rc={rc} status={status}")
scenario(case_E)

def case_F(s):
    s.seed({"base.txt": "base\n",
            "x.txt": "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\n"})
    must(sh(["git", "mv", "x.txt", "y.txt"], s.work), "mv")
    must(sh(["git", "commit", "-qm", "rename"], s.work), "commit rename")
    s.trunk_commit({"x.txt": "line1\nline2 改\nline3\nline4\nline5\nline6\nline7\nline8\n"})
    rc, status, overlap, _ = s.run_tool(fork=s.fork)
    check(rc == 11 and "x.txt" in overlap,
          "F 改名 vs 內容改 → 共同戰場含 x.txt(--no-renames 生效)/ exit 11",
          f"rc={rc} status={status} overlap={overlap}")
scenario(case_F)

def case_H(s):
    build_A(s)
    feat_head = must(sh(["git", "rev-parse", "HEAD"], s.work), "rev-parse").stdout.strip()
    rc1, st1, _, out1 = s.run_tool(fork=None)
    check(rc1 == 2 and st1 is None and "缺 --fork-sha" in out1,
          "H① 缺 --fork-sha → exit 2(不退回 merge-base 猜,不判 N_A_NO_INCOMING)",
          f"rc={rc1} status={st1}")
    rc2, st2, _, _ = s.run_tool(fork=feat_head)
    check(rc2 == 2 and st2 is None,
          "H② 錨點不是整合分支祖先 → exit 2",
          f"rc={rc2} status={st2}")
    must(sh(["git", "branch", "localtrunk", "origin/trunk"], s.work), "branch")
    rc3, st3, _, out3 = s.run_tool(fork=s.fork, integration="localtrunk")
    check(rc3 == 2 and st3 is None and "refs/remotes/" in out3,
          "H③ --integration 給本地 ref → exit 2(必須是遠端追蹤 ref)",
          f"rc={rc3} status={st3}")
    rc4, st4, _, out4 = s.run_tool(fork=s.fork, extra=("--no-fetch",))
    check(rc4 == 2 and "不得用於勾 Exit Checklist" in out4,
          "H④ --no-fetch 診斷模式 → 一律 exit 2 並標記結果不可用",
          f"rc={rc4}")
scenario(case_H)

print("-- 情境 I:用法/參數錯(任何排列都不得死迴圈;每個子案 5 秒逾時) --")


def run_usage_case(args, cwd):
    """跑正式工具,5 秒逾時 —— 逾時回 (None, '');逾時即死迴圈回歸,對應子案必須紅。"""
    env = dict(os.environ)
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
    try:
        proc = subprocess.run(["bash", TOOL, *args], cwd=cwd, capture_output=True,
                              text=True, env=env, timeout=5)
    except subprocess.TimeoutExpired:
        return None, ""
    return proc.returncode, proc.stdout + proc.stderr


def case_I(s):
    # 在其餘座標全部有效的圖上跑(origin/trunk 存在、s.fork 是有效 SHA),
    # 讓每個子案的唯一錯誤就是被測的那個參數 —— 空值/吞旗標被「當成能用」時,
    # 工具會走進前置檢查而不印「用法」,子案就紅。
    build_A(s)
    cases = [
        ("I① 無參數", []),
        ("I② --integration 居末缺值", ["--integration"]),
        ("I③ --fork-sha 居末缺值", ["--fork-sha"]),
        ("I④ 前面成功解析、--fork-sha 居末缺值",
         ["--integration", "origin/trunk", "--fork-sha"]),
        ("I⑤ 前面成功解析、--integration 居末缺值",
         ["--fork-sha", "abc", "--integration"]),
        ("I⑥ 無值旗標先行、--integration 居末缺值", ["--no-fetch", "--integration"]),
        ("I⑦ --fork-sha 不得吞掉 --no-fetch 當值",
         ["--integration", "origin/trunk", "--fork-sha", "--no-fetch"]),
        ("I⑧ 不認得的參數", ["--bogus"]),
        ("I⑨ --integration 空字串不得當值", ["--integration", "", "--fork-sha", s.fork]),
        ("I⑩ --fork-sha 空字串不得當值", ["--integration", "origin/trunk", "--fork-sha", ""]),
    ]
    for label, args in cases:
        rc, out = run_usage_case(args, s.work)
        if rc is None:
            check(False, f"{label} → exit 2+印「用法」", "5 秒逾時 —— 參數解析死迴圈回歸")
        else:
            check(rc == 2 and "用法" in out, f"{label} → exit 2+印「用法」",
                  f"rc={rc} 訊息含「用法」={'是' if '用法' in out else '否'}")
scenario(case_I)

print("-- mutants M-a~M-e:改壞臨時複本,對應情境必須抓到 --")

MUTANTS = {
    "M-a": [('status, code = "SYNC_REQUIRED_NO_OVERLAP", 10',
             'status, code = "N_A_NO_INCOMING", 0', 1)],
    "M-b": [('rc, fork = git("rev-parse", "--verify", f"{FORK_ARG}^{{commit}}")',
             'rc, fork = git("merge-base", "HEAD", full_name)', 1)],
    "M-c": [('"--no-renames", ', '', 2)],
    "M-d": [('if porcelain.strip():', 'if False:', 1)],
    "M-e": [('if not FORK_ARG:', 'if False and not FORK_ARG:', 1),
            ('rc, fork = git("rev-parse", "--verify", f"{FORK_ARG}^{{commit}}")',
             'rc, fork = (git("rev-parse", "--verify", f"{FORK_ARG}^{{commit}}") '
             'if FORK_ARG else git("merge-base", "HEAD", full_name))', 1)],
}


def make_mutant(name):
    text = TOOL_TEXT
    for old, new, count in MUTANTS[name]:
        found = text.count(old)
        if found != count:
            check(False, f"{name} 錨字串命中 {count} 次",
                  f"實得 {found} —— 正式工具文字漂了,更新本 wrapper 的錨")
            return None
        text = text.replace(old, new)
    path = tempfile.mktemp(prefix=f"irmut-{name}.", suffix=".sh")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def mutant_case(name, build, expect_label, judge):
    path = make_mutant(name)
    if not path:
        return
    try:
        def run(s):
            build(s)
            return s
        # judge 拿 (scenario, mutant_path) 自跑並回 (ok, detail)
        tmp = tempfile.mkdtemp(prefix="irguard.")
        try:
            s = Scenario(tmp)
            build(s)
            ok, detail = judge(s, path)
            check(ok, f"{name} 被 {expect_label} 抓到(壞複本給出錯誤答案)", detail)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        os.unlink(path)


def build_D(s):
    build_A(s)
    must(sh(["git", "fetch", "-q", "origin"], s.work), "fetch")
    must(sh(["git", "merge", "-q", "--no-edit", "origin/trunk"], s.work), "merge")


def build_G(s):
    build_A(s)
    must(sh(["git", "fetch", "-q", "origin"], s.work), "fetch")
    must(sh(["git", "rebase", "-q", "origin/trunk"], s.work), "rebase")


mutant_case("M-a", build_A, "情境 A",
    lambda s, p: (lambda r: (r[0] == 0 and r[1] == "N_A_NO_INCOMING",
                             f"rc={r[0]} status={r[1]}"))(s.run_tool(tool_path=p, fork=s.fork)))
mutant_case("M-b", build_D, "情境 D",
    lambda s, p: (lambda r: (r[0] == 0 and r[1] == "N_A_NO_INCOMING",
                             f"rc={r[0]} status={r[1]}"))(s.run_tool(tool_path=p, fork=s.fork)))
mutant_case("M-b", build_G, "情境 G",
    lambda s, p: (lambda r: (r[0] == 0 and r[1] == "N_A_NO_INCOMING",
                             f"rc={r[0]} status={r[1]}"))(s.run_tool(tool_path=p, fork=s.fork)))


def build_F(s):
    s.seed({"base.txt": "base\n",
            "x.txt": "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\n"})
    must(sh(["git", "mv", "x.txt", "y.txt"], s.work), "mv")
    must(sh(["git", "commit", "-qm", "rename"], s.work), "commit")
    s.trunk_commit({"x.txt": "line1\nline2 改\nline3\nline4\nline5\nline6\nline7\nline8\n"})


mutant_case("M-c", build_F, "情境 F",
    lambda s, p: (lambda r: (not (r[0] == 11 and "x.txt" in r[2]),
                             f"rc={r[0]} overlap={r[2]}"))(s.run_tool(tool_path=p, fork=s.fork)))


def build_E(s):
    build_A(s)
    with open(os.path.join(s.work, "dirty.txt"), "w") as fh:
        fh.write("未提交\n")


mutant_case("M-d", build_E, "情境 E",
    lambda s, p: (lambda r: (r[0] == 10,
                             f"rc={r[0]} status={r[1]}"))(s.run_tool(tool_path=p, fork=s.fork)))
mutant_case("M-e", build_A, "情境 H①",
    lambda s, p: (lambda r: (r[0] == 10 and r[1] is not None,
                             f"rc={r[0]} status={r[1]}"))(s.run_tool(tool_path=p, fork=None)))

print("-- 模板順序:先跑工具,才輪得到合併與全套測試 --")

TEMPLATE = os.path.join(ROOT, "_templates", "7-review.md")


def order_violation(text):
    m = re.search(r"^- \[ \] \(條件式\)整合回歸.*?(?=^- \[ \]|^## |\Z)", text, re.M | re.S)
    if not m:
        return "找不到「(條件式)整合回歸」條目"
    body = m.group(0)
    i_tool = body.find("devflow-integration-regression.sh")
    if i_tool < 0:
        return "條目內沒提到 devflow-integration-regression.sh"
    i_merge = body.find("合併")
    i_test = body.find("全套測試")
    if i_merge >= 0 and i_tool > i_merge:
        return "「跑工具」出現在「合併」之後 —— 順序寫反正是原始 bug 的形狀"
    if i_test >= 0 and i_tool > i_test:
        return "「跑工具」出現在「全套測試」之後"
    return None


violation = order_violation(open(TEMPLATE, encoding="utf-8").read())
check(violation is None, "7-review Exit Checklist 條目順序正確(工具先於合併與全套測試)",
      violation or "")
BAD_ORDER = ("- [ ] (條件式)整合回歸:先把整合分支合併進來並跑全套測試,"
             "然後跑 devflow-integration-regression.sh 算交集\n")
check(order_violation(BAD_ORDER) is not None,
      "順序守衛負向:順序調換的樣本會被判違規(守衛有鑑別力)")

print("-- 正本/散發副本 parity(expected set 取自檔案地圖「散發面」標註)--")


def parity_failures(root):
    fails = []
    guide = os.path.join(root, "guides", "guide-dev-flow.html")
    if not os.path.isfile(guide):
        return ["找不到 guides/guide-dev-flow.html"]
    text = open(guide, encoding="utf-8").read()
    m = re.search(r'<h2 id="filemap">.*?(?=<h2 |\Z)', text, re.S)
    if not m:
        return ["找不到 filemap 節"]
    expected = set()
    for row in re.findall(r"<tr>(.*?)</tr>", m.group(0), re.S):
        if "散發面:<code>docs/dev/tools/</code>" not in row:
            continue
        cell = re.search(r"<td>(.*?)</td>", row, re.S)
        code = re.search(r"<code>(.*?)</code>", cell.group(1), re.S) if cell else None
        if code:
            expected.add(html.unescape(code.group(1)).strip())
    if not expected:
        return ["檔案地圖沒有任何一列標「散發面:docs/dev/tools/」—— expected set 空,無從對帳"]
    for name in sorted(expected):
        src = os.path.join(root, "scripts", name)
        dst = os.path.join(root, "docs", "dev", "tools", name)
        if not os.path.isfile(src):
            fails.append(f"正本不存在:scripts/{name}(檔案地圖列還在 → 正副本同刪也會紅)")
        if not os.path.isfile(dst):
            fails.append(f"副本不存在:docs/dev/tools/{name}(忘記散發,或副本被刪)")
        if os.path.isfile(src) and os.path.isfile(dst):
            if open(src, "rb").read() != open(dst, "rb").read():
                fails.append(f"內容不同:{name}(改了正本沒重新散發)")
            src_x = os.stat(src).st_mode & 0o111
            dst_x = os.stat(dst).st_mode & 0o111
            if src_x != dst_x:
                fails.append(f"可執行位元不一致:{name}(正本 {src_x:o} vs 副本 {dst_x:o})")
    tools_dir = os.path.join(root, "docs", "dev", "tools")
    if os.path.isdir(tools_dir):
        for f in sorted(os.listdir(tools_dir)):
            if os.path.isfile(os.path.join(tools_dir, f)) and f not in expected:
                fails.append(f"反向:docs/dev/tools/{f} 不在檔案地圖「散發面」列裡"
                             "(散發了但沒記帳)")
    return fails


real_fails = parity_failures(ROOT)
check(not real_fails, "正本/散發副本 parity 全過(存在性+內容+可執行位元,雙向)",
      "; ".join(real_fails))

NEW_TOOL = "devflow-integration-regression.sh"
for rel in (os.path.join("scripts", NEW_TOOL),
            os.path.join("docs", "dev", "tools", NEW_TOOL)):
    p = os.path.join(ROOT, rel)
    mode = os.stat(p).st_mode & 0o777 if os.path.isfile(p) else None
    check(mode == 0o755, f"{rel} mode=755(檔名+位置+期望 mode 三件一組,寫死)",
          f"實得 {mode:o}" if mode is not None else "檔案不存在")

# 負向 fixture:正副本同時被刪、filemap 列仍在 → parity 必須紅(第 4 型假綠防護)
fixture = tempfile.mkdtemp(prefix="irparity.")
try:
    os.makedirs(os.path.join(fixture, "guides"))
    os.makedirs(os.path.join(fixture, "scripts"))
    os.makedirs(os.path.join(fixture, "docs", "dev", "tools"))
    rows = "".join(
        f'<tr><td><code>{n}</code></td><td>x</td>'
        f'<td>(散發面:<code>docs/dev/tools/</code>)</td></tr>'
        for n in ("tool-x.sh", "tool-y.sh"))
    with open(os.path.join(fixture, "guides", "guide-dev-flow.html"), "w") as fh:
        fh.write(f'<h2 id="filemap">map</h2><table>{rows}</table>')
    for n in ("tool-x.sh", "tool-y.sh"):
        for d in ("scripts", os.path.join("docs", "dev", "tools")):
            p = os.path.join(fixture, d, n)
            with open(p, "w") as fh:
                fh.write("#!/bin/bash\n")
            os.chmod(p, 0o755)
    check(not parity_failures(fixture), "parity 負向 fixture 基線:兩工具齊全 → 綠")
    os.unlink(os.path.join(fixture, "scripts", "tool-y.sh"))
    os.unlink(os.path.join(fixture, "docs", "dev", "tools", "tool-y.sh"))
    fails = parity_failures(fixture)
    check(any("tool-y.sh" in f for f in fails),
          "parity 負向:正副本同時刪、filemap 列仍在 → 紅(不是掃目錄式的靜默縮水)",
          f"實得 {fails}")
finally:
    shutil.rmtree(fixture, ignore_errors=True)

print()
if FAILED:
    print(f"⛔ 整合回歸守衛:{FAILED}/{CHECKS} 失敗")
    sys.exit(1)
print(f"✅ 整合回歸守衛:全過({CHECKS} 項)")
PY
