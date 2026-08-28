#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 5 站審頁產生器 —— 從 5-tasks.md 產出 .r-block 任務卡。

契約:notes/design/stage5-review-ui-contract.md
牙:scripts/check-stage5-card-contract.sh

這支只產第 5 站給人審的頁。不進 build-gate-twin.py STAGES
(那支是執行板)。不包 markdown-it + html-shell。不加「提交判定」。
不發明產品規則。

用法:
  scripts/build-stage5-html.py <5-tasks.md> [--out PATH]
  scripts/build-stage5-html.py --action <5-tasks.md> [--out PATH]
  scripts/build-stage5-html.py --fixture

--fixture 把 scripts/fixtures/stage5-html/tasks-page.md 印到 stdout。
給檔時預設寫同目錄 5-tasks.html(或 --out)。

exit:0 = 寫出 / 1 = 解析不到 T-n / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "scripts" / "fixtures" / "stage5-html" / "tasks-page.md"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
T_HEAD_RE = re.compile(r"^##[ \t]+(T-\d+\S*)\b[ \t]*(.*)$", re.M)
FIELD_RE = re.compile(
    r"^[-*][ \t]+\*{0,2}(Covers|Files|Verify|Blocked-by|Intent|Boundaries)\*{0,2}[ \t]*[:：][ \t]*(.*)$",
    re.M,
)
DONE_RE = re.compile(r"^[-*][ \t]+\[([ xX])\][ \t]+(.+)$", re.M)

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
a.cell:hover{border-color:var(--accent);text-decoration:none}
.r-block{margin:30px 0 0;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);overflow:hidden;box-shadow:var(--shadow)}
.r-head{display:flex;gap:10px;align-items:center;padding:15px 18px;
  border-bottom:1px solid var(--rule-2);border-left:4px solid var(--accent)}
.r-name,.t-line{font-weight:650;text-decoration:none;white-space:nowrap}
.t-line{display:inline-flex;gap:8px;align-items:center}
.tid,.st{white-space:nowrap}
.r-body{padding:14px 18px 16px;overflow-wrap:anywhere;word-break:break-word}
.r-body p{margin:0 0 8px}
.tablewrap{overflow-x:auto}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
"""


def usage():
    print(
        "用法:build-stage5-html.py <5-tasks.md> [--out PATH]\n"
        "     build-stage5-html.py --action <5-tasks.md> [--out PATH]\n"
        "     build-stage5-html.py --fixture\n"
        "契約:notes/design/stage5-review-ui-contract.md\n"
        "產檔器吐 .r-block 卡,T-n 與未完成同行 nowrap。不加提交判定。\n"
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


def parse_tasks(text):
    found = list(T_HEAD_RE.finditer(text or ""))
    tasks = []
    for i, match in enumerate(found):
        tid = match.group(1).strip()
        rest = (match.group(2) or "").strip()
        stop = found[i + 1].start() if i + 1 < len(found) else len(text)
        block = text[match.end():stop]
        fields = {}
        for key, val in FIELD_RE.findall(block):
            fields[key] = val.strip()
        done = None
        for mark, label in DONE_RE.findall(block):
            done = mark.lower() == "x"
            status = "完成" if done else (label.strip() or "未完成")
            break
        if done is None:
            status = "未完成"
        if status != "完成" and "未完成" not in status:
            status = "未完成"
        tasks.append({
            "id": tid,
            "title": rest,
            "status": status,
            "fields": fields,
        })
    return tasks


def render_task(task):
    fields = task["fields"]
    bits = []
    for key in ("Intent", "Covers", "Files", "Verify", "Blocked-by", "Boundaries"):
        if key in fields:
            bits.append("<p><strong>%s</strong> %s</p>" % (esc(key), esc(fields[key])))
    body = "".join(bits) or "<p>—</p>"
    return (
        '<section class="r-block" id="%s">'
        '<div class="r-head"><span class="r-name t-line">'
        '<span class="tid">%s</span><span class="st">%s</span>'
        "</span></div>"
        '<div class="r-body">%s%s</div>'
        "</section>"
    ) % (
        esc(task["id"]),
        esc(task["id"]),
        esc(task["status"]),
        ("<p>%s</p>" % esc(task["title"])) if task["title"] else "",
        body,
    )


def build_html(text):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "5-tasks"
    status = meta.get("status") or ""
    tasks = parse_tasks(body)
    if not tasks:
        die(1, "解析不到 ## T-n")
    open_n = sum(1 for t in tasks if t["status"] != "完成")
    dash = (
        '<div class="dash">'
        '<a class="cell" href="#T-1"><span class="k">狀態</span>'
        '<span class="v">%s</span></a>'
        '<div class="cell"><span class="k">任務</span><span class="v">%d</span></div>'
        '<div class="cell"><span class="k">未完成</span><span class="v">%d</span></div>'
        "</div>"
    ) % (esc(status or "draft"), len(tasks), open_n)
    page = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 5-tasks</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · 5-tasks · 審查介面</p>
  <h1>%s</h1>
  <p class="sub">正本是 md。這頁是審頁任務卡,不是執行板,不加提交判定。</p>
  %s
</header>
<div class="tablewrap">
%s
</div>
<p class="src">由 <code>scripts/build-stage5-html.py</code> 從 md 解析產生,不包 html-shell。</p>
</div>
</body>
</html>
""" % (
        esc(slug),
        CSS,
        esc(slug),
        dash,
        "\n".join(render_task(t) for t in tasks),
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
