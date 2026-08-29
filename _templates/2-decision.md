---
feature: <slug>
stage: 2-decision
status: draft
verdict:             # 空 | PASS | REQUEST_CHANGES | HOLD(Human 判定;全勾不算 PASS)
owner:
reviewers: []        # G1 核准者,不可 = owner
updated:
---

# 2. 收斂 — 方案決策

> 用途:把 1 的發散收成一個選定方案。**G1 gate:人工核准後才寫規格**。
> 本階段固定產出:`2-decision.md`(本模板全節)+ `2-decision.html`(G1 必產;必含
> 方案架構圖、Approaches+Rejected、Owner Calls 待裁決置頂);三條件中 → 另抄 `docs/adr/`。
>
> ## G1 twin 是**審查介面**,不是文件視覺版(README §6)
>
> 三件事缺一不可 —— **產 html 時逐項對照,缺一項就是沒做完**:
>
> | | 要求 | 這一站的內容 |
> |---|---|---|
> | 1 | **動線頂區五格**,每格一句話 + 可點跳轉,審完五格才決定要不要往下讀 | 判定(`## Decision` 首句)/ Owner Calls(已裁決 `x/y`)/ 方案(幾項待審)/ 駁回理由(幾條)/ 狀態(frontmatter) |
> | 2 | **待審項目逐條可勾**,有進度計數,缺必填欄的直接在卡上現形 | 每個 Approach 一張卡、每條 Owner Call 一張卡 |
> | 3 | **背景資料摺疊**(`<details>`,預設收合、內容零刪減) | 既有脈絡、被駁回方案的完整論述、影響面清單 |
>
> 產生方式:`docs/dev/tools/build-gate-twin.py <專案根> <slug> 2-decision`
> (母版在 `scripts/`)。它讀 md 逐條解析,不手抄;解析不到任何一條會直接失敗。
> 審頁(分組卡:Decision 置頂 + 直式 SVG 置中 max-width:360px + 每決策點 `.r-block`
> 內表格 A/B/C 卡,背景摺疊)另一支:`scripts/build-stage2-html.py`(--action 授權)。正本
> `notes/design/stage2-review-ui-contract.md`。不要「勾選提示」「你要審什麼」
> Rejected 釘頂那版,不要手包 html-shell。
>
> 執行清單(開場第一動建成 todo;逐步達成「完成 =」才勾;禁跳項、禁併項):
> 0. 接手盤點:只讀 1-discussion.md(對話不是契約)+ 長期記憶查詢結果(業務語意)。核 status=approved、
>    OQ 全三態;缺 → 退回討論。從 Goals/驗收雛形/[>] 移交項提煉「待收斂決策點」,
>    連同討論期 owner 已自拍的板一併清點。
>    完成 = 決策點清單經使用者確認(確認紀錄節留一行)。
> 1. 方案生成:每決策點 2-3 個 approach 填表,禁單案過場;優劣必有背書 ——
>    引 1-discussion 事實或本階段查證,寫進「依據」欄;引不出就在該欄寫
>    `[Assumption]`,不得留空、不得憑空斷言。完成 = 表齊、每格非空。
> 2. 壓測定案:對推薦案逼問失敗模式/邊界/最貴風險 → Risks & Mitigations(每風險
>    有對策);Success Criteria 逐條可量測(7-review 對照用)。完成 = 兩節齊、
>    無不可量測句。
> 3. 定稿:Decision 一句話+範圍、Rejected 逐案一句棄因、Rationale、Scope & Non-Goals。
>    晚改可見行為(開工後或自稱「完工」但 G3 未過 / 已過 G3):
>    G3 未過 → 同一 feat。先改本檔 Decision / Owner Call,再走 4→5→6→7。
>    1-discussion 保留當時說法,另記後來改口;不准假裝第一次裁決本來就是新的。
>    G3 已過 → 另開薄刀 feat/delta,不准改已封包。
>    純文字、行為不變 → 原包 HISTORY。
>    推翻已核 Decision 不是合法 DD;回本站。DD 寫「不採 2-decision /
>    兩份並存 / 產品跟 4-spec 不跟 Decision」= 流程 bug。
>    完成 = 節全齊、無佔位符。
> 4. Owner Calls 清點:owner 沒問使用者、自己拍的板逐條收進 Owner Calls 節
>    (收錄判準見該節註;上層逐條 OC-n,下層內部項一段帶過)。特別掃兩型必收必標:
>    裁決延伸(使用者只被問到 X,owner 套到 Y/Z)、裁決收窄(使用者要 A,
>    實作成 A 減某部分)。完成 = 步 6 第⑥掃的歸屬雙向對應成立。
> 5. ADR 晉升檢查:三條件逐條答;全是 → 抄 docs/adr/。完成 = 三答落檔。
> 6. 自檢(交審前重讀全檔):①每案優劣有背書?②Decision 覆蓋 1 的每條 Goal
>    (漏的進 Non-Goals)?③[>] 移交項都有著落?④Success Criteria 可量測?
>    ⑤Rejected 無空棄因?⑥歸屬雙向對應:正向 — 步 0 每個決策點皆有使用者
>    裁決(確認紀錄有痕)或 ≥1 條 OC 承接(一對多合法)?反向 — 每條 OC(上層、
>    下層皆算)皆可追溯到某決策點,或標「流程層」?延伸/收窄算新增決策點。
>    任一向斷鏈 = 漏收或無主。問題 → 改檔或回步 1。⑦現況外移:產出有無
>    成段/成表的「是什麼」內容(描述系統現況或既有結構——schema、資料字典、
>    介面清單——而非本次決策)?有 → 外移 docs/specs/,本檔只留決策與為什麼。
>    完成 = 七掃清零(⑥含雙向對應成立)。
> 7. G1 送審:html twin(方案架構圖,比較期並排;OC 待裁決置頂)→ in-review →
>    reviewer。審查者依序:適格人類 reviewer → fresh-context reviewer Agent →
>    owner 自審(有記錄的最後手段)。G1 = 方向核准 +
>    Owner Calls 全裁決(有未裁決 OC 不得過;正本 README §7)。核准 → 三連動
>    (frontmatter/STATUS/twin)。完成 = verdict 記錄+三連動齊。

## Approaches Considered
<!-- 「依據」欄:本列的優/劣/成本從哪來 —— 寫得出出處就寫 `檔:行`、1-discussion 的
     哪一條、或實際跑過的指令輸出;寫不出就寫 `[Assumption]`。
     沒有依據不是不能寫,是不能寫得像有依據(同 1-discussion 的 [Assumption] 規則);
     整欄不得留空,這欄是 G1 判斷「這張表哪幾格是模型猜的」的唯一依據。 -->
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A |  |  |  |  |  |
| B |  |  |  |  |  |

## 方案架構圖
<!-- 每案一張或並排比較(比較期);判準同 README §6:純線性/單層樹 → ASCII
     (半形 | - + > < = [ ]);方塊+連線空間關係 → html 用 SVG(md 留 ASCII 正本)。
     gate 前必有。選定案必須在圖上標「選定」;Rejected 的案若上圖,不得標選定。
     Decision／Rejected 改選定,圖的選定標必須一起改。 -->

## Decision
<!-- 一句話選定 + 範圍 -->

## Rejected Alternatives
<!-- 逐個一句為何不選(未來翻案時省一輪重新調查) -->

## Rationale
<!-- 為何 Decision 贏 -->

## Risks & Mitigations
<!-- 選定方案的風險 + 對策;技術疑問留給 3-prototype 驗 -->

## Success Criteria
<!-- 可量測,7-review 對照 -->

## Scope & Non-Goals(定稿)

## Owner Calls(自判裁決,待人審)
<!-- owner 沒問使用者、自己拍的板。G1 過關條件之一 = 本節全裁決;✗ 打回重擬。審後保留(審計軌跡)。
     收錄判準(適用 feature/bugfix/refactor,不分領域):
     - 收:spec/討論未載明、owner 自選,且 approver 不同意會改變交付內容或流程。
     - 收:把使用者裁決**延伸**到沒被問到的範圍 → 必標「使用者只被問到 X,Y/Z 是 owner 延伸」。
     - 收:對使用者裁決的**收窄**(使用者要 A,實作成 A 減某部分)→ 必寫收窄依據。
     - 不收:Approaches 已並排比較、由使用者裁決的 → 那是 Decision,不是自判。
     - reviewer 相關分兩種:reviewer 指定了解法 → 不收(屬審查紀錄);
       reviewer 只指出問題、owner 自選解法 → 收。
     - 不收:可逆的風格偏好(格式、註解措辭)。
     兩層:會改變使用者可見行為/交付範圍/流程 → 上表逐條審;純內部技術選擇
     (資料結構寫法、索引型式、命名慣例)→ 下方清單告知即可。
     流程層:改變流程而非交付內容的自判(例:跳過某 stage)→ 照收上層並標
     「流程層」,不要求對應步 0 決策點。
     拿不準放上層或下層 → 一律放上層(同 README §5 判級疑義原則) -->

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 |  |  |  |  |  |

### 內部技術選擇(下層,告知即可)
<!-- 一行一項;approver 掃過即可,不逐條裁決 -->

## ADR 晉升檢查
<!-- 三條件全「是」才抄進 docs/adr/(用 _templates/adr.md) -->
- 難逆轉:否/是
- 反直覺:否/是
- 真 trade-off:否/是
→ 晉升:否 / 是(docs/adr/NNNN-<slug>.md)

## 確認紀錄
<!-- 過程留痕,一行一筆(項目 | 日期),如「決策點清單確認 | 2026-07-25」 -->
