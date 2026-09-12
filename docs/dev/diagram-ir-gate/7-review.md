---
feature: diagram-ir-gate
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: implementer-B-stage7
reviewers: []
updated: 2026-09-13
---

# 7. 驗證 —— **不是 G3 PASS**

> 本檔是獨立 Implementer B 的 Stage 7 審查包。`verdict:` 留 **PRE-REVIEW**。
> Agent 不得代填 Human G3 PASS／REQUEST_CHANGES／HOLD。全勾不算 PASS。
> 建議 Human G3 路徑:Verdict 門檻表 → Coverage 抽 S-1.1（`scripts/diagir.py:139-140` + 附錄 A3 收據）→ 現象表 S-2.1／S-4.3 → 再決定。
> STATUS.md Active 不在本 PR 改。

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
> 建議抽驗:Coverage `S-1.1` → `scripts/diagir.py:139-140`（`kind not in VBOX_KINDS`）+ 附錄 A3 parked 收據 `code=DIAGIR_KIND`、sha 仍 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc`。

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `implementer-B-stage7`(獨立 fresh-context Cloud Agent B;**≠** Stage 6 #250 實作 owner `implementer-C`) |
| Human G3 | **未填**。本檔 `verdict: PRE-REVIEW`。不得把機械全綠讀成 Human PASS |
| 讀取順序(可查) | ①`4-spec.md`(G2 PASS、21 S) ②`5-tasks.md`(T-1..T-6) ③`git show 3b22f01`(#250 產品 diff) ④測試碼／fixture（`scripts/test-diagir.sh` 六組 + `scripts/fixtures/diagir/` + `diagir-lab.yaml`） ⑤親跑六組 Verify + 4-spec entry point 四牙 + 步 2c（本 hop 兩次座標相同）→ **之後才** ⑥`review-unlock` 讀 6-notes（含 Self-Review／D-1..D-4） |
| 圍欄 | `hooks/devflow-exec.sh review diagram-ir-gate` 武裝後再 `review-unlock`。doctor:`COMPATIBLE`(契約 2.0.0,runtime 3.23.3,gauntlet 1.3.3) |
| 本輪性質 | 產品碼已在 tip `#250`=`3b22f01`。本 hop 只寫審查包,不改產品碼、不改 STATUS Active。**不是 G3 PASS** |

## Coverage Matrix

自建(grep 4-spec 21 條 S ↔ `scripts/test-diagir.sh` CASE 名／指定牙／`rg`;**未先讀** 6-notes Self-Review)。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `scripts/test-diagir.sh --group validate` CASE `S-1.1_parked_kind_keeps_last_good`;親跑 `python3 scripts/diagir.py deliver scripts/fixtures/diagir/parked.json --out TARGET` | ✅ |
| S-1.2 | 同組 CASE `S-1.2_empty_title_diagir_empty`;親跑 `empty-title.json` | ✅ |
| S-1.3 | 同組 CASE `S-1.3_four_lines_diagir_lines`;親跑 `four-lines.json` | ✅ |
| S-1.4 | 同組 CASE `S-1.4_tree_as_vbox_diagir_family`;親跑 `tree-as-vbox.json` | ✅ |
| S-1.5 | 同組 CASE `S-1.5_short_why_diagir_why`;親跑 `dir-short-why.json`(why 字面 `短`,對齊 `scripts/fixtures/dir-tree/missing-why/purpose.yaml`) | ✅ |
| S-1.6 | 同組 CASE `S-1.6_fail_emits_abort_and_receipt`;抽 S-1.1 stdout 六鍵 + stderr 兩碼行 | ✅ |
| S-2.1 | `scripts/test-diagir.sh --group deliver` CASE `S-2.1_pass_lifecycle_atomic_svg`;親跑 `lifecycle-envelope.json` | ✅ |
| S-2.2 | 同組 CASE `S-2.2_interrupt_keeps_last_good`;旁路寫 `TARGET.tmp`=`<svg viewBox`、不呼叫 `replace` | ✅ |
| S-2.3 | `--group wire` 4 CASE;`rg` 五支產器 `require_write`;tools 副本逐字=`scripts/build-gate-twin.py` | ✅ |
| S-3.1 | `--group route` CASE `S-3.1_route_table_five_rows`;`notes/design/diagir-route.md:7-12` 五列四欄 | ✅ |
| S-3.2 | 同組 CASE `S-3.2_stage1_as_lifecycle_family`;親跑 `stage1-as-lifecycle.json` | ✅ |
| S-3.3 | 同組 CASE `S-3.3_dir_as_vbox_family`;親跑 `dir-as-vbox.json` | ✅ |
| S-3.4 | 同組 CASE `S-3.4_missing_family_not_guessed`;親跑 `missing-family.json`;stdout+stderr 無 auto／detect／已選 | ✅ |
| S-3.5 | 同組 CASE `S-3.5_five_entries_map_five_rows`;`python3 scripts/diagir.py route` 印 `ROUTE_ROWS 5` | ✅ |
| S-4.1 | `--group lab` CASE `S-4.1_lab_index_six_rows`;`scripts/fixtures/diagir-lab.yaml` 六 path + 三 `expect_code` | ✅ |
| S-4.2 | 同組 CASE `S-4.2_three_pos_replay`;本 hop 另親跑三支牙全綠(見回歸列) | ✅ |
| S-4.3 | 同組 CASE `S-4.3_three_neg_hold_last_good`;親跑 `kind-parked.json` + tree-as-vbox + dir-short-why 三次後 sha 不變 | ✅ |
| S-4.4 | 同組 CASE `S-4.4_not_only_lifecycle_json`;負向 path=`kind-parked.json` ≠ `lifecycle.json` | ✅ |
| S-4.5 | 同組 CASE `S-4.5_no_second_lab_tooth`;無 `scripts/check-diagir-lab.sh`;`devflow-check.sh:132,135,236` 仍呼叫三支牙 | ✅ |
| S-5.1 | `--group static-scope` CASE `S-5.1_default_static_svg_no_mermaid`;S-2.1 產出 `rg` 四詞 0 | ✅ |
| S-5.2 | 同組 CASE `S-5.2_no_plugin_bump_no_196`;plugin `3.23.3`;`git diff origin/main...HEAD -- .claude-plugin/plugin.json` 空 | ✅ |
| 既有測試套件(回歸) | 4-spec entry point 四牙 + `test-diagir.sh` 全組 25/25 | ✅ |

**Verify 親跑**(5-tasks 原指令;2026-09-12;產品樹 `3b22f01`;2c 記 n-a 之後、Fresh 綁同一 HEAD):

```
validate CASE n=6; PASS 6/6
deliver  CASE n=2; PASS 2/2
wire     CASE n=4; PASS 4/4
route    CASE n=5; PASS 6/6
lab      CASE n=5; PASS 5/5
static-scope CASE n=2; PASS 2/2
all checks=25; PASS:diagir all 25/25
spec-gate 6/6; vbox-fig 16/16; dir-tree 81/81; gate-twin 222
```

## Verification Evidence

- Source SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
- Final Fresh Run ID: 2026-09-12T1815Z-impl-B-s7
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md && bash scripts/check-vbox-fig.sh && bash scripts/check-dir-tree.sh && bash scripts/check-gate-twin.sh`
- Toolchain: python3.12.3; markdown-it-py 4.0.0(gate-twin pin;`scripts/requirements-methodology-render.txt`;本機 Fresh 前補裝,見附錄 A3); contract 2.0.0; runtime 3.23.3; git 2.43.0; gauntlet 1.3.3

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-vbox-fig／check-dir-tree／check-gate-twin | Final Fresh entry point(見上列四指令) | pass | 四層皆 exit 0:spec-gate 6/6;vbox-fig 16/16;dir-tree 81/81;gate-twin 222 | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md` | pass | exit 0;6/6 形狀全過;21 條 S | |
| check-vbox-fig | `bash scripts/check-vbox-fig.sh` | pass | exit 0;16/16 | |
| check-dir-tree | `bash scripts/check-dir-tree.sh` | pass | exit 0;81/81 | |
| check-gate-twin | `bash scripts/check-gate-twin.sh` | pass | exit 0;222 項全過(初跑 exit 2 缺 markdown-it-py,補裝 4.0.0 後重跑;ENV 不計 IMPL) | |
| test-diagir validate | `bash scripts/test-diagir.sh --group validate` | pass | exit 0;CASE n=6;6/6 | |
| test-diagir deliver | `bash scripts/test-diagir.sh --group deliver` | pass | exit 0;CASE n=2;2/2 | |
| test-diagir wire | `bash scripts/test-diagir.sh --group wire` | pass | exit 0;CASE n=4;4/4 | |
| test-diagir route | `bash scripts/test-diagir.sh --group route` | pass | exit 0;CASE n=5;checks 6/6 | |
| test-diagir lab | `bash scripts/test-diagir.sh --group lab` | pass | exit 0;CASE n=5;5/5 | |
| test-diagir static-scope | `bash scripts/test-diagir.sh --group static-scope` | pass | exit 0;CASE n=2;2/2 | |
| test-diagir all | `bash scripts/test-diagir.sh` | pass | exit 0;25/25 | |
| Supply chain | `bash scripts/check-file-map.sh` | pass | exit 0;scanned=205 exempted=13;無新產品 pip 依賴 | |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded;無產品前端 |
| Race／stress | | n-a | | Explicitly excluded |
| Windows 真機 | | n-a | | Explicitly excluded／Out of Scope |

開工前 `test -x docs/dev/tools/devflow-evidence-gauntlet.sh` → exit 0。

### 2c 整合結論

本 hop 從 `#250` tip 開 branch。`--fork-sha` = 開工 HEAD = `3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。Fresh **之前**跑兩次,STATUS／座標完全相同。工作樹乾淨。合的不是 branch 名(本次不必合)。

- STATUS: N_A_NO_INCOMING
- FORK / HEAD / INTEGRATION / REF: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / refs/remotes/origin/main
- 恢復: n-a(N_A_NO_INCOMING;分岔後對方零新 commit)

6-notes 步 0 FORK=`25997871a86fce87a1b1f0658512d7f96e07dea3`(#244)。用該錨再跑一次(不當本 hop 交集證據;只記恢復路徑):

- STATUS: ALREADY_SYNCED
- FORK / HEAD / INTEGRATION / REF: 25997871a86fce87a1b1f0658512d7f96e07dea3 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 / refs/remotes/origin/main
- 恢復: 路徑 ①重綁 Final Fresh。Source SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4。不得只寫「證據不算數」就過。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得在驗證失敗後覆寫目標(S-1.1～S-1.5) | test-diagir validate + 親跑五封;last-good sha 不變 | pass |
| 不得只印 traceback 而無穩定碼(S-1.6) | S-1.1 stderr 兩行 FAIL;無 Traceback;收據六鍵 | pass |
| 不得留下半份新目標檔(S-2.2) | 旁路 tmp 長度 12;目標仍 last-good | pass |
| 不得未接閘就宣稱 wave-1 完成(S-2.3) | wire 4/4;`Path.write_text` 產品覆寫已刪 | pass |
| 不得黑盒猜 family(S-3.4) | missing-family → DIAGIR_FAMILY;無 auto／detect／已選 | pass |
| 不得只重放 lifecycle.json 當 Lab(S-4.4) | 索引負向=`kind-parked.json` | pass |
| 不得另造 Proof Lab 牙語言(S-4.5) | 無 check-diagir-lab.sh;三支牙仍在 devflow-check | pass |
| 不得把 mermaid／動畫當預設(S-5.1) | S-2.1 SVG 四詞 0 | pass |
| 不得碰 #196、不得 bump plugin(S-5.2) | plugin 3.23.3;plugin diff 空;#250 無名單禁檔 | pass |
| 不得收 Mermaid／Node／hosted／WYSIWYG／Q8／Q9 | #250 name-only 無那些依賴;預設靜態 SVG | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

本 hop 不是 dev-run 引擎案。6-notes 寫 `n-a-manual-impl-C`。欄位留空。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1 | 閘 exit、stdout JSON、stderr、目標 sha256 | exit 1;收據 `code=DIAGIR_KIND` `target_replaced=false`;stderr `FAIL DIAGIR_KIND &#124; knob: 把 kind 改回允許值，或改走路由表上的正確家族`;目標 sha=`8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` | ✅ |
| S-1.2 | exit、收據 `code`、目標 sha | exit 1;`code=DIAGIR_EMPTY`;sha 不變 | ✅ |
| S-1.3 | exit、收據 `code`、目標 sha | exit 1;`code=DIAGIR_LINES`;sha 不變 | ✅ |
| S-1.4 | exit、收據 `code`、目標 sha | exit 1;`code=DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-1.5 | exit、收據 `code`、目標 sha | exit 1;`code=DIAGIR_WHY`;detail `short-or-missing-why:src/`;sha 不變 | ✅ |
| S-1.6 | stdout JSON 六鍵與 stderr 兩碼行 | 六鍵都在;`abort=DIAGIR_ABORT`;`delivered`/`target_replaced` false;stderr 另有 `DIAGIR_ABORT` + Q6 旋鈕;無 Traceback | ✅ |
| S-2.1 | exit、收據四欄、目標檔頭與 sha | exit 0;`ok/delivered/target_replaced` true;`code` null;目標 sha=`053bc4df18d902ce9057ce91eb5e31bfe6d78d66128af29f83bbe5f76fc5a321` ≠ last-good;含 `<svg`/`</svg>`;len=1158 | ✅ |
| S-2.2 | 兩路徑 sha／size | 目標 sha 仍 last-good;tmp 恰 `<svg viewBox`(size 12);目標內容 ≠ tmp | ✅ |
| S-2.3 | 四檔(+兩支呼叫端)diff 與閘 import | `build-dir-tree.py:578` `require_write`;`build-gate-twin.py:2351` + tools 副本 byte-equal;`build-stage1-html.py:483`;stage2:556／stage4:759;產品 `write_text` 覆寫已刪 | ✅ |
| S-3.1 | 路由表列數與四欄 | `notes/design/diagir-route.md:7-12` 五 id;契約欄指回四份已核短冊 | ✅ |
| S-3.2 | exit、`code`、目標 sha | exit 1;`DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-3.3 | exit、`code`、目標 sha | exit 1;`DIAGIR_FAMILY`;sha 不變 | ✅ |
| S-3.4 | 收據 `code` 與是否出現已選／auto／detect | `DIAGIR_FAMILY`;三詞皆無 | ✅ |
| S-3.5 | 路由表產器欄與五入口 | `ROUTE_ROWS 5`;五 builder 各一列;`stage1-now` 不含 vbox-fig;無 hosted／mermaid 第六列 | ✅ |
| S-4.1 | yaml 列數、path、`expect_code` | version 1;六 path;三碼 `DIAGIR_KIND`／`DIAGIR_FAMILY`／`DIAGIR_WHY`;`tooth_language: existing` | ✅ |
| S-4.2 | 三支牙 exit 與閘 pos 收據 | Fresh 三牙全綠;閘對 `lifecycle-envelope`／`behavior-flow-pos`／`dir-tree-pos` `ok=true`(牙組內) | ✅ |
| S-4.3 | 三案 exit、`code`、目標 sha | KIND／FAMILY／WHY;三次後 sha 仍 last-good | ✅ |
| S-4.4 | 索引兩列 path | 負向 `kind-parked.json` ≠ `lifecycle.json`;負向有碼 | ✅ |
| S-4.5 | `devflow-check.sh` 仍呼叫三支牙 | 無 `check-diagir-lab.sh`;L132／135／236 仍 run 三支 | ✅ |
| S-5.1 | 目標檔 `rg` 與是否含 `<svg` | mermaid／mermaid.js／`<animate`／animateTransform 皆 0;有完整 svg | ✅ |
| S-5.2 | plugin diff 與變更清單 | version `3.23.3`;plugin diff 0 bytes;#250 無名單 `b8-gate-twin-review-ui/`／STATUS／HISTORY／IBV | ✅ |

## 截圖槽

本 feat 無產品前端;現象為 CLI／JSON 收據／靜態 SVG 位元組。截圖槽 N/A(無 `shots/` 定名檔 → 產檔器顯示佔位即可)。不准發明編輯 URL。不准新增一張只為了截圖。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／DIAGIR_* 收據／last-good sha
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待／例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 開工 agent | 壞 kind 不得換掉上一張可審圖 | `diagir.py deliver parked.json --out TARGET` | 終端機看 `DIAGIR_KIND` 旋鈕 | 目標停在 last-good | ✅ 人看見碼就改 kind,不要 checkout 舊 html |
| S-1.4 | 開工 agent | 不要把樹收成單盒 vbox | 同入口、tree-as-vbox 信封 | 查 `diagir-route.md` 換產器 | last-good 留下 | ✅ `DIAGIR_FAMILY` |
| S-2.1 | 產檔器 | 通過後人打開完整新圖 | 綠 lifecycle `deliver` | 瀏覽器直開目標 SVG | `replace` 同步結束 | ✅ 1158 bytes 靜態 SVG |
| S-2.2 | 產檔器 | 中斷時審頁仍打得開舊圖 | 旁路寫截斷 `.tmp`、不 `replace` | 刪殘 tmp 後重跑 | 未 replace 視同 ABORT | ✅ 目標仍 last-good |
| S-3.2 | 開工 agent | 第 1 站三框不要畫成生命週期 | stage1-as-lifecycle 信封 | 改跑 `build-stage1-html.py --action` | last-good 留下 | ✅ `DIAGIR_FAMILY` |
| S-3.4 | 開工 agent | 先選家族,不要讓機器猜 | 無 `family` 鍵的 JSON | 打開路由表勾一列 | 不寫檔 | ✅ 拒猜 |
| S-4.3 | owner／審查人 | 負向紅了 last-good 還在 | 三負 `deliver` 同一目標 | 跑索引列 | 負向若蓋檔 → wave-1 未完成 | ✅ `neg_held`;sha 不變 |
| S-5.1 | owner | wave-1 成功條件不是「會動」 | 打開 S-2.1 預設圖 | 瀏覽器離線直開 | 看到動畫預設就打回 | ✅ 四禁詞 0 |
| S-1.2／S-1.3／S-1.5／S-1.6／S-2.3／S-3.1／S-3.3／S-3.5／S-4.1／S-4.2／S-4.4／S-4.5／S-5.2 | — | — | — | — | — | 不適用(4-spec Operational Context 標不適用或純字面／接線／範圍牙) |

## Design Integrity Check(Design Boundary Contract 為 `applicable`)

1. **依賴反向被間接繞過**:未命中 —— 閘 `scripts/diagir.py:18` 只 import `devflow_atomic`;產器 → diagir。沒有 Archify／mermaid／Node import。沒有第二套 CLI 讓產器繞過 `validate` 仍宣稱 wave-1。
2. **資料所有權被繞過寫入**:未命中 —— 失敗路徑(`diagir.py:239-246`)在 `atomic_write` 之前 return;產器產品覆寫改 `require_write`(`diagir.py:261-274`)。inventory 本 slug 未改、形狀仍 tmp+`os.replace`。
3. **相容性破壞包成新增**:未命中 —— 信封鍵仍只有 `family`／`payload`;收據六鍵在。成功收據多 `family`／`out`、失敗多 `detail`／`target_unchanged` 是附加欄,未改必填鍵名。既有三支牙入口字面不變。
4. **一致性邊界被拆解**:未命中 —— 驗證與 `replace` 仍同一 `deliver`;失敗零寫目標。gate-twin 正本與 `docs/dev/tools/build-gate-twin.py` 同 T 逐字同步。
5. **宣告的 Test seam 未被使用**:未命中 —— 正式入口仍是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`;牙仍是 `test-diagir.sh` 六組 + 既有三支。未把 proto 當 ship。
6. **Known design limit 被實作悄悄「解決」**:未命中 —— ①`kind-parked.json` 已落地(Stage 6 契約允許,不是悄悄修掉 Stage 4 限制) ②仍無 OS hook 擋硬跑舊路徑(S-2.3 用 diff 咬) ③G3 現象以 `scripts/diagir.py` 為準,proto 仍非正式。

無未經授權 Boundary 變更。無 🔴。F-2 雙份路由表見 Standards;park 在 Known Limits,不改 R/S。

## Standards Axis

產品樹 = `git show 3b22f01`(#250)。本 PR vs `origin/main` = 本審查檔 + twin。

| F-id | 級 | 位置 | 問題 | 建議 | 影響 S/T |
|---|---|---|---|---|---|
| F-1 | 🟢 | `scripts/check-file-map.sh` `EXPECTED_MAPPED_FILES = 205`;`scripts/check-py-floor.sh:297` `MIN_HEREDOCS = 221`;`scripts/devflow-check.sh` 掛 `test-diagir.sh` | 不在 5-tasks Files 聯集。#250 自承 L1 D-3／D-4:母版自審／PF-2 地板必須跟上新檔,否則 CI 假紅或 PF-2 假綠 | 接受為記帳 L1,不是新 R/S。抽驗:file-map scanned=205;靜態釘 `MIN_HEREDOCS = 221` | S-4.5／T-5 |
| F-2 | 🟡 | `scripts/diagir.py:30-66` `ROUTE` 與 `notes/design/diagir-route.md:7-12` | 契約 Data owner 是 md 表;Python 另有一份五列。目前字面對得上,但會漂 | park。S-3.1 咬 md、S-3.5 咬 CLI;兩份都要綠才過。不要現在合併成單一來源(超出本 hop) | S-3.1／S-3.5 |
| F-3 | 🟢 | `scripts/test-diagir.sh:402-432` S-4.2 | 組內用 `build-vbox-fig.py --fixture lifecycle`／`build-dir-tree.py --fixture good` + 檔存在,不是直接呼叫三支 `check-*.sh` | 接受。4-spec 允許「該牙既有射程內綠」。本 hop Fresh 三支牙 exit 0 | S-4.2 |
| F-4 | 🟢 | `scripts/diagir.py:222-228` `default_body` | CLI 無 `--body` 時 dir-tree／stage1 寫 stub HTML。產器走 `require_write(..., body=真實頁)` | 接受。wave-1 綠交付契約是 lifecycle SVG(S-2.1) | S-2.1／T-3 |
| F-5 | 🟢 | `scripts/diagir.py:74-88` 失敗收據 | 必填六鍵都在;另加 `detail`／`target_unchanged`／`target_existed` | 接受為 additive。S-1.6 用 issubset | S-1.6 |
| F-6 | 🟢 | `6-implementation-notes.md:30-106` T Review Log | T-1..T-6 reviewer = implementer-C self-check,明文留給 PR／G3 | 接受為本檔存在理由。本 hop 獨立重跑數字相符,不當作者主張 | 過程 |
| F-7 | 🟢 | `scripts/test-diagir.sh:495` `origin/main...HEAD` | D-1 把 S-5.2 從雙點改三點,避免 main 後來的 STATUS／HISTORY 假紅 | 接受 L1。本 hop 抽驗 plugin diff 空、#250 無名單禁檔 | S-5.2 |

Dependency Direction／Boundary Leakage／Data Ownership／Interface Stability:未發現反向依賴;內部擋形未漏成公開第二 API;非 owner 未直寫目標;公開入口字面仍是 `diagir.py deliver`／既有三支牙。無 🔴。無未授權 🟡 Boundary(F-2 是複本風險,不是改所有權)。

## Spec Axis

| R | 判定 | 出處 |
|---|---|---|
| R-1 失敗保住 last-good + DIAGIR_* | 符合 | S-1.1～S-1.6 親跑;六碼與 Q6 旋鈕句逐字(`diagir.py:20-27`);last-good sha 對上 Stage 3 鎖值 |
| R-2 通過才原子交付 | 符合 | S-2.1 整份新 SVG;S-2.2 截斷 tmp;S-2.3 五處 `require_write`;`devflow_atomic.py:13-22` 與 inventory:30-37 同形 |
| R-3 五列查找、不猜家族 | 符合 | 表五列;S-3.2～S-3.4 `DIAGIR_FAMILY`;S-3.5 `ROUTE_ROWS 5`;無第六列 |
| R-4 Proof Lab 薄索引 | 符合 | 六列三家族;三負紅且不蓋檔;無第二套 Lab 牙;三支既有牙仍在 |
| R-5 預設靜態 SVG、不碰 #196／plugin | 符合 | S-5.1 四詞 0;plugin `3.23.3`;#250 範圍牙綠 |
| M-1 dir-tree 改走閘 | 符合 | `build-dir-tree.py:576-578` |
| M-2 gate-twin 改走閘 | 符合 | `build-gate-twin.py:2351-2356`;tools 副本 byte-equal |
| M-3 stage1-html 改走閘 | 符合 | `build-stage1-html.py:483-489` |
| Design Boundary | 符合 | 見 Design Integrity Check;無 L2、無未授權變更 |
| 6-notes Deviations | 如實、皆 L1 | D-1 三點 diff;D-2 S-4.5 不禁漢字「取代」;D-3 filemap 205;D-4 MIN_HEREDOCS 221。獨立抽驗對得上,不是 L2 |

## 變更架構圖

產品(#250,已在 tip;`git show 3b22f01` basename)與本 PR 審查密封:

```
[scripts/diagir.py]
    |  validate → fail(DIAGIR_*)
    |  deliver  → [scripts/devflow_atomic.py] atomic_write
    +--> require_write
         build-dir-tree.py
         build-gate-twin.py ----parity---- docs/dev/tools/build-gate-twin.py
         build-stage1-html.py
         build-stage2-html.py
         build-stage4-html.py
    +--> route CLI
         notes/design/diagir-route.md

[scripts/fixtures/diagir-lab.yaml]
    +--> vbox-fig/lifecycle.json + kind-parked.json
    +--> gate-twin/fig-long-label + fig-tree-ascii
    +--> dir-tree/good + missing-why

[scripts/test-diagir.sh]
    groups: validate / deliver / wire / route / lab / static-scope

既有牙(入口不變):
check-vbox-fig.sh / check-dir-tree.sh / check-gate-twin.sh

本 hop(docs-only,不是產品碼):
[7-review.md]   Source SHA=3b22f01 (#250 tip = 本 hop 開工 HEAD)
[7-review.html] G3 twin
```

無新公開 HTTP 端點、無新表。改 Diff 必須改本圖。

## Diff(merge-base(main)..HEAD,逐檔折疊)

`merge-base(origin/main, HEAD)` 在寫檔時 = `3b22f01`(本 hop 從 #250 tip 分出)。產品 #250 已在 main。本 companion PR 相對 main 只新增本檔／twin。

<details>
<summary>產品 #250(已在 tip;審查對象,不是本 PR 新增)</summary>

32 files,+1802/−30。basename 見變更架構圖。入口仍是 `python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`。完整 hunk:`git show 3b22f01`。

</details>

<details>
<summary>docs/dev/diagram-ir-gate/6-implementation-notes.md(+html) — Stage 6 錨點(已在 tip)</summary>

FORK_INTEGRATION_SHA: 25997871a86fce87a1b1f0658512d7f96e07dea3。有 Self-Review;T Review Log 自承 self-check。本 hop 步 4 才讀。

</details>

<details>
<summary>docs/dev/diagram-ir-gate/7-review.md + 7-review.html — 本審查正本</summary>

本檔。`verdict: PRE-REVIEW`。Source SHA=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。Human G3 未填。

</details>

## Verdict

**PRE-REVIEW。不是 G3 PASS。** Human 尚未判定。機械面(本 hop 獨立抽驗,不新造 R/S):

| 門檻 | 本 hop | 證據 |
|---|---|---|
| 本次 S 全綠 | 21/21 自建矩陣 ✅ | Coverage Matrix |
| 既有全綠 | entry point 四層 + test-diagir 25/25 | 6/6;16/16;81/81;222;25/25 |
| 現象證據逐 S 相符 | 21/21 | 現象證據表 |
| Evidence 契約 | Fresh 綁 HEAD;`--review-file` 見附錄 A3 | Source SHA=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4` |
| 無 🔴 | 無。F-2 為 🟡 park | Standards／Spec |
| 2c 在 Fresh 之前 | 是 | 本 hop `N_A_NO_INCOMING`;S6 錨 `ALREADY_SYNCED` 走重綁 |
| Human G3 | **未填** | 本檔不得代填 PASS |

建議 Human:機械證據夠送 G3;要打回就從 F-2(雙份路由)或 T self-check 過程債下手,不要因為「全勾」自動 PASS。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | 主機層不擋「跳過閘硬跑舊 write 路徑」(4-spec Known limit ②) | 中 | park;S-2.3 仍用 diff 咬接線。owner=方法論;追蹤=4-spec Design Constraints |
| 2 | 含 Source SHA 的 commit 不能等於該 commit 自己的 SHA(與 IBV Known limit ② 同一悖論) | 中 | park。本檔 Fresh 寫成開工 HEAD `3b22f01`。本 docs commit 落地後 HEAD 會漂;合法恢復=再重綁 Final Fresh,不得再合產品碼。owner=方法論 |
| 3 | 路由表雙份(md + `diagir.ROUTE`;F-2) | 低 | park;兩份目前對得上。owner=方法論;追蹤=本表 + F-2 |
| 4 | T-1..T-6 獨立 T review 在 Stage 6 是 self-check(F-6) | 低 | 本檔即補救路徑。Human G3 抽驗一列即可。owner=rick |
| 5 | 本檔 `verdict: PRE-REVIEW`;全勾也不算 shipped | 中 | 留給適格人類 reviewer。Agent 禁改成 PASS |
| 6 | Fresh 初跑 `check-gate-twin` 因缺 markdown-it-py exit 2 | 低 | ENV;補裝 pin 4.0.0 後 222 綠。不計 IMPL 失敗 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**(applicable):無未授權 Boundary 變更。F-2 🟡 為複本風險已 park 本表 #3,未改 R/S／所有權／公開 Interface。無須 L2
- [ ] Quiz(**不可逆改動必做**;其餘 full lane 選配,fast 免):公開信封 + last-good;留給 Human G3
- [x] (條件式)整合回歸已在 Final Fresh **之前**完成:步 2c 結論(含三個 SHA 與 canonical ref)在「2c 整合結論」。Source SHA 在 Exit 文件寫成當下等於開工 HEAD。Verdict 之後不得再改程式碼
- [ ] PR → develop(feature branch,禁直上 master;本專案整合分支是 `main`)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`(本 repo 無 living spec;`n-a`)
- [ ] STATUS.md 已更新為 shipped(整合分支上、PR 合併後由合併者做,不塞進本 branch)
- [ ] 7-review frontmatter status: shipped;上游 artifact 可保留 approved(**本檔仍 draft／PRE-REVIEW**)
- [x] 7-review.html 已產生(G3 twin;`scripts/build-gate-twin.py`;審頁另跑 `scripts/build-stage7-html.py --action` → `/tmp/diagir-stage7-shots.html`,不覆寫 twin)
- [ ] feature branch 已刪 / worktree 已清

## 附錄:本輪特有

### A1　本 hop 座標 vs Stage 6 FORK

| 欄 | SHA |
|---|---|
| 產品／Fresh／本 hop 開工 HEAD | 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4 |
| 6-notes FORK(#244) | 25997871a86fce87a1b1f0658512d7f96e07dea3 |
| last-good sha256(S-1.1 鎖值) | 8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc |
| S-2.1 綠交付 sha256 | 053bc4df18d902ce9057ce91eb5e31bfe6d78d66128af29f83bbe5f76fc5a321 |

本 hop 2c 用開工 HEAD 當 fork → `N_A_NO_INCOMING`(exit 0,兩次相同)。用 6-notes FORK → `ALREADY_SYNCED`(exit 2,輸出不算交集)。恢復走路徑 ①,Source SHA 綁 `3b22f01`。

證明指令(工作樹可有未提交的本檔):

```
test "$(python3 -c "import re,pathlib; t=pathlib.Path('docs/dev/diagram-ir-gate/7-review.md').read_text(); print(re.search(r'- Source SHA:\s*([0-9a-fA-F]{7,})', t).group(1))")" = "$(git rev-parse HEAD)" && echo S-SHA-ok
```

本 docs commit 落地後 HEAD 會漂 —— Known Limits ②。合法恢復=再重綁,不是再合 INTEGRATION_SHA。

### A2　作者對照(N4)

先自建 21 列矩陣並親跑,才 `review-unlock` 讀 6-notes。

- Self-Review ①～⑧宣稱的數字(validate 6/6、deliver 2/2、wire 4/4、route 6/6、lab 5/5、static 2/2、vbox 16/16、dir-tree 81/81、gate-twin 222)與本 hop 獨立輸出相符。
- D-1～D-4 皆 L1、理由成立;本 hop 抽驗三點 plugin diff、無 Lab 第二牙、file-map 205、MIN_HEREDOCS 221。
- Decisions(`require_write`、gate-twin 固定兩步 behavior-flow、last-good 用 Stage 3 sha、ellipsis why 地板 4)未改 R/S。
- T Review Log 不是獨立 reviewer(F-6)。本檔補上獨立覆蓋,不採信作者「PASS」當 G3。
- 無作者矩陣可裁出缺漏 S。無 L2 silent drift。

### A3　Fresh／gauntlet 指令與原始輸出

```
test -x docs/dev/tools/devflow-evidence-gauntlet.sh
bash scripts/check-spec-gate.sh docs/dev/diagram-ir-gate/4-spec.md
bash scripts/check-vbox-fig.sh
bash scripts/check-dir-tree.sh
bash scripts/check-gate-twin.sh
bash scripts/test-diagir.sh
```

Fresh 實跑當時 HEAD=`3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`:

```
✅ G2 spec gate:6/6 全過
✅ PASS:vbox-fig 產圖器 + 牙 16/16
✅ PASS:dir-tree 產器 + 牙 81/81
✅ gate twin 產生器守衛:全過(222 項)
✅ PASS:diagir all 25/25
```

`check-gate-twin` 第一次:`缺相依 markdown-it-py` exit 2。`pip install 'markdown-it-py==4.0.0'` 後重跑 222。ENV,不改產品碼。

S-1.1 親跑收據(節錄):

```
exit 1
{"ok": false, "code": "DIAGIR_KIND", "knob": "把 kind 改回允許值，或改走路由表上的正確家族",
 "abort": "DIAGIR_ABORT", "delivered": false, "target_replaced": false}
FAIL DIAGIR_KIND | knob: 把 kind 改回允許值，或改走路由表上的正確家族
FAIL DIAGIR_ABORT | knob: last-good 仍在；先修 IR 再重跑
target sha=8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc
```

S-2.1 親跑收據(節錄):

```
exit 0
{"ok": true, "family": "vbox-lifecycle", "code": null, "delivered": true, "target_replaced": true}
target sha=053bc4df18d902ce9057ce91eb5e31bfe6d78d66128af29f83bbe5f76fc5a321
len=1158; <svg> yes; mermaid=0; <animate=0
```

2c 本 hop 結論行(跑兩次相同):

```
STATUS: N_A_NO_INCOMING
FORK_INTEGRATION_SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
FEATURE_HEAD: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
INTEGRATION_SHA: 3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4
INTEGRATION_REF: refs/remotes/origin/main
共同戰場:無
結論:STATUS=N_A_NO_INCOMING FORK=3b22f01… HEAD=3b22f01… INTEGRATION=3b22f01…(refs/remotes/origin/main)—— 分岔後對方零新 commit,Exit Checklist 可記 n-a
```

Gauntlet(本檔落檔後、`--source-sha $(git rev-parse HEAD)`、`--review-file`、Required 四層旗標加嚴):

```
bash docs/dev/tools/devflow-evidence-gauntlet.sh docs/dev/diagram-ir-gate/7-review.md \
  --source-sha $(git rev-parse HEAD) --review-file \
  --require-layer check-spec-gate \
  --require-layer check-vbox-fig \
  --require-layer check-dir-tree \
  --require-layer check-gate-twin
```

本 hop 實跑:`✅ evidence gauntlet: 91 checks passed — docs/dev/diagram-ir-gate/7-review.md`。Source SHA 當時 = HEAD = `3b22f01a72240ed9c4d57dc0ab8568678e8d6ea4`。

Profile Required 是一條全形 `／` 字串,Evidence 表第一列 Layer 必須與該字串全等,否則 E7 把四層當成一層缺席。

### A4　抽驗座標(給只做第 5 步的人)

| 要看的一句 | 檔:行 |
|---|---|
| parked kind → DIAGIR_KIND | `scripts/diagir.py:139-140` |
| 失敗收據六鍵 + 兩行 FAIL | `scripts/diagir.py:74-88` |
| 通過才 atomic_write | `scripts/diagir.py:238-250` |
| tmp+replace | `scripts/devflow_atomic.py:13-22` |
| dir-tree 接閘 | `scripts/build-dir-tree.py:576-578` |
| 路由五列 | `notes/design/diagir-route.md:7-12` |
| Lab 六列 | `scripts/fixtures/diagir-lab.yaml:1-30` |
| 三支牙仍在 | `scripts/devflow-check.sh:132,135,236` |
