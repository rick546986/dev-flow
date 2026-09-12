---
feature: diagram-ir-gate
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-C-stage7
reviewers: []
updated: 2026-09-12
---

# 7. 驗證 —— **不是 G3 PASS**

> 本檔是 implementer-C 獨立 Stage 7 審查包。`verdict:` 留 `PRE-REVIEW`。
> Human 判定才是 PASS／REQUEST_CHANGES／HOLD。全勾不算 PASS。不發明 G3 PASS。
> 建議下一棒:適格人類 reviewer → 另一個 fresh-context reviewer Agent（≠ #250 實作 session）→ owner 自審(有記錄)為最後手段。

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
> 建議抽驗:`Coverage Matrix` 中位列 **S-3.3**(twin 決定論抽樣) → `scripts/test-diagir.sh:310` + `scripts/fixtures/diagir/dir-as-vbox.json:4`。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-C-stage7`(獨立 fresh-context Cloud Agent;`bc-e842c9ff`)。**≠** Stage 6 #250 實作 session `bc-5ab0653d`。產品 owner 欄仍是 `rick`。 |
| Human G3 | **未寫入**。本檔不得把機械綠寫成 G3 PASS。 |
| 讀取順序(可查) | ①`4-spec.md`(G2 `approved`／`verdict` PASS、21 S) ②`5-tasks.md`(T-1～T-6) ③`git show 3b22f01`(#250 產品 diff) ④`scripts/test-diagir.sh` + 三支既有牙 ⑤親跑 test-diagir 25/25 + check-vbox-fig 16/16 + check-dir-tree 81/81 + check-gate-twin 222 + 逐 S CLI 現象 + 2c 兩次座標相同 → **之後才** ⑥`review-unlock` 讀 6-notes |
| 圍欄 | `hooks/devflow-exec.sh review diagram-ir-gate` 武裝後再 `review-unlock`。doctor:`COMPATIBLE`(契約 2.0.0,runtime 3.23.3,gauntlet 1.3.3) |
| 本輪性質 | 產品碼已在 tip `#250`=`3b22f01`。本 hop **只寫** `7-review.md` + twin。不改產品碼、不改 `STATUS.md` 表列、不代填 Human G3。 |
| 可信／打折 | 機械數字(exit／checks／sha256)可信。F 分級與「沒想到的事」由下一棒 Human 裁量。本 session 與 #250 同標 impl-C,只保證讀取順序與獨立重跑,不保證四眼身分被 hook 擋住。 |

## Coverage Matrix

自建(grep 4-spec 21 條 S ↔ `scripts/test-diagir.sh` CASE／`檔:行`;**未先讀** 6-notes Self-Review)。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/test-diagir.sh:144-149` `S-1.1_parked_kind_keeps_last_good`;閘 `scripts/diagir.py:139-140`;信封 `scripts/fixtures/diagir/parked.json:6` | ✅ |
| S-1.2 | `scripts/test-diagir.sh:150-155`;閘 `scripts/diagir.py:141-142`;信封 `scripts/fixtures/diagir/empty-title.json` | ✅ |
| S-1.3 | `scripts/test-diagir.sh:156-161`;閘 `scripts/diagir.py:143-147`;信封 `scripts/fixtures/diagir/four-lines.json` | ✅ |
| S-1.4 | `scripts/test-diagir.sh:162-167`;閘 `scripts/diagir.py:183-185` + `looks_like_tree` `97-102`;信封 `scripts/fixtures/diagir/tree-as-vbox.json:4-5` (`kind`=`tree-ascii` 且 text 含 `&#124;---`) | ✅ |
| S-1.5 | `scripts/test-diagir.sh:168-173`;閘 `scripts/diagir.py:161-171`;信封 `scripts/fixtures/diagir/dir-short-why.json` | ✅ |
| S-1.6 | `scripts/test-diagir.sh:174-187`(吃 S-1.1 那次 stdout／stderr);收據形 `scripts/diagir.py:74-88` | ✅ |
| S-2.1 | `scripts/test-diagir.sh:190-210`;`deliver` `scripts/diagir.py:232-258`;綠 SVG `scripts/diagir.py:205-214` | ✅ |
| S-2.2 | `scripts/test-diagir.sh:211-226`(旁路寫 `TARGET.tmp`);原語 `scripts/devflow_atomic.py:13-22` | ✅ |
| S-2.3 | `scripts/test-diagir.sh:229-276` 四 CASE;接線 `scripts/build-dir-tree.py:576-578`、`scripts/build-gate-twin.py:2351-2356`、`scripts/build-stage1-html.py:483-489`、`scripts/build-stage2-html.py:556`、`scripts/build-stage4-html.py:759`;tools 副本逐字相同 | ✅ |
| S-3.1 | `scripts/test-diagir.sh:279-303`;表 `notes/design/diagir-route.md:7-12` 五列四欄 | ✅ |
| S-3.2 | `scripts/test-diagir.sh:304-309`;閘 `scripts/diagir.py:186-187`;信封 `scripts/fixtures/diagir/stage1-as-lifecycle.json` | ✅ |
| S-3.3 | `scripts/test-diagir.sh:310-315`;信封 `scripts/fixtures/diagir/dir-as-vbox.json:4-8` | ✅ |
| S-3.4 | `scripts/test-diagir.sh:316-328`;閘 `scripts/diagir.py:156-157`;信封 `scripts/fixtures/diagir/missing-family.json` | ✅ |
| S-3.5 | `scripts/test-diagir.sh:329-373`;`route` CLI `scripts/diagir.py:277-283` 印 `ROUTE_ROWS 5` | ✅ |
| S-4.1 | `scripts/test-diagir.sh:376-401`;索引 `scripts/fixtures/diagir-lab.yaml:1-30` 六列三家族 | ✅ |
| S-4.2 | `scripts/test-diagir.sh:402-433`(閘三正 + 兩支產器 fixture);**本 hop Fresh 另跑** `check-vbox-fig.sh`／`check-dir-tree.sh`／`check-gate-twin.sh` | ✅ |
| S-4.3 | `scripts/test-diagir.sh:434-451` 三負 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY` 且 sha 不變 | ✅ |
| S-4.4 | `scripts/test-diagir.sh:452-458`;負向 path `scripts/fixtures/vbox-fig/kind-parked.json` ≠ `lifecycle.json` | ✅ |
| S-4.5 | `scripts/test-diagir.sh:459-478`;無 `scripts/check-diagir-lab.sh`;`scripts/devflow-check.sh:132` 仍跑三支牙、`:137` 只掛 `test-diagir` 不當 Lab 牙 | ✅ |
| S-5.1 | `scripts/test-diagir.sh:481-492`;綠檔禁 mermaid／`<animate` | ✅ |
| S-5.2 | `scripts/test-diagir.sh:493-522` 三點 `origin/main...HEAD` + untracked;plugin `3.23.3` 空 diff | ✅ |
| 既有測試套件(回歸) | 4-spec entry point 四層 + `scripts/test-diagir.sh` 25/25 + `scripts/check-file-map.sh` scanned=205 | ✅ |

**Verify 親跑**(5-tasks 原指令;2026-09-12;2c 兩次 `N_A_NO_INCOMING` 之後、Fresh 綁 `3b22f01`):

```
=== CASE 24 列(validate 6 / deliver 2 / wire 4 / route 5 / lab 5 / static-scope 2)
checks=25
✅ PASS:diagir all 25/25
```

## Verification Evidence

- Source SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
- Final Fresh Run ID: 2026-09-12T1814Z-impl-C-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md && bash scripts/check-vbox-fig.sh && bash scripts/check-dir-tree.sh && bash scripts/check-gate-twin.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0(gate-twin pin;`scripts/requirements-methodology-render.txt`); contract 2.0.0; runtime 3.23.3; git 2.43.0; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-vbox-fig／check-dir-tree／check-gate-twin | Final Fresh entry point(見上列四指令) | pass | 四層皆 exit 0:spec-gate 6/6;vbox-fig 16/16;dir-tree 81/81;gate-twin 222 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md` | pass | exit 0;6/6 形狀全過;21 條 S | |
| check-vbox-fig | `bash scripts/check-vbox-fig.sh` | pass | exit 0;16/16 | |
| check-dir-tree | `bash scripts/check-dir-tree.sh` | pass | exit 0;81/81 | |
| check-gate-twin | `bash scripts/check-gate-twin.sh` | pass | exit 0;222 項全過 | |
| test-diagir(本 feat 牙;非 Profile Required) | `bash scripts/test-diagir.sh -v` | pass | exit 0;checks=25;25/25 | |
| Supply chain | `bash scripts/check-file-map.sh`(產器寫檔已改,Conditional) | pass | exit 0;scanned=205;table_rows=215 | |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

本環境 doctor 初檢 `markdown-it-py 未裝`;Fresh 前已 `pip install 'markdown-it-py==4.0.0'`。這是 runner 相依,不是產品碼。

### 2c 整合結論

本 Stage 7 分支從 #250 tip 切開。產品已在 `origin/main`。Fresh **之前**連跑兩次,STATUS／三 SHA／ref 完全相同。不合併(N_A)。

- STATUS: N_A_NO_INCOMING
- FORK / HEAD / INTEGRATION / REF: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / refs/remotes/origin/main
- 恢復: n-a(分岔後對方零新 commit)

```
結論:STATUS=N_A_NO_INCOMING FORK=3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 HEAD=3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 INTEGRATION=3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

第二次座標逐字相同。Source SHA 綁產品樹 `3b22f01`。本 docs commit 落地後 HEAD 會漂 —— Known Limits ②。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得在驗證失敗後覆寫目標(S-1.1～S-1.5) | test-diagir validate + 現象 CLI sha 不變 | pass |
| 不得只印 traceback 而無穩定碼(S-1.6) | test-diagir S-1.6;stderr 兩行 FAIL + 無 Traceback | pass |
| 不得留下半份新目標檔(S-2.2) | test-diagir S-2.2;目標 sha=last-good、tmp 長度 12 | pass |
| 不得未接閘就宣稱 wave-1 完成(S-2.3) | test-diagir wire 4 CASE;五支產器 `require_write` | pass |
| 不得黑盒猜 family(S-3.4) | missing-family → `DIAGIR_FAMILY`;無 auto／detect／已選 | pass |
| 不得只重放 lifecycle.json 當 Lab(S-4.4) | kind-parked.json ≠ lifecycle.json 且有 `DIAGIR_KIND` | pass |
| 不得另造 Proof Lab 牙語言(S-4.5) | 無 `check-diagir-lab.sh`;三支既有牙仍在 | pass |
| 不得把 mermaid／動畫當預設(S-5.1) | 綠 SVG 四詞零命中且有 `</svg>` | pass |
| 不得碰 #196、不得 bump plugin(S-5.2) | plugin 3.23.3;三點 diff 空;無 STATUS／IBV／b8 路徑 | pass |
| 不得收 Mermaid／Node／hosted／WYSIWYG／Q8／Q9 | `scripts/diagir.py:11` 禁 import;route 無第六列 hosted | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 hop 不是 dev-run 引擎案。欄位留空。#250 為手動實作。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

last-good sha256 實測 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc`(與 S-1.1 鎖定值相同)。入口一律 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | exit、stdout JSON、stderr、目標 sha | rc=1;`code`=`DIAGIR_KIND`;`target_replaced`=false;sha 不變;stderr `FAIL DIAGIR_KIND &#124; knob: 把 kind 改回允許值，或改走路由表上的正確家族` + `DIAGIR_ABORT` | ✅ |
| S-1.2 | exit、收據 `code`、目標 sha | rc=1;`DIAGIR_EMPTY`;sha 不變;旋鈕「補上非空標題／至少一步」 | ✅ |
| S-1.3 | exit、收據 `code`、目標 sha | rc=1;`DIAGIR_LINES`;sha 不變;旋鈕「收成 1–3 行、刪空行」 | ✅ |
| S-1.4 | exit、收據 `code`、目標 sha | rc=1;`DIAGIR_FAMILY`;detail=`tree-as-vbox`;sha 不變 | ✅ |
| S-1.5 | exit、收據 `code`、目標 sha | rc=1;`DIAGIR_WHY`;detail=`short-or-missing-why:src/`;sha 不變 | ✅ |
| S-1.6 | stdout 六鍵 + stderr 兩碼行 | 六鍵都在;`abort`=`DIAGIR_ABORT`;無 Traceback;旋鈕句在 stderr(見 S-1.1 輸出) | ✅ |
| S-2.1 | exit、收據四欄、檔頭與 sha | rc=0;`ok`/`delivered`/`target_replaced`=true;`code`=null;含 `<svg` 與 `</svg>`;len=1158;sha ≠ last-good;無 mermaid | ✅ |
| S-2.2 | 兩路徑 sha／size | 目標 sha 仍 last-good;tmp 恰 `<svg viewBox`(size 12);目標 ≠ tmp | ✅ |
| S-2.3 | 四檔 + 兩支呼叫端 diff／import | 五處 `require_write`;`pathlib.Path(path).write_text`／`out_local.write_text`／`dest.write_text` 字面不在產品覆寫;tools 副本 `cmp` 相同 | ✅ |
| S-3.1 | 路由表列數與四欄 | `diagir-route.md:7-12` 五 id;契約欄指回四份已核短冊 | ✅ |
| S-3.2 | exit、`code`、目標 sha | rc=1;`DIAGIR_FAMILY`;detail=`stage1-as-lifecycle`;sha 不變 | ✅ |
| S-3.3 | exit、`code`、目標 sha | rc=1;`DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-3.4 | 收據 `code` + 無已選／auto／detect | rc=1;`DIAGIR_FAMILY`;detail=`missing-or-unknown-family`;三詞皆無 | ✅ |
| S-3.5 | 路由表產器欄與五入口 | `ROUTE_ROWS 5`;五 builder 字面各一列;無 hosted;stage1-now 不指 vbox | ✅ |
| S-4.1 | yaml 列數、path、`expect_code` | version 1;六 path;三家族各正負;`tooth_language: existing`;三碼齊 | ✅ |
| S-4.2 | 三支牙 exit + 閘 pos | Fresh:`check-vbox-fig` 16/16、`check-dir-tree` 81/81、`check-gate-twin` 222;閘三正 `ok`=true | ✅ |
| S-4.3 | 三案 exit、`code`、目標 sha | kind-parked→`DIAGIR_KIND`;tree-as-vbox→`DIAGIR_FAMILY`;dir-short-why→`DIAGIR_WHY`;三次 sha 不變 | ✅ |
| S-4.4 | 索引兩列 path | 負向 `kind-parked.json` ≠ `lifecycle.json` 且有 `DIAGIR_KIND` | ✅ |
| S-4.5 | `devflow-check.sh` 仍呼叫三支牙 | 無 `check-diagir-lab.sh`;`:132` 三牙、`:137` 只加 `test-diagir` | ✅ |
| S-5.1 | 目標檔 rg 四詞 + `<svg` | 四詞零命中;`</svg>` 在;靜態 `viewBox="0 0 280 302"` | ✅ |
| S-5.2 | plugin diff + 變更清單 | version `3.23.3`;`git diff origin/main...HEAD -- .claude-plugin/plugin.json` 空;本 hop 三點名單空(產品已在 tip) | ✅ |

原始 CLI 全文見附錄 A3。

## 截圖槽

本 feat 無產品前端;現象為 CLI／sha／牙 exit。截圖槽 N/A(無 `shots/` 定名檔 → 產檔器顯示佔位即可)。不准發明編輯 URL。不准新增一張只為了截圖。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／收據 JSON／目標 sha256
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 開工 agent | 壞 IR 不得換掉上一張可審圖 | `diagir.py deliver` parked 信封 | 終端機看碼與旋鈕;不要 `git checkout` 舊圖 | 目標停在 last-good 直到下次綠交付 | ✅ 人看見 `DIAGIR_KIND` + last-good 仍在 |
| S-1.4 | 開工 agent | 不要把樹收成單盒 vbox | 同一閘、tree-as-vbox 信封 | 查 `diagir-route.md` 後換入口 | last-good 留下 | ✅ `DIAGIR_FAMILY` |
| S-2.1 | 產檔器 | 通過後人打開完整新圖 | 綠 lifecycle `deliver` | 瀏覽器直開目標 SVG | `replace` 同步結束 | ✅ 完整靜態 SVG,len=1158 |
| S-2.2 | 產檔器 | 中斷時審頁仍打得開舊圖 | 旁路寫 `.tmp` 且不 `replace` | 刪殘 tmp 後重跑綠 IR | 未 replace 視同 ABORT | ✅ 目標仍 last-good |
| S-3.2 | 開工 agent | 第 1 站三框不要畫成生命週期 | stage1-as-lifecycle 信封 | 改跑 `build-stage1-html.py --action` | last-good 留下 | ✅ `DIAGIR_FAMILY` |
| S-3.4 | 開工 agent | 先選家族,不要讓機器猜 | 無 `family` 鍵的 JSON | 打開路由表勾一列 | 不寫檔 | ✅ 拒猜 |
| S-4.3 | owner／審查人 | 負向紅了 last-good 還在 | Lab 三負 `deliver` | 跑索引列 | 負向若蓋檔 → wave-1 未完成 | ✅ 三碼對且 sha 不變 |
| S-5.1 | owner | wave-1 成功條件不是「會動」 | 打開 S-2.1 產出 | 瀏覽器直開、離線 | 看到動畫預設就打回 | ✅ 無 mermaid／animate |
| S-1.2／S-1.3／S-1.5／S-1.6／S-2.3／S-3.1／S-3.3／S-3.5／S-4.1／S-4.2／S-4.4／S-4.5／S-5.2 | — | — | — | — | — | 不適用(4-spec Operational Context 標不適用或純字面／接線) |

六條人因檢查:技術上能完成工作;失敗碼把決策權交回人(改 kind／換入口／補 family);未把等待標成完成(`delivered` 失敗為 false);無系統外不可追蹤動作;中斷路徑是刪 tmp 重跑;資訊(旋鈕句)未過期。未發現「看得到但沒有決策權」。

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 閘 `scripts/diagir.py` 擁有判定;產器只 `import diagir` 後 `require_write`。無 event bus／共用 util 讓產器反向驅動碼表。`diagir.py:11` 禁 Archify／mermaid／Node。
2. **資料所有權被繞過寫入**:未命中 —— 產品覆寫改走 `require_write` → `deliver` → 通過後才 `atomic_write`(`diagir.py:232-250`)。`devflow_atomic.py` 不做驗證。S-2.3 牙咬掉舊 `write_text` 字面。
3. **相容性破壞包成新增**:未命中 —— 收據六鍵鎖定;多出來的 `detail`／`target_unchanged`／`target_existed` 是附加欄,六鍵仍在(S-1.6)。五 family id 未改名。
4. **一致性邊界被拆解**:未命中 —— 驗證失敗零寫目標;成功才一次 `os.replace`。S-2.2 未 replace 時目標全舊。
5. **宣告的 Test seam 未被使用**:部分觀察、不升 🟡 —— 契約 seam 是 `python3 scripts/diagir.py deliver` 與三支既有牙。`test-diagir.sh` S-4.2 對 gate-twin 正例只查 `fig-long-label` 檔在、對 vbox／dir-tree 跑產器 `--fixture`,不是直接呼叫 `check-*.sh`。本 hop Fresh **有**跑三支牙,補上契約觀測。見 F-3／Known Limits ④。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— ①`kind-parked.json` 已落地(S-4.3 不再靠 Stage 3 同形信封;限制①解除見 Known Limits)。②主機仍不擋跳過閘的舊 `write_text`(S-2.3 仍用 diff 咬)。③現象入口是 `scripts/diagir.py`,不是 proto。

無未經授權 Boundary 變更。無 🔴。無要 park 的 🟡 Boundary。

## Standards Axis

產品樹 = `git show 3b22f01`(#250)。本 PR vs `origin/main` = 本審查檔 + twin。

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟢 | `scripts/build-gate-twin.py:2343-2356` | twin 寫檔走 `require_write`,但 payload 是固定兩步 `behavior-flow`,不是頁面正文。閘驗的是罐頭信封,不是 html 內容。#191 樹仍能寫出。 | 接受為接線,不是內容閘。抽驗:`cmp` 正本＝tools 副本。記入 Known Limits ③ | S-2.3／M-2 |
| F-2 | 🟢 | `scripts/test-diagir.sh:211-226` | S-2.2 是旁路寫 `.tmp`,不是在 `atomic_write` 裡注入崩潰。與 4-spec GIVEN「旁路寫入且不呼叫 `os.replace`」逐字相符。 | 接受。不要把「沒有真的 kill -9」當成紅 | S-2.2 |
| F-3 | 🟢 | `scripts/test-diagir.sh:402-433` | S-4.2 牙內未直接跑三支 `check-*.sh`。 | 本 hop Fresh 已跑 16/16、81/81、222。抽驗用那三個數字,不要只信 CASE 標籤 | S-4.2／T-5 |
| F-4 | 🟢 | `scripts/diagir.py:74-88` 對 `232-246` | 失敗收據多 `detail`／`target_unchanged`／`target_existed`。六鍵仍在。 | 接受為 additive。勿當新公開契約 | S-1.6 |
| F-5 | 🟢 | `scripts/check-file-map.sh:114`、`scripts/devflow-check.sh:137`、`scripts/check-py-floor.sh`、`scripts/test-architecture-guards.sh` | 這幾檔不在 5-tasks Files 聯集。#250 為掛 `test-diagir`、地圖 205、`MIN_HEREDOCS` 221。R/S 未改。 | L1。接受。抽驗 scanned=205、無 `check-diagir-lab.sh` | S-4.5／S-5.2 |
| F-6 | 🟢 | Diff Budget 4-spec 估 ≤10 檔;#250 32 檔 | 超支是停下訊號,多數是 `scripts/fixtures/diagir/*`。 | 不是 L2。接受 | 過程 |
| F-7 | 🟢 | `scripts/diagir.py:222-228` | CLI 無 `body=` 時 dir-tree／stage1 寫 stub html。產器路徑傳真實 body。 | 接受。G3 現象以產器／lifecycle 為準 | S-2.1 |

Dependency Direction／Boundary Leakage／Data Ownership／Interface Stability:未發現反向依賴、未漏出內部型別、非 owner 未直寫目標、公開入口字面仍是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。無 🔴。無未授權 🟡 Boundary。

## Spec Axis

| R | 判定 | 出處 |
|---|---|---|
| R-1 失敗保住 last-good 並吐 DIAGIR_* | 符合 | S-1.1～S-1.5 五碼 + sha 不變;S-1.6 六鍵 + ABORT + Q6 旋鈕;正式入口不是 proto |
| R-2 通過後才原子交付 | 符合 | S-2.1 整份靜態 SVG;S-2.2 旁路 tmp;S-2.3 五支覆寫經閘。M-1～M-3 舊 `write_text` 行已改 `require_write` |
| R-3 五列查找路由表 | 符合 | S-3.1 五列四欄;S-3.2／S-3.3／S-3.4 `DIAGIR_FAMILY` 且不猜;S-3.5 五入口一一對上、無第六列 |
| R-4 Proof Lab 薄索引 | 符合 | S-4.1 六列;S-4.2 Fresh 三牙綠 + 閘三正;S-4.3 三負不蓋檔;S-4.4 負向 ≠ lifecycle;S-4.5 無第二套 Lab 牙 |
| R-5 預設靜態直式 SVG 且不收 NON-goal | 符合 | S-5.1 四詞零命中;S-5.2 plugin 3.23.3、三點空、無 #196／IBV／STATUS |
| M-1～M-3 | 符合 | dir-tree／gate-twin／stage1 產品覆寫改 `require_write` |
| Design Boundary | 符合 | 見 Design Integrity Check;無 L2、無未授權變更 |
| 6-notes Deviations | 如實 L1 | D-1 三點 diff(S-5.2);D-2 S-4.5 不禁「取代」漢字;D-3／D-4 母版記帳。無 L2。見附錄 A4 |

## 變更架構圖

產品(#250,已在 tip;`git show 3b22f01` basename)與本 PR 審查密封:

```
[scripts/diagir.py]  validate + deliver + route + require_write
    |-- DIAGIR_* / 六鍵收據
    +--> [scripts/devflow_atomic.py]  tmp + os.replace
    +--> [notes/design/diagir-route.md]  五列查找
    +--> [scripts/fixtures/diagir-lab.yaml]  六列索引
    +--> [scripts/fixtures/vbox-fig/kind-parked.json]
    +--> [scripts/fixtures/diagir/*.json] + last-good.svg

[scripts/build-dir-tree.py] ----require_write----\
[scripts/build-gate-twin.py] ----------------------> [diagir.require_write]
[docs/dev/tools/build-gate-twin.py]  (parity copy) /
[scripts/build-stage1-html.py] ---------------------/
[scripts/build-stage2-html.py] ---------------------/
[scripts/build-stage4-html.py] ---------------------/
[scripts/build-vbox-fig.py]  仍只寫 stdout

[scripts/test-diagir.sh]  六組 25 checks
[scripts/devflow-check.sh]  methodology 仍跑三支舊牙 + test-diagir

本 hop(docs-only,不是產品碼):
[7-review.md]   Source SHA=3b22f01 (#250 tip)
[7-review.html] G3 twin
```

無新公開 HTTP 端點、無新表。改 Diff 必須改本圖。

## Diff(merge-base(main)..HEAD,逐檔折疊)

`merge-base(origin/main, HEAD)` 在寫本檔時 = `3b22f01`。產品 #250 已在 main。本 PR 相對 main 只加審查密封。

<details>
<summary>產品 #250(已在 tip;審查對象,不是本 PR 新增)</summary>

32 files,+1802/−30。basename 見變更架構圖。入口仍是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。完整 hunk:`git show 3b22f01`。

</details>

<details>
<summary>docs/dev/diagram-ir-gate/7-review.md + 7-review.html — 本審查正本</summary>

本檔。`verdict: PRE-REVIEW`。Source SHA 維持 Fresh 產品樹 `3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。不是 G3 PASS。

</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** Human 尚未判定。

機械面(本 hop 獨立重跑,不新造 R/S):

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 21/21 自建矩陣 ✅ | Coverage Matrix;每列有 `檔:行` |
| 既有全綠 | entry point 四層 + test-diagir 25/25 | 6/6;16/16;81/81;222;25/25 |
| 現象證據逐 S 相符 | 21/21 | 現象證據表;附錄 A3 |
| Evidence 契約 | Fresh 綁產品 HEAD `3b22f01`;`--review-file` 見附錄 A5 | Source SHA=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`(不追本 docs commit) |
| 無 🔴 | 無 | Standards／Spec;F-1～F-7 皆 🟢 |
| 2c 在 Fresh 之前 | 是 | 兩次 `N_A_NO_INCOMING`,座標相同,未合併 |
| Human G3 | **未寫入** | 本檔禁止發明 PASS |

建議 Human:Verdict 門檻表 → 抽驗 S-3.3 `test-diagir.sh:310` → Fresh 三牙數字 → Known Limits ②／③ → 再決定。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 主機層不擋「跳過閘硬跑舊 write_text」(4-spec Known limit ②) | 中 | park。S-2.3 仍用 diff 咬接線,不是 OS hook。owner=方法論;追蹤=4-spec Design Constraints |
| 2 | 含 Source SHA 的 docs commit 不能等於該 commit 自己的 SHA | 中 | park。本檔 Source SHA 綁 Fresh 產品樹 `3b22f01`。本 hop commit 落地後 HEAD 會漂。合法恢復=再重綁 Final Fresh,不得再合產品碼 |
| 3 | gate-twin `require_write` 驗的是固定兩步 payload,不是頁面正文(`build-gate-twin.py:2343-2356`) | 低 | 接受為接線。#191 樹仍 WARNING+`<pre>`。不要把 twin html 品質當成閘契約 |
| 4 | `test-diagir.sh` S-4.2 不直接呼叫三支 `check-*.sh` | 低 | 本 hop Fresh 已補跑。下一棒抽驗用 16/16、81/81、222,不要只信 CASE 名 |
| 5 | S-4.3 閘負向的 FAMILY 列用 `tree-as-vbox.json`,不是把 `fig-tree-ascii/` 目錄當信封(該 path 是牙 fixture,不是 deliver JSON) | 低 | 接受。碼仍是 `DIAGIR_FAMILY`。索引 path 給牙,閘用同碼信封 |
| 6 | S-2.2 是旁路寫 tmp,不是 `atomic_write` 中途崩潰 | 低 | 接受;與 4-spec GIVEN 相符 |
| 7 | ~~vbox-fig 正式負向檔本 hop 不造(4-spec Known limit ①)~~ | — | 已解除:`scripts/fixtures/vbox-fig/kind-parked.json` 已在 #250 |
| 8 | `proto/diagir_gate.py` 仍在樹裡(非正式通道) | 低 | 接受。G3 現象以 `scripts/diagir.py` 為準(本 hop 已遵守) |
| 9 | 本檔 `verdict: PRE-REVIEW`;全勾也不算 shipped | 中 | 留給 Human G3。owner=rick |
| 10 | #250 改了 file-map／py-floor／architecture-guards／devflow-check／guide-dev-flow.html,超出 5-tasks Files 聯集 | 低 | L1 已記 F-5。作者 D-3／D-4 如實。不要當 L2 |
| 11 | Stage 6 T Review Log 是 implementer-C self-check,不是獨立 T reviewer | 中 | 本 hop 用獨立 Fresh／現象表補四眼的一半。Human G3 仍要另眼 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**(applicable):無未授權 Boundary 變更。F-1～F-7 皆 🟢 且未改 R/S／所有權／公開 Interface。無須 L2。Known Limits ①／③ 已落本節
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配,fast 免):公開信封 + last-good。題在附錄 A6,留給 Human G3
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 兩次 `N_A_NO_INCOMING`(三 SHA 與 ref 在「2c 整合結論」)。Source SHA 綁產品樹 `3b22f01`。Verdict 之後不得再改程式碼
- [ ] PR → develop(feature branch,禁直上 master;本專案整合分支是 `main`)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`(本 repo 無 living spec;`n-a`)
- [ ] STATUS.md 已更新為 shipped(整合分支上、PR 合併後由合併者做,不塞進本 branch)
- [ ] 7-review frontmatter status: shipped;上游 artifact 可保留 approved(**本檔仍 draft／PRE-REVIEW**)
- [x] 7-review.html 已產生(G3 twin;`scripts/build-gate-twin.py`;審頁另跑 `scripts/build-stage7-html.py --action` → `/tmp/diagram-ir-gate-stage7-shots.html`,不覆寫 twin)
- [ ] feature branch 已刪 / worktree 已清

## 附錄:本輪特有

### A1　爭點

1. **本檔是不是 G3 PASS?** 不是。機械 21 S 綠 + 三牙綠 ≠ Human G3。`verdict:` 必須留 `PRE-REVIEW`。
2. **2c 該用哪一個 FORK?** 本審查分支從 #250 tip `3b22f01` 切開,兩次腳本都是 `N_A_NO_INCOMING`。6-notes 步 0 錨是 `25997871a86fce87a1b1f0658512d7f96e07dea3`(#244 Stage 5 tip,Stage 6 開工)。產品已合進 main;拿那個錨再跑會 `ALREADY_SYNCED`,不得當「沒有共同戰場」的證據。
3. **S-4.2 牙夠不夠?** CASE 本身偏弱(F-3)。本 hop 用三支既有牙 Fresh 補上。抽驗請看 16/16、81/81、222。
4. **twin 罐頭 payload 算不算繞閘?** 寫檔路徑經閘(S-2.3 要的)。內容不經閘(Known Limits ③)。不升 🟡 Boundary。

### A2　抽驗列(決定論)

Coverage Matrix 中位列 = S-3.3(與 twin 頂區「抽驗」格同一列)。

- 測試:`scripts/test-diagir.sh:310-315` `S-3.3_dir_as_vbox_family` → `DIAGIR_FAMILY`
- 信封:`scripts/fixtures/diagir/dir-as-vbox.json:4-8` `payload.kind`=`dir-tree`、`root.why` 長度 ≥ 12
- 閘:`scripts/diagir.py:183-185` `looks_like_tree` → `fail("DIAGIR_FAMILY", "tree-as-vbox")`(kind `dir-tree` 走 tree 分支)
- 現象:rc=1;`code`=`DIAGIR_FAMILY`;sha 不變

對得上才准信其餘 20 列。

### A3　現象 CLI 原始輸出(節錄)

```
last-good sha 8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc

S-1.1 rc=1 code=DIAGIR_KIND target_replaced=false sha_same=True
stderr:
FAIL DIAGIR_KIND | knob: 把 kind 改回允許值，或改走路由表上的正確家族
FAIL DIAGIR_ABORT | knob: last-good 仍在；先修 IR 再重跑

S-2.1 rc=0 ok=true delivered=true target_replaced=true len=1158
head: <svg viewBox="0 0 280 302" role="img" aria-label="模組生命週期"
banned mermaid/mermaid.js/<animate/animateTransform = all False

S-4.2 Fresh:
✅ PASS:vbox-fig 產圖器 + 牙 16/16
✅ PASS:dir-tree 產器 + 牙 81/81
✅ gate twin 產生器守衛:全過(222 項)

S-4.3 held last-good after KIND/FAMILY/WHY
S-5.2 plugin 3.23.3; origin/main...HEAD plugin diff empty
```

### A4　作者對照(N4;`review-unlock` 之後才讀)

6-notes owner=`implementer-C`。T Review Log 六則都寫「implementer-C self-check;獨立 T review 留給 PR／G3」。本 hop **不採信**那些 PASS 當四眼,只對矩陣與 Deviations。

| 作者主張 | 自建裁斷 |
|---|---|
| 21 S 各有含 S-id 的 CASE | 相符。矩陣每列有 `test-diagir.sh` 行號。本 hop 重跑 25/25 |
| last-good sha `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` | 相符。本 hop `sha256sum` 同值 |
| S-2.3 五支覆寫經 `require_write`;tools 副本一致 | 相符。本 hop `cmp` 相同;四 CASE 綠 |
| D-1 三點 `origin/main...HEAD` | 如實 L1。本 hop S-5.2 牙即此形。不是 L2 |
| D-2 S-4.5 不禁「取代」漢字 | 如實 L1。THEN 是「不當取代入口」 |
| D-3／D-4 filemap 205、MIN_HEREDOCS 221、`devflow-check` 掛 test-diagir | 如實 L1。對上 F-5。本 hop file-map scanned=205 |
| Decisions:`require_write` API;twin 固定兩步 payload;ellipsis why 地板 4 | 如實,不是 L2。twin 罐頭對上 F-1／Known Limits ③ |
| Self-Review ⑧ `check-stage1-now` 27／`check-stage2-card` 34／`check-stage4-rs` 50 | 檔名是縮寫。本 hop 獨立重跑 `check-stage1-now-contract.sh` 27/27、`check-stage2-card-contract.sh` 34/34、`check-stage4-rs-contract.sh` 50/50 |
| T-1..T-6 verdict PASS 且早於 commit | 作者自審。本 hop 不當四眼。獨立證據是本檔 Fresh／現象表 |
| FORK=`2599787` | 屬實(Stage 6 開工)。本 hop 2c 用審查分支叉點 `3b22f01`(見 A1) |

作者矩陣沒有多報或漏報 S。沒有「看起來 L1、其實動 R/S」的 Deviation。

### A5　Fresh／gauntlet 指令

```
test -x docs/dev/tools/devflow-evidence-gauntlet.sh
bash docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/diagram-ir-gate/7-review.md \
  --source-sha 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 --review-file \
  --require-layer check-spec-gate \
  --require-layer check-vbox-fig \
  --require-layer check-dir-tree \
  --require-layer check-gate-twin
```

Fresh 當時 HEAD=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`:

```
✅ evidence gauntlet: 67 checks passed — docs/dev/diagram-ir-gate/7-review.md
```

Profile Required 是一條全形 `／` 字串,Evidence 表第一列 Layer 必須與該字串全等。

### A6　Quiz(留給 Human;不可逆公開信封)

1. 餵 `kind=parked` 的 vbox-lifecycle 信封時,目標檔與 stderr 各應看到什麼?
2. 為什麼 `build-dir-tree.py`／`build-gate-twin.py`／`build-stage1-html.py` 必須改呼叫同一閘,vbox-fig 卻可以繼續只寫 stdout?
3. 本 slug 為什麼不准新增 `scripts/check-diagir-lab.sh`?
4. 失敗收據一定要有哪六個鍵?少了 `DIAGIR_ABORT` 算不算過?
5. S-5.2 為什麼用三點 `origin/main...HEAD` 而不是雙點 `origin/main`?

全對才准把 `verdict:` 從 PRE-REVIEW 改成 Human PASS,且必須由人類寫入。
