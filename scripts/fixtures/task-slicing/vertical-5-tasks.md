---
feature: fixture-vertical
stage: 5-tasks
status: draft
---

# 5. 任務(fixture:合法垂直切片,期望不警告)

## T-1 打通「查詢到期合約」端到端最薄一刀
- [ ] 完成
- Covers: R-1 / S-1
- Files: `internal/handler/contract.go`, `internal/repo/contract.go`, `src/components/Card.tsx`
- Verify: `go test ./internal/... -run TestExpiring && npm test -- Card`
- Blocked-by: —
- Intent: 系統多了到期查詢:登入者在 dashboard 看到名下 30 天內到期的合約與剩餘天數。
- Boundaries: 複用既有索引,不另建。

## T-2 加上空狀態呈現
- [ ] 完成
- Covers: R-1 / S-2
- Files: `src/components/Card.tsx`
- Verify: `npm test -- Card`
- Blocked-by: T-1
- Intent: 名下無到期合約時,使用者看到「近期無到期合約」而不是空白或錯誤。
- Boundaries: 文案照 spec 寫死。

## T-3 卡片列可點擊導向詳情
- [ ] 完成
- Covers: R-2 / S-3
- Files: `src/components/Card.tsx`
- Verify: `npm test -- Card`
- Blocked-by: T-2
- Intent: 使用者點卡片列後畫面導向該合約詳情頁。
- Boundaries: 不動 Dashboard 版面。
