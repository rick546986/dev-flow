---
feature: dogfood-ping
stage: 6-implementation
status: draft
owner: rick-dev-flow
updated: 2026-09-10
---

# 6. 實作筆記

FORK_INTEGRATION_SHA: 0a89ec85ae2cf3ee0c555b82441caa323e77c10f

## 起手

- 圍欄自查:只讀 4-spec／5-tasks／本檔。禁讀 1/2/3。
- branch:`cursor/dogfood-ping-preview`（既有 preview；本輪 Stage 6 接續）
- 0b worktree 隔離:`n-a`（單 checkout）
- 0c 守衛:本 feat 未跑 `devflow-exec.sh start`（Cloud Agent 實作；獨立 reviewer 另審）

## 摘要

T-1 落地 `scripts/dogfood-ping.sh`（stdout=`dogfood-ok\n`、exit 0）。T-2 同步 file-map 計數 193→194 與指南列。正式 Example 樣張留合 main／Stage 7 打包。

## T Review Log

### T-1
- reviewer identity:implementer self-check（獨立 reviewer 另 agent）
- reviewed-at:2026-09-10
- Verify:`test -x scripts/dogfood-ping.sh && head -n1 scripts/dogfood-ping.sh | grep -Fq '/usr/bin/env bash' && scripts/dogfood-ping.sh > /tmp/dogfood-ping.out; test $? -eq 0 && cmp /tmp/dogfood-ping.out <(printf 'dogfood-ok\n')`
- Verify result:exit 0；`/tmp/dogfood-ping.out` 位元組 `64 6f 67 66 6f 6f 64 2d 6f 6b 0a`（`dogfood-ok`+LF）
- Covers finding:R-1／R-2／R-3／S-1／S-2／S-3
- Files finding:只新增 `scripts/dogfood-ping.sh`
- Design boundary finding:shebang=`#!/usr/bin/env bash`；`printf '%s\n' 'dogfood-ok'`；無 HTTP／npm
- verdict:PASS（implementer）；正式 T review 留給獨立 reviewer

### T-2
- reviewer identity:implementer self-check（獨立 reviewer 另 agent）
- reviewed-at:2026-09-10
- Verify:`bash scripts/check-file-map.sh`
- Verify result:exit 0；`scanned=194`；`EXPECTED_MAPPED_FILES=194`；PASS forward/reverse
- Covers finding:R-4／S-4
- Files finding:`scripts/check-file-map.sh`（常數）、`guides/guide-dev-flow.html`（列）、`scripts/test-architecture-guards.sh`（靜態釘）
- Design boundary finding:未改檢查算法；只加列＋計數＋互釘
- verdict:PASS（implementer）；正式 T review 留給獨立 reviewer

## Decisions + Deviations

| ID | 內容 | 依據 |
|---|---|---|
| D-s6-1 | Example `example/dogfood-ping` 本輪不複製；正本留 `docs/dev/dogfood-ping/` + 腳本 | 4-spec／5-tasks 未要求 Stage 6 寫 Example；Decision 落點在合 main |
| D-s6-2 | host-receipt：工具鏈在 hooks／check-devstage6-graph.sh；本環境無既有 `.devflow/`，且 mint 需 5-tasks approved + allow。已把 5-tasks 標 approved 後再鑄 stage6 收據（見下方 Host receipt） | host-stack-fit Stage6 慣例；dogfood 試跑 |

## Host receipt

- 工具存在:`hooks/devflow-lib.py` mint／verify；`scripts/check-devstage6-graph.sh --action`
- 實跑（本機，`.devflow/` gitignore）:
  - mint:`--action` JSON `cursor.node=N1-arm`／`action=write_notes`／`slug=dogfood-ping` → `allow`；寫出 `.devflow/host-receipt/dogfood-ping/stage6.json`（`schema=devflow-host-receipt/v1`，`DONE=true`）
  - verify:`verify_receipt:true` 同站 → exit 0
- 5-tasks 已標 `status: approved`（owner 准開 Stage 6）後才允許 write_notes／鑄檔

## Diff

### dogfood-ping.sh（新建） · `scripts/dogfood-ping.sh` 1-5  T-1
改什麼：新增極小 CLI，stdout 恰好 dogfood-ok+LF，exit 0。
關聯：5-tasks T-1／4-spec R-1..R-3
```diff
+#!/usr/bin/env bash
+# dogfood-ping — minimal observable CLI (Stage 6).
+printf '%s\n' 'dogfood-ok'
+exit 0
```

### EXPECTED_MAPPED_FILES · `scripts/check-file-map.sh` 114-114  T-2
改什麼：地板計數 193→194，納入新腳本。
關聯：5-tasks T-2／R-4
```diff
-EXPECTED_MAPPED_FILES = 193
+EXPECTED_MAPPED_FILES = 194
```

### filemap 列 · `guides/guide-dev-flow.html`（check-file-map 後）  T-2
改什麼：檔案地圖加 `dogfood-ping.sh` 一列（職責：極小可觀測 CLI）。
關聯：check-file-map forward 命中

### 靜態釘 · `scripts/test-architecture-guards.sh`  T-2
改什麼：`EXPECTED_MAPPED_FILES = 194` 互釘字串同步。
關聯：architecture guards 靜態釘
```diff
-check_static_pin "scripts/check-file-map.sh" "EXPECTED_MAPPED_FILES = 193" "..."
+check_static_pin "scripts/check-file-map.sh" "EXPECTED_MAPPED_FILES = 194" "EXPECTED_MAPPED_FILES 釘死 194(精確值;dogfood-ping.sh +1)"
```
