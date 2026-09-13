---
feature: requirement-discovery-gaps
stage: 6-implementation
status: in-review
owner: implementer-a
updated: 2026-09-13
---

# 6. 實作筆記

> Stage 6 land（Implementer A）。基準 `ab78e8b`（#282）。不發明 G3 PASS、不改 STATUS／HISTORY、不重開 Decision／不發明新 R/S。

FORK_INTEGRATION_SHA: ab78e8b90a48c002b6023e806a9bc4f1d7ea5703

## 起手

- 圍欄自查:只讀 4-spec / 5-tasks / 本檔 / living spec（本 repo `docs/specs/` 無條可引）。禁讀 1/2/3。
- branch:`cursor/rdg-s6-land-a-e370` @ `ab78e8b90a48c002b6023e806a9bc4f1d7ea5703`
- 0b worktree 隔離:`n-a:本 feature 未並行`（單一 checkout，無第二棵 worktree／無共用 DB／無共用 queue）
- 0c 守衛與 doctor:見下

## 守衛輸出

`devflow-exec.sh doctor` → `✅ devflow doctor: COMPATIBLE`（契約 2.0.0；runtime 3.23.4）

`devflow-exec.sh start requirement-discovery-gaps` → `✅ 執行守衛啟動:requirement-discovery-gaps`；`run_id=run_01M2CNWD0SFR4BB3G841GN9PDP`；scope 22 項（聯集 Files）。

`devflow-exec.sh status` → `slug=requirement-discovery-gaps … sentinel=在`；收尾 `extra=3`（L1 allow：本 slug `2-decision.md`／`2-decision.html`、renderer twin）。

## T Review Log

### T-1
- reviewer identity:fresh-context Agent（獨立 T review；implementer-A 不自裁 G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`test ! -e scripts/check-discovery-gaps.sh && … T-1-wired && bash scripts/check-realworld.sh` → `T-1-wired`；`構想在錯欄:goals-dashboard-in-wrong-column`；`172/172` 當時（後續 T-4 加針 → 174/174）
- Covers finding:S-1.2／S-1.4 落地為錯欄 fixture + 不採黑名單
- Files finding:只動 realworld + `scripts/fixtures/discovery-gaps/`
- RED→GREEN finding:見 TDD Evidence T-1
- Test Integrity finding:none
- Design boundary finding:無第四家族；MIN_CHECKS=實數；realworld≠Assumption G2
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`T-2-ok` + realworld 綠
- Covers finding:S-1.1／S-1.3 模板分欄＋example Goals 改口
- Files finding:四檔內
- RED→GREEN finding:見 TDD Evidence T-2
- Test Integrity finding:none
- Design boundary finding:無 dashboard／API 黑名單；未撤 T-1 fixture
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`T-3-skill`／`T-3-wired`；guide-dev-talk 原文同步 PASS
- Covers finding:S-2.1／S-2.2／S-2.3；S-2.2 突變在 `test-architecture-guards.sh` RW-DG1／RW-DG2
- Files finding:六檔內
- RED→GREEN finding:見 TDD Evidence T-3
- Test Integrity finding:none
- Design boundary finding:無第二問句正本；牙不還原對話
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:22Z（round 1 FAIL）／2026-09-13T06:25Z（round 2 PASS）
- Verify:round 2 `T-4-skill`／`T-4-wired`；realworld **174/174**
- Covers finding:round 1 缺 S-3.1「使用者反映」針；round 2 補 `user-report-only.md` + `_is_high_impact` 去掉 `or True`；S-8.3 填檔半邊 `unapproved-as-only-source.md`
- Files finding:三檔＋fixture 目錄
- RED→GREEN finding:見 TDD Evidence T-4；round 1 integrity ⑥
- Test Integrity finding:round 2 none
- Design boundary finding:過期假設未塞進 realworld；同一主張牙
- verdict:PASS（round 2）
- correction + re-review after FAIL:補 S-3.1／S-8.3 填檔對照稿與掃描範圍（Exceptions／痛點，不要求先有狀態+風險=高）

### T-5
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:expired-open C7 exit 1；resolved + 本 slug 4-spec 9/9；`T-5-floor`
- Covers finding:S-4.1～S-4.4
- Files finding:五檔內
- RED→GREEN finding:見 TDD Evidence T-5
- Test Integrity finding:none
- Design boundary finding:C1–C6 保留；無第二 G2 CLI
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-6
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`T-6-template`／`T-6-wired`
- Covers finding:S-5.1／S-5.2／S-5.3；無 Actor Coverage 全表
- Files finding:四檔內
- RED→GREEN finding:見 TDD Evidence T-6
- Test Integrity finding:none
- Design boundary finding:attestation 仍在
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-7
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:disposition-missing C9 exit 1；`T-7-template`；`rg RW-[0-9]` = 0；本 slug 4-spec 9/9
- Covers finding:S-6.1～S-6.4
- Files finding:T-7 Files 內；另 L1 本 slug `2-decision.md`（4B 去 `RW-1`）+ twin html
- RED→GREEN finding:見 TDD Evidence T-7
- Test Integrity finding:none
- Design boundary finding:無第二鏈；C9 缺表只對 full 新式（D-impl-3）
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-8
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`T-8-floor`；`lookback.md` 不在模板；`history-append.sh` 在
- Covers finding:S-7.1／S-7.2／S-7.3
- Files finding:四檔內；L1 renderer twins：`guides/guide-dev-flow.html`、`example/…/7-review.html`
- RED→GREEN finding:見 TDD Evidence T-8
- Test Integrity finding:none
- Design boundary finding:不另造 lookback 永久檔
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-9
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:22Z（round 1 FAIL）／2026-09-13T06:25Z（round 2 PASS）
- Verify:`T-9-read-ok`（S-8.1 exit 0／S-8.2 exit 2／S-8.3 exit 2）；無殘留 `.devtalk-cursor.json`；selftest 459/459
- Covers finding:round 1 只靠 `DEVTALK_MANIFEST`、無 env 時未核不擋；round 2 另掃 `docs/dev/*/1-discussion.md`
- Files finding:五檔內；MIN_CASES 靜態釘在 `test-architecture-guards.sh`（與 T-3 同檔記帳）
- RED→GREEN finding:見 TDD Evidence T-9
- Test Integrity finding:round 2 none
- Design boundary finding:2–7 仍禁；無 `check-evidence-allow.sh`
- verdict:PASS（round 2）
- correction + re-review after FAIL:游標在時讀同檔 manifest；env 仍作 Verify 縫

### T-10
- reviewer identity:fresh-context Agent
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:fast-blank／fast-hit-no-dest C8 exit 1；visual-all-no + 本 slug 4-spec 9/9；`T-10-ok`
- Covers finding:S-9.1～S-9.5
- Files finding:四檔內
- RED→GREEN finding:見 TDD Evidence T-10
- Test Integrity finding:none
- Design boundary finding:僅 lane:fast 發動；Fast 仍可跳過 1–3
- verdict:PASS
- correction + re-review after FAIL:N/A

獨立 T review 總評:T-1…T-10 PASS。**不是 G3。**

## Progress Log

- 2026-09-13 | T-1..T-10 | 901bbcce4a3924e1f39978b225c012c7f44eb925 docs+chore(requirement-discovery-gaps): Stage 6 land (A)

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run: n-a（sequential v1 start，無 run_id 事件通道）

## TDD Evidence

### T-1 / S-1.2
- RED: 5-tasks 開工前表 — `scripts/fixtures/discovery-gaps/` 不存在；realworld 無錯欄針。stub detector 時錯欄 fixture 不紅。
- GREEN: `T-1-wired`；stdout `構想在錯欄:goals-dashboard-in-wrong-column`；`test ! -e scripts/check-discovery-gaps.sh`

### T-1 / S-1.4
- RED: 同上（無 outcome+Requested 對照）
- GREEN: `goals-outcome-with-requested-dashboard` 不因 dashboard／API 誤殺；`detect_goals_wrong_column` 只咬空 Requested +「我要 」開頭

### T-2 / S-1.1
- RED: 模板無 `## Requested solution`；Goals／驗收雛形仍 `畫面路徑 | API 端點`
- GREEN: `T-2-ok`；realworld 地板 check 綠

### T-2 / S-1.3
- RED: example Goals 仍把登入／點擊／一眼可見當目標
- GREEN: Goals 無那三詞；構想只在 Requested solution

### T-3 / S-2.1
- RED: N3「附推薦答案」；無 `發現｜`／`裁決｜`
- GREEN: `T-3-skill`；`禁附推薦`；SKILL／guide 同步 PASS

### T-3 / S-2.2
- RED: 隔離 seed 無 N3；刪一邊前綴不紅
- GREEN: seed 複製 N3；RW-DG1／RW-DG2 `expect fail`；EXPECTED_TOTAL 144→146

### T-3 / S-2.3
- RED: 無 `probe-decision-with-options.md`
- GREEN: 裁決附選項不當發現題違規

### T-4 / S-3.1
- RED: 獨立 review — `_claim_problems` 要先有狀態+風險=高；無「使用者反映」針；`_is_high_impact … or True`
- GREEN: `user-report-only.md`；check 名含 `來源`；174/174

### T-4 / S-3.2
- RED: 無 Observed+path／Assumption+期限內嵌綠針
- GREEN: `_good_obs`／`_good_assume` `not _claim_problems`

### T-4 / S-3.3
- RED: 無 `nod-as-only-source.md`；S1 仍「認可後的清單 = 已核事實」
- GREEN: `T-4-skill`；點頭獨源必紅

### T-4 / S-3.4
- RED: 無 `enum-unknown.md`
- GREEN: Unknown → `枚舉`

### T-4 / S-3.5
- RED: 無「普通 Context 不貼枚舉仍綠」對照
- GREEN: `_low` 不紅

### T-4 / S-8.4
- RED: 無 ticket 解法 fixture
- GREEN: `ticket-solution-as-fact.md` → 解法／不當事實

### T-5 / S-4.1
- RED: `assumption-expired-open.md` 不存在；spec-gate 無 C7
- GREEN: C7 `Assumption 過期仍 open(2020-01-01)`；exit 1

### T-5 / S-4.2
- RED: 無 resolved 對照
- GREEN: `assumption-resolved.md` 9/9

### T-5 / S-4.3
- RED: 本 slug oc-accepted 列可能被新項誤殺
- GREEN: `docs/dev/requirement-discovery-gaps/4-spec.md` 9/9

### T-5 / S-4.4
- RED: 模板／example 無四欄
- GREEN: `T-5-floor`；realworld 四欄地板

### T-6 / S-5.1
- RED: 無 `verdict-accepted-only.md`；模板無 `role=`／`scenario=`
- GREEN: `T-6-template`／`T-6-wired`；殘行必紅

### T-6 / S-5.2
- RED: 完整一行無綠針
- GREEN: `ACCEPTED | role=… | scenario=…` 放行

### T-6 / S-5.3
- RED: 模板可能被寫成 Actor Coverage 全表
- GREEN: `本包必填全表`／`Actor Coverage` 不在模板

### T-7 / S-6.1
- RED: 無 `disposition-missing.md`；模板無 Disposition
- GREEN: C9 `full 缺表`；exit 1

### T-7 / S-6.2
- RED: 本方案處理無 R/S 下落不擋
- GREEN: C9 下落匹配 `R-`／`S-`；本 slug 4-spec 9/9

### T-7 / S-6.3
- RED: example／模板無去向表
- GREEN: `T-7-template`

### T-7 / S-6.4
- RED: 本 slug 2-decision 4B 含 `` `RW-1` ``
- GREEN: `rg RW-[0-9]` 指定六檔 = 0（L1 改 4B 為「第二鏈編號」）

### T-8 / S-7.1
- RED: 模板／example 無回看四欄
- GREEN: `T-8-floor`

### T-8 / S-7.2
- RED: 無 `lookback-missing-threshold.md`
- GREEN: shipped 有回看節缺「低於何值重開」必紅；舊檔無節 no-fire

### T-8 / S-7.3
- RED: 可能另造 lookback 檔
- GREEN: 模板無 `lookback.md` 字樣；有 `history-append.sh`

### T-9 / S-8.1
- RED: 無 Evidence manifest；guard 無 Read 分支。round 1：無 env 時核准列不讀 1-discussion
- GREEN: `T-9-read-ok` exit 0；無 env 時掃 `docs/dev/*/1-discussion.md`；selftest 同檔 是→0

### T-9 / S-8.2
- RED: 方案檔誤寫核准=是可能放行
- GREEN: Read 2-decision exit 2；stderr 含方案檔字樣

### T-9 / S-8.3
- RED: 未核路徑無 env 時 default-allow；填檔牙不咬未核來源
- GREEN: Read 未核 exit 2；`unapproved-as-only-source.md` 主張牙含 `來源`

### T-10 / S-9.1
- RED: 無 `fast-blank-triage.md`
- GREEN: C8 `六問缺表`；exit 1

### T-10 / S-9.2
- RED: 無 `fast-wait-shown-as-done.md`
- GREEN: `T-10-ok`；Q3 是＋等待被顯示成完成；去向 `fast+mini` ≠ Fast；無待裁

### T-10 / S-9.3
- RED: 命中無去向不擋
- GREEN: `fast-hit-no-dest.md` C8 待裁／Fast 紅；exit 1

### T-10 / S-9.4
- RED: 全否純視覺可能被誤殺
- GREEN: `fast-visual-all-no.md` 9/9

### T-10 / S-9.5
- RED: 本 slug full 可能被 Fast 項誤殺
- GREEN: 4-spec C8 `full 缺表 no-fire`；9/9

## Decisions(spec 未載明的自由選擇)

- D-impl-1:isolated seed 沒有 `scripts/fixtures/discovery-gaps/` 時，`check-realworld.sh` 用同形內嵌對照跑同一批 `check()`，不新增 `check_skip(`（`EXPECTED_CHECK_SKIP_CALLS = 1` 釘死且該檔不在本 feat Files）。依據:`scripts/check-design-contract.sh` EXPECTED_CHECK_SKIP_CALLS；N-2 兩環境檢查數一致。
- D-impl-2:C8 Fast 缺表只對 `lane: fast` 且具 `feature:`＋`## ADDED Requirements` 的 4-spec 發動；既有回歸 fixture（全形冒號、late-owner）grandfather。依據:Compatibility「C1–C6 保留；只加項」；T-10 Files 不含那些 fixture。
- D-impl-3:C9 缺 Disposition 只對 `lane: full` 且（有 `## Assumption refs` 或路徑含 `discovery-gaps`）發動；`example/subsidy-3-0-plus/4-spec.md` grandfather。依據:該檔在 CI spec-gate 名單但不在 T-7 Files。

## Deviations

### D-1(L1)
- 現象:T-7 Verify `rg 'RW-[0-9]'` 含本 slug `2-decision.md`；4B 駁回列原文有 `` `RW-1` ``。
- 保守選擇:`devflow-exec.sh allow` 後把 4B 改成「第二鏈編號」。不改 4A、不重開 Decision。
- 理由:S-6.4 觀測是指定檔零命中；負向對照句改述仍表達已拒 4B。
- 影響:T-7 / R-6 / S-6.4（測法收斂，契約「不發第二鏈」不變）

### D-2(L1)
- 現象:T-8 改 `_templates/7-review.md` 後 renderer `--check` 與 `guides/guide-dev-flow.html`、`example/contract-expiry-reminder/7-review.html` 不同步。
- 保守選擇:`allow` + `render-methodology-corrections.sh --write` 重生那兩份 twin。
- 理由:母版要求教師改完重建 html twin；不改 Exit 語意。
- 影響:無 R/S 變更。T-8 Files 不含那兩份 html。

### D-3(L1)
- 現象:4B 改口後本 slug `2-decision.html` 仍殘 `RW-1`。
- 保守選擇:`build-gate-twin.py … 2-decision` 重生 twin。
- 理由:gate twin 必須跟 md 正本走；Verify `rg` 只掃 md。
- 影響:無 R/S 變更。

### D-4(L1)
- 現象:T-9 加 Read 案後 `MIN_CASES` 454→457→459；`test-architecture-guards.sh` 靜態釘必須同步，否則 PF 類互釘假綠／假紅。
- 保守選擇:同步 `MIN_CASES=459` 與 `check_static_pin`。
- 理由:母版記帳，不是新 R/S。T-3 Files 已含該檔。
- 影響:無 R/S 變更。

### D-5(L1)
- 現象:Exit 加回看表後,`template7-exit-quickstart` 的 markdown_visible 留下 `###`,HTML `<h3>` 可見文字沒有。CI methodology 122/123。
- 保守選擇:教師保留「回看約定」四欄,不用 `###` ATX(parity 才能過)。`renderer --write` 重生 guide twin。
- 理由:不改 checker;T-8 Verify 不要求 `###`。
- 影響:T-8 / R-7 / S-7.1(欄位字面不變)

### D-6(L1)
- 現象:隔離 seed 沒有 `scripts/fixtures/discovery-gaps/`;舊 embed 沒有 `- 狀態:` 前綴,`_field` 吃不到,S-3.3／S-3.4／S-8.4 在 RW-0 對照組紅。
- 保守選擇:embed 改成與 fixture 同形(`### Exceptions` + `- 狀態:`)。不新增 `check_skip(`。
- 理由:D-impl-1;EXPECTED_CHECK_SKIP_CALLS 仍 1。
- 影響:無 R/S 變更。T-4 隔離與正式 repo 同針。

### D-7(L1)
- 現象:RW-DG1／RW-DG2 兩個 `mutate <<'PY'` 讓 CI 實得 heredoc 223;`MIN_HEREDOCS` 221 時 PF-2 漏收一枚仍 ≥221 → 假綠。
- 保守選擇:`MIN_HEREDOCS` 與靜態釘改 223。
- 理由:與 diagram-ir-gate D-4 同形母版記帳。
- 影響:無 R/S 變更。

## Files Changed

對照 Diff Budget（估計合計 ≤30 檔）：落地教師 1／2／3／4／7 + skills／指南 + example 改口 + 三支牙 + `scripts/fixtures/discovery-gaps/` + `test-architecture-guards.sh` + 本檔／html。L1：本 slug `2-decision.md`／`.html`、`guides/guide-dev-flow.html`、example `7-review.html`。未改 STATUS／HISTORY／plugin；無 `scripts/check-discovery-gaps.sh`。

行數（工作樹相對 `ab78e8b`，含測試／fixture）：教師與牙約 +600／−30；fixture 目錄另增對照稿。未明顯超 Budget 檔數上限；realworld 非測試增量略超「≤120」估計 → 判 L1（不動 R/S；針都是 S 對照）。

## Diff(各 T commit,逐檔折疊)

### detect_goals_wrong_column · `scripts/check-realworld.sh` 259-272  T-1
改什麼：Goals 第一句「我要 …」且 Requested solution 空 → 構想在錯欄；不掃 dashboard／API 黑名單
關聯：caller 第 11 節 check()／對照 `_EMBED_WRONG`／`_EMBED_OK`
```diff
+def detect_goals_wrong_column(source):
+    goals = _section_after(source, "## Goals")
+    requested = _section_after(source, "## Requested solution")
+    first = _first_goal_line(goals)
+    requested_empty = requested is None or not re.sub(
+        r"<!--.*?-->", "", requested, flags=re.S).strip()
+    if not first or not requested_empty:
+        return False
+    return first == "我要 dashboard" or first.startswith("我要 ")
```

### teacher Goals floor · `scripts/check-realworld.sh` 294-304  T-2
改什麼：模板／example 必須有 Requested solution；Goals 不再預填畫面／API
關聯：讀 `t1`／`e1`；不撤 T-1 fixture
```diff
+check("## Requested solution" in t1, "template 1-discussion 含 ## Requested solution")
+check("畫面路徑 | API 端點" not in (_section_after(t1, "## Goals") or ""),
+      "template Goals 不再預填畫面／API 通道")
```

### N3 完成條件 · `skills/dev-talk/nodes/N3-probe.md` 21-45  T-3
改什麼：發現｜禁附推薦、裁決｜可附選項；兩輪改標輔助
關聯：SKILL 入口摘要／guide-dev-talk 原文同步
```diff
-①一次只問一題、附推薦答案,同題多種解讀 → 列差異讓使用者選、**禁默選**;
+①一次只問一題。兩條路徑硬規則:
+- `發現｜` 現況／案例／例外／證據:開放題,禁附推薦。
+- `裁決｜` 已核事實上的取捨:可附本方案／Non-Goal／另開 slug 等選項與差異。
```

### seed · `scripts/test-architecture-guards.sh` 189-195  T-3
改什麼：隔離複本帶上 N3，刪一邊前綴才驗得到
關聯：RW-DG1／RW-DG2 `expect fail check-realworld.sh`
```diff
+  mkdir -p "$dst/skills/dev-talk/nodes"
+  cp "$ROOT/skills/dev-talk/nodes/N3-probe.md" "$dst/skills/dev-talk/nodes/"
```

### _claim_problems · `scripts/check-realworld.sh` 364-410  T-4
改什麼：掃 Exceptions／痛點；「使用者反映」或缺來源期限 → 來源；未核不得當 Observed 來源
關聯：fixtures `user-report-only`／`nod`／`enum`／`ticket`／`unapproved`
```diff
+            bare = (not status and not source and not deadline
+                    and block.strip().startswith("-") and len(block.strip()) > 3)
+            if "使用者反映" in block or bare:
+                if "path:" not in block and not deadline:
+                    problems.append("來源")
```

### C7 Assumption refs · `scripts/check-spec-gate.sh` 251-292  T-5
改什麼：open + 過去日或 stage-2／stage-3 → FAIL；resolved／oc-accepted 放行
關聯：`_md_rows`／C8／C9 同檔加項
```diff
+        if status == "open" and expired:
+            c7_bad.append(f"L{n + 1}:Assumption 過期仍 open({deadline})")
```

### _accepted_missing_role_scenario · `scripts/check-realworld.sh` 427-441  T-6
改什麼：Human verdict ACCEPTED 缺 role=／scenario= 必紅
關聯：template／example 一行格式；不要求 Actor Coverage 全表
```diff
+        if re.search(r"Human verdict:\s*ACCEPTED\b", line):
+            if "role=" not in line or "scenario=" not in line:
+                return True
```

### C9 Disposition · `scripts/check-spec-gate.sh` 348-372  T-7
改什麼：full 新式缺表或本方案處理無 R/S → FAIL
關聯：D-impl-3 fire 條件；fixture `disposition-missing.md`
```diff
+fire_disp = prof["lane"] == "full" and (
+    assume_i is not None or "discovery-gaps" in spec_path)
```

### 回看約定 · `_templates/7-review.md` 342-349  T-8
改什麼：Exit 加四欄；結果走 history-append.sh；不出現 lookback.md
關聯：example 7-review；realworld `_LOOKBACK`
```diff
+### 回看約定
+| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
```

### _manifest_texts · `hooks/devtalk-guard.sh` 41-85  T-9
改什麼：Read 分支；2–7 硬擋；env 或 `docs/dev/*/1-discussion.md` 的核准格
關聯：selftest S-8.1～S-8.3；Verify `DEVTALK_MANIFEST`
```diff
+    docs = root / "docs" / "dev"
+    if docs.is_dir():
+        for p in docs.glob("*/1-discussion.md"):
+            if "## Evidence manifest" in text:
+                yield text
```

### C8 Fast triage · `scripts/check-spec-gate.sh` 294-346  T-10
改什麼：僅新式 fast 缺表／答空白／命中去向空白或待裁或 Fast → FAIL
關聯：D-impl-2；template `## Fast early risk triage` 在 ADDED 前
```diff
+fire_fast = prof["lane"] == "fast" and has_feature and added_i is not None
+    if hit:
+        if not dest or dest == "待裁" or dest == "Fast":
+            c8_bad.append("命中後去向須 ∈ {full, fast+mini, OC}…")
```

### Fast lane 入口 · `skills/dev-flow/SKILL.md` 34-36  T-10
改什麼：進 4 前六問；命中由 owner 裁；全否仍可跳過 1–3
關聯：spec-gate C8；4-spec 模板六問表
```diff
+- **fast**:…→ **進 4 前六問**(Fast early risk triage:…)。命中由 owner 裁…
```

## Self-Review

①每個 T×S 都有含 S-id 的測試 + 該 T 自己的 RED→GREEN？是。見 TDD Evidence（T-4／T-9 各有 round 1 FAIL 後補針）。
②每 T 在 T Review Log 有 verdict？是。T-1…T-10 皆 PASS（獨立 Agent；T-4／T-9 第二 round）。
③每個 PASS 都早於該 T commit？是。Verify＋獨立 review 先於本 hop commit。
④每個 FAIL 後有較晚 PASS？T-4／T-9 有；其餘無 FAIL。
⑤每個已完成 T 一 commit、Progress Log 有 hash？本 hop 十 T 同一落地 commit（sequential 單代理）；hash 入 Progress Log。
⑥git diff --stat ⊆ Files 聯集？產品檔是。6-notes 恆許。L1 D-1…D-4 見 Deviations。未改 STATUS／plugin。
⑦Decisions/Deviations 與 diff 對得上？是。D-impl-1..3 與 C8／C9／內嵌稿對得上。Design Boundary：無未授權模組、無改 Data Owner、Interface 即三支牙加項／manifest↔guard；未「修掉」known limit ①②。
⑧回歸綠？realworld 174/174；spec-gate 本 slug 4-spec 9/9；selftest 459/459；guide-dev-talk sync PASS；renderer `--check` 4/4。`test-architecture-guards.sh` 全套因環境缺 Python 3.9–3.11（PF-0）＋未提交指紋未能在髒樹當正式綠；EXPECTED_TOTAL 已改 146。不發明 G3。

## Review Follow-up(G3 打回時才用)
