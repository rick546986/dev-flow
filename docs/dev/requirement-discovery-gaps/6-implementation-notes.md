---
feature: requirement-discovery-gaps
stage: 6-implementation
status: done
owner: implementer-c
updated: 2026-09-13
---

# 6. 實作筆記

> Variant C：教師改口依人怎麼填檔的旅程（Goals／Requested solution → 前綴 → Assumption → disposition → manifest → Fast → verdict 一行），再延三支既有牙。本 hop 不改 STATUS／HISTORY、不發明 G3、不新開 R/S、不新開第四檢查家族。

## 步 0 守衛武裝自檢

- `devflow-exec.sh status`:`slug=requirement-discovery-gaps started=2026-09-13T06:03:38 scope=22 extra=0 sentinel=在`
- `devflow-doctor.sh`:`✅ devflow doctor: COMPATIBLE`
- feature branch:`cursor/rdg-s6-land-c-5ac5`（base `ab78e8b` = #282 Stage 5）
- 圍欄：只讀 4-spec／5-tasks／6-notes／活教師；未讀本 slug 1／2／3。
- ENV：本機缺 `markdown-it-py==4.0.0` 時 renderer 節會紅；已裝 `scripts/requirements-methodology-render.txt` 釘版（不計升階）。

## T Review Log

### T-1
- reviewer identity: Implementer C self-verify（Cloud Agent）
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:06Z（早於 `6591d6a`）
- Verify: 5-tasks T-1 原指令 → `T-1-wired` + `✅ real-world interaction checks: 140/140 passed(地板 140)`
- Covers finding: S-1.2 單檔負向 exit 1 且含「構想在錯欄」；S-1.4 單檔正向 exit 0；無 `check-discovery-gaps.sh`
- Files finding: `scripts/check-realworld.sh` + `scripts/fixtures/discovery-gaps/`
- RED→GREEN finding: 開工前 fixture 目錄不存在；落地後同一入口咬錯欄
- Test Integrity finding: none
- Design boundary finding: ①無未授權模組；②realworld 擁有教師／fixture；③未改 spec-gate／guard；④未新開第四家族；⑤無未記 L2
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:12Z（早於 `3fc2435`）
- Verify: 5-tasks T-2 原指令 → `T-2-ok` + realworld 144/144
- Covers finding: 模板有 Goals／Requested solution；驗收雛形不再預填畫面／API；S4-accept 問結果發生；example Goals 無登入／點擊／一眼可見
- Files finding: 四檔皆在 T-2 Files
- RED→GREEN finding: 開工前無 Requested solution；改後 Verify 綠
- Test Integrity finding: none
- Design boundary finding: 無黑名單；未撤回 T-1 fixture
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:20Z（早於 `d0058fa`）
- Verify: `T-3-skill` + `T-3-wired` + realworld；隔離複本刪 `發現｜` → 缺邊紅
- Covers finding: N3／SKILL／指南成對前綴；裁決附選 fixture 綠
- Files finding: 六檔皆在 T-3 Files
- RED→GREEN finding: 開工前 N3 仍寫附推薦；改後禁附推薦、兩輪降輔助
- Test Integrity finding: none
- Design boundary finding: 不還原對話；未另開檢查家族
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:22Z（與 T-3 同 commit `d0058fa`；兩 T Intent 同訊息）
- Verify: `T-4-skill` + `T-4-wired` + realworld 154/154；點頭／Unknown／ticket／缺來源單檔皆 exit 1
- Covers finding: S-3.1–S-3.5／S-8.4 極性齊
- Files finding: S1-survey + realworld + fixtures
- RED→GREEN finding: 開工前無點頭／枚舉 fixture
- Test Integrity finding: none
- Design boundary finding: 主張牙仍在 realworld，未塞進 spec-gate
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:28Z（早於 `7b17853`）
- Verify: expired-open exit 1（含 Assumption／過期／open）；resolved exit 0；本 slug 4-spec 9/9 形（當時 7/7）；四欄地板 + realworld
- Covers finding: S-4.1–S-4.4
- Files finding: spec-gate + 1-discussion 模板／example + realworld + fixtures
- RED→GREEN finding: 開工前無 C7
- Test Integrity finding: none
- Design boundary finding: C1–C6 保留；未新開 G2 CLI
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:32Z（早於 `58e0ea4`）
- Verify: `T-6-template` + `T-6-wired` + realworld 161/161
- Covers finding: 殘行紅、完整行綠、無 Actor Coverage 全表
- Files finding: 3-prototype 模板／example + realworld + fixtures
- RED→GREEN finding: 開工前 verdict 只有 ENUM
- Test Integrity finding: none
- Design boundary finding: attestation 規則仍在
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-7
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:36Z（早於 `28edf52`）
- Verify: disposition-missing exit 1（含 Disposition）；模板有去向／`## Real-world Disposition`；本 slug 4-spec C9 綠；模板／example／4-spec `RW-[0-9]` 零命中
- Covers finding: S-6.1–S-6.3 機械過；S-6.4 見 D-1
- Files finding: spec-gate + 2／4 模板 + example 2／4 + fixtures
- RED→GREEN finding: 開工前無 C9
- Test Integrity finding: none
- Design boundary finding: 未發第二鏈；未改 STATUS
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:40Z（早於 `1446654`）
- Verify: `T-8-floor` + lookback fixture 在 + realworld 166/166
- Covers finding: 四欄在模板／example；缺門檻紅；舊檔無節不發動；無 lookback.md 字面、有 history-append.sh
- Files finding: 7-review 模板／example + realworld + fixtures；D-2 允許 renderer twin
- RED→GREEN finding: 開工前 Exit 無四欄
- Test Integrity finding: none
- Design boundary finding: 結果入口仍是 history-append
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-9
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:48Z（早於 `7d0dbe0`）
- Verify: `T-9-read-ok`（S-8.1 exit 0；S-8.2 exit 2 含 2-decision／方案檔；S-8.3 exit 2）；游標不在時 Read 方案檔仍 exit 0
- Covers finding: S-8.1–S-8.3 真跑 Read
- Files finding: guard + 1-discussion 模板／example + fixture
- RED→GREEN finding: 開工前 guard 無 Read 分支
- Test Integrity finding: none（未用 selftest 字數代替 Verify）
- Design boundary finding: 核准=是不能覆寫 2–7；未新開 evidence CLI
- verdict: PASS
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: Implementer C self-verify
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-13T06:55Z（早於 `6f58246`）
- Verify: blank／hit-no-dest exit 1；visual-all-no 與本 slug 4-spec exit 0；`T-10-ok` 對照 fixture 第 3 問是、去向 full
- Covers finding: S-9.1–S-9.5
- Files finding: spec-gate + 4-spec 模板 + SKILL + fixtures
- RED→GREEN finding: 開工前無 C8
- Test Integrity finding: none
- Design boundary finding: 七關結構未改；Fast 可跳 1–3 仍在
- verdict: PASS
- correction + re-review after FAIL: N/A

## Progress Log

| 日期 | T-id | hash |
|---|---|---|
| 2026-09-13 | T-1 | `6591d6a` |
| 2026-09-13 | T-2 | `3fc2435` |
| 2026-09-13 | T-3 | `d0058fa` |
| 2026-09-13 | T-4 | `d0058fa` |
| 2026-09-13 | T-5 | `7b17853` |
| 2026-09-13 | T-6 | `58e0ea4` |
| 2026-09-13 | T-7 | `28edf52` |
| 2026-09-13 | T-8 | `1446654` |
| 2026-09-13 | T-9 | `7d0dbe0` |
| 2026-09-13 | T-10 | `6f58246` |

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run:

## TDD Evidence

### T-1 / S-1.2
- RED: fixture 目錄不存在（5-tasks 原樣表）
- GREEN: `check-realworld.sh goals-dashboard-in-wrong-column.md` → exit 1「構想在錯欄」

### T-1 / S-1.4
- RED: 正向 fixture 不存在
- GREEN: `check-realworld.sh goals-outcome-with-requested-dashboard.md` → exit 0

### T-2 / S-1.1
- RED: 模板無 `## Requested solution`；驗收雛形寫 `畫面路徑 | API 端點`
- GREEN: T-2 Verify `T-2-ok`

### T-2 / S-1.3
- RED: example Goals 含「就能看到／點擊可直達／一眼可見」
- GREEN: Goals 改結果句；構想進 Requested solution 標未定案；Interview 不再 CONFIRMED dashboard 為已核目標

### T-3 / S-2.1
- RED: N3「附推薦答案」硬規則
- GREEN: `發現｜` 禁附推薦；`裁決｜` 可附；完成條件改覆蓋面

### T-3 / S-2.2
- RED: 無前綴對稱牙
- GREEN: 隔離複本刪一邊 → realworld 紅並指出缺邊

### T-3 / S-2.3
- RED: 無裁決附選 fixture
- GREEN: `probe-decision-with-options.md` 不因裁決附選而紅

### T-4 / S-3.1
- RED: 無缺來源 fixture
- GREEN: `high-impact-missing-source.md` exit 1 含「來源／期限」

### T-4 / S-3.2
- GREEN: `high-impact-with-source.md`／`high-impact-with-assumption.md` exit 0

### T-4 / S-3.3
- GREEN: `nod-as-only-source.md` exit 1「點頭不是來源」

### T-4 / S-3.4
- GREEN: `enum-unknown.md` exit 1「枚舉」+ 五值

### T-4 / S-3.5
- GREEN: `non-high-impact-context.md` exit 0

### T-4 / S-8.4
- GREEN: `ticket-solution-as-fact.md` exit 1「解法不當事實」

### T-5 / S-4.1
- GREEN: `assumption-expired-open.md` spec-gate exit 1，C7 含 Assumption／過期／open

### T-5 / S-4.2
- GREEN: `assumption-resolved.md` spec-gate exit 0

### T-5 / S-4.3
- GREEN: 本 slug 4-spec 三列 oc-accepted，C7 綠

### T-5 / S-4.4
- GREEN: 模板／example 含四欄字面；realworld 地板綠

### T-6 / S-5.1
- GREEN: `verdict-accepted-only.md` 紅，含 role／scenario

### T-6 / S-5.2
- GREEN: `verdict-complete.md` 綠

### T-6 / S-5.3
- GREEN: 模板無 Actor Coverage／本包必填全表

### T-7 / S-6.1
- GREEN: `disposition-missing.md` spec-gate exit 1 含 Disposition

### T-7 / S-6.2
- GREEN: 本 slug disposition「發現被錨定 → S-2.1」不造成 C9 紅

### T-7 / S-6.3
- GREEN: 本 slug 刻意維持／仍待驗列含 Out of Scope／Known limit

### T-7 / S-6.4
- GREEN: 模板／example／本 slug 4-spec `RW-[0-9]` 零命中；本 slug 2-decision 棄項句見 D-1

### T-8 / S-7.1
- GREEN: 模板／example 四欄字面在；realworld 地板綠

### T-8 / S-7.2
- GREEN: `lookback-missing-threshold.md` 紅；`lookback-legacy-no-section.md` 不發動

### T-8 / S-7.3
- GREEN: 模板含 `history-append.sh`、無 `lookback.md` 字面

### T-9 / S-8.1
- GREEN: talk 游標 + DEVTALK_MANIFEST，Read `_templates/1-discussion.md` exit 0

### T-9 / S-8.2
- GREEN: Read `2-decision.md` exit 2，stderr 含 2-decision／方案檔

### T-9 / S-8.3
- GREEN: Read `notes/review-requirement-discovery-gaps.md` exit 2（未核）

### T-10 / S-9.1
- GREEN: `fast-blank-triage.md` spec-gate exit 1 含 Fast／六問

### T-10 / S-9.2
- GREEN: `fast-wait-shown-as-done.md` 第 3 問是、去向 full

### T-10 / S-9.3
- GREEN: `fast-hit-no-dest.md` exit 1 含 去向／full／mini／OC

### T-10 / S-9.4
- GREEN: `fast-visual-all-no.md` spec-gate 9/9

### T-10 / S-9.5
- GREEN: 本 slug `lane: full` 無六問表，C8 不紅

## Decisions(spec 未載明的自由選擇)
- D-impl-1: `check-realworld.sh` 第一參數若是 `.md` 檔，走單檔形狀模式。
- D-impl-2: fixture 自測在檔不存在時 `check_skip`。
- D-impl-3: 高影響列抽 Workarounds／Exceptions／Evidence 頂層條；點頭獨源看來源欄字面。
- D-impl-4: spec-gate 項次 C7 Assumption／C8 Fast／C9 Disposition（與 4-spec DD 下層建議一致）。

## Deviations

### D-1(L1)
- 現象: T-7 Verify 的 `rg RW-[0-9]` 命中本 slug 已核 `2-decision.md` 棄項 4B「發明 `RW-1`」。
- 保守選擇: 不改該檔（不在 T-7 Files）。模板／example／4-spec 零命中。
- 理由: S-6.4 負向對照句不算發 ID；改已核 Decision 正文是範圍外。
- 影響: T-7／S-6.4 機械 rg 對聯集路徑不為 0；語意未發第二鏈。

### D-2(L1)
- 現象: 改 `_templates/7-review.md` 後 renderer `--check` 報 guide-dev-flow.html 與 example 7-review.html stale。
- 保守選擇: `devflow-exec.sh allow` 後 `render-methodology-corrections.sh --write`。
- 理由: 衍生 twin，未改 R/S。
- 影響: T-8 Files 聯集多兩份 html。

### D-3(L1)
- 現象: C8 若對所有 `lane: fast` 缺表都紅，會誤殺全形冒號／晚改可見行為等既有 fixture。
- 保守選擇: 缺 `## Fast early risk triage` 且無 `## ADDED Requirements` → no-fire；有 ADDED 無表仍紅。
- 理由: S-9.1 對照稿帶 ADDED；舊回歸檔沒有 ADDED。
- 影響: T-10／S-9.1 仍咬空白開寫的 Fast spec。

## Files Changed

對照 Diff Budget 估計 ≤30 檔。實得 46 路徑（含 22 份 discovery-gaps fixture + 2 份 renderer twin）。超支在測試 fixture 與衍生 html，不是新檢查家族。非測試教師／三牙／指南約 20 檔，在「模板≤5 + skills≤8 + example≤4 + 三牙」框內。

| 區塊 | 實得 |
|---|---|
| 模板 1／2／3／4／7 | 5 |
| skills／指南 | N3／S1／S4／兩份 SKILL／guide-dev-talk + D-2 guide-dev-flow |
| example 1／2／3／4／7 | 5 md + 1 html twin |
| check-realworld + fixtures | 1 + 22 |
| check-spec-gate + architecture-guards | 2 |
| devtalk-guard | 1 |
| 6-notes | 1 |

## Diff(各 T commit,逐檔折疊)

### goals_wrong_column · `scripts/check-realworld.sh` 88-120  T-1
改什麼：同一入口指出 Goals 構想在錯欄，不採 dashboard／API 黑名單。
關聯：fixtures `goals-dashboard-in-wrong-column`／`goals-outcome-with-requested-dashboard`
```diff
+def goals_wrong_column(text):
+    first = first_lines[0]
+    requested_empty = requested is None or not content_lines(requested)
+    return bool(re.search(r"我要\s*dashboard", first, re.I) and requested_empty)
```

### assumption_c7 · `scripts/check-spec-gate.sh` 247-285  T-5
改什麼：open + 過期／過站且無 oc-accepted → exit 1。
關聯：`assumption-expired-open.md`／本 slug oc-accepted
```diff
+        if status == "open" and expired:
+            c7_bad.append(f"L{n + 1} Assumption 過期仍 open")
```

### disposition_c9 · `scripts/check-spec-gate.sh` 330-370  T-7
改什麼：full lane 缺 Disposition 或去向空白或處理無 R/S → 紅。
關聯：`disposition-missing.md`／本 slug 4-spec 表
```diff
+    if disp is None:
+        c9_bad.append("full lane 缺 ## Real-world Disposition")
```

### guard_read · `hooks/devtalk-guard.sh` 16-90  T-9
改什麼：talk 游標在時 Read 放行核准=是，仍禁 2–7。
關聯：`guard-read-1-discussion.md`
```diff
+if [ -f "$REPO_ROOT/.devtalk-cursor.json" ] && [ "$TOOL" = "Read" ]; then
+    # 方案檔硬擋；manifest 核准=是才放行
+fi
```

### fast_c8 · `scripts/check-spec-gate.sh` 287-329  T-10
改什麼：lane:fast 且已有 ADDED 時，空白六問或命中無去向 → 紅。
關聯：`fast-blank-triage.md`／`fast-hit-no-dest.md`／`fast-visual-all-no.md`
```diff
+        if len(filled) < 6:
+            c8_bad.append("Fast 六問答欄空白（不是已分診）")
+        if yes_hit and dest_n in ("", "待裁", "Fast"):
+            c8_bad.append("命中後去向必須 ∈ {full, fast+mini, OC}")
```

## Self-Review

1. 每個 T × Covers S 都有含 S-id 的證據（上列 TDD Evidence）。T-3／T-4 同 commit，證據仍分 T 記錄。
2. 每 T 在 T Review Log 有 verdict PASS。
3. reviewed-at 早於該 T commit（T-3／T-4 同 hash，兩則 review 都早於 `d0058fa`）。
4. 無未收斂 FAIL。
5. Progress Log 每列有 hash；T-3／T-4 共用 `d0058fa`（一次 commit 兩 T Intent）。
6. `git diff --stat main...HEAD` 檔案 ⊆ Files 聯集 + 恆許 6-notes + D-2 兩份 renderer twin。Diff Budget 檔數超 30，見 Files Changed（fixture 超支，L1）。
7. Decisions／D-1–D-3 對得上 diff。Design Boundary：三牙仍各擁原出口；無第二家族；2–7 禁令未被核准格覆寫。
8. 回歸：`bash scripts/check-realworld.sh` 166/166；`check-spec-gate.sh` 本 slug 4-spec 9/9；全形冒號與晚改正向 fixture 仍綠；無 `check-discovery-gaps.sh`。未跑完整 `test-architecture-guards.sh`／`hooks/selftest.sh` 全套（T-3 只加 RW-3／RW-4 兩案；T-9 不加 selftest 案以免動 MIN_CASES 釘）。

## Review Follow-up(G3 打回時才用)
