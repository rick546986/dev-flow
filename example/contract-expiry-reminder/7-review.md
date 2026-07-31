---
feature: contract-expiry-reminder
stage: 7-review
status: shipped
owner: <reviewer-a>         # reviewer(≠實作 owner <owner>)
updated: 2026-07-23
---

# 7. 驗證

## Coverage Matrix
| S-id | 測試 | 狀態 |
|---|---|---|
| S-1 | `TestExpiring_S1`(Go) | ✅ |
| S-2 | `ExpiringContractsCard "S2 empty"`(vitest) | ✅ |
| S-3 | `ExpiringContractsCard "S3 navigate"`(vitest) | ✅ |
| 既有測試套件(回歸) | `go test ./... && npm test` | ✅ |

## Standards Axis
- F-1 🟡 `internal/handler/contract.go:41` | handler 未設 context timeout,慢查詢會掛住
  dashboard | 建議:`context.WithTimeout(ctx, 2s)`,下個 fast-lane 補。

## Spec Axis
- R-1 符合(S-1/S-2 綠;空狀態文案同 spec)。
- R-2 符合(S-3 綠)。
- D-1 已如實記錄,判定正確(不動 R/S,屬 L1;避開了 migration)。

## Verdict
**PASS**(F-1 為 🟡,開 fast-lane follow-up,不擋出貨)

## Exit Checklist
- [x] Quiz(不可逆改動必做;其餘 full lane 選配,fast 免):本次新增對外 API endpoint `GET /contracts/expiring`,shipped 後即成對外契約,移除屬破壞性變更 → 不可逆,Quiz 必做 —— AI 出 4 題(30 天定義來源/為何不做 email/D-1 為何不加索引/空狀態行為),`<reviewer-a>` 全對
- [x] PR #142 → develop
- [x] 4-spec delta 已併入 `docs/specs/contracts.md`(R-1、R-2 貼入,標 source)
- [x] STATUS.md 已更新為 shipped
- [x] 本資料夾各檔 frontmatter status: shipped/approved
- [x] 7-review.html 已產生(含變更架構圖 + diff 折疊)
- [x] feature branch 已刪
