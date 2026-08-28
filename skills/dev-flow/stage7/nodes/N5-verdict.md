# N5-verdict — G3 判定

## 進條件

N4-author 完成,`7-review.md` 已落檔。不要另開檔。

## 讀什麼

已落檔的 `7-review.md`(含頂欄 `verdict:`)。PASS 條件正本仍是現有 G3(README §7 +
Gauntlet / Evidence 契約 / 空欄擋 / 層名全等 / 出貨樹=審過的樹 /
Final Fresh 綁 SHA)。本檔不另寫通過條件、不重寫那些工具。
`graph.yaml` 是下一跳正本。
sidecar／HTML／localStorage 都不是正本;sidecar 與 md 衝突時 md 勝。

## 寫哪裡

不另開 `7-review-*.md`／`7-self-review.md`。不寫 `6-implementation-notes.md`。
Human verdict 只經頁尾「提交判定」寫進本檔頂欄 `verdict:`。本機游標不進 Git。

## 做什麼

若 `7-review.md` 頂欄 `verdict:` 已是 PASS／REQUEST_CHANGES／HOLD,本 G3 已關;
feature agent 不得手改 `7-review.md` 來記錄 Human verdict。
尚無寫入 → 才准在 chat 問人。REQUEST_CHANGES 走既有修迴圈,不是「把判定貼一遍」。
全勾不算 PASS。核 status／verdict 與現有 G3 機械檢查一致;html twin 用現有
`build-gate-twin.py`,不改它。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor N5-verdict`。

## 完成條件

G3 形狀齊(或 REQUEST_CHANGES 仍以同一份 7-review.md 為正本)。
md 頂欄 `verdict:` 已是 Human 判定或已在 chat 問過。游標在 N5-verdict。

## 下一跳

無
