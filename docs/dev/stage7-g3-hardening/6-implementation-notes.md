---
feature: stage7-g3-hardening
stage: 6-implementation-notes
status: draft
owner: claude/stage7-g3-hardening
updated: 2026-08-22
---

# 6. 實作筆記

## TDD Evidence

| S | RED(舊實作) | GREEN(本輪) |
|---|---|---|
| S-1.1 / S-1.2 | `check-stage67-enforcement` 6 條 ST 失敗;`test-evidence-gauntlet` 38/43,P0-1 兩案紅 | ST 60/60;`test-evidence-gauntlet` 44/44;S67-ST 舊節序 mutation 紅 |
| S-2.1 / S-2.3 | profile-unverified 漏旗標 exit 0(29 checks passed,假綠) | exit 1,E7 |
| S-2.2 | 已綠(無 Required 可擋) | 仍綠 |
| S-3.1 | good-review `--review-file` 不帶 SHA exit 0(25 checks passed,假綠) | exit 1,E2 |
| S-2.4 | good-review `--review-file` 無 Profile exit 0(27 checks,假綠);無 Profile 節同 27 | exit 1,E7 |
| S-2.5 | profile-no-required-row exit 0(27 checks,假綠);`無`/`none` 被當層名 exit 1 | 缺欄 E7 紅;`無`/`none` 綠 |
| S-2.6 | `--profile` 指向 profile-pass 蓋過 sibling → exit 0(31 checks,假綠) | E7 紅 |
| S-3.2 | docs/dev/live-feature 顯式 stale SHA exit 0(29 checks,假綠) | exit 1,E2 |

舊實作數字是先補測試、未改 gauntlet 之前跑出來的,不是回憶。1230 兩條舊實作下
`test-evidence-gauntlet` 48/51。

## Decisions
- D-1:不新增粗體 G3 token。出貨樹收進 Evidence 契約第 1 點全文 + 模板節序,避免
  gate-consistency / EXPECTED token 集合膨脹。
- D-2:Conditional「已觸發」= Evidence 表已列且非 n-a。未列入視為未觸發,仍靠
  Reviewer 對 Profile 條件。不把 Gauntlet 變成去跑專案測試。
- D-3:`--review-file` 才預設 HEAD;顯式 `--source-sha` 在 example/ 與
  scripts/fixtures/ 仍只比對該值。`docs/dev/<feature>/7-review.md` 即使顯式
  傳 SHA 也強制 HEAD(owner 1230 裁)。
- D-4:Gauntlet 1.2.0 → 1.3.0 → 1.3.1 → 1.3.2,五處版本錨 lockstep。
- D-5:`--review-file` 找不到 Verification Profile 即 E7 fail-closed,不得退回
  1.2.0(owner 1230 裁)。
- D-6:Required layers 欄必須在;「無」/none 是明示零層(owner 1630 裁)。
- D-7:`--review-file` 的 `--profile` 只准 sibling 或同一 feature 目錄,不得跨份
  覆寫(owner 1630 裁)。

## Deviations
無。未改 `docs/dev/STATUS.md`。未動 `memory/`、`docs/dev/autoloop/`、PR #15。
