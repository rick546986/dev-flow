---
feature: discovery-gaps-fast-hit-no-dest
stage: 4-spec
status: draft
---

# 4. 規格

## Fast early risk triage
| # | 問 | 答 |
|---|---|---|
| 1 | 改變下一步？ | 否。清單順序不變 |
| 2 | 改權限／核准語意？ | 否。權限沒動 |
| 3 | 改等待／完成語意？ | 是。等待被顯示成完成 |
| 4 | 改角色交接？ | 否。角色沒動 |
| 5 | 改系統外動作？ | 否。沒有新的系統外步驟 |
| 6 | 改中斷恢復？ | 否。恢復路徑沒動 |
| 去向 |  | 待裁 |

## Verification Profile
- lane: fast
- Risk: normal

#### S-fix.1 hit without destination
- GIVEN 第 3 問為是且去向待裁
- WHEN 跑 check-spec-gate
- THEN 該項紅
- 觀測: exit 1 且輸出含 去向 或 full 或 mini 或 OC

## ADDED Requirements
