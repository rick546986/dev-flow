#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""4-spec 審查介面產生器
   輸入：docs/dev/pgs-report-batch-scope/4-spec.md（唯一正本）
   輸出：審查用 artifact html（R/S 拆成可勾選卡片，背景資料摺疊）
   R/S 內容由 md 逐條解析而來，不手抄，避免與正本漂移。
"""
import html
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path("/Users/asheng/dev/ivf_platform")
SLUG = "pgs-report-batch-scope"
SRC = ROOT / "docs/dev" / SLUG / "4-spec.md"
OUT = pathlib.Path(
    "/private/tmp/claude-501/-Users-asheng-dev-ivf-platform/"
    "dc4f496c-c333-40b6-82ea-4359e36d5916/scratchpad/4-spec-review.html"
)

# R 的嚴重度分級（來自 4-spec 本文：R-4 明寫「嚴重度最高」，R-3 是唯一會毀資料的洞）
R_META = {
    "R-1": ("報告 id 的批次歸屬", "core", "顯示錯批報告——使用者看到別批的判讀結果"),
    "R-2": ("同批一致性警示", "core", "歪掉的資料沒人看得見"),
    "R-3": ("HiStork 刪除的批次歸屬", "danger", "跨批刪掉別批的 HiStork 檔，不可逆"),
    "R-4": ("SpaceS 打包的批次歸屬", "danger", "錯的報告 PDF 送到外部送檢平台，不可逆"),
}

INLINE_MD = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*")


def inline(text: str) -> str:
    """行內 markdown（只需 code 與 bold）轉 html，其餘 escape。"""
    out, pos = [], 0
    for m in INLINE_MD.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f"<code>{html.escape(m.group(1))}</code>")
        else:
            out.append(f"<b>{html.escape(m.group(2))}</b>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def split_sections(md: str) -> list:
    """依 '## ' 切章節，回 [(title, body), ...]"""
    parts = re.split(r"^## (.+)$", md, flags=re.M)
    secs = []
    for i in range(1, len(parts), 2):
        secs.append((parts[i].strip(), parts[i + 1]))
    return secs


def parse_scenarios(body: str) -> list:
    """從一個 R 章節解析出 S 卡。"""
    scenarios = []
    chunks = re.split(r"^### (S-[\d.]+) (.+)$", body, flags=re.M)
    for i in range(1, len(chunks), 3):
        sid, stitle, sbody = chunks[i], chunks[i + 1].strip(), chunks[i + 2]
        fields = {}
        for key, pat in (
            ("given", r"^- \*\*GIVEN\*\* (.+?)(?=\n- |\n\n|\Z)"),
            ("when", r"^- \*\*WHEN\*\* (.+?)(?=\n- |\n\n|\Z)"),
            ("then", r"^- \*\*THEN\*\* (.+?)(?=\n- |\n\n|\Z)"),
            ("observe", r"^- \*\*觀測\*\*[:：](.+?)(?=\n- |\n\n|\Z)"),
        ):
            m = re.search(pat, sbody, flags=re.M | re.S)
            fields[key] = " ".join(m.group(1).split()) if m else ""
        baseline = "回歸基準線" in stitle
        clean_title = re.sub(r"（(回歸基準線|主案例)）", "", stitle).strip()
        tag = "回歸基準線" if baseline else ("主案例" if "主案例" in stitle else "")
        scenarios.append((sid, clean_title, tag, fields))
    return scenarios


def scenario_card(sid: str, title: str, tag: str, f: dict) -> str:
    tag_html = f'<span class="tag {"base" if tag == "回歸基準線" else "main"}">{tag}</span>' if tag else ""
    rows = []
    for label, key in (("GIVEN", "given"), ("WHEN", "when"), ("THEN", "then")):
        if f[key]:
            rows.append(
                f'<div class="gwt-row"><span class="gwt-k">{label}</span>'
                f'<span class="gwt-v">{inline(f[key])}</span></div>'
            )
    obs = (
        f'<div class="obs"><span class="obs-k">你要親自跑的觀測</span>'
        f'<span class="obs-v">{inline(f["observe"])}</span></div>'
        if f["observe"]
        else '<div class="obs missing"><span class="obs-k">缺「觀測」欄</span>'
        '<span class="obs-v">這條審不過——沒寫清楚要看哪裡</span></div>'
    )
    return f"""<article class="s-card" data-sid="{sid}">
  <label class="s-head">
    <input type="checkbox" class="s-chk" data-sid="{sid}">
    <span class="s-id">{sid}</span>
    <span class="s-title">{html.escape(title)}</span>
    {tag_html}
  </label>
  <div class="s-body">
    <div class="gwt">{"".join(rows)}</div>
    {obs}
  </div>
</article>"""


SVG_FIG = """<figure class="fig">
<svg id="flow" viewBox="0 0 700 566" role="img" aria-label="status 批次收斂行為流程圖">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path class="ahead" d="M0,0 L10,5 L0,10 z"/>
    </marker>
  </defs>
  <g class="n1"><rect x="180" y="20" width="340" height="44" rx="6" class="b"/><text class="nl" x="192" y="47">列表載入 / 開預覽</text></g>
  <g class="n2"><rect x="180" y="96" width="340" height="44" rx="6" class="b"/><text class="nl" x="192" y="123">rsRefreshButton 讀 btn.dataset</text></g>
  <g class="n3"><rect x="180" y="172" width="340" height="44" rx="6" class="b"/><text class="nl" x="192" y="199">POST status ivf_no+wga_date+sample_list</text></g>
  <g class="n4"><rect x="180" y="248" width="340" height="52" rx="6" class="hl"/><text class="nl" x="192" y="270">status 一次查詢帶齊三鍵</text><text class="nl" x="192" y="288">pgs_ivf_no x wga_date x embryo_no</text></g>
  <g class="n5"><rect x="180" y="332" width="340" height="52" rx="6" class="hl"/><text class="nl" x="192" y="354">rs_resolve_batch_report_ids</text><text class="nl" x="192" y="372">helper 純函式 可單元測試</text></g>
  <g class="n6"><rect x="180" y="416" width="340" height="52" rx="6" class="b"/><text class="nl" x="192" y="438">回應 report_id scope scope_degraded</text><text class="nl" x="192" y="456">id_check</text></g>
  <g class="n7"><rect x="20" y="506" width="300" height="44" rx="6" class="b"/><text class="nl" x="32" y="533">id_check 全 ok 走既有行為</text></g>
  <g class="n8"><rect x="380" y="506" width="300" height="44" rx="6" class="wn"/><text class="nl" x="392" y="533">有異常 面板頂端警示 不擋</text></g>
  <path class="edge" d="M350,64 L350,96" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,140 L350,172" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,216 L350,248" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,300 L350,332" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,384 L350,416" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,468 L350,487 L170,487 L170,506" marker-end="url(#arrow)"/>
  <path class="edge" d="M350,468 L350,487 L530,487 L530,506" marker-end="url(#arrow)"/>
</svg>
<figcaption class="cap">改完之後 <code>status</code> 的讀取路徑：scope 三鍵一次查回整批，
收斂與一致性判定落在 helper 純函式，異常只警示不擋（DD-2）。</figcaption>
</figure>"""


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
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0e1116; --panel:#161a21; --sunk:#1b2029;
    --ink:#e6e9f0; --ink-2:#a6afc1; --ink-3:#7b8598;
    --rule:#2a303b; --rule-2:#212731;
    --accent:#7fa0e0; --accent-soft:#1b2436;
    --ok:#4fbe86; --ok-soft:#132a20;
    --warn:#dda944; --warn-soft:#2c2415;
    --bad:#e4796f; --bad-soft:#2e1a19;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --ground:#0e1116; --panel:#161a21; --sunk:#1b2029;
  --ink:#e6e9f0; --ink-2:#a6afc1; --ink-3:#7b8598;
  --rule:#2a303b; --rule-2:#212731;
  --accent:#7fa0e0; --accent-soft:#1b2436;
  --ok:#4fbe86; --ok-soft:#132a20;
  --warn:#dda944; --warn-soft:#2c2415;
  --bad:#e4796f; --bad-soft:#2e1a19;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif;
  -webkit-font-smoothing:antialiased}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.86em;font-variant-numeric:tabular-nums}
code{background:var(--sunk);border-radius:3px;padding:1px 5px;color:var(--ink-2)}
.wrap{max-width:900px;margin:0 auto;padding:0 20px 96px}

/* ---- 頁首 ---- */
.masthead{padding:34px 0 20px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin:0 0 8px}
h1{font-size:1.62rem;line-height:1.3;margin:0 0 10px;letter-spacing:-.01em;text-wrap:balance}
.sub{color:var(--ink-2);margin:0;font-size:.94rem;max-width:62ch}

/* ---- 動線五格 ---- */
.dash{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));
  margin:20px 0 4px}
.cell{background:var(--panel);border:1px solid var(--rule);border-radius:9px;
  padding:11px 13px;box-shadow:var(--shadow)}
.cell .k{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;display:block;margin-bottom:5px}
.cell .v{font-size:1.02rem;font-weight:650;line-height:1.3;display:block}
.cell .n{font-size:.78rem;color:var(--ink-2);display:block;margin-top:3px}
.cell.is-bad .v{color:var(--bad)} .cell.is-ok .v{color:var(--ok)}
.cell.is-warn .v{color:var(--warn)} .cell.is-accent .v{color:var(--accent)}

/* ---- 進度條 ---- */
.progress{position:sticky;top:0;z-index:20;background:var(--ground);
  border-bottom:1px solid var(--rule);padding:11px 0;margin:22px 0 0}
.progress-in{max-width:900px;margin:0 auto;padding:0 20px;
  display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.bar{flex:1 1 200px;height:7px;background:var(--sunk);border-radius:99px;overflow:hidden;
  min-width:140px}
.bar i{display:block;height:100%;width:0;background:var(--accent);
  transition:width .25s ease;border-radius:99px}
.count{font-weight:650;font-variant-numeric:tabular-nums;white-space:nowrap}
.count b{color:var(--accent)}
.btn{border:1px solid var(--rule);background:var(--panel);color:var(--ink-2);
  border-radius:7px;padding:5px 11px;font-size:.82rem;cursor:pointer;font-family:inherit}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

/* ---- 審查判準 ---- */
.criterion{background:var(--accent-soft);border:1px solid color-mix(in srgb,var(--accent) 26%,transparent);
  border-radius:10px;padding:15px 17px;margin:26px 0}
.criterion h2{margin:0 0 7px;font-size:.95rem;letter-spacing:.02em}
.criterion p{margin:0;color:var(--ink-2);font-size:.9rem}
.criterion .ex{margin-top:9px;padding-top:9px;
  border-top:1px dashed color-mix(in srgb,var(--accent) 30%,transparent);font-size:.85rem}

/* ---- R 區塊 ---- */
.r-block{margin:30px 0 0;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);overflow:hidden;box-shadow:var(--shadow)}
.r-head{display:flex;gap:13px;align-items:flex-start;padding:15px 18px;
  border-bottom:1px solid var(--rule-2);border-left:4px solid var(--accent)}
.r-block.danger .r-head{border-left-color:var(--bad)}
.r-id{font-weight:700;font-size:.95rem;letter-spacing:.02em;white-space:nowrap;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.r-block.danger .r-id{color:var(--bad)}
.r-block.core .r-id{color:var(--accent)}
.r-name{font-weight:650}
.r-risk{display:block;font-size:.83rem;color:var(--ink-2);margin-top:3px}
.r-rule{padding:12px 18px;background:var(--sunk);font-size:.9rem;color:var(--ink-2);
  border-bottom:1px solid var(--rule-2)}
.r-rule b{color:var(--ink)}

/* ---- S 卡 ---- */
.s-card{border-bottom:1px solid var(--rule-2)}
.s-card:last-child{border-bottom:0}
.s-head{display:flex;gap:10px;align-items:center;padding:12px 18px;cursor:pointer;
  flex-wrap:wrap}
.s-head:hover{background:var(--sunk)}
.s-chk{width:17px;height:17px;accent-color:var(--accent);cursor:pointer;flex:none}
.s-chk:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.s-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.83rem;
  font-weight:650;color:var(--accent);background:var(--accent-soft);
  padding:2px 7px;border-radius:5px;flex:none}
.s-title{font-weight:600;font-size:.94rem}
.tag{font-size:.71rem;padding:2px 8px;border-radius:99px;font-weight:600;flex:none}
.tag.base{background:var(--sunk);color:var(--ink-3)}
.tag.main{background:var(--warn-soft);color:var(--warn)}
.s-card.done{background:var(--ok-soft)}
.s-card.done .s-title{color:var(--ink-2)}
.s-body{padding:0 18px 15px 45px}
.gwt{display:grid;gap:5px;margin-bottom:11px}
.gwt-row{display:grid;grid-template-columns:58px 1fr;gap:10px;align-items:baseline}
.gwt-k{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.71rem;
  font-weight:700;color:var(--ink-3);letter-spacing:.06em}
.gwt-v{font-size:.9rem;color:var(--ink-2)}
.obs{background:var(--sunk);border-left:3px solid var(--accent);border-radius:0 7px 7px 0;
  padding:9px 13px}
.obs.missing{border-left-color:var(--bad);background:var(--bad-soft)}
.obs-k{display:block;font-size:.71rem;letter-spacing:.08em;text-transform:uppercase;
  font-weight:700;color:var(--accent);margin-bottom:3px}
.obs.missing .obs-k{color:var(--bad)}
.obs-v{font-size:.88rem;color:var(--ink-2)}

/* ---- 圖 ---- */
.fig{margin:26px 0;padding:17px;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);box-shadow:var(--shadow)}
.fig svg{display:block;width:100%;max-width:660px;margin:0 auto;height:auto}
.cap{color:var(--ink-3);font-size:.82rem;line-height:1.6;margin-top:11px;text-align:center}
svg .b{fill:var(--panel);stroke:var(--rule);stroke-width:1.4}
svg .hl{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.4}
svg .wn{fill:var(--warn-soft);stroke:var(--warn);stroke-width:1.4}
svg .nl{font:11px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ink)}
svg .edge{fill:none;stroke:var(--ink-3);stroke-width:1.6}
svg .ahead{fill:var(--ink-3);stroke:none}

/* ---- 摺疊背景資料 ---- */
.appendix{margin-top:42px;border-top:1px solid var(--rule);padding-top:22px}
.appendix > h2{font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 13px}
details.doc{border:1px solid var(--rule);border-radius:9px;margin-bottom:9px;
  background:var(--panel);overflow:hidden}
details.doc > summary{cursor:pointer;padding:11px 15px;font-weight:600;font-size:.9rem;
  list-style:none;display:flex;justify-content:space-between;gap:10px;align-items:center}
details.doc > summary::-webkit-details-marker{display:none}
details.doc > summary::after{content:"展開";font-size:.76rem;color:var(--ink-3);font-weight:500}
details.doc[open] > summary::after{content:"收合"}
details.doc[open] > summary{border-bottom:1px solid var(--rule-2)}
details.doc:hover{border-color:var(--accent)}
.doc-in{padding:4px 17px 15px;font-size:.9rem;color:var(--ink-2)}
.doc-in h2,.doc-in h3{color:var(--ink);font-size:.95rem;margin:16px 0 7px}
.doc-in table{border-collapse:collapse;width:100%;margin:11px 0;font-size:.84rem}
.doc-in th,.doc-in td{border:1px solid var(--rule);padding:6px 9px;text-align:left;
  vertical-align:top}
.doc-in th{background:var(--sunk);font-weight:650;color:var(--ink)}
.doc-in pre{background:var(--sunk);padding:11px;border-radius:7px;overflow-x:auto;
  font-size:.82rem;line-height:1.5}
.doc-in blockquote{margin:11px 0;padding:.4em 1em;border-left:3px solid var(--rule);
  color:var(--ink-3)}
.tablewrap{overflow-x:auto}
.doc-in ul,.doc-in ol{padding-left:1.35em}
.doc-in li{margin:4px 0}

/* ---- 收尾 ---- */
.verdict{margin-top:34px;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);padding:19px 21px;box-shadow:var(--shadow)}
.verdict h2{margin:0 0 9px;font-size:1rem}
.verdict p{margin:0 0 9px;color:var(--ink-2);font-size:.91rem}
.verdict p:last-child{margin-bottom:0}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media (max-width:560px){
  .s-body{padding-left:18px}
  .gwt-row{grid-template-columns:1fr;gap:2px}
  h1{font-size:1.35rem}
}
"""

JS = """
(function(){
  var boxes = Array.prototype.slice.call(document.querySelectorAll('.s-chk'));
  var bar = document.querySelector('.bar i');
  var done = document.getElementById('done');
  var KEY = 'pgs-batch-scope-g2';
  function load(){
    try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e){ return {}; }
  }
  function save(state){
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch(e){}
  }
  var state = load();
  function paint(){
    var n = 0;
    boxes.forEach(function(b){
      var card = b.closest('.s-card');
      if (b.checked){ n++; card.classList.add('done'); }
      else { card.classList.remove('done'); }
    });
    done.textContent = n;
    bar.style.width = (n / boxes.length * 100) + '%';
  }
  boxes.forEach(function(b){
    if (state[b.dataset.sid]) b.checked = true;
    b.addEventListener('change', function(){
      state[b.dataset.sid] = b.checked;
      save(state); paint();
    });
  });
  document.getElementById('reset').addEventListener('click', function(){
    boxes.forEach(function(b){ b.checked = false; });
    state = {}; save(state); paint();
  });
  paint();
})();
"""


def main() -> int:
    md = SRC.read_text(encoding="utf-8")
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)
    secs = split_sections(md)
    by_title = {t: b for t, b in secs}

    # --- R 區塊 ---
    r_blocks, total_s = [], 0
    for title, body in secs:
        m = re.match(r"(R-\d+) · (.+)", title)
        if not m:
            continue
        rid = m.group(1)
        name, kind, risk = R_META[rid]
        rule = re.search(r"^\*\*(.+?)\*\*$", body.strip(), flags=re.M)
        rule_html = (
            f'<div class="r-rule">{inline(rule.group(1))}</div>' if rule else ""
        )
        cards = parse_scenarios(body)
        total_s += len(cards)
        r_blocks.append(
            f"""<section class="r-block {kind}" id="{rid}">
  <div class="r-head">
    <span class="r-id">{rid}</span>
    <span><span class="r-name">{html.escape(name)}</span>
      <span class="r-risk">出錯的話：{html.escape(risk)}</span></span>
  </div>
  {rule_html}
  {"".join(scenario_card(*c) for c in cards)}
</section>"""
        )

    if total_s != 16:
        print(f"ERROR: 解析到 {total_s} 個 S，預期 16", file=sys.stderr)
        return 1

    # --- 附錄：其餘章節原文（markdown 轉換，不刪內容）---
    appendix_order = [
        ("G2 審查記錄", "G2 審查記錄", "verdict、審查者身分、審前修正"),
        ("Bug Scenario", "根因與重現步驟", "同 ivf_no 兩批的實際案例，5 處缺陷位置"),
        ("Acceptance Criteria", "驗收條件", "S 全綠之外還要滿足什麼"),
        ("Out of Scope", "本次不做的事", "5 條，含另案處理的項目"),
        ("Diff Budget", "改動預算", "≤5 檔／≤250 行"),
        ("Verification Profile（G2 一併審）", "驗證計畫", "lane／Risk／Failure Model／驗證層"),
        ("Drafting Decisions（2026-08-14 全數裁決完畢）", "設計決策 DD-1～DD-8", "全數已核准"),
        ("Test Skeletons", "測試骨架", "純函式 6 個 case"),
        ("Known limits（實作者必讀）", "已知限界", "DB 未實測、無測試環境"),
    ]
    # 未匹配章節守衛：md 新增章節時不得被靜默丟掉
    #（SVG 圖取代了「行為流程」，R-x 已渲染成卡片，其餘一律必須在 appendix_order 內）
    known = {k for k, _, _ in appendix_order} | {"行為流程"}
    unmatched = [
        t for t, _ in secs if not re.match(r"R-\d+ · ", t) and t not in known
    ]
    if unmatched:
        print(f"ERROR: md 有未收錄的章節，會被靜默丟掉：{unmatched}", file=sys.stderr)
        return 1

    appendix = []
    for key, label, hint in appendix_order:
        body = by_title.get(key)
        if body is None:
            print(f"ERROR: 找不到章節「{key}」", file=sys.stderr)
            return 1
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

    page = f"""<title>PGS 報告批次歸屬規格</title>
<style>{CSS}</style>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · Stage 4 · G2 審查</p>
  <h1>PGS 報告 id 的批次歸屬</h1>
  <p class="sub">同一個 <code>ivf_no</code> 分兩次送檢時，報告 id 會跨批誤取——顯示錯批報告、刪錯批的
  HiStork 檔、送錯批的 PDF 到 SpaceS。這份是修正的可測契約，需要你逐條審過才進實作。</p>

  <div class="dash">
    <div class="cell is-ok"><span class="k">狀態</span><span class="v">approved</span>
      <span class="n">4-spec，已進 Stage 5</span></div>
    <div class="cell is-ok"><span class="k">Gate</span><span class="v">G2 PASS</span>
      <span class="n">rick 自審 2026-08-14；G1 依 Owner Call 例外跳過</span></div>
    <div class="cell is-accent"><span class="k">Lane / Risk</span><span class="v">fast / high</span>
      <span class="n">Owner Call 例外已填</span></div>
    <div class="cell is-ok"><span class="k">DD</span><span class="v">8 / 8</span>
      <span class="n">全數已核准</span></div>
    <div class="cell is-ok"><span class="k">Demo verdict</span><span class="v">N/A</span>
      <span class="n">legacy，機械檢查 PASS</span></div>
  </div>
</header>
</div>

<div class="progress">
  <div class="progress-in">
    <span class="count">已審 <b id="done">0</b> / {total_s} 條</span>
    <span class="bar"><i></i></span>
    <button class="btn" id="reset" type="button">清除勾選</button>
  </div>
</div>

<div class="wrap">
  <div class="criterion">
    <h2>G2 已 PASS —— 這頁現在是實作與驗收的對照表</h2>
    <p>rick 於 2026-08-14 逐條審過 {total_s} 個 S 並判 PASS，spec 已 <code>approved</code>。
    下面的勾選框改作 <b>Stage 6 實作與 Stage 7 驗收</b>用：每跑過一條「觀測」就勾一格。</p>
    <p class="ex">判準不變：<b>每個 S 的「觀測」要能照著親自跑一次</b>，並在
    <code>7-review.md</code> 記下現象證據——不接受「程式碼看起來對」。</p>
  </div>

  {SVG_FIG}

  {"".join(r_blocks)}

  <div class="verdict">
    <h2>G2 之後的下落</h2>
    <p><b>已完成</b>：frontmatter <code>approved</code>、reviewers 記 owner 自審、
    STATUS 標 <code>G2✅</code> 並推進到 <code>5-tasks</code>。</p>
    <p><b>進行中</b>：<code>5-tasks.md</code> 切 T，每個 T 的 Verify 都要在動碼前原樣跑一次
    確認「現在不綠、方向對」。</p>
    <p><b>G3 要回到這頁</b>：這 {total_s} 條的「觀測」逐條實跑，現象證據記進
    <code>7-review.md</code>。</p>
  </div>

  <div class="appendix">
    <h2>背景資料（審 S 時要查才展開）</h2>
    {"".join(appendix)}
  </div>

  <p class="src">正本是 <code>docs/dev/pgs-report-batch-scope/4-spec.md</code>，這頁隨時可重生。<br>
  勾選狀態存在你自己的瀏覽器，不會送出去。</p>
</div>
<script>{JS}</script>
"""

    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(page)} bytes) — {total_s} scenarios, {len(appendix)} appendix sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
