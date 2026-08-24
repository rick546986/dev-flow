#!/bin/bash
# Batch-specific renderer for the active guide excerpts and the two corrected example twins.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
MODE=${1:---check}
case "$MODE" in
  --write|--check) ;;
  *) echo "usage: $0 [--write|--check]" >&2; exit 2 ;;
esac

DEVFLOW_RENDER_PYTHON=${DEVFLOW_RENDER_PYTHON:-python}
"$DEVFLOW_RENDER_PYTHON" - "$ROOT" "$MODE" <<'PY'
import html
import os
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt, __version__ as markdown_it_version

root = Path(sys.argv[1])
mode = sys.argv[2]
required_version = "4.0.0"
if markdown_it_version != required_version:
    raise SystemExit(
        f"markdown-it-py {required_version} required; got {markdown_it_version}. "
        f"Install scripts/requirements-methodology-render.txt in the selected Python environment.")

pin = (root / "scripts" / "requirements-methodology-render.txt").read_text(encoding="utf-8").strip()
if pin != f"markdown-it-py=={required_version}":
    raise SystemExit(f"render dependency pin drifted: {pin!r}")

renderer = MarkdownIt("commonmark", {
    "html": True,
    "linkify": False,
    "typographer": False,
}).enable("table")
renderer.renderer.rules["table_open"] = (
    lambda tokens, idx, options, env: '<div class="tablewrap"><table>\n')
renderer.renderer.rules["table_close"] = (
    lambda tokens, idx, options, env: '</table></div>\n')


def read(rel):
    return (root / rel).read_text(encoding="utf-8")


def quote_region(rel, start, stop=None):
    lines = read(rel).splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(">") and start in line]
    if len(starts) != 1:
        raise SystemExit(f"{rel}: expected one quote anchor {start!r}, found {len(starts)}")
    selected = []
    for line in lines[starts[0]:]:
        if not line.startswith(">"):
            break
        if stop and stop in line:
            break
        selected.append(line)
    while selected and selected[-1].strip() == ">":
        selected.pop()
    return "\n".join(selected) + "\n"


def bullet(rel, anchor):
    lines = read(rel).splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("- ") and anchor in line]
    if len(starts) != 1:
        raise SystemExit(f"{rel}: expected one bullet anchor {anchor!r}, found {len(starts)}")
    selected = [lines[starts[0]]]
    for line in lines[starts[0] + 1:]:
        if line.startswith("- ") or line.startswith("## ") or not line.strip():
            break
        selected.append(line)
    return "\n".join(selected) + "\n"


def fenced_seam():
    matches = re.findall(r"```text\n(RED → GREEN.*?review evidence)\n```", read("README.md"), re.S)
    if len(matches) != 1:
        raise SystemExit(f"README.md: expected one Stage 6 seam, found {len(matches)}")
    return "```text\n" + matches[0] + "\n```\n"


def exit_checklist():
    """抽 `## Exit Checklist` 到下一個 `## ` 之前的**完整**區段。

    舊版用 `((?:- \\[ \\].*\\n)+)` 只吃連續的單行項目,遇到第一個多行項目
    (續行以空白開頭)就停住 —— 2026-08 實測:7-review 新增的多行第一項
    讓 quickstart 只剩那一項,後面 7 項全數遺失,而 renderer fixed point
    與 parity 都不會紅(兩邊一起截斷,互相自洽)。
    改成讀整個區段並支援續行;回歸斷言住 check-methodology-corrections.sh。
    """
    source = read("_templates/7-review.md")
    section = re.search(r"^## Exit Checklist[^\n]*\n(.*?)(?=^## |\Z)", source, re.M | re.S)
    if not section:
        raise SystemExit("_templates/7-review.md: Exit Checklist not found")
    body = section.group(1)
    first = re.search(r"^- \[ \]", body, re.M)
    if not first:
        raise SystemExit("_templates/7-review.md: Exit Checklist 區段內找不到任何 `- [ ]` 項目")
    return body[first.start():].rstrip("\n") + "\n"


# README §3 用途欄是一句摘要;細節住 guide 各站,不再把整表當 README 衍生副本。
# Gate 欄仍由 gate-consistency 與 check-methodology-corrections 抽 README。
fragments = {
    ("guides/guide-dev-flow.html", "template2-checklist"):
        quote_region("_templates/2-decision.md", "執行清單("),
    ("guides/guide-dev-flow.html", "template3-checklist"):
        quote_region("_templates/3-prototype.md", "執行清單("),
    ("guides/guide-dev-flow.html", "template4-laws"):
        quote_region("_templates/4-spec.md", "反模糊三律(", "執行清單("),
    ("guides/guide-dev-flow.html", "template4-checklist"):
        quote_region("_templates/4-spec.md", "執行清單(", "起草前估"),
    ("guides/guide-dev-flow.html", "template5-checklist"):
        quote_region("_templates/5-tasks.md", "執行清單("),
    ("guides/guide-dev-flow.html", "template6-checklist"):
        quote_region("_templates/6-implementation-notes.md", "執行清單(", "實作期規則("),
    ("guides/guide-dev-flow.html", "template6-rules"):
        quote_region("_templates/6-implementation-notes.md", "實作期規則("),
    ("guides/guide-dev-flow.html", "template7-checklist"):
        quote_region("_templates/7-review.md", "執行清單("),
    ("guides/guide-dev-flow.html", "readme-reviewer-selection-flow"):
        bullet("README.md", "審查者產生"),
    ("guides/guide-quickstart.html", "readme-stage6-seam-quickstart"): fenced_seam(),
    ("guides/guide-quickstart.html", "readme-reviewer-selection-quickstart"):
        bullet("README.md", "審查者產生"),
    ("guides/guide-quickstart.html", "readme-gate-model-quickstart"):
        bullet("README.md", "G1/G2/G3 審查與 verdict"),
    ("guides/guide-quickstart.html", "template7-exit-quickstart"): exit_checklist(),
}


def replace_marker(source, marker, rendered):
    pattern = re.compile(
        rf"^(?P<indent>[ \t]*)<!-- parity:start {re.escape(marker)} -->\s*.*?"
        rf"^[ \t]*<!-- parity:end {re.escape(marker)} -->",
        re.M | re.S)
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"marker {marker!r}: expected one region, found {len(matches)}")
    indent = matches[0].group("indent")
    body = "\n".join(indent + line if line else "" for line in rendered.rstrip().splitlines())
    replacement = (f"{indent}<!-- parity:start {marker} -->\n{body}\n"
                   f"{indent}<!-- parity:end {marker} -->")
    return source[:matches[0].start()] + replacement + source[matches[0].end():]


expected = {}
for (rel, marker), markdown in fragments.items():
    current = expected.get(rel, read(rel))
    expected[rel] = replace_marker(current, marker, renderer.render(markdown))


def strip_frontmatter(source):
    match = re.match(r"\A---\n.*?\n---\n", source, re.S)
    return source[match.end():] if match else source


shell = read("_templates/html-shell.html")
for rel in (
    "example/contract-expiry-reminder/4-spec.md",
    "example/contract-expiry-reminder/5-tasks.md",
    "example/contract-expiry-reminder/6-implementation-notes.md",
    "example/contract-expiry-reminder/7-review.md",
):
    markdown = strip_frontmatter(read(rel))
    title_match = re.search(r"^#\s+(.+)$", markdown, re.M)
    if not title_match:
        raise SystemExit(f"{rel}: H1 title not found")
    title = title_match.group(1).strip()
    body = renderer.render(markdown).rstrip()
    page = shell.replace("{{TITLE}}", html.escape(title, quote=True))
    marker = "  <!-- {{CONTENT}} -->"
    if page.count(marker) != 1:
        raise SystemExit("_templates/html-shell.html: content marker must occur exactly once")
    page = page.replace(marker, body).rstrip("\n") + "\n"
    expected[rel[:-3] + ".html"] = page

changed = []
for rel, wanted in expected.items():
    path = root / rel
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current != wanted:
        changed.append(rel)
        if mode == "--write":
            path.write_text(wanted, encoding="utf-8")

if changed and mode == "--check":
    print("derived files are stale:", file=sys.stderr)
    for rel in changed:
        print(f"  - {rel}", file=sys.stderr)
    raise SystemExit(1)
if mode == "--write":
    print(f"rendered {len(changed)} changed derived files ({len(expected)} tracked outputs checked)")
else:
    print(f"✅ renderer fixed point: {len(expected)}/{len(expected)} tracked outputs byte-identical")
PY
