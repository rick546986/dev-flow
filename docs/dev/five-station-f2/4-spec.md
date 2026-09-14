---
feature: five-station-f2
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站 F2 change spec（Winner B + owner standing soft-fix）

> 基準:`origin/main`（G1 PASS after #333／#334）。Lane = **full**。契約不 bump。
> G1 已過。Stage 3：**無 trigger**（本刀 coordinator／slug 倉／電池，無新前端、無新互動方案）→ 不建 `3-prototype.md`、不另開 proto 桶。**本 hop 不送 G2**：頂欄 `status: draft`、`verdict` 空。不發明 PASS。
> 原文獨立於 A／C（B 線當時未讀他稿）。**本檔含 owner standing soft-fix**（#336 多數勝出後吸收，非 B 線當時已讀他稿）。
> B 線主軸全留：① RP-9／10／11 **讀 slug 倉真計數**（禁只咬 fixture「第 3 次」）；② marketplace×doctor **約束不是功能**；③ Q12 **第一次成功 persist＝0，其後 +1**；④ Spec／Build **同桶**（拒七 stem）；⑤ CASE 極性＝**注入壞行為 → 該格紅**。Decision 原 13 列只准加；入口＝`scripts/test-five-station-f2.sh`。
> Standing 必釘：M1–M16 去向＋**任一 Must-keep 紅 → 拒 hop**（不只 M11／T Verify）；NEW5-HOP-OK 用可解析謂詞表／逐 hop GWT（吸 A）；Verification Profile 寫 lane／Risk 判準句、F2 電池進 Conditional（Required 不得 unverified）、本 hop Final Fresh＝`check-spec-gate.sh` 一條；DBC Trigger 含 ⑨ Feature Risk=high；Out of Scope 三把鎖「後站不准改成 In」；hollow 三陷阱各一 S（吸 C）；Stage 5 Files 具名准許清單，F3／token／graph Diff Budget＝0 且有失敗 S（吸 C）。
> 本 PR **只** `4-spec.md` + `4-spec.html`。不改 STATUS／HISTORY／2-decision／模板／graph／scripts 牙／契約。不寫 coordinator 碼。

## 補助模組生命週期（預覽）

主詞是「F2 coordinator 的 slug 級只增倉 + 五桶觸發 + 雙路電池」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：slug 級只增倉、檔→五站五桶觸發表、F2 單一電池入口、CASE 注入紅格
- 改行為（相關一格）：RP-9／10／11 改讀 slug 倉；coordinator 先問專案樹三前置；marketplace×doctor 當約束
- 退役：沒有
- 不動：七檔名、G1／G2／`ACCEPTED` token、`graph.yaml`、doctor 實作、`agent-event` schema、本 slug 舊 7、F1 十二群牙

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「F1 已鎖 cap 數字與拒收謂詞,但計數落在哪、鍵叫什麼明文交給 F2」 | 本方案處理 | R-1、S-1.1、S-1.11、S-5.4 |
| 「現行牙只對 fixture 字樣『第 3 次』正則紅——沒有倉,第三次重寫在 live 裡可以假裝第一次」 | 本方案處理 | S-1.5、S-1.12、S-4.11 |
| 「若三個 cap 寫進 run 級 events.jsonl,新 run 歸零 = 暗改 cap(X5)」 | 本方案處理 | S-1.4、S-1.11 |
| 「marketplace update 換 hops,doctor 仍印 COMPATIBLE」 | 本方案處理 | R-3、S-3.1、S-3.2 |
| 「若後續 coordinator 把綠或我已在 plugin cache 當成切五站,舊 7 slug 會被折」 | 本方案處理 | S-3.1、S-3.6、S-7.2、S-7.4 |
| Journey「owner／寫手 chat『可以開下一站』」 | 本方案處理 | S-4.6、S-6.2 |
| Journey「live 第三次重寫假裝第一次」 | 本方案處理 | S-1.5、S-1.8、S-4.4 |
| Workaround「F1 用文案正則擋『doctor 綠所以跟 hops』；擋的是寫出來的謊,不是 coordinator 行為」 | 本方案處理 | S-3.1、S-3.4 |
| Workaround「STATUS／HISTORY 當 hop log」 | 本方案處理 | S-5.2 |
| Exception「舊 7 與 in-flight 不套三個 cap」 | 本方案處理 | S-7.4、S-1.10 |
| Exception「F2 可以寫 coordinator 碼,但 F3 前預設路線仍舊 7」 | 本方案處理 | S-7.1、S-8.1 |
| Exception「[Assumption] 把 cap 放進 run 級 events = X5」 | 本方案處理 | S-1.11 |
| Exception「[Assumption] dual-path 同一入口兩路都必須能獨立變紅」 | 本方案處理 | S-4.1、S-4.4、S-4.5、S-4.6、S-4.7 |
| Exception「[Assumption] NEW5 試體是合成 fixture,不是本 slug」 | 本方案處理 | S-7.7 |
| 「本 tree 搜過:沒有 F2 coordinator 實作檔」 | 本方案處理 | S-8.4 |
| Q9 三個計數器落點 | 本方案處理 | R-1、S-1.1 |
| Q10 run 級歸零是否 X5 | 本方案處理 | S-1.4、S-1.11 |
| Q11 hop_id 在 F3 前怎麼認 | 本方案處理 | R-2、S-2.1 |
| Q12 初寫 vs 重寫 | 本方案處理 | S-1.1、S-1.2、S-1.3、S-4.12 |
| Q13／Q14／Q18 事件怎麼接 × schema bump | 本方案處理 | R-5、S-5.3 |
| Q15 Goal 連帶 Decide 是否一次寫 | 本方案處理 | S-1.9 |
| Q16 T≤4 與 hop 重寫 | 本方案處理 | S-1.10 |
| Q17 三前置 | 本方案處理 | S-7.1 |
| Q19 RP-9／10／11 必須餵真計數 | 本方案處理 | S-1.5、S-1.6、S-1.7、S-1.12 |
| Q20 多份 plugin cache 認哪一份 | 本方案處理 | S-7.2、S-7.3 |
| Q21 F2 完是否=檔在或 F1 綠 | 本方案處理 | S-4.9、S-8.5、S-8.6、S-8.8 |
| Q22 三失敗不得當成功 | 本方案處理 | S-4.4、S-4.5、S-4.6、S-6.4、S-6.5 |
| Q23 事件五問、不鎖鍵 | 本方案處理 | S-5.1、S-5.4 |
| Q24 Backlog A 過期 | 刻意維持 | Out of Scope：本 PR 不改 STATUS／HISTORY |
| 「鎖:不刪 G1／G2／ACCEPTED；不做 F3 cut；不把 in-flight 折成五站」 | 本方案處理 | S-8.1、S-8.2、S-8.3、S-8.9 |
| M1–M16 帶走表 | 本方案處理 | S-6.5、S-6.6；Must-keep Disposition 16 列 |

## SC → S 對照

Decision Success Criteria 每條至少一條獨立可測 S。4-spec **只准加不准減** CASE 列。

| SC | 一句 | 本檔 S |
|---|---|---|
| SC-BATTERY | 單一入口；NEW5+OLD7 都過才 exit 0 | S-4.1 |
| SC-NEW5-HOP-OK | 謂詞表列全真、latch 假、Must-keep 綠 → hop；五問可答 | S-4.2、S-4.15、S-4.16、S-4.17、S-4.18、S-4.19、S-5.1 |
| SC-NEW5-PRED-STOP | 謂詞表任一列假 → 不 hop、停修、不留要不要繼續 | S-4.3、S-6.2 |
| SC-NEW5-CAP-3 | 第 3 次 hop 重寫拒；Escalated；拒後仍是 2 | S-1.5、S-1.8、S-4.4 |
| SC-NEW5-DECIDE-2 | 第 2 次 Decide 整站重開拒 | S-1.6 |
| SC-NEW5-GOAL-2 | 離開 Intake 後第 2 次 Goal 重開拒 | S-1.7、S-1.9 |
| SC-NEW5-MK-RED | 注入 Must-keep 紅仍 hop → 該格紅 | S-4.4、S-4.8、S-6.5 |
| SC-NEW5-SHIP-MECH | 注入機械綠無人 PASS 卻 Done → 該格紅 | S-4.5 |
| SC-NEW5-WAIT-RED | 注入謂詞真 latch 假仍等人 → 該格紅 | S-4.6 |
| SC-NEW5-RUN2 | 新 run_id 數字仍在、不是 0 | S-1.4 |
| SC-OLD7-NO-FIVE | 已有 1–7 `.md` → 無五站狀態；三 cap 不套 | S-7.4 |
| SC-OLD7-FOLD-RED | 注入對 in-flight 寫五站狀態 → 該格紅 | S-4.7 |
| SC-OLD7-TOKEN | token 與檔仍在；F1 牙回歸仍綠 | S-7.5、S-8.3 |
| SC-OLD7-SELF | 對本目錄求五站自動前進 → 跳不過 | S-7.6 |
| SC-DOCTOR | COMPATIBLE 時拒五站 hop；理由不是「doctor 已綠」 | S-3.1、S-3.4 |
| SC-KNIFE | 宣稱完成後無 F3 cut、不折、不刪 token | S-8.1、S-8.2、S-8.3、S-8.9 |
| SC-HOLLOW | 檔在／只 F1 綠／只 NEW5 綠 ≠ F2 綠 | S-4.9、S-8.5、S-8.6、S-8.8 |
| SC-Q-CARRY | Q9–Q24 皆有去向 | 本節 Disposition；S-8.7 |
| SC-PR | 本 Decision hop 只 2-decision 雙檔（已過）。**本 Stage 4 hop** 只 4-spec 雙檔、draft、無 G2 PASS | S-8.4 |

## CASE → S 對照（Decision 13 列只准加）

極性：標「→ 紅」＝**注入該壞行為**，該格必須獨立變紅。把「拒 hop」記成紅格綠＝極性反了，已拒。

| CASE | 路 | 紅／綠 | 本檔 S |
|---|---|---|---|
| NEW5-HOP-OK | NEW5 | 綠：合法 hop | S-4.2 |
| NEW5-PRED-STOP | NEW5 | 綠：合法停修 | S-4.3 |
| NEW5-CAP-3 | NEW5 | 綠：合法拒第 3 次 | S-1.5、S-1.8 |
| NEW5-DECIDE-2 | NEW5 | 綠：合法拒第 2 次 Decide | S-1.6 |
| NEW5-GOAL-2 | NEW5 | 綠：合法拒第 2 次 Goal | S-1.7 |
| NEW5-MK-RED | NEW5 | **注入** Must-keep 紅仍 hop → **該格紅** | S-4.4、S-4.8 |
| NEW5-SHIP-MECH | NEW5 | **注入** 機械綠無人 PASS 卻 Done → **該格紅** | S-4.5 |
| NEW5-WAIT-RED | NEW5 | **注入** 謂詞真 latch 假仍等人 → **該格紅** | S-4.6 |
| NEW5-RUN2 | NEW5 | 綠：新 run 數字仍在 | S-1.4 |
| OLD7-NO-FIVE | OLD7 | 綠：無五站寫入 | S-7.4 |
| OLD7-FOLD-RED | OLD7 | **注入** 對 in-flight 寫五站 → **該格紅** | S-4.7 |
| OLD7-TOKEN | OLD7 | 綠：token 在 | S-7.5 |
| OLD7-SELF | OLD7 | 綠：本目錄合法拒 | S-7.6 |
| NEW5-STORE-READ | NEW5 | **加列**：**注入** RP-9／10／11 只咬 fixture 字樣、不讀 1A 倉 → **該格紅** | S-1.12、S-4.11 |
| NEW5-SEVEN-STEM | NEW5 | **加列**：**注入** 七 stem 各一桶 → **該格紅** | S-2.4 |
| NEW5-SPEC-SHARE | NEW5 | **加列**：綠：`3-prototype` 與 `4-spec` 同 Spec 桶 | S-2.2、S-4.13 |
| NEW5-BUILD-SHARE | NEW5 | **加列**：綠：`5-tasks` 與 `6-notes` 同 Build 桶 | S-2.3、S-4.14 |
| NEW5-Q12-ZERO | NEW5 | **加列**：綠：第一次成功 persist＝0，不算進 hop≤2 | S-1.1、S-1.3、S-4.12 |

減 Decision 原 13 列任一列 = 翻 Decision。加列不得把「檔在」加成通過條件。

## Must-keep Disposition（M1–M16）

語法:`M11 → R-x/S-y | Non-Goal:<reason>`。不另發 ID 鏈。M15／M16 是**約束**，不是 Non-Goal。少任一 M = 違 brief，不得 hop（S-6.5）。不得只把 M11／T Verify 當完整度。

| M | 去向 | 下落 |
|---|---|---|
| M1 ID 鏈；測試名含 S-id | 本方案處理 | S-6.5；Build→Ship 測名含 S-id（S-4.19） |
| M2 資訊圍欄 | 本方案處理 | S-6.5；實作者只准讀 4-spec＋5-tasks＋6-notes＋CONTEXT＋living spec |
| M3 反模糊三律 | 本方案處理 | S-4.17、S-6.5；`check-spec-gate.sh` 形狀綠 |
| M4 Real-world → OC | 本方案處理 | S-4.15 I3；各 S Operational Context |
| M5 Human 主權；禁代填 PASS／ACCEPTED | 本方案處理 | S-4.5、S-6.3、S-6.5 |
| M6 G3 Evidence 八點 | 本方案處理 | S-6.3、S-6.5；機械綠 ≠ Ship Done |
| M7 Verification Profile + lane | 本方案處理 | S-4.17、S-6.5；`lane:`／`Risk:` 可解析 |
| M8 DBC | 本方案處理 | 本檔 DBC；S-6.5 |
| M9 Scope guard：Files ⊆ 5-tasks 聯集 | 本方案處理 | S-4.19、S-6.5、S-8.9 |
| M10 驗證五律 | 本方案處理 | S-6.5；無原始輸出 → 未完成、不得 hop |
| M11 T seam + 四欄 | 本方案處理 | S-6.1、S-6.5、S-4.4 |
| M12 author ≠ approver | 本方案處理 | S-4.19、S-6.5；reviewer＝implementer → 不 hop |
| M13 html 重生 | 本方案處理 | S-8.4；`scripts/build-stage4-html.py --action` |
| M14 不可逆才 Quiz | 刻意維持 | S-6.5；F2 不新開例行 Quiz；不可逆無 Quiz → 紅 |
| M15 token／檔仍在 | 本方案處理 | S-8.3、S-7.5；禁刪是約束 |
| M16 F0 不改 graph／既有牙 | 本方案處理 | S-2.7、S-8.9；禁改 graph／既有牙是約束 |

## NEW5 自動前進謂詞表（S-4.2 機讀；一列一謂詞）

Coordinator 讀本表，不讀「謂詞全真」四字。當下 hop 的列全真 ∧ 該 hop latch 列假 ∧ Must-keep M1–M16 綠 → 立刻 hop。任一列假 → 停該站修（S-4.3）。S5a 與 S5b 互斥：先評 Stage 3 trigger，再走其中一條。Ship **無**自動前進列。

| hop | 列 | 真條件（可解析） | latch | 假則 |
|---|---|---|---|---|
| Intake→Decide | I1 | `1-discussion.md` 存在且可解析 | A1／A2＝否 | 停 Intake |
| Intake→Decide | I2 | Open Questions 全數已解或明標 `[Assumption]` | A1／A2＝否 | 停 Intake |
| Intake→Decide | I3 | 有 `## Real-world Context`，或 brief 承認的 legacy 且標了 legacy | A1／A2＝否 | 停 Intake |
| Intake→Decide | I4 | A1／A2 生成謂詞若為真，則對應產檔器 exit 0 | A1／A2＝否 | 停 Intake |
| Decide→Spec | D1 | `2-decision.md` 存在 | A4＝否（不等 G1 `verdict:`） | 停 Decide |
| Decide→Spec | D2 | `## Decision` 非空 | A4＝否 | 停 Decide |
| Decide→Spec | D3 | Owner Calls／OC 全裁決，無「待裁決」字樣 | A4＝否 | 停 Decide |
| Decide→Spec | D4 | A3 自動前進謂詞真；A4 twin 已產或可產 | A4＝否 | 停 Decide |
| Spec→Build | Sp1 | `4-spec.md` 存在 | A6／A7＝否（不等 G2 `verdict:`） | 停 Spec |
| Spec→Build | Sp2 | 每個 S 有觀測欄；`lane:`／`Risk:` 可解析 | A6／A7＝否 | 停 Spec |
| Spec→Build | Sp3 | Drafting Decisions 無殘留「待裁決」 | A6／A7＝否 | 停 Spec |
| Spec→Build | Sp4 | `check-spec-gate.sh` 形狀綠 | A6／A7＝否 | 停 Spec |
| Spec→Build | Sp5a | B1 未命中：九條 trigger 全未命中，或已落檔全未勾＋n-a 原因 → A5 不建頁，本列視為真 | B1＝否 | 停 Spec |
| Spec→Build | Sp5b | B1 命中：`3-prototype.md` 在；Human verdict＝`ACCEPTED` 且有人類 attestation | B1＝是 → HumanWait | 不 hop |
| Spec→Build | Sp6 | B2 若命中：UI twin 已產 | — | 停 Spec |
| Build→Ship | Bu1 | `5-tasks.md` 在；每 T 有 Covers／Files／Verify／Blocked-by | A8／A9＝否 | 停 Build |
| Build→Ship | Bu2 | `6-implementation-notes.md` 在；每 T 獨立 review PASS 且 reviewer ≠ implementer | A8／A9＝否 | 停 Build |
| Build→Ship | Bu3 | 本次 S 全綠；Files ⊆ 5-tasks Files 聯集 | A8／A9＝否 | 停 Build |
| Build→Ship | Bu4 | Must-keep M1–M16 全綠（S-6.5） | A8／A9＝否 | 停 Build |
| Ship→Done | — | **無自動前進列**。機械綠仍 HumanWait | A10＝是 | 留 Ship |

## ADDED Requirements

### R-1: 系統 SHALL 把三個 cap 計數寫進 slug 級只增倉，且 RP-9／10／11 讀該倉

1A＋6A＋Q12。三計數器（`hop_rewrites[hop_id]`／`decide_reopen`／`goal_reopen`）住 slug 範圍、只增不減。某 `hop_id` **第一次成功 persist＝0**，其後每一次成功 persist 該桶 +1；第一次寫不算進 hop≤2。新 `run_id`／重開 process 之後數字仍在。RP-9／10／11 讀這倉的數字，不得只咬 fixture 正文「第 3 次」字樣。Goal 連帶回到 Decide 時兩個計數**同一次 mutation** 寫入。舊 7 走 `allow_legacy()` 不碰這倉。鍵名 OPEN（4-spec 只釘路徑形，見 DD-1）。

**審的時候看什麼**
倉是不是 slug 級、是不是只增。第一次 persist 之後該桶是不是 0。第三次重寫拒的時候牙讀的是倉裡的 2，不是稿子上的「第 3 次」。新 run 之後數字是不是還在。

#### S-1.1 第一次成功 persist 該 hop 桶＝0
- GIVEN NEW5 合成 fixture 的某 `hop_id`（例：Spec）在 slug 倉尚無任何成功 persist
- WHEN coordinator 第一次成功 persist 該 hop 的寫入
- THEN 該 hop 桶數字＝0；倉內可指出這次 persist；第一次寫不算進 hop≤2（仍准再重寫 2 次）
- 觀測:從該 slug 倉（路徑形見 DD-1）讀該 hop 桶 | 數字＝0、有一筆可指 persist 算過 | n-a:F2 碼未落地。替代：本條與 Decision 約束 6 字面；電池落地後 CASE NEW5-Q12-ZERO
- Operational Context:不適用 — 計數寫入，無新的現場交接。

#### S-1.2 其後每一次成功 persist 該桶 +1
- GIVEN 同一 NEW5 slug 的 Spec 桶已因第一次 persist＝0
- WHEN coordinator 第二次成功 persist Spec（重寫 `4-spec.md` 或同桶 `3-prototype.md`）
- THEN Spec 桶數字＝1；第三次成功 persist 後＝2
- 觀測:從同一 slug 倉連續讀 Spec 桶 | 序列 0→1→2 算過 | n-a:F2 未落地。替代：Decision 約束 6；狀態機 `:L129`
- Operational Context:不適用 — 同 S-1.1。

#### S-1.3 第一次寫不算進 hop≤2
- GIVEN NEW5 slug 的 Spec 桶＝0（僅初寫）
- WHEN 有人把「已經寫過一次所以 hop cap 用掉 1」當成拒下一次重寫的理由
- THEN 下一次重寫仍被允許；拒點仍是「已重寫 2 次之後的第 3 次重寫」
- 觀測:從 hop 拒絕輸出與倉數字看 | 桶＝0 時重寫不被 hop≤2 拒；桶＝2 時第 3 次重寫才拒算過 | n-a:F2 未落地。替代：狀態機 `:L129`「第一次寫不算」
- Operational Context:不適用 — cap 算術。

#### S-1.4 新 run_id 再讀數字仍在（NEW5-RUN2）
- GIVEN NEW5 slug 的 Spec 桶已＝1、`decide_reopen`＝0、`goal_reopen`＝0
- WHEN 另開新 `run_id`（新 process）再讀同一 slug 倉
- THEN 三個數字仍是 1／0／0，不是 0／0／0；不得讀 `.devflow/runs/<新run_id>/coordinator/events.jsonl` 當 cap 正本
- 觀測:從 slug 倉跨兩個 `run_id` 讀 | 數字未被新 run 清掉算過 | n-a:F2 未落地。替代：Decision SC-NEW5-RUN2；1-discussion AC-1
- Operational Context:不適用 — 倉壽命，無人員交接。

#### S-1.5 RP-9 讀倉：第 3 次 hop 重寫拒（NEW5-CAP-3）
- GIVEN NEW5 slug 同一 `hop_id` 已成功 persist 到桶＝2（初寫 0 + 兩次重寫）；倉外另有一份 fixture 正文**沒有**「第 3 次」字樣
- WHEN 第 3 次重寫被要求執行
- THEN 被拒；狀態＝Escalated；拒後該桶仍是 2；RP-9 紅的依據是倉裡的 2，不是 fixture 字樣
- 觀測:從拒絕理由 + slug 倉數字 + RP-9 輸出看 | 第 3 次未 hop、數字仍 2、理由含倉計數算過 | n-a:F2 未落地。替代：對照 `scripts/five_station_f1.py` L327-L333 現行只咬字樣；本條要求改讀倉
- Operational Context:
  - Actor:coordinator／F2 牙
  - Goal:live 第三次重寫看得見
  - Situation:倉＝2，fixture 可能沒有「第 3 次」
  - Known information:hop≤2；只增不減
  - Missing information:寫手會不會改 fixture 字樣來躲牙
  - Human decision:Escalated 之後由人明示下一手
  - Authority:Agent 不得 reset 計數再 hop
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:Escalated 等人；不得暗改 cap
  - Recovery:人明示修 brief／放行一次／停；禁止把數字改小
  - Audit/handoff requirement:拒絕理由可指到倉
  - Observation:見本條觀測

#### S-1.6 RP-10 讀倉：第 2 次 Decide 整站重開拒（NEW5-DECIDE-2）
- GIVEN NEW5 slug 已 hop 出 Decide 一次；`decide_reopen`＝0；倉外 fixture 正文沒有「Decide 重開第 2」字樣
- WHEN 第 2 次 Decide 整站重開被要求執行
- THEN 被拒；`decide_reopen` 在拒前的寫入後為 1 或維持「已用盡」且不得被改小；站內尚未 hop 出的小改不算一次
- 觀測:從拒絕理由 + slug 倉 `decide_reopen` 看 | 第 2 次整站重開未成、牙讀倉不算字樣算過 | n-a:F2 未落地。替代：RP-10；狀態機 `:L130`
- Operational Context:不適用 — 同 cap 讀倉，無新交接。

#### S-1.7 RP-11 讀倉：離開 Intake 後第 2 次 Goal 重開拒（NEW5-GOAL-2）
- GIVEN NEW5 slug 已 hop 出 Intake；`goal_reopen`＝0；已用過 Decide 那 1 次重開
- WHEN 第 2 次 Goal 重開（改 Intake 目標／Success Criteria）被要求執行
- THEN 被拒；可同時用盡 Decide cap；RP-11 讀倉，不讀 fixture「Goal 重開第 2」字樣
- 觀測:從拒絕理由 + `goal_reopen`／`decide_reopen` 倉數字看 | 第 2 次 Goal 未成、Decide 不得被躲掉算過 | n-a:F2 未落地。替代：RP-11；狀態機 `:L137`
- Operational Context:不適用 — 同 cap 讀倉。

#### S-1.8 拒後計數仍是 2（無人手改小、無 reset）
- GIVEN S-1.5 的拒已發生；Spec 桶＝2
- WHEN 同一 process 或新 `run_id` 再讀該桶，或有人嘗試把數字改成 0 再 hop
- THEN 數字仍是 2；reset 再 hop＝X5，必須被拒
- 觀測:從倉連續讀 + 對 reset 再 hop 的拒絕看 | 數字不減、reset hop 被拒算過 | n-a:F2 未落地。替代：狀態機 X5 `:L198`
- Operational Context:不適用 — 只增不減。

#### S-1.9 Goal+Decide 兩個計數同一次 mutation 寫入
- GIVEN NEW5 slug 已 hop 出 Intake 與 Decide；Goal reopen 會連帶回到 Decide
- WHEN 一次 Goal reopen 寫入發生
- THEN `goal_reopen` 與因此觸發的 `decide_reopen` 在**同一 mutation** 寫入；不得先寫 Goal 成功、Decide 漏寫而讓 NEW5-GOAL-2 綠、Decide cap 被躲
- 觀測:從倉的單次寫入邊界（同一 persist 交易／同一 append 批次）看 | 兩計數同進或同失敗算過 | n-a:F2 未落地。替代：Decision OC-8；狀態機 `:L137`
- Operational Context:不適用 — 寫入原子性。

#### S-1.10 T 嘗試 ≤4 不與 hop 桶混算，除非整站重寫 Build
- GIVEN NEW5 slug 在 Build；某 T 重做第 2 次（該 T 嘗試計數＝2）；`5-tasks.md`／`6-implementation-notes.md` 未被整站重寫
- WHEN 該 T 再重做（仍 ≤4）
- THEN Build hop 桶**不**因此 +1；該 T 吃既有嘗試上限 4。僅當整份 `5-tasks.md` 或 `6-implementation-notes.md` 被整站重寫時，Build 桶 +1（兩檔同桶，不是兩個 stem 桶）
- 觀測:從 Build 桶與該 T 嘗試計數並列看 | T 重做時 hop 桶不動；整站重寫才 +1 算過 | n-a:F2 未落地。替代：狀態機 `:L107-L108`；Decision 約束 5
- Operational Context:不適用 — 兩套上限分家。

#### S-1.11 cap 正本不得是 run 級 events.jsonl
- GIVEN 現行 run ledger 路徑為 `.devflow/runs/<run_id>/coordinator/events.jsonl`
- WHEN F2 落地後有人把三個 cap 只寫進該 run 檔、不寫 slug 倉
- THEN 該做法＝1B，已拒；SC-NEW5-RUN2 必須失敗（新 run 讀空檔＝0）
- 觀測:從 cap 讀取路徑看 | 正本路徑不在 `runs/<run_id>/` 底下算過 | 現況 `observability/devflow_obs/ledger.py` L3-L6 證明 run 級存在；本條禁把它當 cap 倉
- Operational Context:不適用 — 倉選址。

#### S-1.12 只咬 fixture 字樣＝6C，電池該格紅（NEW5-STORE-READ）
- GIVEN NEW5 slug 倉 Spec＝2；對照稿**刪掉**「第 3 次」字樣；RP-9 若仍只跑 `five_station_f1.py` 正則
- WHEN 電池跑 NEW5-STORE-READ：第 3 次重寫 + 只餵字樣牙、不讀倉
- THEN **該格獨立變紅**（預期紅）。字樣牙綠不得標本格綠，也不得標 F2 成功
- 觀測:從電池該 CASE 的獨立 exit／紅標看 | 不讀倉的路徑紅；讀倉拒第 3 次的路徑才是 NEW5-CAP-3 綠算過 | n-a:電池未落地。替代：Decision 6C 棄因；`five_station_f1.py` L327-L333
- Operational Context:不適用 — 牙接線。

### R-2: 系統 SHALL 用五站桶觸發表，且 Spec／Build 同桶

3A。`hop_id` ∈ {Intake, Decide, Spec, Build, Ship}。`3-prototype.md` 與 `4-spec.md` → **同一 Spec 桶**。`5-tasks.md` 與 `6-implementation-notes.md` → **同一 Build 桶**。無 Stage 3 trigger → 不建 `3-prototype`、也不另開 proto 桶。禁止七個 stem 各一桶。舊節點 `N7-g1`／`N6-g2` 不是 hop_id。F2 不改 `graph.yaml`。

**審的時候看什麼**
寫 `4-spec.md` 與寫 `3-prototype.md` 是不是加同一個數字。七 stem 會不會把 hop≤2 變成七個 2。

#### S-2.1 hop_id 只有五個站名
- GIVEN F2 coordinator 要寫入五站倉
- WHEN 寫入一筆 hop 紀錄
- THEN `hop_id` 只准是 Intake／Decide／Spec／Build／Ship 五字之一；不得寫 `N7-g1`／`N6-g2`／七個 md stem
- 觀測:從倉／紀錄裡的 hop 識別看 | 集合＝五站名算過 | n-a:F2 未落地。替代：Decision 約束 14 表
- Operational Context:不適用 — 識別字面。

#### S-2.2 3-prototype 與 4-spec 同一 Spec 桶（NEW5-SPEC-SHARE）
- GIVEN NEW5 slug 無 Stage 3 trigger 時只有 `4-spec.md`；另造一條命中 B1 的 NEW5，已有 `3-prototype.md` 第一次 persist（Spec＝0）
- WHEN 同一 slug 再成功 persist `4-spec.md`
- THEN Spec 桶＝1（不是另開一個 4-spec 桶＝0）；兩次寫入可在同一桶指出
- 觀測:從 Spec 桶數字看 | 兩檔共享一個 ≤2 算過 | n-a:F2 未落地。替代：Decision 約束 14 列 `3-prototype.md`／`4-spec.md`
- Operational Context:不適用 — 分桶。

#### S-2.3 5-tasks 與 6-notes 同一 Build 桶（NEW5-BUILD-SHARE）
- GIVEN NEW5 slug `5-tasks.md` 第一次 persist（Build＝0）
- WHEN 同一 slug 再成功 persist `6-implementation-notes.md`（非整站重寫以外的「整份檔第一次寫」仍是同桶的下一次 persist）
- THEN Build 桶＝1；不是 `5-tasks` 桶 0 加 `6-notes` 桶 0
- 觀測:從 Build 桶數字看 | 兩檔共享一個 ≤2 算過 | n-a:F2 未落地。替代：Decision 約束 14
- Operational Context:不適用 — 分桶。

#### S-2.4 注入七 stem 各一桶 → 該格紅（NEW5-SEVEN-STEM）
- GIVEN 電池 CASE NEW5-SEVEN-STEM
- WHEN **注入**「`3-prototype`／`4-spec`／`5-tasks`／`6-notes` 各一桶、各 ≤2」
- THEN **該格獨立變紅**。七 stem 會把 hop≤2 稀釋成七個獨立 2。不得把「coordinator 拒寫七 stem」記成此格綠
- 觀測:從該 CASE 獨立紅標看 | 注入七 stem 行為紅算過 | n-a:電池未落地。替代：Decision Rejected「七 stem 各一桶」
- Operational Context:不適用 — 極性與分桶。

#### S-2.5 無 Stage 3 trigger 不建 proto 桶
- GIVEN NEW5 純守衛 feat：九條 trigger 全未命中
- WHEN coordinator 評 Spec
- THEN 不建 `3-prototype.md`；不另開 proto／Stage3 桶；Spec 只由 `4-spec.md` 觸發
- 觀測:從目錄與 hop 桶名看 | 無 `3-prototype.md`、無第三個中間桶算過 | n-a:F2 未落地。替代：Decision 約束 14 末段
- Operational Context:不適用 — 本 hop Stage 3 對帳 N/A 同源。

#### S-2.6 舊 graph 節點不是 hop_id
- GIVEN 舊 7 graph 仍有 `N7-g1`／`N6-g2`
- WHEN coordinator 寫五站倉
- THEN 不得把這兩個節點名當成 `hop_id`；in-flight 與 NEW5 不得共用舊節點 id 污染計數
- 觀測:從倉 hop_id 字面看 | 不含 `N7-g1`／`N6-g2` 算過 | 現況 `skills/dev-flow/stage2/graph.yaml` 仍經 N7-g1；本條禁冒充
- Operational Context:不適用 — 識別隔離。

#### S-2.7 F2 不改 graph.yaml
- GIVEN 本刀範圍＝coordinator + slug 倉 + 電池
- WHEN F2 宣稱完成
- THEN `git diff` 對各站 `graph.yaml` 為空（相對 F2 開工點）；不得另寫一份五站 graph
- 觀測:從 F2 實作 PR 的 `git diff --name-only` 看 | 無 `skills/dev-flow/stage*/graph.yaml` 算過 | 本 Stage 4 hop 亦不改 graph
- Operational Context:不適用 — 檔集。

### R-3: 系統 SHALL 把 marketplace × doctor 誠實當約束不是功能

4A。`doctor COMPATIBLE`／exit 0 只證明握手（`2.0.0 ∈ supported`），≠ 路線沒變、≠ 已切五站。`marketplace update` 單獨 ≠ cut。本刀不改 `hooks/_doctor_impl.py`、不改 marketplace。「我已在 plugin cache」不是第四條前置。

**審的時候看什麼**
綠的那行有沒有被拿來當 hop 通行證。拒絕理由寫的是「未宣告 2.1.0／仍舊 7」，不是「doctor 已綠」。

#### S-3.1 COMPATIBLE 時拒五站 hop（SC-DOCTOR）
- GIVEN 契約仍 `2.0.0`；`devflow-doctor.sh` 印 `COMPATIBLE` 且 exit 0
- WHEN coordinator 被求對 live slug 走五站 hop
- THEN 拒絕；拒絕理由字面含「路線未宣告」或「仍舊 7」；理由**不含**「doctor 已綠所以可 hop」
- 觀測:從該次 hop 拒絕 stdout／紀錄看 | 理由是路線，不是握手綠算過 | 本 tree 現況：`devflow-contract.json` 2.0.0 + doctor 可綠
- Operational Context:
  - Actor:採用 owner／doctor 操作者
  - Goal:綠≠切線
  - Situation:剛跑完 doctor、看到 COMPATIBLE
  - Known information:綠＝`2.0.0 ∈ supported`
  - Missing information:人會不會把綠讀成「可以跟 hops」
  - Human decision:要切線必須宣告 2.1.0 且 F3 cut 已發生
  - Authority:coordinator 禁用綠當路條
  - External dependency:採用端契約檔
  - Out-of-system action:人跑 doctor
  - Waiting/timeout behavior:無
  - Recovery:宣告 2.1.0 之前維持舊 7
  - Audit/handoff requirement:拒絕理由可核對
  - Observation:見本條觀測

#### S-3.2 marketplace update 單獨 ≠ cut
- GIVEN 採用端只做了 `marketplace update`（或同等 plugin cache 換 hops）；契約未宣告 2.1.0
- WHEN 有人把 hops 當五站預設
- THEN 該組合被看成違規；路線仍舊 7
- 觀測:從路線判定看 | 未改線；2.0.0+五站 hops 紅算過 | n-a:採用假樹後造。替代：F1 SLOT-UNDECLARED-ROUTE／SLOT-REJECT；Decision SC-DOCTOR 第二句
- Operational Context:
  - Actor:採用 owner
  - Goal:更新 plugin 後不被遠端改線
  - Situation:hops 已換、契約未動
  - Known information:marketplace 單一 entry `./`
  - Missing information:契約何時 bump
  - Human decision:未宣告 2.1.0 之前當舊 7
  - Authority:update ≠ cut
  - External dependency:plugin cache
  - Out-of-system action:`marketplace update`
  - Waiting/timeout behavior:無
  - Recovery:補宣告或把 hops 當違規
  - Audit/handoff requirement:路線判定可核對
  - Observation:見本條觀測

#### S-3.3 2.0.0 + 五站 hops 預設＝違規
- GIVEN 契約寫 `2.0.0`；host plugin 的 hops 已是五站預設
- WHEN coordinator 評路線
- THEN 判定＝違規；不得改線；NEW5 只打合成 fixture，不得把 live slug 切五站
- 觀測:從路線判定 + F1 SLOT-REJECT 回歸看 | 違規、不改線算過 | F1 牙 `scripts/five_station_f1.py` S-5.5／S-5.6 仍綠於文案；本條加行為
- Operational Context:不適用 — 同 S-3.2 的判定核對。

#### S-3.4 「doctor exit 0 所以可以跟 hops」文案仍紅
- GIVEN F1 對照稿含「doctor exit 0 所以可以跟 hops」或同等句
- WHEN 跑 `scripts/test-five-station-f1.sh`（或 `five_station_f1.py` 對該稿）
- THEN 該文案仍紅（F1 S-5.6 回歸）。F2 不得把這條回歸關掉來換 coordinator 綠
- 觀測:從 F1 十二群該案輸出看 | 文案牙仍紅算過 | 現況 `scripts/five_station_f1.py` L217-L224
- Operational Context:不適用 — 回歸地板。

#### S-3.5 本刀不改 doctor、不改 marketplace
- GIVEN F2 實作 PR
- WHEN 看 `git diff --name-only`
- THEN 不含 `hooks/_doctor_impl.py`、不含 marketplace 清單被改成「綠＝切線」
- 觀測:從該 PR 檔集看 | 兩路檔未改語意算過 | 本 Stage 4 hop 亦不改那兩路
- Operational Context:不適用 — 檔集約束。

#### S-3.6 「我已在 plugin cache」不是第四條前置
- GIVEN 三前置為：契約已宣告 2.1.0 ∧ 非 in-flight ∧ F3 cut 已發生
- WHEN 有人只證明「本 process 的 plugin cache 已有五站 hops 碼」
- THEN 仍 `allow_legacy()`；cache 不是第四條
- 觀測:從路線閘輸入看 | 缺任一前置仍舊 7；cache 位址不構成放行算過 | n-a:F2 未落地。替代：Decision 4A「也不是第四條」
- Operational Context:不適用 — 前置清單。

### R-4: 系統 SHALL 用同一電池跑 NEW5+OLD7，且 CASE 極性＝注入壞行為該格紅

5A＋約束 15。單一入口（DD-2）。缺一路、跳過一路、只轉呼叫 `test-five-station-f1.sh`、只證明檔在 → 整電池非 0。標「→ 紅」的列＝注入該壞行為，該格必須獨立變紅。

**審的時候看什麼**
紅格是不是真的餵了壞行為。有沒有把「coordinator 拒 hop」偷偷記成紅格綠。缺 OLD7 能不能整電池綠。

#### S-4.1 單一入口；缺一路即非 0（SC-BATTERY）
- GIVEN 入口檔為 `scripts/test-five-station-f2.sh`（DD-2）；NEW5 組與 OLD7 組皆已實作
- WHEN (a) 兩組都過；(b) 只跑 NEW5；(c) 只跑 OLD7；(d) 入口只 exec `scripts/test-five-station-f1.sh`
- THEN (a) exit 0；(b)(c)(d) 皆非 0。兩支互不認識的腳本各綠一次 ≠ dual-path
- 觀測:從該入口原始 stdout／exit 看 | 四格對上表算過 | n-a:入口未落地。替代：Decision SC-BATTERY 字面
- Operational Context:不適用 — 電池入口。

#### S-4.2 NEW5-HOP-OK 綠
- GIVEN NEW5 合成 fixture（路徑見 DD-3，不是本目錄、不是 `five-station-simplify`）；三前置全真；當下 hop 在「NEW5 自動前進謂詞表」的列全真（Intake→Decide＝I1–I4；Decide→Spec＝D1–D4；Spec→Build 無 trigger＝Sp1–Sp4＋Sp5a＋Sp6；Build→Ship＝Bu1–Bu4；依當下 hop 選一組）；該 hop 的 latch 列全假；Must-keep M1–M16 全綠（S-6.5）；該 hop 桶 < 2
- WHEN 電池跑 NEW5-HOP-OK
- THEN 發生 hop；人指得到一筆紀錄且五問有答；此格為**綠格**（合法行為應發生）。不得用「謂詞全真」四字替代上表列
- 觀測:從 hop 紀錄 + 該 CASE 綠標 + 謂詞表列對照看 | hop 發生、五問有答、此格綠、紀錄可指到當下 hop 的表列算過 | n-a:F2 未落地。替代：Decision SC-NEW5-HOP-OK；本檔謂詞表；S-4.15–S-4.19
- Operational Context:
  - Actor:coordinator
  - Goal:表列真立刻 hop
  - Situation:latch 未命中
  - Known information:本檔 NEW5 自動前進謂詞表
  - Missing information:無
  - Human decision:中間不簽
  - Authority:coordinator 禁問要不要繼續
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:中間不停
  - Recovery:任一表列假改走 S-4.3
  - Audit/handoff requirement:紀錄答五問並指出哪幾列為真
  - Observation:見本條觀測

#### S-4.3 NEW5-PRED-STOP 綠
- GIVEN NEW5：至少一條自動前進謂詞假（例：某 S 缺觀測欄，或 OC 未裁）
- WHEN 電池跑 NEW5-PRED-STOP
- THEN 不 hop；理由含該謂詞假；無「要不要繼續／請人審／確認一下」；此格綠（合法停修）
- 觀測:從停點理由 + 該 CASE 綠標看 | 不 hop、無等人句算過 | n-a:F2 未落地。替代：Decision SC-NEW5-PRED-STOP
- Operational Context:
  - Actor:寫手
  - Goal:假謂詞就修檔
  - Situation:形狀或 OC 未齊
  - Known information:哪一列假
  - Missing information:owner 會不會口頭放行
  - Human decision:修該列，不口頭繞
  - Authority:coordinator 禁改問人
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停在該站直到謂詞真
  - Recovery:補欄或補裁後重評
  - Audit/handoff requirement:停修理由留下
  - Observation:見本條觀測

#### S-4.4 注入 Must-keep 紅仍 hop → 該格紅（NEW5-MK-RED）
- GIVEN 電池 CASE NEW5-MK-RED；對照物為「任一 Must-keep（M1–M16）紅仍 hop」。例：T 缺 Verify（M11）；等價例：缺 ID 鏈（M1）、缺觀測欄（M3）、reviewer＝implementer（M12）
- WHEN **注入**該壞行為（不是注入「coordinator 拒 hop」）
- THEN **該格獨立變紅**。把「coordinator 拒 hop」記成此格綠＝極性反了，已拒。不得標 F2 成功。只測 M11、放過其餘 M 紅仍 hop＝本條紅
- 觀測:從該 CASE 獨立紅標看 | 注入壞行為紅；拒 hop 不得當此格綠；M1–M16 任一紅仍 hop 都算本格紅算過 | n-a:電池未落地。替代：Decision 約束 15；SC-NEW5-MK-RED；S-6.5
- Operational Context:不適用 — 測法極性，無新交接。

#### S-4.5 注入機械綠無人 PASS 卻 Done → 該格紅（NEW5-SHIP-MECH）
- GIVEN NEW5 已有 `7-review.md`；機械項全綠；頂欄 `verdict:` 空白
- WHEN **注入**「標 Ship Done／狀態 Done」
- THEN **該格獨立變紅**。合法行為是進 HumanWait，那是綠格義務，不是本紅格
- 觀測:從該 CASE 紅標 + 狀態不是 Done 看 | 注入 Done 紅算過 | n-a:F2 未落地。替代：狀態機 `:L119-L120`；RP-8
- Operational Context:
  - Actor:Ship 審查者
  - Goal:出貨仍由人寫頂欄
  - Situation:機械全綠
  - Known information:A10 latch＝是
  - Missing information:人是否讀完 Evidence
  - Human decision:寫 PASS／REQUEST_CHANGES／HOLD
  - Authority:只有人寫 md 頂欄
  - External dependency:無
  - Out-of-system action:人打開出貨審頁
  - Waiting/timeout behavior:停到人寫；無逾時自動 Done
  - Recovery:HOLD 留 Ship
  - Audit/handoff requirement:正本＝頂欄
  - Observation:見本條觀測

#### S-4.6 注入謂詞真 latch 假仍等人 → 該格紅（NEW5-WAIT-RED）
- GIVEN NEW5：當下 hop 的謂詞表列全真（S-4.2 表）、latch 假
- WHEN **注入**留下「要不要繼續／請人審／確認一下」
- THEN **該格獨立變紅**。中途等人不是客氣。合法立刻 hop 是 NEW5-HOP-OK 綠格
- 觀測:從該 CASE 紅標 + 前進紀錄字面看 | 注入等人句紅算過 | n-a:F2 未落地。替代：Decision 約束 8；RP-14
- Operational Context:
  - Actor:coordinator／寫手
  - Goal:中間不等
  - Situation:latch 未命中
  - Known information:A4／A7 latch＝否
  - Missing information:人會不會要求順便問
  - Human decision:不在中間簽
  - Authority:禁問要不要繼續
  - External dependency:無
  - Out-of-system action:不准把 twin URL 當「請簽」
  - Waiting/timeout behavior:中間不停
  - Recovery:刪問人紀錄後重評
  - Audit/handoff requirement:前進紀錄可核對
  - Observation:見本條觀測

#### S-4.7 注入對 in-flight 寫五站 → 該格紅（OLD7-FOLD-RED）
- GIVEN OLD7 fixture 已有 1–7 `.md`
- WHEN **注入**對該 fixture 寫五站狀態或五站 hop
- THEN **該格獨立變紅**（RP-15）。清回舊 7 是修復，不是此格綠
- 觀測:從該 CASE 紅標看 | 注入折線紅算過 | n-a:電池未落地。替代：Decision SC-OLD7-FOLD-RED
- Operational Context:不適用 — 極性；in-flight 保護見 R-7。

#### S-4.8 極性反了（拒 hop 當紅格綠）必須被拒
- GIVEN 有人把 NEW5-MK-RED／NEW5-SHIP-MECH／NEW5-WAIT-RED／OLD7-FOLD-RED 的「coordinator 拒寫／拒 hop」標成該格綠
- WHEN 電池或 7-review 對帳 CASE 表
- THEN 整電池非 0 或該對帳失敗；不得標 F2 成功
- 觀測:從 CASE 極性欄與該格 exit 看 | 紅格只接受注入壞行為的紅算過 | 本檔 CASE 表「注入」欄即測法
- Operational Context:不適用 — 測法契約。

#### S-4.9 檔在／只 F1 綠／只 NEW5 綠＝hollow（SC-HOLLOW）
- GIVEN 下列任一被標「F2 綠」：(a) 僅證明 coordinator 檔存在（S-8.5）；(b) 僅 `test-five-station-f1.sh` 十二群綠（S-8.6）；(c) 僅 NEW5-HOP-OK 綠而 OLD7 組未跑（S-8.8）
- WHEN 電池或完成宣稱被核對
- THEN 必須非 0／必須被拒。三陷阱各有獨立 S，本條是索引
- 觀測:從入口 exit + 完成宣稱對照看 | 三假綠皆非 0 算過 | Decision SC-HOLLOW；S-8.5／S-8.6／S-8.8
- Operational Context:不適用 — 完成定義。

#### S-4.10 不得減 Decision 原 13 列 CASE
- GIVEN Decision「本方案要求」表 13 列
- WHEN 本檔或後站 5-tasks 列 CASE
- THEN 13 列名稱都在；只准加列；加列不得把「檔在」加成通過條件
- 觀測:從本檔 CASE → S 表列名看 | 13 名全在、加列 5 名見上表算過 | 讀本檔 CASE 表
- Operational Context:不適用 — 表完整性。

#### S-4.11 NEW5-STORE-READ 是加列紅格
- GIVEN CASE NEW5-STORE-READ（本檔加列）
- WHEN **注入** RP-9／10／11 只咬 fixture 字樣、不讀 1A 倉
- THEN 該格獨立變紅（與 S-1.12 同一測法）
- 觀測:從該 CASE 紅標看 | 與 S-1.12 同過 | 見 S-1.12
- Operational Context:不適用 — 加列索引。

#### S-4.12 NEW5-Q12-ZERO 是加列綠格
- GIVEN CASE NEW5-Q12-ZERO
- WHEN 某 hop_id 第一次成功 persist
- THEN 該桶＝0；第一次寫不算進 hop≤2；此格綠
- 觀測:從該 CASE 綠標 + 倉數字看 | 與 S-1.1／S-1.3 同過 | 見 S-1.1
- Operational Context:不適用 — 加列索引。

#### S-4.13 NEW5-SPEC-SHARE 是加列綠格
- GIVEN CASE NEW5-SPEC-SHARE
- WHEN `3-prototype.md` 與 `4-spec.md` 先後 persist
- THEN 同一 Spec 桶；此格綠
- 觀測:同 S-2.2 | 同桶算過 | 見 S-2.2
- Operational Context:不適用 — 加列索引。

#### S-4.14 NEW5-BUILD-SHARE 是加列綠格
- GIVEN CASE NEW5-BUILD-SHARE
- WHEN `5-tasks.md` 與 `6-implementation-notes.md` 先後 persist
- THEN 同一 Build 桶；此格綠
- 觀測:同 S-2.3 | 同桶算過 | 見 S-2.3
- Operational Context:不適用 — 加列索引。

#### S-4.15 Intake→Decide：I1–I4 全真才 hop
- GIVEN NEW5 合成 fixture 已過三前置；I1–I4 全真（`1-discussion.md` 可解析；Open Questions 已解或明標 `[Assumption]`；有 `## Real-world Context` 或標了 legacy；A1／A2 若應產則產檔器 exit 0）
- WHEN coordinator 評 Intake → Decide
- THEN hop 發生；前進紀錄寫 from=Intake、to=Decide；A1／A2 latch＝否 → 紀錄不含「請人審 A1」「請人審 A2」
- 觀測:從該 slug 前進紀錄與目錄檔看 | from-to=Intake→Decide 且無請人審 A1／A2 算過 | n-a:F2 coordinator 本 hop 不落地。替代：狀態機 §2.1；本檔謂詞表 I1–I4
- Operational Context:
  - Actor:coordinator／寫手
  - Goal:Intake 表列真就進 Decide，不等「可以開下一站」
  - Situation:NEW5 fixture、三前置已過
  - Known information:狀態機 §2.1；A1／A2 latch＝否
  - Missing information:現場會不會仍用 chat 當開關
  - Human decision:不在 Intake 簽
  - Authority:coordinator 禁問「要不要繼續」
  - External dependency:無
  - Out-of-system action:不准改問 owner 繞假表列
  - Waiting/timeout behavior:中間不停
  - Recovery:任一 I 列假 → 停 Intake 修該列；出現請人審 → NEW5-WAIT-RED 紅
  - Audit/handoff requirement:前進紀錄可核五問
  - Observation:見本條觀測

#### S-4.16 Decide→Spec：D1–D4 全真且不等 G1 verdict
- GIVEN 同一 NEW5 fixture；D1–D4 全真（`2-decision.md` 在；`## Decision` 非空；OC 全裁決、無「待裁決」字樣；A3 真且 A4 twin 已產或可產）
- WHEN coordinator 評 Decide → Spec
- THEN hop 發生；**不**等人寫 G1 `verdict:`；紀錄 from=Decide、to=Spec
- 觀測:從前進紀錄看 | Decide→Spec 發生且無「請填 G1 verdict」算過 | n-a:coordinator 未落地。替代：狀態機 §2.2；本檔謂詞表 D1–D4
- Operational Context:不適用 — 與 S-4.15 同一 hop 家族；本條只換 Decide 表列與「不等 G1」。

#### S-4.17 Spec→Build 無 trigger：Sp1–Sp4＋Sp5a＋Sp6 真、不建 3-prototype
- GIVEN NEW5 fixture；九條 Stage 3 trigger 全未命中；Sp1–Sp4 真；Sp5a 視為真；Sp6 若 B2 未命中則本列不擋
- WHEN coordinator 評 Spec → Build
- THEN hop 發生；目錄**沒有**新建 `3-prototype.md`；A5 不建頁；**不**等人寫 G2 `verdict:`
- 觀測:從目錄 `ls` 與前進紀錄看 | Spec→Build 發生、無 `3-prototype.md`、無請填 G2 算過 | n-a:coordinator 未落地。替代：狀態機 §2.3 第 5 條；本檔謂詞表 Sp5a
- Operational Context:
  - Actor:coordinator
  - Goal:無互動風險不產 Demo、不 latch
  - Situation:0 trigger
  - Known information:九條 trigger；A5 沒命中不建頁
  - Missing information:無
  - Human decision:不在 Spec 簽 Demo
  - Authority:未命中不得強迫 `ACCEPTED`
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:不 latch
  - Recovery:若被要求 `ACCEPTED` → 不 hop
  - Audit/handoff requirement:trigger 判定落檔
  - Observation:見本條觀測

#### S-4.18 Spec→Build 命中 B1：Sp5b 未寫 attestation 不得 hop
- GIVEN 另一份 NEW5 fixture；九條 trigger 至少一條命中；`3-prototype.md` 在
- WHEN Human verdict ≠ `ACCEPTED`、或 `ACCEPTED` 但無 `Verdict attestation: human:<名>` 行，且 coordinator 被求 hop 出 Spec
- THEN 不 hop；B1 命中且 attestation 未寫 → 進 HumanWait，不是偷偷 hop；無 attestation 的 `ACCEPTED` = Sp5b 假
- 觀測:從 hop 拒絕理由與狀態看 | 狀態=HumanWait 或停 Spec；未 hop 到 Build 算過 | n-a:coordinator 未落地。替代：狀態機 §2.3 第 6 條；本檔謂詞表 Sp5b
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
  - Waiting/timeout behavior:HumanWait 直到 Human verdict 寫入
  - Recovery:REVISE → 回 Spec 重 Demo，吃 hop cap
  - Audit/handoff requirement:attestation 行
  - Observation:見本條觀測

#### S-4.19 Build→Ship：Bu1–Bu4 全真才 hop
- GIVEN NEW5 fixture；Bu1–Bu4 全真（每 T 四欄；每 T 獨立 review PASS 且 reviewer ≠ implementer；本次 S 全綠；Files ⊆ 5-tasks Files 聯集；Must-keep M1–M16 綠）
- WHEN coordinator 評 Build → Ship
- THEN hop 發生；A8／A9 latch＝否 → 紀錄不含「想給人看看任務板」「請人審 A8」
- 觀測:從前進紀錄與 T 卡看 | Build→Ship 發生且無請人審任務板算過 | n-a:coordinator 未落地。替代：狀態機 §2.4；本檔謂詞表 Bu1–Bu4
- Operational Context:不適用 — 與 S-4.15 同一 hop 家族；本條只換 Build 四欄、獨立 review、Must-keep。

### R-5: 系統 SHALL 留下可指的 hop／latch／cap 紀錄，不 bump agent-event、不鎖鍵名

2C。前進／latch／cap 各留一筆人指得到的紀錄，能答五問（誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated）。不鎖 JSON／YAML 鍵名。本刀不 bump `agent-event`。看板／chat／`STATUS.md` 不是正本。

**審的時候看什麼**
人能不能指到三筆。五問有沒有答。有沒有靠 `attempt_completed` 冒充。有沒有偷偷 bump schema。

#### S-5.1 三類紀錄各至少一筆且五問有答
- GIVEN NEW5 一次 hop 成功、一次 latch 開火、一次 cap 用盡
- WHEN 人問「有沒有留下」
- THEN 三類各至少一筆可指；每筆能答誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated
- 觀測:從 slug ledger（與 1A 同壽命）指檔看 | 三類＋五問有答算過 | n-a:F2 未落地。替代：1-discussion AC-7；Decision Q23
- Operational Context:不適用 — 紀錄可指性。

#### S-5.2 正本不是 chat、不是 STATUS、不是 attempt_completed
- GIVEN 同 S-5.1 的三筆
- WHEN 有人只拿出 Cursor chat、`STATUS.md` 過期列、或既有 `attempt_completed` 事件
- THEN 那些**不算** hop／latch／cap 正本
- 觀測:從「正本路徑」是否等於 chat／STATUS／`attempt_completed` 看 | 三者皆否算過 | 1-discussion L246 已拒 attempt 冒充
- Operational Context:不適用 — 正本排除。

#### S-5.3 本刀不 bump agent-event
- GIVEN 現行 `observability/schema/agent-event.schema.json` 無 hop／latch／cap 型別；`stage` 正則吃不進 Intake／Decide
- WHEN F2 宣稱完成
- THEN 該 schema 的 major.minor 不因本刀上升；採用端只 update plugin、契約 schema 仍 1.1 時，不得因本刀被 doctor 判 INCOMPATIBLE
- 觀測:從 F2 實作 PR diff 與契約 `schema_versions` 看 | 無 bump 算過 | `hooks/_doctor_impl.py` L216-L233；Decision Q18 去向＝避免 bump
- Operational Context:不適用 — schema 凍結。

#### S-5.4 鍵名保持 OPEN
- GIVEN Decision「語意槽可答、鍵名 OPEN」
- WHEN 後站把 `event_type=hop_advanced`（或任一具體 JSON 鍵）寫成「本 Decision／本 spec 已核必填鍵」
- THEN ＝偷做 annex，必須回 Stage 2；本檔只要求五問可答
- 觀測:從本檔與後站 5-tasks 是否把具體鍵當已核看 | 無已核鍵名算過 | Decision 約束 11
- Operational Context:不適用 — 鍵名紀律。

### R-6: 系統 SHALL 把 Must-keep 放進自動前進謂詞，且三失敗各自可紅

6A。Must-keep **M1–M16 任一紅**不得 hop（不是只擋 M11／T Verify）。三失敗：(1)謂詞表列真仍留下要不要繼續；(2)Must-keep 紅仍 hop；(3)機械綠 → Ship Done。latch 未命中不得中途等人。

**審的時候看什麼**
有沒有「已經五站了所以可省」。有沒有只測 M11。三條失敗是不是各有一格能紅。M1–M16 去向表在不在。

#### S-6.1 Must-keep 未綠不得 hop（M11 例）
- GIVEN NEW5 Build：某 T 缺 Verify（M11／RP-1）
- WHEN coordinator 評 Build→Ship
- THEN 不 hop；理由含 Must-keep／Verify 缺。不得用「已經五站了」省略
- 觀測:從 hop 拒絕理由看 | 含缺 Verify、不含「已經五站了所以可 hop」算過 | brief §5 M11；Decision 約束 7
- Operational Context:
  - Actor:寫手／獨立 T reviewer
  - Goal:完整度留下
  - Situation:T 卡缺欄
  - Known information:四欄必填
  - Missing information:無
  - Human decision:補 Verify，不口頭 hop
  - Authority:coordinator 禁 hop
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停 Build 修
  - Recovery:補四欄後重評
  - Audit/handoff requirement:拒絕理由留下
  - Observation:見本條觀測

#### S-6.2 謂詞真 ∧ latch 假 → 立刻 hop，不准留下等人句
- GIVEN NEW5 Decide：Decision 非空、OC 全裁、latch 假
- WHEN coordinator 評 Decide→Spec
- THEN 立刻 hop；前進紀錄無「要不要繼續／請人審／確認一下」
- 觀測:從 hop 是否發生 + 紀錄字面看 | hop 發生且無三人句算過 | Decision 約束 8
- Operational Context:見 S-4.2／S-4.6（本條是謂詞契約，S-4.6 是注入紅格）。

#### S-6.3 Ship 無自動前進
- GIVEN NEW5 `7-review.md` 在；機械全綠；`verdict:` 空白
- WHEN coordinator 評 Ship→Done
- THEN 不得 hop 到 Done；必須 HumanWait
- 觀測:從狀態看 | 停 Ship／HumanWait、不是 Done 算過 | 狀態機 §2.5
- Operational Context:見 S-4.5。

#### S-6.4 三失敗各自可紅，不得當成功
- GIVEN 電池同時有 NEW5-WAIT-RED、NEW5-MK-RED、NEW5-SHIP-MECH
- WHEN 各注入對應壞行為
- THEN 三格各自獨立紅；任一被標 F2 成功 → 整電池非 0
- 觀測:從三格獨立紅標看 | 三條都能紅、不能互抵銷算過 | Decision Q22；1-discussion AC-10
- Operational Context:不適用 — 三格索引。

#### S-6.5 任一 Must-keep（M1–M16）紅 → 拒 hop
- GIVEN NEW5 當下 hop 的謂詞表列其餘為真；M1–M16 **任一**紅（例：M1 測名無 S-id；M3 某 S 缺觀測欄；M5 代填 `ACCEPTED`；M9 Files 超出聯集；M11 T 缺 Verify；M12 reviewer＝implementer；M15 token 被刪）
- WHEN coordinator 評該 hop
- THEN 不 hop；理由含該 M 編號或同等 Must-keep 名。只擋 M11、其餘 M 紅仍 hop＝本條紅。不得用「已經五站了」省略
- 觀測:從 hop 拒絕理由 + 對照稿（16 份各少一 M）看 | 16 份皆不 hop；理由可指到該 M 算過 | brief §5「少一條 = 本 brief 被違反」；本檔 Must-keep Disposition
- Operational Context:
  - Actor:寫手／coordinator
  - Goal:完整度留下，不是摺掉
  - Situation:有人想只守 T Verify
  - Known information:M1–M16 表
  - Missing information:無
  - Human decision:補該 M，不口頭 hop
  - Authority:coordinator 禁 hop
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停該站修
  - Recovery:該 M 綠後重評
  - Audit/handoff requirement:拒絕理由留下 M 編號
  - Observation:見本條觀測

#### S-6.6 M1–M16 去向表完整，無一題標可選
- GIVEN 本檔 Must-keep Disposition 16 列
- WHEN 人逐條對帳 brief §5
- THEN M1–M16 皆有去向 ∈ {本方案處理, 刻意維持}；下落至少一條 S-；無一列空白、無一列標可選／Non-Goal 當省略
- 觀測:從本檔 Must-keep Disposition 表列看 | 16 列皆有去向與下落 S 算過 | 讀本檔 Must-keep Disposition
- Operational Context:不適用 — 去向帳。

### R-7: 系統 SHALL 先問專案樹路線，且 live slug（含本目錄）不建五站機

4A＋7A＋8A 自保。三前置全要，缺一 → `allow_legacy()`。plugin cache 只選本 process 讀哪份 hops **碼**，不是路線許可。NEW5＝合成 fixture（DD-3），不是本目錄、不是 `five-station-simplify`。

**審的時候看什麼**
本目錄有沒有被當成 NEW5。OLD7 有沒有被寫入五站狀態。cache 新會不會拖走另一台機器的舊 7。

#### S-7.1 三前置缺一條就 allow_legacy
- GIVEN 缺「契約已宣告 2.1.0」或「非 in-flight」或「F3 cut 已發生」任一
- WHEN coordinator 評是否建五站機
- THEN `allow_legacy()`；不建五站機；不套三 cap
- 觀測:從路線閘輸出看 | 缺一條＝舊 7 算過 | n-a:F2 未落地。替代：Decision 4A；brief §6
- Operational Context:不適用 — 前置閘。

#### S-7.2 plugin cache 只選碼，不是路條
- GIVEN 同一 repo；行程 A 的 host plugin root 已是五站 hops 碼；契約未宣告 2.1.0
- WHEN 行程 A 的 coordinator 評路線
- THEN 路線仍舊 7；cache 只決定讀哪份 hops **碼**
- 觀測:從路線判定 vs `DEVFLOW`／plugin root 看 | 碼新、路舊算過 | Decision 7A
- Operational Context:
  - Actor:兩台機器上的寫手
  - Goal:不得遠端改線
  - Situation:多 cache
  - Known information:hops 住方法包
  - Missing information:人會不會以為「我更新了所以大家五站」
  - Human decision:認專案樹契約 + 該 slug 是否已有 1–7 `.md`
  - Authority:禁因 A 機 hops 新改 B 機舊 7
  - External dependency:各機 plugin cache
  - Out-of-system action:各機自己 update
  - Waiting/timeout behavior:無
  - Recovery:寫進採用說明，不用共識掃描掩蓋
  - Audit/handoff requirement:路線判定可核對專案樹
  - Observation:見本條觀測

#### S-7.3 不得掃全機最新 cache 改線
- GIVEN 磁碟上另有一份「更新」的 plugin cache
- WHEN coordinator 選 hops 碼
- THEN 不掃「最新」其他 cache；不得因他份 cache 把本行程舊 7 slug 改線
- 觀測:從「讀哪一份 plugin root」看 | 只讀當下行程 host root 算過 | Decision 7B 棄
- Operational Context:不適用 — 同 S-7.2。

#### S-7.4 OLD7-NO-FIVE 綠
- GIVEN OLD7 fixture 已有 1–7 `.md`（DD-4）
- WHEN 電池跑 OLD7-NO-FIVE
- THEN 無五站狀態寫入；三 cap 不套；可走既有 T 上限 4；此格綠
- 觀測:從該 fixture 目錄 + 倉是否被建立看 | 無五站機、三 cap 未套算過 | n-a:電池未落地。替代：Decision SC-OLD7-NO-FIVE
- Operational Context:不適用 — OLD7 路。

#### S-7.5 OLD7-TOKEN 綠
- GIVEN 同一 OLD7 fixture
- WHEN 跑 `scripts/check-gate-tokens.sh`（或同等）與 F1 十二群
- THEN token／G1／G2／`ACCEPTED` 檔仍在；F1 牙回歸仍綠；此格綠
- 觀測:從 token 檢查 + `test-five-station-f1.sh` exit 看 | 兩路綠算過 | 現況 token 牙已存在
- Operational Context:不適用 — 回歸。

#### S-7.6 OLD7-SELF：對本目錄求五站自動前進跳不過
- GIVEN `docs/dev/five-station-f2/` 已有 1-discussion／2-decision（in-flight）
- WHEN 對本目錄要求五站自動前進
- THEN 被拒；目錄仍是舊 7 站檔；試體不是把本目錄當 NEW5
- 觀測:從對本目錄的 hop 拒絕 + `ls docs/dev/five-station-f2/` 看 | 有舊 7 檔、無五站機寫入算過 | 本 hop 落 4-spec 後仍 in-flight
- Operational Context:不適用 — 自保。

#### S-7.7 NEW5 試體是合成 fixture
- GIVEN NEW5 試體路徑（DD-3）
- WHEN 電池選 hop 主詞
- THEN 路徑不是 `docs/dev/five-station-f2/`，也不是 `docs/dev/five-station-simplify/`
- 觀測:從電池 fixture 路徑看 | 兩 live slug 目錄不當 NEW5 主詞算過 | Decision 約束 3
- Operational Context:不適用 — 試體選址。

### R-8: 系統 SHALL 鎖死三把 Non-Goals，且本 hop 只交 draft 規格雙檔

8A。不做 F3 cut；不折 in-flight；不刪 G1／G2／`ACCEPTED`。**後站不准把這三把改成 In。** 本 hop 只 `4-spec.md` + `4-spec.html`；`status: draft`；`verdict` 空；無 G2 PASS。後站 Diff Budget 只准 F2 scripts；F3／token／graph＝0。

**審的時候看什麼**
diff 是不是只有這兩檔。頂欄有沒有被寫成 PASS。有沒有 F3 聲明。

#### S-8.1 不做 F3 cut（SC-KNIFE）
- GIVEN F2 宣稱完成之後
- WHEN 人找「新 slug 預設五站」聲明，或後站 5-tasks／6-notes 把 F3 cut 標成 In／可選
- THEN 無 F3 cut 把新 slug 預設改五站；guide／STATUS 用語未切五站；**後站不准改成 In**
- 觀測:從 F2 完成樹的 guide／STATUS／契約 + 後站 Files 看 | 預設仍舊 7；把 F3 改成 In＝本條紅算過 | brief §7 F3 列；Decision Out「後站不准改成 In」
- Operational Context:不適用 — 刀範圍。

#### S-8.2 不折 in-flight
- GIVEN 任一已有 1–7 `.md` 的 slug（含本目錄）
- WHEN F2 落地，或後站把「折 in-flight」標成 In／可選
- THEN 該 slug 仍舊 7；無五站狀態寫入；**後站不准改成 In**
- 觀測:從那些目錄與 OLD7-NO-FIVE + 後站 Files 看 | 仍舊 7；改成 In＝本條紅算過 | 與 S-7.4／S-4.7 同鎖
- Operational Context:不適用 — freeze。

#### S-8.3 不刪 G1／G2／ACCEPTED token 與檔
- GIVEN F2 完成樹
- WHEN 跑 token 檢查，或後站把「刪 token」標成 In／可選
- THEN G1／G2／`ACCEPTED` token 與檔仍在；**後站不准改成 In**
- 觀測:從 `scripts/check-gate-tokens.sh` + 後站 Files 看 | 仍綠；改成 In＝本條紅算過 | 與 S-7.5 同
- Operational Context:不適用 — 禁刪。

#### S-8.4 本 Stage 4 hop 只 4-spec 雙檔、draft、無 G2 PASS
- GIVEN 本 PR 對 `origin/main`
- WHEN `git diff --name-only origin/main`
- THEN 只含 `docs/dev/five-station-f2/4-spec.md` 與 `docs/dev/five-station-f2/4-spec.html`；頂欄 `status: draft`；`verdict` 空；無 G2 PASS；無 STATUS／HISTORY／模板／graph／scripts 新牙／契約 bump
- 觀測:從本 PR diff + 本檔 frontmatter 看 | 兩檔、draft、verdict 空算過 | 讀本檔頂欄與 `git diff --name-only`
- Operational Context:不適用 — 本 hop 檔集。

#### S-8.5 檔在 ≠ F2 完
- GIVEN 僅 coordinator 模組檔存在、電池未綠
- WHEN 有人標 F2 綠
- THEN 必須被拒（5B 已拒）
- 觀測:從完成條件是否要求 S-4.1 看 | 檔在單獨不算完算過 | Decision 約束 1
- Operational Context:不適用 — 完成定義。

#### S-8.6 F1 十二群綠 ≠ F2 完
- GIVEN `scripts/test-five-station-f1.sh` exit 0
- WHEN 有人標 F2 綠且未跑 S-4.1 入口
- THEN 必須被拒（5C 已拒）
- 觀測:從完成條件是否另要求 F2 入口看 | F1 綠是回歸地板不是完工算過 | `scripts/test-five-station-f1.sh` L1-L16
- Operational Context:不適用 — 完成定義。

#### S-8.7 Q9–Q24 皆有去向（SC-Q-CARRY）
- GIVEN 1-discussion Q9–Q24
- WHEN 人讀本檔 Real-world Disposition
- THEN 每題有去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗}；Q21／Q22／Q23 不得標可選
- 觀測:從本檔 Disposition 表列看 | Q9–Q24 皆有列、Q21–Q23 下落是 S 算過 | 讀本檔 Disposition
- Operational Context:不適用 — 去向帳。

#### S-8.8 只跑 NEW5 綠 ≠ F2 完
- GIVEN 僅 NEW5-HOP-OK（或 NEW5 組）綠，OLD7 組未跑或被跳過
- WHEN 有人標 F2 綠
- THEN 必須被拒（SC-HOLLOW (c)）；與 S-4.1(b)／S-4.9(c) 同一測法，本條單獨可指
- 觀測:從入口 exit + 完成宣稱對照看 | 只 NEW5 綠仍非 0 算過 | Decision SC-HOLLOW (c)
- Operational Context:不適用 — 完成定義。

#### S-8.9 Stage 5 Files 准許清單；F3／token／graph Diff Budget＝0
- GIVEN 本 slug G2 已過，進入 5-tasks；或後站實作 PR 對開工點
- WHEN 列 Files 聯集，並跑 `git diff --name-only`
- THEN 只准下列路徑：`scripts/test-five-station-f2.sh`；`scripts/` 下 F2 coordinator 實作檔（不含 doctor／模板）；`scripts/fixtures/five-station-f2/**`；把 RP-9／10／11 接到 1A 倉的最小改動（可改 `scripts/five_station_f1.py` 讀倉，不改字樣牙回歸）；本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html。下列區塊 Diff Budget **必須＝0**，否則本條紅：`guides/` F3 cut 聲明；各站 `skills/dev-flow/stage*/graph.yaml`；G1／G2／`ACCEPTED` token 檔被刪；`_templates/`；`hooks/_doctor_impl.py` 握手語意；`devflow-contract.json` bump；`docs/dev/STATUS.md`／`HISTORY.md`（看板另 companion）
- 觀測:從 5-tasks Files 聯集 + 後站 `git diff --name-only` 看 | 超出准許清單或 F3／token／graph 行數 ≠ 0 → 本條紅算過 | n-a:5-tasks 尚未寫。替代：本檔 Diff Budget 與 Out of Scope
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:只施工 F2 scripts
  - Situation:G2 剛過
  - Known information:8A 刀範圍；准許清單具名
  - Missing information:有沒有人想順便切 graph
  - Human decision:F3 另開 slug
  - Authority:本 R
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:把 F3／模板／doctor／graph／token 刪檔從 Files 刪掉
  - Audit/handoff requirement:5-tasks Files
  - Observation:見本條觀測

## MODIFIED Requirements

本 repo `docs/specs/` 無 living spec 條文可引。F1 已核契約（`docs/dev/five-station-simplify/4-spec.md`）本刀**不改其 SHALL 原文**；只把 F1 明文交給 F2 的縫接上：

| 縫 | F1 原文要點 | 本刀怎麼接 | 本檔 S |
|---|---|---|---|
| 計數落點 | rewrite 三 cap 數字已鎖，落點交 F2，不鎖鍵名 | 落點＝slug 級只增倉；鍵名仍 OPEN | R-1、S-5.4 |
| RP-9／10／11 | 牙現況咬 fixture 字樣 | 改讀 1A 倉；字樣牙可留回歸 | S-1.5、S-1.6、S-1.7、S-1.12 |
| doctor 綠 | SLOT-DOCTOR-GREEN-MEANS 文案牙 | 行為牙：綠≠hop；不改 doctor | R-3 |
| 本 slug 舊 7 | 五站 hop 跳不過 | 對本目錄建五站機＝RP-15 | S-7.6 |

故本節無「改寫已刊 living 條文」列。

## REMOVED Requirements

無。不刪 F1 十二群、不刪 token、不刪舊 7 graph。

## 行為流程圖(R 級)

```
[R-1] 三 cap 寫進 slug 倉且 RP 讀倉
  第一次 persist＝0 其後 +1
  新 run 數字仍在
  第三次重寫讀倉拒
[R-2] 五站桶且 Spec Build 同桶
  3-proto 與 4-spec 同 Spec
  七 stem 注入則紅
[R-3] marketplace 乘 doctor 是約束
  COMPATIBLE 不是 hop 通行證
  update 單獨不是 cut
[R-4] 同一電池且注入壞行為該格紅
  缺一路整電池非 0
  拒 hop 不得當紅格綠
[R-5] 紀錄答五問不 bump 不鎖鍵
  正本不是 chat 或 STATUS
[R-6] Must-keep 進謂詞且三失敗可紅
  任一 M1–M16 紅拒 hop
  Ship 無自動 Done
[R-7] 先問專案樹且 live 不建五站機
  cache 只選碼
  本目錄跳不過
[R-8] 三把鎖且本 hop 只交 draft 雙檔
  後站不准改成 In
  F3／token／graph＝0
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.9）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、本目錄 freeze md、doctor 握手、Disposition／CASE／Must-keep／謂詞表。F2 行為 S 的綠發生在後站落地之後，不在本 PR。S 數見確認紀錄；>40 誠實記帳，不另切開新 slug。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-f2/4-spec.md` 後審頁可解析 R/S。本 hop 禁改 `scripts/` 牙。
- 非功能：本 slug 自己仍走舊 7。dual-read 未 bump。本 hop 不送 G2。
- 無 golden master（可見路線行為在 F3 才變；本 hop 不改 runtime）。

### Stage 3 對帳

N/A。無 `3-prototype.md`。九條 trigger 對本刀（coordinator／slug 倉／電池／約束）：新前端流程否；改變下一步否（hop 規則 F0／F1 已鎖，本刀不新設計互動）；角色交接否；人工核准否（Ship 既有）；等待退回逾時否（latch 既有規則）；權限差異否；系統外動作否（marketplace 是既有升級路徑，不新開互動方案）；多種互動設計否；操作流程不確定否。0 命中 → Stage 3 維持選配，不建頁、不 latch Demo。Decision 內部技術選擇寫「不預先跳過、觸發判定留給該站」——本站判定＝0 命中，**不是**「命中仍跳過」的 skip OC。Demo verdict＝N/A＋本段原因。

## Out of Scope

鎖死，後站不准改成 In：

1. **F3 cut**（新 slug 預設五站；guide／STATUS／graph 用語切五站）。
2. **把 in-flight 折成五站**（含本目錄、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
3. **刪 G1／G2／`ACCEPTED` token 或檔**。
4. 放寬 hop≤2／Decide≤1／Goal reopen≤1。
5. 拿本 slug 或 `five-station-simplify` 當 NEW5 白老鼠。
6. 把 run 級 `events.jsonl` 當 cap 倉。
7. 把 doctor 綠／marketplace update／他份 cache 當路線許可。
8. 把「檔在」或「F1 綠」或「只跑 NEW5-HOP-OK」當 F2 完成。
9. 本 PR 實作 coordinator、改 STATUS／HISTORY、填 G2 PASS、合併、改 `_templates/`／`graph.yaml`／既有牙（除後站准許的 RP 讀倉最小接線）、bump 契約。
10. 選定 event／倉的 JSON 鍵名或 schema 版本號。
11. 七 stem 各一桶。
12. 改 `hooks/_doctor_impl.py` 握手語意。
13. Q24 過期看板：本 PR 不改 STATUS。
14. 本 hop 改 2-decision 頂欄或 OC 狀態。

## Diff Budget

整節是估計，不是承諾。[Assumption]。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| 本 hop 規格 md | 1 | ≤1,800 | `docs/dev/five-station-f2/4-spec.md` |
| 本 hop 審頁 html | 1 | 產器產出 | `4-spec.html`；不手包 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約／2-decision | 0 | 0 | 本 hop＝0；出現＝S-8.4 紅 |

**G2 之後、本 slug Stage 5–7（只 F2 scripts）**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| `scripts/test-five-station-f2.sh` | 1 | ≤200 | 單一電池入口 |
| coordinator 實作（`scripts/` 下，不含 doctor／模板） | ≤4 | ≤600 | slug 倉／路線閘／hop 評 |
| `scripts/fixtures/five-station-f2/new5/` + `old7/` | ≤12 | ≤400 | 合成 NEW5 + OLD7 |
| RP-9／10／11 讀 1A 倉最小接線（可改 `scripts/five_station_f1.py`） | ≤2 | ≤80 | 不改字樣牙回歸 |
| 電池／CASE 測試（與非測試分開） | ≤6 | ≤800（測試） | 突變另加係數 |
| F3 cut（`guides/` 切五站） | 0 | 0 | ＝0，否則 S-8.9 紅 |
| 各站 `graph.yaml` | 0 | 0 | ＝0，否則 S-8.9 紅 |
| G1／G2／`ACCEPTED` token 刪檔 | 0 | 0 | ＝0，否則 S-8.9 紅 |
| `_templates/`／doctor 握手／契約 bump／STATUS／HISTORY | 0 | 0 | 看板另 companion |

Stage 5 Files 准許清單正本＝S-8.9。超出 → L2。

## Dependencies

| 依賴 | justification |
|---|---|
| F0 brief＋狀態機 | cap 數字、謂詞、latch 正本；本檔不重開 |
| F1 teeth＋annex | 字樣牙與 doctor 文案牙當回歸地板；本刀加讀倉路徑 |
| `scripts/check-spec-gate.sh` | 本 hop 形狀閘 |
| `scripts/build-stage4-html.py` | 本 hop 審頁 |
| `scripts/check-gate-tokens.sh` | OLD7-TOKEN |
| `scripts/test-five-station-f1.sh` | 回歸；**不是** F2 完成入口 |
| 現行 doctor／契約 2.0.0 | SC-DOCTOR 現況可測；本刀不改 |

無新外部服務。slug 倉是本 repo 檔案，不是新 SaaS。

## Design Boundary Contract

- Applicability: applicable
- Trigger(s): ⑦寫入原子性（Goal+Decide 同 mutation）／⑧新增 filesystem 能力（slug 倉）／⑨Feature Risk = high／⑪狀態機與 Escalated 恢復
- Design source: `notes/design/five-station-simplify-f0-state-machine.md` §3 偽碼；Decision 1A／2C；new local design＝倉路徑形（DD-1）

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| slug 倉 | 三計數 + hop／latch／cap 紀錄 | 該 slug 的 coordinator 寫者 | 讀專案樹契約與 `docs/dev/<slug>/` 站檔 | run 級 `events.jsonl` 當 cap 正本；他份 plugin cache；STATUS／chat |
| 路線閘 | 三前置 → 五站機或 `allow_legacy()` | 專案樹契約 + 該 slug 是否已有 1–7 `.md` | host plugin root（只選碼） | doctor 綠；marketplace update；掃最新 cache |
| F2 電池 | NEW5+OLD7 同一 process | 合成 fixture + OLD7 fixture | F1 十二群當回歸 | 本目錄當 NEW5；只轉呼叫 F1 腳本當完成 |
| 舊 7 graph／doctor | 不動 | 既有 owner | F1 牙回歸 | F2 改其語意 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| persist(hop_id) | 成功寫入 → 桶 0 然後 +1 | 超 cap → Escalated，數字不減 | 單 hop 桶 +1 與該筆紀錄同成功或同失敗 | 不 bump agent-event |
| Goal reopen mutation | Goal+Decide 兩計數 | 分兩次寫＝躲 Decide cap | **同一 mutation**；只成功一筆＝違 S-1.9 | 舊 7 不走此流 |
| 路線閘 | 三前置布林 | 缺一 → allow_legacy | 只讀專案樹；不寫採用端契約 | 2.0.0 握手綠仍舊 7 |
| 電池入口 | 無／選跑兩組 | 缺一組 → 非 0 | 單一 process 內兩組都跑完才 0 | F1 腳本不是入口 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| slug store | 只增讀寫 | coordinator | slug → 三計數 + 紀錄 | 寫失敗不 hop、不暗減 | 讀路徑可換 fixture 根 |
| hop evaluator | 評 brief §3 謂詞 | store、路線閘 | 真→hop；假→停修 | 禁改問人 | 注入缺欄／缺 Verify |
| cap teeth | RP-9／10／11 讀倉 | store | 倉≥上限 → 紅 | 字樣牙只回歸 | 倉＝2 且稿無「第 3 次」 |
| battery | 13+ 加列 CASE | NEW5／OLD7 fixture | 紅格餵壞行為 | 極性反了 → 非 0 | 各 CASE 獨立 exit |

### Design Constraints

- 必須:slug 級只增；Q12 persist＝0 後 +1；Spec／Build 同桶；RP-9／10／11 讀倉；紅格注入壞行為；同一電池；三前置；五問可答。
- 禁止:run 級 cap；七 stem；bump agent-event；鎖 JSON 鍵名；doctor 綠當路條；本目錄當 NEW5；本 hop 填 G2 PASS。
- Extension point:4-spec 可加 CASE 列；鍵名仍 OPEN。
- Known design limit:本 hop 不落地 coordinator；行為 S 的執行綠在後站。審頁產器 `steps[:8]`，本檔正好 8 個 R，不增 R-9。F2 完成樹之前 doctor 綠陷阱仍在現場（約束，不是本刀修 doctor）。

## Verification Profile

- lane: full（判準:新 filesystem 能力＝slug 倉、狀態機／Escalated、Feature Risk=high、採用端改線風險。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:計數完整性＝資料遺失變種、採用端被改線、併發兩 process 寫倉、誤做 F3 則不可逆。模板「資料遺失／併發／不可逆／公開 API」吃這條）
- Failure model: 見下表
- Negative constraints: 見 Out of Scope 全列（後站不准改成 In）；另：RP-9／10／11 不得只咬字樣；紅格不得把拒 hop 當綠；本 hop 不得改 STATUS／牙／契約；鍵名不得升成已核；不得只擋 M11
- Required layers: spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`）；token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F2 電池列 Required——Required 層不得 unverified
- Conditional layers: F2 coordinator／電池落地 → 該刀列入 Required，單一入口 `bash scripts/test-five-station-f2.sh`（NEW5+OLD7；缺一路即非 0）；F1 十二群在電池落地後當回歸地板重跑。契約／schema 被後站改動 → doctor 握手重跑。本 hop 不改那些檔、電池未落地 → 本 hop 不觸發 Conditional
- Explicitly excluded layers: UI e2e（本刀無新前端）；負荷／效能（coordinator 非熱路徑）；金流／auth fuzz（不涉）；本 hop 跑 coordinator（碼 Out of Scope）
- Final fresh entry point: `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`
- Reliability triage:
  - Concurrency: applicable — 新 `run_id` 不得把 slug 倉歸零（S-1.4）；兩 process 同 slug 只增不減（Failure Model「並行寫」）
  - Idempotency: applicable — 第一次成功 persist＝0；同一初寫重試不得再 +1（S-1.1／S-1.2）；Goal+Decide 同 mutation（S-1.9）
  - Timeout/retry: applicable — latch／Escalated／Ship 無逾時自動 Done（S-4.5、S-6.3）；重試寫入不得當新的 cap 次數，除非是另一次成功 persist（S-1.2）

### Failure Model

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| 新 run 讀空檔當 0 | 暗改 cap（X5） | SC-NEW5-RUN2 紅；倉在 `runs/<id>/` | Required:S-1.4、S-1.11 | — |
| RP 只咬「第 3 次」字樣 | live 第三次當第一次 | NEW5-STORE-READ 該格不紅 | Required:S-1.12、S-4.11 | — |
| 七 stem 分桶 | hop≤2 被稀釋 | NEW5-SEVEN-STEM 不紅 | Required:S-2.4 | — |
| doctor 綠當 hop 通行證 | 舊 7 被折 | 拒絕理由含「doctor 已綠」 | Required:S-3.1 | — |
| 紅格極性反了 | 壞行為測成綠 | MK／SHIP／WAIT／FOLD 被標綠 | Required:S-4.8 | — |
| Goal／Decide 分兩次寫 | Decide cap 被躲 | NEW5-GOAL-2 綠而 decide_reopen 未動 | Required:S-1.9 | — |
| 只跑 NEW5 或只跑 F1 | hollow F2 | 入口仍 0 | Required:S-4.1、S-4.9 | — |
| 對本目錄建五站機 | 觀測白老鼠 | OLD7-SELF 跳得過 | Required:S-7.6 | — |
| 本 hop 自填 G2 PASS | 四眼破 | 頂欄 PASS | Required:S-8.4 | — |
| 並行兩 process 各寫 +1 | 計數跳或丟失 | 倉非整增量 | Required:Concurrency | 本 hop 不寫碼；後站 seam＝store 可換根 |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q10 run 級倉＝X5 | stage-2 | oc-accepted |
| Q17 三前置全要 | stage-2 | oc-accepted |
| Q19 RP 必須讀真計數 | stage-2 | oc-accepted |
| 倉路徑形交 4-spec（本檔 DD-1） | 2026-12-31 | open |
| 電池入口檔名交 4-spec（本檔 DD-2） | 2026-12-31 | open |

Q10／Q17／Q19 已由 Decision OC-4／5／6 升格，故 oc-accepted。後兩列是本檔釘形，期限給後站落地，不是已過站。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–8A。推翻 Decision 不是合法 DD。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | slug 倉路徑形＝`docs/dev/<slug>/.five-station/store`（檔或目錄皆可，正本不在 `.devflow/runs/<run_id>/`）。鍵名仍 OPEN | Decision 把路徑形交給 4-spec；必須可測且躲 X5 | `2-decision.md` 決策點 1A 劣欄「4-spec 才釘形」；狀態機 `:L122-L124`。路徑本身 `[Assumption]` | 改回 run 級＝X5；改鎖 JSON 鍵＝違 OC-3 | 待人審 |
| DD-2 | 單一電池入口檔名＝`scripts/test-five-station-f2.sh` | Decision 只鎖同一 process、缺一路即非 0；檔名交給 4-spec | `2-decision.md` 5A 劣欄；內部技術選擇「入口檔名交 4-spec」。檔名 `[Assumption]` | 改兩支腳本各綠＝hollow | 待人審 |
| DD-3 | NEW5 fixture 根＝`scripts/fixtures/five-station-f2/new5/`（合成；不當 hop 主詞的 live 目錄） | Decision 約束 3 | `2-decision.md` 約束 3。路徑 `[Assumption]` | 拿本目錄當白老鼠＝RP-15 | 待人審 |
| DD-4 | OLD7 fixture 根＝`scripts/fixtures/five-station-f2/old7/`（已有 1–7 `.md`） | 與 NEW5 分家，供同一入口第二路 | `2-decision.md` 5A。路徑 `[Assumption]` | 與 NEW5 混目錄會折線 | 待人審 |
| DD-5 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 G2 PASS | 計數完整性＋採用端改線＋狀態機；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief「No G2 PASS」 | 改 normal 則 Failure Model 變選配；代填 PASS＝假綠 | 待人審 |
| DD-6 | 加 5 列 CASE：NEW5-STORE-READ／NEW5-SEVEN-STEM／NEW5-SPEC-SHARE／NEW5-BUILD-SHARE／NEW5-Q12-ZERO。Decision 原 13 列不減 | B 線主軸可測；Decision 只准加 | `2-decision.md`「只准加不准減」；本 hop B-line brief | 減原列＝翻 Decision | 待人審 |
| DD-7 | S 數 >40 留在本檔、不另切開新 slug；行為圖 8 框對 8 個 R（產器 `steps[:8]`） | 誠實記帳；不改 scripts | `scripts/build-stage4-html.py` L450；本 hop 不改牙 | 增 R-9 則圖丟框 | 待人審 |
| DD-8 | Stage 3 對帳＝0 命中 N/A，不是「命中仍跳過」 | Decision 無 skip OC；本刀無新互動 | `2-decision.md` 內部技術選擇「不預先跳過」；本 hop dispatch skip＝不建 3-prototype | 寫 skip OC 而無命中＝假跳過 | 待人審 |
| DD-9 | 原文獨立於 A／C；standing 才吸 A 謂詞表／C hollow＋Files 准許清單。不換 winner | owner standing soft-fix；B 線主軸（讀倉／同桶／doctor／Q12／注入紅）全留 | 本 hop owner 指令；#336 多數勝 | 改換 C 當 winner＝丟 B 讀倉主軸 | 待人審 |
| DD-10 | M1–M16 任一紅拒 hop；HOP-OK 用謂詞表不寫「謂詞全真」；F2 電池列 Conditional；DBC 含 ⑨；三把鎖後站不准改成 In；F3／token／graph Diff Budget＝0 | R1／R2 must-fix + 吸 C／A | owner standing 清單 | 只擋 M11 或 Required 列未落地電池＝形狀／語意裂 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `STATUS.md`、不 bump plugin、不開 5-tasks、不發明 G2 PASS。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- F1 字樣正則牙留作回歸；不得替代 1A 倉。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。

## Test Skeletons(選配)

- `test_s_1_1_first_persist_is_zero`
- `test_s_1_2_later_persist_increments`
- `test_s_1_3_first_write_not_in_hop_cap`
- `test_s_1_4_new_run_keeps_counts`
- `test_s_1_5_rp9_reads_store_third_rewrite`
- `test_s_1_6_rp10_reads_store_second_decide`
- `test_s_1_7_rp11_reads_store_second_goal`
- `test_s_1_8_reject_leaves_count_at_two`
- `test_s_1_9_goal_decide_same_mutation`
- `test_s_1_10_t_retry_not_hop_bucket`
- `test_s_1_11_not_run_level_events`
- `test_s_1_12_fixture_text_only_red`
- `test_s_2_1_hop_id_five_names`
- `test_s_2_2_proto_and_spec_share_spec_bucket`
- `test_s_2_3_tasks_and_notes_share_build_bucket`
- `test_s_2_4_seven_stem_inject_red`
- `test_s_2_5_no_proto_bucket_without_trigger`
- `test_s_2_6_old_graph_nodes_not_hop_id`
- `test_s_2_7_no_graph_yaml_change`
- `test_s_3_1_compatible_refuses_five_hop`
- `test_s_3_2_marketplace_update_not_cut`
- `test_s_3_3_v200_plus_five_hops_illegal`
- `test_s_3_4_doctor_phrase_still_red`
- `test_s_3_5_no_doctor_marketplace_edit`
- `test_s_3_6_cache_not_fourth_precondition`
- `test_s_4_1_single_entry_both_paths`
- `test_s_4_2_new5_hop_ok_green`
- `test_s_4_3_new5_pred_stop_green`
- `test_s_4_4_inject_must_keep_red`
- `test_s_4_5_inject_ship_mech_red`
- `test_s_4_6_inject_wait_red`
- `test_s_4_7_inject_fold_red`
- `test_s_4_8_polarity_invert_rejected`
- `test_s_4_9_hollow_rejected`
- `test_s_4_10_cannot_drop_case_rows`
- `test_s_4_15_intake_to_decide_i1_i4`
- `test_s_4_16_decide_to_spec_no_g1_wait`
- `test_s_4_17_spec_to_build_no_trigger`
- `test_s_4_18_spec_to_build_b1_needs_attestation`
- `test_s_4_19_build_to_ship_bu1_bu4`
- `test_s_5_1_five_questions_answerable`
- `test_s_5_2_not_chat_status_attempt`
- `test_s_5_3_no_agent_event_bump`
- `test_s_5_4_keys_remain_open`
- `test_s_6_1_must_keep_blocks_hop`
- `test_s_6_2_true_pred_hops_now`
- `test_s_6_3_ship_no_auto_done`
- `test_s_6_4_three_failures_independently_red`
- `test_s_6_5_any_must_keep_red_refuses_hop`
- `test_s_6_6_m1_m16_disposition_complete`
- `test_s_7_1_missing_precondition_legacy`
- `test_s_7_2_cache_selects_code_not_route`
- `test_s_7_3_no_scan_newest_cache`
- `test_s_7_4_old7_no_five_green`
- `test_s_7_5_old7_token_green`
- `test_s_7_6_old7_self_refuses`
- `test_s_7_7_new5_is_synthetic`
- `test_s_8_1_no_f3_cut`
- `test_s_8_2_no_fold_inflight`
- `test_s_8_3_tokens_remain`
- `test_s_8_4_this_hop_two_files_draft`
- `test_s_8_5_files_exist_not_done`
- `test_s_8_6_f1_green_not_done`
- `test_s_8_7_q9_q24_have_disposition`
- `test_s_8_8_new5_only_not_done`
- `test_s_8_9_stage5_files_allowlist_zero_budget`

## 確認紀錄

- 接手盤點 | 2026-09-14 | dispatch：G1 PASS、Skip Stage 3。2-decision 選定 1A+2C+3A+4A+5A+6A+7A+8A。Stage 3 本站判定 0 命中（N/A），無 skip OC。living `docs/specs/` 0 條。驗收雛形 AC-1…AC-10 + Decision SC 全表 + CASE 13 列。
- 雙源清點 | 2026-09-14 | 雛形 10 條 + Decision SC／CASE → 全數 ADDED R-1…R-8。living spec 0 條可引；F1 縫 4 條記 MODIFIED 對照、不改 F1 SHALL 原文。
- R 範圍 | 2026-09-14 | B 線 8 R：倉+RP 讀倉／同桶／doctor 約束／注入紅電池／五問紀錄／Must-keep／路線自保／刀+本 hop。產器 8 框上限。
- S 展開 | 2026-09-14 | 每 S 有觀測欄。CASE 13 列全掛 S；加 5 列。Q12 persist＝0/+1、Spec／Build 同桶、RP 讀倉、極性注入→紅皆有獨立 S。standing 後 S＝70（加 M1–M16／逐 hop／hollow 分條／Files 准許清單）。
- 4 小節 | 2026-09-14 | AC／Out of Scope／Diff Budget／Dependencies 齊。
- Profile + DBC | 2026-09-14 | lane full＋判準句、Risk high＋判準句、Failure Model 10 列、Reliability 三問 applicable、DBC applicable（⑦⑧⑨⑪）。F2 電池＝Conditional；Final Fresh＝check-spec-gate 一條。
- Stage 3 對帳 | 2026-09-14 | N/A，0 命中。Demo verdict N/A＋原因。
- DD 掃描 | 2026-09-14 | 上層 DD-1…DD-10 待人審。無未定事項三詞。不翻 Decision。
- 獨立於 A／C（原文） | 2026-09-14 | B 線當時只讀 2-decision＋brief F2＋狀態機＋4-spec 模板。
- Owner standing soft-fix | 2026-09-14 | Winner B 多數 #336。釘：M1–M16 去向＋任一 M 紅拒 hop；HOP-OK 謂詞表／逐 hop GWT（吸 A）；Profile 判準句＋電池 Conditional＋Fresh＝spec-gate；DBC ⑨；OOS「後站不准改成 In」；hollow 三 S（吸 C）；Stage 5 Files 准許清單＋F3／token／graph＝0（吸 C）。B 線讀倉／同桶／doctor／Q12／注入紅全留。不發明 G2 PASS。
- 本 hop 不送 G2 | 2026-09-14 | `verdict` 空；`status: draft`。
