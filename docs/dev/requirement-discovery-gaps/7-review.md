---
feature: requirement-discovery-gaps
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: rick
reviewers: [implementer-A-stage7]
updated: 2026-09-13
---

# 7. 驗證 —— **不是 G3 PASS**（Stage 7 Implementer A PRE-REVIEW）

> 本檔是獨立 fresh-context Stage 7 Implementer A 的交接審查，**不是 Human G3 PASS**。
> 頂欄 `verdict: PRE-REVIEW`。禁止把本 hop 讀成出貨核准。
> 建議下一棒：適格人類 reviewer（owner `rick` 或指定人）依閱讀動線第 5 步抽驗後，才把 `verdict` 改成 PASS／REQUEST_CHANGES／HOLD。
> 產品碼已在 tip `#286`=`fdbd569`。本 hop **只寫** `7-review.md` + `7-review.html`，不改 STATUS／HISTORY，不發明新 R/S，不開第二檢查家族。

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
> | 5 | **抽驗一列** | 從 Coverage Matrix / Standards Axis / Spec Axis 任挑一列,照它給的 `檔:行` 去看。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步** —— verdict 可以寫得漂亮,`檔:行` 對不上就是對不上。
> 三大節(Spec Axis / Coverage Matrix / Standards Axis)通常佔全文四成以上,
> 用途是**查證庫**(懷疑某一格時去查),不是通讀對象。
>
> 建議抽驗:`Coverage Matrix` 中位列 **S-4.1** → `scripts/check-spec-gate.sh:251-292` + fixture `scripts/fixtures/discovery-gaps/assumption-expired-open.md:29`（親跑 exit 1,輸出 `Assumption 過期仍 open`）。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-A-stage7`（獨立 fresh-context Cloud Agent A;`bc-b68d44ad-3771-4b5b-b50e-d12a30a282b9`）。**≠** Stage 6 Implementer A（#286 session `bc-70142fc5-585b-493c-9526-bff74bcfe370`;6-notes frontmatter owner=`implementer-a`）。產品 owner 欄仍是 `rick`。 |
| Human G3 | **未寫**。本 hop 不得發明 PASS。`verdict: PRE-REVIEW`。 |
| 讀取順序(可查) | ①`4-spec.md`（G2 PASS、35 S） ②`5-tasks.md`（T-1～T-10） ③#286 產品檔清單（48 檔;merge `fdbd569`） ④三支既有牙 + `scripts/fixtures/discovery-gaps/` ⑤親跑 T-1～T-10 Verify + 4-spec entry point + 步 2c 兩次座標相同 → **之後才** ⑥`review-unlock` 讀 6-notes Self-Review |
| 圍欄 | `hooks/devflow-exec.sh review requirement-discovery-gaps` 武裝後再 `review-unlock`。doctor:`COMPATIBLE`（契約 2.0.0,runtime 3.23.4,gauntlet 1.3.3）。exec-state 提示契約 `exec-v3`／runtime `exec-v4` 雙軌,武裝有效。 |
| 本輪性質 | 產品已在 `origin/main` `#286`。本 hop 只產 Stage 7 審查稿。**不是 G3 PASS**。不改 STATUS／HISTORY。 |
| 可信／打折 | 機械數字（exit／checks／字樣）以本 hop 親跑為準。F-id 分級與「沒想到的事」留給人類 G3。本審查者 ≠ Stage 6 實作 session,不是 owner 自審。 |

## Coverage Matrix

自建（grep 4-spec 35 條 S ↔ 三支既有牙／fixture／`rg`;**未先讀** 6-notes Self-Review）。無 `scripts/check-discovery-gaps.sh`。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/check-realworld.sh:294-299`;模板 `_templates/1-discussion.md:86-90`（`## Goals` + `## Requested solution`）;S4-accept `skills/dev-talk/nodes/S4-accept.md:20-23` | ✅ |
| S-1.2 | `scripts/check-realworld.sh:259-292`;fixture `scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md:4`;親跑印 `構想在錯欄` | ✅ |
| S-1.3 | `scripts/check-realworld.sh:300-304`;example Goals `example/contract-expiry-reminder/1-discussion.md:73-76`;Requested `78-79`。THEN 第二句見 F-1 🟡 | ✅ |
| S-1.4 | `scripts/check-realworld.sh:290`;fixture `scripts/fixtures/discovery-gaps/goals-outcome-with-requested-dashboard.md:3-10`;不採黑名單 | ✅ |
| S-2.1 | `skills/dev-talk/nodes/N3-probe.md:23-25` + `:44-45`;`skills/dev-talk/SKILL.md:104`;`scripts/check-realworld.sh:313-320` | ✅ |
| S-2.2 | `scripts/test-architecture-guards.sh:732-751`（RW-DG1／RW-DG2）;`scripts/check-realworld.sh:313-314`。本 hop 隔離突變：刪一邊前綴 → 對稱牙必紅 | ✅ |
| S-2.3 | fixture `scripts/fixtures/discovery-gaps/probe-decision-with-options.md:2-3`;`scripts/check-realworld.sh:333-335`;realworld 174/174 含此項 | ✅ |
| S-3.1 | fixture `scripts/fixtures/discovery-gaps/user-report-only.md:4`;牙 `scripts/check-realworld.sh:373-378` + `:436-437` | ✅ |
| S-3.2 | 內嵌好卡 `scripts/check-realworld.sh:421-429` + `:444-445`（Observed+path 與 Assumption+期限） | ✅ |
| S-3.3 | fixture `scripts/fixtures/discovery-gaps/nod-as-only-source.md:6-8`;牙 `scripts/check-realworld.sh:386-387` + `:440`;S1 `skills/dev-talk/nodes/S1-survey.md:29-30` | ✅ |
| S-3.4 | fixture `scripts/fixtures/discovery-gaps/enum-unknown.md:6`;牙 `scripts/check-realworld.sh:338` + `:384-385` + `:441` | ✅ |
| S-3.5 | 內嵌低影響 `scripts/check-realworld.sh:431-435` + `:446` | ✅ |
| S-4.1 | `scripts/check-spec-gate.sh:251-292` C7;fixture `scripts/fixtures/discovery-gaps/assumption-expired-open.md:29`;親跑 exit 1,`Assumption 過期仍 open(2020-01-01)` | ✅ |
| S-4.2 | 同 C7;fixture `scripts/fixtures/discovery-gaps/assumption-resolved.md:29`;親跑 exit 0,9/9 | ✅ |
| S-4.3 | 同 C7;本檔 `docs/dev/requirement-discovery-gaps/4-spec.md:605-607` 三列 `oc-accepted`;親跑 slug spec-gate 9/9 | ✅ |
| S-4.4 | `scripts/check-realworld.sh:450-453`;模板 `_templates/1-discussion.md:75-78`;example `:62-64` | ✅ |
| S-5.1 | fixture `scripts/fixtures/discovery-gaps/verdict-accepted-only.md:4`;牙 `scripts/check-realworld.sh:462-474` | ✅ |
| S-5.2 | 完整行內嵌 `scripts/check-realworld.sh:472-476`;example `example/contract-expiry-reminder/3-prototype.md:142` | ✅ |
| S-5.3 | `scripts/check-realworld.sh:458-459`;`_templates/3-prototype.md:128` 有 `role=`／`scenario=`,無 Actor Coverage 全表必填 | ✅ |
| S-6.1 | `scripts/check-spec-gate.sh:348-372` C9;fixture `scripts/fixtures/discovery-gaps/disposition-missing.md` 無表;親跑 exit 1,`缺 ## Real-world Disposition`。射程收窄見 F-2 🟡 | ✅ |
| S-6.2 | 同 C9;`scripts/check-spec-gate.sh:368`;本檔 disposition `4-spec.md:615` 下落 `S-2.1`；slug 親跑 C9 綠 | ✅ |
| S-6.3 | 同 C9;`scripts/check-spec-gate.sh:370`;本檔 `:624-629` 刻意維持／仍待驗落到 Out of Scope／Known limit | ✅ |
| S-6.4 | 本 hop `rg -n 'RW-[0-9]'` 對模板／本 slug／example 2／4 六路 = 0 命中 | ✅ |
| S-7.1 | `scripts/check-realworld.sh:478-481`;`_templates/7-review.md:344-348`;example `example/contract-expiry-reminder/7-review.md:274-275` | ✅ |
| S-7.2 | fixture `scripts/fixtures/discovery-gaps/lookback-missing-threshold.md:12-14` 缺「低於何值重開」;牙 `scripts/check-realworld.sh:486-497` | ✅ |
| S-7.3 | `scripts/check-realworld.sh:482-483`;模板 `:345-346` 含 `history-append.sh`、無 `lookback.md`;本 hop `rg lookback.md` 活教師 0 | ✅ |
| S-8.1 | `hooks/devtalk-guard.sh:13-85`;fixture `scripts/fixtures/discovery-gaps/guard-read-1-discussion.md:6`;親跑 Read `_templates/1-discussion.md` rc=0;selftest `hooks/selftest.sh:563-564` | ✅ |
| S-8.2 | 同 guard `:33-40`;fixture `:7` 核准誤寫「是」;親跑 Read `2-decision.md` rc=2,stderr 含 `方案檔`;selftest `:565-566` | ✅ |
| S-8.3 | 同 guard `:82-84`;fixture `:8` 核准=`未核`;親跑 Read `notes/review-requirement-discovery-gaps.md` rc=2,`未核路徑`;主張牙 `scripts/check-realworld.sh:438-439` | ✅ |
| S-8.4 | fixture `scripts/fixtures/discovery-gaps/ticket-solution-as-fact.md:5-8`;牙 `scripts/check-realworld.sh:390-393` + `:442-443` | ✅ |
| S-9.1 | `scripts/check-spec-gate.sh:294-314` C8;fixture `scripts/fixtures/discovery-gaps/fast-blank-triage.md` 無六問表;親跑 exit 1,`六問缺表` | ✅ |
| S-9.2 | fixture `scripts/fixtures/discovery-gaps/fast-wait-shown-as-done.md:15` 第 3 問=`是。等待被顯示成完成`;`:19` 去向=`fast+mini`（≠ Fast／待裁） | ✅ |
| S-9.3 | 同 C8 `:341-343`;fixture `scripts/fixtures/discovery-gaps/fast-hit-no-dest.md:19` 去向=`待裁`;親跑 exit 1,`不得空白／待裁／Fast` | ✅ |
| S-9.4 | 同 C8;fixture `scripts/fixtures/discovery-gaps/fast-visual-all-no.md:13-19` 全否 + 去向 Fast;親跑 exit 0,9/9 | ✅ |
| S-9.5 | 同 C8 `:308-309`;本檔 `4-spec.md` `lane: full` 無六問表;親跑 C8 `full 缺表 no-fire` | ✅ |
| 既有測試套件(回歸) | 4-spec entry point 兩指令 + T-1～T-10 Verify + 無第四家族 | ✅ |

**Verify 親跑**（5-tasks 原指令;2026-09-13;2c 兩次 `N_A_NO_INCOMING` 之後、Fresh 綁 `fdbd569`）:

```
T-1-wired
T-2-ok
T-3-skill / T-3-wired
T-4-skill / T-4-wired
assumption-expired-open exit=1 (C7 FAIL; 8/9)
assumption-resolved exit=0 (9/9)
slug 4-spec exit=0 (9/9, 35 S)
T-5-floor / T-6-template / T-6-wired
disposition-missing exit=1 (C9 FAIL; 8/9)
RW-[0-9] = 0
T-8-floor; lookback.md = 0
fast-blank exit=1; fast-hit-no-dest exit=1; fast-visual exit=0
T-10-ok
T-9-read-ok (S-8.1 rc=0; S-8.2 rc=2 方案檔; S-8.3 rc=2 未核)
check-realworld 174/174 (地板 174;初跑缺 markdown-it-py 為 ENV,pip 後綠)
NO scripts/check-discovery-gaps.sh
```

## Verification Evidence

- Source SHA: fdbd5696aeb491538276caa09370744370189601
- Final Fresh Run ID: 2026-09-13T0705Z-impl-A-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && bash scripts/check-realworld.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0（Fresh 前 pip;doctor 初檢未裝）; contract 2.0.0; runtime 3.23.4; git 2.43.0; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md` | pass | exit 0;9/9;35 條 S;C7／C8／C9 綠 | |
| check-realworld | `bash scripts/check-realworld.sh` | pass | exit 0;174/174（地板 174）;stdout 含 `構想在錯欄` | |
| devtalk-guard | T-9 Verify:talk 游標 + `DEVTALK_MANIFEST` 對三路徑餵 `tool_name=Read` | pass | 3/3:核准=是 rc=0;方案檔 rc=2;未核 rc=2 | |
| check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支 | 同上三列 Fresh 入口（4-spec Required 欄被 gauntlet 在全形分號切開的第一個 token;不是第四家族） | pass | 三牙合計 9/9 + 174/174 + 3/3 | |
| check-stage4-rs-contract.sh` 是本 hop 審頁形狀，不落地缺口牙，不列入本欄） | 4-spec 原文把這句標「不列入本欄」;parser 因 `；` 誤切。Fresh 仍是三牙,本 hop 不把審頁形狀當缺口牙 | pass | 0 第四家族;審頁牙未當缺口入口 | |
| Supply chain | `test ! -e scripts/check-discovery-gaps.sh` + `rg RW-[0-9]` 六路 | pass | 第四家族 0;第二鏈 0 命中 | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

本環境 doctor 初檢 `markdown-it-py 未裝`;Fresh 前已 `pip install 'markdown-it-py==4.0.0'`。這是 runner 相依,不是產品碼。realworld 第一次 173/174 即此 ENV,重跑 174/174。

### 2c 整合結論

本 Stage 7 分支從 `#286` tip `fdbd569` 切開。產品已在 `origin/main`。Fresh **之前**連跑兩次,STATUS／三 SHA／ref 完全相同。不合併（N_A）。

- STATUS: N_A_NO_INCOMING
- FORK / HEAD / INTEGRATION / REF: fdbd5696aeb491538276caa09370744370189601 / fdbd5696aeb491538276caa09370744370189601 / fdbd5696aeb491538276caa09370744370189601 / refs/remotes/origin/main
- 恢復: n-a（分岔後對方零新 commit）

```
結論:STATUS=N_A_NO_INCOMING FORK=fdbd5696aeb491538276caa09370744370189601 HEAD=fdbd5696aeb491538276caa09370744370189601 INTEGRATION=fdbd5696aeb491538276caa09370744370189601(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

第二次座標逐字相同。本 hop 開工 `git rev-parse HEAD`=`fdbd5696aeb491538276caa09370744370189601`。本 docs commit 落地後 HEAD 會再漂 —— Known Limits ②。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得把構想寫進 Goals 還當已完成分欄（S-1.2） | check-realworld S-1.2;fixture 錯欄 exit 形 + 字樣 `構想在錯欄` | pass |
| 不得用 dashboard／API 黑名單誤殺結果句（S-1.4） | check-realworld S-1.4;outcome fixture 不紅 | pass |
| 不得讓發現題附推薦仍當硬規則（S-2.1） | N3-probe:23-25;realworld :315 | pass |
| 不得把點頭當唯一來源（S-3.3） | realworld :440;nod fixture | pass |
| 不得讓過期 open Assumption 通過 spec-gate（S-4.1） | spec-gate C7;expired-open exit 1 | pass |
| 不得只寫 ACCEPTED + 日期當完整 verdict（S-5.1） | realworld :473-474;殘行 fixture | pass |
| 不得讓痛點列去向空白或發第二鏈編號（S-6.1、S-6.4） | spec-gate C9 + `rg RW-[0-9]`=0 | pass |
| 不得另造 lookback 永久檔（S-7.3） | realworld :482;活教師 `lookback.md`=0 | pass |
| 不得讀 2–7 方案檔或未核路徑當已授權（S-8.2、S-8.3） | guard Read 親跑 rc=2 兩案 | pass |
| 不得把 Fast 空白六問當已分診（S-9.1） | spec-gate C8;fast-blank exit 1 | pass |
| 不得新造檢查家族、不得本 hop 改 STATUS／模板正本、不得發明 G3 | `test ! -e check-discovery-gaps.sh`;本 hop 只寫 7-review*;verdict PRE-REVIEW | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 hop 不是 dev-run 引擎案。欄位留空。#286 為手動實作（Stage 6 sequential T-1…T-10）。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

reviewer 親自重跑;不採信 6-notes 貼的文字。CLI／字面牙,無 GUI。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 改後三檔原文：兩節名 + Goals／S4-accept 不再要求通道 | 模板 `:86-90` 兩節都在;驗收雛形 `:110` 改問結果發生;S4-accept `:20`「從哪裡看出結果發生」;T-2-ok | ✅ |
| S-1.2 | 指定檢查 exit 與 stderr 含 `構想在錯欄` 或 `Requested solution` | realworld 印 `構想在錯欄:goals-dashboard-in-wrong-column`;fixture `:4` 字面「我要 dashboard」;174/174 | ✅ |
| S-1.3 | 改後 example Goals／Requested／Interview | Goals `:73-76` 無登入／點擊／一眼可見;Requested `:79`「未定案：站內 dashboard」;Interview `:133` 不得當已核目標。AC `:98-117` 仍寫 dashboard —— F-1 | ✅ |
| S-1.4 | exit 0 且不因 dashboard／API 含錯欄字樣 | outcome fixture 第一句是結果;Requested 有未定案 dashboard;realworld S-1.4 check 綠 | ✅ |
| S-2.1 | 改後 N3 與指南對稱句 | N3 `:23-25` 發現禁推薦、裁決可附;`:45` 兩輪標輔助;SKILL `:104` 入口摘要同期 | ✅ |
| S-2.2 | 隔離複本刪一邊前綴 → exit ≠ 0 且含缺邊字樣 | 隔離突變：刪 `發現｜` → 只剩裁決;刪 `裁決｜` → 只剩發現。對稱 check `:313-314` 必紅。牙接線 `:732-751` | ✅ |
| S-2.3 | 裁決附選仍綠 | probe fixture 兩前綴都在;裁決行附三選;realworld `:335` 綠 | ✅ |
| S-3.1 | 缺來源且缺期限 exit ≠ 0,含來源／Assumption／期限 | user-report-only 只寫「使用者反映」;realworld `:437` 綠（必紅項） | ✅ |
| S-3.2 | 有來源或有期限都 exit 0 | 內嵌 Observed+`path:L12` 與 Assumption+`stage-2` 四欄;` :444-445` 綠 | ✅ |
| S-3.3 | 點頭獨源 exit ≠ 0,含點頭 | nod fixture 來源=`使用者點頭`;`:440` 含「點頭」 | ✅ |
| S-3.4 | 集合外 exit ≠ 0,含枚舉 | enum fixture 狀態=`Unknown`;`:441` 含「枚舉」 | ✅ |
| S-3.5 | 普通 Context 無枚舉仍綠 | 內嵌 path:L 無風險=高 + 高影響列齊;`:446` 綠 | ✅ |
| S-4.1 | spec-gate exit 1,含 Assumption／過期／open | expired-open 親跑 exit 1;`L29:Assumption 過期仍 open(2020-01-01)` | ✅ |
| S-4.2 | 不得只因 resolved 列 exit 1 | resolved fixture 親跑 9/9 exit 0 | ✅ |
| S-4.3 | oc-accepted 放行 | slug 4-spec 三列 `oc-accepted`;C7 綠;9/9 | ✅ |
| S-4.4 | 模板／範例含四欄字面 | 兩檔都有「若為假影響什麼／影響級／怎麼驗／何時／由誰驗」;T-5-floor | ✅ |
| S-5.1 | 殘行 exit ≠ 0,含 role 或 scenario | verdict-accepted-only 只有 ACCEPTED + attestation;`:474` 必紅項綠 | ✅ |
| S-5.2 | 完整行不得只因該行紅 | 內嵌 `ACCEPTED &#124; role=Fast 實作者 &#124; scenario=AC-9`;`:476` 綠 | ✅ |
| S-5.3 | 零命中「本包必填全表」;role／scenario 在 | 模板 `:128` 有 role／scenario;「Actor Coverage」不在模板;` :458-459` | ✅ |
| S-6.1 | spec-gate exit 1,含 Disposition 或去向 | disposition-missing 親跑 exit 1;`缺 ## Real-world Disposition 或 去向空白` | ✅ |
| S-6.2 | 下落含 R-／S- 則該列不紅 | slug `:615` `S-2.1、S-2.2`;C9 綠 | ✅ |
| S-6.3 | 非處理有 OOS／limit／slug | slug `:624-629`;C9 綠 | ✅ |
| S-6.4 | `rg RW-[0-9]` 空 | 六路 0 命中 | ✅ |
| S-7.1 | 模板／範例四欄都在 | 兩檔四欄字面齊;T-8-floor | ✅ |
| S-7.2 | 有節缺欄紅;舊檔無節不發動 | lookback fixture 缺「低於何值重開」;`:496` 必紅;舊形 `:497` 不誤殺 | ✅ |
| S-7.3 | 零命中另造 lookback.md;含 history-append.sh | 模板 `:346`;example `:274`;`rg lookback.md`=0 | ✅ |
| S-8.1 | guard 對核准=是 Read exit 0 | 親跑 rc=0;fixture 列 `_templates/1-discussion.md` 核准=是 | ✅ |
| S-8.2 | 方案檔 exit 2;stderr 含 2-decision／4-spec／方案檔 | 親跑 rc=2;`⛔ …方案檔仍禁讀(2-decision／4-spec／2–7;核准格不能覆寫)` | ✅ |
| S-8.3 | 未核 Read exit 2;主張牙紅 | 親跑 rc=2;`⛔ …未核路徑不得當已授權 evidence`;realworld `:439` | ✅ |
| S-8.4 | 解法建議當 Observed 必紅,含解法／不當事實 | ticket fixture;`:443` 綠 | ✅ |
| S-9.1 | spec-gate exit 1,含 Fast／六問／triage | fast-blank 親跑 exit 1;`C8 Fast early risk triage(六問缺表)` | ✅ |
| S-9.2 | fixture 第 3 列=是且去向三擇一 | wait fixture `:15` + `:19`=`fast+mini`;T-10-ok | ✅ |
| S-9.3 | 命中無去向 exit 1 | fast-hit-no-dest 親跑 exit 1;`命中後去向須 ∈ {full, fast+mini, OC}` | ✅ |
| S-9.4 | 全否 + Fast 不得只因此紅 | fast-visual 親跑 9/9 exit 0 | ✅ |
| S-9.5 | 本檔 Fast 項 no-fire | slug spec-gate `C8 …(full 缺表 no-fire)`;9/9 | ✅ |

原始 CLI 全文見附錄 A3。

## 截圖槽

本 feat 無產品前端;現象為 CLI／exit／字樣。截圖槽 N/A（無 `shots/` 定名檔 → 產檔器顯示佔位即可）。不准發明編輯 URL。不准新增一張只為了截圖。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／fixture 字樣／guard Read rc
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.2 | G1 reviewer | 構想不能混成目標 | 跑 check-realworld 對錯欄稿 | 把該句搬到 Requested solution | 檢查同步結束 | ✅ 人看見「構想在錯欄」 |
| S-1.3 | 採用者 | 抄範例時寫結果 | 打開 example 1-discussion | 以改口後 Goals 為抄本 | 無 | ✅ Goals 已改結果;AC 仍教 dashboard（F-1） |
| S-2.1 | 訪談對象／討論 agent | 不被錨定 | N3 走發現｜開放題 | 人回答現況,不從推薦挑 | 一題一答 | ✅ 硬規則已改;兩輪降輔助 |
| S-3.3 | 討論 agent／G1 | 認可≠來源升格 | 主張牙擋點頭獨源 | 補 path 或改 Assumption | 無 | ✅ 點頭獨源紅;S1 已改口 |
| S-4.1 | G2 reviewer | 過期假設進不了 G2 | `check-spec-gate.sh` 對 expired-open | 改 resolved 或 oc-accepted | 拒絕發生在送審關 | ✅ 人看得見 C7 FAIL |
| S-5.1 | 後讀 3-prototype 的人 | 一行看出驗了誰／哪場 | realworld 殘行牙 | 人類親填 role／scenario | 無 attestation 仍被既有牙拒 | ✅ 殘行紅;完整行綠 |
| S-6.1 | 收斂者／G2 | 痛點不能無聲消失 | spec-gate C9 | 按 2-decision 抄表 | 無 | ✅ 缺表紅;本 slug 表在 |
| S-7.1 | owner | 出貨留下回看約定 | Exit 四欄地板 | 到期用 history-append | 回看日未到不得寫已改善 | ✅ 四欄在;無 lookback.md |
| S-8.1 | 討論 agent | 核准後讀得到事實 | guard Read 核准=是 | owner 先核擬路徑 | 核准空白不得往下 | ✅ rc=0 |
| S-8.2 | 討論 agent | 方案檔仍進不去 | Read 2-decision | 改讀 specs／原始碼 | 核准格不能覆寫禁令 | ✅ rc=2 方案檔 |
| S-8.3 | 討論 agent／owner | 未核不得當已授權 | Read 未核路徑 | 送核准卡或維持 Assumption | 顯性等 owner | ✅ rc=2 未核 |
| S-9.1 | Fast 實作者 | 寫 4 前先收完六問 | spec-gate C8 | 對 diff 答六問 | 未收束不得進 R/S | ✅ 空白表紅 |
| S-9.2 | Fast 實作者／owner | 等待誤標不能當純視覺 Fast | 填 wait fixture 表 | owner 裁去向 | 待裁期間不得開寫 | ✅ #3=是;去向 fast+mini |
| S-1.1／S-1.4／S-2.2／S-2.3／S-3.1／S-3.2／S-3.4／S-3.5／S-4.2／S-4.3／S-4.4／S-5.2／S-5.3／S-6.2／S-6.3／S-6.4／S-7.2／S-7.3／S-8.4／S-9.3／S-9.4／S-9.5 | — | — | — | — | — | 不適用（4-spec Operational Context 標不適用或純字面／靜態牙） |

六條人因檢查:技術上能完成工作（終端機拒絕看得到）;失敗把決策權交回人（搬欄／補來源／改 status／補 role／填六問去向）;未把等待標成完成（C7／C8／C9 FAIL 不是 warning）;系統外動作（訪談／owner 核／到期回看）有 Recovery;中斷路徑是修欄後重跑;資訊（stderr 字樣）未過期。未發現「看得到但沒有決策權」。F-1 是教師抄本殘留,不是操作走查失敗。

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 三支牙仍各擁判定;無第四 CLI、無 event bus 讓 example 反向驅動 gate。guard Read 只讀 manifest 字面。
2. **資料所有權被繞過寫入**:未命中 —— spec-gate／realworld 只讀;guard 不改目標檔。
3. **相容性破壞包成新增**:未命中 C1–C6 保留,只加 C7–C9（腳本頂註 `:16-29` 從六項改九項）。exit 契約仍 0／1／2。
4. **一致性邊界被拆解**:未命中 —— 單檔字面檢查,無 transaction。
5. **宣告的 Test seam 未被使用**:未命中 —— fixture 目錄 `scripts/fixtures/discovery-gaps/` 18 份都被對應 S 引用;T-9 真餵 Read,不是只數 selftest 字樣。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— A-2 仍不還原整場對話;guard 仍不是 OS hook。C9「新式」收窄是射程選擇（F-2）,不是把已知限制修掉。

無 🔴。F-1／F-2 併入 Standards／Spec Axis,不另立第三軸。

## Standards Axis

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟡 | `example/contract-expiry-reminder/1-discussion.md:98-117` AC 仍鎖 dashboard／卡片／URL;` :89` Q3「本期只做站內 dashboard」。牙只掃 Goals 節 `scripts/check-realworld.sh:300-304` | S-1.3 THEN 第二句「若仍要提 dashboard／卡片／URL,只出現在 Requested solution」。機械覆蓋只做到 Goals 三句改口;活教師 AC／Q3 仍教通道 | 人類 G3 裁:①當 L1（M-2 只要求 Goals 改寫）park;或 ②回 Stage 6 把 AC 觀測改成「結果在哪被看見」 | S-1.3／T-2 |
| F-2 | 🟡 | `scripts/check-spec-gate.sh:351-352` `fire_disp = full and (Assumption refs 或 path 含 discovery-gaps)`。對照:`docs/dev/diagram-ir-gate/4-spec.md` full、無 Assumption refs、無 Disposition → 親跑 C9 `no-fire` 仍 9/9 | S-6.1 THEN 寫「full lane 缺表 → exit 1」。實作加「新式」才發動,舊 full 不誤殺 | 人類 G3 裁:接受為 L1（不炸舊 spec）並在 4-spec／6-notes 對帳;或回 G2 把 S-6.1 改成「新式 full」 | S-6.1／T-7 |
| F-3 | 🟢 | `#286` `0d21547` 修 PF-2 INTERP;`scripts/test-architecture-guards.sh:2529` `MIN_HEREDOCS = 222` | Stage 6 曾為地板與 INTERP 牙打架。落地樹已恢復牙 | 無需本 hop 動碼。記下以免 G3 以為 PF-2 仍破 | 回歸 |

無 🔴。Dependency Direction／Boundary Leakage／Data Ownership／Interface Stability:無未授權新 CLI、無內部型別漏出、無非 owner 寫入、C1–C6 加項相容。F-2 是公開檢查發動條件收窄,已列 🟡。

## Spec Axis

逐 R;對照實際 diff／親跑。6-notes Deviations 在 N4 才讀,差異裁斷見附錄 A4。

| R | 判定 | 出處 |
|---|---|---|
| R-1 | **符合**(S-1.3 第二句偏離 → F-1 🟡,不翻 R) | 模板分欄 `_templates/1-discussion.md:86-90`;錯欄牙 `:288-292`;不黑名單 `:290`;example Goals 已改口 |
| R-2 | **符合** | N3 `:23-25`／`:44-45`;單邊缺失牙接線 `:732-751`;裁決附選 fixture 綠 |
| R-3 | **符合** | 五值 `CLAIM_STATUSES` `:338`;點頭／枚舉／缺源 fixture 紅;低影響不逼貼綠;S1 `:29-30` 認可≠升格 |
| R-4 | **符合** | C7 過期 open 紅、resolved／oc-accepted 綠;四欄地板在模板／example |
| R-5 | **符合** | 殘行紅、完整行綠;模板 `:128` 有 role／scenario;無 Actor Coverage 全表 |
| R-6 | **符合本 slug／fixture**;舊 full 射程見 F-2 🟡 | C9 對 discovery-gaps 缺表紅;本檔 disposition `:613-629`;`RW-[0-9]`=0 |
| R-7 | **符合** | Exit 四欄在模板 `:348` 與 example `:275`;有節缺欄紅;結果入口 `history-append.sh` |
| R-8 | **符合** | 親跑 Read 三案;方案檔禁令 `:33-40` 不能被核准=是覆寫;ticket 解法不當事實 |
| R-9 | **符合** | 空白／待裁紅;wait fixture #3=是且去向 fast+mini;全否 Fast 綠;本檔 full no-fire |
| Design Constraints | **符合** | 三支既有牙;同檔就地欄;無第二家族;無第二鏈;無 lookback 永久檔;本 hop 不改 STATUS |
| Architecture Boundaries | **符合**(C9 發動條件見 F-2) | spec-gate 擁有 G2;realworld 擁有教師地板;guard 擁有 talk 期擋讀 |
| Interface | **符合加項** | C1–C6 保留;Read 只在 talk 游標在時發動 |

無未經授權、會改 R/S 或資料所有權的 🔴 Boundary 變更。

## 變更架構圖

對上 #286 basename。不要拿 F-id／S-id 當模組名。

```
採用者抄教師
  |
  +--> _templates/1-discussion.md  Goals / Requested / Assumption四欄 / Evidence manifest
  +--> _templates/2-decision.md    Real-world 去向
  +--> _templates/3-prototype.md   Human verdict role= scenario=
  +--> _templates/4-spec.md        Fast early risk triage + Real-world Disposition
  +--> _templates/7-review.md      Exit 回看四欄 -> history-append.sh
  +--> example/contract-expiry-reminder/{1,2,3,4,7}-*
  +--> skills/dev-talk/nodes/{N3-probe,S4-accept,S1-survey}.md
  +--> skills/dev-talk/SKILL.md + guides/guide-dev-talk.html
  +--> skills/dev-flow/SKILL.md + guides/guide-dev-flow.html
                    |
                    v
        +-----------+-----------+
        |                       |
 check-realworld.sh      check-spec-gate.sh
  Goals錯欄/前綴/主張     C7 Assumption refs
  verdict一行/回看四欄    C8 Fast triage
        |               C9 Disposition
        |                       |
        +-----------+-----------+
                    |
           hooks/devtalk-guard.sh
           talk游標在 -> Read 分支
           核准=是放行; 2-7 仍禁; 未核擋
                    |
           同一入口: scripts/devflow-check.sh
           fixture: scripts/fixtures/discovery-gaps/*
           回歸: hooks/selftest.sh + test-architecture-guards.sh
           禁: check-discovery-gaps.sh (不存在)
```

公開「端點」= 三支既有 CLI 的 exit 契約（realworld 0／1;spec-gate 0／1／2;guard Read 0／2）。新表名=`## Requested solution`／`## Evidence manifest`／`## Assumption refs`／`## Real-world Disposition`／`## Fast early risk triage`／Exit 回看四欄。

## Diff(merge-base(develop)..HEAD,逐檔折疊)

產品樹 = `origin/main` `#286`=`fdbd569`（5 commits: Stage 6 land + PF-2／graph／Exit parity）。本 Stage 7 分支切開時與 tip 相同;本 docs commit 只加 `7-review.md`／`7-review.html`。

<details>
<summary>三支牙 + fixture（+check-realworld +266/−1; +check-spec-gate +129/−3; +devtalk-guard +79; discovery-gaps 18 檔）</summary>

`scripts/check-realworld.sh` 加 S-1…S-7／S-8.4 地板,`MIN_CHECKS=174`。`scripts/check-spec-gate.sh` 加 C7／C8／C9。`hooks/devtalk-guard.sh` 加 Read 分支。fixture 目錄 `scripts/fixtures/discovery-gaps/`。無 `check-discovery-gaps.sh`。

</details>

<details>
<summary>活教師（_templates 1／2／3／4／7; example 1／2／3／4／7; skills N3／S1／S4／兩 SKILL; guides 兩份）</summary>

分欄、前綴、四欄、verdict 一行、disposition、Fast 六問、Exit 回看、Evidence manifest。example 1-discussion Goals 改口;AC 仍提 dashboard（F-1）。

</details>

<details>
<summary>回歸地板（test-architecture-guards RW-DG1／2; selftest S-8 Read 五案; check-py-floor MIN_HEREDOCS=222）</summary>

S-2.2 隔離突變接線。S-8 Read 不靠 `grep -c`。PF-2 INTERP 牙在 `0d21547` 修回。

</details>

<details>
<summary>本 slug 過程檔（6-notes + html; 2-decision／5-tasks 微調）</summary>

Stage 6 筆記在 #286。本 hop **步 4 才讀** Self-Review。本 hop 不改這些檔。

</details>

Banned:無新檢查家族。本 hop 不改 `docs/dev/STATUS.md`／`HISTORY.md`、不 bump plugin。

## Verdict

**PRE-REVIEW** —— **不是 G3 PASS**。機械面:本次 35 S 親跑綠 + 三支牙回歸綠 + 現象逐 S 有實跑證據 + 無 🔴。Human G3 未寫。兩個 🟡（F-1 教師 AC 殘通道、F-2 C9 新式射程）要 owner 裁 park 或回修,未處置不得勾 Design Boundary Exit。

建議 reviewer 路徑:①抽驗 S-4.1 fixture 行 29 與 C7 輸出 ②抽驗 T-9 三案 stderr ③看 F-1／F-2 要不要接受 ④人類才改頂欄 `verdict`。

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 35/35 機械綠（F-1 不把 S-1.3 打成 ❌） | Coverage Matrix |
| 既有全綠 | realworld 174/174;slug spec-gate 9/9;無第四家族 | Verification Evidence |
| 現象證據逐 S 相符 | 35 列親跑 | 現象證據表 |
| Evidence 契約 | gauntlet 見附錄 A5（本檔落檔後跑） | 2d |
| 無 🔴 | 無 🔴;2 條 🟡 未 park | Standards／Spec |
| Human G3 | **未寫** | 本欄 |

輪次:1。未走 breaker。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | A-2 誘導無法從最終 md 還原整場對話;硬 gate 只守前綴對稱與「發現題附推薦」形 | 中 | 維持 4-spec Known design limit ①;不新造對話硬 gate |
| 2 | 本 docs commit 會讓 Fresh `Source SHA` 不再等於 HEAD | 低 | 與既有 Stage 7 同形;人類 G3 可重綁或接受 |
| 3 | guard 只在 talk 游標在時擋 Read;人跳過 hook 硬讀方案檔不擋 | 中 | 維持 Known design limit ②;不新造 OS hook |
| 4 | 「不改語意」與「這條算不算高影響」仍是人判 | 低 | 牙只驗表形;G1／G2 抽查 |
| 5 | F-1:example AC／Q3 仍教 dashboard,S-1.3 THEN 第二句未完全落地 | 中 | park 本列或回 T-2 改 AC 觀測句。追蹤:本表 #5 |
| 6 | F-2:C9 只打新式 full,舊 full 缺 Disposition 不紅 | 中 | park 本列（不誤殺舊 spec）或回 G2 改 S-6.1 發動條件。追蹤:本表 #6 |
| 7 | 本 hop 未跑完整 `scripts/test-architecture-guards.sh` 種子複本（只做與 RW-DG1／2 等價的隔離前綴突變 + 接線行號） | 低 | 人類 G3 若要種子級複驗,跑該檔 RW-DG 兩案 |
| 8 | 採用現場 Q6 三條仍是 oc-accepted／仍待驗,沒有逐字稿 | 中 | 回看四欄追;不捏訪談（OC-3） |
| 9 | 審頁產器行為圖硬切 8 框;本 hop 不改產器 | 低 | 維持 4-spec limit ④ |

已解除的用刪除線保留,本輪無。

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**(契約 `applicable`):F-1／F-2 🟡 尚未 ①修正 ②L2 回 G2 ③Owner 明示接受或 park（本檔 Known Limits #5／#6 是審查者建議落點,不是 Human owner 署名）。無記錄的 🟡 = 未處置,不得勾。
- [ ] Quiz（公開檢查 exit 契約 = 不可逆;full lane 必做）:題在附錄 A6。approver 全對才准 merge
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 兩次 `N_A_NO_INCOMING`;FORK=HEAD=INTEGRATION=`fdbd5696aeb491538276caa09370744370189601`;ref=`refs/remotes/origin/main`。本 hop 不改產品碼。
- [ ] PR → develop（本 repo 整合分支是 `main`;Draft PR 見本 hop。禁直上 master。未 merge）
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`（本 repo 無 living spec;`n-a` 仍要人類勾）
- [ ] STATUS.md 已更新為 shipped（**本 hop 不改 STATUS**;合併後由合併者在整合分支做）
- [ ] 7-review frontmatter status: shipped（本 hop 留 `draft` + `PRE-REVIEW`）
- [x] 7-review.html 已產生（`build-stage7-html.py --action` 後以 `build-gate-twin.py` 寫 G3 twin;判定格 PRE-REVIEW）
- [ ] feature branch 已刪 / worktree 已清

回看約定

| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| 2026-10-13 | rick | 下一場採用／dogfood 的 Stage 1:`## Goals` 是否仍把通道當目標;N3 發現題是否仍附推薦;Fast 4-spec 是否有六問 | 任一現場 Goals 仍鎖 dashboard／畫面通道,或發現題路徑又把「附推薦」當硬規則,或 Fast 空白六問仍送進 G2 |

結果到期用 `scripts/history-append.sh` 追加,不另造永久 lookback 檔。到期未回看不得把九缺口寫成已改善。

## 附錄:本輪特有

### A1　本輪爭點

1. 本檔是 PRE-REVIEW,不是 Human G3 PASS。
2. F-1:S-1.3 THEN 第二句 vs 牙只掃 Goals。
3. F-2:S-6.1「凡 full 缺表就紅」vs C9 只打新式。
4. 審查者 `implementer-A-stage7` ≠ Stage 6 `implementer-a`。
5. 無第二檢查家族、無新 R/S、無 STATUS／HISTORY 改動。

### A2　建議人類 G3 路徑

Verdict 門檻表 → 抽 S-4.1 與 T-9 → 裁 F-1／F-2 → 才改頂欄 `verdict`。全勾不算 PASS。

### A3　親跑原始輸出(索引)

Fresh 兩指令:

```
=== G2 spec gate:docs/dev/requirement-discovery-gaps/4-spec.md ===
✅ C1 …(共 35 條 S)
✅ C2 lane=full / Risk=high
✅ C7 Assumption refs 無過期 open
✅ C8 Fast early risk triage(full 缺表 no-fire)
✅ C9 Real-world Disposition 去向／下落形狀
✅ G2 spec gate:9/9 全過
```

```
  構想在錯欄:goals-dashboard-in-wrong-column
✅ real-world interaction checks: 174/174 passed(地板 174)
```

T-9:

```
S-8.1 rc=0
S-8.2 rc=2  ⛔ devtalk-guard:方案檔仍禁讀(2-decision／4-spec／2–7;核准格不能覆寫)
S-8.3 rc=2  ⛔ devtalk-guard:未核路徑不得當已授權 evidence
T-9-read-ok
```

負向 fixture:expired-open／disposition-missing／fast-blank／fast-hit-no-dest 皆 exit 1 且字樣對。正向:resolved／visual／slug 4-spec 皆 9/9。

### A4　作者對照(N4;`review-unlock` 之後才讀)

6-notes owner=`implementer-a`（Stage 6 #286）。T Review Log 十則都寫「fresh-context Agent」PASS。本 hop **不採信**那些 PASS 當四眼,只對自建矩陣與 Deviations／Decisions。本審查者 ≠ 該 session。

| 作者主張 | 自建裁斷 |
|---|---|
| 35 S 各有牙／fixture;無第四家族 | 相符。矩陣每列有 `檔:行`。本 hop 重跑 T-1…T-10 + 三牙 |
| realworld 174/174;slug spec-gate 9/9 | 相符。本 hop 同數 |
| D-impl-1:隔離 seed 無 fixture 目錄時走內嵌稿;不新增 check_skip | 相符。`check-realworld.sh:237-239` 寫明內嵌。不是 L2 |
| D-impl-2:C8 只打新式 fast（`feature:` + ADDED） | 相符。S-9.1 本就只打 `lane: fast`。grandfather 舊 fixture 是 L1 |
| D-impl-3:C9 只打新式 full（Assumption refs 或 discovery-gaps 路徑） | **如實記錄**。本 hop 獨立親跑 `diagram-ir-gate/4-spec.md` C9 no-fire。這就是 F-2 🟡:S-6.1 字面是凡 full 缺表就紅。作者判 L1（不炸舊 spec）。人類決定要不要回 G2 改 S-6.1。**不是 silent D**;也不是新 R/S |
| D-1…D-8 皆標 L1 | 抽 D-1（本 slug 4B 去 `RW-1` 字面）／D-7（PF-2 INTERP／`MUT` tag）與 diff 對得上,不是 L2 |
| Self-Review ⑧:`test-architecture-guards.sh` 全套因 PF-0 未當正式綠 | 相符。本 hop 亦未跑全套種子;S-2.2 用等價隔離突變 + 接線行。Known Limits #7 |
| FORK_INTEGRATION_SHA=`ab78e8b` | Stage 6 分岔錨。本 hop 2c 用已合 tip `fdbd569`（產品已在 main;與 IBV／diagram-ir 同形）。若用 `ab78e8b` 會把 #286 自己算成 incoming |
| 未「修掉」known limit ①② | 相符。對話仍不還原;無 OS hook |
| S-1.3 = example Goals 改口 | 作者**沒**把 AC／Q3 殘 dashboard 列 Deviation。本 hop 獨立標 F-1 🟡。不是 L2 |

無實為 L2 卻寫成 L1 的翻案。F-1／F-2 維持 🟡,留給 Human G3。

### A5　Gauntlet

```
✅ evidence gauntlet: 64 checks passed — docs/dev/requirement-discovery-gaps/7-review.md
run-id: 20260913T070345Z-p3072
tool-version: 1.3.3
declared-source-sha = expected-source-sha = fdbd5696aeb491538276caa09370744370189601
violations: 0
```

4-spec Required 欄用全形 `；` 寫註解,gauntlet `tokenize_layer_field` 切開成兩個 token。Layer 表用同形列對上,避免改 4-spec（本 hop 禁新 R/S）。三支真牙列仍在。

### A6　Quiz（給 approver;不可逆改動）

1. 這輪新能力掛在哪三支既有牙?有沒有第四支 CLI?
2. 為什麼過期 Assumption 的拒絕必須發生在 `check-spec-gate.sh` 而不是「模板有欄」?
3. owner 把 2-decision 寫進 Evidence manifest 且核准=是,Read 會怎樣?為什麼?
4. Fast 只改一個狀態字、把等待顯示成完成,六問第幾題必須是「是」?去向可以是 Fast 嗎?
5. F-2 說 C9 不打舊 full spec。若你不能接受,該走 L1 park 還是回 G2 改 S-6.1?
