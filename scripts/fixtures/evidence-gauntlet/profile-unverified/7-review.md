# fixture:Required 層 Race/stress 標 unverified;漏帶 --require-layer 時舊實作 fail-open

## Coverage Matrix
| S-id | 測試 | 狀態 |
|---|---|---|
| S-1 | `test_s_1` | ✅ |

## Verification Evidence
- Source SHA: abc1234def5678
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `pytest -q`
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | pass | 17 passed, 0 failed | |
| Real execution | `curl -s :8080/x` | pass | HTTP 200, 3 rows | |
| Race/stress | | unverified | | 無成熟 race 工具,已記待辦 |
| Supply chain | | unverified | | dependency set 有變,但本輪沒跑 |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 不得破壞既有 API 簽名 | 既有整合測試(回歸列) | pass |

## Standards Axis
- F-1 🟢 無

## Spec Axis
- R-1 符合

## Operational Walkthrough
- reviewer 親跑 `curl -s :8080/x` → HTTP 200

## 現象證據(逐 S)
| S-id | 觀測方式 | 實跑證據 | 相符? |
|---|---|---|---|
| S-1 | curl /x | HTTP 200 | ✅ |
