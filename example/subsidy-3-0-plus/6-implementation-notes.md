---
feature: subsidy-3-0-plus
stage: 6-implementation-notes
status: draft
owner: IVF後台
updated: 2026-08-29
---
# 6. 實作筆記 — 試管補助 3.0 PLUS（T-1～T-4）

只寫 worktree `/path/to/ivf_platform_subsidy-3-0-plus`。未碰主目錄、27004、191、180。T-4 形成胚胎 OPU 只讀小字放在補助金額上限格內（3.0 與 PLUS 都顯示；非獨立列）。

## 改了什麼

### T-1 三處金額同一張表
- PLUS 只看主檔 `apply_date >= 2026-09-01`（ROC 115/9/1）。沒有 today 開關。
- 三函式共用基數＋方案拆分：JS `calculateSubsidy3Amount`、`calculateSubsidy3AmountAdd`、PHP `calculateSubsidy3AmountForSchedule5`。
- 3.0（申請日 < 9/1）維持原 39 切兩格數字。
- PLUS 內部三欄基數不變（畫面仍兩格，不是三格畫面）：未滿 40 第1次 10+0+5；第2–3次 6+5+4；第4–6次 4+0+2。滿 40 第1次 7+1+5；第2–3次 4+5+4。
- 方案拆分後把形成併入取卵，畫面只留兩格。完整 A/B：未滿40 15／15／6 萬；滿40 13／13 萬。只取卵走官方取卵欄；只植入走官方植入欄。
- 低收入仍 10+5=15，再依方案拆。
- 方案：A/B 完整（最高額）；C 僅植入；D/E/F／無法植入 僅取卵；方案 1 看 `inside_operation`。
- `subsidy_version` 仍寫 `3.0`。

### T-2 兩格＋手改不蓋（2026-08-26 鎖定：形成併取卵）
- PLUS 與 3.0 畫面都是 取卵＋植入。PLUS 兩格可手改（readonly false）；3.0 仍 readonly。`#embryo_subsidy_wrap` 永不顯示。
- 形成不落新欄：`subsidy_limit = 取卵+植入`（形成已在計算時併入取卵）。載入不還原第三格。
- 手改設 hidden `subsidy_amount_manual=1`。PLUS 存檔若 POST 已有取卵／植入／上限則保留，不重算覆蓋。3.0 仍後端覆寫。

### T-3 年齡鎖
- `calcSchedule5AgeAndAmount`：`#first_subsidy_age_input` 已有值就不覆寫，改用該值算金額。

## 關鍵行號

| 檔 | 行 | 做什麼 |
|---|---|---|
| `controllers/backend/ivf.php` | 1455–1470 | add_schedule5：PLUS 保留 POST 金額 |
| `controllers/backend/ivf.php` | 1618–1636 | update_schedule5：同上 |
| `controllers/backend/ivf.php` | 7436–7448 | 公開 `calculateSubsidy3Amount` 也吃 apply_date |
| `controllers/backend/ivf.php` | 7489–7496 | `isSubsidy3PlusByApplyDate`（2026-09-01） |
| `controllers/backend/ivf.php` | 7537–7604 | 3.0／PLUS 基數表 |
| `controllers/backend/ivf.php` | 7640–7663 | `calculateSubsidy3AmountForSchedule5` |
| `views/backend/ivf_subsidy_edit.php` | subsidy3_fields | PLUS／3.0 兩格；形成格 hidden |
| `views/backend/ivf_subsidy_edit.php` | 2590–2795 | JS 切日＋`calculateSubsidy3Amount` |
| `views/backend/ivf_subsidy_edit.php` | 3004–3028 | `calcSchedule5AgeAndAmount` 不覆寫 first_subsidy_age |
| `views/backend/ivf_subsidy_edit.php` | 3077–3110 | `calculateSubsidy3AmountAdd` |

## 風險
- PLUS 滿 40 第 4–6 次規格沒給，基數維持 0（40+ 實務最多 3 次）。
- PLUS 存檔以畫面 POST 為準；若 JS 算錯會原樣寫入。3.0 仍後端重算。
- `apply_date` 沒 POST 時會查主表（`flush_cache`）。查不到就當 3.0。
- 形成已併入取卵；不再用上限−取卵−植入還原第三格。
- 附表五編輯 dialog 的金額 input id 本來就重複（foreach），這輪沒拆。
- 27004 未掛本樹，畫面未在此 session 人工回歸。
- PHP 5.3：新碼只用 `array()` / `isset()? :`，無 `[]`、`??`、`fn()`。

### T-4 附表五列出形成胚胎 OPU
- 只讀 SELECT，不寫 `ivf_fbt` / `ivf_opu`，不擋存檔，不依 2PN 改金額。
- 不是獨立列：小字放在「補助金額上限」格內、取卵／植入兩格下方（灰字 11px）。3.0 與 PLUS 新增／編輯都顯示。方案 C 仍僅植入，有對到仍列出 OPU；2PN=0 也列。
- 路徑：附表五 `fbt_date` + 主檔 `cNumber` → `ivf_fbt.bt_date`（同日多筆取 `id DESC` 最新）→ `opu_ivf_no` → `ivf_opu`（必帶 `cNumber`）的 `ivf_no` / `opu_date` / `sum_2pn`。
- FBT 對不到且畫面已有 `opu_date` 時，改用 `ivf_opu.cNumber + opu_date`。無 `fbt_date` 或都對不到：顯示「未對到」。
- AJAX：`POST /backend/ivf/lookupFormingEmbryoOpu`；改 `fbt_date`（或 `opu_date`）會重查。

## 關鍵行號（T-4）

| 檔 | 行 | 做什麼 |
|---|---|---|
| `controllers/backend/ivf.php` | 7667–7676 | `lookupFormingEmbryoOpu` JSON（只讀） |
| `controllers/backend/ivf.php` | 7726–7740 | `ivf_fbt`：`cNumber` + `bt_date`，同日最新 |
| `controllers/backend/ivf.php` | 7774–7805 | `ivf_opu`：`cNumber` + `ivf_no`／`opu_date`，取 `sum_2pn` |
| `views/backend/ivf_subsidy_edit.php` | 補助金額上限格內 | 新增／編輯 OPU 小字 |
| `views/backend/ivf_subsidy_edit.php` | 3001–3005 | 改 `fbt_date` 觸發查詢 |
| `views/backend/ivf_subsidy_edit.php` | 3132–3175 | 顯示 `ivf_no`／取卵日／`sum_2pn` |


## 2026-08-26 鎖定：形成金額併入取卵
- 基數表內部仍可有 ovum／embryo／implant。`applySubsidy3PlanSplit`（及 JS `applySubsidy3PlanToParts`）之後：`ovum += embryo`、`embryo = 0`、`total = ovum + implant`。
- 最高額只在取卵＋植入都在（完整 A/B）。只取卵或只植入走官方 PLUS 欄，不把形成加回去。
- 畫面回到兩格；形成胚胎 OPU 查詢與 `lookupFormingEmbryoOpu` 保留，改為金額格內小字。
