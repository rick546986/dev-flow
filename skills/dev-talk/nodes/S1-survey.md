# S1-survey — 盤現況

## 進條件

S0 已完成(slug / 起點 / 模式已定)。MEMORY_SESSION_ID 仍在。游標在 S1。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

白名單 → 條列事實(帶數字與檔案位置),含受影響面清點
(這個想法會碰到哪些既有程式碼/檔案/介面/資料)。
不讀白名單外的文件類資料夾。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。不得 talk end。
本機游標只留在本機,不進 Git。

## 做什麼

先消化本場 brief:known_facts／known_knowledge／repo_signals／conflicts 逐項過一遍,
每項落到「已驗證進 Context」「留 Log 待驗證」「不相關」三者之一。
讀白名單,條列事實並一併回報使用者。
Context 每條 = 已驗證斷言 + 出處(`path:L<起>` 或 `path:L<起>-L<迄>`)。
沒讀過的路徑不進 Context。brief 條目與 `ask()` 線索都要再經 current repo／spec 驗證。
同 slug 重跑覆寫 `1-discussion.md` 時,逐條重讀出處:路徑不在、行段失效、
內容不再支持斷言 → 該條降回 Log 待驗證。
認可後的清單 = 本次「已核事實」。
條件命中才畫可選目錄樹,食譜在 `_templates/1-discussion.md` 頂註;不進本 hop。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S1-survey "$MEMORY_SESSION_ID"`。

## 完成條件

使用者認可;認可後的清單就是本次已核事實。本機游標在 S1-survey。

## 下一跳

S2-world
