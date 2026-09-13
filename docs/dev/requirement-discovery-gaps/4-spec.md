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

> 基準:main tip `9eddf22`（#274 Stage3 Human ACCEPTED 已合）。契約不 bump。本 hop **只寫 Stage 4**，不改 `_templates/`／`skills/`／`example/`／守衛正本、不 bump plugin、不改 `STATUS.md`／`HISTORY.md`、不開 Stage 5、不發版。
> Decision 正本:`docs/dev/requirement-discovery-gaps/2-decision.md`（1A+2A+3A+4A+5A+6A+7A+8A；OC-1～OC-6 ✅；G1 `verdict` PASS）。Stage 3 Variant A 同檔就地欄；`3-prototype.md` `status: approved`，`Human verdict: ACCEPTED | role=owner | scenario=AC-1–AC-9`，attestation `human:rick @ 2026-09-13`。
> Demo 前置已滿足（#274）。本 hop **不發明 G2 PASS**。4-spec 頂欄 `verdict` 留空、`status` draft，等人審。
> 九條 ID 各一條 R：A-1→R-1 … A-7→R-7、B-1→R-8、B-2→R-9。Goals 只寫結果；欄位／前綴／牙是觀測面，不是目標本身。
> 本檔 R/S 是 Stage 6 要落地的契約。本 PR 不改活教師正本。

## 補助模組生命週期（預覽）

主詞是「需求發現九缺口的欄位與牙」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：`## Requested solution`、`發現｜`／`裁決｜`、高影響主張枚舉欄、Assumption 四欄與 `## Assumption refs`、disposition 三欄、Exit 回看四欄、`## Evidence manifest`、Fast 六問表、verdict `role=`／`scenario=`
- 改行為（相關一格）：`check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh` 射程延到上列形狀；N3-probe／S4-accept／S1-survey；2-decision 接手與 4-spec 對帳；7-review Exit；Fast 進 4 前分診；example 同期改口
- 退役：沒有
- 不動：七關編號、第二條 Journey／Actor／RW ID 鏈、A-5 Actor Coverage 全表、新造檢查家族、STATUS／HISTORY 寫入口、圍欄仍禁 2–7 方案檔、九條 DO／LIGHT

## ADDED Requirements

### R-1: 系統 SHALL 讓人讀 Stage 1 時能分辨工作結果與解法構想
A-1／1A／SC-1。結果住 `## Goals`；構想住 `## Requested solution` 並標未定案。Goals 句不把畫面／API／元件寫成目標本身。不採 dashboard／API 黑名單（已拒）；靠分欄形狀 + G1 抽查。本檔自己先照做：R 標題寫人要分辨的結果，不把「加一個標題」當成目標。

**審的時候看什麼**
打開模板與範例的 Goals 節。結果句不鎖通道；「我要 dashboard」只能在 Requested solution。對照稿必須被指出「構想在錯欄」。

#### S-1.1 模板必須分欄且 Goals 指令不再鎖通道
- GIVEN tip `_templates/1-discussion.md` 現況：L75–L76 只有 `## Goals`（「想達成」），沒有 `## Requested solution`；L91–L96 驗收雛形「從哪看」候選寫成 `畫面路徑 | API 端點 | log | 產出檔`；`skills/dev-talk/nodes/S4-accept.md:19-22` 問「從哪裡看(畫面/端點/檔案/log)」
- WHEN Stage 6 依本 R 改完這三處（本 hop 不改正本）並讀改後檔
- THEN `_templates/1-discussion.md` 含字面 `## Goals` 與 `## Requested solution`；Goals 指令不再要求候選畫面／API／元件通道；L96 那行不再把 `畫面路徑 | API 端點` 寫成必填候選；S4-accept 改問「從哪裡看出結果發生」，不把畫面／端點／元件當成 Goal 本身
- 觀測:從這三檔改後原文看 | 兩節名都在、Goals／S4-accept 不再要求通道候選算過 | 用 tip 三檔當負向、改後三檔當正向測
- Operational Context:不適用 — 模板字面，無現場人員交接。

#### S-1.2 「我要 dashboard」寫進 Goals 的對照稿必須被指出錯欄
- GIVEN 一份 Stage 1 對照稿：`## Goals` 第一句字面為「我要 dashboard」，`## Requested solution` 缺或空
- WHEN 跑本 feat 掛進 `check-realworld.sh` 的指定形狀檢查（同一入口，不另開 `check-discovery-gaps.sh`；對照稿可放 `scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md`）
- THEN exit ≠ 0；stdout 或 stderr 含 `構想在錯欄` 或 `Requested solution`
- 觀測:從該檢查的 exit 與 stderr 看 | exit ≠ 0 且含指定字樣算過 | 用上列 fixture 測
- Operational Context:
  - Actor:G1 reviewer
  - Goal:構想不能混成目標
  - Situation:採用者把「我要 dashboard」寫進 Goals
  - Known information:節名契約 `## Goals`／`## Requested solution`
  - Missing information:該 dashboard 是否只是構想
  - Human decision:把構想搬到 Requested solution，或退回 Stage 1
  - Authority:形狀檢查擋錯欄；G1 抽查語意
  - External dependency:無
  - Out-of-system action:在終端機跑指定檢查
  - Waiting/timeout behavior:檢查同步結束
  - Recovery:把該句搬到 `## Requested solution` 並標未定案後重跑
  - Audit/handoff requirement:stderr 留「構想在錯欄」
  - Observation:見本條觀測

#### S-1.3 完整範例 Goals 不得再把登入／點擊／一眼可見當成目標本身
- GIVEN tip `example/contract-expiry-reminder/1-discussion.md:62-65` Goals 寫「業務登入後…就能看到」「點擊可直達」「一眼可見的目前狀態」；L83–L103 AC 鎖 dashboard／卡片／URL；L119 Interview 結「dashboard 是最低成本的呈現面」
- WHEN Stage 6 同期改口（1A／Q14，同一 slug）
- THEN 該檔 `## Goals` 三句不再把登入／點擊／一眼可見寫成目標本身；若仍要提 dashboard／卡片／URL，只出現在 `## Requested solution` 且標未定案；L119 不得再當已核目標
- 觀測:從改後 example 1-discussion 的 Goals／Requested solution／Interview Log 看 | Goals 無通道目標、構想另欄算過 | 用 tip L62–L65／L119 當負向、改後檔當正向測
- Operational Context:
  - Actor:採用者（會抄 example）
  - Goal:抄範例時寫結果，不抄「Goal = dashboard」
  - Situation:打開完整範例當樣張
  - Known information:本 R 分欄契約
  - Missing information:範例是否已改口
  - Human decision:以改口後範例為抄本
  - Authority:example 是活教師
  - External dependency:無
  - Out-of-system action:人打開 example
  - Waiting/timeout behavior:無
  - Recovery:若 Goals 仍鎖通道，同一 T 改到符合 THEN
  - Audit/handoff requirement:Requested solution 標未定案
  - Observation:見本條觀測

#### S-1.4 合法領域詞出現在結果句不得只因含 dashboard／API 就紅
- GIVEN 一份 Stage 1：`## Goals` 寫「讓負責業務在合約到期前做完續約決定」；`## Requested solution` 寫「未定案：站內 dashboard」；正文他處可出現 API／dashboard 當領域詞
- WHEN 跑 S-1.2 同一支指定檢查
- THEN exit 0；輸出不得只因出現 `dashboard` 或 `API` 就含 `構想在錯欄`
- 觀測:從 exit 與是否誤殺領域詞看 | exit 0 且無錯欄字樣算過 | 用 `scripts/fixtures/discovery-gaps/goals-outcome-with-requested-dashboard.md` 測
- Operational Context:不適用 — 與 S-1.2 同一檢查；本條只驗「不採黑名單」。

### R-2: 系統 SHALL 在蒐集上次真實做法時不先塞推薦答案
A-2／1A／SC-2。發現題（現況／案例／例外／證據）問句前綴字面 `發現｜`，禁附推薦答案。裁決題（已核事實上的取捨）前綴字面 `裁決｜`，可附選項／差異／推薦。不要求從最終 1-discussion 還原整場對話。刪掉其中一邊對稱句 → 靜態牙紅。完成條件改覆蓋面；「連續兩輪無新問題」只當輔助訊號。

**審的時候看什麼**
只看問句本身。有 `發現｜` 的問句不得附推薦。刪掉 `發現｜` 或 `裁決｜` 其中一邊，指定檢查必須紅。

#### S-2.1 發現題路徑不得再把附推薦當硬規則
- GIVEN tip `skills/dev-talk/nodes/N3-probe.md:22-23` 寫「一次只問一題、附推薦答案」；L41 完成條件「連續兩輪無新問題」
- WHEN Stage 6 改 N3-probe（及指南對稱句）
- THEN 發現題路徑不再把「附推薦答案」當硬規則；該節含字面 `發現｜` 與「禁附推薦」；裁決題路徑含字面 `裁決｜` 且可附選項／差異／推薦；完成條件改為必查面已覆蓋、關鍵反例已問、證據缺口已顯性化；「連續兩輪無新問題」只標輔助
- 觀測:從改後 N3-probe 與指南對稱句看 | 發現禁推薦、裁決可附、兩輪降為輔助算過 | 用 tip L22–L23／L41 當負向測
- Operational Context:
  - Actor:訪談對象／討論 agent
  - Goal:被問「上次真的怎麼做」時不被錨定
  - Situation:N3 正在蒐集現況
  - Known information:題型前綴 `發現｜`／`裁決｜`
  - Missing information:受訪者上次真實做法
  - Human decision:答開放題；不從推薦裡挑一個
  - Authority:skill 硬規則；靜態牙守對稱句
  - External dependency:口頭／Email 訪談
  - Out-of-system action:人回答現況
  - Waiting/timeout behavior:一題一答；不等推薦清單
  - Recovery:若問句已附推薦，重寫為 `發現｜` 開放題再問
  - Audit/handoff requirement:Interview Log 高影響發現題由 Stage 1 自檢抽查
  - Observation:見本條觀測

#### S-2.2 刪掉發現或裁決其中一邊前綴指令必須紅
- GIVEN Stage 6 已落地的 `skills/dev-talk/nodes/N3-probe.md`（或同等發現／裁決節點）與指南對稱句，兩邊都有 `發現｜` 與 `裁決｜`
- WHEN 對隔離複本刪掉其中一邊字面（只留 `發現｜` 或只留 `裁決｜`）再跑 `check-realworld.sh`（同一入口）
- THEN exit ≠ 0；輸出含 `發現｜` 或 `裁決｜`（指出缺的那一邊）
- 觀測:從該檢查 exit 與缺邊字樣看 | 單邊缺失必紅算過 | 用隔離複本突變測
- Operational Context:不適用 — 靜態對稱牙，無現場交接。

#### S-2.3 裁決題附選項不得被當成發現題違規
- GIVEN 一份 Interview Log：`發現｜上次真的怎麼做？`（無推薦）；下一題 `裁決｜這條痛點進本方案還是 Non-Goal？` 附「本方案／Non-Goal／另開 slug」三選
- WHEN 跑 S-2.2 同一支靜態牙（對填好的討論稿只抽前綴與「發現題附推薦」形；不還原整場對話）
- THEN 不得因裁決題附選項而 exit ≠ 0
- 觀測:從該稿跑檢查的 exit 看 | 裁決附選仍綠、發現附推薦才紅算過 | 用 `scripts/fixtures/discovery-gaps/probe-decision-with-options.md` 測
- Operational Context:不適用 — 與 S-2.2 同一牙；本條只驗裁決題可附選。

### R-3: 系統 SHALL 讓高影響主張回到可重開來源或 Assumption 加期限
A-3／2A／OC-5／SC-3。高影響列就地標狀態 ∈ {Observed, Reported, Inferred, Assumption, Conflict}。Evidence 最小欄：來源類型、as-of、角色或範圍、支持哪一段、限制。來源 XOR Assumption+期限。點頭紀錄不得當唯一來源。只要求高影響列（OC-5），不要求每一句 Context 都貼枚舉。

**高影響列**（本檔鎖定，供牙抽樣）：列在 Real-world Context 的 Workarounds 或 Exceptions；或 Current Journey「痛點」欄非空；或該列含 `[Assumption]`／Open Questions `[~]` 且同行寫「風險=高」或「影響級」為高；或 Interview Log 該 Q 前有 ⚠️。已核 `path:L` 事實句若無「風險=高」，不要求枚舉。

**審的時候看什麼**
沿一條高影響主張往回走。要嘛碰到可重開來源，要嘛碰到 Assumption+期限。只有「使用者點頭」不得當來源。

#### S-3.1 高影響主張缺來源且缺期限必須紅
- GIVEN 一份 1-discussion 高影響列（Journey 痛點或 Exceptions）：無狀態枚舉、無來源類型、無 Assumption 期限；或只寫「使用者反映」
- WHEN 跑本 feat 掛進 `check-realworld.sh` 的高影響主張形狀檢查（同一入口）
- THEN exit ≠ 0；輸出含 `來源` 或 `Assumption` 或 `期限`
- 觀測:從 exit 與字樣看 | 缺來源且缺期限必紅算過 | 用 Stage 3 壞卡「使用者反映希望 dashboard」同形 fixture 測
- Operational Context:不適用 — 填檔形狀，無新交接。

#### S-3.2 有可重開來源或有 Assumption 加期限必須綠
- GIVEN 兩份對照：①狀態=Observed、來源類型=本 tree skill、as-of=2026-09-13、角色或範圍=討論 agent、支持哪一段=1-discussion Context N3、限制=無採用現場逐字稿；②狀態=Assumption、期限=Stage 2、四欄齊（見 R-4）
- WHEN 跑 S-3.1 同一支檢查
- THEN 兩份都 exit 0
- 觀測:從兩份 exit 看 | 有來源或有期限都綠算過 | 用 Stage 3 好卡「發現被錨定」與 Q6 四欄同形測
- Operational Context:不適用 — 正向形狀。

#### S-3.3 點頭紀錄不得當唯一來源
- GIVEN 一份高影響列：狀態=Observed，來源類型或來源欄只寫「使用者點頭」或「認可後清單」，沒有可重開 path 或訪談逐字稿位置
- WHEN 跑 S-3.1 同一支檢查
- THEN exit ≠ 0；輸出含 `點頭` 或 `不是來源` 或同等「點頭不得當來源」
- 觀測:從 exit 與字樣看 | 點頭獨源必紅算過 | 用 `scripts/fixtures/discovery-gaps/nod-as-only-source.md` 測
- Operational Context:
  - Actor:討論 agent／G1 reviewer
  - Goal:認可是確認理解，不是驗證營運事實
  - Situation:S1-survey 使用者點頭後，agent 要把清單升成已核事實
  - Known information:tip `skills/dev-talk/nodes/S1-survey.md:28-29` 現況把認可後清單當已核事實
  - Missing information:原始碼或營運出處
  - Human decision:補 path 或改標 Assumption+期限
  - Authority:牙擋點頭獨源；人判來源是否真能重開
  - External dependency:無
  - Out-of-system action:打開聲稱的來源
  - Waiting/timeout behavior:無
  - Recovery:改標 Assumption 或補可重開 path 後重跑
  - Audit/handoff requirement:來源欄不是「點頭」
  - Observation:見本條觀測

#### S-3.4 狀態枚舉必須落在五值集合
- GIVEN 一份高影響列狀態字面為 `Unknown` 或 `Fact`（不在 {Observed, Reported, Inferred, Assumption, Conflict}）
- WHEN 跑 S-3.1 同一支檢查
- THEN exit ≠ 0；輸出含 `枚舉` 或列出五值之一
- 觀測:從 exit 與字樣看 | 集合外必紅算過 | 用 `scripts/fixtures/discovery-gaps/enum-unknown.md` 測
- Operational Context:不適用 — 枚舉形狀。語意是否填對仍是 G1 抽查。

#### S-3.5 非高影響 Context 句不貼枚舉不得紅
- GIVEN 一份 1-discussion：Context 有已核 `path:L` 句、無「風險=高」；高影響列（例外／痛點）枚舉與來源齊
- WHEN 跑 S-3.1 同一支檢查
- THEN exit 0（OC-5：不要求每一句 Context 都貼）
- 觀測:從 exit 看 | 普通 Context 無枚舉仍綠算過 | 用本 slug 1-discussion Context 形當正向測
- Operational Context:不適用 — 收窄範圍，無交接。

### R-4: 系統 SHALL 在高影響 Assumption 到期未驗時擋下 G2
A-4／3A／SC-4。擋點長在既有 `check-spec-gate.sh`（G2 形狀 Gate，不另造家族）。Assumption 四欄字面：若為假影響什麼／影響級／怎麼驗／何時／由誰驗。4-spec 用 `## Assumption refs` 表讓腳本看見引用：欄位 `引用（原文片段）`／`deadline`／`status`；`status` ∈ {open, resolved, oc-accepted}；`deadline` = `YYYY-MM-DD` 或 `stage-2`／`stage-3`。status=open 且期限已過（日期早於今天，或 `stage-N` 而本檔已在第 4 站）且無 oc-accepted → 該檢查 exit 1。已驗轉 Observed／Reported（status=resolved）或 Owner Call 接受風險（status=oc-accepted）→ exit 0。

**審的時候看什麼**
人看得見的拒絕發生在 `check-spec-gate.sh`，不是「模板有欄就綠」。過期 + 未驗 + 無 OC 必須 exit 1。

#### S-4.1 過期未驗無 OC 的引用必須讓 spec-gate exit 1
- GIVEN 一份 4-spec 含 `## Assumption refs` 一列：引用=「採用現場仍把解法寫進 Goal」、deadline=`2020-01-01` 或 `stage-2`、status=`open`；無 oc-accepted
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec>`
- THEN exit 1；輸出含 `Assumption` 或 `過期` 或 `open`
- 觀測:從 spec-gate exit 與輸出看 | 過期 open 必紅算過 | 用 `scripts/fixtures/discovery-gaps/assumption-expired-open.md` 測
- Operational Context:
  - Actor:G2 reviewer
  - Goal:過期高影響假設進不了 G2
  - Situation:期限=Stage 2，人已在寫 4-spec
  - Known information:四欄與 refs 表
  - Missing information:該假設是否已驗
  - Human decision:驗轉 resolved，或寫 oc-accepted 接受殘餘風險
  - Authority:spec-gate 機械拒送審
  - External dependency:無
  - Out-of-system action:在終端機跑 spec-gate
  - Waiting/timeout behavior:拒絕發生在送審那一關，同步結束
  - Recovery:改 status=resolved 或 oc-accepted 後重跑；不要口頭說「知道有假設」
  - Audit/handoff requirement:refs 表看得到 status
  - Observation:見本條觀測

#### S-4.2 已驗轉 resolved 必須讓 spec-gate exit 0
- GIVEN 同一表形，該列 status=`resolved`（已轉 Observed 或 Reported），deadline 可仍是過去日期
- WHEN 跑 S-4.1 同一支 `check-spec-gate.sh`
- THEN 不得只因該列而 exit 1（其他既有 C1–C6 仍按其自身規則）
- 觀測:從該 fixture 的 spec-gate 對 Assumption 項看 | 該項綠算過 | 用 `scripts/fixtures/discovery-gaps/assumption-resolved.md` 測
- Operational Context:不適用 — 與 S-4.1 同一擋點；本條只換 status。

#### S-4.3 Owner Call 接受風險必須讓 spec-gate 放行該列
- GIVEN 同一表形，status=`oc-accepted`（本 slug 對照：2-decision OC-3 收窄 Q6 與三條現場假設）
- WHEN 跑 S-4.1 同一支檢查
- THEN 不得只因該列而 exit 1
- 觀測:從 Assumption 項看 | oc-accepted 放行算過 | 用本檔 `## Assumption refs` 三列測
- Operational Context:不適用 — 與 S-4.1 同一擋點；本條只換 OC 接受。

#### S-4.4 模板與範例必須有 Assumption 四欄地板
- GIVEN `_templates/1-discussion.md`（或 2-decision 模板 Assumptions 落點）與 `example/contract-expiry-reminder/1-discussion.md` 在 Stage 6 改後
- WHEN 跑 `check-realworld.sh`
- THEN 兩份都含四欄字面「若為假影響什麼」「影響級」「怎麼驗」「何時／由誰驗」（或同等表頭）；缺任一欄 → exit ≠ 0
- 觀測:從 realworld 對四欄字面的檢查看 | 缺欄紅、齊則綠算過 | 用改後模板／範例測
- Operational Context:不適用 — 模板地板，不是填檔 G2 擋點。

### R-5: 系統 SHALL 讓後讀者從 Human verdict 一行看出驗了哪個角色與哪場
A-5 LIGHT／8A／SC-5。Human verdict 本文格式：`<ENUM> | role=<Actors 表角色> | scenario=<AC-id 或 Demo Script 場景名>`。只寫 ACCEPTED + 姓名日期不得當完整 verdict。不做 Actor Coverage 全表。既有 attestation 牙（不是 Agent 代填）仍在。

**審的時候看什麼**
遮住前後文只看該行。要答得出驗了誰、驗了哪場。殘行（只有 ACCEPTED 與日期）必須紅。

#### S-5.1 只有 ACCEPTED 與姓名日期不得當完整 verdict
- GIVEN 一份 3-prototype User Demo Feedback：`Human verdict: ACCEPTED` 與 `Verdict attestation: human:rick @ 2026-09-13`，同行或該節無 `role=`、無 `scenario=`
- WHEN 跑本 feat 掛進 `check-realworld.sh` 的 verdict 一行檢查（同一入口；對填好的 3-prototype 在 ENUM=ACCEPTED 時發動）
- THEN exit ≠ 0；輸出含 `role` 或 `scenario`
- 觀測:從 exit 與字樣看 | 殘行必紅算過 | 用 Stage 3 殘行對照測
- Operational Context:
  - Actor:後讀 3-prototype 的人
  - Goal:一行內答出驗了誰、驗了哪場
  - Situation:有人按過 ACCEPTED
  - Known information:既有 attestation 牙
  - Missing information:角色與場景
  - Human decision:補 role 與 scenario，或改 NOT_REVIEWED
  - Authority:牙擋殘行；Agent 仍禁代填 attestation
  - External dependency:無
  - Out-of-system action:人類親填
  - Waiting/timeout behavior:無 attestation 的 ACCEPTED 仍被既有 runtime 拒
  - Recovery:改成 `ACCEPTED | role=Fast 實作者 | scenario=AC-9` 後重跑
  - Audit/handoff requirement:一行內同時有 ENUM、role、scenario
  - Observation:見本條觀測

#### S-5.2 完整一行必須綠
- GIVEN `Human verdict: ACCEPTED | role=Fast 實作者 | scenario=AC-9` 且 attestation 行符合既有契約
- WHEN 跑 S-5.1 同一支檢查
- THEN 不得只因該行而 exit ≠ 0
- 觀測:從該項看 | 完整行放行算過 | 用 Stage 3 完整行形測
- Operational Context:不適用 — 與 S-5.1 同一牙；本條只換完整行。

#### S-5.3 模板與範例不得要求 Actor Coverage 全表
- GIVEN Stage 6 改後的 `_templates/3-prototype.md` 與 example 3-prototype
- WHEN 搜 `Actor Coverage` 作為本包必填表（每個關鍵角色標 direct interview／observation／proxy／not covered）
- THEN 零命中「本包必填全表」指令；`role=`／`scenario=` 指令在；既有 attestation 規則仍在
- 觀測:從兩檔原文看 | 無全表必填、有一行角色場景算過 | 用改後模板／範例測
- Operational Context:不適用 — LIGHT 上限，無新全表交接。

### R-6: 系統 SHALL 讓 Stage 1 高影響痛點到 Stage 4 每條都有去向
A-6／4A／SC-6。Stage 2 表引用 Stage 1 原文片段 + 去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗} + 一句理由。不另發第二鏈編號。Stage 4 `## Real-world Disposition` 三欄：引用／去向／下落。標「本方案處理」者下落必須是至少一條 `R-` 或 `S-` id（Decision 4A：至少一條 R/S）；其餘落到 Out of Scope／Known limit／後續 slug。full lane 缺表 → 指定檢查紅。不發明第二條 ID 鏈。

**審的時候看什麼**
用原文片段對一次。Stage 1 寫過的高影響列後面還在。去向空白或第二鏈編號必須紅。

#### S-6.1 full lane 缺 disposition 或去向空白必須紅
- GIVEN 一份 full lane 4-spec：無 `## Real-world Disposition`，或有表但某一列去向空白
- WHEN 跑 `check-spec-gate.sh`（同一支，加 disposition 形狀項）
- THEN exit 1；輸出含 `Disposition` 或 `去向`
- 觀測:從 spec-gate exit 與字樣看 | 缺表或空白去向必紅算過 | 用 Stage 3 壞卡「痛點消失／去向空白」同形測
- Operational Context:
  - Actor:收斂者／G2 reviewer
  - Goal:痛點不能無聲消失
  - Situation:Stage 1 Journey 寫了「痛點消失」
  - Known information:2-decision 已有去向帳形
  - Missing information:Stage 4 下落
  - Human decision:補表或把列標刻意維持／Non-Goal
  - Authority:spec-gate 擋缺表
  - External dependency:無
  - Out-of-system action:對原文片段
  - Waiting/timeout behavior:無
  - Recovery:按 2-decision 表抄進 4-spec 並填 S-id 或 Out of Scope
  - Audit/handoff requirement:引用用原文，不用第二鏈編號
  - Observation:見本條觀測

#### S-6.2 本方案處理必須落到至少一條 R 或 S
- GIVEN 一份 4-spec disposition：引用=Journey「發現被錨定」、去向=本方案處理、下落=`S-2.1`
- WHEN 跑 S-6.1 同一項
- THEN 該列不造成 exit 1；若下落沒有任何以 `R-` 或 `S-` 開頭的 id → exit 1
- 觀測:從該列下落是否含 `R-` 或 `S-` id 看 | 有則綠、無則紅算過 | 用本檔 disposition「發現被錨定 → S-2.1」測
- Operational Context:不適用 — 下落形狀。

#### S-6.3 非處理去向必須落到 Out of Scope 或 Known limit 或後續 slug
- GIVEN 三列：刻意維持 → 下落含 `Out of Scope` 或 `Known limit`；仍待驗 → 下落含 `Known limit`；另開 slug → 下落含一個 `docs/dev/<slug>/` 或 slug 字面
- WHEN 跑 S-6.1 同一項
- THEN 三列都不造成 exit 1；若去向不是「本方案處理」且下落空白 → exit 1
- 觀測:從三列下落看 | 非處理必有 OOS／limit／slug 算過 | 用本檔 Exception 三列測
- Operational Context:不適用 — 非處理下落。

#### S-6.4 不得出現第二鏈編號
- GIVEN `_templates/2-decision.md`、`_templates/4-spec.md`、本 slug 2-decision／4-spec、example 對應檔在 Stage 6 改後
- WHEN 搜第二鏈前綴加連字號加數字（字面形：大寫 R、大寫 W、連字號、一位數字）
- THEN 零命中（引用欄是原文片段，不是第二鏈編號；負向對照句若只寫「不得發第二鏈」也不算發 ID）
- 觀測:從 `rg -n 'RW-[0-9]'` 對上列路徑看 | 輸出為空算過 | 用改後模板／本 slug／example 測
- Operational Context:不適用 — 禁第二鏈，無交接。

### R-7: 系統 SHALL 在出貨時留下回看日期 owner 來源與門檻
A-7／5A／SC-7。約定寫在 7-review Exit，四欄字面：回看日期／回看 owner／資料來源／低於何值重開。結果到期用既有 `history-append.sh` 追加。不另造永久 `lookback.md`。G3 不必等數週結果。牙驗四欄在；指標是否代表問題改善是人判。到期未回看不得把問題寫成已改善。

**審的時候看什麼**
Exit 四個欄位名都在。缺一欄紅。結果列走 HISTORY 寫入口，不是新檔種類。

#### S-7.1 模板或範例 Exit 缺四欄之一必須紅
- GIVEN Stage 6 改後的 `_templates/7-review.md` Exit 與 `example/contract-expiry-reminder/7-review.md`
- WHEN 跑 `check-realworld.sh`
- THEN 兩份都含字面「回看日期」「回看 owner」「資料來源」「低於何值重開」；缺任一 → exit ≠ 0
- 觀測:從 realworld 對四欄字面看 | 缺欄紅、齊則該項綠算過 | 用改後模板／範例測
- Operational Context:
  - Actor:owner
  - Goal:出貨時留下誰／何時／用什麼／低於何值重開
  - Situation:G3 功能全綠，準備勾 Exit
  - Known information:四欄字面
  - Missing information:採用現場真實指標
  - Human decision:填四欄；到期用 HISTORY 追加結果
  - Authority:牙驗欄在；改善與否是人判
  - External dependency:日曆、採用專案 Stage 1
  - Out-of-system action:到期回看
  - Waiting/timeout behavior:回看日未到不得把問題寫成已改善
  - Recovery:補缺欄後重跑；不要另造 lookback.md
  - Audit/handoff requirement:Exit 四欄 + 到期 HISTORY 列
  - Observation:見本條觀測

#### S-7.2 已宣稱 shipped 的 7-review 含回看節卻缺欄必須紅
- GIVEN 一份填好的 `7-review.md`：`status: shipped` 或 Exit 已勾，且含 `回看` 節或四欄名之一，但缺「低於何值重開」
- WHEN 跑 `check-realworld.sh`（射程延到此填檔；無回看節的舊 7-review 不發動）
- THEN exit ≠ 0；輸出含缺的欄名
- 觀測:從該填檔檢查看 | 有節缺欄必紅、舊檔無節不發動算過 | 用 `scripts/fixtures/discovery-gaps/lookback-missing-threshold.md` 與一份無回看節的舊 7-review 測
- Operational Context:不適用 — 填檔地板；舊檔不誤殺。

#### S-7.3 回看結果必須走 history-append 不得另造永久檔
- GIVEN Stage 6 改後的 7-review 模板／指南：結果入口寫 `scripts/history-append.sh`
- WHEN 搜本 feat 落地後的活教師（`_templates/7-review.md`、指南 lookback 句、example 7-review）是否要求新建 `lookback.md`
- THEN 零命中「另造 lookback.md／永久 lookback 檔」；含 `history-append.sh`
- 觀測:從 `rg -n 'lookback\\.md' _templates/7-review.md example/contract-expiry-reminder/7-review.md` 看 | 無永久檔、有 append 入口算過 | 用改後三處測
- Operational Context:不適用 — 寫入口契約。

### R-8: 系統 SHALL 讓 owner 核准後的事實路徑讀得到事件行為結果且方案檔仍禁讀
B-1／6A／SC-8。本輪清單節名 `## Evidence manifest`，與 1-discussion **同檔**（不另造永久檔種類）。表頭：想找哪類／為什麼／擬路徑或來源／owner 核准／已讀。`owner 核准` ∈ {是, 未核, 禁}。`devtalk-guard.sh` 延伸讀取圍欄（同一支腳本）：talk 游標在時，放行核准=是的路徑；仍禁 2-decision／3-prototype／4-spec／5-tasks／6-implementation-notes／7-review（含 html twin）。未核准路徑不得當已授權 evidence。ticket／SOP 裡的解法建議不當事實。

**審的時候看什麼**
核准格是「是」才能讀到事件／行為／結果。讀 2-decision／4-spec 仍被擋。未核路徑不得引用。

#### S-8.1 核准路徑必須讀得到
- GIVEN talk 游標在（`.devtalk-cursor.json` 或既有 talk 游標檔存在）；`docs/dev/<slug>/1-discussion.md` 的 `## Evidence manifest` 有一列：擬路徑=`_templates/1-discussion.md`、owner 核准=`是`
- WHEN 討論者 Read 該擬路徑（經 `devtalk-guard.sh` 的 Read 分支）
- THEN 該次 Read 不被 guard exit 2 擋下（exit 0）
- 觀測:從 guard 對該 Read 的 exit 看 | 核准=是放行算過 | 用本 slug 原料列同形測
- Operational Context:
  - Actor:討論 agent
  - Goal:owner 核准後讀得到事件／行為／結果
  - Situation:要核「Goal 鎖通道」教師
  - Known information:manifest 核准格=是
  - Missing information:檔內具體行
  - Human decision:owner 已核這條路徑
  - Authority:guard 放行核准列
  - External dependency:無
  - Out-of-system action:讀已指名檔
  - Waiting/timeout behavior:核准格空白時不得往下讀
  - Recovery:先列「想找哪類＋為什麼」等 owner 核
  - Audit/handoff requirement:已讀欄可改「是」
  - Observation:見本條觀測

#### S-8.2 方案檔即使被列入也必須禁
- GIVEN talk 游標在；manifest 有一列擬路徑=`docs/dev/foo/2-decision.md` 或 `docs/dev/foo/4-spec.md`，owner 核准即使誤寫「是」
- WHEN Read 該路徑
- THEN `devtalk-guard.sh` exit 2；stderr 含 `2-decision` 或 `4-spec` 或 `方案檔`
- 觀測:從 guard exit 與 stderr 看 | 2–7 方案檔必擋算過 | 用 Stage 3 「2-decision／4-spec 列為禁」同形測
- Operational Context:
  - Actor:討論 agent
  - Goal:下游方案檔仍進不去
  - Situation:有人把 2-decision 寫進擬路徑
  - Known information:圍欄禁 2／3／4／5／6／7
  - Missing information:無
  - Human decision:該列改核准=禁，不當事實
  - Authority:guard 硬擋，核准格不能覆寫禁令
  - External dependency:無
  - Out-of-system action:改讀 specs／原始碼／已核事實路徑
  - Waiting/timeout behavior:無
  - Recovery:從擬路徑刪掉方案檔
  - Audit/handoff requirement:該列核准=禁
  - Observation:見本條觀測

#### S-8.3 未核准路徑不得當已授權
- GIVEN talk 游標在；擬路徑=`notes/review-requirement-discovery-gaps.md`、owner 核准=`未核` 或格空白
- WHEN Read 該路徑，或 1-discussion 把該路徑當 Evidence 唯一來源
- THEN Read：guard exit 2。填檔：S-3.1 同一主張牙 exit ≠ 0（未核不得當已授權）
- 觀測:從 guard exit 與主張牙看 | 未核禁讀且不得當來源算過 | 用 Stage 3「採用現場逐字稿未核」同形測
- Operational Context:
  - Actor:討論 agent／owner
  - Goal:未指名資料夾不能先列目錄當已授權
  - Situation:想收 Q6 現場逐字稿
  - Known information:無採用 log
  - Missing information:owner 是否核准
  - Human decision:核或維持未核（本 slug OC-3：不捏造訪談）
  - Authority:owner 才能改核准=是
  - External dependency:系統外訪談稿
  - Out-of-system action:送核准卡
  - Waiting/timeout behavior:顯性「等 owner」；未核不得往下
  - Recovery:核准後才讀；或維持 Assumption
  - Audit/handoff requirement:核准格空白 = 禁讀
  - Observation:見本條觀測

#### S-8.4 ticket 或 SOP 裡的解法建議不得當事實
- GIVEN 一份 Evidence 列：來源是 ticket／SOP 正文裡的「建議做 dashboard」，狀態卻標 Observed
- WHEN 跑 S-3.1 同一支主張牙（skill 對稱句：解法建議進 Requested solution，不進 Evidence）
- THEN exit ≠ 0；輸出含 `解法` 或 `Requested solution` 或 `不當事實`
- 觀測:從該牙 exit 與字樣看 | 解法建議當 Observed 必紅算過 | 用 `scripts/fixtures/discovery-gaps/ticket-solution-as-fact.md` 測
- Operational Context:不適用 — 與 A-3 同一主張牙；本條只釘 ticket 解法。

### R-9: 系統 SHALL 在 Fast 寫規格前收完六問早期風險分診
B-2／7A／OC-6／SC-9。進 Stage 4 **之前**六問（字面）：改變下一步？／改權限／核准語意？／改等待／完成語意？／改角色交接？／改系統外動作？／改中斷恢復？每問答 `是` 或 `否` 加一句。節名 `## Fast early risk triage`，可附在 4-spec 頂，但必須出現在 `## ADDED Requirements` 之前。空白 ≠ 已分診。全否且已有 approved spec 且不改語意的純視覺／文案（OC-6）→ 去向=`Fast`。任一「是」→ 去向 ∈ {full, fast+mini, OC}，不可空白開寫。擋點長在 `check-spec-gate.sh`：僅 `lane: fast` 發動。

**審的時候看什麼**
六問都有是／否＋一句。「只改狀態字、把等待顯示成完成」必須命中第 3 問。命中列有 full／mini／OC，不是空白開寫。

#### S-9.1 Fast 六問空白不得當已分診
- GIVEN 一份 `lane: fast` 的 4-spec：無 `## Fast early risk triage`，或六問「答」欄空白
- WHEN 跑 `check-spec-gate.sh`
- THEN exit 1；輸出含 `Fast` 或 `六問` 或 `triage`
- 觀測:從 spec-gate exit 與字樣看 | 空白表必紅算過 | 用 `scripts/fixtures/discovery-gaps/fast-blank-triage.md` 測
- Operational Context:
  - Actor:Fast 實作者
  - Goal:寫 4-spec 前先收完六問
  - Situation:檔數少、想直接開寫
  - Known information:六問表頭
  - Missing information:這次 diff 是否改等待語意
  - Human decision:填六問；命中則請 owner 裁去向
  - Authority:spec-gate 擋未分診的 Fast
  - External dependency:無
  - Out-of-system action:對 diff 答六問
  - Waiting/timeout behavior:未收束不得進 R/S
  - Recovery:填滿六問與去向後重跑
  - Audit/handoff requirement:表在 ADDED 之前
  - Observation:見本條觀測

#### S-9.2 等待被顯示成完成必須命中第 3 問
- GIVEN Fast 對照案：只改一個狀態字，把等待顯示成完成；六問第 1／2／4／5／6 = 否，第 3 = 是（一句含「等待被顯示成完成」）
- WHEN 人依表填完（Stage 6 的對照 fixture 已填好）
- THEN 第 3 問命中為是；去向不得是空白，且不得是 `Fast`（必須 ∈ {full, fast+mini, OC}）
- 觀測:從該 fixture 表第 3 列與去向列看 | #3=是且去向三擇一算過 | 用 Stage 3 AC-9 對照案同形測
- Operational Context:
  - Actor:Fast 實作者／owner
  - Goal:等待誤標不能當純視覺 Fast
  - Situation:「只改狀態字」
  - Known information:OC-6 純視覺不改語意才可 Fast
  - Missing information:owner 選 full、mini 還是 OC
  - Human decision:owner 裁去向
  - Authority:命中後去向空白 → spec-gate 紅
  - External dependency:無
  - Out-of-system action:owner 寫去向
  - Waiting/timeout behavior:待裁期間不得開寫 R/S
  - Recovery:填 full／fast+mini／OC 後重跑
  - Audit/handoff requirement:第 3 問「是」+ 一句
  - Observation:見本條觀測

#### S-9.3 命中卻無去向必須紅
- GIVEN `lane: fast` 的 4-spec：六問第 3 答=`是。等待被顯示成完成`，去向欄空白或字面 `待裁`
- WHEN 跑 `check-spec-gate.sh`
- THEN exit 1；輸出含 `去向` 或 `full` 或 `mini` 或 `OC`
- 觀測:從 spec-gate 看 | 命中無去向必紅算過 | 用 `scripts/fixtures/discovery-gaps/fast-hit-no-dest.md` 測
- Operational Context:不適用 — 與 S-9.2 同一去向契約；本條只驗空白去向。

#### S-9.4 全否且不改語意的純視覺必須可維持 Fast
- GIVEN `lane: fast` 的 4-spec：六問皆 `否`＋一句（例如「只改 CSS 色」）；已有 approved spec；去向=`Fast`
- WHEN 跑 `check-spec-gate.sh`
- THEN 不得只因六問全否＋去向 Fast 而 exit 1（OC-6）
- 觀測:從該項看 | 純視覺全否可 Fast 算過 | 用 `scripts/fixtures/discovery-gaps/fast-visual-all-no.md` 測
- Operational Context:不適用 — OC-6 收窄；「不改語意」仍由 reviewer 對 diff，牙只驗表形。

#### S-9.5 full lane 無六問表不得被 Fast 項誤殺
- GIVEN 本檔 `- lane: full` 且無 `## Fast early risk triage`
- WHEN 跑 `check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md`
- THEN 不得因缺六問表而 FAIL（Fast 項 no-fire）
- 觀測:從本檔跑 spec-gate 的 Fast 項看 | full 缺表不紅算過 | 用本檔測
- Operational Context:不適用 — 發動條件。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec。下列是**活教師原文**；Stage 6 改口。本 hop 不改正本。

### M-1: 模板 Goals 與雛形觀測鎖通道
原條文(`_templates/1-discussion.md:75-76` 與 `:91-96`)：
> Goals「條列，可驗證的想達成」；驗收雛形「從哪看:`<畫面路徑 | API 端點 | log | 產出檔>`」
改成:Goals 只寫結果；新增 `## Requested solution`；雛形「從哪看」改問結果在哪被看見，不預填畫面／API 通道。承接 S-1.1。

### M-2: 範例把 dashboard 寫進 Goal／AC／Interview
原條文(`example/contract-expiry-reminder/1-discussion.md:62-65`、`:83-103`、`:119`)：
> 登入後不用翻清單就能看到；點擊可直達；一眼可見；AC 鎖 dashboard；Interview「dashboard 是最低成本的呈現面」
改成:Goals 改寫結果；通道進 Requested solution 並標未定案。承接 S-1.3。

### M-3: N3 發現題也要附推薦
原條文(`skills/dev-talk/nodes/N3-probe.md:22-23`、`:41`)：
> 一次只問一題、附推薦答案；連續兩輪無新問題可停
改成:發現題 `發現｜` 禁推薦；裁決題 `裁決｜` 可附；兩輪只當輔助。承接 S-2.1／S-2.2。

### M-4: S4-accept 把從哪看鎖成畫面／端點
原條文(`skills/dev-talk/nodes/S4-accept.md:19-22`)：
> 從哪裡看(畫面/端點/檔案/log)
改成:問結果在哪發生，不鎖通道。承接 S-1.1。

### M-5: 認可後清單即已核事實
原條文(`skills/dev-talk/nodes/S1-survey.md:28-29`)：
> 認可後的清單 = 本次已核事實
改成:認可 ≠ 來源升格；高影響主張仍要來源或 Assumption+期限。承接 S-3.3。

### M-6: realworld 牙只驗章節與訪談字樣
原條文(`scripts/check-realworld.sh:88-91`)：
> 只驗 Assumption 標記與 Evidence 含「訪談」
改成:加高影響枚舉／來源 XOR 期限／verdict 一行／lookback 四欄／前綴對稱／Goals 分欄地板；MIN_CHECKS 改成加完後的實際檢查數。承接 R-1～R-5、R-7。

### M-7: Human verdict 只有 ENUM
原條文(`_templates/3-prototype.md:128-129`)：
> Human verdict: ACCEPTED | REVISE | NOT_REVIEWED
改成:同 ENUM 加上 `| role=… | scenario=…`。承接 S-5.1。

### M-8: Stage 2／4 不對帳 Stage 1 痛點
原條文(`_templates/2-decision.md:35-37`、`:59-60`；`_templates/4-spec.md:72-75`)：
> 接手從 Goals／驗收雛形／`[>]` 提煉；Stage 4 只對帳 Stage 3 場景
改成:加 disposition 表；Stage 4 對帳含 Stage 1 高影響列下落。承接 R-6。

### M-9: Exit 無回看四欄
原條文(`_templates/7-review.md:316-342`)：
> Exit Checklist 勾到 shipped，無回看日期／owner／來源／門檻
改成:Exit 加四欄字面；結果走 `history-append.sh`。承接 R-7。

### M-10: Fast 省略 1–3 且人機風險寫在 4-spec
原條文(`skills/dev-flow/SKILL.md:34-36`；`_templates/4-spec.md:266-269`)：
> Fast 省略 Stage 1–3；高風險人機互動在 4-spec 才列自動升 Full
改成:進 4 前六問；命中由 owner 裁 full／fast+mini／OC。七關結構不改（Exception「Fast 合法跳過 1–3」刻意維持）。承接 R-9。

### M-11: devtalk-guard 只掃 skill 寫入洩漏
原條文(`hooks/devtalk-guard.sh:16-21`)：
> 非 skills/dev-talk/ 靜默放行；只掃寫入下游字眼
改成:同一支腳本加 Read 分支：talk 游標在時放行 manifest 核准=是；仍禁 2–7。承接 R-8。

## REMOVED Requirements

無。不刪 Fast 可跳過 1–3、不刪既有 attestation 牙、不刪第二鏈禁令、不刪檢查家族名。

## 行為流程圖(R 級)

```
[R-1] 分辨工作結果與解法構想
  Goals 只寫結果
  構想進 Requested solution
  對照稿指出錯欄
[R-2] 發現題不先塞推薦
  發現｜禁推薦
  裁決｜可附選項
  刪一邊前綴就紅
[R-3] 高影響主張回到來源或期限
  五值枚舉加來源欄
  點頭不得當獨源
  非高影響句不逼貼
[R-4] 過期假設擋下 G2
  refs 表 open 且過期就紅
  resolved 或 oc-accepted 放行
  R-5 verdict 一行寫清角色場景
[R-6] 痛點列逐條有去向
  原文片段加五值去向
  處理必有 R/S
  不發第二鏈編號
[R-7] 出貨留下回看四欄
  Exit 日期 owner 來源門檻
  結果走 HISTORY 追加
[R-8] 核准後讀得到事實且方案檔仍禁
  未核不得讀
  2-7 仍擋
[R-9] Fast 寫規格前收完六問
  空白不是已分診
  等待誤標必命中
  命中要有去向
```

審頁產器 `build-stage4-html.py` 行為圖仍硬切 8 框（本 hop 不改產器）。R-5 SHALL「verdict 一行寫清角色場景」寫在 R-4 框步驟列，讓 **R-9 獨立成框**；九個 R-id 都在圖上。

## Assumption refs

本 slug 自己吃 3A 形。Q6 與三條現場假設由 OC-3 接受殘餘風險（不捏造訪談）。

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q6 採用現場仍把解法寫進 Goal | stage-2 | oc-accepted |
| 現場發現題仍附推薦 | stage-2 | oc-accepted |
| Fast 因檔數少漏判互動 | stage-2 | oc-accepted |

## Real-world Disposition

承接 2-decision 去向帳。引用 Stage 1 原文，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| Journey「發現被錨定」 | 本方案處理 | S-2.1、S-2.2 |
| Journey「點頭當證據」 | 本方案處理 | S-3.3 |
| Journey「痛點消失」 | 本方案處理 | S-6.1、S-6.2 |
| Journey「問題沒改善」 | 本方案處理 | S-7.1、S-7.3 |
| Journey「互動風險晚露」 | 本方案處理 | S-9.1、S-9.2 |
| Workaround「owner 用審核筆記記缺口」 | 本方案處理 | S-1.1 |
| Workaround「現場證據靠記憶轉述」 | 本方案處理 | S-8.1、S-8.3 |
| Workaround「Fast 直接寫 4-spec」 | 本方案處理 | S-9.1、S-9.4 |
| Workaround「人口頭記先問現況」 | 本方案處理 | S-2.1 |
| Exception「Fast 合法跳過 1–3」 | 刻意維持 | Out of Scope：七關結構不改；只加進 4 前六問 |
| Exception「A-5 只 LIGHT」 | 刻意維持 | Out of Scope：不做 Actor Coverage 全表；S-5.3 |
| Exception「`[~]` 可走到 G2」 | 本方案處理 | S-4.1 |
| Exception／Q6「採用現場仍把解法寫進 Goal」 | 仍待驗 | Known limit：OC-3；本 repo 範例教師 = Observed |
| Exception「現場發現題仍附推薦」 | 仍待驗 | Known limit：無逐字稿；1A 改未來問法 |
| Exception「Fast 因檔數少漏判互動」 | 仍待驗 | Known limit：採用現場是否踩過無 log |

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-9.5）。
- 既有測試全綠：`bash scripts/check-realworld.sh`、`bash scripts/check-spec-gate.sh`（對本檔與既有 fixture）、`hooks/devtalk-guard.sh` 既有寫入洩漏回歸、`bash scripts/devflow-check.sh` 對應段。
- 非功能：指定檢查對單份 md 在本機同步結束；不新增網路 capability。
- 行為不變類（M-10 Fast 可跳 1–3、第二鏈禁令、attestation）：golden master — 同一份「Fast 且六問全否＋純視覺」仍可 Fast；第二鏈編號仍零命中；無 attestation 的 ACCEPTED 仍拒。

## Out of Scope

- 1B／1C、2B／2C、3B／3C、4B／4C、5B／5C、6B／6C、7B／7C、8B／8C（見 2-decision Rejected）。
- 新造 `check-discovery-gaps.sh` 或任何第二檢查家族。
- 第二鏈編號／Journey／Actor 第二鏈。
- Actor Coverage 全表。
- 另造永久 lookback.md 或另檔 evidence-manifest.md／triage 卡（Variant B 已棄）。
- dashboard／API 黑名單。
- 拆成九個 slug。
- 本 hop 改 `_templates/`／`skills/`／`example/`／守衛正本（契約在 R/S，落地 Stage 6）。
- 本 hop 改 `STATUS.md`／`HISTORY.md`、bump plugin、發版、開 `5-tasks.md`。
- 發明 G2／G3 PASS。
- 重開九條 DO／LIGHT。
- 從最終 1-discussion 還原整場對話當 A-2 硬 gate。
- 主機層攔截「跳過 guard 硬 Read 方案檔」（Known limit：牙咬 talk 游標在時的 hook，不是 OS hook）。

### Stage 3 對帳

#274 已合 main：`3-prototype.md` `status: approved`；`Human verdict: ACCEPTED | role=owner | scenario=AC-1–AC-9`；`Verdict attestation: human:rick @ 2026-09-13`。Demo 前置已滿足。本 hop 4-spec 頂欄 `verdict` 仍空，不發明 G2 PASS。

- 3-prototype「Scenario AC-1」→ S-1.1、S-1.2、S-1.3、S-1.4
- 3-prototype「Scenario AC-2」→ S-2.1、S-2.2、S-2.3
- 3-prototype「Scenario AC-3」→ S-3.1、S-3.2、S-3.3、S-3.4
- 3-prototype「Scenario AC-4」→ S-4.1、S-4.2、S-4.3、S-4.4
- 3-prototype「Scenario AC-5」→ S-5.1、S-5.2、S-5.3
- 3-prototype「Scenario AC-6」→ S-6.1、S-6.2、S-6.3、S-6.4
- 3-prototype「Scenario AC-7」→ S-7.1、S-7.2、S-7.3
- 3-prototype「Scenario AC-8」→ S-8.1、S-8.2、S-8.3、S-8.4
- 3-prototype「Scenario AC-9」→ S-9.1、S-9.2、S-9.3、S-9.4
- Method Variant A 同檔就地欄 → 各 R 的節名／表頭；Variant B／C 在 Out of Scope
- Method 等待誤標對照 → S-9.2
- Operational Context Recovery（搬構想、重寫發現題、補來源或期限、驗轉或 OC、人類親填 verdict、從片段恢復、HISTORY 追加、等 owner 才讀、owner 裁六問去向）→ 各對應 S 的 Recovery 欄

## Diff Budget

本節是**估計**（給後續 Stage 6，不是本規格 PR 的檔數）。超支本身非偏差，是停下判 L1/L2 的訊號。Decision 已拒拆 slug。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| 模板 1／2／3／4／7 節名與表頭 | ≤5 | ≤180 | ≤40 |
| skills／指南對稱句（dev-talk 節點＋dev-flow lane） | ≤8 | ≤160 | ≤40 |
| example 1／3／4／7 改口 | ≤4 | ≤80 | ≤20 |
| `check-realworld.sh` 地板＋MIN_CHECKS＋fixture | ≤6 | ≤120 | ≤220 |
| `check-spec-gate.sh` 加 Assumption／Fast／disposition 項＋fixture | ≤5 | ≤140 | ≤220 |
| `devtalk-guard.sh` Read 分支＋既有洩漏回歸 | ≤2 | ≤80 | ≤120 |
| **合計** | **≤30** | **≤760** | **≤660** |

[Assumption] 係數按「一個 S 一到兩條測試」，未加 mutation。本規格 PR 本身只動 `docs/dev/requirement-discovery-gaps/4-spec.md` 與 twin html。檔數 >15 是大案訊號；Decision 一包不拆，超支時先判 L1（不動 R/S）或回 G2。

## Dependencies

- `scripts/check-realworld.sh` —— justification:OC-1 模板／範例地板；本 feat 延射程，不另造家族。
- `scripts/check-spec-gate.sh` —— justification:已是 G2 Gate；3A／7A／4A 擋點加在同一支。
- `hooks/devtalk-guard.sh` —— justification:已是討論圍欄；6A 改允許集合。
- 它們已掛進的 `scripts/devflow-check.sh` —— justification:既有入口，不加第三支 CLI。
- `scripts/history-append.sh` —— justification:5A 回看結果寫入口。
- talk 游標檔（`check-devtalk-graph.sh --write-cursor` 已寫）—— justification:S-8.1 用既有標記認 talk 期，不新造 session 格式。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（模板／skill／三支牙／example）；②修改公開檢查 exit 契約（spec-gate 加項、realworld 加項、guard Read）；③跨模組 Interface（manifest 核准格 ↔ guard 允許集合）；⑨Feature Risk = high；⑩三個以上模組；⑪錯誤恢復（過期假設、未核禁讀、Fast 未分診）
- Design source: 既有 pattern —— 1A 延既有牙、Variant A 同檔就地欄、Decision 1A–8A；欄位字面是 Stage 3 留給本檔的 local lock

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| `check-spec-gate.sh` | G2 形狀：既有 C1–C6 + Assumption refs／Fast 六問／disposition | **擁有** 4-spec 送審通過／失敗 | → 4-spec 正文、→ `spec_profile()` | 不得新開第二支 G2 CLI；不得判語意 |
| `check-realworld.sh` | 模板／範例地板 + 有條件填檔（verdict 一行、lookback 四欄、Goals 錯欄 fixture） | **擁有** 教師地板判定 | → `_templates/`、`example/`、指定 fixture | 不得當唯一填檔 G2 Gate（過期假設不放這裡） |
| `devtalk-guard.sh` | talk 期 Read 允許集合 + 既有寫入洩漏 | **擁有** 討論期擋讀 | → 1-discussion manifest、→ talk 游標 | 不得放行 2–7；不得新開 `check-evidence-allow.sh` |
| 1-discussion 同檔欄 | Goals／Requested／manifest／主張欄 | 討論者擁有列；owner 擁有核准格 | ← 白名單＋核准路徑 | 不得把方案檔當 Observed |
| 2-decision／4-spec disposition | 原文片段去向與 R/S 下落 | 收斂者／規格作者 | ← Stage 1 原文 | 不得發第二鏈編號 |
| 7-review Exit | 回看四欄 | owner 擁有約定 | → `history-append.sh` | 不得另造 lookback 檔 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| spec-gate 讀 4-spec | in:一份 md；out:exit 0／1／2 + C 項 | 過期 open／Fast 空白／disposition 空白 → 1 | 只讀，不寫 4-spec | C1–C6 保留；只加項 |
| realworld 讀模板／範例／指定填檔 | in:root；out:exit 0／1 | 缺節名／缺四欄／殘行 verdict → 1 | 只讀 | MIN_CHECKS = 加完後實數，不是下限寬放 |
| guard Read | in:tool_input.file_path；out:exit 0／2 | 方案檔或未核路徑 → 2 | 不改目標檔 | 寫入洩漏掃描保留；Read 只在 talk 游標在時發動 |
| manifest 核准格 | in:是／未核／禁；out:允許集合 | 未核當已授權 → 主張牙紅 | 人寫一格，guard 讀字面 | 核准=是不能覆寫 2–7 禁令 |
| disposition 下落 | in:去向五值；out:R-id 或 S-id 或 OOS／limit／slug | 本方案處理無 R/S → 紅 | 4-spec 與 2-decision 引用同一原文片段 | 不另發 ID |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| spec-gate 新項（與 C1–C6 同檔函式） | 解析 refs／六問／disposition 表 | ← 4-spec、← `spec_profile` | md → lane? → 表形 | full 六問 no-fire；open+過期紅 | S-4.1～S-4.3、S-6.*、S-9.* |
| realworld 新 check() | 節名、前綴對稱、枚舉集合、verdict 一行、lookback 字面 | ← 模板／example／fixture | 字串包含 | 舊 7-review 無回看節 no-fire | S-1.*、S-2.2、S-3.*、S-5.*、S-7.1 |
| guard Read 分支 | talk 游標？→ 對 path | ← manifest 核准列 | path → 放行／exit 2 | 游標不在走舊寫入邏輯 | S-8.1～S-8.3 |
| 活教師改口 | 換指令與範例句 | ← 1A 字面 | 搜舊針 → 改分欄／前綴 | 漏改 example → S-1.3 紅 | S-1.3、S-2.1、M-2 |

### Design Constraints
- 必須:沿用三支既有牙；同檔就地欄；五值枚舉；disposition 原文片段；Exit 四欄；manifest 五欄；六問在 ADDED 前；verdict 含 role 與 scenario；MIN_CHECKS 等於實數。
- 禁止:第二檢查家族；第二鏈編號；lookback 永久檔；Actor Coverage 全表；dashboard／API 黑名單；本 hop 改 STATUS 表列；本 hop 落地碼當規格的一部分；本 hop 開 Stage 5；本 hop 填 G2 PASS。
- Extension point:採用現場是否照抄範例（OC-3 仍待驗）另用回看四欄追，不在本 slug 捏訪談。
- Known design limit:
  ① A-2 誘導無法從最終 md 完整還原；硬 gate 只守對稱句與「發現題附推薦」形，不還原對話。
  ② guard 只在 talk 游標在時擋 Read；人跳過 hook 硬讀方案檔，本 feat 不新造 OS hook。
  ③ 「不改語意」與「這條算不算高影響」仍是人判；牙只驗形狀。
  ④ 審頁產器行為圖硬切 8 框；R-5 SHALL 寫在 R-4 框步驟列，R-9 獨立成框。本 hop 不改產器。

## Verification Profile(G2 一併審)
- lane: full（判準:新能力、改公開檢查契約、高風險人機互動（訪談錨定／G2 假綠／證據越權）。owner 已 lock full；無偏離）
- Risk: high（判準:公開檢查 exit 契約 + 討論期讀取權限 + 過期假設假綠。模板「公開 API／不可逆契約副作用／高風險人機互動」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得把構想寫進 Goals 還當已完成分欄（S-1.2）
  - 不得用 dashboard／API 黑名單誤殺結果句（S-1.4）
  - 不得讓發現題附推薦仍當硬規則（S-2.1）
  - 不得把點頭當唯一來源（S-3.3）
  - 不得讓過期 open Assumption 通過 spec-gate（S-4.1）
  - 不得只寫 ACCEPTED + 日期當完整 verdict（S-5.1）
  - 不得讓痛點列去向空白或發第二鏈編號（S-6.1、S-6.4）
  - 不得另造 lookback 永久檔（S-7.3）
  - 不得讀 2–7 方案檔或未核路徑當已授權（S-8.2、S-8.3）
  - 不得把 Fast 空白六問當已分診（S-9.1）
  - 不得新造檢查家族、不得本 hop 改 STATUS／模板正本、不得發明 G2 PASS
- Required layers:check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支；`check-stage4-rs-contract.sh` 是本 hop 審頁形狀，不落地缺口牙，不列入本欄）
- Conditional layers:Supply chain — 當實作改到三支牙或 example 時，必跑 `devflow-check.sh` 對應段 + S-6.4 的 `rg`
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Race／stress（單檔字面檢查）、Windows 真機（Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && bash scripts/check-realworld.sh`
- Reliability triage:
  - Concurrency: n-a — 單一作者寫一份討論／規格；檢查只讀；無多 writer 鎖契約
  - Idempotency: applicable — 同一份 fixture 再跑指定檢查，exit 與字樣相同（S-1.2、S-4.1、S-9.1）
  - Timeout/retry: n-a — 本機檔案檢查同步結束，不自動重試；人修欄後重跑（S-4.1 Recovery）

Human verdict: ACCEPTED | role=owner | scenario=AC-1–AC-9。attestation:`human:rick @ 2026-09-13`（#274 已合 main）。4-spec 頂欄 `verdict` 仍空，不發明 G2 PASS。

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| Goals 仍鎖通道 | 下一場討論仍抄 Goal=dashboard | 模板／example Goals 仍要畫面／點擊 | Required:S-1.1、S-1.3 | — |
| 錯欄對照稿仍綠 | G1 看不到構想在錯欄 | S-1.2 fixture exit 0 | Required:S-1.2 | — |
| 黑名單誤殺 | 合法結果句被紅 | S-1.4 fixture exit ≠ 0 | Required:S-1.4 | — |
| 發現題仍附推薦 | 訪談被錨定 | N3 仍寫附推薦當硬規則 | Required:S-2.1 | — |
| 點頭當證據 | 假 Observed 替方案背書 | 點頭獨源 fixture 綠 | Required:S-3.3 | — |
| 過期假設過 G2 | 測試綠、原假設已假 | spec-gate 對 expired-open exit 0 | Required:S-4.1 | — |
| 殘行 verdict | 後讀者看不出驗了誰 | ACCEPTED+日期仍綠 | Required:S-5.1 | — |
| 痛點消失 | Stage 1 列後面沒了 | disposition 空白仍綠 | Required:S-6.1 | — |
| 出貨無回看 | 問題沒改善仍當 shipped | Exit 缺四欄仍綠 | Required:S-7.1 | — |
| 規定了但讀不到 | B-1 假規則 | 核准=是仍被擋，或未核仍當來源 | Required:S-8.1、S-8.3 | — |
| 方案檔被打開 | 討論直奔結論 | Read 2-decision exit 0 | Required:S-8.2 | — |
| Fast 空白開寫 | 等待誤標晚露 | 空白六問 spec-gate exit 0 | Required:S-9.1、S-9.2 | — |
| 另造第二家族 | 兩套方法論 | 出現 `check-discovery-gaps.sh` 當唯一入口 | Required:S-1.2 觀測「同一入口」 | — |
| 跳過 hook 硬讀 | 主機不擋 | 人直接 Read 方案檔 | Known limit ② | 本 feat 不新造 OS hook |
| 對話誘導還原失敗 | 最終 md 看不出當時問法 | 無對話硬 gate | Known limit ① | 只守對稱句 |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 1A–8A。本 hop 不填 G2 PASS。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 高影響抽樣規則鎖定為本檔 R-3 四條（Workarounds／Exceptions／Journey 痛點非空／`[Assumption]` 或 `[~]` 且風險或影響級為高／Interview ⚠️）。已核 path:L 無「風險=高」不貼枚舉 | OC-5 把「何謂高影響」留給 4-spec；全句枚舉會變字樣儀式 | `2-decision.md` OC-5；`3-prototype.md` 2A 好卡只要求高影響列 | 改成每句都貼則 S-3.5 翻案 | 待人審 |
| DD-2 | 4-spec 讓腳本看見 Assumption 的形 = `## Assumption refs` 三欄（引用／deadline／status∈{open,resolved,oc-accepted}）。deadline=`YYYY-MM-DD` 或 `stage-2`／`stage-3`。open + 已過站或過去日 → spec-gate exit 1 | 3A 要人看得見的 G2 拒絕；spec-gate 只讀 4-spec | `2-decision.md` 決策點 3A；`3-prototype.md` 3A | 改欄名則 S-4.1 fixture 全改 | 待人審 |
| DD-3 | Fast 六問節名 = `## Fast early risk triage`，必須在 `## ADDED Requirements` 之前。六問字面鎖定 Stage 3 表。去向 ∈ {Fast, full, fast+mini, OC}。僅 `lane: fast` 發動 | 7A 要在 lane 選定前收束；full 已走 Stage 1 | `3-prototype.md` 7A 表；`2-decision.md` OC-6 | 改節名或改成一律升 full = 已拒 7B | 待人審 |
| DD-4 | disposition 表頭三欄：引用（Stage 1 原文片段）／去向五值／下落。full 必有 `## Real-world Disposition`。本方案處理 → 下落匹配 `R-` 或 `S-`（Decision 4A）；禁第二鏈編號 | 4A 不另發第二鏈；G2 要看到下落 | `3-prototype.md` 4A；`1-discussion.md:117` | 改發第二鏈編號 = 已拒 4B | 待人審 |
| DD-5 | evidence manifest 節名 = `## Evidence manifest`，住 `1-discussion.md` 同檔。五欄字面鎖定 Stage 3。talk 期判定 = 既有 talk 游標檔存在。核准 ∈ {是, 未核, 禁}；是不能覆寫 2–7 禁令 | 6A 改允許集合；5A 已拒另造永久檔；B 把同一成本加到另檔 | `3-prototype.md` 6A；`2-decision.md` 6A | 改另檔 manifest = 採 Variant B，已棄 | 待人審 |
| DD-6 | lookback 四欄字面鎖定「回看日期／回看 owner／資料來源／低於何值重開」。填檔牙只在 7-review 已出現回看節或四欄名時發動；舊檔無節不誤殺 | 5A 約定在 Exit、結果走 HISTORY | `3-prototype.md` 5A；`2-decision.md` 5A | 改永久 lookback 檔 = 已拒 5C | 待人審 |
| DD-7 | Human verdict 一行鎖定 `<ENUM> \| role=<Actors 表角色> \| scenario=<AC-id 或 Demo Script 場景名>`。ACCEPTED 仍要既有 attestation。本包不加 Actor Coverage 全表 | Owner 已裁 LIGHT；只留 attestation 看不出驗了誰 | `3-prototype.md` 8A；`1-discussion.md:114` | 改全表 = 已拒 8B | 待人審 |
| DD-8 | Feature Risk = high。本 hop `verdict` 留空，由人類 G2 填。implementer 不得寫 PASS。Stage 3 依 owner brief 2026-09-13 當 ACCEPTED 對帳，不代填 attestation | 公開檢查契約 + 討論期讀取權限 + 過期假設假綠；四眼原則 | `_templates/4-spec.md` Risk 判準；本 hop brief「no G2 PASS invented」 | 改 normal 則 Failure Model 改選配；代填 PASS = 假綠 | 待人審 |

### 內部技術選擇(下層,告知即可)
- spec-gate 新項與 C1–C6 同檔；項次建議 C7 Assumption refs、C8 Fast triage、C9 disposition。落地時改腳本頂註「六項」為實際項數。
- realworld 每加一條 `check()` 必須把 `MIN_CHECKS` 改成當下實數，不是寬放下限。
- guard Read 只認既有 talk 游標檔；游標不在則維持今日只掃 `skills/dev-talk/*` 寫入洩漏。
- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `docs/dev/STATUS.md` 正本表列、不 bump plugin、不開 5-tasks。
- 本 hop 不落地 Stage 6 守衛碼；形狀以 R/S 為準。
- 負向 fixture 目錄建議 `scripts/fixtures/discovery-gaps/`（Stage 6 才新增檔）。

## Test Skeletons(選配)

- `test_s_1_1_template_splits_goals_and_requested`
- `test_s_1_2_dashboard_in_goals_flagged_wrong_column`
- `test_s_1_3_example_goals_drop_channel_as_goal`
- `test_s_1_4_domain_word_dashboard_not_blacklisted`
- `test_s_2_1_discover_path_drops_recommend_hard_rule`
- `test_s_2_2_deleting_one_prefix_fails_static_tooth`
- `test_s_2_3_decision_question_may_offer_options`
- `test_s_3_1_high_impact_missing_source_and_deadline_fails`
- `test_s_3_2_source_or_deadline_passes`
- `test_s_3_3_nod_as_only_source_fails`
- `test_s_3_4_enum_outside_set_fails`
- `test_s_3_5_non_high_impact_context_without_enum_passes`
- `test_s_4_1_expired_open_assumption_spec_gate_fails`
- `test_s_4_2_resolved_assumption_spec_gate_passes`
- `test_s_4_3_oc_accepted_assumption_spec_gate_passes`
- `test_s_4_4_template_example_assumption_four_columns`
- `test_s_5_1_accepted_without_role_scenario_fails`
- `test_s_5_2_complete_verdict_line_passes`
- `test_s_5_3_no_actor_coverage_table_required`
- `test_s_6_1_missing_or_blank_disposition_fails`
- `test_s_6_2_handled_row_requires_s_id`
- `test_s_6_3_other_dest_requires_oos_limit_or_slug`
- `test_s_6_4_no_rw_second_chain`
- `test_s_7_1_template_example_lookback_four_fields`
- `test_s_7_2_shipped_lookback_missing_field_fails`
- `test_s_7_3_result_uses_history_append_not_new_file`
- `test_s_8_1_approved_path_readable`
- `test_s_8_2_solution_files_still_denied`
- `test_s_8_3_unapproved_path_not_authorized`
- `test_s_8_4_ticket_solution_not_a_fact`
- `test_s_9_1_fast_blank_triage_fails`
- `test_s_9_2_wait_shown_as_done_hits_q3`
- `test_s_9_3_hit_without_destination_fails`
- `test_s_9_4_visual_all_no_may_stay_fast`
- `test_s_9_5_full_lane_without_triage_not_killed`

## 確認紀錄
- 雙源清點 | 2026-09-13 | 驗收雛形 AC-1～AC-9 共 9 條 → ADDED R-1～R-9。living spec `docs/specs/` 0 條。活教師十一句進 MODIFIED M-1～M-11。Decision 剩餘 = 1A–8A 欄位與牙射程
- R 範圍 | 2026-09-13 | Implementer A 依 brief：九條 ID 各一 R；1A+2A+3A+4A+5A+6A+7A+8A 不重開。範圍 = 同檔欄位形狀 + 延既有三支牙；排除本 hop 改模板正本、STATUS／HISTORY、G2 PASS、Stage 5+
- S 展開 | 2026-09-13 | R-1～R-9 全展開；每 S 有觀測欄；交接／核准／等待／系統外動作的 S 有 Operational Context
- 3a 四節 | 2026-09-13 | AC／Out of Scope／Diff Budget／Dependencies 齊
- 3b Profile | 2026-09-13 | lane full、Risk high、Failure Model、Reliability triage、Design Boundary applicable
- 3c Stage 3 | 2026-09-13 | AC-1～AC-9 + Method + Recovery 逐場有下落；Human ACCEPTED 依 owner brief 2026-09-13
- DD 掃描 | 2026-09-13 | 上層八條待人審；無「未決」殘留字；不翻已核 Decision；全文無未定三詞
- G2 verdict | 2026-09-13 | 留空等人審；不發明 PASS
