# N5-verdict — G3 判定

## 進條件

N4-author 完成,`7-review.md` 已落檔。不要另開檔。

## 讀什麼

已落檔的 `7-review.md`(含頂欄 `verdict:`)。PASS 條件正本仍是現有 G3(`guides/guide-dev-flow.html#gates` +
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
J5 shadow(W4)與本 G3 的關係:Jev **不寫**本檔頂欄 `verdict:`、不改 PASS 條件、不擋本節點。
Human verdict 落檔**之後**才可跑 worker 與配對(順序不可反,否則 Jev 的 route 會在判定前被看到):
`python3 ${DEVFLOW_ROOT}/scripts/devflow-jev.py drain` 送 queue 裡的 shadow evaluation(失敗只記 shadow failure);
`python3 ${DEVFLOW_ROOT}/scripts/devflow-jev.py label --slug <slug> --from-review --reviewer-ref <reviewer> --session-ref <reviewer session>`
把本檔的 Human verdict 配到**同一 evidence 版本**的 evaluation;HEAD 或 evidence 變了它會拒絕,不得手改讓它過。
兩步都可留給 owner 之後做;不做也不影響 G3。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage7-graph.sh --write-cursor N5-verdict`。

## 完成條件

G3 形狀齊(或 REQUEST_CHANGES 仍以同一份 7-review.md 為正本)。
md 頂欄 `verdict:` 已是 Human 判定或已在 chat 問過。游標在 N5-verdict。

## 下一跳

無
