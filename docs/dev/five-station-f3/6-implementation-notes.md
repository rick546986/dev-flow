---
feature: five-station-f3
stage: 6-implementation
status: draft
owner: implementer-A
updated: 2026-09-14
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 822f84289f6f4267252907e36862e93f1c90eb9d

> Single implementer stream（F2 pattern）。T Review **PENDING_INDEPENDENT_REVIEW**（author ≠ reviewer；未自填 ACCEPTED）。未發明 Human G3 PASS。5-tasks checkbox 保持未勾。活樹 cut 只在 T-10 收口寫入。

## 0. 起手

### 0a branch／錨點

- 只讀 4-spec／5-tasks／本檔／living。禁讀 1／2／3。
- `git fetch origin main` → `FORK=822f84289f6f4267252907e36862e93f1c90eb9d`
- `git switch -c cursor/five-station-f3-stage6-impl-c424 "$FORK"`
- `test "$(git rev-parse HEAD)" = "$FORK"` → 通過

### 0b worktree 隔離

n-a:本 feature 未並行。單一 checkout、無第二 worktree；不改 STATUS（companion 由 coordinator 開）；無另開容器／DB／queue。

### 0c 守衛與 doctor

手動實作（非 dev-run 派工）。`devflow-exec.sh start` 未武裝本 session（cloud agent 單線）。doctor 綠只握手，不是 hop 通行證（T-7 DOCTOR-NE-TICKET）。

## T Review Log

implementer-A 不得自裁 ACCEPTED。下列每 T 等獨立 reviewer（fresh-context Agent 或適格人類）親跑 Verify。未發明 G3。未勾 5-tasks checkbox。

| T | verdict | 分類 | 一句 |
|---|---|---|---|
| T-1 | PENDING_INDEPENDENT_REVIEW | — | ATTEST-VISIBLE 五切片 `--slot`；讀端只讀 |
| T-2 | PENDING_INDEPENDENT_REVIEW | — | ATTEST-SILENT-RED 注入 `return True` |
| T-3 | PENDING_INDEPENDENT_REVIEW | — | READ-SEAM 三切片；只讀正本鍵 |
| T-4 | PENDING_INDEPENDENT_REVIEW | — | PRE 五棵；`F3 cut 未發生`；禁「已宣告所以切了」 |
| T-5 | PENDING_INDEPENDENT_REVIEW | — | NEW5-CUT-OK 條件邊；`--group graph-edges` 官方名 |
| T-6 | PENDING_INDEPENDENT_REVIEW | — | GRAPH-WORD-NE＋指南五站用語；節點／token 不刪 |
| T-7 | PENDING_INDEPENDENT_REVIEW | — | doctor 漏加印 INCOMPATIBLE；綠≠票；握手 0 diff |
| T-8 | PENDING_INDEPENDENT_REVIEW | — | WAIT／KEEP-MK／SHIP-MECH 注入紅 |
| T-9 | PENDING_INDEPENDENT_REVIEW | — | OLD7 凍結＋SELF-OLD7 |
| T-10 | PENDING_INDEPENDENT_REVIEW | — | 25 CASE＋`--only`／`--probe`＋活樹 cut |

### T-1
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: 5-tasks 原指令（五 `--slot` `-ge 5`）→ 待 reviewer 親跑
- Covers finding: implementer 自檢 S-1.1／S-1.2／S-1.4／S-1.5 有含 S-id assertion；非 verdict
- Files finding: ⊆ T-1 Files；未寫活樹 cut（T-10 才寫）
- RED→GREEN finding: 開工前 `test-five-station-f3.sh` 不存在＝RED；落地後五切片可數
- Test Integrity finding: implementer 自檢 none；待獨立審
- Design boundary finding: implementer 自檢 n-a pending；契約 applicable
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: `--case ATTEST-SILENT-RED` → 待親跑
- Covers finding: S-1.3／S-1.6；未改 STATUS；用語交付不在本 T
- Files finding: ⊆ T-2 Files
- RED→GREEN finding: 注入 `return True` 無三槽＝該格紅
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: READ-SEAM 三切片 `-ge 3` → 待親跑
- Covers finding: S-2.1／S-2.2／S-2.3；`contract_version()` 只讀 `devflow_contract_version`
- Files finding: ⊆ T-3 Files；未 bump 活樹（T-7）
- RED→GREEN finding: 舊 reader（F2）對 2.1.0 fixture 回空／不以 2.1 開頭＝紅格
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: PRE 五棵 `-ge 5`＋拒因字面 → 待親跑
- Covers finding: S-2.4…S-2.7
- Files finding: ⊆ T-4 Files；未改 graph.yaml（T-5）
- RED→GREEN finding: 缺 cut 理由含 `F3 cut 未發生`；禁「已宣告所以切了」
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: NEW5-CUT-OK＋PRE-HOPS-200＋`--group graph-edges` `-ge 3` → 待親跑
- Covers finding: S-3.1／S-3.2／S-3.5／S-3.6／S-7.4；禁 GRAPH-AGREE
- Files finding: ⊆ T-5 Files；`N7-g1.md`／`N6-g2.md` 仍在
- RED→GREEN finding: cut-ok 不進例行停；2.0.0 跳過側不生效
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: GRAPH-WORD-NE＋`check-gate-tokens.sh` → 待親跑
- Covers finding: S-3.3／S-3.4
- Files finding: ⊆ T-6 Files；token 牙只呼叫
- RED→GREEN finding: 指南五站用語 ∧ 預設仍 N7-g1 ∧ 標成功＝該格紅
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-7
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: DOCTOR-HONEST／NE-TICKET＋`git diff --exit-code -- hooks/_doctor_impl.py` → 待親跑
- Covers finding: S-4.1…S-4.5
- Files finding: ⊆ T-7 Files；未改 `_doctor_impl.py`；未寫活樹 cut
- RED→GREEN finding: 漏加 2.1.0 → INCOMPATIBLE；綠不當 hop 票
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: NEW5-WAIT-RED／KEEP-MK-RED／KEEP-SHIP-MECH `-ge 3` → 待親跑
- Covers finding: S-6.1／S-6.2／S-6.3／S-5.3
- Files finding: ⊆ T-8 Files
- RED→GREEN finding: 三注入各為紅格；KEEP-MK 具名 M3／M5／M9／M11／M12／M15
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-9
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: OLD7-FREEZE／OLD7-FOLD-RED／SELF-OLD7 `-ge 3` → 待親跑
- Covers finding: S-7.1／S-7.2／S-7.3／S-7.5
- Files finding: ⊆ T-9 Files；本目錄／f2／simplify 不當 NEW5
- RED→GREEN finding: in-flight 整段舊 7；三凍結 slug 跳不過
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: PENDING_INDEPENDENT_REVIEW
- reviewer kind: fresh-context Agent（待派；≠ implementer-A）
- reviewed-at: n-a:尚未獨立審
- Verify: `-v` `-ge 25`＋`--only` exit 3＋`--probe`＋`--group hollow -ge 6`＋F2 地板 → 待親跑
- Covers finding: S-5.*／S-8.2／S-8.3／S-8.4＋S-8.1／S-8.5／S-8.6 gate
- Files finding: ⊆ S-8.2 准許清單；STATUS／HISTORY／`_templates/`／handshake＝0
- RED→GREEN finding: 單一 process 三路；hollow 探針 exit 3；未知旗標 exit 2
- Test Integrity finding: pending
- Design boundary finding: pending
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

## Progress Log

<!-- T Review PASS 後才記 hash。本 stream 未自裁 PASS，故無 ACCEPTED 列。 -->

implementer commits（軌跡，不是 Progress Log 驗收列）：見本 branch `git log`。獨立審 PASS 後由 reviewer／coordinator 補 hash。

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)

Run: n-a:manual-implementer-stream

## TDD Evidence

### T-1 / S-1.1
- RED: `bash scripts/test-five-station-f3.sh --case ATTEST-VISIBLE --slot ok` → 腳本不存在（開工前）
- GREEN: 同指令；`which_condition=f3-cut`；`f3_cut_happened` True

### T-1 / S-1.2
- RED: `--slot missing`／`--slot empty` 不存在
- GREEN: 缺檔／空 who → False

### T-1 / S-1.4
- RED: 無 readonly 切片
- GREEN: `--slot readonly` 呼叫前後位元組不變

### T-1 / S-1.5
- RED: 無 sibling-reject
- GREEN: `--slot sibling-reject`；契約無 cut 兄弟鍵

### T-2 / S-1.3
- RED: 無 ATTEST-SILENT-RED
- GREEN: 注入 `return True` 無三槽＝該格紅

### T-2 / S-1.6
- RED: 用語／blame 可冒充 SoT
- GREEN: 本 T 未改 STATUS；guide 用語不在本 T Files

### T-3 / S-2.1
- RED: F2 `contract_version` 讀錯鍵回空
- GREEN: `--reader canonical-200` 回 `2.0.0`

### T-3 / S-2.2
- RED: 無 READ-SEAM 舊 reader 格
- GREEN: 無旗標切片＝舊 reader 紅格

### T-3 / S-2.3
- RED: 正本 2.1.0 仍宣告假
- GREEN: `--reader canonical-210` 以 `2.1` 開頭；cut 獨立假

### T-4 / S-2.4
- RED: 2.1.0 冒充 cut
- GREEN: PRE-210-NE-CUT 理由含 `F3 cut 未發生`

### T-4 / S-2.5
- RED: PRE-AND 三缺不可數
- GREEN: `--missing declared|in-flight|cut` 各自理由

### T-4 / S-2.6
- RED: 2.0.0＋五站 hops 放行
- GREEN: PRE-HOPS-200 印 SLOT-REJECT

### T-4 / S-2.7
- RED: 未宣告就跳過
- GREEN: 跳過側在 `declared` 假時不生效

### T-5 / S-3.1
- RED: cut-ok 仍進 N7-g1
- GREEN: NEW5-CUT-OK hop 紀錄無例行停

### T-5 / S-3.2
- RED: graph 單邊跳過
- GREEN: PRE-HOPS-200 dual-read 仍舊 7

### T-5 / S-3.5
- RED: 發明 GRAPH-AGREE
- GREEN: `--group graph-edges` 只印官方名

### T-5 / S-3.6
- RED: 刪節點或只翻函式
- GREEN: `next_when_five` 條件邊＋路線閘；節點檔仍在

### T-5 / S-7.4
- RED: 本目錄當 NEW5
- GREEN: 試體根 `scripts/fixtures/five-station-f3/new5/cut-ok/`

### T-6 / S-3.3
- RED: 只用字當成功
- GREEN: GRAPH-WORD-NE 該格紅

### T-6 / S-3.4
- RED: 刪 N7-g1／token
- GREEN: 節點檔在；`check-gate-tokens.sh` 綠

### T-7 / S-4.1
- RED: supported 無 2.1.0
- GREEN: `hooks/runtime-capabilities.json` 含 `2.1.0`

### T-7 / S-4.2
- RED: 漏加仍印 COMPATIBLE
- GREEN: DOCTOR-HONEST 印 INCOMPATIBLE 且非 0

### T-7 / S-4.3
- RED: 綠當 hop 票
- GREEN: DOCTOR-NE-TICKET 理由是路線

### T-7 / S-4.4
- RED: 改握手
- GREEN: `git diff --exit-code -- hooks/_doctor_impl.py`

### T-7 / S-4.5
- RED: marketplace 當第四前置
- GREEN: 閘丟棄 marketplace／cache

### T-8 / S-6.1
- RED: 謂詞真仍等人卻標成功
- GREEN: NEW5-WAIT-RED 該格紅

### T-8 / S-6.2
- RED: Must-keep 紅仍 hop
- GREEN: KEEP-MK-RED 具名六 M

### T-8 / S-6.3
- RED: 機械 Ship Done
- GREEN: KEEP-SHIP-MECH 該格紅

### T-8 / S-5.3
- RED: 拒 hop 記成紅格綠
- GREEN: `--probe polarity` exit 1

### T-9 / S-7.1
- RED: OLD7 被折五站
- GREEN: OLD7-FREEZE 無五站機

### T-9 / S-7.2
- RED: 對 in-flight 寫五站當綠
- GREEN: OLD7-FOLD-RED 該格紅

### T-9 / S-7.3
- RED: 本目錄自動五站
- GREEN: SELF-OLD7 三凍結 slug 跳不過

### T-9 / S-7.5
- RED: 發明活五站名字
- GREEN: 只寫合成 fixture；未點名第一隻活五站

### T-10 / S-5.1
- RED: 入口只轉 F2 或缺一路
- GREEN: 同一 process NEW5+OLD7+TOKEN

### T-10 / S-5.2
- RED: 減 Decision 原 20 列
- GREEN: 官方 25 名齊

### T-10 / S-5.4–S-5.6／S-5.9–S-5.11
- RED: hollow 當綠
- GREEN: `--group hollow -ge 6`；探針 exit 3

### T-10 / S-5.7
- RED: F2 回歸紅
- GREEN: F3-F2-REGRESS 地板 `failed=0`

### T-10 / S-5.8
- RED: token 被刪
- GREEN: TOKEN-KEEP；`check-gate-tokens.sh`

### T-10 / S-8.2–S-8.4
- RED: Files 超清單／刪 token
- GREEN: 准許清單內；TOKEN-DEL-RED 該格紅

### T-10 / S-8.1／S-8.5／S-8.6
- RED: 重開 4-spec／Q21–23 可選／F2 park
- GREEN: Covers gate；未改 4-spec 頂欄、未重開 park

## Decisions(spec 未載明的自由選擇)

- 讀端與電池放 `scripts/five_station_f3.py`，不改 `five_station_f2.py` 的 `contract_version`／`f3_cut_happened`。[Assumption] 改 F2 讀鍵會在 T-7 bump 後讓 F2 S-3.3 假紅；F2 恒 `False` 也保住 F2「本 hop 不切」。READ-SEAM 舊 reader 直接呼叫 F2。
- graph 預設 `next` 維持字串 `N7-g1`／`N6-g2`，另加 `next_when_five`。[Assumption] 既有 `check-devstage2-graph.sh`／`check-devstage4-graph.sh` 把 `next` 當字串與節點「下一跳」對帳；改成 map 會炸 P0。YAML 鍵名不鎖（5-tasks）。
- 可選 `scripts/check-five-station-f3.sh` 只印「不是電池入口」、exit 0。依據 4-spec DD-2／S-5.10。
- `frozen_slug` 只認 `/docs/dev/<slug>`，且 `/scripts/fixtures/` 一律假。[Assumption] NEW5 根路徑字面含 `five-station-f3`，若用 substring 會把合成 fixture 誤凍成 SELF-OLD7。

## Deviations

無。未動 R/S。未重開 F2 park。未發明 G3。

## Files Changed

對照 4-spec S-8.2 Diff Budget：

- `guides/guide-dev-flow.html`（T-6 七站單行 → 五站用語）
- `devflow-contract.json`（只 bump `devflow_contract_version` → `2.1.0`）
- `hooks/runtime-capabilities.json`（只加 `2.1.0`）
- `skills/dev-flow/stage2/graph.yaml`（`next_when_five`；不刪 N7-g1）
- `skills/dev-flow/stage4/graph.yaml`（`next_when_five`；不刪 N6-g2）
- `scripts/five_station_f3.py`
- `scripts/test-five-station-f3.sh`
- `scripts/check-five-station-f3.sh`（選配；非第四路）
- `scripts/fixtures/five-station-f3/`
- `docs/dev/f3-cut-attestation.json`（T-10）
- `docs/dev/five-station-f3/6-implementation-notes.md` + html

未改：`_templates/`、`hooks/_doctor_impl.py`、STATUS／HISTORY、`scripts/five_station_f2.py`、token 檔、`docs/dev/five-station-f2/` 已封 R／S、5-tasks checkbox。

## Diff(各 T commit,逐檔折疊)

### f3_cut_happened · `scripts/five_station_f3.py` f3_cut_happened  T-1
改什麼：只讀獨立三槽檔；缺檔／空槽／AND 捆進 which → False；不寫檔。
關聯：caller Battery.run_attest_visible／callee _read_json
```diff
 def f3_cut_happened(project_root):
+    path = Path(project_root) / "docs" / "dev" / "f3-cut-attestation.json"
+    if not (_nonempty_str(who) and _nonempty_str(when) and _nonempty_str(which)):
+        return False
+    if AND_IN_WHICH.search(which):
+        return False
+    return True
```

### contract_version · `scripts/five_station_f3.py` contract_version  T-3
改什麼：只讀 `devflow_contract_version`，無 fallback 錯鍵。
關聯：caller declared／READ-SEAM／callee _read_json
```diff
 def contract_version(project_root):
+    val = blob.get("devflow_contract_version")
+    return str(val) if val is not None else ""
```

### allow_legacy · `scripts/five_station_f3.py` allow_legacy  T-4
改什麼：三前置 AND；doctor／marketplace／cache 丟棄；缺一 → legacy。
關聯：caller refuse_hop_reason／graph_next
```diff
 def allow_legacy(project_root, slug_dir, doctor_green=False, ...):
+    _ = (doctor_green, marketplace_updated, cache_has_hops)
+    if dec and (not flying) and cut:
+        return False, "five"
+    return True, "legacy"
```

### refuse_hop_reason · `scripts/five_station_f3.py` refuse_hop_reason  T-4
改什麼：拒因咬缺的那一條；必含 `F3 cut 未發生`；禁「已宣告所以切了」。
關聯：caller Battery.run_pre_210／run_pre_and
```diff
 def refuse_hop_reason(project_root, slug_dir, doctor_green=False):
+    if not declared(project_root):
+        return "路線未宣告 仍舊 7"
+    if has_old7(slug_dir):
+        return "仍舊 7 in-flight"
+    if not f3_cut_happened(project_root):
+        return "仍舊 7 F3 cut 未發生"
```

### graph_next · `scripts/five_station_f3.py` graph_next  T-5
改什麼：預設 `next` 仍例行閘；`next_when_five` 只在三前置真時生效。
關聯：caller Battery.run_cut_ok／run_pre_hops_200
```diff
 def graph_next(graph_path, from_node, project_root, slug_dir):
+    default = fields.get("next", "")
+    skip = fields.get("next_when_five", "")
+    if (not legacy) and skip:
+        return skip
+    return default
```

### S6-selfcheck next_when_five · `skills/dev-flow/stage2/graph.yaml` S6-selfcheck  T-5
改什麼：條件邊跳過 N7-g1；預設 next 字串不變。
關聯：callee graph_next
```diff
   S6-selfcheck:
     next: N7-g1
+    next_when_five: N8-end
```

### S5-gate next_when_five · `skills/dev-flow/stage4/graph.yaml` S5-gate  T-5
改什麼：條件邊跳過 N6-g2；預設 next 字串不變。
關聯：callee graph_next
```diff
   S5-gate:
     next: N6-g2
+    next_when_five: N7-end
```

### guide five-station wording · `guides/guide-dev-flow.html` flow-lead  T-6
改什麼：七站單行改五站用語（交付物 ≠ SoT）。
關聯：Battery.run_graph_word_ne
```diff
-  <p class="lead">這章要你懂:<strong>七站單行,只有 G1 / G2 / G3 會被人擋</strong>。
+  <p class="lead">這章要你懂:<strong>五站單行,只有 Ship 會被人擋</strong>。
```

### contract bump · `devflow-contract.json` devflow_contract_version  T-7
改什麼：正本鍵 bump 到 2.1.0。
關聯：doctor handshake／declared
```diff
- "devflow_contract_version": "2.0.0",
+ "devflow_contract_version": "2.1.0",
```

### supported 2.1.0 · `hooks/runtime-capabilities.json` supported_contract_versions  T-7
改什麼：supported 只加 2.1.0；不改握手實作。
關聯：devflow-doctor.sh
```diff
   "supported_contract_versions": [
     "2.0.0",
+    "2.1.0"
   ],
```

### live cut attestation · `docs/dev/f3-cut-attestation.json`  T-10
改什麼：T-10 才寫活樹三槽；which_condition=f3-cut。
關聯：f3_cut_happened
```diff
+{
+  "who": "rick",
+  "when": "2026-09-14T00:00:00+08:00",
+  "which_condition": "f3-cut"
+}
```

### Battery.case · `scripts/five_station_f3.py` Battery.case  T-10
改什麼：只印官方 25 名；發明名直接 FATAL。
關聯：test-five-station-f3.sh
```diff
 def case(self, name):
+    if name not in OFFICIAL:
+        raise SystemExit("FATAL: invented CASE name %s" % name)
+    print("=== CASE %s" % name)
```

## Self-Review

①每個「T × Covers S」都有含 S-id 的測試 + 該 T 自己的 RED/GREEN 證據（見 TDD Evidence；未跨 T 共用）？是（implementer 自檢；獨立審未過）。
②每 T 在 T Review Log 有 verdict？有：一律 PENDING_INDEPENDENT_REVIEW（不得自填 ACCEPTED）。
③每個 PASS 都早於該 T commit？n-a：無 PASS。
④每個 FAIL 後有較晚 PASS？n-a：尚無獨立 FAIL。
⑤每個已完成 T 一 commit、Progress Log 每列有 hash？未勾 checkbox；Progress Log 空（等獨立審）。
⑥git diff --stat 檔案 ⊆ Files 聯集、Diff Budget 內？是（S-8.2 准許清單）。
⑦Decisions/Deviations 與 diff 對得上？是；無 silent drift；DBC applicable：未改握手／未刪節點／未重開 park。
⑧回歸綠？F2 地板＋F3 電池待本 branch 實跑（見 Verify）；未發明 G3。

## Review Follow-up(G3 打回時才用)

n-a:未送 G3。
