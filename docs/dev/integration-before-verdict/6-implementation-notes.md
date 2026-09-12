---
feature: integration-before-verdict
stage: 6-implementation
status: approved
owner: stage6-#231
updated: 2026-09-12
---

# 6. 實作筆記（薄；Stage 7 錨點）

FORK_INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab

> 本檔**不是** Stage 6 實作日誌正本。#231 合進 tip 時沒有 6-notes。
> Stage 7 graph／`devflow-integration-regression.sh --fork-sha` 需要步 0 錨點，
> 所以本 hop 只補 FORK + 指向 #231。**沒有 Self-Review 節**（審查者不得從本檔
> 得到作者主張）。產品 diff 以 `git show c7e69ac`（#231）為準。

## 起手

- 圍欄自查:本檔只服務 Stage 7 `--fork-sha`。禁把本檔當 Self-Review。
- branch（Stage 7 審查）:`cursor/ibv-stage7-review-b-b9a2`
- 錨點時刻:`origin/main` = `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`（#231 已在 tip）
- 0b worktree 隔離:`n-a:本 feature 未並行`（單一 checkout；無容器／DB／佇列）
- 0c:見下方 doctor／exec 記錄（Stage 7 N0 沿用）

## 摘要

Stage 6 產品在 tip `#231` / `c7e69ac`：AS-1 填檔牙（`check-stage67` ST-filled）+ 活教師改口。R-5 真跑留本 Stage 7 hop。

## T Review Log

產品 T-1／T-2／T-3 的 Verify 由 Stage 7 審查者親跑，不寫在本檔。

## Decisions + Deviations

| ID | 內容 | 依據 |
|---|---|---|
| D-s7-fork | 本檔只記 FORK，不補造 Stage 6 Self-Review | 派工：thin 6-notes only if needed for FORK／Stage7 graph |

## Diff

### FORK 錨點欄 · `docs/dev/integration-before-verdict/6-implementation-notes.md` 11-11  T-s7-bookkeeping
改什麼：補 Stage 7 `--fork-sha` 吃的 40 碼錨點（#231 合 tip 後本 slug 仍缺 6-notes）。
關聯：`devflow-integration-regression.sh --fork-sha`／Stage 7 graph S2c
```diff
+FORK_INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab
```
