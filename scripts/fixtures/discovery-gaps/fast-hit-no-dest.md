---
feature: discovery-gaps-fast-hit
stage: 4-spec
status: draft
---

# 4. 規格 — S-9.3 命中卻無去向

## Fast early risk triage

| 問 | 答 |
|---|---|
| 改變下一步？ | 否。只改一個狀態字 |
| 改權限／核准語意？ | 否。權限不變 |
| 改等待／完成語意？ | 是。等待被顯示成完成 |
| 改角色交接？ | 否。角色不變 |
| 改系統外動作？ | 否。無新系統外動作 |
| 改中斷恢復？ | 否。恢復不變 |
| 去向 | 待裁 |

## Verification Profile

- lane: fast
- Risk: normal

## ADDED Requirements

#### S-1 hit-no-dest

- GIVEN 第 3 問是且去向待裁 WHEN 跑 spec-gate THEN exit 1
- 觀測:從本檔 C8 看 | 命中無去向必紅 | 用本 fixture 測
