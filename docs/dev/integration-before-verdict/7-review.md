---
feature: integration-before-verdict
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-B-stage7
updated: 2026-09-12
---

# 7. 驗證 —— **不是 G3 PASS**

> 本檔是獨立 Implementer B 的 Stage 7 審查正本。`verdict:` 留 **PRE-REVIEW**。
> Human G3 仍留給 owner：抽驗一列 `檔:行` → 接受則用頁尾「提交判定」寫入
> `PASS`／`REQUEST_CHANGES`／`HOLD`。全勾不算 PASS。本 hop **不代填 G3 PASS**。

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
> 建議 Human G3 路徑:Verdict 門檻表 → 附錄 A1 R-5 兩 SHA 對照 → Coverage 抽 S-1.1 或 S-5.1 → 再決定。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-B-stage7`(獨立 fresh-context Cloud Agent B;**≠** Stage 6 #231 實作 owner) |
| Human G3 | 未寫。本檔 `verdict: PRE-REVIEW`。建議 owner 親自「提交判定」 |
| 讀取順序(可查) | ①`4-spec.md`(G2 PASS、16 S) ②`5-tasks.md`(T-1／T-2／T-3;R-5 不切 T) ③`git show c7e69ac`(#231 產品 diff,13 檔 +179/−13) ④測試碼／fixture(`check-stage67-enforcement.sh` `_filled_judge`、`scripts/fixtures/stage67-filled-tooth/` 五份) ⑤親跑 T-1／T-2／T-3 + 4-spec entry point + 步 2c(合併前兩次座標相同) → **之後才** ⑥`review-unlock` 讀薄 6-notes(無 Self-Review) |
| 圍欄 | `hooks/devflow-exec.sh review integration-before-verdict` 武裝後再 `review-unlock`。doctor:`COMPATIBLE`(契約 2.0.0,runtime 3.23.3,gauntlet 1.3.3) |
| 本輪性質 | 審查密封稿。產品碼已在 tip `#231`。本 PR 只加薄 6-notes + 本檔／html。**不是 G3 PASS** |

## Coverage Matrix

自建(grep 4-spec S 清單 ↔ 指定檢查／fixture／`rg`;**未先讀** 6-notes Self-Review;薄 6-notes 本來就沒有 Self-Review)。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/check-stage67-enforcement.sh` `_filled_judge` 353-366;fixture `scripts/fixtures/stage67-filled-tooth/void-only.md` → `ST-filled: void-only fail:void-only` | ✅ |
| S-1.2 | 同入口;fixture `rebind-sha.md` → `pass:rebind-sha:def4567890abc` | ✅ |
| S-1.3 | 同入口;fixture `item-fail.md` → `pass:item-FAIL` | ✅ |
| S-1.4 | `scripts/devflow-integration-regression.sh` 與 `docs/dev/tools/` 同檔 L206-207 GUIDANCE 含「重綁」與「FAIL」 | ✅ |
| S-2.1 | 同入口;fixture `na-incoming.md` → `no-fire:N_A_NO_INCOMING` | ✅ |
| S-2.2 | 同入口;fixture `draft-unclaimed.md` → `no-fire:draft` | ✅ |
| S-3.1 | `rg` `example/contract-expiry-reminder/` 舊針 0;`7-review.md:24` 現寫 2d Final Fresh | ✅ |
| S-3.2 | `manifests/p4-gauntlet-gates.md:52` 寫 2d;兩支腳本 L2「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」 | ✅ |
| S-3.3 | fixture `bad-dd-unresolved.md:229` 現寫 `2d gauntlet`;`check-spec-gate.sh` 對該檔 exit 1(C5) | ✅ |
| S-3.4 | 活路徑聯合 `rg` 0;`notes/dispatch-*`／HISTORY／stage7-loop 不在聯集 | ✅ |
| S-4.1 | `_templates/7-review.md` 頂註「整合回歸」offset 929 < 「Final Fresh Run」5616 | ✅ |
| S-4.2 | `check-stage67` 79 項 exit 0;`check-integration-regression-guard` 36/36;`test-evidence-gauntlet` 68/68 | ✅ |
| S-4.3 | 兩腳本仍有「絕不動樹」與 `sys.exit(code)`;STATUS 名 + exit 0/10/11/2 不變;無 `scripts/check-already-synced.sh` | ✅ |
| S-5.1 | Exit 文件寫成當下:`Source SHA` = `git rev-parse HEAD` = `a8793dfeb7d75c2347618d16f13a30ae807a9e6e`(見附錄 A1) | ✅ |
| S-5.2 | 對照:若 Fresh／Verdict 先綁 `5742b55` 再合 `0294f8f`,HEAD 會變成 `a8793df`;兩 SHA 都印出且不等(見附錄 A1) | ✅ |
| S-5.3 | `rg -n '跳過 2c&#124;Exit 才合併' docs/dev/integration-before-verdict/` 命中全是拒項／對照／spec,不是本 slug 執行指令(見附錄 A2) | ✅ |
| 既有測試套件(回歸) | 4-spec entry point + T-1／T-2／T-3 Verify(數字見 Verification Evidence) | ✅ |

**Verify 親跑**(5-tasks 原指令;2026-09-12;2c 合併 `0294f8f` 之後、Fresh 之前重跑):

```
ST-filled: void-only fail:void-only
ST-filled: rebind-sha pass:rebind-sha:def4567890abc
ST-filled: item-fail pass:item-FAIL
ST-filled: na-incoming no-fire:N_A_NO_INCOMING
ST-filled: draft-unclaimed no-fire:draft
✅ check-stage67-enforcement: Stage 6/7 強制條款齊(79 項檢查全過)
ST-filled count=5
S-4.1-ok
T-2-ok
example 舊針=0; fixture 2c gauntlet=0; spec-gate fixture exit=1; live-path rg=0
```

## Verification Evidence

- Source SHA: a8793dfeb7d75c2347618d16f13a30ae807a9e6e
- Final Fresh Run ID: 2026-09-12T1630Z-impl-B-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0(gate-twin pin;`scripts/requirements-methodology-render.txt`); contract 2.0.0; runtime 3.23.3; git 2.43.0; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-stage67-enforcement／check-integration-regression-guard／test-evidence-gauntlet | Final Fresh entry point(見上列四指令) | pass | 四層皆 exit 0:spec-gate 6/6;stage67 79;guard 36/36;gauntlet tests 68/68 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md` | pass | exit 0;6/6 形狀全過;16 條 S | |
| check-stage67-enforcement | `bash scripts/check-stage67-enforcement.sh` | pass | exit 0;79 項全過;ST-filled 5 列 | |
| check-integration-regression-guard | `bash scripts/check-integration-regression-guard.sh` | pass | exit 0;36/36 | |
| test-evidence-gauntlet | `bash scripts/test-evidence-gauntlet.sh` | pass | exit 0;68/68 | |
| Supply chain | `rg -n '執行清單 2c 的 Final Fresh&#124;Exit Checklist.*整合回歸.*計算工具' example/contract-expiry-reminder/ manifests/p4-gauntlet-gates.md scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` | pass | 命中 0 行(S-3.4;#231 改過 example／manifest／檔頭所以本層必跑) | |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

### 2c 整合結論

授權合併的那一次(Fresh **之前**跑兩次,STATUS／座標完全相同,然後合印出的 INTEGRATION_SHA,不是 branch 名):

- STATUS: SYNC_REQUIRED_NO_OVERLAP
- FORK / HEAD / INTEGRATION / REF: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab / 5742b5575e9f4b2f63b4aa1d425e858d2bace5dc / 0294f8f4d39fb6d8858a62191fd82773dee30e96 / refs/remotes/origin/main
- 恢復: n-a(SYNC_REQUIRED_NO_OVERLAP;已合 INTEGRATION_SHA 並在 Fresh 前跑全套)

合併後若再跑同一支腳本,會印 `ALREADY_SYNCED`(exit 2)。這次輸出**不當交集證據**。恢復走路徑 ①,不是只寫「證據不算數」:

- STATUS: ALREADY_SYNCED
- FORK / HEAD / INTEGRATION / REF: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab / a8793dfeb7d75c2347618d16f13a30ae807a9e6e / 0294f8f4d39fb6d8858a62191fd82773dee30e96 / refs/remotes/origin/main
- 恢復: 重綁 Final Fresh。Source SHA: a8793dfeb7d75c2347618d16f13a30ae807a9e6e

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得只寫作廢句讓已宣稱 ALREADY_SYNCED 過關(S-1.1) | check-stage67-enforcement ST-filled void-only | pass |
| 不得誤殺 N_A_NO_INCOMING 或未勾 draft(S-2.1／S-2.2) | ST-filled na-incoming + draft-unclaimed | pass |
| 不得重編號 2c、不得拆既有模板順序牙(S-4.1／S-4.2) | 模板 offset + 三支既有牙 | pass |
| 不得改整合腳本 STATUS／exit 演算法(S-4.3) | T-2-ok + 絕不動樹 + sys.exit(code) | pass |
| 不得改 HISTORY／dispatch／stage7-loop 當時句(S-3.4、OC-2) | #231 `--name-only` 無那些路徑 | pass |
| 不得在本 slug 過程檔宣告跳過 2c 或 Exit 才合併(S-5.3) | 附錄 A2 逐行分類 | pass |
| 不得碰 #196／diagram-ir-gate／九條缺口／本 hop bump plugin | #231 與本 PR 檔清單 | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 hop 不是 dev-run 引擎案。欄位留空。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 指定檢查 exit ≠ 0 且含 void-only;`void-only.md` | stderr:`ST-filled: void-only fail:void-only`;家族 exit 0(對照組紅、整支綠) | ✅ |
| S-1.2 | exit 0 且輸出含 def4567890abc | `ST-filled: rebind-sha pass:rebind-sha:def4567890abc` | ✅ |
| S-1.3 | exit 0 且含 item-FAIL | `ST-filled: item-fail pass:item-FAIL` | ✅ |
| S-1.4 | 兩檔 GUIDANCE 含重綁與 FAIL | 兩檔 L206-207:`下一步二選一:重綁 Final Fresh(Source SHA ≥7 hex),或在 7-review 寫本項 FAIL` | ✅ |
| S-2.1 | exit 0 且含 no-fire 與 N_A_NO_INCOMING | `ST-filled: na-incoming no-fire:N_A_NO_INCOMING` | ✅ |
| S-2.2 | exit 0 且含 no-fire 與 draft | `ST-filled: draft-unclaimed no-fire:draft` | ✅ |
| S-3.1 | example 目錄舊針空;Fresh 寫 2d | `rg` 0 行;`example/.../7-review.md:24`「執行清單 2d 的 Final Fresh Run」 | ✅ |
| S-3.2 | manifest／檔頭舊針空 | manifest:52「2d 的文檔化命令」;腳本 L2 新檔頭;舊針 `rg` 0 | ✅ |
| S-3.3 | fixture 無 2c gauntlet;spec-gate 仍 exit 1 | fixture:229 `2d gauntlet`;`check-spec-gate.sh` 該檔 exit 1 | ✅ |
| S-3.4 | 活路徑聯合 rg 空 | 聯集 0 行 | ✅ |
| S-4.1 | 頂註 integ 偏移 < fresh 偏移 | python 印 `929 5616 True` | ✅ |
| S-4.2 | 三支既有牙 exit 0 | 79;36/36;68/68 | ✅ |
| S-4.3 | 絕不動樹;exit 0/10/11/2;無自動重綁 | T-2-ok;無 `check-already-synced.sh` | ✅ |
| S-5.1 | 本檔 Source SHA 與 `git rev-parse HEAD` 逐字相同 | 附錄 A1:`a8793dfeb7d75c2347618d16f13a30ae807a9e6e` = HEAD(Exit 文件寫成當下) | ✅ |
| S-5.2 | 對照兩欄 SHA 都印且不等 | `5742b5575e9f4b2f63b4aa1d425e858d2bace5dc` ≠ `a8793dfeb7d75c2347618d16f13a30ae807a9e6e` | ✅ |
| S-5.3 | 命中必須是拒項／對照,不是執行指令 | 附錄 A2 逐行;本檔不把那兩句寫成指令 | ✅ |

## 截圖槽

本 feat 無產品前端;現象為 CLI／fixture／`rg`。截圖槽 N/A(無 `shots/` 定名檔 → 產檔器顯示佔位即可)。不准發明編輯 URL。不准新增一張只為了截圖。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／ST-filled／Source SHA
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | Stage 7 reviewer | 勾 2c 時不能靠「證據不算數」過關 | 跑 `check-stage67-enforcement.sh` | 終端機看 void-only 紅 | 檢查同步結束 | ✅ 人看見 fail:void-only 就不能勾過 |
| S-1.2 | Stage 7 reviewer | 已合過時重綁 Fresh 到當下 HEAD | 寫「重綁 Final Fresh。Source SHA: <hex≥7>」 | 把 SHA 貼進恢復欄 | SHA 短於 7 當 void-only | ✅ 本檔恢復欄綁 `a8793df`(≥7) |
| S-1.3 | Stage 7 reviewer | 座標已髒時停在 2c | 恢復欄寫「本項 FAIL」 | 從乾淨 FORK 重算 | 停到人重算 | ✅ fixture 綠;本 hop 走重綁不走 FAIL |
| S-2.1 | Stage 7 reviewer | 零新 commit 記 n-a 即過 | 腳本 STATUS=`N_A_NO_INCOMING` | 不合併 | 後來有新 commit 就重跑 | ✅ fixture no-fire;本 hop 實際是 SYNC_REQUIRED |
| S-2.2 | Stage 7 reviewer | 未勾草稿不被提前紅擋住 | 維持 `status: draft`、verdict 非 PASS | 繼續填,不要先送 G3 | 勾了或 verdict PASS 後改走 S-1.1 | ✅ 本檔 draft + PRE-REVIEW |
| S-3.1 | 採用者 | 抄範例走 2c 整合 → 2d Fresh | 打開 example 7-review／4-spec | 人打開檔 | 舊針仍在就同一 T 改到零 | ✅ 現檔寫 2d |
| S-5.1 | owner | Verdict 綁的樹就是出貨的樹 | 讀本檔 Source SHA 對 `git rev-parse HEAD` | Exit 只准文件／PR,不准再合碼 | 兩 SHA 不同就不得 ship | ✅ Exit 文件寫成當下相等;見 Known Limits ② |
| S-1.4／S-3.2／S-3.3／S-3.4／S-4.1／S-4.2／S-4.3／S-5.2／S-5.3 | — | — | — | — | — | 不適用(4-spec Operational Context 標不適用或純字面) |

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 填檔牙住 `scripts/check-stage67-enforcement.sh` `_filled_judge`(353-366);整合腳本仍只算只判。沒有第二套 CLI、沒有 event bus 讓腳本間接改 STATUS。
2. **資料所有權被繞過寫入**:未命中 —— 牙只讀 fixture／7-review 字面,不寫 7-review;腳本「絕不動樹」(`scripts/devflow-integration-regression.sh:8`)。本 hop 不改產品碼。
3. **相容性破壞包成新增**:未命中 —— ST-filled 是加射程,既有 ST 模板順序項仍在;STATUS 名與 exit 0／10／11／2 不變。
4. **一致性邊界被拆解**:未命中 —— 2c 結論塊仍是人寫一格恢復;腳本不覆寫 7-review。example 與 `bad-dd-unresolved.md` 同 T(#231 T-3)改口。
5. **宣告的 Test seam 未被使用**:未命中 —— 五份對照就是契約 Test seam(`scripts/fixtures/stage67-filled-tooth/`);入口仍是 `bash scripts/check-stage67-enforcement.sh`。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— ①牙仍讀字面不重算 merge-base;②本 hop 不新造 editor hook;③本 hop 才產生 7-review(Known limit ③ 的觀測物現在在)。

無未經授權 Boundary 變更。無 🔴。無要 park 的 🟡 Boundary。

## Standards Axis

產品樹 = `git show c7e69ac`(#231)。本 PR vs `origin/main` = 薄 6-notes + 本審查檔。

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟢 | `scripts/check-stage67-enforcement.sh:409` `MIN_CHECKS = 66` | 母版實跑 79;seed() 只帶一份 example → 地板必須 ≤ seed,否則 S67-0 假紅。#231 已說明 | 接受。抽驗:地板 66、本機 79、seed 約 67 | S-4.2 |
| F-2 | 🟢 | `example/contract-expiry-reminder/4-spec.html` | #231 未改此 html。舊針 `rg` 0,不擋 S-3.1 | 接受。活教師正本是 md;html 無舊針 | S-3.1 |
| F-3 | 🟢 | 薄 `6-implementation-notes.md` | #231 合 tip 時沒有 6-notes。本 hop 只補 FORK,無 Self-Review | 接受為 Stage 7 錨點,不當作者主張 | 過程 |
| F-4 | 🟢 | Design Boundary | 牙擁有通過／失敗;腳本擁有 STATUS／exit;無第二 CLI | 抽驗 `_filled_judge` 與腳本 L8／L217 | R-1／R-4 |

Dependency Direction／Boundary Leakage／Data Ownership／Interface Stability:未發現反向依賴、未漏出內部型別、非 owner 未直寫 STATUS、公開檢查入口字面不變。無 🔴。無未授權 🟡 Boundary。

## Spec Axis

| R | 判定 | 出處 |
|---|---|---|
| R-1 拒絕 void-only ALREADY_SYNCED | 符合 | S-1.1 紅;S-1.2／S-1.3 綠;S-1.4 GUIDANCE 兩詞都在。本檔合併後 ALREADY_SYNCED 走重綁 SHA,不是只寫作廢 |
| R-2 放過 n-a／draft | 符合 | S-2.1／S-2.2 no-fire;本檔 `status: draft`、`verdict: PRE-REVIEW` |
| R-3 清除活教師舊序 | 符合 | S-3.1～S-3.4 活路徑 0;example／manifest／檔頭改口;fixture 仍 C5 紅 |
| R-4 保留 2c 編號與模板牙 | 符合 | 2c 仍叫整合回歸;模板 929<5616;三牙綠;演算法／exit 不變 |
| R-5 出貨樹=核准樹 | 符合(本 hop 真跑) | S-5.1 Exit 文件寫成當下 SHA=HEAD;S-5.2 對照兩 SHA 不等;S-5.3 無執行指令。順序:2c 合 `0294f8f` → 全套 → 2d Fresh 綁 `a8793df` |
| M-1～M-4 | 符合 | example 2d;fixture 2d;manifest 2d;檔頭「不是 Exit 程序」 |
| Design Boundary | 符合 | 見 Design Integrity Check;無 L2、無未授權變更 |
| 6-notes Deviations | 無作者 Self-Review 可對 | 薄 6-notes 只有 D-s7-fork(只記 FORK)。#231 PR 正文 T-1／T-2／T-3 與本 hop 獨立數字相符 |

## 變更架構圖

產品(#231,已在 tip;`git show c7e69ac` basename)與本 PR 審查密封:

```
[check-stage67-enforcement.sh]
    |  ST-filled _filled_judge
    +--> fixtures/stage67-filled-tooth/
         void-only.md
         rebind-sha.md
         item-fail.md
         na-incoming.md
         draft-unclaimed.md

[devflow-integration-regression.sh] ----parity---- [docs/dev/tools/devflow-integration-regression.sh]
    |  header + GUIDANCE only
    +--> manifests/p4-gauntlet-gates.md   (2c needle -> 2d)

[example/contract-expiry-reminder/7-review.md]
[example/contract-expiry-reminder/7-review.html]
[example/contract-expiry-reminder/4-spec.md]
    +--> scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md

本 PR(審查密封,不是產品碼):
[6-implementation-notes.md]  FORK=c7e69ac
[6-implementation-notes.html]
[7-review.md]                Source SHA=a8793df (Fresh = 2c 後 HEAD)
[7-review.html]              G3 twin
```

無新公開 HTTP 端點、無新表。改 Diff 必須改本圖。

## Diff(merge-base(main)..HEAD,逐檔折疊)

`merge-base(origin/main, HEAD)` 在寫本檔時 = `0294f8f`。產品 #231 已在 main,不在本 PR diff。本 PR 相對 main 是薄 6-notes(+html)與本審查檔。

<details>
<summary>docs/dev/integration-before-verdict/6-implementation-notes.md + 本檔 twin — 薄 FORK 錨點(+N 見 git show 5742b55)</summary>

FORK_INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab。無 Self-Review。產品 diff 以 `git show c7e69ac` 為準。

</details>

<details>
<summary>docs/dev/integration-before-verdict/7-review.md + 7-review.html — 本審查正本</summary>

本檔。`verdict: PRE-REVIEW`。Source SHA 綁 2c 後 HEAD `a8793dfeb7d75c2347618d16f13a30ae807a9e6e`。

</details>

<details>
<summary>產品 #231(已在 tip;審查對象,不是本 PR 新增)</summary>

13 files, +179/−13。basename 見變更架構圖。入口仍是 `bash scripts/check-stage67-enforcement.sh`。完整 hunk:`git show c7e69ac`。

</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。**

機械面(給 Human 抽驗,不是代填判定):

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 16/16 自建矩陣 ✅ | Coverage Matrix |
| 既有全綠 | entry point 四層 + T-1／T-2／T-3 | 6/6;79;36;68/68 |
| 現象證據逐 S 相符 | 16/16 | 現象證據表 |
| Evidence 契約 | Fresh 綁 HEAD;`--review-file` 見附錄 A3 | Source SHA=`a8793dfeb7d75c2347618d16f13a30ae807a9e6e` |
| 無 🔴 | 無 | Standards／Spec |
| 2c 在 Fresh 之前 | 是 | 先合 `0294f8f`,再 Fresh |
| Human G3 | **未寫** | owner「提交判定」 |

建議 Human:接受則 `verdict: PASS` 且 `status` 仍等 Exit;不接受則 `REQUEST_CHANGES` 列要改的 F。本 Agent 不寫 PASS。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 填檔牙讀字面,不重算 git merge-base(4-spec Known limit ①) | 低 | park;腳本座標真偽仍靠人貼結論塊。owner=方法論;追蹤=4-spec Design Constraints |
| 2 | 編輯器不能擋 Verdict 後改碼,也不能讓「含 Source SHA 的 commit」等於該 commit 自己的 SHA(4-spec Known limit ②) | 中 | park。Exit 文件寫成當下 SHA=HEAD 已證。之後若再 commit 本檔,HEAD 會漂;合法恢復=重綁 Final Fresh(AS-1 路徑 ①),不得再合產品碼。owner=方法論 |
| 3 | ~~本 hop 不產生 7-review(4-spec Known limit ③)~~ | — | 已解除:本檔即觀測物 |
| 4 | MIN_CHECKS 地板 66 ≠ 母版實跑 79 | 低 | 接受;見 F-1／#231 說明 |
| 5 | 本檔 `verdict: PRE-REVIEW`;全勾也不算 shipped | 資訊 | Human G3 仍必須「提交判定」 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**(applicable):無未授權 Boundary 變更。F-1～F-4 皆 🟢 且未改 R/S／所有權／公開 Interface。無須 L2、無須 park Boundary
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配,fast 免):本 PR 是審查密封,產品碼已在 #231;留給 Human G3
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 結論(含三個 SHA 與 canonical ref)在「2c 整合結論」。Source SHA 在 Exit 文件寫成當下等於 HEAD。Verdict 之後不得再改程式碼
- [ ] PR → develop(feature branch,禁直上 master;本專案整合分支是 `main`)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`(本 repo 無 living spec;`n-a`)
- [ ] STATUS.md 已更新為 shipped(整合分支上、PR 合併後由合併者做,不塞進本 branch)
- [ ] 7-review frontmatter status: shipped;上游 artifact 可保留 approved
- [x] 7-review.html 已產生(G3 twin;`scripts/build-gate-twin.py`;審頁另跑 `scripts/build-stage7-html.py --action` → `/tmp/ibv-stage7-shots.html`,不覆寫 twin)
- [ ] feature branch 已刪 / worktree 已清

## 附錄:本輪特有

### A1　R-5 真跑(S-5.1／S-5.2)

**S-5.1 Exit 文件寫成當下 Source SHA = HEAD**

```
git rev-parse HEAD
a8793dfeb7d75c2347618d16f13a30ae807a9e6e
```

本檔 Verification Evidence `Source SHA:` 同一字串。證明指令(Fresh／Exit 文件寫成當下;工作樹可有未提交的本檔):

```
test "$(python3 -c "import re,pathlib; t=pathlib.Path('docs/dev/integration-before-verdict/7-review.md').read_text(); print(re.search(r'- Source SHA:\s*([0-9a-fA-F]{7,})', t).group(1))")" = "$(git rev-parse HEAD)" && echo S-5.1-ok
```

這不是「commit 含自己的 SHA」(做不到)。這是 4-spec S-5.1 要的:勾／寫 Exit 文件時兩字串相同。之後若提交本檔,HEAD 會變 —— Known Limits ②;合法恢復=重綁,不是再合 INTEGRATION_SHA。

**S-5.2 Verdict-then-merge 對照(本 hop 實樹,不是假 SHA)**

若先在薄 6-notes tip `5742b55` 綁 Fresh／Verdict,再合腳本印的 `0294f8f`:

| 欄 | SHA |
|---|---|
| 對照 Verdict Source SHA | 5742b5575e9f4b2f63b4aa1d425e858d2bace5dc |
| 合完後 HEAD | a8793dfeb7d75c2347618d16f13a30ae807a9e6e |

`5742b5575e9f4b2f63b4aa1d425e858d2bace5dc` ≠ `a8793dfeb7d75c2347618d16f13a30ae807a9e6e`。這就是「出貨樹 ≠ 核准樹」。本 hop **沒有**走這條:先 2c 合 `0294f8f`,再 Fresh 綁合完的 HEAD。

### A2　S-5.3 命中分類(不是執行指令)

`rg -n '跳過 2c|Exit 才合併' docs/dev/integration-before-verdict/` 有命中。4-spec 允許拒項／對照敘事。逐行:

| 檔:行 | 分類 | 為什麼不是本 slug 指令 |
|---|---|---|
| `1-discussion.md:62` | 風險假設 | 「誰都可跳過 2c」是現場風險,不是本 slug 要跳 |
| `1-discussion.md:69` | `[Assumption]` | 同上 |
| `1-discussion.md:176` | `[Assumption]` | 同上 |
| `2-decision.md:23` | 拒項 C | 方案 C 被拒;劣勢寫「誰都能跳過 2c」 |
| `2-decision.md:52` | 拒項 C | 「跳過 2c 與只寫作廢仍能過」= 為什麼不選 C |
| `2-decision.md:61` | 問題陳述 | 「人可以跳過 2c」是現況缺口 |
| `2-decision.md:96` | SC-5 禁令 | 「無『跳過 2c』或『Exit 才合併』的流程宣告」 |
| `4-spec.md:221,224,253,255,257,309,405` | spec／禁令 | R-5／S-5.3 在禁止那兩句當指令 |
| `5-tasks.md:79` | Split Decisions | 「禁寫」那兩句,不是叫人跳 |
| 同目錄 `*.html` | twin | 與 md 同期拒項／spec |

本檔與薄 6-notes **沒有**把「跳過 2c」或「Exit 才合併」寫成要做的步驟。

### A3　Fresh／gauntlet 指令與原始輸出

```
test -x docs/dev/tools/devflow-evidence-gauntlet.sh
bash docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/integration-before-verdict/7-review.md \
  --source-sha $(git rev-parse HEAD) --review-file \
  --require-layer check-spec-gate \
  --require-layer check-stage67-enforcement \
  --require-layer check-integration-regression-guard \
  --require-layer test-evidence-gauntlet
```

Fresh 實跑(工作樹有未提交本檔;HEAD 仍是 `a8793dfeb7d75c2347618d16f13a30ae807a9e6e`):

```
✅ evidence gauntlet: 60 checks passed — docs/dev/integration-before-verdict/7-review.md
```

S-5.1 同時:`test Source SHA = git rev-parse HEAD` → `S-5.1-ok`。
Profile Required 是一條全形 `／` 字串,Evidence 表第一列 Layer 必須與該字串全等,否則 E7 把四層當成一層缺席。

### A4　作者對照(N4;薄 6-notes 無 Self-Review)

薄 6-notes 明確寫「沒有 Self-Review」「不得從本檔得到作者主張」。對照結果:沒有作者矩陣可裁。#231 PR 說 T-1／T-2／T-3 已綠;本 hop 獨立重跑數字相符(ST-filled 5;T-2-ok;活路徑 0;C5 仍紅)。D-s7-fork(只記 FORK)屬實,不是 L2。

### A5　2c 原始結論行(合併前,跑兩次相同)

```
STATUS: SYNC_REQUIRED_NO_OVERLAP
FORK_INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab
FEATURE_HEAD: 5742b5575e9f4b2f63b4aa1d425e858d2bace5dc
INTEGRATION_SHA: 0294f8f4d39fb6d8858a62191fd82773dee30e96
INTEGRATION_REF: refs/remotes/origin/main
共同戰場:無
結論:STATUS=SYNC_REQUIRED_NO_OVERLAP FORK=c7e69ac… HEAD=5742b55… INTEGRATION=0294f8f…(refs/remotes/origin/main)—— 仍要合併 INTEGRATION_SHA + 跑全套測試
```

合的是 `0294f8f4d39fb6d8858a62191fd82773dee30e96`,得到 merge `a8793df`。之後才 Fresh。
