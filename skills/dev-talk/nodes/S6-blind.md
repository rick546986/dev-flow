# S6-blind — 盲點掃描

## 進條件

S5 已完成。MEMORY_SESSION_ID 仍在。游標在 S6。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

已核事實、Goals、驗收雛形、發散段。不讀白名單外的文件類資料夾。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。不得 talk end。
本機游標只留在本機,不進 Git。

## 做什麼

列出「使用者沒想到要問、答案可能改變方向」的 unknown unknowns,
逐條解釋;並列出「使用者可能覺得顯然而沒說出口」的隱含預設,逐條問使用者確認。
新問題 → 步 3 重開再問。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S6-blind "$MEMORY_SESSION_ID"`。

## 完成條件

使用者對兩份清單皆回應過(至少一句,沉默不算)。本機游標在 S6-blind。

## 下一跳

N9-write-md
