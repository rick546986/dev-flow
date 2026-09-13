---
feature: five-station-simplify
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-13
---

# 1. 討論 — 五站簡化（Implementer C：Must-keep 防掏空）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／狀態機落檔,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1 討論調查**；不送 G1、不改 STATUS、不合併。
> 原料:`notes/design/five-station-simplify-brief-v3.md`、`notes/design/five-station-simplify-f0-state-machine.md`、母版模板／gate token／各站 graph。
> C 線強調:例行中閘已在現場被蓋章；若後來 Spec／Build 偷走 Must-keep,任務會**假完成**。本檔必須把「後站不准掏空的清單」寫死。

## Problem
痛:母版七站加上例行 G1／Stage 3 `ACCEPTED`／G2,讓「方向、互動、契約」三次都要等人——等人的次數等於站數。採用現場 2026-08-17 兩案回報的是 G1／G2／G3 **物質洞**(散發路徑、守衛自打),不是蓋章證據。母版 dogfood 另證例行中閘已被 chat 蓋過:「Treat as PASS／都過／可以」落成 `verdict: PASS`,審查物質沒進人腦。摺站若只殺等待、卻讓 Spec／Build 以「已經五站了」拿掉 ID 鏈、反模糊、T 四欄、acceptance seam,勾選會綠、工作沒做完。
受影響:母版維護者、coordinator、採用專案 owner、Build 實作者、Ship 審查者。頻率:每條 full lane；Fast 仍吃 G2 物質。影響:中間卡排隊,或摺完後任務假完成。
現在怎麼繞:owner 在 chat 簽 G1／G2；Agent 把 `verdict: PASS` 落進 md；未跑完的 full lane 靠記憶判斷模板好不好用；F0 只鎖設計、牙與路線都還沒切。

## Context(已知事實)
- F0 十條已鎖(五站別名、殺例行停、Ship 唯人、條件頁、UI twin 條件、Must-keep、dual-read 2.1.0、F0–F3 切刀、in-flight 凍舊 7、禁刪 G1/G2/`ACCEPTED`):notes/design/five-station-simplify-brief-v3.md:L30-L45
- 摺的是預設人類停點,不是完整度;物質(OC、R/S、Demo、Evidence)該留:notes/design/five-station-simplify-brief-v3.md:L13-L28
- 五站是路線別名,舊七份檔名不動;`1-discussion.md`…`7-review.md` 仍是產物:notes/design/five-station-simplify-brief-v3.md:L47-L58
- 表 A:A4／A7 twin 仍產但 latch=否;A10 Ship 是唯一預設人類 latch:notes/design/five-station-simplify-brief-v3.md:L86-L97
- 表 B:B1 Demo 命中九條 trigger 才 latch;`ACCEPTED` 仍人類親填+attestation:notes/design/five-station-simplify-brief-v3.md:L101-L117
- Must-keep M1–M16 少一條=違 brief,不是簡化成功;F1 牙對這張表:notes/design/five-station-simplify-brief-v3.md:L135-L158
- F0 本輪不准改 `_templates/`、README §7 錨、各站 `graph.yaml`、既有牙;不准刪 G1/G2/`ACCEPTED`:notes/design/five-station-simplify-brief-v3.md:L7-L9
- Build→Ship 謂詞:每 T 有 Covers／Files／Verify／Blocked-by;每 T 獨立 review PASS;Files ⊆ 5-tasks 聯集;A8／A9 不得因「想給人看任務板」停:notes/design/five-station-simplify-f0-state-machine.md:L98-L108
- Ship 無自動前進;機械全綠仍必須 HumanWait;代寫 `verdict: PASS`=違 OC-3:notes/design/five-station-simplify-f0-state-machine.md:L110-L120
- 禁則 X2 刪 token、X4 in-flight 套新機、X5 暗改 cap、X7 Agent 書面審冒充判定:notes/design/five-station-simplify-f0-state-machine.md:L189-L201
- rewrite cap 已鎖:hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改 cap;舊 7 不套這三 cap:notes/design/five-station-simplify-brief-v3.md:L131 notes/design/five-station-simplify-f0-state-machine.md:L122-L139
- in-flight = `docs/dev/<slug>/` 已有任一站檔 → 整段舊 7 到 Ship;F0–F2 母版新開軌也舊 7 直到 F3:notes/design/five-station-simplify-brief-v3.md:L160-L167
- STATUS Backlog A 已指本 brief+狀態機;下一刀 F1 teeth+dual-read annex:docs/dev/STATUS.md:L50
- STATUS Backlog B 凍 Stage 1–4 模板直到完整 full-lane 觀測做完 → F1 牙只准 scripts／annex:docs/dev/STATUS.md:L48
- 現行契約仍是七份文檔+G1／G2／G3:docs/dev/readme-contract-extract.md:L7-L17
- Gate token 釘死:G1=Owner Calls 全裁決+抽查下層誤放;G2=R/S 全審+DD+Profile+Demo verdict;G3=本次 S 全綠+回歸+現象+Evidence 八點:scripts/check-gate-tokens.sh:L44-L60
- G1／G2／G3 定義句與四眼順序:docs/dev/readme-contract-extract.md:L68-L107
- 2-decision 頂註:G1=人工核准後才寫規格;送審要人寫 verdict: _templates/2-decision.md:L13-L14 _templates/2-decision.md:L68-L72
- Stage 2 graph 預設路經 `N7-g1`(例行人類停點節點):skills/dev-flow/stage2/graph.yaml:L53-L57
- 4-spec 反模糊三律+G2 twin 必產: _templates/4-spec.md:L18-L28 _templates/4-spec.md:L40-L45
- Stage 4 graph 預設路經 `N6-g2`:skills/dev-flow/stage4/graph.yaml:L93-L98
- 5-tasks 每 T 必填 Covers／Files／Verify／Blocked-by: _templates/5-tasks.md:L50
- 6-notes 逐 T seam=RED→GREEN→scope→Verify→independent T review→PASS→commit→記帳: _templates/6-implementation-notes.md:L104-L137
- 契約抽同一條 seam:docs/dev/readme-contract-extract.md:L28-L34
- Stage 3:`ACCEPTED` 人類親填+attestation;Agent 禁代填: _templates/3-prototype.md:L19-L22 _templates/3-prototype.md:L128-L129
- Human 判定正本=同目錄 md 頂欄 `verdict:`;勾選≠PASS:notes/design/gate-verdict-write.md:L8-L11
- Real-world 三站銜接:Stage 1 節→條件 Demo→S 級 Operational Context:notes/design/real-world-interaction.md:L16-L22
- dogfood-ping G1:owner chat「Treat G1 as PASS」;reviewers=[user];owner 自審有記錄:docs/dev/dogfood-ping/2-decision.md:L110
- dogfood-ping G2:同日 owner chat 簽 `verdict: PASS`:docs/dev/dogfood-ping/4-spec.md:L14-L16 docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L7-L10
- 同一 dogfood 的 Stage 3 Human verdict 曾留空、owner chat 仍准開 Stage 4:docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9
- integration-before-verdict:G1 按 owner chat「都過」落檔:docs/dev/integration-before-verdict/2-decision.md:L89
- diagram-ir-gate:G1 按 owner chat「可以」落檔:docs/dev/diagram-ir-gate/2-decision.md:L112
- 2026-08-17 兩個採用專案回報的母版缺陷就被叫做 G1／G2／G3;路徑是現場踩到→口頭轉述→owner 中繼:notes/dispatch-accounting-symmetry.md:L10 notes/dispatch-accounting-symmetry.md:L361
- STATUS 寫明 G1／G2／G3「全是現場真踩到的」;SDC 因零現場痛不做:docs/dev/STATUS.md:L49
- 2026-08 派工仍寫:母版自己還沒拿 full lane 1→7 當觀測實驗,且當時禁改 Stage 1–4 模板免污染觀測:notes/dispatch-parallel-feature-gaps.md:L279-L285
- 契約正本仍 `2.0.0`;runtime 只聲明支持 `2.0.0`;plugin `3.24.0`:devflow-contract.json:L1-L3 hooks/runtime-capabilities.json:L1-L4
- doctor:專案契約版本必須 ∈ plugin `supported_contract_versions`,否則 fail-closed、不靜默退回舊行為:hooks/_doctor_impl.py:L193-L202
- 節點 MD／graph 不複製進採用專案;更新=`marketplace update`+`plugin update`;marketplace 單一 entry `./`:skills/dev-setup/SKILL.md:L16 skills/dev-setup/SKILL.md:L62-L68
- 第 1 站審頁 `build-stage1-html.py` 與掃頁 `build-scan-html.py` 預設都寫同名 `1-discussion.html`:scripts/build-stage1-html.py:L8-L18 scripts/build-scan-html.py:L3-L9
- 受影響面(後續刀才動,本 hop 不動):`_templates/` 七份、`skills/dev-flow/stage*/graph.yaml`、`scripts/check-gate-tokens.sh`、`docs/dev/readme-contract-extract.md` §7、`scripts/build-gate-twin.py`、`hooks/_stage3_impl.py`、coordinator(尚未存在)、採用專案 upgrade 到 2.1.0 之後的路線。

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 母版 owner(tony／rick) | 摺掉例行等人,但不丟完整度;Ship 仍由人出貨 | 裁 F0、簽 G1／G2／G3、寫 md `verdict:` | F0 brief、本 tree、chat 隊列 | 採用現場是否仍逐字審中閘 | GitHub、Cursor chat |
| 派工／討論 agent | 把調查寫成 1-discussion;停在閘門等人 | 寫本目錄討論檔 | 模板、brief、白名單 | owner 會不會真讀 twin | Cloud Agent、PR |
| coordinator(F2 後) | 謂詞真就 hop,假就停修,不改問人 | 讀謂詞、禁寫判定 | 表 A／B、狀態機 | 現場會不會要求「順便問人」 | 尚未落地 |
| Build 實作者 | 把 T 勾完往前走 | 寫 5-tasks／6-notes／碼 | 4-spec+5-tasks | Spec 有沒有把 Must-keep 寫進 R/S | git、測試 |
| 獨立 T reviewer | 擋假綠 T | 給該 T PASS／FAIL | 該 T Files／Verify | 若 seam 被偷走,沒有 RED 可審 | 另一 session |
| Ship 審查者 | 出貨樹=審過的樹 | 寫 7-review `verdict:` | G3 八點、coverage | 中閘沒等人之後,物質有沒有被掏空 | 瀏覽器審頁 |
| 採用專案 owner | 少停、別在 public 洩漏現場 | 系統外(回報靠口頭／去識別化檔) | 自己踩到的 G1／G2／G3 洞 | 母版何時切五站 | Email、口頭、去識別化貼檔 |
| in-flight slug 執行者 | 走完手上那條舊 7,不被中途改路線 | 既有 graph／模板 | 自己目錄已有站檔 | F3 cut 會不會誤折自己 | 既有 hop |

### Current Journey
正式 SOP:full 走 1→2→(3)→4→5→6→7,G1／條件 S3／G2／G3 各等人寫判定。實際做法(沒有五站、也常沒有真審)如下。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 討論 agent | 寫 1-discussion,status 留 draft | `_templates/1-discussion.md` | owner 看不看 | 討論檔 | 調查若沒鎖 Must-keep,後站可裝沒看見 |
| 2 | 收斂者 | 寫 2-decision,開 G1 twin | Stage 2 graph `N7-g1` | owner | twin+md | 例行停;人用 chat 蓋章 |
| 3 | owner | chat「Treat as PASS／都過／可以」 | Cursor chat | — | `verdict: PASS` | 方向卡沒被讀完也過 |
| 4 | 助手 | 有 trigger 仍可能 chat 准開 Stage 4,Demo 欄空 | 3-prototype | owner 親填 attestation | 空欄或後補 | 互動停點也被繞 |
| 5 | 規格者 | 寫 4-spec,開 G2 twin | Stage 4 `N6-g2` | owner | R/S+Profile | 第二次例行停;再蓋一次章 |
| 6 | 實作者 | 切 T、跑 seam、等人審每個 T | 5-tasks／6-notes | 獨立 reviewer | checkbox | 若四欄／seam 被省,勾選假完成 |
| 7 | owner | Ship／G3 才認真看(或不看) | 7-review | 自己 | `verdict:` | 中間三次已耗盡注意力 |
| 8 | 採用現場 | 踩到母版洞,口頭轉述 | 系統外 | owner 中繼 | 派工單 G1／G2／G3 條 | 沒標準回報口;痛是真的 |

### Workarounds
- owner 用 chat 當閘門:「Treat G1 as PASS」「G2 PASS」「都過」「可以」。系統留下 `verdict: PASS`,不留下「讀過哪五格」。
- Agent 把口頭章落進 md 頂欄;HTML 勾選本來就不是判定,現場連勾選都省了。
- dogfood-ping 用極小 CLI 走完 1→7,仍在同一日 chat 簽 G1 與 G2;Stage 3 attestation 可空著先開 Stage 4。
- 採用現場洞靠 owner 口頭中繼進 `notes/dispatch-accounting-symmetry.md`;不進 public issue。
- 未做完的 full-lane 觀測,靠大 feat 記憶判斷模板;STATUS 仍留「下一輪才跑觀測」那列。
- 這些步驟常不留「這條 Must-keep 後來去哪」或「這次 G1 抽查了哪條下層誤放」。

### Exceptions
- Fast lane 合法省略 Stage 1–3,仍吃 G2 物質(Profile／Demo 條件);不是本包要廢 Fast。
- Owner Call 可明示跳過 Stage 3;B1 沒命中則不產 Demo、不 latch。
- in-flight:目錄已有任一站檔 → 整段舊 7,含例行 G1／G2,直到 Ship。
- F0–F2 期間新開的母版改版軌仍走舊 7(brief §6)。
- owner 自審是有記錄的最後手段;dogfood-ping G1 已走這條,不假裝四眼。
- `[Assumption]` 採用現場仍用同一套 chat 蓋章過 G1／G2:無採用逐字稿;風險=高(若為假,「殺例行停」的現場理由變弱,Must-keep 仍在);期限=F1 annex 前抽一案,過期擋本 slug G2。
- `[Assumption]` 後站寫手會用「已經五站了」省略 M11／M3／M1:無未來 log;風險=高(若為假,F1 牙只防漂移不防現在);期限=Stage 2 對帳,過期擋把「可選四欄」寫進 Decision。
- `[Assumption]` A1 審頁與 A2 掃頁將繼續共寫 `1-discussion.html`:兩支產檔器同 dest;風險=中(若為假,F1 不必為雙檔名加牙);期限=F1 annex。

### Evidence
- F0 書面鎖定:notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md;Owner 已核准(檔頭)。本 hop 只調查、不改那兩檔。
- 本 tree 已核:上列 Context 出處(2026-09-13 讀過,行段支持斷言)。
- 母版 dogfood 蓋章鏈:docs/dev/dogfood-ping/2-decision.md:L110、docs/dev/dogfood-ping/4-spec.md:L14-L16、docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L7-L10。
- 同型 chat 落章:docs/dev/integration-before-verdict/2-decision.md:L89、docs/dev/diagram-ir-gate/2-decision.md:L112。
- 採用現場兩案回報被叫做 G1／G2／G3 **物質洞**(不是蓋章證據):notes/dispatch-accounting-symmetry.md:L10、L361;STATUS 複述「現場真踩到」:docs/dev/STATUS.md:L49。
- 觀測實驗延後、禁先改 1–4 模板:notes/dispatch-parallel-feature-gaps.md:L279-L285;STATUS Backlog B:docs/dev/STATUS.md:L48。
- 採用 hop 身分:skills/dev-setup/SKILL.md:L16、L62-L68;doctor 握手:hooks/_doctor_impl.py:L193-L202;契約仍 `2.0.0`:devflow-contract.json:L1-L3。
- `[Assumption]` 三條見 Exceptions;採用逐字稿／未來寫手 log／產檔器分檔皆無。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「採用現場也 chat 蓋章」為假 → 殺例行停的現場理由變弱,但不改 Must-keep | 高 | 抽一採用案:G1／G2 twin 是否有人讀五格再寫 `verdict:` | F1 annex 前／owner;過期擋本 slug G2 |
| A1／A2 其實已分檔 → F1 不必為雙檔名加牙 | 中 | 讀兩支產檔器 dest 與 Pages 清單是否已分檔 | F1 annex／寫手 |
| 「後站會偷 Must-keep」為假 → F1 牙主要防未來漂移 | 高 | Stage 2 對帳:Decision 有無把 M1／M3／M11 標成可選 | Stage 2／收斂者;過期擋 G2 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | 調查必須跟 brief／狀態機,不跟對話記憶 | notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名) | 是 |
| 現行七站／gate／牙 | 要證明摺的是停點不是物質 | docs/dev/readme-contract-extract.md、scripts/check-gate-tokens.sh、_templates/2-decision.md、_templates/4-spec.md、_templates/5-tasks.md、_templates/6-implementation-notes.md、skills/dev-flow/stage2/graph.yaml、skills/dev-flow/stage4/graph.yaml | 是(使用者點名母版) | 是 |
| dogfood 蓋章 | 現場／on-site 痛:例行閘被 chat 蓋 | docs/dev/dogfood-ping/2-decision.md、4-spec.md、DOGFOOD-NOTES.md | 是(本 tree 公開 dogfood) | 是 |
| 同型母版 feat | 證明不是單案 | docs/dev/integration-before-verdict/2-decision.md、docs/dev/diagram-ir-gate/2-decision.md | 是 | 是 |
| 採用現場回報 | 兩個專案踩到的**物質洞**被叫做 G1／G2／G3 | notes/dispatch-accounting-symmetry.md、docs/dev/STATUS.md | 是(本 tree) | 是 |
| 採用 hop 身分 | marketplace 可換 hops、doctor 仍可綠 | skills/dev-setup/SKILL.md、hooks/_doctor_impl.py、devflow-contract.json | 是(本 tree) | 是 |
| 採用逐字稿 | 驗證「現場也蓋章」 | 無;public repo 禁收公司路徑 | 禁 | 否 |

## Goals
- G-out-1:人預設只在出貨停下來寫判定;中間站不等「請按提交判定」。謂詞假 = 停在該站修,不是改問人。
- G-out-2:摺站之後,M1–M16 每一項仍成立。少一項被人看成違規,不能看成簡化成功。
- G-out-3:後來寫規格／切任務的人,不能把「已經五站了」當成省略 ID 鏈、反模糊、**T 四欄、或 RED→獨立審查 seam** 的理由。這兩項是 Owner-locked,不是未定案。省略後的勾選必須仍看得出是未完成。
- G-out-4:人殺掉的是「例行等人」;Agent 代寫 `ACCEPTED`／Ship `PASS`、無 attestation 的 `ACCEPTED`,仍被當成沒寫。
- G-out-5:已開工 slug 繼續走舊 7 直到出貨;舊契約讀舊 7 不一次變紅。
- G-out-6:命中互動 trigger 時,人仍要親做 Demo 並寫 attestation;沒命中不產頁、不等第二次人。
- G-out-7:本討論列出的 Must-keep 與現場痛點,到規格／任務時每條都有去向(處理／刻意維持／Non-Goal／另開 slug／仍待驗),不能無聲消失。
- G-out-8:本 slug 是第一個 live freeze 樣本——自己的出貨路徑仍是舊 7 直到 Ship;不拿自己當新 5 的第一個白老鼠。

## Requested solution（候選，未定案）
- 預設路線用五個別名 Intake→Decide→Spec→Build→Ship;檔名家族不換。
- 例行 G1／S3-`ACCEPTED`／G2 不再是人類必停;token、twin、graph 節點、牙都留。
- Ship(舊 G3 物質)保持唯一人類必停;coordinator 禁代寫 `verdict:`。
- 條件頁走表 A／B:生成謂詞假不產頁;latch 假不准問人。
- Must-keep 進後站 disposition 語法候選:每條 M 用 `M11 → R-x/S-y | Non-Goal:<reason>`(Q9 種子);不另發 ID 鏈。
- F1 才釘牙與 dual-read annex;F2 才寫 coordinator;F3 才切新 slug 預設路線。
- 本 hop 不選定牙長在哪支腳本、annex 欄位名、或 event schema。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`graph.yaml`、gate token、STATUS、HISTORY、契約版本。
- 本 hop 不送 G1;status 留 draft;不合併。
- 不刪 G1／G2／`ACCEPTED` 檔或 token。
- 不把 in-flight slug 折成五站。
- 不寫 coordinator 碼(F2)。
- 不把七份文檔改名成新家族。
- 不重開 F0 十條;翻任何一條=新 brief。
- 不新增第二條 Journey／Actor ID 鏈。
- 不把「蓋章很煩」解讀成「物質也可以省」。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:full
- [x] Q2:本 hop 是否只 Stage 1 調查、不改 STATUS、不合併?→ 使用者:是
- [x] Q3:F0 十條是否已鎖、本討論不得翻案?→ brief OC-1…OC-10;翻=新 brief
- [x] Q4:摺的是停點還是完整度?→ brief:停點;Must-keep 一項都不能因摺站消失
- [x] Q5:Goals 是否只寫結果、解法另欄?→ 本檔已照做
- [~] Q6:採用現場是否仍用 chat 蓋章過 G1／G2?(帶假設:是;風險=高;期限=F1 annex 前抽一案,過期擋本 slug G2)
- [x] Q7:F1 牙最少拒收謂詞?→ 最小集已鎖:T 缺 Covers／Files／Verify／Blocked-by → 紅;無 RED 輸出或 reviewer=implementer → T 未完成;S 含 TBD／不可測 → 紅。牙長在 scripts／annex(Backlog B 凍 Stage 1–4 模板)。
- [>] Q8:dual-read 2.1.0 欄位與舊檔不紅的缺省?→ 移交 F1 annex
- [x] Q9:Must-keep disposition 引用語法?→ 種子:`M11 → R-x/S-y | Non-Goal:<reason>`。不另發 ID 鏈;每條高影響 M 必有去向。
- [>] Q10:coordinator event 與 rewrite cap 計數落點?→ 移交 F2
- [>] Q11:B1 命中與「chat 准開下一站」並存時,attestation 空是否仍機械拒?→ 移交 Stage 2(現行牙已拒;五站後要保持)
- [x] Q12:本 slug 自己 in-flight 之後走舊 7 還是等 F3?→ OC-9 + brief §6 已鎖。本資料夾已存在 = in-flight,整段舊 7 直到 Ship。母版 F3 前新開改版軌也走舊 7。不是交接、不是等 F3 再決定。

## Constraints
- 本 PR 不宣稱 G1 PASS;不改 STATUS／HISTORY。
- 討論盲下游:本檔不指定腳本／API／元件當目標。
- **Owner-locked Constraint:T 四欄(Covers／Files／Verify／Blocked-by)與 RED→獨立審查 seam 不可選。**不是 Requested solution 的未定案;省略後勾選仍算未完成。
- **Owner-locked rewrite cap:**hop≤2／Decide≤1／Goal reopen≤1;用盡 → Escalated;不准暗改 cap。舊 7 不套這三 cap。
- **採用 hop 身分:**graph／hooks 住方法包。未 upgrade 到 2.1.0 dual-read 之前,`marketplace update` 可換 hops,而 doctor 仍可因契約 `2.0.0` 握手綠。未 upgrade = 必須仍走舊 7,不得遠端改線。
- 詞條(語言,不是方案):**五站**=Intake／Decide／Spec／Build／Ship 路線別名,不是新檔名。**例行停點**=預設人類必停的 G1／S3-`ACCEPTED`／G2。**Must-keep**=brief §5 M1–M16。**掏空**=後站用「已五站」省略 Must-keep。**假完成 T**=checkbox 已勾,但缺 Covers／Verify／RED 輸出／獨立 reviewer。**蓋章**=chat 口頭 PASS、五格未讀。**latch**=表 A／B 規定必須等人的列。**dual-read**=2.1.0 同時讀舊 7 與新 5。**in-flight freeze**=已有站檔的 slug 走舊 7 到 Ship。本 hop 不寫進長期記憶。

### F1 移交種子(不是施工)
- Backlog B 凍 Stage 1–4 模板 → 本 slug F1 牙只准長在 `scripts/` 與 annex,不准改 `_templates/` 1–4。
- in-flight 偵測:F3 cut 當下 `docs/dev/<slug>/` 已有任一站檔(1–7 任一 md)→ 整段舊 7 到 Ship。本資料夾已存在 = 已 in-flight。
- Q6 過期 → 擋本 slug G2(不得把「現場都蓋章」當已核事實)。

### Stage 1 必須帶走、後站不准掏空
後站若把下表當「簡化細節」拿掉,任務看起來做完、工作沒做完。本表是調查產出,不是施工單。

| 帶走什麼 | 若被 Spec／Build 偷走 | 人看見什麼 | F1 拒收謂詞 | 本檔鎖在哪 |
|---|---|---|---|---|
| M1 ID 鏈 R→S→T→test→D→F;測試名含 S-id | 測試不叫 S;鏈斷。**不是**「T 缺 Covers」(那是四欄,見 M11) | Ship coverage 對不上 S | 測試名不含 S-id → 紅 | G-out-3、AC-3 |
| M2 圍欄 | 實作者翻 1／2／3 補洞 | spec 空洞仍往下寫(**不是** checkbox 假完成) | — | G-out-7 |
| M3 反模糊三律 | S 寫適當／TBD／不可測 | 測試空轉也綠 | S 含 TBD／不可測 → 紅 | G-out-3、AC-3 |
| M4 Real-world→Demo→OC | 無 trigger 也省、有 trigger 也省 | UI 綠燈但人做不完 | — | G-out-6、AC-6 |
| M5 人寫 `ACCEPTED`／Ship `PASS` | Agent 代填 | 出貨 verdict 是機器的 | — | G-out-4、AC-4 |
| M6 G3 Evidence 八點 | 只留測試綠 | 現象沒被看過 | — | G-out-2 |
| M7 Profile+`fast`+`high` 拒 | 高風險走 fast | runtime 本該拒的包出貨 | — | G-out-2 |
| M8 DBC 條件式 | 整節刪 | 設計邊界沉默 | — | G-out-2 |
| M9 Files ⊆ 5-tasks | 範圍外檔跟著合 | 任務板說沒改、diff 有改 | 缺 Files 欄或 Files ⊈ 5-tasks 聯集 → 紅 | G-out-3、AC-3 |
| M10 驗證五律 | 派工者下場修、無原始輸出 | 審查看摘要當證據 | 無原始輸出 → 紅 | G-out-3 |
| M11 T seam + 四欄 | 跳 RED／跳獨立審／缺四欄 | **假完成 T**(C 線主風險) | 缺 Covers／Files／Verify／Blocked-by → 紅;無 RED 輸出或 reviewer=implementer → T 未完成 | G-out-3、AC-3 |
| M12 author≠approver | 自己簽自己 | 四眼只剩欄位 | — | G-out-4 |
| M13 html 重生 | 只丟 raw md | 人審不到頁(**不是** checkbox 假完成) | — | 本 hop 仍產 html |
| M14 不可逆才 Quiz | 不可逆省 Quiz;或把 Quiz 當每次必停 | 不可逆無 Quiz = 危險合進去;每次 Quiz = 把例行人停加回。Quiz ≠ 預設第三停 | 不可逆且無 Quiz → 紅;非不可逆被強制 Quiz 當例行停 → 違 G-out-1 | G-out-1 |
| M15 token／檔仍在 | 刪 G1／G2／`ACCEPTED` 好寫謂詞 | dual-read／舊 7 一次紅 | — | G-out-5、AC-5 |
| M16 F0 不改 graph／牙 | F0「順便」改路線 | 觀測被污染(**不是** checkbox 假完成) | — | Non-Goals |

帶走但不是 M 編號(後站一樣不准無聲拿掉):

| 帶走什麼 | 若被偷走 | 人看見什麼 | 鎖在哪 |
|---|---|---|---|
| rewrite cap:hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改 | 用盡仍 hop 或 reset 計數 | 重寫無限、cap 變裝飾 | Constraints、Q10 計數落點仍移交 F2 |
| 採用 hop 身分:未 2.1.0 dual-read 前,marketplace 可換 hops 而 doctor 仍綠 | 當「doctor 綠 = 路線沒變」 | 採用端被遠端改線 | Constraints、G-out-5 |
| 本 slug = live freeze 樣本 | 拿自己當新 5 白老鼠 | 觀測被自己污染 | G-out-8、Q12 |

## 驗收雛形
- AC-1(G-out-1):假設一條新 slug 已走完 Decide／Spec／Build 且中間 latch 未命中,當 coordinator 評謂詞,則它不在 G1／G2 頁等人按提交判定;謂詞假時停在該站修。
  - 從哪看:該 slug 的前進紀錄／停點(人可核對的 hop 或拒絕理由)
  - 看到什麼算對:中間無「請人審 A4／A7」;停修理由是謂詞假,不是「先問 owner 要不要繼續」
  - 拿什麼試:F0 鎖定後的下一刀假資料(後續造);本 hop 不跑 coordinator
- AC-2(G-out-2):假設有人宣稱「五站已簡化」但 M 表少一項,當對照 brief §5,則該宣稱被看成違規。
  - 從哪看:那次改動的規格／任務／牙輸出,對照 M1–M16
  - 看到什麼算對:少項被點名;沒有「已經五站了」當省略理由
  - 拿什麼試:本檔 Constraints 表;以及一份故意拿掉 T 的 Verify 欄的對照稿
- AC-3(G-out-3):假設 Build 寫了一個 T,當人只看該 T,則仍看得到 Covers 的 S-id、Files、Verify、Blocked-by,以及 RED→獨立 reviewer 的縫;缺任一項不能當完成。
  - 從哪看:該份 5-tasks 的 T 卡,加上 6-notes 該 T 的 TDD／review 紀錄
  - 看到什麼算對:四欄非空;有失敗測試輸出與不同於實作者的 reviewer;checkbox 在缺欄時不能冒充完成
  - 拿什麼試:現行 `_templates/5-tasks.md`／`6-implementation-notes.md` 必填句;一份「Verify: 看起來沒問題」的假 T
- AC-4(G-out-4):假設中間例行停已殺掉,當 Agent 寫入 `ACCEPTED` 或 Ship `PASS`,則系統當沒寫。
  - 從哪看:該 md 頂欄／attestation 行,以及試圖 hop 的拒絕
  - 看到什麼算對:無人類 attestation 的 `ACCEPTED` 不得離 Spec;無人 `verdict: PASS` 不得 Done
  - 拿什麼試:dogfood-ping 曾空著 attestation 仍開 Stage 4 的對照(現行痛);後續牙必須擋這型
- AC-5(G-out-5):假設 F3 cut 當下某 slug 已有站檔,當路線被求切五站,則該 slug 仍走舊 7 到 Ship;舊 7 讀檔不因 2.1.0 一次變紅。
  - 從哪看:該 slug 目錄與契約讀檔結果
  - 看到什麼算對:仍有 G1／G2 例行停(舊路);dual-read 綠;沒有五站狀態寫入
  - 拿什麼試:本 repo 任一已有 1–7 檔的 slug;不是本 hop
- AC-6(G-out-6):假設本次改動命中「新前端／改變下一步／多種互動」之一,當人要進 Build,則已有人類 `ACCEPTED`+attestation;未命中則無 Demo 頁、無第二次人停。
  - 從哪看:3-prototype 是否存在、Human verdict 行、A5 是否建頁
  - 看到什麼算對:命中→有 attestation;未命中→n-a 原因,不是空白
  - 拿什麼試:純守衛 feat vs 改人點流程的 feat(後續造)
- AC-7(G-out-7):假設本檔 Constraints 表列了一條 Must-keep 或 Journey 痛點,當人讀到 Spec／Build,則該條有去向。
  - 從哪看:Stage 2→4 之間的去向帳,以及對應 R/S 或 T
  - 看到什麼算對:每條高影響列都有 `M11 → R-x/S-y | Non-Goal:<reason>` 形去向;沒有「Stage 1 寫過、後面消失」
  - 拿什麼試:本檔「假完成 T」「chat 蓋章」「Demo 欄空仍開 Stage 4」三列
- AC-8(G-out-8):假設本 slug 走到自己的 G1／G2／G3,當有人想用五站自動前進跳過,則跳不過。
  - 從哪看:本目錄站檔與被要求的 hop
  - 看到什麼算對:仍有例行 G1／條件 S3／G2／G3;沒有五站自動前進寫入
  - 拿什麼試:本資料夾已存在 = in-flight;不是後續造的假 slug

## 現況圖
誰:owner
做什麼:對話簽閘門
工具:chat／PR
痛點:蓋章當審查
↓
誰:派工助手
做什麼:每站停等人
工具:graph／twin
痛點:中間卡排隊
↓
誰:實作者
做什麼:摺站省完整度
工具:5-tasks
痛點:任務假完成

## 邏輯圖(ASCII)
```
now
|-- wait x3
|   |-- G1 chat PASS          [dogfood / 都過 / 可以]
|   |-- S3 column empty       [chat still opens 4]
|   +-- G2 chat PASS          [same day]
|-- fold
|   |-- kill wait             [OC-2]
|   |-- keep substance        [M1-M16]
|   +-- steal keep?           [hollow]
|       |-- drop T fields
|       |-- skip RED/review
|       +-- fake-done T       [C risk]
+-- ship
    |-- only default human stop
    +-- agent PASS = missing
adopted
|-- marketplace update
|-- contract still 2.0.0
+-- doctor may stay green
```

## Interview Log(推理鏈外顯)
- Q:為什麼要摺例行 G1／G2,又為什麼不能把 token 一起刪?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L13-L28 notes/design/five-station-simplify-brief-v3.md:L30-L45 skills/dev-flow/stage2/graph.yaml:L53-L57 skills/dev-flow/stage4/graph.yaml:L93-L98 scripts/check-gate-tokens.sh:L44-L60
  - 推理:graph 把人類停寫進預設 hop。等人的次數被站數綁死。物質(OC 全裁決、R/S、Profile、Demo 條件)與「按提交判定」不是同一物。刪 token 會讓 dual-read 與 in-flight 舊 7 失去錨。
  - 結論:CONFIRMED 摺停點、留物質與檔;刪 token=新 brief,不是本討論可選。
- ⚠️ Q:現場最近一次走完閘門時,人是真審還是蓋章?
  - 事實:docs/dev/dogfood-ping/2-decision.md:L110 docs/dev/dogfood-ping/4-spec.md:L14-L16 docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L7-L10 docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9 docs/dev/integration-before-verdict/2-decision.md:L89 docs/dev/diagram-ir-gate/2-decision.md:L112
  - 推理:母版自己的極小 dogfood 在同一日用 chat 把 G1 與 G2 簽成 PASS,且 Demo 欄可空著先開 Stage 4。另外兩條母版 feat 把「都過／可以」落成 G1 PASS。這是 on-site 蓋章,不是「審頁五格被讀完」。採用現場是否同一手勢 = `[Assumption]`。
  - 結論:CONFIRMED 母版 dogfood 的例行中閘已被蓋章;殺等待有現場依據。採用現場外推帶假設,期限 F1 前抽案。
- ⚠️ Q:Must-keep 被偷走時,為什麼會變成「任務假完成」而不是「比較乾淨的五站」?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L135-L158 notes/design/five-station-simplify-f0-state-machine.md:L98-L108 _templates/5-tasks.md:L50 _templates/6-implementation-notes.md:L104-L137 docs/dev/readme-contract-extract.md:L28-L34
  - 推理:Build 謂詞與現行 T 自足律靠四欄+seam。若 Spec 寫模糊 S(偷 M3),或 Build 讓 Verify 變成「看起來沒問題」、跳 RED、讓實作者自審(偷 M11／M10／M12),checkbox 仍可勾。Ship coverage 對不到 S,現象沒被看過。brief 寫明少一條=違規。C 線把這當成主風險:等人消失後,寫手最容易拿完整度填那個洞。
  - 結論:CONFIRMED Stage 1 必須帶走 M 表與假完成定義;後站省略四欄／seam=未完成,不是簡化。
- Q:Stage 1 還要鎖住哪些東西,Spec／Build 才掏不空?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L101-L117 notes/design/five-station-simplify-f0-state-machine.md:L110-L120 notes/design/gate-verdict-write.md:L8-L11 notes/design/real-world-interaction.md:L16-L22
  - 推理:只寫「五站＋少等人」不夠。必須連 B1 latch、Ship 禁代寫、md 頂欄才是判定、Real-world 三站銜接、in-flight／dual-read 一起帶走。否則 Spec 會把 Demo 當已廢中閘,Build 會把任務板當可選。
  - 結論:CONFIRMED 帶走清單=Constraints 表+G-out-1…7;去向語法移交 Stage 2。
- Q:採用現場的 G1／G2／G3 痛,跟「蓋章」是同一件事嗎?
  - 事實:notes/dispatch-accounting-symmetry.md:L10 notes/dispatch-accounting-symmetry.md:L361 docs/dev/STATUS.md:L49 notes/dispatch-parallel-feature-gaps.md:L279-L285
  - 推理:採用兩案回報的是母版缺陷(散發路徑、守衛自打),名字剛好叫 G1／G2／G3,證明現場真的在走這些閘,痛是實的。那是「閘的物質有洞」,**不是**蓋章證據。蓋章證據只來自母版 dogfood 三案(Treat as PASS／都過／可以)。兩件事都真:物質要留(且要有牙),等待不該例行。2026-08 連母版自己的完整觀測都還在排隊,更不能先改模板污染觀測——F0 禁改模板與 Backlog B 一致。
  - 結論:CONFIRMED 採用回報=物質洞;dogfood 蓋章支持殺例行停。兩者不可互相取消、不可互相冒充。
- Q:為什麼 Ship 必須留下、中間機械綠也不能自動 Done?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L38 notes/design/five-station-simplify-f0-state-machine.md:L110-L120 docs/dev/readme-contract-extract.md:L68-L74
  - 推理:人握方向與出貨。中間卡改謂詞。若機械綠可寫 `PASS`,蓋章只是從 G1 搬到 Ship,而且 Agent 可以代搬。四眼在 Ship 仍要人。
  - 結論:CONFIRMED 唯一預設人停=Ship;Agent 寫 PASS=未寫。
- ⚠️ Q:若只殺等待、不釘 Must-keep 牙,最極端會怎樣?(發散)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L158 _templates/4-spec.md:L40-L45 docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9
  - 推理:寫手會複製 dogfood 捷徑:chat 准下一站、欄位空、T 只留標題。五站 hop 更快,假完成更多。最極端:G1／G2 檔被刪去「好寫謂詞」,舊 7 一次紅,in-flight 無路。
  - 結論:CONFIRMED 最少拒收謂詞已鎖(Q7):缺四欄→紅;無 RED／reviewer=implementer→T 未完成;S TBD／不可測→紅。牙長在 scripts／annex,形狀細節仍移交 F1。
- Q:採用端 hop 身分在 2.0.0 時會怎樣?
  - 事實:skills/dev-setup/SKILL.md:L16 skills/dev-setup/SKILL.md:L62-L68 hooks/_doctor_impl.py:L193-L202 devflow-contract.json:L1-L3 notes/design/five-station-simplify-brief-v3.md:L160-L169
  - 推理:graph／hooks 住方法包。marketplace update 換 hops。契約握手仍是 `{2.0.0}`,doctor 可繼續綠,路線卻已被遠端改。brief 才寫「upgrade 到 2.1.0 才看五站;未 upgrade = 舊 7」。
  - 結論:CONFIRMED 未 dual-read 之前,marketplace 可改 hops 而 doctor 仍綠。這是帶走項,不是 F1 才發現的驚喜。
- Q:本 slug 自己走舊 7 還是等 F3?rewrite cap 是不是未定案?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L44 notes/design/five-station-simplify-brief-v3.md:L131 notes/design/five-station-simplify-brief-v3.md:L160-L167 notes/design/five-station-simplify-f0-state-machine.md:L122-L139
  - 推理:OC-9 + §6 已鎖。本資料夾已有站檔 = in-flight,整段舊 7 到 Ship。母版 F3 前新開軌也舊 7。這不是交接。hop≤2／Decide≤1／Goal reopen≤1 用盡 Escalated,不准暗改 —— 也已鎖,不是 Requested solution。
  - 結論:CONFIRMED Q12 `[x]`;本 slug = 第一個 live freeze 樣本(G-out-8)。cap 進 Constraints,不進未定案。
- ⚠️ Q:本 hop 有沒有把 F0 當成已經施工?範圍有沒有長大?(盲點)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L7-L9 docs/dev/STATUS.md:L48 docs/dev/STATUS.md:L50 本 hop brief(只 Stage 1、不改 STATUS、獨立)
  - 推理:F0 已落盤是 Context,不是本 PR 的實作範圍。隱含預設「後站會偷 Must-keep」無未來 log,已標 Assumption。Q6 過期改擋本 slug G2。A1／A2 共寫 `1-discussion.html` 帶假設進 F1。Backlog B 凍模板 → F1 牙只准 scripts／annex。本檔不改模板、不送 G1,避免跟 F0 禁令撞車。
  - 結論:CONFIRMED 本 PR 只落討論;不重開十條;不改 STATUS。Q6 過期擋本 slug G2。
