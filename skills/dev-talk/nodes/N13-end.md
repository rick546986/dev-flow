# N13-end — 過目與收尾

## 進條件

步 8–10 已完成。`1-discussion.md` 與同目錄 html 都在。MEMORY_SESSION_ID 仍在。
游標在 N13。N13 之前的節點不得跑本檔的 `talk end`。

## 讀什麼

`1-discussion.md`(正本)與同目錄 html。Open Questions 只認三態。

## 寫哪裡

討論檔 status 改 approved。
只經 `dev-memory.py talk end $MEMORY_SESSION_ID` 寫入長期記憶並關閉 session;
不直接改長期記憶檔。turn / propose 到此為止。
不寫程式碼。不另存第二份 `1-discussion.md`。

## 做什麼

舊執行清單步 11。把 html 給使用者過目(md 為正本)。
Open Questions 只有三態:`[x]` 已解 / `[~]` 帶假設(使用者明說先這樣)/ `[>]` 移交
(本討論不解,標注留待後續)。
使用者點頭 → status 改 approved → 跑 `dev-memory.py talk end $MEMORY_SESSION_ID`
(這一步才把已確認的語意寫進長期記憶並關閉 session;原始對話逐字稿只留在本機,
永遠不進版本控制)。
它回 `promoted: 0` 是合法結果 —— 這一輪沒有形成可確認的語意就是沒有,
**不要為了有東西可交而硬記一筆** → **停**。
跑 `${CLAUDE_PLUGIN_ROOT}/scripts/check-devtalk-graph.sh --write-cursor N13-end "$MEMORY_SESSION_ID"`。

## 完成條件

使用者點頭。status 已是 approved。`talk end` 已跑。session 關閉。本場結束。

## 下一跳

無
