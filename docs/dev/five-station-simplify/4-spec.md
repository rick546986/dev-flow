---
feature: five-station-simplify
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站簡化（Implementer B：條件頁／空欄／freeze／握手陷阱）

> 基準:main tip `fdd39c5`（#309 Human Demo ACCEPTED、#310 STATUS 伴列）。契約不 bump。Lane = **full**。本 hop **只本檔 + 審頁 html**；`status: draft`；頂欄 `verdict:` 留空。**不發明 G2 PASS**、不改 `STATUS.md`／`HISTORY.md`、不改 `_templates/`／`graph.yaml`／`scripts/` 牙／契約、不開 Stage 5、不合併。
> Decision 正本:`docs/dev/five-station-simplify/2-decision.md`（1A+2A+3A+4A+5A+6A+7A；OC-1～OC-11 ✅；G1 `verdict` PASS）。`3-prototype.md` `status: approved`，`Human verdict: ACCEPTED | role=母版 owner | scenario=AC-1`，attestation `human:rick @ 2026-09-14`。
> B 線獨立於 A／C，未讀他線 Stage 4。本檔把表 A／B 謂詞、空 attestation、in-flight freeze、marketplace×doctor 綠陷阱寫成可測 S；Must-keep M1–M16 去向齊；T 四欄＋seam 標 Owner-locked **未來 T 約束**。F1 牙本 hop 不落地。

## 補助模組生命週期（預覽）

主詞是「條件頁 latch + in-flight freeze + 採用端握手陷阱」，不是整份方法論。直式圖，置中。
- 新生（這輪沒有）：不加 coordinator 碼、不加 F1 牙檔、不加契約 2.1.0 欄位名。
- 改行為（相關一格）：F1 起 `scripts/`／annex 必須能紅 RP-1…RP-16 與「契約 2.0.0 + 五站 hops」；F3 後新 slug 依表 A／B 產頁≠latch；本 slug 整段舊 7。
- 退役：沒有。
- 不動：七檔名、G1／G2／`ACCEPTED` token、各站 `graph.yaml`、Stage 1–4 模板、本 slug 舊 7 例行閘、STATUS／HISTORY 寫入口、契約 `2.0.0`、既有 doctor 握手演算法。

## Fast early risk triage

full lane；本表只留痕，C8 no-fire。六問皆「是」→ 去向不得 Fast。

| 問 | 答 |
|---|---|
| 改變下一步？ | 是。Decide／Spec／Build 完成且中間 latch 未命中時，下一步是 hop，不是「請按提交判定」。 |
| 改權限／核准語意？ | 是。誰准寫 `ACCEPTED`／Ship `PASS`；chat 不是判定。 |
| 改等待／完成語意？ | 是。例行 G1／G2 不再等人；Ship 與 B1 命中仍等人。 |
| 改角色交接？ | 是。coordinator 評謂詞；人只在 latch 列寫頂欄。 |
| 改系統外動作？ | 是。marketplace update 換 hops ≠ 已切五站。 |
| 改中斷恢復？ | 是。已有 1–7 任一 `.md` → 整段舊 7 到 Ship。 |
| 去向 | full |

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「例行 G1／S3-ACCEPTED／G2 讓方向、互動、契約三次都要等人」 | 本方案處理 | S-1.1、S-1.2、S-1.8 |
| 「Treat as PASS／都過／可以落成 verdict: PASS」 | 本方案處理 | S-2.1、S-2.2 |
| Journey「owner chat 蓋章；方向卡沒被讀完也過」 | 本方案處理 | S-1.1、S-2.1 |
| Journey「Demo 欄空、chat 仍准開 Stage 4」 | 本方案處理 | S-2.1、S-2.3 |
| Journey「實作者若省四欄／seam，勾選假完成」 | 本方案處理 | S-5.2、S-5.6 |
| Workaround「Agent 把口頭章落進 md 頂欄」 | 本方案處理 | S-2.1、S-2.2 |
| Exception「in-flight 整段舊 7」 | 本方案處理 | S-3.1、S-3.2 |
| Exception「F0–F2 母版新開改版軌仍舊 7」 | 本方案處理 | S-3.2 |
| 「marketplace 可換 hops，doctor 仍可因 2.0.0 握手綠」 | 本方案處理 | S-4.1、S-4.2、S-4.3 |
| 「本 slug = live freeze 樣本」 | 本方案處理 | S-3.1 |
| Q11 空 attestation 五站後是否仍機械拒 | 本方案處理 | S-2.1、S-2.3 |
| M1–M16 帶走表 | 本方案處理 | S-5.1 |
| Journey「採用現場踩洞靠口頭中繼」 | 刻意維持 | Out of Scope：本包不建回報口 |
| Workaround「採用洞進 dispatch-accounting-symmetry，不進 public issue」 | 刻意維持 | Out of Scope：public repo 禁收公司路徑 |
| Exception「Fast 仍吃 G2 物質」 | 刻意維持 | Out of Scope：不廢 Fast |
| Exception「[Assumption] 採用現場仍 chat 蓋章」 | 仍待驗 | Assumption refs Q6；OC-8；不得升成已核 |
| Exception「A1／A2 共寫 1-discussion.html」 | 仍待驗 | Known limit：本 slug F1 annex 核 dest，本檔不選定分檔 |

## Must-keep Disposition（Q9 種子；不另發 ID）

| M | 去向 | 下落 |
|---|---|---|
| M1 ID 鏈；測試名含 S-id | 本方案處理 | S-5.4 |
| M2 圍欄 | 刻意維持 | Out of Scope：實作者禁讀 1／2／3 補洞 |
| M3 反模糊三律 | 本方案處理 | S-5.3 |
| M4 Real-world→Demo→OC | 本方案處理 | S-1.4、S-1.5、S-1.6 |
| M5 人寫 ACCEPTED／Ship PASS | 本方案處理 | S-2.1、S-2.2 |
| M6 G3 Evidence 八點 | 本方案處理 | S-1.3 |
| M7 Profile + fast+high 拒 | 刻意維持 | Verification Profile 本節 |
| M8 DBC 條件式 | 刻意維持 | Design Boundary Contract 本節 |
| M9 Files ⊆ 5-tasks | 本方案處理 | S-5.2 |
| M10 驗證五律（原始輸出） | 本方案處理 | S-5.2 |
| M11 T 四欄 + RED→獨立審查 seam | 本方案處理 | S-5.2、S-5.6 |
| M12 author≠approver | 刻意維持 | S-2.2；Ship 與任何 latch |
| M13 html 重生 | 本方案處理 | S-5.8 |
| M14 不可逆才 Quiz | 刻意維持 | S-1.10 |
| M15 token／檔仍在 | 本方案處理 | S-1.1、S-1.2 |
| M16 F0 不改 graph／牙 | 本方案處理 | S-6.1、S-6.4 |

T 四欄（Covers／Files／Verify／Blocked-by）與 RED→獨立審查 seam = **Owner-locked 未來 T 約束**。本檔不發明 5-tasks 新欄名；Stage 5 每 T 必須帶這四欄與 seam，缺則該 T 不得標完成（S-5.6）。

## ADDED Requirements

### R-1: 系統 SHALL 依表分開產頁與 latch
1A／SC-1／SC-6／AC-6／brief §3。表 A／B 每列有**生成謂詞**與**人類 latch**。生成假 → 不產頁、不算缺。latch 假 → 不准問人。latch 真 → stop-at 該站、把頁給人、等人把判定寫進同目錄 md。STATUS 旗標定義見下；本 hop 不改 `STATUS.md`。

**STATUS 旗標（本檔可測定義）**

| 旗標 | 字面位置 | latch 開火時 | latch 未開火時 |
|---|---|---|---|
| `Gates-G1` | `docs/dev/STATUS.md` Active 列 `Gates` 的 `G1✅`／`G1⬜` | 舊 7：等人寫 G1 `verdict:` 才准翻 ✅。五站新 slug：A4 latch=否，不得因 twin 已產把列寫成「等人簽 G1」 | 五站：Decide 謂詞全真即可 hop；Gates 不出現 G1 等人 |
| `Gates-G2` | 同列 `G2✅`／`G2⬜` | 舊 7：等人寫 G2。五站：僅 B1 命中時停 Spec；A7 latch=否 | A7 twin 仍產；Gates 不因 twin 已產標 G2 已過 |
| `Gates-G3` | 同列 `G3✅`／`G3⬜` | A10 永遠 latch：機械全綠仍保持 `G3⬜` 直到人寫 Ship `PASS` | 不適用（A10 latch 永遠是） |
| `Demo-B1` | `3-prototype.md` `Human verdict` + `Verdict attestation` | 九條 trigger 任一命中：空 attestation 不得當已過 | 未命中：不建 Demo 頁；Gates 不標「缺 Stage 3」 |
| `in_flight` | `docs/dev/<slug>/` 是否已有 1–7 任一 `.md` | 真 → 整段舊 7；五站 hop 跳 G1／G2 必須失敗 | 僅 html、無 md → 不凍（OC-5） |
| `status-diff` | 本 PR `git diff --name-only` 是否含 `docs/dev/STATUS.md` | 本 hop 必須**不含**（OC-4） | 同左 |

**審的時候看什麼**
每列只問四件事：產不產、latch 開不開、stop-at 在哪、哪一格 STATUS 旗標准翻。A4／A7 twin 仍產 ≠ 等人。latch 未開卻留下「請人審」→ 紅。

#### S-1.1 A4 產頁且不 latch
- GIVEN F3 後新 slug 目錄已有 `2-decision.md`，`## Decision` 非空，Owner Calls 無「待人審」殘留，B1 九條 trigger 全未勾
- WHEN coordinator 評 Decide→Spec，並讀該 slug 前進紀錄與 `STATUS.md` Active 列
- THEN 生成 A4 方向卡（舊 G1 twin）為是；人類 latch 為否；前進紀錄無字面「請人審 A4」與「請按提交判定」；stop-at 不是 Decide 等人；`Gates-G1` 不得只因 twin 已產改成等人簽 G1
- 觀測: n-a:coordinator 本 hop 不落地。替代：從 `notes/design/five-station-simplify-brief-v3.md` 表 A 的 A4 列與 3-prototype 盤 2 對照 | 生成=是、latch=否、無「請人審 A4」算過 | 用 brief 表 A + 盤 2 A4 列測
- Operational Context:
  - Actor:coordinator（F2 後）／母版 owner
  - Goal:Decide 物質留下、例行 G1 不停
  - Situation:Decision 與 OC 已裁決
  - Known information:A4 生成謂詞=有 `2-decision.md`；latch=否
  - Missing information:無
  - Human decision:不在 A4 按提交判定
  - Authority:coordinator 評謂詞；人禁被叫來繞假謂詞
  - External dependency:無
  - Out-of-system action:不把 A4 URL 當「請簽 G1」丟進 chat
  - Waiting/timeout behavior:不等 G1；謂詞假才停修
  - Recovery:OC 有未裁列 → 停 Decide 補裁，不改問「要不要繼續」
  - Audit/handoff requirement:前進紀錄可核對無「請人審 A4」
  - Observation:見本條觀測

#### S-1.2 A7 產頁且不 latch
- GIVEN 同一新 slug 已有 `4-spec.md`，每個 S 有觀測欄，`lane:`／`Risk:` 可解析，Drafting Decisions 無「待人審」殘留，B1 已熄或未命中
- WHEN coordinator 評 Spec→Build
- THEN 生成 A7 契約卡（舊 G2 twin）為是；人類 latch 為否；前進紀錄無字面「請人審 A7」；`Gates-G2` 不得只因 twin 已產標已過
- 觀測: n-a:coordinator 本 hop 不落地。替代：從 brief 表 A 的 A7 列與盤 2 對照 | 生成=是、latch=否、無「請人審 A7」算過 | 用 brief 表 A + 盤 2 A7 列測
- Operational Context:
  - Actor:coordinator／母版 owner
  - Goal:G2 物質留下、例行 G2 不停
  - Situation:規格形狀已綠
  - Known information:A7 生成=有 `4-spec.md`；Demo 條件在 B1 不在 A7
  - Missing information:無
  - Human decision:不在 A7 按提交判定
  - Authority:同 S-1.1
  - External dependency:無
  - Out-of-system action:不把 A7 URL 當「請簽 G2」
  - Waiting/timeout behavior:不等 G2
  - Recovery:形狀紅 → 停 Spec 修 S，不改問人
  - Audit/handoff requirement:前進紀錄無「請人審 A7」
  - Observation:見本條觀測

#### S-1.3 A10 機械綠仍 latch
- GIVEN 新 slug 已有 `7-review.md`，G3 物質檢查全綠，md 頂欄 `verdict:` 空白
- WHEN coordinator 評 Ship→Done，並讀 `Gates-G3`
- THEN 生成 A10 為是；人類 latch 為是；stop-at = Ship／`HumanWait`；不得標 Done；`Gates-G3` 保持 `G3⬜` 直到人寫 `verdict: PASS`
- 觀測:從狀態機 `notes/design/five-station-simplify-f0-state-machine.md` §2.5 與 brief 表 A A10 列看 | 機械綠仍必須進 HumanWait、無人 PASS 不得 Done 算過 | 用該兩檔原文測
- Operational Context:
  - Actor:Ship 審查者
  - Goal:出貨仍由人寫頂欄
  - Situation:機械項全綠
  - Known information:A10 latch=是；Agent 禁寫 PASS
  - Missing information:人是否讀完 Evidence 八點
  - Human decision:寫 `PASS`／`REQUEST_CHANGES`／`HOLD`
  - Authority:只有人寫 md 頂欄 `verdict:`
  - External dependency:無
  - Out-of-system action:人打開出貨審頁
  - Waiting/timeout behavior:停到人寫；無逾時自動 Done
  - Recovery:`HOLD` 留 Ship；`REQUEST_CHANGES` 回可改的上一站
  - Audit/handoff requirement:判定正本=同目錄 md 頂欄，不是勾選
  - Observation:見本條觀測

#### S-1.4 A5 未命中不建頁
- GIVEN 一條純守衛 feat：`3-prototype.md` 不存在，或九條 trigger 全未勾且已寫 n-a 原因
- WHEN coordinator 評 Spec，並看 A5 是否建 html
- THEN 不建原型審頁；latch=否；G2 Demo 條件記 N/A + 原因（不是空白）；`Demo-B1` 不存在；`Gates` 不標「缺 Stage 3」為缺陷
- 觀測:從 brief 表 A A5 列與 3-prototype 盤 2「A5 n-a」對照 | 無檔或全未勾 → 不建頁、n-a 有原因算過 | 用盤 2 好例測
- Operational Context:
  - Actor:母版 owner
  - Goal:沒命中不第二次等人
  - Situation:九條 trigger 全假
  - Known information:A5 生成謂詞要「有檔且 trigger≥1」
  - Missing information:無
  - Human decision:不補假 Demo
  - Authority:未命中不准產頁、不准問人
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無第二次人停
  - Recovery:後來才命中 trigger → 改走 S-1.5
  - Audit/handoff requirement:n-a 原因寫在 3-prototype 或 G2 Demo 欄
  - Observation:見本條觀測

#### S-1.5 B1 命中則 latch 停 Spec
- GIVEN 新 slug 九條 trigger 至少一條已勾（本 slug 對照：改變下一步／角色交接／人工核准／等待／權限／系統外動作 = 6 條）
- WHEN coordinator 評 Spec→Build，`3-prototype.md` 的 Human verdict 不是 `ACCEPTED` 或 attestation 行缺 `human:` + `@`
- THEN B1 latch=是；stop-at = Spec／`HumanWait`；不得 hop 出 Spec；必須把 Demo 頁給人；`Demo-B1` 未熄時 `Gates-G2` 不得標已過
- 觀測:從本目錄 `3-prototype.md` 觸發判定（6 條勾）與狀態機 §2.3 條 6 對照 | 命中且無完整 attestation → 不得離 Spec 算過 | 用本目錄現檔 + 狀態機 L90-L96 測
- Operational Context:
  - Actor:母版 owner
  - Goal:命中互動時人親做 Demo
  - Situation:trigger≥1
  - Known information:B1 latch=是；Agent 禁寫 attestation
  - Missing information:人是否走完 Demo Script
  - Human decision:親填 `ACCEPTED` + attestation，或 `REVISE`
  - Authority:只有參與 Demo 的人
  - External dependency:人實際點盤
  - Out-of-system action:依 Demo Script 走卡
  - Waiting/timeout behavior:停 Spec 到人寫完；`NOT_REVIEWED` 不得前進
  - Recovery:欄空 → 人補寫；禁止叫 Agent 代填
  - Audit/handoff requirement:attestation 行緊隨 Human verdict
  - Observation:見本條觀測

#### S-1.6 B1 未命中不產 Demo
- GIVEN 新 slug 九條 trigger 全未勾，已落檔 n-a 原因
- WHEN coordinator 評 Spec→Build 或有人要求 `ACCEPTED`
- THEN 不產 Demo；不准問人；無第二次人停；要求 `ACCEPTED` → 紅（RP-12）
- 觀測:從狀態機 §6.5 與 Decision RP-12 對照 | 未命中卻要求 ACCEPTED 必須列為拒收算過 | 用 2-decision RP-12 列測
- Operational Context:
  - Actor:coordinator
  - Goal:未命中不造第二次人停
  - Situation:純後端／純守衛
  - Known information:B1 命中謂詞=九條任一
  - Missing information:無
  - Human decision:不補假 ACCEPTED
  - Authority:未命中禁問人
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無 B1 等待
  - Recovery:誤勾 trigger → 改走 S-1.5
  - Audit/handoff requirement:n-a 原因非空白
  - Observation:見本條觀測

#### S-1.7 latch 未命中卻問人必須紅
- GIVEN 新 slug 停在 Decide 或 Spec，A4／A7 latch=否，A10／B1 皆未開火
- WHEN coordinator 或 Agent 留下字面「請人審」「請 owner 看一下」「要不要繼續」
- THEN 該筆記錄為違 brief §3 出口第 5 步；F1 牙紅（RP-14）；stop-at 必須是「該站謂詞假，停修」，不是 HumanWait
- 觀測:從 Decision RP-14 與 3-prototype 盤 2 壞例對照 | 有「請人審」且 latch 列全假 → 列為紅算過 | 用盤 2 壞例 + RP-14 測
- Operational Context:
  - Actor:coordinator
  - Goal:不把客氣問人當停點
  - Situation:中間站物質未過或已過但 latch=否
  - Known information:latch 列假
  - Missing information:無
  - Human decision:不回答「要不要繼續」來繞謂詞
  - Authority:coordinator 禁問
  - External dependency:無
  - Out-of-system action:不把頁 URL 在 latch=否時丟給人
  - Waiting/timeout behavior:無人等
  - Recovery:刪「請人審」紀錄，回到該站修謂詞
  - Audit/handoff requirement:前進紀錄可被掃到「請人審」字樣
  - Observation:見本條觀測

#### S-1.8 謂詞假則停該站修
- GIVEN 新 slug 在 Decide 且 OC 仍有未裁列，或在 Spec 且某一 S 缺觀測欄，或在 Build 且某一 T 缺 Verify
- WHEN coordinator 評 hop
- THEN 不得 hop；stop-at = 該站；拒絕理由字面含該謂詞（「OC 未裁」／「缺觀測」／「缺 Verify」）；不得改寫成「先問 owner 要不要繼續」
- 觀測:從 1-discussion AC-1 觀測句與 3-prototype 盤 1 末段對照 | 停修理由是謂詞假、不是問人算過 | 用 AC-1 + 盤 1 測
- Operational Context:
  - Actor:該站寫手
  - Goal:補齊謂詞再 hop
  - Situation:自動前進有一假
  - Known information:哪一條謂詞假
  - Missing information:補完後是否全真
  - Human decision:修檔，不授權跳過
  - Authority:coordinator 只評謂詞
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無人等；寫手修完再評
  - Recovery:補齊後重評；吃 hop cap（舊 7 不套）
  - Audit/handoff requirement:拒絕輸出含謂詞名
  - Observation:見本條觀測

#### S-1.9 表 A 其餘列產頁且不 latch
- GIVEN 新 slug 分別已有 `1-discussion.md`／`2-decision.md`／`4-spec.md`／`5-tasks.md`／`6-implementation-notes.md`
- WHEN 逐列評 A1／A2／A3／A6／A8／A9
- THEN 各列生成=是；人類 latch=否；A8／A9 不得因「想給人看任務板」進入 HumanWait
- 觀測:從 brief 表 A 各列「人類 latch」欄看 | 上列六格皆否算過 | 用 brief L86-L97 測
- Operational Context:不適用 — 與 S-1.1／S-1.2 同型的列舉對照，無新的人員交接。

#### S-1.10 B2 同一人停且 B4 不可逆才 Quiz
- GIVEN 新 slug 命中 B1 的前端／下一步／多種互動三條之一（B2），或變更屬不可逆（schema／公開 API／權限／金流／資料遺失）
- WHEN 評 B2／B4
- THEN B2 與 B1 共用**一次** HumanWait，不另開第二次人停；B4 可與 A10 同一人停；非不可逆卻強制 Quiz 當例行停 → 違 G-out-1／RP-7
- 觀測:從 brief 表 B B2／B4 列與 Decision RP-7 對照 | 同一人停、非不可逆不做 Quiz 算過 | 用 brief L101-L117 + RP-7 測
- Operational Context:
  - Actor:母版 owner／approver
  - Goal:Quiz 不是第三個例行停
  - Situation:不可逆才做 Quiz
  - Known information:B4 命中謂詞=不可逆
  - Missing information:無
  - Human decision:不可逆時與 Ship 同一次停答 Quiz
  - Authority:approver
  - External dependency:無
  - Out-of-system action:答 Quiz
  - Waiting/timeout behavior:可併 Ship；不准拆第三次例行停
  - Recovery:誤做 Quiz → 記違 G-out-1
  - Audit/handoff requirement:Quiz 全對才准與 Ship 一起過
  - Observation:見本條觀測

### R-2: 系統 SHALL 拒絕空欄 attestation 與 chat 判定
5A／SC-4／SC-6／RP-12／RP-13／RP-16／OC-6／AC-4。判定正本=同目錄 md 頂欄或 Human verdict 行。owner chat「可以／准開下一站／Treat as PASS」不得寫入，也不得當 attestation 替代。

**審的時候看什麼**
只看 md 行與 hop 拒絕，不看 chat。空欄 +「可以開 Stage 4」必須仍卡 Spec。Agent 寫入的 `ACCEPTED`／Ship `PASS` 當成沒寫。

#### S-2.1 空 attestation 加 chat 准開不得離 Spec
- GIVEN B1 已命中；`3-prototype.md` 的 Human verdict 空白或 `NOT_REVIEWED`；`Verdict attestation:` 空白；Cursor chat 出現「可以開 Stage 4」
- WHEN 任何程序把該 chat 當核准並嘗試 hop 出 Spec
- THEN hop 失敗（RP-13）；chat 字串不得寫入 Human verdict，也不得寫入 attestation；`Demo-B1` 保持未熄
- 觀測:從 `docs/dev/dogfood-ping/DOGFOOD-NOTES.md` L9 與 Decision 5A／OC-6 對照 | 欄空仍開 Stage 4 的對照必須列為不得離 Spec 算過 | 用 DOGFOOD-NOTES L9 + 本目錄曾 NOT_REVIEWED 的史實測
- Operational Context:
  - Actor:母版 owner
  - Goal:空欄不能被口頭帶走
  - Situation:dogfood 捷徑
  - Known information:chat 不是判定
  - Missing information:人是否親做 Demo
  - Human decision:親寫 attestation，或不准 hop
  - Authority:md 頂欄／Human verdict 行
  - External dependency:Cursor chat（系統外）
  - Out-of-system action:人拒絕把「可以」當 attestation
  - Waiting/timeout behavior:停 Spec
  - Recovery:人親填完整行後走 S-2.4
  - Audit/handoff requirement:chat 紀錄不得替代 attestation 行
  - Observation:見本條觀測

#### S-2.2 Agent 代寫視為未寫
- GIVEN Agent 或 coordinator 把 `ACCEPTED` 寫進 `3-prototype.md`，或把 `verdict: PASS` 寫進 `7-review.md`，且無 `Verdict attestation: human:<名> @ <YYYY-MM-DD>` 或無人在頂欄親寫
- WHEN 系統評該判定是否已寫
- THEN 視為未寫（RP-16）；不得離 Spec；不得 Done；fixture 含 `test-only human fixture` 字樣的 ACCEPTED 正式判定拒收
- 觀測:從 `_templates/3-prototype.md` 頂註「Agent 禁代填」與 Decision RP-16 對照 | 代寫=未寫算過 | 用模板頂註 + RP-16 測
- Operational Context:
  - Actor:Ship 審查者／母版 owner
  - Goal:機器不能出貨
  - Situation:有人叫 Agent「Treat as PASS」
  - Known information:M5／G-out-4
  - Missing information:無
  - Human decision:刪代寫，改自己寫
  - Authority:人；author≠approver
  - External dependency:無
  - Out-of-system action:owner 自己鍵入
  - Waiting/timeout behavior:判定未寫則繼續等
  - Recovery:刪 Agent 行，人重寫
  - Audit/handoff requirement:attestation 必須 `human:` 開頭
  - Observation:見本條觀測

#### S-2.3 B1 未命中卻要求 ACCEPTED 必須紅
- GIVEN 九條 trigger 全未勾
- WHEN 規格或 hop 要求 Human verdict=`ACCEPTED` 才能離 Spec
- THEN F1 牙紅（RP-12）；走 S-1.6
- 觀測:從 Decision RP-12 列看 | 未命中卻要求 ACCEPTED → 紅算過 | 用 RP-12 原文測
- Operational Context:不適用 — 與 S-1.6 同一拒收，無新交接。

#### S-2.4 人類 ACCEPTED 加 attestation 可離 Spec
- GIVEN B1 已命中；`Human verdict: ACCEPTED`；下一行 `Verdict attestation: human:rick @ 2026-09-14`；不是 `REVISE`／`NOT_REVIEWED`
- WHEN coordinator 再評 Spec→Build
- THEN B1 熄火；在其餘 Spec 謂詞全真下准 hop；本目錄現況即此形（#309）
- 觀測:從 `docs/dev/five-station-simplify/3-prototype.md` L353-L354 看 | 字面 ACCEPTED + `human:rick @ 2026-09-14` 算過 | 用該檔現況測
- Operational Context:
  - Actor:母版 owner
  - Goal:Demo 做完才能進規格
  - Situation:本 slug 已 ACCEPTED
  - Known information:attestation 行完整
  - Missing information:無
  - Human decision:已寫
  - Authority:參與 Demo 的人
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:B1 已熄
  - Recovery:若改成 REVISE → 回 Stage 3
  - Audit/handoff requirement:attestation 行保留
  - Observation:見本條觀測

#### S-2.5 否定跳過句不得當 skip OC
- GIVEN `2-decision.md` 內部技術選擇寫「不預先跳過 Stage 3…（本檔無「跳過 Stage 3」流程層 OC）」
- WHEN 跑 `python3 hooks/_stage3_impl.py five-station-simplify`
- THEN 語意應 REJECT（否定「跳過」≠ Owner Call 跳過）；2026-09-14 實跑曾誤 `g2_demo=PASS`／`trigger_source=owner-call`。本 hop 不改該腳本；F1 必須收緊謂詞：同時出現「Stage 3」與「跳過」時，若句中有「不／無／不得」則不得當 skip
- 觀測:從 3-prototype 盤 4 原始輸出摘要看 | 現況牙誤 PASS 已記帳；F1 收緊後同一句不得再 PASS 算本條落地 | 用盤 4 那段 stdout 當負向對照
- Operational Context:
  - Actor:G2 reviewer／F1 寫牙的人
  - Goal:否定句不能冒充已跳 Demo
  - Situation:現行牙誤匹配
  - Known information:句子意思是不准跳
  - Missing information:F1 腳本何時落地
  - Human decision:本 hop 不修牙；F1 改謂詞
  - Authority:F1 annex
  - External dependency:現有 `_stage3_impl.py`
  - Out-of-system action:跑該指令看 stdout
  - Waiting/timeout behavior:檢查同步結束
  - Recovery:F1 加否定詞掃描
  - Audit/handoff requirement:stdout JSON `stage3-verdict-v1` 留檔
  - Observation:見本條觀測

### R-3: 系統 SHALL 凍結已有站檔走舊七站
4A／SC-5／SC-8／RP-15／AC-5／AC-8／OC-5。偵測=`docs/dev/<slug>/` 已有 1–7 任一 `.md`。僅 html 不算開工。本目錄已有 `1-discussion.md` = 第一個 live freeze 樣本。F3 cut 不得把 in-flight 折五站。

**審的時候看什麼**
只認 md。對本目錄要求五站自動前進、跳過例行 G1／G2 → 必須跳不過。本 PR `status-diff` 必須不含 `STATUS.md`。

#### S-3.1 本 slug 五站 hop 跳不過
- GIVEN `docs/dev/five-station-simplify/1-discussion.md` 存在（亦已有 `2-decision.md`／`3-prototype.md`）
- WHEN 任何程序把本 slug 寫入五站狀態，或要求自動前進跳過例行 G1／G2
- THEN `in_flight=True`；整段舊 7 到自己的 Ship（仍有例行 G1／條件 S3／G2／G3）；寫入五站狀態 → 紅（RP-15）；`Gates` 現況字面含 `G1✅ G2⬜ G3⬜`；本 PR 檔集不含 `docs/dev/STATUS.md`
- 觀測:從本目錄 `ls docs/dev/five-station-simplify/*.md` 與 `docs/dev/STATUS.md` Active 列看 | 至少三份 md 存在、Gates 含 `G2⬜`、`git diff --name-only origin/main` 不含 STATUS.md 算本 hop 過 | 用本 tree 現檔測
- Operational Context:
  - Actor:in-flight slug 執行者／coordinator
  - Goal:走完手上舊 7，不被中途改線
  - Situation:本資料夾已開工
  - Known information:任一 1–7 md = 凍
  - Missing information:無
  - Human decision:本 slug 自己的 G2／G3 仍等人
  - Authority:4A／OC-5
  - External dependency:無
  - Out-of-system action:不把本 slug 當新 5 白老鼠
  - Waiting/timeout behavior:本 slug 仍例行等 G2／G3
  - Recovery:誤寫五站狀態 → 刪該寫入，回舊 graph
  - Audit/handoff requirement:目錄裡的 md 即恢復錨
  - Observation:見本條觀測

#### S-3.2 F3 cut 已有 md 的 slug 仍舊 7
- GIVEN F3 cut 當下某 slug 的 `docs/dev/<slug>/` 已有 `1-discussion.md`…`7-review.md` 任一檔
- WHEN 路線被求切成五站預設
- THEN 該 slug 仍走舊 7（仍有例行 G1／條件 S3／G2／G3）直到自己的 Ship；F0–F2 期間母版新開改版軌同樣舊 7
- 觀測:從 brief §6 與 Decision 4A 對照 | 「已有任一站檔 → 整段舊 7」字面在兩檔算過 | 用 brief L160-L167 + 2-decision 4A 測
- Operational Context:
  - Actor:採用專案 owner／母版維護者
  - Goal:進行中 feat 不中途改 hop
  - Situation:F3 cut
  - Known information:偵測只認 md
  - Missing information:無
  - Human decision:不折 in-flight
  - Authority:OC-9／X4
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:舊 7 仍例行等中閘
  - Recovery:誤折 → 回舊 graph，計違 X4
  - Audit/handoff requirement:不得寫入五站狀態
  - Observation:見本條觀測

#### S-3.3 裸 html 不凍
- GIVEN 某目錄只有 `1-discussion.html`／`2-decision.html`，沒有任何 1–7 `.md`
- WHEN 評 `in_flight`
- THEN `in_flight=False`；不因產檔器誤生 html 而凍結
- 觀測:從 Decision OC-5 對照 | 只認 md、裸 html 不算開工算過 | 用 OC-5 原文測
- Operational Context:不適用 — 偵測規則對帳，無人員交接。

#### S-3.4 舊檔缺新五站欄不紅
- GIVEN 契約已是 2.1.0 dual-read；某舊 7 slug 的站檔缺新 5 欄（別名／自動前進欄）
- WHEN 2.1.0 讀檔器解析該 slug
- THEN 不得因缺新欄一次變紅（SC-5 第 2 句／OC-1 第 2 句）；能解析兩套 ≠ 已切五站
- 觀測: n-a:2.1.0 annex 本 hop 不落地。替代：從 Decision OC-1／SC-5／SC-9 對照 | 「舊檔缺新欄不紅」與「能解析 ≠ 已切」兩句都在算過 | 用 2-decision OC-1 與 SC-5 測
- Operational Context:
  - Actor:採用專案 owner
  - Goal:舊 slug 不被誤殺
  - Situation:尚未改欄
  - Known information:dual-read 誠實第 2 句
  - Missing information:annex 鍵名（OC-3 不鎖）
  - Human decision:不把「不紅」讀成「可以默默切五站」
  - Authority:2A
  - External dependency:未來 2.1.0 讀檔器
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:若被做成缺欄就紅 → 違 2A，回 Stage 2
  - Audit/handoff requirement:讀檔結果可分「合法缺省」與「已切」
  - Observation:見本條觀測

#### S-3.5 舊七站不套 rewrite 三 cap
- GIVEN slug 的 `in_flight=True` 或路線=舊 7
- WHEN 該 slug 重寫同一 hop 第 3 次，或 Decide 重開，或 Goal 重開
- THEN 不套 hop≤2／Decide≤1／Goal reopen≤1；改走既有 T 嘗試上限 4 與既有修迴圈
- 觀測:從狀態機 §3 補充與 brief §4 對照 | 「舊 7 不套這三 cap」字面在算過 | 用狀態機 L139 + brief L131 測
- Operational Context:不適用 — cap 適用範圍對帳。

### R-4: 系統 SHALL 拒絕把握手綠解釋成已切五站
3A／SC-9／SC-10／OC-1／OC-2。doctor 綠只證明契約版本 ∈ `supported_contract_versions`。marketplace 單一 `source: ./` 可換整包 hops。兩件事可同時成立。F1 最少拒收：契約仍 2.0.0 且 hops 已是五站預設 → 紅／不得改線。

**審的時候看什麼**
三格 AND 才准說「路線」：契約版本、hops 預設、freeze md。`COMPATIBLE`／exit 0 單獨不得解釋成已切，也不得解釋成路線沒變。

#### S-4.1 對照稿不得說已切五站
- GIVEN `devflow_contract_version=2.0.0` 且 marketplace 已更新使 hops 預設五站 且 `hooks/devflow-doctor.sh` exit 0
- WHEN 文案、謂詞或 STATUS 註解把「doctor 綠」寫成「已切五站」或「可以跟 hops 走」
- THEN 該文案／謂詞紅（SC-10）；採用端仍必須走舊 7；未 upgrade 不得遠端改線
- 觀測:從 3-prototype 盤 5 現檔表與 Decision SC-10 對照 | 契約 2.0.0 + doctor COMPATIBLE + marketplace `source: ./` 三格同時成立，且正文禁止「綠=已切」算過 | 用盤 5 表 + `hooks/devflow-doctor.sh` 現跑測
- Operational Context:
  - Actor:採用專案 owner
  - Goal:拒絕被遠端改線
  - Situation:marketplace update 後 doctor 仍綠
  - Known information:握手不讀 hops
  - Missing information:採用端是否已宣告 2.1.0
  - Human decision:未 2.1.0 則拒絕跟 hops 走
  - Authority:OC-1 第 3 句
  - External dependency:`marketplace update`
  - Out-of-system action:更新後核契約版本
  - Waiting/timeout behavior:無
  - Recovery:把「已切」文案改成「僅握手」
  - Audit/handoff requirement:三格 AND 才准說路線
  - Observation:見本條觀測

#### S-4.2 doctor 只握手版本
- GIVEN `hooks/_doctor_impl.py` L193–L202 只比對契約版本 ∈ supported
- WHEN 對 tip 跑 `hooks/devflow-doctor.sh` 並 `rg` 該實作
- THEN exit 0 且輸出含 `COMPATIBLE` 或 `2.0.0 ∈ supported`；源碼不含 `hops`／`graph.yaml`／`marketplace`／`Intake` 作為握手條件
- 觀測:從該腳本 exit 與 `_doctor_impl.py` 原文看 | exit 0 且握手不讀 hops 算過 | 用 2026-09-14 盤 5 同形指令測
- Operational Context:不適用 — 現檔源碼與 CLI 輸出，無人員交接。

#### S-4.3 F1 牙必須紅二點零加五站 hops
- GIVEN F1 annex 已落地（本 hop 不寫）
- WHEN 對照「契約仍 2.0.0 且 hops 已是五站預設」
- THEN 指定牙 exit ≠ 0 或同等拒絕；annex 可加謂詞，不可刪本條
- 觀測: n-a:F1 牙本 hop 不落地。替代：從 Decision OC-2／SC-10／RP 表外的採用端拒收句對照 | 「2.0.0 + 五站 hops → 紅／不得改線」字面在 Decision 算過 | 用 2-decision OC-2 與 SC-10 測
- Operational Context:
  - Actor:F1 寫牙的人
  - Goal:陷阱可被機械紅
  - Situation:本 hop 只鎖謂詞
  - Known information:牙只准 `scripts/` 與 annex
  - Missing information:腳本名（OC-3）
  - Human decision:F1 才選腳本
  - Authority:OC-2
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:本 hop 不等牙
  - Recovery:本 PR 出現 `scripts/` 新牙 → 違 7A
  - Audit/handoff requirement:本 hop `git diff` 不含 `scripts/` 新檔
  - Observation:見本條觀測

#### S-4.4 未宣告二點一不得遠端改線
- GIVEN 採用端未宣告契約 2.1.0 dual-read
- WHEN marketplace 已把方法包 hops 換成五站預設
- THEN 採用端執行面仍必須舊 7；不得因 hops 檔已換就走五站自動前進
- 觀測:從 Decision OC-1 第 3 句與 Constraints「採用 hop 身分」對照 | 未 upgrade = 舊 7 算過 | 用 2-decision L108／L136 測
- Operational Context:
  - Actor:採用專案 owner
  - Goal:自己決定何時 upgrade
  - Situation:遠端 pack 已換
  - Known information:graph／hooks 住方法包
  - Missing information:無
  - Human decision:upgrade 到 2.1.0 之前拒絕新路線
  - Authority:採用端 owner
  - External dependency:marketplace
  - Out-of-system action:`plugin update` 後仍核契約
  - Waiting/timeout behavior:無
  - Recovery:被改線 → 回舊 7 graph
  - Audit/handoff requirement:契約版本欄可核對
  - Observation:見本條觀測

#### S-4.5 能解析兩套不是已切
- GIVEN 2.1.0 讀檔器能解析舊 7 與新 5
- WHEN 有人把「能 dual-read」或「doctor 綠」說成採用端已切五站
- THEN 該解釋紅（SC-9）；誠實三句必須同時成立
- 觀測:從 Decision OC-1 三句對照 | 缺第 3 句的「誠實」不得當已核算過 | 用 OC-1 原文測
- Operational Context:不適用 — 與 S-4.1 同一解釋禁令。

### R-5: 系統 SHALL 為 Must-keep 留下去向並鎖四欄 seam
6A／SC-2／SC-3／SC-7／SC-13／OC-10／OC-11／AC-2／AC-3／AC-7。少任一 M = 違 brief，不能寫成「已經五站了所以可省」。人見面時機選定 **T 卡上就紅**（Stage 3 ACCEPTED）。

**審的時候看什麼**
本檔 M1–M16 表是否每條都有去向。T-fake（缺四欄、`Verify: 看起來沒問題`、無 RED、reviewer=implementer）即使勾選仍未完成。本 slug 後站若把四欄／seam／M1／M3／M11 標成可選 → 擋本 slug G2。

#### S-5.1 M1 到 M16 每條都有去向
- GIVEN 本檔「Must-keep Disposition」表
- WHEN 對照 brief §5 的 M1–M16
- THEN 16 列皆在；每列去向 ∈ {本方案處理, 刻意維持}；本方案處理列的下落匹配 `S-` 或本檔具名節；M15／M16 不得寫成 Non-Goal
- 觀測:從本檔 Must-keep Disposition 表數列看 | 16 列齊、M15／M16 非 Non-Goal 算過 | 用本檔該表 + brief L135-L158 測
- Operational Context:不適用 — 去向帳對照，無現場交接。

#### S-5.2 假完成 T 在卡上就紅
- GIVEN 一份 T 卡：Covers／Files／Verify／Blocked-by 任一空，或 Verify 字面為「看起來沒問題」，或無 RED 輸出，或 reviewer=implementer，且 checkbox 已勾，註「已經五站了，四欄／seam 可選」
- WHEN 人只看該 T 卡（A8）或 F1 牙評該 T
- THEN 該 T 不得標完成（RP-1／RP-2／SC-3）；紅必須出現在**寫卡當下**，不得拖到 hop 板或 Ship 才出現；勾選 ≠ 完成
- 觀測:從 3-prototype 盤 3 壞卡 T-fake 與 Decision SC-3 對照 | T-fake 未完成、時機=T 卡上就紅算過 | 用盤 3 T-fake + 人見面時機表測
- Operational Context:
  - Actor:獨立 T reviewer
  - Goal:擋假綠 T
  - Situation:寫手用五站當省略理由
  - Known information:四欄必填；seam 要 RED 與他人審
  - Missing information:無
  - Human decision:拒自審、退回補欄
  - Authority:reviewer ≠ implementer
  - External dependency:另一 session
  - Out-of-system action:不把 chat「看起來可以」當 Verify
  - Waiting/timeout behavior:T 未完成則 Build 不得 hop
  - Recovery:補四欄、貼 RED 輸出、換 reviewer
  - Audit/handoff requirement:6-notes 留 RED 與 reviewer 名
  - Observation:見本條觀測

#### S-5.3 S 含未定事項三詞或模糊詞必須紅
- GIVEN 一份 S 正文含模板反模糊第 2 條的未定事項三詞，或含第 1 條模糊詞清單中的任一字，或標不可測
- WHEN 跑 `scripts/check-spec-gate.sh` 或 F1 對 S 的牙（RP-3）
- THEN 該 S 紅；不得當完成
- 觀測:從本檔自身跑 `scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md` 看 | 本檔 C4 必須 exit 0；對照稿 S-fuzzy 必須被點名紅算過 | 用本檔（正向）+ 盤 3 壞卡 S-fuzzy（負向對照）測
- Operational Context:不適用 — 形狀牙，無現場交接。

#### S-5.4 測試名不含 S-id 必須紅
- GIVEN 一條測試函式名不含它所蓋 S 的 id（例如蓋 S-1.1 卻叫 `test_happy_path`）
- WHEN F1 牙或 coverage 對帳
- THEN 紅（RP-4／M1）
- 觀測: n-a:本 hop 無測試碼。替代：從 Decision RP-4 與本檔 Test Skeletons 命名看 | 每個 stub 名含 `s_` + 對應 S 號算本 hop 形狀過 | 用本檔 Test Skeletons 節測
- Operational Context:不適用 — 命名契約。

#### S-5.5 標可選則擋本 slug G2
- GIVEN 本 slug 的 `4-spec.md` 或未來 `5-tasks.md` 把 M1／M3／M11 或 T 四欄／seam 寫成「可選」或「已五站故可省」
- WHEN 評本 slug G2
- THEN 不得過（OC-11）；該寫法=違 6A
- 觀測:從本檔全文 `rg` 「可選四欄」「可選 seam」「已五站故省」看 | 本檔不得把四欄／seam／M1／M3／M11 標可選算過 | 用本檔 `rg` 測
- Operational Context:
  - Actor:本 slug G2 reviewer
  - Goal:後站不能掏空
  - Situation:有人想簡化欄位
  - Known information:OC-11
  - Missing information:無
  - Human decision:打回重寫
  - Authority:擋 G2
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:G2 不過
  - Recovery:改回 Owner-locked
  - Audit/handoff requirement:OC-11 原文
  - Observation:見本條觀測

#### S-5.6 四欄與 seam 是未來 T 約束
- GIVEN Stage 5 將寫 `5-tasks.md`（本 hop 不寫）
- WHEN 任一 T 落檔
- THEN 該 T 必須有非空 Covers／Files／Verify／Blocked-by；6-notes 該 T 必須有 RED 輸出與不同於實作者的 reviewer；本檔 R-5 即這條約束的引用錨，不另發明欄名
- 觀測:從 `_templates/5-tasks.md` L50 與 `_templates/6-implementation-notes.md` L104-L137 看 | 現行模板已要求四欄與 seam；本檔把它標不可選算過 | 用那兩段原文測
- Operational Context:
  - Actor:Build 實作者／獨立 T reviewer
  - Goal:checkbox 不能冒充完成
  - Situation:未來切 T
  - Known information:Owner-locked
  - Missing information:具體 Files 清單（Stage 5 才填）
  - Human decision:缺欄就不勾
  - Authority:5-tasks 模板 + 本 R
  - External dependency:無
  - Out-of-system action:跑測試留原始輸出
  - Waiting/timeout behavior:T 未完成則不得 hop 出 Build
  - Recovery:補欄後重評
  - Audit/handoff requirement:四欄在 T 卡上可見
  - Observation:見本條觀測

#### S-5.7 少一條 M 不得稱簡化成功
- GIVEN 一份規格／任務／牙輸出宣稱「五站已簡化」但 M1–M16 少任一項
- WHEN 對照 brief §5
- THEN 該宣稱被點名違 brief（SC-2）；不得寫成簡化成功
- 觀測:從 Decision SC-2 與本檔 S-5.1 表對照 | 少項必須被點名算過 | 用故意拿掉 Verify 的 T-fake 當少 M11 對照
- Operational Context:不適用 — 宣稱對帳。

#### S-5.8 本 hop 必須重生審頁 html
- GIVEN 本 hop 改了 `4-spec.md`
- WHEN 跑 `scripts/build-stage4-html.py --action docs/dev/five-station-simplify/4-spec.md`
- THEN 同目錄寫出 `4-spec.html`；不得只丟 raw md 送審（M13）
- 觀測:從該 html 是否存在且含本檔 R-id 看 | 檔在且含 `R-1`…`R-6` 算過 | 用產檔器輸出測
- Operational Context:不適用 — 產檔器，無現場交接。

### R-6: 系統 SHALL 維持拒收集只准加並紅超限 rewrite
OC-10／SC-13／RP-8…RP-11／狀態機 §6。RP-1…RP-16 是 F1 牙最小集：annex 只准加、不准減。本 hop `git diff` 不含 `scripts/` 新牙（7A／M16）。

**審的時候看什麼**
annex 刪 RP 任一列 = 翻 Decision。Ship 無人 PASS 卻標 Done → 紅。hop／Decide／Goal 超限仍繼續 → 紅。本 PR 檔集只准本目錄 `4-spec.md` 與 `4-spec.html`。

#### S-6.1 annex 不准減 RP 列
- GIVEN Decision「本方案要求」RP-1…RP-16
- WHEN F1 annex 或後站規格刪其中任一列，或把該列標可選
- THEN 視為翻 Decision，回 Stage 2；SC-13 失敗
- 觀測:從 2-decision L119-L137 數 RP 列看 | 16 列都在；本檔未把任一 RP 標可選算過 | 用 2-decision 該表測
- Operational Context:不適用 — 最小集對帳。

#### S-6.2 rewrite 超限必須紅
- GIVEN 五站路線 slug（非舊 7）同一 hop 重寫計數將到 3，或 Decide 已重開 1 次再進 Decide，或離開 Intake 後 Goal 已重開 1 次再重開
- WHEN 程序仍繼續 hop
- THEN 紅（RP-9／RP-10／RP-11）；進 `Escalated`；不得暗改 cap 數字
- 觀測: n-a:coordinator／計數器本 hop 不落地。替代：從狀態機 §3／§6.2–§6.4 與 Decision RP-9…11 對照 | 數字 hop≤2／Decide≤1／Goal reopen≤1 與「用盡 Escalated」字面在算過 | 用狀態機 L122-L139 + RP-9…11 測
- Operational Context:
  - Actor:coordinator／owner
  - Goal:重寫有上限
  - Situation:同一 hop 被要求再寫
  - Known information:三 cap 已鎖
  - Missing information:計數落點（F2）
  - Human decision:用盡後明示下一手
  - Authority:人處理 Escalated
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:Escalated 等人
  - Recovery:不得 reset 計數再 hop（X5）
  - Audit/handoff requirement:F2 才接 event；F0 只鎖要留紀錄
  - Observation:見本條觀測

#### S-6.3 無人 PASS 不得標 Done
- GIVEN `7-review.md` 機械全綠，頂欄無人類 `verdict: PASS`
- WHEN 任何程序把該 slug 標 Done 或把 STATUS Gates 寫成 `G3✅`
- THEN 紅（RP-8）；保持 S-1.3
- 觀測:從狀態機 §6.1 與 Decision RP-8 對照 | 無人 PASS 卻 Done 必須紅算過 | 用 RP-8 + §6.1 測
- Operational Context:不適用 — 與 S-1.3 同一人主權。

#### S-6.4 本 PR 檔集只准規格與審頁
- GIVEN 本 hop 工作樹相對 `origin/main`
- WHEN 列 `git diff --name-only origin/main`
- THEN 只含 `docs/dev/five-station-simplify/4-spec.md` 與 `docs/dev/five-station-simplify/4-spec.html`；不含 `_templates/`、`graph.yaml`、`scripts/` 新牙、`STATUS.md`、`HISTORY.md`、`devflow-contract.json`
- 觀測:從該 `git diff --name-only` 看 | 檔名集合恰為上述兩檔算過 | 用本 PR 工作樹測
- Operational Context:不適用 — 檔集對帳（M16／7A）。

## MODIFIED Requirements

無。本 hop 不改 living 正本（`_templates/`、各站 `graph.yaml`、gate token、`devflow-contract.json`、doctor 握手）。F1 起才改 `scripts/`／annex；F3 才切新 slug 預設路線。

## REMOVED Requirements

無。不刪 G1／G2／`ACCEPTED` token 或檔。不刪 Fast。不刪七檔名家族。

## 行為流程圖(R 級)

```
[R-1] 依表分開產頁與 latch
  產頁不是等人
  latch 真才停
  旗標對 Gates
[R-2] 拒絕空欄 attestation
  chat 不是判定
  代寫視為未寫
[R-3] 凍結已有站檔
  只認 md
  五站 hop 跳不過
[R-4] 拒絕把握手綠解釋成已切
  三格 AND 才准說路線
  二點零加五站 hops 要紅
[R-5] 留下去向並鎖四欄 seam
  T 卡上就紅
  少一條 M 違 brief
[R-6] 拒收集只准加
  超限 rewrite 紅
  本 PR 只兩檔
```

## Acceptance Criteria

- 本 hop：`scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md` exit 0；`4-spec.html` 由 `scripts/build-stage4-html.py --action` 重生；S-5.1 十六列齊；S-6.4 檔集恰兩檔。
- 後續 F1：S-2.1／S-2.2／S-4.3／S-5.2／S-6.1／S-6.2 對指定牙綠；本 hop 不要求牙已存在。
- 回歸：既有 `scripts/check-gate-tokens.sh` 仍能解析 G1／G2／G3；本 hop 不改那支腳本。
- 非功能：本 hop 無效能契約。相容=舊 7 in-flight 不被本 PR 改線。
- 本檔頂欄 `verdict:` 留空直到人類 G2；全 S 卡勾選 ≠ PASS。

## Out of Scope

- 本 PR 實作 F1 牙／annex／doctor 路線欄；本 PR 寫 coordinator（F2）；本 PR 切預設路線（F3）。
- 改 `_templates/`、`graph.yaml`、gate token、`scripts/` 正本、`STATUS.md`、`HISTORY.md`、契約版本。
- 發明 G2 PASS、合併、開 `5-tasks.md`。
- 刪 G1／G2／`ACCEPTED`；改七檔名；廢 Fast；第二條 ID 鏈。
- 拿本 slug 當新 5 白老鼠（4C 已拒）。
- 把 Q6 升成已核事實。
- 選定 dual-read 欄位名或 coordinator event schema（OC-3）。
- 建採用現場回報口；把採用路徑寫進 public issue。
- 讀 A／C 線 Stage 4 並與其對齊（本檔獨立）。
- 重開 F0 十條。

### Stage 3 對帳

`3-prototype.md` `status: approved`；`Human verdict: ACCEPTED | role=母版 owner | scenario=AC-1`；`Verdict attestation: human:rick @ 2026-09-14`（#309）。D1 選定；人見面時機選定 T 卡上就紅。2-decision 擬回寫列本 hop 仍不動該檔；1A–7A 不重開。本檔承接 Demo 場景，不發明新互動。

- 3-prototype「Scenario AC-1」→ S-1.1、S-1.2、S-1.8
- 3-prototype「Scenario AC-6」→ S-1.1、S-1.2、S-1.3、S-1.4、S-1.5、S-1.6、S-1.7、S-1.10
- 3-prototype「Scenario AC-3」→ S-5.2、S-5.3、S-5.5、S-5.6、S-5.7
- 3-prototype「Scenario AC-4」→ S-2.1、S-2.2、S-2.4
- 3-prototype「Scenario AC-8」→ S-3.1
- 3-prototype「Scenario AC-5」→ S-3.2、S-3.4
- 3-prototype「Scenario SC-9」→ S-4.1、S-4.2、S-4.5
- 3-prototype「Scenario RP-14」→ S-2.5
- Method 盤 2 表 A／B → R-1
- Method 盤 3 T-fake／T 卡上就紅 → S-5.2
- Method 盤 4 空 attestation → S-2.1、S-2.2
- Method 盤 5 freeze×doctor → S-3.1、S-4.1、S-4.2
- Operational Context Recovery（停修、人補 attestation、回舊 graph、F1 收緊 skip）→ 各對應 S 的 Recovery 欄
- 棄：hop 板／Ship 重建（晚發現）→ Out of Scope，不另開 R

## Diff Budget

本節是**估計**。本規格 PR 本身只動兩檔。下表給後續 F1–F3，不是本 PR 承諾。

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| 本 hop `4-spec.md` + 產器 html | 2 | ≤900 | 0 |
| F1 `scripts/`／annex 拒收牙 + fixture | ≤8 | ≤400 | ≤600 |
| F2 coordinator + event 計數 | ≤10 | ≤800 | ≤500 |
| F3 新 slug 預設路線（不動 freeze slug） | ≤6 | ≤300 | ≤200 |
| **合計（後續，非本 PR）** | **≤26** | **≤2400** | **≤1300** |

[Assumption] 係數按「一個 S 一到兩條測試」，未加 mutation。本 PR 檔數=2；超支訊號看後續刀，不看本 hop。

## Dependencies

- `docs/dev/five-station-simplify/2-decision.md` —— justification:G1 已核方向；本檔不翻 1A–7A。
- `docs/dev/five-station-simplify/3-prototype.md` —— justification:Human ACCEPTED + attestation；Demo 場景對帳。
- `notes/design/five-station-simplify-brief-v3.md` —— justification:表 A／B 與 Must-keep 正本。
- `notes/design/five-station-simplify-f0-state-machine.md` —— justification:latch／cap／禁則。
- `hooks/_stage3_impl.py` —— justification:S-2.5 負向對照；本 hop 不改。
- `hooks/devflow-doctor.sh`／`hooks/_doctor_impl.py` —— justification:S-4.2 現檔握手。
- `.claude-plugin/marketplace.json` —— justification:S-4.1 單一 `source: ./`。
- `scripts/check-spec-gate.sh` —— justification:本 hop 形狀 Gate。
- `scripts/build-stage4-html.py` —— justification:M13 審頁。
- F1 annex／`scripts/` 牙 —— justification:S-4.3／S-6.1 落地；**本 hop 不新增此依賴的檔**。
- F2 coordinator —— justification:自動前進 runtime；本 hop 不寫。
- 無新外部服務、無新套件、無 migration。

## Design Boundary Contract(G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（graph／doctor／marketplace／STATUS／未來 coordinator）；⑦Idempotency／計數（rewrite cap）；⑨Feature Risk = high；⑪狀態機與 HumanWait／Escalated 恢復
- Design source: 既有 pattern —— brief §3 表 A／B、狀態機、Decision 1A–7A；本檔只把已核謂詞寫成 S，不新發明產品行為

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| 表 A／B 謂詞（brief §3） | 產頁與 latch 的唯一正本 | owner 擁有 brief | → 狀態機 latch 指標 | 不得另寫第二張頁表 |
| in-flight 偵測 | 認 1–7 `.md` | slug 目錄擁有站檔 | → `docs/dev/<slug>/` | 不得只認 html |
| doctor 握手 | 契約版本 ∈ supported | 契約檔擁有版本 | → `devflow-contract.json` | 不得讀 hops 當已切證據 |
| F1 牙（未來） | 紅 RP-1…16 與 2.0.0+五站 hops | annex 擁有加項 | → `scripts/` | 不得改 Stage 1–4 模板；本 hop 零碼 |
| 本 slug 舊 7 | 自己的 G1／G2／G3 | 本目錄 md | → 既有 graph | 不得套五站機 |
| STATUS 寫入口 | Active 列 Gates | 整合分支 | → `status-update.sh` | feature branch 禁改表列 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| coordinator 評 hop（F2） | in:slug 檔與表 A／B；out:hop／停修／HumanWait | 謂詞假→停修；latch 未開卻問人→紅 | 不寫判定 | 舊 7 不進本機 |
| B1 attestation | in:Human verdict + attestation 行；out:准／拒 hop | 空欄或 Agent 代寫→視為未寫 | 人寫一行，機只讀字面 | 既有機械拒保持 |
| doctor CLI | in:專案契約版本；out:COMPATIBLE／exit | 版本 ∉ supported → fail-closed | 只讀 | 不把 exit 0 當路線 |
| F3 cut | in:目錄是否有 md；out:舊 7 或新 5 | 寫入五站狀態到 in-flight → 紅 | 切線不改已有 md 內容 | 雙路線並存到 in-flight Ship |
| 本 hop 檔集 | in:git diff；out:兩檔 | 多檔→S-6.4 失敗 | 單一 PR | 不 bump 契約 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 本檔 R／S | 把已核謂詞寫成可測契約 | ← Decision／brief／狀態機／Demo | md → G2 人審 | 模糊詞／缺觀測 → spec-gate 紅 | `check-spec-gate.sh` |
| 審頁產器 | 從 md 吐 R／S 卡 + 生命週期 + 行為圖 | ← 本檔 | md → html | 缺 GWT 紅底 | S-5.8 |
| 未來 F1 牙 | 紅 RP 與採用端陷阱 | ← annex、← 現有 scripts 家族 | fixture → exit | 減 RP 列=翻 Decision | S-4.3、S-6.1 |
| 未來 coordinator | 評謂詞、進 HumanWait | ← 表 A／B | 狀態機 | cap 用盡 Escalated | S-1.*、S-6.2 |

### Design Constraints
- 必須:表 A／B 為 latch 正本；in-flight 只認 md；chat 不是判定；M1–M16 每條有去向；T 四欄＋seam 不可選；RP 最小集只准加；本 slug 舊 7；本 PR 只兩檔。
- 禁止:本 hop 改模板／graph／牙／STATUS；本 hop 發明 G2 PASS；刪 token；把 doctor 綠當已切；把本 slug 當新 5；減 RP；標可選四欄。
- Extension point:annex 鍵名、牙腳本名、event schema 留給本 slug F1／F2，不在本檔鎖。
- Known design limit:
  ① Q6 採用現場是否 chat 蓋章仍是 Assumption；不得當已核（OC-8）。
  ② F1 牙與 coordinator 本 hop 不存在；相關 S 用 Decision／現檔替代觀測。
  ③ `_stage3_impl.py` 會把否定「跳過」讀成 skip（S-2.5）；本 hop 不修。
  ④ 審頁產器行為圖硬切 8 框；本檔 6 個 R，不改產器。
  ⑤ A1／A2 是否分檔仍待 F1 annex。

## Verification Profile(G2 一併審)
- lane: full（判準:新能力、改等待／核准語意、高風險人機互動、狀態機、不可逆 F3 cut。owner 指示=full。判準=full。**無偏離**）
- Risk: high（判準:誰准寫判定=權限語意；F3 cut=不可逆路線；舊 7／新 5 並存=併發；契約 dual-read=公開契約面）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得在 A4／A7 latch=否時留下「請人審」（S-1.7）
  - 不得把 chat 准開當 attestation（S-2.1）
  - 不得把 Agent 代寫當成已寫（S-2.2）
  - 不得對本 slug 五站自動前進跳 G1／G2（S-3.1）
  - 不得把 doctor 綠寫成已切五站（S-4.1）
  - 不得把 T 四欄／seam／M1／M3／M11 標可選（S-5.5）
  - 不得減 RP-1…RP-16（S-6.1）
  - 不得本 hop 改 STATUS／模板／graph／scripts 牙／契約
  - 不得發明 G2 PASS
- Required layers:check-spec-gate（本 hop 形狀）；本 hop 無產品碼層。可寫「形狀一層」
- Conditional layers:Supply chain — 當 F1 改 `scripts/` 或 annex 時必跑對應牙 + S-4.2 doctor 現檔；當 F3 切線時必跑 S-3.1／S-3.2
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Race／stress（狀態機尚未 runtime）、Windows 真機（Out of Scope）
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md`
- Reliability triage:
  - Concurrency: applicable — 舊 7 in-flight 與 F3 後新 5 並存；落到 S-3.1、S-3.2、Failure Model「誤折 in-flight」
  - Idempotency: applicable — rewrite cap 只增不減；同一 doctor 輸入再跑仍 exit 0＋握手句（S-4.2、S-6.2）
  - Timeout/retry: applicable — HumanWait／Escalated 無人寫則不停成 Done；檢查同步結束、人修後重跑（S-1.3、S-1.5、S-6.2）

Demo verdict 條件:有 Stage 3 trigger（6 條）且人類 ACCEPTED + attestation（#309）。本檔不代填 G2 `verdict:`。

### Failure Model(Risk: high 必填)
| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| A4／A7 被當例行停 | 等人次數仍綁站數 | 前進紀錄出現「請人審 A4／A7」 | Required:S-1.1、S-1.2、S-1.7 | F2 前用對照稿 |
| 空欄被 chat 帶走 | dogfood 捷徑寫進新機 | hop 出 Spec 而 attestation 空 | Required:S-2.1 | — |
| Agent 代寫 PASS | 機器出貨 | 無 human: 行仍 Done | Required:S-2.2、S-6.3 | — |
| 本 slug 被折五站 | 觀測被自己污染 | 本目錄寫入五站狀態 | Required:S-3.1 | — |
| 裸 html 誤凍 | 空目錄被當開工 | 只 html 卻 in_flight | Required:S-3.3 | — |
| doctor 綠冒充已切 | 採用端被遠端改線 | 文案寫「綠=五站」 | Required:S-4.1、S-4.5 | F1 牙落地前用 Decision 句 |
| 假完成 T | checkbox 綠、工作沒做 | T-fake 被標完成 | Required:S-5.2 | — |
| 後站標可選 | Must-keep 被掏空 | 4-spec 寫「四欄可選」 | Required:S-5.5 | — |
| annex 減 RP | 拒收集被掏空 | RP 列少於 16 | Required:S-6.1 | — |
| cap 被暗改 | 重寫無限 | 用盡仍 hop | Required:S-6.2 | F2 前無計數 runtime |
| 否定跳過句誤 PASS | 未 Demo 當已過 | `_stage3_impl.py` g2_demo=PASS | Required:S-2.5 | 本 hop 不修現牙（limit ③） |
| Q6 被升格 | 假現場證據 | 正文寫「採用現場已核蓋章」 | Required:Assumption refs | 無採用逐字稿 |

## Assumption refs

Q6 殘餘風險由 OC-8 接受（不擋本 G1；仍禁止升成已核）。A1／A2 分檔交 F1 annex。

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q6 採用現場仍 chat 蓋章過 G1／G2 | stage-2 | oc-accepted |
| 後站會用「已經五站了」省略 M11／M3／M1 | stage-2 | resolved |
| A1／A2 共寫 1-discussion.html | 2026-12-31 | open |

## Drafting Decisions(草擬自判,待人審)

上層各條**不改** Decision 已核的可見行為；只鎖定本檔怎麼寫成 S。狀態不是「待人審未裁」，是草擬自判（G2 人仍可推翻）。

### 逐條裁決(上層)
| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | STATUS 旗標的可測定義 = Active 列 Gates 字面 + `Demo-B1` 行 + `in_flight` md 偵測 + 本 PR 不含 STATUS.md。不新造 STATUS 欄位 | B 線要「latch 開火 vs 不開」看得到旗標；feature branch 禁改 STATUS 表列 | `docs/dev/STATUS.md` L10-L26；2-decision OC-4 | 改成另造 sidecar 旗標則 S-1.* 觀測全改 | ✅ 草擬自判 |
| DD-2 | F1 牙在本檔寫成可拒收 S，本 PR 不落地腳本。觀測雙層：n-a:牙未落地 + Decision／現檔替代 | 7A／OC-7；模板要求觀測在本 repo 可執行 | 2-decision 7A；`_templates/4-spec.md` 觀測頂註 | 本 PR 出現 scripts 新牙 = 違 7A | ✅ 草擬自判 |
| DD-3 | T 四欄＋seam 在本檔標「未來 T 約束」，不在本 hop 寫 5-tasks 或新欄名 | 6A Owner-locked；Stage 5 才切 T | 1-discussion L185；2-decision L112 | 本 hop 開 5-tasks = 超 scope | ✅ 草擬自判 |
| DD-4 | Q6 進 Assumption refs 為 oc-accepted；正文禁止寫成已核採用現場蓋章 | OC-8；C7 過期 open 會擋形狀 | 2-decision OC-8；1-discussion L174 | 升成已核 = SC-12 失敗 | ✅ 草擬自判 |
| DD-5 | 表 A 其餘列（A1／A2／A3／A6／A8／A9）收成 S-1.9，不各開 R | 避免單份 S 數爆；行為詞仍在 R-1 | `[Assumption]` 起草切片 | 拆 R 則流程圖加框，產器 8 框上限仍夠 | ✅ 草擬自判 |

### 內部技術選擇(下層,告知即可)
- 審頁用 `scripts/build-stage4-html.py --action`，不手包 html-shell，不把審頁塞進 `build-gate-twin.py` STAGES。
- 未讀 A／C 線 Stage 4。
- 本 hop 不跑 `status-update.sh`、不改 HISTORY、不填頂欄 PASS。
- rewrite cap 數字不重開；計數落點仍本 slug F2。
- dual-read 欄位名不鎖（OC-3）。
- 生命週期主詞寫「條件頁 latch + freeze + 握手陷阱」，不是整套方法論。
- R／S 編號：條件頁 R-1、空欄 R-2、freeze R-3、握手 R-4、Must-keep R-5、RP／檔集 R-6。

## Test Skeletons(選配)

- `test_s_1_1_a4_generates_without_latch`
- `test_s_1_2_a7_generates_without_latch`
- `test_s_1_3_a10_mech_green_still_humanwait`
- `test_s_1_4_a5_no_hit_no_page`
- `test_s_1_5_b1_hit_stops_at_spec`
- `test_s_1_6_b1_miss_no_demo`
- `test_s_1_7_ask_human_without_latch_rejects`
- `test_s_1_8_false_predicate_stops_at_station`
- `test_s_1_9_table_a_other_rows_no_latch`
- `test_s_1_10_b2_same_wait_b4_irreversible_quiz`
- `test_s_2_1_empty_attestation_chat_cannot_leave_spec`
- `test_s_2_2_agent_write_counts_unwritten`
- `test_s_2_3_no_b1_hit_accepted_rejects`
- `test_s_2_4_human_accepted_plus_attestation_leaves_spec`
- `test_s_2_5_negated_skip_not_owner_call`
- `test_s_3_1_this_slug_five_station_hop_fails`
- `test_s_3_2_f3_cut_existing_md_stays_old7`
- `test_s_3_3_html_only_not_in_flight`
- `test_s_3_4_old_file_missing_new_fields_not_red`
- `test_s_3_5_old7_skips_rewrite_caps`
- `test_s_4_1_doctor_green_not_cut`
- `test_s_4_2_doctor_handshake_version_only`
- `test_s_4_3_f1_rejects_2_0_0_plus_five_station_hops`
- `test_s_4_4_no_2_1_0_no_remote_reroute`
- `test_s_4_5_parse_both_is_not_cut`
- `test_s_5_1_m1_to_m16_all_disposed`
- `test_s_5_2_fake_t_red_on_card`
- `test_s_5_3_fuzzy_s_rejects`
- `test_s_5_4_test_name_missing_s_id_rejects`
- `test_s_5_5_optional_keep_blocks_this_slug_g2`
- `test_s_5_6_four_fields_seam_future_t_constraint`
- `test_s_5_7_missing_m_not_simplify_success`
- `test_s_5_8_stage4_html_rebuilt`
- `test_s_6_1_annex_cannot_drop_rp`
- `test_s_6_2_rewrite_over_cap_rejects`
- `test_s_6_3_no_human_pass_not_done`
- `test_s_6_4_pr_files_only_spec_and_html`

## 確認紀錄

- 前站核對 + 雙源清點 | 2026-09-14 | G1 PASS（2-decision approved）；3-prototype approved + Human ACCEPTED + attestation。雛形 AC-1…AC-8 + Decision SC-1…SC-13。living spec 本 hop 零條 MODIFIED（不改模板／graph／契約）。
- R 範圍確認 | 2026-09-14 | B-line brief：表 A／B 謂詞、空 attestation、freeze、doctor 綠陷阱、M 去向、四欄 seam。六條 R。
- S 逐段確認 | 2026-09-14 | R-1…R-6 全展開；每 S 有觀測欄。
- 收尾四小節 | 2026-09-14 | Acceptance／Out of Scope／Diff Budget／Dependencies 齊。
- Profile + DBC | 2026-09-14 | lane=full、Risk=high、Failure Model 齊；DBC applicable。
- Stage 3 對帳 | 2026-09-14 | Demo Script 各場落到 R／S；棄 hop 板／Ship 重建。
- DD 掃描 | 2026-09-14 | 上層五條草擬自判；無未定事項三詞殘留。
- 機械關卡 | 2026-09-14 | `check-spec-gate.sh` 9/9 全過（37 條 S）。審頁 `build-stage4-html.py --action` 已寫 `4-spec.html`。
