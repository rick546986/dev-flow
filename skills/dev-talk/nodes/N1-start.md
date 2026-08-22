# N1-start — 開場

## 進條件

這是新場:沒有 MEMORY_SESSION_ID,本機也沒有「現在節點」。
下一次 `/dev-talk` 一律新 session,絕不接上一場。
若本機已有 MEMORY_SESSION_ID(重跑),本節點不是入口 —— 從現在節點繼續,不要進本檔。

## 讀什麼

本檔、`graph.yaml`(下一跳正本)、入口檔的盲原則 / 讀寫白名單 / 記憶生命週期。
只讀白名單;白名單外的文件類資料夾不進、不列、不搜。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。
本機游標(現在節點、MEMORY_SESSION_ID)只留在本機,不進 Git。

## 做什麼

1. 跑 `${CLAUDE_PLUGIN_ROOT}/memory/dev-memory.py talk start "<本輪主題>"`。
   它回 `session_id` 與 brief。把 `session_id` 當 MEMORY_SESSION_ID,**全程重用**。
   brief 的 open questions 是 N3 逐題逼問的起點之一,不是全部。
2. 把執行清單 0-11 建成 todo(開場第一動;逐項達成完成條件才勾;禁跳項、禁併項)。
3. 本機游標寫成 N1-start。

## 完成條件

已有 MEMORY_SESSION_ID。0-11 todo 已建。本機游標在 N1-start。

## 下一跳

N3-probe
(先走入口檔暫留正文步 0–2,完成後進 N3)
