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
# 驗十件:
#   ①模板頂註的規則要點(整合分支維護/寫入紀律)在
#     `docs/dev/STATUS.md` 也存在 —— 釘「要點都在」,不比逐字(兩份用途不同,
#     硬釘逐字會天天假紅)。「ship 移出由誰做」不在這裡驗:關鍵詞集合釘不住
#     actor(改成 owner 三個詞照樣全中,B-2),由⑨⑩ scoped 驗。
#   ②`_templates/STATUS.md` Active 表頭含 `Branch` 欄,表頭/分隔列/範例列欄數一致,
#     範例列 `Branch` 那一格逐字 = sentinel `n-a:尚未建立 branch`(B-3:全檔搜尋
#     驗不到這一格 —— 頂註說明裡的同字串會餵綠,必須取儲存格比)
#   ③`guides/guide-quickstart.html` 的手寫 STATUS 範例列欄數 = 模板表頭欄數
#   ④~⑥(A-3)quickstart Stage 6「完整可複製指令」區塊:html.unescape 後只解析
#     該 <pre> 區塊(不在全文湊關鍵詞),單線與 worktree 兩條動線分開驗
#     fetch < 取錨點 < 建 branch < 驗 HEAD=="$FORK" < 寫錨點 < commit 錨點 <
#     push -u < STATUS 交接 < 回 feature/worktree < start/status/doctor 的先後關係;
#     `_templates/6-implementation-notes.md` 步 0 要有獨立逐字欄
#     `FORK_INTEGRATION_SHA: <40 碼>`;unescape 後全檔禁 `feature/<slug>` 命名。
#   ⑨(B-2a)模板頂註「什麼時候/誰改」交接表:ship 那一列的 actor 儲存格,
#     粗體 actor 必須逐字是「合併那個 PR 的人」,且格內不得出現粗體 owner。
#   ⑩(B-2b)docs/dev/STATUS.md 沒有交接表:只取頂註「ship 移出 Active 由…
#     在合併之後」那一句,actor 片語必須含「合併那個 PR 的人」且不含 owner
#     —— 不在整份頂註找散落的「移出/Active/合併/PR」(那樣改成 owner 照樣全中)。
#   ⑪~⑬(C-2)直接補修判準的三個正本分開 scoped:
#     ⑪ README §7 算法段:判定順序鏈(fetch 釘整合分支 < Stage 1–5 sentinel 等值
#       才跳過 < Stage 6 一律 fail-closed < Stage 7 才進 mode/ref/SHA < rev-parse
#       釘 remote-tip < pinned tree 讀 5-tasks 與 6-notes < execution.mode <
#       --is-ancestor < 聯集 < 補修者 checkout clean/無 ahead)用 index 比序;
#       兩個 git show 必須讀同一個 <remote-tip>(中途重 resolve 就是兩份文件
#       可能來自不同 SHA);「不是 Lane 欄」「不要求 SHA 相等」「不得只查最新
#       一個」「parallel fail-closed」逐一釘住。
#     ⑫ skills/dev-run/SKILL.md 發布紀律:sequential 收尾 push 的位置必須在
#       bookkeeping 之後、stop/回報之前;parallel 在 integration 合回 feature
#       之後、回報之前;兩邊都要有 fetch 後 remote tip == feature HEAD 驗證與
#       「失敗不得宣稱 Stage 6 完成」—— 用順序鏈驗位置,不是只找 push 字。
#     ⑬ _templates/STATUS.md Branch 段:兩段式發布都要在(起手=建立可查座標、
#       不代表執行中 remote 完整;Stage 6 收尾由 dev-run 再發布最終 tip)。
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
readme = read("README.md")
devrun = read("skills/dev-run/SKILL.md")

# ①規則要點對帳:每個要點 = 一組必須同時出現的關鍵詞(不比逐字)。
# 「ship 移出由誰做」原本也在這裡(["移出","Active","合併"]),但關鍵詞裡沒有任何
# 一個指向 actor —— 把「合併那個 PR 的人」改成「owner」三個詞照樣全中(B-2)。
# 已升級成⑨⑩的 scoped 斷言(兩個受測面結構不同,分開釘),不在此保留弱版並存。
POINTS = [
    ("只在整合分支維護", ["只在整合分支", "不碰本檔"]),
    ("改前 pull --ff-only", ["pull --ff-only"]),
    ("push 被拒走 rebase 重放並核對列集合", ["rebase", "列集合"]),
    ("禁 force push / reset --hard", ["push --force", "reset --hard"]),
    # 「窗口最短」= 寫入紀律真正要的東西;「立刻 commit」只是達成它的手段之一。
    # 母版原本把手段寫成規則(在有護欄擋直接 commit 的專案上會變成「照做就違規」),
    # 拆成「動作/落點」兩層之後,能被機械釘住的就只剩這個目的本身 —— 沒有這一條,
    # 今天有人把整段寫入紀律刪掉只留 pull/rebase/force 三條,本守衛照樣全綠。
    ("寫入窗口最短", ["窗口最短"]),
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
    # B-3:sentinel 必須驗「範例列 Branch 那一格」本身。全檔(甚至全模板)搜尋都不行 ——
    # 頂註填法說明裡也有同字串,把範例格改壞照樣綠。
    if "Branch" in header:
        idx = header.index("Branch")
        got = sample[idx] if idx < len(sample) else "<缺格>"
        if got != "n-a:尚未建立 branch":
            fails.append("範例列 Branch 格必須逐字 = `n-a:尚未建立 branch`"
                         f"(實得 `{got}`;頂註說明裡的 sentinel 不算數)")
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


# ⑨⑩(B-2)ship 移出 Active 的「誰做」—— 兩個受測面結構不同,分開 scoped,
# 不能共用一套關鍵詞(頂註別處也有 PR/合併/移出,散落關鍵詞恆真)。
def handoff_actor_failures(template_text):
    """受測面 a:_templates/STATUS.md 頂註「什麼時候/誰改」交接表,取 ship 列 actor 儲存格。
    actor = 格內第一個 **粗體** 標記(表的既有慣例:兩列都以粗體標 actor;
    「他不一定是 owner」是說明文字,不是 actor 指派,所以不能拿裸字串 owner 判)。"""
    pre = preamble(template_text)
    ship_cells = None
    for row in re.findall(r"^>\s*\|(.+)\|\s*$", pre, re.M):
        cells = [c.strip() for c in row.split("|")]
        if len(cells) >= 2 and "ship" in cells[0] and "移出" in cells[0]:
            ship_cells = cells
            break
    if ship_cells is None:
        return ["_templates/STATUS.md 頂註交接表找不到「ship 移出」列(整列/整表被刪也算違規)"]
    actor_cell = ship_cells[1]
    bolds = re.findall(r"\*\*(.+?)\*\*", actor_cell)
    if not bolds:
        return [f"ship 列 actor 儲存格沒有粗體標記的 actor(實得 `{actor_cell}`)"]
    fails = []
    if bolds[0] != "合併那個 PR 的人":
        fails.append(f"ship 列 actor 必須逐字是「合併那個 PR 的人」(實得粗體 actor `{bolds[0]}`)")
    hit = [b for b in bolds if "owner" in b.lower()]
    if hit:
        fails.append(f"ship 列 actor 儲存格出現粗體 owner(實得 {hit})—— 交接正本是 merger")
    return fails


def docs_ship_actor_failures(docs_text):
    """受測面 b:docs/dev/STATUS.md 沒有 actor table —— 只取頂註
    「ship 移出 Active 由…在合併之後」那一句驗責任片語。"""
    flat = re.sub(r"\n>\s*", " ", preamble(docs_text))
    m = re.search(r"ship 移出\s*Active 由(.{0,40}?)在合併之後", flat)
    if not m:
        return ["docs/dev/STATUS.md 頂註找不到「ship 移出 Active 由…在合併之後」責任句"
                "(句子被刪或 actor 片語被改到面目全非都算違規)"]
    actor_seg = m.group(1)
    fails = []
    if "合併那個 PR 的人" not in actor_seg:
        fails.append(f"責任句 actor 必須是「合併那個 PR 的人」(實得 `{actor_seg.strip()}`)")
    if "owner" in actor_seg.lower():
        fails.append(f"責任句 actor 片語出現 owner(實得 `{actor_seg.strip()}`)—— 交接正本是 merger")
    return fails


def forbidden_name_failures(quickstart_text):
    if "feature/<slug>" in html.unescape(quickstart_text):
        return ["unescape 後仍出現 `feature/<slug>`(branch 命名正本是 feat/<slug>)"]
    return []


# ⑪~⑬(C-2)直接補修判準:三個正本分開 scoped,不能只驗 README。
def readme_patch_section(readme_text):
    m = re.search(r"「其他 feature 碰過的檔」的定義(.*?)revert 之後的坑",
                  readme_text, re.S)
    return m.group(1) if m else None


def readme_patch_failures(readme_text):
    """⑪ README 算法段:順序鏈 + 關鍵判準逐一釘住,只在算法段內找(scoped)。"""
    sec = readme_patch_section(readme_text)
    if sec is None:
        return ["README 找不到直接補修算法段(「其他 feature 碰過的檔」的定義 ~ revert 之後的坑)"]
    fails = chain_failures(sec, [
        ("fetch 後先釘整合分支 SHA", r"`git fetch` 後先把\*\*整合分支\*\*釘成 SHA"),
        ("Stage 1–5 sentinel 逐字等值才跳過", r"Stage 1–5 且 `Branch` 欄逐字等於 `n-a:尚未建立 branch` 才跳過"),
        ("Stage 6 一律 fail-closed", r"Stage 6 一律 fail-closed"),
        ("只有 Stage 7 才進 mode/ref/SHA 驗證", r"只有 Stage 7 的列才進 mode/ref/SHA 驗證"),
        ("rev-parse --verify 釘 remote-tip", r"rev-parse --verify"),
        ("pinned tree 讀 5-tasks", r"git show <remote-tip>:docs/dev/<slug>/5-tasks\.md"),
        ("pinned tree 讀 6-notes", r"git show <remote-tip>:docs/dev/<slug>/6-implementation-notes\.md"),
        ("mode 資料源 execution.mode", r"`execution\.mode`"),
        ("parallel 一律 fail-closed", r"明寫 `parallel`[\s\S]{0,60}fail-closed"),
        ("Progress Log 每一個 ACCEPTED", r"每一個\*\*[\s\S]{0,20}ACCEPTED"),
        ("merge-base --is-ancestor", r"merge-base --is-ancestor"),
        ("補修者 checkout clean", r"checkout 也必須 clean"),
        ("無 ahead 未推", r"無 ahead 未推"),
        ("不可觀測不准宣稱零交集", r"不准宣稱零交集"),
    ], "README 補修算法")
    for label, token in [
        ("禁讀 main checkout 舊副本", "不准讀目前"),
        ("mode 不是 Lane 欄", "不是 STATUS 的 `Lane` 欄"),
        ("mode 缺省視為 sequential", "缺省視為 `sequential`"),
        ("ancestor 不要求 SHA 相等", "不要求 SHA 相等"),
        ("不得只查最新一個 ACCEPTED", "不得只查最新一個"),
    ]:
        if token not in sec:
            fails.append(f"README 補修算法:缺關鍵判準「{label}」(找不到 `{token}`)")
    tips = re.findall(r"git show ([^:`\s]+):docs/dev/<slug>/", sec)
    if len(tips) != 2 or len(set(tips)) != 1:
        fails.append("兩份文件必須讀同一個 pinned <remote-tip>"
                     f"(實得 {tips};中途重新 resolve = 兩份可能來自不同 SHA)")
    return fails


def devrun_publish_failures(devrun_text):
    """⑫ dev-run 發布紀律:用順序鏈驗 push 的「位置」,不是只找 push 字。"""
    fails = []
    m_seq = re.search(r"## 收尾(.*?)## 並行模式", devrun_text, re.S)
    if not m_seq:
        fails.append("dev-run 找不到 sequential 收尾節(## 收尾 ~ ## 並行模式)")
    else:
        fails += chain_failures(m_seq.group(1), [
            ("bookkeeping commit", r"bookkeeping commit"),
            ("push feature branch", r"push feature branch 到\s*remote"),
            ("fetch 後驗證", r"`git fetch` 驗證"),
            ("remote tip == feature HEAD", r"remote tip 等於當下 feature HEAD"),
            ("失敗不得宣稱 Stage 6 完成", r"不得宣稱 Stage 6 完成"),
            ("stop", r"`devflow-exec\.sh stop`"),
            ("回報進 Stage 7", r"回報使用者進"),
        ], "sequential 收尾")
    m_par = re.search(r"## 並行模式(.*?)## Stage 7 送審前置", devrun_text, re.S)
    if not m_par:
        fails.append("dev-run 找不到並行模式節(## 並行模式 ~ ## Stage 7 送審前置)")
    else:
        fails += chain_failures(m_par.group(1), [
            ("integration 合回 feature branch", r"合回 feature branch"),
            ("push feature branch", r"push feature branch 到\s*remote"),
            ("remote tip == feature HEAD", r"remote tip 等於當下 feature HEAD"),
            ("失敗不得宣稱 Stage 6 完成", r"不得宣稱 Stage 6 完成"),
            ("回報進 Stage 7", r"回報使用者進"),
        ], "parallel 收尾")
    return fails


def status_branch_failures(template_text):
    """⑬ STATUS Branch 段:兩段式發布(起手座標 + Stage 6 收尾最終 tip)都要在。"""
    pre = preamble(template_text)
    m = re.search(r"`Branch` 欄填法:(.*)", pre, re.S)
    if not m:
        return ["_templates/STATUS.md 頂註找不到「`Branch` 欄填法:」段"]
    sec = m.group(1)
    return [f"Branch 段缺「{label}」(找不到 `{token}`)"
            for label, token in [
                ("起手發布=建立可查座標", "建立可查的座標"),
                ("不代表執行中 remote 完整", "不代表執行中的 remote 已經完整"),
                ("Stage 6 收尾再發布最終 tip", "再發布最終"),
                ("正本指向 dev-run 收尾", "skills/dev-run/SKILL.md"),
                ("未發布窗口由 README 算法封住", "負責封住"),
            ] if token not in sec]


print("-- ①規則要點:模板 vs 母版自用 docs/dev/STATUS.md --")
fails = policy_failures(template, docs)
check(not fails, "規則要點兩份都在(整合分支維護/寫入紀律四組;ship actor 由⑨⑩驗)",
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

print("-- ⑨ship 移出的 actor:模板交接表儲存格(B-2a)--")
fails = handoff_actor_failures(template)
check(not fails, "交接表 ship 列粗體 actor 逐字=「合併那個 PR 的人」且無粗體 owner",
      "; ".join(fails))

print("-- ⑩ship 移出的 actor:docs 頂註責任句(B-2b)--")
fails = docs_ship_actor_failures(docs)
check(not fails, "docs 責任句 actor 含「合併那個 PR 的人」且不含 owner",
      "; ".join(fails))

print("-- ⑪直接補修算法:README 順序鏈與 pinned-tree 判準(C-2)--")
fails = readme_patch_failures(readme)
check(not fails, "README:S1–5 sentinel→S6 fail-closed→S7 pinned/ancestor/clean 鏈全對",
      "; ".join(fails))

print("-- ⑫Stage 6 最終發布紀律:dev-run 收尾(C-2)--")
fails = devrun_publish_failures(devrun)
check(not fails, "dev-run:seq 與 parallel 的 push 位置+remote-tip 驗證都在序內",
      "; ".join(fails))

print("-- ⑬STATUS Branch 段兩段式發布(C-2)--")
fails = status_branch_failures(template)
check(not fails, "Branch 段:起手座標與 Stage 6 收尾最終 tip 說明都在",
      "; ".join(fails))

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
mutated_template = template.replace(
    "**合併那個 PR 的人** —— 他不一定是 owner", "**owner**")
check(bool(handoff_actor_failures(mutated_template)),
      "負向⑨:交接表 ship 列 actor 改成 owner(移出/Active/合併三詞都還在)→ 紅")
mutated_docs = docs.replace("由**合併那個 PR 的人**在合併之後", "由 **owner** 在合併之後")
check(bool(docs_ship_actor_failures(mutated_docs)),
      "負向⑩:docs 責任句 actor 改成 owner → 紅")
mutated_template = template.replace("| n-a:尚未建立 branch |", "| feat/x(本地名) |")
check(bool(table_failures(mutated_template)),
      "負向⑪:範例列 Branch 格改別的字、頂註 sentinel 留著(欄數不變)→ 紅"
      "(舊版全檔搜尋在此假綠)")
mutated_readme = readme.replace("Stage 6 一律 fail-closed", "Stage 6 也照 Stage 7 驗")
check(bool(readme_patch_failures(mutated_readme)),
      "負向⑫:README 拿掉 Stage 6 fail-closed → 紅")
mutated_readme = readme.replace("讀出**每一個**", "讀出最新一個").replace(
    "不得只查最新一個", "查最新一個即可")
check(bool(readme_patch_failures(mutated_readme)),
      "負向⑬:README 把「每一個 ACCEPTED」弱化成只查最新一個 → 紅")
m3 = re.search(r"3\. \*\*Stage 6 一律 fail-closed\*\*[\s\S]*?(?=4\. \*\*只有 Stage 7)", readme)
m4 = re.search(r"4\. \*\*只有 Stage 7[\s\S]*?(?=5\. 排除)", readme)
if m3 and m4 and m3.end() <= m4.start():
    mutated_readme = (readme[:m3.start()] + m4.group(0) + m3.group(0)
                      + readme[m4.end():])
else:
    mutated_readme = readme  # 抓不到兩段 = 正向⑪早已紅;讓這條也紅出來
check(bool(readme_patch_failures(mutated_readme)),
      "負向⑭:README Stage 6/Stage 7 判定段倒序(內容都在,只換順序)→ 紅")
mutated_devrun = re.sub(r"\*\*發布最終成果:最後一個 bookkeeping[\s\S]*?不得宣稱 Stage 6 完成\*\*",
                        "", devrun, count=1)
check(bool(devrun_publish_failures(mutated_devrun)),
      "負向⑮:dev-run 刪 sequential 最終 push+驗證段 → 紅")
mutated_devrun = re.sub(r"\*\*發布最終成果:\nintegration 合回[\s\S]*?不得宣稱 Stage 6 完成\*\*",
                        "", devrun, count=1)
check(bool(devrun_publish_failures(mutated_devrun)),
      "負向⑯:dev-run 刪 parallel 最終 push+驗證段 → 紅")
mutated_template = template.replace("再發布最終", "不再另外發布")
check(bool(status_branch_failures(mutated_template)),
      "負向⑰:STATUS Branch 段刪 Stage 6 最終 tip 發布說明 → 紅")
# ⑱⑲:兩份頂註各拿掉一次「窗口最短」——其餘寫入紀律(pull/rebase/force)原封不動,
# 唯一的錯誤是把規則的目的拿掉、只留手段。兩份分開試:只釘一份的話,另一份被刪
# 不會有任何訊號(POINTS 是對兩份各驗一次,負向也要各驗一次才對稱)。
mutated_template = template.replace("**寫入窗口最短**", "**盡快**")
check(bool(policy_failures(mutated_template, docs)),
      "負向⑱:模板頂註拿掉「窗口最短」(其餘寫入紀律都還在)→ 紅")
mutated_docs = docs.replace("**寫入窗口最短**", "**盡快**")
check(bool(policy_failures(template, mutated_docs)),
      "負向⑲:docs 頂註拿掉「窗口最短」→ 紅")

# ── 檢查數地板:防止檢查段/負向 fixture 整段被刪後檢查數靜默縮水仍全綠(B-4)──
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」(同 repo 慣例:
# check-gate-twin.sh、check-dev-setup-discipline.sh 的 MIN_CHECKS);之後每加一條
# 檢查都要同步調高。字面值與這整個 if 區塊(condition+記錄 failure+非零退出鏈)
# 另被 test-architecture-guards.sh 靜態互釘外釘,兩處要同一個 commit 一起改。
MIN_CHECKS = 32
if CHECKS < MIN_CHECKS:
    FAILED += 1
    print(f"  ✗ 檢查數地板:實際只跑了 {CHECKS} 項(地板 {MIN_CHECKS})—— "
          f"檢查段或負向 fixture 被刪掉或迴圈跑了零圈,這比單項失效更嚴重")

print()
if FAILED:
    print(f"⛔ STATUS 規則對帳:{FAILED}/{CHECKS} 失敗")
    sys.exit(1)
print(f"✅ STATUS 規則對帳:全過({CHECKS} 項)")
PY
