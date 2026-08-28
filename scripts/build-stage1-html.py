#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 1 站審頁產生器 —— 從 1-discussion.md 產出摘要／三框現況圖／人表。

契約:notes/design/stage1-review-ui-contract.md
牙:scripts/check-stage1-now-contract.sh

這支只產第 1 站給人審的頁。掃頁仍是 build-scan-html.py(S10,html-shell)。
不改 build-scan-html.py。不進 build-gate-twin.py STAGES。不包 html-shell。
第 1 站三框是另一套,不併進 vbox-fig 生命週期圖規則。不發明產品規則。

用法:
  scripts/build-stage1-html.py <1-discussion.md> [--out PATH]
  scripts/build-stage1-html.py --action <1-discussion.md> [--out PATH]
  scripts/build-stage1-html.py --fixture

--fixture 把 scripts/fixtures/stage1-html/scan-page.md 印到 stdout。
給檔時預設寫同目錄 1-discussion.html(或 --out)。

exit:0 = 寫出 / 1 = 解析不到摘要或三框 / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "scripts" / "fixtures" / "stage1-html" / "scan-page.md"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
H2_RE = re.compile(r"^##[ \t]+(.+?)\s*$", re.M)
OQ_RE = re.compile(r"^[-*]\s*\[(x|~|>)\]\s*(.+)$", re.M)
SEP_LINE_RE = re.compile(r"^(?:--+>|→|->|↓|▼)+$")
FIELD_LABELS = (
    (re.compile(r"^(?:誰|Actor)[:：]\s*", re.I), "who"),
    (re.compile(r"^(?:做什麼|動作|真實動作)[:：]\s*"), "action"),
    (re.compile(r"^(?:工具|用什麼|使用工具)[:：]\s*"), "tool"),
    (re.compile(r"^(?:痛點|痛)[:：]\s*"), "pain"),
)
FRAME_TOP = 8
FRAME_PITCH = 104
CAPTION_EXTRA = 100
VB_W = 200
RECT_X, RECT_W, RECT_H = 20, 160, 88
TEXT_X = 100

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
.sum{margin:0}
.sum .pain{font-weight:650;margin:0 0 8px}
.badge{font-size:.71rem;padding:2px 8px;border-radius:99px;font-weight:600;
  margin-right:6px;display:inline-block}
.badge.ok{background:var(--ok-soft);color:var(--ok)}
.badge.warn{background:var(--warn-soft);color:var(--warn)}
.badge.base{background:var(--sunk);color:var(--ink-3)}
.figwrap{display:flex;justify-content:center;margin:12px 0}
#scan-now{width:100%;max-width:360px;height:auto;display:block}
#scan-now .b{fill:var(--panel);stroke:var(--rule);stroke-width:1.2}
#scan-now .hl{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.4}
#scan-now .no{fill:var(--bad-soft);stroke:var(--bad);stroke-width:1.4}
#scan-now text{font-size:11px;fill:var(--ink);font-family:inherit}
#scan-now text.cap,#scan-now text.no{font-size:10px}
#scan-now text.no{fill:var(--bad)}
#scan-now .flow{stroke:var(--ink-3);stroke-width:1.2;fill:none}
#scan-people{width:100%;border-collapse:collapse;font-size:.92rem}
#scan-people th,#scan-people td{border-bottom:1px solid var(--rule-2);
  text-align:left;padding:8px 6px}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
"""


def usage():
    print(
        "用法:build-stage1-html.py <1-discussion.md> [--out PATH]\n"
        "     build-stage1-html.py --action <1-discussion.md> [--out PATH]\n"
        "     build-stage1-html.py --fixture\n"
        "契約:notes/design/stage1-review-ui-contract.md\n"
        "產檔器吐 .sum#scan-sum／#scan-now／#scan-people。不改 build-scan-html.py,\n"
        "不進 build-gate-twin.py STAGES,不包 markdown-it + html-shell。",
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


def parse_table(body):
    rows = []
    header = None
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and set(cells[0]) <= set("-: "):
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


def split_problem(body):
    text = re.sub(r"<!--.*?-->", "", body or "", flags=re.S).strip()
    pain, bypass = "", ""
    match = re.search(r"現在怎麼繞[:：]?\s*(.+)", text, re.S)
    if match:
        bypass = match.group(1).strip()
        pain = text[: match.start()].strip()
    else:
        parts = re.split(r"\n\s*\n", text, maxsplit=1)
        pain = parts[0].strip()
        bypass = parts[1].strip() if len(parts) > 1 else ""
    pain = re.sub(r"^痛[:：]\s*", "", pain)
    pain = re.sub(r"\s+", " ", pain).strip(" 。")
    bypass = re.sub(r"^現在怎麼繞[:：]\s*", "", bypass)
    bypass = re.sub(r"\s+", " ", bypass).strip(" 。")
    return pain, bypass


def parse_oq(body):
    items = []
    mapping = {"x": "已解", "~": "假設", ">": "移交"}
    for mark, raw in OQ_RE.findall(body or ""):
        q = raw.strip()
        items.append((q, mapping[mark]))
    return items


def parse_frames(body):
    frames = []
    buf = []

    def frame_from_stack(lines):
        who = action = tool = pain = ""
        leftovers = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            hit = False
            for pat, key in FIELD_LABELS:
                if pat.search(line):
                    val = pat.sub("", line).strip()
                    if key == "who":
                        who = val
                    elif key == "action":
                        action = val
                    elif key == "tool":
                        tool = val
                    else:
                        pain = val
                    hit = True
                    break
            if not hit:
                leftovers.append(line)
        if not who and leftovers:
            who = leftovers[0]
        return (who, action, tool, pain)

    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if SEP_LINE_RE.match(line):
            if buf:
                frames.append(frame_from_stack(buf))
                buf = []
            continue
        buf.append(line)
        if len(buf) == 4:
            frames.append(frame_from_stack(buf))
            buf = []
    if buf:
        frames.append(frame_from_stack(buf))
    return [f for f in frames if any(part.strip() for part in f)]


def render_svg(frames):
    if len(frames) != 3:
        die(1, "現況圖必須是直式三框,不是珠鏈")
    height = FRAME_TOP + 3 * FRAME_PITCH + CAPTION_EXTRA
    parts = [
        '<svg id="scan-now" viewBox="0 0 %d %d" role="img" '
        'aria-label="現況三框">' % (VB_W, height),
    ]
    for i, (who, action, tool, pain) in enumerate(frames):
        y = FRAME_TOP + i * FRAME_PITCH
        kind = "no" if i == 2 else ("hl" if i == 0 else "b")
        parts.append(
            '  <rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="6"/>'
            % (kind, RECT_X, y, RECT_W, RECT_H)
        )
        rows = (
            (18, "", who),
            (44, "", action),
            (64, "", tool),
            (84, "no" if i == 2 else "cap", pain),
        )
        for dy, cls, val in rows:
            cls_attr = ' class="%s"' % cls if cls else ""
            parts.append(
                '  <text%s text-anchor="middle" x="%d" y="%d">%s</text>'
                % (cls_attr, TEXT_X, y + dy, esc(val))
            )
        if i < 2:
            y1 = y + RECT_H
            y2 = y + FRAME_PITCH
            parts.append(
                '  <path class="flow" d="M%d,%d L%d,%d"/>' % (TEXT_X, y1, TEXT_X, y2)
            )
    cap_y = FRAME_TOP + 3 * FRAME_PITCH + 12
    parts.append(
        '  <text class="cap" text-anchor="middle" x="%d" y="%d">痛在最後一步</text>'
        % (TEXT_X, cap_y)
    )
    parts.append("</svg>")
    return "\n".join(parts)


def build_html(text):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "1-discussion"
    _, problem = section_named(body, ("Problem", "問題"))
    pain, bypass = split_problem(problem)
    if not pain:
        die(1, "Problem 抽不到痛")
    _, oq_body = section_named(body, ("Open Questions", "Open Question"))
    questions = parse_oq(oq_body)
    counts = {"已解": 0, "假設": 0, "移交": 0}
    for _q, state in questions:
        counts[state] = counts.get(state, 0) + 1
    _, fig_body = section_named(body, ("現況圖",))
    frames = parse_frames(fig_body)
    if len(frames) != 3:
        die(1, "解析不到直式三框現況圖")
    _, actors = section_named(body, ("Actors", "Real-world Context"))
    if "Actor" not in (actors or "") and "誰" not in (actors or ""):
        # Actors may live under Real-world Context; try a nested ## Actors
        _t, actors = section_named(body, ("Actors",))
    header, rows = parse_table(actors)
    if not rows:
        die(1, "Actors 表是空的")
    who_i = col_index(header, "Actor", "誰")
    want_i = col_index(header, "真實目標", "要什麼")
    miss_i = col_index(header, "缺少資訊", "缺什麼")
    people_rows = []
    for row in rows:
        people_rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                esc(cell(row, who_i if who_i >= 0 else 0)),
                esc(cell(row, want_i if want_i >= 0 else 1)),
                esc(cell(row, miss_i if miss_i >= 0 else 4)),
            )
        )
    badges = (
        '<span class="badge ok">已解 %d</span>' % counts["已解"],
        '<span class="badge warn">假設 %d</span>' % counts["假設"],
        '<span class="badge base">移交 %d</span>' % counts["移交"],
    )
    dash = (
        '<div class="dash">'
        '<div class="cell"><span class="k">已解</span><span class="v">%d</span></div>'
        '<div class="cell"><span class="k">假設</span><span class="v">%d</span></div>'
        '<div class="cell"><span class="k">移交</span><span class="v">%d</span></div>'
        "</div>"
    ) % (counts["已解"], counts["假設"], counts["移交"])
    page = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 1-discussion</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · 1-discussion · 審查介面</p>
  <h1>%s</h1>
  <p class="sub">正本是 md。這頁由產檔器重生,不是掃頁 html-shell。</p>
  %s
</header>
<section class="r-block" id="sum-card">
  <div class="r-head"><span class="r-name">摘要</span></div>
  <div class="r-body">
    <section class="sum" id="scan-sum">
      <p class="pain">痛:%s</p>
      <p>現在怎麼繞:%s</p>
      %s
    </section>
  </div>
</section>
<section class="r-block" id="now-card">
  <div class="r-head"><span class="r-name">現況</span></div>
  <div class="r-body">
    <div class="figwrap">
%s
    </div>
  </div>
</section>
<section class="r-block" id="people-card">
  <div class="r-head"><span class="r-name">誰在做</span></div>
  <div class="r-body">
    <table id="scan-people">
      <tr><th>誰</th><th>要什麼</th><th>缺什麼</th></tr>
      %s
    </table>
  </div>
</section>
<p class="src">由 <code>scripts/build-stage1-html.py</code> 從 md 解析產生,不包 html-shell。</p>
</div>
</body>
</html>
""" % (
        esc(slug),
        CSS,
        esc(slug),
        dash,
        esc(pain),
        esc(bypass or "（未寫）"),
        " ".join(badges),
        render_svg(frames),
        "\n      ".join(people_rows),
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
