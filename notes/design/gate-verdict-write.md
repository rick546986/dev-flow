# Human gate verdict 寫入(鎖死)

> G1／G2／G3 給人審的 html twin,勾選不是判定。本檔鎖**判定怎麼落盤**。
> 正本是同目錄 md 頂欄 `verdict:`,不是 HTML、不是 localStorage、不是 sidecar。
> 不發明第六個 `build-gate-twin` stage。補助產品詞不得當通用規則。

## 鎖死

1. **正本是 md 頂欄 `verdict:`**。`7-review.md`／`2-decision.md`／`4-spec.md`
   頂欄 `verdict:` 才是 Human 判定。允許值:`PASS`／`REQUEST_CHANGES`／`HOLD`。
   HTML／localStorage／sidecar 都不是正本。sidecar 與 md 衝突時 **md 勝**。
2. **只有「提交判定」才寫入**。勾選只是瀏覽器草稿,存在 localStorage。
   **全勾不算 PASS**。沒按「提交判定」= 尚未寫入。
3. **必須寫同目錄 md**。提交時寫入該 gate 同目錄 md 的 `verdict:`。
   可另寫一行 `- Human verdict note:`。可另寫選配 sidecar
   `docs/dev/<slug>/7-review.verdict.json`(G1／G2 對應 `2-decision.verdict.json`／
   `4-spec.verdict.json`)給不想解析 md 的 skill;sidecar 不是正本。
4. **寫入路徑**。優先 `dev-flow gate serve`(`python3 scripts/devflow_gate.py serve`)
   POST 到本機 helper,由 helper 改 md。`file://` 後備:File System Access 寫同一份
   md。不要假裝 localStorage 已落盤。
5. **skill／hop**。md 頂欄 `verdict:` 已是 `PASS`／`REQUEST_CHANGES`／`HOLD` →
   該 gate 已關;feature agent **不得手改** review／decision／spec 檔來記錄
   Human verdict。尚無寫入 → 才准在 chat 問人。`REQUEST_CHANGES` 走既有修迴圈,
   不是「把判定貼一遍」。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| G3 twin 五格／執行板 | `_templates/7-review.md` + `scripts/build-gate-twin.py` |
| 第 7 站截圖槽 | `notes/design/stage7-review-ui-contract.md` |
| 第 6 站審碼 hunk | `notes/design/stage5-review-ui-contract.md` |
