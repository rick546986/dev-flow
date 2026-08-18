# 審核區：需求討論與真實世界需求的制度缺口（**未裁定，暫緩處理**）

> 2026-08-17 盤點 `dev-talk`、Stage 1–7 模板、real-world 守衛與完整範例後產出，
> 2026-08-18 從 `notes/dispatch-parallel-feature-gaps.md` 拆出獨立成檔。
>
> ## ⛔ 這份不是派工單，不要照著做
>
> **owner 已裁定：這九條暫緩，等 dev-flow 自己跑完一次完整 full lane 之後再逐條裁決。**
>
> 理由：這九條跟前七輪修的東西性質不同 —— 前七輪修的是具體缺陷（守衛假綠、路徑推導錯、
> 字元集打錯），驗證方式是「弄壞它、看守衛會不會紅」；**這九條修的是方法論的設計是否恰當，
> 只能靠真的跑一次流程看有沒有改善**。而且它們會動到 `dev-talk` 核心契約、Stage 1–4 模板
> 與範例，採用專案全部要跟著動 —— 用單一實例的證據去改最核心的部分，風險不對稱。
>
> A-7 自己就講出了答案：「流程能證明功能做對，不能證明真實問題有改善」。
>
> **處理順序**：先跑一次完整 normal-risk full lane（1-discussion → 7-review、過 G1/G2/G3），
> 走完之後拿實際踩到的東西對照這九條，再決定哪幾條是真痛點。

---

> 2026-08-17 盤點 `dev-talk`、Stage 1–7 模板、real-world 守衛與完整範例後追加。
> **本區不屬於上面「已定的四項」，也不在本派工單授權範圍內。** owner 尚未逐項裁決；
> 後續執行者讀到本檔時，**不得因為上面的觸發句而直接實作本區**。
>
> 分級沿用採用回饋的語意：**A**＝可能讓流程全綠、卻解錯問題；**B**＝不一定立刻解錯，
> 但會讓證據不足或人機互動風險到後段才暴露。以下是供 owner 審核的候選，不是既定修法。

## 建議審核順序

1. 先裁 **A-1、A-2**：兩條都在修「訪談還沒完成，方案已先被問題形狀鎖死」。
2. 再裁 **A-3、A-4、A-6**：三條共同決定 Stage 1 的證據如何可靠地穿過 G1/G2。
3. 再裁 **A-5、A-7**：決定「誰能代表真實使用者」與「出貨後如何知道問題真的改善」。
4. 最後裁 **B-1、B-2**：分別是資料入口與 Fast lane 的例外路徑。

## A-1 — Stage 1 說「不做決定」，但驗收雛形會在 G1 前鎖死解法

### 證據

- `_templates/1-discussion.md:12` 明文說 Stage 1「不做決定」。
- `skills/dev-talk/SKILL.md:63-68` 又要求每條 Goal 指定「從哪裡看」，候選直接列
  畫面／端點／檔案／log；`_templates/1-discussion.md:74-81` 也把這四種**實作通道**
  寫進固定骨架。
- `_templates/4-spec.md:48-53` 會把 Stage 1 的驗收雛形與觀測方式直接升成 R/S，
  因此早期選到的通道不是暫時筆記，而是會一路進入可測契約。
- 填好範例已示範這種漂移：`example/contract-expiry-reminder/1-discussion.md:62-65`
  的 Goals 已指定登入、點擊與一眼可見；`:83-103` 的 AC 更鎖定 dashboard、卡片與 URL。
  `:115-118` 甚至在 Stage 1 就記「dashboard 是最低成本的呈現面」與「登入時即時查詢優先」。

### 會怎麼失效

使用者帶著「我要一個 dashboard」來，真正問題可能是資料不可信、責任人不清楚或現行 SOP
無人遵守。現行流程會把 dashboard 寫進 Goal／AC，Stage 2 只剩「dashboard 怎麼做」的
方案比較；最後七關全綠，仍可能只是**準確做完被指定的功能，沒有準確處理原問題**。

### 候選決定（待 owner 裁）

- Stage 1 把 `Goals` 限定為人的結果／工作狀態；使用者帶來的功能想法另標
  `Requested solution（候選，未定案）`，不得混成 Goal。
- Stage 1 的驗收雛形只回答「人在真實工作中看到什麼結果才算改善」，不指定畫面路徑、
  API、元件或資料格式。**選定解法後**，Stage 2/4 才把結果翻成 repo 內可執行的觀測方式。
- Stage 2 在原因尚可能由流程／政策／資料品質解決時，至少比較一個 no-build／process-only
  方案；不合理時可註明理由，不為湊數硬塞。
- 同步改正完整範例，否則模板說 outcome、範例仍教人寫 solution，採用者會照範例走偏。

### 機械化判斷

只能**部分機械化**。可守「Requested solution 與 Goals 分欄」「Stage 2 有 no-build
適用性判定」及範例形狀；無法只靠關鍵字可靠判斷一句 Goal 是否偷帶解法，這一半應留給
Stage 1 自檢與 G1 reviewer，避免用 `dashboard/API` 黑名單誤殺合法領域詞。

## A-2 — 「每題附推薦答案」會污染對真實行為的發現

### 證據

`skills/dev-talk/SKILL.md:53-57` 把「一次只問一題、**附推薦答案**」設成逐題逼問的硬規則，
但同一份 skill 的 `:37-52` 又要採集最近一次真實行為、workaround、exception 與 evidence。
兩種問法沒有分流：模型在蒐集事實時也可能先告訴受訪者「我覺得答案是 X」。

### 會怎麼失效

推薦答案會形成錨定。受訪者容易確認模型提供的合理敘事，而不是回想「上次真的怎麼做」；
最後文件有完整 Journey 和 Evidence 外觀，內容其實是模型與受訪者共同合理化出的理想流程。
`skills/dev-talk/SKILL.md:61-62` 的「連續兩輪無新問題」又是 agent 自己可提前達成的停止條件，
不能補救這個偏誤。

### 候選決定（待 owner 裁）

- 明分兩種問題：**發現題**（現況、最近案例、例外、證據）一律先開放問、不得附推薦；
  **裁決題**（已核事實上的取捨）才提供選項、差異與推薦。
- 發現題答完後可用中性覆述請對方校正；推薦只能出現在事實被覆述確認之後。
- 完成條件由「連續兩輪無新問題」改成「必查面已覆蓋、關鍵反例已問、證據缺口已顯性化」；
  兩輪無新問題最多當輔助訊號，不當充分條件。

### 機械化判斷

對話語意無法從最終 md 完整還原，**不值得假裝有硬 gate**。可在 skill 與 guide 釘死
「發現題禁推薦／裁決題可推薦」的對稱措辭，並用靜態守衛防其中一邊漂移；真正是否問成
誘導題，由 Stage 1 自檢抽查 Interview Log 的高影響題。

## A-3 — 「有證據／Assumption」二分太粗，且主張沒有逐條連到來源

### 證據

- `skills/dev-talk/SKILL.md:34-36` 把使用者「認可」後的技術清單直接升格為「已核事實」；
  但使用者認可是**確認理解或相關性**，不等於他有能力驗證原始碼、數字或營運事實。
- `skills/dev-talk/SKILL.md:47-52` 與 `_templates/1-discussion.md:54-56` 只要求列 Evidence
  並以 `[Assumption]` 區分；沒有來源日期、角色、樣本範圍、支持哪條主張、限制或衝突來源。
- `scripts/check-realworld.sh:71-91` 的守衛只驗章節／表頭存在、範例有 `[Assumption]`
  與「訪談」字樣。即使 Evidence 只有一句模糊的「使用者反映」，整組仍可綠。
- 完整範例 `example/contract-expiry-reminder/1-discussion.md:54-60` 的證據品質其實不差，
  但依然只能靠讀者猜哪個來源支持 Actors、Journey 與每一條 Exception。

### 會怎麼失效

「查到的」「某角色口述的」「模型從兩件事推論的」「多個來源互相衝突的」全被壓成
同一種「不是 Assumption 的事實」。Stage 2 `_templates/2-decision.md:35-36` 只要引用
`1-discussion` 的「事實」就能替方案優劣背書，fresh reviewer 無法重建證據強度。

### 候選決定（待 owner 裁）

- 不新增 Journey/Actor 第二 ID 鏈；改在重要主張就地標狀態：`Observed`（直接查到）、
  `Reported`（某角色陳述）、`Inferred`（明寫推理）、`Assumption`、`Conflict`。
- Evidence 改成最小結構：來源類型、日期／as-of、角色或資料範圍、支持的段落／列、
  限制與反證；敏感來源只留去識別化指標，不貼原始個資。
- 「使用者認可」只代表「確認這份盤點可作為討論起點」；證據狀態仍由來源決定，
  不因點頭自動升格。
- G1 reviewer 抽查至少一條高影響主張，沿引用回到來源摘要；對不上就退回 Stage 1。

### 機械化判斷

可機械驗 Evidence 欄位、狀態枚舉、重要表格每列有 source／Assumption，以及範例負向 fixture；
來源是否真的支持主張仍是 reviewer 語意判斷。守衛要避免重演現況的「只驗有 Evidence 字樣」。

## A-4 — 高影響假設可以合法一路帶到 G2，沒有風險門檻或驗證期限

### 證據

- `skills/dev-talk/SKILL.md:93-95` 允許 Open Questions 以 `[~]`「帶假設」收尾並把
  Stage 1 標 approved；`_templates/1-discussion.md:64-69` 也把它列為合法終態。
- `_templates/2-decision.md:31-36` 接手時只核 status 與三態，沒有檢查假設會不會改變
  權限、法規、金流、資料安全、外部承諾或整個方案方向。
- `_templates/4-spec.md:48-53` 會把驗收雛形升為 R/S；目前沒有「本 S 依賴哪個尚未驗證
  的高影響假設」欄位。

### 會怎麼失效

例如「主管有權代替法務核准」「外部窗口會在三天內回覆」或「歷史資料一定有 end_date」
都能以 `[~]` 合法通過。等到 Stage 6 才發現為假時，只能走 L2 大幅返工；更糟時測試完全
符合錯誤前提，G3 也會綠。

### 候選決定（待 owner 裁）

- 每個 `[Assumption]`／`[~]` 補四件事：若為假會影響什麼、影響級、怎麼驗、何時／由誰驗。
- 涉權限／法規／金流／資料隔離／不可逆行為／外部承諾的高影響假設，在 G1 前只能二選一：
  驗證完轉成 Observed/Reported，或由人類 Owner Call 明示接受風險並指定後續落點。
- Stage 4 的 R/S 若仍依賴合法保留的假設，要就地引用；假設被推翻時能機械列出需重審的 S，
  而不是靠記憶找。

### 機械化判斷

影響級需要語意判斷，但「每個假設有四欄」「high 必有 resolved 或 Owner Call」「S 引用的
假設存在」可機械檢查。若 owner 不想新增引用語法，至少可在 G1/G2 checklist 做人工對帳，
但需明記這會是散文規則。

## A-5 — Human verdict 只證明「有人按過」，不證明代表性角色驗過

### 證據

- Stage 1 Actors 很完整，但沒有「哪個 actor 是直接訪談、代理轉述或完全未接觸」的 coverage。
- `_templates/3-prototype.md:98-120` 只要求 `Participants` 自由文字與任一人類 attestation；
  沒要求 participant 的角色能對應 Demo Script 的「使用者角色」，也沒限制 verdict 的適用範圍。
- `skills/dev-flow/SKILL.md:98-103` 與 `scripts/check-realworld.sh:121-151` 機械保證的是
  「不是 Agent 代填」，沒有保證是實際操作員、核准者或受影響角色填。
- `_templates/7-review.md:112-116,200-205` 的 Operational Walkthrough 仍由 reviewer
  代入角色走查；它能抓邏輯缺口，不能取代真實角色對工作可行性的確認。

### 會怎麼失效

需求發起人或主管可以替第一線操作員按 ACCEPTED；內部人員也可以替系統外窗口判斷
交接可行。runtime 看到合法 human attestation 就放行，文件卻把局部意見呈現成整個
互動方案已驗證。

### 候選決定（待 owner 裁）

- Stage 1 增加 Actor Coverage：每個關鍵角色標 direct interview／direct observation／
  proxy／not covered，proxy 必寫限制。
- Stage 3 的 Participants 必填「對應 Actor／實際角色」，Human verdict 同時列
  `covered roles` 與 `covered scenarios`；ACCEPTED 只對該覆蓋範圍有效。
- 主要操作員或具決策權角色未覆蓋時，不一定一律停案（外部角色常無法直接 Demo），
  但必須由 Owner Call 接受 proxy 風險，不能靜默當成完整驗證。

### 機械化判斷

可驗欄位非空、角色名能對到 Stage 1 Actors、ACCEPTED 有 coverage；「這個人是否真能代表
該角色」仍需人工。runtime 不應只檢 attestation 格式後就把 coverage 視為完整。

## A-6 — 真實世界資訊沒有 disposition map，能在 Stage 2→4 間靜默消失

### 證據

- `_templates/2-decision.md:31-34` 只從 Goals／驗收雛形／`[>]` 提煉決策點；
  `:47-55` 的自檢只要求 Decision 覆蓋 Goals、移交項有著落。
- Current Journey 的痛點、Workarounds、Exceptions 與 Evidence 限制沒有逐條
  `addressed / intentionally unchanged / Non-Goal / separate feature` 的去向。
- `_templates/4-spec.md:48-64` 有驗收雛形→R/S 與 Stage 3 Scenario→R/S 的對帳，
  卻沒有 Stage 1 Real-world Context→Decision／R/S 的對帳。
- `scripts/check-realworld.sh:211-228` 已替 Stage 3 Scenario 補了「逐場點名」守衛，
  反而凸顯 Stage 1 的現實痛點仍無同級保護。

### 會怎麼失效

Journey 發現「代理主管事後不補知會」、Exception 發現「多人共管會重複聯絡」，但 Goals
只寫主要 happy path。Stage 2/4 沒有任何紅字要求處置這兩點，它們可以無聲消失；最後
Operational Context 看起來很完整，只是從一份已漏資料的 R/S 往下展開。

### 候選決定（待 owner 裁）

- Stage 2 增加 `Real-world Disposition`：逐條引用高影響痛點／workaround／exception，
  標記本方案處理、刻意維持、Non-Goal、另開 slug 或仍待驗證，並寫理由。
- Stage 4 對帳：標「本方案處理」者至少落到一條 R/S；其他狀態至少落到 Out of Scope、
  Known limit 或明確的後續 slug。只引用原文片段，不新增第二條 Journey ID 鏈。
- G1 twin 把「未處置的 real-world rows」放動線頂區，讓 reviewer 不必展開背景才看得到。

### 機械化判斷

可驗每條 disposition 非空、`addressed` 有 R/S、`non-goal/limit` 有落點；「哪些是高影響、
引用是否語意相符」仍由 reviewer 判。可沿用 Stage 3 對帳的負向 fixture 方式，避免只驗空表存在。

## A-7 — 流程能證明功能做對，不能證明真實問題有改善

### 證據

- `_templates/1-discussion.md:18-19` 的 Problem 只要求「誰、什麼痛、怎麼繞」，未要求
  影響人口、頻率、嚴重度／成本、觀測期間與資料來源。
- `_templates/2-decision.md:37-39,85-86` 只要求 Success Criteria「可量測」，未區分
  交付指標（功能可用）與結果指標（漏件、等待時間、返工是否下降）。
- `_templates/7-review.md:133-144` 的 PASS 全是出貨前驗證；`:267-282` Exit Checklist
  沒有上線後的量測 owner、觀測窗、回看日期或失敗觸發條件。
- 完整範例 `example/contract-expiry-reminder/1-discussion.md:12-19` 自發寫了每季漏件與
  8,000 筆量級，顯示這些資訊有價值；但模板未強制，`:83-103` 仍只驗卡片功能，
  沒有驗「漏約是否真的下降」。

### 會怎麼失效

G3 能證明卡片、API、權限與等待狀態符合 S，不能回答使用者是否因此少漏件、少等人或
少用 Excel。流程把 `PASS/shipped` 當終點後沒有學習迴圈，錯的產品假設只會變成一份
技術上正確的 living spec。

### 候選決定（待 owner 裁）

- Stage 1 Problem 加最小 baseline：受影響者／事件量、頻率、影響、觀測期間、來源；
  無資料可明寫 Unknown/Assumption，不為填數字而捏造。
- Stage 2 Success Criteria 分 `Delivery` 與 `Outcome`；Outcome 填 baseline、target、
  measurement、owner、window，無法量測時寫理由與可接受的 proxy。
- Stage 7 shipped 不必等待數週結果，但 Exit 必留下 post-ship outcome check 的日期、owner、
  資料來源與「低於何值要回來重開討論／回滾／另開 feature」。
- outcome review 結果要有既有落點（例如 HISTORY 追加或 7-review 附錄），不要另造一套
  永久文件卻沒有維護者。

### 機械化判斷

可檢欄位與追蹤落點存在、到期未回看時在 STATUS 顯示；指標是否真能代表問題改善是人類
判斷。不要把「填了任意數字」誤當成已建立有效 outcome metric。

## B-1 — 讀取白名單與 Evidence 期待互相打架，真實資料通常只能靠使用者記憶轉述

### 證據

`skills/dev-talk/SKILL.md:15-19` 只准主動讀 `CONTEXT.md`、`docs/specs/`、原始碼與
使用者**已指名**的檔案；文件資料夾甚至不可列目錄。可是 `:47-48` 期待 Evidence
包含實際案例、正式辦法、log、表單、畫面與使用者反映。support ticket、incident、
analytics 匯出、研究筆記、SOP 或附件若沒有被使用者先說出精確位置，agent 不得發現它們。

### 會怎麼失效

anti-premature-convergence 的圍欄擋住下游解法是合理的，但目前同時擋住上游事實。
agent 最容易取得的只剩原始碼與眼前使用者的記憶，結果 Real-world Context 形式完整、
證據仍偏向單一人的回想。

### 候選決定（待 owner 裁）

- 保留禁讀 2/3/4/5/6/7 與既有方案文件；另開**事實型 evidence allowlist**：
  使用者提供／授權的 support、incident、analytics、SOP、去識別化 log、表單與畫面。
- agent 可先列「想找哪類證據與原因」，由使用者授權來源或路徑；授權後才讀，避免無邊界
  掃描私密資料。外部 connector 也遵守相同規則。
- Evidence 記來源與限制，不把 ticket 內的解法建議當事實；只萃取事件、行為與結果。

### 機械化判斷

檔案型守衛可依路徑／本輪 evidence manifest 放行並繼續封鎖下游 artifact；外部資料源的
授權與去識別化需靠工具權限與人工確認。這條若只改散文、不改 `devtalk-guard` 的允許集合，
會變成「規定了但讀不到」的 A-0/A-13 同型問題。

## B-2 — Fast lane 先跳過 Stage 1–3，才在 Stage 4 判人機互動風險，順序太晚

### 證據

- `README.md:160-173` 規定 Fast lane 直接從 4-spec 起跑，跳過討論與原型。
- `skills/dev-flow/SKILL.md:119-120` 對 fast lane 無 1/3 檔直接判 legacy/N-A 放行。
- `_templates/4-spec.md` 雖有 Operational Context 與「高風險人機互動 → Full」的規則，
  但 lane 已在進 Stage 4 前選完；而「高風險人機互動」沒有一個先於 lane 選擇的具體盤點。

### 會怎麼失效

「只改一個按鈕」「修一個狀態字」可以只有一兩個檔，卻可能讓沒有權限的人誤以為已核准、
把等待誤顯示為完成，或破壞中斷恢復。它會因檔案少／bugfix 先進 Fast lane，沒有 Actors、
Journey、Demo，再靠一條技術重現 scenario 出貨。

### 候選決定（待 owner 裁）

- lane 選擇前加一個**最小 interaction triage**：是否改變下一步、權限／核准、等待／完成
  語意、角色交接、系統外動作、中斷恢復。全否且行為已有 approved spec 才可直接 fast。
- 命中不必一律跑整套 full：owner 可裁「升 full」或「fast + mini real-world delta」；
  mini 至少要寫 Actor、實際工作影響、權限／等待／例外與代表性驗證方式。
- 已有 approved spec 且只是純視覺、不改語意的 bug 可維持 fast，避免把小修全拖進訪談。

### 機械化判斷

可要求 Fast lane 4-spec 帶結構化 triage 結果，命中卻無 full／mini／Owner Call 即拒；
是否真的「不改語意」仍由 reviewer 查 diff 與既有 spec。不能只靠檔案數判互動風險。

## 本區 owner 裁決格式（建議）

每條只要補一行，避免把候選直接改寫成既定事項：

```text
- A-1: 採 / 不採 / 改案 — 理由；若採，指定落點與是否要機械守衛
```

若採用，建議另開一份新的 dispatch／feature，而不是把本區混進上面「四項已定」的驗收；
這九條會改 `dev-talk` 的核心契約、Stage 1–4 模板與範例，應獨立走 G1/G2，並保留現行
real-world 機制的回歸基準。
