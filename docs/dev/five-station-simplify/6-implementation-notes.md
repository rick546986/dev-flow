---
feature: five-station-simplify
stage: 6-implementation
status: draft
owner: implementer-A
updated: 2026-09-14
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: f3f28bdb183c3d0e1ccbecd7e6cde261e7679c62

## 0. 起手

### 0a branch／錨點

- 只讀 4-spec／5-tasks／本檔／living。禁讀 1／2／3。
- `git fetch origin main` → `FORK=f3f28bdb183c3d0e1ccbecd7e6cde261e7679c62`
- `git switch -c cursor/five-station-simplify-f1-d64f "$FORK"`
- `test "$(git rev-parse HEAD)" = "$FORK"` → 通過

### 0b worktree 隔離

n-a:本 feature 未並行。單一 checkout、無第二 worktree；不改 STATUS；無另開容器／DB／queue。

### 0c 守衛與 doctor

```
✅ 執行守衛啟動:five-station-simplify
scope(6 項):
  notes/design/five-station-simplify-f1-dual-read-annex.md
  notes/design/five-station-simplify-f1-rp-min-set.md
  scripts/check-five-station-f1.sh
  scripts/five_station_f1.py
  scripts/fixtures/five-station-simplify/
  scripts/test-five-station-f1.sh
run_id=run_01M2EKHH78QSHRFAG2QAVSCJFN
slug=five-station-simplify started=2026-09-14T00:02:18 scope=6 extra=0 sentinel=在
✅ devflow doctor: COMPATIBLE
```

## T Review Log

獨立 T review **未做**。implementer 自檢只標 PRE，不得當最終 PASS。5-tasks checkbox 保持未勾。

### T-1
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self（非獨立）
- reviewed-at: 2026-09-14 PRE
- Verify: `n=$(bash scripts/test-five-station-f1.sh --group rp16 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 2 && bash scripts/test-five-station-f1.sh --group rp16` → n=2；failed=0
- Covers finding: S-3.1 Agent 代寫紅、人類 attestation 不誤殺
- Files finding: 牙骨架＋RP-16 列＋兩份對照稿，未出聯集
- RED→GREEN finding: 5-tasks 開工前腳本不存在＝RED；本 T Verify 綠
- Test Integrity finding: none（自檢；待獨立審）
- Design boundary finding: 未改 hooks／模板／graph；未鎖鍵名
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group slots` → n=2；failed=0（完整 annex 綠；缺 SLOT-DOCTOR-GREEN-MEANS 紅）
- Covers finding: S-5.8 九槽可指到
- Files finding: dual-read annex + 牙加厚
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未把 SLOT 寫成必填 schema 鍵
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group dual-read` → n=5；failed=0
- Covers finding: S-5.4 缺新欄不紅；S-5.5／S-5.6 doctor 綠≠已切／不得跟 hops；S-5.7／S-5.9 2.0.0+五站 hops 仍舊 7
- Files finding: annex + 牙 + fixtures
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未改 doctor 握手
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group inflight` → n=3；failed=0
- Covers finding: 有 md 凍＋拒 hop（RP-15）；僅 html → in_flight=false
- Files finding: 未改 graph.yaml、未寫五站狀態進本 slug
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 只釘偵測布林
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group rp1` → n=2；failed=0
- Covers finding: S-2.2 缺欄／「看起來沒問題」→ RP-1
- Files finding: 未改 5-tasks 模板
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 紅在卡上，未延後 Ship
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group seam` → n=3；failed=0
- Covers finding: S-2.3 無 RED／自審；S-2.9 摘要無原始輸出
- Files finding: 牙 + rp-min-set + fixtures
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未把自審寫成可選
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-7
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group spec-name` → n=3；failed=0；`c4_fail=True`（實呼 `check-spec-gate.sh`）
- Covers finding: S-2.4 接 C4；S-2.5 `test_store_half_slot` 紅
- Files finding: 未把 check-spec-gate.sh 列入 Files、未改 C4 詞表
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 無第二模糊詞家族
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group brief-files` → n=3；failed=0
- Covers finding: S-2.1 少 M11；S-2.7 可選句；S-2.8 Files 超聯集
- Files finding: 未改 _templates/
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未把 M 標可選
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-9
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: 四張具名檔存在 + `--group attest` n=5；failed=0
- Covers finding: RP-13／12／14、S-4.5、S-1.7 demo_page=false
- Files finding: 未改 `_stage3_impl.py`
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: chat 不是 attestation
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group ship-quiz` → n=4；failed=0
- Covers finding: RP-7、可逆強制 Quiz、RP-8、S-3.3 八點
- Files finding: 未改 7-review 模板
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未實作 coordinator HumanWait
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-11
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: 三張超 cap 具名檔 + `--group rp-min-set` n=17；failed=0
- Covers finding: RP-1…16 各紅一次；刪 RP-8 annex → S-2.6
- Files finding: rp-min-set annex 列齊 16
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未實作 F2 計數器、未鎖 event 鍵
- verdict: PRE
- correction + re-review after FAIL: N/A

### T-12
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: 五張 reopen 具名檔 + `T-12-no-reopen` + `--group f1-close` n=10 ≥9；failed=0
- Covers finding: 七舊名／token／Files 閉聯集／Q6 open／五張已拒案紅
- Files finding: 未越六條聯集
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未 bump 契約、未改 STATUS
- verdict: PRE
- correction + re-review after FAIL: N/A

## Progress Log

<!-- 獨立 review PASS 後才記正式 hash。下列是實作 commit，不是 T review PASS。 -->

| 日期 | T-id | 一行 |
|---|---|---|
| 2026-09-14 | T-1…T-12 | 3c8d718 實作落地（review=PRE，非正式 PASS） |

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)

Run: n-a（sequential 手動；無 exec-v2 run_id 事件）

## TDD Evidence

RED 共用基準（5-tasks「Verify 開工前原樣跑」2026-09-14）：`scripts/test-five-station-f1.sh` 不存在 → 十二欄皆非零。

### T-1 / S-3.1
- RED: 腳本不存在 → 非零
- GREEN: `--group rp16` → `=== CASE` ×2；`failed=0`；Agent `verdict: PASS` → RP-16；人類 attestation 不紅

### T-2 / S-5.8
- RED: 腳本不存在 → 非零
- GREEN: `--group slots` ×2；完整 annex `slots_ok=True`；`slots-missing-one.md` → `RED S-5.8 缺 SLOT: SLOT-DOCTOR-GREEN-MEANS`

### T-3 / S-5.4
- RED: 腳本不存在 → 非零
- GREEN: `dual-old7-missing-new5.md` red=False；`missing_new5_legal=True`

### T-3 / S-5.5
- RED: 腳本不存在 → 非零
- GREEN: `dual-doctor-green-means-cut.md` → `RED S-5.5`

### T-3 / S-5.6
- RED: 腳本不存在 → 非零
- GREEN: `dual-doctor-follow-hops.md` → `RED S-5.6 doctor 綠不得跟 hops`

### T-3 / S-5.7
- RED: 腳本不存在 → 非零
- GREEN: `dual-200-plus-five-hops.md` → `RED S-5.7`；`route=old-7`

### T-3 / S-5.9
- RED: 腳本不存在 → 非零
- GREEN: `dual-hops-first-then-contract.md` → 同 S-5.7；任一寫入順序仍舊 7

### T-4 / S-5.1
- RED: 腳本不存在 → 非零
- GREEN: `inflight-has-md.md` → RP-15；`in_flight=True`

### T-4 / S-5.2
- RED: 腳本不存在 → 非零
- GREEN: `inflight-this-slug-five-hop.md` → RP-15；`hop_blocked=True`

### T-4 / S-5.3
- RED: 腳本不存在 → 非零
- GREEN: `inflight-html-only.md` red=False；`in_flight=False`

### T-5 / S-2.2
- RED: 腳本不存在 → 非零
- GREEN: `--group rp1` ×2；缺欄／`看起來沒問題` → RP-1

### T-6 / S-2.3
- RED: 腳本不存在 → 非零
- GREEN: `rp-02-no-red.md`／`rp-02-self-review.md` → RP-2

### T-6 / S-2.9
- RED: 腳本不存在 → 非零
- GREEN: `rp-06-summary-only.md` → RP-6

### T-7 / S-2.4
- RED: 腳本不存在 → 非零
- GREEN: `rp-03-vague-tbd.md` → RP-3 且 `c4_fail=True`（呼叫既有 C4）；不可測句 → RP-3

### T-7 / S-2.5
- RED: 腳本不存在 → 非零
- GREEN: `test_store_half_slot` → RP-4

### T-8 / S-2.1
- RED: 腳本不存在 → 非零
- GREEN: `brief-missing-must-keep.md` → S-2.1

### T-8 / S-2.7
- RED: 腳本不存在 → 非零
- GREEN: `brief-optional-four-fields.md` → S-2.7

### T-8 / S-2.8
- RED: 腳本不存在 → 非零
- GREEN: `rp-05-files-outside-union.md` → RP-5（`hooks/_stage3_impl.py`、`graph.yaml`）

### T-9 / S-4.1
- RED: 腳本不存在 → 非零
- GREEN: 人類兩行在的對照屬 T-1 正向；本群組以空欄／強迫／請人審／否定跳過為負向

### T-9 / S-4.2
- RED: 腳本不存在 → 非零
- GREEN: `rp-13-empty-attestation-plus-chat.md` → RP-13；`leave_spec=False`

### T-9 / S-4.3
- RED: 腳本不存在 → 非零
- GREEN: `rp-12-miss-forced-accepted.md` → RP-12

### T-9 / S-4.4
- RED: 腳本不存在 → 非零
- GREEN: `rp-14-please-review-latch-false.md` → RP-14

### T-9 / S-4.5
- RED: 腳本不存在 → 非零
- GREEN: `skip-negation-as-oc.md` → S-4.5；`skip_oc=False`

### T-9 / S-1.7
- RED: 腳本不存在 → 非零
- GREEN: 同一 miss fixture → `demo_page=False`

### T-10 / S-1.10
- RED: 腳本不存在 → 非零
- GREEN: 不可逆無 Quiz → RP-7；可逆強制 Quiz → S-1.10

### T-10 / S-3.2
- RED: 腳本不存在 → 非零
- GREEN: `rp-08-done-without-pass.md` → RP-8

### T-10 / S-3.3
- RED: 腳本不存在 → 非零
- GREEN: `s-3-3-evidence-omit-eight.md` → S-3.3

### T-11 / S-2.6
- RED: 腳本不存在 → 非零
- GREEN: `--group rp-min-set` ×17；RP-1…16 各紅；`rp-min-set-delete-rp8.md` → `少 RP: RP-8`

### T-12 / S-1.1
- RED: 腳本不存在 → 非零
- GREEN: live `seven_old_count=5`；`new_family=False`；G1／G2／ACCEPTED token 仍在

### T-12 / S-6.2
- RED: 腳本不存在 → 非零
- GREEN: live `q6_open=True` 且未對 4-spec 誤紅 S-6.3

### T-12 / S-6.3
- RED: 腳本不存在 → 非零
- GREEN: `q6-as-fact.md` → S-6.3

### T-12 / S-8.1
- RED: 腳本不存在 → 非零
- GREEN: 有 annex／scripts 牙；diff 無 graph 切線、無 coordinator

### T-12 / S-8.5
- RED: 腳本不存在 → 非零
- GREEN: live `files_closed=True`

### T-12 / S-8.6
- RED: 腳本不存在 → 非零
- GREEN: 五張 `reopen-*.md` → S-8.6；5-tasks 無 `改採 [12467][BC]`

## Decisions(spec 未載明的自由選擇)

- 單一檢查家族 `check-five-station-f1` + `five_station_f1.py` kind 分派：對照稿用 `f1-kind`／檔名前綴選規則包，避免 annex 正文提到「doctor exit 0 所以可以跟 hops 走」被自己誤殺。依據：S-8.1 一家族；OC-3 不鎖鍵。
- fixture 目錄 `scripts/fixtures/five-station-simplify/`：4-spec DD 下層建議。依據：4-spec 內部技術選擇。
- T-11 一次寫齊 RP-1…16 列（T-1 只要求 RP-16 一列）：最終 annex 必須可對十六紅。依據：S-2.6／T-11 Intent。
- live Q6 掃描跳過 4-spec 自己的 GIVEN／「寫成 Observed」例句。依據：[Assumption] S-6.3 觀測是擋升格句，不是讓契約自紅。
- 不把新牙掛進 `hooks/selftest.sh` MIN_CASES／`EXPECTED_MAPPED_FILES`。依據：S-8.5 Files 聯集不含 hooks／file-map；Split Decisions。

## Deviations

### D-1(L1)
- 現象:`bash scripts/check-file-map.sh` → `scanned=208 ≠ EXPECTED_MAPPED_FILES=205`（新 3 支 scripts/*.py|sh）
- 保守選擇:不改 `check-file-map.sh`、`guides/guide-dev-flow.html`、`test-architecture-guards.sh`
- 理由:S-8.5／T-12 Boundaries：紅了是 L1 訊號不是本 hop 預授權
- 影響:T-12／R-8／S-8.5；CI file-map 會紅直到 coordinator 另刀地板

### D-2(L1)
- 現象:`five_station_f1.py` ≈407 行，超過 Diff Budget「scripts 新牙非測試 ≤250」
- 保守選擇:不拆第二家族、不加第 4 支 scripts 檔
- 理由:一家族覆蓋 16 RP + 9 SLOT；再拆檔會撞 ≤4 檔格，且不改 R/S
- 影響:T-1…T-12 實作密度；annex 兩檔 40+23 行仍在 ≤200

## Files Changed

對照 4-spec Diff Budget F1：annex 2 檔；scripts 新牙 3 檔 + fixture 目錄；本目錄 6-notes（+html）。零 graph／hooks／_templates／STATUS。

- `scripts/five_station_f1.py`（新）
- `scripts/check-five-station-f1.sh`（新）
- `scripts/test-five-station-f1.sh`（新）
- `scripts/fixtures/five-station-simplify/*`（新）
- `notes/design/five-station-simplify-f1-dual-read-annex.md`（新）
- `notes/design/five-station-simplify-f1-rp-min-set.md`（新）
- `docs/dev/five-station-simplify/6-implementation-notes.md`（新）
- `docs/dev/five-station-simplify/6-implementation-notes.html`（產檔器）

## Diff(各 T commit,逐檔折疊)

### Result.red · `scripts/five_station_f1.py` 70-76  T-1
改什麼：Finding 只收 red code，給 selftest 對 RP。
關聯：caller `evaluate`
```diff
 class Result:
     def __init__(self):
         self.items = []
         self.info = {}
+    def red(self, code, msg):
+        self.items.append((code, True, msg))
```

### infer_kind · `scripts/five_station_f1.py` 106-113  T-1
改什麼：長前綴先配，避免 dual-read annex 被當成 dual 文案規則。
關聯：caller `evaluate`
```diff
 def infer_kind(path, meta):
+    if meta.get("f1-kind"):
+        return meta["f1-kind"]
+    name = os.path.basename(path)
+    for prefix, kind in KIND_PREFIX:
+        if prefix in name:
+            return kind
+    return "generic"
```

### in_flight · `scripts/five_station_f1.py` 123-125  T-4
改什麼：只認 1–7 `.md` basename，html 不算凍。
關聯：caller `evaluate` inflight 包
```diff
 def in_flight(files):
+    bases = {os.path.basename(item) for item in files}
+    return any(name in bases for name in STAGE_MD)
```

### run_c4 · `scripts/five_station_f1.py` 156-168  T-7
改什麼：F1 接既有 spec-gate C4，不另造模糊詞家族。
關聯：caller `evaluate` spec 包／callee `scripts/check-spec-gate.sh`
```diff
 def run_c4(path, root):
+    proc = subprocess.run(["bash", script, path], capture_output=True, text=True)
+    if re.search(r"❌\s*C4\b", blob):
+        return True
```

### evaluate · `scripts/five_station_f1.py` 171-188  T-1
改什麼：Agent 代寫 ACCEPTED／Ship PASS 無人類 attestation = RP-16 未寫。
關聯：caller `check_path`／peer `Result.red`
```diff
 def evaluate(text, path="", root=None):
+    if kind == "verdict":
+        if ACCEPTED.search(body) and not attest:
+            result.red("RP-16", "ACCEPTED 無 human attestation = 未寫")
+        if PASS_LN.search(body) and writer != "human" and not attest:
+            result.red("RP-16", "Ship PASS 無人類頂欄 = 未寫")
```

### evaluate · `scripts/five_station_f1.py` 189-193  T-2
改什麼：九 SLOT 缺一紅。
關聯：dual-read annex
```diff
+    if kind in ("slots", "annex"):
+        missing = [slot for slot in SLOTS if slot not in body]
+        if missing:
+            result.red("S-5.8", "缺 SLOT: " + ",".join(missing))
```

### evaluate · `scripts/five_station_f1.py` 201-210  T-3
改什麼：doctor／2.0.0+hops 文案紅；缺新 5 欄不紅。
關聯：dual-read fixtures
```diff
+    if ("2.0.0" in body and re.search(r"五站預設|five-station-default", body)):
+        result.red("S-5.7", "2.0.0+五站 hops → 仍舊 7")
+        result.info["route"] = "old-7"
```

### evaluate · `scripts/five_station_f1.py` 195-199  T-11
改什麼：RP 最小集減列紅。
關聯：rp-min-set annex
```diff
+    if kind in ("rpset", "annex"):
+        missing = [rp for rp in RPS if not re.search(r"\b%s\b" % rp, body)]
+        if missing:
+            result.red("S-2.6", "annex 少 RP: " + ",".join(missing))
```

### evaluate · `scripts/five_station_f1.py` 212-221  T-4
改什麼：in-flight 五站 hop＝RP-15。
關聯：fixtures `inflight-*`
```diff
+        if flying and ("five-station" in want or "五站 hop" in body):
+            result.red("RP-15", "in-flight 不得五站 hop／寫五站狀態")
```

### evaluate · `scripts/five_station_f1.py` 223-250  T-5
改什麼：T 卡缺四欄或 Verify「看起來沒問題」→ RP-1。
關聯：fixtures `rp-01-*`
```diff
+            if miss:
+                result.red("RP-1", "%s 缺欄 %s" % (task["name"], miss))
+            if task["verify"] and "看起來沒問題" in task["verify"]:
+                result.red("RP-1", "%s Verify 無鑑別力" % task["name"])
```

### evaluate · `scripts/five_station_f1.py` 252-260  T-6
改什麼：無 RED／自審／無原始輸出。
關聯：fixtures `rp-02-*`／`rp-06-*`
```diff
+        if re.search(r"無 RED|RED:\s*(無|—|n/a|缺失)", body):
+            result.red("RP-2", "無 RED 輸出")
```

### evaluate · `scripts/five_station_f1.py` 262-273  T-7
改什麼：接 C4 三詞與測試名無 S-id。
關聯：callee `run_c4`
```diff
+        if any(word in body for word in VAGUE_ALL):
+            result.red("RP-3", "未定事項三詞")
+            result.info["c4_fail"] = bool(run_c4(path, root))
```

### evaluate · `scripts/five_station_f1.py` 244-250  T-8
改什麼：少 Must-keep 與可選句、Files 超聯集。
關聯：fixtures `brief-*`／`rp-05-*`
```diff
+        if OPTIONAL.search(body):
+            result.red("S-2.7", "可選句擋 G2")
```

### evaluate · `scripts/five_station_f1.py` 275-293  T-9
改什麼：空 attestation＋chat／強迫 ACCEPTED／請人審／否定跳過。
關聯：fixtures `rp-12`…`rp-14`／`skip-negation-as-oc.md`
```diff
+        if CHAT.search(body) and not attest:
+            result.red("RP-13", "空 attestation + chat 不得離 Spec")
```

### evaluate · `scripts/five_station_f1.py` 296-312  T-10
改什麼：不可逆無 Quiz、無人 PASS 卻 Done、八點不齊。
關聯：fixtures `rp-07`／`rp-08`／`s-3-3-*`
```diff
+        if value != "PASS":
+            result.red("RP-8", "無人 PASS 卻 Done")
```

### evaluate · `scripts/five_station_f1.py` 314-320  T-11
改什麼：三 cap 對照稿各紅（不寫計數器）。
關聯：fixtures `rp-09`…`rp-11`
```diff
+        if re.search(r"第\s*3\s*次|重寫第 3", body):
+            result.red("RP-9", "hop 重寫第三次")
```

### evaluate · `scripts/five_station_f1.py` 322-329  T-12
改什麼：改採已拒案與 Q6 升格。
關聯：fixtures `reopen-*`／`q6-as-fact.md`
```diff
+        for match in REOPEN.finditer(body):
+            result.red("S-8.6", "重開已拒案 %s" % match.group(1))
```

### live_close · `scripts/five_station_f1.py` 332-381  T-12
改什麼：本 slug 七舊名／token／Files 閉聯集／Q6 open；4-spec GIVEN 例句不誤殺。
關聯：讀 `docs/dev/five-station-simplify/5-tasks.md`（不寫入）
```diff
 def live_close(root):
+    result.info["new_family"] = any(name in names for name in NEW_FAMILY)
+    result.info["files_closed"] = closed
+    result.info["q6_open"] = bool(re.search(
+        r"Q6[^\n]*採用現場[^\n]*\|\s*open\b", spec_text
+    ))
```

### check_path · `scripts/five_station_f1.py` 384-386  T-1
改什麼：牙入口讀單一 fixture。
關聯：`check-five-station-f1.sh`
```diff
 def check_path(path, root=None):
+    return evaluate(Path(path).read_text(encoding="utf-8"), path=str(path), root=root)
```

## Self-Review

①每個 T×S 有含 S-id 的 CASE 名 + 該 T 自己的 RED（開工前腳本不存在）與 GREEN（上列 Verify）。不得跨 T 把 GREEN 輸出當另一 T 的唯一證據；T-9／T-11／T-12 另點具名檔。
②每 T 在 T Review Log 有 verdict=PRE（不是獨立 PASS）。
③PRE ≠ PASS；沒有「PASS 早於 commit」可填。獨立 reviewer 尚未跑。
④無 FAIL 後未收斂的 T。
⑤實作一次落地 T-1…T-12（sequential 依賴同一牙）；正式「每 T 一 commit」等獨立 PASS 後由 reviewer／coordinator 切。Progress Log 尚未填 PASS hash。
⑥`git status` 新增檔 ⊆ 5-tasks Files 聯集 + 本目錄 6-notes。file-map 紅＝D-1 L1。
⑦Decisions／D-1／D-2 對得上 diff。DBC：無未授權模組依賴；Data owner 仍是母版 scripts／annex；未改 Interface 正本（doctor／_stage3）；未「修好」Known limit（仍不改 `_stage3_impl.py`，改由 F1 SLOT-SKIP-NEGATION 收）。
⑧本次 S 的 F1 牙群組全綠。既有 `check-file-map.sh` 紅（D-1）。未發明 G3 PASS。未跑全 repo selftest（S-8.5 禁改 hooks 地板）。

## Review Follow-up(G3 打回時才用)

（空）
