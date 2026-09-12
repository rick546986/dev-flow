# 活教師intended rewrite（PROTOTYPE — 只展示形狀，不改正本）

Stage 6 才改下列活路徑。本檔是 T-now 的intended 對照表。
不改 `notes/dispatch-*`、`docs/dev/HISTORY.md`、`docs/dev/stage7-loop/`（OC-2）。

## Stage 7 intended order（tip 模板已是此序；活教師必須教同一序）

```
2c 整合回歸     ← 最後一次准改碼 / 改 HEAD
  → 2d Final Fresh  ← Source SHA = 當下 HEAD
  → 雙軸 + 現象
  → Verdict
  → Exit            ← 只准文件／PR；禁合併、禁改碼
```

舊序（活教師仍在教，必須清掉）:

```
2c Final Fresh / gauntlet
  → Verdict
  → Exit 才合 INTEGRATION_SHA
```

## 對照

| 活路徑 | 現況（舊教師） | intended |
|---|---|---|
| `example/contract-expiry-reminder/7-review.md` | `執行清單 2c 的 Final Fresh Run` | `執行清單 2d 的 Final Fresh Run` |
| `example/contract-expiry-reminder/4-spec.md` | `7-review 執行清單 2c gauntlet` | `7-review 執行清單 2d gauntlet` |
| `manifests/p4-gauntlet-gates.md` | `7-review 執行清單 2c 的文檔化命令` | `7-review 執行清單 2d 的文檔化命令` |
| `scripts/devflow-integration-regression.sh` 檔頭 | `Stage 7 Exit Checklist「(條件式)整合回歸」計算工具` | `Stage 7 執行清單 2c「(條件式)整合回歸」計算工具`（不是 Exit Checklist 程序） |
| `docs/dev/tools/devflow-integration-regression.sh` 檔頭 | 同上（散發副本） | 同上 |
| 同腳本 `ALREADY_SYNCED` GUIDANCE | `本次輸出不算數`（無下一步） | `本次輸出不算數。恢復：重跑 2d Final Fresh 綁當下 HEAD（寫入 Source SHA），或本項 FAIL。不得只寫「證據不算數」就勾過。` |

衍生 fixture（Stage 6 與正本同一 T）: `scripts/fixtures/spec-gate-dd-subsection/bad-dd-unresolved.md` 抄了 4-spec 的 `2c gauntlet` 句，改編號必須同步。
