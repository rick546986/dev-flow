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
# 驗三件:
#   ①模板頂註的規則要點(整合分支維護/不碰/merger 移出/寫入紀律)在
#     `docs/dev/STATUS.md` 也存在 —— 釘「要點都在」,不比逐字(兩份用途不同,
#     硬釘逐字會天天假紅)
#   ②`_templates/STATUS.md` Active 表頭含 `Branch` 欄,表頭/分隔列/範例列欄數一致,
#     範例列帶 sentinel `n-a:尚未建立 branch`(逐字,機械判定用)
#   ③`guides/guide-quickstart.html` 的手寫 STATUS 範例列欄數 = 模板表頭欄數
# 並各帶內建負向 fixture(把三件各改壞一次,守衛必須紅 —— 不紅就是白做)。
#
# 掛載:scripts/devflow-check.sh group_architecture()。
# 用法:scripts/check-status-policy.sh(無參數)
# exit:0 = 全過 / 1 = 有 FAIL / 2 = 環境或解析失敗(fail-closed)
set -uo pipefail

[ $# -eq 0 ] || { echo "usage: $0(無參數)" >&2; exit 2; }
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

DEVFLOW_ROOT="$ROOT" python3 - <<'PY'
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

print()
if FAILED:
    print(f"⛔ STATUS 規則對帳:{FAILED}/{CHECKS} 失敗")
    sys.exit(1)
print(f"✅ STATUS 規則對帳:全過({CHECKS} 項)")
PY
