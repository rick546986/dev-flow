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

# 5. 任務 — F3 cut 可見紀錄／讀鍵／graph+dual-read／doctor 清單／三路電池（Writer A 獨立全稿）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、DD-1…DD-10 Owner PASS；main tip `4d0a5b6`／#380，規格 #379／#378 Winner A）。Lane = **full**。本 hop **只寫任務雙檔**。
> 原文獨立於 B／C（A 線未讀他稿）。不換 winner。不落地 `scripts/` 實作、不改 `STATUS.md`／`HISTORY.md`、不改 1–4 文檔、不發明 G3、不開 Stage 6。
> Knife = **只 F3 cut**：獨立三槽紀錄 + `contract_version()` 只讀正本鍵 + graph 條件邊與 dual-read + doctor 只加 `2.1.0` + 同一電池 NEW5＋OLD7＋TOKEN。**不是**改握手、**不是**刪 token／節點、**不是**拿本目錄當 NEW5。
> Scope lock（S-8.2）：Files 聯集只准下面「F3 Files 准許清單」。`_templates/`／`_doctor_impl.py` 握手／STATUS／HISTORY／本目錄當 NEW5／刪 G1／G2／`ACCEPTED`／重開 F2 park Diff Budget **＝0**。
> tracer（A 線主軸）：T-1 先打通 **三槽可見＋缺檔空槽回假**；T-2 silent True 該格紅；T-3 **READ-SEAM** 只 bump 不修 reader 紅；T-4 **PRE-210-NE-CUT／PRE-AND／PRE-HOPS-200** 具名缺位＋理由字面；再加厚 graph／doctor／keep／freeze；T-10 收口 25 CASE。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。`which_condition` 只命名 cut 位元（例 `f3-cut`），不准捆三前置 AND，不准把 `F3-cut-happened` 當唯一合法戳記。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-7.3）。F3 入口是**新家族** `scripts/test-five-station-f3.sh`（加 `scripts/five_station_f3.py` 與／或改 `scripts/five_station_f2.py` 的讀鍵／cut 讀端／路線閘），不是改 `_doctor_impl.py` 握手、不是改 `_templates/`、不是拿 F2 電池當完成。
cut SoT 路徑（DD-1）：`docs/dev/f3-cut-attestation.json`（獨立檔；三槽 `who`／`when`／`which_condition` 皆非空字串才合格）。**禁止**寫進 `devflow-contract.json` 當版本兄弟布林。函式 `f3_cut_happened()` **只讀不寫**。
`contract_version()`（DD／S-2.1）：**只讀** `devflow_contract_version`。禁止 fallback／dual-read `version`／`contract_version`。只 bump 正本、reader 仍舊＝READ-SEAM 紅。
NEW5 fixture 根（DD-3）：`scripts/fixtures/five-station-f3/new5/`（合成；不是本目錄、不是 `five-station-f2`、不是 `five-station-simplify`）。
OLD7 fixture 根（DD-4）：`scripts/fixtures/five-station-f3/old7/`（已有 1–7 `.md`）。
三前置繼承 F2 4A：`declared` ∧ ¬in-flight ∧ cut；缺一 → `allow_legacy()`。2.1.0 ≠ cut。缺 cut 理由字面必須含 `F3 cut 未發生`。
graph 機制（DD-5）：`stage2`／`stage4` `graph.yaml` **條件邊**＋ coordinator 路線閘讀**同一**三前置。節點 `N7-g1`／`N6-g2` 與 token **不刪**。
doctor：只把 `2.1.0` 寫進 `hooks/runtime-capabilities.json` 的 `supported_contract_versions`。綠 ≠ ticket。marketplace／cache 不是第四條前置。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
Decision 原 20 列 CASE 只准加；本 hop 承接 20＋standing 加列 5＝**官方 25 名**，減一列＝翻 Decision。發明名不是通過條件。
紅格極性＝**注入該壞行為 → 該格獨立紅**。把「coordinator 拒 hop」記成紅格綠＝極性反了，已拒。
可選 `scripts/check-five-station-f3.sh` 不是第四條電池路。F2 綠是地板（F3-F2-REGRESS），**不是** SC-BATTERY 第四條 IFF。

### 本 hop 點名對照（Stage 6 才建檔；Verify 必須點到官方 CASE 名＋具名路徑）

| T | 路／CASE | 檔（皆在 `scripts/fixtures/five-station-f3/`，除非另註） | 紅／綠什麼 |
|---|---|---|---|
| T-1 | ATTEST-VISIBLE `--slot ok` | `new5/attest/ok/docs/dev/f3-cut-attestation.json`（`who`＝`rick`、`when`＝ISO-8601 非空、`which_condition`＝`f3-cut`） | 綠：人指得到三槽；`f3_cut_happened` 回 `True`；依據是檔不是 `return True` |
| T-1 | ATTEST-VISIBLE `--slot missing` | `new5/attest/missing/`（**無**該 JSON） | 綠：讀端 `False`；不得因契約／guide 已寫五站而回真 |
| T-1 | ATTEST-VISIBLE `--slot empty` | `new5/attest/empty-who/docs/dev/f3-cut-attestation.json`（`who`＝`""` 或缺 `when`） | 綠：讀端 `False` |
| T-1 | ATTEST-VISIBLE `--readonly` | 同上 `ok/`；呼叫前後比位元組 | 綠：函式不建／不覆寫／不刪該檔 |
| T-1 | ATTEST-VISIBLE `--sibling-reject` | `new5/attest/sibling-bool.md`（cut 寫進契約 JSON 兄弟鍵） | 綠：該寫法被拒；SoT 仍是獨立三槽檔 |
| T-2 | ATTEST-SILENT-RED | `new5/inject-silent-true.md` | **注入** 只 `return True`、無合格三槽，卻稱已切 → **該格紅** |
| T-3 | READ-SEAM | `new5/read-seam/devflow-contract.json`（正本鍵已 `2.1.0`；reader 仍讀 `version`／`contract_version`） | **注入** 只 bump 正本、reader 仍舊、卻稱已宣告 → **該格紅**；`declared` 仍假 |
| T-3 | READ-SEAM `--reader canonical-200` | `new5/read-seam/canonical-200.json`（只有 `devflow_contract_version`＝`2.0.0`） | 綠：回 `2.0.0`；原始碼無 `blob.get("version")`／`blob.get("contract_version")` |
| T-3 | READ-SEAM `--reader canonical-210` | `new5/read-seam/canonical-210.json`（正本鍵＝`2.1.0`；reader 已修） | 綠：回傳以 `2.1` 開頭；`declared` 真；**cut 仍獨立為假** |
| T-4 | PRE-210-NE-CUT | `new5/pre/210-ne-cut/`（正本 `2.1.0`＋reader 已修；無 1–7 `.md`；三槽檔缺席） | 綠：`allow_legacy()`；理由含字面 `F3 cut 未發生`；理由**不含**「已宣告所以切了」 |
| T-4 | PRE-AND `--missing declared` | `new5/pre/and-no-declared/`（cut 真、¬in-flight 真、`declared` 假） | 綠：legacy；理由含 `路線未宣告` 或 `仍舊 7` |
| T-4 | PRE-AND `--missing in-flight` | `new5/pre/and-in-flight/`（`declared` 真、cut 真、已有 1–7 `.md`） | 綠：legacy；理由含 `in-flight` |
| T-4 | PRE-AND `--missing cut` | `new5/pre/and-no-cut/`（`declared` 真、¬in-flight 真、cut 假） | 綠：legacy；理由含 `F3 cut 未發生` |
| T-4 | PRE-HOPS-200 | `new5/pre/hops-200/`（契約仍 `2.0.0`；hops 預設被當成五站） | 綠：SLOT-REJECT；**不得改線** |
| T-5 | NEW5-CUT-OK | `new5/cut-ok/`（三前置全真；cut 當下零個 1–7 `.md`） | 綠：預設五站；無例行 G1／G2 停；不進 `N7-g1`／`N6-g2` |
| T-6 | GRAPH-WORD-NE | `new5/graph-word-ne.md` | **注入** 只改用字、新 slug 仍停 `N7-g1`，卻標成功 → **該格紅** |
| T-7 | DOCTOR-HONEST | `new5/doctor-honest/`（契約 `2.1.0`；supported 仍只有 `2.0.0`） | 綠：`INCOMPATIBLE` 且非 exit 0 |
| T-7 | DOCTOR-NE-TICKET | `new5/doctor-ne-ticket/`（`COMPATIBLE`＋契約 `2.0.0` 求五站 hop） | 綠：拒；理由是路線，**不含**「doctor 已綠所以可 hop」 |
| T-8 | NEW5-WAIT-RED | `new5/inject-wait-red.md` | **注入** 謂詞真 latch 假仍例行停 `N7-g1`／留下「要不要繼續」→ **該格紅** |
| T-8 | KEEP-MK-RED | `new5/inject-keep-mk-red.md` | **注入** Must-keep 紅仍 hop（例 M3／M5／M9／M11／M12／M15）→ **該格紅** |
| T-8 | KEEP-SHIP-MECH | `new5/inject-keep-ship-mech.md` | **注入** 機械全綠、無人寫 `verdict: PASS` 卻 Ship Done → **該格紅** |
| T-9 | OLD7-FREEZE | `old7/`（已有 1–7 `.md`） | 綠：整段舊 7；無五站狀態；三 cap 不套 |
| T-9 | OLD7-FOLD-RED | `old7/inject-fold-red.md` | **注入** 對 in-flight 寫五站 → **該格紅** |
| T-9 | SELF-OLD7 | 本目錄＋`docs/dev/five-station-f2/`＋`docs/dev/five-station-simplify/` | 綠：求五站自動前進跳不過 |
| T-10 | TOKEN-KEEP | 落地樹 | 綠：`check-gate-tokens.sh` exit 0；token 字面與檔仍在 |
| T-10 | TOKEN-DEL-RED | `new5/inject-token-del.md` | **注入** 刪 token 卻標 F3 成功 → **該格紅** |
| T-10 | HOLLOW-TRUE／FILES／F2／WORD／TWO-SCRIPT | `new5/hollow-*.md` | **注入** 函式真／檔在／只 F2 綠／只用字／兩支腳本各綠 → **該格紅** |
| T-10 | HOLLOW-HTML-NE-GWT | `new5/html-only/`（只有 `*.html`、零個 1–7 `.md`） | 綠：不是 in-flight GWT |
| T-10 | F3-F2-REGRESS | 呼叫既有 `scripts/test-five-station-f2.sh`（**不進 Files**） | 綠：F2 exit 0 且 `failed=0`；**不是**第四條 IFF |

官方 25 名＝Decision 原 20＋standing 加列 5：NEW5-CUT-OK、NEW5-WAIT-RED、OLD7-FREEZE、OLD7-FOLD-RED、TOKEN-KEEP、TOKEN-DEL-RED、ATTEST-VISIBLE、ATTEST-SILENT-RED、PRE-210-NE-CUT、PRE-AND、PRE-HOPS-200、READ-SEAM、DOCTOR-HONEST、DOCTOR-NE-TICKET、GRAPH-WORD-NE、SELF-OLD7、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT、F3-F2-REGRESS、KEEP-MK-RED、KEEP-SHIP-MECH。`--group` 的 `=== CASE` 名詞也必須落在這 25 名內。

### N1 R/S 盤點（49 S；49／49 皆被至少一個 T 的 Covers 承接）

| R | F3 必須落地的 S | 本 hop T |
|---|---|---|
| R-1 | S-1.1、S-1.2、S-1.4、S-1.5 | T-1 |
| R-1 | S-1.3、S-1.6 | T-2 |
| R-2 | S-2.1、S-2.2、S-2.3 | T-3 |
| R-2 | S-2.4、S-2.5、S-2.6、S-2.7 | T-4 |
| R-3 | S-3.1、S-3.2、S-3.5、S-3.6 | T-5 |
| R-3 | S-3.3、S-3.4 | T-6 |
| R-4 | S-4.1、S-4.2、S-4.3、S-4.4、S-4.5 | T-7 |
| R-6 | S-6.1、S-6.2、S-6.3 | T-8 |
| R-7 | S-7.1、S-7.2、S-7.3、S-7.4、S-7.5 | T-9 |
| R-5／R-8 | S-5.1…S-5.11；S-8.2、S-8.3、S-8.4；S-8.1、S-8.5、S-8.6（Covers gate） | T-10 |

### 已綠／掛 Covers gate（不另開水平抄表 T）

| S | 為什麼不另開 T | 去向 |
|---|---|---|
| S-8.1 | 本條是 Stage 4 hop 檔集（當時只 4-spec 雙檔、draft）。G2 已過（#379／#380）。不是 Stage 6 工作 | T-10 Covers gate one-liner。不准重開、不准改 4-spec 頂欄 |
| S-8.5 | Q15–Q27 去向已在 4-spec Real-world Disposition | T-10 Covers gate one-liner。後站不得把任一 Q 標消失 |
| S-8.6 | F2 park D-1／D-2／D-3／F-c-4 已封；本刀不重開 | T-10 Covers gate one-liner。四項不出現在 In |

### F3 Files 准許清單（S-8.2 可核）

Stage 6 全部 T 的 Files 聯集只准：

- `guides/guide-dev-flow.html`（七站單行 → 五站用語；≠ SoT）
- `devflow-contract.json`（**只** bump `devflow_contract_version`）
- `hooks/runtime-capabilities.json`（**只**加 `2.1.0`）
- `skills/dev-flow/stage2/graph.yaml`；`skills/dev-flow/stage4/graph.yaml`（條件邊；節點檔不刪）
- `scripts/five_station_f2.py` 與／或 `scripts/five_station_f3.py`（讀鍵＋cut 讀端＋路線閘）
- `docs/dev/f3-cut-attestation.json`（三槽；cut 當下才寫）
- `scripts/test-five-station-f3.sh`（單一電池入口；每個跑 F3 Verify 的 T 必列）
- `scripts/check-five-station-f3.sh`（可選獨立 check；有也不構成第四條電池路）
- `scripts/fixtures/five-station-f3/`（含上表具名路徑；Stage 6 才建檔）
- 本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html

超出上列 = L2／違 S-8.2。禁把 `_templates/`、`hooks/_doctor_impl.py`、`docs/dev/STATUS.md`／`HISTORY.md`、本目錄當 NEW5、G1／G2／`ACCEPTED` token 刪檔、`docs/dev/five-station-f2/` 已封 R／S、節點 `N7-g1.md`／`N6-g2.md` 刪檔寫進任一 T 的 Files。F2 電池與 `check-gate-tokens.sh` 只准呼叫、不准列入 Files、不准改。

### Verify 開工前原樣跑（2026-09-14；F3 電池尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-10 | `scripts/test-five-station-f3.sh` 不存在 → 非零 | ③綠不了但方向對 |

## T-1 打通三槽可見紀錄且缺檔空槽讀端回假
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.4, S-1.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/attest/
- Verify: `test -f scripts/fixtures/five-station-f3/new5/attest/ok/docs/dev/f3-cut-attestation.json && test ! -e scripts/fixtures/five-station-f3/new5/attest/missing/docs/dev/f3-cut-attestation.json && test -f scripts/fixtures/five-station-f3/new5/attest/empty-who/docs/dev/f3-cut-attestation.json && n=$( { bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot ok -v; bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot missing -v; bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot empty -v; bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --readonly -v; bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --sibling-reject -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 5 && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot ok && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot missing && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot empty && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --readonly && bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --sibling-reject`
  五格皆印 `=== CASE ATTEST-VISIBLE`。`--slot ok`：三槽非空、`which_condition`＝`f3-cut`（只命名 cut 位元，不是三前置 AND，不是字面 `F3-cut-happened`）、讀端 `True`。`--slot missing`／`--slot empty`：讀端 `False`。`--readonly`：呼叫前後檔位元組不變。`--sibling-reject`：契約檔無 cut 兄弟鍵當 SoT。
- Blocked-by: —
- Risk: high
- Intent: 日常要宣稱「已切」，人必須能打開一份獨立 JSON，用手指到誰寫的、什麼時候寫、指認的是哪一個 cut 位元；檔不在或任一槽空，系統就當沒切。改的是 cut 紀錄形與只讀函式，試體在 `new5/attest/` 四棵子樹，不是把布林塞進契約檔、也不是先改 graph。不會變成「函式回真就算切了」、不會讓讀端自己生檔、不會把宣告／in-flight 捆進 `which_condition`。
- Boundaries: 准改模組＝cut 讀端（`five_station_f3.py` 的 `f3_cut_happened`）＋電池入口骨架＋上列 attest fixture。Data owner＝人類寫入的三槽檔。Interface＝讀三槽→bool；缺檔／空槽→False。Forbidden＝`devflow-contract.json` 兄弟布林當 SoT、git blame 冒充 who／when、STATUS／guide 用語當 SoT、函式寫入／覆寫／刪檔、把 `which_condition` 寫成三前置 AND 或唯一戳記 `F3-cut-happened`、本 T 改 graph／bump 契約／寫活樹 `docs/dev/f3-cut-attestation.json`。Test seam＝換 fixture 根可注入缺檔／空槽／兄弟鍵。本 T 不評路線閘（屬 T-4）。

## T-2 注入 silent True 無紀錄卻稱已切讓該格紅
- [ ] 未完成
- Covers: R-1 / S-1.3, S-1.6
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/inject-silent-true.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/inject-silent-true.md && n=$(bash scripts/test-five-station-f3.sh --case ATTEST-SILENT-RED -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f3.sh --case ATTEST-SILENT-RED`
- Blocked-by: T-1
- Intent: 日常有人只把函式改成字面 `return True`、樹上沒有合格三槽，卻對外說 F3 已切，電池這一格必須自己紅，不能靠「函式回真」混過去。改的是空切紅格，不是改 guide 當成功、也不是改 STATUS。不會變成用語／blame／看板能讓讀端變真；guide 七站單行仍是後站交付物（屬 T-6），改完仍 ≠ 切成功。
- Boundaries: 准改模組＝ATTEST-SILENT-RED 注入跑者＋上列具名稿。Data owner＝合成 NEW5。Test seam＝無三槽＋字面 True→該格獨立非 0。Forbidden＝把「函式回真」記成本格綠、用 git blame／STATUS Active 列／只改 guide 用字宣稱已切、本 PR 改 `STATUS.md`、本 T 改 `guides/guide-dev-flow.html`（用語交付屬 T-6）。Error／State seam＝缺檔或空槽時 silent True 必須紅。本 T 不修 reader 讀鍵（屬 T-3）。

## T-3 讓 contract_version 只讀正本鍵且只 bump 不修 reader 該格紅
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/five_station_f2.py, scripts/fixtures/five-station-f3/new5/read-seam/
- Verify: `test -f scripts/fixtures/five-station-f3/new5/read-seam/devflow-contract.json && test -f scripts/fixtures/five-station-f3/new5/read-seam/canonical-200.json && test -f scripts/fixtures/five-station-f3/new5/read-seam/canonical-210.json && n=$( { bash scripts/test-five-station-f3.sh --case READ-SEAM -v; bash scripts/test-five-station-f3.sh --case READ-SEAM --reader canonical-200 -v; bash scripts/test-five-station-f3.sh --case READ-SEAM --reader canonical-210 -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case READ-SEAM && bash scripts/test-five-station-f3.sh --case READ-SEAM --reader canonical-200 && bash scripts/test-five-station-f3.sh --case READ-SEAM --reader canonical-210`
  三格皆印 `=== CASE READ-SEAM`。無旗標＝注入舊 reader（正本已 `2.1.0` 仍回 `""` 或不以 `2.1` 開頭）→該格紅。`--reader canonical-200`＝只讀正本回 `2.0.0`。`--reader canonical-210`＝回傳以 `2.1` 開頭且 `declared` 真；本格不得把 `declared` 真寫成 cut 真。
- Blocked-by: T-2
- Risk: high
- Intent: 日常有人把契約檔的正本鍵改成 `2.1.0`，但讀版本的函式還在找舊鍵，系統必須當「還沒宣告」，這一格要紅。修過之後，現況只有正本鍵＝`2.0.0` 的樹要回 `2.0.0` 不是空字串；正本鍵＝`2.1.0` 才算已宣告。改的是讀鍵縫，不是 bump 活樹契約、不是寫 cut 檔。不會變成 fallback 舊鍵、不會讓「檔上有 2.1.0」單獨等於已切。
- Boundaries: 准改模組＝`contract_version()` 讀徑（可改 `five_station_f2.py` 與／或 `five_station_f3.py`）＋上列 read-seam fixture。Data owner＝`devflow-contract.json` 的 `devflow_contract_version`。Interface＝只讀正本鍵→字串；缺檔／缺鍵→`""`。Forbidden＝`blob.get("version")`／`blob.get("contract_version")` fallback、只 bump 正本就稱已宣告、本 T bump 活樹 `devflow-contract.json`、本 T 寫 cut 紀錄、把 `declared` 真當成 cut 真。Test seam＝假契約檔三份（舊 reader／canonical-200／canonical-210）。本 T 不評三前置 AND（屬 T-4）。

## T-4 讓三前置缺一 legacy 且 2.1.0 冒充不了 cut
- [ ] 未完成
- Covers: R-2 / S-2.4, S-2.5, S-2.6, S-2.7
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/pre/
- Verify: `test -d scripts/fixtures/five-station-f3/new5/pre/210-ne-cut && test -d scripts/fixtures/five-station-f3/new5/pre/and-no-declared && test -d scripts/fixtures/five-station-f3/new5/pre/and-in-flight && test -d scripts/fixtures/five-station-f3/new5/pre/and-no-cut && test -d scripts/fixtures/five-station-f3/new5/pre/hops-200 && n=$( { bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT -v; bash scripts/test-five-station-f3.sh --case PRE-AND --missing declared -v; bash scripts/test-five-station-f3.sh --case PRE-AND --missing in-flight -v; bash scripts/test-five-station-f3.sh --case PRE-AND --missing cut -v; bash scripts/test-five-station-f3.sh --case PRE-HOPS-200 -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 5 && bash scripts/test-five-station-f3.sh --case PRE-210-NE-CUT && bash scripts/test-five-station-f3.sh --case PRE-AND --missing declared && bash scripts/test-five-station-f3.sh --case PRE-AND --missing in-flight && bash scripts/test-five-station-f3.sh --case PRE-AND --missing cut && bash scripts/test-five-station-f3.sh --case PRE-HOPS-200`
  五格名詞只准 `PRE-210-NE-CUT`／`PRE-AND`／`PRE-HOPS-200`。PRE-210-NE-CUT 理由必含 `F3 cut 未發生`、必不含「已宣告所以切了」。PRE-AND 三刀理由必須對上缺的那一條（`路線未宣告` 或 `仍舊 7`／`in-flight`／`F3 cut 未發生`）。PRE-HOPS-200＝SLOT-REJECT 且路線仍舊 7。
- Blocked-by: T-3
- Risk: high
- Intent: 日常契約已經 2.1.0、目錄也還沒有舊站檔，只要 cut 紀錄沒寫，求五站必須被拒，嘴上要說「F3 cut 未發生」，不能說「已經宣告所以切了」。三條前置少任何一條都回舊 7，而且理由要指到少的那一條。有人契約還停在 2.0.0 就把 hops 預設改五站，必須 SLOT-REJECT、線不能動。改的是路線閘理由字面，試體在 `new5/pre/` 五棵具名子樹。不會變成 marketplace／cache 當第四條前置，不會讓 hops 預設五站早於 2.1.0 宣告。
- Boundaries: 准改模組＝路線閘（`allow_legacy`／`refuse_hop_reason`）＋上列五棵 PRE fixture。Data owner＝專案樹契約＋cut 檔＋該 slug 是否已有 1–7 `.md`。Interface＝三前置→(legacy, why)；缺 cut→理由含 `F3 cut 未發生`。Forbidden＝2.1.0 當 cut、marketplace／plugin cache 當第四前置或路條、只切 graph 契約仍 2.0.0 卻改線、doctor 綠當放行、本 T 改活樹 graph／bump 活樹契約。Compatibility＝未宣告採用端持續舊 7。本 T 不落地條件邊（屬 T-5）。本 T 不測 NEW5 預設五站綠格（屬 T-5）。

## T-5 讓 cut 後新 slug 預設五站且 graph 與路線閘同一三前置
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.5, S-3.6
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, skills/dev-flow/stage2/graph.yaml, skills/dev-flow/stage4/graph.yaml, scripts/fixtures/five-station-f3/new5/cut-ok/
- Verify: `test -d scripts/fixtures/five-station-f3/new5/cut-ok && n=$( { bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK -v; bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK --dual-read undeclared -v; bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK --agree gate-graph -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK && bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK --dual-read undeclared && bash scripts/test-five-station-f3.sh --case NEW5-CUT-OK --agree gate-graph`
  三格皆印 `=== CASE NEW5-CUT-OK`。無旗標＝三前置真、零個 1–7 `.md`→預設五站、無例行 G1／G2 停。`--dual-read undeclared`＝契約仍 `2.0.0` 時條件邊跳過側不得生效。`--agree gate-graph`＝同一組布林下路線閘與下一跳同意，不得「graph 已跳、coordinator 仍 legacy」或反向。
- Blocked-by: T-4
- Risk: high
- Intent: 日常 cut 之後才開、目錄裡還沒有舊站檔的新工作，寫到 Stage 2／4 不該再例行停下來等人蓋 G1／G2。契約還沒宣告 2.1.0 的採用端，即使 hops 檔已經長了條件邊，也必須仍走舊 7。改的是兩站 graph 的條件邊與路線閘同一套三前置，試體是 `new5/cut-ok/`，不是本目錄。不會變成刪掉閘節點、不會只翻函式讓預設路仍進 `N7-g1`。
- Boundaries: 准改模組＝`stage2`／`stage4` `graph.yaml` 條件邊＋路線閘＋上列 cut-ok fixture。機制形＝條件邊＋路線閘讀同一三前置（3C）。Forbidden＝刪 `N7-g1`／`N6-g2` 節點檔、只 hop-skip 不當條件邊、未宣告就讓跳過側生效、拿本目錄／`five-station-f2`／`five-station-simplify` 當 NEW5、活樹 hops 預設五站早於 2.1.0 宣告（活樹 bump 屬 T-7；本 T 條件邊的跳過側對未宣告必須關閉）。Interface＝與路線閘同成功或同失敗。本 T 不改 guide 用字（屬 T-6）。本 T 不寫活樹 cut 檔（屬 T-10）。

## T-6 注入只改用字仍停 N7-g1 該格紅且節點 token 不刪
- [ ] 未完成
- Covers: R-3 / S-3.3, S-3.4
- Files: scripts/test-five-station-f3.sh, guides/guide-dev-flow.html, scripts/fixtures/five-station-f3/new5/graph-word-ne.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/graph-word-ne.md && test -f skills/dev-flow/stage2/nodes/N7-g1.md && test -f skills/dev-flow/stage4/nodes/N6-g2.md && n=$(bash scripts/test-five-station-f3.sh --case GRAPH-WORD-NE -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f3.sh --case GRAPH-WORD-NE && bash scripts/check-gate-tokens.sh`
  GRAPH-WORD-NE 咬「guide 已寫五站、Stage 2 預設仍進 `N7-g1` 卻標成功」。`check-gate-tokens.sh` 只呼叫、不進 Files、不准改。
- Blocked-by: T-5
- Intent: 日常有人只把指南改成「五站」、graph 預設卻還停在 G1，卻說 F3 做完了，這一格必須紅。同一刀要把指南七站單行改成五站用語（交付物），但改完仍不是成功的充分條件。閘節點檔與 G1／G2／`ACCEPTED` 字面都還在。改的是指南用字＋用字空切紅格，不是刪節點、不是改 STATUS。不會變成用語切就算切了。
- Boundaries: 准改模組＝`guides/guide-dev-flow.html` 七站單行＋ GRAPH-WORD-NE 注入稿。Forbidden＝刪節點檔、刪 token、本 PR／本 feature branch 改 `STATUS.md`（看板用語走整合分支 companion）、把本格綠定義成「guide 已寫五站」、把 HOLLOW-WORD 與本格對調（本格咬 graph 仍停；只用字＝hollow 屬 T-10）。節點檔不進 Files（不准改、不准刪）。本 T `git diff` 對 `skills/dev-flow/stage*/nodes/` 必須為空。

## T-7 只把 2.1.0 加進 supported 且 doctor 綠當不成路條
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3, S-4.4, S-4.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, devflow-contract.json, hooks/runtime-capabilities.json, scripts/fixtures/five-station-f3/new5/doctor-honest/, scripts/fixtures/five-station-f3/new5/doctor-ne-ticket/
- Verify: `test -d scripts/fixtures/five-station-f3/new5/doctor-honest && test -d scripts/fixtures/five-station-f3/new5/doctor-ne-ticket && n=$( { bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST -v; bash scripts/test-five-station-f3.sh --case DOCTOR-NE-TICKET -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 2 && bash scripts/test-five-station-f3.sh --case DOCTOR-HONEST && bash scripts/test-five-station-f3.sh --case DOCTOR-NE-TICKET`
  活樹同刀：`devflow_contract_version`＝`2.1.0` 且 `supported_contract_versions` 含字面 `2.1.0`。DOCTOR-HONEST 用 fixture（契約 2.1.0、清單仍只有 2.0.0）必須印 `INCOMPATIBLE` 且非 0。握手語意不准改。
- Blocked-by: T-6
- Intent: 日常把契約升到 2.1.0 時，支援清單要同一刀寫上 `2.1.0`；漏寫就該誠實不相容，不能為了升級好看而放綠。有人剛跑完 doctor 看到相容，就拿這次綠去要五站 hop，必須拒絕，理由是路線還沒切，不能寫「doctor 已經綠所以可以 hop」。改的是契約正本鍵與 supported 清單，不是握手實作、不是 marketplace。不會變成綠＝路條，不會把 cache 當成第四條前置。
- Boundaries: 准改模組＝`devflow-contract.json`（只 bump 正本鍵）＋ `hooks/runtime-capabilities.json`（只加 `2.1.0`）＋上列兩棵 doctor fixture。Forbidden＝改 `hooks/_doctor_impl.py` 握手語意、放寬 2.1.0 ∉ supported 仍 `COMPATIBLE`、把綠定義改成「路線 OK／已切」、marketplace／cache 當 cut 或路條、本 T 寫 cut 紀錄（cut 仍假＝活樹 PRE-210-NE-CUT 態，正確）。Interface＝版本 ∈ supported 才 COMPATIBLE（現況句，不准改）。本 T 結束時 `_doctor_impl.py` 握手段空 diff 或僅非語意註解。

## T-8 摺例行停點不摺完整度且三失敗各自可紅
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.2, S-6.3
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/inject-wait-red.md, scripts/fixtures/five-station-f3/new5/inject-keep-mk-red.md, scripts/fixtures/five-station-f3/new5/inject-keep-ship-mech.md
- Verify: `test -f scripts/fixtures/five-station-f3/new5/inject-wait-red.md && test -f scripts/fixtures/five-station-f3/new5/inject-keep-mk-red.md && test -f scripts/fixtures/five-station-f3/new5/inject-keep-ship-mech.md && n=$(bash scripts/test-five-station-f3.sh --case NEW5-WAIT-RED --case KEEP-MK-RED --case KEEP-SHIP-MECH -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case NEW5-WAIT-RED --case KEEP-MK-RED --case KEEP-SHIP-MECH`
- Blocked-by: T-7
- Risk: high
- Intent: 日常電池要能餵三種壞行為、三格各自紅：謂詞已經真還例行停 G1 或留下「要不要繼續」；Must-keep 任一條紅（缺觀測欄、代填 ACCEPTED、Files 超清單、缺 Verify、reviewer 就是實作者、token 被刪）卻還 hop，還拿「已經 cut 了」當藉口；測試全綠但沒有人在 7-review 頂欄寫 PASS 就標 Ship 做完。改的是三個注入紅格，不是放寬完整度。不會變成只擋其中一條、不會讓「已經切了」把這三格洗綠。
- Boundaries: 准改模組＝F3 電池 KEEP／WAIT 注入跑者＋上列三張具名稿。摺的是例行 `N7-g1`／`N6-g2`，不是 Must-keep、不是 Ship 唯人。Forbidden＝只擋 M11、用 cut 省略完整度、機械綠自動 `verdict: PASS`、把「coordinator 拒 hop」記成這三格綠（極性反了）、Agent 代填 PASS。KEEP-MK 具名例＝M3／M5／M9／M11／M12／M15。本 T 不跑完整 25 格（屬 T-10）。

## T-9 凍結 in-flight 且本目錄／F2／simplify 五站 hop 跳不過
- [ ] 未完成
- Covers: R-7 / S-7.1, S-7.2, S-7.3, S-7.4, S-7.5
- Files: scripts/test-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/old7/
- Verify: `test -d scripts/fixtures/five-station-f3/old7 && n=$(bash scripts/test-five-station-f3.sh --case OLD7-FREEZE --case OLD7-FOLD-RED --case SELF-OLD7 -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f3.sh --case OLD7-FREEZE --case OLD7-FOLD-RED --case SELF-OLD7`
- Blocked-by: T-8
- Intent: 日常已經有舊七站檔的工作必須走完舊路，不能中途被建成五站機；若有人硬寫五站狀態，那一格要紅。對本目錄、對 F2、對 simplify 要求自動前進五站，必須跳不過。NEW5 試體只准用合成根，或 cut 之後才開、當時沒有舊站檔的新目錄。改的是 freeze 與自保，不是發明第一隻活五站名字。不會變成拿本 slug 當白老鼠。
- Boundaries: 准改模組＝路線閘對 in-flight／本目錄／F2／simplify 的拒＋ OLD7 fixture 根。NEW5 試體＝`scripts/fixtures/five-station-f3/new5/`。Forbidden＝本目錄當 NEW5、`five-station-f2`／`five-station-simplify` 當 NEW5、對 OLD7 寫五站狀態（那是 OLD7-FOLD-RED 的注入，不是本綠格）、寫出具體活五站 slug 名當已核目標、僅 html twin 當 in-flight（僅 html 屬 T-10 HOLLOW-HTML-NE-GWT）。電池 Data owner＝OLD7 fixture，不是本目錄 hop 主詞。

## T-10 收口同一電池三路、hollow 與 Files 准許清單
- [ ] 未完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3, S-5.4, S-5.5, S-5.6, S-5.7, S-5.8, S-5.9, S-5.10, S-5.11; R-8 / S-8.2, S-8.3, S-8.4; S-8.1（gate：Stage 4 hop 雙檔已 G2 綠，不准重開）；S-8.5（gate：Q15–Q27 去向已綠）；S-8.6（gate：F2 park D-1／D-2／D-3／F-c-4 不重開）
- Files: scripts/test-five-station-f3.sh, scripts/check-five-station-f3.sh, scripts/five_station_f3.py, scripts/fixtures/five-station-f3/new5/, scripts/fixtures/five-station-f3/old7/, docs/dev/f3-cut-attestation.json, docs/dev/five-station-f3/5-tasks.md, docs/dev/five-station-f3/5-tasks.html, docs/dev/five-station-f3/6-implementation-notes.md, docs/dev/five-station-f3/7-review.md
- Verify: `test -d scripts/fixtures/five-station-f3/new5 && test -d scripts/fixtures/five-station-f3/old7 && n=$(bash scripts/test-five-station-f3.sh -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 25 && bash scripts/test-five-station-f3.sh && bash scripts/test-five-station-f3.sh --help 2>&1 | grep -q -- '--only' && test "$(bash scripts/test-five-station-f3.sh --only new5 >/dev/null 2>&1; echo $?)" -ne 0 && test "$(bash scripts/test-five-station-f3.sh --only old7 >/dev/null 2>&1; echo $?)" -ne 0 && test "$(bash scripts/test-five-station-f3.sh --only token >/dev/null 2>&1; echo $?)" -ne 0 && bash scripts/test-five-station-f2.sh && bash scripts/check-gate-tokens.sh`
  25 個官方 CASE 名都在。`--only new5`／`old7`／`token` 各非 0（缺一路 ≠ 同一電池）。F2 電池與 token 牙只呼叫、不進 Files。可選 check 腳本綠 ≠ 第四條 IFF。
- Blocked-by: T-9
- Risk: high
- Intent: 日常宣稱 F3 完，必須是同一支入口在同一趟把 NEW5、OLD7、TOKEN 三路都跑完才算。只證明函式是真的、檔在、F2 綠、指南改了字、兩支腳本各綠一次、或目錄只有 html，都必須自己紅。活樹這時才寫上三槽紀錄，新工作才真的預設五站。改的是收口對照與活樹 cut 檔，不是順便改 STATUS、不是掃 4-spec 正文當綠。不會變成 hollow F3，不會發明 G3 PASS，不會重開 F2 已停的項。
- Boundaries: 准改模組＝電池入口收口＋活樹 `docs/dev/f3-cut-attestation.json`（三槽；`which_condition` 只命名 cut 位元）＋可選 check 腳本＋本 slug 6／7 過程檔。Interface＝單一 process 三組都跑完才 0；F2 腳本不是入口。Forbidden＝F2 綠寫進 SC-BATTERY IFF、兩支腳本各綠當同一電池、僅 html 當 in-flight GWT、減 Decision 原 20 列、Files 超出 S-8.2、`_templates/`／`_doctor_impl.py` 握手／STATUS／HISTORY／本目錄當 NEW5／刪 token／重開 F2 park 行數 ≠ 0、改 4-spec 頂欄（S-8.1）、把 Q15–Q27 標消失、發明 G3 PASS。Diff Budget 0 區塊命中＝本條紅。HOLLOW-WORD 與 GRAPH-WORD-NE 分帳：前者＝只用字；後者＝graph 仍停卻標成功（已由 T-6 加厚）。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-10 單鏈 | Feature Risk high；cut 讀端／讀鍵／閘／graph／電池改同一家族。Files 重疊時 parallel 會吵 | 4-spec Verification Profile Risk high；使用者 brief「execution.mode sequential」 | 讓 T-6 與 T-7 平行。棄：guide／契約同波難收口 |
| T-1 選 ATTEST-VISIBLE 五切片不當 NEW5-CUT-OK | 最薄端到端是「人指得到三槽、缺了就假」；預設五站是加厚，不是第一刀可觀測主詞 | 4-spec S-1.1／S-1.2；Writer A 主軸 attestation | T-1 先做 NEW5-CUT-OK。棄：還沒有可見紀錄，五站預設是空切 |
| T-3 三切片掛同一官方名 READ-SEAM | 讀縫紅格與正本鍵 2.0.0／2.1.0 是同一讀徑的厚薄，不是三個發明 CASE | 4-spec S-2.1／S-2.2／S-2.3；禁發明通過名 | 發明 `READ-CANON-200`。棄：偷加官方列 |
| T-4 五格具名 PRE（PRE-210-NE-CUT＋PRE-AND 三缺＋PRE-HOPS-200） | standing／Writer A：缺哪一條必須對到理由字面；`-ge 5` 不得兩條 `--case` 倒五行 | 4-spec S-2.4／S-2.5／S-2.6／S-2.7 | 一條 PRE-AND 不含三缺。棄：分不清哪一前置沒測 |
| 活樹 bump＋supported 掛 T-7；活樹 cut 檔掛 T-10 | 同刀加清單（S-4.1）；T-7 後 cut 仍假＝合法 PRE-210-NE-CUT 活態；T-10 才寫三槽讓新 slug 預設五站 | 4-spec S-2.4／S-4.1／S-3.1 | T-5 同時 bump＋寫 cut。棄：沒先證明 2.1.0 ≠ cut |
| T-5 條件邊可先落地、跳過側對未宣告關閉 | dual-read：graph 檔有條件邊 ≠ 未宣告被改線 | 4-spec S-3.2／S-2.7 | T-5 把活樹 hops 預設改五站。棄：違 PRE-HOPS-200 |
| S-8.1／S-8.5／S-8.6 掛 T-10 Covers gate，不另開 T | 49／49 可追；Stage 4 檔集、Disposition、F2 park 已在 G2 綠 | 4-spec S-8.1／S-8.5／S-8.6 | 發明 T-11 重抄 Disposition。棄：水平切帳 |
| 通過條件＝官方 25 名；禁掃 markdown 當 Stage 6 綠 | 發明名與掃 4-spec／5-tasks 字串無鑑別力 | 4-spec S-5.2；F2 standing 同形 | 發明 `ATTEST-OK-PLUS`／python 掃 md。棄：假綠 |
| 不改 doctor 握手／token／STATUS／F2 park | S-8.2 Diff Budget 0；後站不准改成 In | 4-spec S-4.4／S-8.3／S-8.6 | T-7 順便修握手。棄：越刀 |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f3.sh` 不存在 → 十欄皆非零 | 模板 Verify 三律 ③ | 用已綠的 F2 電池當 T-10。棄：違 S-5.6／S-5.7 |
