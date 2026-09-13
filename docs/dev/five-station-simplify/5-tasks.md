---
feature: five-station-simplify
stage: 5-tasks
status: draft
owner: rick
updated: 2026-09-14
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務 — five-station-simplify（Implementer C：anti-hollow F1）

> 把 4-spec（G2 PASS、`verdict: PASS`、`status: approved`、#315／#316）切成可派工縱切。
> C 線只施工 **F1 annex + teeth**。每個 F1 擁有的 RP-1…RP-16 至少一張 T，且該 T 的 Verify 含**會紅的對照稿 selftest**。
> Must-keep 牙：M11＝T-1／T-2；M3＝T-3；M1＝T-4。S-8.6 重開 1B／2B／4C／6B／7C 必須可紅。
> dual-read annex 只鎖九個 `SLOT-` 語意槽，**不鎖欄位鍵名**（OC-3）。
> F2／F3 的 S **本 slug 零 Files**（見 Split Decisions）。不改 Stage 1–4 `_templates/`、不切 `graph.yaml` 預設、不改 `STATUS.md`、不合併、不發明 G3。
> 本 hop **只寫任務**，不落地牙碼。`status` 留 draft。
> 模式：sequential（Feature Risk high；同一支 F1 牙檔重疊）。
> tracer：T-1 先讓「annex 在、牙入口在、RP-1 缺欄壞卡紅」可觀測，再逐 RP 加厚。

## 開工前提

Stage 4 已核准。G2 PASS 已在 tip（#315 本文、#316 STATUS companion）。本 hop 不改 `4-spec.md`／`4-spec.html`。
牙只准長在 `scripts/` 與本 slug annex。負向 fixture 目錄鎖定 `scripts/fixtures/five-station-simplify/`（4-spec DD 下層；本 hop 只點名，Stage 6 才新增檔）。
Design Boundary Contract = applicable。每個 T 的 Boundaries 只摘該 T 碰得到的禁區。
RP-9／RP-10／RP-11 在本 slug 只做**對照稿謂詞牙**（S-2.6「超 cap 各紅至少一次」）。計數器／event schema／coordinator 評表 = F2，本檔那些 S 的 Files 聯集為空。

### N1 R/S 盤點（52 S）

| R | S | 本 hop T |
|---|---|---|
| R-2 假完成／Must-keep | S-2.2 RP-1 缺四欄或 Verify 看起來沒問題 | T-1（tracer） |
| R-2 | S-2.3 RP-2 無 RED 或自審 | T-2（M11） |
| R-2 | S-2.4 RP-3 未定事項三詞／不可測 | T-3（M3） |
| R-2 | S-2.5 RP-4 測試名無 S-id | T-4（M1） |
| R-2 | S-2.8 RP-5 Files 缺或超出聯集 | T-5 |
| R-2 | S-2.9 RP-6 無原始輸出 | T-6 |
| R-2 | S-2.6 annex 只准加；16 列都能紅 | T-14／T-15／T-16／T-17 |
| R-2 | S-2.1 少 Must-keep 違 brief；S-2.7 可選四欄擋 G2 | T-20 |
| R-1 表 A／B 牙 | S-1.10 RP-7 不可逆無 Quiz | T-7 |
| R-3 代寫判定 | S-3.2 RP-8 無人 PASS 卻 Done；S-3.3 Evidence 八點 | T-8 |
| R-3 | S-3.1 RP-16 Agent 代寫 ACCEPTED／PASS | T-9 |
| R-4 attestation | S-4.3 RP-12 未命中卻要求 ACCEPTED | T-10 |
| R-4 | S-4.1 B1 要人類 attestation；S-4.2 RP-13 空欄+chat | T-11 |
| R-4 | S-4.4 RP-14 latch 假卻請人審 | T-12 |
| R-4 | S-4.5 否定跳過句不得當 skip OC | T-22 |
| R-5 舊七／doctor | S-5.1 RP-15 in-flight 寫五站；S-5.2 本 slug 跳不過；S-5.3 僅 html 不凍 | T-13 |
| R-5 | S-5.8 九個 SLOT- 語意槽 | T-17 |
| R-5 | S-5.4 缺新欄不紅；S-5.5／S-5.6／S-5.7／S-5.9 doctor 綠≠已切 | T-18 |
| R-6 Must-keep／Q6 | S-6.1 Disposition；S-6.2 Q6 仍待驗；S-6.3 升格擋 G2 | T-23 |
| R-8 分刀 | S-8.6 不得重開 1B／2B／4C／6B／7C | T-19 |
| R-8 | S-8.1／S-8.5 本 slug 只 F1；S-8.7 builder 重生 | T-1＋T-21 |
| R-1 表 A／B coordinator | S-1.1…S-1.9、S-1.11、S-1.12 | **deferred F2／F3 · Files=0** |
| R-7 rewrite cap 計數 | S-7.1、S-7.2、S-7.3、S-7.4 | **deferred F2 · Files=0** |
| R-8 F2／F3 刀 | S-8.2、S-8.3 | **deferred F2／F3 · Files=0** |
| R-8 已完成 hop | S-8.4 本 Stage 4 PR 只 4-spec 雙檔 | **已滿足 · 本 hop 零 Files** |

### RP → T 對照（F1 擁有的 16 列；每列一張會紅的對照稿）

| RP | 一句 | T | 對照稿（Stage 6 才建檔） |
|---|---|---|---|
| RP-1 | T 缺四欄或 Verify 寫看起來沒問題 | T-1 | `scripts/fixtures/five-station-simplify/rp-01-t-fake-missing-fields.md` |
| RP-2 | 無 RED 或 reviewer=implementer | T-2 | `scripts/fixtures/five-station-simplify/rp-02-no-red-self-review.md` |
| RP-3 | S 含未定事項三詞或不可測 | T-3 | `scripts/fixtures/five-station-simplify/rp-03-vague-or-untestable-s.md` |
| RP-4 | 測試名不含 S-id | T-4 | `scripts/fixtures/five-station-simplify/rp-04-test-name-no-sid.md` |
| RP-5 | 缺 Files 或 Files ⊈ 聯集 | T-5 | `scripts/fixtures/five-station-simplify/rp-05-files-not-subset.md` |
| RP-6 | 完成宣稱無原始輸出／無檔:行 | T-6 | `scripts/fixtures/five-station-simplify/rp-06-no-raw-output.md` |
| RP-7 | 不可逆無 Quiz；可逆強制 Quiz | T-7 | `scripts/fixtures/five-station-simplify/rp-07-irreversible-no-quiz.md` |
| RP-8 | Ship 無人 PASS 卻 Done | T-8 | `scripts/fixtures/five-station-simplify/rp-08-ship-done-without-pass.md` |
| RP-9 | hop 重寫第 3 次仍繼續 | T-14 | `scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md` |
| RP-10 | Decide 重開第 2 次仍繼續 | T-15 | `scripts/fixtures/five-station-simplify/rp-10-second-decide-reopen.md` |
| RP-11 | Goal 重開第 2 次仍繼續 | T-16 | `scripts/fixtures/five-station-simplify/rp-11-second-goal-reopen.md` |
| RP-12 | B1 未命中卻要求 ACCEPTED | T-10 | `scripts/fixtures/five-station-simplify/rp-12-miss-forced-accepted.md` |
| RP-13 | B1 命中、無 attestation 卻 hop | T-11 | `scripts/fixtures/five-station-simplify/rp-13-empty-attestation-plus-chat.md` |
| RP-14 | latch 未命中卻留下請人審 | T-12 | `scripts/fixtures/five-station-simplify/rp-14-please-review-latch-false.md` |
| RP-15 | 舊 7 in-flight 被寫入五站狀態 | T-13 | `scripts/fixtures/five-station-simplify/rp-15-inflight-five-station-state.md` |
| RP-16 | Agent 代寫 ACCEPTED 或 Ship PASS | T-9 | `scripts/fixtures/five-station-simplify/rp-16-agent-written-verdict.md` |

### Verify 開工前原樣跑（2026-09-14；牙尚未落地）

| T | 結果 | 處置 |
|---|---|---|
| T-1…T-23 | `scripts/check-five-station-f1.sh`、`scripts/test-five-station-f1.sh`、`docs/dev/five-station-simplify/f1-annex.md`、`scripts/fixtures/five-station-simplify/` 皆不存在 | ③綠不了但方向對（缺檔／exit ≠ 預期） |

## T-1 立起 F1 牙入口與 annex，並讓 RP-1 缺欄壞卡紅
- [ ] 完成
- Covers: R-2 / S-2.2; R-8 / S-8.1
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, docs/dev/five-station-simplify/f1-annex.md, scripts/fixtures/five-station-simplify/rp-01-t-fake-missing-fields.md
- Verify: `test -f docs/dev/five-station-simplify/f1-annex.md && test -x scripts/check-five-station-f1.sh && { bash scripts/check-five-station-f1.sh --rp RP-1 scripts/fixtures/five-station-simplify/rp-01-t-fake-missing-fields.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-1 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: —
- Intent: 日常多一次終端機拒絕：有人交一張缺 Covers／Files／Verify／Blocked-by、或 Verify 只寫「看起來沒問題」、還勾了完成的任務卡，同一支新牙會紅，勾選不算做完。改的是本 slug annex 與 `scripts/` 新入口，不是改討論／決策／規格模板。不會變成 Cursor 擋寫、不會新開 coordinator、不會在本 T 改 graph 預設或 STATUS。
- Boundaries: 只准新增／編輯 Files 四項。F1 牙模組擁有 RP 對照與 annex 最小集；禁改 `_templates/` 1-discussion／2-decision／3-prototype／4-spec、禁改各站 `graph.yaml` 預設路、禁改 `STATUS.md`／`HISTORY.md`／`devflow-contract.json`。annex 本 T 至少列出 RP-1…RP-16 與九個 SLOT- id 的語意句，不准把 JSON／YAML 鍵名寫死成契約。禁止新增 coordinator 檔。Actor=獨立 T reviewer；Goal=假完成卡當下看見紅；Recovery=補齊四欄後紅熄。

## T-2 讓無 RED 或自審的任務標未完成（M11）
- [ ] 完成
- Covers: R-2 / S-2.3
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-02-no-red-self-review.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-2 scripts/fixtures/five-station-simplify/rp-02-no-red-self-review.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-2 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常少一次「自己審自己就勾完」：沒有失敗測試原始輸出、或 reviewer 欄等於實作者，這張 T 必須停在未完成。改的是同一支 F1 牙對 seam 的拒絕，不是另造審查 UI。不會變成允許自審當簡化、不會在本 T 改 Stage 6 模板正文。
- Boundaries: 只准改 Files 三項。M11 四欄+seam 不可選。禁把 reviewer=implementer 寫成合法捷徑。禁改 `_templates/6-implementation-notes.md` 當本 T 範圍外的模板凍結（本 T 只咬對照稿）。禁止 coordinator。Actor=獨立 T reviewer；Goal=自審與無紅燈輸出不得過；Recovery=換 session 重審並貼原始輸出。

## T-3 讓含未定事項三詞或不可測的規格紅（M3）
- [ ] 完成
- Covers: R-2 / S-2.4
- Files: scripts/check-five-station-f1.sh, scripts/check-spec-gate.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-03-vague-or-untestable-s.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-3 scripts/fixtures/five-station-simplify/rp-03-vague-or-untestable-s.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-3 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常送規格時，S 正文若出現既有 C4 未定事項三詞、或只寫「系統應處理錯誤」卻無可斷言輸出，檢查必須紅，那條 S 不能當 T 的綠燈封面。改的是接進既有 `check-spec-gate.sh` C4 的 F1 對照，不是第二個模糊詞家族。不會變成另造 `check-vague.sh`、不會放寬 C1–C9。
- Boundaries: F1 接既有 spec-gate C4，不另開模糊詞 CLI。只准改 Files 四項。禁改 `_templates/4-spec.md`。對照稿必須含 `VAGUE_ALL` 三詞之一或不可測句。Actor=G2 形狀牙；Goal=不可測 S 進不了 Covers 綠燈；Recovery=改成可斷言輸出後重跑。

## T-4 讓測試名不含 S-id 的案例紅（M1）
- [ ] 完成
- Covers: R-2 / S-2.5
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-04-test-name-no-sid.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-4 scripts/fixtures/five-station-simplify/rp-04-test-name-no-sid.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-4 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常多一次命名拒絕：函數叫 `test_store_half_slot`（沒有 `s_`／`S-` 與對應 S-id）會紅；對照名 `test_s_2_5_test_name_requires_s_id` 不因本條紅。改的是測試命名牙，不是改產品邏輯。不會變成全庫改名儀式、不會誤殺已含 S-id 的 skeleton。
- Boundaries: 只准改 Files 三項。selftest 新案例名必須含 `s_` 與 S-id，否則本條會打自己。禁改 Stage 1–4 模板。Actor=T 實作者；Goal=測試名能被 reviewer 用鏈對到 S；Recovery=把函數名改成含 S-id 後重跑。

## T-5 讓缺 Files 或超出聯集的任務紅
- [ ] 完成
- Covers: R-2 / S-2.8
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-05-files-not-subset.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-5 scripts/fixtures/five-station-simplify/rp-05-files-not-subset.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-5 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常少一次「Files 欄空白或寫了任務單沒列的路徑還算完成」：缺 Files、或列出的路徑不在同一份任務單聯集內，必須紅。改的是 scope 牙，不是放寬 Stage 6 守衛。不會變成允許超出聯集當簡化。
- Boundaries: 只准改 Files 三項。RP-5／M9 不可選。禁在對照稿把缺欄寫成合法。禁止改 `hooks/devflow-lib.py` 的 scope 演算法當本 T 主詞（本 T 只加 F1 對照）。Actor=Stage 6 守衛／T reviewer；Goal=超出聯集不得標完成；Recovery=把路徑收回聯集或補欄。

## T-6 讓完成宣稱無原始輸出的任務紅
- [ ] 完成
- Covers: R-2 / S-2.9
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-06-no-raw-output.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-6 scripts/fixtures/five-station-simplify/rp-06-no-raw-output.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-6 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常少一次「摘要句當證據」：完成宣稱只有「看起來沒問題」、沒有指令原始輸出也沒有 `檔:行`，必須紅。改的是驗證五律牙，不是改聊天語氣。不會變成口頭「過了」可過。
- Boundaries: 只准改 Files 三項。RP-6／M10 不可選。摘要不得當證據。禁改 STATUS。Actor=T reviewer；Goal=沒有原始輸出就未完成；Recovery=補 stdout 或 `檔:行` 後重跑。

## T-7 讓不可逆無 Quiz 與可逆強制 Quiz 都紅
- [ ] 完成
- Covers: R-1 / S-1.10
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-07-irreversible-no-quiz.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-7 scripts/fixtures/five-station-simplify/rp-07-irreversible-no-quiz.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-7 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常出貨時，改到 schema／公開 API／權限／金流／資料遺失卻沒 Quiz 會紅；只是可逆小改卻被當成例行第三停也會紅。改的是 Quiz 開火對照稿，不是實作 coordinator 的停點機。不會變成每次出貨都 Quiz、不會在本 T 寫 F2 前進紀錄。
- Boundaries: 只准改 Files 三項。本 T 不新增 coordinator、不改 graph。B4 可與 Ship 同一人停，不准拆第三次例行停。Actor=Ship 審查者；Goal=不可逆才考人；Recovery=不可逆補 Quiz；可逆拆掉例行 Quiz。

## T-8 讓無人寫 PASS 卻標 Done 的出貨紅，並咬 Evidence 八點
- [ ] 完成
- Covers: R-3 / S-3.2, S-3.3
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-08-ship-done-without-pass.md, scripts/fixtures/five-station-simplify/ship-evidence-missing-eight.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-8 scripts/fixtures/five-station-simplify/rp-08-ship-done-without-pass.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --evidence-eight scripts/fixtures/five-station-simplify/ship-evidence-missing-eight.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-8 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 2`
- Blocked-by: T-1
- Intent: 日常機械全綠仍不能把 slug 標 Done：頂欄沒有人類 `PASS` 就紅；7-review 少 Evidence 八點任一、或用「已經摺站」當省略理由，也紅。改的是出貨物質牙，不是代人簽 PASS。不會變成 Agent 可寫頂欄、不會在本 hop 跑 G3 或發明 G3 PASS。
- Boundaries: 只准改 Files 四項。禁寫本 slug `7-review.md` 頂欄 `verdict: PASS`。禁改 living 契約八點正文。本 T 不開 G3。Actor=Ship 審查者；Goal=出貨樹=人簽過且八點在；Recovery=人寫頂欄並補齊八點。

## T-9 讓 Agent 代寫 ACCEPTED 或 Ship PASS 視為未寫
- [ ] 完成
- Covers: R-3 / S-3.1
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-16-agent-written-verdict.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-16 scripts/fixtures/five-station-simplify/rp-16-agent-written-verdict.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-16 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常少一次機器蓋章：3-prototype 被 Agent 寫入 ACCEPTED 卻沒有 `Verdict attestation: human:`，或 7-review 頂欄 PASS 的寫入者是 Agent／coordinator，系統當沒寫，不得離 Spec、不得 Done。改的是判定主權牙，不是改聊天。不會變成 chat「Treat as PASS」可過。
- Boundaries: 只准改 Files 三項。Agent／coordinator 禁寫 ACCEPTED／Ship PASS。本 T 不示範填 ACCEPTED。禁改 Stage 3 模板欄位名。Actor=母版 owner；Goal=判定只由人寫；Recovery=刪機器寫入，人重寫。

## T-10 讓未命中 Demo 卻要求 ACCEPTED 的案例紅
- [ ] 完成
- Covers: R-4 / S-4.3
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-12-miss-forced-accepted.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-12 scripts/fixtures/five-station-simplify/rp-12-miss-forced-accepted.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-12 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常純守衛 feat 不該被逼做 Demo：九條 trigger 全假或沒有 3-prototype 時，有人仍要求 ACCEPTED，必須紅；同時不建 Demo 頁、不第二次等人。改的是未命中路徑牙，不是補假 Demo。不會變成沒命中還產頁。
- Boundaries: 只准改 Files 三項。未命中不准產 Demo html。禁改 `_templates/3-prototype.md`。Actor=母版 owner；Goal=沒命中不第二次等人；Recovery=刪強迫 ACCEPTED，留下 n-a 原因。

## T-11 讓空 attestation 加 chat 准開不得離 Spec
- [ ] 完成
- Covers: R-4 / S-4.1, S-4.2
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-13-empty-attestation-plus-chat.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-13 scripts/fixtures/five-station-simplify/rp-13-empty-attestation-plus-chat.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-13 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常少一次 dogfood 捷徑：Human verdict 或 attestation 空，owner chat 寫「可以開 Stage 4／准開下一站」，仍不得 hop 出 Spec，chat 文字不准寫進 Human verdict。trigger 已命中時，必須同時有人類 ACCEPTED 與 `human:<名> @ <日>` 才准走。改的是 attestation 牙，不是改 chat 產品。不會變成 Agent 代填 attestation。
- Boundaries: 只准改 Files 三項。chat 不是判定（OC-6）。禁把 chat 抄進 3-prototype 頂欄。禁改 Stage 3 模板。Actor=母版 owner；Goal=空欄+chat 仍卡 Spec；Recovery=人類補行後重評。

## T-12 讓 latch 未命中卻留下請人審的紀錄紅
- [ ] 完成
- Covers: R-4 / S-4.4
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-14-please-review-latch-false.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-14 scripts/fixtures/five-station-simplify/rp-14-please-review-latch-false.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-14 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常少一次客氣問人：A4／A7 latch=否，前進紀錄仍寫「請 owner 看一下／要不要繼續」，必須紅，不是禮貌。改的是請人審句對照，不是實作 F2 hop log 機。不會在本 T 寫 coordinator。
- Boundaries: 只准改 Files 三項。本 T 不新增 coordinator 檔、不改 graph。對照稿是假 hop 紀錄，不是本 slug 真狀態。Actor=後站寫手；Goal=沒命中就不問人；Recovery=刪請人審句。

## T-13 讓 in-flight 寫入五站狀態與本資料夾跳閘都紅
- [ ] 完成
- Covers: R-5 / S-5.1, S-5.2, S-5.3
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-15-inflight-five-station-state.md, scripts/fixtures/five-station-simplify/html-only-not-inflight.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-15 scripts/fixtures/five-station-simplify/rp-15-inflight-five-station-state.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --inflight scripts/fixtures/five-station-simplify/html-only-not-inflight.md; test $? -eq 0; } && python3 -c "import pathlib; p=pathlib.Path('docs/dev/five-station-simplify'); md=list(p.glob('[1-7]-*.md')); assert any(x.name=='1-discussion.md' for x in md); print('T-13-this-slug-has-md')" && n=$(bash scripts/test-five-station-f1.sh --rp RP-15 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 2`
- Blocked-by: T-1
- Intent: 日常本資料夾不能當新五站白老鼠：已有 1–7 任一 `.md` 的 slug 被寫入五站狀態會紅；只有 html、沒有 md 的空目錄不算開工。打開本目錄仍看得到 `1-discussion.md`，五站 hop 跳過 G1／G2 必須跳不過。改的是 freeze 偵測牙（只認 md），不是折本 slug。不會採 4C。
- Boundaries: 只准改 Files 四項。in-flight 只認 1–7 `.md`（OC-5）。禁把本 slug 標成五站機。禁改 graph 預設。Actor=本 slug 執行者；Goal=觀測不被自己污染；Recovery=清回舊 7 狀態。

## T-14 讓第三次 hop 重寫對照稿紅（不實作計數器）
- [ ] 完成
- Covers: R-2 / S-2.6
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-9 scripts/fixtures/five-station-simplify/rp-09-third-hop-rewrite.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-9 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常 F1 必須先能紅「同一 hop 已重寫兩次、第三次還要繼續」這份對照稿，證明 RP-9 列沒有從最小集消失。改的是 fixture 謂詞，不是 coordinator 計數器、不是 event schema。不會在本 T 鎖欄位鍵名、不會寫前進引擎。
- Boundaries: 只准改 Files 三項。S-7.1 計數落點交 F2，本 T 零 coordinator／零 event 檔。不准暗改 cap 數字（仍是 hop≤2）。Actor=F1 寫牙的人；Goal=超 cap 對照稿會紅；Recovery=對照稿停在第 2 次重寫。

## T-15 讓第二次 Decide 重開對照稿紅（不實作計數器）
- [ ] 完成
- Covers: R-2 / S-2.6
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-10-second-decide-reopen.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-10 scripts/fixtures/five-station-simplify/rp-10-second-decide-reopen.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-10 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常 F1 必須能紅「已離開 Decide 又整站重開第二次」的對照稿，站內尚未 hop 出去的小改不當一次。改的仍是謂詞牙，不是 Decide 狀態機實作。不會做 F2。
- Boundaries: 只准改 Files 三項。S-7.2 零 Files。不准放寬 Decide≤1。Actor=F1 寫牙的人；Goal=第二次整站重開對照紅；Recovery=對照稿只留一次重開。

## T-16 讓第二次 Goal 重開對照稿紅（不實作計數器）
- [ ] 完成
- Covers: R-2 / S-2.6
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/rp-11-second-goal-reopen.md
- Verify: `{ bash scripts/check-five-station-f1.sh --rp RP-11 scripts/fixtures/five-station-simplify/rp-11-second-goal-reopen.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --rp RP-11 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常 F1 必須能紅「已 hop 出 Intake 後 Goal 重開第二次」的對照稿。改的是 RP-11 列還在最小集，不是 Goal 重寫引擎。不會做 F2。
- Boundaries: 只准改 Files 三項。S-7.3 零 Files。不准放寬 Goal reopen≤1。Actor=F1 寫牙的人；Goal=第二次 Goal 重開對照紅；Recovery=對照稿只留一次。

## T-17 讓 annex 刪 RP 列或少一個 SLOT 語意槽就紅
- [ ] 完成
- Covers: R-2 / S-2.6; R-5 / S-5.8
- Files: docs/dev/five-station-simplify/f1-annex.md, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/annex-delete-rp-08.md, scripts/fixtures/five-station-simplify/annex-missing-slot-parse-old7.md
- Verify: `{ bash scripts/check-five-station-f1.sh --annex-min-set scripts/fixtures/five-station-simplify/annex-delete-rp-08.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --slots scripts/fixtures/five-station-simplify/annex-missing-slot-parse-old7.md; test $? -eq 1; } && bash scripts/check-five-station-f1.sh --slots docs/dev/five-station-simplify/f1-annex.md && python3 -c "import pathlib,re; t=pathlib.Path('docs/dev/five-station-simplify/f1-annex.md').read_text(); ids=['SLOT-PARSE-OLD7','SLOT-PARSE-NEW5','SLOT-MISSING-NEW5-DEFAULT','SLOT-UNDECLARED-ROUTE','SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS','SLOT-DOCTOR-GREEN-MEANS','SLOT-IN-FLIGHT-DETECT','SLOT-RP-MIN-SET','SLOT-SKIP-NEGATION']; assert all(i in t for i in ids); assert not re.search(r'(?i)required[- ]key\\s*[:=]\\s*[\"\\']', t); print('T-17-slots-no-locked-keys')" && n=$(bash scripts/test-five-station-f1.sh --slots -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 2`
- Blocked-by: T-1
- Intent: 日常核 annex 時，少一個 `SLOT-` id（例如沒有「能解析舊 7」）或刪掉 RP-8 那一列，檢查必須紅。人用 SLOT- id 對到一欄或一句等效話即可，鍵叫什麼本檔不鎖。改的是 annex 形狀，不是選定 JSON 欄名。不會偷做 OC-3 禁止的鍵名表。
- Boundaries: 只准改 Files 五項。九個 SLOT- id 必在；F1 可另命名鍵，但每個 id 要能指到一欄或等效句。禁止在 annex 把特定鍵名寫成唯一合法名。OC-10：RP 只准加不准減。禁止 coordinator event schema。Actor=F1 annex 寫手；Goal=減列或少槽進不了完成；Recovery=補回該 SLOT- id 或 RP 列。

## T-18 讓舊檔缺新欄不紅，並紅契約仍二點零加五站 hops
- [ ] 完成
- Covers: R-5 / S-5.4, S-5.5, S-5.6, S-5.7, S-5.9
- Files: docs/dev/five-station-simplify/f1-annex.md, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/dual-read-old7-missing-new5-ok.md, scripts/fixtures/five-station-simplify/dual-read-2.0.0-plus-five-hops.md
- Verify: `bash scripts/check-five-station-f1.sh --dual-read scripts/fixtures/five-station-simplify/dual-read-old7-missing-new5-ok.md && { bash scripts/check-five-station-f1.sh --dual-read scripts/fixtures/five-station-simplify/dual-read-2.0.0-plus-five-hops.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --dual-read -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 3`
- Blocked-by: T-17
- Intent: 日常採用端看到兩件事：舊 7 檔少了新 5 欄位時，2.1.0 讀檔器不紅（合法缺省）；契約仍 2.0.0 且 hops 已被換成五站預設時，必須紅，且不得把 doctor 握手綠寫成「可以跟 hops 走」或「已切五站」。兩源誰先改都一樣。改的是 dual-read 誠實牙，不是改 doctor 握手語義當 3B。不會遠端改線、不會鎖缺省鍵名。
- Boundaries: 只准改 Files 五項。不改 `hooks/_doctor_impl.py` 握手集合當本 T 主詞（3B 已拒）。doctor 綠只證明版本集合。未宣告 2.1.0 = 舊 7。禁止 marketplace 包裝當路線仲裁。Actor=採用專案 owner；Goal=不被遠端改線還以為沒變；Recovery=釘 2.0.0 並把 hops 當未授權，或正式 upgrade。

## T-19 讓重開 1B／2B／4C／6B／7C 的任務稿紅
- [ ] 完成
- Covers: R-8 / S-8.6
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/
- Verify: `python3 -c "import pathlib; t=pathlib.Path('docs/dev/five-station-simplify/5-tasks.md').read_text(); assert '改採 1B' not in t and '改採 2B' not in t and '改採 4C' not in t and '改採 6B' not in t and '改採 7C' not in t; print('T-19-this-tasks-no-reopen')" && { bash scripts/check-five-station-f1.sh --reject-reopen scripts/fixtures/five-station-simplify/reopen-1b-delete-tokens.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --reject-reopen scripts/fixtures/five-station-simplify/reopen-2b-old-file-red.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --reject-reopen scripts/fixtures/five-station-simplify/reopen-4c-this-slug-as-new5.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --reject-reopen scripts/fixtures/five-station-simplify/reopen-6b-must-keep-optional.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --reject-reopen scripts/fixtures/five-station-simplify/reopen-7c-merge-knives.md; test $? -eq 1; } && n=$(bash scripts/test-five-station-f1.sh --reject-reopen -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 5`
- Blocked-by: T-1
- Intent: 日常實作時若有人把「刪 token／舊檔缺欄就紅／本 slug 當新 5／Must-keep 可選／併刀 F1+F2+F3」寫回任務單或實作選擇，同一支牙必須紅，而且本份 5-tasks 自己也不能出現「改採」那五個代號。改的是已拒案守門，不是翻 Decision。不會把推翻 1A–7A 寫成合法 DD。
- Boundaries: 只准改 Files 三項（牙、selftest、fixture 目錄）。1B=刪 token；2B=舊檔缺欄就紅；4C=本 slug 當新 5；6B=M 可選；7C=併刀。出現「改採」這些代號 = 違 Spec，回 G2，不算本 T 完成。禁改 Decision。Actor=Stage 5／6 寫手；Goal=已拒案進不了實作；Recovery=刪該句後重跑。

## T-20 讓少 Must-keep 的簡化宣稱與可選四欄句紅
- [ ] 完成
- Covers: R-2 / S-2.1, S-2.7
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/missing-must-keep-is-simplified.md, scripts/fixtures/five-station-simplify/optional-four-fields.md
- Verify: `{ bash scripts/check-five-station-f1.sh --must-keep scripts/fixtures/five-station-simplify/missing-must-keep-is-simplified.md; test $? -eq 1; } && { bash scripts/check-five-station-f1.sh --must-keep scripts/fixtures/five-station-simplify/optional-four-fields.md; test $? -eq 1; } && python3 -c "import pathlib,re; t=pathlib.Path('docs/dev/five-station-simplify/5-tasks.md').read_text(); assert not re.search(r'可選四欄|可選 seam|已五站故省', t); print('T-20-this-tasks-no-optional')" && n=$(bash scripts/test-five-station-f1.sh --must-keep -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 2`
- Blocked-by: T-1
- Intent: 日常有人寫「五站已簡化所以可省 Verify／seam／Must-keep」，必須被點名違 brief；本 slug 後站文檔若出現「四欄可選／seam 可選／已五站故省」，送審要擋。改的是 C 線掏空句牙，不是把 M 標成口味。不會採 6B。
- Boundaries: 只准改 Files 四項。M1／M3／M11 與四欄／seam 不可選（OC-11）。本份 5-tasks 正文零處寫那三句。禁改 Stage 1–4 模板來「釘欄位」（6C 已拒）。Actor=本 slug G2／F1 對照；Goal=掏空句進不了後站；Recovery=刪可選句後重送。

## T-21 讓 Files 聯集超出 F1 或審頁手包就紅
- [ ] 完成
- Covers: R-8 / S-8.1, S-8.5, S-8.7
- Files: scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/check-file-map.sh, guides/guide-dev-flow.html, scripts/fixtures/five-station-simplify/files-union-has-coordinator.md
- Verify: `{ bash scripts/check-five-station-f1.sh --scope-union scripts/fixtures/five-station-simplify/files-union-has-coordinator.md; test $? -eq 1; } && python3 -c "import pathlib,re; t=pathlib.Path('docs/dev/five-station-simplify/5-tasks.md').read_text(); files=re.findall(r'^- Files: (.+)$', t, re.M); blob=' '.join(files); assert 'graph.yaml' not in blob; assert '_templates/1-discussion' not in blob and '_templates/2-decision' not in blob and '_templates/3-prototype' not in blob and '_templates/4-spec' not in blob; assert 'STATUS.md' not in blob; assert 'coordinator' not in blob.lower(); print('T-21-union-is-f1')" && bash scripts/check-file-map.sh && n=$(bash scripts/test-five-station-f1.sh --scope-union -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常本 slug 後站若把 coordinator、預設 graph 切線、Stage 1–4 模板或 STATUS 寫進 Files，必須紅。新腳本要進檔案地圖，否則 file-map 會紅。審頁必須用對應 `build-stageN-html.py --action` 或 5-tasks 的 twin 產檔器重生，不得手包 html-shell。改的是刀範圍與產檔紀律，不是切預設路線。不會做 F2／F3。
- Boundaries: 只准 `scripts/` 新牙、本 slug annex、本目錄 5／6／7、file-map 列。禁 `graph.yaml` 預設切線、禁 Stage 1–4 `_templates/`、禁 `STATUS.md`、禁 coordinator 碼。新 `scripts/*.sh` 必須列入 guide file-map，且 `EXPECTED_MAPPED_FILES` 改成加完後的實際數。html 禁止手包 `_templates/html-shell.html`。Actor=Stage 5 寫手；Goal=只施工 F1；Recovery=把超範圍檔從 Files 刪掉。

## T-22 讓否定跳過句不再被讀成 skip Owner Call
- [ ] 完成
- Covers: R-4 / S-4.5
- Files: hooks/_stage3_impl.py, hooks/selftest.sh, scripts/check-five-station-f1.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/skip-negation-as-oc.md
- Verify: `{ bash scripts/check-five-station-f1.sh --skip-negation scripts/fixtures/five-station-simplify/skip-negation-as-oc.md; test $? -eq 1; } && python3 hooks/_stage3_impl.py five-station-simplify && n=$(bash scripts/test-five-station-f1.sh --skip-negation -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常重跑本 slug 的 Stage 3 機械檢查時，「不預先跳過 Stage 3」不得再被讀成 skip OC。對照稿若把「不／無／不得」加「跳過」當成已跳，必須紅。改的是既有 `_stage3_impl.py` 謂詞收緊（4-spec Known limit，F1 才修），不是改 Decision 原文。不會把本 slug 改成未命中、不會改 Stage 3 模板。
- Boundaries: 只准改 Files 五項。收緊 skip 匹配：同時否定「不／無／不得」的「跳過」不得當 owner-call。禁改 `_templates/3-prototype.md`。禁改 graph。selftest 地板隨新案例同步。Actor=G2 reviewer／F1 寫牙的人；Goal=「不准跳」不被讀成「已跳」；Recovery=謂詞收緊後重跑應拒該假 skip。

## T-23 讓 Q6 升格句與缺 Disposition 去向紅
- [ ] 完成
- Covers: R-6 / S-6.1, S-6.2, S-6.3
- Files: scripts/check-five-station-f1.sh, scripts/check-spec-gate.sh, scripts/test-five-station-f1.sh, scripts/fixtures/five-station-simplify/q6-as-observed-fact.md
- Verify: `{ bash scripts/check-five-station-f1.sh --q6 scripts/fixtures/five-station-simplify/q6-as-observed-fact.md; test $? -eq 1; } && bash scripts/check-spec-gate.sh docs/dev/five-station-simplify/4-spec.md && python3 -c "import pathlib,re; t=pathlib.Path('docs/dev/five-station-simplify/4-spec.md').read_text(); assert re.search(r'Q6', t); assert 'open' in t; hits=[ln for ln in t.splitlines() if '採用現場' in ln]; assert hits and all(('Assumption' in ln) or ('仍待驗' in ln) or ('open' in ln) for ln in hits); print('T-23-q6-open')" && n=$(bash scripts/test-five-station-f1.sh --q6 -v 2>&1 | grep -c '^=== RUN'); test "$n" -ge 1`
- Blocked-by: T-1
- Intent: 日常有人把「採用現場也 chat 蓋章」寫成已核事實，本 slug 送審要打回；4-spec 的高影響列仍要看得到去向。本檔保持 Q6 status=open，不是 oc-accepted。改的是升格牙與既有 spec-gate C9，不是捏造採用逐字稿。不會抽公司路徑進 public repo。
- Boundaries: 只准改 Files 四項。Q6 保持 Assumption／仍待驗／open。禁止把 Q6 標 oc-accepted。public repo 禁收公司路徑。spec-gate 擁有 Disposition 形狀；本 T 不改 4-spec 已核正文。Actor=本 slug G2 reviewer；Goal=不捏造採用現場；Recovery=改回 Assumption 後重送。

## Split Decisions(拆分自判)

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| sequential，不開 parallel | Feature Risk high；T-2…T-23 重疊同一支 `check-five-station-f1.sh`／annex。parallel 須明確啟用。 | `_templates/5-tasks.md` execution.mode 缺省 sequential；4-spec Verification Profile Risk high | 棄 T-14 ∥ T-15 ∥ T-16 平行（檔案重疊同一牙）。 |
| T-1 先打通 annex＋牙入口＋RP-1 | tracer：完成後系統多一個可觀測拒絕（缺欄壞卡紅），其餘 RP 才有掛鉤。 | 4-spec S-2.2「T 卡上就紅」；模板 tracer bullet | 棄先寫 dual-read 全文再補 RP-1（那會變成水平切 annex→牙→fixture）。 |
| 每個 F1 擁有的 RP 獨立一張會紅的 T | C 線 anti-hollow：一張 mega-T 只跑 RP-1 會把 RP-9…16 做成散文覆蓋。 | 本 hop brief；4-spec S-2.6「16 列都能紅」；OC-10 | 棄「R-2 九個 S 一 T」。棄無 fixture 的 Covers 空掛。 |
| M11／M3／M1 分開 T-1／T-2／T-3／T-4 | 三顆牙是三個可觀測拒絕，合併會讓 Verify 跑不相干指令。 | Must-keep Disposition M11→S-2.2／S-2.3；M3→S-2.4；M1→S-2.5 | 棄「Must-keep 一 T」。 |
| RP-9／10／11 只做對照稿；S-7.1…S-7.4 零 Files | F1 必須證明最小集含超 cap 列；計數落點／event schema 是 F2。本 slug 那些 S 不進任何 T 的 Files。 | 4-spec S-2.6 vs S-7.1…S-7.4；OC-3；S-8.5 | 棄本 slug 寫 coordinator 計數器（F2 implementation T）。棄把 S-7.x 掛進 T-14 Files。 |
| S-1.1…S-1.9、S-1.11、S-1.12 零 Files | 表 A／B 產頁與 latch 是 F2 coordinator 評表；本 hop 只留 RP-7（S-1.10）這顆 F1 牙。 | 4-spec S-1.2…S-1.5「n-a:F2 未落地」；S-8.2；本 hop brief 獨立於 A／B | 棄本 slug 實作前進紀錄／請人審 A4 引擎。 |
| S-8.2／S-8.3 零 Files | F2 coordinator、F3 新 slug 預設切線不在本 slug Stage 5–7。 | 4-spec S-8.5／Out of Scope／Diff Budget F2／F3 = 0 | 棄 graph 預設切線 T。棄本 slug 當新 5（4C）。 |
| S-8.4 不派 T | 該 S 量的是 Stage 4 PR 檔集，已在 #315 滿足；本 hop 再派會變成改歷史 diff。 | 4-spec S-8.4；#315 | 棄本 hop 重跑「只含 4-spec 雙檔」當 Stage 5 Verify。 |
| SLOT 只鎖 id＋意思 | T-17 Verify 掃九個 `SLOT-` id，並拒絕 annex 把鍵名寫成 required-key。 | 4-spec S-5.8；OC-3 | 棄在 5-tasks 鎖定 JSON 鍵名。 |
| S-8.6 獨立 T-19 | 重開已拒案是 C 線第二顆主牙，不可埋進 T-20 散文。 | 4-spec S-8.6；DD-8 | 棄只在 Split Decisions 寫「不要重開」而無對照稿。 |
| 不切 G3、不改 STATUS、status 留 draft | owner brief：只寫 Stage 5；5-tasks 不是 gate。 | 本 hop brief；N6 定案權在 owner | 棄本 hop 把 status 轉 approved。棄 STATUS／HISTORY companion。 |
