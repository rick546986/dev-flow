---
feature: five-station-f3
stage: 5-tasks
status: draft
owner: rick
updated: 2026-09-14
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — F3 cut 可見紀錄／讀鍵／graph+dual-read／doctor／三路電池（Writer C 競稿）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、DD-1…DD-10 Owner PASS；main tip `4d0a5b6`／#380，規格 #379／#378 Winner A + standing）。Lane = **full**。本 hop **不 bump** 契約、不改 runtime 碼。
> 原文獨立於 A／B（C 線當時未讀他稿）。**本 hop 只寫任務雙檔**，不落地 `scripts/`、不改 `STATUS.md`／`HISTORY.md`、不改 1–4、不發明 G3、不開 Stage 6。
> Knife = **只 F3 cut**：可見三槽紀錄 + `contract_version()` 只讀正本鍵 + graph 條件邊與 dual-read + doctor 只加 `2.1.0` + **同一 process** NEW5＋OLD7＋TOKEN。**不是**刪 token、**不是**折 in-flight、**不是**本 slug 當白老鼠。
> C 線主軸（仍全覆蓋）：**電池極性**（注入壞行為→該格紅；拒 hop ≠ 紅格綠）＋**freeze／fold**（OLD7／本目錄／f2／simplify 整段舊 7；WAIT-RED／KEEP-MK／KEEP-SHIP-MECH 各自可紅）＋**Non-Goals／Files 准許清單／Diff Budget 0** 同條鎖＋**hollow 探針**特別利（函式真／檔在／只 F2／只用字／兩支腳本各綠／僅 html；`--probe`／`--only` 一等旗標、exit 3 ≠ 用法 exit 2）。
> tracer：T-1 先打通「人指得到三槽、silent True 該格紅」；T-2／T-3 加厚讀縫與三前置；T-4 才切 graph 行為；T-5 doctor 清單；T-6 fold 三紅；T-7 freeze／折線；T-8 六支 hollow；T-9 同一電池 25 CASE + 極性鎖 + Files／0 預算。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。`which_condition` 只命名 cut 位元（例 `f3-cut`），不准寫成三前置 AND，不准把 `F3-cut-happened` 當唯一合法戳記。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-7.3）。F3 入口是**新家族** `scripts/test-five-station-f3.sh`（加 `scripts/five_station_f2.py` 與／或後繼 `scripts/five_station_f3.py` 的 cut 讀端／讀鍵／路線閘；電池 CASE 可同檔）。可選 `scripts/check-five-station-f3.sh` **不是**第四條電池路。
Cut SoT（DD-1）＝獨立檔 `docs/dev/f3-cut-attestation.json` 三槽 `who`／`when`／`which_condition` 皆非空字串。**禁止**寫進 `devflow-contract.json` 當兄弟布林。函式只讀、不寫。
NEW5 fixture 根（DD-3）＝`scripts/fixtures/five-station-f3/new5/`（合成；cut 當下無 1–7 `.md`）。**禁止**本目錄、`five-station-f2`、`five-station-simplify`。
OLD7 fixture 根（DD-4）＝`scripts/fixtures/five-station-f3/old7/`（已有至少一個 1–7 `.md`）。
graph 切換（DD-5）＝`stage2`／`stage4` `graph.yaml` **條件邊** + 路線閘讀**同一**三前置。節點 `N7-g1`／`N6-g2` **不刪**。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
Decision 原 20 列 CASE 只准加；本 hop 承接 20＋standing 加列 5＝**官方 25 名**，減一列＝翻 Decision。發明名不是通過條件。加列不得把「函式真／檔在／F2 綠／用字／兩支腳本各綠／僅 html」加成通過條件。
紅格極性＝**注入該壞行為 → 該格獨立紅**。把「coordinator 拒 hop／拒寫」記成紅格綠＝極性反了，整電池必須非 0（S-5.3）。
`--only new5|old7|token` 與 `--probe hollow-true|hollow-files|hollow-f2|hollow-word|two-script|polarity` 是入口**一等旗標**（必須出現在 `--help`）。`--only`／hollow `--probe`（除 polarity）＝exit **3**（即使那一路本身綠）。`--probe polarity`＝模擬「拒 hop 當紅格綠」→ 入口必須 exit **1**（非整電池 0）。未知旗標／用法錯誤＝exit **2**，**不得**被 `exit≠0` 誤當 hollow 綠。
F2 綠是地板（F3-F2-REGRESS），**不是** SC-BATTERY 第四條 IFF。
本 hop 不發明第一隻活五站名字。不重開 F2 park D-1／D-2／D-3／F-c-4。

### 本 hop 點名對照（Stage 6 才建檔；Verify 必須點到官方 CASE 名＋具名路徑）

| T | 路／CASE | 檔（皆在 `scripts/fixtures/five-station-f3/`，另加 cut 正本） | 紅／綠什麼 |
|---|---|---|---|
| T-1 | ATTEST-VISIBLE | `attest/three-slots.json`（落地後對照 `docs/dev/f3-cut-attestation.json`） | 綠：三槽非空、人指得到、讀端回真；`which_condition` 只命名 cut 位元 |
| T-1 | （S-1.2／S-1.4／S-1.5） | `attest/missing-file/`、`attest/empty-slot.json` | 綠義務：缺檔／空槽回假；函式不寫檔；契約檔無 cut 兄弟鍵 |
| T-1 | ATTEST-SILENT-RED | `attest/inject-silent-true.md` | **注入** 只 `return True`、無合格三槽，卻稱已切 → **該格紅** |
| T-2 | READ-SEAM | `pre/read-seam-old-reader/` | **注入** 只 bump 正本、reader 仍讀錯鍵，卻稱已宣告 → **該格紅** |
| T-3 | PRE-210-NE-CUT | `pre/210-ne-cut/` | 綠：2.1.0 真、cut 假 → `allow_legacy()`；理由含字面 `F3 cut 未發生` |
| T-3 | PRE-AND | `pre/and-missing-declared/`、`pre/and-missing-cut/`、`pre/and-missing-inflight/` | 綠：三前置缺一 → legacy；理由對得上缺的那一條 |
| T-3 | PRE-HOPS-200 | `pre/hops-200/` | 綠：2.0.0＋五站 hops 預設 → SLOT-REJECT、未改線 |
| T-4 | NEW5-CUT-OK | `new5/`（零個 1–7 `.md`） | 綠：三前置全真 → 預設五站、不進 `N7-g1`／`N6-g2` |
| T-4 | GRAPH-WORD-NE | `new5/inject-graph-word.md` | **注入** 只改 guide 用字、新 slug 仍停 `N7-g1`，卻標成功 → **該格紅** |
| T-5 | DOCTOR-HONEST | `doctor/honest-no-supported/` | 綠：2.1.0 ∉ supported → `INCOMPATIBLE`、非 exit 0 |
| T-5 | DOCTOR-NE-TICKET | `doctor/compatible-still-old7.md` | 綠：`COMPATIBLE`＋2.0.0 求五站 hop → 拒；理由是路線，不含「doctor 已綠」 |
| T-6 | NEW5-WAIT-RED | `new5/inject-wait-red.md` | **注入** 謂詞真、latch 假，仍例行停 `N7-g1`／留下「要不要繼續」→ **該格紅** |
| T-6 | KEEP-MK-RED | `new5/inject-mk-red.md` | **注入** Must-keep 任一紅仍 hop（例 M3／M5／M9／M11／M12／M15）→ **該格紅**；只擋 M11＝本格紅 |
| T-6 | KEEP-SHIP-MECH | `new5/inject-ship-mech.md` | **注入** 機械全綠、無人寫 `verdict: PASS` 卻標 Ship Done → **該格紅** |
| T-7 | OLD7-FREEZE | `old7/`（已有 1–7 `.md`） | 綠：整段舊 7；無五站狀態；三 cap 不套 |
| T-7 | OLD7-FOLD-RED | `old7/inject-fold-red.md` | **注入** 對 in-flight 寫五站狀態／五站 hop → **該格紅** |
| T-7 | SELF-OLD7 | `old7/`＋本目錄／`five-station-f2`／`five-station-simplify` 只讀探 | 綠：對上述求五站自動前進跳不過 |
| T-8 | HOLLOW-TRUE | `hollow/inject-true.md` | **注入** 把 `f3_cut_happened==True` 標成 F3 綠 → **該格紅**；`--probe hollow-true` exit 3 |
| T-8 | HOLLOW-FILES | `hollow/inject-files.md` | **注入** 把「檔在」標成 F3 綠 → **該格紅**；`--probe hollow-files` exit 3 |
| T-8 | HOLLOW-F2 | `hollow/inject-f2.md` | **注入** 只跑 F2 電池綠就標 F3 綠 → **該格紅**；`--probe hollow-f2` exit 3 |
| T-8 | HOLLOW-WORD | `hollow/inject-word.md` | **注入** 只用字標 F3 綠 → **該格獨立紅**（不是 GRAPH-WORD-NE 附註）；`--probe hollow-word` exit 3 |
| T-8 | HOLLOW-TWO-SCRIPT | `hollow/inject-two-script.md` | **注入** 兩支腳本各綠一次就標同一電池綠 → **該格紅**；`--probe two-script` exit 3 |
| T-8 | HOLLOW-HTML-NE-GWT | `old7/html-only/`（只有 `*.html`、零個 1–7 `.md`） | 綠：`has_old7` 假；僅 html ≠ in-flight GWT |
| T-9 | TOKEN-KEEP | （呼叫既有 token 牙，不改） | 綠：`check-gate-tokens.sh` exit 0；G1／G2／`ACCEPTED` 仍在 |
| T-9 | TOKEN-DEL-RED | `token/inject-del.md` | **注入** 刪 token 卻標 F3 成功 → **該格紅** |
| T-9 | F3-F2-REGRESS | （呼叫既有 F2 電池，不改） | 綠：`test-five-station-f2.sh` exit 0 且 `failed=0`；**不是**第四路 IFF |
| T-9 | SC-BATTERY | `new5/` + `old7/` + TOKEN | 單一 process 三路都過才 exit 0；`--only new5|old7|token` 各 exit 3；`--probe polarity` exit 1 |

官方 25 名＝Decision 原 20＋standing 5：NEW5-CUT-OK、NEW5-WAIT-RED、OLD7-FREEZE、OLD7-FOLD-RED、TOKEN-KEEP、TOKEN-DEL-RED、ATTEST-VISIBLE、ATTEST-SILENT-RED、PRE-210-NE-CUT、PRE-HOPS-200、READ-SEAM、DOCTOR-HONEST、DOCTOR-NE-TICKET、GRAPH-WORD-NE、SELF-OLD7、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、KEEP-MK-RED、KEEP-SHIP-MECH、PRE-AND、F3-F2-REGRESS、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT。`--group`／`--probe` 印出的 `=== CASE` 名詞也必須落在這 25 名內。

### N1 R/S 盤點（49 S；49／49 皆被至少一個 T 的 Covers 承接）

| R | F3 必須落地的 S | 本 hop T |
|---|---|---|
| R-1 | S-1.1、S-1.2、S-1.3、S-1.4、S-1.5、S-1.6 | T-1 |
| R-2 | S-2.1、S-2.2、S-2.3 | T-2 |
| R-2 | S-2.4、S-2.5、S-2.6、S-2.7 | T-3 |
| R-3 | S-3.1、S-3.2、S-3.3、S-3.5、S-3.6 | T-4 |
| R-4 | S-4.1、S-4.2、S-4.3、S-4.4、S-4.5 | T-5 |
| R-6 | S-6.1、S-6.2、S-6.3 | T-6 |
| R-7／R-3 | S-7.1、S-7.2、S-7.3、S-7.4、S-7.5；S-3.4 | T-7 |
| R-5 | S-5.4、S-5.5、S-5.6、S-5.9、S-5.10、S-5.11 | T-8 |
| R-5／R-8 | S-5.1、S-5.2、S-5.3、S-5.7、S-5.8；S-8.2、S-8.3、S-8.4；S-8.1、S-8.5、S-8.6（Covers gate） | T-9 |

### 已綠／掛 Covers gate（不另開水平抄表 T）

| S | 為什麼不另開 T | 去向 |
|---|---|---|
| S-8.1 | 本條是 Stage 4 hop 檔集（當時只 4-spec 雙檔、draft、無 G2 PASS）。G2 已過。不是 Stage 6 工作 | T-9 Covers gate one-liner。不准重開、不准改 4-spec 頂欄、不准把本 hop 再填 PASS |
| S-8.5 | Q15–Q27 去向已在 4-spec Real-world Disposition | T-9 Covers gate one-liner。後站不得把任一 Q 標可選／消失 |
| S-8.6 | F2 park D-1／D-2／D-3／F-c-4 已封；本刀 In 不得出現 | T-9 Covers gate one-liner。不准改 `docs/dev/five-station-f2/` 已封 R／S |

### F3 Files 准許清單（S-8.2 可核；禁區 Diff Budget 0 寫在同一條）

Stage 6 全部 T 的 Files 聯集只准（可少用、不可超）：

- `guides/guide-dev-flow.html`（七站單行 → 五站用語；≠ SoT）
- `devflow-contract.json`（**只** bump `devflow_contract_version`→`2.1.0`）
- `hooks/runtime-capabilities.json`（**只**加 `2.1.0`）
- `skills/dev-flow/stage2/graph.yaml`、`skills/dev-flow/stage4/graph.yaml`（條件邊；節點檔不刪）
- `scripts/five_station_f2.py` 與／或 `scripts/five_station_f3.py`（讀鍵＋cut 讀端＋路線閘）
- `docs/dev/f3-cut-attestation.json`
- `scripts/test-five-station-f3.sh`（單一電池入口；每個跑 F3 Verify 的 T 必列）
- `scripts/check-five-station-f3.sh`（可選；有也不構成第四條電池路）
- `scripts/fixtures/five-station-f3/`（含上表具名路徑；Stage 6 才建檔）
- 本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html

下列區塊 Diff Budget **必須＝0**，否則 S-8.2／S-8.3 紅：`_templates/` Stage 1–4 正文；`hooks/_doctor_impl.py` 握手語意；`docs/dev/STATUS.md`／`HISTORY.md`（看板另 companion）；把本目錄當 NEW5 fixture；刪 G1／G2／`ACCEPTED` token 檔；重開 F2 park D-1／D-2／D-3／F-c-4；改 `docs/dev/five-station-f2/` 已封 R／S。

超出上列 = L2／違 S-8.2。禁把 `_doctor_impl.py`、`STATUS.md`、`HISTORY.md`、`_templates/`、本目錄當 NEW5、token 刪檔、F2 已封稿寫進任一 T 的 Files。F2 電池與 token 牙只准呼叫。

### Verify 開工前原樣跑（2026-09-14；F3 電池尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-9 | `scripts/test-five-station-f3.sh` 不存在 → 非零 | ③綠不了但方向對 |

## T-1 打通可見三槽 cut 紀錄且 silent True 該格紅
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4, S-1.5, S-1.6
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, docs/dev/f3-cut-attestation.json, scripts/fixtures/five-station-f3/attest/
- Verify: `test -d scripts/fixtures/five-station-f3/attest && n=$(bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --case ATTEST-SILENT-RED -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 2 && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --case ATTEST-SILENT-RED`
- Blocked-by: —
- Risk: high
- Intent: 日常有人要宣稱「F3 已切」，必須先在獨立檔留下誰／何時／切哪個位元，打開檔案就能指到三個非空槽；讀函式回真的依據是這份檔，不是函式裡寫死 True。檔不在或任一槽空，讀端必須回假，契約已是 2.1.0 或 guide 已寫「五站」也救不了。有人只把函式改成 return True、檔卻缺，電池 ATTEST-SILENT-RED 那一格必須自己紅，不得把「函式回真」記成該格綠。改的是 cut 紀錄檔與只讀函式，試體在 `attest/`，不是把 cut 塞進契約 JSON、不是用 git blame 冒充誰／何時。不會變成 silent 空切、不會把 declare／in-flight 捆進 `which_condition`、不會讓本 T 去切 graph 或 bump 契約。
- Boundaries: 准改模組＝cut 紀錄檔 + `f3_cut_happened` 讀端 + 電池入口骨架 + 具名 attest fixture。Data owner＝寫入該檔的人類。SoT 路徑＝`docs/dev/f3-cut-attestation.json`（DD-1）。Interface＝讀三槽 → bool；缺檔／空槽 → False；函式不建立、不覆寫、不刪該檔。`which_condition` 只命名 cut 位元（例 `f3-cut`）；禁止三前置 AND；禁止字面 `F3-cut-happened` 當唯一合法戳記。Forbidden＝契約兄弟布林、blame／STATUS／guide 用語當 SoT、本 T 改 `graph.yaml`／doctor／token、拿本目錄當 NEW5。Test seam＝換 fixture 根可注入缺檔／空槽／silent True。S-1.6 用語切是交付物但仍 ≠ 成功充分條件；本 T 不改 STATUS。

## T-2 讓正本鍵宣告可讀且只 bump 不修 reader 該格紅
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/pre/read-seam-old-reader/
- Verify: `test -d scripts/fixtures/five-station-f3/pre/read-seam-old-reader && n=$(bash scripts/test-five-station-f3.sh --case READ-SEAM -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f3.sh --case READ-SEAM`
- Blocked-by: T-1
- Intent: 日常打開本樹契約，落地後的版本讀函式必須回 `2.0.0`（或之後的正本鍵值），不准再去翻 `version`／`contract_version` 兩個錯鍵、也不准因此回空字串。有人只把正本鍵改成 2.1.0、reader 卻仍讀錯鍵，卻嘴上說「已宣告」，電池 READ-SEAM 那一格必須自己紅，`declared` 仍假。正本鍵真的是 2.1.0 且 reader 已修，`declared` 才真——這仍不是 cut。改的是讀鍵，試體是 `pre/read-seam-old-reader/`，不是 bump 當 cut、不是本 T 改 hops 預設。不會變成錯鍵 fallback、不會讓 2.1.0 單獨冒充已切。
- Boundaries: 准改模組＝`contract_version()` 讀徑 + READ-SEAM 具名 fixture。Data owner＝`devflow-contract.json` 的 `devflow_contract_version`。Allowed＝只讀正本鍵。Forbidden＝`version`／`contract_version` fallback、本 T 把 cut 寫進契約檔、本 T 改 hops／graph、把 `declared` 真寫成 cut 真。Interface＝正本鍵以 `2.1` 開頭 → `declared` 真；cut 位元仍獨立。Test seam＝假契約檔：正本已 2.1.0、reader 仍舊。本 T 不評三前置 AND（屬 T-3）。

## T-3 讓三前置缺一仍舊 7 且 2.0.0 加五站 hops 被拒
- [ ] 未完成
- Covers: R-2 / S-2.4, S-2.5, S-2.6, S-2.7
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/pre/
- Verify: `test -d scripts/fixtures/five-station-f3/pre/210-ne-cut && test -d scripts/fixtures/five-station-f3/pre/hops-200 && n=$(bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT --case PRE-AND --case PRE-HOPS-200 -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT --case PRE-AND --case PRE-HOPS-200`
- Blocked-by: T-2
- Intent: 日常契約已經 2.1.0、目錄也還沒有站檔，只要 cut 紀錄缺，求五站必須仍走舊 7，拒絕理由要看得到「F3 cut 未發生」，不准寫「已宣告所以切了」。三條前置少一條都一樣——缺宣告理由含「路線未宣告」或「仍舊 7」，缺 ¬in-flight 理由含「in-flight」，缺 cut 理由含「F3 cut 未發生」。有人契約還停在 2.0.0 就把 hops 預設當五站，必須 SLOT-REJECT，路線不得改；marketplace／cache 換了 hops 也不算。hops 預設五站不得早於 2.1.0 已宣告，必須同刀或宣告在先。改的是路線閘三前置，試體在 `pre/` 四組缺一／hops-200，不是本 T 去改 graph 邊、不是 doctor 綠當票。不會變成 2.1.0 當 cut、不會遠端改線。
- Boundaries: 准改模組＝路線閘 `allow_legacy`／`refuse_hop_reason` + 上列五份具名 pre fixture。三前置＝`declared` ∧ ¬in-flight ∧ cut；缺一 → legacy。Forbidden＝把 bump 當 cut、marketplace／cache 當第四前置、只切 graph 契約仍 2.0.0 卻放行、本 T 刪 `N7-g1`。Interface＝拒因字面分缺哪一條；2.0.0＋五站 hops＝SLOT-REJECT、未改線。Idempotency：同一三前置重複評必須同一答案。本 T 結束時不得單邊改 `graph.yaml` 預設跳過（與宣告同刀屬 T-4）。Test seam＝三組缺一 fixture + hops-200 假樹。

## T-4 讓 cut 後新 slug 預設五站且只改用字該格紅
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.5, S-3.6
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, skills/dev-flow/stage2/graph.yaml, skills/dev-flow/stage4/graph.yaml, guides/guide-dev-flow.html, scripts/fixtures/five-station-f3/new5/
- Verify: `test -d scripts/fixtures/five-station-f3/new5 && n=$(bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK --case GRAPH-WORD-NE -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 2 && bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK --case GRAPH-WORD-NE`
- Blocked-by: T-3
- Risk: high
- Intent: 日常 cut 之後才開、目錄裡還沒有任何 1–7 站檔的新 slug，預設必須走五站，中間不准再停下來等人審例行 G1／G2，也不准再進 `N7-g1`／`N6-g2` 當例行停點。契約還是 2.0.0 的採用端，即使 graph 檔已經寫了條件邊，仍必須舊 7，條件邊的「跳過」側不得生效。路線閘與條件邊對同一組三前置必須給同一答案，不准出現一邊已跳過、一邊仍 legacy。有人只把 guide 改成「五站」、新 slug 卻仍停在 `N7-g1`，卻標 F3 成功，GRAPH-WORD-NE 那一格必須自己紅。改的是條件邊＋同一謂詞的路線閘，試體是合成 `new5/`，不是刪節點、不是只翻函式留例行停（3D）。不會變成用語切、不會未宣告就被改線、不會本 T 刪 token。
- Boundaries: 准改模組＝`stage2`／`stage4` `graph.yaml` 條件邊 + 路線閘 + guide 七站單行用語 + NEW5 合成根。機制形＝條件邊＋路線閘（DD-5）；兩邊讀同一三前置（S-3.5）。Forbidden＝刪 `N7-g1.md`／`N6-g2.md`、只 hop-skip、只改用字當成功、未宣告就跳過、拿本目錄當 NEW5、marketplace 單獨改線。Data owner＝各站 graph + 專案樹契約／cut／該 slug 1–7 `.md`。Compatibility＝節點檔保留。guide 用語是交付物 ≠ SoT ≠ GRAPH-WORD-NE 綠條件。本 T 不測 fold 三紅（屬 T-6）、不測 in-flight freeze（屬 T-7）。

## T-5 讓 2.1.0 進 supported 且 doctor 綠當不成路條
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, hooks/runtime-capabilities.json, devflow-contract.json, scripts/fixtures/five-station-f3/doctor/
- Verify: `test -d scripts/fixtures/five-station-f3/doctor && n=$(bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST --case DOCTOR-NE-TICKET -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 2 && bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST --case DOCTOR-NE-TICKET`
- Blocked-by: T-4
- Intent: 日常契約 bump 到 2.1.0 的同一刀，supported 清單必須出現字面 `2.1.0`；漏了，doctor 要印 INCOMPATIBLE 且非 0，不准為了好看改成 COMPATIBLE。現況 doctor 對 2.0.0 可以 COMPATIBLE／exit 0，有人拿這次綠當 cut 或求五站 hop，必須拒絕，理由是路線（未宣告／仍舊 7／F3 cut 未發生），不准寫「doctor 已綠所以可 hop」。只證明 marketplace 或 plugin cache 已有五站 hops，仍舊 7——那不是第四條前置。改的是 supported 清單與路線閘丟棄 doctor 綠，試體在 `doctor/`，不是改握手實作、不是出貨態故意 doctor 紅。不會變成 4B／4C（綠變 ticket 或放寬握手）。
- Boundaries: 准改模組＝`hooks/runtime-capabilities.json` 的 `supported_contract_versions`（只加 `2.1.0`）+ 契約正本鍵 bump（只 `devflow_contract_version`）+ 路線閘丟棄 doctor 綠 + 具名 doctor fixture。Forbidden＝改 `hooks/_doctor_impl.py` 握手語意（版本 ∈ supported 才 COMPATIBLE）、放寬 2.1.0 ∉ supported 仍綠、把綠定義改成「路線 OK／已切」、marketplace／cache 當 cut 或路條、把 `_doctor_impl.py` 列入 Files。握手語意 Diff Budget＝0。doctor 綠只證明握手。本 T 可呼叫既有 `devflow-doctor.sh`，不准改它的握手檔。

## T-6 注入例行停／Must-keep 紅仍 hop／機械 Ship 讓該格獨立紅
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.2, S-6.3
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/inject-wait-red.md, scripts/fixtures/five-station-f3/new5/inject-mk-red.md, scripts/fixtures/five-station-f3/new5/inject-ship-mech.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/inject-wait-red.md && test -f scripts/fixtures/five-station-f3/new5/inject-mk-red.md && test -f scripts/fixtures/five-station-f3/new5/inject-ship-mech.md && n=$(bash scripts/test-five-station-f3.sh --case NEW5-WAIT-RED --case KEEP-MK-RED --case KEEP-SHIP-MECH -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case NEW5-WAIT-RED --case KEEP-MK-RED --case KEEP-SHIP-MECH`
- Blocked-by: T-5
- Risk: high
- Intent: 日常電池必須能**餵壞行為**讓三格各自紅，而且不得因「已經 cut 了」變綠。謂詞已真、latch 仍假，卻還例行走進 `N7-g1` 或留下「要不要繼續／請人審」（`inject-wait-red.md`）→ NEW5-WAIT-RED 該格紅。Must-keep 任一條已經紅（具名例：M3 缺觀測欄、M5 代填 ACCEPTED、M9 Files 超出聯集、M11 缺 Verify、M12 reviewer＝implementer、M15 token 被刪）卻仍 hop，還用「已經 cut 了」當理由（`inject-mk-red.md`）→ KEEP-MK-RED 該格紅；只擋 M11、其餘 M 紅仍 hop＝本格紅。機械全綠、7-review 頂欄沒有人寫 `verdict: PASS`，卻標 Ship Done（`inject-ship-mech.md`）→ KEEP-SHIP-MECH 該格紅。把「coordinator 拒 hop／拒寫」標成這些紅格綠＝極性反了，整電池必須非 0。三失敗不得互抵銷。改的是 fold 紅格測法，不是把完整度摺掉、不是讓機械自己 Ship。不會變成 hollow（那是 T-8）、不會本 T 去折 in-flight（那是 T-7）。
- Boundaries: 准改模組＝F3 電池 fold／keep CASE 跑者 + 上列三張具名注入稿。摺的是新 slug 例行 `N7-g1`／`N6-g2`，不是 Must-keep、不是 Ship 唯人。Test seam＝各 CASE 獨立 exit；紅格只接受注入壞行為的紅。Forbidden＝極性反了仍標 F3 成功、用 cut 省略 Must-keep、只測 M11 當完整 KEEP-MK、Ship 自動 Done、Agent 代填 PASS。Error／State seam＝注入等人句／M 紅仍 hop／頂欄空白卻 Done。本 T 不跑六支 hollow（屬 T-8）、不跑完整 25 格（屬 T-9）、不對 OLD7 寫五站（屬 T-7）。

## T-7 凍結已有站檔的 slug 且對 in-flight 寫五站該格紅
- [ ] 未完成
- Covers: R-7 / S-7.1, S-7.2, S-7.3, S-7.4, S-7.5; R-3 / S-3.4
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/old7/
- Verify: `test -d scripts/fixtures/five-station-f3/old7 && n=$(bash scripts/test-five-station-f3.sh --case OLD7-FREEZE --case OLD7-FOLD-RED --case SELF-OLD7 -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case OLD7-FREEZE --case OLD7-FOLD-RED --case SELF-OLD7`
- Blocked-by: T-6
- Risk: high
- Intent: 日常已經有任一 1–7 `.md` 的 slug（`old7/`）必須整段走完舊 7：例行 G1／條件 S3／G2／G3 都還在，目錄不准被寫入五站狀態，三 cap 不套。有人對這種目錄注入五站狀態或五站 hop（`old7/inject-fold-red.md`），OLD7-FOLD-RED 該格必須自己紅；把「清回舊 7／拒寫」記成此格綠＝極性反了。對 `docs/dev/five-station-f3/`、`docs/dev/five-station-f2/`、`docs/dev/five-station-simplify/` 求五站自動前進必須跳不過，本目錄出貨路徑仍舊 7。NEW5 試體根只能是合成 `scripts/fixtures/five-station-f3/new5/`，或一個 cut **之後**才開、cut 當下沒有 1–7 `.md` 的 slug——不准發明「第一隻活五站」名字當已核目標。節點 `N7-g1`／`N6-g2` 與 token 檔必須仍在。改的是 freeze／自保與折線紅格，不是把 in-flight 折成五站、不是拿本 slug 當白老鼠。不會變成對 live 建五站機。
- Boundaries: 准改模組＝路線閘對 in-flight／本目錄／f2／simplify 的拒 + OLD7 fixture 根 + 折線注入稿。NEW5 試體＝DD-3 合成根。Forbidden＝本目錄／f2／simplify 當 NEW5、對 OLD7 寫五站狀態當綠格義務、刪 `N7-g1`／`N6-g2`、發明活五站 slug 名、把僅 html 當 in-flight（那是 T-8 HOLLOW-HTML-NE-GWT）。OLD7-FREEZE 的 Data owner＝OLD7 fixture，不是本目錄 hop 主詞。S-3.4 節點與 token 檔保留：`ls` 仍見節點；token 牙回歸掛 T-9 呼叫、不進本 T Files。本 T 不改 STATUS。

## T-8 讓六支 hollow 探針各自現形且僅 html 不當站檔
- [ ] 未完成
- Covers: R-5 / S-5.4, S-5.5, S-5.6, S-5.9, S-5.10, S-5.11
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/check-five-station-f3.sh, scripts/fixtures/five-station-f3/hollow/, scripts/fixtures/five-station-f3/old7/html-only/
- Verify: `test -d scripts/fixtures/five-station-f3/hollow && test -d scripts/fixtures/five-station-f3/old7/html-only && n=$(bash scripts/test-five-station-f3.sh --case HOLLOW-TRUE --case HOLLOW-FILES --case HOLLOW-F2 --case HOLLOW-WORD --case HOLLOW-TWO-SCRIPT --case HOLLOW-HTML-NE-GWT -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 6 && bash scripts/test-five-station-f3.sh --help 2>&1 | grep -q -- '--probe' && test "$(bash scripts/test-five-station-f3.sh --probe hollow-true >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --probe hollow-files >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --probe hollow-f2 >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --probe hollow-word >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --probe two-script >/dev/null 2>&1; echo $?)" -eq 3 && bash scripts/test-five-station-f3.sh --case HOLLOW-TRUE --case HOLLOW-FILES --case HOLLOW-F2 --case HOLLOW-WORD --case HOLLOW-TWO-SCRIPT --case HOLLOW-HTML-NE-GWT`
- Blocked-by: T-7
- Risk: high
- Intent: 日常有人想用捷徑宣稱 F3 完，六件事必須各自被抓到，不能互當附註。只證明函式回 True（無三路、無可見紀錄）→ HOLLOW-TRUE 紅。只證明 F3 相關檔存在 → HOLLOW-FILES 紅。只跑 F2 電池拿到 exit 0／`failed=0` → HOLLOW-F2 紅。只改 guide／STATUS 用語 → HOLLOW-WORD **獨立**紅（S-3.3 咬的是「graph 仍停卻標成功」；本格咬「只用字＝hollow」）。NEW5 腳本與 OLD7 腳本（或 `test-five-station-f3.sh` 與 `check-five-station-f3.sh`）分開跑各綠一次、沒有單一 process 把三路跑完，卻標 SC-BATTERY 綠 → HOLLOW-TWO-SCRIPT 紅。目錄只有 html twin、一個 1–7 `.md` 都沒有 → `has_old7` 必須假，不准把 html 當成 in-flight 站檔。`--probe` 必須是 `--help` 裡的一等旗標；五支 hollow `--probe` 各須 exit **3**。未知旗標是 exit 2，**不得**被「exit≠0」誤當本探針綠。改的是 hollow 探針與 html-only fixture，不是把 hollow 加成通過條件。不會變成「檔在／F2 綠／用字」當 F3 完。
- Boundaries: 准改模組＝電池 hollow CASE 跑者 + `--probe` 一等旗標 + `hollow/` 五張注入稿 + `old7/html-only/`。Interface＝hollow `--probe` exit 3；用法／未知旗標 exit 2；HOLLOW-HTML-NE-GWT 是綠格義務（`has_old7` 假），不是 exit 3。Forbidden＝用未知旗標非 0 冒充 hollow、把 HOLLOW-WORD 併進 GRAPH-WORD-NE、把兩支腳本各綠當同一電池、把僅 html 當 GWT、把 F2 綠寫進 SC-BATTERY IFF、掃 4-spec／5-tasks markdown 當綠。可選 `check-five-station-f3.sh` 若本 T 用來示範「兩支各綠」，必須列入 Files，且**不得**當第四條電池路。本 T Verify 不含 `--only` 三路（屬 T-9）也不含完整 25 格。

## T-9 收口同一電池 25 CASE、極性鎖與 Files／Diff Budget 0
- [ ] 未完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3, S-5.7, S-5.8; R-8 / S-8.2, S-8.3, S-8.4; S-8.1（gate：Stage 4 hop 雙檔已 G2 綠，不准重開）；S-8.5（gate：Q15–Q27 去向已綠，不得標可選）；S-8.6（gate：F2 park 四項保持 Out）
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/check-five-station-f3.sh, scripts/fixtures/five-station-f3/new5/, scripts/fixtures/five-station-f3/old7/, scripts/fixtures/five-station-f3/token/, docs/dev/five-station-f3/5-tasks.md, docs/dev/five-station-f3/6-implementation-notes.md, docs/dev/five-station-f3/7-review.md
- Verify: `test -d scripts/fixtures/five-station-f3/new5 && test -d scripts/fixtures/five-station-f3/old7 && n=$(bash scripts/test-five-station-f3.sh -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 25 && bash scripts/test-five-station-f3.sh && bash scripts/test-five-station-f3.sh --help 2>&1 | grep -q -- '--only' && test "$(bash scripts/test-five-station-f3.sh --only new5 >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --only old7 >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --only token >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --probe polarity >/dev/null 2>&1; echo $?)" -eq 1 && bash scripts/test-five-station-f2.sh && bash scripts/check-gate-tokens.sh`
- Blocked-by: T-8
- Risk: high
- Intent: 日常宣稱 F3 完，必須是**同一支** `scripts/test-five-station-f3.sh` 在同一 process 把 NEW5 組、OLD7 組、TOKEN 組都跑完才 exit 0。缺一路、跳過一路、入口只 exec／只轉呼叫 `test-five-station-f2.sh`、只證明檔在、只 F2 綠、只用字、兩支腳本各綠 → 整電池非 0。`--only` 必須是 `--help` 裡的一等旗標；`--only new5`／`--only old7`／`--only token` 各須 exit **3**（即使那一路本身綠）。`--probe polarity` 模擬「把拒 hop 記成紅格綠」必須讓入口 exit **1**，不准變成 0，也不准冒充 hollow 的 3。未知旗標是 exit 2。25 個官方 CASE 名都在，原 20 列一格都不能少；F2 電池另跑當地板（exit 0 且 stdout 含 `failed=0`），**不得**寫進 IFF 第四路。token 牙仍綠；有人注入刪 G1／G2／`ACCEPTED` 卻標 F3 成功 → TOKEN-DEL-RED 該格紅。Files 聯集不超出 S-8.2 准許清單；`_templates/`、doctor 握手、STATUS／HISTORY、本目錄當 NEW5、刪 token、重開 F2 park 行數＝0。S-8.1／S-8.5／S-8.6 gate：不准重開已過的 Stage 4 hop 檔集、不准把 Q15–Q27 標可選、不准把 F2 park 四項改成 In。改的是收口對照與鎖，不是順便改 STATUS，也不是掃 markdown 字串當綠。不會變成 hollow F3、不會發明 G3 PASS。
- Boundaries: 准改模組＝電池入口收口（可動上列 impl／fixture／本 slug 過程檔）。Interface＝單一 process 三組都跑完才 0；F2 腳本不是入口；可選 check 不是第四路。`--only` 一等旗標；子集 hollow＝exit 3；極性反了＝exit 1；用法／未知旗標＝exit 2。Forbidden＝F3 完成樹把 in-flight 折成五站、刪 token、重開 F2 park、把 Q 標可選、減 Decision 原 20 列、Files 超出 S-8.2、把 F2 綠寫進 IFF、用 python 掃 markdown 當 Stage 6 綠、用未知旗標非 0 冒充 hollow、本 hop 改 4-spec 頂欄。Diff Budget 0 區塊命中＝本條紅。token 牙與 F2 電池只呼叫、不准列入「要改的檔」之外的禁區、不准改。禁改 STATUS／HISTORY。本目錄過程檔在清單內 ≠ NEW5 fixture。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-9 單鏈 | Feature Risk high；cut 讀端／讀鍵／閘／graph／電池改同一支 coordinator。Files 重疊時 parallel 會吵 | 4-spec Verification Profile Risk high；C 線 brief「sequential」 | 讓 T-4 與 T-5 平行。棄：graph／契約同刀約束 S-2.7 |
| T-1 選 ATTEST-VISIBLE＋SILENT-RED 當第一刀 | 最薄端到端是「人指得到三槽、空切該格紅」；graph／doctor 是加厚，不是第一刀可觀測主詞 | 4-spec S-1.1／S-1.3；C 線 cut SoT | T-1 先做 NEW5-CUT-OK。棄：還沒有可見紀錄，五站預設是假切 |
| fold 三紅獨立 T-6，freeze／折線獨立 T-7 | C 強調 polarity＋freeze／fold；WAIT／MK／SHIP 是「摺停點不摺完整度」，OLD7 是「已有站檔不准折」。混一 T 會把拒 hop 測成 FOLD-RED 綠 | 4-spec R-6／R-7；S-5.3 極性 | 一 T 兼 fold 與 freeze。棄：測法對調 |
| hollow 六格獨立 T-8，不塞進 T-9 收口 | C 強調探針利；`--probe` exit 3 必須與 `--only` 三路、`--probe polarity` exit 1 分開數。HOLLOW-WORD 必須是獨立格，不是 GRAPH-WORD-NE 附註 | 4-spec S-5.4…S-5.6／S-5.9…S-5.11；standing hollow | 只在 T-9 用 `--only` 冒充六支 hollow。棄：WORD／TWO-SCRIPT／HTML 變附註 |
| `--probe` 一等旗標；hollow＝exit 3；polarity＝exit 1；未知＝exit 2 | 未知旗標 exit≠0 會假綠；拒 hop 當紅格綠必須是電池失敗（1），不是 hollow（3） | 4-spec S-5.3；F2 T-10 standing 吸 C 的 exit 3 慣例 | `! bash --only new5` 靠未知旗標非 0。棄：假綠 |
| 單一檢查家族 `test-five-station-f3`；可選 `check-five-station-f3.sh` 不是第四路 | Diff Budget 入口 1 檔；SC-BATTERY 禁兩支腳本各綠（HOLLOW-TWO-SCRIPT） | 4-spec DD-2；S-5.1／S-5.10 | 每 CASE 一支 sh。棄：hollow 變種 |
| S-8.1／S-8.5／S-8.6 掛 T-9 Covers gate，不另開 T | 49／49 可追；Stage 4 檔集、Disposition、F2 park 已在 G2 綠 | 4-spec S-8.1／S-8.5／S-8.6 | 發明 T-10 重抄 Disposition。棄：水平切帳 |
| TOKEN-KEEP／F3-F2-REGRESS 掛 T-9 呼叫、不進 Files | 既有牙／F2 電池是地板，不是本刀要改的檔；改它們＝越刀 | 4-spec S-5.7／S-5.8；S-8.2 准許清單 | 把 `test-five-station-f2.sh` 列入 Files。棄：F2 綠冒充 F3 |
| 不改 doctor 握手／token／STATUS／`_templates/` | S-8.2 Diff Budget 0；Non-Goals 後站不准改成 In | 4-spec S-4.4／S-8.2／S-8.3／Out of Scope | T-5 順便修 `_doctor_impl.py`。棄：越刀 |
| 不發明活五站名字；NEW5 只用合成根 | Q25／OC-9／S-7.5；本 slug 一有 1–4 就是 in-flight | 4-spec S-7.4／S-7.5 | 在 5-tasks 寫「第一隻活五站＝\<name\>」。棄：X4 |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f3.sh` 不存在 → 九欄皆非零 | 模板 Verify 三律 ③ | 用已綠的 F2 電池當 T-9。棄：違 S-5.6／S-5.7 |
