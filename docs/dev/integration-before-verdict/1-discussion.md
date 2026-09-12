---
feature: integration-before-verdict
stage: 1-discussion
status: draft
owner: tony
reviewers: []
updated: 2026-09-12
baseline: tip 52fe54b / plugin 3.23.3
contract: 2.0.0
---

# 1. 討論 — 整合回歸放在 Fresh／雙軸／Verdict 之前

> 用途:發散。**不做決定、不簽 G1。** 本場依 owner 書面 brief 落檔,不是現場一問一答。
> 未核敘述標 `[Assumption]`。本 hop 只產本檔與 `1-discussion.html`。
> 本 slug 是 owner 指定的第一個真實 **full lane** 題目;實作與 G1 留給後續 hop。

## Problem
誰:要簽 G3／出貨的 reviewer 與 owner,以及照 `_templates/7-review.md` 走 Exit 的實作者。
痛:舊節序是 Final Fresh → Verdict → Exit 才整合同步。人核准的那棵樹,不是最後出貨的那棵樹 —— Exit 合併 `INTEGRATION_SHA` 之後 HEAD 變了。`ALREADY_SYNCED` 當初只說「證據不算數」,沒給恢復路徑。
現在怎麼繞:靠人記得「Verdict 後不要再合碼」;或走 `stage7-g3-hardening` 那種跳過 Stage 1–3 的迴圈補丁。STATUS Backlog 仍用過期行號描述 Fresh→Verdict→Exit,看板與 tip 模板講的不是同一件事。

## Context(已知事實)
- owner 書面裁決:把整合回歸與同步移到 Final Fresh／雙軸審查／Verdict **之前**;獨立成 feature 走完整七站,當第一個真實 full lane 題目;會動模板節序與機械錨點,不該塞進發版前補丁。出處:notes/dispatch-v380-landing.md:L1011-L1018
- 派工單描述的**舊**節序是 Final Fresh(`7-review.md` 當時 :94)→ Verdict(:133)→ Exit 整合同步(:281);`ALREADY_SYNCED`(:291)只說證據不算數。出處:notes/dispatch-v380-landing.md:L1011-L1016
- 2026-09-12 tip 模板頂註已寫「出貨樹=審過的樹」:整合回歸必須在 Final Fresh 之前;Verdict 後改碼作廢 G3。出處:_templates/7-review.md:L30-L31
- tip 執行清單步 2c 已是整合回歸,且寫死「跑腳本算交集 → 合併 → 跑全套測試 → 再進 2d Final Fresh」,不是 Fresh → Verdict → Exit 才合併。出處:_templates/7-review.md:L100-L105
- tip `ALREADY_SYNCED` 已給恢復路徑:重跑 Final Fresh 綁當下 HEAD,或本項 FAIL;不得只寫「證據不算數」就過。出處:_templates/7-review.md:L110-L113
- 步 2d 是 Final Fresh Run;步 3 是雙軸審;步 5 是 Verdict(之後禁止再改程式碼,作廢 G3);步 6 Exit 只准文件／PR／living spec。出處:_templates/7-review.md:L121-L122 _templates/7-review.md:L152-L153 _templates/7-review.md:L167-L177 _templates/7-review.md:L179-L181
- md **閱讀**節序仍是 Coverage… → Verdict → Known Limits → Exit Checklist;Exit 條改成「整合回歸已在 Final Fresh **之前**完成」,並禁 Verdict 後再合併 `INTEGRATION_SHA`。出處:_templates/7-review.md:L303-L305 _templates/7-review.md:L330-L333
- Stage 7 graph 鏈是 S2c-integration → S2d-fresh → S2e-walkthrough → N3-axes → N5-verdict。出處:skills/dev-flow/stage7/graph.yaml:L45-L47 skills/dev-flow/stage7/graph.yaml:L78-L97
- S2c 節點正文要求整合回歸在 Final Fresh 之前,下一跳 S2d-fresh。出處:skills/dev-flow/stage7/nodes/S2c-integration.md:L23-L25 skills/dev-flow/stage7/nodes/S2c-integration.md:L36
- `check-stage67-enforcement.sh` ST 組驗頂註字面順序(整合回歸在 Final Fresh Run 之前)、「作廢 G3」、「重跑 Final Fresh」、Exit 不得再合併 INTEGRATION_SHA。出處:scripts/check-stage67-enforcement.sh:L298-L322
- `stage7-g3-hardening` 已有 4-spec 寫 S-1.1／S-1.2,但明寫「未重開 Stage 1–3」。出處:docs/dev/stage7-g3-hardening/4-spec.md:L9-L13 docs/dev/stage7-g3-hardening/4-spec.md:L17-L31
- 整合回歸工具檔頭仍自稱 Stage 7 Exit Checklist「(條件式)整合回歸」計算工具。出處:docs/dev/tools/devflow-integration-regression.sh:L2
- 本討論基準 plugin `3.23.3`。出處:.claude-plugin/plugin.json:L3
- owner 2026-09-12:本 slug `integration-before-verdict`、lane **full**、本 hop **只 Stage 1**、**不簽 G1**。出處:本 session 書面 brief
- 九條制度缺口同日已裁、實作另開後續 feature,不進本 slug。出處:notes/review-requirement-discovery-gaps.md:L15-L29
- 本 landing 後 STATUS Active 已有本 slug,stage=`1-discussion`,Gates 仍 G1⬜。出處:docs/dev/STATUS.md:L34

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| Stage 7 reviewer | 核准的 SHA 就是出貨 SHA | 寫 7-review;簽 PASS／REQUEST_CHANGES | 當下 7-review 清單與 graph | 採用現場是否仍照舊 Exit 合併 | GitHub、PR |
| owner / approver | 不在 PASS 之後被靜默換樹 | 簽 G3、改方法論 | 派工單舊痛 + tip 已補過清單 | 還剩哪些機械錨／範例在教舊序 | STATUS、聊天 |
| 實作者 | 照清單做完就能出貨 | 合 feature branch;跑回歸腳本 | 眼前那份 7-review 頂註 | 看板 Backlog 與模板是否同一故事 | git、CI |
| 採用專案維護者 | 抄模板不會核准錯樹 | 本機 plugin／dev-setup | 散發後的 `_templates/7-review.md` | 自己專案有沒有人仍從 Exit 才合碼 | `/plugin update` |
| STATUS 讀者 | 知道現在誰在做整合節序 | 讀／經腳本改看板 | Backlog 舊句(過期行號) | tip 清單其實已 2c→2d | `status-update.sh` |

### Current Journey
| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | reviewer | 在 feature tip 跑 Fresh／gauntlet | 7-review、gauntlet | 乾淨工作樹 | Source SHA = 當時 HEAD | 若稍後合碼,這 SHA 作廢 |
| 2 | reviewer | 雙軸審 + 填 Verdict PASS | 7-review.md | owner 或獨立 reviewer | verdict=PASS | 人以為這棵樹已鎖 |
| 3 | 實作者 | 照舊記憶在 Exit 合併 INTEGRATION_SHA | git、回歸腳本 | 整合分支新 commit | HEAD 變了 | 出貨樹 ≠ 核准樹 |
| 4 | 任一人 | 撞 `ALREADY_SYNCED` | 回歸腳本 | 無人給恢復步驟(舊文) | 證據作廢 | 舊文只說不算數 |
| 5 | owner | 看 STATUS 舊句決定要不要立案 | STATUS.md | 無人走完 1→7 | Backlog 仍寫 :94/:133/:281 | 看板與 tip 打架 |

正式 SOP(tip 頂註):2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只做文件。實際做法仍可能跟舊派工單／STATUS 舊句走。[Assumption] 採用現場「常」在 Verdict 後才合碼:從派工單舊痛推出,無 2026-09 採用 log;驗證期限 2026-10-12,到期未驗則本假設不得當 G2 事實。

### Workarounds
- 人記得「Verdict 後不要再合碼」,口頭交接,系統不留「已在 Fresh 前合過」的強制紀錄(除了有人真的跑 2c)。
- `stage7-g3-hardening` 用迴圈 4-spec 補 S-1.1／S-1.2,跳過討論與決策。
- STATUS 把整件事掛在 Backlog,用過期行號描述,當「還沒做」。
- 沒留下紀錄的步驟:誰在哪一次 Exit 合併了哪一個 `INTEGRATION_SHA`,常只在 local git reflog。

### Exceptions
- `N_A_NO_INCOMING`:分岔後對方零新 commit,不必合併。
- `ALREADY_SYNCED`:已經合過,交集證據作廢;tip 要重跑 Fresh 或 FAIL。
- Fast lane 仍用同一份 7-review 模板,沒有另一套 Exit。
- owner 自審:同一人寫碼又簽 PASS,更依賴節序寫死,不能靠第二人攔住後合碼。
- 誰都跳得過 graph／`--action`;沒有主機層擋「先 Verdict 再合併」。

### Evidence
- Observed:上列 Context 出處,本 working tree 讀過。
- Observed:owner 2026-09-12 書面 brief(本 session):slug `integration-before-verdict`;lane full;只 Stage 1;不簽 G1;來源指定 `notes/dispatch-v380-landing.md` 與 `_templates/7-review.md`。
- Observed:同日九條缺口已裁、實作另開,見 `notes/review-requirement-discovery-gaps.md` Owner Call。
- Reported:2026-08 派工單收尾節的舊節序與弱 `ALREADY_SYNCED`(dispatch-v380-landing)。
- `[Assumption]` 採用現場仍有人按舊 Exit 合併。風險:若為假,本 slug 主要剩文件／看板／錨點對齊,不是救活的出貨事故。期限:2026-10-12;誰驗:本 feature Stage 2 對採用回報或 dogfood 7-review 抽查。到期未驗 → 不得當 G2 事實。

## Goals
- G1:人簽 G3 PASS 時,核准的那棵樹就是出貨的那棵樹;之後沒有一次「合法」的整合同步改 HEAD。
- G2:已經合過碼(`ALREADY_SYNCED`)時,人拿得到可執行的恢復路(重綁送審樹或停止),不是「證據不算數、繼續勾」。
- G3:新接手的 reviewer 不靠口頭記憶,就能看出整合發生在 Fresh、雙軸、Verdict 之前。
- G4:本 slug 用完整 full lane 走完,讓「審過的樹=出貨的樹」被真的跑過一次,而不是只靠迴圈補丁宣稱已修。

## Requested solution（候選，未定案）
owner 帶來的做法(不是 Goal):把「整合回歸與同步」移到 Final Fresh／雙軸／Verdict **之前**;獨立走完整七站。Stage 2 仍須並排比較(含適用時的 no-build:只改 STATUS／派工單過期句、不動模板)。本 hop 不定案。

## Non-Goals(初稿)
- 本 hop 不簽 G1、不寫 2-decision、不改 `_templates/7-review.md` 正文。
- 不實作 2026-09-12 九條制度缺口(A-1~B-2);那些另開 feature。
- 不動 PR #196(b8 gate-twin owner PASS)的 STATUS 列。
- 不刪 SDC C 列;不把 Windows 複驗做進本 slug(本 landing 只從 Backlog 拿掉那列,不跑 Windows)。
- 不 bump plugin、不發版、不 merge。
- 不把 twin 閱讀動線「先讀 Verdict」改成先讀整合 —— 那是給人看判定,不是執行序。[Assumption] 閱讀動線不在本 slug;期限 2026-10-12,Stage 2 裁。

## Open Questions
- [x] Q1:整合要不要發生在 Fresh／雙軸／Verdict 之前?→ owner:要。
- [x] Q2:lane?→ owner:**full**。
- [x] Q3:這題是不是第一個真實 full lane?→ owner:是;獨立七站,不塞發版前補丁。
- [x] Q4:本 hop 簽不簽 G1?→ 不簽。status 留 draft。
- [x] Q5:九條缺口進不進本 slug?→ 不進;同日已裁,實作另開。
- [~] Q6:tip 清單／graph／ST 守衛已是 2c→2d,本 slug 還要動什麼?(帶假設:剩餘是文件節名／工具檔頭／STATUS 過期句／範例／機械錨是否仍教「Exit 才合碼」,加上用 1→7 真走一遍;不是重做已綠的 ST 字面序。期限 2026-10-12,Stage 2 對帳後才能當 G2 範圍。)
- [~] Q7:閱讀節序 Verdict 仍在 Exit 之前,算不算「整合在 Verdict 之前」未完成?(帶假設:不算。閱讀動線是給人看判定;執行序才改 HEAD。期限同上,Stage 2 裁。)
- [>] Q8:`stage7-g3-hardening` 要不要本 slug 宣告 superseded?→ 本討論不解;Stage 2／owner 裁要不要收編那份 4-spec。

## Constraints
- full lane;作者 ≠ G1 approver。
- 機械錨(ST 組、stage7 graph、integration-regression 守衛)若要動,必須與「出貨樹=審過的樹」同向,不准為了綠而放寬。
- STATUS 表列只准 `scripts/status-update.sh`;HISTORY 只准 `scripts/history-append.sh`。
- 本討論不改 hooks／skills 正文、不升 plugin `3.23.3`。
- 人看討論用繁中;ID 維持英式。

## 驗收雛形
- AC-1(G1):假設一條 feature 在 G3 被標 PASS,當出貨動作做完,則人核對「Verdict 綁定的樹」與「實際出貨的樹」是同一棵;中間沒有一次整合同步改 HEAD。
  - 從哪看:人用來宣告 PASS 與宣告 shipped 的同一份紀錄(現況常是 7-review 的 Source SHA／HEAD 句)
  - 看到什麼算對:兩個 SHA 相同;沒有「PASS 之後才合併 INTEGRATION_SHA」的紀錄
  - 拿什麼試:本母版下一輪真走 Stage 7 的 feature(本 slug 自己,或既有 dogfood／host-stack-fit 的 Exit 句當反例教材)
- AC-2(G2):假設回歸腳本印出 `ALREADY_SYNCED`,當 reviewer 繼續走,則他只能選「重綁當下送審樹再 Fresh」或「本項 FAIL 停下來」;不能只寫「證據不算數」就勾過。
  - 從哪看:人當時手上的恢復說明 + 該次 7-review 有沒有繼續勾
  - 看到什麼算對:出現可執行的二選一;沒有「不算數但過」
  - 拿什麼試:人為先合過整合分支再跑回歸腳本的 throwaway(本 hop 不跑)
- AC-3(G3):假設一個沒跟過 2026-08 補丁的 reviewer 第一次讀 Stage 7 怎麼做,當他排出「改 HEAD 的動作」與「Fresh／雙軸／Verdict」,則改 HEAD 的動作在後三者之前。
  - 從哪看:他實際遵循的步驟清單(不是口頭回憶)
  - 看到什麼算對:整合／合併出現在 Fresh、雙軸、Verdict 之前;Exit 不再是合併點
  - 拿什麼試:當下 `_templates/7-review.md` 頂註 2c–5 與 Exit 條
- AC-4(G4):假設本 slug 被當成「第一個真實 full lane」,當 Stage 1 完成,則後續仍要走 2→7 與 G1/G2/G3,而不是再跳過 1–3 補一刀。
  - 從哪看:本目錄是否只有討論稿、STATUS 是否把本 slug 放在 Active 1-discussion
  - 看到什麼算對:本 hop 無 2-decision／無 G1 PASS;Active 列 stage=1-discussion
  - 拿什麼試:本 PR 檔案清單

## 現況圖
誰:reviewer
做什麼:Fresh 綁 feature tip
工具:gauntlet / 7-review
痛點:SHA 還會被換
↓
誰:owner
做什麼:簽 Verdict PASS
工具:7-review.md
痛點:以為樹已鎖
↓
誰:實作者
做什麼:Exit 才合 INTEGRATION_SHA
工具:git / 舊清單
痛點:出貨樹不是核准樹

## 邏輯圖(ASCII)
```
old order
|-- Fresh Run          [bind SHA]
|-- dual-axis
|-- Verdict PASS       [approve that SHA]
+-- Exit sync          [merge INTEGRATION_SHA -> HEAD changes]
                       [approved tree != ship tree]

tip checklist (2026-09-12)
|-- 2c integration     [last HEAD change]
|-- 2d Fresh           [bind ship tree]
|-- 3 dual-axis
|-- 5 Verdict
+-- 6 Exit             [docs / PR only]

still mixed
|-- STATUS backlog     [stale L94/L133/L281 story]
|-- tool header        [still says Exit Checklist]
|-- hardening 4-spec   [skipped Stage 1-3]
+-- this slug          [full lane, Stage 1 only]
```

## Interview Log(推理鏈外顯)
- Q:舊痛是不是「核准樹 ≠ 出貨樹」?
  - 事實:notes/dispatch-v380-landing.md:L1011-L1016
  - 推理:Fresh／Verdict 綁的是合併前的 HEAD;Exit 再合 `INTEGRATION_SHA` 後 HEAD 變了。核准動作發生在換樹之前。
  - 結論:CONFIRMED 舊痛是節序,不是回歸腳本算錯。
- ⚠️ Q:owner 要的落點是什麼?本 hop 做到哪?
  - 事實:notes/dispatch-v380-landing.md:L1016-L1018
  - 推理:書面要整合在 Fresh／雙軸／Verdict 之前,且走完整七站。brief 把本 hop 收在 Stage 1、禁 G1 PASS。
  - 結論:CONFIRMED 方向已裁;本檔只討論,不實作、不簽 G1。
- Q:2026-09-12 tip 還是不是派工單寫的 Fresh→Verdict→Exit?
  - 事實:_templates/7-review.md:L100-L105 _templates/7-review.md:L110-L113 _templates/7-review.md:L330-L333
  - 推理:頂註 2c 已在 2d 前;ALREADY_SYNCED 已有恢復路;Exit 改成「已在 Fresh 之前完成」且禁再合碼。STATUS／派工單仍用舊行號描述。
  - 結論:CONFIRMED 清單與 Exit 條已改;看板故事過期。
- Q:graph 與 ST 守衛有沒有跟著改?
  - 事實:skills/dev-flow/stage7/graph.yaml:L45-L47 scripts/check-stage67-enforcement.sh:L298-L322
  - 推理:S2c 下一跳是 S2d;ST 組咬字面序與「不得再合併」。機械層已守新序,不是零保護。
  - 結論:CONFIRMED 核心執行鏈已釘;本 slug 若重寫已綠錨點會重複。
- ⚠️ Q:既有 hardening 能不能代替 full lane?
  - 事實:docs/dev/stage7-g3-hardening/4-spec.md:L9-L13
  - 推理:那份自己寫「未重開 Stage 1–3」。owner 要的是完整七站觀測,不是再補一刀規格。
  - 結論:CONFIRMED hardening ≠ 本 slug 的 full lane;Q8 是否 superseded 移交 Stage 2。
- Q:還有誰在講「Exit 才整合」?
  - 事實:docs/dev/tools/devflow-integration-regression.sh:L2
  - 推理:工具檔頭仍掛 Exit Checklist 舊身分。人搜「整合回歸」會先撞到 Exit 故事。
  - 結論:CONFIRMED 至少檔頭／STATUS 舊句仍教舊序;Q6 假設剩餘是對齊不是重做 2c。
- ⚠️ Q:閱讀節序 Verdict 在 Exit 前,算不算還沒把整合放到 Verdict 前?
  - 事實:_templates/7-review.md:L12-L22 _templates/7-review.md:L303-L333
  - 推理:閱讀動線要人先看判定;執行清單才准改 HEAD。兩者目的不同。把 ## Verdict 搬到整合節後面會打 gate-twin 五格。
  - 結論:OPEN 帶假設 Q7:閱讀序不在本 slug。Stage 2 裁。
- Q:本討論能不能當 G1 過關文件?
  - 事實:本檔 frontmatter status: draft
  - 推理:brief 明寫 No G1 PASS;Open Questions 仍有 `[~]`／`[>]`。
  - 結論:CONFIRMED 本 hop 停在 draft,不進 Stage 2。
