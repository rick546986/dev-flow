# fixture:非法 status 值(PASSED / skip 不在四值內)

## Verification Evidence
- Source SHA: abc1234def5678
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `bash scripts/devflow-evidence-gauntlet.sh target.md`
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | PASSED | 17 passed | |
| Lint | `ruff check .` | skip | | 趕時間 |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 無 | — | n-a |
