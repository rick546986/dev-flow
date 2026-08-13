#!/bin/bash
# devtalk-guard.sh — dev-flow plugin 內建:dev-talk 盲原則守衛(PostToolUse hook)
# 單一正本(隨 plugin 走,兩帳號共用同一 local plugin 目錄)。
# 行為:非 skills/dev-talk/ 路徑靜默放行;dev-talk 檔案寫入後跑洩漏掃描,
#       命中 → exit 2(stderr 回饋給模型要求立即修正)。
INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | /usr/bin/python3 -c "import json,sys
try: print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))
except Exception: pass" 2>/dev/null)
case "$FILE" in
  */skills/dev-talk/*) : ;;
  *) exit 0 ;;
esac
[ -f "$FILE" ] || exit 0
LEAK=$(grep -nE "dev-flow|2-decision|4-spec|5-tasks|7-review|G1|G2|G3|gate|twin|pipeline|規劃|plan" "$FILE" 2>/dev/null)
if [ -n "$LEAK" ]; then
  {
    echo "⛔ devtalk-guard:盲原則洩漏 —— 剛寫入的 dev-talk 檔案含下游階段字眼(不得出現):"
    echo "$LEAK"
    echo "請立即修正該檔(移除相關字眼);若判定為誤報,回報使用者裁決。"
  } >&2
  exit 2
fi
exit 0
