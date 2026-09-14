---
feature: five-station-f3
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: writer-A
reviewers: []
updated: 2026-09-14
---

# 7. 驗證 —— **不是 G3 PASS**（F3 knife only）

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
> | 5 | **抽驗一列** | Human 抽驗加 **S-5.1**：`scripts/test-five-station-f3.sh:1-20`（單一入口）、`scripts/five_station_f3.py:30-56`（OFFICIAL 25）、同檔 `:1134-1145`（`--only new5&#124;old7&#124;token` → exit 3）。twin 第五格＝Coverage 中位列 **S-5.2**（決定論 `rows[n//2]`；本場 twin 實得）。殘項 **S-2.4**：`:548-556`（`declared` 真、cut 假 → `allow_legacy`）、`:177-178`（理由字面 `F3 cut 未發生`）、`scripts/fixtures/five-station-f3/new5/pre-210-ne-cut/devflow-contract.json:1-3`（正本鍵 `2.1.0`、無三槽）。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 用途:**G3 出貨關卡**。本檔是 **Writer A 獨立全文**，`verdict: PRE-REVIEW`、`status: draft`。**不是 Human G3 PASS**。author ≠ human。全勾 ≠ PASS。機械全綠 ≠ 人簽。
> 產品碼已在 `main` tip `#385`=`7c2ef24` + STATUS companion `#390`=`cc5faa9`。本 PR **只** 7-review 雙檔。不改 STATUS／HISTORY。不發明 Human G3。不重開 F2 park D-1／D-2／D-3／F-c-4。不刪 token。Scope = **F3 cut only**。
> Source SHA 綁 **真實 main tip** `cc5faa9f2c3c02709758b9805ba52bc984dcadf7`（本 hop 親跑樹）。docs commit 會再漂 SHA，不重綁、不發明第二次 Fresh。

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| 審查者 | Writer A／`s7-fresh-reviewer-A`（fresh-context Cloud Agent `bc-37087c5e-d7ad-424a-933f-dbf8fcdd9acd`；**≠** Stage 6 實作 owner `implementer-A`／#385；**≠** 人類 owner `rick`） |
| Stage 6 實作 | `implementer-A`；獨立 T-Review RR1（#389）／RR2（#388）各 10／10 ACCEPTED。**不是** G3 |
| Human G3 | **未簽**。本檔禁寫 `verdict: PASS`。`reviewers: []`。頂欄只准 `PRE-REVIEW`／`draft`，直到人類親填 |
| 讀取順序（可查） | ①`4-spec.md`（G2 PASS、49 S、DD-1…DD-10 Owner PASS） ②`5-tasks.md`（T-1…T-10、官方 25 CASE、S-8.2 准許清單） ③`scripts/test-five-station-f3.sh` + `five_station_f3.py` + fixtures ④`git diff 822f842..7c2ef24`（產品）／`822f842..cc5faa9`（含 STATUS companion） ⑤親跑電池／hollow／polarity／F2 地板／spec-gate／F1／tokens／file-map／doctor → **之後才** ⑥讀 `6-implementation-notes.md` Self-Review／D-1／RR1／RR2 |
| 圍欄 | 本雲端未武裝 `devflow-exec.sh review`（無 session runtime）。讀取順序靠散文紀律：矩陣與實跑先於 Self-Review |
| 本輪性質 | 產品碼已在 `main` tip `#385`+`#390`=`cc5faa9`。本 PR **只** 7-review 雙檔。不改 STATUS／HISTORY。**不是 G3 PASS**。建議路徑：適格人類 reviewer → 開審頁 → 抽驗 S-5.1 三個 `檔:行` → 對 Known Limits #1（D-1）明示接受／park 或打回 |
| 可信／打折 | 機械數字（25 CASE／`=== CASE` 印 33／failed=0／hollow exit 3／polarity exit 1／spec-gate 9/9／F2 18／F1 63）以本場 PRE-REVIEW 親跑為準。F-id 分級與「沒想到的事」打折：author ≠ human，本場不得代填 park。D-1 🟡 **未 park** |

建議路徑：人類打開本檔／twin → 抽驗 S-5.1 → 裁決 D-1（及本場另列的 Diff Budget 🟡）→ 經官方 `scripts/devflow_gate.py write` 落頂欄。Writer A 不代填。

## Coverage Matrix

自建（grep `S-`／`=== CASE`／`OFFICIAL` ↔ 4-spec 49 S；**未先讀** Self-Review）。末列固定回歸。官方 CASE 名只准 25，減一列＝翻 Decision。預設入口印 `=== CASE` ×33＝切片重複（ATTEST-VISIBLE×5／READ-SEAM×3／PRE-AND×3），**unique＝25**。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `ATTEST-VISIBLE --slot ok`；`five_station_f3.py:446-456` 三槽＋`f3_cut_happened` True | ✅ |
| S-1.2 | 同 CASE `--slot missing`／`empty`；`:458-468` 缺檔／空槽 → False | ✅ |
| S-1.3 | `ATTEST-SILENT-RED`；注入 `return True` 無合格三槽＝該格紅 | ✅ |
| S-1.4 | `--slot readonly`；`:470-478` 位元組不變 | ✅ |
| S-1.5 | `--slot sibling-reject`；cut 不得鎖契約兄弟鍵 | ✅ |
| S-1.6 | GRAPH-WORD-NE＋活樹 guide 五站用語；SoT 仍是三槽檔，不是 blame／STATUS | ✅ |
| S-2.1 | `READ-SEAM --reader canonical-200`；`contract_version` 只讀正本鍵 → `2.0.0` | ✅ |
| S-2.2 | `READ-SEAM` 預設；只 bump 正本、舊 reader 仍舊＝該格紅 | ✅ |
| S-2.3 | `--reader canonical-210`；回傳以 `2.1` 開頭；cut 仍獨立假 | ✅ |
| S-2.4 | `PRE-210-NE-CUT`；`allow_legacy`；理由含 `F3 cut 未發生`（本場殘項抽驗） | ✅ |
| S-2.5 | `PRE-AND` 三缺；缺一 → legacy | ✅ |
| S-2.6 | `PRE-HOPS-200`；`SLOT-REJECT`；路線仍舊 7 | ✅ |
| S-2.7 | 同 CASE；未宣告時 `next_when_five` 跳過側不生效 | ✅ |
| S-3.1 | `NEW5-CUT-OK`；s2=`N8-end` s4=`N7-end`；無例行停 | ✅ |
| S-3.2 | `PRE-HOPS-200`＋`--group graph-edges`；未宣告仍舊 7 | ✅ |
| S-3.3 | `GRAPH-WORD-NE`；只用字、`graph_next` 仍 `N7-g1`＝該格紅 | ✅ |
| S-3.4 | 同 CASE；`test -f` `N7-g1.md`／`N6-g2.md`；token 牙仍綠 | ✅ |
| S-3.5 | `NEW5-CUT-OK`；閘與 stage2／stage4 同意 | ✅ |
| S-3.6 | `graph.yaml` `next_when_five`＋`graph_next`；不是刪節點、不是只翻函式 | ✅ |
| S-4.1 | 活樹 `hooks/runtime-capabilities.json` 含 `2.1.0`；`_doctor_impl.py` diff＝0 | ✅ |
| S-4.2 | `DOCTOR-HONEST`；印 `INCOMPATIBLE`、非 exit 0 | ✅ |
| S-4.3 | `DOCTOR-NE-TICKET`；拒因是路線，不含「doctor 已綠所以可 hop」 | ✅ |
| S-4.4 | `git diff --exit-code -- hooks/_doctor_impl.py`（`822f842..cc5faa9`＝0） | ✅ |
| S-4.5 | `allow_legacy(..., marketplace_updated, cache_has_hops)` 忽略第四條 | ✅ |
| S-5.1 | 單一入口 `test-five-station-f3.sh`；缺 `--only` 一路即 exit 3 | ✅ |
| S-5.2 | unique CASE 名＝官方 25；無 `GRAPH-AGREE`／`NEW5-MKTG`／`DOC-OK`（本場 twin 中位列） | ✅ |
| S-5.3 | WAIT／KEEP-MK／SHIP 注入紅；cut-ok `refuse=None` 不假綠 | ✅ |
| S-5.4 | `HOLLOW-TRUE`；函式真當 F3 綠＝該格紅 | ✅ |
| S-5.5 | `HOLLOW-FILES`；檔在當綠＝該格紅 | ✅ |
| S-5.6 | `HOLLOW-F2`；只 F2 綠當 F3 綠＝該格紅 | ✅ |
| S-5.7 | `F3-F2-REGRESS`；`test-five-station-f2.sh` failed=0（地板，不是 IFF） | ✅ |
| S-5.8 | `TOKEN-KEEP`；`check-gate-tokens.sh` exit 0 | ✅ |
| S-5.9 | `HOLLOW-WORD`；只用字當綠＝獨立紅格 | ✅ |
| S-5.10 | `HOLLOW-TWO-SCRIPT`；兩支腳本各綠 ≠ 同一電池 | ✅ |
| S-5.11 | `HOLLOW-HTML-NE-GWT`；僅 html → `has_old7` 假 | ✅ |
| S-6.1 | `NEW5-WAIT-RED`；注入仍停 `N7-g1`＝該格紅 | ✅ |
| S-6.2 | `KEEP-MK-RED`；M3／M5／M9／M11／M12／M15 具名；不只 M11 | ✅ |
| S-6.3 | `KEEP-SHIP-MECH`；機械 Done＝該格紅 | ✅ |
| S-7.1 | `OLD7-FREEZE`；1–7 `.md` → legacy；無五站機 | ✅ |
| S-7.2 | `OLD7-FOLD-RED`；對 in-flight 寫五站＝該格紅 | ✅ |
| S-7.3 | `SELF-OLD7`；本目錄／F2／simplify 跳不過 | ✅ |
| S-7.4 | 同 CASE；NEW5＝`scripts/fixtures/five-station-f3/new5/` | ✅ |
| S-7.5 | 無第一隻活五站發明名；`--group` 名詞 ⊆ 官方 25 | ✅ |
| S-8.1 | gate：4-spec 頂欄已 Human G2；本場不重開、不改 4-spec | ✅ |
| S-8.2 | Files ⊆ 准許清單 **＋ D-1 L1 四檔具名**（見 Known Limits #1） | ✅ |
| S-8.3 | token／F2 已封 R／S／in-flight 折線 diff＝0 | ✅ |
| S-8.4 | `TOKEN-DEL-RED`；注入刪 token 卻標成功＝該格紅 | ✅ |
| S-8.5 | 4-spec Disposition Q15–Q27 有去向；spec-gate C9 | ✅ |
| S-8.6 | `docs/dev/five-station-f2/` diff＝0；不重開 F2 park | ✅ |
| 既有測試套件(回歸) | `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`；`bash scripts/test-five-station-f2.sh`；`bash scripts/test-five-station-f1.sh`；`bash scripts/check-file-map.sh`；`bash scripts/check-gate-tokens.sh` | ✅ |

**回歸末行（reviewer @ `cc5faa9`）**：spec-gate `9/9` exit 0（49 S）；F3 `failed=0` unique CASE=25（印 33）；F2 `failed=0` CASE=18；F1 `failed=0` CASE=63；file-map `scanned=213` exit 0；tokens 全過；doctor `COMPATIBLE`（約束，不是 hop 通行證）。`--only new5&#124;old7&#124;token` 各 exit 3；`--probe hollow-*`／`two-script` 各 exit 3；`--probe polarity` exit 1；未知旗標／`--only bogus` exit 2。

## Verification Evidence

<!-- Final Fresh 在 Stage 6 錨 ALREADY_SYNCED 之後走路徑①重綁當下 main tip。
     產品碼樹 = origin/main after #385 + STATUS #390。本 PR 後續只加本雙檔，不改牙。 -->

- Source SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
- Final Fresh Run ID: f3-s7a-fresh-cc5faa9-20260914
- Entry point: `bash scripts/test-five-station-f3.sh`（Conditional 已落地 → 本場列入加嚴 Required）然後 `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`
- Toolchain: system bash + python3 + repo scripts（無新套件）

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| spec-gate（本 hop：`bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md`） | `bash scripts/check-spec-gate.sh docs/dev/five-station-f3/4-spec.md` | pass | exit 0; 9/9; 49 S | |
| token 檢查（本 hop 可跑 `scripts/check-gate-tokens.sh`）。本 hop **不**把未落地的 F3 電池列 Required | `bash scripts/check-gate-tokens.sh` | pass | exit 0; G1 2 token; G2 3 token; G3 4 token | |
| test-five-station-f3 | `bash scripts/test-five-station-f3.sh` | pass | failed=0; unique CASE=25; printed CASE=33; exit 0 | |
| hollow --only new5 | `bash scripts/test-five-station-f3.sh --only new5` | pass | exit 3; 印 hollow --only new5 | |
| hollow --only old7 | `bash scripts/test-five-station-f3.sh --only old7` | pass | exit 3; 印 hollow --only old7 | |
| hollow --only token | `bash scripts/test-five-station-f3.sh --only token` | pass | exit 3; 印 hollow --only token | |
| unknown --only | `bash scripts/test-five-station-f3.sh --only bogus` | pass | exit 2（用法；不得當 hollow 綠） | |
| hollow --probe hollow-true | `bash scripts/test-five-station-f3.sh --probe hollow-true` | pass | exit 3; 印 hollow probe is not F3 complete | |
| hollow --probe polarity | `bash scripts/test-five-station-f3.sh --probe polarity` | pass | exit 1; 印 3 CASE + polarity 探針（非法拒當紅格綠） | |
| test-five-station-f2 | `bash scripts/test-five-station-f2.sh` | pass | failed=0; CASE=18; exit 0 | |
| test-five-station-f1 | `bash scripts/test-five-station-f1.sh` | pass | failed=0; CASE=63; exit 0 | |
| file-map regression | `bash scripts/check-file-map.sh` | pass | exit 0; scanned=213; table_rows=223 | |
| doctor handshake | `bash hooks/devflow-doctor.sh` | pass | COMPATIBLE; docs/dev 契約仍 2.0.0 ∈ supported（含 2.1.0）; gauntlet 1.3.3 | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile 未列本層 Required；本刀無突變套件） |
| UI e2e（本刀無新前端） | | n-a | | Explicitly excluded；F3 無產品 UI |
| 負荷／效能（路線閘非熱路徑） | | n-a | | Explicitly excluded |
| 金流／auth fuzz（不涉） | | n-a | | Explicitly excluded |

八點機械面（G3 錨全文）見附錄 A5。指向 **單一電池 + hollow／polarity 探針 + F2 地板**，不是「檔在」或「只 F2 綠」。**八點齊 ≠ 機械代填 Human PASS**。本檔 `verdict: PRE-REVIEW`。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得 silent `True` 當 cut（S-1.3、S-5.4） | ATTEST-SILENT-RED；HOLLOW-TRUE | pass |
| 不得 2.1.0 當 cut（S-2.4） | PRE-210-NE-CUT；理由含 `F3 cut 未發生` | pass |
| 不得 fallback 錯鍵（S-2.1、S-2.2） | READ-SEAM 三切片；`contract_version` 只讀正本鍵 | pass |
| 不得七／未宣告就跳過（S-2.6、S-3.2） | PRE-HOPS-200；graph-edges | pass |
| 紅格不得把拒 hop 當綠（S-5.3） | WAIT／KEEP-MK／SHIP 注入紅 | pass |
| 不得只跑 NEW5 或只跑 F2（S-5.1、S-5.6） | `--only` exit 3；HOLLOW-F2 | pass |
| 不得對本目錄建五站機（S-7.3） | SELF-OLD7 | pass |
| 不得本 hop 自填 G3 PASS（S-8.1 鏡像） | 本檔 `verdict: PRE-REVIEW`；author ≠ human | pass |
| 不得 F3 再折 in-flight／刪 token／重開 F2 park（S-8.3、S-8.4、S-8.6） | F2 目錄 diff＝0；TOKEN-DEL-RED；token 牙綠 | pass |
| 不得 doctor 綠當路條（S-4.3） | DOCTOR-NE-TICKET | pass |
| 不得只擋 M11（S-6.2） | KEEP-MK 六個 M id | pass |
| Out of Scope 後站不准改成 In | 5-tasks／6-notes 鎖仍 Out；本 PR 不改 STATUS | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

（#385 為 Cloud Agent 手動／非 dev-run ledger。本節留白，不虛構模型歷史。）

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

> **s7-fresh-reviewer-A 2026-09-14 親跑** `bash scripts/test-five-station-f3.sh -v`（不採信 6-notes 貼文）。長輸出見附錄 A4。樹＝`cc5faa9`。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 三槽檔＋`f3_cut_happened` | `[ok] S-1.1 who/when nonempty`／`which_condition=f3-cut`／`f3_cut_happened True` | ✅ |
| S-1.2 | 缺檔或空槽 | `[ok] S-1.2 missing → False`／`empty → False` | ✅ |
| S-1.3 | silent True 該格紅 | `[ok] S-1.3 silent True without slots is the red cell` | ✅ |
| S-1.4 | 函式不寫檔 | `[ok] S-1.4 bytes unchanged` | ✅ |
| S-1.5 | 契約兄弟鍵拒 | `[ok] S-1.5 sibling-key SoT rejected` | ✅ |
| S-1.6 | 用語 ≠ SoT | 活樹 `docs/dev/f3-cut-attestation.json` 三槽；guide 只改 lead 用字 | ✅ |
| S-2.1 | 只讀正本鍵 | `[ok] S-2.1 reader returns 2.0.0` | ✅ |
| S-2.2 | 舊 reader 紅 | `[ok] S-2.2 inject old reader claim is the red cell` | ✅ |
| S-2.3 | 2.1 已宣告、cut 獨立 | `[ok] S-2.3 declared true`／`cut still independently false` | ✅ |
| S-2.4 | 2.1 真 cut 假 | `[ok] S-2.4 allow_legacy`／`reason has F3 cut 未發生` | ✅ |
| S-2.5 | 三前置缺一 | PRE-AND 三切片各 `[ok] S-2.5 legacy` | ✅ |
| S-2.6 | 2.0.0＋五站 hops | `[ok] S-2.6 SLOT-REJECT`／`route still old 7` | ✅ |
| S-2.7 | 未宣告跳過側不生效 | `[ok] S-2.7 skip side inactive while undeclared` | ✅ |
| S-3.1 | cut 後無 1–7 → 五站 | `[ok] S-3.1 route is five`／`stage2 skips routine N7-g1` | ✅ |
| S-3.2 | dual-read 未宣告 | PRE-HOPS-200＋graph-edges 仍舊 7 | ✅ |
| S-3.3 | 只用字紅 | `[ok] S-3.3 wording-only inject graph_next stays N7-g1 is the red cell` | ✅ |
| S-3.4 | 節點不刪 | `[ok] S-3.4 nodes kept`；磁碟 `N7-g1.md`／`N6-g2.md` 仍在 | ✅ |
| S-3.5 | 閘＝邊 | `[ok] S-3.5 gate and stage2 agree`／`stage4 agree` | ✅ |
| S-3.6 | 條件邊＋閘 | `next_when_five: N8-end`／`N7-end`；`graph_next` 讀同一 `allow_legacy` | ✅ |
| S-4.1 | supported 加 2.1.0 | 活樹 `supported_contract_versions` 含 `2.1.0` | ✅ |
| S-4.2 | 漏清單誠實紅 | `[ok] S-4.2 prints INCOMPATIBLE`／`non-zero exit` | ✅ |
| S-4.3 | 綠 ≠ ticket | `[ok] S-4.3 reason is route`；活樹 doctor 仍 `COMPATIBLE`（docs/dev 契約 2.0.0） | ✅ |
| S-4.4 | 不改握手 | `git diff 822f842..cc5faa9 -- hooks/_doctor_impl.py`＝空 | ✅ |
| S-4.5 | marketplace／cache 非第四條 | `allow_legacy` 丟棄那兩參；`:149-152` | ✅ |
| S-5.1 | 單一入口三路 | 無引數 exit 0；任一 `--only` exit 3 | ✅ |
| S-5.2 | 不得減 20 列 | unique＝25（20＋standing 5）；無發明名 | ✅ |
| S-5.3 | 極性 | WAIT／MK／SHIP `[ok]` 注入是紅格；cut-ok None 不假綠 | ✅ |
| S-5.4 | hollow True | `[ok] S-5.4 inject True-as-green is the red cell` | ✅ |
| S-5.5 | hollow 檔在 | `[ok] S-5.5 inject files-exist-as-green is the red cell` | ✅ |
| S-5.6 | hollow F2 | `[ok] S-5.6 inject F2-green-as-F3 is the red cell` | ✅ |
| S-5.7 | F2 地板 | `[ok] S-5.7 F2 battery still green (floor)`；另親跑 F2 `failed=0` | ✅ |
| S-5.8 | token 仍在 | `[ok] S-5.8 token teeth still green` | ✅ |
| S-5.9 | hollow 用字 | `[ok] S-5.9 inject wording-as-green is the red cell` | ✅ |
| S-5.10 | 兩支腳本 | `[ok] S-5.10 two scripts each green is the red cell`；`check-five-station-f3.sh` 只宣告不是入口 | ✅ |
| S-5.11 | 僅 html | `[ok] S-5.11 has_old7 false` | ✅ |
| S-6.1 | 注入仍等人 | `[ok] S-6.1 inject wait is the red cell` | ✅ |
| S-6.2 | MK 仍 hop | `[ok] S-6.2 inject MK-red still hop is the red cell`；六 M | ✅ |
| S-6.3 | 機械 Done | `[ok] S-6.3 inject mechanical Done is the red cell` | ✅ |
| S-7.1 | in-flight 舊 7 | `[ok] S-7.1 no five-station machine` | ✅ |
| S-7.2 | 折線紅 | `[ok] S-7.2 inject five-station write on OLD7 is the red cell` | ✅ |
| S-7.3 | 本目錄跳不過 | `[ok] S-7.3 five-station-f3/f2/simplify cannot auto-advance` | ✅ |
| S-7.4 | NEW5＝合成根 | `[ok] S-7.4 NEW5 is synthetic` | ✅ |
| S-7.5 | 不發明活五站名 | 無 `NEW5-MKTG`／`GRAPH-AGREE` | ✅ |
| S-8.1 | 不重開 Stage 4 頂欄 | 4-spec 仍 Human G2；本 PR 不改它 | ✅ |
| S-8.2 | Files 准許＋D-1 | 產品 diff 超出三支 CI 腳本＋guide `#filemap`＝**D-1 具名** | ✅ |
| S-8.3 | 禁區 0 | token 刪檔／F2 已封／折 in-flight＝0 | ✅ |
| S-8.4 | 注入刪 token 紅 | `[ok] S-8.4 inject token delete claim is the red cell` | ✅ |
| S-8.5 | Q15–Q27 去向 | Disposition 表在；spec-gate C9 | ✅ |
| S-8.6 | 不重開 F2 park | `docs/dev/five-station-f2/` 本刀 diff＝0 | ✅ |

## 截圖槽

本場無產品 UI（F3 = CLI coordinator + fixture 自檢）。目錄無 `shots/`。不准新增、不准發明編輯 URL。缺檔不寫「未掛」。

### 進場
- data-shot: n-a
- src: n-a
- caption: 無畫面；現象 = 電池 CASE stdout
- 進場:本場無可從列表打開的既有 UI 紀錄。不准新增。
- hang-point: n-a

## Operational Walkthrough

F3 是 cut 紀錄／讀鍵／條件邊／路線閘／電池，不是現場交接 UI。有 Operational Context 的 S 以「owner 寫三槽、新 slug 不再例行停、in-flight 仍舊 7」走一遍；注入格與純內部約束標不適用。

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 母版 owner | 留下可指的 cut | 寫三槽 JSON | 人填 who／when | 檔未寫＝未切 | 人指得到；讀端 True |
| S-1.2／S-1.4／S-1.5 | — | — | 讀端 | 不寫判定 | 缺槽＝False | 不適用（只讀） |
| S-1.3 | 電池作者 | 餵 silent True | 注入格 | 不把函式真當切 | 該格紅 | 極性對 |
| S-1.6 | 寫手 | 改 guide 用字 | 七站→五站 lead | 不把用語當 SoT | 用語切 ≠ 行為切 | SoT 仍是三槽 |
| S-2.1…S-2.3 | 採用端／讀鍵 | 宣告 2.1.0 | `contract_version` | 不 fallback 錯鍵 | 只 bump 正本仍假 | READ-SEAM 紅 |
| S-2.4／S-2.5 | coordinator | 三前置 AND | `allow_legacy` | 2.1.0 ≠ cut | 缺一 → 仍舊 7 | 理由分缺哪一條 |
| S-2.6／S-2.7 | 遠端採用端 | 不被 2.0.0 改線 | SLOT-REJECT | 先 bump 再 hops | 未宣告不得跳過 | 仍舊 7 |
| S-3.1 | 新 slug 寫手 | 不再例行停 G1／G2 | `graph_next`＋閘 | 不寫「要不要繼續」 | latch 假 | hop 到 N8-end／N7-end |
| S-3.2／S-3.5／S-3.6 | — | — | 條件邊＝閘 | — | 兩邊同意 | 不適用（同意探針） |
| S-3.3 | 電池作者 | 只用字不得綠 | GRAPH-WORD-NE | 不把 guide 當切 | 該格紅 | 極性對 |
| S-3.4 | 方法論維護者 | 舊 7 錨仍在 | 節點檔＋token | 不刪 N7-g1／N6-g2 | dual-read 仍可測 | 檔在 |
| S-4.1／S-4.2 | plugin 維護者 | 漏清單誠實紅 | supported 加 2.1.0 | 不改握手 | INCOMPATIBLE | DOCTOR-HONEST |
| S-4.3 | 採用端 | doctor 綠後想 hop | `refuse_hop_reason` | 不把 COMPATIBLE 當切線 | 仍舊 7 | 理由是路線 |
| S-4.4／S-4.5 | — | — | 握手／cache | marketplace 不當票 | 第四條不存在 | 不適用（約束） |
| S-5.1／S-5.2／S-5.7…S-5.11 | — | — | 電池入口 | hollow exit 3 | 兩支腳本 ≠ 同一電池 | 不適用（完成定義） |
| S-5.3…S-5.6 | 電池作者 | 餵 hollow | `--probe`／注入 | 不把拒 hop 記綠 | 各格獨立紅 | 極性對 |
| S-6.1 | 新 slug 寫手 | 謂詞真仍等人＝紅 | WAIT-RED | 刪等人句 | 例行停不得當綠 | 該格紅 |
| S-6.2 | T reviewer | Must-keep 紅仍 hop＝紅 | KEEP-MK | 補六 M | 不得只測 M11 | 該格紅 |
| S-6.3 | owner | Ship 唯人 | SHIP-MECH | 人寫 PASS | 無逾時自動 Done | 該格紅 |
| S-7.1／S-7.2 | 已 freeze slug | 不被折成五站 | OLD7 | 不寫五站狀態 | 注入折線＝紅 | 仍舊 7 |
| S-7.3…S-7.5 | 本 slug owner | 本目錄不是白老鼠 | SELF-OLD7 | 另開 cut 之後才開的 slug | 跳不過 | 合成 fixture |
| S-8.1…S-8.6 | Stage 5／6／7 寫手 | 只施工 F3 准許檔 | Files 聯集 | STATUS 走 companion | D-1 四檔待 Human park | 刀口守住；L1 未 park |

六條 walkthrough 檢查（技術過但人做不完／看得見沒決策權／等待標成完成／系統外失蹤／中斷不能恢復／資訊過期）：本場未命中。Ship 無自動 Done（S-6.3）。cut 檔未寫＝未切，無逾時變真（S-1.1）。

## Design Integrity Check(Design Boundary Contract 為 `applicable` 時逐項過;`n-a` 時記 n-a)

DBC = applicable（4-spec ②③⑧⑨⑩）。命中項併入雙軸；本清單不另立 Gate。

1. **依賴反向被間接繞過**:未命中。路線閘讀契約＋cut 檔＋1–7 `.md`；Files 不含 `hooks/_doctor_impl.py`；`822f842..cc5faa9` 握手語意 0 行。doctor 綠不是第四條前置（S-4.3／S-4.5）。
2. **資料所有權被繞過寫入**:未命中。cut 檔 owner＝寫入的人類；`f3_cut_happened` 只讀（S-1.4）。契約正本鍵 owner＝`devflow-contract.json`；reader 不寫。本目錄／F2／simplify 不建五站機（S-7.3）。
3. **相容性破壞包成新增**:未命中。公開契約 **additive** bump `2.0.0`→`2.1.0`＋supported 加列；未改既有 2.0.0 握手語意。`agent-event` 未 bump。`next_when_five` 是新鍵，預設 `next` 仍進例行停。
4. **一致性邊界被拆解**:未命中。三前置 AND 在閘與條件邊同一函式 `allow_legacy`（S-3.5）。未把「只 bump 正本」與「reader 已修」揉成一格（READ-SEAM 獨立紅）。
5. **宣告的 Test seam 未被使用**:未命中。seam＝`f3_cut_happened`／`contract_version`／`allow_legacy`／`graph_next`／`--case`／`--only`／`--probe`；電池走同一入口 `test-five-station-f3.sh`。
6. **Known design limit 被實作悄悄「解決」**:未命中。4-spec Stage 4 hop 的「本 hop 不落地」已被後站落地（預期）。doctor 綠陷阱仍在採用現場（活樹 doctor 讀 `docs/dev/devflow-contract.json`＝`2.0.0` 仍 `COMPATIBLE`）。D-1 是 CI 註冊，不是把「不准切」修掉——活樹 cut 檔是 T-10 明文準許的 SoT。F2 park 未重開。

## Standards Axis

獨立掃（未先採信 Self-Review）。無 🔴。無未授權 Boundary 變更。D-1 與本場另列 Diff Budget 超支皆 🟡 **未 park**（Human 未簽）。

- F-s7a-1 🟡 D-1 四檔在 5-tasks S-8.2 准許清單正文之外（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`／guide `#filemap` 三列） | 4-spec L838 寫「超出 → L2」；作者／RR1／RR2 CONCUR L1 | 本場獨立再評：**仍 L1**（host CI 註冊，不是第二次 cut、不是刪 token、不是重開 F2 park）。**未 park**。見 Known Limits #1
- F-s7a-2 🟡 `scripts/fixtures/five-station-f3/` tracked＝49 > Stage 4 Diff Budget「≤12」 | 估計超支 | 方法：`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3` → 49。作者 6-notes **未立 D-n**。本場獨立記 🟡。不動 R/S。見 KL #2
- F-s7a-3 🟡 `5-tasks.md` `status: approved` 而 checkbox 全 `[ ] 未完成` | 看起來像任務已核 | N1-arm／graph P0 only（作者 Files Changed 已寫）。不是勾 T、不是 G3。本場獨立記 🟡。見 KL #3
- F-s7a-4 🟡 `scripts/five_station_f3.py` `wc -l` = 1162 > Diff Budget coordinator ≤200 | 行數超估 | 單一家族（不改 `five_station_f2.py` 是作者 Decision，擋 F2 假紅）。作者未立 D-n。本場獨立記 🟡。見 KL #4
- F-s7a-5 🟢 `--probe polarity` 恆 exit 1；`polarity_inverted` 在 cut-ok `refuse is None` 時 `invert_from_clean=True` | 腳本頂註寫 `--probe polarity → exit 1`；電池紅格另有 `[ok]` | 探針是一等旗標示範「非法拒當紅格綠」，不是產品回歸紅。不升 🟡
- F-s7a-6 🟢 預設入口印 `=== CASE` ×33、unique＝25 | 切片（ATTEST×5／READ-SEAM×3／PRE-AND×3）重複官方名 | S-5.2 鎖的是官方 25 **名**，不是印次。不發明名
- F-s7a-7 🟢 `--group graph-edges` 印 NEW5-CUT-OK＋PRE-HOPS-200（count=3） | 名詞 ⊆ 官方 25；無 `GRAPH-AGREE` | 對準 T-5 Verify
- Design Boundary（Dependency Direction／Leakage／Ownership／Interface Stability）:無未授權變更。D-1 是 host CI 地板，不是新公開 API。契約 bump 是 spec 授權的 additive 2.1.0

## Spec Axis

逐 R。Deviations：D-1 如實。作者未立 D-2／D-3／行數超支 —— 本場補 🟡，不把「沒寫」當成沒有。無隱藏 L2。F2 park 明確未重開。未發明 G3。

| R | 判定 | 證據 |
|---|---|---|
| R-1 | **符合** | S-1.1…S-1.6；三槽 SoT；silent True 紅；只讀；非契約兄弟鍵 |
| R-2 | **符合** | S-2.1…S-2.7；只讀正本鍵；PRE-210／PRE-AND／PRE-HOPS-200 |
| R-3 | **符合** | S-3.1…S-3.6；`next_when_five`；閘同意；節點不刪 |
| R-4 | **符合** | S-4.1…S-4.5；supported 加 2.1.0；握手 0 diff；綠 ≠ ticket |
| R-5 | **符合** | S-5.1…S-5.11；25 名；hollow／兩腳本／html；F2 地板 |
| R-6 | **符合** | S-6.1…S-6.3；WAIT／MK／SHIP 注入紅 |
| R-7 | **符合** | S-7.1…S-7.5；OLD7 凍結；SELF；合成 NEW5 |
| R-8 | **符合（刀）＋D-1 未 park** | S-8.1…S-8.6。D-1 四檔是明文 L1，不是 silent extras。Human 尚未接受／park |
| D-1(L1) | 如實；本場 CONCUR L1；**未 park** | 四檔具名。4-spec「超出→L2」字母讀留檔。不動 R/S。等 Human |
| Design Boundary | 符合契約 | 無未授權 Boundary；未偷偷修掉 Known design limit；未重開 F2 park |

## 變更架構圖

必須對上 `#385` basename（本 PR 只加 `7-review.md`／`7-review.html`）。

```text
[test-five-station-f3.sh] ----exec----> [five_station_f3.py]
                                         +-- f3_cut_happened
                                         |     docs/dev/f3-cut-attestation.json
                                         |     who / when / which_condition
                                         +-- contract_version
                                         |     只讀 devflow_contract_version
                                         +-- allow_legacy / refuse_hop_reason
                                         |     declared ∧ ¬in-flight ∧ cut
                                         +-- graph_next
                                               stage2 S6-selfcheck.next_when_five -> N8-end
                                               stage4 S5-gate.next_when_five     -> N7-end
                                               default next 仍 N7-g1 / N6-g2

[check-five-station-f3.sh]  (選配薄殼, exit 0, 不是第四路)

live tree:
  root devflow-contract.json          = 2.1.0
  docs/dev/devflow-contract.json      = 2.0.0  (doctor 讀這份 → 仍 COMPATIBLE)
  hooks/runtime-capabilities.json     += 2.1.0
  docs/dev/f3-cut-attestation.json    = 三槽 (T-10)
  this slug / f2 / simplify           = frozen OLD7

D-1 floor (not 5-tasks Files union):
  check-file-map.sh          EXPECTED 210 -> 213
  test-architecture-guards.sh  pin 213
  devflow-check.sh           run F3 check + test
  guide #filemap             三列
```

## Diff(merge-base(main)..HEAD,逐檔折疊)

本審查 hop 相對開工 `cc5faa9` 只加本雙檔（寫完才 commit）。產品樹相對 Stage 6 錨 `822f842`：

<details>
<summary title="cut 讀端＋電池"><code>scripts/five_station_f3.py</code> +1162／<code>scripts/test-five-station-f3.sh</code> +20／<code>scripts/check-five-station-f3.sh</code> +7</summary>
<pre>單一家族 coordinator。OFFICIAL 25。f3_cut_happened 只讀三槽。
contract_version 只讀正本鍵。allow_legacy 三 AND。graph_next 讀 next_when_five。
入口薄殼 exec python3。選配 check 只宣告不是電池。</pre>
</details>

<details>
<summary title="條件邊"><code>skills/dev-flow/stage2/graph.yaml</code> · <code>skills/dev-flow/stage4/graph.yaml</code></summary>
<pre>+next_when_five: N8-end
+next_when_five: N7-end
預設 next 仍 N7-g1／N6-g2。節點檔 0 刪。</pre>
</details>

<details>
<summary title="契約＋supported＋cut 檔"><code>devflow-contract.json</code> · <code>hooks/runtime-capabilities.json</code> · <code>docs/dev/f3-cut-attestation.json</code></summary>
<pre>devflow_contract_version 2.0.0 → 2.1.0
supported += 2.1.0
who=rick／when=2026-09-14T00:00:00+08:00／which_condition=f3-cut</pre>
</details>

<details>
<summary title="用語＋D-1 地圖"><code>guides/guide-dev-flow.html</code></summary>
<pre>七站單行 → 五站單行,只有 Ship 會被人擋
#filemap +three rows (five_station_f3.py／check／test)</pre>
</details>

<details>
<summary title="D-1 CI 地板"><code>scripts/check-file-map.sh</code> · <code>scripts/devflow-check.sh</code> · <code>scripts/test-architecture-guards.sh</code></summary>
<pre>EXPECTED_MAPPED_FILES 210→213
architecture run F3 check + test
static pin 213</pre>
</details>

<details>
<summary title="fixtures"><code>scripts/fixtures/five-station-f3/</code></summary>
<pre>tracked=49（NEW5＋OLD7＋inject＋html-only）。Diff Budget 估 ≤12 → F-s7a-2。</pre>
</details>

<details>
<summary title="過程檔"><code>docs/dev/five-station-f3/6-implementation-notes.md</code> · html · 5-tasks 頂欄</summary>
<pre>6-notes + RR1／RR2 10／10 ACCEPTED。5-tasks D-3 形 status approved、checkbox 未勾。
STATUS／HISTORY 是 companion #390，不在本 PR。</pre>
</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** Writer A ≠ 人類。`reviewers: []`。禁止把本檔頂欄寫成 PASS／REQUEST_CHANGES／HOLD。機械面（本次 49 S 綠＋回歸綠＋現象相符＋Evidence 八點機械面＋無 🔴）交給本檔查證庫；**人簽仍缺**。D-1／F-s7a-2／F-s7a-3／F-s7a-4 🟡 **未 park**。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 49 S 全綠 | Coverage 49 列 ✅；unique 25 CASE failed=0 | reviewer 實跑；**Human 未簽** |
| 既有回歸綠 | spec-gate 9/9；F2 CASE=18；F1 CASE=63；file-map 213；tokens | reviewer 實跑；**Human 未簽** |
| 現象證據逐 S | 上表＋附錄 A4 | reviewer 親跑電池；**Human 未簽** |
| Evidence 契約 | 本節四欄＋層表；gauntlet 見附錄 A5 | 機械面交給本檔；**Human 未簽** |
| 無 🔴 | 無產品行為 🔴；F-s7a-1…4 皆 🟡 | **未 park**；Exit 人項不勾 |
| F2 park | 明確未重開 | `docs/dev/five-station-f2/` diff＝0 |
| Human G3 | **未簽** | 不得把 PRE-REVIEW 讀成 PASS |

- G3 | 2026-09-14 | **PRE-REVIEW**。Writer A 獨立全文。author ≠ human。D-1 L1 CONCUR、未 park。Source SHA＝真實 main tip `cc5faa9f2c3c02709758b9805ba52bc984dcadf7`。不發明 PASS。STATUS 另 companion（已在 #390；本 PR 不改）。

### 步 2c 整合回歸（Final Fresh 之前）

Stage 6 `FORK_INTEGRATION_SHA=822f84289f6f4267252907e36862e93f1c90eb9d`（6-notes 步 0；本場核過）。本工作樹開工 = 已合入的 `origin/main`。

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: 822f84289f6f4267252907e36862e93f1c90eb9d
FEATURE_HEAD: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=ALREADY_SYNCED FORK=822f84289f6f4267252907e36862e93f1c90eb9d HEAD=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 INTEGRATION=cc5faa9f2c3c02709758b9805ba52bc984dcadf7(refs/remotes/origin/main)—— 你已經同步過了,本次輸出不算數
```

路徑①：**重綁 Final Fresh** 到當下 HEAD = `cc5faa9`（本檔 Source SHA）。共同戰場 = #385＋#390 本身，已當審核對象逐檔看過，不得用此次腳本輸出當「沒有共同戰場」。本 hop **不重綁 Fresh、不改產品碼**。產品碼已在 main；本 PR 只文件。

本 review hop 另跑 `--fork-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7`（= 開工 HEAD = `origin/main` tip）：

```
STATUS: N_A_NO_INCOMING
FORK_INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
FEATURE_HEAD: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_SHA: cc5faa9f2c3c02709758b9805ba52bc984dcadf7
INTEGRATION_REF: refs/remotes/origin/main
結論:STATUS=N_A_NO_INCOMING FORK=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 HEAD=cc5faa9f2c3c02709758b9805ba52bc984dcadf7 INTEGRATION=cc5faa9f2c3c02709758b9805ba52bc984dcadf7(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

該輸出只記本審查 hop 座標，不取代上面 Stage 6 錨的 `ALREADY_SYNCED`，也不當「無共同戰場」。**不 merge 產品碼。** 第二次重跑座標相同（工作樹乾淨、`origin/main` 未再前進）。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | D-1(L1)：host CI 四檔不在 5-tasks S-8.2 准許清單正文。`EXPECTED_MAPPED_FILES` 210→213；`devflow-check.sh` 註冊 F3 電池；architecture 釘；guide **檔案地圖三列**（非第二次 cut）。4-spec L838「超出 → L2」與字母讀留檔 | L1／🟡 | **未 park**。等 Human 接受／park。落點=本表。owner=rick。不在本 PR 縮四檔、不重開 G2 |
| 2 | F-s7a-2：Stage 4 fixture 估 ≤12 檔；**tracked＝49**（`git ls-tree -r --name-only HEAD -- scripts/fixtures/five-station-f3`）。作者未立 D-n | L1／🟡 | **未 park**。不動 R/S。owner=rick。落點=本表 |
| 3 | F-s7a-3：`5-tasks.md` `status: approved` 而 checkbox 全未勾 | L1／🟡 | **未 park**。N1-arm／graph P0 only，不是勾 T、不是 G3。owner=rick。落點=本表 |
| 4 | F-s7a-4：`five_station_f3.py` 1162 行 > Diff Budget coordinator ≤200。作者未立 D-n | L1／🟡 | **未 park**。不拆回 F2 檔（作者 Decision：改 F2 讀鍵會炸 F2 S-3.3）。owner=rick。落點=本表 |
| 5 | doctor 綠陷阱仍在採用現場（4-spec Known design limit）。F3 只加 2.1.0 進 supported，不修 `_doctor_impl.py`。活樹 doctor 讀 `docs/dev/devflow-contract.json`＝2.0.0 仍 COMPATIBLE | 已知 | 維持約束。綠 ≠ ticket（S-4.3） |
| 6 | 步 2c：Stage 6 錨 `ALREADY_SYNCED`；本 review hop 另記 `N_A_NO_INCOMING`（fork＝`cc5faa9`）。兩輸出皆不作「無共同戰場」證據 | 流程 | 已走路徑① 重綁 Fresh 到 `cc5faa9`。不 merge |
| 7 | 本檔 `verdict: PRE-REVIEW`。全勾 ≠ PASS。Human 未簽 | 流程 | 必須由人類落 `verdict:`。Writer A 禁代填 |
| 8 | F2 park D-1／D-2／D-3／F-c-4 已封。本刀不重開、不把 F2 已封 R／S 改成 In | 範圍 | 維持。`docs/dev/five-station-f2/` diff＝0 |

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**:無未授權 Boundary 變更（DIC 六項未命中）。D-1 是 Files／CI 註冊 L1，**不是** Boundary 變更；**但 D-1／F-s7a-2／F-s7a-3／F-s7a-4 🟡 未 park** —— 本項不勾，直到 Human 接受／park（落點＝Known Limits）或打回
- [ ] Quiz（不可逆改動必做；其餘 full lane 選配）:本刀 bump 公開契約 2.1.0＋切 `graph.yaml` 條件邊＝不可逆。Quiz 留給 Human；本 reviewer **不代考、不代答**
- [x] (條件式)整合回歸已在 Final Fresh **之前**記錄:ALREADY_SYNCED 三 SHA＋canonical ref 貼於 Verdict；Fresh 重綁 `cc5faa9`。本 review hop 另記 `N_A_NO_INCOMING`（fork＝`cc5faa9`）。Verdict 後禁改產品碼
- [ ] PR → main:本 hop 開 Stage 7 PR；**禁直上 master**。Human G3 未簽；合入由 merger 做（本 Exit 項 merge 後勾）
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`: n-a（F3 活契約在 repo 根 `devflow-contract.json` 2.1.0，不是 `docs/specs/` living 句；本 PR 不另抄）
- [ ] STATUS.md 已更新為 shipped:**merge 後由 merger 在 main 做**。本 branch **不改 STATUS**
- [ ] 7-review frontmatter status: shipped:本 hop 必須停在 `status: draft` + `verdict: PRE-REVIEW`（Human 未簽；Exit 人項被未 park 🟡 擋住）
- [x] 7-review.html 已產生:先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py /workspace five-station-f3 7-review`（twin 覆寫同檔；無 shots 時 twin 較完整；抽驗格＝中位列 S-5.2；Human 加抽 S-5.1；殘項 S-2.4）。不要只留 shell 截圖
- [ ] feature branch 已刪 / worktree 已清:merge 後再做

回看約定
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| G3 後 | rick | 本檔 Coverage／KL #1；`test-five-station-f3.sh` 仍 failed=0 且 `--only` exit 3 | 電池變紅、hollow 不再是 3、或有人刪 token／重開 F2 park |
| 下一刀前 | rick | S-8.6／KL #8；F2 7-review park 列仍在 | 有人把 F2 D-1…F-c-4 改成 In |

## 附錄:本輪特有

### A1　本輪爭點

1. **G3 主權**：機械全綠 ≠ Human PASS。本 hop `verdict: PRE-REVIEW`。author ≠ human。不得代填。
2. **D-1 准許清單張力**：四檔是 CI 註冊。本場 CONCUR L1。4-spec「超出→L2」字母讀留檔。**未 park**。Exit #1 不勾。
3. **Scope**：只 F3 cut。不重開 F2 park。不刪 token。不拿本 slug 當白老鼠。出貨證據＝**單一電池 + hollow／polarity + F2 地板**，不是檔在、不是只 F2 綠。
4. **2c**：Stage 6 錨 `ALREADY_SYNCED`。本 review hop 另記 `N_A_NO_INCOMING`。不重 merge。Fresh 綁真實 main tip `cc5faa9`。
5. **作者 vs 本場**：Self-Review ①–⑧ 主張電池綠＋RR1／RR2 10／10＋未發明 G3＋D-1 具名 —— 與本場實跑一致。作者 ⑥「Diff Budget 內」過滿：D-1 解釋 Files 超出，但 fixture 49＞12、coordinator 1162＞200 未立 D-n（本場 F-s7a-2／F-s7a-4）。作者 T 列 PENDING 被 RR1／RR2 覆蓋為 ACCEPTED —— 不是 G3。
6. **5-tasks checkbox**：全未勾，正確。`status: approved`＝N1-arm，不是 T 核完。

### A2　本場不宣稱的事

Human G3 PASS。STATUS shipped。5-tasks checkbox 勾選。重開 F2 park。刪 token／刪 `N7-g1`／`N6-g2`。把 doctor 綠當切線。把「檔在／只 F2 綠／兩支腳本各綠」當 F3 完。

### A3　Human 路徑（尚未走）

1. 開 Pages／本機審頁（路徑見 PR）。
2. 抽驗 **S-5.1** 三個 `檔:行`（入口／`:30-56` OFFICIAL 25／`:1134-1145` `--only` exit 3）。殘項 S-2.4 仍在（`:548-556`／`:177-178`／pre-210 fixture）。
3. Known Limits #1（D-1）／#2（fixture）／#3（5-tasks 頂欄）／#4（1162＞200）：明示接受／park 或打回。
4. 判定未落：不得把本檔讀成 PASS。落點＝頂欄 `verdict:`，只經官方 write。
5. attestation 必須 `human:<名> @ <日>`；Agent 禁寫該行。

### A4　Final Fresh 原始輸出（索引）

```
$ git rev-parse HEAD
cc5faa9f2c3c02709758b9805ba52bc984dcadf7

$ bash scripts/test-five-station-f3.sh
… unique 25 CASE … printed === CASE ×33 … [ok] …
failed=0
exit 0

$ bash scripts/test-five-station-f3.sh -v | grep -c '^=== CASE'
33

$ bash scripts/test-five-station-f3.sh -v | grep '^=== CASE' | sed 's/^=== CASE //' | sort -u | wc -l
25

$ bash scripts/test-five-station-f3.sh --only new5; echo $?
3
$ bash scripts/test-five-station-f3.sh --only old7; echo $?
3
$ bash scripts/test-five-station-f3.sh --only token; echo $?
3
$ bash scripts/test-five-station-f3.sh --only bogus; echo $?
2
$ bash scripts/test-five-station-f3.sh --bogus; echo $?
2

$ bash scripts/test-five-station-f3.sh --probe hollow-true; echo $?
3
$ bash scripts/test-five-station-f3.sh --probe polarity; echo $?
1

$ bash scripts/test-five-station-f3.sh --group graph-edges -v | grep -c '^=== CASE'
3
$ bash scripts/test-five-station-f3.sh --group hollow -v | grep -c '^=== CASE'
6
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
exit 0
```

官方 25 名（預設入口 unique）：NEW5-CUT-OK、NEW5-WAIT-RED、OLD7-FREEZE、OLD7-FOLD-RED、TOKEN-KEEP、TOKEN-DEL-RED、ATTEST-VISIBLE、ATTEST-SILENT-RED、PRE-210-NE-CUT、PRE-AND、PRE-HOPS-200、READ-SEAM、DOCTOR-HONEST、DOCTOR-NE-TICKET、GRAPH-WORD-NE、SELF-OLD7、HOLLOW-TRUE、HOLLOW-FILES、HOLLOW-F2、KEEP-MK-RED、KEEP-SHIP-MECH、HOLLOW-WORD、HOLLOW-TWO-SCRIPT、HOLLOW-HTML-NE-GWT、F3-F2-REGRESS。無 `GRAPH-AGREE`／`NEW5-MKTG`／`DOC-OK`。

### A5　Evidence 八點 + Gauntlet

G3 錨八點（正本 `guides/guide-dev-flow.html#gates`）本場對照 —— **單一電池 + hollow ≠ 檔在／只 F2**：

1. Final Fresh 綁 Source SHA＝送審產品 HEAD：`cc5faa9f2c3c02709758b9805ba52bc984dcadf7`（**真實 main tip**，含 #385＋#390）。本 PR 只文件，不改產品碼。docs commit 會再漂 SHA，不重綁、不發明第二次 Fresh。
2. Required Layer = pass：spec-gate 9/9；token 全過。電池已落地 → 本場把 `test-five-station-f3` 當加嚴 Required 且 pass。
3. 已觸發 Conditional = pass：F3 電池＋hollow／polarity；F2／F1 回歸。
4. 不得存在任何 fail：Verification Evidence 層表無 fail。
5. Required 不得 unverified／n-a：電池／spec-gate／token 皆 pass。
6. Explicitly Excluded 可 n-a＋理由：UI e2e／負荷／金流已附理由。
7. Optional 可 unverified＋誠實：無另開 Optional 層假裝 pass。
8. Gauntlet PASS 不取代雙軸／Walkthrough／矩陣／現象：見本檔三大節。**Human G3 未簽**。

Writer A 於產品樹 `cc5faa9`（本雙檔 commit 前）親跑：

```
$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f3/7-review.md \
    --source-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7 \
    --review-file --require-layer test-five-station-f3
✅ evidence gauntlet: 91 checks passed — docs/dev/five-station-f3/7-review.md
exit 0

$ bash scripts/devflow-evidence-gauntlet.sh docs/dev/five-station-f3/7-review.md \
    --source-sha cc5faa9f2c3c02709758b9805ba52bc984dcadf7 \
    --review-file --require-layer test-five-station-f3 \
    --require-layer test-five-station-f2
✅ evidence gauntlet: 92 checks passed — docs/dev/five-station-f3/7-review.md
exit 0
```

本 branch docs commit 後 `--review-file` 強制當下 HEAD → E2 宣告 `cc5faa9` ≠ HEAD（預期漂移，**不重綁、不發明第二次 Fresh**）。`--source-sha` 仍綁真實 main tip `cc5faa9`。Required 兩層用 4-spec 解析出的**全名**（全形括號，不是 substring）。旗標只能加嚴。

`7-review.html`：先 `scripts/build-stage7-html.py --action`，再 `docs/dev/tools/build-gate-twin.py`（twin 覆寫同檔；無 shots 時 twin 較完整）。**不要只留 build-stage7-html 的槽頁、沒過 twin。** Pages 掛 twin。

### A6　作者對照（N4；矩陣之後才讀）

- Self-Review ①–⑧：49 S 有 S-id assertion、未發明 G3、D-1 對得上、DBC 未偷偷修 limit、電池 25／33／failed=0 —— 與獨立實跑一致。
- RR1／RR2：各 10／10 ACCEPTED（#389／#388）。不是 self-ACCEPTED。本場抽查 T-4 理由字面、T-5 `next_when_five`、T-8 六 M、T-10 `--only` exit 3 —— 與 RR 列相符。
- 差異：作者 ⑥ 寫「Diff Budget 內」—— 本場 **CHALLENGE 過滿**：D-1 只覆蓋 Files 准許清單外的 CI 四檔；fixture 49＞12 與 coordinator 1162＞200 未立 D-n（F-s7a-2／F-s7a-4）。5-tasks 頂欄 approved 作者寫在 Files Changed，未立 D-n（F-s7a-3）。
- Decisions（新家族 `five_station_f3.py`／`next_when_five` 字串鍵／frozen 不咬 fixture 路徑／DOCTOR-HONEST 禁綠詞咬完整 `COMPATIBLE` 行）不構成 L2。
- 不另存 `7-review-*.md`。
- Human G3 另由 rick 落檔，不由作者／Writer A 代填。
