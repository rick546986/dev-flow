---
feature: five-station-simplify
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 1. 討論 — 五站簡化(摺例行人停、不摺完整度)

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／狀態機落檔,不是現場一問一答。
> Implementer **A** 獨立盤點;不抄其他 implementer。Lane = **full**。本 hop **不送 G1**。
> 本 slug **自己仍走舊 7 站**(含例行 G1／條件 S3／G2／G3)直到 Ship;本檔只討論「新 5」長什麼樣。
> 本 PR **不實作 F1–F3**、不改母版模板／gates／graphs、不改 STATUS。未核敘述標 `[Assumption]`。
> 原料:`notes/design/five-station-simplify-brief-v3.md`、`notes/design/five-station-simplify-f0-state-machine.md`、`docs/dev/STATUS.md` Backlog 列 A。

## Problem
痛:full lane 把「方向、互動、契約」三次都做成**例行人類停點**(G1／S3-`ACCEPTED`／G2),等人次數被站數綁死;物質(OC、R/S、Demo、Evidence)該留,停點不該等於站數。
受影響:母版維護者、gate 審者、採用專案 owner、之後才存在的 coordinator。頻率:每條 full 軌至少三停,再加 Ship。觀測窗:2026-09-13 本 repo 剛跑完的 `requirement-discovery-gaps`(同日 G1 等→G1 PASS→S3 `NOT_REVIEWED`→G2 等→G2 PASS→G3 PASS)。
現在怎麼繞:人喊「繼續」+ agent 跟 `graph.yaml`  hop;fresh-context Agent 當書面審;owner 自審當最後手段;STATUS 同伴 PR 在合主線後才改看板;Fast 合法跳 1–3。

## Context(已知事實)
- F0 brief 是設計正本不是契約;Owner 已核;F0 零 bump、不准改 `_templates/`／README §7 錨／各站 `graph.yaml`／既有牙;不准刪 G1／G2／`ACCEPTED`:notes/design/five-station-simplify-brief-v3.md:L1-L9
- 摺的是預設人類停點不是完整度;物質留下、等人次數不該等於站數:notes/design/five-station-simplify-brief-v3.md:L13-L28
- OC-1…OC-10 已鎖:五站 Intake→Decide→Spec→Build→Ship;殺例行 G1／S3-`ACCEPTED`／G2;Ship 唯人;條件頁表 A/B;UI twin 只 UI/flow;Must-keep;dual-read 2.1.0;F0→F3;in-flight 凍舊 7;禁刪禁改正本:notes/design/five-station-simplify-brief-v3.md:L36-L45
- 五站是預設路線別名;舊七份檔名不動;`1-discussion.md`…`7-review.md` 仍是產物:notes/design/five-station-simplify-brief-v3.md:L47-L58
- 表 A1–A10 各有生成謂詞／人類 latch／自動前進謂詞;A4／A7 twin 仍產但例行不等人;A10 是唯一預設人停:notes/design/five-station-simplify-brief-v3.md:L85-L97
- 表 B1 Demo+`ACCEPTED`、B2 UI twin、B3 Variant、B4 Quiz、B5 Design Boundary;latch 未命中卻問人 = 違 brief:notes/design/five-station-simplify-brief-v3.md:L103-L117
- F0 不寫 coordinator 碼;誰前進／誰准寫判定／中間站無人停／rewrite cap／舊 7 執行面／觀測「要留」已鎖,落地從 F2:notes/design/five-station-simplify-brief-v3.md:L119-L133
- Must-keep M1–M16(ID 鏈、圍欄、反模糊、Real-world→Demo→OC、Human 主權、G3 八點、Profile、DBC、scope guard、五律、T seam、四眼、html 重生、Quiz、token 全留、graph 不改):notes/design/five-station-simplify-brief-v3.md:L135-L157
- 契約 dual-read minor=2.1.0;`2.0.0` 繼續讀舊 7;F0 不 bump;F3 cut 後新 slug 才預設五站;採用專案要 upgrade 到 2.1.0 才看五站:notes/design/five-station-simplify-brief-v3.md:L160-L169
- 四刀不准併:F0 設計、F1 teeth+annex、F2 coordinator／dual-path、F3 cut;F3 後 G1/G2/`ACCEPTED` 仍在 repo:notes/design/five-station-simplify-brief-v3.md:L171-L181
- 狀態機:Idle→Intake→Decide→Spec→Build→Ship→Done;`HumanWait`／`Escalated` 不是站;in-flight 不建本機:notes/design/five-station-simplify-f0-state-machine.md:L21-L50
- Intake→Decide 謂詞:1-discussion 可解析、OQ 全解或明標假設、Real-world Context 在(legacy 除外);假則停 Intake,不得進 HumanWait:notes/design/five-station-simplify-f0-state-machine.md:L60-L69
- Ship→Done **沒有**自動前進;機械全綠仍必須 HumanWait;代填 `verdict: PASS` 違 OC-3:notes/design/five-station-simplify-f0-state-machine.md:L110-L120
- rewrite cap:hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;舊 7 不套這三 cap:notes/design/five-station-simplify-f0-state-machine.md:L122-L139
- 禁則 X1–X8(自動前進 Ship、刪 token、F0 改 graph、in-flight 套新機、暗改 cap、未命中卻問人、Agent 冒充判定、把 A4/A7 當例行停加回):notes/design/five-station-simplify-f0-state-machine.md:L189-L207
- STATUS 只在整合分支維護;feature branch 不碰本檔;表列唯一寫入口 `status-update.sh`:docs/dev/STATUS.md:L10-L26
- Active 目前無進行中改版軌:docs/dev/STATUS.md:L30-L32
- Backlog B:owner 已排完整 full lane 觀測實驗,在那之前不動 Stage 1–4 模板:docs/dev/STATUS.md:L48
- Backlog 列 A 指向本 slug 的 F0 brief＋狀態機;下一刀 F1 teeth＋dual-read annex:docs/dev/STATUS.md:L50
- 現行契約句仍是七份文檔 + G1/G2/G3:docs/dev/readme-contract-extract.md:L7-L17
- G1 = 方向核准 + Owner Calls 全裁決:docs/dev/readme-contract-extract.md:L77-L83
- G2 = R/S 全審 + DD 全裁決 + Verification Profile + Demo verdict;`ACCEPTED` 須人類、Runtime 拒 Agent 自產:docs/dev/readme-contract-extract.md:L85-L107
- G3 = 本次 S 全綠 + 回歸綠 + 現象證據 + Evidence 八點:docs/dev/readme-contract-extract.md:L109-L128
- author ≠ approver;審查序:適格人類 → fresh-context Agent → owner 自審(最後手段):docs/dev/readme-contract-extract.md:L70-L74
- G1/G2/G3 twin 五格標籤釘死;判定正本是 md 頂欄 `verdict:` 不是勾選:docs/dev/readme-contract-extract.md:L50-L58 notes/design/gate-verdict-write.md:L8-L24
- Stage 1 討論由 `/dev-talk` 專職;gate = OQ 全解或明標假設;Stage 2 gate = G1:skills/dev-flow/SKILL.md:L41-L45
- full lane = 1–7 全套(3 選配);fast 可省 1–3:skills/dev-flow/SKILL.md:L34-L36
- Stage 2 預設 hop 含 N7-g1;完成條件要求 twin 已產且 verdict 已記錄:skills/dev-flow/stage2/graph.yaml:L53-L55 skills/dev-flow/stage2/nodes/N7-g1.md:L22-L35
- Stage 4 預設 hop 含 N6-g2;未裁決 DD／缺 Profile／Demo 不合不得過:skills/dev-flow/stage4/graph.yaml:L93-L96 skills/dev-flow/stage4/nodes/N6-g2.md:L20-L32
- Stage 7 終點 N5-verdict;agent 不得手改 `verdict:`;尚無寫入才准在 chat 問人:skills/dev-flow/stage7/graph.yaml:L96-L102 skills/dev-flow/stage7/nodes/N5-verdict.md:L20-L32
- Stage 3 九條 trigger 在模板;命中→條件式必要;跳過須 Owner Call 含「Stage 3」+「跳過」:_templates/3-prototype.md:L15-L27 _templates/3-prototype.md:L53-L61
- `_stage3_impl.py` 擋無 attestation 的 `ACCEPTED`;`NOT_REVIEWED` ≠ `ACCEPTED`;legacy／fast 無 1/3 檔可 N/A:hooks/_stage3_impl.py:L15-L28
- `check-spec-gate.sh` 是 Gate 不是 warning;exit 1 = G2 不得送審:scripts/check-spec-gate.sh:L35-L39
- `build-gate-twin.py` STAGES=`2-decision|4-spec|7-review|5-tasks`;GATE_STAGES 三站:scripts/build-gate-twin.py:L93-L96
- 第 1 站審頁產檔器 `build-stage1-html.py`;掃頁另一支 `build-scan-html.py`;兩支預設都寫同名 `1-discussion.html`:scripts/build-stage1-html.py:L8-L18 scripts/build-scan-html.py:L3-L9
- Pages 掛的站審檔名含 `1-discussion.html`,不含 3／4 的審頁名:notes/design/pages-hosting.md:L11-L13 scripts/publish-pages.sh:L62
- Real-world Context →(條件)Demo → S 級 Operational Context,不另發 ID 鏈:notes/design/real-world-interaction.md:L16-L22
- Design Boundary 是 4-spec 內條件章節,不是新站、不新 ID、由既有 G2 一併審:notes/design/design-boundary-contract.md:L8-L13
- 現行契約版 `2.0.0`;plugin 版 `3.24.0`:devflow-contract.json:L2 .cursor-plugin/plugin.json:L2-L3
- Stage 1 模板明文「不做決定」;本階段固定產出 md+html: _templates/1-discussion.md:L12-L14
- 2026-09-13 `requirement-discovery-gaps` 實跑:Stage 2 落地後 awaiting human G1:docs/dev/HISTORY.md:L552-L555
- 同 slug 人類 G1 PASS 後 Stage 仍停 2-decision:docs/dev/HISTORY.md:L557-L561
- Stage 3 落地時 Human verdict 仍 `NOT_REVIEWED`:docs/dev/HISTORY.md:L563-L567
- Stage 4 落地後 awaiting human G2:docs/dev/HISTORY.md:L569-L573
- 人類 G2 PASS 後 Stage 仍停 4-spec:docs/dev/HISTORY.md:L575-L579
- 人類 G3 PASS 後才 shipped、Active 移出:docs/dev/HISTORY.md:L599-L603
- 該 slug 的 2-decision 頂欄已是人寫 `verdict: PASS`,並聲明不是 Agent 自裁:docs/dev/requirement-discovery-gaps/2-decision.md:L1-L14
- 長期記憶對「五站／例行 gate 為何等人」=`NO_RELIABLE_MATCH`;「目前七站」=`NEEDS_VERIFICATION` 且 local-store schema STALE。本場不以記憶當現況。(本機 `dev-memory.py ask` 2026-09-13)
- 受影響面(後續刀才動,本 hop 不動):`_templates/` 1–7、`skills/dev-flow/stage{2,3,4,5,6,7}/graph.yaml`、`skills/dev-talk/`、`docs/dev/readme-contract-extract.md` §7、`hooks/_stage3_impl.py`、`scripts/check-spec-gate.sh`、`scripts/build-gate-twin.py`、`scripts/build-stage{1-7}-html.py`、`devflow-contract.json`、`guides/guide-dev-flow.html`、採用專案 `dev-setup` upgrade 路徑

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 寫手 | 把本站寫到可 hop,不被例行停拖住 | 寫 `docs/dev/<slug>/` 該站 md | 模板、graph、本站產物 | 人何時按判定;下一站能不能自動走 | graph.yaml |
| 審者 | 只在方向／互動／契約／出貨真要人時出手 | 寫 md 頂欄 `verdict:`／attestation | gate twin、審頁 | 這頁是不是例行停、能不能跳 | gate-twin |
| owner | 握方向與出貨;看板只反映現況 | 裁 OC／G1–G3;合主線後改 STATUS | F0 brief、STATUS、HISTORY | 採用現場等人痛是否同母版 | STATUS |
| 討論 agent | 把「摺站」寫成可收斂討論,不直奔施工 | 寫 1-discussion | 白名單、指名 brief | 未指名的採用現場 log | 口頭、GitHub |
| Demo 參與者 | 互動方案由人說了算,不被 Agent 代填 | 親填 `ACCEPTED`+attestation | 可操作 Demo | 無 trigger 時為何還被叫來 | 瀏覽器、throwaway |
| 採用專案維護者 | 升級後路線清楚;未升級仍走舊 7 | 本機 plugin／`dev-setup` | 本機契約版 | 2.1.0 何時到、舊 slug 會否變紅 | plugin 市集 |
| coordinator | 謂詞真就 hop,假就停修,不准問「要不要繼續」 | F2 前**不存在**;今由人+agent 代跳 | 無 runtime | 謂詞／cap／latch 尚未有牙 | 「繼續 \<slug\>」 |
| STATUS 同伴寫手 | 合主線後改看板,不塞進 feature PR | 只在 `main` 跑 `status-update.sh` | 合併結果 | feature branch 上的表列會被牙打紅 | 短命 companion PR |

### Current Journey
正式 SOP:full 走 1→2(+G1 人停)→條件 3(+`ACCEPTED`)→4(+G2 人停)→5→6→7(+G3 人停)。實際做法(無五站、無 coordinator 時)如下。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 寫手 | 寫站產twin | graph.yaml | 審者 | 該站 md+html | 停等人類 |
| 2 | 審者 | 開頁交判定 | gate-twin | — | md `verdict:` | 例行三停 |
| 3 | owner | 催下一站 | STATUS | 寫手 | HISTORY／Active | 等人=站數 |

### Workarounds
- 人在 chat 喊「繼續 \<slug\>」;agent 讀 `graph.yaml` 進下一 hop。沒有 coordinator 讀謂詞。
- fresh-context reviewer Agent 做書面審,常被當成「過 gate」的替代;契約仍要人類 `verdict:`。
- owner 自審當最後手段(有記錄);四眼被壓成一人兩角。
- Stage 3 用 Owner Call「跳過」繞 `ACCEPTED`;或落地後長期停在 `NOT_REVIEWED` 再等人。
- Fast 合法跳 1–3,把早期風險拖到 4-spec。
- STATUS 不進 feature PR;另開 companion 在 `main` 改表列。
- 本 repo 剛發生的土法:同一 slug 一天內三次「awaiting human」(G1／S3／G2),再加 G3。
- 這些繞法常不留「這次停是例行還是真要人」的機械紀錄。

### Exceptions
- Fast lane 合法省略 Stage 1–3;無 1/3 檔 → `_stage3_impl.py` 判 legacy/N-A。
- 命中 Stage 3 trigger 仍可經 Owner Call 跳過(行內同時含「Stage 3」與「跳過」)。
- 1-discussion 無 Real-world Context 的舊檔走 legacy,不要求回頭補作業。
- in-flight:`docs/dev/<slug>/` 在 F3 cut 當下已有任一站檔 → 整段凍舊 7 直到 Ship。本 slug 自己就屬這條。
- owner 自審可關 G1/G2/G3,但必須記 reviewers,不准假裝四眼。
- 測試 fixture 的 `ACCEPTED` 必須含 `test-only human fixture`;正式模式拒收。
- `REQUEST_CHANGES`／`REVISE`／`HOLD` 走修迴圈,不得用「自動前進」跳過。
- `[Assumption]` 採用現場等人痛與母版同量級:無採用 log;風險=高(若為假,F1 優先級下降但不改 OC-2);期限=Stage 2 對帳,過期擋本 slug 的 G2。
- `[Assumption]` A1 審頁與 A2 掃頁將長期共寫 `1-discussion.html`:現況兩支產檔器同 dest;風險=中(若為假,F1 不必為雙檔名加牙);期限=F1 annex。
- `[Assumption]` 本 slug 進舊 7 的 Stage 3 時會命中「改變下一步／角色交接／人工核准／等待逾時」:無本場判定節;風險=高(若為假,本 slug 可 n-a);期限=本 slug Stage 3。

### Evidence
- Owner 鎖定 brief v3(2026-09-13 #293):notes/design/five-station-simplify-brief-v3.md 全文;本 hop 只 Stage 1、full、不送 G1、不實作 F1–F3(本 session brief)。
- F0 狀態機(同日 #293):notes/design/five-station-simplify-f0-state-machine.md 全文。
- STATUS Backlog 列 A(合主線 #294):docs/dev/STATUS.md:L50。
- 母版同日實跑三次例行人停:docs/dev/HISTORY.md:L552-L603;2-decision 人寫 PASS:docs/dev/requirement-discovery-gaps/2-decision.md:L1-L14。
- 本 tree 已核:上列 Context 出處(2026-09-13 讀過,行段支持斷言)。
- 長期記憶無五站條目;不以記憶補事實。
- `[Assumption]` 三條見 Exceptions;期限如上。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 採用現場其實不痛例行 G1/G2 → F1 投資理由變弱,但不翻 OC-2 | 高 | 問一家已 upgrade 的採用專案最近一次 full 等人次數 | Stage 2／owner |
| A1/A2 其實已有不衝突 dest → F1 不必為雙檔名加 annex | 中 | 讀兩支產檔器 dest 與 Pages 清單是否已分檔 | F1 annex／寫手 |
| 本 slug Stage 3 零命中 → 本軌可 n-a,不 latch Demo | 高 | 本 slug 開 Stage 3 時對九條逐條勾 | 本 slug Stage 3／寫手 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | 本場指名原料 | `notes/design/five-station-simplify-brief-v3.md` | 是 | 是 |
| F0 狀態機 | 本場指名原料 | `notes/design/five-station-simplify-f0-state-machine.md` | 是 | 是 |
| 看板列 A | 本場指名原料 | `docs/dev/STATUS.md` | 是 | 是 |
| 現行 7 站契約 | 對照「現在怎麼走」 | `docs/dev/readme-contract-extract.md` §3／§7 | 是 | 是 |
| 各站 graph／hop | 證明 G1/G2/G3 在預設路上 | `skills/dev-flow/stage{2,4,7}/` | 是 | 是 |
| 同日實跑等人 | 最近一次真的發生 | `docs/dev/HISTORY.md` 2026-09-13 `requirement-discovery-gaps` | 是 | 是 |
| 採用現場等人 log | 痛是否只發生在母版 | 無落盤路徑 | 未核 | 否 |
| 其他 implementer 討論 | 禁抄 | `docs/dev/five-station-simplify/` 他稿 | 禁 | 否 |

## Goals
- G-out-1:人握的是方向與出貨,不是每一張中間卡;中間卡過謂詞就走,沒過就停修。
- G-out-2:例行人類停點從「G1 + 條件 S3 + G2 + G3」收成「預設只剩出貨那一停」;互動／不可逆仍可條件式叫人。
- G-out-3:摺停點之後,Must-keep 完整度一項都不因「已經比較少站」被省略。
- G-out-4:已開工的舊 7 slug 不被中途折成新路線,直到該 slug 出貨。
- G-out-5:同時存在舊 7 與新 5 時,舊 slug 不會只因契約 minor 升級而整批變紅。
- G-out-6:沒命中「該叫人」的頁,沒有人會被系統叫去按判定。
- G-out-7:沒有互動風險的改動,不被迫產互動頁、不等 Demo。
- G-out-8:本 slug 自己的出貨路徑仍是舊 7,直到它自己 Ship;不拿自己當新 5 的第一個白老鼠。

## Requested solution（候選，未定案）
- 預設路線別名五站:**Intake → Decide → Spec → Build → Ship**;檔名家族仍是 `1-discussion`…`7-review`。
- **例行** G1／S3-`ACCEPTED`／G2 不再是人類必停;機制、檔、token、牙全留。
- 預設人類必停只剩 Ship(舊 G3 物質);coordinator 不得代寫 `verdict:`。
- 頁走表 A1–A10 + 表 B;生成謂詞假 → 不產頁;人類 latch 假 → 不准問人。
- UI twin 只在 UI/flow 必要;與 B1 同一 latch,不另開第二次人停。
- Must-keep 十六條仍成立。
- 契約 minor 2.1.0 dual-read 舊 7 與新 5;F0 不 bump;條文進 F1 annex。
- 交付切刀:F1 teeth+dual-read annex → F2 coordinator／dual-path → F3 cut。F0 已落盤。
- 本 hop 不選定牙長在哪支腳本、coordinator 是新 process 還是改 graph、A1/A2 是否分檔。

## Non-Goals(初稿)
- 本 PR 不實作 F1 teeth、不寫 dual-read annex、不寫 coordinator、不 bump、不 cut。
- 不改 `_templates/`、各站 `graph.yaml`、README §7 錨、既有牙、STATUS、HISTORY。
- 不刪 G1／G2／`ACCEPTED` 檔、token、twin。
- 不把 in-flight slug(含本 slug)折成五站。
- 不遠端改採用專案路線。
- 不重開 OC-1…OC-10;翻任何一條 = 新 brief。
- 不另發 Journey／Actor／五站專屬 ID 鏈。
- 不把「七份檔太多」當成要摺的東西;摺的是停點。
- 不抄其他 implementer 的討論稿。

## Open Questions
- [x] Q1:lane 是否 full?→ owner:full;本 slug 走舊 7 全套
- [x] Q2:本 hop 是否只 Stage 1、不送 G1、不實作 F1–F3?→ owner:是
- [x] Q3:Goals 是否只寫結果、五站別名另欄?→ owner 意圖已鎖;本檔已分欄
- [x] Q4:預設人停是否只剩 Ship?→ F0 OC-3 已鎖
- [x] Q5:G1/G2/`ACCEPTED` 是否刪檔?→ OC-10 已鎖:不刪
- [x] Q6:本 slug 是否中途切五站?→ OC-9 已鎖:否,凍舊 7 到 Ship
- [~] Q7:採用現場等人痛是否與母版同量級?(帶假設:是;風險=高;期限=Stage 2,過期擋本 slug G2)
- [~] Q8:coordinator 今日是否已存在?(帶假設:不存在,hop 靠人喊繼續+graph;風險=低;F2 才落地)
- [~] Q9:A1 審頁與 A2 掃頁是否將繼續共寫 `1-discussion.html`?(帶假設:是,F0 不改產檔器;風險=中;期限=F1 annex)
- [>] Q10:F1 牙最小集合落在哪些腳本／fixture?→ 移交 Stage 2／F1
- [>] Q11:2.1.0 dual-read 欄位、缺省、舊檔不紅的寫法?→ 移交 F1 annex
- [>] Q12:in-flight 機械偵測(「已有任一站檔」如何掃、誰蓋戳)?→ 移交 Stage 2／F2
- [>] Q13:本 slug 自己的 Stage 3 九條是否命中?→ 移交本 slug Stage 3
- [>] Q14:Quiz 與 Ship 同一次人停的頁面怎麼併?→ 移交 Stage 2／F2
- [>] Q15:Backlog B「觀測前不動 Stage 1–4 模板」與 F1 若要釘模板句如何共存?→ 移交 Stage 2／owner

## Constraints
- 本 PR 不宣稱 G1 PASS;status 留 draft;不改 STATUS／HISTORY。
- 表列只准 `scripts/status-update.sh`;本 branch 禁改正本表列。
- 本 slug 過程檔走舊 7;新 5 只出現在討論／後續規格,不出現在本 slug 的 hop 機。
- F0 已鎖面不得當本場「待裁決」重開。
- 高影響 `[Assumption]`／`[~]` 必寫風險 + 期限;到期未驗擋本 slug G2。
- 詞條(語言,不是方案):例行停點 = 預設路上每次都等人的 gate;物質 = 檔／token／牙／謂詞仍在;路線別名 = 五站名稱對舊七檔;page-human latch = 表 A/B 欄為「是」才准問人;in-flight freeze = 已有站檔的 slug 整段舊 7。本 hop 不寫進長期記憶。
- 記憶對帳:無可信五站記憶;schema STALE。現況只信本 tree。

## 驗收雛形
- AC-1(G-out-1):假設一份新 slug 已過中間站謂詞,當 coordinator(或今時代跳的人)要離站,則不必等人按中間判定,也不得問「要不要繼續」。
  - 從哪看:該 slug 離站紀錄(前進／停修),不是聊天同意
  - 看到什麼算對:謂詞全真→已離站;一假→停在該站修;沒有「請 owner 看一下再走」
  - 拿什麼試:本 brief 表 A 一列 latch=否的站;以及一份謂詞未齊卻問人的對照稿
- AC-2(G-out-2):假設一條無互動、非不可逆的 full 軌跑完,當數人類必停,則只在出貨停一次。
  - 從哪看:該軌的人停紀錄(md 頂欄／attestation／HISTORY「awaiting human」)
  - 看到什麼算對:沒有例行 G1／G2／S3-`ACCEPTED` 等人;有 Ship `verdict:` 由人寫
  - 拿什麼試:對照本 repo 2026-09-13 `requirement-discovery-gaps` 的三次 awaiting;新路線應少兩到三次
- AC-3(G-out-3):假設有人說「已經五站了所以這條 Must-keep 可省」,當抽 M1–M16 任一條,則該條仍在且可指出正本。
  - 從哪看:Must-keep 表與對應牙／模板／契約句
  - 看到什麼算對:十六條都能指到現行正本;沒有「因為摺站所以省略」
  - 拿什麼試:brief §5 表;抽 M5 attestation 與 M15 token 仍在
- AC-4(G-out-4):假設 F3 cut 當下某 slug 已有任一站檔,當有人要把該 slug 改走五站機,則改不動。
  - 從哪看:該 slug 的路線標記／coordinator 是否建五站機
  - 看到什麼算對:仍走既有 graph;沒有五站狀態寫入
  - 拿什麼試:本 slug 自己(已有 1-discussion 即凍舊 7);另造「cut 後才開的新 slug」對照
- AC-5(G-out-5):假設採用專案從契約 `2.0.0` 升到 `2.1.0`,當舊 7 slug 再跑既有牙,則不因缺五站欄而整批紅。
  - 從哪看:該次 upgrade 後舊 slug 的檢查輸出
  - 看到什麼算對:舊 7 欄位可空、可留人寫值;新欄缺省不紅
  - 拿什麼試:一份只有七站欄的舊 4-spec／2-decision;F1 annex 落地後再跑
- AC-6(G-out-6):假設某頁 latch=否,當流程還在跑,則沒有「請人審這頁」的紀錄。
  - 從哪看:前進／latch 機械紀錄(F2 才有 schema;此前看 chat／HISTORY 有沒有不該有的 awaiting)
  - 看到什麼算對:latch 假 → 無請人審;latch 真 → 必停且不代填
  - 拿什麼試:A4/A7(twin 產但不等人)對照 A10
- AC-7(G-out-7):假設本次變更是純腳本／API／守衛／文件,當問有沒有 Demo／UI twin,則沒有,且不等人填 `ACCEPTED`。
  - 從哪看:該 slug 是否存在 `3-prototype` Demo 與 UI twin;B1 判定
  - 看到什麼算對:未命中 → A5 n-a、無 attestation 要求;命中 → 人親填 + attestation
  - 拿什麼試:本 slug 若 Stage 3 判定未命中的對照;以及一份改了人點流程的對照
- AC-8(G-out-8):假設本 slug 走到自己的 G1/G2/G3,當有人想用五站自動前進來跳過,則跳不過。
  - 從哪看:本 slug 各 gate 的 md 頂欄與 STATUS／HISTORY
  - 看到什麼算對:仍等人寫 G1/G2/G3;`verdict:` 仍是人寫
  - 拿什麼試:本 slug 後續 hop(本 PR 不送 G1)

## 現況圖
誰:寫手
做什麼:寫站產twin
工具:graph.yaml
痛點:停等人類
↓
誰:審者
做什麼:開頁交判定
工具:gate-twin
痛點:例行三停
↓
誰:owner
做什麼:催下一站
工具:STATUS
痛點:等人=站數

## 邏輯圖(ASCII)
```
now (old 7, this slug too)
|-- write station
|   |-- graph hop
|   +-- wait human     [G1 / S3 / G2]
|-- click verdict
|   |-- md top verdict:
|   +-- tick != PASS
|-- STATUS companion
|   +-- wait count = stations
requested (not decided here)
|-- alias 5
|   |-- keep 7 filenames
|   +-- keep G1/G2/ACCEPTED tokens
|-- kill routine human
|   |-- keep matter
|   +-- Ship only default stop
+-- knives
    |-- F1 teeth + 2.1.0 annex
    |-- F2 coordinator
    +-- F3 cut (new slugs only)
```

## Interview Log(推理鏈外顯)
- Q:為什麼現況的痛是「等人次數=站數」,不是「七份檔太多」?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L13-L28 docs/dev/HISTORY.md:L552-L555 docs/dev/HISTORY.md:L569-L573 skills/dev-flow/stage2/nodes/N7-g1.md:L33-L35
  - 推理:brief 明文摺停點不摺檔名。N7-g1 完成條件要 verdict 已記錄,所以預設 hop 走不完。同日母版實跑在 G1、S3、G2 各等一次。若只合併檔案、不停點,人還是按三次。
  - 結論:CONFIRMED 討論對象是例行人停;七檔是 dual-read／in-flight 要留的物質。
- Q:為什麼本檔要把「想達成的結果」和「五站別名」分開寫?
  - 事實:_templates/1-discussion.md:L12-L14 notes/design/five-station-simplify-brief-v3.md:L36-L45
  - 推理:Stage 1 不做決定。五站／殺例行停／Ship 唯人是 owner 帶來的解法構想,已鎖但仍是 Requested solution。Goals 只寫人還能握方向與出貨、舊軌不紅、沒命中不叫人。
  - 結論:CONFIRMED Goals 不寫 Intake／Decide 當目標本身;構想另欄且標未定案。
- Q:為什麼本 slug 設計新 5,自己卻必須走舊 7?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L44 notes/design/five-station-simplify-brief-v3.md:L164-L167 notes/design/five-station-simplify-f0-state-machine.md:L49-L50
  - 推理:F0–F2 期間新開的母版改版軌仍走舊 7,避免雙路線污染觀測。本檔一落地,`docs/dev/five-station-simplify/` 已有站檔,F3 cut 時就是 in-flight。狀態機對舊 7 不建本機。
  - 結論:CONFIRMED 本 slug 是凍舊 7 的第一個活樣本;拿自己試新 5 hop = 違 OC-9。
- Q:為什麼 dual-read 是 2.1.0、而且 F0 不 bump?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L6 notes/design/five-station-simplify-brief-v3.md:L42 notes/design/five-station-simplify-brief-v3.md:L164-L165 devflow-contract.json:L2
  - 推理:現在契約是 `2.0.0`,只認識舊 7。minor 可加五站別名／自動前進欄,但必須讓舊 slug 缺新欄也不紅。F0 只落設計;條文進 F1 annex。一次大爆炸改模板 = 舊軌全紅。
  - 結論:CONFIRMED 本 hop 不 bump;欄位形狀移交 F1。
- Q:為什麼 UI twin／Demo 不能每 feat 必產?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L40 notes/design/five-station-simplify-brief-v3.md:L103-L107 _templates/3-prototype.md:L15-L26 hooks/_stage3_impl.py:L15-L28
  - 推理:現制已是「命中九條才必要」。若摺站後反而每 feat 等人 Demo,等人次數不會下降。純守衛／文件被叫去按 `ACCEPTED` 就是新痛。B1 未命中卻要求 `ACCEPTED` 是 F1 要紅的項。
  - 結論:CONFIRMED UI/flow 才 latch;本 slug 自己是否命中移交 Stage 3,不在本 hop 代判。
- ⚠️ Q:若為了讓謂詞好寫而刪 G1/G2/`ACCEPTED` token,會怎樣?(發散)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L45 notes/design/five-station-simplify-f0-state-machine.md:L189-L207 docs/dev/readme-contract-extract.md:L77-L83 docs/dev/readme-contract-extract.md:L85-L107
  - 推理:舊 7 in-flight 與 dual-read 還要讀這些錨。`gate-consistency` 咬粗體詞。刪 token 會讓舊 slug 與檢查器同時失明。X2 已禁。最極端:新 5 看起來乾淨,舊 7 全紅,採用專案無法 upgrade。
  - 結論:CONFIRMED 刪 token 不是簡化、是新 brief。本 hop 不選牙怎麼釘「仍在」。
- ⚠️ Q:若 F1 為了釘 latch 去改 Stage 1–4 模板,會撞到什麼?(發散)
  - 事實:docs/dev/STATUS.md:L48 notes/design/five-station-simplify-brief-v3.md:L178 _templates/1-discussion.md:L12-L14
  - 推理:Backlog B 凍結模板是為了先做一次完整舊 7 觀測。F1 牙若只加 scripts／annex、不改模板句,可避開。若牙必須改模板,就和觀測實驗搶同一塊布。F0 已禁改模板。
  - 結論:OPEN 共存策略移交 Stage 2／owner;本 hop 不選「先觀測」還是「先釘牙」。
- ⚠️ Q:本 hop 有沒有悄悄變成施工?A1/A2 共檔是不是沒問出口的隱含預設?(盲點)
  - 事實:scripts/build-stage1-html.py:L8-L18 scripts/build-scan-html.py:L3-L9 notes/design/pages-hosting.md:L11-L13 notes/design/five-station-simplify-brief-v3.md:L87-L88
  - 推理:brief 把 A1／A2 寫成兩頁,現行兩支產檔器卻寫同一個 `1-discussion.html`。F0 不改產檔器,所以「兩頁」今天不是兩檔。隱含預設「有站就有獨立頁」不成立。另一隱含預設「記憶裡已有五站」也不成立——ask 無命中。範圍上 owner 已限 Stage 1、不實作 F1–F3;本檔若開始改產檔器就是長大。
  - 結論:CONFIRMED 本 PR 只落討論+掃／審頁 twin;不重開 OC;不改產檔器。Q9 帶假設進 F1。
