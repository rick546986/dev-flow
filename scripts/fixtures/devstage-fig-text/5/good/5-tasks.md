# 5. 任務 — 圖對文字樣張

## T-1 API:GET /contracts/expiring
- [x] 完成
- Covers: R-1
- Files: `internal/handler/contract.go`
- Verify: `go test`
- Blocked-by: —

## T-2 前端:dashboard 到期卡片
- [x] 完成
- Covers: R-1
- Files: `src/pages/Dashboard.tsx`
- Verify: `npm test`
- Blocked-by: T-1

## T-3 卡片列點擊
- [x] 完成
- Covers: R-2
- Files: `src/components/ExpiringContractsCard.tsx`
- Verify: `npm test`
- Blocked-by: T-2

## T 依賴 DAG(Blocked-by,機械導出)
```
T-1 --> T-2 --> T-3
```
