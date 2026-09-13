---
feature: discovery-gaps-assumption-expired
stage: 4-spec
status: draft
---

# 4. 規格 — S-4.1 過期 open Assumption

## Verification Profile

- lane: full
- Risk: normal

#### S-1 expired-open

- GIVEN refs 一列 deadline 已過且 status=open WHEN 跑 spec-gate THEN exit 1
- 觀測:從本檔 C7 看 | 過期 open 必紅 | 用 2020-01-01 open 列測

## Real-world Disposition

| 引用（Stage 1 原文片段） | 去向 | 下落 |
|---|---|---|
| 採用現場仍把解法寫進 Goal | 本方案處理 | S-1 |

## Assumption refs

| 引用（原文片段） | deadline | status |
|---|---|---|
| 採用現場仍把解法寫進 Goal | 2020-01-01 | open |
