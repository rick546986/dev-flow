# 1. 討論 — 掃頁樣張

## Problem
業務靠記憶追到期,每季漏續約。
現在怎麼繞:Excel 私表 + 電話催。

## Context(已知事實)
- 議約週期約一個月,見 docs/specs/contracts.md:L10-L20

## Real-world Context

### Actors
| Actor | 真實目標 | 權限 | 掌握資訊 | 缺少資訊 | 系統外工具 |
|---|---|---|---|---|---|
| 業務 | 到期不漏 | 讀寫名下 | 合約清單 | [Assumption] 主管不看私表 | Excel |

### Current Journey
| Step | 誰 | 真實動作 | 使用工具 | 等待誰 | 系統留下什麼 | 痛點 |
|---|---|---|---|---|---|---|
| 1 | 業務 | 翻私表 | Excel | — | 無 | 漏續約 |

### Workarounds
Excel 私表 + 電話催。

## Open Questions
- [x] 合約即將到期要提前幾天開始催,若同一客戶同時有多筆即將到期,清單要一次列出還是分開提醒,業務離職後這些列要轉給誰?
- [~] 離職後提醒給誰?
- [>] 一次 200 筆怎麼看?

## 驗收雛形
- 假設名下有 30 天內未續約,當業務打開看板,則該筆在清單
  - 從哪看:看板
  - 看到什麼算對:合約編號出現

## 現況圖
```
行政
建補助案、填申請日
後台
PLUS 還不會自動切
↓
行政
新增附表五、選 A–F
後台
看不到 2PN
↓
行政
口頭對 OPU／FBT
另開單
完整額只能猜
```

## Interview Log
- Q:第1條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第1條推理。
  - 結論:CONFIRMED 第1條。
- Q:第2條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第2條推理。
  - 結論:CONFIRMED 第2條。
- Q:第3條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第3條推理。
  - 結論:CONFIRMED 第3條。
- Q:第4條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第4條推理。
  - 結論:CONFIRMED 第4條。
- Q:第5條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第5條推理。
  - 結論:CONFIRMED 第5條。
- Q:第6條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第6條推理。
  - 結論:CONFIRMED 第6條。
- Q:第7條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第7條推理。
  - 結論:CONFIRMED 第7條。
- Q:第8條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第8條推理。
  - 結論:CONFIRMED 第8條。
- Q:第9條?
  - 事實:docs/specs/contracts.md:L10-L20
  - 推理:第9條推理。
  - 結論:CONFIRMED 第9條。
