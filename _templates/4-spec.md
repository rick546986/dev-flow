---
feature: <slug>
stage: 4-spec
status: draft
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
> 3. 邊界收尾:Acceptance Criteria(全 S 綠+回歸+非功能;行為不變 → golden master)、
>    Out of Scope、Diff Budget、Dependencies;同步填 Verification Profile(含 `lane:`
>    欄,Lane 規則見該節;Risk 判準見該節;Risk: high → Failure Model 表必填)。
>    Stage 3 對帳:逐一核對 3-prototype Demo Script 場景。每個已 ACCEPTED 的場景
>    必須對應至少一條 R/S,或在 Out of Scope 明列排除理由;沒有 Stage 3 時記 N/A。
>    完成 = 四節齊 + Verification Profile 填畢 + Stage 3 對帳逐場有下落。
> 4. Drafting Decisions 清點:草擬自拍板逐條(決策|理由|棄項|待人審);全文掃
>    TBD/之後再說/實作再定 → 命中即轉 DD 或退回提問。完成 = 掃描零殘留。
> 5. 自檢(反模糊掃描):逐 S 過三律(見上,含模糊詞掃);鏈檢:每條驗收雛形 ≥1 個 S
>    承接、每 MODIFIED 有原文引用。任一否 → 重寫該 S;(選配)每 S 產 named test
>    skeleton 入 Test Skeletons 節。完成 = 逐 S 打勾+鏈檢清零。
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
     純線性 → ASCII 半形;多分支/跨層 → html 用 SVG(md 留 ASCII 正本)。gate 前必有 -->

## Acceptance Criteria
<!-- 打包驗收:全部 S 綠 + 既有測試全綠(回歸)+ 非功能(效能/相容/安全)。
     行為不變類 → golden master:同輸入,改動前後輸出逐列一致 -->

## Out of Scope

## Diff Budget
<!-- 預期 ≤N 檔 / ≤M 行。超支本身非偏差,是停下判 L1/L2 的訊號;分不清一律當 L2 -->

## Dependencies
<!-- 依賴的其他 feature / 外部系統 / migration。每個新依賴/新工具一行 justification
     (為何需要),G2 一併審;未經本節授權的新 capability 屬 7-review finding -->

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
- Required layers:(Final Fresh Run 必跑)
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
  (排除的重驗證層明示 + 一句理由,禁默排)。`Reliability triage:` 三問不在
  五欄之內但兩 lane 皆必答 —— fast lane 多半三項皆 `n-a`,理由仍不得省。
- 自動升 Full(任一命中即不得 fast):Risk high、schema migration、權限或資料隔離、
  資料刪除、不可逆資料轉換、金流/交易、核心醫療業務邏輯、並發/鎖/排程、新增
  network/filesystem/subprocess/credential capability、對外 API 契約變更、
  高風險人機互動。
- `lane: fast` 配 `Risk: high` → Runtime(start 時)、模板檢查與 Gate 一律拒絕;
  例外僅限 Owner Call 明示 —— 於本節寫**結構化專用欄**(runtime 唯一認的形):
  `- Owner Call 例外:<非空理由>`
  (行首 dash、「Owner Call 例外」+ 冒號 + 非空理由;雜訊行/敘述性提及不觸發,
  理由留空不構成例外)。

### Failure Model(Risk: high 必填)
<!-- 先答「這個改動可能如何傷害使用者/資料/權限/流程/系統」再選層;每個 mode 指到
     一個「真能抓到它」的層,蓄意不覆蓋 → 未覆蓋原因明寫並轉載 7-review known limits -->
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|

## Drafting Decisions(草擬自判,待人審)
<!-- 模型草擬時自己拍的板,每條:決策 | 理由 | 放棄的替代項 | 狀態(待人審→✅/✗)。
     G2 過關條件之一 = 本節全裁決;✗ 打回重寫。審後保留(審計軌跡) -->

## Test Skeletons(選配)
<!-- 每 S 一個 named stub(名含 S-id,如 test_s_1_1_store_half_slot),語言隨 repo,
     內文可空。給執行層高保真參照(code 形式 > 散文);不採用整節留空 -->

## 確認紀錄
<!-- 過程留痕,一行一筆(項目 | 日期),如「R 範圍確認 | 2026-07-25」「S 逐段確認完成 | 2026-07-25」 -->
