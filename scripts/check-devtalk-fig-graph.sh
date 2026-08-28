#!/bin/bash
# check-devtalk-fig-graph.sh — 方法流程圖對 graph.yaml hop 鏈 + 掃頁樣張六件
#
# 為什麼需要:改 hop / 改規則時,「在講這技能怎麼走」的圖／表若沒跟上,會默默
# 不匹配。既有 check-devtalk-graph.sh 管節點檔與 next;check-devtalk-guide-sync.sh
# 管原文與步數;check-guides-fig-sync.sh 管 fig-lifecycle 雙副本 —— 都不管
# 「圖上的 hop id 集合是不是 graph.yaml 那一串」。本檔把那顆牙補上。
#
# 正本:skills/dev-talk/graph.yaml,從 entry 沿 next 走到空,那一串 hop id 就是流程。
#
# 必須對帳(只這些,「在講這技能怎麼走」):
#   - guides/guide-dev-talk.html #fig-map(svg)、#map-hops(表)、#map-chain(節點鏈 pre)
#   - 若 SKILL.md 或 html-shell.html 出現 <svg>(方法流程圖),一併納入
# 不准對帳(對了反而錯):
#   - 各 feature 的 1-discussion.html「現在怎麼走」(使用者世界,不是 skill hop)
#   - fig-lifecycle / fig-lifecycle-qs(Claude Code 生命週期)
#   - 站 2–7、gate twin、README 五格
#
# 對帳規則(fail-closed):
#   - 每個納入的圖／表,hop id 集合 = graph 鏈集合。少一個或多一個都 FAIL(exit 1)
#   - 順序必須跟 next 鏈一致(表:資料列序;svg:主幹 <text> 由上而下=文件序)
#   - 抽不到圖、html id 不唯一、或解析到 0 個 hop → exit 2(NOT-PARSED)
#
# 掃頁樣張(同檔第二節,免得漏掛):
#   scripts/fixtures/devtalk-html-scan/good/1-discussion.html
#   必須有:摘要卡(.sum)、直式 svg 或 pre、人表、題表、驗收表、details 問答(預設摺著)
#   現況圖必須有限寬且欄內置中(width:220px + .figwrap justify-content:center)
#
# 掃頁產生器(同檔第三節):
#   scripts/build-scan-html.py --action 從同目錄 1-discussion.md 產出六件套。
#   生成頁必須過同一套六件／置中契約;缺一件或現況圖貼左／撐滿欄必須紅。
#   現況圖必須長手樣三框:每框四行(誰／做什麼／工具／痛點,痛不准空)、
#   框 x=20 width=160 height=88、字 text-anchor="middle" x=100、
#   三步時 viewBox="0 0 200 420",不裁字、不把四行堆疊拆成很多小格、
#   框高≠88／每框 text<4／痛空 必須紅。
#   不准攤成 twin 卡,不加 g1-ask／「你要審什麼」／勾選講義。
#
# 破壞實驗(本檔每次跑,除非 --skip-mutation):
#   複本刪掉圖上一個 hop → 必須紅;graph.yaml 多一個 hop 不改圖 → 必須紅;
#   樣張拿掉 details → 必須紅;樣張圖改回撐滿欄 → 必須紅;好樣本必須綠;
#   生成頁拿掉人表 → 必須紅;生成頁圖改撐滿欄必須紅;
#   框高改 28／每框少一行／痛空／堆疊拆很多小格 → 必須紅。
#
# 用法:
#   scripts/check-devtalk-fig-graph.sh [root]
#   scripts/check-devtalk-fig-graph.sh --skip-mutation [root]
# exit:0 = 全過 / 1 = 真漂移 / 2 = NOT-PARSED
#
# 不改 check-devtalk-graph.sh / check-devtalk-guide-sync.sh / check-guides-fig-sync.sh。

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
SKIP_MUTATION=0
if [ "${1:-}" = "--skip-mutation" ]; then
  SKIP_MUTATION=1
  shift
fi
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" "$SELF/check-devtalk-fig-graph.sh" "$SKIP_MUTATION" <<'PY'
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]
self_script = sys.argv[2]
skip_mutation = sys.argv[3] == "1"

HOP_RE = re.compile(r"(?:N|S)\d+-[A-Za-z0-9-]+")
GRAPH = os.path.join(root, "skills", "dev-talk", "graph.yaml")
GUIDE = os.path.join(root, "guides", "guide-dev-talk.html")
SKILL = os.path.join(root, "skills", "dev-talk", "SKILL.md")
SHELL = os.path.join(root, "skills", "dev-talk", "html-shell.html")
FIXTURE = os.path.join(
    root, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.html"
)
FIXTURE_MD = os.path.join(
    root, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.md"
)
BUILD = os.path.join(root, "scripts", "build-scan-html.py")
REQUIRED_FIG_IDS = ("fig-map", "map-hops", "map-chain")
FORBIDDEN_FIG_IDS = ("fig-lifecycle", "fig-lifecycle-qs")


class NotParsed(Exception):
    pass


class Mismatch(Exception):
    pass


def graph_chain(path):
    if not os.path.isfile(path):
        raise NotParsed("缺 skills/dev-talk/graph.yaml")
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^entry:\s*(\S+)\s*$", text, re.M)
    if not m:
        raise NotParsed("graph.yaml 找不到 entry")
    entry = m.group(1).strip().strip("'\"")
    next_map = {}
    current = None
    for raw in text.splitlines():
        stripped = raw.strip()
        if (not stripped) or stripped.startswith("#"):
            continue
        node_m = re.match(r"^  ([NS]\d+-[A-Za-z0-9-]+):\s*$", raw)
        if node_m:
            current = node_m.group(1)
            continue
        if current is None:
            continue
        next_m = re.match(r"^    next:\s*(.*)$", raw)
        if not next_m:
            continue
        val = next_m.group(1).strip().strip("'\"")
        if val in ("", "null", "~"):
            val = ""
        next_map[current] = val
    if entry not in next_map:
        raise NotParsed("graph.yaml entry 不在 nodes 或沒有 next")
    chain = []
    cur = entry
    seen = set()
    while cur:
        if cur in seen:
            raise NotParsed("graph.yaml next 鏈成環")
        if cur not in next_map:
            raise NotParsed("graph.yaml 節點 %s 沒有 next" % cur)
        chain.append(cur)
        seen.add(cur)
        cur = next_map[cur]
    if not chain:
        raise NotParsed("graph.yaml next 鏈是空的")
    return chain


def count_id(text, html_id):
    return text.count('id="%s"' % html_id)


def extract_svg(text, svg_id):
    marker = '<svg id="%s"' % svg_id
    n = text.count(marker)
    if n != 1:
        raise NotParsed('svg id="%s" 在檔內出現 %d 次(需恰為 1)' % (svg_id, n))
    start_re = re.compile(re.escape(marker) + r"[^>]*>")
    start_m = start_re.search(text)
    if not start_m:
        raise NotParsed('找不到 <svg id="%s" ...>' % svg_id)
    token_re = re.compile(r"<svg\b[^>]*>|</svg>")
    pos = start_m.end()
    depth = 1
    max_depth = 1
    while depth > 0:
        m = token_re.search(text, pos)
        if not m:
            raise NotParsed('<svg id="%s"> 找不到收尾 </svg>' % svg_id)
        if m.group(0) == "</svg>":
            depth -= 1
        else:
            depth += 1
            max_depth = max(max_depth, depth)
        pos = m.end()
    if max_depth > 1:
        raise NotParsed('<svg id="%s"> 有巢狀 svg,fail-closed' % svg_id)
    return text[start_m.start():pos]


def extract_table(text, table_id):
    marker = '<table id="%s"' % table_id
    n = text.count(marker)
    if n != 1:
        raise NotParsed('table id="%s" 在檔內出現 %d 次(需恰為 1)' % (table_id, n))
    start = text.find(marker)
    end = text.find("</table>", start)
    if end < 0:
        raise NotParsed('table id="%s" 找不到 </table>' % table_id)
    return text[start:end + len("</table>")]


def hops_from_svg(block):
    ordered = []
    seen = set()
    for inner in re.findall(r"<text\b[^>]*>(.*?)</text>", block, re.S):
        plain = html.unescape(re.sub(r"<[^>]+>", "", inner))
        for hop in HOP_RE.findall(plain):
            if hop in seen:
                raise NotParsed("svg 主幹 hop id 重複:%s" % hop)
            seen.add(hop)
            ordered.append(hop)
    if not ordered:
        raise NotParsed("svg 解析到 0 個 hop")
    return ordered


def hops_from_table(block):
    ordered = []
    seen = set()
    for row in re.findall(r"<tr>(.*?)</tr>", block, re.S):
        if "<th>" in row:
            continue
        first = re.search(r"<td>(.*?)</td>", row, re.S)
        if not first:
            continue
        plain = html.unescape(re.sub(r"<[^>]+>", "", first.group(1)))
        found = HOP_RE.findall(plain)
        if not found:
            continue
        if len(found) != 1:
            raise NotParsed("表列第一格 hop id 不唯一:%s" % found)
        hop = found[0]
        if hop in seen:
            raise NotParsed("表 hop id 重複:%s" % hop)
        seen.add(hop)
        ordered.append(hop)
    if not ordered:
        raise NotParsed("表解析到 0 個 hop")
    return ordered


def hops_from_pre(block):
    plain = html.unescape(re.sub(r"<[^>]+>", "", block))
    ordered = HOP_RE.findall(plain)
    if not ordered:
        raise NotParsed("pre 解析到 0 個 hop")
    if len(ordered) != len(set(ordered)):
        raise NotParsed("pre hop id 不唯一:%s" % ordered)
    return ordered


def extract_pre(text, pre_id):
    marker = '<pre id="%s"' % pre_id
    n = text.count(marker)
    if n != 1:
        raise NotParsed('pre id="%s" 在檔內出現 %d 次(需恰為 1)' % (pre_id, n))
    start = text.find(marker)
    end = text.find("</pre>", start)
    if end < 0:
        raise NotParsed('pre id="%s" 找不到 </pre>' % pre_id)
    return text[start:end + len("</pre>")]


def optional_svg_hops(path, label):
    if not os.path.isfile(path):
        return None
    text = open(path, encoding="utf-8").read()
    if "<svg" not in text:
        return None
    ids = re.findall(r'<svg id="([^"]+)"', text)
    if not ids:
        raise NotParsed("%s 有 <svg> 但沒有穩定 id" % label)
    if len(ids) != len(set(ids)):
        raise NotParsed("%s svg id 不唯一:%s" % (label, ids))
    out = []
    for svg_id in ids:
        if svg_id in FORBIDDEN_FIG_IDS:
            raise NotParsed("%s 不該拿 %s 當方法流程圖" % (label, svg_id))
        out.append((label + "#" + svg_id, hops_from_svg(extract_svg(text, svg_id))))
    return out


def account_figures(chain):
    figures = []
    if not os.path.isfile(GUIDE):
        raise NotParsed("缺 guides/guide-dev-talk.html")
    guide = open(GUIDE, encoding="utf-8").read()
    for forbidden in FORBIDDEN_FIG_IDS:
        if count_id(guide, forbidden):
            raise NotParsed(
                "guide-dev-talk 出現 %s —— 那是生命週期圖,不准拿來對 hop" % forbidden
            )
    figures.append(("guide#fig-map", hops_from_svg(extract_svg(guide, "fig-map"))))
    figures.append(("guide#map-hops", hops_from_table(extract_table(guide, "map-hops"))))
    figures.append(("guide#map-chain", hops_from_pre(extract_pre(guide, "map-chain"))))
    for path, label in ((SKILL, "SKILL.md"), (SHELL, "html-shell.html")):
        extra = optional_svg_hops(path, label)
        if extra:
            figures.extend(extra)
    failures = []
    for name, hops in figures:
        print("[%s] hops=%s" % (name, " → ".join(hops)))
        if set(hops) != set(chain):
            missing = [h for h in chain if h not in hops]
            extra = [h for h in hops if h not in chain]
            failures.append(
                "%s hop 集合 ≠ graph 鏈(少 %s / 多 %s)" % (name, missing, extra)
            )
        if hops != chain:
            failures.append(
                "%s hop 順序 ≠ next 鏈\n    圖:%s\n    鏈:%s"
                % (name, " → ".join(hops), " → ".join(chain))
            )
    if failures:
        raise Mismatch("\n".join(failures))
    return figures


def viewbox_hw(svg):
    m = re.search(r'viewBox="([^"]+)"', svg)
    if not m:
        return None
    parts = m.group(1).split()
    if len(parts) != 4:
        return None
    try:
        return float(parts[2]), float(parts[3])
    except ValueError:
        return None


def inner_text(block):
    return html.unescape(re.sub(r"<[^>]+>", "", block))


def first_block(text, pattern):
    m = re.search(pattern, text, re.S)
    return m.group(0) if m else ""


def scan_fig_center_gaps(text, label):
    """直式現況圖必須有限寬且欄內水平置中。width:100% / max-width:100% 會把
    畫布撐滿、狹長圖貼左 —— 那正是要擋的。"""
    style = first_block(text, r"<style\b[^>]*>.*?</style>")
    compact = re.sub(r"\s+", "", style)
    gaps = []
    if "justify-content:center" not in compact:
        gaps.append("%s 缺 .figwrap justify-content:center" % label)
    if "width:220px" not in compact:
        gaps.append("%s 圖缺有限寬 width:220px" % label)
    if "width:max-content" not in compact:
        gaps.append("%s pre 圖缺 width:max-content" % label)
    if "svg{max-width:100%" in compact:
        gaps.append("%s svg 仍是 max-width:100%(會撐滿欄、圖貼左)" % label)
    return gaps


def diagram_src_lines(md_text):
    """現況圖 fence 裡的內容行(含 ↓ 分隔)。"""
    m = re.search(r"^#{2,3}\s+現況圖\s*$", md_text or "", re.M)
    if not m:
        return []
    rest = md_text[m.end() :]
    nxt = re.search(r"^#{2,3}\s+", rest, re.M)
    body = rest[: nxt.start()] if nxt else rest
    fences = re.findall(r"```[^\n]*\n(.*?)```", body, re.S)
    blob = "\n".join(fences).strip() if fences else body
    lines = []
    for raw in blob.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[-+|\\/\s]+", line):
            continue
        lines.append(line)
    return lines


def expected_frame_count(lines):
    """獨立數框:全是箭頭行 → 一行一框;否則四行堆疊一框。不准跟產生器同一套拆法。"""
    content = [
        ln for ln in lines if not re.fullmatch(r"(?:--+>|→|->|↓|▼)+", ln)
    ]
    if not content:
        return 0
    arrowish = [ln for ln in content if re.search(r"→|->|--[^>\n]+-->", ln)]
    if arrowish and len(arrowish) == len(content):
        return len(content)
    if len(content) % 4 == 0:
        return len(content) // 4
    if arrowish:
        return len(arrowish)
    return len(content)


def scan_now_svg(text):
    m = re.search(
        r'<svg\b[^>]*\bid="scan-now"[^>]*>.*?</svg>', text or "", re.S
    )
    if m:
        return m.group(0)
    m = re.search(r'<svg\b[^>]*id="scan-now"[^>]*>.*?</svg>', text or "", re.S)
    return m.group(0) if m else ""


def check_scan_now_shape(text, label, md_text):
    """咬手樣三框:88 高、每框四行、痛不准空、堆疊 md 不准拆很多小格。"""
    svg = scan_now_svg(text)
    if not svg:
        raise Mismatch("%s 缺 svg#scan-now" % label)
    hw = viewbox_hw(svg)
    if not hw:
        raise Mismatch("%s #scan-now 沒有 viewBox" % label)
    width, height = hw
    gaps = []
    if width != 200:
        gaps.append(
            "%s viewBox 寬是 %s,手樣是 200(舊產生器是 160)" % (label, int(width))
        )
    src_lines = diagram_src_lines(md_text)
    want = expected_frame_count(src_lines)
    rects = re.findall(r"<rect\b[^>]*>", svg)
    if want and len(rects) != want:
        gaps.append(
            "%s 現況圖應 %d 框卻畫了 %d 格(堆疊四行不准拆小格)"
            % (label, want, len(rects))
        )
    if want == 3:
        if 'viewBox="0 0 200 420"' not in svg:
            gaps.append(
                '%s 三步必須 viewBox="0 0 200 420",實得 %s'
                % (label, re.search(r'viewBox="[^"]+"', svg).group(0) if re.search(r'viewBox="[^"]+"', svg) else "無")
            )
        if height >= 700:
            gaps.append("%s viewBox 高 %s,舊產生器那種 780 不准回來" % (label, int(height)))
    for i, rect in enumerate(rects, 1):
        hm = re.search(r'\bheight="(\d+)"', rect)
        xm = re.search(r'\bx="(\d+)"', rect)
        wm = re.search(r'\bwidth="(\d+)"', rect)
        if not hm or hm.group(1) != "88":
            gaps.append(
                "%s 第 %d 框高是 %s,手樣是 88"
                % (label, i, hm.group(1) if hm else "無")
            )
        if not xm or xm.group(1) != "20":
            gaps.append(
                "%s 第 %d 框 x 是 %s,手樣是 20"
                % (label, i, xm.group(1) if xm else "無")
            )
        if not wm or wm.group(1) != "160":
            gaps.append(
                "%s 第 %d 框寬是 %s,手樣是 160"
                % (label, i, wm.group(1) if wm else "無")
            )
    body = re.sub(
        r'<text\b[^>]*>痛在最後一步</text>', "", svg
    )
    texts = re.findall(r"<text\b[^>]*>.*?</text>", body)
    if rects and len(texts) != 4 * len(rects):
        gaps.append(
            "%s 每框要四行 text(誰／做什麼／工具／痛),實得 %d 框 %d 行"
            % (label, len(rects), len(texts))
        )
    else:
        for i in range(len(rects)):
            group = texts[i * 4 : (i + 1) * 4]
            if len(group) < 4:
                gaps.append("%s 第 %d 框 text 少於 4" % (label, i + 1))
                continue
            for j, node in enumerate(group, 1):
                if 'text-anchor="middle"' not in node:
                    gaps.append(
                        "%s 第 %d 框第 %d 行缺 text-anchor=\"middle\""
                        % (label, i + 1, j)
                    )
                if not re.search(r'\bx="100"', node):
                    gaps.append(
                        "%s 第 %d 框第 %d 行 x 不是 100" % (label, i + 1, j)
                    )
            pain_inner = inner_text(group[3]).strip()
            if not pain_inner:
                gaps.append("%s 第 %d 框痛是空的" % (label, i + 1))
    if "痛在最後一步" not in inner_text(svg):
        gaps.append("%s 圖下缺小字「痛在最後一步」" % label)
    rect_classes = re.findall(r'<rect class="([^"]+)"', svg)
    if rect_classes and rect_classes[-1] != "no":
        gaps.append("%s 最後一框要用痛的強調色 class=\"no\"" % label)
    if len(rect_classes) >= 3 and rect_classes[1] != "b":
        gaps.append("%s 中框要用 class=\"b\"" % label)
    if len(rects) >= 2 and not re.search(r'<path\b[^>]*class="flow"', svg):
        gaps.append("%s 框間缺 .flow" % label)
    long_needles = ("建補助案、填申請日", "新增附表五、選 A–F", "口頭對 OPU／FBT")
    for needle in long_needles:
        if needle in (md_text or "") and needle not in svg:
            gaps.append("%s 裁字了,手樣要完整「%s」" % (label, needle))
    pain_needles = ("PLUS 還不會自動切", "看不到 2PN", "完整額只能猜")
    for needle in pain_needles:
        if needle in (md_text or "") and needle not in svg:
            gaps.append("%s 缺痛「%s」" % (label, needle))
    if "痛在這" in inner_text(svg) and "痛在最後一步" not in inner_text(svg):
        gaps.append("%s 還在寫舊caption「痛在這」" % label)
    if gaps:
        raise Mismatch("%s現況圖形狀:" % label + "、".join(gaps))


def check_scan_page(text, label):
    missing = []
    sum_block = first_block(
        text, r'<section[^>]*class="[^"]*\bsum\b[^"]*"[^>]*>.*?</section>'
    )
    if not sum_block:
        sum_block = first_block(
            text, r'<div[^>]*class="[^"]*\bsum\b[^"]*"[^>]*>.*?</div>'
        )
    if not sum_block:
        missing.append("摘要卡(.sum)")
    else:
        blob = inner_text(sum_block)
        for token in ("已解", "假設", "移交"):
            if token not in blob:
                missing.append("摘要卡缺 OQ 三態「%s」" % token)
        if len(re.findall(r'class="badge', sum_block)) < 3:
            missing.append("摘要卡 OQ 三態 badge 少於 3")
    svgs = re.findall(r"<svg\b.*?</svg>", text, re.S)
    vertical = False
    for block in svgs:
        hw = viewbox_hw(block)
        if hw and hw[1] > hw[0]:
            vertical = True
            break
    nonempty_pre = False
    for m in re.finditer(r"<pre\b[^>]*>(.*?)</pre>", text, re.S):
        if inner_text(m.group(1)).strip():
            nonempty_pre = True
            break
    if not vertical and not nonempty_pre:
        missing.append("直式 svg 或非空 pre")
    if svgs:
        blob = "".join(svgs)
        if not re.search(r'class="(?:[^"]*\s)?(?:b|hl|no)(?:\s[^"]*)?"', blob):
            missing.append("svg 缺 .b/.hl/.no")
        if not re.search(r'class="(?:[^"]*\s)?(?:flow|cap)(?:\s[^"]*)?"', blob):
            missing.append("svg 缺 .flow/.cap")
    people = first_block(text, r'<table[^>]*id="scan-people"[^>]*>.*?</table>')
    if not people:
        missing.append("人表(#scan-people)")
    else:
        blob = inner_text(people)
        for token in ("誰", "要什麼", "缺什麼"):
            if token not in blob:
                missing.append("人表缺欄「%s」" % token)
        if "[Assumption]" not in people:
            missing.append("人表 [Assumption] 看不見")
    qs = first_block(text, r'<table[^>]*id="scan-qs"[^>]*>.*?</table>')
    if not qs:
        missing.append("題表(#scan-qs)")
    elif "著落" not in inner_text(qs):
        missing.append("題表缺著落欄")
    ac = first_block(text, r'<table[^>]*id="scan-ac"[^>]*>.*?</table>')
    if not ac:
        missing.append("驗收表(#scan-ac)")
    else:
        blob = inner_text(ac)
        for token in ("假設", "從哪看", "看到什麼"):
            if token not in blob:
                missing.append("驗收表缺「%s」" % token)
    details = re.findall(r"<details\b([^>]*)>(.*?)</details>", text, re.S)
    if not details:
        missing.append("details 問答")
    else:
        for attrs, body in details:
            if re.search(r"(^|\s)open(\s|=|>|$)", attrs):
                missing.append("問答 details 必須預設摺著(不准 open)")
                break
            if "問答" not in inner_text(body):
                missing.append("details 不是問答摘要")
                break
    if "mermaid" in text.lower():
        missing.append("%s禁 mermaid" % label)
    if re.search(r'<img[^>]+src="https?://', text):
        missing.append("%s禁外連圖" % label)
    if "--acc" not in text:
        missing.append("%s顏色缺 --acc" % label)
    if "g1-ask" in text or "你要審什麼" in text:
        missing.append("%s不准出現 g1-ask／你要審什麼" % label)
    if re.search(r'class="(?:r-block|s-card)"', text):
        missing.append("%s不准攤成 twin 卡" % label)
    if 'type="checkbox"' in text.lower():
        missing.append("%s不准出現審查勾選" % label)
    order = [
        ("摘要卡", text.find('class="sum"')),
        ("現況圖", text.find('id="scan-now"') if 'id="scan-now"' in text else text.find("<pre")),
        ("人表", text.find('id="scan-people"')),
        ("題表", text.find('id="scan-qs"')),
        ("驗收表", text.find('id="scan-ac"')),
        ("問答", text.find("<details")),
    ]
    prev_name, prev_pos = None, -1
    for name, pos in order:
        if pos < 0:
            continue
        if pos < prev_pos:
            missing.append("掃頁順序錯:%s 在 %s 前面" % (name, prev_name))
            break
        prev_name, prev_pos = name, pos
    missing.extend(scan_fig_center_gaps(text, label))
    if not re.search(
        r'<div class="figwrap">\s*<svg\b[^>]*\bid="scan-now"', text, re.S
    ) and not re.search(
        r'<div class="figwrap">\s*<pre\b[^>]*\bid="scan-now"', text, re.S
    ):
        missing.append("%s #scan-now 沒包 .figwrap" % label)
    # 去重但保序
    seen = set()
    uniq = []
    for item in missing:
        if item in seen:
            continue
        seen.add(item)
        uniq.append(item)
    if uniq:
        raise Mismatch("%s缺件:" % label + "、".join(uniq))


def check_fixture():
    if not os.path.isfile(FIXTURE):
        raise NotParsed("缺掃頁樣張 scripts/fixtures/devtalk-html-scan/good/1-discussion.html")
    if not os.path.isfile(FIXTURE_MD):
        raise NotParsed(
            "缺掃頁樣張 md scripts/fixtures/devtalk-html-scan/good/1-discussion.md"
        )
    html_text = open(FIXTURE, encoding="utf-8").read()
    md_text = open(FIXTURE_MD, encoding="utf-8").read()
    check_scan_page(html_text, "掃頁樣張")
    check_scan_now_shape(html_text, "掃頁樣張", md_text)
    print("[scan] fixture 六件齊,問答摺著")
    print("[scan] fixture 現況圖有限寬且欄內置中")
    print("[scan] fixture 現況圖三框手樣形狀")


def generate_scan(md_path, out_path):
    if not os.path.isfile(BUILD):
        raise NotParsed("缺 scripts/build-scan-html.py")
    proc = subprocess.run(
        [sys.executable, BUILD, "--action", md_path, "--out", out_path],
        capture_output=True,
        text=True,
    )
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        raise Mismatch(
            "產生器對樣張 md 必須綠,實際 rc=%s\n%s" % (proc.returncode, blob[-1200:])
        )
    if not os.path.isfile(out_path):
        raise Mismatch("產生器沒寫出 %s" % out_path)
    return open(out_path, encoding="utf-8").read()


def check_generated():
    if not os.path.isfile(FIXTURE_MD):
        raise NotParsed(
            "缺掃頁樣張 md scripts/fixtures/devtalk-html-scan/good/1-discussion.md"
        )
    fd, out = tempfile.mkstemp(suffix=".html", prefix="scan-gen-")
    os.close(fd)
    try:
        text = generate_scan(FIXTURE_MD, out)
        check_scan_page(text, "生成頁")
        check_scan_now_shape(
            text, "生成頁", open(FIXTURE_MD, encoding="utf-8").read()
        )
        print("[scan] 生成頁現況圖三框手樣形狀")
    finally:
        try:
            os.remove(out)
        except OSError:
            pass
    print("[scan] 從 md 生成的掃頁六件齊,現況圖有限寬且欄內置中")


def check_live():
    chain = graph_chain(GRAPH)
    print("[graph] chain=" + " → ".join(chain))
    if len(chain) < 2:
        raise NotParsed("graph.yaml hop 鏈短於 2,解析不可信")
    account_figures(chain)
    check_fixture()
    if not os.path.isfile(SHELL):
        raise NotParsed("缺 skills/dev-talk/html-shell.html")
    shell_gaps = scan_fig_center_gaps(
        open(SHELL, encoding="utf-8").read(), "html-shell"
    )
    if shell_gaps:
        raise Mismatch("掃頁母版圖未置中:" + "、".join(shell_gaps))
    print("[scan] html-shell 現況圖有限寬且欄內置中")
    check_generated()


def copy_tree(dst):
    mapping = [
        (GRAPH, os.path.join(dst, "skills", "dev-talk", "graph.yaml")),
        (SKILL, os.path.join(dst, "skills", "dev-talk", "SKILL.md")),
        (SHELL, os.path.join(dst, "skills", "dev-talk", "html-shell.html")),
        (GUIDE, os.path.join(dst, "guides", "guide-dev-talk.html")),
        (FIXTURE, os.path.join(
            dst, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.html"
        )),
        (FIXTURE_MD, os.path.join(
            dst, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.md"
        )),
        (BUILD, os.path.join(dst, "scripts", "build-scan-html.py")),
    ]
    for src, dest in mapping:
        if not os.path.isfile(src):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy(src, dest)


def child_rc(tree):
    proc = subprocess.run(
        ["bash", self_script, "--skip-mutation", tree],
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout or "") + "\n" + (proc.stderr or "")


def run_mutations():
    failures = []

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-good-") as tmp:
        copy_tree(tmp)
        rc, blob = child_rc(tmp)
        if rc == 0:
            print("[mut] ✓ 好樣本複本綠")
        else:
            failures.append("好樣本複本必須綠,實際 rc=%s\n%s" % (rc, blob[-1200:]))

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-delhop-") as tmp:
        copy_tree(tmp)
        guide = os.path.join(tmp, "guides", "guide-dev-talk.html")
        text = open(guide, encoding="utf-8").read()
        start = text.find('<svg id="fig-map"')
        end = text.find("</svg>", start) if start >= 0 else -1
        if start < 0 or end < 0 or "S5-diverge" not in text[start:end]:
            failures.append("破壞實驗 #fig-map 找不到 S5-diverge 可刪")
        else:
            block = text[start:end].replace("S5-diverge", "", 1)
            open(guide, "w", encoding="utf-8").write(text[:start] + block + text[end:])
            rc, blob = child_rc(tmp)
            if rc == 1:
                print("[mut] ✓ 圖上刪一個 hop 必須紅")
            else:
                failures.append(
                    "圖上刪一個 hop 必須 exit 1,實際 rc=%s\n%s" % (rc, blob[-1200:])
                )

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-addhop-") as tmp:
        copy_tree(tmp)
        gpath = os.path.join(tmp, "skills", "dev-talk", "graph.yaml")
        text = open(gpath, encoding="utf-8").read()
        old = "    next: N13-end"
        new = (
            "    next: S99-extra\n"
            "  S99-extra:\n"
            "    file: nodes/S99-extra.md\n"
            "    next: N13-end"
        )
        if text.count(old) < 1:
            failures.append("破壞實驗找不到 S10 next: N13-end")
        else:
            open(gpath, "w", encoding="utf-8").write(text.replace(old, new, 1))
            rc, blob = child_rc(tmp)
            if rc == 1:
                print("[mut] ✓ graph 多一個 hop 不改圖必須紅")
            else:
                failures.append(
                    "graph 多一個 hop 必須 exit 1,實際 rc=%s\n%s" % (rc, blob[-1200:])
                )

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-nodetails-") as tmp:
        copy_tree(tmp)
        fpath = os.path.join(
            tmp, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.html"
        )
        text = open(fpath, encoding="utf-8").read()
        text = re.sub(r"<details\b.*?</details>", "", text, count=1, flags=re.S)
        open(fpath, "w", encoding="utf-8").write(text)
        rc, blob = child_rc(tmp)
        if rc == 1:
            print("[mut] ✓ 樣張拿掉 details 必須紅")
        else:
            failures.append(
                "樣張拿掉 details 必須 exit 1,實際 rc=%s\n%s" % (rc, blob[-1200:])
            )

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-noassume-") as tmp:
        copy_tree(tmp)
        fpath = os.path.join(
            tmp, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.html"
        )
        text = open(fpath, encoding="utf-8").read()
        if "[Assumption]" not in text:
            failures.append("破壞實驗樣張找不到 [Assumption]")
        else:
            open(fpath, "w", encoding="utf-8").write(text.replace("[Assumption]", "", 1))
            rc, blob = child_rc(tmp)
            if rc == 1:
                print("[mut] ✓ 樣張拿掉 [Assumption] 必須紅")
            else:
                failures.append(
                    "樣張拿掉 [Assumption] 必須 exit 1,實際 rc=%s\n%s" % (rc, blob[-1200:])
                )

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-stretch-") as tmp:
        copy_tree(tmp)
        fpath = os.path.join(
            tmp, "scripts", "fixtures", "devtalk-html-scan", "good", "1-discussion.html"
        )
        text = open(fpath, encoding="utf-8").read()
        if "width:220px" not in text:
            failures.append("破壞實驗樣張找不到 width:220px")
        else:
            open(fpath, "w", encoding="utf-8").write(
                text.replace("width:220px", "width:100%", 1)
            )
            rc, blob = child_rc(tmp)
            if rc == 1:
                print("[mut] ✓ 樣張圖改回撐滿欄必須紅")
            else:
                failures.append(
                    "樣張圖改回撐滿欄必須 exit 1,實際 rc=%s\n%s" % (rc, blob[-1200:])
                )

    with tempfile.TemporaryDirectory(prefix="devtalk-fig-gen-") as tmp:
        out = os.path.join(tmp, "1-discussion.html")
        try:
            text = generate_scan(FIXTURE_MD, out)
            md_text = open(FIXTURE_MD, encoding="utf-8").read()
            check_scan_page(text, "生成頁")
            check_scan_now_shape(text, "生成頁", md_text)
            print("[mut] ✓ 樣張 md 生成頁綠")
        except (Mismatch, NotParsed) as exc:
            failures.append("樣張 md 生成頁必須綠:%s" % exc)
        else:
            old_shape = text.replace(
                'viewBox="0 0 200 420"', 'viewBox="0 0 160 780"', 1
            )
            try:
                check_scan_now_shape(old_shape, "生成頁", md_text)
                failures.append("生成頁改回 160×780 必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁改回 160×780 必須紅")
            clipped = text.replace("建補助案、填申請日", "建補助案", 1)
            try:
                check_scan_now_shape(clipped, "生成頁", md_text)
                failures.append("生成頁裁掉長標籤必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁裁掉長標籤必須紅")
            short = re.sub(r'\bheight="88"', 'height="28"', text)
            try:
                check_scan_now_shape(short, "生成頁", md_text)
                failures.append("生成頁框高改 28 必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁框高≠88 必須紅")
            few = re.sub(
                r'<text\b[^>]*>行政</text>\s*',
                "",
                text,
                count=1,
            )
            try:
                check_scan_now_shape(few, "生成頁", md_text)
                failures.append("生成頁每框 text<4 必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁每框 text<4 必須紅")
            empty_pain = text.replace("PLUS 還不會自動切", "", 1)
            try:
                check_scan_now_shape(empty_pain, "生成頁", md_text)
                failures.append("生成頁痛空必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁痛空必須紅")
            many = re.sub(r"(<rect\b[^>]*>)", r"\1\1\1\1", text, count=3)
            try:
                check_scan_now_shape(many, "生成頁", md_text)
                failures.append("堆疊 md 拆成很多小格必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 堆疊 md 拆成很多小格必須紅")
            broken = re.sub(
                r'<table[^>]*id="scan-people".*?</table>', "", text, count=1, flags=re.S
            )
            try:
                check_scan_page(broken, "生成頁")
                failures.append("生成頁拿掉人表必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁拿掉人表必須紅")
            stretched = text.replace("width:220px", "width:100%", 1)
            try:
                check_scan_page(stretched, "生成頁")
                failures.append("生成頁圖改撐滿欄必須紅,卻綠了")
            except Mismatch:
                print("[mut] ✓ 生成頁圖改撐滿欄必須紅")

    if failures:
        raise Mismatch("破壞實驗沒咬到:\n" + "\n".join(failures))


try:
    check_live()
except NotParsed as exc:
    print("FATAL: %s(NOT-PARSED)" % exc, file=sys.stderr)
    sys.exit(2)
except Mismatch as exc:
    print("❌ FAIL:%s" % exc, file=sys.stderr)
    sys.exit(1)

if not skip_mutation:
    try:
        run_mutations()
    except Mismatch as exc:
        print("❌ FAIL:%s" % exc, file=sys.stderr)
        sys.exit(1)

print("✅ PASS:方法流程圖 hop 對帳 + 掃頁樣張六件 + 生成頁六件／置中 + 破壞實驗全過")
sys.exit(0)
PY
