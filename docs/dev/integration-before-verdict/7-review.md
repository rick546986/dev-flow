---
feature: integration-before-verdict
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-a-ibv-stage7
updated: 2026-09-12
---

# 7. 驗證 —— **不是 G3 PASS**

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
> Implementer A 自審交接:`verdict: PRE-REVIEW`。**Human G3 才是 PASS／REQUEST_CHANGES／HOLD**。
> 建議 reviewer 路徑:適格人類(owner `rick`)親開 gate twin → 抽驗一列 → 才寫頂欄 `verdict:`。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| Author A | `implementer-a-ibv-stage7`(fresh-context Cloud Agent A;**≠** Stage 6 Implementer B / `#231`) |
| Human G3 | 仍留給 owner `rick`;本檔**不代填** PASS／shipped |
| 讀取順序(可查) | ①`4-spec.md`(G2 approved) ②`5-tasks.md` ③diff／測試(`check-stage67-enforcement.sh` ST-filled、五份 `stage67-filled-tooth/`、整合腳本 GUIDANCE、example／manifest／fixture) ④親跑 T-1／T-2／T-3 Verify + 現象 + 2c + Fresh → **之後才** ⑤讀薄檔 `6-implementation-notes.md`(無 Self-Review;只含 FORK + Verify 重跑 + Files) |
| 圍欄 | 未武裝 `devflow-exec.sh review`(本 hop 只寫 docs)。doctor:`COMPATIBLE`(契約 2.0.0;runtime 3.23.3;gauntlet 1.3.3) |
| 本輪性質 | Stage 7 證據包;`verdict: PRE-REVIEW`;`status: draft`。**不是 G3 PASS**。不准 sibling `7-review-*.md`／`7-self-review.md` |

## Coverage Matrix

自建(grep 測試／fixture／活路徑 ↔ 4-spec S 清單;**未先讀** Self-Review——6-notes 沒有該節)。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/fixtures/stage67-filled-tooth/void-only.md` + `_filled_judge` `scripts/check-stage67-enforcement.sh:353-366` | ✅ `ST-filled: void-only fail:void-only` |
| S-1.2 | `rebind-sha.md` 同入口 | ✅ `pass:rebind-sha:def4567890abc` |
| S-1.3 | `item-fail.md` 同入口 | ✅ `pass:item-FAIL` |
| S-1.4 | GUIDANCE `scripts/devflow-integration-regression.sh:202-207` 與散發副本 | ✅ T-2-ok(含「重綁」與「FAIL」) |
| S-2.1 | `na-incoming.md` | ✅ `no-fire:N_A_NO_INCOMING` |
| S-2.2 | `draft-unclaimed.md` | ✅ `no-fire:draft` |
| S-3.1 | `rg` example `contract-expiry-reminder/` | ✅ 0 行;`7-review.md:24` 已寫 2d Fresh |
| S-3.2 | manifest L52 + 兩支腳本檔頭 L2 | ✅ 舊針 0;`2d 的文檔化命令`;檔頭「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」 |
| S-3.3 | `bad-dd-unresolved.md:229` + `check-spec-gate.sh` | ✅ 無「2c gauntlet」;exit 1(C5) |
| S-3.4 | 活路徑聯合 `rg` | ✅ 0 行 |
| S-4.1 | `_templates/7-review.md` 頂註偏移 | ✅ `S-4.1-ok`(integ 在 Fresh 前) |
| S-4.2 | 三支既有牙 | ✅ stage67 79/79;guard 36;gauntlet tests 68/68 |
| S-4.3 | 腳本 STATUS／exit 碼／「絕不動樹」 | ✅ T-2-ok;exit 仍 0／10／11／2 |
| S-5.1 | Fresh 當下 `git rev-parse HEAD` vs Source SHA | ✅ 兩字串=`57b9770f73bade592c904b96f512beaa1a4e99aa`(Exit 未宣稱 ship) |
| S-5.2 | 文字對照(未真做錯誤序) | ✅ 附錄 A2:`aaa1111` ≠ `bbb2222` |
| S-5.3 | `rg` 本 slug 過程檔 | ✅ 命中皆拒項／約束;零執行指令 |
| 既有測試套件(回歸) | Fresh entry point(下節) | ✅ exit 0 |

**Verify 親跑**(5-tasks 原文;Fresh 後 HEAD=`57b9770f73bade592c904b96f512beaa1a4e99aa`):

T-1:`ST-filled count=5`;五列如上;三支牙綠;`S-4.1-ok`;`T1_VERIFY_EXIT:0`。

T-2:`T-2-ok`;`T2_VERIFY_EXIT:0`。

T-3:負向 fixture C5 紅(exit 1);活路徑 `rg` 0;`T3_VERIFY_EXIT:0`。

## Verification Evidence

- Source SHA: 57b9770f73bade592c904b96f512beaa1a4e99aa
- Final Fresh Run ID: 2026-09-12T1611Z-impl-a-r1
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md && bash scripts/check-stage67-enforcement.sh && bash scripts/check-integration-regression-guard.sh && bash scripts/test-evidence-gauntlet.sh`
- Toolchain: python3.12.3; gauntlet 1.3.3; contract 2.0.0; runtime 3.23.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-stage67-enforcement／check-integration-regression-guard／test-evidence-gauntlet | Fresh entry point(上列四指令) | pass | exit 0;spec-gate 6/6;stage67 79/79;guard 36;gauntlet tests 68/68 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/integration-before-verdict/4-spec.md` | pass | exit 0;6/6;16 條 S | |
| check-stage67-enforcement | `bash scripts/check-stage67-enforcement.sh` | pass | exit 0;79 項;ST-filled 5 列 | |
| check-integration-regression-guard | `bash scripts/check-integration-regression-guard.sh` | pass | exit 0;36 項 | |
| test-evidence-gauntlet | `bash scripts/test-evidence-gauntlet.sh` | pass | exit 0;68/68 | |
| Supply chain | `rg -n` 活路徑聯集(S-3.4) | pass | 0 行 | |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Out of Scope |

**2c 在 2d 之前**(結論行原文):

```
結論:STATUS=SYNC_REQUIRED_NO_OVERLAP FORK=c7e69acb5f5cd070ef0ad8d6da8fda12ddd472ab HEAD=b98c894342e22c8e924965f8189b3248d999a19c INTEGRATION=0294f8f4d39fb6d8858a62191fd82773dee30e96(refs/remotes/origin/main)—— 仍要合併 INTEGRATION_SHA + 跑全套測試(沒有共同戰場不代表不會壞)
```

第二次重跑(動手合併前)STATUS／三 SHA／REF 完全相同。已合併印出的 `INTEGRATION_SHA`=`0294f8f4d39fb6d8858a62191fd82773dee30e96`(#235 只動 `STATUS.md`;共同戰場:無)。合併後 Fresh Source SHA = 當下 HEAD = `57b9770f73bade592c904b96f512beaa1a4e99aa`。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得只寫「證據不算數／輸出不算數」就讓已宣稱 ALREADY_SYNCED 過關(S-1.1) | ST-filled void-only | pass |
| 不得誤殺 N_A_NO_INCOMING 或未勾 draft(S-2.1／S-2.2) | na-incoming／draft-unclaimed | pass |
| 不得重編號 2c、不得拆既有模板順序牙(S-4.1／S-4.2) | S-4.1-ok + 三支牙 | pass |
| 不得改整合腳本 STATUS／exit 演算法(S-4.3) | T-2-ok;「絕不動樹」+ exit 0／10／11／2 | pass |
| 不得改 HISTORY／dispatch／stage7-loop 當時句(S-3.4、OC-2) | `#231` 檔名清單無那些路徑 | pass |
| 不得在本 slug 過程檔寫成執行指令的禁句(S-5.3) | 過程檔 `rg`;命中皆拒項 | pass |
| 不得碰 #196／diagram-ir-gate／九條缺口／本 hop bump plugin | 本 PR 檔名=6-notes + 7-review;2c 只合已在 main 的 STATUS hop | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

Stage 6 為 Implementer B 雲端手動(`#231`)。本 Stage 7 為獨立 Agent A 審查,無 dev-run ledger。本節留白。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

Reviewer 親自實跑。不相符則 ❌。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 指定檢查 exit≠0 且含 void-only | stderr `ST-filled: void-only fail:void-only`;整支仍 exit 0(對照組紅、家族綠) | ✅ |
| S-1.2 | exit 0 且輸出含 ≥7 hex | `ST-filled: rebind-sha pass:rebind-sha:def4567890abc` | ✅ |
| S-1.3 | exit 0 且含 item-FAIL | `ST-filled: item-fail pass:item-FAIL` | ✅ |
| S-1.4 | 兩檔 GUIDANCE 含重綁與 FAIL | T-2-ok;正本 L206-207「重綁 Final Fresh」+「寫本項 FAIL」 | ✅ |
| S-2.1 | no-fire + N_A_NO_INCOMING | `ST-filled: na-incoming no-fire:N_A_NO_INCOMING` | ✅ |
| S-2.2 | no-fire + draft | `ST-filled: draft-unclaimed no-fire:draft` | ✅ |
| S-3.1 | example 兩針零命中 | `rg` 空;`example/.../7-review.md:24`「執行清單 2d 的 Final Fresh」 | ✅ |
| S-3.2 | 三檔舊針零;檔頭改口 | `rg` 空;腳本 L2「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」;manifest L52「2d 的文檔化命令」 | ✅ |
| S-3.3 | fixture 無 2c gauntlet;check-spec-gate exit 1 | `rg` 0;`⛔ G2 spec gate:5/6` C5 | ✅ |
| S-3.4 | 活路徑聯合 `rg` 零 | 輸出空 | ✅ |
| S-4.1 | 頂註「整合回歸」偏移 <「Final Fresh Run」 | `S-4.1-ok` | ✅ |
| S-4.2 | 三支 exit 0 | 79／36／68 全綠 | ✅ |
| S-4.3 | 四碼 + 絕不動樹 | T-2-ok;檔內仍 `sys.exit(code)` | ✅ |
| S-5.1 | Source SHA vs `git rev-parse HEAD` | Fresh 當下兩者=`57b9770f73bade592c904b96f512beaa1a4e99aa` | ✅ |
| S-5.2 | 對照兩 SHA 都印且不同 | 附錄 A2;`aaa1111` ≠ `bbb2222`;未真做錯誤序 | ✅ |
| S-5.3 | 過程檔 `rg`;執行指令零 | 命中在 1／2／4／5 拒項與約束句 | ✅ |

## 截圖槽

本 feat 無產品前端;現象為 CLI／fixture／`rg`。截圖槽 N/A(無 `shots/` 定名檔 → 產檔器顯示佔位即可)。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／ST-filled 列
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | Stage 7 reviewer | 勾 2c 時不能靠作廢句過關 | 跑 `check-stage67-enforcement.sh` | 終端機看 void-only 紅 | 補重綁 SHA 或本項 FAIL 後重跑;不要進 Verdict | ✅ 人看得到紅 |
| S-1.2 | Stage 7 reviewer | 恢復路徑走通才能進 2d | 寫「重綁 Final Fresh。Source SHA: hex≥7」 | 把 SHA 寫進恢復欄 | SHA 短於 7 → 當 void-only | ✅ fixture 綠 |
| S-1.3 | Stage 7 reviewer | 停在 2c,從乾淨座標重算 | 恢復欄寫「本項 FAIL」 | owner 看 7-review | 停到人重算 | ✅ fixture 綠 |
| S-2.1 | Stage 7 reviewer | 零新 commit 記 n-a 進 2d | 轉記腳本 STATUS | 無合併 | 後來對方有新 commit → 重跑腳本 | ✅ 本輪實際是 SYNC_REQUIRED(對方有 #235),不是誤殺 n-a |
| S-2.2 | Stage 7 reviewer | 未勾草稿不被提前紅 | 繼續填 draft | 不要先送 G3 | 勾了 2c 或 PASS 後改走 S-1.* | ✅ draft fixture no-fire |
| S-3.1 | 採用者 | 抄範例走 2c 整合 → 2d Fresh | 打開 example | 人打開檔 | rg 仍命中則同一 T 改到零 | ✅ 已改口 |
| S-5.1 | owner | Verdict 綁的樹就是出貨的樹 | 對帳 Source SHA 與 HEAD | Exit 只准文件／PR | 兩 SHA 不同就不得 ship | ✅ Fresh 當下相等;本檔不宣稱 ship |
| 其餘純內部 S | — | — | — | — | — | 不適用(4-spec 已標無人員交接) |

## Design Integrity Check(Design Boundary Contract = `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 牙住 `check-stage67-enforcement.sh:325-397`;不新開 `check-already-synced.sh`;整合腳本仍只算只判。
2. **資料所有權被繞過寫入**:未命中 —— 填檔判定屬牙;STATUS 名稱與三 SHA 屬整合腳本;7-review 恢復欄屬人填。
3. **相容性破壞包成新增**:未命中 —— exit 仍 0／10／11／2;`ALREADY_SYNCED` 仍 exit 2;只加 ST-filled 射程與 GUIDANCE 句。
4. **一致性邊界被拆解**:未命中 —— 牙只讀 fixture／填檔;腳本不動樹(`scripts/devflow-integration-regression.sh:9`)。
5. **宣告的 Test seam 未被使用**:未命中 —— 五份 Stage 3 同形 fixture;入口仍是 `bash scripts/check-stage67-enforcement.sh`。
6. **Known design limit 被悄悄「解決」**:未命中 —— 牙仍讀字面不重算 merge-base;無新 editor hook 擋 Verdict 後改碼。

## Standards Axis

無 🔴。無未授權 Boundary 變更。

- F-1 🟢 6-notes 為薄回填(Stage 6 `#231` 未交 6-notes)。本檔無 Self-Review,不與 7-review 競爭。影響:S2c fork-sha 可查。
- F-2 🟢 2c 實得 `SYNC_REQUIRED_NO_OVERLAP` 而非 brief 預測的 `N_A_NO_INCOMING`(tip 在分岔後多了 `#235` STATUS hop)。已合併印出的 INTEGRATION_SHA 再 Fresh。影響:S-5.1 形狀仍成立。
- F-3 🟢 `#231` MIN_CHECKS 地板 66(seed 67／母版 79)已在 Stage 6 說明;本 hop 不重開牙。

Design Boundary 四項(Standards 加查):
- **Dependency Direction**:符合 —— 牙 → 7-review 字串;腳本 → git;無第二套 CLI。
- **Boundary Leakage**:符合 —— 無 `check-already-synced.sh`。
- **Data Ownership**:符合 —— 恢復欄人寫;腳本不覆寫 7-review。
- **Interface Stability**:符合 —— STATUS 集合與 exit 碼不變;GUIDANCE additive。

## Spec Axis

- R-1 符合(S-1.1 紅;S-1.2／S-1.3 綠;S-1.4 GUIDANCE 有恢復下一步)。
- R-2 符合(S-2.1／S-2.2 no-fire)。
- R-3 符合(S-3.1～S-3.4 活教師舊針歸零;衍生 fixture 仍 C5 紅)。
- R-4 符合(2c 仍叫整合回歸且在 2d 前;三支牙綠;演算法只算只判)。
- R-5 符合形狀(S-5.1 Fresh SHA=HEAD;S-5.2 對照兩 SHA 不同且都印出;S-5.3 無執行指令)。**未宣稱 Exit／ship**——G3 仍留給人。
- 6-notes Deviations:無新 D-n;Files 聯集與 `#231` 對得上。
- Design Boundary 契約逐條:符合;Known design limit ①–③ 未被悄悄修掉。

## 變更架構圖

```text
[check-stage67 ST 組]
   既有模板順序牙
   + ST-filled 填檔牙 (_filled_judge)
        |
        v
   fixtures/stage67-filled-tooth/
     void-only / rebind-sha / item-fail
     na-incoming / draft-unclaimed
   入口仍是 bash scripts/check-stage67-enforcement.sh

[devflow-integration-regression.sh]     [docs/dev/tools/ 散發副本]
   檔頭:步 2c,Fresh 之前,不是 Exit 程序
   GUIDANCE:ALREADY_SYNCED → 重綁或本項 FAIL
   演算法／exit 0,10,11,2 不動樹

[manifests/p4-gauntlet-gates.md]  2c 文檔化命令 → 2d
[example/contract-expiry-reminder/]
   7-review + 4-spec  2c Fresh/gauntlet → 2d
[spec-gate-dd-subsection/bad-dd-unresolved.md]  同 T 改口,C5 仍紅

[本 slug Stage 7]
   2c 腳本 → (必要時合 INTEGRATION_SHA) → 2d Fresh
   7-review Source SHA = Fresh HEAD
```

圖上 basename 對得上 Diff:`check-stage67-enforcement.sh`、`devflow-integration-regression.sh`、`p4-gauntlet-gates.md`、`void-only.md` 等。無新公開 HTTP 端點、無新表。

## Diff(merge-base(origin/main)..產品 tip `#231`,逐檔折疊)

產品碼已在 `#231`(`c7e69ac`;+179/-13,13 檔)。本 PR 只加 Stage 7 文檔(+2c 合入已在 main 的 `#235` STATUS,未手改表列)。

<details>
<summary>scripts/check-stage67-enforcement.sh +85 — ST-filled _filled_judge</summary>

```
_filled_judge: ALREADY_SYNCED+已宣稱 → void-only 紅;Source SHA≥7 或「本項 FAIL」綠
N_A_NO_INCOMING / 未勾 draft → no-fire
同一入口;MIN_CHECKS=66(seed 地板)
```

</details>

<details>
<summary>scripts/fixtures/stage67-filled-tooth/* +83 — 五份對照</summary>

```
void-only.md / rebind-sha.md / item-fail.md / na-incoming.md / draft-unclaimed.md
形狀對齊 Stage 3;verdict PASS+已勾 2c 才開火(draft 未勾不開火)
```

</details>

<details>
<summary>scripts + docs/dev/tools/devflow-integration-regression.sh +6/-6 — 檔頭與 GUIDANCE</summary>

```
檔頭改「步 2c 整合回歸,Fresh 之前,不是 Exit 程序」
ALREADY_SYNCED GUIDANCE 加「重綁 Final Fresh」或「本項 FAIL」
sys.exit(code) 與 STATUS 名稱不動
```

</details>

<details>
<summary>example／manifest／spec-gate fixture — 2c→2d 改口</summary>

```
example 7-review.md:24 與 4-spec.md:223;manifest L52;bad-dd-unresolved.md:229
舊針歸零;負向 fixture 仍 C5 紅
```

</details>

<details>
<summary>docs/dev/integration-before-verdict/6-implementation-notes.md +96 — 薄座標檔</summary>

```
FORK_INTEGRATION_SHA 40 碼;T-1/T-2/T-3 Verify 重跑;Files touched
無 Self-Review
```

</details>

## Verdict

**PRE-REVIEW** —— 不是 G3 PASS。全勾不算 PASS。Human 判定才寫頂欄。

建議門檻表(給下一棒;本檔不代填 PASS):

| 門檻 | 證據 | 本檔 |
|---|---|---|
| 本次 S 全綠 | Coverage／現象 16 S | ✅ 形狀+實跑 |
| 既有全綠 | Fresh 四指令 | ✅ |
| 現象證據逐 S | 上表 | ✅ |
| Evidence 契約 | gauntlet --review-file(本檔落檔後跑) | 見附錄 A3 |
| 無 🔴 | Standards／Spec | ✅ 無 🔴 |
| 出貨樹=審過的樹 | 2c 在 2d 前;Source SHA=Fresh HEAD | ✅ 序正確;未 ship |

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 填檔牙讀字面,不重算 git merge-base(4-spec Known limit ①) | 低 | park;契約已寫 |
| 2 | 無 editor hook 擋 Verdict 後改碼(Known limit ②) | 中 | park;作廢 G3 仍靠 7-review 契約 |
| 3 | 本檔 `verdict: PRE-REVIEW`;Human 未簽 | 高 | owner 親審 twin 後才寫 PASS／REQUEST_CHANGES |
| 4 | 7-review 文檔再 commit 會讓 HEAD ≠ Fresh Source SHA | 中 | 預期:Exit 只准文件。Ship 前若要 S-5.1 字面相等,Human 在最後一棵送審樹上重綁 Fresh,或接受「Fresh SHA=合併後／寫檔前 HEAD」。本檔不宣稱 Exit 完成 |
| 5 | 2c 合入 `#235` STATUS 列(integration-before-verdict → 7-review)。本 hop **未手改** STATUS 表列 | 低 | 那是 2c 合併印出的 SHA,不是本 branch 寫入口 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**(契約 `applicable`):無未授權 Boundary 變更;六項 DIC 未命中。無未記錄 🟡。
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配):題目在附錄 A4;**等 Human 答完才准 merge**——本檔不代答、不勾
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 結論(含三個 SHA 與 canonical ref)貼在 Verification Evidence;Source SHA 於 Fresh 當下等於 HEAD。Verdict 之後不准再改程式碼。
- [ ] PR → develop(本 hop 開 **draft** PR → `main`;禁直上 master)。未 merge、不宣稱 shipped
- [x] 4-spec delta 已併入 `docs/specs/<domain>.md`:**n-a**(本 repo 無 `docs/specs/` living spec;4-spec Out of Scope 已寫)
- [ ] STATUS.md 已更新為 shipped(**禁止**本 branch 做;合併後由合併者在整合分支做)
- [ ] 7-review frontmatter status: shipped;**保持 draft／PRE-REVIEW**
- [x] 7-review.html 已產生(build-stage7-html + build-gate-twin;見附錄 A3)
- [ ] feature branch 已刪 / worktree 已清

## 附錄:本輪特有

### A1　本輪爭點

- 出貨樹是否等於核准樹:本 hop 證明 **2c 在 2d 前**(先合 `0294f8f` 再 Fresh `57b9770`)。
- G3 主權:Agent 只交 PRE-REVIEW。owner 預核中間站「一路到 stage7 我在審」**不**等於本檔可以寫 PASS。

### A2　S-5.2 Verdict-then-merge 對照(未執行錯誤序)

未把 INTEGRATION 留到 Verdict 之後才合。對照樣本(文字／fixture 形狀,與 Stage 3 `aaa1111`／`bbb2222` 同形):

| 欄 | 值 |
|---|---|
| 若先寫 Verdict Source SHA | `aaa1111` |
| 若再合 INTEGRATION_SHA 後 HEAD | `bbb2222` |
| 相等? | 否(`aaa1111` ≠ `bbb2222`);兩值都印出 |

本輪實做對照:2c 合併前 FEATURE_HEAD=`b98c894342e22c8e924965f8189b3248d999a19c`;合併 INTEGRATION=`0294f8f4d39fb6d8858a62191fd82773dee30e96` 後 Fresh HEAD=`57b9770f73bade592c904b96f512beaa1a4e99aa`。若把 Fresh／Verdict 綁在合併前的 `b98c894` 再合,兩 SHA 會不同 —— 那正是 S-5.2 要能指出的事。我們沒有那樣出貨。

### A3　產檔與 gauntlet

- `scripts/build-stage7-html.py --action docs/dev/integration-before-verdict/7-review.md`
- `scripts/build-gate-twin.py /workspace integration-before-verdict 7-review`(最後覆寫同檔,作 G3 五格卡)
- gauntlet:`docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/integration-before-verdict/7-review.md --source-sha $(git rev-parse HEAD) --review-file --require-layer check-spec-gate --require-layer check-stage67-enforcement --require-layer check-integration-regression-guard --require-layer test-evidence-gauntlet` → `✅ evidence gauntlet: 60 checks passed`(Fresh 樹 HEAD=`57b9770f73bade592c904b96f512beaa1a4e99aa`;本檔當時尚未 commit)

### A4　Quiz(給 Human;不代答)

1. 填檔牙的唯一入口檔名是什麼?為什麼不准新開 `check-already-synced.sh`?
2. `ALREADY_SYNCED` 已宣稱時,恢復欄哪兩句會綠?只寫「證據不算數」會怎樣?
3. 為什麼整合回歸必須在 Final Fresh 之前?Verdict 後再合 INTEGRATION_SHA 會破壞哪一條(S-id)?
4. 本輪 2c 印出的 STATUS 是什麼?合的是 branch 名還是哪一顆 SHA?
5. 本檔為什麼不能寫 `verdict: PASS`?

### A5　S-5.3 命中分類

`rg -n '跳過 2c&#124;Exit 才合併' docs/dev/integration-before-verdict/` 命中 1-discussion／2-decision／4-spec／5-tasks 的**拒項與約束**(含「禁寫」「無…流程宣告」)。7-review／6-notes 不把那些詞寫成「本 slug 要這樣做」的執行指令。
