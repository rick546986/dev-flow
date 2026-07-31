---
feature: contract-expiry-reminder
stage: 2-decision
status: approved
owner: <owner>
reviewers: [<reviewer-a>]   # G1 由 <reviewer-a> 核准(≠owner)
updated: 2026-07-23
---

# 2. 收斂 — 到期提醒的實現方式

## Approaches Considered
| 方案 | 摘要 | 優 | 劣 | 成本 |
|---|---|---|---|---|
| A 登入即時查 | dashboard 載入時 API 即時查 expiring 合約 | 零新 infra、實作最小 | 每次載入查一次;無主動推播 | 0.5 週 |
| B nightly cron + 通知表 | 排程掃描寫入 notifications 表 | 可擴充 email;查詢便宜 | 要新增 cron 進程 + 新表 | 1.5 週 |
| C MQ 事件驅動 | 合約異動發事件,消費者判斷到期 | 即時、最可擴充 | 引入 MQ = 新 infra,violates constraint | 3 週+ |

## 方案架構圖
```
[A] 登入即時查(選定)
  業務登入 -> Dashboard 載入 -> GET /contracts/expiring?days=30
    -> service.ListExpiring() [抽象層, 供 B 複用]
      -> repo 查 idx_contracts_end_date [8k 筆, p95 < 50ms]
    -> 卡片渲染 [到期列表 / 空狀態]

[B] nightly cron + 通知表
  cron(nightly) -> scan contracts.end_date
    -> write notifications 表 [新表]
  Dashboard 載入 -> 讀 notifications 表 [可擴充 email]

[C] MQ 事件驅動
  合約異動 -> publish event -> MQ [新 infra, 違反 constraint]
    -> consumer 判斷到期 -> 通知
```

## Decision
採 **A(登入即時查)**,API 設計預留 B 的擴充空間(查詢邏輯抽成 service,未來 cron 可直接複用)。

## Rejected Alternatives
- B:本期不做 email,通知表沒有消費者,先做是浪費。
- C:8,000 筆量級用 MQ 是 overkill,且違反「不引入新 infra」約束。

## Rationale
量級小(8k 筆,索引查詢 <50ms)、需求只到「看得到」,即時查是最短路徑;service 抽象保住升級路。

## Risks & Mitigations
- 查詢慢拖累 dashboard → prototype 前先 EXPLAIN 驗證;超過 100ms 就加覆蓋索引。
- UI 形式不確定(badge? 卡片?)→ 交給 3-prototype 用 variants 挑。

## Success Criteria
- 30 天內到期且未續約的合約,dashboard 100% 可見。
- dashboard 載入增加延遲 < 100ms(p95)。

## Scope & Non-Goals(定稿)
- In:dashboard 卡片、API、詳情連結。
- Out:email/LINE、自訂天數、主管彙總報表。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|
| OC-1 | 已有後繼續約紀錄的合約**不列入**提醒。使用者只被問到「30 天內到期要提醒」,「排除已續約」是 owner 延伸 | 已續約的提醒是雜訊,業務無事可做 | 卡片會多列已續約合約;Success Criteria 第 1 條「未續約」字眼與 4-spec 的過濾條件都要改 | ✅ |
| OC-2 | 只處理 end_date 非空的合約(無期限合約不列)。使用者說「快到期的要看得到」,此為收窄;依據:無 end_date 無從計算「到期」 | 語意上「無期限」不存在到期日,強列需另發明規則 | 要先定義無期限合約的到期語意,Scope 擴大、需回頭問使用者 | ✅ |
| OC-3 | 零筆到期時 dashboard 仍顯示空狀態卡片,不隱藏整卡 | 讓業務能區分「沒有到期」與「功能壞了」 | 前端渲染邏輯改寫,3-prototype 的 variant 題目跟著變 | ✅ |
| OC-4 | 卡片只顯示最靠近到期的 10 筆,其餘收進「查看全部」連結 | 防到期數量多時卡片過長 | 到期 >10 筆時的 UI 行為改變,3-prototype variant 題目跟著變 | **✗** `<reviewer-a>`:截斷會讓業務漏看 → 改為全數顯示+卡片內滾動(裁決後歸使用者裁決,計入確認紀錄;本列保留 = 審計軌跡) |

### 內部技術選擇(下層,告知即可)
- 天數走 query 參數 `days` 預設 30(自訂天數仍 out of scope,參數化只為測試方便)。
- 查詢複用既有 `idx_contracts_end_date`,不另建索引(EXPLAIN 驗證留給 prototype)。

## ADR 晉升檢查
- 難逆轉:否(service 抽象保住退路)
- 反直覺:否
- 真 trade-off:是
→ 晉升:**否**(留在本檔即可)

## 確認紀錄
- 決策點清單確認 | 2026-07-23
- Owner Calls 全裁決(OC-1~3 ✅、OC-4 ✗ 改全數顯示+滾動,`<reviewer-a>`)| 2026-07-23
- prototype 回寫(UI 形式定案為 B dashboard 卡片,見 3-prototype Verdict) | 2026-07-23
