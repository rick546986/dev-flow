---
feature: five-station-f3
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 1. 討論 — 五站 F3（Implementer C：cut 證明／前置／graph／doctor／成功≠空切）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／F1 annex／F2 Decision,不是現場一問一答。
> Lane = **full**。本檔 **只 Stage 1 討論**；status 留 **draft**；**不送 G1**、不宣稱 Human Stage1 PASS。本 PR 不改 STATUS／HISTORY。
> 原料:brief-v3 §6–§7、F0 狀態機、F1 annex、F2 完成樹（coordinator + G3 PASS）、`_templates/1-discussion.md`。
> C 線只挖五件事:①**cut attestation**（人怎麼看見「已切」、禁默默改函式）；②**前置**（2.1.0／非 in-flight／cut 三者會不會互證成空）；③**graph**（用語 vs 改 `N7-g1`／`N6-g2`）；④**doctor 誠實**（綠仍≠路條；bump 後握手）；⑤**成功判準**（檔在／用字／`True` ≠ F3 完）。
> F3 刀(brief §7):**Cut**＝新 slug 預設五站；舊 7 只服務 freeze + dual-read；guide／STATUS 用語切五站。**不做**:刪 G1／G2／`ACCEPTED`；改已經 freeze 的 slug；一次大爆炸改模板全文。本 slug **不是**第一隻活五站白老鼠。

## Problem
痛:F1 牙與 F2 coordinator 都已 G3 PASS,但 `f3_cut_happened` 恒 `False`,新開 slug 預設仍舊 7——仍經 `N7-g1`／`N6-g2` 等人,chat 仍可蓋章。F3 該把「之後才開、cut 當下尚無 1–7 `.md`」的 slug 預設改五站;若只把函式改 `True`、只改 guide 用字、或契約仍 `2.0.0` 就把 hops 當五站預設,會變成空切、SLOT-REJECT 紅、或遠端改線。本目錄一有本檔就是 in-flight,拿自己當第一隻活五站 = 污染觀測。
現在怎麼繞:新 slug 走舊 7 graph;coordinator 對 live 一律 `allow_legacy()`;doctor 印 `COMPATIBLE` 當「沒事」;owner 用 chat 開下一站。F3 尚未開刀。

## Context(已知事實)
- F3 刀=新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide／STATUS 用語切五站。不做:刪 G1／G2／`ACCEPTED`;改已經 freeze 的 slug;一次大爆炸改模板全文:notes/design/five-station-simplify-brief-v3.md:L180-L182
- F3 之後 token **仍在 repo**;刪它們=新 brief,不是本切法的尾巴:notes/design/five-station-simplify-brief-v3.md:L182
- in-flight freeze:`docs/dev/<slug>/` 在 F3 cut 當下已有任一站檔 → 整段舊 7(含例行 G1／條件 S3／G2／G3)直到 Ship;不准中途切五站:notes/design/five-station-simplify-brief-v3.md:L165
- 新 slug:F3 cut **之後**才預設五站。F0–F2 期間新開的母版改版軌仍走舊 7:notes/design/five-station-simplify-brief-v3.md:L166
- 舊 7 機械:模板、graph、G1／G2／`ACCEPTED` 牙、`_stage3_impl.py` **不刪**。Cut 之後它們服務 in-flight + dual-read:notes/design/five-station-simplify-brief-v3.md:L167
- 採用專案:`dev-setup` upgrade 到 2.1.0 之後才看五站;未 upgrade = 舊 7;不得遠端改別人 repo 的路線:notes/design/five-station-simplify-brief-v3.md:L168
- 禁併刀:四刀不准併、不准 F0 偷做 F1 牙:notes/design/five-station-simplify-brief-v3.md:L173
- OC-9 in-flight freeze;OC-10 F0–F3 都不刪 G1／G2／`ACCEPTED`;F0 不改模板／gates／graphs:notes/design/five-station-simplify-brief-v3.md:L44-L45
- 狀態機 `Idle`:新 slug 在 F3 前仍開舊 7、不進本機;F3 後進 `Intake`:notes/design/five-station-simplify-f0-state-machine.md:L37
- in-flight freeze:slug 已有舊 7 檔 → 不建立本機;coordinator 放手給既有 graph:notes/design/five-station-simplify-f0-state-machine.md:L49-L50
- X4:in-flight slug 套本機 = 違 OC-9:notes/design/five-station-simplify-f0-state-machine.md:L196
- SLOT-UNDECLARED-ROUTE:未宣告 2.1.0 dual-read 時,採用端路線 = 舊 7;marketplace 不能單獨改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L20
- SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS:契約仍 2.0.0 且 hops 已是五站預設 → 紅、不得改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24
- SLOT-DOCTOR-GREEN-MEANS:doctor 綠／`COMPATIBLE`／exit 0 只證明握手;`≠` 路線沒變、`≠` 已切五站:notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28
- SLOT-IN-FLIGHT-DETECT:已有 1–7 任一 `.md` → in_flight;僅 html、零個 1–7 `.md` → 不是 in-flight:notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32
- F1 G3 PASS、Active 已移出:docs/dev/HISTORY.md:L659-L663
- F2 coordinator G3 PASS;HISTORY 明寫 **no F3 opened**:docs/dev/HISTORY.md:L719-L723
- F2 7-review 頂欄 `verdict: PASS`／`status: approved`;標題鎖 **F2 knife only**:docs/dev/five-station-f2/7-review.md:L1-L12
- 本 tree Active **空**(`目前無進行中的改版軌。`):docs/dev/STATUS.md:L32
- STATUS Backlog A **仍寫**「下一刀 F1 teeth＋dual-read annex」—— F1／F2 已出貨,此列是過期看板,不是「F3 已切」:docs/dev/STATUS.md:L50
- F2 完成樹:coordinator 在;`f3_cut_happened` **恒 `False`**(註解:F2 never cuts):scripts/five_station_f2.py:L276-L278
- 三前置:`declared`(契約字串以 `2.1` 開頭) ∧ ¬in-flight ∧ cut → 才回五站;否則 `allow_legacy()`:scripts/five_station_f2.py:L286-L293
- doctor／marketplace／cache 被丟棄,不是路條:scripts/five_station_f2.py:L289-L290
- 缺 cut 時拒絕理由=`仍舊 7 F3 cut 未發生`;缺 2.1=`路線未宣告 仍舊 7`;in-flight=`仍舊 7 in-flight`:scripts/five_station_f2.py:L303-L307
- F2 `contract_version()` 讀 `version` 或 `contract_version`,**不讀** `devflow_contract_version`:scripts/five_station_f2.py:L260-L268
- 現行契約正本鍵是 `devflow_contract_version`=`2.0.0`(沒有 `version`／`contract_version` 鍵):devflow-contract.json:L1-L2
- runtime 只聲明支持 `2.0.0`:hooks/runtime-capabilities.json:L1-L4
- doctor:專案契約版本必須 ∈ plugin `supported_contract_versions`,否則 fail-closed:hooks/_doctor_impl.py:L193-L202
- doctor 綠時印 `COMPATIBLE` 並 exit 0:hooks/_doctor_impl.py:L492-L500
- Stage 2 graph 預設路經 `N7-g1`(例行人類停點):skills/dev-flow/stage2/graph.yaml:L53-L57
- Stage 4 graph 預設路經 `N6-g2`:skills/dev-flow/stage4/graph.yaml:L93-L98
- Gate token 釘死:G1=OC 全裁決+抽查下層誤放;G2=R/S+DD+Profile+Demo;G3=本次 S 全綠+回歸+現象+Evidence:scripts/check-gate-tokens.sh:L44-L60
- F2 S-8.1:完成樹無 F3 cut;guide／STATUS 用語未切五站;後站不准把 F3 改成 In:docs/dev/five-station-f2/4-spec.md:L826-L830
- F2 Out of Scope 把 F3 寫成「新 slug 預設五站;guide／STATUS／**graph 用語**切五站」—— brief §7「做」列只寫 guide／STATUS 用語,沒寫改 `graph.yaml`:docs/dev/five-station-f2/4-spec.md:L963 notes/design/five-station-simplify-brief-v3.md:L180
- 指南現況用語仍是「七站單行,只有 G1 / G2 / G3 會被人擋」:guides/guide-dev-flow.html:L573
- STATUS 政策:feature branch／worktree **不碰** STATUS 正本表列;ship 移出 Active 由合併後在整合分支做:docs/dev/STATUS.md:L10-L13
- Backlog B 凍 Stage 1–4 模板直到完整 full-lane 觀測做完:docs/dev/STATUS.md:L48
- 受影響面(本 hop 不動):`f3_cut_happened`、`devflow-contract.json`、`hooks/runtime-capabilities.json`、`hooks/_doctor_impl.py`、各站 `graph.yaml`、`guides/guide-dev-flow.html`、STATUS／HISTORY 用語、各 in-flight slug 的路線、本目錄自己(一落檔即 in-flight)。

## Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 母版 owner(tony／rick) | 切新 slug 預設五站,但不折舊 7、不刪閘 | 裁 brief、簽 gate | F0–F2 落盤、本 tree | cut 要寫在哪才算「已發生」 | GitHub、Cursor chat |
| F3 討論／實作 agent | 把 attestation／前置／graph／doctor／成功問清楚;本 hop 只寫討論 | 寫本目錄討論檔 | brief、annex、F2 碼、doctor | 函式 `True` 算不算 cut | Cloud Agent、PR |
| coordinator(已落地) | 三前置全真才建五站機;否則 `allow_legacy()` | 讀契約／站檔／cut 函式;**禁**寫判定 | `allow_legacy`、拒絕理由 | `f3_cut_happened` 何時准改 | 本 tree `five_station_f2.py` |
| 採用專案 owner | 更新 plugin 後路線不要被遠端改 | 系統外(自己 repo 的契約檔) | 自己的契約、doctor 輸出 | hops 已換、契約仍 2.0.0 時誰說了算 | marketplace／plugin 指令、口頭 |
| in-flight slug 執行者 | 走完手上舊 7,不被中途折五站 | 既有 graph／模板 | 自己目錄已有 1–7 `.md` | F3 cut 會不會誤折自己 | 既有 hop |
| 新 slug 寫手(cut 後才開) | 預設五站、中間不等例行閘 | 寫 1–7 檔名家族 | 模板、F2 coordinator | graph 是否仍停 `N7-g1` | PR、chat |
| doctor 操作者 | 看握手綠／紅 | 跑 `devflow-doctor.sh` | `COMPATIBLE`／`INCOMPATIBLE` 一行 | 綠 ≠ 切線;bump 後 supported 沒跟上會紅 | 終端機 |
| Ship 審查者 | 出貨樹=審過的樹;機械綠 ≠ PASS | 寫 7-review `verdict:` | G3 八點 | hop 有沒有跳過 Must-keep | 瀏覽器審頁 |

## Real-world Context

### Actors
表見上節獨立 H2 `## Actors`。產檔器只吃該表的誰／要什麼／缺什麼;`#scan-people` 不捲 Journey 或 Assumption。

### Current Journey
正式 SOP(F3 後才預設):新 slug 走五站別名 + coordinator 評謂詞 hop;舊 slug 仍舊 7。實際做法(**現在、F3 尚未落地**)如下。兩者都記。現況圖只畫這段,不畫尚未發生的 cut 箱。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 母版 | 把 F2 coordinator 合進 plugin | marketplace／git | — | `allow_legacy`;`f3_cut_happened`=`False` | 新 slug 仍舊 7 |
| 2 | 採用 owner | `marketplace update` + `plugin update` | plugin cache | — | 新 hops／新牙;契約檔常未動 | hops 已換,契約仍 2.0.0 |
| 3 | 同一人 | 跑 doctor | `devflow-doctor.sh` | — | `COMPATIBLE` + exit 0 | 綠只證明 `2.0.0 ∈ supported`≠切線 |
| 4 | 新 slug 寫手 | 開資料夾、寫 `1-discussion.md` | 舊 7 模板／graph | owner 簽 G1 | 站檔 + G1 twin | 仍經 `N7-g1` 等人;chat 可蓋章 |
| 5 | coordinator | 評三前置,缺 cut → legacy | `five_station_f2.py` | — | 理由=`F3 cut 未發生` | 碼在,預設沒切 |
| 6 | in-flight 執行者 | 仍走 `N7-g1`／`N6-g2` | 既有 graph | owner 簽閘 | G1／G2 twin | 若 cut 誤折就沒舊路 |
| 7 | 指南讀者 | 讀「七站單行,只有 G1／G2／G3 會被人擋」 | `guide-dev-flow.html` | — | 七站用語 | 用語未切;切了用字≠行為 |
| 8 | 本討論 | 把 attestation／前置／graph／doctor／成功問成 OQ | 本檔 | 後續 F3 收斂 | 討論檔 | 本 hop 不選定落點 |

### Workarounds
- F2 用恒 `False` 的 `f3_cut_happened` 擋 live 五站;擋的是**行為**,不是「人看得見的 cut 紀錄」。
- F1 文案牙擋「doctor 綠所以跟 hops」;擋的是**寫出來的謊**,不是 cut 本身。
- 採用端路線實際靠「人記得 brief §6」與「不要遠端改別人 repo」。
- owner 用 chat 當新 slug 的 hop 開關。系統留下下一站檔,不留下「cut 已發生」。
- STATUS／HISTORY 當刀口 log:人記得改看板;Backlog A 仍停在「下一刀 F1」。
- 這些步驟常不留「這次 cut 誰簽的、讀哪個鍵、graph 有沒有一起動」。

### Exceptions
- 舊 7 與 in-flight **不套**三個 cap;它們走既有 T 嘗試上限 4。
- Fast lane 不是本包要廢;本 slug 是 full。
- F3 可以改預設路線,但**不准**改已經 freeze 的 slug。
- 模板全文改寫若要做,另開刀,不叫 F3 偷做。
- doctor schema／契約版本不合會 INCOMPATIBLE(與路線是兩條)。
- `[Assumption]` 採用端典型升級=先 marketplace update、後(或不)bump 契約:無採用逐字稿;風險=高。
- `[Assumption]` 只把 `f3_cut_happened` 改 `True`、不 bump 2.1.0、不改 hops 預設 = 空切:無未來 log;風險=高。
- `[Assumption]` 契約仍 2.0.0 卻把 hops 當五站預設 = SLOT-REJECT 紅或關牙後遠端改線:風險=高;期限=Stage 2;過期擋把「只切 hops」寫進 Decision。
- `[Assumption]` 只改 guide／STATUS 用字、graph 仍停 `N7-g1` = 用語切、行為沒切:風險=高;期限=Stage 2。
- `[Assumption]` NEW5 試體是合成 fixture 或 **cut 之後才開** 的新 slug,不是本目錄、也不是 `five-station-f2`／`five-station-simplify`:風險=高;期限=Stage 2;過期擋把本目錄當白老鼠。

### Evidence
- F0／F1／F2 書面:brief-v3、狀態機、F1 annex、F2 4-spec／7-review;Owner 已核准(檔頭／G3)。本 hop 不改那些檔。
- 本 tree 已核:上列 Context 出處(2026-09-14 讀過 `origin/main` `2b6a9b2`,行段支持斷言)。
- F1／F2 已出貨:docs/dev/HISTORY.md:L659-L663、L719-L723。Active 空:docs/dev/STATUS.md:L32。Backlog A 過期:docs/dev/STATUS.md:L50。
- coordinator／doctor／契約／graph／token:上列 scripts／hooks／skills／guides 出處。
- `[Assumption]` 見 Exceptions;採用升級逐字稿／未來 cut 紀錄／第一隻活五站皆無。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「函式改 True ≠ cut」為假 → attestation 可以只改 `f3_cut_happened` | 高 | Decision 有無把「無人類可見紀錄的 True」標成合法 cut | F3 收斂;過期擋把 silent flip 當已核 |
| 「2.1.0 必須跟 hops 預設同動」為假 → 可先切 hops 再 bump | 高 | 對照 F1 SLOT-REJECT:2.0.0+五站 hops 是否仍紅 | Stage 2／owner;過期擋「只切 hops」 |
| 「讀錯契約鍵」為假 → bump `devflow_contract_version` 就能讓 `declared` 真 | 高 | 改完正本鍵後跑 `contract_version()` 是否仍回空字串 | Stage 2／實作者;過期擋「bump 了所以已宣告」 |
| 「用語切 ≠ 行為切」為假 → 只改 guide 就算 F3 完 | 高 | 新 slug 是否仍經 `N7-g1` 等人 | Stage 2;過期擋把用字當成功 |
| 「NEW5 用合成或 cut 後新開 slug」為假 → 拿本目錄當白老鼠 | 高 | Files／fixture 路徑不含本目錄站檔當 hop 試體 | Stage 2;過期擋 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | 調查跟 brief／狀態機 | notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名) | 是 |
| F1 annex | 2.1.0／doctor／in-flight SLOT | notes/design/five-station-simplify-f1-dual-read-annex.md | 是(使用者點名) | 是 |
| F2 完成樹 | coordinator 預設舊 7、G3 PASS、無 F3 | docs/dev/five-station-f2/4-spec.md、docs/dev/five-station-f2/7-review.md、scripts/five_station_f2.py、docs/dev/HISTORY.md | 是(使用者點名 prior knives G3 PASS) | 是 |
| Stage 1 模板 | 骨架與審頁 | _templates/1-discussion.md | 是(方法包) | 是 |
| doctor／契約 | 綠=握手;正本鍵名 | hooks/_doctor_impl.py、devflow-contract.json、hooks/runtime-capabilities.json | 是(本 tree) | 是 |
| graph／指南 | 例行停點與七站用語仍在 | skills/dev-flow/stage2/graph.yaml、skills/dev-flow/stage4/graph.yaml、guides/guide-dev-flow.html | 是(本 tree) | 是 |
| token | 禁刪 | scripts/check-gate-tokens.sh | 是(本 tree) | 是 |
| 看板 | Active 空;Backlog A stale;F3 未開 | docs/dev/STATUS.md、docs/dev/HISTORY.md | 是(本 tree) | 是 |
| 採用升級逐字稿 | 驗證「先 update 後 bump」 | 無;public repo 禁收公司路徑 | 禁 | 否 |

## Goals
- G-cut-1:cut 之後,一個 **cut 當下沒有** 1–7 `.md` 的新 slug,預設走五站;中間不等例行 G1／G2 提交判定。
- G-freeze-1:cut 當下已有 1–7 `.md` 的 slug(含本目錄、含 `five-station-f2`、含 `five-station-simplify`)整段舊 7 到 Ship;沒有五站狀態寫入。
- G-token-1:G1／G2／`ACCEPTED` token 與檔仍在;dual-read／舊 7 牙不一次紅。
- G-attest-1:人能指出「cut 已發生」的**可見紀錄**(誰、何時、讀哪個條件)。只把函式改 `True`、不留紀錄,不算切完。
- G-pre-1:契約仍 `2.0.0` 且 hops 已當五站預設 → 仍被看成違規,不得改線。
- G-honest-1:doctor 印 `COMPATIBLE`／exit 0,不足以當 cut、也不足以讓 coordinator 走五站 hop。
- G-graph-1:人能分辨「用語切了」與「新 slug 不再例行停 `N7-g1`／`N6-g2`」。兩者若不同,不得互相冒充成功。
- G-self-1:本 slug 自己走到 G1／G2／G3 時仍是舊 7;沒有五站狀態寫入;不是第一隻活五站白老鼠。
- G-success-1:F3 完＝同一電池能證明(a)cut 後新 slug 預設五站、(b)in-flight 仍舊 7、(c)token 仍在。檔在、guide 用字、`f3_cut_happened==True`、F2 綠 ≠ F3 完。
- G-keep-1:點名三種失敗不得當 F3 成功:(1)謂詞真仍等人;(2)Must-keep 紅仍 hop;(3)機械綠 → Ship Done。
- G-carry-1:本檔列出的 attestation／前置／graph／doctor／成功題,到規格時每條有去向,不能無聲消失。

## Requested solution
- F3 做 **Cut**:新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide／STATUS 用語切五站。
- **cut attestation 落點本討論不選定。**語意槽(誰／何時／讀哪個條件／是否人類可見)要能被指出。
- 三前置仍是:宣告 2.1.0 ∧ 非 in-flight ∧ cut 已發生。缺一條 → `allow_legacy()`。doctor 綠、marketplace update、plugin cache **不是**第四條。
- 本 hop 不選定:要不要 bump `devflow-contract.json`、要不要改 `graph.yaml`、要不要改 `_doctor_impl.py`、attestation 寫在函式／檔／契約／看板哪一格。
- 候選(未定案):同一入口 dual-path selftest——cut 後新 slug 形 + in-flight OLD7 形,缺一路即紅。
- 舊 token／twin／graph 檔不刪。NEW5 只准合成 fixture,或 **cut 之後才開** 的新 slug;不准本目錄。
- 模板全文改寫另開刀。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`graph.yaml`、gate token、STATUS、HISTORY、契約版本、doctor、coordinator。
- 本 hop 不送 G1;status 留 draft;不宣稱 Human Stage1 PASS;不合併。
- **鎖:不刪 G1／G2／`ACCEPTED`;不把 in-flight 折成五站;不拿本 slug 當活五站白老鼠。**
- 不一次大爆炸改模板全文(brief §7 明文不是 F3)。
- 不重開 F0 十條;不放寬 hop≤2／Decide≤1／Goal≤1。
- 不在本討論選定 attestation 落點、graph 改寫幅度、或契約鍵怎麼對。
- 不把「doctor 綠」或「marketplace update」寫成 cut。
- 不把「檔在」「guide 已寫五站」「函式回 `True`」「F2 綠」寫成 F3 完成。
- 不把「已經 cut 了」解讀成 Must-keep 也可以 hop 掉。
- 不發明本 slug 的 G1／G2／G3 PASS。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:full
- [x] Q2:本 hop 是否只 Stage 1、不改 STATUS、不合併、不發明 G1?→ 原派工:是。status 留 draft
- [x] Q3:F3 刀是否=新 slug 預設五站、舊 7 只服務 freeze+dual-read、guide／STATUS 用語切五站、不刪閘、不折 freeze?→ brief §7;翻=新 brief
- [x] Q4:本 slug 可否當第一隻活五站白老鼠?→ 否。本檔一落盤=`1-discussion.md` 在 = in-flight,整段舊 7 到 Ship
- [x] Q5:prior knives 是否 G3 PASS、F3 是否已開?→ F1 HISTORY G3 PASS;F2 7-review + HISTORY G3 PASS 且明寫 no F3 opened;Active 空
- [x] Q6:F2 coordinator 現在對 live 預設哪條路?→ `f3_cut_happened` 恒 False → `allow_legacy()`;拒絕理由含「F3 cut 未發生」
- [x] Q7:G1／G2／`ACCEPTED` 可否刪?→ 否。F0–F3 都不刪;刪=新 brief
- [x] Q8:in-flight 偵測是否=1–7 任一 `.md`?→ F1 SLOT-IN-FLIGHT-DETECT;僅 html 不算
- [x] Q9:doctor 綠是否等於已切五站?→ 否。SLOT-DOCTOR-GREEN-MEANS;F2 綠不是路條
- [x] Q10:marketplace update 單獨是否=cut?→ 否。SLOT-UNDECLARED-ROUTE;F2 S-3.2
- [x] Q11:plugin cache 是否第四條前置?→ 否。F2 S-3.6
- [x] Q12:cut 之後 Must-keep／三失敗是否仍在?→ 在。摺的是停點不是完整度;F3 不准偷 M
- [x] Q13:本 hop 可否改模板全文?→ 否。brief §7 不做;Backlog B 仍凍 Stage 1–4 模板
- [x] Q14:STATUS Backlog A「下一刀 F1」算不算現況或已切證據?→ Active 空;A 列 stale;不是 F3 已切
- [~] Q15:cut attestation 是否必須人類可見、可指出,而不能只把 `f3_cut_happened` 改 `True`?(帶假設:**必須可見**;暫定值=silent flip 不合法;風險=高;期限=F3 Decision,過期不得把函式 `True` 當已核 cut)
- [~] Q16:2.1.0 宣告是否必須與「hops 預設五站」同刀或先於該刀?(帶假設:**必須同動或先宣告**;否則 SLOT-REJECT;風險=高;期限=F3 Decision,過期擋「只切 hops」)
- [~] Q17:F2 `contract_version()` 不讀 `devflow_contract_version`——F3 若只 bump 正本鍵,`declared` 是否仍假?(帶假設:**仍假,除非改讀鍵或雙寫**;風險=高;期限=F3 Decision,過期擋「bump 了所以已宣告」)
- [~] Q18:契約 bump 到 2.1.0 時,`supported_contract_versions` 若仍只有 `2.0.0`,doctor 是否應誠實紅?(帶假設:**應 INCOMPATIBLE**;綠仍只握手、不是路條;風險=高;期限=F3 Decision)
- [~] Q19:F3 成功是否=同一電池 (a)cut 後新 slug 預設五站 (b)OLD7 freeze (c)token 在,缺一即紅?(帶假設:**是**;檔在／用字／`True`／F2 綠都不算;風險=高;期限=F3 Decision,過期擋 hollow)
- [>] Q20:attestation 落點在哪?改函式讀檔／契約 2.1.0 本身／人類 verdict／STATUS 用語／獨立標記?本討論不選。移交 F3 收斂
- [>] Q21:F3 要不要改各站 `graph.yaml`(拿掉預設 `N7-g1`／`N6-g2` 等人)?brief「做」列是 guide／STATUS 用語;F2 Out of Scope 把 graph 用語捆進 F3;F0 OC-10 只禁 F0 改 graph。移交 F3
- [>] Q22:F3 要不要改 `hooks/_doctor_impl.py`,還是只動 `supported_contract_versions` 清單?移交 F3
- [>] Q23:「guide 用語切五站」算哪些檔?至少 `guides/guide-dev-flow.html` 仍寫七站單行。移交 F3
- [>] Q24:brief 要 F3 切 STATUS 用語,但 feature branch 禁碰 STATUS 正本——用語切走 companion、還是本刀例外?移交 F3(與看板政策對帳)
- [>] Q25:第一隻活五站 slug 叫什麼、何時開?不是本目錄、不是已 freeze 的 F1／F2 母軌。移交 F3;本討論不發明名字

## Constraints
- 本 PR 不宣稱 G1 PASS、不宣稱 Human Stage1 PASS;不改 STATUS／HISTORY。
- 討論盲下游:本檔不指定腳本／API／元件當目標;attestation／graph／契約鍵只寫成 OQ。
- **Owner-locked F3 刀:**新 slug 預設五站;舊 7 只服務 freeze+dual-read;不刪閘;不折 freeze;不炸模板。
- **Owner-locked 本 slug 路線:**舊 7 到 Ship。不是白老鼠。
- **Owner-locked cap 數字:**hop≤2／Decide≤1／Goal reopen≤1;舊 7 不套。
- **Owner-locked:Must-keep 未綠不得 hop。**三失敗不得當成功。
- **採用 hop 身分:**graph／hooks 住方法包。未宣告 2.1.0 之前,marketplace 可換 hops 而 doctor 仍可因 `2.0.0` 握手綠。綠 ≠ 切線。
- 詞條(語言,不是方案):**cut**=新 slug 預設從舊 7 改五站這一件事,不是刪閘、不是折舊 slug。**cut attestation**=人指得到的「已切」紀錄,不是函式回傳值本身。**三前置**=2.1.0 已宣告 ∧ ¬in-flight ∧ cut 已發生。**空切**=用字／函式／檔在變了,新 slug 行為沒變,或舊 slug 被折。**正本鍵**=`devflow_contract_version`。**讀鍵縫**=F2 `contract_version()` 讀的 `version`／`contract_version` 與正本鍵不是同一個。**graph 用語**=指南／看板把七站改稱五站。**graph 行為**=預設 hop 不再例行停 `N7-g1`／`N6-g2`。**in-flight freeze**=已有 1–7 `.md` 的 slug 走舊 7。**白老鼠**=拿本目錄或已 freeze 母軌當第一隻活五站。本 hop 不寫進長期記憶。

### F3 移交種子(不是施工)
- Q15–Q19 過期 → 擋本 slug G2(不得把假設升格成已核)。
- Q20–Q25 維持 `[>]`;後站不得假裝 Stage 1 已選落點。
- Q21 是 C 線主縫:brief 與 F2 Out of Scope 對 graph 的句子不一致,必須在 Decision 對帳,不能默選。
- Q17 是前置主縫:只 bump 正本鍵可能切不動 `declared`。
- 本資料夾已有本檔 = 已 in-flight;後站不得對自己開五站機。

## 驗收雛形
- AC-1(G-cut-1):假設 F3 已宣稱 cut,當人開一個 **cut 當下沒有** 1–7 `.md` 的新 slug 並求預設路線,則走五站,中間不等例行 G1／G2 提交判定。
  - 從哪看:該 slug 的路線判定／hop 紀錄(人可指的檔或拒絕理由;不預填通道)
  - 看到什麼算對:預設五站;沒有「請人審 A4／A7」的例行停
  - 拿什麼試:cut **之後**才造的假 slug;不是本目錄
- AC-2(G-freeze-1):假設 F3 cut 當下某 slug 已有站檔,當路線被求切五站,則該 slug 仍走舊 7 到 Ship。
  - 從哪看:該 slug 目錄與被拒絕的 hop
  - 看到什麼算對:仍有例行 G1／條件 S3／G2／G3;沒有五站狀態寫入
  - 拿什麼試:本目錄(本 hop 落檔即 in-flight);`five-station-f2`;任一已有 1–7 `.md` 的 slug
- AC-3(G-token-1):假設 F3 做完,當人找 G1／G2／`ACCEPTED` token,則檔仍在。
  - 從哪看:`scripts/check-gate-tokens.sh` 與 token 檔
  - 看到什麼算對:exit 0;token 字面仍在
  - 拿什麼試:本 tree 現況牙
- AC-4(G-attest-1):假設有人只把 `f3_cut_happened` 改成 `return True` 且沒有可見紀錄,當宣稱 F3 已切,則失敗。
  - 從哪看:cut 紀錄(人可指出誰／何時／讀哪個條件)
  - 看到什麼算對:有可見紀錄才算切;只有函式 `True` 不算
  - 拿什麼試:後續造的對照;本 hop 不跑 coordinator
- AC-5(G-pre-1):假設契約仍 `2.0.0`、hops 已被人當五站預設,當評路線,則違規、不得改線。
  - 從哪看:路線判定 + F1 SLOT-REJECT
  - 看到什麼算對:2.0.0+五站 hops 紅;未改線
  - 拿什麼試:採用端假樹(後續造)
- AC-6(G-honest-1):假設 doctor 剛印 `COMPATIBLE` 且契約仍 `2.0.0`,當有人把綠當 cut 或求五站 hop,則拒絕;理由是路線,不是「doctor 已綠」。
  - 從哪看:該次 hop 的拒絕理由
  - 看到什麼算對:理由含「路線未宣告」或「仍舊 7」或「cut 未發生」;不含「doctor 已綠所以可 hop」
  - 拿什麼試:本 tree 現況(契約 2.0.0 + doctor 可綠 + cut False)
- AC-7(G-graph-1):假設指南已改寫「五站」、但 Stage 2 graph 仍預設進 `N7-g1`,當有人標 F3 成功,則不得只靠用字過關。
  - 從哪看:guide 用字 **與** 新 slug 是否仍例行停 G1
  - 看到什麼算對:用語與行為分開記帳;只改用字≠成功
  - 拿什麼試:現況 `guide-dev-flow.html` L573 + `stage2/graph.yaml` L53-L57
- AC-8(G-self-1):假設本 slug 被求切五站自動前進,當看本目錄,則仍是舊 7 站檔與例行閘。
  - 從哪看:本目錄 1–7 `.md` 與被拒絕的 hop
  - 看到什麼算對:有 `1-discussion.md`;無五站機寫入
  - 拿什麼試:本資料夾
- AC-9(G-success-1):假設 F3 宣稱完成,當人只跑成功電池或只證明函式 `True`,則 (a)(b)(c) 三路都必須能獨立變紅、也能一起綠。
  - 從哪看:F3 selftest 出口與具名案(後續造;本 hop 不跑)
  - 看到什麼算對:三路各有至少一條正向綠、一條缺行為紅;整電池 exit 0 當且僅當三路都過
  - 拿什麼試:cut 後新 slug 形(合成或新開)+ 已有 1–7 `.md` 的 OLD7 + token 還在;不是本目錄
- AC-10(G-keep-1):假設出現下列任一,當有人標 F3 成功,則失敗:(1)謂詞全真且 latch 假,卻仍留下「要不要繼續」;(2)Must-keep 紅仍 hop;(3)機械全綠且無人寫 `verdict: PASS` 卻標 Ship Done。
  - 從哪看:hop 紀錄／拒絕理由／7-review 頂欄
  - 看到什麼算對:三條各自可紅;沒有「已經 cut 了所以可省」
  - 拿什麼試:F2 已有的三張注入對照形;後續沿用,不是本 hop
- AC-11(G-carry-1):假設本檔 Q15–Q25 列了一題,當人讀到 F3 Decision／Spec,則該題有去向。
  - 從哪看:Stage 2 對帳
  - 看到什麼算對:每條高影響 OQ 有處理／Non-Goal／仍待驗;沒有消失
  - 拿什麼試:Q15 可見紀錄、Q16 同動、Q17 讀鍵縫、Q19 三路電池、Q21 graph

## 現況圖
誰:F2 coordinator
做什麼:allow_legacy
工具:f3_cut=False
痛點:新 slug 仍舊 7
↓
誰:doctor
做什麼:印 COMPATIBLE
工具:devflow-doctor.sh
痛點:綠≠切線
↓
誰:新 slug 寫手
做什麼:仍經 N7-g1 等人
工具:舊 7 graph
痛點:chat 蓋章當審查

## 邏輯圖(ASCII)
```
now
|-- F1 G3 PASS
|-- F2 G3 PASS            [coordinator in tree]
|-- f3_cut_happened       [always False]
|-- contract 2.0.0        [key=devflow_contract_version]
|-- F2 reader             [reads version|contract_version => ""]
|-- doctor COMPATIBLE     [handshake != route]
|-- graph N7-g1 / N6-g2   [routine human stop]
|-- guide still "7-station"
|-- STATUS Active empty
+-- Backlog A             [stale: still says next=F1]

cut-attest                [OPEN; Q15/Q20]
|-- silent True           [hollow]
|-- human-visible record  [who/when/which]
|-- contract 2.1.0 as cut [key seam Q17]
+-- STATUS wording        [branch may not touch board]

preconditions             [OPEN; Q16-Q18]
|-- 2.1.0 declared
|-- not in-flight
|-- cut happened
|-- 2.0.0 + five hops     [SLOT-REJECT]
+-- supported list        [doctor may go red]

graph                     [OPEN; Q21]
|-- wording only          [guide/STATUS]
|-- rewrite N7-g1/N6-g2   [behavior]
+-- later knife           [not silent pick]

f3-must-prove
|-- NEW after cut         [not this dir]
|   +-- default five      [no routine G1/G2 wait]
|-- OLD7 freeze
|   |-- no five-state
|   +-- tokens still in
+-- same battery          [each path can red]

fail
|-- silent True as cut
|-- hops five + 2.0.0     -> SLOT-REJECT or remote route
|-- wording-only success
|-- fold in-flight
|-- delete tokens
|-- this slug as white-rat
|-- doctor green as cut
+-- file exists / F2 green -> hollow F3
```

## Interview Log(推理鏈外顯)
- Q:F3 這一刀到底做什麼、為什麼 F2 做完還不能當已經切?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L166 notes/design/five-station-simplify-brief-v3.md:L180-L182 scripts/five_station_f2.py:L276-L278 docs/dev/HISTORY.md:L719-L723
  - 推理:brief 把 coordinator 與 cut 拆成兩刀。F2 G3 明寫 no F3 opened。函式恒 False,live 一律 legacy。預設路線沒變,所以現場痛(新 slug 仍等人、chat 仍蓋章)還在。
  - 結論:CONFIRMED F3 = 新 slug 預設五站 + 舊 7 只服務 freeze/dual-read + 用語切;F2 完 ≠ 已切。
- ⚠️ Q:為什麼「把 `f3_cut_happened` 改 `True`」不能當 cut attestation?
  - 事實:scripts/five_station_f2.py:L276-L278 notes/design/five-station-simplify-brief-v3.md:L180 docs/dev/five-station-f2/4-spec.md:L826-L830
  - 推理:F2 把 cut 做成一個永遠假的布林,好測「未切」。若 F3 只翻真,人在 tree 裡看不到誰准了、讀哪個條件、graph／契約有沒有一起動。這跟 F2「檔在 ≠ 完」同一形:布林是實作開關,不是出貨證明。可見紀錄的落點未選(Q20)。
  - 結論:NEEDS_VERIFICATION silent `True` 不合法(Q15 `[~]`);過期不得當已核寫進 Decision。
- ⚠️ Q:為什麼 2.1.0 宣告必須跟 hops 預設同動?讀錯鍵又為什麼是縫?
  - 事實:notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24 scripts/five_station_f2.py:L260-L268 scripts/five_station_f2.py:L286-L293 devflow-contract.json:L1-L2
  - 推理:F1 已釘 2.0.0+五站 hops=紅。只切 hops 不 bump = SLOT-REJECT,或關牙後遠端改線。F2 的 `declared` 卻讀 `version`／`contract_version`,正本是 `devflow_contract_version`。只 bump 正本鍵,`contract_version()` 仍回空字串,三前置第一條永不真——看起來 bump 了,live 仍 legacy,或反過來有人另寫一個假鍵讓 `declared` 真。
  - 結論:NEEDS_VERIFICATION Q16 同動、Q17 讀鍵縫;兩條都過期擋 G2。
- ⚠️ Q:graph 是改 hop、還是只改用字?為什麼本討論不准默選?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L180 docs/dev/five-station-f2/4-spec.md:L963 skills/dev-flow/stage2/graph.yaml:L53-L57 guides/guide-dev-flow.html:L573 notes/design/five-station-simplify-brief-v3.md:L45
  - 推理:brief F3「做」= guide／STATUS 用語。F2 Out of Scope 把 **graph 用語**捆進 F3。現場新 slug 等人是因為 graph 預設進 `N7-g1`／`N6-g2`。只改指南「七站→五站」,寫手仍停 G1 = 空切。改 graph 又碰 OC-10「F0 不改 graphs」與「不炸模板」——改 hop 節點≠炸模板,但是不是本刀,brief 沒寫死。默選任一邊都會偷做或空切。
  - 結論:OPEN Q21;Decision 必須對帳 brief vs F2 捆句,不得默選。
- Q:doctor 在 cut／bump 之後還誠實嗎?(發散)
  - 事實:hooks/_doctor_impl.py:L193-L202 hooks/_doctor_impl.py:L492-L500 hooks/runtime-capabilities.json:L1-L4 notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28
  - 推理:綠的定義是「契約版本 ∈ supported」。bump 到 2.1.0 而 supported 仍 `{2.0.0}` → 誠實紅。人會以為「更新壞了」。若為了綠而讓 doctor 在未宣告時仍 COMPATIBLE 且被讀成切線,SLOT 變裝飾。改握手實作 vs 只加 supported 清單 = Q22。
  - 結論:CONFIRMED 綠永遠只握手。Q18 `[~]` 誠實紅;Q22 移交實作落點。
- ⚠️ Q:F3 完成為什麼不能等於「函式真了」或「指南寫五站」?
  - 事實:docs/dev/five-station-f2/4-spec.md:L826-L830 notes/design/five-station-simplify-brief-v3.md:L165-L168 scripts/check-gate-tokens.sh:L44-L60
  - 推理:F2 已證「檔在／單路綠 ≠ 完」。F3 同形:只翻布林、只用字、只改看板,都測不到「新 slug 預設」+「舊 slug 沒被折」+「token 還在」。缺一路的電池可以全綠而現場已毀。
  - 結論:CONFIRMED G-success-1／Q19;三路可獨立紅才算完。
- Q:本 slug 會不會把自己當五站白老鼠?
  - 事實:notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32 notes/design/five-station-simplify-brief-v3.md:L165 notes/design/five-station-simplify-f0-state-machine.md:L49-L50
  - 推理:本檔落盤後目錄已有 `1-discussion.md`。偵測只認 1–7 `.md`。整段舊 7 到 Ship。對本目錄建五站機 = RP-15／X4。第一隻活五站必須是 cut **之後**才開的 slug(Q25)。
  - 結論:CONFIRMED 本 slug = live freeze 樣本(G-self-1、Q4);不是白老鼠。
- ⚠️ Q:本 hop 有沒有偷選落點、偷改 graph、或發明 G1?(盲點)
  - 事實:本 hop 派工(只 Stage 1、不改 STATUS、不合併、不發明 G1);notes/design/five-station-simplify-brief-v3.md:L173 docs/dev/STATUS.md:L10-L13
  - 推理:Requested solution 只列候選。Q20／Q21／Q22 維持 `[>]`。隱含預設(可見紀錄、同動、讀鍵縫、三路電池、誠實紅)已標 `[~]` 與期限。不改本 PR 的 STATUS,避免跟「feature branch 不碰看板」撞車——這正是 Q24 要移交的縫。
  - 結論:CONFIRMED 本檔只落討論;不選落點;不改 graph／契約／doctor;不宣稱 Human Stage1／G1。Q15–Q19 過期擋本 slug G2。
