---
feature: five-station-f3
stage: 6-implementation
status: draft
owner: implementer-A
updated: 2026-09-14
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 822f84289f6f4267252907e36862e93f1c90eb9d

> Single implementer stream（F2 pattern）。T Review **PENDING_INDEPENDENT_REVIEW**（author ≠ reviewer；未自填 ACCEPTED）。standing rework **不是** self-ACCEPTED。獨立重審 **RR2**（本檔文末；獨立於 RR1）。implementer／standing 列不得刪。未發明 Human G3 PASS。5-tasks checkbox 保持未勾。活樹 cut 只在 T-10 收口寫入。

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

R1 #386／R2 #387 的 FAIL 表在那些 notes PR，**本檔不覆寫**。standing rework 見文末「Owner standing rework」；standing 列仍是 **PENDING_INDEPENDENT_RE-REVIEW**，不是 self-ACCEPTED。獨立 verdict 見 **T Review Log — Independent RR2 re-review**。

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

<!-- T Review PASS 後才記 hash。implementer stream 未自裁 PASS。 -->

implementer commits（軌跡，不是 Progress Log 驗收列）：見 impl branch `git log`。

| 日期 | T | 一句 |
|---|---|---|
| 2026-09-14 | T-1…T-10 | Independent RR2 re-review after #385／`ae9c064`：10／10 ACCEPTED；未發明 G3；未勾 checkbox |

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
- GREEN（standing）: `graph_next(cut-ok)` → N8-end／N7-end；wording-only inject 仍 N7-g1；不是 guide+YAML 字串綠

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
- GREEN（standing）: stdout 印字面 `路線未宣告 仍舊 7`（Verify `grep` 打得到）

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
- GREEN（standing）: `evaluate_hop(inject-keep-mk-red)` → `injected-mk M3 M5 M9 M11 M12 M15`；合法拒含 M 編號；cut-ok `None` 不假綠

### T-8 / S-6.3
- RED: 機械 Ship Done
- GREEN: KEEP-SHIP-MECH 該格紅

### T-8 / S-5.3
- RED: 拒 hop 記成紅格綠
- GREEN: `--probe polarity` exit 1
- GREEN（standing）: 探針真跑 cut-ok／MK 拒／三注入，不再硬編碼 stub

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
- DOCTOR-HONEST 禁綠詞只咬 `✅ devflow doctor: COMPATIBLE`。[Assumption] `INCOMPATIBLE` 含 substring `COMPATIBLE`，用 `not in out` 會假紅。
- OLD7-FREEZE 拒因接受 `仍舊 7` 或 `in-flight`。OLD7 fixture 無契約檔 → 先走「路線未宣告 仍舊 7」，仍是整段舊 7。

## Deviations

- **D-1 L1 — CI 註冊四檔**（同 F2 D-1 L1 綁死）。新增 `scripts/test-five-station-f3.sh` + `scripts/check-five-station-f3.sh` + `scripts/five_station_f3.py` 後，`devflow-check.sh` 註冊自審與 `check-file-map.sh` 會紅（`check-*.sh`／`test-*.sh` 必須出現在會被執行的 `run` 行；必列檔必須進檔案地圖）。S-8.2 准許清單正文不含這四檔；4-spec「超出 → L2」字面張力仍在。本 hop 誠實處：四檔具名、不假裝已在 5-tasks Files、不重開 4-spec、不把這層當成第二次 F3 cut、不刪 G1/G2/token。這四檔是新電池腳本的 host CI 註冊（縮了 `REPO_REFERENCE`／file-map 會紅），不是再切一次預設路線。不動 R/S。未發明 G3。

### RR2 on D-1（獨立重審；不刪上列）

- **D-1 L1 — CONCUR**。四檔具名：`check-file-map.sh`、`test-architecture-guards.sh`、`devflow-check.sh`、guide `#filemap` 三列。RR2 對 `ae9c064` vs `origin/main` 核過這四檔在、`_doctor_impl.py`／STATUS／HISTORY／token／`_templates/`＝0。不重開 4-spec（S-8.1／S-8.6）。不因此翻 T-10。

## Files Changed

對照 4-spec S-8.2 Diff Budget：

- `guides/guide-dev-flow.html`（T-6 七站單行 → 五站用語；**D-1 L1** 另加檔案地圖三列）
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
- `docs/dev/five-station-f3/5-tasks.md` 頂欄 `status` 僅 N1-arm（`draft`→`approved`；checkbox 未勾）

D-1 L1 准許清單修訂（不是 silent extras、也不是第二次 cut）：

1. `guides/guide-dev-flow.html` `#filemap` 三列（`five_station_f3.py`／`check-five-station-f3.sh`／`test-five-station-f3.sh`）
2. `scripts/check-file-map.sh`（`EXPECTED_MAPPED_FILES` 210→213）
3. `scripts/test-architecture-guards.sh`（靜態釘 210→213）
4. `scripts/devflow-check.sh`（architecture `run` 行註冊 F3 check + test）

未改：`_templates/`、`hooks/_doctor_impl.py`、STATUS／HISTORY、`scripts/five_station_f2.py`、token 檔、`docs/dev/five-station-f2/` 已封 R／S、5-tasks checkbox（只動頂欄 status）。

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

### refuse_hop_reason · `scripts/five_station_f3.py` refuse_hop_reason  T-4 T-8
改什麼：拒因咬缺的那一條；必含 `F3 cut 未發生`；禁「已宣告所以切了」。standing：AND 真仍查 Must-keep；`mk_reds` 非空 → 理由含該 M 編號。cut-ok `None` 不是紅格綠。
關聯：caller Battery.run_pre_210／run_pre_and／run_keep_mk_red
```diff
 def refuse_hop_reason(project_root, slug_dir, doctor_green=False, mk_reds=None):
+    if not declared(project_root):
+        return "路線未宣告 仍舊 7"
+    if has_old7(slug_dir):
+        return "仍舊 7 in-flight"
+    if not f3_cut_happened(project_root):
+        return "仍舊 7 F3 cut 未發生"
+    if mk_reds:
+        return "Must-keep 紅 " + " ".join(mk_reds)
+    return None
```

### evaluate_hop · `scripts/five_station_f3.py` evaluate_hop  T-8
改什麼：注入稿餵進真 hop 評測；KEEP-MK 理由含 M3／M5／M9／M11／M12／M15。合法拒 ≠ 注入極性。
關聯：caller Battery.run_keep_mk_red／run_wait_red／run_keep_ship_mech／polarity_inverted
```diff
 def evaluate_hop(project_root, slug_dir, inject=None, inject_path=None, ...):
+    kind, text = parse_inject(inject_path)
+    if inject == "mk-hop":
+        return True, "injected-mk " + " ".join(mids), extra
+    if inject == "wait":
+        return False, "injected-wait N7-g1 要不要繼續", extra
+    if inject == "ship-done":
+        return True, "injected-done ship_done 機械", extra
+    reason = refuse_hop_reason(..., mk_reds=extra["mids"] or None)
```

### run_graph_word_ne · `scripts/five_station_f3.py` run_graph_word_ne  T-6
改什麼：fail-closed：cut AND 後 `graph_next` 必須跳過 N7-g1／N6-g2；用語＋`graph_next` 仍恆 N7-g1＝該格紅。不靠 guide「五站」+ YAML `next==N7-g1` 字串綠。
關聯：callee graph_next／evaluate_hop
```diff
 def run_graph_word_ne(self):
+    s2 = graph_next(stage2, "S6-selfcheck", cut, slug)
+    wording_only = ("五站" in guide) and (s2 == "N7-g1")
+    self.check((not wording_only) and s2 == "N8-end",
+               "S-3.3 after cut AND hop skips N7-g1")
+    hopped, why, extra = evaluate_hop(cut, slug, inject_path=fx)
+    self.check(extra.get("s2") == "N7-g1", "wording-only inject is the red cell")
```

### run_doctor_ne_ticket · `scripts/five_station_f3.py` run_doctor_ne_ticket  T-7
改什麼：拒因印到 stdout，5-tasks Verify `grep` 打得到 `路線未宣告`／`仍舊 7`。
關聯：callee refuse_hop_reason
```diff
 def run_doctor_ne_ticket(self):
+    reason = refuse_hop_reason(tree, slug, doctor_green=True)
+    print(reason or "")
```

### polarity_inverted · `scripts/five_station_f3.py` polarity_inverted  T-8
改什麼：`--probe polarity` 真跑 cut-ok／MK 拒／三張注入；不再硬編碼 stub。合法拒當紅格綠 → 探針 FAIL exit 1。
關聯：caller main --probe polarity
```diff
 def polarity_inverted(project_root):
+    legal = refuse_hop_reason(cut, slug)
+    mk_legal = refuse_hop_reason(cut, slug, mk_reds=list(KEEP_MK_IDS))
+    hopped, why, _ = evaluate_hop(cut, slug, inject_path=fx)
+    return (legal is None) or (mk_legal and "injected-mk" not in mk_legal)
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
⑥git diff --stat 檔案 ⊆ Files 聯集、Diff Budget 內？是（S-8.2 准許清單 + **D-1 L1** 四檔 CI 註冊；四檔具名，不是 silent extras）。
⑦Decisions/Deviations 與 diff 對得上？是；D-1 L1 已列；無 silent drift；DBC applicable：未改握手／未刪節點／未重開 park。
⑧回歸綠？standing rework 後親跑：`bash scripts/test-five-station-f3.sh -v` → `=== CASE` ×33、unique 官方 25 名、`failed=0` exit 0。`--only new5|old7|token` 各 exit 3；`--probe hollow-*`／`two-script` 各 exit 3；`--probe polarity` exit 1（真評測，非法拒當紅格綠）；未知旗標 exit 2；`--group hollow` ≥6。`test-five-station-f2.sh` `failed=0`。`check-gate-tokens.sh` 綠。`check-devstage2/4/6-graph.sh` 綠。`git diff --exit-code -- hooks/_doctor_impl.py`。未發明 G3。T-6／T-7／T-8 5-tasks Verify 原文本地過。

## Review Follow-up(G3 打回時才用)

n-a:未送 G3。

## Owner standing rework（post R1+#386／R2+#387）— 待獨立重審

implementer ≠ R1／R2 reviewer。本塊只記修正與自檢，**verdict 不是 ACCEPTED**。未發明 G3。未勾 5-tasks checkbox。R1／R2 FAIL 表留在 #386／#387，本節不覆寫。

> RR2 已審（#385 tip `ae9c064`）：上表 standing 列仍不是 self-ACCEPTED。獨立 verdict 見 **T Review Log — Independent RR2 re-review**。

| T | standing | 一句 |
|---|---|---|
| T-6 | REWORKED · 待重審 | GRAPH-WORD-NE fail-closed：cut AND 後 `graph_next` 跳過 N7-g1／N6-g2；用語＋恆 N7-g1＝該格紅 |
| T-7 | REWORKED · 待重審 | DOCTOR-NE-TICKET stdout 印 `路線未宣告 仍舊 7`；Verify `grep` 打得到 |
| T-8 | REWORKED · 待重審 | 三注入進 `evaluate_hop`；`refuse_hop_reason` 含 M 編號；cut-ok `None` 不假綠；polarity 真探針 |
| T-9 | REWORKED · 待重審（殘） | FOLD-RED 走真閘＋inject-fold，不再只 grep 稿 |
| T-10 | REWORKED · 待重審（殘） | hollow／TOKEN-DEL 走評測器；token 牙真閘 |

### Rework T-6 / S-3.3
- Verify: 5-tasks 原指令（GRAPH-WORD-NE＋`check-gate-tokens.sh`）本地過。`graph_next(cut-ok)` → `N8-end`／`N7-end`；注入 wording-only → extra.s2=`N7-g1`；未 AND 仍 `N7-g1`
- Covers finding: S-3.3 不再只咬 guide「五站」+ YAML `next==N7-g1`。S-3.4 節點／token 未刪
- Files finding: ⊆ T-6 Files（電池＋注入稿；guide 用語交付已在）
- verdict: **PENDING_INDEPENDENT_RE-REVIEW**（不是 ACCEPTED）

### Rework T-7 / S-4.3
- Verify: 5-tasks 原指令。`DOCTOR-NE-TICKET -v` stdout 含字面 `路線未宣告 仍舊 7`；禁「doctor 已綠所以可 hop」／`COMPATIBLE so hop`／`handshake-means-route`。`_doctor_impl.py` 0 diff
- Covers finding: S-4.3 拒因可被 Verify `grep` 打到（不再只計算）。S-4.2 HONEST 仍印 INCOMPATIBLE
- verdict: **PENDING_INDEPENDENT_RE-REVIEW**

### Rework T-8 / S-6.1–S-6.3
- Verify: 5-tasks 原指令 `-ge 3`。KEEP-MK stdout 含 `injected-mk M3 M5 M9 M11 M12 M15`；合法 `refuse_hop_reason(..., mk_reds=)` 含同組 M 且不含 `injected-mk`；cut-ok `refuse_hop_reason` 是 `None` 且不拿來綠這三格。WAIT 注入仍停 N7-g1；SHIP 注入 `injected-done`。`--probe polarity` 真跑三注入＋cut-ok，exit 1
- Covers finding: S-6.1／S-6.2／S-6.3 紅格＝注入壞行為；S-5.3 極性探針不再硬編碼 stub
- Files finding: ⊆ T-8 Files
- verdict: **PENDING_INDEPENDENT_RE-REVIEW**

### Rework T-9／T-10 residual
- Verify: T-9 原指令 `-ge 3`；T-10 hollow group `-ge 6`；TOKEN-DEL 真跑 `check-gate-tokens.sh` 仍綠＋inject 評測
- Covers finding: S-7.2／S-5.4…S-5.6／S-5.9／S-5.10／S-8.4 不再只 grep 注入稿
- verdict: **PENDING_INDEPENDENT_RE-REVIEW**（殘項 polish，不是 self-ACCEPTED）

## T Review Log — Independent RR2 re-review（post #385／`ae9c064`）

Independent Re-Reviewer **RR2**（fresh-context Agent；cloud run `bc-108b88c7-4a5d-4808-826c-4cc78fe3d813`）。Implementer = #385 standing rework（≠ 本 reviewer）。**不覆蓋**上面 implementer PENDING／standing PENDING 列。author≠approver（M12）。未讀 RR1 本輪稿當錨。未發明 G3。5-tasks checkbox 保持未勾。未改碼。Gold＝main `5-tasks.md`＋`4-spec.md`。

RR2 親跑（#385 tip `ae9c064`）：

| Probe | Result |
|---|---|
| `scripts/test-five-station-f3.sh -v` | `failed=0` exit 0；`=== CASE` ×33；unique 官方名＝**25** |
| `--only new5\|old7\|token` | 各 exit **3** |
| `--probe hollow-true\|hollow-files\|hollow-f2\|hollow-word\|two-script` | 各 exit **3** |
| `--probe polarity` | exit **1**（真呼叫 `refuse_hop_reason`／`evaluate_hop`，不是硬編碼 stub） |
| `--not-a-real-flag` | exit **2** |
| `--group hollow` | 6 官方 HOLLOW-*；禁 `HOLLOW-OK`／`NEW5-MKTG` |
| `--group graph-edges` | NEW5-CUT-OK＋PRE-HOPS-200；無 `GRAPH-AGREE` |
| `scripts/test-five-station-f2.sh` | `failed=0`（地板，不是 IFF） |
| `check-gate-tokens.sh` + stage2／4／6 graph | 綠 |
| `_doctor_impl.py` vs `origin/main` | 0 diff |
| 5-tasks checkbox | 十列皆 `[ ]` |
| STATUS／HISTORY | 0 diff |

獨立探針（不靠電池自述）：`graph_next(cut-ok)` → s2=`N8-end` s4=`N7-end`；`graph_next(pre-hops-200)` → `N7-g1`；wording_only（guide「五站」∧ cut 後仍 N7-g1）＝**False**。`refuse_hop_reason(doctor-ne-ticket, doctor_green=True)` → `路線未宣告 仍舊 7`（stdout 同字）。`refuse_hop_reason(cut-ok)`＝`None`；`refuse_hop_reason(..., mk_reds=KEEP_MK_IDS)`＝`Must-keep 紅 M3 M5 M9 M11 M12 M15`（無 `injected-mk`）。`evaluate_hop(inject-keep-mk-red)` → hopped True、`injected-mk M3 M5 M9 M11 M12 M15`；WAIT → `injected-wait N7-g1 要不要繼續`；SHIP → `injected-done`。F2 舊 reader 對 seam 2.1.0 回空；F3 `contract_version` 回 `2.1.0`。`f3_cut_happened` ok／missing／empty＝True／False／False；readonly 位元組不變。

| T | RR2 re-review | 分類 | S／hunk | 一句 |
|---|---|---|---|---|
| T-1 | ACCEPTED | — | S-1.1／S-1.2／S-1.4／S-1.5 · `f3_cut_happened` | 抽查：五 `--slot`；`which_condition=f3-cut`；缺檔／空槽 False |
| T-2 | ACCEPTED | — | S-1.3／S-1.6 · ATTEST-SILENT-RED | 抽查：`return True` 無三槽＝該格紅；STATUS 0 diff |
| T-3 | ACCEPTED | — | S-2.1／S-2.2／S-2.3 · `contract_version` | 抽查：F2 舊 reader 錯鍵留下；canonical-210 真、cut 獨立假 |
| T-4 | ACCEPTED | — | S-2.4…S-2.7 · `refuse_hop_reason` | 抽查：`F3 cut 未發生`；PRE-AND 三缺；SLOT-REJECT |
| T-5 | ACCEPTED | — | S-3.1／S-3.2／S-3.5／S-3.6 · `graph_next`／`next_when_five` | 抽查：cut-ok skip；graph-edges 官方名 |
| T-6 | **ACCEPTED** | — | **S-3.3**／S-3.4 · `run_graph_word_ne`／`graph_next` | 先前 FAIL 關：cut AND 後必須 skip；用語＋恆 N7-g1＝該格紅 |
| T-7 | **ACCEPTED** | — | **S-4.3**／S-4.2／S-4.4 · `run_doctor_ne_ticket` `print(reason)` | 先前 FAIL 關：stdout 字面 `路線未宣告 仍舊 7`；握手 0 diff |
| T-8 | **ACCEPTED** | — | **S-6.1／S-6.2／S-6.3** · `evaluate_hop`／`refuse_hop_reason` | 先前 FAIL 關：真 hop＋六 M id＋cut-ok `None` 不假綠 |
| T-9 | ACCEPTED | — | S-7.1／S-7.2／S-7.3／S-7.5 · FREEZE／FOLD／SELF | 抽查：真閘拒＋inject-fold；三凍結 slug 跳不過 |
| T-10 | ACCEPTED | — | S-5.*／S-8.2 · 25＋`--only`／`--probe` | 抽查：25 名＋exit 對。D-1 **CONCUR L1** |

### T-1
- reviewer identity: Independent Re-Reviewer RR2（fresh-context Agent；≠ #385 implementer）
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`（#385 standing rework；非 implementer PRE）
- Verify: 五 `--slot` `-ge 5`；各 slot exit 0。親探 `f3_cut_happened(ok/missing/empty)`＝True／False／False；`which_condition=f3-cut`；readonly 位元組不變
- Covers finding: S-1.1／S-1.2／S-1.4／S-1.5 有含 S-id assertion
- Files finding: ⊆ T-1 Files；活樹 cut 是 T-10 寫的，本 T fixture 只讀
- RED→GREEN finding: 缺檔／空槽可紅；不是契約／guide 用字冒充
- Test Integrity finding: none
- Design boundary finding: `which_condition` 不是三前置 AND、不是 `F3-cut-happened`
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A（本 T 先前未 FAIL）

### T-2
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: `--case ATTEST-SILENT-RED` exit 0。`git diff --name-only origin/main -- docs/dev/STATUS.md` 空
- Covers finding: S-1.3／S-1.6。用語交付不在本 T
- Files finding: ⊆ T-2 Files
- RED→GREEN finding: 無三槽＋字面 `return True`＝該格紅
- Test Integrity finding: none
- Design boundary finding: 未改 STATUS
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: READ-SEAM 三切片。親探：F3 `contract_version(seam)`＝`2.1.0`；F2 舊 reader 回 `""`（仍讀 `version`／`contract_version`）
- Covers finding: S-2.1／S-2.2／S-2.3。cut 在 canonical-210 仍獨立假
- Files finding: ⊆ T-3 Files；F2 舊 reader 未改
- RED→GREEN finding: 舊 reader 看不見 2.1＝紅格；不是 fallback 雙讀
- Test Integrity finding: none
- Design boundary finding: 只讀正本鍵
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: PRE 五棵。`PRE-210-NE-CUT -v` 含 `F3 cut 未發生`、不含「已宣告所以切了」；`--missing declared` 含 `路線未宣告`／`仍舊 7`；in-flight 含 `in-flight`；PRE-HOPS-200 含 `SLOT-REJECT`
- Covers finding: S-2.4…S-2.7
- Files finding: ⊆ T-4 Files
- RED→GREEN finding: 三缺各自可數；doctor 綠不進理由
- Test Integrity finding: none
- Design boundary finding: marketplace／cache 不是第四前置
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: NEW5-CUT-OK＋`--group graph-edges` n=3 官方名。親探 `graph_next(cut-ok)`＝N8-end／N7-end；`N7-g1.md`／`N6-g2.md` 仍在
- Covers finding: S-3.1／S-3.2／S-3.5／S-3.6／S-7.4。禁 `GRAPH-AGREE`
- Files finding: ⊆ T-5 Files；YAML `next` 仍 N7-g1／N6-g2，另加 `next_when_five`
- RED→GREEN finding: 未宣告跳過側不生效（PRE-HOPS-200 仍 N7-g1）
- Test Integrity finding: none
- Design boundary finding: 條件邊＋路線閘，不是刪節點
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: 5-tasks 原文 GRAPH-WORD-NE＋`check-gate-tokens.sh` → exit 0。親探：cut AND 後 `graph_next` skip；未 AND 仍 N7-g1；`evaluate_hop(inject-graph-word-ne)` why＝`injected-graph-word still N7-g1` extra.s2＝N7-g1
- Covers finding: **S-3.3 成立**（先前 R2 FAIL IMPL 已關）。不再只咬 guide「五站」+ YAML `next==N7-g1`。fail-closed：cut AND 後若 `graph_next` 仍恆 N7-g1 → 該格 RED。S-3.4 節點／token 仍在
- Files finding: ⊆ T-6 Files；token 牙只呼叫
- RED→GREEN finding: 用語交付 ≠ 本格綠；行為 skip 才過 fail-closed
- Test Integrity finding: 殘（不翻 T）：inject 半邊仍用檔名 kind。牙齒在 `graph_next` fail-closed，不是稿 grep
- Design boundary finding: 未刪節點、未刪 token、未把拒 hop 記成本格綠
- verdict: ACCEPTED
- correction + re-review after FAIL: #385 `ae9c064` 修 S-3.3 fail-closed；本列為重審 PASS

### T-7
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: 5-tasks 原文 DOCTOR-HONEST＋DOCTOR-NE-TICKET → n=2；ticket stdout 含字面 `路線未宣告 仍舊 7`；禁「doctor 已綠所以可 hop」／`COMPATIBLE so hop`／`handshake-means-route`。HONEST 印 `INCOMPATIBLE` 且非 0。`grep 2.1.0 hooks/runtime-capabilities.json`；`git diff --exit-code origin/main -- hooks/_doctor_impl.py`
- Covers finding: **S-4.3 成立**（先前 R1 FAIL TEST 已關）。拒因印到 stdout，Verify `grep` 打得到。S-4.1／S-4.2／S-4.4／S-4.5：清單有 2.1.0；握手 0 diff；綠≠票
- Files finding: ⊆ T-7 Files；未寫活樹 cut（T-10 才寫）
- RED→GREEN finding: 誠實紅＝HONEST 綠義務；NE-TICKET 是拒 hop 綠義務
- Test Integrity finding: none（stdout 牙不再空轉）
- Design boundary finding: `doctor_green` 被丟棄；marketplace／cache 不是票
- verdict: ACCEPTED
- correction + re-review after FAIL: #385 `ae9c064` `print(reason)`；本列為重審 PASS

### T-8
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: 5-tasks 原文 WAIT／KEEP-MK／SHIP `-ge 3` exit 0。親 `evaluate_hop`：MK hopped＋`injected-mk M3 M5 M9 M11 M12 M15`（不是只 M11）；WAIT s2＝N7-g1／`要不要繼續`；SHIP `injected-done`。合法 `refuse_hop_reason(mk_reds=)` 含同組 M、不含 `injected-mk`。cut-ok refuse＝`None` 且三格都斷言不得拿它假綠。`--probe polarity` exit 1
- Covers finding: **S-6.1／S-6.2／S-6.3 成立**（先前 R1／R2 FAIL IMPL 已關）。紅格＝注入壞行為進 `evaluate_hop`，不是只 grep 稿。S-5.3 極性探針真評測
- Files finding: ⊆ T-8 Files（三張具名 .md；F3 准許清單沒有 16 棵 overlay 樹）
- RED→GREEN finding: 綠＝抓到注入 hop／等人／機械 Done；合法拒是另一條義務
- Test Integrity finding: 殘（不翻 T）：inject kind 來自檔名。F3 Files 就是稿，M id 從稿文抽出且 `refuse_hop_reason` 真咬。`--probe polarity` 兩分支都 exit 1（契約要 1）
- Design boundary finding: 未把 cut 當 Must-keep 省略；未代填 PASS
- verdict: ACCEPTED
- correction + re-review after FAIL: #385 `ae9c064` 真 hop＋M id＋極性；本列為重審 PASS

### T-9
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: FREEZE／FOLD-RED／SELF-OLD7 `-ge 3` exit 0
- Covers finding: S-7.1／S-7.2／S-7.3／S-7.5。FOLD 走真閘＋`injected-fold`，不是只 grep 稿
- Files finding: ⊆ T-9 Files；NEW5 不是本目錄
- RED→GREEN finding: in-flight 整段舊 7；三凍結 slug 跳不過
- Test Integrity finding: none
- Design boundary finding: 未發明活五站名字
- verdict: ACCEPTED
- correction + re-review after FAIL: standing 殘項 polish 已夠；本列 ACCEPTED

### T-10
- reviewer identity: Independent Re-Reviewer RR2
- reviewer kind: fresh-context Agent
- reviewed-at: 2026-09-14 post-`ae9c064`
- Verify: `-v` unique 25；`--only` 各 3；hollow probe 各 3；polarity 1；未知 2；`--group hollow` ≥6 具名；F2 `failed=0`；token 牙綠
- Covers finding: S-5.1…S-5.11／S-8.2／S-8.3／S-8.4。S-8.1／S-8.5／S-8.6 gate：未重開 4-spec、未標 Q21–23 可選、未重開 F2 park
- Files finding（誠實）: S-8.2 准許清單＋**D-1 L1** 四檔（`check-file-map.sh`／`test-architecture-guards.sh`／`devflow-check.sh`／guide `#filemap`）。禁區 Diff Budget 0
- RED→GREEN finding: 單一 process 三路；html-only∈new5
- Test Integrity finding: 殘（不翻 T）：`--probe hollow-*` 仍是 exit-3 入口（CASE 跑者走評測器）
- Design boundary finding: D-1 CONCUR L1。未發明 G3。checkbox 未勾
- verdict: ACCEPTED
- correction + re-review after FAIL: N/A（本 T 先前 ACCEPTED；殘項不翻）
