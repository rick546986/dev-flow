---
feature: subsidy-3-0-plus
stage: 5-tasks
status: draft
owner: IVF後台
updated: 2026-08-26
execution:
  mode: sequential
---
# 5. 任務 — 試管補助 3.0 PLUS

dev-flow · Stage 5 · full · 2026-08-26
上游＝`4-spec.md`（G2 PASS 2026-08-26 使用者審 html）

tracer：先讓 PLUS 金額三格在畫面＋存檔對（T-1→T-2），再鎖年齡（T-3），再列 OPU（T-4）。

## 執行前提
- 只寫本 worktree。主目錄與 27004 不動。
- 正式區／191 不碰。180 不加欄。
- 形成金額先不落新欄：存 `subsidy_limit = 取卵+形成+植入`，讀回來形成＝上限−取卵−植入。
- Verify 用 grep 形狀（動碼前紅、後綠）。行為靠人工回歸。
- PHP 5.3.3：不使用短陣列 `[]`、不使用 `??`。

## T-1 三處金額函式依申請日切 PLUS 表

- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, R-2 / S-2.1, S-2.3, R-4 / S-4.2
- Files: controllers/backend/ivf.php, views/backend/ivf_subsidy_edit.php
- Verify: `rg -n "2026-09-01|embryo" controllers/backend/ivf.php views/backend/ivf_subsidy_edit.php | grep -c "2026-09-01"` 
- Intent: 申請日 ≥ 2026-09-01 用 PLUS 三欄（完整／取卵無法植入／僅植入），形成＝完整−取卵−植入；9/1 前仍 3.0 兩格數字。
- Boundaries: 改 `calculateSubsidy3Amount`、`calculateSubsidy3AmountAdd`、`calculateSubsidy3AmountForSchedule5` 三處同一張表。低收入仍 15 萬。不改顆數、不改 38 文案。PLUS 切日看主檔 apply_date，不看 today。
- Blocked-by: —

## T-2 附表五畫面三格且手改存檔不蓋

- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2
- Files: views/backend/ivf_subsidy_edit.php, controllers/backend/ivf.php
- Verify: `rg -n "胚胎形成|embryo_subsidy" views/backend/ivf_subsidy_edit.php | grep -c "胚胎形成"`
- Intent: PLUS 看得到取卵／胚胎形成／植入；手改後存檔再打開數字還在。
- Boundaries: 3.0 舊案維持兩格 readonly＋後端覆寫。PLUS 打開可改；後端若 POST 帶 subsidy_amount_manual=1 就用畫面值，不算回去。形成不新增 DB 欄。27004 不掛本樹。
- Blocked-by: T-1

## T-3 新增附表五不覆寫已存金額年齡

- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2
- Files: views/backend/ivf_subsidy_edit.php
- Verify: `rg -n "first_subsidy_age" views/backend/ivf_subsidy_edit.php | grep -c "calcSchedule5AgeAndAmount"`
- Intent: 第 2 次附表五不會把 first_subsidy_age 重算掉。
- Boundaries: 只改 `calcSchedule5AgeAndAmount`：已有 first_subsidy_age 就不要寫回。不改次數欄 first_time_subsidy_age。不開新補助案（歸零是人工新開）。
- Blocked-by: T-1

## T-4 附表五列出形成胚胎的 OPU

- [x] 完成
- Covers: R-4 / S-4.1, S-4.2
- Files: views/backend/ivf_subsidy_edit.php, controllers/backend/ivf.php
- Verify: `rg -n "sum_2pn|opu_ivf_no" views/backend/ivf_subsidy_edit.php controllers/backend/ivf.php | grep -c "sum_2pn"`
- Intent: 有 fbt_date 時附表五看得到對到的 OPU ivf_no、取卵日、2PN。方案 C 仍是僅植入。
- Boundaries: 用 fbt_date→ivf_fbt（cNumber+bt_date）→opu_ivf_no→OPU sum_2pn。不硬擋顆數。查詢要帶 cNumber，不單靠 ivf_no。
- Blocked-by: T-2
