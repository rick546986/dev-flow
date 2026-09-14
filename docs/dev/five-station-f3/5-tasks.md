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

# 5. 任務 — F3 cut 可見紀錄 + 讀鍵 + graph 條件邊 + 路線閘 + doctor 清單（Writer B 獨立全稿）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、DD-1…DD-10 Owner PASS；main tip `4d0a5b6`／#380，Human G2 `#379`）。Lane = **full**。契約本 hop **不** bump。
> 原文獨立於 A／C（B 線未讀他稿）。**不換 winner**。不吸收尚未存在的他稿。
> 本 hop **只寫任務雙檔**，不落地 `scripts/`／`graph.yaml`／契約／doctor／cut 檔、不改 `STATUS.md`／`HISTORY.md`、不改 1–4、不發明 G3、不開 Stage 6。
> Knife = **只 F3**：可見 cut 紀錄 + `contract_version()` 只讀正本鍵 + graph **條件邊** + 路線閘同一三前置 + doctor **只加** `2.1.0` + 同一電池 NEW5＋OLD7＋TOKEN。**不是**刪 `N7-g1`／`N6-g2`、**不是**改握手、**不是**折 in-flight、**不是**本目錄當白老鼠。
> Scope lock（S-8.2）：Files 聯集只准下面「F3 Files 准許清單」。`_templates/`／doctor 握手／STATUS／HISTORY／本目錄當 NEW5／刪 token／重開 F2 park Diff Budget **＝0**。
> tracer（B 線）：T-1 先打通 **三槽可見且讀端只讀**；T-4 釘路線閘三前置字面；T-5 釘 graph 條件邊＋閘同意＋ dual-read；T-7 釘 doctor `INCOMPATIBLE` 與「綠≠ticket」。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。graph YAML 鍵名不鎖；`which_condition` 只命名 cut 位元，不准寫成三前置 AND，不准把 `F3-cut-happened` 當唯一合法戳記。不發明第一隻活五站名字。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-7.3）。F3 入口是**新家族** `scripts/test-five-station-f3.sh`（可加 `scripts/five_station_f3.py`，或改 `scripts/five_station_f2.py` 讀端／閘；可選 `scripts/check-five-station-f3.sh` **不是**第四條電池路），不是改 `_doctor_impl.py` 握手、不是改 `_templates/`、不是拿本目錄當 NEW5。
cut 路徑（DD-1）：`docs/dev/f3-cut-attestation.json`（獨立檔；三槽 `who`／`when`／`which_condition` 皆非空字串）。**禁止**寫進 `devflow-contract.json` 當版本兄弟布林。函式 `f3_cut_happened()` **只讀**。
NEW5 fixture 根（DD-3）：`scripts/fixtures/five-station-f3/new5/`（合成；不是本目錄、不是 `five-station-f2`、不是 `five-station-simplify`）。
OLD7 fixture 根（DD-4）：`scripts/fixtures/five-station-f3/old7/`（已有 1–7 `.md`）。
graph 切換（DD-5）：`skills/dev-flow/stage2/graph.yaml` 與 `skills/dev-flow/stage4/graph.yaml` **條件邊**（真：跳過例行停；假：仍進 `N7-g1`／`N6-g2`）＋ coordinator 路線閘讀**同一**三前置。節點檔不刪。不是只 hop-skip、不是刪節點。
三前置繼承 F2 4A：`declared` ∧ ¬in-flight ∧ cut。缺一 → `allow_legacy()`。2.1.0 ≠ cut。doctor 綠／marketplace／cache **不是**第四條。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
Decision 原 20 列 CASE 只准加；本 hop 承接 20＋standing 加列 5＝**官方 25 名**，減一列＝翻 Decision。發明名（`NEW5-MKTG-*`／`GRAPH-AGREE-*`／`DOC-OK`）**不是**通過條件。`--group` 印出的 `=== CASE` 名詞必須落在這 25 名內。
紅格極性＝**注入該壞行為 → 該格獨立紅**。把「coordinator 拒 hop／doctor 印 INCOMPATIBLE」記成紅格綠＝極性反了，已拒。
`--only new5|old7|token` 是入口一等旗標（必須出現在 `--help`）。hollow 探針約定 exit **3**。未知旗標／用法錯誤＝exit 2，**不得**被 `exit≠0` 誤當 hollow 綠。
現況地板（本 hop 可跑、≠ F3 完）：`hooks/devflow-doctor.sh` 印 `COMPATIBLE`／exit 0（契約仍 `2.0.0` ∈ supported）；`scripts/test-five-station-f2.sh` exit 0 且 `failed=0`。

### 本 hop 點名對照（Stage 6 才建檔；Verify 必須點到官方 CASE 名＋具名路徑）

| T | 路／CASE | 檔（皆在 `scripts/fixtures/five-station-f3/`，除非另註） | 紅／綠什麼 |
|---|---|---|---|
| T-1 | ATTEST-VISIBLE | `new5/attest-visible/`（內含合格三槽 JSON） | 綠：人指得到 `who`／`when`／`which_condition`；`f3_cut_happened` 回真且只讀這份檔 |
| T-2 | ATTEST-SILENT-RED | `new5/inject-silent-true.md` | **注入** 字面 `return True`、無合格三槽，卻稱已切 → **該格紅** |
| T-3 | READ-SEAM | `new5/inject-read-seam.md` | **注入** 只 bump 正本、reader 仍讀 `version`／`contract_version`，卻稱已宣告 → **該格紅** |
| T-4 | PRE-210-NE-CUT | `new5/pre-210-ne-cut/` | 綠：`declared` 真、cut 假 → `allow_legacy()`；理由含字面 `F3 cut 未發生`；理由不含「已宣告所以切了」 |
| T-4 | PRE-AND | `new5/pre-and/`（三組各缺一前置） | 綠：缺 `declared`／缺 ¬in-flight／缺 cut 三組皆 legacy，理由對得上缺的那一條 |
| T-4 | PRE-HOPS-200 | `new5/pre-hops-200/` | 綠：契約仍 `2.0.0`＋五站 hops 預設 → SLOT-REJECT；路線仍舊 7 |
| T-5 | NEW5-CUT-OK | `new5/cut-ok/`（cut 當下**無** 1–7 `.md`） | 綠：預設五站；hop 紀錄**無**例行 `N7-g1`／`N6-g2` 停；閘與條件邊同意 |
| T-6 | GRAPH-WORD-NE | `new5/inject-graph-word-ne.md` | **注入** 只改 guide 用字、Stage 2 預設仍進 `N7-g1`，卻標 F3 成功 → **該格紅** |
| T-7 | DOCTOR-HONEST | `new5/doctor-honest/`（契約 `2.1.0`、supported 仍只有 `2.0.0`） | 綠：doctor 印 `INCOMPATIBLE` 且非 exit 0（誠實紅＝本格綠義務） |
| T-7 | DOCTOR-NE-TICKET | `new5/doctor-ne-ticket/`（現況可：`COMPATIBLE`＋`2.0.0`） | 綠：求五站 hop **拒**；理由含 `路線未宣告` 或 `仍舊 7` 或 `F3 cut 未發生`；理由**不含**「doctor 已綠所以可 hop」 |
| T-8 | NEW5-WAIT-RED | `new5/inject-wait-red.md` | **注入** 謂詞真 latch 假仍例行停 `N7-g1`／留下「要不要繼續」 → **該格紅** |
| T-8 | KEEP-MK-RED | `new5/inject-keep-mk-red.md` | **注入** Must-keep 任一紅仍 hop（例 M3／M5／M9／M11／M12／M15）→ **該格紅** |
| T-8 | KEEP-SHIP-MECH | `new5/inject-keep-ship-mech.md` | **注入** 機械全綠、無人寫 `verdict: PASS` 卻 Ship Done → **該格紅** |
| T-9 | OLD7-FREEZE | `old7/`（已有 1–7 `.md`） | 綠：整段舊 7；無五站狀態；三 cap 不套 |
| T-9 | OLD7-FOLD-RED | `old7/inject-fold-red.md` | **注入** 對 in-flight 寫五站狀態／五站 hop → **該格紅** |
| T-9 | SELF-OLD7 | 本目錄＋`docs/dev/five-station-f2/`＋`docs/dev/five-station-simplify/` | 綠：求五站自動前進跳不過 |
| T-10 | TOKEN-KEEP | （呼叫既有 token 牙，不改） | 綠：`check-gate-tokens.sh` exit 0；G1／G2／`ACCEPTED` 仍在 |
| T-10 | TOKEN-DEL-RED | `new5/inject-token-del.md` | **注入** 刪 token 卻標 F3 成功 → **該格紅** |
| T-10 | HOLLOW-TRUE | `new5/inject-hollow-true.md` | **注入** 把 `f3_cut_happened==True` 標成 F3 綠 → **該格紅** |
| T-10 | HOLLOW-FILES | `new5/inject-hollow-files.md` | **注入** 把「檔在」標成 F3 綠 → **該格紅** |
| T-10 | HOLLOW-F2 | `new5/inject-hollow-f2.md` | **注入** 只跑 F2 電池綠就標 F3 綠 → **該格紅** |
| T-10 | HOLLOW-WORD | `new5/inject-hollow-word.md` | **注入** 只用字標 F3 綠 → **該格獨立紅**（不是 GRAPH-WORD-NE 附註） |
| T-10 | HOLLOW-TWO-SCRIPT | `new5/inject-hollow-two-script.md` | **注入** 兩支腳本各綠一次就標同一電池綠 → **該格紅** |
| T-10 | HOLLOW-HTML-NE-GWT | `new5/html-only/`（只有 `*.html`、零個 1–7 `.md`） | 綠：`has_old7` 假；僅 html ≠ in-flight |
| T-10 | F3-F2-REGRESS | （呼叫既有 F2 電池，不改） | 綠：F2 仍 `failed=0`；**不是** SC-BATTERY 第四路 |

官方 25 名＝Decision 原 20＋standing 加列 5：NEW5-CUT-OK、NEW5-WAIT-RED、OLD7-FREEZE、OLD7-FOLD-RED、TOKEN-KEEP、TOKEN-DEL-RED、ATTEST-VISIBLE、ATTEST-SILENT-RED、PRE-210-NE-CUT、PRE-AND、PRE-HOPS-200、READ-SEAM、DOCTOR-HONEST、DOCTOR-NE-TICKET、GRAPH-WORD-NE、SELF-OLD7、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、KEEP-MK-RED、KEEP-SHIP-MECH、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT、F3-F2-REGRESS。`--group graph-edges`／`--group doctor`／`--group hollow` 的 `=== CASE` 名詞也必須落在這 25 名內。

### N1 R/S 盤點（49 S；49／49 皆被至少一個 T 的 Covers 承接）

| R | F3 必須落地的 S | 本 hop T |
|---|---|---|
| R-1 | S-1.1、S-1.2、S-1.4、S-1.5 | T-1 |
| R-1 | S-1.3、S-1.6 | T-2 |
| R-2 | S-2.1、S-2.2、S-2.3 | T-3 |
| R-2 | S-2.4、S-2.5、S-2.6、S-2.7 | T-4 |
| R-3／R-7 | S-3.1、S-3.2、S-3.5、S-3.6；S-7.4 | T-5 |
| R-3 | S-3.3、S-3.4 | T-6 |
| R-4 | S-4.1、S-4.2、S-4.3、S-4.4、S-4.5 | T-7 |
| R-5／R-6 | S-5.3；S-6.1、S-6.2、S-6.3 | T-8 |
| R-7 | S-7.1、S-7.2、S-7.3、S-7.5 | T-9 |
| R-5／R-8 | S-5.1、S-5.2、S-5.4、S-5.5、S-5.6、S-5.7、S-5.8、S-5.9、S-5.10、S-5.11；S-8.2、S-8.3、S-8.4；S-8.1、S-8.5、S-8.6（Covers gate） | T-10 |

### 已綠／掛 Covers gate（不另開水平抄表 T）

| S | 為什麼不另開 T | 去向 |
|---|---|---|
| S-8.1 | 本條是 Stage 4 hop 檔集（當時只 4-spec 雙檔、draft、無自填 PASS）。G2 已過。不是 Stage 6 工作 | T-10 Covers gate one-liner。不准重開、不准改 4-spec 頂欄 |
| S-8.5 | Q15–Q27 去向已在 4-spec Real-world Disposition | T-10 Covers gate one-liner。後站不得把 Q21／Q22／Q23 標可選 |
| S-8.6 | F2 park D-1／D-2／D-3／F-c-4 已封；F3 不重開 | T-10 Covers gate one-liner。不准改 `docs/dev/five-station-f2/` 已封 R／S |
| S-7.5 | 「不發明第一隻活五站名字」是命名禁令，不是另開試體 | T-9 Covers。只寫「合成 fixture 或 cut 之後才開」 |

### F3 Files 准許清單（S-8.2 可核）

Stage 6 全部 T 的 Files 聯集只准：

- `guides/guide-dev-flow.html`（七站單行 → 五站用語；≠ SoT）
- `devflow-contract.json`（只 bump `devflow_contract_version` → `2.1.0`）
- `hooks/runtime-capabilities.json`（只加 `2.1.0` 進 `supported_contract_versions`）
- `skills/dev-flow/stage2/graph.yaml`（條件邊；**不刪** `nodes/N7-g1.md`）
- `skills/dev-flow/stage4/graph.yaml`（條件邊；**不刪** `nodes/N6-g2.md`）
- `scripts/five_station_f2.py` 與／或 `scripts/five_station_f3.py`（讀鍵＋cut 讀端＋路線閘）
- `docs/dev/f3-cut-attestation.json`
- `scripts/test-five-station-f3.sh`（單一電池入口；每個跑 F3 Verify 的 T 必列）
- `scripts/check-five-station-f3.sh`（選配；有也不構成第四條電池路）
- `scripts/fixtures/five-station-f3/`（含上表具名路徑；Stage 6 才建檔）
- 本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html

超出上列 = L2／違 S-8.2。禁把 `_templates/`、`hooks/_doctor_impl.py`、`docs/dev/STATUS.md`／`HISTORY.md`、token 刪檔、`docs/dev/five-station-f2/` 已封 R／S、本目錄當 NEW5 fixture、`scripts/test-five-station-f2.sh`／`scripts/test-five-station-f1.sh`／`scripts/check-gate-tokens.sh`／`hooks/devflow-doctor.sh` 寫進任一 T 的 Files。F2／F1／token／doctor 腳本只准呼叫。

### Verify 開工前原樣跑（2026-09-14；F3 電池尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-10 | `scripts/test-five-station-f3.sh` 不存在 → 非零 | ③綠不了但方向對 |
| 現況地板（不當 T 綠） | `hooks/devflow-doctor.sh` → `COMPATIBLE`／exit 0；`scripts/test-five-station-f2.sh` → `failed=0` | 記作 DOCTOR-NE-TICKET／F3-F2-REGRESS 地板，不是 F3 完 |

## T-1 打通三槽可見紀錄且讀端只讀不寫
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.4, S-1.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, docs/dev/f3-cut-attestation.json, scripts/fixtures/five-station-f3/new5/attest-visible/
- Verify: `test -d scripts/fixtures/five-station-f3/new5/attest-visible && n=$(bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE`
- Blocked-by: —
- Risk: high
- Intent: 日常要宣稱「F3 已切」，人必須打得開一份獨立 JSON，指得到誰、何時、切的是哪個 cut 位元；系統問「切了沒」只看這份檔，檔不在或任一格空就當沒切。改的是 cut 紀錄檔與讀它的函式，試體是 `new5/attest-visible/`，不是把布林塞進契約 JSON、不是 git blame、不是看板列。不會變成函式自己寫檔、不會把宣告／in-flight 捆進 `which_condition`、不會在本 T 改 graph 或 doctor。
- Boundaries: 准改模組＝cut 紀錄檔＋`f3_cut_happened()` 讀端＋電池入口骨架＋具名 NEW5 三槽 fixture。Data owner＝寫入該檔的人類。路徑＝`docs/dev/f3-cut-attestation.json`（DD-1）。Interface＝三槽非空 → True；缺檔／空槽 → False；呼叫前後檔位元組不變。`which_condition` 只命名 cut 位元（例 `f3-cut`），禁止三前置 AND，禁止唯一合法戳記 `F3-cut-happened`。Forbidden＝契約兄弟布林、silent `return True`（屬 T-2）、改 doctor／graph、拿本目錄當 NEW5、本 T 評 hop。Test seam＝換 fixture 根可注入缺檔。本 T 不掛 F2 綠當完成。

## T-2 注入 silent True 與只用字當刀讓該格紅
- [ ] 未完成
- Covers: R-1 / S-1.3, S-1.6
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, guides/guide-dev-flow.html, scripts/fixtures/five-station-f3/new5/inject-silent-true.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/inject-silent-true.md && n=$(bash scripts/test-five-station-f3.sh --case ATTEST-SILENT-RED -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f3.sh --case ATTEST-SILENT-RED`
- Blocked-by: T-1
- Intent: 日常有人只把函式改成永遠真、或只把指南改成「五站」、或拿 blame／看板當刀，卻說已經切了——電池這一格必須自己紅，不能靠「函式回真」混過去。指南七站單行仍要改成五站用語（交付物），但改完仍不夠當成功。改的是空切紅格與指南用字，不是改 STATUS 正本、不是把用語寫進 SoT。不會變成 GRAPH-WORD-NE（那格咬 graph 仍停，屬 T-6）、不會在本 T 碰契約 bump。
- Boundaries: 准改模組＝電池 ATTEST-SILENT-RED 跑者＋指南七站單行＋上列注入稿。guide 是交付物 ≠ SoT。Forbidden＝本 feature branch 改 `STATUS.md`、把 blame／看板當 `f3_cut_happened` 真、把「函式回真」記成本格綠、改 graph（屬 T-5／T-6）。本 T 結束時 `git diff --name-only` 對 `docs/dev/STATUS.md` 必須為空。Test seam＝無合格三槽＋字面 `return True`。

## T-3 讓版本讀端只咬正本鍵且錯讀該格紅
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/inject-read-seam.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/inject-read-seam.md && n=$(bash scripts/test-five-station-f3.sh --case READ-SEAM -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && src=$(python3 -c "import pathlib; p=pathlib.Path('scripts/five_station_f3.py'); q=pathlib.Path('scripts/five_station_f2.py'); t=(p.read_text() if p.is_file() else '')+(q.read_text() if q.is_file() else ''); print(t)") && echo "$src" | grep -qv 'blob.get("version")' && echo "$src" | grep -qv 'blob.get("contract_version")' && echo "$src" | grep -q 'devflow_contract_version' && bash scripts/test-five-station-f3.sh --case READ-SEAM`
- Blocked-by: T-2
- Intent: 日常問「現在契約幾點」，必須只看 `devflow_contract_version`；本樹現況那個鍵是 `2.0.0`，讀端要回 `2.0.0`，不准回空字串、不准改去翻 `version`／`contract_version`。若有人只把正本改成 `2.1.0`、讀端卻還在翻錯鍵，卻喊「已宣告」——READ-SEAM 該格必須獨立紅，`declared` 仍假。改的是讀鍵縫，不是 bump 活樹契約（bump 屬 T-7）、不是把 2.1.0 當成 cut。不會變成 fallback 雙讀、不會在本 T 切 hops。
- Boundaries: 准改模組＝`contract_version()` 讀端（`five_station_f2.py` 與／或 `five_station_f3.py`）＋ READ-SEAM 注入稿。Interface＝只讀正本鍵；正本以 `2.1` 開頭 → `declared` 真；cut 位元仍獨立。Forbidden＝fallback 錯鍵、本 T bump 活樹 `devflow-contract.json`（同刀 bump 屬 T-7）、把 `declared` 真寫成 cut 真、改 doctor。現況縫＝`five_station_f2.py` 讀錯鍵回空字串。Test seam＝假契約檔正本已 2.1.0、reader 仍舊。

## T-4 讓路線閘三前置缺一就舊 7 且理由咬得到缺哪一條
- [ ] 未完成
- Covers: R-2 / S-2.4, S-2.5, S-2.6, S-2.7
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/pre-210-ne-cut/, scripts/fixtures/five-station-f3/new5/pre-and/, scripts/fixtures/five-station-f3/new5/pre-hops-200/
- Verify: `test -d scripts/fixtures/five-station-f3/new5/pre-210-ne-cut && test -d scripts/fixtures/five-station-f3/new5/pre-and && test -d scripts/fixtures/five-station-f3/new5/pre-hops-200 && n=$(bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT --case PRE-AND --case PRE-HOPS-200 -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && a=$(bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT -v 2>&1) && echo "$a" | grep -q 'F3 cut 未發生' && echo "$a" | grep -qv '已宣告所以切了' && echo "$a" | grep -qv 'doctor 已綠所以可 hop' && b=$(bash scripts/test-five-station-f3.sh --case PRE-AND -v 2>&1) && echo "$b" | grep -E -q '路線未宣告|仍舊 7' && echo "$b" | grep -E -q 'in-flight|F3 cut 未發生' && c=$(bash scripts/test-five-station-f3.sh --case PRE-HOPS-200 -v 2>&1) && echo "$c" | grep -q 'SLOT-REJECT' && echo "$c" | grep -qv 'marketplace' && bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT --case PRE-AND --case PRE-HOPS-200`
- Blocked-by: T-3
- Risk: high
- Intent: 日常契約已經 2.1.0、目錄也沒有舊站檔，但 cut 紀錄沒寫，求五站必須被擋，理由要看得見「F3 cut 未發生」，不准寫成「已宣告所以切了」。三條前置少任何一條都走舊 7：少宣告 →「路線未宣告／仍舊 7」；少 ¬in-flight → 理由含 `in-flight`；少 cut →「F3 cut 未發生」。有人契約還停在 2.0.0 就把 hops 預設當五站，必須 SLOT-REJECT、線不准改，marketplace／cache 換碼也不算。改的是路線閘三個布林與拒因字面，不是改 graph 檔（條件邊屬 T-5）、不是 bump 活樹。不會變成 2.1.0 單獨冒充 cut、不會把 doctor 綠寫進理由。
- Boundaries: 准改模組＝coordinator `allow_legacy()`／`refuse_hop_reason()`＋上列三組具名 fixture。Interface＝三前置 AND；缺一 → legacy；PRE-210-NE-CUT 理由**必須**含字面 `F3 cut 未發生`、**禁止**含「已宣告所以切了」；PRE-AND 三組理由對得上缺的那一條；PRE-HOPS-200 ＝ SLOT-REJECT 且路線仍舊 7。Forbidden＝marketplace／cache 當第四前置、doctor 綠當路條、本 T 改 `graph.yaml`（未宣告就跳過＝S-2.6／S-3.2 紅）、本 T bump 活樹契約。S-2.7：條件邊可先落地，但跳過側在 `declared` 假時不得生效；無條件改 hops 預設且契約仍 2.0.0＝本 T PRE-HOPS-200 紅。Error seam＝拒因字面可稽核。本 T 不測 cut 後真的跳過例行閘（屬 T-5）。

## T-5 讓 graph 條件邊與路線閘同一三前置且 cut 後不再例行停
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.5, S-3.6; R-7 / S-7.4
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, skills/dev-flow/stage2/graph.yaml, skills/dev-flow/stage4/graph.yaml, scripts/fixtures/five-station-f3/new5/cut-ok/
- Verify: `test -f skills/dev-flow/stage2/nodes/N7-g1.md && test -f skills/dev-flow/stage4/nodes/N6-g2.md && test -d scripts/fixtures/five-station-f3/new5/cut-ok && n=$( { bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK -v; bash scripts/test-five-station-f3.sh --case PRE-HOPS-200 -v; bash scripts/test-five-station-f3.sh --group graph-edges -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && out=$(bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK -v 2>&1) && echo "$out" | grep -q 'NEW5-CUT-OK' && echo "$out" | grep -E -qv 'enter N7-g1|例行停 N7-g1|請人審' && echo "$out" | grep -E -qv 'enter N6-g2|例行停 N6-g2' && echo "$out" | grep -E -q 'allow_legacy=false|legacy 假|why=five|路線=五站' && d=$(bash scripts/test-five-station-f3.sh --case PRE-HOPS-200 -v 2>&1) && echo "$d" | grep -q 'SLOT-REJECT' && echo "$d" | grep -E -q '仍舊 7|N7-g1' && g=$(bash scripts/test-five-station-f3.sh --group graph-edges -v 2>&1) && echo "$g" | grep -c '^=== CASE' | awk '{exit !($1>=3)}' && echo "$g" | grep -E -qv 'GRAPH-AGREE|GRAPH-SKIP|NEW5-EDGE' && bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK && bash scripts/test-five-station-f3.sh --group graph-edges`
- Blocked-by: T-4
- Risk: high
- Intent: 日常 cut 之後才開、目錄還沒有 1–7 站檔的新工作，走 Stage 2／Stage 4 時不該再停下來等人蓋 G1／G2；graph 下一跳與路線閘對同一組「已宣告、不是飛行中、已切」必須給同一個答案——閘說五站，graph 就不得再把人送進 `N7-g1`／`N6-g2`；閘說舊 7，條件邊的跳過側就不得生效。契約還是 2.0.0 時，即使 graph 檔已經寫了條件邊，新工作仍走舊 7（PRE-HOPS-200 再跑一次當 dual-read）。試體根必須是 `new5/cut-ok/`，不是本目錄。改的是兩份 `graph.yaml` 的條件邊與閘的同意探針，不是刪節點檔、不是只把函式改真。不會變成只 hop-skip、不會發明 `GRAPH-AGREE` 當官方 CASE 名。
- Boundaries: 准改模組＝`stage2`／`stage4` `graph.yaml` 條件邊＋路線閘同意探針＋`new5/cut-ok/`。機制形＝條件邊＋路線閘（DD-5／S-3.6），不是刪 `N7-g1.md`／`N6-g2.md`，不是只翻 `f3_cut_happened`。Interface＝同一組（`declared`、in-flight、cut）→ graph next 與 `allow_legacy()` 同意；三前置真 → 不進例行停；`declared` 假 → 跳過側不生效（S-3.2）。`--group graph-edges` 的 `=== CASE` 名詞只准官方 25 名（本組用 NEW5-CUT-OK＋PRE-HOPS-200；同意探針仍印這兩個名字，禁 `GRAPH-AGREE`／`GRAPH-SKIP`／`NEW5-EDGE`）。YAML 鍵名不鎖；可觀測的是 next 與 hop 紀錄。Forbidden＝刪節點、未宣告就跳過、本目錄／`five-station-f2`／`five-station-simplify` 當 NEW5、本 T bump 活樹契約、本 T 改 doctor。節點檔本 T 結束時必須仍在（`test -f` 已寫進 Verify）。NEW5 根＝DD-3 合成根（S-7.4）。

## T-6 注入只改用字仍停 N7-g1 該格紅且節點 token 不刪
- [ ] 未完成
- Covers: R-3 / S-3.3, S-3.4
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, guides/guide-dev-flow.html, scripts/fixtures/five-station-f3/new5/inject-graph-word-ne.md
- Verify: `test -f skills/dev-flow/stage2/nodes/N7-g1.md && test -f skills/dev-flow/stage4/nodes/N6-g2.md && test -f scripts/fixtures/five-station-f3/new5/inject-graph-word-ne.md && n=$(bash scripts/test-five-station-f3.sh --case GRAPH-WORD-NE -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f3.sh --case GRAPH-WORD-NE && bash scripts/check-gate-tokens.sh`
- Blocked-by: T-5
- Intent: 日常有人指南已經寫「五站」、但 Stage 2 預設路仍把人送進 `N7-g1`，卻標 F3 成功——GRAPH-WORD-NE 必須獨立紅，用語與行為分開記帳。`N7-g1.md`／`N6-g2.md` 與 G1／G2／`ACCEPTED` token 還在，token 牙仍綠。改的是這格注入測法，不是刪閘節點來「看起來像切了」。不會變成 HOLLOW-WORD（那格咬「只用字當 F3 綠」、屬 T-10）、不會把「coordinator 拒 hop」記成本格綠。
- Boundaries: 准改模組＝GRAPH-WORD-NE 注入稿＋電池該格。Test seam＝guide 已五站用字 ∧ Stage 2 預設仍進 `N7-g1` ∧ 有人標成功 → 該格紅。Forbidden＝刪節點檔、刪 token、把拒 hop 記成本格綠、把本格與 HOLLOW-WORD 對調。token 牙只呼叫 `scripts/check-gate-tokens.sh`，**不准列入 Files、不准改**。本 T 不測 hollow 用字格（屬 T-10）。

## T-7 讓 doctor 漏加 2.1.0 印 INCOMPATIBLE 且綠不能當 hop 票
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, devflow-contract.json, hooks/runtime-capabilities.json, scripts/fixtures/five-station-f3/new5/doctor-honest/, scripts/fixtures/five-station-f3/new5/doctor-ne-ticket/
- Verify: `test -d scripts/fixtures/five-station-f3/new5/doctor-honest && test -d scripts/fixtures/five-station-f3/new5/doctor-ne-ticket && n=$(bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST --case DOCTOR-NE-TICKET -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 2 && hon=$(bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST -v 2>&1) && echo "$hon" | grep -q 'INCOMPATIBLE' && echo "$hon" | grep -qv 'COMPATIBLE' && echo "$hon" | grep -qv 'doctor 已綠所以可 hop' && ticket=$(bash scripts/test-five-station-f3.sh --case DOCTOR-NE-TICKET -v 2>&1) && echo "$ticket" | grep -E -q '路線未宣告|仍舊 7|F3 cut 未發生' && echo "$ticket" | grep -qv 'doctor 已綠所以可 hop' && echo "$ticket" | grep -qv 'COMPATIBLE so hop' && echo "$ticket" | grep -qv 'handshake-means-route' && grep -q '2.1.0' hooks/runtime-capabilities.json && git diff --exit-code -- hooks/_doctor_impl.py && bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST --case DOCTOR-NE-TICKET`
- Blocked-by: T-6
- Risk: high
- Intent: 日常有人把契約改成 2.1.0、卻忘了把 `2.1.0` 寫進 runtime 支援清單，doctor 必須老實印 `INCOMPATIBLE` 且不能 exit 0——這格綠的意思是「誠實紅有出現」，不是把紅改成綠好看。另一邊：現況 doctor 已經 `COMPATIBLE`（契約仍 2.0.0），有人拿這次綠去求五站 hop，必須被拒，理由是路線（未宣告／仍舊 7／cut 未發生），理由裡不准出現「doctor 已綠所以可 hop」。活樹同一刀把 `2.1.0` 加進 supported，握手實作一個位元組都不能改。marketplace／cache 換碼不是第四條前置。改的是清單與「綠≠票」閘，不是放寬握手。不會變成 4B（綠當路條）或 4C（漏加仍綠）。
- Boundaries: 准改模組＝`devflow-contract.json` 只 bump 正本鍵＋`hooks/runtime-capabilities.json` 只加 `2.1.0`＋路線閘丟棄 doctor 綠＋上列兩組 fixture。DOCTOR-HONEST fixture＝契約 `2.1.0` ∧ supported 仍只有 `2.0.0` → 必須印 `INCOMPATIBLE` 且非 0（誠實紅＝本格綠義務，**不是**紅格）。DOCTOR-NE-TICKET fixture＝`COMPATIBLE`＋`2.0.0` 求五站 hop → 拒；理由集合＝`路線未宣告`｜`仍舊 7`｜`F3 cut 未發生`；禁止集合＝`doctor 已綠所以可 hop`／`COMPATIBLE so hop`。Interface＝版本 ∈ supported 才 COMPATIBLE（握手句不變）。Forbidden＝改 `hooks/_doctor_impl.py`（Verify 已 `git diff --exit-code`）、放寬 2.1.0 ∉ supported 仍綠、把綠定義改成「路線 OK／已切」、marketplace／cache 當第四前置、把 doctor／F1 腳本列入 Files。doctor 入口只呼叫 `hooks/devflow-doctor.sh`。本 T 不測 hollow（屬 T-10）。

## T-8 注入例行等人／Must-keep 紅 hop／機械 Ship 讓該格獨立紅
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.2, S-6.3; R-5 / S-5.3
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/inject-wait-red.md, scripts/fixtures/five-station-f3/new5/inject-keep-mk-red.md, scripts/fixtures/five-station-f3/new5/inject-keep-ship-mech.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/inject-wait-red.md && test -f scripts/fixtures/five-station-f3/new5/inject-keep-mk-red.md && test -f scripts/fixtures/five-station-f3/new5/inject-keep-ship-mech.md && n=$(bash scripts/test-five-station-f3.sh --case NEW5-WAIT-RED --case KEEP-MK-RED --case KEEP-SHIP-MECH -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case NEW5-WAIT-RED --case KEEP-MK-RED --case KEEP-SHIP-MECH`
- Blocked-by: T-7
- Risk: high
- Intent: 日常電池必須能餵三種壞行為、三格各自紅：謂詞已經真、沒人卡住，卻仍把人停在 `N7-g1` 或留下「要不要繼續」（NEW5-WAIT-RED）；Must-keep 任一條紅（缺觀測欄、代填 ACCEPTED、Files 超清單、缺 Verify、自己審自己、token 被刪）卻還 hop，還拿「已經 cut 了」當理由（KEEP-MK-RED；只擋 M11 放過其餘＝本格紅）；機器全綠、7-review 頂欄沒人寫 `verdict: PASS` 卻標 Ship 做完（KEEP-SHIP-MECH）。把「coordinator 拒 hop」標成這些紅格綠＝極性反了，整電池必須非 0。三失敗不得互抵銷。改的是紅格測法，不是把拒 hop 改記成綠。不會變成「檔在／只 F2 綠」當成功（那是 T-10 hollow）。
- Boundaries: 准改模組＝F3 電池紅格跑者＋上列三張具名注入稿。Data owner＝合成 NEW5 fixture。Test seam＝各 CASE 獨立 exit；紅格只接受注入壞行為的紅。KEEP-MK 具名例＝M3 缺觀測欄／M5 代填 `ACCEPTED`／M9 Files 超出聯集／M11 缺 Verify／M12 reviewer＝implementer／M15 token 被刪；只測 M11＝本格紅。Forbidden＝極性反了仍標 F3 成功、用 cut 省略 Must-keep、Ship 自動 Done、Agent 代填 PASS。Error／State seam＝注入等人句／紅 hop／機械 Done。本 T 不跑完整 25 格（屬 T-10）。本 T 不測合法拒 hop 的綠義務（F2 已核；本刀只保紅格）。

## T-9 讓已有站檔整段舊 7 且本目錄／F2／simplify 五站 hop 跳不過
- [ ] 未完成
- Covers: R-7 / S-7.1, S-7.2, S-7.3, S-7.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/old7/
- Verify: `test -d scripts/fixtures/five-station-f3/old7 && n=$(bash scripts/test-five-station-f3.sh --case OLD7-FREEZE --case OLD7-FOLD-RED --case SELF-OLD7 -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case OLD7-FREEZE --case OLD7-FOLD-RED --case SELF-OLD7`
- Blocked-by: T-8
- Intent: 日常已經有 1–7 站檔的工作必須走完整段舊 7，不能中途被折成五站、不能寫五站狀態、三個 hop cap 也不套。有人硬寫五站進去，OLD7-FOLD-RED 該格必須紅。對 `docs/dev/five-station-f3/`、`five-station-f2`、`five-station-simplify` 要求五站自動前進必須跳不過；本目錄出貨仍舊 7。不寫出「第一隻活五站＝某某 slug」當已核目標。改的是 in-flight 凍結與自保，不是拿本 slug 當白老鼠。不會變成對 live 建五站機。
- Boundaries: 准改模組＝路線閘對 in-flight／本目錄／F2／simplify 的拒 + OLD7 fixture 根。NEW5 試體＝DD-3 合成根。Forbidden＝本目錄當 NEW5、`five-station-f2`／`five-station-simplify` 當 NEW5、對 OLD7 寫五站狀態（那是 OLD7-FOLD-RED 的注入，不是 FREEZE 綠格）、發明活五站 slug 名（S-7.5）、刪 token。僅 html ≠ in-flight（HOLLOW-HTML-NE-GWT 屬 T-10）。電池 Data owner＝OLD7 fixture，不是本目錄 hop 主詞。

## T-10 收口同一電池 25 CASE、TOKEN、hollow 與 Files 准許清單
- [ ] 未完成
- Covers: R-5 / S-5.1, S-5.2, S-5.4, S-5.5, S-5.6, S-5.7, S-5.8, S-5.9, S-5.10, S-5.11; R-8 / S-8.2, S-8.3, S-8.4; S-8.1（gate：Stage 4 hop 雙檔已 G2 綠，不准重開 4-spec 頂欄）；S-8.5（gate：Q15–Q27 去向已綠，Q21–Q23 不得標可選）；S-8.6（gate：F2 park D-1…F-c-4 不准重開）
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f2.py, scripts/five_station_f3.py, scripts/check-five-station-f3.sh, scripts/fixtures/five-station-f3/new5/, scripts/fixtures/five-station-f3/old7/
- Verify: `test -d scripts/fixtures/five-station-f3/new5 && test -d scripts/fixtures/five-station-f3/old7 && n=$(bash scripts/test-five-station-f3.sh -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 25 && bash scripts/test-five-station-f3.sh && bash scripts/test-five-station-f3.sh --help 2>&1 | grep -q -- '--only' && test "$(bash scripts/test-five-station-f3.sh --only new5 >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --only old7 >/dev/null 2>&1; echo $?)" -eq 3 && test "$(bash scripts/test-five-station-f3.sh --only token >/dev/null 2>&1; echo $?)" -eq 3 && t=$(bash scripts/test-five-station-f3.sh --case TOKEN-KEEP --case TOKEN-DEL-RED --case F3-F2-REGRESS -v 2>&1) && echo "$t" | grep -c '^=== CASE' | awk '{exit !($1>=3)}' && h=$(bash scripts/test-five-station-f3.sh --group hollow -v 2>&1) && echo "$h" | grep -c '^=== CASE' | awk '{exit !($1>=6)}' && echo "$h" | grep -q 'HOLLOW-TRUE' && echo "$h" | grep -q 'HOLLOW-FILES' && echo "$h" | grep -q 'HOLLOW-F2' && echo "$h" | grep -q 'HOLLOW-WORD' && echo "$h" | grep -q 'HOLLOW-TWO-SCRIPT' && echo "$h" | grep -q 'HOLLOW-HTML-NE-GWT' && echo "$h" | grep -E -qv 'HOLLOW-OK|NEW5-MKTG' && bash scripts/test-five-station-f2.sh && bash scripts/check-gate-tokens.sh`
- Blocked-by: T-9
- Risk: high
- Intent: 日常宣稱 F3 完，必須是**同一支** `scripts/test-five-station-f3.sh` 在同一 process 把 NEW5、OLD7、TOKEN 三組都跑完才 exit 0。缺一路、跳過一路、入口只轉呼叫 F2 電池、只證明函式真、只證明檔在、只用字、兩支腳本各綠一次、只 F2 綠 → 整電池非 0。`--only new5`／`old7`／`token` 必須是 `--help` 裡的一等旗標，各須 exit **3**；未知旗標是 exit 2，不得被「非 0」誤當 hollow 綠。25 個官方 CASE 名都在，一格都不能少。本 T 具名收口格＝TOKEN-KEEP、TOKEN-DEL-RED、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT、F3-F2-REGRESS。F3-F2-REGRESS 綠是地板，**不是**第四條 IFF。TOKEN-KEEP＝token 牙仍綠；TOKEN-DEL-RED＝注入刪 token 卻標成功必須紅。HOLLOW-HTML-NE-GWT＝只有 html、沒有 1–7 `.md` 的目錄不是 in-flight。Files 聯集不超出准許清單；`_templates/`、doctor 握手、STATUS／HISTORY、本目錄當 NEW5、刪 token、重開 F2 park 行數＝0。不准重開已過的 Stage 4 頂欄、不准把 Q21／Q22／Q23 標可選。改的是收口對照，不是順便發明 G3 PASS，也不是掃 4-spec／5-tasks markdown 當綠。
- Boundaries: 准改模組＝電池入口收口（可動上列 impl／fixture／可選 check）。Interface＝單一 process 三組都跑完才 0；F2 腳本不是入口；可選 `check-five-station-f3.sh` 不是第四路。`--only` 一等旗標；hollow＝exit 3；用法／未知旗標＝exit 2。`--group hollow` 名詞只准官方 25 名（HOLLOW-TRUE／FILES／F2／WORD／TWO-SCRIPT／HTML-NE-GWT），禁 `HOLLOW-OK`／`NEW5-MKTG`。Forbidden＝F2 綠寫進 IFF、兩支腳本各綠當同一電池、僅 html 當 GWT、減 Decision 原 20 列、Files 超出 S-8.2、用 python 掃 markdown 當 Stage 6 綠、用未知旗標非 0 冒充 hollow、改 STATUS／HISTORY、改 4-spec 頂欄（S-8.1）、重開 F2 park（S-8.6）、發明活五站名字。Diff Budget 0 區塊命中＝本條紅。F2／token 腳本只呼叫、不進 Files。本 T Verify 是 SC-BATTERY 全入口（`-ge 25`）＋三條 hollow 探針＋F2 地板＋token 牙；cut／讀鍵／閘／graph／doctor／紅格已由 T-1…T-9 加厚。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-10 單鏈 | Feature Risk high；讀端／閘／graph／doctor／電池改同一組 coordinator 檔。Files 重疊時 parallel 會吵 | 4-spec Verification Profile Risk high；使用者 B-line brief「sequential」 | 讓 T-4 與 T-5 平行。棄：閘與條件邊必須同謂詞，平行會先切 graph 後補閘 |
| T-1 選 ATTEST-VISIBLE 不當 NEW5-CUT-OK | 最薄端到端是「人指得到三槽、函式只讀」；graph 跳過是加厚，不是第一刀可觀測主詞 | 4-spec S-1.1／S-1.4；B 線主軸 cut SoT | T-1 先做 NEW5-CUT-OK。棄：還沒有可見紀錄，跳過是假切 |
| 路線閘（T-4）與 graph 條件邊（T-5）拆開 | B 線要 Verify 咬拒因字面與 next／同意探針；混一 T 會讓 SLOT-REJECT 與「真的跳過」互相遮 | 4-spec S-2.4…S-2.7 對 S-3.1／S-3.5；B 線 brief「graph + route gate 尤其清楚」 | 一 T 兼閘與邊。棄：PRE-HOPS-200 綠會被誤認成已經跳過 |
| T-5 `--group graph-edges` 只印官方名 NEW5-CUT-OK＋PRE-HOPS-200，禁 `GRAPH-AGREE` | standing／F2：`--group` 名詞必須落在官方 CASE；同意探針不是第 26 名 | 4-spec CASE 只准加不准減；S-3.5 無獨立 CASE 名 | 發明 GRAPH-AGREE 當通過條件。棄：偷做 annex |
| doctor HONEST 與 NE-TICKET 同 T-7，Verify 分行咬 `INCOMPATIBLE` 與拒因集合 | B 線要 honesty／ticket 字面牙；兩格極性不同（誠實紅＝HONEST 綠義務；NE-TICKET 是拒 hop 綠義務） | 4-spec S-4.2／S-4.3；現況 doctor 已 COMPATIBLE 可當 NE-TICKET 地板 | 只跑 doctor exit 0 當 T-7 綠。棄：綠變 ticket |
| T-7 `git diff --exit-code -- hooks/_doctor_impl.py` 寫進同一條 Verify | S-4.4 握手語意 Diff Budget 0；不進 Files 仍要機械咬 | 4-spec S-4.4／S-8.2 | 只在 Boundaries 寫「不准改」。棄：Stage 6 手滑改握手 |
| 紅格（T-8）與 freeze（T-9）拆開 | 極性反了會把拒寫測成 OLD7-FOLD-RED 綠；FREEZE 是綠格義務 | 4-spec 約束 16；S-7.1／S-7.2 | 一 T 兼折線紅與凍結綠。棄：測法對調 |
| S-8.1／S-8.5／S-8.6 掛 T-10 Covers gate，不另開 T | 49／49 可追；Stage 4 檔集與 Disposition／park 已在 G2 綠 | 4-spec S-8.1／S-8.5／S-8.6 | 發明 T-11 重抄 Disposition。棄：水平切帳 |
| S-7.5 掛 T-9，不另開 T | 命名禁令跟 SELF-OLD7 同一把鎖 | 4-spec S-7.5／OC-9 | 寫出活五站 slug 當已核。棄：X4 |
| 單一檢查家族 `test-five-station-f3`；`--only token` 當第三路 hollow | Diff Budget 入口 1 檔；SC-BATTERY 三路；F2 的 `--only f1` 在 F3 換成 token | 4-spec DD-2；S-5.1 | 每 CASE 一支 sh；或 `--only f2` 當 IFF。棄：hollow 變種 |
| T-10 hollow 探針 exit 3；`--only` 必須在 `--help` | 未知旗標 exit≠0 會假綠 | 4-spec S-5.4…S-5.6／S-5.9…S-5.11 | `! bash --only new5` 靠未知旗標非 0。棄：假綠 |
| 通過條件＝官方 25 名；禁掃 markdown 當 Stage 6 綠 | 發明名與掃 4-spec／5-tasks 字串無鑑別力 | 4-spec S-5.2 | `NEW5-MKTG-*`／`GRAPH-AGREE`／python 掃 md。棄：假綠 |
| 不改 doctor 握手／不刪節點／不碰 STATUS | S-8.2 Diff Budget 0；三把鎖後站不准改成 In | 4-spec S-4.4／S-3.4／S-8.1…S-8.3 | T-7 順便修握手。棄：越刀 |
| 可選 `check-five-station-f3.sh` 列入 T-10 Files，但不進 IFF | DD-2 准獨立 check；HOLLOW-TWO-SCRIPT 咬兩支各綠 | 4-spec DD-2；S-5.10 | 把 check 當第四條電池路。棄：hollow |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f3.sh` 不存在 → 十欄皆非零；doctor／F2 現況綠只當地板 | 模板 Verify 三律 ③ | 用已綠的 F2 十二群當 T-10。棄：違 S-5.6／S-5.7 |