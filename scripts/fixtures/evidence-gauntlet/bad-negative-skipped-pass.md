# fixture:negative constraint 標 skipped 卻寫 pass

## Verification Evidence
- Source SHA: abc1234def5678
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `bash scripts/devflow-evidence-gauntlet.sh target.md`
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | pass | 17 passed, 0 failed | |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 不得破壞既有 API 簽名 | skipped: 時間不夠 | pass |
