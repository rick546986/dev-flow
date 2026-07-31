---
feature: contract-expiry-reminder
stage: 3-prototype
status: approved
owner: <owner>
updated: 2026-07-23
---

# 3. 原型 — 提醒的 UI 形式:badge 還是卡片?

## Question
2-decision Risks 第 2 條:業務接受哪種呈現?sidebar badge(低調)vs dashboard 卡片(顯眼)。

## Method
- branch:`proto/expiry-ui-variants`(throwaway,不進 main)
- UI 2 variants,superpowers visual companion 互動挑:
  - Variant A:sidebar「合約」項加紅色數字 badge,點開 drawer 列表
  - Variant B:dashboard 頂部卡片,直接列出到期合約(剩餘天數倒數)

## 結構圖
```
Variant A: sidebar badge
  Sidebar[合約 項目 + 紅色數字 badge] -> click -> Drawer[到期合約清單]

Variant B: dashboard 卡片(選定, 3/3 票)
  Dashboard 頂部 -> ExpiringContractsCard[
    合約名稱 | 剩餘天數
  ] -> click 列 -> /contracts/:id
```

## Result
業務主管 + 2 位業務實測選 **B**(companion events:B 被選 3/3)。
理由:badge 要多點一層才看得到,「登入第一眼」是需求本體。

## Verdict
- 回寫 2-decision Risks:UI 形式已定 → dashboard 卡片。
- branch `proto/expiry-ui-variants` 已刪;Variant B 結構截圖存 `3-prototype.html`。
