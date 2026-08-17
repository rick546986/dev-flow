#!/bin/bash
# devflow-prebash.sh — PreToolUse(Bash):擋掉 shell 繞過的兩類動作 ——
# ①讀上游討論檔(圍欄②的 Bash 破口)②破壞守衛狀態(rm 旗標 / 直寫 exec.json)。
# 治標不治本(shell 語意無法窮舉),但堵掉隨手可為的低成本繞過。
# ⚠️ payload 走 stdin 直通 python,殼層不碰內容(F2:env 傳遞撞 ARG_MAX → rc=126
# 靜默自壞;見 devflow-guard.sh 同註與 devflow-lib.py read_hook_input())。
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
exec /usr/bin/python3 "$(dirname "$0")/_prebash_impl.py" "$ROOT"
