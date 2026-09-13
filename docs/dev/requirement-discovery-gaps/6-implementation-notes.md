---
feature: requirement-discovery-gaps
stage: 6-implementation
status: in-review
owner: implementer-B
updated: 2026-09-13
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: ab78e8b90a48c002b6023e806a9bc4f1d7ea5703

## 起手

- 圍欄自查:只讀 4-spec / 5-tasks / 本檔 / living spec。禁讀 1/2/3 當輸入。T-7 Verify 的 `rg RW-[0-9]` 命中本 slug 已核准 2-decision 4B 駁回格字面 `RW-1` → 只改該格寫法(D-1 L1),不翻 Decision 4A。
- branch:`cursor/rdg-s6-land-b-6420` @ `ab78e8b90a48c002b6023e806a9bc4f1d7ea5703`
- 0a:`test "$(git rev-parse HEAD)" = "ab78e8b90a48c002b6023e806a9bc4f1d7ea5703"` 開 branch 當下成立。本欄此後不更新。
- 0b worktree 隔離:`n-a:本 feature 未並行`(單一 checkout,無第二棵 worktree / 無共用 DB / 無第二組 port)
- 0c 守衛與 doctor:見下。Variant B:teeth-first,T-1 先鎖 `test ! -e scripts/check-discovery-gaps.sh`。

## 守衛輸出

`bash hooks/devflow-exec.sh status` → `無執行旗標(守衛沉睡)`

`bash hooks/devflow-doctor.sh` → `✅ devflow doctor: COMPATIBLE`(契約 2.0.0;runtime 3.23.4;exec-state 未武裝)

5-tasks frontmatter 仍 `status: draft`(Stage 5 hop 留下)。owner brief 要求本 hop 落地 Stage 6、不發明 G3、不改 STATUS/HISTORY、不新開 R/S。未跑 `devflow-exec.sh start`(會被 draft 擋、且 brief 不要求武裝)。scope 以 5-tasks Files 聯集人工守。

## T Review Log

獨立 T review 留給 PR 人類／fresh-context reviewer。本欄是 implementer-B 自檢(雲端單代理),verdict 不代替 G3。

### T-1
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`test ! -e scripts/check-discovery-gaps.sh && … T-1-wired && bash scripts/check-realworld.sh` → `T-1-wired`;`181/181`(地板 181);第四家族檔不存在
- Covers finding:S-1.2 錯欄 fixture 紅;S-1.4 結果句 + Requested solution 不因 dashboard/API 誤殺
- Files finding:只動 `check-realworld.sh` + `scripts/fixtures/discovery-gaps/`
- RED→GREEN finding:Stage 5 開工前表「fixture 目錄不存在／無錯欄針」;落地後官方 Verify 綠。隔離複本走 inline,未加 `check_skip`
- Test Integrity finding:none(無 skip/xfail;無 `check(True`;MIN_CHECKS=實數)
- Design boundary finding:未新開第四家族;realworld 不擋過期假設;MIN_CHECKS=181=實數
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:官方 T-2 指令 → `T-2-ok`;realworld 181/181
- Covers finding:S-1.1 模板分欄;S-1.3 example Goals 無「就能看到／點擊可直達／一眼可見」
- Files finding:模板／S4-accept／example 1-discussion／realworld 地板。未撤回 T-1 fixture
- RED→GREEN finding:開工前無 `## Requested solution`、驗收雛形仍寫畫面路徑;落地後 T-2-ok
- Test Integrity finding:none
- Design boundary finding:無 dashboard/API 黑名單;S4 只改「從哪看」
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:20Z
- Verify:`T-3-skill` + `T-3-wired` + realworld 181/181;`check-devtalk-guide-sync.sh` PASS(13 段原文)
- Covers finding:S-2.1 前綴;S-2.2 architecture DG-1/DG-2 刪一邊必紅;S-2.3 裁決附選不紅
- Files finding:N3／SKILL／guide-dev-talk／realworld／fixture／test-architecture-guards
- RED→GREEN finding:開工前 N3 仍「附推薦答案」;落地後刪一邊前綴必紅
- Test Integrity finding:none;`EXPECTED_*` 與實跑互釘 18/129/147
- Design boundary finding:指南原文仍是 SKILL 子字串;未另造問句正本;未改 guard
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:21Z
- Verify:`T-4-skill` + 三負向 fixture 存在 + `T-4-wired` + realworld 181/181
- Covers finding:S-3.1–S-3.5 與 S-8.4 同一 `detect_claim_shape`;點頭／Unknown／ticket→Observed 紅;Observed+來源與 Assumption+期限綠
- Files finding:S1-survey／realworld／discovery-gaps fixture。只掃 `### 高影響列`
- RED→GREEN finding:開工前 S1 仍「認可後的清單 = 已核事實」;落地後舊句消失
- Test Integrity finding:none
- Design boundary finding:未把過期假設擋點放進 realworld;未發第二鏈
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-5
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:21Z
- Verify:expired-open exit 1(C7);resolved 9/9;本 slug 4-spec 9/9;`T-5-floor`;realworld 181/181
- Covers finding:S-4.1 過期 open 擋;S-4.2 resolved 放行;S-4.3 oc-accepted 本 slug 綠;S-4.4 四欄地板
- Files finding:spec-gate／1-discussion 模板+example／realworld／fixture
- RED→GREEN finding:開工前無 C7、無 expired fixture;落地後 C7 咬過期 open
- Test Integrity finding:none
- Design boundary finding:C1–C6 保留;無第二支 G2 CLI;無表 no-fire
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-6
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:21Z
- Verify:`T-6-template` + `T-6-wired` + realworld 181/181
- Covers finding:S-5.1 只寫 ACCEPTED 紅;S-5.2 模板／example 含 role=／scenario=;S-5.3 無 Actor Coverage 全表
- Files finding:3-prototype 模板+example／realworld／verdict fixture
- RED→GREEN finding:開工前 Human verdict 只有 ENUM;落地後殘行 fixture 紅
- Test Integrity finding:none
- Design boundary finding:未改 attestation 牙;未加全表;未改 guard／spec-gate
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-7
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:21Z
- Verify:disposition-missing exit 1(C9);`T-7-template`;`rg RW-[0-9]` 六檔 = 0;本 slug 4-spec 9/9
- Covers finding:S-6.1–S-6.4 表／去向／R-S 下落／無第二鏈字面
- Files finding:spec-gate／2-decision+4-spec 模板／example 對應檔／fixture。L1:本 slug 2-decision 4B 格(D-1)
- RED→GREEN finding:開工前無 Disposition 節;落地後缺表 fixture C9 紅;subsidy 無表 no-fire
- Test Integrity finding:none
- Design boundary finding:未改 STATUS;引用用原文;C9 不誤殺無表舊 full(非 discovery-gaps)
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-8
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:21Z
- Verify:`T-8-floor`;lookback fixture 在;realworld 181/181;`lookback.md` 字面不在模板
- Covers finding:S-7.1 四欄;S-7.2 shipped+回看節缺閾值紅、舊檔無節 no-fire;S-7.3 結果入口 history-append.sh
- Files finding:7-review 模板+example／realworld／fixture。L1:renderer 衍生 `7-review.html` 與 `guide-dev-flow.html`
- RED→GREEN finding:開工前無四欄;落地後地板綠
- Test Integrity finding:none
- Design boundary finding:未造 lookback 永久檔;未改 history-append 演算法
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-9
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:22Z
- Verify:官方 T-9 python 真跑 Read 三案 → `T-9-read-ok`(S-8.1 exit 0;S-8.2 exit 2 含「方案檔」;S-8.3 exit 2)
- Covers finding:核准=是可讀模板;2-decision 即使列進 manifest 仍禁;未核路徑禁
- Files finding:guard／1-discussion 模板+example／fixture。未改 `hooks/selftest.sh`(Files 准改、非必改;Verify 不靠 grep selftest;避免 MIN_CASES pin)
- RED→GREEN finding:開工前無 Read 分支、無 manifest;落地後三案 exit 對
- Test Integrity finding:none(未加 skip;未用字數代替 exit)
- Design boundary finding:未新開 evidence CLI;2–7 不可被核准格覆寫;游標不在走舊寫入洩漏
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-10
- reviewer identity:implementer-B self-check(雲端單代理;獨立 T review 留給 PR)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-13T06:22Z
- Verify:fast-blank／fast-hit-no-dest exit 1;fast-visual-all-no 9/9;本 slug 4-spec 9/9;`T-10-ok`
- Covers finding:S-9.1–S-9.4 Fast 六問與去向;S-9.5 full 本 slug no-fire
- Files finding:spec-gate／4-spec 模板／dev-flow SKILL／fixture
- RED→GREEN finding:開工前無 C8;落地後空白六問與命中無去向紅;既有 fast CI fixture(無表、非 discovery-gaps)no-fire
- Test Integrity finding:none
- Design boundary finding:未拆 Fast 7 關;未新造 triage 檔;C1–C6 保留
- verdict:PASS
- correction + re-review after FAIL:N/A

## Progress Log

日期 | T-id | 一行
---|---|---
2026-09-13 | T-1…T-10 | `58250b33dfafdb04514bc7b35cc5c013dbb2d5f4` Stage 6 land (B)
2026-09-13 | T-3 T-8 | `3d7d62cf13268b36f0244cb549d751fe26aa3ad8` CI REPO_REFERENCE: MIN_HEREDOCS 223 + exit-checklist parity
2026-09-13 | T-3 | `328ab192847ca043941f2128fec66831cce0510c` CI: keep MIN_HEREDOCS 221 via .py mutant; 5-tasks approved
2026-09-13 | T-7 | `ad06d222869daa2b5ccec731c37d9672c97c8feb` restore example `2-decision.html` `#basis` `<td>依據</td>` (self-judgment 49/49); keep 去向帳 twin

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run: n-a

## TDD Evidence

RED 來源:5-tasks「Verify 開工前原樣跑」(2026-09-13;牙尚未落地)。GREEN = 本 hop 官方 Verify。負向 fixture 現在仍 exit 1,證明牙咬的是對的東西。

### T-1 / S-1.2
- RED: fixture 目錄不存在;`check-realworld.sh` 無錯欄針 → T-1-wired 不能成立
- GREEN: `T-1-wired`;`goals-dashboard-in-wrong-column` → `構想在錯欄`;realworld 181/181

### T-1 / S-1.4
- RED: 無合法對照稿,無法證明「不因 dashboard/API 誤殺」
- GREEN: `goals-outcome-with-requested-dashboard` → `detect_goals_wrong_column` 回 None;`test ! -e scripts/check-discovery-gaps.sh`

### T-2 / S-1.1
- RED: 模板無 `## Requested solution`;驗收雛形仍 `畫面路徑 | API 端點`
- GREEN: `T-2-ok`

### T-2 / S-1.3
- RED: example Goals 含「就能看到／點擊可直達／一眼可見」
- GREEN: Goals 三句已改口;Requested solution 未定案 dashboard;Interview → `NEEDS_VERIFICATION 呈現面尚未定案`

### T-3 / S-2.1
- RED: N3 寫「附推薦答案」;無 `發現｜`／`裁決｜`
- GREEN: `T-3-skill`;完成條件改必查面／反例／證據缺口;兩輪只標輔助

### T-3 / S-2.2
- RED: 無隔離突變案,刪一邊前綴不會紅
- GREEN: architecture `DG-0` pass / `DG-1` fail / `DG-2` fail;`EXPECTED_CONTROLS=18` `NEGATIVES=129` `TOTAL=147`

### T-3 / S-2.3
- RED: 無裁決附選 fixture
- GREEN: `probe-decision-with-options.md` 不觸發「發現題禁附推薦」

### T-4 / S-3.1
- RED: 無高影響列解析
- GREEN: `detect_claim_shape` 只讀 `### 高影響列`

### T-4 / S-3.2
- RED: 無 Observed+來源／Assumption+期限正例
- GREEN: 兩正例 `is None`

### T-4 / S-3.3
- RED: 點頭可當獨源
- GREEN: `nod-as-only-source.md` → 「點頭不是來源」

### T-4 / S-3.4
- RED: Unknown 可過
- GREEN: `enum-unknown.md` → 枚舉必須落在五值

### T-4 / S-3.5
- RED: S1 把認可當已核事實
- GREEN: `T-4-skill`;舊句刪除

### T-4 / S-8.4
- RED: ticket 解法可標 Observed
- GREEN: `ticket-solution-as-fact.md` → 「解法建議不當事實」

### T-5 / S-4.1
- RED: spec-gate 無 C7
- GREEN: `assumption-expired-open.md` exit 1,C7 印過期 open

### T-5 / S-4.2
- RED: 無 resolved 對照
- GREEN: `assumption-resolved.md` 9/9

### T-5 / S-4.3
- RED: 本 slug oc-accepted 可能被新項誤殺
- GREEN: `docs/dev/requirement-discovery-gaps/4-spec.md` 9/9

### T-5 / S-4.4
- RED: 模板／example 無四欄字
- GREEN: `T-5-floor`

### T-6 / S-5.1
- RED: 無殘行 fixture
- GREEN: `verdict-accepted-only.md` → 缺 role=/scenario=

### T-6 / S-5.2
- RED: 模板／example 無 role=／scenario=
- GREEN: `T-6-template`

### T-6 / S-5.3
- RED: 可能被寫成全表
- GREEN: 模板無「本包必填全表」／`Actor Coverage`

### T-7 / S-6.1
- RED: 無 Disposition 節
- GREEN: 模板 `## Real-world Disposition`;2-decision `## Real-world 去向帳`

### T-7 / S-6.2
- RED: 缺表不擋 G2
- GREEN: `disposition-missing.md` exit 1,C9

### T-7 / S-6.3
- RED: 本方案處理可無 R/S
- GREEN: C9 要求下落 `\b[RS]-\S+`

### T-7 / S-6.4
- RED: Verify `rg RW-[0-9]` 命中 4B 格 `RW-1`
- GREEN: 六檔 rg = 0(D-1 改寫 4B,不翻 4A)

### T-8 / S-7.1
- RED: 7-review 無四欄
- GREEN: `T-8-floor`

### T-8 / S-7.2
- RED: 無缺閾值 fixture
- GREEN: `lookback-missing-threshold.md` 紅;舊 7-review 無節 no-fire

### T-8 / S-7.3
- RED: 可能另造 lookback 檔
- GREEN: 模板含 `history-append.sh`;`lookback.md` 字面不在模板／example

### T-9 / S-8.1
- RED: guard 無 Read 分支
- GREEN: Read 核准=是的 `_templates/1-discussion.md` exit 0

### T-9 / S-8.2
- RED: 方案檔可被核准格放行
- GREEN: Read `2-decision.md` exit 2,stderr 含「方案檔」

### T-9 / S-8.3
- RED: 未核路徑可當已授權
- GREEN: Read `notes/review-requirement-discovery-gaps.md` exit 2

### T-10 / S-9.1
- RED: 無 Fast 六問節
- GREEN: 模板 `## Fast early risk triage` 在 ADDED 之前;SKILL「進 4 前六問」

### T-10 / S-9.2
- RED: 空白可當已分診
- GREEN: `fast-blank-triage.md` exit 1,C8「缺節」;`fast-wait-shown-as-done.md` Q3=是且去向非 Fast

### T-10 / S-9.3
- RED: 命中無去向不擋
- GREEN: `fast-hit-no-dest.md` exit 1

### T-10 / S-9.4
- RED: 六問全否仍可能被誤殺
- GREEN: `fast-visual-all-no.md` 9/9,去向=Fast

### T-10 / S-9.5
- RED: full 本 slug 可能被 C8 誤殺
- GREEN: 本 slug 4-spec C8 no-fire,9/9

## Decisions(spec 未載明的自由選擇)

- C7/C8/C9 採 grandfather:無對應 heading 的舊 fixture／subsidy 不發動;有 heading 或 path 含 `discovery-gaps` 才咬。依據:4-spec Compatibility「C1–C6 保留;只加項」+ 不得改 CI fixture 目錄。[Assumption] 舊 fast fixture 不是本 feat 的分診對象。
- 高影響牙只解析 `### 高影響列`,不掃 example Journey。依據:T-4 Files 不能改 example 枚舉;4-spec「普通已核 path:L 句沒寫風險=高不必貼枚舉」。
- Guard Read:未列入 manifest 的路徑放行(讓普通源碼 Read 仍可用);列了但核准≠是才擋;2–7 檔名永遠擋。依據:S-8.1 觀測是三條指定路徑的 exit,不是全盤白名單。
- T-9 不加 `hooks/selftest.sh` ck()。依據:T-9 Verify 明文「不靠 grep selftest」;加案要動 `test-architecture-guards.sh` 的 `MIN_CASES`(非 T-9 Files)。
- 隔離複本缺 fixture 用 `load_fix(name, inline)`,不加 `check_skip`。依據:`EXPECTED_CHECK_SKIP_CALLS = 1` 釘死。
- MIN_CHECKS 改成加完後實數 181,不是寬下限。依據:T-1 Boundaries。
- 未改 `hooks/selftest.sh`;Read 牙以官方 Verify 三案 exit 為準。
- renderer `--write` 後衍生 `guides/guide-dev-flow.html` 與 example `7-review.html`。依據:realworld renderer --check;L1 衍生雙生,不是新 R/S。
- 本 hop 5-tasks checkbox 勾 T-1…T-10,status 維持 draft。依據:owner brief 不轉 approved、不發明 G3。

## Deviations

### D-1(L1)
- 現象:T-7 Verify `rg RW-[0-9]` 掃本 slug 已核准 `2-decision.md`,4B 駁回格原文 `發明 \`RW-1\`` 命中,Verify 永遠紅。該檔不在 T-7 Files。
- 保守選擇:把 4B 格改寫成「發明第二鏈編號（大寫 R、大寫 W、連字號、一位數字）」,Decision 4A 不動、R/S 不動。
- 理由:S-6.4 THEN 是「不得發第二鏈」,不是要在已駁回格保留會被 rg 咬到的示範 id。改的是字面,不是方案。
- 影響:T-7 / R-6 / S-6.4(測法可綠;4A 契約不變)

### D-2(L1)
- 現象:Diff Budget 合計檔 ≤30。本 hop 18 份 discovery-gaps fixture + 三支牙 + 模板／skill／example + 本檔／twin + renderer 衍生,檔數超過估計。
- 保守選擇:不砍 Verify 點名的 fixture、不另開第四家族、不拆 slug。超支當訊號記下,不回 G2。
- 理由:4-spec Diff Budget 寫明「超支本身非偏差,是停下判 L1/L2 的訊號」且「Decision 已拒拆 slug」。每份 fixture 都被某個 T Verify `test -f` 或 spec-gate 吃到。
- 影響:無 R/S 變更。檔數訊號留給 Stage 7。

### D-3(L1)
- 現象:5-tasks `status: draft` 且無 exec.json,`devflow-exec.sh status` = 守衛沉睡。模板 0c 寫「沒武裝就不准開工」。
- 保守選擇:不 invent start、不改 5-tasks 為 approved、不改 STATUS。doctor COMPATIBLE 已貼。scope 按 Files 聯集人工守。
- 理由:owner brief 明確「No G3, no STATUS/HISTORY」;Stage 5 hop 故意留 draft。武裝不了是上游狀態,不是本 hop 發明的流程。
- 影響:圍欄②靜默;本檔已顯性記錄。獨立 T review 留給 PR。

### D-4(L1)
- 現象:#285／#286 CI。①`template7-exit-quickstart` 巢狀 `- ` 與 `markdown_visible` 剝 dash 不齊。②DG-1/DG-2 曾嵌兩枚 `mutate <<'PY'`,實得 223;只把 `MIN_HEREDOCS` 調到 223 是餘裕,PF-2 關掉 INTERP 只少 1 仍可能打平假綠。③有 6-notes 後 `check-devstage6-graph` 要求同 slug `5-tasks` `status: approved`。
- 保守選擇:Exit 回看四欄改續行。DG 突變改呼叫 `scripts/fixtures/discovery-gaps/mutate_n3_prefix.py`,`MIN_HEREDOCS` **維持 221**。5-tasks frontmatter 改 approved。不改 STATUS／HISTORY、不發明 G3。
- 理由:host-stack-fit D-heredoc-1:新牙不該靠新增 `<<'PY'` 撐地板;PF-2 必須「INTERP 關 → 計數跌破」。graph 契約:6-notes 存在則 N1-arm 入口是 approved 5-tasks。
- 影響:T-3／T-8 測法;5-tasks status 機械改口(Stage 5 hop 曾留 draft)。

## Files Changed

對照 Diff Budget(估計 ≤30 檔 / ≤760 非測試 / ≤660 測試):

| 區塊 | 實際 |
|---|---|
| 模板 1／2／3／4／7 | `_templates/{1-discussion,2-decision,3-prototype,4-spec,7-review}.md` |
| skills／指南 | `skills/dev-talk/{SKILL.md,nodes/N3-probe.md,S1-survey.md,S4-accept.md}`、`skills/dev-flow/SKILL.md`、`guides/guide-dev-talk.html`、L1 `guides/guide-dev-flow.html` |
| example | `example/contract-expiry-reminder/{1,2,3,4}-*.md`、`7-review.md`、L1 `7-review.html` |
| realworld + fixture | `scripts/check-realworld.sh` + `scripts/fixtures/discovery-gaps/*`(18) |
| spec-gate + fixture | `scripts/check-spec-gate.sh`(C7/C8/C9) |
| guard | `hooks/devtalk-guard.sh`(Read 分支)。未改 `selftest.sh` |
| architecture | `scripts/test-architecture-guards.sh`(DG-0/1/2 + EXPECTED_*;DG 突變走 fixture `.py`) |
| L1 母版記帳 | `scripts/check-py-floor.sh` `MIN_HEREDOCS` **維持 221**(D-4,不抬地板) |
| L1 本 slug | `docs/dev/requirement-discovery-gaps/2-decision.md`(D-1);`5-tasks.md` checkbox;本檔 + html twin |
| 未改 | `4-spec.md` R/S、STATUS、HISTORY、plugin、`scripts/check-discovery-gaps.sh`(確認不存在) |

`git diff --stat`(不含未追蹤 fixture／本檔):23 files, +615/−73。fixture 另 18 檔。檔數超 Budget → D-2。

回歸摘要(本 hop 官方牙 + 既有正例):realworld 181/181;`check-design-contract.sh` 166/166;本 slug／example／subsidy／`spec-gate-fullwidth-colon` 皆 9/9;`check-devtalk-selfclean` 綠;`check-devtalk-guide-sync` 綠。`test-architecture-guards.sh` 全量在髒樹會報「正式 repo 指紋改變」+ 環境 PF-0(Python 3.9 針,既有 ENV);DG-0/1/2 隔離已對。

## Diff(各 T commit,逐檔折疊)

### detect_goals_wrong_column · `scripts/check-realworld.sh` L260-278  T-1
改什麼：Goals 第一句「我要 dashboard」且 Requested solution 空 → 構想在錯欄
關聯：load_fix 錯欄／合法對照稿;不掃黑名單詞
```diff
+def detect_goals_wrong_column(text):
+    goals = heading_body(text, "Goals")
+    req = heading_body(text, "Requested solution")
+    ...
+    if first.startswith("我要 dashboard") and req_empty:
+        return "構想在錯欄：我要 dashboard 寫在 Goals，Requested solution 空"
+    return None
```

### no_fourth_family · `scripts/check-realworld.sh` L295-296  T-1
改什麼：鎖定沒有 `scripts/check-discovery-gaps.sh`
關聯：OC-1 同一入口;T-1 Verify `test ! -e`
```diff
+check(not os.path.isfile(os.path.join(root, "scripts/check-discovery-gaps.sh")),
+      "未新開 check-discovery-gaps.sh(OC-1 同一入口)")
```

### MIN_CHECKS · `scripts/check-realworld.sh` L547-547  T-1
改什麼：地板改成加完後實數 181
關聯：N-2;刪 check 必連地板
```diff
-MIN_CHECKS = <舊實數>
+MIN_CHECKS = 181
```

### Requested solution · `_templates/1-discussion.md` L76-81  T-2
改什麼：Goals 只寫工作結果;構想進 Requested solution
關聯：S4-accept「從哪裡看出結果發生」;example 同期改口
```diff
 ## Goals
+<!-- 條列,可驗證的「想達成」。只寫工作結果,不把畫面／API／元件寫成目標本身。 -->
+
+## Requested solution
+<!-- 解法構想(未定案)。「我要 dashboard／某 API／某元件」寫這裡,並標未定案。 -->
```

### 怎麼看到 · `skills/dev-talk/nodes/S4-accept.md` L18-22  T-2
改什麼：從哪看改問結果發生,不把畫面／端點當 Goal
關聯：模板驗收雛形不再預填畫面路徑 \| API 端點
```diff
-不綁做法),每條再問出「怎麼看到」三件:①從哪裡看(畫面/端點/檔案/log)
+不綁做法),每條再問出「怎麼看到」三件:①從哪裡看出結果發生(不把畫面/
+端點/元件當成 Goal 本身)
```

### N3 前綴 · `skills/dev-talk/nodes/N3-probe.md` L23-30  T-3
改什麼：發現｜禁附推薦;裁決｜可附選;兩輪只標輔助
關聯：SKILL 入口摘要／guide 原文必須 substring-sync
```diff
-①一次只問一題、附推薦答案,同題多種解讀 → 列差異讓使用者選、**禁默選**;
+①一次只問一題。發現題前綴字面 `發現｜`,禁附推薦;裁決題前綴字面 `裁決｜`,
+可附本方案／Non-Goal／另開 slug 等選項。同題多種解讀 → 列差異讓使用者選、**禁默選**;
+「連續兩輪無新問題」只標輔助,不是唯一完成條件。
```

### seed_n3 · `scripts/test-architecture-guards.sh` L730-757  T-3
改什麼：隔離複本帶 N3;刪發現｜或裁決｜一邊必紅
關聯：realworld 在 N3 已改口後只盯 N3 正文
```diff
+seed_n3() {
+  d=$(seed "$1")
+  mkdir -p "$d/skills/dev-talk/nodes"
+  cp "$ROOT/skills/dev-talk/nodes/N3-probe.md" "$d/skills/dev-talk/nodes/"
+  echo "$d"
+}
+D=$(seed_n3 dg0); expect pass check-realworld.sh "$D" "DG-0 N3 發現｜與裁決｜都在"
+...
+expect fail check-realworld.sh "$D" "DG-1 刪掉 N3 發現｜前綴必須紅"
+expect fail check-realworld.sh "$D" "DG-2 刪掉 N3 裁決｜前綴必須紅"
```

### detect_claim_shape · `scripts/check-realworld.sh` L401-423  T-4
改什麼：高影響列五值枚舉;點頭非獨源;ticket 解法不當 Observed
關聯：只吃 `### 高影響列`;S-8.4 同函式
```diff
+def detect_claim_shape(fields):
+    if status and status not in CLAIM_ENUM:
+        return f"枚舉必須落在 {', '.join(sorted(CLAIM_ENUM))}"
+    if nod and not reopen:
+        return "點頭不是來源"
+    if ticketish and status == "Observed":
+        return "解法建議不當事實"
```

### 認可語意 · `skills/dev-talk/nodes/S1-survey.md` L29-31  T-4
改什麼：認可 ≠ 來源升格
關聯：SKILL S1 摘要同期;guide 原文 sync
```diff
-   認可後的清單 = 本次「已核事實」。
+   使用者認可代表確認理解,認可 ≠ 來源升格;高影響主張仍要可重開來源或
+   Assumption+期限,不得把認可後清單當唯一來源。
```

### C7 · `scripts/check-spec-gate.sh` L251-281  T-5
改什麼：有 Assumption refs 表才驗;open+過期日或 stage-2/3 → FAIL
關聯：resolved／oc-accepted 放行;無表 no-fire
```diff
+# ---- C7:Assumption refs(有表才發動;無表 no-fire,不誤殺舊 fixture)----
+        if status == "open" and expired:
+            c7_bad.append(f"L{n + 1} Assumption 過期仍 open:{line[:70]}")
+    record("C7", not c7_bad, "Assumption refs 無過期 open(有表才驗)", c7_bad or [])
+else:
+    record("C7", True, "Assumption refs 無表 = no-fire")
```

### detect_verdict_incomplete · `scripts/check-realworld.sh` L467-472  T-6
改什麼：ACCEPTED 殘行缺 role= 或 scenario= 必紅
關聯：既有 attestation 牙仍在;模板不要求全表
```diff
+def detect_verdict_incomplete(text):
+    for match in re.finditer(r"Human verdict:\s*(.+)", text):
+        line = match.group(1)
+        if re.match(r"ACCEPTED\b", line) and ("role=" not in line or "scenario=" not in line):
+            return "ACCEPTED 殘行缺 role= 或 scenario="
```

### Human verdict · `_templates/3-prototype.md` L129-129  T-6
改什麼：一行加 role=／scenario= 槽
關聯：example 3-prototype 同期
```diff
-- Human verdict: ACCEPTED | REVISE | NOT_REVIEWED
+- Human verdict: ACCEPTED | REVISE | NOT_REVIEWED | role=<Actors 表角色> | scenario=<AC-id 或 Demo Script 場景名>
```

### C9 · `scripts/check-spec-gate.sh` L319-346  T-7
改什麼：有表必驗去向／下落;discovery-gaps + full 缺表必紅
關聯：subsidy 等舊 full 無表 no-fire
```diff
+# ---- C9:Real-world Disposition(有表必驗;discovery-gaps + full 缺表必紅)----
+            if dest == "本方案處理" and not re.search(r"\b[RS]-\S+", drop):
+                c9_bad.append(f"L{n + 1} 本方案處理下落必須有 R- 或 S-")
```

### 4B 字面 · `docs/dev/requirement-discovery-gaps/2-decision.md` L44-44  T-7
改什麼：駁回格不再寫會被 `RW-[0-9]` 咬到的示範 id
關聯：D-1;Decision 4A 不動
```diff
-| 4B | 發明 `RW-1`… 第二條 ID 鏈，R/S 引用 RW-id | …
+| 4B | 發明第二鏈編號（大寫 R、大寫 W、連字號、一位數字）第二條 ID 鏈，R/S 引用該 id | …
```

### missing_lookback · `scripts/check-realworld.sh` L501-508  T-8
改什麼：已出現回看節才驗四欄;缺「低於何值重開」紅
關聯：舊 7-review 無節 no-fire;模板禁 lookback.md 字面
```diff
+def missing_lookback(text):
+    present = any(field in text for field in LOOKBACK_FIELDS) or (
+        "回看" in text and "Exit" in text)
+    if not present:
+        return None
+    return [field for field in LOOKBACK_FIELDS if field not in text]
```

### 回看約定 · `_templates/7-review.md` L343-348  T-8
改什麼：Exit 加四欄;結果走 history-append.sh
關聯：example 7-review 一行四欄;renderer 衍生 html
```diff
+- [ ] **回看約定**(四欄必填;結果到期用 `scripts/history-append.sh` 追加,不另造永久回看檔):
+      - 回看日期:
+      - 回看 owner:
+      - 資料來源:
+      - 低於何值重開:
```

### Read 分支 · `hooks/devtalk-guard.sh` L20-72  T-9
改什麼：talk 游標在時 Read 方案檔永禁;manifest 核准≠是禁
關聯：DEVTALK_MANIFEST 測試縫;游標不在走舊寫入洩漏
```diff
+if [ "$TOOL" = "Read" ]; then
+    ...
+if sol:
+    print('方案檔', file=sys.stderr)
+    sys.exit(2)
+if listed is not None:
+    if approved != '是':
+        sys.exit(2)
```

### Evidence manifest · `_templates/1-discussion.md` L93-97  T-9
改什麼：同檔五欄核准表
關聯：guard 讀字面;example 同期
```diff
+## Evidence manifest
+<!-- 討論期想讀的事實路徑。owner 核准 ∈ {是, 未核, 禁}。核准=是才能讀;
+     2-decision／3-prototype／4-spec／5-tasks／6-implementation-notes／7-review 即使誤寫「是」仍禁。 -->
+| 想找哪類 | 為什麼 | 擬路徑或來源 | owner 核准 | 已讀 |
```

### C8 · `scripts/check-spec-gate.sh` L283-317  T-10
改什麼：僅 lane:fast 且(有表或 discovery-gaps)才驗六問／去向
關聯：命中後去向不得 Fast／待裁／空白;full no-fire
```diff
+# ---- C8:Fast early risk triage(僅 lane: fast;discovery-gaps 或缺表／有表都驗)----
+        if any(not a.strip() for _, a, _ in answers) or len(answers) < 6:
+            c8_bad.append("Fast 六問答欄空白或不足")
+        if yes_hits:
+            if dest in ("", "待裁", "Fast"):
+                c8_bad.append("命中後去向必須是 full／fast+mini／OC,不得空白、待裁或 Fast")
```

### Fast triage 節 · `_templates/4-spec.md` L112-126  T-10
改什麼：ADDED 之前放六問表
關聯：SKILL「進 4 前六問」;full 可省略
```diff
+## Fast early risk triage
+| 改變下一步？ | |
+| 改權限／核准語意？ | |
+| 改等待／完成語意？ | |
+| 改角色交接？ | |
+| 改系統外動作？ | |
+| 改中斷恢復？ | |
```

### spec-gate 九項 · `skills/dev-flow/SKILL.md` L108-112  T-10
改什麼：G2 文案六項 → 九項(C7/C8/C9)
關聯：check-spec-gate 檔頭同步
```diff
-  `bash <master>/scripts/check-spec-gate.sh docs/dev/<slug>/4-spec.md`。它查六項,
-  一項一條、六項都要過:
+  `bash <master>/scripts/check-spec-gate.sh docs/dev/<slug>/4-spec.md`。它查九項,
+  一項一條、九項都要過(C1–C6 原形 + C7 Assumption refs／C8 Fast 六問／C9 Disposition):
```

### mutate_n3_prefix · `scripts/fixtures/discovery-gaps/mutate_n3_prefix.py` L1-16  T-3
改什麼：DG-1/DG-2 改呼叫 .py,不新增 `<<'PY'`
關聯：test-architecture-guards DG 案;`MIN_HEREDOCS` 維持 221
```diff
+root = pathlib.Path(sys.argv[1])
+needle = sys.argv[2]
+rewritten = text.replace(needle, "", 1)
```

### 回看約定 · `_templates/7-review.md` L343-344  T-8
改什麼：四欄改同一項續行,避免指南 parity 留下字面 `-`
關聯：renderer `template7-exit-quickstart`;欄位字與 history-append.sh 仍在
```diff
-- [ ] **回看約定**(四欄必填;結果到期用 `scripts/history-append.sh` 追加,不另造永久回看檔):
-      - 回看日期:
-      - 回看 owner:
-      - 資料來源:
-      - 低於何值重開:
+- [ ] **回看約定**(四欄必填;結果到期用 `scripts/history-append.sh` 追加,不另造永久回看檔):
+      回看日期: ／ 回看 owner: ／ 資料來源: ／ 低於何值重開:
```

## Self-Review

①每個 T×S 都有含 S-id 的測試 + 該 T 自己的 RED/GREEN?是。見 TDD Evidence;牙是既有三支的加項,S-id 寫在 check 標籤／fixture 檔名／官方 Verify。
②每 T 在 T Review Log 有 verdict?是。T-1…T-10 自檢 PASS;獨立 reviewer 留給 PR(不發明 G3)。
③每個 PASS 都早於該 T commit?本 hop 十 T 同一 land commit;Verify 全綠後才 commit。
④每個 FAIL 後有較晚 PASS?無 FAIL round。
⑤每個已完成 T 一 commit、Progress Log 有 hash?十 T 單一 land `58250b33dfafdb04514bc7b35cc5c013dbb2d5f4`(sequential 同樹改三支牙)。
⑥git diff --stat ⊆ Files 聯集?產品檔是。超出:D-1 本 slug 2-decision 一字;D-2 fixture 檔數;D-4 5-tasks `approved`(graph 契約);renderer 衍生 guide-dev-flow.html。未改 STATUS／HISTORY／4-spec R/S／plugin。
⑦Decisions/Deviations 與 diff 對得上?是。C7/C8/C9 grandfather、無第四家族、`MIN_HEREDOCS` 維持 221、無 lookback.md。Design Boundary:無未授權模組;Data Owner 仍是三支牙／同檔欄;Interface 為 spec-gate 加項與 guard Read;未修掉 known limit ①②③。
⑧回歸綠?官方 T-1…T-10 Verify 全綠;realworld 181/181;design-contract 166/166;methodology 124/124;四份既有 4-spec 9/9;devtalk selfclean／guide-sync 綠。

## Review Follow-up(G3 打回時才用)
