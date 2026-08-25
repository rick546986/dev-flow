# 2. 收斂 — 圖對文字樣張

## Approaches Considered
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| A 登入即時查 | dashboard 即時查 | 零 infra | 無推播 | 0.5 週 | `[Assumption]` |
| B nightly cron + 通知表 | 排程寫通知表 | 可擴充 | 新進程 | 1.5 週 | `[Assumption]` |
| C MQ 事件驅動 | 事件驅動 | 即時 | 新 infra | 3 週 | `[Assumption]` |

## 方案架構圖
```
[A] 登入即時查(選定)
  業務登入 -> Dashboard -> GET /contracts/expiring

[B] nightly cron + 通知表
  cron -> notifications 表

[C] MQ 事件驅動
  異動 -> MQ
```

## Decision
採 A(登入即時查),API 預留 B 的擴充。

## Rejected Alternatives
- B:本期不做 email。
- C:違反不引入新 infra。
