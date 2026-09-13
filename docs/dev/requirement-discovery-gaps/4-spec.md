---
feature: requirement-discovery-gaps
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-13
---

# 4. 規格 — 九條需求發現缺口進方法論(change spec)

> 基準:`main` tip `be808fb`(#273 STATUS Stage3 after #270)。G1 PASS + OC-1…OC-6 在 main(`#268`／`#269`)。Human ACCEPTED Stage 3 @ 2026-09-13(`human:rick`;8A 行 `ACCEPTED | role=owner | scenario=AC-1–AC-9`;平行紀錄 #274)。本 hop **只寫** `4-spec.md` + `4-spec.html`。不改 `_templates/`／`skills/`／守衛／範例正本。不改 `STATUS.md`／`HISTORY.md`。**不發明 G2 PASS**(頂欄 `verdict` 空、`status` draft;DD 待人審)。
> Decision 正本:`docs/dev/requirement-discovery-gaps/2-decision.md`(1A+2A+3A+4A+5A+6A+7A+8A;`verdict` PASS)。Stage 3 選定 Variant A 同檔就地欄,不重開 1A–8A。
> 本檔把九條缺口釘成可測 R/S。腳本家族只延伸 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`(及它們已掛進的 `devflow-check`)。不新造 `check-discovery-gaps.sh`。不發明 RW-id。

## 補助模組生命週期（預覽）

主詞是「九缺口的活教師 + 既有三支牙射程」,不是整份方法論。直式圖,置中。
- 新生（這輪沒有）：不加第二套檢查家族、不加 `lookback.md`、不加 RW-id。
- 改行為（相關一格）：模板 1／2／3／4／7 分欄與表頭;dev-talk 發現題前綴;範例 Goals 改口;三支既有牙加射程。
- 退役：沒有。
- 不動：七關結構、OC-1 三支腳本家族名、STATUS 只在整合分支寫、plugin 版本、本 hop 不改模板正本。

## ADDED Requirements

### R-1: 系統 SHALL 把工作結果與解法構想分欄
1A／SC-1。結果節名鎖定 `## Goals`;構想節名鎖定 `## Requested solution`。Goals 指令不再要求候選畫面／API／元件通道。構想不寫進 Goals。`example/contract-expiry-reminder/1-discussion.md` 的 Goals 不再把登入／點擊／一眼可見寫成目標本身。牙走 `check-realworld.sh`(模板＋範例地板)。不重開 1A。

**審的時候看什麼**
看節名與 Goals 第一句。構想在 Goals = 失敗。對照稿「我要 dashboard」必須被指出「構想在錯欄」。

#### S-1.1 模板兩節名都在且 Goals 不再鎖通道
- GIVEN 落地後的 `_templates/1-discussion.md` 與 `skills/dev-talk/nodes/S4-accept.md`
- WHEN 跑 `bash scripts/check-realworld.sh`
- THEN 該檢查 exit 0;1-discussion 模板含字面 `## Goals` 與 `## Requested solution`;Goals 或驗收雛形指令不再把 `畫面路徑 | API 端點` 寫成「從哪看」的唯一候選;S4-accept 不再寫「從哪裡看(畫面/端點/檔案/log)」當硬規則
- 觀測:從 `check-realworld.sh` 的 exit 與兩檔字面看 | exit 0 且兩節名在、舊唯一候選句不在算過 | 拿落地後的模板與 S4-accept 原文測
- Operational Context:不適用 — 模板字面形狀,無人員交接。

#### S-1.2 「我要 dashboard」寫進 Goals 的對照稿必須被指出
- GIVEN 一份 Stage 1 對照稿:Goals 唯一一條是「我要 dashboard」,沒有 `## Requested solution` 節
- WHEN 對該對照稿跑本 feat 掛進 `check-realworld.sh` 的指定形狀檢查(同一入口,不另開 `check-discovery-gaps.sh`)
- THEN exit ≠ 0;stdout 或 stderr 含 `構想在錯欄` 或 `Requested solution`
- 觀測:從該檢查的 exit 與 stderr 看 | exit ≠ 0 且含指定字樣算過 | 用 `scripts/fixtures/` 既有家族下一份「Goals 只寫 dashboard」對照稿測
- Operational Context:
  - Actor:G1 reviewer
  - Goal:構想不能混成目標
  - Situation:採用者抄「我要 dashboard」進 Goals
  - Known information:節名契約、對照稿正文
  - Missing information:該詞在該領域是否真的是工作結果
  - Human decision:退回 Stage 1,把構想搬到 Requested solution
  - Authority:形狀檢查擋錯欄;語意仍是 G1 人審
  - External dependency:無
  - Out-of-system action:在終端機跑指定檢查
  - Waiting/timeout behavior:檢查同步結束;無重試契約
  - Recovery:把 dashboard 句搬到 `## Requested solution` 並標未定案;Goals 改寫工作結果後重跑
  - Audit/handoff requirement:退回理由寫在 G1 審面,不是只在聊天
  - Observation:見本條觀測

#### S-1.3 完整範例 Goals 不再把登入／點擊／一眼可見當目標
- GIVEN 落地後的 `example/contract-expiry-reminder/1-discussion.md`
- WHEN 讀 `## Goals` 節(到下一個 `##` 為止)
- THEN 該節沒有把「登入後」「點擊可直達」「一眼可見」寫成目標句本身;若仍描述呈現面,該句必須在 `## Requested solution` 且標未定案
- 觀測:從該檔 Goals 節字面看 | 三個舊教師詞不在 Goals 目標句算過 | 拿落地後範例原文測
- Operational Context:不適用 — 範例教師字面,無人員交接。

### R-2: 系統 SHALL 讓發現題不附推薦答案
1A／SC-2。發現題前綴字面 `發現｜`(禁附推薦)。裁決題前綴字面 `裁決｜`(可附選項／差異／推薦)。`skills/dev-talk` 發現題路徑不再把「附推薦答案」當硬規則。刪掉其中一邊前綴對稱句 → 靜態牙紅。不要求從最終 1-discussion 還原整場對話。

**審的時候看什麼**
只看問句本身有沒有 `發現｜`／`裁決｜`,以及發現題是否先給答案。

#### S-2.1 發現題路徑不再硬性要求附推薦
- GIVEN 落地後的 `skills/dev-talk/nodes/N3-probe.md` 與指南對稱句
- WHEN 跑 `bash scripts/check-realworld.sh`
- THEN 該檢查 exit 0;N3-probe 完成條件或三律不再把「附推薦答案」寫成發現題硬規則;檔內含字面 `發現｜` 與 `裁決｜`
- 觀測:從 exit 與 N3-probe 字面看 | 舊硬規則句不在、兩個前綴都在算過 | 拿落地後 N3-probe 原文測
- Operational Context:
  - Actor:討論 agent／訪談對象
  - Goal:被問「上次真的怎麼做」時題目本身不塞推薦
  - Situation:N3 逐題逼問
  - Known information:題目前綴契約
  - Missing information:受訪者上次真實做法
  - Human decision:答現況,不挑方案
  - Authority:討論 agent 出題;受訪者答
  - External dependency:訪談在系統外
  - Out-of-system action:口頭或 Email 答「上次怎麼做」
  - Waiting/timeout behavior:等受訪者答完才進下一題
  - Recovery:發現題已附推薦 → 刪推薦、加 `發現｜` 後重問
  - Audit/handoff requirement:Interview Log 高影響發現題可抽查問句
  - Observation:見本條觀測

#### S-2.2 裁決題可以附選項
- GIVEN 一句已核事實「Journey 痛點發現被錨定」
- WHEN 討論 agent 輸出裁決題 `裁決｜這條痛點進本方案還是 Non-Goal?` 並附兩個選項
- THEN 指定檢查不因「裁決題附選項」而 exit ≠ 0
- 觀測:從指定檢查對「裁決題含選項」對照稿的 exit 看 | exit 0 算過 | 用帶 `裁決｜` 且附選項的對照問句測
- Operational Context:不適用 — 裁決題正負向對照,無新交接。

#### S-2.3 刪掉其中一邊前綴對稱句必須紅
- GIVEN 一份 skill 或指南對照稿只留 `發現｜`、刪光 `裁決｜`(或相反)
- WHEN 跑 S-2.1 同一支指定檢查
- THEN exit ≠ 0;輸出含 `發現｜` 或 `裁決｜`
- 觀測:從 exit 與輸出看 | exit ≠ 0 且點名缺的那一個前綴算過 | 用刪邊對照稿測
- Operational Context:不適用 — 靜態對稱牙,無人員交接。

### R-3: 系統 SHALL 要求高影響主張帶狀態枚舉與來源 XOR 期限
2A／SC-3／OC-5。高影響列(見 DD-1)必須就地表列:主張原文片段、狀態 ∈ {Observed, Reported, Inferred, Assumption, Conflict}、來源類型、as-of、角色或範圍、支持哪一段、限制。來源 XOR Assumption+期限。點頭紀錄不得當唯一來源。不要求 Stage 1 每一句 Context 都貼狀態。

**審的時候看什麼**
沿一條高影響主張走回來源欄或期限欄。只有「使用者反映」= 失敗。

#### S-3.1 七欄齊且枚舉 ∈ 集合的好卡必須綠
- GIVEN 一份 Stage 1 對照稿,高影響表有一列:主張=`Journey「發現被錨定」`、狀態=`Observed`、來源類型=`本 tree skill`、as-of=`2026-09-13`、角色或範圍=`討論 agent`、支持哪一段=`1-discussion Context N3`、限制=`無採用現場逐字稿`
- WHEN 跑本 feat 掛進 `check-realworld.sh` 的指定形狀檢查
- THEN exit 0
- 觀測:從該檢查 exit 看 | exit 0 算過 | 用 Stage 3 Method 2A 好卡同形 fixture 測
- Operational Context:
  - Actor:G1／G2 reviewer
  - Goal:主張能走回可重開來源
  - Situation:審高影響列
  - Known information:七欄與枚舉集合
  - Missing information:來源檔是否仍支持該句(語意,人審)
  - Human decision:抽一條往回走;對不上退回 Stage 1
  - Authority:牙只驗形狀;G1 驗語意
  - External dependency:本 tree 來源檔
  - Out-of-system action:打開來源路徑核對行段
  - Waiting/timeout behavior:無
  - Recovery:缺欄則補來源或改 Assumption+期限後重跑
  - Audit/handoff requirement:表列留在 1-discussion 同檔
  - Observation:見本條觀測

#### S-3.2 無枚舉且無來源也無期限的壞卡必須紅
- GIVEN 一份對照稿,高影響列只寫「使用者反映希望 dashboard」,沒有狀態枚舉、沒有來源類型、沒有 `期限=`
- WHEN 跑 S-3.1 同一支指定檢查
- THEN exit ≠ 0;輸出含 `狀態` 或 `來源` 或 `Assumption`
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含指定字樣之一算過 | 用 Stage 3 2A 壞卡同形 fixture 測
- Operational Context:
  - Actor:G1 reviewer
  - Goal:缺來源的高影響主張過不了形狀
  - Situation:壞卡只有「使用者反映」
  - Known information:缺哪欄
  - Missing information:真實來源
  - Human decision:退回補來源或標 Assumption+期限
  - Authority:指定檢查 exit 擋送審地板
  - External dependency:無
  - Out-of-system action:問訪談對象或讀已核路徑
  - Waiting/timeout behavior:等補欄
  - Recovery:補七欄或 Assumption 四欄後重跑;不得用點頭紀錄當唯一來源
  - Audit/handoff requirement:退回寫明缺枚舉還是缺來源
  - Observation:見本條觀測

#### S-3.3 點頭紀錄不得當唯一來源
- GIVEN 一份對照稿,高影響列狀態=`Observed`,來源類型只寫「使用者點頭」或「認可後清單」,沒有路徑出處、也沒有 `期限=`
- WHEN 跑 S-3.1 同一支指定檢查
- THEN exit ≠ 0;輸出含 `點頭` 或 `不是來源`
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含指定字樣之一算過 | 用「點頭當 Observed」對照稿測
- Operational Context:不適用 — 與 S-3.2 同型負向,差在來源格填了點頭。

### R-4: 系統 SHALL 拒絕引用已過期未結案高影響 Assumption 的 4-spec 送 G2
3A／SC-4。擋點是既有 `check-spec-gate.sh`(G2 形狀 Gate),不是只加厚模板地板。4-spec 若仍引用高影響、已過期限、未 resolved、無 Owner Call 接受風險的 Assumption → exit 1。已驗轉 Observed／Reported、或結案=`OC-accept` 的對照稿 exit 0。期限機器形見 DD-3。

**審的時候看什麼**
看 `check-spec-gate.sh` 對過期卡的 exit,不是看模板有沒有四欄。

#### S-4.1 過期 + 未結案 + 無 OC 必須 exit 1
- GIVEN 一份 4-spec 含 Cited Assumptions 列:引用片段=`Q6 採用現場仍把解法寫進 Goal`、狀態=`Assumption`、期限=`Stage 2`、結案為空或 `—`;該檔沒有任何 `OC-accept`／`Owner Call` 接受該列風險的字樣
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN exit 1;stdout 或 stderr 含 `過期` 或 `Assumption`
- 觀測:從該命令的 exit 與輸出看 | exit 1 且含指定字樣算過 | 用「期限=Stage 2、結案空、無 OC」對照 4-spec 測
- Operational Context:
  - Actor:G2 reviewer
  - Goal:未驗的高影響假設進不了 G2
  - Situation:期限已過(4-spec 存在 ⇒ Stage 2 期限已過)、列仍是 Assumption
  - Known information:Cited Assumptions 表、期限規則(DD-3)
  - Missing information:該假設現在是真是假
  - Human decision:驗轉 Observed／Reported,或寫 OC-accept,或刪引用
  - Authority:`check-spec-gate.sh` exit 1 擋送審
  - External dependency:無
  - Out-of-system action:對帳本 repo 範例或接受風險
  - Waiting/timeout behavior:擋到人結案;無自動重試
  - Recovery:結案改 Observed／Reported／OC-accept 後重跑;不要只改散文說「知道有假設」
  - Audit/handoff requirement:拒絕發生在 G2 送審命令,不是事後口頭
  - Observation:見本條觀測

#### S-4.2 已驗或 OC-accept 的過期列必須 exit 0(形狀)
- GIVEN 一份 4-spec 引用同一條期限=`Stage 2` 的假設,結案=`OC-accept` 且依據寫 `OC-3`,其餘 C1–C6 形狀齊
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN 過期-Assumption 這一項不構成 exit 1(本項綠;其他 C 項仍各自判)
- 觀測:從該命令輸出看 | 無「過期 Assumption」FAIL 行算過 | 用本 slug 自己的 Cited Assumptions(OC-3)測
- Operational Context:
  - Actor:G2 reviewer
  - Goal:owner 已收窄的假設可以送審
  - Situation:OC-3 已寫「不用假訪談收尾」
  - Known information:OC-3 正文、結案欄
  - Missing information:採用現場是否照抄(仍是 Assumption,已接受)
  - Human decision:接受 OC-3 收窄
  - Authority:owner OC;牙認 OC-accept
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:若推翻 OC-3 → 回第 2 站,不得只改 4-spec
  - Audit/handoff requirement:結案欄看得見 OC-3
  - Observation:見本條觀測

### R-5: 系統 SHALL 要求 Human verdict 一行含角色與場景
8A／SC-5。模板與牙要求一行內有角色與場景。字面:`Human verdict: <ENUM> | role=<Actors 表角色> | scenario=<AC-id>`。只寫 `ACCEPTED` + 姓名日期的對照稿不得當完整 verdict。不做 Actor Coverage 全表。既有 attestation 規則不變(人類親填;`human:<姓名> @ <YYYY-MM-DD>`)。

**審的時候看什麼**
遮住前後文只看 Human verdict 那一行,能否答「驗了誰、驗了哪場」。

#### S-5.1 含 role 與 scenario 的一行算完整形狀
- GIVEN `_templates/3-prototype.md` 落地後,User Demo Feedback 的 Human verdict 列含字面 `role=` 與 `scenario=`
- WHEN 跑 `bash scripts/check-realworld.sh`
- THEN exit 0;模板該行不是只寫 `ACCEPTED | REVISE | NOT_REVIEWED` 而無 role／scenario 提示
- 觀測:從 exit 與模板 Human verdict 行看 | 兩個鍵都在算過 | 拿落地後 3-prototype 模板測
- Operational Context:
  - Actor:後讀 3-prototype 的人
  - Goal:一眼看出驗了哪個角色、哪場
  - Situation:讀 ACCEPTED 行
  - Known information:8A 字面
  - Missing information:寫下的角色是否真的是操作者(牙不驗身份)
  - Human decision:不完整就退回補行
  - Authority:人類填 verdict;Agent 禁代填 attestation
  - External dependency:Demo 在系統外
  - Out-of-system action:人類走 Demo 後親填
  - Waiting/timeout behavior:未填 = NOT_REVIEWED,不得當 ACCEPTED
  - Recovery:補 `role=` 與 `scenario=` 後重讀;不要只補姓名日期
  - Audit/handoff requirement:attestation 仍獨立一行
  - Observation:見本條觀測

#### S-5.2 只寫 ACCEPTED 加姓名日期的對照稿不完整
- GIVEN 一份 3-prototype 對照稿,Human verdict 行只有 `ACCEPTED`,另有 `human:rick @ 2026-09-13`,沒有 `role=`、沒有 `scenario=`
- WHEN 對該對照稿跑本 feat 掛進 `check-realworld.sh` 的指定形狀檢查
- THEN exit ≠ 0;輸出含 `role` 或 `scenario`
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含指定字樣之一算過 | 用「殘行 ACCEPTED + 姓名日期」fixture 測
- Operational Context:不適用 — 與 S-5.1 對照的負向形狀。

### R-6: 系統 SHALL 為 Stage 1 高影響列留下 disposition 去向
4A／SC-6。Stage 2 表頭三欄:引用(Stage 1 原文片段)／去向／理由。去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗}。不另發 RW-id。標「本方案處理」的列,Stage 4 至少一條 R/S;其餘落到 Out of Scope／Known limit／後續 slug。缺去向 → G1 審面或指定檢查能指出來。

**審的時候看什麼**
用原文片段(不是 RW-1)對一次。去向空白 = 失敗。

#### S-6.1 模板與範例地板有三欄表頭
- GIVEN 落地後的 `_templates/2-decision.md`
- WHEN 跑 `bash scripts/check-realworld.sh`
- THEN exit 0;該模板含表頭字面 `引用`、`去向`、`理由`,且含五態去向字面各至少一次(指令或範例列)
- 觀測:從 exit 與 2-decision 模板字面看 | 三欄與五態都在算過 | 拿落地後模板測
- Operational Context:不適用 — 模板地板。

#### S-6.2 本方案處理的列在 4-spec 至少一條 R/S
- GIVEN 一份已 approved 的 2-decision,disposition 有列 `Journey「痛點消失」` 去向=`本方案處理`;對應 4-spec 全文
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN 若 4-spec 正文(含 Stage 3 對帳表)沒有出現片段 `痛點消失` 且沒有任何 `S-` 承接 → 該項 FAIL、整體 exit 1;本 slug 本檔對帳表有該片段且落到 S-6.2／S-6.3 → 本項綠
- 觀測:從 spec-gate 輸出看 | 缺片段則 FAIL、有片段則本項綠算過 | 用「有 disposition、4-spec 刪光該片段」對照稿,以及本檔正文測
- Operational Context:
  - Actor:收斂者／G2 reviewer
  - Goal:Stage 1 痛點到 Stage 4 仍有去向
  - Situation:寫完 4-spec 要送 G2
  - Known information:2-decision disposition 表、4-spec R/S
  - Missing information:無
  - Human decision:漏列就補 R/S 或改去向
  - Authority:spec-gate 擋「本方案處理卻無下落」
  - External dependency:同 slug 的 2-decision
  - Out-of-system action:無
  - Waiting/timeout behavior:擋到補下落
  - Recovery:補對帳列或把去向改成刻意維持／Non-Goal／另開 slug／仍待驗
  - Audit/handoff requirement:對帳表留在 4-spec
  - Observation:見本條觀測

#### S-6.3 去向空白或使用 RW-id 必須被指出
- GIVEN 一份 2-decision 對照稿,列 `Journey「痛點消失」` 的去向格空白;或引用格寫 `RW-1`
- WHEN 對該對照稿跑本 feat 掛進 `check-realworld.sh` 的指定形狀檢查
- THEN exit ≠ 0;輸出含 `去向` 或 `RW-id` 或 `RW-1`
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含指定字樣之一算過 | 用 Stage 3 4A 壞卡同形 fixture 測
- Operational Context:不適用 — 負向表頭／ID 鏈。

### R-7: 系統 SHALL 在 7-review Exit 留下回看四欄
5A／SC-7。字面四欄:`回看日期:`／`回看 owner:`／`資料來源:`／`低於何值重開:`。放在 `_templates/7-review.md` 的 Exit Checklist。結果到期用既有 `history-append.sh` 追加。不另造永久 `lookback.md`。缺任一欄 → 指定檢查 exit ≠ 0。G3 不必等數週結果。填了數字 ≠ 問題已改善(人判)。

**審的時候看什麼**
Exit 四個欄位名在不在。只寫 HISTORY、Exit 無約定 = 失敗。

#### S-7.1 模板 Exit 四個欄位名都在
- GIVEN 落地後的 `_templates/7-review.md`
- WHEN 跑 `bash scripts/check-realworld.sh`
- THEN exit 0;Exit Checklist 節含四個字面 `回看日期:`、`回看 owner:`、`資料來源:`、`低於何值重開:`
- 觀測:從 exit 與 Exit 節字面看 | 四個欄位名都在算過 | 拿落地後 7-review 模板測
- Operational Context:
  - Actor:owner
  - Goal:出貨時留下誰／何時／用什麼／低於何值重開
  - Situation:勾 Exit、尚未到期
  - Known information:四欄字面、HISTORY 寫入口
  - Missing information:到期後的真實指標
  - Human decision:填四欄;到期再 append 結果
  - Authority:owner 填約定;牙驗欄在
  - External dependency:`scripts/history-append.sh`
  - Out-of-system action:日曆回看、讀採用專案 Stage 1
  - Waiting/timeout behavior:等到回看日期;到期未回看不得把問題寫成已改善
  - Recovery:缺欄則補四欄後重跑;不要另造 `lookback.md`
  - Audit/handoff requirement:約定在 7-review Exit;結果在 HISTORY
  - Observation:見本條觀測

#### S-7.2 缺任一欄的對照稿必須紅
- GIVEN 一份 7-review 對照稿,Exit 只寫「之後再看」或只含三個回看欄
- WHEN 對該對照稿跑本 feat 掛進 `check-realworld.sh` 的指定形狀檢查
- THEN exit ≠ 0;輸出含所缺欄位名或 `回看`
- 觀測:從 exit 與輸出看 | exit ≠ 0 算過 | 用缺欄 Exit fixture 測
- Operational Context:不適用 — 負向地板。

#### S-7.3 本 feat 不得新造 lookback 永久檔
- GIVEN 本 feat 落地 diff(相對於本 4-spec 寫作時的 main)
- WHEN 列出新增路徑
- THEN 沒有任何新檔名為 `lookback.md` 或 `*-lookback.md`
- 觀測:從 `git diff --name-only` 對落地 PR 看 | 無該檔名算過 | 拿 Stage 6 落地 diff 測
- Operational Context:不適用 — 檔種類禁令。

### R-8: 系統 SHALL 只放行本輪 owner 核准的事實路徑
6A／SC-8／B-1。討論者先在 `1-discussion.md` 的 `## Evidence manifest` 列表:想找哪類／為什麼／擬路徑或來源／owner 核准／已讀。owner 核准後,`devtalk-guard.sh`(或同等讀取圍欄,同一家族)放行該清單路徑。仍禁 `2-decision`／`3-prototype`／`4-spec`／`5-tasks`／`6-implementation-notes`／`7-review`。未核准路徑不得當已授權 evidence。ticket／SOP 裡的解法建議不當事實。

**審的時候看什麼**
核准格是「是」才能讀。讀 2-decision／4-spec 仍被擋。未核路徑被引用 = 失敗。

#### S-8.1 已核准事實路徑讀得到
- GIVEN 一份 1-discussion,`## Evidence manifest` 有列:擬路徑=`_templates/1-discussion.md`、owner 核准=`是`
- WHEN 討論 agent 讀該路徑(dev-talk 白名單延伸後)
- THEN `devtalk-guard.sh` 對該讀取不因「不在舊三類白名單」而擋;該路徑內容可被引用為事件／行為／結果
- 觀測:從守衛對「讀已核路徑」的 exit 看 | 不擋該路徑算過 | 用核准列 + 讀該路徑的 hook 輸入測
- Operational Context:
  - Actor:討論 agent
  - Goal:owner 核准後讀得到事實
  - Situation:manifest 核准格已是「是」
  - Known information:擬路徑、核准格
  - Missing information:路徑裡哪一段支持哪句(人寫出處)
  - Human decision:owner 先核清單
  - Authority:owner 放行;守衛執行
  - External dependency:本 tree 已指名檔
  - Out-of-system action:owner 在 GitHub 或對話核可
  - Waiting/timeout behavior:核准格空白 = 禁讀,停在「等 owner」
  - Recovery:先送清單;核准後才讀;中斷從核准格恢復
  - Audit/handoff requirement:核准痕跡留在 manifest 表
  - Observation:見本條觀測

#### S-8.2 讀 2-decision 或 4-spec 仍被擋
- GIVEN 同一場討論,manifest 即使誤列 `docs/dev/foo/2-decision.md` 或 `4-spec.md` 且核准格寫「是」
- WHEN 討論 agent 讀該方案檔
- THEN `devtalk-guard.sh` exit ≠ 0(或同等擋讀);輸出含 `2-decision` 或 `4-spec`
- 觀測:從守衛 exit 與輸出看 | 擋且點名方案檔算過 | 用讀 2-decision／4-spec 的 hook 輸入測
- Operational Context:
  - Actor:討論 agent
  - Goal:方案檔仍進不去
  - Situation:有人想把 Decision 當事實
  - Known information:圍欄③仍在
  - Missing information:無
  - Human decision:不得用方案檔當 evidence
  - Authority:守衛擋讀
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:從白名單刪該列;改列事實路徑送核
  - Audit/handoff requirement:禁讀寫進輸出,不是只寫 skill 句子
  - Observation:見本條觀測

#### S-8.3 未核准路徑與 ticket 解法不得當已授權
- GIVEN manifest 一列擬路徑為採用現場逐字稿、owner 核准=`未核` 或空白;另一列把 ticket 裡的「做一個 dashboard」當來源
- WHEN 討論 agent 把該未核路徑或 ticket 解法寫進 Context 當已核事實
- THEN 指定檢查或守衛 exit ≠ 0;輸出含 `未核` 或 `解法不當事實`
- 觀測:從 exit 與輸出看 | exit ≠ 0 且含指定字樣之一算過 | 用未核列／ticket 解法對照稿測
- Operational Context:
  - Actor:討論 agent／owner
  - Goal:未授權資料不當證據
  - Situation:Q6 無現場 log
  - Known information:核准格空白、OC-3
  - Missing information:現場逐字稿
  - Human decision:不捏造訪談;維持 Assumption
  - Authority:owner 不核則不得讀
  - External dependency:外部 ticket／SOP
  - Out-of-system action:若要核,owner 明示路徑
  - Waiting/timeout behavior:未核就停
  - Recovery:刪該引用或改標 Assumption
  - Audit/handoff requirement:已讀欄仍為否
  - Observation:見本條觀測

### R-9: 系統 SHALL 在 Fast 進 Stage 4 前收束六問
7A／SC-9／OC-6。進 Stage 4 **之前**填六問,每問「是」或「否」加一句。問句字面鎖定:改變下一步？／改權限／核准語意？／改等待／完成語意？／改角色交接？／改系統外動作？／改中斷恢復？。空白 ≠ 已分診。全否且已有 approved spec 且不改語意的純視覺／文案 → 維持 Fast。命中 → owner 裁升 full、fast+mini、或 OC 接受風險;去向空白 → `check-spec-gate.sh` 對該 Fast 4-spec exit ≠ 0。「只改狀態字、把等待顯示成完成」必須命中第三問。

**審的時候看什麼**
六問在 R/S 之前。等待誤標對照案第三問必須是「是」。空白表不是已分診。

#### S-9.1 Fast 4-spec 缺六問或空白答不得當已分診
- GIVEN 一份 `lane: fast` 的 4-spec,沒有 `## Fast six questions` 節,或六問的「答」格全空
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN exit 1;輸出含 `六問` 或 `Fast`
- 觀測:從 exit 與輸出看 | exit 1 且含指定字樣之一算過 | 用空白六問 Fast fixture 測
- Operational Context:
  - Actor:Fast 實作者
  - Goal:寫規格前先看互動風險
  - Situation:檔數少、想走 Fast
  - Known information:六問表
  - Missing information:這次 diff 是否改等待語意
  - Human decision:逐問答是／否+一句
  - Authority:spec-gate 擋未收束
  - External dependency:已有 approved spec(全否時)
  - Out-of-system action:看 diff
  - Waiting/timeout behavior:未填完不得開寫 R/S
  - Recovery:填六問後重跑;中斷從六問表恢復
  - Audit/handoff requirement:六問節在 ADDED 之前
  - Observation:見本條觀測

#### S-9.2 等待顯示成完成必須命中第三問
- GIVEN 對照案:只改一個狀態字,把等待顯示成完成;六問第 1／2／4／5／6 答「否」,第 3 問若也答「否」
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>` 或本 feat 掛在同一家族的對照檢查
- THEN 不得把該稿當已完成早期分診:exit ≠ 0,或輸出含 `等待` 且要求第 3 問為「是」
- 觀測:從該命令 exit／輸出看 | 第 3 問答「否」的等待誤標稿被擋算過 | 用 Stage 3 AC-9 對照案 fixture 測
- Operational Context:
  - Actor:Fast 實作者／G2 reviewer
  - Goal:等待語意被改時不能假裝 Fast 無害
  - Situation:「只改狀態字」
  - Known information:AC-9 對照案
  - Missing information:owner 要升 full、mini 還是 OC
  - Human decision:第 3 問改「是」並填去向
  - Authority:owner 裁去向;牙擋假「全否」
  - External dependency:無
  - Out-of-system action:owner 裁示
  - Waiting/timeout behavior:命中後停到有去向
  - Recovery:第 3 問改「是」;去向填 full 或 mini 或 OC
  - Audit/handoff requirement:去向寫在六問表最後一列
  - Observation:見本條觀測

#### S-9.3 命中列去向必須是 full 或 mini 或 OC
- GIVEN 一份 Fast 4-spec,六問第 3 問答「是」,去向格空白
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN exit 1;輸出含 `去向` 或 `full` 或 `mini` 或 `OC`
- 觀測:從 exit 與輸出看 | exit 1 且點名去向算過 | 用「命中無去向」fixture 測
- Operational Context:
  - Actor:owner
  - Goal:命中不是空白開寫
  - Situation:六問已有「是」
  - Known information:三擇一
  - Missing information:這次要哪一擇
  - Human decision:裁升 full、fast+mini、或 OC 接受風險
  - Authority:owner;牙驗去向非空且 ∈ 集合
  - External dependency:無
  - Out-of-system action:寫 OC 或改 lane
  - Waiting/timeout behavior:停到去向有值
  - Recovery:填 `full` 或 `mini` 或 `OC` 後重跑
  - Audit/handoff requirement:去向與命中列同一張表
  - Observation:見本條觀測

#### S-9.4 純視覺不改語意且六問全否可維持 Fast
- GIVEN 一份 Fast 4-spec:已有 approved spec;六問皆「否」且各有一句「只改 CSS 顏色、不改等待／權限／下一步」;去向=`Fast`
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec.md>`
- THEN 六問這一項不構成 exit 1(本項綠;其他 C 項仍各自判)
- 觀測:從輸出看 | 無「六問未收束」FAIL 行算過 | 用 OC-6 純視覺 fixture 測
- Operational Context:不適用 — OC-6 收窄的綠路徑,無新交接。

### R-10: 系統 SHALL 只延伸既有三支牙且不發明第二 ID 鏈
OC-1／SC-10。機械牙只延伸 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`(及 `devflow-check` 已掛入口)。不新造 `check-discovery-gaps.sh` 當唯一入口。不發明 `RW-`／`JNY-`／`ACT-` ID。本 hop 不改 STATUS／HISTORY／模板正本、不填 G2 verdict。

**審的時候看什麼**
落地 diff 的新腳本名與正文 ID。出現第二套牙或 RW-1 = 失敗。

#### S-10.1 指定檢查入口仍是既有三支
- GIVEN 本 feat 落地後的 `scripts/` 目錄與 `scripts/devflow-check.sh`
- WHEN 搜尋新入口
- THEN 不存在被當成唯一入口的 `scripts/check-discovery-gaps.sh`;SC-1…SC-9 的指定檢查呼叫字面仍是三支既有腳本之一
- 觀測:從 `scripts/` 檔名與 6-notes／測試呼叫看 | 無該新檔當唯一入口算過 | 拿落地 tree 測
- Operational Context:不適用 — 腳本家族禁令。

#### S-10.2 過程檔與模板不出現 RW 第二鏈
- GIVEN 落地後的 `_templates/1-discussion.md`、`_templates/2-decision.md`、`_templates/4-spec.md` 與本 slug 過程檔
- WHEN 搜 `RW-\d`、`JNY-\d`、`ACT-\d`
- THEN 零命中(負向對照句「不得寫 RW-1」不算發 ID)
- 觀測:從 `rg -n 'RW-[0-9]|JNY-[0-9]|ACT-[0-9]'` 看 | 零命中算過 | 對落地模板與本目錄測
- Operational Context:不適用 — ID 鏈禁令。

## MODIFIED Requirements

living spec `docs/specs/` 本 repo 0 條可引。下列是現況活教師原文,落地後改行為(引原文,標改什麼)。

### M-1: 驗收雛形「從哪看」不再鎖通道
原條文:`_templates/1-discussion.md` 驗收雛形「從哪看:<畫面路徑 | API 端點 | log | 產出檔>」;`skills/dev-talk/nodes/S4-accept.md`「從哪裡看(畫面/端點/檔案/log)」。
改什麼:觀測三件仍要(從哪看／看到什麼算對／拿什麼試),候選改為本 repo 可執行的現象,包括討論分欄與腳本 exit;不得把畫面／API／元件寫成唯一通道。承接 R-1。

### M-2: N3 發現題不再「每題附推薦」
原條文:`skills/dev-talk/nodes/N3-probe.md`「一次只問一題、附推薦答案」。
改什麼:發現題禁推薦;裁決題才可附選項／差異／推薦。完成條件改覆蓋面(必查面已覆蓋、關鍵反例已問、證據缺口已顯性化);「連續兩輪無新問題」只當輔助訊號。承接 R-2。

### M-3: 點頭不再升格為已核事實
原條文:`skills/dev-talk/nodes/S1-survey.md`「認可後的清單 = 本次已核事實」。
改什麼:認可 = 確認理解,不是來源。高影響主張走 R-3。承接 R-3。

### M-4: realworld 牙從「有字樣」延到欄位形狀
原條文:`scripts/check-realworld.sh` 只驗章節／`[Assumption]`／「訪談」字樣。
改什麼:加驗 2A 七欄與枚舉集合、8A role／scenario、4A 三欄、5A 四欄、1A 兩節名、2A 來源 XOR 期限。射程仍是模板＋範例地板 + 本 feat 指定對照稿。填好的 4-spec 過期假設改由 `check-spec-gate.sh` 擋(R-4)。

### M-5: devtalk-guard 從只掃寫入洩漏延到事實入口
原條文:`hooks/devtalk-guard.sh` 只掃 `skills/dev-talk/*` 寫入是否洩漏下游字眼。
改什麼:讀取圍欄放行本輪 manifest 已核准路徑;仍禁 2–7。承接 R-8。

### M-6: 完整範例不再教 Goal = dashboard
原條文:`example/contract-expiry-reminder/1-discussion.md` Goals 指定登入／點擊／一眼可見;AC 鎖 dashboard;Interview Log「dashboard 是最低成本的呈現面」。
改什麼:Goals 改寫工作結果;呈現面進 Requested solution 並標未定案。承接 R-1。Q6 採用者是否照抄維持 Assumption(OC-3)。

### M-7: Fast 在進 4 前加六問
原條文:`skills/dev-flow/SKILL.md` Fast 省略 Stage 1–3,從 4-spec 起跑;高風險人機互動寫在 4-spec Verification Profile,lane 已選完。
改什麼:省略 1–3 仍合法;進 4 之前必須收束六問(R-9)。Exception「Fast 合法跳過 1–3」刻意維持。

## REMOVED Requirements

無。不刪七關、不刪 Fast lane、不刪 attestation、不刪既有三支腳本。

## 行為流程圖(R 級)

```
[R-1] 結果與構想分欄
  Goals 只寫工作結果
  構想進 Requested solution
[R-2] 發現題不附推薦
  發現｜禁推薦
  裁決｜可附選項
[R-3] 高影響主張帶枚舉
  來源 XOR 期限
  點頭不是來源
[R-4] 拒絕過期假設送 G2
  spec-gate exit 1
  OC 接受可過
[R-5] 要求 verdict 角色場景
  role 與 scenario 同行
  只寫姓名日期不完整
[R-6] 留下 disposition 去向
  引用原文三欄
  本方案處理有 R/S
[R-7] Exit 留下回看四欄
  四個欄位名都在
  結果走 HISTORY
[R-8] 放行核准事實路徑
  未核不得當授權
  2-7 仍禁
[R-9] Fast 進 4 前收束六問
  空白不是已分診
  等待誤標必命中
[R-10] 只延伸既有三支牙
  不新造檢查家族
  不發明 RW-id
```

## Acceptance Criteria

- 全部 S 綠(S-1.1～S-10.2)。
- 既有測試全綠:`devflow-check` 回歸,含現況 `check-realworld.sh`／`check-spec-gate.sh` 舊項不因本 feat 誤殺。
- 非功能:指定檢查對單份 md 在本機同步跑完;不新增網路 capability;不 bump plugin。
- 行為不變類(R-10／M-7 Fast 仍可省略 1–3):golden master — 同一份純視覺 Fast 對照,六問全否仍走 Fast;七關節名不改。

## Out of Scope

- 1B／1C／2B／2C／3B／3C／4B／4C／5B／5C／6B／6C／7B／7C／8B／8C(2-decision 已拒)。
- 新造檢查家族、`check-discovery-gaps.sh` 當唯一入口。
- RW-id／Journey／Actor 第二鏈。
- 永久 `lookback.md`。
- Actor Coverage 全表。
- 拆成九個 slug。
- dashboard／API 詞黑名單。
- 本 hop 改 `_templates/`／`skills/`／`example/`／守衛正本(契約在本檔;碼在 Stage 6)。
- 本 hop 改 `STATUS.md`／`HISTORY.md`。
- 本 hop 發明 G2／G3 PASS、代填 4-spec `verdict`。
- 重開九條 DO／LIGHT、重開 1A–8A、重開 OC-1…OC-6。
- 假現場訪談收 Q6。
- Windows 真機驗證。

### Stage 3 對帳

Human verdict: ACCEPTED | role=owner | scenario=AC-1–AC-9。attestation:`human:rick @ 2026-09-13`(owner brief;平行 PR #274)。2-decision 無「跳過 Stage 3」OC。選定 Variant A。無 REVISE 場景。

- 3-prototype「Scenario AC-1」→ S-1.1、S-1.2、S-1.3(M-1／M-6)
- 3-prototype「Scenario AC-2」→ S-2.1、S-2.2、S-2.3(M-2)
- 3-prototype「Scenario AC-3」→ S-3.1、S-3.2、S-3.3(M-3／M-4)
- 3-prototype「Scenario AC-4」→ S-4.1、S-4.2
- 3-prototype「Scenario AC-5」→ S-5.1、S-5.2
- 3-prototype「Scenario AC-6」→ S-6.1、S-6.2、S-6.3
- 3-prototype「Scenario AC-7」→ S-7.1、S-7.2、S-7.3
- 3-prototype「Scenario AC-8」→ S-8.1、S-8.2、S-8.3(M-5)
- 3-prototype「Scenario AC-9」→ S-9.1、S-9.2、S-9.3、S-9.4(M-7)
- Method 走查「壞卡／空白六問／無去向」→ S-3.2、S-6.3、S-9.1
- Operational Context Recovery(搬節、補來源、OC-accept、等核准、填去向)→ 各相關 S 的 Recovery 欄

## Diff Budget

整節是估計,不是承諾。[Assumption]

| 區塊 | 檔(估) | 非測試行(估) | 測試／fixture 行(估) |
|---|---|---|---|
| `_templates/` 1／2／3／4／7-review | ≤5 | ≤180 | 0(模板本身) |
| `skills/dev-talk/` + `skills/dev-flow/SKILL.md` + 指南句 | ≤6 | ≤120 | 0 |
| `scripts/check-realworld.sh` + `check-spec-gate.sh` | ≤2 | ≤220 | ≤500(對照稿) |
| `hooks/devtalk-guard.sh` | ≤1 | ≤80 | ≤120 |
| `example/contract-expiry-reminder/` | ≤2 | ≤80 | 0 |
| 本 slug 過程檔(本 hop 只 4-spec) | ≤2 | 本 hop 已寫 | 0 |
| **合計** | **≤20 檔** | **≤700 行** | **≤650 行** |

超支本身非偏差,是停下判 L1/L2 的訊號;分不清一律當 L2。本 hop 實際落地檔 = `4-spec.md` + `4-spec.html` 兩份。

## Dependencies

- `scripts/check-realworld.sh` —— justification:SC-1／2／3／5／6 地板／7 的指定檢查家族;已掛 `devflow-check`。
- `scripts/check-spec-gate.sh` —— justification:SC-4／SC-6 下落／SC-9 的 G2 擋點;已是 Gate。
- `hooks/devtalk-guard.sh` —— justification:SC-8 改允許集合;已是討論圍欄。
- `scripts/devflow-check.sh` —— justification:三支牙已掛的回歸入口,不另造。
- `scripts/history-append.sh` —— justification:5A 結果寫入口,不新造 lookback 檔。
- `scripts/build-stage4-html.py` —— justification:本 hop 審頁;不改該腳本。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組(模板／skill／範例／三支牙);③修改跨模組 Interface(realworld 欄位、spec-gate 過期項、devtalk 讀取允許集合);⑨Feature Risk = high;⑩三個以上模組共同參與
- Design source: 既有 pattern —— `check-realworld.sh` 模板地板、`check-spec-gate.sh` G2 Gate、`devtalk-guard.sh` 圍欄;欄位字面是 Decision + Stage 3 Variant A 留給本檔的 local lock

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| `check-realworld.sh` | 模板＋範例＋指定對照稿的欄位地板 | **擁有**地板通過／失敗 | → `_templates/`、`example/`、對照 fixture | 不得當填好 4-spec 的過期-Assumption Gate(那是 spec-gate);不得新開家族 |
| `check-spec-gate.sh` | 填好的 4-spec:過期假設、Fast 六問、本方案處理下落 | **擁有** G2 形狀拒絕 | → 該份 4-spec.md、同 slug 2-decision disposition | 不得改 C1–C6 舊語意當誤殺;不得另造 `check-discovery-gaps.sh` |
| `devtalk-guard.sh` | 討論讀寫圍欄:放行核准事實路徑、擋 2–7 | **擁有**擋／放行 | → 本輪 `## Evidence manifest` | 不得放寬整個 `docs/`／`notes/`;不得把 ticket 解法當事實 |
| 活教師(模板／N3／範例) | 人會抄的分欄、前綴、表頭 | 各檔擁有自己的字面 | → 本檔 R/S 字面 | 不得發明 RW-id;不得在 Goals 鎖通道 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| realworld 地板 | in:模板／範例／對照稿;out:exit 0／≠ 0 | 錯欄／缺欄／殘行 → ≠ 0 | 只讀,不寫 feature 檔 | 舊 MIN_CHECKS 項仍在;只加新項 |
| spec-gate 過期／六問 | in:一份 4-spec;out:exit 0／1 | 過期未結案或六問未收束 → 1 | 只讀 | C1–C6 舊項相容;本 feat 加項 |
| devtalk 讀取 | in:路徑 + manifest;out:放行或擋 | 方案檔／未核 → 擋 | 不改方案檔 | 舊寫入洩漏掃描仍在 |
| disposition／lookback 字面 | in:2-decision／7-review 正文;out:欄在或不在 | 空白去向／缺回看欄 → ≠ 0 | 人寫表,腳本不填 | 五態去向集合鎖定 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 高影響表解析 | 認七欄與枚舉集合 | ← 1-discussion | md 表 → 列 → XOR | 缺列形狀紅 | S-3.1／S-3.2 fixture |
| Cited Assumptions 解析 | 認期限與結案 | ← 4-spec | Stage N 過期? → OC-accept? | 過期未結案紅 | S-4.1／S-4.2 |
| 六問解析 | 認六答與去向 | ← Fast 4-spec | 空白? 命中? 去向 ∈ 集合? | 未收束紅 | S-9.1～S-9.4 |
| manifest 允許集合 | 核准路徑 ∪ 舊三類,減 2–7 | ← 1-discussion、devtalk-guard | 核准=是才放行 | 未核／方案檔擋 | S-8.1～S-8.3 |

### Design Constraints
- 必須:沿用三支既有牙;Variant A 同檔就地欄;節名 `## Goals`／`## Requested solution`;前綴 `發現｜`／`裁決｜`;去向五態;lookback 四欄字面;verdict `role=`／`scenario=`;本 hop 不改模板正本。
- 禁止:第二套檢查家族;RW-id;lookback 永久檔;Actor Coverage 全表;dashboard／API 黑名單;本 hop 改 STATUS／HISTORY;本 hop 填 G2 PASS;捏造現場 log。
- Extension point:Stage 6 才改模板／守衛／範例;Stage 7 才填本包自己的 lookback 四欄。
- Known design limit:
  ① 牙只驗形狀(欄在、枚舉 ∈ 集合、XOR、去向非空)。語意與「這條算不算高影響」仍是人判(DD-1 給抽樣規則,腳本認表列)。
  ② A-2 誘導無法從最終 md 還原整場對話;靜態牙只防前綴被刪。
  ③ 擋不住「錯的人寫對的 role 字」。
  ④ Q6 採用現場是否照抄無 log;本 repo 範例教師 = Observed,現場 = Assumption(OC-3)。
  ⑤ 本 hop 不產生落地碼;S 的 fixture 在 Stage 6 才進 `scripts/fixtures/`。

## Verification Profile(G2 一併審)

- lane: full(判準:新能力、改公開檢查契約、高風險人機互動、權限／資料隔離(事實入口)。owner 已 lock full;無偏離)
- Risk: high(判準:公開檢查 exit 契約 + 讀取權限允許集合 + 訪談錨定／等待誤標。模板「公開 API／不可逆契約副作用／高風險人機互動」吃這條)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得把構想寫進 Goals 當目標(S-1.2)
  - 不得讓發現題硬性附推薦(S-2.1)
  - 不得把點頭當唯一來源(S-3.3)
  - 不得讓過期未結案高影響 Assumption 送進 G2(S-4.1)
  - 不得只寫 ACCEPTED + 姓名日期當完整 verdict(S-5.2)
  - 不得讓「本方案處理」列無 R/S 下落(S-6.2)
  - 不得另造 `lookback.md`(S-7.3)
  - 不得放行未核路徑或 2–7 方案檔(S-8.2／S-8.3)
  - 不得把空白六問當已分診,或讓等待誤標全打「否」(S-9.1／S-9.2)
  - 不得新造 `check-discovery-gaps.sh` 當唯一入口,不得發 RW-id(S-10.1／S-10.2)
  - 不得在本 hop 改 STATUS／HISTORY／模板正本、不得代填 G2 PASS
- Required layers:check-spec-gate／check-realworld／devflow-check
- Conditional layers:devtalk-guard 讀取圍欄 — 當實作改到 `hooks/devtalk-guard.sh` 或 skill 白名單時必跑 S-8.1～S-8.3
- Explicitly excluded layers:Mutation(本 hop 只規格)、e2e／Playwright(無產品前端)、Race／stress(單檔字面檢查,無新併發契約)、Windows 真機(Out of Scope)
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && bash scripts/check-realworld.sh && bash scripts/devflow-check.sh`
- Reliability triage:
  - Concurrency: n-a — 單一作者寫一份 md;檢查只讀;無多 writer 契約
  - Idempotency: applicable — 同一份 fixture 再跑指定檢查,exit 與字樣相同(S-1.2／S-4.1／S-9.1)
  - Timeout/retry: n-a — 本機檔案;檢查同步結束,不自動重試

本 slug lane=full,已走 Stage 1–3。R-9 的六問 Gate 對**本檔**不適用(不是 Fast 4-spec)。Human verdict(Stage 3 Demo):ACCEPTED | role=owner | scenario=AC-1–AC-9;`human:rick @ 2026-09-13`。這是 Demo 條件,不是本檔 G2 PASS。

### Failure Model(Risk: high 必填)

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| Goals 仍教 dashboard | 下一場討論複製通道鎖 | 範例 Goals 仍含登入／點擊當目標 | Required:S-1.3 | — |
| 發現題仍附推薦 | 受訪者被錨定 | N3 仍寫「附推薦答案」當硬規則 | Required:S-2.1 | — |
| 點頭當事實 | 假 Observed 進 Decision | 來源格只有「點頭」卻綠 | Required:S-3.3 | — |
| 過期假設仍進 G2 | 假前提上的測試全綠 | spec-gate 對 S-4.1 卡 exit 0 | Required:S-4.1 | — |
| verdict 只證明有人按過 | 後讀者不知驗了誰 | 殘行仍綠 | Required:S-5.2 | — |
| 痛點靜默消失 | Journey 列無下落 | 本方案處理無片段 | Required:S-6.2 | — |
| 出貨無回看 | 問題沒改善仍 shipped | Exit 缺四欄 | Required:S-7.2 | — |
| 規定了但讀不到 | B-1 假規則 | 核准路徑仍擋、或 2-decision 放行 | Required:S-8.1／S-8.2 | — |
| Fast 六問在 lane 選完後才填 | 等待誤標晚露 | 空白表 exit 0 | Required:S-9.1／S-9.2 | — |
| 另造第二套牙 | 兩套方法論 | 出現 `check-discovery-gaps.sh` 當唯一入口 | Required:S-10.1 | — |
| 錯的人寫對的 role 字 | 代表性假通過 | 字面齊、人不是該角色 | Known limit ③ | 本包 LIGHT,不驗身份 |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 1A–8A、不翻 OC-1…OC-6。狀態待人審(G2 才裁決;本 hop 不代填 PASS)。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 高影響抽樣=命中任一即高影響:(H1) Journey 痛點格／Workaround 條／Exception 條;(H2) `[Assumption]` 或 `[~]` 且影響級=`高`;(H3) 被 Stage 2 Decision／OC／DD 當依據。機器只認已列表列,不掃每一句 Context | OC-5 禁止每句都貼;腳本要看得見列 | `2-decision.md` OC-5;`3-prototype.md` 2A「只要求高影響列」 | 改成每句枚舉 = 字樣儀式;改成純人判則 SC-3 牙落空 | 待人審 |
| DD-2 | 2A 表頭鎖定:`主張(原文片段)`／`狀態`／`來源類型`／`as-of`／`角色或範圍`／`支持哪一段`／`限制`。狀態集合={Observed, Reported, Inferred, Assumption, Conflict} | Stage 3 Variant A 好卡 | `3-prototype.md` Method 2A 表 | 改欄名則 S-3.1 fixture 全改 | 待人審 |
| DD-3 | Assumption 四欄鎖定:`假設`／`若為假影響什麼`／`影響級`／`怎麼驗`／`何時／由誰驗`。期限機器形:`期限=YYYY-MM-DD` 或 `期限=Stage N`。4-spec 引用形= `## Cited Assumptions` 表:`引用片段`／`狀態`／`期限`／`結案`;結案 ∈ {Observed, Reported, OC-accept, —}。`期限=Stage N` 且檔是 4-spec 且 N∈{1,2,3} ⇒ 過期 | 3A 要人看得見的 G2 拒絕;Stage 1 已用「期限=Stage 2」 | `3-prototype.md` 3A;`1-discussion.md` Q6 | 改只認日曆日期則本 slug Q6 形狀要重寫 | 待人審 |
| DD-4 | disposition 表頭鎖定:`引用(Stage 1 原文片段)`／`去向`／`理由`。去向集合五態見 R-6。引用=原文片段,長度至少一個 Journey／Workaround／Exception 名詞(例如 `痛點消失`) | 4A;禁 RW-id | `2-decision.md` Real-world Disposition;`3-prototype.md` 4A | 改 RW-id = 採 4B,已拒 | 待人審 |
| DD-5 | evidence manifest 節名鎖定 `## Evidence manifest`,住 `1-discussion.md` 同檔,不另造 `evidence-manifest.md`。表頭:`想找哪類`／`為什麼`／`擬路徑或來源`／`owner 核准`／`已讀`。核准格機器值:`是`／`未核`／`禁` | Variant A;拒 B 另造檔 | `3-prototype.md` 6A;`2-decision.md` 5A 已拒永久檔 | 改另檔 = 採 Variant B,已棄 | 待人審 |
| DD-6 | Fast 六問節名鎖定 `## Fast six questions`,必須出現在該 Fast 4-spec 的 ADDED Requirements **之前**。六問字面見 R-9。去向機器值:`Fast`／`full`／`mini`／`OC` | 7A;lane 選定前 | `3-prototype.md` 7A;`2-decision.md` OC-6 | 改寫進 Verification Profile = 重演晚露 | 待人審 |
| DD-7 | lookback 四欄字面鎖定:`回看日期:`／`回看 owner:`／`資料來源:`／`低於何值重開:`,住 7-review Exit Checklist | 5A | `3-prototype.md` 5A;`2-decision.md` 決策點 5 | 改 HISTORY-only = 採 5B,已拒 | 待人審 |
| DD-8 | Human verdict 一行鎖定:`<ENUM> \| role=<Actors 表角色> \| scenario=<AC-id>`。ENUM 仍是 ACCEPTED／REVISE／NOT_REVIEWED。attestation 行不變 | 8A LIGHT | `3-prototype.md` 8A;`1-discussion.md` AC-5 | 改全表 = 採 8B,已拒 | 待人審 |
| DD-9 | Feature Risk = high;本 hop 頂欄 `verdict` 留空,`status` draft。Demo ACCEPTED ≠ G2 PASS | 公開檢查契約 + 四眼原則;brief「No fake G2」 | `_templates/4-spec.md` Risk 判準;本 hop brief | 改 normal 則 Failure Model 改選配;代填 PASS = 假綠 | 待人審 |
| DD-10 | 「從哪看」候選不再唯一鎖畫面／端點;本 repo 可執行的現象(討論分欄、腳本 exit、檔、log)都算。禁止把 dashboard／API 做成詞黑名單 | A-1 已拒誤殺領域詞;SC-1 要分欄不是禁詞 | `2-decision.md` Rejected「dashboard／API 黑名單」;`1-discussion.md` AC-1 | 改黑名單會誤殺合法領域詞 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 指定檢查入口字面:`bash scripts/check-realworld.sh`、`bash scripts/check-spec-gate.sh <4-spec.md>`、`hooks/devtalk-guard.sh`。不在本 hop 發明新 CLI 名。
- spec-gate 新項加在 C1–C6 之後,不改舊六項語意。
- 審頁用 `scripts/build-stage4-html.py --action`;不手包 html-shell,不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `docs/dev/STATUS.md` 正本表列。
- 本 hop 不落地 Stage 6 守衛碼;形狀以 R/S 為準。
- 本 slug 自己的 Fast 六問:N/A(lane=full,已走 1–3)。

## Cited Assumptions

| 引用片段 | 狀態 | 期限 | 結案 |
|---|---|---|---|
| Q6 採用現場仍把解法寫進 Goal | Assumption | Stage 2 | OC-accept |
| 現場發現題仍附推薦 | Assumption | Stage 2 | OC-accept |
| Fast 現場因檔數少漏判互動 | Assumption | Stage 2 | OC-accept |

依據:OC-3(`2-decision.md` Owner Calls)。本 repo 範例教師 = Observed;採用現場照抄 = 仍 Assumption。不捏造現場 log。

## Real-world Disposition(本 slug Stage 1 → 本檔)

| 引用(Stage 1 原文片段) | 去向 | Stage 4 下落 |
|---|---|---|
| Journey「發現被錨定」 | 本方案處理 | R-2／S-2.1 |
| Journey「點頭當證據」 | 本方案處理 | R-3／S-3.3 |
| Journey「痛點消失」 | 本方案處理 | R-6／S-6.2 |
| Journey「問題沒改善」 | 本方案處理 | R-7／S-7.1 |
| Journey「互動風險晚露」 | 本方案處理 | R-9／S-9.1 |
| Workaround「owner 用審核筆記記缺口」 | 本方案處理 | 本 slug R-1…R-10 取代筆記 |
| Workaround「現場證據靠記憶轉述」 | 本方案處理 | R-8／S-8.1 |
| Workaround「Fast 直接寫 4-spec」 | 本方案處理 | R-9;全否且不改語意仍可 Fast(S-9.4) |
| Workaround「人口頭記先問現況」 | 本方案處理 | R-2／S-2.1 |
| Exception「Fast 合法跳過 1–3」 | 刻意維持 | M-7;只加進 4 前六問 |
| Exception「A-5 只 LIGHT」 | 刻意維持 | R-5;不做全表 |
| Exception「`[~]` 可走到 G2」 | 本方案處理 | R-4／S-4.1 |
| Exception／Q6「採用現場仍把解法寫進 Goal」 | 仍待驗 | Cited Assumptions + OC-3;Known limit ④ |
| Exception「現場發現題仍附推薦」 | 仍待驗 | 同上 |
| Exception「Fast 因檔數少漏判互動」 | 仍待驗 | 同上 |

## Test Skeletons(選配)

- `test_s_1_1_template_has_goals_and_requested_solution`
- `test_s_1_2_dashboard_in_goals_fails`
- `test_s_1_3_example_goals_drop_login_click`
- `test_s_2_1_n3_drops_recommend_on_discover`
- `test_s_2_2_decide_prefix_may_offer_options`
- `test_s_2_3_missing_one_prefix_fails`
- `test_s_3_1_seven_column_observed_passes`
- `test_s_3_2_user_said_dashboard_fails`
- `test_s_3_3_nod_is_not_a_source`
- `test_s_4_1_expired_unresolved_assumption_fails_spec_gate`
- `test_s_4_2_oc_accept_passes_spec_gate`
- `test_s_5_1_verdict_line_has_role_and_scenario`
- `test_s_5_2_accepted_name_date_only_fails`
- `test_s_6_1_disposition_headers_in_template`
- `test_s_6_2_handled_row_has_rs`
- `test_s_6_3_blank_dest_or_rw_id_fails`
- `test_s_7_1_exit_has_four_lookback_fields`
- `test_s_7_2_missing_lookback_field_fails`
- `test_s_7_3_no_lookback_md_file`
- `test_s_8_1_approved_fact_path_readable`
- `test_s_8_2_decision_and_spec_still_blocked`
- `test_s_8_3_unapproved_or_ticket_solution_not_fact`
- `test_s_9_1_blank_six_questions_fails`
- `test_s_9_2_wait_shown_as_done_hits_q3`
- `test_s_9_3_hit_without_disposition_fails`
- `test_s_9_4_visual_only_all_no_stays_fast`
- `test_s_10_1_no_new_check_family`
- `test_s_10_2_no_rw_id_chain`

## 確認紀錄

- 雙源清點 | 2026-09-13 | 驗收雛形 AC-1…AC-9 共 9 條;2-decision SC-1…SC-10 共 10 條;living spec `docs/specs/` 0 條可引 → 行為 ADDED R-1…R-10;活教師七句進 MODIFIED M-1…M-7
- 前站核對 | 2026-09-13 | 2-decision `status=approved`、`verdict` PASS、OC-1…OC-6 ✅(#268)。Stage 3 Human ACCEPTED | role=owner | scenario=AC-1–AC-9;`human:rick @ 2026-09-13`(brief;平行 #274)。本 hop 不改 3-prototype.md
- R 範圍 | 2026-09-13 | Implementer B 依 brief「landing nine gaps per Decision 1A–8A」編碼 R-1…R-9 對 SC-1…SC-9,R-10 對 OC-1／SC-10
- S 展開 | 2026-09-13 | R-1…R-10 全展開;每 S 有觀測欄;交接／核准／等待／權限的 S 有 Operational Context
- 3a 四節 | 2026-09-13 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-13 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-13 | AC-1…AC-9 逐場有 R/S 下落;Recovery 欄有下落
- DD 掃描 | 2026-09-13 | 上層十條待人審;DD 節無未決標記;不翻已核 Decision;未定事項三詞全文零命中
- G2 | 2026-09-13 | **不送、不發明 PASS**。頂欄 `verdict` 空、`status` draft。形狀可跑 `check-spec-gate.sh`(現況 C1–C6;過期／六問項尚未落地,本檔 Cited Assumptions 已預留 OC-accept)
