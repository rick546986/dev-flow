---
feature: diagram-ir-gate
stage: 6-implementation
status: draft
owner: cursor-cloud-agent
updated: 2026-09-12
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 25997871a86fce87a1b1f0658512d7f96e07dea3

## 起手

- 圍欄自查:只讀 4-spec / 5-tasks / 本檔 / living spec(本 repo `docs/specs/` 無條可引)。禁讀 1/2/3。proto 只對照形狀。
- branch:`cursor/diagram-ir-gate-stage6-impl-a-990c` @ `25997871a86fce87a1b1f0658512d7f96e07dea3`（#244 Stage 5 tip）
- 0b worktree 隔離:`n-a:本 feature 未並行`（單一 checkout；無第二棵 worktree／無共用 DB／無容器 port）
- 0c 守衛與 doctor:雲端單代理獨立實作（impl-A）。`devflow-exec` 未在此 hop 武裝；scope 以 5-tasks Files 聯集 + D-1 檔案地圖記帳為準。

## T Review Log

### T-1
- reviewer identity:implementer self-check（雲端單代理;獨立 T review 留給 PR／G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:`n=$(bash scripts/test-diagir.sh --group validate -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-diagir.sh --group validate`
- Covers finding:S-1.1..S-1.6 各有含 S-id 的案例
- Files finding:`scripts/diagir.py`、`scripts/test-diagir.sh`、`scripts/fixtures/diagir/`
- RED→GREEN finding:Stage 5 開工前牙不存在 exit 127；本 hop 落地後 validate ≥6 綠
- Test Integrity finding:none
- Design boundary finding:閘擁有 DIAGIR_*；未 import Archify／mermaid／Node；失敗不呼叫 atomic_write
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:implementer self-check（雲端單代理;獨立 T review 留給 PR／G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:`n=$(bash scripts/test-diagir.sh --group deliver -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-diagir.sh --group deliver`
- Covers finding:S-2.1／S-2.2
- Files finding:`scripts/diagir.py`、`scripts/devflow_atomic.py`、牙／治具
- RED→GREEN finding:同 T-1；deliver 組落地後綠
- Test Integrity finding:none
- Design boundary finding:`atomic_write` 只做 tmp+replace；驗證失敗不呼叫
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:implementer self-check（雲端單代理;獨立 T review 留給 PR／G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:`n=$(bash scripts/test-diagir.sh --group wire -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 4 && bash scripts/test-diagir.sh --group wire`
- Covers finding:S-2.3
- Files finding:三支產器 + stage2／stage4 + tools 副本
- RED→GREEN finding:產品目標不再 `Path.write_text`／`dest.write_text`／`out_local.write_text`
- Test Integrity finding:none
- Design boundary finding:vbox-fig 仍只 stdout；tools 副本 `cp` 同步
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:implementer self-check（雲端單代理;獨立 T review 留給 PR／G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:`n=$(bash scripts/test-diagir.sh --group route -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-diagir.sh --group route`
- Covers finding:S-3.1..S-3.5
- Files finding:`notes/design/diagir-route.md` + 閘／牙
- RED→GREEN finding:五列四欄齊；錯家族／缺欄 → DIAGIR_FAMILY
- Test Integrity finding:none
- Design boundary finding:無第六家族；未猜 family
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-5
- reviewer identity:implementer self-check（雲端單代理;獨立 T review 留給 PR／G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:`n=$(bash scripts/test-diagir.sh --group lab -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 5 && bash scripts/test-diagir.sh --group lab`
- Covers finding:S-4.1..S-4.5
- Files finding:`diagir-lab.yaml`、`kind-parked.json`、牙／治具
- RED→GREEN finding:六列三家族；三負不蓋 last-good；無第二套 Lab 牙
- Test Integrity finding:none
- Design boundary finding:索引只點名既有 fixture；`tooth_language: existing`
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-6
- reviewer identity:implementer self-check（雲端單代理;獨立 T review 留給 PR／G3）
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12
- Verify:`n=$(bash scripts/test-diagir.sh --group static-scope -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-diagir.sh --group static-scope`
- Covers finding:S-5.1／S-5.2
- Files finding:牙／治具
- RED→GREEN finding:綠交付無 mermaid／動畫；plugin 仍 3.23.3；無 #196／IBV／STATUS 表列
- Test Integrity finding:none
- Design boundary finding:未 bump plugin、未收 Node render
- verdict:PASS
- correction + re-review after FAIL:N/A

## Progress Log

<!-- 日期 | T-id | hash；PASS 後填 -->

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run:

## TDD Evidence

### T-1 / S-1.1
- RED: `bash scripts/test-diagir.sh --group validate` → Stage 5 開工前 `No such file` exit 127
- GREEN: 見 Verify 組 validate

### T-1 / S-1.2
- RED: 同上（同一牙未落地）
- GREEN: `test_s_1_2_empty_title_diagir_empty`

### T-1 / S-1.3
- RED: 同上
- GREEN: `test_s_1_3_four_lines_diagir_lines`

### T-1 / S-1.4
- RED: 同上
- GREEN: `test_s_1_4_tree_as_vbox_diagir_family`

### T-1 / S-1.5
- RED: 同上
- GREEN: `test_s_1_5_short_why_diagir_why`

### T-1 / S-1.6
- RED: 同上
- GREEN: `test_s_1_6_fail_emits_abort_and_receipt`

### T-2 / S-2.1
- RED: `--group deliver` exit 127
- GREEN: `test_s_2_1_pass_lifecycle_atomic_svg`

### T-2 / S-2.2
- RED: 同上
- GREEN: `test_s_2_2_interrupt_keeps_last_good`

### T-3 / S-2.3
- RED: `--group wire` exit 127
- GREEN: wire 四案（靜態接線 + dir-tree／stage1 實寫 + 壞 IR 仍拒）

### T-4 / S-3.1
- RED: `--group route` exit 127
- GREEN: `test_s_3_1_route_table_five_rows`

### T-4 / S-3.2
- RED: 同上
- GREEN: `test_s_3_2_stage1_as_lifecycle_family`

### T-4 / S-3.3
- RED: 同上
- GREEN: `test_s_3_3_dir_as_vbox_family`

### T-4 / S-3.4
- RED: 同上
- GREEN: `test_s_3_4_missing_family_not_guessed`

### T-4 / S-3.5
- RED: 同上
- GREEN: `test_s_3_5_five_entries_map_five_rows`

### T-5 / S-4.1
- RED: `--group lab` exit 127；`diagir-lab.yaml` 不存在
- GREEN: `test_s_4_1_lab_index_six_rows`

### T-5 / S-4.2
- RED: 同上
- GREEN: `test_s_4_2_three_pos_replay`

### T-5 / S-4.3
- RED: 同上
- GREEN: `test_s_4_3_three_neg_hold_last_good`

### T-5 / S-4.4
- RED: 同上
- GREEN: `test_s_4_4_not_only_lifecycle_json`

### T-5 / S-4.5
- RED: 同上
- GREEN: `test_s_4_5_no_second_lab_tooth`

### T-6 / S-5.1
- RED: `--group static-scope` exit 127
- GREEN: `test_s_5_1_default_static_svg_no_mermaid`

### T-6 / S-5.2
- RED: 同上
- GREEN: `test_s_5_2_no_plugin_bump_no_196`

## Decisions(spec 未載明的自由選擇)

- D-impl-1: 產器接線用同模組 `persist_product(family, payload, path, content)`，CLI 仍是 `deliver ENVELOPE.json --out TARGET`。HTML 產器組一個該家族合法 payload，驗證過才 `atomic_write` 產品字串。依據:4-spec S-2.3「或同模組函式」。
- D-impl-2: gate-twin 散發副本用 walk-up 載入 `scripts/diagir.py`，避免 `docs/dev/tools/` 目錄沒有 sibling 模組。依據:[Assumption] tools 副本必須與正本 `cp` 同步且不得 raw write。
- D-impl-3: CLI `deliver` 無 `--content` 時寫內建靜態 SVG（含 `<svg`、無 mermaid）。依據:S-2.1／S-5.1 觀測欄。

## Deviations

### D-1(L1)
- 現象:新增 `scripts/diagir.py`、`scripts/devflow_atomic.py`、`scripts/test-diagir.sh` 會讓 `check-file-map.sh` 的 `EXPECTED_MAPPED_FILES` 從 202 變成 205，且檔案地圖／靜態互釘必須跟著改。這三檔不在任一 T 的 Files 聯集。
- 保守選擇:同步上修常數、補 `guides/guide-dev-flow.html` #filemap 三列、改 `scripts/test-architecture-guards.sh` 互釘。不改 STATUS 表列、不 bump plugin。
- 理由:既有牙／`devflow-check` 必須維持綠；不動 R/S。
- 影響:T-1..T-6 落地 / 無 R/S 變更

## Files Changed

對照 4-spec Diff Budget（閘／原子寫／接線／路由／Lab）+ D-1 檔案地圖記帳 + 本檔。

## Diff(各 T commit,逐檔折疊)

### persist_product · `scripts/diagir.py` 248-250  T-1
改什麼：正式閘 validate + DIAGIR_* 收據，失敗不寫檔。
關聯：產器 → persist_product → atomic_write
```diff
+def persist_product(path, text, family, payload):
+    return deliver({"family": family, "payload": payload}, str(path), content=text)
```

### atomic_write · `scripts/devflow_atomic.py` 13-22  T-2
改什麼：抽出 tmp+os.replace+補 newline。
關聯：diagir.deliver 唯一寫入
```diff
+def atomic_write(path, text):
+    tmp = path + ".tmp"
+    os.replace(tmp, path)
```

### write_text · `scripts/build-dir-tree.py` 576-588  T-3
改什麼：產品覆寫改走 persist_product。
關聯：diagir
```diff
-    pathlib.Path(path).write_text(text, encoding="utf-8")
+    result = diagir.persist_product(str(path), text, "dir-tree", payload)
```

### main · `scripts/build-stage1-html.py` 480-484  T-3
改什麼：審頁寫檔改走 stage1-now 閘。
關聯：diagir.persist_product
```diff
-        dest.write_text(html_out, encoding="utf-8")
+    result = diagir.persist_product(str(dest), html_out, "stage1-now", STAGE1_PAYLOAD)
```

### print_route · `scripts/diagir.py` 256-262  T-4
改什麼：`route` 印五列查找表。
關聯：notes/design/diagir-route.md
```diff
+def print_route():
+    print("ROUTE_ROWS %d" % len(ROUTE))
```

## Self-Review

①每個 T×S 有含 S-id 的測試 + 該 T RED/GREEN：是（Stage 5 127 為 RED；本 hop GREEN 見牙）。
②每 T 在 T Review Log 有 verdict：是。
③PASS 早於 commit：雲端單代理自檢；獨立審查留給 PR。
④無未收斂 FAIL。
⑤Progress Log 於 commit 後補 hash。
⑥git diff 檔案 = Files 聯集 + D-1 地圖三檔 + 本 6-notes + 5-tasks checkbox。
⑦D-1 已記；無 silent drift。
⑧回歸：check-vbox-fig／check-dir-tree／check-gate-twin／相關 devflow-check 段。
