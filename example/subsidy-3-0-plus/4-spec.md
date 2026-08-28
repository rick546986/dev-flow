---
feature: subsidy-3-0-plus
stage: 4-spec
status: draft-for-review
owner: IVF後台
reviewers: []
updated: 2026-08-28
---
# 4. 規格 — 試管補助 3.0 PLUS

審查稿，feat 正本未改。

## 確認紀錄
- 由 2026-08-25～26 已鎖討論 + 2-decision 展開。G1 未正式勾；方向已在對話鎖定。27004 等另一 session 測完再掛。

## 補助模組生命週期（預覽）

只畫補助模組。有關聯的收成一格，不拆檔名。直式圖，置中。
- 新生（這輪沒有）：不加欄。
- 改行為（相關一格）：PLUS 切表／兩格／OPU 小字。
- 退役：形成金額第三格。
- 不動：3.0 兩格、主目錄、27004、191。

## ADDED

### R-1 切表
主檔 `apply_date` ≥ `2026-09-01` 用 PLUS 表；否則整案 3.0（含之後附表五）。沒有 today 開關。

切的是金額表，不是 worktree。`apply_date` < 2026-09-01 → 整案 3.0 兩格表，年齡切在 39；`apply_date` ≥ 2026-09-01 → PLUS（方案拆三筆，畫面併成兩格），年齡切在 40。沒有「今天到了 9/1 全院切」的 today 開關；次數上限本來就 40：1–39→6 次，40–45→3 次。

**審的時候看什麼**
看主檔申請日，不是看今天、也不是看 worktree 有沒有切。8/31 立案的案子第二次附表五仍是 3.0 兩格（取卵 6 萬、植入 4 萬、上限 10 萬），不會冒出 15 萬。9/1 立案才走 PLUS，畫面仍是兩格，不是三格。年齡切點 3.0 用 39、PLUS 用 40。次數上限 1–39→6、40–45→3 本來就在，這輪沒改。

#### S-1.1 PLUS 第一次完整
- GIVEN 主檔 `apply_date` = 2026-09-01、`first_subsidy_age` = 35、`subsidy_times` 首次、方案 A 或 B、低收入＝否
- WHEN 計算附表五金額
- THEN 取卵 100000、植入 50000、上限 150000（形成 0 已併入取卵）
- 觀測：附表五兩格＋上限。資料：測試案申請日填 9/1。

#### S-1.2 舊案第 2 次仍 3.0
- GIVEN 主檔 `apply_date` = 2026-08-31、年齡 35、第 2 次、方案 A、低收入＝否
- WHEN 計算附表五金額
- THEN 走 3.0：取卵 60000、植入 40000、上限 100000；不出現 PLUS 的 15 萬
- 觀測：同一舊案第二次附表五。

#### S-1.3 PLUS 第 2 次完整
- GIVEN `apply_date` = 2026-09-01、年齡 35、第 2 次、方案 A、低收入＝否
- WHEN 計算
- THEN 取卵 110000、植入 40000、上限 150000（形成 5 萬併入取卵）
- 觀測：兩格加總 15 萬。

### R-2 兩格（形成併取卵）
PLUS 方案拆三筆：取卵、形成、植入。畫面只給兩格：取卵格＝取卵＋形成，植入格＝植入。上限＝兩格相加。

例：未滿 40 第 1 次完整 10+0+5 → 取卵 10 萬、植入 5 萬、上限 15 萬。未滿 40 第 2 次完整 6+5+4 → 取卵格 11 萬、植入 4 萬、上限 15 萬。滿 40 第 1 次 7+1+5 → 取卵 8 萬、植入 5 萬、上限 13 萬（先照算）。

自動填後可手改兩格，存檔不覆寫。3.0 本來就是兩格，不併形成。形成胚胎 OPU 只讀小字放上限格內，不另開金額格。

**審的時候看什麼**
PLUS 表本身是三筆（取卵、形成、植入），畫面上只出現兩格。取卵格已經把形成加進去：10+0+5 顯示 10 萬／5 萬，6+5+4 顯示 11 萬／4 萬，7+1+5 顯示 8 萬／5 萬。上限是兩格相加，不是再加一格形成。手改取卵或植入後存檔，後端不能算回自動值。OPU 小字在上限格，不是第三個金額格。

#### S-2.1 自動拆
- GIVEN PLUS、未滿 40、第 2～3 次完整
- WHEN 帶入方案 A
- THEN 兩格：取卵 110000（6+5 併入）、植入 40000、上限 150000
- 觀測：附表五金額欄（無形成金額格）。

#### S-2.2 手改留存
- GIVEN PLUS 已自動填 取卵 110000／植入 40000
- WHEN 把取卵改成 90000 並存檔再打開
- THEN 取卵仍是 90000，後端不得算回 110000
- 觀測：存檔後重整。

#### S-2.3 滿 40 第 1 次
- GIVEN PLUS、`first_subsidy_age` = 40、首次完整、低收入＝否
- WHEN 計算
- THEN 取卵 80000（7+1 併入）、植入 50000、上限 130000
- 觀測：兩格。先照算。

### R-3 年齡鎖與歸零
同一輪次數用 `first_time_subsidy_age`、金額用 `first_subsidy_age`，不重判。申請滿再來新開一筆，舊案不動。

**審的時候看什麼**
次數欄讀 `first_time_subsidy_age`，金額欄讀 `first_subsidy_age`，兩顆分開、同一輪不重判。申請日實務不改；新增附表五也不覆寫已存的 `first_subsidy_age`。次數用滿（6 或 3）再來是新開一筆，舊案列不動。新案才用新申請日與妻生日重算兩格年齡。沒有「同一案改回首次」這條路。

#### S-3.1 第 2 次不改年齡格
- GIVEN 已有 `first_subsidy_age`=35、`first_time_subsidy_age`=35
- WHEN 新增第 2 次附表五（申請日沒改）
- THEN 兩格年齡仍是 35
- 觀測：主檔年齡欄。

#### S-3.2 新開一筆重算
- GIVEN 舊案已用滿次數
- WHEN 新開一筆補助、新申請日、妻生日算出 40
- THEN 新案兩格年齡是 40，舊案列不變
- 觀測：兩筆主檔。

### R-4 形成胚胎 OPU
附表五用 `fbt_date` → FBT → `opu_ivf_no` → OPU，列出形成胚胎的那張 OPU（`ivf_no`、取卵日、`sum_2pn`）。方案 C 不當完整。

**審的時候看什麼**
路徑是 `fbt_date` → FBT → `opu_ivf_no` → OPU。看得到的是那張 OPU 的 `ivf_no`、取卵日、`sum_2pn`，寫在上限格小字。方案 C 即使有植入日也只走僅植入，上限＝植入格，不是完整最高額。沒對到 FBT／OPU 就沒有這段小字。這輪不硬擋植入顆數。

#### S-4.1 有植入且 2PN>0
- GIVEN PLUS、有 `fbt_date` 對到 FBT，其 `opu_ivf_no` 的 `sum_2pn`>0，方案非 C
- WHEN 打開附表五
- THEN 看得到該 OPU 的 `ivf_no`、取卵日、2PN
- 觀測：補助金額上限格內小字（ivf_no／取卵日／2PN；非獨立列）。

#### S-4.2 方案 C
- GIVEN 方案 C、有 `fbt_date`
- WHEN 計算上限
- THEN 走僅植入，不是完整最高額
- 觀測：上限＝植入格。

### R-5 測試掛載
27004 等另一 session 測完再把 bind 從主目錄改掛本 worktree。此前只寫本 worktree。

27004 是測試機容器，現在 bind 主目錄 `/path/to/ivf_platform`（ERP 分支）。本 feat 碼在 subsidy worktree；不切掛載時 27004 看不到 PLUS。等另一 session 測完再把 bind 改掛本 worktree；切之前只寫 worktree、不動主目錄、不開第二容器。

**審的時候看什麼**
27004 現在掛的是主目錄 ERP 分支，不是本 worktree。這輪改 PHP 只寫 worktree，27004 重整畫面應維持 ERP 行為。不切 bind、不動主目錄、不另開第二個容器。PLUS 畫面要等另一 session 測完、改掛本 worktree 之後才會出現。切掛載之前，27004 看不到 PLUS 是對的。

#### S-5.1 未切前
- GIVEN 27004 仍掛 `/path/to/ivf_platform`
- WHEN 本 worktree 改 PHP
- THEN 27004 畫面不變（另一 session 不受影響）
- 觀測：27004 重整仍是 ERP 分支行為。

## MODIFIED
- `calculateSubsidy3Amount`／Add／`calculateSubsidy3AmountForSchedule5`：PLUS 切日＋形成併取卵後兩格。3.0 路徑數字不變。

## REMOVED
- 無。不刪 3.0 兩格邏輯。

## Acceptance Criteria
- S-1.1～S-4.2 綠。低收入仍 15 萬。顆數不硬擋。正式區／191 無寫入。180 不加欄除非使用者准。
- 「綠」是指 S-1.1～S-4.2 的兩格數字與觀測位置都對上，不是改成三格、也不是用 today 切表。

## Out of Scope
- Revised。顆數 38 硬擋。低收入改。主目錄 ERP。today 開關。國健署正文衝突（[>]）。
- 以上都不進本 feat；國健署正文若跟 briefing 衝突另開討論，不在這裡改金額。

## Diff Budget
- `views/backend/ivf_subsidy_edit.php`
- `controllers/backend/ivf.php`（三處金額之一）
- 附表五新增／更新存檔（同檔或 model）
- 可選：`ivf_subsidy_schedule5.embryo_subsidy_amount` 欄（測試庫、需准）
- `docs/dev/subsidy-3-0-plus/*`

## Dependencies
- 形成不落庫；畫面兩格，上限＝取卵＋植入。
- 27004 切掛載：等另一 session。

## Verification Profile
- lane: full
- Risk: medium（金額、新欄）
- 回歸：3.0 舊案兩格數字不變；低收入 15 萬。

## Design Boundary
- 只動補助編輯／附表五金額。不碰 PGS／報告。

## Drafting Decisions
- DD-1 形成金額落庫欄名：`embryo_subsidy_amount`。180 未准不加。
- DD-2 G1 以對話鎖定視同方向可寫規格；正式 G1 勾仍待你。

## Test Skeletons
- 申請日 9/1 vs 8/31 各一筆。
- 未滿 40 第 1／2 次。
- 滿 40 第 1 次（取卵含形成 8 萬）。
- 手改取卵後重整。
- 測的是畫面兩格：第 1 次 10+5、第 2 次 11+4、滿 40 第 1 次 8+5，以及手改取卵 90000 存檔後不被算回。
