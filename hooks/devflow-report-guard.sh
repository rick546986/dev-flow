#!/bin/bash
# devflow-report-guard.sh — PostToolUse(Edit|Write):缺陷回報檔的去識別化守衛。
# 只掃 `.devflow/reports/*.md`(dev-report skill 的產出位置);**其餘路徑一律
# 靜默放行** —— 這條錯了會變成「裝了 plugin 就不能寫任何檔」。
# 抓結構性識別特徵(絕對路徑/git SHA/email/內網位址/分支名/不存在於母版的路徑);
# 語意識別資訊(公司名、業務術語)沒有結構特徵,hook 抓不到 —— 那半靠 skill 白名單
# 與產出前人工確認,兩層缺一不可。fail-open 於環境問題(空輸入/壞 JSON → 放行)。
# ⚠️ payload 走 stdin 直通 python,殼層不碰內容(F2:env 傳遞撞 ARG_MAX → rc=126
# 靜默自壞;見 devflow-guard.sh 同註與 devflow-lib.py read_hook_input())。
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
. "$(dirname "$0")/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
exec "$DEVFLOW_PY" "$(dirname "$0")/_report_impl.py" "$ROOT"
