---
feature: five-station-f2
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 1. 討論 — 五站 F2（Implementer C：anti-hollow／dual-path selftest）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／狀態機、以及 F1 已落地牙清冊，不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1 討論**；status 留 draft；不送 G1、不改 STATUS、不合併、不寫 coordinator 碼。
> 原料:`notes/design/five-station-simplify-brief-v3.md` §4 Runtime + §7 F2 列、`notes/design/five-station-simplify-f0-state-machine.md`、F1 落地牙清冊、`_templates/1-discussion.md`。
> C 線強調:F2 成功條件不是「coordinator 檔存在」、也不是「F1 牙還綠」。usable brief 寫明 F2 = coordinator 接自動前進 + event 留前進／latch／cap；**成功判準 = dual-path selftest 綠**。只綠 NEW5 開心路徑、或把 F1 對照稿字串紅當成活計數、或順便切 F3 預設路線，都是掏空。

## Problem
痛:F1 牙已能對 RP-1…16 與九個 SLOT 對照稿紅，但 repo 裡沒有 coordinator。現場要 hop 仍靠人／agent 在 chat 問「要不要繼續」。F1 的 RP-9／10／11 只吃對照稿字面「第 3 次」，不是 slug 級活計數；既有 `devflow-agent-event` 追的是 run／attempt／review，沒有前進／latch／cap。若本刀只交一個空殼 coordinator、或只測新 5 開心 hop、或把 F1 回歸綠寫成 F2 完成，勾選會綠、工作沒做完。
受影響:母版維護者、尚未落地的 coordinator、in-flight slug 執行者、Ship 審查者、採用端仍走舊 7 的人。頻率:每條要自動前進的五站 slug；舊 7 路徑每次 F2 回歸都要陪跑。影響:假 hop、無事件、或把進行中 feat 折成五站。
現在怎麼繞:人在 chat 問要不要繼續；F1 腳本對 fixture 字串紅；in-flight 繼續走 graph 的 `N7-g1`／`N6-g2` 等人。

## Context(已知事實)
- F2 刀做:coordinator／runtime 接自動前進；event 留前進／latch／cap；仍不刪舊 token。不做:把 in-flight 折成五站；拿掉 G1／G2／`ACCEPTED` 檔:notes/design/five-station-simplify-brief-v3.md:L171-L180
- Runtime:coordinator 讀 §3 謂詞，真則 hop、假則停；不准問「要不要繼續」。人才能寫 Ship `verdict:`／`ACCEPTED`／attestation。Latch 只准表 A／B 開火。觀測:前進／latch／cap 都要留機械紀錄(F2 才接 event schema):notes/design/five-station-simplify-brief-v3.md:L119-L133
- Rewrite cap 已鎖:hop≤2／Decide≤1／Goal reopen≤1；用盡 fail-closed 升給人，不准暗改 cap。舊 7 執行面仍跑既有 graph／模板／牙；coordinator 不得把舊 7 slug 強折成五站:notes/design/five-station-simplify-brief-v3.md:L131-L133
- F3 才 Cut:新 slug 預設五站。F0–F2 期間母版新開改版軌仍走舊 7。F3 不做:刪 token、改已 freeze 的 slug、一次改模板全文:notes/design/five-station-simplify-brief-v3.md:L164-L180
- in-flight = `docs/dev/<slug>/` 已有 1–7 任一 `.md` → 整段舊 7 到 Ship；只 html、零個 1–7 `.md` 才不算凍:notes/design/five-station-simplify-brief-v3.md:L160-L167 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32
- 狀態機:舊 7 in-flight 的 hop 本機不管；Idle 在 F3 前仍開舊 7；已有舊 7 檔 → 不建立五站機。`Ship` 無自動前進；機械全綠仍必須 HumanWait；代寫 `verdict: PASS`=違 OC-3:notes/design/five-station-simplify-f0-state-machine.md:L9-L15 notes/design/five-station-simplify-f0-state-machine.md:L36-L38 notes/design/five-station-simplify-f0-state-machine.md:L49-L50 notes/design/five-station-simplify-f0-state-machine.md:L110-L120
- 禁則 X2 刪 token、X4 in-flight 套新機、X5 暗改 cap、X6 latch 未命中卻問人:notes/design/five-station-simplify-f0-state-machine.md:L189-L201
- cap 計法:第一次寫不算；同一 hop 第 3 次重寫拒；Decide 重開≤1；離開 Intake 後 Goal reopen≤1；舊 7 不套這三 cap:notes/design/five-station-simplify-f0-state-machine.md:L122-L139
- F1 牙入口與自檢已落地:`scripts/check-five-station-f1.sh` 轉呼 `five_station_f1.py`；`scripts/test-five-station-f1.sh` 十二群(rp16／slots／dual-read／inflight／rp1／seam／spec-name／brief-files／attest／ship-quiz／rp-min-set／f1-close):scripts/check-five-station-f1.sh:L1-L9 scripts/test-five-station-f1.sh:L1-L16
- F1 釘 RP-1…16 與九 SLOT；RP-15=in-flight 不得五站 hop／寫五站狀態；RP-16=Agent 代寫判定=未寫:scripts/five_station_f1.py:L15-L26 scripts/five_station_f1.py:L226-L235 notes/design/five-station-simplify-f1-rp-min-set.md:L7-L25 notes/design/five-station-simplify-f1-dual-read-annex.md:L6-L38
- F1 超 cap 三列是對照稿字串紅，不是活計數器:fixture 寫「第 3 次重寫」即 RP-9；`kind==cap` 用正則吃「第 3 次／Decide 重開第 2／Goal 重開第 2」。5-tasks 明寫 T-11 不選 event 鍵名、不寫計數器:scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md:L1-L4 scripts/five_station_f1.py:L327-L333 docs/dev/five-station-simplify/5-tasks.md:L70-L72
- F1 父 slug 把 coordinator 評表 A／B、S-7.1…S-7.4 計數落點、S-8.2 coordinator+event 全部延後 F2；本 slug Stage 5–7 只准 F1:docs/dev/five-station-simplify/5-tasks.md:L66-L72 docs/dev/five-station-simplify/4-spec.md:L16-L17 docs/dev/five-station-simplify/4-spec.md:L828-L832
- S-1.2／S-1.3 觀測欄現況是 `n-a:F2 coordinator 尚未落地`；S-8.2 THEN=coordinator 評表 A／B + event 留前進／latch／cap；不准折 in-flight、不准刪 token、不准放寬三 cap:docs/dev/five-station-simplify/4-spec.md:L133-L137 docs/dev/five-station-simplify/4-spec.md:L153-L157 docs/dev/five-station-simplify/4-spec.md:L828-L832
- S-7.4:五站超限仍紅、舊 7 第 3 次站內重寫**不**因三 cap 紅(走既有 T 嘗試上限 4)；計數落點與 event 鍵名本檔不鎖(OC-3):docs/dev/five-station-simplify/4-spec.md:L768-L812
- 現有 event 正本是 Agent Attempt／Review／Tool lifecycle。已列 event_type 含 `run_started`…`final_fresh_run_completed`，**沒有** hop／latch／cap／HumanWait／Escalated。`stage` 欄 pattern 是 `^[1-7]-[a-z-]+$`，不是五站別名:hooks/devflow_obs_vendor/schema/agent-event.schema.json:L2-L18 hooks/devflow_obs_vendor/schema/agent-event.schema.json:L81-L104
- repo 無 coordinator 模組檔(本 hop glob `*coordinator*` = 0)。Stage 2／4 graph 預設路仍經 `N7-g1`／`N6-g2`:skills/dev-flow/stage2/graph.yaml:L53-L57 skills/dev-flow/stage4/graph.yaml:L93-L98
- Gate token 仍釘 G1／G2／G3 物質句；F1 live_close 要求 G1／G2／`ACCEPTED` 仍在:scripts/check-gate-tokens.sh:L44-L60 scripts/five_station_f1.py:L359-L362 scripts/test-five-station-f1.sh:L272-L274
- F1 live 關閉:七舊檔名在、無 `intake.md` 家族、Files 聯集只准 F1 牙／annex:scripts/five_station_f1.py:L345-L376
- STATUS Active 仍是父 slug `five-station-simplify` 在 6-implementation-notes、G3 未過；Backlog A 原文仍寫「下一刀 F1」(F1 牙已合、文案未改)。本 hop 不改 STATUS:docs/dev/STATUS.md:L30-L34 docs/dev/STATUS.md:L46-L52
- 本 hop 寫出 `docs/dev/five-station-f2/1-discussion.md` 之後，本 slug **自己**變成 in-flight(已有 1–7 `.md`)，整段走舊 7 到 Ship，不得當 NEW5 白老鼠:notes/design/five-station-simplify-brief-v3.md:L160-L167 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32
- F0 檔頭禁令:不准改 `_templates/`、README §7 錨、各站 `graph.yaml`、既有牙;不准刪 G1／G2／`ACCEPTED`:notes/design/five-station-simplify-brief-v3.md:L7-L9
- 受影響面(後續刀才動,本 hop 不動):尚未存在的 coordinator runtime、event 寫入點(既有 schema 或旁系,鍵名未鎖)、F2 selftest／fixture、`docs/dev/<slug>/` 路線判斷。**不准動**:`_templates/`、各站 `graph.yaml` 預設 hop、G1／G2／`ACCEPTED` token、F1 牙語意、契約 bump、STATUS／HISTORY。

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| owner | 摺例行等人,但不丟完整度;F2 要真 hop+真事件 | 裁 brief、寫 md `verdict:` | F0／F1 已核、本 tree | dual-path 會不會被寫成單路開心測 | Cursor chat |
| F1牙 | 對照稿紅 RP／SLOT；擋 in-flight 寫五站狀態 | 讀 fixture／annex；無 hop 權 | RP-1…16、九 SLOT | 計數落點尚未存在 | test-f1腳本 |
| in-flight執行者 | 走完手上舊 7,不被中途折五站 | 既有 graph／模板 | 自己目錄已有 1–7 `.md` | F2 會不會誤建五站機 | graph/twin |
| 派工 agent | 把本調查寫成討論檔 | 寫本目錄 Stage 1 | 白名單+指名原料 | owner 會不會把「檔在」當完成 | Cloud Agent、PR |
| Ship 審查者 | 出貨仍由人簽 | 寫 `7-review` `verdict:` | G3 物質 | 機械綠會不會被寫成 Done | 瀏覽器審頁 |

### Current Journey
正式 SOP:full 走 1→2→(3)→4→5→6→7,G1／條件 S3／G2／G3 各等人。F1 之後多了一層「牙對照稿可紅」,但仍無人評表 A／B。實際做法(沒有 F2 coordinator)如下。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | owner | chat問要不要繼續 | Cursor chat | — | 口頭准下一站,常無 hop 紀錄 | 謂詞假也改問人 |
| 2 | F1牙 | 對照稿字串紅 | test-f1腳本 | — | fixture 紅碼;無 slug 計數 | 無計數無事件 |
| 3 | in-flight執行者 | 走舊7等閘 | graph/twin | owner 寫 G1／G2 | 舊 7 站檔+twin | 怕被折成五站 |

### Workarounds
- owner／agent 用 chat「要不要繼續／可以開下一站」代替謂詞 hop。系統常不留前進紀錄,只留對話。
- F1 自檢對 `rp-09`／`rp-10`／`rp-11` 字串紅,讓「超 cap」看起來已有牙。沒有 coordinator 讀計數器,也沒有 event。
- in-flight 繼續走 `N7-g1`／`N6-g2` 等人。F1 RP-15 只能擋「對照稿裡寫五站 hop」,擋不住尚未存在的 runtime 真 hop。
- 既有 observability 把 `writer: coordinator` 的 attempt／run 事件寫進 `events.jsonl`。那是執行鏈,不是站級前進／latch／cap。
- 這些步驟常不留「哪一列謂詞為真才 hop」或「這次 cap +1 之後是幾」。

### Exceptions
- Fast lane 合法省略 Stage 1–3,仍吃 G2 物質;不是本包要廢 Fast。
- B1 沒命中 → 不產 Demo、不 latch。latch 未命中卻問人 = 違 brief,F1 RP-14 已能對照稿紅。
- in-flight:任一 1–7 `.md` → 不建立五站機,整段舊 7。本 slug 一落 `1-discussion.md` 即 freeze。
- F0–F2 母版新開改版軌仍舊 7,直到 F3 cut。F2 可在 **fixture／selftest** 跑 NEW5 路徑,不得把預設 graph hop 切成五站。
- 舊 7 重寫走既有 T 嘗試上限 4,不套 hop≤2／Decide≤1／Goal reopen≤1。
- `[Assumption]` dual-path 電池是**同一入口**兩路都必須能獨立變紅(不是兩支互不認識的腳本各綠一次)。風險=高(若為假,「selftest 綠」可只測開心 NEW5)；期限=Stage 2；過期擋把「只跑 F1 回歸」寫進 Decision。
- `[Assumption]` 前進／latch／cap 可落在既有 `devflow-agent-event` 擴充或旁系家族；本討論不鎖鍵名(OC-3)。風險=中(若為假,後站會提早鎖 schema)；期限=F2 annex／Stage 4；過期不得把鍵名寫進 Goal。
- `[Assumption]` NEW5 路徑的試體是合成 fixture,不是本 slug、也不是 `five-station-simplify`。風險=高(若為假,觀測被自己污染)；期限=Stage 2；過期擋 4C。

### Evidence
- F0 書面鎖定:notes/design/five-station-simplify-brief-v3.md:L119-L133、L171-L180；狀態機 notes/design/five-station-simplify-f0-state-machine.md。Owner 已核准(檔頭)。本 hop 不改那兩檔。
- F1 落地牙:scripts/five_station_f1.py、scripts/test-five-station-f1.sh、notes/design/five-station-simplify-f1-rp-min-set.md、notes/design/five-station-simplify-f1-dual-read-annex.md；父 slug 5-tasks／4-spec 延後表。本 hop 2026-09-14 讀過,行段支持斷言。
- F1 cap 對照稿只四行字面:scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md:L1-L4。
- 現有 event 清單無 hop／latch／cap:hooks/devflow_obs_vendor/schema/agent-event.schema.json:L81-L104。
- graph 預設人類停點仍在:skills/dev-flow/stage2/graph.yaml:L53-L57、skills/dev-flow/stage4/graph.yaml:L93-L98。
- `[Assumption]` 三條見 Exceptions。無採用端 F2 runtime 逐字稿。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「同一入口兩路都能紅」為假 → 兩支腳本各綠可冒充 dual-path | 高 | Stage 2 對帳:Decision 是否要求同一電池缺一路即紅 | Stage 2／收斂者;過期擋 G2 |
| 「鍵名可後鎖」為假 → 本檔若先寫鍵名=偷做 annex | 中 | 本檔 Goals／AC 無 event 欄名;後站才選落點 | F2 annex／Stage 4 |
| 「NEW5 用合成 fixture」為假 → 拿本 slug 當白老鼠,違 OC-9 | 高 | Files／fixture 路徑不含本目錄站檔當 hop 試體 | Stage 2;過期擋 4C |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 Runtime + F2 列 | 本刀範圍與成功條件 | notes/design/five-station-simplify-brief-v3.md | 是(使用者點名) | 是 |
| F0 狀態機 | 謂詞／cap／latch／禁則 | notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名) | 是 |
| F1 落地牙清冊 | 繼承什麼、什麼還是對照稿 | scripts/five_station_f1.py、scripts/test-five-station-f1.sh、scripts/fixtures/five-station-simplify/、兩份 annex、父 slug 4-spec／5-tasks | 是(使用者點名) | 是 |
| Stage 1 模板 | 十節＋現況圖＋html 產器 | _templates/1-discussion.md | 是(使用者點名) | 是 |
| 現有 event／graph／token | 證明 F2 事件與預設路線都還沒接 | hooks/devflow_obs_vendor/schema/agent-event.schema.json、skills/dev-flow/stage2/graph.yaml、stage4/graph.yaml、scripts/check-gate-tokens.sh | 是(本 tree) | 是 |
| 採用 F2 逐字稿 | 驗證現場是否已有自動 hop | 無;F2 runtime 尚未存在 | 禁 | 否 |

## Goals
- G-out-1:**dual-path selftest 同一電池兩路全綠**才算 F2 完。缺 NEW5 或缺 OLD7、或把 F1 回歸綠寫成 F2 綠 = 未完成。
- G-out-2:NEW5(非 in-flight 試體)謂詞全真 → coordinator hop 下一站,紀錄不含「要不要繼續／請人審 A4／A7」。任一謂詞假 → 停該站修,理由含該謂詞,不改問人。
- G-out-3:前進／latch／cap **三次觸發都留下可核對的機械紀錄**。只有註解、或只有 attempt／review 事件、或缺一類 = 沒有 F2 event。
- G-out-4:三 cap 是活計數(只增不減)。同一 hop 第 3 次重寫、Decide 第 2 次整站重開、離開 Intake 後 Goal 第 2 次重開 → Escalated,不得暗改歸零。舊 7 同樣動作**不**因這三 cap 紅。
- G-out-5:in-flight slug(已有 1–7 任一 `.md`)不被寫入五站狀態、不被五站 hop。coordinator 看到舊 7 標記就放手給既有 graph。
- G-out-6:F2 之後 G1／G2／`ACCEPTED` token 與檔仍在;F1 十二群自檢仍綠。不得為了好寫謂詞刪 token。
- G-out-7:Ship 無自動前進。機械全綠仍 HumanWait。Agent／coordinator 寫 `ACCEPTED` 或 Ship `PASS` = 未寫。
- G-out-8:本刀不是 F3。graph 預設 hop 仍經 `N7-g1`／`N6-g2`。本 slug 與父 slug 都是 freeze 樣本,不得當 NEW5 白老鼠。

## Requested solution
- 候選(未定案):coordinator 讀 brief §3／狀態機謂詞,真 hop、假停修;latch 開火進 HumanWait;cap 用盡進 Escalated。
- 候選(未定案):機械紀錄涵蓋前進／latch／cap 三次觸發。鍵名／檔名／是否擴充既有 schema **未定**(OC-3)。
- 候選(未定案):一支(或同一入口的兩 group)selftest 同時跑 NEW5 與 OLD7,缺一路即紅。
- 本 hop 不選定腳本路徑、event 欄名、或產頁引擎實作。

## Non-Goals(初稿)
- **鎖:不切 F3 預設路線。**不准改各站 `graph.yaml` 讓新 slug 預設 Intake→Ship。那是 F3 cut,不是 F2 成功。
- **鎖:不把 in-flight 折成五站。**已有 1–7 `.md` 的 slug(含本目錄一落檔、含 `five-station-simplify`)整段舊 7 到 Ship。
- **鎖:不刪 G1／G2／`ACCEPTED` 檔或 token。**
- 不放寬 hop≤2／Decide≤1／Goal reopen≤1;不准用盡後 reset。
- 不改 F1 牙語意、不減 RP-1…16、不重開 1B／2B／4C／6B／7C。
- 不 bump 契約、不把 doctor 握手綠說成已切五站。
- 本 hop 不寫 coordinator 碼、不改 STATUS／HISTORY／`_templates/`、不送 G1、status 留 draft。
- 不把七份文檔改名成 `intake.md` 家族。
- 不把既有 attempt／review 事件冒充站級前進／latch／cap。
- 不拿本 slug 或父 slug 當 NEW5 hop 試體。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:full
- [x] Q2:本 hop 是否只 Stage 1、draft、獨立 A／B?→ 使用者:是;只產本目錄 `1-discussion.md`+html
- [x] Q3:F2 成功條件?→ usable brief:coordinator 自動前進 + event 留前進／latch／cap;**判準 = dual-path selftest 綠**,不是檔在、不是 F1 仍綠
- [x] Q4:本刀是否含 F3 預設路線切?→ 否。F3 另刀;graph 預設 hop 不動
- [x] Q5:Non-Goals 是否鎖 F3／in-flight 折／token 刪?→ 是,本檔鎖死
- [x] Q6:F1 超 cap 牙算不算 F2 計數已落地?→ 否。T-11 對照稿字串紅;計數落點交 F2(S-7.4)
- [x] Q7:本 slug 落檔後走哪條路?→ 已有 `1-discussion.md` = in-flight,整段舊 7。NEW5 只准合成 fixture
- [~] Q8:event 落在既有 `devflow-agent-event` 還是旁系?(帶假設:可後選;本討論不鎖鍵名。風險=中;期限=F2 annex／Stage 4)
- [~] Q9:dual-path 要同一入口才能紅?(帶假設:是;缺一路即整電池紅。風險=高;期限=Stage 2,過期擋 G2)
- [>] Q10:F3 新 slug 預設五站怎麼 cut?→ 移交 `five-station-f3`(建議 slug);本討論不解

## Constraints
- 本 PR 不宣稱 G1 PASS;不改 STATUS／HISTORY;不寫碼。
- 討論盲下游:本檔不指定腳本／API／元件當 Goal。
- **Owner-locked rewrite cap:**hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改。舊 7 不套。
- **Owner-locked Non-Goals:**F3 cut／in-flight 折／token 刪 三條本討論即鎖,後站不得改成可選。
- **OC-3:**不鎖 event／annex 鍵名。Q8 帶假設。
- 詞條(語言,不是方案):**F2**=coordinator 自動前進 + 前進／latch／cap 機械紀錄。**dual-path**=同一電池的 NEW5(非 in-flight 試體 hop+事件)與 OLD7(in-flight／dual-read 不折、token 在、三 cap 不套)。**掏空**=檔在或 F1 綠或單路開心測冒充 F2 完。**活計數**=slug 級只增不減的 cap,對照稿字串紅不算。**NEW5 試體**=合成 fixture,不是已有 1–7 `.md` 的目錄。本 hop 不寫進長期記憶(`CONTEXT.md` 本 tree 不存在;使用者限產本目錄雙檔)。

### F1 落地牙清冊(本刀繼承,不准當 F2 完成證明)
| 已落地 | 人看見 | 還不是 F2 |
|---|---|---|
| RP-1…16 對照各紅;減列 annex 紅 | `test-five-station-f1.sh --group rp-min-set` | 無 coordinator 評表 A／B |
| 九 SLOT dual-read 誠實 | `--group slots`／`dual-read` | 無 2.1.0 bump、無預設切線 |
| RP-15 in-flight 對照稿拒 hop | `--group inflight` | runtime 尚無五站機可誤寫 |
| RP-16 Agent 代寫=未寫 | `--group rp16` | 尚無 coordinator 可代寫 Ship |
| RP-9／10／11 字面「第 N 次」紅 | fixture 四行+`kind==cap` 正則 | **無活計數、無 event** |
| live_close:七舊名、token 在、無新家族 | `--group f1-close` | 不證明 hop 發生過 |
| 父 slug Files 聯集關閉、零 coordinator | 5-tasks S-8.5／延後表 | F2 另 slug 才准寫 runtime |

### F2 dual-path 必須證明(後站不准掏空)
後站若把下表當「簡化細節」拿掉,selftest 可綠、工作沒做完。本表是調查產出,不是施工單。

| 帶走什麼 | 若被 Spec／Build 偷走 | 人看見什麼 | 怎麼知道沒做完 |
|---|---|---|---|
| NEW5:謂詞全真 → hop、不改問人 | coordinator 檔在但不 hop | 仍 chat「要不要繼續」 | 電池無 hop 紀錄,或紀錄含改問人句 |
| NEW5:謂詞假 → 停修、理由含該謂詞 | 假謂詞改問人／進 HumanWait | 停成等人 | 理由無該謂詞、或含「要不要繼續」 |
| NEW5:latch 真 → HumanWait;禁代寫判定 | 機械綠寫 PASS／ACCEPTED | Ship 自動 Done | 無人頂欄 PASS 卻 Done |
| NEW5:前進／latch／cap 三類機械紀錄 | 只寫註解或 attempt 事件冒充 | F1 綠、runtime 無痕 | 三類缺一 |
| NEW5:三 cap 活計數、用盡 Escalated | 對照稿字串紅當計數 | 第 3 次仍 hop | 計數未增仍繼續 |
| OLD7:in-flight 不建機、不寫五站狀態 | 已有 md 的 slug 被折五站 | 例行 G1 被跳過 | 五站狀態寫入或 hop 成功 |
| OLD7:不套三 cap | 舊 7 被 hop≤2 誤殺 | 合法重寫變 Escalated | 舊 7 因三 cap 紅 |
| OLD7:token + F1 十二群仍綠 | 刪 token 好寫謂詞 | dual-read／舊 7 一次紅 | token 缺或 F1 回歸紅 |
| 兩路同一電池全綠 | 只測 NEW5 或只重跑 F1 | 「selftest 綠」假完成 | 任一 path 無具名可紅案 |
| 非 F3:graph 預設仍 `N7-g1`／`N6-g2` | 順便切預設路線 | 新 slug 被遠端改線 | `graph.yaml` 預設切線(本刀 Non-Goal) |

## 驗收雛形
- AC-1(G-out-1):假設 F2 宣稱完成,當人只跑成功電池,則 NEW5 與 OLD7 兩組具名案都必須能獨立變紅、也必須能一起綠;只重跑 `test-five-station-f1.sh` 不算 F2 綠。
  - 從哪看:F2 selftest 出口與具名 CASE 清單(後續造;本 hop 不跑)
  - 看到什麼算對:兩 path 都有至少一條正向綠、一條缺行為紅;整電池 exit 0 當且僅當兩路都過
  - 拿什麼試:合成 NEW5 fixture + 已有 1–7 `.md` 的 OLD7 fixture;不是本目錄
- AC-2(G-out-2):假設 NEW5 試體 Decide／Spec／Build 謂詞全真且中間 latch 未命中,當 coordinator 評謂詞,則它 hop 且不在 A4／A7 等人;再假設同一試體少一條 OC 裁決,則停修理由含該謂詞、不含「要不要繼續」。
  - 從哪看:該試體前進／停點紀錄
  - 看到什麼算對:真→有 hop、無「請人審 A4／A7」;假→無 hop、理由點名謂詞
  - 拿什麼試:後續造的兩份 NEW5 對照(全真／缺 OC)
- AC-3(G-out-3):假設 NEW5 發生一次 hop、一次 latch 開火、一次 cap 用盡,當人讀機械紀錄,則三類觸發各至少一筆,且不是 `attempt_completed`／`review_completed` 冒充。
  - 從哪看:F2 觀測落點(檔／log;鍵名未定)
  - 看到什麼算對:三類齊;缺一類則電池紅
  - 拿什麼試:同一試體依序觸發三件事的 fixture
- AC-4(G-out-4):假設 NEW5 同一 hop 已重寫 2 次,當第 3 次仍被要求繼續,則 Escalated、計數不得歸零。再假設 OLD7 做第 3 次站內重寫,則**不**因這三 cap 紅。
  - 從哪看:NEW5 計數與拒絕;OLD7 既有 T 嘗試路徑
  - 看到什麼算對:NEW5 第 3 次紅;OLD7 不因 cap 紅
  - 拿什麼試:活計數試體,不是只改 `rp-09` 字串
- AC-5(G-out-5):假設某目錄已有 `1-discussion.md`,當 coordinator 被要求五站 hop,則拒寫五站狀態、放手給舊 7 graph。
  - 從哪看:該目錄檔案與被拒 hop
  - 看到什麼算對:無五站機寫入;仍走 `N7-g1`／`N6-g2` 等閘
  - 拿什麼試:父 slug 目錄或同等 OLD7 fixture
- AC-6(G-out-6):假設 F2 落地後有人掃 token 與 F1 十二群,當對照 F1 live_close,則 G1／G2／`ACCEPTED` 仍在,且 `test-five-station-f1.sh` 仍綠。
  - 從哪看:token 掃描 + F1 自檢出口
  - 看到什麼算對:三 token 在;F1 failed=0
  - 拿什麼試:本 tree 現有 F1 入口;F2 diff 不得刪 token
- AC-7(G-out-7):假設 NEW5 已機械全綠走到 Ship,當無人寫頂欄 `verdict: PASS`,則不得 Done;coordinator 寫 PASS 視為未寫。
  - 從哪看:slug 狀態與判定行
  - 看到什麼算對:停 HumanWait;無人類 PASS 不得 Done
  - 拿什麼試:Ship 機械綠、頂欄空／agent 寫 PASS 的對照
- AC-8(G-out-8):假設有人把本刀 diff 拿去改 `graph.yaml` 預設 hop 或拿本目錄當 NEW5 試體,當對照本檔 Non-Goals,則該改動不算 F2 成功。
  - 從哪看:`git diff` 檔名與 fixture 路徑
  - 看到什麼算對:無各站 `graph.yaml` 預設切線;NEW5 fixture 不在 `docs/dev/five-station-f2/` 或 `docs/dev/five-station-simplify/`
  - 拿什麼試:本 PR 檔集;後續 F2 實作 PR 的 Files 聯集

## 現況圖
誰:owner
做什麼:chat問要不要繼續
工具:Cursor chat
痛點:謂詞假也改問人
↓
誰:F1牙
做什麼:對照稿字串紅
工具:test-f1腳本
痛點:無計數無事件
↓
誰:in-flight執行者
做什麼:走舊7等閘
工具:graph/twin
痛點:怕被折成五站

## 邏輯圖(ASCII)
```
now
|-- owner chat
|   +-- ask continue          [no hop record]
|-- F1 teeth
|   |-- RP/SLOT fixture red
|   +-- cap = string match    [not live count]
+-- in-flight old 7
    |-- N7-g1 / N6-g2 wait
    +-- fear fold

f2-must-prove
|-- NEW5 fixture
|   |-- pred true = hop
|   |-- pred false = stop-fix
|   +-- events: hop,latch,cap
|-- OLD7 fixture
|   |-- no five-state
|   |-- no three-cap
|   +-- tokens + F1 still green
+-- hollow if
    |-- file exists only
    |-- F1 green as F2
    +-- F3 cut smuggled
```

## Interview Log(推理鏈外顯)
- Q:為什麼 F2 完成不能等於「coordinator 檔存在」或「F1 還綠」?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L171-L180 notes/design/five-station-simplify-brief-v3.md:L119-L133 docs/dev/five-station-simplify/4-spec.md:L828-L832 scripts/test-five-station-f1.sh:L1-L16
  - 推理:brief F2 列要的是自動前進行為 + 前進／latch／cap 紀錄。F1 十二群證明的是對照稿牙,S-1.2 自己寫 n-a:F2 未落地。檔在或 F1 回歸綠沒有鑑別力——沒 hop 也能綠。
  - 結論:CONFIRMED F2 成功判準 = dual-path selftest 綠;F1 綠是回歸地板,不是本刀完成證明。
- ⚠️ Q:F1 的 RP-9／10／11 為什麼不能當 F2 計數已落地?
  - 事實:scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md:L1-L4 scripts/five_station_f1.py:L327-L333 docs/dev/five-station-simplify/5-tasks.md:L70-L72 docs/dev/five-station-simplify/4-spec.md:L808-L812
  - 推理:fixture 四行寫「第 3 次」就紅。`kind==cap` 吃字面。5-tasks 寫明不寫計數器、不選 event 鍵名。S-7.4 把落點交 F2。把字串紅當成活計數 = 掏空。
  - 結論:CONFIRMED 對照稿字串紅 ≠ 活計數;G-out-4／AC-4 必須用會 +1 的試體。
- ⚠️ Q:既有 `writer: coordinator` 的 events.jsonl 算不算 F2 event?
  - 事實:hooks/devflow_obs_vendor/schema/agent-event.schema.json:L2-L18 hooks/devflow_obs_vendor/schema/agent-event.schema.json:L81-L104 notes/design/five-station-simplify-brief-v3.md:L133
  - 推理:現有事件是 attempt／review／run 生命週期。清單沒有 hop／latch／cap。brief 要留的是站級前進／latch／cap。拿執行鏈冒充站級觀測,電池會假綠。
  - 結論:CONFIRMED 三類站級觸發必須另有可核對紀錄;鍵名未鎖(Q8)。
- Q:為什麼 F3 切預設路線必須鎖在 Non-Goals?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L164-L180 notes/design/five-station-simplify-f0-state-machine.md:L36-L38 skills/dev-flow/stage2/graph.yaml:L53-L57 skills/dev-flow/stage4/graph.yaml:L93-L98
  - 推理:F2 可在 fixture 跑 NEW5,但 Idle 在 F3 前仍開舊 7。graph 預設仍 N7-g1／N6-g2。把切線當 F2 成功 = 併刀,採用端未 upgrade 也會被遠端改 hop。
  - 結論:CONFIRMED Q4／G-out-8;graph 預設切線是 F3,不是本刀。
- Q:本 slug 一寫 1-discussion 為什麼不能當 NEW5 試體?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L160-L167 notes/design/five-station-simplify-f1-dual-read-annex.md:L30-L32 notes/design/five-station-simplify-f0-state-machine.md:L49-L50
  - 推理:SLOT-IN-FLIGHT-DETECT:任一 1–7 `.md` → in_flight=true,不得寫五站狀態。本檔一落地本目錄即 freeze。拿自己 hop = 4C,觀測被污染。
  - 結論:CONFIRMED Q7;NEW5 只准合成 fixture。
- ⚠️ Q:若只測 NEW5 開心 hop、不跑 OLD7,最極端會怎樣?(發散)
  - 事實:notes/design/five-station-simplify-f0-state-machine.md:L189-L201 notes/design/five-station-simplify-brief-v3.md:L171-L180 scripts/five_station_f1.py:L226-L235
  - 推理:寫手會讓 coordinator 對任何目錄 hop。in-flight 被折、token 被刪「好寫謂詞」、舊 7 被三 cap 誤殺。brief F2「不做」列整排失效,但單路 selftest 仍綠。
  - 結論:CONFIRMED 缺 OLD7 具名可紅案 = 電池未完成;這是 C 線主風險。
- Q:隱含預設「F2 先把 coordinator 掛上、event 下一刀再接」成立嗎?(盲點)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L133 docs/dev/five-station-simplify/4-spec.md:L828-L832
  - 推理:brief 把「要留機械紀錄」鎖在 F2,不是 F3。S-8.2 THEN 同時要 coordinator 與 event。拆刀會讓 hop 無法審計,蓋章只是從 chat 搬進無痕 hop。
  - 結論:CONFIRMED 前進／latch／cap 紀錄與自動前進同刀;只交 hop 不交事件 = 掏空。
- ⚠️ Q:本 hop 有沒有把 F2 當成已經施工、範圍有沒有長到 F3?(盲點)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L7-L9 docs/dev/STATUS.md:L30-L34
  - 推理:F1 已落盤是 Context,不是本 PR 實作。本檔不寫碼、不改 graph、不改 STATUS。Q8／Q9 帶假設進 Stage 2,不升格。Q10 移交 F3。
  - 結論:CONFIRMED 本 PR 只落討論;不重開十條;不切 F3;不把假設寫成已核事實。
