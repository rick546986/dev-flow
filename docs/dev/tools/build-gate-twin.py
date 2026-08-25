#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate twin 產生器 —— 把 gate 站與 5-tasks 的 md 正本轉成**審查介面／執行板**(README §6)。

三個 gate 站的 twin 不是「md 的視覺版」,是給人**審**的介面;5-tasks 的 twin 不是
gate(無 G 編號、免 reviewer 核准),但一樣不是「md 直轉攤平」,是給人**照著動工**的
**執行板**(K-3,README §6「三種形狀的差別」)。規格見 README §6〈審查動線頂區〉/
〈執行板頂區〉與各模板頂註;本檔是那份規格的實作。

    用法:build-gate-twin.py <專案根目錄> <slug> <stage>
         stage ∈ 2-decision | 4-spec | 7-review | 5-tasks

    預設只寫一份本機完整文件:
      <根>/docs/dev/<slug>/<stage>.html
    發布用片段是 opt-in:只有明確設定 DEVFLOW_ARTIFACT_OUT 才呼叫
    artifact_page() 寫出(Claude Code 發布路徑);未設定時不得產出
    <stage>-review.artifact.html。片段**無** doctype/html/head/body。
    也可用環境變數:DEVFLOW_PROJECT_ROOT / DEVFLOW_SLUG / DEVFLOW_ARTIFACT_OUT

三個 gate 站三件必含(缺一就不是審查介面):
  ①動線頂區五格,每格一句話 + 可點跳轉  ②待審項目逐條可勾 + 進度計數,缺必填欄直接紅底
  ③背景資料收進 <details>,預設收合、內容零刪減
5-tasks 執行板四件必含(README §6〈執行板頂區〉):上述①③外加
  ②任務卡逐條可勾,六欄必填(Covers/Files/Verify/Blocked-by/Intent/Boundaries)
  缺任一即紅底,Owner 選配  ④依賴 DAG 由 Blocked-by 自動衍生(Kahn 拓撲分波,ASCII)

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

STAGES = ("2-decision", "4-spec", "7-review", "5-tasks")

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

# ── 5-tasks 執行板專用(K-3):章節/欄位判斷 ─────────────────────────────────
# `\b` 邊界防「T-10」被 `T-1` 子字串誤吃;`[:：]?` 額外容許「T-1: 標題」這個
# 冒號變體(規格明講兩種都要吃),這一段是**純顯示用**的裝飾切法,不影響下面
# TASK_FIELD_LINE 的機器對齊(見其 docstring)。
TASK_HEAD = re.compile(r"^(T-\d+)\b[:：]?\s*(.*)$")
# `##` 兩個字面井號、不是母版三站沿用的 `#{2,6}` 寬鬆 pattern —— 這裡刻意對齊
# `tests/parallel-stage6/contract_ref.py` 的 HEAD_RE(`^##\s+(T-\d+)\b\s*(.*)$`)。
# 5-tasks 的 T 不像 R/S 有「同一份 spec、多層標題都合法」的採用專案差異;真正會讀
# 這份 md 的 Stage 6 執行引擎只認 `##`,twin 若跟著放寬到 `###` 就會秀出一顆
# 引擎根本看不到的幽靈卡片 —— 那才是最壞的「與正本漂移」。
TASK_LEVEL = 2
TASK_REQUIRED = ("Covers", "Files", "Verify", "Blocked-by", "Intent", "Boundaries")
# 保留欄清單(含 parallel 選配欄)逐字照抄 contract_ref.py 的 FIELD_RE ——
# 理由見獨立審查:twin 若用不同的「這行算不算新欄位」判準,續行邊界判斷就可能
# 跟 Stage 6 scope guard 對同一份 md 得出不同答案(例如某行被 twin 當續行併入
# Boundaries,却被真正的 parser 認成新的 Files 欄、fail-closed 擋下)。
# `\s*-\s*` 而非 `^-\s*`:允許任意縮排,子項寫法一樣要被認成「新欄位」而不是續行。
_TASK_RESERVED = ("Covers", "Files", "Verify", "Blocked-by", "Integrate-after", "Risk",
                  "Review-mode", "Semantic-conflicts-with", "Intent", "Boundaries", "Owner")
TASK_FIELD_LINE = re.compile(
    r"^\s*-\s*(" + "|".join(_TASK_RESERVED) + r")\s*:\s*(.*?)\s*$")


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


def _unclosed_html_comment(md):
    """回傳未閉合 `<!--` 的 html_block token(沒有就回 None)—— N-4。

    CommonMark 的 html_block type-2(以 `<!--` 開頭)結束條件是某一行含 `-->`;
    找不到收尾時,parser 會把 map 一路吃到檔尾,跟 fence 未閉合是同一種病:
    後面所有內容(含其中的 level-2 標題)被併入這個 html_block,**結構塌陷**——
    章節數對不上,但 N-1 的對帳與 check-gate-twin.sh 的第 2 層都是用
    markdown-it 數節,兩邊看到的是同一份「被吞過」的 token stream,對不出破綻。
    這條警告是唯一訊號,判斷法與 _unclosed_fences 同款:直接問 token.map 是否
    被迫延伸到檔尾,不用「開合次數奇偶」這種猜的。
    """
    lines = md.splitlines(keepends=True)
    for tok in MarkdownIt("commonmark").parse(md):
        if tok.type != "html_block" or not tok.map:
            continue
        if "<!--" not in tok.content or "-->" in tok.content:
            continue
        if tok.map[1] == len(lines):  # 被迫吃到檔尾 = 沒找到收尾的 -->
            return tok
    return None


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


def card(item_id, title, tag, rows, missing=None, sub="", extra="", dup=None, lead=""):
    """一張待審卡。missing 有值 → 紅底現形(缺必填欄的項目不得只在別處列表)。

    missing 可以是單一欄名字串(既有用法,如 2-decision 的「裁決」)或缺欄清單
    (K-7:4-spec 的 GIVEN/WHEN/THEN/觀測皆必填,同一張卡可能同時缺好幾欄)——
    清單用頓號連接,如 `缺「GIVEN、觀測」欄`;只缺一欄時仍是 `缺「觀測」欄`
    這種單欄格式(動線頂區的 n_obs 計數靠這個字串,見 dash_cells)。

    dup:同一 T 內重複保留欄的欄名清單(H-1,K-3 現形)。有值 → 卡照樣紅底
    (即使 missing 為空),多印一段「重複欄「X」」的 flag,呼應
    `tests/parallel-stage6/contract_ref.py` fail-closed 時用的「重複保留欄」
    用語 —— 真正吃這份 md 的引擎會直接拒啟,twin 這裡只現形、不擋產出。
    跟 missing 的紅底旗標**並存**(同一張卡兩種問題都要看得到,不是互斥),
    只有兩者都沒有時才退回顯示 `sub`(既有行為不變)。

    extra:K-3 加的第 4 個插槽(5-tasks 的 Boundaries `<details>`)。跟 `sub` 不同 ——
    `sub` 缺欄時會被 `missing`/`dup` 的紅底 flag 蓋掉(同 K-7 邏輯:欄位缺就不演有值),
    但 Boundaries 摺疊是「不論其他欄缺不缺都要在」的必含元素,所以 `extra` 永遠
    附加在 `{flag}` 後面、不受 missing 影響。**接在同一行**(`{flag}{extra}`,
    不另起新行)是刻意的:三個既有 gate 站從不傳 `extra`,值恆為 `""`;若各自佔一行,
    模板裡固定的換行/縮排字元仍會印出來,即使插值是空字串也會讓三站的輸出多一行
    空白,直接打破「三個 gate 站渲染輸出不得變動」的驗收基準。同行拼接時空字串
    不添一字,byte-for-byte 不受影響。

    lead:4-spec 加的第 5 個插槽(「你要審什麼」)。插在 GWT **前面**。2/5/7 不傳,
    預設 `""`,與 `extra` 同一招:接在 `<div class="gwt">` 同一行前面,空字串不添一字。
    """
    tag_html = f'<span class="tag main">{html.escape(tag)}</span>' if tag else ""
    body_rows = "".join(
        f'<div class="gwt-row"><span class="gwt-k">{html.escape(k)}</span>'
        f'<span class="gwt-v">{inline(v)}</span></div>'
        for k, v in rows if v
    )
    flags = []
    if missing:
        label = "、".join(missing) if isinstance(missing, (list, tuple)) else missing
        flags.append(f'<div class="obs missing"><span class="obs-k">缺「{html.escape(label)}」欄</span>'
                     f'<span class="obs-v">這條審不過 —— 沒寫清楚要看哪裡</span></div>')
    if dup:
        dlabel = "、".join(dup) if isinstance(dup, (list, tuple)) else dup
        flags.append(f'<div class="obs missing"><span class="obs-k">重複欄「{html.escape(dlabel)}」</span>'
                     f'<span class="obs-v">同一 T 內同名保留欄出現兩次 —— 引擎(contract_ref.py)'
                     f'對此 fail-closed 拒啟,twin 僅現形不擋產出</span></div>')
    flag = "".join(flags) if flags else sub
    bad = bool(missing) or bool(dup)
    return f"""<article class="s-card{' bad' if bad else ''}" data-sid="{html.escape(item_id)}">
  <label class="s-head">
    <input type="checkbox" class="s-chk" data-sid="{html.escape(item_id)}">
    <span class="s-id">{html.escape(item_id)}</span>
    <span class="s-title">{inline(title)}</span>
    {tag_html}
  </label>
  <div class="s-body">
    {lead}<div class="gwt">{body_rows}</div>
    {flag}{extra}
  </div>
</article>"""


def obs_block(text, label="你要親自跑的觀測"):
    """高亮列(沿用 4-spec 的「觀測」樣式)。K-3 的 5-tasks Intent 借用同一個
    class(`.obs`),只換 label,不必為執行板另刻一顆視覺一樣的 block。"""
    return (f'<div class="obs"><span class="obs-k">{html.escape(label)}</span>'
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


# ── 4-spec 審查卡:作業脈絡在 R、S 是問題 + GWT + 觀測 ────────────────────────
# 人要能只看 HTML 審每一條 S。作業脈絡從該 R 下各 S 的 Operational Context 合併,
# 只在 R 頭貼一次;S 卡禁止再貼一份,也禁止「這一點在說什麼」那種複寫 GWT 的 claim。
# ⚠️ `[ \t]*` 不用 `\s*` —— `\s` 含換行,` - Operational Context:` 後面若直接換行,
# `\s*` 會把下一行 `- Actor:…` 整段吃進 rest,「誰在用」從此消失。
OC_HEAD = re.compile(r"^\s*-\s*Operational Context\s*[:：][ \t]*(.*)$", re.M)
OC_FIELD = re.compile(r"^[ \t]+-\s*([^:：\n]+)[:：]\s*(.*)$")
# 樣張五列(不是把 13 欄 OC 全攤)。空值不佔列,避免「不適用」長成空段六列。
OC_SHOW = (
    ("誰在用", ("Actor",)),
    ("他要幹嘛", ("Goal",)),
    ("他不知道", ("Missing information",)),
    ("系統外", ("Out-of-system action", "External dependency")),
    ("等待", ("Waiting/timeout behavior",)),
)
# 「這條才變的」優先看這些欄 —— 人審時真正會改判定的差,不是 Situation 換句話說。
OC_DELTA_KEYS = (
    "Goal", "Human decision", "Authority", "Actor",
    "Waiting/timeout behavior", "Out-of-system action", "Observation",
)


def _oc_norm(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def parse_oc(seg):
    """從一條 S 的本文抽出 Operational Context。

    回 None(沒寫)、`{"na": 理由}`(md 寫不適用)、或欄名→值的 dict。
    掃原文即可:OC 是給人看的欄位表,不會合法出現在 fence 裡;GWT 的 fence 遮蔽
    仍由呼叫端的 FIELD 掃描負責。
    """
    m = OC_HEAD.search(seg)
    if not m:
        return None
    rest = m.group(1).strip()
    if rest.startswith("不適用"):
        return {"na": rest}
    fields = {}
    for ln in seg[m.end():].splitlines():
        if not ln.strip():
            continue
        fm = OC_FIELD.match(ln)
        if not fm:
            if re.match(r"^\s*-\s+\S", ln) and not ln.startswith((" ", "\t")):
                break
            if fields and ln[:1].isspace():
                last = next(reversed(fields))
                fields[last] += " " + ln.strip()
            continue
        fields[fm.group(1).strip()] = fm.group(2).strip()
    return fields or None


def merge_r_oc(ocs):
    """一條 R 的作業脈絡:有一份完整 OC 就用第一份當共用底;全是不適用就一行不適用。"""
    filled = [o for o in ocs if o and "na" not in o]
    if filled:
        return dict(filled[0])
    nas = [o for o in ocs if o and "na" in o]
    if nas:
        return {"na": nas[0]["na"]}
    return None


def render_r_oc(oc):
    """R 頭底下的作業脈絡。不適用 = 一行,不要空表。"""
    if not oc:
        return ""
    if "na" in oc:
        reason = oc["na"]
        if reason == "不適用":
            body = "不適用。"
        else:
            body = reason if reason.startswith("不適用") else "不適用。" + reason
        return f'<div class="r-oc"><p class="r-oc-na">{inline(body)}</p></div>'
    rows = []
    for label, keys in OC_SHOW:
        val = ""
        for k in keys:
            v = (oc.get(k) or "").strip()
            if v and v not in ("無", "不適用"):
                val = v
                break
        if not val:
            continue
        rows.append(
            f'<div class="r-oc-row"><span class="r-oc-k">{html.escape(label)}</span>'
            f'<span class="r-oc-v">{inline(val)}</span></div>')
    if not rows:
        return ""
    return (f'<div class="r-oc"><div class="r-oc-h">作業脈絡(整條 R 共用)</div>'
            f'{"".join(rows)}</div>')


def oc_delta_line(s_oc, r_oc):
    """S 相對 R 共用脈絡只補 1 句。沒差就空字串 —— 不要為了填格子而貼。"""
    if not s_oc or not r_oc or "na" in s_oc or "na" in r_oc:
        return ""
    # 空狀態 vs 錯誤是常見洞:Observation 在講這個時,優先於 Goal 換句話說。
    sv_obs, rv_obs = _oc_norm(s_oc.get("Observation", "")), _oc_norm(r_oc.get("Observation", ""))
    if sv_obs and sv_obs != rv_obs and re.search(r"空狀態|錯誤狀態|不是錯", sv_obs):
        sent = re.split(r"[。；\n]", sv_obs, 1)[0].strip()
        if sent:
            return sent
    for key in OC_DELTA_KEYS:
        sv, rv = _oc_norm(s_oc.get(key, "")), _oc_norm(r_oc.get(key, ""))
        if sv and sv != rv:
            sent = re.split(r"[。；\n]", sv, 1)[0].strip()
            if sent:
                return sent
    return ""


def _obs_surface(obs):
    """觀測欄「從哪看」那段,用來問能不能離開 DB 驗。"""
    part = (obs or "").split("|")[0].strip()
    part = re.sub(r"^從\s*", "", part)
    part = re.sub(r"\s*看\s*$", "", part).strip()
    return part or "觀測欄寫的畫面"


def _precision_token(text):
    """THEN/觀測裡的精度字樣(「10 天」、30 天、p95 < 100ms)。"""
    m = re.search(r"「([^」]{1,16})」", text or "")
    if m and re.search(r"\d", m.group(1)):
        return m.group(1)
    m = re.search(r"(\d+\s*天|\d+\s*ms|p95)", text or "", re.I)
    return m.group(1) if m else ""


def _dd_for_precision(md, token):
    """精度字樣對得上哪一條 DD。對不到就只問「跟 DD 對得上嗎」,不寫死樣張的 DD-1。"""
    if not token or not md:
        return ""
    needle = re.sub(r"\d+", "N", token)
    for row in re.finditer(r"^\|\s*(DD-\d+)\s*\|([^|]+)\|", mask_fenced(md), re.M):
        did, what = row.group(1), row.group(2)
        if any(p in what for p in (token, needle, "精度", "天", "小時")):
            return did
    return ""


def review_questions(fields, oc, md):
    """從這條 S 的洞抽 2–3 個問題。必須是問題,不能重述 GWT。"""
    given, when, then = fields.get("given", ""), fields.get("when", ""), fields.get("then", "")
    obs = fields.get("observe", "")
    # 精度只看 THEN(斷言語)——觀測第三段常寫「用 30 天內…測」,那是測資不是精度契約。
    # 權限/歷程只看本條 THEN+觀測,不掃整份 OC(R 共用 Authority 會誤給每張 S 貼權限題)。
    own = " ".join((then, obs))
    qs = []

    def add(q):
        q = (q or "").strip()
        if not q:
            return
        if not q.endswith("？") and not q.endswith("?"):
            q += "？"
        # 禁複寫 GWT:問題不得整段搬 GIVEN/WHEN/THEN
        gwt = (given, when, then)
        if any(part and len(part) >= 8 and part in q for part in gwt):
            return
        if q not in qs:
            qs.append(q)

    surface = _obs_surface(obs)
    if obs and not re.search(r"\bDB\b|資料庫|SQL|EXPLAIN", obs, re.I):
        add(f"只看「{surface}」、不對 DB,能不能判定這條對錯")
    token = _precision_token(then)
    if token:
        dd = _dd_for_precision(md, token)
        if dd:
            add(f"「{token}」的精度是寫死的嗎?跟 {dd} 對得上嗎")
        else:
            add(f"「{token}」的精度是寫死的嗎?跟 Drafting Decisions 對得上嗎")
    if re.search(r"空狀態|不顯示錯誤|無到期|零筆|空列表", own):
        add("空狀態跟查詢失敗,觀測上分得出來嗎")
    if re.search(r"灰階|拒絕|權限|僅主管|403|授權", own):
        add("權限防線在 API,還是只在 UI 灰階")
    if re.search(r"歷程", own):
        add("只看 UI 上的歷程,能不能驗這條")
    if oc and "na" in oc:
        add("這條是單純導覽/內部行為,寫不適用的理由站得住嗎")
    if len(qs) < 2 and obs:
        add("這條觀測寫的「從哪看 / 看到什麼算對」不打開 md 能獨立判定嗎")
    if len(qs) < 2:
        add("這條不打開 4-spec.md、只看這一卡,寫到可以過 G2 了嗎")
    if len(qs) < 2:
        add("觀測離開 DB 還能單獨驗嗎?空狀態跟失敗分得出來嗎")
    return qs[:3]


def render_ask(questions, box_class="s-ask", head_class="s-ask-h"):
    """「你要審什麼」清單。4-spec 預設 s-ask;2-decision 傳 g1-ask,class 分站。"""
    if not questions:
        return ""
    items = "".join(
        f'<li><span class="qmark">?</span><span>{inline(q)}</span></li>'
        for q in questions)
    return (f'<div class="{html.escape(box_class)}">'
            f'<div class="{html.escape(head_class)}">你要審什麼</div>'
            f"<ul>{items}</ul></div>")


def s_tag(fields, oc):
    """標籤從本條 THEN/觀測抽,不寫死 S-id,也不吃 R 共用 Authority(會誤標整組)。"""
    blob = " ".join((fields.get("then", ""), fields.get("observe", "")))
    if re.search(r"灰階|僅主管|權限|拒絕|403|授權", blob):
        return "權限"
    return ""


# ── 各 stage 的解析器:回 (cards_html, n_items, dash_cells, used_titles) ────────

def parse_spec(md, secs):
    """4-spec:每個 S 一張卡,缺「觀測」欄紅底。

    卡形狀(G2 給人審,不是 md 直轉):R 頭 + 作業脈絡一次;S = 勾選 / id / 標題 /
    2–3 條「你要審什麼」+ 既有 GWT + 既有觀測 + 可選的「這條才變的」一句。
    勾選語意 = 這條寫到可以過 G2,不是審查者已跑過觀測。
    """
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
        parsed = []
        for k, hm in enumerate(hits):
            sid, stitle = hm.group(1), hm.group(2).strip()
            start = hm.end()
            end = hits[k + 1].start() if k + 1 < len(hits) else len(body)
            seg_masked = masked_body[start:end]
            seg_raw = body[start:end]
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
            parsed.append((sid, stitle, f, missing_fields, parse_oc(seg_raw)))
        r_oc = merge_r_oc([p[4] for p in parsed])
        inner = []
        for sid, stitle, f, missing_fields, s_oc in parsed:
            qs = review_questions(f, s_oc, md)
            delta = oc_delta_line(s_oc, r_oc)
            extra = ""
            if delta:
                extra = (f'<p class="s-delta"><strong>這條才變的：</strong>'
                         f"{inline(delta)}</p>")
            inner.append(card(
                sid, stitle or rname, s_tag(f, s_oc),
                [("GIVEN", f["given"]), ("WHEN", f["when"]), ("THEN", f["then"])],
                missing=missing_fields or None,
                sub=obs_block(f["observe"]) if f["observe"] else "",
                extra=extra,
                lead=render_ask(qs),
            ))
            n += 1
        if inner:
            cards.append(
                f'<section class="r-block" id="{html.escape(rid)}">'
                f'<div class="r-head"><span class="r-id">{html.escape(rid)}</span>'
                f'<span><span class="r-name">{inline(rname)}</span></span></div>'
                f'{render_r_oc(r_oc)}'
                f'{"".join(inner)}</section>')
    hint = ('<p class="g2-chk-hint">勾選 = 這條寫到可以過 G2,不是你已跑過觀測。'
            '</p>') if cards else ""
    return hint + "".join(cards), n, used


def _chosen_letter(md):
    """## Decision 選定哪一案(A/B/C)。對不到就空字串,不寫死樣張的 A。"""
    text = _section_text(md, "Decision")
    m = re.search(r"採\s*\*+([A-Z])", text)
    if m:
        return m.group(1)
    m = re.search(r"採\s+([A-Z])\b", text)
    return m.group(1) if m else ""


def _rejected_by_letter(md):
    """Rejected Alternatives 條列 → {字母: 一句棄因}。"""
    sec = _section_text(md, "Rejected Alternatives")
    out = {}
    for m in re.finditer(r"^\s*[-*]\s+([A-Z])\s*[:：]\s*(.+)$", mask_fenced(sec), re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def _bind_stage(blob):
    """從「若被推翻會怎樣」等文字判綁到哪一站,不寫死樣張 id。"""
    found = []
    for name, pat in (
        ("4-spec", r"4-spec|S-\d+|R-\d+"),
        ("3-prototype", r"3-prototype"),
        ("5-tasks", r"5-tasks|\bT-\d+"),
        ("7-review", r"7-review"),
        ("Success Criteria", r"Success Criteria"),
        ("Scope", r"\bScope\b|範圍擴大"),
    ):
        if re.search(pat, blob or ""):
            found.append(name)
    return "、".join(found)


def _oc_rejected(decided, status):
    """OC 的否決項:推翻 / 棄項括號 / 不X / 只處理 Y;寫不出就標未寫棄項。"""
    if re.search(r"✗", status or ""):
        return "原裁決被推翻"
    plain = re.sub(r"[*`]", "", decided or "")
    m = re.search(r"[（(]棄項[:：]([^)）]+)[)）]", plain)
    if m:
        return m.group(1).strip()
    m = re.search(r"不(列入|隱藏|另建|引入|做)([^，。；]{0,12})", plain)
    if m:
        return "對立面：" + m.group(1) + m.group(2).strip()
    m = re.search(r"只處理([^。；（(]{2,24})", plain)
    if m:
        return "不在範圍：" + m.group(1).strip()
    return "未寫棄項"


def render_g1_oc(md):
    """頁上一次作業脈絡。從 Decision / Scope / Success Criteria 抽,沒有就不貼。"""
    rows = []
    dec = _headline(_section_text(md, "Decision"), limit=72)
    if dec and dec != "—":
        rows.append(("選定", dec))
    scope = _section_text(md, "Scope")
    in_m = re.search(r"In\s*[:：]\s*(.+)", scope)
    out_m = re.search(r"Out\s*[:：]\s*(.+)", scope)
    if in_m:
        rows.append(("範圍", in_m.group(1).strip()))
    if out_m:
        rows.append(("不做", out_m.group(1).strip()))
    sc = _headline(_section_text(md, "Success Criteria"), limit=60)
    if sc and sc != "—":
        rows.append(("成功長這樣", sc))
    if not rows:
        return ""
    body = "".join(
        f'<div class="g1-oc-row"><span class="g1-oc-k">{html.escape(k)}</span>'
        f'<span class="g1-oc-v">{inline(v)}</span></div>'
        for k, v in rows)
    return (f'<div class="g1-oc"><div class="g1-oc-h">作業脈絡(本頁一次)</div>'
            f"{body}</div>")


def decision_review_questions(kind, decided, rejected, bind, status, extra_banned, md):
    """從 2-decision 的洞抽 2–3 問。必須是問題,不重述裁決/否決項/綁到哪一站。"""
    qs = []
    banned = [x for x in ((decided, rejected, bind) + tuple(extra_banned or ())) if x]

    def add(q):
        q = (q or "").strip()
        if not q:
            return
        if not q.endswith("？") and not q.endswith("?"):
            q += "？"
        if any(part and len(part) >= 8 and part in q for part in banned):
            return
        if q not in qs:
            qs.append(q)

    if kind == "approach":
        if status == "選定":
            add("選定這案之後還退得回去嗎")
            add("4-spec 還要走這條實作路嗎")
            add("被駁回的案在後站有沒有又被寫回來")
        else:
            add("這案被駁了,4-spec 還寫著它嗎")
            add("否決原因現在還站得住嗎")
            add("這扇門關死了,還是以後能升級回來")
    else:
        if re.search(r"✗", status or "") or "推翻" in (status or ""):
            add("原裁決已被推翻,4-spec 還留著舊寫法嗎")
        else:
            adr = _section_text(md, "ADR")
            if re.search(r"難逆轉\s*[:：]\s*是", adr):
                add("這條標了難逆轉,翻案代價還真實嗎")
            else:
                add("這條翻案只改文件,還是已經不可逆")
        if bind and "4-spec" in bind:
            add("4-spec 還依賴這條嗎?拿掉它哪一條會垮")
        else:
            add("4-spec 還要這條裁決嗎,還是只活在本站")
        add("這條否掉的做法,後站有沒有又開回來")
    if len(qs) < 2:
        add("不打開 2-decision.md、只看這一卡,G1 審得過嗎")
    if len(qs) < 2:
        add("否決項在後站是不是真的關了")
    return qs[:3]


def parse_decision(md, secs):
    """2-decision:每個 Approach 一張卡、每條 Owner Call 一張卡。

    卡形狀(G1 給人審,不是 md 直轉):頁上一次作業脈絡;每張卡留裁決、否決項、
    綁到哪一站,加 2–3 條「你要審什麼」(可不可逆、4-spec 還要不要它、否決項
    是否真的關了)。禁止「這一點在說什麼」。勾選 = 這條可以過 G1,不是已寫進 4-spec。
    """
    cards, n, used = [], 0, set()
    chosen = _chosen_letter(md)
    rejected_map = _rejected_by_letter(md)
    for _lvl, title, body in secs:
        # 只吃 L2:模板的「逐條裁決」是 Owner Calls 底下的 H3,再吃一次會複製 OC 卡。
        if _lvl != 2:
            continue
        if re.match(r"^(Approaches Considered|Owner Calls|逐條裁決)", title):
            rows = table_rows(body)
            if not rows:
                continue
            used.add(title)
            inner = []
            is_oc = bool(re.match(r"^(Owner Calls|逐條裁決)", title))
            for header, cells in rows:
                item = cells[0] if cells else ""
                if not item or item.startswith("<"):
                    continue
                keys = header[1:] + [f"欄{i}" for i in range(len(header), len(cells))]
                pairs = list(zip(keys, cells[1:]))
                extra_banned = [v for _k, v in pairs]
                if is_oc:
                    decided = pairs[0][1] if pairs else ""
                    st = next((v for k, v in pairs if "狀態" in k), "")
                    miss = None if (st and "待" not in st) else "裁決"
                    overturn = next((v for k, v in pairs if "推翻" in k), "")
                    bind = _bind_stage(" ".join((decided, overturn))) or "本站"
                    rejected = _oc_rejected(decided, st)
                    if re.search(r"✗", st):
                        ruling, tag = "推翻", "推翻"
                    elif miss:
                        ruling, tag = "待人審", ""
                    else:
                        ruling, tag = "已裁決", ""
                    qs = decision_review_questions(
                        "oc", decided, rejected, bind, st, extra_banned, md)
                    inner.append(card(
                        item, decided or item, tag,
                        [("裁決", ruling), ("否決項", rejected), ("綁到哪一站", bind)],
                        missing=miss,
                        lead=render_ask(qs, "g1-ask", "g1-ask-h"),
                    ))
                else:
                    letter_m = re.match(r"([A-Z])\b", item)
                    letter = letter_m.group(1) if letter_m else ""
                    is_chosen = bool(letter) and letter == chosen
                    summary = pairs[0][1] if pairs else item
                    rej_reason = rejected_map.get(letter, "")
                    if is_chosen:
                        ruling, tag = "選定", "選定"
                        others = "；".join(
                            f"{k}:{v}" for k, v in rejected_map.items() if k != letter)
                        rejected = others or "未列 Rejected Alternatives"
                        bind = "4-spec"
                    else:
                        ruling, tag = "駁回", ""
                        rejected = rej_reason or "未列 Rejected Alternatives"
                        bind = _bind_stage(rej_reason) or "本站"
                    qs = decision_review_questions(
                        "approach", summary, rejected, bind, ruling, extra_banned, md)
                    inner.append(card(
                        item, summary or item, tag,
                        [("裁決", ruling), ("否決項", rejected), ("綁到哪一站", bind)],
                        lead=render_ask(qs, "g1-ask", "g1-ask-h"),
                    ))
                n += 1
            if inner:
                cards.append(f'<section class="r-block" id="{anchor_id(title)}">'
                             f'<div class="r-head">'
                             f'<span class="r-name">{inline(title)}</span></div>'
                             f'{"".join(inner)}</section>')
    hint = ('<p class="g1-chk-hint">勾選 = 這條裁決可以過 G1,不是已寫進 4-spec。'
            '</p>') if cards else ""
    return hint + render_g1_oc(md) + "".join(cards), n, used


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


def parse_task_fields(body):
    """把一個 T 的 body 切成欄位。回 `(fields, dups)`:`fields` 是欄名→值的 dict,
    `dups` 是重複出現的保留欄名清單(見下方 H-1 段落)。

    欄位開始行判準(`TASK_FIELD_LINE`)逐字對齊 `tests/parallel-stage6/contract_ref.py`
    的 FIELD_RE —— 真正吃這份 md 的 Stage 6 scope guard 用同一顆正則判斷「這行是不是
    新欄位」;twin 若判準不同,可能把 Stage 6 會擋下來的一行(例如縮排的 `- Files:`
    子項)誤判成續行併入 Boundaries,審查者看到的字面跟引擎實際吃到的字面就不一致了。

    續行:比 contract_ref.py 多做一件事 —— 把後續縮排、非新欄位的行併入目前欄位
    (模板頂註「續行禁令」講的正是這個現象,例:範例 T-1 的 Boundaries 第二行
    「Design Boundary(摘自…)」)。這是 **twin 專屬的顯示加值**:contract_ref.py
    的機器消費者只讀欄位那一行(Files/Verify/Blocked-by 這些機器判準值本來就該是
    單行),但 Boundaries/Intent 是給人看的,續行內容不顯示等於白寫 —— K-3 規格
    明講「值含續行」,這裡刻意比機器解析更寬,不影響上面提到的欄位邊界對齊。
    重複保留欄(同一欄名出現兩次)保留首筆、不覆蓋 —— 對齊 contract_ref.py 的
    fail-closed 精神(它會記錯誤;twin 不擋產出,但也不能靜默選後筆)。回傳的
    第二個值 `dups` 是偵測到的重複欄名清單(依出現順序、去重)——H-1:twin 不能
    只默默保留首筆就算了事,還要讓這張卡紅底現形 + 讓 stderr 點名引擎會
    fail-closed 拒啟,不然審查者看到的 twin 是綠的,引擎卻直接拒啟同一份 md。
    掃遮蔽版(``` 區塊不算,理由同 mask_fenced);遮蔽版與原文等長,可用同一行索引切原文。
    """
    masked = mask_fenced(body)
    fields, cur, dups = {}, None, []
    for mln, rln in zip(masked.splitlines(), body.splitlines()):
        fm = TASK_FIELD_LINE.match(mln)
        if fm:
            key = fm.group(1)
            if key in fields:
                if key not in dups:
                    dups.append(key)
                cur = None       # 重複保留欄:首筆已在,忽略後筆,也不再累加續行進去
                continue
            cur = key
            fields[cur] = rln[fm.start(2):].strip()
            continue
        if cur and mln.strip() and mln[:1].isspace() and not TASK_FIELD_LINE.match(mln):
            fields[cur] += "\n" + rln.strip()
    return fields, dups


def _task_sections(secs):
    """secs 裡標題形如 `T-1 標題` / `T-1: 標題`、且標題層級為 `##`(TASK_LEVEL)的節。
    回 [(tid, title, body), ...],依 md 出現順序(sections() 本身就是順序輸出)。
    """
    out = []
    for lvl, title, body in secs:
        if lvl != TASK_LEVEL:
            continue
        m = TASK_HEAD.match(title)
        if m:
            out.append((m.group(1), title, body))
    return out


def parse_tasks(_md, secs):
    """5-tasks:每個 T 一張執行卡(README §6「執行板」,K-3)。

    六欄必填(Covers/Files/Verify/Blocked-by/Intent/Boundaries)缺任一即紅底,
    格式與機制**沿用 K-7**(card() 的 missing 清單、「缺「X」欄」字串)—— 執行板跟
    4-spec 的審查介面一樣,「缺必填欄」不能只在別處列表,必須在卡上直接現形。
    Owner 選配,不進 TASK_REQUIRED 就永遠不會觸發缺欄。
    Intent 借 obs_block 的高亮樣式(標籤換成「Intent」);Boundaries 走 card() 新加的
    `extra` 插槽,包成 `<details>`(預設收合、經 md_block 渲染、原文零刪減)——
    這正是 owner 兩次抱怨的那件事:Boundaries 常常上千字,直接攤平會把
    Covers/Files/Verify 擠到畫面外,摺起來才看得下去。

    H-1(2026-08-15 獨立審查):同一 T 內若有保留欄重複出現(常見成因是
    Boundaries/Intent 的續行被寫成 `- Files:` 這種子項),真正吃這份 md 的
    Stage 6 引擎(`tests/parallel-stage6/contract_ref.py`)fail-closed 拒啟,
    twin 卻只是「保留首筆」悄悄過關 —— 審查者看到綠卡、引擎卻拒收同一份 md。
    這裡把 `parse_task_fields` 回傳的 `dups` 接進 `card()` 的 `dup` 參數,讓卡
    照樣紅底 + flag 點名重複欄,並在 stderr 印一行 NOTE(見 main() 呼叫處)提醒
    這件事引擎會 fail-closed——twin 仍不擋產出,只現形。
    """
    cards, n, used = [], 0, set()
    for tid, title, body in _task_sections(secs):
        used.add(title)
        f, dups = parse_task_fields(body)
        missing = [k for k in TASK_REQUIRED if not (f.get(k) or "").strip()]
        rows = [(k, f.get(k, "")) for k in ("Covers", "Files", "Verify", "Blocked-by")]
        intent = f.get("Intent", "").strip()
        sub = obs_block(intent, label="Intent") if intent else ""
        bounds = f.get("Boundaries", "").strip()
        extra = ""
        if bounds:
            extra = (f'<details class="t-bound"><summary>Boundaries —— 這個 T 的硬約束與禁區'
                      f'</summary><div class="body">{md_block(bounds)}</div></details>')
        rest = title[len(tid):].strip(" :：") or tid
        cards.append(card(tid, rest, "", rows, missing=missing or None, sub=sub, extra=extra,
                          dup=dups or None))
        if dups:
            print(f"NOTE: {tid} 重複保留欄「{'、'.join(dups)}」:twin 不擋產出(只現形紅底),但真正吃這份"
                  f"md 的引擎(tests/parallel-stage6/contract_ref.py)對「重複保留欄」fail-closed 拒啟",
                  file=sys.stderr)
        n += 1
    return "".join(cards), n, used


def _task_deps(secs):
    """每個 T 的 Blocked-by 原始文字 → 依賴的 T id 清單(依 md 出現順序)。

    抽 id 用 `re.findall(r"T-\\d+", value)`,跟 contract_ref.py 的 `_extract_ids`
    同一招:`-`/`—`/`無`/空白裡都不會有 `T-\\d+` 子字串,正則本身就回空清單,
    不必另外維護一份「哪些字算空」的清單去追平那邊的 EMPTY_MARKS。
    回 [(tid, [dep_id, ...]), ...]。
    """
    out = []
    for tid, _title, body in _task_sections(secs):
        f, _dups = parse_task_fields(body)
        out.append((tid, re.findall(r"T-\d+", f.get("Blocked-by", ""))))
    return out


def build_dag(secs):
    """Blocked-by → ASCII 波次圖(Kahn 拓撲分波)。回 (html, 邊數, warnings)。

    選 Kahn 拓撲而不是手畫 SVG:README §6 自己就寫「T 依賴 DAG(ASCII 天生適合)」,
    Blocked-by 是純文字關係,拓撲序自然就是波次,不必假裝這是需要空間佈局的圖 ——
    原型(notes/patches/gate-twin-ui-prototype)手畫一張 SVG,節點/邊換一份 5-tasks
    就要重畫,還背著手刻座標的幾何缺陷風險,這正是母版化要避免的事。

    引用不存在的 T、自我引用 → 該邊被排除且列進 warnings(fail-loud,不擋產出:
    欄位本身有值,卡不因此變紅,K-3 規格明講「卡不紅」);排除法沿用
    `tests/parallel-stage6/contract_ref.py` 對同一種錯誤的判法(引用不存在 id /
    自我引用皆記錯誤,只是那邊是 fail-closed 擋 start,這裡是 fail-loud 純現形)。
    卡在剩餘節點裡走不完波次 → 環,warnings 列出環上節點,DAG 區印
    「(依賴有環:…)」,同樣不擋產出。
    """
    tasks = _task_deps(secs)
    ids = [t for t, _ in tasks]
    idset = set(ids)
    warnings = []
    deps = {}
    for tid, raw in tasks:
        clean = []
        for d in raw:
            if d == tid:
                warnings.append(f"{tid} 的 Blocked-by 引用自己,已忽略此邊")
                continue
            if d not in idset:
                warnings.append(f"{tid} 的 Blocked-by 引用不存在的 {d},已忽略此邊")
                continue
            clean.append(d)
        deps[tid] = clean

    remaining = {t: list(deps[t]) for t in ids}
    resolved = set()
    lines, wave_no = [], 0
    while remaining:
        wave_no += 1
        wave = [t for t in ids if t in remaining and all(d in resolved for d in remaining[t])]
        if not wave:
            cyc = [t for t in ids if t in remaining]
            warnings.append(f"依賴有環,卡在環裡走不完波次的 T:{'、'.join(cyc)}")
            lines.append(f"(依賴有環:{'、'.join(cyc)})")
            break
        parts = [f"{t} ←({','.join(deps[t])})" if deps[t] else t for t in wave]
        lines.append(f"Wave {wave_no}: " + "、".join(parts))
        for t in wave:
            del remaining[t]
        resolved.update(wave)

    text = "\n".join(lines) if lines else "(沒有 T,無 DAG 可畫)"
    edge_count = sum(len(v) for v in deps.values())
    html_out = (f'<section class="dag" id="dag"><h2>T 依賴 DAG(Blocked-by,自動衍生)</h2>'
                f'<pre>{html.escape(text)}</pre></section>')
    return html_out, edge_count, warnings


def _tasks_done_count(secs):
    """任務板進度:算「- [x] 完成」的張數,不是 SCRIPT 的即時勾選狀態(那個永遠從
    0 起算,見 SCRIPT 的 load()/paint())。這格是 md 正本此刻的真實完成度快照 ——
    跟 7-review「出貨」格算 Exit Checklist `- [x]` 的手法同一套(dash_cells 的
    `known_sec`/`ec` 那段),不是另外發明的機制。"""
    done, total = 0, 0
    for _tid, _title, body in _task_sections(secs):
        total += 1
        m = re.search(r"^\s*-\s*\[( |x|X)\]", mask_fenced(body), re.M)
        if m and m.group(1).lower() == "x":
            done += 1
    return done, total


PARSERS = {"4-spec": parse_spec, "2-decision": parse_decision, "7-review": parse_review,
           "5-tasks": parse_tasks}


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
        # G3(2026-08-17):分號曾是兩個半形 0x3b(本想寫「;或；」),全形分號不當截斷點。
        ln = re.split(r"[,。;；]", ln)[0].strip()
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


def dash_cells(stage, md, n_items, n_bad, secs, n_obs=0, dag_edges=0, dag_done=0):
    """五格內容依 stage 不同(README §6 的表)。**格數固定五格,每格都要有跳轉目標**。

    回 [(標籤, 值, 註, 錨點), ...]。錨點是章節標題或固定 id;main 會檢查目標
    存不存在,不存在就退回 `#cards`(待審區)—— 規格要求「每格一句話 + 一個跳轉」,
    沒有跳轉就不算做到(2026-08-15 獨立審查 H1)。

    n_obs:4-spec 專用(K-7)—— 缺「觀測」欄的張數(main 用 `cards.count('觀測」欄')`
    算,觀測固定排最後,這個字串只在缺觀測時出現)。跟 n_bad(任何一欄缺、卡片紅底
    的總張數)分開算,是因為「待審 S」格的註要先報缺觀測(G3 驗收的唯一依據),
    沒有缺觀測但有其他紅卡時才退而求其次報「缺必填欄」。

    dag_edges/dag_done:5-tasks 專用(K-3)。main() 只算一次 `build_dag()`/
    `_tasks_done_count()` 並把數字傳進來,不在這裡重算 —— 否則同一份 md 的
    DAG 警告(引用不存在的 T / 有環)會被印兩次 stderr NOTE(一次來自 main() 產
    `#dag` 區塊,一次來自這裡重新解析),對著同一個問題喊兩次沒有增加資訊量。
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
        lane_val = _find(md, r"^\s*-?\s*lane:\s*(\S+)")
        risk_val = _find(md, r"^\s*-\s*Risk:\s*(\S+)")
        return [
            ("狀態", _find(md, r"^status:\s*(\S+)"), "frontmatter", "#top"),
            ("待審 S", f"{n_items} 條", s_note, "#cards"),
            # ⚠️ 兩個查詢先落成變數再進 f-string:Python 3.11 及更早**不允許**
            # f-string 的表達式部分含反斜線,而正則裡有 `\s`/`\S`。寫在 f-string 裡
            # 會在 3.9(macOS 內建 /usr/bin/python3)直接 SyntaxError —— 整支檔案讀不進去,
            # 採用專案產不出 gate 審查頁。守衛:scripts/check-py-floor.sh。
            ("lane · Risk", f"{lane_val} · {risk_val}",
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
    if stage == "5-tasks":
        # 執行板不是 gate(無 G 編號),但五格規格一樣釘死在 README §6〈執行板頂區〉。
        if n_bad:
            t_note = f"{n_bad} 條缺必填欄"
        else:
            t_note = "六欄齊全"
        # 「模式」是 execution.mode(frontmatter,選配),跟「狀態」一樣沒有專屬章節可跳,
        # 兩格都錨 #top(frontmatter 本身就在頁首)——與 2-decision/4-spec 既有慣例一致
        # (那兩站也都有 frontmatter 衍生格錨在 #top)。
        return [
            ("狀態", _find(md, r"^status:\s*(\S+)"), "frontmatter", "#top"),
            ("任務", f"{n_items} 個 T", t_note, "#cards"),
            ("模式", _find(md, r"^\s*mode:\s*(\S+)", "sequential"),
             "execution.mode(未標=sequential)", "#top"),
            ("依賴", f"{dag_edges} 條", "Blocked-by 邊", "#dag"),
            ("進度", f"{dag_done}/{n_items}" if n_items else "—",
             "已勾 完成/總數", "#progress"),
        ]
    known_sec = _section_text(md, "Known Limits")
    # 條數 = 表格「資料列」+ bullet 列。舊寫法 `[-*|]` 連表頭列與 `|---|` 分隔列
    # 都算進去(4 條限界報成 6 條)—— 這格給人的是「有幾條要看」,計數必須
    # 對得上人打開該節數得到的條數(2026-08-15 K-6 修範例時交叉驗證抓到)。
    known = len(table_rows(known_sec)) + \
        len(re.findall(r"^\s*[-*]\s+\S", mask_fenced(known_sec), re.M))
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

    _raw_src_text = src.read_text(encoding="utf-8")
    md = re.sub(r"\A---\n.*?\n---\n", "", _raw_src_text, flags=re.S)
    # frontmatter 是整段**刪除**(不是等長遮蔽),md 的行號因此比原始檔少了
    # frontmatter 的行數 —— N-4 的行號警告要對「使用者打開來看的原始檔」報,
    # 不能對切掉 frontmatter 後的 md 報(否則每份有 frontmatter 的正式文件都會
    # 報錯行號,直接違背這條警告存在的目的:讓人一眼找到是哪裡沒收尾)。
    _fm_match_for_lineno = re.match(r"\A---\n.*?\n---\n", _raw_src_text, flags=re.S)
    _fm_line_offset = _fm_match_for_lineno.group(0).count("\n") if _fm_match_for_lineno else 0
    # 未閉合的 fence 會把其後全部內容吃成程式碼(規則正確,但不得靜默 —— 二次複審 P3)。
    # 判定「未閉合」用 token-based(見 _unclosed_fences);swallowed 行數計算沿用舊版
    # (遮蔽版與原文逐行比,任何被清空的非空行都算——不只算未閉合那個 fence 自己的)。
    _mk = mask_fenced(md)
    swallowed = sum(1 for a, b in zip(md.splitlines(), _mk.splitlines())
                    if a.strip() and not b.strip())
    if swallowed and _unclosed_fences(md):
        print(f"⚠️  偵測到**未閉合**的 code fence:其後 {swallowed} 行非空內容被當成程式碼,"
              f"不會進待審區也不會進背景資料。請補上收尾的 ``` 或 ~~~。", file=sys.stderr)

    # N-4:未閉合的 <!-- html 註解會把其後所有 level-2 標題吞成同一個 html_block,
    # 結構塌陷卻無 traceback、無 exit 1(N-1 的對帳也看不到,因為 markdown-it 本身
    # 就沒切出被吞的節)——這條警告是唯一訊號,必補,且要指出起始行號。
    _unclosed_comment = _unclosed_html_comment(md)
    if _unclosed_comment and _unclosed_comment.map:
        _uhc_line = _unclosed_comment.map[0] + 1 + _fm_line_offset  # 原始檔行號(含 frontmatter)
        print(f"⚠️  偵測到**未閉合**的 <!-- html 註解:從第 {_uhc_line} 行起,"
              f"其後內容(可能含 level-2 標題)被併入前一節,結構塌陷。請補上收尾的 -->。",
              file=sys.stderr)

    fm = re.match(r"\A---\n(.*?)\n---\n", src.read_text(encoding="utf-8"), flags=re.S)
    fm_text = fm.group(1) if fm else ""
    secs = sections(md)

    cards, n_items, used = PARSERS[stage](md, secs)
    rendered_rids = re.findall(r'<section class="r-block" id="(R-\d+)"', cards)
    if n_items == 0:
        hint = ("T 標題要 `## T-<id>`;必填欄要 `- Covers/Files/Verify/Blocked-by/Intent/Boundaries:`"
                if stage == "5-tasks" else "S 標題要 `#### S-<id>`;表格要有表頭列")
        print(f"ERROR: 一條待審項目都沒解析到 —— 檢查 {stage}.md 的標題與欄位格式({hint})",
              file=sys.stderr)
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

    # K-3:5-tasks 專屬的 DAG 區塊。只算一次(main 產 `#dag` html、把警告印到
    # stderr),數字再傳進 dash_cells 給「依賴」「進度」兩格用 —— 見 dash_cells
    # docstring,避免同一份 md 的警告被印兩次。
    dag_html, dag_edges, dag_done = "", 0, 0
    if stage == "5-tasks":
        dag_html, dag_edges, dag_warnings = build_dag(secs)
        for w in dag_warnings:
            print(f"NOTE: {w}", file=sys.stderr)
        dag_done, _dag_total = _tasks_done_count(secs)

    # 置頂節:判定本身與判定的前提,直接顯示在卡片之前,不摺疊
    pinned, pinned_titles = [], set()
    for lvl, title, body in secs:
        if lvl <= 2 and PINNED_PAT.search(title) and body.strip():
            pinned_titles.add(title)
            pinned.append(f'<section class="pinned" id="{anchor_id(title)}">'
                          f'<h2>{inline(title)}</h2>'
                          f'<div class="doc-in">{md_block(body)}</div></section>')

    # 背景資料:沒被做成卡片的章節一律收進 details,內容零刪減。
    # 已經做成卡片的內容**不得重複出現** —— 章節本身被用過、或它底下含有已渲染的
    # R/S 標題(例:`## ADDED Requirements` 的 body 含全部 R 與 S),一律跳過。
    appendix, skipped, dropped, dropped_empty = [], [], [], []
    for lvl, title, body in secs:
        if lvl > 2 or title in used:
            continue
        if not body.strip():
            # N-1:空節目前不進背景資料(渲染了也是空白),但仍要有下落 ——
            # 明確歸類「dropped(空)」並列入盤點 NOTE,不算失敗(設計檔已定案的例外)。
            dropped_empty.append(title)
            continue
        # 只有 4-spec 的解析器(parse_spec)會用 R_HEAD 識別「已處理」的 R 容器標題
        # 並塞進 used;其他 stage 沒有這層機制,若讓這裡不分 stage 一律 continue,
        # 一個湊巧長得像 `R-\d` 的標題(非 4-spec 場景)就會被吞掉且沒有任何下落
        # ——這正是 N-1 要擋的那種消失,所以這條 continue 只在 4-spec 生效
        #(4-spec 底下這條理論上恆假,因為同樣的 R_HEAD 判斷已經在 parse_spec 把
        # title 塞進 used,不會走到這裡;留著只是防禦性對齊,不影響其他 stage)。
        if stage == "4-spec" and R_HEAD.match("#" * lvl + " " + title):
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
            continue  # 置頂節另外處理,不摺疊 —— 下落已算進 pinned_titles,不是消失
        appendix.append(
            f'<details class="doc" id="{anchor_id(title)}">'
            f'<summary><span>{inline(title)}</span></summary>'
            f'<div class="doc-in">{md_block(body)}</div></details>')
        skipped.append(title)
    if skipped:
        print(f"NOTE: 以下章節收進背景資料(預設收合、內容零刪減):{skipped}", file=sys.stderr)
    if dropped:
        print(f"NOTE: 以下父節的內容已整段渲染成卡片,不重複顯示:{dropped}", file=sys.stderr)
    if dropped_empty:
        print(f"NOTE: 以下章節本文為空,視為 dropped(空),不進背景資料:{dropped_empty}",
              file=sys.stderr)

    # N-1(HIGH,獨立審查,通用對帳,不逐處手加):輸入 md 的每一個 level-2 章節,
    # 都要能在上面四條路徑之一找到下落 ——
    #   ①渲染成卡片(used) ②置頂節(pinned_titles) ③背景 details(skipped)
    #   ④明確 dropped 且已印 NOTE(dropped / dropped_empty)
    # 四者皆非 = 靜默消失(這正是審查者實測的破口:appendix 迴圈加一條 continue,
    # 章節數對不上卻沒有任何斷言發現)。這裡是與資料格無關的通用盤點,不看
    # 章節名字,任何未來新增的章節/新增的 continue 分支都逃不掉這道收尾。
    l2_titles = [title for lvl, title, _b in secs if lvl == 2]
    accounted = used | pinned_titles | set(skipped) | set(dropped) | set(dropped_empty)
    missing_fate = [t for t in l2_titles if t not in accounted]
    if missing_fate:
        print(f"盤點失敗:章節「{missing_fate[0]}」無下落"
              + (f"(同批還有 {len(missing_fate) - 1} 節:{missing_fate[1:]})"
                 if len(missing_fate) > 1 else "")
              + " —— 不是卡片、不是置頂節、沒收進背景資料,也沒被列進 dropped NOTE,"
                "在產出物裡找不到任何痕跡。", file=sys.stderr)
        return 1
    n_used_l2 = len({t for t in l2_titles if t in used})
    print(f"NOTE: 盤點 L2 共 {len(l2_titles)} 節 = 卡片節 {n_used_l2}"
          f" + 置頂 {len(pinned_titles)} + 背景 {len(skipped)}"
          f" + dropped {len(dropped) + len(dropped_empty)}", file=sys.stderr)

    raw_cells = dash_cells(stage, fm_text + "\n" + md, n_items, n_bad, secs, n_obs,
                           dag_edges=dag_edges, dag_done=dag_done)
    have_ids = ({anchor_id(title) for _l, title, _b in secs} | {"cards", "top"}
                # `dag`/`progress` 是 5-tasks 才有的固定 id(見下方 body_html),
                # 三個 gate 站沒有這兩個目標,加進去也不影響它們(它們的五格從不
                # 引用 #dag/#progress,這個聯集只在 5-tasks 才真的被用到)。
                | ({"dag", "progress"} if stage == "5-tasks" else set()))
    cells = "".join(
        f'<a class="cell" href="{a if a.lstrip("#") in have_ids else "#cards"}">'
        f'<span class="k">{html.escape(k)}</span>'
        f'<span class="v">{html.escape(str(v))}</span>'
        f'<span class="n">{html.escape(n)}</span></a>'
        for k, v, n, a in raw_cells)

    title = f"{slug} · {stage}"
    # 執行板不是「審查介面」,措辭跟著換 —— 但這三個變數對三個 gate 站的值逐字等於
    # 原本寫死的字串,所以那三站的輸出 byte-for-byte 不變(見下方 body_html 的
    # f-string 插槽如何接回原字)。`progress_id`/`dag_html` 同理:gate 站永遠是空字串,
    # 直接接在既有那一行的**行尾**(不另起新行),空字串接上去不會多一個字元。
    kind_label = "執行板" if stage == "5-tasks" else "審查介面"
    cta = "動工" if stage == "5-tasks" else "往下讀"
    verb_done = "完成" if stage == "5-tasks" else "審"
    progress_id = ' id="progress"' if stage == "5-tasks" else ""
    body_html = f"""<div class="wrap" id="top">
<header class="masthead">
  <p class="eyebrow">dev-flow · {html.escape(stage)} · {kind_label}</p>
  <h1>{html.escape(slug)}</h1>
  <p class="sub">正本是 <code>docs/dev/{html.escape(slug)}/{html.escape(stage)}.md</code>,
  這頁隨時可重生。<strong>審完頂區五格再決定要不要{cta}。</strong></p>
  <div class="dash">{cells}</div>
</header>
{"".join(pinned)}
<div class="progress"{progress_id}>
  <div class="progress-in">
    <span class="count">已{verb_done} <b id="done">0</b> / {n_items} 條</span>
    <span class="bar"><i></i></span>
    <button class="btn" id="clear" type="button">清除勾選</button>
  </div>
</div>{dag_html}
<div id="cards">
{cards}
</div>
<h2 class="apx-h">背景資料(預設收合,內容零刪減)</h2>
{"".join(appendix)}
<footer class="foot">由 <code>scripts/build-gate-twin.py</code> 從 md 正本逐條解析產生,不手抄。</footer>
</div>"""

    out_local = root / "docs/dev" / slug / f"{stage}.html"
    # CSS_SPEC4 只加給 4-spec、CSS_SPEC2 只加給 2-decision、CSS_TASKS 只加給
    # 5-tasks(都是加法式新 class)。7-review 的 extra_css 仍是 CSS_SPEC。
    extra_css = ui.CSS_SPEC + (ui.CSS_SPEC4 if stage == "4-spec" else "") + (
        ui.CSS_SPEC2 if stage == "2-decision" else "") + (
        ui.CSS_TASKS if stage == "5-tasks" else "")
    out_local.write_text(ui.local_page(title, extra_css, body_html, SCRIPT), encoding="utf-8")
    # 片段是 opt-in:只有呼叫端明確設定 DEVFLOW_ARTIFACT_OUT 才寫。空字串 / 空白
    # 視同未設,避免「變數在、值是空的」仍落到預設 sidecar。
    art_out = os.environ.get("DEVFLOW_ARTIFACT_OUT", "").strip()
    if art_out:
        out_art = pathlib.Path(art_out)
        out_art.parent.mkdir(parents=True, exist_ok=True)
        out_art.write_text(ui.artifact_page(title, extra_css, body_html, SCRIPT), encoding="utf-8")
        print(f"wrote {out_local} + {out_art} — {n_items} 條待審,{len(appendix)} 節背景資料")
    else:
        print(f"wrote {out_local} — {n_items} 條待審,{len(appendix)} 節背景資料")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
