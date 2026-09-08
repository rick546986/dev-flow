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
現況圖(誰／做什麼／工具／痛點)必須從 Actors 名字集合與
Current Journey 有序步長出來,不准另發明天系統流卻叫現況圖。
現況圖是標題卡,不要把 Current Journey 整格搬進來。
渲染後四欄每行 ≤13 全形(W／F／A=1、其餘=0.5;這是權重和,不是「13 個字」;
空白=0.5)。量畫進圖的字:四行全帶標籤的堆疊形會剝標籤再量;一行形若寫標籤,
標籤會被畫出也會被量。超過 → S10 `build-scan-html.py` exit 1。
before／after:`月初翻 Excel 私表比對到期日` = 13.5 → `翻私表`。
與 `check-devtalk-fig-journey.sh` 共存:Journey 每步的誰／工具／動作／痛點
token 必須是圖上子字串;只縮圖、不縮 Journey 儲存格,S10 綠了這支牙會紅。
標題卡 ⇒ 先縮 Journey 再畫圖。
現況圖≠邏輯圖。
明天系統流(做完功能之後怎麼走)不准佔現況圖這個槽,也不准拿去對 Journey。
若骨架仍叫「邏輯圖」但畫的是現在怎麼走,先正名為現況圖,或另開「現況圖」節。
重跑本節點 = 覆寫同一路徑,不是另存一份。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor N9-write-md "$MEMORY_SESSION_ID"`。

## 完成條件

該 slug 目錄只有一份 `1-discussion.md`。十節齊、無佔位符。
現況圖已從 Actors＋Current Journey 長出(標題卡／每行 ≤13 全形),不是明天系統流。
本機游標仍在 N9(或已標完成、準備走 S8-review)。

## 下一跳

S8-review
