---
feature: five-station-f3
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 1. 討論 — 五站 F3（Implementer B：Cut attestation／三前置／graph vs dual-read）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／狀態機／F1 annex／F2 G3 PASS,不是現場一問一答。
> Lane = **full**。本檔 **只 Stage 1 討論**；status 留 **draft**；**不送 G1**、不宣稱 Human Stage1 PASS。本 PR 不改 STATUS／HISTORY。
> 原料:brief-v3 §6–§7、F0 狀態機、F1 annex、F2 4A／OC-4／OC-12、`scripts/five_station_f2.py`、`_templates/1-discussion.md`。
> B 線只挖五件事:①cut **怎麼證明發生過**;②F2 **三前置** cut 之後還是不是三條;③**graph 預設 hop** vs **dual-read 2.1.0**;④**doctor 約束**;⑤F3 **完成判準**。
> F3 刀(brief §7):**Cut** —— 新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide／STATUS 用語切五站。不做:刪 G1／G2／`ACCEPTED`;改已經 freeze 的 slug;一次大爆炸改模板全文。F3 之後 token **仍在**。本 slug **dogfood 舊 7** 到 Ship。

## Problem
痛:F2 coordinator 已 G3 PASS,NEW5 合成 fixture 能 hop,但 live 新 slug 預設仍舊 7。`f3_cut_happened` 恆 `False`;三前置(2.1.0 ∧ ¬in-flight ∧ cut)在 live 樹永遠缺第三條,常常連第一條也缺。寫手開新 feature 仍走 `N7-g1`／`N6-g2` 等人;doctor 仍可印 `COMPATIBLE`;F2 電池綠 ≠ 預設已切。F2 自己把「新 slug 預設五站」鎖成 Out,完成樹沒有 cut 聲明。
現在怎麼繞:新 slug 靠 chat／手開下一站;coordinator 對 live 一律 `allow_legacy()`;五站 hop 只打合成 fixture;STATUS Backlog A 仍寫「下一刀 F1」。本討論只把 cut 怎麼證、三前置怎麼留、graph 動不動、doctor 綠能不能當票、什麼叫 F3 完,問成 OQ。

## Context(已知事實)
- F3 刀=Cut:新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide／STATUS 用語切五站。不做:刪 G1／G2／`ACCEPTED`;改已經 freeze 的 slug;一次大爆炸改模板全文:notes/design/five-station-simplify-brief-v3.md:L180-L182
- F3 之後 token 與檔仍在;刪它們=新 brief,不是本切法的尾巴:notes/design/five-station-simplify-brief-v3.md:L182
- in-flight freeze:`docs/dev/<slug>/` 在 F3 cut 當下已有任一 1–7 `.md` → 整段舊 7 到 Ship;不准中途切五站:notes/design/five-station-simplify-brief-v3.md:L165 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32
- F0–F2 期間新開的母版改版軌仍走舊 7;F3 cut 之後才預設五站:notes/design/five-station-simplify-brief-v3.md:L166
- 採用專案 upgrade 到 2.1.0 之後才看五站;未 upgrade = 舊 7;不得遠端改別人 repo 的路線:notes/design/five-station-simplify-brief-v3.md:L168
- F0 十條已鎖;OC-9 freeze;OC-10 F0–F3 都不刪 token;F0 不改模板／gates／graphs:notes/design/five-station-simplify-brief-v3.md:L30-L45
- Idle:新 slug 在 F3 前仍開舊 7、不進五站機;F3 後進 Intake:notes/design/five-station-simplify-f0-state-machine.md:L37
- 本機不管舊 7 in-flight hop;那些仍走既有 `graph.yaml`:notes/design/five-station-simplify-f0-state-machine.md:L10-L15
- in-flight freeze:slug 已有舊 7 檔 → 不建立本機;coordinator 放手給既有 graph:notes/design/five-station-simplify-f0-state-machine.md:L49-L50
- SLOT-UNDECLARED-ROUTE:未宣告 2.1.0 時採用端路線=舊 7;marketplace 不能單獨改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L20
- SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS:契約仍 2.0.0 且 hops 已是五站預設 → 紅、不得改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24
- SLOT-DOCTOR-GREEN-MEANS:`COMPATIBLE`／exit 0 只證明握手(`2.0.0 ∈ supported`);≠ 路線沒變,≠ 已切五站:notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28
- F2 選定 4A:三前置全要=契約已宣告 2.1.0 ∧ 非 in-flight ∧ **F3 cut 已發生**;缺一 → `allow_legacy()`;doctor／marketplace／cache 不是第四條:docs/dev/five-station-f2/2-decision.md:L79
- F2 OC-4 把 Q17 三前置升格為 Decision;少「F3 已 cut」會在 F0–F2 母版軌提前切線:docs/dev/five-station-f2/2-decision.md:L292
- F2 OC-12:coordinator 準存在,但 F3 前對 live slug 禁評五站謂詞;碼可合進 plugin,預設仍舊 7:docs/dev/five-station-f2/2-decision.md:L300
- F2 S-7.1:三前置缺一條就 `allow_legacy()`;不建五站機;不套三 cap:docs/dev/five-station-f2/4-spec.md:L757-L761
- F2 S-8.1:F2 完成樹無 F3 cut 把新 slug 預設改五站;guide／STATUS 用語未切五站;後站不准把 F3 改成 In:docs/dev/five-station-f2/4-spec.md:L826-L831
- F2 入口是 `scripts/test-five-station-f2.sh` 家族,不是 F3 cut、不是改 `graph.yaml`、不是 bump 契約:docs/dev/five-station-f2/5-tasks.md:L26
- 現行 `f3_cut_happened` 讀樹被允許,但函式本體恆 `return False`;註解寫「F2 never cuts… we do not invent a cut」:scripts/five_station_f2.py:L276-L278
- `allow_legacy`:synthetic NEW5 例外;否則要 `declared(2.1)` ∧ ¬flying ∧ cut 才回五站;doctor／marketplace／cache 被丟棄:scripts/five_station_f2.py:L281-L293
- 拒 hop 理由是「路線未宣告 仍舊 7」／「仍舊 7 in-flight」／「仍舊 7 F3 cut 未發生」,不是「doctor 已綠」:scripts/five_station_f2.py:L296-L307
- F2 `contract_version()` 讀專案樹 `version` 或 `contract_version`;空字串也不算 2.1:scripts/five_station_f2.py:L260-L268
- 現行契約正本鍵是 `devflow_contract_version`=`2.0.0`,不是 `version`／`contract_version`:devflow-contract.json:L1-L3
- runtime 只聲明支持 `2.0.0`:hooks/runtime-capabilities.json:L1-L4
- doctor 握手讀 `devflow_contract_version` ∈ `supported_contract_versions`,否則 fail-closed:hooks/_doctor_impl.py:L193-L202
- doctor 綠印 `COMPATIBLE` 並 exit 0:hooks/_doctor_impl.py:L492-L500
- Stage 2 預設路經 `N7-g1`(例行人類停點):skills/dev-flow/stage2/graph.yaml:L53-L57
- Stage 4 預設路經 `N6-g2`:skills/dev-flow/stage4/graph.yaml:L93-L98
- F2 S-2.7:完成樹相對基準零 `graph.yaml` diff:docs/dev/five-station-f2/7-review.md:L72
- F1 G3 PASS、Active 已移出:docs/dev/HISTORY.md:L659-L663 docs/dev/five-station-simplify/7-review.md:L1-L12
- F2 coordinator G3 PASS;owner chat「G3過」;park D-1／D-2／D-3／F-c-4;**no F3 opened**:docs/dev/HISTORY.md:L719-L723 docs/dev/five-station-f2/7-review.md:L1-L12 docs/dev/five-station-f2/7-review.md:L32
- 本 tree Active **空**:docs/dev/STATUS.md:L32
- STATUS Backlog A **仍寫**「下一刀 F1 teeth＋dual-read annex」—— F1／F2 已出貨,此列是過期看板,不是「F3 已 cut」:docs/dev/STATUS.md:L50
- Gate token 仍釘 G1／G2／G3 物質句:scripts/check-gate-tokens.sh:L44-L60
- 受影響面(本 hop 不動):`f3_cut_happened`、`allow_legacy`、各站 `graph.yaml`、`devflow-contract.json`、`hooks/_doctor_impl.py`、`hooks/runtime-capabilities.json`、guide／STATUS 用語、各 in-flight slug 的路線、本目錄自己(一落檔即 in-flight)。

## Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 母版 owner(tony／rick) | 新 slug 預設五站,但不折舊 7、不刪 token | 裁 brief、簽 gate | F0–F2 落盤、本 tree | cut 用哪份樹證據才算「已發生」 | GitHub、Cursor chat |
| F3 討論／實作 agent | 把 cut 證明與三前置問清楚;本 hop 只寫討論 | 寫本目錄討論檔 | brief、F2 4A、`five_station_f2.py` | graph 改了會不會拖走 in-flight | Cloud Agent、PR |
| 下一站寫手 | 謂詞真就寫下一站,不要等「要不要繼續」 | 寫 2／4／5／6 檔 | 模板、F2 coordinator | live 新 slug 何時不再走 N7-g1 | PR、chat |
| coordinator(已落地,cut 未翻) | 三前置全真才建五站機;否則 `allow_legacy()` | 讀謂詞、寫事件、**禁**寫判定 | 表 A／B、`f3_cut_happened` | 恆 False 要讀樹的哪一格 | `scripts/five_station_f2.py` |
| 採用專案 owner | 更新 plugin 後路線不要被遠端改 | 系統外(自己 repo 的契約檔) | 自己的 `devflow-contract.json`、doctor 輸出 | 2.0.0 + 五站 hops 預設誰說了算 | marketplace／plugin 指令、口頭 |
| in-flight slug 執行者 | 走完手上舊 7,不被 F3 cut 折成五站 | 既有 graph／模板 | 自己目錄已有 1–7 `.md` | 共用 `graph.yaml` 被改預設時自己還走哪 | 既有 hop |
| 本 slug 執行者 | 用舊 7 跑完 F3 自己;不當新 5 白老鼠 | 舊 7 graph／G1／G2／G3 | 本目錄將有 `1-discussion.md` | 後站會不會對自己開五站機 | Cloud Agent、PR |
| doctor 操作者 | 看握手綠／紅 | 跑 `devflow-doctor.sh` | `COMPATIBLE`／`INCOMPATIBLE` 一行 | 綠 ≠ cut;2.1.0 握手 ≠ 五站 | 終端機 |
| Ship 審查者 | 出貨樹=審過的樹;機械綠 ≠ PASS | 寫 7-review `verdict:` | G3 八點 | hop 有沒有跳過 Must-keep | 瀏覽器審頁 |

## Real-world Context

### Actors
表見上節獨立 H2 `## Actors`。產檔器只吃該表的誰／要什麼／缺什麼;`#scan-people` 不捲 Journey 或 Assumption。

### Current Journey
正式 SOP(F3 後才預設):新 slug Idle→Intake,coordinator 評謂詞 hop;in-flight 仍舊 7。實際做法(**現在、F3 尚未 cut**)如下。兩者都記。現況圖只畫這段,不畫尚未發生的 cut 箱。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 母版 | 把 F2 coordinator 合進 plugin | marketplace／git | — | `five_station_f2.py`;`f3_cut_happened`≡False | live 新 slug 不進五站機 |
| 2 | 新 slug 寫手 | 開 `docs/dev/<新slug>/1-discussion.md` | 舊 7 graph `N7-g1`／`N6-g2` | owner 簽 G1／G2 | 舊 7 站檔 | F2 完仍等人 |
| 3 | coordinator | 評三前置 | `allow_legacy` | — | `仍舊 7 F3 cut 未發生` | 第三條恆假;常連 2.1.0 也缺 |
| 4 | 同一人 | 跑 doctor | `devflow-doctor.sh` | — | `COMPATIBLE` + exit 0 | 綠只證明 `2.0.0 ∈ supported`≠cut |
| 5 | `[Assumption]` 採用寫手 | 把綠或「F2 電池綠」讀成已切五站 | chat／README | — | 可能寫出 F1 已紅的那句 | 文案牙紅、預設行為還沒切 |
| 6 | in-flight 執行者 | 仍走既有 graph | `graph.yaml` | owner 簽閘 | G1／G2 twin | 若 F3 改共用 graph 預設,自己可能被折 |
| 7 | 看板 | Backlog A 仍指 F1 | STATUS.md | — | 過期列 | 用語未切五站;不能當 cut 證明 |
| 8 | 本討論 | 把證明／前置／graph／doctor／完成問成 OQ | 本檔 | 後續 F3 收斂 | 討論檔 | 本 hop 不選定 attestation |

### Workarounds
- F2 用合成 NEW5 fixture 證明 hop;live 樹靠 `f3_cut_happened`≡False 自保。沒有「cut 已發生」的樹證據。
- 新 slug 下一站靠 chat「可以開下一站」。系統留下站檔,不留下「三前置哪一條為真」。
- doctor 綠當「我更新了」的畫面;F1 牙只咬寫出來的謊,不切預設。
- STATUS／HISTORY 當 hop log:人記得改看板,看板可以停在「下一刀 F1」。
- 這些步驟常不留「這次 cut 讀了樹的哪一格」或「graph 預設改了之後 in-flight 還走哪份 hops」。

### Exceptions
- 舊 7 與 in-flight **不套**三個 cap;它們走既有 T 嘗試上限 4。
- Fast lane 不是本包要廢;本 slug 是 full、且自己走舊 7。
- F2 coordinator 碼已在 plugin;F3 前(含本討論落檔當下)live 一律舊 7。
- NEW5 試體是合成 fixture,不是本 slug、也不是 `five-station-simplify`／`five-station-f2`。
- `[Assumption]` 採用端典型升級=先 marketplace update、後(或不)bump 契約:無採用逐字稿;風險=高。
- `[Assumption]` 只翻 `f3_cut_happened` 為 True、契約仍 2.0.0 → 第一前置仍假,live 新 slug 仍舊 7:風險=高。
- `[Assumption]` 改共用 `graph.yaml` 預設、不留舊 7 fork → in-flight 被折:風險=高。
- `[Assumption]` 把 doctor 學會 2.1.0 當成 cut → SLOT-DOCTOR-GREEN-MEANS 復活:風險=高。
- `[Assumption]` `f3_cut_happened()==True` 或「檔在」= F3 完:風險=高;期限=Stage 2;過期擋 hollow。

### Evidence
- F0／F1／F2 書面:brief-v3、狀態機、F1 annex、F2 Decision／4-spec／5-tasks／7-review;Owner 已核准(檔頭)。本 hop 不改那些檔。
- 本 tree 已核:上列 Context 出處(2026-09-14 讀過,行段支持斷言)。
- F1／F2 已出貨:docs/dev/HISTORY.md:L659-L663、L719-L723。Active 空:docs/dev/STATUS.md:L32。Backlog A 過期:docs/dev/STATUS.md:L50。
- cut 恆假／三前置／doctor 鍵:上列 `five_station_f2.py`／契約／doctor 出處。
- `[Assumption]` 見 Exceptions;cut 樹證據／採用升級逐字稿／graph 雙 fork 皆無。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「三前置 cut 後仍要三條」為假 → cut 單獨就能讓未宣告 2.1.0 的 live 新 slug 切五站 | 高 | Stage 2 對帳:Decision 是否仍寫 2.1.0 ∧ ¬in-flight ∧ cut | F3 Decision／owner;過期擋把兩前置當已核 |
| 「cut attestation 必須樹可讀,不是 chat／STATUS 一句」為假 → 看板用語切五站就可當 cut | 高 | 指出 `f3_cut_happened` 讀哪一格;STATUS 過期列能不能翻 True | F3 Decision;過期不得把 Backlog 改口當已核 cut |
| 「改共用 graph 預設會折 in-flight」為假 → F3 可直接改 `graph.yaml` 預設 hop | 高 | 已有 1–7 `.md` 的 slug 在 graph 預設改後是否仍走 N7-g1／N6-g2 | Stage 2／收斂者;過期擋「順便改 graph」 |
| 「doctor 學會 2.1.0 = 握手,不是 cut」為假 → 綠變成路條 | 高 | doctor 綠之後 coordinator 是否仍先問三前置 | F3 Decision;過期擋「COMPATIBLE 所以已切」 |
| 「布林翻 True = F3 完」為假 → 必須另有可量測成功 | 高 | Decision／Spec 有無把 hollow 標成完成 | Stage 2;過期擋 G2 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | F3 刀與 freeze／禁刪 | notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名 F0/F1) | 是 |
| F1 annex | dual-read／doctor SLOT | notes/design/five-station-simplify-f1-dual-read-annex.md | 是(使用者點名) | 是 |
| F2 出貨 | 三前置、cut 恆假、S-8.1 | docs/dev/five-station-f2/2-decision.md、4-spec.md、5-tasks.md、7-review.md、scripts/five_station_f2.py | 是(使用者點名 F2) | 是 |
| Stage 1 模板 | 骨架與審頁 | _templates/1-discussion.md | 是(本 hop 模板) | 是 |
| 契約／doctor／graph | 2.0.0 握手;N7-g1／N6-g2 仍在 | devflow-contract.json、hooks/runtime-capabilities.json、hooks/_doctor_impl.py、skills/dev-flow/stage2/graph.yaml、skills/dev-flow/stage4/graph.yaml | 是(本 tree;annex／F2 指向) | 是 |
| 出貨＋看板 | F1／F2 G3 PASS;Active 空;Backlog A 過期 | docs/dev/HISTORY.md、docs/dev/STATUS.md、docs/dev/five-station-simplify/7-review.md | 是(本 tree) | 是 |
| 採用升級逐字稿 | 驗證「先 update 後 bump」 | 無;public repo 禁收公司路徑 | 禁 | 否 |

## Goals
- G-cut-1:F3 做完之後,一個**尚無** 1–7 `.md` 的新 slug,預設走五站,不再以例行 G1／G2 當必停。
- G-freeze-1:F3 cut 當下已有 1–7 `.md` 的 slug,整段舊 7 到 Ship;沒有五站狀態寫入。
- G-self-1:本 slug 自己走到 G1／G2／G3 時仍是舊 7;沒有五站機寫入。本目錄是 dogfood 舊 7,不是新 5 白老鼠。
- G-token-1:G1／G2／`ACCEPTED` token 與檔仍在。
- G-pre-1:F2 三前置仍是建五站機的閘;F3 只供應第三條(cut 已發生),不發明第四條(doctor／marketplace／cache)。
- G-honest-1:`COMPATIBLE`／exit 0 不足以當 cut,也不足以讓 coordinator 走五站 hop。
- G-honest-2:`marketplace update` 單獨發生,不足以改採用端路線。
- G-hollow-1:F3 完 ≠ `f3_cut_happened()==True`、≠「檔在」、≠「F2 電池仍綠」。
- G-carry-1:本檔列出的 cut attestation／三前置／graph vs dual-read／doctor／成功判準,到規格時每條有去向,不能無聲消失。
- G-reg-1:F2 同一電池 NEW5+OLD7 回歸仍綠(地板,不是 F3 完成)。

## Requested solution
- F3 做 brief §7 Cut:新 slug 預設五站;舊 7 只服務 freeze + dual-read;guide／STATUS 用語切五站。
- **cut 怎麼證明、graph 動不動、2.1.0 要不要本刀 bump、成功 CASE 叫什麼,本討論不選定。**
- 候選(未定案):`f3_cut_happened` 改讀樹上某一格,而不是把常數改 True 就算完。
- 候選(未定案):三前置維持合取;cut 真且未宣告 2.1.0 → 仍舊 7(SLOT-UNDECLARED-ROUTE)。
- 候選(未定案):in-flight 繼續吃既有 `graph.yaml`;新 slug 的預設 hop 另路,不拿共用 graph 一刀切。
- doctor 握手可以學會 2.1.0;**COMPATIBLE 仍不是 cut**。
- 舊 token／twin／graph 檔不刪。本 hop 不選定 attestation 路徑、契約鍵名、或 graph fork 檔名。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`graph.yaml`、gate token、STATUS、HISTORY、契約版本、`f3_cut_happened`、doctor 握手。
- 本 hop 不送 G1;status 留 draft;不宣稱 Human Stage1 PASS;不合併。
- **鎖:不刪 G1／G2／`ACCEPTED`;不把 in-flight 折成五站;不拿本 slug 當新 5 白老鼠。**
- 不重開 F0 十條;不放寬 hop≤2／Decide≤1／Goal≤1。
- 一次大爆炸改模板全文(brief:另開刀,不叫 F3 偷做)。
- 不把 doctor 綠／marketplace update／plugin cache 寫成 cut 或第四前置。
- 不把「`f3_cut_happened` 翻 True」或「F2 仍綠」寫成 F3 完成。
- 不在本討論選定 attestation 落點、graph fork、或 2.1.0 是否本刀 bump。
- 不重開 F2 已鎖的計數落點／event 鍵名／五桶 `hop_id`。
- 不處理 F2 park 的 D-1／D-2／D-3／F-c-4(不是本刀)。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:本 slug dogfood 舊 7 全套 meta-process
- [x] Q2:本 hop 是否只 Stage 1、不改 STATUS、不合併、不發明 G1?→ 原 brief:是
- [x] Q3:F3 刀是否=新 slug 預設五站、舊 7 只服務 freeze+dual-read、guide／STATUS 用語切五站?→ brief §7;翻=新 brief
- [x] Q4:in-flight 是否整段舊 7 到 Ship?→ brief §6 + OC-9。本目錄一有 1–7 `.md` = in-flight
- [x] Q5:可否刪 G1／G2／`ACCEPTED`?→ 否。F0–F3 都不刪;刪=新 brief
- [x] Q6:本 slug 是否自己走舊 7、不當新 5 白老鼠?→ 是。dogfood 舊 7 到 Ship
- [x] Q7:F0／F1 與 F2 是否已 G3 PASS、且 F2 把預設留在舊 7?→ HISTORY G3✅;`f3_cut_happened`≡False;S-8.1 無 cut 聲明
- [x] Q8:doctor 綠是否等於已 cut 或可跟 hops?→ 否。SLOT-DOCTOR-GREEN-MEANS;F2 4A 已鎖綠不是票
- [>] Q9:**Cut attestation** —— `f3_cut_happened` 要讀樹的哪一格才算「已發生」?常數翻 True／標記檔／契約 2.1.0／guide+STATUS 用語／`graph.yaml` 預設 hop 不再經 N7-g1?F2 只准讀樹、不准發明 cut。本討論不選。移交 F3 收斂
- [>] Q10:**F2 三前置** cut 之後是否仍要「2.1.0 ∧ ¬in-flight ∧ cut」三條合取?只翻 cut、契約仍 2.0.0 → live 新 slug 仍卡第一條。把 cut 等同 2.1.0 bump → 兩條塌成一條。維持三條 → 未 upgrade 的採用端仍舊 7(brief §6)。本討論不選。移交 F3
- [>] Q11:**graph vs dual-read** —— cut 是改各站 `graph.yaml` 預設 hop(拿掉 N7-g1／N6-g2)、還是宣告 2.1.0 dual-read 讓舊 7 與新 5 共存、還是兩者都要、還是只翻 coordinator、graph 不動?F2 S-2.7 零 graph diff;in-flight 仍吃既有 graph;2.0.0+五站 hops 預設=SLOT-REJECT。移交 F3
- [~] Q12:**doctor 約束** —— F3 若 bump 契約到 2.1.0,doctor 可否把 `2.1.0` 加進 `supported_contract_versions`(握手),但仍禁止 `COMPATIBLE`＝cut／＝五站?(帶假設:**可以學會 2.1.0,綠仍不是票**;暫定值=握手≠路線;風險=高;期限=F3 Decision,過期擋「COMPATIBLE 所以已切」)
- [>] Q13:**成功判準** —— F3 完要量哪幾格?種子(未鎖):空新 slug 預設五站;in-flight 仍舊 7;本 slug 仍舊 7;token 在;doctor 綠≠cut;F2 電池仍綠(回歸地板);2.0.0+五站 hops 仍紅。hollow 不得當完:`f3_cut_happened==True`、檔在、只改 guide 一句、只 F2 綠。移交 F3
- [~] Q14:F2 `contract_version()` 讀 `version`／`contract_version`,doctor 讀 `devflow_contract_version`。cut／2.1.0 宣告若只改其中一把鍵,三前置與握手會各說各話?(帶假設:**必須對帳,不得默認同一鍵**;期限=F3 Decision,過期擋把「契約檔改了」當已宣告)
- [>] Q15:guide／STATUS 用語切五站是 brief F3 列內的工作,還是 cut attestation 本身?本 PR 不改 STATUS。用語切了、布林仍 False,算不算 cut?移交 F3
- [x] Q16:cache／marketplace 可否當第四前置或當 cut?→ 否。F2 4A／S-3.6 已鎖

## Constraints
- 本 PR 不宣稱 G1 PASS、不宣稱 Human Stage1 PASS;不改 STATUS／HISTORY。
- 討論盲下游:本檔不指定腳本／API／元件當目標;attestation／graph／bump 只寫成 OQ。
- **Owner-locked F3 刀:**新 slug 預設五站;舊 7 只服務 freeze + dual-read;不刪 token;不折 in-flight;不爆炸改模板。
- **Owner-locked 本 slug 路線:**舊 7 到 Ship。本資料夾一有本檔 = 已 in-flight。
- **Owner-locked 三前置形狀:**F2 4A／OC-4 已鎖「缺一條就舊 7」。F3 可供應第三條,不可把 doctor／cache 加成第四條。第三條「讀哪」仍 OPEN(Q9)。
- **Owner-locked doctor 誠實:**綠只證明握手。綠 ≠ cut。
- **Owner-locked cap 數字:**hop≤2／Decide≤1／Goal reopen≤1;舊 7 不套。
- **採用 hop 身分:**graph／hooks 住方法包。未宣告 2.1.0 之前,marketplace 可換 hops 而 doctor 仍可因 `2.0.0` 握手綠。
- 詞條(語言,不是方案):**cut**=新 slug 預設從舊 7 換成五站這件事,不是刪檔。**cut attestation**=`f3_cut_happened` 讀樹的哪一格才准回 True。**三前置**=2.1.0 ∧ ¬in-flight ∧ cut。**dual-read**=2.1.0 同時讀舊 7 與新 5。**graph 預設**=各站 `graph.yaml` 預設 hop(今經 N7-g1／N6-g2)。**doctor 約束**=綠只握手。**hollow F3**=布林／檔在／F2 綠冒充 cut。**in-flight freeze**=已有 1–7 `.md` 的 slug 走舊 7。本 hop 不寫進長期記憶。

### F3 移交種子(不是施工)
- Q9／Q15 是 attestation 家族;Q10／Q14 是三前置家族;Q11 是 graph vs dual-read;Q12 是 doctor;Q13 是成功判準。維持未鎖。
- Q10／Q12／Q14 過期 → 擋本 slug G2(不得把假設升格成已核)。
- Q3／Q4／Q5／Q6／Q8／Q16 已解;後站不得把 freeze／禁刪／綠≠cut 標可選。
- 本資料夾已有本檔 = 已 in-flight;後站不得對自己開五站機。

## 驗收雛形
- AC-1(G-cut-1):假設 F3 宣稱完成且某 slug 目錄尚無 1–7 `.md`,當寫手開該 slug,則預設走五站,不再以例行 G1／G2 當必停。
  - 從哪看:該 slug 的路線判定 + 中間停點紀錄
  - 看到什麼算對:Idle→Intake;中間無「請人審 A4／A7」;不是舊 7 例行停
  - 拿什麼試:F3 之後造的空 slug;不是本目錄
- AC-2(G-freeze-1):假設 F3 cut 當下某 slug 已有 1–7 `.md`,當路線被求切五站,則仍舊 7 到 Ship。
  - 從哪看:該目錄站檔 + 被拒絕的 hop
  - 看到什麼算對:仍有例行 G1／條件 S3／G2／G3;無五站機寫入
  - 拿什麼試:任一已有站檔的 slug;`five-station-f2`／`five-station-simplify`
- AC-3(G-self-1):假設本 slug 被求切五站自動前進,當看本目錄,則仍是舊 7 站檔與例行閘。
  - 從哪看:本目錄 1–7 `.md` 與被拒絕的 hop
  - 看到什麼算對:有 `1-discussion.md`;無五站機寫入
  - 拿什麼試:本資料夾(本 hop 落檔即 in-flight)
- AC-4(G-token-1):假設 F3 做完,當人找 G1／G2／`ACCEPTED` token 與檔,則仍在。
  - 從哪看:`scripts/check-gate-tokens.sh` + 模板／graph 檔
  - 看到什麼算對:token 句仍在;檔未刪
  - 拿什麼試:現行 token 牙
- AC-5(G-pre-1):假設 cut 已宣告但契約未宣告 2.1.0,當 coordinator 評 live 新 slug,則仍 `allow_legacy()`。
  - 從哪看:路線閘理由
  - 看到什麼算對:理由含未宣告／仍舊 7;不是「cut 已發生所以可 hop」
  - 拿什麼試:後續造;本 hop 不選 2.1.0 是否 bump
- AC-6(G-honest-1／G-honest-2):假設 doctor 剛印 `COMPATIBLE` 或只做了 `marketplace update`,當有人把這當 cut,則被拒。
  - 從哪看:該次 hop 的拒絕理由
  - 看到什麼算對:理由是路線／cut 未發生,不是「doctor 已綠」
  - 拿什麼試:本 tree 現況(契約 2.0.0 + doctor 可綠)
- AC-7(G-hollow-1／G-carry-1):假設本檔 Q9–Q15 列了一題,當人讀到 F3 Decision／Spec,則該題有去向;且不得只憑布林 True／檔在／F2 綠宣稱 F3 完。
  - 從哪看:Stage 2 對帳 + F3 完成宣稱
  - 看到什麼算對:五個家族各有處理／Non-Goal／仍待驗;hollow 被點名
  - 拿什麼試:Q9 attestation、Q10 三前置、Q11 graph、Q12 doctor、Q13 成功
- AC-8(G-reg-1):假設 F3 宣稱完成,當重跑 `scripts/test-five-station-f2.sh` 全入口,則仍 exit 0;只重跑 F2 不算 F3 綠。
  - 從哪看:F2 電池出口
  - 看到什麼算對:NEW5+OLD7 仍能獨立紅、也能一起綠
  - 拿什麼試:現行 F2 電池;不是本 hop

## 現況圖
誰:新 slug 寫手
做什麼:開新 feature
工具:舊 7 graph
痛點:F2 完仍等人
↓
誰:coordinator
做什麼:評三前置
工具:five_station_f2.py
痛點:cut 恆假
↓
誰:doctor
做什麼:印 COMPATIBLE
工具:devflow-doctor.sh
痛點:綠≠cut

## 邏輯圖(ASCII)
```
now
|-- F1 G3 PASS            [teeth + annex]
|-- F2 G3 PASS            [coordinator]
|   |-- NEW5 fixture hop
|   |-- f3_cut_happened   [= False]
|   +-- live new slug     [old 7 wait]
|-- contract 2.0.0
|-- doctor COMPATIBLE     [handshake != cut]
|-- graph N7-g1 / N6-g2   [still default]
+-- STATUS Backlog A      [stale: next=F1]

three-pre                    [F2 4A locked shape]
|-- 2.1.0 declared
|-- not in-flight
+-- F3 cut happened          [OPEN how; Q9]

cut-attestation              [OPEN; Q9/Q15]
|-- flip constant True
|-- marker file
|-- contract 2.1.0           [may collapse Q10]
|-- guide + STATUS words
+-- graph default hop

graph-vs-dual-read           [OPEN; Q11]
|-- change graph.yaml        [may fold in-flight]
|-- declare 2.1.0 dual-read
|-- both
+-- coordinator only         [graph stays]

fail
|-- doctor green as cut      -> SLOT lie
|-- marketplace as cut       -> remote route
|-- flip bool = F3 done      -> hollow
|-- F2 green = F3 done       -> floor as finish
|-- shared graph rewrite     -> fold freeze
|-- this slug as NEW5        -> dogfood lie
+-- delete tokens            -> new brief
```

## Interview Log(推理鏈外顯)
- Q:F3 這一刀到底做什麼、本討論為什麼不准切線?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L180-L182 notes/design/five-station-simplify-brief-v3.md:L165-L166 scripts/five_station_f2.py:L276-L278
  - 推理:brief 把 coordinator 與 cut 拆成兩刀。F2 完成樹把 cut 鎖成 Out,函式恆 False。本 hop 只准問「怎麼證明 cut」,不准在 Stage 1 把布林翻掉。
  - 結論:CONFIRMED F3 = Cut;本檔只討論;不發明 attestation、不送 G1。
- ⚠️ Q:F2 完了,現場為什麼還在等人?
  - 事實:docs/dev/five-station-f2/4-spec.md:L826-L831 scripts/five_station_f2.py:L281-L293 skills/dev-flow/stage2/graph.yaml:L53-L57 docs/dev/HISTORY.md:L719-L723
  - 推理:F2 證明的是合成 fixture hop,不是 live 預設。三前置在 live 缺 cut(常連 2.1.0 也缺)。graph 預設仍經 N7-g1。HISTORY 寫 no F3 opened。痛在預設,不在 coordinator 檔不在。
  - 結論:CONFIRMED 痛=F2 後預設仍舊 7;F2 綠是地板不是 F3。
- ⚠️ Q:cut 要怎麼證明發生過,為什麼不能把常數改 True?
  - 事實:scripts/five_station_f2.py:L276-L278 docs/dev/five-station-f2/2-decision.md:L79 docs/dev/STATUS.md:L50
  - 推理:F2 准讀樹、不准發明 cut。常數翻 True 沒有樹證據,重跑舊電池會把 S-3.2 的「cut 未發生」一併殺死。STATUS 用語是 brief F3 列,但本 tree Backlog A 過期,看板不能當正本。讀哪一格仍 OPEN。
  - 結論:OPEN Q9／Q15;attestation 移交 F3;不選落點。
- ⚠️ Q:F2 三前置在 cut 之後還要三條嗎?
  - 事實:docs/dev/five-station-f2/2-decision.md:L292 docs/dev/five-station-f2/4-spec.md:L757-L761 notes/design/five-station-simplify-brief-v3.md:L168 notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L24
  - 推理:少 2.1.0 只翻 cut = 未 upgrade 的採用端被遠端改線。把 cut 等同 bump = 兩條塌成一條,SLOT-UNDECLARED 失去獨立牙。維持三條則 F3 可能「cut 真、現場仍舊 7」,看起來像沒切。
  - 結論:OPEN Q10;形狀已鎖、合取是否維持移交;過期擋兩前置當已核。
- ⚠️ Q:改 graph 預設,跟宣告 dual-read,是同一件事嗎?
  - 事實:notes/design/five-station-simplify-f0-state-machine.md:L10-L15 notes/design/five-station-simplify-f0-state-machine.md:L49-L50 docs/dev/five-station-f2/7-review.md:L72 notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24
  - 推理:in-flight hop 正本是既有 graph。共用 `graph.yaml` 拿掉 N7-g1,freeze 樣本可能一起改線。只宣告 2.1.0、graph 仍經 G1,寫手仍等人。只改 graph、契約仍 2.0.0,SLOT-REJECT 紅。兩槓不是同一物。
  - 結論:OPEN Q11;本討論不選 graph／dual-read／兩者／只翻 coordinator。
- ⚠️ Q:doctor 學會 2.1.0,算不算 cut?
  - 事實:hooks/_doctor_impl.py:L193-L202 hooks/_doctor_impl.py:L492-L500 notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28 scripts/five_station_f2.py:L260-L268 devflow-contract.json:L1-L3
  - 推理:doctor 綠只證明契約版本 ∈ supported。加 2.1.0 進 supported 是握手,不是路線。F2 讀的契約鍵與 doctor 讀的鍵不是同一個;只改一把會各說各話。
  - 結論:NEEDS_VERIFICATION Q12／Q14;假設=綠仍不是票、兩鍵必須對帳。
- Q:什麼叫 F3 完?最極端的假完成是什麼?(發散)
  - 事實:docs/dev/five-station-f2/2-decision.md:L261 docs/dev/five-station-f2/4-spec.md:L826-L831 scripts/five_station_f2.py:L276-L278
  - 推理:F2 已示範 hollow=檔在／F1 綠／單路 hop。F3 對應 hollow=布林 True／guide 一句／F2 電池仍綠。真完至少要能指出空新 slug 預設五站,且 freeze／本 slug／token／doctor 約束同時成立。
  - 結論:OPEN Q13;成功種子列出、不鎖 CASE 名。
- ⚠️ Q:本 hop 有沒有偷做 cut 或把自己當白老鼠?(盲點)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L165-L166 本 hop brief(只 Stage 1、不改 STATUS、不發明 G1)
  - 推理:本檔落盤後目錄已有 `1-discussion.md`=in-flight。Requested solution 只列候選。Q9–Q15 維持 `[>]`／`[~]`。不改 STATUS,避免跟「feature branch 不碰看板」撞車,也避免把看板改口冒充 cut。
  - 結論:CONFIRMED 本檔只落討論;不切線;不刪 token;本 slug 舊 7。Q10／Q12／Q14 過期擋本 slug G2。不宣稱 Human Stage1／G1。
