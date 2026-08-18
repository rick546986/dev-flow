#!/bin/bash
# check-status-policy.sh — STATUS 規則對帳守衛(Repo-local)。
#
# 為什麼需要:「STATUS.md 只在整合分支維護」這條規則第一次落地時,只寫進散發給
# 採用專案的 `_templates/STATUS.md`,母版自用的 `docs/dev/STATUS.md` 沒套 ——
# 寫下規則的那一輪,下一個 commit 就自己破了例(第 6 型假綠:不對稱保護,修法
# 只套觸發它的那一個實例;規格正本 notes/dispatch-v380-blockers.md S-1)。
# 另外 Active 表頭新增的 `Branch` 欄(README §7「直接補修」判準的資料來源)
# 全 repo 原本沒有任何守衛在看,quickstart 的範例列又是手寫的、renderer 不同步。
#
# 驗六件:
#   ①模板頂註的規則要點(整合分支維護/不碰/merger 移出/寫入紀律)在
#     `docs/dev/STATUS.md` 也存在 —— 釘「要點都在」,不比逐字(兩份用途不同,
#     硬釘逐字會天天假紅)
#   ②`_templates/STATUS.md` Active 表頭含 `Branch` 欄,表頭/分隔列/範例列欄數一致,
#     範例列帶 sentinel `n-a:尚未建立 branch`(逐字,機械判定用)
#   ③`guides/guide-quickstart.html` 的手寫 STATUS 範例列欄數 = 模板表頭欄數
#   ④~⑥(A-3)quickstart Stage 6「完整可複製指令」區塊:html.unescape 後只解析
#     該 <pre> 區塊(不在全文湊關鍵詞),單線與 worktree 兩條動線分開驗
#     fetch < 取錨點 < 建 branch < 驗 HEAD=="$FORK" < 寫錨點 < commit 錨點 <
#     push -u < STATUS 交接 < 回 feature/worktree < start/status/doctor 的先後關係;
#     `_templates/6-implementation-notes.md` 步 0 要有獨立逐字欄
#     `FORK_INTEGRATION_SHA: <40 碼>`;unescape 後全檔禁 `feature/<slug>` 命名。
# 並各帶內建負向 fixture(把各件改壞一次,守衛必須紅 —— 不紅就是白做)。
#
# 掛載:scripts/devflow-check.sh group_architecture()。
# 用法:scripts/check-status-policy.sh(無參數)
# exit:0 = 全過 / 1 = 有 FAIL / 2 = 環境或解析失敗(fail-closed)
set -uo pipefail

[ $# -eq 0 ] || { echo "usage: $0(無參數)" >&2; exit 2; }
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

DEVFLOW_ROOT="$ROOT" python3 - <<'PY'
import html
import os
import re
import sys

ROOT = os.environ["DEVFLOW_ROOT"]

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


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        print(f"FATAL: 找不到 {rel}", file=sys.stderr)
        sys.exit(2)
    return open(path, encoding="utf-8").read()


template = read("_templates/STATUS.md")
docs = read("docs/dev/STATUS.md")
quickstart = read("guides/guide-quickstart.html")
template6 = read("_templates/6-implementation-notes.md")

# ①規則要點對帳:每個要點 = 一組必須同時出現的關鍵詞(不比逐字)。
POINTS = [
    ("只在整合分支維護", ["只在整合分支", "不碰本檔"]),
    ("ship 移出 Active 由 merger 在合併後做", ["移出", "Active", "合併"]),
    ("改前 pull --ff-only", ["pull --ff-only"]),
    ("push 被拒走 rebase 重放並核對列集合", ["rebase", "列集合"]),
    ("禁 force push / reset --hard", ["push --force", "reset --hard"]),
]


def preamble(text):
    """檔頭到第一個 `## ` 之前的頂註區 —— 規則必須住在這裡;
    只掃全檔的話,檔案別處(如 Backlog 註記)提到同字串會讓刪規則不被抓到。"""
    m = re.search(r"^## ", text, re.M)
    return text[:m.start()] if m else text


def policy_failures(template_text, docs_text):
    fails = []
    for label, tokens in POINTS:
        for name, text in (("_templates/STATUS.md", preamble(template_text)),
                           ("docs/dev/STATUS.md", preamble(docs_text))):
            missing = [t for t in tokens if t not in text]
            if missing:
                fails.append(f"{name} 頂註缺要點「{label}」(找不到 {missing})")
    return fails


def active_table(text):
    """回 (header_cells, sep_cells, sample_cells);找不到回 None。"""
    m = re.search(r"^\| Feature \|.*$", text, re.M)
    if not m:
        return None
    lines = text[m.start():].splitlines()
    if len(lines) < 3:
        return None
    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]
    return cells(lines[0]), cells(lines[1]), cells(lines[2])


def table_failures(template_text):
    fails = []
    table = active_table(template_text)
    if table is None:
        return ["_templates/STATUS.md 找不到 Active 表(表頭 `| Feature |…`)"]
    header, sep, sample = table
    if "Branch" not in header:
        fails.append(f"Active 表頭缺 `Branch` 欄(實得 {header})")
    if not (len(header) == len(sep) == len(sample)):
        fails.append(f"表頭/分隔列/範例列欄數不一致({len(header)}/{len(sep)}/{len(sample)})")
    if "n-a:尚未建立 branch" not in template_text:
        fails.append("範例列缺 sentinel `n-a:尚未建立 branch`(逐字,機械判定用)")
    return fails


def quickstart_failures(template_text, quickstart_text):
    table = active_table(template_text)
    if table is None:
        return ["模板 Active 表解析失敗,quickstart 對帳無基準"]
    header = table[0]
    m = re.search(r"^.*\| full \| 1-discussion \|.*$", quickstart_text, re.M)
    if not m:
        return ["guides/guide-quickstart.html 找不到 STATUS 範例列"
                "(含 `| full | 1-discussion |` 的那行)"]
    row = m.group(0)
    inner = re.search(r"<code>\|(.*)\|</code>", row)
    if not inner:
        return ["quickstart 範例列不是 `<code>|…|</code>` 形狀"]
    cols = [c for c in inner.group(1).split("|")]
    if len(cols) != len(header):
        return [f"quickstart 範例列 {len(cols)} 欄 ≠ 模板表頭 {len(header)} 欄"
                "(那段是手寫的,renderer 不會同步,要手改)"]
    return []


# ④~⑥(A-3)Stage 6 動線結構斷言 —— 只解析「完整可複製指令」那個 <pre> 區塊,
# 不在全文湊關鍵詞;順序用 index 比,不只驗 presence(否則順序 mutant 混得過去)。
def stage6_block(quickstart_text):
    """回 (header, single, wt, tail);解析失敗回 None。先 html.unescape 再切段 ——
    原始碼存的是 `feat/&lt;slug&gt;`,不 unescape 什麼都搜不到(假綠)。"""
    un = html.unescape(quickstart_text)
    m = re.search(r"完整可複製指令.*?<pre>(.*?)</pre>", un, re.S)
    if not m:
        return None
    pre = m.group(1)
    i_s, i_w, i_t = pre.find("# 單線"), pre.find("# 並行"), pre.find("# 兩者接下來都一樣")
    if i_s < 0 or i_w < 0 or i_t < 0 or not (i_s < i_w < i_t):
        return None
    return pre[:i_s], pre[i_s:i_w], pre[i_w:i_t], pre[i_t:]


def chain_failures(hay, steps, where):
    """steps = [(label, regex)];每步必須存在,且首次出現位置嚴格遞增。"""
    fails, prev_label, prev_i = [], None, -1
    for label, pat in steps:
        m = re.search(pat, hay)
        if not m:
            fails.append(f"{where}:找不到「{label}」")
            continue
        if m.start() < prev_i:
            fails.append(f"{where}:「{label}」出現在「{prev_label}」之前,順序錯")
        else:
            prev_label, prev_i = label, m.start()
    return fails


def stage6_failures(quickstart_text, part):
    blk = stage6_block(quickstart_text)
    if blk is None:
        return ["Stage 6「完整可複製指令」<pre> 區塊解析失敗(缺 單線/並行/共用尾段 標記或順序錯)"]
    header, single, wt, tail = blk
    if part == "shared":
        return (chain_failures(header, [
            ("git fetch", r"git fetch"),
            ("rev-parse --verify 取錨點(^{commit})", r"rev-parse --verify[^\n]*\^\{commit\}"),
        ], "共用起手式") + chain_failures(tail, [
            ("devflow-exec.sh start", r'devflow-exec\.sh" start'),
            ("devflow-exec.sh status", r'devflow-exec\.sh" status'),
            ("devflow-doctor.sh", r"devflow-doctor\.sh"),
        ], "共用尾段"))
    if part == "single":
        return chain_failures(single, [
            ("從 \"$FORK\" 建 feat/<slug>", r'git switch -c feat/<slug>[^\n]*"\$FORK"'),
            ("驗 HEAD == \"$FORK\"", r'rev-parse HEAD[^\n]*"\$FORK"'),
            ("寫錨點欄 FORK_INTEGRATION_SHA", r"FORK_INTEGRATION_SHA"),
            ("只 commit 錨點", r"git commit[^\n]*錨點"),
            ("push -u 發布", r"git push -u"),
            ("STATUS 交接", r"STATUS"),
            ("切回 feat/<slug>", r"git switch feat/<slug>"),
        ], "單線動線")
    return chain_failures(wt, [
        ("worktree add 以 \"$FORK\" 為起點", r'git worktree add -b feat/<slug>[^\n]*"\$FORK"'),
        ("git -C 驗新樹 HEAD == \"$FORK\"", r'git -C [^\n]*rev-parse HEAD[^\n]*"\$FORK"'),
        ("寫錨點欄 FORK_INTEGRATION_SHA", r"FORK_INTEGRATION_SHA"),
        ("樹內只 commit 錨點", r"git -C [^\n]*commit[^\n]*錨點"),
        ("樹內 push -u", r"git -C [^\n]*push -u"),
        ("STATUS 交接", r"STATUS"),
        ("cd 進 worktree", r"(?m)^cd <path>"),
    ], "worktree 動線")


def template6_fork_field_failures(t6_text):
    m = re.search(r"^> 0\. 起手式.*?(?=^> 1\. )", t6_text, re.M | re.S)
    if not m:
        return ["_templates/6-implementation-notes.md 找不到步 0 區段(`> 0. 起手式` ~ `> 1. `)"]
    for line in m.group(0).splitlines():
        if line.lstrip("> ").strip() == "FORK_INTEGRATION_SHA: <40 碼>":
            return []
    return ["步 0 缺獨立逐字欄 `FORK_INTEGRATION_SHA: <40 碼>`(散文/註解提及不算)"]


def forbidden_name_failures(quickstart_text):
    if "feature/<slug>" in html.unescape(quickstart_text):
        return ["unescape 後仍出現 `feature/<slug>`(branch 命名正本是 feat/<slug>)"]
    return []


print("-- ①規則要點:模板 vs 母版自用 docs/dev/STATUS.md --")
fails = policy_failures(template, docs)
check(not fails, "規則要點兩份都在(整合分支維護/merger 移出/寫入紀律五組)",
      "; ".join(fails))

print("-- ②Active 表頭與範例列 --")
fails = table_failures(template)
check(not fails, "模板 Active 表頭含 Branch 欄、欄數一致、sentinel 逐字在",
      "; ".join(fails))

print("-- ③quickstart 手寫範例列 --")
fails = quickstart_failures(template, quickstart)
check(not fails, "quickstart 範例列欄數 = 模板表頭欄數", "; ".join(fails))

print("-- ④Stage 6 共用起手式與尾段(fetch→取錨點;start→status→doctor)--")
fails = stage6_failures(quickstart, "shared")
check(not fails, "共用起手式 fetch 在取錨點前、尾段 start/status/doctor 齊且序對",
      "; ".join(fails))

print("-- ⑤Stage 6 單線動線 --")
fails = stage6_failures(quickstart, "single")
check(not fails, "單線:建branch→驗HEAD→寫錨點→commit錨點→push→STATUS交接→切回,序全對",
      "; ".join(fails))

print("-- ⑥Stage 6 worktree 動線 --")
fails = stage6_failures(quickstart, "worktree")
check(not fails, "worktree:add($FORK)→git -C 驗HEAD→寫錨點→commit→push→STATUS→cd,序全對",
      "; ".join(fails))

print("-- ⑦template6 步 0 錨點欄 --")
fails = template6_fork_field_failures(template6)
check(not fails, "步 0 有獨立逐字欄 FORK_INTEGRATION_SHA: <40 碼>", "; ".join(fails))

print("-- ⑧branch 命名禁字 --")
fails = forbidden_name_failures(quickstart)
check(not fails, "quickstart unescape 後無 feature/<slug>", "; ".join(fails))

print("-- 負向 fixture(改壞必須紅,不紅就是白做)--")
mutated_docs = docs.replace("只在整合分支", "在任何分支").replace("不碰本檔", "隨便改")
check(bool(policy_failures(template, mutated_docs)),
      "負向①:刪掉 docs/dev/STATUS.md 的規則段 → 紅")
mutated_template = template.replace("| Branch ", "").replace("| n-a:尚未建立 branch ", "")
check(bool(table_failures(mutated_template)),
      "負向②:模板表頭拿掉 Branch 欄 → 紅")
old_row = ("<code>| &lt;slug&gt; | full | 1-discussion | &lt;你的名字&gt; "
           "| G1⬜ G2⬜ G3⬜ | &lt;日期&gt; |</code>")
mutated_qs = re.sub(r"^.*\| full \| 1-discussion \|.*$", old_row, quickstart,
                    count=1, flags=re.M)
check(bool(quickstart_failures(template, mutated_qs)),
      "負向③:只改模板不改 quickstart 範例列(欄數退回 6)→ 紅")
mutated_qs = re.sub(r"(?m)^git fetch [^\n]*\n", "", quickstart, count=1)
check(bool(stage6_failures(mutated_qs, "shared")),
      "負向④:Stage 6 拿掉 git fetch → 紅")
m_f = re.search(r"(?m)^git fetch [^\n]*$", quickstart)
m_c = re.search(r"(?m)^FORK=\$\([^\n]*$", quickstart)
if m_f and m_c and m_f.start() < m_c.start():
    swapped = (quickstart[:m_f.start()] + m_c.group(0)
               + quickstart[m_f.end():m_c.start()] + m_f.group(0)
               + quickstart[m_c.end():])
else:
    swapped = quickstart  # 找不到兩行 = 正向檢查早就紅了;這裡讓負向也紅出來
check(bool(stage6_failures(swapped, "shared")),
      "負向⑤:fetch 移到取錨點之後(只換順序,兩行都在)→ 紅")
mutated_qs = quickstart.replace(
    'git worktree add -b feat/&lt;slug&gt; &lt;path&gt; "$FORK"',
    "git worktree add -b feat/&lt;slug&gt; &lt;path&gt;")
check(bool(stage6_failures(mutated_qs, "worktree")),
      "負向⑥:worktree add 拿掉 \"$FORK\" 起點 → 紅")
mutated_t6 = "\n".join(
    line for line in template6.splitlines()
    if line.lstrip("> ").strip() != "FORK_INTEGRATION_SHA: <40 碼>")
check(bool(template6_fork_field_failures(mutated_t6)),
      "負向⑦:刪 template6 步 0 錨點欄(散文提及仍在)→ 紅")
check(bool(forbidden_name_failures(quickstart + "\n<!-- feature/&lt;slug&gt; -->")),
      "負向⑧:塞回 feature/<slug> 命名 → 紅")

print()
if FAILED:
    print(f"⛔ STATUS 規則對帳:{FAILED}/{CHECKS} 失敗")
    sys.exit(1)
print(f"✅ STATUS 規則對帳:全過({CHECKS} 項)")
PY
