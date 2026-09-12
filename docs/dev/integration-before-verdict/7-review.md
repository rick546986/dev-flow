---
feature: integration-before-verdict
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-c
updated: 2026-09-12
---

# 7. 驗證 —— **不是 G3 PASS**（Implementer C 獨立預審）

> Human G3 **留給人**。本檔 `verdict: PRE-REVIEW`、`status: draft`。
> 建議 reviewer 路徑：適格人類 → 抽驗 Coverage／現象任一列的 `檔:行` → 再填 Human verdict。
> 全勾不算 PASS。Agent 不代填 PASS／REQUEST_CHANGES／HOLD。

> ## Reviewer 閱讀動線(**必留;給看的人,不是給寫的人**)
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

## 限制聲明（讀取順序 + 身分）

| | |
|---|---|
| Author C | Implementer C（獨立 Cloud Agent；**≠** Stage 6 `#231` 實作 owner） |
| Human G3 | **未填**。本檔只交預審證據包 |
| 讀取順序（可查） | ①`4-spec.md`（G2 `status: approved` / `verdict: PASS`）②`5-tasks.md` ③測試／fixture／`git show c7e69ac` ④親跑 T-1／T-2／T-3 Verify + S-5.1～S-5.3 ⑤**2c 兩次**（先於 2d）⑥Final Fresh 入口 ⑦才 `review-unlock` 讀 thin `6-implementation-notes.md` |
| 圍欄 | `hooks/devflow-exec.sh review integration-before-verdict` 已武裝；doctor `COMPATIBLE` |
| 本輪性質 | draft 預審。**不是 G3 PASS**。不改 STATUS。不改產品碼 |

#231 沒有 6-notes Self-Review 可錨定。thin 6-notes 是本 hop 補的 FORK／doctor 錨，八問自承「未知／不代簽」。

## Coverage Matrix

自建（grep fixture／腳本字面 ↔ 4-spec S 清單；**未先讀** Self-Review）。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `ST-filled: void-only fail:void-only`；`scripts/check-stage67-enforcement.sh:353-366` + `scripts/fixtures/stage67-filled-tooth/void-only.md` | ✅ |
| S-1.2 | `ST-filled: rebind-sha pass:rebind-sha:def4567890abc`；同函式 + `rebind-sha.md` | ✅ |
| S-1.3 | `ST-filled: item-fail pass:item-FAIL`；同函式 + `item-fail.md` | ✅ |
| S-1.4 | GUIDANCE `scripts/devflow-integration-regression.sh:202-211`（正本與 `docs/dev/tools/` 同句）含「重綁」與「FAIL」 | ✅ |
| S-2.1 | `ST-filled: na-incoming no-fire:N_A_NO_INCOMING` | ✅ |
| S-2.2 | `ST-filled: draft-unclaimed no-fire:draft` | ✅ |
| S-3.1 | `rg` example 零命中「執行清單 2c 的 Final Fresh&#124;執行清單 2c gauntlet」；`example/contract-expiry-reminder/7-review.md:24` 已寫 2d | ✅ |
| S-3.2 | manifest `manifests/p4-gauntlet-gates.md:52` 寫 2d；兩腳本檔頭「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」 | ✅ |
| S-3.3 | `bad-dd-unresolved.md` 無「2c gauntlet」；`check-spec-gate.sh` 對該檔 exit 1（C5） | ✅ |
| S-3.4 | 活路徑聯合 `rg` 零命中 | ✅ |
| S-4.1 | `_templates/7-review.md` 頂註「整合回歸」偏移 &lt;「Final Fresh Run」；`S-4.1-ok` | ✅ |
| S-4.2 | `check-stage67-enforcement.sh` 79 項 exit 0；`check-integration-regression-guard.sh` 36 項 exit 0；`test-evidence-gauntlet.sh` 68/68 | ✅ |
| S-4.3 | 腳本仍「絕不動樹」；STATUS 四名 + exit `, 2` / `, 10` / `, 11` 仍在；`sys.exit(code)` 仍在 | ✅ |
| S-5.1 | 2d 當下 Source SHA = `git rev-parse HEAD` = `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`。**Exit 未勾** → 不宣稱 after-Exit | ⚠ |
| S-5.2 | 對照：Verdict Source SHA=`aaa1111`；合完後 HEAD=`bbb2222`；兩值都印且不等 | ✅ |
| S-5.3 | `rg -n '跳過 2c&#124;Exit 才合併' docs/dev/integration-before-verdict/` 命中皆拒項／禁令／對照，無「本 slug 要跳過／Exit 才合」指令 | ✅ |
| 既有測試套件(回歸) | 5-tasks T-1／T-2／T-3 Verify + Final Fresh 四支入口 | ✅ |

**Verify 親跑**（5-tasks 原指令；2026-09-12；2c 之前已跑完 T 組，2d 再跑入口）：

```
ST-filled count=5
ST-filled: void-only fail:void-only
ST-filled: rebind-sha pass:rebind-sha:def4567890abc
ST-filled: item-fail pass:item-FAIL
ST-filled: na-incoming no-fire:N_A_NO_INCOMING
ST-filled: draft-unclaimed no-fire:draft
✅ check-stage67-enforcement: Stage 6/7 強制條款齊(79 項檢查全過)
✅ 整合回歸守衛:全過(36 項)
✅ evidence gauntlet tests: 68/68 passed
S-4.1-ok
T1_VERIFY_EXIT:0
T-2-ok
T2_VERIFY_EXIT:0
=== G2 spec gate:.../bad-dd-unresolved.md === C5 FAIL → T3_VERIFY_EXIT:0
✅ G2 spec gate:docs/dev/integration-before-verdict/4-spec.md 6/6
```

## Verification Evidence

- Source SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab
- Final Fresh Run ID: 2026-09-12T1608Z-implementer-c-r1
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Toolchain: python3.12.3; markdown-it-py==4.0.0; contract 2.0.0; runtime 3.23.3; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-stage67-enforcement／check-integration-regression-guard／test-evidence-gauntlet | Final Fresh entry point（上列四指令） | pass | spec-gate 6/6；stage67 79 項 exit 0；guard 36 項；gauntlet tests 68/68；T1/T2/T3 Verify exit 0 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md` | pass | exit 0；6/6 形狀全過；16 條 S | |
| check-stage67-enforcement | `bash scripts/check-stage67-enforcement.sh` | pass | exit 0；79 項；ST-filled 5 行 | |
| check-integration-regression-guard | `bash scripts/check-integration-regression-guard.sh` | pass | exit 0；36 項 | |
| test-evidence-gauntlet | `bash scripts/test-evidence-gauntlet.sh` | pass | 68/68 passed | |
| Supply chain | `rg -n '執行清單 2c 的 Final Fresh&#124;Exit Checklist.*整合回歸.*計算工具' example/contract-expiry-reminder/ manifests/p4-gauntlet-gates.md scripts/devflow-integration-regression.sh docs/dev/tools/devflow-integration-regression.sh` | pass | 0 hits（S-3.4） | |
| Mutation | | n-a | | Explicitly excluded（4-spec Verification Profile） |
| e2e／Playwright | | n-a | | Explicitly excluded：無產品前端 |
| Race／stress | | n-a | | Explicitly excluded：單檔字面檢查 |
| Windows 真機 | | n-a | | Out of Scope |

**2c 在 2d 之前**（兩次座標相同；工作樹乾淨；腳本只算只判）：

```
STATUS: N_A_NO_INCOMING
FORK_INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab
FEATURE_HEAD: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab
INTEGRATION_SHA: c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab
INTEGRATION_REF: refs/remotes/origin/main
共同戰場:無
結論:STATUS=N_A_NO_INCOMING FORK=c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab HEAD=c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab INTEGRATION=c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

第二次相同。未合併任何 INTEGRATION_SHA（n-a 不必合）。

**Gauntlet 聲明**：`--review-file` 會把本路徑 Source SHA 強制成當時 `HEAD`。2d 在**尚未提交本檔**時跑，宣告 SHA = `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab` = 當時 HEAD = `#231` 出貨樹。本 PR 之後若再有 docs commit，HEAD 會動 → 必須重綁 Source SHA 再跑 2d，否則 E2 stale。**不把提交後未重綁寫成已過 S-5.1 after-Exit。**

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得只寫「證據不算數／輸出不算數」就讓已宣稱 ALREADY_SYNCED 過關(S-1.1) | ST-filled void-only exit ≠ 0 + `void-only` | pass |
| 不得誤殺 N_A_NO_INCOMING 或未勾 draft(S-2.1／S-2.2) | ST-filled na-incoming／draft-unclaimed no-fire | pass |
| 不得重編號 2c、不得拆既有模板順序牙(S-4.1／S-4.2) | S-4.1-ok + 三支牙 exit 0 | pass |
| 不得改整合腳本 STATUS／exit 演算法(S-4.3) | 四 STATUS 名 + exit 0／10／11／2 +「絕不動樹」 | pass |
| 不得改 HISTORY／dispatch／stage7-loop 當時句(S-3.4、OC-2) | `#231` diff 無那些路徑 | pass |
| 不得在本 slug 過程檔宣告跳過 2c 或 Exit 才合併(S-5.3) | 過程檔 `rg`；命中皆拒項／禁令 | pass |
| 不得碰 #196／diagram-ir-gate／九條缺口／本 hop bump plugin | `#231` 與本 PR 檔名清單 | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

Stage 6 為 `#231` 雲端實作；本 Stage 7 為獨立 Implementer C 手審。無 dev-run ledger。本節留白。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

Reviewer 親自實跑。不採信 6-notes 貼文（#231 本來就沒有）。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 指定檢查 exit 與 stderr；void-only 必須紅 | `ST-filled: void-only fail:void-only`；整支 `check-stage67` 仍 exit 0（對照組預期紅、家族綠） | ✅ |
| S-1.2 | exit 0 且輸出含 `def4567890abc` | `ST-filled: rebind-sha pass:rebind-sha:def4567890abc` | ✅ |
| S-1.3 | exit 0 且含 `item-FAIL` 或「本項 FAIL」 | `ST-filled: item-fail pass:item-FAIL` | ✅ |
| S-1.4 | 兩檔 GUIDANCE 含「重綁」或「重跑 Final Fresh」，且含「FAIL」 | `scripts/devflow-integration-regression.sh:206-207`「重綁 Final Fresh」+「本項 FAIL」；散發副本同步 | ✅ |
| S-2.1 | exit 0 且含 `no-fire` 與 `N_A_NO_INCOMING` | `ST-filled: na-incoming no-fire:N_A_NO_INCOMING` | ✅ |
| S-2.2 | exit 0 且含 `no-fire` 與 `draft` | `ST-filled: draft-unclaimed no-fire:draft` | ✅ |
| S-3.1 | example 兩檔零命中舊 2c=Fresh／gauntlet 針 | `rg` 空；`7-review.md:24`「執行清單 2d 的 Final Fresh Run」 | ✅ |
| S-3.2 | manifest／兩檔頭零命中舊針 | manifest:52 寫 2d；檔頭 L2「不是 Exit 程序」 | ✅ |
| S-3.3 | fixture 無「2c gauntlet」且 spec-gate 仍 exit 1 | C5 待裁決仍紅；T3_VERIFY_EXIT:0 | ✅ |
| S-3.4 | 活路徑聯合 `rg` 空 | LIVE_RG_ZERO | ✅ |
| S-4.1 | 頂註 integ 偏移 &lt; fresh | `S-4.1-ok` | ✅ |
| S-4.2 | 三支既有牙 exit 0 | 79／36／68 皆綠 | ✅ |
| S-4.3 | 四碼 +「絕不動樹」+ 只改檔頭／GUIDANCE | `#231` 兩腳本各 ±6 行；`sys.exit(code)` 仍在 | ✅ |
| S-5.1 | 7-review Source SHA 與 `git rev-parse HEAD` | 2d 當下兩字串 = `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`。Exit 未勾 → **不相符不得寫 after-Exit ✅** | ⚠ |
| S-5.2 | 對照兩欄都印且不等 | `aaa1111 ≠ bbb2222`（故意 Verdict 後才合） | ✅ |
| S-5.3 | 過程檔 `rg`；拒項可命中 | 見附錄 A5；無執行指令要跳過 2c／Exit 才合 | ✅ |

## 截圖槽

本 feat 無產品前端；現象為 CLI／fixture exit。截圖槽 N/A。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場；牙在 shell exit／fixture 字面
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | Stage 7 reviewer | 勾 2c 時不能靠「證據不算數」過關 | 跑 `check-stage67` 讀填檔 | 終端機 | void-only 紅 → 補重綁或 FAIL，不要進 Verdict | ✅ 人能完成工作 |
| S-1.2 | Stage 7 reviewer | 恢復路徑走通再進 2d | 恢復欄寫 `Source SHA:` ≥7 hex | 把 SHA 寫進 7-review | SHA 短於 7 → 當 void-only | ✅ |
| S-1.3 | Stage 7 reviewer | 停在 2c，不整份 G3 默過 | 恢復欄寫「本項 FAIL」 | 從乾淨 FORK 重跑腳本 | 停到人重算 | ✅ 等待未被標成完成 |
| S-2.1 | Stage 7 reviewer | 零新 commit 記 n-a 即過 | 轉記 `N_A_NO_INCOMING` | 無合併 | 後來對方有 commit → 重跑 | ✅ 本 hop 即此 STATUS |
| S-2.2 | Stage 7 reviewer | 未勾草稿不被提前紅 | 繼續填；不先送 G3 | 編輯器 | 勾了 2c 或 `verdict: PASS` 才開火 | ✅ 本檔 draft／PRE-REVIEW |
| S-5.1 | owner | Verdict 綁的樹就是出貨的樹 | 對帳 Source SHA 與 HEAD | Exit 只准文件／PR | 兩 SHA 不同不得 ship；HEAD 變了作廢 G3 | ⚠ 預審已對上 2d HEAD；Exit／G3 留給人 |
| S-1.4／S-3.*／S-4.* | — | — | — | — | — | 不適用（4-spec 標無人員交接） |

六條抽查：技術過但人做不完／看得見沒決策權／等待誤標完成／系統外無追蹤／中斷不能恢復／資訊過期 —— 填檔牙只讀字面（Known limit ①），人仍有恢復決策權；n-a 沒被標成「已合併」。

## Design Integrity Check(Design Boundary Contract = `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 牙住 `scripts/check-stage67-enforcement.sh:325-397`；沒有新 CLI 被腳本或 example 當唯一入口（無 `check-already-synced.sh` 檔）。
2. **資料所有權被繞過寫入**:未命中 —— 牙只讀 7-review；整合腳本仍擁有 STATUS 名稱與三 SHA（`devflow-integration-regression.sh:8-10,189-217`）。
3. **相容性破壞包成新增**:未命中 —— exit 碼集合仍是 0／10／11／2；`ALREADY_SYNCED` 仍 exit 2。
4. **一致性邊界被拆解**:未命中 —— 腳本仍只算只判、不動樹；合併仍是人的事。
5. **宣告的 Test seam 未被使用**:未命中 —— 五份 fixture 由同一 `_filled_judge` 跑；測試名對 S-1.1～S-2.2。
6. **Known design limit 被悄悄「解決」**:未命中 —— 牙仍讀字面、不重算 merge-base；無 editor hook 擋 Verdict 後改碼。

## Standards Axis

- F-1 🟡 `scripts/check-stage67-enforcement.sh:405-409` | 問題：母版實得 79 項，`MIN_CHECKS=66`（seed 只帶 example、實得 67）。地板為免 S67-0 假紅而留下 13 項餘裕 —— 母版刪掉部分 ST-filled 以外的檢查仍可能踩在地板上。#231 PR 已寫明。 | 建議：讓 architecture-guards `seed()` 帶上 `stage67-filled-tooth/`，地板收到 79。不擋本 hop（既有 S67-0／S67-9 契約）。影響回歸牙強度，非 R/S 行為。
- F-2 🟡 `#231` 無 `6-implementation-notes.md` | 問題：Stage 6 缺 FORK 欄與 T Review Log；2c 錨靠本 hop thin 6-notes 事後補（FORK=切開審查 branch 的 tip，不是 T-1 當下的 `#226`）。 | 建議：後續 hop 若再實作，步 0 當場記 40 碼。本 hop 不補假 PASS。影響流程可信度。
- F-3 🟢 Diff Budget | #231 13 檔（含五份 fixture）&gt; 估 ≤9。4-spec 寫超支是 L1 訊號不是自動偏差；檔名仍在 5-tasks Files 聯集。 |

Design Boundary 四項（Standards 加查）：
- **Dependency Direction**:符合 —— 牙 → 7-review 字串；腳本 → git；無反向。
- **Boundary Leakage**:符合 —— 無第二套整合 CLI；STATUS 名稱仍由腳本擁有。
- **Data Ownership**:符合 —— 恢復欄是人填；牙不寫 7-review。
- **Interface Stability**:符合 —— GUIDANCE／檔頭 additive；exit 碼相容。

無 🔴。

## Spec Axis

- R-1 符合（S-1.1 紅、S-1.2／S-1.3 綠、S-1.4 GUIDANCE 有下一步）。出處：`check-stage67-enforcement.sh:353-366`；`devflow-integration-regression.sh:202-211`。
- R-2 符合（S-2.1／S-2.2 no-fire）。出處：同 `_filled_judge` 前兩分支。
- R-3 符合（S-3.1～S-3.4 `rg` 零 + fixture 仍 C5 紅）。
- R-4 符合（2c 仍叫整合回歸且在 2d 前；三支牙綠；演算法未改）。
- R-5 **部分**：S-5.2／S-5.3 符合。S-5.1 在 2d 當下 SHA=HEAD，但 **未勾 Exit、未 Human G3** → 不得寫「after-Exit 全綠」。本軸不把 ⚠ 升成符合、也不降成偏離翻案。
- 6-notes Deviations：thin 檔無產品 D-n。F-2 是缺檔，不是 L2 翻 Decision。
- Design Boundary 契約逐條：符合；Known limit ①～③ 未被悄悄修掉。
- F-1 為地板餘裕，不改 R-1 開火語意。

## 變更架構圖

```text
[填好的 7-review.md]
   STATUS + FORK/HEAD/INTEGRATION/REF + 恢復欄
        |
        v
[scripts/check-stage67-enforcement.sh]
   ST 模板序（既有） + ST-filled _filled_judge
     |-- void-only --------> exit != 0 (void-only)
     |-- rebind Source SHA -> exit 0
     |-- 本項 FAIL --------> exit 0
     |-- N_A / draft ------> no-fire
        |
        +-- 同一入口 bash scripts/check-stage67-enforcement.sh
            無 check-already-synced.sh

[scripts/devflow-integration-regression.sh]
   == docs/dev/tools/ 散發副本
   只算只判 / 絕不動樹
   GUIDANCE: 重綁 Final Fresh 或 本項 FAIL
   檔頭: 步 2c, Fresh 之前, 不是 Exit

[活教師]
   example/7-review + 4-spec  -- 2c Fresh/gauntlet --> 2d
   manifests/p4-gauntlet-gates.md                 --> 2d
   spec-gate fixture 同一 T 改口; C5 仍紅

[本 slug 7-review / Exit]
   2c 整合 --> 2d Fresh --> 雙軸 --> Human G3
   Source SHA 必須 = HEAD（出貨樹=核准樹）
```

圖上 basename 對 `#231` diff：`check-stage67-enforcement.sh`、`devflow-integration-regression.sh`、`p4-gauntlet-gates.md`、example `7-review.md`／`4-spec.md`、`bad-dd-unresolved.md`、五份 `stage67-filled-tooth/*.md`。無新公開 HTTP 端點、無新表。

## Diff(merge-base = `ed594bf`..`c7e69ac` = `#231`,逐檔折疊)

完整位元：`git show c7e69ac`。13 檔 +179/−13。本 PR 只加審查文檔。

<details>
<summary>scripts/check-stage67-enforcement.sh +85/−2 — ST-filled + MIN_CHECKS 60→66</summary>

```
_filled_judge / _filled_claimed / 五份 fixture 對照
void-only 紅; rebind SHA≥7 或「本項 FAIL」綠; n-a／draft no-fire
同一入口; 無 check-already-synced.sh
```
</details>

<details>
<summary>scripts/fixtures/stage67-filled-tooth/{void-only,rebind-sha,item-fail,na-incoming,draft-unclaimed}.md +83</summary>

```
五份對照形狀對齊 Stage 3 / DD-1 結論塊
```
</details>

<details>
<summary>scripts/devflow-integration-regression.sh +3/−3 — 檔頭 + GUIDANCE</summary>

```
檔頭改「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」
ALREADY_SYNCED GUIDANCE 加「重綁 Final Fresh」或「本項 FAIL」
sys.exit(code) / 四 STATUS / 絕不動樹 未改
```
</details>

<details>
<summary>docs/dev/tools/devflow-integration-regression.sh +3/−3 — 散發 parity</summary>

```
與正本同一檔頭／GUIDANCE
```
</details>

<details>
<summary>manifests/p4-gauntlet-gates.md +1/−1 — 2c→2d 文檔化命令</summary>

```
「7-review 執行清單 2d 的文檔化命令」
```
</details>

<details>
<summary>example/contract-expiry-reminder/7-review.md +1/−1 與 .html +1/−1</summary>

```
Final Fresh 序號 2c → 2d
```
</details>

<details>
<summary>example/contract-expiry-reminder/4-spec.md +2/−2 + spec-gate fixture +1/−1</summary>

```
2c gauntlet → 2d gauntlet; C5 負向針仍紅
```
</details>

Banned 路徑不在 `#231`：無 `docs/dev/STATUS.md`、無 plugin bump、無 `notes/dispatch-*`、無 `HISTORY.md`、無 `docs/dev/stage7-loop/`、無 `check-already-synced.sh`。

## Verdict

**PRE-REVIEW** —— Implementer C 獨立預審。**不是 G3 PASS。** Human 判定留給 owner。

| 門檻 | 證據 | 簽署 |
|---|---|---|
| 本次 S 全綠 | S-1.1～S-4.3／S-5.2／S-5.3 ✅；S-5.1 ⚠（Exit 未勾） | Agent C 預審；**非 Human** |
| 既有回歸綠 | T-1／T-2／T-3 Verify exit 0；四支 Final Fresh 入口綠 | 同上 |
| 現象證據逐 S 相符 | 上表；S-5.1 標 ⚠ 不是假裝相符 | 同上 |
| Evidence 契約 | 2d 當下 Source SHA=HEAD；gauntlet 在提交前對本檔跑（見附錄 A4） | 提交後須重綁再跑 |
| 無 🔴 | F-1／F-2 🟡；F-3 🟢 | Human 尚未接受 yellows |

重驗輪次:1（Implementer C PRE-REVIEW）。未進 REQUEST_CHANGES 迴圈。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 填檔牙讀字面，不重算 merge-base（4-spec Known limit ①） | 高（設計已知） | park：契約已列；人貼結論行 |
| 2 | 編輯器不能擋 Verdict 後改碼（Known limit ②） | 高（設計已知） | park：作廢 G3 契約；本 feat 不新造 hook |
| 3 | S-5.1 after-Exit 要 Human 勾 Exit + Source SHA 仍 = 當時 HEAD | 高（本 hop 未做） | **留給 Human G3**：勾 Exit 前重綁 SHA；HEAD 動了回 2c／2d |
| 4 | #231 無 6-notes；FORK 是審查 branch 切開 tip，不是 T-1 開工錨 | 中（流程） | park：F-2；後續實作步 0 當場記 |
| 5 | `MIN_CHECKS=66` vs 母版 79（F-1） | 中 | park 或另票讓 seed 帶 fixture |
| 6 | 本 PR 提交 7-review 後 HEAD ≠ 2d SHA，除非重綁 | 中 | 與 #3 同一條；禁把 stale SHA 當 S-5.1 ✅ |

## Exit Checklist(全勾才算 shipped)

- [ ] **Design Boundary finding 全數處置**：預審無未授權 Boundary 變更；F-1／F-2 🟡 **尚未** Human 接受或 park。無記錄的 🟡 = 未處置，**不得勾**。
- [ ] Quiz（不可逆／公開檢查契約）：題在附錄 A3；**Human 全對才准 merge**。Agent 不代答。
- [ ] (條件式)整合回歸已在 Final Fresh **之前**完成：預審兩次 `N_A_NO_INCOMING`、三 SHA 同 `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`（見 Verification Evidence）。**留給 Human 核對後勾**。Verdict 後不得再改程式碼。
- [ ] PR → main（draft 先開；禁直上 master）。STATUS 不進本 branch。
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`：n-a（本 repo 無對應 living 條；Human 確認）
- [ ] STATUS.md 已更新為 shipped（**合併後**由合併者做；本 hop 不改 STATUS）
- [ ] 7-review frontmatter status: shipped（本檔停 draft／PRE-REVIEW）
- [ ] 7-review.html 已產生（本 hop 會產；Human 核對動線五格後勾）
- [ ] feature branch 已刪 / worktree 已清（merge 後）

### Owner G3 出手清單

1. 抽驗 Coverage／現象任一列 `檔:行`。
2. 接受或 park F-1／F-2 🟡（寫 owner／理由／落點）。
3. 答 A3 Quiz。
4. 若 HEAD ≠ Source SHA → 重綁 2d，再填 Human verdict。
5. 不要在本 branch 改 `STATUS.md`。

## 附錄:本輪特有

### A1　讀取順序聲明(防錨定)

1. 4-spec / 5-tasks
2. `#231` diff 與 fixture／牙原始碼
3. 自建 Coverage Matrix + 親跑 Verify／現象
4. **2c 兩次**（`N_A_NO_INCOMING`）**之後**才 2d
5. 才 `review-unlock` 讀 thin 6-notes

與作者主張：#231 無 Self-Review。thin 6-notes 八問自承未知。無錨定衝突。

### A2　可證偽點(請挑戰)

1. `_filled_judge` 是否真的要「ALREADY_SYNCED **且** 已宣稱」才開火？（draft 見 `ALREADY_SYNCED` 必須仍 no-fire）
2. Required layers 全形 `／` 是否被 gauntlet 當單一 token？（本檔首層名與其全等）
3. S-5.3 命中是否混進「本 slug 要跳過 2c」的指令句？
4. `#231` 是否偷偷改了 `sys.exit(code)` 或 STATUS 名稱？

### A3　Quiz(給 approver；不可逆檢查契約)

1. 已宣稱的 `ALREADY_SYNCED` 只寫「證據不算數」，指定檢查應 exit 什麼？stderr 要有哪個字？
2. 恢復路徑哪兩條會讓同一支檢查變綠？SHA 最短幾顆 hex？
3. 為什麼 2c 必須在 2d 之前？Verdict 後再合 INTEGRATION_SHA，Source SHA 與 HEAD 會怎樣？
4. `N_A_NO_INCOMING` 與未勾 draft 為什麼不該預先紅？
5. 本 slug 過程檔能不能寫「跳過 2c」或「Exit 才合併」當執行指令？

### A4　環境與工具備註

- doctor：`COMPATIBLE`。`scripts/devflow-doctor.sh` 不存在；用 `hooks/devflow-doctor.sh`。
- 2c 用 `docs/dev/tools/devflow-integration-regression.sh --integration origin/main --fork-sha c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`。
- gauntlet 散發副本：`test -x docs/dev/tools/devflow-evidence-gauntlet.sh` 成立。
- 4-spec Required layers 用全形 `／` 串成單一 token；Evidence 表首列層名與此 token 全等。
- 本 hop 不跑 `status-update.sh`、不改 Active 表列。
- 2d gauntlet 實跑（提交前；`--source-sha` = 當時 HEAD = `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab`）:`✅ evidence gauntlet: 56 checks passed`。提交本檔後 HEAD 會離該 SHA，必須重綁再跑，不得把這次 56 當 after-Exit。

### A5　S-5.3 `rg` 命中分類

指令：`rg -n '跳過 2c|Exit 才合併' docs/dev/integration-before-verdict/`

| 檔 | 性質 |
|---|---|
| `1-discussion.md` | 討論假設「誰都可跳過」—— 痛點，不是本 slug 指令 |
| `2-decision.md`／`.html` | 拒 C／SC-5「無此宣告」—— 拒項 |
| `4-spec.md`／`.html` | R-5／S-5.3／Negative constraint「不得宣告」—— 禁令 |
| `5-tasks.md`／`.html` | Split Decisions 引用禁寫約束 —— 對照 |

無「請跳過 2c」或「Exit 才合併本 slug」的執行句。

### A6　S-5.2 對照原文

```
Verdict Source SHA=aaa1111
post-verdict INTEGRATION_SHA merge HEAD=bbb2222
both printed: aaa1111 bbb2222
differ: True
```

這是故意「Verdict 後才合」的文字 fixture，不是本 branch 真的合過。本 hop 2c 為 `N_A_NO_INCOMING`，沒有合碼。

### A7　與 thin 6-notes 對照裁斷

| 作者主張（thin） | 獨立複核 |
|---|---|
| #231 無 T Review PASS | ✅ 同意；不代簽 |
| FORK = 審查切開 tip | ✅ 同意；F-2 記下與 T-1 開工錨可能不同 |
| 八問未知 | ✅ 同意；本檔用親跑 Verify 補觀測，不把未知寫成有 |
| 無 L2 | ✅ 同意 |

### A8　2c 整合結論（欄位；非新 ## 節）

- STATUS: N_A_NO_INCOMING
- FORK / HEAD / INTEGRATION / REF: `c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab` / 同 / 同 / `refs/remotes/origin/main`
- 恢復: n-a（分岔後對方零新 commit）
- 二次重跑: STATUS 與三 SHA／REF 完全相同後才往 2d
