---
feature: <slug>
stage: 4-spec
status: draft
verdict:             # 空 | PASS | REQUEST_CHANGES | HOLD(Human 判定;全勾不算 PASS)
owner:
reviewers: []        # G2 審查者,不可 = owner
updated:
parent:               # 選填,僅切片情境填:上游 1-discussion/2-decision 所在資料夾,如 docs/dev/<slug>/
---

# 4. 規格 — change spec(delta)

> 用途:本次變更的**可測契約**。SDD 真相來源;6 的測試從 S-id 長出來;7 逐條驗。
> 格式:openspec delta。Scenario 寫到「可直接變成一個測試」的精度。
> 通用慣例/架構不變量住 `.claude/rules/`,spec 只寫本次 delta,不重抄 rules。
> ship 後由 7-Exit 把 delta 併入 docs/specs/<domain>.md,此檔隨 feature 封存。
> 本階段固定產出:`4-spec.md`(本模板全節)+ `4-spec.html`(G2 必產;必含 R 級
> 行為流程圖、Drafting Decisions 待裁決置頂)。
>
> ## G2 twin 是**審查介面**,不是文件視覺版(README §6)
>
> 2026-08-15 補。起因:owner 打開一份合規的 `4-spec.html`(md 直轉、16 個 S 攤平在
> 單欄長文),第一句話是「這份給人看得有點雜亂」——**規範管的是「必含什麼元素」,
> 不管「長什麼形狀」**,所以完全照規則做仍然難審。三件事缺一不可,
> **產 html 時逐項對照,缺一項就是沒做完**:
>
> | | 要求 | 這一站的內容 |
> |---|---|---|
> | 1 | **動線頂區五格**,每格一句話 + 可點跳轉,審完五格才決定要不要往下讀 | 狀態(frontmatter)/ 待審 S(幾條 + **幾條缺觀測欄**)/ lane · Risk / DD 進度 `x/y` / Demo verdict |
> | 2 | **待審項目逐條可勾**,有進度計數,缺必填欄的直接在卡上現形 | **每個 S 一張卡**(GIVEN/WHEN/THEN 對齊、「觀測」欄獨立標色);**缺 GIVEN/WHEN/THEN/觀測任一欄即紅底**(動線頂區優先報缺觀測條數)——觀測是 G3 驗收的唯一依據 |
> | 3 | **背景資料摺疊**(`<details>`,預設收合、內容零刪減) | Bug Scenario、Acceptance Criteria、Out of Scope、Diff Budget、Verification Profile、DD 表、Test Skeletons、Known limits |
>
> 產生方式:`docs/dev/tools/build-gate-twin.py <專案根> <slug> 4-spec`
> (母版在 `scripts/`)。它讀 md 逐條解析,不手抄;解析不到任何一條會直接失敗。
> 審頁(R/S 卡 + 生命週期直式 SVG 置中 max-width:360px + 審的時候看什麼 +
> GIVEN/WHEN/THEN,提交判定寫頂欄 verdict:)另一支:`scripts/build-stage4-html.py`
> (--action 授權)。正本 `notes/design/stage4-review-ui-contract.md`。
> 不進 gate-twin STAGES,不包 html-shell。生命週期四格吃
> `## 補助模組生命週期（預覽）` 四條,不只認自創標題。
>
> 反模糊三律(防偷懶條文):
> 1. 每條 S 必須可直接轉成**一個測試**:含具體輸入與可斷言輸出;禁模糊詞
>    (適當/正確/合理/必要時/妥善/robust/等等/視情況)。
> 2. 未定事項禁寫「TBD/之後再說/實作再定」—— 只能列入 Drafting Decisions
>    (標待裁決)或退回提問。
> 3. G2 逐 S 自問:「fresh 工程師只看這條,寫得出測試嗎?」寫不出 = 重寫。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項併項、禁一發全生):
> 0. 接手盤點:先前站核對 —— 2-decision status=approved(G1 過)?3-prototype 若
>    存在,findings 已回寫 2-decision 且 frontmatter 收尾?缺 → 停,回補。再讀
>    1-discussion(驗收雛形/OQ)、2-decision(Decision/Scope/Success Criteria)、
>    living spec 相關域。完成 = 前站核對過 + 雙源清點回報(雛形 N 條、living 受影響條文)。
> 1. 雙源列 R:驗收雛形逐條 → ADDED;living spec 受影響 → MODIFIED/REMOVED
>    (引原條文)。完成 = R 清單經使用者確認範圍(確認紀錄節留一行)。
> 2. 逐 R 展開 S:一次一個 R,GWT 寫到「可直接變一個測試」(具體輸入+可斷言輸出),
>    **每 S 承接 1-discussion 該條驗收雛形的「觀測方式」**(從哪看/看到什麼算對/
>    拿什麼資料試;雛形沒寫就在此補齊,純內部行為註明「無外部現象」)。
>    段段給使用者確認。完成 = 全 R 展開、每 S 有觀測欄、每段有確認(確認紀錄節留一行)。
> 3. 邊界收尾與 Stage 3 對帳,分三小步:
>    - **3a. 收尾四小節**:Acceptance Criteria(全 S 綠+回歸+非功能;行為不變 →
>      golden master)、Out of Scope、Diff Budget、Dependencies。
>      完成 = 四節齊。
>    - **3b. Verification Profile + Design Boundary**:同步填 Verification
>      Profile(含 `lane:` 欄,Lane 規則見該節;Risk 判準見該節;Risk: high →
>      Failure Model 表必填)與 Design Boundary Contract(條件式:觸發條件見該節,
>      全未命中才可 `n-a` + 具體理由;Fast lane 不豁免觸發條件)。
>      完成 = Verification Profile 填畢 + Design Boundary Contract 有結論
>      (applicable 全填 / n-a 附理由)。
>    - **3c. Stage 3 對帳**:逐一核對 3-prototype Demo Script 場景。每個已
>      ACCEPTED 的場景必須對應至少一條 R/S,或在 Out of Scope 明列排除理由;
>      沒有 Stage 3 時記 N/A。Method 走查條列也算 ACCEPTED 行為的下落來源之一;
>      Operational Context 的 `Recovery:` 欄位內容也算下落。
>      完成 = Stage 3 對帳逐場有下落。
> 4. Drafting Decisions 清點:草擬自拍板逐條進上層表(決定了什麼|為什麼|依據|
>    若被推翻會怎樣|狀態),純內部技術選擇進下層清單;全文掃
>    TBD/之後再說/實作再定 → 命中即轉 DD 或退回提問。完成 = 掃描零殘留。
> 5. 自檢(反模糊掃描):**先跑機械關卡** `scripts/check-spec-gate.sh <本檔路徑>`
>    (C1 每 S 有觀測欄 / C2 Profile 可解析 / C3 lane×Risk 合法 / C4 模糊詞 /
>    C5 DD 無殘留待裁決);紅了先修再往下,它擋的都是模板明文要求卻沒人擋的項。
>    機械過了才做人工部分:鏈檢每條驗收雛形 ≥1 個 S 承接、每 MODIFIED 有原文引用。
>    任一否 → 重寫該 S;(選配)每 S 產 named test skeleton 入 Test Skeletons 節。
>    完成 = 機械關卡 exit 0 + 逐 S 打勾 + 鏈檢清零。
> 6. G2 送審:html twin(R 級行為流程圖;DD 待裁決置頂)→ in-review → reviewer。
>    審查者依序:適格人類 reviewer → fresh-context reviewer Agent → owner 自審
>    (有記錄的最後手段)。G2 審查關鍵條件 = R/S 全審 + DD 全裁決
>    + Verification Profile(依 lane 正確填寫;未填視為步 3 未完成)
>    + Demo verdict(條件式:無 Stage 3 trigger → N/A+原因;有 trigger → 需人類
>    ACCEPTED,REVISE/NOT_REVIEWED 不得過,跳過需 Owner Call;Agent 不得代填)——
>    條件全文見 README §7。核准 → 三連動。
>    完成 = verdict+三連動。
>
> 起草前估 S 數,單份 >~40 → 先切片(見 README §14)。
>
> Operational Context(承接 1-discussion Real-world Context 與 3-prototype Demo 回饋):
> 涉人員操作/交接/等待/權限的重要 S 必附(欄位見 S-1 樣板);純內部行為 S 寫
> 「不適用 + 一句理由」。每個重要 S 須同時答得出五問 —— 系統要做什麼?人看到後要做
> 什麼?誰有權決定?哪些事情不在系統內發生?外部事情沒完成時,系統顯示什麼?
> Operational Context 附著於 S-id,不另發 Journey/Actor/Interaction ID(單一 ID 鏈)。
> 3-prototype 有 User Demo Feedback 時:Human verdict ≠ ACCEPTED → 相關互動 S 不得
> 定案(列 Drafting Decisions 待裁決,或退回 Stage 3 重新 Demo)。

## ADDED Requirements
<!-- Scenario 種子:先收割 1-discussion.md 的「驗收雛形」,逐條升級為正式 GWT -->
### R-1: 系統 SHALL <行為>
#### S-1
- GIVEN
- WHEN
- THEN
- 觀測(承接 1-discussion 驗收雛形;7 據此驗現象):從哪看 | 看到什麼算對 | 拿什麼資料試
  <!-- ⚠️ **觀測方式必須在本 repo 可執行**(後端 = 打得出 request、批次 = 看得到 log/
       產出檔)。指向本 repo 之外的東西(前端在另一 repo、尚未實作、要真人操作外部系統)
       → **當場**在本欄標 `n-a:<理由>` 並補一條本 repo 內可執行的替代觀測。
       理由:7-review 步 2b 的「現象證據逐 S 相符」是 G3 的 PASS 條件之一,
       這裡寫下做不到的事,等於在 G2 就種下一個 G3 必然的 ❌。
       (2026-08 order-intake 實測:多數 S 的觀測欄寫的是前端畫面,而前端屬另一 repo
       且尚未實作 —— 整個現象證據節到 G3 才發現結構上跑不了。) -->
- Operational Context(涉人員操作/交接/等待/權限的重要 S 必填;純內部行為 S 寫「不適用+理由」):
  - Actor:
  - Goal:
  - Situation:
  - Known information:
  - Missing information:
  - Human decision:
  - Authority:
  - External dependency:
  - Out-of-system action:
  - Waiting/timeout behavior:
  - Recovery:
  - Audit/handoff requirement:
  - Observation:

## MODIFIED Requirements
<!-- 引 living spec 原條文,標出改什麼 -->

## REMOVED Requirements

## 行為流程圖(R 級)
<!-- 每個主要 R 一張行為流程(輸入 → 分支 → 輸出);判準同 README §6:
     純線性 → ASCII 半形;多分支/跨層 → html 用 SVG(md 留 ASCII 正本)。gate 前必有。
     每個 R-id 必須在圖上,該 R 標題 SHALL 後的行為詞至少一個在圖上;改行為詞必須改圖。 -->

## Acceptance Criteria
<!-- 打包驗收:全部 S 綠 + 既有測試全綠(回歸)+ 非功能(效能/相容/安全)。
     行為不變類 → golden master:同輸入,改動前後輸出逐列一致 -->

## Out of Scope

## Diff Budget
<!-- ⚠️ 本節整節是**估計**,不是事實。模板自己實測過誤差可達 3 倍(見下 ③)。
     審的時候當預測看,不要當承諾;數字沒把握就直接標 [Assumption]。

     預期 ≤N 檔 / ≤M 行。超支本身非偏差,是停下判 L1/L2 的訊號;分不清一律當 L2。

     估法(2026-08 order-intake 實測後補;舊版本節全文只有上面這兩句,連怎麼估都沒說):
     ① 建議按區塊拆估,不要只給一個總數(例:ent schema / handler / repo / migration /
        測試 各自一行 ≤N 檔 / ≤M 行),超支時才看得出是哪一塊爆的。
     ② 測試檔與非測試碼分開估——兩者的行為與係數天差地遠,合併成一個總數會讓
        「非測試碼準、測試碼爆」被平均掉,看起來只是小超支,實際是估法整個錯了。
     ③ 若本輪計畫用突變測試／對抗式驗證(mutation/property-based)當補償控制,
        測試檔的估法要用不同係數——不是「一個 S 一條測試」的天真估法。實測(order-intake,
        26 個 T、約 160 刀突變):天真估法 ~15 檔/~5,800 行,實得 20 檔/18,458 行,
        約為天真估法的 **3 倍**。理由:每一刀首輪全綠的突變都要補一條新測試,
        這是紀律的直接後果,不是估錯。
     ④ 超支本身非偏差,是停下判 L1/L2 的訊號;分不清一律當 L2(與原句一致,維持不變)。 -->

## Dependencies
<!-- 依賴的其他 feature / 外部系統 / migration。每個新依賴/新工具一行 justification
     (為何需要),G2 一併審;未經本節授權的新 capability 屬 7-review finding -->

## Design Boundary Contract(條件式;G2 一併審)
<!-- 本章節是 Stage 4 的一部分,不是新 Stage、不新增 Gate、不新增 ID 鏈 ——
     沿用既有 R/S id、Module 名與 Interface 名。詳細語意正本:
     `notes/design/design-boundary-contract.md`(觸發條件判準、欄位語意、好壞範例、
     n-a 合法與非法例、Architecture 與 Software Design 的分界)。

     觸發條件(任一命中即必填,`Applicability: applicable`):
       ①跨模組或跨 bounded context ②新增或修改公開 API ③新增或修改跨模組 Interface
       ④Schema migration 或資料所有權變更 ⑤新增 Queue/Event/Scheduler/Background job
       ⑥新增外部服務或系統整合 ⑦涉及 Transaction/Concurrency/Lock/Idempotency
       ⑧新增 Network/Filesystem/Subprocess/Credential capability ⑨Feature Risk = high
       ⑩三個以上模組共同參與主要行為 ⑪有狀態機或複雜錯誤恢復流程
     全部未命中才可寫 `Applicability: n-a — <具體理由>`;不得只寫「不適用」。
     Fast lane 預設可 n-a,但命中上列任一條仍必須填,不得因 fast lane 跳過。

     寫作紀律(保持精簡,不是巨型架構文件):
     - applicable 不代表要畫大型 UML;小型 Feature 一至兩列即可完成。
     - 涉及資料 → 說清楚 Data owner;涉及跨模組 → 說清楚依賴方向;
       涉及寫入 → 說清楚 Transaction/Consistency boundary;
       涉及公開 Interface → 說清楚相容策略;涉及狀態或錯誤流程 → 留下 Test seam。
     - 不重複 Reliability Triage 內容,只引用其結論;不重複 Failure Model,
       只說明 Failure 在哪個 Boundary 被隔離或傳遞;不重複 Operational Context。
     - 不得藉本章節新增未經使用者核准的產品行為(要新增行為走 R/S 與 G2)。 -->

- Applicability: applicable | n-a — <理由>
- Trigger(s): <命中的條件;n-a 時寫 —>
- Design source: <既有 pattern／ADR／living spec;無則寫 new local design>

### Architecture Boundaries
<!-- 跨越模組邊界的事。Forbidden dependencies 沒有時寫 —,不留空 -->
| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|

### Interface & Consistency Contract
<!-- 涉及寫入時 Transaction / Consistency boundary 不得省略:要答得出
     「這兩筆寫入只成功一筆會怎樣」 -->
| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|

### Software Design
<!-- 模組內部的事。Test seam 指到可注入點/可觀測點,寫「加測試」不合格 -->
| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|

### Design Constraints
- 必須:
- 禁止:
- Extension point:
- Known design limit:
<!-- Known design limit = 明知做不到或不保證的事,誠實列出不扣分;
     把已知缺口寫成「已處理」才是問題。與 7-review known limits 同一件事,不另立追蹤鏈 -->

## Verification Profile(G2 一併審)
<!-- Risk 二值的唯一定義住本節;本節 Risk = Feature Risk(決定 Profile 深度與 lane
     升級);5-tasks T 級 `Risk:` 欄 = Task Risk(決定該 T review-mode 缺省)——
     兩 scope 沿用同一判準,不另設第二套分級。Required 層在 7-review Verification
     Evidence 裡只能 pass/fail,unverified/n-a 不滿足 Required;Excluded 層在
     Evidence 記 n-a + 理由,維持層清單全量可稽核 -->
- lane: full | fast(必填;G2 依 lane 驗 Profile 填寫,Lane 規則見下)
- Risk: normal | high(缺省 normal;判準:涉金流/auth/資料遺失/併發/公開 API/不可逆
  改動 → high;此即 Feature Risk)
- Failure model:(Risk: high 必填,normal 選配;表見下)
- Negative constraints:(本次變更「不得」做的事,逐條;來源:Out of Scope、
  living spec 不變量、回歸義務)
- Required layers:(Final Fresh Run 必跑;本欄必須在,可寫「無」/none,缺欄 = E7 紅。Gauntlet 讀本欄,漏帶 `--require-layer` 不再 fail-open。旗標只能加嚴;`--profile` 不得指向別份 feature)
- Conditional layers:(條件觸發;註明觸發條件,如「dependency set 變動 → Supply chain」)
- Explicitly excluded layers:(明示排除 + 一句理由;禁默排)
- Final fresh entry point:(單一 persisted 命令,CI/人類皆一條命令重跑)
- Reliability triage:(Full 與 Fast lane 都必答;逐項二選一 + 具體理由)
  - Concurrency: applicable | n-a — <理由;適用時指向 S／Failure Model／Out of Scope／Known limit>
  - Idempotency: applicable | n-a — <理由;適用時指向契約或未覆蓋風險>
  - Timeout/retry: applicable | n-a — <理由;適用時指向契約、驗證層或未覆蓋風險>
<!-- Reliability triage 規則:①`n-a` 必附一句具體理由,不能只寫「不適用」。
     ②`applicable` 不等於本輪一定要實作,但必須明確落到至少一處:R/S、Failure Model、
     Negative Constraints、Required／Conditional 驗證層、Out of Scope／Known limit。
     ③本欄只把已存在或確實相關的風險顯性化,不得據此自行新增產品行為或可靠性保證。 -->

### Lane 規則(lane 欄的填寫契約;runtime 讀 `lane:` 行與 `- Risk:` 首值)
- Full lane = 完整 Profile:上列全欄(Feature Risk/Failure Model/Negative Constraints/
  Required/Conditional/Explicitly Excluded/Final Fresh Entry Point)。
- Fast lane = 最小 Profile,本節只填五欄:`Risk: normal` / `Verify:` /
  `Negative Constraints:` / `Advanced verification excluded:` / `Exclusion reason:`
  (排除的重驗證層明示 + 一句理由,禁默排)。
- 兩 lane 共用(不受 lane 影響):`Reliability triage:` 三問必答。它**不在** fast lane
  的五欄之內,但 fast lane 一樣要答 —— 多半三項皆 `n-a`,理由仍不得省。看到「五欄」
  就以為 fast lane 只需五行 = 漏填,G2 視為步 3 未完成。
- 自動升 Full(任一命中即不得 fast):Risk high、schema migration、權限或資料隔離、
  資料刪除、不可逆資料轉換、金流/交易、核心醫療業務邏輯、並發/鎖/排程、新增
  network/filesystem/subprocess/credential capability、對外 API 契約變更、
  高風險人機互動。
- `lane: fast` 配 `Risk: high` → Runtime(start 時)、模板檢查與 Gate 一律拒絕;
  例外僅限 Owner Call 明示 —— 於本節寫**結構化專用欄**(runtime 唯一認的形):
  `- Owner Call 例外:<非空理由>`
  (行首 dash、「Owner Call 例外」+ 冒號 + 非空理由;雜訊行/敘述性提及不觸發,
  理由留空不構成例外)。
- **lane 由判準決定,不由 owner 指示決定**;owner 指示與判準不同時,必須在本節明記
  **偏離與理由**(往嚴的方向偏離——例如判準算 fast、owner 指示走 full——也要記,
  不是只記「降級」那個方向)。未記偏離的 lane 選擇視為判準未確認,G2 視為步 3 未完成。

### Failure Model(Risk: high 必填)
<!-- ⚠️ 本表整表是**推測**——還沒發生的失效,不是觀測到的現象。它跟 7-review 的
     「現象證據」表長得一樣,但那張是實際跑出來的,這張是猜的,別把兩者當同一種東西。

     先答「這個改動可能如何傷害使用者/資料/權限/流程/系統」再選層;每個 mode 指到
     一個「真能抓到它」的層,蓄意不覆蓋 → 未覆蓋原因明寫並轉載 7-review known limits -->
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|

## Drafting Decisions(草擬自判,待人審)
<!-- 模型草擬時自己拍的板。G2 過關條件之一 = 本節全裁決;✗ 打回重寫。審後保留(審計軌跡)。
     分兩層,判準與 2-decision 的 Owner Calls 同一套:
     - 上層:會改變使用者看得到的行為、交付範圍或流程 → 下表逐條裁決。
     - 下層:純內部技術選擇(資料結構寫法、索引型式、命名慣例)→ 下方清單告知即可。
     - 拿不準放哪層 → 一律放上層(同 README §5 判級疑義原則)。
     「依據」欄:寫得出出處就寫 `檔:行` 或實際指令輸出;寫不出就寫 `[Assumption]`。
     沒有依據不是不能寫,是不能寫得像有依據(同 1-discussion 的 [Assumption] 規則)。 -->

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 |  |  |  |  |  |

### 內部技術選擇(下層,告知即可)
<!-- 一行一項;approver 掃過即可,不逐條裁決 -->

## Test Skeletons(選配)
<!-- 每 S 一個 named stub(名含 S-id,如 test_s_1_1_store_half_slot),語言隨 repo,
     內文可空。給執行層高保真參照(code 形式 > 散文);不採用整節留空 -->

## 確認紀錄
<!-- 過程留痕,一行一筆(項目 | 日期),如「R 範圍確認 | 2026-07-25」「S 逐段確認完成 | 2026-07-25」 -->
