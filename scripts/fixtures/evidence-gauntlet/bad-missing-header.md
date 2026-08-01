# fixture:header 欄位缺漏(無 Final Fresh Run ID、Entry point 空)

## Verification Evidence
- Source SHA: abc1234def5678
- Entry point:
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | pass | 17 passed, 0 failed | |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 無 | — | n-a |
