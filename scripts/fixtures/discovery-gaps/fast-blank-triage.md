---
feature: discovery-gaps-fast-blank
stage: 4-spec
status: draft
---

# 4. 規格 — S-9.1 Fast 六問空白

## Verification Profile

- lane: fast
- Risk: normal

## ADDED Requirements

#### S-1 blank-triage

- GIVEN lane fast 無六問表 WHEN 跑 spec-gate THEN exit 1
- 觀測:從本檔 C8 看 | 空白表必紅 | 用本 fixture 測
