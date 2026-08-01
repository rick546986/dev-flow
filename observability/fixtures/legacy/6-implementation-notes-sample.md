---
feature: legacy-feature
stage: 6-implementation
status: shipped
owner: rick
updated: 2026-06-15
---

# 6. 實作筆記

> 舊格式示範:ledger 制度之前的 feature,只有執行軌跡 Markdown、沒有 Run ID。
> stats 工具必須仍能讀(十三節「舊 Markdown 沒有 Run ID 時仍能讀」)。

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)

| T-id | 失敗分類 | 模型升階史 | 回合數 | 原因 |
|---|---|---|---|---|
| T-1 | — | — | 1 | — |
| T-2 | IMPL | haiku→sonnet | 2 | verify 紅一次,升階後過 |
| T-3 | ENV | — | 1 | node 版本不合,修環境重跑不計升階 |

## TDD Evidence

(略,與 ledger 無關)
