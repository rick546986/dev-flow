---
feature: stage7-review-fixture
stage: 7-review
status: draft
verdict: PRE-REVIEW
owner: fixture
updated: 2026-08-28
---

# 7. 驗證 — 審頁截圖槽 fixture

## 截圖槽

### 進場
- data-shot: list-entry
- src: shots/form6-list.png
- caption: 附表六列表
- 進場:從附表六列表打開已生成附表五。不准新增。不准發明編輯 URL。
- hang-point: e2e/open-existing.spec.ts

### 已生成紀錄
- data-shot: generated-form5
- src: shots/form5-ready.png
- caption: 已生成附表五
- hang-point: e2e/form5-ready.spec.ts
