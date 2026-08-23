# N13-end

## 進條件

步 8–10 已完成。html 已產。MEMORY_SESSION_ID 仍在。

## 讀什麼

`1-discussion.md` 與同目錄 html。

## 寫哪裡

討論檔 status 改 approved。只經 `talk end` 寫入長期記憶,不直接改記憶檔。

## 做什麼

給使用者過目。點頭後跑 `talk end`,關閉 session。
跑 `scripts/check-devtalk-graph.sh --write-cursor N13-end "$MEMORY_SESSION_ID"`。

## 完成條件

使用者點頭。`talk end` 已跑。session 關閉。

## 下一跳

無
