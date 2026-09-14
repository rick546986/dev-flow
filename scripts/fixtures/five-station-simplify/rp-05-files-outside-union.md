---
f1-kind: tcard
f1-union: scripts/five_station_f1.py, scripts/check-five-station-f1.sh
---
## T-ok
- Covers: R-2 / S-2.8
- Files: scripts/five_station_f1.py
- Verify: bash scripts/test-five-station-f1.sh --group brief-files
- Blocked-by: —
## T-over
- Covers: R-2 / S-2.8
- Files: hooks/_stage3_impl.py, graph.yaml
- Verify: echo ok
- Blocked-by: —
