# fixture:coverage pass 只給全域百分比,無 changed-lines covered/total

## Verification Evidence
- Source SHA: abc1234def5678
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `bash scripts/devflow-evidence-gauntlet.sh target.md`
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | pass | 17 passed, 0 failed | |
| Changed-line coverage | `pytest --cov` | pass | 全域 92% coverage | |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 無 | — | n-a |
