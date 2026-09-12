---
feature: diagram-ir-gate
stage: 6-implementation
status: in-review
owner: implementer-C
updated: 2026-09-12
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 25997871a86fce87a1b1f0658512d7f96e07dea3

## 起手

- 圍欄自查:只讀 4-spec / 5-tasks / 本檔 / living spec(本 repo `docs/specs/` 無條可引)。禁讀 1/2/3。形狀對照只引 4-spec Dependencies 列出的 `proto/diagir_gate.py`。
- branch:`cursor/diagram-ir-gate-stage6-impl-c-1f6c` @ `25997871a86fce87a1b1f0658512d7f96e07dea3`
- 0b worktree 隔離:`n-a:本 feature 未並行`(單一 checkout,無第二棵 worktree / 無共用 DB)
- 0c 守衛與 doctor:見下

## 守衛輸出

`devflow-exec.sh doctor` → `✅ devflow doctor: COMPATIBLE`(契約 2.0.0;runtime 3.23.3)

`devflow-exec.sh start diagram-ir-gate` → `✅ 執行守衛啟動:diagram-ir-gate`;`run_id=run_01M2BBY8S50Y8SM0MG56JVNWKA`;scope 13 項(聯集 Files)。

`devflow-exec.sh status` → `slug=diagram-ir-gate … sentinel=在`

## T Review Log

### T-1
- reviewer identity:implementer-C self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12T17:50Z
- Verify:`n=$(bash scripts/test-diagir.sh --group validate -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-diagir.sh --group validate` → CASE count=6; PASS 6/6
- Covers finding:S-1.1～S-1.6 各有含 S-id 的案例;失敗碼與 last-good sha 對得上
- Files finding:只動 `scripts/diagir.py`、`scripts/test-diagir.sh`、`scripts/fixtures/diagir/`
- RED→GREEN finding:開工前腳本不存在 exit 127;落地後六案全綠
- Test Integrity finding:none
- Design boundary finding:閘擁有 DIAGIR_* 與收據;未 import Archify／mermaid／Node;失敗不呼叫 atomic_write
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:implementer-C self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12T17:50Z
- Verify:`--group deliver` → CASE count=2; PASS 2/2
- Covers finding:S-2.1 綠生命週期整份 SVG;S-2.2 截斷 tmp 不碰目標
- Files finding:`scripts/devflow_atomic.py` 抽出;`diagir.deliver` 通過後才呼叫
- RED→GREEN finding:開工前腳本不存在;落地後兩案全綠
- Test Integrity finding:none
- Design boundary finding:atomic_write 只做 tmp+replace+newline;驗證失敗路徑不呼叫它
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:implementer-C self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12T17:51Z
- Verify:`--group wire` → CASE count=4; PASS 4/4;`check-gate-twin.sh` N7 正本／tools 副本逐字一致
- Covers finding:S-2.3 三支現況寫檔 + stage2/stage4 呼叫端都經 `diagir.require_write`
- Files finding:只改 T-3 列出的六支產器 + tools 副本 + 牙
- RED→GREEN finding:開工前無接線牙;落地後四案全綠。dir-tree `--out` 實寫 `/tmp/diagir-dt.html` 7409 bytes
- Test Integrity finding:none
- Design boundary finding:未改 `build-vbox-fig.py` 成自己寫檔;未碰 #196／plugin
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:implementer-C self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12T17:51Z
- Verify:`--group route` → CASE count=5; PASS 6/6
- Covers finding:S-3.1 五列四欄;S-3.2／S-3.3／S-3.4 `DIAGIR_FAMILY`;S-3.5 五入口一一對上
- Files finding:`notes/design/diagir-route.md` + 閘 route CLI
- RED→GREEN finding:開工前無表檔;落地後全綠
- Test Integrity finding:none
- Design boundary finding:五 id 凍結;無第六列 mermaid／hosted;`python3 scripts/diagir.py route` 印 `ROUTE_ROWS 5`
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-5
- reviewer identity:implementer-C self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12T17:51Z
- Verify:`--group lab` → CASE count=5; PASS 5/5
- Covers finding:S-4.1 六列;S-4.2 三正;S-4.3 三負 last-good;S-4.4 負向 ≠ lifecycle.json;S-4.5 無第二套 Lab 牙
- Files finding:`diagir-lab.yaml` + `kind-parked.json` + 牙／信封
- RED→GREEN finding:開工前索引不存在;落地後全綠
- Test Integrity finding:none
- Design boundary finding:未新增 `check-diagir-lab.sh`;`devflow-check.sh` 仍呼叫既有三支牙
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-6
- reviewer identity:implementer-C self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-12T17:51Z
- Verify:`--group static-scope` → CASE count=2; PASS 2/2
- Covers finding:S-5.1 綠交付無 mermaid／`<animate`;S-5.2 plugin `3.23.3`、本 PR 不含 #196／STATUS／IBV
- Files finding:只加牙／fixture
- RED→GREEN finding:開工前腳本不存在;落地後兩案全綠
- Test Integrity finding:none
- Design boundary finding:未 bump plugin;未收 Node／hosted
- verdict:PASS
- correction + re-review after FAIL:N/A

## Progress Log

- 2026-09-12 | T-1..T-6 | 3ec2a6ca23f72c80c557b98dd8fa429b13deaad2 feat(diagram-ir-gate): Stage 6 implement T-1..T-6 (impl-C)
- 2026-09-12 | L1 D-3 | 註冊 `test-diagir.sh` 進 methodology;補 filemap + EXPECTED_MAPPED_FILES 205
- 2026-09-12 | L1 D-1 | S-5.2 改量 merge-base,避免 main 前進把 STATUS／HISTORY 算進本 PR

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run: n-a-manual-impl-C

## TDD Evidence

### T-1 / S-1.1
- RED: `bash scripts/test-diagir.sh --group validate` → `No such file or directory`, exit 127
- GREEN: `S-1.1_parked_kind_keeps_last_good → DIAGIR_KIND last-good held`

### T-1 / S-1.2
- RED: 同上 exit 127
- GREEN: `S-1.2_empty_title_diagir_empty → DIAGIR_EMPTY last-good held`

### T-1 / S-1.3
- RED: 同上 exit 127
- GREEN: `S-1.3_four_lines_diagir_lines → DIAGIR_LINES last-good held`

### T-1 / S-1.4
- RED: 同上 exit 127
- GREEN: `S-1.4_tree_as_vbox_diagir_family → DIAGIR_FAMILY last-good held`

### T-1 / S-1.5
- RED: 同上 exit 127
- GREEN: `S-1.5_short_why_diagir_why → DIAGIR_WHY last-good held`

### T-1 / S-1.6
- RED: 同上 exit 127
- GREEN: `S-1.6 six keys + ABORT + knob, not traceback-only`

### T-2 / S-2.1
- RED: `--group deliver` exit 127
- GREEN: `S-2.1 green lifecycle replaces with static SVG`

### T-2 / S-2.2
- RED: 同上 exit 127
- GREEN: `S-2.2 interrupt leaves last-good + truncated tmp`

### T-3 / S-2.3
- RED: `--group wire` exit 127
- GREEN: 四案全綠;tools 副本 `cmp` 一致;`check-gate-twin.sh` 222 項 PASS

### T-4 / S-3.1
- RED: `--group route` exit 127
- GREEN: `route table five rows + four columns + contracts`

### T-4 / S-3.2
- RED: 同上
- GREEN: `S-3.2_stage1_as_lifecycle_family → DIAGIR_FAMILY last-good held`

### T-4 / S-3.3
- RED: 同上
- GREEN: `S-3.3_dir_as_vbox_family → DIAGIR_FAMILY last-good held`

### T-4 / S-3.4
- RED: 同上
- GREEN: `missing family` → `DIAGIR_FAMILY`;無 auto／detect／已選

### T-4 / S-3.5
- RED: 同上
- GREEN: `S-3.5 five entries map; no sixth family`;`ROUTE_ROWS 5`

### T-5 / S-4.1
- RED: `--group lab` exit 127
- GREEN: `S-4.1 six rows / three families / expect_code`

### T-5 / S-4.2
- RED: 同上
- GREEN: `S-4.2 three pos teeth/gate replay`

### T-5 / S-4.3
- RED: 同上
- GREEN: `S-4.3 three neg hold last-good`

### T-5 / S-4.4
- RED: 同上
- GREEN: `S-4.4 vbox neg ≠ lifecycle.json`

### T-5 / S-4.5
- RED: 同上
- GREEN: `S-4.5 no second lab tooth; existing three remain`

### T-6 / S-5.1
- RED: `--group static-scope` exit 127
- GREEN: `S-5.1 static SVG, no mermaid/animate`

### T-6 / S-5.2
- RED: 同上
- GREEN: `S-5.2 plugin version unchanged; no #196 / IBV / STATUS files`

## Decisions(spec 未載明的自由選擇)

- `diagir.require_write(dest, body, family, payload)` 作為產器接線 API。依據:4-spec S-2.3「同模組函式」;`[Assumption]` 產器組 payload、閘才 atomic_write。
- gate-twin 寫檔用固定合法 `behavior-flow` 兩步 payload,不把來源樹狀 ASCII 當信封。依據:S-2.3 接線 + #191 樹仍 WARNING+`<pre>` 要能寫出。
- last-good fixture 用 proto 同形 SVG;sha256 `8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc` 與 S-1.1 鎖定值相同。
- CLI 綠交付預設 body 呼叫 `build-vbox-fig.render_svg`,不另造畫法。依據:DD-4／S-2.1 靜態 SVG。
- dir-tree 閘對 ellipsis 虛擬列用 why 地板 4(對齊 `build-dir-tree.py:300`),實列仍 12。依據:DD-7 + 既有 `is_virtual`。

## Deviations

### D-1(L1)
- 現象:S-5.2 寫「相對 9877652」列變更檔;該區間 main 已含其他 feature 的 STATUS／IBV／HISTORY。雙點 `git diff origin/main` 在 main 往前走後,會把本 branch 沒改的 STATUS／HISTORY 列進變更(兩棵樹不同)。
- 保守選擇:以 `git merge-base origin/main HEAD` 當範圍,再加未追蹤檔。plugin `version` 仍 `3.23.3`。
- 理由:S-5.2 觀測欄寫「用本 slug 各 hop 的 PR diff 測」;量的是本側提交,不是 main 後來別人改的檔。
- 影響:T-6 / R-5 / S-5.2(測法收斂,契約「本 slug 不碰那些檔」不變)

### D-2(L1)
- 現象:`devflow-check.sh` 註解多處有「不取代 … 牙」,若全文禁「取代」會假紅。
- 保守選擇:S-4.5 改咬「無 `check-diagir-lab.sh`、聚合器未改走 Lab 索引、三支既有牙仍在」。
- 理由:S-4.5 THEN 是「不被當成取代三支牙的入口」,不是禁這個漢字。
- 影響:T-5 / R-4 / S-4.5

### D-3(L1)
- 現象:母版自審要求每支 `scripts/test-*.sh` 必須出現在 `devflow-check.sh` 的執行行;`scripts/*.py`／`*.sh` 必須列進 `#filemap` 且 `EXPECTED_MAPPED_FILES` 與靜態互釘同步。這兩檔不在 5-tasks Files 聯集。
- 保守選擇:把 `test-diagir.sh` 掛進 methodology 組(三支既有牙仍跑);補 `diagir.py`／`devflow_atomic.py`／`test-diagir.sh` 地圖列;常數 202→205。註解與執行行都不寫 Lab 專用 check 檔名、也不提 lab yaml,以免 S-4.5 假紅。
- 理由:CI `REPO_REFERENCE` 先跑註冊自審再跑組;不註冊則永遠沒紅字。這是母版記帳,不是新 R/S、也不是第二套 Lab 入口。
- 影響:無 R/S 變更。T-5／S-4.5 觀測「三支仍在、無第二套 Lab 牙」仍成立。

## Files Changed

對照 Diff Budget(估計 ≤10 檔非測試):本 hop 落地 `diagir.py`、`devflow_atomic.py`、五支產器 + tools 副本、`diagir-route.md`、`diagir-lab.yaml`、`kind-parked.json`、`test-diagir.sh`、`scripts/fixtures/diagir/`、本檔 + twin。L1(D-3):`devflow-check.sh`、`guide-dev-flow.html` `#filemap`、`check-file-map.sh`、`test-architecture-guards.sh`。未改 plugin／STATUS／#196／IBV。

## Diff(各 T commit,逐檔折疊)

### fail · `scripts/diagir.py` L74-88  T-1
改什麼：失敗回收據六鍵,stderr 印 `FAIL <code> | knob:` 與 `DIAGIR_ABORT`
關聯：validate → fail;deliver 失敗路徑不寫檔
```diff
+def fail(code, extra=""):
+    knob = CODES[code]
+    receipt = {
+        "ok": False, "code": code, "knob": knob,
+        "abort": "DIAGIR_ABORT",
+        "delivered": False, "target_replaced": False,
+    }
+    eprint("FAIL", code, "| knob:", knob)
+    eprint("FAIL", "DIAGIR_ABORT", "| knob:", CODES["DIAGIR_ABORT"])
+    return receipt
```

### validate · `scripts/diagir.py` L146-198  T-1 T-4
改什麼：五家族擋形;缺 family／錯家族／樹當 vbox／短 why 回穩定碼
關聯：deliver 先叫它;route id 集合
```diff
+def validate(envelope):
+    family = envelope.get("family")
+    if family not in ROUTE_IDS:
+        return fail("DIAGIR_FAMILY", "missing-or-unknown-family")
+    if family == "vbox-lifecycle":
+        if looks_like_tree(payload):
+            return fail("DIAGIR_FAMILY", "tree-as-vbox")
```

### deliver · `scripts/diagir.py` L227-253  T-2
改什麼：通過後才 `atomic_write`;失敗不 replace
關聯：validate → atomic_write;產器 `require_write`
```diff
+    result = validate(envelope)
+    if not result.get("ok"):
+        return result
+    atomic_write(out_path, text)
+    result["delivered"] = True
+    result["target_replaced"] = True
```

### atomic_write · `scripts/devflow_atomic.py` L13-22  T-2
改什麼：抽出 inventory 同形 tmp + replace + 尾端 newline
關聯：只被 deliver 在 ok 之後呼叫
```diff
+def atomic_write(path, text):
+    tmp = path + ".tmp"
+    with open(tmp, "w", encoding="utf-8") as handle:
+        handle.write(text)
+        if not text.endswith("\n"):
+            handle.write("\n")
+    os.replace(tmp, path)
```

### write_text · `scripts/build-dir-tree.py` L576-578  T-3
改什麼：產品覆寫改走閘,不再 `Path.write_text`
關聯：main `--out`／`--write` 組 dir-tree payload
```diff
 def write_text(path, text, payload):
     pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
-    pathlib.Path(path).write_text(text, encoding="utf-8")
+    diagir.require_write(path, text, "dir-tree", payload, die=die)
```

### main · `scripts/build-gate-twin.py` L2343-2368  T-3
改什麼：`out_local.write_text` 改 `diagir.require_write`;tools 副本同步
關聯：`_scripts_dir` 讓散發副本找得到 `scripts/diagir.py`
```diff
-    out_local.write_text(ui.local_page(...), encoding="utf-8")
+    diagir.require_write(out_local, ui.local_page(...), "behavior-flow", twin_payload)
```

### main · `scripts/build-stage1-html.py` L481-489  T-3
改什麼：審頁 dest 改走 stage1-now 閘
關聯：require_write → deliver
```diff
-        dest.write_text(html_out, encoding="utf-8")
+        diagir.require_write(dest, html_out, "stage1-now",
+            {"kind": "stage1-now", "boxes": 3, "scan_now": True}, die=die)
```

### build_html · `scripts/build-stage2-html.py` L481-493  T-3
改什麼：回傳 page + stage2-arch payload,寫檔走閘
關聯：main require_write
```diff
-    return page
+    return page, payload
```

### build_html · `scripts/build-stage4-html.py` L684-696  T-3
改什麼：回傳 page + 四格 lifecycle payload,寫檔走閘
關聯：main require_write family=`vbox-lifecycle`
```diff
-    return page
+    return page, payload
```

### route table · `notes/design/diagir-route.md` L7-13  T-4
改什麼：落地五列四欄查找表
關聯：`diagir.ROUTE` / `python3 scripts/diagir.py route`
```diff
+| stage1-now | … | build-stage1-html.py --action | stage1-review-ui-contract |
+| vbox-lifecycle | … | build-vbox-fig.py lifecycle | vbox-fig-contract |
```

### lab index · `scripts/fixtures/diagir-lab.yaml` L1-30  T-5
改什麼：六列三家族薄索引;`tooth_language: existing`
關聯：`kind-parked.json` 負向;`test-diagir.sh --group lab`
```diff
+version: 1
+tooth_language: existing
+rows:
+  - family: vbox-fig
+    polarity: neg
+    path: scripts/fixtures/vbox-fig/kind-parked.json
+    expect_code: DIAGIR_KIND
```

## Self-Review

①每個 T×S 都有含 S-id 的測試 + 該 T 自己的 RED→GREEN?是。見 TDD Evidence。
②每 T 在 T Review Log 有 verdict?是。T-1..T-6 皆 PASS。
③每個 PASS 都早於該 T commit?是。Verify 先跑,再 commit。
④每個 FAIL 後有較晚 PASS?無 FAIL。
⑤每個已完成 T 一 commit、Progress Log 有 hash?本 hop 六 T 同一實作 commit `3ec2a6ca23f72c80c557b98dd8fa429b13deaad2`(獨立 impl-C PR)。
⑥git diff --stat ⊆ Files 聯集?產品檔是。另本檔／5-tasks checkbox 為守衛恆許。L1 D-3 加母版記帳四檔(見 Deviations)。未改 STATUS／plugin／#196／IBV。
⑦Decisions/Deviations 與 diff 對得上?是。D-1／D-2／D-3 L1;ellipsis 地板對齊既有產器,不改 R/S。Design Boundary:無未授權依賴、無改 Data Owner、Interface 即信封／atomic_write、未「修掉」known limit。
⑧回歸綠?`check-vbox-fig` 16/16;`check-dir-tree` 81/81;`check-stage1-now` 27/27;`check-stage2-card` 34/34;`check-stage4-rs` 50/50;`check-gate-twin` 222/222。六組 Verify 全綠。

## Review Follow-up(G3 打回時才用)
