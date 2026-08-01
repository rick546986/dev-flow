# fixture:宣告 Source SHA 僅 1 字元 —— 任意互為前綴即過的漏洞(m1)

## Verification Evidence
- Source SHA: f
- Final Fresh Run ID: 2026-08-02T1200Z-r1
- Entry point: `bash scripts/devflow-evidence-gauntlet.sh target.md`
- Toolchain: requirements-dev.txt

| Layer | Command | Status | Result | Skipped reason |
|---|---|---|---|---|
| Full test suite | `pytest -q` | pass | 17 passed, 0 failed | |

## Negative Constraint Mapping
| Constraint | Test/Layer | Status |
|---|---|---|
| 無 | — | n-a |
