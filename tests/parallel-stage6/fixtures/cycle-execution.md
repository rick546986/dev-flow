---
feature: cycle-execution-fixture
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-02
execution:
  mode: parallel
---

# 5. 任務(execution DAG cycle fixture)

## T-1 甲
- [ ] 完成
- Covers: R-1 / S-1
- Files: `src/a.ts`
- Verify: `npm test`
- Blocked-by: T-2

## T-2 乙
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/b.ts`
- Verify: `npm test`
- Blocked-by: T-1
