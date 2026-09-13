---
feature: fast-hit-no-dest
stage: 4-spec
status: draft
---

# 4. 規格 — 命中卻無去向

## Fast early risk triage

| 問 | 答 |
|---|---|
| 改變下一步？ | 否。狀態字未改流程 |
| 改權限／核准語意？ | 否。權限不變 |
| 改等待／完成語意？ | 是。等待被顯示成完成 |
| 改角色交接？ | 否。角色不變 |
| 改系統外動作？ | 否。無新系統外動作 |
| 改中斷恢復？ | 否。恢復不變 |

去向: 待裁

## ADDED Requirements

### R-1: 系統 SHALL 顯示剩餘天數
#### S-1 顯示剩餘天數
- GIVEN 合約剩餘 14 天
- WHEN 開頁
- THEN 顯示 14 天
- 觀測:從頁面看 | 看到 14 天算過 | 用剩餘 14 天測

## Verification Profile

- lane: fast
- Risk: normal
