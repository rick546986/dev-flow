---
feature: requirement-discovery-gaps
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 1. 討論 — 需求發現九條制度缺口

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 書面 Owner Call 落檔,不是現場一問一答。
> Lane = **full**。本 hop **不送 G1**。未核敘述標 `[Assumption]`。
> A-1 已裁:Goals 只寫結果;Requested solution 另節。本檔自己先照做。
> 原料:`notes/review-requirement-discovery-gaps.md`(2026-09-12 已裁;不是施工單)。

## Problem
痛:方法論能讓七關全綠,卻解錯真實問題——Goals 鎖解法、發現題先塞推薦答案、痛點在 Stage 2→4 靜默消失、出貨後沒人回看真實指標。
受影響:母版維護者與採用專案訪談對象。頻率:每條 full 討論、每條 fast 的 4-spec。影響:流程全綠但原問題仍在。觀測窗:2026-08-17 盤點至 2026-09-12 裁決。來源:notes/review-requirement-discovery-gaps.md:L16-L30 與本 tree 核對。採用專案出貨後真實問題是否改善 = Unknown(現制沒有回看落點)。
現在怎麼繞:owner 用審核筆記人工記缺口;現場靠一人記憶轉述;Fast 跳過 Stage 1–3 直接寫 4-spec。

## Context(已知事實)
- Owner Call 2026-09-12 九條已裁:A-1…A-4/A-6/A-7/B-1/B-2 = DO,A-5 = LIGHT;實作另開 feature,本檔不是施工單:notes/review-requirement-discovery-gaps.md:L16-L30 notes/review-requirement-discovery-gaps.md:L326-L342
- STATUS Backlog 已寫「九條已裁、實作另開」;HISTORY 把裁決與 `integration-before-verdict` 分開記:docs/dev/STATUS.md:L50 docs/dev/HISTORY.md:L500-L504
- Stage 1 明文「不做決定」,驗收雛形卻把「從哪看」候選鎖成畫面路徑／API 端點／檔案／log: _templates/1-discussion.md:L12 _templates/1-discussion.md:L91-L96
- 討論節點要求每條 Goal 問出「從哪裡看(畫面/端點/檔案/log)」;Stage 4 把雛形觀測方式升成 R/S:skills/dev-talk/nodes/S4-accept.md:L19-L22 _templates/4-spec.md:L56-L60
- 填好範例 Goals 已指定登入／點擊／一眼可見;AC 鎖 dashboard、卡片、URL;Interview Log 在 Stage 1 就結「dashboard 是最低成本的呈現面」:example/contract-expiry-reminder/1-discussion.md:L62-L65 example/contract-expiry-reminder/1-discussion.md:L83-L103 example/contract-expiry-reminder/1-discussion.md:L115-L118
- 逐題逼問硬規則是「一次一題、附推薦答案」;同一條鏈又要採最近一次真實行為。完成條件是「連續兩輪無新問題」:skills/dev-talk/nodes/N3-probe.md:L22-L23 skills/dev-talk/nodes/S2-world.md:L20-L34 skills/dev-talk/nodes/N3-probe.md:L41
- 使用者認可後的清單 = 已核事實;點頭即可升格:skills/dev-talk/nodes/S1-survey.md:L28-L29 skills/dev-talk/nodes/S1-survey.md:L41-L42
- Evidence 只要求列出處並以 `[Assumption]` 二分;real-world 牙只驗章節／`[Assumption]`／「訪談」字樣: _templates/1-discussion.md:L72-L73 scripts/check-realworld.sh:L88-L91
- 範例 Evidence 品質不差,但主張未逐條連到來源:example/contract-expiry-reminder/1-discussion.md:L54-L60
- Stage 2 用 1-discussion「事實」替方案背書;接手只核 status 與 OQ 三態,`[~]` 是合法終態: _templates/2-decision.md:L39-L41 _templates/2-decision.md:L35-L37 _templates/1-discussion.md:L82-L86
- Human verdict 要人類親填 + attestation,Participants 是自由文字;牙守「不是 Agent 代填」,不守角色／場景: _templates/3-prototype.md:L118-L129 skills/dev-flow/SKILL.md:L102-L105 scripts/check-realworld.sh:L137-L138
- Stage 2 從 Goals／驗收雛形／`[>]` 提煉決策,自檢只覆蓋 Goals 與移交;Stage 4 對帳 Stage 3 場景,不對帳 Stage 1 痛點列: _templates/2-decision.md:L35-L37 _templates/2-decision.md:L59-L60 _templates/4-spec.md:L72-L75 scripts/check-realworld.sh:L215-L231
- Problem 模板只要求誰／痛／怎麼繞;Success Criteria 只要求可量測;Exit 勾到 shipped,沒有出貨後回看: _templates/1-discussion.md:L33-L34 _templates/2-decision.md:L42-L44 _templates/2-decision.md:L102-L103 _templates/7-review.md:L316-L342
- 範例 Problem 自發寫了每季漏件與量級,但 AC 仍只驗卡片功能:example/contract-expiry-reminder/1-discussion.md:L12-L13 example/contract-expiry-reminder/1-discussion.md:L83-L103
- 討論讀取白名單 = 長期記憶／`docs/specs/`／原始碼／使用者已指名檔;文件夾不列不搜;S2 仍期待案例／SOP／log／表單／畫面:skills/dev-talk/SKILL.md:L17-L21 skills/dev-talk/nodes/S1-survey.md:L13 skills/dev-talk/nodes/S2-world.md:L30-L31
- `devtalk-guard` 只掃 `skills/dev-talk/*` 寫入是否洩漏下游字眼,不管事實型證據入口:hooks/devtalk-guard.sh:L16-L21
- Fast lane 省略 Stage 1–3,從 4-spec 起跑;無 1/3 檔判 legacy/N-A;「高風險人機互動」在 4-spec 才列自動升 Full,lane 已在進 Stage 4 前選完:skills/dev-flow/SKILL.md:L34-L36 skills/dev-flow/SKILL.md:L126-L128 guides/guide-dev-flow.html:L663-L667 guides/guide-dev-flow.html:L714-L715 _templates/4-spec.md:L266-L269
- 本 repo 已有 Fast 省略 1–3 的實例:docs/dev/engine-fence-masking/4-spec.md:L11-L12
- 受影響面(後續才動,本 hop 不動):`skills/dev-talk/` 節點、`_templates/1-discussion.md`／`2-decision.md`／`3-prototype.md`／`4-spec.md`／`7-review.md`、`scripts/check-realworld.sh`、`hooks/devtalk-guard.sh`、`example/contract-expiry-reminder/1-discussion.md`、`skills/dev-flow/SKILL.md` lane、`guides/guide-dev-flow.html#lanes`

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 討論 agent | 把模糊想法寫成可收斂討論 | 寫 1-discussion | 模板、skill、白名單 | 未指名的現場證據 | — |
| 訪談對象 | 被問「上次怎麼做」時不被錨定 | 系統外 | 自己上次真實做法 | 問題是否已帶推薦答案 | 口頭、Email |
| 收斂者 | 定方向且不漏高影響痛點 | 寫 2-decision | Goals、AC、`[>]` | Journey 痛點去向 | 2-decision |
| owner | 流程解對問題;出貨後知道有無改善 | 裁 OC／G1–G3 | 裁決表、本 tree | 採用現場是否照範例走偏 | GitHub、審核筆記 |
| Fast 實作者 | 小改快速出貨,不誤改權限／等待語意 | 寫 4-spec | 檔數少、已有 spec | 互動風險是否被改到 | 診斷迴圈 |
| G2 reviewer | 未驗的高影響假設能擋下 | 退回／擋 G2 | 4-spec、OQ 三態 | 哪個 Assumption 已過期 | 檢查腳本 |

### Current Journey
正式 SOP:full 走 Stage 1 Real-world Context → 2 →(3)→ 4;Fast 合法省略 1–3,從診斷迴圈進 4-spec。實際做法(無本包時)如下。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 討論 agent | 帶推薦問現況 | dev-talk | 訪談對象 | Interview Log | 發現被錨定 |
| 2 | 討論 agent | 認可後升已核事實 | S1-survey | owner | Context | 點頭當證據 |
| 3 | 收斂者 | 只收 Goal AC | 2-decision | — | Decision | 痛點消失 |
| 4 | owner | G3綠就出貨 | 7-review | — | shipped | 問題沒改善 |
| 5 | Fast 實作者 | 跳過 1–3 寫規格 | 4-spec | — | 4-spec | 互動風險晚露 |

### Workarounds
- owner 用 `notes/review-requirement-discovery-gaps.md` 人工記缺口;系統不擋「Goals 寫 dashboard」。
- 現場證據靠眼前使用者記憶轉述;未先說出路徑的 SOP／ticket／log 進不了白名單。
- Fast 直接寫 4-spec;互動風險等到 Verification Profile 才出現,lane 已選定。
- 人口頭記「先問現況、別先給答案」;N3 仍要求附推薦答案。
- 這些步驟常不留「這條痛點後來去哪」或「出貨後誰回看」的紀錄。

### Exceptions
- Fast lane 合法跳過 Stage 1–3;無 1/3 檔 → Stage 3 機械判 legacy/N-A。
- Owner Call 可明示跳過 Stage 3;A-5 本包只要求 verdict 一行角色／場景,不要求 Actor Coverage 全表。
- `[~]` 帶假設可把 Stage 1 標 approved;高影響假設目前能合法走到 G2。
- `[Assumption]` 採用現場仍照範例把解法寫進 Goal:無採用專案 log;風險=高(若為假,改範例優先級下降,但不改「Goals 鎖解法」的模板病);期限=Stage 2 對帳,過期擋 G2。
- `[Assumption]` 現場訪談仍在發現題附推薦答案:無逐字稿;風險=高(若為假,A-2 牙主要防未來漂移);期限=Stage 2,過期擋 G2。
- `[Assumption]` Fast 現場會因檔數少而漏判互動風險:本 repo 有省略 1–3 的實例,採用現場是否踩過權限／等待誤標 = 無 log;風險=高;期限=Stage 2,過期擋 G2。

### Evidence
- owner 書面 Owner Call(2026-09-12):九條裁決見 notes/review-requirement-discovery-gaps.md:L16-L30;本 hop 只 Stage 1、full、不送 G1、不解凍模板(本 session brief)。
- 盤點原料(2026-08-17／08-18,2026-09-12 改標已裁):notes/review-requirement-discovery-gaps.md 全文。限制:分析檔,不是採用現場訪談。
- 本 tree 已核:上列 Context 出處(2026-09-13 讀過,行段支持斷言)。
- Fast 省略 1–3 的本 repo 實例:docs/dev/engine-fence-masking/4-spec.md:L11-L12
- `[Assumption]` 三條見 Exceptions;皆無採用現場 log;期限 Stage 2,過期擋 G2。

## Goals
- G-out-1:人讀 Stage 1 時,能分辨「要達成的工作結果」與「帶來的解法構想」;構想不混成目標。
- G-out-2:人被問「上次真的怎麼做」時,問題本身不先塞推薦答案。
- G-out-3:高影響主張要嘛能回到可重開的來源,要嘛標 Assumption 且有驗證期限;點頭不把主張升格成證據。
- G-out-4:高影響 Assumption 到期仍未驗時,人進不了 G2。
- G-out-5:人看 Human verdict 時,能看出是哪個角色、哪個場景被驗過。
- G-out-6:Stage 1 記過的高影響痛點／workaround／exception,到 Stage 4 時每條都有去向,不能無聲消失。
- G-out-7:出貨後有人、有日、有來源、有「低於何值要重開」的回看;不是只證明功能做對。
- G-out-8:事實型證據在 owner 核准後能進討論;下游方案檔仍進不去。
- G-out-9:Fast lane 在寫 4-spec 之前,人已經看過這次改動是否碰到下一步／權限／等待／交接／系統外／中斷恢復。

## Requested solution（候選，未定案）
- Goals 與 Requested solution 分欄;驗收雛形不鎖畫面／API／元件;Stage 2 原因仍可能由流程／政策／資料品質解決時,比較 no-build／process-only(不合理可註明,不硬塞)。
- 發現題(現況／案例／例外／證據)禁附推薦答案;裁決題(已核事實上的取捨)可附選項／差異／推薦。
- 主張 → 來源,或 Assumption + 驗證期限;使用者點頭 ≠ 證據升格。
- 高影響 Assumption 寫風險 + 期限;到期未驗擋 G2。
- Human verdict 一行寫清角色／場景(A-5 LIGHT;不做 Actor Coverage 全表)。
- Stage 2→4 要有 disposition ledger:高影響痛點／workaround／exception 逐條標去向。
- 出貨後必留 improvement lookback(日期／owner／資料來源／低於何值要重開)。
- 另開 owner 核准的事實型 evidence 入口;仍禁讀下游方案檔。
- Fast 進 Stage 4 前做 early risk triage(下一步／權限／等待語意／交接／系統外／中斷恢復)。
- 同步改正完整範例,避免模板說結果、範例仍教解法。
- 本 hop 不選定改哪些守衛、欄位形狀、或 lookback 落哪一份檔。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`skills/`、`example/`、守衛、STATUS、HISTORY。
- 本 hop 不送 G1;status 留 draft。
- 不做 A-5 Actor Coverage 全表;不重開九條 DO／LIGHT。
- 不把九條拆成九個 slug;不混進 `integration-before-verdict`。
- 不新增第二條 Journey／Actor ID 鏈。
- 不把 ticket／SOP 裡的解法建議當事實。

## Open Questions
- [x] Q1:lane 是否 full?→ owner:full
- [x] Q2:九條是否一包?→ owner:一包,A-1…A-7、B-1、B-2
- [x] Q3:A-5 是否 LIGHT、其餘 DO?→ owner:是
- [x] Q4:本 hop 是否送 G1?→ owner:否,只 Stage 1
- [x] Q5:Goals 是否只寫結果、解法另欄?→ owner:是;本檔已照做
- [~] Q6:採用現場是否仍照範例把解法寫進 Goal?(帶假設:是;風險=高;期限=Stage 2 對帳,過期擋 G2)
- [>] Q7:各條機械牙落點(skill／模板／守衛／範例)怎麼切?→ 移交 Stage 2
- [>] Q8:Evidence 最小欄位與狀態枚舉要不要 Observed／Reported／Inferred?→ 移交 Stage 2
- [>] Q9:過期 Assumption 擋 G2 的牙長在哪支腳本／清單?→ 移交 Stage 2
- [>] Q10:disposition 引用語法(不另發 ID 鏈)怎麼寫?→ 移交 Stage 2
- [>] Q11:lookback 落 HISTORY 還是 7-review 附錄?→ 移交 Stage 2
- [>] Q12:evidence allowlist 形狀與 `devtalk-guard` 怎麼改才不會「規定了但讀不到」?→ 移交 Stage 2
- [>] Q13:Fast triage 命中後升 full、mini real-world,還是 Owner Call?→ 移交 Stage 2
- [>] Q14:範例何時改、是否同 slug?→ 移交 Stage 2+

## Constraints
- 本 PR 不宣稱 G1 PASS;不改 STATUS／HISTORY(整合分支才寫表列)。
- 表列只准 `scripts/status-update.sh`;HISTORY 只准 `history-append.sh`。
- 圍欄仍禁讀下游方案檔;B-1 只開事實入口,不開 2／3／4／5／6／7。
- A-5 本包上限 = verdict 一行角色／場景。
- 高影響 `[Assumption]`／`[~]` 必寫風險 + 期限;到期未驗擋 G2(本檔 Q6 與 Exceptions 三條已先照做)。
- 詞條(語言,不是方案):發現題 = 問現況／案例／例外／證據的題;裁決題 = 已核事實上的取捨題。Requested solution = 使用者帶來的解法構想,未定案。disposition ledger = 高影響真實世界列的去向帳。improvement lookback = 出貨後回看真實問題有無改善。本 hop 不寫進長期記憶。

## 驗收雛形
- AC-1(G-out-1):假設人讀一份 Stage 1,當對照「想達成的結果」與「想做的功能」,則結果在 Goals,功能構想不在 Goals。
  - 從哪看:該 feature 的討論記錄裡,目標與構想是否分開
  - 看到什麼算對:目標句不指定畫面／API／元件;構想另欄且標未定案
  - 拿什麼試:本檔;以及一份故意把「我要 dashboard」寫進目標的對照稿
- AC-2(G-out-2):假設訪談者在蒐集「上次真的怎麼做」,當問題出口時,則該題不附推薦答案。
  - 從哪看:該場發現題的問句本身(不是事後合理化)
  - 看到什麼算對:問句是開放的;推薦只出現在事實被覆述確認之後的裁決題
  - 拿什麼試:本包落地後的一次真實討論;或一份「發現題先給答案」的對照問句
- AC-3(G-out-3):假設一份討論有高影響主張,當 reviewer 沿主張往回走,則要嘛碰到可重開的來源,要嘛碰到 Assumption + 期限;沒有「因為點過頭所以是事實」。
  - 從哪看:該主張旁的出處或 Assumption 標記
  - 看到什麼算對:來源能重開且支持該句,或有期限;點頭紀錄不單獨當來源
  - 拿什麼試:本檔 Context 各條;以及範例 Evidence 未逐條連主張的現況
- AC-4(G-out-4):假設高影響 Assumption 已過驗證期限仍未驗,當人要過 G2,則過不了。
  - 從哪看:G2 送審被擋下的結果(人看得見的拒絕,不是事後口頭提醒)
  - 看到什麼算對:明確因過期假設被拒;不是「知道有假設仍綠」
  - 拿什麼試:本檔 Q6 過期仍未對帳的假設稿(後續造)
- AC-5(G-out-5):假設人讀一筆 ACCEPTED 的 Human verdict,當問「這次驗了誰、驗了哪場」,則一行內能答出來。
  - 從哪看:該筆 verdict 本文
  - 看到什麼算對:角色與場景都寫了;不是只寫 ACCEPTED 與姓名日期
  - 拿什麼試:後續命中 Stage 3 的 Demo 回饋;本 hop 不 Demo
- AC-6(G-out-6):假設 Stage 1 記了一條高影響痛點／workaround／exception,當人讀到 Stage 4,則該條有去向(處理／刻意維持／Non-Goal／另開 slug／仍待驗)。
  - 從哪看:Stage 2→4 之間那份去向帳,以及 Stage 4 對應落點
  - 看到什麼算對:每條高影響列都有去向;沒有「Stage 1 寫過、後面消失」
  - 拿什麼試:本檔 Journey 的「痛點消失」「發現被錨定」「問題沒改善」三列
- AC-7(G-out-7):假設 feature 已 shipped,當回看日到了,則有人用事先寫下的來源核對真實問題,低於門檻要重開。
  - 從哪看:出貨時留下的回看約定(日期／owner／來源／門檻)
  - 看到什麼算對:四欄都在;到期未回看不能假裝問題已改善
  - 拿什麼試:本包自己出貨後的回看約定(後續站寫);不是本 hop 的 G3
- AC-8(G-out-8):假設 owner 核准一份事實型證據,當討論者要引用它,則讀得到事件／行為／結果;同時打不開下游方案檔。
  - 從哪看:該場討論用到的證據,以及試圖讀 2-decision／4-spec 時的阻擋
  - 看到什麼算對:核准過的事實進得來;方案檔仍進不去;ticket 裡的解法建議不當事實
  - 拿什麼試:一份 owner 核准的去識別化 SOP／案例,加一份 2-decision 負向嘗試
- AC-9(G-out-9):假設人要走 Fast 寫 4-spec,當還沒收束「下一步／權限／等待／交接／系統外／中斷」六問,則還不能把這次當成已完成的早期風險分診。
  - 從哪看:進 Stage 4 之前那份分診結果
  - 看到什麼算對:六問都有答;命中者有升 full／mini／Owner Call 的去向,不是空白就開寫規格
  - 拿什麼試:「只改一個狀態字、但會把等待顯示成完成」的對照案

## 現況圖
誰:討論 agent
做什麼:帶推薦問現況
工具:dev-talk
痛點:發現被錨定
↓
誰:收斂者
做什麼:只收 Goal AC
工具:2-decision
痛點:痛點消失
↓
誰:owner
做什麼:G3綠就出貨
工具:7-review
痛點:問題沒改善

## 邏輯圖(ASCII)
```
now
|-- talk (discover)
|   |-- recommend-on-ask   [A-2]
|   |-- nod = verified     [A-3]
|   +-- Goal locks channel [A-1]
|-- 2 then 4
|   |-- only Goals/AC      [A-6]
|   +-- [~] to G2          [A-4]
|-- ship
|   |-- G3 green
|   +-- no lookback        [A-7]
+-- fast
    |-- skip 1-3
    +-- triage at 4        [B-2]
evidence wall: facts blocked with solutions [B-1]
verdict: any human click   [A-5 LIGHT]
```

## Interview Log(推理鏈外顯)
- Q:為什麼 Stage 1 說不做決定,驗收雛形仍會在 G1 前鎖死解法?
  - 事實:_templates/1-discussion.md:L12 _templates/1-discussion.md:L91-L96 skills/dev-talk/nodes/S4-accept.md:L19-L22 _templates/4-spec.md:L56-L60 example/contract-expiry-reminder/1-discussion.md:L62-L65
  - 推理:「從哪看」的候選直接列畫面／端點。Stage 4 把這層升成可測契約。範例已示範把 dashboard 寫進 Goal／AC。使用者帶著「我要 dashboard」來時,Stage 2 只剩「dashboard 怎麼做」。
  - 結論:CONFIRMED Goals 必須只寫人的結果;構想進 Requested solution;本檔 AC 不鎖通道。
- ⚠️ Q:為什麼「每題附推薦答案」會污染對真實行為的發現?
  - 事實:skills/dev-talk/nodes/N3-probe.md:L22-L23 skills/dev-talk/nodes/S2-world.md:L20-L34 skills/dev-talk/nodes/N3-probe.md:L41
  - 推理:發現題與裁決題共用同一條「附推薦」規則。受訪者容易確認模型的合理敘事,而不是回想上次真的怎麼做。「兩輪無新問題」是 agent 自己可提前達成的停止條件,補救不了錨定。
  - 結論:CONFIRMED 發現題禁推薦;裁決題才可附。現場是否仍這樣問 = `[Assumption]`,期限 Stage 2。
- Q:為什麼「點頭」不能把主張升格成證據,高影響假設又為什麼不能一路帶到 G2?
  - 事實:skills/dev-talk/nodes/S1-survey.md:L28-L29 _templates/1-discussion.md:L82-L86 _templates/2-decision.md:L35-L37 scripts/check-realworld.sh:L88-L91
  - 推理:認可是確認理解,不是驗證原始碼或營運事實。`[~]` 可讓 Stage 1 approved。接手不看假設會不會改權限／金流／方向。牙只驗有 Evidence 字樣。過期假設若為假,測試仍會綠。
  - 結論:CONFIRMED 主張 → 來源或 Assumption+期限;高影響過期擋 G2。狀態枚舉細節移交 Stage 2。
- Q:為什麼 A-5 只 LIGHT,不在本包做 Actor Coverage 全表?
  - 事實:_templates/3-prototype.md:L118-L129 skills/dev-flow/SKILL.md:L102-L105 notes/review-requirement-discovery-gaps.md:L25
  - 推理:現制已能擋 Agent 代填,擋不住「錯的人按對的鈕」。owner 裁 LIGHT = 先讓後讀者看得出驗了誰、驗了哪場。全表是另一層成本,本包不做。
  - 結論:CONFIRMED 本包驗收停在 verdict 一行角色／場景。
- Q:為什麼真實世界列能在 Stage 2→4 靜默消失?
  - 事實:_templates/2-decision.md:L35-L37 _templates/2-decision.md:L59-L60 _templates/4-spec.md:L72-L75 scripts/check-realworld.sh:L215-L231
  - 推理:收斂只吃 Goals／AC／`[>]`。Stage 3 場景有逐場點名牙,Stage 1 痛點列沒有同級保護。Journey 發現的代理不補知會、共管重複聯絡,可以不進 R/S。
  - 結論:CONFIRMED 要有 Stage 2→4 disposition ledger;引用語法移交 Stage 2。
- Q:為什麼 G3 綠仍不能證明真實問題有改善?事實入口與 Fast 順序又差在哪?
  - 事實:_templates/7-review.md:L316-L342 skills/dev-talk/SKILL.md:L17-L21 skills/dev-flow/SKILL.md:L34-L36 _templates/4-spec.md:L266-L269 docs/dev/engine-fence-masking/4-spec.md:L11-L12
  - 推理:Exit 證明功能做對,沒有回看日／owner／來源／門檻。圍欄擋住下游方案是對的,但同時擋住未指名的上游事實。Fast 用檔數／bugfix 起跑,「高風險人機互動」寫在 4-spec,lane 已選完。
  - 結論:CONFIRMED A-7 要 lookback;B-1 要 owner 核准的事實入口且仍禁方案檔;B-2 要 Stage 4 前的早期分診。落點與升 full／mini 移交 Stage 2。
- ⚠️ Q:若只改散文、不改牙,會怎樣?(發散)
  - 事實:hooks/devtalk-guard.sh:L16-L21 scripts/check-realworld.sh:L88-L91 notes/review-requirement-discovery-gaps.md:L293-L296
  - 推理:B-1 若只改 skill 句子、不改允許集合,會變成「規定了但讀不到」。A-1 若只用 dashboard／API 黑名單,會誤殺合法領域詞。A-2 的誘導無法從最終 md 完整還原。
  - 結論:OPEN 機械化必須部分牙 + 部分 reviewer;本 hop 不選定牙的形狀。最極端:九條全寫進指南、現場仍照範例走偏。
- ⚠️ Q:本 hop 範圍有沒有悄悄變成施工?九條一包會不會太大?(盲點)
  - 事實:notes/review-requirement-discovery-gaps.md:L16-L30 docs/dev/STATUS.md:L50
  - 推理:owner 明定一包、實作另開、本 hop 只 Stage 1。隱含預設「採用者照範例走」沒有現場 log,已標 Assumption。另一隱含預設「改模板就夠」不成立——範例與牙會教人走偏。
  - 結論:CONFIRMED 本 PR 只落討論;不重開拆包;不改模板。Q6 過期擋 G2。
