#!/bin/bash
# check-devstage-fig-text.sh — 2／3／4／5／7 站「圖對文字」指紋牙
#
# 為什麼需要:那站的關鍵文字改了、那站的圖沒改,會默默錯。既有
# check-devtalk-fig-graph.sh 管 skill hop;check-devtalk-fig-journey.sh 管第 1 站
# Journey;check-guides-fig-sync.sh 管 fig-lifecycle;check-gate-twin.sh 管審查介面
# —— 都不管「表或標題抽出的流程指紋 vs 該站圖節」。本檔是另一顆牙,不准塞進
# hop／Journey／check-guides-fig-sync.sh,也不准拆成 5 支。
#
# 這條線不是 hop 對 graph.yaml,也不是第 1 站 Journey,也不是「請人看 html
# 好不好」。咬的是機器牙。指紋,不要整檔 SHA。第 6 站沒有必產圖槽,本輪不開;
# 不准動 _templates/6-implementation-notes.md,不准發明第 6 站圖。
#
# 主咬:該站「表或標題抽出的流程指紋」vs「md 圖節(第 5 站改咬 html #dag)」。
# 副咬:md 圖與 html 同節指紋。2／4／7 的 gate twin 把 md 圖 dump 進 details,
# 重產後恆同,不准把 md-vs-html 當主牙。3 的 html 不是 gate-twin
# (STAGES 不含 3-prototype)。example 的 html 是 html-shell、零 id,不准拿它當
# 「沒 id」去改產生器。
#
# html 怎麼找圖:咬標題含「方案架構圖／結構圖／行為流程圖／變更架構圖」,
# 不要寫死 sec-…(anchor_id() 跟標題走,加括號就變)。產生器現況僅供對帳:
# 2≈sec-方案架構圖、4≈sec-行為流程圖-R-級、7≈sec-變更架構圖、5=#dag
# (build_dag 寫死)。禁止為統一 #fig-* 改 build-gate-twin.py／html-shell.html。
# #fig-* 只准手寫 fixture fallback。
#
# 不掃 live docs/dev/<slug>。要掃方法包內第二正例
# example/contract-expiry-reminder/(它不是 live slug)。紅了只准:修抽法,或只
# 補該站圖槽讓指紋對上文字。不准改 example 的表／Decision／R／T／Diff 正文。
#
# 抽法(鎖死;oracle = example/contract-expiry-reminder;NFKC、去空白)。
# 抽不到唯一解 → exit 2 NOT-PARSED。某一站抽不到 → 那站 NOT-PARSED,不准
# 把該站從牙拿掉充綠。
#
# 2  2-decision.md + .html
#    方案名:只從 ## Approaches Considered 表第一欄抽。
#    選定案:Approaches − Rejected 必須恰好 1 個;或 Decision 首句
#    「採／選定／採用」對上唯一方案 token。兩者都有就必須一致。
#    圖:## 方案架構圖。選定案必須在圖上標「選定」。Rejected 的案若上圖,
#    不得標選定。禁止只核對 A/B/C 都在圖上。Decision 改選定、圖的「選定」
#    標沒改 → 必須紅。
# 3  3-prototype.md + .html(選配)
#    兩檔都不存在 → 跳過、綠。只抽 Method 裡的 Variant X／具名模組名。
#    圖:## 結構圖,要標選定 variant。抽不到任何具名 variant → NOT-PARSED。
#    不要從 Question 散文亂切詞。
# 4  4-spec.md + .html
#    每個 ### R-n: 的 R-id,加上標題裡 SHALL 後的行為詞(例:R-1 → 顯示、
#    到期卡片;不是只留 R-1)。圖:## 行為流程圖(R 級)。每個 R-id 必須在圖上;
#    該 R 的行為詞至少一個在圖上。圖上多的 R 必須對文字。禁止只咬 R-1 R-2 R-3。
# 5  5-tasks.md + .html
#    只比 md 每個 ## T-n 的 id ＋ Blocked-by 邊集合,對 html #dag 裡的
#    T-n／←(T-n)。模板沒有 md 圖槽。不要比 md 手畫 T-1 --> T-2,那跟 #dag
#    不是同一張。不要對 5 做 md-vs-html 圖指紋。
# 7  7-review.md + .html
#    不要 F-id,不要現象證據 S-id。咬 ## Diff 的檔名 basename ＋公開端點／
#    新表名。圖:## 變更架構圖。圖上多的模組必須對得上 Diff。無 Diff 節 →
#    NOT-PARSED。
#
# 正例:scripts/fixtures/devstage-fig-text/{2,3,4,5,7}/good/
# 破壞實驗(本檔每次跑,除非 --skip-mutation):
#   改 2 的選定標、3 的 variant 名、4 的 SHALL 行為詞、5 的 Blocked-by、
#   7 的 Diff basename／端點,不改圖就紅。好樣本／example 必須綠。
#
# 用法:
#   scripts/check-devstage-fig-text.sh [root]
#   scripts/check-devstage-fig-text.sh --skip-mutation [root]
# exit:0 = 全過 / 1 = 真漂移 / 2 = NOT-PARSED
#
# 不改 check-devtalk-fig-graph.sh / check-devtalk-fig-journey.sh /
# check-guides-fig-sync.sh / check-gate-twin.sh / build-gate-twin.py。

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

python3 - "$ROOT" "$SELF/check-devstage-fig-text.sh" "$SKIP_MUTATION" <<'PY'
import html as htmlmod
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]
self_script = sys.argv[2]
skip_mutation = sys.argv[3] == "1"

FIX_ROOT = os.path.join(root, "scripts", "fixtures", "devstage-fig-text")
EXAMPLE = os.path.join(root, "example", "contract-expiry-reminder")

STAGE_FILES = {
    2: ("2-decision.md", "2-decision.html"),
    3: ("3-prototype.md", "3-prototype.html"),
    4: ("4-spec.md", "4-spec.html"),
    5: ("5-tasks.md", "5-tasks.html"),
    7: ("7-review.md", "7-review.html"),
}
FIG_NEEDLES = {
    2: ("方案架構圖",),
    3: ("結構圖",),
    4: ("行為流程圖",),
    7: ("變更架構圖",),
}
EMPTY_CELLS = {
    "", "—", "-", "–", "−", "無", "无", "n/a", "N/A", "NA", "none", "None",
}
SHALL_STOP = {
    "系統", "該", "且", "的", "在", "中", "與", "由", "僅", "可", "每筆", "未",
    "任何", "一個", "及其", "以及", "或者", "不是", "不得", "可以", "及其",
    "登入者", "可見", "天內", "未續約", "動作", "明確", "合約", "頁",
}
CODE_EXT_RE = re.compile(
    r"\.(?:go|ts|tsx|js|jsx|py|sql|md|html|css|json|yml|yaml|vue)$", re.I
)
TEST_FILE_RE = re.compile(
    r"(?:_test\.|\.test\.|\.spec\.|e2e/|tests?/)", re.I
)
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)
HTML_HEAD_RE = re.compile(
    r"<(h[1-6]|summary)(\s[^>]*)?>(.*?)</\1>", re.S | re.I
)
HTTP_RE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/[^\s<`'\"，,。;；\]\)\|]+)", re.I
)
PATH_RE = re.compile(r"(?<![\w.])(/[A-Za-z][A-Za-z0-9_.:${}/}-]*)")
CREATE_RE = re.compile(
    r"\bCREATE\s+(?:TABLE|TYPE)\s+(?:IF\s+NOT\s+EXISTS\s+)?(`?)([A-Za-z_][\w]*)\1",
    re.I,
)
T_HEAD_RE = re.compile(r"^##\s+(T-\d+)\b", re.M)
R_HEAD_RE = re.compile(r"^###\s+(R-\d+)\s*[:：]\s*(.+?)\s*$", re.M)
VARIANT_RE = re.compile(r"\bVariant\s+([A-Za-z0-9]+)\b")
MODULE_RE = re.compile(
    r"(?:`([A-Za-z][\w./-]*\.[A-Za-z][\w]*)`)|"
    r"\b([A-Z][A-Za-z0-9]+(?:Card|Board|View|Page|Service|Handler|Repo))\b"
)
DAG_EDGE_RE = re.compile(r"(T-\d+)\s*←\(([^)]*)\)")
CODE_RE = re.compile(r"`([^`]+)`")
HTML_CODE_RE = re.compile(r"<code>(.*?)</code>", re.S | re.I)
SELECT_VERBS = ("採", "選定", "採用")


class NotParsed(Exception):
    pass


class Mismatch(Exception):
    pass


class SkipStage(Exception):
    pass


def normalize(text):
    if text is None:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", "", text)
    return text


def inner_text(block):
    return htmlmod.unescape(re.sub(r"<[^>]+>", "", block or ""))


def headings(text):
    found = []
    for match in HEADING_RE.finditer(text):
        found.append((match.start(), match.end(), match.group(2).strip()))
    return found


def section_named(text, predicate, label):
    found = headings(text)
    hits = []
    for index, (start, end, title) in enumerate(found):
        if predicate(title):
            body_end = found[index + 1][0] if index + 1 < len(found) else len(text)
            hits.append((title, text[end:body_end]))
    if not hits:
        raise NotParsed("抽不到%s" % label)
    if len(hits) > 1:
        raise NotParsed("%s 出現 %d 次(需恰為 1)" % (label, len(hits)))
    return hits[0]


def parse_table(section_body, label):
    rows = []
    for raw in section_body.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise NotParsed("%s 表列不足(需要表頭+資料列)" % label)
    header = rows[0]
    data = rows[1:]
    if not data:
        raise NotParsed("%s 沒有資料列" % label)
    return header, data


def diagram_body_md(md, needles, label):
    title, body = section_named(
        md, lambda t: any(n in t for n in needles), label
    )
    fences = re.findall(r"```[^\n]*\n(.*?)```", body, re.S)
    if fences:
        return title, "\n".join(fences)
    return title, body


def html_heading_hits(html_text, needles):
    hits = []
    for match in HTML_HEAD_RE.finditer(html_text):
        title = inner_text(match.group(3)).strip()
        if any(n in title for n in needles):
            hits.append((match.start(), match.end(), match.group(1).lower(), title))
    return hits


def extract_tagged(text, tag, html_id):
    start_re = re.compile(
        r'<%s\b[^>]*\bid="%s"[^>]*>' % (re.escape(tag), re.escape(html_id)),
        re.I,
    )
    matches = list(start_re.finditer(text))
    if not matches:
        return None
    if len(matches) != 1:
        raise NotParsed(
            '%s id="%s" 在檔內出現 %d 次(需恰為 1)' % (tag, html_id, len(matches))
        )
    start = matches[0].start()
    close = "</%s>" % tag
    end = text.find(close, matches[0].end())
    if end < 0:
        raise NotParsed('%s id="%s" 找不到 %s' % (tag, html_id, close))
    return text[start:end + len(close)]


def html_figure_fallback_figid(html_text, label):
    ids = re.findall(r'\bid="(fig-[^"]+)"', html_text)
    if not ids:
        raise NotParsed("抽不到 html %s(標題無圖名,亦無手寫 #fig-*)" % label)
    uniq = []
    for html_id in ids:
        if html_id not in uniq:
            uniq.append(html_id)
    if len(uniq) != 1:
        raise NotParsed(
            "html %s 標題找不到,且 #fig-* 不唯一:%s" % (label, uniq)
        )
    html_id = uniq[0]
    for tag in ("svg", "pre", "section", "figure", "div"):
        block = extract_tagged(html_text, tag, html_id)
        if block is not None:
            return html_id, block
    raise NotParsed('html #%s 不是 svg／pre／含圖容器' % html_id)


def slice_until_next_heading(html_text, start, rank):
    rest = html_text[start:]
    if rank == "summary":
        close = re.search(r"</details>", rest, re.I)
        if not close:
            raise NotParsed("html summary 找不到收尾 </details>")
        return rest[:close.end()]
    nxt = re.search(r"<h[12]\b", rest[1:], re.I)
    if nxt:
        return rest[: nxt.start() + 1]
    return rest


def diagram_body_html(html_text, needles, label):
    hits = html_heading_hits(html_text, needles)
    if not hits:
        fig_id, block = html_figure_fallback_figid(html_text, label)
        return fig_id, block
    if len(hits) > 1:
        raise NotParsed("%s html 圖標題出現 %d 次(需恰為 1)" % (label, len(hits)))
    start, end, rank, title = hits[0]
    body = slice_until_next_heading(html_text, end, rank)
    return title, body


def diagram_plain(block):
    texts = re.findall(r"<text\b[^>]*>(.*?)</text>", block, re.S)
    if texts:
        return "".join(inner_text(t) for t in texts)
    pres = re.findall(r"<pre\b[^>]*>(.*?)</pre>", block, re.S)
    if pres:
        return "\n".join(inner_text(p) for p in pres)
    return inner_text(block)


def read_pair(md_path, html_path, optional=False):
    md_ok = os.path.isfile(md_path)
    html_ok = os.path.isfile(html_path)
    if optional and (not md_ok) and (not html_ok):
        raise SkipStage("兩檔都不存在,跳過")
    if not md_ok:
        raise NotParsed("缺 %s" % md_path)
    if not html_ok:
        raise NotParsed("缺 %s" % html_path)
    return (
        open(md_path, encoding="utf-8").read(),
        open(html_path, encoding="utf-8").read(),
    )


def approach_key(name):
    match = re.match(r"^\s*([A-Za-z]|\d+)", name.strip())
    if match:
        return match.group(1).upper()
    return normalize(name)


def parse_approaches(md):
    _, body = section_named(
        md,
        lambda t: "Approaches Considered" in t or t.strip() == "Approaches",
        "Approaches Considered 表",
    )
    _header, data = parse_table(body, "Approaches Considered")
    names = []
    for row in data:
        cell = row[0].strip() if row else ""
        if normalize(cell) in {normalize(x) for x in EMPTY_CELLS} or not cell:
            continue
        names.append(re.sub(r"\s+", " ", cell))
    if not names:
        raise NotParsed("Approaches 解析到 0 個方案")
    keys = [approach_key(n) for n in names]
    if len(set(keys)) != len(keys):
        raise NotParsed("Approaches 方案 token 不唯一:%s" % keys)
    return names, keys


def parse_rejected_keys(md, keys):
    try:
        _, body = section_named(
            md,
            lambda t: "Rejected" in t,
            "Rejected Alternatives",
        )
    except NotParsed:
        return []
    found = []
    for raw in body.splitlines():
        line = raw.strip().lstrip("-*").strip()
        if not line:
            continue
        token = re.split(r"[:：\s]", line, maxsplit=1)[0].strip()
        key = approach_key(token) if token else ""
        if key in keys and key not in found:
            found.append(key)
    return found


def parse_decision_key(md, keys):
    _, body = section_named(
        md, lambda t: t.strip() == "Decision" or t.startswith("Decision"), "Decision"
    )
    first = ""
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue
        first = inner_text(line)
        break
    if not first:
        return None
    if not any(v in first for v in SELECT_VERBS):
        return None
    match = re.search(r"(?:採|選定|採用)\s*[*]*\s*([A-Za-z0-9]+)", first)
    if not match:
        raise NotParsed("Decision 首句有採／選定／採用但對不上任何方案 token")
    token = match.group(1).upper()
    if token not in keys:
        raise NotParsed("Decision 首句選定 token %s 不在 Approaches" % token)
    return token


def selected_key(md, names, keys):
    rejected = parse_rejected_keys(md, keys)
    remain = [k for k in keys if k not in rejected]
    from_set = remain[0] if len(remain) == 1 else None
    from_dec = parse_decision_key(md, keys)
    if from_set and from_dec and from_set != from_dec:
        raise NotParsed(
            "Approaches−Rejected 選定 %s 與 Decision 選定 %s 不一致"
            % (from_set, from_dec)
        )
    chosen = from_set or from_dec
    if not chosen:
        raise NotParsed("抽不到唯一選定案(Approaches−Rejected 不是恰好 1,Decision 也對不上)")
    return chosen, rejected, dict(zip(keys, names))


def labeled_blocks(plain, labels):
    hits = []
    for label in labels:
        needles = ["[" + label + "]", label]
        pos = -1
        used = None
        for needle in needles:
            found = plain.find(needle)
            if found >= 0 and (pos < 0 or found < pos):
                pos = found
                used = needle
        if pos >= 0:
            hits.append((pos, label, used))
    hits.sort()
    blocks = {}
    for i, (pos, label, _used) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(plain)
        blocks[label] = plain[pos:end]
    return blocks


def bite_stage2(md, html_text, tag):
    names, keys = parse_approaches(md)
    chosen, rejected, keymap = selected_key(md, names, keys)
    _title, md_fig = diagram_body_md(md, FIG_NEEDLES[2], "方案架構圖")
    _ht, html_fig = diagram_body_html(html_text, FIG_NEEDLES[2], "方案架構圖")
    md_plain = md_fig
    html_plain = diagram_plain(html_fig)
    failures = []
    fp = []
    for label, plain, where in (
        ("md方案架構圖", md_plain, "md"),
        ("html方案架構圖", html_plain, "html"),
    ):
        if not normalize(plain):
            raise NotParsed("%s %s 抽出 0 個字" % (tag, label))
        blocks = labeled_blocks(plain, keys)
        if chosen not in blocks:
            failures.append("%s %s 缺選定案「%s」" % (tag, label, keymap[chosen]))
        else:
            if "選定" not in blocks[chosen]:
                failures.append(
                    "%s %s 選定案「%s」未標「選定」" % (tag, label, keymap[chosen])
                )
        for rk in rejected:
            if rk in blocks and "選定" in blocks[rk]:
                failures.append(
                    "%s %s Rejected 案「%s」不得標選定" % (tag, label, keymap[rk])
                )
        marked = [k for k, b in blocks.items() if "選定" in b]
        fp.append((where, tuple(marked)))
    if fp[0][1] != fp[1][1]:
        failures.append(
            "%s md 方案架構圖與 html 同節選定標不同 md:%s html:%s"
            % (tag, fp[0][1], fp[1][1])
        )
    print("[%s] approaches=%s selected=%s rejected=%s" % (
        tag, ",".join(keys), chosen, ",".join(rejected) or "∅"
    ))
    if failures:
        raise Mismatch("\n".join(failures))
    print("[%s] 選定標 md=%s html=%s" % (tag, fp[0][1], fp[1][1]))
    return ("sel:" + chosen, tuple(sorted(rejected)))


def parse_method_variants(md):
    _, body = section_named(
        md, lambda t: t.strip() == "Method" or t.startswith("Method"), "Method"
    )
    found = []
    for match in VARIANT_RE.finditer(body):
        token = "Variant " + match.group(1)
        if token not in found:
            found.append(token)
    if not found:
        for match in MODULE_RE.finditer(body):
            token = match.group(1) or match.group(2)
            if token and token not in found:
                found.append(token)
    if not found:
        raise NotParsed("Method 抽不到任何具名 variant")
    return found


def variant_labels(variants):
    labels = []
    for v in variants:
        m = re.match(r"Variant\s+(\S+)", v)
        if m:
            labels.append(m.group(1))
        else:
            labels.append(v)
    return labels


def bite_stage3(md, html_text, tag):
    variants = parse_method_variants(md)
    labels = variant_labels(variants)
    _title, md_fig = diagram_body_md(md, FIG_NEEDLES[3], "結構圖")
    _ht, html_fig = diagram_body_html(html_text, FIG_NEEDLES[3], "結構圖")
    md_plain = md_fig
    html_plain = diagram_plain(html_fig)
    failures = []
    fp = []
    for label, plain in (("md結構圖", md_plain), ("html結構圖", html_plain)):
        if not normalize(plain):
            raise NotParsed("%s %s 抽出 0 個字" % (tag, label))
        norm = normalize(plain)
        missing = [v for v in variants if normalize(v) not in norm and normalize(variant_labels([v])[0]) not in norm]
        if missing:
            failures.append("%s %s 缺 Method variant %s" % (tag, label, missing))
        blocks = labeled_blocks(plain, ["Variant " + x for x in labels] + labels)
        marked = []
        for lab, block in blocks.items():
            if "選定" in block:
                marked.append(lab)
        if not marked:
            failures.append("%s %s 沒有任何 variant 標「選定」" % (tag, label))
        else:
            ok = False
            for mark in marked:
                key = mark.replace("Variant ", "")
                if any(variant_labels([v])[0] == key or v == mark for v in variants):
                    ok = True
            if not ok:
                failures.append(
                    "%s %s 標選定的 %s 不在 Method 具名 variant 裡"
                    % (tag, label, marked)
                )
        extra = []
        for vm in VARIANT_RE.finditer(plain):
            token = vm.group(1)
            if token not in labels:
                extra.append(token)
        if extra:
            failures.append("%s %s 多出 variant %s,對不上 Method" % (tag, label, extra))
        fp.append(tuple(sorted(normalize(x) for x in marked)))
    if fp[0] != fp[1]:
        failures.append(
            "%s md 結構圖與 html 同節選定標不同 md:%s html:%s" % (tag, fp[0], fp[1])
        )
    print("[%s] variants=%s" % (tag, ",".join(variants)))
    if failures:
        raise Mismatch("\n".join(failures))
    print("[%s] 選定標 md=%s html=%s" % (tag, fp[0], fp[1]))
    return tuple(variants), fp[0]


def shall_words(title):
    match = re.search(r"SHALL\s+(.+)$", title, re.I | re.S)
    if not match:
        raise NotParsed("R 標題沒有 SHALL:%s" % title)
    tail = match.group(1)
    words = []

    def add(tok):
        if not tok or tok in SHALL_STOP or tok in words:
            return
        words.append(tok)

    for tok in re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}", tail):
        add(tok)
    for chunk in re.split(r"[、，。；;,.!?！？/／|且與的在中由僅可該]+", tail):
        for run in re.findall(r"[\u4e00-\u9fff]+", chunk):
            if len(run) < 2:
                continue
            if len(run) <= 4:
                add(run)
            for size in (2, 3, 4):
                if len(run) < size:
                    continue
                for i in range(0, len(run) - size + 1):
                    add(run[i:i + size])
    if not words:
        raise NotParsed("SHALL 後抽不到行為詞:%s" % title)
    return words


def parse_requirements(md):
    found = list(R_HEAD_RE.finditer(md))
    if not found:
        raise NotParsed("抽不到 ### R-n: 標題")
    rows = []
    seen = set()
    for match in found:
        rid = match.group(1)
        if rid in seen:
            raise NotParsed("R-id 重複:%s" % rid)
        seen.add(rid)
        title = match.group(2).strip()
        rows.append((rid, shall_words(title)))
    return rows


def bite_stage4(md, html_text, tag):
    reqs = parse_requirements(md)
    _title, md_fig = diagram_body_md(md, FIG_NEEDLES[4], "行為流程圖")
    _ht, html_fig = diagram_body_html(html_text, FIG_NEEDLES[4], "行為流程圖")
    md_plain = md_fig
    html_plain = diagram_plain(html_fig)
    failures = []
    fps = []
    text_ids = [r for r, _ in reqs]
    for label, plain in (("md行為流程圖", md_plain), ("html行為流程圖", html_plain)):
        if not normalize(plain):
            raise NotParsed("%s %s 抽出 0 個字" % (tag, label))
        norm = normalize(plain)
        fig_ids = re.findall(r"R-\d+", plain)
        fig_set = []
        for rid in fig_ids:
            if rid not in fig_set:
                fig_set.append(rid)
        for rid, words in reqs:
            if rid not in fig_set and normalize(rid) not in norm:
                failures.append("%s %s 缺 %s" % (tag, label, rid))
                continue
            if not any(normalize(w) in norm for w in words):
                failures.append(
                    "%s %s %s 的 SHALL 行為詞一個都不在圖上:%s"
                    % (tag, label, rid, "、".join(words))
                )
        extra = [rid for rid in fig_set if rid not in text_ids]
        if extra:
            failures.append("%s %s 多出 R %s,對不上文字" % (tag, label, extra))
        hit = []
        for rid, words in reqs:
            hit.append((rid, tuple(w for w in words if normalize(w) in norm)))
        fps.append(tuple(hit))
    if fps[0] != fps[1]:
        failures.append(
            "%s md 行為流程圖與 html 同節指紋不同\n    md:%s\n    html:%s"
            % (tag, fps[0], fps[1])
        )
    print("[%s] R=%s" % (tag, ",".join(text_ids)))
    if failures:
        raise Mismatch("\n".join(failures))
    print("[%s] 行為詞 md=%s" % (tag, fps[0]))
    return fps[0]


def parse_tasks(md):
    found = list(T_HEAD_RE.finditer(md))
    if not found:
        raise NotParsed("抽不到 ## T-n")
    nodes = []
    edges = set()
    for i, match in enumerate(found):
        tid = match.group(1)
        end = found[i + 1].start() if i + 1 < len(found) else len(md)
        body = md[match.end():end]
        field = re.search(r"^\s*-\s*Blocked-by:\s*(.+)$", body, re.M)
        if not field:
            raise NotParsed("%s 缺 Blocked-by" % tid)
        raw = field.group(1).strip()
        deps = re.findall(r"T-\d+", raw)
        if normalize(raw) in {normalize(x) for x in EMPTY_CELLS}:
            deps = []
        nodes.append(tid)
        for dep in deps:
            edges.add((dep, tid))
    if len(nodes) != len(set(nodes)):
        raise NotParsed("T-id 重複:%s" % nodes)
    return nodes, edges


def extract_dag(html_text):
    n = html_text.count('id="dag"')
    if n == 0:
        raise NotParsed('抽不到 html #dag')
    if n != 1:
        raise NotParsed('html #dag 出現 %d 次(需恰為 1)' % n)
    block = None
    for tag in ("section", "div", "pre", "figure"):
        block = extract_tagged(html_text, tag, "dag")
        if block is not None:
            break
    if block is None:
        raise NotParsed('html #dag 不是 section／pre／含圖容器')
    plain = diagram_plain(block)
    if not normalize(plain):
        raise NotParsed("html #dag 抽出 0 個字")
    nodes = []
    for tid in re.findall(r"T-\d+", plain):
        if tid not in nodes:
            nodes.append(tid)
    if not nodes:
        raise NotParsed("html #dag 解析到 0 個 T-n")
    edges = set()
    for match in DAG_EDGE_RE.finditer(plain):
        dst = match.group(1)
        for src in re.findall(r"T-\d+", match.group(2)):
            edges.add((src, dst))
    return nodes, edges, plain


def bite_stage5(md, html_text, tag):
    md_nodes, md_edges = parse_tasks(md)
    html_nodes, html_edges, _plain = extract_dag(html_text)
    failures = []
    if set(md_nodes) != set(html_nodes):
        failures.append(
            "%s md T 集合 ≠ html #dag(少 %s / 多 %s)"
            % (
                tag,
                [t for t in md_nodes if t not in html_nodes],
                [t for t in html_nodes if t not in md_nodes],
            )
        )
    if md_edges != html_edges:
        failures.append(
            "%s md Blocked-by 邊 ≠ html #dag ←(T-n)\n    md:%s\n    html:%s"
            % (
                tag,
                tuple(sorted(md_edges)),
                tuple(sorted(html_edges)),
            )
        )
    print("[%s] T=%s edges=%d" % (tag, ",".join(md_nodes), len(md_edges)))
    if failures:
        raise Mismatch("\n".join(failures))
    print("[%s] dag edges=%s" % (tag, tuple(sorted(html_edges))))
    return tuple(md_nodes), tuple(sorted(md_edges))


def basename_of(path):
    path = htmlmod.unescape(path).strip().strip("`")
    path = path.split()[0] if path.split() else path
    path = path.replace("\\", "/")
    return os.path.basename(path)


def is_pathish(token):
    token = htmlmod.unescape(token).strip().strip("`")
    if not token or "\n" in token or len(token) > 180:
        return False
    first = token.split()[0]
    if first.upper() in {
        "SELECT", "UPDATE", "INSERT", "DELETE", "FROM", "WHERE", "CREATE",
    }:
        return False
    return bool(CODE_EXT_RE.search(first) or CODE_EXT_RE.search(os.path.basename(first)))


def parse_diff(md):
    _, body = section_named(
        md,
        lambda t: t.strip().startswith("Diff") or t.startswith("Diff("),
        "Diff",
    )
    if not body.strip():
        raise NotParsed("Diff 節是空的")
    bases = []
    for raw in CODE_RE.findall(body) + [
        inner_text(x) for x in HTML_CODE_RE.findall(body)
    ]:
        if not is_pathish(raw):
            continue
        base = basename_of(raw)
        if not base or base in bases:
            continue
        bases.append((base, raw.replace("\\", "/")))
    endpoints = []
    for method, path in HTTP_RE.findall(body):
        item = (method.upper(), normalize_path(path))
        if item not in endpoints:
            endpoints.append(item)
    paths = []
    for path in PATH_RE.findall(body):
        np = normalize_path(path)
        if np not in paths:
            paths.append(np)
    tables = []
    for _q, name in CREATE_RE.findall(body):
        if name not in tables:
            tables.append(name)
    return {
        "body": body,
        "bases": bases,
        "endpoints": endpoints,
        "paths": paths,
        "tables": tables,
        "norm": normalize(body),
    }


def normalize_path(path):
    path = htmlmod.unescape(path).rstrip(".,;:)")
    path = re.sub(r"\$\{[^}]+\}", ":id", path)
    path = re.sub(r":[A-Za-z_][\w]*", ":id", path)
    path = re.sub(r"\bC\.id\b", ":id", path)
    path = re.sub(r"/+", "/", path)
    return path


def figure_modules(plain):
    modules = re.findall(r"\[([^\[\]]+)\]", plain)
    endpoints = [(m.upper(), normalize_path(p)) for m, p in HTTP_RE.findall(plain)]
    paths = [normalize_path(p) for p in PATH_RE.findall(plain)]
    return modules, endpoints, paths


def stem(name):
    return name.rsplit(".", 1)[0] if "." in name else name


def parent_dir(path):
    parts = path.replace("\\", "/").split("/")
    if len(parts) >= 2:
        return parts[-2]
    return ""


def diff_covers_basename(base, raw, fig_norm, fig_modules):
    if TEST_FILE_RE.search(raw) or TEST_FILE_RE.search(base):
        return True
    cleaned = re.sub(r"^\d+_", "", stem(base))
    candidates = [base, stem(base), cleaned, parent_dir(raw)]
    fig_join = " ".join(fig_modules)
    fig_n = fig_norm + normalize(fig_join)
    for cand in candidates:
        if not cand:
            continue
        if normalize(cand) in fig_n:
            return True
    return False


def token_in_diff(token, diff):
    token = token.strip()
    n = normalize(token)
    if not n:
        return True
    if n in diff["norm"]:
        return True
    method_m = re.match(
        r"(GET|POST|PUT|PATCH|DELETE)\s+(.+)$", token, re.I
    )
    path_part = method_m.group(2).strip() if method_m else re.split(
        r"[\s+]+", token, maxsplit=1
    )[0]
    np = normalize_path(path_part)
    if any(np == p or normalize(np) == normalize(p) for p in diff["paths"]):
        return True
    if any(np == p for _m, p in diff["endpoints"]):
        return True
    if any(n == normalize(b) or n == normalize(stem(b)) for b, _r in diff["bases"]):
        return True
    if any(n == normalize(t) for t in diff["tables"]):
        return True
    last = path_part.strip().rstrip("/").rsplit("/", 1)[-1]
    last = re.sub(r"^:id$", "", last)
    if last and normalize(last) in diff["norm"]:
        return True
    return False


def bite_stage7(md, html_text, tag):
    diff = parse_diff(md)
    _title, md_fig = diagram_body_md(md, FIG_NEEDLES[7], "變更架構圖")
    _ht, html_fig = diagram_body_html(html_text, FIG_NEEDLES[7], "變更架構圖")
    md_plain = md_fig
    html_plain = diagram_plain(html_fig)
    failures = []
    fps = []
    for label, plain in (("md變更架構圖", md_plain), ("html變更架構圖", html_plain)):
        if not normalize(plain):
            raise NotParsed("%s %s 抽出 0 個字" % (tag, label))
        modules, endpoints, paths = figure_modules(plain)
        fig_norm = normalize(plain)
        for base, raw in diff["bases"]:
            if not diff_covers_basename(base, raw, fig_norm, modules):
                failures.append(
                    "%s %s 缺 Diff basename「%s」" % (tag, label, base)
                )
        for method, path in diff["endpoints"]:
            if (method, path) not in endpoints and normalize(path) not in fig_norm:
                failures.append(
                    "%s %s 缺 Diff 端點 %s %s" % (tag, label, method, path)
                )
        for path in diff["paths"]:
            if path in diff_covers_ignore_paths():
                continue
            if normalize(path) in fig_norm or any(
                normalize(path) == normalize(p) for p in paths
            ):
                continue
            # 路徑在 Diff 程式碼裡很碎,只要求最後一段或全路徑對得上圖或可忽略測試檔
            last = path.rstrip("/").rsplit("/", 1)[-1]
            if last and normalize(last) in fig_norm:
                continue
        for table in diff["tables"]:
            if normalize(table) not in fig_norm and not any(
                normalize(table) in normalize(m) for m in modules
            ):
                # 歷程表常畫成「歷程表」而不是 SQL 名;只要 Diff 表名的顯著詞在圖上
                stem_tok = table.replace("contract_", "").replace("_status", "")
                if stem_tok and normalize(stem_tok) in fig_norm:
                    continue
                if "history" in table.lower() and "歷程" in plain:
                    continue
                failures.append("%s %s 缺新表名「%s」" % (tag, label, table))
        extras = []
        for mod in modules:
            if looks_like_architecture_token(mod) and not token_in_diff(mod, diff):
                extras.append(mod)
        for method, path in endpoints:
            blob = method + " " + path
            if not token_in_diff(blob, diff) and not token_in_diff(path, diff):
                extras.append(blob)
        if extras:
            failures.append(
                "%s %s 多出模組／端點 %s,對不上 Diff" % (tag, label, extras)
            )
        fps.append((tuple(modules), tuple(endpoints)))
    if fps[0] != fps[1]:
        failures.append(
            "%s md 變更架構圖與 html 同節指紋不同\n    md:%s\n    html:%s"
            % (tag, fps[0], fps[1])
        )
    print("[%s] diff bases=%s endpoints=%s tables=%s" % (
        tag,
        ",".join(b for b, _ in diff["bases"]),
        ",".join("%s %s" % e for e in diff["endpoints"]) or "∅",
        ",".join(diff["tables"]) or "∅",
    ))
    if failures:
        raise Mismatch("\n".join(failures))
    print("[%s] 圖模組=%s" % (tag, fps[0][0]))
    return fps[0]


def diff_covers_ignore_paths():
    return ()


def looks_like_architecture_token(mod):
    mod = mod.strip()
    if re.search(r"\.[A-Za-z][A-Za-z0-9]+$", mod):
        return True
    if mod.startswith("/") or re.match(r"^(GET|POST|PUT|PATCH|DELETE)\b", mod):
        return True
    if re.match(r"^[A-Z][A-Za-z0-9]+$", mod) and len(mod) >= 4:
        return True
    return False


def check_stage(stage, md_path, html_path, tag):
    optional = stage == 3
    try:
        md, html_text = read_pair(md_path, html_path, optional=optional)
    except SkipStage as exc:
        print("[%s] skip(%s)" % (tag, exc))
        return "skip"
    if stage == 2:
        return bite_stage2(md, html_text, tag)
    if stage == 3:
        return bite_stage3(md, html_text, tag)
    if stage == 4:
        return bite_stage4(md, html_text, tag)
    if stage == 5:
        return bite_stage5(md, html_text, tag)
    if stage == 7:
        return bite_stage7(md, html_text, tag)
    raise NotParsed("未知站 %s" % stage)


def fixture_paths(stage):
    md_name, html_name = STAGE_FILES[stage]
    folder = os.path.join(FIX_ROOT, str(stage), "good")
    return (
        os.path.join(folder, md_name),
        os.path.join(folder, html_name),
        folder,
    )


def example_paths(stage):
    md_name, html_name = STAGE_FILES[stage]
    return (
        os.path.join(EXAMPLE, md_name),
        os.path.join(EXAMPLE, html_name),
    )


def check_fixtures():
    if not os.path.isdir(FIX_ROOT):
        raise NotParsed("缺正例目錄 scripts/fixtures/devstage-fig-text/")
    for stage in (2, 3, 4, 5, 7):
        md_path, html_path, folder = fixture_paths(stage)
        if not os.path.isdir(folder):
            raise NotParsed("缺 %s" % folder)
        check_stage(stage, md_path, html_path, "fixture-%s" % stage)


def check_example():
    if not os.path.isdir(EXAMPLE):
        raise NotParsed("缺 example/contract-expiry-reminder/")
    for stage in (2, 3, 4, 5, 7):
        md_path, html_path = example_paths(stage)
        check_stage(stage, md_path, html_path, "example-%s" % stage)


def copy_tree(dst):
    src_fix = os.path.join(root, "scripts", "fixtures", "devstage-fig-text")
    dest_fix = os.path.join(dst, "scripts", "fixtures", "devstage-fig-text")
    shutil.copytree(src_fix, dest_fix)
    src_ex = os.path.join(root, "example", "contract-expiry-reminder")
    dest_ex = os.path.join(dst, "example", "contract-expiry-reminder")
    os.makedirs(dest_ex, exist_ok=True)
    for stage in (2, 3, 4, 5, 7):
        md_name, html_name = STAGE_FILES[stage]
        for name in (md_name, html_name):
            src = os.path.join(src_ex, name)
            if os.path.isfile(src):
                shutil.copy(src, os.path.join(dest_ex, name))


def child_rc(tree):
    proc = subprocess.run(
        ["bash", self_script, "--skip-mutation", tree],
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout or "") + "\n" + (proc.stderr or "")


def replace_in_section(text, heading_substr, old, new, label, replace_all=False):
    found = headings(text)
    for index, (start, end, title) in enumerate(found):
        if heading_substr not in title:
            continue
        body_end = found[index + 1][0] if index + 1 < len(found) else len(text)
        body = text[end:body_end]
        if old not in body:
            raise Mismatch("破壞實驗 %s 找不到 %r" % (label, old))
        if replace_all:
            body = body.replace(old, new)
        else:
            body = body.replace(old, new, 1)
        return text[:end] + body + text[body_end:]
    raise Mismatch("破壞實驗找不到節 %s" % label)


def write(path, text):
    open(path, "w", encoding="utf-8").write(text)


def expect_rc(tmp, want, ok_msg, fail_msg, failures):
    rc, blob = child_rc(tmp)
    if rc == want:
        print("[mut] ✓ %s" % ok_msg)
    else:
        failures.append("%s,實際 rc=%s\n%s" % (fail_msg, rc, blob[-1600:]))


def run_mutations():
    failures = []

    with tempfile.TemporaryDirectory(prefix="dsft-good-") as tmp:
        copy_tree(tmp)
        expect_rc(tmp, 0, "好樣本複本綠", "好樣本複本必須綠", failures)

    with tempfile.TemporaryDirectory(prefix="dsft-2sel-") as tmp:
        copy_tree(tmp)
        path = os.path.join(tmp, "scripts", "fixtures", "devstage-fig-text", "2", "good", "2-decision.md")
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text, "Decision", "採 A(登入即時查)", "採 B(nightly cron + 通知表)", "Decision 選定"
            )
            text = replace_in_section(
                text, "Rejected", "- B:", "- A:", "Rejected 換成刷掉 A"
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            write(path, text)
            expect_rc(
                tmp, 1,
                "改 2 的選定(Decision／Rejected)不改圖必須紅",
                "改 2 選定不改圖必須 exit 1",
                failures,
            )

    with tempfile.TemporaryDirectory(prefix="dsft-3var-") as tmp:
        copy_tree(tmp)
        path = os.path.join(tmp, "scripts", "fixtures", "devstage-fig-text", "3", "good", "3-prototype.md")
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text, "Method", "Variant B", "Variant D", "Method variant 名"
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            write(path, text)
            expect_rc(
                tmp, 1,
                "改 3 的 variant 名不改圖必須紅",
                "改 3 variant 名不改圖必須 exit 1",
                failures,
            )

    with tempfile.TemporaryDirectory(prefix="dsft-4shall-") as tmp:
        copy_tree(tmp)
        path = os.path.join(tmp, "scripts", "fixtures", "devstage-fig-text", "4", "good", "4-spec.md")
        text = open(path, encoding="utf-8").read()
        old = "系統 SHALL 在 dashboard 顯示到期卡片"
        new = "系統 SHALL 寄送email廣播且不渲染界面"
        if old not in text:
            failures.append("破壞實驗 4 找不到 SHALL 原句")
        else:
            write(path, text.replace(old, new, 1))
            expect_rc(
                tmp, 1,
                "改 4 的 SHALL 行為詞不改圖必須紅",
                "改 4 SHALL 行為詞不改圖必須 exit 1",
                failures,
            )

    with tempfile.TemporaryDirectory(prefix="dsft-5edge-") as tmp:
        copy_tree(tmp)
        path = os.path.join(tmp, "scripts", "fixtures", "devstage-fig-text", "5", "good", "5-tasks.md")
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text, "T-3", "Blocked-by: T-2", "Blocked-by: T-1", "T-3 Blocked-by"
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            write(path, text)
            expect_rc(
                tmp, 1,
                "改 5 的 Blocked-by 不改 #dag 必須紅",
                "改 5 Blocked-by 不改 #dag 必須 exit 1",
                failures,
            )

    with tempfile.TemporaryDirectory(prefix="dsft-7base-") as tmp:
        copy_tree(tmp)
        path = os.path.join(tmp, "scripts", "fixtures", "devstage-fig-text", "7", "good", "7-review.md")
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text,
                "Diff",
                "`src/pages/Dashboard.tsx`",
                "`src/pages/Dashboard.tsx`\n`src/evil/Evil.tsx`",
                "Diff 增 basename",
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            write(path, text)
            expect_rc(
                tmp, 1,
                "Diff 增一個 basename 不改圖必須紅",
                "Diff 增 basename 不改圖必須 exit 1",
                failures,
            )

    with tempfile.TemporaryDirectory(prefix="dsft-7ep-") as tmp:
        copy_tree(tmp)
        path = os.path.join(tmp, "scripts", "fixtures", "devstage-fig-text", "7", "good", "7-review.md")
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text,
                "Diff",
                "GET /contracts/expiring",
                "GET /contracts/expired",
                "Diff 改端點",
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            write(path, text)
            expect_rc(
                tmp, 1,
                "Diff 改一個端點不改圖必須紅",
                "Diff 改端點不改圖必須 exit 1",
                failures,
            )

    if failures:
        raise Mismatch("破壞實驗沒咬到:\n" + "\n".join(failures))


try:
    check_fixtures()
    check_example()
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

print("✅ PASS:2／3／4／5／7 圖對文字指紋 + 破壞實驗全過")
sys.exit(0)
PY
