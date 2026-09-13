---
feature: five-station-simplify
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站簡化 change spec（Implementer C：anti-hollow）

> 基準:main tip `fdd39c5`（#310 Human Demo ACCEPTED 已合）。Lane = **full**。契約不 bump。
> 本 hop **只寫** `4-spec.md` + `4-spec.html`（`scripts/build-stage4-html.py --action`）。不改 `_templates/`／`graph.yaml`／`scripts/` 牙、不 bump `devflow-contract.json`、不改 `STATUS.md`／`HISTORY.md`、不開 Stage 5、不發明 G2 PASS、不合併。
> Decision 正本:`docs/dev/five-station-simplify/2-decision.md`（1A+2A+3A+4A+5A+6A+7A；OC-1～OC-11 ✅；G1 `verdict` PASS）。`3-prototype.md` `status: approved`；`Human verdict: ACCEPTED | role=母版 owner | scenario=AC-1`；attestation `human:rick @ 2026-09-14`。
> 本檔定義 F1／F2／F3 **必須滿足**的契約。本 PR 不實作那三刀。本 slug Stage 5–7（G2 之後）只准落地 **F1 annex + teeth（`scripts/`／annex）**；F2 coordinator 與 F3 cut **不在**本 slug Stage 5–7。
> C 線：每個 SC-1…SC-13 至少一條 S；M→R/S 去向齊；OC 掛 S-id；rewrite cap 數字鎖給 F2 計數器（落點交 F2，OC-3／Q10）；1B／2B／4C／6B／7C 進 Non-Goals，Stage 5 不得重開。
> 獨立於 A／B 線 Stage 4；未讀他線 4-spec。`verdict` 留空，由人類 G2 填。

## 補助模組生命週期（預覽）

主詞是「五站路線別名 + F1 拒收牙 + F2 計數／前進 + F3 新 slug 預設」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：五站別名對照、RP-1…RP-16 最小拒收集、rewrite 三 cap 計數器契約、F0→F3 分刀範圍、Must-keep／OC 掛 S 表
- 改行為（相關一格）：F1 起 `scripts/`／annex 咬 RP 與 dual-read 誠實；F2 起 coordinator 評表 A／B；F3 起新 slug 預設五站。本 hop 只把契約寫進本檔
- 退役：沒有
- 不動：七檔名、G1／G2／`ACCEPTED` token、既有 graph／Stage 1–4 模板、本 slug 舊 7、Fast 物質、第二條 ID 鏈

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「例行 G1／S3-ACCEPTED／G2 讓方向、互動、契約三次都要等人」 | 本方案處理 | S-1.2、S-1.3、S-1.4 |
| 「Treat as PASS／都過／可以落成 verdict: PASS，審查物質沒進人腦」 | 本方案處理 | S-3.1、S-3.2 |
| 「摺站若只殺等待、卻讓 Spec／Build 拿掉 ID 鏈、反模糊、T 四欄、acceptance seam」 | 本方案處理 | S-2.1、S-2.2、S-2.3、S-2.4、S-2.5 |
| Journey「owner chat 蓋章；方向卡沒被讀完也過」 | 本方案處理 | S-3.1、S-4.2 |
| Journey「Demo 欄空、chat 仍准開 Stage 4」 | 本方案處理 | S-4.1、S-4.2 |
| Journey「實作者若省四欄／seam，勾選假完成」 | 本方案處理 | S-2.2、S-2.3 |
| Journey「採用現場踩洞靠口頭中繼」 | 刻意維持 | Out of Scope：本包不建回報口 |
| Workaround「Agent 把口頭章落進 md 頂欄」 | 本方案處理 | S-3.1、S-4.2 |
| Workaround「採用洞進 dispatch-accounting-symmetry，不進 public issue」 | 刻意維持 | Out of Scope：public repo 禁收公司路徑 |
| Exception「Fast 仍吃 G2 物質」 | 刻意維持 | Out of Scope：不廢 Fast；本檔 Verification Profile 仍 full |
| Exception「in-flight 整段舊 7」 | 本方案處理 | S-5.1、S-5.2 |
| Exception「F0–F2 母版新開改版軌仍舊 7」 | 本方案處理 | S-8.1、S-8.3 |
| Exception「[Assumption] 採用現場仍 chat 蓋章」 | 仍待驗 | S-6.2、S-6.3；Assumption refs Q6 |
| Exception「後站會用『已經五站了』省略 M11／M3／M1」 | 本方案處理 | S-2.1、S-2.7 |
| Exception「A1／A2 共寫 1-discussion.html」 | 仍待驗 | Known limit：F1 annex 核 dest；本檔不選定分檔 |
| 「marketplace 可換 hops，doctor 仍可因 2.0.0 握手綠」 | 本方案處理 | S-5.5、S-5.6、S-5.7 |
| 「本 slug = live freeze 樣本」 | 本方案處理 | S-5.2 |
| Q8 dual-read 2.1.0 欄位與舊檔不紅缺省 | 本方案處理 | S-5.4；欄位名仍 F1 annex（OC-3） |
| Q10 coordinator event 與 rewrite cap 計數落點 | 本方案處理 | S-7.4 |
| Q11 空 attestation 五站後是否仍機械拒 | 本方案處理 | S-4.2 |
| M1–M16 帶走表 | 本方案處理 | S-6.1；Must-keep Disposition 16 列 |
| rewrite cap hop≤2／Decide≤1／Goal reopen≤1 | 本方案處理 | S-7.1、S-7.2、S-7.3、S-7.4 |
| 「本 hop 不改模板、不送 G1」 | 刻意維持 | S-8.4（本 hop 改成不送 G2、只寫 4-spec） |

## Must-keep Disposition

語法:`M11 → R-x/S-y | Non-Goal:<reason>`。不另發 ID 鏈。M15／M16 是**約束**，不是 Non-Goal。

| M | 去向 | 下落 |
|---|---|---|
| M1 ID 鏈；測試名含 S-id | 本方案處理 | S-2.5 |
| M2 圍欄 | 刻意維持 | Out of Scope：本 slug 不改圍欄正本；實作者仍禁讀 1／2／3 補洞 |
| M3 反模糊 | 本方案處理 | S-2.4 |
| M4 Real-world→Demo→OC | 本方案處理 | S-4.1、S-4.3 |
| M5 人寫 ACCEPTED／Ship PASS | 本方案處理 | S-3.1、S-3.2 |
| M6 G3 Evidence 八點 | 本方案處理 | S-3.2（Ship 物質不因摺站省略） |
| M7 Profile + fast+high 拒 | 刻意維持 | 本檔 Verification Profile；Fast 仍吃 G2 物質 |
| M8 DBC 條件式 | 刻意維持 | 本檔 Design Boundary Contract |
| M9 Files ⊆ 5-tasks | 本方案處理 | S-2.2 |
| M10 驗證五律 | 本方案處理 | S-2.3（無原始輸出 → 未完成） |
| M11 T seam + 四欄 | 本方案處理 | S-2.2、S-2.3 |
| M12 author≠approver | 刻意維持 | S-2.3（reviewer=implementer → 未完成） |
| M13 html 重生 | 本方案處理 | S-8.4 |
| M14 不可逆才 Quiz | 刻意維持 | S-1.4（Quiz 可併 Ship；不准第三例行停） |
| M15 token／檔仍在 | 本方案處理 | S-1.1；禁刪 token 是約束 |
| M16 F0 不改 graph／牙 | 本方案處理 | S-8.4、S-8.1；禁改 graph／既有牙是約束 |

## Owner Call hang

| OC | 掛到 |
|---|---|
| OC-1 dual-read 誠實三句 | S-5.4、S-5.5、S-5.7 |
| OC-2 2.0.0+五站 hops → 紅／不得改線 | S-5.5、S-5.6 |
| OC-3 不鎖 annex 鍵名／event schema | S-5.4、S-7.4 |
| OC-4 本 Decision hop 不改 STATUS／不發明 G1 PASS | S-8.4（本 hop 對稱：不改 STATUS、不發明 G2 PASS） |
| OC-5 in-flight 只認 1–7 `.md` | S-5.3 |
| OC-6 chat 不是判定 | S-3.1、S-4.2 |
| OC-7 本 Decision hop 連 scripts／annex 也不寫 | S-8.4、S-8.6 |
| OC-8 Q6 保持 Assumption；升格擋本 slug G2 | S-6.2、S-6.3 |
| OC-9 SC 用對照稿／拒絕／檔集 | 全 S 觀測欄 |
| OC-10 RP-1…16 只准加不准減 | S-2.6 |
| OC-11 後站把 Must-keep／四欄／seam 標可選 → 擋本 slug G2 | S-2.7 |

## ADDED Requirements

### R-1: 系統 SHALL 凍結七檔名並殺掉例行等人
SC-1／1A／表 A。五站 Intake／Decide／Spec／Build／Ship 是路線**別名**。檔名家族仍是 `1-discussion.md`…`7-review.md`。摺的是例行 G1／S3-`ACCEPTED`／G2 人類停，不是 token、不是 twin。謂詞假 = 停該站修。A4／A7 twin 仍產、latch=否。A10 唯一預設人停。Quiz 可併 Ship，不准第三例行停。不採 1B。

**審的時候看什麼**
目錄裡仍是七個舊檔名。新 slug 中間前進紀錄沒有「請人審 A4／A7／提交判定」。謂詞假的停修句寫該謂詞，不寫「先問 owner」。

#### S-1.1 五站別名對到七個凍結檔名
- GIVEN F3 之後一條新 slug 的 `docs/dev/<slug>/` 已有 `1-discussion.md`、`2-decision.md`、`4-spec.md`、`5-tasks.md`、`6-implementation-notes.md`、`7-review.md`；條件命中時另有 `3-prototype.md`
- WHEN coordinator 或寫手把該 slug 標成 Intake→Decide→Spec→Build→Ship
- THEN 五個站名只當別名；目錄內零個檔名為 `intake.md`／`decide.md`／`spec.md`／`build.md`／`ship.md`；G1／G2／`ACCEPTED` token 與檔仍在
- 觀測:從該 slug 目錄 `ls` 與 token 掃描看 | 七舊名在、新家族名不在、token 仍在算過 | n-a:F3 尚未切新 slug 預設（本 PR 不實作 F3）。替代：`rg -n "檔名家族不動|1-discussion.md" docs/dev/five-station-simplify/4-spec.md docs/dev/five-station-simplify/2-decision.md` 對到 1A；本 repo 現況七檔名仍是舊家族
- Operational Context:不適用 — 檔名對照，無新的現場交接。

#### S-1.2 中間 latch 未命中時前進紀錄沒有請人審 A4／A7
- GIVEN F3 後新 slug：Decide／Spec／Build 謂詞全真、B1 未命中、A10 尚未寫 `verdict:`
- WHEN coordinator 從 Intake 評到 Ship 前並留下前進紀錄
- THEN 該紀錄不含「請人審 A4」「請人審 A7」「請按提交判定」；A4／A7 twin 檔可已產
- 觀測:從該 slug 前進紀錄／hop log 看 | 中間無上列三句、twin 可存在算過 | n-a:F2 coordinator 尚未落地。替代：對照 `3-prototype.md` 盤 1 新 5 欄；本檔與 Decision SC-1 字面
- Operational Context:
  - Actor:coordinator（F2 後）／母版 owner
  - Goal:中間不等提交判定
  - Situation:新 slug、latch 未命中
  - Known information:表 A latch 欄；A4／A7 = 否
  - Missing information:現場會不會要求「順便問人」
  - Human decision:不在 A4／A7 簽；只在 Ship 簽
  - Authority:coordinator 禁問「要不要繼續」
  - External dependency:無
  - Out-of-system action:不准改問 owner 來繞假謂詞
  - Waiting/timeout behavior:中間不停；Ship 才 HumanWait
  - Recovery:若紀錄出現請人審 A4／A7，當 RP-14 紅，刪該問人紀錄後重評
  - Audit/handoff requirement:前進紀錄可核對
  - Observation:見本條觀測

#### S-1.3 謂詞假時停修理由是該謂詞不是改問人
- GIVEN 同一新 slug：`2-decision.md` 有一條 OC 狀態為未裁決，或某 S 含 C4 未定事項三詞
- WHEN coordinator 評 Decide→Spec 或 Spec→Build
- THEN 不停成 HumanWait；停修理由字面含該謂詞（未裁決 OC 或未定事項三詞）；理由不含「先問 owner 要不要繼續」
- 觀測:從停點理由字串看 | 含該謂詞、不含改問人句算過 | n-a:F2 未落地。替代：`3-prototype.md` 盤 1 末段；Decision SC-1 第二句
- Operational Context:
  - Actor:coordinator／寫手
  - Goal:假謂詞就修檔
  - Situation:OC 未裁決或 S 含未定事項三詞
  - Known information:哪一列謂詞假
  - Missing information:owner 會不會口頭放行
  - Human decision:修該列，不口頭繞
  - Authority:coordinator 禁改問人
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停在該站直到謂詞真
  - Recovery:補裁決或刪未定事項三詞後重評
  - Audit/handoff requirement:停修理由留在該站 md 或 hop 拒絕輸出
  - Observation:見本條觀測

#### S-1.4 A4／A7 仍產且不 latch；A10 機械綠仍等人
- GIVEN 新 slug 已有 `2-decision.md` 與 `4-spec.md`；稍後有 `7-review.md` 且 G3 物質檢查全綠；本改動不是不可逆（非 schema／公開 API／權限／金流／資料遺失）
- WHEN 產檔器跑 A4／A7／A10；coordinator 評 latch
- THEN A4／A7 html twin 存在且 latch=否；A10 存在且進入 HumanWait；本條不另開 Quiz 第三次例行停
- 觀測:從三個 html 是否存在與 hop 是否在 A10 停看 | twin 在、A4／A7 不等、A10 等、無第三停算過 | n-a:F2／F3 未落地。替代：`3-prototype.md` 盤 2 表 A4／A7／A10／B4 列
- Operational Context:
  - Actor:母版 owner
  - Goal:只在出貨停
  - Situation:機械項已綠
  - Known information:A10 latch=是
  - Missing information:人會不會把 twin 當成還要簽 G1／G2
  - Human decision:寫 Ship `verdict:`；不在 A4／A7 簽
  - Authority:只有人准寫 Ship `verdict:`
  - External dependency:無
  - Out-of-system action:人打開 A10 審頁
  - Waiting/timeout behavior:機械綠仍等頂欄
  - Recovery:誤在 A4／A7 等人 → RP-14 紅
  - Audit/handoff requirement:頂欄 `verdict:` 才是判定
  - Observation:見本條觀測

### R-2: 系統 SHALL 把假完成任務與短缺 Must-keep 點名成違 brief
SC-2／SC-3／SC-13／6A／RP-1…RP-4／OC-10／OC-11。少任一 M1–M16 = 違 brief，不能寫成簡化成功。T 四欄與 RED→獨立審查 seam 不可選。人見面時機 = **T 卡上就紅**（Stage 3 選定）。F1 牙最小集 = RP-1…RP-16，annex 只准加不准減。不採 6B。

**審的時候看什麼**
打開 T-fake：缺四欄、`Verify: 看起來沒問題`、無 RED、自審、勾選已打。卡上必須已紅，勾選不算完成。少 M 的「五站已簡化」宣稱被點名違 brief。

#### S-2.1 少任一 Must-keep 的簡化宣稱必須被點名違 brief
- GIVEN 一份規格或任務或牙輸出宣稱「五站已簡化」，且 M1–M16 少任一項（對照稿：拿掉 T 的 Verify 欄，即少 M11）
- WHEN 對照 `notes/design/five-station-simplify-brief-v3.md` §5 與本檔 Must-keep Disposition
- THEN 該宣稱被標成違 brief；不得出現「已經五站了所以可省」當省略理由
- 觀測:從那次輸出對 M 表的點名看 | 少項被點名、省略理由句不在算過 | 用 AC-2／Decision SC-2 對照稿；本檔 Disposition 列齊 16 條
- Operational Context:不適用 — 對照表點名，不是新交接。

#### S-2.2 缺四欄或 Verify 寫看起來沒問題的 T 在卡上就紅
- GIVEN `3-prototype.md` 盤 3 壞卡 T-fake：Covers／Files／Verify／Blocked-by 缺或 `Verify: 看起來沒問題`；checkbox `[x] done`；註「已經五站了，四欄／seam 可選」
- WHEN 寫手保存該 T 或 reviewer 打開 A8 任務板該卡
- THEN 該卡當下顯示 RP-1 紅；勾選不把該 T 標成完成
- 觀測:從該 T 卡／A8 當下狀態看 | 卡上紅、完成標未寫上算過 | n-a:F1 牙未掛 A8。替代：用盤 3 T-fake 原文當輸入；本檔與 Decision SC-3 字面要求「該 T 不得標完成」
- Operational Context:
  - Actor:獨立 T reviewer／Ship 審查者
  - Goal:假完成 T 當下看見紅
  - Situation:寫手勾了 done
  - Known information:四欄契約、T-ok 對照
  - Missing information:寫手是否打算 hop 再補
  - Human decision:退回補欄，不把勾選當完成
  - Authority:缺欄 checkbox 無效
  - External dependency:無
  - Out-of-system action:不要用 chat「看起來可以」勾完
  - Waiting/timeout behavior:無；紅在寫卡當下
  - Recovery:補齊四欄後紅熄
  - Audit/handoff requirement:卡上 RP-1
  - Observation:見本條觀測

#### S-2.3 無 RED 或 reviewer 等於 implementer 的 T 未完成
- GIVEN 同一 T-fake：無 RED 輸出；reviewer 欄 = 該 T 實作者
- WHEN 有人要把該 T 標完成
- THEN 系統標未完成（RP-2）；6-notes 無失敗測試原始輸出也算未完成（RP-6／M10）
- 觀測:從該 T 縫與 6-notes 證據欄看 | 無 RED 或自審 → 未完成算過 | n-a:F1 牙未掛 seam。替代：盤 3 T-fake；Decision RP-2／RP-6
- Operational Context:
  - Actor:獨立 T reviewer
  - Goal:自審與無紅燈輸出不得過
  - Situation:實作者想自己簽
  - Known information:author≠approver
  - Missing information:另一 session 是否已審
  - Human decision:換 reviewer；補 RED 輸出
  - Authority:reviewer 必須 ≠ implementer
  - External dependency:另一 session
  - Out-of-system action:開第二 session 審
  - Waiting/timeout behavior:縫不存在就停 Build
  - Recovery:換人重審並貼原始輸出
  - Audit/handoff requirement:6-notes 留 RED 輸出與 reviewer id
  - Observation:見本條觀測

#### S-2.4 含未定事項三詞或不可測的 S 必須紅
- GIVEN 壞卡 S-fuzzy：S 正文含 `scripts/check-spec-gate.sh` C4 `VAGUE_ALL` 三詞之一，或只寫「系統應處理錯誤」且無可斷言輸出
- WHEN 跑本 feat 掛進的 S 形狀牙（F1 接既有 `check-spec-gate.sh` C4，不另造家族）
- THEN exit ≠ 0（RP-3）；該 S 不得當 T 的 Covers 綠燈
- 觀測:從該檢查 exit 看 | 未定事項三詞或不可測必紅算過 | 正向：本檔各 S 有具體輸入與可斷言輸出。負向 fixture 目錄交 F1 annex，本 hop 不新增 `scripts/` 檔
- Operational Context:不適用 — 規格形狀牙。

#### S-2.5 測試名不含 S-id 必須紅
- GIVEN 一條測試函數名 `test_store_half_slot`（不含 `s_` 或 `S-` 與對應 S-id）
- WHEN 跑 F1 對測試名的牙（RP-4／M1）
- THEN 該測試被紅；對照名 `test_s_2_5_test_name_requires_s_id` 不因本條紅
- 觀測:從牙對測試名的輸出看 | 無名中 S-id → 紅、名含 S-id → 不因本條紅算過 | n-a:F1 牙未落地。替代：本檔 Test Skeletons 每個名字含 `s_` 與 S-id
- Operational Context:不適用 — 測試命名牙。

#### S-2.6 F1 牙能紅 RP-1 到 RP-16 且 annex 刪任一列就紅
- GIVEN F1 annex 列出 RP-1…RP-16；另造一份 annex 刪掉 RP-8（Ship 無人 PASS 卻 Done）
- WHEN 跑 F1 最小集對照（OC-10：只准加不准減）
- THEN 完整集能對 T-fake／S-fuzzy／Agent 代寫／超 cap／空 attestation／in-flight 寫五站狀態各紅至少一次；刪 RP-8 的 annex 被紅
- 觀測:從 annex 列與牙對 16 個對照的拒絕看 | 16 列都能紅、減列 annex 紅算過 | n-a:F1 未落地。替代：本檔與 `2-decision.md` 「本方案要求」表 16 列字面可被 `rg` 對到 RP-1…RP-16
- Operational Context:不適用 — annex 最小集。

#### S-2.7 本 slug 後站把四欄或 seam 或 Must-keep 標可選必須擋 G2
- GIVEN 本 slug 的 `4-spec.md` 或後續 `5-tasks.md` 出現「四欄可選」或「seam 可選」或「已五站故省 Must-keep」
- WHEN 人送本 slug G2（或 F1 對本 slug 後站文檔的對照）
- THEN 該送審不得過（OC-11）；本檔正文零處把 M1／M3／M11 或四欄／seam 標成可選
- 觀測:從本檔 `rg` 與 G2 拒絕看 | 本檔無「可選四欄／可選 seam／已五站故省」；若後站寫出 → 擋 G2 算過 | 對本檔跑 `rg -n "可選四欄|可選 seam|已五站故省" docs/dev/five-station-simplify/4-spec.md` 必須零命中
- Operational Context:
  - Actor:本 slug G2 reviewer
  - Goal:C 線掏空句進不了後站
  - Situation:有人想把 M11 寫成簡化細節
  - Known information:OC-11、6A
  - Missing information:後站會不會改口
  - Human decision:打回該句
  - Authority:擋本 slug G2
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:未刪該句不得離 G2
  - Recovery:刪可選句後重送
  - Audit/handoff requirement:OC-11 列
  - Observation:見本條觀測

### R-3: 系統 SHALL 把 Agent 代寫判定當成未寫
SC-4／RP-8／RP-16／5A。預設人類停點只有 Ship。Agent 或 coordinator 寫入 `ACCEPTED` 或 Ship `PASS`（無人類 attestation／無人類頂欄）= 未寫。不採 5B／5C。

**審的時候看什麼**
壞卡 Agent：頂欄被機器寫成 PASS。系統當沒寫，不得 Done、不得離 Spec。

#### S-3.1 Agent 寫入 ACCEPTED 或 Ship PASS 視為未寫
- GIVEN B1 命中的 `3-prototype.md` 由 Agent 寫入 `Human verdict: ACCEPTED` 且無 `Verdict attestation: human:` 行；或 `7-review.md` 頂欄 `verdict: PASS` 的寫入者是 Agent／coordinator
- WHEN 系統評「是否已寫判定」
- THEN 視為未寫（RP-16）；不得 hop 出 Spec；不得標 Done
- 觀測:從頂欄／attestation 與 hop 拒絕看 | 無人類 attestation 的 ACCEPTED 與無人類頂欄的 PASS 皆未寫算過 | n-a:F1 牙未改寫入路徑。替代：盤 4 壞卡 Agent；dogfood-ping `DOGFOOD-NOTES.md` L9 對照；本 hop **不**示範填 ACCEPTED
- Operational Context:
  - Actor:母版 owner
  - Goal:判定只由人寫
  - Situation:Agent 想代填
  - Known information:md 頂欄才是正本
  - Missing information:chat「Treat as PASS」會不會被抄進 md
  - Human decision:親寫 attestation 或頂欄；禁止叫 Agent 代填
  - Authority:Agent／coordinator 禁寫 ACCEPTED／Ship PASS
  - External dependency:Cursor chat（不是判定）
  - Out-of-system action:人類親做 Demo 或親寫 Ship
  - Waiting/timeout behavior:未寫則留在該 latch
  - Recovery:刪機器寫入，人重寫
  - Audit/handoff requirement:attestation 行或頂欄作者
  - Observation:見本條觀測

#### S-3.2 Ship 無人寫 PASS 卻標 Done 必須紅
- GIVEN `7-review.md` 頂欄 `verdict:` 空或 `HOLD` 或 `REQUEST_CHANGES`；機械項全綠
- WHEN 有人把該 slug 標 `Done` 或自動前進離開 Ship
- THEN 紅（RP-8）；狀態留 Ship／HumanWait
- 觀測:從 slug 狀態與牙輸出看 | 無人 PASS → 不得 Done 算過 | n-a:F2 狀態機未落地。替代：狀態機 §2.5／§6.1；Decision RP-8
- Operational Context:
  - Actor:Ship 審查者
  - Goal:出貨樹=人簽過的樹
  - Situation:機械全綠
  - Known information:A10 latch=是
  - Missing information:人是否讀完八點
  - Human decision:寫 PASS 或 HOLD 或 REQUEST_CHANGES
  - Authority:只有人
  - External dependency:無
  - Out-of-system action:人打開 7-review 審頁
  - Waiting/timeout behavior:綠了仍等
  - Recovery:HOLD 留 Ship；REQUEST_CHANGES 回上一站並吃 cap
  - Audit/handoff requirement:頂欄 `verdict:`
  - Observation:見本條觀測

### R-4: 系統 SHALL 拒空 attestation 且未命中不產 Demo
SC-6／Q11／5A／RP-12／RP-13／RP-14。九條 trigger 命中 → 進 Build 前必須人類 `ACCEPTED`+attestation。chat「可以／准開下一站」不是 attestation。未命中 → 不產 Demo、不第二次人停、n-a 有原因。否定「跳過 Stage 3」的句子不得被讀成 skip OC。

**審的時候看什麼**
壞卡 dogfood：欄空 + chat 准開。不得離 Spec。本 slug 自己的 Stage 3 已是人類 ACCEPTED + `human:rick @ 2026-09-14`。

#### S-4.1 B1 命中時進 Build 前已有人類 ACCEPTED 加 attestation
- GIVEN 九條 trigger 至少一條勾選（本 slug 命中 6 條）；`3-prototype.md` 在
- WHEN coordinator 評 Spec→Build
- THEN 僅當 Human verdict=`ACCEPTED` 且存在 `Verdict attestation: human:<名> @ <YYYY-MM-DD>` 才准 hop；`REVISE`／`NOT_REVIEWED`／無 attestation 的 ACCEPTED = 假
- 觀測:從 3-prototype 兩行與 hop 結果看 | 本 slug 現況兩行都在（#309／#310）故語意上 B1 已熄；缺一行則 hop 拒算過 | 讀 `docs/dev/five-station-simplify/3-prototype.md` 的 Human verdict 與 attestation 行
- Operational Context:
  - Actor:母版 owner
  - Goal:互動定案前親做 Demo
  - Situation:trigger 已命中
  - Known information:九條清單、attestation 格式
  - Missing information:人是否真的走過 Demo Script
  - Human decision:親填 ACCEPTED 或 REVISE
  - Authority:Agent 禁寫 attestation
  - External dependency:人實際點／比對卡
  - Out-of-system action:依 Demo Script 走 D1
  - Waiting/timeout behavior:B1 HumanWait
  - Recovery:REVISE → 改完重 Demo
  - Audit/handoff requirement:attestation 行
  - Observation:見本條觀測

#### S-4.2 欄空加 chat 准開不得離 Spec
- GIVEN Human verdict 空或 attestation 空；owner chat 字面「可以開 Stage 4」或「准開下一站」
- WHEN 有人要把該寫入當 attestation 或 hop 出 Spec
- THEN 拒絕（RP-13／OC-6）；chat 文字不寫入 Human verdict
- 觀測:從頂欄／attestation 是否仍空與 hop 拒絕看 | 空欄+chat 仍不得離 Spec 算過 | 對照 dogfood-ping `DOGFOOD-NOTES.md` L9；盤 4 壞卡 dogfood
- Operational Context:
  - Actor:母版 owner
  - Goal:chat 不能替代 attestation
  - Situation:dogfood 捷徑
  - Known information:判定正本=md 頂欄
  - Missing information:助手會不會把 chat 抄進 md
  - Human decision:親寫 attestation，或留在 Stage 3
  - Authority:chat 不是判定
  - External dependency:Cursor chat
  - Out-of-system action:人打字進 3-prototype，不是進 chat
  - Waiting/timeout behavior:空欄就卡 Spec
  - Recovery:人類補行後重評
  - Audit/handoff requirement:attestation 行
  - Observation:見本條觀測

#### S-4.3 未命中不產 Demo；若仍要求 ACCEPTED 則紅
- GIVEN 純守衛 feat：`3-prototype.md` 不存在，或九條全未勾且 n-a 原因非空
- WHEN coordinator 評 B1／A5；另有人要求該 feat 必須有 `ACCEPTED`
- THEN 不建 Demo html；不第二次人停；n-a 原因可讀。要求 `ACCEPTED` 的那次 → 紅（RP-12）
- 觀測:從 A5 是否建頁與 RP-12 拒絕看 | 無頁、有原因、強迫 ACCEPTED 紅算過 | n-a:本 slug 不是未命中樣本（已命中 6 條）。替代：盤 2 A5 好例「純後端 feat」
- Operational Context:不適用 — 未命中路徑無第二次交接。

#### S-4.4 latch 未命中卻留下請人審紀錄必須紅
- GIVEN A4 或 A7 latch=否；coordinator 仍寫下「請 owner 看一下」或「要不要繼續」
- WHEN F1／F2 評 RP-14
- THEN 該紀錄紅；不是客氣
- 觀測:從 hop／chat 紀錄是否含請人審句看 | 有句就紅算過 | n-a:F2 未落地。替代：盤 2 壞例 RP-14；brief §3 出口第 5 步
- Operational Context:
  - Actor:coordinator
  - Goal:沒命中就不問人
  - Situation:twin 已產
  - Known information:latch=否
  - Missing information:owner 是否自己打開 twin
  - Human decision:不彈審
  - Authority:禁開審查 widget
  - External dependency:無
  - Out-of-system action:不准把 A4 URL 當「請簽」
  - Waiting/timeout behavior:不問就不等
  - Recovery:刪請人審紀錄
  - Audit/handoff requirement:RP-14 輸出
  - Observation:見本條觀測

#### S-4.5 否定跳過句不得被讀成 skip Owner Call
- GIVEN `2-decision.md` 內部技術選擇含「不預先跳過 Stage 3」且同行有「本檔無『跳過 Stage 3』流程層 OC」
- WHEN 跑 `python3 hooks/_stage3_impl.py five-station-simplify`
- THEN 語意應 REJECT（trigger 已命中且當時 verdict 曾為 `NOT_REVIEWED` 時不得因該行當 skip）。2026-09-14 實跑 stdout 曾 `g2_demo=PASS`、`trigger_source=owner-call` —— 這是現行牙誤綠，F1 必須收緊：同時否定「不／無／不得」的「跳過」不得當 skip OC
- 觀測:從該指令 stdout 的 `trigger_source` 與 F1 收緊後的 exit 看 | 今日誤 PASS 記帳；F1 後否定句不得再當 skip 算過 | 原始輸出見 `3-prototype.md` 盤 4；本 hop 不改 `_stage3_impl.py`
- Operational Context:
  - Actor:G2 reviewer／F1 寫牙的人
  - Goal:「不准跳」不被讀成「已跳」
  - Situation:現行牙字面撞「Stage 3」+「跳過」
  - Known information:2026-09-14 stdout
  - Missing information:F1 謂詞怎寫（annex，OC-3）
  - Human decision:F1 收緊 skip；本 hop 不修牙
  - Authority:F0／Backlog B 禁本 hop 改既有牙
  - External dependency:無
  - Out-of-system action:在終端機重跑該指令
  - Waiting/timeout behavior:同步結束
  - Recovery:F1 改謂詞後重跑應 REJECT 該假 skip
  - Audit/handoff requirement:盤 4 原始輸出摘要
  - Observation:見本條觀測

### R-5: 系統 SHALL 凍結舊七並拒把 doctor 綠說成已切
SC-5／SC-8／SC-9／SC-10／2A／3A／4A／OC-1／OC-2／OC-5。F3 cut 當下已有 1–7 任一 `.md` → 整段舊 7。本 slug 是 live freeze 樣本。2.1.0 讀舊 7 缺新 5 欄不紅。doctor 綠只證明握手。不採 2B／4C。

**審的時候看什麼**
三格 AND 才准說「路線」：契約版本、hops 是否五站預設、目錄有沒有 1–7 md。單獨 `COMPATIBLE`／exit 0 不准當已切。

#### S-5.1 F3 cut 當下已有 md 的 slug 仍走舊 7
- GIVEN F3 cut 瞬間 `docs/dev/<slug>/` 已有 `1-discussion.md`…`7-review.md` 任一
- WHEN 有人要求該 slug 改走五站自動前進
- THEN 該 slug 仍有例行 G1／條件 S3／G2／G3；不得寫入五站狀態（RP-15）
- 觀測:從該目錄站檔與狀態欄看 | 舊 7 閘仍在、無五站狀態算過 | 對照本 repo 任一已有站檔的 slug；不是後造假目錄
- Operational Context:
  - Actor:in-flight slug 執行者
  - Goal:走完手上舊 7
  - Situation:F3 已切新 slug 預設
  - Known information:目錄已有 md
  - Missing information:cut 會不會誤折自己
  - Human decision:拒絕折線
  - Authority:coordinator 對舊 7 放手給既有 graph
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:仍例行等 G1／G2
  - Recovery:若被寫入五站狀態 → RP-15 紅並清回舊 7
  - Audit/handoff requirement:目錄 md 列表
  - Observation:見本條觀測

#### S-5.2 對本資料夾要求五站 hop 跳過 G1／G2 必須跳不過
- GIVEN `docs/dev/five-station-simplify/` 已有 `1-discussion.md`（與後續 2／3／本 4 檔）
- WHEN coordinator 或寫手對本 slug 下五站自動前進、跳過例行 G1／G2
- THEN 跳不過（SC-8）；本資料夾整段舊 7 直到自己的 Ship
- 觀測:從本目錄 `ls *.md` 與被拒的 hop 看 | `1-discussion.md` EXISTS；五站 hop 拒算過 | `ls docs/dev/five-station-simplify/*.md`；n-a:F2 未落地故今日無 coordinator hop。替代：Decision 4A／SC-8 字面
- Operational Context:
  - Actor:本 slug 執行者／coordinator
  - Goal:觀測不被自己污染
  - Situation:有人想拿本 slug 當新 5 白老鼠
  - Known information:4C 已拒
  - Missing information:無
  - Human decision:拒絕 4C
  - Authority:in-flight 不建立五站機
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:本 slug 自己的 G2／G3 仍等人
  - Recovery:刪五站狀態寫入
  - Audit/handoff requirement:目錄 md
  - Observation:見本條觀測

#### S-5.3 僅有 html 無 md 不算 in-flight
- GIVEN `docs/dev/<slug>/` 只有 `1-discussion.html`，零個 `1-discussion.md`…`7-review.md`
- WHEN 評 in-flight（OC-5）
- THEN 不凍結；F3 後該空 md 目錄可開五站機。本目錄因已有 md 而凍，不是因 html
- 觀測:從「是否存在 1–7 `.md`」布林看 | 僅 html → in_flight=false；有 md → true 算過 | 本目錄 html+md 同時存在 → 因 md 而凍
- Operational Context:不適用 — 偵測規則。

#### S-5.4 二點一讀舊七缺新五欄不紅
- GIVEN 契約已宣告 2.1.0 dual-read；一份舊 7 slug 的站檔缺新 5 欄位（欄位名交 F1 annex，本檔不鎖鍵名，OC-3）
- WHEN 2.1.0 讀檔器解析該舊檔
- THEN 缺新欄 = 合法缺省，該檢查不紅（SC-5 第 2 句／OC-1 第 2 句）
- 觀測:從該讀檔檢查 exit 看 | 缺新欄不紅算過 | n-a:2.1.0 annex 未寫。替代：Decision SC-9 第一句；本檔不選定欄位名
- Operational Context:不適用 — 讀檔缺省。

#### S-5.5 契約仍二點零加 hops 已五站加 doctor 綠不得說已切
- GIVEN 本 tree 現況：`devflow_contract_version=2.0.0`；`hooks/devflow-doctor.sh` 對 2.0.0 握手綠（2026-09-14 實跑 `COMPATIBLE`／exit 0）；marketplace 單一 `source: ./` 可換 hops；doctor 源碼不含 `hops`／`graph.yaml`／`marketplace`／`Intake`
- WHEN 有人把這三件事 AND 解釋成「採用端已切五站」
- THEN 該解釋紅（SC-9）；doctor 綠只能證明 `2.0.0 ∈ supported`
- 觀測:從 `bash hooks/devflow-doctor.sh` exit 與 `_doctor_impl.py` L193–L202 是否讀 hops 看 | 今日 exit 0；握手不讀 hops；文案把綠當成已切 → 紅算過 | 重跑 doctor；讀盤 5 證據表
- Operational Context:
  - Actor:採用專案 owner
  - Goal:拒絕被遠端改線還以為沒變
  - Situation:marketplace update 之後
  - Known information:doctor 只握手版本
  - Missing information:hops 是否已被換成五站預設
  - Human decision:核契約版本；未 2.1.0 留舊 7
  - Authority:未 upgrade 不得遠端改線
  - External dependency:`marketplace update`
  - Out-of-system action:人跑 doctor、讀 marketplace
  - Waiting/timeout behavior:無
  - Recovery:把「已切」文案改成「只握手」
  - Audit/handoff requirement:三格 AND
  - Observation:見本條觀測

#### S-5.6 把 doctor 綠寫成可以跟 hops 走必須紅
- GIVEN 文案或謂詞寫「doctor exit 0 所以可以跟 hops 走」或同等句
- WHEN F1 評 SC-10 對照
- THEN 該文案／謂詞紅
- 觀測:從 F1 牙對該句的拒絕看 | 句在 → 紅算過 | n-a:F1 未落地。替代：Decision SC-10 字面；本檔本條
- Operational Context:不適用 — 文案拒收。

#### S-5.7 未 upgrade 的採用端必須仍走舊 7
- GIVEN 採用端契約仍 2.0.0；方法包 hops 已被 marketplace 換成五站預設
- WHEN 採用端開新 slug 或繼續舊 slug
- THEN 路線必須仍是舊 7；F1 至少紅「契約仍 2.0.0 且 hops 已是五站預設」（OC-2）
- 觀測:從採用端實際 hop 與 F1 牙看 | 仍舊 7、2.0.0+五站 hops 紅算過 | n-a:F1 牙未掛。替代：OC-1 第 3 句；盤 5 反事實
- Operational Context:
  - Actor:採用專案 owner
  - Goal:不被遠端改線
  - Situation:plugin 已 update
  - Known information:未宣告 2.1.0
  - Missing information:何時 upgrade
  - Human decision:拒絕跟 hops；或正式 upgrade 到 dual-read
  - Authority:未 upgrade = 舊 7
  - External dependency:marketplace
  - Out-of-system action:人決定是否 upgrade
  - Waiting/timeout behavior:無
  - Recovery:釘契約 2.0.0 並把 hops 當未授權
  - Audit/handoff requirement:F1 拒絕輸出
  - Observation:見本條觀測

### R-6: 系統 SHALL 把每條 Must-keep 與 Owner Call 掛到 Scenario 並拒 Q6 升格
SC-7／SC-12／OC-8。高影響列必須有 `M… → R-x/S-y` 或 `Non-Goal:<reason>`。Q6「採用現場也 chat 蓋章」保持 Assumption 或仍待驗。寫成已核事實 → 本 slug G2 打回。

**審的時候看什麼**
Must-keep Disposition 16 列都有下落。Q6 列仍標 Assumption／仍待驗，沒有「已 Observed」。

#### S-6.1 本檔高影響列每條都有去向
- GIVEN Stage 1 Constraints／Must-keep／Journey 高影響列與 Stage 2 Real-world 去向表
- WHEN 人讀本 4-spec 的 Real-world Disposition 與 Must-keep Disposition
- THEN 每條高影響列去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗}；標本方案處理者下落含 `R-` 或 `S-` id
- 觀測:從本檔兩張表看 | C9 形狀過；無「Stage 1 寫過、後面消失」算過 | 跑 `bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md` 的 C9；目視 16 條 M 都有下落
- Operational Context:不適用 — 去向帳形狀。

#### S-6.2 Q6 句仍標 Assumption 或仍待驗
- GIVEN 本檔任何提到「採用現場也 chat 蓋章」的句子
- WHEN 人掃描本檔與 2-decision
- THEN 該句帶 Assumption 或「仍待驗」；Assumption refs 列 Q6 status 不是 resolved
- 觀測:從本檔 Assumption refs 與 Disposition Q6 列看 | status=open 或仍待驗算過 | 讀本檔 `## Assumption refs`
- Operational Context:不適用 — 標籤紀律。

#### S-6.3 把 Q6 寫成已核事實必須擋本 slug G2
- GIVEN 一份本 slug 4-spec 把 Q6 寫成 Observed 或「已核：採用現場都蓋章」
- WHEN 送本 slug G2
- THEN 打回（SC-12／OC-8）；本檔未這樣寫
- 觀測:從 G2 拒絕與本檔用詞看 | 升格句 → 打回；本檔無「已核事實」句算過 | `rg -n "採用現場" docs/dev/five-station-simplify/4-spec.md` 各命中行須含 Assumption 或仍待驗
- Operational Context:
  - Actor:本 slug G2 reviewer
  - Goal:不捏造採用逐字稿
  - Situation:沒有採用訪談
  - Known information:母版 dogfood 蓋章 = Observed；採用外推 = Assumption
  - Missing information:採用現場手勢
  - Human decision:保持 Assumption，或 F1 annex 前抽一案後改 status
  - Authority:升格擋 G2
  - External dependency:採用逐字稿（public 禁收公司路徑）
  - Out-of-system action:owner 抽案（期限見 Assumption refs）
  - Waiting/timeout behavior:未抽案就不得升格
  - Recovery:改回 Assumption／仍待驗
  - Audit/handoff requirement:refs 表
  - Observation:見本條觀測

### R-7: 系統 SHALL 讓 F2 計數器咬重寫上限
狀態機 §6.2–§6.4／RP-9…RP-11。數字已鎖：hop≤2／Decide≤1／Goal reopen≤1。用盡 → Escalated，不准暗改。舊 7 不套這三 cap。計數落點（event schema／哪支腳本／哪根欄）交 F2，本檔不鎖鍵名（OC-3／Q10）。

**審的時候看什麼**
第三次 hop 重寫、第二次 Decide 重開、離開 Intake 後第二次改 Goal —— 三次都紅。舊 7 slug 做同樣動作不吃這三 cap。

#### S-7.1 hop 重寫第三次仍繼續必須紅
- GIVEN 五站 slug；同一 hop_id 已重寫 2 次（第一次寫不算；第 2 次重寫已計）
- WHEN 第 3 次重寫仍被要求繼續
- THEN 紅（RP-9）；進入 Escalated；不得暗改計數歸零
- 觀測:從 F2 計數器與拒絕看 | 第 3 次 → 紅算過 | n-a:計數落點交 F2。替代：狀態機 §3 表 hop≤2；本檔本條。本 hop 不選定 event 欄名
- Operational Context:
  - Actor:coordinator／Escalated 接收者
  - Goal:重寫有上限
  - Situation:同一 hop 又被要求重寫
  - Known information:數字 ≤2
  - Missing information:計數存在哪（F2）
  - Human decision:修 brief 或停，不准 reset
  - Authority:不准暗改 cap
  - External dependency:無
  - Out-of-system action:人明示下一手
  - Waiting/timeout behavior:Escalated 等人
  - Recovery:人明示後才離 Escalated
  - Audit/handoff requirement:計數只增不減
  - Observation:見本條觀測

#### S-7.2 Decide 重開第二次仍繼續必須紅
- GIVEN 該 slug 已離開 Decide 一次，且已重開 Decide 1 次
- WHEN 第 2 次整站重開 Decide（含 Decision 翻案、OC 重裁）仍繼續
- THEN 紅（RP-10）。Decide 站內、尚未 hop 出去的小改不算一次
- 觀測:從 Decide cap 看 | 第 2 次重開 → 紅；站內小改不計算過 | n-a:落點交 F2。替代：狀態機 §3.2
- Operational Context:不適用 — 與 S-7.1 同一計數器家族；本條只換 Decide 桶。

#### S-7.3 離開 Intake 後 Goal 重開第二次仍繼續必須紅
- GIVEN 該 slug 已 hop 出 Intake；Goal／Success Criteria／問題陳述已重開改寫 1 次
- WHEN 第 2 次重開仍繼續
- THEN 紅（RP-11）。若此次 Goal 重開造成第二次 Decide，同時用盡 Decide cap → Escalated
- 觀測:從 Goal reopen 計數看 | 第 2 次 → 紅算過 | n-a:落點交 F2。替代：狀態機 §3.3
- Operational Context:不適用 — 與 S-7.1 同一家族；本條只換 Goal 桶。

#### S-7.4 計數落點交 F2 且舊七不套三 cap
- GIVEN 本檔與 F2 annex；另給一個 in-flight 舊 7 slug 做第 3 次站內重寫
- WHEN F2 選定 event schema／腳本名（本檔不鎖）
- THEN 五站 slug 的三次超限對照仍紅；該舊 7 slug **不**因本三 cap 紅（走既有 T 嘗試上限 4）
- 觀測:從「五站超限紅／舊 7 不套」對照看 | 兩行都成立算過 | n-a:F2 未選定落點。替代：OC-3／Q10；Decision「舊 7 不套這三 cap」
- Operational Context:不適用 — 範圍聲明。

### R-8: 系統 SHALL 分四刀交付並把本 slug 後站限在 F1
SC-11／7A／brief §7。本 Spec 定義 F1／F2／F3 必須滿足什麼。本 PR 不實作。本 slug Stage 5–7 只准 F1 annex+teeth。1B／2B／4C／6B／7C 不得被 Stage 5 重開。

**審的時候看什麼**
本 PR `git diff --name-only origin/main` 只有本目錄 4-spec 雙檔。後站 Files 聯集若出現 coordinator 或切預設路線或改 `_templates/`，超出本 R。

#### S-8.1 F1 必須交付 teeth 加 dual-read annex 且不准切預設路線
- GIVEN F1 刀的交付清單
- WHEN F1 結束（另一次 PR／T，不在本 PR）
- THEN 產出含：能紅 RP-1…RP-16 的牙（`scripts/`／annex）+ 2.1.0 dual-read 讀法（舊檔缺新欄不紅；2.0.0+五站 hops 紅）。不准改新 slug 預設路線、不准寫 coordinator、不准刪 G1／G2／`ACCEPTED`
- 觀測:從 F1 diff 與牙輸出看 | 有 annex／scripts 牙；無 graph 預設切線；無 coordinator 碼算過 | n-a:本 PR 不實作 F1。替代：brief §7 F1 列；本檔本條。本 hop `git diff --name-only` 不得出現 `scripts/` 新牙
- Operational Context:不適用 — 刀範圍。

#### S-8.2 F2 必須交付 coordinator 加 event 且不准折 in-flight
- GIVEN F1 已過；F2 刀開始
- WHEN F2 結束
- THEN 產出含：coordinator 評表 A／B 自動前進；event 留前進／latch／cap。不准把 in-flight 折五站、不准刪 token、不准放寬三 cap 數字
- 觀測:從 F2 diff 與狀態機行為看 | 有前進／latch／cap 紀錄；舊 7 slug 不被寫入五站狀態算過 | n-a:F2 不在本 slug Stage 5–7。替代：brief §7 F2 列；本檔 Out of Scope
- Operational Context:不適用 — 刀範圍。

#### S-8.3 F3 必須讓新 slug 預設五站且不准改已 freeze 的 slug
- GIVEN F2 已過；F3 cut
- WHEN 新開一條 slug；同時讀本 slug 目錄
- THEN 新 slug 預設 Intake→Decide→Spec→Build→Ship（中間例行不等）。本 slug 與 cut 當下已有 md 的 slug 仍舊 7。G1／G2／`ACCEPTED` 仍在 repo
- 觀測:從 F3 後新舊 slug 路線看 | 新五舊七、token 仍在算過 | n-a:F3 不在本 slug Stage 5–7。替代：brief §7 F3 列；S-5.1／S-5.2
- Operational Context:不適用 — 刀範圍。

#### S-8.4 本 Stage 4 PR 只含四規格雙檔
- GIVEN 本 branch 相對 `origin/main`
- WHEN 跑 `git diff --name-only origin/main`
- THEN 輸出只含 `docs/dev/five-station-simplify/4-spec.md` 與 `docs/dev/five-station-simplify/4-spec.html`。零 `_templates/`、零 `graph.yaml`、零 `scripts/` 新牙、零 `STATUS.md`、零 `HISTORY.md`、零 `devflow-contract.json`。本檔 `verdict` 空；`status: draft`
- 觀測:從該指令 stdout 與本檔 frontmatter 看 | 兩檔、頂欄 draft／verdict 空算過 | 在本 branch 跑 `git diff --name-only origin/main`
- Operational Context:不適用 — 本 PR 檔集。

#### S-8.5 本 slug Stage 5 到 7 只准落地 F1
- GIVEN 本 slug G2 已過，進入 5-tasks
- WHEN 列 Files 聯集
- THEN 只准 `scripts/` 新牙、本 slug annex、本目錄 5／6／7 過程檔。不准 coordinator 碼、不准改預設 `graph.yaml` 路線、不准改 Stage 1–4 `_templates/`、不准把本 slug 折成五站
- 觀測:從後續 5-tasks Files 聯集看 | 超出上列 → L2／違本 R 算過 | n-a:5-tasks 尚未寫。替代：本檔 Out of Scope 與本條 THEN
- Operational Context:
  - Actor:本 slug Stage 5 寫手
  - Goal:只施工 F1
  - Situation:G2 剛過
  - Known information:7A 四刀不併
  - Missing information:有沒有人想順便寫 coordinator
  - Human decision:另開 slug／另刀做 F2
  - Authority:本 R
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:把 F2／F3 檔從 Files 刪掉
  - Audit/handoff requirement:5-tasks Files
  - Observation:見本條觀測

#### S-8.6 已拒方案不得被 Stage 5 重開
- GIVEN Decision Rejected Alternatives 列 1B、2B、4C、6B、7C（及 1C／2C／3B／3C／4B／5B／5C／6C／7B）
- WHEN Stage 5 寫 T 或 Stage 6 做選擇
- THEN 不得把上列方案當成可選實作。1B=刪 token；2B=舊檔缺欄就紅；4C=本 slug 當新 5 白老鼠；6B=M 可選；7C=併刀 F1+F2+F3
- 觀測:從 5-tasks／6-notes 是否出現「改採 1B／2B／4C／6B／7C」看 | 出現 → 違本 Spec，回 G2 不算；本檔 Non-Goals 含這五個代號算過 | 讀本檔 Out of Scope
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:不重開已拒案
  - Situation:實作時覺得刪 token 比較好寫
  - Known information:Rejected 表
  - Missing information:無
  - Human decision:停，回第 2 站才准翻案
  - Authority:推翻 Decision 不是合法 DD
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:刪該 T
  - Audit/handoff requirement:Non-Goals
  - Observation:見本條觀測

## MODIFIED Requirements

本 slug Stage 5–7 **不改** living 契約句。現行正本仍是七份文檔 + 例行 G1／G2／G3：

原條文（`docs/dev/readme-contract-extract.md` L7–L17）：七份檔各一 Gate；G1／G2／G3 物質句仍在。

改什麼（**F3 才改預設路線**；本檔用 ADDED 定義必須滿足的新行為）：新 slug 預設五站別名；檔名與 token 不動；例行人類停只留 Ship。本 hop 與本 slug Stage 5–7 不改正文。

無本 hop 要落地的 MODIFIED 條文。

## REMOVED Requirements

無。不刪 G1／G2／`ACCEPTED` 檔或 token。不刪 Fast。不刪七檔名。不刪第二條 ID 鏈禁令。

## 行為流程圖(R 級)

```
[R-1] 凍結七檔名並殺掉例行等人
  五站是別名
  謂詞假停修
  A4 A7 產而不 latch
[R-2] 把假完成任務與短缺 Must-keep 點名成違 brief
  T 卡上就紅
  RP 只准加
[R-3] 把 Agent 代寫判定當成未寫
  Ship 唯人
[R-4] 拒空 attestation 且未命中不產 Demo
  chat 不是判定
[R-5] 凍結舊七並拒把 doctor 綠說成已切
  本 slug 跳不過
[R-6] 把每條 Must-keep 與 Owner Call 掛到 Scenario 並拒 Q6 升格
  去向必有 R/S
[R-7] 讓 F2 計數器咬重寫上限
  hop Decide Goal 數字已鎖
  計數落點交 F2
[R-8] 分四刀交付並把本 slug 後站限在 F1
  本 PR 只 4-spec
  1B 2B 4C 6B 7C 不重開
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.6）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、本目錄 freeze md、doctor 握手、Disposition／Non-Goals／Assumption 用詞。F1／F2／F3 行為 S 的綠發生在各刀落地之後，不在本 PR。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-simplify/4-spec.md` 後審頁可解析 R/S。不回歸改既有牙（本 hop 禁改 `scripts/`）。
- 非功能：本 slug 自己仍走舊 7（SC-8）。dual-read 未 bump（F0／本 hop 不 bump）。
- 無 golden master（可見路線行為在 F3 才變；本 hop 不改 runtime）。

### Stage 3 對帳

`3-prototype.md` `status: approved`；`Human verdict: ACCEPTED | role=母版 owner | scenario=AC-1`；`Verdict attestation: human:rick @ 2026-09-14`（#309／#310）。Demo 前置已滿足。本 hop **不**發明 G2 PASS。

- Scenario AC-1（新 slug 中間不停）→ S-1.2、S-1.3
- Scenario AC-6（表 A／B）→ S-1.4、S-4.3、S-4.4
- Scenario AC-3（假完成 T；T 卡上就紅）→ S-2.1、S-2.2、S-2.3、S-2.4
- Scenario AC-4（空 attestation + Agent 代寫）→ S-3.1、S-4.2
- Scenario AC-8（本 slug 仍舊 7）→ S-5.2
- Scenario AC-5（舊檔不紅＋F3 cut 仍舊 7）→ S-5.1、S-5.4
- Scenario SC-9（doctor 綠 ≠ 已切）→ S-5.5、S-5.6、S-5.7
- Scenario RP-14（否定跳過被當成已跳）→ S-4.5
- Method 盤 1…5 → 上列 S
- Method 選定人見面「T 卡上就紅」→ S-2.2
- Operational Context Recovery（停修、補欄、換 reviewer、刪機器判定、補 attestation、拒遠端改線、Escalated）→ 各對應 S 的 Recovery
- D1 無第二互動 Variant；1A–7A 不重開 → Out of Scope／S-8.6

## Out of Scope

本 slug Stage 5–7（G2 之後的立即 Build）**不做**：

- F2 coordinator／event schema 落地（本檔 R-7／S-8.2 只定義必須滿足什麼）
- F3 cut／改新 slug 預設 `graph.yaml` 路線（S-8.3）
- 本 Stage 4 PR 寫 F1 牙或 annex 檔（S-8.4；F1 只准 G2 **之後**）
- 改 `_templates/`、各站 `graph.yaml`、既有牙、`devflow-contract.json` bump
- 改 `STATUS.md`／`HISTORY.md`；發明 G2 PASS；合併本 PR 當已過 G2
- 拿本 slug 當新 5 白老鼠（4C）
- 刪 G1／G2／`ACCEPTED`（1B）
- 舊檔缺新欄就紅（2B）
- 把 Must-keep 或四欄／seam 標可選（6B）
- 併刀 F1+F2+F3（7C）
- 1C 只加厚散文；2C／3C 用 marketplace 或「版本與 hops 同步」假裝已切；3B 本刀改 doctor；4B F3 折 in-flight；5B chat 繞 attestation；5C 取消 attestation；6C F1 改 1–4 模板；7B 本 PR 寫 F1 牙
- 重開 F0 十條；改七份文檔檔名；廢 Fast；第二條 Journey／Actor／M ID 鏈
- 選定 dual-read 欄位名或 coordinator event 鍵名（OC-3）
- 把 Q6 升成已核事實
- 建採用現場回報口；收公司路徑進 public repo

## Diff Budget

本節是**估計**。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `4-spec.md` | 1 | ≤900 | 0 |
| `4-spec.html`（產檔器） | 1 | ≤800（生成） | 0 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約 | 0 | 0 | 0 |

**G2 之後、本 slug Stage 5–7（只 F1）**［Assumption：牙形未鎖］

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| annex（dual-read 欄位／RP 表） | ≤2 | ≤200 | ≤40 |
| `scripts/` 新牙（接 check-spec-gate／新對照，不改 Stage 1–4 模板） | ≤4 | ≤250 | ≤400 |
| 本目錄 5-tasks／6-notes／7-review | ≤3 | ≤400 | 0 |
| F2 coordinator／F3 graph 切線 | 0（Out of Scope） | 0 | 0 |

測試與非測試分開估。F1 若用突變補牙，測試行可能到天真估法的 3 倍 —— 超支就停、判 L1/L2。

## Dependencies

- 已核 Decision／Stage 3 Human ACCEPTED（#300／#303／#306／#309／#310）。無新外部系統。
- F1 依賴本檔 G2 人類 PASS 之後才准動 `scripts/`／annex。
- F2 依賴 F1 annex（含 cap 數字；落點 F2）。
- F3 依賴 F2 coordinator 可評表 A／B。
- 不新增套件、不新增網路 capability。未經本節授權的新 capability 屬 7-review finding。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（文檔家族 × scripts／annex × 未來 coordinator × 採用端 hops）②契約 minor 2.1.0 讀檔（F1 annex）⑧F1 新檢查能力（scripts）⑨Feature Risk = high ⑪五站狀態機與 latch／cap 恢復
- Design source: `notes/design/five-station-simplify-brief-v3.md`；`notes/design/five-station-simplify-f0-state-machine.md`；2-decision 1A–7A

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| 本檔 4-spec（契約） | 定義五站／RP／cap／分刀 | 本 slug md | 讀 1／2／3 過程檔 | 改 living 契約句（F3 才動） |
| F1 scripts／annex | 咬 RP 與 dual-read 誠實 | 母版 scripts | 讀契約版本、hops 是否五站預設、站檔形狀 | 改 `_templates/` 1–4；改既有 doctor 握手語義當本 Decision hop |
| F2 coordinator | 評表 A／B、cap、latch | slug 狀態（F2 定 schema） | 讀 brief §3、本檔 R-1／R-4／R-7 | 折 in-flight；代寫判定 |
| 既有 graph／token | 服務舊 7 + dual-read | 方法包 graph | 被 F3 改**新 slug 預設** | F0–本 slug Stage 5–7 改 graph；刪 token |
| 採用端 | 未 2.1.0 走舊 7 | 採用專案契約檔 | marketplace 換包 | 遠端在 2.0.0 改線 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| dual-read 2.1.0 | 舊 7 檔或缺新 5 欄 → 合法缺省 | 2.0.0+五站 hops → 紅 | 讀檔不寫入採用端路線 | 舊 slug 不一次變紅 |
| Ship `verdict:` | 人寫 PASS／REQUEST_CHANGES／HOLD | Agent 寫入 = 未寫 | 頂欄與 checkbox 不是同一筆；只成功勾選不算判定 | 舊 7 in-flight 仍等人 |
| B1 attestation | `human:<名> @ <日>` | 空 + chat = 拒 hop | 與 Human verdict 兩行都要在才算寫入 | 五站後保持 |
| rewrite cap | hop_id／Decide／Goal 三次計數 | 超限 → Escalated | 三桶同時算；只增不減 | 舊 7 不套 |

兩筆寫入只成功一筆：頂欄 PASS 寫入但 attestation 空 → 仍未寫（S-3.1／S-4.1）。cap 計數寫入但狀態已 hop → Escalated 優先，不得當已過。

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 本 4-spec | 可測契約 | Decision、Stage 3 | 只文件 | DD 待人審 | spec-gate C1–C9 |
| F1 牙（後站） | 紅 RP 對照 | annex、既有 check-spec-gate | fixture → exit | 減 RP 列 → 紅 | 對照稿路徑交 annex |
| F2 計數器（另刀） | 三 cap | event（未鎖） | slug 級只增 | 超限 Escalated | 偽碼在狀態機 §3 |
| Freeze 偵測 | md 在否 | 目錄 | in_flight bool | 裸 html 不凍 | `ls *.md` |

### Design Constraints

- 必須:五站是別名；Ship 唯人；RP-1…16 只准加；本 slug 舊 7；本 slug Stage 5–7 只 F1
- 禁止:1B／2B／4C／6B／7C；本 hop 改模板／graph／STATUS；Agent 代寫判定；doctor 綠冒充已切
- Extension point:F1 annex 加謂詞；F2 選定計數落點
- Known design limit:Q6 無採用逐字稿；A1／A2 dest 未核；annex 鍵名未鎖；現行 `_stage3_impl.py` 會把否定跳過句讀成 skip（S-4.5，F1 才收緊）；本 hop 不修該牙

## Verification Profile(G2 一併審)

- lane: full（判準:新能力、改公開方法論路線、採用端遠端改線、不可逆 F3 切預設。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:公開契約 2.1.0、不可逆預設路線、權限／判定主權、採用端資料面「被改線」。模板「公開 API／不可逆／高風險人機互動」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得刪 G1／G2／`ACCEPTED`（S-1.1、1B）
  - 不得把假完成 T 當簡化成功（S-2.1、S-2.2）
  - 不得把四欄／seam／Must-keep 標可選（S-2.7）
  - 不得讓 Agent 代寫判定算已寫（S-3.1）
  - 不得讓空 attestation + chat 離 Spec（S-4.2）
  - 不得把本 slug 折成五站（S-5.2、4C）
  - 不得把 doctor 綠說成已切五站（S-5.5、S-5.6）
  - 不得把 Q6 升成已核事實（S-6.3）
  - 不得暗改 cap 或套到舊 7（S-7.1、S-7.4）
  - 不得在本 slug Stage 5–7 做 F2／F3（S-8.5）
  - 不得重開 1B／2B／4C／6B／7C（S-8.6）
  - 不得本 hop 改 STATUS／模板／graph／scripts 牙／契約 bump
- Required layers:check-spec-gate（本 hop 形狀）。文件層：本 PR 檔集（S-8.4）、Disposition C9、Assumption 用詞（S-6.2）
- Conditional layers:F1 落地 → 該刀牙列入 Required 並重跑對照稿；改 doctor 文案 → 重跑 `hooks/devflow-doctor.sh` + S-5.5 對照
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Race／stress（無多 writer runtime）、Windows 真機、本 hop 跑 coordinator（F2 Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md && python3 scripts/build-stage4-html.py --action docs/dev/five-station-simplify/4-spec.md`
- Reliability triage:
  - Concurrency: n-a — 一 slug 一機；本 hop 無多 writer 鎖契約；F2 才有 coordinator
  - Idempotency: applicable — 同一對照再評 freeze／doctor 綠≠已切／本 PR 檔集，結果相同（S-5.2、S-5.5、S-8.4）
  - Timeout/retry: n-a — 機械檢查同步結束；HumanWait 是 latch 不是重試（S-1.4、S-3.2）

### Failure Model(Risk: high 必填)

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 摺站後假完成 T | 勾選綠、工作沒做完 | T-fake 卡上不紅 | Required:S-2.2、S-2.3 | F1 牙落地前只文件對照 |
| 少 Must-keep 當簡化成功 | 完整度被掏空 | 「已五站故省」未被點名 | Required:S-2.1、S-2.7 | — |
| annex 減 RP | Ship／cap／attestation 牙消失 | 刪 RP-8 仍綠 | Required:S-2.6 | F1 後才跑 |
| Agent 代寫判定 | 出貨是機器的 | 無 attestation 的 ACCEPTED 仍 hop | Required:S-3.1、S-3.2 | — |
| chat 帶走空欄 | Demo 沒做就進 Build | 欄空 +「可以開 Stage 4」過 Spec | Required:S-4.2 | — |
| 否定跳過當 skip | 沒 Demo 卻 g2_demo=PASS | `_stage3_impl.py` trigger_source=owner-call | Conditional:S-4.5 | 本 hop 不修該牙（Known limit） |
| 本 slug 當新 5 | F0–F2 觀測被污染 | 五站狀態寫入本目錄 | Required:S-5.2 | — |
| doctor 綠冒充已切 | 採用端被遠端改線 | 文案寫「COMPATIBLE = 五站」 | Required:S-5.5、S-5.6 | — |
| Q6 升格 | 假 Observed 替殺等待背書 | 「採用現場都蓋章」無 Assumption | Required:S-6.3 | 採用逐字稿禁收 |
| cap 暗改或套舊 7 | 重寫無限或誤殺 in-flight | 第 3 次 hop 仍過；舊 7 被 cap 紅 | Required:S-7.1、S-7.4 | 落點 F2 |
| 併刀或後站做 F2／F3 | in-flight 與採用端同時爆 | 5-tasks Files 含 coordinator／graph 切線 | Required:S-8.5、S-8.6 | — |
| 本 hop 改 STATUS／模板 | 並行 session 互蓋；污染觀測 | diff 出現 STATUS 或 `_templates/` | Required:S-8.4 | — |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q6 採用現場仍 chat 蓋章 | 2026-10-31 | open |
| A1／A2 共寫 1-discussion.html | 2026-10-31 | open |
| 後站會用已經五站了省略 Must-keep | stage-2 | resolved |

Q6 期限 = F1 annex 前抽一案。升格成已核事實仍擋本 slug G2（S-6.3），與 status=open 並行：open 不是「已核」。第三列 Stage 2 已用 6A／OC-11 收束，故 resolved。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–7A。推翻 Decision 不是合法 DD。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | SC-1…SC-13 收成 R-1…R-8；每條 SC 至少一條 S（對照見確認紀錄） | C 線 anti-hollow；單份避免 >40 S 切片 | 本 hop brief；`2-decision.md` Success Criteria | 拆 slug 或漏 SC | 待人審 |
| DD-2 | 本 slug Stage 5–7 只落地 F1 annex+teeth；F2／F3 本檔定義但不施工 | 7A 四刀不併；Diff Budget 本 hop 只文件 | `2-decision.md` 7A／OC-7 | 後站寫 coordinator = 違 S-8.5 | 待人審 |
| DD-3 | rewrite 三 cap 數字鎖在 S-7.1…S-7.3；計數落點交 F2，不鎖鍵名 | OC-3／Q10 | `2-decision.md` OC-3；狀態機 §3 | 本檔鎖 event 欄名 = 偷做 F2 | 待人審 |
| DD-4 | Q6 Assumption refs = open／2026-10-31；升格句另由 S-6.3 擋 G2 | C7 不得用已過站 deadline 擋形狀；SC-12 仍咬語意升格 | `2-decision.md` OC-8／SC-12 | 改 resolved = 假裝已抽採用案 | 待人審 |
| DD-5 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 PASS | 公開路線＋判定主權＋採用端改線；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief | 改 normal 則 Failure Model 變選配；代填 PASS = 假綠 | 待人審 |
| DD-6 | 假完成紅的觀測落點 = T 卡上就紅（Stage 3 選定），不是 hop 板或 Ship 重建 | 對齊 SC-3「該 T 不得標完成」 | `3-prototype.md` 盤 3 | 改 hop 才紅 = 已棄 Variant B | 待人審 |
| DD-7 | 行為圖 8 框對 8 個 R；審頁產器硬切 8 框 | 產器 `steps[:8]`；不改 scripts | `scripts/build-stage4-html.py` L450 | 增 R-9 則圖丟框 | 待人審 |
| DD-8 | Non-Goals 點名 1B／2B／4C／6B／7C（及同表其餘已拒案），Stage 5 不得重開 | C 線：後站不能把已拒案當可選 | `2-decision.md` Rejected Alternatives | 刪這五個代號 = Stage 5 可重開 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `STATUS.md`、不 bump plugin、不開 5-tasks。
- 未讀 A／B 線 Stage 4。
- 負向 fixture 目錄建議 `scripts/fixtures/five-station-simplify/`（F1 才新增檔）。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- skip-OC 誤匹配記 S-4.5，本 hop 不改 `_stage3_impl.py`。

## Test Skeletons(選配)

- `test_s_1_1_aliases_keep_seven_filenames`
- `test_s_1_2_no_please_review_a4_a7`
- `test_s_1_3_false_predicate_stops_without_asking`
- `test_s_1_4_a4_a7_produce_no_latch_a10_waits`
- `test_s_2_1_missing_must_keep_is_brief_violation`
- `test_s_2_2_t_fake_red_on_card`
- `test_s_2_3_no_red_or_self_review_incomplete`
- `test_s_2_4_vague_or_untestable_s_fails`
- `test_s_2_5_test_name_requires_s_id`
- `test_s_2_6_rp_min_set_add_only`
- `test_s_2_7_optional_fields_block_this_g2`
- `test_s_3_1_agent_written_verdict_unread`
- `test_s_3_2_ship_done_without_human_pass_fails`
- `test_s_4_1_b1_requires_human_accepted_attestation`
- `test_s_4_2_empty_attestation_plus_chat_cannot_leave_spec`
- `test_s_4_3_miss_skips_demo_forced_accepted_fails`
- `test_s_4_4_ask_human_when_latch_false_fails`
- `test_s_4_5_negated_skip_is_not_skip_oc`
- `test_s_5_1_inflight_md_stays_old_7`
- `test_s_5_2_this_slug_five_station_hop_blocked`
- `test_s_5_3_html_only_not_inflight`
- `test_s_5_4_old_seven_missing_new_fields_not_red`
- `test_s_5_5_doctor_green_is_not_cut`
- `test_s_5_6_doctor_green_follow_hops_text_fails`
- `test_s_5_7_unupgraded_adopter_stays_old_7`
- `test_s_6_1_high_impact_rows_have_disposition`
- `test_s_6_2_q6_stays_assumption`
- `test_s_6_3_q6_as_fact_blocks_g2`
- `test_s_7_1_third_hop_rewrite_fails`
- `test_s_7_2_second_decide_reopen_fails`
- `test_s_7_3_second_goal_reopen_fails`
- `test_s_7_4_counting_locus_is_f2_old_7_exempt`
- `test_s_8_1_f1_teeth_and_annex_only`
- `test_s_8_2_f2_coordinator_no_inflight_fold`
- `test_s_8_3_f3_new_slug_five_station_freeze_untouched`
- `test_s_8_4_this_pr_docs_only`
- `test_s_8_5_this_slug_stage_5_to_7_is_f1_only`
- `test_s_8_6_rejected_1b_2b_4c_6b_7c_cannot_reopen`

## 確認紀錄

- 接手盤點 | 2026-09-14 | G1 PASS（2-decision approved／verdict PASS／OC-1…11 ✅）。Stage 3 approved + Human ACCEPTED + attestation `human:rick @ 2026-09-14`（#309／#310）。無「Stage 3」+「跳過」流程層 OC。living `docs/specs/` 0 條。驗收雛形 AC-1…AC-8 + Decision SC-1…SC-13。
- 雙源清點 | 2026-09-14 | 雛形 8 條 + SC 13 條 → ADDED R-1…R-8。living 契約句 L7–L17 列 MODIFIED 說明（本 slug Stage 5–7 不改正文）。REMOVED 無。
- R 範圍 | 2026-09-14 | Implementer C brief：每個 SC 至少一 S；F0→F3 分刀；別名 vs 七檔名；Ship 唯人；Agent 判定=未寫；cap 給 F2；M／OC 掛 S；本 hop 只文件。使用者本指令 = 範圍確認。
- S 展開 | 2026-09-14 | R-1…R-8 全展開；每 S 有觀測欄；交接／核准／等待／權限 S 有 Operational Context。
- SC 鏈 | 2026-09-14 | SC-1→S-1.2／S-1.3／S-1.4；SC-2→S-2.1；SC-3→S-2.2…S-2.5；SC-4→S-3.1／S-3.2；SC-5→S-5.1／S-5.4；SC-6→S-4.1…S-4.3；SC-7→S-6.1；SC-8→S-5.2；SC-9→S-5.5；SC-10→S-5.6／S-5.7；SC-11→S-8.4／S-8.5；SC-12→S-6.2／S-6.3；SC-13→S-2.6／S-2.7。
- 3a 四節 | 2026-09-14 | AC／Out of Scope／Diff Budget／Dependencies 齊。
- 3b Profile | 2026-09-14 | lane full、Risk high、Failure Model、Reliability triage、DBC applicable。
- 3c Stage 3 | 2026-09-14 | AC-1／AC-3／AC-4／AC-5／AC-6／AC-8／SC-9／RP-14 + Method／Recovery 逐場有下落。
- DD 掃描 | 2026-09-14 | 上層八條待人審；無「待裁決」殘留；不翻已核 Decision。
- 機械關卡 | 2026-09-14 | `scripts/check-spec-gate.sh` 9/9。審頁 `scripts/build-stage4-html.py --action` → 8 R／38 S、status=draft、verdict=PRE-REVIEW。
