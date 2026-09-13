---
feature: requirement-discovery-gaps
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-B-stage7
reviewers: [implementer-B-stage7]
updated: 2026-09-13
---

# 7. 驗證 —— **不是 G3 PASS**

> Independent Stage 7 Implementer B（fresh context；≠ Stage 6 implementer-A；≠ owner rick）。
> 產品樹 = main `#286` `fdbd569`。本 hop 只寫本檔 + official html twin。
> `verdict:` 留 **PRE-REVIEW**。Human 才准填 PASS／REQUEST_CHANGES／HOLD。全勾不算 PASS。
> 建議 Human G3 路徑:Verdict 門檻表 → twin／步 5 抽驗格 **S-5.3**（`_templates/3-prototype.md:128` + `scripts/check-realworld.sh:458-459`）→ 附錄 A1（A-1／OC-1）→ 附錄 A2（F-1）→ 可選加抽 S-1.4 或 S-8.2 → 再決定。
> **本場 twin 抽驗格 = Coverage 中位列 S-5.3**（決定論 `rows[len//2]`）。S-1.4／S-8.2 只是可選加抽，不是第五格。

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
> | 5 | **抽驗一列** | 本場 twin 第五格鎖 **S-5.3**。打開 `_templates/3-prototype.md:128`（`role=`／`scenario=`；無 Actor Coverage 全表）與 `scripts/check-realworld.sh:458-459`。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-B-stage7`（獨立 fresh-context Cloud Agent B;**≠** Stage 6 `#286` implementer-A;`≠` owner rick） |
| Human G3 | **未寫**。本檔 `verdict: PRE-REVIEW`。不是 G3 PASS。 |
| 讀取順序(可查) | ①`4-spec.md`（G2 PASS、R-1…R-9／35 S） ②`5-tasks.md`（T-1…T-10） ③`#286` diff（`2bfb906..fdbd569`、48 檔 +2429/−141） ④測試碼／fixture／三支牙 ⑤親跑 T-1…T-10 Verify + 4-spec entry point + S-2.2 隔離突變 + 步 2c（兩次座標相同後合 `37a4284`）→ **之後才** ⑥讀 `6-implementation-notes.md`（Self-Review／Deviations D-1…D-8） |
| 圍欄 | 本環境無 `.devflow/exec.json`（`scripts/devflow-exec.sh` 不存在;runtime 在 `hooks/devflow-exec.sh`）。讀取順序靠散文紀律,不靠 review hook。doctor:`COMPATIBLE`（契約 2.0.0,runtime 3.23.4,gauntlet 1.3.3） |
| 本輪性質 | 產品碼已在 tip `#286`。2c 合進 `#287` STATUS／HISTORY 列（incoming,不是本 hop 撰寫）。本 hop **只寫** `7-review.md` + html twin。不改 STATUS／HISTORY 正本、不新造檢查家族、不 merge 本 PR。 |

本檔不是 owner 自審。機械數字（exit／174/174／9/9／Read 三案）可抽驗;F-id 分級與「沒想到的事」交給下一棒 Human。

## Coverage Matrix

自建（grep 4-spec S 清單 ↔ 指定檢查／fixture／`rg`;**未先讀** 6-notes Self-Review）。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/check-realworld.sh:294-299`;`_templates/1-discussion.md:86-90`;`skills/dev-talk/nodes/S4-accept.md:20-23`;T-2-ok | ✅ |
| S-1.2 | `scripts/check-realworld.sh:259-292`;fixture `scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md:1-9`;stdout `構想在錯欄:goals-dashboard-in-wrong-column`;`test ! -e scripts/check-discovery-gaps.sh` | ✅ |
| S-1.3 | `scripts/check-realworld.sh:300-304`;`example/contract-expiry-reminder/1-discussion.md:73-79`;Goals 無「就能看到／點擊可直達／一眼可見」 | ✅ |
| S-1.4 | `scripts/check-realworld.sh:262-263,290`;fixture `scripts/fixtures/discovery-gaps/goals-outcome-with-requested-dashboard.md:1-10`;detector 不掃 dashboard／API 詞 | ✅ |
| S-2.1 | `skills/dev-talk/nodes/N3-probe.md:22-25,44-45`;`skills/dev-talk/SKILL.md:104`;`guides/guide-dev-talk.html:201-202`;T-3-skill | ✅ |
| S-2.2 | `scripts/test-architecture-guards.sh:732-751`（RW-DG1／RW-DG2）;本 hop 隔離突變刪 `發現｜`／`裁決｜` → realworld exit 1、失敗項含缺邊前綴 | ✅ |
| S-2.3 | `scripts/check-realworld.sh:333-335`;fixture `scripts/fixtures/discovery-gaps/probe-decision-with-options.md:1-4` | ✅ |
| S-3.1 | `scripts/check-realworld.sh:436-437`;fixture `scripts/fixtures/discovery-gaps/user-report-only.md:1-5` | ✅ |
| S-3.2 | `scripts/check-realworld.sh:444-445`（`_good_obs`／`_good_assume`） | ✅ |
| S-3.3 | `scripts/check-realworld.sh:440`;fixture `scripts/fixtures/discovery-gaps/nod-as-only-source.md:1-8`;`skills/dev-talk/nodes/S1-survey.md:29-30`（節點已改口） | ✅ |
| S-3.4 | `scripts/check-realworld.sh:441`;fixture `scripts/fixtures/discovery-gaps/enum-unknown.md:1-8` | ✅ |
| S-3.5 | `scripts/check-realworld.sh:446`（`_low` 普通 Context 不紅） | ✅ |
| S-4.1 | `scripts/check-spec-gate.sh:251-292` C7;fixture `scripts/fixtures/discovery-gaps/assumption-expired-open.md:25-29` → exit 1、`Assumption 過期仍 open(2020-01-01)` | ✅ |
| S-4.2 | 同 C7;fixture `scripts/fixtures/discovery-gaps/assumption-resolved.md:25-29` → 9/9 exit 0 | ✅ |
| S-4.3 | `docs/dev/requirement-discovery-gaps/4-spec.md:603-607` 三列 `oc-accepted` → spec-gate 9/9 | ✅ |
| S-4.4 | `scripts/check-realworld.sh:450-453`;`_templates/1-discussion.md:75-78`;`example/contract-expiry-reminder/1-discussion.md:62-66` | ✅ |
| S-5.1 | `scripts/check-realworld.sh:462-474`;fixture `scripts/fixtures/discovery-gaps/verdict-accepted-only.md:1-5` | ✅ |
| S-5.2 | `scripts/check-realworld.sh:472-476`;完整行 `role=`／`scenario=` 放行 | ✅ |
| S-5.3 | `scripts/check-realworld.sh:458-459`;`_templates/3-prototype.md:128`;`rg` `Actor Coverage`／`本包必填全表` = 0 | ✅ |
| S-6.1 | `scripts/check-spec-gate.sh:348-372` C9;fixture `scripts/fixtures/discovery-gaps/disposition-missing.md:1-23` → exit 1、`full 缺表` | ✅ |
| S-6.2 | `scripts/check-spec-gate.sh:368-369`;本檔 disposition `4-spec.md:615-626` 下落含 `S-` | ✅ |
| S-6.3 | `4-spec.md:624-629`（刻意維持 → Out of Scope;仍待驗 → Known limit） | ✅ |
| S-6.4 | `rg -n 'RW-[0-9]'` 指定六檔 = 0（本 hop 親跑） | ✅ |
| S-7.1 | `scripts/check-realworld.sh:478-481`;`_templates/7-review.md:344-349`;`example/contract-expiry-reminder/7-review.md:273-277` | ✅ |
| S-7.2 | `scripts/check-realworld.sh:486-497`;fixture `scripts/fixtures/discovery-gaps/lookback-missing-threshold.md:1-15`;舊檔無節 no-fire | ✅ |
| S-7.3 | `_templates/7-review.md:345-346`;`rg lookback.md` 模板／example 7-review = 0;含 `history-append.sh` | ✅ |
| S-8.1 | `hooks/devtalk-guard.sh:13-80`;T-9 Verify Read `_templates/1-discussion.md` exit 0;`hooks/selftest.sh:563-564` | ✅ |
| S-8.2 | `hooks/devtalk-guard.sh:33-40`;T-9 Read `2-decision.md` exit 2、stderr `方案檔仍禁讀`;selftest `:565-566` | ✅ |
| S-8.3 | `hooks/devtalk-guard.sh:82-84`;T-9 Read 未核 path exit 2;fixture `unapproved-as-only-source.md:1-8` + `check-realworld.sh:438-439` | ✅ |
| S-8.4 | `scripts/check-realworld.sh:442-443`;fixture `scripts/fixtures/discovery-gaps/ticket-solution-as-fact.md:1-8` | ✅ |
| S-9.1 | `scripts/check-spec-gate.sh:294-346` C8;fixture `fast-blank-triage.md:1-19` → exit 1、`六問缺表` | ✅ |
| S-9.2 | fixture `fast-wait-shown-as-done.md:9-19`;Q3=`是。等待被顯示成完成`;去向=`fast+mini` ≠ Fast;T-10-ok | ✅ |
| S-9.3 | fixture `fast-hit-no-dest.md:9-19` → C8 exit 1、`不得空白／待裁／Fast` | ✅ |
| S-9.4 | fixture `fast-visual-all-no.md:9-19` → spec-gate 9/9 exit 0 | ✅ |
| S-9.5 | 本 slug `4-spec.md` C8 `full 缺表 no-fire`;9/9 | ✅ |
| 既有測試套件(回歸) | 4-spec entry point + T-1…T-10 Verify + S-2.2 隔離突變;見 Verification Evidence | ✅ |

**Verify 親跑**（5-tasks 原指令;2026-09-13;2c 合 `37a4284` 之後、Fresh 之前重跑 realworld／spec-gate）:

```
T-1-wired
  構想在錯欄:goals-dashboard-in-wrong-column
✅ real-world interaction checks: 174/174 passed(地板 174)
T-2-ok
T-3-skill
T-3-wired
T-4-skill
T-4-wired
expired_exit=1  (C7 L29:Assumption 過期仍 open(2020-01-01))
assumption-resolved 9/9
本 slug 4-spec 9/9 (35 S)
T-5-floor
T-6-template
T-6-wired
disp_exit=1  (C9 full 缺表)
T-7-template
RW_HITS=0
T-8-floor
T9_CASES S-8.1 rc=0; S-8.2 rc=2 方案檔仍禁讀; S-8.3 rc=2 未核路徑不得當已授權
T-9-read-ok
blank_exit=1  (C8 六問缺表)
hit_exit=1    (C8 命中後去向待裁)
visual_exit=0
T-10-ok
S-2.2 dg1/dg2 隔離突變 OK_RED（失敗項:N3-probe 含發現｜／裁決｜前綴）
no scripts/check-discovery-gaps.sh
no scripts/check-evidence-allow.sh
```

T-1 第一次因環境缺 `markdown-it-py` 紅（`renderer --check`）—— ENV,補裝 `markdown-it-py==4.0.0` 後 174/174。不計 IMPL 失敗。

## Verification Evidence

- Source SHA: e922c2b0e5e39b2bafaa5c6aaf5a7b5f3303af8e
- Final Fresh Run ID: 2026-09-13T0705Z-impl-B-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && bash scripts/check-realworld.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0(`scripts/requirements-methodology-render.txt`); contract 2.0.0; runtime 3.23.4; git 2.43.0; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支 | 4-spec Required 被全形分號切出的第一 token;三牙親跑 | pass | spec-gate 9/9 exit 0;realworld 174/174 exit 0;T-9 Read 三案 0/2/2 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md` | pass | exit 0;9/9;35 條 S | |
| check-realworld | `bash scripts/check-realworld.sh` | pass | exit 0;174/174;stdout 含構想在錯欄 1 行 | |
| devtalk-guard | T-9 Verify `tool_name=Read` 三案 | pass | S-8.1 exit 0;S-8.2 exit 2;S-8.3 exit 2 | |
| Supply chain | `rg -n 'RW-[0-9]'` 指定六檔 + `test ! -e scripts/check-discovery-gaps.sh` | pass | RW 命中 0;第四家族檔不存在 | |
| check-stage4-rs-contract.sh` 是本 hop 審頁形狀，不落地缺口牙，不列入本欄） | （幽靈 token） | unverified | | 4-spec Required layers 欄含全形分號,gauntlet tokenize 切出第二 token;4-spec 自己寫「不列入本欄」。見附錄 A3 |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |
| check-py-floor | `bash scripts/check-py-floor.sh` | n-a | | ENV:本機無 Python 3.9–3.11;exit 2 找不到直譯器。不是本 feat 產品紅 |

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

Final Fresh gauntlet（`--source-sha e922c2b0e5e39b2bafaa5c6aaf5a7b5f3303af8e --review-file`）:61 checks、1 violation — E7 required layer 第二幽靈 token 未 pass。見附錄 A3。不把幽靈 token 標 pass。

### 2c 整合結論

授權合併的那一次（Fresh **之前**跑兩次,STATUS／座標完全相同,然後合印出的 INTEGRATION_SHA,不是 branch 名）:

- STATUS: SYNC_REQUIRED_NO_OVERLAP
- FORK / HEAD / INTEGRATION / REF: `fdbd5696aeb491538276caa09370744370189601` / `fdbd5696aeb491538276caa09370744370189601` / `37a4284848fdcfd4d7ad2385ed6df2c74fd613fd` / `refs/remotes/origin/main`
- 共同戰場:無（incoming = `#287` STATUS／HISTORY 列,3 檔 +9/−2）
- 恢復: n-a（SYNC_REQUIRED_NO_OVERLAP;已 fast-forward 合 INTEGRATION_SHA,合後 realworld 174/174、本 slug spec-gate 9/9）

本 hop **沒有撰寫** STATUS／HISTORY;那是 incoming `#287`。合完 HEAD=`37a4284`。之後若再跑同一支腳本會印 `ALREADY_SYNCED`（exit 2）——不當交集證據。`#287` `37a4284848fdcfd4d7ad2385ed6df2c74fd613fd` 已在 tip（本 hop must-fix 不重做 2c）。Source SHA 於本輪 must-fix 後重綁當下 HEAD。再一次 docs commit 仍會漂（Known Limit 本 hop ①）。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得把構想寫進 Goals 還當已完成分欄(S-1.2) | check-realworld S-1.2 fixture;stdout 構想在錯欄 | pass |
| 不得用 dashboard／API 黑名單誤殺結果句(S-1.4) | check-realworld S-1.4;detector 只咬空 Requested +「我要 」 | pass |
| 不得讓發現題附推薦仍當硬規則(S-2.1) | N3-probe:22-25 禁附推薦;T-3-skill | pass |
| 不得把點頭當唯一來源(S-3.3) | nod-as-only-source + S1-survey.md:29-30 | pass |
| 不得讓過期 open Assumption 通過 spec-gate(S-4.1) | C7 expired-open exit 1 | pass |
| 不得只寫 ACCEPTED + 日期當完整 verdict(S-5.1) | verdict-accepted-only 殘行必紅 | pass |
| 不得讓痛點列去向空白或發第二鏈編號(S-6.1、S-6.4) | C9 缺表 exit 1;`rg RW-[0-9]` = 0 | pass |
| 不得另造 lookback 永久檔(S-7.3) | 模板無 lookback.md;有 history-append.sh | pass |
| 不得讀 2–7 方案檔或未核路徑當已授權(S-8.2、S-8.3) | guard Read exit 2 兩案 | pass |
| 不得把 Fast 空白六問當已分診(S-9.1) | C8 blank-triage exit 1 | pass |
| 不得新造檢查家族、不得本 hop 改 STATUS／模板正本、不得發明 G3 | `test ! -e scripts/check-discovery-gaps.sh`;本 hop 只寫 7-review*;verdict PRE-REVIEW | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 feat Stage 6 為手動 sequential（6-notes:Run n-a）。本 Stage 7 亦手動。本節留白,不虛構模型歷史。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

reviewer **親自重跑**;不採信 6-notes 貼的文字。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 從改後三檔原文看;兩節名都在、Goals／S4-accept 不再要求通道候選 | `_templates/1-discussion.md:86-90` 有 `## Goals` 與 `## Requested solution`;驗收雛形:110 寫「不預填畫面／API 通道」;`S4-accept.md:20`「從哪裡看出結果發生」 | ✅ |
| S-1.2 | 從該檢查 exit 與 stderr 看;exit ≠ 0 且含指定字樣 | 套件內對 fixture 斷言 `_wrong_hit` 為真並印 `構想在錯欄:goals-dashboard-in-wrong-column`;套件本身 exit 0（T-1 Verify 設計）。同一入口,無第四家族 | ✅ |
| S-1.3 | 從改後 example Goals／Requested solution／Interview Log 看 | Goals:73-76 三句是結果;Requested solution:78-79「未定案：站內 dashboard」;Interview:133「通道構想見 Requested solution」 | ✅ |
| S-1.4 | 從 exit 與是否誤殺領域詞看 | fixture 含 dashboard／API 當領域詞;`detect_goals_wrong_column` 回 False;`check(not _ok_hit, …不因 dashboard/API 誤殺)` 綠 | ✅ |
| S-2.1 | 從改後 N3-probe 與指南對稱句看 | N3:22-25 發現禁推薦、裁決可附;完成條件:44-45 兩輪只標輔助;SKILL:104 與 guide:201 同步 | ✅ |
| S-2.2 | 從該檢查 exit 與缺邊字樣看 | 隔離複本刪一邊前綴 → realworld 173/174 紅;失敗項 `N3-probe 含發現｜前綴`／`含裁決｜前綴` | ✅ |
| S-2.3 | 從該稿跑檢查的 exit 看 | fixture 兩邊前綴都在;裁決附三選;`_discover_line_has_recommend` 假 | ✅ |
| S-3.1 | 從 exit 與字樣看 | `user-report-only.md` 只寫「使用者反映希望 dashboard」→ problems 含 `來源` | ✅ |
| S-3.2 | 從兩份 exit 看 | `_good_obs`（Observed+path:L）與 `_good_assume`（Assumption+期限+四欄）`not _claim_problems` | ✅ |
| S-3.3 | 從 exit 與字樣看 | `nod-as-only-source.md` 來源=使用者點頭 → `點頭`;節點 S1-survey:29-30 已改「認可不是來源升格」 | ✅ |
| S-3.4 | 從 exit 與字樣看 | `enum-unknown.md` 狀態=Unknown → `枚舉` | ✅ |
| S-3.5 | 從 exit 看 | `_low` 普通 path:L 句無風險=高、高影響列齊 → 不紅 | ✅ |
| S-4.1 | 從 spec-gate exit 與輸出看 | expired-open C7 ❌;`L29:Assumption 過期仍 open(2020-01-01)`;exit 1 | ✅ |
| S-4.2 | 從該 fixture 的 Assumption 項看 | resolved 9/9;C7 ✅ | ✅ |
| S-4.3 | 從本檔 Assumption refs 三列看 | 三列 status=oc-accepted;本 slug 9/9 | ✅ |
| S-4.4 | 從 realworld 對四欄字面看 | 模板:77-78 與 example:63-66 四欄齊 | ✅ |
| S-5.1 | 從 exit 與字樣看 | `verdict-accepted-only.md` 只有 ACCEPTED+attestation → `_accepted_missing_role_scenario` 真 | ✅ |
| S-5.2 | 從該項看 | 完整行放行 | ✅ |
| S-5.3 | 從兩檔原文看 | 模板:128 有 role=／scenario=;`Actor Coverage` 零命中 | ✅ |
| S-6.1 | 從 spec-gate exit 與字樣看 | disposition-missing C9 ❌;`缺 ## Real-world Disposition`;exit 1 | ✅ |
| S-6.2 | 從該列下落是否含 R- 或 S- 看 | 本檔「發現被錨定 → S-2.1、S-2.2」;C9 本方案處理匹配 `R-`／`S-` | ✅ |
| S-6.3 | 從三列下落看 | Exception 三列:Out of Scope／Known limit 都在;C9 不紅 | ✅ |
| S-6.4 | 從 `rg -n 'RW-[0-9]'` 對上列路徑看 | 輸出為空 | ✅ |
| S-7.1 | 從 realworld 對四欄字面看 | 模板:348 與 example:275 四欄齊 | ✅ |
| S-7.2 | 從該填檔檢查看 | lookback-missing-threshold 缺「低於何值重開」必紅;舊檔無節不發動 | ✅ |
| S-7.3 | 從 `rg lookback.md` 看 | 模板／example 7-review 無永久檔;有 history-append.sh | ✅ |
| S-8.1 | 從 guard 對該 Read 的 exit 看 | T-9:核准=是 → exit 0 | ✅ |
| S-8.2 | 從 guard exit 與 stderr 看 | T-9:2-decision 即使核准=是 → exit 2;`方案檔仍禁讀(2-decision／4-spec／2–7` | ✅ |
| S-8.3 | 從 guard exit 與主張牙看 | T-9:未核 → exit 2;`未核路徑不得當已授權 evidence`;填檔牙含來源 | ✅ |
| S-8.4 | 從該牙 exit 與字樣看 | ticket-solution-as-fact → `解法`／`不當事實` | ✅ |
| S-9.1 | 從 spec-gate exit 與字樣看 | fast-blank C8 ❌;`六問缺表`;exit 1 | ✅ |
| S-9.2 | 從該 fixture 表第 3 列與去向列看 | Q3 是+「等待被顯示成完成」;去向 fast+mini;無待裁 | ✅ |
| S-9.3 | 從 spec-gate 看 | fast-hit-no-dest 去向=待裁 → C8 ❌;exit 1 | ✅ |
| S-9.4 | 從該項看 | fast-visual-all-no 六問皆否+去向 Fast → 9/9 | ✅ |
| S-9.5 | 從本檔跑 spec-gate 的 Fast 項看 | C8 `full 缺表 no-fire`;9/9 | ✅ |

S-1.2 觀測欄寫「THEN exit ≠ 0」。實作是**套件內斷言 fixture 必須被指出錯欄**,套件綠。與 T-1 Verify 一致。不是對 fixture 當獨立 CLI 輸入。見附錄 A1。

## 截圖槽

本 feat 無產品前端、無 `shots/`、無進場紀錄。觀測是 CLI 牙與教師原文。不准發明編輯 URL、不准新增截圖。

### 進場
- data-shot: n-a
- src: （無）
- caption: 無 GUI 進場。twin 抽驗格是 Coverage 中位列 S-5.3（`_templates/3-prototype.md:128`）。
- 進場:從列表打開已存在紀錄。不准新增。本目錄無已存在 shots。
- hang-point: n-a（無 e2e）

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.2 | G1 reviewer | 構想不能混成目標 | 跑 check-realworld;讀錯欄 stderr | 把該句搬到 Requested solution | 檢查同步結束 | ✅ 人看得見拒絕;Authority=形狀+G1 語意 |
| S-1.3 | 採用者 | 抄範例時寫結果 | 打開 example 1-discussion | — | Goals 仍鎖通道則同一 T 改 | ✅ Goals 已改口。Q3／AC 仍教 dashboard 通道,見 F-2 🟡 |
| S-2.1 | 訪談對象／討論 agent | 不被錨定 | 讀 N3 發現｜開放題 | 人口頭／Email 答現況 | 一題一答;不等推薦清單 | ✅ 問句本身不再塞推薦 |
| S-3.3 | 討論 agent／G1 | 認可≠營運事實 | 跑主張牙;打開聲稱來源 | 補 path 或改 Assumption | — | ✅ 牙擋點頭獨源。SKILL／指南入口仍舊句,見 F-1 |
| S-4.1 | G2 reviewer | 過期假設進不了 G2 | 跑 spec-gate | 改 resolved 或 oc-accepted | 拒絕發生在送審關 | ✅ 人看得見 C7 紅 |
| S-5.1 | 後讀 3-prototype 的人 | 一行答出驗了誰／哪場 | 讀 Human verdict 行 | 人類親填 role／scenario | 無 attestation 仍被既有 runtime 拒 | ✅ 殘行紅;Agent 仍禁代填 |
| S-6.1 | 收斂者／G2 | 痛點不能無聲消失 | 跑 spec-gate;對原文片段 | 補表或標刻意維持 | — | ✅ 新式 full 缺表紅。legacy full grandfather,見 KL-C9 |
| S-7.1 | owner | 出貨留下誰／何時／用什麼／門檻 | 填 Exit 四欄 | 到期 history-append;日曆回看 | 回看日未到不得寫已改善 | ✅ 欄在。指標是否改善仍人判 |
| S-8.1 | 討論 agent | 核准後讀得到事實 | Read 核准=是的擬路徑 | 先列「想找哪類＋為什麼」等 owner 核 | 核准格空白不得往下 | ✅ 放行 |
| S-8.2 | 討論 agent | 方案檔仍進不去 | Read 2-decision | 改讀 specs／原始碼 | — | ✅ 核准格不能覆寫禁令 |
| S-8.3 | 討論 agent／owner | 未核不得當已授權 | Read 未核 path | 送核准卡或維持 Assumption | 顯性等 owner | ✅ 擋。Known limit:跳過 hook 硬讀不擋 |
| S-9.1 | Fast 實作者 | 寫 4 前先收完六問 | 跑 spec-gate | 對 diff 答六問 | 未收束不得進 R/S | ✅ 新式 fast 空白紅 |
| S-9.2 | Fast 實作者／owner | 等待誤標不能當純視覺 Fast | 填六問第 3=是 | owner 裁 full／mini／OC | 待裁期間不得開寫 | ✅ fixture 去向 fast+mini |
| S-1.1／S-1.4／S-2.2／S-2.3／S-3.1／S-3.2／S-3.4／S-3.5／S-4.2／S-4.3／S-4.4／S-5.2／S-5.3／S-6.2／S-6.3／S-6.4／S-7.2／S-7.3／S-8.4／S-9.3／S-9.4／S-9.5 | — | — | — | — | — | 不適用（4-spec Operational Context 標不適用或純字面／靜態牙） |

六條掃描:技術通過但人無法完成工作 — 未見（SKILL 入口舊句會誤導,但是節點正本已改,見 F-1）。看得到但沒有決策權 — Fast 命中去向仍要 owner 裁,牙擋待裁。等待誤標為完成 — S-9.2 命中第 3 問。系統外動作 — 訪談／回看／owner 核准卡可追。中斷恢復 — 改欄後重跑。資訊過期 — C7 過期 open 紅。

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 牙仍是三支既有 CLI;guard 讀 manifest,不經新 util／event bus 放行 2–7。無 `check-discovery-gaps.sh`。
2. **資料所有權被繞過寫入**:未命中 —— spec-gate／realworld 只讀;guard 不改目標檔。過期假設擋點在 spec-gate,不在 realworld（4-spec Boundary）。
3. **相容性破壞包成新增**:未命中 —— C1–C6 保留,只加 C7／C8／C9。realworld `MIN_CHECKS=174` 改成實數。guard 寫入洩漏掃描仍在;Read 只在 talk 游標在時發動。
4. **一致性邊界被拆解**:未命中 —— 無多筆寫入交易。核准格是人寫一格、guard 讀字面。
5. **宣告的 Test seam 未被使用**:未命中 —— fixture 目錄 `scripts/fixtures/discovery-gaps/` 就是契約 seam;T-1…T-10 Verify 真跑那三支牙,不是只數 selftest 字樣（T-9 真餵 Read）。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— ①A-2 仍只守對稱句,不還原對話;②guard 仍只在 talk 游標在時擋 Read,無 OS hook;③「不改語意／算不算高影響」仍人判;④審頁產器 8 框未改。C8／C9 收窄發動是 6-notes D-impl-2／D-impl-3（grandfather 既有 fixture）,不是把 Known limit 修掉。

無未經授權 Boundary 變更。無 🔴。C8／C9 收窄已記 L1,見 Known Limits。

## Standards Axis

產品樹 = `git diff --stat 2bfb906..fdbd569`（#286）。本 PR vs 合完 2c 的 main = 本審查檔 + twin。

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟡 | `skills/dev-talk/SKILL.md:102`;`guides/guide-dev-talk.html:197-198,225` | M-5／S-3.3 節點 `S1-survey.md:29-30` 已改「認可不是來源升格」。SKILL 入口與指南完成條件仍寫「認可後即已核事實／認可清單 = 已核事實」。T-3 為 N3 前綴同步了 SKILL／指南;T-4 Files 不含這兩檔,複製層漏改。人先讀 SKILL／指南會抄舊規則 | Human 三擇一:①修 SKILL 步 1 入口＋guide 表／原文與節點一致（不開新檢查家族）②明示 park（落點 Known Limits #12）③REQUEST_CHANGES 回 Stage 6 補複製層 | R-3／S-3.3／T-4 |
| F-2 | 🟡 | `example/contract-expiry-reminder/1-discussion.md:89,97-117` | S-1.3 THEN 第二句:若仍提 dashboard／卡片／URL,只准出現在 `## Requested solution` 且標未定案。Goals 已改口,但 Q3「本期只做站內 dashboard」與 AC-1…AC-5「從哪看」仍鎖 dashboard 通道。T-2 Verify 不查 AC。抄範例的人會把通道當驗收 | Human 三擇一:①park（接受 Q3／AC 是已核歷史觀測面;S-1.3 機械只鎖 Goals＋L119;落點 Known Limits #16）②L2 回 G2 加 S,要求 AC／Q 也不鎖通道③本 feat 外另開 slug 改 example AC。本 hop 不改產品碼 | R-1／S-1.3／M-2／T-2 |
| F-3 | 🟢 | `scripts/check-realworld.sh:259-271` | `detect_goals_wrong_column` 只咬第一句「我要 dashboard」或「我要 」開頭 + Requested 空。不是 dashboard／API 黑名單（A-1） | 接受。其他錯欄句靠 G1。可選加抽 S-1.4 fixture 含領域詞仍綠（不是 twin 第五格） | R-1／S-1.2／S-1.4／T-1 |
| F-4 | 🟡 | `scripts/check-spec-gate.sh:351-357` `fire_disp` | S-6.1 字面:凡 `lane: full` 缺 `## Real-world Disposition` 或去向空白 → spec-gate exit 1。實作 `fire_disp` 只對「新式」full（有 Assumption refs 或路徑含 `discovery-gaps`）發動。舊 full（如 `example/subsidy-3-0-plus/4-spec.md`）缺表 no-fire。本 feat fixture 有 refs,牙有咬到;契約字面比牙寬 | Human 三擇一:①park D-impl-3 grandfather（落點 Known Limits #7）②L2 改 S-6.1 寫明「僅新式 full」③加寬 C9 打所有 full（產品碼,本 hop 不做） | R-6／S-6.1／T-7 |
| F-5 | 🟢 | `scripts/check-py-floor.sh:294`;`hooks/devtalk-guard.sh` `<<'READ'` | #286 後續 commit 撤回抬地板:RW-DG 改 tag MUT;Read 只靠 INTERP;`MIN_HEREDOCS=222`。PF-2 牙留下 | 接受。符合 OC-1「不另造家族、不為新牙毀舊牙」 | 過程／T-9／T-3 |
| F-6 | 🟢 | `scripts/check-spec-gate.sh:307-311` C8 `fire_fast` | C8 只對新式 fast 發動（D-impl-2）。S-9.1 字面較寬;本 feat fixture 有 `feature:`＋ADDED,牙有咬到 | 接受為 L1。與 F-4 分開:三審 must-fix 點名的是 C9／S-6.1。見 KL-C8 | R-9／S-9.1 |

**Dependency Direction**:符合 —— realworld → 模板／example／fixture;spec-gate → 4-spec 正文 + `spec_profile()`;guard → manifest + talk 游標。無反向。無第四 CLI。

**Boundary Leakage**:符合 —— 無內部 struct 漏出;檢查輸出是 exit + 字樣。

**Data Ownership**:符合 —— spec-gate 擁有 G2 形狀;realworld 擁有教師地板;guard 擁有討論期擋讀。過期假設未塞進 realworld。

**Interface Stability**:符合 —— C1–C6 保留;寫入洩漏掃描保留;Read 加項且游標不在走舊邏輯。無 `check-discovery-gaps.sh`。

無 🔴。🟡 三條:F-1（SKILL／指南 S1 入口）、F-2（example Q3／AC 仍教 dashboard 通道）、F-4（C9 只打新式 full）。都不是未授權 Boundary 變更（節點／牙在契約內,複製層或發動收窄）。不得帶著未 park／未修的 🟡 勾「Design Boundary finding 全數處置」。

## Spec Axis

Variant B 偏置:先壓 A-1（不採黑名單）與 OC-1（只延三支既有牙）。

| R | 判定 | 出處 |
|---|---|---|
| R-1 分辨結果與構想 | **符合牙;活教師 AC／Q3 偏離一層（F-2 🟡）** | S-1.1 模板分欄;`S4-accept.md:20` 改問結果發生。S-1.2 同一入口指出錯欄,無 `check-discovery-gaps.sh`。S-1.3 Goals 三句已改口。**S-1.3 THEN 第二句**未落地:example Q3:89 與 AC:97-117 仍鎖 dashboard。**S-1.4** A-1 不採黑名單成立（可選加抽,不是 twin 第五格） |
| R-2 發現題不先塞推薦 | 符合 | N3 兩路徑;`禁附推薦`;S-2.2 單邊缺失紅;S-2.3 裁決附選不紅。Known limit ①維持:不還原對話 |
| R-3 高影響主張回來源或期限 | **偏離一層複製** | 牙與節點符合（S-3.1…S-3.5、S-8.4 同主張牙）。F-1:SKILL／指南入口仍教「認可後即已核事實」。機械 S-3.3 仍綠。不是 L2（R/S 沒翻） |
| R-4 過期假設擋 G2 | 符合 | C7 在 `check-spec-gate.sh`（不另造家族）。expired-open exit 1;resolved／oc-accepted 放行;四欄地板在 |
| R-5 verdict 一行 | 符合 | 殘行紅;完整行綠;無 Actor Coverage 全表;attestation 行仍在 |
| R-6 痛點列有去向 | **符合本 feat fixture;字面偏離（F-4 🟡）** | 本 feat 缺表紅;本方案處理要 R／S;非處理有 OOS／limit;第二鏈 `rg` 0。C9 `fire_disp` 只打新式 full,S-6.1 寫凡 full。Human 見 F-4 三擇一 |
| R-7 回看四欄 | 符合 | 模板／example 四欄在;有節缺門檻紅;結果入口 `history-append.sh`;無 lookback.md |
| R-8 核准後讀得到且方案檔仍禁 | 符合 | S-8.1／8.2／8.3 真跑 Read 三案 exit。2–7 硬擋,核准格不能覆寫。Known limit ②維持:無 OS hook |
| R-9 Fast 寫 4 前六問 | 符合（發動收窄已記） | 空白紅;等待誤標命中 Q3;待裁紅;全否可 Fast;本檔 full no-fire。C8 只對新式 fast 發動 = D-impl-2,見 KL-C8 |
| OC-1 三牙、不另造家族 | **符合**（Variant B 主壓） | `test ! -e scripts/check-discovery-gaps.sh`;`test ! -e scripts/check-evidence-allow.sh`。擋點只加在 `check-realworld.sh`／`check-spec-gate.sh`／`hooks/devtalk-guard.sh`（+ 已掛進的 devflow-check）。MIN_CHECKS=174 實數。PF-2 用 MUT／READ tag 保住舊牙,不抬地板假綠 |
| A-1 不採黑名單 | **符合**（Variant B 主壓） | 見 R-1／S-1.4。Out of Scope「dashboard／API 黑名單」未被實作偷偷做起來 |
| M-1…M-11 | 符合（M-5 複製層除外） | 活教師改口對得上各 M;M-5 節點改了、SKILL／指南入口沒改（F-1） |
| Design Boundary | 符合 | 見 Design Integrity Check。無未授權 Boundary。無悄悄修掉 Known design limit ①②③④ |
| 6-notes Deviations | **如實** | D-1…D-8 皆 L1,抽驗對得上 diff:4B 去 `RW-1`（`2-decision.md` 決策點 4）;guide／example 7-review html 回看表;2-decision.html 重生;MIN_CASES／MIN_HEREDOCS 記帳;embed 同形;5-tasks `status: approved`。D-impl-1…3 與 C8／C9／內嵌稿對得上。**沒有**把 F-1 寫進 Deviations —— 那是本 hop 自建,不是作者隱匿 L2 |

## 變更架構圖

產品（#286,已在 tip `fdbd569`）與本 hop 審查密封:

```
[check-realworld.sh]     MIN_CHECKS=174
    |  Goals 錯欄 / 不採黑名單
    |  發現｜裁決｜對稱
    |  高影響主張 / 點頭 / ticket
    |  verdict 一行 / 回看四欄
    +--> scripts/fixtures/discovery-gaps/
         goals-dashboard-in-wrong-column.md
         goals-outcome-with-requested-dashboard.md
         probe-decision-with-options.md
         user-report-only.md  nod-as-only-source.md
         enum-unknown.md  ticket-solution-as-fact.md
         unapproved-as-only-source.md
         verdict-accepted-only.md
         lookback-missing-threshold.md
         + spec-gate fixtures (assumption / disposition / fast-*)

[check-spec-gate.sh]     C1-C6 保留 + C7 C8 C9
    |  C7 Assumption refs
    |  C8 Fast early risk triage (lane:fast 新式)
    |  C9 Real-world Disposition (full 新式)
    +--> 同上 discovery-gaps spec-gate fixtures

[devtalk-guard.sh]       寫入洩漏保留 + Read 分支
    |  talk 游標?  2-7 硬擋  核准=是才放行
    +--> 1-discussion ## Evidence manifest
    +--> DEVTALK_MANIFEST / docs/dev/*/1-discussion.md
    +--> hooks/selftest.sh S-8.1..S-8.3

[_templates/1,2,3,4,7] ----example/contract-expiry-reminder----
[skills/dev-talk/N3 S1 S4] [skills/dev-talk/SKILL.md]
[skills/dev-flow/SKILL.md] [guides/guide-dev-talk.html]
[guides/guide-dev-flow.html]   (T-8 renderer twin;回看四欄)
[scripts/test-architecture-guards.sh]  RW-DG1/2 + seed N3
[scripts/check-py-floor.sh]            MIN_HEREDOCS=222 INTERP

#287 incoming(2c 合進,不是本 hop 撰寫):
[docs/dev/STATUS.md] [docs/dev/HISTORY.md]

本 hop(docs-only,不是產品碼):
[7-review.md]     Source SHA=e922c2b (第一份 7-review commit;再 commit 仍漂)
[7-review.html]   official G3 twin
```

無新公開 HTTP 端點、無新表、無第四檢查家族。改 Diff 必須改本圖。

## Diff(merge-base(main)..HEAD,逐檔折疊)

2c 合完後 HEAD=`37a4284` = `origin/main` tip。本 hop 相對 main 只會多本檔／twin。下面先摺 **#286 產品**（審查對象）,再摺本 hop。

<details>
<summary title="+267/-?; detect_goals_wrong_column + 11-17 節"><code>scripts/check-realworld.sh</code> (+267; <code>detect_goals_wrong_column</code>／主張牙／verdict／lookback)</summary>
<pre><span class="add">+def detect_goals_wrong_column(source):</span>
<span class="add">+    """構想寫進 Goals、Requested solution 缺或空 → 構想在錯欄。</span>
<span class="add">+    不採 dashboard／API 黑名單:結果句即使含這兩個詞,只要構想在 Requested</span>
<span class="add">+    solution,不算錯欄。"""</span>
<span class="add">+    ...</span>
<span class="add">+    return first == "我要 dashboard" or first.startswith("我要 ")</span>
<span class="add">+MIN_CHECKS = 174</span></pre>
</details>

<details>
<summary title="+132; C7 C8 C9"><code>scripts/check-spec-gate.sh</code> (+132; <code>C7</code>／<code>C8</code>／<code>C9</code>)</summary>
<pre><span class="add">+#   C7 Assumption refs:open + 過期 ... → FAIL</span>
<span class="add">+#   C8 Fast early risk triage:僅 lane:fast + 新式 ... → FAIL</span>
<span class="add">+#   C9 Real-world Disposition:full + 新式 ... → FAIL</span>
<span class="add">+fire_fast = prof["lane"] == "fast" and has_feature and added_i is not None</span>
<span class="add">+fire_disp = prof["lane"] == "full" and (</span>
<span class="add">+    assume_i is not None or "discovery-gaps" in spec_path)</span></pre>
</details>

<details>
<summary title="+79; Read 分支"><code>hooks/devtalk-guard.sh</code> (+79; Read + 方案檔硬擋)</summary>
<pre><span class="add">+if sol.search(posix):</span>
<span class="add">+    print("⛔ devtalk-guard:方案檔仍禁讀...", file=sys.stderr)</span>
<span class="add">+    raise SystemExit(2)</span>
<span class="add">+            if approved == "是":</span>
<span class="add">+                raise SystemExit(0)</span></pre>
</details>

<details>
<summary title="教師改口"><code>_templates/1-discussion.md</code> <code>_templates/2-decision.md</code> <code>_templates/3-prototype.md</code> <code>_templates/4-spec.md</code> <code>_templates/7-review.md</code></summary>
<pre><span class="add">+## Requested solution</span>
<span class="add">+## Evidence manifest</span>
<span class="add">+## Fast early risk triage</span>
<span class="add">+## Real-world Disposition</span>
<span class="add">+| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |</span>
<span class="add">+- Human verdict: ... | role=&lt;…&gt; | scenario=&lt;…&gt;</span></pre>
</details>

<details>
<summary title="N3／S1／S4／Fast 入口"><code>skills/dev-talk/nodes/N3-probe.md</code> <code>S1-survey.md</code> <code>S4-accept.md</code> <code>skills/dev-flow/SKILL.md:36</code></summary>
<pre><span class="add">+- `發現｜` ...禁附推薦。</span>
<span class="add">+- `裁決｜` ...可附選項</span>
<span class="add">+   認可確認的是理解對了,不是來源升格。</span>
<span class="add">+①從哪裡看出結果發生</span>
<span class="add">+→ **進 4 前六問**(Fast early risk triage:…)</span></pre>
</details>

#286 其餘 fixture／example／guide／`check-py-floor.sh`／`test-architecture-guards.sh`／6-notes 見 `git diff --stat 2bfb906..fdbd569`（48 檔）。本 hop 落檔後本節加 `7-review.md`／`7-review.html`。

## Verdict

**PRE-REVIEW** —— 不是 G3 PASS。Implementer B 不得代填 Human 判定。

建議下一棒:適格人類 reviewer（≠ rick 若他要避 owner 自審;或 owner 自審但必須另寫限制聲明）。Agent 再審必須 fresh context。

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 35 S 機械牙／教師原文／Read 三案皆綠 | Coverage + 現象證據 |
| 既有全綠 | realworld 174/174;本 slug spec-gate 9/9;S-2.2 突變紅 | Verification Evidence |
| 現象證據逐 S 相符 | 35 列已填;S-1.2 套件 vs「exit ≠ 0」已說明 | 現象證據表 |
| Evidence 契約 | gauntlet 61 checks、1 violation:E7 幽靈 token（附錄 A3）。`--source-sha e922c2b`。不是產品牙紅 | 附錄 A3 |
| 無 🔴 | 無 🔴。🟡 F-1／F-2／F-4 待 Human park 或修 | Standards Axis |
| 出貨樹=審過的樹 | 2c 合 `37a4284` 在 Fresh 之前;Source SHA 重綁 `e922c2b` | 2c 節 |

PASS 條件未全滿足（Human 未判、F-1 未處置、gauntlet 幽靈 token、Source SHA 將漂）。故 **不得** 寫 PASS。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 重綁 Source SHA=`e922c2b0e5e39b2bafaa5c6aaf5a7b5f3303af8e` 之後若再 commit,HEAD 又漂。Gauntlet `--source-sha` 必須等於當下 HEAD | 中 | 下一棒重綁 Source SHA + 重跑 gauntlet。park:本節 |
| 2 | 4-spec Known design limit ①:A-2 誘導無法從最終 md 還原;硬 gate 只守對稱句與「發現題附推薦」形 | 低（契約已列） | 維持。不要加對話還原器 |
| 3 | 4-spec Known design limit ②:guard 只在 talk 游標在時擋 Read;人跳過 hook 硬讀方案檔,本 feat 不新造 OS hook | 中（契約已列） | 維持。owner 不能接受就另開 slug,不要在本 feat 加 OS hook |
| 4 | 4-spec Known design limit ③:「不改語意」與「算不算高影響」仍是人判 | 低 | 維持 |
| 5 | 4-spec Known design limit ④:審頁產器行為圖硬切 8 框;R-5 SHALL 寫在 R-4 框 | 低 | 維持。本 hop 不改產器 |
| 6 | KL-C8／D-impl-2:C8 只對 `lane: fast` 且 `feature:` + `## ADDED Requirements` 發動;legacy fast fixture grandfather | 中 | 已如實記 6-notes。新 Fast 4-spec 必須有 feature:＋ADDED,否則六問牙 no-fire |
| 7 | KL-C9／D-impl-3／F-4 🟡:`scripts/check-spec-gate.sh` `fire_disp`（約 L351–357）只對「新式」full 發動（有 Assumption refs 或路徑含 `discovery-gaps`）;`example/subsidy-3-0-plus/4-spec.md` grandfather。S-6.1 字面「凡 full 缺表就紅」比牙寬 | 中 | Human 三擇一:①park 本條為 D-impl-3 ②L2 改 S-6.1 寫明「僅新式 full」③加寬 C9 打所有 full（產品碼,本 hop 不做）。未選不得勾 Boundary 處置 |
| 8 | L1 D-1:本 slug `2-decision.md` 4B 原文 `RW-1` 改成「第二鏈編號」,只為 S-6.4 `rg` 零命中 | 低 | 已如實。4A 未動 |
| 9 | L1 D-2／D-5:T-8 回看表不用 `###`(parity);renderer 重生 `guides/guide-dev-flow.html` 與 example 7-review.html | 低 | 已如實。欄位字面仍在 |
| 10 | L1 D-7:RW-DG 改 `<<'MUT'`;guard Read 改 `<<'READ'`;`MIN_HEREDOCS=222`。撤回抬地板 | 低 | 已如實。PF-2 牙留下 |
| 11 | L1 D-8:5-tasks frontmatter 改 `approved`（graph P0） | 低 | 已如實。不是 G3 |
| 12 | F-1:SKILL／指南 S1 入口仍寫認可=已核事實 | 中 | 見 Standards F-1。owner park 或修複製層後才能勾 Boundary 處置 |
| 13 | 4-spec Out of Scope／Disposition 仍待驗三列（OC-3）:採用現場仍把解法寫進 Goal;現場發現題仍附推薦;Fast 因檔數少漏判互動 | 中（契約已列） | 回看四欄追;本 slug 不捏訪談 |
| 14 | `check-py-floor.sh` 本環境缺 Python 3.9–3.11 → exit 2;全套 `test-architecture-guards.sh` 未當正式綠（同 6-notes Self-Review ⑧） | 低（ENV） | 有 3.9–3.11 的機器重跑。本 hop 隔離做了 S-2.2 兩案 |
| 15 | 本環境無 `devflow-exec.sh review` 武裝（無 `.devflow/exec.json`） | 低 | 讀取順序已落檔。有 runtime 的機器可補武裝 |
| 16 | F-2 🟡:`example/contract-expiry-reminder/1-discussion.md` Q3:89 + AC:97–117 仍教 dashboard／渠道,對不上 S-1.3 THEN 第二句（若仍提 dashboard／卡片／URL,只准出現在 `## Requested solution` 且標未定案） | 中 | Human 三擇一:①park 本條（接受 Q3／AC 是已核歷史觀測面）②L2 回 G2 加 S,要求 AC／Q 也不鎖通道③本 feat 外另開 slug 改 example AC。本 hop 不改產品碼 |

已解除的用刪除線保留 —— 本輪無已解除列。

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**:無未授權 Boundary。🟡 三條待 Human park 或修:F-1（KL #12）／F-2（KL #16）／F-4（KL #7）。未 park／未修不得勾
- [ ] Quiz（不可逆:方法論教師 + 公開檢查契約）:見附錄 A4。Human 全對才准 merge
- [x] 整合回歸已在 Final Fresh **之前**完成:2c 結論（三個 SHA + ref）在 Verification Evidence。`#287` `37a4284` 已在 tip。本 hop must-fix 後重綁 Source SHA。Verdict 後禁止再改產品碼
- [ ] PR → develop／本專案 main（feature branch,禁直上 master）。本 hop brief:Draft PR,Do not merge
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md` —— n-a:本 repo 無 `docs/specs/` living spec（4-spec 已寫）
- [ ] STATUS.md 已更新為 shipped —— **不做**。brief:No STATUS／HISTORY。incoming `#287` 只記 Stage 6,不是本 hop shipped
- [ ] 7-review frontmatter status: shipped —— **不做**。維持 `draft` + `PRE-REVIEW`
- [x] 7-review.html 已產生（build-gate-twin.py;含變更架構圖）
- [ ] feature branch 已刪／worktree 已清 —— **不做**。Draft PR 未 merge

回看約定

| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| 2026-10-13 | rick | 下一場採用 Stage 1:`## Goals` 是否仍把通道當目標;N3 問句是否仍附推薦;SKILL 步 1 入口是否仍寫認可=已核事實 | 抽 3 份新 1-discussion,若 ≥2 份 Goals 仍鎖通道,或 SKILL:102 仍是舊句 → 重開 R-1／R-3 |

結果到期用 `scripts/history-append.sh` 追加,不另造永久 lookback 檔。回看日未到不得把九缺口寫成已改善。

## 附錄:本輪特有

### A1　Variant B:A-1 不採黑名單 + OC-1 三牙

這是本 hop 要人先看的爭點。

**A-1**（已拒 dashboard／API 黑名單）落地在 `scripts/check-realworld.sh:260-271`。錯欄條件是:Goals 第一句存在 **且** Requested solution 缺或空 **且**（第一句 ==「我要 dashboard」或 startswith「我要 」）。S-1.4 fixture 正文有 dashboard／API,構想在 Requested solution → 不紅。抽驗:`goals-outcome-with-requested-dashboard.md:3-10`。

**OC-1**（只延三支既有牙）:本 hop 親跑 `test ! -e scripts/check-discovery-gaps.sh`、`test ! -e scripts/check-evidence-allow.sh`。S-1.2／S-2.*／S-3.*／S-5.*／S-7.*／S-8.4 走 `check-realworld.sh`。S-4／S-6／S-9 走 `check-spec-gate.sh`。S-8.1…S-8.3 走 `devtalk-guard.sh`。沒有第四入口。

S-1.2 THEN 寫「exit ≠ 0」。實作選擇與 T-1 Verify 相同:套件綠、fixture 必須被指出錯欄、stdout 含「構想在錯欄」。這不是黑名單,也不是第二家族。

### A2　F-1 SKILL／指南 S1 入口漂移（本 hop 自建,6-notes 未列）

`skills/dev-talk/nodes/S1-survey.md:29-30`（T-4 Files 內）:

> 認可確認的是理解對了,不是來源升格。認可後清單不得當唯一來源

`skills/dev-talk/SKILL.md:102`（T-4 未改）:

> 入口摘要:…認可後即已核事實

`guides/guide-dev-talk.html:197` 完成條件「認可清單 = 「已核事實」」;`:198` 原文 blockquote 抄 SKILL 舊句。

T-3 Boundaries 自己寫過:「指南抄的是 SKILL 摘要,只改指南會漂」。N3 做了同步,S1 沒做。牙仍擋點頭獨源,所以不是 🔴。人抄 SKILL／指南會把認可升格教回去,所以是 🟡。

6-notes Deviations 沒寫這條。不是作者隱匿 L2（R/S 沒翻、節點已改）;是複製層漏網。本 hop 如實補上。

### A3　Required layers 幽靈 token

`4-spec.md:759` Required layers 用全形 `／` 連三牙,後面括號說明含全形 `；`。gauntlet `tokenize_layer_field` 認 `；` 為分隔,切成:

1. `check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支`
2. `` check-stage4-rs-contract.sh` 是本 hop 審頁形狀，不落地缺口牙，不列入本欄） ``

第二 token 是解析事故,4-spec 自己說不列入本欄。本檔不給它假 pass。Final Fresh gauntlet 對本檔很可能 E7。這是 PRE-REVIEW 的另一個理由,不是產品牙紅。

修法（不在本 hop）:4-spec Required layers 改成頓號分隔三個短名,說明放到下一行或 `——` 之後。那是 L2 形狀（動 Verification Profile 欄）,要回 G2。

### A4　Quiz（給 approver;不可逆方法論改動）

1. 錯欄牙掃的是 dashboard／API **詞黑名單**,還是分欄形狀?答案必須指出 `detect_goals_wrong_column` 與 S-1.4 fixture。
2. 九缺口的機械入口是哪三支?有沒有 `check-discovery-gaps.sh`?
3. owner 把 2-decision 寫進 Evidence manifest 且核准=是,Read 會怎樣?哪一支、exit code?
4. Fast 六問第 3 題「是。等待被顯示成完成」、去向寫 Fast 或待裁,spec-gate 會怎樣?
5. 本檔為什麼不是 G3 PASS?至少要提到 PRE-REVIEW、F-1、或幽靈 token／SHA 會漂 其中兩件。

### A5　對照作者（N4;先自建矩陣後才讀）

| 作者主張 | 本 hop 裁定 |
|---|---|
| T-1…T-10 review PASS;不是 G3 | 同意。本 hop 也不發明 G3 |
| 無第四家族;MIN_CHECKS=174 | 同意。親跑 |
| D-1…D-8 皆 L1 | 同意。抽驗 4B 改口、回看 twin、MUT／READ、5-tasks approved |
| D-impl-2／3 C8／C9 收窄 | 同意為 L1。Spec 字面較寬,已進 Known Limits,不升 L2 |
| Self-Review ⑧ architecture-guards 因缺 3.9–3.11 未正式綠 | 同意。本 hop 同 ENV;改隔離跑 S-2.2 |
| 未列 SKILL／指南 S1 舊句 | **補 F-1**。不是 L2,但是 🟡 |
| Files 聯集外的 L1 檔 | 同意範圍:2-decision.md／html、guide-dev-flow.html、example 7-review.html、check-py-floor.sh、5-tasks status。6-notes 恆許 |

無作者把 L2 寫成 L1。無 Decisions 實為翻 R/S。
