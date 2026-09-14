---
feature: five-station-f2
stage: 5-tasks
status: draft
owner: rick
updated: 2026-09-14
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — 五站 F2 coordinator + slug 倉 + 雙路電池（Writer A）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、main tip `5d686da`／#339；STATUS companion `#340`）。Lane = **full**。契約不 bump。
> 本 hop **只寫任務雙檔**，不落地 `scripts/`、不改 `STATUS.md`／`HISTORY.md`、不改 4-spec、不發明 G3、不 merge。
> Scope lock（S-8.9）：本 slug Stage 5–7 **只 F2**。Files 聯集 ⊆ 下方准許清單。**不准** F3 cut、**不准**切 `graph.yaml`、**不准**刪 G1／G2／`ACCEPTED` token、**不准**改 `_templates/`／doctor 握手／契約 bump。
> Diff Budget：F3／token／graph／模板／doctor／契約／STATUS／HISTORY **必須＝0**。本檔 Files 聯集已收在准許清單內。
> tracer（A 線）：T-1 先打通 **slug 倉 + Q12 第一次 persist＝0** 端到端 RED→GREEN；再加厚 RP 讀倉、五桶、doctor 約束、合法 hop、五問紀錄、注入紅格、Must-keep、專案樹／OLD7，最後雙路電池整包綠。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。
> 本檔 frontmatter `status: draft`。第 5 站不是 gate；owner 定案前不得動工。不發明 G3 PASS。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-7.6／S-8.2）。F2 是**新家族** `scripts/test-five-station-f2.sh`（加 `scripts/five_station_f2.py` 實作、可選把倉拆到 `scripts/five_station_f2_store.py`），不是改既有 doctor 握手、不是改 `_templates/`、不是 F3 cut。
NEW5 合成 fixture 根＝`scripts/fixtures/five-station-f2/new5/`（DD-3；不是本目錄、不是 `five-station-simplify`）。
OLD7 fixture 根＝`scripts/fixtures/five-station-f2/old7/`（DD-4；已有 1–7 `.md`）。
slug 倉路徑形＝`docs/dev/<slug>/.five-station/store`（DD-1；檔或目錄皆可；正本不在 `.devflow/runs/<run_id>/`）。鍵名 OPEN。
電池入口必須印 `=== CASE <NAME>`（與 F1 同形），才餵得進 Verify 的案例數斷言。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
Decision 原 13 列 CASE + 4-spec 加列 5 名只准加不准減。紅格極性＝**注入壞行為 → 該格紅**；把「拒 hop」記成紅格綠＝極性反了。

### 電池 CASE／群組（Stage 6 才建檔；Verify 必須點到 CASE 名）

| T | `--group` | 必印 `=== CASE`（官方名優先） | `-ge` |
|---|---|---|---|
| T-1 | store | NEW5-Q12-ZERO、NEW5-RUN2 | 2 |
| T-2 | teeth | NEW5-CAP-3、NEW5-DECIDE-2、NEW5-GOAL-2、NEW5-STORE-READ | 4 |
| T-3 | buckets | NEW5-SPEC-SHARE、NEW5-BUILD-SHARE、NEW5-SEVEN-STEM | 3 |
| T-4 | doctor | SC-DOCTOR、NEW5-MKTG-NOT-CUT、NEW5-UNDECLARED、F1-DOCTOR-PHRASE | 4 |
| T-5 | hop | NEW5-HOP-OK、NEW5-PRED-STOP | 2 |
| T-6 | events | NEW5-EVT-HOP、NEW5-EVT-LATCH、NEW5-EVT-CAP | 3 |
| T-7 | polarity | NEW5-MK-RED、NEW5-SHIP-MECH、NEW5-WAIT-RED、OLD7-FOLD-RED | 4 |
| T-8 | must-keep | NEW5-MK-M11、NEW5-MK-ANY、NEW5-SHIP-WAIT | 3 |
| T-9 | route | OLD7-NO-FIVE、OLD7-TOKEN、OLD7-SELF | 3 |
| T-10 |（不篩、整包入口） | Decision 原 13 + 加列 5 ＝ 18 名全在 | 18 |

T-4／T-6／T-8 的群組名不是 Decision 原列；4-spec 只准加不准減，加列不得把「檔在」加成通過條件。T-5 的逐 hop（S-4.15…S-4.19）與 T-1／T-3／T-9 的加厚斷言，寫進對應官方 CASE 的同一格體內，不必另發明可刪的通過條件。

### N1 R/S 盤點（70 S；本 hop 全承 F2）

| R | F2 必須落地的 S | 本 hop T |
|---|---|---|
| R-1 | S-1.1、S-1.2、S-1.3、S-1.4、S-1.10、S-1.11；S-4.12 | T-1 |
| R-1 | S-1.5、S-1.6、S-1.7、S-1.8、S-1.9、S-1.12；S-4.11 | T-2 |
| R-2 | S-2.1、S-2.2、S-2.3、S-2.4、S-2.5、S-2.6；S-4.13、S-4.14 | T-3 |
| R-3 | S-3.1、S-3.2、S-3.3、S-3.4、S-3.5、S-3.6 | T-4 |
| R-4／R-6 | S-4.2、S-4.3、S-4.15、S-4.16、S-4.17、S-4.18、S-4.19、S-6.2 | T-5 |
| R-5 | S-5.1、S-5.2、S-5.3、S-5.4 | T-6 |
| R-4／R-6／R-8 | S-4.4、S-4.5、S-4.6、S-4.7、S-4.8、S-4.9、S-6.4、S-8.5、S-8.6、S-8.8 | T-7 |
| R-6 | S-6.1、S-6.3、S-6.5、S-6.6 | T-8 |
| R-7 | S-7.1、S-7.2、S-7.3、S-7.4、S-7.5、S-7.6、S-7.7 | T-9 |
| R-2／R-4／R-8 | S-2.7、S-4.1、S-4.10、S-8.1、S-8.2、S-8.3、S-8.4、S-8.7、S-8.9 | T-10 |

70／70 皆被至少一個 T 承接。S-6.6／S-8.4／S-8.7 是「已在 4-spec 綠、後站不准翻」的守門，不是另開行為；掛 T-8／T-10 用電池＋檔集斷言釘死。無延後表。

### F2 Files 准許清單（S-8.9 可核）

Stage 6 全部 T 的 Files 聯集只准這幾條（fixture 目錄當前綴）：

- `scripts/test-five-station-f2.sh`
- `scripts/five_station_f2.py`
- `scripts/five_station_f2_store.py`
- `scripts/fixtures/five-station-f2/`
- `scripts/five_station_f1.py`（只准 RP-9／10／11 改讀 1A 倉；字樣牙回歸必須仍綠）
- 本目錄 `5-tasks.md`／`5-tasks.html`／`6-implementation-notes.md`／`6-implementation-notes.html`／`7-review.md`／`7-review.html`

超出上列 = L2／違 S-8.9。禁把 `guides/` F3 切線、`skills/dev-flow/stage*/graph.yaml`、G1／G2／`ACCEPTED` token 刪檔、`_templates/`、`hooks/_doctor_impl.py`、`devflow-contract.json`、`docs/dev/STATUS.md`／`HISTORY.md` 寫進任一 T 的 Files。

### Verify 開工前原樣跑（2026-09-14；電池尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-10 | `scripts/test-five-station-f2.sh` 不存在 → 非零 | ③綠不了但方向對 |

## T-1 打通 slug 倉第一次 persist＝0 的 Q12 縱切
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4, S-1.10, S-1.11; R-4 / S-4.12
- Files: scripts/five_station_f2.py, scripts/five_station_f2_store.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group store -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f2.sh --group store`
- Blocked-by: —
- Risk: high
- Intent: 日常多一次可指的倉數字：NEW5 合成 fixture 某 hop 第一次成功寫入之後該桶是 0（不是 1），再寫才 0→1→2；第一次寫不准拿來拒下一次重寫。另開新 run_id 再讀，數字仍在，不是 0。某 T 重做第 2 次（≤4）且沒整站重寫 Build 兩檔時，Build 桶不得 +1。改的是 slug 級只增倉與電池 NEW5-Q12-ZERO／NEW5-RUN2，不是 Cursor 擋寫、不是先鋪五站 graph。不會變成把 cap 正本塞進 run 級 events.jsonl，也不會把本目錄當 NEW5 白老鼠。
- Boundaries: Allowed module = slug 倉 + F2 電池入口（可把倉拆到 `five_station_f2_store.py`）。Data owner = 該 slug 的 coordinator 寫者。Forbidden dependency = run 級 `.devflow/runs/<run_id>/coordinator/events.jsonl` 當 cap 正本；他份 plugin cache；STATUS／chat。Interface = persist(hop_id)；路徑形 DD-1＝`docs/dev/<slug>/.five-station/store`（檔或目錄皆可）；讀路徑必須可換 fixture 根。Transaction = 單 hop 桶與該筆紀錄同成功或同失敗；同一初寫重試不得再 +1。Error seam = 寫失敗不 hop、不暗減。鍵名 OPEN。本 T 不接 RP 字樣牙、不評 hop 謂詞表、不改 `five_station_f1.py`。

## T-2 讓 RP-9／10／11 讀倉拒第三次重寫且字樣牙不得冒充
- [ ] 未完成
- Covers: R-1 / S-1.5, S-1.6, S-1.7, S-1.8, S-1.9, S-1.12; R-4 / S-4.11
- Files: scripts/five_station_f2.py, scripts/five_station_f2_store.py, scripts/five_station_f1.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group teeth -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --group teeth`
- Blocked-by: T-1
- Risk: high
- Intent: 日常 live 第三次重寫同一 hop、稿子上沒有「第 3 次」字樣時，牙必須因倉裡的 2 而拒，狀態 Escalated，拒後數字仍是 2。第 2 次 Decide 整站重開、離開 Intake 後第 2 次 Goal 重開同樣讀倉拒；Goal 連帶 Decide 的兩個計數必須同一 mutation 寫入，不得先寫 Goal 成功讓 Decide cap 被躲。注入「只咬 fixture 字樣、不讀倉」時 NEW5-STORE-READ 該格必須獨立紅。改的是 RP-9／10／11 讀倉接線與四格電池，不是改字樣牙回歸、不是放寬 hop≤2。不會變成 6C（繼續只咬正文）、不會 reset 數字再 hop。
- Boundaries: Allowed = F2 倉＋`five_station_f1.py` 最小讀倉接線。Forbidden = 改 F1 字樣正則回歸讓「第 3 次」稿不再紅；把拒 hop 記成 NEW5-STORE-READ 綠；把數字改小。Transaction = Goal+Decide 同一次 mutation，只成功一筆＝違 S-1.9。Test seam = 倉＝2 且對照稿刪掉「第 3 次」；NEW5-CAP-3 綠（讀倉拒）與 NEW5-STORE-READ 紅（不讀倉）必須分開。字樣牙只回歸。本 T 不評 marketplace／doctor、不切五桶觸發表。

## T-3 釘五桶 hop_id 且讓 Spec／Build 同桶、七 stem 注入變紅
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3, S-2.4, S-2.5, S-2.6; R-4 / S-4.13, S-4.14
- Files: scripts/five_station_f2.py, scripts/five_station_f2_store.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group buckets -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group buckets`
- Blocked-by: T-2
- Intent: 日常寫 `3-prototype.md` 再寫 `4-spec.md`，加的是同一個 Spec 桶，不是兩個 0。寫 `5-tasks.md` 再寫 `6-implementation-notes.md`，加的是同一個 Build 桶。hop_id 只准 Intake／Decide／Spec／Build／Ship 五字；舊節點 N7-g1／N6-g2 與七個 md stem 不得進倉。無 Stage 3 trigger 時不建 `3-prototype`、也不另開 proto 桶。注入「七 stem 各一桶各 ≤2」時 NEW5-SEVEN-STEM 該格必須獨立紅。改的是檔→五站觸發表，不是改 `graph.yaml`、不是另寫一份五站 graph。不會變成把 hop≤2 稀釋成七個獨立 2。
- Boundaries: Allowed = coordinator 觸發表 + NEW5 fixture。Forbidden = 改各站 `graph.yaml`；用 N7-g1／N6-g2 當 hop_id；七 stem 各一桶；無 trigger 仍建 proto 桶。NEW5-SEVEN-STEM 綠格義務＝注入七 stem 行為紅，不得把「coordinator 拒寫七 stem」記成此格綠。S-2.7（diff 對 graph 為空）掛 T-10，本 T 不把 `graph.yaml` 寫進 Files。本 T 不評 doctor、不寫事件鍵名。

## T-4 把 marketplace×doctor 當約束並在 COMPATIBLE 時拒五站 hop
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5, S-3.6
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group doctor -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --group doctor && bash scripts/test-five-station-f1.sh --group dual-read`
- Blocked-by: T-3
- Intent: 日常有人跑完 doctor 看到 COMPATIBLE／exit 0，或只做了 marketplace update、或只證明「我已在 plugin cache」，coordinator 對 live slug 求五站 hop 必須拒；理由是「路線未宣告／仍舊 7」，不得寫「doctor 已綠所以可 hop」。契約 2.0.0 + 五站 hops 預設＝違規，路線仍舊 7。F1 文案「doctor exit 0 所以可以跟 hops」仍紅（回歸地板）。改的是路線閘行為牙，不是改 doctor 握手、不是改 marketplace 清單。不會變成第四條前置、不會 bump 契約到 2.1.0。
- Boundaries: Allowed = F2 路線閘。Forbidden = 改 `hooks/_doctor_impl.py` 握手語意；改 marketplace 讓綠＝切線；把 doctor 綠／update／cache 當路條。S-3.4 接既有 `scripts/test-five-station-f1.sh --group dual-read`，該腳本只准呼叫、不准列入 Files、不准關掉這條回歸來換 coordinator 綠。S-3.5 由本 T 的 Files 聯集與後站 diff 守：不含 doctor／marketplace。本 T 不建五站機給 live slug。

## T-5 打通謂詞表列全真立刻 hop、列假停修且不等 G1／G2
- [ ] 未完成
- Covers: R-4 / S-4.2, S-4.3, S-4.15, S-4.16, S-4.17, S-4.18, S-4.19; R-6 / S-6.2
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group hop -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f2.sh --group hop`
- Blocked-by: T-4
- Risk: high
- Intent: 日常 NEW5 合成 fixture 三前置已過、當下 hop 的謂詞表列全真、latch 假、Must-keep 綠、該桶 <2 時，必須立刻 hop，紀錄寫得出 from／to，中間不准留下「要不要繼續／請人審／確認一下」。任一表列假 → 停該站修，理由含該列，不問人。Intake→Decide 吃 I1–I4；Decide→Spec 吃 D1–D4 且不等 G1 verdict；無 trigger 的 Spec→Build 吃 Sp1–Sp4＋Sp5a＋Sp6、不建 3-prototype、不等 G2 verdict；B1 命中但缺人類 attestation → 不 hop、進 HumanWait；Build→Ship 吃 Bu1–Bu4。改的是 hop 評表，不是改問 owner、不是填 PASS。不會變成用「謂詞全真」四字替代表列，也不會在本 T 標 Ship Done。
- Boundaries: Allowed = hop evaluator + NEW5 fixture。Forbidden = 問「要不要繼續」；等 G1／G2 頂欄才 hop；Agent 寫 attestation；拿本目錄當 hop 主詞。NEW5-HOP-OK 必須對到 4-spec 謂詞表列，不得只印「謂詞全真」。S5a／S5b 互斥：先評 Stage 3 trigger。Ship **無**自動前進列（S-6.3 掛 T-8）。本 T 不注入壞行為（屬 T-7）、不鎖事件 JSON 鍵。

## T-6 留下 hop／latch／cap 紀錄讓人答五問且不鎖鍵名
- [ ] 未完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3, S-5.4
- Files: scripts/five_station_f2.py, scripts/five_station_f2_store.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group events -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group events`
- Blocked-by: T-5
- Intent: 日常一次 hop 成功、一次 latch 開火、一次 cap 用盡之後，人必須指得到三筆紀錄，每筆能答誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated。拿出 Cursor chat、`STATUS.md` 過期列、或既有 `attempt_completed` 都不算正本。改的是與 1A 同壽命的 slug ledger，不是 bump `agent-event` schema、不是選定 `event_type=hop_advanced` 當已核鍵。不會變成採用端只 update plugin、契約 schema 仍 1.1 就被 doctor 判 INCOMPATIBLE，也不會把看板當 hop log。
- Boundaries: Allowed = slug ledger（與倉同壽命）。Forbidden = bump `observability/schema/agent-event.schema.json`；把具體 JSON／YAML 鍵寫成「本 Decision／本 spec 已核」；用 chat／STATUS／`attempt_completed` 冒充。鍵名保持 OPEN；後站鎖鍵＝偷做 annex，回 Stage 2。Compatibility = 不 bump agent-event。本 T 不改 doctor、不改 STATUS。Test seam = 三類各至少一筆可指，五問有答即可，不比鍵名。

## T-7 注入壞行為讓紅格獨立變紅且 hollow 不得當 F2 綠
- [ ] 未完成
- Covers: R-4 / S-4.4, S-4.5, S-4.6, S-4.7, S-4.8, S-4.9; R-6 / S-6.4; R-8 / S-8.5, S-8.6, S-8.8
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group polarity -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --group polarity`
- Blocked-by: T-6
- Risk: high
- Intent: 日常電池必須能各自餵壞行為並讓該格獨立紅：Must-keep 紅仍 hop（NEW5-MK-RED）；機械綠無人寫 PASS 卻標 Done（NEW5-SHIP-MECH）；謂詞真 latch 假仍留下「要不要繼續／請人審／確認一下」（NEW5-WAIT-RED）；對已有 1–7 `.md` 的 in-flight 寫五站狀態（OLD7-FOLD-RED）。把「coordinator 拒 hop／拒寫」記成這些紅格綠＝極性反了，整組必須非 0。只證明 coordinator 檔在、只跑 F1 十二群、只跑 NEW5 組而跳過 OLD7，都不得標 F2 綠。改的是電池極性與 hollow 拒收，不是把合法拒 hop 塗成紅格綠。不會變成缺一路仍 exit 0。
- Boundaries: 極性契約＝列寫「→ 紅」就餵壞行為，該格獨立變紅；`--group polarity` exit 0 **當且僅當**四格預期紅都紅、極性反了被拒、三個 hollow 宣稱被拒。Forbidden = 把拒 hop 當紅格綠；只測 M11、放過其餘 M 紅仍 hop（完整 16 M 拒 hop 屬 T-8，本 T 至少要讓「只測 M11」本身紅）；把檔在／F1 綠／只 NEW5 綠加成通過條件。OLD7-FOLD-RED 清回舊 7 是修復，不是此格綠。本 T 不改 token、不折 live slug。

## T-8 讓任一 Must-keep 紅就拒 hop 且 Ship 無自動 Done
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.3, S-6.5, S-6.6
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group must-keep -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group must-keep`
- Blocked-by: T-7
- Intent: 日常 Build 某 T 缺 Verify（M11），或 M1–M16 任一紅（測名無 S-id、缺觀測欄、代填 ACCEPTED、Files 超出聯集、reviewer＝implementer、token 被刪……），coordinator 必須不 hop，理由含該 M 編號或同等名，不得說「已經五站了所以可 hop」。只擋 M11、其餘 M 紅仍 hop＝本條紅。`7-review.md` 機械全綠但頂欄 `verdict:` 空白時，不得 hop 到 Done，必須 HumanWait。4-spec Must-keep Disposition 16 列必須仍在、無一列標可選。改的是自動前進謂詞的完整度牙，不是重寫 brief、不是本 hop 跑 G3。不會變成先 hop 再補 Must-keep。
- Boundaries: Must-keep 進謂詞；M1–M16 任一紅 → 拒 hop。Test seam = 對照稿 16 份各少一 M，皆不 hop。S-6.6 守門＝讀 `docs/dev/five-station-f2/4-spec.md` 的 Disposition 16 列去向 ∈ {本方案處理, 刻意維持}，下落至少一條 S-；本 T 不准把該表標可選／Non-Goal。Ship 無自動前進列。Forbidden = 用「已經五站了」省略；Agent 代填 PASS／ACCEPTED。本 T 不刪 token、不發明 G3。

## T-9 先問專案樹三前置並讓 OLD7 與本目錄不建五站機
- [ ] 未完成
- Covers: R-7 / S-7.1, S-7.2, S-7.3, S-7.4, S-7.5, S-7.6, S-7.7
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group route -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group route`
- Blocked-by: T-8
- Risk: high
- Intent: 日常缺「契約已宣告 2.1.0」或「非 in-flight」或「F3 cut 已發生」任一條，必須 `allow_legacy()`，不建五站機、不套三 cap。plugin cache 只決定本 process 讀哪份 hops 碼，不是路條；不得掃磁碟上「最新」的其他 cache 把舊 7 拖走。OLD7 fixture 已有 1–7 `.md` → 無五站狀態寫入、三 cap 不套、token／F1 牙仍綠（OLD7-NO-FIVE／OLD7-TOKEN）。對 `docs/dev/five-station-f2/` 求五站自動前進跳不過（OLD7-SELF）。NEW5 試體路徑不是本目錄、也不是 `five-station-simplify`。改的是路線閘與 OLD7 路，不是遠端改線、不是拿 live slug 當白老鼠。不會變成 F3 前對 live 評五站謂詞。
- Boundaries: 三前置全要；缺一＝舊 7。路線 SoT＝專案樹（契約檔 + 該 slug 是否已有 1–7 `.md`），不認啟動 cache。NEW5 根＝DD-3 `scripts/fixtures/five-station-f2/new5/`；OLD7 根＝DD-4 `scripts/fixtures/five-station-f2/old7/`。Forbidden = 掃最新 cache；本目錄／`five-station-simplify` 當 NEW5；對 in-flight 寫五站機。OLD7-TOKEN 接 `scripts/check-gate-tokens.sh` 與 `scripts/test-five-station-f1.sh`，兩支只准呼叫、不准列入 Files、不准刪 token 來換綠。本 T 不改 graph、不 bump 契約。

## T-10 鎖死三把 Non-Goals 並讓同一電池 NEW5+OLD7 一起綠
- [ ] 未完成
- Covers: R-2 / S-2.7; R-4 / S-4.1, S-4.10; R-8 / S-8.1, S-8.2, S-8.3, S-8.4, S-8.7, S-8.9
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/five_station_f2_store.py, scripts/five_station_f1.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 18 && bash scripts/test-five-station-f2.sh && python3 -c "import pathlib,re,subprocess; t=pathlib.Path('docs/dev/five-station-f2/5-tasks.md').read_text(); spec=pathlib.Path('docs/dev/five-station-f2/4-spec.md').read_text(); names='NEW5-HOP-OK NEW5-PRED-STOP NEW5-CAP-3 NEW5-DECIDE-2 NEW5-GOAL-2 NEW5-MK-RED NEW5-SHIP-MECH NEW5-WAIT-RED NEW5-RUN2 OLD7-NO-FIVE OLD7-FOLD-RED OLD7-TOKEN OLD7-SELF NEW5-STORE-READ NEW5-SEVEN-STEM NEW5-SPEC-SHARE NEW5-BUILD-SHARE NEW5-Q12-ZERO'.split(); assert all(n in t for n in names); assert 'F3 cut' in spec and '後站不准改成 In' in spec; assert spec.count('| M1')+spec.count('| M2')>=1; q=sum(1 for i in range(9,25) if ('Q'+str(i)) in spec); assert q>=16; print('T-10-knife-ok')"`
- Blocked-by: T-9
- Risk: high
- Intent: 日常宣稱 F2 完時，必須是同一支 `scripts/test-five-station-f2.sh` 在同一 process 把 NEW5 組與 OLD7 組都跑完才 exit 0。只跑 NEW5、只跑 OLD7、入口只 exec `test-five-station-f1.sh`、兩支互不認識的腳本各綠一次，都必須非 0。Decision 原 13 列 CASE 名都在，加列 5 名都在，不得減列。完成樹沒有 F3 cut 把新 slug 預設改五站、沒有把 in-flight 折成五站、沒有刪 G1／G2／`ACCEPTED`；後站不准把這三把改成 In。`graph.yaml` diff 為空。4-spec 已過的 G2／Q9–Q24 去向不得被本刀翻掉。改的是收口電池與刀範圍守門，不是順便切 guide、不是改 STATUS。不會變成檔在＝完、不會發明 G3。
- Boundaries: SC-BATTERY＝單一入口；缺一路即非 0。S-8.9 Files 聯集＝本檔「F2 Files 准許清單」。Diff Budget 必須＝0 的區塊：`guides/` F3 cut；各站 `graph.yaml`；token 刪檔；`_templates/`；doctor 握手；`devflow-contract.json` bump；STATUS／HISTORY。S-8.4 原 GWT 是 Stage 4 hop 只交 4-spec 雙檔（已在 #339 綠）；本 T 守門＝不准重開那條、不准在本刀改 4-spec 頂欄。S-8.7 守門＝4-spec Disposition 仍覆蓋 Q9–Q24。Forbidden = 把三把鎖標可選／In；把「檔在」加成通過條件；本 T 改 STATUS／HISTORY。本 hop 不把 6-notes／7-review 當完成條件。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-10 單鏈 | Feature Risk high；倉／牙／hop／電池改同一支 `five_station_f2.py`。Files 重疊，無法證明可平行 | 4-spec Verification Profile Risk high；模板 parallel 須 Files 不重疊 | parallel 讓 T-2 與 T-3 同時改倉。棄：review 吵、計數互踩 |
| T-1 選 Q12 persist＝0 不當 hop 謂詞 | 最薄端到端是「倉數字可指、第一次＝0」；沒有倉，後面 RP／hop／電池都咬錯東西 | 4-spec S-1.1／S-4.12；使用者 Cover「slug store + Q12」 | T-1 先做 hop 評表。棄：沒倉的 hop 是 hollow |
| 單一實作家族 `five_station_f2` + 單一電池入口 | Diff Budget coordinator ≤4、入口 1 檔；SC-BATTERY 禁兩支互不認識的腳本 | 4-spec DD-2；S-4.1 | 每 CASE 一支 `test-new5-*.sh`。棄：hollow dual-path |
| 倉可拆第二檔 `five_station_f2_store.py` | Budget 准 ≤4；T-1／T-6 寫入原子性與路徑可換根值得分檔，但不是必拆 | 4-spec DBC slug store；Diff Budget | 第三、第四支雜檔。棄：爆檔數。棄：把倉寫進 run ledger |
| RP 讀倉最小改 `five_station_f1.py` | 4-spec 明文可改讀倉、不改字樣牙回歸；不另造第二支 cap 牙家族 | 4-spec S-1.5…S-1.7／S-1.12；S-8.9 | 關掉 F1 正則來換綠。棄：6C |
| T-4／T-6／T-8 加 group 名 | Decision 原 13 列沒有獨立 doctor／events／must-keep CASE 名；只准加 | 4-spec「只准加不准減」 | 減 NEW5-HOP-OK 來騰位。棄：翻 Decision |
| S-6.6／S-8.4／S-8.7 掛守門 T、不另開行為 T | 三條已在 4-spec 綠（Disposition／Stage 4 檔集／Q 去向）。另開 T 會變成水平「再寫一次表」 | 4-spec S-6.6／S-8.4／S-8.7；F1 同款延後／守門 | 發明 T-11 重抄 Disposition。棄：無新可觀測行為 |
| 不改 doctor／graph／模板／STATUS | S-3.5／S-2.7／S-8.9；本 hop 只任務雙檔 | 4-spec S-8.9；使用者 Hard Files | 順便 F3 cut 或改 STATUS。棄：違刀 |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f2.sh` 不存在 → 十欄皆非零 | 模板 Verify 三律 ③ | 用已綠的 `test-five-station-f1.sh` 當 T-1 牙。棄：無鑑別力且違 S-8.6 |
