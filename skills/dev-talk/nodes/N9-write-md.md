# N9-write-md — 落檔 md

## 進條件

步 4–6 已完成。MEMORY_SESSION_ID 仍在。游標在 N9。
本節點 ≠ 舊執行清單步 9(詞彙對帳正本在 `nodes/S9-terms.md`)。

## 讀什麼

本場已核事實、真實世界五份、Goals / 驗收雛形、Interview Log、入口檔產出骨架。
不讀白名單外的文件類資料夾。

## 寫哪裡

只覆寫 `docs/dev/<slug>/1-discussion.md`,不另存。
禁止依節點另開討論檔。不得寫程式碼。不得 talk end。不直接改長期記憶檔。
同目錄 html 不在本節點(正本 `nodes/S10-html.md`)。

## 做什麼

舊執行清單步 7:按骨架寫 `1-discussion.md`。十節齊、無佔位符
(真實世界五份為其中一節,子節全在)。
現況圖(誰 → 用什麼 → 做什麼 → 痛在哪)必須從 Actors 名字集合與
Current Journey 有序步長出來,不准另發明天系統流卻叫現況圖。
明天系統流(做完功能之後怎麼走)不准佔現況圖這個槽,也不准拿去對 Journey。
若骨架仍叫「邏輯圖」但畫的是現在怎麼走,先正名為現況圖,或另開「現況圖」節。
重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor N9-write-md "$MEMORY_SESSION_ID"`。

## 完成條件

該 slug 目錄只有一份 `1-discussion.md`。十節齊、無佔位符。
現況圖已從 Actors＋Current Journey 長出,不是明天系統流。
本機游標仍在 N9(或已標完成、準備走 S8-review)。

## 下一跳

S8-review
