---
feature: integration-before-verdict
stage: 5-tasks
status: approved
owner: rick
updated: 2026-09-12
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務

> 把 4-spec（owner 口頭 G2 PASS 2026-09-12；tip `6b49d95`／#216 原 `verdict` 為空，本 hop 只落 frontmatter 以免 Stage 5 graph 拒寫）切成可派工的縱切。
> 本 hop **只寫任務**，不改 `scripts/` 正本、不改 example／manifest、不 bump plugin、不改 `STATUS.md` 表列、不碰 `#196`／diagram-ir-gate、不發版、不寫 Stage 6 碼、不代填 G3。
> 範圍只切 **AS-1 填檔牙** + **活教師掃蕩**。R-5（出貨樹=核准樹的本 slug 真跑）留後續 hop。

## 開工前提

4-spec 依 owner 口頭 G2 PASS 2026-09-12 視為核准。牙掛進既有 `check-stage67` ST 組，不新開 `check-already-synced.sh`。整合腳本只改檔頭／GUIDANCE，STATUS／exit 碼集合不變。活教師改口只動編號／檔頭；HISTORY／dispatch／stage7-loop 不改。2c 仍叫整合回歸，Fresh／gauntlet 改 2d。

## T-1 掛上 check-stage67 填檔牙並用五份對照擋住 void-only
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3; R-2 / S-2.1, S-2.2; R-4 / S-4.1, S-4.2
- Files: scripts/check-stage67-enforcement.sh, scripts/test-architecture-guards.sh, scripts/fixtures/stage67-filled-already-synced/
- Verify: `n=$(bash scripts/check-stage67-enforcement.sh 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Blocked-by: —
- Risk: high
- Intent: 勾 2c 或送 G3 之後，只寫「證據不算數／輸出不算數」會被同一支檢查擋住；重綁 ≥7 hex 或寫「本項 FAIL」才過；還沒勾的草稿與 `N_A_NO_INCOMING` 不會被提前紅。改的是填檔判定與五份對照樣張，不是整合腳本演算法，也不是第二套 CLI。
- Boundaries: 填檔牙住 `check-stage67` ST 組，擁有通過／失敗判定；只讀 7-review，不寫回該檔。禁止新開 `check-already-synced.sh` 當唯一入口，禁止改整合腳本 exit 碼或 STATUS 名稱，禁止刪掉或改鬆既有 ST 模板順序項。結論塊欄位鎖定 STATUS + FORK／HEAD／INTEGRATION／REF + 恢復欄二選一「重綁 Final Fresh。Source SHA: <hex≥7>」或「本項 FAIL」。發動條件=正文有 `ALREADY_SYNCED` 且已宣稱。Actor=Stage 7 reviewer；Goal=不能靠「證據不算數」過關；Human decision=選重綁或本項 FAIL；Authority=reviewer 寫 7-review、檢查 exit 擋勾過；Recovery=補 SHA 或 FAIL 後重跑，不要進 Verdict。Test seam=五份對照 + 既有三支模板牙仍綠。加 S67-FF 負向案時同一 T 改 `EXPECTED_NEGATIVES`／`EXPECTED_TOTAL`。

## T-2 改整合腳本 GUIDANCE 與檔頭並保持只算只判
- [ ] 未完成
- Covers: R-1 / S-1.4; R-3 / S-3.2; R-4 / S-4.3
- Files: scripts/devflow-integration-regression.sh, docs/dev/tools/devflow-integration-regression.sh
- Verify: `n=$(rg -n '重綁' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh | wc -l) && test "$n" -ge 2 && n2=$(rg -n 'FAIL' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh | wc -l) && test "$n2" -ge 2 && ! rg -q 'Exit Checklist.*整合回歸.*計算工具' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh && test "$(rg -c 'sys.exit\(code\)' scripts/devflow-integration-regression.sh)" -ge 1 && bash scripts/check-integration-regression-guard.sh`
- Blocked-by: T-1
- Intent: 腳本印 `ALREADY_SYNCED` 時，人看得到下一步是重綁或 FAIL，不再只聽到「輸出不算數」就結束；檔頭改口成步 2c 整合回歸、Fresh 之前，不再自稱 Exit 程序的計算工具。改的是兩支腳本的檔頭與 GUIDANCE 句子。不會變成自動重綁、自動 FAIL、merge／rebase，也不會改 0／10／11／2。
- Boundaries: 整合腳本擁有三 SHA 與 STATUS 名稱，只算只判、絕不動樹。本 T 只准改檔頭與 GUIDANCE 字，禁止改 `sys.exit(code)` 與 STATUS 集合，禁止新增自動重綁或把 `ALREADY_SYNCED` 自動當 FAIL。散發副本與正本同一 T 一起改，好過 parity 牙。S-3.2 的 manifest 句留給 T-3。

## T-3 掃蕩 example／manifest／衍生 fixture 的舊序針
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4
- Files: example/contract-expiry-reminder/7-review.md, example/contract-expiry-reminder/7-review.html, example/contract-expiry-reminder/4-spec.md, manifests/p4-gauntlet-gates.md, scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md
- Verify: `n=$(rg -n '執行清單 2c 的 Final Fresh|執行清單 2c gauntlet|執行清單 2c 的文檔化命令|Exit Checklist.*整合回歸.*計算工具' example/contract-expiry-reminder/7-review.md example/contract-expiry-reminder/7-review.html example/contract-expiry-reminder/4-spec.md manifests/p4-gauntlet-gates.md scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh | wc -l); test "$n" -eq 0 && ! rg -q '2c gauntlet' scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md && ! bash scripts/check-spec-gate.sh scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md`
- Blocked-by: T-2
- Intent: 抄完整範例或看 gauntlet manifest 的人會走出 2c 整合 → 2d Fresh，不會再把 2c 當成 Fresh／gauntlet。改的是範例 md／其 html twin、manifest、以及跟 example 同一句的衍生負向樣張。不會變成重編號整份 Stage 7 清單，也不會改 HISTORY／dispatch／stage7-loop 當時句。
- Boundaries: 活教師各檔擁有自己的字面；2c 編號仍留給整合回歸。Fresh／gauntlet 只准改成 2d。example 與 `spec-gate-dd-subsection` 衍生 fixture 必須同一 T 改口，改完後 `check-spec-gate.sh` 對該負向 fixture 仍 exit 1。禁止改 `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/`。禁止重寫 `_templates/7-review.md` 已搬的 2c 散文。S-3.4 聯合 `rg` 含 T-2 已改的兩支腳本檔頭，故本 T 硬等 T-2。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| 本檔只切 AS-1 填檔牙 + 活教師；R-5／S-5.1～S-5.3 不進任何 T | owner Stage 5 brief 指定 tooth + live-teacher only。S-5.1 要等本 slug 真跑到 Stage 7 Exit 才有觀測物；S-5.2／S-5.3 是後續 hop 的出貨樹對照，不是這次實作刀。4-spec 也寫「R-5 的真跑留後續 hop」 | 4-spec R-5／Out of Scope；owner Stage 5 brief | 硬塞 T-4 做 S-5.1「假 Verify」。棄：現在沒有 7-review 產物，會變成空跑或假綠 |
| `execution.mode: sequential`，Blocked-by 成 T-1→T-2→T-3 | tip 預設 sequential，parallel 要明示才啟。Feature Risk = high。T-1 與 T-2 檔案不重疊、理論可同波，但第一刀必須先打通填檔牙，GUIDANCE／教師改口再加厚 | `_templates/5-tasks.md` execution 缺省；4-spec Risk high | 開 parallel：T-1∥T-2，T-3 等 T-2。棄：省不下多少，還要 integration branch |
| T-1 含五份對照（void-only／rebind／FAIL／n-a／draft）+ S-4.1／S-4.2 | 最薄縱切必須同時回答「何時紅」與「何時不紅」。既有模板牙是填檔牙的禁區，第一刀就要仍綠，不能留到最後才發現拆掉 | 4-spec S-1.1～S-2.2、S-4.1、S-4.2；模板 tracer-bullet | 把 no-fire 拆成 T-1b。棄：T-1 會只剩函式層，答不出「什麼情況不開火」 |
| T-1 Files 用 fixture 目錄條目，不另開 `test-stage67-filled-tooth.sh` | Diff Budget 填檔牙 ≤3 檔。`=== CASE` 由同一支 `check-stage67-enforcement.sh` 印，不新開 mapped 腳本，免得順便改 file-map／EXPECTED_MAPPED_FILES | 4-spec Diff Budget；OC-1 同一入口 | 新開測試腳本 + 改 guide filemap。棄：超出 ≤3，且變成第二套入口假象 |
| T-2 只動兩支整合腳本；manifest 留給 T-3 | S-1.4 與 S-4.3 的可觀測行為都在這兩檔。S-3.2 的腳本檔頭也在這兩檔，同一刀改完。manifest 與 example 是教師掃蕩，跟 GUIDANCE 不是同一條使用者路徑 | 4-spec S-1.4／S-3.2／S-4.3 | T-2 連 manifest 一起改。棄：Files 會跨教師與腳本兩條故事 |
| T-3 等 T-2（S-3.4 聯合 needle 含腳本檔頭） | 聯合 `rg` 的活路徑聯集含兩支腳本。T-2 未改檔頭時 T-3 的 Verify 必然紅，而且紅的不是 example | 4-spec S-3.4 | T-3 `Blocked-by: —`。棄：Verify 會把 T-2 的活做算進 T-3 |
| R-4 不另開回歸 T | S-4.1／S-4.2 接在 T-1 Verify 尾（三支既有牙）；S-4.3 接在 T-2。單獨 T-4 的 Verify 在開工前已經全綠，沒有 RED→GREEN | 模板 Verify 三律① | 另開 T-4 只跑三支腳本。棄：無鑑別力 |
| Verify 開工前實跑（2026-09-12，尚未寫填檔牙／尚未改口） | T-1：`check-stage67-enforcement.sh` 現印成功句、`=== CASE` = 0，`-ge 5` 紅（③方向對）。T-2：`重綁` 在兩支腳本 0 命中，`-ge 2` 紅（③）。T-3：活路徑 needle 仍命中，`n -eq 0` 紅（③）；`check-spec-gate.sh` 對負向 fixture 已 exit 1（尾段已綠，鑑別力在前段 `rg`） | 模板 Verify 三律；下方實跑紀錄 | 用已綠的 `check-stage67-enforcement.sh` 當 T-1 唯一牙。棄：無鑑別力 |

### Verify 開工前實跑紀錄

在 tip `6b49d95`、尚未改 `scripts/`／example／manifest 時原樣跑（2026-09-12）：

- T-1：`n=$(bash scripts/check-stage67-enforcement.sh 2>&1 | grep -c '^=== CASE'); echo n=$n` → `n=0`；整條 Verify 在 `test "$n" -ge 5` 紅。同檔現況 `bash scripts/check-stage67-enforcement.sh` 本身 exit 0（①所以不能當唯一牙）。
- T-2：`rg -n '重綁' scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` 零命中；`n=0`，`-ge 2` 紅。`Exit Checklist.*整合回歸.*計算工具` 在兩支檔頭仍在。
- T-3：同一 `rg` 在 example md／7-review.html／manifest／兩支腳本仍有命中（實得 6 行，含 html twin）；`n -eq 0` 紅。`check-spec-gate.sh` 對負向 fixture 已 exit 1。
