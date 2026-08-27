#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 1 掃頁產生器 —— 從 1-discussion.md 產出六件套 1-discussion.html。

用法:
  scripts/build-scan-html.py <1-discussion.md> [--out PATH]
  scripts/build-scan-html.py --action <1-discussion.md> [--out PATH]

預設寫到同目錄 1-discussion.html。
殼只繼承 skills/dev-talk/html-shell.html(置中／有限寬 CSS 已在母版)。
這是掃頁臉,不是 gate twin:不准攤成審查卡、不加 g1-ask／「你要審什麼」／勾選講義。
#scan-now 只從 md「現況圖」節重生,不准拿邏輯圖／明天系統流充這個槽。

exit:0 = 寫出 / 1 = md 缺六件原料或現況圖抽不到 / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHELL = ROOT / "skills" / "dev-talk" / "html-shell.html"
CONTENT_MARK = "<!-- {{CONTENT}} -->"

HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)
OQ_RE = re.compile(r"^[-*]\s*\[(x|~|>)\]\s*(.+)$", re.M)
ARROW_TOKEN_RE = re.compile(r"--([^-\n>]+)-->")
ARROW_SPLIT_RE = re.compile(r"\s*(?:--+>|→|->|↓|▼)\s*")
PAIN_RE = re.compile(r"^痛[:：]")
FM_RE = re.compile(r"\A---\n.*?\n---\n", re.S)


def usage():
    print(
        "用法:build-scan-html.py <1-discussion.md> [--out PATH]\n"
        "     build-scan-html.py --action <1-discussion.md> [--out PATH]",
        file=sys.stderr,
    )


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def esc(text):
    return html.escape(text or "", quote=True)


def strip_fm(text):
    return FM_RE.sub("", text, count=1)


def inner_plain(text):
    text = re.sub(r"<!--.*?-->", "", text or "", flags=re.S)
    return text.strip()


def section_named(text, pred, label):
    found = []
    for match in HEADING_RE.finditer(text):
        title = match.group(2).strip()
        found.append((match.start(), match.end(), match.group(1), title))
    for i, (start, end, marks, title) in enumerate(found):
        if not pred(title):
            continue
        stop = len(text)
        for j in range(i + 1, len(found)):
            if len(found[j][2]) <= len(marks):
                stop = found[j][0]
                break
        return title, text[end:stop]
    raise ValueError("抽不到「%s」節" % label)


def optional_section(text, pred):
    try:
        return section_named(text, pred, "")
    except ValueError:
        return "", ""


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


def first_assumption(*blobs):
    for blob in blobs:
        match = re.search(r"\[Assumption\][^\n|]*", blob or "")
        if match:
            return match.group(0).strip()
    return ""


def clip_label(token):
    text = PAIN_RE.sub("", token or "").strip()
    text = re.sub(r"\s+", "", text)
    if len(text) > 6:
        text = text[:6]
    return text


def split_problem(body):
    text = inner_plain(body)
    text = re.sub(r"^#+\s+.*$", "", text, flags=re.M).strip()
    pain, bypass = "", ""
    match = re.search(r"現在怎麼繞[:：]?\s*(.+)", text, re.S)
    if match:
        bypass = match.group(1).strip()
        pain = text[: match.start()].strip()
    else:
        match = re.search(r"(現在[^。\n]+)", text)
        if match:
            bypass = match.group(1).strip()
            pain = (text[: match.start()] + text[match.end() :]).strip()
        else:
            parts = re.split(r"\n\s*\n", text, maxsplit=1)
            pain = parts[0].strip()
            bypass = parts[1].strip() if len(parts) > 1 else ""
    pain = re.sub(r"^痛[:：]\s*", "", pain)
    pain = re.sub(r"\s+", " ", pain).strip(" 。")
    bypass = re.sub(r"^現在怎麼繞[:：]\s*", "", bypass)
    bypass = re.sub(r"^現在靠\s*", "", bypass)
    bypass = re.sub(r"\s+", " ", bypass).strip(" 。")
    return pain, bypass


def parse_oq(body):
    items = []
    mapping = {"x": "已解", "~": "假設", ">": "移交"}
    for mark, raw in OQ_RE.findall(body or ""):
        q = raw.strip()
        q = re.sub(r"^Q\d+[:：]\s*", "", q)
        q = re.split(r"\s*→\s*", q, maxsplit=1)[0].strip()
        q = q.rstrip("?").strip()
        if q and not q.endswith("?"):
            q = q + "?"
        items.append((q, mapping[mark]))
    return items


def parse_people(md):
    title, body = optional_section(md, lambda t: t.replace(" ", "") == "Actors" or t.startswith("Actors"))
    if not body:
        raise ValueError("抽不到 Actors 表")
    header, rows = parse_table(body)
    if not rows:
        raise ValueError("Actors 表是空的")
    who_i = col_index(header, "Actor", "誰")
    want_i = col_index(header, "真實目標", "要什麼")
    miss_i = col_index(header, "缺少資訊", "缺什麼")
    work, work_body = optional_section(
        md, lambda t: "Workarounds" in t or "土法" in t
    )
    evidence, ev_body = optional_section(md, lambda t: "Evidence" in t or "證據" in t)
    assume = first_assumption(body, work_body, ev_body)
    people = []
    for row in rows:
        who = cell(row, who_i if who_i >= 0 else 0)
        want = cell(row, want_i if want_i >= 0 else 1)
        miss = cell(row, miss_i if miss_i >= 0 else 4)
        if assume and "[Assumption]" not in miss:
            miss = (miss + " " + assume).strip() if miss else assume
        if who:
            people.append((who, want, miss))
    if not people:
        raise ValueError("Actors 沒有可列的人")
    if assume and not any("[Assumption]" in row[2] for row in people):
        who, want, miss = people[0]
        people[0] = (who, want, (miss + " " + assume).strip())
    return people


def parse_ac(body):
    items = []
    current = None
    for raw in (body or "").splitlines():
        stripped = raw.strip()
        if re.match(r"^[-*]\s+從哪看", stripped):
            if current is not None:
                current["where"] = re.sub(r"^[-*]\s+從哪看[:：]?\s*", "", stripped)
            continue
        if re.match(r"^[-*]\s+看到什麼", stripped):
            if current is not None:
                current["see"] = re.sub(
                    r"^[-*]\s+看到什麼(?:算對)?[:：]?\s*", "", stripped
                )
            continue
        if re.match(r"^[-*]\s+拿什麼", stripped):
            continue
        if re.match(r"^[-*]\s+", stripped) and not raw[:1].isspace():
            if current is not None:
                items.append(current)
            rule = re.sub(r"^[-*]\s+", "", stripped)
            rule = re.sub(r"^AC-\S+\s*[（(][^)）]*[)）][:：]?\s*", "", rule)
            current = {"rule": rule, "where": "", "see": ""}
    if current is not None:
        items.append(current)
    return [it for it in items if it["rule"]]


def parse_log(body):
    lines = []
    for raw in (body or "").splitlines():
        stripped = raw.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        lines.append(stripped)
    return lines[:8]


def diagram_ascii(md):
    try:
        title, body = section_named(md, lambda t: "現況圖" in t, "現況圖")
    except ValueError:
        logic, _ = optional_section(md, lambda t: "邏輯圖" in t)
        if logic:
            raise ValueError(
                "現況圖槽仍叫「%s」——先正名或另開「現況圖」節,"
                "不准讓明天系統流佔這個槽" % logic
            )
        raise ValueError("抽不到現況圖")
    fences = re.findall(r"```[^\n]*\n(.*?)```", body, re.S)
    if fences:
        return "\n".join(fences).strip()
    return inner_plain(body)


def diagram_tokens(ascii_text):
    tokens = []
    for raw in (ascii_text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        pieces = []
        pos = 0
        for match in ARROW_TOKEN_RE.finditer(line):
            before = line[pos : match.start()].strip()
            if before:
                pieces.extend(p for p in ARROW_SPLIT_RE.split(before) if p.strip())
            pieces.append(match.group(1).strip())
            pos = match.end()
        rest = line[pos:].strip()
        if rest:
            pieces.extend(p for p in ARROW_SPLIT_RE.split(rest) if p.strip())
        for piece in pieces:
            piece = piece.strip(" -|+")
            if not piece:
                continue
            if tokens and tokens[-1] == piece:
                continue
            tokens.append(piece)
    return tokens


def render_svg(tokens):
    nodes = []
    for token in tokens:
        label = clip_label(token)
        if not label:
            continue
        kind = "b"
        if PAIN_RE.match(token) or "痛" in token:
            kind = "no"
        elif not nodes:
            kind = "hl"
        nodes.append((kind, label, token))
    if not nodes:
        raise ValueError("現況圖抽不到節點")
    if nodes[-1][0] != "no":
        last = nodes[-1]
        nodes[-1] = ("no", last[1], last[2])
    width, node_w, node_h, gap, top = 160, 100, 36, 26, 8
    x = (width - node_w) // 2
    step = node_h + gap
    height = max(top + len(nodes) * step + 28, 220)
    parts = [
        '<svg id="scan-now" viewBox="0 0 %d %d" role="img" '
        'aria-label="現況:誰、怎麼做、痛在哪">' % (width, height),
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto">',
        '<path d="M0,0 L10,5 L0,10 Z" style="fill:var(--muted)"/></marker></defs>',
    ]
    cx = width // 2
    for i, (kind, label, _raw) in enumerate(nodes):
        y = top + i * step
        parts.append(
            '<rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="6"/>'
            % (kind, x, y, node_w, node_h)
        )
        parts.append('<text x="%d" y="%d">%s</text>' % (x + 18, y + 22, esc(label)))
        if i < len(nodes) - 1:
            y1 = y + node_h
            y2 = y + step
            parts.append(
                '<path class="flow" marker-end="url(#arrow)" d="M%d,%d L%d,%d"/>'
                % (cx, y1, cx, y2)
            )
    if nodes[-1][0] == "no":
        cap_y = top + (len(nodes) - 1) * step + node_h + 18
        parts.append(
            '<text class="cap" x="%d" y="%d">痛在這</text>' % (x + 12, cap_y)
        )
    parts.append("</svg>")
    return "\n".join(parts)


def render_fig(ascii_text, actor_names):
    tokens = diagram_tokens(ascii_text)
    has_people = any(any(name and name in tok for name in actor_names) for tok in tokens)
    has_pain = any(PAIN_RE.match(tok) or "痛" in tok for tok in tokens)
    use_svg = len(tokens) >= 2 and (has_people or has_pain or len(tokens) >= 3)
    if use_svg:
        fig = render_svg(tokens)
    else:
        if not ascii_text.strip():
            raise ValueError("現況圖是空的")
        fig = '<pre id="scan-now">%s</pre>' % esc(ascii_text.rstrip())
    return '<div class="figwrap">\n%s\n</div>' % fig


def page_title(md):
    match = re.search(r"^#\s+(.+?)\s*$", md, re.M)
    if match:
        return match.group(1).strip()
    return "1. 討論"


def build_body(md):
    _pt, problem = optional_section(md, lambda t: t.startswith("Problem") or t.startswith("問題"))
    pain, bypass = split_problem(problem)
    if not pain:
        raise ValueError("Problem 抽不到痛")
    _ot, oq_body = optional_section(
        md, lambda t: t.startswith("Open Questions") or "Open Question" in t
    )
    questions = parse_oq(oq_body)
    counts = {"已解": 0, "假設": 0, "移交": 0}
    for _q, state in questions:
        counts[state] = counts.get(state, 0) + 1
    people = parse_people(md)
    actor_names = [who for who, _w, _m in people]
    _at, ac_body = optional_section(md, lambda t: "驗收" in t)
    ac_items = parse_ac(ac_body)
    if not ac_items:
        raise ValueError("抽不到驗收雛形")
    _lt, log_body = optional_section(
        md, lambda t: t.startswith("Interview Log") or "問答" in t
    )
    log_lines = parse_log(log_body)
    if not log_lines and questions:
        log_lines = ["Q:%s 著落:%s" % (q, st) for q, st in questions[:4]]
    if not log_lines:
        raise ValueError("抽不到 Interview Log／問答")
    fig = render_fig(diagram_ascii(md), actor_names)

    badges = [
        '<span class="badge ok">已解 %d</span>' % counts["已解"],
        '<span class="badge warn">假設 %d</span>' % counts["假設"],
        '<span class="badge">移交 %d</span>' % counts["移交"],
    ]
    people_rows = [
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (esc(who), esc(want), esc(miss))
        for who, want, miss in people
    ]
    q_rows = [
        "<tr><td>%s</td><td>%s</td></tr>" % (esc(q), esc(st)) for q, st in questions
    ]
    if not q_rows:
        q_rows = ["<tr><td>（無）</td><td>已解</td></tr>"]
    ac_rows = [
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (esc(it["rule"]), esc(it["where"] or "—"), esc(it["see"] or "—"))
        for it in ac_items
    ]
    log_html = "\n  ".join("<p>%s</p>" % esc(line) for line in log_lines)

    return "\n".join(
        [
            '<section class="sum" id="scan-sum">',
            '  <p class="pain">痛:%s</p>' % esc(pain),
            "  <p>現在怎麼繞:%s</p>" % esc(bypass or "（未寫）"),
            "  " + "\n  ".join(badges),
            "</section>",
            "",
            fig,
            "",
            '<table id="scan-people">',
            "  <tr><th>誰</th><th>要什麼</th><th>缺什麼</th></tr>",
            "  " + "\n  ".join(people_rows),
            "</table>",
            "",
            '<table id="scan-qs">',
            "  <tr><th>題目</th><th>著落</th></tr>",
            "  " + "\n  ".join(q_rows),
            "</table>",
            "",
            '<table id="scan-ac">',
            "  <tr><th>假設…當…則…</th><th>從哪看</th><th>看到什麼</th></tr>",
            "  " + "\n  ".join(ac_rows),
            "</table>",
            "",
            '<details id="scan-log">',
            "  <summary>問答摘要</summary>",
            "  " + log_html,
            "</details>",
            "",
        ]
    )


def parse_args(argv):
    out = None
    paths = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--action":
            i += 1
            if i < len(argv) and not argv[i].startswith("-"):
                paths.append(argv[i])
                i += 1
            continue
        if arg in ("--out", "-o"):
            i += 1
            if i >= len(argv):
                die(2, "--out 需要路徑")
            out = argv[i]
            i += 1
            continue
        if arg in ("-h", "--help"):
            usage()
            sys.exit(0)
        if arg.startswith("-"):
            die(2, "不明參數:%s" % arg)
        paths.append(arg)
        i += 1
    if len(paths) != 1:
        usage()
        sys.exit(2)
    src = pathlib.Path(paths[0]).expanduser().resolve()
    dest = pathlib.Path(out).expanduser().resolve() if out else src.with_name("1-discussion.html")
    return src, dest


def main(argv):
    src, dest = parse_args(argv)
    if not src.is_file():
        die(2, "拒絕:讀不到 %s" % src)
    if not SHELL.is_file():
        die(2, "拒絕:讀不到掃頁母版 %s" % SHELL)
    md = strip_fm(src.read_text(encoding="utf-8"))
    try:
        body = build_body(md)
    except ValueError as exc:
        die(1, "拒絕:%s" % exc)
    shell = SHELL.read_text(encoding="utf-8")
    if CONTENT_MARK not in shell:
        die(2, "掃頁母版缺 %s" % CONTENT_MARK)
    if "{{TITLE}}" not in shell:
        die(2, "掃頁母版缺 {{TITLE}}")
    title = esc(page_title(md))
    if "<title>{{TITLE}}</title>" not in shell:
        die(2, "掃頁母版缺 <title>{{TITLE}}</title>")
    page = shell.replace("<title>{{TITLE}}</title>", "<title>%s</title>" % title, 1)
    page = page.replace(CONTENT_MARK, body, 1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
