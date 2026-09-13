---
feature: discovery-gaps-fast-blank
stage: 4-spec
status: draft
---

# 4. 規格

## Verification Profile
- lane: fast
- Risk: normal

#### S-fix.1 blank Fast triage
- GIVEN lane=fast 且無六問表
- WHEN 跑 check-spec-gate
- THEN 該項紅
- 觀測: exit 1 且輸出含 Fast 或 六問 或 triage

## ADDED Requirements
