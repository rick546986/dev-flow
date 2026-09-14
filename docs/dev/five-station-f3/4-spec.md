---
feature: five-station-f3
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站 F3 change spec（Writer B：cut 證明／讀鍵縫／graph+dual-read／doctor 誠實／成功≠空切）

> 基準:`origin/main` tip `191570c`（#373 Stage3-A + standing；G1 已核 #368）。Lane = **full**。Gold = G1 Decision B + soft-fix **1A+2A+3C+4A+5A+6A**。
> 本 hop **只** `4-spec.md` + `4-spec.html`。`status: draft`。`verdict` 空。**不發明 G2 PASS**。不改 STATUS／HISTORY／2-decision／3-prototype／模板／graph／doctor／契約／coordinator。不合併。
> Stage 3：**Owner ACCEPTED Stage3 N/A**（九條 0／9；Demo verdict＝N/A＋原因；不是 skip-OC）。本檔不改 `3-prototype.md`、不發明該檔 Human ACCEPTED。
> 原文獨立於他線 Stage 4（B 線當時未讀 A／C 規格稿）。不換 Decision winner。不重開 1A–6A。
> B 線主軸：① cut SoT＝人類可見獨立紀錄（誰／何時／哪個條件），函式只讀；② 讀鍵縫只讀正本鍵；③ graph **與** dual-read 都要、節點不刪；④ doctor 只加清單、綠≠ticket；⑤ 同一電池三路可獨立紅；⑥ Non-Goals 鎖 + Stage 5 Files 准許清單。
> Decision 原 20 列 CASE + standing PRE-AND／F3-F2-REGRESS **只准加不准減**。極性＝注入壞行為該格紅。F2 綠是地板，不是 SC-BATTERY 第四條 IFF。

## 補助模組生命週期（預覽）

主詞是「F3 cut：新 slug 預設五站的可見紀錄＋讀鍵＋graph 行為＋doctor 清單＋三路電池」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：cut 可見紀錄檔、F3 單一電池入口、NEW5／OLD7／TOKEN 三路 CASE
- 改行為（相關一格）：`f3_cut_happened()` 改讀紀錄；`contract_version()` 只讀正本鍵；cut 後新 slug 不再例行停 `N7-g1`／`N6-g2`；`supported` 加 2.1.0
- 退役：沒有
- 不動：G1／G2／`ACCEPTED` token、`N7-g1`／`N6-g2` 節點檔、doctor 握手語意、本 slug 舊 7、F2 park D-1／D-2／D-3／F-c-4、Stage 1–4 模板全文

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「F3 該把『之後才開、cut 當下尚無 1–7 `.md`』的 slug 預設改五站」 | 本方案處理 | R-6、S-6.6、S-3.1 |
| 「只把函式改 `True`、只改 guide 用字、或契約仍 `2.0.0` 就把 hops 當五站預設」 | 本方案處理 | S-1.3、S-3.5、S-2.5 |
| 「本目錄一有本檔就是 in-flight,拿自己當第一隻活五站 = 污染觀測」 | 本方案處理 | S-7.3、S-7.4 |
| Journey「新 slug 仍經 `N7-g1` 等人;chat 可蓋章」 | 本方案處理 | S-3.1、S-3.2 |
| Journey「doctor 綠只證明 `2.0.0 ∈ supported`≠切線」 | 本方案處理 | R-4、S-4.1、S-4.2 |
| Journey「coordinator 缺 cut → legacy；理由=`F3 cut 未發生`」 | 本方案處理 | S-6.2 |
| Workaround「恒 `False` 擋 live 五站；擋的是行為,不是人看得見的 cut 紀錄」 | 本方案處理 | R-1、S-1.2 |
| Workaround「STATUS／HISTORY 當刀口 log；看板列 ≠ cut」 | 本方案處理 | S-1.5 |
| Exception「不准改已經 freeze 的 slug」 | 本方案處理 | S-6.4、S-6.5 |
| Exception「NEW5 不是本目錄、也不是 `five-station-f2`／`five-station-simplify`」 | 本方案處理 | S-7.4、S-5.11 |
| Q15 silent flip 不合法 | 本方案處理 | S-1.3、S-5.3 |
| Q16 2.1.0 必須同動或先於 hops 預設 | 本方案處理 | S-2.4、S-2.5 |
| Q17 只 bump 正本鍵、`declared` 仍假 | 本方案處理 | S-2.1、S-2.3 |
| Q18 bump 後 supported 未加 → 誠實紅 | 本方案處理 | S-4.3 |
| Q19 同一電池三路、hollow 不算 | 本方案處理 | R-5、S-5.1、S-5.3、S-5.4、S-5.5 |
| Q20 第三位元怎麼被指認 | 本方案處理 | S-1.1、S-1.8 |
| Q21 graph 四選項 | 本方案處理 | R-3、S-3.6 |
| Q22 改 doctor 實作還是只加清單 | 本方案處理 | S-4.4 |
| Q23 guide 用語算哪些檔 | 本方案處理 | S-1.5 |
| Q24 STATUS 用語 vs feature branch 禁碰 | 本方案處理 | S-1.5、S-8.3 |
| Q25 第一隻活五站叫什麼 | 本方案處理 | S-7.4 |
| Q26 三前置形狀、2.1.0 ≠ cut | 本方案處理 | S-1.4、S-6.1、S-6.2 |
| Q27 live reader 回空字串 | 本方案處理 | S-2.1、S-2.6 |
| 「鎖:不刪 G1／G2／`ACCEPTED`；不把 in-flight 折成五站；不拿本 slug 當白老鼠」 | 本方案處理 | R-7、S-7.1、S-7.2、S-7.3 |
| Q1–Q14／Q3 刀定義 | 本方案處理 | R-6、S-8.5 |
| Q14 Backlog A 過期 | 刻意維持 | Out of Scope：本 PR 不改 STATUS |
| M1–M16／三失敗不得因「已經 cut 了」省略 | 本方案處理 | S-7.5、S-7.6 |

## SC → S 對照

Decision Success Criteria 每條至少一條獨立可測 S。4-spec **只准加不准減** CASE 列。

| SC | 一句 | 本檔 S |
|---|---|---|
| SC-BATTERY | 單一入口；NEW5+OLD7+TOKEN 都過才 exit 0 | S-5.1、S-5.2、S-5.10 |
| SC-F2-REGRESS | F2 電池仍綠；地板≠完 | S-5.7 |
| SC-NEW5-CUT-OK | cut 後新 slug 預設五站 | S-6.6、S-3.1 |
| SC-NEW5-WAIT-RED | 注入仍例行停 `N7-g1` → 該格紅 | S-3.2 |
| SC-OLD7-FREEZE | 已有 1–7 `.md` 仍舊 7 | S-6.4 |
| SC-OLD7-FOLD-RED | 注入對 in-flight 寫五站 → 該格紅 | S-6.5 |
| SC-TOKEN-KEEP | token 檔仍在 | S-7.1 |
| SC-TOKEN-DEL-RED | 注入刪 token 標成功 → 該格紅 | S-7.2 |
| SC-ATTEST-VISIBLE | 人指得到誰／何時／哪個條件 | S-1.1 |
| SC-ATTEST-SILENT-RED | 注入 silent True → 該格紅 | S-1.3 |
| SC-PRE-210-NE-CUT | 2.1.0 真、cut 假 → legacy；理由含「F3 cut 未發生」 | S-6.2 |
| SC-PRE-AND | 三前置缺一 → `allow_legacy()` | S-6.1 |
| SC-PRE-HOPS-200 | 2.0.0 + 五站 hops 預設 → SLOT-REJECT | S-2.5 |
| SC-READ-SEAM | 注入只 bump 正本、reader 仍舊 → 該格紅 | S-2.3 |
| SC-DOCTOR-HONEST | 2.1.0 ∉ supported → INCOMPATIBLE | S-4.3 |
| SC-DOCTOR-NE-TICKET | COMPATIBLE + 2.0.0 求五站 hop → 拒；理由是路線 | S-4.2 |
| SC-GRAPH-WORD-NE | 只用字、新 slug 仍停 `N7-g1`、標成功 → 該格紅 | S-3.5 |
| SC-SELF-OLD7 | 本目錄／F2／simplify 求五站跳不過 | S-7.3 |
| SC-HOLLOW | 函式真／檔在／只 F2 綠／只用字 標 F3 綠 → 紅 | S-5.3、S-5.4、S-5.5、S-5.6 |
| SC-KEEP | Must-keep 紅仍 hop、機械綠 Ship Done → 該格紅 | S-7.5、S-7.6 |
| SC-Q-CARRY | Q15–Q27 皆有去向 | S-7.9 |
| SC-PR | 本 PR 只 4-spec 雙檔；draft；verdict 空 | S-8.1 |

## CASE → S 對照（Decision 20 列 + standing 2 列只准加）

| CASE | 路 | 本檔 S |
|---|---|---|
| NEW5-CUT-OK | NEW5 | S-6.6 |
| NEW5-WAIT-RED | NEW5 | S-3.2 |
| OLD7-FREEZE | OLD7 | S-6.4 |
| OLD7-FOLD-RED | OLD7 | S-6.5 |
| TOKEN-KEEP | TOKEN | S-7.1 |
| TOKEN-DEL-RED | TOKEN | S-7.2 |
| ATTEST-VISIBLE | ATTEST | S-1.1 |
| ATTEST-SILENT-RED | ATTEST | S-1.3 |
| PRE-210-NE-CUT | PRE | S-6.2 |
| PRE-AND | PRE | S-6.1 |
| PRE-HOPS-200 | PRE | S-2.5 |
| READ-SEAM | PRE | S-2.3 |
| DOCTOR-HONEST | DOC | S-4.3 |
| DOCTOR-NE-TICKET | DOC | S-4.2 |
| GRAPH-WORD-NE | GRAPH | S-3.5 |
| SELF-OLD7 | SELF | S-7.3 |
| HOLLOW-TRUE | HOLLOW | S-5.3 |
| HOLLOW-FILES | HOLLOW | S-5.4 |
| HOLLOW-F2 | HOLLOW | S-5.5 |
| F3-F2-REGRESS | 地板 | S-5.7 |
| KEEP-MK-RED | KEEP | S-7.5 |
| KEEP-SHIP-MECH | KEEP | S-7.6 |

## ADDED Requirements

### R-1: 系統 SHALL 把 cut attestation 收成人類可見獨立紀錄，且 `f3_cut_happened()` 只讀該紀錄

1A。SoT＝三個語意槽：誰／何時／哪個條件。路徑＝`notes/design/five-station-f3-cut-attestation.md`（DD-1）。函式本體 `return True` 且紀錄缺＝空切。2.1.0／STATUS／guide／檔案地圖列／git blame **不是** SoT。**禁止**把 cut 鎖成 `devflow-contract.json` 裡跟 `devflow_contract_version` 同檔的兄弟布林。

**審的時候看什麼**
人能不能指出三槽。函式是不是只讀。silent True 該格是不是紅。2.1.0 與看板是不是被拒當 SoT。

#### S-1.1 ATTEST-VISIBLE：人指得到誰／何時／哪個條件
- GIVEN `notes/design/five-station-f3-cut-attestation.md` 存在，YAML frontmatter 三鍵皆非空：`who:` 人類 id（不是 git author）、`when:` `YYYY-MM-DD`、`condition:` 字面 `F3-cut-happened`
- WHEN 人打開該檔並讀 frontmatter
- THEN 三槽各有可指值；`f3_cut_happened(<project_root>)` 回 `True`
- 觀測:從該檔 frontmatter + 函式回傳看 | 三鍵可讀且函式真算過 | n-a:紀錄檔本 hop 未落。替代：本條字面 + DD-1；後站落地後讀該路徑
- Operational Context:
  - Actor:母版 owner
  - Goal:指出「已切」而不是口頭說切了
  - Situation:F2 函式恒假；看板已開仍未切
  - Known information:三槽語意已鎖
  - Missing information:本 hop 尚未寫該檔
  - Human decision:誰簽名寫進 `who:`
  - Authority:Agent 不得用 git blame 填 `who:`／`when:`
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:缺任一鍵 → 函式回假，當未切
  - Audit/handoff requirement:檔本身即紀錄
  - Observation:見本條觀測

#### S-1.2 `f3_cut_happened()` 只讀不寫判定
- GIVEN 紀錄檔缺席或任一鍵空
- WHEN 呼叫 `f3_cut_happened(<project_root>)`
- THEN 回 `False`；函式不得在呼叫當下建立或改寫該檔
- 觀測:從函式回傳與該檔是否被寫看 | 回假且檔未被本呼叫建立算過 | `scripts/five_station_f2.py:L276-L278` 現況恒假；落地後讀 DD-1 路徑
- Operational Context:不適用 — 讀端純內部。

#### S-1.3 ATTEST-SILENT-RED：注入 silent True
- GIVEN `f3_cut_happened` 被改成 `return True`，且 `notes/design/five-station-f3-cut-attestation.md` 缺席或三鍵任一空
- WHEN 有人宣稱 F3 已切
- THEN 該格獨立紅；不得標 F3 綠
- 觀測:從 F3 電池 ATTEST-SILENT-RED 格看 | 注入後該格紅算過 | n-a:電池未落地。替代：Decision CASE 表 ATTEST-SILENT-RED
- Operational Context:不適用 — 電池紅格。

#### S-1.4 2.1.0 已宣告 ≠ cut SoT
- GIVEN `devflow_contract_version` 已是 `2.1.0`，cut 紀錄缺席
- WHEN 評第三位元
- THEN cut 仍假；`2.1.0` 不得被讀成 SoT
- 觀測:從 cut 函式與契約鍵看 | 契約 2.1 且函式假算過 | 對照 S-6.2
- Operational Context:不適用 — 位元獨立。

#### S-1.5 STATUS／guide 用語 ≠ SoT
- GIVEN `guides/guide-dev-flow.html` 已把七站單行改寫五站，或整合分支 STATUS 用語已切，但 cut 紀錄缺席
- WHEN 有人把用字當成已切
- THEN 用語是交付物、不是 SoT；cut 仍假。本 feature branch 不改 `docs/dev/STATUS.md`；guide 至少含 `guides/guide-dev-flow.html` 原七站單行那句。F2 D-1 檔案地圖列仍 ≠ cut
- 觀測:從 cut 函式 + 本 PR `git diff --name-only` 看 | 無 STATUS 正本、cut 仍假算過 | `docs/dev/STATUS.md:L10-L13`；`guides/guide-dev-flow.html:L573`
- Operational Context:不適用 — 用語與看板政策。

#### S-1.6 禁止與版本同檔的兄弟布林
- GIVEN `devflow-contract.json` 被加上與 `devflow_contract_version` 同檔的 `f3_cut_happened` 布林，且獨立紀錄檔缺席
- WHEN 有人把該布林當真 SoT
- THEN 必須被拒；SoT 仍是 DD-1 路徑的三槽
- 觀測:從契約 JSON 鍵集 + cut 讀端看 | 讀端不讀同檔兄弟布林算過 | Decision 約束 3
- Operational Context:不適用 — 禁落點。

#### S-1.7 git blame 不是 who／when
- GIVEN 紀錄檔存在但 `who:`／`when:` 空，僅 git blame 有作者與日期
- WHEN 評 cut
- THEN 函式回 `False`；blame 不得冒充三槽
- 觀測:從 frontmatter 空鍵 + 函式回傳看 | 回假算過 | Decision 約束 3
- Operational Context:不適用 — 禁推導。

#### S-1.8 紀錄路徑形＝DD-1 具名檔
- GIVEN 後站實作 cut 讀端
- WHEN 列出 cut SoT 路徑
- THEN 正本路徑是 `notes/design/five-station-f3-cut-attestation.md`；三鍵名是 `who`／`when`／`condition`
- 觀測:從讀端打開的路徑看 | 等於本條具名路徑算過 | DD-1
- Operational Context:不適用 — 路徑形。

### R-2: 系統 SHALL 讓 `contract_version()` 只讀正本鍵，且 hops 預設五站不得早於 2.1.0 已宣告

2A。正本鍵＝`devflow_contract_version`。禁止 fallback／dual-read `version`／`contract_version`。錯鍵 bump ≠ 已宣告。**2.1.0 仍 ≠ cut**。

**審的時候看什麼**
讀哪一個鍵。錯鍵 bump 能不能冒充 declared。2.0.0 + 五站 hops 是不是 SLOT-REJECT。

#### S-2.1 只讀 `devflow_contract_version`
- GIVEN 本 tree `devflow-contract.json` 只有鍵 `devflow_contract_version`=`2.0.0`，沒有 `version`／`contract_version`
- WHEN 呼叫落地後的 `contract_version(<project_root>)`
- THEN 回傳字串以 `2.0` 開頭（現況 F2 回 `""`＝已核縫；落地必須改讀正本鍵）
- 觀測:從函式回傳看 | 落地後非空且以 `2.0` 或 `2.1` 開頭算過 | `scripts/five_station_f2.py:L260-L268`；`devflow-contract.json:L1-L2`
- Operational Context:不適用 — 讀鍵內部。

#### S-2.2 錯鍵 bump ≠ 已宣告
- GIVEN 只把 `version` 或 `contract_version` 寫成 `2.1.0`，正本鍵仍 `2.0.0`
- WHEN 評 `declared`
- THEN `declared` 假；錯鍵不得 fallback
- 觀測:從 `contract_version()` 與 `startswith("2.1")` 看 | 仍假算過 | Decision OC-3
- Operational Context:不適用 — 禁 fallback。

#### S-2.3 READ-SEAM：注入只 bump 正本、reader 仍舊
- GIVEN 正本鍵已改 `2.1.0`，但 `contract_version()` 仍只讀 `version`／`contract_version`（回 `""`）
- WHEN 有人宣稱「已宣告 2.1.0」
- THEN 該格獨立紅
- 觀測:從 F3 電池 READ-SEAM 格看 | 注入後該格紅算過 | n-a:電池未落地。替代：Decision CASE READ-SEAM
- Operational Context:不適用 — 電池紅格。

#### S-2.4 hops 預設五站不得早於 2.1.0 已宣告
- GIVEN 正本鍵仍 `2.0.0`（`declared` 假）
- WHEN 有人把 hops 預設改成五站（新 slug 不再例行停 `N7-g1`／`N6-g2`）
- THEN 違規；不得改線
- 觀測:從路線判定 + F1 SLOT-REJECT 看 | 未改線算過 | annex SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS
- Operational Context:
  - Actor:採用專案 owner
  - Goal:plugin 更新後路線不被遠端改
  - Situation:hops 已換、契約常未 bump
  - Known information:SLOT-REJECT；2.1.0 ≠ cut
  - Missing information:現場會不會先切 hops
  - Human decision:要不要 bump 正本鍵
  - Authority:marketplace 不能單獨改線
  - External dependency:採用端自己的契約檔
  - Out-of-system action:marketplace update
  - Waiting/timeout behavior:無
  - Recovery:缺宣告 → 仍舊 7
  - Audit/handoff requirement:拒絕理由含路線
  - Observation:見本條觀測

#### S-2.5 PRE-HOPS-200：2.0.0 + 五站 hops 預設
- GIVEN 契約仍 `2.0.0`、hops 已被人當五站預設
- WHEN 評路線
- THEN SLOT-REJECT；不得改線（綠格：合法拒）
- 觀測:從路線判定輸出看 | 違規且未改線算過 | Decision CASE PRE-HOPS-200
- Operational Context:不適用 — 與 S-2.4 同約束，本條是具名 CASE。

#### S-2.6 落地後正本鍵 2.1.0 → 回傳以 `2.1` 開頭
- GIVEN 正本鍵＝`2.1.0`，讀端已只讀該鍵
- WHEN 呼叫 `contract_version(<project_root>)`
- THEN 回傳以 `2.1` 開頭；`declared` 真。**仍 ≠ cut**
- 觀測:從函式回傳看 | 以 `2.1` 開頭且 cut 位元可獨立為假算過 | Decision 約束 5
- Operational Context:不適用 — 讀端落地後。

### R-3: 系統 SHALL 同時做 graph 行為與 2.1.0 dual-read，且不刪 `N7-g1`／`N6-g2`

3C。未宣告 2.1.0＝舊 7。cut 後、非 in-flight 的新 slug 預設路不再例行進 `N7-g1`／`N6-g2`。節點不刪。切換機制＝coordinator hop-skip + 保留節點（DD-3）。guide／STATUS 用語必要但不充分。

**審的時候看什麼**
新 slug 還等不等 G1。未宣告是不是仍舊 7。節點 yaml 還在不在。只用字能不能冒充成功。

#### S-3.1 cut 後新 slug 不再例行停 `N7-g1`／`N6-g2`
- GIVEN 三前置全真：正本鍵已宣告 2.1.0 ∧ 該 slug 在 cut 當下無 1–7 `.md` ∧ cut 紀錄三槽齊
- WHEN 求該新 slug 的預設 hop 路
- THEN 預設五站；中間不留下「請人審」G1／G2 例行停；hop 目標不是 `N7-g1`／`N6-g2`
- 觀測:從該 slug 路線判定／hop 紀錄看 | 無例行 G1／G2 停算過 | n-a:本 hop 不改 graph。替代：Decision NEW5-CUT-OK；試體見 S-5.11
- Operational Context:
  - Actor:新 slug 寫手（cut 之後才開）
  - Goal:預設五站、中間不等例行閘
  - Situation:現況 graph 預設進 `N7-g1`／`N6-g2`
  - Known information:3C observable 已鎖
  - Missing information:本 hop 機制未落地
  - Human decision:Ship 仍唯人
  - Authority:Agent 不得用 chat 蓋章當 G1
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:例行停摺掉；Ship 仍等
  - Recovery:三前置缺一 → 仍舊 7
  - Audit/handoff requirement:hop 紀錄
  - Observation:見本條觀測

#### S-3.2 NEW5-WAIT-RED：注入仍例行停
- GIVEN 三前置全真、latch 假
- WHEN 注入「仍例行進 `N7-g1`／留下要不要繼續／請人審」
- THEN 該格獨立紅
- 觀測:從 F3 電池 NEW5-WAIT-RED 格看 | 注入後該格紅算過 | n-a:電池未落地。替代：Decision CASE NEW5-WAIT-RED
- Operational Context:不適用 — 電池紅格。

#### S-3.3 未宣告 2.1.0＝舊 7
- GIVEN 正本鍵仍 `2.0.0`
- WHEN 求任一 slug（含合成 NEW5 形）的預設路
- THEN 舊 7；仍可進 `N7-g1`／`N6-g2`
- 觀測:從路線判定看 | `allow_legacy()` 真、理由含「路線未宣告」或「仍舊 7」算過 | F1 SLOT-UNDECLARED-ROUTE
- Operational Context:不適用 — dual-read 閘。

#### S-3.4 節點 `N7-g1`／`N6-g2` 不刪
- GIVEN F3 落地後的 `skills/dev-flow/stage2/graph.yaml` 與 `skills/dev-flow/stage4/graph.yaml`
- WHEN 搜節點 id `N7-g1` 與 `N6-g2`
- THEN 兩節點仍在檔內；in-flight 與未宣告仍可走這兩點
- 觀測:從兩份 `graph.yaml` 字面看 | 兩 id 仍在算過 | `skills/dev-flow/stage2/graph.yaml:L53-L57`；`skills/dev-flow/stage4/graph.yaml:L93-L98`
- Operational Context:不適用 — 節點保留。

#### S-3.5 GRAPH-WORD-NE：只用字標成功
- GIVEN `guides/guide-dev-flow.html` 已寫五站，Stage 2 graph 預設仍進 `N7-g1`，cut 後新 slug 仍例行等人
- WHEN 有人標 F3 成功
- THEN 該格獨立紅
- 觀測:從 F3 電池 GRAPH-WORD-NE 格看 | 注入後該格紅算過 | n-a:電池未落地。替代：Decision CASE GRAPH-WORD-NE
- Operational Context:不適用 — 電池紅格。

#### S-3.6 切換機制＝coordinator hop-skip + 保留節點
- GIVEN 三前置全真
- WHEN coordinator 選下一 hop
- THEN 跳過 `N7-g1`／`N6-g2`；yaml 仍保留這兩節點。未宣告或 in-flight → 仍進入這兩點。不另建第二份 graph 檔當正本
- 觀測:從 hop 目標 id + yaml 節點仍在看 | 真時跳過、假時進入、節點仍在算過 | DD-3
- Operational Context:不適用 — 機制形。

### R-4: 系統 SHALL 把 doctor 綠當握手約束，只加 `supported` 清單，不改握手語意

4A。`COMPATIBLE`／exit 0 只證明契約版本 ∈ `supported_contract_versions`。≠ cut、≠ 路條、≠ 第四條前置。漏加 2.1.0 → 誠實 INCOMPATIBLE。不改 `hooks/_doctor_impl.py` 握手語意。

**審的時候看什麼**
綠能不能當 hop 票。漏清單是不是紅。握手實作有沒有被改。

#### S-4.1 doctor 綠 ≠ cut、≠ 路條
- GIVEN 本 tree 契約 `2.0.0`、doctor 可印 `COMPATIBLE` 且 exit 0、cut 假
- WHEN 有人把這次綠當成 cut 或五站許可
- THEN 拒絕；綠只握手
- 觀測:從 doctor 輸出 + 路線判定看 | 綠且仍 legacy 算過 | `hooks/_doctor_impl.py:L492-L500`；annex SLOT-DOCTOR-GREEN-MEANS
- Operational Context:不適用 — 約束。

#### S-4.2 DOCTOR-NE-TICKET：COMPATIBLE + 2.0.0 求五站 hop
- GIVEN doctor 剛印 `COMPATIBLE`、契約仍 `2.0.0`
- WHEN 求五站 hop
- THEN 拒；拒絕理由含「路線未宣告」或「仍舊 7」或「F3 cut 未發生」；理由**不含**「doctor 已綠所以可 hop」
- 觀測:從該次 hop 拒絕理由看 | 含路線句、不含 doctor 已綠句算過 | `scripts/five_station_f2.py:L300-L307`
- Operational Context:
  - Actor:doctor 操作者／新 slug 寫手
  - Goal:看握手綠／紅，不要把綠當切線
  - Situation:升級後 doctor 常仍綠
  - Known information:綠＝版本 ∈ supported
  - Missing information:現場會不會把綠當票
  - Human decision:要不要 bump 契約
  - Authority:doctor 不能改線
  - External dependency:無
  - Out-of-system action:跑 `devflow-doctor.sh`
  - Waiting/timeout behavior:無
  - Recovery:理由指向路線
  - Audit/handoff requirement:拒絕理由字面
  - Observation:見本條觀測

#### S-4.3 DOCTOR-HONEST：2.1.0 ∉ supported → INCOMPATIBLE
- GIVEN 正本鍵已 `2.1.0`，`hooks/runtime-capabilities.json` 的 `supported_contract_versions` 仍只有 `2.0.0`
- WHEN 跑 doctor
- THEN 印 INCOMPATIBLE 且非 0（綠格：誠實紅）。不得為了升級好看放寬握手
- 觀測:從 doctor stdout／exit 看 | INCOMPATIBLE 且非 0 算過 | `hooks/_doctor_impl.py:L193-L202`；`hooks/runtime-capabilities.json:L1-L4`
- Operational Context:不適用 — 握手清單。

#### S-4.4 不改 `_doctor_impl.py` 握手語意
- GIVEN 後站 Files 聯集
- WHEN 看 `hooks/_doctor_impl.py` 對 `supported_contract_versions` 的比對
- THEN 語意仍是「契約版本必須 ∈ supported，否則 fail-closed」；本刀只准改 `supported_contract_versions` 清單（`hooks/runtime-capabilities.json`）
- 觀測:從後站 `git diff hooks/_doctor_impl.py` 看 | 握手語意 diff 空、或僅註解算過 | F2 Out #12；本檔 Files 准許清單
- Operational Context:不適用 — 檔集約束。

#### S-4.5 marketplace／cache 不是第四條前置
- GIVEN `marketplace_updated=True` 或 `cache_has_hops=True`，三前置仍缺
- WHEN 評 `allow_legacy()`
- THEN 仍 legacy；marketplace／cache 被丟棄
- 觀測:從 `allow_legacy` 回傳看 | 仍 legacy 算過 | `scripts/five_station_f2.py:L289-L290`
- Operational Context:不適用 — 既有約束繼承。

### R-5: 系統 SHALL 用同一電池證明三路，且 hollow 具名格可獨立紅

5A。單一入口。exit 0 **當且僅當** NEW5 組、OLD7 組、TOKEN 組都過。函式真／檔在／只 F2 綠／只用字 ≠ 完。F2 綠是地板（F3-F2-REGRESS），不是第四條 IFF。極性＝注入壞行為該格紅。

**審的時候看什麼**
是不是同一 process。缺一路是不是非 0。四種 hollow 能不能各自紅。F2 綠有沒有被寫進 IFF。

#### S-5.1 單一入口（SC-BATTERY）
- GIVEN 入口檔 `scripts/test-five-station-f3.sh`（DD-2）
- WHEN 不帶參數跑該入口
- THEN 同一 process 內跑完 NEW5、OLD7、TOKEN 三組；缺一組、跳過一組 → 非 0
- 觀測:從該入口 stdout／exit 看 | 三組都列名且缺一則非 0 算過 | n-a:入口未落。替代：Decision SC-BATTERY；DD-2
- Operational Context:不適用 — 電池入口。

#### S-5.2 exit 0 當且僅當三組都過
- GIVEN NEW5 組綠、OLD7 組綠、TOKEN 組綠、且無 hollow 紅格被標綠
- WHEN 入口結束
- THEN exit 0。任一組未過 → 非 0
- 觀測:從入口 exit 看 | IFF 三組算過 | Decision 約束 11
- Operational Context:不適用 — 同一電池。

#### S-5.3 HOLLOW-TRUE：只把函式真標 F3 綠
- GIVEN 僅 `f3_cut_happened==True`，三路未過
- WHEN 有人標 F3 綠
- THEN 該格獨立紅
- 觀測:從 F3 電池 HOLLOW-TRUE 格看 | 注入後該格紅算過 | Decision CASE HOLLOW-TRUE
- Operational Context:不適用 — 電池紅格。

#### S-5.4 HOLLOW-FILES：只把檔在標 F3 綠
- GIVEN 僅 coordinator／紀錄／入口檔存在，三路未過
- WHEN 有人標 F3 綠
- THEN 該格獨立紅
- 觀測:從 F3 電池 HOLLOW-FILES 格看 | 注入後該格紅算過 | Decision CASE HOLLOW-FILES
- Operational Context:不適用 — 電池紅格。

#### S-5.5 HOLLOW-F2：只跑 F2 電池綠就標 F3 綠
- GIVEN 僅 `scripts/test-five-station-f2.sh` exit 0、`failed=0`
- WHEN 有人標 F3 綠且未跑 S-5.1 入口
- THEN 該格獨立紅
- 觀測:從 F3 電池 HOLLOW-F2 格看 | 注入後該格紅算過 | Decision CASE HOLLOW-F2
- Operational Context:不適用 — 電池紅格。

#### S-5.6 只用字 ≠ F3 完
- GIVEN 僅 guide／STATUS 用語已切，三路未過
- WHEN 有人標 F3 綠
- THEN 必須被拒（SC-HOLLOW (d)）
- 觀測:從完成條件是否另要求 S-5.1 看 | 用字單獨不算完算過 | Decision SC-HOLLOW (d)
- Operational Context:不適用 — 完成定義。

#### S-5.7 F3-F2-REGRESS：F2 電池仍綠（地板）
- GIVEN F3 落地後
- WHEN 跑 `scripts/test-five-station-f2.sh`
- THEN exit 0 且 `failed=0`。本格綠 ≠ F3 完，也不得寫進 SC-BATTERY 的 IFF
- 觀測:從 F2 腳本 stdout／exit 看 | exit 0、`failed=0` 算過 | `scripts/test-five-station-f2.sh:L1-L11`
- Operational Context:不適用 — 回歸地板。

#### S-5.8 不得減 Decision CASE 原列
- GIVEN Decision 原 20 列 + standing PRE-AND + F3-F2-REGRESS
- WHEN 列本檔 CASE → S 表
- THEN 上列 22 名皆在；可加列，不可刪原列，不可把「函式真／檔在／F2 綠／用字」加成通過條件
- 觀測:從本檔 CASE 表看 | 22 名皆有 S 算過 | 本檔 CASE → S 對照
- Operational Context:不適用 — 表完整性。

#### S-5.9 極性：注入壞行為 → 該格紅
- GIVEN 任一標「→ 紅」的 CASE
- WHEN 測法改成「coordinator 拒 hop／拒寫，所以該格綠」
- THEN 極性反了，必須被拒
- 觀測:從該紅格測法看 | 注入壞行為才算該格測法算過 | Decision 約束 16
- Operational Context:不適用 — 測法極性。

#### S-5.10 兩支互不認識的腳本各綠一次 ≠ 同一電池
- GIVEN NEW5 腳本與 OLD7 腳本分開跑、各 exit 0，沒有單一入口
- WHEN 有人標 SC-BATTERY 綠
- THEN 必須被拒
- 觀測:從是否存在單一 process 入口看 | 兩支腳本各綠不算算過 | Decision 約束 11
- Operational Context:不適用 — 入口形。

#### S-5.11 NEW5 試體＝合成 fixture 或 cut 之後才開的 slug
- GIVEN 選 F3 NEW5 試體路徑
- WHEN 列路徑
- THEN 根＝`scripts/fixtures/five-station-f3/new5/`（合成；cut 當下無 1–7 `.md`），或 cut **之後**才開的新 slug。**不是** `docs/dev/five-station-f3/`、`docs/dev/five-station-f2/`、`docs/dev/five-station-simplify/`。不發明活五站名字
- 觀測:從電池／Files 路徑看 | 不含三個 live 目錄當 hop 試體算過 | DD-4；OC-9
- Operational Context:不適用 — 試體根。

### R-6: 系統 SHALL 繼承 F2 三前置 AND，缺一條就 `allow_legacy()`

宣告 2.1.0 ∧ ¬in-flight ∧ cut 已發生。2.1.0 ≠ cut。in-flight＝目錄已有 1–7 任一 `.md`（僅 html 不算）。

**審的時候看什麼**
缺哪一條。拒絕理由是不是「F3 cut 未發生」。in-flight 有沒有被折。

#### S-6.1 PRE-AND：三前置缺一 → `allow_legacy()`
- GIVEN 三前置任一為假
- WHEN 評 `allow_legacy(<project_root>, <slug_dir>)`
- THEN 回 `(True, "legacy")`；不建五站機
- 觀測:從函式回傳看 | legacy 真算過 | `scripts/five_station_f2.py:L286-L293`
- Operational Context:不適用 — 既有 AND。

#### S-6.2 PRE-210-NE-CUT：2.1.0 真、cut 假
- GIVEN `declared` 真、¬in-flight、cut 假
- WHEN 求五站 hop
- THEN `allow_legacy()`；拒絕理由含「F3 cut 未發生」；理由不含「已宣告所以切了」
- 觀測:從 `refuse_hop_reason` 看 | 含「F3 cut 未發生」算過 | `scripts/five_station_f2.py:L307`
- Operational Context:不適用 — 合法拒。

#### S-6.3 in-flight → legacy
- GIVEN 目錄已有 1–7 任一 `.md`（例如本目錄已有 `1-discussion.md`）
- WHEN 評路線
- THEN in-flight；`allow_legacy()`；理由含「仍舊 7 in-flight」
- 觀測:從 `has_old7` + 拒絕理由看 | in-flight 且 legacy 算過 | `scripts/five_station_f2.py:L271-L273`、`:L305-L306`
- Operational Context:不適用 — 偵測。

#### S-6.4 OLD7-FREEZE：已有 1–7 `.md` 整段舊 7
- GIVEN fixture 根 `scripts/fixtures/five-station-f3/old7/` 已有至少一個 1–7 `.md`
- WHEN 求切五站
- THEN 仍舊 7 到 Ship；無五站狀態寫入；三 cap 不套
- 觀測:從該 fixture 目錄與 hop 紀錄看 | 無五站狀態檔、仍有例行閘路徑算過 | Decision CASE OLD7-FREEZE
- Operational Context:不適用 — freeze 綠格。

#### S-6.5 OLD7-FOLD-RED：注入對 in-flight 寫五站
- GIVEN 同上 OLD7 fixture
- WHEN 注入對該目錄寫五站狀態或五站 hop
- THEN 該格獨立紅
- 觀測:從 F3 電池 OLD7-FOLD-RED 格看 | 注入後該格紅算過 | Decision CASE OLD7-FOLD-RED
- Operational Context:不適用 — 電池紅格。

#### S-6.6 NEW5-CUT-OK：cut 當下無 1–7 `.md` → 預設五站
- GIVEN 合成 fixture `scripts/fixtures/five-station-f3/new5/` 在 cut 當下無 1–7 `.md`，且三前置全真
- WHEN 求預設路線
- THEN 預設五站；不等例行 G1／G2 提交判定
- 觀測:從該 fixture 路線判定看 | 五站且無例行停算過 | Decision CASE NEW5-CUT-OK
- Operational Context:不適用 — 與 S-3.1 同 observable，本條是具名 CASE。

#### S-6.7 僅 html 不算 in-flight
- GIVEN 目錄只有 `*.html`、零個 1–7 `.md`
- WHEN 評 `has_old7`
- THEN 不是 in-flight
- 觀測:從 `has_old7` 回傳看 | 假算過 | F1 SLOT-IN-FLIGHT-DETECT
- Operational Context:不適用 — 偵測邊界。

### R-7: 系統 SHALL 鎖死 Non-Goals：不刪 token、不折 in-flight、不白老鼠、不重開 F2 park、Must-keep 仍咬

6A。後站不准把本節改成可選。

**審的時候看什麼**
token 還在不在。本目錄有沒有被當 NEW5。F2 park 有沒有被借刀。Must-keep 紅能不能 hop。

#### S-7.1 TOKEN-KEEP：G1／G2／`ACCEPTED` 仍在
- GIVEN F3 落地後
- WHEN 跑 `scripts/check-gate-tokens.sh`
- THEN exit 0；G1／G2／`ACCEPTED` token 與檔仍在
- 觀測:從該腳本 exit + token 字面看 | exit 0 且字面仍在算過 | `scripts/check-gate-tokens.sh:L44-L60`
- Operational Context:不適用 — token 牙。

#### S-7.2 TOKEN-DEL-RED：注入刪 token 卻標成功
- GIVEN 刪 G1 或 G2 或 `ACCEPTED` token／檔
- WHEN 有人標 F3 成功
- THEN 該格獨立紅
- 觀測:從 F3 電池 TOKEN-DEL-RED 格看 | 注入後該格紅算過 | Decision CASE TOKEN-DEL-RED
- Operational Context:不適用 — 電池紅格。

#### S-7.3 SELF-OLD7：本目錄／F2／simplify 跳不過
- GIVEN slug 目錄是 `docs/dev/five-station-f3/` 或 `docs/dev/five-station-f2/` 或 `docs/dev/five-station-simplify/`
- WHEN 求五站自動前進
- THEN 跳不過；仍是舊 7 站檔；無五站狀態寫入
- 觀測:從該目錄站檔 + 被拒絕的 hop 看 | 有 1–7 `.md`、無五站機寫入算過 | Decision CASE SELF-OLD7
- Operational Context:
  - Actor:本 slug 執行者
  - Goal:走完手上舊 7，不被中途折
  - Situation:本目錄已有 1-discussion／2-decision／3-prototype
  - Known information:SLOT-IN-FLIGHT-DETECT
  - Missing information:後站會不會對自己開五站機
  - Human decision:第一隻活五站另開、不在本檔發明名字
  - Authority:對本目錄建五站機＝X4
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:本 slug 仍等人簽閘
  - Recovery:拒絕 hop
  - Audit/handoff requirement:本目錄站檔
  - Observation:見本條觀測

#### S-7.4 不發明活五站名字、不白老鼠
- GIVEN Q25
- WHEN 讀本檔
- THEN 沒有第一隻活五站 slug 名；NEW5 試體只准 S-5.11 路徑
- 觀測:從本檔全文搜 slug 名看 | 無新發明 live 五站名算過 | OC-9
- Operational Context:不適用 — 命名禁令。

#### S-7.5 KEEP-MK-RED：注入 Must-keep 紅仍 hop
- GIVEN Must-keep 任一紅（例：T 缺 Verify）
- WHEN 注入仍 hop
- THEN 該格獨立紅；不得用「已經 cut 了」省略
- 觀測:從 F3 電池 KEEP-MK-RED 格看 | 注入後該格紅算過 | Decision CASE KEEP-MK-RED
- Operational Context:不適用 — 電池紅格。

#### S-7.6 KEEP-SHIP-MECH：注入機械綠無人 PASS 卻 Ship Done
- GIVEN 機械全綠、無人寫 7-review `verdict: PASS`
- WHEN 注入標 Ship Done
- THEN 該格獨立紅
- 觀測:從 F3 電池 KEEP-SHIP-MECH 格看 | 注入後該格紅算過 | Decision CASE KEEP-SHIP-MECH
- Operational Context:不適用 — 電池紅格。

#### S-7.7 不重開 F2 park D-1／D-2／D-3／F-c-4
- GIVEN F2 7-review 已 park D-1／D-2／D-3／F-c-4
- WHEN 本 slug Files 或 Decision 被要求重開這四項
- THEN 必須被拒；後站不准改成 In
- 觀測:從本檔 Out of Scope + Files 准許清單看 | 四項不在准許施工列算過 | `docs/dev/five-station-f2/7-review.md:L445-L452`
- Operational Context:不適用 — Non-Goal 抬高。

#### S-7.8 不炸 Stage 1–4 模板全文
- GIVEN Backlog B 仍凍 Stage 1–4 模板
- WHEN 列本刀 Files
- THEN `_templates/` 的 Stage 1–4 正文 Diff Budget＝0
- 觀測:從後站 `git diff --name-only _templates/` 看 | 無 Stage 1–4 正文改動算過 | `docs/dev/STATUS.md` Backlog B；brief §7
- Operational Context:不適用 — 模板凍。

#### S-7.9 Q15–Q27 皆有去向（SC-Q-CARRY）
- GIVEN 1-discussion Q15–Q27
- WHEN 人讀本檔 Real-world Disposition
- THEN 每題有去向 ∈ {本方案處理, 刻意維持, Non-Goal, 另開 slug, 仍待驗}；Q15／Q16／Q17／Q19／Q21 下落是 S、不得標可選
- 觀測:從本檔 Disposition 表列看 | Q15–Q27 皆有列算過 | 本檔 Disposition
- Operational Context:不適用 — 去向帳。

### R-8: 系統 SHALL 讓本 hop 只交 draft 規格雙檔，並給 Stage 5 具名 Files 准許清單；Stage 3＝N/A

本 Stage 4 hop 不落地 cut。後站 Files 超出准許清單＝本條紅。

**審的時候看什麼**
本 PR 是不是只有兩檔。verdict 是不是空。Files 清單有沒有具名。Stage 3 是不是 0／9 N/A。

#### S-8.1 本 Stage 4 hop 只 4-spec 雙檔、draft、無 G2 PASS
- GIVEN 本 PR 對 `origin/main`
- WHEN 跑 `git diff --name-only origin/main`
- THEN 只含 `docs/dev/five-station-f3/4-spec.md` 與 `docs/dev/five-station-f3/4-spec.html`；頂欄 `status: draft`；`verdict` 空；無 G2 PASS；無 STATUS／HISTORY／2-decision／3-prototype／模板／graph／scripts 新牙／契約 bump
- 觀測:從本 PR diff + 本檔 frontmatter 看 | 兩檔、draft、verdict 空算過 | 讀本檔頂欄與 `git diff --name-only`
- Operational Context:不適用 — 本 hop 檔集。

#### S-8.2 Stage 5 Files 准許清單
- GIVEN 本 slug G2 已過，進入 5-tasks；或後站實作 PR 對開工點
- WHEN 列 Files 聯集，並跑 `git diff --name-only`
- THEN 只准下列路徑：`scripts/test-five-station-f3.sh`；`scripts/check-five-station-f3.sh`（若需要獨立 check 入口）；`scripts/five_station_f2.py`（只准改 `contract_version()` 讀鍵與 `f3_cut_happened()` 讀端，不改 F2 完成樹）；`scripts/fixtures/five-station-f3/**`；`notes/design/five-station-f3-cut-attestation.md`；`devflow-contract.json`（只准 bump `devflow_contract_version` 到 2.1.0，**不准**加同檔兄弟 cut 布林）；`hooks/runtime-capabilities.json`（只准 `supported_contract_versions` 加 `2.1.0`）；`guides/guide-dev-flow.html`（用語交付物，至少改七站單行）；`skills/dev-flow/stage2/graph.yaml` 與 `skills/dev-flow/stage4/graph.yaml`（只准改預設 `next:`／條件邊，**不准刪** `N7-g1`／`N6-g2`）；本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html。下列區塊 Diff Budget **必須＝0**，否則本條紅：G1／G2／`ACCEPTED` token 檔被刪；`_templates/` Stage 1–4 正文；`hooks/_doctor_impl.py` 握手語意；`docs/dev/STATUS.md`／`HISTORY.md`（看板另 companion）；把本目錄當 NEW5 fixture；重開 F2 park D-1／D-2／D-3／F-c-4
- 觀測:從 5-tasks Files 聯集 + 後站 `git diff --name-only` 看 | 超出准許清單或禁區行數 ≠ 0 → 本條紅算過 | n-a:5-tasks 尚未寫。替代：本檔 Diff Budget 與 Out of Scope
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:只施工 F3 cut 准許檔
  - Situation:G2 剛過
  - Known information:准許清單具名；禁區＝0
  - Missing information:有沒有人想順便刪閘或改 STATUS
  - Human decision:STATUS 用語走整合分支 companion
  - Authority:本 R
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無
  - Recovery:把禁區檔從 Files 刪掉
  - Audit/handoff requirement:5-tasks Files
  - Observation:見本條觀測

#### S-8.3 本 PR／本 feature branch 不改 STATUS／HISTORY
- GIVEN 本 Stage 4 PR
- WHEN 看 diff
- THEN 無 `docs/dev/STATUS.md`、無 `docs/dev/HISTORY.md`、無 `docs/dev/HISTORY.html`
- 觀測:從 `git diff --name-only` 看 | 三檔不在算過 | Decision OC-10；Q24
- Operational Context:不適用 — 看板政策。

#### S-8.4 Stage 3 對帳＝0／9 N/A（Owner ACCEPTED Stage3 N/A）
- GIVEN `docs/dev/five-station-f3/3-prototype.md` 九條全未勾；Demo verdict＝N/A；Owner 本 hop 指令 ACCEPTED Stage3 N/A
- WHEN 對帳本檔 R／S
- THEN 無 ACCEPTED Demo 場景要掛 R／S；整節 N/A＋原因。不是「命中仍跳過」的 skip-OC。不發明 3-prototype Human ACCEPTED。不建 `3-prototype.html`
- 觀測:從 3-prototype 勾選列 + 本節 Stage 3 對帳看 | 0／9、Demo N/A、本檔無 ACCEPTED 場算過 | `docs/dev/five-station-f3/3-prototype.md:L19-L32`、`:L145-L159`
- Operational Context:不適用 — 對帳。

#### S-8.5 本檔不把「不預先跳過 Stage 3」當 skip-OC
- GIVEN `2-decision.md:L305` 含「Stage 3」與「跳過」字樣
- WHEN `_stage3_impl.py` 掃 `owner_call`
- THEN 理由仍是 0／9 N/A，不是 `SKIPPED_OWNER_CALL`；本檔不得把該句寫成流程層 skip
- 觀測:從 `_stage3_impl.py five-station-f3` 的 `reason` 看 | 含 0/9 N/A、不含 SKIPPED_OWNER_CALL 算過 | `3-prototype.md:L140-L158`
- Operational Context:不適用 — 機械閘語意。

## MODIFIED Requirements

本 repo `docs/specs/` 無 living spec 條文可引。F2 已核契約（`docs/dev/five-station-f2/4-spec.md`）本刀**不改其 SHALL 原文**；只把 F2 明文交給 F3 的縫接上：

| 縫 | F2 原文要點 | 本刀怎麼接 | 本檔 S |
|---|---|---|---|
| 三前置 AND | 2.1.0 ∧ ¬in-flight ∧ cut；2.1.0 ≠ cut | 繼承；第三位元改讀可見紀錄 | S-6.1、S-1.2 |
| `f3_cut_happened` 恒 False | F2 never cuts | 改讀 DD-1 檔；silent True 紅 | S-1.2、S-1.3 |
| reader 錯鍵 | 讀 `version`／`contract_version` → `""` | 只讀正本鍵 | S-2.1 |
| doctor 綠 | 約束不是票；不改握手 | 只加 supported 清單 | S-4.4 |
| 本 slug 舊 7 | 五站 hop 跳不過 | 對本目錄建五站機＝X4 | S-7.3 |
| F3 刀 | F2 Out：後站不准把 F3 改成 In | **本 slug 就是那一刀**；F2 檔不改 | R-6 |

故本節無「改寫已刊 living 條文」列。

## REMOVED Requirements

無。不刪 F2 完成樹、不刪 token、不刪 `N7-g1`／`N6-g2`、不刪 doctor 握手。

## 行為流程圖(R 級)

```
[R-1] 可見紀錄為 cut SoT 且函式只讀
  三槽 who when condition
  silent True 該格紅
[R-2] 只讀正本鍵且 hops 不得早於 2.1.0
  錯鍵 bump 不是已宣告
  2.0.0 加五站 hops 拒
[R-3] graph 行為加 dual-read 且節點不刪
  新 slug 不再例行停 N7-g1
  未宣告仍舊 7
[R-4] doctor 只加清單且綠不是票
  漏 2.1.0 誠實紅
  拒絕理由是路線
[R-5] 同一電池三路且 hollow 可紅
  缺一路整電池非 0
  F2 綠只是地板
[R-6] 三前置 AND 缺一就 legacy
  理由含 F3 cut 未發生
  in-flight 不折
[R-7] 不刪閘不折不白老鼠
  token 仍在
  Must-keep 紅仍拒 hop
[R-8] 本 hop 只 draft 雙檔加 Files 清單
  Stage3 N/A 零命中
  禁區 Diff Budget 等於 0
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.5）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、Disposition／CASE／Files 清單、Stage 3 N/A 字面。F3 行為 S 的綠發生在後站落地之後，不在本 PR。S 數見確認紀錄；>40 誠實記帳，不另切開新 slug。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-f3/4-spec.md` 後審頁可解析 R/S。本 hop 禁改 `scripts/` 牙。
- 非功能：本 slug 自己仍走舊 7。本 hop 不 bump 契約、不改 graph。本 hop 不送 G2。
- 無 golden master（可見路線行為在後站 cut 落地才變；本 hop 不改 runtime）。

### Stage 3 對帳

Owner ACCEPTED Stage3 N/A。`3-prototype.md` 九條全未勾（0／9）。Demo verdict＝N/A＋各條原因。無 ACCEPTED Demo 場景。無 `3-prototype.html`（N-skip）。

| # | 觸發 | 命中 | 下落 |
|---|---|---|---|
| 1 | 有新的前端流程 | 否 | 無場景；Out of Scope：無新產品畫面 |
| 2 | 改變使用者下一步 | 否 | 3C observable 已鎖；simplify D1 已走；本刀無新「點哪」 |
| 3 | 涉及角色交接 | 否 | 交接名單沿用；1A 三槽不是新交接 UI |
| 4 | 涉及人工核准 | 否 | 不新增閘；可見紀錄不是新核准 Demo |
| 5 | 涉及等待/退回/逾時 | 否 | 摺例行停點；Ship 等待語意已鎖 |
| 6 | 涉及權限差異 | 否 | 未宣告不得改線已是牙 |
| 7 | 涉及系統外動作 | 否 | marketplace／doctor 語意已鎖 |
| 8 | 涉及多種可行互動設計 | 否 | 1A–6A 已 lock；OPEN 是檔名／機制 |
| 9 | Stage 1 操作流程不確定 | 否 | Q15–Q27 已收進 Decision |

Decision 內部技術選擇寫「不預先跳過、觸發判定留給該站」——該站判定＝0 命中，**不是** skip-OC。Demo verdict＝N/A＋本表。本 hop 不改 `3-prototype.md`。

## Out of Scope

鎖死，後站不准改成 In：

1. **重開 F2 park D-1／D-2／D-3／F-c-4。**
2. **刪 G1／G2／`ACCEPTED` token 或檔**。
3. **把 in-flight 折成五站**（含本目錄、含 `five-station-f2`、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
4. **拿本 slug 當活五站白老鼠**；發明第一隻活五站名字。
5. **silent `True` 當 cut**；把 `f3_cut_happened==True` 當 F3 完。
6. **2.1.0 當 cut**；重開 4A 三前置形狀。
7. **doctor 綠／marketplace update／plugin cache 當 cut 或路條**；出貨態故意 doctor 紅當目標；改 `_doctor_impl.py` 握手語意。
8. **只改 guide／STATUS 用字當 F3 完**；本 PR／本 feature branch 改 STATUS 正本表列。
9. **只改 graph、不宣告 2.1.0**；**只宣告 dual-read、新 slug 仍停 `N7-g1`**；**只翻 coordinator 留例行停點**。
10. **刪 `N7-g1`／`N6-g2` 節點**；一次大爆炸改模板全文。
11. 放寬 hop≤2／Decide≤1／Goal reopen≤1；重開 F0 十條。
12. 把「檔在」或「F2 綠」當 F3 完成；把 F2 綠寫成 SC-BATTERY 第四條 IFF。
13. 本 PR 實作 cut／改 `graph.yaml`／bump 契約／改 doctor／改 coordinator、填 G2 PASS、改 2-decision／3-prototype。
14. 把 cut 鎖成與版本同檔的兄弟布林；用 git blame 冒充 who／when。
15. 改已經 freeze 的 slug 的路線。
16. fallback／dual-read 錯鍵當 `contract_version()` 正讀；錯鍵 bump 當已宣告。

## Diff Budget

整節是估計，不是承諾。[Assumption]。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| 本 hop 規格 md | 1 | ≤1,400 | `docs/dev/five-station-f3/4-spec.md` |
| 本 hop 審頁 html | 1 | 產器產出 | `4-spec.html`；不手包 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約／2-decision／3-prototype | 0 | 0 | 本 hop＝0；出現＝S-8.1 紅 |

**G2 之後、本 slug Stage 5–7（只 F3 准許檔）**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| `scripts/test-five-station-f3.sh` | 1 | ≤250 | 單一電池入口 |
| `scripts/check-five-station-f3.sh` | ≤1 | ≤120 | 可選獨立 check |
| `scripts/five_station_f2.py` 讀端 | 1 | ≤80 | 只讀鍵 + cut 讀檔 |
| `notes/design/five-station-f3-cut-attestation.md` | 1 | ≤40 | 三槽 |
| `scripts/fixtures/five-station-f3/new5/` + `old7/` | ≤12 | ≤400 | 合成 NEW5 + OLD7 |
| `devflow-contract.json` 正本鍵 bump | 1 | ≤4 | 只 `devflow_contract_version` |
| `hooks/runtime-capabilities.json` 加 2.1.0 | 1 | ≤4 | 只 supported 清單 |
| `guides/guide-dev-flow.html` 用語 | 1 | ≤30 | 七站單行 → 五站 |
| `stage2`／`stage4` `graph.yaml` 預設 next | 2 | ≤40 | 不刪節點 |
| 電池／CASE 測試（與非測試分開） | ≤8 | ≤900（測試） | 突變另加係數 |
| G1／G2／`ACCEPTED` token 刪檔 | 0 | 0 | ＝0，否則 S-8.2 紅 |
| `_templates/` Stage 1–4／doctor 握手／STATUS／HISTORY | 0 | 0 | 看板另 companion |
| 同檔兄弟 cut 布林 | 0 | 0 | ＝0，否則 S-1.6 紅 |

Stage 5 Files 准許清單正本＝S-8.2。超出 → L2。

## Dependencies

| 依賴 | justification |
|---|---|
| F0 brief＋狀態機 | freeze／新 slug／舊機械／採用端四條；本檔不重開 |
| F1 teeth＋annex | SLOT-REJECT／DOCTOR-GREEN／IN-FLIGHT-DETECT 回歸地板 |
| F2 coordinator＋電池 | 三前置形狀、`allow_legacy`、F2 綠＝地板 |
| `scripts/check-spec-gate.sh` | 本 hop 形狀閘 |
| `scripts/build-stage4-html.py` | 本 hop 審頁 |
| `scripts/check-gate-tokens.sh` | TOKEN-KEEP |
| `scripts/test-five-station-f2.sh` | 地板；**不是** F3 完成入口 |
| 現行 doctor／契約 2.0.0 | SC-DOCTOR 現況可測；本 hop 不改 |

無新外部服務。cut 紀錄是本 repo 檔案，不是新 SaaS。

## Design Boundary Contract

- Applicability: applicable
- Trigger(s): ①跨模組（coordinator 讀端／契約／graph／supported 清單）／②公開契約版本 2.1.0／③跨模組 Interface（hop 目標）／⑨Feature Risk = high／⑪狀態機（五站 vs 舊 7）
- Design source: Decision 1A／2A／3C／4A／5A／6A；`notes/design/five-station-simplify-f1-dual-read-annex.md`；new local design＝cut 紀錄路徑形（DD-1）與 hop-skip 機制（DD-3）

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| cut 紀錄檔 | 三槽 who／when／condition | 母版 owner 簽名 | `f3_cut_happened()` 只讀 | `devflow-contract.json` 兄弟布林；git blame；STATUS；chat |
| 讀鍵 | `declared` ← 正本鍵 | `devflow-contract.json` | 只讀 `devflow_contract_version` | fallback `version`／`contract_version` |
| 路線閘 | 三前置 → 五站或 `allow_legacy()` | 專案樹契約 + 1–7 `.md` + cut 紀錄 | F2 coordinator | doctor 綠；marketplace；cache |
| graph 節點 | 保留 `N7-g1`／`N6-g2` 給 freeze／未宣告 | 方法包 yaml | coordinator hop-skip | 刪節點；未宣告遠端改線 |
| F3 電池 | NEW5+OLD7+TOKEN 同一 process | 合成 fixture | F2 電池當地板 | 本目錄當 NEW5；只轉呼叫 F2 當完成 |
| doctor | 握手 | supported 清單 | 只加 2.1.0 | 改握手語意；綠當路條 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| `f3_cut_happened()` | 讀 DD-1 檔 → bool | 缺檔／缺鍵 → False | 只讀；呼叫不寫檔 | 不與版本同檔 |
| `contract_version()` | 讀正本鍵 → 字串 | 缺檔／缺鍵 → `""` | 禁止錯鍵 fallback | 2.0.0 現況落地後應回 `2.0.0` |
| 路線閘 | 三前置布林 | 缺一 → allow_legacy | 只讀專案樹＋紀錄；不寫採用端契約 | 未宣告仍舊 7 |
| hop-skip | 三前置全真 → 跳過 N7-g1／N6-g2 | 缺一 → 仍進入 | yaml 節點不刪 | in-flight 共用舊路 |
| 電池入口 | 無參數 | 缺一組 → 非 0 | 單一 process 內三組都跑完才 0 | F2 腳本不是入口 |
| doctor supported | 契約版本 ∈ 清單 | 漏 2.1.0 → INCOMPATIBLE | 不改比對語意 | 綠 ≠ 路條 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| cut record parser | 解析三槽 | `f3_cut_happened` | 檔 → bool | 缺鍵＝假 | 可換 fixture 紀錄檔 |
| version reader | 只讀正本鍵 | 路線閘 | JSON → 字串 | 錯鍵忽略 | 可換假契約檔 |
| hop skipper | 真則跳過例行閘 | graph 節點（保留） | 前置 → hop id | 缺前置走舊點 | 注入仍進 N7-g1 |
| battery | 22+ CASE | NEW5／OLD7／TOKEN fixture | 紅格餵壞行為 | 極性反了 → 非 0 | 各 CASE 獨立格 |
| supported list | 加 2.1.0 | doctor（不改實作） | 清單 → 握手 | 漏加誠實紅 | 清單去掉 2.1.0 |

### Design Constraints

- 必須:可見紀錄三槽；函式只讀；只讀正本鍵；hops 不得早於 2.1.0；graph+dual-read；節點不刪；同一電池三路；Files 准許清單。
- 禁止:silent True；同檔兄弟布林；blame 當 who／when；doctor 綠當票；本目錄當 NEW5；本 hop 填 G2 PASS；刪 token；折 in-flight。
- Extension point:4-spec 可加 CASE 列；不得減原 22 列。
- Known design limit:本 hop 不落地 cut／graph／契約；行為 S 的執行綠在後站。審頁產器 `steps[:8]`，本檔正好 8 個 R，不增 R-9。STATUS 用語切只能走整合分支 companion。cut 落地前現場新 slug 仍舊 7（本來就該如此）。

## Verification Profile

- lane: full（判準:公開契約版本、採用端改線、graph 預設 hop、Feature Risk=high。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:採用端被遠端改線、不可逆預設路線、公開契約 API。模板「不可逆／公開 API」吃這條）
- Failure model: 見下表
- Negative constraints: 見 Out of Scope 全列（後站不准改成 In）；另：紅格不得把拒 hop 當綠；本 hop 不得改 STATUS／牙／契約／graph；不得把 F2 綠寫進 SC-BATTERY IFF；不得只加 supported 卻改握手語意
- Required layers: spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`）；token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F3 電池列 Required——Required 層不得 unverified
- Conditional layers: F3 cut／電池落地 → 該刀列入 Required，單一入口 `bash scripts/test-five-station-f3.sh`（NEW5+OLD7+TOKEN；缺一路即非 0）；F2 電池在落地後當地板重跑。契約 bump 後 doctor 握手重跑。本 hop 不改那些檔、電池未落地 → 本 hop 不觸發 Conditional
- Explicitly excluded layers: UI e2e（本刀無新前端）；負荷／效能（cut 非熱路徑）；金流／auth fuzz（不涉）；本 hop 跑 cut 落地碼（碼 Out of Scope）
- Final fresh entry point: `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`
- Reliability triage:
  - Concurrency: applicable — 兩 process 同讀 cut 紀錄與正本鍵，不得一個看見 cut、一個看見未切（Failure Model「讀端分叉」；落地後同一檔同一鍵）
  - Idempotency: applicable — 再讀同一紀錄檔不得把假變真；`contract_version()` 對同一 JSON 再讀結果不變（S-1.2、S-2.1）
  - Timeout/retry: n-a — 本刀無新逾時／重試迴圈；例行停點摺掉後剩 Ship 等人，語意已由 F0／F2 鎖（S-7.6）

### Failure Model

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| silent True 當 cut | 無可見紀錄卻改線 | ATTEST-SILENT-RED 不紅 | Required:S-1.3、S-5.3 | — |
| 2.1.0 冒充 cut | 第三位元無法獨立為假 | PRE-210-NE-CUT 理由錯 | Required:S-1.4、S-6.2 | — |
| 只 bump 正本、reader 仍舊 | 假宣告 | READ-SEAM 不紅 | Required:S-2.3 | — |
| 2.0.0 + 五站 hops | 遠端改線 | PRE-HOPS-200 不拒 | Required:S-2.5 | — |
| 只用字當完 | 行為沒切 | GRAPH-WORD-NE 不紅 | Required:S-3.5、S-5.6 | — |
| 刪 N7-g1／N6-g2 | in-flight 無舊路 | S-3.4 字面消失 | Required:S-3.4 | — |
| doctor 綠當票 | 舊 7 被折 | 拒絕理由含「doctor 已綠」 | Required:S-4.2 | — |
| 漏 supported 卻放寬綠 | 隱瞞未宣告 | DOCTOR-HONEST 不紅 | Required:S-4.3 | — |
| 只跑 F2 或只檔在 | hollow F3 | 入口仍 0 | Required:S-5.1、S-5.4、S-5.5 | — |
| 對本目錄建五站機 | 觀測白老鼠 | SELF-OLD7 跳得過 | Required:S-7.3 | — |
| 本 hop 自填 G2 PASS | 四眼破 | 頂欄 PASS | Required:S-8.1 | — |
| 讀端分叉 | 一 process 切、一 process 未切 | 兩讀結果不同 | Conditional:Concurrency | 本 hop 不寫碼；後站 seam＝紀錄檔可換 |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q15 silent flip 不合法 | stage-2 | oc-accepted |
| Q16 hops 不得早於 2.1.0 | stage-2 | oc-accepted |
| Q17 只 bump 正本仍假 | stage-2 | oc-accepted |
| Q18 漏 supported 誠實紅 | stage-2 | oc-accepted |
| Q19 同一電池三路 | stage-2 | oc-accepted |
| cut 紀錄路徑交 4-spec（本檔 DD-1） | 2026-12-31 | open |
| 電池入口檔名交 4-spec（本檔 DD-2） | 2026-12-31 | open |
| graph 切換機制交 4-spec（本檔 DD-3） | 2026-12-31 | open |

Q15–Q19 已由 Decision OC 升格，故 oc-accepted。後三列是本檔釘形，期限給後站落地，不是已過站。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–6A。推翻 Decision 不是合法 DD。狀態留待人審；**不發明 G2 PASS**。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | cut 紀錄路徑＝`notes/design/five-station-f3-cut-attestation.md`；鍵＝`who`／`when`／`condition`（`condition` 字面 `F3-cut-happened`）。不是契約同檔兄弟布林 | Decision 把路徑 OPEN 交 4-spec；必須可測且人指得到 | `2-decision.md` 約束 3；決策點 1A。路徑本身 `[Assumption]` | 改回同檔布林＝誘發 bump＝cut；改 blame＝違約束 3 | 待人審 |
| DD-2 | 單一電池入口檔名＝`scripts/test-five-station-f3.sh` | Decision 只鎖同一 process、缺一路即非 0；檔名交給 4-spec | `2-decision.md` 5A；內部技術選擇「入口檔名交 4-spec」。檔名 `[Assumption]` | 改兩支腳本各綠＝hollow；只包 F2 腳本＝HOLLOW-F2 | 待人審 |
| DD-3 | graph 切換＝coordinator hop-skip + 保留 `N7-g1`／`N6-g2` 節點；不另建第二份 graph 當正本 | Decision 只鎖 observable；機制交 4-spec | `2-decision.md` OC-5。機制 `[Assumption]` | 刪節點＝折 in-flight；只改用字＝GRAPH-WORD-NE | 待人審 |
| DD-4 | NEW5 fixture 根＝`scripts/fixtures/five-station-f3/new5/`；OLD7 根＝`scripts/fixtures/five-station-f3/old7/` | 與 live 三目錄分家 | `2-decision.md` 約束 12。路徑 `[Assumption]` | 拿本目錄當白老鼠＝X4 | 待人審 |
| DD-5 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 G2 PASS | 採用端改線＋不可逆預設＋公開契約；四眼 | `_templates/4-spec.md` Risk 判準；本 hop brief「No G2 invent」。`[Assumption]` 僅本 hop 範圍 | 改 normal 則 Failure Model 變選配；代填 PASS＝假綠 | 待人審 |
| DD-6 | Stage 3 對帳＝0 命中 N/A；Owner ACCEPTED Stage3 N/A；不是「命中仍跳過」 | Decision 無 skip OC；九條全未勾；owner 本 hop 指令 N/A | `3-prototype.md:L19-L32`；本 hop dispatch | 寫 skip OC 而無命中＝假跳過；發明 ACCEPTED＝假 hit | 待人審 |
| DD-7 | Stage 5 Files 准許清單＝S-8.2 具名路徑；禁區 Diff Budget＝0 | F2 S-8.9 同形；F3 要動契約／graph／guide，所以清單與 F2 相反處寫死 | 本檔 S-8.2。清單本身 `[Assumption]` | 無清單則後站可偷刪閘或改 STATUS | 待人審 |
| DD-8 | S 數 >40 留在本檔、不另切開新 slug；行為圖 8 框對 8 個 R（產器 `steps[:8]`） | 誠實記帳；不改 scripts | `scripts/build-stage4-html.py` L450；本 hop 不改牙 | 增 R-9 則圖丟框 | 待人審 |
| DD-9 | 原文獨立於他線 Stage 4；不換 Decision winner 1A+2A+3C+4A+5A+6A | Writer B 主軸（cut SoT／讀鍵／graph+dual／doctor／hollow／Files） | 本 hop owner 指令 | 改換 winner＝丟 B 骨架 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `STATUS.md`（另 companion）、不 bump plugin、不開 5-tasks、不發明 G2／G3 PASS。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。
- F2 電池可留作回歸地板（F3-F2-REGRESS）；不得替代 F3 三路電池。
- `3-prototype.md` 維持原檔；本 hop 不回寫、不建 html。
- Backlog A「下一刀 F1」保持 stale 事實，本 PR 不改看板。

## Test Skeletons(選配)

- `test_s_1_1_attest_visible`
- `test_s_1_3_attest_silent_red`
- `test_s_2_1_read_canonical_key`
- `test_s_2_3_read_seam_red`
- `test_s_2_5_pre_hops_200`
- `test_s_3_1_new_slug_no_n7`
- `test_s_3_2_new5_wait_red`
- `test_s_3_4_nodes_kept`
- `test_s_4_2_doctor_ne_ticket`
- `test_s_4_3_doctor_honest`
- `test_s_5_1_battery_single_entry`
- `test_s_5_3_hollow_true`
- `test_s_5_4_hollow_files`
- `test_s_5_5_hollow_f2`
- `test_s_6_2_pre_210_ne_cut`
- `test_s_6_5_old7_fold_red`
- `test_s_7_1_token_keep`
- `test_s_7_3_self_old7`
- `test_s_8_1_pr_two_files_draft`
- `test_s_8_2_files_allowlist`

## 確認紀錄

- 前站核對 | 2026-09-14 | G1 PASS（#368，`2-decision.md` `verdict: PASS`、OC-1…OC-12 ✅）。Stage 3：#373 0／9 N/A；Owner 本 hop 指令 ACCEPTED Stage3 N/A。無晚改可見行為。雙源：驗收雛形 AC-1…AC-11 共 11 條；living spec 無改寫列。
- R 範圍 | 2026-09-14 | 8 個 R：cut SoT／讀鍵縫／graph+dual-read／doctor／電池+hollow／三前置／Non-Goals／本 hop+Files+Stage3。Writer B 自定範圍；G2 人審。
- S 展開 | 2026-09-14 | 每 S 有觀測欄。Decision 22 CASE 全掛 S。SC 全表有 S。
- 4 小節 | 2026-09-14 | AC／Out of Scope／Diff Budget／Dependencies 齊。
- Profile + DBC | 2026-09-14 | lane full、Risk high、Failure Model 有表、Reliability triage 三問。DBC applicable（①②③⑨⑪）。
- Stage 3 對帳 | 2026-09-14 | 九條逐列 N/A。Owner ACCEPTED Stage3 N/A。不是 skip-OC。
- DD 掃描 | 2026-09-14 | 上層 DD-1…DD-9 待人審。無「待裁決」字面。無 C4 未定三詞。
- 本 hop 不送 G2 | 2026-09-14 | `verdict` 空；`status: draft`。不跑三連動。不改 STATUS。
