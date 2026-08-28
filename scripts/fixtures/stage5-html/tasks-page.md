---
feature: stage5-review-fixture
stage: 5-tasks
status: draft
owner: fixture
updated: 2026-08-28
---

# 5. 任務 — 審頁卡 fixture

## T-1 查詢入口
- [ ] 未完成
- Covers: S-1
- Files: `src/query.py`, `src/query_test.py`
- Verify: `python3 -m pytest src/query_test.py -q`
- Blocked-by: —
- Intent: 系統多了到期查詢入口,空結果回空列表。
- Boundaries: 只讀既有表,不另建索引。

## T-2 列表卡
- [ ] 未完成
- Covers: S-2
- Files: `src/card.py`, `src/card_test.py`
- Verify: `python3 -m pytest src/card_test.py -q`
- Blocked-by: T-1
- Intent: 列表多了到期卡;零筆顯示空狀態,不隱藏整卡。
- Boundaries: 空狀態文案寫死,不得自創。

## T-3 點進詳情
- [x] 完成
- Covers: S-3
- Files: `src/card.py`
- Verify: `python3 -m pytest src/card_test.py -q`
- Blocked-by: T-2
- Intent: 每列可點進既有詳情頁。
- Boundaries: 照既有詳情路由,不准發明新編輯 URL。
