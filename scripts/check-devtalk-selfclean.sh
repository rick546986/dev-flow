#!/bin/bash
# check-devtalk-selfclean.sh — 母版自己的 dev-talk 產物必須過母版自己的盲原則守衛
# (B-1/G2 同型通解,2026-08-17)。
#
# 為什麼需要:「母版自己的產物過不了母版自己的守衛」已發生兩次 ——
#   B-1:母版的 _templates/5-tasks.md 過不了 parse_5_tasks;
#   G2:skills/dev-talk/SKILL.md 頂部的版本沿革註解含下游字眼,任何人一改該檔
#       就被 devtalk-guard 擋死(guard 只在寫入時觸發,所以平常看不出來)。
# 同一型出現兩次 = 需要機械層,不是逐次修文字。本守衛把「寫入時才會發現」變成
# 「每次 devflow-check 都先驗」:對 skills/dev-talk/ 底下**每一個檔**餵一次
# 真的 devtalk-guard(不複製它的字詞表 —— 複製 = 雙正本,守衛改了這裡就漂移)。
#
# exit code:0 = 全部檔案過 guard;1 = 任一檔被 guard 擋(列出 guard 原話);
# 2 = 掃到 0 檔或 guard 腳本缺失(fail-closed)。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
GUARD="$ROOT/hooks/devtalk-guard.sh"
DIR="$ROOT/skills/dev-talk"

[ -f "$GUARD" ] || { echo "FATAL: 找不到 $GUARD(守衛本體缺失)" >&2; exit 2; }
[ -d "$DIR" ]   || { echo "FATAL: 找不到 $DIR" >&2; exit 2; }

COUNT=0
BAD=0
while IFS= read -r f; do
  COUNT=$((COUNT + 1))
  OUT=$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s"}}' "$f" \
        | bash "$GUARD" 2>&1); RC=$?
  if [ "$RC" -ne 0 ]; then
    BAD=$((BAD + 1))
    echo "❌ $f 過不了 devtalk-guard(rc=$RC)—— 改這個檔就會被自己的守衛擋死:"
    printf '%s\n' "$OUT" | sed 's/^/   /'
  fi
done < <(find "$DIR" -type f | sort)

if [ "$COUNT" -eq 0 ]; then
  echo "FATAL: skills/dev-talk/ 掃到 0 檔 —— 不是「全乾淨」,是目錄空了" >&2
  exit 2
fi

echo "=== dev-talk 自淨檢查:$COUNT 檔全部餵過真的 devtalk-guard ==="
if [ "$BAD" -ne 0 ]; then
  echo "⛔ $BAD 檔被擋 —— 母版自己的產物過不了母版自己的守衛(B-1/G2 型)。"
  echo "   修法:把含下游字眼的內容移到不受掃描的位置(例:docs/PLUGIN.md),"
  echo "   不要放寬 guard 字詞表(放寬 = 真洩漏也放行)。"
  exit 1
fi
echo "✅ 全過(guard 字詞表單一正本,本檢查直接執行 guard 本體,不另抄一份)"
