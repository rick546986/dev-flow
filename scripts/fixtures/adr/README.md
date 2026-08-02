# ADR 守衛 fixture

刻意**不放在** `docs/adr/`:duplicate-number fixture 若落在真實掃描路徑,
本 repo 的 ADR 檢查會永遠紅。這裡的檔案只被 `scripts/check-adr-integrity.sh`
的 fixture battery 讀,不是本 repo 的真實 ADR。

| 目錄 | 期望 | 為什麼 |
|---|---|---|
| `good/` | PASS | 編號唯一、檔名合規 |
| `duplicate-number/` | FAIL | `0007` 出現兩次 |
| `bad-filename/` | FAIL | 檔名不是 `NNNN-kebab-slug.md` |
