---
feature: five-station-f2
stage: 7-review
status: draft
verdict:
owner: s7-writer-a
reviewers: []
updated: 2026-09-14
---

# 7. 驗證 —— **不是 G3 PASS**（Writer A 審查草稿；F2 only）

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
> | 5 | **抽驗一列** | 本場 twin 第五格鎖 Coverage 中位列 **S-4.1**。打開 `scripts/test-five-station-f2.sh:1-15`（單一入口 `exec python3 five_station_f2.py`）、`scripts/five_station_f2.py:33-38`（官方 18 名）、`scripts/five_station_f2.py:1131-1147`（`--only new5&#124;old7&#124;f1` → exit 3）。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡**。本檔是 **Writer A** 獨立審查草稿。`verdict:` **空**（語意＝NOT_REVIEWED）。`status: draft`。**未發明 Human G3 PASS**。機械全綠 ≠ 人簽。D-1／D-2／D-3 等 owner 接受／park，本 reviewer **不代填 G3**。
> 產品碼樹 = `origin/main` tip `#351`=`858336e`（RR2 已合）。本 PR **只** `7-review.md` + `7-review.html`。Scope = **F2 only**。不宣稱 F3 cut。STATUS 另 companion。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | `s7-writer-a`（fresh-context Cloud Agent Writer A；**≠** Stage 6 實作 owner `implementer-A`／#346／#349） |
| Stage 6 實作 | `implementer-A`（#346）；standing rework #349。獨立 T 審：R2+#347、R1+#348、RR1+#350、RR2+#351。**都不是** G3 |
| Human G3 | **未簽**。`verdict:` 空＝NOT_REVIEWED。`reviewers: []`。Agent **禁寫** Human PASS |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、70 S） ②`5-tasks.md`（T-1…T-10；`status: approved`＝N1-arm，checkbox 未勾） ③`scripts/test-five-station-f2.sh` + `scripts/five_station_f2.py` + fixtures ④`git diff 4516fe0..858336e`（#346…#351 vs Stage 6 STATUS） ⑤親跑電池／hollow／spec-gate／file-map／token／F1 回歸 → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-1／D-2／D-3 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 session runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 `main` tip `#351`=`858336e`。審核樹 Source SHA = `858336e9441cec636549b3dc2d35ef273e03794f`。本 PR **只** 7-review 雙檔。Knife = **F2 only**。不改 STATUS。**不發明 Human G3** |
| 可信／打折 | 機械數字（18 CASE／failed=0／hollow exit 3／spec-gate 9/9／file-map 210）以本場親跑為準。F-id 分級與「owner 接不接受 D-1／D-2／D-3」打折——本檔只列、不代決 |
| 建議 reviewer 路徑 | ①適格人類 owner rick 抽驗 S-4.1 三個 `檔:行` ②讀 Known Limits #1–#3 明示接受或打回 ③人親寫頂欄 `verdict:`（PASS／REQUEST_CHANGES／HOLD）。**全勾 ≠ PASS** |

## Coverage Matrix

自建（grep 官方 `=== CASE`／`--group` ↔ 4-spec 70 S；**未先讀** Self-Review）。本表列 **F2 必須落地的 S** + 回歸末列。F3 切線見附錄 A2，不標 ✅。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `NEW5-Q12-ZERO`；`five_station_f2.py:171-179` persist first=0 | ✅ |
| S-1.2 | `NEW5-Q12-ZERO`；`:187-193` 其後 +1 | ✅ |
| S-1.3 | `NEW5-Q12-ZERO`；初寫不算 hop≤2 | ✅ |
| S-1.4 | `NEW5-RUN2`；新 process 仍 2/0/0 | ✅ |
| S-1.5 | `NEW5-CAP-3`；`:181-186` 倉＝2 拒第 3 次；fixture 無「第 3 次」 | ✅ |
| S-1.6 | `NEW5-DECIDE-2`；RP-10 讀倉 | ✅ |
| S-1.7 | `NEW5-GOAL-2`；RP-11 讀倉 | ✅ |
| S-1.8 | `NEW5-CAP-3`；拒後仍 2、reset hop 拒 | ✅ |
| S-1.9 | `NEW5-GOAL-2`；`goal_reopen:239-257` 同 mutation | ✅ |
| S-1.10 | `NEW5-GOAL-2`；T retry ≠ hop 桶 | ✅ |
| S-1.11 | `NEW5-Q12-ZERO`／`NEW5-RUN2`；倉不在 `runs/` | ✅ |
| S-1.12 | `NEW5-STORE-READ`；`string_only_cap_red:549` 不讀倉＝紅格 | ✅ |
| S-2.1 | `NEW5-SPEC-SHARE`；hop_id 只五站 | ✅ |
| S-2.2 | `NEW5-SPEC-SHARE`；3-proto／4-spec 同 Spec 桶 | ✅ |
| S-2.3 | `NEW5-BUILD-SHARE`；5-tasks／6-notes 同 Build 桶 | ✅ |
| S-2.4 | `NEW5-SEVEN-STEM`；注入七 stem＝紅格 | ✅ |
| S-2.5 | `NEW5-SPEC-SHARE`；`persist:160-161` 拒 Stage3；無 proto 檔／無 Stage3 桶 | ✅ |
| S-2.6 | `NEW5-SPEC-SHARE`；`N7-g1`／`N6-g2` 不是 hop_id | ✅ |
| S-2.7 | `git diff --name-only 4516fe0..858336e` 零 `graph.yaml` | ✅ |
| S-3.1 | `--group doctor-route`；`refuse_hop_reason:296-308` 理由是路線 | ✅ |
| S-3.2 | `--group doctor-route`；marketplace／cache ≠ 路條 | ✅ |
| S-3.3 | `--group doctor-route`；契約仍 2.0.x | ✅ |
| S-3.4 | `test-five-station-f1.sh` S-5.6 文案牙仍紅 | ✅ |
| S-3.5 | #346…#351 未改 `hooks/_doctor_impl.py` | ✅ |
| S-3.6 | `--group doctor-route`；cache 不是第四前置 | ✅ |
| S-4.1 | 入口 exit 0；`--only new5&#124;old7&#124;f1` 各 exit 3（本場抽驗列） | ✅ |
| S-4.2 | `NEW5-HOP-OK`；`--hop I D Sp Bu` 綠 hop | ✅ |
| S-4.3 | `NEW5-PRED-STOP`；`why==Sp2`；未 hop Spec→Build | ✅ |
| S-4.4 | `NEW5-MK-RED`；`inject=mk-hop` 該格紅 | ✅ |
| S-4.5 | `NEW5-SHIP-MECH`；`inject=ship-done` 該格紅 | ✅ |
| S-4.6 | `NEW5-WAIT-RED`；`inject=wait` 該格紅 | ✅ |
| S-4.7 | `OLD7-FOLD-RED`；注入五站寫入＝紅格 | ✅ |
| S-4.8 | 四紅格皆餵 inject 壞行為；拒 hop 不當綠 | ✅ |
| S-4.9 | `--only` 三探針 exit 3；檔在／只 F1／只 NEW5 ≠ F2 完 | ✅ |
| S-4.10 | `OFFICIAL` 18 名＝Decision 13＋加列 5；無發明名 | ✅ |
| S-4.11 | 同 S-1.12 `NEW5-STORE-READ` | ✅ |
| S-4.12 | 同 S-1.1 `NEW5-Q12-ZERO` | ✅ |
| S-4.13 | 同 S-2.2 `NEW5-SPEC-SHARE` | ✅ |
| S-4.14 | 同 S-2.3 `NEW5-BUILD-SHARE` | ✅ |
| S-4.15 | `--hop I`；Intake→Decide；無請人審 | ✅ |
| S-4.16 | `--hop D`；Decide→Spec；不等 G1 | ✅ |
| S-4.17 | `--hop Sp`；Spec→Build 無 trigger；不建 3-prototype | ✅ |
| S-4.18 | `--hop Sp5b`；無 attestation → HumanWait | ✅ |
| S-4.19 | `--hop Bu`；Build→Ship Bu1–Bu4 | ✅ |
| S-5.1 | `--group events` n=3（hop／latch／cap）；五問可答 | ✅ |
| S-5.2 | events 正本＝slug ledger，不是 chat／STATUS | ✅ |
| S-5.3 | #346…#351 未 bump `agent-event` schema | ✅ |
| S-5.4 | 鍵名 OPEN；5-tasks／6-notes 未把 JSON 鍵寫成已核 | ✅ |
| S-6.1 | `--group must-keep` M11 overlay 拒 hop（理由含 M11） | ✅ |
| S-6.2 | `NEW5-HOP-OK`；無「要不要繼續／請人審」 | ✅ |
| S-6.3 | `NEW5-SHIP-MECH`；機械綠不得 Done | ✅ |
| S-6.4 | MK／SHIP／WAIT 三格各自紅 | ✅ |
| S-6.5 | `--group must-keep` 16 份 overlay；各 `ok=False`、`why`＝該 M、未 hop→Ship | ✅ |
| S-6.6 | 4-spec Must-keep Disposition 16 列；G2 已核；T-8 Covers gate | ✅ |
| S-7.1 | `OLD7-NO-FIVE`；三前置缺 → `allow_legacy:281-293` | ✅ |
| S-7.2 | `--group doctor-route`；cache 只選碼 | ✅ |
| S-7.3 | 同 S-7.2；不掃全機最新 cache | ✅ |
| S-7.4 | `OLD7-NO-FIVE`；1–7 `.md`；無五站機 | ✅ |
| S-7.5 | `OLD7-TOKEN`；token 牙＋F1 回歸綠 | ✅ |
| S-7.6 | `OLD7-SELF`；本目錄不得自動前進 | ✅ |
| S-7.7 | NEW5 根＝`scripts/fixtures/five-station-f2/new5/` | ✅ |
| S-8.1 | `f3_cut_happened:276-278` 恆 False；無 F3 預設切線 | ✅ |
| S-8.2 | OLD7／本目錄仍舊 7 | ✅ |
| S-8.3 | `check-gate-tokens.sh` 全過；token 未刪 | ✅ |
| S-8.4 | Stage 4 hop 已 G2（#339）；本場不重開 4-spec 頂欄 | ✅ |
| S-8.5 | `--only`／完成條件要求電池，檔在不算完 | ✅ |
| S-8.6 | `--only f1` exit 3；F1 綠 ≠ F2 完 | ✅ |
| S-8.7 | 4-spec Disposition Q9–Q24 有去向；Q21–Q23 未標可選 | ✅ |
| S-8.8 | `--only new5` exit 3 | ✅ |
| S-8.9 | Files 聯集 ⊆ 准許清單；D-1 四檔＝documented L1（見 KL #1），不是 F3／graph／token | ✅ |
| 既有測試套件(回歸) | `bash scripts/test-five-station-f1.sh`；`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`；`bash scripts/check-file-map.sh`；`bash scripts/check-gate-tokens.sh` | ✅ |

**回歸末行（Writer A @ `858336e`）**：電池 `=== CASE`＝18、`failed=0`、exit 0。`--only new5&#124;old7&#124;f1` 各 exit 3。未知 `--only bogus` exit 2。`--help` 含 `--only`。spec-gate `9/9`（70 S）。file-map `scanned=210`。token 守衛全過。F1 `failed=0`（63 CASE）。

## Verification Evidence

<!-- Final Fresh 在 ALREADY_SYNCED 之後重綁當下 main tip（步 2c 路徑①）。
     產品碼樹 = origin/main after #346…#351。本 PR 後續只加本雙檔，不改牙。 -->

- Source SHA: 858336e9441cec636549b3dc2d35ef273e03794f
- Final Fresh Run ID: f2-s7a-fresh-858336e-20260914
- Entry point: `bash scripts/test-five-station-f2.sh`（F2 Conditional 已落地 → 本場當 Required：NEW5+OLD7 單一入口）然後 hollow `--only new5&#124;old7&#124;f1`；形狀層 `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`） | `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md` | pass | exit 0; 9/9; 70 S | |
| token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F2 電池列 Required | `bash scripts/check-gate-tokens.sh` | pass | exit 0; G1/G2/G3 token 未增刪 | |
| test-five-station-f2 | `bash scripts/test-five-station-f2.sh -v` | pass | exit 0; failed=0; CASE=18 | |
| hollow --only new5 | `bash scripts/test-five-station-f2.sh --only new5` | pass | exit 3; 印 hollow --only new5 | |
| hollow --only old7 | `bash scripts/test-five-station-f2.sh --only old7` | pass | exit 3; 印 hollow --only old7 | |
| hollow --only f1 | `bash scripts/test-five-station-f2.sh --only f1` | pass | exit 3; F1-only is not F2 complete | |
| unknown --only | `bash scripts/test-five-station-f2.sh --only bogus` | pass | exit 2（用法；不得當 hollow 綠） | |
| doctor-route group | `bash scripts/test-five-station-f2.sh --group doctor-route -v` | pass | exit 0; failed=0 | |
| must-keep group | `bash scripts/test-five-station-f2.sh --group must-keep -v` | pass | exit 0; 16 overlay 各拒 | |
| events group | `bash scripts/test-five-station-f2.sh --group events -v` | pass | exit 0; CASE=3 官方名 | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | exit 0; failed=0; CASE=63 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=210; table_rows=220 | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| e2e／Playwright | | n-a | | Explicitly excluded；F2 無產品 UI |
| Race／stress | | n-a | | Explicitly excluded；Concurrency 以 NEW5-RUN2 新 process 再讀為準 |
| Windows 真機 | | n-a | | Explicitly excluded |
| F3 cut／graph 切線 | | n-a | | Out of Scope；本場不跑、不宣稱 |

八點機械面（G3 錨全文）見附錄 A5。指向 **單一電池 + hollow**，不是「檔在」或「只 F1 綠」。**八點齊 ≠ Human G3 PASS**。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得只咬 fixture「第 3 次」字樣（S-1.12、S-4.11） | `NEW5-STORE-READ`；`caps_from_store=False` | pass |
| 不得把 cap 放 run 級 events（S-1.4、S-1.11） | `NEW5-RUN2`；倉路徑禁 `runs/` | pass |
| 不得七 stem 各一桶（S-2.4） | `NEW5-SEVEN-STEM` | pass |
| 不得把 doctor 綠當 hop 通行證（S-3.1） | `--group doctor-route` | pass |
| 不得把拒 hop 當紅格綠（S-4.8） | MK／SHIP／WAIT／FOLD 皆 inject | pass |
| 不得 Goal／Decide 分兩次寫躲 cap（S-1.9） | `goal_reopen` 同 mutation | pass |
| 不得只跑 NEW5 或只轉 F1（S-4.1、S-4.9、S-8.8） | `--only new5&#124;f1` exit 3 | pass |
| 不得對本目錄建五站機（S-7.6） | `OLD7-SELF` | pass |
| 不得本 hop 自填 G3 PASS（S-8.4 同族） | 本檔 `verdict:` 空；`status: draft` | pass |
| 不得減 Decision 原 13 列（S-4.10） | `OFFICIAL` 18＝13+5 | pass |
| 不得只擋 M11（S-6.5） | must-keep 16 overlay | pass |
| 不得 F3 cut／刪 token／改 graph（S-8.1…S-8.3、S-8.9） | diff 零 graph／token 刪檔／契約 bump | pass |
| 不得把 F3／折線／刪 token 改成 In | 5-tasks／6-notes 仍 Out | pass |
| 不得鎖 JSON 鍵名（S-5.4） | 鍵名 OPEN | pass |
| 不得 bump agent-event（S-5.3） | 無 schema bump | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#346／#349 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **s7-writer-a 2026-09-14 親跑** `bash scripts/test-five-station-f2.sh -v` 與 hollow／`--group`（不採信 6-notes 貼文）。長輸出見附錄 A4。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 第一次成功 persist＝0 | `[ok] S-1.1 first persist=0`；retry 同寫 | ✅ |
| S-1.2 | 其後 +1 | `[ok] S-1.2 second persist=1` | ✅ |
| S-1.3 | 初寫不算 hop≤2 | `[ok] S-1.3 two rewrites after first` | ✅ |
| S-1.4 | 新 run_id 數字仍在 | `[ok] S-1.4 new process still 2/0/0` | ✅ |
| S-1.5 | 第 3 次讀倉拒；fixture 無「第 3 次」 | `[ok] S-1.5 third rewrite refused`；Escalated | ✅ |
| S-1.6 | 第 2 次 Decide 讀倉拒 | `[ok] S-1.6 second Decide reopen refused` | ✅ |
| S-1.7 | 第 2 次 Goal 讀倉拒 | `[ok] S-1.7 second Goal refused` | ✅ |
| S-1.8 | 拒後仍 2 | `[ok] S-1.8 still 2`；`no reset hop` | ✅ |
| S-1.9 | Goal+Decide 同 mutation | `[ok] S-1.9 Goal+Decide same mutation` | ✅ |
| S-1.10 | T retry ≠ hop | `[ok] S-1.10 T retry ≠ hop` | ✅ |
| S-1.11 | 正本不在 `runs/` | `[ok] S-1.11 store not run-level` | ✅ |
| S-1.12 | 只咬字樣＝該格紅 | `[ok] S-1.12/S-4.11 string-only miss is the red cell` | ✅ |
| S-2.1 | hop_id 五字 | `[ok] S-2.1 only five hop_id` | ✅ |
| S-2.2 | Spec 同桶 | `[ok] S-2.2/S-4.13 same Spec bucket` | ✅ |
| S-2.3 | Build 同桶 | `[ok] S-2.3/S-4.14 same Build bucket` | ✅ |
| S-2.4 | 七 stem 注入紅 | `[ok] S-2.4 seven-stem injection is the red cell` | ✅ |
| S-2.5 | 無 proto 桶 | `[ok] S-2.5 persist refuses Stage3 bucket` | ✅ |
| S-2.6 | 舊節點不是 hop_id | `[ok] S-2.6 old graph nodes are not hop_id` | ✅ |
| S-2.7 | 不改 graph | `git diff --name-only` 無 `stage*/graph.yaml` | ✅ |
| S-3.1 | COMPATIBLE 仍拒 hop；理由是路線 | `[ok] S-3.1 reason is not doctor-green ticket` | ✅ |
| S-3.2 | update／cache ≠ cut | `[ok] S-3.2/S-3.6 marketplace+cache ≠ ticket` | ✅ |
| S-3.3 | 2.0.0+hops 仍違規 | `[ok] S-3.3 contract still 2.0.x` | ✅ |
| S-3.4 | F1「跟 hops」文案仍紅 | F1 `test_s_5_6_*` red=True | ✅ |
| S-3.5 | 不改 doctor | diff 無 `_doctor_impl.py` | ✅ |
| S-3.6 | cache 不是第四前置 | `[ok] S-3.6 cache is not a fourth precondition` | ✅ |
| S-4.1 | 兩路都過才 0；缺一路非 0 | 入口 0；`--only`×3 皆 3（抽驗列） | ✅ |
| S-4.2 | HOP-OK 綠 | `--hop I/D/Sp/Bu` failed=0 | ✅ |
| S-4.3 | PRED-STOP 綠；理由謂詞假 | `[ok] S-4.3 predicate false → no hop (got Sp2)` | ✅ |
| S-4.4 | 注入 MK 紅仍 hop＝該格紅 | `[ok] S-4.4 inject MK-red still hop is the red cell` | ✅ |
| S-4.5 | 注入機械 Done＝該格紅 | `[ok] S-4.5 inject mechanical Done is the red cell` | ✅ |
| S-4.6 | 注入等人句＝該格紅 | `[ok] S-4.6 inject 要不要繼續 is the red cell` | ✅ |
| S-4.7 | 注入折 OLD7＝該格紅 | `[ok] S-4.7 inject five-station write on OLD7` | ✅ |
| S-4.8 | 極性＝注入壞行為 | 四紅格皆 inject；合法拒在 must-keep 綠義務 | ✅ |
| S-4.9 | 三 hollow | `--only new5&#124;old7&#124;f1` exit 3 | ✅ |
| S-4.10 | 18 名不減 | `grep -c '^=== CASE'`＝18；名＝OFFICIAL | ✅ |
| S-4.11 | 同 S-1.12 | STORE-READ 紅格 | ✅ |
| S-4.12 | 同 S-1.1 | Q12-ZERO 綠 | ✅ |
| S-4.13 | 同 S-2.2 | SPEC-SHARE 綠 | ✅ |
| S-4.14 | 同 S-2.3 | BUILD-SHARE 綠 | ✅ |
| S-4.15 | I1–I4 hop | `[ok] S-4.15 Intake→Decide hop I1–I4` | ✅ |
| S-4.16 | D1–D4；不等 G1 | `[ok] S-4.16 no wait for G1` | ✅ |
| S-4.17 | Sp 無 trigger | `[ok] S-4.17 no 3-prototype created` | ✅ |
| S-4.18 | Sp5b 無 attestation | `[ok] S-4.18 Sp5b no attestation → HumanWait` | ✅ |
| S-4.19 | Bu1–Bu4 | `[ok] S-4.19 Build→Ship Bu1–Bu4` | ✅ |
| S-5.1 | 三類紀錄＋五問 | events：hop／latch／cap 各至少一 | ✅ |
| S-5.2 | 正本不是 STATUS | `[ok] S-5.2 original is slug ledger` | ✅ |
| S-5.3 | 不 bump schema | 無 `agent-event.schema.json` diff | ✅ |
| S-5.4 | 鍵名 OPEN | 5-tasks／6-notes 無已核鍵名 | ✅ |
| S-6.1 | M11 缺 Verify 拒 hop | must-keep `11-m11.md` why=M11 | ✅ |
| S-6.2 | 謂詞真立刻 hop | `[ok] S-6.2 no please-review` | ✅ |
| S-6.3 | Ship 無自動 Done | SHIP-MECH 紅格 | ✅ |
| S-6.4 | 三失敗各自紅 | MK／SHIP／WAIT 三 CASE 獨立 | ✅ |
| S-6.5 | 任一 M 紅拒 hop | 16× `ok=False`、`did not hop to Ship` | ✅ |
| S-6.6 | Disposition 16 列 | 4-spec 表在；無「可選」 | ✅ |
| S-7.1 | 缺前置 → legacy | `[ok] S-7.1 in-flight → legacy` | ✅ |
| S-7.2 | cache 只選碼 | doctor-route marketplace+cache | ✅ |
| S-7.3 | 不掃最新 cache | 同 S-7.2；`allow_legacy` 忽略 cache | ✅ |
| S-7.4 | OLD7 無五站機 | `[ok] S-7.4 no five-station machine` | ✅ |
| S-7.5 | token＋F1 | `[ok] S-7.5 tokens still present`；F1 綠 | ✅ |
| S-7.6 | 本目錄跳不過 | `[ok] S-7.6 this slug cannot auto-advance` | ✅ |
| S-7.7 | NEW5＝合成 fixture | `[ok] S-7.7 NEW5 is synthetic fixture` | ✅ |
| S-8.1 | 不做 F3 cut | `f3_cut_happened` return False；guide 無預設切五站 | ✅ |
| S-8.2 | 不折 in-flight | OLD7／本目錄仍舊 7 | ✅ |
| S-8.3 | 不刪 token | token 牙 exit 0 | ✅ |
| S-8.4 | Stage 4 檔集已過；本場不代填 G2／G3 | 4-spec `verdict: PASS` 是 Human G2；本檔 G3 空 | ✅ |
| S-8.5 | 檔在 ≠ 完 | 完成條件＝S-4.1 入口 | ✅ |
| S-8.6 | F1 綠 ≠ 完 | `--only f1` exit 3 | ✅ |
| S-8.7 | Q9–Q24 去向 | Disposition 表；Q21–Q23 下落是 S | ✅ |
| S-8.8 | 只 NEW5 ≠ 完 | `--only new5` exit 3 | ✅ |
| S-8.9 | Files 准許＋Budget 0 | 准許清單內檔＋D-1 四檔具名 L1；graph／token／契約＝0 | ✅ |

## 截圖槽

本場無產品 UI（F2 = coordinator／slug 倉／CLI 電池）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = dual-path selftest CASE + hollow exit 3
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F2 coordinator 是 slug 倉 + 電池，不是現場交接 UI。有 Operational Context 的 S 以「寫手／coordinator／Ship 審查者」走一遍；標不適用的純內部 S 不裝成人員旅程。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.5 | coordinator／F2 牙 | live 第三次重寫看得見 | 倉＝2 拒 hop；Escalated | 人明示下一手 | Escalated 等人；禁 reset | 拒；數字仍 2 |
| S-3.1 | 採用 owner | 綠≠切線 | doctor COMPATIBLE 仍拒五站 hop | 人跑 doctor | 宣告 2.1.0 之前舊 7 | 理由是路線 |
| S-4.2 | coordinator | 表列真立刻 hop | HOP-OK 四 hop | 中間不簽 | 中間不停 | hop 發生 |
| S-4.3 | 寫手 | 假謂詞就修檔 | PRED-STOP 停 Spec | 不口頭繞 | 停到謂詞真 | why=Sp2 |
| S-4.5 | Ship 審查者 | 出貨仍由人寫頂欄 | 注入 Done＝紅格 | 人打開審頁 | 無逾時自動 Done | HumanWait 義務 |
| S-4.6 | coordinator／寫手 | 中間不等 | 注入等人句＝紅格 | 不准把 twin 當請簽 | 中間不停 | 該格紅 |
| S-4.15 | coordinator／寫手 | Intake 表列真就進 Decide | `--hop I` | 不在 Intake 簽 | 中間不停 | from-to 對 |
| S-4.17 | coordinator | 無 trigger 不產 Demo | `--hop Sp` | 不簽 Demo | 不 latch | 無 3-prototype |
| S-4.18 | Demo 參與者 | 互動未核不得離 Spec | `--hop Sp5b` | 人親填 attestation | HumanWait | 未 hop Build |
| S-6.1 | 寫手／T reviewer | 完整度留下 | M11 overlay 拒 hop | 補 Verify | 停 Build | why=M11 |
| S-6.5 | 寫手／coordinator | 任一 M 紅不得 hop | 16 overlay | 補該 M | 停該站 | 16 份未 hop Ship |
| S-7.2 | 兩台機器寫手 | 不得遠端改線 | cache 新仍舊 7 | 各機自己 update | 無 | 碼新路舊 |
| S-1.1 等算術／極性／檔集 | — | — | — | — | — | 不適用（純內部） |

六條檢查：技術通過但人無法完成工作／看得見沒決策權／等待誤標完成／系統外無法追蹤／中斷無法恢復／資訊過期或多人同時 —— 本場電池路徑未命中「誤標完成」（SHIP-MECH 反而是注入紅）。**人仍必須自己寫 G3 頂欄**；本檔空欄就是這條還沒走完。

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中。F2 讀 F1 `evaluate` 只接 RP-9／10／11 讀倉；未改 doctor 握手。`allow_legacy` 把 doctor／marketplace／cache 當約束丟棄。
2. **資料所有權被繞過寫入**:未命中。倉 owner＝該 slug coordinator；正本 `docs/dev/<slug>/.five-station/store`；禁 `runs/<id>/`。
3. **相容性破壞包成新增**:未命中。契約仍 2.0.0；無新公開 doctor API；`agent-event` 未 bump。
4. **一致性邊界被拆解**:未命中。`goal_reopen` 與 `decide_reopen` 同一次 `save_store`（S-1.9）。
5. **宣告的 Test seam 未被使用**:未命中。seam＝單一入口 `test-five-station-f2.sh`、`--only`、官方 CASE 名、`evaluate_hop(inject=)`。selftest 走同一 `persist`／`evaluate_hop`。
6. **Known design limit 被實作悄悄「解決」**:未命中。`f3_cut_happened` 仍 False；F3 未切。鍵名仍 OPEN。D-1 是 CI 註冊 L1，不是把 S-8.9「F3／token／graph＝0」修掉。

任一命中 → 至少 🟡。本場無未授權 Boundary 變更。D-1／D-2／D-3 是 L1 記帳，不是 Boundary 繞過。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更。

- F-s7-1 🟡 D-1(L1) host CI 註冊四檔（`check-file-map.sh` EXPECTED 208→210、`devflow-check.sh` 註冊電池、`test-architecture-guards.sh`、`guides/guide-dev-flow.html` **檔案地圖列**）超出 5-tasks／4-spec S-8.9 准許清單正文。R1 曾 CHALLENGE 應 L2；R2／RR1／RR2 **CONCUR L1**。本場獨立再評：**CONCUR L1**（縮了 CI 自審紅；guide 變的是地圖列不是 F3 cut；未改 graph／token／契約）。**不代 owner 接受**。見 KL #1
- F-s7-2 🟢 D-2(L1) fixture 超 Stage 4「≤12」估計。tracked fixtures＝49（含 16 份 must-keep + 具名 hop／注入）。不動 R/S。見 KL #2
- F-s7-3 🟢 D-3(L1) `5-tasks.md` `status: approved` 只為 N1-arm／graph P0。checkbox 未勾。不是 G3。見 KL #3
- F-s7-4 🟢 `--group doctor-route` 第 4 格仍掛 `NEW5-Q12-ZERO` 名（T-5 殘）。內容是 S-3.6 cache 不是第四前置，不是發明 `NEW5-MKTG-*`。不升 🟡
- F-s7-5 🟢 `five_station_f2.py` 1158 行單檔。4-spec 未另鎖 F2 行數上限；不拆第二家族（會撞 Files 格）。誠實範圍，不是 L2
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。D-1 是 host 註冊 L1，不是切五站預設

## Spec Axis

逐 R。F3 條標「本場不宣稱符合」。Deviations：D-1／D-2／D-3 如實，無隱藏 L2。

| R | 判定 | 證據 |
|---|---|---|
| R-1 | **符合（F2）** | S-1.1…S-1.12 Coverage ✅。persist first=0、新 process 仍 2、讀倉拒第 3／Decide／Goal |
| R-2 | **符合（F2）** | S-2.1…S-2.7。Spec／Build 同桶；七 stem 紅；無 graph diff |
| R-3 | **符合（F2）** | S-3.1…S-3.6。doctor 綠≠路條；未改 `_doctor_impl.py` |
| R-4 | **符合（F2）** | S-4.1…S-4.19。18 CASE；hollow exit 3；紅格極性＝注入 |
| R-5 | **符合（F2）** | S-5.1…S-5.4。events 三官方名；鍵名 OPEN；schema 未 bump |
| R-6 | **符合（F2）** | S-6.1…S-6.6。16 M overlay 拒 hop；三失敗可紅 |
| R-7 | **符合（F2）** | S-7.1…S-7.7。本目錄／OLD7 不建五站機；NEW5＝合成 fixture |
| R-8 | **符合（本場責任）** | S-8.1…S-8.3／S-8.5…S-8.8 ✅。S-8.4 已 G2。S-8.9＝准許清單 + **D-1 L1 具名**（見 KL #1）。**不宣稱 F3** |
| D-1(L1) | 如實；**待 owner 接受／park** | file-map 210；四檔具名。本場 CONCUR L1，不升 L2、不代 G3 |
| D-2(L1) | 如實；**待 owner 接受／park** | 估計 vs 具名 16+hop／注入 |
| D-3(L1) | 如實；**待 owner 接受／park** | `status: approved`＝N1-arm |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit |

作者 Self-Review ①–⑧：電池 CASE 含 S-id、未發明 G3、D-1／D-2／D-3 對得上、DBC 未偷偷修 limit —— 與本場實跑一致。5-tasks checkbox 保持未勾＝誠實（T 審在 6-notes，不靠勾選冒充 G3）。T-5 殘（doctor-route 第 4 格掛 Q12 名）作者與 RR2 已記；本場不另開 🔴。

## 變更架構圖

必須對上 #346…#351 basename（本 PR 只加 `7-review.md`／`7-review.html`）。

```text
[test-five-station-f2.sh] ----exec----> [five_station_f2.py]
                                          +-- persist / persist_stem
                                          +-- goal_reopen (Goal+Decide one save)
                                          +-- allow_legacy / refuse_hop_reason
                                          +-- evaluate_hop(inject=) / pred_false
                                          +-- Battery OFFICIAL 18 CASE
                                          +-- --only new5|old7|f1 → exit 3
[five_station_f1.py evaluate] --caps_near--> slug store (RP-9/10/11)
                                          string regex kept as regression
fixtures/five-station-f2/new5/   NEW5 合成（不是本 slug、不是 simplify）
fixtures/five-station-f2/old7/   OLD7 1-7 .md
D-1 floor (not 5-tasks Files union body):
  check-file-map.sh  EXPECTED=210
  devflow-check.sh   architecture 註冊 F2 電池
  test-architecture-guards.sh  靜態釘
  guide-dev-flow.html          filemap 列（非 F3 cut）
NOT in this knife:
  graph.yaml / _templates/ / doctor handshake / contract bump / F3 cut
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

審核的產品碼 = `4516fe0..858336e`（#346 實作 → #349 standing → #350 RR1 → #351 RR2）。中間 STATUS companion 不在本 PR。本 Stage 7 PR 只新增本雙檔。共同戰場已是送審樹本身（見 2c）。

<details>
<summary title="+1158/-0; persist + evaluate_hop + Battery"><code>scripts/five_station_f2.py</code> (+1158/-0)</summary>
<pre><span class="add">+OFFICIAL = 18 CASE names</span>
<span class="add">+def persist(...)  # first=0 then +1; hop_id in PROTO_HOPS refuse</span>
<span class="add">+def goal_reopen(...)  # Goal+Decide one mutation</span>
<span class="add">+def allow_legacy(...)  # doctor/marketplace/cache discarded</span>
<span class="add">+def evaluate_hop(..., inject=)  # pred_false / must-keep / red-cell inject</span>
<span class="add">+--only new5|old7|f1 → return 3</span></pre>
</details>

<details>
<summary title="+15/-0; 入口"><code>scripts/test-five-station-f2.sh</code> (+15/-0)</summary>
<pre><span class="add">+exec python3 five_station_f2.py --root "$ROOT" "$@"</span></pre>
</details>

<details>
<summary title="+15/-1; RP-9/10/11 讀倉"><code>scripts/five_station_f1.py</code> (+15/-1)</summary>
<pre><span class="add">+if caps_from_store: caps = f2.caps_near(path)  # RP-9/10/11</span>
<span class="add">+string regex remains</span></pre>
</details>

<details>
<summary title="fixtures 目錄"><code>scripts/fixtures/five-station-f2/*</code>（tracked 49）</summary>
<pre>new5 hop-ok／pred-stop／hop-sp5b／must-keep 01–16／inject-*／q12／share／old7 1–7 + fold。完整 diff 在 #346／#349。</pre>
</details>

<details>
<summary title="D-1 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code> · <code>guides/guide-dev-flow.html</code></summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 208</span>
<span class="add">+EXPECTED_MAPPED_FILES = 210</span>
<span class="add">+architecture 組註冊 test-five-station-f2.sh</span></pre>
</details>

<details>
<summary title="過程檔"><code>docs/dev/five-station-f2/6-implementation-notes.md</code> · html twin · 5-tasks frontmatter</summary>
<pre>6-notes + twin；5-tasks status approved（D-3）。RR1+#350／RR2+#351 10/10 T ACCEPTED。本 PR 不改那些檔。</pre>
</details>

## Verdict

**NOT_REVIEWED。不是 G3 PASS。** Writer A 機械審查草稿。`verdict:` 頂欄**留空**。`status: draft`。Human 未簽。本 reviewer **不得**也不會填 PASS／REQUEST_CHANGES。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 F2 S 全綠 | Coverage 70 列 ✅；18 CASE failed=0 | Writer A 實跑；**Human 未簽** |
| 既有回歸綠 | F1 63 CASE；spec-gate 9/9；file-map 210；token 全過 | Writer A 實跑；**Human 未簽** |
| 現象證據逐 F2 S | 上表＋附錄 A4 | Writer A 親跑 selftest；**Human 未簽** |
| Evidence 契約八點 | 本節八點表指向電池＋hollow | 機械面交給本檔；**Human 未簽** |
| 無 🔴 | 無產品行為 🔴；F-s7-1 🟡 = D-1 L1 | **待 owner 接受／park D-1／D-2／D-3** |
| F3 | 明確未做 | 不得當五站已切 |
| Human G3 | **NOT_REVIEWED** | 空欄。全勾 ≠ PASS |

- G3 | 2026-09-14 | Writer A 只交草稿。機械綠在案。D-1／D-2／D-3 **不自動 G3**。owner rick 抽驗後親寫頂欄。STATUS 另 companion。

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 `FORK_INTEGRATION_SHA=56c8019c1058c375755ca03944140f79ff8bbe55`。本工作樹開工 = 已合入的 `origin/main` tip `#351`。

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: 56c8019c1058c375755ca03944140f79ff8bbe55
FEATURE_HEAD: 858336e9441cec636549b3dc2d35ef273e03794f
INTEGRATION_SHA: 858336e9441cec636549b3dc2d35ef273e03794f
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=ALREADY_SYNCED FORK=56c8019c1058c375755ca03944140f79ff8bbe55 HEAD=858336e9441cec636549b3dc2d35ef273e03794f INTEGRATION=858336e9441cec636549b3dc2d35ef273e03794f(refs/remotes/origin/main)—— 你已經同步過了,本次輸出不算數
```

路徑①：**重綁 Final Fresh** 到當下 HEAD = `858336e`（本檔 Source SHA）。共同戰場 = #346…#351 本身，已當審核對象逐檔看過，不得用此次腳本輸出當「沒有共同戰場」。本 hop **不重綁產品碼、不改牙**。產品碼已在 main；本 PR 只文件。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | D-1(L1)：host CI 註冊四檔超出 5-tasks／4-spec S-8.9 准許清單正文。EXPECTED 208→210。R1 CHALLENGE（應 L2）留檔；R2／RR1／RR2／本場 CONCUR L1。不是 F3 cut | L1／🟡 | **待 owner 接受／park**。落點=本表。owner=rick。本 reviewer **不代簽、不自動 G3**。不在本 PR 縮那四檔（縮了 file-map／REPO_REFERENCE 會紅） |
| 2 | D-2(L1)：Stage 4 Diff Budget 估 fixture ≤12；tracked＝49（T-8 16 份 must-keep + 具名 hop／注入）。不動 R/S | L1／🟢 | **待 owner 接受／park**。落點=本表。不減官方 18 CASE |
| 3 | D-3(L1)：`5-tasks.md` frontmatter `approved` 只為 N1-arm。checkbox 未勾。不是完成宣告、不是 G3 | L1／🟢 | **待 owner 接受／park**。落點=本表 |
| 4 | F3 新 slug 預設五站未切（S-8.1）。`graph.yaml` 未改。`f3_cut_happened` 恆 False | 範圍 | 另刀 F3。本場不宣稱完成 |
| 5 | 本檔 `verdict:` 空／NOT_REVIEWED。機械全綠 ≠ Human PASS | 流程 | Human 親寫頂欄。全勾不算 PASS |
| 6 | 步 2c `ALREADY_SYNCED`（F2 已合 main）。交集輸出不作「無共同戰場」證據 | 流程 | 已走路徑① 重綁 Fresh 到 `858336e` |
| 7 | T-5 殘：doctor-route 第 4 格掛 `NEW5-Q12-ZERO` 名。語意是 S-3.6 | 🟢 | 不升 🟡；後站若改名須仍落在官方 18 |
| 8 | 鍵名／倉 JSON 形仍 OPEN（S-5.4）。不得當 schema 已核 | 已知 | 維持；偷鎖鍵＝回 Stage 2 |
| 9 | 5-tasks checkbox 未勾。T ACCEPTED 在 6-notes RR1／RR2，不在勾選 | 誠實 | 不補勾冒充 G3 |
| 10 | 本雲端未武裝 `devflow-exec.sh review` | 流程 | 讀取順序靠散文；見限制聲明 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**:無未授權 Boundary 變更（DIC 六項未命中）。D-1 是 CI 註冊 L1 不是 Boundary。DBC applicable 下無 🟡 Boundary 待處置。D-1／D-2／D-3 **人項**見 Quiz／KL，不在本條偷偷勾成 owner 已接受
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:F2 不 bump 契約、不切 `graph.yaml` 預設。Quiz 留給 Human 若認為本刀仍算不可逆；本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:ALREADY_SYNCED 三 SHA＋canonical ref 貼於 Verdict；Fresh 重綁 `858336e`。Verdict 後禁改產品碼
- [ ] PR → main:本 hop 開 Stage 7 PR（標題 `docs(five-station-f2): Stage7-A review draft`）；**禁直上 master**。**不合入**直到 Human G3。合入由 merger 做
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（F2 不改 living 契約句；F3 才動）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**。Active Stage→7-review 另 companion（G3 仍 ⬜）
- [ ] 7-review frontmatter status: shipped:本 hop `status: draft` + `verdict:` 空。**不得**改 approved／PASS
- [x] 7-review.html 已產生:先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py`（twin 覆寫同檔；抽驗格 S-4.1）
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| Human G3 前 | rick | 本檔 Coverage／KL #1–#3；`test-five-station-f2.sh` 仍 failed=0 且 hollow exit 3 | 電池變紅、hollow 不再是 3、或有人把本 slug 當 NEW5／已切 F3 |
| F3 開工前 | rick | 本檔 KL #4；`f3_cut_happened` 仍 False | 有人把 F3 標成 In 或改 `graph.yaml` |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本 hop **故意**留空 `verdict:`。Writer A 不代填。
2. **D-1 准許清單張力**：4-spec L1004「超出 → L2」vs 實作必須註冊 `test-*.sh`。R1 CHALLENGE 留檔。獨立審（含本場）CONCUR L1。**owner 尚未接受** → 不得自動 G3。
3. **Scope**：只 F2。把 R-8 F3 或「新 slug 預設五站」當成已交付 = 錯。出貨證據＝**dual-path selftest**（18 CASE + hollow exit 3），不是檔在、不是只 F1 綠。
4. **2c ALREADY_SYNCED**：F2 已在 main。不重 merge。Fresh 綁 `858336e`。
5. **作者 vs 本場**：Self-Review 主張電池／hollow／未發明 G3 —— 與本場實跑一致。T 列 ACCEPTED 在 RR1+#350／RR2+#351，不是 implementer-self。Human G3 另由 rick 落檔。

### A2　本場不宣稱的事

F3 cut（S-8.1 後站）。`graph.yaml` 切線。刪 G1／G2／`ACCEPTED`。Living 契約 bump。本 slug 折成五站。Human G3 PASS。STATUS shipped。

### A3　Human 路徑（尚未走）

1. 開 Pages／本機審頁（路徑見 PR）。
2. 抽驗 S-4.1 三個 `檔:行`（入口／OFFICIAL 18／`--only` exit 3）。
3. Known Limits #1–#3（D-1／D-2／D-3）：owner 明示接受／park 或打回。
4. 判定由人親寫：`verdict: PASS` 或 `REQUEST_CHANGES` 或 `HOLD`。Agent 禁代填。
5. 頂欄走官方 write 路徑時須 attestation `human:<名> @ <YYYY-MM-DD>`。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
858336e9441cec636549b3dc2d35ef273e03794f

$ bash scripts/test-five-station-f2.sh -v
=== CASE NEW5-Q12-ZERO … OLD7-SELF
failed=0
exit 0
=== CASE count
18

$ bash scripts/test-five-station-f2.sh --only new5; echo $?
hollow --only new5
3
$ bash scripts/test-five-station-f2.sh --only old7; echo $?
3
$ bash scripts/test-five-station-f2.sh --only f1; echo $?
3

$ bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md
✅ C1…C9
✅ G2 spec gate:9/9 全過
exit 0

$ bash scripts/check-file-map.sh
scanned=210 exempted=13
✅ PASS
exit 0

$ bash scripts/check-gate-tokens.sh
✅ Gate Token 釘死守衛:全過
exit 0

$ bash scripts/test-five-station-f1.sh
failed=0
exit 0
```

### A5　Evidence 八點 + Gauntlet

G3 錨八點（正本 `guides/guide-dev-flow.html#gates`）本場對照：

1. Final Fresh 綁 Source SHA＝送審 HEAD：`858336e9441cec636549b3dc2d35ef273e03794f`＝開工 `git rev-parse HEAD`。本 PR 只文件，不改產品碼。docs commit 會再漂 SHA，不重綁、不發明 Final Fresh。
2. Required Layer = pass：spec-gate 9/9；token 全過。電池已落地 → 本場把 `test-five-station-f2` 當加嚴 Required 且 pass。
3. 已觸發 Conditional = pass：F2 電池＋hollow 三探針；F1 十二群回歸。
4. 不得存在任何 fail：Verification Evidence 層表無 fail。
5. Required 不得 unverified／n-a：電池／spec-gate／token 皆 pass。
6. Explicitly Excluded 可 n-a＋理由：UI e2e／負荷／金流／Windows 已附理由。
7. Optional 可 unverified＋誠實：無另開 Optional 層假裝 pass。
8. Gauntlet PASS 不取代雙軸／Walkthrough／矩陣／現象：見本檔三大節。Human 未簽。

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f2/7-review.md \
    --source-sha 858336e9441cec636549b3dc2d35ef273e03794f \
    --review-file --require-layer test-five-station-f2
✅ evidence gauntlet: 92 checks passed — docs/dev/five-station-f2/7-review.md
exit 0
```

Writer A @ `858336e`（工作樹未 commit 本雙檔時跑）。Gauntlet 綠仍**不取代** Human G3。`--review-file` 對本路徑強制 HEAD；本 docs commit 之後 SHA 會漂，不重綁產品碼 Fresh。

`7-review.html`：先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py /workspace five-station-f2 7-review`（twin 覆寫同檔；抽驗格 S-4.1）。Pages 掛 twin。

### A6　作者對照（N4；矩陣之後才讀）

- Self-Review ①–⑧：與獨立實跑一致。未發明 G3。未勾 5-tasks。
- D-1／D-2／D-3 記帳如實。本場不改級、不重開 G2。
- Decisions（JSON 倉、鍵名 OPEN、D-1 四檔保留）不構成 L2。
- 不另存 `7-review-*.md`。
