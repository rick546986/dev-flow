---
status: accepted          # proposed | accepted | deprecated | superseded
date: YYYY-MM-DD
source: docs/dev/<feature>/2-decision.md
topics: []                # 非空 kebab-case;知識索引(Pilot-2)按此分組
supersedes: []            # 本決策整份取代的 ADR id,例如 ["0001"]
superseded_by: null       # 被誰整份取代;status=superseded 時必填
---

# NNNN. <決策標題>

> 晉升條件(三條件**全中**才立此檔,否則留在 2-decision 就好):
> 難逆轉 + 反直覺 + 真 trade-off。
>
> Active = `accepted` only。`proposed` 不是現行決策。
> 整份取代時:新 ADR `supersedes` 舊 id,舊 ADR `status: superseded` + `superseded_by` 回指新 id(雙向必齊)。
> 部分取代與知識索引產生器屬後續 Pilot,本模板只把 meta 留好。

## Context
<!-- 1-3 句:當時面對什麼 -->

## Decision
<!-- 選了什麼 -->

## Considered Options
<!-- 從 2-decision 的 Approaches 摘錄 -->

## Consequences
<!-- 好壞都寫:換到了什麼、付出了什麼 -->
