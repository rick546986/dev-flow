# N7-end — 收尾核對

## 進條件

G2 已有 verdict。`4-spec.md` frontmatter 即將是 approved。游標在 N7。

## 讀什麼

`4-spec.md` frontmatter 與內文(含頂欄 `verdict:`)、`STATUS.md`、`4-spec.html`。
G2 條件正本 `guides/guide-dev-flow.html#gates`。`graph.yaml` 是下一跳正本。
sidecar／HTML／localStorage 都不是正本;sidecar 與 md 衝突時 md 勝。

## 寫哪裡

不新開檔。禁止 `4-spec-*.md`。不寫 `5-tasks.md`(第 5 站另有游標)。
Human verdict 只經頁尾「提交判定」寫進 `4-spec.md` 頂欄 `verdict:`。
本機游標不進 Git。

## 做什麼

若 `4-spec.md` 頂欄 `verdict:` 已是 PASS／REQUEST_CHANGES／HOLD,本 G2 已關;
feature agent 不得手改 `4-spec.md` 來記錄 Human verdict。
尚無寫入 → 才准在 chat 問人。全勾不算 PASS。REQUEST_CHANGES 走既有修迴圈,
不是「把判定貼一遍」。
核 status=approved 且三連動一致(frontmatter／`STATUS.md`／html twin)。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor N7-end`。

## 完成條件

status=approved。游標在 N7-end。

## 下一跳

無
