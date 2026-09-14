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

# 5. 任務 — 五站 F2 coordinator＋slug 倉＋雙路電池（Writer C）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、main tip `475eadc`／#339＋#340）。Lane = **full**。契約不 bump。
> 本 hop **只寫任務雙檔**，不落地 `scripts/`、不改 `STATUS.md`／`HISTORY.md`、不發明 G3、不 merge。
> Knife lock（S-8.9／Out of Scope）：本 slug Stage 5–7 **只 F2**。Files 聯集只准 coordinator＋slug 只增倉＋雙路電池＋RP-9／10／11 讀倉最小接線。**不准** F3 cut、**不准**改 `graph.yaml`、**不准**刪 G1／G2／`ACCEPTED` token、**不准**改 doctor 握手／`_templates/`／契約。
> Diff Budget 0：`guides/` F3 聲明、各站 `graph.yaml`、token 刪檔、`_templates/`、doctor 握手、`devflow-contract.json` bump、`STATUS.md`／`HISTORY.md`。出現＝S-8.9 紅。
> tracer（C 線）：T-1 先打通 **store＋Q12**（第一次成功 persist＝0，NEW5-Q12-ZERO）端到端 RED→GREEN；再加厚跨 run 只增、RP 讀倉、五桶同桶、doctor／路線閘、合法 hop、注入紅格、五問紀錄、Must-keep 全表拒 hop；最後 T-10 才收 **SC-BATTERY 雙路**（檔在／只 F1 綠／只 NEW5 綠皆非 0）。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-7.6／S-8.2）。F2 落地是新家族 `scripts/test-five-station-f2.sh`（加 `scripts/five_station_f2.py`、`scripts/test_five_station_f2.py`），不是改既有 doctor、不是改 `graph.yaml`、不是 F3 cut。
NEW5 試體＝`scripts/fixtures/five-station-f2/new5/`（合成；不當 hop 主詞的 live 目錄）。OLD7 試體＝`scripts/fixtures/five-station-f2/old7/`（已有 1–7 `.md`）。倉路徑形＝`docs/dev/<slug>/.five-station/store`（DD-1；fixture 根下，正本不在 `.devflow/runs/<run_id>/`）。鍵名 OPEN。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
三把 Non-Goals 鎖死，後站不准改成 In：不做 F3 cut；不折 in-flight；不刪 G1／G2／`ACCEPTED`。

## N1 R/S 盤點（70 S；本 hop 承 F2 全落地條）

| R | F2 必須落地的 S | 本 hop T |
|---|---|---|
| R-1 | S-1.1、S-1.3 第一次 persist＝0、初寫不算 hop≤2 | T-1 |
| R-4 | S-4.12 NEW5-Q12-ZERO 綠格 | T-1 |
| R-7 | S-7.7 NEW5 是合成 fixture | T-1 |
| R-1 | S-1.2 其後 +1；S-1.4 NEW5-RUN2；S-1.11 正本不是 run 級 events | T-2 |
| R-1 | S-1.5／S-1.6／S-1.7 RP-9／10／11 讀倉；S-1.8 拒後仍 2；S-1.9 同 mutation；S-1.10 T 重做不混 hop 桶；S-1.12 NEW5-STORE-READ | T-3 |
| R-4 | S-4.11 NEW5-STORE-READ 加列紅格 | T-3 |
| R-2 | S-2.1…S-2.7 五 hop_id、Spec／Build 同桶、七 stem 注入紅、無 proto 桶、舊節點不是 hop_id、不改 graph | T-4 |
| R-4 | S-4.13 NEW5-SPEC-SHARE；S-4.14 NEW5-BUILD-SHARE | T-4 |
| R-3 | S-3.1…S-3.6 doctor／marketplace 是約束、不改 doctor、cache 不是第四條 | T-5 |
| R-7 | S-7.1 三前置缺一 allow_legacy；S-7.2／S-7.3 cache 只選碼、不掃最新 | T-5 |
| R-4 | S-4.2 NEW5-HOP-OK；S-4.3 NEW5-PRED-STOP；S-4.15…S-4.19 五 hop GWT | T-6 |
| R-6 | S-6.2 謂詞真 latch 假立刻 hop | T-6 |
| R-4 | S-4.4…S-4.8 注入壞行為該格紅、極性反了拒 | T-7 |
| R-6 | S-6.3 Ship 無自動 Done；S-6.4 三失敗各自可紅 | T-7 |
| R-5 | S-5.1…S-5.4 五問可指、正本不是 chat／STATUS／attempt、不 bump、鍵名 OPEN | T-8 |
| R-6 | S-6.1／S-6.5 任一 Must-keep 紅拒 hop；S-6.6 去向表完整 | T-9 |
| R-4 | S-4.1 SC-BATTERY；S-4.9／S-4.10 hollow 與 CASE 13 列不減 | T-10 |
| R-7 | S-7.4 OLD7-NO-FIVE；S-7.5 OLD7-TOKEN；S-7.6 OLD7-SELF | T-10 |
| R-8 | S-8.1／S-8.2／S-8.3 三把鎖；S-8.5／S-8.6／S-8.8 hollow；S-8.7 Q 去向；S-8.9 Files 准許清單 | T-10 |

### 已綠／非 Stage 6（不發明實作 T）

| S | 為什麼本 hop 不開落地 T | 去向 |
|---|---|---|
| S-8.4 | 本條觀測的是 **Stage 4 hop** 只 4-spec 雙檔、draft、無自填 G2 PASS。G2 已過（#339）。不是 Stage 6 工作 | 已在 G2 綠。本 hop 只 5-tasks 雙檔，不回改 4-spec、不發明 G3 |

## 本 hop 點名對照稿（Stage 6 才建檔；Verify 必須點到檔名，不是只寫 `-ge N`）

| T | 檔（皆在 `scripts/fixtures/five-station-f2/`） | 紅／綠什麼 |
|---|---|---|
| T-1 | `new5/q12-first-persist/` | 綠：第一次成功 persist 該 hop 桶＝0（NEW5-Q12-ZERO） |
| T-3 | `new5/rp-09-store-cap3.md` | 綠：倉＝2、稿**無**「第 3 次」仍拒第 3 次重寫（NEW5-CAP-3） |
| T-3 | `new5/rp-10-decide-2.md` | 綠：第 2 次 Decide 整站重開拒（NEW5-DECIDE-2） |
| T-3 | `new5/rp-11-goal-2.md` | 綠：第 2 次 Goal 重開拒；Goal+Decide 同 mutation（NEW5-GOAL-2） |
| T-3 | `new5/store-read-text-only.md` | **注入** RP 只咬字樣、不讀倉 → 該格紅（NEW5-STORE-READ） |
| T-4 | `new5/seven-stem-inject.md` | **注入** 七 stem 各一桶 → 該格紅（NEW5-SEVEN-STEM） |
| T-4 | `new5/spec-share/` | 綠：`3-prototype` 與 `4-spec` 同 Spec 桶（NEW5-SPEC-SHARE） |
| T-4 | `new5/build-share/` | 綠：`5-tasks` 與 `6-notes` 同 Build 桶（NEW5-BUILD-SHARE） |
| T-5 | `new5/doctor-compatible-still-old7.md` | 綠：COMPATIBLE 仍拒五站 hop；理由不是「doctor 已綠」 |
| T-7 | `new5/inject-mk-red.md` | **注入** Must-keep 紅仍 hop → 該格紅（NEW5-MK-RED） |
| T-7 | `new5/inject-ship-mech.md` | **注入** 機械綠無人 PASS 卻 Done → 該格紅（NEW5-SHIP-MECH） |
| T-7 | `new5/inject-wait-red.md` | **注入** 謂詞真 latch 假仍等人 → 該格紅（NEW5-WAIT-RED） |
| T-7 | `old7/inject-fold-red.md` | **注入** 對 in-flight 寫五站 → 該格紅（OLD7-FOLD-RED） |
| T-10 | `old7/`（已有 1–7 `.md`） | 綠：無五站寫入、三 cap 不套（OLD7-NO-FIVE） |
| T-10 | `new5/reopen-f3-as-in.md` | 後站把 F3 cut 標 In → 紅（S-8.1） |
| T-10 | `new5/reopen-fold-inflight-as-in.md` | 後站把折 in-flight 標 In → 紅（S-8.2） |
| T-10 | `new5/reopen-delete-tokens-as-in.md` | 後站把刪 token 標 In → 紅（S-8.3） |

## F2 Files 聯集（S-8.9 可核）

Stage 6 全部 T 的 Files 聯集只准這幾條（fixture 目錄當前綴）：

- `scripts/test-five-station-f2.sh`
- `scripts/five_station_f2.py`
- `scripts/test_five_station_f2.py`
- `scripts/fixtures/five-station-f2/`
- `scripts/five_station_f1.py`（只准 RP-9／10／11 改讀 1A 倉；不改字樣牙回歸）
- 本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html（過程檔；各 T 不把過程檔當實作主檔）

超出上列 = L2／違 S-8.9。禁把 `guides/` F3 切線、`graph.yaml`、G1／G2／`ACCEPTED` token 刪檔、`_templates/`、`hooks/_doctor_impl.py`、`devflow-contract.json`、`docs/dev/STATUS.md`、`HISTORY.md` 寫進任一 T 的 Files。

## Verify 開工前原樣跑（2026-09-14；電池尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-10 | `scripts/test-five-station-f2.sh` 不存在 → 非零 | ③綠不了但方向對 |

## T-1 打通第一次 persist 該 hop 桶為 0 的 Q12 縱切
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.3; R-4 / S-4.12; R-7 / S-7.7
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `test -d scripts/fixtures/five-station-f2/new5/q12-first-persist && n=$(bash scripts/test-five-station-f2.sh --case NEW5-Q12-ZERO -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f2.sh --case NEW5-Q12-ZERO`
- Blocked-by: —
- Risk: high
- Intent: 日常第一次把某 hop（例 Spec）寫進合成 NEW5 slug 的倉之後，打開倉就能讀到該桶＝0，而且這次初寫不算進 hop≤2，下一次重寫仍准。改的是 slug 級只增倉與單一電池入口的第一格綠（NEW5-Q12-ZERO），以及合成 fixture 根，不是把本目錄或 `five-station-simplify` 當白老鼠、不是先鋪十八格散文。不會變成 run 級 `events.jsonl` 當倉、不會在本 T 接 RP 字樣牙、不會宣告 F2 完。
- Boundaries: 倉路徑形＝`docs/dev/<slug>/.five-station/store`（fixture 根下；正本不在 `.devflow/runs/<run_id>/`）。Allowed module＝F2 coordinator／電池入口／NEW5 合成 fixture。Forbidden＝拿 `docs/dev/five-station-f2/` 或 `docs/dev/five-station-simplify/` 當 NEW5 主詞、寫 run 級 cap、鎖 JSON 鍵名、改 `graph.yaml`／doctor／token。Data owner＝該合成 slug 的 coordinator 寫者。Test seam＝讀路徑可換 fixture 根。Concurrency：同一初寫重試不得再 +1。本 T 不掛 RP-9／10／11、不跑 OLD7 路、不把「檔在」標 F2 綠。

## T-2 讓其後每次 persist 加一且新 run 讀回來數字仍在
- [ ] 未完成
- Covers: R-1 / S-1.2, S-1.4, S-1.11
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-RUN2 -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 1 && bash scripts/test-five-station-f2.sh --case NEW5-RUN2`
- Blocked-by: T-1
- Risk: high
- Intent: 日常同一 NEW5 slug 第二次、第三次成功 persist 之後，倉裡該桶要走 0→1→2；另開新 `run_id`（新 process）再讀，數字仍是舊的，不是 0。若有人只把三個 cap 寫進 `.devflow/runs/<run_id>/coordinator/events.jsonl`，NEW5-RUN2 必須失敗。改的是倉壽命與讀徑，不是看板、不是 chat。不會變成新 run 暗改 cap（X5）、不會把 run ledger 當正本。
- Boundaries: 正本路徑不得落在 `runs/<run_id>/` 底下。Allowed＝加厚 T-1 倉。Forbidden＝1B run 級 cap、reset 數字再 hop、把 STATUS／chat 當倉。Concurrency：兩 process 同 slug 只增不減；新 `run_id` 不得歸零。本 T 不接 RP 字樣牙、不測五桶分法。

## T-3 讓 RP-9／10／11 改讀倉並讓只咬字樣的路徑變紅
- [ ] 未完成
- Covers: R-1 / S-1.5, S-1.6, S-1.7, S-1.8, S-1.9, S-1.10, S-1.12; R-4 / S-4.11
- Files: scripts/five_station_f2.py, scripts/five_station_f1.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `test -f scripts/fixtures/five-station-f2/new5/rp-09-store-cap3.md && test -f scripts/fixtures/five-station-f2/new5/rp-10-decide-2.md && test -f scripts/fixtures/five-station-f2/new5/rp-11-goal-2.md && test -f scripts/fixtures/five-station-f2/new5/store-read-text-only.md && n=$( { bash scripts/test-five-station-f2.sh --case NEW5-CAP-3 -v; bash scripts/test-five-station-f2.sh --case NEW5-DECIDE-2 -v; bash scripts/test-five-station-f2.sh --case NEW5-GOAL-2 -v; bash scripts/test-five-station-f2.sh --case NEW5-STORE-READ -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --case NEW5-CAP-3 && bash scripts/test-five-station-f2.sh --case NEW5-DECIDE-2 && bash scripts/test-five-station-f2.sh --case NEW5-GOAL-2 && bash scripts/test-five-station-f2.sh --case NEW5-STORE-READ`
- Blocked-by: T-2
- Risk: high
- Intent: 日常 live 第三次重寫時，牙要讀倉裡的 2 並拒、狀態 Escalated、拒後數字仍是 2；稿子就算刪掉「第 3 次」也不能假裝第一次。第 2 次 Decide 整站重開、離開 Intake 後第 2 次 Goal 重開同樣讀倉拒；Goal 連帶 Decide 的兩個數字必須同一次寫入，不得先寫 Goal 成功、Decide 漏寫。T 重做第 2、3、4 次只要沒整站重寫 `5-tasks`／`6-notes`，Build 桶不得 +1。**注入**「RP 只咬 fixture 字樣、不讀倉」時 NEW5-STORE-READ 該格必須獨立紅。改的是 RP 讀倉接線與 cap 算術，不是改 F1 字樣牙回歸、不是放寬三 cap。不會變成 6C、不會 reset 再 hop。
- Boundaries: 只准最小改 `scripts/five_station_f1.py` 讓 RP-9／10／11 讀 1A 倉；F1 十二群字樣牙回歸必須仍綠。Allowed＝F2 倉＋F1 讀倉接線＋上列四張具名 fixture。Forbidden＝刪字樣牙回歸、把數字改小、Goal／Decide 分兩次寫、把 T≤4 與 hop 桶混算、鎖 event 鍵名。Goal+Decide 同一 mutation；只成功一筆＝違 S-1.9。舊 7 走 `allow_legacy()` 不碰這倉。本 T 不改 doctor、不測五桶、不跑 OLD7 折線。

## T-4 讓五站同桶且注入七 stem 各一桶變紅
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3, S-2.4, S-2.5, S-2.6, S-2.7; R-4 / S-4.13, S-4.14
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `test -f scripts/fixtures/five-station-f2/new5/seven-stem-inject.md && test -d scripts/fixtures/five-station-f2/new5/spec-share && test -d scripts/fixtures/five-station-f2/new5/build-share && n=$( { bash scripts/test-five-station-f2.sh --case NEW5-SPEC-SHARE -v; bash scripts/test-five-station-f2.sh --case NEW5-BUILD-SHARE -v; bash scripts/test-five-station-f2.sh --case NEW5-SEVEN-STEM -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --case NEW5-SPEC-SHARE && bash scripts/test-five-station-f2.sh --case NEW5-BUILD-SHARE && bash scripts/test-five-station-f2.sh --case NEW5-SEVEN-STEM`
- Blocked-by: T-3
- Intent: 日常寫 `3-prototype.md` 再寫 `4-spec.md`，加的是同一個 Spec 數字，不是兩個 0；寫 `5-tasks.md` 再寫 `6-implementation-notes.md`，加的是同一個 Build 數字。`hop_id` 只准 Intake／Decide／Spec／Build／Ship，不得寫 `N7-g1`／`N6-g2`／七個 md stem。無 Stage 3 trigger 時不建 `3-prototype`、也不另開 proto 桶。**注入**「七 stem 各一桶各 ≤2」時 NEW5-SEVEN-STEM 該格必須獨立紅；不得把「coordinator 拒寫七 stem」記成此格綠。F2 宣稱完成時 `graph.yaml` 對開工點的 diff 必須空。改的是檔→五站觸發表，不是另寫一份五站 graph。不會變成七個獨立 2、不會偷做 F3。
- Boundaries: 觸發表五桶：`1-discussion`→Intake；`2-decision`→Decide；`3-prototype`｜`4-spec`→同一 Spec；`5-tasks`｜`6-implementation-notes`→同一 Build；`7-review`→Ship。Forbidden＝七 stem 各一桶、舊 graph 節點當 hop_id、另寫五站 graph、改各站 `skills/dev-flow/stage*/graph.yaml`、無 trigger 仍建 proto 桶。Allowed＝F2 coordinator 分桶＋上列 fixture。本 T 不改 RP 接線、不測 doctor 綠。

## T-5 讓 doctor 綠與 marketplace 換 hops 都不能當五站路條
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5, S-3.6; R-7 / S-7.1, S-7.2, S-7.3
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `test -f scripts/fixtures/five-station-f2/new5/doctor-compatible-still-old7.md && n=$(bash scripts/test-five-station-f2.sh --group route -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group route && bash scripts/test-five-station-f1.sh`
- Blocked-by: T-4
- Intent: 日常有人跑完 doctor 看到 `COMPATIBLE`、或只做了 `marketplace update`、或指著「我這份 plugin cache 已有五站 hops」，coordinator 對 live slug 求五站 hop 仍必須拒；理由是「路線未宣告／仍舊 7」，**不含**「doctor 已綠所以可 hop」。缺「契約已宣告 2.1.0」「非 in-flight」「F3 cut 已發生」任一條 → `allow_legacy()`，不建五站機、不套三 cap。cache 只決定本 process 讀哪份 hops **碼**，不掃磁碟上「最新」其他 cache，也不是第四條前置。F1「doctor exit 0 所以可以跟 hops」文案牙必須仍紅。本刀 diff 不含 `hooks/_doctor_impl.py`、不含 marketplace 被改成「綠＝切線」。改的是路線閘，不是修 doctor。不會變成 4B／4C、不會遠端改線。
- Boundaries: 路線閘只讀專案樹契約＋該 slug 是否已有 1–7 `.md`。Allowed＝F2 路線閘＋NEW5 合成路上的約束測。Forbidden＝改 `_doctor_impl.py` 握手語意、把 COMPATIBLE／marketplace update／他份 cache 當 cut、掃最新 cache、把 cache 當第四條前置。讀既有 doctor／契約 2.0.0 當證據，**不准寫進 Files、不准改握手**。F1 十二群是回歸地板，不是本 T 的完成條件。本 T 不跑合法 hop、不折 OLD7。

## T-6 讓謂詞表列真立刻 hop、假則停修且五 hop 可指
- [ ] 未完成
- Covers: R-4 / S-4.2, S-4.3, S-4.15, S-4.16, S-4.17, S-4.18, S-4.19; R-6 / S-6.2
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `n=$( { bash scripts/test-five-station-f2.sh --case NEW5-HOP-OK -v; bash scripts/test-five-station-f2.sh --case NEW5-PRED-STOP -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 2 && bash scripts/test-five-station-f2.sh --case NEW5-HOP-OK && bash scripts/test-five-station-f2.sh --case NEW5-PRED-STOP`
- Blocked-by: T-5
- Intent: 日常合成 NEW5 過了三前置，當下 hop 的表列全真、latch 假、Must-keep 綠、該桶 < 2 時，系統自己前進：Intake→Decide（I1–I4）、Decide→Spec（D1–D4，**不等** G1 `verdict:`）、無 trigger 的 Spec→Build（Sp1–Sp4＋Sp5a＋Sp6，不建 `3-prototype`、不等 G2）、Build→Ship（Bu1–Bu4）。人指得到前進紀錄。任一表列假 → 停該站修，理由含該列，無「要不要繼續／請人審／確認一下」。B1 命中但缺人類 attestation → 不 hop，進 HumanWait。改的是 hop 評表，不是問 owner「可以開下一站」。不會變成中途等人算客氣、不會用「謂詞全真」四字替代表列。
- Boundaries: Coordinator 讀 4-spec「NEW5 自動前進謂詞表」，不讀「謂詞全真」四字。S5a／S5b 互斥：先評 Stage 3 trigger。Ship **無**自動前進列（屬 T-7）。Forbidden＝改問人繞假表列、把 twin URL 當請簽、Agent 寫 attestation、無 trigger 仍強迫 `ACCEPTED`。Audit＝前進紀錄可答五問並指出哪幾列為真（五問落點屬 T-8，本 T 只要求 hop／停修可指）。本 T 是綠格合法行為；注入等人句的紅格屬 T-7。

## T-7 讓注入壞行為的四格各自獨立變紅
- [ ] 未完成
- Covers: R-4 / S-4.4, S-4.5, S-4.6, S-4.7, S-4.8; R-6 / S-6.3, S-6.4
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/, scripts/fixtures/five-station-f2/old7/
- Verify: `test -f scripts/fixtures/five-station-f2/new5/inject-mk-red.md && test -f scripts/fixtures/five-station-f2/new5/inject-ship-mech.md && test -f scripts/fixtures/five-station-f2/new5/inject-wait-red.md && test -f scripts/fixtures/five-station-f2/old7/inject-fold-red.md && n=$( { bash scripts/test-five-station-f2.sh --case NEW5-MK-RED -v; bash scripts/test-five-station-f2.sh --case NEW5-SHIP-MECH -v; bash scripts/test-five-station-f2.sh --case NEW5-WAIT-RED -v; bash scripts/test-five-station-f2.sh --case OLD7-FOLD-RED -v; } 2>&1 | grep -c '^=== CASE') && test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --case NEW5-MK-RED && bash scripts/test-five-station-f2.sh --case NEW5-SHIP-MECH && bash scripts/test-five-station-f2.sh --case NEW5-WAIT-RED && bash scripts/test-five-station-f2.sh --case OLD7-FOLD-RED`
- Blocked-by: T-6
- Risk: high
- Intent: 日常電池要證明壞行為自己會紅，不是證明 coordinator 很會拒絕。分別**注入**：(1) 任一 Must-keep 紅仍 hop；(2) 機械全綠、頂欄 `verdict:` 空白卻標 Ship Done；(3) 謂詞真 latch 假仍留下「要不要繼續／請人審／確認一下」；(4) 對已有 1–7 `.md` 的 OLD7 寫五站狀態。四格各自獨立紅，不能互抵銷。合法行為（立刻 hop、HumanWait 留 Ship、拒折線）不得標成這些紅格的綠。有人把「拒 hop／拒寫」記成紅格綠 → 整電池非 0。改的是 CASE 極性與四張具名注入稿，不是把拒 hop 改名叫綠。不會變成只測 M11、不會讓機械綠自動 Done。
- Boundaries: 極性正本＝4-spec CASE 表「注入該壞行為 → 該格紅」。NEW5-MK-RED 對照物是 M1–M16 **任一**紅仍 hop，不是只餵缺 Verify。Ship 無自動前進；注入 Done 紅，合法 HumanWait 是綠格義務不是本紅格。Forbidden＝極性反了當通過、清回舊 7 當 OLD7-FOLD-RED 綠、三格互抵銷。Test seam＝各 CASE 獨立 exit。本 T 不收 SC-BATTERY 整包（屬 T-10）、不鎖鍵名。

## T-8 留下可指的 hop／latch／cap 紀錄且鍵名保持 OPEN
- [ ] 未完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3, S-5.4
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group events -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group events && test ! -n "$(git diff --name-only -- observability/schema/agent-event.schema.json)"`
- Blocked-by: T-7
- Intent: 日常一次 hop 成功、一次 latch 開火、一次 cap 用盡之後，人要指得到三筆，每筆答得出誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated。只拿出 Cursor chat、`STATUS.md`、或既有 `attempt_completed` 都不算正本。本刀不得 bump `agent-event` schema；後站若把 `event_type=hop_advanced`（或任一具體 JSON 鍵）寫成「Decision／spec 已核必填鍵」＝偷做 annex，必須紅並回 Stage 2。改的是與 1A 同壽命的 slug ledger 可指性，不是觀測棧統一、不是看板。不會變成 bump 採用端 schema、不會鎖鍵名。
- Boundaries: 語意槽可答、鍵名 OPEN。Allowed＝slug ledger（與倉同壽命）。Forbidden＝bump `observability/schema/agent-event.schema.json`、把具體 JSON 鍵當已核、用 chat／STATUS／`attempt_completed` 冒充正本。Compatibility＝採用端契約 schema 仍 1.1 時不得因本刀被 doctor 判 INCOMPATIBLE。本 T 不改 STATUS、不選鍵名當 DD。

## T-9 讓 M1 到 M16 任一紅都拒 hop 且去向表不被標可選
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.5, S-6.6
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group must-keep -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --group must-keep`
- Blocked-by: T-8
- Risk: high
- Intent: 日常 Build 某 T 缺 Verify，或測名無 S-id、某 S 缺觀測欄、代填 `ACCEPTED`、Files 超出聯集、reviewer＝implementer、token 被刪——只要 M1–M16 **任一**紅，coordinator 就不得 hop，理由含該 M 編號；不得用「已經五站了」省略。只擋 M11、其餘 M 紅仍 hop＝本條紅。4-spec Must-keep Disposition 16 列必須仍在、去向不是「可選／Non-Goal 當省略」。改的是自動前進謂詞的完整度閘，不是重寫 brief。不會變成 6B、不會只拿 T Verify 當完整度。
- Boundaries: Must-keep 進 hop 謂詞；少一 M＝違 brief，不得 hop。Allowed＝對照稿 16 份各少一 M（或等價矩陣）＋ M11 缺 Verify 例。Forbidden＝只測 M11、把 M 標可選、把「已經五站了」當 hop 理由。S-6.6 本 T 只核對 4-spec 去向表仍完整，不重寫 Disposition。本 T 的紅是「拒 hop」（合法）；注入「紅仍 hop」的電池紅格已由 T-7 承接。

## T-10 收口雙路電池：兩路都要過、三把鎖不准改成 In、准許清單不越界
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.9, S-4.10; R-7 / S-7.4, S-7.5, S-7.6; R-8 / S-8.1, S-8.2, S-8.3, S-8.5, S-8.6, S-8.7, S-8.8, S-8.9
- Files: scripts/five_station_f2.py, scripts/test-five-station-f2.sh, scripts/test_five_station_f2.py, scripts/fixtures/five-station-f2/new5/, scripts/fixtures/five-station-f2/old7/
- Verify: `test -d scripts/fixtures/five-station-f2/old7 && test -f scripts/fixtures/five-station-f2/new5/reopen-f3-as-in.md && test -f scripts/fixtures/five-station-f2/new5/reopen-fold-inflight-as-in.md && test -f scripts/fixtures/five-station-f2/new5/reopen-delete-tokens-as-in.md && python3 -c "import pathlib,re; t=pathlib.Path('docs/dev/five-station-f2/5-tasks.md').read_text(); files=' '.join(re.findall(r'^- Files: (.+)$', t, re.M)); assert 'graph.yaml' not in files and 'STATUS.md' not in files and '_templates/' not in files and '_doctor_impl.py' not in files and 'devflow-contract.json' not in files; print('T-10-allowlist')" && n=$(bash scripts/test-five-station-f2.sh -v 2>&1 | grep -c '^=== CASE') && test "$n" -ge 18 && bash scripts/test-five-station-f2.sh && ! bash scripts/test-five-station-f2.sh --only new5 && ! bash scripts/test-five-station-f2.sh --only old7 && ! bash scripts/test-five-station-f2.sh --only f1 && bash scripts/test-five-station-f2.sh --case OLD7-NO-FIVE && bash scripts/test-five-station-f2.sh --case OLD7-TOKEN && bash scripts/test-five-station-f2.sh --case OLD7-SELF`
- Blocked-by: T-9
- Risk: high
- Intent: 日常有人宣稱 F2 完，必須是同一支 `scripts/test-five-station-f2.sh` 在**一個 process** 裡把 NEW5 組與 OLD7 組都跑完才 exit 0（SC-BATTERY）。只跑 NEW5、只跑 OLD7、入口只轉呼叫 `test-five-station-f1.sh`、只證明 coordinator 檔在、只證明 F1 十二群綠——皆非 0。OLD7 fixture 已有 1–7 `.md` → 無五站寫入、三 cap 不套、token／G1／G2／`ACCEPTED` 仍在、F1 牙回歸仍綠；對本目錄 `docs/dev/five-station-f2/` 求五站自動前進跳不過。Decision 原 13 列 CASE 名稱都在，只准加列。三張具名稿若把 F3 cut／折 in-flight／刪 token 標成 In／可選，必須紅。本份 5-tasks 的 Files 聯集不得出現 graph／STATUS／模板／doctor／契約。改的是完成定義與三把鎖守門，不是切新 slug 預設、不是改看板。不會變成 hollow F2、不會發明 G3 PASS。
- Boundaries: 單一入口、缺一路即非 0；兩支互不認識的腳本各綠一次 ≠ dual-path。三把鎖後站不准改成 In。Files 聯集＝本檔「F2 Files 聯集」。Forbidden＝把「檔在／F1 綠／只 NEW5-HOP-OK」當完成、減 Decision 原 13 列、改 `guides/` 切五站、改 `graph.yaml`、刪 token、改 STATUS／HISTORY、bump 契約。OLD7-SELF 試體不是把本目錄當 NEW5。Q9–Q24 去向已在 4-spec；本 T 只禁把 Q21／Q22／Q23 標可選。若新檔讓 file-map 紅 → 停、判 L1，不得把既有地板檔預先寫進 Files。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-10 單鏈 | Feature Risk high；C 線指定先 store＋Q12 再加厚，最後才收雙路完成定義。Files 幾乎全重疊同一支 coordinator／電池 | 4-spec Verification Profile Risk high；本 hop C-line brief | parallel。棄：同檔互踩、review 吵、未證明可平行波 |
| T-1 選 Q12 persist＝0 不當電池殼或 RP 牙 | 最薄端到端是「寫一次 → 倉裡是 0 → NEW5-Q12-ZERO 綠」。電池整包是完成定義，不是第一刀可觀測主權 | 4-spec S-1.1／S-4.12；使用者 must-cover store＋Q12 | T-1 先做 SC-BATTERY 空殼。棄：檔在即可綠，正好踩 hollow |
| 單一電池入口 `test-five-station-f2.sh`＋一支 `five_station_f2.py` | Diff Budget coordinator ≤4、入口檔名已由 DD-2 釘死；C 線反 hollow：不先鋪空檔 | 4-spec DD-2；S-4.1；S-8.5 | 每 CASE 一支腳本。棄：兩支互不認識各綠 ≠ dual-path |
| RP 讀倉收進 T-3，不另開 T-11 | 可觀測行為是「牙咬倉裡的 2」，與 Goal+Decide 同 mutation、STORE-READ 紅格同一刀 | 4-spec S-1.5…S-1.12／S-4.11 | 先水平切「倉 API」再切「牙」。棄：水平切層 |
| 五桶＋七 stem 紅收進 T-4 | Spec／Build 同桶與七 stem 注入是同一分桶契約的正反面 | 4-spec R-2；NEW5-SPEC-SHARE／BUILD-SHARE／SEVEN-STEM | 七個 stem 七個 T。棄：水平、稀釋 hop≤2 |
| 合法 hop 與注入紅格拆 T-6／T-7 | 綠格＝合法行為應發生；紅格＝注入壞行為。混在同一 Verify 容易把拒 hop 記成紅格綠 | 4-spec 約束 15；SC-NEW5-MK-RED 極性 | 一 T 跑十八格。棄：極性被平均掉 |
| 事件鍵名 OPEN 獨立 T-8 | 使用者 must-cover events（keys OPEN）；與 hop 評表分開才不會順便鎖鍵 | 4-spec S-5.4；Decision 約束 11 | 在 T-6 順便定 `event_type=hop_advanced`。棄：偷做 annex |
| Must-keep 全表收 T-9，不併進 T-7 | T-7 測的是電池紅格極性；T-9 測的是 coordinator 拒 hop。兩種可觀測，不可互相冒充 | 4-spec S-4.4 vs S-6.5 | 只留 NEW5-MK-RED。棄：只擋 M11 |
| SC-BATTERY＋三把鎖＋OLD7 收 T-10 | C 線完成定義＝同一入口兩路都能獨立紅也能一起綠；三把鎖與 hollow 是收口，不是第一刀 | 4-spec S-4.1／S-8.1…S-8.9；Decision 5A | T-1 先寫「檔在＝開工」。棄：5B。棄：F3／token／graph 寫進 Files |
| S-8.4 不開落地 T | 觀測的是已過的 Stage 4 hop 檔集 | 4-spec S-8.4；本檔已綠表 | 回頭改 4-spec 頂欄。棄：越本 hop 刀 |
| 不改 doctor／graph／token／STATUS | S-8.9 Diff Budget 0；S-3.5／S-2.7／S-8.3 | 4-spec Out of Scope；Hard Files allowlist | 順便切 F3。棄：8B／8C |
| file-map／devflow-check 不進 Files | 既有牙／地板；紅了是 L1 訊號不是本 hop 預授權 | 4-spec S-8.9；`scripts/check-file-map.sh` | T-10 順便改 EXPECTED_MAPPED_FILES。棄：把既有牙寫進 F2 Files |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f2.sh` 不存在 → 十欄皆非零 | 模板 Verify 三律 ③ | 用已綠的 F1 十二群當 T-10 完成。棄：無鑑別力且違 S-8.6 |
