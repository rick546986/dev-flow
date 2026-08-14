#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dev-flow gate twin 共用 UI 層
   一份 CSS、兩種輸出殼（本機完整文件 / Artifact 片段），供 4-spec 與 5-tasks 共用。
   母版待修清單 B-8 的建議修法 4：合併成單一產生器、兩種輸出模式。
"""

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
a{color:var(--accent)}
.wrap{max-width:900px;margin:0 auto;padding:0 20px 96px}

/* ---- 頁首 ---- */
.masthead{padding:34px 0 20px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin:0 0 8px}
h1{font-size:1.62rem;line-height:1.3;margin:0 0 10px;letter-spacing:-.01em;text-wrap:balance}
.sub{color:var(--ink-2);margin:0;font-size:.94rem;max-width:62ch}

/* ---- 動線格 ---- */
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

/* ---- sticky 進度 ---- */
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

/* ---- 提示框 ---- */
.criterion{background:var(--accent-soft);border:1px solid color-mix(in srgb,var(--accent) 26%,transparent);
  border-radius:10px;padding:15px 17px;margin:26px 0}
.criterion h2{margin:0 0 7px;font-size:.95rem;letter-spacing:.02em;border:0;padding:0}
.criterion p{margin:0;color:var(--ink-2);font-size:.9rem}
.criterion .ex{margin-top:9px;padding-top:9px;
  border-top:1px dashed color-mix(in srgb,var(--accent) 30%,transparent);font-size:.85rem}

/* ---- 區塊卡（R / T 共用）---- */
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

/* ---- 圖 ---- */
.fig{margin:26px 0;padding:17px;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);box-shadow:var(--shadow)}
.fig svg{display:block;width:100%;max-width:700px;margin:0 auto;height:auto}
.cap{color:var(--ink-3);font-size:.82rem;line-height:1.6;margin-top:11px;text-align:center}
svg .b{fill:var(--panel);stroke:var(--rule);stroke-width:1.4}
svg .hl{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.4}
svg .wn{fill:var(--warn-soft);stroke:var(--warn);stroke-width:1.4}
svg .bd{fill:var(--bad-soft);stroke:var(--bad);stroke-width:1.4}
svg .nl{font:11px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ink)}
svg .sm{font:10px ui-monospace,SFMono-Regular,Menlo,monospace;fill:var(--ink-3)}
svg .edge{fill:none;stroke:var(--ink-3);stroke-width:1.6}
svg .ahead{fill:var(--ink-3);stroke:none}

/* ---- 摺疊 ---- */
.appendix{margin-top:42px;border-top:1px solid var(--rule);padding-top:22px}
.appendix > h2{font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 13px;border:0;padding:0}
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
.doc-in h2,.doc-in h3{color:var(--ink);font-size:.95rem;margin:16px 0 7px;border:0;padding:0}
.doc-in table{border-collapse:collapse;width:100%;margin:11px 0;font-size:.84rem}
.doc-in th,.doc-in td{border:1px solid var(--rule);padding:6px 9px;text-align:left;
  vertical-align:top}
.doc-in th{background:var(--sunk);font-weight:650;color:var(--ink)}
.doc-in pre{background:var(--sunk);padding:11px;border-radius:7px;overflow-x:auto;
  font-size:.82rem;line-height:1.5}
.doc-in blockquote{margin:11px 0;padding:.4em 1em;border-left:3px solid var(--rule);
  color:var(--ink-3)}
.doc-in ul,.doc-in ol{padding-left:1.35em}
.doc-in li{margin:4px 0}
.tablewrap{overflow-x:auto}

/* ---- 收尾 ---- */
.verdict{margin-top:34px;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);padding:19px 21px;box-shadow:var(--shadow)}
.verdict h2{margin:0 0 9px;font-size:1rem;border:0;padding:0}
.verdict p{margin:0 0 9px;color:var(--ink-2);font-size:.91rem}
.verdict p:last-child{margin-bottom:0}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media (max-width:560px){h1{font-size:1.35rem}}
"""

# 4-spec 的 S 卡樣式
CSS_SPEC = """
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
@media (max-width:560px){
  .s-body{padding-left:18px}
  .gwt-row{grid-template-columns:1fr;gap:2px}
}
"""

# 5-tasks 的 T 卡樣式
CSS_TASKS = """
.t-intent{padding:13px 18px;background:var(--accent-soft);
  border-bottom:1px solid var(--rule-2);font-size:.91rem;color:var(--ink)}
.t-intent .k{display:block;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
  font-weight:700;color:var(--accent);margin-bottom:4px}
.t-grid{display:grid;grid-template-columns:86px 1fr;gap:0;font-size:.88rem}
.t-grid .k{padding:9px 0 9px 18px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:.73rem;font-weight:700;color:var(--ink-3);letter-spacing:.05em;
  border-bottom:1px solid var(--rule-2);background:var(--sunk)}
.t-grid .v{padding:9px 18px 9px 12px;color:var(--ink-2);
  border-bottom:1px solid var(--rule-2);min-width:0;overflow-wrap:anywhere}
.t-grid .v:last-of-type,.t-grid .k:last-of-type{border-bottom:0}
.t-grid .v code{font-size:.8em}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.76rem;
  background:var(--accent-soft);color:var(--accent);padding:2px 7px;border-radius:5px;
  font-weight:650}
.chip.file{background:var(--sunk);color:var(--ink-2);font-weight:500}
.chip.none{background:var(--sunk);color:var(--ink-3);font-weight:500}
.vfy{background:var(--sunk);border-radius:6px;padding:8px 10px;display:block;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.76rem;
  line-height:1.55;color:var(--ink-2);overflow-x:auto;white-space:pre-wrap;
  overflow-wrap:anywhere}
.t-bound{border-top:1px solid var(--rule-2)}
.t-bound > summary{cursor:pointer;padding:11px 18px;font-size:.84rem;font-weight:600;
  color:var(--ink-2);list-style:none;display:flex;justify-content:space-between;gap:10px}
.t-bound > summary::-webkit-details-marker{display:none}
.t-bound > summary::after{content:"展開禁區";font-size:.75rem;color:var(--ink-3);font-weight:500}
.t-bound[open] > summary::after{content:"收合"}
.t-bound > summary:hover{background:var(--sunk)}
.t-bound .body{padding:2px 18px 15px;font-size:.87rem;color:var(--ink-2);line-height:1.7}
.t-bound .body code{font-size:.85em}
.danger-note{display:inline-block;font-size:.73rem;font-weight:700;color:var(--bad);
  background:var(--bad-soft);padding:2px 8px;border-radius:99px;margin-left:6px}
.t-done{width:17px;height:17px;accent-color:var(--accent);cursor:pointer;flex:none;
  margin-top:2px}
.r-block.t-block.done{opacity:.72}
.r-block.t-block.done .r-head{border-left-color:var(--ok)}
@media (max-width:560px){
  .t-grid{grid-template-columns:1fr}
  .t-grid .k{padding:9px 18px 2px;border-bottom:0;background:transparent}
  .t-grid .v{padding-left:18px}
}
"""


def local_page(title: str, extra_css: str, body: str, script: str = "") -> str:
    """本機直接開的完整 html 文件。"""
    js = f"<script>{script}</script>" if script else ""
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{CSS}{extra_css}</style>
</head>
<body>
{body}
{js}
</body>
</html>
"""


def artifact_page(title: str, extra_css: str, body: str, script: str = "") -> str:
    """Artifact 發布用片段（外層由 Artifact 自動包 doctype/html/head/body）。"""
    js = f"<script>{script}</script>" if script else ""
    return f"""<title>{title}</title>
<style>{CSS}{extra_css}</style>
{body}
{js}
"""
