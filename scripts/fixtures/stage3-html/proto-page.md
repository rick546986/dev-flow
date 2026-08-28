---
feature: stage3-review-fixture
stage: 3-prototype
status: approved
owner: fixture
updated: 2026-08-28
---

# 3. 原型 — 列表怎麼呈現?

## Stage 3 觸發判定(條件式必要)
- [x] 有新的前端流程(列表新卡)
- [x] 改變使用者下一步(登入第一眼決定跟催哪件)
- [ ] 涉及角色交接
- [ ] 涉及人工核准
- [ ] 涉及等待/退回/逾時
- [x] 涉及權限差異(本人與主管可看範圍不同)
- [ ] 涉及系統外動作
- [x] 涉及多種可行互動設計(badge / 卡片)
- [ ] Stage 1 尚有操作流程不確定性

→ 命中 4 條:Stage 3 條件式必要,執行(不跳過)。

## Question
2-decision Risks 第 1 條:列表用 sidebar badge 還是 dashboard 卡片?

## Method
- branch:`proto/list-ui-variants`(throwaway,不進 main)
- Demo 形式:可點擊 HTML prototype
- Variant A:sidebar 紅色數字 badge
- Variant B:dashboard 頂部卡片(選定)

## 結構圖
- Variant A: sidebar badge
- Variant B: dashboard 卡片(選定)
- 列內標狀態

## Demo Script

### Scenario AC-1(看到提醒)
- 使用者角色:負責業務
- 真實目標:今天決定要跟催哪件
- 起始狀態:fixture 一筆未處理
- 操作步驟:登入 → 看到期卡片
- 系統回應:卡片列出名稱與剩餘天數
- 系統外下一步:無
- 觀察問題:第一眼看得到嗎?

### Scenario AC-2(空狀態)
- 使用者角色:名下無到期件的業務
- 真實目標:確認今天不用跟催
- 起始狀態:fixture 空組
- 操作步驟:登入 → 看卡片
- 系統回應:「近期無到期」,無錯誤
- 系統外下一步:無
- 觀察問題:空狀態會不會被當成壞掉?

## Result
業務選 **B**(卡片)。badge 要多點一層,違背「登入第一眼」。

## User Demo Feedback
- Demo date: 2026-08-28
- Participants: 業務 ×2(test-only human fixture)
- Variant reviewed: A / B
- Accepted interaction: B
- Rejected interaction: A
- Human verdict: ACCEPTED
- Verdict attestation: human:fixture @ 2026-08-28(test-only human fixture)

## Verdict
- 回寫 2-decision Risks 第 1 條:UI 形式已定 → dashboard 卡片。
- branch `proto/list-ui-variants` 已刪。
