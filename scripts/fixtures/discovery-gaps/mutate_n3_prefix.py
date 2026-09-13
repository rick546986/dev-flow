#!/usr/bin/env python3
"""DG-1/DG-2: delete one N3 prefix in an isolated seed. Not a <<'PY' heredoc."""
import pathlib
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: mutate_n3_prefix.py <seed-root> <prefix>")
root = pathlib.Path(sys.argv[1])
needle = sys.argv[2]
path = root / "skills/dev-talk/nodes/N3-probe.md"
text = path.read_text(encoding="utf-8")
rewritten = text.replace(needle, "", 1)
if rewritten == text:
    raise SystemExit(f"DG mutation 沒生效:{needle}")
path.write_text(rewritten, encoding="utf-8")
