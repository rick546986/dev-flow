# Design Boundary Contract — 條件式設計契約(Stage 4 內章節)

> **本檔 = Design Boundary Contract 的語意正本**:觸發條件、欄位語意、好壞範例、
> 邊界歸屬、`n-a` 的合法與非法寫法。
> **填寫用的表格骨架正本**住 `_templates/4-spec.md` 的同名章節;
> README §3 只留一段摘要與本檔連結,不重抄。
>
> 三句先立不變量:
> ①**不是新 Stage**。本章節是 Stage 4 的一部分,由既有 **G2** 一併審,不新增 Gate。
> ②**不新增 ID 鏈**。沿用既有 `R-` / `S-` / `T-`、既有 Module 名與 Interface 名;
> 不發 Boundary-id、Component-id、Interface-id。
> ③**不新增產品行為**。本章節只把「既有設計與已知限制」顯性化;要新增行為必須走
> R/S 與 G2,不得藉本章節夾帶。

## 0. 缺口與定位

DevFlow 原本從 4-spec(可測契約)直接跳到 5-tasks(可勾選任務)。中間這一段
——「這些行為要落在哪些模組、資料歸誰、依賴往哪個方向、跨模組介面長怎樣、
一致性邊界在哪、元件怎麼分責、測試接縫留在哪」——沒有契約,只能靠實作者臨場發揮。
結果是同一份 spec 交給不同執行者會長出不同架構,而 Stage 7 的 Spec Axis 只能對照
R/S,無從判斷架構有沒有漂。

Design Boundary Contract 補的就是這一段,且**只補這一段**:

| 本章節做 | 本章節不做 |
|---|---|
| 說清楚本次變更的模組邊界與依賴方向 | 畫全系統架構圖 / 大型 UML |
| 說清楚資料所有權與一致性邊界 | 重寫 living spec 或既有架構決策 |
| 說清楚公開介面的相容策略 | 取代 ADR(長命決策仍住 `docs/adr/`) |
| 說清楚元件分責與測試接縫 | 取代 Reliability Triage / Failure Model / Operational Context |
| 誠實列出 Known design limit | 藉「顯性化」偷渡新產品承諾 |

**小改不必寫巨型文件。** 命中觸發條件的小型 Feature,三張表各一到兩列就是合格產出;
全部未命中時合法寫 `n-a` + 具體理由(規則見 §5)。

## 1. 觸發條件(Applicability)

以下任一命中,Design Boundary Contract **必須**填寫(`Applicability: applicable`):

| # | 觸發條件 | 命中時至少要說清楚 |
|---|---|---|
| 1 | 跨模組或跨 bounded context | 依賴方向、禁止方向 |
| 2 | 新增或修改公開 API | 相容策略(Compatibility 欄) |
| 3 | 新增或修改跨模組 Interface | Input/Output、Errors、相容策略 |
| 4 | Schema migration 或資料所有權變更 | Data owner、Transaction/Consistency boundary |
| 5 | 新增 Queue／Event／Scheduler／Background job | 誰觸發、誰消費、失敗落在哪個 Boundary |
| 6 | 新增外部服務或系統整合 | 邊界在哪隔離、錯誤如何傳遞 |
| 7 | 涉及 Transaction、Concurrency、Lock、Idempotency | Transaction/Consistency boundary + Known design limit |
| 8 | 新增 Network／Filesystem／Subprocess／Credential capability | 該 capability 被哪個 Boundary 持有、禁止誰直接用 |
| 9 | Feature Risk = high(4-spec Verification Profile) | 全三表 |
| 10 | 有三個以上模組共同參與主要行為 | Architecture Boundaries 表逐模組 |
| 11 | 有狀態機或複雜錯誤恢復流程 | State/Data flow + Error handling + Test seam |

**Fast lane 規則**:Fast lane **預設**可以 `n-a`,但命中上述任一條時**仍必須填**;
不得以「這是 fast lane」當跳過理由。

但要說清楚它與「自動升 Full」的實際關係,別給人錯誤預期(2026-08 校正:先前寫成
「多與自動升 Full 重疊」是不準確的):

| | 觸發條件 | 與 4-spec「自動升 Full」清單的關係 |
|---|---|---|
| 已被 lane 攔下 | ②公開 API、④schema migration、⑧新 capability、⑨Risk high | 命中即自動升 Full,**根本不會是 fast lane**,所以這四條對 fast lane 沒有額外負擔 |
| lane 攔不到 | ①跨模組、③跨模組 Interface、⑤Queue/Event/Scheduler、⑥外部整合、**⑦的 Idempotency 部分**、⑩三模組以上、⑪狀態機 | **可以在合法的 fast lane 變更上命中** —— 這七條才是 fast lane 真正會遇到的 |

⚠️ **⑦是唯一被拆開的一條**(2026-08 fresh review F-6 校正):觸發條件⑦是
「Transaction/Concurrency/Lock/**Idempotency**」,但 `_templates/4-spec.md`
「自動升 Full」清單只涵蓋到「並發/鎖/排程」與「金流/交易」——
**沒有 Idempotency**。因此「只補一個 idempotency key、不涉交易與並發」這類變更
**可以合法走 fast lane**,卻仍命中觸發條件⑦而必須填本章節。
先前把整條⑦寫在「已被 lane 攔下」是錯的,會讓人以為 fast lane 完全不會遇到⑦。
（不改 lane 語意:要不要把「冪等」加進自動升 Full 清單是 lane 規則的獨立決定,
正本在 `_templates/4-spec.md`「Lane 規則」節,不在本檔改。）

對第二類,規則不放寬(仍必須填),但**填法明確放寬**:fast lane 命中時允許
**最小填法** —— 三張表**只填與該變更直接相關的那一到兩列**,用不到的表寫 `—`,
Design Constraints 只寫「禁止」與「Known design limit」兩項。
判準:一個 ≤2 檔的 bugfix 若跨了模組邊界,它需要的是「別把依賴方向弄反」這一句,
不是一份架構文件。要求超過這個程度就是把 fast lane 拖成 full lane,屬於設計錯誤。

**與 Feature Risk 的關係**:`Risk: high` 是觸發條件之一(第 9 條),不是唯一條件。
`Risk: normal` 但命中第 1～8、10、11 任一條,一樣要填。

## 2. 欄位語意

### 2.1 抬頭三行

| 欄 | 語意 | 合法值 |
|---|---|---|
| `Applicability` | 本章節這次要不要填 | `applicable` 或 `n-a — <具體理由>` |
| `Trigger(s)` | 命中了 §1 的哪幾條(寫條件本身,不是條號流水帳) | `applicable` 時必須非空;`n-a` 時寫 `—` |
| `Design source` | 這次設計是沿用既有 pattern／ADR／living spec,還是本地新設計 | 既有出處(檔名或 ADR 編號),或 `new local design` |

`Design source` 的用途:讓 Stage 7 reviewer 知道該拿什麼當基準對照。寫
`new local design` 不是缺點,是誠實訊號 —— 代表本次沒有既有 pattern 可循,
Reviewer 應加重審視。

### 2.2 Architecture Boundaries(架構邊界)

| 欄 | 語意 | 寫法紀律 |
|---|---|---|
| Boundary / Module | 參與本次行為的模組或邊界名 | 用 repo 裡實際存在的名字,不自創抽象層名 |
| Responsibility | 這個邊界在本次行為裡負責什麼(一句) | 動詞開頭;不寫「處理相關邏輯」這種空句 |
| Data owner | 誰擁有這份資料的寫入權 | 一份資料只能有一個 owner;讀者不是 owner |
| Allowed dependencies | 本模組**可以**依賴誰 | 寫方向(`A → B`)或模組名清單 |
| Forbidden dependencies | 本模組**不得**依賴誰 | 這是負向約束,Stage 6/7 據此判 drift |

**Data owner 的判準**:誰負責維持這份資料的不變量,誰就是 owner。能讀但不能寫的
模組不是 owner;能寫但不負責不變量的(例如純轉發)也不是 owner —— 那代表設計有問題,
應在此處攤開。

**Forbidden dependencies 不得留空**。真的沒有禁止項就寫 `—`,但多數命中觸發條件的
變更都存在至少一條(最常見:UI 層不得直接觸資料層、Handler 不得繞過 Service 寫入)。

### 2.3 Interface & Consistency Contract(介面與一致性契約)

| 欄 | 語意 | 寫法紀律 |
|---|---|---|
| Interface / Flow | 對外或跨模組的介面、或一條完整流程 | 用實際端點/函式簽章名,例 `GET /contracts/expiring` |
| Input / Output | 進去什麼、出來什麼 | 型別或欄位層級,不寫「相關參數」 |
| Errors | 這條介面會產生哪些錯誤、錯誤語意是什麼 | 含錯誤如何被呼叫端辨識(狀態碼/錯誤型別) |
| Transaction / Consistency boundary | 哪些寫入必須同生共死;跨界之後是什麼一致性 | 明寫「同一交易」或「非同一交易 + 後果」 |
| Compatibility | 對既有呼叫端的相容策略 | `additive` / `breaking + migration 步驟` / `internal only` |

**涉及寫入時 Transaction / Consistency boundary 不得省略**,而且必須答得出
「這兩筆寫入如果只成功一筆會怎樣」。答案是「不會只成功一筆,同一交易」也算合格答案,
但要寫出來。

### 2.4 Software Design(軟體設計)

| 欄 | 語意 | 寫法紀律 |
|---|---|---|
| Component | 實作單位(檔/類別/函式群),比 Module 細一層 | 對得上 5-tasks 的 Files 欄 |
| Responsibility | 這個元件做什麼(一句,可執行) | 讀完就知道要寫什麼函式 |
| Collaborators | 它呼叫誰、被誰呼叫 | 只列本次相關的,不列全圖 |
| State / Data flow | 狀態住哪、資料怎麼流過它 | 無狀態就寫 `stateless` |
| Error handling | 錯誤在這裡被**吸收**還是**往上傳** | 二選一講明;吸收要說降級成什麼 |
| Test seam | 從哪裡可以把這個元件的行為釘住 | 指到可注入點/可觀測點,不寫「寫單元測試」 |

**Test seam 是本表最容易寫廢的欄**。合格的 Test seam 讓 Stage 5 的 `Verify:` 與
Stage 6 的 RED 測試知道從哪下手。寫「加測試」不合格;寫「service 層可注入 clock,
用固定 today 驗剩餘天數」合格。

### 2.5 Design Constraints

| 項 | 語意 |
|---|---|
| 必須 | 本次實作**必須**維持的硬約束(正向) |
| 禁止 | 本次實作**不得**做的事(負向);與 Verification Profile 的 Negative constraints 不同層次 —— 這裡是設計層,那裡是驗證層 |
| Extension point | 明確留給未來的擴充點;沒有就寫 `—`,不要為了填而虛構 |
| Known design limit | 本設計**明知**做不到或不保證的事 |

**Known design limit 是本章節最有價值的一欄**。它把「我們知道但這次不解」與
「我們沒想到」分開。誠實列出的 limit 不是扣分項;把已知缺口寫成「已處理」才是。
Known design limit 應同時出現在 7-review 的 known limits(既有機制),不另立追蹤鏈。

## 3. Architecture 與 Software Design 的分界

同一份契約裡兩者常被混寫。判準:

| 問題 | 屬於 | 落在哪張表 |
|---|---|---|
| 這個責任歸哪個模組? | Architecture | Architecture Boundaries |
| 誰可以寫這份資料? | Architecture | Architecture Boundaries(Data owner) |
| A 能不能依賴 B? | Architecture | Architecture Boundaries(Allowed/Forbidden) |
| 這個介面改了會不會弄壞呼叫端? | Architecture | Interface & Consistency Contract(Compatibility) |
| 這兩筆寫入是不是同一個交易? | Architecture | Interface & Consistency Contract |
| 這個模組**內部**怎麼拆成幾個元件? | Software Design | Software Design |
| 錯誤在哪一層被吃掉? | Software Design | Software Design(Error handling) |
| 狀態存在哪個物件上? | Software Design | Software Design(State / Data flow) |
| 要怎麼把行為釘住來測? | Software Design | Software Design(Test seam) |

一句話:**跨越模組邊界的是 Architecture,模組內部的是 Software Design。**
Interface & Consistency Contract 是兩者的交界,所以獨立一張表。

## 4. 已由別節承接的內容(不得重複,只引用結論)

| 內容 | 既有正本 | 本章節該怎麼寫 |
|---|---|---|
| Concurrency / Idempotency / Timeout-retry 三問 | 4-spec `Reliability triage` | **不重抄三問**;只在 Known design limit 或 Transaction boundary 引用它的結論 |
| 失敗模式清單與驗證層對應 | 4-spec `Failure Model`(Risk: high 必填) | **不重抄失敗清單**;只說明該 failure 在**哪個 Boundary 被隔離或傳遞** |
| 人的工作、權限、系統外動作、等待 | 4-spec 各 S 的 `Operational Context` | **不重抄**;只在 Architecture Boundaries 寫「權限在哪一層強制」 |
| 本次不得做的事(驗證層) | 4-spec `Negative constraints` | Design Constraints 的「禁止」寫**設計層**約束(依賴方向、寫入路徑),不重抄驗證層條目 |
| 依賴的其他 feature / 外部系統 / migration | 4-spec `Dependencies` | 不重抄;Architecture Boundaries 只寫本次行為經過的邊界 |
| 不在本次範圍的行為 | 4-spec `Out of Scope` | 不重抄;若某個 Out of Scope 造成設計上的已知缺口,寫進 Known design limit 並指回去 |
| 長命架構決策(為何這樣選) | `docs/adr/NNNN-*.md` | `Design source` 欄指過去,不在此複述決策理由 |

判斷口訣:**別處已經回答「是什麼」的,這裡只回答「落在哪個邊界」。**

## 5. `n-a` 的合法與非法

`n-a` 的唯一合法形式:`Applicability: n-a — <具體理由>`。理由必須說明
**為什麼 §1 十一條全部未命中**,不是說明這個 feature 有多小。

### 合法例

- `n-a — 單檔文案修正:只改 i18n 字典值,無模組邊界、無 API、無 schema、無新依賴、Risk: normal`
- `n-a — 只在既有 Service 內補一個純函式與其單元測試,不跨模組、不動資料寫入路徑、不改任何對外簽章`
- `n-a — 僅調整既有報表查詢的排序欄位,讀路徑、無寫入、無 schema 變更、呼叫端契約不變`

共同點:**逐條回應了觸發條件**,讀者可以自行複查。

### 非法例

| 寫法 | 為何非法 |
|---|---|
| `n-a` | 無理由,違反「不得只寫不適用」 |
| `n-a — 不適用` | 同義反覆,零資訊 |
| `n-a — 這次很小` | 大小不是觸發條件;小改也可能改公開 API |
| `n-a — fast lane` | Fast lane 不豁免觸發條件 |
| `n-a — 之後再補` | 未定事項只能進 Drafting Decisions,不得寫在此欄 |
| `n-a — 沒有架構變更`(但 Dependencies 寫著 migration) | 與同一份 4-spec 自相矛盾,第 4 條已命中 |

最後一列是 G2 reviewer 最該抓的型態:**`n-a` 與同一份 4-spec 其他節互相矛盾**。
機械腳本抓不到這種矛盾(它不懂語意),這是 Reviewer 的責任。

## 6. 好例與壞例(以 `example/contract-expiry-reminder` 為底)

### 好:Architecture Boundaries 一列

```
| Contract API (backend handler + service) | 提供到期查詢與狀態標記兩個端點,並在此層強制「已續約僅主管」 | 不擁有資料;寫入委派 Contract store | → Contract store | 不得由 Dashboard UI 直接觸 DB |
```

好在哪:責任是動詞句;明說自己**不是** owner;依賴方向單向;禁止項具體到層。

### 壞:同一列寫成

```
| Backend | 處理相關業務邏輯 | contracts | 依賴需要的模組 | 無 |
```

壞在哪:責任空句;Data owner 只寫資料表名不說誰負責不變量;
Allowed dependencies 是廢話;Forbidden 寫「無」而非 `—`,且事實上存在禁止項。

### 好:Known design limit 一條

```
- Known design limit:狀態寫入無版本欄與衝突偵測,兩人同時以過期畫面標記時後手覆蓋前手
  (歷程留兩筆但無衝突提示);本次不引入樂觀鎖,見 4-spec Out of Scope 與 Reliability triage。
```

好在哪:講清楚**會發生什麼**,不是講「有風險」;指回既有節,不重抄。

### 壞:同一條寫成

```
- Known design limit:併發情況可能有問題,後續評估。
```

壞在哪:模糊詞(「可能有問題」「後續評估」)違反 4-spec 反模糊三律;
未定事項應進 Drafting Decisions。

## 7. Stage 5／6／7 怎麼承接(只指路,規則正本在各模板)

| Stage | 承接方式 | 規則住哪 |
|---|---|---|
| 5 | 相關 T 的既有 `Boundaries:` 欄摘錄**該 T 的最小子集**(不複製整份契約) | `_templates/5-tasks.md` |
| 6 | T Review / Self-Review 加四條 drift 檢查;改到邊界即記 **L2** 回 G2 | `_templates/6-implementation-notes.md` |
| 7 | Standards Axis 查依賴方向/邊界洩漏/資料所有權/介面穩定;Spec Axis 逐條對照本契約 | `_templates/7-review.md` |

**不新增 Review Stage、不新增 Gate、不新增 Task 欄位。** Stage 6 的 Worker 只拿到
與其 T 相關的 Boundary 子集,不得因為本章節而被要求回讀 Stage 1～3。

## 8. 機械檢查的邊界(腳本驗什麼、不驗什麼)

`scripts/check-design-contract.sh` 是**結構**守衛,只驗以下**八類**(每類展開成數十條逐欄斷言;
以腳本實際輸出的計數為準,本節是分類摘要不是斷言清單):

1. `_templates/4-spec.md` 有 `## Design Boundary Contract` 章節。
2. 該章節有 `Applicability` 與 `Trigger(s)` 欄。
3. 三張表的必要欄位存在(表頭字串)。
4. Example 命中觸發條件時填為 `applicable`。
5. Example 三張表的必要欄位存在。
6. `n-a` 必須有非空理由。
7. README 只留摘要與正本連結:三張表的表頭字串不得出現在 README,且 README 必須連到本檔。
8. Stage 5／6／7 三個模板有承接規則。

腳本**不宣稱**能判斷:模組邊界劃得對不對、Data owner 合不合理、Interface 設計好不好、
Transaction boundary 是否符合領域。**這些永遠是 G2／G3 Reviewer 的判斷**,
與 README §7「強制力對照」表的分類一致:本項屬「本 repo 腳本驗欄位存在 + 人工判語意」。
