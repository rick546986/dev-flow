#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate twin 產生器 —— 把 gate 站的 md 正本轉成**審查介面**(README §6)。

三個 gate 站的 twin 不是「md 的視覺版」,是給人**審**的介面。規格見 README §6
〈審查動線頂區〉與各模板頂註;本檔是那份規格的實作。

    用法:build-gate-twin.py <專案根目錄> <slug> <stage>
         stage ∈ 2-decision | 4-spec | 7-review

    輸出兩份(**同一份內容,兩種殼**):
      <根>/docs/dev/<slug>/<stage>.html                  本機看的完整 html 文件
      <根>/docs/dev/<slug>/<stage>-review.artifact.html  發布用片段,**無**
                                                          doctype/html/head/body
    也可用環境變數:DEVFLOW_PROJECT_ROOT / DEVFLOW_SLUG / DEVFLOW_ARTIFACT_OUT

三件必含(缺一就不是審查介面):
  ①動線頂區五格,每格一句話 + 可點跳轉  ②待審項目逐條可勾 + 進度計數,缺必填欄直接紅底
  ③背景資料收進 <details>,預設收合、內容零刪減

**不手抄**:所有卡片由 md 逐條解析而來,所以不會與正本漂移。
解析不到任何一條待審項目 → exit 1(不產出空殼)。想釘死條數 → 設 DEVFLOW_EXPECT_ITEMS。

標題 pattern 刻意放寬到 `^#{2,6}`,與 `scripts/check-spec-gate.sh` 的
`S_HEAD = ^#{2,6}\\s*S-\\S+` 對齊 —— 母版範例寫 `#### S-1`、採用專案有寫
`### S-1.1 標題` 的,兩種都要吃得到,否則同一份 spec 會出現「G2 關卡過了但 twin 產不出來」。

exit code:0 = 產出成功 / 1 = 解析不到內容或條數不符 / 2 = 用法錯誤、檔案讀不到
"""
import html
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import devflow_twin_ui as ui  # noqa: E402  # type: ignore[import-not-found]

STAGES = ("2-decision", "4-spec", "7-review")

# 這些節**永遠不摺疊**:它們是判定本身或判定的前提,藏起來等於沒審。
# (2026-08-15 dogfood 抓到:用本工具產自己的 7-review 時,「限制聲明」與 verdict
#  被收進背景資料、`## Verdict` 整節消失 —— 最該先讀的三樣全不見。)
PINNED_PAT = re.compile(
    r"限制聲明|^Decision\b|Verdict|判定|Known Limits|已知限界|Reviewer 閱讀動線")
# `^Decision\b` 只命中 G1 的判定節,不會誤中 `Drafting Decisions` / `Split Decisions`
#(2026-08-15 獨立審查 H3:少了這條,G1 的判定被摺進背景資料 —— 與本規則自己
# 寫的「藏起來等於沒審」矛盾,而且是 dogfood 修過的同一種 bug 只修了一站。)

INLINE_MD = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*")
H_ANY = re.compile(r"^(#{2,6})\s+(.*?)\s*$", re.M)
S_HEAD = re.compile(r"^#{2,6}\s*(S-\S+)\s*(.*)$", re.M)
R_HEAD = re.compile(r"^#{2,6}\s*(R-\d+)\s*[:：·]?\s*(.*)$", re.M)
FIELD = {
    "given": re.compile(r"^\s*-\s*\*{0,2}GIVEN\*{0,2}\s*[:：]?\s*(.*)$", re.M | re.I),
    "when": re.compile(r"^\s*-\s*\*{0,2}WHEN\*{0,2}\s*[:：]?\s*(.*)$", re.M | re.I),
    "then": re.compile(r"^\s*-\s*\*{0,2}THEN\*{0,2}\s*[:：]?\s*(.*)$", re.M | re.I),
    # 觀測欄容許 `- 觀測(承接…):內容` 這種帶括號註記的寫法
    "observe": re.compile(r"^\s*-\s*\*{0,2}\s*觀測\*{0,2}[^：:\n]*[：:]\s*(.*)$", re.M),
}


def inline(text):
    """行內 markdown(只需 code 與 bold)轉 html,其餘 escape。"""
    out, pos = [], 0
    for m in INLINE_MD.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<code>{html.escape(m.group(1))}</code>")
        else:
            out.append(f"<strong>{html.escape(m.group(2))}</strong>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def mask_fenced(md):
    """把 ``` 圍起來的區塊換成等長空白,讓標題/欄位 regex 掃不到裡面的假標題。

    位移完全保留(等長替換),所以所有 regex 的 index 仍可直接切原文。
    起因(2026-08-15 獨立審查 H4):`## Test Skeletons` 裡的程式碼範例寫了
    `### R-9`/`#### S-9.1`,結果被當成真標題 —— 多出一張幻影卡污染進度分母,
    而且整節被「body 含 R/S 就跳過」的規則靜默刪掉,C3「內容零刪減」直接破功。
    """
    out, fenced = [], False
    for ln in md.splitlines(keepends=True):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            out.append(" " * (len(ln) - 1) + "\n" if ln.endswith("\n") else " " * len(ln))
            continue
        if fenced:
            out.append(" " * (len(ln) - 1) + "\n" if ln.endswith("\n") else " " * len(ln))
        else:
            out.append(ln)
    return "".join(out)


def sections(md):
    """依標題切段,回 [(level, title, body), ...]。

    body 是**含子標題**的整段(延伸到下一個同級或更高級標題為止)——
    `### R-1` 底下的 `#### S-1` 必須留在 R 的 body 裡,否則一條 S 都解析不到。
    掃描用遮蔽版(程式碼區塊內的假標題不算),切出來的 body 用原文(零刪減)。
    """
    heads = list(H_ANY.finditer(mask_fenced(md)))
    out = []
    for i, m in enumerate(heads):
        lvl = len(m.group(1))
        end = len(md)
        for nxt in heads[i + 1:]:
            if len(nxt.group(1)) <= lvl:
                end = nxt.start()
                break
        out.append((lvl, m.group(2), md[m.end():end]))
    return out


def table_rows(body):
    """把一個章節裡的 markdown 表格拆成 [(header, [cells]), ...];沒有表格回 []。"""
    lines = [l.rstrip() for l in body.splitlines()]
    header, rows = None, []
    for i, ln in enumerate(lines):
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue  # 分隔列
        if header is None:
            header = cells
            continue
        if any(cells):
            rows.append(cells)
    return [(header, r) for r in rows] if header else []


def card(item_id, title, tag, rows, missing=None, sub=""):
    """一張待審卡。missing 有值 → 紅底現形(缺必填欄的項目不得只在別處列表)。"""
    tag_html = f'<span class="tag main">{html.escape(tag)}</span>' if tag else ""
    body_rows = "".join(
        f'<div class="gwt-row"><span class="gwt-k">{html.escape(k)}</span>'
        f'<span class="gwt-v">{inline(v)}</span></div>'
        for k, v in rows if v
    )
    if missing:
        flag = (f'<div class="obs missing"><span class="obs-k">缺「{html.escape(missing)}」欄</span>'
                f'<span class="obs-v">這條審不過 —— 沒寫清楚要看哪裡</span></div>')
    else:
        flag = sub
    return f"""<article class="s-card{' bad' if missing else ''}" data-sid="{html.escape(item_id)}">
  <label class="s-head">
    <input type="checkbox" class="s-chk" data-sid="{html.escape(item_id)}">
    <span class="s-id">{html.escape(item_id)}</span>
    <span class="s-title">{inline(title)}</span>
    {tag_html}
  </label>
  <div class="s-body">
    <div class="gwt">{body_rows}</div>
    {flag}
  </div>
</article>"""


def obs_block(text):
    return (f'<div class="obs"><span class="obs-k">你要親自跑的觀測</span>'
            f'<span class="obs-v">{inline(text)}</span></div>')


def md_block(body):
    """把一段 md 轉成 html:表格、清單、程式碼區塊、段落。

    刻意不依賴外部 markdown 套件 —— 這支工具會被散發到採用專案,多一個相依就多一個
    「在別人機器上跑不起來」的理由。表格必須渲染成真表格:置頂節(限制聲明/Verdict/
    Known Limits)幾乎都是表格,用 <pre> 顯示等於沒給人看。
    """
    out, i = [], 0
    lines = body.strip("\n").splitlines()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append(f'<pre><code>{html.escape(chr(10).join(lines[i + 1:j]))}</code></pre>')
            i = j + 1
        elif ln.startswith("|"):
            j = i
            rows = []
            while j < len(lines) and lines[j].startswith("|"):
                cells = [c.strip() for c in lines[j].strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    rows.append(cells)
                j += 1
            if rows:
                head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
                body_rows = "".join(
                    "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                    for r in rows[1:])
                out.append(f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead>'
                           f"<tbody>{body_rows}</tbody></table></div>")
            i = j
        elif re.match(r"^\s*[-*]\s+", ln):
            j, items = i, []
            while j < len(lines) and re.match(r"^\s*[-*]\s+", lines[j]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[j]))
                j += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            i = j
        elif ln.strip():
            out.append(f"<p>{inline(ln)}</p>")
            i += 1
        else:
            i += 1
    return "".join(out)


# ── 各 stage 的解析器:回 (cards_html, n_items, dash_cells, used_titles) ────────

def parse_spec(_md, secs):
    """4-spec:每個 S 一張卡,缺「觀測」欄紅底。"""
    cards, n, used = [], 0, set()
    for lvl, title, body in secs:
        rm = R_HEAD.match("#" * lvl + " " + title)
        if rm is None:
            continue
        rid, rname = rm.group(1), rm.group(2)
        used.add(title)
        chunks = S_HEAD.split(mask_fenced(body))
        raw_chunks = S_HEAD.split(body)  # 內容取原文(零刪減),切點取遮蔽版
        inner = []
        for i in range(1, len(chunks), 3):
            sid, stitle = chunks[i], chunks[i + 1].strip()
            sbody = raw_chunks[i + 2] if i + 2 < len(raw_chunks) else chunks[i + 2]
            f = {}
            for key, pat in FIELD.items():
                fm = pat.search(sbody)
                f[key] = fm.group(1).strip() if fm else ""
            inner.append(card(
                sid, stitle or rname, "",
                [("GIVEN", f["given"]), ("WHEN", f["when"]), ("THEN", f["then"])],
                missing=None if f["observe"] else "觀測",
                sub=obs_block(f["observe"]) if f["observe"] else "",
            ))
            n += 1
        if inner:
            cards.append(
                f'<section class="r-block" id="{html.escape(rid)}">'
                f'<div class="r-head"><span class="r-id">{html.escape(rid)}</span>'
                f'<span><span class="r-name">{inline(rname)}</span></span></div>'
                f'{"".join(inner)}</section>')
    return "".join(cards), n, used


def parse_decision(_md, secs):
    """2-decision:每個 Approach 一張卡、每條 Owner Call 一張卡。"""
    cards, n, used = [], 0, set()
    for _lvl, title, body in secs:
        if re.match(r"^(Approaches Considered|Owner Calls|逐條裁決)", title):
            rows = table_rows(body)
            if not rows:
                continue
            used.add(title)
            inner = []
            for header, cells in rows:
                item = cells[0] if cells else ""
                if not item or item.startswith("<"):
                    continue
                keys = header[1:] + [f"欄{i}" for i in range(len(header), len(cells))]
                pairs = list(zip(keys, cells[1:]))
                miss = None
                if re.match(r"^OC-\d+", item):
                    st = next((v for k, v in pairs if "狀態" in k), "")
                    if not st or "待" in st:
                        miss = "裁決"
                inner.append(card(item, pairs[0][1] if pairs else "", "", pairs[1:], missing=miss))
                n += 1
            if inner:
                cards.append(f'<section class="r-block" id="{anchor_id(title)}">'
                             f'<div class="r-head">'
                             f'<span class="r-name">{inline(title)}</span></div>'
                             f'{"".join(inner)}</section>')
    return "".join(cards), n, used


def parse_review(_md, secs):
    """7-review:逐 S 現象證據 + Exit Checklist 逐項。"""
    cards, n, used = [], 0, set()
    for _lvl, title, body in secs:
        if not re.match(r"^(現象證據|Exit Checklist|Coverage Matrix)", title):
            continue
        rows = table_rows(body)
        inner = []
        if rows:
            used.add(title)
            for header, cells in rows:
                item = cells[0] if cells else ""
                if not item or item.startswith("<"):
                    continue
                keys = header[1:] + [f"欄{i}" for i in range(len(header), len(cells))]
                pairs = list(zip(keys, cells[1:]))
                inner.append(card(item, pairs[0][1] if pairs else "", "", pairs[1:]))
                n += 1
        else:
            checks = re.findall(r"^\s*-\s*\[( |x|X)\]\s*(.+)$", body, re.M)
            if checks:
                used.add(title)
                for i, (mark, text) in enumerate(checks, 1):
                    inner.append(card(f"EC-{i}", text, "已勾" if mark.lower() == "x" else "", []))
                    n += 1
        if inner:
            cards.append(f'<section class="r-block" id="{anchor_id(title)}">'
                         f'<div class="r-head">'
                         f'<span class="r-name">{inline(title)}</span></div>'
                         f'{"".join(inner)}</section>')
    return "".join(cards), n, used


PARSERS = {"4-spec": parse_spec, "2-decision": parse_decision, "7-review": parse_review}


# ── 動線頂區五格 ───────────────────────────────────────────────────────────────

def _find(md, pattern, default="—"):
    r"""抓一個欄位值。**只取到第一個分隔符為止** —— md 的欄位常帶括號註記
    (`lane: full(判準:…)`)、行尾註解(`verdict:  # PRE-REVIEW | …`),
    用 `\S+` 會把整串雜訊吃進動線格(2026-08-15 獨立審查 M6)。"""
    m = re.search(pattern, md, re.M)
    if not m:
        return default
    v = re.split(r"[()（）#|]|——|\s{2,}", m.group(1).strip())[0].strip(" `*,、。")
    return v or default


def anchor_id(title):
    """章節標題 → 穩定的 html id(給動線格跳轉用)。"""
    return "sec-" + re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "-", title).strip("-")[:48]


def _headline(text, limit=30):
    """一段內文 → 一句摘要:去 md 粗體/清單記號,取第一句,超長截斷。"""
    for ln in text.strip().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith(("|", "#", ">", "<!--")):
            continue
        ln = re.sub(r"[*`]", "", re.sub(r"^\s*[-*]\s+", "", ln))
        ln = re.split(r"[,。;;]", ln)[0].strip()
        return (ln[:limit] + "…") if len(ln) > limit else (ln or "—")
    return "—"


def dash_cells(stage, md, n_items, n_bad, secs):
    """五格內容依 stage 不同(README §6 的表)。**格數固定五格,每格都要有跳轉目標**。

    回 [(標籤, 值, 註, 錨點), ...]。錨點是章節標題或固定 id;main 會檢查目標
    存不存在,不存在就退回 `#cards`(待審區)—— 規格要求「每格一句話 + 一個跳轉」,
    沒有跳轉就不算做到(2026-08-15 獨立審查 H1)。
    """
    def sec_anchor(*names):
        for _l, title, _b in secs:
            if any(title.startswith(n) for n in names):
                return "#" + anchor_id(title)
        return "#cards"

    if stage == "4-spec":
        dd_sec = _section_text(md, "Drafting Decisions")
        # DD 可能是表格(| DD-1 |)也可能是 bullet 清單(母版模板就是清單、無編號)
        dd_rows = re.findall(r"^\|\s*DD-\d+", dd_sec, re.M) or \
            re.findall(r"^\s*[-*]\s+\S", dd_sec, re.M)
        dd_open = len(re.findall(r"待裁決", dd_sec))
        return [
            ("狀態", _find(md, r"^status:\s*(\S+)"), "frontmatter", "#top"),
            ("待審 S", f"{n_items} 條",
             f"{n_bad} 條缺觀測欄" if n_bad else "欄位齊全", "#cards"),
            ("lane / Risk", f'{_find(md, r"^\s*-?\s*lane:\s*(\S+)")} · '
                            f'{_find(md, r"^\s*-\s*Risk:\s*(\S+)")}',
             "Verification Profile", sec_anchor("Verification Profile")),
            ("DD 進度", f"{len(dd_rows) - dd_open}/{len(dd_rows)}" if dd_rows else "—",
             "全裁決才可送審", sec_anchor("Drafting Decisions")),
            ("Demo verdict", _find(md, r"Human verdict:\s*(\S+)"),
             "來自 3-prototype", sec_anchor("Verification Profile", "Acceptance")),
        ]
    if stage == "2-decision":
        oc_sec = _section_text(md, "Owner Calls")
        oc_total = len(re.findall(r"^\|\s*OC-\d+", oc_sec, re.M))
        oc_open = len(re.findall(r"^\|\s*OC-\d+.*待", oc_sec, re.M))
        rej_sec = _section_text(md, "Rejected Alternatives")
        rej = len(re.findall(r"^\s*[-*]\s+\S", rej_sec, re.M))
        return [
            ("判定", _headline(_section_text(md, "Decision")), "選了哪個方案",
             sec_anchor("Decision")),
            ("Owner Calls", f"{oc_total - oc_open}/{oc_total}" if oc_total else "—",
             "待裁決幾條", "#cards"),
            ("方案", f"{n_items} 項待審", f"{rej} 條駁回理由", "#cards"),
            ("駁回理由", f"{rej} 條", "Rejected Alternatives", sec_anchor("Rejected")),
            ("狀態", _find(md, r"^status:\s*(\S+)"), "frontmatter", "#top"),
        ]
    known_sec = _section_text(md, "Known Limits")
    known = len(re.findall(r"^\s*[-*|]\s*\S", known_sec, re.M))
    ec = re.findall(r"^\s*-\s*\[( |x|X)\]", _section_text(md, "Exit Checklist"), re.M)
    apx = _section_text(md, "附錄")
    disputes = len(re.findall(r"^#{3,6}\s*A\d", apx, re.M))
    return [
        ("判定", _find(md, r"^verdict:\s*(\S+)"), "frontmatter verdict", sec_anchor("Verdict")),
        ("出貨", f"{sum(1 for m in ec if m.lower() == 'x')}/{len(ec)}" if ec else "—",
         "Exit Checklist", sec_anchor("Exit Checklist")),
        ("爭點", f"{disputes} 條", "附錄:本輪特有", sec_anchor("附錄")),
        ("風險", f"{known} 條", "Known Limits", sec_anchor("Known Limits")),
        ("待審項目", f"{n_items} 條", "現象證據 + 出貨清單", "#cards"),
    ]


def _section_text(md, name):
    for _lvl, title, body in sections(md):
        if title.startswith(name):
            return body
    return ""


SCRIPT = """
(function(){
  var boxes = [].slice.call(document.querySelectorAll('.s-chk'));
  if (!boxes.length) return;
  var bar = document.querySelector('.bar i'), done = document.getElementById('done');
  var KEY = 'devflow-gate-twin:' + document.title;
  function load(){ try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e){ return {}; } }
  function save(s){ try { localStorage.setItem(KEY, JSON.stringify(s)); } catch(e){} }
  var state = load();
  function paint(){
    var n = 0;
    boxes.forEach(function(b){
      var card = b.closest('.s-card');
      if (b.checked){ n++; card.classList.add('done'); } else { card.classList.remove('done'); }
    });
    if (done) done.textContent = n;
    if (bar) bar.style.width = (n / boxes.length * 100) + '%';
  }
  boxes.forEach(function(b){
    if (state[b.dataset.sid]) b.checked = true;
    b.addEventListener('change', function(){ state[b.dataset.sid] = b.checked; save(state); paint(); });
  });
  var clr = document.getElementById('clear');
  if (clr) clr.addEventListener('click', function(){
    state = {}; save(state); boxes.forEach(function(b){ b.checked = false; }); paint();
  });
  paint();
})();
"""


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    root = pathlib.Path(args[0] if len(args) > 0
                        else os.environ.get("DEVFLOW_PROJECT_ROOT", ".")).expanduser().resolve()
    slug = args[1] if len(args) > 1 else os.environ.get("DEVFLOW_SLUG", "")
    stage = args[2] if len(args) > 2 else ""
    if not slug or stage not in STAGES:
        print(f"用法:build-gate-twin.py <專案根目錄> <slug> <stage>\n"
              f"     stage ∈ {' | '.join(STAGES)}", file=sys.stderr)
        return 2

    src = root / "docs/dev" / slug / f"{stage}.md"
    if not src.is_file():
        print(f"拒絕:讀不到 {src}", file=sys.stderr)
        return 2

    md = re.sub(r"\A---\n.*?\n---\n", "", src.read_text(encoding="utf-8"), flags=re.S)
    fm = re.match(r"\A---\n(.*?)\n---\n", src.read_text(encoding="utf-8"), flags=re.S)
    fm_text = fm.group(1) if fm else ""
    secs = sections(md)

    cards, n_items, used = PARSERS[stage](md, secs)
    if n_items == 0:
        print(f"ERROR: 一條待審項目都沒解析到 —— 檢查 {stage}.md 的標題與欄位格式"
              f"(S 標題要 `#### S-<id>`;表格要有表頭列)", file=sys.stderr)
        return 1
    expect = os.environ.get("DEVFLOW_EXPECT_ITEMS", "").strip()
    if expect and not expect.isdigit():
        print(f"拒絕:DEVFLOW_EXPECT_ITEMS 需為整數,得「{expect}」"
              f"(打錯而被靜默忽略 = 以為釘死了其實沒有)", file=sys.stderr)
        return 2
    if expect and n_items != int(expect):
        print(f"ERROR: 解析到 {n_items} 條,預期 {expect}(DEVFLOW_EXPECT_ITEMS)", file=sys.stderr)
        return 1
    n_bad = cards.count('class="s-card bad"')
    print(f"NOTE: 解析到 {n_items} 條待審項目" + (f",其中 {n_bad} 條缺必填欄" if n_bad else ""),
          file=sys.stderr)

    # 置頂節:判定本身與判定的前提,直接顯示在卡片之前,不摺疊
    pinned = []
    for lvl, title, body in secs:
        if lvl <= 2 and PINNED_PAT.search(title) and body.strip():
            pinned.append(f'<section class="pinned" id="{anchor_id(title)}">'
                          f'<h2>{inline(title)}</h2>'
                          f'<div class="doc-in">{md_block(body)}</div></section>')

    # 背景資料:沒被做成卡片的章節一律收進 details,內容零刪減。
    # 已經做成卡片的內容**不得重複出現** —— 章節本身被用過、或它底下含有已渲染的
    # R/S 標題(例:`## ADDED Requirements` 的 body 含全部 R 與 S),一律跳過。
    appendix, skipped = [], []
    for lvl, title, body in secs:
        if lvl > 2 or title in used or not body.strip():
            continue
        if R_HEAD.match("#" * lvl + " " + title):
            continue
        masked = mask_fenced(body)
        if stage == "4-spec" and (R_HEAD.search(masked) or S_HEAD.search(masked)):
            continue
        if PINNED_PAT.search(title):
            continue  # 置頂節另外處理,不摺疊
        appendix.append(
            f'<details class="doc" id="{anchor_id(title)}">'
            f'<summary><span>{inline(title)}</span></summary>'
            f'<div class="doc-in">{md_block(body)}</div></details>')
        skipped.append(title)
    if skipped:
        print(f"NOTE: 以下章節收進背景資料(預設收合、內容零刪減):{skipped}", file=sys.stderr)

    raw_cells = dash_cells(stage, md + "\n" + fm_text, n_items, n_bad, secs)
    have_ids = {anchor_id(title) for _l, title, _b in secs} | {"cards", "top"}
    cells = "".join(
        f'<a class="cell" href="{a if a.lstrip("#") in have_ids else "#cards"}">'
        f'<span class="k">{html.escape(k)}</span>'
        f'<span class="v">{html.escape(str(v))}</span>'
        f'<span class="n">{html.escape(n)}</span></a>'
        for k, v, n, a in raw_cells)

    title = f"{slug} · {stage}"
    body_html = f"""<div class="wrap" id="top">
<header class="masthead">
  <p class="eyebrow">dev-flow · {html.escape(stage)} · 審查介面</p>
  <h1>{html.escape(slug)}</h1>
  <p class="sub">正本是 <code>docs/dev/{html.escape(slug)}/{html.escape(stage)}.md</code>,
  這頁隨時可重生。<strong>審完頂區五格再決定要不要往下讀。</strong></p>
  <div class="dash">{cells}</div>
</header>
{"".join(pinned)}
<div class="progress">
  <div class="progress-in">
    <span class="count">已審 <b id="done">0</b> / {n_items} 條</span>
    <span class="bar"><i></i></span>
    <button class="btn" id="clear" type="button">清除勾選</button>
  </div>
</div>
<div id="cards">
{cards}
</div>
<h2 class="apx-h">背景資料(預設收合,內容零刪減)</h2>
{"".join(appendix)}
<footer class="foot">由 <code>scripts/build-gate-twin.py</code> 從 md 正本逐條解析產生,不手抄。</footer>
</div>"""

    out_local = root / "docs/dev" / slug / f"{stage}.html"
    out_art = pathlib.Path(os.environ.get(
        "DEVFLOW_ARTIFACT_OUT", str(root / "docs/dev" / slug / f"{stage}-review.artifact.html")))
    out_local.write_text(ui.local_page(title, ui.CSS_SPEC, body_html, SCRIPT), encoding="utf-8")
    out_art.write_text(ui.artifact_page(title, ui.CSS_SPEC, body_html, SCRIPT), encoding="utf-8")
    print(f"wrote {out_local} + {out_art} — {n_items} 條待審,{len(appendix)} 節背景資料")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
