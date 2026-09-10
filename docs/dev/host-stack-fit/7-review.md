---
feature: host-stack-fit
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: agent-a-stage7-host-stack-fit
updated: 2026-09-10
baseline: v3.22.1 / 0a89ec8
contract: 2.0.0
issue: 149
---

# 7. 驗證 —— **這不是 G3 PASS**(Human G3 才填 PASS／REQUEST_CHANGES／HOLD)

> ## 白話摘要(給 owner)
>
> Stage 6(#160／`0a89ec8`)已合併:七站 `--action` allow 會鑄 `.devflow/host-receipt/<slug>/<station>.json`;
> `verify_receipt:true` 只核對不鑄;缺檔／手填／stamp／slug／root 對不上會紅且 stderr 含「未跑 --action」。
> `dev-setup` 寫專案級 I2 `docs/dev/0-inventory.json`;I4 `0-stack.md` 要人明確要求才寫。
> 契約仍 `2.0.0`,薄殼仍無 hooks。
>
> **請抽驗**:任挑 Coverage Matrix 一列的 `檔:行`;再跑一次
> `bash scripts/test-host-receipt.sh --group verify-receipt` 與
> `bash scripts/test-stack-inventory.sh --group i2`。
>
> **Known Limits 仍在**:① Cursor Write 無 hook;② stamp 非密碼學防偽;③ I2 不因 pull 自動刷新;
> ④ 間接相依可能晚爆;⑤ 本雲端 VM 無 Python 3.9–3.11 → PF-0／`devflow-check architecture` 紅(ENV);
> plugin cache 對齊仍手動(Non-Goal)。
>
> **Agent A 建議**:在接受 PF-0 為環境已知限的前提下,**建議 Human G3 PASS**。
> 本檔 `verdict:` 故意留 `PRE-REVIEW`,不代填 Human PASS。Agent B 會獨立挑戰本 PR。

> ## Reviewer 閱讀動線(**必留**)
>
> | 步 | 讀哪節 | 這步問的唯一問題 |
> |---|---|---|
> | 1 | **Verdict** | 判定是什麼?門檻表每一格是不是都有證據? |
> | 2 | **Exit Checklist** | 還缺什麼才能出貨?哪幾項要 owner 親自動? |
> | 3 | **附錄:本輪特有** | 本輪的爭點/分歧在哪,誰對? |
> | 4 | **Known Limits** | 有沒有一條是 owner 不能接受的? |
> | 5 | **抽驗一列** | 從 Coverage Matrix / Standards Axis / Spec Axis 任挑一列,照它給的 `檔:行` 去看。對得上就信剩下的,對不上就整份退回 |
>
> **只做一步就做第 5 步。**

## 限制聲明(讀取順序 + 身分)

| | |
|---|---|
| 審查者 | `agent-a-stage7-host-stack-fit`(fresh-context Cloud Agent A;**≠** Stage 6 實作 owner `cursor-cloud-agent`) |
| 讀取順序(可查) | ①`4-spec.md` ②`5-tasks.md` ③測試碼(`test-host-receipt.sh`／`test-stack-inventory.sh`／`test-host-adapter.sh` + fixtures) ④`git show 0a89ec8`(Stage 6 vs `cedfe69`) ⑤實作碼(`hooks/devflow-lib.py` mint／verify、七站腳本鉤子、`write-stack-inventory.py`) ⑥親跑 Verify／現象／回歸 → **之後才** ⑦`review-unlock` 讀 `6-implementation-notes.md` Self-Review |
| 圍欄 | `hooks/devflow-exec.sh review host-stack-fit` 曾武裝(步 0);回歸前 `stop` 以免測試寫入被擋。doctor:`COMPATIBLE`(契約 2.0.0) |
| 本輪性質 | 獨立 Stage 7 交接文件;`verdict: PRE-REVIEW`;**不是 G3 PASS**。建議 Human 審完再填 PASS／REQUEST_CHANGES／HOLD。建議路徑:Human 抽驗 + Agent B 挑戰本 PR |

## Coverage Matrix

自建(grep 測試函式名含 S-id ↔ 4-spec S 清單;**未先讀** Self-Review)。

| S-id | 測試 | 狀態 |
|---|---|---|
| S-1.1 | `test_s_1_1_station_action_mints_receipt` + talk／stage2／3／5／6／7;`scripts/fixtures/host-receipt/run_cases.py:147-166,687-694` | ✅ mint-stage4+mint-rest |
| S-1.2 | `test_s_1_2_receipt_fields_and_stamp` `run_cases.py:168-200` | ✅ |
| S-1.3 | `test_s_1_3_probe/start/write_cursor/write_scope_does_not_mint` `run_cases.py:679-682` | ✅ |
| S-1.4 | `test_s_1_4_deny/exit2/allow_overwrites` `run_cases.py:683-685` | ✅ |
| S-2.1 | `test_s_2_1_valid_receipt_verify_exit_0` `run_cases.py:439` | ✅ |
| S-2.2 | missing／empty／blank ×3 `run_cases.py:697-699` | ✅ |
| S-2.3 | handfilled／no-stamp／done-str／done-false ×4 `run_cases.py:700-703` | ✅ |
| S-2.4 | stamp／station／script／slug／root ×5 `run_cases.py:704-708` | ✅ |
| S-2.5 | `test_s_2_5_start_only_not_armed` + `test_s_2_5_host_copy_has_pretooluse_and_action` `run_cases.py:712-714` | ✅ |
| S-2.6 | `test_s_2_6_fail_closed_before_first_write` `run_cases.py:713` | ✅ |
| S-2.7 | `test_s_2_7_action_verify_receipt_is_not_a_switch` `run_cases.py:650-672` | ✅(見 Spec Axis F-1 文案) |
| S-3.1 | `test_s_3_1_i2_path_and_required_fields` `stack-inventory/run_cases.py:63` | ✅ |
| S-3.2 | `test_s_3_2_pack_pins_markdown_it_py` `:87` | ✅ |
| S-3.3 | `test_s_3_3_gap_39_vs_312_before_stage4` `:112` | ✅ |
| S-3.4 | `test_s_3_4_check_rewrites_stale_i2` + `test_s_3_4_guidance_says_rerun` `:129,:149` | ✅ |
| S-3.5 | `test_s_3_5_missing_i2_check_not_success` `:157` | ✅ |
| S-4.1 | `test_s_4_1_setup_does_not_require_i4` `:194` | ✅ |
| S-4.2 | `test_s_4_2_i4_content_when_asked` `:207` | ✅ |
| S-4.3 | `test_s_4_3_no_per_slug_stack_and_lock_wins` `:242` | ✅ |
| S-5.1 | `test_s_5_1_pack_and_product_same_keys` `:171` | ✅ |
| S-6.1 | host-adapter「S-6.1 .cursor-plugin/plugin.json 無 hooks 鍵」`scripts/test-host-adapter.sh:777` | ✅ |
| S-6.2 | 七站仍接 `--action` + 契約 2.0.0 `test-host-adapter.sh:798-811` | ✅ |
| S-6.3 | 無 `check-host-receipt.sh` + diff 無模板／STATUS `test-host-adapter.sh:815`;`git diff --name-only 0a89ec8^..0a89ec8` | ✅ |
| 既有測試套件(回歸) | 見 Verification Evidence:methodology／contracts／render 全綠;architecture PF-0 ENV 紅;host 三套全綠 | ✅/⚠ |

**Verify 親跑**(5-tasks 原指令;2026-09-10T0842Z UTC):

```
mint-stage4: CASE_COUNT=9 EXIT=0  [host-receipt] passed=9 failed=0
mint-rest:   CASE_COUNT=6 EXIT=0  passed=6 failed=0
verify-receipt: CASE_COUNT=14 EXIT=0 passed=14 failed=0
fail-closed-claim: CASE_COUNT=3 EXIT=0 passed=3 failed=0
i2: CASE_COUNT=7 EXIT=0  [stack-inventory] passed=7 failed=0
i4: CASE_COUNT=3 EXIT=0  passed=3 failed=0
host-adapter: CHECK_COUNT=58 EXIT=0  === test-host-adapter:58/58 ===
全量: test-host-receipt 32/32; test-stack-inventory 10/10
```

## Verification Evidence

- Source SHA: 0a89ec85ae2cf3ee0c555b82441caa323e77c10f
- Final Fresh Run ID: 2026-09-10T0842Z-agent-a-r1
- Entry point: `bash scripts/check-spec-gate.sh docs/dev/host-stack-fit/4-spec.md && bash scripts/check-host-adapter.sh && bash scripts/devflow-check.sh`
- Toolchain: python3.12.3; markdown-it-py==4.0.0; contract 2.0.0; runtime 3.22.1

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| check-spec-gate／check-host-adapter／七站 graph `--action` 自檢／devflow-check | Final Fresh entry point(上列三指令) | fail | 前三段綠:spec-gate 6/6;host-adapter PASS;mint-rest 6/6+adapter 58/58。`devflow-check all`:methodology 44、contracts 5、render 2 全綠;architecture PF-0 無 3.9–3.11 直譯器 exit 2(唯一產品外紅;PF-2 仍綠 MIN_HEREDOCS=214) | |
| check-spec-gate | `bash scripts/check-spec-gate.sh docs/dev/host-stack-fit/4-spec.md` | pass | exit 0;6/6 形狀全過;23 條 S | |
| check-host-adapter | `bash scripts/check-host-adapter.sh` | pass | exit 0;PASS host-adapter | |
| 七站 graph --action 自檢 | `bash scripts/test-host-receipt.sh --group mint-rest` | pass | mint-rest 6/6;host-adapter 七站 deny+S-6.2 綠 | |
| devflow-check | `bash scripts/devflow-check.sh all` | fail | methodology44 contracts5 render2 綠;architecture PF-0 exit 2 | |
| Mutation | | n-a | | Explicitly excluded(4-spec Verification Profile) |
| e2e／Playwright | | n-a | | Explicitly excluded |
| Race／stress | | n-a | | Explicitly excluded |
| Supply chain | | n-a | | Conditional:本 feat 未改真 pin／requirements 正本(只加 fixture 複本) |

**Gauntlet 降級聲明**:本 VM 無 Python 3.9–3.11 → Required 束中 `devflow-check` 無法全綠(PF-0 ENV)。`devflow-evidence-gauntlet.sh --review-file` 會報 E6／E7。逐層手動實跑證據見上表與附錄 A4;不得把 gauntlet 未全綠默認為已過。Human 若接受 PF-0=Known Limit ⑤,方可把 Evidence 契約視為「產品面通過、環境地板待補」。

整合回歸(步 2c):`docs/dev/tools/devflow-integration-regression.sh --integration origin/main --fork-sha 0a89ec85ae2cf3ee0c555b82441caa323e77c10f` → `STATUS: N_A_NO_INCOMING`;FORK=HEAD=INTEGRATION=`0a89ec85ae2cf3ee0c555b82441caa323e77c10f`(refs/remotes/origin/main)。

## Negative Constraint Mapping

| Constraint | Test/Layer | Status |
|---|---|---|
| 不得用 probe／start／write-cursor／write-scope 冒充鑄造(S-1.3) | `test_s_1_3_*` ×4 | pass |
| 不得把空檔／手填／缺 DONE／slug 或 root 對不上當有效收據(S-2.2／S-2.3／S-2.4) | verify-receipt 12 負向案 | pass |
| 不得把 `action:"verify_receipt"` 當核對開關(S-2.7) | `test_s_2_7_*` | pass |
| 不得出現「已與 Claude 同等武裝」(S-2.2／S-2.5) | verify_fail_ok + host_copy | pass |
| 不得強制每專案 I4(S-4.1) | `test_s_4_1_*` | pass |
| 不得把 digest 當 lock 正本(S-4.3) | `test_s_4_3_*` | pass |
| 不得加假 PreToolUse／改鬆 `--action`／解凍模板／修 cache／bump plugin(S-6.1～S-6.3) | host-adapter S-6.* + `git diff --name-only 0a89ec8^..0a89ec8` | pass |

## 執行記錄(dev-run 引擎案;手動實作留白)

Stage 6 為雲端手動／單代理實作(見 6-notes);本 Stage 7 為獨立 Agent A 審查,無 dev-run ledger。本節留白。

## 現象證據(逐 S,對照 4-spec 的「觀測」欄)

Reviewer 親自實跑(暫存根;指令與 exit 如下)。不相符則 ❌。

| S-id | 觀測方式(引 4-spec) | 實跑證據 | 相符? |
|---|---|---|---|
| S-1.1／S-1.2 | 暫存根跑 stage4 `--action` allow;讀 JSON／自算 stamp | `exit=0 file=True schema=devflow-host-receipt/v1 DONE=True stamp_ok=True root_match=True` | ✅ |
| S-1.3 | `--probe` 空樹 | `probe_exit=1 receipt_jsons=0` | ✅ |
| S-1.4 | 測試群組 mint-stage4 deny／exit2／overwrite | passed=9(含三案) | ✅ |
| S-2.1 | mint 後 `verify_receipt:true` | `mint_exit=0 verify_exit=0 stamp_unchanged=True` | ✅ |
| S-2.2 | 缺檔 verify | `exit=1` stderr=`未跑 --action(缺檔)`;無「同等武裝」 | ✅ |
| S-2.3／S-2.4 | verify-receipt 群組 | 14/14 | ✅ |
| S-2.5／S-2.6 | fail-closed-claim | 3/3;文案含「沒有 PreToolUse」與 `--action`(`guides/guide-dev-flow.html:2856-2858`,`docs/PLUGIN.md:63`,`skills/dev-setup/SKILL.md:52-54`) | ✅ |
| S-2.7 | payload `action:"verify_receipt"` 無布林 | `exit=0 minted=True has_未跑=False`(未進 verify-only) | ✅(核心);文案見 F-1 |
| S-3.1／S-3.2／S-3.3 | `write-stack-inventory.py --root <pack> --runtime-version 3.9.6` | schema=`devflow-stack-inventory/v1`;pin `markdown-it-py==4.0.0`;gaps 含 `3.9.6`／`3.12+`／`markdown-it-py==4.0.0`;預設無 I4 | ✅ |
| S-3.4／S-3.5 | i2 群組 | 7/7;`skills/dev-setup/SKILL.md:471`「依賴變了要重跑」 | ✅ |
| S-4.1／S-4.2／S-4.3 | 預設無 I4;`--write-stack` 後有正本句與 digest 非 lock 句 | `default_i4=False`;asked 後兩句皆在 | ✅ |
| S-5.1 | pack vs product 鍵集合 | i2 群組案綠 | ✅ |
| S-6.1 | 讀 `.cursor-plugin/plugin.json` | `hooks` 鍵不存在 | ✅ |
| S-6.2 | 七腳本 `[ "${1:-}" = "--action" ]` + 契約 | 七處皆有;契約 `2.0.0`;plugin version 仍 `3.22.1` | ✅ |
| S-6.3 | Stage 6 檔名清單 | 無 `_templates/1-4`、無 `docs/dev/STATUS.md`、無假 `check-host-receipt.sh` | ✅ |

## 截圖槽

本 feat 無產品前端;現象為 CLI／JSON。截圖槽 N/A(無 shots/ 定名檔 → 產檔器顯示佔位即可)。

### 進場
- data-shot: n-a-cli
- src: shots/n-a.png
- caption: 無 GUI 進場;牙在 shell exit／JSON
- 進場:從列表打開已存在紀錄。不准新增。
- hang-point: `.e2e` n-a

## Operational Walkthrough

| S-id | 角色 | 真實目標 | 系統操作 | 系統外步驟 | 等待/例外 | 結果 |
|---|---|---|---|---|---|---|
| S-1.1 | 開工 agent | 留下已跑 `--action` 的收據 | 跑該站 `--action` allow | 終端機 | deny／exit 2 不鑄;修好重跑 | ✅ 人能指著檔說在 |
| S-2.1／S-2.5／S-2.6 | 開工 agent／owner | 宣稱可寫碼前先有牙 | `verify_receipt:true` | owner 看紅就否決「已武裝」 | 紅 → 先鑄再核 | ✅ start-only 不能冒充;Cursor Write 仍無 hook(Known limit ①) |
| S-3.1／S-3.3／S-3.4 | owner／採用者 | 進 Stage 4 前看見落差 | `dev-setup` check 寫 I2 | 換 3.12+ venv | pull 不自動改 I2 | ✅ gaps 提早落檔 |
| S-4.1／S-4.2 | 採用者 | 不要每專案強制 I4 | 預設只 I2;要才 `--write-stack` | — | 缺 I4 ≠ broken | ✅ |
| S-6.1 | owner | 不造假 hook | 審 `.cursor-plugin/plugin.json` | — | 發現 hooks 鍵就打回 | ✅ |
| 其餘純內部 S | — | — | — | — | — | 不適用(4-spec 已標) |

## Design Integrity Check(Design Boundary Contract = `applicable`)

1. **依賴反向被間接繞過**:未命中 —— mint／verify 住 `hooks/devflow-lib.py:944-1086`;七站只呼叫 `after_station_action`;I2 writer 不讀收據。
2. **資料所有權被繞過寫入**:未命中 —— 收據只由該站腳本鑄;I2 由 `write-stack-inventory.py`／dev-setup 寫;產品碼不當收據正本。
3. **相容性破壞包成新增**:未命中 —— 既有 allow／deny／exit 0／1／2 不變;只加選布林與鑄檔副作用(`devflow-lib.py:1008-1024`)。
4. **一致性邊界被拆解**:未命中 —— allow 與鑄檔同次;鑄失敗回 2(`:1021-1023`)。
5. **宣告的 Test seam 未被使用**:未命中 —— 暫存根跑 `--action`／writer;測試名含 S-id。
6. **Known design limit 被悄悄「解決」**:未命中 —— Cursor Write 仍無 hook;stamp 仍非密碼學防偽;I2 仍不因 pull 自動刷新。

## Standards Axis

- F-1 🟡 `docs/dev/host-stack-fit/4-spec.md` S-2.7 括號句「未知動詞 → 既有 deny」vs 實作／測試 | 問題:stage4 對非 LOCKED 未知 `action` **既有行為是 allow**(實跑 `allow\tS5-gate 允許 verify_receipt`;測試註解 `run_cases.py:660-661`)。核心契約「布林才是核對開關」成立,但 spec 括號與既有 graph 不符。 | 建議:G3 後 fast-lane 改 S-2.7 括號為「未知動詞依既有 graph(stage4 非 LOCKED → allow)」,或另開票收緊未知動詞 —— **不擋本 hop 出貨**(不動 R/S 行為正本:只認布林)。影響 S-2.7。
- F-2 🟢 `6-implementation-notes.md` D-review-1 | Stage 6 T Review 為 implementer self-check | 本 Stage 7／Agent B／Human G3 補四眼。影響流程可信度,非產品碼。
- F-3 🟢 Diff Budget | 實作 ~40 檔 > 估 ≤16 | 已記 6-notes D-budget-1(L1);內容仍在 Files 聯集。

Design Boundary 四項(Standards 加查):
- **Dependency Direction**:符合 —— 腳本 → lib;setup → writer;無反向。
- **Boundary Leakage**:符合 —— 收據 schema 只經正規路徑;無第二家族 `check-host-receipt.sh`。
- **Data Ownership**:符合 —— 鑄造權在該站腳本;盤點權在 dev-setup／writer。
- **Interface Stability**:符合 —— additive(`verify_receipt` 缺欄=舊行為);契約仍 2.0.0;plugin 未升版。

無 🔴。

## Spec Axis

- R-1 符合(S-1.1…S-1.4 綠;七站鉤子 `after_station_action` 於各 `check-dev*-graph.sh`)。
- R-2 符合(S-2.1…S-2.7 綠;只認 `payload.get("verify_receipt") is True` at `devflow-lib.py:1008`)。
- R-3 符合(I2 schema／母版 pin／gaps／缺檔 check 紅)。
- R-4 符合(預設無 I4;人要求才寫;digest 非正本)。
- R-5 符合(S-5.1 pack／product 鍵集合)。
- R-6 符合(S-6.1…S-6.3;契約 2.0.0;無模板解凍／STATUS／假 hooks)。
- 6-notes Deviations／Decisions:D-mint-1／D-i2-1／D-t7-1／D-heredoc-1／D-budget-1／D-review-1 與 diff 對得上;無未記 L2。
- Design Boundary 契約逐條:符合;Known design limit ①–④ 未被悄悄修掉。
- F-1(上軸)為 **spec 括號 vs 既有 graph** 文案漂移,不改 R-2 行為判定。

## 變更架構圖

```text
[七站 --action 腳本]
   talk/stage2..stage7
        |
        v
[hooks/devflow-lib.py]
   after_station_action
     |-- verify_receipt:true --> verify_host_receipt (只讀)
     |-- allow + slug --------> mint_host_receipt ----+
                                                      |
                                                      v
                                      .devflow/host-receipt/<slug>/<station>.json
                                      (gitignore; stamp 含 root)

[skills/dev-setup] --> [scripts/write-stack-inventory.py]
                            |-- 預設 --> docs/dev/0-inventory.json (I2)
                            |-- --write-stack --> docs/dev/0-stack.md (I4 投影)

[說明] guide #host / PLUGIN.md / dev-setup SKILL
       「沒有 PreToolUse」+「--action」鑄／核

[地板] test-host-receipt / test-stack-inventory / test-host-adapter
       + file-map 193 + architecture-guards + devflow-check 掛載
```

## Diff(merge-base = `cedfe69`..`0a89ec8`,逐檔折疊)

完整位元:`git show 0a89ec8`。摘要 +N/-N(產品相關):

<details>
<summary>hooks/devflow-lib.py +167 — mint／verify／after_station_action</summary>

```
host_receipt_stamp / mint_host_receipt / after_station_action / verify_host_receipt
路徑 .devflow/host-receipt/<slug>/<station>.json;stamp 含 root;os.replace 原子寫
verify 失敗 stderr「未跑 --action」;只認 JSON 布林 verify_receipt is True
```
</details>

<details>
<summary>scripts/check-dev{talk,stage2..7}-graph.sh 各 ~+23/-2 — 呼叫 after_station_action</summary>

```
evaluate 後 extra = lib.after_station_action(...); extra is not None → sys.exit(extra)
deny／exit 2／--write-cursor 不走鑄造成功路徑
```
</details>

<details>
<summary>scripts/write-stack-inventory.py +292 — I2／選配 I4</summary>

```
schema devflow-stack-inventory/v1; --check 缺 I2 → broken; --write-stack 才寫 0-stack.md
```
</details>

<details>
<summary>scripts/test-host-receipt.sh +63 / fixtures/host-receipt/run_cases.py +741</summary>

```
groups: mint-stage4(9) mint-rest(6) verify-receipt(14) fail-closed-claim(3)
```
</details>

<details>
<summary>scripts/test-stack-inventory.sh +39 / fixtures/stack-inventory/run_cases.py +293</summary>

```
groups: i2(7) i4(3)
```
</details>

<details>
<summary>scripts/test-host-adapter.sh +52/-1 — MIN_CASES=58 + S-6.*</summary>

```
無 hooks 鍵;七站 --action;契約 2.0.0;無 check-host-receipt.sh
```
</details>

<details>
<summary>guides/guide-dev-flow.html / docs/PLUGIN.md / skills/dev-setup/SKILL.md — 主機文案</summary>

```
同時出現「沒有 PreToolUse」與「--action」鑄／核對;`start` ≠ 已武裝
I2／I4／「依賴變了要重跑」
```
</details>

<details>
<summary>地板:check-file-map EXPECTED=193; check-dev-setup-discipline MIN=32; architecture-guards; devflow-check 掛兩牙</summary>

```
+ test-host-receipt.sh / test-stack-inventory.sh / write-stack-inventory.py
```
</details>

<details>
<summary>docs/dev/host-stack-fit/6-implementation-notes.md(+html) — Stage 6 筆記</summary>

```
T-1…T-7 記錄;Self-Review;D-* Decisions
```
</details>

Banned 路徑不在 diff:無 `_templates/{1-4}`、無 `docs/dev/STATUS.md`、無 `.claude-plugin` version bump、無 `.cursor-plugin` hooks 鍵。

## Verdict

**PRE-REVIEW**(Agent A 自審落點;**不是** Human G3 PASS)。

| 門檻 | 證據 | Agent A 判讀 |
|---|---|---|
| 本次 S 全綠 | Coverage Matrix 23/23 ✅ | 通過 |
| 既有回歸綠 | methodology／contracts／render 全綠;host 三套全綠;architecture **PF-0 ENV 紅** | 產品回歸通過;全套 `devflow-check all` 因環境未全綠 |
| 現象證據逐 S 相符 | 上表 ✅ | 通過 |
| Evidence 契約 | Required 三層 pass;`devflow-check` 層 fail(PF-0) | 機械面未全綠;建議 Human 明示接受 PF-0 |
| 無 🔴 | Standards／Spec 無 🔴;僅 F-1 🟡 文案 | 通過(加嚴門檻) |

**建議 Human**:接受 Known Limits(含 PF-0)→ **G3 PASS**;若要求本機先有 3.9–3.11 讓 architecture 全綠再出貨 → **HOLD**。勿代填。

重驗輪次:1(首輪 PRE-REVIEW)。

## Known Limits

| # | 限制 | 嚴重度 | 建議處置 |
|---|---|---|---|
| 1 | Cursor Write 工具沒有 hook;人可跳過核對仍改檔 | 高(設計已知) | park:4-spec Known design limit ①;牙停在收據＋不得宣稱武裝 |
| 2 | stamp 不是對抗已讀規格者的密碼學防偽 | 中 | park:limit ②;防空檔／手填／改欄 |
| 3 | I2 不因 `git pull` 自動刷新;依賴變了要人重跑 setup | 中 | park:limit ③;指引句已在 |
| 4 | 間接／transitive 相依仍可能晚爆 | 中 | park:limit ④／D1 |
| 5 | 本雲端／部分 CI 無 Python 3.9–3.11 → PF-0／`check-py-floor` 無法取證,`devflow-check architecture` 紅 | 中(ENV) | park:設 `DEVFLOW_PY_FLOOR_BIN` 或裝 3.9–3.11;非本 feat 產品回歸。PF-2 仍綠 |
| 6 | 現場 plugin cache Refresh 仍手動(Non-Goal／OC-4) | 低 | park:另票;本 feat 不做 |
| 7 | Stage 6 T Review 為同一代理 self-check(D-review-1) | 流程 | 本 Stage 7 + Agent B + Human G3 補四眼 |

## Exit Checklist(全勾才算 shipped)

- [x] **Design Boundary finding 全數處置**:無未授權 Boundary 變更;F-1 為 spec 括號文案(L1 建議後修),非 Boundary 違規。n-a 處置項:無 🟡 Boundary。
- [ ] Quiz(**不可逆／公開契約副作用 → 建議做**):見附錄 A3;Human／approver 答對後再 merge
- [x] 整合回歸已在 Final Fresh **之前**完成:`STATUS=N_A_NO_INCOMING`;FORK=HEAD=INTEGRATION=`0a89ec85ae2cf3ee0c555b82441caa323e77c10f`(origin/main)。本 PR 不改產品碼。
- [ ] PR → develop／main(本 draft PR 只含 Stage 7 文檔;**勿直上 master 以外政策**;Human merge)
- [ ] 4-spec delta 已併入 `docs/specs/<domain>.md`(本 repo `docs/specs/` 無對應 living 條 → Human 確認 n-a 或另開 living)
- [ ] STATUS.md 已更新為 shipped(**合併後**由合併者做,不塞本 branch)
- [ ] 7-review frontmatter status: shipped(Human G3 PASS 後)
- [ ] 7-review.html 已產生(本 PR 會產;`build-gate-twin` + `build-stage7-html`)
- [ ] feature branch 已刪 / worktree 已清(merge 後)

## 附錄:本輪特有

### A1　讀取順序聲明(防錨定)

1. 4-spec / 5-tasks  
2. 測試與 Stage 6 diff(`0a89ec8`)／實作碼  
3. 自建 Coverage Matrix + 親跑 Verify／現象／回歸  
4. 才 `review-unlock` 讀 6-notes Self-Review  

與作者主張差異:作者已標 D-review-1／PF-0／D-budget-1 —— 獨立複核同意。新發現僅 F-1(S-2.7 括號 vs 既有 allow-unknown)。

### A2　Agent B 可證偽點(請挑戰)

1. `hooks/devflow-lib.py:1008` 是否真的只認布林 `is True`(字串 `"true"` 必須紅)?  
2. S-2.7 實跑是否可能被解讀成「未知動詞 allow = fail-open 核對」?(應否:未進 verify-only)  
3. PF-0 紅是否掩蓋了本 feat 引入的其他 architecture 失敗?(對照:清掉 `.devflow/runs` 後唯一紅為 PF-0)  
4. Coverage 是否漏 S?(23 條 S 是否都有含 S-id 的案?)

### A3　Quiz(給 approver;不可逆契約副作用)

1. 非 Claude 主機要證明「已跑該站 `--action`」,看哪個路徑的什麼檔?  
2. 核對開關是哪個 JSON 欄／型別?`action:"verify_receipt"` 可不可以當開關?  
3. 只跑 `devflow-exec start`、沒有收據時,`verify_receipt:true` 的 exit 與 stderr 關鍵字是什麼?  
4. I2 與 I4 哪個是盤點正本?預設 setup 會不會寫 `0-stack.md`?  
5. 本 feat 之後契約版本、薄殼 `hooks` 鍵、是否新增 `check-host-receipt.sh`?

### A4　環境與工具備註

- 初跑 `devflow-check` 曾因缺 `markdown-it-py` 紅;本 session 已 `pip install markdown-it-py==4.0.0` 後 render／gate-twin 綠。
- 武裝 Stage 7 review 時,部分 graph 測試會被 write-scope 擋 → 回歸前必須 `devflow-exec stop`。
- 殘留 `.devflow/runs`(無 attempt 事件)會讓 `check-model-tiering` NOT-PARSED → 清掉再跑。
- **Gauntlet 實跑**(Source SHA = `0a89ec85ae2cf3ee0c555b82441caa323e77c10f` = 當時 HEAD):

```
❌ evidence gauntlet: 3 violation(s) in 48 checks — docs/dev/host-stack-fit/7-review.md
  - E6: 「check-spec-gate／check-host-adapter／七站 graph `--action` 自檢／devflow-check」fail —— Gauntlet 有失敗層,不得宣告 Stage 7 PASS
  - E6: 「devflow-check」fail —— Gauntlet 有失敗層,不得宣告 Stage 7 PASS
  - E7: required layer「check-spec-gate／check-host-adapter／七站 graph `--action` 自檢／devflow-check」缺席或未 pass(unverified/n-a 不滿足 required)
```

  此三條皆源自 PF-0 ENV(無 3.9–3.11),與產品 S 綠無關。降級=逐層手動實跑已落 Verification Evidence;Agent A **不**把 gauntlet 未全綠寫成 PASS。
- 4-spec Required layers 用全形 `／` 串成單一 token(gauntlet 不拆 `／`);Evidence 表首列層名與此 token 全等。
- `7-review.html` 以 `docs/dev/tools/build-gate-twin.py /workspace host-stack-fit 7-review` 為準(動線五格)。`build-stage7-html.py` 會覆寫同檔且無 shots 時較瘦;本 PR 最終保留 twin。
### A5　與 Stage 6 Self-Review 對照裁斷

| 作者主張 | 獨立複核 |
|---|---|
| 全 S 有含 S-id 測試 | ✅ 同意(矩陣) |
| T Review self-check | ✅ 同意;本檔補獨立審 |
| PF-0 ENV | ✅ 同意;再現 |
| D-heredoc-1 保 PF-2 | ✅ 同意;PF-2 仍綠 |
| 無 L2／無假 hook／契約 2.0.0 | ✅ 同意 |
| (未提)S-2.7 括號 vs allow-unknown | 本輪 F-1 🟡 |
