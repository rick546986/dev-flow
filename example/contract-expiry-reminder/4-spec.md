---
feature: contract-expiry-reminder
stage: 4-spec
status: approved
owner: <owner>
reviewers: [<reviewer-b>]     # G2 由 <reviewer-b> 審(≠owner)
updated: 2026-07-23
---

# 4. 規格 — 合約到期提醒(change spec)

## ADDED Requirements

### R-1: 系統 SHALL 在 dashboard 顯示登入者可見、30 天內到期且未續約的合約卡片
#### S-1
- GIVEN 登入業務 `<owner>` 名下有合約 C,`end_date = today + 10d`,未續約
- WHEN `<owner>` 開啟 dashboard
- THEN 到期卡片列出 C,顯示合約名稱與剩餘天數「10 天」
- 觀測:從 `<owner>` 的 dashboard 到期卡片看 | 看到 C 與「10 天」算對 | 用 C(`end_date = today + 10d`,未續約)測

#### S-2
- GIVEN `<owner>` 名下無 30 天內到期的合約
- WHEN `<owner>` 開啟 dashboard
- THEN 卡片顯示空狀態「近期無到期合約」,不顯示錯誤
- 觀測:從 `<owner>` 的 dashboard 到期卡片看 | 看到「近期無到期合約」且無錯誤算對 | 用名下無 30 天內到期未續約合約的 `<owner>` 測

### R-2: 卡片中每筆合約 SHALL 可點擊導向該合約詳情頁
#### S-3
- GIVEN 到期卡片列出合約 C
- WHEN `<owner>` 點擊 C 那一列
- THEN 導向 `/contracts/C.id` 詳情頁
- 觀測:從 C 那一列與瀏覽器 URL 看 | 點擊後 URL 為 `/contracts/C.id` 且顯示 C 詳情算對 | 用 S-1 的到期合約 C 測

## MODIFIED Requirements
(無 —— 不改既有行為)

## REMOVED Requirements
(無)

## 行為流程圖(R 級)
```
[R-1] dashboard 顯示到期卡片
  登入 -> 開啟 dashboard -> GET /contracts/expiring?days=30
    -> 查詢結果
      = 有到期合約 -> 卡片列出 [名稱 + 剩餘天數]
      = 無到期合約 -> 空狀態 [近期無到期合約]

[R-2] 卡片列可點擊導向詳情
  卡片列出到期合約 C -> 使用者點擊該列 -> 導向 /contracts/C.id
```

## Acceptance Criteria
- S-1 ~ S-3 測試全綠。
- dashboard p95 載入延遲增加 < 100ms(8k 筆量級,EXPLAIN 驗證走索引)。

## Out of Scope
email/LINE 通知、自訂天數、主管彙總報表。

## Diff Budget
≤ 6 檔 / ≤ 400 行(API handler+service+query、前端卡片元件+route、測試)。

## Dependencies
無(不依賴其他 feature;不需 migration)。

## Drafting Decisions(草擬自判,已裁決)
- 剩餘天數顯示「N 天」不含小時 | 理由:業務以天為單位追 | 棄項:精確到時分 | ✅
- S-2 空狀態文案寫死於 spec | 理由:驗收要可測,文案不可漂 | 棄項:留給前端自由 | ✅

## Test Skeletons(選配)
```go
func TestExpiring_S1(t *testing.T) {
	// GIVEN 登入業務 <owner> 名下合約 C, end_date = today+10d, 未續約
	// WHEN <owner> 開啟 dashboard (GET /contracts/expiring?days=30)
	// THEN 到期卡片列出 C, 顯示名稱與剩餘天數「10 天」
	t.Skip("skeleton - see 4-spec S-1; S-2/S-3 由前端 vitest 承接,見 6-implementation-notes")
}
```

## 確認紀錄
- R 範圍確認 | 2026-07-23
- S 逐段確認完成 | 2026-07-23
