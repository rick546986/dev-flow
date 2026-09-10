---
feature: dogfood-ping
stage: 5-tasks
status: draft
owner: rick-dev-flow
updated: 2026-09-10
execution:
  mode: sequential
---

# 5. 任務 — dogfood-ping

> 把 4-spec（G2 PASS）切成可勾選實作單。**本站只派工，不寫正式碼**（正式 `scripts/dogfood-ping.sh` 留 Stage 6）。
> 模式：sequential。tracer：T-1 先讓 CLI 可觀測，T-2 再補地板。

## T-1 新增 dogfood-ping CLI（印 dogfood-ok、exit 0）
- [ ] 未完成
- Covers: R-1, R-2, R-3 / S-1, S-2, S-3
- Files: `scripts/dogfood-ping.sh`
- Verify: `test -x scripts/dogfood-ping.sh && head -n1 scripts/dogfood-ping.sh | grep -Fq '/usr/bin/env bash' && scripts/dogfood-ping.sh > /tmp/dogfood-ping.out; test $? -eq 0 && cmp /tmp/dogfood-ping.out <(printf 'dogfood-ok\n')`
- Blocked-by: —
- Intent: 系統多了一支可執行腳本 `scripts/dogfood-ping.sh`：跑起來 stdout 恰好 `dogfood-ok\n`，exit 0。
- Boundaries: 只准新增／編輯 Files 列出的那一支腳本；shebang 必須 `#!/usr/bin/env bash`；輸出用 `printf '%s\n' 'dogfood-ok'`（或位元組等價），不用 echo；不准加 HTTP／npm／第二支腳本；不准動 host-stack-fit／#163／#165。

## T-2 同步 file-map 地板（檢查綠）
- [ ] 未完成
- Covers: R-4 / S-4
- Files: `scripts/check-file-map.sh`, `guides/guide-dev-flow.html`
- Verify: `bash scripts/check-file-map.sh`
- Blocked-by: T-1
- Intent: 新增腳本後 file-map／計數地板綠——`check-file-map.sh` exit 0，不因漏登 `scripts/dogfood-ping.sh` 而紅。
- Boundaries: 只准改 file-map 列與 `EXPECTED_MAPPED_FILES`（或等價計數）讓新腳本入帳；不准改檢查算法／放寬守衛；不准動 host-stack-fit 正本；不准在本 T 改 CLI 行為（行為屬 T-1）。

## T 依賴
```
T-1 --> T-2
```
