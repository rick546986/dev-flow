---
feature: fixture-horizontal
stage: 5-tasks
status: draft
---

# 5. 任務(fixture:刻意水平切層,期望 heuristic 出 WARNING)

## T-1 Database schema
- [ ] 完成
- Covers: R-1 / S-1
- Files: `migrations/0001_init.sql`
- Verify: `make migrate`
- Blocked-by: —
- Intent: 建立資料表結構
- Boundaries: —

## T-2 Repository 層
- [ ] 完成
- Covers: R-1 / S-1
- Files: `internal/repo/thing.go`
- Verify: `go test ./internal/repo/...`
- Blocked-by: T-1
- Intent: 實作資料存取
- Boundaries: —

## T-3 Service 層
- [ ] 完成
- Covers: R-1 / S-1
- Files: `internal/service/thing.go`
- Verify: `go test ./internal/service/...`
- Blocked-by: T-2
- Intent: 建立商業邏輯層
- Boundaries: —

## T-4 API
- [ ] 完成
- Covers: R-1 / S-1
- Files: `internal/handler/thing.go`
- Verify: `go test ./internal/handler/...`
- Blocked-by: T-3
- Intent: 實作 handler
- Boundaries: —

## T-5 UI
- [ ] 完成
- Covers: R-1 / S-1
- Files: `src/pages/Thing.tsx`
- Verify: `npm test`
- Blocked-by: T-4
- Intent: 前端頁面
- Boundaries: —
