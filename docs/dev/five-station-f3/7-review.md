---
feature: five-station-f3
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: s7-writer-C
updated: 2026-09-14
---

# 7. 驗證 —— **不是 G3 PASS**（Writer C 獨立全稿；F3 cut + 電池）

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
> | 5 | **抽驗一列** | Human 抽驗加 **S-5.1**：`scripts/test-five-station-f3.sh:1-20`（單一入口 `exec`）、`scripts/five_station_f3.py:30-56`（OFFICIAL 25）、同檔 `:1133-1145`（`--only new5&#124;old7&#124;token` → exit 3）。twin 第五格＝Coverage 中位列 **S-5.2**（決定論 `rows[n//2]`，含回歸列 n=50 → S-5.2；`:30-56` 官方 25、`:417-421` 發明名 FATAL）。殘項 **S-2.4**：`:177-178`（缺 cut → `F3 cut 未發生`）、`:545-557`（PRE-210-NE-CUT 讀倉）。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡**。本檔是 **Writer C 獨立 PRE-REVIEW**，**不是** Human G3 PASS。全勾 ≠ PASS。機械綠 ≠ 代填 `verdict: PASS`。
> 基準:`origin/main` tip `#390`=`cc5faa9`（STATUS companion）；產品碼 `#385`=`7c2ef24`。Gold 4-spec／5-tasks／6-notes；獨立 RR1 `#389`／RR2 `#388` 各 10／10 ACCEPTED。**RR ≠ G3**。
> Scope = **F3 cut + 讀鍵 + 條件邊 + 路線閘 + doctor 清單 + 單一電池**。本 slug 自己仍舊 7（S-7.3）。不重開 F2 park。本 PR **只** 7-review 雙檔。不改 STATUS／HISTORY。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | Writer C／`s7-writer-C`（fresh-context Cloud Agent `bc-f43650fe-3769-4445-9f0f-345fd9341436`；**≠** Stage 6 實作 owner `implementer-A`／#385） |
| Stage 6 實作 | `implementer-A`；獨立 T-Review RR1（#389）／RR2（#388）各 10／10 ACCEPTED。**不是** G3 |
| Human G3 | **未簽**。本檔 `verdict: PRE-REVIEW`。Agent 禁代填 PASS／REQUEST_CHANGES／HOLD |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、49 S、DD-1…DD-10 Owner PASS） ②`5-tasks.md`（T-1…T-10；checkbox 全未勾） ③`scripts/test-five-station-f3.sh` + `five_station_f3.py` + fixtures ④`git diff 822f842..7c2ef24` ⑤親跑電池／hollow／spec-gate／F2／F1／tokens／file-map／doctor／graph → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-1／RR1／RR2 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 session runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 `main` tip `#390`=`cc5faa9`。本 PR **只** 7-review 雙檔。不改 STATUS／HISTORY。**不是 G3 PASS** |
| 可信／打折 | 機械數字（25 官方名／33 CASE 行／failed=0／hollow exit 3／spec-gate 9/9／F1 63／F2 18）以本場親跑為準。F-id 分級與「沒想到的事」打折：作者 Self-Review 不得當錨。RR1／RR2 是 T 審，不是出貨 |

建議路徑：適格人類 reviewer（owner rick）抽驗 S-5.1 三個 `檔:行` + Known Limits，經 `scripts/devflow_gate.py write` 才准改頂欄。走 owner 自審必須另寫限制聲明（本檔已有）。不開 sibling `7-review-*.md`。

## Coverage Matrix

自建（grep `#### S-` ↔ 電池 `[ok] S-`／官方 CASE／diff；**未先讀** Self-Review）。末列固定回歸。49 S。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `ATTEST-VISIBLE --slot ok`；`five_station_f3.py:444-456` 三槽＋`f3-cut` | ✅ |
| S-1.2 | 同 CASE `--slot missing`／`empty`；`:457-469` | ✅ |
| S-1.3 | `ATTEST-SILENT-RED`；`:498-508` 注入 `return True` 無三槽＝紅格 | ✅ |
| S-1.4 | `--slot readonly`；`:470-482` 位元組不變 | ✅ |
| S-1.5 | `--slot sibling-reject`；`:483-494` 活樹契約無 cut 兄弟鍵 | ✅ |
| S-1.6 | guide 已寫「五站」（交付物）；`f3_cut_happened` 仍只讀三槽；本 PR 不改 STATUS | ✅ |
| S-2.1 | `READ-SEAM --reader canonical-200`；`:528-532` 回 `2.0.0` | ✅ |
| S-2.2 | `READ-SEAM` 預設；`:515-527` F2 舊 reader 看不見 2.1＝紅格 | ✅ |
| S-2.3 | `--reader canonical-210`；`:533-541` declared 真、cut 獨立假 | ✅ |
| S-2.4 | `PRE-210-NE-CUT`；`:545-561` 理由含字面 `F3 cut 未發生` | ✅ |
| S-2.5 | `PRE-AND` 三缺；`:563-601` | ✅ |
| S-2.6 | `PRE-HOPS-200`；`:603-615` SLOT-REJECT；`nxt==N7-g1` | ✅ |
| S-2.7 | 同 CASE；`:613` 未宣告跳過側不生效 | ✅ |
| S-3.1 | `NEW5-CUT-OK`；`:617-639` s2=`N8-end` s4=`N7-end` | ✅ |
| S-3.2 | PRE-HOPS-200＋graph 已有 `next_when_five`；未宣告仍 `N7-g1` | ✅ |
| S-3.3 | `GRAPH-WORD-NE`；`:641-680` 用字＋恒停＝紅；cut AND 後真跳過 | ✅ |
| S-3.4 | 同 CASE；`N7-g1.md`／`N6-g2.md` 仍在；token 牙綠 | ✅ |
| S-3.5 | CUT-OK；`:633-636` 閘與兩邊 graph 同意 | ✅ |
| S-3.6 | diff：條件邊＋`five_station_f3.py` 閘；零節點刪檔 | ✅ |
| S-4.1 | `hooks/runtime-capabilities.json` 含 `2.1.0`；`_doctor_impl.py` diff＝0 | ✅ |
| S-4.2 | `DOCTOR-HONEST`；`:683-697` 印 `INCOMPATIBLE`、非 0 | ✅ |
| S-4.3 | `DOCTOR-NE-TICKET`；`:699-721` stdout 字面 `路線未宣告 仍舊 7` | ✅ |
| S-4.4 | `git diff --exit-code -- hooks/_doctor_impl.py` | ✅ |
| S-4.5 | `allow_legacy` 丟棄 marketplace／cache；PRE-HOPS-200 理由無 marketplace | ✅ |
| S-5.1 | 全入口 exit 0；`--only new5&#124;old7&#124;token` 各 exit 3（本場抽驗列） | ✅ |
| S-5.2 | `OFFICIAL` 25 名＝Decision 原 20＋standing 5；減列會 `FATAL` | ✅ |
| S-5.3 | 紅格皆「is the red cell」；legal refuse ≠ 該格綠；`--probe polarity` exit 1 | ✅ |
| S-5.4 | `HOLLOW-TRUE`；`:848-859` | ✅ |
| S-5.5 | `HOLLOW-FILES`；`:861-873` | ✅ |
| S-5.6 | `HOLLOW-F2`；`:875-884` | ✅ |
| S-5.7 | `F3-F2-REGRESS`；F2 `failed=0`（地板，不是 IFF） | ✅ |
| S-5.8 | `TOKEN-KEEP`；`check-gate-tokens.sh` exit 0 | ✅ |
| S-5.9 | `HOLLOW-WORD`；`:886-899` 獨立格 | ✅ |
| S-5.10 | `HOLLOW-TWO-SCRIPT`；`:901-910`；可選 check ≠ 第四路 | ✅ |
| S-5.11 | `HOLLOW-HTML-NE-GWT`；`:912-920` `has_old7` 假 | ✅ |
| S-6.1 | `NEW5-WAIT-RED`；`:723-742` 注入仍停 `N7-g1` | ✅ |
| S-6.2 | `KEEP-MK-RED`；`:744-770` `injected-mk M3 M5 M9 M11 M12 M15` | ✅ |
| S-6.3 | `KEEP-SHIP-MECH`；`:772-786` 注入機械 Done＝紅 | ✅ |
| S-7.1 | `OLD7-FREEZE`；`:788-798` 無五站機 | ✅ |
| S-7.2 | `OLD7-FOLD-RED`；`:800-812` 注入寫五站＝紅 | ✅ |
| S-7.3 | `SELF-OLD7`；`:814-821` 本目錄／F2／simplify 跳不過 | ✅ |
| S-7.4 | 同 CASE；`:822-828` NEW5＝合成 fixture | ✅ |
| S-7.5 | 5-tasks／6-notes／本檔無「活五站 slug＝&lt;name&gt;」已核句 | ✅ |
| S-8.1 | Stage 4 hop 歷史約束；4-spec 已 Human G2；本場不重開頂欄 | ✅ |
| S-8.2 | Files ⊆ 准許清單＋**D-1 L1** 四檔具名（見 KL #1） | ✅ |
| S-8.3 | token／in-flight／F2 park Diff Budget 0；`_templates/`＝0 | ✅ |
| S-8.4 | `TOKEN-DEL-RED`；`:835-846` 注入刪 token＝紅；真牙仍綠 | ✅ |
| S-8.5 | 4-spec Disposition Q15–Q27 有去向；Q21–Q23 非可選 | ✅ |
| S-8.6 | 不改 `docs/dev/five-station-f2/` 已封 R／S；不重開 park | ✅ |
| 既有測試套件(回歸) | `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`；`bash scripts/test-five-station-f2.sh`；`bash scripts/test-five-station-f1.sh`；`bash scripts/check-file-map.sh`；`bash scripts/check-gate-tokens.sh` | ✅ |

**回歸末行（reviewer @ `cc5faa9`）**：spec-gate `9/9` exit 0（49 S）；F3 `failed=0` CASE 行=33／unique=25；F2 `failed=0` CASE=18；F1 `failed=0` CASE=63；file-map `scanned=213` exit 0；tokens 全過；stage2／4／6 graph 綠；doctor 對根契約 `2.1.0`＝`COMPATIBLE`（約束，不是 hop 通行證）。預設不帶 `--contract` 的 doctor 讀 `docs/dev/devflow-contract.json` 仍 `2.0.0`（見 KL #5）。

## Verification Evidence

<!-- Final Fresh 在 ALREADY_SYNCED 之後重綁當下 main tip（步 2c 路徑①）。
     產品碼樹 = origin/main after #385／#390。本 PR 後續只加本雙檔，不改牙。 -->

- Source SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
- Final Fresh Run ID: f3-s7c-fresh-cc5faa9-20260914
- Entry point: `bash scripts/test-five-station-f3.sh`（Conditional 已落地 → 本場列入 Required）然後 `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件；twin 另裝 `markdown-it-py==4.0.0`）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`） | `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md` | pass | exit 0; 9/9; 49 S | |
| token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F3 電池列 Required | `bash scripts/check-gate-tokens.sh` | pass | exit 0; G1 2 token; G2 3 token; G3 4 token | |
| test-five-station-f3 | `bash scripts/test-five-station-f3.sh` | pass | failed=0; CASE lines=33; unique official=25; exit 0 | |
| hollow --only new5 | `bash scripts/test-five-station-f3.sh --only new5` | pass | exit 3; 印 hollow --only new5 | |
| hollow --only old7 | `bash scripts/test-five-station-f3.sh --only old7` | pass | exit 3; 印 hollow --only old7 | |
| hollow --only token | `bash scripts/test-five-station-f3.sh --only token` | pass | exit 3; 印 hollow --only token | |
| unknown --only f1 | `bash scripts/test-five-station-f3.sh --only f1` | pass | exit 2（用法；不得當 hollow 綠） | |
| unknown flag | `bash scripts/test-five-station-f3.sh --bogus` | pass | exit 2; 印 FATAL: 未知旗標 | |
| hollow --probe hollow-true | `bash scripts/test-five-station-f3.sh --probe hollow-true` | pass | exit 3 | |
| hollow --probe hollow-files | `bash scripts/test-five-station-f3.sh --probe hollow-files` | pass | exit 3 | |
| hollow --probe hollow-f2 | `bash scripts/test-five-station-f3.sh --probe hollow-f2` | pass | exit 3 | |
| hollow --probe hollow-word | `bash scripts/test-five-station-f3.sh --probe hollow-word` | pass | exit 3 | |
| hollow --probe two-script | `bash scripts/test-five-station-f3.sh --probe two-script` | pass | exit 3 | |
| polarity probe | `bash scripts/test-five-station-f3.sh --probe polarity` | pass | exit 1; 真評測（非法拒當紅格綠）；見 F-s7c-5 | |
| test-five-station-f2 | `bash scripts/test-five-station-f2.sh` | pass | failed=0; CASE=18; exit 0 | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | failed=0; CASE=63; exit 0 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=213; table_rows=223 | |
| doctor handshake (root 2.1.0) | `bash hooks/devflow-doctor.sh --contract /workspace/devflow-contract.json` | pass | COMPATIBLE; contract 2.1.0 ∈ supported | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| UI e2e（本刀無新前端） | | n-a | | Explicitly excluded；F3 無產品 UI |
| 負荷／效能（路線閘非熱路徑） | | n-a | | Explicitly excluded |
| 金流／auth fuzz（不涉） | | n-a | | Explicitly excluded |
| architecture-guards PF-0 | `bash scripts/test-architecture-guards.sh` | n-a | | ENV：本機無 Python 3.9–3.11 下限直譯器（PF-0 exit 2）。不是 F3 產品行為。file-map 213 已另列 pass |

八點機械面（G3 錨全文）見附錄 A5。指向 **單一電池 + hollow 三探針 + polarity exit 1**，不是「檔在」或「只 F2 綠」。**八點齊 ≠ 機械代填 Human G3**。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得 silent `True` 當 cut（S-1.3） | ATTEST-SILENT-RED 紅格 | pass |
| 不得契約兄弟布林當 SoT（S-1.5） | sibling-reject；活樹無 cut 鍵 | pass |
| 不得 fallback 錯鍵（S-2.1、S-2.2） | F3 `contract_version` 只讀正本；F2 舊 reader 紅格 | pass |
| 2.1.0 ≠ cut（S-2.4） | PRE-210-NE-CUT 理由 `F3 cut 未發生` | pass |
| 三前置缺一 → legacy（S-2.5） | PRE-AND 三棵 | pass |
| 不得 2.0.0＋五站 hops（S-2.6） | PRE-HOPS-200 SLOT-REJECT | pass |
| 不得只改用字當切（S-3.3、S-5.9） | GRAPH-WORD-NE／HOLLOW-WORD 各紅 | pass |
| 不得 doctor 綠當 hop 通行證（S-4.3） | DOCTOR-NE-TICKET 理由是路線 | pass |
| 紅格不得把拒 hop 當綠（S-5.3） | WAIT／MK／SHIP 注入紅；polarity exit 1 | pass |
| 不得只跑 NEW5 或只跑 F2（S-5.1、S-5.6） | `--only` exit 3；HOLLOW-F2 紅 | pass |
| 不得兩支腳本各綠當同一電池（S-5.10） | HOLLOW-TWO-SCRIPT 紅 | pass |
| 不得對本目錄建五站機（S-7.3） | SELF-OLD7 | pass |
| 不得本 hop 自填 G3 PASS（對照 S-8.1） | 本檔 `verdict: PRE-REVIEW` | pass |
| 不得刪 token／折 in-flight／重開 F2 park（S-8.3、S-8.6） | token 牙綠；F2 已封 R／S 未改 | pass |
| 不得鎖第一隻活五站名字（S-7.5） | 無已核活 slug 名 | pass |
| Out of Scope 後站不准改成 In | 5-tasks／6-notes 禁區仍 0 | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#385 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **s7-writer-C 2026-09-14 親跑** `bash scripts/test-five-station-f3.sh -v`（不採信 6-notes 貼文）。長輸出見附錄 A4。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 打開三槽檔＋`f3_cut_happened` | `[ok] S-1.1 who/when nonempty`／`which_condition=f3-cut`／`True` | ✅ |
| S-1.2 | 函式回傳 | `[ok] S-1.2 missing → False`／`empty → False` | ✅ |
| S-1.3 | ATTEST-SILENT-RED 格 | `[ok] S-1.3 silent True without slots is the red cell` | ✅ |
| S-1.4 | 呼叫前後位元組 | `[ok] S-1.4 bytes unchanged`／`missing stays missing` | ✅ |
| S-1.5 | 契約鍵集合 | `[ok] S-1.5 live contract has no cut sibling` | ✅ |
| S-1.6 | guide＋三槽＋本 PR 檔集 | guide 含「五站」；cut 仍讀 JSON；本 PR 不改 STATUS | ✅ |
| S-2.1 | 假契約檔回傳 | `[ok] S-2.1 reader returns 2.0.0` | ✅ |
| S-2.2 | 舊 reader vs 正本 | `[ok] S-2.2 old reader does not see 2.1`／紅格 | ✅ |
| S-2.3 | 正本 2.1.x | `[ok] S-2.3 declared true`／`cut still independently false` | ✅ |
| S-2.4 | 拒因字面 | `[ok] S-2.4 reason has F3 cut 未發生` | ✅ |
| S-2.5 | 三缺各一棵 | 三格 `[ok] S-2.5 legacy`＋對應理由 | ✅ |
| S-2.6 | SLOT-REJECT | `[ok] S-2.6 SLOT-REJECT`／`仍舊 7` | ✅ |
| S-2.7 | graph_next 未宣告 | `[ok] S-2.7 skip side inactive while undeclared` | ✅ |
| S-3.1 | hop 紀錄 | `hop-record route=five s2=N8-end s4=N7-end` | ✅ |
| S-3.2 | 未宣告採用端 | PRE-HOPS-200 `nxt==N7-g1`（條件邊已在檔上） | ✅ |
| S-3.3 | 注入用字＋恒停 | `[ok] S-3.3 wording-only inject graph_next stays N7-g1 is the red cell` | ✅ |
| S-3.4 | 節點檔 | `[ok] S-3.4 nodes kept`；本場 `test -f` 兩節點 | ✅ |
| S-3.5 | 閘＝邊 | `[ok] S-3.5 gate and stage2 agree`／stage4 | ✅ |
| S-3.6 | diff 檔名 | `graph.yaml` 加 `next_when_five`；無節點刪 | ✅ |
| S-4.1 | supported 清單 | `runtime-capabilities.json` 含 `2.1.0` | ✅ |
| S-4.2 | doctor stdout | `[ok] S-4.2 prints INCOMPATIBLE`／non-zero | ✅ |
| S-4.3 | 拒因 stdout | `路線未宣告 仍舊 7`（可 grep） | ✅ |
| S-4.4 | handshake diff | `_doctor_impl.py` 對 `822f842..HEAD` 空 | ✅ |
| S-4.5 | 閘輸入 | `allow_legacy` 丟棄 cache／marketplace | ✅ |
| S-5.1 | 入口 stdout／exit | 全入口 0；`--only` 3／3／3；未知 2 | ✅ |
| S-5.2 | CASE 名清單 | unique=25＝官方 25；無發明名 | ✅ |
| S-5.3 | 紅格極性 | 各格「is the red cell」；polarity exit 1 | ✅ |
| S-5.4 | HOLLOW-TRUE | `[ok] S-5.4 inject True-as-green is the red cell` | ✅ |
| S-5.5 | HOLLOW-FILES | `[ok] S-5.5 inject files-exist-as-green is the red cell` | ✅ |
| S-5.6 | HOLLOW-F2 | `[ok] S-5.6 inject F2-green-as-F3 is the red cell` | ✅ |
| S-5.7 | F2 地板 | `[ok] S-5.7 F2 battery still green (floor)` | ✅ |
| S-5.8 | token 牙 | `[ok] S-5.8 token teeth still green` | ✅ |
| S-5.9 | HOLLOW-WORD | `[ok] S-5.9 inject wording-as-green is the red cell` | ✅ |
| S-5.10 | HOLLOW-TWO-SCRIPT | `[ok] S-5.10 two scripts each green is the red cell` | ✅ |
| S-5.11 | html-only | `[ok] S-5.11 has_old7 false` | ✅ |
| S-6.1 | 注入等人 | `[ok] S-6.1 inject wait is the red cell` | ✅ |
| S-6.2 | 注入 MK 仍 hop | `injected-mk M3 M5 M9 M11 M12 M15` | ✅ |
| S-6.3 | 注入機械 Done | `[ok] S-6.3 inject mechanical Done is the red cell` | ✅ |
| S-7.1 | OLD7 1–7 | `[ok] S-7.1 no five-station machine` | ✅ |
| S-7.2 | 注入折線 | `[ok] S-7.2 inject five-station write on OLD7 is the red cell` | ✅ |
| S-7.3 | 活目錄 | `[ok] S-7.3 five-station-f3 cannot auto-advance`（另 f2／simplify） | ✅ |
| S-7.4 | NEW5 路徑 | `[ok] S-7.4 NEW5 is synthetic` | ✅ |
| S-7.5 | 全文搜尋 | 無「第一隻活五站＝&lt;slug&gt;」已核句 | ✅ |
| S-8.1 | 4-spec 頂欄 | 已 Human G2；本 PR 不改它 | ✅ |
| S-8.2 | Files 聯集 | 准許清單＋D-1 四檔具名 | ✅ |
| S-8.3 | 禁區 diff | token／handshake／F2 R／S／`_templates/`＝0 | ✅ |
| S-8.4 | TOKEN-DEL-RED | `[ok] S-8.4 inject token delete claim is the red cell` | ✅ |
| S-8.5 | Disposition | Q15–Q27 列在；Q21–23 有 S | ✅ |
| S-8.6 | F2 已封 | `docs/dev/five-station-f2/` 本刀未改 R／S | ✅ |

## 截圖槽

本場無產品 UI（F3 = CLI coordinator + fixture 自檢）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = 電池 CASE stdout
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F3 是 cut／路線閘／電池，不是現場交接 UI。有 Operational Context 的 S 以「owner 寫三槽／coordinator 被閘擋住或立刻 hop」走一遍；標不適用的純內部 S 不裝成人員旅程。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 母版 owner | 留下可指的 cut | 讀 `f3-cut-attestation.json` | 人寫三槽、git 提交 | 檔未寫＝未切 | 人指得到 who／when／`f3-cut` |
| S-1.2／S-1.4／S-1.5 | — | — | 讀端布林 | — | 缺槽＝False | 不適用（讀端） |
| S-1.3 | Ship 審查者 | 擋空切 | ATTEST-SILENT-RED | 不得把函式真當切 | 該格紅 | 空切被看見 |
| S-1.6 | 看板寫手 | 用語切五站 | guide 改字 | STATUS 只走 companion | 看板 ≠ 刀 | 本 PR 不改 STATUS |
| S-2.1…S-2.3 | — | — | 只讀正本鍵 | — | 錯鍵忽略 | 不適用（讀鍵） |
| S-2.4 | coordinator | 已宣告但未切 | `refuse_hop_reason` | 補三槽 | 理由 `F3 cut 未發生` | legacy |
| S-2.5 | coordinator | 三前置缺一 | PRE-AND | 補缺的那一條 | 各有理由 | legacy |
| S-2.6／S-2.7／S-3.2 | 未宣告採用端 | 不要被遠端改線 | graph_next | 先 bump 2.1.0 | 仍進 N7-g1 | SLOT-REJECT |
| S-3.1／S-3.5 | 新 slug 寫手 | cut 後立刻五站 | `--case NEW5-CUT-OK` | 不寫「要不要繼續」 | 無例行閘 | hop N8-end／N7-end |
| S-3.3 | 電池作者 | 只用字不得當切 | GRAPH-WORD-NE | 真跳過才算 | 注入恒停＝紅 | 極性對 |
| S-3.4／S-3.6 | — | — | 條件邊＋閘 | — | 節點不刪 | 不適用（機制形） |
| S-4.1／S-4.4 | — | — | supported 加 2.1.0 | — | 不改握手 | 不適用（清單） |
| S-4.2 | 採用端 | 漏加要誠實紅 | DOCTOR-HONEST | 加 supported | INCOMPATIBLE | 非 0 |
| S-4.3 | 採用端 | doctor 綠後想 hop | DOCTOR-NE-TICKET | 不把 COMPATIBLE 當切線 | 仍舊 7 | 理由是路線 |
| S-4.5 | — | — | 閘丟棄 cache | — | 不是第四前置 | 不適用 |
| S-5.1／S-5.3…S-5.11 | — | — | 單一入口 | — | hollow exit 3 | 不適用（完成定義） |
| S-6.1 | 寫手 | 謂詞真仍等人 | WAIT-RED 注入 | 刪等人句 | 停 N7-g1 | 該格紅 |
| S-6.2 | T reviewer | MK 紅不准 hop | KEEP-MK 注入 | 補四欄 | 注入仍 hop＝紅 | M3…M15 具名 |
| S-6.3 | owner | Ship 唯人 | SHIP-MECH 注入 | 人寫 PASS | 自動 Done＝紅 | HumanWait 才合法 |
| S-7.1／S-7.2 | 舊 slug owner | 已飛的保持舊 7 | OLD7 | 不折成五站 | 注入寫五站＝紅 | 凍結 |
| S-7.3 | 本 slug owner | 本目錄不是白老鼠 | SELF-OLD7 | 不拿本目錄當 NEW5 | 跳不過 | `仍舊 7 in-flight` |
| S-7.4／S-7.5 | Stage 5／6 寫手 | 不發明活五站名 | 合成 fixture | cut 之後才開的新 slug | — | 無名已核 |
| S-8.1…S-8.6 | — | — | Files／hollow | F2 park 另封 | 後站不准改成 In | 不適用（鎖） |

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec ②③⑧⑨⑩）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中。F3 讀 doctor／契約當證據，Files 不含 `hooks/_doctor_impl.py`；#385 未改握手語意。
2. **資料所有權被繞過寫入**:未命中。cut owner＝寫三槽的人類；`f3_cut_happened` 只讀。OLD7／本目錄不建五站機（S-7.1／S-7.3）。
3. **相容性破壞包成新增**:未命中。根契約 bump `2.1.0` 是宣告的 Compatibility 路徑；`agent-event` 未 bump。adopter 複本 `docs/dev/devflow-contract.json` 仍 `2.0.0`＝Known Limit #5，不是把 2.0.0 假裝成已宣告。
4. **一致性邊界被拆解**:未命中。三前置同一 `allow_legacy`／`graph_next`（S-3.5）。
5. **宣告的 Test seam 未被使用**:未命中。seam＝`f3_cut_happened`／`contract_version`／`evaluate_hop`／`--case`／`--only`／`--probe`；電池走同一入口。`--probe polarity` 是 fail-closed 探針，不是把 CASE 綠假裝驗過（F-s7c-5）。
6. **Known design limit 被實作悄悄「解決」**:未命中。doctor 綠陷阱仍在現場（約束）；本目錄仍舊 7。D-1 是 CI 註冊，不是把 F2 park「修掉」。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更。

- F-s7c-1 🟡 D-1 四檔在 5-tasks S-8.2 准許清單正文之外（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`／`guides/guide-dev-flow.html` `#filemap` 三列） | 4-spec L838 寫「超出 → L2」；作者已立 D-1 L1 | 本場獨立再評：**仍 L1**（host CI 註冊，不是第二次 cut／不是刪 token）。建議 Human park。見 Known Limits #1
- F-s7c-2 🟡 `scripts/five_station_f3.py` `wc -l` = 1162 > Diff Budget coordinator ≤200 | 行數超估（讀端＋閘＋Battery 同檔） | 對齊 F2 F-c-4。單一家族、不拆第二檔（會撞 Files 格）。作者未立 D-n。本場立 🟡。建議 Human park。見 KL #2
- F-s7c-3 🟡 fixture 超 Stage 4「≤12」估計 | 估計超支 | **tracked＝49**（方法：`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3`）。作者未立 D-n。本場立 🟡。不動 R/S。見 KL #3
- F-s7c-4 🟡 `5-tasks.md` `status: approved` 而 checkbox 全未勾 | 看起來像任務已核 | N1-arm／graph P0 only（`check-devstage6-graph`），不是勾 T、不是 G3。作者 Files Changed 有記。見 KL #4
- F-s7c-5 🟢 `five_station_f3.py:282-305`／`:1118-1127` `--probe polarity` | 健康樹上 `legal is None` → `polarity_inverted` 恒真；兩分支都印 FAIL、恒 exit 1 | 契約是「真評測、不是 stub」；CASE 格已獨立證極性。不升 🟡
- F-s7c-6 🟢 `docs/dev/devflow-contract.json` 仍 `2.0.0`；根檔已 `2.1.0` | 預設 doctor 讀 adopter 複本 | Files 准的是根 `devflow-contract.json`。不是把 2.0.0 當已宣告。見 KL #5
- F-s7c-7 🟢 `--group graph-edges` 重印 `NEW5-CUT-OK`＋`PRE-HOPS-200`（官方名，不發明 `GRAPH-AGREE`） | 第 3 格再印一次 CUT-OK | 殘項；不升 🟡
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。D-1 是 host CI 地板，不是新公開 API

## Spec Axis

逐 R。Deviations：D-1 如實。作者未立 D-2／D-3／行數 D-n —— 本場補記為 L1 🟡，**不**自升 L2。無隱藏 L2。本 slug 明確仍舊 7。

| R | 判定 | 證據 |
|---|---|---|
| R-1 | **符合** | S-1.1…S-1.6；三槽檔在；silent True 紅；函式只讀 |
| R-2 | **符合** | S-2.1…S-2.7；F3 reader 只讀正本；F2 舊 reader 留作 READ-SEAM；2.1.0 ≠ cut |
| R-3 | **符合** | S-3.1…S-3.6；`next_when_five`；閘同意；節點不刪 |
| R-4 | **符合** | S-4.1…S-4.5；supported 加 2.1.0；握手 0 diff；綠≠票 |
| R-5 | **符合** | S-5.1…S-5.11；25 名；hollow exit 3；F2 地板 |
| R-6 | **符合** | S-6.1…S-6.3；WAIT／MK／SHIP 各紅；MK 具名六個 M |
| R-7 | **符合** | S-7.1…S-7.5；OLD7 凍結；本目錄跳不過；無活五站已核名 |
| R-8 | **符合（刀）＋D-1 待 Human park** | S-8.1…S-8.6。D-1 四檔是明文 L1，不是 silent extras。Human G3 **未簽** |
| D-1(L1) | 如實；本場 CONCUR L1 | 四檔具名。4-spec「超出→L2」字母讀留檔。待 Human park |
| 行數／fixture／N1-arm | 作者未立 D-n；本場補 🟡 | F-s7c-2／F-s7c-3／F-s7c-4。不動 R/S |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit |

## 變更架構圖

必須對上 #385 basename（本 PR 只加 `7-review.md`／`7-review.html`）。

```text
[test-five-station-f3.sh] ----exec----> [five_station_f3.py]
                                         +-- f3_cut_happened / store
                                         |     docs/dev/f3-cut-attestation.json
                                         +-- contract_version (canonical key only)
                                         +-- allow_legacy / refuse_hop_reason
                                         +-- graph_next (next_when_five)
                                         +-- evaluate_hop / inject polarity
                                         +-- Battery official 25 CASE
[five_station_f2.py]  --old reader--     READ-SEAM (version/contract_version)
stage2/graph.yaml  next=N7-g1  next_when_five=N8-end
stage4/graph.yaml  next=N6-g2  next_when_five=N7-end
hooks/runtime-capabilities.json  +2.1.0
devflow-contract.json (repo root)  2.1.0
docs/dev/devflow-contract.json     2.0.0  (adopter copy; KL #5)
D-1 floor (not 5-tasks Files union):
  check-file-map.sh        EXPECTED=213
  devflow-check.sh         architecture/test-five-station-f3
  test-architecture-guards.sh  靜態釘 213
  guide-dev-flow.html      檔案地圖三列（非第二次 cut）
FROZEN (still old 7):
  docs/dev/five-station-f3 | five-station-f2 | five-station-simplify
NOT in this knife:
  _templates / _doctor_impl.py handshake / token delete / F2 park reopen
  Human G3 / this-slug-as-NEW5
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

審核的產品碼 = `822f842..7c2ef24`（#385 實作＋standing rework）。`cc5faa9`＝#390 STATUS companion（本 Stage 7 PR **不**改 STATUS）。本 Stage 7 PR 只新增本雙檔。共同戰場已是送審樹本身（見 2c）。

<details>
<summary title="+1162/-0; cut + gate + battery"><code>scripts/five_station_f3.py</code> (+1162/-0)</summary>
<pre><span class="add">+OFFICIAL = 25 CASE 名</span>
<span class="add">+def f3_cut_happened(...)  # three-slot read-only</span>
<span class="add">+def contract_version(...)  # canonical key only</span>
<span class="add">+def allow_legacy / refuse_hop_reason  # 三前置 AND</span>
<span class="add">+def evaluate_hop(...)  # inject polarity</span>
<span class="add">+class Battery  # 25 CASE + hollow --only exit 3</span></pre>
</details>

<details>
<summary title="+20/-0; 入口"><code>scripts/test-five-station-f3.sh</code> (+20/-0)</summary>
<pre><span class="add">+exec python3 five_station_f3.py --root "$ROOT" "$@"</span></pre>
</details>

<details>
<summary title="+7/-0; 非第四路"><code>scripts/check-five-station-f3.sh</code> (+7/-0)</summary>
<pre><span class="add">+echo "…independent check, not the F3 battery entry"</span>
<span class="add">+exit 0</span></pre>
</details>

<details>
<summary title="cut SoT"><code>docs/dev/f3-cut-attestation.json</code></summary>
<pre><span class="add">+who=rick when=2026-09-14T00:00:00+08:00 which_condition=f3-cut</span></pre>
</details>

<details>
<summary title="2.1.0 宣告"><code>devflow-contract.json</code> · <code>hooks/runtime-capabilities.json</code></summary>
<pre><span class="del">-devflow_contract_version 2.0.0</span>
<span class="add">+devflow_contract_version 2.1.0</span>
<span class="add">+supported += 2.1.0</span></pre>
</details>

<details>
<summary title="條件邊"><code>skills/dev-flow/stage2/graph.yaml</code> · <code>skills/dev-flow/stage4/graph.yaml</code></summary>
<pre><span class="add">+next_when_five: N8-end  # stage2 S6-selfcheck; default next still N7-g1</span>
<span class="add">+next_when_five: N7-end  # stage4 S5-gate; default next still N6-g2</span></pre>
</details>

<details>
<summary title="fixtures 目錄"><code>scripts/fixtures/five-station-f3/*</code>（tracked 49 via git ls-tree；F-s7c-3）</summary>
<pre>方法：git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3 → 49
new5/: attest-visible、cut-ok、pre-*、read-seam、doctor-*、inject-*、html-only
old7/: 1–7 .md + inject-fold-red
完整 diff 在 #385。</pre>
</details>

<details>
<summary title="D-1 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code> · <code>guides/guide-dev-flow.html</code></summary>
<pre><span class="del">-EXPECTED_MAPPED_FILES = 210</span>
<span class="add">+EXPECTED_MAPPED_FILES = 213</span>
<span class="add">+architecture 組註冊 test-five-station-f3.sh / check-five-station-f3.sh</span>
<span class="add">+guide 檔案地圖三列（非第二次 cut）</span></pre>
</details>

<details>
<summary title="過程檔"><code>docs/dev/five-station-f3/6-implementation-notes.md</code> · html twin · 5-tasks</summary>
<pre>6-notes + RR1／RR2 10／10 ACCEPTED。5-tasks D-3 形 frontmatter approved。STATUS／HISTORY 是 #390 companion，不在本 PR。</pre>
</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** Writer C 獨立全稿。機械門檻本場親跑為綠；Human 未簽。全勾 ≠ PASS。RR1／RR2 10／10 **不是** G3。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 49 S 全綠 | Coverage 49 列 ✅；25 官方名；33 CASE 行 failed=0 | reviewer 實跑；**Human G3 未簽** |
| 既有回歸綠 | spec-gate 9/9；F2 CASE=18；F1 CASE=63；file-map 213；tokens | reviewer 實跑；**Human G3 未簽** |
| 現象證據逐 S | 上表＋附錄 A4 | reviewer 親跑電池；**Human G3 未簽** |
| Evidence 契約 | 本節四欄＋層表；gauntlet 見附錄 A5 | 機械面交給本檔；**Human G3 未簽** |
| 無 🔴 | 無產品行為 🔴；F-s7c-1…4 皆 🟡 | **待 Human 接受／park D-1／行數／fixture／N1-arm** |
| F3 範圍 | cut 已寫三槽＋根契約 2.1.0＋條件邊；**本目錄仍舊 7** | 不得當「本 slug 已切五站」 |
| Human G3 | **未簽** | 本檔停 PRE-REVIEW |

- G3 | 2026-09-14 | **未發明**。本 hop = Writer C PRE-REVIEW。建議路徑：human:rick 抽驗 S-5.1 + park KL #1–#4 後，才准 `scripts/devflow_gate.py write`。Source SHA 維持 `cc5faa9f2c3c02709758b9805ba52bc984dcadf7`。STATUS 不在本 PR。

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 `FORK_INTEGRATION_SHA=822f84289f6f4267252907e36862e93f1c90eb9d`。本工作樹開工 = 已合入的 `origin/main`。

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: 822f84289f6f4267252907e36862e93f1c90eb9d
FEATURE_HEAD: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=ALREADY_SYNCED FORK=822f84289f6f4267252907e36862e93f1c90eb9d HEAD=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 INTEGRATION=cc5faa9f2c3c02709758b9805ba52bc984dcadf7(refs/remotes/origin/main)—— 你已經同步過了,本次輸出不算數
```

路徑①：**重綁 Final Fresh** 到當下 HEAD = `cc5faa9`（本檔 Source SHA）。共同戰場 = #385／#390 本身，已當審核對象逐檔看過，不得用此次腳本輸出當「沒有共同戰場」。本 hop **不改產品碼**。產品碼已在 main；本 PR 只文件。

本 review hop 另跑 `--fork-sha cc5faa9`（= 開工 HEAD = `origin/main` tip）：

```
STATUS: N_A_NO_INCOMING
FORK_INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
FEATURE_HEAD: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=N_A_NO_INCOMING …—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

該輸出只記本審查 hop 座標，不取代上面 Stage 6 錨的 `ALREADY_SYNCED`，也不當「無共同戰場」。**不 merge 產品碼。**

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | D-1(L1)：host CI 四檔不在 5-tasks S-8.2 准許清單正文。`EXPECTED_MAPPED_FILES` 210→213；`devflow-check.sh` 註冊 F3 電池；architecture 釘；guide **檔案地圖三列**（非第二次 cut）。4-spec L838「超出 → L2」與作者 D-1 留檔 | L1／🟡 | **待 Human 接受／park**。落點=本表。owner=rick。不在本 PR 縮四檔、不重開 G2 |
| 2 | F-s7c-2(L1)：`five_station_f3.py` 1162 行 > Diff Budget coordinator ≤200。作者未立 D-n | L1／🟡 | **待 Human 接受／park**。不拆第二家族。owner=rick。落點=本表 |
| 3 | F-s7c-3(L1)：Stage 4 fixture 估 ≤12 檔；**tracked＝49**（`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3`）。作者未立 D-n | L1／🟡 | **待 Human 接受／park**。不動 R/S。owner=rick。落點=本表 |
| 4 | F-s7c-4(L1)：`5-tasks.md` frontmatter `draft`→`approved`（N1-arm／graph P0）。checkbox 未勾、不是 T ACCEPTED、不是 G3 | L1／🟡 | **待 Human 接受／park**。owner=rick。落點=本表 |
| 5 | 根契約 `2.1.0`；`docs/dev/devflow-contract.json` 仍 `2.0.0`。預設 doctor 讀 adopter 複本 → 印 2.0.0 ∈ supported。F3 reader 對專案根回 2.1.0 | 範圍／誠實 | 維持。Files 准的是根檔。不得把預設 doctor 2.0.0 說成「未 bump」或「已宣告採用端」 |
| 6 | 本目錄／F2／simplify 仍舊 7（S-7.3）。cut 真 ≠ 本 slug 自動前進 | 範圍 | **F3 範圍誠實**：已切的是「之後才開、無 1–7 `.md` 的新 slug」。本目錄是白老鼠禁區 |
| 7 | doctor 綠陷阱仍在採用現場（4-spec Known design limit）。F3 只加清單＋行為牙，不修 `_doctor_impl.py` | 已知 | 維持約束 |
| 8 | 步 2c：Stage 6 錨 `ALREADY_SYNCED`；本 review hop 另記 `N_A_NO_INCOMING`（fork＝`cc5faa9`）。兩輸出皆不作「無共同戰場」證據 | 流程 | 已走路徑① 重綁 Fresh 到 `cc5faa9`。不 merge |
| 9 | 本檔 `verdict: PRE-REVIEW`。全勾 ≠ PASS。Human 未簽 | 流程 | 建議路徑見限制聲明。不得發明 G3 |
| 10 | `--probe polarity` 恒 exit 1（F-s7c-5）。architecture-guards PF-0 本機缺 3.9–3.11＝ENV | 殘項／ENV | 極性以 CASE 格為準。PF-0 不列入 F3 產品紅 |

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**:無未授權 Boundary 變更（DIC 六項未命中）。D-1 是 Files／CI 註冊 L1，**不是** Boundary 變更；**Human 尚未 park**（本表 #1）。未勾
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:本刀 bump 根契約 `2.1.0`＋切條件邊，Human 可裁為不可逆。本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:ALREADY_SYNCED 三 SHA＋canonical ref 貼於 Verdict；Fresh 重綁 `cc5faa9`。本 review hop 另記 `N_A_NO_INCOMING`（fork＝`cc5faa9`）。Verdict 後禁改產品碼
- [ ] PR → main:本 hop 開 Stage 7 PR；**禁直上 master**。Human G3 未簽；合入由 merger 做
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（F3 不改 living 契約句；方法論仍在 4-spec／guide）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**
- [ ] 7-review frontmatter status: shipped:本 hop `status: draft` + `verdict: PRE-REVIEW`（G3 未過）
- [x] 7-review.html 已產生:先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py /workspace five-station-f3 7-review`（twin 覆寫同檔；無 shots 時 twin 較完整；抽驗格＝中位列 S-5.2；Human 加抽 S-5.1；殘項 S-2.4）
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| Human G3 後 | rick | 本檔 Coverage／KL #1–#4；`test-five-station-f3.sh` 仍 failed=0 且 `--only` exit 3 | 電池變紅、hollow 不再是 3、或有人把本 slug 當第一隻活五站 |
| 下一隻新 slug 開工前 | rick | S-3.1／S-7.3／KL #6；條件邊仍在、本目錄仍舊 7 | 未宣告採用端被改線，或本目錄被折成五站 |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本 hop **停 PRE-REVIEW**。RR1／RR2 10／10 是 T 審。
2. **D-1 准許清單張力**：四檔是 CI 註冊。本場 CONCUR L1。R8「超出→L2」字母讀留檔。待 Human park。
3. **Scope 誠實**：F3 **已切**（三槽＋根 2.1.0＋`next_when_five`＋NEW5 預設五站）。**本目錄仍舊 7**。把「five-station-f3 自己已走五站」當成已交付 = 錯。出貨證據＝**單一電池 + hollow 三探針**，不是檔在、不是只 F2 綠。
4. **2c**：Stage 6 錨 `ALREADY_SYNCED`。本 review hop 另記 `N_A_NO_INCOMING`。不重 merge。Fresh 綁 `cc5faa9`。
5. **作者 vs 本場**：Self-Review ①–⑧ 主張電池綠＋RR1／RR2 10／10＋未發明 G3 —— 與本場實跑一致。作者未立行數／fixture D-n —— 本場補 F-s7c-2／F-s7c-3，不升 L2。
6. **adopter 契約複本**：根 2.1.0／`docs/dev` 2.0.0 並存。預設 doctor 印 2.0.0 不是「未 bump」，也不是「採用端已宣告」。

### A2　本場不宣稱的事

Human G3 PASS。本 slug 已切五站。living spec 改寫。STATUS shipped（#390 只推到 6-implementation-notes、G3⬜）。5-tasks checkbox 勾選（仍未勾，正確）。F2 park 重開。發明第一隻活五站名字。

### A3　Human 路徑（尚未走）

1. 開 Pages／本機審頁（路徑見 PR）。
2. 抽驗 **S-5.1** 三個 `檔:行`（入口／`:30-56` OFFICIAL 25／`:1133-1145` `--only` exit 3）。殘項 S-2.4（`:177-178`／`:545-557`）。
3. Known Limits #1（D-1）／#2（行數）／#3（fixture）／#4（N1-arm）：接受或打回。
4. 判定未落：不得由 Writer C 代填 PASS。
5. 頂欄只准官方 write 路徑寫入。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
cc5faa9f2c3c02709758b9805ba52bc984dcadf7

$ bash scripts/test-five-station-f3.sh
… 33 × === CASE … [ok] …
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

$ bash scripts/test-five-station-f3.sh --group hollow -v | grep -c '^=== CASE'
6
$ bash scripts/test-five-station-f3.sh --group doctor -v | grep -c '^=== CASE'
2
$ bash scripts/test-five-station-f3.sh --group graph-edges -v | grep -c '^=== CASE'
3

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

$ bash hooks/devflow-doctor.sh --contract /workspace/devflow-contract.json
✅ devflow doctor: COMPATIBLE
contract-version: 2.1.0 ∈ supported
exit 0

$ python3 -c "import five_station_f3 as f3; print(f3.contract_version('.'), f3.f3_cut_happened('.'), f3.refuse_hop_reason('.', 'docs/dev/five-station-f3'))"
2.1.0 True 仍舊 7 in-flight
```

官方 25 名（`OFFICIAL` 元組）：NEW5-CUT-OK、NEW5-WAIT-RED、OLD7-FREEZE、OLD7-FOLD-RED、TOKEN-KEEP、TOKEN-DEL-RED、ATTEST-VISIBLE、ATTEST-SILENT-RED、PRE-210-NE-CUT、PRE-AND、PRE-HOPS-200、READ-SEAM、DOCTOR-HONEST、DOCTOR-NE-TICKET、GRAPH-WORD-NE、SELF-OLD7、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、KEEP-MK-RED、KEEP-SHIP-MECH、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT、F3-F2-REGRESS。無 `GRAPH-AGREE`／`NEW5-MKTG-*`／`DOC-OK`。

### A5　Evidence 八點 + Gauntlet

G3 錨八點（正本 `guides/guide-dev-flow.html#gates`）本場對照 —— **單一電池 + hollow ≠ 檔在／只 F2**：

1. Final Fresh 綁 Source SHA＝送審產品 HEAD：`cc5faa9f2c3c02709758b9805ba52bc984dcadf7`。本 PR 只文件，不改產品碼。docs commit 會再漂 SHA，不重綁、不發明第二次 Fresh。
2. Required Layer = pass：spec-gate 9/9；token 全過。電池已落地 → 本場把 `test-five-station-f3` 當加嚴 Required 且 pass。
3. 已觸發 Conditional = pass：F3 電池＋hollow 三探針；F2／F1 回歸。
4. 不得存在任何 fail：Verification Evidence 層表無 fail。
5. Required 不得 unverified／n-a：電池／spec-gate／token 皆 pass。
6. Explicitly Excluded 可 n-a＋理由：UI e2e／負荷／金流已附理由。
7. Optional 可 unverified＋誠實：architecture PF-0 以 ENV n-a 記，不假裝 pass。
8. Gauntlet PASS 不取代雙軸／Walkthrough／矩陣／現象：見本檔三大節。Human G3 **未簽**。

Writer C 於產品樹 `cc5faa9`（本雙檔 commit 前）親跑：

```
$ bash docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/five-station-f3/7-review.md \
    --source-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7 \
    --review-file \
    --require-layer spec-gate（全名） --require-layer token 檢查（全名）
✅ evidence gauntlet: 116 checks passed
exit 0

$ …同上再加 --require-layer test-five-station-f3 --require-layer test-five-station-f2
✅ evidence gauntlet: 118 checks passed
exit 0
```

docs commit 後 `--review-file` 強制當下 HEAD → E2 宣告 `cc5faa9` ≠ HEAD 為預期漂移，**不重綁、不發明第二次 Fresh**。`--source-sha` 仍綁產品樹 `cc5faa9`。Required 兩層用 4-spec 解析出的**全名**（全形括號，不是 substring）。加嚴只加、不拿掉 Required。

`7-review.html`：先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py`（twin 覆寫同檔；無 shots 時 twin 較完整）。Pages 掛 twin。

### A6　作者對照（N4；矩陣之後才讀）

- Self-Review ①–⑧：49 S 有 S-id assertion、未發明 G3、D-1 對得上、DBC 未偷偷修 limit —— 與獨立實跑一致。
- RR1／RR2：各 10／10 ACCEPTED（#389／#388）。不是 self-ACCEPTED。本場抽查 T-6 wording-only 紅、T-7 stdout `路線未宣告 仍舊 7`、T-8 `injected-mk` 六個 M —— 與 RR 列相符。
- 差異：作者只立 D-1。本場另記 F-s7c-2（1162＞200）／F-s7c-3（fixture 49）／F-s7c-4（N1-arm）／F-s7c-5（polarity 恒 1）／F-s7c-6（adopter 契約複本）。不升 L2。
- Decisions（F3 不改 F2 reader／`next_when_five` 鍵／frozen 不咬 fixture 路徑）不構成 L2。
- 不另存 `7-review-*.md`。
- Human G3 另由 rick 落檔，不由作者／Writer C 代填。
