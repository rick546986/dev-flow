#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 6 站審碼頁產生器 —— 從 6-implementation-notes.md 的 ## Diff 產出 hunk 頁。

契約:notes/design/stage5-review-ui-contract.md §第6站審碼
牙:scripts/check-stage6-hunk-contract.sh

這支只產第 6 站給人審的色碼 hunk 頁。不進 build-gate-twin.py STAGES
(那支是 2-decision | 4-spec | 7-review | 5-tasks 的 gate 卡／執行板)。
不包 markdown-it + html-shell。不發明產品規則。

chrome 跟第 2／4／5 站同一套 token( --ground／--panel／--accent,
加 --ok-soft／--bad-soft)。每個改過的函式自己一塊 details.hunk。

用法:
  scripts/build-stage6-html.py <6-implementation-notes.md> [--out PATH]
  scripts/build-stage6-html.py --fixture

--fixture 把 scripts/fixtures/stage6-html/hunk-page.md 印到 stdout。
給檔時預設寫同目錄 6-implementation-notes.html(或 --out)。

exit:0 = 寫出 / 1 = 解析不到 ## Diff hunk / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "scripts" / "fixtures" / "stage6-html" / "hunk-page.md"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
H2_RE = re.compile(r"^##[ \t]+(.+?)\s*$", re.M)
HUNK_HEAD_RE = re.compile(
    r"^###[ \t]+(.+?)[ \t]+·[ \t]+`([^`]+)`[ \t]+(\S+)[ \t]+((?:T-\S+)(?:[ \t]+T-\S+)?)\s*$",
    re.M,
)
WHY_RE = re.compile(r"^改什麼[:：]\s*(.+)\s*$", re.M)
REL_RE = re.compile(r"^關聯[:：]?\s*(.+)\s*$", re.M)
T_HEAD_RE = re.compile(r"^#{2,4}[ \t]+(T-\d+\S*)\b(.*)$", re.M)
FENCE_RE = re.compile(r"^```(?:diff)?\s*\n(.*?)^```\s*$", re.M | re.S)
SKIP_DIFF_META = re.compile(r"^(diff --git |index |--- |\+\+\+ |@@ )")

# 跟第 2／4／5 站同一盤 token。只抄 chrome + hunk 所需 class,不 import gate-twin。
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
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0e1116; --panel:#161a21; --sunk:#1b2029;
    --ink:#e6e9f0; --ink-2:#a6afc1; --ink-3:#7b8598;
    --rule:#2a303b; --rule-2:#212731;
    --accent:#7fa0e0; --accent-soft:#1b2436;
    --ok:#4fbe86; --ok-soft:#132a20;
    --warn:#dda944; --warn-soft:#2c2415;
    --bad:#e4796f; --bad-soft:#2e1a19;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --ground:#0e1116; --panel:#161a21; --sunk:#1b2029;
  --ink:#e6e9f0; --ink-2:#a6afc1; --ink-3:#7b8598;
  --rule:#2a303b; --rule-2:#212731;
  --accent:#7fa0e0; --accent-soft:#1b2436;
  --ok:#4fbe86; --ok-soft:#132a20;
  --warn:#dda944; --warn-soft:#2c2415;
  --bad:#e4796f; --bad-soft:#2e1a19;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif;
  -webkit-font-smoothing:antialiased}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.86em;font-variant-numeric:tabular-nums}
code{background:var(--sunk);border-radius:3px;padding:1px 5px;color:var(--ink-2)}
a{color:var(--accent)}
.wrap{max-width:900px;margin:0 auto;padding:0 20px 96px}
.masthead{padding:34px 0 20px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin:0 0 8px}
h1{font-size:1.62rem;line-height:1.3;margin:0 0 10px;letter-spacing:-.01em;text-wrap:balance}
.sub{color:var(--ink-2);margin:0;font-size:.94rem;max-width:62ch}
.r-block{margin:30px 0 0;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);overflow:hidden;box-shadow:var(--shadow)}
.r-head{display:flex;gap:13px;align-items:flex-start;padding:15px 18px;
  border-bottom:1px solid var(--rule-2);border-left:4px solid var(--accent)}
.r-name{font-weight:650}
.r-body{padding:14px 18px 16px;font-size:.94rem;color:var(--ink)}
.r-body p{margin:0 0 8px}
.r-body p:last-child{margin-bottom:0}
.tag{font-size:.71rem;padding:2px 8px;border-radius:99px;font-weight:600}
.tag.base{background:var(--sunk);color:var(--ink-3)}
details.hunk{border:1px solid var(--rule);border-radius:9px;margin:10px 12px 12px;
  background:var(--sunk);overflow:hidden}
details.hunk>summary{cursor:pointer;padding:11px 15px;font-weight:600;font-size:.9rem;
  list-style:none;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
details.hunk>summary::-webkit-details-marker{display:none}
.hunk-why,.hunk-rel{margin:8px 15px;font-size:.9rem}
.hunk-why{color:var(--ink)}
.hunk-rel{color:var(--ink-2)}
.diff{margin:0 12px 12px;border:1px solid var(--rule);border-radius:7px;overflow:auto;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.82rem}
.ln{display:flex;white-space:pre;padding:1px 10px;line-height:1.55}
.ln .m{display:inline-block;width:1.2em;flex:none;color:var(--ink-3)}
.ln.ctx{color:var(--ink-3);background:var(--panel)}
.ln.add{background:var(--ok-soft);color:var(--ok)}
.ln.del{background:var(--bad-soft);color:var(--bad)}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
@media (max-width:560px){h1{font-size:1.35rem}}
"""


def usage():
    print(
        "用法:build-stage6-html.py <6-implementation-notes.md> [--out PATH]\n"
        "     build-stage6-html.py --fixture\n"
        "契約:notes/design/stage5-review-ui-contract.md §第6站審碼\n"
        "產檔器吃 ## Diff:每個函式一塊,吐 details.hunk／hunk-why／hunk-rel／.ln.add。\n"
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
    """抽第一個標題落在 names 的 ## 節(到下一 ##)。"""
    wanted = {name.lower() for name in names}
    found = list(H2_RE.finditer(text or ""))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        key = title.split("(", 1)[0].strip().lower()
        if key not in wanted and title.lower() not in wanted:
            continue
        stop = found[i + 1].start() if i + 1 < len(found) else len(text)
        return title, text[match.end():stop]
    return None, ""


def plain_paragraphs(body):
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    chunks = []
    for block in re.split(r"\n\s*\n", body.strip()):
        line = " ".join(part.strip() for part in block.splitlines() if part.strip())
        if line.startswith("#"):
            continue
        if line:
            chunks.append(line)
    return chunks


def parse_t_cards(text, diff_span):
    cards = []
    for match in T_HEAD_RE.finditer(text or ""):
        if diff_span and diff_span[0] <= match.start() < diff_span[1]:
            continue
        tid = match.group(1).strip()
        rest = (match.group(2) or "").strip()
        start = match.end()
        nxt = T_HEAD_RE.search(text, start)
        h2 = H2_RE.search(text, start)
        stop = len(text)
        for cand in (nxt, h2):
            if cand and cand.start() < stop:
                stop = cand.start()
        paras = plain_paragraphs(text[start:stop])
        cards.append((tid, rest, paras[:3]))
    return cards


def parse_hunks(diff_body):
    hunks = []
    for match in HUNK_HEAD_RE.finditer(diff_body or ""):
        fn = match.group(1).strip()
        path = match.group(2).strip()
        lines = match.group(3).strip()
        tags = match.group(4).split()
        start = match.end()
        nxt = HUNK_HEAD_RE.search(diff_body, start)
        stop = nxt.start() if nxt else len(diff_body)
        block = diff_body[start:stop]
        why_m = WHY_RE.search(block)
        rel_m = REL_RE.search(block)
        fence = FENCE_RE.search(block)
        diff_text = fence.group(1) if fence else ""
        hunks.append({
            "fn": fn,
            "file": path,
            "lines": lines,
            "tags": tags,
            "why": why_m.group(1).strip() if why_m else "",
            "rel": rel_m.group(1).strip() if rel_m else "—",
            "diff": diff_text,
        })
    return hunks


def render_diff_lines(diff_text):
    out = []
    for raw in (diff_text or "").splitlines():
        if SKIP_DIFF_META.match(raw):
            continue
        if raw.startswith("+"):
            kind, mark, body = "add", "+", raw[1:]
        elif raw.startswith("-"):
            kind, mark, body = "del", "-", raw[1:]
        else:
            kind, mark, body = "ctx", " ", raw[1:] if raw.startswith(" ") else raw
        out.append(
            '<div class="ln %s"><span class="m">%s</span>%s</div>'
            % (kind, esc(mark), esc(body))
        )
    return "\n".join(out)


def render_hunk(hunk):
    tags = "".join(
        '<span class="tag base">%s</span>' % esc(tag) for tag in hunk["tags"]
    )
    why = hunk["why"] or "—"
    if not why.startswith("改什麼"):
        why = "改什麼：" + why
    rel = hunk["rel"] or "—"
    if not rel.startswith("關聯"):
        rel = "關聯：" + rel
    return (
        '<details class="hunk" open>'
        "<summary>%s · <code>%s</code> %s %s</summary>"
        '<p class="hunk-why">%s</p>'
        '<p class="hunk-rel">%s</p>'
        '<div class="diff">\n%s\n</div>'
        "</details>"
    ) % (
        esc(hunk["fn"]),
        esc(hunk["file"]),
        esc(hunk["lines"]),
        tags,
        esc(why),
        esc(rel),
        render_diff_lines(hunk["diff"]),
    )


def render_block(block_id, title, paragraphs):
    body = "".join("<p>%s</p>" % esc(p) for p in paragraphs if p)
    if not body:
        body = "<p>—</p>"
    return (
        '<section class="r-block" id="%s">'
        '<div class="r-head"><span class="r-name">%s</span></div>'
        '<div class="r-body">%s</div>'
        "</section>"
    ) % (esc(block_id), esc(title), body)


def build_html(text):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "6-implementation-notes"
    status = meta.get("status") or ""
    owner = meta.get("owner") or ""
    updated = meta.get("updated") or ""

    _, summary_body = section_named(body, ("摘要",))
    _, changed_body = section_named(body, ("改了什麼", "改了什麽"))
    diff_title, diff_body = section_named(body, ("Diff", "Diff(各 T commit,逐檔折疊)"))
    if diff_title is None:
        die(1, "解析不到 ## Diff 節")

    diff_span = None
    found = list(H2_RE.finditer(body))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        key = title.split("(", 1)[0].strip().lower()
        if key == "diff" or title.lower().startswith("diff"):
            stop = found[i + 1].start() if i + 1 < len(found) else len(body)
            diff_span = (match.start(), stop)
            break

    hunks = parse_hunks(diff_body)
    if not hunks:
        die(1, "解析不到 ## Diff hunk(要 ### <fn> · `<file>` <lines>  T-n)")

    summary_paras = plain_paragraphs(summary_body)
    changed_paras = plain_paragraphs(changed_body)
    if not summary_paras:
        bits = ["slug `%s`" % slug]
        if status:
            bits.append("status %s" % status)
        if owner:
            bits.append("owner %s" % owner)
        if updated:
            bits.append("updated %s" % updated)
        summary_paras = ["／".join(bits)]
    if changed_paras:
        summary_paras = summary_paras + ["改了什麼：" + changed_paras[0]]

    t_cards = parse_t_cards(body, diff_span)
    if not t_cards:
        seen = []
        for hunk in hunks:
            for tag in hunk["tags"]:
                if tag not in seen:
                    seen.append(tag)
                    t_cards.append((tag, "", []))

    blocks = [render_block("summary", "摘要", summary_paras)]
    for tid, rest, paras in t_cards:
        title = (tid + " " + rest).strip()
        blocks.append(render_block(tid, title, paras or ["—"]))

    hunk_html = "\n".join(render_hunk(hunk) for hunk in hunks)
    blocks.append(
        '<section class="r-block" id="hunks">'
        '<div class="r-head"><span class="r-name">Hunks</span></div>'
        "%s"
        "</section>" % hunk_html
    )

    meta_bits = []
    if status:
        meta_bits.append("status %s" % status)
    if owner:
        meta_bits.append("owner %s" % owner)
    sub = "正本是 md 的 ## Diff,這頁由產檔器重生。不要當第二份正本。"
    if meta_bits:
        sub = "／".join(meta_bits) + "。" + sub

    page = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 6-implementation-notes</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · 6-implementation-notes · 審查介面</p>
  <h1>%s</h1>
  <p class="sub">%s</p>
</header>
%s
<p class="src">由 <code>scripts/build-stage6-html.py</code> 從 md ## Diff 解析產生,不包 html-shell。</p>
</div>
</body>
</html>
""" % (esc(slug), CSS, esc(slug), esc(sub), "\n".join(blocks))
    return page


def parse_args(argv):
    if not argv or argv[0] in ("-h", "--help"):
        usage()
        sys.exit(2)
    if argv[0] == "--fixture":
        return "fixture", None
    path = argv[0]
    out = None
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] == "--out" and i + 1 < len(rest):
            out = rest[i + 1]
            i += 2
            continue
        usage()
        sys.exit(2)
    return path, out


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
