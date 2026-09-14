#!/bin/bash
# test-five-station-f2.sh — F2 dual-path battery (single entry).
#
# Official 18 CASE names only. Hollow probes:
#   --only new5|old7|f1  → exit 3 (even if that path is green)
# Unknown flag / usage   → exit 2 (must not be mistaken for hollow)
#
# Usage: scripts/test-five-station-f2.sh [--case NAME]... [--group NAME]
#        [--hop I|D|Sp|Bu|Sp5b] [--only new5|old7|f1] [-v|--verbose] [--help]
# exit: 0 = NEW5+OLD7 both green / 1 = a CASE missed polarity / 2 = usage
#       3 = hollow --only probe
set -uo pipefail
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
exec python3 "$SELF_DIR/five_station_f2.py" --root "$ROOT" "$@"
