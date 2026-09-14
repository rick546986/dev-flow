---
feature: five-station-f2
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: writer-c
reviewers: []
updated: 2026-09-14
---
- Reviewer note: Stage7-C draft（fresh-context Writer C；≠ implementer-A／≠ rick）。**不是 G3 PASS**。Human 未簽。Agent 禁寫頂欄 PASS。5-tasks checkbox 保持未勾。

# 7. 驗證 —— **不是 G3 PASS**（Stage7-C draft；F2 knife only）

> ## Reviewer 閱讀動線(**必留;給看的人,不是給寫的人**)
>
> 以下五步固定,產文件時逐字保留、只換數字:
>
> | 步 | 讀哪節 | 這步問的唯一問題 |
> |---|---|---|
> | 1 | **Verdict** | 判定是什麼?門檻表每一格是不是都有證據? |
> | 2 | **Exit Checklist** | 還缺什麼才能出貨?哪幾項要 owner 親自動? |
> | 3 | **附錄:本輪特有** | 本輪的爭點/分歧在哪,誰對? |
> | 4 | **Known Limits** | 有沒有一條是 owner 不能接受的? |
> | 5 | **抽驗一列** | 本場 twin 第五格鎖 Coverage 中位列 **S-4.3**。打開 `scripts/five_station_f2.py:875-882`（PRED-STOP `why==Sp2`、未 hop Spec→Build、無「要不要繼續」）、`scripts/five_station_f2.py:464-465`（`OBS_FIELD` 缺 → `Sp2`）、`scripts/fixtures/five-station-f2/new5/pred-stop/docs/dev/stop/4-spec.md`（故意不寫觀測欄）。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡**。本檔是 **Writer C 獨立審查草稿**，`verdict: PRE-REVIEW`，`status: draft`。**全勾 ≠ PASS。Human 未簽。未發明 G3 PASS。**
> 產品碼已在 `origin/main` tip `#351`=`858336e`（實作 #346／standing #349／RR1 #350／RR2 #351）。本 PR **只** `7-review.md` + `7-review.html`。Scope = **F2 knife only**。不宣稱 F3 cut。不改 STATUS。不合併。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | Writer C（fresh-context Cloud Agent `bc-9df2e6c4-c3cb-4178-8bed-8dd41d185619`；**≠** Stage 6 實作 owner `implementer-A`／#346／#349） |
| Stage 6 實作 | `implementer-A`；獨立 T-Review R2／R1 後 standing rework；**RR1 #350 與 RR2 #351 各 10/10 ACCEPTED**。**不是** G3 |
| Human G3 | **未簽**。頂欄禁止 PASS。本檔不得被讀成 G3 PASS |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、70 S、DD-1…DD-10 Owner PASS） ②`5-tasks.md`（T-1…T-10；checkbox 未勾） ③`scripts/test-five-station-f2.sh` + `scripts/five_station_f2.py` + fixtures ④`git show 481e9cc`／`c16a3ce`（#346／#349 vs `56c8019`） ⑤親跑電池／hollow／spec-gate／token／F1／doctor-route／must-keep／events → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-1／D-2／D-3／RR1／RR2 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 `.devflow/` runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 main。審核樹 Source SHA = `858336e9441cec636549b3dc2d35ef273e03794f`（本 docs commit 會再漂 SHA，不重綁、不發明第二份 Fresh）。本 PR 只 7-review 雙檔。**F2 knife only** |
| 可信／打折 | 機械數字（18 CASE／failed=0／hollow exit 3／spec-gate 9/9／token 全過／F1 failed=0）以本場親跑為準。F-id 分級與 D-1「L1 vs 4-spec 超出→L2」張力交給 Human。未想到的事打折 |

建議 reviewer 路徑：適格人類（owner rick）開審頁抽驗 S-4.3 三個 `檔:行`，讀 Known Limits D-1–D-3，再經頁尾「提交判定」寫頂欄。Agent 不代填。

## Coverage Matrix

自建（grep `five_station_f2.py` 的 `S-*` check／官方 18 CASE ↔ 4-spec 70 S；**未先讀** Self-Review）。末列固定回歸。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | NEW5-Q12-ZERO；`five_station_f2.py:621-624` first persist=0 + 同 token idempotent | ✅ |
| S-1.2 | 同 CASE；`:626` second persist=1 | ✅ |
| S-1.3 | 同 CASE；`:628-629` 兩次 rewrite 後仍允許（第一次不算 hop≤2） | ✅ |
| S-1.4 | NEW5-RUN2；`:646-647` 新 process 仍 2 | ✅ |
| S-1.5 | NEW5-CAP-3；`:667-675` 第 3 次拒／Escalated／RP-9 讀倉 | ✅ |
| S-1.6 | NEW5-DECIDE-2；`:700-704` 第 2 次 Decide 拒＋RP-10 | ✅ |
| S-1.7 | NEW5-GOAL-2；`:720-724` 第 2 次 Goal 拒＋RP-11 | ✅ |
| S-1.8 | NEW5-CAP-3；`:669-671` 拒後仍 2、reset hop 拒 | ✅ |
| S-1.9 | NEW5-GOAL-2；`:714-715` Goal+Decide 同 mutation | ✅ |
| S-1.10 | NEW5-GOAL-2；`:728-729` T retry ≠ hop 桶 | ✅ |
| S-1.11 | Q12／RUN2；`:631`／`:648-649` 路徑不含 `.devflow/runs/` | ✅ |
| S-1.12 | NEW5-STORE-READ；`:684` 字樣牙不讀倉＝紅格 | ✅ |
| S-2.1 | NEW5-SPEC-SHARE；`:742` hop_id ⊆ 五站名 | ✅ |
| S-2.2 | NEW5-SPEC-SHARE；`:741` proto+spec 同 Spec 桶＝1 | ✅ |
| S-2.3 | NEW5-BUILD-SHARE；`:771` tasks+notes 同 Build 桶＝1 | ✅ |
| S-2.4 | NEW5-SEVEN-STEM；`:784` 注入七 stem＝紅格 | ✅ |
| S-2.5 | `run_share`；`:753-761` 無 proto 檔；`persist(Stage3)` 拒 `no-proto-bucket` | ✅ |
| S-2.6 | SPEC-SHARE；`:743-744` 無 N7-g1／N6-g2 | ✅ |
| S-2.7 | `#346`／`#349` `git diff --name-only` 零 `graph.yaml` | ✅ |
| S-3.1 | `--group doctor-route`；`:793-797` 拒 hop、理由是路線、不含「doctor 已綠所以可 hop」 | ✅ |
| S-3.2 | doctor-route；`:801-804` marketplace+cache ≠ ticket；`f3_cut_happened` 假 | ✅ |
| S-3.3 | doctor-route；`:807-809` 契約仍 2.0.x | ✅ |
| S-3.4 | F1 回歸 `test_s_5_6_*`；`five_station_f1.py:217-218` 文案牙仍紅 | ✅ |
| S-3.5 | `#346`／`#349` 未改 `hooks/_doctor_impl.py`／marketplace | ✅ |
| S-3.6 | doctor-route；`:812-813` cache 不是第四條前置 | ✅ |
| S-4.1 | 全入口 exit 0；`--only new5&#124;old7&#124;f1` 各 exit 3（本場抽驗以外的完成定義） | ✅ |
| S-4.2 | NEW5-HOP-OK `--hop I/D/Sp/Bu`；`:835-867` 四 hop 綠 | ✅ |
| S-4.3 | NEW5-PRED-STOP；`:875-882` `why==Sp2`（本場抽驗列） | ✅ |
| S-4.4 | NEW5-MK-RED；`:935` `inject=mk-hop` 仍 hop＝紅格 | ✅ |
| S-4.5 | NEW5-SHIP-MECH；`:943` 注入 Done＝紅格 | ✅ |
| S-4.6 | NEW5-WAIT-RED；`:950` 注入等人句＝紅格 | ✅ |
| S-4.7 | OLD7-FOLD-RED；`:960` 對 OLD7 寫五站倉＝紅格 | ✅ |
| S-4.8 | T-7 四格皆 `inject=` 壞行為；拒 hop 不當紅格綠（與 S-4.4…S-4.7 同測） | ✅ |
| S-4.9 | hollow 三探針 exit 3；檔在／只 F1／只 NEW5 ≠ 完成 | ✅ |
| S-4.10 | `OFFICIAL` 18 名（`:33-39`）；本場 `=== CASE` = 18；無發明名 | ✅ |
| S-4.11 | 同 S-1.12 | ✅ |
| S-4.12 | 同 S-1.1／S-1.3；`:632` | ✅ |
| S-4.13 | 同 S-2.2 | ✅ |
| S-4.14 | 同 S-2.3 | ✅ |
| S-4.15 | HOP-OK `--hop I`；`:835-838` Intake→Decide | ✅ |
| S-4.16 | `--hop D`；`:847-849` 不等 G1 | ✅ |
| S-4.17 | `--hop Sp`；`:856-860` 無 trigger 不建 proto | ✅ |
| S-4.18 | `--hop Sp5b`；`:893-894` 無 attestation → HumanWait | ✅ |
| S-4.19 | `--hop Bu`；`:867` Bu1–Bu4 | ✅ |
| S-5.1 | `--group events`；`:902-925` hop／latch／cap 三筆＋五問欄 | ✅ |
| S-5.2 | events；`:926-927` 正本不是 STATUS／attempt_completed | ✅ |
| S-5.3 | `#346`／`#349` 零 `observability/schema/`／契約 bump | ✅ |
| S-5.4 | `five_station_f2.py:5`「Key names are implementer-local (OPEN)」；5-tasks 未把具體鍵寫成已核 | ✅ |
| S-6.1 | `--group must-keep` M11 overlay；`evaluate_hop` 拒、`why` 含 M11 | ✅ |
| S-6.2 | HOP-OK I；`:839-840` 無「要不要繼續／請人審」 | ✅ |
| S-6.3 | 合法 Bu hop → Ship 不是 Done；Done 只在 `inject=ship-done` 紅格 | ✅ |
| S-6.4 | MK／SHIP／WAIT 三格獨立紅（S-4.4…S-4.6） | ✅ |
| S-6.5 | `--group must-keep` 16 CASE；M1–M16 各 `ok=False` 且 `why` 含該 M、未 hop→Ship | ✅ |
| S-6.6 | 4-spec Must-keep Disposition 16 列皆有去向；無「可選」（G2 已綠；本場複核表在） | ✅ |
| S-7.1 | OLD7-NO-FIVE／doctor-route；`:997`／`:801-803` 缺前置 → legacy | ✅ |
| S-7.2 | `allow_legacy` `:289-290` 丟棄 cache 旗標；doctor-route S-3.2／S-3.6 | ✅ |
| S-7.3 | 同 S-7.2；不掃最新 cache | ✅ |
| S-7.4 | OLD7-NO-FIVE；`:993-996` 有 1–7 md、無五站機 | ✅ |
| S-7.5 | OLD7-TOKEN；`:1005-1010` token exit 0＋F1 exit 0 | ✅ |
| S-7.6 | OLD7-SELF；`:1015-1017` 本目錄跳不過、舊 7 檔仍在 | ✅ |
| S-7.7 | OLD7-SELF；`:1019-1022` NEW5 不是本目錄／simplify | ✅ |
| S-8.1 | `f3_cut_happened` 恆假；guide 無「新 slug 預設五站」；後站 Files 未把 F3 改成 In | ✅ |
| S-8.2 | OLD7-NO-FIVE＋OLD7-FOLD-RED；in-flight 不折 | ✅ |
| S-8.3 | `check-gate-tokens.sh` exit 0；零 token 刪檔 | ✅ |
| S-8.4 | gate：Stage 4 hop 雙檔已 G2 綠，不准重開（本場不重審 4-spec 頂欄） | ✅ |
| S-8.5 | 完成條件要求 S-4.1 入口；檔在單獨不算（hollow `--only`） | ✅ |
| S-8.6 | F1 綠是回歸地板；`--only f1` exit 3 | ✅ |
| S-8.7 | gate：Q9–Q24 去向已 G2 綠；Q21–Q23 不得標可選 | ✅ |
| S-8.8 | `--only new5` exit 3 | ✅ |
| S-8.9 | 行為 Files ⊆ 准許清單；D-1 四檔是 documented L1（見 KL #1），不是 F3／graph／token | ✅ |
| 既有測試套件(回歸) | `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`；`bash scripts/check-gate-tokens.sh .`；`bash scripts/test-five-station-f1.sh`；`bash scripts/check-file-map.sh` | ✅ |

**回歸末行（Writer C @ `858336e`）**：spec-gate `9/9` exit 0（70 S）；token 全過；F1 `failed=0`；file-map forward 210 exit 0。F2 電池 `failed=0`、`=== CASE` = 18、exit 0。hollow 三探針各 exit 3。未知旗標 exit 2。

## Verification Evidence

<!-- Final Fresh 綁產品樹 main tip。本 PR 後續只加本雙檔，不改牙。
     4-spec Required 層名（gauntlet 全等）照 Verification Profile 原文 tokenize。
     電池已落地 → Conditional 觸發；本場另加 --require-layer 加嚴。 -->

- Source SHA: 858336e9441cec636549b3dc2d35ef273e03794f
- Final Fresh Run ID: f2-s7c-fresh-858336e-20260914
- Entry point: `bash scripts/test-five-station-f2.sh`（F2 Conditional：電池列入 Required）然後 `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`） | `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md` | pass | exit 0; 9/9; 70 S | |
| token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F2 電池列 Required | `bash scripts/check-gate-tokens.sh .` | pass | exit 0; G1/G2/G3 token 全過 | |
| test-five-station-f2 | `bash scripts/test-five-station-f2.sh -v` | pass | exit 0; failed=0; CASE=18 | |
| hollow-new5 | `bash scripts/test-five-station-f2.sh --only new5` | pass | exit 3 | |
| hollow-old7 | `bash scripts/test-five-station-f2.sh --only old7` | pass | exit 3 | |
| hollow-f1 | `bash scripts/test-five-station-f2.sh --only f1` | pass | exit 3 | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | exit 0; failed=0 | |
| f2-doctor-route | `bash scripts/test-five-station-f2.sh --group doctor-route -v` | pass | exit 0; failed=0 | |
| f2-must-keep | `bash scripts/test-five-station-f2.sh --group must-keep -v` | pass | exit 0; CASE=16; failed=0 | |
| f2-events | `bash scripts/test-five-station-f2.sh --group events -v` | pass | exit 0; failed=0 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; forward 210; table_rows=220 | |
| UI e2e（本刀無新前端） | | n-a | | Explicitly excluded |
| 負荷／效能（coordinator 非熱路徑） | | n-a | | Explicitly excluded |
| 金流／auth fuzz（不涉） | | n-a | | Explicitly excluded |
| 本 hop 跑 coordinator（碼 Out of Scope） | | n-a | | Stage 4 hop 語意；本場 Stage 7 已改跑落地電池（上行 test-five-station-f2） |

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得只咬 fixture「第 3 次」字樣（RP-9／10／11） | NEW5-STORE-READ 紅格；CAP-3／DECIDE-2／GOAL-2 讀倉 | pass |
| 紅格不得把拒 hop 當綠 | NEW5-MK-RED／SHIP-MECH／WAIT-RED／OLD7-FOLD-RED 皆 `inject=` | pass |
| 本 hop 不得改 STATUS／牙／契約 | `#346`／`#349` 零 STATUS／doctor／契約／token 刪檔 | pass |
| 鍵名不得升成已核 | S-5.4；OPEN 註記 | pass |
| 不得只擋 M11 | `--group must-keep` 16 M 各拒 | pass |
| 不得做 F3 cut／折 in-flight／刪 token | S-8.1…S-8.3；hollow＋token | pass |
| 不得把檔在／只 F1／只 NEW5 當完成 | `--only` 三探針 exit 3 | pass |
| 不得 bump agent-event | 零 schema diff | pass |
| 不得七 stem 各一桶 | NEW5-SEVEN-STEM 紅格 | pass |
| 不得把 run 級 events 當 cap 倉 | S-1.11 路徑檢查 | pass |
| 不得改 `graph.yaml`／`_templates/` | `#346`／`#349` 零那些路徑 | pass |
| Q24 看板／本 PR 改 STATUS | 本 review PR 不改 STATUS | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#346／#349 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **Writer C 2026-09-14 親跑** `bash scripts/test-five-station-f2.sh -v` 與 `--group`／`--only`（不採信 6-notes 貼文）。長輸出見附錄 A4。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 從 slug 倉讀 hop 桶＝0 | `[ok] S-1.1 first persist=0`；retry `idempotent` 仍 0 | ✅ |
| S-1.2 | 連續讀 +1 | `[ok] S-1.2 second persist=1` | ✅ |
| S-1.3 | 桶＝0 時重寫不被 hop≤2 拒 | `[ok] S-1.3 two rewrites after first` | ✅ |
| S-1.4 | 跨 process 再讀 | `[ok] S-1.4 new process still 2/0/0` | ✅ |
| S-1.5 | 拒＋倉數字＋RP-9 | `[ok] S-1.5 third rewrite refused`／Escalated／`RP-9 reads store` | ✅ |
| S-1.6 | 拒＋decide_reopen | `[ok] S-1.6 second Decide reopen refused` | ✅ |
| S-1.7 | 拒＋goal／decide | `[ok] S-1.7 second Goal refused` | ✅ |
| S-1.8 | 數字不減 | `[ok] S-1.8 still 2`／`no reset hop` | ✅ |
| S-1.9 | 同一次 mutation | `[ok] S-1.9 Goal+Decide same mutation` | ✅ |
| S-1.10 | T 重做 hop 桶不動 | `[ok] S-1.10 T retry ≠ hop` | ✅ |
| S-1.11 | 正本不在 `runs/` | `[ok] S-1.11 store not run-level` | ✅ |
| S-1.12 | 不讀倉路徑紅 | `[ok] S-1.12/S-4.11 string-only miss is the red cell` | ✅ |
| S-2.1 | hop 識別＝五站名 | `[ok] S-2.1 only five hop_id` | ✅ |
| S-2.2 | Spec 同桶 | `[ok] S-2.2/S-4.13 same Spec bucket` | ✅ |
| S-2.3 | Build 同桶 | `[ok] S-2.3/S-4.14 same Build bucket` | ✅ |
| S-2.4 | 七 stem 紅 | `[ok] S-2.4 seven-stem injection is the red cell` | ✅ |
| S-2.5 | 無 proto 桶 | `[ok] S-2.5 persist refuses Stage3 bucket` | ✅ |
| S-2.6 | 不含舊 graph 節點 | `[ok] S-2.6 old graph nodes are not hop_id` | ✅ |
| S-2.7 | diff 無 graph.yaml | `#346`／`#349` name-only 無 `**/graph.yaml` | ✅ |
| S-3.1 | 拒因是路線 | `[ok] S-3.1 reason is route` | ✅ |
| S-3.2 | 未改線 | `[ok] S-3.2 F3 cut has not happened` | ✅ |
| S-3.3 | 2.0.x＋五站 hops 違規 | `[ok] S-3.3 contract still 2.0.x` | ✅ |
| S-3.4 | F1 文案牙仍紅 | F1 `test_s_5_6_* red=True` | ✅ |
| S-3.5 | 檔集 | 零 doctor／marketplace 語意 diff | ✅ |
| S-3.6 | cache 不放行 | `[ok] S-3.6 cache is not a fourth precondition` | ✅ |
| S-4.1 | 入口 exit 四格 | 全跑 0；`--only` 三格 3；未知旗標 2 | ✅ |
| S-4.2 | hop＋五問＋綠 | HOP-OK 四 hop `[ok]` | ✅ |
| S-4.3 | 停點理由含謂詞假 | `[ok] S-4.3 predicate false → no hop (got Sp2)`（抽驗列） | ✅ |
| S-4.4 | 注入 MK 仍 hop 紅 | `[ok] S-4.4 inject MK-red still hop is the red cell` | ✅ |
| S-4.5 | 注入 Done 紅 | `[ok] S-4.5 inject mechanical Done is the red cell` | ✅ |
| S-4.6 | 注入等人句紅 | `[ok] S-4.6 inject 要不要繼續 is the red cell` | ✅ |
| S-4.7 | 注入折線紅 | `[ok] S-4.7 inject five-station write on OLD7` | ✅ |
| S-4.8 | 紅格只接受注入壞行為 | 四格皆 `inject=`；電池 exit 0 | ✅ |
| S-4.9 | 三假綠非 0 | hollow 三探針 exit 3 | ✅ |
| S-4.10 | 13 名全在＋加列 5 | `OFFICIAL` 18；本場印 18 名 | ✅ |
| S-4.11 | 同 S-1.12 | 同上 | ✅ |
| S-4.12 | 同 S-1.1 | 同上 | ✅ |
| S-4.13 | 同 S-2.2 | 同上 | ✅ |
| S-4.14 | 同 S-2.3 | 同上 | ✅ |
| S-4.15 | Intake→Decide 紀錄 | `[ok] S-4.15 from-to` | ✅ |
| S-4.16 | 無請填 G1 | `[ok] S-4.16 no wait for G1` | ✅ |
| S-4.17 | 無 3-prototype | `[ok] S-4.17 no 3-prototype created` | ✅ |
| S-4.18 | HumanWait | `[ok] S-4.18 Sp5b no attestation → HumanWait` | ✅ |
| S-4.19 | Build→Ship | `[ok] S-4.19 Build→Ship Bu1–Bu4` | ✅ |
| S-5.1 | 三類紀錄＋五問 | events 組 hop／latch／cap 各 `[ok]` | ✅ |
| S-5.2 | 正本不是 chat／STATUS | `[ok] S-5.2 original is slug ledger` | ✅ |
| S-5.3 | schema 不 bump | 零 schema diff | ✅ |
| S-5.4 | 無已核鍵名 | OPEN 註記仍在 | ✅ |
| S-6.1 | 拒含缺 Verify | must-keep `11-m11.md` `why=M11` | ✅ |
| S-6.2 | 立刻 hop、無人句 | `[ok] S-6.2 no please-review` | ✅ |
| S-6.3 | 停 Ship／HumanWait | 合法 Bu 到 Ship；Done 只在注入紅格 | ✅ |
| S-6.4 | 三格獨立紅 | 三 CASE 皆印且電池仍 0 | ✅ |
| S-6.5 | 16 份皆不 hop | must-keep 16×`evaluate_hop refuses` | ✅ |
| S-6.6 | Disposition 16 列 | 4-spec L128–143 16 列；無「可選」 | ✅ |
| S-7.1 | 缺一條＝舊 7 | `[ok] S-7.1 in-flight → legacy` | ✅ |
| S-7.2 | 碼新路舊 | cache 旗標被丟棄 | ✅ |
| S-7.3 | 只讀當下 host root | 同 S-7.2 | ✅ |
| S-7.4 | 無五站機 | `[ok] S-7.4 no five-station machine` | ✅ |
| S-7.5 | token＋F1 綠 | `[ok] S-7.5 tokens still present`／`F1 battery still green` | ✅ |
| S-7.6 | 本目錄跳不過 | `[ok] S-7.6 this slug cannot auto-advance` | ✅ |
| S-7.7 | NEW5 是合成 | `[ok] S-7.7 NEW5 is synthetic fixture` | ✅ |
| S-8.1 | 預設仍舊 7 | `f3_cut_happened` 假；無 F3 聲明 | ✅ |
| S-8.2 | in-flight 仍舊 7 | OLD7-NO-FIVE 綠 | ✅ |
| S-8.3 | token 仍在 | token 守衛 exit 0 | ✅ |
| S-8.4 | Stage 4 hop 已過 | 不重開 4-spec 頂欄 | ✅ |
| S-8.5 | 檔在不算完 | hollow 探針 | ✅ |
| S-8.6 | F1 綠不算完 | `--only f1` exit 3 | ✅ |
| S-8.7 | Q9–Q24 去向 | G2 Disposition 表仍在 | ✅ |
| S-8.8 | 只 NEW5 非 0 | `--only new5` exit 3 | ✅ |
| S-8.9 | Files＋Budget 0 區塊 | 行為檔 ⊆ 清單；D-1 四檔見 KL | ✅ |

## 截圖槽

本場無產品 UI（F2 = CLI coordinator + 電池）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = 電池 CASE stdout
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F2 是 coordinator／倉／電池，不是現場交接 UI。有 Operational Context 的 S 以「寫手／coordinator 被閘擋住或立刻 hop」走一遍；標不適用的純內部 S 不裝成人員旅程。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.5 | coordinator | 第三次重寫讀倉拒 | persist 第 4 token → refused／Escalated | 不改數字、不口頭放行 | Escalated | 相符 |
| S-3.1 | 採用端寫手 | doctor 綠仍舊 7 | `refuse_hop_reason(..., doctor_green=True)` | 不跟 hops | 無 hop | 理由是路線 |
| S-3.2 | 採用端 | update ≠ cut | marketplace+cache 仍 legacy | 不改線 | — | 相符 |
| S-4.2 | coordinator | 表列真立刻 hop | evaluate_hop I/D/Sp/Bu | 中間不簽 | 不停 | hop 發生 |
| S-4.3 | 寫手 | 假謂詞就修檔 | PRED-STOP `why=Sp2` | 補觀測欄 | 停 Spec | 無人句 |
| S-4.5 | Ship 審查者 | 出貨仍由人寫頂欄 | 注入 Done＝紅格 | 人寫 PASS | HumanWait | 機械 Done 被抓 |
| S-4.6 | coordinator | 中間不等 | 注入等人句＝紅格 | 刪問人句 | 中間不停 | 紅 |
| S-4.15 | 寫手 | Intake 表列真就進 Decide | `--hop I` | 不在 Intake 簽 | 中間不停 | from-to 對 |
| S-4.17 | coordinator | 無 trigger 不產 Demo | `--hop Sp` | 不補假 Demo | 不 latch | 無 proto |
| S-4.18 | Demo 參與者 | 未核不得離 Spec | `--hop Sp5b` | 人親填 attestation | HumanWait | 相符 |
| S-6.1 | 寫手 | 缺 Verify 不得 hop | M11 overlay | 補四欄 | 停 Build | `why=M11` |
| S-7.2 | 兩台機器寫手 | 不得遠端改線 | cache 旗標丟棄 | 各機自己 update | — | 路仍舊 7 |
| S-8.9 | Stage 5 寫手 | 只施工 F2 scripts | Files 聯集 | F3 另開 slug | — | 行為檔閉；D-1 見 KL |
| 其餘 S | — | — | — | — | — | 不適用（計數／檔集／表完整性／極性索引） |

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec ⑦⑧⑨⑪）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中 🔴。`five_station_f1.py:328-331` 函式內 lazy import `five_station_f2.caps_near`＝S-8.9 准許的 RP 讀倉最小接線；`f1_check` 反呼 F1 是電池回歸。不是 event bus 暗改路線。
2. **資料所有權被繞過寫入**:未命中。cap 正本在 `docs/dev/<slug>/.five-station/store`；`persist` 拒 run 級路徑。OLD7 合法路徑不建五站機。
3. **相容性破壞包成新增**:未命中。契約仍 2.0.x；無新公開 doctor API；鍵名 OPEN。
4. **一致性邊界被拆解**:未命中。`goal_reopen` 兩計數同一次 `save_store`（S-1.9）。
5. **宣告的 Test seam 未被使用**:未命中。seam = 單一入口 `test-five-station-f2.sh` + 官方 CASE 名 + `--only` exit 3；電池走同一 `persist`／`evaluate_hop`。
6. **Known design limit 被實作悄悄「解決」**:未命中。doctor 綠陷阱仍在現場（約束，不修 doctor）。`f3_cut_happened` 恆假＝誠實「F2 從不切」，不是假裝已 F3。D-1 是 CI 註冊，不是把 S-8.9 默改成已解決。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更把 R/S／資料所有權／公開 Interface 改掉。

- F-c-1 🟡 `#346` 准許清單外四檔（`check-file-map.sh`、`test-architecture-guards.sh`、`devflow-check.sh`、`guides/guide-dev-flow.html` 檔案地圖列） | 4-spec L1004「超出 → L2」與 S-8.9 字面張力 | 作者記 **D-1(L1)**：host CI 註冊，不是 F3 cut。R1 CHALLENGE 留檔；RR1／RR2 CONCUR L1。本場獨立再評：**仍 L1／🟡**，不升 🔴（未切預設路線、未刪 token、未改 graph）。Human 必須決定接受／park 或回 G2。見 KL #1
- F-c-2 🟡 fixture 實得 63 檔 > Stage 4 估 ≤12 | 估計超支 | **D-2(L1)**。5-tasks T-8 已寫 16 份 must-keep。不動 R/S。見 KL #2
- F-c-3 🟡 `5-tasks.md` frontmatter `status: approved` 而 checkbox 全未勾 | 看起來像任務已核 | **D-3(L1)**：N1-arm／graph P0 only，不是勾 T、不是 G3。見 KL #3
- F-c-4 🟡 `scripts/five_station_f2.py` `wc -l` = 1158 > Diff Budget coordinator ≤600 | 行數超估 | 作者未另立 D-n。本場記 🟡：單一家族、不拆第二檔（會撞 ≤4 檔格）。不改 R/S。不升 L2
- F-c-5 🟢 doctor-route 第 4 格 CASE 名掛 `NEW5-Q12-ZERO` | 名與 S-3.6 內容不符 | T-5 殘項；極性仍綠。不另開 🔴
- F-c-6 🟢 `evaluate_hop(..., inject=)` 直接寫壞狀態 | 紅格是餵壞行為 | 與 S-4.8 同一測法契約；合法拒走 `must-keep` overlay
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。D-1 四檔 = documented L1 CI 地板，不進 5-tasks Files 正文

## Spec Axis

逐 R。Deviations D-1／D-2／D-3 如實。無隱藏 L2。**不把本檔寫成 R 已 Human 核准。**

| R | 判定 | 證據 |
|---|---|---|
| R-1 | 符合（本場機械） | S-1.1…S-1.12 親跑 ✅；RP-9／10／11 讀倉；第一次 persist＝0 |
| R-2 | 符合 | S-2.1…S-2.7；七 stem 紅；無 graph.yaml |
| R-3 | 符合 | S-3.1…S-3.6；doctor 綠≠hop；F1 文案牙仍紅 |
| R-4 | 符合 | 18 CASE；hollow exit 3；PRED-STOP `Sp2`；注入四紅格 |
| R-5 | 符合 | events 三類；不 bump schema；鍵名 OPEN |
| R-6 | 符合 | must-keep 16 拒；三失敗獨立紅；Ship 無自動 Done |
| R-7 | 符合 | 三前置缺 → legacy；本目錄／OLD7 不建五站機；NEW5 合成 |
| R-8 | **機械符合＋D-1 張力** | 三把鎖仍 Out。S-8.4／S-8.7 gate 不重開。S-8.9 行為檔閉；D-1 四檔是 L1 不是 F3。F3 未做 |
| D-1(L1) | 如實；Human 未 park | 四檔具名。本場 CONCUR L1（理由同 RR2：CI 註冊）。R1 CHALLENGE 不刪 |
| D-2(L1) | 如實 | 63 vs ≤12 估計 |
| D-3(L1) | 如實 | approved＝N1-arm |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit |

## 變更架構圖

必須對上 #346／#349 basename。本 PR 只加 `7-review.md`／`7-review.html`。

```text
[test-five-station-f2.sh] --exec--> [five_station_f2.py]
        |                              |
        |                              +-- persist / store_path
        |                              |     docs/dev/<slug>/.five-station/store
        |                              +-- evaluate_hop / allow_legacy
        |                              +-- Battery OFFICIAL 18 CASE
        |                              +-- f1_check --> five_station_f1.py
        |                                    caps_from_store (RP-9/10/11)
        v
[fixtures/five-station-f2/new5/]   [fixtures/five-station-f2/old7/]
        q12 / hop-ok / pred-stop / must-keep×16 / inject-*
--only new5|old7|f1  --> exit 3
未知旗標             --> exit 2
NEW5+OLD7 全綠       --> exit 0
```

D-1 守衛（非圖上模組）：`check-file-map.sh` 210、`devflow-check.sh` 註冊 F2 電池、`test-architecture-guards.sh` 靜態釘、`guides/guide-dev-flow.html` 檔案地圖列。

## Diff(merge-base(develop)..HEAD,逐檔折疊)

本 review hop 對 `858336e` 只將新增下列兩檔（產品碼已在 main，不重貼 #346／#349 全文）：

<details>
<summary title="+本檔; Stage7-C draft"><code>docs/dev/five-station-f2/7-review.md</code></summary>
<pre>Stage7-C 審查草稿。verdict=PRE-REVIEW。status=draft。不是 G3 PASS。</pre>
</details>

<details>
<summary title="產器 Twin"><code>docs/dev/five-station-f2/7-review.html</code></summary>
<pre>scripts/build-stage7-html.py --action 產出。不手包 html-shell。</pre>
</details>

產品樹（已合 main，本場審核對象，不在本 PR 重改）：

<details>
<summary title="+1158; coordinator+電池"><code>scripts/five_station_f2.py</code></summary>
<pre><span class="add">+HOPS / OFFICIAL 18 / persist / goal_reopen / evaluate_hop / Battery</span></pre>
</details>

<details>
<summary title="+15; 單一入口"><code>scripts/test-five-station-f2.sh</code></summary>
<pre><span class="add">+exec python3 five_station_f2.py --root "$ROOT" "$@"</span></pre>
</details>

<details>
<summary title="+14; RP 讀倉"><code>scripts/five_station_f1.py</code></summary>
<pre><span class="add">+caps_from_store → five_station_f2.caps_near</span></pre>
</details>

<details>
<summary title="fixtures"><code>scripts/fixtures/five-station-f2/**</code></summary>
<pre>new5／old7／must-keep×16／hop-ok／pred-stop／inject-*。完整 diff 在 #346／#349。</pre>
</details>

<details>
<summary title="D-1 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code> · <code>guides/guide-dev-flow.html</code></summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 208</span>
<span class="add">+EXPECTED_MAPPED_FILES = 210</span>
<span class="add">+architecture/test-five-station-f2</span></pre>
</details>

## Verdict

**不是 G3 PASS。** `verdict: PRE-REVIEW`。`status: draft`。Human 未簽。Writer C 不代填 PASS／REQUEST_CHANGES／HOLD。

機械面（本場親跑 @ `858336e`）對得上金標：4-spec G2 PASS；5-tasks T-1…T-10 在（checkbox 未勾＝D-3 誠實）；RR1／RR2 各 10/10 ACCEPTED；電池 exit 0；hollow 三探針 exit 3；L1 D-1／D-2／D-3 如實；刀口只 F2。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 F2 S 全綠 | Coverage 70 列 ✅；18 CASE failed=0；must-keep 16 | Writer C 實跑；**Human 未簽** |
| 既有回歸綠 | spec-gate 9/9；token 全過；F1 failed=0；file-map 210 | Writer C 實跑；**Human 未簽** |
| 現象證據逐 S | 上表＋附錄 A4 | 親跑電池；**Human 未簽** |
| Evidence 契約 | 本節四欄＋層表；gauntlet 見附錄 A5 | 機械面交給本檔；**不得當成 Human PASS** |
| 無 🔴 | 無產品行為 🔴；F-c-1…F-c-4 皆 🟡＝D-n／行數 | Human 必須看 KL #1（D-1 張力） |
| F3 | 明確未做 | 不得當五站已切 |
| Human G3 | **未簽** | 本欄空白 ≠ PASS |

- G3 | 2026-09-14 | Writer C 只交 draft。未發明 Human G3 PASS。reviewers 空。頂欄 PRE-REVIEW。Source SHA 產品樹 `858336e9441cec636549b3dc2d35ef273e03794f`。不開 F3。STATUS 另 companion。

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 `FORK_INTEGRATION_SHA=56c8019c1058c375755ca03944140f79ff8bbe55`（6-notes 步 0）。產品已合 main。

本 review hop 從 latest main 再開：`--fork-sha 858336e9441cec636549b3dc2d35ef273e03794f`（= 開工 HEAD = `origin/main`）。

```
STATUS: N_A_NO_INCOMING
FORK_INTEGRATION_SHA: 858336e9441cec636549b3dc2d35ef273e03794f
FEATURE_HEAD: 858336e9441cec636549b3dc2d35ef273e03794f
INTEGRATION_SHA: 858336e9441cec636549b3dc2d35ef273e03794f
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=N_A_NO_INCOMING FORK=858336e9441cec636549b3dc2d35ef273e03794f HEAD=858336e9441cec636549b3dc2d35ef273e03794f INTEGRATION=858336e9441cec636549b3dc2d35ef273e03794f(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

若改用 Stage 6 錨 `56c8019` 重跑，預期 `ALREADY_SYNCED`（產品已合）——該輸出不算「無共同戰場」。路徑①：Final Fresh 綁當下產品 HEAD `858336e`。本 hop **不 merge、不改產品碼**。共同戰場 = #346／#349 本身，已當審核對象逐檔看過。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | D-1(L1)：#346 改了 S-8.9 准許清單外四檔（file-map 208→210、architecture 釘、`devflow-check` 註冊 F2、guide **檔案地圖列**）。4-spec L1004 寫「超出 → L2」。R1 CHALLENGE；RR1／RR2／本場 CONCUR L1（CI 註冊，不是 F3 cut） | L1／🟡 | **Human 必須接受／park 或回 G2**。落點=本表。owner=rick。本 PR 不拆那四檔、不重開 4-spec（S-8.4） |
| 2 | D-2(L1)：fixture 實得 63 檔（must-keep 16 份）> Stage 4 估 ≤12。不動 R/S | L1／🟡 | park 本表。照 5-tasks 具名路徑；不減 18 CASE |
| 3 | D-3(L1)：`5-tasks.md` `status: approved` 只為 N1-arm／graph P0。checkbox 全未勾。不是 T 完成、不是 G3 | L1／🟡 | 維持未勾。Human 勿把 approved 讀成 shipped |
| 4 | `five_station_f2.py` 1158 行 > Diff Budget ≤600。作者未立 D-n | 🟡 | 告知；不拆第二家族。Human 可 park |
| 5 | F3 新 slug 預設五站未切。`graph.yaml` 未改 | 範圍 | 另刀 F3。本場不宣稱 |
| 6 | doctor 綠陷阱仍在現場（4-spec Known design limit）。本刀不修 doctor | 已知 | 維持約束 |
| 7 | 鍵名／event schema 仍 OPEN | 已知 | 勿當 annex 已核 |
| 8 | 本雲端未武裝 `devflow-exec.sh`；doctor 工具路徑本環境無 `scripts/devflow-doctor.sh` | 環境 | 讀取順序靠散文；token／spec-gate／電池已親跑 |
| 9 | 本檔 `verdict: PRE-REVIEW`。全勾 ≠ PASS。Human 未簽 | 流程 | 等人類提交判定。**不得把本草稿當 G3 PASS** |

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**(契約 `applicable`):無未授權 Boundary 變更把 R/S 改掉。D-1 是 CI 註冊 L1／🟡，**不是**已由 Human park——本項 **不得勾**，直到 owner 明示接受／park（寫下 owner、理由、本表 #1）或回 G2
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:F2 不 bump 契約、不切 `graph.yaml`。Quiz 留給 Human。本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:本 review hop `N_A_NO_INCOMING` 三 SHA＋canonical ref 貼於 Verdict。產品樹 Fresh 綁 `858336e`。Verdict 後禁改產品碼。本 hop **不 merge**
- [ ] PR → main:本 hop 開 Stage7-C draft PR；**禁直上 master**；**禁合併直到 Human G3**
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（F2 不改 living 契約句；F3 才動）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**
- [ ] 7-review frontmatter status: shipped:本 hop 維持 `status: draft` + `verdict: PRE-REVIEW`
- [x] 7-review.html 已產生:`scripts/build-stage7-html.py --action`（抽驗格 S-4.3）
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| Human G3 前 | rick | 本檔 KL #1 D-1 張力；電池仍 exit 0／hollow 仍 3 | 有人把 D-1 當已 G2 默改、或 hollow 不再 3 |
| F3 開工前 | rick | S-8.1…S-8.3；`graph.yaml` 未切 | 預設被寫成五站或 token 被刪 |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本 hop **明確不是 G3 PASS**。
2. **D-1 張力**：4-spec「超出 → L2」vs CI 註冊 L1。R1 CHALLENGE 留檔。本場 CONCUR L1，**不代 Human park**。
3. **Scope**：只 F2。把 F3 cut 或「新 slug 預設五站」當成已交付 = 錯。
4. **2c**：本 review hop `N_A_NO_INCOMING`。不 merge。Fresh 綁產品 `858336e`。
5. **作者 vs 本場**：RR1／RR2 10/10 ACCEPTED 與本場實跑一致（18 CASE、hollow 3、PRED-STOP `Sp2`、must-keep 16）。差異：本場另記 F-c-4 行數 1158＞600（作者未立 D-n）。

### A2　刀口（F2 only）

做了：slug 倉、RP 讀倉、五桶、雙路電池、hollow 探針、Must-keep 16、三把鎖約束。
沒做：F3 cut、改 graph、刪 token、改 doctor 握手、bump 契約、把本目錄當 NEW5、發明 G3 PASS。

### A3　建議 Human 路徑（未走）

1. 開本 PR 審頁（html twin）。
2. 抽驗 S-4.3 三個 `檔:行`。
3. Known Limits #1（D-1）：接受／park 或回 G2。
4. 判定只經頁尾「提交判定」寫頂欄。Agent 禁寫 PASS。
5. 未 Demo／未 Human 簽 = 保持 PRE-REVIEW。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
858336e9441cec636549b3dc2d35ef273e03794f

$ bash scripts/test-five-station-f2.sh -v
=== CASE NEW5-Q12-ZERO
=== CASE NEW5-RUN2
=== CASE NEW5-CAP-3
=== CASE NEW5-STORE-READ
=== CASE NEW5-DECIDE-2
=== CASE NEW5-GOAL-2
=== CASE NEW5-SPEC-SHARE
=== CASE NEW5-BUILD-SHARE
=== CASE NEW5-SEVEN-STEM
=== CASE NEW5-HOP-OK
=== CASE NEW5-PRED-STOP
=== CASE NEW5-MK-RED
=== CASE NEW5-SHIP-MECH
=== CASE NEW5-WAIT-RED
=== CASE OLD7-FOLD-RED
=== CASE OLD7-NO-FIVE
=== CASE OLD7-TOKEN
=== CASE OLD7-SELF
failed=0
exit 0
=== CASE count = 18

$ bash scripts/test-five-station-f2.sh --only new5; echo $?
hollow --only new5
3
$ bash scripts/test-five-station-f2.sh --only old7; echo $?
hollow --only old7
3
$ bash scripts/test-five-station-f2.sh --only f1; echo $?
3
$ bash scripts/test-five-station-f2.sh --only-bogus; echo $?
FATAL: 未知旗標 --only-bogus
2

$ bash scripts/test-five-station-f2.sh --group must-keep -v
=== CASE count = 16; failed=0; exit 0
（M1…M16 各 evaluate_hop refuses）

$ bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md
✅ C1…C9
✅ G2 spec gate:9/9 全過
exit 0

$ bash scripts/check-gate-tokens.sh .
✅ Gate Token 釘死守衛:全過
exit 0

$ bash scripts/test-five-station-f1.sh
failed=0
exit 0

$ bash scripts/check-file-map.sh
table_rows=220
✅ PASS:forward 210
exit 0
```

### A5　Gauntlet

Writer C 於產品樹 `858336e`（本 md 落檔、尚未 docs-commit）親跑：

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f2/7-review.md \
    --source-sha 858336e9441cec636549b3dc2d35ef273e03794f --review-file \
    --require-layer test-five-station-f2 \
    --require-layer test-five-station-f1
✅ evidence gauntlet: 84 checks passed — docs/dev/five-station-f2/7-review.md
exit 0
```

`--require-layer` 只加嚴，不拿掉 4-spec Required（spec-gate／token 檢查）。本 docs commit 會再漂 SHA，不重綁、不發明第二份 Fresh。

`7-review.html`：`scripts/build-stage7-html.py --action docs/dev/five-station-f2/7-review.md`。不手包 html-shell。

### A6　作者對照（N4；矩陣之後才讀）

- Self-Review ①–⑧：18 CASE、未發明 G3、D-1／D-2／D-3 對得上、DBC 未偷偷修 limit —— 與獨立實跑一致。
- RR1／RR2：各 T-1…T-10 ACCEPTED（10/10）。本場抽查 T-4 S-2.5 已無 `or True`；T-6 PRED-STOP `why==Sp2`；T-8 16 overlay 真拒。同意。
- 差異：本場 `wc -l five_station_f2.py` = 1158（Budget ≤600）→ F-c-4 🟡。作者未立 D-n。
- R1 對 D-1 的 CHALLENGE 列保留；本場不塗掉、不自改 4-spec。
- 5-tasks checkbox 仍未勾 —— 與 D-3／RR 紀錄一致。
- 不另存 `7-review-*.md`。
