---
feature: stage7-subsidy-shape
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: fixture
updated: 2026-08-28
---

# 7. 驗證 — 補助沒有截圖槽標題的寫法

## 現象證據

### 進場
![附表六列表](shots/form6-list.png)
從附表六列表打開已生成附表五。不准新增。不准發明編輯 URL。
e2e: e2e/open-existing.spec.ts

![打開已存在](shots/open-existing.png)

### 已生成紀錄
![已生成附表五](shots/form5-ready.png)
e2e: e2e/form5-ready.spec.ts

### 列表核對
![列表核對](shots/list-check.png)
e2e: e2e/list-check.spec.ts

### 詳情
![詳情](shots/detail-view.png)
![欄位](shots/detail-fields.png)
e2e: e2e/detail-view.spec.ts

### 空狀態
![空狀態](shots/empty-state.png)
e2e: e2e/empty-state.spec.ts
