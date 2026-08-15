#!/bin/bash
# README master-only 標記守衛(MED-4,第二批獨立審查):`<!-- devflow:master-only:start -->`
# 與 `<!-- devflow:master-only:end -->` 必須數量相等、逐一配對(每個 start 之後最近
# 出現的一個 marker 必須是 end),不得巢狀/交錯。
#
# 起因:skills/dev-setup/SKILL.md 的 install/upgrade/check 全靠
#   sed -n '/<!-- devflow:master-only:start -->/,/<!-- devflow:master-only:end -->/!p'
# 抽 README.md 裡「純母版導覽、對採用專案是死引用」的區塊。若這對標記不對稱
# (例如少了一個 end、或不慎巢狀重覆 start),sed range 會靜默抽到檔尾或抽出錯誤
# 內容 —— 沒有任何報錯,採用專案落地的 docs/dev/README.md 就此帶著錯誤內容。
# 本守衛不管內容,只驗標記本身的配對形狀。
#
# 用法:
#   scripts/check-readme-markers.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供負向 mutation 驗證
# (test-architecture-guards.sh 的 MM-* 案)。

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import re
import sys

root = sys.argv[1]
path = os.path.join(root, "README.md")
if not os.path.isfile(path):
    print(f"⛔ README master-only 標記守衛:README.md 不存在({path})")
    raise SystemExit(1)

with open(path, encoding="utf-8") as fh:
    text = fh.read()

START = "<!-- devflow:master-only:start -->"
END = "<!-- devflow:master-only:end -->"

markers = []
for m in re.finditer(re.escape(START) + "|" + re.escape(END), text):
    kind = "start" if m.group(0) == START else "end"
    line = text.count("\n", 0, m.start()) + 1
    markers.append((kind, line))

n_start = sum(1 for k, _ in markers if k == "start")
n_end = sum(1 for k, _ in markers if k == "end")

print("=== README master-only 標記守衛 ===")
print(f"  • start 標記數:{n_start}")
print(f"  • end   標記數:{n_end}")

checks = 0
problems = []


def check(condition, label, detail=""):
    global checks
    checks += 1
    if not condition:
        problems.append(label + (f":{detail}" if detail else ""))


check(n_start == n_end, "start/end 數量不相等",
      f"{n_start} 個 start、{n_end} 個 end" if n_start != n_end else "")

# 0/0 在「數量相等」的字面意義下算平衡,但這是同一種靜默毀損的更重版本:
# 整組 master-only 標記被刪掉時,SKILL.md 的 sed `!p` 抽取管線變成無操作
# (印出整份檔案),母版限定的內容會原樣灌進採用專案的 docs/dev/README.md,
# 而不是被剝除 —— 不能因為「0 對」在數學上平衡就放行。
check(not (n_start == 0 and n_end == 0), "start/end 標記整組消失(0 對)",
      "sed 剝除管線會變成無操作,母版限定內容會原樣流入採用專案"
      if (n_start == 0 and n_end == 0) else "")

nested_msgs = []
orphan_msgs = []
open_since = None
for kind, line in markers:
    if kind == "start":
        if open_since is not None:
            nested_msgs.append(
                f"第 {line} 行出現 start,但第 {open_since} 行的 start 還沒被 end 閉合")
        else:
            open_since = line
    else:  # end
        if open_since is None:
            orphan_msgs.append(f"第 {line} 行的 end 沒有對應的 start(多餘,或成對順序錯亂)")
        else:
            open_since = None

check(not nested_msgs,
      "巢狀/交錯的 start(禁止:每個 start 後最近的 marker 必須是 end)",
      "; ".join(nested_msgs))
check(not orphan_msgs, "end 缺對應的 start", "; ".join(orphan_msgs))
check(open_since is None, "start 未被 end 閉合(未閉合 —— sed 抽取會靜默跑到檔尾)",
      f"第 {open_since} 行的 start 沒有對應的 end" if open_since is not None else "")

# ── 檢查數地板(N-2,2026-08-15)────────────────────────────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」——地板留餘裕=沒有牙齒
# (同 repo 慣例:scripts/check-stage67-enforcement.sh:232、
# scripts/test-architecture-guards.sh 的 EXPECTED_TOTAL)。上面 5 條規則(數量相等/
# 非全消失/無巢狀/無孤兒 end/無未閉合 trailing)是結構固定的規則數,不隨檔案裡
# 實際有幾對標記而變動 —— 刪掉整段規則(例如巢狀/孤兒偵測那個迴圈連同兩條 check())
# 之前沒有任何東西會發現「斷言區塊不見了」,守衛照樣可能印全過。
# 新增/刪除規則時把這個數字一起調。
MIN_CHECKS = 5
if checks < MIN_CHECKS:
    problems.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                     f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

if problems:
    print()
    for p in problems:
        print(f"  ✗ {p}")
    print()
    print("⛔ README master-only 標記守衛:FAILED")
    raise SystemExit(1)

print(f"  ✓ {n_start} 對標記皆配對、無巢狀/交錯(檢查數 {checks}/{MIN_CHECKS})")
print()
print("✅ README master-only 標記守衛:全過")
PY
