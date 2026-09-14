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

# 5. 任務 — F2 coordinator + slug 倉 + 雙路電池（Writer B）

> 基準:`4-spec.md` G2 PASS（`verdict: PASS`、`status: approved`、DD-1…DD-10 Owner PASS；main tip `475eadc`／#340，規格 #339／#336 Winner B）。Lane = **full**。契約不 bump。
> 本 hop **只寫任務雙檔**，不落地 `scripts/`、不改 `STATUS.md`／`HISTORY.md`、不改 4-spec、不發明 G3、不 merge。
> Knife = **只 F2**：coordinator + slug 級只增倉 + 雙路電池 + RP-9／10／11 讀倉接線。**不是 F3**、**不是改 graph**、**不是刪 token**。
> Scope lock（S-8.9）：Files 聯集只准下面「F2 Files 准許清單」。F3／token 刪檔／`graph.yaml`／`_templates/`／doctor 握手／契約 bump／STATUS／HISTORY Diff Budget **＝0**。
> tracer（B 線）：T-1 先打通 **Q12 第一次 persist＝0 + 新 run 數字仍在** 的倉縱切；再加厚讀倉牙、五桶同桶、doctor 約束、謂詞 hop＋五問紀錄、注入壞行為紅格、Must-keep 全表、OLD7 路，最後同一入口 18 CASE 收口。
> 執行者只准讀本檔 + `4-spec.md` + living／`CONTEXT.md`。禁讀 1／2／3 補洞。鍵名保持 OPEN，不准把具體 JSON 鍵寫成已核。

## 開工前提

Stage 4 已核准。本 slug 自己仍走舊 7（S-7.6）。F2 入口是**新家族** `scripts/test-five-station-f2.sh`（加 `scripts/five_station_f2.py` coordinator／倉／路線閘／hop 評；電池 CASE 可同檔或 `scripts/five_station_f2_battery.py`），不是改 doctor、不是改 `_templates/`、不是 F3 cut。
倉路徑形（DD-1）：`docs/dev/<slug>/.five-station/store`（檔或目錄皆可；正本不在 `.devflow/runs/<run_id>/`）。鍵名 OPEN。
NEW5 fixture 根（DD-3）：`scripts/fixtures/five-station-f2/new5/`（合成；不是本目錄、不是 `five-station-simplify`）。
OLD7 fixture 根（DD-4）：`scripts/fixtures/five-station-f2/old7/`（已有 1–7 `.md`）。
RP-9／10／11 最小接線可改 `scripts/five_station_f1.py` 讀倉；F1 字樣牙留回歸，不得替代 1A 倉。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
Decision 原 13 列 CASE 只准加；本 hop 承接 13＋加列 5＝18 名，減一列＝翻 Decision。
紅格極性＝**注入該壞行為 → 該格獨立紅**。把「coordinator 拒 hop」記成紅格綠＝極性反了，已拒。

### 本 hop 點名對照（Stage 6 才建檔；Verify 必須點到 CASE 名）

| T | 路／CASE | 紅／綠什麼 |
|---|---|---|
| T-1 | NEW5-Q12-ZERO | 綠：第一次成功 persist＝0，不算進 hop≤2 |
| T-1 | NEW5-RUN2 | 綠：新 `run_id` 再讀，數字仍在、不是 0 |
| T-2 | NEW5-CAP-3 | 綠：第 3 次 hop 重寫讀倉拒；Escalated；拒後仍是 2 |
| T-2 | NEW5-STORE-READ | **注入** RP 只咬 fixture「第 3 次」字樣、不讀倉 → **該格紅** |
| T-3 | NEW5-DECIDE-2 | 綠：第 2 次 Decide 整站重開讀倉拒 |
| T-3 | NEW5-GOAL-2 | 綠：離開 Intake 後第 2 次 Goal 重開讀倉拒；Goal+Decide 同 mutation |
| T-4 | NEW5-SPEC-SHARE | 綠：`3-prototype` 與 `4-spec` 同一 Spec 桶 |
| T-4 | NEW5-BUILD-SHARE | 綠：`5-tasks` 與 `6-notes` 同一 Build 桶 |
| T-4 | NEW5-SEVEN-STEM | **注入** 七 stem 各一桶 → **該格紅** |
| T-5 | SC-DOCTOR | COMPATIBLE 時拒五站 hop；理由是路線，不是「doctor 已綠」 |
| T-6 | NEW5-HOP-OK | 綠：謂詞表列全真、latch 假、Must-keep 綠 → hop；五問可答 |
| T-6 | NEW5-PRED-STOP | 綠：謂詞假 → 不 hop、停修、不留要不要繼續 |
| T-7 | NEW5-MK-RED | **注入** Must-keep 紅仍 hop → **該格紅** |
| T-7 | NEW5-SHIP-MECH | **注入** 機械綠無人 PASS 卻 Done → **該格紅** |
| T-7 | NEW5-WAIT-RED | **注入** 謂詞真 latch 假仍等人 → **該格紅** |
| T-7 | OLD7-FOLD-RED | **注入** 對 in-flight 寫五站 → **該格紅** |
| T-8 | Must-keep 16 份 | 任一 M1–M16 紅 → 合法拒 hop（綠格義務，不是 NEW5-MK-RED） |
| T-9 | OLD7-NO-FIVE | 綠：已有 1–7 `.md` → 無五站狀態；三 cap 不套 |
| T-9 | OLD7-TOKEN | 綠：token／G1／G2／`ACCEPTED` 仍在；F1 牙回歸仍綠 |
| T-9 | OLD7-SELF | 綠：對本目錄求五站自動前進跳不過 |
| T-10 | SC-BATTERY | 單一入口；NEW5+OLD7 都過才 exit 0；缺一路／只轉 F1 → 非 0 |

### N1 R/S 盤點（70 S；本 hop 承 F2 必須落地的 S）

| R | F2 必須落地的 S | 本 hop T |
|---|---|---|
| R-1 | S-1.1、S-1.2、S-1.3、S-1.4、S-1.11；S-4.12（NEW5-Q12-ZERO） | T-1 |
| R-1 | S-1.5、S-1.8、S-1.12；S-4.11（NEW5-STORE-READ） | T-2 |
| R-1 | S-1.6、S-1.7、S-1.9、S-1.10 | T-3 |
| R-2 | S-2.1…S-2.7；S-4.13、S-4.14 | T-4 |
| R-3／R-7 | S-3.1…S-3.6；S-7.1、S-7.2、S-7.3 | T-5 |
| R-4／R-5／R-6 | S-4.2、S-4.3、S-4.15…S-4.19；S-5.1…S-5.4；S-6.2 | T-6 |
| R-4／R-6 | S-4.4…S-4.8；S-6.3、S-6.4 | T-7 |
| R-6 | S-6.1、S-6.5 | T-8 |
| R-7 | S-7.4、S-7.5、S-7.6、S-7.7 | T-9 |
| R-4／R-8 | S-4.1、S-4.9、S-4.10；S-8.1、S-8.2、S-8.3、S-8.5、S-8.6、S-8.8、S-8.9 | T-10 |

### 已綠／本 hop 不開 T（不是 F2 實作工作）

| S | 為什麼本 hop 不開 T | 去向 |
|---|---|---|
| S-6.6 | M1–M16 去向表已在 4-spec、G2 已核；F2 不重做 Disposition | 已綠。T-8 只落地「任一 M 紅拒 hop」，不改表 |
| S-8.4 | 本條是 Stage 4 hop 檔集（當時只 4-spec 雙檔）。G2 已過。不是 Stage 6 工作 | 已過。本 PR 只 5-tasks 雙檔 |
| S-8.7 | Q9–Q24 去向已在 4-spec Real-world Disposition | 已綠。後站不得把 Q21／Q22／Q23 標可選（T-10 Boundaries） |

### F2 Files 准許清單（S-8.9 可核）

Stage 6 全部 T 的 Files 聯集只准：

- `scripts/test-five-station-f2.sh`
- `scripts/five_station_f2.py`
- `scripts/five_station_f2_battery.py`（選配；CASE 跑者若拆檔）
- `scripts/five_station_f1.py`（只准 RP-9／10／11 改讀倉，不改字樣牙回歸）
- `scripts/fixtures/five-station-f2/`
- 本目錄 `5-tasks.md`／`6-implementation-notes.md`／`7-review.md` 及其 html

超出上列 = L2／違 S-8.9。禁把 `guides/` F3 切線、`skills/dev-flow/stage*/graph.yaml`、G1／G2／`ACCEPTED` token 刪檔、`_templates/`、`hooks/_doctor_impl.py`、`devflow-contract.json`、`docs/dev/STATUS.md`／`HISTORY.md` 寫進任一 T 的 Files。

### Verify 開工前原樣跑（2026-09-14；F2 電池尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-10 | `scripts/test-five-station-f2.sh` 不存在 → 非零 | ③綠不了但方向對 |

## T-1 打通第一次 persist＝0 且新 run 再讀數字仍在
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4, S-1.11; R-4 / S-4.12
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-Q12-ZERO --case NEW5-RUN2 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f2.sh --case NEW5-Q12-ZERO --case NEW5-RUN2`
- Blocked-by: —
- Risk: high
- Intent: 日常第一次把某 hop 寫進倉，數字是 0 不是 1，還准再重寫兩次；第二次、第三次成功 persist 才變成 1、2。另開一個 process／新 run_id 再讀，三個數字還在，不是被清空成 0。改的是 slug 級只增倉與電池入口骨架，不是把計數塞進 `.devflow/runs/<run_id>/coordinator/events.jsonl`，也不是先鋪十八格散文。不會變成「檔在就算 F2 完」、不會在本 T 評 hop 謂詞、不會鎖 JSON 鍵名。
- Boundaries: 准改模組＝F2 coordinator／倉＋電池入口＋NEW5 fixture 根。Data owner＝該 slug 的 coordinator 寫者。倉路徑形＝`docs/dev/<slug>/.five-station/store`（DD-1）；正本禁止落在 `runs/<run_id>/`。Interface＝`persist(hop_id)` 成功→桶 0 然後 +1；寫失敗不 hop、不暗減。Concurrency：新 run 不得歸零；兩 process 只增不減。Idempotency：同一初寫重試不得再 +1。Forbidden＝run 級 cap、改 doctor／graph／token、拿本目錄當 NEW5、本 T 寫完整 hop 評。Test seam＝讀路徑可換 fixture 根。本 T 不掛 F1 字樣牙當完成。

## T-2 讓第三次 hop 重寫讀倉拒且只咬字樣的牙該格紅
- [ ] 未完成
- Covers: R-1 / S-1.5, S-1.8, S-1.12; R-4 / S-4.11
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/five_station_f1.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-CAP-3 --case NEW5-STORE-READ -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f2.sh --case NEW5-CAP-3 --case NEW5-STORE-READ`
- Blocked-by: T-1
- Intent: 日常同一 hop 已經寫到桶＝2 時，第三次重寫必須被拒、狀態 Escalated、數字仍是 2；理由指到倉裡的 2，不是稿子上有沒有「第 3 次」。若有人把 RP-9／10／11 仍只餵字樣牙、不讀倉，電池 NEW5-STORE-READ **該格必須獨立紅**，字樣牙綠不得標 F2 成功。改的是 cap 牙改讀 1A 倉（可動 `five_station_f1.py` 最小接線），不是放寬 hop≤2、不是 reset 再 hop。不會變成 6C（繼續只咬字樣）、不會把手改小數字當合法。
- Boundaries: 准改模組＝slug 倉讀徑＋F1 RP-9 最小接線。cap teeth 讀倉；字樣牙只回歸。Test seam＝倉＝2 且對照稿**刪掉**「第 3 次」。Forbidden＝改字樣牙回歸讓它不再紅、把「coordinator 拒 hop」記成 NEW5-STORE-READ 綠、reset 計數再 hop（X5）、改 doctor。本 T 不接 Decide／Goal 重開（屬 T-3）。Error＝超 cap → Escalated，數字不減。

## T-3 讓 Decide／Goal 重開讀倉拒且兩計數同一次寫入
- [ ] 未完成
- Covers: R-1 / S-1.6, S-1.7, S-1.9, S-1.10
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/five_station_f1.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-DECIDE-2 --case NEW5-GOAL-2 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f2.sh --case NEW5-DECIDE-2 --case NEW5-GOAL-2`
- Blocked-by: T-2
- Intent: 日常已經 hop 出 Decide 之後，第二次整站重開 Decide 必須讀倉被拒；已經離開 Intake 之後，第二次改 Goal 也必須被拒，而且這次寫入要把 `goal_reopen` 與連帶的 `decide_reopen` **同一 mutation** 寫進去，不得先寫 Goal 成功、Decide 漏寫。Build 裡某 T 重做第 2 次（仍 ≤4）**不得**讓 Build hop 桶 +1；只有整份 `5-tasks.md` 或 `6-implementation-notes.md` 被整站重寫才加 Build 桶。改的是 RP-10／11 讀倉與一次寫，不是兩套上限混算。不會變成分兩次寫躲 Decide cap、不會把 T 重做算成 hop 重寫。
- Boundaries: 准改模組＝倉 mutation＋RP-10／11 讀倉。Transaction＝Goal+Decide **同一 mutation**；只成功一筆＝違 S-1.9。舊 7 不走此流。Forbidden＝分倉、把 T≤4 混進 hop 桶、把 `5-tasks`／`6-notes` 拆成兩個 stem 桶（同桶屬 T-4）、鎖鍵名。Interface＝Goal reopen 兩計數同進或同失敗。本 T 不測七 stem。

## T-4 讓五站五桶且 Spec／Build 同桶、注入七 stem 該格紅
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3, S-2.4, S-2.5, S-2.6, S-2.7; R-4 / S-4.13, S-4.14
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-SPEC-SHARE --case NEW5-BUILD-SHARE --case NEW5-SEVEN-STEM -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --case NEW5-SPEC-SHARE --case NEW5-BUILD-SHARE --case NEW5-SEVEN-STEM`
- Blocked-by: T-3
- Intent: 日常寫 `3-prototype.md` 再寫 `4-spec.md`，加的是同一個 Spec 數字，不是兩個 0；寫 `5-tasks.md` 再寫 `6-implementation-notes.md`，加的是同一個 Build 數字。`hop_id` 只准 Intake／Decide／Spec／Build／Ship 五字。無 Stage 3 trigger 時不建 `3-prototype`、也不另開 proto 桶。若有人注入「七個 stem 各一桶、各 ≤2」，NEW5-SEVEN-STEM **該格必須獨立紅**——不得把「coordinator 拒寫七 stem」記成此格綠。改的是檔→五站觸發表，不是改 `graph.yaml`、不是用 `N7-g1`／`N6-g2` 冒充 hop_id。不會變成七 stem、不會另寫一份五站 graph。
- Boundaries: 准改模組＝hop 觸發表（五桶）。Forbidden dependencies＝改各站 `graph.yaml`、把舊節點當 hop_id、七 stem 各一桶、無 trigger 仍建 proto 桶。Data owner＝該 slug 站檔寫入。本 T 結束時 `git diff` 對 `skills/dev-flow/stage*/graph.yaml` 必須為空。Test seam＝注入七 stem 行為紅。本 T 不評 doctor 路線。

## T-5 讓 doctor 綠與 marketplace／cache 當不成 hop 通行證
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5, S-3.6; R-7 / S-7.1, S-7.2, S-7.3
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group doctor-route -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --group doctor-route`
- Blocked-by: T-4
- Intent: 日常有人剛跑完 doctor、看到 COMPATIBLE／exit 0，就要求對 live slug 走五站 hop，必須拒絕；理由字面是「路線未宣告」或「仍舊 7」，**不含**「doctor 已綠所以可 hop」。只做了 marketplace update、契約仍 2.0.0，路線仍舊 7。三前置（宣告 2.1.0 ∧ 非 in-flight ∧ F3 cut 已發生）缺一條就 `allow_legacy()`，不建五站機。「我已在 plugin cache」不是第四條；不得掃全機最新 cache 改線。F1「doctor exit 0 所以可以跟 hops」文案牙仍紅。改的是路線閘，不是改 `hooks/_doctor_impl.py`、不是改 marketplace。不會變成 4B／4C（綠或 cache 當路條）。
- Boundaries: 准改模組＝路線閘。Data owner＝專案樹契約 + 該 slug 是否已有 1–7 `.md`。Allowed＝讀 host plugin root（只選碼）。Forbidden＝doctor 綠當路條、marketplace update 當 cut、掃最新 cache、把 cache 當第四前置、改 `_doctor_impl.py` 握手語意、bump `devflow-contract.json`。Interface＝三前置布林；缺一 → allow_legacy；2.0.0 握手綠仍舊 7。讀 doctor 只當證據，**不准列入 Files、不准改握手**。SC-DOCTOR 本 T 必須可測。本 T 不對本目錄開五站機（屬 T-9）。

## T-6 讓謂詞表列真立刻 hop、假則停修、紀錄答五問
- [ ] 未完成
- Covers: R-4 / S-4.2, S-4.3, S-4.15, S-4.16, S-4.17, S-4.18, S-4.19; R-5 / S-5.1, S-5.2, S-5.3, S-5.4; R-6 / S-6.2
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-HOP-OK --case NEW5-PRED-STOP -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-five-station-f2.sh --case NEW5-HOP-OK --case NEW5-PRED-STOP`
- Blocked-by: T-5
- Intent: 日常 NEW5 合成 fixture 過了三前置，當下 hop 的謂詞表列全真、latch 假、Must-keep 綠，系統必須**自己 hop**，不准留下「要不要繼續／請人審／確認一下」。缺觀測欄或 OC 未裁就停該站修，理由指到那一列假，不改問人。四個自動前進 hop 都要看得到：Intake→Decide（I1–I4）、Decide→Spec（D1–D4，不等 G1 verdict）、Spec→Build 無 trigger（Sp1–Sp4＋Sp5a＋Sp6，不建 3-prototype、不等 G2）、Build→Ship（Bu1–Bu4）。B1 命中但沒有人類 attestation 不得離 Spec。每一次 hop／一次 latch／一次 cap 用盡，人指得到紀錄且能答五問（誰／從哪到哪／哪條謂詞／哪只 cap／是否 Escalated）；正本不是 chat、不是 STATUS、不是 `attempt_completed`。改的是 hop 評＋slug ledger，不是 bump `agent-event`、不是鎖 `event_type=hop_advanced`。不會變成中途等人客氣、不會把鍵名寫成已核。
- Boundaries: 准改模組＝hop evaluator + slug ledger（與 1A 同壽命）。讀 4-spec「NEW5 自動前進謂詞表」，不讀「謂詞全真」四字。Forbidden＝bump `observability/schema/agent-event.schema.json`、把具體 JSON 鍵當本 Decision 已核、正本寫進 chat／STATUS／`attempt_completed`、問要不要繼續、Agent 代寫 attestation。Ship **無**自動前進列（屬 T-7／S-6.3）。Compatibility＝不 bump agent-event。鍵名 OPEN。Audit＝五問可答。本 T 的 NEW5-HOP-OK 必須涵蓋四 hop 各至少一筆 `=== CASE`（加 PRED-STOP 與 Sp5b 無 attestation，故 `-ge 6`）。

## T-7 注入 Must-keep 紅／機械 Done／等人／折線讓該格獨立紅
- [ ] 未完成
- Covers: R-4 / S-4.4, S-4.5, S-4.6, S-4.7, S-4.8; R-6 / S-6.3, S-6.4
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/five_station_f2_battery.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case NEW5-MK-RED --case NEW5-SHIP-MECH --case NEW5-WAIT-RED --case OLD7-FOLD-RED -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-five-station-f2.sh --case NEW5-MK-RED --case NEW5-SHIP-MECH --case NEW5-WAIT-RED --case OLD7-FOLD-RED`
- Blocked-by: T-6
- Risk: high
- Intent: 日常電池必須能**餵壞行為**讓四格各自紅：Must-keep 任一紅卻仍 hop（NEW5-MK-RED；只測 M11、放過其餘 M＝本格紅）；機械全綠、頂欄 `verdict:` 空白卻標 Ship Done（NEW5-SHIP-MECH；合法是 HumanWait，不是此紅格綠）；謂詞真 latch 假卻留下要不要繼續（NEW5-WAIT-RED）；對已有 1–7 `.md` 的 fixture 寫五站狀態（OLD7-FOLD-RED）。把「coordinator 拒 hop／拒寫」標成這些紅格綠＝極性反了，整電池必須非 0。三失敗不得互抵銷。改的是電池紅格測法，不是把拒 hop 改記成綠。不會變成「檔在／只 F1 綠／只 NEW5 綠」當成功（那是 T-10 hollow）。
- Boundaries: 准改模組＝F2 電池 CASE 跑者。Data owner＝合成 NEW5 + OLD7 fixture。Test seam＝各 CASE 獨立 exit；紅格只接受注入壞行為的紅。Forbidden＝極性反了仍標 F2 成功、只測 M11 當完整 Must-keep、把清回舊 7 記成 OLD7-FOLD-RED 綠、Ship 自動 Done。Error／State seam＝注入缺 Verify／代填 PASS／等人句／折線寫入。`five_station_f2_battery.py` 可省略（CASE 留在 `five_station_f2.py`），但若拆檔必須在本 T Files。本 T 不跑完整 18 格（屬 T-10）。

## T-8 讓任一 Must-keep 紅就拒 hop 且不只擋 M11
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.5
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --group must-keep -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 16 && bash scripts/test-five-station-f2.sh --group must-keep`
- Blocked-by: T-7
- Intent: 日常有人缺了 T 的 Verify、或測名沒 S-id、或 reviewer＝implementer、或 token 被刪，coordinator 評該 hop 必須**不 hop**，理由含該 M 編號；不得用「已經五站了所以可 hop」。十六份對照各少一條 M1–M16，十六份都要停。這是合法拒（綠格義務）。T-7 的 NEW5-MK-RED 是**注入仍 hop** 才紅，兩格不得對調。改的是自動前進謂詞含完整度，不是重寫 brief 的 M 表（S-6.6 已綠）。不會變成只擋 M11、不會把 Must-keep 標可選。
- Boundaries: 准改模組＝hop evaluator 的 Must-keep 列（Bu4／各 hop）。Test seam＝16 份各少一 M 的對照稿（例：M11 缺 Verify；M1 測名無 S-id；M3 缺觀測欄；M5 代填 `ACCEPTED`；M9 Files 超出聯集；M12 reviewer＝implementer；M15 token 被刪）。Forbidden＝只擋 M11、把 M 標可選／Non-Goal、用「已經五站了」省略。S-6.6 去向表不准在本 T 改寫。本 T 不刪 token 真檔（M15 用 fixture）。

## T-9 讓 OLD7 不建五站機且本目錄五站 hop 跳不過
- [ ] 未完成
- Covers: R-7 / S-7.4, S-7.5, S-7.6, S-7.7
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh --case OLD7-NO-FIVE --case OLD7-TOKEN --case OLD7-SELF -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-five-station-f2.sh --case OLD7-NO-FIVE --case OLD7-TOKEN --case OLD7-SELF`
- Blocked-by: T-8
- Intent: 日常已有 1–7 `.md` 的 slug 必須沒有五站狀態寫入、三 cap 不套，可走既有 T 上限 4；token／G1／G2／`ACCEPTED` 仍在，F1 十二群回歸仍綠。對 `docs/dev/five-station-f2/` 要求五站自動前進必須跳不過，目錄仍是舊 7 站檔。NEW5 試體路徑必須是 `scripts/fixtures/five-station-f2/new5/`，不是本目錄、不是 `five-station-simplify`。改的是 OLD7 路與自保，不是折 in-flight、不是拿本 slug 當白老鼠。不會變成對 live 建五站機。
- Boundaries: 准改模組＝路線閘對 in-flight／本目錄的拒 + OLD7 fixture。NEW5 試體＝DD-3 合成根。Forbidden＝本目錄當 NEW5、`five-station-simplify` 當 NEW5、對 OLD7 寫五站狀態（那是 T-7 OLD7-FOLD-RED 的注入，不是本綠格）、刪 token。OLD7-TOKEN 可呼叫既有 `scripts/check-gate-tokens.sh` 與 `scripts/test-five-station-f1.sh`，**不准把它們列入 Files、不准改**。電池 Data owner＝OLD7 fixture，不是本目錄 hop 主詞。

## T-10 收口同一電池 18 CASE、三把鎖與 Files 准許清單
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.9, S-4.10; R-8 / S-8.1, S-8.2, S-8.3, S-8.5, S-8.6, S-8.8, S-8.9
- Files: scripts/test-five-station-f2.sh, scripts/five_station_f2.py, scripts/five_station_f2_battery.py, scripts/five_station_f1.py, scripts/fixtures/five-station-f2/
- Verify: `n=$(bash scripts/test-five-station-f2.sh -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 18 && bash scripts/test-five-station-f2.sh`
- Blocked-by: T-9
- Risk: high
- Intent: 日常宣稱 F2 完，必須是**同一支** `scripts/test-five-station-f2.sh` 在同一 process 把 NEW5 組與 OLD7 組都跑完才 exit 0。缺一路、跳過一路、入口只 exec `test-five-station-f1.sh`、只證明 coordinator 檔在、只 F1 十二群綠、只 NEW5-HOP-OK 綠 → 整電池非 0。18 個 CASE 名都在（Decision 原 13 + 加列 5），一格都不能少，加列不得把「檔在」加成通過條件。完成樹沒有 F3 cut 把新 slug 預設改五站、沒有把 in-flight 折成五站、沒有刪 G1／G2／`ACCEPTED`；後站不准把這三把改成 In。Files 聯集不超出准許清單；`guides/` F3、`graph.yaml`、token 刪檔、`_templates/`、doctor 握手、契約 bump、STATUS／HISTORY 行數＝0。改的是收口對照，不是順便切 graph。不會變成 hollow F2、不會發明 G3 PASS。
- Boundaries: 准改模組＝電池入口收口（可動上列五條 impl／fixture）。Interface＝單一 process 兩組都跑完才 0；F1 腳本不是入口。Forbidden＝F3 cut 改成 In、折 in-flight 改成 In、刪 token 改成 In、把 Q21／Q22／Q23 標可選、減 Decision 原 13 列、Files 超出 S-8.9 准許清單。Diff Budget 0 區塊命中＝本條紅。本 T Verify 是 SC-BATTERY 全入口（`-ge 18` 含 NEW5-* 與 OLD7-* 全名）；Q12／五桶／doctor／注入紅／五問／Must-keep／路線閘已由 T-1…T-9 加厚，本 T 驗它們能在同一入口一起綠、也能在缺一路時一起非 0。禁改 STATUS／HISTORY。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`；Blocked-by 成 T-1→…→T-10 單鏈 | Feature Risk high；倉／牙／閘／hop／電池改同一支 `five_station_f2.py`。Files 重疊時 parallel 會吵 | 4-spec Verification Profile Risk high；使用者 B-line brief「Prefer sequential」 | 讓 T-4 與 T-5 平行。棄：同檔 overlap |
| T-1 選 Q12＋RUN2 不當 NEW5-HOP-OK | 最薄端到端是「倉真的寫了、跨 run 還在」；hop 謂詞是加厚，不是第一刀可觀測主詞 | 4-spec S-1.1／S-1.4；B 線主軸③ Q12 | T-1 先做 hop-ok。棄：還沒有倉，hop 數字假 |
| 單一檢查家族 `test-five-station-f2` | Diff Budget 入口 1 檔；SC-BATTERY 禁兩支腳本各綠 | 4-spec DD-2；S-4.1 | 每 CASE 一支 sh。棄：hollow 變種 |
| RP 讀倉掛 T-2／T-3，可動 `five_station_f1.py` | B 線主軸①；S-8.9 准最小接線；字樣牙留回歸 | 4-spec S-1.5…S-1.7／S-1.12；S-8.9 | 本 hop 另造第二家族牙。棄：爆檔數 |
| 紅格與合法拒拆成 T-7／T-8 | 極性反了會把拒 hop 測成 NEW5-MK-RED 綠；S-6.5 是 16 份合法拒 | 4-spec 約束 15；S-4.8 | 一 T 兼紅格與拒 hop。棄：測法對調 |
| S-6.6／S-8.4／S-8.7 不開 T | 去向表與 Stage 4 檔集已在 G2 綠；使用者禁發明 G3、禁改 4-spec | 本檔已綠表；4-spec S-8.4 是當時 hop | 為 Disposition 重開 T-11。棄：水平切帳 |
| 不改 doctor／graph／token／STATUS | S-8.9 Diff Budget 0；三把鎖後站不准改成 In | 4-spec S-3.5／S-2.7／S-8.1…S-8.3／S-8.9 | T-5 順便修 doctor。棄：越刀 |
| 鍵名 OPEN、不 bump agent-event | Decision 約束 11；S-5.3／S-5.4 | 4-spec R-5 | T-6 鎖 `event_type=hop_advanced`。棄：偷做 annex |
| Verify 開工前實跑（2026-09-14） | `scripts/test-five-station-f2.sh` 不存在 → 十欄皆非零 | 模板 Verify 三律 ③ | 用已綠的 F1 十二群當 T-10。棄：違 S-8.6 |
