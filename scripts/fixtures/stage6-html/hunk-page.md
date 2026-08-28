---
feature: hunk-page-fixture
stage: 6-implementation
status: draft
owner: fixture
updated: 2026-08-28
---

# 6. 實作筆記

## 摘要

三個函式這輪改完:日期解析、狀態標籤、晶片渲染。空值不再當空字串。

## 改了什麼

日期空值回「—」;狀態標籤與晶片共用同一句,不再各寫一份。

## T-1

日期解析改走單一入口 `parse_submitted_on`。

## T-2

狀態標籤與晶片對齊,空值顯示「—」。

## Diff

### parse_submitted_on · `src/dates.py` 12-20  T-1
改什麼：空字串不再當合法日期,改回 None。
關聯：caller `build_row`／無對語函式
```diff
 def parse_submitted_on(raw):
     if not raw:
-        return ""
+        return None
     return parse_iso(raw)
```

### format_status_label · `src/status.py` 8-18  T-2
改什麼：狀態文案改走單一函式,空值回「—」。
關聯：callee `label_for`／誰叫它 `render_chip`
```diff
 def format_status_label(raw):
     if not raw:
+        return "—"
     return label_for(raw)
```

### render_chip · `src/chip.py` 24-36  T-1 T-2
改什麼：晶片改吃 format_status_label,不再自己拼字。
關聯：peer `format_status_label`／caller `build_row`
```diff
 def render_chip(row):
-    text = row.status or ""
+    text = format_status_label(row.status)
     return Chip(text)
```
