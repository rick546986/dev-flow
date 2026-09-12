---
feature: demo
stage: 4-spec
status: draft
---

# 4. 規格

## ADDED Requirements

### R-1: 系統 SHALL 顯示列表

#### S-1
- GIVEN 已登入
- WHEN 開啟列表
- THEN 看到卡片
- 觀測:打 GET /list | 回 200 | 種子

## 行為流程圖(R 級)
```
[Actor] --> [Page R-1]
|-- login with a very long branch label that must not be silently clipped at forty-two chars
|-- open list
|-- click card row
```

## Verification Profile(G2 一併審)
- lane: fast
- Risk: normal
