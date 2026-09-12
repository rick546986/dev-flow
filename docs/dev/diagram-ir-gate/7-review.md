---
feature: diagram-ir-gate
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: rick
reviewers: []
updated: 2026-09-12
---

# 7. 驗證 —— **不是 G3 PASS**

> 本檔是獨立 Implementer A 的 Stage 7 交接／機械審查正本。`verdict:` 留 `PRE-REVIEW`。
> Human G3 **空白** —— Agent 不寫 PASS／REQUEST_CHANGES／HOLD。全勾不算 PASS。
> 建議 Human G3 路徑:Verdict 門檻表 → 附錄 A1（2c `ALREADY_SYNCED` 重綁）→ Coverage 抽 S-3.2 或 S-1.1 → 再決定。
> STATUS.md Active 不在本 PR 改。產品碼已在 tip `#250`（`3b22f01`）。本 hop docs-only。

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

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-A-stage7`(獨立 fresh-context Cloud Agent A;**≠** Stage 6 #250 實作 owner `implementer-C`) |
| Human G3 | **空白**。本檔 `verdict: PRE-REVIEW`。owner=`rick`。`reviewers: []` |
| 讀取順序(可查) | ①`4-spec.md`(G2 PASS、21 S) ②`5-tasks.md`(T-1..T-6) ③`git show 3b22f01`(#250 產品 diff,32 檔 +1802/−30) ④測試碼／fixture(`scripts/test-diagir.sh` 六組、`scripts/fixtures/diagir/`、`diagir-lab.yaml`、`kind-parked.json`) ⑤親跑六組 Verify + 4-spec entry point + 步 2c 兩次 → **之後才** ⑥讀 6-notes(含 Self-Review;exec 未武裝,靠讀取順序) |
| 圍欄 | `hooks/devflow-exec.sh status` = 無執行旗標(守衛沉睡)。doctor:`COMPATIBLE`(契約 2.0.0,runtime 3.23.3,gauntlet 1.3.3)。完成條件是可查讀取順序,不是可宣稱身分 |
| 本輪性質 | 產品碼已在 tip `#250`。本 hop 只寫 7-review + twin。不改產品碼、不改 STATUS Active、不 bump plugin、不碰 #196／IBV。**不是 G3 PASS** |

## Coverage Matrix

自建(grep 4-spec S 清單 ↔ `scripts/test-diagir.sh` CASE 名／`檔:行`;**未先讀** 6-notes Self-Review)。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/test-diagir.sh:144-149` `S-1.1_parked_kind_keeps_last_good`;閘 `scripts/diagir.py:139-140`;信封 `scripts/fixtures/diagir/parked.json` | ✅ |
| S-1.2 | `scripts/test-diagir.sh:150-155`;閘 `scripts/diagir.py:141-142`;`scripts/fixtures/diagir/empty-title.json` | ✅ |
| S-1.3 | `scripts/test-diagir.sh:156-161`;閘 `scripts/diagir.py:143-147`;`scripts/fixtures/diagir/four-lines.json` | ✅ |
| S-1.4 | `scripts/test-diagir.sh:162-167`;閘 `scripts/diagir.py:183-185`;`scripts/fixtures/diagir/tree-as-vbox.json` | ✅ |
| S-1.5 | `scripts/test-diagir.sh:168-173`;閘 `scripts/diagir.py:168-171`;`scripts/fixtures/diagir/dir-short-why.json` | ✅ |
| S-1.6 | `scripts/test-diagir.sh:174-187`;收據 `scripts/diagir.py:74-88` | ✅ |
| S-2.1 | `scripts/test-diagir.sh:190-210`;`scripts/diagir.py:232-258`;`scripts/fixtures/diagir/lifecycle-envelope.json` | ✅ |
| S-2.2 | `scripts/test-diagir.sh:211-226`;原語 `scripts/devflow_atomic.py:13-22` | ✅ |
| S-2.3 | `scripts/test-diagir.sh:229-276`;`scripts/build-dir-tree.py:576-578`;`scripts/build-gate-twin.py:2351-2356`;`scripts/build-stage1-html.py:483-489`;`scripts/build-stage2-html.py:556`;`scripts/build-stage4-html.py:759` | ✅ |
| S-3.1 | `scripts/test-diagir.sh:279-303`;`notes/design/diagir-route.md:7-12` | ✅ |
| S-3.2 | `scripts/test-diagir.sh:304-309`;閘 `scripts/diagir.py:186-187`;`scripts/fixtures/diagir/stage1-as-lifecycle.json` | ✅ |
| S-3.3 | `scripts/test-diagir.sh:310-315`;`scripts/fixtures/diagir/dir-as-vbox.json` | ✅ |
| S-3.4 | `scripts/test-diagir.sh:316-328`;閘 `scripts/diagir.py:156-157`;`scripts/fixtures/diagir/missing-family.json` | ✅ |
| S-3.5 | `scripts/test-diagir.sh:329-373`;`python3 scripts/diagir.py route` `scripts/diagir.py:277-283` | ✅ |
| S-4.1 | `scripts/test-diagir.sh:376-401`;`scripts/fixtures/diagir-lab.yaml:1-30` | ✅ |
| S-4.2 | `scripts/test-diagir.sh:402-433`;三正信封 + `build-vbox-fig.py --fixture lifecycle` + `build-dir-tree.py --fixture good` | ✅ |
| S-4.3 | `scripts/test-diagir.sh:434-451`;`scripts/fixtures/vbox-fig/kind-parked.json` | ✅ |
| S-4.4 | `scripts/test-diagir.sh:452-458`;`scripts/fixtures/diagir-lab.yaml:8-12` | ✅ |
| S-4.5 | `scripts/test-diagir.sh:459-478`;`scripts/devflow-check.sh:132,135,236`;無 `scripts/check-diagir-lab.sh` | ✅ |
| S-5.1 | `scripts/test-diagir.sh:481-491`;S-2.1 綠交付 `rg` 四詞 | ✅ |
| S-5.2 | `scripts/test-diagir.sh:493-522`;`.claude-plugin/plugin.json:3` `version`=`3.23.3`;`git diff origin/main...HEAD` 空 | ✅ |
| 既有測試套件(回歸) | 4-spec entry point + 六組 `test-diagir.sh`(數字見 Verification Evidence) | ✅ |

**Verify 親跑**(5-tasks 原指令;2026-09-12;2c 兩次同座標之後、Fresh 綁 `3b22f01`):

```
CASE_COUNT validate=6; PASS:diagir validate 6/6; exit 0
CASE_COUNT deliver=2; PASS:diagir deliver 2/2; exit 0
CASE_COUNT wire=4; PASS:diagir wire 4/4; exit 0
CASE_COUNT route=5; PASS:diagir route 6/6; exit 0
CASE_COUNT lab=5; PASS:diagir lab 5/5; exit 0
CASE_COUNT static-scope=2; PASS:diagir static-scope 2/2; exit 0
PASS:diagir all 25/25; exit 0
```

## Verification Evidence

- Source SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
- Final Fresh Run ID: 2026-09-12T1815Z-impl-A-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md && bash scripts/check-vbox-fig.sh && bash scripts/check-dir-tree.sh && bash scripts/check-gate-twin.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0(gate-twin pin;`scripts/requirements-methodology-render.txt`); contract 2.0.0; runtime 3.23.3; git 2.43.0; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-vbox-fig／check-dir-tree／check-gate-twin | Final Fresh entry point(見上列四指令) | pass | 四層皆 exit 0:spec-gate 6/6;vbox-fig 16/16;dir-tree 81/81;gate-twin 222 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md` | pass | exit 0;6/6 形狀全過;21 條 S | |
| check-vbox-fig | `bash scripts/check-vbox-fig.sh` | pass | exit 0;16/16 | |
| check-dir-tree | `bash scripts/check-dir-tree.sh` | pass | exit 0;81/81 | |
| check-gate-twin | `bash scripts/check-gate-twin.sh` | pass | exit 0;222 項 | |
| test-diagir | `bash scripts/test-diagir.sh` | pass | exit 0;25/25(六組 CASE 6+2+4+5+5+2) | |
| Supply chain | | n-a | | Conditional:本 hop docs-only,未改產器寫檔、未加新 Python 依賴 |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

### 2c 整合結論

6-notes 步 0 `FORK_INTEGRATION_SHA: 25997871a86fce87a1b1f0658512d7f96e07dea3`。Fresh **之前**連跑兩次,STATUS／三 SHA／REF 完全相同:

- STATUS: ALREADY_SYNCED
- FORK / HEAD / INTEGRATION / REF: 25997871a86fce87a1b1f0658512d7f96e07dea3 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / refs/remotes/origin/main
- 兩次皆 exit 2(腳本對 ALREADY_SYNCED 的契約碼)
- 共同戰場:無 —— **本次輸出不當交集證據**(ALREADY_SYNCED 恢復路徑 ①)

恢復走路徑 ①,不是只寫「證據不算數」:重綁 Final Fresh。Source SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4(Fresh 開工 `git rev-parse HEAD`;#250 squash tip = origin/main)。未再合 INTEGRATION_SHA(合的會是自己)。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得在驗證失敗後覆寫目標(S-1.1～S-1.5) | test-diagir validate 五案 + 親跑 sha 不變 | pass |
| 不得只印 traceback 而無穩定碼(S-1.6) | validate S-1.6;stderr 兩行 FAIL、無 Traceback | pass |
| 不得留下半份新目標檔(S-2.2) | deliver S-2.2;tmp 長度 12、目標仍 last-good | pass |
| 不得未接閘就宣稱 wave-1 完成(S-2.3) | wire 4 CASE;`require_write` 六處;`cmp` tools 副本 | pass |
| 不得黑盒猜 family(S-3.4) | route missing-family;`DIAGIR_FAMILY`;無 auto／detect／已選 | pass |
| 不得只重放 lifecycle.json 當 Lab(S-4.4) | lab yaml 負向 `kind-parked.json` ≠ 正例 | pass |
| 不得另造 Proof Lab 牙語言(S-4.5) | 無 `check-diagir-lab.sh`;devflow-check 仍跑三支既有牙 | pass |
| 不得把 mermaid／動畫當預設(S-5.1) | 綠 SVG 四詞 0 命中;含 `</svg>` | pass |
| 不得碰 #196、不得 bump plugin(S-5.2) | plugin `3.23.3`;`origin/main...HEAD` 空;本 hop 檔清單 | pass |
| 不得收 Mermaid／Node／hosted／WYSIWYG／Q8／Q9 | #250 `--name-only` 無那些路徑;本 PR docs-only | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 hop 不是 dev-run 引擎案。欄位留空。Stage 6 亦標 `n-a-manual-impl-C`。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 閘 exit、stdout JSON、stderr、目標 sha256 | exit 1;`code`=`DIAGIR_KIND`;`target_replaced`=false;sha 仍 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc`;stderr `FAIL DIAGIR_KIND &#124; knob: 把 kind 改回允許值，或改走路由表上的正確家族` | ✅ |
| S-1.2 | exit、收據 `code`、目標 sha | exit 1;`DIAGIR_EMPTY`;sha 不變 | ✅ |
| S-1.3 | exit、收據 `code`、目標 sha | exit 1;`DIAGIR_LINES`;sha 不變 | ✅ |
| S-1.4 | exit、收據 `code`、目標 sha | exit 1;`DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-1.5 | exit、收據 `code`、目標 sha | exit 1;`DIAGIR_WHY`;sha 不變 | ✅ |
| S-1.6 | stdout 六鍵與 stderr 兩碼行 | 六鍵都在;`abort`=`DIAGIR_ABORT`;`delivered`/`target_replaced`=false;stderr 另有 `DIAGIR_ABORT` 旋鈕句;無 Traceback | ✅ |
| S-2.1 | exit、收據四欄、目標檔頭與 sha | exit 0;`ok`/delivered/target_replaced=true;`code`=null;len=1158;`&lt;svg`+`&lt;/svg>`;sha ≠ last-good(`053bc4df18d902ce9057ce91eb5e31bfe6d78d66128af29f83bbe5f76fc5a321`) | ✅ |
| S-2.2 | 兩路徑 sha／size | 目標 sha=last-good;tmp size=12 內容恰 `&lt;svg viewBox`;目標 ≠ tmp | ✅ |
| S-2.3 | 四檔(+兩支審頁)diff 與閘 import | `require_write` 在 dir-tree:576-578、gate-twin:2351、stage1:483、stage2:556、stage4:759;`cmp` tools 副本一致;vbox-fig 仍 stdout | ✅ |
| S-3.1 | 路由表列數與四欄 | `notes/design/diagir-route.md:7-12` 剛好五 id;四欄非空;契約指回已核檔 | ✅ |
| S-3.2 | exit、`code`、目標 sha | exit 1;`DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-3.3 | exit、`code`、目標 sha | exit 1;`DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-3.4 | 收據 `code` 與自動選列字樣 | `DIAGIR_FAMILY`;stdout+stderr 無 auto／detect／已選 | ✅ |
| S-3.5 | 路由表產器欄與五入口 | `ROUTE_ROWS 5`;五 builder 各一列;`stage1-now` 不指 vbox-fig;`dir-tree` 不指 vbox／twin | ✅ |
| S-4.1 | yaml 列數、path、`expect_code` | version 1;六 path;三家族各 1 正 1 負;三碼 KIND／FAMILY／WHY;`tooth_language: existing` | ✅ |
| S-4.2 | 三支牙 exit 與閘 pos 收據 | vbox `--fixture lifecycle` exit 0;dir-tree `--fixture good` exit 0;fig-long-label 檔在;三 pos 閘 `ok`=true | ✅ |
| S-4.3 | 三案 exit、`code`、目標 sha | kind-parked→KIND;tree-as-vbox→FAMILY;dir-short-why→WHY;三次後 sha 仍 last-good | ✅ |
| S-4.4 | 索引兩列 path | 負向 `kind-parked.json` ≠ `lifecycle.json`;有 `DIAGIR_KIND` | ✅ |
| S-4.5 | `devflow-check.sh` 仍呼叫三支牙 | 無 `check-diagir-lab.sh`;聚合器 L132／135／236 仍跑三支;無「取代」Lab 入口 | ✅ |
| S-5.1 | 目標檔 `rg` 與是否含 svg | mermaid／mermaid.js／`&lt;animate`／animateTransform 各 0;有 `&lt;svg` | ✅ |
| S-5.2 | plugin diff 與變更清單 | version `3.23.3`;`git diff origin/main...HEAD -- .claude-plugin/plugin.json` 空;本 hop 未列 #196／STATUS／IBV | ✅ |

## 截圖槽

本 feat 無產品前端;現象為 CLI／fixture／`rg`。截圖槽 N/A(無 `shots/` 定名檔 → 產檔器顯示佔位即可)。不准發明編輯 URL。不准新增一張只為了截圖。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／DIAGIR_* 收據／last-good sha
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 開工 agent | 壞 IR 不得換掉上一張可審圖 | `python3 scripts/diagir.py deliver parked.json --out target.svg` | 終端機看 DIAGIR_KIND 與旋鈕 | 目標停 last-good,直到下次綠交付 | ✅ 人看見碼就改 kind,不必 checkout 舊檔 |
| S-1.4 | 開工 agent | 不要把樹收成單盒 vbox | 同一閘、tree-as-vbox 信封 | 查 `notes/design/diagir-route.md` 後換入口 | last-good 留下 | ✅ `DIAGIR_FAMILY` |
| S-2.1 | 產檔器 | 通過後人打開完整新圖 | 綠 lifecycle `deliver` | 瀏覽器／編輯器開目標 | `replace` 同步結束 | ✅ 完整靜態 SVG、sha 變了 |
| S-2.2 | 產檔器 | 寫入中斷時審頁仍打得開舊圖 | 旁路寫 `&lt;svg viewBox` tmp、不 `replace` | 刪殘 tmp 後重跑 | 未 replace 視同 ABORT | ✅ 目標仍 last-good |
| S-3.2 | 開工 agent | 第 1 站三框不要畫成生命週期四格 | stage1-as-lifecycle 信封 | 改跑 `build-stage1-html.py --action` | last-good 留下 | ✅ `DIAGIR_FAMILY` |
| S-3.4 | 開工 agent | 先選家族,不要讓機器猜 | 無 `family` 鍵的 JSON | 打開路由表勾一列 | 不寫檔 | ✅ 拒猜 |
| S-4.3 | owner／審查人 | 負向紅了 last-good 還在 | 三負 `deliver` 同一目標 | 跑索引列 | 負向若蓋檔 → wave-1 未完成 | ✅ 三碼對、sha 不變 |
| S-5.1 | owner | wave-1 成功條件不是「會動」 | 打開 S-2.1 預設圖 | 瀏覽器直開、離線 | 看到動畫預設就打回 | ✅ 靜態 SVG、四詞 0 |
| S-1.2／S-1.3／S-1.5／S-1.6／S-2.3／S-3.1／S-3.3／S-3.5／S-4.1／S-4.2／S-4.4／S-4.5／S-5.2 | — | — | — | — | — | 不適用(4-spec Operational Context 標不適用或純字面／接線) |

六條人因檢查(技術過但人做不完／看得見沒決策權／等待標成完成／系統外丟追／中斷不能恢復／資訊過期或併寫):未命中。失敗路徑把決策權留給人(改 IR／換產器);系統外步驟就是重跑閘。

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 產器 → `diagir.require_write` → `atomic_write`。閘 `default_body` 可載 `build-vbox-fig.render_svg`(既有產器,契約允許)。無 event bus／全域狀態讓被禁模組反向改 STATUS。
2. **資料所有權被繞過寫入**:未命中 —— 驗證失敗不呼叫 `atomic_write`(`scripts/diagir.py:238-246`)。產器不再對目標 `Path.write_text`。
3. **相容性破壞包成新增**:未命中 —— 信封／`DIAGIR_*`／收據是新公開 API(spec 授權)。既有三支牙入口字面仍在。plugin version 未變。
4. **一致性邊界被拆解**:未命中 —— 原子寫仍是單次 tmp+`os.replace`(`scripts/devflow_atomic.py:13-22` ≡ inventory:30-37)。失敗零寫目標。
5. **宣告的 Test seam 未被使用**:未命中 —— 入口仍是 `python3 scripts/diagir.py deliver` 與六組 `test-diagir.sh`。S-2.2 按契約旁路寫 tmp、不呼叫 replace。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— ①`kind-parked.json` 已落地(契約說 Stage 6 才造;不是偷偷取消限制)。②仍無 OS hook 擋硬跑舊 `write_text`(S-2.3 用 diff)。③proto 仍非正式(`docs/dev/diagram-ir-gate/proto/diagir_gate.py` 未當 ship)。

無未經授權 Boundary 變更。無 🔴。無要 park 的 🟡 Boundary。

## Standards Axis

產品樹 = `git show 3b22f01`(#250)。本 PR vs `origin/main` = 本審查檔 + twin。

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟢 | `docs/dev/diagram-ir-gate/6-implementation-notes.md:29-106` | T Review Log 是 implementer-C self-check,不是獨立 T reviewer | 接受為 Stage 6 雲端單代理限制。獨立審查是本檔,不採信作者 PASS 當 G3 | 過程 |
| F-2 | 🟢 | `scripts/diagir.py:217-228` `default_body` | CLI 無 `body=` 時 dir-tree／stage1 吐占位 html,不是真產器頁 | 接受。S-2.1 契約只鎖綠生命週期 SVG;產器接線傳真實 `body` | S-2.1／S-2.3 |
| F-3 | 🟢 | `scripts/test-diagir.sh:495` `origin/main...HEAD` | S-5.2 測法從雙點收斂成三點(D-1 L1) | 接受。觀測欄寫「本 slug 各 hop 的 PR diff」;三點才不會把後來 STATUS 算進來 | S-5.2 |
| F-4 | 🟢 | `scripts/check-file-map.sh` EXPECTED=205;`MIN_HEREDOCS`=221 | 母版記帳超出 5-tasks Files(D-3／D-4 L1) | 接受。不註冊 `test-diagir.sh` 會讓 CI 自審假紅;不是第二套 Lab 牙 | S-4.5 |
| F-5 | 🟢 | `scripts/diagir.py:74-88` 失敗收據 | 六鍵之外多 `detail`／`target_unchanged`／`target_existed` | 接受。spec 寫「必含」不是「只能這些鍵」 | S-1.6 |

Dependency Direction／Boundary Leakage／Data Ownership／Interface Stability:未發現反向依賴、未漏出 Archify／mermaid 型別、非 owner 未直寫目標、公開檢查入口(`deliver`／`route`／三支既有牙)字面不變。無 🔴。無未授權 🟡 Boundary。

## Spec Axis

| R | 判定 | 出處 |
|---|---|---|
| R-1 失敗保住 last-good 並吐 DIAGIR_* | 符合 | S-1.1～S-1.5 親跑 exit≠0、碼對、sha=`8ed83a4d…22354dbc`;S-1.6 六鍵+ABORT+旋鈕、非 traceback |
| R-2 通過後才原子交付 | 符合 | S-2.1 整份新靜態 SVG;S-2.2 中斷只留截斷 tmp;S-2.3 五支寫檔+tools 副本走同一閘;vbox-fig 仍 stdout |
| R-3 五列查找路由表 | 符合 | S-3.1 五列四欄;S-3.2／S-3.3／S-3.4 `DIAGIR_FAMILY` 且不猜;S-3.5 `ROUTE_ROWS 5`、無第六列 |
| R-4 Proof Lab 薄索引 | 符合 | S-4.1 六列;S-4.2 三正綠;S-4.3 三負紅且不蓋檔;S-4.4 負向≠lifecycle.json;S-4.5 無第二套 Lab 牙 |
| R-5 預設靜態 SVG 且不收 NON-goal | 符合 | S-5.1 四詞 0;S-5.2 plugin `3.23.3`、#250 與本 hop 皆無 #196／IBV／STATUS／plugin version |
| M-1～M-3 | 符合 | 三處 `write_text` 改 `require_write`(dir-tree:576-578、gate-twin:2351、stage1:483) |
| Design Boundary | 符合 | 見 Design Integrity Check;D-1～D-4 皆 L1,無 L2、無未授權變更 |
| 6-notes Deviations | 如實 | D-1 三點 diff、D-2「取代」漢字、D-3 filemap 205、D-4 heredoc 221 —— 獨立複核成立,不是 L2。Self-Review 數字與本 hop 親跑相符(6／2／4／6／5／2;25/25;16;81;222)。作者 T PASS 不當 G3 |

## 變更架構圖

產品(#250,已在 tip;`git show 3b22f01` basename)與本 PR 審查密封:

```
[diagir.py]  deliver / route / validate / require_write
    |  fail -> receipt JSON + DIAGIR_* + DIAGIR_ABORT (no write)
    +--> [devflow_atomic.py]  tmp + os.replace
    +--> [build-vbox-fig.py]  stdout / render_svg (still no file write)

[build-dir-tree.py] --------require_write family=dir-tree----> [diagir.py]
[build-gate-twin.py] -------require_write family=behavior-flow--> [diagir.py]
    +==parity== [docs/dev/tools/build-gate-twin.py]
[build-stage1-html.py] -----require_write family=stage1-now----> [diagir.py]
[build-stage2-html.py] -----require_write family=stage2-arch---> [diagir.py]
[build-stage4-html.py] -----require_write family=vbox-lifecycle-> [diagir.py]

[notes/design/diagir-route.md]  five-row lookup
[scripts/fixtures/diagir-lab.yaml] --points--> vbox-fig / gate-twin / dir-tree fixtures
[scripts/fixtures/vbox-fig/kind-parked.json]
[scripts/test-diagir.sh]  validate/deliver/wire/route/lab/static-scope

#250 母版記帳(L1,不是新 R/S):
[devflow-check.sh]  hang test-diagir.sh next to three teeth
[guides/guide-dev-flow.html]  #filemap rows
[check-file-map.sh]  EXPECTED_MAPPED_FILES=205
[check-py-floor.sh]  MIN_HEREDOCS=221

本 hop 審查密封(docs-only,不是產品碼):
[7-review.md]   Source SHA=3b22f01 (#250 tip = Fresh HEAD)
[7-review.html] G3 twin
```

無新公開 HTTP 端點、無新表。改 Diff 必須改本圖。

## Diff(merge-base(main)..HEAD,逐檔折疊)

`merge-base(origin/main, HEAD)` 在 Fresh 時 = `3b22f01`(本 hop 尚未提交)。產品 #250 已在 main。本 companion PR 相對 main 只加本檔／twin。

<details>
<summary>產品 #250(已在 tip;審查對象,不是本 PR 新增)</summary>

32 files, +1802/−30。basename 見變更架構圖。入口仍是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。完整 hunk:`git show 3b22f01`。

</details>

<details>
<summary>docs/dev/diagram-ir-gate/6-implementation-notes.md + html — Stage 6 已在 tip</summary>

FORK_INTEGRATION_SHA: 25997871a86fce87a1b1f0658512d7f96e07dea3。有 Self-Review(implementer-C self-check)。本 hop 不改 6-notes。

</details>

<details>
<summary>docs/dev/diagram-ir-gate/7-review.md + 7-review.html — 本審查正本</summary>

本檔。`verdict: PRE-REVIEW`。Source SHA=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。Human G3 空白。

</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** Human G3 空白,留給 owner `rick`(頁尾「提交判定」)。Agent 不代填 PASS。

機械面(Implementer A 抽驗表;全勾也不算 PASS):

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 21/21 自建矩陣 ✅ | Coverage Matrix |
| 既有全綠 | entry point 四層 + 六組 test-diagir | 6/6;16/16;81/81;222;25/25 |
| 現象證據逐 S 相符 | 21/21 | 現象證據表 |
| Evidence 契約 | Fresh 綁 HEAD;`--review-file` 見附錄 A3 | Source SHA=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4` |
| 無 🔴 | 無 | Standards／Spec;F-1～F-5 皆 🟢 |
| 2c 在 Fresh 之前 | 是 | 先跑兩次 ALREADY_SYNCED(同座標),再 Fresh 重綁 |
| Human G3 | **空白** | 本檔 `verdict: PRE-REVIEW` |

建議 Human reviewer 路徑:適格人類 ≠ implementer-C、≠ 本檔作者 → 抽驗 S-1.1 或 S-3.2 的 `檔:行` → 看附錄 A1 重綁 SHA → 再填頁尾判定。

- G3 | 未寫 | 等待 Human。owner 自審若要走,必須另寫限制聲明且不得由本 Agent 代填 PASS

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 主機層不擋「跳過閘硬跑舊 write_text」(4-spec Known limit ②) | 中 | park;S-2.3 用 diff 咬接線。owner=方法論;追蹤=4-spec Design Constraints |
| 2 | 編輯器不能擋 Verdict 後改碼,也不能讓「含 Source SHA 的 commit」等於該 commit 自己的 SHA(與 IBV Known limit ② 同形) | 中 | park。本檔 Exit 寫成當時 `3b22f01`=HEAD 已證;本 docs commit 落地後 HEAD 會再漂。合法恢復=再重綁 Final Fresh,不得再合產品碼。owner=方法論 |
| 3 | throwaway `proto/diagir_gate.py` 非正式(4-spec Known limit ③) | 低 | park;G3 現象以 `scripts/diagir.py` 為準(本 hop 已這樣做) |
| 4 | Stage 6 T Review 是 implementer-C self-check,不是獨立 T reviewer | 低 | 接受;見 F-1。本檔才是獨立 Stage 7 |
| 5 | 本檔 `verdict: PRE-REVIEW`;全勾也不算 shipped | — | 留給 Human G3。STATUS.md Active 不在本 PR 改 |
| 6 | 2c 對 6-notes FORK(`2599787`)印 ALREADY_SYNCED(產品已在 tip) | 低 | 已走恢復路徑 ① 重綁 Fresh。不當交集證據 |
| 7 | CLI `default_body` 對 dir-tree／stage1 是占位(F-2) | 低 | 接受;產器接線傳真實 body。後刀若要 CLI 真畫,另 slug |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**(applicable):無未授權 Boundary 變更。F-1～F-5 皆 🟢 且未改 R/S／所有權／公開 Interface。無須 L2、無須 park Boundary
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配,fast 免):本 PR 是審查密封,產品碼已在 #250;留給 Human G3(題見附錄 A5)
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 結論(含三個 SHA 與 canonical ref)在「2c 整合結論」。ALREADY_SYNCED 走重綁。Source SHA 在 Exit 文件寫成當下等於 HEAD。Verdict 之後不得再改程式碼
- [ ] PR → develop(feature branch,禁直上 master;本專案整合分支是 `main`)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`(本 repo 無 living spec;`n-a`)
- [ ] STATUS.md 已更新為 shipped(整合分支上、PR 合併後由合併者做,不塞進本 branch)
- [ ] 7-review frontmatter status: shipped;上游 artifact 可保留 approved —— **本檔停 draft／PRE-REVIEW,Human G3 才改**
- [x] 7-review.html 已產生(G3 twin;`scripts/build-gate-twin.py`;審頁另跑 `scripts/build-stage7-html.py --action` → `/tmp/diagir-stage7-shots.html`,不覆寫 twin)
- [ ] feature branch 已刪 / worktree 已清

## 附錄:本輪特有

### A1　2c ALREADY_SYNCED 與 Fresh 重綁(S-5.1 形)

產品 #250 已 squash 進 `origin/main`。用 6-notes FORK `2599787` 跑整合腳本,HEAD 已是 INTEGRATION,故印 `ALREADY_SYNCED`(exit 2)。兩次座標相同:

```
STATUS: ALREADY_SYNCED
FORK_INTEGRATION_SHA: 25997871a86fce87a1b1f0658512d7f96e07dea3
FEATURE_HEAD: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
INTEGRATION_SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
INTEGRATION_REF: refs/remotes/origin/main
共同戰場:無
```

恢復路徑 ①:重綁 Final Fresh。Source SHA = `git rev-parse HEAD` =

```
3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
```

本檔 Verification Evidence `Source SHA:` 同一字串。這不是「commit 含自己的 SHA」(做不到)。本 docs commit 落地後 HEAD 會再漂 —— Known Limits ②;合法恢復=再重綁,不是再合產品碼。

### A2　作者對照(N4)

先自建矩陣與親跑,才讀 6-notes Self-Review。裁斷:

- 作者六組數字與本 hop 獨立重跑相符,沒有「作者綠、審查紅」。
- T Review Log 的 PASS 是 self-check(F-1),不當獨立 T 審查、不當 G3。
- D-1～D-4 如實,皆 L1:三點 diff／「取代」漢字／filemap 205／heredoc 221。獨立看 diff 後接受,不升 L2。
- Decisions(`require_write` API、gate-twin 固定合法 payload、last-good sha 鎖定、vbox render、ellipsis why 地板 4)與 diff 對得上,未改 R/S。
- 6-notes `status: in-review`、owner=`implementer-C` ≠ 本檔 reviewer。本 hop 不改 6-notes。

### A3　Fresh／gauntlet 指令

```
test -x docs/dev/tools/devflow-evidence-gauntlet.sh
bash docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/diagram-ir-gate/7-review.md \
  --source-sha $(git rev-parse HEAD) --review-file \
  --require-layer check-spec-gate \
  --require-layer check-vbox-fig \
  --require-layer check-dir-tree \
  --require-layer check-gate-twin
```

Fresh 實跑當時 HEAD=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`(工作樹可有未提交的本檔):

```
✅ evidence gauntlet: 65 checks passed — docs/dev/diagram-ir-gate/7-review.md
```

S-5.1 同時:`test Source SHA = git rev-parse HEAD` → `S-5.1-ok`。
Profile Required 是一條全形 `／` 字串,Evidence 表第一列 Layer 必須與該字串全等,否則 E7 把四層當成一層缺席。

### A4　S-1.1 抽驗原文(給第 5 步)

`python3 scripts/diagir.py deliver scripts/fixtures/diagir/parked.json --out $TARGET` 在 last-good 目標上:

```
exit=1
code=DIAGIR_KIND
target_replaced=false
before=after=8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc
stderr:
FAIL DIAGIR_KIND | knob: 把 kind 改回允許值，或改走路由表上的正確家族
FAIL DIAGIR_ABORT | knob: last-good 仍在；先修 IR 再重跑
```

對得上 `scripts/diagir.py:139-140`(kind 不在 `b`／`hl`／`wn` → `DIAGIR_KIND`)與 `scripts/test-diagir.sh:144-149`。

### A5　Quiz(選配;Human G3 用,本檔不代答)

1. wave-1 正式入口是哪一條命令?proto 能不能當 ship?
2. 驗證失敗時目標檔應發生什麼?收據最少哪六個鍵?
3. 為什麼 S-5.2 要用三點 `origin/main...HEAD` 而不是雙點?
4. 2c 印 `ALREADY_SYNCED` 時,合法下一步是重綁 Fresh 還是只寫「證據不算數」?
5. 本 slug 為什麼不能 bump plugin、不能改 #196 檔?
