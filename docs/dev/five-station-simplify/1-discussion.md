---
feature: five-station-simplify
stage: 1-discussion
status: draft
owner: implementer-b
reviewers: []
updated: 2026-09-13
---

# 1. 討論 — 摺例行停點、不摺完整度

> 用途:發散。**不做決定**。Lane = **full**。本 hop 只 Stage 1,不送 G1,不改 STATUS,不寫 F1 牙、不改名模板、不刪 gate。
> Owner 已鎖意圖寫在 Requested solution,不是 Goals。未核敘述標 `[Assumption]`。
> 原料(使用者指名):`notes/design/five-station-simplify-brief-v3.md`、`notes/design/five-station-simplify-f0-state-machine.md`、STATUS Backlog、現行七站模板與牙。本票自己仍走七站。
> Implementer B 獨立稿。角度:誰會被錯刪中間 gate 傷害、採用產品 repo 的爆炸半徑。不讀 A/C 稿。

## Problem
誰:母版 owner、full-lane 實作者、G1/G2/Demo 被叫來的人、以及 marketplace 更新就吃到新 hops 的採用專案維護者。
痛:七站加上例行 G1 / S3-`ACCEPTED` / G2,讓「方向、互動、契約」三次都要等人;等人次數被做成等於站數。物質(OC、R/S、Demo、Evidence)該留,例行停不該留。若有人把「殺掉例行停」做成刪檔/刪 token,in-flight 舊 7 與未 upgrade 的採用樹會一起炸。
現在怎麼繞:session 卡住等人按「提交判定」;形狀綠就口頭放行;Owner 自審當日常;採用端釘舊 plugin 或乾脆不 upgrade。

## Context(已知事實)
- F0 brief 是設計正本不是契約;本輪零 bump、不准改 `_templates/`／README §7 錨／`graph.yaml`／既有牙、不准刪 G1／G2／`ACCEPTED`:notes/design/five-station-simplify-brief-v3.md:L1-L9
- 摺的是預設人類停點不是完整度;第一性是人握方向與出貨,不是每一張中間卡:notes/design/five-station-simplify-brief-v3.md:L13-L28
- Owner 十條已鎖:五站、殺例行 G1／S3-`ACCEPTED`／G2、Ship 唯人、條件頁 A/B、UI twin 只 UI/flow、Must-keep、dual-read 2.1.0、F0→F3、in-flight freeze、禁刪禁改正本:notes/design/five-station-simplify-brief-v3.md:L30-L45
- 五站是預設路線別名;舊七份檔名不動;`1-discussion.md`…`7-review.md` 仍是產物:notes/design/five-station-simplify-brief-v3.md:L47-L70
- 表 A1–A10 與表 B 各有生成謂詞與人類 latch;A4/A7 twin 續產但例行不等;B1 Demo 命中才 latch;沒命中 latch 卻問人 = 違 brief:notes/design/five-station-simplify-brief-v3.md:L83-L117
- Must-keep M1–M16(ID 鏈、圍欄、反模糊、Real-world、Human 主權、G3 八點、Profile、DBC、scope、五律、T seam、四眼、html、Quiz、token 留、graph 暫不改)少一條 = 違 brief:notes/design/five-station-simplify-brief-v3.md:L135-L158
- 遷移:契約 dual-read minor 2.1.0;`2.0.0` 續讀舊 7;in-flight 整段舊 7;採用專案 upgrade 到 2.1.0 才看五站;不得遠端改別人 repo 路線;F0–F3 切法與「刪 token = 新 brief」:notes/design/five-station-simplify-brief-v3.md:L160-L182
- Ship `verdict:` 只准人寫;`ACCEPTED` 要人類 attestation;A1–A9 例行不要求人類 verdict;Agent 書面審不構成停點:notes/design/five-station-simplify-brief-v3.md:L184-L198
- 狀態機:Idle→Intake→Decide→Spec→Build→Ship→Done;in-flight 不建本機;Ship 無自動前進;機械綠仍必須 HumanWait:notes/design/five-station-simplify-f0-state-machine.md:L19-L50 notes/design/five-station-simplify-f0-state-machine.md:L60-L120
- Rewrite cap:hop≤2、Decide≤1、Goal reopen≤1;用盡 Escalated,不得暗改:notes/design/five-station-simplify-f0-state-machine.md:L122-L155
- Latch 出口與禁則 X1–X8(含自動前進 Ship、刪 token、改 graph 當 F0、in-flight 套新機、latch 未命中卻問人):notes/design/five-station-simplify-f0-state-machine.md:L157-L208
- STATUS 只在整合分支維護;feature branch 不碰本檔;Backlog A 列已指向 F0 兩檔,下一刀 F1;另有「在觀測實驗前不動 Stage 1–4 模板」的 B 列:docs/dev/STATUS.md:L10-L12 docs/dev/STATUS.md:L44-L50
- 現行七份文檔與 gate:1 無人停、2=**G1**、3 選配回寫、4=**G2**、5 欄位、6 T review、7=**G3**:docs/dev/readme-contract-extract.md:L7-L17
- 四眼:`author ≠ approver`;審者順序人類→fresh Agent→owner 自審;G1=方向+**Owner Calls 全裁決**;G2=**R/S 全審 + Drafting Decisions 全裁決**+**Verification Profile**+**Demo verdict**;G3=綠+回歸+現象+**Evidence 契約全過**:docs/dev/readme-contract-extract.md:L68-L115
- G1/G2/G3 twin 頂區五格由 `check-gate-twin.sh` 釘死:docs/dev/readme-contract-extract.md:L50-L59
- T seam 與驗證五律(證據=原始輸出、派工者不下場、反預判、HITL 不代答、失敗先分類):docs/dev/readme-contract-extract.md:L26-L48
- 2-decision 頂欄 `verdict:`;用途句寫「**G1 gate:人工核准後才寫規格**」;送審步要人寫 verdict+三連動: _templates/2-decision.md:L1-L15 _templates/2-decision.md:L68-L72
- Stage 3 九條 trigger;命中才必要;ACCEPTED 要人類 attestation,Agent 禁寫;零命中不建 html: _templates/3-prototype.md:L15-L26 _templates/3-prototype.md:L48-L61 _templates/3-prototype.md:L108-L129
- 4-spec 頂欄 `verdict:`;G2 twin 必產: _templates/4-spec.md:L1-L19
- 7-review 頂欄 `verdict:`;G3 出貨;全勾不算 PASS: _templates/7-review.md:L1-L35
- Stage 2 圖在 N7-g1 產 twin、等人寫 `verdict:`;尚無寫入才准問人:skills/dev-flow/stage2/nodes/N7-g1.md:L22-L35
- Stage 4 圖在 N6-g2 產 twin;未裁決 DD／缺 Profile／Demo 不合不得過:skills/dev-flow/stage4/nodes/N6-g2.md:L20-L32
- hop 正本仍把 G1/G2 當站尾節點:skills/dev-flow/stage2/graph.yaml:L53-L64 skills/dev-flow/stage4/graph.yaml:L93-L104
- `_stage3_impl.py` 命中≥1 且 ACCEPTED 無 attestation → REJECT:hooks/_stage3_impl.py:L8-L19 hooks/_stage3_impl.py:L263-L275
- `gate-consistency.sh` 從契約檔 §7 抽 G1/G2/G3 token 比對三處摘要;anchor 不見 → exit 2:hooks/gate-consistency.sh:L1-L8
- `check-spec-gate.sh` 是 G2 **形狀**過濾器不是語意審查;缺欄曾讓採用現場走到 Stage 6 才爆:scripts/check-spec-gate.sh:L1-L39
- 契約正本仍 `2.0.0`;runtime 只聲明支持 `2.0.0`;plugin `3.24.0`:devflow-contract.json:L1-L3 hooks/runtime-capabilities.json:L1-L4 .cursor-plugin/plugin.json:L1-L3
- doctor:專案契約版本必須 ∈ plugin `supported_contract_versions`,否則 fail-closed、不靜默退回舊行為:hooks/_doctor_impl.py:L193-L202
- 節點 MD／graph **不複製**進採用專案,正本在方法包;skills+hooks 隨 plugin 全域生效;更新=`marketplace update`+`plugin update`;marketplace 單一 entry `./`:skills/dev-setup/SKILL.md:L14-L16 skills/dev-setup/SKILL.md:L62-L68 .cursor-plugin/marketplace.json:L10-L16
- 本改版是新能力／不可逆流程契約 → full lane 1–7(3 選配);階段表仍把 G1/G2/G3 寫成人類 gate:skills/dev-flow/SKILL.md:L34-L36 skills/dev-flow/SKILL.md:L39-L49
- 採用現場至少四棵產品樹曾從舊模板遷到母版,問題是母版的不是專案的:notes/adoption-findings-2026-08-04.md:L1-L5
- Human 判定正本是同目錄 md 頂欄 `verdict:`;勾選≠PASS;HTML／localStorage／sidecar 不是正本:notes/design/gate-verdict-write.md:L7-L16
- Stage 1 模板:發散、不做決定;固定產 md+掃頁 html: _templates/1-discussion.md:L10-L14

## Real-world Context

沒有五站時,人「真的」完成一件 full-lane 母版改版的方式 = 七站 + 三次例行人停 + 一次出貨人停。正式 SOP 與實際繞法都記。

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 實作者 | 做出貨,少卡在中間 | 寫 1–6 | 模板、graph、牙 | 人何時才真要看 | GitHub PR |
| G1審者 | 方向對再放行 | 寫 G1 `verdict:` | 2-decision twin | 物質已齊卻仍被叫 | 瀏覽器勾選 |
| Demo人 | 互動做對再定案 | 寫 ACCEPTED+attestation | Demo | 非 UI 為何也被叫 | 口頭、會議 |
| G2審者 | 契約對再放行 | 寫 G2 `verdict:` | 4-spec twin | 形狀已綠還要人停嗎 | check-spec-gate |
| 出貨審 | 做出來的對才 PASS | 寫 Ship `verdict:` | 7-review | Agent 會否代填 PASS | Gauntlet |
| 採用者 | 舊七站 feature 不被遠端改線 | 本機 plugin／upgrade | 契約 2.0.0 | 母版何時切五站 | marketplace |
| owner | 少例行等人、完整度不掉 | 裁 OC／Ship | F0 brief | [Assumption] 採用 in-flight 數量 | GitHub |

### Current Journey
正式 SOP:full 走 1→2(G1 等人)→(3 命中則 ACCEPTED 等人)→4(G2 等人)→5→6→7(G3 等人)。實際做法(無本包、最近一次母版改版)如下。兩者都留。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 實作者 | 寫決策等G1 | 2-decision | G1審者 | G1 twin | 例行等人 |
| 2 | 實作者 | Demo等判定 | 3-prototype | Demo人 | attestation | 例行等人 |
| 3 | 實作者 | 寫契約等G2 | 4-spec | G2審者 | G2 twin | 例行等人 |

出貨審在 Step 3 之後才上場;那一停是要留的,不畫進現況圖(現況圖是中間卡痛,不是明天五站流)。

### Workarounds
- session 停在 N7-g1／N6-g2,等人按「提交判定」;勾選留在 localStorage,沒提交就不算。
- 形狀綠(`check-spec-gate.sh` exit 0)就口頭說過;這句常常**不留紀錄**。
- Owner 自審(契約裡的最後手段)被拿來當日常四眼。
- 用 fresh-context Agent 書面審冒充 G1/G2 人類停。
- 採用端釘舊 plugin 版本,或只 update plugin 不跑 `dev-setup upgrade`。
- Owner Call 寫「Stage 3」「跳過」來躲 Demo。
- 沒留下「這次 G1/G2 人到底看了物質還是只看綠勾」的紀錄。

### Exceptions
- Fast lane 合法省略 Stage 1–3;無 1/3 檔 → `_stage3_impl.py` 判 legacy/N-A。
- 命中 trigger 仍跳過 Stage 3 → 必須人類 Owner Call,Agent 不得代決。
- `test-only human fixture` 的 ACCEPTED 永遠不能當正式判定。
- **錯刪中間 gate 會傷害誰**(本討論主軸;正式 SOP 沒寫「可以刪」,實際若有人把 OC-2 做成刪檔):
  1. **本 repo in-flight slug**:N7-g1／N6-g2／`_stage3_impl.py` 仍等人寫 `verdict:`／attestation;token 沒了就走不完舊 7。本檔一旦落地,本 slug 自己也算已開工,F3 cut 時必須 freeze 舊 7。
  2. **採用產品 repo 的 in-flight**:graph/hooks 住方法包,不在他們樹上;`marketplace update` 就能換 hops。他們的 `docs/dev/<slug>/2-decision.md` 仍預期 G1 等人。點名過的樹:report-system、python_scheduling_system、icryobank-crm-api-golang、python-prism(另有後續 ivf_platform／order-intake)。
  3. **Demo 參與者與 UI/flow 使用者**:attestation 牙沒了,Agent 可順手填 ACCEPTED,互動未驗就進 Spec。
  4. **G1/G2 審者**:若連 Decision／OC／R/S／twin 五格一起刪,他們失去唯一審查介面;物質與停點被捆掉。
  5. **doctor／gate-consistency／selftest**:§7 錨消失 → exit 2;更糟是摘要先改、正本錨被拿掉,檢查失明、假綠。
  6. **未 upgrade 的 2.0.0 採用樹**:doctor 仍可能 COMPATIBLE(runtime 只認 2.0.0),但 hops 已被 plugin 換走 = 遠端改線。
- 中途把 in-flight 折成五站:同一 slug 一邊 N7-g1 等人、一邊 coordinator 不等人 → 停點分裂。
- `[Assumption]` 採用現場此刻仍有至少一棵 in-flight 舊 7:無各產品 repo 即時盤點;風險=高(若為假,freeze 仍要留,只是 F3 當下集合可能為空);期限=F1 annex 問 maintainer,過期擋 G2。
- `[Assumption]` 母版例行文檔案的 G1/G2 人審深度接近橡皮圖章:無抽樣 log;風險=高(若為假,殺掉例行停會讓唯一一次真看方向/契約消失,完整度掉在人眼不在牙);期限=Stage 2 抽最近 G1/G2 PR,過期擋 G2。

### Evidence
- Owner 已核准 F0 brief + 狀態機(本 tree 2026-09-13 讀過,行段支持斷言):notes/design/five-station-simplify-brief-v3.md:L30-L45 notes/design/five-station-simplify-f0-state-machine.md:L19-L50
- STATUS Backlog A 列與「feature branch 不改 STATUS」:docs/dev/STATUS.md:L10-L12 docs/dev/STATUS.md:L44-L50
- 七站 gate／四眼／形狀牙／attestation 機械:docs/dev/readme-contract-extract.md:L68-L115 _templates/2-decision.md:L1-L15 _templates/3-prototype.md:L108-L129 hooks/_stage3_impl.py:L8-L19 scripts/check-spec-gate.sh:L1-L39 hooks/gate-consistency.sh:L1-L8
- 採用爆炸面:skills/dev-setup/SKILL.md:L14-L16 skills/dev-setup/SKILL.md:L62-L68 hooks/_doctor_impl.py:L193-L202 notes/adoption-findings-2026-08-04.md:L1-L5
- 本 session brief:Stage 1 only、full、Implementer B、禁 STATUS、禁 F1 碼、禁模板改名、禁刪 gate(使用者書面;本 hop 契約)。
- `[Assumption]` 兩條見 Exceptions;期限如上,過期擋 G2。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 採用現場已無 in-flight 舊 7 → freeze 集合為空,但不准因此刪舊 7 機械 | 高 | 問 Adoption 點名樹的 maintainer:F3 cut 當下 `docs/dev/<slug>/` 是否仍有未 Ship 檔 | F1 annex／owner;過期擋 G2 |
| G1/G2 例行並非橡皮圖章 → 殺例行停會少掉一次真看方向/契約 | 高 | 抽最近 5 次母版 G1/G2:人是否改過物質、是否只按 PASS | Stage 2／owner;過期擋 G2 |
| 採用端總是 upgrade 契約才 update plugin → 遠端改線風險下降(仍要 dual-read) | 高 | 對帳 plugin cache 版號 vs 專案 `devflow-contract.json` | F1 dual-read annex;過期擋 G2 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定意圖 | 本討論原料 | notes/design/five-station-simplify-brief-v3.md | 是 | 是 |
| F0 狀態機 | 謂詞／cap／latch | notes/design/five-station-simplify-f0-state-machine.md | 是 | 是 |
| 看板 | Backlog 與禁改規則 | docs/dev/STATUS.md | 是 | 是 |
| 七站正本與牙 | 遷移起點 | `_templates/*`、stage2/stage4 graph、`hooks/_stage3_impl.py`、`scripts/check-spec-gate.sh`、`hooks/gate-consistency.sh` | 是 | 是 |
| 採用現場 | 爆炸半徑 | notes/adoption-findings-2026-08-04.md、skills/dev-setup/SKILL.md、hooks/_doctor_impl.py | 是 | 是 |

## Goals
- G-out-1:人只在「這次真的需要人裁決」時被叫來停;例行中間卡不等人。
- G-out-2:停點摺掉之後,現行完整度(ID 鏈、圍欄、反模糊、Real-world、人主權、G3 八點、Profile、DBC、scope、五律、T seam、四眼、html、Quiz、舊 token、舊 graph 服務)一項都不因「站變少了」消失。
- G-out-3:已經開工的 slug 繼續走完舊七站,不會在半路被改路線。
- G-out-4:仍握契約 2.0.0、尚未明示 upgrade 的採用專案,不會因為母版切路線而一次變紅,也不會在他們沒 upgrade 時被換成新路線。
- G-out-5:有人把中間 gate 的檔或 token 刪掉當「簡化成功」時,出貨前看得到失敗,不能綠著上船。
- G-out-6:這次改動真的碰到人點的流程時,人仍親口判定互動;沒碰到則不叫人、不強迫多一張互動頁。
- G-out-7:出貨判定仍是人寫下的;機器全綠不能自己變成「過了」。

## Requested solution
候選、未定案(Owner 已鎖當意圖,本 hop 不把它寫成 Goal):
- 預設路線五站別名 Intake → Decide → Spec → Build → Ship;舊七檔名不動。
- 例行 G1／S3-`ACCEPTED`／G2 不再是人類必停;機制、檔、token、牙全留。
- 預設人類必停只有 Ship;coordinator 不得代寫 `verdict:`。
- 頁走表 A/B 謂詞;生成假 → 不產頁;latch 假 → 不准問人。
- UI twin 只在 UI/flow;純後端／無互動不產、不 latch Demo。
- Must-keep 16 項;契約 minor 2.1.0 dual-read 舊 7 與新 5。
- 交付序 F1 teeth+annex → F2 coordinator → F3 cut;F0 已落地。
- 本 hop 不選定牙長在哪支腳本、coordinator 事件 schema、或模板何時改寫。

## Non-Goals(初稿)
- 本 hop 不寫 F1 碼、不加牙、不 bump plugin／契約、不改 `_templates/`、不改 `graph.yaml`、不刪 G1/G2/`ACCEPTED`、不改名七份文檔。
- 本 hop 不改 STATUS／HISTORY(整合分支才寫表列)。
- 不做四站或六站;不把 Build 再拆成人停。
- 不把 in-flight slug(含本 slug 一旦落檔)中途折成五站。
- 不遠端改採用產品 repo 的路線;不在 2.0.0 讀者上一次變紅。
- 不讓 coordinator 或 Agent 代寫 Ship `PASS`／Demo `ACCEPTED`／attestation。
- 不把 fresh-context Agent 書面審當成 G1/G2 人類停。
- 不在本 hop 做模板全文改寫(brief:那是另開刀,不叫 F3)。
- 不重開 STATUS 那條「先跑完整 dogfood 再動 Stage 1–4 模板」的觀測凍結;本 hop 只寫討論。

## Open Questions
- [x] Q1:lane 是否 full?→ owner:full(不可逆流程契約)
- [x] Q2:本 hop 是否只 Stage 1、不送 G1?→ owner:是
- [x] Q3:預設路線是否五站、不是四/六?→ owner:OC-1
- [x] Q4:是否只殺例行停、留 G1/G2/`ACCEPTED` 機制與檔?→ owner:OC-2／OC-10
- [x] Q5:預設人類必停是否只有 Ship?→ owner:OC-3
- [x] Q6:頁是否走表 A/B 謂詞?→ owner:OC-4
- [x] Q7:UI twin 是否只在 UI/flow?→ owner:OC-5
- [x] Q8:Must-keep 是否一項都不能少?→ owner:OC-6
- [x] Q9:是否 dual-read 2.1.0、2.0.0 續讀舊 7?→ owner:OC-7
- [x] Q10:交付是否 F1→F2→F3、本 hop 不寫 F1?→ owner:OC-8
- [x] Q11:已開工是否 freeze 舊 7 到 Ship?→ owner:OC-9
- [x] Q12:本 hop 是否禁改 STATUS?→ owner:是;本檔已照做
- [~] Q13:採用現場 F3 cut 當下是否仍有 in-flight 舊 7?(帶假設:至少一棵;風險=高;F1 annex 問 maintainer,過期擋 G2)
- [~] Q14:例行 G1/G2 是否接近橡皮圖章?(帶假設:母版例行文檔案是;風險=高;Stage 2 抽樣,過期擋 G2)
- [>] Q15:F1 牙落哪幾支腳本／fixture?→ 移交 Stage 2
- [>] Q16:契約 2.1.0 bump 落 F1 還是更後?→ 移交 F1 annex

## Constraints
- 本 PR 不宣稱 G1 PASS;status 留 draft;不改 STATUS／HISTORY。
- 本票過程仍走現行七站(含後續若送的例行 G1/G2);不偷跑五站 coordinator。
- 表列只准整合分支上的 `scripts/status-update.sh`。
- 高影響 `[Assumption]`／`[~]` 必寫風險+期限;到期未驗擋 G2。
- 詞條(語言,不是方案):例行停點 = 不問謂詞、站到了就叫人的停。物質 = OC／R/S／Demo／Evidence 那些不因摺站而消失的東西。latch = 謂詞為真才准問人的那一下。dual-read = 同一契約同時讀舊 7 與新 5,舊檔不紅。in-flight = F3 cut 當下該 slug 已有任一站檔。Must-keep = 完整度清單,不是站名。本 hop 不寫進長期記憶。

## 驗收雛形
- AC-1(G-out-1):假設一份新 slug 在 F3 之後走預設路線,當中間站物質已齊且沒有 latch,則沒有人被叫來按中間判定。
  - 從哪看:該 slug 有沒有中間站「等人寫 `verdict:`」的停點紀錄
  - 看到什麼算對:Decide／Spec 例行無人停;有停只出現在 latch 命中或 Ship
  - 拿什麼試:純文件／守衛案(無九條 trigger);對照現況 N7-g1／N6-g2 必問人
- AC-2(G-out-2):假設停點已摺,當有人用「已經比較少站」當理由省略完整度,則那項省略不成立。
  - 從哪看:Must-keep 對照(ID 鏈、圍欄、人主權、G3 八點等)是否仍可指出正本
  - 看到什麼算對:16 項都還找得到現行正本;不是「五站所以免」
  - 拿什麼試:本檔 Context 已列的契約檔 §7、五律、`_stage3_impl.py` attestation
- AC-3(G-out-3):假設某 slug 在 F3 cut 當下已有任一站檔,當路線切換發生,則該 slug 仍走舊七站到 Ship。
  - 從哪看:該 slug 目錄與它被要求的 hop
  - 看到什麼算對:仍出現 G1／條件 S3／G2／G3 舊停點;沒有被寫入五站狀態
  - 拿什麼試:本 slug(本檔落地後即 in-flight);再加一份只有 `1-discussion.md` 的對照
- AC-4(G-out-4):假設採用專案契約仍是 2.0.0 且未 upgrade,當母版已切五站別名,則他們的舊 slug 不紅、路線也不被換走。
  - 從哪看:doctor 握手結果,以及他們 session 實際走的 hop
  - 看到什麼算對:2.0.0 ∈ supported;未 upgrade 仍走舊 7;不是 marketplace 一更新 hops 就變
  - 拿什麼試:Adoption 點名的產品樹契約檔 + 本 repo `hooks/runtime-capabilities.json`
- AC-5(G-out-5):假設有人刪了 G1／G2／`ACCEPTED` 檔或契約 token 並宣稱簡化完成,當要出貨,則過不了。
  - 從哪看:出貨前看得到的拒絕(檢查輸出或審查紀錄),不是事後口頭
  - 看到什麼算對:明確因缺 token／缺檔被拒;不是綠著合併
  - 拿什麼試:對 `gate-consistency.sh`／`_stage3_impl.py` 抽掉 `ACCEPTED` 錨的對照稿(後續造,本 hop 不造)
- AC-6(G-out-6):假設九條 trigger 命中(或本次改了人點的流程),當要離開互動未定案的那一站,則必須有人親填判定+attestation;沒命中則沒有 Demo 人停、也沒有強迫互動頁。
  - 從哪看:3-prototype 有無 Human verdict 行;有無被叫來的 Demo 人
  - 看到什麼算對:命中 → `ACCEPTED`+`human:<名> @ <日>`;未命中 → 不產 Demo、不 latch
  - 拿什麼試:改審頁動線的對照(命中「改變下一步」);純腳本／牙 feat(不命中)
- AC-7(G-out-7):假設 Ship 材料機械全綠,當還沒有人寫頂欄判定,則狀態不是出貨完成。
  - 從哪看:7-review 頂欄 `verdict:` 與是否被標完成
  - 看到什麼算對:無人 `PASS` → 停在出貨;機器不得寫入 `PASS`
  - 拿什麼試:本母版既有 G3 頂欄規則;對照「機械綠就標 Done」的負向稿

## 現況圖
誰:實作者
做什麼:寫決策等G1
工具:2-decision
痛點:例行等人
↓
誰:實作者
做什麼:Demo等判定
工具:3-prototype
痛點:例行等人
↓
誰:實作者
做什麼:寫契約等G2
工具:4-spec
痛點:例行等人

## 邏輯圖(ASCII)
```
now waits
|-- G1 human        [routine]
|-- S3 ACCEPTED     [if trigger]
|-- G2 human        [routine]
+-- G3/Ship         [keep]

material stays
|-- Decision + OC
|-- 9 triggers + Demo + attest
|-- R/S + DD + Profile
+-- G3 eight + verdict

hurt-if-delete
|-- in-flight old-7
|-- adopted plugin hops
|-- Demo tripwire
+-- dual-read 2.0.0

adopted blast
|-- graphs live in plugin
|-- marketplace update
|-- contract still 2.0.0
+-- doctor may stay green
```

## Interview Log(推理鏈外顯)
- Q:為什麼 Goals 不能寫「做成五站」?
  - 事實:_templates/1-discussion.md:L10-L14 notes/design/five-station-simplify-brief-v3.md:L13-L28 notes/design/five-station-simplify-brief-v3.md:L30-L45
  - 推理:Stage 1 不做決定。五站、殺例行停、條件頁是 Owner 帶來的解法。人要的結果是少被無謂叫來、完整度還在、舊 slug 與採用樹不被誤傷。把站名寫進 Goal,Stage 2 只剩「五站怎麼改檔名」。
  - 結論:CONFIRMED Goals 只寫停點與完整度與傷害面;五站進 Requested solution。
- ⚠️ Q:錯刪 G1／G2／ACCEPTED 檔或 token,誰會受傷?
  - 事實:docs/dev/readme-contract-extract.md:L68-L115 hooks/gate-consistency.sh:L1-L8 hooks/_stage3_impl.py:L8-L19 skills/dev-flow/stage2/nodes/N7-g1.md:L22-L35 skills/dev-flow/stage4/nodes/N6-g2.md:L20-L32 notes/design/five-station-simplify-brief-v3.md:L30-L45
  - 推理:現行停點編在 hop 尾與機械牙,不是散文。刪 token 會讓 in-flight 走不完舊 7、Demo 失去 attestation 拒收、§7 三處對帳失明或全紅。OC-2 寫的是殺例行停,不是刪機制。捆掉物質等於審者沒介面。
  - 結論:CONFIRMED 受傷的是 in-flight 實作者、採用端未完成 slug、Demo 人、中間審者、以及依賴錨的檢查;刪檔不是簡化。
- ⚠️ Q:採用產品 repo 的爆炸半徑在哪?為什麼不是「他們自己 upgrade 才會碰到」?
  - 事實:skills/dev-setup/SKILL.md:L14-L16 skills/dev-setup/SKILL.md:L62-L68 .cursor-plugin/marketplace.json:L10-L16 hooks/_doctor_impl.py:L193-L202 hooks/runtime-capabilities.json:L1-L4 notes/adoption-findings-2026-08-04.md:L1-L5 notes/design/five-station-simplify-brief-v3.md:L160-L182
  - 推理:graph 與 hooks 住方法包,不進採用樹。marketplace 單一 entry,update plugin = 換 hops。契約仍只握手 2.0.0,doctor 可以繼續綠,路線卻已被遠端改。Adoption 已證母版問題會在至少四棵產品樹顯現。brief 才寫「不得遠端改別人路線」。
  - 結論:CONFIRMED 爆炸先發生在 plugin hops,不是他們樹上的模板副本;dual-read 與「未 upgrade = 舊 7」是同一道牆。
- Q:為什麼 S3-ACCEPTED 要留物質、只摺例行停?
  - 事實:_templates/3-prototype.md:L15-L26 _templates/3-prototype.md:L48-L61 _templates/3-prototype.md:L108-L129 hooks/_stage3_impl.py:L8-L19 hooks/_stage3_impl.py:L263-L275 notes/design/five-station-simplify-brief-v3.md:L83-L117
  - 推理:九條 trigger 與 attestation 是互動風險的牙,不是站名。無 trigger 本就 N/A。有 trigger 卻因「五站了」免人填,等於 Agent 可定互動。表 B 把這次人停收成一次 latch,不另開第三次例行停。
  - 結論:CONFIRMED 留 trigger／Demo／attestation;latch 只在命中時開火。
- Q:為什麼本票落地後必須還走舊七站,不能自己先切五站?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L30-L45 notes/design/five-station-simplify-brief-v3.md:L160-L182 notes/design/five-station-simplify-f0-state-machine.md:L19-L50 docs/dev/STATUS.md:L44-L50
  - 推理:OC-9 = 已有站檔就 freeze。本檔落地 = 本 slug 已開工。F0–F2 母版新軌也明文走舊 7,避免雙路線污染觀測。狀態機對 in-flight 不建新機。
  - 結論:CONFIRMED 本 slug 與其他已開工軌 F3 前整段舊 7。
- Q:為什麼要先 dual-read 2.1.0,不能在 2.0.0 上直接改預設路線?
  - 事實:devflow-contract.json:L1-L3 hooks/runtime-capabilities.json:L1-L4 hooks/_doctor_impl.py:L193-L202 notes/design/five-station-simplify-brief-v3.md:L160-L182
  - 推理:現在握手是單點集合 `{2.0.0}`。只改 hops 不 bump,doctor 仍綠,行為已變。只 bump 不 dual-read,所有 2.0.0 採用樹一次 INCOMPATIBLE。2.1.0 必須同時讀兩套,舊 slug 不紅。
  - 結論:CONFIRMED 2.1.0 的意義是雙讀,不是換招牌;F0 不 bump。
- ⚠️ Q:若改成四站、或讓機械綠自動寫 Ship PASS、或刪 token 好寫謂詞,會怎樣?(發散)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L30-L45 notes/design/five-station-simplify-f0-state-machine.md:L60-L120 notes/design/five-station-simplify-f0-state-machine.md:L157-L208 notes/design/gate-verdict-write.md:L7-L16
  - 推理:四站 = 新 brief。自動 PASS = 違反 OC-3 與 X1,出貨主權沒了。刪 token = X2,謂詞好寫但 dual-read 與 in-flight 死。最極端:marketplace 一更,採用端全改線、Ship 變機器章。
  - 結論:OPEN 發散只記傷害,不收斂成方案;本 hop 不採四站／自動 PASS／刪 token。
- ⚠️ Q:有哪些沒問出口的預設可能翻案?(盲點)
  - 事實:scripts/check-spec-gate.sh:L1-L39 skills/dev-flow/stage2/nodes/N7-g1.md:L22-L35 docs/dev/STATUS.md:L44-L50 notes/design/five-station-simplify-brief-v3.md:L171-L182
  - 推理:形狀牙不看人有沒有真審,所以「殺例行停很安全」依賴橡皮圖章假設。Coordinator 是 F2 才有的角色,F1 之前沒有自動 hop。STATUS B 列還凍著 Stage 1–4 模板,與日後模板改寫刀衝突,brief 已把改寫排除在 F3 外。隱含預設「採用者會先 upgrade 再 update plugin」沒有現場 log。
  - 結論:NEEDS_VERIFICATION 橡皮圖章與 upgrade 順序兩條假設;Coordinator 不存在與模板凍結則已鎖,不在本 hop 翻。
