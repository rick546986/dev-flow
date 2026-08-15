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

exit code:0 = 產出成功 / 1 = 解析不到內容或條數不符 / 2 = 用法錯誤、檔案讀不到、
           相依 markdown-it-py 缺失或版本不符
"""
import html
import os
import pathlib
import re
import sys

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

# ── 相依 gate ──────────────────────────────────────────────────────────────
# 解析層(fence 遮蔽、章節切割)的判斷來源是 markdown-it-py 的 CommonMark
# token stream,不是手刻正則(理由見 mask_fenced/sections 的 docstring)。
# 這支工具會被散發到採用專案,缺相依或版本不對時**不吐 traceback、不靜默
# 降級回正則**——降級等於讓兩邊 diverge 卻不吭聲,比直接擋下來更危險。
_MDIT_REQUIRED = "4.0.0"
_MDIT_REQ_FILE = _SCRIPT_DIR / "requirements-methodology-render.txt"
# 散發副本(docs/dev/tools/build-gate-twin.py)身邊沒有 requirements-methodology-render.txt
# ——那個檔只活在 scripts/。訊息固定指它會在散發副本上指向一個不存在的路徑,所以
# 只有它真的在 `_SCRIPT_DIR` 旁邊時才提,否則只給通用的 pip install 一行。
_MDIT_HINT = (
    f"請跑 pip install -r {_MDIT_REQ_FILE}(或 pip install 'markdown-it-py==4.0.0')"
    if _MDIT_REQ_FILE.is_file()
    else "請跑 pip install 'markdown-it-py==4.0.0'"
)
try:
    from markdown_it import MarkdownIt, __version__ as _MDIT_VERSION
except ImportError:
    print(f"缺相依 markdown-it-py:{_MDIT_HINT}", file=sys.stderr)
    sys.exit(2)
if _MDIT_VERSION != _MDIT_REQUIRED:
    print(f"缺相依 markdown-it-py(需要 {_MDIT_REQUIRED},目前是 {_MDIT_VERSION}):{_MDIT_HINT}",
          file=sys.stderr)
    sys.exit(2)

sys.path.insert(0, str(_SCRIPT_DIR))
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
# ⚠️ 用 `[ \t]` 不用 `\s` —— `\s` 含換行,標題後若全是空白(fence 遮蔽後就是這樣)
# 會跨行吃到很遠,整節 body 變空字串再被靜默丟掉(2026-08-15 二次複審 P4,
# 已實際發生在出貨的 7-review.html:`## 變更架構圖` 整節不見)。
H_ANY = re.compile(r"^(#{2,6})[ \t]+([^\n]*?)[ \t]*$", re.M)
# ⚠️ 同 H_ANY 的理由,同一類 bug:用 `[ \t]` 不用 `\s` —— `#### S-1`(無尾隨標題文字)
# 時 `\s*` 會跨行吃到下一行(通常是 `- GIVEN …`),把 GIVEN 欄整段吞進標題文字,
# GIVEN 欄從此消失(P4 同類,2026-08-15 三次複審抓到,已實際發生在母版範例的
# S-1:產出的 twin 裡 GIVEN 出現 0 次、卡標題是被吞的 GIVEN 文字)。
S_HEAD = re.compile(r"^#{2,6}[ \t]*(S-\S+)[ \t]*(.*)$", re.M)
R_HEAD = re.compile(r"^#{2,6}[ \t]*(R-\d+)[ \t]*[:：·]?[ \t]*(.*)$", re.M)
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
    """把 fenced code block 換成等長空白,讓標題/欄位 regex 掃不到裡面的假標題。

    位移完全保留(等長替換),所以在遮蔽版上取到的 index 可直接切原文。

    判斷來源:markdown-it-py(CommonMark 合規 parser)的 token stream —— 只信
    `token.type == "fence"` 的 `token.map` 行範圍(含開閉圍欄行;未閉合時
    parser 自己會把 map 一路算到檔尾,見 main 的未閉合偵測)。舊版靠手刻正則
    逐行維護一顆 parity 開關,三輪審查抓出 P1(巢狀圍欄:四個反引號包三個
    反引號,前綴 toggle 誤判成「內層也是 fence」)、P2(未閉合圍欄吃掉呼叫端
    接上去的 frontmatter)、P4(正則的 `$`/`\\s` 跨行語意錯位)—— 這類「什麼
    算 fence、收尾字元/長度對不對」的判斷,合規 parser 本來就會做對,不必
    再刻一次正則狀態機去追平 CommonMark 的圍欄規則。

    刻意選擇:只遮 `fence`(``` / ~~~ 圍欄式),**不遮 `code_block`**
    (4 格縮排式)—— 舊版正則的 opener 判斷只認圍欄開頭字元,縮排式從來
    沒被遮蔽過;現在若連縮排式也遮,會把「原樣保留」變成「被清空」,
    直接打破 byte-identical 的驗收基準,所以刻意不遮。
    """
    lines = md.splitlines(keepends=True)
    fence_lines = set()
    for tok in MarkdownIt("commonmark").parse(md):
        if tok.type == "fence" and tok.map:
            fence_lines.update(range(tok.map[0], tok.map[1]))

    def blank(ln):
        return (" " * (len(ln) - 1) + "\n") if ln.endswith("\n") else " " * len(ln)

    return "".join(blank(ln) if i in fence_lines else ln for i, ln in enumerate(lines))


def _closer_ok(line, ch, n):
    """`line` 是不是給定字元/長度的合法 fence 收尾:同種字元、長度 ≥ opener、縮排 ≤3。"""
    body = line.rstrip("\r\n")
    return bool(re.match(r"^ {0,3}" + re.escape(ch) + "{" + str(n) + ",}[ \t]*$", body))


def _unclosed_fences(md):
    """回傳『延伸到檔尾且未被合法收尾』的 fence token 清單(main 的未閉合警告用)。

    取代舊版「fence opener 數 % 2」的奇偶啟發式 —— parity 只能猜「大概有幾個
    沒收尾」,猜不出「是哪一個、收尾字元/長度對不對」,而且巢狀圍欄一多就會
    整個猜錯。現在直接問 parser:某個 fence 的 `token.map` 一路算到檔尾,且
    檔尾那一行不構成合法 closer(字元同種、長度 ≥ opener、縮排 ≤3),才算
    未閉合 —— 這與『收尾字元/長度/縮排在 CommonMark 裡合不合法』用的是同一套
    規則,不是另外猜的。
    """
    lines = md.splitlines(keepends=True)
    out = []
    for tok in MarkdownIt("commonmark").parse(md):
        if tok.type != "fence" or not tok.map:
            continue
        start, end = tok.map
        if end != len(lines):
            continue  # 有合法收尾且非檔尾,略過
        ch, n = tok.markup[0], len(tok.markup)
        last_line = lines[end - 1] if end > start else ""
        if not _closer_ok(last_line, ch, n):
            out.append(tok)
    return out


def sections(md):
    """依標題切段,回 [(level, title, body), ...]。

    body 是**含子標題**的整段(延伸到下一個同級或更高級標題為止)——
    `### R-1` 底下的 `#### S-1` 必須留在 R 的 body 裡,否則一條 S 都解析不到。

    候選標題來源:同一次 parse 拿到的 `heading_open` token,過濾條件是
    (a) `token.markup` 以 `#` 開頭(排除 setext,`===`/`---` 那種)
    (b) level 2-6。圍欄內的假標題(```/~~~ 包住的 `### 假標題`)在 parser
    眼裡本來就不構成 heading——連 token 都不會產生,不必再靠遮蔽版排除
    (這正是換掉手刻正則的目的:讓「什麼算標題」交給合規 parser 判斷)。

    每個候選 heading 仍用既有的 H_ANY 對它**原始碼那一行**做一次 match:
    match 不到就跳過(維持舊版對「無標題文字」這類寫法的排除行為),
    match 到就用它取 title(語意不變,含尾隨 `##` 等裝飾)。body 的 char
    span 演算法維持舊版:從該行 H_ANY match 的結尾切到下一個同級或更高級
    標題的行首,沒有就切到檔尾;body 一律取原文(零刪減)。行號→char
    offset 用行首 offset 的前綴和換算。
    """
    lines = md.splitlines(keepends=True)
    line_start = [0] * (len(lines) + 1)
    for i, ln in enumerate(lines):
        line_start[i + 1] = line_start[i] + len(ln)

    heads = []  # [(lvl, title, line_head_offset, body_start_offset), ...]
    for tok in MarkdownIt("commonmark").parse(md):
        if tok.type != "heading_open" or not tok.markup.startswith("#") or not tok.map:
            continue
        lvl_tag = int(tok.tag[1:])
        if not (2 <= lvl_tag <= 6):
            continue
        i = tok.map[0]
        m = H_ANY.match(lines[i])
        if not m:
            continue
        lvl = len(m.group(1))          # 層級語意維持舊版:來自 H_ANY 的 match,不是 token.tag
        heads.append((lvl, m.group(2), line_start[i], line_start[i] + m.end()))

    out = []
    for idx, (lvl, title, _line_off, body_start) in enumerate(heads):
        end = len(md)
        for nxt_lvl, _t, nxt_line_off, _b in heads[idx + 1:]:
            if nxt_lvl <= lvl:
                end = nxt_line_off
                break
        out.append((lvl, title, md[body_start:end]))
    return out


def table_rows(body):
    """把一個章節裡的 markdown 表格拆成 [(header, [cells]), ...];沒有表格回 []。

    ``` 區塊裡的表格不算(2026-08-15 複審 N2:Owner Calls 節內的程式碼範例寫
    `| OC-9 | 待裁決 |`,會多出幻影卡並把計數從 1/1 變成 1/3)。
    遮蔽版與原文等長且行數相同,所以用遮蔽版判斷、用原文取內容。
    """
    raw = body.splitlines()
    masked = mask_fenced(body).splitlines()
    header, rows = None, []
    for i, mln in enumerate(masked):
        if not mln.lstrip().startswith("|"):
            continue
        ln = raw[i].rstrip()
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
    """一張待審卡。missing 有值 → 紅底現形(缺必填欄的項目不得只在別處列表)。

    missing 可以是單一欄名字串(既有用法,如 2-decision 的「裁決」)或缺欄清單
    (K-7:4-spec 的 GIVEN/WHEN/THEN/觀測皆必填,同一張卡可能同時缺好幾欄)——
    清單用頓號連接,如 `缺「GIVEN、觀測」欄`;只缺一欄時仍是 `缺「觀測」欄`
    這種單欄格式(動線頂區的 n_obs 計數靠這個字串,見 dash_cells)。
    """
    tag_html = f'<span class="tag main">{html.escape(tag)}</span>' if tag else ""
    body_rows = "".join(
        f'<div class="gwt-row"><span class="gwt-k">{html.escape(k)}</span>'
        f'<span class="gwt-v">{inline(v)}</span></div>'
        for k, v in rows if v
    )
    if missing:
        label = "、".join(missing) if isinstance(missing, (list, tuple)) else missing
        flag = (f'<div class="obs missing"><span class="obs-k">缺「{html.escape(label)}」欄</span>'
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

    這個小型渲染器本身仍刻意手刻、不呼叫 markdown-it-py —— 它只做展示用的
    表格/清單/程式碼區塊轉換,職責跟解析層(判斷 fence 邊界、切章節)不同,
    沒必要為了展示格式也綁進 parser 的 token stream。
    模組層級已不是「不依賴外部套件」:解析層(mask_fenced/sections/未閉合
    偵測)判斷來源是 markdown-it-py 的 token stream,缺相依會在模組頂端的
    gate 直接 exit 2(見檔案開頭)。表格必須渲染成真表格:置頂節(限制聲明/
    Verdict/Known Limits)幾乎都是表格,用 <pre> 顯示等於沒給人看。
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
        # 遮蔽版與原文**等長**,所以在遮蔽版上取到的 index 可以直接切原文。
        # ⚠️ 不要對兩份各 split 一次再用同一個 i 取值 —— 段數不同會錯位,
        # 結果是審查者讀到 ``` 區塊裡的假 GIVEN/WHEN/THEN 而且毫無警告
        #(2026-08-15 複審 N1:那正是本檔前一版引入的 bug)。
        masked_body = mask_fenced(body)
        hits = list(S_HEAD.finditer(masked_body))
        inner = []
        for k, hm in enumerate(hits):
            sid, stitle = hm.group(1), hm.group(2).strip()
            start = hm.end()
            end = hits[k + 1].start() if k + 1 < len(hits) else len(body)
            seg_masked = masked_body[start:end]
            # K-7:模板要求 GIVEN/WHEN/THEN/觀測四欄皆必填,缺任何一欄都要紅底現形,
            # 不是只有「觀測」。FIELD 的 key 順序(given/when/then/observe)固定就是
            # GIVEN、WHEN、THEN、觀測這個守衛靠的順序,不必另外排序。
            f, missing_fields = {}, []
            FIELD_LABEL = {"given": "GIVEN", "when": "WHEN", "then": "THEN", "observe": "觀測"}
            for key, pat in FIELD.items():
                fm = pat.search(seg_masked)          # 掃遮蔽版(fence 內不算)
                f[key] = body[start + fm.start(1):start + fm.end(1)].strip() if fm else ""
                if not f[key]:
                    missing_fields.append(FIELD_LABEL[key])
            inner.append(card(
                sid, stitle or rname, "",
                [("GIVEN", f["given"]), ("WHEN", f["when"]), ("THEN", f["then"])],
                missing=missing_fields or None,
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
    masked = mask_fenced(md)                    # ``` 區塊裡的假欄位不算(複審 N2)
    m = re.search(pattern, masked, re.M)
    if not m:
        return default
    raw_val = md[m.start(1):m.end(1)]           # 等長遮蔽 → index 可直接切原文
    v = re.split(r"[()（）#|]|——|\s{2,}", raw_val.strip())[0].strip(" `*,、。")
    return v or default


_ANCHOR_SEEN = {}


def anchor_id(title):
    """章節標題 → 穩定的 html id(給動線格跳轉用)。撞名補序號(複審 N6)。"""
    base = "sec-" + re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "-", title).strip("-")[:48]
    for k, v in _ANCHOR_SEEN.items():
        if v == title:
            return k                     # 同一個標題永遠同一個 id(冪等,不論被呼叫幾次)
    if base in _ANCHOR_SEEN:
        i = 2
        while f"{base}-{i}" in _ANCHOR_SEEN:
            i += 1
        base = f"{base}-{i}"
    _ANCHOR_SEEN[base] = title
    return base


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


def _sample_row(md):
    """P5:7-review「抽驗」格的值 —— 決定論從 Coverage Matrix 抽一列,不是隨機。

    抽樣規則刻意不用 random/時間:同一份 md 每次重跑都要抽到同一列(產出必須
    可重現,否則審查者兩次看到不同的「抽驗」目標,對不上就沒有意義)。抽法:
    取 `rows[len(rows)//2]`(中位列),值 = 該列第一欄,超過 14 字截斷加「…」。
    無表格或無列 → `"—"`。
    """
    rows = table_rows(_section_text(md, "Coverage Matrix"))
    if not rows:
        return "—"
    _header, cells = rows[len(rows) // 2]
    val = cells[0] if cells else ""
    return (val[:14] + "…") if len(val) > 14 else (val or "—")


def dash_cells(stage, md, n_items, n_bad, secs, n_obs=0):
    """五格內容依 stage 不同(README §6 的表)。**格數固定五格,每格都要有跳轉目標**。

    回 [(標籤, 值, 註, 錨點), ...]。錨點是章節標題或固定 id;main 會檢查目標
    存不存在,不存在就退回 `#cards`(待審區)—— 規格要求「每格一句話 + 一個跳轉」,
    沒有跳轉就不算做到(2026-08-15 獨立審查 H1)。

    n_obs:4-spec 專用(K-7)—— 缺「觀測」欄的張數(main 用 `cards.count('觀測」欄')`
    算,觀測固定排最後,這個字串只在缺觀測時出現)。跟 n_bad(任何一欄缺、卡片紅底
    的總張數)分開算,是因為「待審 S」格的註要先報缺觀測(G3 驗收的唯一依據),
    沒有缺觀測但有其他紅卡時才退而求其次報「缺必填欄」。
    """
    def sec_anchor(*names):
        for _l, title, _b in secs:
            if any(title.startswith(n) for n in names):
                return "#" + anchor_id(title)
        return "#cards"

    if stage == "4-spec":
        dd_sec = _section_text(md, "Drafting Decisions")
        # DD 可能是表格(| DD-1 |)也可能是 bullet 清單(母版模板就是清單、無編號)
        dd_rows = re.findall(r"^\|\s*DD-\d+", mask_fenced(dd_sec), re.M) or \
            re.findall(r"^\s*[-*]\s+\S", mask_fenced(dd_sec), re.M)
        dd_open = len(re.findall(r"待裁決", mask_fenced(dd_sec)))
        if n_obs:
            s_note = f"{n_obs} 條缺觀測欄"
        elif n_bad:
            s_note = f"{n_bad} 條缺必填欄"
        else:
            s_note = "欄位齊全"
        return [
            ("狀態", _find(md, r"^status:\s*(\S+)"), "frontmatter", "#top"),
            ("待審 S", f"{n_items} 條", s_note, "#cards"),
            ("lane · Risk", f'{_find(md, r"^\s*-?\s*lane:\s*(\S+)")} · '
                            f'{_find(md, r"^\s*-\s*Risk:\s*(\S+)")}',
             "Verification Profile", sec_anchor("Verification Profile")),
            ("DD 進度", f"{len(dd_rows) - dd_open}/{len(dd_rows)}" if dd_rows else "—",
             "全裁決才可送審", sec_anchor("Drafting Decisions")),
            ("Demo verdict", _find(md, r"Human verdict:\s*(\S+)"),
             "來自 3-prototype", sec_anchor("Verification Profile", "Acceptance")),
        ]
    if stage == "2-decision":
        oc_sec = _section_text(md, "Owner Calls")
        oc_total = len(re.findall(r"^\|\s*OC-\d+", mask_fenced(oc_sec), re.M))
        oc_open = len(re.findall(r"^\|\s*OC-\d+.*待", mask_fenced(oc_sec), re.M))
        rej_sec = _section_text(md, "Rejected Alternatives")
        rej = len(re.findall(r"^\s*[-*]\s+\S", mask_fenced(rej_sec), re.M))
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
    known = len(re.findall(r"^\s*[-*|]\s*\S", mask_fenced(known_sec), re.M))
    ec = re.findall(r"^\s*-\s*\[( |x|X)\]", mask_fenced(_section_text(md, "Exit Checklist")), re.M)
    apx = _section_text(md, "附錄")
    disputes = len(re.findall(r"^#{3,6}\s*A\d", mask_fenced(apx), re.M))
    return [
        ("判定", _find(md, r"^verdict:\s*(\S+)"), "frontmatter verdict", sec_anchor("Verdict")),
        ("出貨", f"{sum(1 for m in ec if m.lower() == 'x')}/{len(ec)}" if ec else "—",
         "Exit Checklist", sec_anchor("Exit Checklist")),
        ("爭點", f"{disputes} 條", "附錄:本輪特有", sec_anchor("附錄")),
        ("風險", f"{known} 條", "Known Limits", sec_anchor("Known Limits")),
        ("抽驗", _sample_row(md), "對得上才信剩下的", sec_anchor("Coverage Matrix")),
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
    # 未閉合的 fence 會把其後全部內容吃成程式碼(規則正確,但不得靜默 —— 二次複審 P3)。
    # 判定「未閉合」用 token-based(見 _unclosed_fences);swallowed 行數計算沿用舊版
    # (遮蔽版與原文逐行比,任何被清空的非空行都算——不只算未閉合那個 fence 自己的)。
    _mk = mask_fenced(md)
    swallowed = sum(1 for a, b in zip(md.splitlines(), _mk.splitlines())
                    if a.strip() and not b.strip())
    if swallowed and _unclosed_fences(md):
        print(f"⚠️  偵測到**未閉合**的 code fence:其後 {swallowed} 行非空內容被當成程式碼,"
              f"不會進待審區也不會進背景資料。請補上收尾的 ``` 或 ~~~。", file=sys.stderr)

    fm = re.match(r"\A---\n(.*?)\n---\n", src.read_text(encoding="utf-8"), flags=re.S)
    fm_text = fm.group(1) if fm else ""
    secs = sections(md)

    cards, n_items, used = PARSERS[stage](md, secs)
    rendered_rids = re.findall(r'<section class="r-block" id="(R-\d+)"', cards)
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
    n_obs = cards.count('觀測」欄')  # K-7:缺「觀測」欄的張數(觀測固定排最後,見 card())
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
    appendix, skipped, dropped = [], [], []
    for lvl, title, body in secs:
        if lvl > 2 or title in used or not body.strip():
            continue
        if R_HEAD.match("#" * lvl + " " + title):
            continue
        masked = mask_fenced(body)
        # 只跳過「已經整段被渲染成卡片」的父節(例:`## ADDED Requirements` 底下就是全部 R/S)。
        # 判準用**已渲染的 R id**,不是任何長得像 R/S 的字 —— 否則
        # `## Known limits` 底下寫一個 `### S-1 的已知限界` 就會讓整節連同內容消失,
        # 而且一個字都不印(2026-08-15 複審 N3)。
        # 判準:該節底下**直接就是那些 R 的標題行**(例:`## ADDED Requirements`)。
        # 不能用「內文提到 R-1」—— 那會讓任何提到需求編號的背景節整段消失,
        # 而且 `R-1 in "R-10"` 還會子字串誤中(2026-08-15 二次複審 N3)。
        heads_here = {m.group(1) for m in R_HEAD.finditer(masked)}
        if stage == "4-spec" and rendered_rids and heads_here >= set(rendered_rids):
            dropped.append(title)
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
    if dropped:
        print(f"NOTE: 以下父節的內容已整段渲染成卡片,不重複顯示:{dropped}", file=sys.stderr)

    raw_cells = dash_cells(stage, fm_text + "\n" + md, n_items, n_bad, secs, n_obs)
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
