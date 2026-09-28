---
title: jev-gate W0 source closure（P0-5～P0-9）
slug: jev-gate
status: W0 closed（probe + source 精讀完成;不開 P1-G1～G7、不寫 runtime）
date: 2026-09-22
base: research/jev-supermemory 6824fa6（roadmap draft-v4）
inputs: roadmap.md §1 P0 表、§15 剩餘 source 驗證;本檔 evidence/w0/ 下四支 probe 的實跑輸出
---

# W0 source closure

> **本檔只做 roadmap draft-v4 §15 列的 source/probe closure。**不改 `main`、不改 runtime、
> 不寫 `scripts/devflow-jev.py`(含 shadow)、不動 P1-G1～G7。所有 probe 都在暫存假 repo /
> 隔離 `AGENTMEM_HOME` 上跑,只讀本 repo 現有 hooks／memory 模組。
> 每個 P0 一段:**做了什麼／結論／證據路徑**。行號以 `6824fa6` 為準。
>
> 硬約束不重投(roadmap §0):J1→J3→J5 shadow;七組守衛 foundation 全綠前不准寫 runtime;
> 雙閘門 key + 每專案 opt-in;不接 supermemory;J2 保留排後;既有 G1/G2/G3／mechanical／
> human attestation 不得被繞過。本檔的結論只**收窄**後續設計空間,不新增 owner 決策。

## 證據索引

| 檔 | 內容 |
|---|---|
| `evidence/w0/probe-p0-5-run-lifecycle.sh` → `p0-5-run-lifecycle.json` | Stage6→Stage7／bare Stage7／re-arm／stop 的逐步 `exec.json` + `.devflow/runs/` 快照 |
| `evidence/w0/probe-p0-6-durable-events.py` → `p0-6-durable-events.json` | `append_events(kind=jev)` durable→rebuild→index→ask/context roundtrip;writer 邊界;三組 multiwriter |
| `evidence/w0/probe-p0-8-upgrade-manifest.sh` → `p0-8-upgrade-manifest.jsonl` | 假採用樹 + pack 副本多一列 manifest;問每條機械路徑誰看得到缺件(`rc` 為被測指令本身的 exit code;doctor 保留完整輸出) |
| `evidence/w0/probe-p0-9-devtalk-whitelist.sh` → `p0-9-devtalk-whitelist.jsonl` | hooks 掛載、graph action 詞彙、devtalk-guard／devflow-guard 對 1-discussion Read 的實際判定 |

重跑:`bash docs/dev/jev-gate/evidence/w0/probe-p0-5-run-lifecycle.sh .`(其餘同型;P0-6 用 `python3 … .`)。
輸出裡的 ULID／暫存路徑每次不同,結構與布林結論不變。

---

## P0-5 Stage 7 run lifecycle（Stage6→Stage7 / bare Stage7）

**做了什麼**:在假 repo 上跑真 `hooks/devflow-exec.sh` + `hooks/devflow-obs.sh`,依序
`status` → obs(未武裝)→ `start f1` → obs attempt → 同 slug 再 `start` → `review f1` →
obs review → `review bare`(異 slug)→ `review-unlock` → `stop` → obs(已 stop)→
bare `review bare` → obs → 再 `review bare` → unlock → stop → 再 `review bare` → stop;
每步 dump `exec.json` 的 `run_id/schema/phase/review_unlocked` 與 `.devflow/runs/` 檔案表。

**結論**(對應 `p0-5-run-lifecycle.json` 各 step):

1. **`run_id` 的生成點有三個,不是「只有 Stage 6 start」**:legacy sequential start
   (`_exec_impl.py:344`)、VNext feature-scope start(`:386`)、bare Stage 7 review 自建
   (`:1023`);task-scoped start 另在 `:428`。三條非 task 路徑都寫 `schema=exec-v4`。
   probe step 10／42 實證:`start f1` 與 bare `review bare` 各自拿到新 `run_id`。
2. **Stage6→Stage7 同一 run**:`review <slug>` 在 `exec.json` 已存在時只加
   `phase=review, review_unlocked=false`,`run_id` 不變(`:981-994`;step 20 `same_run_stage6_to_7=true`)。
   obs 事件因此落在同一個 `.devflow/runs/<run_id>/`(step 21 的 `reviews/rev_…/events.jsonl`
   與 step 13 的 `attempts/att_…` 同目錄)。
3. **同 slug 再 `start` 是允許的 re-arm,會換 `run_id`**(`:277` 明文「同 slug 同 task re-arm:
   允許」;step 12 `restart_regenerates_run_id=true`)。既有 attempt 事件留在舊 run 目錄,
   新事件寫到新目錄(step 13 出現兩個 run 目錄)。→ **一個 feature 在 Stage 6 期間可以對應多個
   `run_id`**;J5 pairing 不得把 `run_id` 當 feature 級 identity。
4. **bare Stage 7**(無 Stage 6 state):每次 `stop` 後再 `review` 都是新 `run_id`(step 42→51,
   `bare_new_run_per_arm=true`);同 slug 未 stop 再 `review` 走「沿用」分支、`run_id` 不變(step 44,
   訊息仍印「沿用既有 Stage 6 exec.json」——文案誤導,實際沒有 Stage 6)。bare 武裝 `scope=[]`、
   baseline 收全部髒檔(`:1002-1013`),不要求 4-spec approved(`:996-1001` 註解)。
5. **`exec.json` 是 obs 事件的唯一 run 綁定**:`_obs_impl.read_state()`(`:175-195`)沒有旗標、
   沒 `run_id`、或格式非 `run_<ULID>` 一律 die;step 02／31 實證未武裝與 `stop` 之後都 exit 1,
   事件不落盤。**`stop` 不清 `.devflow/runs/`**(step 30 後 runs 檔仍在),但之後沒有任何合法
   寫入口,直到下一次武裝產生新 run。
6. **`_templates/7-review.md:62` 的「建議跑 review 武裝」在 runtime 是選配**:沒有任何 hook 在
   Stage 7 強制 `review <slug>` 存在。沒武裝 = 沒 `run_id` = 沒有 obs 事件可綁。→ J5 若要「可觀測」
   只能在**有武裝**的 Ship case 上成立;沒武裝的 case 只能靠 evidence/artifact hash 配對。
7. 三條拒絕路徑由 probe 實證、**但既有 selftest 沒有覆蓋**:異 slug `review` 拒(step 22;
   `_exec_impl.py:987-989`)、slug 目錄不存在拒(step 41;`:1002-1003`)、無 `exec.json` 的
   `review-unlock` 拒(step 40;`:1117-1118`)。`hooks/selftest.sh:401-451` 只測沿用分支的圍欄③
   (讀 6-notes 擋／7-review*、evidence/ 放行／unlock),`:2558-2588` s7c 只測 bare 武裝成功後的
   派工分層;三條拒絕在 selftest 零案例。這是 P1 期可補的 selftest 缺口,不是 Jev 的事。
   **2026-09-23 補記(owner 裁 C3,盡快 P1 L1)**:三案已釘進 `hooks/selftest.sh:2573-2580` s7c 段
   (無 `exec.json` 的 `review-unlock`／不存在 slug 的 `review`／武裝中對異 slug `review`,各期望 exit 1),
   `MIN_CASES` 459→462,`scripts/test-architecture-guards.sh` 靜態釘同步;本容器實跑 451/462,11 紅與
   乾淨 6824fa6 worktree 完全同集(9 條 doctor 因 printer-python 3.11、2 條 f4 唯讀因 root),新三案全綠。
8. schema fail-closed 對照(step 14):`agent_role=implementer`、`prompt.version=1` 的 attempt 事件被
   `validate_or_die` 拒(exit 1、不落盤),錯誤訊息逐欄列 enum／pattern
   (`observability/schema/agent-event.schema.json` 的 `fields.agent_role`、`prompt_object.fields.version`)。

**對 J5 run_id／observability 的可用性判定**:

- `run_id` 可用作 **evaluation 的 provenance 欄位**(記錄「這次 J5 shadow 是在哪個武裝期算的」),
  **不可**用作 case identity、不可用作 dedupe key、不可假設 Stage 6 與 Stage 7 一定同 run、
  不可假設一個 feature 只有一個 run。P1-F4 的 pairing key 維持 roadmap 寫法
  `feature + gate + artifact_hash + evidence_hash + HEAD + timestamps`,`run_id` 只作附註。
- observability 對 J5 是「有武裝才有」的 best-effort 通道;J5 shadow enqueue 不得依賴它。
  roadmap §6 P4 表「J1–J3 observability 強耦合」維持「先不把它當必要條件」。
- 文案修正建議(不在 W0 做):`_exec_impl.py:994` 的「沿用既有 Stage 6 exec.json」在 bare
  re-arm 時應改為「沿用既有 exec.json(phase=review)」。這是 P1 以後的 L1 小修,與 Jev 無關。

**證據路徑**:`docs/dev/jev-gate/evidence/w0/p0-5-run-lifecycle.json`(step 00–52 + `99-run-id-summary`);
source:`hooks/_exec_impl.py:223-277, 341-359, 382-400, 428-455, 460-481, 957-1052, 1110-1133`;
`hooks/_obs_impl.py:175-214, 403-440`;`hooks/devflow-lib.py:481-487`;`hooks/_dispatch_impl.py:55-80`。

---

## P0-6 `append_events(kind=jev)` full sync／index／multiwriter

**做了什麼**:隔離 `AGENTMEM_HOME` + 假 git repo,`dev-memory.py setup --no-embeddings` 建
identity;直接呼叫 `durable.append_events()` 寫 `kind=jev` 事件(含自訂 `jev{}` dict、
`source_type=jev`、`source_ref=J5:<feature>`),一筆合法 `evt_<ULID>`、一筆自訂字串 id;
測冪等／同 id 異內容／writer 邊界(title/body 絕對路徑、secret、藏在自訂欄位);
用 `dev-memory.py status` 觸發 `ensure_durable_mirror → rebuild_local`,直接開 SQLite 讀
`events` 表與 `items` 索引;`ask`／`context`;`durable-check`;三組 multiwriter
(同檔 race、同檔決定性交錯、異檔)。

**結論**(對應 `p0-6-durable-events.json` steps):

1. **durable 檔面:自訂欄位完整保存**(step 15 `custom_preserved_in_file=true`)。
   `append_events` 只剔 `None` 值、掃 `title/body`、驗 `paths`、要求 `event_id`(`durable.py:755-764`),
   其餘 key 原樣落 JSONL。冪等(step 11 寫入 0 檔)與同 id 異內容拒收(step 12)與 draft-v4 記錄一致。
2. **sync/index 面:自訂欄位被丟棄,只剩 canonical 欄位**。`sync.py:198-211` 把 durable event
   映射到 `store.add_event()` 的固定參數(kind/title/body/occurred_at/branch/commit_sha/session_id/
   signal/paths/source_type/source_ref/durable_ref/event_id);SQLite `events` 表沒有任何 JSON
   payload 欄(step 20 `events_cols` 共 17 欄,`custom_column_exists=false`)。索引文字只有
   `kind + title + body`(`store.py:283-286`)。→ **`jev{route,confidence,evidence_hash,…}` 在 local
   mirror 端不可查、不可過濾。**
3. **`event_id` 必須是合法 `evt_<ULID>`,否則 local 端每次 rebuild 換新 id**。`sync.py:210-212`
   對非法 id 傳 `None` → `store.add_event()`(`store.py:257`)隨機生一個(step 21:自訂字串 id 那筆兩次 rebuild
   得到不同 `evt_…`,而合法 id 那筆穩定)。durable 檔本身仍以原字串去重,但 local↔durable 對不上號。
   → Jev evaluation 若要 durable/local 可互相引用,**`event_id` 必須用 `ids.new_id("event")` 產生**;
   `evaluation_id`／`questionset_hash` 等放別的欄位,不得塞進 `event_id`。
4. **read 面可達**:`ask "之前 J5 shadow evaluation 改過什麼"` → `query_kind=HISTORY`、
   `retrieval_status=OK`、兩筆 event hit(step 30);`context --json` 的 recent events 節列出
   `jev:J5 shadow evaluation …`(step 31)。→ `kind=jev` 會**混進一般 HISTORY 檢索與 context 預載**。
   這是雙面刃:可查,但 shadow 期間的評估雜訊會出現在 `context` 預載與 `ask` HISTORY 檢索
   (dev-talk `talk start` 的 brief 不讀 events —— `devtalk.py:115-124` 回傳 topic/known_knowledge/known_facts/
   repo_signals/candidate_entities/conflicts/open_questions,全部來自 knowledge/facts/conflicts 與 repo 檔案掃描
   (`repo_signals`:`:111,136`),沒有任何欄位讀 `store.events()`)。→ P1-G4 要為 `kind=jev` 的 `title`
   定固定前綴,讓 HISTORY/context 裡一眼認得出是 shadow 評估;durable 仍是 owner decision 5 的
   ID/hash 正本,不因此改走「只進 local」。
5. **writer 邊界只掃 `title/body`**:絕對路徑與 secret 在 body 會被拒(step 13),**藏在自訂 `jev{}`
   dict 內不會**(step 14 `rejected=false`)。`_assert_portable_content` docstring(`durable.py:76-97`)
   明寫結構化 ref 欄位由 `consolidate` 的 `signal.gate(extra_texts=json.dumps(payload))` 涵蓋——
   但**直接呼叫 `append_events()` 走不到 `consolidate`**。→ J5 若直接 `append_events`,
   P1-G4 必須自己呼叫 `signal.gate(<kind>, title, body, extra_texts=[json.dumps(record)])`
   (`signal.py:205`;第一個位置參數是 **kind**,不是文字),不能只靠 writer。
   **kind 有硬約束**:`classify()` 對不在 `HIGH_SIGNAL_KINDS` 的 kind 一律回 LOW
   (`signal.py:196-202`,註解明寫「要 durable 就得先把種類納入 HIGH_SIGNAL_KINDS,那是一次
   要被 review 的改動」),`gate()` 於 `:220-222` 記一條「低訊號」reason,`:233` 據此 `durable_allowed=False`;`jev` 不在
   `HIGH_SIGNAL_KINDS`(`:28-47`)。writer 之所以放行 probe 的 `kind=jev`,只因它寫死
   `signal.gate("domain_clarification", extra_texts=texts)`(`durable.py:95`),與 record 的 kind 無關。
   → P1-G4 二選一:借一個既有 HIGH kind 當 gate 的 kind 參數(record 的 `kind` 仍寫 `jev`),
   或把 `jev` 加進 `HIGH_SIGNAL_KINDS`(memory 模組的 reviewed 變更,L2)。writer 邊界呼叫點見 `durable.py:95`。
6. **multiwriter:同一 session 檔沒有檔級互斥,read-modify-replace 視窗會 lost update**。
   step 50(40+40 筆真併發)偶然 0 lost,但 step 51 決定性交錯(A 讀完舊快照後等 B 寫完再取代)
   **5/10 lost,全部是 B 的**;source 無 `fcntl/flock`(step 60)。異 session 檔(step 52)0 lost。
   → **多 writer 安全的唯一條件是「每個 writer 自己的 `session_id`」**(= 各自的 JSONL 檔;
   `durable.py:681-692` 註解本來就是這個設計)。J5 worker、consolidate、人工 `remember` 不得共用
   session key。
7. **`durable-check` 會把未 commit 的 `.dev-flow/events/*.jsonl` 判 `DURABLE_UNCOMMITTED` FAIL**
   (step 40)。→ J5 shadow 每次寫 durable 都會把專案推進「記憶未 commit」狀態;shadow 期間高頻
   寫入會讓 `durable-check` 常紅,這是選 durable 通道的實際成本。

**對 owner decision 5(「優先沿用 `append_events()`」)的判定**:**可沿用,但有四條硬邊界**,
不構成「不適合」、不觸發備選 raw ledger namespace:

| 邊界 | 落到哪個 P1 |
|---|---|
| durable event 只放 canonical 欄位能表達的東西:`title/body/paths/source_type/source_ref`;結構化指標(route/confidence/hash)**要嘛編進 `body` 的固定文字格式,要嘛接受「durable 有、local 不可查」** | P1-G4 資料模型:建議 `body` 用 `key=value;…` 單行 canonical 字串,hash 進 `source_ref`,`jev{}` dict 仍寫(檔面保存)但不當查詢依據 |
| `event_id` 一律 `ids.new_id("event")`;evaluation identity 另欄 | P1-G4 |
| 每個 J5 writer 獨立 `session_id`(建議 `jev-<gate>-<run_id 或 evaluation_id>`) | P1-G4／P1-F4 |
| 直接 `append_events` 前自己過 `signal.gate(<HIGH kind>, title, body, extra_texts=[json.dumps(record)])`;`kind=jev` 本身會被 `classify()` 判 LOW → 要嘛借既有 HIGH kind 當參數,要嘛把 `jev` 加進 `HIGH_SIGNAL_KINDS`(reviewed 變更) | P1-G4 privacy tests(+ 若加 kind:memory 模組 L2) |

若 P1-G4 評估後認為「local 不可查」不可接受,備選是**擴 `sync.py` 映射 + `events` 表加一欄**
(方法論 repo 的 L2 變更),不是另開 raw ledger。

**證據路徑**:`docs/dev/jev-gate/evidence/w0/p0-6-durable-events.json`;source:
`memory/agentmem/durable.py:76-97, 681-692, 700-789`;`memory/agentmem/sync.py:198-212, 308-336, 441-450, 716-757`;
`memory/agentmem/store.py:251-287`;`memory/agentmem/ids.py:21-36, 75-79`;`memory/agentmem/signal.py:28-47, 196-225`;`memory/agentmem/devtalk.py:84-136`。

---

## P0-7 對 jev-gate 有關 source 的精讀結論

每支一段「對 jev-gate 的限制」。

### `hooks/_exec_impl.py`(1136 行)
- run 生命週期見 P0-5。額外限制:`exec.json` 有 shadow hash(`devflow-lib.py:195-226`),
  **任何 CLI 之外的寫入都會被 postbash(`_postbash_impl.py:52`)與 exec CLI 各子命令
  (`_exec_impl.py:532/552/982/1119`)的 hash 比對抓成 fail-closed**;guard/prebash 則用路徑規則
  直接拒寫 `.devflow/`(`devflow-lib.py:406-411`、`_prebash_impl.py:636-648`),不看 hash。→ Jev runtime 絕不可寫 `.devflow/exec.json`
  或其它 `.devflow/` 檔(obs 事件走 `devflow-obs.sh`;J5 自己的 local replay store 不得放 `.devflow/`
  之外的 repo 內路徑,`_obs_impl.runs_root():198-214` 對 `DEVFLOW_RUNS_ROOT` 也是這條規則)。
- `stop`(`:460-481`)刪 `exec.json`+sentinel+未消耗 tier-exempt;不動 `runs/`。
- Stage 7 bare 武裝不驗 4-spec approved(`:997-999`)。J5 packet 若想拿「spec approved」當 header 事實,
  要自己讀 `4-spec.md` frontmatter,不能從武裝狀態推。

### `hooks/devflow-lib.py`(1086 行)
- `UPSTREAM=("1-discussion","2-decision","3-prototype")`、`CONTRACT=UPSTREAM+("4-spec",)`(`:15-16`);
  `is_contract_path()`(`:264`)是圍欄②的判準,**任何 slug**。→ J1 在 dev-talk 端跑,不受此限;
  J3/J5 若在武裝期間執行,packet builder **讀不到 1/2/3 檔**(guard 擋 Read、prebash 擋 shell),
  只能用 4-spec/5-tasks/7-review/evidence;**review phase 未 `review-unlock` 前連本 slug 的 6-notes
  也被圍欄③擋**(`_guard_impl.py:128-133`),unlock 後才加回。這與 roadmap「J5 header 機械事實」一致,
  但要明寫:**J5 packet 不得含上游討論原文**,不只是 privacy 理由,是 runtime 本來就擋。
- `write_scope_verdict()`(`:390`)是三主機共用的寫入判定(`scripts/check-write-scope.sh` 檔頭);
  Jev 產生的任何檔(report/replay)寫在 `docs/dev/<slug>/` 下時要落在 review 期允許的
  `7-review*`／`evidence/` 前綴(白名單正本 `devflow-lib.py:417-419` 的 `write_scope_verdict`,
  guard 呼叫點 `_guard_impl.py:141-143`,偵測網對稱放行 `_postbash_impl.py:124-125`),
  否則被當 scope 外。→ J5 report 的 durable 落點若在 feature 目錄,只能是 `evidence/`。
- `new_run_id()`(`:481-487`)與 memory 的 `ids.new_id()` 是兩套獨立 ULID(`memory/agentmem/ids.py:1-15`
  明寫不共用);J5 evaluation 若同時要 run 鏈與 memory 鏈的 id,要各取各的,不得互填。

### `hooks/_obs_impl.py`(748 行)
- 事件 schema `devflow-agent-event/1.1`;`attempt_started` 必填 `attempt_id(att_ULID)/agent_role
  ∈{worker,reviewer,adviser,verifier}/model/prompt{id,version x.y.z,hash sha256}/base_sha`;
  `review_started` 必填 `review_id(rev_ULID)`(`observability/schema/agent-event.schema.json`)。
  probe step 14 刻意送錯 role／version,被 schema 機械拒收(見 P0-5 結論 8);schema 正本是
  `observability/schema/agent-event.schema.json`(`fields`／`prompt_object`／`events` 三節)。
- 沒有 `jev`／`evaluation` 事件型別;`hook-event` 通道禁 `agent_role/model/prompt`(檔頭)。
  → J5 若要進 obs,只能借 `review_started/review_completed`(agent_role=adviser?)或
  `mechanical_gate_completed(gate=…)`;**新增事件型別是 schema 1.x→ L2 變更**,W0 不做、
  roadmap 也未列。建議 J5 shadow 期不進 obs,只在 P1-F4 用 `mechanical_gate_completed` 記
  「J5 evaluation enqueued/skipped」這種不含分數的狀態事件(schema 已有 `gate/result/violation`)。
- 180 天 raw retention;`retention prune` 僅手動、禁背景自動刪除(檔頭 `:25-26`);`archive` 同屬 OC-5 但檔頭未加手動限制(`:24`)。J5 replay 若寄生 runs/,
  同受此政策;local replay store 另立目錄反而比較乾淨。

### `memory/agentmem/sync.py`(1090 行)
- 見 P0-6 結論 2/3/6/7。另:`consolidate()`(`:441`)是 durable 的**唯一設計寫入時機**,候選必須掛
  OPEN session(`:471-484`);直接 `append_events` 繞過這層是「內部 API」路徑,docstring
  (`durable.py:76-97`)接受這種呼叫但要求 writer 自守。→ P1-G4 二選一要明寫:
  (a) J5 走 `talk/session propose → confirm → consolidate` 正規路(有 session、有 gate、有候選狀態),
  或 (b) 直接 `append_events` + 自帶 `signal.gate`。(a) 較合 memory 架構,但每次 J5 都要開 session。
- `ensure_durable_mirror()`(`:308-336`)以整棵 `.dev-flow/` 指紋決定重建;J5 每寫一筆 durable
  就會讓下一次任何 `ask/context` 觸發 full rebuild(step 20/21 都 rebuild)。高頻 shadow 寫入 =
  高頻 rebuild;這是選 durable 的效能成本(小專案可忽略,但要知道)。

### `memory/agentmem/durable.py`(837 行)
- 見 P0-6。補:`_atomic_write`(`:208`)只保證單 writer 原子取代;`event_file()`(`:681`)
  按 `session_id + 月份`分檔。**跨月**:同 session 在月底/月初寫兩筆會落兩檔,去重範圍是**單檔**
  (`_existing_events` 只讀同檔),同 `event_id` 跨月不會被抓。→ J5 的 `occurred_at` 必須用
  evaluation 時間且一筆一 id,不得「同一 evaluation 補寫不同 occurred_at」。

### `notes/design/gate-verdict-write.md` + `scripts/check-gate-verdict-write.sh`
- 鎖死 1-5:Human verdict 正本 = md 頂欄 `verdict:`,只有「提交判定」才寫,全勾不算 PASS,
  feature agent 不得手改 review/decision/spec 檔記錄 verdict(`:9-22`)。牙:`check-gate-verdict-write.sh`
  釘句子 + 實測 serve POST。→ **J3 recommendation／J5 shadow 都不得寫 `verdict:`、不得寫 sidecar
  `*.verdict.json`**(那也是 human 判定的副本);J5 report 只能是獨立檔(`evidence/` 或 replay store)。
  roadmap「J3 不得寫 G2 verdict」有機械牙可依,不必新增。

### file/write-scope 檢查(`scripts/check-write-scope.sh` + `devflow-lib.write_scope_verdict`)
- Bash 寫入 prevent-before:未武裝 allow、武裝且 scope 外 deny、契約缺 exit 2(檔頭)。
  三主機共用同一判定,不准為別的主機放鬆。→ Jev runtime 寫檔一律先過 `--action`;
  Cursor/Codex 主機沒有 PreToolUse 時這是唯一牙。P1-F1 的 `report/replay` 寫入要在 selftest
  裡加 `check-write-scope --action` 案例。

### `skills/dev-setup/SKILL.md` 升級段落(`:265-345`)+ `scripts/check-dev-setup-discipline.sh`
- 見 P0-8。補:discipline checker 只驗 SKILL.md **有沒有講**十四條紀律(needle 比對,
  `MIN_CHECKS=38`),不驗採用專案(`:1-30` 檔頭自述「零機械檢查」的補丁)。→ 新增 manifest 列
  不會讓它紅;要讓「散發 devflow-jev.py」有牙,得靠 `check-ship-manifest.sh`(母版側)
  + 採用專案側的 doctor 擴充(P0-8 結論)。

### guide parity 區塊(`guides/guide-dev-flow.html`)
- 14 個 `<!-- parity:start … -->` 錨:`readme-stage6-seam-quickstart:484`、
  `readme-reviewer-selection-quickstart:535`、`readme-gate-model-quickstart:673`、
  `readme-stage-table:781`、`template2-checklist:935`、`template3-checklist:1022`、
  `template4-laws:1082`、`template4-checklist:1118`、`template5-checklist:1230`、
  `template6-checklist:1322`、`template6-rules:1495`、`template7-checklist:1702`、
  `template7-exit-quickstart:1870`、`readme-reviewer-selection-flow:1929`。
- 牙:`scripts/check-methodology-corrections.sh:91`(`marker_fragment`)、`:250-267`
  (readme-stage-table 對契約檔 §3 逐列比 檔名+Gate;用途欄不比)。
- 限制:**任何把 Jev 寫進 gate 條件、審查者順序、模板執行清單的改動都會同時打到
  契約檔 §3/§7、SKILL.md 階段表、三份模板頂註、guide parity 區塊**(`hooks/gate-consistency.sh`
  也在抽 token)。→ roadmap P3-2(`roadmap.md:279`)的清單**至少包含**這 14 個錨 + 契約檔 §3/§7
  + `gate-consistency` token 表;roadmap 另列的 reviewer-selection 5 處、`_gate_consistency_impl.py`
  ordered tuple、`gate-verdict-write.md` 契約族 10 檔與 `check-gate-verdict-write.sh` 照舊,本節不收窄它。
  W6 之前 Jev 不得出現在任何 parity 區塊內。P0-7 到此把
  「guide parity 區塊列出實際 section/line」的完成條件關掉。

**證據路徑**:本節即結論;行號可用 `grep -n` 對 `6824fa6` 復核。無需 probe。

---

## P0-8 dev-setup upgrade 對 ship-manifest 新增列

**做了什麼**:依 install 步 0/8 語意用目前 `ship-manifest.json`(9 列)種一棵「已安裝」採用樹
(tools/ 7 支 + `.devflow-baseline/` 快照 + `_templates/`),commit;複製整個 pack 到暫存,
往副本的 manifest 加第 10 列 `scripts/devflow-jev.py → docs/dev/tools/devflow-jev.py 755`
(source 是 3 行 placeholder,**不是 runtime**);然後逐一問機械路徑。

**結論**(對應 `p0-8-upgrade-manifest.jsonl`):

1. **採用樹沒有 manifest 副本、契約沒有 manifest 版本欄**(step 01
   `adopted_tree_has_manifest_copy=false`、`contract_has_ship_manifest_version=false`;
   `devflow-contract.json` 沒有任何 ship-manifest／manifest 版本欄,唯一 manifest 字樣是
   `schema_versions.context_manifest`)。
   → 採用專案側**沒有任何本地資料**能告訴它「上游多了一列」。
2. **母版側牙會紅**:`check-ship-manifest.sh` 對 pack 副本 exit 1,報 `副本不存在:docs/dev/tools/devflow-jev.py`
   與 `檔案地圖缺散發面:devflow-jev.py`(step 11 `rc=1`);補了 pack 內 tools/ 副本後仍剩檔案地圖那條(step 12 `rc=1`)。
   `--validate` 只看結構,綠(step 10)。→ 新增列在**方法論 repo** 有雙牙(parity + 檔案地圖),
   這是 W2 P1-F1「ship-manifest 分發」(`roadmap.md:123`)的既有依靠。
3. **採用專案側全部看不到**:`doctor` 的檢查項是 contract-version／capabilities／schema／exec-state／
   wave_review／gauntlet(+root)／history-append-root／printer-python／gate-consistency／prompt-registry／
   host-install(+ `schema:unknown-keys` info;step 20 完整輸出;`_doctor_impl.py`),**沒有任何一項讀 `ship-manifest.json` 或逐列驗 tools/**
   (`grep -n manifest hooks/_doctor_impl.py` 只命中 `context_manifest`)。step 20 的 `⛔ INCOMPATIBLE`
   (`rc=1`)**唯一**來源是 `printer-python`(本容器 `/usr/bin/python3` 是 3.11,低於 `PRINTER_PY_FLOOR` 3.12,`_doctor_impl.py:385-390` 只看版本就紅;step 20b 只有這一條 ✗),
   與 manifest 新列無關;
   `devflow-upgrade-leftovers.sh` 只管 `_templates/` 退役檔,`leftover: none`(step 21;檔頭「准刪」清單);
   `check-dev-setup-discipline.sh` 只驗 SKILL.md needle,綠(step 22)。
4. **upgrade 散文會覆蓋新列,但沒有「新增」的分類**:SKILL.md `## upgrade` 首條寫「只覆蓋
   … ship-manifest.json 每一列的 destination」(`:265-274`),agent 逐列 cp 時新列自然會被建出;
   三方比對判別法只定義「本地現況 ≠ 上游舊 blob ⇒ 客製」,對「本地缺、baseline 缺」沒有明文
   (step 30 我把它歸①,是我的推論,不是 SKILL.md 的原文)。→ 若 agent 照 upgrade 段首條的
   「先 diff 摘要給使用者過目」(`:274-275`)只列既有檔,**新列可能不出現在摘要裡就被建立**,
   或反過來被漏掉——兩種都沒有牙。
5. **check 第 13 項**(`:460-470`)是採用專案內唯一會逐列**驗證** destination 存在／mode／diff 的動作
   (install 步 0 `:104-110` 與 upgrade 首條 `:265-268` 的逐列 cp 只散發、不驗缺件),但它是 agent
   執行的散文,且只在「在專案內跑 check」時發生。

**判定**:**不會自動同步。**既有採用專案要拿到 `devflow-jev.py`／題組／schema,依賴 (a) 有人在該專案
跑 `dev-setup upgrade` 且 agent 忠實逐列 cp,(b) 之後跑 check 第 13 項才會發現漏。roadmap P0-8 的
「若不會自動同步,W2 必須增加 manifest-version 檢查或明列人工 upgrade」→ **兩者都要**:

- W2/P1-F1(roadmap §1 W2 列同時點名 P0-8 落地;該列的 P1-F6 是對抗 fixtures 隨 `test-devflow-jev.sh` 落地,屬 W2 但不是分發;分發只屬 P1-F1。2026-09-23 owner 裁 C4:行號筆誤已在本分支改為 `981-994`):`devflow-contract.json` 加 `ship_manifest_version`(或 manifest 加 `version` 並由
  doctor 讀採用樹 `docs/dev/devflow-contract.json` 比對),doctor 新增一項「manifest 逐列存在性」;
  這是 L2(契約 + doctor),不在 W0 做。
- 在那之前,P1-F1 的 `devflow-jev.py` **未散發到採用專案 = 該專案零出境**(雙閘門之外的第三道
  自然 fail-safe),文件要明寫「既有專案需手動 upgrade」。
- SKILL.md upgrade 段建議補一句「manifest 新列(本地缺、baseline 缺)= ①母版新增,直接散發並列摘要」
  並在 `check-dev-setup-discipline.sh` 加 needle。L1,可與 P1-F1 的分發同批。

**證據路徑**:`docs/dev/jev-gate/evidence/w0/p0-8-upgrade-manifest.jsonl`;source:
`skills/dev-setup/SKILL.md:104-110, 251-263, 265-274, 460-470`;`scripts/check-ship-manifest.sh:1-30`;
`scripts/devflow_ship_manifest.py:1-40`;`scripts/devflow-upgrade-leftovers.sh:1-30`;
`hooks/_doctor_impl.py:273-361`;`devflow-contract.json`;`scripts/check-dev-setup-discipline.sh:1-30, 177-195`。

---

## P0-9 dev-talk 讀取白名單對舊 `1-discussion.md` 路徑

**做了什麼**:讀白名單原文與所有節點的「讀什麼」;查 `hooks.json` 掛載;抽 `graph.yaml` 的
action 詞彙;直接餵 `devtalk-guard.sh`／`devflow-guard.sh`／`devflow-prebash.sh` 一個
Read 舊 slug `1-discussion.md`,分別在「talk 游標在、未武裝」「無游標」「dev-flow 武裝中」三態。

**一句結論**:**不算。**白名單三種(長期記憶入口、`docs/specs/`、原始碼)+「使用者主動指名的檔案」
(`skills/dev-talk/SKILL.md:17-19`);`docs/dev/<slug>/` 是文件類資料夾,S1 明寫
「不讀其他 `docs/dev/<slug>/`」(`nodes/S1-survey.md:13`);路由層(`skills/dev-flow/SKILL.md:48`
Intake 列)只「請他改跑 `/dev-talk`」,**不傳路徑**;N1 規定「下一次 /dev-talk 一律新 session,
絕不接上一場」(`nodes/N1-start.md:8`、`SKILL.md:64`)。唯一能讀既有 `1-discussion.md` 的節點是
**同 slug 重談**:S1 步 4「同 slug 另開 dev-talk、覆寫 `1-discussion.md` 時 … 必須逐條重讀出處」
(`S1-survey.md:34-36`)與 S8「可改已有的 `1-discussion.md`」(`S8-review.md:15`)——那是
「本 slug 的產出物」,不是白名單放行「舊路徑」。

**機械面**(對應 `p0-9-devtalk-whitelist.jsonl`):

1. `devtalk-guard.sh` 掛在 **PostToolUse `Edit|Write`**(`hooks/hooks.json:49-60`),它的 Read 分支
   (`devtalk-guard.sh:12-90`,擋 2–7 方案檔、放 Evidence manifest 核准=是)在 Claude hooks.json
   下**不會被 Read 事件觸發**(step 10)。直接餵也證明:游標在時 Read 舊 `1-discussion` **靜默放行**
   (step 20,exit 0;對照 `2-decision` exit 2,step 21)。→ 讀取白名單對 1-discussion **零機械執行**。
2. `graph.yaml` action 詞彙只有 `talk_*`／`write_*`(step 11,`any_read_action=false`);
   `check-devtalk-graph.sh --action` 管不到讀。
3. dev-flow **武裝中**任何 slug 的 `1-discussion` Read／shell 讀都被圍欄②擋(step 30/31;
   `_guard_impl.py:135-138`、`_prebash_impl.py:648-652`)——但那是 Stage 6/7 的事,dev-talk 期間不武裝。

**對 J1 的後果**(roadmap P0-9 完成條件「若不算,J1 ASK_MORE 每輪文件必須明說會從 S0–S2 重新盤查」):

- **成立。**J1 ASK_MORE 第二輪 = 新 `/dev-talk` session(N1 鐵則),S0→S1→S2 重跑;既有
  `1-discussion.md` 只在同 slug 重談時經 S1 步 4 逐條重驗出處後可沿用,不是自動 context。
  P1-F2 的 ASK_MORE 文件要寫這句,且 J1 packet 的 `quoted_context` **不得夾帶上一輪 1-discussion 原文
  當「已核事實」**——它只能是 S1 待重驗的 Log 材料。
- J1 不得建議 agent「直接讀舊 1-discussion 省一輪」;那等於用 Jev 繞白名單。
- 讀取白名單目前是純散文;若 J1 落地後發現 agent 因 ASK_MORE 而偷讀 `docs/dev/*`,補牙的位置是
  `devtalk-guard` 的 Read 分支 + `hooks.json` matcher 加 `Read`(L1,主機相容性要另驗;
  Cursor/Codex 無 PostToolUse Read)。W0 不改。

**證據路徑**:`docs/dev/jev-gate/evidence/w0/p0-9-devtalk-whitelist.jsonl`;source:
`skills/dev-talk/SKILL.md:17-21, 64, 92-96`;`skills/dev-talk/nodes/{N1-start.md:8-9, S0-scope.md:10-11,
S1-survey.md:13, 34-36, S8-review.md:15, N9-write-md.md:11}`;`skills/dev-flow/SKILL.md:48, 57-62`;
`hooks/hooks.json:49-60`;`hooks/devtalk-guard.sh:12-97`;`hooks/_guard_impl.py:126-138`;
`hooks/_prebash_impl.py:648-652`;`hooks/devflow-lib.py:15-16, 264`。

---

## W0 完成定義對帳（roadmap §9）

| W0 完成條件 | 狀態 |
|---|---|
| P0-5 lifecycle 有 probe 結論 | ✅ 三個 run_id 生成點;Stage6→7 同 run;re-arm/bare 每次新 run;obs 只在武裝期 |
| P0-6 fullroundtrip/index/multiwriter 有 probe 結論 | ✅ 檔面保存、index 丟自訂欄、非法 id 每次重生、read 可達、同檔多 writer 會 lost update、異檔安全 |
| P0-8 upgrade 有實測結論 | ✅ 不自動同步;母版側有牙、採用側零牙;W2 要 manifest 版本 + doctor 逐列 |
| P0-9 whitelist 有 source 結論 | ✅ 不算;J1 ASK_MORE 每輪從 S0–S2 重盤;讀白名單零機械執行 |
| API limit/Score 說法已修正 | ✅ draft-v4 §0.1 已記(W0 前) |
| No-Go:仍有會改資料模型或 runtime lifecycle 的未知 source | 無。P0-6 邊界表與 P0-5 判定已把資料模型與 lifecycle 的變數收成 P1-G4／P1-F4 的設計輸入 |

**W0 → W1 可放行。**W1 仍是 P1-G1～G7 pure/schema/fake transport + P2-1;runtime 一行不寫。

## 本輪明確沒做的事

- 沒改 `hooks/`、`memory/`、`skills/`、`scripts/`、契約檔、模板、guide。
- 沒寫 `scripts/devflow-jev.py`(P0-8 probe 用的 3 行 placeholder 只存在於暫存 pack 副本,隨 probe 刪除)。
- 沒登記 `docs/dev/STATUS.md`(P0-10 落 main 才做)。
- 沒歸檔 roadmap §18 的外部 Codex 材料。
