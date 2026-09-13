---
feature: requirement-discovery-gaps
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-c-stage7
reviewers: []
updated: 2026-09-13
---

# 7. 驗證 —— **不是 G3 PASS**

> Implementer C 自建審查（fresh context；**≠** Stage 6 implementer-A）。
> `verdict:` 留 `PRE-REVIEW`。Agent **不發明** G3 PASS／REQUEST_CHANGES／HOLD。
> 建議 Human G3 路徑:Verdict 門檻表 → 附錄 A2 Fresh 實輸出 → 附錄 A3 回看四欄 → Coverage 抽 **S-5.3**（矩陣中位列）→ 再決定。
> 本 hop 只寫 `7-review.md` + html twin。不改 `STATUS.md`／`HISTORY.md`。不 merge。

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
> 用途:**G3 出貨關卡**。雙軸審(mattpocock):Standards = 通用品質、Spec = 逐條對
> 4-spec。本次 S 全綠 + **既有測試全綠(回歸)** + 無 🔴 才 PASS。
> **出貨樹=審過的樹**:整合回歸(改 HEAD)必須在 Final Fresh 之前;Verdict 後改碼
> 作廢 G3。過 gate 後產 7-review.html 供報告。
> 本階段固定產出:`7-review.md`(本模板全節)+ `7-review.html`(G3 必產;必含
> 變更架構圖、F-id 分級表、現象證據表、全 branch diff 折疊 + 執行記錄表)。
> **就這兩個檔,不多不少。禁止長出 `7-review-<誰>.md`、`7-self-review.md` 這類並存檔**。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-c-stage7`（獨立 fresh-context Cloud Agent C;**≠** Stage 6 #286 `implementer-a`） |
| Human G3 | **未寫入**。本檔 `verdict: PRE-REVIEW`。建議路徑:適格人類 reviewer（owner rick）→ 本檔門檻表／A2／A3／抽驗 S-5.3 |
| 讀取順序(可查) | ①`4-spec.md`（G2 PASS、35 S）②`5-tasks.md`（T-1…T-10）③`git diff 2bfb906 fdbd569`（#286 產品 48 檔）④fixture／三支牙／教師 ⑤親跑 T-1…T-10 + 三支牙 + 步 2c（兩次座標相同後合 `37a4284`）→ **之後才** ⑥`review-unlock` 讀 6-notes Self-Review |
| 圍欄 | `hooks/devflow-exec.sh review requirement-discovery-gaps` 武裝後再 `review-unlock`。doctor:`COMPATIBLE`（契約 2.0.0,runtime 3.23.4,gauntlet 1.3.3） |
| 本輪性質 | 產品碼已在 tip `#286`（`fdbd569`）。2c 合入 `#287` STATUS 後 Fresh 樹=`99a3e3b`。本 hop 只落審查檔。**不是 G3 PASS** |

## Coverage Matrix

自建（grep 4-spec 35 條 S ↔ 三支牙／`scripts/fixtures/discovery-gaps/`／教師字面／`rg`;**未先讀** 6-notes Self-Review）。末列回歸。中位列（`rows[len//2]`）= **S-5.3**（36 列之 index 18；twin 抽驗格用同一規則）。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/check-realworld.sh` 第 12 節;`_templates/1-discussion.md:86-90` `## Goals`＋`## Requested solution`;`skills/dev-talk/nodes/S4-accept.md:20`「從哪裡看出結果發生」 | ✅ |
| S-1.2 | 同入口;`scripts/fixtures/discovery-gaps/goals-dashboard-in-wrong-column.md` → stdout `構想在錯欄:goals-dashboard-in-wrong-column`;realworld 174/174 | ✅ |
| S-1.3 | `example/contract-expiry-reminder/1-discussion.md:73-79` Goals 無登入／點擊／一眼可見;構想在 Requested solution | ✅ |
| S-1.4 | `goals-outcome-with-requested-dashboard.md`;`detect_goals_wrong_column` 不因 dashboard／API 誤殺 | ✅ |
| S-2.1 | `skills/dev-talk/nodes/N3-probe.md:24-25` `發現｜`＋「禁附推薦」;`裁決｜`可附選;完成條件兩輪標輔助 | ✅ |
| S-2.2 | `test-architecture-guards.sh` RW-DG1／RW-DG2:`預期 fail,實得 fail`（刪一邊前綴） | ✅ |
| S-2.3 | `probe-decision-with-options.md`;裁決附選不當發現題違規 | ✅ |
| S-3.1 | `user-report-only.md`;`_claim_problems` 含「來源」 | ✅ |
| S-3.2 | 內嵌 `_good_obs`／`_good_assume` `not _claim_problems` | ✅ |
| S-3.3 | `nod-as-only-source.md`;`S1-survey.md:29-30` 認可≠來源升格 | ✅ |
| S-3.4 | `enum-unknown.md` →「枚舉」 | ✅ |
| S-3.5 | `_low` 普通 Context 無枚舉不紅 | ✅ |
| S-4.1 | `bash scripts/check-spec-gate.sh scripts/fixtures/discovery-gaps/assumption-expired-open.md` → exit 1;C7 `L29:Assumption 過期仍 open(2020-01-01)` | ✅ |
| S-4.2 | `assumption-resolved.md` → exit 0;9/9 | ✅ |
| S-4.3 | 本 slug `4-spec.md` C7 oc-accepted;9/9 | ✅ |
| S-4.4 | 模板／example「若為假影響什麼」「影響級」「怎麼驗」 | ✅ |
| S-5.1 | `verdict-accepted-only.md`;缺 `role=`／`scenario=` 必紅 | ✅ |
| S-5.2 | 完整 `ACCEPTED &#124; role=… &#124; scenario=…` 放行;`_templates/3-prototype.md` 含 `role=`／`scenario=` | ✅ |
| S-5.3 | `_templates/3-prototype.md`／example 3-prototype 零命中「本包必填全表」／`Actor Coverage`;有 `role=`／`scenario=` | ✅ |
| S-6.1 | `disposition-missing.md` C9 exit 1 | ✅ |
| S-6.2 | 本 slug disposition「發現被錨定 → S-2.1」;C9 下落匹配 `R-`／`S-` | ✅ |
| S-6.3 | Exception 三列 OOS／limit／slug;本檔 4-spec 9/9 | ✅ |
| S-6.4 | `rg -n 'RW-[0-9]'` 指定六檔 = 0（exit 1 = 無命中） | ✅ |
| S-7.1 | `_templates/7-review.md:348` 與 `example/contract-expiry-reminder/7-review.md:275` 四欄字面齊;`T-8-floor` | ✅ |
| S-7.2 | `lookback-missing-threshold.md` 缺「低於何值重開」;realworld 該項綠;舊檔無節 no-fire | ✅ |
| S-7.3 | `rg -n 'lookback\\.md' _templates/7-review.md example/contract-expiry-reminder/7-review.md` = 0;`history-append.sh` 在模板 L345 | ✅ |
| S-8.1 | `devtalk-guard.sh` Read `_templates/1-discussion.md` exit 0（游標在＋核准=是） | ✅ |
| S-8.2 | Read `2-decision.md` exit 2;stderr `方案檔仍禁讀` | ✅ |
| S-8.3 | Read `notes/review-requirement-discovery-gaps.md` exit 2;stderr `未核路徑不得當已授權 evidence` | ✅ |
| S-8.4 | `ticket-solution-as-fact.md` → 解法／不當事實 | ✅ |
| S-9.1 | `fast-blank-triage.md` C8 exit 1;`缺 ## Fast early risk triage` | ✅ |
| S-9.2 | `fast-wait-shown-as-done.md:15` 第 3 問=是＋「等待被顯示成完成」;去向 `fast+mini` ≠ Fast | ✅ |
| S-9.3 | `fast-hit-no-dest.md` C8 exit 1;`命中後去向須 ∈ {full, fast+mini, OC}` | ✅ |
| S-9.4 | `fast-visual-all-no.md` exit 0;9/9 | ✅ |
| S-9.5 | 本 slug `4-spec.md` C8 `full 缺表 no-fire`;9/9 | ✅ |
| 既有測試套件(回歸) | 4-spec entry point + T-1…T-10 Verify + 合 `37a4284` 後重跑 realworld 174/174、spec-gate 9/9 | ✅ |

**Verify 親跑**（5-tasks 原指令;2026-09-13;2c 合 `37a4284` 之後、Fresh 綁 `99a3e3b`）:T-1…T-10 皆 `EXIT:0`。數字見 Verification Evidence／附錄 A2。

## Verification Evidence

- Source SHA: 99a3e3b0fc0c7a7b8a795cebd5996e984d3cc5d1
- Final Fresh Run ID: 2026-09-13T0705Z-impl-C-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md && bash scripts/check-realworld.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0（`scripts/requirements-methodology-render.txt`）; contract 2.0.0; runtime 3.23.4; git 2.43.0; gauntlet 1.3.3

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

4-spec Required 原文用全形 `／` 與括號內 `；`。Gauntlet `tokenize_layer_field` **不切**全形 `／`、**會切** `；`，實切成兩枚假層名（附錄 A4）。下表 Layer 用**意圖層名**（三支牙）寫人讀的列;E7 機械列另見 A4。不要把第二枚垃圾 token 標 pass。

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md` | pass | exit 0;9/9;C1 35 條 S;C7 oc-accepted;C8 full no-fire;C9 去向齊 | |
| check-realworld | `bash scripts/check-realworld.sh` | pass | exit 0;174/174 passed(地板 174);stdout `構想在錯欄:goals-dashboard-in-wrong-column` | |
| devtalk-guard | T-9 Verify 三案 Read（游標在＋`DEVTALK_MANIFEST`） | pass | S-8.1 exit 0;S-8.2 exit 2 stderr 含方案檔;S-8.3 exit 2 stderr 含未核 | |
| Supply chain | `rg -n 'RW-[0-9]'` 六檔 + `test ! -e scripts/check-discovery-gaps.sh` + `devflow-check.sh methodology` | pass | `rg` 0 行;無第四家族;methodology 在圍欄武裝下 `test-devstage2-graph` ENV 紅（F-4）,牙／example 段已綠 | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |

### 2c 整合結論

授權合併的那一次（Fresh **之前**跑兩次,STATUS／座標完全相同,然後合印出的 INTEGRATION_SHA,不是 branch 名）:

- STATUS: SYNC_REQUIRED_NO_OVERLAP
- FORK / HEAD / INTEGRATION / REF: fdbd5696aeb491538276caa09370744370189601 / fdbd5696aeb491538276caa09370744370189601 / 37a4284848fdcfd4d7ad2385ed6df2c74fd613fd / refs/remotes/origin/main
- 恢復: n-a（SYNC_REQUIRED_NO_OVERLAP;已合 INTEGRATION_SHA + 重跑 realworld 174/174、spec-gate 9/9、T-8／T-9／T-10）

第二次跑（動手合併前）與第一次完全相同。合的是 `37a4284848fdcfd4d7ad2385ed6df2c74fd613fd`（#287 STATUS／HISTORY only;共同戰場無）。合完 HEAD=`99a3e3b0fc0c7a7b8a795cebd5996e984d3cc5d1`。之後才 Fresh。

合併後若再跑同一支腳本（fork 仍是 `fdbd569`）,會印 `ALREADY_SYNCED`(exit 2)。那次輸出**不當交集證據**。本 hop 走路徑 ①:重綁 Final Fresh 到合完 HEAD `99a3e3b`。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得把構想寫進 Goals 還當已完成分欄(S-1.2) | realworld 錯欄 fixture | pass |
| 不得用 dashboard／API 黑名單誤殺結果句(S-1.4) | goals-outcome-with-requested-dashboard | pass |
| 不得讓發現題附推薦仍當硬規則(S-2.1) | N3-probe 禁附推薦 + RW-DG | pass |
| 不得把點頭當唯一來源(S-3.3) | nod-as-only-source | pass |
| 不得讓過期 open Assumption 通過 spec-gate(S-4.1) | C7 expired-open exit 1 | pass |
| 不得只寫 ACCEPTED + 日期當完整 verdict(S-5.1) | verdict-accepted-only | pass |
| 不得讓痛點列去向空白或發第二鏈編號(S-6.1、S-6.4) | C9 + `rg RW-[0-9]`=0 | pass |
| 不得另造 lookback 永久檔(S-7.3) | 模板無 `lookback.md`;有 `history-append.sh` | pass |
| 不得讀 2–7 或未核路徑當已授權(S-8.2、S-8.3) | guard Read exit 2 ×2 | pass |
| 不得把 Fast 空白六問當已分診(S-9.1) | C8 blank-triage exit 1 | pass |
| 不得新造檢查家族 | `test ! -e scripts/check-discovery-gaps.sh` | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 hop 不是 dev-run 引擎案。Stage 6 6-notes:`Run: n-a（sequential v1 start）`。欄位留空。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 改後三檔原文;兩節名在、Goals／S4 不再要求通道 | `_templates/1-discussion.md:86-90`;`S4-accept.md:20`;`T-2-ok` | ✅ |
| S-1.2 | 指定檢查 exit ≠ 0 且含錯欄字樣 | stdout:`構想在錯欄:goals-dashboard-in-wrong-column`;realworld exit 0（對照組紅、整支綠） | ✅ |
| S-1.3 | 改後 example Goals／Requested／Interview | Goals L73-76 結果句;L78-79 Requested 未定案 dashboard | ✅ |
| S-1.4 | exit 0 且不因 dashboard／API 含錯欄 | 174/174;`detect_goals_wrong_column` 對 outcome+Requested 不命中 | ✅ |
| S-2.1 | 改後 N3／指南對稱句 | N3 L24-25／L44-45;`T-3-skill` | ✅ |
| S-2.2 | 隔離複本刪一邊前綴 → exit ≠ 0 | `RW-DG1`／`RW-DG2` 預期 fail,實得 fail | ✅ |
| S-2.3 | 裁決附選仍綠 | `probe-decision-with-options.md` 兩邊前綴在 | ✅ |
| S-3.1 | exit ≠ 0 含來源／Assumption／期限 | `user-report-only` check 名含來源 | ✅ |
| S-3.2 | 兩份對照 exit 0 | `_good_obs`／`_good_assume` | ✅ |
| S-3.3 | 點頭獨源 exit ≠ 0 | `nod-as-only-source`;S1-survey L29-30 | ✅ |
| S-3.4 | 集合外必紅 | `enum-unknown` → 枚舉 | ✅ |
| S-3.5 | 普通 Context 無枚舉仍綠 | `_low` | ✅ |
| S-4.1 | spec-gate exit 1 含 Assumption／過期／open | `❌ C7` `L29:Assumption 過期仍 open(2020-01-01)`;exit 1 | ✅ |
| S-4.2 | resolved 不因該列 exit 1 | `assumption-resolved.md` 9/9 exit 0 | ✅ |
| S-4.3 | oc-accepted 放行 | 本 slug 4-spec 9/9 | ✅ |
| S-4.4 | 模板／範例四欄字面 | `T-5-floor` | ✅ |
| S-5.1 | 殘行 exit ≠ 0 含 role 或 scenario | `verdict-accepted-only` | ✅ |
| S-5.2 | 完整一行放行 | `T-6-template`／`T-6-wired` | ✅ |
| S-5.3 | 無全表必填、有一行角色場景 | 模板／example 零 `Actor Coverage` 必填;有 `role=`／`scenario=`（抽驗列） | ✅ |
| S-6.1 | spec-gate exit 1 含 Disposition／去向 | `❌ C9 Real-world Disposition(full 缺表)`;exit 1 | ✅ |
| S-6.2 | 下落含 R-／S- | 本檔 disposition S-2.1;C9 綠 | ✅ |
| S-6.3 | 非處理有 OOS／limit／slug | 本檔 Exception 三列 | ✅ |
| S-6.4 | `rg RW-[0-9]` 空 | exit 1;0 行 | ✅ |
| S-7.1 | realworld 對四欄字面 | 教師 L348／L275 四欄齊;`T-8-floor`（A3） | ✅ |
| S-7.2 | 有節缺欄必紅、舊檔不發動 | fixture 缺「低於何值重開」;174/174 含該 check | ✅ |
| S-7.3 | 無 lookback.md、有 history-append | `rg lookback.md` 0;`_templates/7-review.md:345` | ✅ |
| S-8.1 | guard Read exit 0 | `PATH _templates/1-discussion.md exit=0` | ✅ |
| S-8.2 | exit 2 含 2-decision／方案檔 | stderr:`⛔ devtalk-guard:方案檔仍禁讀(2-decision／4-spec／2–7;核准格不能覆寫)` | ✅ |
| S-8.3 | Read exit 2;主張牙未核 | stderr:`⛔ devtalk-guard:未核路徑不得當已授權 evidence` | ✅ |
| S-8.4 | 解法建議當 Observed 必紅 | `ticket-solution-as-fact` | ✅ |
| S-9.1 | spec-gate exit 1 含 Fast／六問／triage | `❌ C8` `缺 ## Fast early risk triage`;exit 1 | ✅ |
| S-9.2 | fixture 第 3 列是＋去向三擇一 | `fast-wait-shown-as-done.md:15-19` Q3=是;去向 `fast+mini` | ✅ |
| S-9.3 | 命中無去向 exit 1 | `命中後去向須 ∈ {full, fast+mini, OC}`;exit 1 | ✅ |
| S-9.4 | 全否＋Fast 不因此 exit 1 | `fast-visual-all-no.md` 9/9 | ✅ |
| S-9.5 | 本檔 Fast 項 no-fire | `✅ C8 Fast early risk triage(full 缺表 no-fire)` | ✅ |

## 截圖槽

本 feat 無產品前端;現象為 CLI／fixture／`rg`。截圖槽 N/A（無 `shots/` 定名檔 → 產檔器顯示佔位即可）。不准發明編輯 URL。不准新增一張只為了截圖。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／錯欄字樣／回看四欄／guard Read
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.2 | G1 reviewer | 構想不能混成目標 | 跑 `check-realworld.sh` | 終端機看錯欄字樣 | 檢查同步結束 | ✅ 人看見「構想在錯欄」就退回 Stage 1 |
| S-1.3 | 採用者 | 抄範例時寫結果 | 打開 example 1-discussion | 人打開檔 | 若 Goals 仍鎖通道同一 T 改 | ✅ Goals 已改口 |
| S-2.1 | 訪談對象／討論 agent | 不被推薦錨定 | 依 N3 `發現｜` 開放問 | 人答現況 | 一題一答;不等推薦清單 | ✅ 發現禁推薦已在 skill |
| S-3.3 | 討論 agent／G1 | 點頭不是來源 | 主張牙擋點頭獨源 | 打開聲稱的來源 | 無 | ✅ 殘列必須補 path 或改 Assumption |
| S-4.1 | G2 reviewer | 過期假設進不了 G2 | 跑 `check-spec-gate.sh` | 終端機看 C7 | 拒絕發生在送審那一關 | ✅ exit 1 + 過期 open 字樣 |
| S-5.1 | 後讀 3-prototype 的人 | 一行看出驗了誰／哪場 | 遮住前後文只看 Human verdict | 人類親填 | 無 attestation 仍被既有牙拒 | ✅ 殘行紅;完整行綠 |
| S-5.3 | 後讀模板的人 | 不被要求 Actor Coverage 全表 | 搜模板 | 人打開檔 | LIGHT 上限 | ✅ 無全表必填（抽驗列） |
| S-6.1 | 收斂者／G2 | 痛點不能無聲消失 | 跑 spec-gate | 對原文片段 | 無 | ✅ 缺表 C9 紅 |
| S-7.1 | owner | 出貨留下誰／何時／用什麼／門檻 | 看 Exit 四欄 | 到期用 HISTORY 追加 | 回看日未到不得寫已改善 | ✅ 教師四欄齊（A3） |
| S-8.1 | 討論 agent | 核准後讀得到事實 | Read 核准=是的路徑 | owner 已核 | 核准格空白不得往下 | ✅ exit 0 |
| S-8.2 | 討論 agent | 方案檔仍進不去 | Read 2-decision | 改讀 specs／原始碼 | 無 | ✅ exit 2;核准格不能覆寫 |
| S-8.3 | 討論 agent／owner | 未核不得當已授權 | Read 未核路徑 | 送核准卡 | 顯性等 owner | ✅ exit 2 |
| S-9.1 | Fast 實作者 | 寫 4-spec 前先收完六問 | 跑 spec-gate | 對 diff 答六問 | 未收束不得進 R/S | ✅ 空白表 C8 紅 |
| S-9.2 | Fast 實作者／owner | 等待誤標不能當純視覺 Fast | 填六問第 3=是 | owner 裁去向 | 待裁不得開寫 | ✅ fixture 去向 `fast+mini` |
| S-1.1／S-1.4／S-2.2／S-2.3／S-3.1／S-3.2／S-3.4／S-3.5／S-4.2／S-4.3／S-4.4／S-5.2／S-6.2／S-6.3／S-6.4／S-7.2／S-7.3／S-8.4／S-9.3／S-9.4／S-9.5 | — | — | — | — | — | 不適用（4-spec Operational Context 標不適用或純字面） |

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 三支既有牙各擁自己的判定;沒有第四 CLI、沒有 event bus 讓 realworld 去擋 G2 過期假設。
2. **資料所有權被繞過寫入**:未命中 —— spec-gate／realworld／guard 只讀;guard 不寫目標檔。
3. **相容性破壞包成新增**:未命中 —— C1–C6 保留只加 C7–C9;MIN_CHECKS=174 實數;寫入洩漏掃描仍在;Read 只在 talk 游標在時發動。
4. **一致性邊界被拆解**:未命中 —— manifest 核准格與 guard 允許集合同一字面;example 與模板同 T 改口。
5. **宣告的 Test seam 未被使用**:未命中 —— fixture 目錄 `scripts/fixtures/discovery-gaps/` 就是契約 Test seam;入口仍是三支既有牙。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— ①A-2 仍不還原對話;②guard 仍不是 OS hook;③「不改語意」仍是人判;④審頁 8 框未改產器。

無未經授權 Boundary 變更。無 🔴。無要 park 的 🟡 Boundary（F-1 是 Profile 字串切層,不是 Boundary 越權）。

## Standards Axis

產品樹 = `git diff 2bfb906 fdbd569`（#286）。本 PR vs `origin/main`（`37a4284`）= 本審查檔（+ 2c 已合進的 #287,產品碼零）。

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟡 | `4-spec.md:759` Required layers 用全形 `／` + 括號內 `；` | Gauntlet `tokenize_layer_field` 不切 `／`、切 `；` → 兩枚假層名;第二枚把「不列入本欄」的 `check-stage4-rs-contract.sh` 切進來。E7 全等對不上意圖三層 | Human G3 裁:接受「意圖三層＋本檔 Fresh 實跑」為 Evidence,或 L1 改 4-spec 分隔符（頓號／逗號、括號內勿用 `；`）後重綁 Fresh。**不在本 hop 改 4-spec** | S-2d／E7 |
| F-2 | 🟢 | `scripts/check-py-floor.sh` MIN_HEREDOCS=222;`guides/guide-dev-flow.html`;example `7-review.html` | #286 Files 超出 5-tasks 聯集三檔。作者 D-2／D-5／D-7 記 L1 | 接受。獨立對過:py-floor 是 INTERP 獨佔＋PF-2 牙;guide／example html 是 Exit 四欄 parity | T-8／T-9 |
| F-3 | 🟢 | `scripts/check-py-floor.sh` PF-0 | 本機無 Python 3.9–3.11 → PF-0 exit 2。RW-DG1／2 與 PF-1／PF-2 仍綠 | ENV。#286 CI REPO_REFERENCE 綠。不把本機 PF-0 當產品紅 | 回歸 |
| F-4 | 🟢 | `devflow-check.sh methodology` | 圍欄③武裝時 `test-devstage2-graph` 三案被本 slug review scope 擋（跨 feature 寫） | ENV。解鎖後仍限寫 7-review*。不把圍欄誤殺當產品紅 | Supply chain |
| F-5 | 🟢 | 本檔 Source SHA | 含 Source SHA 的 commit 落地後 HEAD 會漂 | 同 4-spec Known limit 精神。Fresh 綁 `99a3e3b`（2c 後、本檔 commit 前）。合法恢復=再重綁,不是再合產品碼 | S-2d |

Dependency Direction／Boundary Leakage／Data Ownership／Interface Stability:未發現反向依賴、未漏出內部型別、非 owner 未直寫 STATUS 演算法、公開檢查入口字面仍是三支既有牙。無 🔴。無未授權 🟡 Boundary。

## Spec Axis

| R | 判定 | 出處 |
|---|---|---|
| R-1 分辨結果與構想 | 符合 | S-1.1 分欄;S-1.2 錯欄紅;S-1.3 example 改口;S-1.4 不黑名單 |
| R-2 發現題不先塞推薦 | 符合 | S-2.1 N3;S-2.2 RW-DG;S-2.3 裁決可附 |
| R-3 主張回來源或期限 | 符合 | S-3.1–S-3.5;S-8.4 同牙 |
| R-4 過期假設擋 G2 | 符合 | S-4.1 C7 紅;S-4.2／S-4.3 綠;S-4.4 四欄地板 |
| R-5 verdict 一行角色場景 | 符合 | S-5.1 殘行紅;S-5.2 完整行綠;S-5.3 無全表（中位抽驗） |
| R-6 痛點列有去向 | 符合 | S-6.1 缺表紅;S-6.2／S-6.3 下落;S-6.4 無 RW-id。作者 D-1 L1 改本 slug 4B 字面,契約不變 |
| R-7 出貨回看四欄 | 符合 | S-7.1 教師四欄;`T-8-floor`;S-7.2 fixture;S-7.3 無 lookback.md。作者 D-5 L1 不用 `###`(parity) |
| R-8 核准可讀、方案檔仍禁 | 符合 | S-8.1–S-8.3 三案 exit;S-8.4 ticket。作者 D-7 L1 改 READ／MUT tag |
| R-9 Fast 六問 | 符合 | S-9.1／S-9.3 紅;S-9.2／S-9.4／S-9.5 綠。D-impl-2 grandfather 既有 fast fixture |
| M-1～M-11 | 符合 | 教師／牙改口對得上 MODIFIED |
| Design Boundary | 符合 | 見 Design Integrity;無 L2 |
| 6-notes Deviations | 如實 | D-1…D-8 皆 L1;獨立對過 Files 超聯集三檔=作者 D-2／D-5／D-7。無作者矩陣可裁成「多報綠」。D-impl-1…3 不是 L2 |

## 變更架構圖

產品(#286,已在 tip `fdbd569`)與本 PR 審查密封:

```
[check-realworld.sh]  MIN_CHECKS=174
    |  Goals 錯欄 / 前綴對稱 / 主張牙 / verdict 一行 / 回看四欄
    +--> scripts/fixtures/discovery-gaps/
         goals-dashboard-in-wrong-column.md
         goals-outcome-with-requested-dashboard.md
         probe-decision-with-options.md
         nod-as-only-source.md
         enum-unknown.md
         ticket-solution-as-fact.md
         user-report-only.md
         unapproved-as-only-source.md
         verdict-accepted-only.md
         lookback-missing-threshold.md
         guard-read-1-discussion.md

[check-spec-gate.sh]  C7 Assumption / C8 Fast / C9 Disposition
    +--> assumption-expired-open.md
         assumption-resolved.md
         disposition-missing.md
         fast-blank-triage.md
         fast-hit-no-dest.md
         fast-visual-all-no.md
         fast-wait-shown-as-done.md

[devtalk-guard.sh]  Read 分支 <<'READ'
    +--> .devtalk-cursor.json (ephemeral)
    +--> DEVTALK_MANIFEST 或 docs/dev/*/1-discussion.md

[_templates/1-discussion.md]  Goals / Requested / Assumption 四欄 / Evidence manifest
[_templates/2-decision.md]    去向
[_templates/3-prototype.md]   role= / scenario=
[_templates/4-spec.md]        Fast triage + Disposition (ADDED 前)
[_templates/7-review.md]      回看四欄 + history-append.sh
[example/contract-expiry-reminder/1|2|3|4|7-*.md]
[skills/dev-talk/nodes/N3-probe.md S1-survey.md S4-accept.md]
[skills/dev-flow/SKILL.md]    進 4 前六問
[guides/guide-dev-talk.html]
[guides/guide-dev-flow.html]  L1 parity 回看表
[scripts/test-architecture-guards.sh]  RW-DG1/2 + MIN_HEREDOCS pin
[scripts/check-py-floor.sh]   MIN_HEREDOCS=222

本 companion hop(docs-only):
[7-review.md]                 Source SHA=99a3e3b (2c 後 HEAD)
[7-review.html]               G3 twin;抽驗=S-5.3
```

無新公開 HTTP 端點、無新表。改 Diff 必須改本圖。

## Diff(merge-base(main)..HEAD,逐檔折疊)

`merge-base(origin/main, HEAD)` 在寫本檔時:產品 #286 已在 main。2c 合 `37a4284`（#287 STATUS）後 tip=`99a3e3b`。本 PR 相對 `origin/main` 只加本檔／twin。

<details>
<summary>產品 #286(已在 tip;審查對象,不是本 PR 新增)</summary>

48 files,+2429/−141。basename 見變更架構圖。入口仍是 `check-realworld.sh`／`check-spec-gate.sh`／`devtalk-guard.sh`。完整 hunk:`git show fdbd569` 或 `git diff 2bfb906 fdbd569`。

</details>

<details>
<summary>2c 合入 #287(STATUS／HISTORY only;Fresh 之前)</summary>

`docs/dev/STATUS.md`／`HISTORY.md`／`HISTORY.html`。Active → 6-implementation-notes;G3 仍⬜。本 hop **沒有**另寫 STATUS／HISTORY。

</details>

<details>
<summary>docs/dev/requirement-discovery-gaps/7-review.md + 7-review.html — 本審查正本</summary>

本檔。`verdict: PRE-REVIEW`。Source SHA=`99a3e3b0fc0c7a7b8a795cebd5996e984d3cc5d1`。

</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** Agent 不代填 Human 判定。

機械面（Implementer C 抽驗表,不新造 R/S）:

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 35/35 自建矩陣 ✅ | Coverage Matrix |
| 既有全綠 | entry point + T-1…T-10;合後重跑 | realworld 174/174;spec-gate 9/9 |
| 現象證據逐 S 相符 | 35/35 | 現象證據表 |
| Evidence 契約 | Fresh 綁 2c 後 HEAD;`--review-file` 見附錄 A2／A4 | Source SHA=`99a3e3b…`;E7 層名切分=F-1 |
| 無 🔴 | 無 🔴;F-1 🟡 | Standards／Spec |
| 2c 在 Fresh 之前 | 是 | 兩次相同後合 `37a4284`,再 Fresh |
| Human G3 | **未寫入** | 建議 owner rick 抽 S-5.3 + A3 四欄 |

建議 Human:機械數字夠支持 PASS;**先裁 F-1**（E7 層名）再寫 `verdict:`。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | A-2 誘導無法從最終 md 還原(4-spec Known limit ①) | 低 | park;硬 gate 只守對稱句。owner=方法論;追蹤=4-spec Design Constraints |
| 2 | guard 不是 OS hook(Known limit ②) | 低 | park。人跳過 hook 硬讀方案檔,本 feat 不新造 |
| 3 | 「不改語意」與「何謂高影響」仍是人判(Known limit ③) | 低 | park;牙只驗形狀 |
| 4 | 審頁產器行為圖硬切 8 框(Known limit ④) | 低 | park;本 hop 不改產器 |
| 5 | 含 Source SHA 的本檔 commit 落地後 HEAD 會漂 | 中 | park。Fresh 綁 `99a3e3b`。合法恢復=再重綁,不是再合產品碼 |
| 6 | 本機 PF-0 無 3.9–3.11;methodology 在 review 圍欄下誤殺 stage2 graph | 低 | ENV;CI／解圍欄後另跑。不當產品紅 |
| 7 | 4-spec Required layers 全形 `／`＋`；` 讓 Gauntlet 切出假層名 | 中 | **F-1**。Human 裁接受或 L1 改分隔符。本 hop 不改 4-spec |
| 8 | 本檔 `verdict: PRE-REVIEW`;全勾也不算 shipped | — | 留給 Human G3。STATUS Active 不在本 PR 改 |

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**(applicable):無未授權 Boundary。F-1 是 Profile 字串切層,不是 Boundary 越權。F-2…F-5 🟢。**F-1 🟡 待 Human 裁** —— 未裁不得勾
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配):公開檢查 exit 契約已改 → 建議 Human 做 3–5 題。本 hop 不代考
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 結論（兩次相同;FORK=`fdbd569` HEAD=`fdbd569` INTEGRATION=`37a4284` REF=`refs/remotes/origin/main`）在「2c 整合結論」。Source SHA 綁合完 HEAD `99a3e3b`。Verdict 之後不得再改程式碼
- [ ] PR → develop（本專案整合分支是 `main`;本 hop 開 draft PR,禁直上 master,**不 merge**）
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`（本 repo 無 living spec;`n-a`）
- [ ] STATUS.md 已更新為 shipped（整合分支上、PR 合併後由合併者做;**本 hop 不改 STATUS／HISTORY**）
- [ ] 7-review frontmatter status: shipped（現為 `draft` + `PRE-REVIEW`）
- [ ] 7-review.html 已產生（本 hop 產 twin;Human 核過才算 Exit 勾）
- [ ] feature branch 已刪 / worktree 已清

回看約定
<!-- 出貨時留下誰／何時／用什麼資料回看、低於何值重開。結果到期用
     `scripts/history-append.sh` 追加,不另造永久 lookback 檔。Exit 節內不用
     ### 標題。 -->
| 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
|---|---|---|---|
| 2026-12-13 | rick | 下一場 full 討論的 1-discussion Goals／N3 問句 + 下一場 Fast 4-spec 六問表;到期用 `scripts/history-append.sh` 追加 | Goals 仍把通道當目標,或發現題仍附推薦,或 Fast 空白六問仍能送審 |

## 附錄:本輪特有

### A1　2c 原始結論行(合併前,跑兩次相同)

```
STATUS: SYNC_REQUIRED_NO_OVERLAP
FORK_INTEGRATION_SHA: fdbd5696aeb491538276caa09370744370189601
FEATURE_HEAD: fdbd5696aeb491538276caa09370744370189601
INTEGRATION_SHA: 37a4284848fdcfd4d7ad2385ed6df2c74fd613fd
INTEGRATION_REF: refs/remotes/origin/main
共同戰場:無
結論:STATUS=SYNC_REQUIRED_NO_OVERLAP FORK=fdbd569… HEAD=fdbd569… INTEGRATION=37a4284…(refs/remotes/origin/main)—— 仍要合併 INTEGRATION_SHA + 跑全套測試
```

合的是 `37a4284848fdcfd4d7ad2385ed6df2c74fd613fd`,得到 merge `99a3e3b0fc0c7a7b8a795cebd5996e984d3cc5d1`。之後才 Fresh。#287 只動 STATUS／HISTORY,產品牙數字不變。

### A2　Final Fresh 實跑輸出(Variant C)

Entry point 與合後重跑（工作樹乾淨、HEAD=`99a3e3b`）:

```
$ bash scripts/check-spec-gate.sh docs/dev/requirement-discovery-gaps/4-spec.md
=== G2 spec gate:docs/dev/requirement-discovery-gaps/4-spec.md ===
✅ C1 每個 S 都有觀測欄(共 35 條 S)
✅ C2 Verification Profile 可解析(lane=full / Risk=high)
✅ C3 lane/Risk 組合合法(OC-4:fast + high 需 Owner Call 例外)
✅ C4 模糊詞掃描(全文三詞 + 逐 S 三律清單)
✅ C5 Drafting Decisions 無殘留「待裁決」(L789 起)
✅ C6 晚改可見行為不得停成「4-spec 壓 Decision」(DD／確認紀錄)
✅ C7 Assumption refs 無過期 open(過期須 resolved 或 oc-accepted)
✅ C8 Fast early risk triage(full 缺表 no-fire)
✅ C9 Real-world Disposition 去向／下落形狀

✅ G2 spec gate:9/9 全過(形狀檢查;R/S 與 DD 的內容仍須人審)。

$ bash scripts/check-realworld.sh
  構想在錯欄:goals-dashboard-in-wrong-column
✅ real-world interaction checks: 174/174 passed(地板 174)
```

負向牙抽樣（合後仍紅）:

```
assumption-expired-open.md → exit 1; ❌ C7 L29:Assumption 過期仍 open(2020-01-01)
disposition-missing.md     → exit 1; ❌ C9 Real-world Disposition(full 缺表)
fast-blank-triage.md       → exit 1; ❌ C8 缺 ## Fast early risk triage
fast-hit-no-dest.md        → exit 1; ❌ C8 命中後去向須 ∈ {full, fast+mini, OC}
assumption-resolved.md     → exit 0; 9/9
fast-visual-all-no.md      → exit 0; 9/9
```

guard Read 三案:

```
PATH _templates/1-discussion.md
  exit=0
PATH docs/dev/requirement-discovery-gaps/2-decision.md
  exit=2
  stderr='⛔ devtalk-guard:方案檔仍禁讀(2-decision／4-spec／2–7;核准格不能覆寫)'
PATH notes/review-requirement-discovery-gaps.md
  exit=2
  stderr='⛔ devtalk-guard:未核路徑不得當已授權 evidence'
```

T-1…T-10 親跑皆 `EXIT:0`（`/tmp/rdg-s7-verify/T-*.out`）。Gauntlet `--review-file` 原始輸出見 A4。

### A3　Exit 回看四欄(Variant C;Stage 6 教師)

教師正本（#286 T-8）四欄字面與寫入口:

```
FILE _templates/7-review.md
  回看日期 FOUND
  回看 owner FOUND
  資料來源 FOUND
  低於何值重開 FOUND
  lookback.md mentions: 0
  history-append.sh: FOUND
  L348: | 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |

FILE example/contract-expiry-reminder/7-review.md
  同上四欄 FOUND
  lookback.md mentions: 0
  history-append.sh: FOUND
  L275: | 回看日期 | 回看 owner | 資料來源 | 低於何值重開 |
  L277: | 2026-10-23 | owner | 下季漏約件數(週會) | 漏約件數不降於上季 |
```

`rg -n 'lookback\.md'` 對上列兩檔 → 0 行。`guides/guide-dev-flow.html` L1 parity 同步四欄表頭（作者 D-2／D-5）。

S-7.2 負向:`scripts/fixtures/discovery-gaps/lookback-missing-threshold.md` 有回看節但表頭缺「低於何值重開」;realworld 該 check 在 174/174 內。

本檔 Exit 回看表四欄齊,結果入口寫 `history-append.sh`,不另造 `lookback.md`。

### A4　Gauntlet 層名實切 + `--review-file`(寫檔後補)

4-spec L759 原文:

`Required layers:check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支；…不列入本欄）`

`tokenize_layer_field` 實切:

```
REQUIRED:
  'check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支'
  'check-stage4-rs-contract.sh` 是本 hop 審頁形狀，不落地缺口牙，不列入本欄）'
```

意圖三層（`check-spec-gate`／`check-realworld`／`devtalk-guard`）**不是**這兩個 token。本檔 Evidence 表用人讀的三層寫 pass,不把第二枚垃圾 token 標 pass。指令（HEAD=`99a3e3b0fc0c7a7b8a795cebd5996e984d3cc5d1`）:

```
test -x docs/dev/tools/devflow-evidence-gauntlet.sh
bash docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/requirement-discovery-gaps/7-review.md \
  --source-sha 99a3e3b0fc0c7a7b8a795cebd5996e984d3cc5d1 --review-file \
  --require-layer check-spec-gate \
  --require-layer check-realworld \
  --require-layer devtalk-guard
```

實跑（2026-09-13;本檔已落、尚未 commit）:

```
❌ evidence gauntlet: 2 violation(s) in 56 checks — docs/dev/requirement-discovery-gaps/7-review.md
  - E7: required layer「check-spec-gate／check-realworld／devtalk-guard（九缺口牙只這三支」缺席或未 pass(unverified/n-a 不滿足 required)
  - E7: required layer「check-stage4-rs-contract.sh` 是本 hop 審頁形狀，不落地缺口牙，不列入本欄）」缺席或未 pass(unverified/n-a 不滿足 required)
```

56 項裡其餘（含 E2 SHA 綁定）過。兩條紅就是 F-1:Profile 切出來的假層名在 Evidence 表沒有、也不該有 pass 列。不把垃圾 token 標 pass 來假綠 E7。

### A5　作者對照(N4)

讀取順序:矩陣與牙跑完才 `review-unlock`。作者 Self-Review ①–⑧:35 S 有 RED→GREEN;T-1…T-10 PASS;T-4／T-9 有 FAIL→較晚 PASS;十 T 同一落地 commit;L1 D-1…D-8;回歸 174/174 與本 hop 獨立數字相符。

差異裁定:
- 作者說 extra=3（2-decision＋renderer）。獨立 `--name-only` 還看到 `check-py-floor.sh`／`guide-dev-flow.html`／example `7-review.html`。作者 Deviations 已覆蓋（D-2／D-5／D-7）。**不另開 🔴**。
- 作者未寫 Required 層 `；` 切分。本 hop 獨立發現 → **F-1 🟡**。
- 作者 PF-0 ENV 與本機相同。接受。
- 無 L2。無 Self-Review 多報綠。

### A6　抽驗列 S-5.3(twin 中位)

決定論:`Coverage Matrix` 36 列（35 S + 回歸）,`rows[18]` = S-5.3。

去看:
- `_templates/3-prototype.md` Human verdict 指令含 `role=`／`scenario=`,無「本包必填全表」／`Actor Coverage`
- `example/contract-expiry-reminder/3-prototype.md` 同行格式
- `scripts/check-realworld.sh` 第 16 節殘行牙

對得上才信其餘 34 列。
