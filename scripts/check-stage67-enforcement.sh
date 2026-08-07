#!/bin/bash
# Stage 6/7 執行期強制條款守衛(Repo-local,REPO_REFERENCE only)。
#
# 起因(2026-08 order-intake 真實執行,26 個 T 全程):四條「寫在散文裡、沒有任何
# 機械檢查」的規則同時失效,而每一份產出看起來都完整:
#
#   A1 守衛沉睡  `.devflow/exec.json` 不存在時 guard hook 直接 sys.exit(0)
#                (devflow-lib.py::load_state 註解原文「真的沒在執行 → 沉睡」)。
#                該 feature 因 devflow-exec.sh 啟動失敗(D-9)從未武裝 →
#                圍欄②/契約防篡改/scope 三道全程沒觸發,沒有任何訊號。
#   A3 Verify 假綠 `-run '<pattern>'` 沒匹配到測試時 runner 回 exit 0。實測 T-25 的
#                Verify 在還沒寫任何測試的 HEAD 上跑出 `=== RUN` 0 行、exit 0、
#                並印出 `T-25 PASS`。
#   A4 gauntlet 路徑 模板寫死 `docs/dev/tools/...`,該目錄在採用專案不存在 →
#                Evidence 層靜默跳過,7-review 照樣填得完。
#   A5 觀測不可執行 4-spec 的觀測欄可以寫「前端畫面」,而前端在另一 repo 且未實作 →
#                7-review 步 2b 的「現象證據逐 S 相符」(PASS 條件之一)結構上做不到,
#                到 G3 才發現。
#
# 本守衛不判斷內容好壞,只驗「模板與範例有沒有把這四條變成可查的硬條款」。
# 邊界:本檔只掃**本 repo 的模板與範例**;採用專案的 runtime 強制屬外部 plugin。
#
# 用法:
#   scripts/check-stage67-enforcement.sh [root]   # 缺省 = repo root
#
# 退出碼:0 = 全過;1 = 有條款缺失(逐條列出);2 = 用法錯誤。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  case "$1" in
    -h|--help|help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; } ;;
  esac
fi

python3 - "$ROOT" <<'PY'
import os
import re
import sys

root = sys.argv[1]
fails = []
checks = 0


def read(rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def need(cond, msg):
    """cond 為 False 即記一條失敗。每呼叫一次算一項檢查。"""
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


# ── A1:守衛武裝自檢必須寫進 Stage 6 與 Stage 7 的步 0 ────────────────────────
#
# needle 選「守衛武裝自檢」與 `.devflow/exec.json` 兩個字面:前者是條款名(人找得到),
# 後者是**它為什麼存在的根因**(拿掉根因就只剩一句沒有牙齒的提醒)。
for rel in ("_templates/6-implementation-notes.md", "_templates/7-review.md"):
    src = read(rel)
    need(src is not None, f"A1:{rel} 不存在")
    if src is None:
        continue
    need("守衛武裝自檢" in src,
         f"A1:{rel} 的執行清單缺「守衛武裝自檢」硬關卡 —— "
         f"守衛沒武裝與沒在用 dev-flow 在系統裡長得一模一樣")
    need(".devflow/exec.json" in src,
         f"A1:{rel} 沒寫出根因 `.devflow/exec.json`(guard 靠它判斷要不要醒)")
    need("devflow-exec.sh status" in src,
         f"A1:{rel} 沒給可執行的自檢指令 `devflow-exec.sh status`")

# ── A3:Verify 的篩選器假綠 ──────────────────────────────────────────────────
src = read("_templates/5-tasks.md")
need(src is not None, "A3:_templates/5-tasks.md 不存在")
if src:
    need("=== RUN" in src,
         "A3:_templates/5-tasks.md 沒給「數案例數」的具體做法(缺 `=== RUN` 骨架)")
    need(re.search(r"-run.{0,40}(沒匹配|零匹配|沒有匹配)", src, re.S) is not None
         or "篩選器" in src,
         "A3:_templates/5-tasks.md 沒說明「篩選器沒匹配也回 exit 0」這個假綠來源")
    need("原樣跑一次" in src,
         "A3:_templates/5-tasks.md 缺「Verify 開工前原樣跑一次」的條款 —— "
         "少了它,不可能綠/已經綠的 Verify 欄要到做完才發現")

# ── A3 的範例承接:範例必須示範正確做法,不能自己違規 ─────────────────────────
#
# 這一項是「守衛跑得過 ≠ 擋得住」的關鍵:條款只寫在模板註解裡沒人照做,
# 範例才是實際被抄的東西。
for base, _dirs, files in os.walk(os.path.join(root, "example")):
    if "5-tasks.md" not in files:
        continue
    rel = os.path.relpath(os.path.join(base, "5-tasks.md"), root)
    with open(os.path.join(base, "5-tasks.md"), encoding="utf-8") as fh:
        body = fh.read()
    for line in body.splitlines():
        if not line.startswith("- Verify:"):
            continue
        # 只管真的用了篩選器的行
        if not re.search(r"(?<![\w-])(-run|-k|--filter)(?![\w-])", line):
            continue
        need("=== RUN" in line or "grep -c" in line,
             f"A3:{rel} 的 Verify 用了測試篩選器卻沒有案例數斷言 —— "
             f"沒匹配到測試時 runner 回 exit 0,該欄退化成「測試不存在也算過」:\n"
             f"        {line.strip()}")

# ── A4:gauntlet 路徑不得寫死成採用專案不存在的路徑 ──────────────────────────
src = read("_templates/7-review.md")
need(src is not None, "A4:_templates/7-review.md 不存在")
if src:
    need("docs/dev/tools/devflow-evidence-gauntlet.sh" not in src,
         "A4:_templates/7-review.md 把 gauntlet 路徑寫死成 "
         "`docs/dev/tools/devflow-evidence-gauntlet.sh` —— 該目錄在採用專案不存在,"
         "那一步會**靜默跳過**而 7-review 仍填得完")
    need("test -x" in src,
         "A4:_templates/7-review.md 沒要求開工前確認 gauntlet 真的存在(缺 `test -x`)")
    need("降級" in src,
         "A4:_templates/7-review.md 沒規定「裝不了就明記為降級」—— "
         "沒有這條就會默默當成跑過")
    # 母版必須真的在 scripts/,否則上面那句安裝指引也是空的
    need(os.path.exists(os.path.join(root, "scripts/devflow-evidence-gauntlet.sh")),
         "A4:母版 scripts/devflow-evidence-gauntlet.sh 不存在,安裝指引指向空氣")

# ── A5:觀測方式必須在本 repo 可執行 ─────────────────────────────────────────
spec = read("_templates/4-spec.md")
need(spec is not None, "A5:_templates/4-spec.md 不存在")
if spec:
    need("觀測方式必須在本 repo 可執行" in spec,
         "A5:_templates/4-spec.md 的觀測欄沒規定「必須在本 repo 可執行」—— "
         "寫下做不到的觀測 = 在 G2 就種下一個 G3 必然的 ❌")
    need(re.search(r"觀測[^\n]{0,80}n-a", spec) is not None
         or "標 `n-a:" in spec,
         "A5:_templates/4-spec.md 沒給「做不到時當場標 n-a 並補替代觀測」的出口")
rev = read("_templates/7-review.md")
if rev:
    need("結構上做不到" in rev,
         "A5:_templates/7-review.md 的現象證據節沒呼應「觀測指向本 repo 之外時」的處置")

# ── 檢查數地板:防止有人把上面整段刪成空迴圈仍然 exit 0 ──────────────────────
# ⚠️ 這個數字必須**等於當下的實際檢查數**,不是「大概抓個下限」。
# 負向測試 S67-6 實測:原本填 16(A1 那組恰好 8 項,24-8=16)→ 刪掉整組 A1 之後
# 剛好等於地板,守衛照樣 exit 0。地板留餘裕 = 地板沒有牙齒。
# 新增檢查時把這個數字一起往上調(同 test-architecture-guards.sh 的 EXPECTED_* 體例)。
MIN_CHECKS = 24
if checks < MIN_CHECKS:
    fails.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                 f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

if fails:
    print(f"⛔ check-stage67-enforcement: {len(fails)} 條失敗(共跑 {checks} 項)")
    for f in fails:
        print(f"  ❌ {f}")
    raise SystemExit(1)

print(f"✅ check-stage67-enforcement: Stage 6/7 四條強制條款齊({checks} 項檢查全過)")
print("   A1 守衛武裝自檢 / A3 Verify 案例數斷言 / A4 gauntlet 路徑 / A5 觀測可執行性")
PY
