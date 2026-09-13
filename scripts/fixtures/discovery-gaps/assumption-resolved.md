---
feature: discovery-gaps-assumption-resolved
stage: 4-spec
status: draft
---

# 4. 規格

## Verification Profile
- lane: fast
- Risk: normal

#### S-fix.1 resolved Assumption
- GIVEN refs 表該列 status=resolved
- WHEN 跑 check-spec-gate
- THEN 不得只因該列而紅
- 觀測: Assumption 項綠

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| 採用現場仍把解法寫進 Goal | 2020-01-01 | resolved |
