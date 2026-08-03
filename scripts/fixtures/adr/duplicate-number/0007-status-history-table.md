# 7. 狀態歷程獨立成表

- Status: accepted
- Date: 2026-03-11

## Context
狀態變更要可追誰在何時改。

## Decision
獨立 `contract_status_history` 表,不用 audit log 通用表。

## Consequences
查詢多一次 join。
