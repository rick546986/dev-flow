# 7. 驗證 — 圖對文字樣張

## Standards Axis
- F-1 黃燈 handler timeout(不要拿 F-id 對圖)

## 變更架構圖
```
[Dashboard.tsx]
       |
       v
[ExpiringContractsCard.tsx]
       |
       v
[GET /contracts/expiring]
       |
       v
[PATCH /contracts/:id/status]
       |
       v
[renewal_status]
```

## Diff(merge-base(develop)..HEAD,逐檔折疊)

`src/pages/Dashboard.tsx`
`src/components/ExpiringContractsCard.tsx`

GET /contracts/expiring
PATCH /contracts/:id/status
CREATE TABLE renewal_status (id UUID)
