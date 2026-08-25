#!/bin/bash
# check-devtalk-fig-journey.sh — feature 討論的現況圖對 Actors／Current Journey
#
# 為什麼需要:訪談改了「人現在怎麼走」,現況圖若沒跟上會默默錯。既有
# check-devtalk-fig-graph.sh 管 skill hop／導覽全程地圖／掃頁六件形狀 ——
# 不管各 feature 的現況圖。本檔是另一顆牙,不准取代那支。
#
# 這顆牙不管 skill hop。
#
# 指紋(機械,不是整檔 SHA):
#   流程:Actors 名字集合 + Current Journey 有序列(誰、工具、動作詞、痛點詞)。
#        正規化空白與全半形(NFKC)。
#   圖:md「現況圖」節(不准拿「邏輯圖／明天系統流」充這個槽)以及 html #scan-now
#      的 svg／pre,抽出同樣 token。
#   咬:Journey 每步的誰／工具必須在圖上;圖上多出來的人／工具必須對得上
#      Actors／Journey;步序一致。md 現況圖與 html #scan-now 指紋必須相同。
#   抽不到表或圖 → exit 2(NOT-PARSED)。
#
# 正例:scripts/fixtures/devtalk-fig-journey/good/
#   (必須有 Actors 表 + Current Journey 表 + 現況圖;html-scan 樣張不夠,另開目錄)
#
# 破壞實驗(本檔每次跑,除非 --skip-mutation):
#   改 Journey 的工具不改圖必須紅;改圖上的角色不改 Journey 必須紅;好樣本必須綠。
#
# 用法:
#   scripts/check-devtalk-fig-journey.sh [root]
#   scripts/check-devtalk-fig-journey.sh --skip-mutation [root]
# exit:0 = 全過 / 1 = 真漂移 / 2 = NOT-PARSED
#
# 不改 check-devtalk-fig-graph.sh / check-devtalk-graph.sh / check-devtalk-guide-sync.sh。

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

python3 - "$ROOT" "$SELF/check-devtalk-fig-journey.sh" "$SKIP_MUTATION" <<'PY'
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

FIX_DIR = os.path.join(
    root, "scripts", "fixtures", "devtalk-fig-journey", "good"
)
FIX_MD = os.path.join(FIX_DIR, "1-discussion.md")
FIX_HTML = os.path.join(FIX_DIR, "1-discussion.html")

EMPTY_CELLS = {
    "", "—", "-", "–", "−", "無", "无", "n/a", "N/A", "NA", "none", "None",
}
STOPWORDS = {
    "現況", "現況圖", "邏輯圖", "痛在這", "痛在哪", "現在", "怎麼走", "怎麼做",
    "做什麼", "用什麼", "然後", "之後", "下一步", "步驟", "誰", "工具", "動作",
    "痛點", "等待", "系統", "直式", "樣張", "討論", "明天", "系統流", "ascii",
    "ASCII", "pre", "svg", "SVG",
}
SPLIT_RE = re.compile(r"[、,，/;；／|]+")
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)


class NotParsed(Exception):
    pass


class Mismatch(Exception):
    pass


def normalize(text):
    if text is None:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", "", text)
    return text


def split_items(cell):
    raw = re.sub(r"<[^>]+>", "", cell or "")
    raw = htmlmod.unescape(raw)
    out = []
    for part in SPLIT_RE.split(raw):
        part = part.strip()
        if normalize(part) in {normalize(x) for x in EMPTY_CELLS} or part in EMPTY_CELLS:
            continue
        if not part:
            continue
        out.append(part)
    return out


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
    header = [normalize(c) for c in rows[0]]
    data = rows[1:]
    if not data:
        raise NotParsed("%s 沒有資料列" % label)
    return header, data


def col_index(header, names, label):
    want = [normalize(n) for n in names]
    for index, cell in enumerate(header):
        if cell in want:
            return index
    raise NotParsed("%s 缺欄(%s)" % (label, "/".join(names)))


def parse_actors(md):
    _, body = section_named(
        md,
        lambda t: "Actors" in t or t.startswith("角色"),
        "Actors 表",
    )
    header, data = parse_table(body, "Actors")
    name_i = col_index(header, ("Actor", "角色", "誰"), "Actors")
    tool_i = None
    for candidate in ("系統外工具", "工具"):
        try:
            tool_i = col_index(header, (candidate,), "Actors")
            break
        except NotParsed:
            continue
    names = []
    tools = []
    for row in data:
        if name_i >= len(row):
            continue
        items = split_items(row[name_i])
        if not items:
            continue
        names.append(normalize(items[0]))
        if tool_i is not None and tool_i < len(row):
            tools.extend(normalize(x) for x in split_items(row[tool_i]))
    if not names:
        raise NotParsed("Actors 解析到 0 個名字")
    return names, tools


def parse_journey(md):
    _, body = section_named(
        md,
        lambda t: "Current Journey" in t or "現況旅程" in t,
        "Current Journey 表",
    )
    header, data = parse_table(body, "Current Journey")
    who_i = col_index(header, ("誰", "Actor"), "Current Journey")
    act_i = col_index(header, ("真實動作", "動作"), "Current Journey")
    tool_i = col_index(header, ("使用工具", "工具"), "Current Journey")
    pain_i = col_index(header, ("痛點", "痛"), "Current Journey")
    steps = []
    for row in data:
        def cell(idx):
            return row[idx] if idx < len(row) else ""
        who_items = split_items(cell(who_i))
        if not who_items:
            continue
        tools = [normalize(x) for x in split_items(cell(tool_i))]
        actions = [normalize(x) for x in split_items(cell(act_i))]
        pains = [normalize(x) for x in split_items(cell(pain_i))]
        steps.append(
            {
                "who": normalize(who_items[0]),
                "tools": tools,
                "actions": actions,
                "pains": pains,
            }
        )
    if not steps:
        raise NotParsed("Current Journey 解析到 0 步")
    return steps


def diagram_body_md(md):
    try:
        title, body = section_named(
            md, lambda t: "現況圖" in t, "現況圖"
        )
    except NotParsed:
        logic = None
        try:
            logic, _ = section_named(md, lambda t: "邏輯圖" in t, "邏輯圖")
        except NotParsed:
            logic = None
        if logic:
            raise NotParsed(
                "現況圖槽仍叫「%s」——先正名或另開「現況圖」節,"
                "不准讓明天系統流佔這個槽" % logic
            )
        raise NotParsed("抽不到現況圖")
    fences = re.findall(r"```[^\n]*\n(.*?)```", body, re.S)
    if fences:
        return title, "\n".join(fences)
    return title, body


def extract_tagged(text, tag, html_id):
    marker = '<%s id="%s"' % (tag, html_id)
    n = text.count(marker)
    if n == 0:
        return None
    if n != 1:
        raise NotParsed('%s id="%s" 在檔內出現 %d 次(需恰為 1)' % (tag, html_id, n))
    start = text.find(marker)
    close = "</%s>" % tag
    end = text.find(close, start)
    if end < 0:
        raise NotParsed('%s id="%s" 找不到 %s' % (tag, html_id, close))
    return text[start:end + len(close)]


def extract_scan_now(html_text):
    n = html_text.count('id="scan-now"')
    if n == 0:
        raise NotParsed('抽不到 html #scan-now')
    if n != 1:
        raise NotParsed('html #scan-now 出現 %d 次(需恰為 1)' % n)
    for tag in ("svg", "pre", "section", "div", "figure"):
        block = extract_tagged(html_text, tag, "scan-now")
        if block is None:
            continue
        if tag in ("svg", "pre"):
            return block
        inner_svg = re.search(r"<svg\b.*?</svg>", block, re.S)
        inner_pre = re.search(r"<pre\b.*?</pre>", block, re.S)
        if inner_svg:
            return inner_svg.group(0)
        if inner_pre:
            return inner_pre.group(0)
        return block
    raise NotParsed("html #scan-now 不是 svg／pre／含圖容器")


def diagram_plain(block):
    texts = re.findall(r"<text\b[^>]*>(.*?)</text>", block, re.S)
    if texts:
        return "".join(inner_text(t) for t in texts)
    return inner_text(block)


def vocab_from(actors, actor_tools, steps):
    vocab = set(actors)
    vocab.update(actor_tools)
    for step in steps:
        vocab.add(step["who"])
        vocab.update(step["tools"])
        vocab.update(step["actions"])
        vocab.update(step["pains"])
    vocab = {v for v in vocab if v and v not in STOPWORDS}
    return vocab


def scan_order(plain, vocab):
    norm = normalize(plain)
    tokens = sorted(vocab, key=len, reverse=True)
    ordered = []
    index = 0
    while index < len(norm):
        hit = None
        for tok in tokens:
            if tok and norm.startswith(tok, index):
                hit = tok
                break
        if hit:
            ordered.append(hit)
            index += len(hit)
        else:
            index += 1
    return tuple(ordered), norm


def leftovers(norm, vocab):
    masked = norm
    for tok in sorted(vocab, key=len, reverse=True):
        if tok:
            masked = masked.replace(tok, " " * len(tok))
    runs = re.findall(r"[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9]{1,}", masked)
    extra = []
    for run in runs:
        token = normalize(run)
        if not token or token in STOPWORDS:
            continue
        extra.append(token)
    return extra


def bite(label, plain, actors, actor_tools, steps, vocab):
    ordered, norm = scan_order(plain, vocab)
    if not norm.strip():
        raise NotParsed("%s 抽出 0 個字" % label)
    failures = []
    known_people = set(actors) | {s["who"] for s in steps}
    known_tools = set(actor_tools)
    for step in steps:
        known_tools.update(step["tools"])
    prev_tool_pos = -1
    for index, step in enumerate(steps, 1):
        if step["who"] not in norm:
            failures.append("%s 缺 Journey 第 %d 步的誰「%s」" % (label, index, step["who"]))
        tool_positions = []
        for tool in step["tools"]:
            pos = norm.find(tool)
            if pos < 0:
                failures.append(
                    "%s 缺 Journey 第 %d 步的工具「%s」" % (label, index, tool)
                )
            else:
                tool_positions.append(pos)
        if tool_positions:
            here = min(tool_positions)
            if here < prev_tool_pos:
                failures.append(
                    "%s Journey 第 %d 步工具順序早於前一步(步序不一致)"
                    % (label, index)
                )
            prev_tool_pos = here
    extra = leftovers(norm, vocab)
    for token in extra:
        if token in known_people or token in known_tools:
            continue
        if any(token in k or k in token for k in known_people | known_tools):
            continue
        failures.append("%s 多出人／工具「%s」,對不上 Actors／Journey" % (label, token))
    return ordered, failures


def check_pair(md_path, html_path, tag):
    if not os.path.isfile(md_path):
        raise NotParsed("缺 %s" % md_path)
    if not os.path.isfile(html_path):
        raise NotParsed("缺 %s" % html_path)
    md = open(md_path, encoding="utf-8").read()
    html_text = open(html_path, encoding="utf-8").read()
    actors, actor_tools = parse_actors(md)
    steps = parse_journey(md)
    _title, md_fig = diagram_body_md(md)
    html_fig = extract_scan_now(html_text)
    vocab = vocab_from(actors, actor_tools, steps)
    print("[%s] actors=%s steps=%d" % (tag, ",".join(actors), len(steps)))
    md_order, md_fail = bite(
        tag + " md現況圖", md_fig, actors, actor_tools, steps, vocab
    )
    html_plain = diagram_plain(html_fig)
    html_order, html_fail = bite(
        tag + " html#scan-now", html_plain, actors, actor_tools, steps, vocab
    )
    failures = md_fail + html_fail
    if md_order != html_order:
        failures.append(
            "%s md 現況圖與 html #scan-now 指紋不同\n    md:%s\n    html:%s"
            % (tag, " → ".join(md_order) or "(空)", " → ".join(html_order) or "(空)")
        )
    if failures:
        raise Mismatch("\n".join(failures))
    print("[%s] md=%s" % (tag, " → ".join(md_order)))
    print("[%s] html=%s" % (tag, " → ".join(html_order)))


def check_live():
    if not os.path.isdir(FIX_DIR):
        raise NotParsed(
            "缺正例目錄 scripts/fixtures/devtalk-fig-journey/good/"
            "(html-scan 樣張不夠,必須另開目錄)"
        )
    check_pair(FIX_MD, FIX_HTML, "fixture")


def copy_tree(dst):
    dest_md = os.path.join(
        dst, "scripts", "fixtures", "devtalk-fig-journey", "good", "1-discussion.md"
    )
    dest_html = os.path.join(
        dst, "scripts", "fixtures", "devtalk-fig-journey", "good", "1-discussion.html"
    )
    os.makedirs(os.path.dirname(dest_md), exist_ok=True)
    shutil.copy(FIX_MD, dest_md)
    shutil.copy(FIX_HTML, dest_html)


def child_rc(tree):
    proc = subprocess.run(
        ["bash", self_script, "--skip-mutation", tree],
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout or "") + "\n" + (proc.stderr or "")


def replace_in_section(text, heading_substr, old, new, label):
    found = headings(text)
    for index, (start, end, title) in enumerate(found):
        if heading_substr not in title:
            continue
        body_end = found[index + 1][0] if index + 1 < len(found) else len(text)
        body = text[end:body_end]
        if old not in body:
            raise Mismatch("破壞實驗 %s 找不到 %r" % (label, old))
        body = body.replace(old, new, 1)
        return text[:end] + body + text[body_end:]
    raise Mismatch("破壞實驗找不到節 %s" % label)


def run_mutations():
    failures = []

    with tempfile.TemporaryDirectory(prefix="devtalk-fj-good-") as tmp:
        copy_tree(tmp)
        rc, blob = child_rc(tmp)
        if rc == 0:
            print("[mut] ✓ 好樣本複本綠")
        else:
            failures.append("好樣本複本必須綠,實際 rc=%s\n%s" % (rc, blob[-1200:]))

    with tempfile.TemporaryDirectory(prefix="devtalk-fj-tool-") as tmp:
        copy_tree(tmp)
        path = os.path.join(
            tmp, "scripts", "fixtures", "devtalk-fig-journey", "good", "1-discussion.md"
        )
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text, "Current Journey", "| Excel |", "| Google試算表 |", "Journey 工具"
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            open(path, "w", encoding="utf-8").write(text)
            rc, blob = child_rc(tmp)
            if rc == 1:
                print("[mut] ✓ 改 Journey 的工具不改圖必須紅")
            else:
                failures.append(
                    "改 Journey 工具不改圖必須 exit 1,實際 rc=%s\n%s"
                    % (rc, blob[-1200:])
                )

    with tempfile.TemporaryDirectory(prefix="devtalk-fj-role-") as tmp:
        copy_tree(tmp)
        path = os.path.join(
            tmp, "scripts", "fixtures", "devtalk-fig-journey", "good", "1-discussion.md"
        )
        text = open(path, encoding="utf-8").read()
        try:
            text = replace_in_section(
                text, "現況圖", "負責業務", "倉管", "現況圖角色"
            )
        except Mismatch as exc:
            failures.append(str(exc))
        else:
            open(path, "w", encoding="utf-8").write(text)
            rc, blob = child_rc(tmp)
            if rc == 1:
                print("[mut] ✓ 改圖上的角色不改 Journey 必須紅")
            else:
                failures.append(
                    "改圖上的角色不改 Journey 必須 exit 1,實際 rc=%s\n%s"
                    % (rc, blob[-1200:])
                )

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

print("✅ PASS:現況圖對 Actors／Current Journey 指紋 + 破壞實驗全過")
sys.exit(0)
PY
