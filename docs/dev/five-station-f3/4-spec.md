---
feature: five-station-f3
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站 F3 change spec（Winner A + owner standing soft-fix：cut 可見紀錄／讀鍵／graph+dual-read／doctor 清單／三路電池）

> Lane = **full**。G1 已核（`2-decision.md` `verdict: PASS`、`status: approved`、OC-1…OC-12 ✅）。Winner B soft-fix 骨架 **1A+2A+3C+4A+5A+6A**。本 hop **只**本目錄 `4-spec.md` + `4-spec.html`。`status: draft`。`verdict` 空。**不發明 G2 PASS**。不改 `STATUS.md`／`HISTORY.md`／`2-decision.md`／`3-prototype.md`。不 bump 契約、不改 `graph.yaml`、不改 doctor 握手、不寫 cut 碼。
> Stage 3：Winner A 九條 **0／9**；Demo verdict＝**N/A**。Human ACCEPTED 已落主線（#374／`34eec6b`；`human:rick @ 2026-09-14`；scenario＝0/9 Demo N/A accepted）。無 ACCEPTED 互動場景。本 hop **不改** `3-prototype.md`。
> Writer A 本站只釘 Decision 留給 4-spec 的形：**cut SoT＝語意槽 who／when／which_condition**；路徑＝獨立檔 `docs/dev/f3-cut-attestation.json`（**不是** `devflow-contract.json` 兄弟布林；**不是** silent `True`）。`contract_version()` **只讀** `devflow_contract_version`。graph **行為**＋ dual-read **都要**；機制＝條件邊＋路線閘（同一三前置）；`N7-g1`／`N6-g2` 節點與 token **不刪**。doctor **只加** `2.1.0` 進 supported。同一電池 NEW5＋OLD7＋TOKEN；極性＝注入壞行為→**該格**紅。F2 綠是地板。
> 原文獨立於 B／C（A 線當時未讀他稿）。**本檔含 owner standing soft-fix**（#378 多數勝出後吸收，非 A 線當時已讀他稿）。不換 winner。吸收 B（L1）：Files 准許清單**必須**含本 slug `5-tasks.md`／`6-implementation-notes.md`／`7-review.md`（＋html），且禁區 Diff Budget 0 寫在**同一條 S**（`_templates/`／doctor 握手／STATUS／本目錄當 NEW5／刪 token／重開 F2 park）；hollow＝用字獨立格、兩支腳本各綠 ≠ 同一電池、僅 html ≠ in-flight GWT；可選 `scripts/check-five-station-f3.sh`；marketplace／cache 不是第四條前置。吸收 C（L1）：KEEP-MK 具名 M 例；`which_condition` **只命名 cut 位元**（不把 S-1.1 撐成三前置 AND）。**不收** B 的 `condition: F3-cut-happened` 戳記、**不收**「只 hop-skip」讀 3C、**不收** C 的 Stage3 `NOT_REVIEWED`。
> 不重開 F2 park D-1／D-2／D-3／F-c-4。本 slug **不是**白老鼠。

## 補助模組生命週期（預覽）

主詞是「F3 cut：可見紀錄＋讀鍵＋graph 條件邊＋doctor supported」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：獨立 cut 紀錄檔、F3 單一電池入口、NEW5／OLD7 fixture 根
- 改行為（相關一格）：`f3_cut_happened()` 改讀紀錄；`contract_version()` 改只讀正本鍵；新 slug 不再例行停 `N7-g1`／`N6-g2`；supported 加 `2.1.0`；guide 七站單行改五站用語
- 退役：沒有
- 不動：G1／G2／`ACCEPTED` token 與檔、`N7-g1`／`N6-g2` 節點檔、`_doctor_impl.py` 握手語意、F2 park D-1…F-c-4、本 slug 舊 7、Stage 1–4 模板全文

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「F3 該把『之後才開、cut 當下尚無 1–7 `.md`』的 slug 預設改五站」 | 本方案處理 | R-3、S-3.1 |
| 「只把函式改 `True`、只改 guide 用字、或契約仍 `2.0.0` 就把 hops 當五站預設」 | 本方案處理 | S-1.3、S-2.6、S-3.3 |
| 「本目錄一有本檔就是 in-flight,拿自己當第一隻活五站 = 污染觀測」 | 本方案處理 | S-7.3、S-7.4 |
| Journey「新 slug 仍經 `N7-g1` 等人;chat 可蓋章」 | 本方案處理 | S-3.1、S-6.1 |
| Journey「doctor 綠只證明 `2.0.0 ∈ supported`≠切線」 | 本方案處理 | S-4.3 |
| Journey「coordinator 缺 cut → legacy；理由=`F3 cut 未發生`」 | 本方案處理 | S-2.4、S-2.5 |
| Workaround「恒 `False` 擋 live 五站；擋的是行為,不是人看得見的 cut 紀錄」 | 本方案處理 | R-1、S-1.1、S-1.4 |
| Workaround「STATUS／HISTORY 當刀口 log；看板列 ≠ cut」 | 本方案處理 | S-1.6、S-8.1 |
| Exception「不准改已經 freeze 的 slug」 | 本方案處理 | S-7.1、S-7.2 |
| Exception「只把函式改 True、不 bump、不改 hops = 空切」 | 本方案處理 | S-1.3、S-5.4 |
| Exception「契約仍 2.0.0 卻把 hops 當五站預設 = SLOT-REJECT」 | 本方案處理 | S-2.6、S-2.7 |
| Exception「只改 guide、graph 仍停 `N7-g1` = 用語切、行為沒切」 | 本方案處理 | S-3.3 |
| Exception「NEW5 不是本目錄、也不是 `five-station-f2`／`five-station-simplify`」 | 本方案處理 | S-7.4、S-7.5 |
| Q15 silent flip 不合法 | 本方案處理 | S-1.3 |
| Q16 2.1.0 必須同動或先於 hops 預設 | 本方案處理 | S-2.6、S-2.7 |
| Q17 只 bump 正本鍵、`declared` 仍假 | 本方案處理 | S-2.1、S-2.2 |
| Q18 bump 後 supported 未加 → 誠實紅 | 本方案處理 | S-4.2 |
| Q19 同一電池三路、hollow 不算 | 本方案處理 | S-5.1、S-5.4、S-5.5、S-5.6、S-5.9、S-5.10、S-5.11 |
| Q20 第三位元怎麼被指認 | 本方案處理 | S-1.1、S-1.5 |
| Q21 graph 四選項 | 本方案處理 | R-3、S-3.2、S-3.5 |
| Q22 改 doctor 實作還是只加清單 | 本方案處理 | S-4.1、S-4.4 |
| Q23 guide 用語算哪些檔 | 本方案處理 | S-1.6 |
| Q24 STATUS 用語 vs feature branch 禁碰 | 本方案處理 | S-1.6、S-8.1 |
| Q25 第一隻活五站叫什麼 | 本方案處理 | S-7.5 |
| Q26 三前置形狀、2.1.0 ≠ cut | 本方案處理 | S-2.4、S-2.5 |
| Q27 live reader 回空字串 | 本方案處理 | S-2.1、S-2.3 |
| 「鎖:不刪 G1／G2／`ACCEPTED`；不把 in-flight 折成五站；不拿本 slug 當白老鼠」 | 本方案處理 | S-5.8、S-7.2、S-7.3、S-8.3、S-8.4 |
| Q14 Backlog A 過期 | 刻意維持 | Out of Scope：本 PR 不改 STATUS |
| Q1–Q14／Q3 刀定義 | 本方案處理 | R-8、S-8.5 |

## SC → S 對照

Decision Success Criteria 每條至少一條獨立可測 S。CASE 表只准加不准減。

| SC | 一句 | 本檔 S |
|---|---|---|
| SC-BATTERY | 單一入口；NEW5＋OLD7＋TOKEN 都過才 exit 0；F2 綠不是第四條 IFF | S-5.1、S-5.7 |
| SC-F2-REGRESS | `test-five-station-f2.sh` exit 0、`failed=0`（地板） | S-5.7 |
| SC-NEW5-CUT-OK | cut 後新 slug 預設五站；無例行 G1／G2 停 | S-3.1 |
| SC-NEW5-WAIT-RED | 注入謂詞真仍例行停 `N7-g1` → 該格紅 | S-6.1 |
| SC-OLD7-FREEZE | 已有 1–7 `.md` → 舊 7；無五站狀態 | S-7.1 |
| SC-OLD7-FOLD-RED | 注入對 in-flight 寫五站 → 該格紅 | S-7.2 |
| SC-TOKEN-KEEP | token 與檔仍在；`check-gate-tokens.sh` 綠 | S-5.8 |
| SC-TOKEN-DEL-RED | 注入刪 token 卻標 F3 成功 → 該格紅 | S-8.4 |
| SC-ATTEST-VISIBLE | 人指得到 who／when／which_condition | S-1.1 |
| SC-ATTEST-SILENT-RED | 注入 silent `True` 無紀錄卻稱已切 → 該格紅 | S-1.3 |
| SC-PRE-210-NE-CUT | 2.1.0 真、cut 假 → `allow_legacy()`；理由含「F3 cut 未發生」 | S-2.4 |
| SC-PRE-AND | 三前置缺一 → `allow_legacy()` | S-2.5 |
| SC-PRE-HOPS-200 | 2.0.0＋五站 hops 預設 → SLOT-REJECT、未改線 | S-2.6 |
| SC-READ-SEAM | 注入只 bump 正本、reader 仍舊、卻稱已宣告 → 該格紅 | S-2.2 |
| SC-DOCTOR-HONEST | 2.1.0 ∉ supported → INCOMPATIBLE | S-4.2 |
| SC-DOCTOR-NE-TICKET | `COMPATIBLE`＋2.0.0 求五站 hop → 拒；理由是路線 | S-4.3 |
| SC-GRAPH-WORD-NE | 只改用字、新 slug 仍停 `N7-g1`、卻標成功 → 該格紅 | S-3.3 |
| SC-SELF-OLD7 | 對本目錄／F2／simplify 求五站自動前進 → 拒 | S-7.3 |
| SC-HOLLOW | 僅函式真／僅檔在／僅 F2 綠／僅用字標 F3 綠 → 非 0；兩支腳本各綠 ≠ 同一電池；僅 html ≠ in-flight GWT | S-5.4、S-5.5、S-5.6、S-5.9、S-5.10、S-5.11、S-3.3 |
| SC-KEEP | KEEP-MK-RED／KEEP-SHIP-MECH 為預期紅 | S-6.2、S-6.3 |
| SC-Q-CARRY | Q15–Q27 皆有去向 | 本節 Disposition；S-8.5 |
| SC-PR | **本 Stage 4 hop** 只 4-spec 雙檔、draft、無 G2 PASS、不改 STATUS | S-8.1 |

## CASE → S 對照（Decision 原 20 列＋standing 加列；只准加）

極性：標「→ 紅」＝**注入該壞行為**，該格必須獨立變紅。把「拒 hop」記成紅格綠＝極性反了，已拒。

| CASE | 路 | 紅／綠 | 本檔 S |
|---|---|---|---|
| NEW5-CUT-OK | NEW5 | 綠：cut 後無 1–7 `.md` → 預設五站 | S-3.1 |
| NEW5-WAIT-RED | NEW5 | **注入** 謂詞真、latch 假，仍例行停 `N7-g1`／留下「要不要繼續」（→ 紅） | S-6.1 |
| OLD7-FREEZE | OLD7 | 綠：已有 1–7 `.md` → 舊 7 | S-7.1 |
| OLD7-FOLD-RED | OLD7 | **注入** 對 in-flight 寫五站狀態／五站 hop（→ 紅） | S-7.2 |
| TOKEN-KEEP | TOKEN | 綠：G1／G2／`ACCEPTED` 仍在 | S-5.8 |
| TOKEN-DEL-RED | TOKEN | **注入** 刪 token 卻標 F3 成功（→ 紅） | S-8.4 |
| ATTEST-VISIBLE | ATTEST | 綠：人指得到三槽 | S-1.1 |
| ATTEST-SILENT-RED | ATTEST | **注入** 只 `return True`、無可見紀錄，卻宣稱已切（→ 紅） | S-1.3 |
| PRE-210-NE-CUT | PRE | 綠：2.1.0 真、cut 假 → `allow_legacy()` | S-2.4 |
| PRE-AND | PRE | 綠：三前置缺一 → `allow_legacy()` | S-2.5 |
| PRE-HOPS-200 | PRE | 綠：2.0.0＋五站 hops → SLOT-REJECT | S-2.6 |
| READ-SEAM | PRE | **注入** 只 bump 正本、reader 不讀它，卻稱已宣告（→ 紅） | S-2.2 |
| DOCTOR-HONEST | DOC | 綠：2.1.0 ∉ supported → INCOMPATIBLE | S-4.2 |
| DOCTOR-NE-TICKET | DOC | 綠：`COMPATIBLE`＋2.0.0 求五站 hop → 拒 | S-4.3 |
| GRAPH-WORD-NE | GRAPH | **注入** 只改用字、新 slug 仍停 `N7-g1`，卻標成功（→ 紅） | S-3.3 |
| SELF-OLD7 | SELF | 綠：本目錄／F2／simplify 求五站自動前進跳不過 | S-7.3 |
| HOLLOW-TRUE | HOLLOW | **注入** 把 `f3_cut_happened==True` 標成 F3 綠（→ 紅） | S-5.4 |
| HOLLOW-FILES | HOLLOW | **注入** 把「檔在」標成 F3 綠（→ 紅） | S-5.5 |
| HOLLOW-F2 | HOLLOW | **注入** 只跑 F2 電池綠就標 F3 綠（→ 紅） | S-5.6 |
| HOLLOW-WORD | HOLLOW | **注入** 只用字（guide／STATUS 用語）標 F3 綠（→ 紅）；獨立格，不是 GRAPH-WORD-NE 的附註 | S-5.9 |
| HOLLOW-TWO-SCRIPT | HOLLOW | **注入** 兩支腳本各綠一次就標同一電池綠（→ 紅） | S-5.10 |
| HOLLOW-HTML-NE-GWT | HOLLOW | 綠：目錄只有 `*.html`、零個 1–7 `.md` → **不是** in-flight GWT | S-5.11 |
| F3-F2-REGRESS | 地板 | 綠：F2 電池仍 exit 0；**不是** SC-BATTERY 第四路 | S-5.7 |
| KEEP-MK-RED | KEEP | **注入** Must-keep 紅仍 hop（→ 紅） | S-6.2 |
| KEEP-SHIP-MECH | KEEP | **注入** 機械全綠、無人寫 `verdict: PASS` 卻標 Ship Done（→ 紅） | S-6.3 |

減 Decision 原 20 列任一列 = 翻 Decision。standing 加列 PRE-AND、F3-F2-REGRESS、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT 不減。加列不得把「函式真／檔在／F2 綠／用字／兩支腳本各綠／僅 html」加成通過條件。

## ADDED Requirements

### R-1: 系統 SHALL 把 cut SoT 收成人類可見獨立紀錄的語意槽，且 `f3_cut_happened()` 只讀

1A＋OC-1／OC-2／OC-11。SoT＝檔上三個非空槽：`who`（誰）、`when`（何時）、`which_condition`（讀哪個條件＝**cut 位元本身**，不是三前置 AND）。路徑釘死＝`docs/dev/f3-cut-attestation.json`（獨立檔；**禁止**寫進 `devflow-contract.json` 當版本兄弟布林）。缺檔或任一槽空／缺席 → `f3_cut_happened()` 回 `False`。函式本體改 `return True` 且紀錄缺＝空切（ATTEST-SILENT-RED）。git blame 不是 `who`／`when`。STATUS／guide 用語是交付物，不是 SoT。F2 D-1 檔案地圖列仍 ≠ cut。`which_condition` **禁止**寫成 `F3-cut-happened` 戳記當唯一合法值；槽值命名 cut 位元即可。

**審的時候看什麼**
人能不能指出三槽。函式是不是只讀這份檔。silent `True` 那一格是不是紅。cut 鍵有沒有偷偷跟 `devflow_contract_version` 住同一份 JSON。

#### S-1.1 ATTEST-VISIBLE：三槽非空 → 人指得到且讀端回真
- GIVEN `docs/dev/f3-cut-attestation.json` 存在，且 JSON 物件含非空字串 `who`＝`rick`、`when`＝`2026-09-14T00:00:00+08:00`、`which_condition`＝`f3-cut`（只命名 cut 位元；**不是** `declared ∧ ¬in-flight ∧ cut` 的完整 AND；**不是**字面 `F3-cut-happened` 戳記）
- WHEN 人打開該檔，且呼叫 `f3_cut_happened(<專案根>)`
- THEN 人能逐字指出三個槽的值；函式回 `True`；回真的依據是這份檔，不是函式字面 `return True`。`which_condition` 只證明 cut 位元有被指認；`declared` 與 ¬in-flight 仍由 S-2.4／S-2.5 獨立評，不得因本槽非空就當三前置全真
- 觀測:從 `docs/dev/f3-cut-attestation.json` 與 `f3_cut_happened` 回傳看 | 三槽非空、`which_condition` 只含 cut 位元名、回 `True` 算過 | n-a:F3 碼未落地。替代：Decision CASE ATTEST-VISIBLE；後站電池該格
- Operational Context:
  - Actor:母版 owner
  - Goal:留下可指的 cut 紀錄
  - Situation:F3 要宣稱已切
  - Known information:SoT 是三槽，不是函式；三前置 AND 在路線閘，不在本槽
  - Missing information:後站何時寫入這份檔
  - Human decision:誰寫 `who`、何時寫 `when`；`which_condition` 只寫 cut 位元名
  - Authority:Agent 不得用 `return True` 冒充已切；不得把 declare／in-flight 捆進本槽
  - External dependency:無
  - Out-of-system action:owner 在 git 提交這份檔
  - Waiting/timeout behavior:檔未寫＝未切，無逾時自動變真
  - Recovery:刪檔或清空任一槽 → 讀端回 `False`
  - Audit/handoff requirement:三槽留在版控檔，可供 7-review 指到
  - Observation:見本條觀測

#### S-1.2 缺檔或空槽 → 讀端回假
- GIVEN 下列任一：檔不存在；檔在但 `who` 為 `""`；檔在但缺 `when` 鍵
- WHEN 呼叫 `f3_cut_happened(<專案根>)`
- THEN 回 `False`；不得因契約已是 `2.1.0` 或 guide 已寫「五站」而回 `True`
- 觀測:從函式回傳看 | 缺檔／空槽＝`False` 算過 | n-a:F3 碼未落地。替代：Decision 約束 3
- Operational Context:不適用 — 讀端布林，無新交接畫面。

#### S-1.3 ATTEST-SILENT-RED：注入 silent True 無紀錄卻稱已切 → 該格紅
- GIVEN 電池 ATTEST-SILENT-RED 格；tree 無合格三槽紀錄（缺檔或任一槽空）
- WHEN 注入把 `f3_cut_happened` 改成字面 `return True`，且宣稱 F3 已切
- THEN **該格紅**（獨立非 0）；不得把「函式回真」記成該格綠
- 觀測:從 F3 電池 ATTEST-SILENT-RED 格 exit／標誌看 | 注入後該格紅算過 | n-a:電池未落地。替代：Decision CASE ATTEST-SILENT-RED；1-discussion AC-4
- Operational Context:
  - Actor:Ship 審查者／電池
  - Goal:擋空切
  - Situation:有人只翻函式
  - Known information:無三槽紀錄
  - Missing information:無
  - Human decision:該格紅不得改可選
  - Authority:後站不得把此格改綠當成功
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:補上合格三槽後，本格不再適用（改測 ATTEST-VISIBLE）
  - Audit/handoff requirement:紅格輸出可指
  - Observation:見本條觀測

#### S-1.4 函式只讀、不寫判定
- GIVEN 合格三槽檔已在，或檔不在
- WHEN `f3_cut_happened(<專案根>)` 被呼叫
- THEN 函式不建立、不覆寫、不刪 `docs/dev/f3-cut-attestation.json`；回傳只反映呼叫當下檔上三槽是否齊
- 觀測:從呼叫前後該檔的存在與內容看 | 位元組不變算過 | n-a:F3 碼未落地。替代：Decision 約束 3；OC-1
- Operational Context:不適用 — 讀端無寫入。

#### S-1.5 cut 不得鎖成契約檔兄弟布林
- GIVEN `devflow-contract.json` 現況鍵是 `devflow_contract_version`
- WHEN 有人把 cut 寫成同一份 JSON 的兄弟鍵（例：`f3_cut_happened: true`）並稱這是 SoT
- THEN 該寫法被拒；SoT 仍是 `docs/dev/f3-cut-attestation.json` 的三槽；2.1.0 宣告仍 ≠ cut
- 觀測:從 cut 紀錄路徑與 `devflow-contract.json` 鍵集合看 | 契約檔無 cut 兄弟鍵當 SoT 算過 | 本 tree `devflow-contract.json` 現況 + Decision 約束 3
- Operational Context:不適用 — 檔形約束。

#### S-1.6 用語／blame／看板 ≠ SoT；guide 仍是交付物
- GIVEN guide 至少含 `guides/guide-dev-flow.html` 現況七站單行；STATUS 政策禁 feature branch 碰正本表列
- WHEN 有人用 git blame、STATUS Active 列、或只改 guide／STATUS 用字宣稱 cut 已發生
- THEN 宣稱失敗；SoT 仍是三槽檔。guide 七站單行**必須**在後站改成五站用語（交付物），但改完仍 ≠ 成功充分條件。STATUS 用語切走整合分支 companion；本 feature branch、本 PR 不改 `STATUS.md`
- 觀測:從 cut 紀錄檔、`guides/guide-dev-flow.html`、本 PR `git diff --name-only` 看 | 無 STATUS；blame／看板不能讓 `f3_cut_happened` 變真算過 | 本 tree `guides/guide-dev-flow.html`；`docs/dev/STATUS.md` L10-L13；F2 D-1
- Operational Context:
  - Actor:母版 owner／看板寫手
  - Goal:用語切五站，但不拿看板當刀
  - Situation:feature branch 禁碰 STATUS 正本
  - Known information:F2 D-1 檔案地圖列 ≠ cut
  - Missing information:companion PR 何時開
  - Human decision:STATUS 用語只在整合分支寫
  - Authority:本 PR 不得改 STATUS
  - External dependency:整合分支 companion
  - Out-of-system action:合併後才跑 `status-update.sh`
  - Waiting/timeout behavior:companion 未開 ≠ 未切
  - Recovery:誤改 STATUS → 本 S 紅
  - Audit/handoff requirement:本 PR 檔集可稽核
  - Observation:見本條觀測

### R-2: 系統 SHALL 讓 `contract_version()` 只讀 `devflow_contract_version`，且 2.1.0 ≠ cut

2A＋OC-3／OC-4。落地後 `contract_version()` **只讀**正本鍵 `devflow_contract_version`。禁止 fallback／dual-read `version`／`contract_version`。只 bump 那兩個錯鍵 ≠ 已宣告。正本鍵值以 `2.1` 開頭 → `declared` 真。三前置繼承 F2 4A／S-7.1：`declared` ∧ ¬in-flight ∧ cut；缺一 → `allow_legacy()`。hops 預設五站不得早於 2.1.0 已宣告。2.0.0＋五站 hops 預設＝SLOT-REJECT，不得改線。

**審的時候看什麼**
讀錯鍵會不會仍回空字串。2.1.0 能不能單獨冒充 cut。缺 cut 時拒絕理由是不是「F3 cut 未發生」。

#### S-2.1 只讀正本鍵；錯鍵不冒充
- GIVEN 專案樹 `devflow-contract.json` 只有 `devflow_contract_version`＝`2.0.0`，沒有 `version`／`contract_version` 鍵（本 tree 現況）
- WHEN 呼叫落地後的 `contract_version(<專案根>)`
- THEN 回傳 `2.0.0`（以正本鍵為準）；不得回 `""`；不得去讀 `version` 或 `contract_version`
- 觀測:從 `contract_version()` 回傳與函式讀鍵清單看 | 回 `2.0.0` 且原始碼無 `blob.get("version")`／`blob.get("contract_version")` 算過 | 現況 `scripts/five_station_f2.py` L260-L268 讀錯鍵回 `""`＝本條要修的縫；`devflow-contract.json` L1-L2
- Operational Context:不適用 — 讀鍵，無人員交接。

#### S-2.2 READ-SEAM：注入只 bump 正本、reader 仍舊、卻稱已宣告 → 該格紅
- GIVEN 電池 READ-SEAM 格；`devflow-contract.json` 的 `devflow_contract_version` 已改成 `2.1.0`；reader 仍只讀 `version`／`contract_version`
- WHEN 有人宣稱「已宣告 2.1.0」
- THEN **該格紅**；`declared` 仍假（reader 回 `""` 或不以 `2.1` 開頭）
- 觀測:從 READ-SEAM 格與 `contract_version()` 回傳看 | 注入後該格紅、回傳不以 `2.1` 開頭算過 | n-a:F3 reader 未落地。替代：Decision CASE READ-SEAM；Q27 已核空字串
- Operational Context:不適用 — 注入格。

#### S-2.3 正本鍵 2.1.0 且 reader 已修 → declared 真
- GIVEN 落地後 reader 只讀 `devflow_contract_version`；該鍵＝`2.1.0`
- WHEN 評 `declared`
- THEN `contract_version()` 回傳以 `2.1` 開頭；`declared` 真。**cut 位元仍獨立**：本條不把 `declared` 真寫成 cut 真
- 觀測:從 `contract_version()` 回傳看 | 以 `2.1` 開頭算過 | n-a:未 bump。替代：Decision 約束 5
- Operational Context:不適用 — 宣告布林。

#### S-2.4 PRE-210-NE-CUT：2.1.0 真、cut 假 → allow_legacy；理由含「F3 cut 未發生」
- GIVEN `declared` 真（正本鍵 `2.1.0` 且 reader 已修）；slug 無 1–7 `.md`（¬in-flight）；`docs/dev/f3-cut-attestation.json` 缺席或任一槽空（cut 假）
- WHEN 對該 slug 求五站路線
- THEN `allow_legacy()`；拒絕理由含字面 `F3 cut 未發生`；理由不含「已宣告所以切了」
- 觀測:從 `allow_legacy`／`refuse_hop_reason` 看 | legacy 真且理由含 `F3 cut 未發生` 算過 | 現況 `scripts/five_station_f2.py` L303-L307；Decision CASE PRE-210-NE-CUT
- Operational Context:
  - Actor:coordinator
  - Goal:第三位元可獨立為假
  - Situation:契約已 2.1.0 但 cut 紀錄沒寫
  - Known information:2.1.0 ≠ cut
  - Missing information:無
  - Human decision:不得把 bump 當成 cut
  - Authority:coordinator 禁寫判定；只讀
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:寫合格三槽後才可能走五站（仍須另兩前置）
  - Audit/handoff requirement:拒因字面可稽核
  - Observation:見本條觀測

#### S-2.5 PRE-AND：三前置缺一 → allow_legacy
- GIVEN 三前置（`declared` ∧ ¬in-flight ∧ cut）任一為假；另兩條為真
- WHEN 對該 slug 求五站路線
- THEN `allow_legacy()`；不建五站機。缺 `declared` → 理由含 `路線未宣告` 或 `仍舊 7`；缺 ¬in-flight → 理由含 `in-flight`；缺 cut → 理由含 `F3 cut 未發生`
- 觀測:從三組缺一 fixture 的拒絕理由看 | 三組皆 legacy 且理由對得上缺的那一條算過 | Decision CASE PRE-AND；F2 S-7.1
- Operational Context:不適用 — 同一路線閘，無新畫面。

#### S-2.6 PRE-HOPS-200：2.0.0＋五站 hops 預設 → SLOT-REJECT、未改線
- GIVEN 契約 `devflow_contract_version` 仍＝`2.0.0`；有人把 hops 預設當成五站（新 slug 不再進 `N7-g1`／`N6-g2`）
- WHEN 評採用端路線
- THEN 違規（F1 SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS）；**不得改線**；不得因 marketplace／plugin cache 已換 hops 而放行
- 觀測:從路線判定／SLOT-REJECT 牙看 | 2.0.0＋五站 hops 紅且路線仍舊 7 算過 | annex SLOT-REJECT；Decision CASE PRE-HOPS-200
- Operational Context:
  - Actor:採用專案 owner
  - Goal:升級後不被遠端改線
  - Situation:hops 已換、契約仍 2.0.0
  - Known information:未宣告＝舊 7
  - Missing information:採用端是否 bump
  - Human decision:採用端自己 bump 契約
  - Authority:marketplace 不得單獨改線
  - External dependency:採用端契約檔（系統外）
  - Out-of-system action:採用端改自己的 `devflow-contract.json`
  - Waiting/timeout behavior:未 bump 則持續舊 7
  - Recovery:宣告 2.1.0 後才可能改線（仍須 cut 與 ¬in-flight）
  - Audit/handoff requirement:SLOT-REJECT 輸出可指
  - Observation:見本條觀測

#### S-2.7 hops 預設五站不得早於 2.1.0 已宣告
- GIVEN 正本鍵尚未以 `2.1` 開頭（`declared` 假）
- WHEN 後站要把各站 `graph.yaml` 預設路改成跳過 `N7-g1`／`N6-g2`
- THEN 該改動與 2.1.0 宣告必須同刀或宣告在先；只切 graph、契約仍 2.0.0＝S-2.6 紅
- 觀測:從同一 PR／同一落地 commit 的契約鍵與 graph 預設邊看 | 宣告已真或 graph 仍進例行停點算過 | Decision 約束 6；OC-4
- Operational Context:不適用 — 同刀順序約束。

### R-3: 系統 SHALL 同時做 graph 行為切與 2.1.0 dual-read，且不刪節點

3C＋OC-5。dual-read：未宣告 2.1.0＝舊 7。graph **行為**：cut 後、非 in-flight 的新 slug 預設路**不再例行進** `N7-g1`／`N6-g2`。切換機制釘死＝各站 `graph.yaml` **條件邊**（真：跳過例行停點；假：仍進 `N7-g1`／`N6-g2`）＋ coordinator 路線閘讀**同一**三前置謂詞；兩邊必須同意。節點檔與 token **不刪**。只改 guide／STATUS 用字 ≠ 成功（GRAPH-WORD-NE）。

**審的時候看什麼**
新 slug 還等不等 G1／G2。未宣告的採用端有沒有被改線。`N7-g1.md`／`N6-g2.md` 還在不在。

#### S-3.1 NEW5-CUT-OK：cut 後無 1–7 `.md` → 預設五站、不等例行閘
- GIVEN 三前置全真；合成 fixture slug 在 cut 當下**沒有**任一 1–7 `.md`（路徑見 DD-3，不是本目錄）
- WHEN 對該 slug 求預設路線並走 Stage 2／Stage 4 hop
- THEN 預設五站；中間**沒有**例行「請人審」G1／G2 提交判定；不進入 `N7-g1`／`N6-g2` 當例行停點
- 觀測:從該 fixture 的 hop 紀錄／路線判定看 | 預設五站且無例行 G1／G2 停算過 | n-a:graph／coordinator 未落地。替代：Decision CASE NEW5-CUT-OK；1-discussion AC-1
- Operational Context:
  - Actor:新 slug 寫手（cut 後才開）
  - Goal:不等例行閘往下寫
  - Situation:cut 已發生、契約已宣告、目錄無站檔
  - Known information:摺的是例行停點，不是 Must-keep
  - Missing information:無
  - Human decision:Ship 仍唯人
  - Authority:Agent 仍禁寫 `ACCEPTED`／Ship `PASS`
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:例行 G1／G2 不再等；Ship 仍等
  - Recovery:任一前置變假 → 回舊 7
  - Audit/handoff requirement:hop 紀錄可指「未進 N7-g1」
  - Observation:見本條觀測

#### S-3.2 dual-read：未宣告 2.1.0 → 仍舊 7（即使 graph 檔已有條件邊）
- GIVEN 契約仍 `2.0.0`；`graph.yaml` 已含條件邊原文
- WHEN 對未宣告採用端的新 slug 求路線
- THEN 仍舊 7；條件邊的「跳過」側不得生效；marketplace 已換 hops ≠ 改線
- 觀測:從採用端假樹路線看 | 未宣告＝舊 7 算過 | F1 SLOT-UNDECLARED-ROUTE；Decision 3C
- Operational Context:不適用 — 與 S-2.6 同一閘，本條咬 graph 側不得單邊生效。

#### S-3.3 GRAPH-WORD-NE：注入只改用字、新 slug 仍停 N7-g1，卻標成功 → 該格紅
- GIVEN 電池 GRAPH-WORD-NE 格；`guides/guide-dev-flow.html` 已改寫「五站」；Stage 2 graph 預設仍進 `N7-g1`
- WHEN 有人標 F3 成功
- THEN **該格紅**；用語與行為分開記帳
- 觀測:從 GRAPH-WORD-NE 格看 | 注入後該格紅算過 | 現況 `guides/guide-dev-flow.html` L573 + `skills/dev-flow/stage2/graph.yaml` L53-L57；1-discussion AC-7
- Operational Context:不適用 — 注入格。

#### S-3.4 節點 N7-g1／N6-g2 與 token 檔不刪
- GIVEN 現況 `skills/dev-flow/stage2/nodes/N7-g1.md`、`skills/dev-flow/stage4/nodes/N6-g2.md`、`scripts/check-gate-tokens.sh` 所釘 token 檔
- WHEN F3 落地完成
- THEN 上述節點檔仍在；G1／G2／`ACCEPTED` token 字面仍在；`check-gate-tokens.sh` 仍綠
- 觀測:從 `ls`／`check-gate-tokens.sh` 看 | 檔在且牙 exit 0 算過 | 本 tree 節點與 `scripts/check-gate-tokens.sh` L44-L60
- Operational Context:不適用 — 檔保留。

#### S-3.5 coordinator 路線閘與 graph 條件邊讀同一三前置
- GIVEN 同一組（`declared`、in-flight、cut）布林
- WHEN graph 條件邊決定「進或不進 `N7-g1`／`N6-g2`」，且 coordinator `allow_legacy()` 決定五站或舊 7
- THEN 兩邊對同一組布林給同一答案；不得出現「graph 已跳過例行停、coordinator 仍 legacy」或反向
- 觀測:從同一 fixture 的 graph 下一跳與 `allow_legacy` 回傳看 | 同意算過 | n-a:未落地。替代：Decision OC-5 機制釘形＝條件邊＋路線閘
- Operational Context:不適用 — 雙讀一致性。

#### S-3.6 切換機制＝條件邊＋路線閘；不是刪節點、不是只翻函式
- GIVEN Q21 四選項已選定 3C
- WHEN 後站實作切換
- THEN 實作形是：`skills/dev-flow/stage2/graph.yaml` 與 `skills/dev-flow/stage4/graph.yaml` 的條件邊＋ `scripts/five_station_f2.py`（或後繼 `scripts/five_station_f3.py`）路線閘。禁止：刪 `N7-g1`／`N6-g2` 節點檔；只改 `f3_cut_happened` 可真而預設路仍進例行停（3D，已拒）
- 觀測:從 Files 准許清單與 git diff 檔名看 | 有條件邊與路線閘、無節點刪檔算過 | Decision 3C／3D Rejected
- Operational Context:不適用 — 機制形。

### R-4: 系統 SHALL 只把 2.1.0 寫進 supported，且綠≠ticket、漏加誠實紅

4A＋OC-6／OC-7。不改 `hooks/_doctor_impl.py` 握手語意。契約 bump 到 2.1.0 時，**只**把 `2.1.0` 寫進 `supported_contract_versions`（`hooks/runtime-capabilities.json` 與任何 runtime 同源清單）。漏加 → doctor **INCOMPATIBLE**。`COMPATIBLE`／exit 0 只證明握手，≠ cut、≠ 路條、≠ 第四條前置。marketplace／cache 同樣不是 ticket。

**審的時候看什麼**
supported 有沒有 `2.1.0`。漏了會不會紅。綠了會不會被拿去 hop。

#### S-4.1 同刀把 2.1.0 加進 supported；不改握手實作
- GIVEN 後站 bump `devflow_contract_version`＝`2.1.0`
- WHEN 同一落地把 `2.1.0` 寫入 `hooks/runtime-capabilities.json` 的 `supported_contract_versions`
- THEN 清單含字面 `2.1.0`；`hooks/_doctor_impl.py` 握手語意（版本必須 ∈ supported，否則 fail-closed）與現況相同
- 觀測:從 `hooks/runtime-capabilities.json` 與 `_doctor_impl.py` diff 看 | 清單含 `2.1.0`；握手函式無語意 diff 算過 | 現況 `hooks/runtime-capabilities.json` L1-L4 只聲明 `2.0.0`；`_doctor_impl.py` L193-L202
- Operational Context:不適用 — 清單與握手檔。

#### S-4.2 DOCTOR-HONEST：2.1.0 ∉ supported → INCOMPATIBLE
- GIVEN 契約鍵＝`2.1.0`；`supported_contract_versions` 仍只有 `2.0.0`
- WHEN 跑 `devflow-doctor.sh`（或等價 doctor 入口）
- THEN 印 `INCOMPATIBLE` 且非 exit 0；不得為了「升級好看」改成 `COMPATIBLE`
- 觀測:從 doctor stdout／exit 看 | `INCOMPATIBLE` 且非 0 算過 | Decision CASE DOCTOR-HONEST；`_doctor_impl.py` L193-L202
- Operational Context:
  - Actor:doctor 操作者
  - Goal:看見誠實紅
  - Situation:bump 了但清單沒跟上
  - Known information:綠的定義是版本 ∈ supported
  - Missing information:無
  - Human decision:補清單，不是放寬握手
  - Authority:不得改握手以求綠
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:把 `2.1.0` 寫進 supported 後可再綠（仍只握手）
  - Audit/handoff requirement:紅輸出可指
  - Observation:見本條觀測

#### S-4.3 DOCTOR-NE-TICKET：COMPATIBLE＋2.0.0 求五站 hop → 拒；理由是路線
- GIVEN 本 tree 契約 `2.0.0`；doctor 可印 `COMPATIBLE` 且 exit 0（現況握手綠）
- WHEN 有人把這次綠當 cut，或求五站 hop
- THEN 拒絕；理由含 `路線未宣告` 或 `仍舊 7` 或 `F3 cut 未發生`；理由**不含**「doctor 已綠所以可 hop」
- 觀測:從該次 hop 拒絕理由看 | 理由是路線、不是 doctor 綠算過 | 本 tree 現況可測；Decision CASE DOCTOR-NE-TICKET；1-discussion AC-6
- Operational Context:
  - Actor:doctor 操作者／新 slug 寫手
  - Goal:綠不當路條
  - Situation:doctor 剛印 COMPATIBLE
  - Known information:SLOT-DOCTOR-GREEN-MEANS
  - Missing information:無
  - Human decision:不得跟 hops
  - Authority:coordinator 丟棄 doctor 綠
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:無；綠永遠只握手
  - Audit/handoff requirement:拒因可指
  - Observation:見本條觀測

#### S-4.4 不改 `_doctor_impl.py` 握手語意
- GIVEN F3 Files 准許清單
- WHEN 後站落地 doctor 相關 diff
- THEN 准改的是 supported 清單；禁止改「版本 ∈ supported 才 COMPATIBLE」這句握手；禁止放寬 2.1.0 ∉ supported 仍綠（4C，已拒）；禁止把綠定義改成「路線 OK／已切」（4B，已拒）
- 觀測:從 `_doctor_impl.py` 握手段 diff 看 | 握手段空 diff 或僅非語意註解算過 | F2 4-spec Out #12；Decision 約束 8／9
- Operational Context:不適用 — 檔 diff 約束。

#### S-4.5 marketplace／cache 不是第四條前置
- GIVEN 三前置為：宣告 2.1.0 ∧ ¬in-flight ∧ cut 已發生
- WHEN 有人只證明 marketplace update 或 plugin cache 已有五站 hops 碼
- THEN 仍 `allow_legacy()`；marketplace／cache **不是**第四條前置，也不是 cut，也不是路條
- 觀測:從路線閘輸入看 | 缺任一前置仍舊 7；cache 位址不構成放行算過 | Decision 約束 8；F2 S-3.2／S-3.6
- Operational Context:不適用 — 前置清單。

### R-5: 系統 SHALL 用同一電池跑 NEW5＋OLD7＋TOKEN，且注入壞行為該格紅

5A＋OC-8／OC-12。單一入口＝`scripts/test-five-station-f3.sh`。exit 0 **當且僅當** NEW5 組、OLD7 組、TOKEN 組都過。缺一組、跳過一組、或入口只轉呼叫 `scripts/test-five-station-f2.sh` → 非 0。F2 綠是地板（F3-F2-REGRESS），**不是**第四條 IFF。具名 hollow：函式真／檔在／只 F2 綠／**只用字**／**兩支腳本各綠**／**僅 html 當 in-flight GWT**。極性＝注入壞行為→**該格**紅。

**審的時候看什麼**
是不是同一 process。紅格是不是餵壞行為。F2 綠有沒有被寫進 IFF。

#### S-5.1 SC-BATTERY：單一入口；缺一路即非 0
- GIVEN 入口 `scripts/test-five-station-f3.sh`；NEW5／OLD7／TOKEN 三組 fixture 都在
- WHEN 跑該入口
- THEN exit 0 **當且僅當**三組都過。缺一組、跳過一組、或入口只 `exec`／只轉呼叫 `scripts/test-five-station-f2.sh` → 非 0
- 觀測:從該入口原始 stdout／exit 看 | 三組全過才 0；少一組非 0 算過 | n-a:入口未落地。替代：Decision SC-BATTERY
- Operational Context:不適用 — 電池入口。

#### S-5.2 不得減 Decision CASE 原 20 列
- GIVEN 本檔 CASE → S 對照表
- WHEN 後站寫電池
- THEN Decision 原 20 列（NEW5-CUT-OK…KEEP-SHIP-MECH 不含 standing 加列之前的集合）每列都有對應格；standing 加列 PRE-AND、F3-F2-REGRESS 仍在；減任一原列＝翻 Decision
- 觀測:從電池 CASE 名清單與本檔對照表看 | 原 20 列皆在算過 | Decision「只准加不准減」
- Operational Context:不適用 — 表列完整性。

#### S-5.3 極性：注入壞行為 → 該格紅；拒 hop 不得當紅格綠
- GIVEN 任一標「→ 紅」的 CASE
- WHEN 測法改成「coordinator 拒 hop／拒寫」並把該格標綠
- THEN 整電池非 0（極性反了，已拒）
- 觀測:從極性探針看 | 拒 hop 當紅格綠 → 入口非 0 算過 | Decision 約束 16
- Operational Context:不適用 — 測法極性。

#### S-5.4 HOLLOW-TRUE：注入把函式真標成 F3 綠 → 該格紅
- GIVEN 電池 HOLLOW-TRUE 格
- WHEN 注入把 `f3_cut_happened==True` 標成 F3 綠（無三路、無可見紀錄要求）
- THEN **該格紅**
- 觀測:從 HOLLOW-TRUE 格看 | 注入後該格紅算過 | Decision CASE HOLLOW-TRUE；1-discussion 具名 hollow
- Operational Context:不適用 — 注入格。

#### S-5.5 HOLLOW-FILES：注入把「檔在」標成 F3 綠 → 該格紅
- GIVEN 電池 HOLLOW-FILES 格
- WHEN 注入只證明 F3 相關檔存在就標 F3 綠
- THEN **該格紅**
- 觀測:從 HOLLOW-FILES 格看 | 注入後該格紅算過 | Decision CASE HOLLOW-FILES；F2 D-1 同類
- Operational Context:不適用 — 注入格。

#### S-5.6 HOLLOW-F2：注入只跑 F2 電池綠就標 F3 綠 → 該格紅
- GIVEN 電池 HOLLOW-F2 格
- WHEN 注入只跑 `scripts/test-five-station-f2.sh` 得 exit 0、`failed=0` 就標 F3 綠
- THEN **該格紅**
- 觀測:從 HOLLOW-F2 格看 | 注入後該格紅算過 | Decision CASE HOLLOW-F2
- Operational Context:不適用 — 注入格。

#### S-5.7 F3-F2-REGRESS：F2 電池仍綠（地板，不是 IFF）
- GIVEN F3 落地樹
- WHEN 跑 `scripts/test-five-station-f2.sh`
- THEN exit 0 且 stdout 含 `failed=0`。本格綠 **不得**寫進 SC-BATTERY 的 IFF 第四路；單獨本格綠 ≠ F3 完
- 觀測:從 F2 電池原始 stdout／exit 看 | exit 0 且 `failed=0` 算過 | 本 hop 可先跑現況當地板；Decision CASE F3-F2-REGRESS
- Operational Context:不適用 — 回歸地板。

#### S-5.8 TOKEN-KEEP：G1／G2／ACCEPTED 仍在
- GIVEN F3 落地樹
- WHEN 跑 `scripts/check-gate-tokens.sh`
- THEN exit 0；G1／G2／`ACCEPTED` token 字面與檔仍在
- 觀測:從 `scripts/check-gate-tokens.sh` stdout／exit 看 | exit 0 且 token 字面仍在算過 | 本 tree 現況牙；1-discussion AC-3
- Operational Context:不適用 — token 牙。

#### S-5.9 HOLLOW-WORD：注入只用字標 F3 綠 → 該格紅
- GIVEN 電池 HOLLOW-WORD 格；僅 guide／STATUS 用語已切，三路未過
- WHEN 注入把「用字已切」標成 F3 綠
- THEN **該格獨立紅**。本格不是 S-3.3 GRAPH-WORD-NE 的附註：S-3.3 咬「graph 仍停卻標成功」；本格咬「只用字＝hollow」
- 觀測:從 HOLLOW-WORD 格看 | 注入後該格紅算過 | Decision SC-HOLLOW (d)；standing 加列
- Operational Context:不適用 — 注入格。

#### S-5.10 HOLLOW-TWO-SCRIPT：兩支腳本各綠 ≠ 同一電池
- GIVEN NEW5 腳本與 OLD7 腳本（或 `test-five-station-f3.sh` 與另一支 check）分開跑、各 exit 0，沒有單一 process 入口把三路跑完
- WHEN 有人標 SC-BATTERY 綠
- THEN **該格獨立紅**。兩支腳本各綠一次 ≠ 同一電池
- 觀測:從是否存在單一 process 入口看 | 兩支腳本各綠不算同一電池算過 | Decision 約束 11
- Operational Context:不適用 — 入口形。

#### S-5.11 HOLLOW-HTML-NE-GWT：僅 html ≠ in-flight GWT
- GIVEN 目錄只有 `*.html`、零個 1–7 `.md`
- WHEN 評 `has_old7`／in-flight
- THEN 不是 in-flight；不得把 html twin 當成 1–7 GWT 已在飛。僅 html ≠ 已有站檔
- 觀測:從 `has_old7` 回傳看 | 假算過 | F1 SLOT-IN-FLIGHT-DETECT
- Operational Context:不適用 — 偵測邊界。

### R-6: 系統 SHALL 摺例行停點、不摺完整度，且三失敗各自可紅

G-keep-1。摺的是新 slug 例行 `N7-g1`／`N6-g2`，不是 Must-keep、不是 Ship 唯人。三種失敗不得因「已經 cut 了」變綠。

**審的時候看什麼**
cut 之後 Must-keep 紅還能不能 hop。機械綠能不能自己 Ship Done。謂詞真了還會不會留下「要不要繼續」。

#### S-6.1 NEW5-WAIT-RED：注入謂詞真仍例行停 N7-g1 → 該格紅
- GIVEN 電池 NEW5-WAIT-RED 格；三前置真；latch 假
- WHEN 注入仍例行進入 `N7-g1`、或留下「要不要繼續／請人審」句，卻標 F3 成功
- THEN **該格紅**
- 觀測:從 NEW5-WAIT-RED 格看 | 注入後該格紅算過 | Decision CASE NEW5-WAIT-RED；1-discussion AC-10(1)
- Operational Context:
  - Actor:新 slug 寫手
  - Goal:不等例行閘
  - Situation:謂詞已真、有人仍停 G1
  - Known information:3C 已鎖 observable
  - Missing information:無
  - Human decision:該格紅不得改可選
  - Authority:chat 蓋章 ≠ 審查
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:例行停＝本格要抓的壞行為
  - Recovery:拿掉例行停後走 S-3.1
  - Audit/handoff requirement:紅格可指
  - Observation:見本條觀測

#### S-6.2 KEEP-MK-RED：注入 Must-keep 紅仍 hop → 該格紅
- GIVEN 電池 KEEP-MK-RED 格；NEW5；三前置全真；F2 已核 M1–M16 **任一**紅（例：M3 某 S 缺觀測欄；M5 代填 `ACCEPTED`；M9 Files 超出聯集；M11 T 缺 Verify；M12 reviewer＝implementer；M15 token 被刪）
- WHEN 注入「該 M 紅仍 hop」，且用「已經 cut 了」當理由
- THEN **該格紅**。不得用 cut 省略。只擋 M11、其餘 M 紅仍 hop＝本條紅
- 觀測:從 KEEP-MK-RED 格看 | 注入後該格紅；拒絕理由含該 M 編號算過 | Decision CASE KEEP-MK-RED；F2 S-6.5 回歸
- Operational Context:不適用 — 注入格；完整度牙已在 F0–F2。

#### S-6.3 KEEP-SHIP-MECH：注入機械綠無人 PASS 卻 Ship Done → 該格紅
- GIVEN 電池 KEEP-SHIP-MECH 格
- WHEN 注入機械全綠、無人在 7-review 頂欄寫 `verdict: PASS`，卻標 Ship Done
- THEN **該格紅**
- 觀測:從 KEEP-SHIP-MECH 格與 7-review 頂欄看 | 注入後該格紅算過 | Decision CASE KEEP-SHIP-MECH
- Operational Context:
  - Actor:Ship 審查者
  - Goal:機械綠 ≠ PASS
  - Situation:電池全綠、頂欄空
  - Known information:G3 唯人
  - Missing information:無
  - Human decision:只有人寫 `verdict: PASS`
  - Authority:Agent 禁代填 PASS
  - External dependency:無
  - Out-of-system action:人在審頁提交判定
  - Waiting/timeout behavior:無人寫則留 Ship，無逾時自動 Done
  - Recovery:人寫 PASS 後才 Done
  - Audit/handoff requirement:頂欄是正本
  - Observation:見本條觀測

### R-7: 系統 SHALL 凍結 in-flight（含本目錄），且 NEW5 試體不是白老鼠

6A＋OC-9。cut 當下已有任一 1–7 `.md` → 整段舊 7 到 Ship；無五站狀態寫入；三 cap 不套。對本目錄／`five-station-f2`／`five-station-simplify` 求五站自動前進 → 跳不過。NEW5＝`scripts/fixtures/five-station-f3/new5/` 合成 fixture，或 cut **之後**才開的 slug。**不發明**第一隻活五站名字。

**審的時候看什麼**
本目錄有沒有被建成五站機。OLD7 fixture 有沒有被折。試體路徑是不是合成根。

#### S-7.1 OLD7-FREEZE：已有 1–7 `.md` → 舊 7、無五站狀態
- GIVEN OLD7 fixture（DD-4）已有至少一個 1–7 `.md`；三前置其他位元任意
- WHEN 求切五站或建五站機
- THEN 整段舊 7（例行 G1／條件 S3／G2／G3 仍在）；目錄無五站狀態寫入；三 cap 不套
- 觀測:從該 fixture 目錄與 hop 看 | 無五站狀態、仍舊 7 算過 | Decision CASE OLD7-FREEZE；SLOT-IN-FLIGHT-DETECT
- Operational Context:
  - Actor:in-flight slug 執行者
  - Goal:走完手上舊 7
  - Situation:目錄已有站檔
  - Known information:僅 html 不算 in-flight
  - Missing information:無
  - Human decision:不得中途折五站
  - Authority:coordinator 放手給既有 graph
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:仍等既有閘
  - Recovery:無；freeze 到 Ship
  - Audit/handoff requirement:站檔仍是 1–7 家族
  - Observation:見本條觀測

#### S-7.2 OLD7-FOLD-RED：注入對 in-flight 寫五站 → 該格紅
- GIVEN 電池 OLD7-FOLD-RED 格；fixture 已有 1–7 `.md`
- WHEN 注入對該 slug 寫五站狀態或五站 hop
- THEN **該格紅**
- 觀測:從 OLD7-FOLD-RED 格看 | 注入後該格紅算過 | Decision CASE OLD7-FOLD-RED
- Operational Context:不適用 — 注入格。

#### S-7.3 SELF-OLD7：本目錄／F2／simplify 求五站自動前進 → 跳不過
- GIVEN `docs/dev/five-station-f3/` 已有 `1-discussion.md`（本 hop 另有 `2-decision.md`／`3-prototype.md`／本檔）；`docs/dev/five-station-f2/` 與 `docs/dev/five-station-simplify/` 亦已有 1–7 `.md`
- WHEN 對上述任一目錄求五站自動前進
- THEN 跳不過；無五站機寫入；本目錄出貨路徑仍舊 7
- 觀測:從被拒絕的 hop 與目錄檔名看 | 仍是舊 7 站檔、無五站狀態算過 | 本目錄現況；Decision CASE SELF-OLD7；1-discussion AC-8
- Operational Context:
  - Actor:F3 實作 agent
  - Goal:不污染觀測
  - Situation:本檔一落盤即 in-flight
  - Known information:Q4／Q25／OC-9
  - Missing information:無
  - Human decision:第一隻活五站另開（本檔不發明名字）
  - Authority:對本目錄建五站機＝X4
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:本 slug 仍等舊 7 閘
  - Recovery:無；freeze 到 Ship
  - Audit/handoff requirement:目錄檔名可指
  - Observation:見本條觀測

#### S-7.4 NEW5 試體＝合成 fixture 或 cut 之後才開的 slug
- GIVEN 電池 NEW5 路
- WHEN 選試體根
- THEN 根＝`scripts/fixtures/five-station-f3/new5/`（合成），或一個 **cut 之後**才建立、cut 當下無 1–7 `.md` 的 slug。禁止：`docs/dev/five-station-f3/`、`docs/dev/five-station-f2/`、`docs/dev/five-station-simplify/`
- 觀測:從 fixture 路徑與電池 NEW5 根看 | 路徑落在合成根或 post-cut 新 slug 算過 | Decision 約束 12
- Operational Context:不適用 — 試體路徑。

#### S-7.5 不發明第一隻活五站名字
- GIVEN Q25／OC-9
- WHEN 本檔或後站 5-tasks／6-notes 提到「第一隻活五站」
- THEN 不寫出具體 slug 名當已核目標；只寫「合成 fixture 或 cut 之後才開」
- 觀測:從本檔全文與後站 Files 看 | 無「活五站 slug＝<name>」已核句算過 | 本檔搜尋；Decision OC-9
- Operational Context:不適用 — 命名禁令。

### R-8: 系統 SHALL 鎖死 Non-Goals 與 Stage 5–7 Files 准許清單，且本 hop 只交 draft 規格雙檔

6A。後站不准把鎖改成 In。本 Stage 4 hop：只 `4-spec.md`＋`4-spec.html`；`status: draft`；`verdict` 空；不改 STATUS；不發明 G2 PASS。

**審的時候看什麼**
本 PR 檔集。Files 准許清單有沒有含本 slug 5／6／7（＋html），且禁區 Diff Budget 0 是否寫在同一條。Q15–Q27 有沒有下落。

#### S-8.1 本 Stage 4 hop 只 4-spec 雙檔、draft、無 G2 PASS、不改 STATUS
- GIVEN 本 PR 相對 `origin/main`
- WHEN 列 `git diff --name-only origin/main`
- THEN 檔集＝`docs/dev/five-station-f3/4-spec.md` 與 `docs/dev/five-station-f3/4-spec.html`。本檔頂欄 `status: draft`、`verdict` 空（或僅空白）。無 `STATUS.md`／`HISTORY.md`／`2-decision.md`／`3-prototype.md`／`graph.yaml`／契約／doctor／coordinator
- 觀測:從 `git diff --name-only origin/main` 與本檔 frontmatter 看 | 兩檔、draft、verdict 空算過 | 本 hop 檔集
- Operational Context:
  - Actor:Writer A／reviewer
  - Goal:交 draft 規格，不自填 G2
  - Situation:G1 已過、Stage 3 N/A 已接受
  - Known information:四眼；author ≠ approver
  - Missing information:G2 人類判定
  - Human decision:G2 由 reviewer／owner 寫頂欄
  - Authority:本 hop Agent 禁寫 `verdict: PASS`
  - External dependency:無
  - Out-of-system action:coordinator 下一問才是人審 G2
  - Waiting/timeout behavior:等人審；無逾時自動 PASS
  - Recovery:誤填 PASS → 本 S 紅
  - Audit/handoff requirement:frontmatter 可指
  - Observation:見本條觀測

#### S-8.2 Stage 5–7 Files 准許清單與禁區 Diff Budget 0
- GIVEN 後站 5-tasks Files 聯集
- WHEN 實作 F3 cut
- THEN 只准下列路徑（可少用、不可超）：`guides/guide-dev-flow.html`；`devflow-contract.json`（只 bump `devflow_contract_version`）；`hooks/runtime-capabilities.json`（只加 `2.1.0`）；`skills/dev-flow/stage2/graph.yaml`；`skills/dev-flow/stage4/graph.yaml`（條件邊；節點檔不刪）；`scripts/five_station_f2.py` 與／或 `scripts/five_station_f3.py`（讀鍵＋cut 讀端＋路線閘）；`docs/dev/f3-cut-attestation.json`；`scripts/test-five-station-f3.sh`；`scripts/check-five-station-f3.sh`（可選獨立 check 入口）；`scripts/fixtures/five-station-f3/`；**本目錄** `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html。下列區塊 Diff Budget **必須＝0**，否則本條紅：`_templates/` Stage 1–4 正文；`hooks/_doctor_impl.py` 握手語意；`docs/dev/STATUS.md`／`HISTORY.md`（看板另 companion）；把本目錄當 NEW5 fixture；刪 G1／G2／`ACCEPTED` token 檔；重開 F2 park D-1／D-2／D-3／F-c-4
- 觀測:從 5-tasks Files 聯集與 git diff 檔名看 | 超出准許清單或禁區行數 ≠ 0 → 本條紅算過 | 本條即准許清單＋禁區正本
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:只施工 F3 cut 准許檔
  - Situation:G2 剛過
  - Known information:准許清單具名；禁區＝0；本 slug 過程檔必須在清單內
  - Missing information:有沒有人想順便刪閘或改 STATUS
  - Human decision:STATUS 用語走整合分支 companion
  - Authority:本 R
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:把禁區檔從 Files 刪掉
  - Audit/handoff requirement:5-tasks Files
  - Observation:見本條觀測

#### S-8.3 Diff Budget 0：刪 token／折 in-flight／重開 F2 park 或 F2 R/S
- GIVEN 後站 diff
- WHEN 出現下列任一：刪 G1／G2／`ACCEPTED` token 或檔；對 in-flight 寫五站狀態；重開 F2 park D-1／D-2／D-3／F-c-4；改 `docs/dev/five-station-f2/` 已封 R／S 當本刀 In
- THEN 該 diff **0 檔 0 行**被允許；出現＝本 S 紅、翻 Decision
- 觀測:從 git diff 檔名與 `docs/dev/five-station-f2/` 是否被改看 | 上述集合空 diff 算過 | Decision Non-Goals 1–4／15
- Operational Context:不適用 — Diff Budget 0 約束。

#### S-8.4 TOKEN-DEL-RED：注入刪 token 卻標 F3 成功 → 該格紅
- GIVEN 電池 TOKEN-DEL-RED 格
- WHEN 注入刪 G1／G2／`ACCEPTED` token 或檔，卻標 F3 成功
- THEN **該格紅**
- 觀測:從 TOKEN-DEL-RED 格看 | 注入後該格紅算過 | Decision CASE TOKEN-DEL-RED
- Operational Context:不適用 — 注入格。

#### S-8.5 Q15–Q27 皆有去向
- GIVEN 本檔 Real-world Disposition
- WHEN 對 Q15–Q27 逐條找去向
- THEN 每條都是「本方案處理」且下落含 R- 或 S-，或「刻意維持」且下落非空；沒有消失
- 觀測:從本檔 Disposition 表看 | Q15–Q27 皆有列算過 | 本檔 Disposition；1-discussion AC-11
- Operational Context:不適用 — 對帳表。

#### S-8.6 不重開 F2 park D-1／D-2／D-3／F-c-4
- GIVEN F2 7-review 已 park D-1／D-2／D-3／F-c-4
- WHEN 本刀 4-spec／後站 5-tasks 列 In
- THEN 上述四項不出現在 In；出現＝翻 Decision 6A
- 觀測:從本檔 Out of Scope 與後站 Files 看 | 四項皆 Out 算過 | `docs/dev/five-station-f2/7-review.md` L445-L452；Decision Non-Goal 1
- Operational Context:不適用 — park 鎖。

## MODIFIED Requirements

本 repo `docs/specs/` 無 living spec 條文可引。F1／F2 已核契約本刀**不改其已刊 SHALL 原文**；只把 F2 明文交給 F3 的縫接上：

| 縫 | F2／F1 原文要點 | 本刀怎麼接 | 本檔 S |
|---|---|---|---|
| `f3_cut_happened` 恒 False | F2 never cuts；讀樹允許、不發明 cut | 改讀 `docs/dev/f3-cut-attestation.json` 三槽 | R-1 |
| `contract_version()` 讀錯鍵 | 讀 `version`／`contract_version` → 本 tree `""` | 只讀 `devflow_contract_version` | S-2.1 |
| 三前置 AND | 宣告 2.1.0 ∧ ¬in-flight ∧ cut；缺一 legacy | 繼承；2.1.0 ≠ cut | S-2.4、S-2.5 |
| doctor 綠 | SLOT-DOCTOR-GREEN-MEANS；F2 不改握手 | 只加 supported；握手不動 | R-4 |
| 本 slug 舊 7 | 五站 hop 跳不過 | 對本目錄建五站機＝X4 | S-7.3 |
| F2 S-8.1 不做 F3 cut | F2 刀鎖 | 本刀**做** cut；不改 F2 已刊原文 | 本檔 ADDED 全列 |

故本節無「改寫已刊 living 條文」列。

## REMOVED Requirements

無。不刪 F1／F2 牙、不刪 token、不刪 `N7-g1`／`N6-g2`、不刪舊 7 graph。

## 行為流程圖(R 級)

```
[R-1] 把 cut SoT 收成可見紀錄
  三槽 who when which_condition
  函式只讀獨立檔
  silent True 該格紅
[R-2] 只讀正本鍵且 2.1.0 不是 cut
  錯鍵不冒充 declared
  缺一前置就 legacy
[R-3] 同時切 graph 行為與 dual-read
  新 slug 不再例行停
  節點與 token 不刪
[R-4] 把 2.1.0 寫進 supported
  漏加誠實 INCOMPATIBLE
  綠不是 ticket
[R-5] 用同一電池跑三路
  注入壞行為該格紅
  F2 綠只是地板
[R-6] 摺停點不摺完整度
  謂詞真仍等人該格紅
  機械綠不能 Ship Done
[R-7] 拒絕本目錄當白老鼠
  in-flight 整段舊 7
  NEW5 只用合成根
[R-8] 鎖 Non-Goals 與 Files 清單
  本 hop 只交 draft 雙檔
  刪 token 折舊 重開 F2＝0
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.6，含 standing 加列 S-4.5／S-5.9／S-5.10／S-5.11）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、本目錄 freeze md、Disposition／CASE／SC 表。F3 行為 S 的綠發生在後站落地之後，不在本 PR。S 數見確認紀錄；>40 誠實記帳，不另切開新 slug。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-f3/4-spec.md` 後審頁可解析 R/S。本 hop 禁改 `scripts/` 牙。F2 電池現況可跑當地板，≠ F3 完。
- 非功能：本 slug 自己仍走舊 7。本 hop 不 bump、不改 graph。本 hop 不送 G2（不發明 PASS）。
- 無 golden master（可見路線行為在後站才變；本 hop 不改 runtime）。

### Stage 3 對帳

**N/A（Human ACCEPTED 的是 0／9 Demo N/A，不是可點場）。** `3-prototype.md` 在主線 `#374`：`status: approved`；Winner A 九條全未勾；Demo verdict＝N/A＋各條原因。Human verdict＝`ACCEPTED`（`human:rick @ 2026-09-14`；scenario＝0/9 Demo N/A accepted）。無 ACCEPTED 互動場景可對 R／S——人裁的是觸發表，不是 Demo 腳本。

| Stage 3 場／走查 | 下落 |
|---|---|
| 九條觸發判定 0／9（正式路徑） | Demo N/A。無互動 R／S 要從 Demo 長出。cut／讀鍵／graph／doctor／電池由本檔 ADDED 承接 Decision，不是 Demo |
| 「非 Demo（反事實紀錄）：N/A 路徑」 | **不是** Demo。產檔器刻意不用 `### Scenario`。Out of Scope：不把反事實當 ACCEPTED 場 |
| 「非 Demo（反事實紀錄）：若人工核准 UI 命中才走」 | **不執行**。本站判定不夠構成 trigger。可見紀錄由 R-1 承接，不是核准 UI |
| Method 反事實表九列 | 全不執行。不重做 `five-station-simplify` D1 |
| Human verdict 列（主線已 `ACCEPTED` + attestation） | 已落 `#374`。本 hop **不改** `3-prototype.md`。G2 Demo 條件走「無 trigger → N/A＋原因」支路（`_stage3_impl.py` 0／9 PASS） |
| AC-8／G-self-1 註（本 hop 落 Stage 3 檔 ≠ 白老鼠） | S-7.3；不是 Demo 欄 |
| Recovery:（3-prototype 無獨立 OC 表；觸發表 Recovery 語意＝0 命中無 Demo 可做） | 本節 N/A；相關恢復在 S-1.2（缺槽＝未切）、S-7.1（freeze） |

Decision 內部技術選擇「不預先跳過 Stage 3；觸發判定留給該站」——該站已行使判定＝0 命中，**不是**「命中仍跳過」的 skip OC。`2-decision.md` L305 含「Stage 3」與「跳過」字樣會被 `_stage3_impl.py` 掃進 `owner_call` 欄——**那不是 skip-OC 命中**；reason 仍是 0／9 N/A。

## Out of Scope

鎖死，後站不准改成 In：

1. **把 in-flight 折成五站**（含本目錄、含 `five-station-f2`、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
2. **刪 G1／G2／`ACCEPTED` token 或檔**；刪 `N7-g1`／`N6-g2` 節點檔。
3. **拿本 slug 當活五站白老鼠**；發明第一隻活五站名字。
4. **silent `True` 當 cut**；把 `f3_cut_happened==True` 當 F3 完。
5. **2.1.0 當 cut**；重開 F2 4A 三前置形狀。
6. **doctor 綠／marketplace update／plugin cache 當 cut 或路條**；出貨態故意 doctor 紅當目標；改 `_doctor_impl.py` 握手語意。
7. **只改 guide／STATUS 用字當 F3 完**；本 PR／本 feature branch 改 STATUS 正本表列。
8. **只改 graph、不宣告 2.1.0**；**只宣告 dual-read、新 slug 仍停 `N7-g1`**；**只翻 coordinator 留例行停點**。
9. 一次大爆炸改模板全文；放寬 hop≤2／Decide≤1／Goal reopen≤1；重開 F0 十條。
10. 把「檔在」或「F2 綠」當 F3 完成；把 F2 綠寫成 SC-BATTERY 第四條 IFF；兩支腳本各綠當同一電池；僅 html twin 當 in-flight GWT。
11. **重開 F2 park D-1／D-2／D-3／F-c-4**；改 F2 已封 R／S。
12. 把 cut 鎖成 `devflow-contract.json` 兄弟布林；用 git blame 冒充 who／when。
13. fallback／dual-read 錯鍵當 `contract_version()` 正讀。
14. 本 PR 實作 cut／改 `graph.yaml`／bump 契約／改 doctor／改 coordinator、填 G2 PASS、改 `3-prototype.md`。
15. Stage 3 反事實紙卡當可操作 Demo；重做 `five-station-simplify` D1。

## Diff Budget

整節是估計，不是承諾。[Assumption]。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| 本 hop 規格 md | 1 | ≤1,600 | `docs/dev/five-station-f3/4-spec.md` |
| 本 hop 審頁 html | 1 | 產器產出 | `4-spec.html`；`build-stage4-html.py --action`；不手包 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約／2-decision／3-prototype | 0 | 0 | 本 hop＝0；出現＝S-8.1 紅 |

**G2 之後、本 slug Stage 5–7（只 F3 准許清單）**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| `guides/guide-dev-flow.html` 用語 | 1 | ≤80 | 七站單行 → 五站用語；≠ SoT |
| `devflow-contract.json` | 1 | ≤8 | 只 bump `devflow_contract_version`→`2.1.0` |
| `hooks/runtime-capabilities.json` | 1 | ≤8 | 只加 `2.1.0` |
| `stage2`／`stage4` `graph.yaml` 條件邊 | 2 | ≤80 | 節點檔 0 刪 |
| coordinator 讀鍵＋cut 讀端＋路線閘 | ≤2 | ≤200 | `five_station_f2.py` 與／或 `five_station_f3.py` |
| `docs/dev/f3-cut-attestation.json` | 1 | ≤20 | 三槽；cut 當下才寫 |
| `scripts/test-five-station-f3.sh` | 1 | ≤250 | 單一電池入口 |
| `scripts/check-five-station-f3.sh` | ≤1 | ≤120 | 可選獨立 check；有也不構成第四條電池路 |
| 本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html | ≤6 | 過程檔 | 准許清單必含；≠ NEW5 fixture |
| `scripts/fixtures/five-station-f3/` | ≤12 | ≤400 | NEW5＋OLD7 合成 |
| 電池／CASE 測試（與非測試分開） | ≤8 | ≤1,000（測試） | 突變另加係數 |
| 刪 G1／G2／`ACCEPTED` token | 0 | 0 | ＝0，否則 S-8.3／S-8.4 紅 |
| 折 in-flight／改已 freeze slug 路線 | 0 | 0 | ＝0，否則 S-7.2 紅 |
| 重開 F2 park D-1…F-c-4 或 F2 R／S | 0 | 0 | ＝0，否則 S-8.6 紅 |
| `_doctor_impl.py` 握手語意 | 0 | 0 | ＝0，否則 S-4.4 紅 |
| `_templates/` 全文／doctor 握手／本 feature branch STATUS／本目錄當 NEW5 | 0 | 0 | ＝0，否則 S-8.2 紅；看板另 companion |

Stage 5 Files 准許清單正本＝S-8.2。超出 → L2。

## Dependencies

| 依賴 | justification |
|---|---|
| F0 brief＋狀態機 | freeze／新 slug／舊機械／採用端四條；本檔不重開 |
| F1 annex | SLOT-REJECT／DOCTOR-GREEN／IN-FLIGHT-DETECT 回歸 |
| F2 coordinator＋4A | 三前置形狀與完成樹；`f3_cut_happened` 現況恒 False |
| `scripts/check-spec-gate.sh` | 本 hop 形狀閘 |
| `scripts/build-stage4-html.py` | 本 hop 審頁 |
| `scripts/check-gate-tokens.sh` | TOKEN-KEEP |
| `scripts/test-five-station-f2.sh` | 地板；**不是** F3 完成入口 |
| 現行 doctor／契約 2.0.0 | DOCTOR-NE-TICKET 現況可測；本 hop 不改 |
| `_stage3_impl.py` | G2 Demo N/A 機械支路；本 hop 不改 |

無新外部服務。cut 紀錄是本 repo 檔案，不是新 SaaS。

## Design Boundary Contract

- Applicability: applicable
- Trigger(s): ②公開契約（`devflow_contract_version` 2.1.0＋cut 紀錄檔）／③跨模組 Interface（coordinator 路線閘 × graph 條件邊）／⑧filesystem（獨立 cut 紀錄檔）／⑨Feature Risk = high／⑩契約＋graph＋doctor 清單＋coordinator 四模組
- Design source: F2 `scripts/five_station_f2.py` 三前置；F1 annex SLOT；Decision 1A＋2A＋3C＋4A；new local design＝cut 紀錄路徑（DD-1）與條件邊（DD-5）

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| cut 紀錄檔 | 三槽 SoT | 寫入該檔的人類 | 被 `f3_cut_happened()` 讀 | `devflow-contract.json` 兄弟鍵；STATUS；git blame |
| 讀鍵 | `declared` | `devflow-contract.json` 的 `devflow_contract_version` | 只讀正本鍵 | `version`／`contract_version` fallback |
| 路線閘 | 三前置 → 五站或 `allow_legacy()` | 專案樹契約＋cut 檔＋該 slug 1–7 `.md` | graph 條件邊（同一謂詞） | doctor 綠；marketplace；cache |
| graph 條件邊 | 進或不進 `N7-g1`／`N6-g2` | 各站 `graph.yaml` | 路線閘同一謂詞 | 刪節點檔；未宣告就跳過 |
| doctor supported | 握手清單 | plugin `supported_contract_versions` | 契約版本字串 | 把綠當路條 |
| F3 電池 | NEW5＋OLD7＋TOKEN 同一 process | 合成 fixture | F2 電池當地板 | 本目錄當 NEW5；只轉呼叫 F2 當完成 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| `f3_cut_happened(root)` | 讀三槽 → bool | 缺檔／空槽 → False | 只讀；不寫紀錄檔 | F2 恒 False 的語意被本刀取代 |
| `contract_version(root)` | 讀正本鍵 → 字串 | 缺檔／缺鍵 → `""` | 只讀正本鍵 | 廢止錯鍵 fallback |
| `allow_legacy(root, slug)` | 三前置 → (legacy, why) | 缺一 → legacy | 只讀；不寫採用端契約 | 拒因字面含「F3 cut 未發生」 |
| graph 條件邊 | 同一三前置 → next node | 未宣告／in-flight／未切 → 仍進 N7-g1／N6-g2 | 與路線閘同成功或同失敗（S-3.5） | 節點檔保留 |
| 電池入口 | 無引數 | 缺一組 → 非 0 | 單一 process 三組都跑完才 0 | F2 腳本不是入口 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| cut record | 三槽持久化 | 人類寫者、`f3_cut_happened` | 檔 → bool | 缺槽＝False | 換 fixture 根可注入缺檔 |
| version reader | 只讀正本鍵 | `devflow-contract.json` | 鍵 → 字串 | 錯鍵忽略 | 假契約檔 |
| route gate | 三 AND | reader、cut record、`has_old7` | 真→五站；假→legacy | 理由字面分缺哪一條 | 三組缺一 fixture |
| graph edges | 跳過或進入例行停 | route gate | 謂詞→next | 未宣告不得跳過 | 條件邊 fixture |
| battery | 22 列 CASE | NEW5／OLD7／TOKEN fixture | 紅格餵壞行為 | 極性反了 → 非 0 | 各 CASE 獨立 exit |

### Design Constraints

- 必須:三槽可見紀錄；只讀正本鍵；graph＋dual-read 都要；supported 加 2.1.0；同一電池三路；注入→該格紅。
- 禁止:silent True；契約兄弟布林；blame 當 who／when；doctor 綠當路條；本目錄當 NEW5；本 hop 填 G2 PASS；重開 F2 park。
- Extension point:4-spec 可加 CASE 列；不得把 hollow 加成通過條件。
- Known design limit:本 hop 不落地 cut／reader／graph／doctor 清單；行為 S 的執行綠在後站。審頁產器 `steps[:8]`，本檔正好 8 個 R，不增 R-9。F3 完成樹之前 doctor 綠陷阱與例行停點仍在現場（約束，不是本 hop 改 runtime）。

## Verification Profile

- lane: full（判準:公開契約變更、跨模組 Interface、新增 filesystem 能力＝cut 紀錄檔、Feature Risk=high、採用端改線風險。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:採用端被遠端改線、cut 空切導致路線不可逆誤切、公開方法論契約／graph 預設。模板「公開 API／不可逆／資料隔離變種」吃這條）
- Failure model: 見下表
- Negative constraints: 見 Out of Scope 全列（後站不准改成 In）；另：`contract_version()` 不得 fallback 錯鍵；紅格不得把拒 hop 當綠；本 hop 不得改 STATUS／牙／契約／3-prototype；不得把 F2 綠寫進 SC-BATTERY IFF
- Required layers: spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`）；token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F3 電池列 Required——Required 層不得 unverified
- Conditional layers: F3 reader／graph 條件邊／cut 紀錄／電池落地 → 該刀列入 Required，單一入口 `bash scripts/test-five-station-f3.sh`（NEW5＋OLD7＋TOKEN；缺一路即非 0）；F2 電池在落地後當回歸地板重跑。契約／supported 被後站改動 → doctor 握手重跑。本 hop 不改那些檔、電池未落地 → 本 hop 不觸發 Conditional
- Explicitly excluded layers: UI e2e（本刀無新前端）；負荷／效能（路線閘非熱路徑）；金流／auth fuzz（不涉）；本 hop 跑 F3 coordinator／改 graph（碼 Out of Scope）
- Final fresh entry point: `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`
- Reliability triage:
  - Concurrency: n-a — 本刀不新增兩 process 共寫倉；cut 紀錄由人類一次寫入、讀端只讀（S-1.4）。並行改 graph 與契約的風險落在 S-2.7 同刀約束，不是 runtime lock
  - Idempotency: applicable — 同一合格三槽重複讀必須仍 `True`；缺槽重複讀必須仍 `False`（S-1.1／S-1.2）；`allow_legacy` 對同一三前置重複評必須同一答案（S-2.5）
  - Timeout/retry: applicable — 檔未寫＝未切，無逾時自動變真（S-1.1 Recovery）；Ship 無逾時自動 Done（S-6.3）；未宣告採用端持續舊 7，無逾時改線（S-2.6）

### Failure Model

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| silent True 當 cut | 空切；人指不到三槽 | ATTEST-SILENT-RED 不紅 | Required:S-1.3、S-5.4 | — |
| 2.1.0 當 cut | 第三位元無法獨立為假 | PRE-210-NE-CUT 理由變成「已宣告所以切了」 | Required:S-2.4 | — |
| 只 bump 正本、不修 reader | 假宣告；live 仍 legacy | READ-SEAM 不紅 | Required:S-2.2 | — |
| hops 先切、契約仍 2.0.0 | 遠端改線或 SLOT-REJECT 被關 | PRE-HOPS-200 不紅 | Required:S-2.6、S-3.2 | — |
| 只改 guide 用字 | 用語切、行為沒切 | GRAPH-WORD-NE 不紅 | Required:S-3.3 | — |
| 刪 N7-g1／N6-g2 或刪 token | 舊 7／dual-read 失去錨 | TOKEN-DEL-RED 不紅；節點檔消失 | Required:S-3.4、S-8.4 | — |
| 改 doctor 握手或放寬綠 | 綠變 ticket | DOCTOR-HONEST 變 COMPATIBLE | Required:S-4.2、S-4.4 | — |
| 只跑 F2 或「檔在」當 F3 完 | hollow | HOLLOW-F2／HOLLOW-FILES 不紅 | Required:S-5.5、S-5.6 | — |
| 只用字／兩支腳本各綠／僅 html 當 GWT | hollow | HOLLOW-WORD／HOLLOW-TWO-SCRIPT 不紅；html 被當 in-flight | Required:S-5.9、S-5.10、S-5.11 | — |
| 對本目錄建五站機 | 觀測白老鼠 | SELF-OLD7 跳得過 | Required:S-7.3 | — |
| 本 hop 自填 G2 PASS | 四眼破 | 頂欄 PASS | Required:S-8.1 | — |
| 路線閘與 graph 不同意 | 新 slug 仍等人或未宣告被改線 | S-3.5 兩邊答案不同 | Conditional:落地後電池 | 本 hop 不寫碼 |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q15 silent flip 不合法 | stage-2 | oc-accepted |
| Q16 hops 不得早於 2.1.0 宣告 | stage-2 | oc-accepted |
| Q17 只 bump 正本 declared 仍假 | stage-2 | oc-accepted |
| Q18 漏 supported 誠實紅 | stage-2 | oc-accepted |
| Q19 同一電池三路 | stage-2 | oc-accepted |
| cut 紀錄路徑交 4-spec（本檔 DD-1） | 2026-12-31 | open |
| 電池入口檔名交 4-spec（本檔 DD-2） | 2026-12-31 | open |
| NEW5／OLD7 fixture 根交 4-spec（本檔 DD-3／DD-4） | 2026-12-31 | open |
| graph 切換機制交 4-spec（本檔 DD-5） | 2026-12-31 | open |

Q15–Q19 已由 Decision OC-11／4／3／7／12 升格，故 oc-accepted。後四列是本檔釘形，期限給後站落地，不是已過站。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–6A。推翻 Decision 不是合法 DD。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | cut 紀錄路徑＝`docs/dev/f3-cut-attestation.json`；三鍵 `who`／`when`／`which_condition` 皆非空字串才算合格。`which_condition` **只命名 cut 位元**（例：`f3-cut`）；禁止把三前置 AND 捆進本槽；禁止把 `F3-cut-happened` 當唯一合法戳記。不是 `devflow-contract.json` 兄弟布林 | Decision 把路徑交給 4-spec；必須可測且擋 A 線同檔布林；standing 修 S-1.1 例不得把 declare 塞進 cut 槽 | `2-decision.md` 約束 3；OC-1。路徑本身 `[Assumption]` | 改回 silent True 或同檔布林＝翻 1A；把 AND 捆進本槽＝翻 4A 位元獨立 | 待人審 |
| DD-2 | 單一電池入口檔名＝`scripts/test-five-station-f3.sh`；可選另加 `scripts/check-five-station-f3.sh`（獨立 check，不是第四條電池路） | Decision 只鎖同一 process、缺一路即非 0；檔名交給 4-spec | `2-decision.md` 5A；內部技術選擇「入口檔名交 4-spec」。檔名 `[Assumption]` | 改兩支腳本各綠＝HOLLOW-TWO-SCRIPT；只包 F2 腳本＝HOLLOW-F2 | 待人審 |
| DD-3 | NEW5 fixture 根＝`scripts/fixtures/five-station-f3/new5/`（合成；不是本目錄） | Decision 約束 12 | `2-decision.md` 約束 12。路徑 `[Assumption]` | 拿本目錄當白老鼠＝X4 | 待人審 |
| DD-4 | OLD7 fixture 根＝`scripts/fixtures/five-station-f3/old7/`（已有 1–7 `.md`） | 與 NEW5 分家，供同一入口第二路 | `2-decision.md` 5A。路徑 `[Assumption]` | 與 NEW5 混目錄會折線 | 待人審 |
| DD-5 | graph 切換機制＝`stage2`／`stage4` `graph.yaml` 條件邊＋ coordinator 路線閘讀同一三前置；節點不刪 | Decision OC-5 機制 OPEN；本檔釘 observable 對得上的最小形 | `2-decision.md` OC-5。機制形 `[Assumption]` | 只翻函式留 N7-g1＝3D 空切；刪節點＝6B | 待人審 |
| DD-6 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 G2 PASS | 採用端改線＋公開契約＋空切不可逆；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief「Do NOT invent G2 PASS」 | 改 normal 則 Failure Model 變選配；代填 PASS＝假綠 | 待人審 |
| DD-7 | S 數 >40 留在本檔、不另切開新 slug；行為圖 8 框對 8 個 R（產器 `steps[:8]`） | 誠實記帳；不改 scripts | `scripts/build-stage4-html.py` L450；本 hop 不改牙 | 增 R-9 則圖丟框 | 待人審 |
| DD-8 | Stage 3 對帳＝0 命中 N/A；Human ACCEPTED 已落主線（#374）；不是「命中仍跳過」；本 hop 不改 `3-prototype.md` | Decision 無 skip OC；Winner A 0／9 | `3-prototype.md` 頂欄 approved；Human `ACCEPTED` + `human:rick @ 2026-09-14`；`34eec6b` | 寫 skip OC 或把 N/A 改成可點 Demo＝假 hit | 待人審 |
| DD-9 | 本 hop 原文跟 Winner B Decision；釘獨立檔三槽，不收 Stage2-A 同檔兄弟布林 | owner 鎖 1A 路徑 OPEN 且禁兄弟布林 | `2-decision.md` L19、L115 | 把 cut 放回契約 JSON＝翻約束 3 | 待人審 |
| DD-10 | Stage 5–7 Files 准許清單＝S-8.2（**同一條**含本 slug `5-tasks.md`／`6-implementation-notes.md`／`7-review.md`＋html，且禁區 Diff Budget＝0：`_templates/`／doctor 握手／STATUS／本目錄當 NEW5／刪 token／重開 F2 park） | 使用者本 hop 必蓋；Decision 6A；standing 吸 B Files 形 | 本 hop brief；`2-decision.md` Non-Goals | 清單外改檔＝L2；0 預算被破＝翻鎖；漏過程檔＝後站無法記帳 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `STATUS.md`（另 companion）、不 bump plugin、不開 5-tasks、不發明 G2 PASS。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。
- F2 電池可留作回歸地板（F3-F2-REGRESS）；不得替代 F3 三路電池。
- `when` 槽字面用 ISO-8601；本檔 S-1.1 舉例 `2026-09-14T00:00:00+08:00`，不是唯一合法值。
- `which_condition` 舉例 `f3-cut`（只命名 cut 位元）。禁止把 declare／in-flight 捆進同一槽。禁止把 `F3-cut-happened` 當唯一合法戳記。
- coordinator 後繼檔名可為 `scripts/five_station_f3.py`；亦可改 `five_station_f2.py` 讀端。兩路擇一，Files 清單都准。graph 切換仍是條件邊＋路線閘，不是只 hop-skip。

## Test Skeletons(選配)

- `test_s_1_1_attest_visible_three_slots`
- `test_s_1_2_missing_file_or_empty_slot_false`
- `test_s_1_3_silent_true_cell_red`
- `test_s_1_4_reader_does_not_write`
- `test_s_1_5_not_contract_sibling_bool`
- `test_s_1_6_wording_blame_board_not_sot`
- `test_s_2_1_reads_only_canonical_key`
- `test_s_2_2_read_seam_inject_red`
- `test_s_2_3_canonical_210_declared_true`
- `test_s_2_4_pre_210_ne_cut`
- `test_s_2_5_pre_and_missing_one`
- `test_s_2_6_pre_hops_200_slot_reject`
- `test_s_2_7_hops_not_before_declared`
- `test_s_3_1_new5_cut_ok_no_routine_gate`
- `test_s_3_2_dual_read_undeclared_old7`
- `test_s_3_3_graph_word_ne_red`
- `test_s_3_4_nodes_and_tokens_kept`
- `test_s_3_5_gate_and_graph_agree`
- `test_s_3_6_mechanism_is_edges_plus_gate`
- `test_s_4_1_add_210_to_supported`
- `test_s_4_2_doctor_honest_incompatible`
- `test_s_4_3_doctor_ne_ticket`
- `test_s_4_4_no_handshake_edit`
- `test_s_4_5_marketplace_cache_not_fourth`
- `test_s_5_1_single_entry_three_groups`
- `test_s_5_2_cannot_drop_case_rows`
- `test_s_5_3_polarity_inject_that_cell`
- `test_s_5_4_hollow_true_red`
- `test_s_5_5_hollow_files_red`
- `test_s_5_6_hollow_f2_red`
- `test_s_5_7_f2_regress_floor`
- `test_s_5_8_token_keep`
- `test_s_5_9_hollow_word_red`
- `test_s_5_10_two_scripts_not_same_battery`
- `test_s_5_11_html_only_not_inflight_gwt`
- `test_s_6_1_new5_wait_red`
- `test_s_6_2_keep_mk_red`
- `test_s_6_3_keep_ship_mech`
- `test_s_7_1_old7_freeze`
- `test_s_7_2_old7_fold_red`
- `test_s_7_3_self_old7`
- `test_s_7_4_new5_synthetic_root`
- `test_s_7_5_no_invented_live_slug`
- `test_s_8_1_this_hop_two_files_draft`
- `test_s_8_2_files_allowlist`
- `test_s_8_3_diff_budget_zero_locks`
- `test_s_8_4_token_del_red`
- `test_s_8_5_q_carry`
- `test_s_8_6_no_reopen_f2_park`

## 確認紀錄

- 前站核對 | 2026-09-14 | G1 PASS（`2-decision.md` verdict PASS／status approved／OC-1…OC-12 ✅）。Winner B soft-fix 1A+2A+3C+4A+5A+6A。Stage 3 Winner A 0／9 Demo N/A；Human ACCEPTED 已落 `#374`（`34eec6b`）。基準 `origin/main` `34eec6b`。不發明 G2 PASS。不改 STATUS。
- standing soft-fix | 2026-09-14 | Winner A 多數（R1+R2→A #378；R3→B #375）。吸收 B Files／hollow／可選 check／marketplace 非第四前置；吸收 C KEEP-MK 具名 M＋`which_condition` 只命名 cut 位元。修 S-1.1 例不再把 declare 捆進 cut 槽。不收 B 的 `F3-cut-happened` 戳記、不收「只 hop-skip」讀 3C、不收 C 的 Stage3 `NOT_REVIEWED`。不發明 G2 PASS。
- 雙源清點 | 2026-09-14 | 驗收雛形 AC-1…AC-11 共 11 條 → 各至少一 S。living `docs/specs/` 無條文；F1／F2 縫接表在 MODIFIED，無改寫已刊 SHALL。
- R 範圍 | 2026-09-14 | ADDED R-1…R-8（cut 紀錄／讀鍵／graph+dual-read／doctor／電池／keep／freeze／Files）。REMOVED 無。Writer A 釘路徑：獨立 JSON 三槽，不是契約兄弟布林。
- S 逐段 | 2026-09-14 | 49 條 S（S-1.1…S-8.6；standing 加 S-4.5／S-5.9／S-5.10／S-5.11）。每 S 有觀測欄。>40 留本檔（DD-7），不另切開新 slug。
- 3a 四節 | 2026-09-14 | Acceptance Criteria／Out of Scope／Diff Budget／Dependencies 齊。
- 3b Profile＋DBC | 2026-09-14 | lane full、Risk high、Failure Model 12 列、Reliability triage 三問、DBC applicable。
- 3c Stage 3 對帳 | 2026-09-14 | 整節 N/A。0／9；Human ACCEPTED（#374）裁的是觸發表；反事實非 Demo 不進 R／S；不改 `3-prototype.md`。不是 `NOT_REVIEWED`。
- DD 清點 | 2026-09-14 | DD-1…DD-10 上層待人審；無「待裁決」字樣。全文無 C4 未定事項三詞。
- 機械關卡 | 2026-09-14 | `scripts/check-spec-gate.sh` 須 9/9。審頁 `scripts/build-stage4-html.py --action`。
