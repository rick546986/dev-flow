---
feature: requirement-discovery-gaps
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 1. 討論 — 需求發現九條制度缺口

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 Owner Call 與書面 brief 落檔,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1、不送 G1**。未核敘述標 `[Assumption]`。
> A-1 已裁:Goals 只寫人的結果;Requested solution 另節、未定案。
> 九條一包:A-1～A-4／A-6／A-7／B-1／B-2 **DO**;A-5 **LIGHT**。審核區只當原料,本 hop 不施工。

## Problem
痛:用 DevFlow 開需求時,討論 agent 與發起人常把「我要一個 dashboard」寫進 Goals／驗收;發現題先附推薦答案;主張沒連來源;高影響假設能合法帶到 G2;Journey 痛點在 Stage 2→4 靜默消失;G3 全綠也不回答真實問題有沒有改善;Fast lane 因檔少跳過 Stage 1–3,人機風險到 Stage 4 才碰。流程可以全綠,卻解錯問題。
現在怎麼繞:owner 口頭把解法從 Goal 拆開;G1/G2 reviewer 靠經驗抽查證據;Fast lane 開工 agent「自己知道」該不該升 full;出貨後沒有指定回看。

## Context(已知事實)
- 本討論基準 plugin `3.23.4`:.claude-plugin/plugin.json:L3
- 2026-09-12 Owner Call 鎖定九條一包(A-1～A-4／A-6／A-7／B-1／B-2 DO;A-5 LIGHT);落點與機械守衛留給後續 G1/G2,審核區不是施工單:notes/review-requirement-discovery-gaps.md:L16-L30 notes/review-requirement-discovery-gaps.md:L326-L342
- Backlog 仍寫「九條已裁、實作另開後續 feature」;本檔只在 main 維護,feature branch 不碰:docs/dev/STATUS.md:L10-L26 docs/dev/STATUS.md:L49
- Stage 1 模板明文「不做決定」,驗收雛形卻把畫面路徑／API 端點列進固定骨架:_templates/1-discussion.md:L12 _templates/1-discussion.md:L91-L98
- 驗收雛形要問「從哪裡看(畫面/端點/檔案/log)」;Stage 4 把該觀測方式升成每條 S:skills/dev-talk/nodes/S4-accept.md:L19-L22 _templates/4-spec.md:L56-L61
- 完整範例 Goals 已指定登入／點擊／一眼可見;AC 鎖 dashboard、卡片、URL;Interview Log 在 Stage 1 就結論「dashboard 是最低成本呈現面」:example/contract-expiry-reminder/1-discussion.md:L62-L65 example/contract-expiry-reminder/1-discussion.md:L83-L103 example/contract-expiry-reminder/1-discussion.md:L115-L118
- 發現題與裁決題未分流:逐題逼問硬規則是「一次只問一題、附推薦答案」;完成條件是「連續兩輪無新問題」:skills/dev-talk/nodes/N3-probe.md:L22-L26 skills/dev-talk/nodes/N3-probe.md:L39-L41
- 同一條鏈又要採集最近一次真實行為、workaround、exception、evidence:skills/dev-talk/nodes/S2-world.md:L20-L34
- 使用者認可後的清單直接當「已核事實」:skills/dev-talk/nodes/S1-survey.md:L28-L29
- Stage 1 只要求 Evidence 列表與 `[Assumption]` 二分;守衛只驗章節／表頭存在、範例有 `[Assumption]` 與「訪談」字樣: _templates/1-discussion.md:L48 _templates/1-discussion.md:L72-L73 scripts/check-realworld.sh:L71-L91
- `[~]` 帶假設是合法終態;Stage 2 接手只核 status 與 OQ 三態,從 Goals／驗收雛形／`[>]` 提煉決策點: _templates/1-discussion.md:L82-L86 _templates/2-decision.md:L35-L37
- Stage 2 自檢要求 Decision 覆蓋 Goals、Success Criteria 可量測;未要求逐條處置 Journey 痛點／workaround／exception:_templates/2-decision.md:L42-L44 _templates/2-decision.md:L59-L60
- Stage 4 有驗收雛形→R/S 與 Stage 3 Scenario 對帳,沒有 Stage 1 Real-world → Decision／R/S 對帳;realworld 守衛已替 Stage 3 補逐場點名:_templates/4-spec.md:L56-L76 scripts/check-realworld.sh:L215-L232
- Human verdict 要 Participants 自由文字與人類 attestation;機械保證「不是 Agent 代填」,不保證角色對得上 Demo Script: _templates/3-prototype.md:L108-L129 scripts/check-realworld.sh:L121-L151
- Stage 7 Operational Walkthrough 由 reviewer 代入角色走查;PASS 是出貨前驗證;Exit Checklist 無上線後回看日期／owner／門檻:_templates/7-review.md:L146-L150 _templates/7-review.md:L167-L181 _templates/7-review.md:L316-L342
- 範例 Problem 自發寫了每季漏 2-3 件與約 8,000 筆,模板 Problem 只要求誰／痛／繞:example/contract-expiry-reminder/1-discussion.md:L12-L19 _templates/1-discussion.md:L33-L34
- 讀取白名單:長期記憶入口、`docs/specs/`、原始碼、使用者**已指名**的檔;文件類資料夾不列目錄。S2 卻期待 Evidence 含案例／辦法／log／表單／畫面:skills/dev-talk/SKILL.md:L17-L21 skills/dev-talk/nodes/S2-world.md:L30-L31
- Fast lane 跳過 Stage 1–3,從 4-spec 起跑;無 1/3 檔判 legacy/N-A 放行:skills/dev-flow/SKILL.md:L35-L36 guides/guide-dev-flow.html:L663-L667 skills/dev-flow/SKILL.md:L126-L128
- Stage 4 才寫「高風險人機互動」自動升 Full;lane 已在進 Stage 4 前選完:_templates/4-spec.md:L266-L269
- Stage 1 固定產 md + 審頁 html;審頁走 `build-stage1-html.py --action`,不要手包 html-shell:_templates/1-discussion.md:L13-L20 notes/design/stage1-review-ui-contract.md:L15-L20
- Context 出處語法只有 `path:L起` 或 `path:L起-L迄`:_templates/1-discussion.md:L36-L39
- owner 2026-09-13 書面 brief:slug `requirement-discovery-gaps`;單一 full-lane 包九條;本 hop 只 Stage 1、不送 G1;不改模板／技能／範例／STATUS;與 A/B 獨立實作
- Problem 最小 baseline(A-7 形;無採用現場量測則標 Unknown,不捏造):受影響者=討論 agent／發起人／owner／G1/G2 reviewer／Fast lane 開工 agent／第一線操作員(常沒被訪);事件量=Unknown(無採用專案 log);影響=全綠仍解錯問題;觀測期間=2026-08-17→2026-09-12;來源=notes/review-requirement-discovery-gaps.md:L16-L30

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 需求發起人 | 把手上痛趕快做成功能 | 提需求、點頭確認討論 | 自己要的畫面／捷徑 | 真正痛是不是資料／SOP／權責 | 口頭、PR、ticket |
| 討論 agent | 把討論寫成可收斂的 1-discussion | 讀白名單;寫本 slug 討論檔 | 模板骨架、skill 節點 | 未指名的 SOP／ticket／log | 編輯器、終端機 |
| owner | 九條依 Owner Call 落地,不全綠卻解錯 | 裁 lane／G1–G3、核准證據入口 | 2026-09-12 裁決、本 tree | 採用現場是否仍這樣敗 | GitHub、審核區 |
| G1/G2 reviewer | 方向與 R/S 真的對得上現實 | 退回 Stage 1／擋 G2 | 討論檔與 Decision | 主張是否真有來源;痛點去向 | 瀏覽器、PR |
| 第一線操作員 | 工作做完、少漏件、少等人 | 常無討論權;系統外或只操作 | 最近一次真實做法 | 討論有沒有訪到自己 | Excel、LINE、Email |
| Fast lane 開工 agent | 小修快出、檔少就走 fast | 選 lane、寫 4-spec | 檔數／bugfix 標籤 | 這次改不改下一步／權限／等待語意 | 終端機、diff |

### Current Journey
正式 SOP:full 走 `/dev-talk` 收 Real-world,Stage 1「不做決定」;Stage 2 從 Goals／雛形收斂;Fast lane 省 Stage 1–3,從 4-spec 起。
實際:發起人帶來通道;agent 寫進 Goals／AC;發現題附推薦;認可升格事實;Fast lane 用檔少當判準。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 需求發起人 | 帶「我要 dashboard／按鈕」來開討論 | 口頭、brief | 討論 agent | 解法已在提問裡 | 問題被通道綁死 |
| 2 | 討論 agent | 把想法寫進 Goals／AC;發現題附推薦答案 | 模板、N3-probe | 發起人點頭 | 1-discussion 形狀齊 | 現況被理想流程取代 |
| 3 | 討論 agent | 只讀白名單與已指名檔;Evidence 靠口述 | skill 白名單 | owner 若要補檔 | 形式完整、來源偏一人 | 上游事實進不來 |
| 4 | G1 reviewer | 核 Goals 覆蓋與方案依據 | 2-decision | owner | Decision 對齊 Goals | Journey 痛點未處置 |
| 5 | Stage 4 作者 | 雛形觀測升成 S;Fast 直接寫 bug scenario | 4-spec | G2 | R/S 綁早期通道 | 人機風險此時才寫 |
| 6 | owner | 看 G3 全綠當出貨 | 7-review | — | PASS／shipped | 真實問題沒量、沒回看 |

### Workarounds
- owner 口頭說「那是 Requested solution,不是 Goal」;模板沒有這欄,下一個 agent 仍照範例寫通道。
- reviewer 重讀原始碼／自己記的 ticket,重建證據強度;系統只驗「有 Evidence 字樣」。
- 人記得問「ACCEPTED 是誰按的、哪個場景」;Human verdict 沒有角色／場景欄,靜默當全覆蓋。
- Fast lane 開工 agent「自己知道」該升 full;沒有進 Stage 4 前的結構化 triage。
- 母版近稿(integration-before-verdict、diagram-ir-gate)已自發加 Requested solution 節;這是人記 A-1,不是模板契約。
- 這些步驟常不留「哪條痛點被刻意不處理」的紀錄。

### Exceptions
- 已有 approved spec、只改視覺、不改權限／等待／交接語意的 bug,Owner Call 允許維持 fast,不必硬拖進訪談。
- 外部窗口／系統外核准者常無法直接 Demo;A-5 LIGHT 只要 Human verdict 一行寫清角色／場景,不在本輪做 Actor Coverage 全表。
- `[~]` 帶假設可把 Stage 1 標 approved;高影響假設(權限／法規／金流／資料隔離／外部承諾)目前沒有過期擋 G2。
- 誰都可以跳過 Real-world 深問、只填表頭;realworld 守衛仍綠。
- `[Assumption]` 採用現場仍把功能想法寫進 Goals、發現題仍附推薦、Fast lane 仍只看檔數(無採用專案 log;風險=高,會讓本包改錯層;期限=Stage 2 對帳,過期擋 G2)。

### Evidence
- owner 書面 brief(本 session 2026-09-13):slug `requirement-discovery-gaps`;九條一包;A-5 LIGHT 其餘 DO;full lane;只 Stage 1、不送 G1;不改模板／技能／範例／STATUS;與 A/B 獨立。
- Owner Call 正本:notes/review-requirement-discovery-gaps.md:L16-L30 notes/review-requirement-discovery-gaps.md:L326-L342
- 審核區分析原文(原料,非施工單):notes/review-requirement-discovery-gaps.md:L39-L324
- 已核文件:上列 Context 出處(本 working tree 讀過)。
- 範例漂移:example/contract-expiry-reminder/1-discussion.md:L62-L65 example/contract-expiry-reminder/1-discussion.md:L83-L103
- 母版近稿已示範 A-1 分欄:docs/dev/integration-before-verdict/1-discussion.md:L76 docs/dev/diagram-ir-gate/1-discussion.md:L95
- `[Assumption]` 採用現場仍這樣敗:無 log;風險=高;期限 Stage 2;過期擋 G2。

## Goals
- G-out-1:討論結束時,人能分開「要改善的工作結果」與「帶來的功能想法」;後者不能當已選定解法。
- G-out-2:蒐集現況／案例／例外／證據時,受訪者不被模型先給的答案錨定。
- G-out-3:高影響主張能回到來源,或帶期限的 Assumption;使用者點頭不升格證據。
- G-out-4:高影響 Assumption 過期未驗時,不能進 G2。
- G-out-5:Human verdict 看得出是哪個角色、哪個場景按的(本輪 LIGHT,不要求全角色覆蓋表)。
- G-out-6:Stage 1 盤到的高影響痛點／workaround／exception,到 Stage 4 時每條有去向,不能無聲消失。
- G-out-7:出貨後有人在指定日期回看真實問題有沒有改善;低於門檻要重開。
- G-out-8:事實型證據在 owner 核准後能被讀到,同時仍禁讀下游方案檔。
- G-out-9:Fast lane 進 Stage 4 前已做過人機互動風險盤點;命中時有升 full／mini／Owner Call,不能只因檔少就跳過。

## Requested solution（候選，未定案）
- Goals 與 Requested solution 分欄;驗收雛形只寫人看見的結果,不鎖畫面／API／元件;Stage 2 原因仍可能由流程／政策／資料品質解決時,比較 no-build／process-only(不合理可註明,不硬塞)。
- 發現題禁附推薦答案;裁決題(已核事實上的取捨)可附選項／差異／推薦。完成條件改看必查面／反例／證據缺口,兩輪無新問題只當輔助訊號。
- 主張就地標 Observed／Reported／Inferred／Assumption／Conflict;Evidence 最小結構含來源類型、as-of、範圍、支持哪段、限制;點頭 ≠ 升格。
- 每個高影響 Assumption／`[~]` 寫風險、影響級、怎麼驗、何時／由誰驗;過期擋 G2。
- Human verdict 一行寫清角色／場景(A-5 LIGHT);不在本輪做 Actor Coverage 全表。
- Stage 2→4 disposition ledger:高影響痛點／workaround／exception 逐條標 addressed／刻意維持／Non-Goal／另開 slug／仍待驗證。
- 出貨後 improvement lookback:日期、owner、資料來源、低於何值重開;落點用既有 HISTORY／7-review 附錄,不另造無人維護的永久檔。
- 保留禁讀 2/3/4/5/6/7 與方案檔;另開事實型 evidence 入口,owner 核准後才讀。
- Fast lane 進 Stage 4 前做 early risk triage(下一步／權限／等待語意／交接／系統外／中斷恢復);命中則升 full 或 fast+mini real-world delta,或 Owner Call。
- 本 hop 不選定各條落在 skill／模板／守衛／範例的哪一句,也不選定機械化深度。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`skills/`、`example/`、`docs/dev/STATUS.md`、`HISTORY.md`。
- 本 hop 不送 G1、不實作守衛、不 bump plugin。
- 不重開 Owner Call;不把九條拆成九個 slug。
- 不做 A-5 Actor Coverage 全表。
- 不另發 Journey／Actor／Interaction 第二條 ID 鏈。
- 不動開著或已合的 integration-before-verdict／diagram-ir-gate 施工;不把本包混進「四項已定」驗收。
- 不用 `dashboard`／`API` 黑名單當 Goal 語意守衛(會誤殺合法領域詞)。
- 不掃未授權的私密資料夾或外部 connector。

## Open Questions
- [x] Q1:lane 是否 full?→ owner:full
- [x] Q2:九條是否單一 full-lane 一包?→ owner:是
- [x] Q3:A-5 是否 LIGHT、其餘是否 DO?→ Owner Call 2026-09-12:是;不重開
- [x] Q4:本 hop 是否送 G1、是否改模板／技能／範例／STATUS?→ owner:只 Stage 1;不送 G1;不改那些檔
- [x] Q5:審核區是否施工單?→ 否;只當證據／原料
- [~] Q6:採用現場是否仍把功能想法寫進 Goals、發現題仍附推薦、Fast 仍只看檔數?(帶假設:是;無採用專案 log;風險=高;期限=Stage 2 對帳,過期擋 G2)
- [>] Q7:各條落點(skill／模板／守衛／範例)與「形狀牙 vs reviewer 語意」邊界 → 移交 Stage 2
- [>] Q8:Stage 2 no-build／process-only 適用性判定怎麼寫、不合理時如何註明 → 移交 Stage 2
- [>] Q9:lookback 落 HISTORY 還是 7-review 附錄、到期未回看如何顯性化 → 移交 Stage 2
- [>] Q10:evidence allowlist 與現有白名單／`devtalk-guard` 怎麼對齊,才不會「規定了但讀不到」 → 移交 Stage 2
- [>] Q11:Fast lane mini real-world delta 的最小欄位與 Owner Call 形 → 移交 Stage 2

## Constraints
- 表列只准 `scripts/status-update.sh` 且必須在 `main`;本 feature branch 不改 `docs/dev/STATUS.md`。
- HISTORY 只准 `history-append.sh`;本 hop 不追加。
- 本 PR 不宣稱 G1 PASS;status 留 draft;Owner Call／gates 留給人。
- 與 A/B 獨立落檔,不抄他稿當正本。
- 人看討論用繁中;ID／R／S／T 維持英式。
- 後續若命中 Stage 3:Human verdict 一行寫角色／場景(A-5 LIGHT),不在本 hop 做。
- 高影響 `[Assumption]`(Q6)未在期限內驗證 → 擋 G2。

## 驗收雛形
- AC-1(G-out-1):假設發起人帶著「我要一個 dashboard」來開討論,當討論落檔完成,則 Goals 只寫人的工作結果,功能想法在 Requested solution 且標未定案。
  - 從哪看:該 feature 的 1-discussion Goals 節與 Requested solution 節
  - 看到什麼算對:Goals 沒有指定畫面／端點／元件;Requested solution 可以有,且標未定案。不是「Goals 寫了 dashboard 但加一句之後再說」
  - 拿什麼試:本 slug 這份討論;或一份故意把 dashboard 寫進 Goal 的對照稿
- AC-2(G-out-2):假設正在問「最近一次真的怎麼處理」,當問題仍屬發現題,則題目不附推薦答案。
  - 從哪看:該場 Interview Log 的高影響發現題,以及後續 skill／指南對發現題／裁決題的對稱措辭
  - 看到什麼算對:發現題是開放問;推薦只出現在事實被覆述確認之後的裁決題。不是「連續兩輪無新問題」當充分完成條件
  - 拿什麼試:本場 Log 的發現題;後續再抽一份採用討論的高影響題
- AC-3(G-out-3／G-out-4):假設有一條會改變權限／金流／外部承諾的主張,當它不是直接查到的事實,則必須連到來源,或標 Assumption 並寫風險與驗證期限;期限過了仍未驗,則不得進 G2。
  - 從哪看:1-discussion 該條主張＋Open Questions `[~]`;後續 G2 送審紀錄
  - 看到什麼算對:看得到來源或「風險＋期限＋誰驗」;過期仍帶著送 G2 會被退回。點頭本身不把狀態改成 Observed
  - 拿什麼試:本檔 Q6;再造一條無來源、無期限的高影響假設對照
- AC-4(G-out-5):假設有人填了 Human verdict = ACCEPTED,當人讀那一行,則看得出是哪個角色、哪個場景按的。
  - 從哪看:3-prototype(或同等 Demo 回饋)的 Human verdict 行
  - 看到什麼算對:角色名與場景各至少一個非空;不是只有 attestation 日期。本輪不要求 Actor Coverage 全表
  - 拿什麼試:後續命中 Stage 3 的本 slug Demo;或一份只填 attestation、沒寫角色／場景的對照
- AC-5(G-out-6):假設 Stage 1 列了高影響痛點／workaround／exception,當 Stage 4 定稿,則每條都有去向。
  - 從哪看:Stage 2 disposition 與 Stage 4 Out of Scope／R/S／Known limit／後續 slug
  - 看到什麼算對:「本方案處理」至少落到一條 R/S;其餘落到 Non-Goal／limit／另開 slug／仍待驗證,並有理由。不是表在但列空
  - 拿什麼試:本檔 Journey Step 4–6 與 Exceptions 的代理核准／共管重複／Fast 跳過
- AC-6(G-out-7):假設 feature 已標 shipped,當人打開出貨紀錄,則看得到回看日期、owner、資料來源、低於何值要重開。
  - 從哪看:出貨紀錄(既有 HISTORY 或 7-review 附錄;落點 Stage 2 定)
  - 看到什麼算對:四欄都在;低於門檻的動作是重開討論／回滾／另開 feature 之一。G3 PASS 本身不算 outcome 已改善
  - 拿什麼試:本 slug 後續自己走到 Stage 7;或一份 Exit 全勾卻沒有回看欄的對照
- AC-7(G-out-8):假設 owner 已核准一類事實型證據(例如去識別化 incident／SOP),當討論 agent 要採 Evidence,則核准後讀得到,且仍讀不到 2/3/4/5/6/7 與方案檔。
  - 從哪看:該場 Evidence 來源列＋讀取紀錄(允許清單或等同授權)
  - 看到什麼算對:核准來源出現在 Evidence,並標限制;未核准路徑與下游方案檔仍被擋
  - 拿什麼試:owner 指名一份 SOP／去識別化 log;對照讀 2-decision 應被擋
- AC-8(G-out-9):假設有人要把「只改一個狀態字」走 Fast lane,當該改動會改下一步／權限／等待語意／交接／系統外／中斷恢復之一,則進 Stage 4 前已有 triage 結果,且命中時有升 full、mini delta 或 Owner Call。
  - 從哪看:進 Stage 4 前的 triage 紀錄(後續落在 4-spec 或更早的最小盤點;形狀 Stage 2 定)
  - 看到什麼算對:六項有是／否;命中卻無 full／mini／Owner Call 不得當合法 fast。不是只寫「檔數 ≤2」
  - 拿什麼試:一份故意改等待語意、檔數只有一的對照;再對一份純視覺、不改語意的 bug

## 現況圖
誰:討論 agent
做什麼:把功能想法寫進 Goals
工具:模板+skill
痛點:解法在 G1 前鎖死
↓
誰:G1/G2 reviewer
做什麼:只核 Goals 覆蓋
工具:2-decision
痛點:痛點靜默消失
↓
誰:owner
做什麼:看 G3 全綠出貨
工具:7-review
痛點:真實問題沒量

## 邏輯圖(ASCII)
```
now
|-- discovery (full)
|   |-- requested channel -> Goals / AC
|   |-- probe + recommended answer
|   |-- nod => verified fact
|   +-- [~] assumption may reach G2
|-- stage 2-4
|   |-- decide from Goals / AC / [>]
|   +-- X no disposition of journey rows
|-- ship
|   |-- G3 greens on S / tests
|   +-- X no outcome lookback
+-- fast lane
    |-- skip stage 1-3
    |-- triage only inside 4-spec
    +-- file-count / bugfix as proxy
```

## Interview Log(推理鏈外顯)
- Q:為什麼 Stage 1 說不做決定,驗收雛形仍會在 G1 前鎖死解法?
  - 事實:_templates/1-discussion.md:L12 _templates/1-discussion.md:L91-L98 skills/dev-talk/nodes/S4-accept.md:L19-L22 _templates/4-spec.md:L56-L61 example/contract-expiry-reminder/1-discussion.md:L62-L65
  - 推理:「從哪看」把畫面／端點寫進固定骨架;Stage 4 再升成 S。範例已示範 Goals／AC 鎖 dashboard。使用者帶來的通道會變成可測契約,Stage 2 只剩「怎麼做這個功能」。
  - 結論:CONFIRMED 要分欄:Goals 只寫人的結果;Requested solution 另節未定案;本檔 AC 只觀測討論／gate 產出上的人可見結果,不鎖產品畫面／API／元件。
- Q:為什麼「每題附推薦答案」會污染對真實行為的發現?
  - 事實:skills/dev-talk/nodes/N3-probe.md:L22-L26 skills/dev-talk/nodes/S2-world.md:L20-L34 skills/dev-talk/nodes/N3-probe.md:L39-L41
  - 推理:同一條逼問鏈既要採集最近一次真實做法,又要先給推薦。受訪者容易確認模型敘事,而不是回想上次真的怎麼做。「兩輪無新問題」是 agent 自己可提前達成的停止條件,補不了錨定。
  - 結論:CONFIRMED 發現題禁推薦、裁決題可附;完成條件應看必查面／反例／證據缺口。對話語意不值得假裝有硬 gate。
- ⚠️ Q:使用者點頭是不是就把主張升成已核事實?
  - 事實:skills/dev-talk/nodes/S1-survey.md:L28-L29 _templates/1-discussion.md:L48 scripts/check-realworld.sh:L71-L91 _templates/2-decision.md:L39-L41
  - 推理:認可是確認理解或相關性,不是驗證原始碼／營運數字的能力。守衛只驗有 Evidence／Assumption 字樣。Stage 2 只要引用「事實」就能替方案背書。
  - 結論:CONFIRMED 點頭 ≠ 證據升格;主張必須連到來源,或 Assumption＋期限。本檔 Context 只收本 tree 讀過且行段支持的斷言。
- ⚠️ Q:高影響假設現在能不能合法一路帶到 G2?
  - 事實:_templates/1-discussion.md:L82-L86 _templates/2-decision.md:L35-L37 _templates/4-spec.md:L56-L61
  - 推理:`[~]` 是合法終態。Stage 2 不查假設是否改權限／法規／金流／方向。Stage 4 也沒有「本 S 依賴哪條未驗假設」。假前提上的測試仍可讓 G3 綠。
  - 結論:CONFIRMED 高影響 Assumption 要寫風險＋期限;過期擋 G2。本檔 Q6 就是這類假設。
- Q:為什麼 A-5 只做 LIGHT、不在本輪做 Actor Coverage 全表?
  - 事實:notes/review-requirement-discovery-gaps.md:L26 _templates/3-prototype.md:L108-L129 scripts/check-realworld.sh:L121-L151 _templates/7-review.md:L146-L150
  - 推理:現況機械只保證「有人按過、不是 Agent」。owner 已裁本輪只要 verdict 一行寫清角色／場景。外部角色常無法直接 Demo,全表會把本包拖成第二條 ID 鏈。
  - 結論:CONFIRMED A-5 LIGHT:verdict 看得出誰、哪個場景;不在本輪做 coverage 全表。
- ⚠️ Q:真實世界列為什麼能在 Stage 2→4 靜默消失?
  - 事實:_templates/2-decision.md:L36-L37 _templates/2-decision.md:L59-L60 _templates/4-spec.md:L56-L76 scripts/check-realworld.sh:L215-L232
  - 推理:決策點從 Goals／雛形／`[>]` 來,自檢只問 Goals 覆蓋。Stage 3 場景已有逐場點名牙,Stage 1 痛點沒有同級保護。Goals 只寫 happy path 時,代理不補知會、共管重複聯絡可以無聲消失。
  - 結論:CONFIRMED 要 disposition ledger,不另發 Journey ID。標「本方案處理」者落到 R/S;其餘落到 Non-Goal／limit／另開 slug。
- Q:G3 全綠能不能證明真實問題有改善?
  - 事實:_templates/1-discussion.md:L33-L34 _templates/2-decision.md:L42-L44 _templates/7-review.md:L167-L181 _templates/7-review.md:L316-L342 example/contract-expiry-reminder/1-discussion.md:L12-L19
  - 推理:PASS／Exit 全是出貨前驗證。範例自發寫了漏件量級,模板不強制,AC 仍只驗卡片。shipped 之後沒有日期／owner／門檻。
  - 結論:CONFIRMED 出貨後必留 lookback;G3 綠 ≠ outcome 改善。本檔 Problem 已用 Unknown 標採用現場量,不捏造數字。
- ⚠️ Q:為什麼事實進不來,而 Fast lane 的人機風險又來得太晚?
  - 事實:skills/dev-talk/SKILL.md:L17-L21 skills/dev-talk/nodes/S2-world.md:L30-L31 skills/dev-flow/SKILL.md:L35-L36 skills/dev-flow/SKILL.md:L126-L128 _templates/4-spec.md:L266-L269 guides/guide-dev-flow.html:L663-L667
  - 推理:圍欄擋住下游方案是對的,但同時擋住未指名的 SOP／ticket／log。Fast lane 合法跳過 1–3,「高風險人機互動」寫在已選定 lane 之後的 4-spec;檔少／bugfix 可讓等待語意被改掉卻沒有 Actors／Demo。
  - 結論:CONFIRMED B-1 要 owner 核准的事實入口、仍禁讀方案檔;B-2 要進 Stage 4 前的 early triage。兩者的形狀牙留給 Stage 2,本 hop 不定稿。
