# fixture:fail 列 Result 含多餘 `|`,整列欄數 ≠5 —— 不得靜默丟列(fail-closed)

## Verification Evidence
- Source SHA: abc1234def5678
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `bash scripts/devflow-evidence-gauntlet.sh target.md`
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | pass | 17 passed, 0 failed | |
| Types/compile | `mypy src` | fail | 2 failed | see log | |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 無 | — | n-a |
