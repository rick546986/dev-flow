#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5-tasks 執行介面產生器
   輸入：<專案根>/docs/dev/<slug>/5-tasks.md（唯一正本）
   輸出：本機 5-tasks.html（完整文件）+ artifact 片段
   T 由 md 逐條解析，不手抄；Boundaries 摺疊、Verify 獨立標示、DAG 用 inline SVG。

   用法：build_tasks.py <專案根目錄> <slug> [artifact 輸出路徑]
   或用環境變數：DEVFLOW_PROJECT_ROOT / DEVFLOW_SLUG / DEVFLOW_ARTIFACT_OUT
"""
import html
import os
import pathlib
import re
import sys

import markdown

import devflow_ui

_ARGV = sys.argv[1:]
ROOT = pathlib.Path(
    _ARGV[0] if len(_ARGV) > 0 else os.environ.get("DEVFLOW_PROJECT_ROOT", ".")
).expanduser().resolve()
SLUG = _ARGV[1] if len(_ARGV) > 1 else os.environ.get("DEVFLOW_SLUG", "")
if not SLUG:
    sys.exit("用法：build_tasks.py <專案根目錄> <slug> [artifact 輸出路徑]"
             "（或設 DEVFLOW_PROJECT_ROOT / DEVFLOW_SLUG）")
SRC = ROOT / "docs/dev" / SLUG / "5-tasks.md"
OUT_LOCAL = ROOT / "docs/dev" / SLUG / "5-tasks.html"
OUT_ART = pathlib.Path(
    _ARGV[2] if len(_ARGV) > 2
    else os.environ.get(
        "DEVFLOW_ARTIFACT_OUT",
        str(ROOT / "docs/dev" / SLUG / "5-tasks-view.artifact.html"),
    )
).expanduser()


def _expect(name: str):
    """期望條數：設了才檢查，沒設就只印實際條數（原本寫死 5，換一份任務清單必誤判）。"""
    raw = os.environ.get(name, "").strip()
    return int(raw) if raw.isdigit() else None


EXPECT_T = _expect("DEVFLOW_EXPECT_T")
TITLE = "PGS 報告批次歸屬任務板"

FIELDS = ("Covers", "Files", "Verify", "Blocked-by", "Intent", "Boundaries", "Owner")


def md_inline(text: str) -> str:
    """一段文字轉 html（保留 code / bold），去掉外層 <p>。"""
    out = markdown.markdown(text.strip(), output_format="html")
    return re.sub(r"^<p>|</p>$", "", out.strip())


def split_sections(md: str) -> list:
    parts = re.split(r"^## (.+)$", md, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def parse_task(body: str) -> dict:
    """把一個 T 的 body 切成欄位（含續行合併）。"""
    lines = body.splitlines()
    out, cur = {}, None
    for ln in lines:
        m = re.match(r"^- ([A-Za-z][\w-]*): ?(.*)$", ln)
        if m and m.group(1) in FIELDS:
            cur = m.group(1)
            out[cur] = m.group(2).strip()
        elif cur and ln.strip() and not ln.startswith("- ["):
            out[cur] += ("\n" if ln.startswith("  ") and out[cur] else " ") + ln.strip()
        elif not ln.strip():
            cur = None if cur in ("Covers", "Files", "Verify", "Blocked-by") else cur
    return out


def chips(text: str, cls: str = "") -> str:
    items = [x for x in re.split(r"[,、；;]|\s/\s", text) if x.strip()]
    items = [re.sub(r"[`\s]", "", x) for x in items]
    items = [x for x in items if x and x != "—"]
    if not items:
        return '<span class="chip none">—</span>'
    return '<div class="chips">' + "".join(
        f'<span class="chip {cls}">{html.escape(x)}</span>' for x in items
    ) + "</div>"


def task_card(tid: str, title: str, f: dict) -> str:
    danger = "⚠️" in f.get("Boundaries", "")
    kind = "danger" if danger else "core"
    note = ""
    if danger:
        m = re.search(r"⚠️ \*\*(.+?)。?\*\*", f.get("Boundaries", ""))
        note = f'<span class="danger-note">{html.escape(m.group(1))}</span>' if m else ""

    verify = f.get("Verify", "").strip().strip("`")
    bound_html = md_inline(f.get("Boundaries", "—").replace("\n", "\n\n"))

    return f"""<section class="r-block t-block {kind}" id="{tid}" data-tid="{tid}">
  <div class="r-head">
    <input type="checkbox" class="t-done" data-tid="{tid}" aria-label="{tid} 完成">
    <span class="r-id">{tid}</span>
    <span><span class="r-name">{html.escape(title)}</span>{note}</span>
  </div>
  <div class="t-intent"><span class="k">做完之後，系統多了什麼</span>{md_inline(f.get("Intent", "—"))}</div>
  <div class="t-grid">
    <span class="k">Covers</span><span class="v">{chips(f.get("Covers", ""))}</span>
    <span class="k">Files</span><span class="v">{chips(f.get("Files", ""), "file")}</span>
    <span class="k">Blocked-by</span><span class="v">{chips(f.get("Blocked-by", "—"))}</span>
    <span class="k">Verify</span><span class="v"><code class="vfy">{html.escape(verify)}</code></span>
  </div>
  <details class="t-bound">
    <summary>Boundaries — 這個 T 的硬約束與禁區</summary>
    <div class="body">{bound_html}</div>
  </details>
</section>"""


SVG_DAG = """<figure class="fig">
<svg id="dag" viewBox="0 0 700 322" role="img" aria-label="T 依賴 DAG">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path class="ahead" d="M0,0 L10,5 L0,10 z"/>
    </marker>
  </defs>
  <g class="d1"><rect x="190" y="16" width="320" height="50" rx="6" class="hl"/><text class="nl" x="202" y="38">T-1 抽 helper 純函式</text><text class="sm" x="202" y="55">helpers + tests / S-1.3 S-1.6 S-2.1~2.3</text></g>
  <g class="d2"><rect x="190" y="110" width="320" height="50" rx="6" class="hl"/><text class="nl" x="202" y="132">T-2 status 三鍵查詢 + 前端 scope</text><text class="sm" x="202" y="149">tracer bullet 打通點 / S-1.1 S-1.2 S-1.4 S-1.5</text></g>
  <g class="d3"><rect x="8" y="236" width="216" height="66" rx="6" class="b"/><text class="nl" x="20" y="258">T-3 警示 UI</text><text class="sm" x="20" y="275">view + helpers</text><text class="sm" x="20" y="291">S-2.1 S-2.2 S-2.3</text></g>
  <g class="d4"><rect x="242" y="236" width="216" height="66" rx="6" class="bd"/><text class="nl" x="254" y="258">T-4 HiStork 刪除</text><text class="sm" x="254" y="275">不可逆 刪外部檔</text><text class="sm" x="254" y="291">S-3.1 S-3.2 S-3.3</text></g>
  <g class="d5"><rect x="476" y="236" width="216" height="66" rx="6" class="bd"/><text class="nl" x="488" y="258">T-5 SpaceS 打包</text><text class="sm" x="488" y="275">不可逆 對外送出</text><text class="sm" x="488" y="291">S-4.1~4.4</text></g>
  <path class="edge" d="M350,66 L350,110" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,160 L350,200 L116,200 L116,236" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,160 L350,236" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,160 L350,200 L584,200 L584,236" marker-end="url(#arrow)"/>
</svg>
<figcaption class="cap">執行順序 T-1 → T-2 → T-3 → T-4 → T-5（<code>execution.mode: sequential</code>）。
T-3／T-4／T-5 邏輯上互不依賴，但都動到同一個 controller 或 view，依序做。
兩個紅框是不可逆的：刪外部檔、對外送 PDF。</figcaption>
</figure>"""

JS = """
(function(){
  var boxes = Array.prototype.slice.call(document.querySelectorAll('.t-done'));
  var bar = document.querySelector('.bar i');
  var done = document.getElementById('done');
  var KEY = 'pgs-batch-scope-t';
  function load(){ try { return JSON.parse(localStorage.getItem(KEY)||'{}'); } catch(e){ return {}; } }
  function save(s){ try { localStorage.setItem(KEY, JSON.stringify(s)); } catch(e){} }
  var state = load();
  function paint(){
    var n = 0;
    boxes.forEach(function(b){
      var card = b.closest('.t-block');
      if (b.checked){ n++; card.classList.add('done'); } else { card.classList.remove('done'); }
    });
    done.textContent = n;
    bar.style.width = (n / boxes.length * 100) + '%';
  }
  boxes.forEach(function(b){
    if (state[b.dataset.tid]) b.checked = true;
    b.addEventListener('change', function(){ state[b.dataset.tid] = b.checked; save(state); paint(); });
  });
  document.getElementById('reset').addEventListener('click', function(){
    boxes.forEach(function(b){ b.checked = false; }); state = {}; save(state); paint();
  });
  paint();
})();
"""

APPENDIX = [
    ("執行前提（實作者必讀）", "執行前提", "純函式紀律、S-id 命名、Verify 骨架與開工前實跑結果"),
    ("S → T 覆蓋對照（16 個 S 全數有下落）", "S → T 覆蓋對照", "16 個 S 逐一對到 T"),
    ("Diff Budget 對帳", "Diff Budget 對帳", "4 檔／預算 ≤5"),
    ("Split Decisions", "Split Decisions", "拆分與排序的四條決策"),
]


def main() -> int:
    md = re.sub(r"\A---\n.*?\n---\n", "", SRC.read_text(encoding="utf-8"), flags=re.S)
    secs = split_sections(md)
    by_title = {t: b for t, b in secs}

    # 上面那份章節清單是照原始那份任務清單寫的，換一份章節名一定不同 ——
    # 改成「自動收進附錄末尾並印出」，既不靜默丟失、也不擋住別的專案。
    known = {k for k, _, _ in APPENDIX} | {"T 依賴 DAG"}
    unmatched = [t for t, _ in secs if not re.match(r"T-\d+ ", t) and t not in known]
    appendix_order = list(APPENDIX)
    if unmatched:
        print(f"NOTE: 以下章節不在預設附錄清單，已自動收進附錄末尾：{unmatched}",
              file=sys.stderr)
        appendix_order += [(t, t, "md 內原有章節（自動收錄）") for t in unmatched]

    cards, n_t = [], 0
    for title, body in secs:
        m = re.match(r"(T-\d+) (.+)", title)
        if not m:
            continue
        f = parse_task(body)
        missing = [k for k in ("Covers", "Files", "Verify", "Blocked-by", "Intent", "Boundaries")
                   if not f.get(k)]
        if missing:
            print(f"ERROR: {m.group(1)} 缺欄 {missing}", file=sys.stderr)
            return 1
        cards.append(task_card(m.group(1), m.group(2), f))
        n_t += 1

    if n_t == 0:
        print("ERROR: 一個 T 都沒解析到 —— 檢查 5-tasks.md 的 T 標題與欄位格式", file=sys.stderr)
        return 1
    if EXPECT_T is not None and n_t != EXPECT_T:
        print(f"ERROR: 解析到 {n_t} 個 T，預期 {EXPECT_T}（DEVFLOW_EXPECT_T）", file=sys.stderr)
        return 1
    print(f"NOTE: 解析到 {n_t} 個 T", file=sys.stderr)

    appendix = []
    skipped = []
    for key, label, hint in appendix_order:
        body = by_title.get(key)
        if body is None:
            skipped.append(key)
            continue
        inner = markdown.markdown(
            body, extensions=["tables", "fenced_code", "sane_lists"], output_format="html"
        )
        inner = inner.replace("<table>", '<div class="tablewrap"><table>').replace(
            "</table>", "</table></div>"
        )
        appendix.append(
            f"""<details class="doc">
  <summary><span>{html.escape(label)} <span style="color:var(--ink-3);font-weight:400">— {html.escape(hint)}</span></span></summary>
  <div class="doc-in">{inner}</div>
</details>"""
        )

    if skipped:
        print(f"NOTE: 這份 md 沒有以下章節，已略過：{skipped}", file=sys.stderr)

    body = f"""<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · Stage 5 · 任務板</p>
  <h1>PGS 報告 id 的批次歸屬</h1>
  <p class="sub">把 <code>4-spec.md</code>（G2 PASS）切成 {n_t} 個可勾選的實作單。
  順序是 tracer bullet：先把判定邏輯與主案例打通，最後才碰兩個不可逆的外部副作用。</p>
  <div class="dash">
    <div class="cell is-accent"><span class="k">任務</span><span class="v">{n_t} 個 T</span>
      <span class="n">sequential，不並行</span></div>
    <div class="cell is-ok"><span class="k">覆蓋</span><span class="v">16 / 16 S</span>
      <span class="n">每個 S 都有 T</span></div>
    <div class="cell is-ok"><span class="k">Diff Budget</span><span class="v">4 / 5 檔</span>
      <span class="n">≤250 行</span></div>
    <div class="cell is-bad"><span class="k">不可逆</span><span class="v">T-4 · T-5</span>
      <span class="n">刪外部檔／對外送 PDF</span></div>
    <div class="cell is-warn"><span class="k">測試基準線</span><span class="v">29 → 46</span>
      <span class="n">本次加 17 個 case</span></div>
  </div>
</header>
</div>

<div class="progress">
  <div class="progress-in">
    <span class="count">已完成 <b id="done">0</b> / {n_t} 個 T</span>
    <span class="bar"><i></i></span>
    <button class="btn" id="reset" type="button">清除勾選</button>
  </div>
</div>

<div class="wrap">
  <div class="criterion">
    <h2>動任何一行程式之前先讀這段</h2>
    <p><b>可測核心一律抽進 <code>helpers/report_system_helper.php</code> 純函式。</b>
    本專案唯一的自動化測試是純函式 CLI，controller 的 DB 查詢與 view 的 DOM 操作都測不到——
    不抽的話這個 T 就沒有任何會失敗的檢查。</p>
    <p class="ex"><b>Verify 為什麼是三段式</b>：<b>要防的是「案例根本沒加」</b>——
    「沒寫測試」與「測試全過」在單看 exit code 時無法區分，所以
    <code>grep -c '^  ok  - '</code> 的計數才是主要鑑別力，
    <code>ALL PASS</code> 那段是冗餘保險。<br>
    <b>測試案例命名帶 S-id</b>：<code>check(..., '[S-2.1] …')</code>，這是 R→S→T 追溯鏈的接點。</p>
  </div>

  {SVG_DAG}

  {"".join(cards)}

  <div class="verdict">
    <h2>每個 T 做完的收尾</h2>
    <p>RED → GREEN → scope check（動到的檔 ⊆ 該 T 的 Files）→ 跑 Verify →
    <b>獨立 review（reviewer ≠ implementer）</b>→ PASS → commit →
    記進 <code>6-implementation-notes.md</code> 的 Progress Log。</p>
    <p>改動檔案超出該 T 的 Files → 停下判 L1／L2，分不清一律當 L2（回頭改 4-spec、重過 G2）。</p>
  </div>

  <div class="appendix">
    <h2>細節（要查才展開）</h2>
    {"".join(appendix)}
  </div>

  <p class="src">正本是 <code>docs/dev/pgs-report-batch-scope/5-tasks.md</code>，這頁隨時可重生。<br>
  勾選狀態存在你自己的瀏覽器，不會送出去。</p>
</div>
"""

    css = devflow_ui.CSS_TASKS
    OUT_LOCAL.write_text(devflow_ui.local_page(TITLE, css, body, JS), encoding="utf-8")
    OUT_ART.write_text(devflow_ui.artifact_page(TITLE, css, body, JS), encoding="utf-8")
    print(f"wrote {OUT_LOCAL} + {OUT_ART} — {n_t} tasks, {len(appendix)} appendix sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
