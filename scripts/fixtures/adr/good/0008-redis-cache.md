---
status: accepted
date: 2026-04-01
source: fixture
topics: [cache]
supersedes: ["0002"]
superseded_by: null
---

# 0008. 改用 Redis 快取

## Context
多機部署後本機檔案快取不一致。

## Decision
改用 Redis。

## Consequences
多一個外部相依。
