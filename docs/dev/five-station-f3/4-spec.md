---
feature: five-station-f3
stage: 4-spec
status: draft
verdict:
owner: rick
reviewers: []
updated: 2026-09-14
---

# 4. 規格 — 五站 F3 change spec（Writer C：cut SoT／讀鍵縫／graph+dual-read／doctor／SC≠hollow／Files 准許清單）

> 基準:金本 Decision B + standing soft-fix（`2-decision.md` `verdict: PASS`、OC-1…OC-12 ✅；#366／#368）。骨架 **1A+2A+3C+4A+5A+6A**。Lane = **full**。
> Writer C 只釘 Decision 交給本站的三個形：cut SoT 路徑、graph 切換機制、電池入口檔名；再把 Files 准許清單與 Stage 3 N/A 寫死。不換 winner。不重開 F2 park D-1／D-2／D-3／F-c-4。不重開 4A 三前置形狀。
> Stage 3：九條 0 命中 → **Demo verdict = N/A**。Owner ACCEPTED Stage3 N/A（無 trigger、無 Demo）。不是 Human ACCEPTED 一場可點 Demo。見 Stage 3 對帳。
> 本 hop **只** `4-spec.md` + `4-spec.html`。`status: draft`。`verdict` 空。**不發明 G2 PASS**。不改 `STATUS.md`／`HISTORY.md`／`2-decision.md`／`3-prototype.md`／`_templates/`／`graph.yaml`／doctor／契約／coordinator。不寫 cut 碼。不合併。
> CASE 原 20 列 + standing PRE-AND／F3-F2-REGRESS **只准加不准減**。極性＝注入壞行為 → **該格**紅。F2 綠是地板，不是 SC-BATTERY 第四條 IFF。

## 補助模組生命週期（預覽）

主詞是「F3 cut：可見紀錄 SoT + 讀鍵縫 + graph 謂詞跳過 + doctor 清單 + 三路電池」，不是整份方法論。直式圖，置中。
- 新生（這輪新欄／新表）：cut 可見紀錄檔、F3 單一電池入口、NEW5／OLD7／TOKEN 三路 CASE
- 改行為（相關一格）：`f3_cut_happened()` 改讀可見紀錄；`contract_version()` 只讀正本鍵；新 slug 不再例行進 `N7-g1`／`N6-g2`
- 退役：沒有
- 不動：G1／G2／`ACCEPTED` token、`N7-g1`／`N6-g2` 節點本體、`_doctor_impl.py` 握手語意、F2 park D-1／D-2／D-3／F-c-4、本 slug 舊 7、`_templates/` 全文

## Real-world Disposition

承接 Stage 2 去向帳。引用 = Stage 1 原文片段，不發第二鏈編號。

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 「F3 該把『之後才開、cut 當下尚無 1–7 `.md`』的 slug 預設改五站」 | 本方案處理 | R-3、S-3.1、S-5.2 |
| 「只把函式改 `True`、只改 guide 用字、或契約仍 `2.0.0` 就把 hops 當五站預設」 | 本方案處理 | S-1.2、S-2.4、S-3.3 |
| 「本目錄一有本檔就是 in-flight,拿自己當第一隻活五站 = 污染觀測」 | 本方案處理 | S-6.4、S-6.5 |
| Journey「新 slug 仍經 `N7-g1` 等人;chat 可蓋章」 | 本方案處理 | S-3.1、S-3.2 |
| Journey「doctor 綠只證明 `2.0.0 ∈ supported`≠切線」 | 本方案處理 | R-4、S-4.2 |
| Journey「coordinator 缺 cut → legacy；理由=`F3 cut 未發生`」 | 本方案處理 | S-2.3、S-6.1 |
| Workaround「恒 `False` 擋 live 五站；擋的是行為,不是人看得見的 cut 紀錄」 | 本方案處理 | R-1、S-1.3 |
| Workaround「STATUS／HISTORY 當刀口 log；看板列 ≠ cut」 | 本方案處理 | S-1.6、S-8.3 |
| Exception「不准改已經 freeze 的 slug」 | 本方案處理 | S-6.2、S-6.3 |
| Exception「`[Assumption]` 只把函式改 True、不 bump、不改 hops = 空切」 | 本方案處理 | S-1.2、S-5.6 |
| Exception「契約仍 2.0.0 卻把 hops 當五站預設 = SLOT-REJECT」 | 本方案處理 | S-2.4 |
| Exception「只改 guide、graph 仍停 `N7-g1` = 用語切、行為沒切」 | 本方案處理 | S-3.3 |
| Exception「NEW5 不是本目錄、也不是 `five-station-f2`／`five-station-simplify`」 | 本方案處理 | S-6.5 |
| Q15 silent flip 不合法 | 本方案處理 | S-1.2、S-1.5 |
| Q16 2.1.0 必須同動或先於 hops 預設 | 本方案處理 | S-2.4、S-2.5 |
| Q17 只 bump 正本鍵、`declared` 仍假 | 本方案處理 | S-2.1、S-2.2 |
| Q18 bump 後 supported 未加 → 誠實紅 | 本方案處理 | S-4.1 |
| Q19 同一電池三路、hollow 不算 | 本方案處理 | R-5、S-5.1、S-5.6、S-5.7、S-5.8 |
| Q20 第三位元怎麼被指認 | 本方案處理 | S-1.1、S-1.3、DD-1 |
| Q21 graph 四選項 | 本方案處理 | R-3、S-3.1、S-3.4、DD-2 |
| Q22 改 doctor 實作還是只加清單 | 本方案處理 | S-4.1、S-4.4 |
| Q23 guide 用語算哪些檔 | 本方案處理 | S-1.6、S-8.2 |
| Q24 STATUS 用語 vs feature branch 禁碰 | 本方案處理 | S-8.3 |
| Q25 第一隻活五站叫什麼 | 本方案處理 | S-6.5 |
| Q26 三前置形狀、2.1.0 ≠ cut | 本方案處理 | S-2.3、S-6.1 |
| Q27 live reader 回空字串 | 本方案處理 | S-2.1 |
| 「鎖:不刪 G1／G2／`ACCEPTED`；不把 in-flight 折成五站；不拿本 slug 當白老鼠」 | 本方案處理 | R-8、S-5.4、S-6.4、S-8.1 |
| Q14 Backlog A 過期 | 刻意維持 | Out of Scope：本 PR 不改 STATUS；看板 lag ≠ 已切 |
| AC-11 Q15–Q25 到規格有去向 | 本方案處理 | 本節 Disposition；S-8.6 |

## SC → S 對照

Decision Success Criteria 每條至少一條獨立可測 S。4-spec **只准加不准減** CASE 列。

| SC | 一句 | 本檔 S |
|---|---|---|
| SC-BATTERY | 單一入口；NEW5+OLD7+TOKEN 都過才 exit 0；F2 綠不是第四條 IFF | S-5.1 |
| SC-F2-REGRESS | F2 電池仍綠；地板，不是完 | S-5.9 |
| SC-NEW5-CUT-OK | cut 後新 slug 預設五站；不等例行 G1／G2 | S-3.1、S-5.2 |
| SC-NEW5-WAIT-RED | 注入謂詞真仍停 `N7-g1` → 該格紅 | S-3.2 |
| SC-OLD7-FREEZE | 已有 1–7 `.md` → 舊 7；無五站寫入 | S-6.2 |
| SC-OLD7-FOLD-RED | 注入對 in-flight 寫五站 → 該格紅 | S-6.3 |
| SC-TOKEN-KEEP | token 與檔仍在；`check-gate-tokens.sh` 綠 | S-5.4 |
| SC-TOKEN-DEL-RED | 注入刪 token 卻標 F3 成功 → 該格紅 | S-5.5 |
| SC-ATTEST-VISIBLE | 人指得到誰／何時／哪個條件 | S-1.1 |
| SC-ATTEST-SILENT-RED | 注入 silent `True` 無紀錄卻宣稱已切 → 該格紅 | S-1.2 |
| SC-PRE-210-NE-CUT | 2.1.0 真、cut 假 → `allow_legacy()`；理由含「F3 cut 未發生」 | S-2.3 |
| SC-PRE-AND | 三前置缺一 → `allow_legacy()` | S-6.1 |
| SC-PRE-HOPS-200 | 2.0.0 + 五站 hops 預設 → SLOT-REJECT、未改線 | S-2.4 |
| SC-READ-SEAM | 注入只 bump 正本、reader 仍舊、卻稱已宣告 → 該格紅 | S-2.2 |
| SC-DOCTOR-HONEST | 2.1.0 ∉ supported → INCOMPATIBLE | S-4.1 |
| SC-DOCTOR-NE-TICKET | COMPATIBLE + 2.0.0 求五站 hop → 拒；理由是路線 | S-4.2 |
| SC-GRAPH-WORD-NE | 只改用字、新 slug 仍停 `N7-g1`、卻標成功 → 該格紅 | S-3.3 |
| SC-SELF-OLD7 | 對本目錄／F2／simplify 求五站自動前進 → 拒 | S-6.4 |
| SC-HOLLOW | 僅函式真／僅檔在／僅 F2 綠／僅用字 → 不得當 F3 綠 | S-5.6、S-5.7、S-5.8、S-3.3 |
| SC-KEEP | Must-keep 紅仍 hop／機械綠無人 PASS 卻 Done → 該格紅 | S-7.1、S-7.2 |
| SC-Q-CARRY | Q15–Q27 皆有去向 | 本節 Disposition；S-8.6 |
| SC-PR | 本 Stage 4 hop 只 4-spec 雙檔、draft、無 G2 PASS、無 STATUS | S-8.4 |

## CASE → S 對照（Decision 原 20 列 + standing 2 列只准加）

極性：標「→ 紅」＝**注入該壞行為**，該格必須獨立變紅。把「拒 hop」記成紅格綠＝極性反了，已拒。

| CASE | 路 | 紅／綠 | 本檔 S |
|---|---|---|---|
| NEW5-CUT-OK | NEW5 | 綠：cut 後無 1–7 `.md` → 預設五站 | S-3.1、S-5.2 |
| NEW5-WAIT-RED | NEW5 | **注入** 謂詞真 latch 假仍停 `N7-g1`／要不要繼續 → **該格紅** | S-3.2 |
| OLD7-FREEZE | OLD7 | 綠：已有 1–7 `.md` → 舊 7、無五站寫入 | S-6.2 |
| OLD7-FOLD-RED | OLD7 | **注入** 對 in-flight 寫五站狀態／五站 hop → **該格紅** | S-6.3 |
| TOKEN-KEEP | TOKEN | 綠：token 與檔仍在 | S-5.4 |
| TOKEN-DEL-RED | TOKEN | **注入** 刪 token 卻標 F3 成功 → **該格紅** | S-5.5 |
| ATTEST-VISIBLE | ATTEST | 綠：人指得到誰／何時／哪個條件 | S-1.1 |
| ATTEST-SILENT-RED | ATTEST | **注入** silent `True` 無可見紀錄卻宣稱已切 → **該格紅** | S-1.2 |
| PRE-210-NE-CUT | PRE | 綠：2.1.0 真、cut 假 → `allow_legacy()` | S-2.3 |
| PRE-AND | PRE | 綠：三前置缺一 → `allow_legacy()` | S-6.1 |
| PRE-HOPS-200 | PRE | 綠：2.0.0 + 五站 hops → SLOT-REJECT | S-2.4 |
| READ-SEAM | PRE | **注入** 只 bump 正本、reader 仍舊、卻稱已宣告 → **該格紅** | S-2.2 |
| DOCTOR-HONEST | DOC | 綠：2.1.0 ∉ supported → INCOMPATIBLE | S-4.1 |
| DOCTOR-NE-TICKET | DOC | 綠：COMPATIBLE 不是 hop 通行證 | S-4.2 |
| GRAPH-WORD-NE | GRAPH | **注入** 只改用字、新 slug 仍停 `N7-g1`、卻標成功 → **該格紅** | S-3.3 |
| SELF-OLD7 | SELF | 綠：本目錄／F2／simplify 跳不過 | S-6.4 |
| HOLLOW-TRUE | HOLLOW | **注入** 把 `f3_cut_happened==True` 標成 F3 綠 → **該格紅** | S-5.6 |
| HOLLOW-FILES | HOLLOW | **注入** 把「檔在」標成 F3 綠 → **該格紅** | S-5.7 |
| HOLLOW-F2 | HOLLOW | **注入** 只跑 F2 電池綠就標 F3 綠 → **該格紅** | S-5.8 |
| F3-F2-REGRESS | 地板 | 綠：`test-five-station-f2.sh` exit 0；**不是完** | S-5.9 |
| KEEP-MK-RED | KEEP | **注入** Must-keep 紅仍 hop → **該格紅** | S-7.1 |
| KEEP-SHIP-MECH | KEEP | **注入** 機械綠無人 PASS 卻 Ship Done → **該格紅** | S-7.2 |

減 Decision 原列任一列 = 翻 Decision。加列不得把「函式真／檔在／F2 綠／用字」加成通過條件。

## ADDED Requirements

### R-1: 系統 SHALL 以人類可見獨立紀錄為 cut SoT，且 `f3_cut_happened()` 只讀該紀錄

1A。語意槽＝誰／何時／哪個條件。路徑＝`notes/design/five-station-cut-attest.md`（DD-1）。函式本體改 `return True` 且紀錄缺＝空切。2.1.0 ≠ cut。STATUS／guide 用語 ≠ SoT。禁止同檔兄弟布林。禁止 git blame 冒充 who／when。

**審的時候看什麼**
人能不能指出三個槽。函式是不是只讀。有沒有人把 `True` 或看板當 cut。

#### S-1.1 ATTEST-VISIBLE：人指得到誰／何時／哪個條件
- GIVEN cut 已宣稱發生；SoT 檔為 `notes/design/five-station-cut-attest.md`（DD-1）；frontmatter 三鍵 `who`／`when`／`condition` 皆非空
- WHEN 人打開該檔並讀 frontmatter
- THEN 三槽各自有字面值；`who` 是人類名或帳號，不是 git hash；`when` 是 `YYYY-MM-DD`；`condition` 寫出讀哪個前置（至少含 cut 位元本身）。chat 口頭與函式回傳值本身都不算本格綠
- 觀測:從該檔 frontmatter 三鍵看 | 三鍵非空且人指得到檔路徑算過 | n-a:本 hop 不建該檔。替代：本條字面 + DD-1
- Operational Context:
  - Actor:母版 owner／G2 reviewer
  - Goal:指出「已切」的可見紀錄
  - Situation:有人宣稱 F3 已切
  - Known information:Decision 1A 語意槽
  - Missing information:本 hop 尚未落檔
  - Human decision:三槽空則不得簽已切
  - Authority:owner 寫 SoT；函式禁自寫判定
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:無紀錄則 cut 位元假，live 仍舊 7
  - Recovery:補三槽後重讀
  - Audit/handoff requirement:路徑與三鍵留下
  - Observation:見本條觀測

#### S-1.2 ATTEST-SILENT-RED：注入 silent True 無紀錄卻宣稱已切 → 該格紅
- GIVEN 對照物為「`f3_cut_happened` 改成 `return True`，且 `notes/design/five-station-cut-attest.md` 不存在或任一槽空」
- WHEN **注入**該壞行為，並宣稱 F3 已切
- THEN **該格獨立變紅**。不得標 F3 成功。把「函式回真」記成本格綠＝極性反了，已拒
- 觀測:從該 CASE 獨立紅標看 | 注入 silent True 紅；拒切不得當此格綠算過 | Decision AC-4；約束 1
- Operational Context:不適用 — 測法極性，無新交接。

#### S-1.3 函式只讀 SoT 檔，缺檔或空槽回假
- GIVEN `f3_cut_happened(project_root)` 的讀端
- WHEN (a) SoT 檔缺；(b) 檔在但 `who`／`when`／`condition` 任一空；(c) 三槽皆非空
- THEN (a)(b) 回 `False`；(c) 回 `True`。函式不寫該檔、不寫契約、不寫 STATUS
- 觀測:從該函式回傳值 + 檔是否被寫入看 | 缺／空＝假；滿＝真；函式零寫入算過 | n-a:本 hop 不改 `five_station_f2.py`。替代：Decision 約束 3；DD-1
- Operational Context:不適用 — 讀端契約。

#### S-1.4 禁止把 cut 鎖成 `devflow-contract.json` 兄弟布林
- GIVEN 契約檔現況鍵為 `devflow_contract_version`
- WHEN 後站 Files 或實作把 `f3_cut`／`cut_happened` 布林寫進同一份 `devflow-contract.json`
- THEN 本條紅。cut SoT 必須是獨立紀錄檔（DD-1），不得與版本同檔
- 觀測:從 `devflow-contract.json` 鍵名 + 5-tasks Files 看 | 出現 cut 兄弟布林＝本條紅算過 | Decision 約束 3；OC-1
- Operational Context:不適用 — 檔形禁令。

#### S-1.5 禁止用 git blame 冒充 who／when
- GIVEN SoT 檔或 `f3_cut_happened` 讀端
- WHEN 有人用 `git blame`／commit hash 填 `who` 或 `when`，或讀端以 blame 當三槽
- THEN 不算 ATTEST-VISIBLE 綠；cut 位元仍假，直到 frontmatter 三槽由人類寫入
- 觀測:從 SoT frontmatter 是否引用 blame 當槽值看 | blame 當槽＝本條紅、位元假算過 | Decision 約束 3
- Operational Context:不適用 — 槽來源禁令。

#### S-1.6 STATUS／guide 用語 ≠ SoT
- GIVEN guide 至少含 `guides/guide-dev-flow.html` 七站單行（現況 L573）；STATUS 用語切走整合分支 companion
- WHEN 有人只改該指南用字或只改 STATUS 列，且 SoT 三槽仍空
- THEN cut 位元仍假；用語是 F3 **交付物**不是 SoT。F2 D-1 檔案地圖列仍 ≠ cut
- 觀測:從 SoT 三槽 vs guide／STATUS 用字看 | 用字變、三槽空＝未切算過 | Decision OC-2；F2 7-review D-1
- Operational Context:不適用 — SoT 邊界。

### R-2: 系統 SHALL 只讀正本鍵 `devflow_contract_version`，且 hops 預設五站不得早於 2.1.0 已宣告

2A。本 tree 現況 `contract_version()` 讀 `version`／`contract_version`、回 `""`＝已核。落地後只讀正本鍵。禁止 fallback／dual-read 錯鍵。錯鍵 bump ≠ 已宣告。`supported_contract_versions` 同刀加 `2.1.0`。**2.1.0 仍 ≠ cut**。

**審的時候看什麼**
reader 讀哪個鍵。2.1.0 能不能單獨當 cut。2.0.0 能不能先切 hops。

#### S-2.1 `contract_version()` 只讀正本鍵
- GIVEN 專案根有 `devflow-contract.json`
- WHEN 呼叫 `contract_version(project_root)`
- THEN 回傳值＝該檔 `devflow_contract_version` 的字串。不讀 `version`。不讀 `contract_version`。檔缺或 JSON 壞 → `""`
- 觀測:從該函式對三份對照樹的回傳值看 | 正本 `2.1.0` → 以 `2.1` 開頭；只寫錯鍵 `version=2.1.0` → `""` 算過 | n-a:本 hop 不改 reader。替代：Decision 約束 5；現況 `five_station_f2.py` L260-L268 回 `""`
- Operational Context:不適用 — 讀鍵契約。

#### S-2.2 READ-SEAM：注入只 bump 正本、reader 仍舊、卻稱已宣告 → 該格紅
- GIVEN 對照物為「`devflow_contract_version` 已是 `2.1.0`，但 `contract_version()` 仍讀 `version`／`contract_version` 並回 `""`，有人宣稱已宣告 2.1.0」
- WHEN **注入**該壞行為
- THEN **該格獨立變紅**。`declared` 仍假。落地後：正本鍵 2.1.0 → `contract_version()` 以 `2.1` 開頭才算宣告
- 觀測:從該 CASE 紅標 + reader 回傳值看 | 假宣告紅；正本 2.1.0 且只讀正本才算宣告算過 | Decision SC-READ-SEAM
- Operational Context:不適用 — 測法極性。

#### S-2.3 PRE-210-NE-CUT：2.1.0 真、cut 假 → allow_legacy
- GIVEN `contract_version()` 以 `2.1` 開頭；SoT 三槽空或檔缺（cut 假）；slug 無 1–7 `.md`
- WHEN coordinator 評是否建五站機
- THEN `allow_legacy()` 為真；拒絕理由含「F3 cut 未發生」；理由不含「已宣告所以切了」
- 觀測:從 `allow_legacy`／`refuse_hop_reason` 字面看 | 合法拒綠；理由含「F3 cut 未發生」算過 | Decision SC-PRE-210-NE-CUT；現況 `five_station_f2.py` L307
- Operational Context:不適用 — 前置閘。

#### S-2.4 PRE-HOPS-200：2.0.0 + 五站 hops 預設 → SLOT-REJECT
- GIVEN 契約仍 `devflow_contract_version=2.0.0`；有人把 hops 當五站預設（新 slug 不再例行進 `N7-g1`／`N6-g2`）
- WHEN 評路線（F1 SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS）
- THEN 違規紅；不得改線；採用端仍舊 7
- 觀測:從 SLOT-REJECT 牙 + 路線判定看 | 2.0.0+五站 hops 紅、未改線算過 | F1 annex L22-L24；Decision 約束 6
- Operational Context:
  - Actor:採用專案 owner
  - Goal:marketplace update 不得遠端改線
  - Situation:hops 已換、契約仍 2.0.0
  - Known information:SLOT-REJECT
  - Missing information:現場會不會以為 hops 新＝五站
  - Human decision:先宣告 2.1.0 或不同刀切 hops
  - Authority:禁未宣告改線
  - External dependency:採用端自己的契約檔
  - Out-of-system action:自己 bump 契約
  - Waiting/timeout behavior:未宣告則舊 7
  - Recovery:同刀或先宣告 2.1.0
  - Audit/handoff requirement:SLOT 紅因留下
  - Observation:見本條觀測

#### S-2.5 hops 預設五站不得早於 2.1.0 已宣告
- GIVEN 後站 Files 含 graph 謂詞跳過或 hops 預設五站
- WHEN 同一 commit 的 `devflow_contract_version` 仍為 `2.0.0`，或 `contract_version()` 不以 `2.1` 開頭
- THEN 本條紅。宣告與 hops 預設必須同刀或宣告在先
- 觀測:從同一 diff 的契約鍵 vs graph／hops 預設看 | 先切 hops、未宣告＝本條紅算過 | Decision OC-4
- Operational Context:不適用 — 同刀約束。

### R-3: 系統 SHALL 同時做 graph 行為與 dual-read，且不刪 `N7-g1`／`N6-g2`

3C。dual-read：未宣告 2.1.0＝舊 7。graph **行為**：cut 後、非 in-flight 的新 slug 預設路不再例行進 `N7-g1`／`N6-g2`。切換機制＝**謂詞跳過、節點留下**（DD-2）。guide／STATUS 用語必要但不充分。

**審的時候看什麼**
新 slug 還等不等 G1。舊節點還在不在。只改用字能不能過關。

#### S-3.1 NEW5-CUT-OK：cut 後新 slug 預設五站，不等例行 G1／G2
- GIVEN 三前置全真（宣告 2.1.0 ∧ ¬in-flight ∧ SoT 三槽滿）；NEW5 fixture 在 `scripts/fixtures/five-station-f3/new5/`（DD-4）；cut 當下該 slug 無 1–7 `.md`
- WHEN 求預設路線與 Stage 2／Stage 4 下一跳
- THEN 預設五站；不進入 `N7-g1`／`N6-g2` 等人；前進紀錄無「請人審／要不要繼續」。Ship 仍唯人，不在本條自動 Done
- 觀測:從該 fixture 路線判定 + hop 紀錄看 | 五站、無例行 G1／G2 停算過 | n-a:本 hop 不改 graph。替代：Decision SC-NEW5-CUT-OK；DD-2
- Operational Context:
  - Actor:cut 之後才開的新 slug 寫手
  - Goal:中間不等例行閘
  - Situation:三前置全真
  - Known information:謂詞跳過（DD-2）
  - Missing information:owner 會否口頭要求仍停 G1
  - Human decision:中間不簽；Ship 仍簽
  - Authority:coordinator 禁問要不要繼續
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:中間不停；Ship 仍 HumanWait
  - Recovery:任一前置假改走 S-6.1
  - Audit/handoff requirement:hop 紀錄可指到三前置
  - Observation:見本條觀測

#### S-3.2 NEW5-WAIT-RED：注入謂詞真仍停 N7-g1 → 該格紅
- GIVEN 電池 CASE NEW5-WAIT-RED；三前置全真；latch 假
- WHEN **注入**「仍例行進入 `N7-g1` 或留下要不要繼續／請人審」
- THEN **該格獨立變紅**。合法行為是立刻 hop（綠格義務，見 S-3.1），不是本紅格
- 觀測:從該 CASE 獨立紅標看 | 注入等人紅；合法 hop 不得當此格綠算過 | Decision SC-NEW5-WAIT-RED
- Operational Context:不適用 — 測法極性。

#### S-3.3 GRAPH-WORD-NE：只改用字、新 slug 仍停 N7-g1、卻標成功 → 該格紅
- GIVEN guide 已改寫「五站」或 STATUS 用語已切；Stage 2 graph 仍預設進 `N7-g1`；SoT 或三前置未讓新 slug 跳過例行停
- WHEN 有人標 F3 成功
- THEN **該格獨立變紅**。用語與行為分開記帳；只改用字 ≠ 成功
- 觀測:從 guide 用字 + 新 slug 是否仍進 `N7-g1` + 該 CASE 紅標看 | 用字切、行為沒切、標成功＝紅算過 | Decision SC-GRAPH-WORD-NE；guide L573
- Operational Context:不適用 — 測法極性。

#### S-3.4 節點 N7-g1／N6-g2 不刪
- GIVEN `skills/dev-flow/stage2/graph.yaml` 與 `skills/dev-flow/stage4/graph.yaml`
- WHEN 後站落地 graph 謂詞跳過
- THEN 兩檔仍有鍵 `N7-g1` 與 `N6-g2`（含 `file:` 指向既有 node）。刪鍵或刪 `nodes/N7-g1.md`／`nodes/N6-g2.md`＝本條紅。in-flight 與未宣告 2.1.0 仍走這兩節點
- 觀測:從兩份 `graph.yaml` 鍵名 + node 檔是否存在看 | 鍵在、檔在算過 | Decision 約束 7；brief §6 舊機械不刪
- Operational Context:不適用 — 節點留存。

#### S-3.5 dual-read：未宣告 2.1.0＝舊 7
- GIVEN `contract_version()` 不以 `2.1` 開頭；slug 無 1–7 `.md`（非 in-flight）
- WHEN 求預設路線
- THEN 舊 7；進入 `N7-g1`／`N6-g2` 例行停。graph 謂詞跳過不得在未宣告時生效
- 觀測:從路線判定 + 是否進入 `N7-g1` 看 | 未宣告＝舊 7 算過 | Decision 3C；annex SLOT-UNDECLARED-ROUTE
- Operational Context:不適用 — dual-read 閘。

### R-4: 系統 SHALL 只把 `2.1.0` 加入 supported 清單，且 doctor 綠不得當路條

4A。不改 `hooks/_doctor_impl.py` 握手語意。漏加 → 誠實 INCOMPATIBLE。`COMPATIBLE`／exit 0 只證明握手。marketplace／cache 不是第四條前置。出貨態故意 doctor 紅不是目標。

**審的時候看什麼**
doctor 實作有沒有被改。綠有沒有被寫成 ticket。漏清單會不會被放寬成綠。

#### S-4.1 DOCTOR-HONEST：2.1.0 ∉ supported → INCOMPATIBLE
- GIVEN 契約 `devflow_contract_version=2.1.0`；`hooks/runtime-capabilities.json` 的 `supported_contract_versions` 仍只有 `2.0.0`
- WHEN 跑 doctor（`devflow-doctor.sh` 或同等 `_doctor_impl.py` 入口）
- THEN 印 `INCOMPATIBLE`；exit ≠ 0。不得為了升級好看改握手讓它仍 `COMPATIBLE`
- 觀測:從 doctor stdout／exit 看 | 誠實紅算過 | n-a:本 hop 不 bump。替代：Decision SC-DOCTOR-HONEST；`_doctor_impl.py` L193-L202
- Operational Context:
  - Actor:doctor 操作者
  - Goal:看見握手紅／綠
  - Situation:契約已 bump、清單未加
  - Known information:綠＝版本 ∈ supported
  - Missing information:人會否以為「更新壞了」
  - Human decision:同刀把 `2.1.0` 寫進 supported；不改握手
  - Authority:禁放寬握手
  - External dependency:無
  - Out-of-system action:跑 doctor
  - Waiting/timeout behavior:紅則停在握手，不是切線
  - Recovery:加清單後重跑
  - Audit/handoff requirement:INCOMPATIBLE 一行留下
  - Observation:見本條觀測

#### S-4.2 DOCTOR-NE-TICKET：COMPATIBLE 不是五站 hop 通行證
- GIVEN 本 tree 現況：契約 `2.0.0`；doctor 可印 `COMPATIBLE` 且 exit 0；cut 假
- WHEN 求五站 hop
- THEN 拒；理由含「路線未宣告」或「仍舊 7」或「F3 cut 未發生」；理由不含「doctor 已綠所以可 hop」
- 觀測:從該次 hop 拒絕理由看 | 理由是路線、不是 doctor 綠算過 | 現況可測：契約 2.0.0 + doctor 可綠 + `f3_cut_happened` False
- Operational Context:不適用 — 現況約束；與 F2 S-3.1 同形。

#### S-4.3 marketplace／cache 不是第四條前置
- GIVEN 三前置為：宣告 2.1.0 ∧ ¬in-flight ∧ cut 已發生
- WHEN 有人只證明 marketplace update 或 plugin cache 已有五站 hops 碼
- THEN 仍 `allow_legacy()`；update／cache 不是第四條，也不是 cut
- 觀測:從路線閘輸入看 | 缺任一前置仍舊 7；cache 位址不構成放行算過 | Decision 約束 8；F2 S-3.2／S-3.6
- Operational Context:不適用 — 前置清單。

#### S-4.4 不改 `_doctor_impl.py` 握手語意
- GIVEN 後站 Files 聯集
- WHEN `git diff --name-only` 出現 `hooks/_doctor_impl.py`，且 diff 改「版本必須 ∈ supported」或綠印 `COMPATIBLE` 的語意
- THEN 本條紅。只准改 `supported_contract_versions` 清單（`hooks/runtime-capabilities.json`）
- 觀測:從後站 diff 檔名 + `_doctor_impl.py` 握手句是否被改看 | 握手句被改＝本條紅算過 | Decision OC-6；F2 Out #12
- Operational Context:不適用 — Files 禁令。

### R-5: 系統 SHALL 用同一電池跑 NEW5＋OLD7＋TOKEN，且 hollow／注入壞行為該格紅

5A。單一入口＝`scripts/test-five-station-f3.sh`（DD-3）。缺一路、跳過一路、只轉呼叫 `scripts/test-five-station-f2.sh` → 非 0。F2 綠是地板（S-5.9），不是 IFF 第四路。不發明活五站名字。

**審的時候看什麼**
入口是不是一支。hollow 三格能不能獨立紅。F2 綠有沒有被寫進 IFF。

#### S-5.1 單一入口；缺一路即非 0（SC-BATTERY）
- GIVEN 入口檔為 `scripts/test-five-station-f3.sh`（DD-3）；NEW5 組、OLD7 組、TOKEN 組皆已實作
- WHEN (a) 三組都過；(b) 只跑 NEW5；(c) 只跑 OLD7；(d) 只跑 TOKEN；(e) 入口只 exec `scripts/test-five-station-f2.sh`
- THEN (a) exit 0；(b)(c)(d)(e) 皆非 0。兩支互不認識的腳本各綠一次 ≠ 同一電池
- 觀測:從該入口原始 stdout／exit 看 | 五格對上表算過 | n-a:入口未落地。替代：Decision SC-BATTERY 字面；DD-3
- Operational Context:不適用 — 電池入口。

#### S-5.2 NEW5-CUT-OK 綠格掛電池
- GIVEN NEW5 合成 fixture（DD-4）；三前置全真；S-3.1 條件成立
- WHEN 電池跑 NEW5-CUT-OK
- THEN 此格綠（合法行為：預設五站、不等例行 G1／G2）
- 觀測:從該 CASE 綠標 + S-3.1 同條件看 | 此格綠算過 | n-a:電池未落地。替代：Decision SC-NEW5-CUT-OK
- Operational Context:見 S-3.1。

#### S-5.3 紅格極性：注入壞行為該格紅，拒 hop 不得當紅格綠
- GIVEN 本檔 CASE 表所有標「→ 紅」的列
- WHEN 電池跑那些列
- THEN 測法＝注入該壞行為，該格獨立紅。把「coordinator 拒 hop／拒寫」記成該紅格綠＝整電池非 0
- 觀測:從各紅格測法註記看 | 極性＝注入壞行為；拒 hop 當綠＝本條紅算過 | Decision 約束 16
- Operational Context:不適用 — 測法極性。

#### S-5.4 TOKEN-KEEP 綠
- GIVEN 本 tree token 檔與 `scripts/check-gate-tokens.sh`
- WHEN 電池跑 TOKEN-KEEP（或同等呼叫該腳本）
- THEN exit 0；G1／G2／`ACCEPTED` 字面與檔仍在；此格綠
- 觀測:從 `scripts/check-gate-tokens.sh` 原始 exit／stdout 看 | 綠且 token 字面在算過 | 現況牙可跑
- Operational Context:不適用 — 回歸。

#### S-5.5 TOKEN-DEL-RED：注入刪 token 卻標 F3 成功 → 該格紅
- GIVEN 對照物為「刪 G1 或 G2 或 `ACCEPTED` token 或檔，並標 F3 成功」
- WHEN **注入**該壞行為
- THEN **該格獨立變紅**
- 觀測:從該 CASE 紅標看 | 注入刪 token 紅算過 | Decision SC-TOKEN-DEL-RED
- Operational Context:不適用 — 測法極性。

#### S-5.6 HOLLOW-TRUE：注入把函式真標成 F3 綠 → 該格紅
- GIVEN 對照物為「僅 `f3_cut_happened()==True`，三路電池未全過，卻標 F3 綠」
- WHEN **注入**該標法
- THEN **該格獨立變紅**。整電池非 0
- 觀測:從該 CASE 紅標 + 入口 exit 看 | 函式真冒充完＝紅算過 | Decision SC-HOLLOW (a)
- Operational Context:不適用 — hollow。

#### S-5.7 HOLLOW-FILES：注入把檔在標成 F3 綠 → 該格紅
- GIVEN 對照物為「僅證明 `scripts/test-five-station-f3.sh` 或 SoT 檔存在，三路未全過，卻標 F3 綠」
- WHEN **注入**該標法
- THEN **該格獨立變紅**
- 觀測:從該 CASE 紅標看 | 檔在冒充完＝紅算過 | Decision SC-HOLLOW (b)；F2 D-1 同形
- Operational Context:不適用 — hollow。

#### S-5.8 HOLLOW-F2：注入只跑 F2 電池綠就標 F3 綠 → 該格紅
- GIVEN 對照物為「只跑 `scripts/test-five-station-f2.sh` 得 exit 0，未跑 F3 三路，卻標 F3 綠」
- WHEN **注入**該標法
- THEN **該格獨立變紅**。F2 綠只准掛 F3-F2-REGRESS 地板，不得寫進 SC-BATTERY IFF
- 觀測:從該 CASE 紅標 + SC-BATTERY IFF 是否含 F2 腳本看 | 只 F2 綠冒充完＝紅；IFF 含 F2＝本條紅算過 | Decision SC-HOLLOW (c)；約束 10／11
- Operational Context:不適用 — hollow。

#### S-5.9 F3-F2-REGRESS 地板綠
- GIVEN `scripts/test-five-station-f2.sh` 在
- WHEN 跑該腳本
- THEN exit 0、`failed=0`。此格綠＝地板。單獨綠 ≠ F3 完
- 觀測:從該腳本原始 stdout／exit 看 | exit 0 且 `failed=0` 算過 | 本 hop 可跑現況電池（地板，≠ F3 完）
- Operational Context:不適用 — 回歸地板。

### R-6: 系統 SHALL 繼承三前置 AND，且 live slug（含本目錄）不建五站機

繼承 F2 4A／S-7.1：宣告 2.1.0 ∧ ¬in-flight ∧ cut。缺一 → `allow_legacy()`。in-flight＝1–7 任一 `.md`（僅 html 不算）。NEW5 試體＝合成或 cut 之後才開；不是本目錄、不是 `five-station-f2`、不是 `five-station-simplify`。不發明活五站名字。

**審的時候看什麼**
本目錄有沒有被當成 NEW5。缺一條前置會不會仍建五站機。

#### S-6.1 PRE-AND：三前置缺一 → allow_legacy
- GIVEN 缺「契約已宣告 2.1.0」或「非 in-flight」或「F3 cut 已發生（SoT 三槽滿）」任一
- WHEN coordinator 評是否建五站機
- THEN `allow_legacy()`；不建五站機；不套三 cap
- 觀測:從路線閘輸出看 | 缺一條＝舊 7 算過 | Decision SC-PRE-AND；F2 S-7.1
- Operational Context:不適用 — 前置閘。

#### S-6.2 OLD7-FREEZE 綠
- GIVEN OLD7 fixture 在 `scripts/fixtures/five-station-f3/old7/`（DD-5）已有 1–7 任一 `.md`；或 live 目錄 `docs/dev/five-station-f3/`／`five-station-f2/`／`five-station-simplify/`
- WHEN 電池跑 OLD7-FREEZE 或對該目錄求切五站
- THEN 整段舊 7；無五站狀態寫入；三 cap 不套；可走既有 T 上限 4；此格綠
- 觀測:從該目錄檔名 + 是否出現五站機寫入看 | 舊 7、無五站寫入算過 | Decision SC-OLD7-FREEZE；F1 SLOT-IN-FLIGHT-DETECT
- Operational Context:不適用 — freeze。

#### S-6.3 OLD7-FOLD-RED：注入對 in-flight 寫五站 → 該格紅
- GIVEN in-flight fixture（已有 1–7 `.md`）
- WHEN **注入**「對該目錄寫五站狀態或五站 hop」
- THEN **該格獨立變紅**
- 觀測:從該 CASE 紅標 + 目錄是否被寫入五站狀態看 | 注入折線紅算過 | Decision SC-OLD7-FOLD-RED
- Operational Context:不適用 — 測法極性。

#### S-6.4 SELF-OLD7：對本目錄／F2／simplify 求五站自動前進跳不過
- GIVEN `docs/dev/five-station-f3/` 已有 `1-discussion.md`／`2-decision.md`／`3-prototype.md`（本 hop 再加 `4-spec.md` 仍 in-flight）；`docs/dev/five-station-f2/` 與 `docs/dev/five-station-simplify/` 已有 1–7 `.md`
- WHEN 對這三個目錄要求五站自動前進
- THEN 被拒；目錄仍是舊 7 站檔；無五站機寫入
- 觀測:從對三目錄的 hop 拒絕 + `ls` 站檔看 | 有舊 7 檔、無五站機寫入算過 | Decision SC-SELF-OLD7；本 hop 落 4-spec 後仍 in-flight
- Operational Context:
  - Actor:本 slug 執行者
  - Goal:走完手上舊 7
  - Situation:目錄已有 1–7 `.md`
  - Known information:SLOT-IN-FLIGHT-DETECT
  - Missing information:後站會否把自己當白老鼠
  - Human decision:不准對這三目錄建五站機
  - Authority:coordinator 禁寫五站狀態
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:仍走舊 7 例行閘
  - Recovery:另開 cut 之後才存在的 slug
  - Audit/handoff requirement:拒絕理由含 in-flight
  - Observation:見本條觀測

#### S-6.5 NEW5 試體不是三個 live 目錄；不發明活五站名字
- GIVEN NEW5 試體路徑（DD-4）
- WHEN 電池選 hop 主詞
- THEN 路徑不是 `docs/dev/five-station-f3/`，不是 `docs/dev/five-station-f2/`，不是 `docs/dev/five-station-simplify/`。本檔與 5-tasks 不發明第一隻活五站 slug 名
- 觀測:從電池 fixture 路徑 + 本檔／5-tasks 是否出現活五站新 slug 名看 | 三 live 目錄不當 NEW5；無名算過 | Decision OC-9；約束 12
- Operational Context:不適用 — 試體選址。

### R-7: 系統 SHALL 在 cut 之後仍守 Must-keep 與三失敗，不得用「已經 cut 了」省略

摺的是新 slug 例行停點，不是完整度。Must-keep 去向繼承 F2 已核 M1–M16 表，本刀不重開、不另發 ID。三種失敗各自可紅。

**審的時候看什麼**
「已經 cut 了」有沒有被拿來省 M 或省 Ship 人簽。

#### S-7.1 KEEP-MK-RED：注入 Must-keep 紅仍 hop → 該格紅
- GIVEN NEW5；三前置全真；M1–M16 **任一**紅（例：M3 某 S 缺觀測欄；M5 代填 `ACCEPTED`；M9 Files 超出聯集；M11 T 缺 Verify；M12 reviewer＝implementer；M15 token 被刪）
- WHEN **注入**「該 M 紅仍 hop」
- THEN **該格獨立變紅**。不得用「已經 cut 了」省略。只擋 M11、其餘 M 紅仍 hop＝本條紅
- 觀測:從該 CASE 紅標 + 拒絕理由是否含該 M 看 | 注入仍 hop＝紅算過 | Decision SC-KEEP；F2 S-6.5
- Operational Context:
  - Actor:寫手／coordinator
  - Goal:完整度留下
  - Situation:有人想用 cut 省 Must-keep
  - Known information:F2 M1–M16 表仍在
  - Missing information:無
  - Human decision:補該 M，不口頭 hop
  - Authority:coordinator 禁 hop
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:停該站修
  - Recovery:該 M 綠後重評
  - Audit/handoff requirement:拒絕理由留下 M 編號
  - Observation:見本條觀測

#### S-7.2 KEEP-SHIP-MECH：注入機械綠無人 PASS 卻 Done → 該格紅
- GIVEN NEW5 已有 `7-review.md`；機械項全綠；頂欄 `verdict:` 空白
- WHEN **注入**「標 Ship Done／狀態 Done」
- THEN **該格獨立變紅**。合法行為是 HumanWait。不得用「已經 cut 了」自動 Done
- 觀測:從該 CASE 紅標 + 狀態不是 Done 看 | 注入 Done 紅算過 | Decision SC-KEEP；F0 狀態機 Ship 唯人
- Operational Context:
  - Actor:Ship 審查者
  - Goal:出貨仍由人寫頂欄
  - Situation:機械全綠
  - Known information:Ship 無自動前進
  - Missing information:無
  - Human decision:親寫 `verdict: PASS` 才 Done
  - Authority:Agent 禁代填 PASS
  - External dependency:無
  - Out-of-system action:人審頁提交判定
  - Waiting/timeout behavior:停 HumanWait，無逾時自動 Done
  - Recovery:人寫 PASS 後才 Done
  - Audit/handoff requirement:頂欄 `verdict:`
  - Observation:見本條觀測

#### S-7.3 謂詞真 latch 假仍等人＝NEW5-WAIT-RED，不得因 cut 變綠
- GIVEN 三失敗清單：(1) 謂詞真 latch 假仍等人；(2) Must-keep 紅仍 hop；(3) 機械綠無人 PASS 卻 Done
- WHEN 有人標 F3 成功且其中任一被標綠
- THEN 整電池非 0。本條與 S-3.2／S-7.1／S-7.2 同鎖，不另開例外
- 觀測:從三格是否能各自紅看 | 三條都能紅、不能因 cut 互抵銷算過 | Decision 約束 14；1-discussion AC-10
- Operational Context:不適用 — 三格索引。

### R-8: 系統 SHALL 鎖死 Non-Goals 與 Stage 5 Files 准許清單，且本 hop 只交 draft 雙檔

6A。三把鎖 + 不重開 F2 park。後站 Files 超出准許清單 → L2。本 hop 只 `4-spec.md` + `4-spec.html`；`status: draft`；`verdict` 空；無 G2 PASS；無 STATUS。

**審的時候看什麼**
diff 是不是只有這兩檔。頂欄有沒有被寫成 PASS。Files 清單有沒有把 STATUS／刪 token／刪 graph 節點放進去。

#### S-8.1 Non-Goals 後站不准改成 In
- GIVEN 本檔 Out of Scope 全列
- WHEN 後站 5-tasks／6-notes 把下列任一標成 In／可選：刪 token；折 in-flight；本 slug 當白老鼠；silent True 當 cut；2.1.0 當 cut；doctor 綠當 ticket；只改用字當完；刪 `N7-g1`／`N6-g2`；炸模板全文；重開 F2 park D-1／D-2／D-3／F-c-4；重開 4A 形狀；F2 綠當 SC-BATTERY 第四路
- THEN 本條紅
- 觀測:從後站 Scope／Files 是否把上列改成 In 看 | 改成 In＝本條紅算過 | Decision Out 1–16
- Operational Context:不適用 — 範圍鎖。

#### S-8.2 Stage 5 Files 准許清單
- GIVEN 後站 5-tasks Files 聯集
- WHEN 列 Files 並跑 `git diff --name-only`
- THEN 只准下列路徑：`notes/design/five-station-cut-attest.md`；`scripts/five_station_f2.py`（只改 `f3_cut_happened` 讀端 + `contract_version` 只讀正本鍵）；`scripts/test-five-station-f3.sh`；`scripts/fixtures/five-station-f3/**`；`devflow-contract.json`（只 bump `devflow_contract_version` 到 `2.1.0`，不新增 cut 兄弟鍵）；`hooks/runtime-capabilities.json`（只把 `2.1.0` 加入 `supported_contract_versions`）；`guides/guide-dev-flow.html`（七站單行改五站用語）；`skills/dev-flow/stage2/graph.yaml` 與 `skills/dev-flow/stage4/graph.yaml`（只加謂詞跳過，不刪 `N7-g1`／`N6-g2` 鍵與 node 檔）；本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html。超出 → 本條紅
- 觀測:從 5-tasks Files 聯集 + 後站 `git diff --name-only` 看 | 超出准許清單＝本條紅算過 | n-a:5-tasks 尚未寫。替代：本檔 Diff Budget 與 Out of Scope
- Operational Context:
  - Actor:Stage 5 寫手
  - Goal:cut 落地不漏刀、不偷刀
  - Situation:G2 之後才準寫碼
  - Known information:本條清單
  - Missing information:無
  - Human decision:超出先停、判 L1／L2
  - Authority:禁默加 STATUS／doctor 實作／模板全文
  - External dependency:無
  - Out-of-system action:無
  - Waiting/timeout behavior:超出則停
  - Recovery:把禁改檔從 Files 刪掉
  - Audit/handoff requirement:5-tasks Files
  - Observation:見本條觀測

#### S-8.3 本 feature branch 不碰 STATUS 正本；用語切走 companion
- GIVEN 母版 STATUS 只在整合分支維護
- WHEN 本 slug 任一 feature branch（含本 hop）的 `git diff --name-only` 含 `docs/dev/STATUS.md` 或 `docs/dev/HISTORY.md`
- THEN 本條紅。guide 用語切在 `guides/guide-dev-flow.html`。STATUS 用語切由合併後 companion 做
- 觀測:從該 branch diff 檔名看 | 出現 STATUS／HISTORY＝本條紅算過 | Decision OC-2／OC-10；`docs/dev/STATUS.md` L10-L13
- Operational Context:不適用 — 看板政策。

#### S-8.4 本 hop 只交 draft 雙檔；不發明 G2 PASS
- GIVEN 本 PR 對 `origin/main` 的 diff
- WHEN 跑 `git diff --name-only origin/main`
- THEN 只含 `docs/dev/five-station-f3/4-spec.md` 與 `docs/dev/five-station-f3/4-spec.html`。頂欄 `status: draft`；`verdict` 空（或未填）。無 G2 PASS。無 STATUS／HISTORY／2-decision／3-prototype／模板／graph／doctor／契約／coordinator
- 觀測:從本 PR `git diff --name-only origin/main` + 本檔 frontmatter 看 | 兩檔、draft、verdict 空算過 | 本 hop 檔集；Decision 約束 17 的 Stage 4 對應
- Operational Context:不適用 — 本 hop 檔集。

#### S-8.5 Stage 3 對帳＝N/A（0 命中）；Owner ACCEPTED N/A
- GIVEN `3-prototype.md` 九條全未勾；Demo verdict = N/A；Owner ACCEPTED Stage3 N/A（無 trigger、無 Demo）
- WHEN 人讀本檔 Stage 3 對帳與 G2 Demo 條件
- THEN Demo 條件＝N/A + 原因（0／9）。不是 skip-OC。不是 Human ACCEPTED 一場可點 Demo。不得把 N/A 改寫成 ACCEPTED，也不得為湊 Stage 3 發明可點原型
- 觀測:從 `3-prototype.md` 勾選列 + 本檔 Stage 3 對帳節 + `_stage3_impl.py` 0-hit 支路看 | 0／9、Demo N/A、無 ACCEPTED attestation 算過 | `3-prototype.md` L19-L32；owner 本 hop「ACCEPTED Stage3 N/A」
- Operational Context:不適用 — 對帳；無 Demo 可走。

#### S-8.6 Q15–Q27 皆有去向，不得標可選
- GIVEN 本檔 Real-world Disposition
- WHEN 人對 Q15／Q16／Q17／Q18／Q19／Q20／Q21／Q22／Q23／Q24／Q25／Q26／Q27
- THEN 每條去向 ∈ {本方案處理, 刻意維持}；下落至少一條 R-／S- 或 Out of Scope。不得把 Q15／Q16／Q17／Q19／Q21 標可選
- 觀測:從本檔 Disposition 表列看 | 上列 Q 皆有去向與下落算過 | Decision SC-Q-CARRY
- Operational Context:不適用 — 去向帳。

#### S-8.7 不重開 F2 park D-1／D-2／D-3／F-c-4
- GIVEN F2 7-review 已 park D-1／D-2／D-3／F-c-4
- WHEN 本檔 R／S／DD／5-tasks 把其中一項重開為本刀 In
- THEN 本條紅
- 觀測:從本檔 Out of Scope 第 1 條 + 後站 Scope 看 | 重開＝本條紅算過 | Decision Out #1；6A 抬高句
- Operational Context:不適用 — 繼承鎖。

## MODIFIED Requirements

本 repo `docs/specs/` 無 living spec 條文可引。F2 已核契約本刀**不改其 SHALL 原文**；只把 F2 明文交給 F3 的縫接上：

| 縫 | F2 原文要點 | 本刀怎麼接 | 本檔 S |
|---|---|---|---|
| `f3_cut_happened` 恒 False | F2 never cuts | 改讀 DD-1 SoT；缺／空仍假 | R-1、S-1.3 |
| `contract_version()` 讀錯鍵 | 回 `""` | 只讀正本鍵 | S-2.1、S-2.2 |
| 三前置 4A | 2.1.0 ∧ ¬in-flight ∧ cut；2.1.0 ≠ cut | 繼承；不重開 | S-2.3、S-6.1 |
| doctor 綠 ≠ hop | 不改握手 | 只加 supported 清單 | R-4 |
| F3 cut 在 F2 為 Out | 後站不准改成 In **當時** | 本刀把 cut 改成 In；F2 三把鎖其餘仍鎖 | R-3、R-8 |
| 本 slug 舊 7 | 五站 hop 跳不過 | 對本目錄建五站機仍拒 | S-6.4 |

故本節無「改寫已刊 living 條文」列。

## REMOVED Requirements

無。不刪 F2 完成樹、不刪 token、不刪 `N7-g1`／`N6-g2`、不刪 doctor 握手。

## 行為流程圖(R 級)

```
[R-1] 可見紀錄為 SoT 函式只讀
  誰／何時／哪個條件
  silent True 該格紅
[R-2] 只讀正本鍵 2.1.0 非 cut
  錯鍵 bump 非宣告
  hops 不得早於宣告
[R-3] graph 行為加 dual-read
  新 slug 不再停 N7-g1
  節點不刪
[R-4] doctor 只加清單
  綠不是 ticket
  漏清單誠實紅
[R-5] 同一電池三路
  缺一路整電池非 0
  hollow 該格紅
[R-6] 三前置 AND
  缺一條 allow_legacy
  本目錄跳不過
[R-7] Must-keep 與三失敗仍在
  已 cut 不得省略
  注入壞行為該格紅
[R-8] Non-Goals 與 Files 清單
  後站不准改成 In
  本 hop 只 draft 雙檔
```

## Acceptance Criteria

- 全部 S 綠（S-1.1～S-8.7）。本 hop 能綠的是形狀與對照：`check-spec-gate.sh`、本 PR 檔集、本目錄 freeze md、doctor 握手現況、Disposition／CASE／Stage 3 N/A。F3 行為 S 的綠發生在後站落地之後，不在本 PR。S 數見確認紀錄；>40 誠實記帳，不另切開新 slug。
- 既有測試全綠：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`；`python3 scripts/build-stage4-html.py --action docs/dev/five-station-f3/4-spec.md` 後審頁可解析 R/S。本 hop 禁改 `scripts/` 牙。F2 電池地板可跑，≠ F3 完。
- 非功能：本 slug 自己仍走舊 7。本 hop 不 bump 契約、不改 graph、不送 G2。
- 無 golden master（可見路線行為在後站才變；本 hop 不改 runtime）。

### Stage 3 對帳

N/A。`3-prototype.md` 九條全未勾（0／9）。Demo verdict = **N/A** + 各條原因。Owner ACCEPTED Stage3 N/A（本 hop 派工；無 trigger、無 Demo）。

不是「命中仍跳過」的 skip OC。`2-decision.md` 內部技術選擇「不預先跳過 Stage 3；觸發判定留給該站」——該站已判定 0 命中。`_stage3_impl.py` 走 0-hit N/A 支路，`g2_demo=PASS` 指 Demo 條件可過，**不是** G2 PASS。

九條對本刀（cut／契約鍵／graph 謂詞跳過／doctor 清單／三路電池）：新前端流程否；改變下一步否（3C observable 已鎖，simplify D1 已走）；角色交接否；人工核准否（不新增閘）；等待退回逾時否（摺例行停，不新設計等待面）；權限差異否；系統外動作否（marketplace／doctor 語意已鎖）；多種互動設計否（1A–6A 已 lock；OPEN 是檔名／機制形）；操作流程不確定否。

無 ACCEPTED Demo 場景要掛 R/S。反事實紙卡不是 Demo，不掛 S。Human verdict 在 `3-prototype.md` 留 `NOT_REVIEWED`（人未裁觸發表）；Agent 不代填 ACCEPTED。G2 Demo 條件＝N/A＋本段原因。

## Out of Scope

鎖死，後站不准改成 In：

1. **不重開 F2 park D-1／D-2／D-3／F-c-4。**
2. **刪 G1／G2／`ACCEPTED` token 或檔。**
3. **把 in-flight 折成五站**（含本目錄、含 `five-station-f2`、含 `five-station-simplify`、含任何已有 1–7 `.md` 的 slug）。
4. **拿本 slug 當活五站白老鼠**；發明第一隻活五站名字。
5. **silent `True` 當 cut**；把 `f3_cut_happened==True` 當 F3 完。
6. **2.1.0 當 cut**；重開 4A 三前置形狀。
7. **doctor 綠／marketplace update／plugin cache 當 cut 或路條**；出貨態故意 doctor 紅當目標。
8. **只改 guide／STATUS 用字當 F3 完**；本 PR／本 feature branch 改 STATUS 正本表列。
9. **只改 graph、不宣告 2.1.0**；**只宣告 dual-read、新 slug 仍停 `N7-g1`**；**只翻 coordinator 留例行停點。**
10. **刪 `N7-g1`／`N6-g2` 節點**；一次大爆炸改模板全文。
11. 放寬 hop≤2／Decide≤1／Goal reopen≤1；重開 F0 十條。
12. 把「檔在」或「F2 綠」當 F3 完成；把 F2 綠寫成 SC-BATTERY 第四條 IFF。
13. 本 PR 實作 cut／改 `graph.yaml`／bump 契約／改 doctor／改 coordinator、填 G2 PASS、改 STATUS／HISTORY。
14. 把 cut 鎖成與版本同檔的兄弟布林；用 git blame 當 who／when。
15. 改已經 freeze 的 slug 的路線。
16. fallback／dual-read 錯鍵當 `contract_version()` 正讀；錯鍵 bump 當已宣告。
17. 本 hop 改 `2-decision.md`／`3-prototype.md` 頂欄或 OC／Human verdict。

## Diff Budget

整節是估計，不是承諾。[Assumption]。超支本身非偏差，是停下判 L1/L2 的訊號。

**本 Stage 4 hop（立即、本 PR）= 只文件**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| 本 hop 規格 md | 1 | ≤1,200 | `docs/dev/five-station-f3/4-spec.md` |
| 本 hop 審頁 html | 1 | 產器產出 | `4-spec.html`；不手包 |
| `_templates/`／`graph.yaml`／`scripts/`／STATUS／HISTORY／契約／2-decision／3-prototype | 0 | 0 | 本 hop＝0；出現＝S-8.4 紅 |

**G2 之後、本 slug Stage 5–7（只准 S-8.2 清單）**

| 區塊 | 檔 | 行（估） | 註 |
|---|---|---|---|
| `notes/design/five-station-cut-attest.md` | 1 | ≤40 | SoT；三槽 |
| `scripts/five_station_f2.py` 讀端 | 1 | ≤80 | 只改兩個函式 |
| `scripts/test-five-station-f3.sh` | 1 | ≤250 | 單一電池入口 |
| `scripts/fixtures/five-station-f3/new5/` + `old7/` | ≤12 | ≤400 | 合成 NEW5 + OLD7 |
| 電池／CASE 測試（與非測試分開） | ≤6 | ≤900（測試） | 突變另加係數 |
| `devflow-contract.json` bump | 1 | ≤4 | 只改正本鍵到 2.1.0 |
| `hooks/runtime-capabilities.json` | 1 | ≤4 | 只加 `2.1.0` |
| `guides/guide-dev-flow.html` 用語 | 1 | ≤20 | 七站單行 → 五站 |
| stage2／stage4 `graph.yaml` 謂詞跳過 | 2 | ≤40 | 不刪節點 |
| `_templates/` 全文 | 0 | 0 | ＝0，否則 S-8.1 紅 |
| `_doctor_impl.py` 握手 | 0 | 0 | ＝0，否則 S-4.4 紅 |
| 刪 token／刪 `N7-g1`／`N6-g2` | 0 | 0 | ＝0，否則 S-3.4／S-5.5 紅 |
| STATUS／HISTORY | 0 | 0 | 看板另 companion |

Stage 5 Files 准許清單正本＝S-8.2。超出 → L2。

## Dependencies

| 依賴 | justification |
|---|---|
| F0 brief＋狀態機 | cut／freeze／舊機械四條連讀；本檔不重開十條與三 cap |
| F1 teeth＋annex | SLOT-REJECT／DOCTOR-GREEN／IN-FLIGHT-DETECT 回歸地板 |
| F2 coordinator＋4A | 三前置形狀與 `allow_legacy`／拒絕理由；F2 綠是地板 |
| `scripts/check-spec-gate.sh` | 本 hop 形狀閘 |
| `scripts/build-stage4-html.py` | 本 hop 審頁 |
| `scripts/check-gate-tokens.sh` | TOKEN-KEEP |
| `scripts/test-five-station-f2.sh` | F3-F2-REGRESS 地板；**不是** F3 完成入口 |
| 現行 doctor／契約 2.0.0 | SC-DOCTOR-NE-TICKET 現況可測；本 hop 不改 |
| `3-prototype.md` 0／9 | Stage 3 對帳 N/A |

無新外部服務。SoT 是本 repo markdown，不是新 SaaS。

## Design Boundary Contract

- Applicability: applicable
- Trigger(s): ②公開契約鍵 `devflow_contract_version` 變更／③跨模組 Interface（coordinator 讀端 × graph 下一跳）／⑧filesystem（SoT 檔）／⑨Feature Risk = high／⑪狀態機（新 slug 預設路 vs in-flight 舊 7）
- Design source: Decision 1A／2A／3C／4A／5A／6A；F1 annex；F2 4-spec 路線閘；new local design＝SoT 路徑與謂詞跳過形（DD-1／DD-2）

### Architecture Boundaries

| Boundary / Module | Responsibility | Data owner | Allowed dependencies | Forbidden dependencies |
|---|---|---|---|---|
| cut SoT 檔 | 誰／何時／哪個條件 | 母版 owner 人類寫入 | `f3_cut_happened` 只讀 | `devflow-contract.json` 兄弟布林；git blame；STATUS；chat |
| 讀鍵 | `declared` 布林 | 專案樹 `devflow_contract_version` | 只讀正本鍵 | `version`／`contract_version` fallback |
| 路線閘 | 三前置 → 五站或 `allow_legacy()` | 專案樹契約 + 該 slug 是否已有 1–7 `.md` + SoT | F2 coordinator | doctor 綠；marketplace；cache |
| graph 節點 | 例行停點留下給 freeze／未宣告 | 既有 graph owner | 謂詞跳過（DD-2） | 刪 `N7-g1`／`N6-g2` |
| doctor | 握手 | plugin `supported_contract_versions` | 只加清單 | 改握手語意；綠當路條 |
| F3 電池 | NEW5+OLD7+TOKEN 同一 process | 合成 fixture | F2 電池當地板 | 本目錄當 NEW5；只轉呼叫 F2 腳本當完成 |

### Interface & Consistency Contract

| Interface / Flow | Input / Output | Errors | Transaction / Consistency boundary | Compatibility |
|---|---|---|---|---|
| `f3_cut_happened(root)` | SoT 三槽滿 → True；否則 False | 檔缺／空槽 → False | 只讀；不寫 SoT／契約／STATUS | F2 恒 False 是落地前地板 |
| `contract_version(root)` | 正本鍵字串或以 `2.1` 開頭 | 檔缺／壞 → `""` | 只讀正本鍵；與 cut 位元分開 | 錯鍵 bump ≠ declared |
| 路線閘 | 三前置布林 | 缺一 → allow_legacy + 具名理由 | 只讀專案樹；不寫採用端契約 | 2.0.0 握手綠仍舊 7 |
| graph 下一跳 | 三前置全真 → 跳過 `N7-g1`／`N6-g2` | 未宣告或 in-flight → 仍進節點 | 節點檔不刪 | 舊 7 in-flight 仍走既有 graph |
| 電池入口 | 無／選跑三組 | 缺一組 → 非 0 | 單一 process 內三組都跑完才 0 | F2 腳本不是入口 |

### Software Design

| Component | Responsibility | Collaborators | State / Data flow | Error handling | Test seam |
|---|---|---|---|---|---|
| SoT reader | 讀三槽 | `f3_cut_happened` | 檔 → True／False | 缺／空 → False，不丟例外冒充 True | 可換 fixture 根指到假 SoT |
| key reader | 只讀正本鍵 | 路線閘 `declared` | JSON → 字串 | 錯鍵忽略 | 三份對照樹：正本／錯鍵／缺檔 |
| hop skip | 三前置真則跳過例行停 | 路線閘、graph 節點 | 真→跳過；假→進 N7-g1／N6-g2 | 禁改問人 | 注入仍進 N7-g1 |
| battery | 22 列 CASE | NEW5／OLD7／TOKEN fixture | 紅格餵壞行為 | 極性反了 → 非 0 | 各 CASE 獨立 exit |

### Design Constraints

- 必須:可見紀錄三槽；函式只讀；只讀正本鍵；graph 行為 + dual-read；節點不刪；doctor 只加清單；同一電池三路；三前置 AND；Files 准許清單。
- 禁止:silent True；兄弟布林；blame 當槽；2.1.0＝cut；未宣告切 hops；刪閘；折 in-flight；本目錄當 NEW5；本 hop 填 G2 PASS；改 STATUS。
- Extension point:4-spec 可加 CASE 列；不得把 hollow 加成通過條件。
- Known design limit:本 hop 不落地 cut／reader／graph／契約；行為 S 的執行綠在後站。審頁產器 `steps[:8]`，本檔正好 8 個 R，不增 R-9。F3 完成樹之前現場仍舊 7（約束，不是本 hop 先切）。

## Verification Profile

- lane: full（判準:公開契約鍵變更、graph 預設 hop、採用端改線風險、Feature Risk=high。owner 指示 full；與判準相同，無偏離）
- Risk: high（判準:採用端被遠端改線、誤折 in-flight、誤刪 token、契約／路線不可逆。模板「公開 API／不可逆／資料隔離」吃這條）
- Failure model: 見下表
- Negative constraints: 見 Out of Scope 全列（後站不准改成 In）；另：reader 不得 fallback 錯鍵；紅格不得把拒 hop 當綠；本 hop 不得改 STATUS／牙／契約／graph；不得只擋 M11；F2 綠不得寫進 SC-BATTERY IFF
- Required layers: spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`）；token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F3 電池列 Required——Required 層不得 unverified
- Conditional layers: F3 cut／電池落地 → 該刀列入 Required，單一入口 `bash scripts/test-five-station-f3.sh`（NEW5+OLD7+TOKEN；缺一路即非 0）；F2 電池在落地後當回歸地板重跑（F3-F2-REGRESS）。契約／supported 被後站改動 → doctor 握手重跑。本 hop 不改那些檔、電池未落地 → 本 hop 不觸發 Conditional
- Explicitly excluded layers: UI e2e（本刀無新前端）；負荷／效能（cut 非熱路徑）；金流／auth fuzz（不涉）；本 hop 跑 cut 實作（碼 Out of Scope）
- Final fresh entry point: `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`
- Reliability triage:
  - Concurrency: n-a — 本刀不新開並發寫倉；SoT 由人類寫一次、讀端只讀；兩 process 讀同一檔不改線（不保證、也不新增寫鎖）
  - Idempotency: applicable — 重讀 SoT／正本鍵必須得到同一布林；重跑 doctor 對同一契約＋supported 必須同一握手（S-1.3、S-2.1、S-4.1）
  - Timeout/retry: applicable — Ship 無逾時自動 Done（S-7.2）；未宣告／未 cut 時無逾時改線（S-3.5、S-2.3）

### Failure Model

| Failure mode | 影響 | 可觀測訊號 | 驗證層 | 未覆蓋原因 |
|---|---|---|---|---|
| silent True 當 cut | 空切；人指不到三槽 | ATTEST-SILENT-RED 不紅 | Required:S-1.2、S-1.3 | — |
| 2.1.0 當 cut | 第三位元無法獨立為假 | PRE-210-NE-CUT 變紅或消失 | Required:S-2.3 | — |
| 只 bump 正本、reader 仍舊 | 假宣告；live 仍 legacy | READ-SEAM 不紅 | Required:S-2.2 | — |
| 2.0.0 + 五站 hops | SLOT-REJECT 或遠端改線 | PRE-HOPS-200 不紅 | Required:S-2.4 | — |
| 只改 guide 用字 | 用語切、行為沒切 | GRAPH-WORD-NE 不紅 | Required:S-3.3 | — |
| 刪 N7-g1／N6-g2 | in-flight 失去舊停點 | S-3.4 紅 | Required:S-3.4 | — |
| doctor 綠當 hop 通行證 | 舊 7 被折 | 拒絕理由含「doctor 已綠」 | Required:S-4.2 | — |
| 放寬握手以免紅 | 隱瞞 supported 沒跟上 | DOCTOR-HONEST 變 COMPATIBLE | Required:S-4.1、S-4.4 | — |
| 只跑 F2 或只證明檔在 | hollow F3 | 入口仍 0 | Required:S-5.1、S-5.7、S-5.8 | — |
| 對本目錄建五站機 | 觀測白老鼠 | SELF-OLD7 跳得過 | Required:S-6.4 | — |
| 已 cut 省 Must-keep／Ship | 完整度被摺 | KEEP-MK-RED／KEEP-SHIP-MECH 不紅 | Required:S-7.1、S-7.2 | — |
| 本 hop 自填 G2 PASS | 四眼破 | 頂欄 PASS | Required:S-8.4 | — |
| feature branch 改 STATUS | 並行 session 互蓋 | diff 含 STATUS.md | Required:S-8.3 | — |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| Q15 silent flip 不合法 | stage-2 | oc-accepted |
| Q16 hops 不得早於 2.1.0 宣告 | stage-2 | oc-accepted |
| Q17 只 bump 正本仍假 | stage-2 | oc-accepted |
| Q18 漏 supported 誠實紅 | stage-2 | oc-accepted |
| Q19 同一電池三路 | stage-2 | oc-accepted |
| Q21 兩者都要、節點不刪 | stage-2 | oc-accepted |
| Q26 2.1.0 ≠ cut | stage-2 | oc-accepted |
| Q27 reader 回空字串 | stage-2 | oc-accepted |
| SoT 路徑形交 4-spec（本檔 DD-1） | 2026-12-31 | open |
| graph 謂詞跳過形交 4-spec（本檔 DD-2） | 2026-12-31 | open |
| 電池入口檔名交 4-spec（本檔 DD-3） | 2026-12-31 | open |

Q15–Q19／Q21／Q26／Q27 已由 Decision OC 升格，故 oc-accepted。後三列是本檔釘形，期限給後站落地，不是已過站。

## Drafting Decisions(草擬自判,待人審)

形狀已寫進 R/S。本表只記本檔鎖定的選擇。不翻 1A–6A。推翻 Decision 不是合法 DD。

### 逐條裁決(上層)

| DD | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| DD-1 | cut SoT 檔＝`notes/design/five-station-cut-attest.md`；frontmatter 必填 `who`／`when`／`condition`。`f3_cut_happened()` 只讀此檔。缺檔或任一槽空 → False。不鎖 `devflow-contract.json` 兄弟布林。不用 git blame 當槽 | Decision 把路徑交給 4-spec；必須人指得到且與版本分檔 | `2-decision.md` 約束 3；OC-1。路徑本身 `[Assumption]` | 改回 silent True 或同檔布林＝空切／bump＝cut | 待人審 |
| DD-2 | graph 切換＝**謂詞跳過、節點留下**。三前置全真 → 不進入 `N7-g1`／`N6-g2`；否則仍進。不另建第二份 graph、不刪節點鍵 | Decision 3C 鎖 observable、機制交 4-spec | `2-decision.md` OC-5；內部技術選擇 L308。機制形 `[Assumption]` | 只改 graph 或只宣告＝已拒的 3A／3B；刪節點＝6B | 待人審 |
| DD-3 | 單一電池入口檔名＝`scripts/test-five-station-f3.sh`。同一 process；NEW5+OLD7+TOKEN；缺一路即非 0。不得只轉呼叫 `test-five-station-f2.sh` | Decision 只鎖同一 process；檔名交給 4-spec | `2-decision.md` 5A；內部技術選擇 L309。檔名 `[Assumption]` | 兩支腳本各綠＝hollow | 待人審 |
| DD-4 | NEW5 fixture 根＝`scripts/fixtures/five-station-f3/new5/`（合成；cut 當下無 1–7 `.md`） | Decision 約束 12 | `2-decision.md` 約束 12。路徑 `[Assumption]` | 拿本目錄當白老鼠＝X4 | 待人審 |
| DD-5 | OLD7 fixture 根＝`scripts/fixtures/five-station-f3/old7/`（已有 1–7 `.md`）。live  freeze 樣本另含本目錄／F2／simplify | 與 NEW5 分家，供同一入口第二路 | `2-decision.md` 5A。路徑 `[Assumption]` | 與 NEW5 混目錄會折線 | 待人審 |
| DD-6 | Stage 5 Files 准許清單＝S-8.2 具名路徑。STATUS／doctor 握手／刪 token／刪 graph 節點／模板全文／契約 cut 兄弟鍵＝0 | Writer C 主軸：後站不可默加刀 | 本 hop 派工「Files allowlist」；Decision Out。清單 `[Assumption]` | 無清單則 F3 偷做或空切 | 待人審 |
| DD-7 | Feature Risk = high；本檔 `verdict` 空、`status: draft`；implementer 不寫 G2 PASS；本 hop 不改 STATUS | 採用端改線＋不可逆；四眼；看板政策 | `_templates/4-spec.md` Risk 判準；本 hop brief「No G2 invent／No STATUS」 | 改 normal 則 Failure Model 變選配；代填 PASS＝假綠 | 待人審 |
| DD-8 | Stage 3 對帳＝0 命中 N/A；Owner ACCEPTED Stage3 N/A。不是 skip-OC，不是 Human ACCEPTED Demo | Decision 無 skip OC；九條 0 命中；派工金本 | `3-prototype.md` L19-L32；本 hop「Owner ACCEPTED Stage3 N/A」 | 寫 ACCEPTED 而無 Demo＝假 hit；寫 skip 而無命中＝假跳過 | 待人審 |
| DD-9 | 原文獨立於尚未出現的 A／B Stage 4 稿。金本＝Decision B 1A+2A+3C+4A+5A+6A。不換 winner。不重開 F2 park | Writer C 派工；standing 已在 Decision | `#366`／`#368`；本 hop「Gold: G1 Decision B soft-fix」 | 改換骨架＝翻 G1 | 待人審 |
| DD-10 | S 數 >40 留在本檔、不另切開新 slug；行為圖 8 框對 8 個 R（產器 `steps[:8]`） | 誠實記帳；不改 scripts | `scripts/build-stage4-html.py` L450；本 hop 不改牙 | 增 R-9 則圖丟框 | 待人審 |

### 內部技術選擇(下層,告知即可)

- 審頁用 `scripts/build-stage4-html.py --action`；不手包 html-shell；不把審頁塞進 `build-gate-twin.py` STAGES。
- 本 hop 不改 `STATUS.md`（另 companion）、不 bump 契約、不開 5-tasks、不發明 G2 PASS。
- 本檔不寫 C4 未定事項三詞字面，改指 `check-spec-gate.sh` `VAGUE_ALL`。
- 舊 7 in-flight 仍走既有 `graph.yaml` 與 T 嘗試上限 4。
- F2 電池可留作回歸地板（F3-F2-REGRESS）；不得替代 F3 三路電池。
- SoT 用 markdown frontmatter 三鍵，不用 JSON 布林。
- graph 謂詞跳過由 coordinator 評三前置；`graph.yaml` 只加條件邊或註記，不刪鍵。

## Test Skeletons(選配)

- `test_s_1_1_attest_visible_three_slots`
- `test_s_1_2_attest_silent_red`
- `test_s_1_3_reader_false_when_missing_or_empty`
- `test_s_1_4_no_sibling_boolean_in_contract`
- `test_s_1_5_blame_is_not_who_when`
- `test_s_1_6_wording_is_not_sot`
- `test_s_2_1_contract_version_reads_canonical_key`
- `test_s_2_2_read_seam_red`
- `test_s_2_3_pre_210_ne_cut`
- `test_s_2_4_pre_hops_200_slot_reject`
- `test_s_2_5_hops_not_before_declare`
- `test_s_3_1_new5_cut_ok`
- `test_s_3_2_new5_wait_red`
- `test_s_3_3_graph_word_ne`
- `test_s_3_4_nodes_kept`
- `test_s_3_5_undeclared_stays_old7`
- `test_s_4_1_doctor_honest_incompatible`
- `test_s_4_2_doctor_ne_ticket`
- `test_s_4_3_marketplace_cache_not_fourth`
- `test_s_4_4_no_doctor_handshake_edit`
- `test_s_5_1_battery_single_entry`
- `test_s_5_4_token_keep`
- `test_s_5_5_token_del_red`
- `test_s_5_6_hollow_true`
- `test_s_5_7_hollow_files`
- `test_s_5_8_hollow_f2`
- `test_s_5_9_f2_regress_floor`
- `test_s_6_1_pre_and`
- `test_s_6_2_old7_freeze`
- `test_s_6_3_old7_fold_red`
- `test_s_6_4_self_old7`
- `test_s_6_5_new5_not_live_dirs`
- `test_s_7_1_keep_mk_red`
- `test_s_7_2_keep_ship_mech`
- `test_s_8_2_stage5_files_allowlist`
- `test_s_8_4_this_hop_draft_two_files`
- `test_s_8_5_stage3_na`

## 確認紀錄

- R 範圍確認 | 2026-09-14 | Writer C 依金本 Decision B 1A–6A + 派工必蓋：cut SoT、讀鍵縫、graph+dual-read、doctor、SC／hollow、Non-Goals、Files 准許清單、Stage3 N/A。8 個 R。不另開 slug。
- S 逐段確認完成 | 2026-09-14 | 全 R 已展開；每 S 有觀測欄。Decision CASE 22 列全掛 S。加 Files／本 hop draft／Stage3 N/A／Q-carry。S＝44（S-1.1–S-1.6、S-2.1–S-2.5、S-3.1–S-3.5、S-4.1–S-4.4、S-5.1–S-5.9、S-6.1–S-6.5、S-7.1–S-7.3、S-8.1–S-8.7）。
- 4 小節 | 2026-09-14 | AC／Out of Scope／Diff Budget／Dependencies 齊。
- Verification Profile + DBC | 2026-09-14 | lane: full；Risk: high；Failure Model 13 列；DBC applicable（②③⑧⑨⑪）。
- Stage 3 對帳 | 2026-09-14 | 0／9 N/A；Owner ACCEPTED Stage3 N/A；無 ACCEPTED Demo 場景。
- DD 掃描 | 2026-09-14 | DD-1…DD-10 待人審。無未定三詞。不翻 Decision。
- 本 hop 不送 G2 | 2026-09-14 | `verdict` 空；`status: draft`；不跑 N7 三連動；不改 STATUS。
