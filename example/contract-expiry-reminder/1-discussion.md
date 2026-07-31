---
feature: contract-expiry-reminder
stage: 1-discussion
status: approved
owner: <owner>
reviewers: [<reviewer-a>]
updated: 2026-07-23
---

# 1. 討論 — 合約到期提醒

## Problem
業務靠記憶與 Excel 追合約到期,平均每季漏 2-3 件續約,客戶流失後才發現。

## Context(已知事實)
- `docs/specs/contracts.md`:合約 CRUD 已有,`contracts.end_date` 欄位存效期,無任何通知機制。
- 後端 Go/Echo/ent,無 scheduler、無 MQ(引入 = 新 infra)。
- 現有 dashboard 頁面有空白卡片區(前端 `src/pages/Dashboard.tsx`)。
- 量級:活躍合約約 8,000 筆。

## Goals
- 業務登入後,不用翻任何清單就能看到「30 天內到期」的合約。
- 點擊可直達該合約詳情。

## Non-Goals(初稿)
- email / LINE 通知(之後再議)。
- 自訂提醒天數。

## Open Questions
- [x] Q1:提前幾天算「即將到期」?→ 30 天(業務主管拍板,寫入 CONTEXT.md「Expiring」)
- [x] Q2:誰要看到?→ 只有該合約負責業務 + 主管
- [x] Q3:站內顯示還是 email?→ 本期只做站內 dashboard

## Constraints
- 不引入新 infra(無 MQ / 無獨立 scheduler service)。
- 兩週內要上(下一版 release)。

## 驗收雛形
- AC-1(Goal 1):任一負責業務登入 dashboard,名下 30 天內到期且未續約的合約 100% 出現在卡片。
  - 從哪看:以 `<owner>` 登入後的 dashboard 到期卡片。
  - 看到什麼算對:卡片列出合約 C,顯示合約名稱與剩餘天數「10 天」。
  - 拿什麼資料試:`<owner>` 名下合約 C,`end_date = today + 10d`,未續約。
- AC-2(Goal 1):無到期合約時顯示空狀態「近期無到期合約」,不報錯。
  - 從哪看:以 `<owner>` 登入後的 dashboard 到期卡片。
  - 看到什麼算對:顯示「近期無到期合約」且畫面沒有錯誤。
  - 拿什麼資料試:`<owner>` 名下沒有 30 天內到期且未續約的合約。
- AC-3(Goal 2):點擊卡片任一列,導向該合約詳情頁。
  - 從哪看:dashboard 到期卡片中的合約 C 那一列與瀏覽器 URL。
  - 看到什麼算對:點擊 C 後 URL 為 `/contracts/C.id` 並顯示該合約詳情頁。
  - 拿什麼資料試:沿用 AC-1 的合約 C,使其先出現在到期卡片。

## 邏輯圖(ASCII)
```
登入 → dashboard 載入 → 查 expiring(end_date - today ≤ 30 且未續約)
                          ├─ 有 → 卡片列出(名稱 + 剩餘天數)→ 點擊 → 詳情頁
                          └─ 無 → 空狀態「近期無到期合約」
```

## Interview Log(三段結論)
- explore:現況無任何通知/排程機制;dashboard 是最低成本的呈現面。
- grill-with-docs:逼出「Expiring」精確定義(30 天 + 未續約),新增 CONTEXT.md 詞條 Expiring、Renewal。
- brainstorming:方向收斂為「登入時即時查詢」優先,cron 留作後手 → 進 2-decision 比較。
