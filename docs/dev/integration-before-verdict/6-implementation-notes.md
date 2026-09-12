---
feature: integration-before-verdict
stage: 6-implementation
status: draft
owner: rick
updated: 2026-09-12
---

# 6. 實作筆記（薄檔：座標 + Verify，不是第二份審查）

> Stage 6 已由 Implementer B 合進 tip `#231`（`c7e69ac`）。本檔**只**給 Stage 7
> S2c `--fork-sha` 與 T Verify 重跑落點。**沒有 Self-Review**——審查正本是
> `7-review.md`。禁止再長 `6-implementation-notes-*.md`。

FORK_INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab

## 起手（回填，供 2c）

- 本 Stage 7 審查 branch `cursor/ibv-stage7-impl-a-d268` 從 tip `#231` 開出。
  上列 FORK = 開 branch 當下 `origin/main`（`c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`）。
- Stage 6 歷史分岔（Implementer B 從 `#226` 開工）= `ed594bfa846206b81a09be317cac8bbafa4c14ba`；
  落地 squash = `#231` / `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`。2c 吃的是上列 FORK 欄，不是這段歷史句。
- 0b worktree 隔離:`n-a:本 feature 未並行`（單一 checkout，無第二棵 worktree／無共用 DB）
- 0c doctor:`COMPATIBLE`（契約 2.0.0；runtime 3.23.3；gauntlet 1.3.3）。exec 未武裝（本 hop 只寫 docs）。

## T-1 / T-2 / T-3 Verify（Stage 7 親跑；5-tasks 原文）

日期:2026-09-12。HEAD 當時 = `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`。

### T-1

```
ST-filled count=5
ST-filled: void-only fail:void-only
ST-filled: rebind-sha pass:rebind-sha:def4567890abc
ST-filled: item-fail pass:item-FAIL
ST-filled: na-incoming no-fire:N_A_NO_INCOMING
ST-filled: draft-unclaimed no-fire:draft
✅ check-stage67-enforcement: Stage 6/7 強制條款齊(79 項檢查全過)
✅ 整合回歸守衛:全過(36 項)
✅ evidence gauntlet tests: 68/68 passed
S-4.1-ok
T1_VERIFY_EXIT:0
```

### T-2

```
T-2-ok
T2_VERIFY_EXIT:0
```

### T-3

```
=== G2 spec gate:scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md ===
✅ C1 … C4
❌ C5 Drafting Decisions 無殘留「待裁決」(L248 起)
✅ C6
⛔ G2 spec gate:5/6 通過,1 項 FAIL
T3_VERIFY_EXIT:0
```

負向 fixture 仍 exit 1（C5）。活路徑舊針 `rg` 零命中。

## Files touched（#231 落地；本 hop 不改碼）

- `scripts/check-stage67-enforcement.sh`（ST-filled 牙；`MIN_CHECKS=66`）
- `scripts/fixtures/stage67-filled-tooth/{void-only,rebind-sha,item-fail,na-incoming,draft-unclaimed}.md`
- `scripts/devflow-integration-regression.sh`（檔頭 + GUIDANCE；演算法／exit 碼不動）
- `docs/dev/tools/devflow-integration-regression.sh`（散發副本 parity）
- `manifests/p4-gauntlet-gates.md`（2c 文檔化命令 → 2d）
- `example/contract-expiry-reminder/{7-review.md,7-review.html,4-spec.md}`
- `scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md`

## Progress Log

| 日期 | T-id | 一行 |
|---|---|---|
| 2026-09-12 | T-1..T-3 | squash `#231` `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`（Implementer B） |

## 執行軌跡

手動／雲端 Stage 6（#231）。本檔不虛構 dev-run ledger。

## TDD Evidence

見上 Verify 原文。RED 在 Stage 5 開工前原樣跑已記於 `5-tasks.md`（牙未落地時 T-1/T-2/T-3 皆紅）。

## Decisions / Deviations

無本 hop 新 D-n。Stage 6 範圍 = 5-tasks Files 聯集。

## Files Changed

對照 4-spec Diff Budget（估 ≤9 檔）。#231 產品檔 13（含 5 fixture + 活教師 + 牙 + 兩支腳本 + manifest）。本 hop 只加本檔與 `7-review.*`。
