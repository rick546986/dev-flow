#!/bin/bash
# history-guard.sh — dev-flow plugin 內建:改版歷史索引的單一寫入口守衛(PreToolUse hook)。
#
# 擋什麼:用 Edit / Write 直接改 `docs/dev/HISTORY.md`。
# 為什麼:那個檔可能同時有多個 session 在寫。Edit/Write 是「讀整檔 → 改 → 寫回」,
#         兩個 session 交錯時後寫的會把先寫的整段蓋掉,而且**不會有任何錯誤訊息**。
#         正確寫入口是 `scripts/history-append.sh`(目錄鎖 + 重試 + 純追加)。
#
# 不擋什麼(以下一律靜默放行,exit 0):
#   - 任何其他檔案(含 `_templates/HISTORY.md` 這份格式樣板本身)
#   - Read
#   - 經由 Bash 執行的 `history-append.sh`(hook 攔的是 Edit/Write 工具,不攔 shell)
#
# fail-open 的理由:本守衛只防「並發覆寫」這一種失誤,不是安全邊界。
#   讀不到輸入、解析不出路徑時一律放行 —— 讓一支輔助守衛有能力擋住全部寫入,
#   比它想防的問題更危險。
set -u

. "$(dirname "$0")/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)

INPUT=$(cat 2>/dev/null) || exit 0
[ -n "$INPUT" ] || exit 0

FILE=$(printf '%s' "$INPUT" | "$DEVFLOW_PY" -c "import json,sys
try: print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))
except Exception: pass" 2>/dev/null)

[ -n "$FILE" ] || exit 0

case "$FILE" in
  */docs/dev/HISTORY.md) : ;;
  *) exit 0 ;;
esac

{
  echo "⛔ history-guard:不要用 Edit/Write 直接改 docs/dev/HISTORY.md。"
  echo ""
  echo "   理由:同一個專案可能同時有多個 session 在寫這個檔。Edit/Write 會整檔寫回,"
  echo "   兩邊交錯時後寫的會把先寫的那筆整段蓋掉,而且不會報錯。"
  echo ""
  echo "   請改用唯一寫入口(目錄鎖 + 重試 + 純追加)。它在哪:"
  echo "     採用專案  → docs/dev/tools/history-append.sh(dev-setup 散發)"
  echo "     方法論母版 → scripts/history-append.sh"
  echo ""
  echo "     <上面那支> --slug <代號> --what <做了什麼> \\"
  echo "                --why <為什麼> --where <落在哪> \\"
  echo "                [--version vX.Y.Z] [--adr NNNN] [--detail <連結>]"
  echo ""
  echo "   先看要寫出什麼再決定:加 --dry-run 只印不寫。"
  echo "   歷史是只增不改的 —— 要修正舊條目,追加新的一筆並註明推翻了哪一筆。"
} >&2
exit 2
