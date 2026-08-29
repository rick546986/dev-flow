#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 站審頁產生器 —— 從 2-decision.md 產出分組卡 + Decision 後直式 SVG。

契約:notes/design/stage2-review-ui-contract.md
牙:scripts/check-stage2-card-contract.sh

這支只產第 2 站給人審的頁。不進 build-gate-twin.py STAGES
(那支是 G1 五格卡)。不包 markdown-it + html-shell。
不要「勾選提示」「你要審什麼」Rejected 釘頂那版。不發明產品規則。

用法:
  scripts/build-stage2-html.py <2-decision.md> [--out PATH]
  scripts/build-stage2-html.py --action <2-decision.md> [--out PATH]
  scripts/build-stage2-html.py --fixture

--fixture 把 scripts/fixtures/stage2-html/decision-page.md 印到 stdout。
給檔時預設寫同目錄 2-decision.html(或 --out)。

exit:0 = 寫出 / 1 = 解析不到 Decision 或方案 / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "scripts" / "fixtures" / "stage2-html" / "decision-page.md"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
H2_RE = re.compile(r"^##[ \t]+(.+?)\s*$", re.M)
H3_RE = re.compile(r"^###[ \t]+(.+?)\s*$", re.M)
H4_RE = re.compile(r"^####[ \t]+(.+?)\s*$", re.M)
LIST_RE = re.compile(r"^[-*]\s+(.+)$", re.M)
FIG_HEAD = re.compile(r"^\[([^\]]+)\]\s*(.*)$")

CANVAS_W = 280
BOX_W = 200
BOX_X = 40
CX = 140
TOP = 10
GAP = 22
PAD_TOP = 12
TITLE_H = 16
LINE_H = 14
PAD_BOTTOM = 12

CSS = """
:root{
  --ground:#fbfbfd; --panel:#ffffff; --sunk:#f2f3f7;
  --ink:#161920; --ink-2:#4d5566; --ink-3:#79839a;
  --rule:#dfe2ea; --rule-2:#eceef4;
  --accent:#31508f; --accent-soft:#e8edf8;
  --ok:#1f7a4d; --ok-soft:#e3f3ea;
  --warn:#9a6407; --warn-soft:#fbf0dc;
  --bad:#a83730; --bad-soft:#fae7e5;
  --shadow:0 1px 2px rgba(20,26,40,.05),0 6px 18px -10px rgba(20,26,40,.18);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.86em;background:var(--sunk);border-radius:3px;padding:1px 5px}
.wrap{max-width:900px;margin:0 auto;padding:0 20px 96px}
.masthead{padding:34px 0 20px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin:0 0 8px}
h1{font-size:1.62rem;line-height:1.3;margin:0 0 10px}
.sub{color:var(--ink-2);margin:0;font-size:.94rem}
.dash{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));
  margin:18px 0 0}
.cell{background:var(--panel);border:1px solid var(--rule);border-radius:9px;
  padding:10px 12px}
.cell .k{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3)}
.cell .v{font-size:1.02rem;font-weight:650;line-height:1.3;display:block}
a.cell{text-decoration:none;color:inherit}
a.cell:hover{border-color:var(--accent)}
.r-block{margin:30px 0 0;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);overflow:hidden;box-shadow:var(--shadow)}
.r-head{padding:15px 18px;border-bottom:1px solid var(--rule-2);
  border-left:4px solid var(--accent)}
.r-name{font-weight:650;text-decoration:none}
.r-body{padding:14px 18px 16px}
.group{margin:0 0 16px}
.group h3{margin:0 0 8px;font-size:.95rem}
.card{border:1px solid var(--rule-2);border-radius:8px;padding:10px 12px;
  margin:0 0 8px;background:var(--sunk)}
.figwrap{display:flex;justify-content:center;margin:8px 0}
.vbox{width:100%;max-width:360px;height:auto;display:block}
.vbox .b{fill:var(--panel);stroke:var(--rule);stroke-width:1.2}
.vbox .hl{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.4}
.vbox .nl{font-size:12px;fill:var(--ink);font-weight:650}
.vbox .sm{font-size:10px;fill:var(--ink-2)}
.vbox .flow{stroke:var(--ink-3);stroke-width:1.2;fill:none}
details.bg{margin:10px 0 0}
details.bg>summary{cursor:pointer;color:var(--ink-2)}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
"""


def usage():
    print(
        "用法:build-stage2-html.py <2-decision.md> [--out PATH]\n"
        "     build-stage2-html.py --action <2-decision.md> [--out PATH]\n"
        "     build-stage2-html.py --fixture\n"
        "契約:notes/design/stage2-review-ui-contract.md\n"
        "產檔器吐分組卡 + Decision 後直式 SVG。不進 build-gate-twin.py STAGES,\n"
        "不包 markdown-it + html-shell,不要勾選提示／你要審什麼／Rejected 釘頂。",
        file=sys.stderr,
    )


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def esc(text):
    return html.escape(text or "", quote=False)


def parse_frontmatter(text):
    match = FM_RE.match(text or "")
    if not match:
        return {}, text or ""
    meta = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, text[match.end():]


def section_named(text, names):
    wanted = {name.lower() for name in names}
    found = list(H2_RE.finditer(text or ""))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        key = title.split("(", 1)[0].strip().lower()
        if key not in wanted and title.lower() not in wanted:
            if not any(title.lower().startswith(n) for n in wanted):
                continue
        stop = found[i + 1].start() if i + 1 < len(found) else len(text)
        return title, text[match.end():stop]
    return None, ""


def parse_groups(approaches):
    groups = []
    h3 = list(H3_RE.finditer(approaches or ""))
    if not h3:
        cards = parse_cards(approaches or "")
        if cards:
            groups.append(("方案", cards))
        return groups
    for i, match in enumerate(h3):
        title = match.group(1).strip()
        stop = h3[i + 1].start() if i + 1 < len(h3) else len(approaches)
        cards = parse_cards(approaches[match.end():stop])
        groups.append((title, cards))
    return groups


def parse_table(body):
    rows = []
    header = None
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        if set(cells[0]) <= set("-: "):
            continue
        if header is None:
            header = cells
            continue
        rows.append(cells)
    return header or [], rows


def col_index(header, *needles):
    for i, name in enumerate(header):
        compact = name.replace(" ", "")
        if any(n in compact for n in needles):
            return i
    return -1


def cell(row, idx):
    if idx < 0 or idx >= len(row):
        return ""
    return row[idx].strip()


def parse_cards(blob):
    cards = []
    h4 = list(H4_RE.finditer(blob or ""))
    if h4:
        for i, match in enumerate(h4):
            title = match.group(1).strip()
            stop = h4[i + 1].start() if i + 1 < len(h4) else len(blob)
            body = " ".join(
                line.strip()
                for line in blob[match.end():stop].splitlines()
                if line.strip() and not line.strip().startswith("#")
            )
            cards.append((title, body))
        return cards
    header, rows = parse_table(blob)
    if rows:
        name_i = col_index(header, "方案", "Approach")
        if name_i < 0:
            name_i = 0
        sum_i = col_index(header, "摘要")
        pro_i = col_index(header, "優")
        con_i = col_index(header, "劣")
        for row in rows:
            name = cell(row, name_i)
            if not name or set(name) <= set("-: "):
                continue
            bits = []
            summary = cell(row, sum_i)
            if summary:
                bits.append(summary)
            pro = cell(row, pro_i)
            con = cell(row, con_i)
            if pro:
                bits.append("優:" + pro)
            if con:
                bits.append("劣:" + con)
            if not bits:
                extras = [c for i, c in enumerate(row) if i != name_i and c]
                bits.append("／".join(extras[:3]))
            cards.append((name, " ".join(bits)))
        return cards
    return cards


def parse_steps(fig_body, decision):
    """認 `[A] 標題(選定)` 當一框,框上保留標籤與「選定」,給 fig-text 對文字。"""
    steps = []
    current = None

    def flush():
        if current:
            steps.append(current)

    for raw in (fig_body or "").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("```"):
            continue
        if stripped.startswith("|") or stripped.startswith("<"):
            continue
        match = FIG_HEAD.match(stripped)
        if match:
            flush()
            label = match.group(1).strip()
            rest = match.group(2).strip()
            current = ("[%s] %s" % (label, rest)).strip() if rest else "[%s]" % label
        elif current is None:
            current = stripped
    flush()
    if not steps:
        for item in LIST_RE.findall(fig_body or ""):
            steps.append(item.strip())
    if not steps and decision:
        steps = [decision.strip().split("。")[0][:24] or "選定"]
    return steps[:8]


def render_vbox(steps):
    if not steps:
        die(1, "Decision 後抽不到直式步驟")
    box_h = PAD_TOP + TITLE_H + LINE_H + PAD_BOTTOM
    height = TOP + len(steps) * box_h + (len(steps) - 1) * GAP + TOP
    parts = [
        '<svg class="vbox" viewBox="0 0 %d %d" role="img" aria-label="選定方案步驟">'
        % (CANVAS_W, height),
    ]
    y = TOP
    hl_idx = next((i for i, title in enumerate(steps) if "選定" in title), 0)
    for i, title in enumerate(steps):
        kind = "hl" if i == hl_idx else "b"
        parts.append(
            '  <rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="8"/>'
            % (kind, BOX_X, y, BOX_W, box_h)
        )
        parts.append(
            '  <text class="nl" text-anchor="middle" x="%d" y="%d">%s</text>'
            % (CX, y + PAD_TOP + 12, esc(title))
        )
        if i < len(steps) - 1:
            y1 = y + box_h
            y2 = y1 + GAP
            parts.append(
                '  <path class="flow" d="M%d,%d L%d,%d"/>' % (CX, y1, CX, y2)
            )
        y += box_h + GAP
    parts.append("</svg>")
    return "\n".join(parts)


def first_sentence(body):
    text = re.sub(r"<!--.*?-->", "", body or "", flags=re.S).strip()
    text = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return text


def build_html(text):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "2-decision"
    status = meta.get("status") or ""
    _, approaches = section_named(body, ("Approaches Considered", "Approaches"))
    groups = parse_groups(approaches)
    if not groups:
        die(1, "解析不到分組方案卡")
    _, decision = section_named(body, ("Decision",))
    decision_text = first_sentence(decision)
    if not decision_text:
        die(1, "解析不到 ## Decision")
    _, fig_body = section_named(body, ("方案架構圖",))
    steps = parse_steps(fig_body, decision_text)
    _, rejected = section_named(body, ("Rejected Alternatives", "Rejected"))
    _, rationale = section_named(body, ("Rationale", "既有脈絡"))
    _, context = section_named(body, ("既有脈絡",))
    _, risks = section_named(body, ("Risks & Mitigations", "Risks"))

    empty_groups = [title for title, cards in groups if not cards]
    if empty_groups:
        die(1, "決策點沒有方案卡:" + "、".join(empty_groups))

    group_html = []
    for idx, (title, cards) in enumerate(groups):
        cards_html = "".join(
            '<div class="card"><strong>%s</strong><p>%s</p></div>'
            % (esc(name), esc(blurb or "—"))
            for name, blurb in cards
        )
        group_html.append(
            '<section class="r-block" id="point-%d">'
            '<div class="r-head"><span class="r-name">%s</span></div>'
            '<div class="r-body">%s</div></section>'
            % (idx + 1, esc(title), cards_html)
        )

    bg_bits = []
    for label, blob in (
        ("既有脈絡", context),
        ("Rationale", rationale),
        ("風險", risks),
        ("未採", rejected),
    ):
        prose = first_sentence(blob)
        if prose:
            bg_bits.append("<p><strong>%s</strong> %s</p>" % (esc(label), esc(prose)))
    bg_html = ""
    if bg_bits:
        bg_html = (
            '<details class="bg"><summary>背景</summary>%s</details>'
            % "".join(bg_bits)
        )

    dash = (
        '<div class="dash">'
        '<div class="cell"><span class="k">狀態</span><span class="v">%s</span></div>'
        '<div class="cell"><span class="k">分組</span><span class="v">%d</span></div>'
        '<div class="cell"><span class="k">方案</span><span class="v">%d</span></div>'
        "</div>"
    ) % (
        esc(status or "draft"),
        len(groups),
        sum(len(cards) for _t, cards in groups),
    )

    page = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 2-decision</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · 2-decision · 審查介面</p>
  <h1>%s</h1>
  <p class="sub">正本是 md。這頁是審頁分組卡,不是 gate-twin 勾選卡。</p>
  %s
</header>
<section class="r-block" id="decision">
  <div class="r-head"><span class="r-name">Decision</span></div>
  <div class="r-body">
    <p>%s</p>
  </div>
</section>
<section class="r-block" id="fig">
  <div class="r-head"><h2 class="r-name">方案架構圖</h2></div>
  <div class="r-body"><div class="figwrap">
%s
  </div></div>
</section>
%s
%s
<p class="src">由 <code>scripts/build-stage2-html.py</code> 從 md 解析產生,不包 html-shell。</p>
</div>
</body>
</html>
""" % (
        esc(slug),
        CSS,
        esc(slug),
        dash,
        esc(decision_text),
        render_vbox(steps),
        "\n".join(group_html),
        bg_html,
    )
    return page


def parse_args(argv):
    if not argv or argv[0] in ("-h", "--help"):
        usage()
        sys.exit(2)
    out = None
    fixture = False
    paths = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--fixture":
            fixture = True
            i += 1
            continue
        if arg == "--action":
            i += 1
            if i < len(argv) and not argv[i].startswith("-"):
                paths.append(argv[i])
                i += 1
            continue
        if arg == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
            i += 2
            continue
        if arg.startswith("-"):
            usage()
            sys.exit(2)
        paths.append(arg)
        i += 1
    if fixture:
        return "fixture", out
    if len(paths) != 1:
        usage()
        sys.exit(2)
    return paths[0], out


def main(argv):
    src, out = parse_args(argv)
    if src == "fixture":
        path = FIXTURE
        if not path.is_file():
            die(2, "讀不到 fixture:%s" % path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as err:
            die(2, "讀不到 fixture:%s" % err)
        sys.stdout.write(build_html(text))
        return
    path = pathlib.Path(src)
    if not path.is_file():
        die(2, "讀不到 md:%s" % path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        die(2, "讀不到 md:%s" % err)
    html_out = build_html(text)
    dest = pathlib.Path(out) if out else path.with_suffix(".html")
    try:
        dest.write_text(html_out, encoding="utf-8")
    except OSError as err:
        die(2, "寫不出 html:%s" % err)
    print("wrote %s" % dest)


if __name__ == "__main__":
    main(sys.argv[1:])
