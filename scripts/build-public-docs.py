#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 docs/adr/*.md 與 docs/dev/HISTORY.md 轉成給人點的 html。

md 是 git 正本。html 隨時可重生,不是第二份正本,也不是 Agent Memory。
不要把 ADR 正文抄進 .dev-flow/decisions。

用法:
  python3 scripts/build-public-docs.py            # 寫入
  python3 scripts/build-public-docs.py --write    # 同上
  python3 scripts/build-public-docs.py --check    # 跟現檔比,過期就紅
  python3 scripts/build-public-docs.py --root DIR # 指定 repo 根

視覺 token 抄 _templates/html-shell.html,再加 guides 已有的 --acc / .lead / nav。
不另發明第三套顏色。
"""
from __future__ import print_function

import argparse
import html
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(SCRIPT_DIR)

ADR_NAME = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
H1 = re.compile(r"^#\s+(\d{4})\.\s+(.+?)\s*$")
FIELD = re.compile(r"^-\s+(Status|Date|Source):\s*(.+?)\s*$")
HIST_HEAD = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · ([a-z0-9-]+)(?: · (\S+))?$")
HIST_FIELD = re.compile(r"^-\s+(做了什麼|為什麼|落在哪|詳細|長期決策|另含):\s*(.*)$")
INLINE = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)")

# 跟 html-shell 同一盤色,acc 從 guides 既有 token 來。
CSS = """
  :root{--bg:#ffffff;--fg:#1a1a1a;--muted:#666;--line:#e2e2e2;--card:#f7f7f8;
        --ok:#0a7d33;--warn:#b57700;--bad:#c0392b;--acc:#2563eb;}
  @media(prefers-color-scheme:dark){
    :root:not([data-theme="light"]){
      --bg:#141517;--fg:#e8e8e8;--muted:#9a9a9a;--line:#33363a;--card:#1e2023;
      --ok:#37c871;--warn:#e0a93e;--bad:#e46a5a;--acc:#6ea8ff;}
  }
  :root[data-theme="dark"]{--bg:#141517;--fg:#e8e8e8;--muted:#9a9a9a;--line:#33363a;--card:#1e2023;
        --ok:#37c871;--warn:#e0a93e;--bad:#e46a5a;--acc:#6ea8ff;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
       font:15px/1.7 -apple-system,"PingFang TC","Noto Sans TC",sans-serif}
  main{max-width:880px;margin:0 auto;padding:32px 20px 80px}
  h1{font-size:1.5rem;border-bottom:2px solid var(--line);padding-bottom:.4em}
  h2{font-size:1.15rem;margin-top:2em}
  h3{font-size:1rem;margin-top:1.5em}
  .tablewrap{overflow-x:auto}
  table{border-collapse:collapse;width:100%;margin:1em 0}
  th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
  th{background:var(--card)}
  code,pre{background:var(--card);border-radius:4px;
           font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em}
  pre{padding:12px;overflow-x:auto}
  code{padding:1px 5px}
  blockquote{margin:1em 0;padding:.5em 1em;border-left:3px solid var(--line);color:var(--muted)}
  ul,ol{padding-left:1.4em}
  .meta{color:var(--muted);font-size:.85rem;margin-bottom:2em}
  .badge{display:inline-block;padding:2px 10px;border-radius:999px;
         font-size:.8rem;font-weight:600;border:1px solid transparent}
  .ok{background:color-mix(in srgb,var(--ok) 14%,transparent);color:var(--ok)}
  .warn{background:color-mix(in srgb,var(--warn) 16%,transparent);color:var(--warn)}
  .bad{background:color-mix(in srgb,var(--bad) 14%,transparent);color:var(--bad)}
  details{margin:.6em 0}
  details>summary{cursor:pointer;color:var(--muted)}
  a{color:var(--acc)}
  nav{background:var(--card);border:1px solid var(--line);border-radius:10px;
      padding:10px 16px;margin:1em 0;display:flex;flex-wrap:wrap;gap:6px 16px}
  nav a{text-decoration:none;font-size:.9rem}
  .lead{margin:.2em 0 .9em;padding:.5em .85em;border-left:3px solid var(--acc);
        background:var(--card);border-radius:0 6px 6px 0;font-size:.92rem}
  .foot{margin-top:3em;font-size:.85rem;color:var(--muted);
        border-top:1px solid var(--line);padding-top:1em}
""".strip()


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    directory = os.path.dirname(path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    if not text.endswith("\n"):
        text = text + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def inline_md(text):
    out = []
    pos = 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<code>" + html.escape(m.group(1)) + "</code>")
        elif m.group(2) is not None:
            out.append("<strong>" + html.escape(m.group(2)) + "</strong>")
        else:
            label = html.escape(m.group(3))
            href = html.escape(m.group(4), quote=True)
            out.append('<a href="' + href + '">' + label + "</a>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def _split_table_row(line):
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [c.strip() for c in raw.split("|")]


def _is_table_sep(line):
    cells = _split_table_row(line)
    if not cells:
        return False
    for cell in cells:
        if not re.fullmatch(r":?-{3,}:?", cell):
            return False
    return True


def blocks_to_html(lines):
    """夠用的 md 區塊轉換:標題、表、清單、引用、段落。不是通用 renderer。"""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        hm = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if hm:
            level = len(hm.group(1))
            out.append("<h{0}>{1}</h{0}>".format(level, inline_md(hm.group(2))))
            i += 1
            continue
        if line.startswith(">"):
            quote = []
            while i < n and (lines[i].startswith(">") or not lines[i].strip()):
                if lines[i].startswith(">"):
                    quote.append(lines[i][1:].lstrip())
                i += 1
            out.append("<blockquote>" + "<br>".join(inline_md(q) for q in quote if q) + "</blockquote>")
            continue
        if line.lstrip().startswith("|") and i + 1 < n and _is_table_sep(lines[i + 1]):
            headers = _split_table_row(line)
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append(_split_table_row(lines[i]))
                i += 1
            bits = ['<div class="tablewrap"><table><thead><tr>']
            for h in headers:
                bits.append("<th>" + inline_md(h) + "</th>")
            bits.append("</tr></thead><tbody>")
            for row in rows:
                bits.append("<tr>")
                for cell in row:
                    bits.append("<td>" + inline_md(cell) + "</td>")
                bits.append("</tr>")
            bits.append("</tbody></table></div>")
            out.append("".join(bits))
            continue
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])):
                item = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i])
                i += 1
                while i < n and lines[i].startswith("  ") and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[i]):
                    item = item + " " + lines[i].strip()
                    i += 1
                items.append("<li>" + inline_md(item) + "</li>")
            out.append("<{0}>{1}</{0}>".format(tag, "".join(items)))
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith(">") and not lines[i].lstrip().startswith("|") and not re.match(r"^\s*[-*]\s+", lines[i]) and not re.match(r"^\s*\d+\.\s+", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + inline_md(" ".join(p.strip() for p in para)) + "</p>")
    return "\n".join(out)


def first_sentence(text):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    cut = text.find("。")
    if cut == -1:
        return text
    return text[: cut + 1]


def parse_adr(path):
    text = read_text(path)
    name = os.path.basename(path)
    mname = ADR_NAME.match(name)
    if not mname:
        raise ValueError("ADR 檔名不合規:" + name)
    number = mname.group(1)
    title = ""
    status = ""
    date = ""
    source = ""
    body_lines = []
    context_lines = []
    in_context = False
    for raw in text.splitlines():
        if not title:
            hm = H1.match(raw)
            if hm:
                title = hm.group(2).strip()
                continue
        fm = FIELD.match(raw)
        if fm and not body_lines:
            key = fm.group(1)
            val = fm.group(2).strip()
            if key == "Status":
                status = val.split("#", 1)[0].strip()
            elif key == "Date":
                date = val
            elif key == "Source":
                source = val
            continue
        if raw.startswith("## "):
            in_context = raw.startswith("## Context")
        if in_context and not raw.startswith("## ") and not raw.startswith(">") and raw.strip() and not raw.startswith("- "):
            context_lines.append(raw)
        if raw.startswith("## "):
            body_lines.append(raw)
        elif body_lines:
            body_lines.append(raw)
    why = first_sentence(" ".join(context_lines))
    if not title:
        raise ValueError(name + " 沒有 H1 標題")
    return {
        "number": number,
        "slug_file": name[:-3],
        "title": title,
        "status": status or "unknown",
        "date": date,
        "source": source,
        "why": why,
        "body_html": blocks_to_html(body_lines),
    }


def parse_history(path):
    lines = read_text(path).splitlines()
    entries = []
    i = 0
    while i < len(lines):
        m = HIST_HEAD.match(lines[i])
        if not m:
            i += 1
            continue
        rec = {
            "date": m.group(1),
            "slug": m.group(2),
            "version": m.group(3) or "",
            "做了什麼": "",
            "為什麼": "",
            "落在哪": "",
            "詳細": "",
            "長期決策": "",
            "另含": "",
        }
        i += 1
        extras = []
        while i < len(lines) and not lines[i].startswith("## "):
            fm = HIST_FIELD.match(lines[i])
            if fm:
                rec[fm.group(1)] = fm.group(2).strip()
            elif lines[i].strip():
                extras.append(lines[i].strip())
            i += 1
        if extras and not rec["另含"]:
            rec["另含"] = " ".join(extras)
        entries.append(rec)
    return entries


def badge_class(status):
    low = status.lower()
    if "accept" in low:
        return "ok"
    if "super" in low or "deprecat" in low:
        return "warn"
    if "reject" in low:
        return "bad"
    return "warn"


def page(title, body, extra_nav=""):
    nav = extra_nav
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-TW">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + html.escape(title) + "</title>\n"
        "<style>\n" + CSS + "\n</style>\n"
        "</head>\n"
        "<body>\n"
        "<main>\n"
        + nav
        + body
        + '\n<p class="foot">md 是 git 正本。本頁由 <code>scripts/build-public-docs.py</code> 重生。'
        "不是 Agent Memory,不要把正文抄進 <code>.dev-flow/decisions</code>。</p>\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


def render_index(adrs):
    rows = []
    for a in adrs:
        href = html.escape(
            "https://rick546986.github.io/dev-flow/docs/adr/"
            + a["slug_file"] + ".html",
            quote=True,
        )
        rows.append(
            "<tr>"
            "<td>" + html.escape(a["number"]) + "</td>"
            '<td><a href="' + href + '">' + html.escape(a["title"]) + "</a></td>"
            '<td><span class="badge ' + badge_class(a["status"]) + '">'
            + html.escape(a["status"]) + "</span></td>"
            "<td>" + inline_md(a["why"]) + "</td>"
            "</tr>"
        )
    body = (
        "<h1>長期決策</h1>\n"
        '<p class="lead">人要看為什麼當初這樣選,走這裡。'
        "yaml / <code>.dev-flow/decisions</code> 不是給人讀的頁。</p>\n"
        "<nav>"
        '<a href="https://rick546986.github.io/dev-flow/docs/dev/HISTORY.html">改版歷史</a>'
        '<a href="https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html">dev-flow 導覽</a>'
        '<a href="https://github.com/rick546986/dev-flow/tree/main/docs/adr">md 正本</a>'
        "</nav>\n"
        '<div class="tablewrap"><table>\n'
        "<thead><tr><th>編號</th><th>標題</th><th>狀態</th><th>為什麼</th></tr></thead>\n"
        "<tbody>\n" + "\n".join(rows) + "\n</tbody></table></div>\n"
    )
    return page("長期決策 · ADR", body)


def render_adr(a):
    src = inline_md(a["source"]) if a["source"] else ""
    body = (
        "<h1>" + html.escape(a["number"] + ". " + a["title"]) + "</h1>\n"
        '<p class="meta">'
        '<span class="badge ' + badge_class(a["status"]) + '">'
        + html.escape(a["status"]) + "</span> · "
        + html.escape(a["date"])
        + (" · 出處:" + src if src else "")
        + "</p>\n"
        "<nav>"
        '<a href="https://rick546986.github.io/dev-flow/docs/adr/index.html">決策列表</a>'
        '<a href="' + html.escape(a["slug_file"] + ".md", quote=True) + '">md 正本</a>'
        '<a href="https://rick546986.github.io/dev-flow/docs/dev/HISTORY.html">改版歷史</a>'
        "</nav>\n"
        + a["body_html"]
        + "\n"
    )
    return page(a["number"] + ". " + a["title"], body)


def render_history(entries):
    newest = list(reversed(entries))
    rows = []
    for e in newest:
        extra = []
        if e["落在哪"]:
            extra.append("<div><strong>落在哪</strong> " + html.escape(e["落在哪"]) + "</div>")
        if e["詳細"]:
            extra.append("<div><strong>詳細</strong> " + inline_md(e["詳細"]) + "</div>")
        if e["長期決策"]:
            extra.append("<div><strong>長期決策</strong> " + html.escape(e["長期決策"]) + "</div>")
        if e["另含"]:
            extra.append("<div>" + html.escape(e["另含"]) + "</div>")
        details = ""
        if extra:
            details = (
                "<details><summary>落點與細節</summary>"
                + "".join(extra)
                + "</details>"
            )
        ver = (" · " + html.escape(e["version"])) if e["version"] else ""
        rows.append(
            "<tr>"
            "<td>" + html.escape(e["date"]) + "</td>"
            "<td>" + html.escape(e["slug"]) + ver + "</td>"
            "<td>" + html.escape(e["做了什麼"]) + details + "</td>"
            "<td>" + html.escape(e["為什麼"]) + "</td>"
            "</tr>"
        )
    body = (
        "<h1>改版歷史</h1>\n"
        '<p class="lead">只看日期、做了什麼、為什麼。'
        "最新的在上面。要改這份紀錄,走 <code>scripts/history-append.sh</code>,不要手改 md。</p>\n"
        "<nav>"
        '<a href="https://rick546986.github.io/dev-flow/docs/adr/index.html">決策列表</a>'
        '<a href="HISTORY.md">md 正本</a>'
        '<a href="https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html">dev-flow 導覽</a>'
        "</nav>\n"
        '<div class="tablewrap"><table>\n'
        "<thead><tr><th>日期</th><th>代號</th><th>做了什麼</th><th>為什麼</th></tr></thead>\n"
        "<tbody>\n" + "\n".join(rows) + "\n</tbody></table></div>\n"
    )
    return page("改版歷史", body)


def planned_files(root):
    adr_dir = os.path.join(root, "docs", "adr")
    hist_path = os.path.join(root, "docs", "dev", "HISTORY.md")
    if not os.path.isdir(adr_dir):
        raise SystemExit("找不到 docs/adr/")
    if not os.path.isfile(hist_path):
        raise SystemExit("找不到 docs/dev/HISTORY.md")
    md_names = sorted(n for n in os.listdir(adr_dir) if n.endswith(".md"))
    adrs = []
    for name in md_names:
        if not ADR_NAME.match(name):
            raise SystemExit("ADR 檔名不合規:" + name)
        adrs.append(parse_adr(os.path.join(adr_dir, name)))
    if not adrs:
        raise SystemExit("docs/adr/ 沒有任何 ADR")
    entries = parse_history(hist_path)
    if not entries:
        raise SystemExit("HISTORY.md 抽不到任何條目")
    files = {
        os.path.join(adr_dir, "index.html"): render_index(adrs),
        os.path.join(root, "docs", "dev", "HISTORY.html"): render_history(entries),
    }
    for a in adrs:
        files[os.path.join(adr_dir, a["slug_file"] + ".html")] = render_adr(a)
    return files


def check_files(files):
    problems = []
    for path, want in sorted(files.items()):
        if not os.path.isfile(path):
            problems.append("缺檔:" + path)
            continue
        got = read_text(path)
        if got != want:
            problems.append("過期:" + path + "(跟 md 重生結果不一致,請跑 scripts/build-public-docs.py --write)")
    return problems


def main(argv):
    parser = argparse.ArgumentParser(description="重生 adr / HISTORY 的人頁")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    files = planned_files(root)
    if args.check and args.write:
        print("不可同時 --check 與 --write", file=sys.stderr)
        return 2
    if args.check:
        problems = check_files(files)
        print("=== public-docs twin ===")
        print("  • 應有 {0} 個 html".format(len(files)))
        if problems:
            for p in problems:
                print("  ✗ " + p)
            print("⛔ public-docs twin:FAILED")
            return 1
        print("  ✓ html 與 md 標題/條目同步")
        print("✅ public-docs twin:全過")
        return 0
    for path, text in sorted(files.items()):
        write_text(path, text)
        print("wrote " + os.path.relpath(path, root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
