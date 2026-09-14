---
feature: five-station-f2
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 1. 討論 — 五站 F2（Implementer B：計數落點／doctor 誠實／採用升級陷阱）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／狀態機／F1 annex,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1 討論**；不送 G1、不改 STATUS、不合併。
> 原料:brief-v3、F0 狀態機、F1 annex、F1 RP 最小集、`_templates/1-discussion.md`。
> B 線只挖三件事:①hop≤2／Decide≤1／Goal≤1 的**計數落點**；②marketplace × doctor 誠實 × coordinator；③採用端升級陷阱。
> F2 刀(brief §7):Coordinator + hop／latch／cap 事件；舊 token 全留；**不做 F3 cut**；**不刪** G1／G2／`ACCEPTED`。本 slug 與 F0–F2 母版改版軌仍走**舊 7**。

## Problem
痛:F1 已鎖 cap 數字與拒收謂詞,但「計數落在哪、鍵叫什麼」明文交給 F2。現行牙只對 fixture 字樣「第 3 次」正則紅——沒有倉,第三次重寫在 live 裡可以假裝第一次。採用端 `marketplace update` 換 hops,doctor 仍印 `COMPATIBLE`;若 F2 coordinator 把「綠」或「我已在 plugin cache」當成切五站,舊 7 slug 會被折。若三個 cap 寫進 run 級 `events.jsonl`,新 run 歸零 = 暗改 cap(X5)。
現在怎麼繞:F1 牙對文案「doctor 綠所以跟 hops」紅;沒有 live coordinator;沒有 slug 級計數倉;本資料夾本 hop 才開。

## Context(已知事實)
- F2 刀=Coordinator／runtime 接自動前進;event 留前進／latch／cap;仍不刪舊 token。不做:把 in-flight 折成五站;拿掉 G1／G2／`ACCEPTED` 檔:notes/design/five-station-simplify-brief-v3.md:L176-L180
- F0–F2 期間新開的母版改版軌仍走舊 7;F3 cut 之後才預設五站:notes/design/five-station-simplify-brief-v3.md:L166
- 採用專案 `dev-setup` upgrade 到 2.1.0 之後才看五站;未 upgrade = 舊 7;不得遠端改別人 repo 的路線:notes/design/five-station-simplify-brief-v3.md:L168
- in-flight = `docs/dev/<slug>/` 已有 1–7 任一 `.md` → 整段舊 7 到 Ship:notes/design/five-station-simplify-brief-v3.md:L165 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32
- 本機管五站 hop;不管舊 7 in-flight 的 hop(那些仍走既有 `graph.yaml`):notes/design/five-station-simplify-f0-state-machine.md:L10-L15
- in-flight freeze:slug 已有舊 7 檔 → **不建立本機**;coordinator 放手給既有 graph:notes/design/five-station-simplify-f0-state-machine.md:L49-L50
- rewrite cap 數字已鎖:hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改;舊 7 不套:notes/design/five-station-simplify-brief-v3.md:L131 notes/design/five-station-simplify-f0-state-machine.md:L122-L139
- 三個計數器 slug 級、只增不減;hop cap **按 hop 分桶**;Decide 與 hop **同時算**;Goal reopen 可連帶用盡 Decide cap;計數看寫入發生、不看模型名:notes/design/five-station-simplify-f0-state-machine.md:L124-L138
- 偽碼:`slug.hop_rewrites[hop_id]`／`goal_reopen`／`decide_reopen`;舊 7 走 `allow_legacy()`:notes/design/five-station-simplify-f0-state-machine.md:L143-L155
- T 重做吃該 T 嘗試上限 4,**不**另吃 hop cap,除非整份 5-tasks／6-notes 被整站重寫:notes/design/five-station-simplify-f0-state-machine.md:L107-L108
- 前進／latch／cap 觸發都要留機械紀錄(F2 才接 event schema;F0 只鎖「要留」):notes/design/five-station-simplify-brief-v3.md:L133
- F1 annex:計數落點(event 鍵名)不在 F1 鎖定:notes/design/five-station-simplify-f1-dual-read-annex.md:L36
- F1 RP 最小集:語意清單,不是 event schema;超 cap 三列的計數落點交 F2:notes/design/five-station-simplify-f1-rp-min-set.md:L4
- RP-9／RP-10／RP-11 紅第三次 hop 重寫／第二次 Decide 重開／第二次 Goal 重開;舊 7 不套:notes/design/five-station-simplify-f1-rp-min-set.md:L16-L18
- 現行 F1 牙對 cap 的實作是讀 fixture 正文正則(「第 3 次」「Decide 重開第 2」),不是讀計數倉:scripts/five_station_f1.py:L327-L333
- X5:cap 用盡後 reset 計數再 hop = 暗改 cap:notes/design/five-station-simplify-f0-state-machine.md:L198
- SLOT-UNDECLARED-ROUTE:未宣告 2.1.0 dual-read 時,採用端路線 = 舊 7;marketplace 包裝不能單獨改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L20
- SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS:契約仍 2.0.0 且 hops 已是五站預設 → 紅、不得改線:notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24
- SLOT-DOCTOR-GREEN-MEANS:`devflow-doctor.sh` 綠／`COMPATIBLE`／exit 0 只證明握手(`2.0.0 ∈ supported`)。≠ 路線沒變,≠ 已切五站。文案「doctor exit 0 所以可以跟 hops 走」必須紅:notes/design/five-station-simplify-f1-dual-read-annex.md:L26-L28
- F1 牙對該文案與「COMPATIBLE = 五站」紅:scripts/five_station_f1.py:L60-L62 scripts/five_station_f1.py:L217-L224
- 現行契約仍 `2.0.0`;runtime 只聲明支持 `2.0.0`:devflow-contract.json:L1-L3 hooks/runtime-capabilities.json:L1-L4
- doctor 握手:專案契約版本必須 ∈ plugin `supported_contract_versions`,否則 fail-closed:hooks/_doctor_impl.py:L193-L202
- doctor 另比 vendored schema vs 契約 `schema_versions`;major.minor 不合 → fail-closed:hooks/_doctor_impl.py:L216-L233
- doctor 綠時印 `COMPATIBLE` 並 exit 0:hooks/_doctor_impl.py:L492-L500
- marketplace 單一 entry `./`;更新 = `marketplace update` + `plugin update`;plugin root 在 cache、隨版本變:skills/dev-setup/SKILL.md:L62-L71 .claude-plugin/marketplace.json:L9-L16
- 節點 MD／graph 不複製進採用專案;hops 住方法包:skills/dev-setup/SKILL.md:L16
- 現行 agent-event `stage` 欄正則是 `^[1-7]-[a-z-]+$`;沒有 Intake／Decide 別名:observability/schema/agent-event.schema.json:L18
- 現行已定義事件是 run／stage／attempt／review／gate 生命週期,沒有 hop／latch／cap 事件型別:observability/schema/agent-event.schema.json:L81-L103
- 未定義 `event_type` → `unknown_event_type` 拒:observability/devflow_obs/event_validate.py:L499-L503
- 未列欄且無 `x_` 前綴 → `unknown_field` 拒;`x_` 只受隱私掃描:observability/devflow_obs/event_validate.py:L542-L546
- 現行 ledger 是 run 級:`.devflow/runs/<run_id>/coordinator/events.jsonl`:observability/devflow_obs/ledger.py:L3-L6
- coordinator 事件檔單一寫入者、跨 worktree 分檔(state per-worktree):observability/devflow_obs/writer.py:L5-L6
- F1 母軌 G3 PASS、Active 已移出:docs/dev/HISTORY.md:L659-L663
- 本 tree 搜過:沒有 F2 coordinator 實作檔(只有 obs 的 coordinator 寫者與 ledger 路徑)。
- 受影響面(本 hop 不動):尚未存在的 F2 coordinator、`observability/schema/agent-event.schema.json`、`hooks/_doctor_impl.py`、採用端 plugin cache、各 in-flight slug 的路線、本目錄自己(一落檔即 in-flight)。

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 母版 owner(tony／rick) | F2 接自動前進與事件,但不切 F3、不折舊 7 | 裁 brief、簽 gate | F0／F1 落盤、本 tree | 採用端會不會把 doctor 綠當切線 | GitHub、Cursor chat |
| F2 討論／實作 agent | 把計數落點與升級陷阱問清楚;本 hop 只寫討論 | 寫本目錄討論檔 | brief、annex、schema、doctor | 計數倉選哪一種才不會 X5 | Cloud Agent、PR |
| coordinator(F2 後才有) | 謂詞真 hop;latch 開火停;cap 用盡 Escalated | 讀謂詞、寫事件、**禁**寫判定 | 表 A／B、狀態機 | 計數讀哪;doctor 綠能不能當通行證 | 尚未落地 |
| 採用專案 owner | 更新 plugin 後路線不要被遠端改 | 系統外(自己 repo 的契約檔) | 自己的 `devflow-contract.json`、doctor 輸出 | hops 已換、契約仍 2.0.0 時誰說了算 | marketplace／plugin 指令、口頭 |
| in-flight slug 執行者 | 走完手上舊 7,不被五站狀態寫入 | 既有 graph／模板 | 自己目錄已有 1–7 `.md` | F2 coordinator 會不會誤建五站機 | 既有 hop |
| doctor 操作者 | 看握手綠／紅 | 跑 `devflow-doctor.sh` | `COMPATIBLE`／`INCOMPATIBLE` 一行 | 綠 ≠ 路線;schema 不合也會紅 | 終端機 |

### Current Journey
正式 SOP(F3 後才預設):五站別名 + coordinator 評謂詞 hop。實際做法(**現在、F2 尚未落地**)如下。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 母版 | 把 F1 牙與 annex 合進 plugin(`./` 單一 entry) | marketplace／git | — | RP-9…11 正則牙;SLOT 文案牙 | 超 cap 沒有 live 計數倉 |
| 2 | 採用 owner | `marketplace update` + `plugin update` | plugin cache | — | 新 hops／新牙;契約檔常未動 | hops 已換,契約仍 2.0.0 |
| 3 | 同一人 | 跑 doctor | `devflow-doctor.sh` | — | `COMPATIBLE` + exit 0 | 綠只證明 `2.0.0 ∈ supported` |
| 4 | `[Assumption]` 採用寫手 | 把綠讀成「可以跟新 hops」 | chat／README | — | 可能寫出 F1 已紅的那句 | 文案牙紅、行為還沒人擋 |
| 5 | 舊 7 slug 執行者 | 仍走 graph `N7-g1`／`N6-g2` | 既有 graph | owner 簽閘 | G1／G2 twin | 若 coordinator 提前開火就會被折 |
| 6 | F1 牙 | 對 fixture 寫「第 3 次」的稿紅 | `five_station_f1.py` | — | RED RP-9 | live 第三次重寫沒倉可對 |
| 7 | 本討論 | 把落點與陷阱問成 OQ | 本檔 | 後續 F2 收斂 | 討論檔 | 本 hop 不選定倉 |

### Workarounds
- F1 用文案正則擋「doctor 綠所以跟 hops」;擋的是**寫出來的謊**,不是 coordinator 行為(coordinator 還不存在)。
- cap 牙用 fixture 字樣「第 3 次」充當計數;沒有 slug 級倉。
- 採用端路線實際靠「人記得 brief §6」與「不要遠端改別人 repo」;沒有 coordinator 閘。
- 這些步驟常不留「這次 hop 已重寫幾次」或「doctor 綠之後有沒有人改線」。

### Exceptions
- 舊 7 與 in-flight **不套**三個 cap;它們走既有 T 嘗試上限 4。
- Fast lane 不是本包要廢;本 slug 是 full。
- F2 可以寫 coordinator 碼,但 F3 前預設路線仍舊 7——含本 slug、含其他 F0–F2 母版軌。
- doctor schema 不合會 INCOMPATIBLE(與契約握手綠是兩條)。F2 若 bump `agent_event` 而採用端未同步契約,綠會變紅。
- `[Assumption]` 採用端典型升級=先 marketplace update、後(或不)bump 契約:無採用逐字稿;風險=高。
- `[Assumption]` 把 cap 放進 run 級 events = X5:無未來 log;風險=高。
- `[Assumption]` F2 若不把真計數餵給 RP-9／10／11,牙會繼續只咬 fixture:風險=高。

### Evidence
- F0／F1 書面:brief-v3、狀態機、F1 annex、F1 RP 最小集;Owner 已核准(檔頭)。本 hop 不改那些檔。
- 本 tree 已核:上列 Context 出處(2026-09-14 讀過,行段支持斷言)。
- F1 已出貨:docs/dev/HISTORY.md:L659-L663。
- doctor／marketplace／schema／ledger:上列 hooks／skills／observability 出處。
- `[Assumption]` 三條見 Exceptions;採用升級逐字稿／未來 coordinator log／真計數倉皆無。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「run 級 events 當 cap 倉 = X5」為假 → 計數落點可以住現有 ledger | 高 | 同一 slug 開第二個 `run_id` 後,三個計數是否仍在 | F2 收斂／實作者;過期不得把 run 級倉寫進 Decision 當已核 |
| 「採用端先更新 plugin、契約仍 2.0.0」為假 → marketplace×doctor 陷阱變窄 | 高 | 抽一採用 repo:update 後契約版本與 hops 是否同動 | F2 規格前／owner;過期擋把「現場都會一起 bump」當事實 |
| 「F2 必須餵真計數給 RP-9／10／11」為假 → 牙可繼續咬字樣 | 高 | Stage 2 對帳:Decision 有無把「正則字樣」標成可選 | Stage 2／收斂者;過期擋「牙已夠、不必倉」 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | 調查跟 brief／狀態機 | notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名) | 是 |
| F1 annex／RP | 計數落點移交句、doctor／marketplace SLOT | notes/design/five-station-simplify-f1-dual-read-annex.md、notes/design/five-station-simplify-f1-rp-min-set.md | 是(使用者點名) | 是 |
| Stage 1 模板 | 骨架與審頁 | _templates/1-discussion.md | 是(使用者點名) | 是 |
| F1 牙實作 | 證明 cap 牙現在咬字樣、doctor 牙咬文案 | scripts/five_station_f1.py | 是(本 tree;annex 指向) | 是 |
| doctor／契約 | 綠=握手 | hooks/_doctor_impl.py、devflow-contract.json、hooks/runtime-capabilities.json | 是(本 tree) | 是 |
| marketplace | 單一 entry、update 換 hops | .claude-plugin/marketplace.json、skills/dev-setup/SKILL.md | 是(本 tree) | 是 |
| event／ledger | 無 hop 事件;run 級倉;stage 正則舊 7 | observability/schema/agent-event.schema.json、observability/devflow_obs/event_validate.py、observability/devflow_obs/ledger.py | 是(brief §4 觀測句指向) | 是 |
| F1 出貨 | 下一刀才是 F2 | docs/dev/HISTORY.md | 是(本 tree) | 是 |
| 採用升級逐字稿 | 驗證「先 update 後 bump」 | 無;public repo 禁收公司路徑 | 禁 | 否 |

## Goals
- G-locus-1:離開某一 hop 之後,人能指出**該 hop 桶**已重寫幾次、Decide 重開剩幾次、Goal 重開剩幾次;數字在新 run／重開 process 之後仍在。
- G-locus-2:第三次 hop 重寫、第二次 Decide 重開、第二次 Goal 重開被拒絕時,沒有人改過計數器上的數字。
- G-honest-1:doctor 印 `COMPATIBLE`／exit 0,不足以讓 coordinator 走五站 hop。
- G-honest-2:`marketplace update` 單獨發生,不足以改採用端路線。
- G-trap-1:採用端更新了 plugin、契約仍 2.0.0 時,路線仍是舊 7;2.0.0 + 五站 hops 預設被看成違規。
- G-self-1:本 slug 自己走到 G1／G2／G3 時仍是舊 7;沒有五站狀態寫入。
- G-knife-1:F2 做完之後,G1／G2／`ACCEPTED` token 與檔仍在;沒有 F3 cut;沒有 in-flight 被折。
- G-obs-1:前進／latch 開火／cap 觸發各留一筆人指得到的機械紀錄。
- G-carry-1:本檔列出的計數落點題與升級陷阱,到規格時每條有去向,不能無聲消失。

## Requested solution
- F2 寫 coordinator:讀 brief §3 謂詞,真則 hop,假則停修;latch 開火進 HumanWait;cap 用盡 Escalated。
- 事件留下前進／latch／cap。**計數落點(倉、鍵、hop_id、是否 bump schema)本討論不選定。**
- coordinator 評五站謂詞之前,先問路線:未宣告 2.1.0、或 in-flight、或 F3 前的母版新軌 → 放手舊 7。doctor 綠不是這道問的答案。
- 舊 token／twin／graph 不刪。本 hop 不選定 event 型別名、sidecar 路徑、或 schema 版本號。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`graph.yaml`、gate token、STATUS、HISTORY、契約版本。
- 本 hop 不送 G1;status 留 draft;不合併。
- 不刪 G1／G2／`ACCEPTED`;不做 F3 cut;不把 in-flight 折成五站。
- 不重開 F0 十條;不放寬 hop≤2／Decide≤1／Goal≤1。
- 不把本 slug 當新 5 的第一個白老鼠。
- 不在本討論選定計數倉或 event 鍵名(那是 OQ,不是 Goal)。
- 不把「doctor 綠」寫成路線許可。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:full
- [x] Q2:本 hop 是否只 Stage 1、不改 STATUS、不合併?→ 使用者:是
- [x] Q3:F2 刀是否只做 coordinator + hop／latch／cap 事件、留舊 token、不做 F3、不刪閘?→ brief §7;翻=新 brief
- [x] Q4:本 slug 與 F0–F2 母版新軌是否仍走舊 7?→ brief §6 + OC-9。本目錄一有 1–7 `.md` = in-flight,整段舊 7 到 Ship
- [x] Q5:cap **數字**是否已鎖、F2 不得放寬?→ hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改
- [x] Q6:舊 7／in-flight 是否不套這三 cap?→ 狀態機:走 `allow_legacy()` 與既有 T 上限 4
- [x] Q7:doctor 綠是否等於已切五站或可跟 hops?→ 否。SLOT-DOCTOR-GREEN-MEANS;F1 牙 S-5.6／S-5.5
- [x] Q8:marketplace 包裝能否單獨改線?→ 否。SLOT-UNDECLARED-ROUTE
- [>] Q9:三個計數器的**落點**在哪?slug 級倉／現有 run 級 `coordinator/events.jsonl`／sidecar／重放 git?本討論不選。移交 F2 收斂
- [~] Q10:若落點住 run 級 events,新 `run_id` 計數歸零是否視為 X5?(帶假設:**是**;暫定值=run 級倉不合法;風險=高;期限=F2 Decision,過期不得把 run 級倉當已核)
- [>] Q11:`hop_id` 在 F3 前怎麼認?F2 不改 `graph.yaml`,舊節點是 `N7-g1` 這類;五站 hop 還沒有 graph 節點。移交 F2
- [>] Q12:第一次寫不算、第 3 次重寫拒——落點怎麼分辨「初寫」與「重寫」?計數看寫入、不看模型名。移交 F2
- [>] Q13:事件怎麼接?新 `event_type`(必 bump schema)／既有 `stage_*` 加 `x_`／獨立 slug ledger?現行未定義型別會 `unknown_event_type`。移交 F2
- [>] Q14:現行 `stage` 正則 `^[1-7]-[a-z-]+$` 吃不進 Intake／Decide。塞進 `stage_started` 會格式拒。移交 F2
- [>] Q15:Goal reopen 連帶回到 Decide 時,兩個計數是否必須同一落點一次寫入?分倉可能讓 Goal 重開躲掉 Decide cap。移交 F2
- [>] Q16:T 嘗試 ≤4 與 hop 重寫如何不被同一落點算成一次?整站重寫 5-tasks／6-notes 才吃 hop cap。移交 F2
- [~] Q17:coordinator 開火五站謂詞的前置是否=「契約已宣告 2.1.0」且「非 in-flight」且「預設路線只在 F3 後」?(帶假設:**三條全要**;brief §6 已鎖預設;本討論不發明第四條;期限=F2 Decision)
- [>] Q18:F2 若 bump `agent_event`,採用端只 update plugin、契約仍寫 1.1 → doctor 變 INCOMPATIBLE。這是可接受的誠實紅,還是該避免 bump?與 Q13 綁。移交 F2
- [~] Q19:F2 是否必須讓 RP-9／10／11 讀真計數,而不是繼續咬 fixture 字樣?(帶假設:**必須餵真計數**;否則 live 第三次重寫牙看不見;期限=F2 Decision,過期擋「牙已夠」)
- [>] Q20:Cursor／Claude／Codex 各有一份 plugin cache 時,一主機 hops 新、另一主機仍舊 7——coordinator 認哪一份?移交 F2(採用升級陷阱)

## Constraints
- 本 PR 不宣稱 G1 PASS;不改 STATUS／HISTORY。
- 討論盲下游:本檔不指定腳本／API／元件當目標;落點題只寫成 OQ。
- **Owner-locked cap 數字:**hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改。舊 7 不套。
- **Owner-locked F2 刀:**coordinator + 事件;留 token;不 F3;不刪閘;不折 in-flight。
- **Owner-locked 本 slug 路線:**舊 7 到 Ship。
- **採用 hop 身分:**graph／hooks 住方法包。未宣告 2.1.0 之前,marketplace 可換 hops 而 doctor 仍可因 `2.0.0` 握手綠。綠 ≠ 切線。
- 詞條(語言,不是方案):**計數落點**=三個 cap 存在哪、鍵叫什麼、誰寫誰讀。**hop 桶**=同一 hop 節點的重寫次數,不是全 slug 共用一個 2。**暗改 cap**=用盡後 reset 再 hop(X5)。**doctor 誠實**=綠只證明握手。**升級陷阱**=plugin 與契約不同步、或把綠當切線。**in-flight freeze**=已有 1–7 `.md` 的 slug 走舊 7。本 hop 不寫進長期記憶。

### F2 移交種子(不是施工)
- Q9–Q16 是計數落點家族;Q13 與 Q18 綁(schema bump × doctor)。
- Q17／Q10／Q19 過期 → 擋本 slug G2(不得把假設升格成已核)。
- 本資料夾已有本檔 = 已 in-flight;後站不得對自己開五站機。

## 驗收雛形
- AC-1(G-locus-1):假設某五站 slug 已 hop 出 Intake 且同一 hop 被重寫 1 次,當人另開一個新 run 再問該 hop 的次數,則仍看到 1,不是 0。
  - 從哪看:該 slug 的計數紀錄(人可指的檔或事件;不預填通道)
  - 看到什麼算對:該 hop 桶=1;Decide／Goal 計數未被新 run 清掉
  - 拿什麼試:F2 之後造的假 slug + 第二次 run;本 hop 不跑 coordinator
- AC-2(G-locus-2):假設同一 hop 已重寫 2 次,當第 3 次重寫被要求執行,則被拒且進 Escalated;計數器上的數字沒被人手改小。
  - 從哪看:拒絕理由 + 計數紀錄
  - 看到什麼算對:第 3 次未 hop;數字仍是 2;沒有「reset 再來」
  - 拿什麼試:對照 F1 fixture 字樣稿(現行牙);live 必須對倉,不是對字
- AC-3(G-honest-1):假設採用端 doctor 剛印 `COMPATIBLE` 且契約仍 `2.0.0`,當 coordinator 被求走五站 hop,則拒絕。
  - 從哪看:該次 hop 的拒絕理由
  - 看到什麼算對:理由是路線未宣告／仍舊 7,不是「doctor 已綠」
  - 拿什麼試:本 tree 現況(契約 2.0.0 + doctor 可綠)
- AC-4(G-honest-2／G-trap-1):假設只做了 `marketplace update`、契約未宣告 2.1.0,當有人把 hops 當五站預設,則該組合被看成違規,路線仍舊 7。
  - 從哪看:路線判定 + F1 SLOT-REJECT 同類拒絕
  - 看到什麼算對:未改線;2.0.0+五站 hops 紅
  - 拿什麼試:採用端假樹(後續造);不是本 hop
- AC-5(G-self-1):假設本 slug 被求切五站自動前進,當看本目錄,則仍是舊 7 站檔與例行閘,沒有五站狀態。
  - 從哪看:本目錄 1–7 `.md` 與被拒絕的 hop
  - 看到什麼算對:有 `1-discussion.md`;無五站機寫入
  - 拿什麼試:本資料夾(本 hop 落檔即 in-flight)
- AC-6(G-knife-1):假設 F2 做完,當人找 G1／G2／`ACCEPTED` token 與 in-flight slug,則檔仍在、舊 slug 未被折、沒有 F3 cut。
  - 從哪看:token 檢查、in-flight 目錄、預設路線聲明
  - 看到什麼算對:token 在;in-flight 仍舊 7;新 slug 預設五站尚未發生
  - 拿什麼試:既有 `check-gate-tokens.sh` 與任一已有站檔的 slug
- AC-7(G-obs-1):假設一次 hop 成功、一次 latch 開火、一次 cap 用盡,當人問「有沒有留下」,則三筆都能指出。
  - 從哪看:機械紀錄(落點未定,只問「指得到」)
  - 看到什麼算對:三類各至少一筆;不是只靠 chat
  - 拿什麼試:F2 之後造;本 hop 不選鍵名
- AC-8(G-carry-1):假設本檔 Q9–Q20 列了一題,當人讀到 F2 Decision／Spec,則該題有去向。
  - 從哪看:Stage 2 對帳
  - 看到什麼算對:每條高影響 OQ 有處理／Non-Goal／仍待驗;沒有消失
  - 拿什麼試:Q9 落點、Q10 X5、Q17 三前置、Q19 真計數

## 現況圖
誰:採用 owner
做什麼:marketplace 更新
工具:plugin cache
痛點:doctor 仍綠
↓
誰:F2 coordinator
做什麼:把綠當切線
工具:hops／謂詞
痛點:舊 7 被折
↓
誰:計數器
做什麼:run 級重算
工具:events.jsonl
痛點:cap 暗重置

## 邏輯圖(ASCII)
```
now
|-- F1 teeth
|   |-- RP-9/10/11 regex     [fixture text only]
|   +-- doctor phrase red    [not coordinator]
|-- adopter
|   |-- marketplace update   [hops move]
|   |-- contract still 2.0.0
|   +-- doctor COMPATIBLE    [handshake only]
|-- F2 knife
|   |-- write coordinator
|   |-- emit hop/latch/cap
|   |-- keep tokens
|   +-- no F3 cut
+-- counting locus           [OPEN]
    |-- run events.jsonl     [new run => 0 => X5?]
    |-- slug store           [survives run]
    |-- schema bump          [doctor may go red]
    +-- this slug            [old 7 / in-flight]
```

## Interview Log(推理鏈外顯)
- Q:F2 這一刀到底做什麼、本討論為什麼不准切路線?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L176-L180 notes/design/five-station-simplify-brief-v3.md:L166 notes/design/five-station-simplify-f0-state-machine.md:L49-L50
  - 推理:brief 把 coordinator／事件與 F3 cut 拆成兩刀。F0–F2 母版新軌仍舊 7,避免雙路線污染觀測。本資料夾一有站檔就是 in-flight,機不該建立。
  - 結論:CONFIRMED F2 = coordinator + hop／latch／cap 事件;留 token;不 F3;本 slug 舊 7。
- ⚠️ Q:cap 數字已鎖,為什麼還要把「落點」写成 Open Question,而不是當成已有牙?
  - 事實:notes/design/five-station-simplify-f1-rp-min-set.md:L4 notes/design/five-station-simplify-f1-dual-read-annex.md:L36 scripts/five_station_f1.py:L327-L333 notes/design/five-station-simplify-f0-state-machine.md:L122-L139
  - 推理:數字與拒收謂詞是 F0／F1 的鎖。落點(倉、鍵、`hop_id`)明文不在 F1。現行牙讀的是 fixture 字樣。沒有倉,live 第三次重寫可以當第一次。B 線必須把落點問開,不能在 Stage 1 偷選。
  - 結論:CONFIRMED 數字已鎖、落點未鎖;Q9–Q16 移交 F2;本討論不選定倉。
- ⚠️ Q:為什麼把 cap 寫進現有 `coordinator/events.jsonl` 會變成暗改 cap?
  - 事實:observability/devflow_obs/ledger.py:L3-L6 notes/design/five-station-simplify-f0-state-machine.md:L124 notes/design/five-station-simplify-f0-state-machine.md:L198
  - 推理:ledger 按 `run_id` 分目錄。計數器卻是 slug 級、只增不減。新 run 讀空檔 = 計數 0 = X5。這是假設(Q10),不是已核「F2 會這麼做」。
  - 結論:NEEDS_VERIFICATION run 級倉=X5(Q10 `[~]`);過期不得當已核事實寫進 Decision。
- Q:現行事件欄為什麼接不住五站 hop?
  - 事實:observability/schema/agent-event.schema.json:L18 observability/schema/agent-event.schema.json:L81-L103 observability/devflow_obs/event_validate.py:L499-L503 observability/devflow_obs/event_validate.py:L542-L546
  - 推理:`stage` 只吃 `1-discussion` 這形。沒有 hop／latch／cap 型別。新名字會 `unknown_event_type`。偷加欄要 `x_` 或 bump schema。bump 會碰 doctor 的 schema 握手(Q18)。
  - 結論:CONFIRMED 現行 schema 接不住五站 hop;Q13／Q14／Q18 綁在一起移交。
- ⚠️ Q:marketplace 更新之後,doctor 綠了,coordinator 憑什麼仍走舊 7?
  - 事實:notes/design/five-station-simplify-f1-dual-read-annex.md:L18-L28 hooks/_doctor_impl.py:L193-L202 hooks/_doctor_impl.py:L492-L500 skills/dev-setup/SKILL.md:L62-L71 scripts/five_station_f1.py:L217-L224
  - 推理:hops 住方法包,update 換 cache。doctor 綠只證明契約版本 ∈ supported。F1 已紅「綠所以跟 hops」這句文案。F2 若寫 coordinator 卻用綠當通行證,SLOT 變成裝飾。前置假設=2.1.0 已宣告 ∧ 非 in-flight ∧ 預設只在 F3 後(Q17)。
  - 結論:CONFIRMED 綠 ≠ 切線。Q17 `[~]` 三前置;coordinator 行為牙是 F2 的,不是 F1 文案牙。
- Q:採用端最容易踩的升級陷阱是哪幾種?(發散)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L168 notes/design/five-station-simplify-f1-dual-read-annex.md:L22-L24 hooks/_doctor_impl.py:L216-L233 skills/dev-setup/SKILL.md:L16
  - 推理:典型路徑是先 update plugin。契約仍 2.0.0 + 新 hops = SLOT-REJECT。反過來,F2 bump schema 而契約未跟 = doctor 紅,人會以為「更新壞了」而不是「握手拒絕不同步」。多主機各一份 cache(Q20)會讓同一 repo 在 A 機五站、B 機舊 7。遠端改線 brief 已禁。
  - 結論:CONFIRMED 陷阱至少四種:不同步切線、不同步 schema 紅、多 cache、遠端改線。去向 Q17／Q18／Q20。
- Q:本 slug 會不會把自己當五站白老鼠?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L165-L166 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32 notes/design/five-station-simplify-f0-state-machine.md:L49-L50
  - 推理:本檔落盤後目錄已有 `1-discussion.md`。偵測規則只認 1–7 `.md`,不認 html。整段舊 7 到 Ship。F2 coordinator 對本目錄建五站機 = RP-15。
  - 結論:CONFIRMED 本 slug = live freeze 樣本(G-self-1、Q4);不是新 5 白老鼠。
- ⚠️ Q:本 hop 有沒有偷選落點或偷做 F3?(盲點)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L7-L9 本 hop brief(只 Stage 1、不改 STATUS、獨立 B 線)
  - 推理:Requested solution 只列候選。Q9 維持 `[>]`。隱含預設(run 級=X5、必須餵真計數、三前置)已標 `[~]` 與期限。不改 STATUS,避免跟「feature branch 不碰看板」撞車。
  - 結論:CONFIRMED 本 PR 只落討論;不選倉;不 F3;不改 STATUS。Q10／Q17／Q19 過期擋本 slug G2。
