#!/bin/bash
# devflow-plainspeak.sh — UserPromptSubmit hook:每輪提醒模型「用看得懂的話回」。
#
# 為什麼需要:dev-flow 的三個關卡(G1/G2/G3)把判斷交給人,但人要判斷得先看得懂。
# 母版已經解掉「東西太多不知從哪審」(README §6 動線頂區、待審逐條可勾、背景摺疊),
# 沒解掉的是「內容太技術,看得到但判斷不了」。輸出風格設定只在 session 開頭讀一次,
# context 一長就淡掉;掛在 UserPromptSubmit 的話每一輪都會重新注入一次。
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

# stdin 的 hook payload 用不到(本支不看使用者輸入內容),但要讀掉避免上游 SIGPIPE。
cat >/dev/null 2>&1 || true

# 同時給 systemMessage 與 hookSpecificOutput.additionalContext:不同版本的 runtime
# 讀的欄位不同,多給一個不認得的鍵會被忽略,少給則整段靜默不生效。
cat <<'JSON'
{
  "systemMessage": "【回覆語言】用繁體中文回覆,而且要讓不熟這個領域的人看得懂。\n1. 白話當主詞、術語放括號:先講「會發生什麼事」,再把原詞放進括號對照。例:不要寫「這是 blocking hook,命中時 exit 2」,要寫「這支程式會先看一眼,看到不該出現的東西就把這次修改打回去(blocking hook,回傳代碼 2)」。\n2. 自檢:把每個括號連同術語整段遮掉之後,句子還要讀得懂;做不到就重寫。這條逐格適用 —— 表格的每一格、每個標題、每個清單項各自要過。\n3. 系統內部代號、狀態字串、enum 值要附中文意思:寫「審核中(in_review)」,不要只寫 in_review。\n4. 不受本條規範:程式碼、指令、檔名、commit message、文件內的識別字,一律照原樣寫,不要翻譯。",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "【回覆語言】用繁體中文回覆,而且要讓不熟這個領域的人看得懂。\n1. 白話當主詞、術語放括號:先講「會發生什麼事」,再把原詞放進括號對照。例:不要寫「這是 blocking hook,命中時 exit 2」,要寫「這支程式會先看一眼,看到不該出現的東西就把這次修改打回去(blocking hook,回傳代碼 2)」。\n2. 自檢:把每個括號連同術語整段遮掉之後,句子還要讀得懂;做不到就重寫。這條逐格適用 —— 表格的每一格、每個標題、每個清單項各自要過。\n3. 系統內部代號、狀態字串、enum 值要附中文意思:寫「審核中(in_review)」,不要只寫 in_review。\n4. 不受本條規範:程式碼、指令、檔名、commit message、文件內的識別字,一律照原樣寫,不要翻譯。"
  }
}
JSON
exit 0
