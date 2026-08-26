---
stage: 2-decision
status: draft
---

# 2. 收斂 — 抽不到唯一解

## Approaches Considered

### 決策點 1 要不要做提醒
| 方案 | 摘要 | 優 | 劣 |
|---|---|---|---|
| A 做 | 做提醒 | 看得到 | 多一條路 |
| 10A 越界 | 編號 10 不是決策點 1 | 會被 startswith 誤吃 | 刀必須失敗 |

## Decision
選 1A。

## Rejected
- 1B：不做。

## Owner Calls
- OC-1：只處理有期限的。✅
