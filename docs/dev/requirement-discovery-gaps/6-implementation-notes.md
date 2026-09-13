---
feature: requirement-discovery-gaps
stage: 6-implementation
status: draft
owner: implementer-c
updated: 2026-09-13
---

# 6. 實作筆記

> Variant C：教師改口依人怎麼填檔的旅程（Goals／Requested solution → 前綴 → Assumption → disposition → manifest → Fast → verdict 一行），牙只延三支既有入口。本 hop 不改 STATUS／HISTORY、不發明 G3、不新開 R/S、不新開第四檢查家族。

## 步 0 守衛武裝自檢

- `devflow-exec.sh status`:`slug=requirement-discovery-gaps started=2026-09-13T06:03:38 scope=22 extra=0 sentinel=在`
- `devflow-doctor.sh`:`✅ devflow doctor: COMPATIBLE`
- feature branch:`cursor/rdg-s6-land-c-5ac5`（base `ab78e8b` = #282 Stage 5）
- 圍欄：只讀 4-spec／5-tasks／6-notes／活教師；未讀本 slug 1／2／3。
- ENV：本機缺 `markdown-it-py==4.0.0` 時 renderer 節會紅；已裝 `scripts/requirements-methodology-render.txt` 釘版（不計升階）。

## T Review Log

### T-1
- reviewer identity: Implementer C self-verify（Cloud Agent；獨立 reviewer 未另開 session）
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:06Z（早於本 T commit）
- Verify: 5-tasks T-1 原指令 → `T-1-wired` + `✅ real-world interaction checks: 140/140 passed(地板 140)`
- Covers finding: S-1.2 單檔負向 exit 1 且含「構想在錯欄」；S-1.4 單檔正向 exit 0；無 `check-discovery-gaps.sh`
- Files finding: 只動 `scripts/check-realworld.sh` + `scripts/fixtures/discovery-gaps/`
- RED→GREEN finding: 開工前 fixture 目錄不存在（5-tasks 原樣表）；落地後同一入口咬錯欄、不誤殺領域詞
- Test Integrity finding: none（未刪／放寬既有 assertion；MIN_CHECKS=140 等於實數）
- Design boundary finding: ①無未授權模組；②realworld 仍擁有教師／fixture 地板；③未改 spec-gate／guard 契約；④未新開第四家族；⑤n-a
- verdict: PASS
- correction + re-review after FAIL: N/A

## Progress Log

| 日期 | T-id | hash |
|---|---|---|
| 2026-09-13 | T-1 | *(commit 後補)* |

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run:

## TDD Evidence

### T-1 / S-1.2
- RED: `test -f scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md` → 開工前目錄不存在（5-tasks 原樣表 ③）
- GREEN: `bash scripts/check-realworld.sh scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md` → exit 1；`構想在錯欄：Goals 把通道構想當目標，Requested solution 缺或空`

### T-1 / S-1.4
- RED: 正向 fixture 不存在
- GREEN: `bash scripts/check-realworld.sh scripts/fixtures/discovery-gaps/goals-outcome-with-requested-dashboard.md` → exit 0；預設 `bash scripts/check-realworld.sh` → 140/140

## Decisions(spec 未載明的自由選擇)
- D-impl-1: `check-realworld.sh` 第一參數若是 `.md` 檔，走單檔形狀模式（只咬對照稿）。隔離 root 仍走舊目錄模式。理由：S-1.2 觀測要「對該 fixture exit ≠ 0」，而 T-1 Verify 預設入口必須仍綠。
- D-impl-2: fixture 自測在檔不存在時 `check_skip`（隔離 seed 無 discovery-gaps 目錄）。理由：不改 T-1 Files 外的 `test-architecture-guards.sh`。

## Deviations

（尚無 L1／L2）

## Files Changed

（全 T 後填；對照 Diff Budget）

## Diff(各 T commit,逐檔折疊)

（收尾補）

## Self-Review

（全 T 後填八問）

## Review Follow-up(G3 打回時才用)
