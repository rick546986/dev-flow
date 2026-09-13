---
feature: discovery-gaps-assumption-expired
stage: 4-spec
status: draft
---

# 4. 規格

## Verification Profile
- lane: fast
- Risk: normal

#### S-fix.1 expired open Assumption
- GIVEN refs 表一列 deadline 為過去日且 status=open
- WHEN 跑 check-spec-gate
- THEN 該項紅
- 觀測: exit 1 且輸出含 Assumption 或 過期 或 open

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| 採用現場仍把解法寫進 Goal | 2020-01-01 | open |
