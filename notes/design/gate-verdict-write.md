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
   serve 只收本機同源:Host／Origin 限 `127.0.0.1`／`localhost:<port>`(`file://` 的
   `Origin: null` 也拒)、POST 只收 `application/json`、必帶啟動時產生的一次性 token
   (header `X-Devflow-Gate-Token`,或 GET 頁面時發的 `SameSite=Strict; HttpOnly` cookie);
   不送 CORS `*`。要用 serve 寫,頁面就從 serve 的 URL 開。
5. **skill／hop**。md 頂欄 `verdict:` 已是 `PASS`／`REQUEST_CHANGES`／`HOLD` →
   該 gate 已關;feature agent **不得手改** review／decision／spec 檔來記錄
   Human verdict。尚無寫入 → 才准在 chat 問人。`REQUEST_CHANGES` 走既有修迴圈,
   不是「把判定貼一遍」。
6. **verdict 必附出處**。同一頂欄 `verdict_source:`(`human_attested`／
   `fresh_agent_reviewer`／`owner_self_review`)與 `attested_by:`(`human:<名>` 或 `agent:<id>`)
   隨 `verdict:` 一起落盤;寫入器在有 reviewer 時代填 `human_attested` + `human:<reviewer>`,
   reviewer 是 agent／Jev 一律拒收。缺兩欄 = **unverified**(legacy,gate 照關、只列不紅,**不進任何 graduation n**)。
   **Jev／任何自動化不得寫 `verdict:`、不得填 `attested_by`**。G1(2-decision)／G3(7-review)
   只收人寫的 verdict。**G2 auto**:agent reviewer 的 PASS 只由 `devflow_gate.py write-g2-auto`
   寫入 —— 只收 4-spec、`fresh_agent_reviewer` + `agent:<id>` 且 ≠ `authored_by`／owner,寫前要
   G2R 判 AUTO、未命中任何轉人條件、機械檢查全過,並記 `devflow-jev.py g2-misrelease release`;
   頂欄另帶 `g2_mode: auto`、`routed_by: jev:<id>`、`g2r_case`、`g2r_jev`、`mechanical`(契約 §7
   「G2 provenance」)。格式 attestation 是 provenance tripwire,不是身份驗證。
   機械檢查:`scripts/check-verdict-attestation.sh`。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| G3 twin 五格／執行板 | `_templates/7-review.md` + `scripts/build-gate-twin.py` |
| 第 7 站截圖槽 | `notes/design/stage7-review-ui-contract.md` |
| 第 6 站審碼 hunk | `notes/design/stage5-review-ui-contract.md` |
