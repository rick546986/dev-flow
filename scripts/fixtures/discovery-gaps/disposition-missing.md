---
feature: discovery-gaps-disposition-missing
stage: 4-spec
status: draft
---

# 4. 規格

## Verification Profile
- lane: full
- Risk: normal

#### S-fix.1 missing disposition
- GIVEN full lane 無 Real-world Disposition 表
- WHEN 跑 check-spec-gate
- THEN 該項紅
- 觀測: exit 1 且輸出含 Disposition 或 去向
