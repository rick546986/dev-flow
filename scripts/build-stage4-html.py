#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 站審頁產生器 —— 從 4-spec.md 產出 R/S 卡 + 生命週期直式 SVG。

契約:notes/design/stage4-review-ui-contract.md
牙:scripts/check-stage4-rs-contract.sh

這支只產第 4 站給人審的頁。不進 build-gate-twin.py STAGES
(那支是 G2 五格卡)。不包 markdown-it + html-shell。
chrome 跟第 2／5／7 站同一套 token。生命週期四格:新生 → 改行為 → 退役 → 不動。
補助標題「補助模組生命週期（預覽）」四條要能印成圖,不要只認自創標題。
Human verdict 接 #60:正本是同目錄 md 頂欄 verdict:,只「提交判定」才寫。
不要重做 sidecar。第 1 站三框不併進這份。不發明產品規則。

用法:
  scripts/build-stage4-html.py <4-spec.md> [--out PATH]
  scripts/build-stage4-html.py --action <4-spec.md> [--out PATH]
  scripts/build-stage4-html.py --fixture

--fixture 把 scripts/fixtures/stage4-html/spec-page.md 印到 stdout。
給檔時預設寫同目錄 4-spec.html(或 --out)。

exit:0 = 寫出 / 1 = 解析不到 R/S / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "scripts" / "fixtures" / "stage4-html" / "spec-page.md"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
H2_RE = re.compile(r"^##[ \t]+(.+?)\s*$", re.M)
R_HEAD_RE = re.compile(r"^###[ \t]+(R-\d+\S*)\b[ \t]*(.*)$", re.M)
S_HEAD_RE = re.compile(r"^####[ \t]+(S-\d+\S*)\b[ \t]*(.*)$", re.M)
FIELD_RE = re.compile(
    r"^[-*][ \t]+(GIVEN|WHEN|THEN|觀測)[ \t]*[:：]?[ \t]*(.*)$",
    re.M,
)
SLOT_ORDER = ("新生", "改行為", "退役", "不動")
# 補助實寫:新生（這輪沒有）：／改行為（相關一格）：／退役：／不動：
# 括號可有可無,全形／半形都算。不要只認「新生：」。
SLOT_RE = re.compile(
    r"^(?:[-*]\s*)?(新生|改行為|退役|不動)"
    r"(?:\s*[（(][^）)]*[）)])?\s*[:：]\s*(.+)$"
)
EMPTY_SLOT = ("", "沒有", "不加欄")
TOKEN_RE = re.compile(r"[A-Za-z0-9._-]+|[^A-Za-z0-9._-]")
LIFE_KEYS = (
    "補助模組生命週期",
    "模組生命週期",
    "生命週期",
)

CANVAS_W = 280
BOX_W = 200
BOX_X = 40
CX = 140
TOP = 10
GAP = 22
PAD_TOP = 12
TITLE_H = 16
LINE_H = 14
PAD_BOTTOM = 12

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
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:15px/1.65 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.86em;background:var(--sunk);border-radius:3px;padding:1px 5px}
.wrap{max-width:900px;margin:0 auto;padding:0 20px 96px}
.masthead{padding:34px 0 20px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin:0 0 8px}
h1{font-size:1.62rem;line-height:1.3;margin:0 0 10px}
.sub{color:var(--ink-2);margin:0;font-size:.94rem}
.dash{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));
  margin:18px 0 0}
.cell{background:var(--panel);border:1px solid var(--rule);border-radius:9px;
  padding:10px 12px}
.cell .k{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3)}
.cell .v{font-size:1.02rem;font-weight:650;line-height:1.3;display:block}
a.cell{text-decoration:none;color:inherit}
a.cell:hover{border-color:var(--accent)}
.r-block{margin:30px 0 0;border:1px solid var(--rule);border-radius:12px;
  background:var(--panel);overflow:hidden;box-shadow:var(--shadow)}
.r-head{padding:15px 18px;border-bottom:1px solid var(--rule-2);
  border-left:4px solid var(--accent)}
.r-name{font-weight:650;text-decoration:none}
.r-body{padding:14px 18px 16px;overflow-wrap:anywhere;word-break:break-word}
.r-body p{margin:0 0 8px}
.s-card{border:1px solid var(--rule-2);border-radius:8px;padding:10px 12px;
  margin:0 0 10px;background:var(--sunk)}
.s-card h3{margin:0 0 8px;font-size:.95rem}
.gwt{margin:0 0 6px}
.gwt .k{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-3);display:block}
.ask{margin:8px 0 0;padding:8px 10px;border-left:3px solid var(--accent);
  background:var(--accent-soft)}
.figwrap{display:flex;justify-content:center;margin:8px 0}
.vbox{width:100%;max-width:360px;height:auto;display:block}
.vbox .b{fill:var(--panel);stroke:var(--rule);stroke-width:1.2}
.vbox .hl{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.4}
.vbox .nl{font-size:12px;fill:var(--ink);font-weight:650}
.vbox .sm{font-size:10px;fill:var(--ink-2)}
.vbox .flow{stroke:var(--ink-3);stroke-width:1.2;fill:none}
.miss{background:var(--bad-soft);color:var(--bad);padding:2px 6px;border-radius:4px}
.foot{margin:36px 0 0;padding:16px 18px;border:1px solid var(--rule);
  border-radius:12px;background:var(--panel)}
.gv-row{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0}
.gv-field{display:block;margin:8px 0}
.btn{background:var(--accent);color:#fff;border:0;border-radius:8px;
  padding:8px 14px;font-weight:650;cursor:pointer}
.gv-status{color:var(--ink-2);font-size:.86rem}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
"""

SCRIPT_VERDICT = r"""
(function(){
  var panel = document.getElementById('gate-verdict');
  if (!panel) return;
  var statusEl = document.getElementById('gv-status');
  function status(msg){ if (statusEl) statusEl.textContent = msg; }
  function patchMd(text, verdict, notes){
    if (text.slice(0, 4) !== '---\n') throw new Error('no frontmatter');
    var end = text.indexOf('\n---\n', 3);
    if (end < 0) throw new Error('unclosed frontmatter');
    var fm = text.slice(4, end);
    var rest = text.slice(end + 5);
    if (/^verdict:\s*/m.test(fm)) {
      fm = fm.replace(/^verdict:\s*.*$/m, 'verdict: ' + verdict);
    } else if (/^status:\s*/m.test(fm)) {
      fm = fm.replace(/^(status:\s*.*)$/m, '$1\nverdict: ' + verdict);
    } else {
      fm = 'verdict: ' + verdict + '\n' + fm;
    }
    if (notes) {
      var line = '- Human verdict note: ' + notes.split('\n')[0];
      if (/^- Human verdict note:/m.test(rest)) {
        rest = rest.replace(/^- Human verdict note:.*$/m, line);
      } else {
        rest = line + '\n' + rest;
      }
    }
    return '---\n' + fm + '\n---\n' + rest;
  }
  function payload(verdict){
    return {
      slug: panel.dataset.slug,
      gate: panel.dataset.stage,
      verdict: verdict,
      notes: ((document.getElementById('gv-notes') || {}).value || '').trim(),
      reviewer: ((document.getElementById('gv-reviewer') || {}).value || '').trim(),
      checked: [],
      source_sha: panel.dataset.sourceSha || '',
      sidecar: true
    };
  }
  function postVerdict(body){
    var urls = ['/devflow-gate/verdict'];
    if (location.protocol === 'file:') {
      urls.push('http://127.0.0.1:8765/devflow-gate/verdict');
    }
    var i = 0;
    function next(){
      if (i >= urls.length) return Promise.reject(new Error('no serve'));
      var url = urls[i++];
      return fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      }).then(function(r){
        if (!r.ok) throw new Error('http ' + r.status);
        return r.json();
      }).catch(function(){ return next(); });
    }
    return next();
  }
  async function writeViaFsa(body){
    if (!window.showDirectoryPicker) {
      throw new Error('no File System Access');
    }
    var dir = await window.showDirectoryPicker({id: 'devflow-gate-' + body.slug});
    var mdName = body.gate + '.md';
    var fh = await dir.getFileHandle(mdName);
    var file = await fh.getFile();
    var next = patchMd(await file.text(), body.verdict, body.notes);
    var w = await fh.createWritable();
    await w.write(next);
    await w.close();
    return mdName;
  }
  var submit = document.getElementById('gv-submit');
  if (!submit) return;
  submit.addEventListener('click', function(){
    var picked = document.querySelector('input[name="gv-verdict"]:checked');
    if (!picked) {
      status('請先選 PASS / REQUEST_CHANGES / HOLD。全勾不算 PASS。');
      return;
    }
    var body = payload(picked.value);
    status('寫入中…');
    postVerdict(body).then(function(res){
      status('已寫入 ' + (res.path || (body.gate + '.md')) +
        ' 的 verdict: ' + body.verdict + '。正本是 md，不是勾選、不是 sidecar。');
    }).catch(function(){
      writeViaFsa(body).then(function(name){
        status('已用 File System Access 寫入 ' + name +
          ' 的 verdict: ' + body.verdict + '。正本是 md。');
      }).catch(function(){
        status('寫不進 md。請跑 python3 scripts/devflow_gate.py serve <專案根> 再開這頁。勾選不是判定。');
      });
    });
  });
})();
"""


def usage():
    print(
        "用法:build-stage4-html.py <4-spec.md> [--out PATH]\n"
        "     build-stage4-html.py --action <4-spec.md> [--out PATH]\n"
        "     build-stage4-html.py --fixture\n"
        "契約:notes/design/stage4-review-ui-contract.md\n"
        "產檔器吐 R/S 卡 + 審的時候看什麼 + GIVEN/WHEN/THEN + 生命週期直式 SVG。\n"
        "提交判定寫 md 頂欄 verdict:。不進 build-gate-twin.py STAGES,不包 html-shell。",
        file=sys.stderr,
    )


def die(code, msg):
    print(msg, file=sys.stderr)
    sys.exit(code)


def esc(text):
    return html.escape(text or "", quote=False)


def parse_frontmatter(text):
    match = FM_RE.match(text or "")
    if not match:
        return {}, text or ""
    meta = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, text[match.end():]


def section_named(text, names):
    wanted = []
    for name in names:
        wanted.append(name.lower())
        wanted.append(name.lower().replace("（", "(").replace("）", ")"))
        wanted.append(name.lower().replace("(", "（").replace(")", "）"))
    wanted = set(wanted)
    found = list(H2_RE.finditer(text or ""))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        key = title.split("(", 1)[0].split("（", 1)[0].strip().lower()
        full = title.lower()
        if key not in wanted and full not in wanted:
            if not any(full.startswith(n) or n in full for n in wanted):
                continue
        stop = found[i + 1].start() if i + 1 < len(found) else len(text)
        return title, text[match.end():stop]
    return None, ""


def parse_scenarios(block):
    found = list(S_HEAD_RE.finditer(block or ""))
    scenarios = []
    for i, match in enumerate(found):
        sid = match.group(1).strip()
        rest = (match.group(2) or "").strip()
        stop = found[i + 1].start() if i + 1 < len(found) else len(block)
        body = block[match.end():stop]
        fields = {}
        for key, val in FIELD_RE.findall(body):
            fields[key] = val.strip()
        scenarios.append({
            "id": sid,
            "title": rest,
            "given": fields.get("GIVEN", ""),
            "when": fields.get("WHEN", ""),
            "then": fields.get("THEN", ""),
            "ask": fields.get("觀測", ""),
        })
    return scenarios


def parse_requirements(text):
    found = list(R_HEAD_RE.finditer(text or ""))
    reqs = []
    for i, match in enumerate(found):
        rid = match.group(1).strip()
        rest = (match.group(2) or "").strip()
        rest = re.sub(r"^[:：]\s*", "", rest)
        stop = found[i + 1].start() if i + 1 < len(found) else len(text)
        scenarios = parse_scenarios(text[match.end():stop])
        reqs.append({"id": rid, "title": rest, "scenarios": scenarios})
    return reqs


def collapse_cell(raw):
    """有關聯的收成一格,不拆檔名。空字才改寫「沒有」;「不加欄」原樣留。"""
    text = re.sub(r"\s+", " ", (raw or "").strip())
    text = re.sub(r"[`]+", "", text)
    return text or "沒有"


def slot_blank(val):
    return collapse_cell(val).rstrip("。.") in EMPTY_SLOT


def parse_lifecycle(body):
    slots = {name: "" for name in SLOT_ORDER}
    unlabeled = []
    notes = []
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = SLOT_RE.match(line)
        if match:
            slots[match.group(1)] = collapse_cell(match.group(2))
            continue
        unlabeled.append(line)
    if not any(slots.values()) and len(unlabeled) >= 4:
        for name, line in zip(SLOT_ORDER, unlabeled[:4]):
            slots[name] = collapse_cell(re.sub(r"^[-*]\s*", "", line))
        notes = unlabeled[4:]
    elif not any(slots.values()) and unlabeled:
        # 四條沒標名就按序;多出來當說明,不另開格
        packed = [collapse_cell(re.sub(r"^[-*]\s*", "", x)) for x in unlabeled[:4]]
        while len(packed) < 4:
            packed.append("沒有")
        for name, val in zip(SLOT_ORDER, packed):
            slots[name] = val
        notes = unlabeled[4:]
    else:
        for name in SLOT_ORDER:
            if not slots[name]:
                slots[name] = "沒有"
        notes = [ln for ln in unlabeled if not SLOT_RE.match(ln)]
    return slots, " ".join(notes)


def pick_hl(slots):
    """這輪新功能落點。.hl 不釘在「沒有／不加欄」空格。"""
    for name in SLOT_ORDER:
        val = slots.get(name, "")
        if slot_blank(val):
            continue
        if "這輪" in val or "新功能" in val:
            return name
    if not slot_blank(slots.get("改行為", "")):
        return "改行為"
    for name in SLOT_ORDER:
        if not slot_blank(slots.get(name, "")):
            return name
    return "改行為"


def wrap_lines(text, width=14):
    """直式小字。數字／代號(如 27004)整段留下,不從中間折。"""
    text = collapse_cell(text)
    if len(text) <= width:
        return [text]
    tokens = TOKEN_RE.findall(text)
    lines = []
    cur = ""
    for tok in tokens:
        if not cur:
            cur = tok
            continue
        if len(cur) + len(tok) <= width:
            cur += tok
            continue
        lines.append(cur)
        cur = tok
        if len(lines) == 2:
            used = "".join(lines)
            rest = text[len(used):]
            lines.append(rest or cur)
            return [part for part in lines if part][:3] or ["沒有"]
    if cur:
        lines.append(cur)
    return [part for part in lines if part][:3] or ["沒有"]


def render_lifecycle_svg(slots):
    hl = pick_hl(slots)
    steps = []
    for name in SLOT_ORDER:
        steps.append((name, wrap_lines(slots.get(name) or "沒有")))
    box_h = PAD_TOP + TITLE_H + 3 * LINE_H + PAD_BOTTOM
    height = TOP + len(steps) * box_h + (len(steps) - 1) * GAP + TOP
    parts = [
        '<svg class="vbox" viewBox="0 0 %d %d" role="img" aria-label="模組生命週期">'
        % (CANVAS_W, height),
    ]
    y = TOP
    for i, (title, lines) in enumerate(steps):
        kind = "hl" if title == hl else "b"
        parts.append(
            '  <rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="8"/>'
            % (kind, BOX_X, y, BOX_W, box_h)
        )
        parts.append(
            '  <text class="nl" text-anchor="middle" x="%d" y="%d">%s</text>'
            % (CX, y + PAD_TOP + 12, esc(title))
        )
        for j, line in enumerate(lines):
            parts.append(
                '  <text class="sm" text-anchor="middle" x="%d" y="%d">%s</text>'
                % (CX, y + PAD_TOP + TITLE_H + (j + 1) * LINE_H, esc(line))
            )
        if i < len(steps) - 1:
            y1 = y + box_h
            y2 = y1 + GAP
            parts.append(
                '  <path class="flow" d="M%d,%d L%d,%d"/>' % (CX, y1, CX, y2)
            )
        y += box_h + GAP
    parts.append("</svg>")
    return "\n".join(parts)


def gwt_row(key, val):
    if val:
        return '<p class="gwt"><span class="k">%s</span>%s</p>' % (esc(key), esc(val))
    return (
        '<p class="gwt"><span class="k">%s</span>'
        '<span class="miss">缺 %s</span></p>' % (esc(key), esc(key))
    )


def render_scenario(scen):
    ask = scen["ask"] or "—"
    return (
        '<article class="s-card" id="%s">'
        "<h3>%s</h3>"
        '<p class="ask"><strong>審的時候看什麼</strong> %s</p>'
        "%s%s%s"
        "</article>"
    ) % (
        esc(scen["id"]),
        esc(scen["id"] + ((" " + scen["title"]) if scen["title"] else "")),
        esc(ask),
        gwt_row("GIVEN", scen["given"]),
        gwt_row("WHEN", scen["when"]),
        gwt_row("THEN", scen["then"]),
    )


def render_req(req):
    cards = "".join(render_scenario(s) for s in req["scenarios"]) or "<p>—</p>"
    title = (req["id"] + " " + req["title"]).strip()
    return (
        '<section class="r-block" id="%s">'
        '<div class="r-head"><span class="r-name">%s</span></div>'
        '<div class="r-body">%s</div></section>'
    ) % (esc(req["id"]), esc(title), cards)


def verdict_footer(slug):
    return """<footer class="foot gate-verdict" id="gate-verdict"
  data-slug="%s" data-stage="4-spec" data-source-sha="">
  <p class="gv-canon">正本是同目錄 <code>4-spec.md</code> 頂欄
  <code>verdict:</code>。勾選只是瀏覽器草稿。全勾不算 PASS。
  只有「提交判定」才寫入 Human verdict。sidecar／HTML／localStorage 都不是正本;
  sidecar 與 md 衝突時 md 勝。</p>
  <div class="gv-row" role="radiogroup" aria-label="Human verdict">
    <label><input type="radio" name="gv-verdict" value="PASS"> PASS</label>
    <label><input type="radio" name="gv-verdict" value="REQUEST_CHANGES"> REQUEST_CHANGES</label>
    <label><input type="radio" name="gv-verdict" value="HOLD"> HOLD</label>
  </div>
  <label class="gv-field">備註 <input id="gv-notes" type="text" maxlength="200"></label>
  <label class="gv-field">審查者 <input id="gv-reviewer" type="text" maxlength="80"></label>
  <button type="button" class="btn" id="gv-submit">提交判定</button>
  <p id="gv-status" class="gv-status"></p>
</footer>""" % esc(slug)


def default_lifecycle(reqs):
    added = [r["id"] for r in reqs]
    label = "、".join(added[:3]) if added else "這輪新功能落點"
    return {
        "新生": "沒有",
        "改行為": collapse_cell(label + "(這輪新功能落點)"),
        "退役": "沒有",
        "不動": "其餘既有模組",
    }, "主詞是這個 feat 的那個模組。有關聯的收成一格,不拆檔名。"


def build_html(text):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "4-spec"
    status = meta.get("status") or ""
    verdict = meta.get("verdict") or ""
    reqs = parse_requirements(body)
    if not reqs or not any(r["scenarios"] for r in reqs):
        die(1, "解析不到 R/S")
    life_title, life_body = section_named(body, LIFE_KEYS)
    if life_body:
        slots, notes = parse_lifecycle(life_body)
    else:
        slots, notes = default_lifecycle(reqs)
    s_count = sum(len(r["scenarios"]) for r in reqs)
    dash = (
        '<div class="dash">'
        '<div class="cell"><span class="k">狀態</span><span class="v">%s</span></div>'
        '<div class="cell"><span class="k">verdict</span><span class="v">%s</span></div>'
        '<div class="cell"><span class="k">R</span><span class="v">%d</span></div>'
        '<div class="cell"><span class="k">S</span><span class="v">%d</span></div>'
        "</div>"
    ) % (esc(status or "draft"), esc(verdict or "PRE-REVIEW"), len(reqs), s_count)
    fig = (
        '<section class="r-block" id="lifecycle">'
        '<div class="r-head"><span class="r-name">%s</span></div>'
        '<div class="r-body"><div class="figwrap">\n%s\n</div></div></section>'
    ) % (esc(life_title or "模組生命週期"), render_lifecycle_svg(slots))
    note = notes or "主詞是這個 feat 的那個模組。有關聯的收成一格,不拆檔名。"
    note_card = (
        '<section class="r-block" id="lifecycle-note">'
        '<div class="r-head"><span class="r-name">生命週期說明</span></div>'
        '<div class="r-body"><p>%s</p></div></section>'
    ) % esc(note)
    page = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 4-spec</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · 4-spec · 審查介面</p>
  <h1>%s</h1>
  <p class="sub">正本是 md。這頁是 R/S 卡 + 生命週期直式圖,不是 gate-twin 勾選卡。</p>
  %s
</header>
%s
%s
%s
%s
<p class="src">由 <code>scripts/build-stage4-html.py</code> 從 md 解析產生,不包 html-shell。</p>
</div>
<script>%s</script>
</body>
</html>
""" % (
        esc(slug),
        CSS,
        esc(slug),
        dash,
        fig,
        note_card,
        "\n".join(render_req(r) for r in reqs),
        verdict_footer(slug),
        SCRIPT_VERDICT,
    )
    return page


def parse_args(argv):
    if not argv or argv[0] in ("-h", "--help"):
        usage()
        sys.exit(2)
    out = None
    fixture = False
    paths = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--fixture":
            fixture = True
            i += 1
            continue
        if arg == "--action":
            i += 1
            if i < len(argv) and not argv[i].startswith("-"):
                paths.append(argv[i])
                i += 1
            continue
        if arg == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
            i += 2
            continue
        if arg.startswith("-"):
            usage()
            sys.exit(2)
        paths.append(arg)
        i += 1
    if fixture:
        return "fixture", out
    if len(paths) != 1:
        usage()
        sys.exit(2)
    return paths[0], out


def main(argv):
    src, out = parse_args(argv)
    if src == "fixture":
        path = FIXTURE
        if not path.is_file():
            die(2, "讀不到 fixture:%s" % path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as err:
            die(2, "讀不到 fixture:%s" % err)
        sys.stdout.write(build_html(text))
        return
    path = pathlib.Path(src)
    if not path.is_file():
        die(2, "讀不到 md:%s" % path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        die(2, "讀不到 md:%s" % err)
    html_out = build_html(text)
    dest = pathlib.Path(out) if out else path.with_suffix(".html")
    try:
        dest.write_text(html_out, encoding="utf-8")
    except OSError as err:
        die(2, "寫不出 html:%s" % err)
    print("wrote %s" % dest)


if __name__ == "__main__":
    main(sys.argv[1:])
