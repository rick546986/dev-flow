---
feature: five-station-simplify
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站簡化（Implementer A：Decision → 可測 R/S）

> Change spec（delta）。Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、OC-1…OC-11 ✅）。Stage 3 Human Demo **已在該站落檔**（`3-prototype.md` `status: approved`，`Human verdict: ACCEPTED | role=母版 owner | scenario=AC-1`，`Verdict attestation: human:rick @ 2026-09-14`）。本檔**不發明**第二份 Human Demo ACCEPTED，也不填 G2 `verdict: PASS`。
> 選定方案 = **1A+2A+3A+4A+5A+6A+7A**。本 hop **只本檔 + 審頁 html**。不改 `_templates/`／`graph.yaml`／gate token／`scripts/` 牙、不改 STATUS／HISTORY、不 bump `devflow-contract.json`、不落地 F1／F2／F3、不合併。
> R/S 是 **F1 annex + F1 牙**（以及 F2 cap 計數、F3 切線）要落地的契約。本 PR 零碼。牙長在 `scripts/` 與 annex；本檔只鎖語意槽與拒收謂詞，**不鎖 annex JSON 鍵名**（OC-3）。
> 反模糊：S 可轉單一測試；禁模糊詞；禁未定三詞（C4 全檔掃描那三個 token）。RP-3 在本檔改寫成「C4 未定事項三詞或不可測」，不回抄 Decision 原文那個 token。

## 補助模組生命週期（預覽）

主詞是「五站路線別名 + dual-read 誠實 + 採用端拒收 + Must-keep 牙」，不是整份方法論重寫。
- 新生（F1 才落地，本 PR 不加檔）：dual-read annex 九個 SLOT 語意槽；RP-1…RP-16 牙（只准 `scripts/` 與 annex）
- 改行為（相關一格）：doctor 綠不得冒充已切；marketplace 換 hops 不得遠端改線；in-flight 只認 1–7 `.md`；B1 空 attestation 仍拒；T 卡上就紅；skip-OC 否定句不得當已跳
- 退役：沒有（不刪 G1／G2／`ACCEPTED`）
- 不動：七檔名家族、gate token、F0 的 `graph.yaml`／既有牙、本 slug 舊 7、契約 `2.0.0`（本 hop 不 bump）

## Assumption refs

Q6 與 A1／A2 保持未抽現場。deadline 用 `F1-annex`（不是 `stage-2`），避免本檔自己被 C7 形狀誤殺；**語意**上本 slug G2 仍咬 Q6（OC-8／S-8.4）。

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q6 採用現場仍 chat 蓋章過 G1／G2 | F1-annex | open |
| A1／A2 共寫 `1-discussion.html` | F1-annex | open |
| 後站會用「已經五站了」省略 M11／M3／M1 | stage-2 | resolved |

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段。去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗}。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「例行 G1／S3-ACCEPTED／G2 讓方向、互動、契約三次都要等人」 | 本方案處理 | S-1.1、S-1.4 |
| 「Treat as PASS／都過／可以落成 verdict: PASS」 | 本方案處理 | S-5.2、S-5.3 |
| 「摺站若只殺等待、卻讓 Spec／Build 拿掉 ID 鏈、反模糊、T 四欄、acceptance seam」 | 本方案處理 | S-6.1、S-6.2、S-6.3、S-6.4、S-6.5 |
| Journey「owner chat 蓋章；方向卡沒被讀完也過」 | 本方案處理 | S-1.1、S-5.2 |
| Journey「Demo 欄空、chat 仍准開 Stage 4」 | 本方案處理 | S-5.1、S-5.2 |
| Journey「實作者若省四欄／seam，勾選假完成」 | 本方案處理 | S-6.2、S-6.3 |
| Journey「採用現場踩洞靠口頭中繼」 | 刻意維持 | Out of Scope：本包不建回報口 |
| Workaround「Agent 把口頭章落進 md 頂欄」 | 本方案處理 | S-5.2、S-5.3 |
| Workaround「採用洞進 dispatch-accounting-symmetry，不進 public issue」 | 刻意維持 | Out of Scope：public repo 禁收公司路徑 |
| Exception「Fast 仍吃 G2 物質」 | 刻意維持 | S-8.1（M7）；不廢 Fast |
| Exception「in-flight 整段舊 7」 | 本方案處理 | S-4.1、S-4.2 |
| Exception「F0–F2 母版新開改版軌仍舊 7」 | 本方案處理 | S-4.3 |
| Exception「[Assumption] 採用現場仍 chat 蓋章」 | 仍待驗 | S-8.4；Known limit：Q6 |
| Exception「後站會用『已經五站了』省略 M11／M3／M1」 | 本方案處理 | S-6.1、S-6.9 |
| Exception「A1／A2 共寫 1-discussion.html」 | 仍待驗 | Known limit：F1 annex 核對產檔器 dest |
| 「marketplace 可換 hops，doctor 仍可因 2.0.0 握手綠」 | 本方案處理 | S-2.5、S-3.1、S-3.2 |
| 「本 slug = live freeze 樣本」 | 本方案處理 | S-4.1、S-8.3 |
| Q8 dual-read 2.1.0 欄位與舊檔不紅缺省 | 本方案處理 | S-2.1、S-2.2、S-2.4 |
| Q10 coordinator event 與 rewrite cap 計數落點 | 本方案處理 | S-7.3、S-7.4、S-7.5 |
| Q11 空 attestation 五站後是否仍機械拒 | 本方案處理 | S-5.1 |
| rewrite cap hop≤2／Decide≤1／Goal reopen≤1 | 本方案處理 | S-7.3、S-7.4、S-7.5、S-4.4 |
| 「本 hop 不改模板、不送 G1」 | 刻意維持 | Out of Scope：本 PR 只 4-spec＋html；G1 已在 Stage 2 |

## Must-keep Disposition

語法 = Decision 約束 4／Q9：`M… → R-x/S-y` 或 `Non-Goal:<reason>`。M15／M16 是**約束**，禁止寫成 Non-Goal。

| M | 去向 | 下落 |
|---|---|---|
| M1 ID 鏈；測試名含 S-id | M1 → S-6.5 | RP-4 |
| M2 圍欄 | M2 → S-8.1 | 刻意維持：實作者禁讀 1／2／3 補洞 |
| M3 反模糊 | M3 → S-6.4 | RP-3（C4 未定事項三詞或不可測） |
| M4 Real-world→Demo→OC | M4 → S-8.1、S-5.4 | SC-6 |
| M5 人寫 ACCEPTED／Ship PASS | M5 → S-5.3、S-7.6 | RP-16／RP-8 |
| M6 G3 Evidence 八點 | M6 → S-8.1 | 不因摺站省略 |
| M7 Profile + fast+high 拒 | M7 → S-8.1 | Fast 仍吃 |
| M8 DBC 條件式 | M8 → S-8.1 | 不是新站 |
| M9 Files ⊆ 5-tasks | M9 → S-6.6 | RP-5 |
| M10 驗證五律 | M10 → S-6.7 | RP-6 |
| M11 T seam + 四欄 | M11 → S-6.2、S-6.3 | Owner-locked；RP-1／RP-2 |
| M12 author≠approver | M12 → S-8.1 | Ship 與任何 latch |
| M13 html 重生 | M13 → S-8.1 | twin／審頁仍產 |
| M14 不可逆才 Quiz | M14 → S-6.8 | RP-7；Quiz ≠ 預設第三停 |
| M15 token／檔仍在 | M15 → S-1.3 | 約束；拒 1B |
| M16 F0 不改 graph／牙 | M16 → S-8.2、S-8.3 | 約束；本 PR 不動 |

無高影響 M 落到 Non-Goal。

## OC ledger

| OC | 掛在 | 本檔怎麼咬 |
|---|---|---|
| OC-1 dual-read 誠實三句 | S-2.1、S-2.2、S-2.3、S-2.5 | 能解析兩套 ≠ 已切；doctor 綠 ≠ 路線 |
| OC-2 2.0.0+五站 hops → 紅 | S-3.1、S-2.4 SLOT-REJECT | F1 最少採用端拒收 |
| OC-3 不鎖 annex 鍵名 | S-2.4、DD-1 | 只鎖 SLOT 語意；F1 命名 |
| OC-4 本 Decision hop 不改 STATUS／不發明 G1 | S-8.3 | 本 Stage 4 延續：不改 STATUS、不填 G2 PASS |
| OC-5 in-flight 只認 md | S-4.1、S-4.2 | 裸 html 不凍 |
| OC-6 chat 不是判定 | S-5.2 | 准開／可以／Treat as PASS 無效 |
| OC-7 本 hop 連 scripts／annex 也不寫 | S-8.2、S-8.3 | 本 PR 零牙 |
| OC-8 Q6 不升格；本 slug G2 仍咬 | S-8.4 | refs 列 open → 本檔 verdict 不得 PASS |
| OC-9 SC 用對照稿／拒絕／檔集 | 各 S 觀測欄 | 本檔不寫測試檔 |
| OC-10 RP 最小集只准加 | S-7.1、S-7.2 | 刪列 = 翻 Decision |
| OC-11 後站標可選擋本 slug G2 | S-6.9 | 本檔若寫「可選四欄／可選 seam／已五站故省 Must-keep」即違 |

## RP → S（牙後落地；本 PR 不實作）

| RP | 謂詞（本檔用詞，避開 C4 全檔三詞） | S |
|---|---|---|
| RP-1 | T 缺 Covers／Files／Verify／Blocked-by → 紅 | S-6.2 |
| RP-2 | 無 RED 輸出或 reviewer=implementer → T 未完成 | S-6.3 |
| RP-3 | S 含 C4 未定事項三詞或不可測 → 紅 | S-6.4 |
| RP-4 | 測試名不含 S-id → 紅 | S-6.5 |
| RP-5 | 缺 Files 或 Files ⊈ 5-tasks 聯集 → 紅 | S-6.6 |
| RP-6 | 無原始輸出 → 紅 | S-6.7 |
| RP-7 | 不可逆且無 Quiz → 紅；非不可逆被強制 Quiz 當例行停 → 違 SC-1 | S-6.8 |
| RP-8 | Ship 無人寫 `verdict: PASS` 卻標 Done → 紅 | S-7.6 |
| RP-9 | hop 重寫第 3 次仍繼續 → 紅 | S-7.3 |
| RP-10 | Decide 重開第 2 次仍繼續 → 紅 | S-7.4 |
| RP-11 | Goal 離開 Intake 後重開第 2 次仍繼續 → 紅 | S-7.5 |
| RP-12 | B1 未命中卻要求 `ACCEPTED` → 紅 | S-5.4 |
| RP-13 | B1 命中、無 attestation，卻 hop 出 Spec → 紅 | S-5.1 |
| RP-14 | latch 未命中卻留下「請人審」紀錄 → 紅 | S-5.5 |
| RP-15 | 舊 7 in-flight slug 被寫入五站狀態 → 紅 | S-4.1 |
| RP-16 | Agent 代寫 `ACCEPTED` 或 Ship `PASS` → 視為未寫並紅 | S-5.3 |

## ADDED Requirements

### R-1: 系統 SHALL 用五個別名摺例行人類停點，並留下 token、twin 與七檔名

1A／SC-1／AC-1／AC-6／M15。預設路線別名 = Intake→Decide→Spec→Build→Ship。摺的是例行 G1／S3-`ACCEPTED`／G2 人類停，不是完整度。A4／A7 twin 仍產、latch=否。A10 是唯一預設人類 latch。謂詞假 = 停該站修，不准改問人。

**審的時候看什麼**
新 slug、中間 latch 未命中時，前進紀錄有沒有「請人審 A4／A7」。token 刪了沒有。表 A／B 產不產與等不等能否只靠「有沒有檔／有沒有命中」答完。

#### S-1.1
- GIVEN F3 cut 之後的新 slug：`2-decision.md` 的 Decision 非空、Owner Calls 全裁決、B1 未命中、`4-spec.md` 通過 `check-spec-gate.sh`、每 T 有 Covers／Files／Verify／Blocked-by 且有 RED 與不同於實作者的 reviewer
- WHEN F2 落地後的 coordinator 評 Decide→Spec→Build 自動前進謂詞
- THEN 該 slug 前進紀錄不含字面「請人審 A4」「請人審 A7」「請按提交判定」；A4／A7 twin 檔可以存在
- 觀測:n-a:本 PR 無 coordinator。替代=Stage 3 盤 1「新 5」欄與本條 THEN；F2 用 hop／event 紀錄對同一對照稿測
- Operational Context:
  - Actor:coordinator（F2 後）／母版 owner
  - Goal:中間站不等提交判定
  - Situation:Decide／Spec／Build 謂詞全真、中間 latch 未命中
  - Known information:表 A latch 欄；A4／A7 latch=否
  - Missing information:F2 event schema（落點 F2，數字已鎖）
  - Human decision:無（例行不停）
  - Authority:coordinator 只評謂詞，不准問「要不要繼續」
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不等；謂詞假才停修
  - Recovery:謂詞假 → 停該站修該欄，不改問人
  - Audit/handoff requirement:前進紀錄可核對
  - Observation:見本條觀測

#### S-1.2
- GIVEN 同 S-1.1 的新 slug，但 Owner Calls 有一列不是已裁決，或某 S 缺觀測欄
- WHEN coordinator 評該站謂詞
- THEN 停在該站；拒絕理由含該謂詞名（「OC 未全裁決」或「S 缺觀測」）；輸出不含「要不要繼續」
- 觀測:n-a:本 PR 無 coordinator。替代=本條 THEN + Stage 3 盤 1「謂詞假停修」；F2 對該假謂詞對照稿測
- Operational Context:
  - Actor:coordinator／該站寫手
  - Goal:假謂詞被修掉，不是被口頭繞過
  - Situation:物質沒齊
  - Known information:哪一列未裁決／哪一條 S 缺觀測
  - Missing information:無
  - Human decision:寫手修檔；coordinator 不改問 owner 准不准繼續
  - Authority:謂詞，不是 chat
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停修直到謂詞真
  - Recovery:補齊該欄後重評
  - Audit/handoff requirement:拒絕理由可重讀
  - Observation:見本條觀測

#### S-1.3
- GIVEN F3 cut 之後的工作樹（本 PR 不改這些檔）
- WHEN 跑 `scripts/check-gate-tokens.sh` 並列出 `docs/dev/<任意 slug>/` 的站檔名
- THEN G1／G2／`ACCEPTED` token 錨仍在（該檢查 exit 0）；站檔名仍是 `1-discussion.md`…`7-review.md`，不是另一套家族
- 觀測:從 gate-tokens exit 與檔名看 | token 檢查 exit 0 且七檔名未改家族算過 | 本 tree 現況當正向；刪 token 的隔離複本當負向（F1／F3 後仍要綠）
- Operational Context:不適用 — 檔名與 token 地板，無人員交接。

#### S-1.4
- GIVEN brief 表 A／B 與兩份對照：①新 slug 有 `2-decision.md`、`4-spec.md`、`7-review.md` 機械綠、九條 trigger 未勾；②純守衛 feat、九條未勾
- WHEN 人只看「有沒有檔／有沒有命中」答產不產與等不等
- THEN A4／A7 產且 latch=否；A5 不建頁且 Demo 條件 = N/A + 非空白原因；A10 latch=是且機械綠仍進 HumanWait；B1 未命中不產 Demo；B4 只在不可逆開火，且可與 A10 同一人停，不得拆成第三次例行停
- 觀測:從 Stage 3 盤 2 卡面與本條 THEN 看 | 產／latch 真假與上列一致算過 | 盤 2 表 + 對照①②
- Operational Context:
  - Actor:母版 owner
  - Goal:知道哪一頁要等人
  - Situation:評表 A／B
  - Known information:有沒有檔、trigger 勾了幾條
  - Missing information:無
  - Human decision:只在 latch=是時寫判定
  - Authority:brief §3 表，不是 twin 存在本身
  - External dependency:無
  - Out-of-system action:latch=是時才把頁 URL 丟給人
  - Waiting/timeout behavior:A10 永遠等；A4／A7 不等
  - Recovery:誤把 A4 當 G1 仍要簽 → 對照本條 THEN
  - Audit/handoff requirement:頁 URL 只在 latch=是時交出
  - Observation:見本條觀測

### R-2: 系統 SHALL 用 dual-read 誠實三句定義 2.1.0 annex 語意槽

2A／OC-1／OC-3／SC-5／SC-9／Q8。誠實 = (1) 2.1.0 可解析舊 7 與新 5；(2) 舊 7 缺新欄不紅；(3) 未宣告 2.1.0 即使 marketplace 已換 hops 仍走舊 7。能解析兩套 ≠ 已把對方切到五站。本檔不鎖 annex 鍵名；鎖 SLOT- id 語意。F1 實作這些槽。

**審的時候看什麼**
舊檔缺新欄是合法缺席還是一次變紅。doctor COMPATIBLE 有沒有被寫成「已切五站」。annex 九個 SLOT 少了哪一個。

#### S-2.1
- GIVEN 契約已宣告 minor 2.1.0 且 F1 annex 已落地
- WHEN 2.1.0 讀檔器讀一份舊 7 slug（有 1–7 md、無新 5 欄）與一份新 5 slug（有五站別名欄）
- THEN 兩份都解析成功（exit 0 或 annex 寫明的成功碼），不是只認其中一套
- 觀測:n-a:2.1.0 尚未 bump。替代=annex 必須含 SLOT-PARSE-OLD7 與 SLOT-PARSE-NEW5；F1 用兩份對照稿測
- Operational Context:不適用 — 讀檔器契約，無人員交接。

#### S-2.2
- GIVEN 2.1.0 讀檔器 + 一份舊 7 檔，新 5 欄全部缺席
- WHEN 跑 dual-read 檢查
- THEN 不得因「缺新 5 欄」而 exit ≠ 0；缺省 = 合法缺席（SLOT-MISSING-NEW5-DEFAULT）
- 觀測:n-a:同 S-2.1。替代=SLOT-MISSING-NEW5-DEFAULT 必須寫成合法缺席、不紅；F1 用舊 7 對照稿測
- Operational Context:
  - Actor:採用專案 owner／母版維護者
  - Goal:舊 slug 不被一次變紅
  - Situation:F3 cut 後 dual-read 讀 in-flight 舊檔
  - Known information:SC-5 第 2 句；AC-5
  - Missing information:annex 鍵名（F1 命名）
  - Human decision:不把「不紅」讀成「可以默默切五站」
  - Authority:annex 缺省規則
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:若舊檔被紅，屬違 2A／2B 已拒
  - Audit/handoff requirement:檢查輸出可重跑
  - Observation:見本條觀測

#### S-2.3
- GIVEN 採用端 `devflow_contract_version=2.0.0`（未宣告 2.1.0）
- WHEN marketplace 已把方法包 hops 換成五站預設
- THEN 採用端路線仍是舊 7（SLOT-UNDECLARED-ROUTE=old-7）
- 觀測:從契約版本與路線判定看 | 未宣告 2.1.0 不得走五站預設算過 | 對照稿：2.0.0 + 五站 hops（與 S-3.1 同一稿的路線半句）
- Operational Context:
  - Actor:採用專案 owner
  - Goal:未被遠端改線
  - Situation:marketplace update 已跑、契約仍 2.0.0
  - Known information:OC-1 第 3 句
  - Missing information:採用端何時自己 upgrade
  - Human decision:要不要 upgrade 到 2.1.0
  - Authority:契約版本，不是 marketplace 包裝
  - External dependency:`marketplace update`
  - Out-of-system action:人決定是否 upgrade
  - Waiting/timeout behavior:未 upgrade 維持舊 7
  - Recovery:拒絕跟 hops 走；回退方法包或補 2.1.0
  - Audit/handoff requirement:契約版本可讀
  - Observation:見本條觀測

#### S-2.4
- GIVEN F1 annex 文本（本 slug F1 產出；JSON／YAML 鍵名本檔不鎖）
- WHEN 人用本條 SLOT- id 清單核對 annex
- THEN annex 必須同時具備這九個語意槽（F1 可另命名鍵，但每個 SLOT- id 要能指到一欄或等效句）：SLOT-PARSE-OLD7；SLOT-PARSE-NEW5；SLOT-MISSING-NEW5-DEFAULT=合法缺席不紅；SLOT-UNDECLARED-ROUTE=old-7；SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS=契約仍 2.0.0 且 hops 已是五站預設 → 紅／不得改線；SLOT-DOCTOR-GREEN-MEANS=握手，≠路線沒變，≠已切；SLOT-IN-FLIGHT-DETECT=`docs/dev/<slug>/` 已有 1–7 任一 `.md`；SLOT-RP-MIN-SET=RP-1…RP-16 只准加不准減；SLOT-SKIP-NEGATION=「不／無／不得」加「跳過」不得當 skip OC。少一槽 = F1 未完成
- 觀測:從 F1 annex 正文對九個 SLOT- id 看 | 每個 id 有對應欄或等效句算過 | 本條清單當核對表
- Operational Context:不適用 — annex 契約清單，無現場交接。

#### S-2.5
- GIVEN 本 tree 現況：`docs/dev/devflow-contract.json` 的 `devflow_contract_version=2.0.0`；`hooks/devflow-doctor.sh` 印 `COMPATIBLE` 且 exit 0；`hooks/_doctor_impl.py` 握手段只比對契約版本 ∈ supported
- WHEN 有人把這次 exit 0 寫成「已切五站」或「路線沒變」
- THEN 該寫法違 OC-1／SC-9；F1 牙或同等拒絕必須紅
- 觀測:從 doctor stdout 與 `_doctor_impl.py` 握手段看 | 握手句不含 hops／graph.yaml／marketplace／Intake；exit 0 單獨不得當路線證據算過 | 2026-09-14 盤 5 已實跑：COMPATIBLE、exit 0、源碼約 L193–L202
- Operational Context:
  - Actor:採用專案 owner
  - Goal:拒絕握手冒充切線
  - Situation:剛跑完 doctor、剛做完 marketplace update
  - Known information:盤 5 證據表
  - Missing information:F1 牙腳本名
  - Human decision:不跟 hops 走，直到 2.1.0
  - Authority:OC-1 第 3 句
  - External dependency:doctor、marketplace
  - Out-of-system action:核契約版本
  - Waiting/timeout behavior:無
  - Recovery:把「已切」文案刪掉；等 F1 牙紅 2.0.0+五站 hops
  - Audit/handoff requirement:doctor 原始輸出留下
  - Observation:見本條觀測

### R-3: 系統 SHALL 拒絕把 doctor 綠當成可以跟 hops 走

3A／OC-2／SC-9／SC-10。F1 最少採用端拒收 = 契約仍 2.0.0 且 hops 已是五站預設 → 紅／不得改線。未 upgrade 不得遠端改線。

**審的時候看什麼**
固定對照：`2.0.0` + marketplace 已換五站 hops + doctor exit 0。採用端還能不能被說成「已切」或「跟 hops 走」。

#### S-3.1
- GIVEN 對照稿：`devflow_contract_version=2.0.0` 且 hops 預設已是 Intake→Decide→Spec→Build→Ship
- WHEN 跑 F1 採用端拒收牙（腳本名由 F1 定，本檔不鎖）
- THEN exit ≠ 0；輸出含 `2.0.0` 與五站 hops（或 annex 指定的同等字樣）；不得把採用端改成五站預設
- 觀測:n-a:本 PR 不寫牙。替代=SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS 必須在 annex；F1 用該對照稿測
- Operational Context:
  - Actor:採用專案 owner
  - Goal:拒絕被遠端改線
  - Situation:契約仍 2.0.0、hops 已被換成五站
  - Known information:SC-10 固定對照
  - Missing information:牙掛哪支腳本
  - Human decision:upgrade 或拒絕更新 hops
  - Authority:F1 牙
  - External dependency:marketplace
  - Out-of-system action:停用已換包或回退
  - Waiting/timeout behavior:未 2.1.0 維持舊 7
  - Recovery:回退方法包或 bump 到 2.1.0 dual-read
  - Audit/handoff requirement:牙的 stderr 留下
  - Observation:見本條觀測

#### S-3.2
- GIVEN 一段文案或謂詞把「doctor 綠」寫成「可以跟 hops 走」
- WHEN 跑 S-3.1 同一支牙或 annex 指定的文案檢查
- THEN 紅（SC-10）
- 觀測:n-a:本 PR 不寫牙。替代=本條對照句必須出現在 F1 拒收清單；F1 用該文案稿測
- Operational Context:不適用 — 文案／謂詞檢查，與 S-3.1 同一牙。

#### S-3.3
- GIVEN 採用端未 upgrade 到 2.1.0 dual-read
- WHEN `marketplace update` 換了方法包
- THEN 採用端仍必須走舊 7；把更新本身當成切線 = 違 OC-1 第 3 句
- 觀測:從採用端契約版本與實際 hop 圖看 | 未 2.1.0 仍走舊 7 的 G1／G2 例行停節點算過 | 本 tree `.claude-plugin/marketplace.json` 的 `source: ./` + 現行 `N7-g1`／`N6-g2` 當基線
- Operational Context:不適用 — 與 S-2.3 同一路線半句；本條咬「更新動作 ≠ 切線」。

### R-4: 系統 SHALL 把已有 1–7 任一 md 的 slug 整段凍結在舊 7

4A／OC-5／SC-5／SC-8／AC-8／RP-15。偵測 = `docs/dev/<slug>/` 已有 1–7 任一 `.md`。僅 html 不算開工。本目錄已有 `1-discussion.md` = 第一個 live freeze 樣本。舊 7 不套 rewrite 三 cap。F0–F2 母版新開改版軌也舊 7。

**審的時候看什麼**
對本目錄要求五站自動前進，跳不跳得過。裸 html 會不會被誤凍。

#### S-4.1
- GIVEN `docs/dev/five-station-simplify/` 已有 `1-discussion.md`（亦已有 `2-decision.md`、`3-prototype.md`）
- WHEN coordinator 或任何人要求五站自動前進、跳過本 slug 例行 G1／G2
- THEN 該 hop 被拒（RP-15）；目錄整段舊 7 直到自己的 Ship；不得寫入五站狀態
- 觀測:從本目錄 1–7 `.md` 是否存在 + 被拒 hop 輸出看 | 已有 md 則不得寫入五站狀態算過 | 本資料夾現況
- Operational Context:
  - Actor:in-flight slug 執行者／coordinator
  - Goal:走完手上舊 7，不被中途改線
  - Situation:有人想拿本 slug 當新 5 白老鼠
  - Known information:目錄已有 md；4C 已拒
  - Missing information:無
  - Human decision:本 slug 自己的 G2／G3 仍按舊 7 等人
  - Authority:OC-5／SC-8
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:本 slug 仍例行等 G2／G3
  - Recovery:從目錄裡的 md 接著走舊路
  - Audit/handoff requirement:拒絕寫入五站狀態
  - Observation:見本條觀測

#### S-4.2
- GIVEN 某 slug 目錄只有 `1-discussion.html`、沒有 1–7 任一 `.md`
- WHEN 評 in-flight
- THEN in-flight=False；不得只因裸 html 凍結
- 觀測:從偵測規則看 | 只認 `.md` 算過 | 對照：空目錄+裸 html vs 本目錄有 md
- Operational Context:不適用 — 偵測規則，無人員交接。

#### S-4.3
- GIVEN F0–F2 期間母版新開的改版軌 slug（F3 尚未 cut）
- WHEN 選路線
- THEN 走舊 7，不建立五站機
- 觀測:從該 slug 是否建立五站狀態看 | F3 前新開軌無五站狀態算過 | brief §6 對照
- Operational Context:不適用 — 切刀規則，無現場交接。

#### S-4.4
- GIVEN 舊 7 in-flight slug 發生重寫（含本 slug）
- WHEN 計 hop／Decide／Goal reopen
- THEN 不套 hop≤2／Decide≤1／Goal reopen≤1；走既有 T 嘗試上限 4 與既有修迴圈
- 觀測:從三個 cap 計數器是否對該 slug 遞增看 | 舊 7 不建立或不遞增這三 cap 算過 | 本 slug 自己的修迴圈
- Operational Context:不適用 — cap 適用範圍，計數落點 F2。

### R-5: 系統 SHALL 在 B1 命中且 attestation 空時拒絕離 Spec，並把 Agent 代寫當成未寫

5A／OC-6／SC-4／SC-6／AC-4／RP-8／RP-12／RP-13／RP-14／RP-16。chat「可以／准開」不是判定。latch 未命中不准問人。否定「跳過」不得被讀成 skip OC。

**審的時候看什麼**
欄空 + chat 准開，能不能離 Spec。Agent 寫的 `ACCEPTED`／`PASS` 算不算已寫。否定跳過句有沒有被當成已跳。

#### S-5.1
- GIVEN B1 命中（九條 trigger 任一）且 `3-prototype.md` 沒有人類 attestation 行（`Verdict attestation: human:<名> @ <YYYY-MM-DD>` 缺或空）
- WHEN 要求 hop 出 Spec（開 Stage 4 或五站 Spec→Build）
- THEN 機械拒（RP-13）；不得離 Spec
- 觀測:從 hop 拒絕看 | 無 attestation 不得過算過 | 對照 dogfood-ping `DOGFOOD-NOTES.md` L9 形；本 slug Stage 3 已有 attestation 的現況是正向（已 ACCEPTED），不是本條負向稿
- Operational Context:
  - Actor:母版 owner
  - Goal:B1 命中時人親做 Demo
  - Situation:trigger 已勾、欄空
  - Known information:九條 trigger；attestation 行格式
  - Missing information:人類 attestation
  - Human decision:親寫 ACCEPTED + attestation，或 REVISE
  - Authority:md 行，不是 chat
  - External dependency:無
  - Out-of-system action:人走 Demo
  - Waiting/timeout behavior:停在 Spec 條件附件
  - Recovery:人類親填後重評
  - Audit/handoff requirement:attestation 行可重讀
  - Observation:見本條觀測

#### S-5.2
- GIVEN B1 命中、attestation 空、owner chat 含「可以」「准開下一站」或「Treat as PASS」
- WHEN 有人把該 chat 寫入 Human verdict 或當 attestation 替代
- THEN 該寫入無效（OC-6）；判定正本仍是同目錄 md 的 Human verdict 行與 attestation 行；hop 仍拒
- 觀測:從 md 行與 hop 結果看 | chat 單獨存在時 hop 仍拒算過 | Stage 3 盤 4 壞卡 dogfood
- Operational Context:
  - Actor:母版 owner／助手
  - Goal:口頭章不能帶走空欄
  - Situation:dogfood 捷徑
  - Known information:gate-verdict-write：頂欄才是判定
  - Missing information:無
  - Human decision:親填或停
  - Authority:md，不是 Cursor chat
  - External dependency:Cursor chat
  - Out-of-system action:chat 說話
  - Waiting/timeout behavior:仍卡 Spec
  - Recovery:刪代寫、人類親填
  - Audit/handoff requirement:chat 不得出現在 attestation 行
  - Observation:見本條觀測

#### S-5.3
- GIVEN Agent 或 coordinator 寫入 `ACCEPTED` 或 Ship `verdict: PASS`，且無人類 attestation、無人類頂欄
- WHEN 系統評該欄
- THEN 視為未寫並紅（RP-16）；不得離 Spec、不得 Done
- 觀測:從該 md 與 hop／Done 標看 | 代寫欄被當空算過 | Stage 3 盤 4 壞卡 Agent
- Operational Context:
  - Actor:Ship 審查者／母版 owner
  - Goal:出貨判定是人的
  - Situation:機械全綠、Agent 想代填
  - Known information:brief §8
  - Missing information:人類頂欄
  - Human decision:人寫 PASS／REQUEST_CHANGES／HOLD
  - Authority:人
  - External dependency:無
  - Out-of-system action:人打開審頁寫頂欄
  - Waiting/timeout behavior:A10 HumanWait
  - Recovery:刪代寫後等人
  - Audit/handoff requirement:reviewers 欄與頂欄
  - Observation:見本條觀測

#### S-5.4
- GIVEN 九條 trigger 全未勾，且 2-decision 沒有同一行同時含「Stage 3」與「跳過」的 skip OC
- WHEN 系統評 B1
- THEN 不產 Demo 頁；不得要求 `ACCEPTED`（RP-12）；G2 Demo 條件 = N/A + 非空白原因
- 觀測:從 A5 是否建頁 + 是否出現 ACCEPTED 要求看 | 未命中無頁、無第二次人停算過 | 純守衛 feat 對照
- Operational Context:不適用 — 與 S-1.4 A5／B1 未命中同一觀測面；本條專咬 RP-12。

#### S-5.5
- GIVEN latch 列為假（A4／A7，或 B1 未命中）
- WHEN coordinator 留下「請人審」「請 owner 看一下」或「要不要繼續」
- THEN 紅（RP-14）
- 觀測:n-a:本 PR 無 coordinator。替代=Stage 3 盤 2 壞例 + 本條 THEN；F2 對該「請人審」紀錄測
- Operational Context:
  - Actor:coordinator
  - Goal:latch 假時不准問人
  - Situation:想客氣問一下
  - Known information:brief §3 出口第 5 步
  - Missing information:無
  - Human decision:無（不准問）
  - Authority:latch 列
  - External dependency:無
  - Out-of-system action:禁開審查 widget
  - Waiting/timeout behavior:不等
  - Recovery:刪「請人審」紀錄、停修謂詞
  - Audit/handoff requirement:不得留下請人審
  - Observation:見本條觀測

#### S-5.6
- GIVEN `2-decision.md` 內部技術選擇含「不預先跳過 Stage 3」且同行說明本檔無「跳過 Stage 3」流程層 OC
- WHEN 跑 skip-OC 匹配：現行 `python3 hooks/_stage3_impl.py five-station-simplify`，以及 F1 收緊後的同一入口
- THEN F1 之後：字面同時有「不／無／不得」與「跳過」不得當 skip OC（SLOT-SKIP-NEGATION）；現行 2026-09-14 stdout `g2_demo=PASS`、`trigger_source=owner-call` 是誤綠，本 PR 不改 `_stage3_impl.py`，也不得把該誤綠當成 Human Demo ACCEPTED
- 觀測:從該指令 stdout 與句子中文看 | 現行誤 PASS 已記錄；F1 必須對該否定句 REJECT 算過 | Stage 3 盤 4 原始輸出 + Demo Script Scenario RP-14
- Operational Context:
  - Actor:G2 reviewer／F1 寫牙的人
  - Goal:否定句不被當成已跳
  - Situation:現行牙把「不跳過」讀成 skip
  - Known information:2026-09-14 原始輸出
  - Missing information:F1 收緊後的實作
  - Human decision:F1 改謂詞，本 PR 不改牙
  - Authority:句子語意，不是子字串命中
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:F1 加否定詞閘
  - Audit/handoff requirement:留下這次誤 PASS 輸出
  - Observation:見本條觀測

### R-6: 系統 SHALL 把 Must-keep 少一條視為違 brief，並在 T 卡上拒絕假完成

6A／SC-2／SC-3／AC-3／OC-11／M1／M3／M9／M10／M11／M14／RP-1…RP-7。T 四欄與 RED→獨立審查 seam 不可選。人見面時機 = T 卡上就紅（Stage 3 選定；hop 板／Ship 重建已棄）。

**審的時候看什麼**
T-fake 勾了沒有。紅是寫卡當下還是出貨才出現。「已五站故可省」有沒有被寫進本檔。

#### S-6.1
- GIVEN 一份規格／任務／牙輸出宣稱「五站已簡化」，且 M1–M16 少任一項
- WHEN 對照 `notes/design/five-station-simplify-brief-v3.md` §5
- THEN 該宣稱被點名違 brief，不得寫成簡化成功（SC-2）
- 觀測:從對照輸出或審查紀錄看 | 少項被點名算過 | 故意拿掉 Verify 欄的對照稿
- Operational Context:不適用 — 對照 brief 的審查句，無新交接。

#### S-6.2
- GIVEN T-fake：Covers／Files／Verify／Blocked-by 任一為空，或 Verify 字面為「看起來沒問題」，且 checkbox 已勾
- WHEN 人在寫該 T 或看 A8 的當下評該 T（不是離開 Build 之後，也不是 Ship 才重建）
- THEN 該 T 紅（RP-1）；勾選不得標完成
- 觀測:從該 T 卡當下的未完成狀態看 | 缺欄或「看起來沒問題」與勾選同時存在仍未完成算過 | Stage 3 盤 3 T-fake
- Operational Context:
  - Actor:獨立 T reviewer／Build 實作者
  - Goal:假完成 T 當下就被看見
  - Situation:寫手想用「已五站」省四欄
  - Known information:四欄必填；Stage 3 選定 T 卡上就紅
  - Missing information:無
  - Human decision:退回補欄
  - Authority:T 卡上的 RP，不是 hop 板
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:補齊四欄後重評
  - Audit/handoff requirement:勾選軌跡不得冒充完成
  - Observation:見本條觀測

#### S-6.3
- GIVEN 一個 T 沒有 RED 輸出，或 reviewer 字面等於 implementer
- WHEN 評該 T 是否完成
- THEN 未完成（RP-2）；自審不得標完成
- 觀測:從 6-notes 該 T 的 RED 輸出與 reviewer 欄看 | 缺 RED 或自審 → 未完成算過 | 盤 3 T-fake
- Operational Context:
  - Actor:獨立 T reviewer
  - Goal:縫存在
  - Situation:實作者想自審
  - Known information:author ≠ 該 T reviewer
  - Missing information:另一 session
  - Human decision:換 reviewer 或補 RED
  - Authority:seam
  - External dependency:另一 session
  - Out-of-system action:開第二個審查 session
  - Waiting/timeout behavior:等獨立 review
  - Recovery:換人重審
  - Audit/handoff requirement:reviewer 欄可核對
  - Observation:見本條觀測

#### S-6.4
- GIVEN 一條 S 的 GWT 含 C4 未定事項三詞之任一，或寫不出具體輸入與可斷言輸出
- WHEN 跑 `bash scripts/check-spec-gate.sh <該 4-spec>` 或 F1 同等牙
- THEN exit ≠ 0（RP-3）
- 觀測:從 spec-gate C4 或 F1 牙的 exit 看 | 含未定標記或不可測必紅算過 | 對照稿：S 正文含 C4 三詞之一（本檔自己不得含那三詞）
- Operational Context:不適用 — 形狀檢查。

#### S-6.5
- GIVEN 測試函式名不含 `S-` id（例：`test_happy_path`，名中無 `S-6.5` 這類 token）
- WHEN 跑 F1 牙（RP-4）
- THEN 紅
- 觀測:n-a:本 PR 無該牙。替代=本條 + SLOT-RP-MIN-SET 含 RP-4；F1 用該測試名測
- Operational Context:不適用 — 測試命名牙。

#### S-6.6
- GIVEN 一個 T 缺 Files 欄，或 Files 列出的路徑 ⊈ 同份 5-tasks 全部 T 的 Files 聯集
- WHEN 跑 F1 牙（RP-5）
- THEN 紅
- 觀測:n-a:本 PR 無該牙。替代=本條 + SLOT-RP-MIN-SET 含 RP-5；F1 用範圍外檔對照稿測
- Operational Context:不適用 — scope guard 牙。

#### S-6.7
- GIVEN 一個 T 的完成宣稱只附摘要句、沒有原始指令輸出、也沒有 `檔:行`
- WHEN 跑 F1 牙（RP-6）
- THEN 紅
- 觀測:n-a:本 PR 無該牙。替代=本條 + SLOT-RP-MIN-SET 含 RP-6；F1 用「只有摘要」對照稿測
- Operational Context:不適用 — 驗證五律牙。

#### S-6.8
- GIVEN 兩份對照：①改動命中不可逆（schema／公開 API／權限／金流／資料遺失）且無 Quiz；②改動非不可逆，卻被強制 Quiz 當作例行第三停
- WHEN 評 B4
- THEN ①紅（RP-7）；②違 SC-1／G-out-1（Quiz ≠ 預設第三停）
- 觀測:從 Quiz 是否開火看 | ①無 Quiz 必紅；②可逆強制 Quiz 當例行停必紅算過 | brief 表 B4
- Operational Context:
  - Actor:Ship 審查者
  - Goal:不可逆才考 approver；可逆不加人停
  - Situation:有人想每次都 Quiz
  - Known information:M14
  - Missing information:無
  - Human decision:不可逆才做 Quiz；可與 Ship 同一停
  - Authority:B4 命中謂詞
  - External dependency:無
  - Out-of-system action:不可逆時人答 Quiz
  - Waiting/timeout behavior:可併 A10
  - Recovery:可逆的 Quiz 拆掉
  - Audit/handoff requirement:Quiz 紀錄只在不可逆
  - Observation:見本條觀測

#### S-6.9
- GIVEN 本 slug 的 `4-spec.md` 或後續 `5-tasks.md` 把 Must-keep（尤其 M1／M3／M11）或 T 四欄／seam 標成「可選」，或寫「已經五站了所以可省」
- WHEN 評本 slug G2
- THEN 擋本 slug G2（OC-11）；該句不是合法簡化
- 觀測:從本檔與後續 5-tasks 搜「可選四欄」「可選 seam」「已五站故省」看 | 本檔 Disposition 無此類句；若後站寫出則 G2 不得過算過 | 本檔全文
- Operational Context:不適用 — 本 slug 文件自檢。

### R-7: 系統 SHALL 讓 F1 牙紅 RP-1…RP-16，且 annex 不得減列；rewrite cap 數字已鎖

OC-10／SC-13／狀態機 §6／RP-8…RP-11。annex 只准加不准減。cap：hop≤2／Decide≤1／Goal reopen≤1；用盡 Escalated；不准暗改。計數落點 F2（Q10），數字本檔不重開。

**審的時候看什麼**
16 列對照是不是都能紅。annex 少一列算不算完成。第 3 次 hop 重寫還能不能繼續。

#### S-7.1
- GIVEN F1 牙已落地
- WHEN 對 RP-1…RP-16 各造一份對照稿（每份只觸發一列）
- THEN 16 份都 exit ≠ 0；缺任一列對照 = F1 未完成（SC-13）
- 觀測:n-a:本 PR 不寫牙。替代=本檔「RP → S」表 16 列；F1 用 16 份對照稿測
- Operational Context:不適用 — 牙覆蓋清單。

#### S-7.2
- GIVEN F1 annex 相對本 Decision「本方案要求」RP-1…RP-16 表
- WHEN annex 刪其中任一列
- THEN 該 annex 不得標 F1 完成；刪項 = 翻本 Decision，回 Stage 2（OC-10）
- 觀測:從 annex 列集合與 Decision RP 表做差集看 | 16 列都在、只准加算過 | Decision 該表
- Operational Context:不適用 — annex 集合契約。

#### S-7.3
- GIVEN 五站 slug 同一 hop 已重寫 2 次（第一次寫不算）
- WHEN 要求第 3 次重寫仍繼續
- THEN 紅並進 Escalated（RP-9）；不得把計數歸零再 hop
- 觀測:n-a:計數落點 F2。替代=本條數字 hop≤2 已鎖；F2 event 對該 hop_id 計數
- Operational Context:不適用 — cap 數字已鎖；落點 F2。

#### S-7.4
- GIVEN 已離開 Decide 一次之後又整站重開 Decide（含 Decision 翻案、OC 重裁）
- WHEN 要求第 2 次 Decide 重開仍繼續
- THEN 紅（RP-10）
- 觀測:n-a:計數落點 F2。替代=Decide≤1 已鎖；F2 對 decide_reenter 計數
- Operational Context:不適用 — 同 S-7.3。

#### S-7.5
- GIVEN 已 hop 出 Intake 之後，Goal／Success Criteria 已重開 1 次
- WHEN 要求第 2 次重開仍繼續
- THEN 紅（RP-11）
- 觀測:n-a:計數落點 F2。替代=Goal reopen≤1 已鎖；F2 對 goal 計數
- Operational Context:不適用 — 同 S-7.3。

#### S-7.6
- GIVEN Ship 機械項全綠，且 `7-review.md` 頂欄沒有人類寫入的 `verdict: PASS`
- WHEN 系統或 Agent 把該 slug 標 Done
- THEN 紅（RP-8）；狀態必須留 HumanWait，不得 Done
- 觀測:從 Ship 狀態與頂欄看 | 無人 PASS 不得 Done 算過 | 與 S-5.3 同一拒收家族；本條專咬 Done 標
- Operational Context:
  - Actor:Ship 審查者
  - Goal:出貨仍等人
  - Situation:機械全綠
  - Known information:A10 latch=是
  - Missing information:人類頂欄
  - Human decision:寫 PASS／REQUEST_CHANGES／HOLD
  - Authority:人
  - External dependency:無
  - Out-of-system action:人寫頂欄
  - Waiting/timeout behavior:HumanWait
  - Recovery:刪 Done 標、等人
  - Audit/handoff requirement:頂欄可重讀
  - Observation:見本條觀測

### R-8: 系統 SHALL 維持其餘 Must-keep 不因摺站消失，且 F1 牙只長在 scripts／annex

7A／M2／M4／M6／M7／M8／M12／M13／M16／OC-7。本 Stage 4 PR 只兩檔。Q6 仍 open 則本檔不得 PASS（OC-8）。

**審的時候看什麼**
有沒有用「已經五站了」省略圍欄／Evidence／Profile／DBC。本 PR diff 是不是只兩檔。頂欄有沒有被寫成 PASS。

#### S-8.1
- GIVEN 摺站後的規格／任務／牙
- WHEN 有人用「已經五站了」省略 M2 圍欄、M4 Real-world→Demo→OC、M6 Evidence 八點、M7 `fast`+`high` 拒、M8 DBC、M12 author≠approver、或 M13 html 重生
- THEN 該省略被點名違 brief（與 S-6.1 同型）；上列 M 的現行正本仍生效，本 feat 不刪
- 觀測:從本檔 Must-keep Disposition 與現行正本路徑是否仍被引用看 | 省略句被拒、正本路徑仍在算過 | 本檔 Disposition 表 + plugin SKILL／README §5／§7／`design-boundary-contract.md`
- Operational Context:不適用 — 維持既有正本，無新交接。

#### S-8.2
- GIVEN F1 施工範圍
- WHEN 寫牙或 annex
- THEN 只准改 `scripts/` 與 annex；不得改 `_templates/` 的 Stage 1–4、各站 `graph.yaml`、既有牙正本、`devflow-contract.json`（F0 與本 Stage 4 亦不改這些）
- 觀測:從 F1 PR 的 `git diff --name-only` 看 | 無 `_templates/`、無 `graph.yaml`、無契約 bump 算過 | 對照本 Stage 4 PR 檔集（S-8.3）
- Operational Context:不適用 — 檔集約束。

#### S-8.3
- GIVEN 本 Stage 4 PR 對 `origin/main`
- WHEN 跑 `git diff --name-only origin/main`
- THEN 只含 `docs/dev/five-station-simplify/4-spec.md` 與 `docs/dev/five-station-simplify/4-spec.html`；本檔頂欄 `verdict` 空白；`status: draft`；Agent 不得寫 `verdict: PASS`
- 觀測:從該 diff 與本檔 frontmatter 看 | 兩檔、verdict 空、status=draft 算過 | 本 PR
- Operational Context:不適用 — 本 hop 檔集，無人員交接。

#### S-8.4
- GIVEN 本檔 `## Assumption refs` 的 Q6 列 `status` 仍為 `open`（未抽一採用案）
- WHEN 有人把本檔 `verdict` 寫成 `PASS`
- THEN 違 OC-8；本 slug G2 不得過，直到抽案轉 `resolved` 或 owner 另裁 `oc-accepted`
- 觀測:從本檔 refs 表與頂欄 `verdict` 看 | Q6 仍 open 則 verdict 必須不是 PASS 算過 | 本檔
- Operational Context:
  - Actor:本 slug G2 reviewer
  - Goal:不把 Q6 升成已核事實
  - Situation:無採用逐字稿
  - Known information:OC-8；母版 dogfood 三案 = Observed
  - Missing information:採用現場是否同一手勢
  - Human decision:抽案，或明示 oc-accepted
  - Authority:owner
  - External dependency:採用案（public 禁收公司路徑）
  - Out-of-system action:抽一案或接受殘餘風險
  - Waiting/timeout behavior:未抽則本 slug G2 停
  - Recovery:抽案或 OC 接受風險後再評 G2
  - Audit/handoff requirement:refs 列 status
  - Observation:見本條觀測

## MODIFIED Requirements

### M-L1: 七份文檔仍在；例行人類停點從「每閘等人」改成「預設只 Ship 等人」

原條文（`docs/dev/readme-contract-extract.md` §3 表，約 L7–L17）：

> 1 `1-discussion.md` … Open Questions 全解或明標假設
> 2 `2-decision.md` … **G1** 方向核准 + OC 全裁決
> 4 `4-spec.md` … **G2** R/S 全審 + DD 全裁決 + Verification Profile + Demo verdict
> 7 `7-review.md` … **G3** … PASS → Exit Checklist

改成（F3 之後的新 slug；in-flight 仍走原文）：檔名與 G1／G2／G3 **物質／token 不動**。預設路線改走五個別名。例行人類停只留 Ship（舊 G3 物質）。G1／G2 物質與 twin 仍產，預設不再等人按提交判定。Demo 條件改走表 B（B1 latch），不是每 feat 等人。承接 R-1、R-5。

### M-L2: doctor 握手綠不得再被讀成路線證據

原條文（`hooks/_doctor_impl.py` 約 L193–L202；`hooks/runtime-capabilities.json` 只聲明 `supported_contract_versions=['2.0.0']`）：

> 專案契約版本必須 ∈ plugin `supported_contract_versions`，否則 fail-closed

改成（F1 annex／牙，不改本 hop 的 doctor 腳本）：握手規則本身可留。新增：COMPATIBLE／exit 0 **只**證明版本集合命中，不證明 hops 沒變，不證明已切五站。契約 2.0.0 + 五站 hops → 紅／不得改線。承接 R-2、R-3。

### M-L3: Stage 2／4 graph 預設路經 N7-g1／N6-g2 對新 slug 不再是例行人類停

原條文（`skills/dev-flow/stage2/graph.yaml` 約 L53–L57；`skills/dev-flow/stage4/graph.yaml` 約 L93–L98）：

> 預設路經 N7-g1／N6-g2（例行人類停點節點）

改成（F3 cut 之後的新 slug；F0–F2 **不改**這兩檔）：節點與 token 留著給 dual-read／舊 7。新 5 預設 hop **不等** 人寫 G1／G2 `verdict:`。本 PR 與 F1 **不改** `graph.yaml`。承接 S-1.1、S-8.2。

## REMOVED Requirements

無。不刪 G1／G2／`ACCEPTED` 檔或 token。不廢 Fast。不刪七檔名。不把 in-flight 折成五站。不刪 T 四欄或 acceptance seam。

## 行為流程圖(R 級)

```
[R-1] 摺例行停留物質
  五個別名
  token與七檔名不動
  謂詞假停修
  表A／B產不等於latch
[R-2] dual-read誠實
  解析兩套
  舊檔缺欄不紅
  九個SLOT語意槽
  doctor綠≠已切
[R-3] 採用端陷阱
  2.0.0加五站hops就紅
  不得寫成跟hops走
  未upgrade不得改線
[R-4] in-flight凍結舊7
  任一md整段舊7
  裸html不凍
  本slug跳不過
  舊7不套三cap
[R-5] 人主權
  空attestation不得離Spec
  chat不是判定
  代寫視為未寫
  否定跳過不得當skip
[R-6] Must-keep假完成
  少一M違brief
  T卡上就紅
  四欄與seam不可選
  可選字樣擋本slug G2
[R-7] F1牙最小集
  RP-1到16都能紅
  annex只准加
  rewrite cap用盡Escalated
  無人PASS不得Done
[R-8] 牙只scripts／annex
  其餘M不因摺站消失
  本PR只兩檔
  Q6 open則verdict不得PASS
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.4）。本 Stage 4 PR 可立即核對的子集：S-8.3（檔集）、S-8.4（verdict 空）、S-6.9（本檔無「可選四欄」）、S-2.5（doctor 握手現況）、S-4.1（本目錄已有 md）。其餘 S 的綠 = F1／F2／F3 落地後對照稿紅／綠。
- 既有測試全綠（回歸）：`bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md`；`bash scripts/check-stage4-rs-contract.sh`；既有 `hooks/devflow-doctor.sh` 對 2.0.0 仍 COMPATIBLE（本 hop 不改握手）。
- 非功能：指定檢查對單份 md 在本機同步結束；本 PR 不新增網路／filesystem／credential capability。
- 行為不變類（golden master）：舊 7 in-flight 仍有例行 G1／G2；Fast 仍吃 G2 物質；無 attestation 的 `ACCEPTED` 仍拒；七檔名與 token 仍在。

## Out of Scope

- 1B／1C、2B／2C、3B／3C、4B／4C、5B／5C、6B／6C、7B／7C（見 2-decision Rejected）。
- 重開 F0 十條；刪 G1／G2／`ACCEPTED`；改七檔名；廢 Fast；第二條 Journey／Actor／M ID 鏈。
- 本 PR 實作 F1 牙／annex／doctor 路線欄；本 PR 寫 coordinator；本 PR 切預設路線；本 PR 改 STATUS／HISTORY／`_templates/`／`graph.yaml`／既有牙／`devflow-contract.json`。
- 本 PR 填 G2 `verdict: PASS`；本 PR 合併；本 PR 發明第二份 Human Demo ACCEPTED。
- 拿本 slug 當新 5 白老鼠。
- 把 Q6 升成已核事實。
- 選定 dual-read JSON 鍵名或 coordinator event schema（OC-3；落本 slug F1／F2）。
- 本包不建採用現場回報口（Journey「口頭中繼」刻意維持）。
- public repo 禁收公司路徑（採用洞去識別化刻意維持）。

### Stage 3 對帳

`3-prototype.md` 已合 main（#309）：`status: approved`；`Human verdict: ACCEPTED | role=母版 owner | scenario=AC-1`；`Verdict attestation: human:rick @ 2026-09-14`。本檔引用該事實，不另填一份。Demo 前置已滿足。本檔 `verdict` 留空（不發明 G2 PASS）。

- Scenario AC-1（新 slug 中間不停）→ S-1.1、S-1.2
- Scenario AC-6（表 A／B 產不產／等不等）→ S-1.4、S-5.4、S-5.5
- Scenario AC-3（假完成 T；T 卡上就紅）→ S-6.1、S-6.2、S-6.3、S-6.4、S-6.9
- Scenario AC-4（空 attestation + Agent 代寫）→ S-5.1、S-5.2、S-5.3
- Scenario AC-8（本 slug 仍舊 7）→ S-4.1、S-4.2
- Scenario AC-5（舊檔不紅＋F3 cut 仍舊 7；不是 doctor 綠題）→ S-2.2、S-4.1、S-4.3
- Scenario SC-9（doctor 綠 ≠ 已切）→ S-2.5、S-3.1、S-3.2、S-3.3
- Scenario RP-14（否定跳過被當成已跳）→ S-5.6
- Method 盤 3 人見面時機 T 卡上就紅（選定；hop 板／Ship 重建棄）→ S-6.2
- Method 盤 5 現檔證據表 → S-2.5、S-4.1
- Operational Context Recovery（停修謂詞、人類親填 attestation、從 md 恢復舊 7、拒絕跟 hops 走、F1 收緊 skip）→ 各對應 S 的 Recovery 欄

## Diff Budget

本節是**估計**（給後續 F1／F2／F3，不是本規格 PR 的檔數）。超支本身非偏差，是停下判 L1/L2 的訊號。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| F1 annex（dual-read 九 SLOT + RP 最小集） | ≤2 | ≤220 | ≤80 |
| F1 牙（scripts／既有檢查加項，不新家族） | ≤4 | ≤260 | ≤360 |
| F2 coordinator／event／三 cap 計數 | ≤6 | ≤400 | ≤280 |
| F3 新 slug 預設切線（guide／STATUS 用語；不改 freeze slug） | ≤4 | ≤180 | ≤80 |
| **合計（後續刀）** | **≤16** | **≤1060** | **≤800** |

本規格 PR 本身：2 檔（`4-spec.md` + `4-spec.html`）。[Assumption] 後續刀係數按「一個 S 一到兩條測試」，未加 mutation。檔數 >15 是大案訊號；Decision 四刀不併，超支時先判 L1（不動 R/S）或回 G2。

## Dependencies

- `notes/design/five-station-simplify-brief-v3.md` 與 `notes/design/five-station-simplify-f0-state-machine.md` —— justification:F0 已核正本；本檔不重開十條。
- `hooks/_doctor_impl.py`／`hooks/devflow-doctor.sh` —— justification:SC-9／SC-10 現況握手；F1 加拒收，本 hop 不改。
- `.claude-plugin/marketplace.json` —— justification:單一 `source: ./` 是陷阱正本。
- `scripts/check-spec-gate.sh` —— justification:本 hop 形狀 Gate；RP-3 現已有 C4。
- `scripts/check-gate-tokens.sh` —— justification:S-1.3 token 仍在。
- `hooks/_stage3_impl.py` —— justification:S-5.6 誤匹配證據；F1 收緊，本 hop 不改。
- 後續 F1／F2／F3 本 slug 刀 —— justification:Decision 7A 四刀不併。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（annex／doctor／marketplace hops／coordinator／本 slug 文件）；②修改公開契約讀法（2.1.0 dual-read）；③跨模組 Interface（契約版本 ↔ hops 路線）；⑨Feature Risk = high；⑩三個以上模組；⑪狀態機與錯誤恢復（HumanWait／Escalated／in-flight freeze／skip-OC）
- Design source: Decision 1A–7A；brief §3 表 A／B；狀態機 §2–§6；Stage 3 D1 已 ACCEPTED。本檔 local lock = 九個 SLOT- id（不鎖鍵名）

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| F1 annex | 九 SLOT 語意 + RP 最小集 | 本 slug F1 寫手 | → 2.1.0 讀檔器、→ F1 牙 | 不得改 `_templates/` 1–4；不得減 RP 列；不得本 hop 先寫 |
| F1 牙（scripts／annex） | 紅 RP-1…16 與 2.0.0+五站 hops | F1 | → annex、→ 既有 check-spec-gate／_stage3 | 不得新開第二檢查家族當唯一入口；不得改既有牙正本於 F0／本 hop |
| doctor 握手 | 版本 ∈ supported | 既有 `_doctor_impl.py` | → `devflow-contract.json` | 不得把 COMPATIBLE 當路線證據；本 hop 不改 |
| marketplace hops | 換方法包 | 採用端 owner | → `source: ./` | 未 2.1.0 不得改線 |
| coordinator（F2） | 評謂詞 hop／停修／HumanWait | F2 | → brief §3、→ 狀態機 | 不得問人繞假謂詞；不得寫判定；不得折 in-flight |
| 本 slug 文件 | live freeze 樣本 | 本目錄 md | → 舊 7 graph | 不得寫入五站狀態 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| dual-read 2.1.0 | in:舊 7 或新 5 md；out:解析成功／合法缺席 | 舊檔缺新欄 → 不紅；未宣告 2.1.0 + 五站 hops → 紅 | 只讀站檔，不改 in-flight 路線 | `2.0.0` 繼續只讀舊 7 |
| 採用端拒收牙 | in:契約版本 + hops 預設；out:exit ≠ 0 | 2.0.0+五站 hops → 1 | 不改採用端檔 | doctor 握手行為可留 |
| skip-OC | in:2-decision 字句；out:skip 真／假 | 否定詞+跳過 → 不得 skip | 只讀 | 現行誤 PASS 記 F1 |
| in-flight 偵測 | in:目錄是否有 1–7 `.md`；out:舊 7／新 5 | 有 md 卻寫五站狀態 → 紅 | 不改已有 md | 裸 html 相容＝不凍 |
| Ship Done | in:頂欄 verdict；out:Done／HumanWait | 無人 PASS → 不得 Done | 頂欄與狀態同一真相 | 舊 7 G3 仍等人 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| annex SLOT 清單 | 讓 F1 命名鍵之前語意已鎖 | ← 本檔 S-2.4 | SLOT-id → 欄或等效句 | 少一槽 = F1 未完成 | S-2.4 |
| RP 最小集 | 16 列對照都能紅 | ← Decision RP 表 | 一列一 fixture | 刪列回 Stage 2 | S-7.1、S-7.2 |
| skip 否定閘 | 「不／無／不得」+「跳過」 | ← `_stage3_impl`（F1 改） | 句 → skip 假 | 現行誤綠記帳 | S-5.6 |
| freeze 偵測 | 只認 md | ← 目錄 listing | path → old_7 | html 不凍 | S-4.1、S-4.2 |
| T 卡 RP | 寫卡當下紅 | ← 5-tasks 四欄 | 缺欄 → 未完成 | 勾選無效 | S-6.2、S-6.3 |

### Design Constraints
- 必須:五個別名；token／檔名留；誠實三句；in-flight 只認 md；T 四欄+seam 不可選；RP 最小集只准加；牙只 scripts／annex；本 slug 舊 7；本檔 verdict 空。
- 禁止:本 hop 落地碼；本 hop 填 G2 PASS；本 hop 改 STATUS／模板／graph／契約版本；刪 token；把 Q6 當已核；把 M15／M16 寫成 Non-Goal；hop 板／Ship 重建當假完成的唯一紅點。
- Extension point:annex 鍵名、牙腳本名、event schema — F1／F2 命名，本檔不鎖。
- Known design limit:
  ① Q6 採用現場是否 chat 蓋章仍無逐字稿；本 slug G2 語意上仍咬（S-8.4）；C7 不因 `F1-annex` deadline 形狀紅本檔。
  ② A1／A2 是否分檔仍 Assumption；F1 annex 核 dest。
  ③ 現行 `_stage3_impl.py` 把否定跳過句讀成 skip；本 hop 不修（S-5.6）。
  ④ coordinator／2.1.0 bump 尚未存在；多數 S 的執行觀測在 F1／F2；本 hop 用對照稿＋SLOT 清單當替代觀測。
  ⑤ 審頁產器行為圖建議 8 框；本檔正好 8 個 R，不把 R-id 塞進別框。

## Verification Profile(G2 一併審)

- lane: full（判準:新能力、改公開契約讀法、高風險人機互動（停點／attestation／採用端改線）、不可逆切線在 F3。owner 已 lock full；與判準一致，無偏離）
- Risk: high（判準:公開契約／採用端路線／不可逆 freeze／人機 latch。模板「公開 API／不可逆／高風險人機互動」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得刪 G1／G2／`ACCEPTED` token 或改七檔名（S-1.3）
  - 不得把 doctor 綠寫成已切五站或可以跟 hops 走（S-2.5、S-3.2）
  - 不得讓舊 7 缺新欄一次變紅（S-2.2）
  - 不得遠端改未 upgrade 採用端路線（S-2.3、S-3.3）
  - 不得把本 slug 寫入五站狀態（S-4.1）
  - 不得用 chat 或 Agent 代寫判定（S-5.2、S-5.3）
  - 不得把四欄／seam／Must-keep 標可選（S-6.9）
  - 不得從 annex 減 RP 列（S-7.2）
  - 不得本 hop 改 `_templates/`／`graph.yaml`／`scripts/` 牙／STATUS／HISTORY／契約版本（S-8.2、S-8.3）
  - 不得在 Q6 仍 open 時把本檔 verdict 寫成 PASS（S-8.4）
  - 不得發明 G2 PASS 或第二份 Human Demo ACCEPTED
- Required layers:check-spec-gate；check-stage4-rs-contract；本 hop 檔集 diff（S-8.3）。F1 牙層在 F1 才變 Required，本 hop 不列入（尚未落地）
- Conditional layers:Supply chain — 當 F1 改到 scripts／annex 時，必跑既有 `devflow-check.sh` 對應段 + 16 列 RP 對照；當 F2 加 coordinator 時，必跑 hop／cap event 對照
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Race／stress（文件與同步檢查）、Windows 真機（Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md && bash scripts/check-stage4-rs-contract.sh`
- Reliability triage:
  - Concurrency: applicable — 契約版本與 marketplace hops 可被兩個更新源同時改；落到 S-3.1／S-3.3／Failure Model「遠端改線」
  - Idempotency: applicable — 同一份對照稿再跑指定檢查，exit 與字樣相同（S-2.5 doctor 現況、S-6.4 spec-gate、S-8.3 diff）
  - Timeout/retry: n-a — 本機檔案檢查同步結束，不自動重試；HumanWait 是等人寫判定，不是 timeout／retry 契約

Stage 3 Human verdict 已在 `3-prototype.md`：ACCEPTED | role=母版 owner | scenario=AC-1。attestation:`human:rick @ 2026-09-14`（#309）。4-spec 頂欄 `verdict` 留空，不是 Agent 自裁 PASS。

### Failure Model(Risk: high 必填)

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 例行停沒摺掉 | 人仍在 A4／A7 排隊 | 新 slug 前進紀錄含「請人審 A4」 | Required:S-1.1（F2 後） | 本 hop 無 coordinator |
| 謂詞假改問人 | 口頭繞過物質洞 | 拒絕理由含「要不要繼續」 | Required:S-1.2 | 同上 |
| 舊檔一次變紅 | in-flight 全紅 | 舊 7 缺新欄 exit ≠ 0 | Conditional:F1 dual-read | 2.1.0 未 bump |
| doctor 綠冒充已切 | 採用端被遠端改線 | 文案把 COMPATIBLE 當切線 | Required:S-2.5；Conditional:S-3.1 | 牙未落地 |
| 本 slug 被折五站 | 觀測被自己污染 | 本目錄寫入五站狀態 | Required:S-4.1 | — |
| 空 attestation 離 Spec | dogfood 捷徑回流 | hop 出 Spec 成功 | Required:S-5.1 | — |
| 假完成 T | checkbox 綠、工作沒做 | T-fake 標完成 | Required:S-6.2、S-6.3 | 牙未落地時只文件對照 |
| annex 減 RP | 「已五站」再成省略理由 | RP 列差集非空 | Required:S-7.2 | — |
| cap 被暗改 | 重寫無限 | 第 3 次 hop 仍繼續 | Conditional:S-7.3 | 落點 F2 |
| 本 hop 偷做 F1 | 未過 G2 就長牙 | diff 含 scripts／templates | Required:S-8.3 | — |
| Q6 升格 | 假已核事實 | 本檔 verdict=PASS 且 Q6 open | Required:S-8.4 | 採用逐字稿禁收 |
| skip 否定誤綠 | 以為 Stage 3 已跳 | `_stage3_impl` g2_demo=PASS | Required:S-5.6 記帳；Conditional:F1 | 本 hop 不改牙 |
| 跳過 hook 硬改 STATUS | 並行 session 互蓋 | STATUS 列被本 PR 改 | Required:S-8.3 | 人跳過 hook 屬 Known limit |

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記 Decision／Stage 3 留給本檔鎖定的選擇。不翻 1A–7A。狀態 = 待人審（G2 尚未核；**不是**已裁決 PASS）。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | annex 鍵名不鎖；語意鎖九個 SLOT- id（S-2.4）。F1 命名 JSON／YAML 鍵 | OC-3 禁本檔選定欄位名；測試仍要對得上槽 | `2-decision.md` OC-3；`1-discussion.md` Q8 | 改鎖鍵名 = 偷做 annex；改減 SLOT = 重寫 R-2 | 待人審 |
| DD-2 | F1 牙腳本名不鎖；落點只准 `scripts/` 與 annex | Backlog B 凍 Stage 1–4 模板；OC-7 本 hop 零碼 | `2-decision.md` OC-7／6A；`STATUS.md` Backlog B | 改模板釘欄 = 已拒 6C | 待人審 |
| DD-3 | Feature Risk = high；本檔 `verdict` 留空；implementer 不得寫 PASS | 公開契約 + 採用端路線 + latch；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief | 改 normal 則 Failure Model 改選配；代填 PASS = 假綠 | 待人審 |
| DD-4 | Q6 refs deadline 寫 `F1-annex`、status=open；語意擋 G2 用 S-8.4 不靠 C7 | C7 只認日期或 stage-2／stage-3；用 stage-2 會讓本檔形狀自殺，與「先寫得出 draft spec」衝突 | `2-decision.md` OC-8；`scripts/check-spec-gate.sh` C7 | 改 stage-2 + open → 本檔 check-spec-gate 紅，draft 送不出形狀 | 待人審 |
| DD-5 | 人見面時機鎖定 T 卡上就紅；hop 板／Ship 重建不進 R/S 當完成定義 | Stage 3 Human ACCEPTED 已選；對齊 SC-3「該 T 不得標完成」 | `3-prototype.md` 盤 3；`2-decision.md` SC-3 | 改 hop 才紅 = 晚發現，違 SC-3 | 待人審 |
| DD-6 | 本檔用 8 個 R（1A 停點／2A 誠實／3A 陷阱／4A freeze／5A 人主權／6A Must-keep／7A 牙+cap／8 範圍+Q6） | 審頁產器建議 8 框；超過會 WARNING | `scripts/build-stage4-html.py` steps[:8]；vbox-fig 8 框建議 | 拆第 9 個 R 則須把某 SHALL 併框，否則圖丟高編號 | 待人審 |
| DD-7 | RP-3 在本檔改寫成「C4 未定事項三詞或不可測」，不回抄 Decision 那個未定 token | C4 全檔掃三詞；抄原文會讓本檔形狀紅 | `scripts/check-spec-gate.sh` C4；`2-decision.md` RP-3 | 回抄 token → spec-gate C4 紅 | 待人審 |
| DD-8 | rewrite cap 數字維持 hop≤2／Decide≤1／Goal reopen≤1；計數落點仍本 slug F2 | Q10 已移交 F2；本檔不重開數字 | `2-decision.md` 約束 5；狀態機 §3 | 改數字 = 翻 Decision | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不跑 `status-update.sh`、不改 HISTORY、不開 5-tasks。
- 本 hop 不落地 Stage 6 守衛碼；形狀以 R/S 為準。
- 負向對照稿目錄建議 `scripts/fixtures/five-station/`（F1 才新增檔）。
- A1／A2 共寫 `1-discussion.html` 保持 open，落 F1 annex。
- 未讀 B／C 線 Stage 4 分支；本檔獨立從 main tip 的 1／2／3 收斂。

## Test Skeletons(選配)

- `test_s_1_1_new_slug_no_a4_a7_human_wait`
- `test_s_1_2_false_predicate_stops_without_asking`
- `test_s_1_3_gate_tokens_and_seven_filenames_remain`
- `test_s_1_4_table_a_b_generate_vs_latch`
- `test_s_2_1_dual_read_parses_old7_and_new5`
- `test_s_2_2_old7_missing_new_fields_not_red`
- `test_s_2_3_undeclared_210_stays_old7`
- `test_s_2_4_annex_has_nine_slots`
- `test_s_2_5_doctor_green_is_not_cut`
- `test_s_3_1_contract_200_plus_five_hops_red`
- `test_s_3_2_doctor_green_follow_hops_copy_red`
- `test_s_3_3_marketplace_update_is_not_cut`
- `test_s_4_1_this_slug_five_station_hop_rejected`
- `test_s_4_2_html_only_is_not_in_flight`
- `test_s_4_3_pre_f3_new_tracks_old7`
- `test_s_4_4_old7_skips_rewrite_caps`
- `test_s_5_1_b1_empty_attestation_cannot_leave_spec`
- `test_s_5_2_chat_is_not_attestation`
- `test_s_5_3_agent_write_counts_as_missing`
- `test_s_5_4_b1_miss_must_not_require_accepted`
- `test_s_5_5_latch_miss_ask_human_red`
- `test_s_5_6_skip_oc_negation`
- `test_s_6_1_missing_must_keep_violates_brief`
- `test_s_6_2_t_card_red_on_missing_fields`
- `test_s_6_3_no_red_or_self_review_incomplete`
- `test_s_6_4_unmeasurable_s_fails_spec_gate`
- `test_s_6_5_test_name_without_s_id_red`
- `test_s_6_6_files_not_subset_red`
- `test_s_6_7_no_raw_output_red`
- `test_s_6_8_quiz_only_when_irreversible`
- `test_s_6_9_optional_must_keep_blocks_this_g2`
- `test_s_7_1_all_sixteen_rp_fixtures_red`
- `test_s_7_2_annex_cannot_drop_rp_row`
- `test_s_7_3_third_hop_rewrite_escalates`
- `test_s_7_4_second_decide_reopen_red`
- `test_s_7_5_second_goal_reopen_red`
- `test_s_7_6_ship_done_without_human_pass_red`
- `test_s_8_1_remaining_m_not_omitted`
- `test_s_8_2_f1_teeth_only_scripts_annex`
- `test_s_8_3_this_pr_two_files_verdict_empty`
- `test_s_8_4_q6_open_blocks_g2_pass`

## 確認紀錄

- 接手盤點 | 2026-09-14 | G1 PASS（#303）；Stage 3 Human ACCEPTED（#309）；1-discussion 驗收雛形 8 條（AC-1…AC-8）；living 受影響 3 條（七檔+閘、doctor 握手、graph 例行停節點）。本 hop 不改 living 正本。
- R 範圍 | 2026-09-14 | R-1…R-8 對齊 1A…7A + dual-read／陷阱／freeze／人主權／Must-keep／RP＋cap／本 hop 範圍。獨立於 B／C 線 Stage 4。
- S 展開 | 2026-09-14 | S-1.1…S-8.4 各含觀測三件；涉人員 S 有 Operational Context；純地板 S 標不適用。
- 收尾四節 | 2026-09-14 | Acceptance／Out of Scope／Diff Budget／Dependencies 齊。
- Profile + DBC | 2026-09-14 | lane=full、Risk=high、Failure Model、Reliability 三問、DBC applicable。
- Stage 3 對帳 | 2026-09-14 | Demo Script 八場 + Method 盤 3／盤 5 + Recovery 皆有 S 下落。引用既有 Human ACCEPTED，不另填。
- DD 掃描 | 2026-09-14 | 上層 8 條待人審；DD 節無未決殘留字樣；無未定三詞；不翻 Decision。
- 機械關卡 | 2026-09-14 | 跑 `scripts/check-spec-gate.sh`（本 hop 自檢）；html 用 `scripts/build-stage4-html.py --action`。
