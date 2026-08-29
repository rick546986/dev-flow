---
feature: subsidy-3-0-plus
stage: 4-spec
status: draft
verdict:
owner: IVF後台
reviewers: []
updated: 2026-08-29
---

# 4. 規格 — 試管補助 3.0 PLUS(change spec)

審查稿。本檔依現行 `_templates/4-spec.md` 重寫既有手樣；R/S 產品事實沿用既有鎖，不新開產品行為。feat 正本未改。

## 補助模組生命週期（預覽）

只畫補助模組。有關聯的收成一格，不拆檔名。直式圖，置中。
- 新生（這輪沒有）：不加欄。
- 改行為（相關一格）：PLUS 切表／兩格／OPU 小字。
- 退役：形成金額第三格。
- 不動：3.0 兩格、主目錄、27004、191。

## ADDED Requirements

### R-1: 系統 SHALL 依主檔 apply_date 切 3.0／PLUS 金額表
主檔 `apply_date` ≥ `2026-09-01` 用 PLUS 表；否則整案 3.0（含之後附表五）。沒有 today 開關。

切的是金額表，不是 worktree。`apply_date` < 2026-09-01 → 整案 3.0 兩格表，年齡切在 39；`apply_date` ≥ 2026-09-01 → PLUS（方案拆三筆，畫面併成兩格），年齡切在 40。沒有「今天到了 9/1 全院切」的 today 開關；次數上限本來就 40：1–39→6 次，40–45→3 次。

**審的時候看什麼**
看主檔申請日，不是看今天、也不是看 worktree 有沒有切。8/31 立案的案子第二次附表五仍是 3.0 兩格（取卵 6 萬、植入 4 萬、上限 10 萬），不會冒出 15 萬。9/1 立案才走 PLUS，畫面仍是兩格，不是三格。年齡切點 3.0 用 39、PLUS 用 40。次數上限 1–39→6、40–45→3 本來就在，這輪沒改。

#### S-1.1 PLUS 第一次完整
- GIVEN 主檔 `apply_date` = 2026-09-01、`first_subsidy_age` = 35、`subsidy_times` 首次、方案 A 或 B、低收入＝否
- WHEN 計算附表五金額
- THEN 取卵 100000、植入 50000、上限 150000（形成 0 已併入取卵）
- 觀測:從附表五金額欄兩格＋上限看 | 取卵 100000、植入 50000、上限 150000 且無形成金額格算對 | 用測試案申請日填 2026-09-01、年齡 35、首次、方案 A 或 B、低收入＝否測
- Operational Context:
  - Actor:諮詢／行政（後台補助編輯）
  - Goal:依 115/9/1 PLUS 表算出第一次完整補助，填進附表五
  - Situation:新建補助案並新增附表五；現行程式還不會依申請日切 PLUS
  - Known information:申請日、方案 A/B、低收入＝否、妻年齡 35、首次
  - Missing information:這次有沒有形成胚胎（要另對 OPU／FBT，見 R-4）
  - Human decision:選方案 A 或 B；金額先吃自動填，要不要手改見 S-2.2
  - Authority:後台補助編輯可建案、選方案、看附表五金額
  - External dependency:國健署 PLUS 表／內部 briefing
  - Out-of-system action:對國健署表、紙本、docx
  - Waiting/timeout behavior:等病患資料齊才能建 `apply_date`；不因等待自動切表
  - Recovery:申請日填錯會切錯表；實務不改申請日。重開附表五仍讀主檔 `apply_date`
  - Audit/handoff requirement:主檔留下 `apply_date`、`first_subsidy_age`
  - Observation:附表五兩格＋上限（見本條 觀測）

#### S-1.2 舊案第 2 次仍 3.0
- GIVEN 主檔 `apply_date` = 2026-08-31、年齡 35、第 2 次、方案 A、低收入＝否
- WHEN 計算附表五金額
- THEN 走 3.0：取卵 60000、植入 40000、上限 100000；不出現 PLUS 的 15 萬
- 觀測:從同一舊案第二次附表五金額欄看 | 取卵 60000、植入 40000、上限 100000 且不出現 150000 算對 | 用申請日 2026-08-31、年齡 35、第 2 次、方案 A、低收入＝否的既有案測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:9/1 前立案的案子之後再辦第 2 次，整案仍走 3.0，不被重判
  - Situation:舊案已有第一次；9/1 後回來辦第 2 次附表五
  - Known information:主檔申請日 8/31、第 2 次、方案 A
  - Missing information:無（切表只看主檔申請日）
  - Human decision:不改申請日；不把舊案當新案重開
  - Authority:同 S-1.1
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:不適用（申請日已鎖在主檔）
  - Audit/handoff requirement:主檔 `apply_date` 仍是 2026-08-31
  - Observation:第二次附表五兩格仍是 3.0 數字

#### S-1.3 PLUS 第 2 次完整
- GIVEN `apply_date` = 2026-09-01、年齡 35、第 2 次、方案 A、低收入＝否
- WHEN 計算附表五金額
- THEN 取卵 110000、植入 40000、上限 150000（形成 5 萬併入取卵）
- 觀測:從附表五兩格加總看 | 取卵 110000、植入 40000、上限 150000 算對 | 用申請日 2026-09-01、年齡 35、第 2 次、方案 A、低收入＝否測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:PLUS 第 2 次完整要拿到 15 萬，不能變成 6+4＝10
  - Situation:9/1 立案後的第 2 次附表五
  - Known information:申請日 9/1、第 2 次、方案 A
  - Missing information:形成胚胎是否已對到（數字仍先自動填，見 R-2）
  - Human decision:選方案 A；要不要手改見 S-2.2
  - Authority:同 S-1.1
  - External dependency:PLUS 表第 2～3 次完整 15 萬
  - Out-of-system action:對表
  - Waiting/timeout behavior:不適用
  - Recovery:重開附表五仍依主檔申請日走 PLUS
  - Audit/handoff requirement:同 S-1.1
  - Observation:兩格加總 15 萬

### R-2: 系統 SHALL 把 PLUS 形成金額併入取卵格並只顯示兩格
PLUS 方案拆三筆：取卵、形成、植入。畫面只給兩格：取卵格＝取卵＋形成，植入格＝植入。上限＝兩格相加。

例：未滿 40 第 1 次完整 10+0+5 → 取卵 10 萬、植入 5 萬、上限 15 萬。未滿 40 第 2 次完整 6+5+4 → 取卵格 11 萬、植入 4 萬、上限 15 萬。滿 40 第 1 次 7+1+5 → 取卵 8 萬、植入 5 萬、上限 13 萬（先照算）。

自動填後可手改兩格，存檔不覆寫。3.0 本來就是兩格，不併形成。形成胚胎 OPU 只讀小字放上限格內，不另開金額格。

**審的時候看什麼**
PLUS 表本身是三筆（取卵、形成、植入），畫面上只出現兩格。取卵格已經把形成加進去：10+0+5 顯示 10 萬／5 萬，6+5+4 顯示 11 萬／4 萬，7+1+5 顯示 8 萬／5 萬。上限是兩格相加，不是再加一格形成。手改取卵或植入後存檔，後端不能算回自動值。OPU 小字在上限格，不是第三個金額格。

#### S-2.1 自動拆
- GIVEN PLUS、未滿 40、第 2～3 次完整
- WHEN 帶入方案 A
- THEN 兩格：取卵 110000（6+5 併入）、植入 40000、上限 150000
- 觀測:從附表五金額欄看 | 只有取卵／植入兩格、取卵 110000、植入 40000、上限 150000、無形成金額格算對 | 用 PLUS、未滿 40、第 2 或第 3 次完整、方案 A 測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:第 2／3 次完整 15 萬在畫面上用兩格就能對上，不必再開形成金額格
  - Situation:選方案 A 後系統自動帶入
  - Known information:PLUS、未滿 40、第 2～3 次、方案 A
  - Missing information:無
  - Human decision:接受自動填或改手改（S-2.2）
  - Authority:同 S-1.1
  - External dependency:PLUS 表三筆拆法
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:重選方案 A 會重算自動值；已手改的路徑見 S-2.2
  - Audit/handoff requirement:畫面只留兩格
  - Observation:附表五金額欄無形成金額格

#### S-2.2 手改留存
- GIVEN PLUS 已自動填 取卵 110000／植入 40000
- WHEN 把取卵改成 90000 並存檔再打開
- THEN 取卵仍是 90000，後端不得算回 110000
- 觀測:從存檔後重整的附表五取卵格看 | 取卵仍是 90000 算對 | 用 S-2.1 自動填後把取卵改成 90000、存檔、再打開測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:對完表或特例後手改金額，下次打開還在
  - Situation:自動填 11／4 萬後，人把取卵改成 9 萬
  - Known information:自動值、自己改的 90000
  - Missing information:無
  - Human decision:改哪一格、改成多少
  - Authority:PLUS 兩格可改；3.0 兩格本輪維持既有行為（不在本條）
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:改到一半關頁未存 → 重開仍是自動值 110000；存檔成功後重開必須仍是 90000
  - Audit/handoff requirement:存檔留下手改後的兩格
  - Observation:存檔後重整取卵仍 90000

#### S-2.3 滿 40 第 1 次
- GIVEN PLUS、`first_subsidy_age` = 40、首次完整、低收入＝否
- WHEN 計算附表五金額
- THEN 取卵 80000（7+1 併入）、植入 50000、上限 130000
- 觀測:從附表五兩格看 | 取卵 80000、植入 50000、上限 130000 算對 | 用 PLUS、`first_subsidy_age`=40、首次完整、低收入＝否測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:滿 40 第 1 次仍先照算（7+1+5 → 兩格 8／5、上限 13 萬）
  - Situation:PLUS、首次、年齡 40
  - Known information:`first_subsidy_age`=40、首次、完整
  - Missing information:無
  - Human decision:接受先照算；本輪不收回兩格
  - Authority:同 S-1.1
  - External dependency:PLUS 表滿 40 第 1 次 7+1+5
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:不適用
  - Audit/handoff requirement:兩格 8 萬／5 萬
  - Observation:兩格。先照算。

### R-3: 系統 SHALL 用 first_time_subsidy_age 與 first_subsidy_age 鎖年齡且不重判
同一輪次數用 `first_time_subsidy_age`、金額用 `first_subsidy_age`，不重判。申請滿再來新開一筆，舊案不動。

**審的時候看什麼**
次數欄讀 `first_time_subsidy_age`，金額欄讀 `first_subsidy_age`，兩顆分開、同一輪不重判。申請日實務不改；新增附表五也不覆寫已存的 `first_subsidy_age`。次數用滿（6 或 3）再來是新開一筆，舊案列不動。新案才用新申請日與妻生日重算兩格年齡。沒有「同一案改回首次」這條路。

#### S-3.1 第 2 次不改年齡格
- GIVEN 已有 `first_subsidy_age`=35、`first_time_subsidy_age`=35
- WHEN 新增第 2 次附表五（申請日沒改）
- THEN 兩格年齡仍是 35
- 觀測:從主檔年齡欄看 | `first_subsidy_age` 與 `first_time_subsidy_age` 仍是 35 算對 | 用已有兩顆年齡=35 的案、申請日不變、新增第 2 次附表五測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:同一輪第 2 次附表五不要把年齡重算掉
  - Situation:已有第一次；申請日實務不改
  - Known information:已存兩顆年齡都是 35
  - Missing information:無
  - Human decision:不改申請日
  - Authority:同 S-1.1；新增附表五不得覆寫已存 `first_subsidy_age`
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:不適用
  - Audit/handoff requirement:主檔兩顆年齡欄仍是 35
  - Observation:主檔年齡欄

#### S-3.2 新開一筆重算
- GIVEN 舊案已用滿次數
- WHEN 新開一筆補助、新申請日、妻生日算出 40
- THEN 新案兩格年齡是 40，舊案列不變
- 觀測:從兩筆主檔年齡欄看 | 新案兩格是 40、舊案列年齡不變算對 | 用已用滿次數的舊案、再新開一筆、新申請日＋妻生日算出 40 測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:次數用滿再來＝新開一筆；舊資料不再動
  - Situation:舊案次數已滿（6 或 3）
  - Known information:舊案已滿；新申請日；妻生日
  - Missing information:無
  - Human decision:新開一筆，不走「同一案改回首次」
  - Authority:可建新主檔；不得改舊案列年齡
  - External dependency:無
  - Out-of-system action:人工建新案
  - Waiting/timeout behavior:不適用
  - Recovery:新案建到一半未存 → 舊案仍不動
  - Audit/handoff requirement:兩筆主檔並列
  - Observation:兩筆主檔

### R-4: 系統 SHALL 在上限格列出形成胚胎 OPU 小字且方案 C 走僅植入
附表五用 `fbt_date` → FBT → `opu_ivf_no` → OPU，列出形成胚胎的那張 OPU（`ivf_no`、取卵日、`sum_2pn`）。方案 C 不當完整。

**審的時候看什麼**
路徑是 `fbt_date` → FBT → `opu_ivf_no` → OPU。看得到的是那張 OPU 的 `ivf_no`、取卵日、`sum_2pn`，寫在上限格小字。方案 C 即使有植入日也只走僅植入，上限＝植入格，不是完整最高額。沒對到 FBT／OPU 就沒有這段小字。這輪不硬擋植入顆數。

#### S-4.1 有植入且 2PN>0
- GIVEN PLUS、有 `fbt_date` 對到 FBT，其 `opu_ivf_no` 的 `sum_2pn`>0，方案非 C
- WHEN 打開附表五
- THEN 看得到該 OPU 的 `ivf_no`、取卵日、2PN
- 觀測:從補助金額上限格內小字看 | 出現該 OPU 的 ivf_no／取卵日／2PN、且不是獨立金額列算對 | 用 PLUS、有 `fbt_date` 對到 FBT、`sum_2pn`>0、方案非 C 的測試案測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:不必另開單口頭對 OPU，就能在附表五看到形成胚胎的那張 OPU
  - Situation:現況附表五看不到 2PN，完整額只能猜
  - Known information:`fbt_date`、方案非 C
  - Missing information:沒對到 FBT／OPU 時沒有這段小字
  - Human decision:無（只讀小字，不另開金額格）
  - Authority:後台可讀 OPU／FBT；本輪不硬擋顆數
  - External dependency:實驗室 OPU／FBT（`sum_2pn`、`opu_ivf_no`）
  - Out-of-system action:現況 workaround 是另開單口頭對；本條要把對到的 OPU 寫進上限格
  - Waiting/timeout behavior:還沒有 `fbt_date` → 無小字，不擋存檔
  - Recovery:對不到就沒小字，金額仍走方案自動填
  - Audit/handoff requirement:小字帶 ivf_no／取卵日／2PN
  - Observation:上限格內小字（非獨立列）

#### S-4.2 方案 C
- GIVEN 方案 C、有 `fbt_date`
- WHEN 計算上限
- THEN 走僅植入，不是完整最高額
- 觀測:從附表五上限與植入格看 | 上限＝植入格、不是完整最高額算對 | 用方案 C、有 `fbt_date` 的案測
- Operational Context:
  - Actor:諮詢／行政
  - Goal:方案 C 只解舊凍胚也有植入日，不能當完整
  - Situation:選了 C，畫面上可能仍有植入日
  - Known information:方案 C、有 `fbt_date`
  - Missing information:無
  - Human decision:選 C 就接受僅植入
  - Authority:同 S-1.1
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:不適用
  - Audit/handoff requirement:上限＝植入格
  - Observation:上限＝植入格

### R-5: 系統 SHALL 只把 PHP 寫進本 worktree 且不切 27004 bind
27004 等另一 session 測完再把 bind 從主目錄改掛本 worktree。此前只寫本 worktree。

27004 是測試機容器，現在 bind 主目錄 `/path/to/ivf_platform`（ERP 分支）。本 feat 碼在 subsidy worktree；不切掛載時 27004 看不到 PLUS。等另一 session 測完再把 bind 改掛本 worktree；切之前只寫 worktree、不動主目錄、不開第二容器。

**審的時候看什麼**
27004 現在掛的是主目錄 ERP 分支，不是本 worktree。這輪改 PHP 只寫 worktree，27004 重整畫面應維持 ERP 行為。不切 bind、不動主目錄、不另開第二個容器。PLUS 畫面要等另一 session 測完、改掛本 worktree 之後才會出現。切掛載之前，27004 看不到 PLUS 是對的。

#### S-5.1 未切前
- GIVEN 27004 仍掛 `/path/to/ivf_platform`
- WHEN 本 worktree 改 PHP
- THEN 27004 畫面不變（另一 session 不受影響）
- 觀測:n-a:27004 重整畫面不在本 mothership repo 可執行。替代觀測:本 feat 的 diff 只含 subsidy worktree 路徑、不含主目錄 `/path/to/ivf_platform` 與容器 bind 設定 | 本 repo／本 worktree 無 27004 bind 變更、無主目錄 PHP 寫入算對 | 用本 feat 的 git diff 與檔案清單測
- Operational Context:
  - Actor:測試／維運（切 27004 bind 的人）；諮詢／行政不操作本條
  - Goal:本 feat 先把碼寫進 worktree，不打斷另一 session 正在測的 ERP 主目錄
  - Situation:27004 現掛主目錄；PLUS 畫面要等另一 session 測完再改掛
  - Known information:現掛路徑 `/path/to/ivf_platform`
  - Missing information:另一 session 何時測完
  - Human decision:本 feat 不切 bind；何時改掛由另一 session 決定
  - Authority:本 feat 不得改容器 bind、不得動主目錄、不得開第二容器
  - External dependency:27004 容器、另一 session
  - Out-of-system action:docker bind 切換（本 feat 不做）
  - Waiting/timeout behavior:切掛載之前 27004 看不到 PLUS；這是預期，不是故障
  - Recovery:若誤切，切回主目錄即可；本 feat 規格是根本不切
  - Audit/handoff requirement:本 feat 交付物只在 subsidy worktree
  - Observation:見本條 觀測的本 repo 替代（git diff／檔案清單）

## MODIFIED Requirements
- 既有 `calculateSubsidy3Amount`／`calculateSubsidy3AmountAdd`／`calculateSubsidy3AmountForSchedule5`（`controllers/backend/ivf.php` 與 `views/backend/ivf_subsidy_edit.php` 三處同一張表）：PLUS 切日＋形成併取卵後兩格。3.0 路徑數字不變（S-1.2 即 golden master）。
- 既有附表五新增／更新存檔：PLUS 兩格手改後不得覆寫回自動值（S-2.2）。3.0 存檔行為本輪不改。

## REMOVED Requirements
（無 —— 不刪 3.0 兩格邏輯、不刪次數上限 40 的既有切法。）

## 行為流程圖(R 級)
```
[R-1] 依 apply_date 切 3.0／PLUS 金額表
  主檔 apply_date
    < 2026-09-01 -> 整案 3.0 兩格表（39 切）
    >= 2026-09-01 -> PLUS 兩格（40 切）
  沒有 today 開關

[R-2] 形成併入取卵格、只顯示兩格
  PLUS 三筆 -> 畫面兩格（取卵+形成／植入）
  自動填後可手改；存檔不得算回

[R-3] 鎖年齡且不重判
  次數 -> first_time_subsidy_age
  金額 -> first_subsidy_age
  用滿 -> 新開一筆，舊案不動

[R-4] 上限格列出 OPU 小字；方案 C 走僅植入
  fbt_date -> FBT -> opu_ivf_no -> OPU
  方案 C -> 僅植入，上限=植入格

[R-5] 只寫本 worktree、不切 27004 bind
  27004 仍掛主目錄 -> 畫面不變
```

## Acceptance Criteria
- S-1.1～S-5.1 測試全綠（兩格數字與觀測位置都對上，不是改成三格、也不是用 today 切表）。
- 3.0 舊案兩格數字 golden master：同輸入，改動前後輸出逐列一致（S-1.2）。
- 低收入仍 15 萬（本輪不改低收入規則）。
- 顆數不硬擋；正式區／191 無寫入；180 不加欄除非使用者另准。
- 本 mothership 形狀關卡：`scripts/check-spec-gate.sh example/subsidy-3-0-plus/4-spec.md` exit 0。

## Out of Scope
- Revised。顆數 38 硬擋。低收入改。主目錄 ERP。today 開關。國健署正文衝突（1-discussion `[>]`）。191／正式區寫入。另開第二個 27004 容器。
- 以上都不進本 feat；國健署正文若跟 briefing 衝突另開討論，不在這裡改金額。
- 1-discussion 驗收雛形「術日 115.4.2、未滿 38、選 2 顆仍可存」本輪維持不做硬擋，故不另立 S；驗收是「存檔成功、不擋」＝本節排除硬擋。

Stage 3 對帳(逐場核對 3-prototype Demo Script)—— N/A：本手樣資料夾沒有 `3-prototype.md`，2-decision 也沒有「Stage 3／跳過」Owner Call。本輪不補 Stage 3、不代填 Demo verdict。1-discussion Real-world Context 的操作下落改由各 S 的 Operational Context 承接。

## Diff Budget
本節是估計，不是承諾。

| 區塊 | 檔 | 行(估) | 備註 |
|---|---|---|---|
| 畫面兩格／OPU 小字 | `views/backend/ivf_subsidy_edit.php` | ≤120 | 非測試碼 |
| 三處金額函式切日＋併格 | `controllers/backend/ivf.php` | ≤150 | 非測試碼 |
| 附表五新增／更新存檔 | 同檔或 model | ≤80 | 非測試碼；手改不覆寫 |
| 可選新欄 | `ivf_subsidy_schedule5.embryo_subsidy_amount` | 0（本輪不加） | 180 未准；見 DD-2 |
| 本 mothership 手樣 | `example/subsidy-3-0-plus/4-spec.md` + html twin | 1 組 | 本輪重寫 |
| 測試碼 | 產品樹 PHP 測試（若有） | ≤200 | 與非測試碼分開估；本 mothership 無 IVF 測試床 |

合計預期：產品樹 ≤4 檔／≤350 行非測試碼；測試碼另計。超支停下判 L1/L2。

## Dependencies
- 形成不落庫；畫面兩格，上限＝取卵＋植入。理由：180 未准不加欄，形成用上限−取卵−植入還原（若之後要還原）。
- 27004 切掛載：等另一 session。理由：現掛主目錄 ERP，本 feat 不得搶 bind。
- 不依賴其他 mothership feature。不新增外部套件。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: applicable
- Trigger(s): Feature Risk = high（涉金流：補助金額計算與存檔）、涉及既有金額函式寫入路徑與手改後的一致性（Transaction／Idempotency：自動值與手改不得只成功一筆）、三個以上參與點（編輯畫面／三處金額函式／附表五存檔）共同改 PLUS 切日與兩格
- Design source: 既有 pattern —— 3.0 已用 `calculateSubsidy3Amount` 三處同一張表、`first_subsidy_age`／`first_time_subsidy_age`、附表五兩格；PLUS 切日與形成併取卵是 new local design（無獨立 ADR；2-decision 選 1A+2B+3A+4A，畫面兩格已回寫，見 DD-1）

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| 補助編輯畫面(`views/backend/ivf_subsidy_edit.php`) | 顯示 PLUS／3.0 兩格、手改、上限格 OPU 小字；不自己發明第三格 | 不擁有金額表（只呈現與收集手改） | → 三處金額函式、→ 附表五存檔 | 不得直寫 27004 bind；不得改主目錄 ERP；不得把形成做成獨立金額格 |
| 三處金額函式(`calculateSubsidy3Amount`／Add／`calculateSubsidy3AmountForSchedule5`) | 依主檔 `apply_date` 切 3.0／PLUS，PLUS 把形成併進取卵格 | **擁有**本次金額計算結果（自動值） | → 主檔申請日與兩顆年齡、→ 方案／次數／低收入 | 不得看 today；不得改 `first_subsidy_age` 已存值 |
| 附表五存檔（同檔或 model） | 唯一把兩格手改寫回去的地方；有手改就不得算回自動值 | **擁有**已存附表五兩格 | → 畫面 POST 的兩格 | 不得由 GET／只讀重整覆寫手改；不得寫 191／正式區 |
| 27004 bind／主目錄 | 本 feat 不改 | 不擁有（另一 session） | — | 本 feat 任何模組都不得改 bind、不得寫主目錄 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 三處金額函式（同一張表） | in:主檔 `apply_date`、方案、次數、兩顆年齡、低收入；out:取卵格、植入格、上限 | 申請日缺則走既有 3.0 路徑（本輪不新發明錯誤碼） | 三處必須同一張表；只改一處會讓畫面／新增／後端數字分叉。自動值三欄（取卵／形成／植入）在記憶體併成兩格後一次回傳，不會只回一格 | 3.0 路徑數字不變（additive 切日）；既有呼叫端仍走同函式名 |
| 附表五存檔 | in:兩格手改或自動值；out:重開仍是存進去的兩格 | 本輪不新增存檔錯誤語意 | **兩格與上限在同一次存檔寫入**（只成功一格＝失敗，必須整筆未改）。形成不落庫，上限＝取卵＋植入 | 3.0 存檔行為不變；PLUS 打開可改 |
| FBT→OPU 只讀 | in:`fbt_date`；out:上限格小字（ivf_no／取卵日／2PN）或沒有小字 | 對不到 → 無小字，不擋存檔 | 唯讀：不開交易寫 OPU／FBT | internal only —— 不新開公開 API |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| `calculateSubsidy3Amount`（三處同一張表） | 依 `apply_date` 切表並把 PLUS 形成併進取卵格 | ← 畫面／新增附表五／後端 | stateless；讀主檔欄位 → 回兩格＋上限 | 缺申請日走 3.0；不吞成 PLUS | 固定 `apply_date` 2026-08-31 vs 2026-09-01 斷言兩格數字（S-1.1／S-1.2／S-1.3／S-2.1／S-2.3） |
| 附表五存檔手改旗標（既有或本輪加上「有手改就不要蓋」） | 重開後兩格仍是手改值 | ← 畫面 POST | 狀態住已存附表五兩格 | 存檔失敗整筆未改 | 取卵改 90000 存檔再讀（S-2.2） |
| 上限格 OPU 小字 | `fbt_date`→FBT→`opu_ivf_no`→OPU 列 2PN | ← 畫面；→ OPU／FBT 讀 | stateless 只讀 | 對不到 → 不顯示小字，往上不報錯 | 有／無 `fbt_date`、方案 C（S-4.1／S-4.2） |

### Design Constraints
- 必須:三處金額函式同一張表；PLUS 畫面只有兩格；切表只看主檔 `apply_date`；手改與存檔同一次寫入；OPU 小字只讀、放上限格。
- 禁止:today 開關；形成金額第三格；本 feat 改 27004 bind／主目錄／191；覆寫已存 `first_subsidy_age`；同案改回首次。
- Extension point:180 准了才加 `embryo_subsidy_amount`（本輪不加）。
- Known design limit:
  ①**形成不落庫** —— 若之後要還原形成金額，只能用上限−取卵−植入；沒有獨立欄可對帳（DD-2）。
  ②**27004 本輪看不到 PLUS** —— bind 未切是預期，不是缺陷（S-5.1）。
  ③**滿 40 第 1 次 8 萬看起來怪** —— 先照算，本輪不收回兩格（2-decision OC-3）。
  三項皆為既有鎖的顯性化，不新增產品行為。

## Verification Profile(G2 一併審)
- lane: full（Risk: high 命中自動升 Full 清單「金流/交易」與「核心醫療業務邏輯」，不得 fast；本節 Risk = Feature Risk）
- Risk: high（判準:涉金流 —— 附表五補助金額計算與存檔會改病患可領金額。手樣舊值 `medium` 不是合法 Feature Risk。無法寫成 normal：金額對錯就是金流後果，不是純文案。）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得用 today 切表（S-1.2；Out of Scope）
  - 不得把 PLUS 畫面做成三格形成金額（R-2；生命週期退役格）
  - 不得在手改後算回自動值（S-2.2）
  - 不得覆寫已存 `first_subsidy_age`（S-3.1）
  - 不得把方案 C 當完整最高額（S-4.2）
  - 不得改 27004 bind／主目錄／191／正式區（S-5.1；Out of Scope）
  - 不得硬擋顆數、不得改低收入（Out of Scope）
- Required layers:Full test suite（本 mothership 形狀：`check-spec-gate.sh` 本檔）、Changed-line coverage（產品樹三處金額函式若在實作 session 改到）
- Conditional layers:Real execution（只有另一 session 切 27004 bind 之後才跑畫面；本 feat 未切則不列入 Final Fresh Run）
- Explicitly excluded layers:Mutation（本 mothership 與 IVF PHP 5.3.3 測試機都未配 mutation 工具鏈）、e2e/Playwright（附表五在另一 repo／測試機；本 mothership 無該前端）、Race/stress（本期無新併發寫入路徑）
- Final fresh entry point:`scripts/check-spec-gate.sh example/subsidy-3-0-plus/4-spec.md`
- Reliability triage:(Full 與 Fast lane 都必答)
  - Concurrency: n-a — 本期無新併發寫入路徑；手改是單一存檔覆寫，不是雙人同時編（Out of Scope 未做衝突偵測）
  - Idempotency: applicable — 手改後重開不得算回自動值（S-2.2）；同一申請日重算必須仍得同一兩格自動值，除非已有手改
  - Timeout/retry: n-a — 無外呼；FBT／OPU 對不到就沒小字，不重試、不擋存檔（S-4.1 Recovery）

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 舊案被 today 或附表五日誤切 PLUS | 8/31 立案第 2 次變成 15 萬 | S-1.2 兩格出現 150000 | Full test suite（S-1.2 固定 `apply_date`=2026-08-31） | — |
| PLUS 畫面出現形成金額第三格 | 行政對錯格、上限被加三次 | 附表五出現第三個金額輸入 | Full test suite（S-2.1 斷言無形成金額格） | — |
| 手改被後端算回自動值 | 特例金額被蓋掉 | 取卵 90000 存檔後變回 110000 | Full test suite（S-2.2） | — |
| 方案 C 走完整最高額 | 僅植入案領到完整額 | 上限≠植入格 | Full test suite（S-4.2） | — |
| 本 feat 誤切 27004 bind | 另一 session 的 ERP 測機被換成 PLUS 樹 | bind 路徑不再是 `/path/to/ivf_platform` | 本 mothership：S-5.1 替代觀測（diff 不含 bind） | 27004 畫面本身 n-a（另一 session） |

## Drafting Decisions(草擬自判,待人審)

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 畫面只給兩格（形成併入取卵）。2-decision 已回寫選定 2B；不再是兩份打架 | 完工時使用者改兩格；討論期 2A 三格改列 Rejected。R-2 不改回三格 | `example/subsidy-3-0-plus/2-decision.md` Decision 1A+2B+3A+4A；本檔 R-2；1-discussion 歷史問答仍記當時三格 | 若改回三格，R-2／S-2.1～S-2.3 與生命週期退役格都要改 | 待人審 |
| DD-2 | 本輪不加 `embryo_subsidy_amount`；形成不落庫 | 180 未准不加欄；形成用畫面兩格＋上限表達 | 既有手樣；2-decision ADR 檢查「形成不落庫」 | 要補 migration 與還原邏輯，Diff Budget 與 S-2.2 存檔契約都要改 | 待人審 |
| DD-3 | G1 以對話鎖定視同方向可寫本手樣規格；frontmatter 不代填 Human verdict／G2 PASS | 本輪任務禁止代填 Human verdict；2-decision 已是 approved，但 G2 仍待人 | 本輪 owner 指示「Leave verdict empty」；`2-decision.md` frontmatter `status: approved` | 若 G1 被否認，本檔 R/S 要停 | 待人審 |
| DD-4 | Feature Risk = high，不是手樣舊值 medium，也不是 normal | 模板只准 `normal\|high`；涉補助金額（金流）→ high。無法正當化 normal | `_templates/4-spec.md` Risk 判準「涉金流 → high」 | Verification Profile 與 Design Boundary 觸發條件⑨都要重寫 | 待人審 |
| DD-5 | Stage 3 對帳整節 N/A，不補 3-prototype、不代填 Demo verdict | 手樣沒有 3-prototype；本輪禁止做 Stage 3 | 本資料夾無 `3-prototype.md`；1-discussion 有 Real-world Context，操作下落改寫進各 S Operational Context | 若後補 Stage 3，要逐場對回 R/S 或 Out of Scope | 待人審 |

### 內部技術選擇(下層,告知即可)
- 三處金額函式繼續共用同一張表，不新開第四個計算入口。
- OPU 小字放上限格，不新開獨立列（與 R-4 同一鎖，這裡只記實作落點）。
- 本 mothership Final Fresh Run 只跑 `check-spec-gate.sh` 本檔；IVF PHP 實跑留在產品 worktree／另一 session。

## Test Skeletons(選配)
```
test_s_1_1_plus_first_complete_two_cells
test_s_1_2_old_case_second_stays_3_0
test_s_1_3_plus_second_complete_11_plus_4
test_s_2_1_auto_split_no_formation_cell
test_s_2_2_manual_oocyte_90000_persists
test_s_2_3_age_40_first_8_plus_5
test_s_3_1_second_schedule5_keeps_age_35
test_s_3_2_new_case_recomputes_age_40
test_s_4_1_opu_2pn_smallprint_in_cap_cell
test_s_4_2_scheme_c_implant_only
test_s_5_1_worktree_only_no_27004_bind
```
測的是畫面兩格：第 1 次 10+5、第 2 次 11+4、滿 40 第 1 次 8+5，以及手改取卵 90000 存檔後不被算回。申請日 9/1 vs 8/31 各一筆。

## 確認紀錄
- R 範圍沿用既有手樣 R-1～R-5（兩格／切日／年齡鎖／OPU 小字／只寫 worktree）| 2026-08-29
- S 逐條對應既有 S-1.1～S-5.1，補齊觀測三截與 Operational Context | 2026-08-29
- 1-discussion 四條驗收雛形：1→S-1.1（兩格；歷史問答仍記當時三格）；2→S-1.2；3→S-4.1；4→Out of Scope（不硬擋）| 2026-08-29
- Stage 3 對帳 N/A（無 3-prototype）| 2026-08-29
- Verification Profile 填畢（lane: full；Risk: high）| 2026-08-29
- 2-decision 已回寫選定 2B 兩格；DD-1 不再說兩份打架 | 2026-08-29
