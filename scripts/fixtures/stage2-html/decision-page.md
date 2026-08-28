---
feature: stage2-review-fixture
stage: 2-decision
status: draft
verdict:
owner: fixture
updated: 2026-08-28
---

# 2. 收斂 — 審頁分組卡 fixture

## Approaches Considered

### 決策點：呈現面
#### A 登入即時查
摘要:打開列表時當場查。優:零新排程。劣:每次載入打一次。
#### B 夜間掃描
摘要:夜間寫一張通知表。優:查詢便宜。劣:要新表。

### 決策點：通知面
#### C 只站內
摘要:本期只做站內卡。優:範圍小。劣:沒有站外提醒。
#### D 站外信
摘要:同期加信。優:人不在也看得到。劣:超出本期約束。

## Decision
採 A + C:登入即時查,本期只站內。

## 方案架構圖
- 登入
- 即時查到期
- 站內卡片

## 既有脈絡
現況沒有排程、沒有站外通道。這段是背景,審頁要摺疊。

## Rejected Alternatives
- B:本期沒有通知表的消費者。
- D:本期不做站外信。

## Rationale
最短路徑先讓人看得到;通知表留給之後。

## Risks & Mitigations
- 查詢拖慢列表 → 先量測再加索引。
