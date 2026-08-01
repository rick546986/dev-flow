---
feature: parallel-basic-fixture
stage: 5-tasks
status: approved
owner: <owner>
updated: 2026-08-02
execution:
  mode: parallel
  max_parallel_tasks: 2
  rebuild_integration_on_rework: true
---

# 5. 任務(parallel 全欄位示範 fixture)

## T-1 建 API handler
- [ ] 完成
- Covers: R-1 / S-1
- Files: `internal/handler/contract.go`
- Verify: `go test ./internal/handler/...`
- Blocked-by: —

## T-2 前端卡片
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/components/Card.tsx`
- Verify: `npm test -- Card`
- Blocked-by: —
- Integrate-after: T-1

## T-3 資料庫 migration
- [ ] 完成
- Covers: R-2 / S-3
- Files: `migrations/0007_expiry.sql`
- Verify: `make migrate-test`
- Blocked-by: —
- Risk: high

## T-4 e2e 縱切
- [ ] 完成
- Covers: R-1, R-2 / S-4
- Files: `e2e/expiry.spec.ts`
- Verify: `npx playwright test e2e/expiry.spec.ts`
- Blocked-by: T-1, T-2

## T-5 文件同步
- [ ] 完成
- Covers: R-3 / S-5
- Files: `docs/specs/expiry.md`
- Verify: `bash scripts/check-docs.sh`
- Blocked-by: —
- Risk: normal
- Review-mode: dedicated
- Semantic-conflicts-with: T-2
