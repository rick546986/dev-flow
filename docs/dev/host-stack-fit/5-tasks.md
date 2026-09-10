---
feature: host-stack-fit
stage: 5-tasks
status: approved
owner: rick
updated: 2026-09-09
execution:
  mode: sequential
  max_parallel_tasks: 3
  rebuild_integration_on_rework: true
---

# 5. 任務

> 把 4-spec（G2 PASS、`verdict: PASS`、契約 `2.0.0`）切成可派工的縱切。
> 本 hop **只寫任務**，不改 hooks／skills 正文、不 bump plugin、不改 `STATUS.md` 表列。
> 追蹤:[#149](https://github.com/rick546986/dev-flow/issues/149)。

## 開工前提

Stage 4 已核准。牙是腳本鑄收據 + `verify_receipt:true`，不是假 PreToolUse，也不是第二套 `check-host-receipt.sh`。Cursor Write 工具沒有 hook（Known limit ①）。I2 是專案級 pin + 第一層 `direct_deps`；I4 選配且只有 `docs/dev/0-stack.md`。契約維持 `2.0.0`。

## T-1 打通 stage4 --action allow 鑄出一份可核對的 host-receipt
- [ ] 未完成
- Covers: R-1 / S-1.1, S-1.2, S-1.3, S-1.4
- Files: hooks/devflow-lib.py, scripts/check-devstage4-graph.sh, scripts/test-host-receipt.sh, scripts/fixtures/host-receipt/
- Verify: `n=$(bash scripts/test-host-receipt.sh --group mint-stage4 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 8 && bash scripts/test-host-receipt.sh --group mint-stage4`
- Blocked-by: —
- Intent: stage4 `--action` allow 之後，`.devflow/host-receipt/<slug>/stage4.json` 由腳本寫出 `devflow-host-receipt/v1`，deny／exit 2／probe／start／write-cursor／write-scope 都不鑄
- Boundaries: 本 T 只打通 stage4 這一站的鑄檔縱切（S-1.1 其餘六站留給 T-2）。共用 mint 函式住 `hooks/devflow-lib.py`，stamp 輸入必須含專案 `root`，寫入用 `os.replace` 或同等原子覆寫。路徑鎖定 `.devflow/host-receipt/<slug>/<station>.json`。禁止新開 `check-host-receipt.sh`、禁止 probe 冒充鑄造、禁止改鬆既有 deny／exit 2。產品碼與 I2 不得當收據正本。Actor=開工 agent；Goal=留下「已跑該站 --action」的腳本鑄收據；Authority=腳本 allow 才鑄；Recovery=deny 或契約缺失不鑄，修好後重跑 allow。

## T-2 把同一套鑄檔接到其餘六站 --action
- [ ] 未完成
- Covers: R-1 / S-1.1
- Files: scripts/check-devtalk-graph.sh, scripts/check-devstage2-graph.sh, scripts/check-devstage3-graph.sh, scripts/check-devstage5-graph.sh, scripts/check-devstage6-graph.sh, scripts/check-devstage7-graph.sh, scripts/test-host-receipt.sh, scripts/fixtures/host-receipt/
- Verify: `n=$(bash scripts/test-host-receipt.sh --group mint-rest -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-host-receipt.sh --group mint-rest`
- Blocked-by: T-1
- Intent: talk 與 stage2／3／5／6／7 的 `--action` allow 也各自寫出對應 `talk.json`／`stageN.json`，schema 與 stamp 規則與 T-1 同一份
- Boundaries: 六支腳本只准加呼叫 T-1 共用 mint 的鉤子，不准各站自造第二份 schema 或第二條路徑。station 檔名鎖定 talk／stage2…stage7。禁止改鬆 `[ "${1:-}" = "--action" ]`、禁止讓 `--probe` 代替執法、禁止 bump plugin。Files 超過五檔是因為可觀測行為是「其餘六站同樣鑄檔」同一刀，不是按架構層切開。

## T-3 同一支腳本認 verify_receipt:true 並咬 root／slug／station／script
- [ ] 未完成
- Covers: R-2 / S-2.1, S-2.2, S-2.3, S-2.4, S-2.7
- Files: hooks/devflow-lib.py, scripts/check-devstage4-graph.sh, scripts/test-host-receipt.sh, scripts/fixtures/host-receipt/
- Verify: `n=$(bash scripts/test-host-receipt.sh --group verify-receipt -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 14 && bash scripts/test-host-receipt.sh --group verify-receipt`
- Blocked-by: T-2
- Intent: `verify_receipt:true` 時同一支該站腳本只核對不鑄；有效收據 exit 0，缺檔／空檔／手填／stamp 或身分不符皆紅且 stderr 含「未跑 --action」；`action:"verify_receipt"` 不是核對開關
- Boundaries: 核對開關只有 JSON 布林 `verify_receipt:true`；缺欄=舊 graph 裁決。核對必須同時成立：`receipt.slug`==路徑 slug==`--action` slug、`receipt.station`／`script` 對上呼叫中的腳本、`receipt.root`==本次核對專案根。verify 只讀不寫。禁止把 `action:"verify_receipt"` 當第二把鑰匙或 fail-open。stdout／stderr 不得出現「已與 Claude 同等武裝」。T-2 已把共用鉤子接到七站的話，本 T 只加厚鉤子裡的 verify 分支，不必再抄七份。Actor=開工 agent；Goal=證明本站已有腳本鑄收據才能宣稱可寫碼；Recovery=紅了先重跑該站 `--action` 鑄檔再核。

## T-4 擋住 start-only 武裝宣稱並釘主機文案
- [ ] 未完成
- Covers: R-2 / S-2.5, S-2.6
- Files: guides/guide-dev-flow.html, docs/PLUGIN.md, skills/dev-setup/SKILL.md, scripts/test-host-receipt.sh, scripts/fixtures/host-receipt/
- Verify: `n=$(bash scripts/test-host-receipt.sh --group fail-closed-claim -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-host-receipt.sh --group fail-closed-claim`
- Blocked-by: T-3
- Intent: 只跑 `devflow-exec start`、沒有該站收據時，`verify_receipt:true` 必紅；任何「已武裝／可寫碼」宣稱必須能指出核對過的收據路徑；提到主機限制的文案同時出現「無 PreToolUse」（或「沒有 PreToolUse」）與 `--action`
- Boundaries: 牙停在收據核對與「不得宣稱武裝」，不准在 Cursor Write 上發明編輯器 hook（Known limit ①）。Claude 既有 PreToolUse 擋寫規則不變。禁止假掛 `hooks` 進 `.cursor-plugin/plugin.json`。#host／PLUGIN／setup 只加鑄／核對副作用說明，不改「不准改鬆 --action」禁令。Actor=開工 agent 與 owner；Human decision=核對紅就否決「已武裝」；Observation=核對前 exit ≠ 0，鑄檔並核對後 exit 0。

## T-5 讓 dev-setup 寫出專案級 I2 0-inventory.json
- [ ] 未完成
- Covers: R-3 / S-3.1, S-3.2, S-3.3, S-3.4, S-3.5; R-5 / S-5.1
- Files: skills/dev-setup/SKILL.md, scripts/write-stack-inventory.py, scripts/test-stack-inventory.sh, scripts/check-dev-setup-discipline.sh, scripts/fixtures/stack-inventory/
- Verify: `n=$(bash scripts/test-stack-inventory.sh --group i2 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 6 && bash scripts/test-stack-inventory.sh --group i2`
- Blocked-by: T-4
- Intent: `dev-setup` 的 install／upgrade／check 寫出 `docs/dev/0-inventory.json`（`devflow-stack-inventory/v1`），含專案級 pin、第一層 `direct_deps` 與進 Stage 4 之前就在的 gaps；方法包與產品同一鍵集合
- Boundaries: 深度=專案級宣告 pin + pin／requirements 第一層 `direct_deps`，不是 per-slug「這次 feat 碰到的檔」，不是 lock 全樹／transitive。`dev-setup` 擁有盤點欄位正本，不得讀 I4 digest 回填版本，不得改 Stage 1–4 模板。母版樣張必須看得到 `markdown-it-py==4.0.0` 與 Python 3.9 vs 3.12+ 落差列。指引必須有一句「依賴變了要重跑」。缺 I2 則 check 不得當 current／成功。Actor=owner／採用者／開工 agent；Authority=`dev-setup` 寫檔；Recovery=缺檔=setup 未完成，重跑 check。

## T-6 在人要求且 I2 已在時寫出選配 I4 0-stack.md
- [ ] 未完成
- Covers: R-4 / S-4.1, S-4.2, S-4.3
- Files: scripts/write-stack-inventory.py, skills/dev-setup/SKILL.md, scripts/test-stack-inventory.sh, scripts/fixtures/stack-inventory/
- Verify: `n=$(bash scripts/test-stack-inventory.sh --group i4 -v 2>&1 | grep -c '^=== CASE'); test "$n" -ge 3 && bash scripts/test-stack-inventory.sh --group i4`
- Blocked-by: T-5
- Intent: 預設 setup 只寫 I2、不建 `docs/dev/0-stack.md`；人明確要求時才投影 I2 版本列（可選 digest），且 digest 不是 lock 正本
- Boundaries: I4 只有專案級 `docs/dev/0-stack.md`，不得每 slug 一份。無 I2 不得先寫 I4。必須有一句「盤點正本是 `docs/dev/0-inventory.json`」與一句「digest 不是 lock 正本」。套件版本爭議以 lock／pin 為準。I4 失敗不影響 I2。禁止另造 lockfile 當正本。Actor=採用者決定加不加；Authority=人要求才寫。

## T-7 釘 Non-Goal 回歸並同步新腳本地板
- [ ] 未完成
- Covers: R-6 / S-6.1, S-6.2, S-6.3
- Files: scripts/test-host-adapter.sh, scripts/devflow-check.sh, scripts/check-file-map.sh, scripts/test-architecture-guards.sh, guides/guide-dev-flow.html
- Verify: `n=$(bash scripts/test-host-adapter.sh 2>&1 | grep -c '✓'); test "$n" -ge 57 && test ! -e scripts/check-host-receipt.sh && bash scripts/test-host-adapter.sh`
- Blocked-by: T-6
- Intent: 本 feat 結束後薄殼仍無 `hooks` 鍵、七站仍接 `--action`、契約仍 `2.0.0`、diff 不含模板解凍／STATUS 表列／cache 對齊；新測試腳本已掛進 file-map 與 `devflow-check`
- Boundaries: 本 T 只補負向回歸與地板同步，不發明新執法家族。新增／刪除必列檔時，`EXPECTED_MAPPED_FILES` 與 `test-architecture-guards.sh` 靜態釘、guide `#filemap` 列、若加 selftest 案例則 `MIN_CASES`，必須同一 commit 一起改。禁止改 `.claude-plugin/plugin.json` 的 version 來順便升版。禁止把 `hooks/hooks.json` 抄進 Cursor 薄殼。S-6.3 用 `git diff --name-only` 對本 branch 對帳。

## Split Decisions

| 決策 | 理由 | 依據 | 棄項 |
|---|---|---|---|
| `execution.mode: sequential`，Blocked-by 成 T-1→…→T-7 單鏈 | 收據鑄→核→宣稱、I2→I4、最後地板，前置未達安全狀態後 T 不該開工。I2 理論上可與收據軌道平行，但本 hop brief 要求除非明顯平行否則維持順序 | 4-spec Design Boundary「allow 與鑄檔同一次成功」；使用者 Stage 5 brief | 兩軌 parallel（T-5 `Blocked-by: —`，T-7 等 T-4+T-6）。語意獨立但會讓 verify／I2 同時改 `dev-setup` 與 guide，review 較吵 |
| T-1 含 S-1.3（probe／start／write-cursor／write-scope 不鑄） | 最薄縱切必須同時回答「誰鑄」與「誰不准鑄」，否則 T-1 只剩函式層 | 4-spec S-1.3；模板 tracer-bullet | 把 S-1.3 留到 T-7。棄：那會把鑄檔負向邊界從第一刀拆走 |
| T-2 列出六支腳本 + 測試（>5 檔）不拆 | 可觀測行為是「其餘六站同一套 mint」，Verify 只有一套 `mint-rest`。按腳本拆 T 會變成水平切層 | 4-spec S-1.1 七支清單；模板「不得優先按架構層拆」 | 拆成 talk+2+3 與 5+6+7 兩 T。棄：同一 Verify、同一 Intent |
| T-3 接在 T-2 後，不在 T-1 做 verify | brief 指定先鑄一站、再鋪六站、再加厚核對。T-2 把共用鉤子接到七站後，T-3 只加厚 verify 分支，S-2.* 用 stage4 當代表站 | 4-spec S-2.1 用 stage4；使用者 suggested waves | T-1 就做 stage4 mint+verify。棄：與指定波次不符，且 T-2 接鉤子時 verify 契約還沒釘 |
| T-5 承接 S-5.1 | schema 同一把鑰匙的可觀測結果就是兩份 I2 鍵集合相等，應跟 I2 writer 同一刀 | 4-spec S-5.1／SC-6 | 另開 T 只比鍵。棄：沒有獨立可觀測行為 |
| T-7 才動 file-map／architecture-guards／devflow-check 地板 | 新 `scripts/*.sh`／`*.py` 的 EXPECTED_* 必須跟案例一起改；收到最後一刀避免 T-1／T-5 各改一次地板互相踩 | `scripts/check-file-map.sh` 與 `test-architecture-guards.sh` 互釘註解 | 每個加檔 T 自己改地板。棄：sequential 下會連續改同一常數三次 |
| Verify 開工前實跑（2026-09-09，尚未寫測試腳本） | T-1..T-6：`scripts/test-host-receipt.sh`／`test-stack-inventory.sh` 不存在 → 非零（③綠不了但方向對）。T-7：現況 `test-host-adapter.sh` 約 54 個 `✓`，`-ge 57` 紅（①避免已綠無鑑別力；T-7 要加 ≥3 案並同步 `MIN_CASES`） | 模板 Verify 三律；`scripts/test-host-adapter.sh` `MIN_CASES = 54` | 用已綠的 `check-host-adapter.sh` 當 T-7 唯一牙。棄：無鑑別力 |
