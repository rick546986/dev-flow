#!/bin/bash
# 反水平切層 —— **Warning-only heuristic**(不是 Gate,不是硬性檢查)。
#
# 為什麼只做 warning:Stage 5「禁整份按 DB→Repo→Service→API→UI 逐層分 T」的判準
# 已寫在 `_templates/5-tasks.md`,由人工/fresh reviewer 判。機械判斷會誤傷合法的
# 純 Migration／Infrastructure Task,所以本腳本**只提示、不阻擋**。
#
# 啟發式(兩個條件同時成立才算可疑,且要「大多數 T」都可疑才出 WARNING):
#   ①Task 標題去掉填充詞後,剩下的 token **全部**是架構層名詞
#     (DB / Database / Repository / Service / API / Controller / UI / Frontend / Migration / Schema)。
#   ②Task 的 `Intent:` 缺漏、或找不到行為動詞/可觀測結果的訊號。
#   → 可疑 T 數 > 總 T 數的一半 → `WARNING: possible horizontal task slicing`。
#
# 抑制方式(合法的純架構 Task 怎麼避免被念):把 `Intent:` 寫成「做完系統/使用者多了
# 什麼可觀測行為」—— 這本來就是模板要求的寫法。純 migration Task 只要 Intent 說得出
# 可觀測結果(例如「既有 8k 筆合約可標狀態」),就不會被標記。
#
# **exit code 契約(重要)**:
#   對真實 5-tasks.md 的判斷**一律 warning-only,永遠不會 exit 1**。
#   本腳本唯一會 exit 1 的情況是**自我測試 battery 失敗**(啟發式本身壞掉 / fixture 不見),
#   那不是 warning,是守衛自己故障。
#
# 用法:
#   scripts/check-task-slicing.sh [root]        # 掃 root 的 example/*/5-tasks.md + fixture battery
#   scripts/check-task-slicing.sh --scan FILE   # 只評一份 5-tasks.md;印判定,exit 一律 0

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

SCAN_FILE=""
if [ "${1:-}" = "--scan" ]; then
  if [ -z "${2:-}" ]; then
    echo "usage: $0 --scan <5-tasks.md>" >&2
    exit 2
  fi
  SCAN_FILE="$2"
elif [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

# evaluate <file> → stdout 最後一行是 VERDICT=warn|ok|unreadable
evaluate() {
  python3 - "$1" <<'PY'
import os
import re
import sys

path = sys.argv[1]
if not os.path.isfile(path):
    print(f"  ✗ 讀不到:{path}")
    print("VERDICT=unreadable")
    raise SystemExit(0)

with open(path, encoding="utf-8") as stream:
    text = stream.read()

ARCH = {"db", "database", "repository", "repo", "service", "api", "controller",
        "ui", "frontend", "migration", "schema"}
FILLER = {"層", "實作", "建立", "新增", "相關", "部分", "與", "和", "的", "做",
          "layer", "layers", "impl", "implementation", "setup", "add", "create",
          "build", "wire", "wiring"}
# 「可觀測結果」訊號:做完之後看得到什麼。刻意不含「建立/實作」這類純動作詞。
OBSERVABLE = ["使用者", "系統多了", "多了", "可觀測", "顯示", "看到", "回傳", "輸出",
              "拒絕", "歷程", "新增一筆", "能夠", "可查", "可標", "可點", "畫面",
              "卡片", "回應", "回 200", "回 403", "端到端", "走完", "log",
              "observable", "user", "returns", "shows", "responds"]

blocks = re.split(r"(?=^## T-\d+)", text, flags=re.M)[1:]
suspicious = []
detail = []
for block in blocks:
    title_match = re.match(r"## (T-\d+)\s*(.*)", block)
    task_id = title_match.group(1)
    title = title_match.group(2).strip()
    intent_match = re.search(r"^- Intent:\s*(.*)$", block, re.M)
    intent = intent_match.group(1).strip() if intent_match else ""

    tokens = [t for t in re.split(r"[^0-9A-Za-z一-鿿]+", title) if t]
    meaningful = [t for t in tokens if t.lower() not in FILLER and t not in FILLER]
    arch_only = bool(meaningful) and all(t.lower() in ARCH for t in meaningful)

    intent_weak = (not intent) or intent in {"—", "-", "TBD"} or not any(
        marker in intent for marker in OBSERVABLE)

    if arch_only and intent_weak:
        suspicious.append(task_id)
        detail.append(f"      {task_id} 「{title}」— 標題僅架構層名詞;Intent 無可觀測結果訊號")

total = len(blocks)
print(f"  • {path}: {total} 個 T,{len(suspicious)} 個可疑")
for line in detail:
    print(line)

if total and len(suspicious) * 2 > total:
    print(f"  WARNING: possible horizontal task slicing "
          f"({len(suspicious)}/{total} 個 T 標題只有架構層名詞且 Intent 無可觀測結果)")
    print("           這是提示不是判決 —— 機械判斷不能取代 Reviewer。"
          "純 Migration／Infrastructure Task 合法,把 Intent 寫成可觀測結果即可。")
    print("VERDICT=warn")
else:
    print("VERDICT=ok")
PY
}

if [ -n "$SCAN_FILE" ]; then
  evaluate "$SCAN_FILE"
  exit 0
fi

echo "=== 反水平切層 heuristic(warning-only,永不因 warning 退非零)==="
FAILED=0

echo "-- 真實掃描(repo 內的 5-tasks 範例)--"
shopt -s nullglob
REAL=("$ROOT"/example/*/5-tasks.md)
if [ ${#REAL[@]} -eq 0 ]; then
  echo "  • 無 example/*/5-tasks.md,略過真實掃描"
else
  for file in "${REAL[@]}"; do
    evaluate "$file" | grep -v '^VERDICT='
  done
fi

echo "-- fixture battery(啟發式自我測試;失敗才 exit 1)--"
battery() {
  local file="$1" expect="$2" label="$3"
  local out got
  out=$(evaluate "$SELF_DIR/fixtures/task-slicing/$file")
  got=$(printf '%s\n' "$out" | grep '^VERDICT=' | cut -d= -f2)
  if [ "$got" = "$expect" ]; then
    echo "  ✓ $label:如預期 $expect"
  else
    echo "  ✗ $label:預期 $expect,實得 $got"
    printf '%s\n' "$out" | sed 's/^/      /'
    FAILED=1
  fi
}
battery horizontal-5-tasks.md warn "horizontal fixture(整份按層切,Intent 無可觀測結果)"
battery vertical-5-tasks.md   ok   "vertical fixture(合法垂直切片)"
battery infra-5-tasks.md      ok   "infra fixture(合法純 Migration/Infrastructure,Intent 寫得出可觀測結果)"

echo
if [ "$FAILED" -ne 0 ]; then
  echo "⛔ 反水平切層 heuristic:自我測試失敗(啟發式壞掉,不是 warning)"
  exit 1
fi
echo "✅ 反水平切層 heuristic:自我測試全過(warning 本身不影響 exit code)"
exit 0
