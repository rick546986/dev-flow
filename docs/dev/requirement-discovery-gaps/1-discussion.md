---
feature: requirement-discovery-gaps
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 1. 討論 — 需求發現九條制度缺口（A-1…A-7、B-1、B-2）

> 用途:發散。**不做決定**。本場依 owner 2026-09-12 Owner Call 書面 brief 落檔,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1、不送 G1**。未核敘述標 `[Assumption]`。
> A-1 已裁:Goals 只寫人的結果;Requested solution 另節、未定案。驗收雛形不鎖畫面／API／元件通道。
> 九條一次一包:A-1…A-4／A-6／A-7／B-1／B-2 **DO**;A-5 **LIGHT**。裁決不當 Open Question 重開。

## Problem
痛:討論與七關能全綠,人卻可能只做完被指定的功能,沒處理真實工作問題。
現在怎麼繞:人口頭提醒「別把 dashboard 寫進 Goal」;Owner Call 寫在 notes;reviewer 靠閱讀抓漂移;沒有 disposition 與 lookback 紀錄。

## Context(已知事實)
- Stage 1 頂註明文「不做決定」:_templates/1-discussion.md:L12
- 驗收雛形固定骨架把「從哪看」候選寫成畫面路徑／API／檔案／log:_templates/1-discussion.md:L91-L98
- 討論節點要求每條 Goal 問出「從哪裡看(畫面/端點/檔案/log)」:skills/dev-talk/nodes/S4-accept.md:L19-L23
- Stage 4 把 Stage 1 驗收雛形的觀測方式承接到每條 S:_templates/4-spec.md:L56-L60
- 完整範例 Goals 已指定登入、點擊、一眼可見:example/contract-expiry-reminder/1-discussion.md:L62-L65
- 同範例 AC 鎖定 dashboard、卡片、URL:example/contract-expiry-reminder/1-discussion.md:L83-L103
- 同範例 Interview Log 已記「dashboard 是最低成本的呈現面」:example/contract-expiry-reminder/1-discussion.md:L115-L118
- 逐題逼問硬規則「一次只問一題、附推薦答案」:skills/dev-talk/nodes/N3-probe.md:L22-L26
- 同節完成條件是「連續兩輪無新問題」:skills/dev-talk/nodes/N3-probe.md:L41
- 真實世界盤點要採最近一次真實行為、workaround、exception、evidence:skills/dev-talk/nodes/S2-world.md:L20-L34
- 盤現況:使用者認可後的清單=本次「已核事實」:skills/dev-talk/nodes/S1-survey.md:L28-L29 skills/dev-talk/SKILL.md:L102
- 讀取白名單只准長期記憶入口、`docs/specs/`、原始碼、使用者已指名檔;文件夾不列目錄:skills/dev-talk/SKILL.md:L17-L21
- Evidence 期待含實際案例／訪談／辦法／log／表單／畫面／使用者反映:skills/dev-talk/nodes/S2-world.md:L30-L31
- real-world 守衛驗章節／表頭／範例有 `[Assumption]` 與「訪談」字樣,不驗來源是否支持主張:scripts/check-realworld.sh:L71-L91
- 完整範例 Evidence 品質不差,但仍無逐條主張→來源對帳:example/contract-expiry-reminder/1-discussion.md:L54-L60
- Open Questions 允許 `[~]` 帶假設收尾、Stage 1 仍可標完成:_templates/1-discussion.md:L82-L86
- Stage 2 接手只核 status 與三態,決策點從 Goals／驗收雛形／`[>]` 提煉:_templates/2-decision.md:L35-L38
- Stage 2 自檢要求 Decision 覆蓋 Goals、移交項有著落,不要求處置 Journey 痛點:_templates/2-decision.md:L59-L61
- Success Criteria 只要「可量測」,未分交付指標與結果指標:_templates/2-decision.md:L42-L44 _templates/2-decision.md:L102-L103
- Stage 4 有驗收雛形→R/S 與 Stage 3 場景對帳,沒有 Real-world→Decision／R/S 對帳:_templates/4-spec.md:L56-L60 _templates/4-spec.md:L72-L76
- real-world 守衛已替 Stage 3 對帳做逐場點名,Stage 1 痛點無同級牙:scripts/check-realworld.sh:L215-L232
- Stage 3 Participants 自由文字;Human verdict 只驗人類親填＋attestation,不驗角色／場景覆蓋:_templates/3-prototype.md:L108-L129 scripts/check-realworld.sh:L137-L152
- Stage 7 Operational Walkthrough 由 reviewer 代入角色走查,不能取代真實角色確認:_templates/7-review.md:L146-L149
- Problem 模板只要求誰／痛／怎麼繞,不要求基線人口／頻率／來源:_templates/1-discussion.md:L33-L34
- 完整範例 Problem 自發寫了每季漏件與 8,000 筆量級,AC 仍只驗卡片功能:example/contract-expiry-reminder/1-discussion.md:L12-L19 example/contract-expiry-reminder/1-discussion.md:L83-L103
- Exit Checklist 全是出貨前驗證,無回看日期／owner／來源／低於何值重開:_templates/7-review.md:L316-L342
- Fast lane 省略 Stage 1–3,從 4-spec 起跑:skills/dev-flow/SKILL.md:L35-L36 guides/guide-dev-flow.html:L663-L667
- fast 無 1/3 檔時 Stage 3 機械判 legacy/N-A 放行:skills/dev-flow/SKILL.md:L126-L127
- 4-spec 有「高風險人機互動 → 自動升 Full」,但判準發生在已選 lane、已進 Stage 4 之後:_templates/4-spec.md:L266-L269
- Owner Call 2026-09-12 九條裁決(A-1…A-4／A-6／A-7／B-1／B-2 DO;A-5 LIGHT;實作另開):notes/review-requirement-discovery-gaps.md:L16-L30
- Backlog 仍把九條標成「實作另開後續 feature」:docs/dev/STATUS.md:L49
- HISTORY 記裁決日與「實作另開」:docs/dev/HISTORY.md:L500-L504
- feature branch 禁改 STATUS 表列:docs/dev/STATUS.md:L10-L12 scripts/status-update.sh:L408-L415
- Stage 1 只填 Context + Interview Log;Decision／OC／ADR 不進本 hop:notes/design/stage1-context-chain.md:L21-L26
- Context 出處語法只有 `path:L起` 或 `path:L起-L迄`:_templates/1-discussion.md:L36-L39

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 需求發起人／受訪者 | 把痛講清楚,不要被問成「你要的功能」 | 答問題、點頭、裁 Owner Call | 自己記得的最近一次做法 | 原始碼是否真如 agent 所述;其他角色怎麼做 | 口頭、Email、私表 |
| 討論 agent | 寫完一份可收斂的 1-discussion | 讀白名單、寫本 slug 討論檔 | 模板／節點硬規則、眼前使用者 | 未被指名的 SOP／ticket／log;第一線是否在場 | 編輯器、終端機 |
| G1／G2 reviewer | 方向與契約是在解原問題,不是解被鎖死的功能 | 退回 Stage 1／擋 G2 | 討論與決策文 | 主張是否真有來源;Assumption 過了沒 | 瀏覽器、GitHub |
| 採用專案 owner | 七關綠且現場真的少漏件／少等人／少 Excel | 裁 lane／gate／是否授權讀證據 | 本專案痛與時程 | 模板與範例教的是不是同一套 | GitHub、現場會議 |
| 第一線操作員／系統外窗口 | 把手上那件工作做完 | 系統外(常無帳號、不進 Demo) | 自己的土法與例外 | 討論裡有沒有自己的痛 | Email、電話、Excel |
| 方法論作者(本 repo) | 九條一次收進可審討論,不當九個 slug | 開 feature、裁 DO／LIGHT | Owner Call、本 tree | 採用現場現在是否仍照範例走 | GitHub、notes |

### Current Journey
正式 SOP:Stage 1「不做決定」→ 盤真實世界 → Goals 寫想達成 → Stage 2 比較方案 → Stage 4 才把觀測通道寫進 S。
實際(無本包時):發起人帶著功能想法進來;agent 把通道寫進 Goals／AC,發現題先給推薦答案;點頭後清單變「已核事實」;Stage 2 只比功能怎麼做;痛點可無聲消失;fast 直接 4-spec。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 發起人 | 帶「我要一個 dashboard／按鈕」開工 | 口頭／brief | 討論 agent | 功能句進討論 | 問題還沒挖 |
| 2 | 討論 agent | 發現題附推薦;驗收問畫面／端點 | dev-talk、1-discussion | 受訪者點頭 | Goals／AC 已帶通道 | 解法被提前鎖 |
| 3 | 受訪者 | 認可技術清單與合理敘事 | 對話 | — | 「已核事實」外觀 | 點頭≠查過源碼 |
| 4 | 收斂者 | 從 Goals／AC／`[>]` 提煉決策點 | 2-decision | owner | 方案表只比功能 | 痛點／例外無下落 |
| 5 | 規格者 | 把雛形觀測升成 R/S | 4-spec | G2 reviewer | 通道進可測契約 | 錯前提可測且綠 |
| 6 | fast 開工者 | 以檔少／bugfix 選 fast,跳過 1–3 | 4-spec mini | — | 無 Actors／Journey | 互動風險太晚問 |
| 7 | 出貨審 | G3 驗 S 與 Exit 勾完即 shipped | 7-review | owner | PASS／shipped | 不知真實問題有否改善 |

### Workarounds
- 人口頭說「Goals 寫結果、別寫 dashboard」;系統不擋把通道寫進 Goal。
- 九條裁決先寫在 `notes/review-requirement-discovery-gaps.md`,本 tree 模板／範例／守衛仍是舊形。
- reviewer 靠閱讀抓「解法混進 Goal」與無來源主張;real-world 牙只驗有章節、有 `[Assumption]`、有「訪談」字樣。
- 高影響例外靠記憶補進 Stage 2;沒有 ledger,常不留「這列刻意不處理」紀錄。
- 想引用 SOP／ticket／log 時,要使用者先唸出精確路徑,否則 agent 讀不到。
- 這些步驟多數不留「發現題有沒有先給推薦答案」的對話證據(逐字稿只住本機)。

### Exceptions
- Fast lane 合法跳過 Stage 1–3;「只改一個按鈕」仍可能改下一步／核准／等待語意。
- 本場用書面 Owner Call 代現場訪談;系統外第一線未直接發言。
- `[~]` 與未標期限的 `[Assumption]` 可伴隨 Stage 1 approved;現況無過期擋 G2 的牙。
- 主要操作員未覆蓋時,主管／發起人仍可填 Human verdict;runtime 只認 attestation 格式。
- 誰都可以不讀範例外的模板頂註;採用者照完整範例會把解法寫進 Goal。
- `[Assumption]` 採用現場仍照範例把通道寫進 Goal／AC(無採用 log;風險=高,本包改模板會教不會;期限=Stage 2 對帳範例＋至少一份採用討論,過期擋 G2)。
- `[Assumption]` 現場仍有人用 fast 改核准／等待／交接語意(無 log;風險=高,會在無 Actors／Demo 下出貨;期限=Stage 2 定 triage 落點,過期擋 G2)。

### Evidence
- owner 書面 brief(本 session):slug `requirement-discovery-gaps`;lane full;本 hop 只 Stage 1、不送 G1;九條一次一包;A-5 LIGHT;分析檔只當原料;本 PR 不改 `_templates/`／`skills/`／`example/`／守衛／STATUS／HISTORY;不發明 G-gate PASS。
- Owner Call 正本:notes/review-requirement-discovery-gaps.md:L16-L30
- 分析原料(非施工單):同檔 A-1…B-2 各節;本討論只引用已在本 tree 重讀過的出處。
- 已核文件:上列 Context 出處(本 working tree 讀過)。
- Backlog／HISTORY 仍寫「實作另開」:docs/dev/STATUS.md:L49 docs/dev/HISTORY.md:L500-L504
- 基線(A-7 最小欄,無資料不捏造):受影響者=討論 agent／G1–G2 reviewer／採用專案 owner／常未被訪談的第一線。頻率／件數 `[Assumption]`(無採用專案 log;風險=高,會低估「照範例走偏」;期限=Stage 2 對帳至少一份採用討論或本母版後續 dogfood,過期擋 G2)。影響=全綠仍解錯題。觀測窗=2026-08-17 盤點至 2026-09-12 裁決。來源=本 tree 模板／技能／範例＋Owner Call。
- `[Assumption]` 採用現場仍照範例走偏、fast 仍漏互動風險:無 log;期限 Stage 2,過期擋 G2。

## Goals
- G-split:人寫完／審完 Stage 1 時,能分辨「工作狀態要變成什麼」與「有人提過、仍可推翻的解法」;後者不能當已定案目標。
- G-discover:蒐集現況／最近案例／例外／證據時,受訪者先講自己怎麼做,不被題目裡的推薦答案錨定。
- G-source:高影響主張要嘛連到可核來源,要嘛標 Assumption 並有驗證期限;人點頭只代表「這份盤點可當討論起點」,不把主張升成已核事實。
- G-deadline:高影響 Assumption 寫得出若為假會怎樣、誰在何時驗;期限過了仍未驗,人不能帶它過 G2。
- G-verdict:Human verdict 讓人看得出這次覆蓋哪個角色、哪個場景(本輪一行即可,不是全表)。
- G-ledger:進到 Stage 4 定稿前,高影響痛點／土法／例外每條都有去向(處理／刻意維持／Non-Goal／另開 slug／仍待驗),不能無聲消失。
- G-lookback:宣稱 shipped 之後,人知道何時回看、誰看、看哪份資料、低於何值要重開討論／回滾／另開 feature。
- G-ingress:事實型證據(SOP／ticket／incident／analytics／去識別化 log／表單／畫面)只在 owner 核准該來源後才讀;下游方案檔仍禁讀。
- G-fast:人選 fast 並開始寫 Stage 4 之前,已經做過互動風險 triage(下一步／權限／等待語意／交接／系統外／中斷恢復)。

## Requested solution（候選，未定案）
- Stage 1 把 Goals 與「Requested solution」分欄;驗收雛形只寫人在工作裡看到什麼結果才算改善,選定解法後才由 Stage 2／4 補 repo 內觀測通道。
- Stage 2 在原因仍可能由流程／政策／資料品質解決時,比較 no-build／process-only;不合理可註明,不硬塞。
- 發現題禁附推薦;裁決題(已核事實上的取捨)可附選項／差異／推薦。
- 主張就地標來源或 Assumption＋期限;使用者認可不升格證據。高影響 Assumption 寫風險＋期限;過期擋 G2。
- Human verdict 一行寫角色／場景(A-5 LIGHT);本輪不做 Actor Coverage 全表。
- Stage 2→4 做高影響痛點／土法／例外的 disposition ledger,並在 Stage 4 對帳到 R/S 或 Out of Scope／Known limit／後續 slug。
- Stage 7 Exit 留下 post-ship lookback(日期／owner／來源／低於何值重開);落點用既有 HISTORY 或 7-review 附錄,不另造無主永久檔。
- 開事實型 evidence 入口:列想找的類型與原因 → owner 核准來源／路徑後才讀;仍禁下游 2/3/4/5/6/7 與方案檔。
- Fast lane 在進 Stage 4 前做 early risk triage;命中後由後續站裁升 full 或 fast＋mini real-world delta。
- 同步改正完整範例,避免模板說結果、範例仍教解法。
- 本 hop 不選定欄位形、守衛落點、枚舉名、或「語意一半留給 reviewer」的切割。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`skills/`、`example/`、守衛、`docs/dev/STATUS.md`、`HISTORY.md`。
- 本 hop 不送 G1、不填 G1／G2／G3 PASS、討論檔 status 留 draft。
- 不重開 Owner Call 的 DO／LIGHT;不把 A-5 做成 Actor Coverage 全表。
- 不把九條拆成九個 slug;不與 `integration-before-verdict` 混施工。
- 不為填基線而捏造採用現場件數。
- 不用 `dashboard`／`API` 關鍵字黑名單冒充 A-1 語意守衛(分析已寫會誤殺領域詞;落點交 Stage 2)。
- 不在本 PR bump plugin。

## Open Questions
- [x] Q1:lane 是否 full?→ owner:full
- [x] Q2:九條是否一次一包、A-5 是否 LIGHT?→ owner:一包;A-5 LIGHT,其餘 DO
- [x] Q3:本 hop 是否送 G1、是否改模板／範例／守衛／STATUS?→ owner:只 Stage 1;那些檔下 hop 才動
- [x] Q4:可否重開 Owner Call 的 DO／LIGHT?→ 不可
- [~] Q5:機械牙與 reviewer 語意各守一半,是否為本包預設切割?(帶假設:是,分析已寫「只能部分機械化」;期限=Stage 2 逐條定牙／checklist,過期擋 G2)
- [>] Q6:A-1 分欄形狀、驗收雛形怎麼寫才不算鎖通道、Stage 2 no-build 適用性判定寫在哪?→ 移交 Stage 2
- [>] Q7:A-3 主張狀態枚舉與 Evidence 最小欄位?A-4 高影響怎麼標、過期擋 G2 的牙落在哪支腳本?→ 移交 Stage 2
- [>] Q8:A-6 ledger 欄位、Stage 4 對帳形、G1 twin 是否置頂未處置列?→ 移交 Stage 2
- [>] Q9:A-7 lookback 落 HISTORY 追加、7-review 附錄、或 STATUS 到期提示?→ 移交 Stage 2
- [>] Q10:B-1 evidence allowlist／manifest 與 `devtalk-guard` 允許集合怎麼改,才不會「規定了但讀不到」?→ 移交 Stage 2
- [>] Q11:B-2 triage 問卷放哪(4-spec 前獨立清單 vs Profile 欄)、命中後升 full 或 mini delta 的預設?→ 移交 Stage 2

## Constraints
- 表列只准 `scripts/status-update.sh` 且必須在 `main`;本 feature branch 不改 `docs/dev/STATUS.md`。
- HISTORY 只准 `history-append.sh`;本 hop 不追加。
- 本 PR 不宣稱任何 G-gate PASS;status 留 draft。
- 分析檔不是施工單;落點與牙留給後續 G1／G2。
- 若後續命中 Stage 3:Human verdict 一行寫角色／場景(A-5 LIGHT),不在本 hop 做全表。
- 人看討論用繁中;ID／R／S／T 維持英式。

## 驗收雛形
- AC-1(G-split):假設一份 Stage 1 已寫完,當另一個人只看「結果」與「未定案解法」兩堆文字,則能指出哪幾句是工作狀態、哪幾句拿掉後結果句仍然完整;驗收敘述沒有指定唯一畫面路徑、API 或元件。
  - 從哪看:該次討論裡兩堆並列的文字(名稱可後定)
  - 看到什麼算對:把解法堆整段刪掉,結果堆仍能獨立成立;結果堆改寫成「少漏件／少等人／少用私表」不需要改成某個畫面名。不是「必須出現某節標題」
  - 拿什麼試:本檔 Goals vs Requested solution;對照完整範例現況(Goals／AC 已帶 dashboard)
- AC-2(G-discover):假設 agent 正在問最近一次真實做法／例外／證據,當題目送出,則題目本身沒有先給推薦答案;推薦只出現在事實已被覆述確認之後的裁決題。
  - 從哪看:該場 Interview Log 的高影響發現題,以及(若後續有)題型標記
  - 看到什麼算對:發現題看不出「我覺得答案是 X」;裁決題才看得到選項／差異／推薦
  - 拿什麼試:本場書面 brief(無現場問答)＋後續改 skill 後的一場真實討論抽查
- AC-3(G-source,G-deadline):假設出現高影響主張,當人要把它當事實往下用,則看得到來源,或看得到 Assumption＋若為假的後果＋驗證期限;僅有「使用者點頭」不得把它變成已核事實。期限過了未驗,則不得進 G2。
  - 從哪看:該主張所在段落,以及 G2 送審時的假設清單
  - 看到什麼算對:每條高影響主張能指回來源摘要,或帶期限;過期未驗的檔案不能處於「可過 G2」狀態
  - 拿什麼試:本檔已標期限的兩條 `[Assumption]`;後續造一筆過期未驗的負向樣本
- AC-4(G-verdict):假設有人填了 Human verdict,當另一個人讀那一行,則知道這次覆蓋哪個角色、哪個場景。
  - 從哪看:該次 User Demo Feedback(或同等人類判定處)的 verdict 附近
  - 看到什麼算對:讀得到角色＋場景各至少一個具體名;不是只寫 ACCEPTED
  - 拿什麼試:後續若命中 Stage 3 的本 slug;或改完模板後的範例／fixture
- AC-5(G-ledger):假設 Stage 1 寫了高影響痛點／土法／例外,當 Stage 4 定稿,則每條都有去向;標「本方案處理」的至少落到一條可驗敘述,其他狀態落到 Out of Scope、Known limit 或後續 slug。
  - 從哪看:Stage 2／4 的處置表與對帳結果(名稱可後定)
  - 看到什麼算對:抽一條高影響例外,能指出去向;沒有「Journey 寫了、後面完全沒出現」
  - 拿什麼試:本檔 Journey 的「痛點無下落」「fast 跳過 1–3」兩列,後續站必須處置
- AC-6(G-lookback):假設人勾完 shipped,當看 Exit(或它指定的既有落點),則看得到回看日期、owner、資料來源、低於何值要重開。
  - 從哪看:出貨清單或其指向的既有檔(HISTORY／7-review 附錄等,落點後定)
  - 看到什麼算對:四欄都非空;不是「功能可用＝問題已改善」
  - 拿什麼試:後續本 slug 自己走到 Stage 7 的 Exit;對照現行 Exit 無此四欄
- AC-7(G-ingress):假設 agent 想讀一份未被預先指名的 SOP／ticket／log,當 owner 尚未核准該來源,則不讀;核准後只抽事件／行為／結果,不把票裡的解法建議當事實。下游方案檔仍不讀。
  - 從哪看:該場授權紀錄＋實際讀取範圍
  - 看到什麼算對:未核准就沒有把該檔寫進 Context;核准後 Context 引的是事件與限制,不是票上的實作建議
  - 拿什麼試:後續改守衛的正／負向樣本(未核准路徑、下游 2-decision)
- AC-8(G-fast):假設有人要以 fast 進 Stage 4,當互動風險 triage 尚未做完,則還不能開始把該變更寫成 Stage 4 契約;六問有命中時,人看得到「升 full」或「fast＋最小真實世界補寫」其中一個去向,不能只靠檔案數過關。
  - 從哪看:fast 開工當下的 triage 結果(位置後定)
  - 看到什麼算對:六問皆否且行為已有核准 spec → 才可直接 fast;有命中卻無去向 → 不能當合法 fast
  - 拿什麼試:「只改一個狀態字、但會讓等待看起來像完成」的對照案例

## 現況圖
誰:討論 agent
做什麼:解法寫進 Goal
工具:dev-talk
痛點:問題被鎖死
↓
誰:收斂者
做什麼:只比功能方案
工具:2-decision
痛點:痛點無下落
↓
誰:出貨審
做什麼:驗功能全綠
工具:G3 Exit
痛點:不知有否改善

## 邏輯圖(ASCII)
```
now
|-- Stage 1 says no decision
|   |-- Goals / AC still take channels
|   +-- example teaches dashboard
|-- evidence
|   |-- nod upgrades the list
|   +-- [~] can reach G2
|-- Stage 2-4
|   |-- extract Goals / AC / [>]
|   +-- pains can vanish
|-- Fast lane
|   |-- skip Stage 1-3
|   +-- risk asked at Stage 4
+-- this slug (full, nine IDs)
    |-- outcomes only this hop
    +-- no G1 / no template edit
```

## Interview Log(推理鏈外顯)
- Q:為什麼 Stage 1 說不做決定,驗收雛形仍會在 G1 前鎖死解法?
  - 事實:_templates/1-discussion.md:L12 _templates/1-discussion.md:L91-L98 skills/dev-talk/nodes/S4-accept.md:L19-L23 _templates/4-spec.md:L56-L60 example/contract-expiry-reminder/1-discussion.md:L62-L65 example/contract-expiry-reminder/1-discussion.md:L83-L103
  - 推理:頂註禁止決定,骨架卻要人選通道。Stage 4 把該觀測升成 S。完整範例已示範把 dashboard／URL 寫進 Goals／AC。使用者帶功能進來時,Stage 2 只剩「功能怎麼做」。
  - 結論:CONFIRMED 本包必須把人的結果與未定案解法分開;本檔自己的 Goals 只寫結果。
- Q:為什麼「每題附推薦答案」會污染真實行為?
  - 事實:skills/dev-talk/nodes/N3-probe.md:L22-L26 skills/dev-talk/nodes/S2-world.md:L20-L34 skills/dev-talk/nodes/N3-probe.md:L41
  - 推理:同一條鏈既要採最近一次真實做法,又要每題先給推薦。受訪者容易確認模型的合理敘事。連續兩輪無新問題是 agent 自己可提前達成的停止條件,補不了錨定。
  - 結論:CONFIRMED 發現題與裁決題必須分流;Owner Call 已裁,本討論不重開。
- ⚠️ Q:使用者點頭之後,主張為什麼仍可能沒有來源、卻能一路到 G2?
  - 事實:skills/dev-talk/nodes/S1-survey.md:L28-L29 _templates/1-discussion.md:L82-L86 scripts/check-realworld.sh:L71-L91 _templates/2-decision.md:L35-L38
  - 推理:認可被寫成「已核事實」。`[~]` 是合法終態。守衛只驗有 Evidence 章節與 `[Assumption]` 字樣。Stage 2 引用「事實」即可替方案背書。高影響假設沒有期限牙。
  - 結論:CONFIRMED A-3／A-4 要的是來源或 Assumption＋期限,以及過期擋 G2;點頭不是證據升格。
- ⚠️ Q:真實世界列為什麼能在 Stage 2→4 靜默消失?
  - 事實:_templates/2-decision.md:L35-L38 _templates/2-decision.md:L59-L61 _templates/4-spec.md:L72-L76 scripts/check-realworld.sh:L215-L232
  - 推理:決策點只從 Goals／雛形／`[>]` 來。自檢不要求處置痛點／土法／例外。Stage 4 對帳 Stage 3 場景,不對帳 Stage 1 Real-world。牙已保護 Demo 場景,反而凸顯 Journey 列無保護。
  - 結論:CONFIRMED 需要 disposition ledger;本檔 Journey 高影響列留給後續站處置,不當本 hop 已解。
- Q:為什麼 G3 綠仍不能證明真實問題有改善?
  - 事實:_templates/1-discussion.md:L33-L34 _templates/2-decision.md:L102-L103 _templates/7-review.md:L316-L342 example/contract-expiry-reminder/1-discussion.md:L12-L19
  - 推理:Problem 不強制基線。Success Criteria 不分成交與結果。Exit 停在出貨前勾項。範例自發寫了漏件量級,AC 仍只驗卡片。流程把 shipped 當終點。
  - 結論:CONFIRMED 要 post-ship lookback;本檔 Problem 已寫最小基線,件數標 Assumption。
- Q:白名單為什麼讓 Evidence 期待落空?
  - 事實:skills/dev-talk/SKILL.md:L17-L21 skills/dev-talk/nodes/S2-world.md:L30-L31
  - 推理:圍欄擋住下游方案是對的,但也擋住未被指名的上游事實檔。agent 只剩原始碼與眼前使用者的記憶。Evidence 外形完整,內容偏單人回想。
  - 結論:CONFIRMED B-1 要 owner 核准後的事實入口,同時繼續禁讀下游方案檔。
- ⚠️ Q:Fast lane 為什麼問互動風險太晚?
  - 事實:skills/dev-flow/SKILL.md:L35-L36 guides/guide-dev-flow.html:L663-L667 skills/dev-flow/SKILL.md:L126-L127 _templates/4-spec.md:L266-L269
  - 推理:fast 合法跳過 Stage 1–3。無 1/3 檔則 Stage 3 判 legacy/N-A。4-spec 雖寫高風險人機互動升 Full,但人已經在 Stage 4 裡。檔少的改動仍可能改核准／等待語意。
  - 結論:CONFIRMED 要在進 Stage 4 前做 early risk triage;升 full 或 mini delta 的預設交 Stage 2。
- Q:本 hop 要不要產出 G1、改 STATUS,或把 A-5 做成全表?
  - 事實:notes/review-requirement-discovery-gaps.md:L16-L30 docs/dev/STATUS.md:L10-L12 scripts/status-update.sh:L408-L415 notes/design/stage1-context-chain.md:L21-L26
  - 推理:Owner Call 已裁九條與 A-5 LIGHT。書面 brief 只要 Stage 1。feature branch 拒改 STATUS。Stage 1 不准 Decision。
  - 結論:CONFIRMED 本 PR 只落討論;status 留 draft;不填 G-gate PASS;A-5 一行即可。
