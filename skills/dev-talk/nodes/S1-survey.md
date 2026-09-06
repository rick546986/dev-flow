# S1-survey — 盤現況

## 進條件

S0 已完成(slug / 起點 / 模式已定)。MEMORY_SESSION_ID 仍在。游標在 S1。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

本場 `talk start` 的 brief(`known_facts`／`known_knowledge`／`repo_signals`／
`conflicts`),再讀白名單 → 條列事實(帶數字與檔案位置),含受影響面清點
(這個想法會碰到哪些既有程式碼/檔案/介面/資料)。
不讀白名單外的文件類資料夾。不讀其他 `docs/dev/<slug>/`。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。不得 talk end。
本機游標只留在本機,不進 Git。

## 做什麼

1. **消化 brief**。`known_facts`／`known_knowledge`／`repo_signals`／`conflicts`
   逐項過一遍,每項落到「已驗證進 Context」「留 Log 待驗證」「不相關」三者之一。
   三軸不得互借:只有 `known_facts` 的 `VERIFIED` 才是 Context 候選;
   `known_knowledge` 的 `CONFIRMED` 只是 reasoning signal;`repo_signals`、
   其他狀態、`ask()` 非 `OK` 的答案一律不進 Context,可留 Log 待驗證。
   **signal ≠ evidence;memory ≠ current fact。**
2. 讀白名單(記憶入口、`docs/specs/`、原始碼),條列事實並一併回報使用者。
   認可後的清單 = 本次「已核事實」。
3. 寫進 Context 的每條 = 已驗證斷言 + 出處。出處語法只有一種:
   `path:L<起>` 或 `path:L<起>-L<迄>`;spec 用 `docs/specs/<domain>.md:L<起>-L<迄>`。
   驗證 = 在 current working tree 讀過該路徑、該行段內容支持斷言。沒讀過的路徑不進 Context。
4. 同 slug 另開 dev-talk、覆寫 `1-discussion.md` 時(S8「可改已有的」),必須逐條
   重讀出處:路徑不存在、行段失效、內容不再支持斷言 → 該條降回 Log 待驗證。
   此步人工執行;掃頁產生器不讀產品檔案系統。
5. 條件命中才畫可選目錄樹,食譜在 `_templates/1-discussion.md` 頂註;不進本 hop。
6. 跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S1-survey "$MEMORY_SESSION_ID"`。

## 完成條件

brief 四欄位已逐項消化。使用者認可;認可後的清單就是本次已核事實,
進 Context 者每條帶出處。重跑時出處已重驗。本機游標在 S1-survey。

## 下一跳

S2-world
