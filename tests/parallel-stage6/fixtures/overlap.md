---
feature: overlap-fixture
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-02
execution:
  mode: parallel
  max_parallel_tasks: 3
---

# 5. 任務(Files overlap fixture:同檔 + 目錄前綴兩種)

## T-1 改 a
- [ ] 完成
- Covers: R-1 / S-1
- Files: `src/a.ts`
- Verify: `npm test -- a`
- Blocked-by: —

## T-2 改 a 與 b
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/a.ts`, `src/b.ts`
- Verify: `npm test -- ab`
- Blocked-by: —

## T-3 改 api 目錄
- [ ] 完成
- Covers: R-2 / S-3
- Files: `src/api/`
- Verify: `npm test -- api`
- Blocked-by: —

## T-4 改 api 內單檔
- [ ] 完成
- Covers: R-2 / S-4
- Files: `src/api/x.ts`
- Verify: `npm test -- x`
- Blocked-by: —
