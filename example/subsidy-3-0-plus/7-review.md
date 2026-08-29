---
feature: subsidy-3-0-plus
stage: 7-review
status: draft
verdict: PASS
owner: independent-reviewer
updated: 2026-08-29
---

# 7. 驗證 — 試管補助 3.0 PLUS

> ## Reviewer 閱讀動線
>
> | 步 | 讀哪節 | 這步問的唯一問題 |
> |---|---|---|
> | 1 | **Verdict** | 判定是什麼?門檻表每一格是不是都有證據? |
> | 2 | **Exit Checklist** | 還缺什麼才能出貨?哪幾項要 owner 親自動? |
> | 3 | **附錄:本輪特有** | 本輪的爭點/分歧在哪,誰對? |
> | 4 | **Known Limits** | 有沒有一條是 owner 不能接受的? |
> | 5 | **抽驗一列** | 從 Coverage Matrix 中位列 `檔:行` 去看。對得上就信剩下的,對不上就整份退回 |

**Human PASS**（2026-08-28）。七張 named shots 已收。本輪只回寫畫面兩格觀測，不重填 Human verdict。

## 讀取順序聲明

1. 獨立審查（≠ 實作 owner IVF後台）先讀 `4-spec.md`、`5-tasks.md`、worktree vs `fe927c0` 的兩支 PHP，**未先讀** `6-implementation-notes.md`。
2. 另有獨立 T-review：T-1～T-4 靜態 PASS，無必須修。
3. 彙整者不降級任何 F。無 🔴。
4. 畫面已跑：七張 named shots（進場附表六→已生成附表五）。27004 已還 ERP 主目錄，PHP 覆寫已還原。

## Coverage Matrix

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | 靜態 `ivf.php:7553-7557` 未滿40第1次內部 100000／0／50000 → 畫面 10／5。畫面未跑 | unverified |
| S-1.2 | 靜態 `ivf.php:7578-7590` 3.0 未滿39第2次 60000／40000；非 PLUS 不 keep。畫面未跑 | unverified |
| S-1.3 | 靜態 `ivf.php:7558-7561` 第2–3次內部 60000／50000／40000 → 畫面 11／4。畫面未跑 | unverified |
| S-2.1 | 同 S-1.3；`ivf_subsidy_edit.php:2721-2726` PLUS 兩格解 readonly。畫面未跑 | unverified |
| S-2.2 | 靜態 happy path：手改取卵 keep POST、再開仍是手改兩格。畫面未跑 | unverified |
| S-2.3 | 抽驗：`controllers/backend/ivf.php:7568-7571` 滿40第1次內部 70000／10000／50000 → 畫面 8／5 | unverified |
| S-3.1 | 靜態 `ivf_subsidy_edit.php:3030-3038` 已有 first_subsidy_age 不覆寫。畫面未跑 | unverified |
| S-3.2 | 歸零＝人工新開，本輪無碼 | n-a |
| S-4.1 | 靜態 `ivf.php:7666-7676` 只讀 lookup。畫面未跑 | unverified |
| S-4.2 | 靜態 `ivf.php:7609-7611` 方案 C 清取卵／形成。畫面未跑 | unverified |
| S-5.1 | `docker inspect`：27004 仍掛 `/path/to/ivf_platform` | ✅ |
| 既有測試套件(回歸) | 本 repo 無補助金額自動化測試 | n-a |

5-tasks Verify 形狀（本輪有跑）：T-1 `2026-09-01`×4；T-2 `胚胎形成`×3；T-3 `calcSchedule5AgeAndAmount` 對 first_subsidy_age×1（註解行，形狀弱）；T-4 `sum_2pn`×11（含舊 OPU 碼）。

## Verification Evidence

- Source SHA: 未 commit（worktree dirty，基底 `fe927c0`）
- Final Fresh Run ID: n-a（gauntlet 降級）
- Entry point: 獨立碼審 + T-review + grep 形狀
- Toolchain: 人工；PHP 5.3 靜態掃

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| grep T-1 cutoff | `rg -n "2026-09-01" controllers/backend/ivf.php views/backend/ivf_subsidy_edit.php` | pass | 4 處 | |
| grep T-2 兩格 | `rg -n "胚胎形成" views/backend/ivf_subsidy_edit.php` | pass | 3 處（形成併取卵／hidden wrap，不是第三金額格） | |
| grep T-3 年齡 | `rg` 對 `calcSchedule5AgeAndAmount` + `first_subsidy_age` | pass | 1 處（註解行） | |
| grep T-4 2PN | `rg -n "sum_2pn"` | pass | 11 處（含舊碼） | |
| docker bind | `docker inspect` 27004 volume | pass | 仍主目錄 | |
| Full test suite | | n-a | | 無補助金額自動化測試 |
| Real execution | 27004 掛本樹後走 S-1.1～S-4.2 | unverified | | 另一 session 占用 |
| Evidence gauntlet | | n-a | | 4-spec 未列 Required layers |

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 無 today 開關 | `isSubsidy3PlusByApplyDate` 只比 `2026-09-01` | pass |
| 3.0 舊案後端覆寫 | 非 PLUS 時 `shouldKeepPosted` 回 false | pass |
| 低收入仍 15 萬 | 基數 10+0+5 | pass（static） |
| 顆數不硬擋 | 本輪無 embryo-count block | pass |
| 正式區／191 無寫入 | 只寫 worktree | pass |
| 180 不加欄 | `unset embryo_subsidy_amount`（`1504`、`1650`） | pass |
| 不寫 ivf_fbt／ivf_opu | lookup 只有 select+get | pass |

## 執行記錄

手動實作，無 dev-run。

## 現象證據

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 附表五兩格＋上限。申請日填 9/1 | 已拍 plus-two-cells／v30-two-cells。靜態：`ivf.php:7553-7557` | ❌ |
| S-1.2 | 同一舊案第二次附表五 | 未跑。靜態：3.0 6+4、不 keep | ❌ |
| S-1.3 | 兩格加總 15 萬（11／4） | 未跑。靜態：`7558-7561` | ❌ |
| S-2.1 | 附表五兩格 11／4，無形成金額格 | 未跑。靜態：同 S-1.3 + `2721-2726` | ❌ |
| S-2.2 | 手改取卵 90000 存檔後不被算回 | 未跑。靜態 happy path keep POST | ❌ |
| S-2.3 | 兩格 8／5 萬 | 未跑。抽驗列：`7568-7571` | ❌ |
| S-3.1 | 主檔年齡欄仍 35 | 未跑。靜態：`3030-3038` | ❌ |
| S-3.2 | 兩筆主檔 | 人工新開，本輪無碼 | n-a |
| S-4.1 | 看得到 OPU ivf_no／取卵日／2PN | 未跑。靜態：`7666-7676` | ❌ |
| S-4.2 | 上限＝植入格 | 未跑。靜態：`7609-7611` | ❌ |
| S-5.1 | 27004 重整仍是 ERP | docker 仍掛主目錄 | ✅ |

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 補助行政 | 9／1 新案算出畫面 10／5 | 開附表五、選方案 A | 申請日在主檔 | 未實跑 | 靜態數字對 |
| S-2.2 | 補助行政 | 手改取卵後再打開還在 | 改兩格、存、重整 | 無 | 改方案／次數會先重算蓋手改（F-9） | 存再開走 derive，未實跑 |
| S-3.1 | 補助行政 | 第2次不要改金額年齡 | 新增附表五 | 無 | 改申請日仍會 refresh 年齡（F-10，非 S-3.1） | 靜態符合 |
| S-4.1 | 補助行政 | 看形成胚胎那張 OPU | 填 fbt_date | 對不到仍可存 | location 未過濾；多 ivf_no 取 max 2PN（F-11） | 只讀，不擋存 |
| S-5.1 | 開發 | 另一 session 不受影響 | 只寫 worktree | 等對方測完再掛 | 無 | 符合 |

## Design Integrity Check

契約：只動補助編輯／附表五金額。不碰 PGS／報告。當 applicable。

1. 依賴反向：未命中。
2. 資料所有權：未命中。FBT／OPU 只讀。
3. 相容性破壞包成新增：未命中。`subsidy_version` 仍 `3.0`。形成不落新欄。
4. 一致性：JS／PHP 方案拆分不完全同一套（F-18）。PLUS keep 以畫面 POST 為準。🟡，非 🔴。
5. Test seam：觀測是畫面，本輪無自動化。Coverage unverified。
6. Known limit 被悄悄解決：未命中。27004 未掛、180 不加欄。

## Standards Axis

T-review 與獨立 G3 預審並列。無 🔴。

- F-1 🟢 新 PHP 只用 `array()`／`isset ? :`，無 `[]`／`??`／`fn()`
- F-2 🟢 切日只有 `2026-09-01`，無 today（`ivf.php:7496`、view `2609`）
- F-3 🟢 PLUS 兩格可改；3.0 兩格 readonly＋後端覆寫
- F-4 🟢 已有 `first_subsidy_age` 不覆寫（view `3030-3051`）
- F-5 🟢 OPU 只讀、帶 cNumber、同日 `id DESC`、不擋存、不改金額
- F-6 🟢 3.0 39 切兩格數字不變；低收入 15 萬
- F-7 🟢 180 未加 `embryo_subsidy_amount`（`1504`、`1650`）
- F-8 🟡 `shouldKeepPostedSubsidy3Amounts`（`ivf.php:7520-7533`）不理 `subsidy_amount_manual`。T-2 寫要看旗標；實作是 PLUS＋兩格有值就 keep（對 S-2.2 更寬）。建議對齊 tasks 或改成只看 manual
- F-9 🟡 `calculateSubsidy3Amount` 會 `resetSubsidyAmountManual` 並重算。PLUS 改申請日／次數／方案會先蓋手改；存再開仍走 derive
- F-10 🟡 `refreshFirstSubsidyAgeFromApply`（view `1906-1926`）改申請日／生日仍覆寫年齡。S-3.1 申請日沒改時安全
- F-11 🟡 `$location` 傳了沒用；FBT 對不到改走 form `opu_date`；多 `ivf_no` 用 `pickOpuWithMost2pn`（`7756-7770`）。只影響顯示
- F-12 🟡 編輯 dialog 金額 id 重複（舊帳）。`query2` 只抓進行中（通常一筆）
- F-13 🟡 形成已併取卵；若髒資料上限≠兩格加總，無第三欄可對（不還原第三格）
- F-14 🟡 公開 `calculateSubsidy3Amount` AJAX 吃 apply_date 但不做 plan split。本頁已不打它
- F-15 🟡 `5-tasks.md` T-1／T-2／T-3 仍未勾；notes 當都做了
- F-16 🟡 T-4 verify 的 `sum_2pn` 含舊碼
- F-17 🟢 27004 仍主目錄
- F-18 🟡 JS 對非方案 `1.` 仍吃 `inside_operation`；PHP 只在方案 `1.` 吃。PLUS keep 以 JS 為準

另：畫面 `apply_date` 空白時 JS 當 3.0、後端空白才查主檔再 keep。獨立 G3 與 T-review 都不列 🔴（正常畫面申請日會在）。列入 Known Limits。

## Spec Axis

- R-1 切表 — **符合（靜態）**。`isSubsidy3PlusByApplyDate` 只比主檔／POST `apply_date` 與 `2026-09-01`。無 today。空值當 3.0；空白才查主檔。
- R-2 兩格 — **符合（靜態）**。PLUS 解 readonly、形成併取卵、無形成金額格。3.0 兩格＋後端覆寫。形成不落庫。手改存檔 keep POST。T-2 旗標字面有偏差（F-8），行為仍「手改不蓋」。
- R-3 年齡鎖 — **符合 S-3.1（靜態）**。已有值不覆寫。S-3.2 無碼。改申請日仍 refresh（F-10），不在 S-3.1 GIVEN。
- R-4 形成胚胎 OPU — **符合（靜態結構）**。只讀、cNumber、id DESC、不擋存、不改金額。方案 C 走拆分。額外 heuristic 見 F-11。
- R-5 測試掛載 — **符合**。27004 未掛本樹。

T-review：T-1～T-4 皆 PASS，無必須修。

對照 6-notes（步 4 才讀）：作者多數自述與碼相符。未寫 location 死參數、`pickOpuWithMost2pn`、改 times／plan 會蓋手改、公開 AJAX 無 plan split。T-2 keep 不看 flag，notes 比 tasks 誠實。行號略舊。

## 變更架構圖

```
主檔 apply_date >= 2026-09-01 ?
        |
        +-- 是 PLUS：兩格可改；後端 keep POST（兩格有值）
        +-- 否 3.0：兩格 readonly；後端重算
附表五 fbt_date + cNumber --> ivf_fbt (id DESC) --> ivf_opu（只讀列，不進金額）
```

靜態金額（A／B、非低收入）。內部三筆；畫面只見取卵格／植入格：

| 案例 | 內部取卵 | 內部形成 | 內部植入 | 畫面取卵 | 畫面植入 | 上限 |
|---|---|---|---|---|---|---|
| S-1.1 PLUS 35 首次 | 100000 | 0 | 50000 | 100000 | 50000 | 150000 |
| S-1.2 3.0 35 第2 | 60000 | — | 40000 | 60000 | 40000 | 100000 |
| S-1.3／S-2.1 PLUS 35 第2 | 60000 | 50000 | 40000 | 110000 | 40000 | 150000 |
| S-2.3 PLUS 40 首次 | 70000 | 10000 | 50000 | 80000 | 50000 | 130000 |

## Diff

未 commit。相對 `fe927c0`：

- `controllers/backend/ivf.php`：add／update keep、切日、基數表、方案拆、`lookupFormingEmbryoOpu`
- `views/backend/ivf_subsidy_edit.php`：兩格、PLUS JS、年齡鎖、OPU AJAX
- `docs/dev/STATUS.md` 看板一列

抽驗請看 `ivf.php:7568-7571`。

## Verdict

**PASS**（Human，2026-08-28）。七張圖 + 年齡／手改已看。

| 門檻 | 證據 | 過? |
|---|---|---|
| 本次 S 全綠 | 靜態對得上；畫面除 S-5.1 皆未跑 | 否（缺現象） |
| 既有全綠 | 無自動化回歸 | n-a |
| 現象證據逐 S 相符 | 七張 named shots | 是（首申 10／5 無獨立案，見 Known Limits） |
| Evidence 契約 | gauntlet 降級 | 降級 |
| 無 🔴 | T-review + 獨立 G3 皆無 🔴 | 是 |

Human 已勾 PASS。首申 10 萬／5 萬仍無獨立案，不擋這輪。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 27004 已拍七張後還原 ERP；首申 10 萬／5 萬無獨立案 | 高 | 等另一 session 測完再掛，重跑現象 |
| 2 | 未 commit，無 Source SHA | 中 | 你點頭才 commit |
| 3 | 形成靠上限還原，無新欄 | 低 | 規格允許，park |
| 4 | keep 不看 manual 旗標（F-8） | 中 | 對齊 tasks 或承認「PLUS 一律 keep POST」 |
| 5 | 改方案／次數會先蓋手改（F-9） | 中 | 掛樹後看要不要改 |
| 6 | OPU：location 未用、opu_date fallback、max 2PN（F-11） | 低 | 寫進 spec 或拿掉 |
| 7 | 滿40第4–6次基數 0 | 低 | 次數上限 3，park |
| 8 | 髒資料上限≠兩格加總時無第三欄可對 | 低 | park |
| 9 | 畫面申請日空白時 JS 當 3.0、後端查主檔再 keep | 低 | 正常畫面申請日會在；park |
| 10 | S-3.2 歸零＝人工新開 | — | 本輪不實作 |

## Exit Checklist

- [ ] **Design Boundary finding 全數處置**：無未授權 Boundary。🟡 尚未 owner 接受或 park 落點逐條簽名
- [ ] Quiz：掛樹實跑後再出
- [ ] 整合回歸：未跑。工作樹 dirty
- [ ] PR → develop：未開
- [ ] 4-spec delta 已併入 `docs/specs/`：未做
- [ ] STATUS.md 已更新為 shipped：否
- [ ] 7-review frontmatter status: shipped：否
- [ ] 7-review.html 已產生：本輪重產
- [ ] feature branch 已刪／worktree 已清：否

## 附錄:本輪特有

### A1　為什麼不是 REQUEST_CHANGES

上一份 HTML 把「畫面申請日空白 + keepPosted」列 🔴。獨立 G3 與 T-review 重看後：正常編輯申請日在主檔也在畫面；`query2` 進行中通常一筆；四 T 靜態 PASS。沒有 🔴，改回 PRE-REVIEW。那條改列 Known Limits #9。

### A2　掛樹後先走這五條

S-1.1（9／1 兩格 10／5）、S-1.2（8／31 仍 3.0 兩格）、S-1.3（第2次 11／4）、S-2.2（手改取卵存再開）、S-4.1（fbt_date 列出 OPU）。

### A3　對照作者 6-notes

多數相符。沒寫 F-9／F-11／F-14。T-2 keep 不看 flag，notes 比 5-tasks 準。T-1～T-3 檔案未勾。
