# fixture:合法 Verification Evidence(四值俱全、全規則過)

## Verification Evidence
- Source SHA: abc1234def5678
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `bash scripts/devflow-evidence-gauntlet.sh docs/dev/<slug>/7-review.md`
- Toolchain: requirements-dev.txt(pinned;python3)

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `go test ./... && npm test` | pass | 47 passed, 0 failed | |
| Types/compile | `tsc --noEmit` | pass | 0 errors in 12 files | |
| Changed-line coverage | `pytest --cov --cov-branch` | pass | 31/31 changed lines, 10/10 branches | |
| Mutation | `python tools/mutants.py` | pass | 8/8 killed | |
| Property-based | `pytest tests/test_props.py` | pass | 2 properties, 100 examples each | |
| Real execution | `curl -s :8080/contracts/expiring` | pass | HTTP 200, 3 rows, 10 天欄位正確 | |
| Supply chain | `pip-audit -r requirements-dev.txt` | pass | 0 known vulns; new deps: 0 | |
| Race/stress | | unverified | | 無成熟 race 工具,已記 manifest 待辦 |
| Rollback rehearsal | | n-a | | 本次無 migration,不適用 |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 測試不得依賴真實 sleep/wall-clock | `grep -rn "time.sleep" tests/` → 0 hits | pass |
| 不得新增未授權 network capability | capability diff(人工核對 diff) | unverified |
