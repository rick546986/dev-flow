#!/bin/bash
# test-five-station-f3.sh — F3 single-process battery (NEW5+OLD7+TOKEN).
#
# Official 25 CASE names only. Hollow probes:
#   --only new5|old7|token  → exit 3 (even if that path is green)
#   --probe hollow-*        → exit 3
#   --probe polarity        → exit 1
# Unknown flag / usage      → exit 2 (must not be mistaken for hollow)
#
# Usage: scripts/test-five-station-f3.sh [--case NAME]... [--group NAME]
#        [--slot ok|missing|empty|readonly|sibling-reject]
#        [--reader canonical-200|canonical-210]
#        [--missing declared|in-flight|cut]
#        [--only new5|old7|token] [--probe NAME] [-v|--verbose] [--help]
# exit: 0 = NEW5+OLD7+TOKEN all green / 1 = a CASE missed polarity
#       2 = usage / 3 = hollow --only/--probe
set -uo pipefail
SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
exec python3 "$SELF_DIR/five_station_f3.py" --root "$ROOT" "$@"
