---
feature: discovery-gaps-fast-visual
stage: 4-spec
status: draft
---

# 4. 規格

## Fast early risk triage
| # | 問 | 答 |
|---|---|---|
| 1 | 改變下一步？ | 否。只改 CSS 色 |
| 2 | 改權限／核准語意？ | 否。只改 CSS 色 |
| 3 | 改等待／完成語意？ | 否。只改 CSS 色 |
| 4 | 改角色交接？ | 否。只改 CSS 色 |
| 5 | 改系統外動作？ | 否。只改 CSS 色 |
| 6 | 改中斷恢復？ | 否。只改 CSS 色 |
| 去向 | Fast | 已有 approved spec,不改語意 |

## Verification Profile
- lane: fast
- Risk: normal

#### S-fix.1 visual all no
- GIVEN 六問皆否且去向 Fast
- WHEN 跑 check-spec-gate
- THEN 不得只因全否加 Fast 而紅
- 觀測: Fast 項綠

## Assumption refs
| 引用（原文片段） | deadline | status |
|---|---|---|
| 色票對比 | 2020-01-01 | resolved |

## ADDED Requirements
