---
feature: five-station-f2
stage: 6-implementation
status: draft
owner: implementer-A
updated: 2026-09-14
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 56c8019c1058c375755ca03944140f79ff8bbe55

> Implementer notes. T Review Log is **self-check pending independent review**.
> Do not read these verdicts as T Review ACCEPTED or Human G3 PASS.

## 0. 起手

### 0a branch／錨點

- 只讀 4-spec／5-tasks／本檔／living。禁讀 1／2／3。
- `git fetch origin main` → `FORK=56c8019c1058c375755ca03944140f79ff8bbe55`
- `git switch -c cursor/five-station-f2-s6-impl-5e82 "$FORK"`
- `test "$(git rev-parse HEAD)" = "$FORK"` → 通過

### 0b worktree 隔離

n-a:本 feature 未並行。單一 checkout、無第二 worktree；不改 STATUS（companion #345）；無另開容器／DB／queue。

### 0c 守衛與 doctor

手動實作（非 dev-run 派工）。`devflow-exec.sh start` 未武裝本 session（cloud agent 單線）。doctor 現況 COMPATIBLE＝約束，不是 hop 通行證（T-5）。

## T Review Log

下列為 **implementer-self / pending independent review**。同一 agent 不得自稱 T Review ACCEPTED。未發明 G3 PASS。5-tasks checkbox 保持未勾。

### T-1
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self（非獨立）
- reviewed-at: 2026-09-14 PRE
- Verify: `--case NEW5-Q12-ZERO --case NEW5-RUN2` → n=2；failed=0
- Covers finding: S-1.1／S-1.2／S-1.3／S-1.4／S-1.11／S-4.12 有含 S-id 的 assertion
- Files finding: 入口＋coordinator＋`new5/q12-first-persist/`
- RED→GREEN finding: 開工前腳本不存在＝RED；本 T Verify 綠
- Test Integrity finding: none（自檢；待獨立審）
- Design boundary finding: 倉在 `docs/dev/<slug>/.five-station/store`；未鎖鍵名
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-2
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--case NEW5-CAP-3 --case NEW5-STORE-READ` → n=2；failed=0
- Covers finding: S-1.5／S-1.8／S-1.12／S-4.11
- Files finding: 含 `five_station_f1.py` 讀倉最小接線；字樣牙回歸仍在
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 字樣牙未關掉
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-3
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--case NEW5-DECIDE-2 --case NEW5-GOAL-2` → n=2；failed=0
- Covers finding: S-1.6／S-1.7／S-1.9／S-1.10
- Files finding: RP-10／11 讀倉；Goal+Decide 同 mutation
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未分兩次寫
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-4
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: SPEC-SHARE／BUILD-SHARE／SEVEN-STEM → n=3；failed=0
- Covers finding: S-2.1…S-2.7／S-4.13／S-4.14
- Files finding: 未改 `graph.yaml`
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 七 stem 是注入紅格，不是拒寫當綠
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-5
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group doctor-route` → n=4；F1 `--group dual-read` 另跑
- Covers finding: S-3.1…S-3.6／S-7.1…S-7.3
- Files finding: 未改 doctor／marketplace
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: doctor 綠不是路條
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-6
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--hop I/D/Sp/Bu/Sp5b` + PRED-STOP n=6；`--group events` n=3
- Covers finding: S-4.2／S-4.3／S-4.15…S-4.19／S-5.1…S-5.4／S-6.2
- Files finding: 未 bump agent-event
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 鍵名 OPEN；events CASE 用官方 18 名
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-7
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: MK-RED／SHIP-MECH／WAIT-RED／FOLD-RED → n=4；failed=0
- Covers finding: S-4.4…S-4.8／S-6.3／S-6.4
- Files finding: 四張注入稿
- RED→GREEN finding: 紅格餵壞行為
- Test Integrity finding: none（自檢）
- Design boundary finding: 極性未反
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-8
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: `--group must-keep` → n=16；failed=0
- Covers finding: S-6.1／S-6.5／S-6.6 gate（未改 Disposition 表）
- Files finding: `new5/must-keep/` 16 份
- RED→GREEN finding: 合法拒，不是 NEW5-MK-RED
- Test Integrity finding: none（自檢）
- Design boundary finding: 未發明 NEW5-MK-ANY
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-9
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: OLD7-NO-FIVE／TOKEN／SELF → n=3；failed=0
- Covers finding: S-7.4…S-7.7
- Files finding: OLD7 fixture 根；未把本目錄當 NEW5
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未刪 token
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

### T-10
- reviewer identity: implementer-A（self）
- reviewer kind: implementer-self
- reviewed-at: 2026-09-14 PRE
- Verify: 全入口 n≥18 exit 0；`--only` 三探針 exit 3；未知旗標 exit 2
- Covers finding: S-4.1／S-4.9／S-4.10／S-8.1…S-8.9
- Files finding: 見 D-1（file-map／CI 註冊為 L1）
- RED→GREEN finding: 見 TDD Evidence
- Test Integrity finding: none（自檢）
- Design boundary finding: 未改 graph／token／doctor／契約／STATUS
- verdict: PENDING_INDEPENDENT_REVIEW
- correction + re-review after FAIL: N/A

## Progress Log

<!-- hash 在本 PR 的實作 commit 寫入；獨立 T review 前不勾 5-tasks -->

| 日期 | T-id | 一行 |
|---|---|---|
| 2026-09-14 | T-1…T-10 | `4f0a136` implementer commit；T Review 待獨立審 |

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run:

## TDD Evidence

### T-1 / S-1.1 S-1.2 S-1.3 S-1.4 S-1.11 S-4.12
- RED: `scripts/test-five-station-f2.sh` 不存在 → 非零（5-tasks 開工前原樣）
- GREEN: `--case NEW5-Q12-ZERO --case NEW5-RUN2` → CASE×2；first persist=0；新 process 仍 2

### T-2 / S-1.5 S-1.8 S-1.12 S-4.11
- RED: 無 CAP-3／STORE-READ fixture＋入口 → 非零
- GREEN: n=2；倉＝2 拒第 3 次；字樣牙不讀倉＝該格紅

### T-3 / S-1.6 S-1.7 S-1.9 S-1.10
- RED: 無 DECIDE-2／GOAL-2 → 非零
- GREEN: n=2；Goal+Decide 同 mutation；T retry ≠ hop

### T-4 / S-2.1…S-2.7 S-4.13 S-4.14
- RED: 無 spec-share／build-share／seven-stem → 非零
- GREEN: n=3；同桶；注入七 stem 紅

### T-5 / S-3.1…S-3.6 S-7.1…S-7.3
- RED: 無 doctor-route → 非零
- GREEN: `--group doctor-route` n=4；理由含「路線未宣告／仍舊 7」；F1 dual-read 另跑仍綠

### T-6 / S-4.2 S-4.3 S-4.15…S-4.19 S-5.1…S-5.4 S-6.2
- RED: 無 hop 評 → 非零
- GREEN: hop CASE×6；events CASE×3（NEW5-HOP-OK／PRED-STOP／CAP-3）

### T-7 / S-4.4…S-4.8 S-6.3 S-6.4
- RED: 無注入稿 → 非零
- GREEN: n=4；四格餵壞行為

### T-8 / S-6.1 S-6.5 S-6.6
- RED: 無 must-keep/ → 非零
- GREEN: `--group must-keep` n=16；各 M 拒 hop

### T-9 / S-7.4…S-7.7
- RED: 無 old7/ → 非零
- GREEN: n=3；token＋F1 回歸綠；本目錄跳不過

### T-10 / S-4.1 S-4.9 S-4.10 S-8.1…S-8.9
- RED: 入口不存在 → 非零
- GREEN: `-v` CASE≥18 exit 0；`--only new5|old7|f1` 各 exit 3；未知旗標 exit 2

## Decisions(spec 未載明的自由選擇)

- 倉正本用 JSON 檔（鍵名仍 OPEN，不寫成已核 schema）。依據：DD-1 路徑形；S-5.4。
- CASE 跑者留在 `five_station_f2.py`，不另開 `five_station_f2_battery.py`（T-7 可省略）。依據：5-tasks T-7 Files 選配。
- `--only` 即使該路全綠也 exit 3（hollow 探針）。依據：S-4.1 b／c／d、S-8.8。
- must-keep 16 格 CASE 名用官方 `NEW5-HOP-OK`（Bu4 謂詞），不發明 `NEW5-MK-ANY`。依據：standing 禁發明名。
- F1 `evaluate(..., caps_from_store=True)` 預設讀倉；STORE-READ 注入關讀倉。依據：S-1.12。

## Deviations

### D-1(L1)
- 現象:新增 `scripts/test-five-station-f2.sh` + `scripts/five_station_f2.py` 後，`check-file-map.sh` 與 `devflow-check.sh` 註冊自審會紅（`test-*.sh` 必須出現在 run 行）。
- 保守選擇:上修 `EXPECTED_MAPPED_FILES` 208→210；檔案地圖加兩列；architecture 靜態釘同步；`devflow-check.sh` 註冊 F2 電池。**不是** F3 cut（guide 用語／預設路線未切五站）。
- 理由:line-count Known Limit；不動 R/S。
- 影響:T-10 / R-8 / S-8.9（准許清單外的守衛檔）。後站不准把 F3／token／graph 改成 In。

### D-2(L1)
- 現象:Stage 4 Diff Budget 估 fixture ≤12 檔；T-8 要求 16 份 must-keep + 具名 hop／注入稿，實得超過估計。
- 保守選擇:照 5-tasks 具名路徑建齊；不減官方 18 CASE。
- 理由:超支是估計訊號，不是 R/S 變更。
- 影響:T-8／T-10 fixture 數。

### D-3(L1) — 5-tasks frontmatter `draft` → `approved`(N1-arm / graph P0)
- 現象:6-notes 已存在時 `check-devstage6-graph.sh` P0 要求同 slug `5-tasks.md` 必須 `status: approved`，否則 N1-arm 不是入口。初版 PR 漏改，CI `REPO_REFERENCE` 紅在這條。
- 保守選擇:只改 frontmatter 並重建 html twin。不勾 T checkbox、不把 T Review 標 ACCEPTED、不發明 Human G3。
- 理由:F1 `five-station-simplify/5-tasks.md` 同例；approved 是 Stage 6 入口握手，不是 G3 PASS。
- 影響:`5-tasks.md` / `5-tasks.html` status 欄；graph 檢查。電池 CASE / persist / hop 不變。

## Files Changed

對照 4-spec Diff Budget（G2 之後只 F2 scripts）+ D-1 守衛：

- `scripts/test-five-station-f2.sh`
- `scripts/five_station_f2.py`
- `scripts/five_station_f1.py`（RP 讀倉最小接線）
- `scripts/fixtures/five-station-f2/**`
- `docs/dev/five-station-f2/6-implementation-notes.md` + html
- L1 D-1: `scripts/check-file-map.sh`、`scripts/test-architecture-guards.sh`、`scripts/devflow-check.sh`、`guides/guide-dev-flow.html` 檔案地圖列（非 F3 cut）
- L1 D-3: `docs/dev/five-station-f2/5-tasks.md` / `5-tasks.html` frontmatter `status: approved`（N1-arm；非勾選 T、非 G3）

未改：`graph.yaml`、`_templates/`、`hooks/_doctor_impl.py`、`devflow-contract.json`、STATUS／HISTORY、token 檔。

## Diff(各 T commit,逐檔折疊)

### persist · `scripts/five_station_f2.py` 155-187  T-1 T-2
改什麼：第一次成功 persist＝0，其後 +1；桶＝2 再寫 → Escalated 且數字不減。
關聯：caller Battery.run_q12／run_cap／callee save_store
```diff
 def persist(repo_root, slug, hop_id, token=None, run_id="r1"):
+    if hop_id not in hops:
+        hops[hop_id] = 0
+        return 0, "ok"
+    if current >= 2:
+        data["status"] = "Escalated"
+        return current, "refused"
+    hops[hop_id] = current + 1
```

### persist_stem · `scripts/five_station_f2.py` 190-204  T-4
改什麼：檔名映射五站桶；seven_stem 注入另記，不當綠格。
關聯：caller Battery.run_share
```diff
 def persist_stem(repo_root, slug, stem, seven_stem=False, token=None, run_id="r1"):
+    if seven_stem:
+        data["seven_stem"] = True
+        return 0, "injected-seven"
+    hop = STEM_HOP.get(stem)
+    return persist(repo_root, slug, hop, token=token, run_id=run_id)
```

### goal_reopen · `scripts/five_station_f2.py` 232-250  T-3
改什麼：Goal 與 Decide 計數同一 mutation。
關聯：caller Battery.run_reopen／peer decide_reopen
```diff
 def goal_reopen(repo_root, slug, run_id="r1"):
+    data["goal_reopen"] = g + 1
+    if d < 1:
+        data["decide_reopen"] = d + 1
```

### evaluate · `scripts/five_station_f1.py` 327-345  T-2 T-3
改什麼：RP-9／10／11 讀附近 slug 倉；字樣正則留下做回歸。
關聯：caller f1_check／callee five_station_f2.caps_near
```diff
     if kind == "cap":
+        if caps_from_store:
+            caps = f2.caps_near(path)
+            if caps and int(caps.get("hop_max") or 0) >= 2:
+                result.red("RP-9", "hop 重寫第三次 store=%s" % caps["hop_max"])
         if re.search(r"第\s*3\s*次|重寫第 3", body):
             result.red("RP-9", "hop 重寫第三次")
```

### evaluate_hop · `scripts/five_station_f2.py` 430-480  T-6 T-7 T-8
改什麼：謂詞表列假則停修；Must-keep 紅拒 hop；inject 路徑只服務紅格。
關聯：caller Battery.run_hop／run_inject／run_must_keep
```diff
 def evaluate_hop(repo_root, slug, hop_key, inject=None):
+    if inject == "mk-hop":
+        return True, "injected-mk", data
+    false = pred_false(slug_dir, hop_key)
+    if false:
+        return False, false, data
```

### allow_legacy · `scripts/five_station_f2.py` 260-280  T-5 T-9
改什麼：三前置缺一條就舊 7；doctor／marketplace／cache 不當路條。
關聯：caller refuse_hop_reason／Battery.run_doctor
```diff
 def allow_legacy(project_root, slug_dir, doctor_green=False,
                  marketplace_updated=False, cache_has_hops=False,
                  synthetic_new5=False):
+    if not (declared and (not flying) and cut):
+        return True, "legacy"
```

### main · `scripts/five_station_f2.py` 980-1040  T-10
改什麼：單一入口；`--only` 一等旗標 exit 3；未知旗標 exit 2。
關聯：caller `test-five-station-f2.sh`
```diff
     p.add_argument("--only", choices=("new5", "old7", "f1"),
                    help="hollow probe (exit 3); first-class flag")
+    if args.only in ("new5", "old7", "f1"):
+        return 3
```

## Self-Review

①每個 T×S 有含 S-id 的 assertion + 該 T RED/GREEN：是（TDD Evidence）。不得跨 T 共用入口不存在當唯一證據——各 T 另有 CASE 綠輸出。
②每 T 在 T Review Log 有 verdict：有，皆 PENDING_INDEPENDENT_REVIEW（非 ACCEPTED）。
③每個 PASS 都早於該 T commit：獨立 review 尚未做；本檔不謊稱 PASS 早於 commit。
④FAIL 後有較晚 PASS：T-9 S-7.7 路徑字串誤判已修，自檢重跑綠。
⑤每 T 一 commit：本 PR 收成單一實作 commit（sequential 同檔重疊）；獨立審後可再切。
⑥git diff 檔案：准許清單 + D-1 守衛。graph／token／doctor／契約／STATUS＝0。
⑦Decisions／D-1／D-2 對得上 diff。DBC：無未授權模組；Data owner 仍是 slug coordinator；Goal+Decide 同 mutation 未拆。
⑧回歸：`test-five-station-f1.sh` exit 0；F2 全入口 exit 0。

未發明 G3 PASS。未開 Stage 7。

## Review Follow-up(G3 打回時才用)
