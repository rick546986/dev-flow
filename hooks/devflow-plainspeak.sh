#!/bin/bash
# devflow-plainspeak.sh — UserPromptSubmit hook:每輪提醒模型「用看得懂的話回」。
#
# 為什麼需要:dev-flow 的三個關卡(G1/G2/G3)把判斷交給人,但人要判斷得先看得懂。
# 母版已經解掉「東西太多不知從哪審」(README §6 動線頂區、待審逐條可勾、背景摺疊),
# 沒解掉的是「內容太技術,看得到但判斷不了」。輸出風格設定只在 session 開頭讀一次,
# context 一長就淡掉;掛在 UserPromptSubmit 的話每一輪都會重新注入一次。
#
# 規則文字的正本 = 同目錄 plainspeak-rules.md 的 inject 區塊,本檔不自帶副本。
#
# **預設關閉**:採用 dev-flow 的專案不見得講中文,不能替別人決定回覆語言。
# 要開:在 .claude/settings.json 的 "env" 區塊或 shell 環境設 DEVFLOW_PLAINSPEAK=1。
# 未設 = 什麼都不做、exit 0,對其他人零影響。
#
# exit code:一律 0(這支只注入提醒,不擋任何東西;擋 prompt 不是它的職責)。
set -u

if [ "${DEVFLOW_PLAINSPEAK:-0}" != "1" ]; then
  exit 0
fi

# stdin 的 hook payload 用不到(本支不看使用者輸入內容),讀掉避免上游 SIGPIPE。
cat >/dev/null 2>&1 || true

. "$(dirname "$0")/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
exec "$DEVFLOW_PY" "$(dirname "$0")/_plainspeak_impl.py"
