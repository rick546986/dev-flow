#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可摺疊目錄包含樹產器(dir-tree)。

契約:notes/design/dir-tree-contract.md
牙:scripts/check-dir-tree.sh

吃手寫 YAML 用途表,吐 monospace ├─ │ └─ 巢狀摺疊 HTML。
不要掃 repo 猜 why。每列 why 一句到兩句。預設只露 L1。

用法:
  scripts/build-dir-tree.py --purpose <表.yaml> [--out <html>] [--fragment]
  scripts/build-dir-tree.py --write
  scripts/build-dir-tree.py --check

--write／--check 對的是主指南 guides/guide-dev-flow.html #dirmap
裡 <!-- dir-tree:begin --> … <!-- dir-tree:end --> 那棵片段。
產品 --purpose 仍可吐整頁；--fragment 只吐樹。

無參數或 --help 印用法並 exit 2。
exit:0 = 寫出／對得上 / 1 = 用途表不合法或吐了禁物 / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PURPOSE_PATH = ROOT / "guides" / "dir-tree-purpose.yaml"
GUIDE_PATH = ROOT / "guides" / "guide-dev-flow.html"
FIX_DIR = ROOT / "scripts" / "fixtures" / "dir-tree"
TREE_BEGIN = "<!-- dir-tree:begin -->"
TREE_END = "<!-- dir-tree:end -->"

SCROLL_BLOCK = """<!-- 
  頁內錨點捲動修正：iframe/artifact 載體會把 fragment 導航當新網址，原生 #錨點 不捲動；
  此段攔截頁內錨點點擊改用 scrollIntoView，一般瀏覽器直開不受影響。
-->
<script>
  document.addEventListener('click', function(e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var href = a.getAttribute('href');
    if (href.length <= 1) return;
    var id = decodeURIComponent(href.slice(1));
    var el = document.getElementById(id);
    if (!el) return;
    e.preventDefault();
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.replaceState(null, '', href);
  });
</script>
"""

CSS = """\
  :root{--bg:#ffffff;--fg:#1a1a1a;--muted:#666;--line:#e2e2e2;--card:#f7f7f8;
        --ok:#0a7d33;--warn:#b57700;--bad:#c0392b;--acc:#2563eb;}
  @media(prefers-color-scheme:dark){
    :root{--bg:#141517;--fg:#e8e8e8;--muted:#9a9a9a;--line:#33363a;--card:#1e2023;
          --ok:#37c871;--warn:#e0a93e;--bad:#e46a5a;--acc:#6ea8ff;}
  }
  :root[data-theme="dark"]{--bg:#141517;--fg:#e8e8e8;--muted:#9a9a9a;--line:#33363a;
        --card:#1e2023;--ok:#37c871;--warn:#e0a93e;--bad:#e46a5a;--acc:#6ea8ff;}
  :root[data-theme="light"]{--bg:#ffffff;--fg:#1a1a1a;--muted:#666;--line:#e2e2e2;
        --card:#f7f7f8;--ok:#0a7d33;--warn:#b57700;--bad:#c0392b;--acc:#2563eb;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
       font:15px/1.7 -apple-system,"PingFang TC","Noto Sans TC",sans-serif}
  main{max-width:960px;margin:0 auto;padding:28px 20px 80px}
  h1{font-size:1.5rem;border-bottom:2px solid var(--line);padding-bottom:.4em}
  h2{font-size:1.15rem;margin-top:2.2em}
  nav{background:var(--card);border:1px solid var(--line);border-radius:10px;
      padding:10px 16px;margin:1em 0;display:flex;flex-wrap:wrap;gap:6px 16px}
  nav a{color:var(--acc);text-decoration:none;font-size:.9rem}
  code{background:var(--card);border-radius:4px;padding:1px 5px;
       font-family:ui-monospace,Menlo,monospace;font-size:.88em}
  .muted{color:var(--muted)}
  details{margin:.35em 0 0}
  details>summary{cursor:pointer;color:var(--acc);font-size:.85rem;user-select:none}
  footer.foot{margin-top:3em;font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:1em}

  /* ── Phase 1(guide-dev-talk)定調的可複用 token,勿改名 ───────────── */
  .lead{margin:.2em 0 .9em;padding:.5em .85em;border-left:3px solid var(--acc);
        background:var(--card);border-radius:0 6px 6px 0;font-size:.92rem}
  .tablewrap{overflow-x:auto}

  /* 目錄樹：摺疊仍是一棵 ├─ │ └─ 樹，不是卡片／步驟圖 */
  /* 一根接縫：祖先 .v 每欄都塗；本列 ├─ 仍用 .g:not(.last)::after；.last 不關 .v；不准 .sep */
  .treewrap{overflow-x:auto;background:var(--bg);border:1px solid var(--line);
            border-radius:10px;padding:14px 16px;margin:1em 0}
  .tree{font:13px/1.75 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
        color:var(--fg)}
  .tree details{margin:0}
  .tree .tline{display:grid;grid-template-columns:auto auto minmax(0,1fr);
               align-items:start;column-gap:.5ch}
  .tree summary.tline{list-style:none;cursor:pointer;color:inherit;
                      font-size:inherit;font-weight:400;padding:0;user-select:none}
  .tree summary.tline::-webkit-details-marker{display:none}
  .tree summary.tline::marker{content:""}
  .tree .g{position:relative;color:var(--muted);white-space:pre}
  .tree .g:not(.last)::after{content:"│";font-size:100%;line-height:1;
                             position:absolute;left:calc(100% - 3ch);bottom:0;
                             transform:translateY(50%);color:inherit;pointer-events:none}
  .tree .v{position:relative}
  .tree .v::after{content:"│";position:absolute;left:0;top:50%;
                  font-size:175%;line-height:1;transform:translateY(-50%);
                  color:inherit;pointer-events:none}
  .tree .name{white-space:nowrap}
  .tree summary .name{color:var(--acc)}
  .tree .why{color:var(--muted);min-width:0}
"""


def usage():
    print(
        "用法:build-dir-tree.py --purpose <表.yaml> [--out <html>] [--fragment]\n"
        "     build-dir-tree.py --write\n"
        "     build-dir-tree.py --check\n"
        "契約:notes/design/dir-tree-contract.md\n"
        "--write／--check 把樹插進 guide-dev-flow.html#dirmap。\n"
        "吃手寫 YAML,吐可摺疊 monospace 目錄樹。不准掃 repo 猜 why。",
        file=sys.stderr,
    )


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def esc(text):
    return html.escape(text or "", quote=True)


# ── YAML 子集(與契約範例同形;不支援 flow／anchor／掃目錄)──────────────
class YamlError(ValueError):
    pass


def _parse_scalar(token, lineno):
    token = token.strip()
    if token in ("", "null", "~"):
        return None
    if token == "true":
        return True
    if token == "false":
        return False
    if token.startswith('"'):
        try:
            return json.loads(token)
        except ValueError as exc:
            raise YamlError("第 %d 行:引號字串失敗:%s" % (lineno, exc))
    if token.startswith("'"):
        raise YamlError("第 %d 行:請用雙引號" % lineno)
    if token[0] in "{[&*|>":
        raise YamlError("第 %d 行:不支援 flow／anchor" % lineno)
    return token


def _tokenize(text):
    out = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if raw.startswith("---"):
            raise YamlError("第 %d 行:不支援 ---" % lineno)
        if not raw.strip():
            continue
        stripped = raw.lstrip(" ")
        if stripped.startswith("#"):
            continue
        indent = len(raw) - len(stripped)
        if "\t" in raw[:indent] or raw.startswith("\t"):
            raise YamlError("第 %d 行:縮排不得用 tab" % lineno)
        if indent % 2 != 0:
            raise YamlError("第 %d 行:縮排必須是 2 的倍數" % lineno)
        out.append((indent // 2, stripped.rstrip(), lineno))
    return out


def _split_key(content, lineno):
    m = re.match(r"^([A-Za-z0-9_][A-Za-z0-9_./@+-]*):(?:\s+(.*))?$", content)
    if not m:
        raise YamlError("第 %d 行:不是 key: value" % lineno)
    return m.group(1), (m.group(2) or "")


def _parse_block(tokens, pos, level):
    if pos >= len(tokens):
        return None, pos
    _, content, _ = tokens[pos]
    if content.startswith("- "):
        items = []
        while pos < len(tokens):
            ind, content, lineno = tokens[pos]
            if ind != level or not content.startswith("- "):
                break
            body = content[2:].strip()
            if re.match(r"^[A-Za-z0-9_][A-Za-z0-9_./@+-]*:(\s|$)", body):
                key, token = _split_key(body, lineno)
                if token:
                    item = {key: _parse_scalar(token, lineno)}
                    pos += 1
                else:
                    nested, pos = _parse_block(tokens, pos + 1, level + 2)
                    item = {key: nested}
                while pos < len(tokens) and tokens[pos][0] == level + 1 \
                        and not tokens[pos][1].startswith("- "):
                    _ind2, content2, lineno2 = tokens[pos]
                    key2, token2 = _split_key(content2, lineno2)
                    if token2:
                        item[key2] = _parse_scalar(token2, lineno2)
                        pos += 1
                    else:
                        nested2, pos = _parse_block(tokens, pos + 1, level + 2)
                        item[key2] = nested2
                items.append(item)
            else:
                items.append(_parse_scalar(body, lineno))
                pos += 1
        return items, pos
    mapping = {}
    while pos < len(tokens):
        ind, content, lineno = tokens[pos]
        if ind != level:
            break
        if content.startswith("- "):
            break
        key, token = _split_key(content, lineno)
        if key in mapping:
            raise YamlError("第 %d 行:重複 key %s" % (lineno, key))
        if token:
            mapping[key] = _parse_scalar(token, lineno)
            pos += 1
        else:
            nested, pos = _parse_block(tokens, pos + 1, level + 1)
            mapping[key] = nested
    return mapping, pos


def load_yaml(path):
    try:
        raw = pathlib.Path(path).read_text(encoding="utf-8")
    except OSError as err:
        die(2, "讀不到用途表:%s" % err)
    try:
        tokens = _tokenize(raw)
        if not tokens:
            die(1, "用途表是空的")
        data, pos = _parse_block(tokens, 0, 0)
        if pos != len(tokens):
            die(1, "用途表 YAML 縮排不連續")
    except YamlError as err:
        die(1, "用途表不是契約形 YAML:%s" % err)
    if not isinstance(data, dict):
        die(1, "用途表必須是物件")
    return data


def why_ok(why, minimum=12):
    return isinstance(why, str) and len(why.strip()) >= minimum


def node_why(node, minimum=12):
    why = node.get("why")
    if not why_ok(why, minimum):
        die(1, "列 %s 缺一句到兩句 why" % node.get("name", "?"))
    return why


def expand_ellipsis(node):
    if not isinstance(node, dict):
        die(1, "列不是物件")
    out = dict(node)
    kids = [expand_ellipsis(c) for c in (out.get("children") or [])]
    ell = out.pop("ellipsis", None)
    if ell is not None:
        if not isinstance(ell, str) or len(ell.strip()) < 4:
            die(1, "%s 的 ellipsis 太短" % out.get("name", "?"))
        kids.append({"name": "…", "why": ell.strip(), "virtual": True})
    if kids:
        out["children"] = kids
    else:
        out.pop("children", None)
    return out


def is_virtual(node):
    return bool(node.get("virtual")) or node.get("name") in ("…", "...")


def validate_child(node, root, parent_rel):
    name = node.get("name")
    if not isinstance(name, str) or not name:
        die(1, "列缺 name")
    minimum = 4 if is_virtual(node) else 12
    node_why(node, minimum)
    children = node.get("children") or []
    if children and not isinstance(children, list):
        die(1, "%s 的 children 必須是陣列" % name)
    if is_virtual(node) and children:
        die(1, "ellipsis 列不准再有 children")
    rel = name if not parent_rel else (parent_rel.rstrip("/") + "/" + name)
    if root and not is_virtual(node):
        path = pathlib.Path(root) / rel.rstrip("/")
        if not path.exists():
            die(1, "用途表有、目錄沒有:%s" % rel)
    for child in children:
        if not isinstance(child, dict):
            die(1, "%s 的子列不是物件" % name)
        validate_child(child, root, "" if is_virtual(node) else rel)


def slug_id(rel):
    text = rel.strip("/").replace("/", "-").replace(".", "")
    text = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in text)
    return text.strip("-") or "n"


def why_span(node, minimum=12, filemap_href="#filemap"):
    why = node_why(node, minimum)
    body = esc(why)
    if "#filemap" in why:
        body = body.replace(
            esc("#filemap"),
            '<a href="%s">#filemap</a>' % esc(filemap_href),
        )
    return '<span class="why">%s</span>' % body


def tline(gutter, name, node, summary=False, filemap_href="#filemap", last=False):
    tag = "summary" if summary else "div"
    minimum = 4 if is_virtual(node) else 12
    gcls = "g last" if last else "g"
    return (
        '      <%s class="tline"><span class="%s">%s</span>'
        '<span class="name">%s</span>%s</%s>'
        % (tag, gcls, gutter, esc(name),
           why_span(node, minimum, filemap_href), tag)
    )


def prefix_parts(cont):
    return "".join(
        '<span class="v">│</span>  ' if c else "   " for c in cont
    )


def render_nodes(nodes, cont, parent_rel, lines, filemap_href):
    for i, node in enumerate(nodes):
        last = i == len(nodes) - 1
        prefix = prefix_parts(cont)
        gutter = prefix + ("└─ " if last else "├─ ")
        name = node["name"]
        rel = name if not parent_rel else (parent_rel.rstrip("/") + "/" + name)
        children = node.get("children") or []
        if children:
            nid = node.get("id") or slug_id(rel)
            lines.append('    <details id="%s">' % esc(nid))
            lines.append(tline(gutter, name, node, summary=True,
                              filemap_href=filemap_href, last=last))
            render_nodes(children, cont + [not last], rel, lines, filemap_href)
            lines.append("    </details>")
        else:
            lines.append(tline(gutter, name, node, filemap_href=filemap_href,
                              last=last))


def render_tree(spec, filemap_href="#filemap"):
    root = spec.get("root")
    if not isinstance(root, dict):
        die(1, "用途表要有 root")
    node_why(root)
    name = root.get("name")
    if not isinstance(name, str) or not name:
        die(1, "root 缺 name")
    children = root.get("children") or []
    if not isinstance(children, list) or not children:
        die(1, "root 要有 children")
    lines = [
        '  <div class="treewrap" role="tree" aria-label="%s">'
        % esc(spec.get("aria") or name),
        '  <div class="tree">',
        tline("", name, root, filemap_href=filemap_href, last=True),
        "",
    ]
    render_nodes(children, [], "", lines, filemap_href)
    lines += ["  </div>", "  </div>"]
    return "\n".join(lines) + "\n"


def default_chrome(spec):
    title = spec.get("title") or spec["root"]["name"]
    kind = spec.get("kind") or "product"
    intro = spec.get("intro")
    if not intro:
        if kind == "method-package":
            intro = (
                "人看母版資料夾怎麼疊。不是腳本盤點。腳本盤點在 "
                '<a href="guide-dev-flow.html#filemap">guide-dev-flow 附錄 #filemap</a>。'
            )
        else:
            intro = "人看這個 repo 資料夾怎麼疊、每一列幹嘛。不是腳本盤點。"
    nav = spec.get("nav")
    if nav is None:
        nav = [{"href": "#tree", "label": "目錄樹"}]
        if kind == "method-package":
            nav.append(
                {"href": "guide-dev-flow.html#filemap", "label": "腳本盤點 #filemap"}
            )
    h2 = spec.get("h2") or "目錄樹"
    lead = spec.get("lead") or (
        "預設只看到第一層。摺疊時仍是一棵樹。"
        "藍色資料夾名可點，點開才接子層；子層一樣用 "
        "<code>├─</code> <code>│</code> <code>└─</code>。"
    )
    after = spec.get("after")
    if after is None:
        if kind == "method-package":
            after = (
                "三邊薄殼都指同一棵 <code>skills/</code>。脚本職責見 "
                '<a href="guide-dev-flow.html#filemap">#filemap</a>。'
            )
        else:
            after = "本頁是目錄包含關係，不是 hop 流程、也不是脚本盤點。"
    footer = spec.get("footer")
    if footer is None:
        if kind == "method-package":
            footer = (
                "正本規則:<code>README.md</code>；技能樹:<code>skills/</code>。"
                "本頁是目錄包含關係，不是 hop 流程、也不是脚本盤點。脚本盤點在 "
                '<a href="guide-dev-flow.html#filemap">guide-dev-flow 附錄 #filemap</a>。'
                "視覺語言沿用 <code>guide-dev-talk.html</code> 的共用 token。"
                "疑義以 README 為準。"
            )
        else:
            footer = (
                "畫法:<code>notes/design/dir-tree-contract.md</code>；"
                "產器:<code>scripts/build-dir-tree.py</code>。"
                "有需要才畫，不是每案必跑。"
            )
    return title, intro, nav, h2, lead, after, footer


OPEN_ANCESTOR_JS = """\
<script>
/* 巢狀 details：點頁內錨點時先打開祖先 details */
document.addEventListener('click', function(e) {
  var a = e.target.closest('a[href^="#"]');
  if (!a) return;
  var href = a.getAttribute('href');
  if (href.length <= 1) return;
  var el = document.getElementById(decodeURIComponent(href.slice(1)));
  if (!el) return;
  var node = el;
  while (node) {
    if (node.tagName === 'DETAILS') node.open = true;
    node = node.parentElement;
  }
});
</script>
"""


def render_page(spec, filemap_href="guide-dev-flow.html#filemap"):
    title, intro, nav, h2, lead, after, footer = default_chrome(spec)
    nav_html = "\n".join(
        '    <a href="%s">%s</a>' % (esc(item["href"]), esc(item["label"]))
        for item in nav
    )
    tree = render_tree(spec, filemap_href)
    return "".join([
        "<!DOCTYPE html>\n",
        '<html lang="zh-TW">\n',
        "<head>\n",
        '<meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n',
        "<title>%s</title>\n" % esc(title),
        "<style>\n",
        CSS,
        "</style>\n",
        "</head>\n",
        "<body>\n",
        "<main>\n",
        "  <h1>%s</h1>\n" % esc(title),
        '  <p class="muted">%s</p>\n' % intro,
        "\n",
        "  <nav>\n",
        nav_html,
        "\n  </nav>\n",
        "\n",
        '  <h2 id="tree">%s</h2>\n' % esc(h2),
        '  <p class="lead">%s</p>\n' % lead,
        "\n",
        tree,
        '  <p class="muted">%s</p>\n' % after,
        "\n",
        '  <footer class="foot">\n',
        "    %s\n" % footer,
        "  </footer>\n",
        "</main>\n",
        OPEN_ANCESTOR_JS,
        SCROLL_BLOCK,
        "\n",
        "</body>\n",
        "</html>\n",
    ])


def judge_html(text, label):
    issues = []
    low = text.lower()
    if "```mermaid" in low or "mermaid.js" in low or 'class="mermaid"' in low:
        issues.append("吐 mermaid")
    if "<pre" in low:
        issues.append("吐 <pre>")
    if "<svg" in low:
        issues.append("吐 svg")
    if "<details open" in low:
        issues.append("預設展開")
    if 'class="tline"' not in text and "class='tline'" not in text:
        issues.append("沒有 .tline")
    if "├─" not in text or "└─" not in text:
        issues.append("沒有樹線")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


def prepare(spec, root):
    root_node = spec.get("root")
    if not isinstance(root_node, dict):
        die(1, "用途表要有 root")
    spec = dict(spec)
    spec["root"] = expand_ellipsis(root_node)
    children = spec["root"].get("children") or []
    for child in children:
        validate_child(child, root, "")
    return spec


def emit(spec, root, fragment, filemap_href=None):
    spec = prepare(spec, root)
    if filemap_href is None:
        filemap_href = "#filemap" if fragment else "guide-dev-flow.html#filemap"
    html_out = (
        render_tree(spec, filemap_href) if fragment
        else render_page(spec, filemap_href)
    )
    ok, detail = judge_html(html_out, "產出")
    if not ok:
        die(1, detail)
    return html_out


def extract_tree(page):
    start = page.find(TREE_BEGIN)
    end = page.find(TREE_END)
    if start < 0 or end < 0 or end < start:
        die(1, "guide-dev-flow.html 缺 <!-- dir-tree:begin/end --> 標記")
    return page[start + len(TREE_BEGIN):end].lstrip("\n")


def splice_tree(page, fragment):
    start = page.find(TREE_BEGIN)
    end = page.find(TREE_END)
    if start < 0 or end < 0 or end < start:
        die(1, "guide-dev-flow.html 缺 <!-- dir-tree:begin/end --> 標記")
    return page[:start + len(TREE_BEGIN)] + "\n" + fragment + page[end:]


def write_text(path, text):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(text, encoding="utf-8")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        usage()
        sys.exit(2)

    purpose = None
    root = None
    out = None
    fragment = False
    mode = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--write":
            mode = "write"
            i += 1
        elif arg == "--check":
            mode = "check"
            i += 1
        elif arg == "--fragment":
            fragment = True
            i += 1
        elif arg == "--walk":
            die(2, "拒絕:不准掃 repo 猜 why,用途表手寫")
        elif arg == "--purpose":
            if i + 1 >= len(argv):
                die(2, "--purpose 需要一個值")
            purpose = argv[i + 1]
            i += 2
        elif arg == "--root":
            if i + 1 >= len(argv):
                die(2, "--root 需要一個值")
            root = argv[i + 1]
            i += 2
        elif arg == "--out":
            if i + 1 >= len(argv):
                die(2, "--out 需要一個值")
            out = argv[i + 1]
            i += 2
        elif arg == "--fixture":
            if i + 1 >= len(argv):
                die(2, "--fixture 需要一個值")
            name = argv[i + 1]
            purpose = str(FIX_DIR / name / "purpose.yaml")
            repo = FIX_DIR / name / "repo"
            if repo.is_dir():
                root = str(repo)
            i += 2
        else:
            die(2, "拒絕:未知參數 %s" % arg)

    if mode in ("write", "check"):
        purpose = purpose or str(PURPOSE_PATH)
        root = root or str(ROOT)
        fragment_html = emit(load_yaml(purpose), root, True, "#filemap")
        try:
            current = GUIDE_PATH.read_text(encoding="utf-8")
        except OSError as err:
            die(2, "讀不到 %s:%s" % (GUIDE_PATH, err))
        if mode == "check":
            if extract_tree(current) != fragment_html:
                die(1, "guide-dev-flow.html #dirmap 跟產器產出不一致,"
                    "請跑 scripts/build-dir-tree.py --write")
            print("ok:guide-dev-flow.html #dirmap 對得上產器", file=sys.stderr)
            return
        write_text(GUIDE_PATH, splice_tree(current, fragment_html))
        print("wrote %s #dirmap" % GUIDE_PATH, file=sys.stderr)
        return

    if not purpose:
        die(2, "要 --purpose(或 --write／--check／--fixture)")
    page = emit(load_yaml(purpose), root, fragment)
    if out in (None, "-"):
        sys.stdout.write(page)
        return
    write_text(out, page)
    print("wrote %s" % out, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
