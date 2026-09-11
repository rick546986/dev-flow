# ADR 守衛 fixture

刻意**不放在** `docs/adr/`:負向 fixture 若落在真實掃描路徑,
本 repo 的 ADR 檢查會永遠紅。這裡的檔案只被 `scripts/check-adr-integrity.sh`
的 fixture battery 讀,不是本 repo 的真實 ADR。

| 目錄 | 期望 | 為什麼 |
|---|---|---|
| `good/` | PASS | 檔名合規、status/topics 合法、雙向取代鏈無環、同 topic 最多一份 accepted |
| `duplicate-number/` | FAIL | `0007` 出現兩次 |
| `bad-filename/` | FAIL | 檔名不是 `NNNN-kebab-slug.md` |
| `bad-status/` | FAIL | `status` 不在 `proposed\|accepted\|deprecated\|superseded` |
| `dangling-supersede/` | FAIL | `supersedes` 指向不存在的 ADR(或缺互惠) |
| `supersede-cycle/` | FAIL | supersedes 邊成環 |
| `multi-active-topic/` | FAIL | 同一 `topic` 有兩份 `accepted` |

Active = `accepted` only。`proposed` / `deprecated` / `superseded` 不佔 active 名額。
