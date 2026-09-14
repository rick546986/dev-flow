---
feature: five-station-f3
stage: 7-review
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-14
---
- Human verdict note: human:rick @ 2026-09-14 Asia/Taipei, owner chat「G3過」+ park D-1/fixture 49>12/1162>200/N1-arm/contract dual-copy

# 7. 驗證 —— **G3 PASS**（F3 knife only）

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
> | 5 | **抽驗一列** | Human 抽驗加 **S-5.1**：`scripts/test-five-station-f3.sh:1-20`（單一入口 `exec python3 five_station_f3.py`）、`scripts/five_station_f3.py:32-58`（OFFICIAL 25）、同檔 argparse `:1058-1059` **且** exit body `:1134-1145`（`--only new5&#124;old7&#124;token` → exit 3；**不是** `:1133`）。twin 第五格＝Coverage 中位列 **S-5.2**（決定論 `rows[n//2]`：官方 25 名皆在）。殘項 **S-2.4**：full `:545-561`（`declared` 真／cut 假 → `allow_legacy`）＋ reason `:177-178` 字面 `F3 cut 未發生`。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡**。雙軸審(mattpocock):Standards = 通用品質、Spec = 逐條對
> 4-spec。本次 S 全綠 + **既有測試全綠(回歸)** + 無 🔴 才 PASS。
> **出貨樹=審過的樹**:整合回歸(改 HEAD)必須在 Final Fresh 之前;Verdict 後改碼
> 作廢 G3。過 gate 後產 7-review.html 供報告。
> 本階段固定產出:`7-review.md`(本模板全節)+ `7-review.html`(G3 必產;必含
> 變更架構圖、F-id 分級表、現象證據表、全 branch diff 折疊 + 執行記錄表)。
> **就這兩個檔,不多不少。禁止長出 `7-review-<誰>.md`、`7-self-review.md` 這類並存檔**。
>
> 用途:**G3 出貨關卡**。Human G3 PASS recorded:`human:rick` @ 2026-09-14 Asia/Taipei（owner chat「G3過」）。operator tony 經 `scripts/devflow_gate.py write` 落頂欄。`status: approved`（Exit 人項未全勾 → 尚未 shipped）。
> 機械審查正本仍是獨立 Writer B／`s7-fresh-reviewer-B` 的 Stage 7 檔（#391 Winner B + standing soft-fix）。`Source SHA` 維持產品樹＋#390 companion tip `cc5faa9f2c3c02709758b9805ba52bc984dcadf7`（本 docs commit 會再漂 SHA，不重綁、不發明第二次 Final Fresh）。
> KL #1…#5 L1 由 owner 經本 PASS **接受／park**。STATUS.md Active 不在本 PR 改。Scope = **F3 knife only**。cut **已發生**（三槽檔＋根契約 `2.1.0`＋`next_when_five`＋NEW5 預設五站）。**本 slug／f2／simplify 仍舊 7**（`refuse=仍舊 7 in-flight`；live probe 見 A4）。不重開 F2 park D-1／D-2／D-3／F-c-4。不開新刀。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | Writer B／`s7-fresh-reviewer-B`（fresh-context Cloud Agent `bc-13a4756b-4bbb-4063-9c2c-8774388aaee3`；**≠** Stage 6 實作 owner。#385 implementer stream） |
| Stage 6 實作 | #385 `7c2ef24`；獨立 T-Review RR1（#389）／RR2（#388）各 10／10 ACCEPTED。**不是** G3 |
| Human G3 | **PASS** recorded:`human:rick` @ 2026-09-14 Asia/Taipei（owner chat「G3過」+ park KL #1…#5）。`reviewers: [user]`；`owner: rick`。operator tony 經 `scripts/devflow_gate.py write` |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、49 S、DD-1…DD-10 Owner PASS） ②`5-tasks.md`（T-1…T-10；`status: approved`＝N1-arm） ③`scripts/test-five-station-f3.sh` + `five_station_f3.py` + fixtures ④`git diff 822f842..7c2ef24` ⑤親跑電池／hollow／spec-gate／F2／F1／tokens／file-map／doctor → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-n／RR1／RR2 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 session runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 `main` tip `#385`=`7c2ef24` + companion `#390`=`cc5faa9`。本 PR **只** 7-review 雙檔。不改 STATUS／HISTORY。**Human G3 PASS recorded**；owner standing 准 merge |
| 可信／打折 | 機械數字（25 unique CASE／CASE 行=33／failed=0／hollow exit 3／`--probe polarity` exit 1／spec-gate 9/9／F2 18／F1 63）仍以 PRE-REVIEW 場為準，本 hop 不新造證據。F-s7b-1…F-s7b-5 🟡 = KL #1…#5 已由 owner 接受／park。Human G3 已由 rick 落檔 |

建議路徑已走完：owner chat「G3過」＋ park KL #1…#5（D-1 三支 CI／fixture 49>12／coordinator 1162>200／N1-arm／契約 dual-copy）。頂欄經 `scripts/devflow_gate.py write`。不開新刀。

## Coverage Matrix

自建（grep `S-`／`=== CASE`／`OFFICIAL` ↔ 4-spec 49 S；**未先讀** Self-Review）。末列固定回歸。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `ATTEST-VISIBLE --slot ok`；`five_station_f3.py:450-456` 三槽＋`f3-cut`＋回 True | ✅ |
| S-1.2 | 同 CASE `--slot missing`／`--slot empty`；`:460-469` 回 False | ✅ |
| S-1.3 | `ATTEST-SILENT-RED`；`:505-508` silent True 無三槽＝紅格 | ✅ |
| S-1.4 | `--slot readonly`；`:477-482` 位元組不變 | ✅ |
| S-1.5 | `--slot sibling-reject`；`:485-494` 契約無 cut 兄弟鍵 | ✅ |
| S-1.6 | #385 `git diff --name-only` 無 `STATUS.md`；guide L573「五站單行」；HOLLOW-WORD 獨立紅；函式只讀檔 | ✅ |
| S-2.1 | `READ-SEAM --reader canonical-200`；`:531-532` 回 `2.0.0`；`contract_version` 只 `blob.get("devflow_contract_version")` `:109` | ✅ |
| S-2.2 | `READ-SEAM` 無旗標；`:523-527` 舊 reader 看不見 2.1＝紅格。F2 `:268` 仍讀錯鍵（READ-SEAM 牙） | ✅ |
| S-2.3 | `--reader canonical-210`；`:537-541` 以 `2.1` 開頭、`declared` 真、cut 仍獨立假 | ✅ |
| S-2.4 | `PRE-210-NE-CUT`；full `:545-561`＋reason `:177-178` 字面 `F3 cut 未發生`（本場殘項抽驗） | ✅ |
| S-2.5 | `PRE-AND` 三 `--missing`；`:571-599` 理由對缺的那一條 | ✅ |
| S-2.6 | `PRE-HOPS-200`；`:608-614` SLOT-REJECT＋仍舊 7＋無 marketplace | ✅ |
| S-2.7 | 同 CASE；`:613` undeclared 時 skip 側不生效（`graph_next` 回 `N7-g1`） | ✅ |
| S-3.1 | `NEW5-CUT-OK`；`:628-638` 五站；s2=`N8-end`／s4=`N7-end`；無「請人審」 | ✅ |
| S-3.2 | `PRE-HOPS-200`＋`--group graph-edges`；條件邊在、未宣告仍進 `N7-g1` | ✅ |
| S-3.3 | `GRAPH-WORD-NE`；`:650-674` guide 已五站用字、YAML default 仍 `N7-g1`、注入 constant＝紅格 | ✅ |
| S-3.4 | 同 CASE；`:652` 節點檔仍在；`TOKEN-KEEP`／`check-gate-tokens.sh` 綠 | ✅ |
| S-3.5 | NEW5-CUT-OK；`:634-636` 閘與 stage2／stage4 同意；graph-edges 只印官方名 | ✅ |
| S-3.6 | `stage2/graph.yaml:48`／`stage4/graph.yaml:86` `next_when_five`；節點未刪；不是只翻函式 | ✅ |
| S-4.1 | 根 `devflow-contract.json`＝`2.1.0`；`hooks/runtime-capabilities.json` 含 `2.1.0`；`_doctor_impl.py` diff 空 | ✅ |
| S-4.2 | `DOCTOR-HONEST`；`:691-695` 印 `INCOMPATIBLE` 且非 0 | ✅ |
| S-4.3 | `DOCTOR-NE-TICKET`；stdout `路線未宣告 仍舊 7`；禁 doctor-ticket 句 | ✅ |
| S-4.4 | `git diff --exit-code -- hooks/_doctor_impl.py`（本場相對 `822f842` 與工作樹皆空） | ✅ |
| S-4.5 | `allow_legacy` `:149-152` 丟棄 doctor／marketplace／cache；PRE-HOPS-200 理由無 marketplace | ✅ |
| S-5.1 | 全入口 exit 0；`--only new5&#124;old7&#124;token` 各 exit 3（本場抽驗列） | ✅ |
| S-5.2 | 預設 `-v` unique 官方名＝25；Decision 原 20 列皆在；無減列 | ✅ |
| S-5.3 | `--probe polarity` exit **1**（真評，不是 stub 綠）；紅格餵 `evaluate_hop` | ✅ |
| S-5.4 | `HOLLOW-TRUE`；`:854-858` 注入 True-as-green＝紅格 | ✅ |
| S-5.5 | `HOLLOW-FILES`；`:867-872` 檔在＝紅格 | ✅ |
| S-5.6 | `HOLLOW-F2`；`:878-883` 只 F2 綠＝紅格 | ✅ |
| S-5.7 | `F3-F2-REGRESS`；本場另跑 `test-five-station-f2.sh` failed=0 CASE=18。**不是** IFF 第四路 | ✅ |
| S-5.8 | `TOKEN-KEEP`；`check-gate-tokens.sh` exit 0 | ✅ |
| S-5.9 | `HOLLOW-WORD`；`:892-898` 獨立紅，不是 GRAPH-WORD-NE 附註 | ✅ |
| S-5.10 | `HOLLOW-TWO-SCRIPT`；`:904-909` 兩支各綠＝紅格；可選 check 7 行 stub | ✅ |
| S-5.11 | `HOLLOW-HTML-NE-GWT`；`new5/html-only/`；`:917-920` `has_old7` 假；不在 old7 下 | ✅ |
| S-6.1 | `NEW5-WAIT-RED`；`:732-741` 注入仍停 `N7-g1`＝紅格；cut-ok 合法 skip 不冒充本格 | ✅ |
| S-6.2 | `KEEP-MK-RED`；`:759-769` M3／M5／M9／M11／M12／M15 皆在；不只 M11 | ✅ |
| S-6.3 | `KEEP-SHIP-MECH`；`:778-785` 機械 Done＝紅格 | ✅ |
| S-7.1 | `OLD7-FREEZE`；`:793-798` 1–7 md、legacy、無五站機 | ✅ |
| S-7.2 | `OLD7-FOLD-RED`；`:804-811` 注入寫五站＝紅格 | ✅ |
| S-7.3 | `SELF-OLD7`；`:820-821` 本目錄／F2／simplify 跳不過 | ✅ |
| S-7.4 | 同 CASE；`:824-828` NEW5＝`scripts/fixtures/five-station-f3/new5` | ✅ |
| S-7.5 | 4-spec／5-tasks／`five_station_f3.py` 無「活五站 slug＝&lt;name&gt;」已核句 | ✅ |
| S-8.1 | 4-spec 頂欄仍 Human G2 PASS／approved。本 PR 不改它。Stage 4 hop 檔集已封 | ✅ |
| S-8.2 | 刀口准許清單內；禁區 `_templates/`／`_doctor_impl.py`／本目錄當 NEW5／token 刪檔／F2 已封＝0。**CI 三檔是明文 L1**（見 KL #1） | ✅ |
| S-8.3 | `docs/dev/five-station-f2/` diff 空；token 檔未刪；無 in-flight 折線 | ✅ |
| S-8.4 | `TOKEN-DEL-RED`；`:838-845` 注入刪 token 卻稱成功＝紅格 | ✅ |
| S-8.5 | 4-spec Disposition Q15–Q27 皆有去向；Q21–Q23 非可選 | ✅ |
| S-8.6 | F2 已封 R／S／park 四項不在本刀 In；`five-station-f2/` 0 檔 | ✅ |
| 既有測試套件(回歸) | `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`；`bash scripts/test-five-station-f2.sh`；`bash scripts/test-five-station-f1.sh`；`bash scripts/check-file-map.sh`；`bash scripts/check-gate-tokens.sh` | ✅ |

**回歸末行（reviewer @ `cc5faa9`）**：spec-gate `9/9` exit 0（49 S）；F3 unique CASE=25、CASE 行=33、failed=0；F2 `failed=0` CASE=18；F1 `failed=0` CASE=63；file-map `scanned=213` exit 0；tokens 全過；預設 doctor `COMPATIBLE`（讀 `docs/dev/devflow-contract.json` 仍 `2.0.0` ∈ supported——**綠≠ticket**）；`--contract` 根檔才印 `2.1.0`（見 KL #5）。`--only f1`／`--bogus` exit 2。doctor 綠不是 hop 通行證。live probe：`2.1.0 True 仍舊 7 in-flight`。

## Verification Evidence

<!-- Final Fresh 在 ALREADY_SYNCED 之後重綁當下 main tip（步 2c 路徑①）。
     產品碼樹 = origin/main after #385 + #390。本 PR 後續只加本雙檔，不改牙。 -->

- Source SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
- Final Fresh Run ID: f3-s7b-fresh-cc5faa9-20260914
- Entry point: `bash scripts/test-five-station-f3.sh`（Conditional 已落地 → 本場列入加嚴 Required）然後 `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`） | `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md` | pass | exit 0; 9/9; 49 S | |
| token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F3 電池列 Required | `bash scripts/check-gate-tokens.sh` | pass | exit 0; G1 2 token; G2 3 token; G3 4 token | |
| test-five-station-f3 | `bash scripts/test-five-station-f3.sh` | pass | failed=0; unique CASE=25; CASE lines=33; exit 0 | |
| hollow --only new5 | `bash scripts/test-five-station-f3.sh --only new5` | pass | exit 3; 印 hollow --only new5 | |
| hollow --only old7 | `bash scripts/test-five-station-f3.sh --only old7` | pass | exit 3; 印 hollow --only old7 | |
| hollow --only token | `bash scripts/test-five-station-f3.sh --only token` | pass | exit 3; 印 hollow --only token | |
| --probe hollow-true | `bash scripts/test-five-station-f3.sh --probe hollow-true` | pass | exit 3 | |
| --probe hollow-files | `bash scripts/test-five-station-f3.sh --probe hollow-files` | pass | exit 3 | |
| --probe hollow-f2 | `bash scripts/test-five-station-f3.sh --probe hollow-f2` | pass | exit 3 | |
| --probe hollow-word | `bash scripts/test-five-station-f3.sh --probe hollow-word` | pass | exit 3 | |
| --probe two-script | `bash scripts/test-five-station-f3.sh --probe two-script` | pass | exit 3 | |
| --probe polarity | `bash scripts/test-five-station-f3.sh --probe polarity` | pass | exit 1（真評；`five_station_f3.py:282-305`／`:1118-1127`；不得當 hollow 綠） | |
| unknown --only f1 | `bash scripts/test-five-station-f3.sh --only f1` | pass | exit 2（用法；不得當 hollow 綠） | |
| unknown --bogus | `bash scripts/test-five-station-f3.sh --bogus` | pass | exit 2; 印 FATAL: 未知旗標 | |
| unknown --only | `bash scripts/test-five-station-f3.sh --not-a-real-flag` | pass | exit 2（用法；不得當 hollow 綠） | |
| test-five-station-f2 | `bash scripts/test-five-station-f2.sh` | pass | failed=0; CASE=18; exit 0 | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | failed=0; CASE=63; exit 0 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=213; table_rows=223 | |
| doctor handshake (default) | `bash hooks/devflow-doctor.sh` | pass | COMPATIBLE; 讀 docs/dev 契約 2.0.0 ∈ supported［2.0.0, 2.1.0］; gauntlet 1.3.3（綠≠ticket；KL #5） | |
| doctor handshake (root --contract) | `bash hooks/devflow-doctor.sh --contract /workspace/devflow-contract.json` | pass | COMPATIBLE; 根契約 2.1.0 ∈ supported | |
| architecture-guards PF-0 | `bash scripts/test-architecture-guards.sh` | n-a | | ENV：本機無 Python 3.9–3.11 下限直譯器（PF-0 exit 2）。不是 F3 產品行為。file-map 213 已另列 pass |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| UI e2e（本刀無新前端） | | n-a | | Explicitly excluded；F3 無產品 UI |
| 負荷／效能（路線閘非熱路徑） | | n-a | | Explicitly excluded |
| 金流／auth fuzz（不涉） | | n-a | | Explicitly excluded |
| 本 hop 跑 F3 coordinator／改 graph（碼 Out of Scope） | | n-a | | 層名是 Stage 4 hop 排除句；本場 Stage 7 已跑電池入口，不把此列標 pass 冒充「未落地」 |

八點機械面（G3 錨全文）見附錄 A5。指向 **單一電池 + hollow 三探針 + `--probe`**,不是「檔在」或「只 F2 綠」。**八點齊 ≠ 機械代填 Human G3。**

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得 silent True 當 cut（S-1.3、S-5.4） | ATTEST-SILENT-RED；HOLLOW-TRUE | pass |
| 不得 2.1.0 當 cut（S-2.4） | PRE-210-NE-CUT 理由含 `F3 cut 未發生` | pass |
| 不得只 bump 正本、不修 reader（S-2.2） | READ-SEAM 紅格；F2 舊 reader 仍在 | pass |
| 不得 hops 先切、契約仍 2.0.0（S-2.6、S-3.2） | PRE-HOPS-200 SLOT-REJECT | pass |
| 不得只改 guide 用字（S-3.3、S-5.9） | GRAPH-WORD-NE；HOLLOW-WORD 各獨立紅 | pass |
| 不得刪 N7-g1／N6-g2 或刪 token（S-3.4、S-8.4） | 節點 `test -f`；TOKEN-DEL-RED 紅；tokens 綠 | pass |
| 不得改 doctor 握手或放寬綠（S-4.2、S-4.4） | DOCTOR-HONEST；`_doctor_impl.py` diff＝0 | pass |
| 不得只跑 F2 或「檔在」當 F3 完（S-5.5、S-5.6） | HOLLOW-FILES／HOLLOW-F2 | pass |
| 不得只用字／兩支各綠／僅 html 當 GWT（S-5.9…S-5.11） | HOLLOW-WORD／TWO-SCRIPT／HTML-NE-GWT | pass |
| 不得對本目錄建五站機（S-7.3） | SELF-OLD7 | pass |
| 不得本 hop 自填 G2／G3 PASS（S-8.1） | 4-spec 已 Human G2；本檔 Human G3 經官方 write，非 Writer 自填 | pass |
| 不得 fallback 錯鍵（S-2.1） | `five_station_f3.py:109` 只讀正本鍵 | pass |
| 紅格不得把拒 hop 當綠（S-5.3） | `--probe polarity` exit 1 | pass |
| 不得把 F2 綠寫進 SC-BATTERY IFF（S-5.7） | F3-F2-REGRESS 是地板；`--only` 不是 IFF | pass |
| 不得重開 F2 park（S-8.6） | `five-station-f2/` diff＝0 | pass |
| Out of Scope 後站不准改成 In | 5-tasks Files 禁區 0；本 PR 只 7-review 雙檔 | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#385 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **s7-fresh-reviewer-B 2026-09-14 親跑** `bash scripts/test-five-station-f3.sh -v`（不採信 6-notes 貼文）。長輸出見附錄 A4。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 從三槽檔與 `f3_cut_happened` 回傳看 | `[ok] S-1.1` 四句；`which_condition=f3-cut`；回 True | ✅ |
| S-1.2 | 函式回傳 | `[ok] S-1.2 missing → False`／`empty → False` | ✅ |
| S-1.3 | ATTEST-SILENT-RED 格 | `[ok] S-1.3 silent True without slots is the red cell` | ✅ |
| S-1.4 | 呼叫前後檔位元組 | `[ok] S-1.4 bytes unchanged`／no create/delete | ✅ |
| S-1.5 | cut 路徑與契約鍵集合 | `[ok] S-1.5 live contract has no cut sibling` | ✅ |
| S-1.6 | cut 檔、guide、本 PR 檔名 | #385 無 STATUS；guide L573 五站單行；HOLLOW-WORD 紅 | ✅ |
| S-2.1 | `contract_version()` 回傳與讀鍵 | `[ok] S-2.1 reader returns 2.0.0`；源碼只正本鍵 | ✅ |
| S-2.2 | READ-SEAM 格 | `[ok] S-2.2 inject old reader claim is the red cell` | ✅ |
| S-2.3 | 回傳以 `2.1` 開頭 | `[ok] S-2.3 declared true`／cut independently false | ✅ |
| S-2.4 | `allow_legacy`／拒因 | `[ok] S-2.4 reason has F3 cut 未發生` | ✅ |
| S-2.5 | 三組缺一理由 | 三 `--missing` 各 `[ok] S-2.5` | ✅ |
| S-2.6 | SLOT-REJECT 牙 | `[ok] S-2.6 SLOT-REJECT`；stdout `SLOT-REJECT 仍舊 7 N7-g1` | ✅ |
| S-2.7 | 同刀契約鍵與 graph 預設 | `[ok] S-2.7 skip side inactive while undeclared` | ✅ |
| S-3.1 | fixture hop 紀錄 | `[ok] S-3.1 route is five`；`hop-record route=five s2=N8-end s4=N7-end` | ✅ |
| S-3.2 | 採用端假樹路線 | PRE-HOPS-200 仍舊 7；graph-edges 同意 | ✅ |
| S-3.3 | GRAPH-WORD-NE 格 | `[ok] S-3.3 wording-only inject graph_next stays N7-g1 is the red cell` | ✅ |
| S-3.4 | `ls`／token 牙 | 節點在；tokens exit 0 | ✅ |
| S-3.5 | 同一 fixture 的 next 與 `allow_legacy` | `[ok] S-3.5 gate and stage2/stage4 agree` | ✅ |
| S-3.6 | Files 與 diff 檔名 | 兩份 `graph.yaml` 有 `next_when_five`；無節點刪檔 | ✅ |
| S-4.1 | capabilities 與 doctor diff | supported 含 `2.1.0`；握手檔空 diff | ✅ |
| S-4.2 | doctor stdout／exit | `[ok] S-4.2 prints INCOMPATIBLE`／non-zero | ✅ |
| S-4.3 | hop 拒絕理由 | stdout `路線未宣告 仍舊 7`；禁 doctor-ticket | ✅ |
| S-4.4 | `_doctor_impl.py` diff | 空 | ✅ |
| S-4.5 | 路線閘輸入 | 丟棄 cache／marketplace；缺前置仍 legacy | ✅ |
| S-5.1 | 入口 stdout／exit | 全入口 0；`--only` 3／3／3；未知 2 | ✅ |
| S-5.2 | CASE 名清單 | unique 25＝官方 25；原 20 列皆在 | ✅ |
| S-5.3 | 極性探針 | `--probe polarity` exit 1（`:282-305`／`:1118-1127`） | ✅ |
| S-5.4 | HOLLOW-TRUE 格 | `[ok] S-5.4 inject True-as-green is the red cell` | ✅ |
| S-5.5 | HOLLOW-FILES 格 | `[ok] S-5.5 inject files-exist-as-green is the red cell` | ✅ |
| S-5.6 | HOLLOW-F2 格 | `[ok] S-5.6 inject F2-green-as-F3 is the red cell` | ✅ |
| S-5.7 | F2 電池 stdout／exit | failed=0 CASE=18；不是 IFF | ✅ |
| S-5.8 | token 牙 | exit 0 | ✅ |
| S-5.9 | HOLLOW-WORD 格 | `[ok] S-5.9 inject wording-as-green is the red cell` | ✅ |
| S-5.10 | 是否單一 process 入口 | `[ok] S-5.10 two scripts each green is the red cell` | ✅ |
| S-5.11 | `has_old7` 回傳 | `[ok] S-5.11 has_old7 false`／not under old7 | ✅ |
| S-6.1 | NEW5-WAIT-RED 格 | `[ok] S-6.1 inject wait is the red cell` | ✅ |
| S-6.2 | KEEP-MK-RED 格 | stdout `injected-mk M3 M5 M9 M11 M12 M15` | ✅ |
| S-6.3 | KEEP-SHIP-MECH 格 | `[ok] S-6.3 inject mechanical Done is the red cell` | ✅ |
| S-7.1 | OLD7 目錄與 hop | `[ok] S-7.1 no five-station machine`／still old 7 | ✅ |
| S-7.2 | OLD7-FOLD-RED 格 | `[ok] S-7.2 inject five-station write on OLD7 is the red cell` | ✅ |
| S-7.3 | 被拒 hop 與目錄檔名 | 三 slug `[ok] S-7.3 … cannot auto-advance` | ✅ |
| S-7.4 | NEW5 根路徑 | `[ok] S-7.4 NEW5 is synthetic` | ✅ |
| S-7.5 | 全文搜「活五站 slug＝」 | 無已核句 | ✅ |
| S-8.1 | 4-spec 頂欄 | 仍 G2 PASS；本 PR 不改 | ✅ |
| S-8.2 | 5-tasks Files 聯集與 diff 檔名 | 准許清單內＋CI 三檔 L1（KL #1） | ✅ |
| S-8.3 | git diff 檔名 | F2／token 刪檔／折線＝0 | ✅ |
| S-8.4 | TOKEN-DEL-RED 格 | `[ok] S-8.4 inject token delete claim is the red cell` | ✅ |
| S-8.5 | Disposition 表 | Q15–Q27 皆有列 | ✅ |
| S-8.6 | Out of Scope 與 F2 目錄 | park 四項不在 In；F2 0 檔 | ✅ |

## 截圖槽

本場無產品 UI（F3 = CLI coordinator + fixture 自檢）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = 電池 CASE stdout
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F3 是 cut 紀錄／讀鍵／路線閘／graph 條件邊／電池，不是現場交接 UI。有 Operational Context 的 S 以「owner 寫三槽／寫手被閘擋住或立刻 hop／Ship 唯人」走一遍；標不適用的純內部 S 不裝成人員旅程。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 母版 owner | 留下可指的 cut | 打開 `f3-cut-attestation.json` | git 提交三槽 | 檔未寫＝未切 | 人指得到 who／when／`f3-cut` |
| S-1.2／S-1.4／S-1.5 | — | — | 讀端布林 | — | 缺槽＝False | 不適用（讀端） |
| S-1.3 | Ship 審查者／電池 | 擋空切 | ATTEST-SILENT-RED | 不把函式真當刀 | 該格紅 | 空切可見 |
| S-1.6 | 看板寫手 | 用語切五站 | guide 七站單行→五站 | STATUS 走 companion | 看板 ≠ SoT | 本 feature branch 無 STATUS |
| S-2.1…S-2.3 | — | — | 讀鍵 | — | 錯鍵不冒充 | 不適用（讀鍵） |
| S-2.4 | coordinator | 第三位元可獨立假 | PRE-210-NE-CUT | 不把 bump 當 cut | legacy | 理由=`F3 cut 未發生` |
| S-2.5 | — | — | 三缺一 | — | 各對理由 | 不適用（同一閘） |
| S-2.6 | 採用端 owner | 升級後不被改線 | PRE-HOPS-200 | 自己 bump 契約 | 未 bump＝舊 7 | SLOT-REJECT |
| S-2.7 | — | — | 同刀順序 | — | 未宣告不跳過 | 不適用 |
| S-3.1 | 新 slug 寫手 | 不等例行閘 | `--case NEW5-CUT-OK` | 不寫「要不要繼續」 | Ship 仍等 | hop 無 N7-g1／N6-g2 |
| S-3.2／S-3.5／S-3.6 | — | — | 條件邊＋閘 | — | 兩邊同意 | 不適用（機制） |
| S-3.3 | 電池作者 | 用語≠行為 | GRAPH-WORD-NE | 不把用字當成功 | 該格紅 | 極性對 |
| S-3.4 | — | — | 節點／token | — | 不刪 | 檔在 |
| S-4.1／S-4.4／S-4.5 | — | — | 清單／握手 | — | 握手 0 diff | 不適用 |
| S-4.2 | doctor 操作者 | 看見誠實紅 | DOCTOR-HONEST | 補清單不是放寬握手 | INCOMPATIBLE | 誠實紅＝本格綠 |
| S-4.3 | 寫手 | 綠不當路條 | DOCTOR-NE-TICKET | 不跟 hops | 拒 | 理由是路線 |
| S-5.1／S-5.2／S-5.3／S-5.7 | — | — | 電池入口 | — | hollow exit 3 | 不適用（完成定義） |
| S-5.4…S-5.6／S-5.9…S-5.11 | 電池作者 | 餵 hollow | `--group hollow` | 不把假綠當完 | 各格獨立紅 | 極性對 |
| S-5.8 | — | — | token 牙 | — | 字面仍在 | 不適用 |
| S-6.1 | 新 slug 寫手 | 不等例行閘 | NEW5-WAIT-RED | 刪等人句 | 注入停＝紅 | 該格紅 |
| S-6.2 | T reviewer | Must-keep 仍咬 | KEEP-MK-RED | 補缺的 M | cut 不省略 | 六個 M 皆在 |
| S-6.3 | Ship 審查者 | 機械綠 ≠ PASS | KEEP-SHIP-MECH | 人寫 PASS | 無人則留 Ship | 自動 Done＝紅 |
| S-7.1 | in-flight 執行者 | 走完舊 7 | OLD7-FREEZE | 不中途折 | 仍等既有閘 | 無五站機 |
| S-7.2 | 電池作者 | 擋折線 | OLD7-FOLD-RED | — | 該格紅 | 極性對 |
| S-7.3 | F3 實作 agent | 不污染觀測 | SELF-OLD7 | 不拿本目錄當 NEW5 | 跳不過 | 本 slug 仍舊 7 |
| S-7.4／S-7.5 | — | — | 合成根／命名禁令 | — | 不發明活五站名 | 不適用 |
| S-8.1 | Writer／reviewer | 不自填 G2／G3 | 頂欄 | 人審才寫 PASS | 等人 | Human G3 經官方 write |
| S-8.2／S-8.3／S-8.6 | Stage 5／6 寫手 | 只施工 F3 | Files 聯集 | F2 park 另檔 | CI 三檔 L1 | 刀口守住；L1 明文 |
| S-8.4 | 電池作者 | 擋刪 token | TOKEN-DEL-RED | — | 該格紅 | 極性對 |
| S-8.5 | — | — | Disposition | — | Q 不消失 | 不適用（對帳） |

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec ②③⑧⑨⑩）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中。F3 讀 doctor／契約當證據，Files 不含 `hooks/_doctor_impl.py`；#385 未改握手語意。
2. **資料所有權被繞過寫入**:未命中。cut owner＝寫入三槽檔的人類；函式只讀（S-1.4）。OLD7／本目錄不建五站機（S-7.1／S-7.3）。
3. **相容性破壞包成新增**:未命中到 R/S。根契約 bump 2.1.0 是本刀授權。`docs/dev/devflow-contract.json` 仍 2.0.0＝doctor 讀徑分裂（KL #5），**不是**把 2.1.0 包成「可選欄位」蒙混——根檔已明寫 2.1.0。`agent-event` 未 bump。
4. **一致性邊界被拆解**:未命中。三前置同一 `allow_legacy`；graph `next_when_five` 讀同一 `allow_legacy`（S-3.5）。
5. **宣告的 Test seam 未被使用**:未命中。seam＝`f3_cut_happened`／`contract_version`／`evaluate_hop`／`--case`／`--only`／`--probe`；電池走同一入口。
6. **Known design limit 被實作悄悄「解決」**:未命中。doctor 綠陷阱仍在現場（本場 live doctor 仍 COMPATIBLE，且讀的是 2.0.0 副本）。F2 park 四項未「修掉」。`f3_cut_happened` 不再恒 False——這是本刀授權，不是偷偷解決 F2 限制。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更（CI 三檔是 Files／註冊 L1，不是新公開 API）。

- F-s7b-1 🟡 作者 D-1：host CI **三支腳本**在 S-8.2 准許清單外（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`）。guide 路徑 **已在** S-8.2（用語交付），**不是**第四個溢出。`EXPECTED_MAPPED_FILES` 210→213。4-spec L838「超出 → L2」字母讀留檔 | 同 F2 D-1 綁：host CI 地板，不是第二次 cut、不是重開 F2 park | **CONCUR L1**（與 RR1／RR2 同向）。**Owner accepted／park** via Human G3 PASS。見 Known Limits #1
- F-s7b-2 🟡 `scripts/five_station_f3.py` `wc -l` = 1162 > Diff Budget coordinator ≤200 | 行數超估一個數量級 | 單一家族、不拆第二檔（會撞 Files 格）。不動 R/S。**Owner accepted／park** via Human G3 PASS。見 KL #4
- F-s7b-3 🟡 fixture 超 Stage 4「≤12」估計 | 估計超支 | **tracked＝49**（方法：`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3`）。不動 R/S。**Owner accepted／park** via Human G3 PASS。見 KL #2
- F-s7b-4 🟡 `5-tasks.md` `status: approved` 而 checkbox 全未勾 | 看起來像任務已核 | N1-arm／graph P0 only，不是勾 T、不是 G3。**Owner accepted／park** via Human G3 PASS。見 KL #3
- F-s7b-5 🟡 L1 契約 dual-copy：根 `devflow-contract.json`＝`2.1.0`，`docs/dev/devflow-contract.json` 仍 `2.0.0`。預設 `devflow-doctor.sh`（不帶 `--contract`）讀後者，印 `2.0.0 ∈ supported`。`--contract` 指根檔才印 `2.1.0`。Files 准許清單寫的是根檔。不是 silent extra、也不是放寬握手 | 採用端 dual-read 仍以**該專案自己的契約檔**為準；本 repo doctor 預設讀徑與路線閘讀徑分裂 | **Owner accepted／park** via Human G3 PASS。不升 🔴（S-4.1 授權 bump 根檔；S-4.3 綠≠ticket 仍成立）。見 KL #5
- F-s7b-6 🟢 `scripts/check-five-station-f3.sh` 7 行 stub、exit 0 | 選配、明文「不是電池入口」 | 對準 S-5.10；不發明第四路
- F-s7b-7 🟢 `five_station_f3.py:1058-1059`（argparse）＋`:1134-1145`（exit body；**不是** `:1133`）`--only` | 該路即使綠也 exit 3 | 對準 S-5.1；`--only f1`／`--bogus` exit 2；`--probe polarity` exit 1（`:282-305`／`:1118-1127`）
- F-s7b-8 🟢 預設入口 CASE **行**＝33、unique 名＝25 | 五切片／三 PRE-AND／三 READ-SEAM 重印官方名 | 不發明 `NEW5-MKTG-*`／`GRAPH-AGREE`
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。F-s7b-1 是 host CI 地板，不是新公開 API

## Spec Axis

逐 R。Deviations：本場獨立所見 L1 如上。無隱藏 L2。F2 park 明確未重開。Human G3 已由 rick 落檔；Writer 未自填。

| R | 判定 | 證據 |
|---|---|---|
| R-1 | **符合** | S-1.1…S-1.6；三槽只讀；silent True 紅；契約無兄弟鍵；STATUS 不在 #385 |
| R-2 | **符合** | S-2.1…S-2.7；只讀正本鍵；PRE-210 理由字面；PRE-AND 三缺；SLOT-REJECT |
| R-3 | **符合** | S-3.1…S-3.6；`next_when_five`；節點不刪；GRAPH-WORD-NE 紅；閘與邊同意 |
| R-4 | **符合**＋F-s7b-5 🟡 | S-4.1…S-4.5；supported 加 2.1.0；握手 0 diff；HONEST／NE-TICKET。doctor **活樹讀徑**仍 2.0.0 副本（KL #5） |
| R-5 | **符合** | S-5.1…S-5.11；25 名；hollow 3；polarity 1；未知 2；F2 地板不是 IFF |
| R-6 | **符合** | S-6.1…S-6.3；WAIT／MK／SHIP 三格獨立紅；六個 M |
| R-7 | **符合** | S-7.1…S-7.5；OLD7 凍結；本目錄跳不過；不發明活五站名 |
| R-8 | **符合（刀）＋F-s7b-1 L1** | S-8.1…S-8.6。CI **三支腳本**是明文 L1，不是 silent extras。guide 路徑在 S-8.2，不算第四溢出。F2 park 0 檔。Human G3 PASS recorded |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit（doctor 綠陷阱仍在） |

## 變更架構圖

必須對上 #385 basename（本 PR 只加 `7-review.md`／`7-review.html`）。#390 是 STATUS companion，不在本 PR。

```text
[test-five-station-f3.sh] ----exec----> [five_station_f3.py]
                                         +-- f3_cut_happened / three-slot
                                         |     docs/dev/f3-cut-attestation.json
                                         +-- contract_version (canonical key only)
                                         +-- allow_legacy / refuse_hop_reason
                                         +-- graph_next / next_when_five
                                         +-- evaluate_hop / inject polarity
                                         +-- Battery official 25 CASE
[five_station_f2.py]  --old reader--     READ-SEAM 牙（錯鍵仍在）
[stage2/graph.yaml]   next: N7-g1
                      next_when_five: N8-end
[stage4/graph.yaml]   next: N6-g2
                      next_when_five: N7-end
[devflow-contract.json]            2.1.0   (repo root)
[docs/dev/devflow-contract.json]   2.0.0   (doctor 讀徑；KL #5)
[runtime-capabilities.json]        +2.1.0
fixtures/five-station-f3/new5|old7
CI floor (not 5-tasks Files union):
  check-file-map.sh        EXPECTED=213
  devflow-check.sh         architecture/test-five-station-f3 + check
  test-architecture-guards.sh  靜態釘 213
NOT in this knife:
  _templates / _doctor_impl.py handshake / token 刪檔
  docs/dev/five-station-f2/ (F2 park 不重開)
  本目錄當 NEW5 / 發明活五站名 / STATUS
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

審核的產品碼 = `822f842..7c2ef24`（#385 實作＋standing rework）。companion `#390`=`cc5faa9` 只 STATUS／HISTORY。本 Stage 7 PR 只新增本雙檔。共同戰場已是送審樹本身（見 2c）。

<details>
<summary title="+1162/-0; cut + reader + gate + battery"><code>scripts/five_station_f3.py</code> (+1162/-0)</summary>
<pre><span class="add">+OFFICIAL = 25 CASE 名</span>
<span class="add">+def f3_cut_happened(...)  # three-slot read-only</span>
<span class="add">+def contract_version(...)  # only devflow_contract_version</span>
<span class="add">+def allow_legacy(...)  # declared ∧ ¬in-flight ∧ cut</span>
<span class="add">+def evaluate_hop(...)  # inject polarity</span>
<span class="add">+class Battery  # 25 CASE + hollow --only exit 3 + --probe</span></pre>
</details>

<details>
<summary title="+20/-0; 入口"><code>scripts/test-five-station-f3.sh</code> (+20/-0)</summary>
<pre><span class="add">+exec python3 five_station_f3.py --root "$ROOT" "$@"</span></pre>
</details>

<details>
<summary title="+7/-0; 選配 stub"><code>scripts/check-five-station-f3.sh</code> (+7/-0)</summary>
<pre><span class="add">+echo "check-five-station-f3: independent check, not the F3 battery entry"</span>
<span class="add">+exit 0</span></pre>
</details>

<details>
<summary title="cut SoT"><code>docs/dev/f3-cut-attestation.json</code> (+5/-0)</summary>
<pre><span class="add">+who=rick when=2026-09-14T00:00:00+08:00 which_condition=f3-cut</span></pre>
</details>

<details>
<summary title="契約／supported"><code>devflow-contract.json</code> · <code>hooks/runtime-capabilities.json</code></summary>
<pre><span class="del">-devflow_contract_version 2.0.0</span>
<span class="add">+devflow_contract_version 2.1.0</span>
<span class="add">+supported += 2.1.0</span>
<span class="add">docs/dev/devflow-contract.json 仍 2.0.0（KL #5）</span></pre>
</details>

<details>
<summary title="條件邊"><code>skills/dev-flow/stage2/graph.yaml</code> · <code>skills/dev-flow/stage4/graph.yaml</code></summary>
<pre><span class="add">+next_when_five: N8-end   # stage2; default next 仍 N7-g1</span>
<span class="add">+next_when_five: N7-end   # stage4; default next 仍 N6-g2</span>
<span class="add">節點檔不刪</span></pre>
</details>

<details>
<summary title="fixtures 目錄"><code>scripts/fixtures/five-station-f3/*</code>（tracked 49 via git ls-tree；F-s7b-3）</summary>
<pre>方法：git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3 → 49
new5/: attest-visible 四槽、cut-ok、pre-*、read-seam、doctor-*、inject-*、html-only
old7/: 1–7 .md + inject-fold-red
完整 diff 在 #385。</pre>
</details>

<details>
<summary title="D-1 風格 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code> · <code>guides/guide-dev-flow.html</code></summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 210</span>
<span class="add">+EXPECTED_MAPPED_FILES = 213</span>
<span class="add">+architecture 組註冊 test-five-station-f3.sh / check-five-station-f3.sh</span>
<span class="add">+guide L573 五站單行 + #filemap 三列（guide 在准許清單）</span></pre>
</details>

<details>
<summary title="過程檔"><code>docs/dev/five-station-f3/6-implementation-notes.md</code> · html twin · 5-tasks</summary>
<pre>6-notes + RR1／RR2 10／10 ACCEPTED（#389／#388）。5-tasks N1-arm approved。STATUS／HISTORY 是 #390 companion，不在本 PR。</pre>
</details>

## Verdict

**Human G3 PASS。** `human:rick` @ 2026-09-14 Asia/Taipei（owner chat「G3過」）。`reviewers: [user]`。operator tony 經 `scripts/devflow_gate.py write`。KL #1…#5 L1 Owner accepted／park。不發明新 Final Fresh；Source SHA 維持 `cc5faa9`。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 49 S 全綠 | Coverage 49 列 ✅；unique 25 CASE failed=0 | reviewer 實跑；**Human G3 PASS** |
| 既有回歸綠 | spec-gate 9/9；F2 CASE=18；F1 CASE=63；file-map 213；tokens | reviewer 實跑；**Human G3 PASS** |
| 現象證據逐 S | 上表＋附錄 A4 | reviewer 親跑電池；**Human G3 PASS** |
| Evidence 契約 | 本節四欄＋層表；gauntlet 見附錄 A5 | 機械面交給本檔；**Human G3 PASS** |
| 無 🔴 | 無產品行為 🔴；F-s7b-1…F-s7b-5 皆 🟡 | **Owner accepted／park KL #1…#5** |
| F3 範圍 | cut 已寫三槽＋根契約 2.1.0＋`next_when_five`；**本目錄／f2／simplify 仍舊 7**（`refuse=仍舊 7 in-flight`） | 不得當「本 slug 已切五站」 |
| F2 park | 明確未重開 | `five-station-f2/` diff＝0 |
| Human G3 | **PASS** | `human:rick` @ 2026-09-14 Asia/Taipei owner chat「G3過」 |

- G3 | 2026-09-14 | owner chat「G3過」= Human G3 PASS。KL #1…#5 L1 accepted／park（D-1 三支 CI／fixture 49>12／coordinator 1162>200／N1-arm／契約 dual-copy 2.1.0 vs docs/dev 2.0.0）。owner 自審(有記錄)；reviewers: [user]；operator tony 經 `scripts/devflow_gate.py write` 落頂欄。Source SHA 維持 `cc5faa9f2c3c02709758b9805ba52bc984dcadf7`。不開新刀。STATUS 另 companion。

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 產品分岔點（#385 合入前 main）=`822f84289f6f4267252907e36862e93f1c90eb9d`。本工作樹開工 = 已合入的 `origin/main` tip `#390`。

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: 822f84289f6f4267252907e36862e93f1c90eb9d
FEATURE_HEAD: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=ALREADY_SYNCED FORK=822f84289f6f4267252907e36862e93f1c90eb9d HEAD=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 INTEGRATION=cc5faa9f2c3c02709758b9805ba52bc984dcadf7(refs/remotes/origin/main)—— 你已經同步過了,本次輸出不算數
```

路徑①：**重綁 Final Fresh** 到當下 HEAD = `cc5faa9`（本檔 Source SHA）。共同戰場 = #385 本身，已當審核對象逐檔看過，不得用此次腳本輸出當「沒有共同戰場」。本 hop **不重綁第二次 Fresh、不改產品碼**。產品碼已在 main；本 PR 只文件。

本 review hop 另跑 `--fork-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7`（= 開工 HEAD = `origin/main` tip）：

```
STATUS: N_A_NO_INCOMING
FORK_INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
FEATURE_HEAD: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=N_A_NO_INCOMING FORK=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 HEAD=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 INTEGRATION=cc5faa9f2c3c02709758b9805ba52bc984dcadf7(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

該輸出只記本審查 hop 座標，不取代上面 Stage 6 錨的 `ALREADY_SYNCED`，也不當「無共同戰場」。**不 merge 產品碼。**

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | F-s7b-1：host CI **三支腳本**不在 5-tasks S-8.2 准許清單正文（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`）。`EXPECTED_MAPPED_FILES` 210→213；`devflow-check.sh` 註冊 F3 電池；architecture 釘 213。guide 路徑 **已在** S-8.2（用語交付），**不是**第四溢出。4-spec L838「超出 → L2」字母讀留檔 | L1／🟡 | **Owner accepted／park** via Human G3 PASS（`human:rick` @ 2026-09-14 Asia/Taipei owner chat「G3過」）。落點=本表。owner=rick。不在本 PR 縮三檔、不重開 G2、**不重開 F2 D-1** |
| 2 | F-s7b-3：Stage 4 fixture 估 ≤12 檔；**tracked＝49**（`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3`） | L1／🟡 | **Owner accepted／park** via Human G3 PASS。不動 R/S。owner=rick。落點=本表 |
| 3 | F-s7b-4：`5-tasks.md` frontmatter `draft`→`approved`（N1-arm／graph P0）。checkbox 未勾、不是 T ACCEPTED、不是 G3 | L1／🟡 | **Owner accepted／park** via Human G3 PASS（握手）。owner=rick。落點=本表 |
| 4 | F-s7b-2：`five_station_f3.py` 1162 行 > Diff Budget coordinator ≤200 | L1／🟡 | **Owner accepted／park** via Human G3 PASS（1162>200）。不拆第二家族。owner=rick。落點=本表 |
| 5 | F-s7b-5 🟡 L1 契約 dual-copy：根 2.1.0 vs `docs/dev/devflow-contract.json` 仍 2.0.0。預設 doctor（無 `--contract`）讀後者印 2.0.0 COMPATIBLE；`--contract` 指根檔才印 2.1.0。Files 點名的是根檔 | L1／🟡 | **Owner accepted／park** via Human G3 PASS（接受分裂；doctor 綠≠ticket 仍真）。本 PR 不改契約。owner=rick。落點=本表 |
| 6 | ~~本檔 `verdict: PRE-REVIEW`。全勾 ≠ PASS。Human 未簽~~ | — | 已解除:Human G3 PASS recorded by `human:rick` @ 2026-09-14 Asia/Taipei（owner chat「G3過」）。STATUS.md Active 仍不在本 PR 改 |
| 7 | 步 2c：Stage 6 錨 `ALREADY_SYNCED`；本 review hop 另記 `N_A_NO_INCOMING`（fork＝`cc5faa9`）。兩輸出皆不作「無共同戰場」證據 | 流程 | 已走路徑① 重綁 Fresh 到 `cc5faa9`。不 merge |
| 8 | F2 park D-1／D-2／D-3／F-c-4 不重開。F3 自己的 CI／fixture／行數 L1 **不是**把 F2 park 翻成 In | 範圍 | 本場 0 檔碰 `docs/dev/five-station-f2/` |
| 9 | 可選 `check-five-station-f3.sh` 是 7 行 stub | 已知 | 維持「不是第四路」。HOLLOW-TWO-SCRIPT 仍紅 |
| 10 | doctor 綠陷阱仍在採用現場（4-spec Known design limit）。F3 只加 supported，不修 `_doctor_impl.py` | 已知 | 維持約束 |
| 11 | 本目錄／f2／simplify 仍舊 7（S-7.3）。cut 真 ≠ 本 slug 自動前進。live probe：`contract_version=2.1.0`／`f3_cut_happened=True`／`refuse=仍舊 7 in-flight` | 範圍 | **F3 範圍誠實**：已切的是「之後才開、無 1–7 `.md` 的新 slug」。本目錄是白老鼠禁區 |
| 12 | `--probe polarity` 真評（`:282-305`／`:1118-1127`）恒 exit 1。architecture-guards PF-0 本機缺 3.9–3.11＝ENV n-a | 殘項／ENV | 極性以 CASE 格為準。PF-0 不列入 F3 產品紅 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**:無未授權 Boundary 變更（DIC 六項未命中）。F-s7b-1 是 Files／CI 註冊 L1，**不是** Boundary 變更；owner 經本 PASS 已 park KL #1…#5（本表）。DBC applicable 下無 🟡 Boundary 待處置
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:本刀 bump 根契約 2.1.0＋切條件邊。Quiz 留給 Human 若認為本刀算不可逆；本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:ALREADY_SYNCED 三 SHA＋canonical ref 貼於 Verdict；Fresh 重綁 `cc5faa9`。本 review hop 另記 `N_A_NO_INCOMING`（fork＝`cc5faa9`）。Verdict 後禁改產品碼
- [ ] PR → main:本 hop 開 G3 PASS PR；**禁直上 master**。Human G3 已簽；合入由 merger 做（本 Exit 項 merge 後勾）
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（本 repo 無 living spec 條文可併；F3 不改 F1／F2 已刊 SHALL 原文）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**
- [ ] 7-review frontmatter status: shipped:本 hop `status: approved` + `verdict: PASS`（G3 先過；Exit 人項未全勾故尚未 shipped）
- [x] 7-review.html 已產生:先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py /workspace five-station-f3 7-review`（twin 覆寫同檔；無 shots 時 twin 較完整；抽驗格＝中位列 S-5.2；Human 加抽 S-5.1；殘項 S-2.4）
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| G3 後 | rick | 本檔 Coverage／KL #1…#5；`test-five-station-f3.sh` 仍 failed=0 且 `--only` exit 3 | 電池變紅、hollow 不再是 3、或有人把本 slug 當活五站 |
| 活五站開工前 | rick | S-7.5／SELF-OLD7；本目錄仍舊 7 | 有人寫出「第一隻活五站＝&lt;name&gt;」當已核 |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本 hop 已按 owner chat「G3過」落 `verdict: PASS`。
2. **Files 准許清單張力**：D-1 = CI **三支腳本**（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`）在准許清單外。guide 路徑 **已在** S-8.2，不是第四溢出。本場 CONCUR L1。R8「超出→L2」字母讀留檔。**Owner accepted／park** via 本 PASS；Exit #1 已勾。
3. **Scope 誠實**：F3 **已切**（三槽＋根 2.1.0＋`next_when_five`＋NEW5 預設五站）。**本 slug／f2／simplify 仍舊 7**（`refuse=仍舊 7 in-flight`）。把「five-station-f3 自己已走五站」當成已交付 = 錯。出貨證據＝**單一電池 + hollow 三探針 + `--probe`**,不是檔在、不是只 F2 綠。
4. **2c**：Stage 6 錨 `ALREADY_SYNCED`。本 review hop 另記 `N_A_NO_INCOMING`。不重 merge。Fresh 綁 `cc5faa9`。
5. **契約 dual-copy 🟡 L1**：根 2.1.0 vs `docs/dev` 2.0.0。預設 doctor 印 2.0.0 COMPATIBLE；`--contract` 指根檔才印 2.1.0。獨立評 L1，不升 🔴。**Owner accepted／park** via 本 PASS。
6. **行數／fixture／N1-arm**：1162＞200、49＞12、5-tasks approved 未勾——三條皆 L1，**Owner accepted／park** via 本 PASS。

### A2　本場不宣稱的事

本 slug 已切五站。STATUS shipped（另 companion）。5-tasks checkbox 勾選（仍未勾，正確）。重開 F2 park。發明活五站 slug。把 doctor 綠當已切。把 `docs/dev` 契約對齊寫進本 PR。不開新刀。

### A3　Human 路徑（已走完）

1. 開 Pages／本機審頁（路徑見 PR）。
2. 抽驗 **S-5.1** 三個 `檔:行`（入口／`:32-58` OFFICIAL 25／argparse `:1058-1059` **且** exit body `:1134-1145` `--only` exit 3；**不是** `:1133`）。殘項 S-2.4（full `:545-561`＋reason `:177-178` `F3 cut 未發生`）。
3. Known Limits #1…#5：owner 經本 PASS 接受／park。
4. 判定已落：owner chat「G3過」→ `verdict: PASS`、`status: approved`（`scripts/devflow_gate.py write`）。
5. 頂欄由官方 write 路徑寫入，attestation `human:rick @ 2026-09-14 Asia/Taipei`。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
cc5faa9f2c3c02709758b9805ba52bc984dcadf7

$ bash scripts/test-five-station-f3.sh
… unique 25 × === CASE … [ok] …
failed=0
exit 0

$ bash scripts/test-five-station-f3.sh -v | grep -c '^=== CASE'
33

$ bash scripts/test-five-station-f3.sh -v | grep '^=== CASE' | awk '{print $3}' | sort -u | wc -l
25

$ bash scripts/test-five-station-f3.sh --only new5; echo $?
3
$ bash scripts/test-five-station-f3.sh --only old7; echo $?
3
$ bash scripts/test-five-station-f3.sh --only token; echo $?
3
$ bash scripts/test-five-station-f3.sh --only f1; echo $?
2
$ bash scripts/test-five-station-f3.sh --bogus; echo $?
2
$ bash scripts/test-five-station-f3.sh --probe polarity; echo $?
1
$ bash scripts/test-five-station-f3.sh --not-a-real-flag; echo $?
2

$ for p in hollow-true hollow-files hollow-f2 hollow-word two-script; do
    bash scripts/test-five-station-f3.sh --probe $p >/dev/null; echo $p $?
  done
hollow-true 3
hollow-files 3
hollow-f2 3
hollow-word 3
two-script 3

$ bash scripts/test-five-station-f3.sh --group hollow -v | grep -c '^=== CASE'
6
$ bash scripts/test-five-station-f3.sh --group graph-edges -v | grep -c '^=== CASE'
3
$ bash scripts/test-five-station-f3.sh --group doctor -v | grep -c '^=== CASE'
2

$ bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md
✅ C1…C9
✅ G2 spec gate:9/9 全過
exit 0

$ bash scripts/test-five-station-f2.sh
failed=0
CASE=18
exit 0

$ bash scripts/test-five-station-f1.sh
failed=0
CASE=63
exit 0

$ bash scripts/check-file-map.sh
scanned=213 exempted=13
✅ PASS
exit 0

$ bash scripts/check-gate-tokens.sh
✅ Gate Token 釘死守衛:全過
exit 0

$ bash hooks/devflow-doctor.sh
✅ devflow doctor: COMPATIBLE
contract-version: 2.0.0 ∈ supported ['2.0.0', '2.1.0']
exit 0

$ bash hooks/devflow-doctor.sh --contract /workspace/devflow-contract.json
✅ devflow doctor: COMPATIBLE
contract-version: 2.1.0 ∈ supported ['2.0.0', '2.1.0']
exit 0

$ python3 -c "import sys; sys.path.insert(0,'scripts'); import five_station_f3 as f3; print(f3.contract_version('.'), f3.f3_cut_happened('.'), f3.refuse_hop_reason('.', 'docs/dev/five-station-f3'))"
2.1.0 True 仍舊 7 in-flight

$ git diff --exit-code -- hooks/_doctor_impl.py
exit 0
```

官方 25 名（預設入口 unique）：NEW5-CUT-OK、NEW5-WAIT-RED、OLD7-FREEZE、OLD7-FOLD-RED、TOKEN-KEEP、TOKEN-DEL-RED、ATTEST-VISIBLE、ATTEST-SILENT-RED、PRE-210-NE-CUT、PRE-AND、PRE-HOPS-200、READ-SEAM、DOCTOR-HONEST、DOCTOR-NE-TICKET、GRAPH-WORD-NE、SELF-OLD7、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、KEEP-MK-RED、KEEP-SHIP-MECH、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT、F3-F2-REGRESS。無 `NEW5-MKTG-*`／`GRAPH-AGREE`／`HOLLOW-OK`。

### A5　Evidence 八點 + Gauntlet

G3 錨八點（正本 `guides/guide-dev-flow.html#gates`）本場對照 —— **單一電池 + hollow ≠ 檔在／只 F2**：

1. Final Fresh 綁 Source SHA＝送審產品 HEAD：`cc5faa9f2c3c02709758b9805ba52bc984dcadf7`。本 PR 只文件，不改產品碼。docs commit 會再漂 SHA，不重綁、不發明第二次 Fresh。
2. Required Layer = pass：spec-gate 9/9；token 全過。電池已落地 → 本場把 `test-five-station-f3` 當加嚴 Required 且 pass。
3. 已觸發 Conditional = pass：F3 電池＋hollow／`--probe`；F2／F1 回歸；doctor 握手。
4. 不得存在任何 fail：Verification Evidence 層表無 fail。
5. Required 不得 unverified／n-a：電池／spec-gate／token 皆 pass。
6. Explicitly Excluded 可 n-a＋理由：UI e2e／負荷／金流已附理由。
7. Optional 可 unverified＋誠實：architecture PF-0 以 ENV n-a 記，不假裝 pass。
8. Gauntlet PASS 不取代雙軸／Walkthrough／矩陣／現象：見本檔三大節。**Human G3 PASS recorded**（`human:rick` @ 2026-09-14 Asia/Taipei owner chat「G3過」）。

Writer B 於產品樹 `cc5faa9` 綁 `--source-sha` 親跑（raw；入口＝`scripts/devflow-evidence-gauntlet.sh`）。本 branch 已有 docs commit → `--review-file` 會 E2 漂 SHA（預期；**不重綁、不發明第二次 Fresh**）。下列為不加 `--review-file` 的可重跑綠：

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f3/7-review.md \
    --source-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7 \
    --require-layer test-five-station-f3
✅ evidence gauntlet: 122 checks passed — docs/dev/five-station-f3/7-review.md
exit 0

$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f3/7-review.md \
    --source-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7 \
    --require-layer test-five-station-f3 \
    --require-layer test-five-station-f2
✅ evidence gauntlet: 123 checks passed — docs/dev/five-station-f3/7-review.md
exit 0

$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f3/7-review.md \
    --source-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7 \
    --review-file --require-layer test-five-station-f3 \
    --require-layer test-five-station-f2
# E2: 宣告 cc5faa9 ≠ 當下 HEAD（docs commit 預期漂移）。不重綁 Fresh。
```

`--source-sha` 仍綁產品樹 `cc5faa9`。Required 兩層用 4-spec 解析出的**全名**（全形括號，不是 substring）。加嚴只加 `--require-layer test-five-station-f3`／`test-five-station-f2`（不拿掉 Required）。

`7-review.html`：先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py`（twin 覆寫同檔；無 shots 時 twin 較完整）。Pages 掛 twin。

### A6　作者對照（N4；矩陣之後才讀）

讀取順序已遵守：本節之前的矩陣／實跑／雙軸未參考 Self-Review。`FORK_INTEGRATION_SHA=822f84289f6f4267252907e36862e93f1c90eb9d` 與本場 2c 錨一致。

- Self-Review ①–⑧：49 S 有 S-id assertion、未發明 G3、D-1 對得上、DBC 未偷偷修 limit、電池 33 行／25 名／hollow 3／polarity 1 —— 與獨立實跑一致。
- ⑥「Diff Budget 內」本場**打折**：檔名側 ⊆ 准許清單＋D-1 L1 成立；**行數** `five_station_f3.py` 1162＞估 ≤200 作者未立 D-n。本場獨立記 F-s7b-2 🟡。
- Deviations：作者只立 **D-1 L1**。D-1 = **三支 CI 腳本**在准許清單外（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`）。guide 路徑 **已在** S-8.2，不是第四溢出。RR1／RR2 皆 CONCUR L1。本場 **CONCUR L1** 於這三支腳本。不升 L2、不重開 G2、不重開 F2 D-1。
- 作者未立、本場獨立加的 🟡：F-s7b-2 行數、F-s7b-3 fixture tracked 49＞12、F-s7b-4 5-tasks `approved` 未勾（作者 Files Changed 有寫 N1-arm，未開 D-n）、F-s7b-5 `docs/dev/devflow-contract.json` 仍 2.0.0。
- Decisions（新檔不改 F2 讀鍵／`next_when_five` 不改 `next` 字串／check stub／`frozen_slug` 不吃 fixture 路徑／HONEST 禁綠詞咬完整句）不構成 L2。
- RR1（#389）／RR2（#388）各 10／10 ACCEPTED。不是 self-ACCEPTED。本場抽查 T-4 理由字面、T-6 wording-only 紅、T-7 stdout `路線未宣告 仍舊 7`、T-8 六 M、T-10 25＋`--only` 3 —— 與 RR 列相符。**RR ≠ G3**。
- 不另存 `7-review-*.md`。
- Human G3 已由 `human:rick` @ 2026-09-14 Asia/Taipei（owner chat「G3過」）落檔；operator tony 經官方 write。不由作者／Writer B 代填。
