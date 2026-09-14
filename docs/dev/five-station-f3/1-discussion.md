---
feature: five-station-f3
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 1. 討論 — 五站 F3（Cut：新 slug 預設五站；in-flight 仍舊 7）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／F1 annex／F2 G3 PASS,不是現場一問一答。
> Lane = **full**。本檔 **只 Stage 1 討論**；status 留 **draft**；**不送 G1**、不宣稱 Human Stage1 PASS。本 PR 不改 STATUS／HISTORY（看板由合併後 companion 寫；#359 是 STATUS 開 Active 的另一支,本 PR 不碰）。
> 原料:brief-v3 §6–§7、F0 狀態機、F1 annex、F2 Decision 4A／8A、F2 4-spec S-8.1、F2 7-review G3 PASS、`_templates/1-discussion.md`。
> A 線只挖四件事:①cut 怎麼被**指認**(契約 2.1.0／guide 一句／STATUS／`f3_cut_happened` 翻真)；②F2 三前置(2.1.0 ∧ ¬in-flight ∧ F3 cut)切完之後怎麼還是三條、不要塌成一條；③`graph.yaml` 改預設 vs dual-read 留舊節點；④marketplace × doctor 誠實仍是約束。
> F3 刀(brief §7):**Cut** —— 新 slug 預設五站；舊 7 只服務 freeze + dual-read；guide／STATUS 用語切五站。**不刪** G1／G2／`ACCEPTED`；不改已經 freeze 的 slug；一次大爆炸改模板全文另開刀,不叫 F3 偷做。本 slug 與 F0–F3 母版改版軌仍走**舊 7**(dogfood)。

## Problem
痛:F2 已過 Human G3 PASS —— coordinator、slug 級倉、同一電池 NEW5+OLD7 都在。新工作開出來,路線閘仍 `allow_legacy()`:契約未宣告 2.1.0、`f3_cut_happened()` 硬回假。寫手還是付 7 個停點(例行 G1／條件 S3／G2),人擋在本來可以自動 hop 的站。F3 是最後一刀,也是不可逆的預設翻轉:切完,新 slug 走五站;切錯,in-flight 被折、token 被刪、電池綠變空。
現在怎麼繞:F2 電池用合成 fixture 假裝「三前置全真」打 NEW5;live 新 slug 沒有這條門。下一站靠 chat／手寫舊 7。本資料夾本 hop 才開,一落檔即 in-flight。

## Context(已知事實)
- F3 刀=Cut:新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide／STATUS 用語切五站。不做:刪 G1／G2／`ACCEPTED`;改已經 freeze 的 slug;一次大爆炸改模板全文(模板改寫另開刀):notes/design/five-station-simplify-brief-v3.md:L180-L182
- F3 之後 G1／G2／`ACCEPTED` **仍在 repo**。刪它們=新 brief,不是本切法的尾巴:notes/design/five-station-simplify-brief-v3.md:L182
- 契約 dual-read minor=2.1.0。`2.0.0` 繼續讀舊 7;`2.1.0` 加五站別名／自動前進欄,不得讓舊 slug 一次變紅:notes/design/five-station-simplify-brief-v3.md:L164
- in-flight freeze=`docs/dev/<slug>/` 已有 1–7 任一 `.md` → 整段舊 7 到 Ship。不准中途切五站:notes/design/five-station-simplify-brief-v3.md:L165 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32
- 新 slug:F3 cut 之後才預設五站。F0–F2 期間新開的母版改版軌仍走舊 7:notes/design/five-station-simplify-brief-v3.md:L166
- 舊 7 機械(模板、graph、G1／G2／`ACCEPTED` 牙)不刪。Cut 之後它們服務 in-flight + dual-read:notes/design/five-station-simplify-brief-v3.md:L167
- 採用專案:`dev-setup` upgrade 到 2.1.0 之後才看五站。未 upgrade=舊 7。不得遠端改別人 repo 的路線:notes/design/five-station-simplify-brief-v3.md:L168
- Idle:新 slug 在 F3 前仍開舊 7,不進五站機。F3 後進 `Intake`:notes/design/five-station-simplify-f0-state-machine.md:L37
- 本機不管舊 7 in-flight 的 hop(那些仍走既有 `graph.yaml`):notes/design/five-station-simplify-f0-state-machine.md:L10-L15
- in-flight freeze:slug 已有舊 7 檔 → **不建立本機**;coordinator 放手給既有 graph:notes/design/five-station-simplify-f0-state-machine.md:L49-L50
- F2 三前置全要:契約已宣告 2.1.0 ∧ 非 in-flight ∧ F3 cut 已發生。缺一 → `allow_legacy()`。marketplace × doctor 誠實是約束不是功能。cache 不是第四條:docs/dev/five-station-f2/2-decision.md:L79 docs/dev/five-station-f2/2-decision.md:L136 docs/dev/five-station-f2/4-spec.md:L757-L760
- F2 完定義=同一電池 NEW5+OLD7 都能獨立紅、也能一起綠。檔在／F1 綠／單路 hop ≠ 完:docs/dev/five-station-f2/2-decision.md:L86
- F2 刀鎖死不做 F3 cut;後站不准把 F3 標成 In:docs/dev/five-station-f2/4-spec.md:L826-L829 docs/dev/five-station-f2/4-spec.md:L963
- F2 Human G3 PASS;Active 已移出;「no F3 opened」:docs/dev/HISTORY.md:L719-L723 docs/dev/five-station-f2/7-review.md:L1-L12 docs/dev/five-station-f2/7-review.md:L32
- F2 Known Limit #4:F3 新 slug 預設五站未切;`graph.yaml` 未改。另刀 F3:docs/dev/five-station-f2/7-review.md:L448
- 本 tree Active **空**(`目前無進行中的改版軌。`):docs/dev/STATUS.md:L32
- STATUS Backlog A **仍寫**「下一刀 F1 teeth＋dual-read annex」—— F1／F2 已出貨,此列是過期看板,不是「F3 沒立案」:docs/dev/STATUS.md:L50
- `#359` 是 STATUS companion(開 `five-station-f3` Active、不寫本目錄討論檔)。本 PR 不改 STATUS。
- live 路線閘:`f3_cut_happened()` **硬回 `False`**,註解寫 F2 never cuts:scripts/five_station_f2.py:L276-L278
- `allow_legacy()`:synthetic NEW5 例外;否則要 `declared(2.1)` ∧ ¬flying ∧ cut 才放五站。doctor／marketplace／cache 參數被丟棄,不是路條:scripts/five_station_f2.py:L281-L293
- 拒絕理由三岔:未宣告 2.1 →「路線未宣告 仍舊 7」;已有 1–7 `.md` →「仍舊 7 in-flight」;其餘 →「仍舊 7 F3 cut 未發生」:scripts/five_station_f2.py:L296-L307
- `has_old7`=該 slug 目錄已有 1–7 任一 `.md`(七個 stem 檔名):scripts/five_station_f2.py:L22-L32 scripts/five_station_f2.py:L271-L273
- live `contract_version()` 讀 JSON 鍵 `version` 或 `contract_version`;**不讀** `devflow_contract_version`。本 tree 該函式回傳空字串:scripts/five_station_f2.py:L260-L268
- 人看的契約檔鍵是 `devflow_contract_version`=`2.0.0`:devflow-contract.json:L1-L2
- runtime 只聲明支持 `2.0.0`:hooks/runtime-capabilities.json:L2-L4
- doctor 握手讀的是 `devflow_contract_version` ∈ `supported_contract_versions`,否則 fail-closed:hooks/_doctor_impl.py:L193-L202
- doctor 綠時印 `COMPATIBLE` 並 exit 0:hooks/_doctor_impl.py:L492-L500
- SLOT-UNDECLARED-ROUTE:未宣告 2.1.0 dual-read 時,採用端路線=舊 7;marketplace 包裝不能單獨改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L20
- SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS:契約仍 2.0.0 且 hops 已是五站預設 → 紅、不得改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24
- SLOT-DOCTOR-GREEN-MEANS:`COMPATIBLE`／exit 0 只證明握手。≠ 路線沒變,≠ 已切五站:notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28
- F2 Decision 3A:F2 **不改** `graph.yaml`;hop_id 用五站別名＋檔→五站觸發表;舊節點 `N7-g1` 不是 hop_id:docs/dev/five-station-f2/2-decision.md:L72
- 現行 Stage 2 graph 仍經 `N7-g1`:skills/dev-flow/stage2/graph.yaml:L53-L57
- F2 4-spec Out of Scope #1 把「guide／STATUS／graph 用語切五站」列成 F3,與 brief §7 本文(只寫 guide／STATUS)不完全同一句:docs/dev/five-station-f2/4-spec.md:L963 notes/design/five-station-simplify-brief-v3.md:L180
- F2 D-1:guide **檔案地圖列**≠ F3 cut 聲明:`EXPECTED_MAPPED_FILES` 加列不是切預設:docs/dev/five-station-f2/7-review.md:L445
- guide 用語仍「七站」:guides/guide-dev-flow.html:L209 guides/guide-dev-flow.html:L573
- marketplace 單一 entry `./`;更新=`marketplace update` + `plugin update`;plugin root 在 cache、隨版本變:skills/dev-setup/SKILL.md:L65-L71 .claude-plugin/marketplace.json:L9-L16
- F2 電池單一入口;exit 0=NEW5+OLD7 都綠:scripts/test-five-station-f2.sh:L1-L11
- 本 hop 已跑 `scripts/test-five-station-f2.sh`(2026-09-14,`origin/main` `2b6a9b2`):exit 0;`failed=0`;OLD7-TOKEN／OLD7-NO-FIVE／OLD7-SELF 綠。
- G1／G2／G3 token 牙仍在:scripts/check-gate-tokens.sh:L45-L61 scripts/check-gate-tokens.sh:L268
- 受影響面(本 hop 不動):`f3_cut_happened`、`devflow-contract.json`、`hooks/runtime-capabilities.json`、`guides/guide-dev-flow.html` 用語、各站 `graph.yaml`、gate token、in-flight slug 路線、F1／F2 已鎖 R／S、本目錄自己(一落檔即 in-flight)。STATUS 另 companion。

## Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 母版 owner(tony／rick) | 新 slug 預設五站;舊 slug 不被折;token 仍在 | 裁 brief、簽 gate | F0–F2 落盤、本 tree、F2 G3 PASS | cut 要用哪一個可讀記號才不算空切 | GitHub、Cursor chat |
| F3 討論／實作 agent | 把 cut 指認與三前置問清楚;本 hop 只寫討論 | 寫本目錄討論檔 | brief、F2 4A／S-8.1、路線閘碼 | 契約 bump 是否等於 cut | Cloud Agent、PR |
| 新 slug 寫手 | 開新工作就走五站,不要再付 7 個例行停點 | 寫 1／2／4／5／6 檔 | 模板、F2 coordinator | live 閘什麼時候放五站 | PR、chat |
| in-flight slug 執行者 | 走完手上舊 7,不被五站狀態寫入 | 既有 graph／模板 | 自己目錄已有 1–7 `.md` | F3 會不會改 `graph.yaml` 把舊節點拆掉 | 既有 hop |
| coordinator(已落地) | 三前置全真才建五站機;否則 `allow_legacy()` | 讀謂詞、寫倉、**禁**寫判定 | 表 A／B、狀態機、slug 倉 | `f3_cut_happened` 讀哪 | 無(live 仍硬假) |
| 採用專案 owner | 更新 plugin 後路線不要被遠端改 | 系統外(自己 repo 的契約檔) | 自己的 `devflow-contract.json`、doctor 輸出 | 母版 cut 之後,未 upgrade 會不會被拖走 | marketplace／plugin 指令、口頭 |
| doctor 操作者 | 看握手綠／紅 | 跑 `devflow-doctor.sh` | `COMPATIBLE`／`INCOMPATIBLE` 一行 | 綠 ≠ 路線;2.1.0 ∉ supported 會紅 | 終端機 |
| Ship 審查者 | 出貨樹=審過的樹;機械綠 ≠ PASS | 寫 7-review `verdict:` | G3 八點 | cut 有沒有把 Must-keep 一起摺掉 | 瀏覽器審頁 |
| 電池看守 | F3 之後 NEW5+OLD7 仍能獨立紅、也能一起綠 | 跑 `test-five-station-f2.sh` | 官方 18 CASE | cut 會不會讓 OLD7 路變空綠 | 終端機 |

## Real-world Context

### Actors
表見上節獨立 H2 `## Actors`。產檔器只吃該表的誰／要什麼／缺什麼;`#scan-people` 不捲 Journey 或 Assumption。

### Current Journey
正式 SOP(F3 後才預設):新 slug 進 Intake,coordinator 評謂詞 hop;已有 1–7 `.md` 的 slug 整段舊 7。實際做法(**現在、F3 尚未落地**)如下。兩者都記。現況圖只畫這段,不畫尚未發生的 cut 箱。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 母版 | 把 F2 coordinator／倉／電池合進 plugin | marketplace／git | — | `five_station_f2.py`;18 CASE 綠 | `f3_cut_happened` 硬假 |
| 2 | 新 slug 寫手 | 開 `docs/dev/<slug>/` | 本 repo | — | 空目錄或第一個 md | 預設仍舊 7 |
| 3 | coordinator | 問三前置 | `allow_legacy()` | — | `legacy` +「F3 cut 未發生」 | 碼在也不切 |
| 4 | 同一寫手 | 走完 1–7,在 G1／G2 停 | 既有 graph `N7-g1`／twin | owner 簽閘 | 舊 7 站檔 | 例行停點還在 |
| 5 | 採用 owner | `marketplace update` + doctor | plugin cache／`devflow-doctor.sh` | — | hops 已含 F2 碼;`COMPATIBLE` | 綠 ≠ cut |
| 6 | F2 電池 | 用合成 NEW5 假裝三前置全真 | `test-five-station-f2.sh` | — | `failed=0` | live 新 slug 走不進這條門 |
| 7 | owner／寫手 | chat「可以開 F3」 | Cursor chat | owner | 本討論檔 | 本 hop 不選定 cut 記號 |
| 8 | 本討論 | 把指認與三前置問成 OQ | 本檔 | 後續 F3 收斂 | 討論檔 | 本 hop 不翻閘 |

### Workarounds
- F2 用合成 fixture + `synthetic_new5=True` 繞過 live 三前置,才能打 NEW5 hop。live 新 slug 沒有這面旗。
- `f3_cut_happened()` 用硬編碼假充當「尚未 cut」;沒有可讀的 cut 正本。
- 採用端路線實際靠「人記得 brief §6」與「不要遠端改別人 repo」;F2 行為牙擋的是 coordinator,不是 doctor 文案。
- owner 用 chat 當「可以開 F3」開關。系統留下本討論檔,不留下「cut 已發生」記號。
- STATUS／HISTORY 當 hop log:Active 已空,Backlog A 仍停在「下一刀 F1」。#359 另開 Active,本 PR 不寫看板。
- 這些步驟常不留「新 slug 為什麼仍舊 7」或「哪一個檔被當成 cut」。

### Exceptions
- 已有 1–7 `.md` 的 slug(**含本目錄一落檔**)整段舊 7;F3 不得中途折。
- Fast lane 不是本包要廢;本 slug 是 full。
- F2 已寫 coordinator,但 F3 前預設路線仍舊 7——含本 slug、含其他 F0–F3 母版軌。
- F2 電池 NEW5 是合成 fixture,不是 live 預設翻轉的證據。
- `[Assumption]` 若把 cut 等同「契約檔寫 2.1.0」:live 閘讀的鍵不是 `devflow_contract_version`,naive bump 可能醫生綠／紅與路線閘各走各的。風險=高。
- `[Assumption]` 若把 cut 寫成 guide 一句:F2 已證檔案地圖加列 ≠ cut。風險=高。
- `[Assumption]` 若把 cut 寫成 STATUS 用語:本檔不得改 STATUS;看板已證明會 stale。風險=高。
- `[Assumption]` 改各站 `graph.yaml` 預設路徑=折 in-flight 的捷徑。風險=高。
- `[Assumption]` F3 之後 F2 電池仍必須綠;OLD7 路變空綠=假成功。風險=高;期限=Stage 2。
- `[Assumption]` NEW5 試體仍是合成 fixture,不是本 slug:風險=高;期限=Stage 2;過期擋把本目錄當白老鼠。

### Evidence
- F0／F1／F2 書面:brief-v3、狀態機、F1 annex、F2 2-decision／4-spec／7-review;Owner 已核准(檔頭)。本 hop 不改那些檔、不重開其 R／S。
- 本 tree 已核:上列 Context 出處(2026-09-14 讀過,行段支持斷言)。
- F2 已出貨:docs/dev/HISTORY.md:L719-L723。Active 空:docs/dev/STATUS.md:L32。Backlog A 過期:docs/dev/STATUS.md:L50。
- 路線閘／契約／doctor／graph／guide:上列 scripts／hooks／skills／guides 出處。
- 電池:`scripts/test-five-station-f2.sh` 本 hop 跑過,exit 0、`failed=0`。
- `[Assumption]` 見 Exceptions;cut 正本／採用升級逐字稿／F3 後 live 新 slug 皆無。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「cut = 只 bump 契約到 2.1.0」為假 → 需要獨立可讀記號,否則兩條前置塌成一條 | 高 | Stage 2 對帳:Decision 是否把 2.1.0 與 cut 寫成兩個可獨立假的位元 | Stage 2／收斂者;過期擋把「宣告 2.1.0 就是 cut」當已核 |
| 「live 閘讀得到 `devflow_contract_version`」為假 → naive bump 是空切 | 高 | 已核:本 tree `contract_version()` 回空字串。後站若仍只改人看的鍵、不改讀取,閘不翻 | F3 規格前／實作者;過期擋「檔寫 2.1.0 就算切了」 |
| 「guide 一句 = cut」為假 → 加列會重演 F2 D-1 | 高 | 對照 F2 S-8.1:檔案地圖列曾被明文標「非 F3 cut」 | Stage 2;過期擋把 guide 加句當唯一正本 |
| 「STATUS 用語 = cut」為假 → 看板 lag 會讓閘讀到過期真／假 | 高 | 本 tree Backlog A 仍指 F1;feature branch 禁改 STATUS | Stage 2;過期擋把看板當路線 SoT |
| 「改 `graph.yaml` 才能切預設」為假 → 可只翻閘、留舊節點給 in-flight | 高 | Stage 2 對帳:Decision 是否要求 graph Diff≠0 | Stage 2;過期擋「不改 graph 就不算 cut」 |
| 「F3 後電池可以紅」為假 → 折 OLD7／刪 token 會被空綠蓋住 | 高 | 同一入口仍要兩路可獨立紅、一起綠 | Stage 2／G3;過期擋「預設切了所以舊電池可丟」 |
| 「本 slug 可當 NEW5 白老鼠」為假 → 一有 `1-discussion.md` 就是 freeze | 高 | Files／fixture 路徑不含本目錄站檔當 hop 試體 | Stage 2;過期擋 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | 調查跟 brief／狀態機 | notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名) | 是 |
| F1 annex | 2.1.0／in-flight／doctor SLOT | notes/design/five-station-simplify-f1-dual-read-annex.md | 是(使用者點名) | 是 |
| F2 收斂／規格／出貨 | 三前置、S-8.1、G3 PASS、不重開 R／S | docs/dev/five-station-f2/2-decision.md、4-spec.md、7-review.md | 是(使用者點名) | 是 |
| Stage 1 模板 | 骨架與審頁 | _templates/1-discussion.md | 是(使用者點名) | 是 |
| F2 路線閘 | cut 硬假、三前置、契約讀取鍵 | scripts/five_station_f2.py | 是(本 tree;F2 指向) | 是 |
| 契約／runtime | 人看的鍵 vs 閘讀的鍵;supported 仍 2.0.0 | devflow-contract.json、hooks/runtime-capabilities.json | 是(本 tree) | 是 |
| doctor／marketplace | 綠=握手;update 換 hops | hooks/_doctor_impl.py、.claude-plugin/marketplace.json、skills/dev-setup/SKILL.md | 是(本 tree) | 是 |
| graph／guide | 舊節點仍在;用語仍七站;加列≠cut | skills/dev-flow/stage2/graph.yaml、guides/guide-dev-flow.html、F2 7-review D-1 | 是(本 tree) | 是 |
| F2 出貨＋看板 | Active 空;HISTORY G3 PASS;Backlog A 過期 | docs/dev/HISTORY.md、docs/dev/STATUS.md | 是(本 tree) | 是 |
| F2 電池 | 成功=兩路仍綠 | scripts/test-five-station-f2.sh(本 hop 已跑) | 是(本 tree) | 是 |
| 採用升級逐字稿 | 驗證「先 update 後 bump」 | 無;public repo 禁收公司路徑 | 禁 | 否 |

## Goals
- G-cut-1:人能指出**哪一個可讀記號**表示「F3 cut 已發生」;同一個記號也能被路線閘讀成真。本討論不選定記號。
- G-new-1:cut 之後,**尚未**有 1–7 `.md` 的新 slug 預設走五站(進 Intake,不先開舊 7 例行閘)。
- G-old-1:cut 當下已有 1–7 任一 `.md` 的 slug,整段仍舊 7,直到 Ship;不被寫入五站狀態。
- G-token-1:G1／G2／`ACCEPTED` token 與檔仍在;F1 牙回歸仍綠。
- G-battery-1:**同一電池** NEW5+OLD7 在 F3 之後仍能獨立變紅、也能一起綠。只證明「新 slug 走五站」或「檔在」≠ F3 完。
- G-honest-1:doctor 印 `COMPATIBLE`／exit 0,不足以當 cut。`marketplace update` 單獨發生,不足以改採用端路線。
- G-pre-1:F2 三前置仍是三條可獨立為假的位元。缺一條 → `allow_legacy()`。不把其中兩條默合併。
- G-self-1:本 slug 自己走到 G1／G2／G3 時仍是舊 7;沒有五站狀態寫入。
- G-rs-1:F1／F2 已鎖 R／S 不被本刀重開或改成可選。
- G-carry-1:本檔列出的 cut 指認題與 graph／三前置題,到規格時每條有去向,不能無聲消失。

## Requested solution
- F3 翻預設:新 slug 五站;in-flight 舊 7;舊 token 全留。
- **cut 怎麼被指認(契約 2.1.0／guide 一句／STATUS／翻 `f3_cut_happened`)本討論不選定。** 要能被指出,也要能被閘讀到。
- 三前置維持 AND:2.1.0 已宣告 ∧ ¬in-flight ∧ cut。doctor 綠／marketplace／cache 仍不是第四條。
- `graph.yaml` 改預設 vs 只翻閘、留舊節點給 dual-read —— 候選,未定案。
- F3 完=新 slug 五站 + 舊 slug 仍 7 + 電池仍綠 + token 在。
- 本 hop 不選定契約鍵名修法、不選定 graph Diff、不 bump、不改 STATUS。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`graph.yaml`、gate token、STATUS、HISTORY、契約版本、路線閘碼。
- 本 hop 不送 G1;status 留 draft;不宣稱 Human Stage1 PASS;不合併。
- **鎖:不折 in-flight;不刪 G1／G2／`ACCEPTED`;不重開 F1／F2 已鎖 R／S。**
- 不把本 slug 當新 5 的第一個白老鼠。NEW5 只准合成 fixture。本目錄一有 `1-discussion.md` = in-flight,整段舊 7 到 Ship。
- 不在本討論選定 cut 正本(那是 OQ,不是 Goal)。
- 不把「doctor 綠」或「marketplace update」寫成 cut。
- 不把「guide 加一句」或「STATUS 改用語」在未對帳前寫成已核 cut。
- 不把「檔在」或「F2 綠」寫成 F3 完成。
- 一次大爆炸改模板全文另開刀,不叫 F3。
- 不重開 F0 十條;不放寬 hop≤2／Decide≤1／Goal reopen≤1。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:full。本 slug 走舊 7 元流程(dogfood)
- [x] Q2:本 hop 是否只 Stage 1、不改 STATUS、不合併、不發明 G1?→ 原 brief:是。#359 是 STATUS companion,本 PR 不碰看板
- [x] Q3:F3 刀是否=新 slug 預設五站、in-flight 仍舊 7、不刪 token?→ brief §7;翻=新 brief
- [x] Q4:本 slug 是否仍走舊 7、不得當 NEW5 白老鼠?→ brief §6 + OC-9。本目錄一有 1–7 `.md` = in-flight
- [x] Q5:可否重開 F1／F2 已鎖 R／S?→ 否。本刀另開 slug,不改那些檔的 R／S
- [x] Q6:marketplace × doctor 誠實是否仍是約束、不是路條?→ 是。SLOT-DOCTOR-GREEN-MEANS／SLOT-UNDECLARED-ROUTE;F2 4A／S-3.x 已鎖,本討論不重開
- [x] Q7:F3 成功是否=新 slug 五站 + 舊 slug 仍 7 + 同一電池仍綠 + token 在?→ 是。缺一路或 token 沒了=假成功
- [>] Q8:cut 怎麼被**指認**?人看的契約 `2.1.0`／guide 一句／STATUS 用語／把 `f3_cut_happened()` 從硬假翻真／以上組合?本討論不選。移交 F3 收斂
- [~] Q9:若 cut 只等於「契約已宣告 2.1.0」,三前置是否塌成兩條(2.1.0 與 cut 同一位元)?(帶假設:**會塌**;暫定值=cut 必須是可獨立為假的第三位元;風險=高;期限=F3 Decision,過期不得把「宣告就是 cut」當已核)
- [>] Q10:live `contract_version()` 不讀 `devflow_contract_version`(本 tree 回空字串)。只改人看的鍵到 2.1.0,閘會不會仍當未宣告?與 Q8／Q11 綁。移交 F3
- [>] Q11:若 bump 契約到 2.1.0,`supported_contract_versions` 仍只 `2.0.0` → doctor 變 INCOMPATIBLE。這是可接受的誠實紅,還是 cut 必須連 supported 一起加?與 Q8 綁。移交 F3
- [>] Q12:`graph.yaml` 要不要改預設路徑?改了,in-flight 還走不走 `N7-g1`?不改,只翻閘 + 留舊節點,算不算 brief「guide／STATUS 用語切五站」?F2 4-spec 把 graph 用語列進 F3,brief §7 本文沒寫 graph。移交 F3
- [>] Q13:STATUS 用語能否當 cut 正本?feature branch 禁改 STATUS;本 tree Backlog A 已 stale;companion 與討論不同 PR。移交 F3(與 Q8 綁)
- [~] Q14:F3 之後三前置是否仍要 AND(2.1.0 ∧ ¬in-flight ∧ cut),F3 只負責把 cut 位元翻真?(帶假設:**是**;本討論不發明第四條,也不刪第二條 in-flight;期限=F3 Decision)
- [x] Q15:F2 電池在 F3 之後可否變紅或被丟?→ 否。G-battery-1;舊 7 路必須仍能獨立紅

## Constraints
- 本 PR 不宣稱 G1 PASS、不宣稱 Human Stage1 PASS;不改 STATUS／HISTORY。
- 討論盲下游:本檔不指定腳本／API／元件當目標;cut 記號只寫成 OQ。
- **Owner-locked F3 刀:**新 slug 預設五站;舊 7 只 freeze + dual-read;不刪閘;不折 in-flight。
- **Owner-locked 本 slug 路線:**舊 7 到 Ship。不是 NEW5 白老鼠。
- **Owner-locked:不重開 F1／F2 R／S。** 不放寬三 cap。
- **Owner-locked:Must-keep 未綠不得 hop。** 摺的是例行停點,不是完整度。
- **採用 hop 身分:**graph／hooks 住方法包。未宣告 2.1.0 之前,marketplace 可換 hops 而 doctor 仍可因 `2.0.0` 握手綠。綠 ≠ 切線。
- **F2 三前置是約束繼承,不是本討論重開的 Decision。** Q9／Q14 過期 → 擋本 slug G2。
- 詞條(語言,不是方案):**cut 指認**=哪一個可讀記號讓人與閘同時承認「預設已翻」。**空切**=人看的檔寫了五站／2.1.0,閘仍 `allow_legacy()`。**三前置**=2.1.0 ∧ ¬in-flight ∧ cut,三條可獨立為假。**in-flight freeze**=已有 1–7 `.md` 的 slug 走舊 7。**dual-read**=同一電池的 NEW5(合成 fixture)與 OLD7(不折、token 在)。**doctor 誠實**=綠只證明握手。**升級陷阱**=plugin 與契約不同步、或把綠當切線。本 hop 不寫進長期記憶。

### F3 移交種子(不是施工)
- Q8／Q10／Q11／Q13 是 cut 指認家族。維持未鎖。
- Q9／Q14 過期 → 擋本 slug G2(不得把「宣告就是 cut」或「砍掉 in-flight 位元」升格成已核)。
- Q12 是 graph vs dual-read;與「不折 in-flight」綁。
- Q6／Q7／Q15 已解;後站不得把 doctor 綠當 cut、不得把電池標可選。
- 本資料夾已有本檔 = 已 in-flight;後站不得對自己開五站機。

## 驗收雛形
- AC-1(G-new-1):假設 F3 cut 已發生且某 slug 目錄尚無 1–7 `.md`,當寫手開這個新 slug,則路線是五站(進 Intake),不是舊 7 例行 G1。
  - 從哪看:該 slug 的路線判定(人可指的閘輸出或紀錄;不預填通道)
  - 看到什麼算對:判定=五站／`Intake`;拒絕理由不是「F3 cut 未發生」
  - 拿什麼試:F3 之後造的空 slug;不是本目錄
- AC-2(G-old-1):假設 cut 當下 `docs/dev/<old>/` 已有任一 1–7 `.md`,當 coordinator 被求建五站機,則 `allow_legacy()`;無五站狀態寫入。
  - 從哪看:該目錄 + 路線拒絕理由
  - 看到什麼算對:理由含 in-flight／仍舊 7;無 `.five-station` 寫入
  - 拿什麼試:既有 OLD7 fixture 或任一已有站檔的 live slug;含本目錄
- AC-3(G-token-1):假設 F3 宣稱完成,當人跑 token 牙與 F1 十二群,則 G1／G2／`ACCEPTED` 檔仍在,F1 仍綠。
  - 從哪看:`scripts/check-gate-tokens.sh` + `scripts/test-five-station-f1.sh`
  - 看到什麼算對:兩路 exit 0;token 未刪未改名
  - 拿什麼試:本 tree 現況牙
- AC-4(G-battery-1):假設 F3 宣稱完成,當人跑同一入口 F2 電池,則 NEW5 與 OLD7 仍能獨立紅、也能一起綠。
  - 從哪看:`scripts/test-five-station-f2.sh` stdout／exit
  - 看到什麼算對:整電池 exit 0;`--only new5|old7|f1` 仍非 0;OLD7-FOLD-RED／OLD7-TOKEN 仍能紅／綠
  - 拿什麼試:現成 F2 電池;不是另造「只打新 slug」的開心腳本
- AC-5(G-self-1):假設本 slug 被求切五站自動前進,當看本目錄,則仍是舊 7 站檔與例行閘,沒有五站狀態。
  - 從哪看:本目錄 1–7 `.md` 與被拒絕的 hop
  - 看到什麼算對:有 `1-discussion.md`;無五站機寫入
  - 拿什麼試:本資料夾(本 hop 落檔即 in-flight)
- AC-6(G-honest-1):假設採用端 doctor 剛印 `COMPATIBLE` 且只做了 `marketplace update`,當有人把這兩件事當 cut,則路線仍舊 7(或未宣告)。
  - 從哪看:該次路線判定 + 拒絕理由
  - 看到什麼算對:理由是未宣告／cut 未發生,不是「doctor 已綠」
  - 拿什麼試:本 tree 現況(契約 2.0.0 + doctor 可綠 + F2 碼已在)
- AC-7(G-cut-1／G-pre-1):假設人問「cut 發生了沒」,當看選定的可讀記號與閘,則兩者同一答案;把 2.1.0 關掉或把 cut 關掉可以**分開**讓閘回舊 7。
  - 從哪看:記號本體 + `allow_legacy`／拒絕理由
  - 看到什麼算對:三岔理由仍能分別指出未宣告／in-flight／cut 未發生;不是一個 bump 吃掉兩條
  - 拿什麼試:後續造;本 hop 不選記號
- AC-8(G-rs-1／G-carry-1):假設本檔 Q8–Q15 列了一題,當人讀到 F3 Decision／Spec,則該題有去向;F1／F2 的 R／S 列未被改寫。
  - 從哪看:Stage 2 對帳 + F1／F2 4-spec diff
  - 看到什麼算對:每條高影響 OQ 有處理／Non-Goal／仍待驗;F1／F2 R／S 檔 Diff=0
  - 拿什麼試:Q8 指認、Q9 塌位元、Q12 graph、Q14 三前置 AND

## 現況圖
誰:寫手
做什麼:開新 slug
工具:docs/dev/<slug>/
痛點:預設仍舊7
↓
誰:路線閘
做什麼:三前置缺cut
工具:allow_legacy
痛點:F2碼在也不切
↓
誰:同一寫手
做什麼:走完7站等人
工具:G1/G2 twin
痛點:例行停點還在

## 邏輯圖(ASCII)
```
now
|-- F2 G3 PASS              [coordinator+store+battery]
|-- contract file 2.0.0     [devflow_contract_version]
|-- gate reader ''          [reads version/contract_version]
|-- f3_cut_happened=False   [hardcoded]
|-- allow_legacy            [new slug still old 7]
|-- doctor COMPATIBLE       [handshake != cut]
|-- graph N7-g1             [unchanged]
|-- guide says 七站
|-- STATUS Active empty
+-- Backlog A               [stale: still says next=F1]

cut-attestation            [OPEN; Q8-Q11 Q13]
|-- contract 2.1.0          [may collapse Q9]
|-- guide sentence          [D-1: filemap != cut]
|-- STATUS language         [companion-only; can lag]
|-- flip f3_cut_happened    [gate-readable]
+-- naive bump              [hollow if reader still '']

three-pre                  [2.1.0 AND not-inflight AND cut]
|-- drop any bit            [allow_legacy]
|-- merge 2.1.0==cut        [Q9; OPEN]
+-- cache/doctor/market     [never a fourth]

graph-vs-dual              [OPEN; Q12]
|-- change graph.yaml       [risk fold in-flight]
+-- keep N7-g1 + flip gate  [dual-read keep]

f3-must-prove
|-- new slug                [no 1-7 md => five]
|-- old slug                [has 1-7 md => old 7]
|-- tokens stay
|-- F2 battery still green  [each path can red]
+-- this slug               [old 7 / in-flight]

fail
|-- fold in-flight          -> X4
|-- delete tokens           -> new brief
|-- doctor green as cut     -> SLOT lie
|-- reopen F1/F2 R/S        -> Non-Goal
|-- this dir as NEW5        -> RP-15
|-- battery dropped         -> hollow F3
+-- empty cut               -> file says 2.1; gate still legacy
```

## Interview Log(推理鏈外顯)
- Q:F3 這一刀到底做什麼、本討論為什麼不准折舊 slug?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L180-L182 notes/design/five-station-simplify-brief-v3.md:L165 notes/design/five-station-simplify-f0-state-machine.md:L49-L50
  - 推理:brief 把 coordinator(F2)與預設翻轉(F3)拆成兩刀。in-flight 偵測只認 1–7 `.md`。本資料夾一有站檔就是 freeze,機不該建立。
  - 結論:CONFIRMED F3=cut 新預設五站;舊 7 只 freeze+dual-read;不刪 token;本 slug 舊 7。
- ⚠️ Q:cut 為什麼不能直接寫成「bump 契約到 2.1.0」?
  - 事實:docs/dev/five-station-f2/2-decision.md:L79 scripts/five_station_f2.py:L276-L293 scripts/five_station_f2.py:L260-L268 devflow-contract.json:L1-L2
  - 推理:F2 把 2.1.0 與 cut 寫成 AND 的兩條。若 cut=宣告,兩條塌成一條,in-flight 以外只剩一個位元。更糟:閘讀的鍵不是人看的 `devflow_contract_version`,本 tree 讀到空字串。只改檔上的 2.1.0,閘仍可當未宣告。
  - 結論:OPEN Q8／Q9／Q10。本討論不選定正本;`[~]` 暫定 cut 必須可獨立為假。
- ⚠️ Q:guide 一句或 STATUS 用語夠不夠當 cut?
  - 事實:docs/dev/five-station-f2/7-review.md:L445 docs/dev/five-station-f2/7-review.md:L448 docs/dev/STATUS.md:L32 docs/dev/STATUS.md:L50 guides/guide-dev-flow.html:L209
  - 推理:F2 D-1 已把 guide 檔案地圖加列標成「非 F3 cut」。STATUS 本 PR 不能寫,且 Backlog A 已證明看板會停在過期的「下一刀 F1」。閘今天讀的是硬編碼假,不是這兩份散文。
  - 結論:NEEDS_VERIFICATION Q8／Q13;散文可以是人讀的宣告,未必是閘讀的正本。
- Q:F3 之後三前置還要三條嗎?
  - 事實:docs/dev/five-station-f2/4-spec.md:L757-L760 scripts/five_station_f2.py:L296-L307 docs/dev/five-station-f2/2-decision.md:L207
  - 推理:拒絕理由已經分三岔。F2 寫過:少「cut 已發生」這條,F2 會在母版軌上提前切線。F3 若刪 in-flight 位元,freeze 死。F3 若把 2.1.0 與 cut 合併,採用端未 upgrade 的保護與「母版已 cut」分不開。
  - 結論:NEEDS_VERIFICATION Q14 `[~]` 仍 AND;Q9 擋合併。不發明第四條。
- ⚠️ Q:要不要改 `graph.yaml` 才算切預設?
  - 事實:notes/design/five-station-simplify-f0-state-machine.md:L10-L15 docs/dev/five-station-f2/2-decision.md:L72 skills/dev-flow/stage2/graph.yaml:L53-L57 docs/dev/five-station-f2/4-spec.md:L963 notes/design/five-station-simplify-brief-v3.md:L180
  - 推理:舊 7 in-flight 的 hop 正本是既有 graph。F2 刻意不改 graph、用別名觸發表。brief §7 本文寫 guide／STATUS,沒寫改 graph;F2 Out of Scope 卻把 graph 用語列進 F3。改預設路徑可能讓仍走 `N7-g1` 的 in-flight 斷線;不改又怕有人說「沒切」。
  - 結論:OPEN Q12。候選=改 graph vs 只翻閘留舊節點。本討論不選。
- Q:marketplace 更新、doctor 綠了,為什麼仍不能當 cut?(約束,不是新功能)
  - 事實:notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L28 hooks/_doctor_impl.py:L193-L202 hooks/_doctor_impl.py:L492-L500 scripts/five_station_f2.py:L289-L290
  - 推理:hops 住方法包,update 換 cache。doctor 綠只證明 `2.0.0 ∈ supported`。F2 已把這兩件事從參數列表丟棄。F3 若用綠當 cut,SLOT 變裝飾,採用端未 upgrade 會被遠端改線。
  - 結論:CONFIRMED Q6;綠 ≠ cut。Q11 另問 bump 2.1.0 時 supported 要不要一起加。
- Q:F3 完為什麼不能等於「新 slug 走五站」或「F2 還綠」?
  - 事實:docs/dev/five-station-f2/2-decision.md:L86 scripts/test-five-station-f2.sh:L10 docs/dev/five-station-f2/7-review.md:L448
  - 推理:只測新 slug 會讓 in-flight 被折、token 被刪而看起來「切成功」。F2 電池已經能量這兩路。F3 把預設翻轉之後,這顆電池必須仍綠,否則 hollow 換皮。
  - 結論:CONFIRMED Q7／Q15／G-battery-1。
- Q:本 slug 會不會把自己當五站白老鼠?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L165-L166 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32 scripts/five_station_f2.py:L271-L273
  - 推理:本檔落盤後目錄已有 `1-discussion.md`。偵測規則只認 1–7 `.md`。整段舊 7 到 Ship。對本目錄建五站機=RP-15。
  - 結論:CONFIRMED Q4／G-self-1;dogfood 舊 7,不是 NEW5。
- ⚠️ Q:本 hop 有沒有偷選 cut 或偷改 graph?(盲點)
  - 事實:本 hop brief(只 Stage 1、本 PR 不改 STATUS、不發明 G1)。scripts/five_station_f2.py:L276-L278
  - 推理:Requested solution 只列候選。Q8 維持 `[>]`。隱含預設(cut 獨立於 2.1.0、三前置仍 AND)已標 `[~]` 與期限。不改閘、不 bump、不改 graph。
  - 結論:CONFIRMED 本檔只落討論;不選正本;不切線;不鎖鍵名。Q9／Q14 過期擋本 slug G2。不宣稱 Human Stage1／G1。
- ⚠️ Q:現況圖為什麼不能畫「F3 已切、新 slug 進 Intake」?
  - 事實:scripts/five_station_f2.py:L276-L293 docs/dev/five-station-f2/7-review.md:L448 本 hop 已跑電池 failed=0
  - 推理:審頁三框吃的是 Current Journey,不是未來成功故事。cut 箱是虛構。CURRENT=開新 slug → 閘因缺 cut 仍 legacy → 寫手付 7 站例行停點。
  - 結論:CONFIRMED 現況圖三框只畫現況;未來 cut 留在邏輯圖 `cut-attestation` 枝。
