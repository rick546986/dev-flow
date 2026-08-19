---
feature: contract-expiry-reminder
stage: 4-spec
status: approved
owner: <owner>
reviewers: [<reviewer-b>]     # G2 由 <reviewer-b> 審(≠owner)
updated: 2026-07-23
---

# 4. 規格 — 合約到期提醒(change spec)

## ADDED Requirements

### R-1: 系統 SHALL 在 dashboard 顯示登入者可見、30 天內到期且未續約的合約卡片
#### S-1
- GIVEN 登入業務 `<owner>` 名下有合約 C,`end_date = today + 10d`,未續約
- WHEN `<owner>` 開啟 dashboard
- THEN 到期卡片列出 C,顯示合約名稱與剩餘天數「10 天」
- 觀測:從 `<owner>` 的 dashboard 到期卡片看 | 看到 C 與「10 天」算對 | 用 C(`end_date = today + 10d`,未續約)測
- Operational Context:
  - Actor:負責業務 `<owner>`
  - Goal:不漏約;登入第一眼決定今天要跟催哪件
  - Situation:每日登入;可能同時多件到期,亦可能剛被改派接手別人的合約
  - Known information:合約名稱、剩餘天數、目前處理狀態與下一步
  - Missing information:法務審閱進度(在 Email)、對方窗口意向(在電話)
  - Human decision:先跟催哪一件;要不要升級找主管
  - Authority:讀寫名下合約;不可代表公司拍板非標準價格
  - External dependency:法務回覆、供應商窗口回覆
  - Out-of-system action:Email 合約給法務、電話聯絡供應商
  - Waiting/timeout behavior:等待中合約持續顯示於卡片並標等待對象,不因等待而消失(逾時自動升級提醒 = Out of Scope)
  - Recovery:中斷後重開 dashboard,狀態與下一步仍在(狀態存於系統,非頁面 session)
  - Audit/handoff requirement:狀態變更記誰在何時標(改派後新業務可接手,不必 Email 考古)
  - Observation:卡片列含狀態欄與下一步欄(見 S-4 觀測)

#### S-2
- GIVEN `<owner>` 名下無 30 天內到期的合約
- WHEN `<owner>` 開啟 dashboard
- THEN 卡片顯示空狀態「近期無到期合約」,不顯示錯誤
- 觀測:從 `<owner>` 的 dashboard 到期卡片看 | 看到「近期無到期合約」且無錯誤算對 | 用名下無 30 天內到期未續約合約的 `<owner>` 測
- Operational Context:
  - Actor:負責業務(名下無到期合約)
  - Goal:確認今天不需要跟催
  - Situation:每日登入例行確認
  - Known information:空狀態文案
  - Missing information:無
  - Human decision:無(空狀態=今天無續約動作)
  - Authority:同 S-1
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不適用
  - Recovery:不適用
  - Audit/handoff requirement:不適用
  - Observation:空狀態文案與錯誤狀態可區分(錯誤走查詢失敗呈現,非空狀態)

### R-2: 卡片中每筆合約 SHALL 可點擊導向該合約詳情頁
#### S-3
- GIVEN 到期卡片列出合約 C
- WHEN `<owner>` 點擊 C 那一列
- THEN 導向 `/contracts/C.id` 詳情頁
- 觀測:從 C 那一列與瀏覽器 URL 看 | 點擊後 URL 為 `/contracts/C.id` 且顯示 C 詳情算對 | 用 S-1 的到期合約 C 測
- Operational Context:不適用(單純導覽,無等待/權限差異/系統外動作;人的決策已由 S-1 涵蓋)

### R-3: 系統 SHALL 記錄合約處理狀態與下一步,且狀態僅由明確標記動作改變
#### S-4
- GIVEN 到期卡片列出合約 C,狀態「未處理」;登入者為負責業務 `<owner>`
- WHEN `<owner>` 在 C 列將狀態標為「等待法務」
- THEN C 列顯示狀態「等待法務」、下一步「等法務回覆條款」與最後動作時間;狀態歷程新增一筆(`<owner>`、時間、未處理→等待法務)
- 觀測:從 C 列狀態欄/下一步欄與狀態歷程看 | 標記後顯示「等待法務」「等法務回覆條款」與時間、歷程多一筆算對 | 用 S-1 的合約 C 測
- Operational Context:
  - Actor:負責業務 `<owner>`
  - Goal:把「進行到哪、在等誰」從腦中/Excel 移進系統
  - Situation:剛把合約寄給法務,接下來幾天都在等
  - Known information:自己剛做了什麼(寄出合約)
  - Missing information:法務何時回(系統外 Email)
  - Human decision:標哪個狀態;等多久要催
  - Authority:業務可標等待類與「不續約」;「已續約」僅主管可標(見 S-6)
  - External dependency:法務回覆
  - Out-of-system action:Email 合約給法務;之後電話聯絡供應商(狀態「已聯絡供應商」記錄之)
  - Waiting/timeout behavior:狀態停在「等待法務」並持續顯示,系統不自動轉移、不自動視為完成
  - Recovery:標到一半關頁重開 → 狀態為最後一次成功標記值;可再次標記修正(誤標可改標回前值,歷程留兩筆)
  - Audit/handoff requirement:歷程含誰/何時/從何狀態到何狀態;改派後新業務讀歷程即可接手
  - Observation:C 列狀態欄/下一步欄/最後動作時間 + 詳情頁狀態歷程
#### S-5
- GIVEN 合約 C 狀態「未處理」
- WHEN `<owner>` 開啟 dashboard 看過到期卡片兩次,未做任何標記動作
- THEN C 狀態仍為「未處理」;狀態歷程零新增(不存在「看過即處理」的自動變更)
- 觀測:從 C 列狀態欄與狀態歷程看 | 兩次開啟後仍顯示「未處理」且歷程零新增算對 | 用 S-1 的合約 C 開 dashboard 兩次測
- Operational Context:
  - Actor:負責業務 `<owner>`;下游讀狀態的是主管與接手業務
  - Goal:防「看過提醒」被誤當「完成續約」
  - Situation:業務每天看卡片但未必當天動作
  - Known information:卡片上目前狀態
  - Missing information:無
  - Human decision:看過後可以不動作,不因此背上「已處理」標記
  - Authority:同 S-4
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:「未處理」持續顯示直到有明確標記
  - Recovery:不適用(無狀態變更即無恢復問題)
  - Audit/handoff requirement:歷程零新增即為證據(看過不留「已處理」假象)
  - Observation:狀態欄 + 狀態歷程筆數
#### S-6
- GIVEN 合約 C 狀態「已聯絡供應商」;登入者為負責業務 `<owner>`(非主管)
- WHEN `<owner>` 嘗試將 C 標為「已續約」
- THEN 系統拒絕:「已續約」選項灰階並顯示「已續約僅主管可標」;C 狀態不變、歷程零新增
- 觀測:從 C 列狀態選單與狀態欄看 | 「已續約」灰階、提示字樣出現、狀態仍「已聯絡供應商」算對 | 用非主管帳號 `<owner>` 對 S-4 的合約 C 測
- Operational Context:
  - Actor:負責業務 `<owner>`(嘗試者);業務主管(有權者)
  - Goal:結案定案權留在主管(對應核准權,1-discussion Q5)
  - Situation:談成後業務想直接結案
  - Known information:目前狀態、談判結果(口頭)
  - Missing information:主管是否同意定案
  - Human decision:主管決定是否標「已續約」
  - Authority:「已續約」僅主管;業務可標其餘狀態
  - External dependency:主管確認
  - Out-of-system action:LINE/口頭通知主管來標
  - Waiting/timeout behavior:狀態停在「已聯絡供應商」直到主管動作
  - Recovery:不適用(拒絕操作無副作用)
  - Audit/handoff requirement:「已續約」歷程必然記到主管名下(結案責任可追)
  - Observation:灰階選項 + 提示字樣 + 狀態不變

## MODIFIED Requirements
(無 —— 不改既有行為)

## REMOVED Requirements
(無)

## 行為流程圖(R 級)
```
[R-1] dashboard 顯示到期卡片
  登入 -> 開啟 dashboard -> GET /contracts/expiring?days=30
    -> 查詢結果
      = 有到期合約 -> 卡片列出 [名稱 + 剩餘天數]
      = 無到期合約 -> 空狀態 [近期無到期合約]

[R-2] 卡片列可點擊導向詳情
  卡片列出到期合約 C -> 使用者點擊該列 -> 導向 /contracts/C.id

[R-3] 處理狀態僅由明確標記改變
  卡片列 C -> 標記動作(等待法務/等待主管/已聯絡供應商/不續約)
    -> 權限檢查
      = 通過 -> 更新狀態 + 下一步 + 最後動作時間 + 歷程一筆(誰/何時/舊→新)
      = 「已續約」且非主管 -> 拒絕(灰階 + 提示), 狀態不變
  卡片列 C -> 僅開啟/看過 -> 狀態不變, 歷程零新增
```

## Acceptance Criteria
- S-1 ~ S-6 測試全綠。
- dashboard p95 載入延遲增加 < 100ms(8k 筆量級,EXPLAIN 驗證走索引)。

## Out of Scope
email/LINE 通知、自訂天數、主管彙總報表、自動寄信給法務/供應商、逾時自動升級提醒、法務簽核流程系統化。

Stage 3 對帳(逐場核對 3-prototype Demo Script;第 2 輪 Human verdict: ACCEPTED)—— 下列兩場已 ACCEPTED 的場景本期不形成 R/S,理由與已知風險逐條明列,不默默刪場景:
- 錯誤狀態:`GET /contracts/expiring` 失敗時的專用呈現與重試按鈕(3-prototype「Scenario AC-1(錯誤狀態:expiring 查詢失敗)」)。理由:本期 R-1 只把查詢成功後的「有到期合約 / 無到期合約」兩路徑展開為可測 S(S-1、S-2),失敗路徑的卡片呈現與重試互動未展開,亦不在 Diff Budget 的九檔內。已知風險:查詢失敗若退化成空狀態,業務會誤判「今天沒有到期合約」而漏跟催 —— 正是 Demo 當場提出的觀察問題;補上該 S 之前,失敗期間仍靠 1-discussion/3-prototype 記錄的 Excel 私表 workaround 兜底。S-2 觀測欄只界定「空狀態不是錯誤狀態」,不構成對錯誤呈現的要求。
- 資料過期/併發編輯:偵測他人已改動後拒絕以過期資料標狀態、提示重新整理(3-prototype「Scenario AC-1(資料過期)」)。理由:本期狀態寫入走單一交易,Dependencies 的 migration 只加 `renewal_status` 與狀態歷程表,沒有版本欄或樂觀鎖;要做需另立衝突偵測契約,超出本次 Diff Budget。已知風險:卡片開著隔夜、期間他人改了 `end_date` 或狀態時,後手的標記會以過期畫面覆蓋,歷程雖留兩筆但無衝突提示。S-4 的 Recovery 只涵蓋「自己中斷後重開」,不涵蓋「他人同時改動」;Verification Profile 排除 Race/stress 層排除的是新增併發寫入路徑,不等於已處理本項的 stale read。

Owner confirmation:rick 確認上列兩場已 ACCEPTED 的 Demo 場景明示排除於本期交付範圍(裁決留痕,不新增 R/S,亦不產生任何 TDD Evidence)。

## Diff Budget
≤ 9 檔 / ≤ 600 行(API handler+service+query、狀態 API+migration、前端卡片元件+route、測試)。

## Dependencies
需 migration:`contracts.renewal_status`(enum:未處理/等待法務/等待主管/已聯絡供應商/已續約/不續約)+ 狀態歷程表(contract_id、誰、何時、舊→新)。不依賴其他 feature。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: applicable
- Trigger(s): 新增公開 API(`GET /contracts/expiring`、`PATCH /contracts/:id/status`)、schema migration 與新資料所有權(`contracts.renewal_status` + 狀態歷程表)、涉 Transaction 與 Concurrency/Idempotency(狀態與歷程同交易、stale write)、Feature Risk = high、三個以上模組共同參與(handler / service / repo / dashboard UI)
- Design source: 既有 pattern —— `internal/{handler,service,repo}` 三層與 `ExpiringContractsCard` 元件慣例;本次新增的狀態寫入路徑與歷程表為 new local design(無既有 ADR)

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| Dashboard UI(`src/components/ExpiringContractsCard.tsx`、`src/pages/Dashboard.tsx`) | 呈現到期卡片、狀態欄/下一步欄與列內標記選單;依後端回應把「已續約」灰階並顯示提示 | 不擁有任何資料(僅呈現) | → Contract API(HTTP) | 不得直接觸 DB;不得自行推導權限結論以外的狀態(權限正本在 API 層) |
| Contract API handler(`internal/handler/contract.go`、`internal/handler/contract_status.go`) | 端點入口;在此層強制「已續約僅主管」授權(非主管一律拒絕);把 service/repo 的錯誤轉成 HTTP 回應 | 不擁有資料(委派 store) | → Contract query service、→ Contract status store | 不得繞過 service 自行組查詢;GET 路徑不得寫入 |
| Contract query service(`internal/service/contract.go`) | 到期查詢邏輯 `service.ListExpiring`(抽出以供未來 cron 複用) | 不擁有資料(唯讀) | → Contract read repo | 不得寫入任何欄位或歷程 |
| Contract read repo(`internal/repo/contract.go`) | 讀 `contracts`,複用既有 `idx_contracts_end_date` | 不擁有 `contracts`(既有欄位由既有合約模組擁有,本次不改) | → DB(讀) | 不得寫 `contracts` 既有欄位 |
| Contract status store(`internal/repo/contract_status.go`、`migrations/0007_renewal_status.sql`) | 唯一寫入 `contracts.renewal_status` 與狀態歷程表的地方;維持「狀態變更必留一筆歷程」的不變量 | **擁有** `contracts.renewal_status` 與狀態歷程表 | → DB(讀寫,單一交易) | 不得被 UI 或 service 繞過直呼;不得由任何 GET 路徑進入寫入分支 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| `GET /contracts/expiring?days=30` | in:登入身分 + `days`;out:登入者名下 30 天內到期未續約合約列表(名稱、剩餘天數、狀態、下一步、最後動作時間);零筆 → 200 + 空列表 | 查詢失敗回非 2xx;**前端本期無專用錯誤呈現**(已列 Out of Scope),錯誤與空狀態在 UI 上可能不可區分 → 見 Known design limit | 唯讀:不開交易寫入,任何讀取路徑對狀態與歷程零副作用(S-5 以歷程筆數斷言) | additive —— 新端點,無既有呼叫端 |
| `PATCH /contracts/:id/status` | in:合約 id + 目標狀態(6 值域之一);out:更新後狀態、下一步、最後動作時間 + 歷程新增一筆(誰/何時/舊→新) | 非主管標「已續約」→ 403,狀態不變、歷程零新增;UI 對應灰階選項 + 「已續約僅主管可標」提示 | **狀態更新與歷程寫入在同一交易**(只成功一筆不可能發生);交易邊界止於 Contract status store,不跨模組 | additive —— 新端點,無既有呼叫端 |
| migration `0007_renewal_status` | 加 `contracts.renewal_status` enum 欄 + 新建狀態歷程表 | 演練 down/up 時 orphan rows > 0 即視為失敗(見 Failure Model) | schema 變更為單次 migration;既有 `contracts` 欄位不動 | additive —— 只加欄與加表,既有讀取路徑不受影響 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| `service.ListExpiring` | 依 `days` 與登入者算出到期未續約清單與剩餘天數 | ← handler;→ `repo.Contract` | stateless;讀 `contracts` → 回列表 | 讀取錯誤原樣往上傳,不吞成空列表 | `go test ./internal/... -run TestExpiring`(可注入固定 today 驗「10 天」) |
| `handler.PatchContractStatus` | 解析目標狀態、強制主管授權、呼叫 store、組回應 | ← HTTP;→ `repo.ContractStatus` | stateless;授權判斷不落地 | 授權失敗 → 403 並中止(不進交易);store 錯誤往上傳 | `go test ./internal/... -run TestRenewalStatus_S4`(權限分支) |
| `repo.ContractStatus` | 單一交易內寫狀態 + 追加歷程;唯一寫入點 | ← handler | 狀態住 DB;歷程 append-only(不覆寫、不去重) | 交易失敗整筆回滾,不留半套(呼叫端只看到成功或完全沒發生) | 交易邊界可測:`TestRenewalStatus_S4` 斷言「狀態值變更」與「歷程 +1」同時成立;在 repo 層注入寫入失敗即可驗回滾後狀態與歷程都不變。讀取零副作用由 `TestRenewalStatus_S5_ViewDoesNotComplete` 以歷程筆數斷言 |
| `ExpiringContractsCard` | 卡片列渲染、空狀態文案、列內標記選單與灰階提示 | ← `Dashboard.tsx`;→ Contract API | 前端不保存狀態真相,每次以 API 回應為準(中斷後重開即為最後成功值) | API 非 2xx 時本期無專用錯誤畫面(Known design limit) | `npm test -- ExpiringContractsCard`(S-2 空狀態、S-6 灰階提示) |
| `e2e/expiring-contracts.spec.ts` | 端到端證據:真瀏覽器走完登入 → 卡片 → 詳情,證明三層接起來真的會動 | → Dashboard UI(經瀏覽器);不直呼任何內部模組 | stateless;每次自建測試資料再清掉,不依賴殘留狀態 | 失敗即中止並保留 trace,**不吞錯、不重試**(重試會把 flaky 藏起來) | 本身就是 seam:`npx playwright test e2e/expiring-contracts.spec.ts`,斷言取值照 S-1／S-3 觀測欄 |

### Design Constraints

- 必須:狀態與歷程在同一交易寫入;`contracts.renewal_status` 與歷程表只由 Contract status store 寫;「已續約」授權在 API handler 層強制(UI 灰階只是呈現,不是防線);狀態值域固定 6 值。
- 禁止:任何 GET／讀取路徑進入寫入分支(含「已讀」記錄);UI 直接觸 DB;service 繞過 Contract status store 寫入。(產品行為排除見 Negative constraints／Out of Scope。)
- Extension point:`service.ListExpiring` 已抽出,未來 cron 可複用同一查詢(2-decision 已裁決);歷程表結構可承接後續報表,本期不做。
- Known design limit:
  ①**Stale write 無衝突偵測** —— 未設版本欄或樂觀鎖,兩人以過期畫面先後標記時後手覆蓋前手,歷程留兩筆但無衝突提示(對應 Reliability triage 的 Concurrency: applicable 結論;本期不引入衝突偵測)。
  ②**完整操作不保證冪等** —— 重送相同標記,狀態值收斂但歷程可能新增同值一筆(歷程 append-only、不去重、無 idempotency key);「狀態值收斂」≠「操作冪等」。
  ③**查詢失敗的前端呈現缺口** —— `GET /contracts/expiring` 失敗時無專用錯誤畫面,可能被誤讀為「今天沒有到期合約」(Stage 3 已 ACCEPTED 但本期排除的場景,理由見 Out of Scope)。
  三項皆為既有設計的顯性化,本期不新增樂觀鎖、idempotency key、重試 UI、新 API 或新 schema。

## Verification Profile(G2 一併審)
- lane: full(Risk: high 命中自動升 Full 清單,不得 fast;本節 Risk = Feature Risk,
  5-tasks 逐 T `Risk:` 欄 = Task Risk,判準同一正本)
- Risk: high(判準:公開 API(`GET /contracts/expiring`、`PATCH /contracts/:id/status`)+
  `renewal_status` migration 不可逆改動 + 權限行為(「已續約」僅主管)。T 級沿用同一判準:
  T-5(migration + 權限)標 `Risk: high`,其餘 T 缺省 normal,見 5-tasks)
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 看過/任何 GET 路徑不得改變狀態或新增歷程(1-discussion Q4;S-5)
  - 非主管不得標「已續約」(1-discussion Q5;S-6)
  - 不得自動轉移狀態、不得逾時自動升級(Out of Scope)
- Required layers:Full test suite、Changed-line coverage、Real execution
  (= 7-review 執行清單 2c gauntlet 命令的 `--require-layer` 清單,逐層一個 flag)
- Conditional layers:Types/compile(TS 檔變動觸發)、e2e(新前端互動流程觸發)、
  Rollback rehearsal(schema migration 觸發)—— 本次三者皆觸發,列入 Final Fresh Run
- Explicitly excluded layers:Mutation(本示範 repo 未配 mutation 工具鏈;實案 Risk: high
  應評估納入 Required)、Race/stress(狀態更新走單一交易,本次無新增併發寫入路徑)
- Final fresh entry point:`go test ./... && npm test && npx playwright test`
- Reliability triage:(Full 與 Fast lane 都必答)
  - Concurrency: applicable — 3-prototype 第 2 輪 ACCEPTED 的「資料過期」場景就是併發編輯:卡片開著隔夜、他人已改 `end_date` 或狀態。本期不做衝突偵測,已列 Out of Scope 並附 known risk(後手標記會以過期畫面覆蓋,歷程留兩筆但無衝突提示)。注意本節 Explicitly excluded 的 Race/stress 排除的是「新增併發寫入路徑」的壓力驗證層,與此處的 stale read 缺口不是同一件事,不得互相抵充。
  - Idempotency: applicable — 狀態欄位採 set-to-value(enum 六值,見 Drafting Decisions),重送相同標記後最終狀態值相同、且本次不新增任何對外副作用(自動寄信給法務/供應商、email/LINE 通知皆在 Out of Scope);但每次請求可能新增一筆同值歷程,因此「狀態值收斂」不等於「完整操作冪等」—— 完整操作目前不保證冪等。本期不新增 idempotency key,也不做歷程去重,列為 known limit;此裁決只把既有性質寫明,不新增產品行為。
  - Timeout/retry: applicable — 後端不外呼(聯絡法務與供應商皆為系統外動作,見 S-1/S-4 Operational Context),本期唯一相關面向是 `GET /contracts/expiring` 失敗時前端的重試互動;該項已列 Out of Scope 並附 known risk(失敗退化成空狀態 → 業務誤判無到期合約)。逾時自動升級提醒本就在 Out of Scope。

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 非主管標「已續約」成功(權限繞過) | 結案責任錯置、審計失真 | API 未回 403;「已續約」未灰階 | Full test suite(`TestRenewalStatus_S4` 權限分支 + vitest S6) | — |
| 「看過」觸發狀態自動變更 | 等待被誤標完成 → 漏跟催重現 | 歷程零新增斷言失敗 | Full test suite(`TestRenewalStatus_S5_ViewDoesNotComplete`) | — |
| migration 損及既有合約資料或不可回滾 | 8k 筆合約狀態受損 | down/up 演練 orphan rows > 0 | Rollback rehearsal | — |
| 狀態欄位加入後到期查詢變慢 | dashboard p95 超 100ms(AC) | EXPLAIN 不走索引、p95 上升 | Real execution(EXPLAIN + p95 量測) | — |

## Drafting Decisions(草擬自判,已裁決)

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | 剩餘天數顯示「N 天」不含小時(棄項:精確到時分) | 業務以天為單位追 | `1-discussion.md:35` Current Journey Step 1 記業務「月初翻 Excel 私表比對到期日」= 以天為單位;顯示精度無使用者反饋 = `[Assumption]` | S-1 THEN 的「10 天」字樣與前端格式化都要改 | ✅ |
| DD-2 | S-2 空狀態文案寫死於 spec(棄項:留給前端自由) | 驗收要可測,文案不可漂 | `2-decision.md:66` OC-3 已裁定零筆仍顯示空狀態卡片;文案逐字寫死是本階段延伸 = `[Assumption]` | S-2 變成不可測,7-review 現象證據那列要改判準 | ✅ |
| DD-3 | 狀態值域固定 6 值:未處理/等待法務/等待主管/已聯絡供應商/已續約/不續約(棄項:自由文字狀態) | 可測、可報表 | `1-discussion.md:36-38` Current Journey Step 2-4 的「等待誰」欄依序是業務主管、法務、外部窗口(供應商);「6 值剛好夠」= `[Assumption]`,未窮舉真實案例 | R-3 全部 S 與 migration 的 enum 都要改,已寫入的資料要轉換 | ✅ |
| DD-4 | 「已續約」僅主管可標(棄項:業務可標+事後稽核) | 對應核准權 | `1-discussion.md:77` Q5 已定案「已續約」僅主管可標;`3-prototype.md:139` Permission corrections 記「修正為僅主管可標」 | S-4 權限分支與 Failure Model 第 1 列都要改 | ✅ |
| DD-5 | 看過不改狀態,無「已讀即處理」(棄項:自動標已讀) | 防看過誤當完成 | `3-prototype.md:128` AC-5 場景 3/3 參與者實測確認 | S-5 整條反過來,Failure Model 第 2 列失效 | ✅ |

### 內部技術選擇(下層,告知即可)
(無 —— 本次純內部技術選擇已在 `2-decision.md` 的下層清單記過,不重複記)

## Test Skeletons(選配)
```go
func TestExpiring_S1(t *testing.T) {
	// GIVEN 登入業務 <owner> 名下合約 C, end_date = today+10d, 未續約
	// WHEN <owner> 開啟 dashboard (GET /contracts/expiring?days=30)
	// THEN 到期卡片列出 C, 顯示名稱與剩餘天數「10 天」
	t.Skip("skeleton - see 4-spec S-1; S-2/S-3 由前端 vitest 承接,見 6-implementation-notes")
}

func TestRenewalStatus_S5_ViewDoesNotComplete(t *testing.T) {
	// GIVEN 合約 C 狀態「未處理」; WHEN 開 dashboard 看過兩次不標記
	// THEN 狀態仍「未處理」且歷程零新增(看過 ≠ 完成)
	t.Skip("skeleton - see 4-spec S-5; S-4/S-6 同 R-3 一組")
}
```

## 確認紀錄
- R 範圍確認 | 2026-07-23
- S 逐段確認完成 | 2026-07-23
- Operational Context 逐 S 確認(承接 3-prototype 第 2 輪 Demo ACCEPTED)| 2026-07-23
- Verification Profile 填畢確認(Risk: high;Required 三層 = 2c `--require-layer` 清單)| 2026-07-23
