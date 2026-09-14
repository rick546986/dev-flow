---
feature: five-station-f2
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: s7-fresh-reviewer-B
reviewers: []
updated: 2026-09-14
---

# 7. 驗證 —— **不是 G3 PASS**（Stage7-B + owner standing soft-fix／F2 knife only）

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
> | 5 | **抽驗一列** | Human 抽驗加 **S-4.1**：`scripts/test-five-station-f2.sh:1-15`（單一入口）、`scripts/five_station_f2.py:35-41`（OFFICIAL 18）、同檔 `:1133-1149`（`--only new5&#124;old7&#124;f1` → exit 3）。twin 第五格＝Coverage 中位列 **S-4.11**（決定論 `rows[n//2]`）。殘項 **S-4.3**：`:466-467`（`- lane:`／`- Risk:` 缺 → `Sp2`）、`:464-465`（`OBS_FIELD` 缺 → `Sp2`）、`:877-882`（`why == "Sp2"` 且未 hop Build）、`scripts/fixtures/five-station-f2/new5/pred-stop/docs/dev/stop/4-spec.md:12`（故意無 `- 觀測:`）。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡草稿**。本檔是 Writer B 獨立審查稿＋**owner standing soft-fix**（#354 全票勝出後吸收 A／C，不換 winner）。`verdict: PRE-REVIEW`。`status: draft`。
> **不是 Human G3 PASS。全勾不算 PASS。Agent 禁代填 PASS。**
> 建議 reviewer 路徑：適格人類 owner `rick` 親審本檔 → 用官方 write 路徑落頂欄。
> Scope = **F2 knife only**（coordinator＋slug 倉＋雙路電池＋RP 讀倉）。不宣稱 F3。不改 STATUS。不發明 G3。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | Writer B／`s7-fresh-reviewer-B`（fresh-context Cloud Agent `bc-ef74b1d2-4254-4640-89e2-44b32de04cc9`；**≠** Stage 6 實作 owner `implementer-A`／#346／#349） |
| Stage 6 實作 | `implementer-A`；獨立 T-Review RR1（#350）／RR2（#351）各 10／10 ACCEPTED。**不是** G3 |
| Human G3 | **未寫**。頂欄 `verdict: PRE-REVIEW`。無 attestation。不得當成 PASS |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、70 S、DD-1…DD-10 Owner PASS） ②`5-tasks.md`（T-1…T-10） ③`scripts/test-five-station-f2.sh` + `five_station_f2.py` + fixtures ④`git diff 56c8019..858336e` ⑤親跑電池／hollow／spec-gate／F1／tokens／file-map／doctor → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-1／D-2／D-3／RR1／RR2 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 session runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 `main` tip `#351`=`858336e`。本 PR **只** 7-review 雙檔。不改 STATUS／HISTORY。**不發明 G3 PASS** |
| 可信／打折 | 機械數字（18 CASE／failed=0／hollow exit 3／spec-gate 9/9／F1 63）以本場親跑為準。F-id 分級與 D-1 park **打折**（等人裁決）。「沒想到的事」不保證 |

建議的補救路徑：人類 owner 抽驗 **S-4.1** 三個 `檔:行`（殘項 S-4.3 仍在）→ 裁決 D-1／F-c-4 L1 park 或回 G2 → 用 `scripts/devflow_gate.py write` 落 Human verdict。**本 Agent 不代填。**

## Coverage Matrix

自建（grep `S-`／`=== CASE` ↔ 4-spec 70 S；**未先讀** Self-Review）。末列固定回歸。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `NEW5-Q12-ZERO`；`five_station_f2.py:622` first persist=0 | ✅ |
| S-1.2 | 同 CASE；`:626` second persist=1 | ✅ |
| S-1.3 | 同 CASE；`:629` two rewrites after first | ✅ |
| S-1.4 | `NEW5-RUN2`；`:647` new process still 2/0/0 | ✅ |
| S-1.5 | `NEW5-CAP-3`；`:667-675` 第 3 次拒／Escalated／RP-9 讀倉 | ✅ |
| S-1.6 | `NEW5-DECIDE-2`；`:700-704` | ✅ |
| S-1.7 | `NEW5-GOAL-2`；`:720-724` | ✅ |
| S-1.8 | `NEW5-CAP-3`；`:669-671` still 2／no reset | ✅ |
| S-1.9 | `NEW5-GOAL-2`；`:715` Goal+Decide same mutation | ✅ |
| S-1.10 | 同 CASE；`:728-729` T retry ≠ hop | ✅ |
| S-1.11 | Q12／RUN2；`:631`／`:649` 倉不在 `runs/` | ✅ |
| S-1.12 | `NEW5-STORE-READ`；`:684` 字樣牙不讀倉＝紅格 | ✅ |
| S-2.1 | `NEW5-SPEC-SHARE`；`:742` only five hop_id | ✅ |
| S-2.2 | 同 CASE；`:741` Spec 同桶 | ✅ |
| S-2.3 | `NEW5-BUILD-SHARE`；`:771` Build 同桶 | ✅ |
| S-2.4 | `NEW5-SEVEN-STEM`；`:784` 注入七 stem＝紅格 | ✅ |
| S-2.5 | SPEC-SHARE；`:753-761` 無 proto 檔／拒 `Stage3`（無 `or True`） | ✅ |
| S-2.6 | SPEC-SHARE；`:744` 舊 graph 節點不是 hop_id | ✅ |
| S-2.7 | `git diff 56c8019..858336e` 零 `graph.yaml` | ✅ |
| S-3.1 | `--group doctor-route`；`:793-797` 理由是路線、不含「doctor 已綠」 | ✅ |
| S-3.2 | 同 group；`:803-804` marketplace＋F3 cut 未發生 | ✅ |
| S-3.3 | 同 group；`:809` 契約仍 2.0.x | ✅ |
| S-3.4 | `test-five-station-f1.sh --group dual-read`；S-5.6 文案仍紅 | ✅ |
| S-3.5 | diff `hooks/_doctor_impl.py`＝0 | ✅ |
| S-3.6 | doctor-route；`:813` cache 不是第四前置 | ✅ |
| S-4.1 | 全入口 exit 0；`--only new5&#124;old7&#124;f1` 各 exit 3 | ✅ |
| S-4.2 | `NEW5-HOP-OK` I／D／Sp／Bu 各 hop | ✅ |
| S-4.3 | `NEW5-PRED-STOP`；`:877` `why==Sp2`（本場抽驗列） | ✅ |
| S-4.4 | `NEW5-MK-RED`；`:936` 注入仍 hop＝紅格 | ✅ |
| S-4.5 | `NEW5-SHIP-MECH`；`:944` 注入機械 Done＝紅格 | ✅ |
| S-4.6 | `NEW5-WAIT-RED`；`:951` 注入等人句＝紅格 | ✅ |
| S-4.7 | `OLD7-FOLD-RED`；`:960` 對 OLD7 寫五站＝紅格 | ✅ |
| S-4.8 | 上四格 polarity＝注入壞行為紅，不是拒 hop 當綠 | ✅ |
| S-4.9 | hollow 三探針 exit 3 | ✅ |
| S-4.10 | 預設 `-v` 18 名＝官方 18；無減列、無發明名 | ✅ |
| S-4.11 | 同 S-1.12 | ✅ |
| S-4.12 | 同 S-1.1／S-1.3 | ✅ |
| S-4.13 | 同 S-2.2 | ✅ |
| S-4.14 | 同 S-2.3 | ✅ |
| S-4.15 | `--hop I`；`:835-840` | ✅ |
| S-4.16 | `--hop D`；`:847-849` | ✅ |
| S-4.17 | `--hop Sp`；`:856-860` | ✅ |
| S-4.18 | `--hop Sp5b`；`:894` HumanWait | ✅ |
| S-4.19 | `--hop Bu`；`:867` | ✅ |
| S-5.1 | `--group events` 3 CASE；五問可答 | ✅ |
| S-5.2 | 同 group；`:927` 正本是 slug ledger | ✅ |
| S-5.3 | diff `agent-event.schema.json`＝0 | ✅ |
| S-5.4 | 5-tasks／6-notes 無已核 JSON 鍵；碼註 OPEN | ✅ |
| S-6.1 | `--group must-keep` M11 overlay 拒 hop | ✅ |
| S-6.2 | HOP-OK；`:840` 無「要不要繼續」 | ✅ |
| S-6.3 | SHIP-MECH 注入 Done＝紅；合法是 HumanWait | ✅ |
| S-6.4 | MK／SHIP／WAIT 三格獨立紅 | ✅ |
| S-6.5 | must-keep 16 份各 `ok=False` 且理由含該 M | ✅ |
| S-6.6 | 4-spec Disposition 16 列仍在、無「可選」（G2 gate） | ✅ |
| S-7.1 | OLD7-NO-FIVE；`:997` in-flight → legacy | ✅ |
| S-7.2 | doctor-route cache ≠ 路條 | ✅ |
| S-7.3 | 同 S-3.6／S-7.2 | ✅ |
| S-7.4 | OLD7-NO-FIVE；`:993-996` 無五站機 | ✅ |
| S-7.5 | OLD7-TOKEN；`:1005-1010` token＋F1 綠 | ✅ |
| S-7.6 | OLD7-SELF；`:1015` 本目錄跳不過 | ✅ |
| S-7.7 | 同 CASE；`:1020` NEW5＝合成 fixture | ✅ |
| S-8.1 | `f3_cut_happened` 恆假；guide 無切五站預設 | ✅ |
| S-8.2 | OLD7-NO-FIVE＋無 live `.five-station/` | ✅ |
| S-8.3 | `check-gate-tokens.sh` exit 0 | ✅ |
| S-8.4 | Stage 4 hop 已 G2；本場不重開 4-spec 頂欄 | ✅ |
| S-8.5 | `--only`／完成條件要求 S-4.1，檔在不算完 | ✅ |
| S-8.6 | `--only f1` exit 3；F1 63 CASE 是回歸不是完工 | ✅ |
| S-8.7 | 4-spec Disposition Q9–Q24 有去向；Q21–Q23 非可選 | ✅ |
| S-8.8 | `--only new5` exit 3 | ✅ |
| S-8.9 | 准許清單內 scripts／fixtures；graph／token／doctor／契約＝0。**D-1 四檔是明文 L1** | ✅ |
| 既有測試套件(回歸) | `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`；`bash scripts/test-five-station-f1.sh`；`bash scripts/check-file-map.sh`；`bash scripts/check-gate-tokens.sh` | ✅ |

**回歸末行（reviewer @ `858336e`）**：spec-gate `9/9` exit 0（70 S）；F1 `failed=0` CASE=63；file-map `scanned=210` exit 0；tokens 全過；doctor `COMPATIBLE`（約束，不是 hop 通行證）。

## Verification Evidence

<!-- Final Fresh 在 ALREADY_SYNCED 之後重綁當下 main tip（步 2c 路徑①）。
     產品碼樹 = origin/main after #346…#351。本 PR 後續只加本雙檔，不改牙。 -->

- Source SHA: 858336e9441cec636549b3dc2d35ef273e03794f
- Final Fresh Run ID: f2-s7b-fresh-858336e-20260914
- Entry point: `bash scripts/test-five-station-f2.sh`（Conditional 已落地 → 本場列入 Required）然後 `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md`） | `bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md` | pass | exit 0; 9/9; 70 S | |
| token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F2 電池列 Required | `bash scripts/check-gate-tokens.sh` | pass | exit 0; G1 2 token; G2 3 token; G3 4 token | |
| test-five-station-f2 | `bash scripts/test-five-station-f2.sh` | pass | failed=0; CASE=18; exit 0 | |
| hollow --only new5 | `bash scripts/test-five-station-f2.sh --only new5` | pass | exit 3; 印 hollow --only new5 | |
| hollow --only old7 | `bash scripts/test-five-station-f2.sh --only old7` | pass | exit 3; 印 hollow --only old7 | |
| hollow --only f1 | `bash scripts/test-five-station-f2.sh --only f1` | pass | exit 3; F1-only is not F2 complete | |
| unknown --only | `bash scripts/test-five-station-f2.sh --only bogus` | pass | exit 2（用法；不得當 hollow 綠） | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | failed=0; CASE=63; exit 0 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=210; table_rows=220 | |
| doctor handshake | `bash hooks/devflow-doctor.sh` | pass | COMPATIBLE; contract 2.0.0; gauntlet 1.3.3 | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| UI e2e（本刀無新前端） | | n-a | | Explicitly excluded；F2 無產品 UI |
| 負荷／效能（coordinator 非熱路徑） | | n-a | | Explicitly excluded |
| 金流／auth fuzz（不涉） | | n-a | | Explicitly excluded |
| 本 hop 跑 coordinator（碼 Out of Scope） | | n-a | | 層名是 Stage 4 hop 排除句；本場 Stage 7 已跑電池入口，不把此列標 pass 冒充「未落地」 |

八點機械面（G3 錨全文）見附錄 A5。指向 **單一電池 + hollow 三探針**，不是「檔在」或「只 F1 綠」。**八點齊 ≠ Human G3 PASS**。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得 run 級 cap／X5（S-1.4、S-1.11） | NEW5-RUN2；倉路徑無 `.devflow/runs/` | pass |
| RP 不得只咬「第 3 次」字樣（S-1.12、S-4.11） | NEW5-STORE-READ 紅格 | pass |
| 不得七 stem 分桶（S-2.4） | NEW5-SEVEN-STEM 紅格 | pass |
| 不得 doctor 綠當 hop 通行證（S-3.1） | doctor-route；理由是路線 | pass |
| 紅格不得把拒 hop 當綠（S-4.8） | MK／SHIP／WAIT／FOLD 注入紅 | pass |
| 不得只跑 NEW5 或只跑 F1（S-4.1、S-4.9） | `--only` exit 3 | pass |
| 不得對本目錄建五站機（S-7.6） | OLD7-SELF | pass |
| 不得本 hop 自填 G2／G3 PASS（S-8.4） | 4-spec 已 Human G2；本檔 PRE-REVIEW | pass |
| 不得 F3 cut／折 in-flight／刪 token（S-8.1…S-8.3） | graph／token／doctor diff＝0 | pass |
| 不得鎖 JSON 鍵或 bump agent-event（S-5.3、S-5.4） | schema diff＝0；鍵名 OPEN | pass |
| 不得只擋 M11（S-6.5） | must-keep 16 份 | pass |
| Out of Scope 後站不准改成 In | 5-tasks／6-notes 三把鎖仍 Out | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#346／#349 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **s7-fresh-reviewer-B 2026-09-14 親跑** `bash scripts/test-five-station-f2.sh -v`（不採信 6-notes 貼文）。長輸出見附錄 A4。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 讀 slug 倉該 hop 桶 | `[ok] S-1.1 first persist=0`；retry idempotent 仍 0 | ✅ |
| S-1.2 | 連續讀 Spec 桶 | `[ok] S-1.2 second persist=1` | ✅ |
| S-1.3 | hop 拒絕輸出＋倉數字 | `[ok] S-1.3 two rewrites after first` | ✅ |
| S-1.4 | 新 process 再讀 | `[ok] S-1.4 new process still 2/0/0` | ✅ |
| S-1.5 | 倉＝2 且稿無「第 3 次」仍拒 | `[ok] S-1.5 third rewrite refused`／Escalated／RP-9 reads store | ✅ |
| S-1.6 | Decide 重開讀倉 | `[ok] S-1.6 second Decide reopen refused` | ✅ |
| S-1.7 | Goal 重開讀倉 | `[ok] S-1.7 second Goal refused` | ✅ |
| S-1.8 | 拒後仍是 2 | `[ok] S-1.8 still 2`／no reset | ✅ |
| S-1.9 | 兩計數同 mutation | `[ok] S-1.9 Goal+Decide same mutation` | ✅ |
| S-1.10 | T retry 不進 hop 桶 | `[ok] S-1.10 T retry ≠ hop` | ✅ |
| S-1.11 | 倉不在 run 級 | `[ok] S-1.11 store not run-level` | ✅ |
| S-1.12 | 字樣牙不讀倉＝該格紅 | `[ok] S-1.12/S-4.11 string-only miss is the red cell` | ✅ |
| S-2.1 | hop_id 只有五字 | `[ok] S-2.1 only five hop_id` | ✅ |
| S-2.2 | proto＋spec 同 Spec 桶 | `[ok] S-2.2/S-4.13 same Spec bucket` | ✅ |
| S-2.3 | tasks＋notes 同 Build 桶 | `[ok] S-2.3/S-4.14 same Build bucket` | ✅ |
| S-2.4 | 注入七 stem 紅 | `[ok] S-2.4 seven-stem injection is the red cell` | ✅ |
| S-2.5 | 無 proto 檔／拒 Stage3 | `[ok] S-2.5` 四句；`rg or True`＝無 | ✅ |
| S-2.6 | 舊節點不是 hop_id | `[ok] S-2.6 old graph nodes are not hop_id` | ✅ |
| S-2.7 | graph.yaml 行數 0 | `git diff --name-only` 無 graph.yaml | ✅ |
| S-3.1 | 拒 hop 理由是路線 | `[ok] S-3.1 reason is route`／not doctor-green ticket | ✅ |
| S-3.2 | marketplace ≠ cut | `[ok] S-3.2 F3 cut has not happened` | ✅ |
| S-3.3 | 契約仍 2.0.x | `[ok] S-3.3 contract still 2.0.x` | ✅ |
| S-3.4 | F1「跟 hops」文案仍紅 | dual-read `RED S-5.6 doctor 綠不得跟 hops` | ✅ |
| S-3.5 | 不改 doctor | `_doctor_impl.py` diff 空 | ✅ |
| S-3.6 | cache 不是第四前置 | `[ok] S-3.6 cache is not a fourth precondition` | ✅ |
| S-4.1 | 入口 stdout／exit | 全入口 exit 0；`--only` 3／3／3；未知旗標 2 | ✅ |
| S-4.2 | hop 紀錄＋CASE 綠 | I／D／Sp／Bu 各 `[ok]` hop | ✅ |
| S-4.3 | 謂詞假停修 | `[ok] S-4.3 predicate false → no hop (got Sp2)` | ✅ |
| S-4.4 | 注入 MK 仍 hop＝紅 | `[ok] S-4.4 inject MK-red still hop is the red cell` | ✅ |
| S-4.5 | 注入機械 Done＝紅 | `[ok] S-4.5 inject mechanical Done is the red cell` | ✅ |
| S-4.6 | 注入等人句＝紅 | `[ok] S-4.6 inject 要不要繼續 is the red cell` | ✅ |
| S-4.7 | 對 OLD7 寫五站＝紅 | `[ok] S-4.7 inject five-station write on OLD7` | ✅ |
| S-4.8 | 紅格只接受注入壞行為 | 四格皆「is the red cell」，不是拒 hop 綠 | ✅ |
| S-4.9 | 三假綠皆非 0 | hollow exit 3 | ✅ |
| S-4.10 | 13 原列＋5 加列皆在 | 18 官方名全印出 | ✅ |
| S-4.11 | 同 S-1.12 | 同左 | ✅ |
| S-4.12 | 同 S-1.1 | 同左 | ✅ |
| S-4.13 | 同 S-2.2 | 同左 | ✅ |
| S-4.14 | 同 S-2.3 | 同左 | ✅ |
| S-4.15 | from-to＝Intake→Decide | `[ok] S-4.15 Intake→Decide hop I1–I4` | ✅ |
| S-4.16 | Decide→Spec 不等 G1 | `[ok] S-4.16 no wait for G1` | ✅ |
| S-4.17 | Spec→Build 無 proto | `[ok] S-4.17 no 3-prototype created` | ✅ |
| S-4.18 | Sp5b HumanWait | `[ok] S-4.18 Sp5b no attestation → HumanWait` | ✅ |
| S-4.19 | Build→Ship Bu1–Bu4 | `[ok] S-4.19 Build→Ship Bu1–Bu4` | ✅ |
| S-5.1 | 三類紀錄五問 | events 3 CASE；hop／latch／cap | ✅ |
| S-5.2 | 正本不是 chat／STATUS | `[ok] S-5.2 original is slug ledger` | ✅ |
| S-5.3 | schema 不 bump | agent-event diff 空 | ✅ |
| S-5.4 | 無已核鍵名 | 5-tasks 禁鎖鍵；碼註 OPEN | ✅ |
| S-6.1 | 缺 Verify 拒 hop | must-keep `11-m11.md` why=M11 | ✅ |
| S-6.2 | 謂詞真立刻 hop | `[ok] S-6.2 no please-review` | ✅ |
| S-6.3 | Ship 無自動 Done | SHIP-MECH 注入紅 | ✅ |
| S-6.4 | 三失敗獨立紅 | MK／SHIP／WAIT 各一格 | ✅ |
| S-6.5 | 16 份各少一 M 拒 hop | must-keep n=16；M1…M16 各 why=該 M | ✅ |
| S-6.6 | Disposition 16 列 | 4-spec 表在；無「可選」 | ✅ |
| S-7.1 | 缺前置 allow_legacy | `[ok] S-7.1 in-flight → legacy` | ✅ |
| S-7.2 | cache 只選碼 | doctor-route marketplace+cache ≠ ticket | ✅ |
| S-7.3 | 不掃最新 cache | 同 S-3.6 | ✅ |
| S-7.4 | OLD7 無五站寫入 | `[ok] S-7.4 no five-station machine` | ✅ |
| S-7.5 | token＋F1 仍綠 | `[ok] S-7.5 tokens still present`／F1 green | ✅ |
| S-7.6 | 本目錄跳不過 | `[ok] S-7.6 this slug cannot auto-advance` | ✅ |
| S-7.7 | NEW5 是合成根 | `[ok] S-7.7 NEW5 is synthetic fixture` | ✅ |
| S-8.1 | 無 F3 cut 聲明 | guide 只加檔案地圖列；`f3_cut_happened=False` | ✅ |
| S-8.2 | in-flight 仍舊 7 | live 無 `.five-station/`；OLD7-NO-FIVE | ✅ |
| S-8.3 | token 仍在 | check-gate-tokens exit 0 | ✅ |
| S-8.4 | 不重開 Stage 4 hop | 4-spec 頂欄仍 Human G2；本 PR 不改它 | ✅ |
| S-8.5 | 檔在 ≠ 完 | 完成條件是 S-4.1 入口 | ✅ |
| S-8.6 | F1 綠 ≠ 完 | `--only f1` exit 3 | ✅ |
| S-8.7 | Q9–Q24 有去向 | 4-spec Disposition；Q21–Q23 下落是 S | ✅ |
| S-8.8 | 只 NEW5 ≠ 完 | `--only new5` exit 3 | ✅ |
| S-8.9 | Files 准許＋Diff Budget 0 | 刀口 scripts／fixtures；D-1 四檔明文 L1 | ✅ |

## 截圖槽

本場無產品 UI（F2 = CLI coordinator + fixture 自檢）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = 電池 CASE stdout
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F2 是 coordinator／電池，不是現場交接 UI。有 Operational Context 的 S 以「寫手／coordinator 被閘擋住或立刻 hop」走一遍；標不適用的純內部 S 不裝成人員旅程。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1…S-1.12 | — | — | persist／讀倉 | — | Escalated 停 hop | 不適用（計數寫入） |
| S-2.1…S-2.7 | — | — | 五桶觸發 | — | 七 stem 紅 | 不適用（桶契約） |
| S-3.1 | 採用端 | doctor 綠後想 hop | `refuse_hop_reason` | 不把 COMPATIBLE 當切線 | 仍舊 7 | 理由是路線 |
| S-3.2…S-3.6 | — | — | 路線閘 | — | cache／marketplace 不當票 | 不適用（約束核對） |
| S-4.1／S-4.8…S-4.12／S-4.9 | — | — | 電池入口 | — | hollow exit 3 | 不適用（完成定義） |
| S-4.2／S-4.15 | coordinator／寫手 | Intake 完立刻進 Decide | `--hop I` | 不寫「要不要繼續」 | latch 假 | hop Intake→Decide |
| S-4.3 | 寫手 | 缺觀測欄停 Spec | PRED-STOP | 補 `- 觀測:` | 停修、不問人 | why=Sp2 |
| S-4.4…S-4.7 | 電池作者 | 餵壞行為該格紅 | inject= | 不把拒 hop 記綠 | 各格獨立紅 | 極性對 |
| S-4.16 | — | — | Decide→Spec | — | 不等 G1 | hop |
| S-4.17 | coordinator | 無 trigger 不建 Demo | `--hop Sp` | 不補 3-prototype | 不等 G2 | 無 proto 檔 |
| S-4.18 | Demo 參與者 | 無 attestation 不得離 Spec | `--hop Sp5b` | 人簽 attestation | HumanWait | 未 hop Build |
| S-4.19 | T reviewer | Bu1–Bu4 才進 Ship | `--hop Bu` | 獨立 review | Must-keep 紅則停 | hop Build→Ship |
| S-5.1…S-5.4 | — | — | slug ledger | — | 不 bump schema | 不適用（紀錄契約） |
| S-6.1 | 寫手／T reviewer | 缺 Verify 不准 hop | must-keep M11 | 補四欄 | 停 Build | why=M11 |
| S-6.2 | coordinator | 謂詞真立刻 hop | HOP-OK | 刪等人句 | 無第二次人停 | 無 please-review |
| S-6.3 | owner | Ship 唯人 | SHIP-MECH 注入 | 人寫 PASS | HumanWait | 自動 Done＝紅 |
| S-6.4…S-6.6 | — | — | 三失敗／16 M | — | 不得互抵 | 不適用（測法／去向帳） |
| S-7.1…S-7.7 | 本 slug owner | 本目錄／OLD7 仍舊 7 | allow_legacy | 不拿本目錄當 NEW5 | 跳不過 | OLD7-SELF |
| S-8.1…S-8.8 | — | — | 刀／hollow | — | 後站不准改成 In | 不適用（完成定義） |
| S-8.9 | Stage 5／6 寫手 | 只施工 F2 scripts | Files 聯集 | F3 另開 slug | D-1 四檔等人 park | 刀口守住；L1 明文 |

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec ⑦⑧⑨⑪）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中。F2 讀 doctor／契約當證據，Files 不含 `hooks/_doctor_impl.py`；#346…#351 未改握手語意。
2. **資料所有權被繞過寫入**:未命中。倉 owner＝該 slug coordinator；OLD7／本目錄不建五站機（S-7.4／S-7.6）。
3. **相容性破壞包成新增**:未命中。契約仍 2.0.0；`agent-event` 未 bump。
4. **一致性邊界被拆解**:未命中。`goal_reopen` 兩計數同一 `save_store`（S-1.9）。
5. **宣告的 Test seam 未被使用**:未命中。seam＝`persist`／`evaluate_hop`／`--case`／`--only`；電池走同一入口。
6. **Known design limit 被實作悄悄「解決」**:未命中。doctor 綠陷阱仍在現場（約束）；`f3_cut_happened` 仍假。D-1 是 CI 註冊，不是把 F3 限制「修掉」。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更。

- F-s7b-1 🟡 D-1 四檔在 5-tasks S-8.9 准許清單正文之外（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`／`guides/guide-dev-flow.html` 檔案地圖列） | 4-spec L1004 寫「超出 → L2」；R1 CHALLENGE 留檔 | 本場獨立再評：**仍 L1**（CI 註冊，不是 F3 cut／不是切預設路線）。**Human 尚未 park**。見 Known Limits #1。不得當 G3 已接受
- F-s7b-2 🟢 `five_station_f2.py:1133-1149` `--only` | 該路即使綠也 exit 3 | 對準 S-4.1 b／c／d；未知旗標 exit 2
- F-s7b-3 🟢 `--group doctor-route` 第 4 格 CASE 名掛 `NEW5-Q12-ZERO` | 測的是 S-3.6 cache，名詞借官方 18 名 | 殘項；不發明 `NEW5-MKTG-*`。不升 🟡
- F-s7b-4 🟢 `--group must-keep` 16 格皆印 `NEW5-HOP-OK` | 合法拒走 Bu4，不發明 `NEW5-MK-ANY` | standing 禁發明名。測法是 overlay＋`evaluate_hop`
- F-c-4 🟡 `scripts/five_station_f2.py` `wc -l` = 1158 > Diff Budget coordinator ≤600 | 行數超估 | 吸 C。單一家族、不拆第二檔（會撞 Files 格）。**L1 park**。不動 R/S。見 KL #8
- F-s7b-6 🟡 D-2(L1) fixture 超 Stage 4「≤12」估計 | 估計超支 | **tracked＝49**（方法：`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f2`；45 md＋3 keep＋1 gitignore）。B 稿 62／C 稿 63＝run-generated／工作樹另計，不與 tracked 混寫。不動 R/S。見 KL #2
- F-s7b-7 🟡 D-3(L1) `5-tasks.md` `status: approved` 而 checkbox 全未勾 | 看起來像任務已核 | N1-arm／graph P0 only，不是勾 T、不是 G3。見 KL #3
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。D-1 是 host CI 地板，不是新公開 API

## Spec Axis

逐 R。Deviations：D-1／D-2／D-3 如實，無隱藏 L2。F3 明確未做。

| R | 判定 | 證據 |
|---|---|---|
| R-1 | **符合** | S-1.1…S-1.12 電池綠；persist 第一次＝0；RP-9／10／11 讀倉；STORE-READ 紅格 |
| R-2 | **符合** | S-2.1…S-2.7；Spec／Build 同桶；七 stem 紅；graph.yaml＝0 |
| R-3 | **符合** | S-3.1…S-3.6；doctor 綠≠路條；未改 `_doctor_impl.py` |
| R-4 | **符合** | S-4.1…S-4.19；18 CASE；hollow exit 3；注入四格紅；PRED-STOP `Sp2` |
| R-5 | **符合** | S-5.1…S-5.4；events 三官方名；schema 未 bump；鍵名 OPEN |
| R-6 | **符合** | S-6.1…S-6.6；must-keep 16 份真拒；SHIP 無自動 Done |
| R-7 | **符合** | S-7.1…S-7.7；OLD7 無五站機；本目錄跳不過 |
| R-8 | **符合（刀）＋D-1 待人 park** | S-8.1…S-8.9 電池／diff 側成立。D-1 四檔是明文 L1，不是 silent extras。**不因此代填 G3** |
| D-1(L1) | 如實；**Human 未接受** | 四檔具名。本場 CONCUR L1。R1 CHALLENGE 留檔 |
| D-2(L1) | 如實 | fixture 估 ≤12 vs **tracked 49**（`git ls-tree -r --name-only`）。B/C 曾寫 62／63＝run-generated 另計。不動 R/S |
| D-3(L1) | 如實 | `5-tasks.md` `status: approved`＝N1-arm；checkbox 未勾 |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit |

## 變更架構圖

必須對上 #346…#351 basename（本 PR 只加 `7-review.md`／`7-review.html`）。

```text
[test-five-station-f2.sh] ----exec----> [five_station_f2.py]
                                         +-- persist / store_path
                                         |     docs/dev/<slug>/.five-station/store
                                         +-- evaluate_hop / pred_false / missing_must_keep
                                         +-- allow_legacy / refuse_hop_reason
                                         +-- Battery 18 CASE
[five_station_f1.py]  --caps_near--      RP-9／10／11 讀倉（字樣牙留回歸）
fixtures/five-station-f2/new5|old7
D-1 floor (not 5-tasks Files union):
  check-file-map.sh        EXPECTED=210
  devflow-check.sh         architecture/test-five-station-f2
  test-architecture-guards.sh  靜態釘 210
  guide-dev-flow.html      檔案地圖兩列（非 F3 cut）
NOT in this knife:
  graph.yaml / _templates / doctor handshake / contract bump / F3 預設切線
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

審核的產品碼 = `56c8019..858336e`（#346 實作＋#349 rework＋#350／#351 RR）。本 Stage 7 PR 只新增本雙檔。共同戰場已是送審樹本身（見 2c）。

<details>
<summary title="+1158/-0; persist + hop + battery"><code>scripts/five_station_f2.py</code> (+1158/-0)</summary>
<pre><span class="add">+HOPS = Intake Decide Spec Build Ship</span>
<span class="add">+OFFICIAL = 18 CASE 名</span>
<span class="add">+def persist(...)  # first=0 then +1; cap→Escalated</span>
<span class="add">+def goal_reopen(...)  # 兩計數同 mutation</span>
<span class="add">+def evaluate_hop(...)  # pred / must-keep / inject</span>
<span class="add">+class Battery  # 18 CASE + hollow --only exit 3</span></pre>
</details>

<details>
<summary title="+15/-0; 入口"><code>scripts/test-five-station-f2.sh</code> (+15/-0)</summary>
<pre><span class="add">+exec python3 five_station_f2.py --root "$ROOT" "$@"</span></pre>
</details>

<details>
<summary title="+14/-1; RP 讀倉"><code>scripts/five_station_f1.py</code> (+14/-1)</summary>
<pre><span class="add">+def evaluate(..., caps_from_store=True)</span>
<span class="add">+    caps = five_station_f2.caps_near(path)</span>
<span class="add">+    hop_max&gt;=2 → RP-9; decide_reopen≥1 → RP-10; goal_reopen≥1 → RP-11</span>
<span class="add">+字樣牙仍在（回歸）</span></pre>
</details>

<details>
<summary title="fixtures 目錄"><code>scripts/fixtures/five-station-f2/*</code>（tracked 49 via git ls-tree；D-2）</summary>
<pre>方法：git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f2 → 49（45 md + 3 keep + 1 gitignore）
B 稿曾寫 62、C 稿曾寫 63＝run-generated／工作樹另計，不與 tracked 混寫。
new5/: q12、rp-09/10/11、store-read、spec/build-share、seven-stem、inject-*、must-keep/01-16、hop-ok、pred-stop、hop-sp5b、doctor-compatible
old7/: 1–7 .md + inject-fold-red
完整 diff 在 #346／#349。</pre>
</details>

<details>
<summary title="D-1 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code> · <code>guides/guide-dev-flow.html</code></summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 208</span>
<span class="add">+EXPECTED_MAPPED_FILES = 210</span>
<span class="add">+architecture 組註冊 test-five-station-f2.sh</span>
<span class="add">+guide 檔案地圖兩列（非 F3 cut 聲明）</span></pre>
</details>

<details>
<summary title="過程檔"><code>docs/dev/five-station-f2/6-implementation-notes.md</code> · html twin · 5-tasks</summary>
<pre>6-notes + RR1／RR2 10／10 ACCEPTED。5-tasks D-3 frontmatter approved。STATUS／HISTORY 是 companion，不在本 PR。</pre>
</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** 本場是 Writer B 獨立審查稿。機械門檻有親跑證據；Human 未簽。Agent 禁代填 `verdict: PASS`。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 70 S 全綠 | Coverage 70 列 ✅；18 CASE failed=0 | reviewer 實跑；**Human 未簽** |
| 既有回歸綠 | spec-gate 9/9；F1 CASE=63；file-map 210；tokens | reviewer 實跑；**Human 未簽** |
| 現象證據逐 S | 上表＋附錄 A4 | reviewer 親跑電池；**Human 未簽** |
| Evidence 契約 | 本節四欄＋層表；gauntlet 見附錄 A5 | 機械面交給本檔；**Human 未簽** |
| 無 🔴 | 無產品行為 🔴；F-s7b-1／F-c-4／F-s7b-6／F-s7b-7 皆 🟡 | **待 Human 接受／park D-1／D-2／D-3／F-c-4** |
| F3 | 明確未做 | 不得當五站已切 |
| Human G3 | **未寫** | 頂欄 PRE-REVIEW；建議路徑＝owner rick 親審 |

- G3 | 2026-09-14 | Writer B 落 PRE-REVIEW 稿。standing 吸 A／C 後仍 **PRE-REVIEW**。未發明 Human PASS。D-1／D-2／D-3／F-c-4 如實。Source SHA = `858336e`（產品樹；本 docs commit 會漂 SHA，不重綁、不發明第二次 Fresh）。

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 `FORK_INTEGRATION_SHA=56c8019c1058c375755ca03944140f79ff8bbe55`。本工作樹開工 = 已合入的 `origin/main`。

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: 56c8019c1058c375755ca03944140f79ff8bbe55
FEATURE_HEAD: 858336e9441cec636549b3dc2d35ef273e03794f
INTEGRATION_SHA: 858336e9441cec636549b3dc2d35ef273e03794f
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=ALREADY_SYNCED FORK=56c8019c1058c375755ca03944140f79ff8bbe55 HEAD=858336e9441cec636549b3dc2d35ef273e03794f INTEGRATION=858336e9441cec636549b3dc2d35ef273e03794f(refs/remotes/origin/main)—— 你已經同步過了,本次輸出不算數
```

路徑①：**重綁 Final Fresh** 到當下 HEAD = `858336e`（本檔 Source SHA）。共同戰場 = #346…#351 本身，已當審核對象逐檔看過，不得用此次腳本輸出當「沒有共同戰場」。本 hop **不改產品碼**。產品碼已在 main；本 PR 只文件。

本 review hop 若改用 `--fork-sha 858336e`（= 開工 HEAD = `origin/main` tip），預期 `N_A_NO_INCOMING`（分岔後對方零新 commit）。該輸出只記本審查 hop 座標，不取代上面 Stage 6 錨的 `ALREADY_SYNCED`，也不當「無共同戰場」。**不 merge 產品碼。**

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | D-1(L1)：host CI 四檔不在 5-tasks S-8.9 准許清單正文。`EXPECTED_MAPPED_FILES` 208→210；`devflow-check.sh` 註冊 F2 電池；architecture 釘；guide **檔案地圖列**（非 F3 cut）。4-spec L1004「超出 → L2」與 R1 CHALLENGE 留檔 | L1／🟡 | **待 Human 接受／park**。owner=rick。落點=本表。本場 CONCUR L1（與 RR1／RR2 同向）。不在本 PR 縮四檔、不重開 G2、不發明 G3 |
| 2 | D-2(L1)：Stage 4 fixture 估 ≤12 檔；**tracked＝49**（`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f2`）。B 曾寫 62、C 曾寫 63＝run-generated 另計，不與 tracked 混寫 | L1／🟡 | park。不動 R/S。owner=rick。落點=本表 |
| 3 | D-3(L1)：`5-tasks.md` frontmatter `draft`→`approved`（N1-arm／graph P0）。checkbox 未勾、不是 T ACCEPTED、不是 G3 | L1／🟡 | 接受為握手。owner=rick。落點=本表 |
| 4 | F3 新 slug 預設五站未切（S-8.1）。`graph.yaml` 未改 | 範圍 | 另刀 F3。本場不宣稱 |
| 5 | doctor 綠陷阱仍在採用現場（4-spec Known design limit）。F2 只加行為牙，不修 `_doctor_impl.py` | 已知 | 維持約束 |
| 6 | 步 2c：Stage 6 錨 `ALREADY_SYNCED`；本 review hop 可另記 `N_A_NO_INCOMING`（fork＝`858336e`）。兩輸出皆不作「無共同戰場」證據 | 流程 | 已走路徑① 重綁 Fresh 到 `858336e`。不 merge |
| 7 | 本檔 `verdict: PRE-REVIEW`。全勾 ≠ PASS。Human 未簽 | 流程 | 建議 owner rick 親審後走官方 write 路徑 |
| 8 | F-c-4(L1)：`five_station_f2.py` 1158 行 > Diff Budget coordinator ≤600。作者未立 D-n；B 原標 🟢「不另開 🟡」。standing 吸 C 改記 🟡 | L1／🟡 | park。不拆第二家族。owner=rick。落點=本表 |

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**:無未授權 Boundary 變更（DIC 六項未命中）。D-1 是 Files／CI 註冊 L1，**不是** Boundary 變更；仍須 Human 明示接受或 park（本表 #1）。無記錄的 🟡 = 未處置，**本項不勾**
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:F2 不 bump 契約、不切 `graph.yaml` 預設。Quiz 留給 Human 若認為本刀仍算不可逆；本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:ALREADY_SYNCED 三 SHA＋canonical ref 貼於 Verdict；Fresh 重綁 `858336e`。本 review hop 另可記 `N_A_NO_INCOMING`（fork＝`858336e`）。Verdict 後禁改產品碼
- [ ] PR → main:本 hop 開 Stage 7-B 草稿 PR；**禁直上 master**。不合併。Human 未簽
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（F2 不改 living 契約句；F3 才動）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**
- [ ] 7-review frontmatter status: shipped:本 hop `status: draft` + `verdict: PRE-REVIEW`（**不是** shipped、**不是** PASS）
- [x] 7-review.html 已產生:先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py /workspace five-station-f2 7-review`（twin 覆寫同檔；無 shots 時 twin 較完整；抽驗格＝中位列 S-4.11；Human 加抽 S-4.1；殘項 S-4.3）。不吸 C 的非 twin HTML
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| Human G3 前 | rick | 本檔 Coverage／KL #1；`test-five-station-f2.sh` 仍 failed=0 且 `--only` exit 3 | 電池變紅、hollow 不再是 3、或有人把本 slug 當新 5 |
| F3 開工前 | rick | S-8.1／KL #4；guide 用語仍舊 7 | 有人把 F3 cut 改成 In |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本 hop **故意**留 `PRE-REVIEW`。不吸 A 的空 `verdict:`。不吸 A 已勾 Exit DBC。Writer B／standing 不代填。
2. **D-1 准許清單張力**：四檔是 CI 註冊。本場 CONCUR L1。R1「超出→L2」字母讀留檔。Human 必須明示 park，否則 Exit 第 1 條不得勾。
3. **Scope**：只 F2。把 F3 cut 或「五站已切」當成已交付 = 錯。出貨證據＝**單一電池 + hollow 三探針**，不是檔在、不是只 F1 綠。
4. **2c**：Stage 6 錨 `ALREADY_SYNCED`。本 review hop 可另記 `N_A_NO_INCOMING`。不重 merge。Fresh 綁 `858336e`。
5. **作者 vs 本場**：Self-Review ①–⑧ 主張電池綠＋RR1／RR2 10／10＋未發明 G3 —— 與本場實跑一致。作者 T 列不是 G3。
6. **standing 吸收**：Winner 仍 B。吸 A＝A5 八點圖＋Human 抽驗 S-4.1（`:35-41`／`:1133-1149`）＋hollow 三列＋fixture `git ls-tree` 誠實。吸 C＝F-c-4 1158＞600 L1 park＋D-2／D-3 🟡＋可選 `N_A_NO_INCOMING`＋gauntlet 可加嚴 `--require-layer test-five-station-f1`。不吸 C 非 twin HTML。

### A2　本場不宣稱的事

F3 預設切線。living spec 改寫。Human G3 PASS。STATUS shipped。5-tasks checkbox 勾選（仍未勾，正確）。

### A3　建議 Human 路徑（未走）

1. 開本 PR 審頁。
2. 抽驗 **S-4.1** 三個 `檔:行`（入口／`:35-41` OFFICIAL 18／`:1133-1149` `--only` exit 3）。殘項 S-4.3 仍在（`:466-467`／`:464-465`／`:877-882`）。
3. Known Limits #1（D-1）與 #8（F-c-4）：接受／park 或回 G2。
4. 判定只經頁尾「提交判定」或 `scripts/devflow_gate.py write`。Agent 不代填。不發明 PASS。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
858336e9441cec636549b3dc2d35ef273e03794f

$ bash scripts/test-five-station-f2.sh
… 18 × === CASE … [ok] …
failed=0
exit 0

$ bash scripts/test-five-station-f2.sh -v | grep -c '^=== CASE'
18

$ bash scripts/test-five-station-f2.sh --only new5; echo $?
3
$ bash scripts/test-five-station-f2.sh --only old7; echo $?
3
$ bash scripts/test-five-station-f2.sh --only f1; echo $?
3
$ bash scripts/test-five-station-f2.sh --bogus; echo $?
2

$ bash scripts/test-five-station-f2.sh --group must-keep -v | grep -c '^=== CASE'
16
$ bash scripts/test-five-station-f2.sh --group doctor-route -v | grep -c '^=== CASE'
4
$ bash scripts/test-five-station-f2.sh --group events -v | grep -c '^=== CASE'
3

T-6 hop CASE 合計=6（I／D／Sp／Bu／PRED-STOP／Sp5b）

$ bash scripts/check-spec-gate.sh docs/dev/five-station-f2/4-spec.md
✅ C1…C9
✅ G2 spec gate:9/9 全過
exit 0

$ bash scripts/test-five-station-f1.sh
failed=0
CASE=63
exit 0

$ bash scripts/check-file-map.sh
scanned=210 exempted=13
✅ PASS
exit 0

$ bash scripts/check-gate-tokens.sh
✅ Gate Token 釘死守衛:全過
exit 0

$ bash hooks/devflow-doctor.sh
✅ devflow doctor: COMPATIBLE
exit 0
```

官方 18 名（預設入口印出）：NEW5-Q12-ZERO、NEW5-RUN2、NEW5-CAP-3、NEW5-STORE-READ、NEW5-DECIDE-2、NEW5-GOAL-2、NEW5-SPEC-SHARE、NEW5-BUILD-SHARE、NEW5-SEVEN-STEM、NEW5-HOP-OK、NEW5-PRED-STOP、NEW5-MK-RED、NEW5-SHIP-MECH、NEW5-WAIT-RED、OLD7-FOLD-RED、OLD7-NO-FIVE、OLD7-TOKEN、OLD7-SELF。無 `NEW5-MKTG-*`／`NEW5-EVT-*`／`NEW5-MK-ANY`。

### A5　Evidence 八點 + Gauntlet

G3 錨八點（正本 `guides/guide-dev-flow.html#gates`）本場對照 —— **單一電池 + hollow ≠ 檔在／只 F1**：

1. Final Fresh 綁 Source SHA＝送審產品 HEAD：`858336e9441cec636549b3dc2d35ef273e03794f`。本 PR 只文件，不改產品碼。docs commit 會再漂 SHA，不重綁、不發明 Final Fresh。
2. Required Layer = pass：spec-gate 9/9；token 全過。電池已落地 → 本場把 `test-five-station-f2` 當加嚴 Required 且 pass。
3. 已觸發 Conditional = pass：F2 電池＋hollow 三探針；F1 回歸。
4. 不得存在任何 fail：Verification Evidence 層表無 fail。
5. Required 不得 unverified／n-a：電池／spec-gate／token 皆 pass。
6. Explicitly Excluded 可 n-a＋理由：UI e2e／負荷／金流已附理由。
7. Optional 可 unverified＋誠實：無另開 Optional 層假裝 pass。
8. Gauntlet PASS 不取代雙軸／Walkthrough／矩陣／現象：見本檔三大節。Human 未簽。

Writer B 於產品樹 `858336e`（本雙檔 commit 前）親跑：

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f2/7-review.md \
    --source-sha 858336e9441cec636549b3dc2d35ef273e03794f \
    --review-file --require-layer test-five-station-f2
✅ evidence gauntlet: 69 checks passed — docs/dev/five-station-f2/7-review.md
exit 0
```

standing 加嚴只加 `--require-layer test-five-station-f1`（吸 C 可選；不拿掉 Required）。本 branch docs commit 後 `--review-file` 強制當下 HEAD → E2 宣告 `858336e` ≠ HEAD（預期漂移，**不重綁、不發明第二次 Fresh**）：

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f2/7-review.md \
    --source-sha 858336e9441cec636549b3dc2d35ef273e03794f \
    --review-file --require-layer test-five-station-f2 \
    --require-layer test-five-station-f1
❌ evidence gauntlet: 1 violation(s) in 82 checks
  - E2: stale evidence:宣告 Source SHA 858336e ≠ 當下 docs HEAD
exit 1
```

`--source-sha` 仍綁產品樹 `858336e`。Required 兩層用 4-spec 解析出的**全名**（全形括號，不是 substring）。

`7-review.html`：先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py`（twin 覆寫同檔；無 shots 時 twin 較完整）。**不吸 C 只跑 build-stage7-html、沒過 twin 的 HTML。** Pages 掛 twin。

### A6　作者對照（N4；矩陣之後才讀）

- Self-Review ①–⑧：70 S 有 S-id assertion、未發明 G3、D-1／D-2／D-3 對得上、DBC 未偷偷修 limit —— 與獨立實跑一致。
- RR1／RR2：各 10／10 ACCEPTED（#350／#351）。不是 self-ACCEPTED。本場抽查 T-4 `or True` 已刪、T-6 `why==Sp2`、T-8 16 overlay 真拒 —— 與 RR 列相符。
- 差異：作者 6-notes 寫 T-5 殘「第 4 格掛 NEW5-Q12-ZERO」—— 本場親跑確認，列 F-s7b-3 🟢。standing 另記 F-c-4 🟡（1158＞600；作者未立 D-n）。
- Decisions（JSON 倉／電池不拆檔／`--only` exit 3／must-keep 用官方名）不構成 L2。
- 不另存 `7-review-*.md`。
- standing 不換 winner。不發明 Human G3 PASS。
