---
feature: five-station-f2
stage: 1-discussion
status: draft
owner: rick
reviewers: []
updated: 2026-09-14
---

# 1. 討論 — 五站 F2（Implementer A：缺 coordinator 的現場痛／event 槽／Must-keep vs hop）

> 用途:發散。**不做決定**。本場依 owner 已鎖 F0 brief／狀態機,加上已出貨的 F1 牙與 annex,不是現場一問一答。
> Lane = **full**。本 hop **只 Stage 1 討論調查**；不送 G1、不改 STATUS、不合併。
> A 線強調:F1 牙已能把「非法 hop」的**對照稿**變紅,但沒有 runtime 真的 hop 或拒絕 hop。謂詞全真仍要等人說「繼續」;latch／cap 觸發沒有機械紀錄。自動前進若跳過 Must-keep,會比舊 7 更快假完成。
> 獨立於 B／C。本檔自足。

## Problem
痛:F1 牙已能把「第三次重寫仍繼續」的對照稿變紅,但沒有 coordinator 真的 hop 或拒絕 hop。謂詞全真仍要等人說「繼續」;latch 開火與 cap 觸發只留在 chat 與 STATUS。Must-keep 若被 hop 跳過,假完成會比舊 7 更快。
受影響:母版 owner、下一站寫手、尚未落地的 coordinator、Ship 審查者。頻率:每條想走五站的 full lane；本刀落地前每一刀都靠手開。影響:F1 出貨後下一站仍排隊,或 hop 時把完整度一起跳過。
現在怎麼繞:owner chat「可以開下一站」;寫手手寫下一站檔;F1 對照稿當紙上牙;STATUS／HISTORY 當 hop 紀錄。

## Context(已知事實)
- F0 十條已鎖;F2 刀=Coordinator／runtime 接自動前進,event 留前進／latch／cap,仍不刪舊 token;不准把 in-flight 折五站、不准刪 G1／G2／`ACCEPTED`、不准把新 slug 預設切五站(那是 F3):notes/design/five-station-simplify-brief-v3.md:L30-L45 notes/design/five-station-simplify-brief-v3.md:L171-L180
- 摺的是預設人類停點,不是完整度;Must-keep M1–M16 少一條=違 brief:notes/design/five-station-simplify-brief-v3.md:L13-L28 notes/design/five-station-simplify-brief-v3.md:L135-L158
- Runtime 從 F2 落地:Coordinator 讀表 A／B 謂詞,真則 hop、假則停修,不准問「要不要繼續」;前進／latch／cap 觸發都要留機械紀錄(F0 只鎖「要留」):notes/design/five-station-simplify-brief-v3.md:L119-L133
- Ship 無自動前進;機械全綠仍必須 HumanWait;代寫 `verdict: PASS`=違 OC-3:notes/design/five-station-simplify-f0-state-machine.md:L110-L120
- rewrite cap 已鎖:hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改;舊 7 不套:notes/design/five-station-simplify-f0-state-machine.md:L122-L139
- Latch 列假→禁問人;列真→必須 HumanWait;沒命中卻問人=違 brief:notes/design/five-station-simplify-f0-state-machine.md:L163-L179
- F0–F2 期間新開的母版改版軌仍走舊 7;F3 cut 之後才預設五站:notes/design/five-station-simplify-brief-v3.md:L160-L167
- F1 dual-read annex:SLOT-id 是語意槽,不是 JSON／YAML 必填鍵(OC-3:不鎖欄位鍵名);計數落點(event 鍵名)不在 annex 鎖定:notes/design/five-station-simplify-f1-dual-read-annex.md:L1-L4 notes/design/five-station-simplify-f1-dual-read-annex.md:L34-L36
- F1 RP 最小集:超 cap 三列的計數落點交 F2;本檔不是 event schema:notes/design/five-station-simplify-f1-rp-min-set.md:L1-L4 notes/design/five-station-simplify-f1-rp-min-set.md:L18-L20
- F1 牙 `kind==cap` 用正文正則咬「第 3 次／Decide 重開第 2／Goal 重開第 2」,不是活計數器:scripts/five_station_f1.py:L327-L333
- 三張超 cap 對照稿只是敘述卡:scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md:L1-L4 scripts/fixtures/five-station-simplify/rp-10-second-decide-reopen.md:L1-L4 scripts/fixtures/five-station-simplify/rp-11-second-goal-reopen.md:L1-L4
- F1 牙 `kind==inflight` 咬「對照稿列出 1–7 md 且請求五站 hop」;沒有 runtime 阻擋活 hop:scripts/five_station_f1.py:L226-L235
- F1 牙 `kind==attest` 咬 latch=否卻寫「請 owner 看一下／要不要繼續」:scripts/five_station_f1.py:L298-L300 scripts/fixtures/five-station-simplify/rp-14-please-review-latch-false.md:L1-L5
- F1 牙檔頭寫明不鎖 annex 鍵名(OC-3):scripts/five_station_f1.py:L1-L3
- 父 slug 5-tasks 延後表:S-1.2…S-1.12 的 coordinator 評表 A／B、S-7.1…S-7.4 計數落點、S-8.2 coordinator+event 都交另刀 F2;F1 不選 event 鍵名、不寫計數器:docs/dev/five-station-simplify/5-tasks.md:L66-L72 docs/dev/five-station-simplify/5-tasks.md:L17-L24
- 父 slug 4-spec S-8.2:F2 結束必須有 coordinator 評表 A／B 自動前進,且 event 留前進／latch／cap;不准折 in-flight、不准刪 token、不准放寬三 cap:docs/dev/five-station-simplify/4-spec.md:L828-L832
- 父 slug 4-spec:計數落點(event schema／哪支腳本／哪根欄)交 F2,不鎖鍵名(OC-3／Q10):docs/dev/five-station-simplify/4-spec.md:L769 docs/dev/five-station-simplify/4-spec.md:L808-L812
- 父 slug Stage 6 T-11 自記:未實作 F2 計數器、未鎖 event 鍵:docs/dev/five-station-simplify/6-implementation-notes.md:L187
- 父 slug F1 已 Human G3 PASS(`verdict: PASS`,human:rick @ 2026-09-14);Active 已移出:docs/dev/five-station-simplify/7-review.md:L1-L12 docs/dev/HISTORY.md:L659-L663
- 本 tree 無進行中改版軌;STATUS Backlog A 仍寫「下一刀 F1」(看板未改指 F2):docs/dev/STATUS.md:L32 docs/dev/STATUS.md:L50
- 既有 agent-event 1.1 有 `stage_started`／`stage_completed`,`stage` 形狀是 `^[1-7]-[a-z-]+$`;事件表無 hop／latch／cap:observability/schema/agent-event.schema.json:L18 observability/schema/agent-event.schema.json:L81-L103
- 契約與 runtime 仍 `2.0.0`;agent_event schema 仍 1.1:devflow-contract.json:L1-L12 hooks/runtime-capabilities.json:L1-L17
- Stage 2 graph 預設路經仍含 `N7-g1`(例行人類停點節點):skills/dev-flow/stage2/graph.yaml:L53-L57
- 母版 dogfood 曾用 chat 准開 Stage 4,Human verdict／attestation 欄仍空:docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9
- 每個 T 必填 Covers／Files／Verify／Blocked-by: _templates/5-tasks.md:L50
- 受影響面(後續刀才動,本 hop 不動):尚不存在的 coordinator runtime、event 落點、既有 `graph.yaml` 預設路、`devflow-agent-event` 是否加槽、採用端 upgrade。本 hop 只落討論雙檔。

## Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 母版 owner(tony／rick) | F1 出貨後下一站真的自動走;Ship 仍由人出貨 | 裁 F2 範圍、簽 G1／G2／G3、寫 md `verdict:` | F0 brief、F1 牙、本 tree | 謂詞真時誰該 hop;cap 計在哪 | GitHub、Cursor chat |
| 下一站寫手 | 謂詞真就動手寫下一站,不要等「要不要繼續」 | 寫 2／4／5／6 檔 | 模板、F1 對照稿 | 沒有 runtime 告訴他「可以 hop」 | PR、chat |
| coordinator(尚未落地) | 謂詞真 hop、假停修、latch 開火才問人 | 讀謂詞、禁寫判定 | 表 A／B、狀態機 | 現場會不會要求「順便問人」 | 無(碼不存在) |
| F1 牙 | 對照稿／annex 違 RP 就紅 | 讀 fixture 正文與 `--live` 目錄形狀 | RP-1…16、SLOT | 活 hop、活計數、活 event | `five_station_f1.py` |
| Ship 審查者 | 出貨樹=審過的樹;機械綠 ≠ PASS | 寫 7-review `verdict:` | G3 八點 | hop 過程有沒有跳過 Must-keep | 瀏覽器審頁 |
| in-flight slug 執行者 | 走完手上舊 7,不被新機折線 | 既有 graph／模板 | 自己目錄已有 1–7 md | F2 runtime 會不會誤寫五站狀態 | 既有 hop |
| 採用專案 owner | 少停、別被遠端改線 | 系統外 | 自己踩到的閘 | 母版 F2 會不會改他的預設路 | Email、口頭 |

## Real-world Context

### Actors
表見上節 `## Actors`。產檔器吃獨立 H2,避免把 Journey／Assumption 表捲進 `#scan-people`。

### Current Journey
正式 SOP(brief):五站預設路上,coordinator 評謂詞,真則 hop,假則停修;latch 列真才 HumanWait;hop／latch／cap 留機械紀錄。實際做法(F1 已出貨、F2 未落地)如下。兩者都記。

| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | F1 牙 | 對對照稿跑 RP／SLOT;超 cap 三卡各紅一次 | `check-five-station-f1.sh` | 無人(fixture 自檢) | fixture RED 輸出 | 咬的是敘述卡,不是活 hop |
| 2 | owner | chat「過／可以開下一站」 | Cursor chat | — | 下一站 md 被手開 | 謂詞真也等人;謂詞假也可被准 |
| 3 | 寫手 | 手寫 2／4／5／6／7 | 舊 7 graph(`N7-g1` 仍在) | owner 口頭 | 站檔+twin | 沒有「自動前進」這件事 |
| 4 | STATUS 寫入口 | 人跑 `status-update.sh` 或合併後改看板 | STATUS／HISTORY | 合併的人 | 看板列 | Backlog A 仍指 F1,F1 已 G3 PASS |
| 5 | 無人 | 不評表 A／B、不進 HumanWait、不 tick cap | 無 coordinator | — | 無 hop／latch／cap event | 事後無法證明誰 hop、誰被 latch、誰用盡 cap |
| 6 | F1 牙(再一次) | 若有人把「要不要繼續」寫進對照稿 → RP-14 紅 | 同 Step 1 | — | 又一張紅卡 | 活 chat 那句不會被這支牙看見 |
| 7 | Ship 審查者 | 人寫 `verdict: PASS`(父 slug #323) | 7-review | 自己 | 頂欄 PASS | 中間 hop 沒紀錄,只能信人說「沒跳 Must-keep」 |

### Workarounds
- owner 用 chat 當 hop 開關:「可以開 Stage 4」「過」。系統留下下一站檔,不留下「哪一條自動前進謂詞為真」。
- F1 用三張超 cap 對照稿假裝有計數器;計數本身不存在。
- STATUS／HISTORY 當 hop log:人記得改看板,看板可以停在過期的「下一刀 F1」。
- 既有 `devflow-agent-event` 的 `stage_started`／`stage_completed` 追的是 Stage 6 run 生命週期,不是五站 hop。
- 這些步驟常不留「這次 hop 時 Must-keep 哪幾條綠」。

### Exceptions
- Fast lane 合法省略 Stage 1–3,仍吃 G2 物質;不是本包要廢 Fast。
- B1 沒命中 → 不產 Demo、不 latch;A10 永遠 latch。
- in-flight:目錄已有 1–7 任一 md → 整段舊 7。本資料夾一旦有 `1-discussion.md` = 本 slug 自己 in-flight,走舊 7 到 Ship。
- F0–F2 母版新開軌仍走舊 7(brief §6)。本 slug 是 F2 調查軌,不是 F3 白老鼠。
- 舊 7 不套 hop／Decide／Goal 三 cap;它們走既有 T 嘗試上限 4。
- `[Assumption]` F1 出貨後,下一條 full lane 仍會用 chat 准 hop:無 F1-之後的第二條 live 五站軌;風險=高(若為假,「缺 coordinator」的現場理由變弱,F2 仍要接 event 與 dual-path);期限=本 slug G2 前看下一條母版 full lane,過期不得把「現場已自動 hop」寫成已核事實。
- `[Assumption]` 既有 agent-event 1.1 會被拿來掛 hop／latch／cap 槽,而不是另開帳本:無選定落點;風險=中(若為假,F2 另本,1.1 的 `stage` 形狀仍只服務舊 7);期限=Stage 2;本討論不鎖鍵名。

### Evidence
- F0 書面鎖定:notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md。本 hop 不改那兩檔。
- F1 已核出貨:docs/dev/five-station-simplify/7-review.md:L1-L12;HISTORY:docs/dev/HISTORY.md:L659-L663;牙與 annex 見 Context。
- F1 只咬文字、不 hop:scripts/five_station_f1.py:L327-L333、L226-L235、L298-L300;三張 cap fixture 與 RP-14 fixture。
- 父 slug 自己把 coordinator／計數落點／event 鍵名延後到 F2:docs/dev/five-station-simplify/5-tasks.md:L66-L72、4-spec.md:L828-L832、6-implementation-notes.md:L187。
- 既有 event 表無 hop／latch／cap:observability/schema/agent-event.schema.json:L81-L103。
- 現場手 hop:docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9;graph 仍經 `N7-g1`:skills/dev-flow/stage2/graph.yaml:L53-L57。
- 看板 lag:docs/dev/STATUS.md:L32、L50。
- `[Assumption]` 兩條見 Exceptions。

### Assumption 四欄
| 若為假影響什麼 | 影響級 | 怎麼驗 | 何時／由誰驗 |
|---|---|---|---|
| 「F1 之後現場仍 chat-hop」為假 → 缺 coordinator 的現場理由變弱;F2 仍要接 event 與 dual-path | 高 | 看 F1 G3 之後下一條母版 full lane:下一站是 chat 准的還是謂詞 hop 的 | 本 slug G2 前／owner;過期不得把「已自動 hop」當已核 |
| 「會沿用 agent-event 1.1」為假 → F2 另本;1.1 的 `stage` 形狀繼續只服務舊 7 | 中 | Stage 2 對帳:沿用 1.1 加槽 vs 平行帳本 | Stage 2／收斂者;本討論不鎖鍵名 |

## Evidence manifest
| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
|---|---|---|---|---|
| F0 鎖定面 | F2 刀界與 Runtime／Must-keep | notes/design/five-station-simplify-brief-v3.md、notes/design/five-station-simplify-f0-state-machine.md | 是(使用者點名) | 是 |
| F1 annex／牙 | 看 F1 已紅什麼、什麼交 F2 | notes/design/five-station-simplify-f1-*、scripts/five_station_f1.py、scripts/fixtures/five-station-simplify/ | 是(使用者點名) | 是 |
| 父 slug 延後表 | 證明 coordinator／計數／event 鍵名未做 | docs/dev/five-station-simplify/5-tasks.md、4-spec.md、6-implementation-notes.md、7-review.md | 是(本 tree;F1 已出貨) | 是 |
| 既有 event schema | 證明 hop／latch／cap 槽不存在 | observability/schema/agent-event.schema.json | 是(本 tree 源碼) | 是 |
| 手 hop 現場 | 證明 F1 之後仍靠 chat／graph 節點 | docs/dev/dogfood-ping/DOGFOOD-NOTES.md、skills/dev-flow/stage2/graph.yaml、docs/dev/STATUS.md | 是(本 tree) | 是 |
| 採用逐字稿 | 驗證「採用端也手 hop」 | 無;public repo 禁收公司路徑 | 禁 | 否 |

## Goals
- G-out-1:謂詞全真且 latch 未命中時,slug 前進到下一站,不必等人說「要不要繼續」。
- G-out-2:任一自動前進謂詞為假時,工作停在該站修;不得改問人來繞。
- G-out-3:每一次 hop、每一次 latch 開火／熄火、每一次 cap 加一或用盡,都留下事後可核對的機械紀錄。
- G-out-4:Must-keep 任一條未成立時,不得因「已經五站了」或「想 hop」而前進。省略後的勾選仍看得出是未完成。
- G-out-5:新機可與舊 7 並行;已有 1–7 md 的 slug 不被寫入五站狀態、不被折線。
- G-out-6:本討論只鎖定 hop／latch／cap 的**語意槽**(要能回答誰、從哪到哪、哪條謂詞、哪只 cap、是否 Escalated),不鎖定 JSON／YAML 鍵名。
- G-out-7:Ship 仍只有人寫 `verdict: PASS` 才能 Done;機械綠不得當 PASS。
- G-out-8:本 slug 自己的出貨路徑仍是舊 7 直到 Ship;不拿自己當新 5 的第一個白老鼠。

## Requested solution
- Coordinator 讀 brief §3 表 A／B 謂詞:全真 hop,一假停修;latch 列真才進 HumanWait。**未定案**長在哪支行程／hook／腳本。
- hop／latch／cap 留機械紀錄,語意槽對 G-out-3;鍵名沿用 OC-3 延後(與 F1 SLOT 同型)。**未定案**掛進 agent-event 1.1 或另本。
- 雙路徑:新機可在舊 7 旁邊跑;預設路線仍舊 7 直到 F3。Coordinator 不得折 in-flight。
- 本 hop 不選定 event 欄名、不寫 coordinator 碼、不切 `graph.yaml` 預設路。

## Non-Goals(初稿)
- 本 hop 不改 `_templates/`、`graph.yaml`、gate token、STATUS、HISTORY、契約版本。
- 本 hop 不送 G1;status 留 draft;不合併。
- 不刪 G1／G2／`ACCEPTED` 檔或 token。
- 不把 in-flight slug 折成五站。
- 不把新 slug 預設切五站(F3 cut)。
- 不放寬 hop≤2／Decide≤1／Goal reopen≤1。
- 不在本討論鎖定 event 欄位鍵名。
- 不重開 F0 十條;翻任何一條=新 brief。
- 不把「hop 比較快」解讀成「Must-keep 也可以 hop 掉」。

## Open Questions
- [x] Q1:lane 是否 full?→ 使用者:full
- [x] Q2:本 hop 是否只 Stage 1 調查、不改 STATUS、不合併、不送 G1?→ 使用者:是
- [x] Q3:F2 刀界?→ brief §7:做 coordinator 自動前進 + hop／latch／cap 紀錄 + 雙路徑;不做折 in-flight、刪 token、F3 預設切線
- [x] Q4:F1 是否已用活計數器咬 cap?→ 否。牙用正文正則咬對照稿;計數落點交 F2
- [x] Q5:本討論是否鎖定 event 鍵名?→ 否。OC-3 延後:語意槽,不是 JSON 必填鍵
- [~] Q6:F1 出貨後現場是否仍 chat-hop?(帶假設:是;風險=高;期限=本 slug G2 前看下一條母版 full lane)
- [>] Q7:event 落在哪份 schema／哪支腳本／哪根欄?→ 移交 Stage 2;本討論不解
- [>] Q8:coordinator 是行程、hook,還是腳本?→ 移交 Stage 2
- [x] Q9:Must-keep 未成立時可否 hop?→ 不可。少一條=違 brief,不是簡化成功
- [x] Q10:雙路徑是否等於 F3 cut?→ 否。F2 讓新機可與舊 7 並行;新 slug 預設五站是 F3
- [x] Q11:本 slug 自己走舊 7 還是等 F3?→ 本資料夾已有站檔 = in-flight,整段舊 7 直到 Ship
- [>] Q12:沿用 agent-event 1.1 加槽,還是平行帳本?→ 移交 Stage 2;1.1 的 `stage` 形狀目前只服務舊 7

## Constraints
- 本 PR 不宣稱 G1 PASS;不改 STATUS／HISTORY。
- 討論盲下游:本檔不指定行程／API／元件當目標。
- **Owner-locked:Must-keep 未綠不得 hop。**自動前進謂詞必須包含「完整度仍在」;不是 Requested solution 的未定案。
- **Owner-locked rewrite cap:**hop≤2／Decide≤1／Goal reopen≤1;用盡 Escalated;不准暗改。舊 7 不套。
- **Owner-locked OC-3 延後:**本 hop 不鎖 event／annex 欄位鍵名。語意槽(hop／latch／cap)要能被指出,鍵名後定。
- **雙路徑:**新機不得改舊 7 in-flight 的 hop;不得靠 bump 讓新 slug 預設五站。
- 詞條(語言,不是方案):**hop**=謂詞全真後離站。**latch**=表 A／B 必須等人的列。**cap**=三只只增計數。**語意槽**=要能回答的事實格,不是 JSON key。**紙上牙**=對照稿正文觸發的紅,不是活 runtime。**手 hop**=chat／手寫下一站檔。**假完成 hop**=Must-keep 未綠仍前進。**雙路徑**=新機與舊 7 並行。本 hop 不寫進長期記憶。

## 驗收雛形
- AC-1(G-out-1):假設一條五站 slug 已走完 Decide 且 A3／A4 謂詞全真、latch 未命中,當該評謂詞的角色跑完,則它已在 Spec,且沒有「請人審 A4／要不要繼續」紀錄。
  - 從哪看:該 slug 的前進紀錄(人可核對的 hop 或缺席)
  - 看到什麼算對:有 Decide→Spec 的 hop 紀錄;無「請 owner 看一下」
  - 拿什麼試:後續造的五站假 slug;本 hop 不跑 coordinator
- AC-2(G-out-2):假設同一 slug 的 Decision 仍空或仍有「待裁決」,當該角色跑完,則它仍停 Decide,且停因是謂詞假。
  - 從哪看:停點紀錄／拒絕理由
  - 看到什麼算對:理由是「Decision 空」或「OC 未決」,不是「先問 owner」
  - 拿什麼試:一份故意留「待裁決」的 2-decision 對照
- AC-3(G-out-3):假設發生一次 hop、一次 B1 latch 開火、一次 hop 重寫第 2 次,當人事後翻紀錄,則三件事各自可指出。
  - 從哪看:機械紀錄(檔或 log;不預填 JSON 鍵)
  - 看到什麼算對:能回答從哪到哪、哪條 latch、哪只 cap 現在幾次;缺一槽=未完成
  - 拿什麼試:後續造的三段軌跡;本討論不鎖欄名
- AC-4(G-out-4):假設 Build 有一個 T 缺 Verify,當有人要求 hop 進 Ship,則 hop 被拒;勾選不能冒充完成。
  - 從哪看:該 T 卡 + 被拒絕的 hop
  - 看到什麼算對:拒絕理由點名缺 Verify／Must-keep;沒有「已經五站了」當省略
  - 拿什麼試:現行 F1 `rp-01-missing-four-fields.md` 那型活 slug
- AC-5(G-out-5):假設某 slug 目錄已有 `1-discussion.md`,當新機被求對它做五站 hop,則拒絕且不寫五站狀態。
  - 從哪看:該目錄與被拒絕的 hop
  - 看到什麼算對:仍走舊 7;無五站狀態檔
  - 拿什麼試:本資料夾(一旦本檔存在即 in-flight)
- AC-6(G-out-6):假設本檔列出 hop／latch／cap 三個語意槽,當後站開始寫 schema,則可以改鍵名,但不能少槽。
  - 從哪看:後站 Decision／spec 對本檔 G-out-3 的去向
  - 看到什麼算對:三槽都有去向;沒有「Stage 1 已鎖 `event_type=hop_advanced`」這種鍵名
  - 拿什麼試:本檔 Constraints 的 OC-3 句
- AC-7(G-out-7):假設機械項全綠但 7-review 頂欄不是人寫的 `PASS`,當有人標 Done,則狀態仍停 Ship／HumanWait。
  - 從哪看:7-review 頂欄 + 狀態
  - 看到什麼算對:無人 PASS ≠ Done;Agent 寫 PASS=未寫
  - 拿什麼試:F1 `rp-08-done-without-pass.md` 那型
- AC-8(G-out-8):假設本 slug 走到自己的 G1／G2／G3,當有人想用五站自動前進跳過,則跳不過。
  - 從哪看:本目錄站檔與被要求的 hop
  - 看到什麼算對:仍有例行 G1／條件 S3／G2／G3;沒有五站自動前進寫入
  - 拿什麼試:本資料夾已存在 = in-flight

## 現況圖
誰:F1 牙
做什麼:對照稿變紅
工具:five_station_f1.py
痛點:只咬文字卡
↓
誰:owner／寫手
做什麼:口頭准下一站
工具:chat／PR
痛點:謂詞真也等人
↓
誰:無人
做什麼:不 hop 不記 event
工具:無 coordinator
痛點:cap 無活計數

## 邏輯圖(ASCII)
```
after F1
|-- paper tooth
|   |-- fixture says "3rd rewrite"  -> RED
|   |-- live hop                    -> unseen
|   +-- live cap tick               -> no counter
|-- hand hop
|   |-- chat "open next"
|   |-- write next md
|   +-- STATUS / HISTORY as log
+-- needed
    |-- pred true + latch no  -> hop   [G-out-1]
    |-- pred false            -> stay  [G-out-2]
    |-- must-keep red         -> no hop [G-out-4]
    |-- latch yes             -> wait human
    |-- cap exhaust           -> Escalated
    +-- record hop/latch/cap  [slots, not keys]
fail
|-- hop while must-keep red   -> fake-done faster
|-- stay while pred true      -> still wait
|-- hop Ship w/o human PASS   -> steal OC-3
|-- ask human latch=no        -> RP-14 live
+-- hop with no record        -> cannot audit
```

## Interview Log(推理鏈外顯)
- Q:F1 已經出貨,為什麼缺 coordinator 仍是現場痛,而不是「牙夠了」?
  - 事實:scripts/five_station_f1.py:L327-L333 docs/dev/five-station-simplify/5-tasks.md:L66-L72 docs/dev/five-station-simplify/6-implementation-notes.md:L187 docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9 skills/dev-flow/stage2/graph.yaml:L53-L57
  - 推理:F1 牙對「第 3 次重寫仍繼續」這句話紅,對活 hop 無動作。父 slug 自己把評表 A／B、計數器、event 延後到 F2。現場 hop 仍是 chat 准下一站 + 舊 graph 的 `N7-g1`。牙夠紅卡,不夠離站。
  - 結論:CONFIRMED A 線主痛=紙上牙 vs 活 hop。F1 G3 PASS 不消除這痛。
- ⚠️ Q:自動前進與 Must-keep 撞車時,哪一種失敗比較糟?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L13-L28 notes/design/five-station-simplify-brief-v3.md:L135-L158 notes/design/five-station-simplify-brief-v3.md:L127-L129 _templates/5-tasks.md:L50
  - 推理:三個失敗模式不對稱。(1)謂詞真、Must-keep 綠、latch 假,卻仍等人=F1 之後的現況,浪費停點。(2)Must-keep 紅仍 hop=比舊 7 更快假完成,brief 寫明少一條=違規。(3)Ship 機械綠就 Done=偷 OC-3。A 線把(2)當不可接受,(1)當本刀要消的痛,(3)當已鎖禁則。
  - 結論:CONFIRMED hop 不得跳過 Must-keep;Must-keep 綠且 latch 假時不得再問「要不要繼續」。
- Q:event 需要記下什麼,為什麼本討論不能鎖欄名?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L133 notes/design/five-station-simplify-f1-dual-read-annex.md:L1-L4 notes/design/five-station-simplify-f1-rp-min-set.md:L1-L4 observability/schema/agent-event.schema.json:L18 observability/schema/agent-event.schema.json:L81-L103 docs/dev/five-station-simplify/4-spec.md:L769
  - 推理:brief 鎖「要留」前進／latch／cap。F1 已用 OC-3 把鍵名延後;父 spec Q10 同樣延後。現有 1.1 沒有這三類事件,且 `stage` 形狀是舊 7。本討論若鎖 `event_type=hop_advanced` 就是偷做 annex。語意槽足夠:誰、從哪到哪、哪條謂詞真／假、哪只 cap、是否 Escalated。
  - 結論:CONFIRMED 三槽必留、鍵名 OPEN 交 Stage 2。沿用 1.1 或另本=Q12。
- Q:雙路徑跟「新 slug 預設五站」差在哪?
  - 事實:notes/design/five-station-simplify-brief-v3.md:L160-L167 notes/design/five-station-simplify-brief-v3.md:L171-L180 docs/dev/five-station-simplify/4-spec.md:L828-L832 scripts/five_station_f1.py:L226-L235
  - 推理:F2 要讓新機可跑,且舊 7 in-flight 不被折。F3 才改預設。本資料夾一旦有 md 自己就是 in-flight 樣本。雙路徑失敗=新機寫入舊 slug 的五站狀態(RP-15 活體),或 bump 契約讓未 upgrade 的採用端改線。
  - 結論:CONFIRMED F2=新機旁路;F3=切預設。本 slug 走舊 7(Q11)。
- ⚠️ Q:若 F2 只做 hop、不做 event,最極端會怎樣?(發散)
  - 事實:docs/dev/STATUS.md:L50 docs/dev/dogfood-ping/DOGFOOD-NOTES.md:L9 notes/design/five-station-simplify-f0-state-machine.md:L122-L139
  - 推理: hop 發生了但無法證明。STATUS 已經示範紀錄會過期(Backlog 仍指 F1)。cap 用盡可以口頭 reset 再 hop,F1 牙看不見活計數。最極端:Ship 審查者只能信「我們沒跳 Must-keep」。
  - 結論:CONFIRMED event 不是裝飾;沒有三槽紀錄=G-out-3 失敗,即使 hop 看起來很快。
- Q:latch=否卻問人,跟「謂詞假就停修」,現場會不會被混成同一句「先問 owner」?
  - 事實:notes/design/five-station-simplify-f0-state-machine.md:L163-L179 scripts/five_station_f1.py:L298-L300 scripts/fixtures/five-station-simplify/rp-14-please-review-latch-false.md:L1-L5
  - 推理:兩件事方向相反。謂詞假→停在該站修,對象是寫手,不是 owner 蓋章。latch 假→禁開審查 widget。現場口頭「先問一下」會把兩者糊成例行停。F1 只能紅寫進卡裡的那句;活 chat 仍自由。
  - 結論:CONFIRMED A 線要把「停修」與「問人」拆開;混用=RP-14 活體。
- ⚠️ Q:本 hop 有沒有把 F2 施工範圍寫進 Stage 1?(盲點)
  - 事實:notes/design/five-station-simplify-brief-v3.md:L171-L180 本 hop brief(只 Stage 1、不改 STATUS、獨立於 B／C)
  - 推理:刀界已鎖,但行程／schema／鍵名未鎖。隱含預設「現場仍手 hop」無 F1 之後第二條 live 軌,已標 Q6。隱含預設「會沿用 1.1」已標 Assumption 並移交 Q12。本檔不寫碼、不送 G1,避免跟 F0–F2「新軌仍舊 7」撞車。
  - 結論:CONFIRMED 本 PR 只落討論雙檔;不重開十條;不改 STATUS;不鎖鍵名。
- Q:STATUS Backlog 仍指 F1,這算證據還是噪音?
  - 事實:docs/dev/STATUS.md:L32 docs/dev/STATUS.md:L50 docs/dev/HISTORY.md:L659-L663
  - 推理:Active 已空、HISTORY 已記 F1 G3 PASS,Backlog A 仍寫「下一刀 F1」。這正好是「人記 hop、看板可過期」的活樣本,不是 F1 沒出貨。它支持「STATUS 不能當 hop／cap 正本」。
  - 結論:CONFIRMED 看板 lag 是 G-out-3 的現場動機,不是 F1 未完成的反證。
