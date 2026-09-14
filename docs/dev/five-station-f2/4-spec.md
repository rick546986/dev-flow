---
feature: five-station-f2
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站 F2 change spec（Implementer A：hop 謂詞／Must-keep fail-closed／五問／CASE）

> 基準:`origin/main` tip `ffbe665`（#333 Human G1 PASS + #334 STATUS companion）。Lane = **full**。契約不 bump。
> G1 已核:`docs/dev/five-station-f2/2-decision.md` `status: approved`、`verdict: PASS`、OC-1～OC-12 ✅ Owner PASS（human:rick @ 2026-09-14 Asia/Taipei，owner chat「可以」）。Decision 組合包 = Winner C `#330` + standing soft-fix。**不是** Agent 自裁。
> **無 Stage 3**：Decision 約束 14 + 本 slug 九條 trigger 0 命中 → 不建 `3-prototype.md`、不另開 proto 桶。本檔 Stage 3 對帳 = N/A。
> A 線：coordinator hop 謂詞、Must-keep fail-closed、事件五問、Decision 具名 CASE 全表映射成 S、同一電池 NEW5／OLD7、`hop_id` 觸發表當 S。獨立於 B／C，不讀不併他線 Stage 4 稿。
> 本 hop 只落 `4-spec.md` + `4-spec.html`（`scripts/build-stage4-html.py --action`）。`status: draft`。`verdict` 空。**不發明 G2 PASS**。不改 STATUS／HISTORY／`_templates/`／`graph.yaml`／scripts 牙。不做 F3 cut。不合併。
> Decision 正本:`docs/dev/five-station-f2/2-decision.md`（1A+2C+3A+4A+5A+6A+7A+8A）。13 具名 CASE 只准加不准減。極性＝注入壞行為該格紅，不是「拒 hop 算綠」。

## 補助模組生命週期（預覽）

主詞是「F2 coordinator 自動前進 + slug 級 hop／latch／cap 紀錄 + NEW5／OLD7 同一電池」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：coordinator 評 brief §3 謂詞；slug 級只增倉；五問可答的 hop／latch／cap 紀錄；檔→五站五桶觸發表；同一入口 NEW5+OLD7 具名 CASE
- 改行為（相關一格）：F2 起 coordinator 真則 hop、假則停修、Must-keep 紅不得 hop；RP-9／10／11 改讀真計數。本 hop 只把契約寫進本檔
- 退役：沒有
- 不動：七檔名、G1／G2／`ACCEPTED` token、既有 `graph.yaml`／Stage 1–4 模板、本 slug 舊 7、F1 十二群牙、`agent-event` schema 1.1、契約 `2.0.0`

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「F1 已鎖 cap 數字與拒收謂詞,但計數落在哪、鍵叫什麼明文交給 F2」 | 本方案處理 | S-3.5、S-4.4、S-4.9 |
| 「現行牙只對 fixture 字樣『第 3 次』正則紅——沒有倉,第三次重寫在 live 裡可以假裝第一次」 | 本方案處理 | S-4.5、S-4.9 |
| 「若三個 cap 寫進 run 級 events.jsonl,新 run 歸零 = 暗改 cap(X5)」 | 本方案處理 | S-3.5、S-4.9 |
| 「marketplace update 換 hops,doctor 仍印 COMPATIBLE」 | 本方案處理 | S-6.2、S-6.3 |
| 「若後續 coordinator 把綠或我已在 plugin cache 當成切五站,舊 7 slug 會被折」 | 本方案處理 | S-6.1、S-6.4、S-5.5 |
| Journey「owner／寫手 chat『可以開下一站』」 | 本方案處理 | S-1.8、S-2.3 |
| Journey「live 第三次重寫假裝第一次」 | 本方案處理 | S-4.5 |
| Workaround「F1 用文案正則擋『doctor 綠所以跟 hops』；擋的是寫出來的謊,不是 coordinator 行為」 | 本方案處理 | S-6.2 |
| Workaround「STATUS／HISTORY 當 hop log；看板可以停在過期的下一刀 F1」 | 本方案處理 | S-3.4、S-8.1 |
| Exception「舊 7 與 in-flight 不套三個 cap」 | 本方案處理 | S-5.4 |
| Exception「F2 可以寫 coordinator 碼,但 F3 前預設路線仍舊 7」 | 本方案處理 | S-6.1、S-7.1 |
| Exception「[Assumption] 把 cap 放進 run 級 events = X5」 | 本方案處理 | S-3.5、S-4.9 |
| Exception「[Assumption] dual-path 同一入口兩路都必須能獨立變紅」 | 本方案處理 | S-5.1、S-5.2 |
| Exception「[Assumption] NEW5 試體是合成 fixture,不是本 slug」 | 本方案處理 | S-5.3、S-5.7 |
| 「本 tree 搜過:沒有 F2 coordinator 實作檔」 | 本方案處理 | S-8.1 |
| Q9 三個計數器落點 | 本方案處理 | S-3.5、S-4.4 |
| Q10 run 級歸零是否 X5 | 本方案處理 | S-4.9 |
| Q11 hop_id 在 F3 前怎麼認 | 本方案處理 | S-4.1、S-4.2、S-4.3 |
| Q12 初寫 vs 重寫 | 本方案處理 | S-4.4 |
| Q13／Q14／Q18 事件怎麼接 × schema bump | 本方案處理 | S-3.1、S-3.5 |
| Q15 Goal 連帶 Decide 是否一次寫 | 本方案處理 | S-4.7 |
| Q16 T≤4 與 hop 重寫 | 本方案處理 | S-4.8 |
| Q17 三前置 | 本方案處理 | S-6.1 |
| Q19 RP-9／10／11 必須餵真計數 | 本方案處理 | S-4.5、S-4.6、S-4.7 |
| Q20 多份 plugin cache 認哪一份 | 本方案處理 | S-6.4 |
| Q21 F2 完是否=檔在或 F1 綠 | 本方案處理 | S-5.1、S-5.2 |
| Q22 三失敗不得當成功 | 本方案處理 | S-2.2、S-2.3、S-2.4 |
| Q23 事件五問、不鎖鍵 | 本方案處理 | S-3.1、S-3.5 |
| Q24 Backlog A 過期 | 刻意維持 | Out of Scope：本 hop 不改 STATUS |
| 「鎖:不刪 G1／G2／ACCEPTED；不做 F3 cut；不把 in-flight 折成五站」 | 本方案處理 | S-7.1、S-7.2、S-7.3、S-7.4 |

## Must-keep Disposition

語法:`M11 → R-x/S-y | Non-Goal:<reason>`。不另發 ID 鏈。M15／M16 是**約束**，不是 Non-Goal。F2 自動前進謂詞含完整度：任一 M 紅 → 不得 hop。

| M | 去向 | 下落 |
|---|---|---|
| M1 ID 鏈；測試名含 S-id | 本方案處理 | S-2.1、S-2.5 |
| M2 圍欄 | 刻意維持 | Out of Scope：本 slug 不改圍欄正本 |
| M3 反模糊 | 本方案處理 | S-2.1、S-2.5 |
| M4 Real-world→Demo→OC | 本方案處理 | S-1.3、S-2.5 |
| M5 人寫 ACCEPTED／Ship PASS | 本方案處理 | S-1.6、S-2.4 |
| M6 G3 Evidence 八點 | 本方案處理 | S-2.1、S-2.5 |
| M7 Profile + fast+high 拒 | 刻意維持 | 本檔 Verification Profile |
| M8 DBC 條件式 | 刻意維持 | 本檔 Design Boundary Contract |
| M9 Files ⊆ 5-tasks | 本方案處理 | S-1.5、S-2.1 |
| M10 驗證五律 | 本方案處理 | S-2.1、S-2.5 |
| M11 T seam + 四欄 | 本方案處理 | S-1.5、S-2.2 |
| M12 author≠approver | 本方案處理 | S-1.5、S-2.1 |
| M13 html 重生 | 本方案處理 | S-8.2 |
| M14 不可逆才 Quiz | 刻意維持 | Out of Scope：本 hop 不改 Quiz 正本 |
| M15 token／檔仍在 | 本方案處理 | S-5.6、S-7.3 |
| M16 F0 不改 graph／牙 | 本方案處理 | S-8.1、S-8.4 |

## Owner Call hang

| OC | 掛到 |
|---|---|
| OC-1 計數落點＝slug 級只增倉 | S-3.5、S-4.9 |
| OC-2 事件＝獨立 slug ledger，不 bump `agent-event` | S-3.1、S-3.5 |
| OC-3 hop_id＝五站別名＋檔→五桶觸發表 | S-4.1、S-4.2、S-4.3 |
| OC-4 Q17 三前置升格 | S-6.1 |
| OC-5 Q10 升格：run 級倉＝X5 | S-4.9 |
| OC-6 Q19 升格：RP-9／10／11 讀真計數 | S-4.5、S-4.6、S-4.7 |
| OC-7 cache 只選碼；路線認專案樹 | S-6.4 |
| OC-8 Goal+Decide 同一次 mutation | S-4.7 |
| OC-9 13 具名 CASE 只准加；極性＝注入壞行為該格紅 | S-5.8；CASE → S 表 |
| OC-10 本 Decision hop 不改 STATUS／不發明 G1 PASS | S-8.1（本 hop 對稱：不改 STATUS、不發明 G2 PASS） |
| OC-11 Q12 第一次 persist＝0，其後 +1 | S-4.4 |
| OC-12 F2 碼可存在，F3 前 live 禁評五站謂詞 | S-6.1、S-5.3 |

## SC → S 對照

每條 Decision SC 至少一條獨立可測 S。13 具名 CASE 另見下表。S 總數見確認紀錄；>40 誠實記帳，不另切開新 slug。

| SC | 一句 | 本檔 S |
|---|---|---|
| SC-BATTERY | 單一入口；缺一路即非 0 | S-5.1 |
| SC-NEW5-HOP-OK | 謂詞全真＋latch 假＋Must-keep 綠 → hop＋五問 | S-1.7、S-3.1 |
| SC-NEW5-PRED-STOP | 謂詞假 → 不 hop、停修、無「要不要繼續」 | S-1.8 |
| SC-NEW5-CAP-3 | 第 3 次 hop 重寫拒；Escalated；數字仍 2 | S-4.5 |
| SC-NEW5-DECIDE-2 | 第 2 次 Decide 整站重開拒 | S-4.6 |
| SC-NEW5-GOAL-2 | 離開 Intake 後第 2 次 Goal 重開拒 | S-4.7 |
| SC-NEW5-MK-RED | 注入 Must-keep 紅仍 hop → 該格紅 | S-2.2 |
| SC-NEW5-SHIP-MECH | 注入機械綠卻標 Done → 該格紅 | S-2.4 |
| SC-NEW5-WAIT-RED | 注入謂詞真仍等人 → 該格紅 | S-2.3 |
| SC-NEW5-RUN2 | 新 `run_id` 後數字仍在、不是 0 | S-4.9 |
| SC-OLD7-NO-FIVE | 已有 1–7 `.md` → 無五站狀態；三 cap 不套 | S-5.4 |
| SC-OLD7-FOLD-RED | 注入對 in-flight 寫五站狀態 → 該格紅 | S-5.5 |
| SC-OLD7-TOKEN | token 在；F1 十二群仍可綠 | S-5.6 |
| SC-OLD7-SELF | 對本目錄求五站 hop → 拒 | S-5.7 |
| SC-DOCTOR | doctor 綠 ≠ 五站通行证 | S-6.2 |
| SC-KNIFE | F2 宣稱完成後三把鎖仍鎖 | S-7.4 |
| SC-HOLLOW | 檔在／只跑 F1／只跑 NEW5 ≠ F2 綠 | S-5.2 |
| SC-Q-CARRY | Q9–Q24 有去向；Q21／Q22／Q23 不可選 | S-8.3 |
| SC-PR | Decision hop 檔集已關；本 hop 對稱為只 4-spec 雙檔 | S-8.1 |

## CASE → S 對照

Decision「本方案要求」13 列只准加不准減。極性：標「→ 紅」＝**注入該壞行為**，該格必須獨立變紅。

| CASE | 路 | 紅／綠 | 本檔 S |
|---|---|---|---|
| NEW5-HOP-OK | NEW5 | 綠：合法 hop | S-1.7 |
| NEW5-PRED-STOP | NEW5 | 綠：合法停修 | S-1.8 |
| NEW5-CAP-3 | NEW5 | 綠：合法拒第 3 次 | S-4.5 |
| NEW5-DECIDE-2 | NEW5 | 綠：合法拒第 2 次 Decide | S-4.6 |
| NEW5-GOAL-2 | NEW5 | 綠：合法拒第 2 次 Goal | S-4.7 |
| NEW5-MK-RED | NEW5 | 預期紅：注入 MK 紅仍 hop | S-2.2 |
| NEW5-SHIP-MECH | NEW5 | 預期紅：注入機械綠當 Done | S-2.4 |
| NEW5-WAIT-RED | NEW5 | 預期紅：注入中途等人 | S-2.3 |
| NEW5-RUN2 | NEW5 | 綠：新 run 數字仍在 | S-4.9 |
| OLD7-NO-FIVE | OLD7 | 綠：無五站狀態 | S-5.4 |
| OLD7-FOLD-RED | OLD7 | 預期紅：注入折 in-flight | S-5.5 |
| OLD7-TOKEN | OLD7 | 綠：token＋F1 牙仍在 | S-5.6 |
| OLD7-SELF | OLD7 | 綠：本目錄 hop 被拒 | S-5.7 |

## hop_id 觸發表（Decision 約束 14；S-4.1 測這張表）

五桶，**不是**七個 stem。舊節點 `N7-g1`／`N6-g2` 不是桶名。

| 寫入檔 | hop_id 桶 |
|---|---|
| `1-discussion.md` | Intake |
| `2-decision.md` | Decide |
| `3-prototype.md` | Spec（與 `4-spec.md` 同桶） |
| `4-spec.md` | Spec |
| `5-tasks.md` | Build（與 `6-implementation-notes.md` 同桶） |
| `6-implementation-notes.md` | Build |
| `7-review.md` | Ship |

無 Stage 3 trigger → 不建 `3-prototype.md`、也不另開 proto 桶；Spec 只由 `4-spec.md` 觸發。

## ADDED Requirements

### R-1: 系統 SHALL 只在自動前進謂詞全真時 hop

SC-NEW5-HOP-OK／SC-NEW5-PRED-STOP／6A／狀態機 §2。Coordinator 讀 brief §3 表 A／B「自動前進」欄。全真 ∧ latch 假 ∧ Must-keep 綠 → **立刻 hop**，不准留下「要不要繼續／請人審／確認一下」。一假 → 停該站修，理由寫該謂詞，不是改問人。Ship **沒有**自動前進。評五站謂詞之前先過 R-6 三前置；缺一條 → `allow_legacy()`，不建五站機。

**審的時候看什麼**
對每一跳只問：哪幾條謂詞、全真有沒有 hop、一假有沒有停修句、有沒有「要不要繼續」。Ship 機械全綠仍 HumanWait。

#### S-1.1 Intake→Decide 四條全真才 hop
- GIVEN NEW5 合成 fixture 已過 R-6 三前置；`docs/dev/<slug>/1-discussion.md` 可解析；Open Questions 全數已解或明標 `[Assumption]`；有 `## Real-world Context`（或 brief 承認的 legacy 且標了 legacy）；A1／A2 若應產則 `build-stage1-html.py`／`build-scan-html.py` exit 0
- WHEN coordinator 評 Intake → Decide
- THEN hop 發生；前進紀錄寫 from=Intake、to=Decide；A1／A2 latch=否 → 紀錄不含「請人審 A1」「請人審 A2」
- 觀測:從該 slug 前進紀錄與目錄檔看 | from-to=Intake→Decide 且無請人審 A1／A2 算過 | n-a:F2 coordinator 本 hop 不落地。替代：狀態機 §2.1 四條；本條 GWT；後站電池 NEW5-HOP-OK stdout
- Operational Context:
  - Actor:coordinator（F2 後）／寫手
  - Goal:Intake 謂詞真就進 Decide，不等「可以開下一站」
  - Situation:NEW5 fixture、三前置已過
  - Known information:狀態機 §2.1；A1／A2 latch=否
  - Missing information:現場會不會仍用 chat 當開關
  - Human decision:不在 Intake 簽
  - Authority:coordinator 禁問「要不要繼續」
  - External dependency:無
  - Out-of-system action:不准改問 owner 繞假謂詞
  - Waiting/timeout behavior:中間不停
  - Recovery:謂詞假 → 停 Intake 修該條；出現請人審 → 當 NEW5-WAIT-RED 紅
  - Audit/handoff requirement:前進紀錄可核五問
  - Observation:見本條觀測

#### S-1.2 Decide→Spec 不等 G1 verdict
- GIVEN 同一 NEW5 fixture；`2-decision.md` 在；`## Decision` 非空；Owner Calls／OC 全裁決、無「待裁決」字樣；A3 自動前進謂詞真；A4 twin 已產或可產
- WHEN coordinator 評 Decide → Spec
- THEN hop 發生；**不**等人寫 G1 `verdict:`；紀錄 from=Decide、to=Spec
- 觀測:從前進紀錄看 | Decide→Spec 發生且無「請填 G1 verdict」算過 | n-a:coordinator 未落地。替代：狀態機 §2.2；brief A3／A4；本條
- Operational Context:不適用 — 與 S-1.1 同一 hop 家族；本條只換 Decide 謂詞與「不等 G1」。

#### S-1.3 Spec→Build 無 trigger 時不建 3-prototype
- GIVEN NEW5 fixture；九條 Stage 3 trigger 全未命中（與本 slug Decision 相同）；`4-spec.md` 在；每個 S 有觀測欄；`lane:`／`Risk:` 可解析；Drafting Decisions 無「待裁決」；`check-spec-gate.sh` 形狀綠；A6／A7 可產
- WHEN coordinator 評 Spec → Build
- THEN hop 發生；目錄**沒有**新建 `3-prototype.md`；A5 不建頁；B1 未命中條款視為真；**不**等人寫 G2 `verdict:`
- 觀測:從目錄 `ls` 與前進紀錄看 | Spec→Build 發生、無 `3-prototype.md`、無請填 G2 算過 | n-a:coordinator 未落地。替代：狀態機 §2.3 第 5 條；Decision 約束 14；本 slug 自身 0 trigger
- Operational Context:
  - Actor:coordinator／本 slug 寫手
  - Goal:無互動風險不產 Demo、不 latch
  - Situation:0 trigger（本 Decision 已收）
  - Known information:九條 trigger；A5 沒命中不建頁
  - Missing information:無
  - Human decision:不在 Spec 簽 Demo
  - Authority:未命中不得強迫 `ACCEPTED`（RP-12）
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不 latch
  - Recovery:若被要求 `ACCEPTED` → RP-12 紅
  - Audit/handoff requirement:trigger 判定落檔（本 slug：不建 3-prototype）
  - Observation:見本條觀測

#### S-1.4 Spec→Build 命中 B1 時必須 ACCEPTED 加 attestation
- GIVEN 另一份 NEW5 fixture；九條 trigger 至少一條命中；`3-prototype.md` 在
- WHEN Human verdict ≠ `ACCEPTED`、或 `ACCEPTED` 但無 `Verdict attestation: human:<名>` 行，且 coordinator 被求 hop 出 Spec
- THEN 不 hop；B1 命中且 attestation 未寫 → 進 HumanWait，不是偷偷 hop；無 attestation 的 `ACCEPTED` = 謂詞假
- 觀測:從 hop 拒絕理由與狀態看 | 狀態=HumanWait 或停 Spec；未 hop 到 Build 算過 | n-a:coordinator 未落地。替代：狀態機 §2.3 第 6 條；F1 RP-13
- Operational Context:
  - Actor:Demo 參與者／coordinator
  - Goal:互動未核不得離 Spec
  - Situation:B1 命中
  - Known information:attestation 必須人類親寫
  - Missing information:人何時寫
  - Human decision:ACCEPTED／REVISE／NOT_REVIEWED
  - Authority:Agent 禁寫 attestation
  - External dependency:可操作 Demo
  - Out-of-system action:人親填
  - Waiting/timeout behavior:HumanWait 直到 md 頂欄／Human verdict 寫入
  - Recovery:REVISE → 回 Spec 重 Demo，吃 hop cap
  - Audit/handoff requirement:attestation 行
  - Observation:見本條觀測

#### S-1.5 Build→Ship 四欄與獨立 review 全真才 hop
- GIVEN NEW5 fixture；`5-tasks.md` 每 T 有 Covers／Files／Verify／Blocked-by；`6-implementation-notes.md` 每 T 有獨立 review PASS 且 reviewer ≠ implementer；本次 S 全綠；Files ⊆ 5-tasks Files 聯集
- WHEN coordinator 評 Build → Ship
- THEN hop 發生；A8／A9 latch=否 → 紀錄不含「想給人看看任務板」「請人審 A8」
- 觀測:從前進紀錄與 T 卡看 | Build→Ship 發生且無請人審任務板算過 | n-a:coordinator 未落地。替代：狀態機 §2.4；RP-1／RP-2
- Operational Context:不適用 — 與 S-1.1 同一 hop 家族；本條只換 Build 四欄與獨立 review。

#### S-1.6 Ship 沒有自動前進
- GIVEN NEW5 fixture 已在 Ship；`7-review.md` 在；機械項全綠（Evidence 八點可勾）；md 頂欄 `verdict:` 仍空或不是人寫的 `PASS`
- WHEN coordinator 評 Ship → Done
- THEN **不** hop；必須進 HumanWait（A10 latch=是）；不得把機械綠寫成 `verdict: PASS`
- 觀測:從狀態與頂欄看 | 狀態=HumanWait 或留 Ship；`verdict` 仍空算過 | n-a:coordinator 未落地。替代：狀態機 §2.5；S-2.4 NEW5-SHIP-MECH
- Operational Context:
  - Actor:Ship 審查者／coordinator
  - Goal:出貨樹=審過的樹
  - Situation:機械全綠
  - Known information:A10 是唯一預設人停
  - Missing information:人寫 PASS 還是 REQUEST_CHANGES／HOLD
  - Human decision:頂欄 `verdict:`
  - Authority:coordinator／Agent 禁寫 PASS
  - External dependency:無
  - Out-of-system action:人讀審頁後寫頂欄
  - Waiting/timeout behavior:HumanWait；HOLD 留 Ship
  - Recovery:REQUEST_CHANGES → 回可改的上一站，吃對應 cap
  - Audit/handoff requirement:頂欄 `verdict:` 是正本
  - Observation:見本條觀測

#### S-1.7 NEW5-HOP-OK 綠格：合法 hop 加五問紀錄
- GIVEN NEW5 合成 fixture（不是 `docs/dev/five-station-f2/`、不是 `docs/dev/five-station-simplify/`）；當下 hop 的自動前進謂詞全真；latch 假；Must-keep 全綠；該 hop_id 桶 < 2
- WHEN coordinator 評該 hop
- THEN 發生 hop；人指得到一筆前進紀錄且五問有答（誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated=否）；不是 chat、不是 `attempt_completed` 冒充
- 觀測:從單一電池 NEW5-HOP-OK 格與該筆紀錄看 | 該格綠；五問各有可指答案算過 | n-a:電池入口檔名本 hop 不鎖（Decision 交 4-spec 形、鍵名 OPEN）。替代：本條 GWT；Decision CASE NEW5-HOP-OK；後站入口 stdout 含該 CASE 名且該格綠
- Operational Context:
  - Actor:coordinator／電池操作者
  - Goal:合法 hop 可被指出
  - Situation:謂詞全真
  - Known information:五問語意槽；鍵名不鎖
  - Missing information:紀錄檔路徑（Stage 5 選形，本檔不鎖鍵）
  - Human decision:無（latch 假）
  - Authority:coordinator hop，人不住中間簽
  - External dependency:slug 級倉
  - Out-of-system action:無
  - Waiting/timeout behavior:立刻 hop
  - Recovery:五問缺一格 → 該 hop 不算完成
  - Audit/handoff requirement:五問可指
  - Observation:見本條觀測

#### S-1.8 NEW5-PRED-STOP 綠格：謂詞假就停修
- GIVEN 同一家族 NEW5 fixture；自動前進謂詞至少一條為假（例：`4-spec.md` 缺觀測欄、或 OC 仍有「待裁決」）
- WHEN coordinator 評該 hop
- THEN 不 hop；拒絕理由點名**該條**謂詞假；紀錄與 stdout **不含**「要不要繼續」「請人審」「確認一下」
- 觀測:從 NEW5-PRED-STOP 格與拒絕理由看 | 該格綠；理由含謂詞名；零「要不要繼續」算過 | n-a:coordinator 未落地。替代：Decision CASE NEW5-PRED-STOP；本條
- Operational Context:
  - Actor:寫手／coordinator
  - Goal:假謂詞停在該站修
  - Situation:例如缺觀測欄
  - Known information:哪一條假
  - Missing information:無
  - Human decision:修該站檔，不是簽「繼續」
  - Authority:不准改問人繞
  - External dependency:無
  - Out-of-system action:寫手改 md
  - Waiting/timeout behavior:不停等人；停修
  - Recovery:修到謂詞真再評
  - Audit/handoff requirement:拒絕理由可指謂詞
  - Observation:見本條觀測

### R-2: 系統 SHALL 在 Must-keep 紅時 fail-closed 拒 hop

SC-NEW5-MK-RED／SC-NEW5-WAIT-RED／SC-NEW5-SHIP-MECH／G-keep-1／6A。自動前進謂詞**含完整度**。Must-keep 未綠不得 hop。三失敗各自要能紅，不得用「已經五站了」省略。CASE 極性：紅格＝注入壞行為該格紅，不是「coordinator 拒 hop 算綠」。

**審的時候看什麼**
三張紅格各自獨立。把拒 hop 記成 NEW5-MK-RED 綠＝極性反了，打回。

#### S-2.1 Must-keep 未綠不得 hop
- GIVEN NEW5 fixture；自動前進謂詞其餘為真；latch 假；Must-keep 至少一條紅（例：某一 T 缺 Verify，或測試名不含 S-id）
- WHEN coordinator 評 hop
- THEN 不 hop；拒絕理由含 Must-keep／該 M-id／該缺欄；狀態留在原站
- 觀測:從拒絕理由與狀態看 | 未 hop；理由含 Must-keep 或缺欄名算過 | n-a:coordinator 未落地。替代：brief §5；Decision 約束 7；本條
- Operational Context:
  - Actor:coordinator／寫手
  - Goal:完整度未過不准前進
  - Situation:T 缺 Verify
  - Known information:M11／RP-1
  - Missing information:無
  - Human decision:補欄，不是簽 hop
  - Authority:Must-keep 入謂詞，不是 hop 後警告
  - External dependency:無
  - Out-of-system action:補 5-tasks／測試名
  - Waiting/timeout behavior:停修，不是 HumanWait
  - Recovery:補綠後再評
  - Audit/handoff requirement:拒絕理由
  - Observation:見本條觀測

#### S-2.2 NEW5-MK-RED：注入 Must-keep 紅仍 hop 該格必須紅
- GIVEN NEW5 電池；測法＝**注入**「Must-keep 紅（例：T 缺 Verify）仍 hop」
- WHEN 跑該 CASE 格
- THEN NEW5-MK-RED **獨立變紅**；不得把「coordinator 拒 hop」記成此格綠；此格紅時不得標 F2 成功
- 觀測:從單一電池該格顏色／exit 看 | 注入壞 hop → 該格紅；拒 hop 不得洗成綠算過 | n-a:電池未落地。替代：Decision CASE NEW5-MK-RED 極性句；本條 THEN
- Operational Context:
  - Actor:電池作者／F2 reviewer
  - Goal:極性不反
  - Situation:有人想把「拒 hop」當 MK-RED 綠
  - Known information:OC-9；約束 15
  - Missing information:無
  - Human decision:紅格維持注入測法
  - Authority:翻極性＝翻 Decision
  - External dependency:單一電池入口
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:改回注入測法
  - Audit/handoff requirement:CASE 表極性欄
  - Observation:見本條觀測

#### S-2.3 NEW5-WAIT-RED：注入謂詞真仍等人該格必須紅
- GIVEN NEW5 電池；謂詞全真、latch 假；測法＝**注入**留下「要不要繼續」或「請人審」或「確認一下」
- WHEN 跑該 CASE 格
- THEN NEW5-WAIT-RED 獨立變紅；中途等人不是客氣
- 觀測:從該格顏色看 | 注入這三句任一 → 該格紅算過 | n-a:電池未落地。替代：Decision CASE NEW5-WAIT-RED；F1 RP-14 文案牙仍回歸；本條
- Operational Context:
  - Actor:coordinator／寫手
  - Goal:latch 假不准問人
  - Situation:謂詞已真
  - Known information:X6；A 線中途等人拒法
  - Missing information:無
  - Human decision:無（不該被問）
  - Authority:latch 未命中禁開審查 widget
  - External dependency:無
  - Out-of-system action:不准改問 owner
  - Waiting/timeout behavior:立刻 hop，零等待句
  - Recovery:刪問人紀錄後重評
  - Audit/handoff requirement:前進紀錄無三句
  - Observation:見本條觀測

#### S-2.4 NEW5-SHIP-MECH：注入機械綠當 Done 該格必須紅
- GIVEN NEW5 電池；`7-review.md` 機械項可全綠；無人寫頂欄 `verdict: PASS`；測法＝**注入**標狀態 Done
- WHEN 跑該 CASE 格
- THEN NEW5-SHIP-MECH 獨立變紅；coordinator／Agent 寫入 `PASS` 視為未寫
- 觀測:從該格顏色與狀態看 | 注入 Done → 該格紅；狀態不得為 Done 算過 | n-a:電池未落地。替代：Decision CASE NEW5-SHIP-MECH；F1 RP-8／RP-16
- Operational Context:
  - Actor:Ship 審查者
  - Goal:機械綠 ≠ PASS
  - Situation:勾選已滿
  - Known information:OC-3 Ship 唯人
  - Missing information:人何時寫
  - Human decision:頂欄 `verdict:`
  - Authority:禁代寫
  - External dependency:無
  - Out-of-system action:人寫頂欄
  - Waiting/timeout behavior:HumanWait
  - Recovery:刪機器 `PASS`，留 HumanWait
  - Audit/handoff requirement:頂欄作者是人
  - Observation:見本條觀測

#### S-2.5 Must-keep 16 列都有去向且「已五站故省」必須紅
- GIVEN 本檔 Must-keep Disposition 與一份宣稱「已經五站了所以可省 M11／四欄／seam」的稿
- WHEN 人核對 16 列去向；並把該稿送 F2 電池或 F1 牙
- THEN 16 列每列去向 ∈ {本方案處理, 刻意維持} 且處理列有 `S-` 或 `R-`；該「可省」稿紅（F1 S-2.1／S-2.7 回歸仍咬；F2 不得把 hop 當省略理由）
- 觀測:從本檔 Must-keep 表與牙／電池看 | 16 列有下落；「已五站故省」紅算過 | 讀本檔 Must-keep Disposition；`rg -n "已五站故省|四欄可選" docs/dev/five-station-f2/4-spec.md` 只出現在本條 THEN／Negative Constraints
- Operational Context:不適用 — 去向帳與禁句，無新交接。

### R-3: 系統 SHALL 留下能答五問的 hop／latch／cap 紀錄

SC-NEW5-HOP-OK／G-obs-1／2C／OC-2。前進／latch 開火／cap 用盡各留一筆人指得到的紀錄。五問＝誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated。**不鎖** JSON／YAML 鍵名、不鎖 `event_type`。本刀**不 bump** `agent-event`。看板／chat／`STATUS.md`／`attempt_completed` 不是正本。

**審的時候看什麼**
三類各至少一筆。五個問題有答。沒有鍵名被寫成已核。

#### S-3.1 一次成功 hop 的紀錄答得出五問
- GIVEN NEW5 fixture 剛完成一次合法 hop（S-1.7）
- WHEN 人指該筆前進紀錄
- THEN 五問都有可指答案：誰＝coordinator（或同等執行者 id，鍵名不鎖）；從哪到哪＝兩個五站別名；哪條謂詞＝brief §3 表 A／B 的 id 或等效句；哪只 cap＝該 hop 桶當下數字；是否 Escalated＝否。不是 chat 逐字稿、不是 `attempt_completed` 冒充
- 觀測:從該筆紀錄五格看 | 五格都有值；零 `attempt_completed` 冒充算過 | n-a:紀錄檔路徑本 hop 不鎖。替代：Decision Q23；本條五問清單
- Operational Context:
  - Actor:後站 reviewer／owner
  - Goal:不用問人才知道 hop 為什麼走
  - Situation:hop 已發生
  - Known information:五問語意槽
  - Missing information:鍵名（OPEN）
  - Human decision:無
  - Authority:鎖 `event_type=hop_advanced` 當已核＝偷做 annex，回 Stage 2
  - External dependency:slug ledger
  - Out-of-system action:人指檔
  - Waiting/timeout behavior:無
  - Recovery:缺一問 → 該 hop 未完成
  - Audit/handoff requirement:五問
  - Observation:見本條觀測

#### S-3.2 一次 latch 開火的紀錄答得出五問
- GIVEN NEW5 fixture 命中 A10 或 B1 latch
- WHEN coordinator 進 HumanWait 並留紀錄
- THEN 該筆答五問：誰；從哪到哪（或「留在 Ship／Spec」）；哪條 latch 謂詞（A10／B1／B2／B4）；哪只 cap（本次未加則寫未加）；是否 Escalated＝否
- 觀測:從 latch 紀錄五格看 | 五格可指算過 | n-a:路徑不鎖。替代：brief §3 唯一出口；本條
- Operational Context:不適用 — 與 S-3.1 同一紀錄家族；本條只換 latch 開火。

#### S-3.3 一次 cap 用盡的紀錄答得出五問
- GIVEN NEW5 fixture 觸發 hop≤2 或 Decide≤1 或 Goal reopen≤1 用盡
- WHEN coordinator 進 Escalated 並留紀錄
- THEN 該筆答五問：誰；從哪到哪（被拒的 hop）；哪條謂詞（cap 用盡）；哪只 cap（hop／Decide／Goal 具名）；是否 Escalated＝是
- 觀測:從 cap 紀錄五格看 | Escalated=是且 cap 具名算過 | n-a:路徑不鎖。替代：S-4.5／S-4.6／S-4.7
- Operational Context:不適用 — 與 S-3.1 同一家族；本條只換 cap 用盡。

#### S-3.4 chat 與 STATUS 不得當 hop 正本
- GIVEN 一次 hop 只留下 Cursor chat「可以開下一站」或只改了 `STATUS.md` Backlog，沒有 slug ledger 紀錄
- WHEN 人問「有沒有留下」
- THEN 該 hop **不算**留下；G-obs-1 未滿足
- 觀測:從「可指紀錄」有無看 | 只有 chat／STATUS → 未留下算過 | 本 tree `docs/dev/STATUS.md` Backlog A 過期是活樣本（Q24）；本 hop 不改該列
- Operational Context:不適用 — 正本否定句。

#### S-3.5 紀錄住 slug 級只增倉且不 bump schema、不鎖鍵
- GIVEN 現行 `observability/schema/agent-event.schema.json` 仍是 1.1；現行 run 級路徑是 `.devflow/runs/<run_id>/coordinator/events.jsonl`
- WHEN F2 落地 hop／latch／cap 紀錄與三個計數器
- THEN 計數與五問紀錄住 **slug 級只增倉**（與 run 級 `events.jsonl` 分家）；本刀不新增 `event_type`、不 bump schema、不改 `hooks/_doctor_impl.py`；正文與 DD **沒有**把某一 JSON 鍵名寫成已核
- 觀測:從 F2 diff 與本檔用詞看 | 無 `agent-event` bump；無「已核鍵名=…」；倉不在 `runs/<run_id>/` 下算過 | n-a:本 hop 零碼。替代：`rg -n "event_type=hop_advanced|已核鍵" docs/dev/five-station-f2/4-spec.md` 不得出現「已核」；Decision OC-2／約束 11
- Operational Context:不適用 — 倉與 schema 範圍。

### R-4: 系統 SHALL 用五桶檔→hop_id 觸發表計數

SC-NEW5-CAP-3／DECIDE-2／GOAL-2／RUN2／3A／約束 6／14。`hop_id` ∈ {Intake, Decide, Spec, Build, Ship}。第一次成功 persist＝0；其後每一次成功 persist 該桶 +1；第一次寫不算進 hop≤2。七 stem 各一桶已拒。T 嘗試 ≤4 不與 hop 桶混算，除非整站重寫 `5-tasks.md`／`6-implementation-notes.md`（加的是 **Build** 桶）。

**審的時候看什麼**
觸發表七列。同桶兩檔加的是同一個 2。第 3 次重寫拒且數字仍 2。新 run 不是 0。

#### S-4.1 七個寫入檔映射到五個 hop_id 桶
- GIVEN NEW5 fixture 已過三前置；coordinator 對下列檔做一次成功 persist
- WHEN 讀該次寫入對到的 `hop_id`
- THEN 映射必須是：`1-discussion.md`→Intake；`2-decision.md`→Decide；`3-prototype.md`→Spec；`4-spec.md`→Spec；`5-tasks.md`→Build；`6-implementation-notes.md`→Build；`7-review.md`→Ship。零個映射到 `N7-g1`／`N6-g2`／七個 stem 名
- 觀測:從 hop_id 指派表或紀錄 from／桶名看 | 七列與本檔「hop_id 觸發表」逐列相同算過 | n-a:coordinator 未落地。替代：本檔觸發表；Decision 約束 14；後站對該表的單元測試名含 `s_4_1`
- Operational Context:不適用 — 對照表，無現場交接。

#### S-4.2 同站兩檔同桶且無 trigger 不開 proto 桶
- GIVEN NEW5 fixture A：無 Stage 3 trigger。NEW5 fixture B：有 trigger 且已寫 `3-prototype.md` 與 `4-spec.md`
- WHEN 各做成功 persist
- THEN A：不建 `3-prototype.md`、不存在第六個 proto 桶、Spec 只因 `4-spec.md` +1。B：`3-prototype.md` 與 `4-spec.md` 加的是**同一個** Spec 桶（不是各 ≤2）。`5-tasks.md` 與 `6-implementation-notes.md` 加的是**同一個** Build 桶
- 觀測:從各桶數字看 | A 無 proto 桶；B 的 Spec 數字=兩次 persist 之和（第一次=0 後規則見 S-4.4）算過 | n-a:未落地。替代：Decision 約束 14 末段
- Operational Context:不適用 — 分桶算術。

#### S-4.3 七 stem 各一桶必須被拒
- GIVEN 一份實作把 `3-prototype`／`4-spec`／`5-tasks`／`6-implementation-notes` 分成四個獨立 hop≤2 桶（B 線 2A）
- WHEN 送 F2 規格或電池
- THEN 拒；理由含「稀釋 hop≤2」或「七 stem」
- 觀測:從拒絕理由看 | 七 stem 方案不得當已核算過 | 本檔 Rejected／Out of Scope 含「七 stem」；`2-decision.md` 已拒 B 線 2A
- Operational Context:不適用 — 已拒方案。

#### S-4.4 第一次成功 persist＝0，其後 +1
- GIVEN NEW5 fixture 某 `hop_id` 桶尚無成功 persist
- WHEN 第一次成功 persist 該桶對應檔；之後再成功 persist 同一桶一次
- THEN 第一次之後該桶數字＝0（第一次寫不算進 hop≤2）；第二次之後該桶數字＝1。計數看寫入發生，不看模型名／session
- 觀測:從該桶數字看 | 序列 0 然後 1 算過 | n-a:倉路徑不鎖。替代：Decision 約束 6；狀態機 §3「第一次寫不算」
- Operational Context:不適用 — 計數切點。

#### S-4.5 NEW5-CAP-3：第 3 次 hop 重寫拒且數字仍 2
- GIVEN NEW5 fixture 同一 hop_id 已重寫 2 次（第一次 persist＝0 不算；其後兩次 +1 使數字＝2）
- WHEN 第 3 次重寫被要求執行
- THEN 拒；狀態 Escalated；拒後該桶數字仍是 2（無人手改小、無 reset）。RP-9 讀的是這倉，不是 fixture 正文「第 3 次」
- 觀測:從 NEW5-CAP-3 格、拒絕理由、倉數字看 | 該格綠；Escalated；數字=2 算過 | n-a:倉未落地。替代：Decision CASE NEW5-CAP-3；F1 `five_station_f1.py` RP-9 字樣牙可留回歸，不得替代本倉
- Operational Context:
  - Actor:coordinator／Escalated 接收者
  - Goal:重寫有上限
  - Situation:同一 hop 又被要求重寫
  - Known information:hop≤2
  - Missing information:無（數字已鎖）
  - Human decision:修 brief／放行一次／停（Escalated 出口）
  - Authority:不准暗改 cap（X5）
  - External dependency:slug 倉
  - Out-of-system action:人明示下一手
  - Waiting/timeout behavior:Escalated 等人
  - Recovery:人明示後才離 Escalated
  - Audit/handoff requirement:數字只增不減
  - Observation:見本條觀測

#### S-4.6 NEW5-DECIDE-2：第 2 次 Decide 整站重開拒
- GIVEN NEW5 fixture 已離開 Decide 一次，且已重開 Decide 1 次
- WHEN 第 2 次整站重開 Decide（含 Decision 翻案、OC 重裁）
- THEN 拒（RP-10）。Decide 站內、尚未 hop 出去的小改不算一次。RP-10 讀倉，不是「Decide 重開第 2」字樣
- 觀測:從 NEW5-DECIDE-2 格與 Decide 桶看 | 該格綠；第 2 次重開未發生算過 | n-a:未落地。替代：Decision CASE NEW5-DECIDE-2；狀態機 §3.2
- Operational Context:不適用 — 與 S-4.5 同一 cap 家族；本條只換 Decide 桶。

#### S-4.7 NEW5-GOAL-2：第 2 次 Goal 重開拒且與 Decide 一次寫
- GIVEN NEW5 fixture 已 hop 出 Intake；Goal／Success Criteria／問題陳述已重開 1 次
- WHEN 第 2 次 Goal 重開被要求執行
- THEN 拒（RP-11）。若此次 Goal 重開會造成第二次 Decide，兩個計數**同一次 mutation** 寫入並用盡 Decide cap → Escalated。分兩次寫讓 Goal 躲掉 Decide cap＝違 OC-8
- 觀測:從 NEW5-GOAL-2 格與兩桶數字看 | 該格綠；兩桶同一次寫入；無「只加 Goal 不加 Decide」算過 | n-a:未落地。替代：Decision CASE NEW5-GOAL-2；OC-8
- Operational Context:
  - Actor:coordinator
  - Goal:Goal 重開不能免 Decide cap
  - Situation:離開 Intake 後改 Goal
  - Known information:Goal reopen≤1；Decide≤1
  - Missing information:無
  - Human decision:Escalated 出口
  - Authority:一次 mutation
  - External dependency:slug 倉
  - Out-of-system action:人明示
  - Waiting/timeout behavior:Escalated
  - Recovery:人明示
  - Audit/handoff requirement:兩桶同一筆寫入
  - Observation:見本條觀測

#### S-4.8 T 嘗試 ≤4 不混進 hop 桶
- GIVEN NEW5 fixture 在 Build；同一 T 重做第 2、第 3、第 4 次（acceptance seam）
- WHEN 每次只重做該 T，沒有整份重寫 `5-tasks.md` 或 `6-implementation-notes.md`
- THEN hop／Build 桶數字不變；該 T 吃嘗試上限 4。整份 5-tasks／6-notes 被整站重寫 → 加 **Build** 桶 1，不是兩個 stem 各 +1
- 觀測:從 Build 桶與 T 嘗試計數看 | 單 T 重做桶不變；整站重寫只 +1 Build 算過 | n-a:未落地。替代：狀態機 L107–L108；Decision 約束 5
- Operational Context:不適用 — 計數隔離。

#### S-4.9 NEW5-RUN2：新 run_id 不得把數字歸零
- GIVEN NEW5 fixture 某 hop 桶數字已是 1（或 Decide／Goal 已非 0）
- WHEN 另開新 `run_id`（或重開 process）再讀倉
- THEN 該 hop 桶／Decide／Goal 數字仍在，不是 0。把數字只寫在 `.devflow/runs/<run_id>/coordinator/events.jsonl` → 本條失敗（X5）
- 觀測:從 NEW5-RUN2 格與第二次讀數看 | 該格綠；數字≠0 算過 | n-a:倉路徑不鎖，只鎖「slug 級、只增、跨 run 仍在」。替代：Decision CASE NEW5-RUN2；ledger.py 現行是 run 級＝1B 已拒
- Operational Context:
  - Actor:coordinator／電池
  - Goal:cap 跨 run 仍在
  - Situation:第二次 run
  - Known information:X5
  - Missing information:檔名（Stage 5 選，本檔不鎖鍵）
  - Human decision:無
  - Authority:1B 已拒
  - External dependency:slug 倉
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:若讀到 0 → 本條紅，不得當 F2 綠
  - Audit/handoff requirement:跨 run 讀數
  - Observation:見本條觀測

### R-5: 系統 SHALL 只在同一電池 NEW5+OLD7 都過時宣稱 F2 完

SC-BATTERY／SC-HOLLOW／5A。單一入口（一支 selftest／一個 process）。NEW5＝合成 fixture。OLD7＝已有 1–7 `.md` 的 fixture。缺一路、跳過一路、只跑 `test-five-station-f1.sh`、只證明「檔在」→ 整電池非 0。

**審的時候看什麼**
入口原始 stdout／exit。13 CASE 都在。本目錄不是 NEW5 白老鼠。

#### S-5.1 單一入口缺一路即非 0
- GIVEN F2 電池入口（一支命令／一個 process；檔名本 hop 不鎖）
- WHEN (a) 只跑 NEW5 組；(b) 只跑 OLD7 組；(c) 入口只轉呼叫 `scripts/test-five-station-f1.sh`；(d) 兩組都跑且都過
- THEN (a)(b)(c) exit ≠ 0；(d) exit＝0 **當且僅當**兩組都過。兩支互不認識的腳本各綠一次 ≠ dual-path
- 觀測:從該入口原始 stdout／exit 看 | 缺一路非 0；兩路過才 0 算過 | n-a:入口檔名不鎖。替代：Decision SC-BATTERY；本條四分支
- Operational Context:
  - Actor:F2 reviewer／CI
  - Goal:hollow 不能綠
  - Situation:有人只想跑開心 hop
  - Known information:同一 process
  - Missing information:入口檔名（Stage 5）
  - Human decision:無
  - Authority:5B／5C 已拒
  - External dependency:合成 NEW5 + OLD7 fixture
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:補跑缺的一路
  - Audit/handoff requirement:原始 exit
  - Observation:見本條觀測

#### S-5.2 檔在／只跑 F1／只跑 NEW5-HOP-OK 不得標 F2 綠
- GIVEN 下列任一被標「F2 綠」：(a) 僅證明 coordinator 檔存在；(b) 僅 `test-five-station-f1.sh` 十二群綠；(c) 僅 NEW5-HOP-OK 綠而 OLD7 組未跑
- WHEN 對該宣稱跑電池或審查
- THEN 必須非 0／必須被拒（SC-HOLLOW）
- 觀測:從電池 exit 或審查拒絕看 | (a)(b)(c) 任一當完成 → 非 0 算過 | n-a:未落地。替代：Decision SC-HOLLOW；`scripts/test-five-station-f1.sh` 檔頭仍寫牙自檢不是 hop 電池
- Operational Context:不適用 — 完成定義否定句。

#### S-5.3 NEW5 試體是合成 fixture
- GIVEN F2 電池 NEW5 組的 fixture 路徑清單
- WHEN 人核對路徑
- THEN 清單**不含** `docs/dev/five-station-f2/` 站檔當 hop 試體，也不含 `docs/dev/five-station-simplify/` 當 hop 試體
- 觀測:從 fixture 路徑看 | 兩目錄不在 NEW5 試體算過 | 本 hop `ls docs/dev/five-station-f2/` 已有 1／2 站檔＝in-flight；不得當 NEW5
- Operational Context:不適用 — 路徑禁則。

#### S-5.4 OLD7-NO-FIVE：已有 1–7 md 無五站狀態
- GIVEN OLD7 fixture 目錄已有 1–7 任一 `.md`（可為合成舊 7 樹，不是本目錄當 NEW5）
- WHEN coordinator 看到該 slug
- THEN 不建立五站機；無五站狀態寫入；三 cap 不套（可走既有 T 上限 4）；走 `allow_legacy()`
- 觀測:從 OLD7-NO-FIVE 格與該目錄看 | 該格綠；無五站狀態檔／無三 cap 數字算過 | n-a:未落地。替代：Decision CASE OLD7-NO-FIVE；狀態機 L49–L50
- Operational Context:
  - Actor:in-flight 執行者／coordinator
  - Goal:走完手上舊 7
  - Situation:目錄已有站檔
  - Known information:in-flight = 1–7 任一 `.md`；僅 html 不凍
  - Missing information:無
  - Human decision:無（放手 graph）
  - Authority:不得折
  - External dependency:既有 graph
  - Out-of-system action:無
  - Waiting/timeout behavior:舊 7 例行閘
  - Recovery:若寫入五站狀態 → S-5.5 紅
  - Audit/handoff requirement:in_flight=true
  - Observation:見本條觀測

#### S-5.5 OLD7-FOLD-RED：注入折 in-flight 該格必須紅
- GIVEN OLD7 fixture；測法＝**注入**對該 fixture 寫五站狀態或五站 hop
- WHEN 跑該 CASE 格
- THEN OLD7-FOLD-RED 獨立變紅（RP-15）
- 觀測:從該格顏色看 | 注入折線 → 該格紅算過 | n-a:未落地。替代：Decision CASE OLD7-FOLD-RED；F1 inflight kind
- Operational Context:不適用 — 與 S-2.2 同一注入極性；本條只換折線。

#### S-5.6 OLD7-TOKEN：token 與 F1 牙仍綠
- GIVEN OLD7 fixture 與本 repo token／F1 牙
- WHEN 跑 `scripts/check-gate-tokens.sh`（或同等）與 `scripts/test-five-station-f1.sh`
- THEN 兩支仍綠；G1／G2／`ACCEPTED` 檔與 token 仍在
- 觀測:從 OLD7-TOKEN 格與兩支腳本 exit 看 | 該格綠；token 掃描無缺算過 | 本 hop 不改 token；可在本 tree 跑 `bash scripts/check-gate-tokens.sh` 與 `bash scripts/test-five-station-f1.sh` 作回歸地板
- Operational Context:不適用 — 回歸地板。

#### S-5.7 OLD7-SELF：對本目錄求五站 hop 必須拒
- GIVEN `docs/dev/five-station-f2/` 已有 `1-discussion.md`／`2-decision.md`（本 hop 之後另有 `4-spec.md`）
- WHEN coordinator 被求對本目錄做五站自動前進
- THEN 拒；目錄仍是舊 7 站檔；試體不是把本目錄當 NEW5
- 觀測:從 OLD7-SELF 格與本目錄 `ls` 看 | 該格綠；無五站狀態寫入算過 | 本 hop 落 `4-spec.md` 後 in-flight 更凍；`ls docs/dev/five-station-f2/*.md`
- Operational Context:
  - Actor:本 slug 執行者
  - Goal:自己走到 G1／G2／G3 仍舊 7
  - Situation:本目錄已 in-flight
  - Known information:G-self-1
  - Missing information:無
  - Human decision:不把自己當白老鼠
  - Authority:RP-15
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:舊 7
  - Recovery:刪誤寫的五站狀態
  - Audit/handoff requirement:本目錄檔名仍舊 7
  - Observation:見本條觀測

#### S-5.8 13 CASE 只准加且極性不得反
- GIVEN Decision「本方案要求」13 列與本檔 CASE → S 表
- WHEN 後站 5-tasks／電池少任一列，或把紅格改成「拒 hop 算綠」
- THEN 翻 Decision；本檔不得減列。4-spec 可加列，不可把「檔在」加成通過條件
- 觀測:從兩張表列數與極性欄看 | 13 列都在；三張紅格仍寫注入算過 | 數本檔 CASE → S 表列；對到 Decision L159–L172
- Operational Context:不適用 — 表完整性。

### R-6: 系統 SHALL 在專案樹路線未開時拒評五站謂詞

SC-DOCTOR／4A／7A。評五站謂詞之前先問專案樹：契約已宣告 2.1.0 ∧ 非 in-flight ∧ F3 cut 已發生。缺一條 → `allow_legacy()`。`doctor COMPATIBLE`／exit 0 只證明握手。`marketplace update` 單獨 ≠ cut。plugin cache 只選本 process 讀哪份 hops **碼**，不是路條。本刀不改 `hooks/_doctor_impl.py`。

**審的時候看什麼**
拒絕理由是「路線未宣告／仍舊 7」，不是「doctor 已綠」。cache 路徑不出現在路線許可欄。

#### S-6.1 三前置缺一條就 allow_legacy
- GIVEN 任一 live slug（含本目錄、含 F0–F2 母版新軌）；三前置至少一條假：契約不是已宣告 2.1.0、或 in-flight、或 F3 cut 尚未發生
- WHEN coordinator 被求評五站 hop 謂詞
- THEN 不建五站機；走 `allow_legacy()`；不評 Intake→Decide 等五站謂詞
- 觀測:從路線判定與是否寫入五站狀態看 | allow_legacy；零五站 hop 算過 | n-a:coordinator 未落地。替代：Decision 4A／約束 10；brief §6；本 tree 契約仍 `2.0.0`（`devflow-contract.json`）
- Operational Context:
  - Actor:採用 owner／coordinator
  - Goal:未 cut 前 live 仍舊 7
  - Situation:F3 尚未發生
  - Known information:三前置 AND
  - Missing information:無
  - Human decision:upgrade 契約與等 F3，不是跟 hops
  - Authority:專案樹，不是 cache
  - External dependency:契約檔、站檔目錄
  - Out-of-system action:人改自己 repo 契約
  - Waiting/timeout behavior:無
  - Recovery:三前置全真才准評五站
  - Audit/handoff requirement:拒絕理由含前置名
  - Observation:見本條觀測

#### S-6.2 SC-DOCTOR：COMPATIBLE 不是通行證
- GIVEN 採用端契約仍 `2.0.0`；`devflow-doctor.sh` 可印 `COMPATIBLE` 且 exit 0
- WHEN coordinator 被求走五站 hop
- THEN 拒；拒絕理由是路線未宣告／仍舊 7，**不是**「doctor 已綠」。文案「doctor exit 0 所以可以跟 hops」仍紅（F1 S-5.6 回歸）
- 觀測:從 hop 拒絕理由與 F1 dual 牙看 | 理由不含「doctor 已綠」當許可；F1 S-5.6 對該文案仍紅算過 | 本 tree 可跑 doctor；`scripts/five_station_f1.py` L217–L224 仍咬文案
- Operational Context:
  - Actor:doctor 操作者／coordinator
  - Goal:綠只當握手
  - Situation:剛看到 COMPATIBLE
  - Known information:SLOT-DOCTOR-GREEN-MEANS
  - Missing information:人會不會把綠當切線
  - Human decision:不跟 hops
  - Authority:契約版本
  - External dependency:`devflow-doctor.sh`
  - Out-of-system action:人讀 doctor 一行
  - Waiting/timeout behavior:無
  - Recovery:把「綠所以 hop」當違規
  - Audit/handoff requirement:拒絕理由
  - Observation:見本條觀測

#### S-6.3 marketplace update 單獨 ≠ cut
- GIVEN 只做了 `marketplace update`／`plugin update`；契約未宣告 2.1.0
- WHEN 有人把 hops 當五站預設
- THEN 該組合違規（SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS）；路線仍舊 7
- 觀測:從路線判定看 | 未改線；2.0.0+五站 hops 紅算過 | n-a:採用假樹後站造。替代：F1 annex SLOT-UNDECLARED-ROUTE／SLOT-REJECT；本條
- Operational Context:不適用 — 與 S-6.2 同一路線閘；本條只換 marketplace 單獨發生。

#### S-6.4 plugin cache 只選碼不是路條
- GIVEN 同一 repo 兩台機器／兩個 host 各一份 plugin cache；A 機 hops 已是五站碼，B 機仍舊 7 碼；專案樹契約仍 2.0.0 且 slug in-flight
- WHEN 各 process 啟動 coordinator
- THEN 各 process 讀自己 cache 的 hops **碼**；路線仍認專案樹（2.1.0 ∧ ¬in-flight ∧ F3 cut）。不得因 A 機 hops 新就把 B 機舊 7 slug 遠端改線。不掃磁碟上「最新」的其他 cache
- 觀測:從兩 process 路線輸出看 | 兩路都是舊 7；cache 路徑不在「路線許可」欄算過 | n-a:多 cache 真機本 hop 不跑。替代：Decision 7A／OC-7；brief L168
- Operational Context:
  - Actor:採用 owner／兩台機器
  - Goal:不得遠端改線
  - Situation:多份 cache
  - Known information:cache ≠ cut
  - Missing information:哪台先 update
  - Human decision:認契約檔
  - Authority:專案樹
  - External dependency:各 host plugin cache
  - Out-of-system action:人核契約版本
  - Waiting/timeout behavior:無
  - Recovery:掃最新 cache 的實作 → 當 7B 紅
  - Audit/handoff requirement:路線理由含契約／in-flight／F3，不含 cache mtime
  - Observation:見本條觀測

#### S-6.5 契約 2.0.0 加五站 hops 預設仍舊 7
- GIVEN `devflow_contract_version`＝2.0.0 且方法包 hops 已是五站預設；兩源可不同時刻寫入
- WHEN 任一源先改或同窗寫入
- THEN 路線仍舊 7；F1 紅該組合；doctor 握手綠不得當仲裁
- 觀測:從契約版本與 hops 是否五站預設兩格 AND 看 | 任一寫入順序 → 仍舊 7 算過 | n-a:F1 牙已咬文案；F2 行為牙本 hop 不落地。替代：F1 S-5.7／S-5.9；本條
- Operational Context:不適用 — 與 S-6.2 同一閘；本條只換兩源並寫。

### R-7: 系統 SHALL 鎖死三把 Non-Goals

SC-KNIFE／8A。不做 F3 cut；不折 in-flight；不刪 G1／G2／`ACCEPTED` token 或檔。把其中一把標成「可選簡化」＝翻 Decision。

**審的時候看什麼**
F2 宣稱完成之後，新 slug 預設仍舊 7；in-flight 仍舊 7；token 仍在。

#### S-7.1 本刀不做 F3 cut
- GIVEN F2 落地（後站）或本 hop 宣稱範圍
- WHEN 人找「新 slug 預設五站」聲明（guide／STATUS 用語／`graph.yaml` 預設切線）
- THEN 找不到把新 slug 預設改五站的 cut；F0–F2 母版新軌仍舊 7
- 觀測:從 diff 與 guide／graph 看 | 無 F3 cut 聲明算過 | 本 hop `git diff --name-only origin/main` 不得出現 `graph.yaml` 或 guide 切五站
- Operational Context:不適用 — 刀範圍。

#### S-7.2 不把 in-flight 折成五站
- GIVEN 任一已有 1–7 `.md` 的 slug（含本目錄）
- WHEN F2 完成
- THEN 該 slug 仍舊 7；無五站狀態寫入
- 觀測:從 in-flight 目錄看 | 仍舊 7 算過 | 與 S-5.4／S-5.5 同一禁則；本條是刀鎖
- Operational Context:不適用 — Non-Goal 鎖。

#### S-7.3 不刪 G1／G2／ACCEPTED token 或檔
- GIVEN F2 完成前後
- WHEN 跑 token 檢查
- THEN G1／G2／`ACCEPTED` 檔與 token 仍在
- 觀測:從 `scripts/check-gate-tokens.sh` exit 看 | 綠算過 | 本 hop 不改 token 檔
- Operational Context:不適用 — token 凍結。

#### S-7.4 SC-KNIFE：F2 宣稱完成後三把鎖仍鎖
- GIVEN 有人標「F2 完成」
- WHEN 核對 (1) 新 slug 預設是否被改五站 (2) in-flight 是否被折 (3) token 是否被刪
- THEN 三項都否。任一被實作成「做了」→ F2 失敗，不是簡化成功
- 觀測:從 F2 完成宣稱後的檔集／預設路線看 | 三鎖仍在算過 | n-a:F2 碼未落地。替代：Decision SC-KNIFE；本檔 Out of Scope 1–3
- Operational Context:
  - Actor:F2 reviewer
  - Goal:不准併刀
  - Situation:有人想順便 cut
  - Known information:brief §7
  - Missing information:無
  - Human decision:另開 F3 刀
  - Authority:8B／8C 已拒
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:撤回 cut／折線／刪 token
  - Audit/handoff requirement:Non-Goals
  - Observation:見本條觀測

### R-8: 系統 SHALL 把本 hop 限在 4-spec 雙檔草稿

本 Stage 4 PR 只文件。`status: draft`。`verdict` 空。不發明 G2 PASS。審頁只准 `scripts/build-stage4-html.py --action`。Q9–Q24 去向已在本檔 Disposition。後站不得把 Q21／Q22／Q23 標可選。

**審的時候看什麼**
`git diff --name-only origin/main` 只有兩檔。頂欄 draft、verdict 空。

#### S-8.1 本 PR 只含 4-spec 雙檔且不發明 G2 PASS
- GIVEN 本 branch 相對 `origin/main`
- WHEN 跑 `git diff --name-only origin/main`
- THEN 輸出只含 `docs/dev/five-station-f2/4-spec.md` 與 `docs/dev/five-station-f2/4-spec.html`。零 `_templates/`、零 `graph.yaml`、零 `scripts/` 新牙、零 `STATUS.md`、零 `HISTORY.md`、零 `devflow-contract.json`。頂欄 `status: draft`、`verdict` 空。無 G2 PASS
- 觀測:從該指令 stdout 與本檔 frontmatter 看 | 兩檔、頂欄 draft、verdict 空算過 | 在本 branch 跑 `git diff --name-only origin/main`
- Operational Context:不適用 — 本 PR 檔集。

#### S-8.2 審頁必須由 stage4 builder 重生
- GIVEN 本目錄 `4-spec.md` 已改
- WHEN 產同名 html
- THEN 必須跑 `python3 scripts/build-stage4-html.py --action docs/dev/five-station-f2/4-spec.md`。不得手包 `_templates/html-shell.html`；不得把審頁塞進 `build-gate-twin.py` STAGES
- 觀測:從 html 檔頭／產檔指令看 | 本 hop html 由 stage4 builder 產出算過 | 在本 branch 重跑該指令後 `4-spec.html` 可解析 R/S
- Operational Context:不適用 — 產檔紀律。

#### S-8.3 Q9–Q24 每條有去向且 Q21／Q22／Q23 不可選
- GIVEN Stage 1 Q9–Q24 與本檔 Real-world Disposition
- WHEN 人掃 Disposition
- THEN Q9–Q24 各有去向；Q21／Q22／Q23 去向＝本方案處理且下落含 `S-`；後站把這三題標可選 → 擋本 slug G2
- 觀測:從 Disposition 表看 | 十六題（Q9–Q24）皆有列；Q21→S-5.1／S-5.2；Q22→S-2.2／S-2.3／S-2.4；Q23→S-3.1／S-3.5 算過 | 讀本檔 Real-world Disposition
- Operational Context:不適用 — 去向帳。

#### S-8.4 本 hop 不改模板／graph／STATUS／既有牙
- GIVEN 本 branch diff
- WHEN 列路徑
- THEN 不含 `_templates/`、各站 `graph.yaml`、`STATUS.md`、`HISTORY.md`、`scripts/five_station_f1.py`、`hooks/_doctor_impl.py`
- 觀測:從 `git diff --name-only origin/main` 看 | 上列路徑零命中算過 | 同 S-8.1 指令
- Operational Context:不適用 — 檔集禁則。

## MODIFIED Requirements

本 repo 無 `docs/specs/` living spec 條文可引。F1 已核的拒收謂詞與 dual-read SLOT **不改數字、不改 SLOT 語意**。本檔 ADDED 的是 F2 落點：倉在 slug 級、hop 謂詞含 Must-keep、五問紀錄、五桶觸發表、同一電池。

無本 hop 要落地的 MODIFIED 條文。

## REMOVED Requirements

無。不刪 G1／G2／`ACCEPTED` 檔或 token。不刪 F1 十二群。不刪七檔名。不刪 `agent-event` 1.1。

## 行為流程圖(R 級)

```
[R-1] 只在謂詞全真時 hop
  五跳各自評表 A B
  假則停修
  Ship 無自動前進
[R-2] Must-keep 紅則 fail-closed
  三失敗各自可紅
  注入壞行為該格紅
[R-3] 紀錄答得出五問
  hop latch cap 各一筆
  不鎖鍵 不 bump
[R-4] 五桶檔觸發 hop_id
  persist 0 後加一
  第三拒 新 run 不歸零
[R-5] 同一電池 NEW5 加 OLD7
  缺一路即非 0
  本目錄不是白老鼠
[R-6] 專案樹路線未開則拒評
  三前置
  doctor 綠不是通行證
[R-7] 三把 Non-Goals 鎖死
  不 F3 不折 不刪 token
[R-8] 本 hop 只 4-spec 雙檔
  draft 空 verdict
  builder 重生 html
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.4）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、Disposition／CASE 表、本目錄 freeze md、F1 牙回歸、doctor 握手。F2 coordinator／電池行為 S 的綠發生在後站落地之後，不在本 PR。S 數 >40（見確認紀錄）誠實記帳，不另切開新 slug。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-f2/4-spec.md` 後審頁可解析 R/S。不回歸改既有牙（本 hop 禁改 `scripts/`）。F1 十二群：`bash scripts/test-five-station-f1.sh` 仍可綠（回歸地板，不是 F2 完成）。
- 非功能：本 slug 自己仍走舊 7（S-5.7）。契約不 bump。`agent-event` 不 bump。
- 無 golden master（可見 hop 行為在 F2 碼落地後才變；本 hop 不改 runtime）。

### Stage 3 對帳

N/A。Decision：無 Stage 3 trigger → 不建 `3-prototype.md`、不另開 proto 桶（約束 14）。本目錄無 `3-prototype.md`。無 ACCEPTED 場景要對。無 skip OC（2-decision 無「Stage 3」+「跳過」同行）。下落：S-1.3、S-4.2。

## Out of Scope

- F2 coordinator／電池／slug 倉 **碼**落地（本檔定義必須滿足什麼；施工在後站）
- 選定 event／倉的 JSON 鍵名或 schema 版本號（約束 11）
- F3 cut／改新 slug 預設 `graph.yaml` 路線
- 把 in-flight 折成五站（含本目錄）
- 刪 G1／G2／`ACCEPTED` token 或檔
- 放寬 hop≤2／Decide≤1／Goal reopen≤1
- 拿本 slug 或 `five-station-simplify` 當 NEW5 白老鼠
- 把 run 級 `events.jsonl` 當 cap 倉
- 把 doctor 綠／marketplace update／他份 cache 當路線許可
- 把「檔在」或「F1 綠」當 F2 完成
- 本 hop 改 `STATUS.md`／`HISTORY.md`、發明 G2 PASS、合併、改 `_templates/`／`graph.yaml`／既有牙、bump 契約
- 七 stem 各一桶（B 線 2A）
- 改 `hooks/_doctor_impl.py`
- 獨立於 B／C：不讀不併他線 Stage 4 稿

## Diff Budget

本節是**估計**。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| `4-spec.md` | 1 | ≤1400 | 0 |
| `4-spec.html`（產檔器） | 1 | ≤1600（生成） | 0 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約 | 0 | 0 | 0 |

**G2 之後（F2 碼；不在本 PR）**［Assumption：入口檔名與倉路徑未鎖］

| 區塊 | 檔 | 行(非測試) | 行(測試) |
|---|---|---|---|
| coordinator 評謂詞／latch／cap | ≤4 | ≤400 | ≤200 |
| slug 級倉＋五問紀錄 | ≤3 | ≤250 | ≤150 |
| 同一電池 NEW5+OLD7 入口＋13 CASE | ≤3 | ≤200 | ≤400 |
| F1 牙接真計數（RP-9／10／11） | ≤2 | ≤80 | ≤80 |
| F3 cut／graph 切線 | 0（Out of Scope） | 0 | 0 |

測試與非測試分開估。電池若用突變補紅格，測試行可能到天真估法的 3 倍 —— 超支就停、判 L1/L2。

## Dependencies

- 已核 Decision `#330`＋Human G1 `#333`（OC-1…OC-12 ✅）。無新外部系統。
- F1 牙與 annex 已 G3 PASS：`scripts/five_station_f1.py`、`scripts/test-five-station-f1.sh`、`notes/design/five-station-simplify-f1-rp-min-set.md`、`notes/design/five-station-simplify-f1-dual-read-annex.md`。F2 接真計數，不替代十二群回歸。
- F2 碼依賴本檔 G2 人類 PASS 之後才准動 `scripts/` 新入口。
- F3 依賴 F2 電池綠。
- 不新增套件、不新增網路 capability。未經本節授權的新 capability 屬 7-review finding。
- 電池入口檔名與倉路徑：Decision 只鎖「同一 process、slug 級只增、五問可答」；具體檔名［Assumption］交 Stage 5。

## Design Boundary Contract(條件式;G2 一併審)

- Applicability: applicable
- Trigger(s): ①跨模組（coordinator × slug 倉 × F1 牙 × 採用端 hops／契約）⑤新增 hop／latch／cap 紀錄（slug ledger，不是 bump agent-event）⑦計數只增與 Goal+Decide 一次寫 ⑨Feature Risk = high ⑪五站狀態機與 latch／cap／Escalated 恢復
- Design source: `notes/design/five-station-simplify-brief-v3.md` §3–§7；`notes/design/five-station-simplify-f0-state-machine.md`；2-decision 1A+2C+3A+4A+5A+6A+7A+8A

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| 本檔 4-spec（契約） | 定義 hop 謂詞／Must-keep／五問／CASE／觸發表 | 本 slug md | 讀 1／2 過程檔、brief、狀態機、F1 annex | 改 living 契約句；鎖 JSON 鍵名 |
| F2 coordinator（後站） | 評表 A／B、Must-keep、cap、latch | slug 狀態 | 讀 brief §3、本檔 R-1／R-2／R-4／R-6 | 折 in-flight；代寫判定；用 doctor 綠當路條 |
| slug 級只增倉（後站） | 三 cap＋五問紀錄 | 該 slug | 被 coordinator 寫；被 RP-9／10／11 讀 | 住 `runs/<run_id>/`；reset |
| F1 scripts／annex | 回歸地板＋接真計數 | 母版 scripts | 讀倉數字（F2 後） | 本 hop 改牙；用字樣替代倉 |
| 既有 graph／token | 服務舊 7 + dual-read | 方法包 graph | 被 F3 改**新 slug 預設** | F2 改 graph；刪 token |
| 採用端 | 未 2.1.0 走舊 7 | 採用專案契約檔 | marketplace 換包 | 遠端在 2.0.0 改線 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| 自動前進評表 | 站檔＋Must-keep＋latch → hop 或停修 | 謂詞假 → 停；latch 真 → HumanWait | 評與 hop 同一決定；不得先 hop 再補完整度 | 舊 7 走 allow_legacy |
| 五問紀錄 | hop／latch／cap → 五格可指 | 缺一問 → 該事件未完成 | 與計數同壽命（slug 級） | 不 bump agent-event 1.1 |
| 三 cap | persist／重開 → 只增數字 | 超限 → Escalated | Goal+Decide 同一次 mutation；新 run 不得只成功清數字 | 舊 7 不套 |
| 路線三前置 | 契約版本 × in-flight × F3 cut → 准評或 legacy | 缺一 → 不建五站機 | 認專案樹，不認 cache mtime | 2.0.0 採用端 doctor 可繼續握手綠 |
| 同一電池 | NEW5 組＋OLD7 組 → 單一 exit | 缺一路 → 非 0 | 同一 process；兩腳本各綠 ≠ 過 | F1 十二群是回歸，不是本入口 |

兩筆寫入只成功一筆：Goal 計數寫入但 Decide 未寫 → NEW5-GOAL-2 失敗（S-4.7）。hop 已發生但五問缺格 → 該 hop 未完成（S-3.1）。cap 用盡後 reset 再 hop → X5（S-4.9）。

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| 本 4-spec | 可測契約 | Decision、F1 牙 | 只文件 | DD 待人審 | spec-gate C1–C9 |
| hop 謂詞評表（後站） | 表 A／B 全真才 hop | 站檔、Must-keep | Idle→…→Ship | 一假停修 | 具名 CASE NEW5-HOP-OK／PRED-STOP |
| slug 倉（後站） | 五桶＋Decide＋Goal | coordinator | 只增；persist=0 起 | 超限 Escalated | NEW5-CAP-3／RUN2 |
| 電池入口（後站） | 同一 process 兩路 | NEW5／OLD7 fixture | stdout＋exit | 缺一路非 0 | SC-BATTERY |
| Freeze 偵測 | md 在否 | 目錄 | in_flight bool | 裸 html 不凍 | `ls *.md`；OLD7-SELF |

### Design Constraints

- 必須:謂詞真立刻 hop；Must-keep 入謂詞；五問可答；五桶觸發表；同一電池 13 CASE；本 slug 舊 7
- 禁止:七 stem；run 級倉；doctor 綠當路條；檔在＝完；本 hop 改模板／graph／STATUS；Agent 代寫判定；減 CASE 列；極性反寫
- Extension point:Stage 5 選倉路徑與電池入口檔名；F1 牙加讀倉路徑
- Known design limit:本 hop 不落地 coordinator；倉路徑／入口檔名未鎖（鍵名 OPEN）；F1 RP-9／10／11 現行仍咬字樣，live 第三次要等 F2 接倉；多 cache 真機本 hop 不跑

## Verification Profile(G2 一併審)

- lane: full（判準:新能力、跨模組 coordinator／倉／採用端路線、狀態機、不可逆 cap。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:公開方法論 hop、權限／判定主權、採用端被改線、計數遺失＝暗改 cap、併發兩源更新。模板「公開 API／不可逆／併發／高風險人機互動」吃這條）
- Failure model:(Risk: high 必填,表見下)
- Negative constraints:
  - 不得謂詞真仍留下「要不要繼續」（S-2.3）
  - 不得 Must-keep 紅仍 hop 且把拒 hop 記成該格綠（S-2.2）
  - 不得機械綠當 Ship Done（S-2.4）
  - 不得用 run 級 events 當 cap 倉（S-4.9）
  - 不得七 stem 各一桶（S-4.3）
  - 不得減 13 CASE 或反極性（S-5.8）
  - 不得把本目錄當 NEW5（S-5.3、S-5.7）
  - 不得把 doctor 綠／cache／marketplace 當 cut（S-6.2、S-6.3、S-6.4）
  - 不得 F3 cut／折 in-flight／刪 token（S-7.4）
  - 不得本 hop 改 STATUS／模板／graph／scripts 牙／契約 bump（S-8.1、S-8.4）
  - 不得鎖 event 鍵名或 bump agent-event（S-3.5）
  - 不得發明 G2 PASS（S-8.1）
- Required layers:check-spec-gate（本 hop 形狀）。文件層：本 PR 檔集（S-8.1）、Disposition C9、CASE 13 列、stage4 builder 可解析 R/S
- Conditional layers:F2 碼落地 → 單一電池入口列入 Required 並重跑 13 CASE；改 RP-9／10／11 讀倉 → 重跑 F1 十二群＋NEW5-CAP-3／DECIDE-2／GOAL-2
- Explicitly excluded layers:Mutation（本 hop 只規格）、e2e／Playwright（無產品前端）、Windows 真機、本 hop 跑 coordinator（碼 Out of Scope）、掃全機 plugin cache
- Final fresh entry point:`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md && python3 scripts/build-stage4-html.py --action docs/dev/five-station-f2/4-spec.md`
- Reliability triage:
  - Concurrency: applicable — 契約版本與 marketplace hops 兩源可獨立寫；Goal+Decide 必須同一次 mutation。落到 S-6.5、S-4.7
  - Idempotency: applicable — 同一對照再評 freeze／doctor 綠≠通行證／本 PR 檔集，結果相同（S-5.7、S-6.2、S-8.1）
  - Timeout/retry: n-a — 機械檢查同步結束；HumanWait／Escalated 是 latch／cap 出口不是重試（S-1.6、S-4.5）

### Failure Model(Risk: high 必填)

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 謂詞真仍等人 | 舊痛留下 | 紀錄出現「要不要繼續」 | Required:S-2.3 | F2 碼落地前只文件對照 |
| Must-keep 紅仍 hop | 比舊 7 更快假完成 | NEW5-MK-RED 被洗成綠 | Required:S-2.2 | — |
| 機械綠當 Done | 偷 OC-3 | 無人 PASS 卻 Done | Required:S-2.4 | — |
| run 級倉當 cap | 新 run 歸零＝X5 | NEW5-RUN2 讀到 0 | Required:S-4.9 | — |
| 七 stem 稀釋 hop≤2 | 同站兩檔各 2 | 3-proto 與 4-spec 分桶 | Required:S-4.3 | — |
| 只跑 NEW5 或只跑 F1 | hollow F2 | 電池仍 0 | Required:S-5.1、S-5.2 | — |
| 本目錄當白老鼠 | 觀測被自己污染 | 五站狀態寫入本目錄 | Required:S-5.7 | — |
| doctor 綠冒充已切 | 採用端被改線 | 理由寫「doctor 已綠」 | Required:S-6.2 | — |
| 掃最新 cache | 遠端改線變種 | 未宣告 2.1.0 被拖進五站 | Required:S-6.4 | 真機多 cache 本 hop 不跑 |
| 併刀 F3／折線／刪 token | 新 brief | cut 聲明或 token 缺 | Required:S-7.4 | — |
| 本 hop 改 STATUS／模板 | 並行 session 互蓋 | diff 出現 STATUS 或 `_templates/` | Required:S-8.1 | — |
| 鎖鍵名或 bump schema | 採用端 doctor 誤紅 | agent-event 版本變 | Required:S-3.5 | — |
| RP-9 繼續只咬字樣 | live 第三次假第一次 | 倉未讀 | Required:S-4.5 | F2 接倉後才跑 |
| 審頁手包 | html 與 md 分叉 | 未跑 stage4 builder | Required:S-8.2 | — |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| 電池入口檔名交 Stage 5（Decision 只鎖同一 process） | F2-impl | open |
| slug 倉具體路徑／檔名交 Stage 5（只鎖 slug 級、只增、可指） | F2-impl | open |

兩列 deadline 不是曆日、不是已過站，C7 不紅。升格成已核鍵名仍擋（S-3.5）。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–8A。推翻 Decision 不是合法 DD。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | Decision SC＋13 CASE 收成 R-1…R-8；每條 CASE 至少一條 S（對照見 CASE → S 表） | A 線：謂詞／Must-keep／五問／觸發表／dual-path 可測 | `2-decision.md` Success Criteria 與「本方案要求」表 | 漏 CASE 或減列＝翻 Decision | 待人審 |
| DD-2 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 PASS | hop／cap／採用端改線／判定主權；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief | 改 normal 則 Failure Model 變選配；代填 PASS = 假綠 | 待人審 |
| DD-3 | 倉路徑與電池入口檔名不鎖；只鎖 slug 級只增、同一 process、五問可答 | Decision 約束 11；OC-2／OC-9 下層 | `2-decision.md` L308–L309 | 本檔鎖鍵名＝偷做 annex | 待人審 |
| DD-4 | 行為圖 8 框對 8 個 R；審頁產器硬切 8 框 | 產器 `steps[:8]`；不改 scripts | `scripts/build-stage4-html.py` L450 | 增 R-9 則圖丟框 | 待人審 |
| DD-5 | 無 Stage 3：0 trigger → 不建 3-prototype、不開 proto 桶；對帳 N/A | Decision 約束 14；使用者本 hop | `2-decision.md` L152；本 hop brief | 補 3-prototype＝違 0 trigger | 待人審 |
| DD-6 | S 數 >40 留在本檔、不另切開新 slug | 13 CASE＋五跳謂詞＋觸發表必須獨立 S | 本 hop A 線 brief；F1 4-spec 同判 | 切開＝漏 CASE 風險 | 待人審 |
| DD-7 | 獨立於 B／C；不讀不併他線 Stage 4 | 使用者：Independent of B/C | 本 hop brief | 併稿會把未核選擇寫進本檔 | 待人審 |
| DD-8 | 本 hop 不跑 status-update、不發明 G2 PASS | 與 Decision OC-10 對稱 | `2-decision.md` OC-10；本 hop brief | PR 帶 STATUS 或自填 PASS | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `STATUS.md`、不 bump plugin、不開 5-tasks。
- F1 字樣正則牙可留作回歸；不得替代 1A 倉。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- 負向 CASE fixture 目錄建議 `scripts/fixtures/five-station-f2/`（後站才新增檔）。

## Test Skeletons(選配)

- `test_s_1_1_intake_to_decide_four_predicates`
- `test_s_1_2_decide_to_spec_no_wait_g1`
- `test_s_1_3_spec_to_build_no_trigger_no_prototype`
- `test_s_1_4_spec_b1_hit_requires_attestation`
- `test_s_1_5_build_to_ship_four_fields`
- `test_s_1_6_ship_no_auto_advance`
- `test_s_1_7_new5_hop_ok_five_questions`
- `test_s_1_8_new5_pred_stop_no_continue_prompt`
- `test_s_2_1_must_keep_red_blocks_hop`
- `test_s_2_2_new5_mk_red_inject_polarity`
- `test_s_2_3_new5_wait_red_inject_mid_wait`
- `test_s_2_4_new5_ship_mech_inject_done`
- `test_s_2_5_must_keep_sixteen_rows_and_no_skip`
- `test_s_3_1_hop_record_answers_five_questions`
- `test_s_3_2_latch_record_answers_five_questions`
- `test_s_3_3_cap_record_answers_five_questions`
- `test_s_3_4_chat_status_not_hop_record`
- `test_s_3_5_slug_store_no_schema_bump_no_key_lock`
- `test_s_4_1_file_to_five_bucket_table`
- `test_s_4_2_same_bucket_no_proto_without_trigger`
- `test_s_4_3_seven_stem_buckets_rejected`
- `test_s_4_4_first_persist_zero_then_plus_one`
- `test_s_4_5_new5_cap_3_stays_two`
- `test_s_4_6_new5_decide_2_rejected`
- `test_s_4_7_new5_goal_2_same_mutation`
- `test_s_4_8_t_retry_not_hop_bucket`
- `test_s_4_9_new5_run2_counts_survive`
- `test_s_5_1_single_entry_missing_path_nonzero`
- `test_s_5_2_hollow_file_or_f1_or_new5_only`
- `test_s_5_3_new5_fixture_not_this_dir`
- `test_s_5_4_old7_no_five_state`
- `test_s_5_5_old7_fold_red_inject`
- `test_s_5_6_old7_tokens_and_f1_green`
- `test_s_5_7_old7_self_this_slug_blocked`
- `test_s_5_8_thirteen_case_add_only_polarity`
- `test_s_6_1_three_preconditions_allow_legacy`
- `test_s_6_2_doctor_green_is_not_permit`
- `test_s_6_3_marketplace_update_is_not_cut`
- `test_s_6_4_cache_selects_code_not_route`
- `test_s_6_5_contract_2_0_0_plus_five_hops_stays_old_7`
- `test_s_7_1_no_f3_cut`
- `test_s_7_2_no_inflight_fold`
- `test_s_7_3_tokens_remain`
- `test_s_7_4_sc_knife_after_f2_claimed_done`
- `test_s_8_1_this_pr_docs_only_draft`
- `test_s_8_2_html_via_stage4_builder`
- `test_s_8_3_q9_q24_disposition_q21_q23_required`
- `test_s_8_4_no_template_graph_status_teeth`

## 確認紀錄

- 接手盤點 | 2026-09-14 | G1 PASS（2-decision `approved`／`verdict` PASS／OC-1…12 ✅，#333；基準 #330 soft-fix＋#334 STATUS）。無 Stage 3：0 trigger → 不建 3-prototype。living `docs/specs/` 0 條。驗收雛形 AC-1…AC-10 + Decision SC 全表 + 13 CASE。
- 雙源清點 | 2026-09-14 | 雛形 10 條 + SC 19 條 + CASE 13 列 → ADDED R-1…R-8。living 0 條可引 → MODIFIED 無條文。REMOVED 無。
- R 範圍 | 2026-09-14 | Implementer A brief：hop 謂詞、Must-keep fail-closed、事件五問、CASE 全表映射、NEW5／OLD7、hop_id 觸發表當 S。使用者本指令 = 範圍確認。獨立於 B／C。
- S 展開 | 2026-09-14 | R-1…R-8 全展開；每 S 有觀測欄；交接／核准／等待／權限 S 有 Operational Context。
- SC／CASE 鏈 | 2026-09-14 | 完整表見「SC → S 對照」與「CASE → S 對照」。13 CASE 零減列。
- 3a 四節 | 2026-09-14 | AC／Out of Scope／Diff Budget／Dependencies 齊。
- 3b Profile | 2026-09-14 | lane full、Risk high、Failure Model、Reliability Concurrency=applicable（S-6.5、S-4.7）、DBC applicable。
- 3c Stage 3 | 2026-09-14 | N/A（0 trigger；無 3-prototype；下落 S-1.3、S-4.2）。
- DD 掃描 | 2026-09-14 | 上層八條待人審；無「待裁決」殘留；不翻已核 Decision。
- 機械關卡 | 2026-09-14 | `scripts/check-spec-gate.sh` 9/9。S＝48、R＝8。審頁 `scripts/build-stage4-html.py --action`。
