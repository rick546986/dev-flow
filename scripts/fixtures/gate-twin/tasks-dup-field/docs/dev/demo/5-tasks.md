---
feature: demo
stage: 5-tasks
status: draft
---

# 5. 任務

## T-1 建 schema(Boundaries 續行藏了第二個 Files,H-1 回歸)
- [ ] 完成
- Covers: R-1 / S-1
- Files: `a.py`
- Verify: `pytest -k a`
- Blocked-by: —
- Intent: 系統多了 schema。
- Boundaries: 主要範圍在 a.py。
  - Files: `b.py`

## T-2 幽靈任務 canary 宿主(fence 內藏 `## T-99`,H-1 回歸)
- [ ] 完成
- Covers: R-1 / S-2
- Files: `c.py`
- Verify: `pytest -k c`
- Blocked-by: T-1
- Intent: 這個 T 本身欄位齊全,只是用來裝下面 fence 裡的幽靈任務 canary。
- Boundaries: 下面程式碼區塊裡的 `## T-99` 是假標題,twin 不該把它解析成卡片。

```text
## T-99 幽靈任務(fence 內,twin 與引擎皆不應解析成卡片/任務)
- Covers: R-9 / S-9
- Files: `ghost.py`
- Verify: `pytest -k ghost`
- Blocked-by: —
- Intent: 幽靈。
- Boundaries: —
```
