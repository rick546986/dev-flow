---
feature: host-stack-fit
stage: 6-implementation
status: draft
owner: cursor-cloud-agent
updated: 2026-09-10
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: fa55b484d554588904f5ef510768b7e4d8dcdd91

## 起手

- 圍欄自查:只讀 4-spec / 5-tasks / 本檔 / living spec(本 repo `docs/specs/` 無條可引)。禁讀 1/2/3。
- branch:`cursor/host-stack-fit-stage6-f801` @ `fa55b484d554588904f5ef510768b7e4d8dcdd91`
- 0b worktree 隔離:`n-a:本 feature 未並行`(單一 checkout,無第二棵 worktree / 無共用 DB)
- 0c 守衛與 doctor:見下

## 守衛輸出

`devflow-exec.sh doctor` → `✅ devflow doctor: COMPATIBLE`(契約 2.0.0;runtime 3.22.1)

`devflow-exec.sh start host-stack-fit` → `✅ 執行守衛啟動:host-stack-fit`;`run_id=run_01M24BMZSBB3F47RTTMAXWS3JP`;scope 21 項(聯集 Files)。

`devflow-exec.sh status` → `slug=host-stack-fit … sentinel=在`

## T Review Log

### T-1
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:31Z
- Verify:`n=$(bash scripts/test-host-receipt.sh --group mint-stage4 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 8 && bash scripts/test-host-receipt.sh --group mint-stage4` → CASE count=9; passed=9 failed=0
- Covers finding:S-1.1(stage4)／S-1.2／S-1.3／S-1.4 各有含 S-id 的案例
- Files finding:只動 hooks/devflow-lib.py、scripts/check-devstage4-graph.sh、scripts/test-host-receipt.sh、scripts/fixtures/host-receipt/ + 本檔
- RED→GREEN finding:allow 三案先紅(無檔)、負向六案本就綠;鑄檔後九案全綠
- Test Integrity finding:none(未刪／放寬 assertion、無 skip、無 mock 被測物)
- Design boundary finding:mint 住 lib;stage4 只呼叫鉤子;deny／exit 2／probe／start／write-cursor／write-scope 不鑄;未新開 check-host-receipt.sh
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-2
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:34Z
- Verify:`n=$(bash scripts/test-host-receipt.sh --group mint-rest -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-host-receipt.sh --group mint-rest` → CASE count=6; passed=6 failed=0
- Covers finding:S-1.1 其餘六站各一案
- Files finding:六支該站腳本只加鉤子呼叫;測試與 fixture 在 T-2 Files
- RED→GREEN finding:六站 allow 先紅(無檔)後綠
- Test Integrity finding:none
- Design boundary finding:未自造第二份 schema／路徑;未改鬆 `--action`
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-3
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:37Z
- Verify:`--group verify-receipt` → CASE count=14; passed=14 failed=0
- Covers finding:S-2.1／S-2.2×3／S-2.3×4／S-2.4×5／S-2.7
- Files finding:只加厚 lib verify 分支 + 測試／fixture
- RED→GREEN finding:13 案先因 allow 仍鑄而假綠;S-2.7 改測「空檔+無布林仍走舊 graph 鑄檔」
- Test Integrity finding:none
- Design boundary finding:只認 JSON 布林 `verify_receipt:true`;不認 `action:"verify_receipt"`
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-4
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:39Z
- Verify:`--group fail-closed-claim` → CASE count=3; passed=3 failed=0
- Covers finding:S-2.5 start-only／文案;S-2.6 核對前紅後綠
- Files finding:guide #host／PLUGIN／dev-setup SKILL + 測試
- RED→GREEN finding:文案三檔缺「沒有 PreToolUse」先紅;加鑄／核對副作用句後綠。start-only 與前後核對兩案本就綠(T-3 鉤子)
- Test Integrity finding:none
- Design boundary finding:未加 Cursor Write hook;未改鬆 `--action` 禁令
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-5
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:45Z
- Verify:`n=$(bash scripts/test-stack-inventory.sh --group i2 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-stack-inventory.sh --group i2` → CASE count=7; passed=7 failed=0
- Covers finding:S-3.1／S-3.2／S-3.3／S-3.4×2／S-3.5／S-5.1 各有含 S-id 的案例
- Files finding:write-stack-inventory.py、test-stack-inventory.sh、dev-setup SKILL、check-dev-setup-discipline.sh、fixtures/stack-inventory/
- RED→GREEN finding:無腳本先紅;寫入器 + 七案後綠
- Test Integrity finding:none
- Design boundary finding:I2 專案級 pin + 第一層 direct_deps;written_by=dev-setup;缺檔 check 不得成功;未讀 I4 回填
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-6
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:48Z
- Verify:`n=$(bash scripts/test-stack-inventory.sh --group i4 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-stack-inventory.sh --group i4` → CASE count=3; passed=3 failed=0
- Covers finding:S-4.1／S-4.2／S-4.3
- Files finding:write-stack-inventory.py --write-stack、SKILL「人要才產」、i4 測試
- RED→GREEN finding:預設不建 I4 與無 I2 拒寫先紅;加 --write-stack 與文案後綠
- Test Integrity finding:none
- Design boundary finding:只有 docs/dev/0-stack.md;digest 不是 lock 正本;I4 失敗不影響 I2
- verdict:PASS
- correction + re-review after FAIL:N/A

### T-7
- reviewer identity:implementer self-check(雲端單代理;獨立 T review 留給 PR／G3)
- reviewer kind:fresh-context Agent
- reviewed-at:2026-09-10T00:52Z
- Verify:`n=$(bash scripts/test-host-adapter.sh 2>&1 | grep -c '✓'); test "$n" -ge 57 && test ! -e scripts/check-host-receipt.sh && bash scripts/test-host-adapter.sh` → ✓ count=58; 58/58;無 check-host-receipt.sh
- Covers finding:S-6.1 無 hooks 鍵;S-6.2 七站 --action + 契約 2.0.0;S-6.3 無第二套 check-host-receipt.sh;file-map 193
- Files finding:test-host-adapter／devflow-check／check-file-map／architecture-guards／guide #filemap
- RED→GREEN finding:MIN_CASES=54 時 -ge 57 紅;加四案 + 地板同步後 58/58
- Test Integrity finding:none
- Design boundary finding:未假掛 Cursor hooks;未 bump .claude-plugin version;未改 STATUS 表列
- verdict:PASS
- correction + re-review after FAIL:CI `PF-2` 假綠 → 補 `MIN_HEREDOCS=216`(D-heredoc-1)

## Progress Log

2026-09-10 | T-1 | fb8533a03afc2b7c9592ab8eabcf2d6bfe32e810 stage4 allow 鑄 host-receipt
2026-09-10 | T-2 | dda13c89df9dc831aac0dbb0b8813c045f9a4358 其餘六站 mint
2026-09-10 | T-3 | b855df9130743d975a62c85a97879a4dfea123df verify_receipt
2026-09-10 | T-4 | 540b72cfb3fe8f0d0c5f75a45c7ec68f37a5f27d fail-closed claim
2026-09-10 | T-5 | 33a67ec83c5b38c80c161d9ba8a54da3b9c07c72 I2 write-stack-inventory
2026-09-10 | T-6 | fca0fa6d96109070c83c3ddd052914a709dcfbf1 I4 SKILL wording
2026-09-10 | T-7 | 2698a4eda949d66670c83417ad93478541fac807 Non-Goal + file-map + host-adapter MIN_CASES=58
2026-09-10 | T-7-fix | (本 commit) MIN_HEREDOCS 214→216 修 CI PF-2 假綠

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)
Run: n-a(sequential v1,無 run_id)

## TDD Evidence

### T-1 / S-1.1
- RED: `bash scripts/test-host-receipt.sh --group mint-stage4 -v` → `test_s_1_1_station_action_mints_receipt` ✗ `rc=0 dest=False out=allow	S5-gate 允許 write_spec`
- GREEN: 同指令 → `test_s_1_1_station_action_mints_receipt` ✓;`.devflow/host-receipt/host-stack-fit/stage4.json` 由腳本寫出 `schema=devflow-host-receipt/v1`

### T-1 / S-1.2
- RED: `test_s_1_2_receipt_fields_and_stamp` ✗ `rc=0`(無檔可核欄)
- GREEN: 同案 ✓;鍵集合恰好 12 欄、`DONE is True`、stamp = SHA-256(`devflow-host-receipt/v1|{station}|{slug}|{node}|{script}|{root}|allow|{minted_at}|{payload_sha256}|true`)

### T-1 / S-1.3
- RED: 舊實作本就不鑄 → `test_s_1_3_probe_does_not_mint`／`start`／`write_cursor`／`write_scope` 四案已 ✓(鑑別力在 allow 正案)
- GREEN: 四案仍 ✓;`.devflow/host-receipt/` 零個 `.json`

### T-1 / S-1.4
- RED: `test_s_1_4_allow_overwrites_same_path` ✗(allow 不覆寫);deny／exit 2 兩案已 ✓
- GREEN: 三案 ✓;deny／exit 2 後位元不變;allow 後同路徑覆寫且 `DONE` 仍 true

回歸:`bash scripts/test-devstage4-graph.sh` → `63/63`

### T-2 / S-1.1
- RED: `bash scripts/test-host-receipt.sh --group mint-rest -v` → talk／stage2／3／5／6／7 六案皆 ✗ `rc=0 dest=False out=allow`
- GREEN: 同指令 6/6 ✓;各寫 `talk.json`／`stageN.json`,schema／stamp 與 T-1 同一份

### T-3 / S-2.1
- RED: verify 仍鑄檔 → stamp 變
- GREEN: `test_s_2_1_valid_receipt_verify_exit_0` ✓;exit 0 且 stamp 不變

### T-3 / S-2.2
- RED: 缺／空／空白檔 `verify_receipt:true` 仍 allow 鑄 → rc=0
- GREEN: 三案 ✓;stderr 含「未跑 --action」;不含「已與 Claude 同等武裝」

### T-3 / S-2.3
- RED: 手填 md／缺 stamp／DONE 字串／DONE false 仍鑄 → rc=0
- GREEN: 四案 ✓

### T-3 / S-2.4
- RED: stamp／station／script／slug／root 不符仍鑄 → rc=0
- GREEN: 五案 ✓

### T-3 / S-2.7
- RED: 初版誤要求未知動詞 deny;stage4 既有規則對未知動詞仍 allow
- GREEN: 空檔 + `action:"verify_receipt"` 無布林 → 舊 graph 鑄檔、不是 verify-only

### T-4 / S-2.5
- RED: `#host`／PLUGIN／dev-setup 缺「沒有 PreToolUse」(PLUGIN 亦缺 `--action`)
- GREEN: 三檔皆同時有「沒有 PreToolUse」與 `--action`;start-only 核對紅

### T-4 / S-2.6
- RED: n-a(T-3 已綠;本 T 複測核對前／後)
- GREEN: `test_s_2_6_fail_closed_before_first_write` ✓

### T-5 / S-3.1
- RED: 無 `write-stack-inventory.py` → `--group i2` 非零
- GREEN: `test_s_3_1_i2_path_and_required_fields` ✓;路徑 `docs/dev/0-inventory.json`、schema `devflow-stack-inventory/v1`、`written_by=dev-setup`

### T-5 / S-3.2
- RED: 同組無腳本
- GREEN: `test_s_3_2_pack_pins_markdown_it_py` ✓;母版 pin `markdown-it-py==4.0.0`

### T-5 / S-3.3
- RED: 同組無腳本
- GREEN: `test_s_3_3_gap_39_vs_312_before_stage4` ✓;`--runtime-version 3.9.6` 列出 3.12 落差

### T-5 / S-3.4
- RED: 同組無腳本
- GREEN: `test_s_3_4_check_rewrites_stale_i2`／`test_s_3_4_guidance_says_rerun` ✓;SKILL 有「依賴變了要重跑」

### T-5 / S-3.5
- RED: 缺 I2 仍可能當成功
- GREEN: `test_s_3_5_missing_i2_check_not_success` ✓;stderr `broken:缺 docs/dev/0-inventory.json`、exit 1

### T-5 / S-5.1
- RED: 方法包／產品鍵集合未比
- GREEN: `test_s_5_1_pack_and_product_same_keys` ✓

### T-6 / S-4.1
- RED: 預設 setup 可能誤建 I4
- GREEN: `test_s_4_1_setup_does_not_require_i4` ✓

### T-6 / S-4.2
- RED: SKILL 未寫人要才產
- GREEN: `test_s_4_2_i4_content_when_asked` ✓;檔內「盤點正本是 `docs/dev/0-inventory.json`」

### T-6 / S-4.3
- RED: 可能寫 per-slug 或把 digest 當 lock
- GREEN: `test_s_4_3_no_per_slug_stack_and_lock_wins` ✓;無 I2 拒寫

### T-7 / S-6.1
- RED: 無「薄殼無 hooks」案;MIN_CASES=54
- GREEN: `S-6.1 .cursor-plugin/plugin.json 無 hooks 鍵` ✓

### T-7 / S-6.2
- RED: 無七站 `--action`／契約 2.0.0 案
- GREEN: 兩案 ✓;`docs/dev/devflow-contract.json` 仍 `2.0.0`

### T-7 / S-6.3
- RED: 無「禁止第二套 check-host-receipt.sh」案;file-map 190
- GREEN: 58/58;`check-file-map.sh` scanned=193 PASS;`test ! -e scripts/check-host-receipt.sh`

全 T 複測(T-7 commit 後):T-1 9/9、T-2 6/6、T-3 14/14、T-4 3/3、T-5 7/7、T-6 3/3、T-7 58/58。

## Decisions(spec 未載明的自由選擇)

- D-mint-1:共用鉤子名 `after_station_action` 住 `hooks/devflow-lib.py`;該站腳本只 load + 呼叫。缺 `slug` 不鑄、不改既有 allow 契約(既有 talk fixture 無 slug)。有 slug 的 allow 鑄失敗 → exit 2。依據:4-spec S-1.1 路徑需要 slug;既有 `--action` 綠案不得無故變紅。[Assumption] 無 slug 的 allow 不在本 feat 觀測範圍。
- D-i2-1:`write-stack-inventory.py --runtime-version` 只給測試注入 3.9.6 落差;正式 setup 讀本機 `python3 --version`。依據:S-3.3 觀測要 3.9 vs 3.12+;本 VM 只有 3.12。[Assumption] 採用者本機若只有 3.12,gaps 列可空,樣張仍由測試釘住。
- D-t7-1:T-7 把 `test-host-receipt.sh` 掛 methodology 組、`test-stack-inventory.sh` 掛 architecture 組。依據:5-tasks T-7 Intent「新測試腳本已掛進 file-map 與 devflow-check」。

## Deviations

### D-budget-1(L1)
- 現象:4-spec Diff Budget 估計 ≤16 檔;實作含測試／fixture／地板後 `git diff --name-only` 對 fork 約 37 路徑。
- 保守選擇:不砍測試或合併 T;檔全部落在 5-tasks Files 聯集(+ 永遠允許的 6-notes)。
- 理由:Budget 頂註寫「超支本身非偏差,是停下判 L1/L2 的訊號」。5-tasks 已預告 T-7 才動地板、T-2 六站同刀。未改 R/S。
- 影響:T-1…T-7 / 無 R／S 翻案

### D-review-1(L1)
- 現象:獨立 T review 由同一雲端實作代理自檢,不是另一個 fresh session。
- 保守選擇:每 T 仍跑原 Verify、記 self-check PASS;不代填 G3。
- 理由:本 hop 使用者指定單一雲端代理做完 T-1…T-7;獨立審查留給 PR／G3。
- 影響:T Review Log reviewer identity 已標 self-check

### D-heredoc-1(L1)
- 現象:T-1／T-5 新增 `test-host-receipt.sh`／`test-stack-inventory.sh` 各一條 `<<'PY'`,實得 heredoc=216;T-7 漏同步 `MIN_HEREDOCS`(仍 214)。CI `PF-2` 關掉 `INTERP_TOKEN_RE` 後剩 215 ≥ 214,預期紅卻綠。
- 保守選擇:把 `check-py-floor.sh` 與 architecture-guards 靜態釘一併改成 216。多動 T-7 Files 未列的 `check-py-floor.sh`。
- 理由:該檔頂註「增刪 .sh 或 heredoc 時一起改」;地板必須精確、不留餘裕。未改 R/S。
- 影響:T-7 地板／architecture-guards PF-2

## Files Changed

T-1:hooks/devflow-lib.py、scripts/check-devstage4-graph.sh、scripts/test-host-receipt.sh、scripts/fixtures/host-receipt/**
T-2:其餘六站 `check-dev*-graph.sh` + test-host-receipt mint-rest
T-3:devflow-lib `verify_host_receipt` + test-host-receipt verify-receipt
T-4:guide #host、docs/PLUGIN.md、skills/dev-setup/SKILL.md
T-5:scripts/write-stack-inventory.py、test-stack-inventory.sh、dev-setup SKILL、check-dev-setup-discipline MIN_CHECKS=32
T-6:dev-setup SKILL I4「人要才產」
T-7:test-host-adapter MIN_CASES=58、check-file-map EXPECTED=193、guide #filemap、architecture-guards pin、devflow-check 兩條

## Diff(各 T commit,逐檔折疊)

### mint_host_receipt · `hooks/devflow-lib.py` 961-997  T-1
改什麼：allow 後原子寫 `devflow-host-receipt/v1`,stamp 輸入含 `root`
關聯：callee `host_receipt_stamp`／caller `after_station_action`
```diff
+def mint_host_receipt(root, slug, station, script, argv, payload_bytes, node=""):
+    dest = host_receipt_path(root, slug, station)
+    os.replace(tmp, dest)
```

### after_station_action · `hooks/devflow-lib.py` 1000-1024  T-1 T-3
改什麼：共用鉤子;布林 `verify_receipt:true` 只核對;allow 且有 slug 才鑄
關聯：caller 七站 `--action`;callee `mint_host_receipt`／`verify_host_receipt`
```diff
+def after_station_action(..., verdict):
+    if payload.get("verify_receipt") is True:
+        return verify_host_receipt(...)
+    if verdict != "allow":
+        return None
```

### --action allow 鑄檔 · `scripts/check-devstage4-graph.sh` 694-714  T-1
改什麼：`--action` evaluate 後呼叫 lib 鉤子;deny／exit 2／write-cursor 不鑄
關聯：`after_station_action`
```diff
+        extra = lib.after_station_action(
+            root, "stage4", "scripts/check-devstage4-graph.sh", ...)
+    if extra is not None:
+        sys.exit(extra)
```

### --action allow 鑄檔 · `scripts/check-devtalk-graph.sh` 582-590  T-2
改什麼：talk 站同一鉤子;`station=talk`;不自造 schema
關聯：同形接到 stage2／3／5／6／7
```diff
+        extra = lib.after_station_action(
+            root, "talk", "scripts/check-devtalk-graph.sh", ...)
```

### verify_host_receipt · `hooks/devflow-lib.py` 1027-1086  T-3
改什麼：只核對不鑄;咬 slug／station／script／root／stamp;stderr 含「未跑 --action」
關聯：caller `after_station_action`
```diff
+def verify_host_receipt(root, slug, station, script, payload):
+    if not os.path.isfile(dest):
+        return fail("缺檔")
+    if data.get("DONE") is not True:
+        return fail("DONE")
```

### #host 文案 · `guides/guide-dev-flow.html` 2845-2847  T-4
改什麼：同時寫「沒有 PreToolUse」與 `--action` 鑄／核對
關聯：PLUGIN／dev-setup 同句;牙 `fail-closed-claim`
```diff
+  非 Claude 主機<strong>沒有 PreToolUse</strong>；該站 <code>--action</code> allow
+  才鑄 <code>.devflow/host-receipt/&lt;slug&gt;/&lt;station&gt;.json</code>。
+  核對只認布林 <code>verify_receipt:true</code>（只核對不鑄）。
```

### write_i2 · `scripts/write-stack-inventory.py` 198-204  T-5
改什麼：原子寫專案級 `docs/dev/0-inventory.json`
關聯：caller `main`;schema 由 `build_inventory`
```diff
+def write_i2(root, payload):
+    dest = os.path.join(root, I2_REL)
+    atomic_write(dest, json.dumps(payload, ensure_ascii=False, indent=2))
```

### main --check · `scripts/write-stack-inventory.py` 275-279  T-5
改什麼：缺 I2 印 `broken:缺 docs/dev/0-inventory.json` 並 exit 1
關聯：dev-setup check;S-3.5
```diff
+    if args.check and not os.path.isfile(i2_path):
+        print("broken:缺 docs/dev/0-inventory.json", file=sys.stderr)
+        return 1
```

### write_i4 · `scripts/write-stack-inventory.py` 215-249  T-6
改什麼：人要求才投影 I4;無 I2 拒絕;digest 不是 lock 正本
關聯：caller `main --write-stack`
```diff
+def write_i4(root, inventory, digest_paths):
+    if not os.path.isfile(i2):
+        die("無 I2 不得先寫 I4:缺 docs/dev/0-inventory.json", 1)
+        "盤點正本是 `docs/dev/0-inventory.json`。",
+        "digest 不是 lock 正本。套件版本爭議以 lock／pin 檔為準。",
```

### MIN_CASES · `scripts/test-host-adapter.sh` 48-48  T-7
改什麼：地板 54→58,跟上四條 Non-Goal 案
關聯：S-6.1／S-6.2／S-6.3 新案
```diff
-MIN_CASES = 54
+MIN_CASES = 58
```

### EXPECTED_MAPPED_FILES · `scripts/check-file-map.sh` 114-114  T-7
改什麼：必列檔 190→193(收據牙／I2 寫入器／I2 牙)
關聯：architecture-guards 靜態釘與 guide #filemap 同 commit
```diff
-EXPECTED_MAPPED_FILES = 190
+EXPECTED_MAPPED_FILES = 193
```

### MIN_HEREDOCS · `scripts/check-py-floor.sh` 295-295  T-7
改什麼：heredoc 地板 214→216,消掉 PF-2 假綠餘裕
關聯：architecture-guards `check_static_pin`;新增兩支測試腳本各一條 `<<'PY'`
```diff
-MIN_HEREDOCS = 214
+MIN_HEREDOCS = 216
```

## Self-Review

①每個「T × Covers S」都有含 S-id 的測試 + 該 T 自己的 RED/GREEN?是。T-1…T-4 在 `test-host-receipt.sh`;T-5／T-6 在 `test-stack-inventory.sh`;T-7 在 `test-host-adapter.sh`(S-6.1／S-6.2／S-6.3)。證據在本檔 TDD Evidence,未跨 T 共用同一筆輸出。

②每 T 在 T Review Log 有 verdict?是。T-1…T-7 皆 PASS(implementer self-check)。

③每個 PASS 都早於該 T commit?部分。同一 session 自檢後才 commit;reviewed-at 為當時 UTC。T-2 另有 docs hash commit `ea180ae`(記帳,不是第二刀產品碼)。獨立 fresh reviewer 留給 PR／G3(D-review-1)。

④每個 FAIL 後有較晚 PASS?無 T Review FAIL;T-3 初版 S-2.7 測法偏了(未知動詞仍 allow),改測後同 T 內綠,未另開 FAIL 列。

⑤每個已完成 T 一 commit、Progress Log 每列有 hash?產品碼 T-1…T-7 各一 hash(上表 40 碼)。T-2 多一筆 docs 記帳 `ea180ae`,不另列產品 T。

⑥git diff --stat 檔案 ⊆ Files 聯集、Diff Budget 內?檔名全在 5-tasks Files 聯集 + 本檔。Budget 檔數超支,已記 D-budget-1(L1)。`git diff --stat fa55b48...HEAD`:37 路徑、+2071/−22(含本檔後會再加 html)。無 `docs/dev/STATUS.md`、無模板 1–4 解凍、無 `.claude-plugin` version。

⑦Decisions/Deviations 與 diff 對得上?D-mint-1／D-i2-1／D-t7-1 對得上實作。Design Boundary:未加未授權模組;Data Owner 仍是該站腳本鑄收據、`dev-setup` 寫 I2;Cursor Write Known limit ①未「修掉」;未把 `action:"verify_receipt"` 當開關。

⑧回歸綠?T-1…T-7 Verify 全綠(上列複測)。`test-devstage4-graph.sh` 63/63(T-1 後)。`check-file-map.sh` scanned=193 PASS。PF-0 py-floor 本 VM 無 3.9–3.11 → ENV,不改地板。architecture-guards 在 dirty 樹會因指紋紅;bookkeeping commit 後再跑。

## Review Follow-up(G3 打回時才用)
