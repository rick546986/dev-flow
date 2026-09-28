#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 docs/adr/*.md 與 docs/dev/HISTORY.md 轉成給人點的 html。

md 是 git 正本。html 隨時可重生,不是第二份正本,也不是 Agent Memory。
不要把 ADR 正文抄進 .dev-flow/decisions。

用法:
  python3 scripts/build-public-docs.py            # 寫入
  python3 scripts/build-public-docs.py --write    # 同上
  python3 scripts/build-public-docs.py --check    # 自檢 + 跟現檔比,過期就紅
  python3 scripts/build-public-docs.py --selftest # 只跑 blocks_to_html 自檢 fixture
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
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
HIST_HEAD = re.compile(r"^## (\d{4}-\d{2}-\d{2}) · ([a-z0-9-]+)(?: · (\S+))?$")
HIST_FIELD = re.compile(r"^-\s+(做了什麼|為什麼|落在哪|詳細|長期決策|另含):\s*(.*)$")
# code span 吃任意長度的反引號串(``a`b`` 內可含單反引號),開關兩端等長。
INLINE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)")
# CommonMark:只有反引號 fence 的 info string 不能含反引號;~~~ fence 的 info 什麼都行。
FENCE_OPEN = re.compile(r"^( {0,3})(?:(`{3,})[ \t]*([^`\s]*)[^`]*|(~{3,})[ \t]*(\S*).*)$")
LIST_ITEM = re.compile(r"^([ \t]*)([-*]|\d+\.)\s+(.*)$")


def _unquote_meta(val):
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    return val


def parse_adr_frontmatter(text):
    """讀 ADR YAML frontmatter 的 status/date/source(列表欄位略過)。"""
    match = FM_RE.match(text or "")
    if not match:
        return {}, text or ""
    meta = {}
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if re.match(r"^[ \t]+-\s+", raw):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.split("#", 1)[0].strip()
        if key in ("topics", "supersedes", "superseded_by"):
            continue
        if value in ("", "|", ">", "null", "~", "[]"):
            continue
        meta[key] = _unquote_meta(value)
    return meta, text[match.end():]

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


def _code_span(raw):
    # CommonMark:內容兩端各有一個空白且不全是空白時,各剝一個(讓 `` `x` `` 能包反引號)。
    if len(raw) >= 2 and raw[0] == " " and raw[-1] == " " and raw.strip():
        raw = raw[1:-1]
    return "<code>" + html.escape(raw) + "</code>"


def inline_md(text):
    out = []
    pos = 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(_code_span(m.group(2)))
        elif m.group(3) is not None:
            out.append("<strong>" + html.escape(m.group(3)) + "</strong>")
        else:
            label = html.escape(m.group(4))
            href = html.escape(m.group(5), quote=True)
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


def _indent_width(ws):
    return len(ws.expandtabs(4))


def _fence_block(lines, i):
    """從開頭 fence 讀到等字元、不短於開頭的關閉 fence;沒關就吃到檔尾。"""
    m = FENCE_OPEN.match(lines[i])
    indent = len(m.group(1))
    mark = m.group(2) or m.group(4)
    lang = m.group(3) if m.group(2) else m.group(5)
    close = re.compile(r"^ {0,3}" + re.escape(mark[0]) + "{" + str(len(mark)) + r",}[ \t]*$")
    body = []
    i += 1
    while i < len(lines) and not close.match(lines[i]):
        raw = lines[i]
        lead = len(raw) - len(raw.lstrip(" "))
        body.append(raw[min(lead, indent):])
        i += 1
    if i < len(lines):
        i += 1
    cls = ' class="language-' + html.escape(lang, quote=True) + '"' if lang else ""
    text = "\n".join(html.escape(b, quote=False) for b in body)
    return "<pre><code" + cls + ">" + text + "</code></pre>", i


def _lead(line):
    """行首縮排欄寬(tab 展成 4 欄)。"""
    return _indent_width(line[:len(line) - len(line.lstrip(" \t"))])


def _dedent(line, width):
    """去掉 width 欄的行首縮排(tab 先展開);縮排不足就全去(懶惰接續行)。"""
    ws = line[:len(line) - len(line.lstrip(" \t"))]
    have = _indent_width(ws)
    rest = line[len(ws):]
    return " " * (have - width) + rest if have >= width else rest


def _item_start(line):
    """清單項目開頭(縮排 ≤ 3 欄)→ (marker 縮排, 是否有序, 內容縮排 W, 首行內容);否則 None。

    W = marker 縮排 + marker 寬 + marker 後空白(1–4);空白 ≥ 5 時只算 1(其餘屬項目內容)。
    項目內的後續行以 W 為基準:縮排 ≥ W 的行去掉 W 欄後遞迴當區塊解析。
    """
    m = LIST_ITEM.match(line)
    if not m:
        return None
    indent = _indent_width(m.group(1))
    if indent > 3:
        return None
    after = line[m.end(2):]
    gap = _indent_width(after[:len(after) - len(after.lstrip(" \t"))])
    width = indent + len(m.group(2)) + (gap if gap <= 4 else 1)
    return indent, m.group(2)[0].isdigit(), width, m.group(3)


def _is_list_start(line):
    return _item_start(line) is not None


def _fence_close(line):
    """FENCE_OPEN 命中 → 對應的關閉 fence regex;否則 None。"""
    m = FENCE_OPEN.match(line)
    if not m:
        return None
    mark = m.group(2) or m.group(4)
    return re.compile(r"^ {0,3}" + re.escape(mark[0]) + "{" + str(len(mark)) + r",}[ \t]*$")


def _is_loose(content):
    """項目內容在 fence 外有空行夾在兩個區塊之間 → loose(段落包 <p>);否則 tight。"""
    close = None
    seen_blank = False
    for line in content:
        if close is not None:
            if close.match(line):
                close = None
            continue
        if not line.strip():
            seen_blank = True
            continue
        if seen_blank:
            return True
        close = _fence_close(line)
    return False


def _starts_block(line):
    """會打斷段落的區塊開頭(懶惰接續行不得是這些)。"""
    return bool(FENCE_OPEN.match(line) or re.match(r"^ {0,3}(#{1,6}\s|>|\|)", line))


def _open_paragraph(content):
    """內容最後停在還開著的段落(不在 fence／indented code 內、不是空行、不是標題等區塊)。"""
    state = None                                        # None | para | code | fence
    close = None
    for line in content:
        if state == "fence":
            if close.match(line):
                state = None
            continue
        if not line.strip():
            if state != "code":                         # 空行結束段落;indented code 可夾空行
                state = None
            continue
        if _lead(line) >= 4 and state != "para":
            state = "code"
            continue
        close = _fence_close(line)
        if close is not None:
            state = "fence"
        elif _starts_block(line):
            state = None
        else:
            state = "para"
    return state == "para"


def _list_block(lines, i):
    """從 lines[i](清單項目)讀一段清單。

    每個項目收集自己的內容行(縮排 ≥ W 的行去掉 W 欄;fence 內的空行與內文照收),
    再遞迴 blocks_to_html —— fence、indented code、子清單因此都留在該 <li> 內。
    同層換 ol/ul 就收掉目前的清單、同層另開一個(CommonMark 同一行為)。
    空行之後若下一個非空行縮排 < W → 清單結束(兄弟項目隔空行另開清單,沿用既有輸出)。
    縮排介於 marker 與 W 之間的子項目仍收成子清單(舊輸出相容),此後以它的縮排為 W。
    """
    out = []
    n = len(lines)
    tag = None
    items = []

    def flush():
        if tag:
            out.append("<{0}>{1}</{0}>".format(tag, "".join(items)))

    while i < n:
        st = _item_start(lines[i])
        if st is None:
            break
        indent, ordered, width, first = st
        this_tag = "ol" if ordered else "ul"
        if tag and this_tag != tag:
            flush()
            items = []
        tag = this_tag
        content = [first]
        close = _fence_close(first)
        i += 1
        while i < n:
            raw = lines[i]
            if close is not None:                       # 項目內 fence:空行與內文照收,縮排不足才結束項目
                if raw.strip() and _lead(raw) < width:
                    break
                line = _dedent(raw, width)
                content.append(line)
                if close.match(line):
                    close = None
                i += 1
                continue
            if not raw.strip():
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and _lead(lines[j]) >= width:
                    content.extend([""] * (j - i))
                    i = j
                    continue
                break
            lead = _lead(raw)
            if lead < width and _item_start(raw) and lead > indent:
                width = lead                            # 子項目縮排不足 W:仍收成子清單
            if lead >= width:
                line = _dedent(raw, width)
                content.append(line)
                close = _fence_close(line)
                i += 1
                continue
            if _item_start(raw) or _starts_block(raw) or not _open_paragraph(content):
                break
            content.append(raw.strip())                 # 懶惰接續行:只接在還開著的段落後面
            i += 1
        body = blocks_to_html(content, tight=not _is_loose(content), joiner="")
        items.append("<li>" + body + "</li>")
    flush()
    return "".join(out), i


def _indented_code(lines, i):
    """縮排 ≥ 4 欄的 indented code block;空行可夾在中間,尾端空行不算。"""
    body = []
    n = len(lines)
    while i < n and (not lines[i].strip() or _lead(lines[i]) >= 4):
        body.append(_dedent(lines[i], 4) if lines[i].strip() else "")
        i += 1
    while body and not body[-1]:
        body.pop()
    text = "\n".join(html.escape(b, quote=False) for b in body)
    return "<pre><code>" + text + "</code></pre>", i


def blocks_to_html(lines, tight=False, joiner="\n"):
    """夠用的 md 區塊轉換:標題、fence、indented code、表、(巢狀)清單、引用、段落。不是通用 renderer。

    tight=True(tight 清單項目內)段落不包 <p>。清單項目內容由 _list_block 去縮排後遞迴呼叫本函式。
    維持零相依:ADR 0002 只准 gate twin 解析層用 markdown-it-py,這裡不吃。
    """
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if _lead(line) >= 4:                            # indented code 不能打斷段落:只在區塊開頭判
            block, i = _indented_code(lines, i)
            out.append(block)
            continue
        if FENCE_OPEN.match(line):
            block, i = _fence_block(lines, i)
            out.append(block)
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
        if _is_list_start(line):
            block, i = _list_block(lines, i)
            out.append(block)
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith(">") and not lines[i].lstrip().startswith("|") and not _is_list_start(lines[i]) and not FENCE_OPEN.match(lines[i]):
            para.append(lines[i])
            i += 1
        text = inline_md(" ".join(p.strip() for p in para))
        out.append(text if tight else "<p>" + text + "</p>")
    return joiner.join(out)


# 自檢 fixture:blocks_to_html 支援的語法各一條,--selftest 與 --check 都會跑。
SELFTEST_CASES = [
    (
        "fence 帶語言、escape、保留換行與空行",
        ["```python", "if a < b and c > d:", "", '    print("&")', "```"],
        '<pre><code class="language-python">if a &lt; b and c &gt; d:\n\n'
        '    print("&amp;")</code></pre>',
    ),
    (
        "fence 無語言、內文 # / - / | 不被當成區塊",
        ["段落", "~~~", "# 不是標題", "- 不是清單", "| 不是表 |", "~~~", "尾段"],
        "<p>段落</p>\n<pre><code># 不是標題\n- 不是清單\n| 不是表 |</code></pre>\n<p>尾段</p>",
    ),
    (
        "fence 四個反引號可包三個反引號",
        ["````md", "```", "inner", "```", "````"],
        '<pre><code class="language-md">```\ninner\n```</code></pre>',
    ),
    (
        "巢狀清單:有序/無序混合,子清單在父 <li> 內",
        [
            "1. 甲",
            "   - 甲一",
            "   - 甲二",
            "     1. 甲二之一",
            "     接續行",
            "2. 乙",
            "- 換型別另開同層清單",
        ],
        "<ol><li>甲<ul><li>甲一</li><li>甲二<ol><li>甲二之一 接續行</li></ol></li></ul></li>"
        "<li>乙</li></ol><ul><li>換型別另開同層清單</li></ul>",
    ),
    (
        "扁平清單與接續行行為不變(+ 不是清單記號)",
        ["1. 一", "   + 接續", "2. 二"],
        "<ol><li>一 + 接續</li><li>二</li></ol>",
    ),
    (
        "~~~ fence 的 info string 可含反引號,收尾 ~~~ 不另開 fence",
        ["~~~ js `x`", "q", "~~~", "尾段"],
        '<pre><code class="language-js">q</code></pre>\n<p>尾段</p>',
    ),
    (
        "子清單縮排不一致仍留在同一個子清單",
        ["- a", "    - b", "  - c"],
        "<ul><li>a<ul><li>b</li><li>c</li></ul></li></ul>",
    ),
    (
        "清單項目內縮排的 ``` fence 留在該 <li> 內(含 fence 內空行)",
        ["- 步驟一", "  ```sh", "  make build", "", "  make test", "  ```", "- 步驟二"],
        '<ul><li>步驟一<pre><code class="language-sh">make build\n\nmake test</code></pre></li>'
        "<li>步驟二</li></ul>",
    ),
    (
        "有序清單項目內的 ~~~ fence 以內容縮排(3 欄)為準,fence 內 - 不變清單",
        ["1. 先跑", "   ~~~", "   - 不是清單", "     縮排保留", "   ~~~", "2. 再看"],
        "<ol><li>先跑<pre><code>- 不是清單\n  縮排保留</code></pre></li><li>再看</li></ol>",
    ),
    (
        "巢狀清單的子項目內 fence 留在子 <li> 內,父清單接續",
        ["- 外", "  - 內", "    ```", "    x = 1", "    ```", "  - 內二", "- 外二"],
        "<ul><li>外<ul><li>內<pre><code>x = 1</code></pre></li><li>內二</li></ul></li>"
        "<li>外二</li></ul>",
    ),
    (
        "fence 後縮排不足的行結束清單項目(反例:不硬吞)",
        ["- a", "  ```", "  b", "  ```", "段落"],
        "<ul><li>a<pre><code>b</code></pre></li></ul>\n<p>段落</p>",
    ),
    (
        "4 空格縮排 = indented code(escape、中間空行保留、尾端空行不算)",
        ["段落", "", "    if a < b:", "", "        return 1", "", "尾段"],
        "<p>段落</p>\n<pre><code>if a &lt; b:\n\n    return 1</code></pre>\n<p>尾段</p>",
    ),
    (
        "tab 縮排也是 indented code",
        ["\tx = 1", "\ty = 2"],
        "<pre><code>x = 1\ny = 2</code></pre>",
    ),
    (
        "段落後直接 4 空格不打斷段落(反例:不變 code)",
        ["第一行", "    第二行縮排", "    - 也不是清單"],
        "<p>第一行 第二行縮排 - 也不是清單</p>",
    ),
    (
        "清單項目內 indented code 以內容縮排 + 4 為準(loose 項目包 <p>)",
        ["- 範例:", "", "      echo hi", "", "- 下一項"],
        "<ul><li><p>範例:</p><pre><code>echo hi</code></pre></li></ul>\n<ul><li>下一項</li></ul>",
    ),
    (
        "清單項目內只縮排到內容縮排 + 2 → 仍是段落接續(反例)",
        ["- 項目", "    接續不是 code"],
        "<ul><li>項目 接續不是 code</li></ul>",
    ),
    (
        "有序清單項目內 indented code:內容縮排 3 + 4 = 7 欄",
        ["1. 指令", "", "       ls -la", "2. 結束"],
        "<ol><li><p>指令</p><pre><code>ls -la</code></pre></li><li>結束</li></ol>",
    ),
    (
        "雙反引號 code 可含單反引號,不留字面反引號",
        ["用 ``a`b`` 與 `` `x` `` 還有 `c`"],
        "<p>用 <code>a`b</code> 與 <code>`x`</code> 還有 <code>c</code></p>",
    ),
]


def selftest():
    problems = []
    for name, src, want in SELFTEST_CASES:
        got = blocks_to_html(src)
        if got != want:
            problems.append(name + "\n      want: " + want + "\n      got:  " + got)
    return problems


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
    fm, body_text = parse_adr_frontmatter(text)
    title = ""
    status = fm.get("status", "")
    date = fm.get("date", "")
    source = fm.get("source", "")
    body_lines = []
    context_lines = []
    in_context = False
    for raw in body_text.splitlines():
        if not title:
            hm = H1.match(raw)
            if hm:
                title = hm.group(2).strip()
                continue
        fm_line = FIELD.match(raw)
        if fm_line and not body_lines:
            # 舊 bullet meta 相容(frontmatter 已優先)
            key = fm_line.group(1)
            val = fm_line.group(2).strip()
            if key == "Status" and not status:
                status = val.split("#", 1)[0].strip()
            elif key == "Date" and not date:
                date = val
            elif key == "Source" and not source:
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
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        problems = selftest()
        for p in problems:
            print("  ✗ selftest:" + p)
        if problems:
            print("⛔ public-docs selftest:FAILED")
            return 1
        print("✅ public-docs selftest:{0} 條全過".format(len(SELFTEST_CASES)))
        return 0
    root = os.path.abspath(args.root)
    files = planned_files(root)
    if args.check and args.write:
        print("不可同時 --check 與 --write", file=sys.stderr)
        return 2
    if args.check:
        problems = ["selftest:" + p for p in selftest()]
        problems += check_files(files)
        print("=== public-docs twin ===")
        print("  • blocks_to_html 自檢 {0} 條".format(len(SELFTEST_CASES)))
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
