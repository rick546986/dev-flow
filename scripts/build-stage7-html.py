#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 7 站審頁產生器 —— 從 7-review.md 的 ## 截圖槽產出分組槽／lightbox／掛點。

契約:notes/design/stage7-review-ui-contract.md
牙:scripts/check-stage7-shot-contract.sh

這支只產第 7 站給人審的截圖槽頁。不進 build-gate-twin.py STAGES
(那支是 G3 五格卡)。不包 markdown-it + html-shell。
Human verdict 接 #60:正本是同目錄 md 頂欄 verdict:,只「提交判定」才寫。
不准發明編輯 URL。缺檔顯示佔位,不得留過期「未掛」句。不發明產品規則。

用法:
  scripts/build-stage7-html.py <7-review.md> [--out PATH]
  scripts/build-stage7-html.py --action <7-review.md> [--out PATH]
  scripts/build-stage7-html.py --fixture

--fixture 把 scripts/fixtures/stage7-html/review-page.md 印到 stdout。
給檔時預設寫同目錄 7-review.html(或 --out)。

exit:0 = 寫出 / 1 = 解析不到截圖槽 / 2 = 用法錯誤、檔案讀不到
"""
from __future__ import print_function

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "scripts" / "fixtures" / "stage7-html" / "review-page.md"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
H2_RE = re.compile(r"^##[ \t]+(.+?)\s*$", re.M)
H3_RE = re.compile(r"^###[ \t]+(.+?)\s*$", re.M)
FIELD_RE = re.compile(
    r"^[-*][ \t]+(data-shot|src|caption|進場|hang-point)[ \t]*[:：][ \t]*(.+)$",
    re.M,
)

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
.r-body{padding:14px 18px 16px}
.shot{margin:0 0 12px;cursor:pointer}
.shot img{max-width:100%;border:1px solid var(--rule);border-radius:8px;display:block}
.shot-ph{background:var(--sunk);border:1px dashed var(--rule);border-radius:8px;
  padding:28px;text-align:center;color:var(--ink-3)}
.hang-point{font-size:.82rem;color:var(--ink-2);margin:6px 0 0}
.lightbox{position:fixed;inset:0;background:rgba(16,20,28,.72);display:none;
  align-items:center;justify-content:center;z-index:40;padding:24px}
.lightbox.open{display:flex}
.lightbox img{max-width:min(960px,100%);max-height:90vh;border-radius:8px}
.foot{margin:36px 0 0;padding:16px 18px;border:1px solid var(--rule);
  border-radius:12px;background:var(--panel)}
.gv-row{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0}
.gv-field{display:block;margin:8px 0}
.btn{background:var(--accent);color:#fff;border:0;border-radius:8px;
  padding:8px 14px;font-weight:650;cursor:pointer}
.gv-status{color:var(--ink-2);font-size:.86rem}
.src{color:var(--ink-3);font-size:.8rem;margin-top:26px;text-align:center}
"""

SCRIPT_LIGHTBOX = r"""
(function(){
  var box = document.getElementById('lightbox');
  if (!box) return;
  var img = box.querySelector('img');
  document.querySelectorAll('.shot[data-shot]').forEach(function(el){
    el.addEventListener('click', function(){
      var src = el.getAttribute('data-full') || (el.querySelector('img') || {}).src;
      if (!src) return;
      img.src = src;
      box.classList.add('open');
    });
  });
  box.addEventListener('click', function(){ box.classList.remove('open'); });
})();
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
        "用法:build-stage7-html.py <7-review.md> [--out PATH]\n"
        "     build-stage7-html.py --action <7-review.md> [--out PATH]\n"
        "     build-stage7-html.py --fixture\n"
        "契約:notes/design/stage7-review-ui-contract.md\n"
        "產檔器吐分組槽／data-shot／lightbox／hang-point。提交判定寫 md 頂欄 verdict:。\n"
        "不進 build-gate-twin.py STAGES,不包 markdown-it + html-shell。",
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
    wanted = {name.lower() for name in names}
    found = list(H2_RE.finditer(text or ""))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        key = title.split("(", 1)[0].strip().lower()
        if key not in wanted and title.lower() not in wanted:
            continue
        stop = found[i + 1].start() if i + 1 < len(found) else len(text)
        return title, text[match.end():stop]
    return None, ""


def parse_slots(body):
    slots = []
    found = list(H3_RE.finditer(body or ""))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        stop = found[i + 1].start() if i + 1 < len(found) else len(body)
        block = body[match.end():stop]
        fields = {key: val.strip() for key, val in FIELD_RE.findall(block)}
        src = fields.get("src") or ""
        if src and not src.startswith("shots/"):
            src = "shots/" + src.lstrip("/")
        if src and "/edit" in src.lower():
            die(1, "不准發明編輯 URL")
        slots.append({
            "title": title,
            "shot": fields.get("data-shot") or title,
            "src": src,
            "caption": fields.get("caption") or title,
            "entry": fields.get("進場") or "",
            "hang": fields.get("hang-point") or "",
        })
    return slots


def render_slot(slot):
    src = slot["src"] or ("shots/%s.png" % re.sub(r"[^a-z0-9-]+", "-", slot["shot"].lower()))
    entry = slot["entry"]
    hang = slot["hang"]
    bits = [
        '<figure class="shot" data-shot="%s" data-full="%s">'
        % (esc(slot["shot"]), esc(src)),
        '<img src="%s" alt="%s" onerror="this.hidden=true;this.nextElementSibling.hidden=false">'
        % (esc(src), esc(slot["caption"])),
        '<div class="shot-ph" hidden>佔位</div>',
        "<figcaption>%s</figcaption>" % esc(slot["caption"]),
        "</figure>",
    ]
    if entry:
        bits.append("<p>%s</p>" % esc(entry))
    if hang:
        bits.append(
            '<p class="hang-point" data-hang="%s">e2e hang-point: %s</p>'
            % (esc(hang), esc(hang))
        )
    return (
        '<section class="r-block" id="%s">'
        '<div class="r-head"><span class="r-name">%s</span></div>'
        '<div class="r-body">%s</div></section>'
    ) % (esc(slot["shot"]), esc(slot["title"]), "".join(bits))


def verdict_footer(slug):
    return """<footer class="foot gate-verdict" id="gate-verdict"
  data-slug="%s" data-stage="7-review" data-source-sha="">
  <p class="gv-canon">正本是同目錄 <code>7-review.md</code> 頂欄
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


def build_html(text):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "7-review"
    verdict = meta.get("verdict") or ""
    _, shot_body = section_named(body, ("截圖槽",))
    if shot_body is None or shot_body == "":
        die(1, "解析不到 ## 截圖槽")
    slots = parse_slots(shot_body)
    if not slots:
        die(1, "解析不到截圖槽分組")
    dash = (
        '<div class="dash">'
        '<div class="cell"><span class="k">verdict</span><span class="v">%s</span></div>'
        '<div class="cell"><span class="k">分組</span><span class="v">%d</span></div>'
        "</div>"
    ) % (esc(verdict or "PRE-REVIEW"), len(slots))
    page = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · 7-review</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <p class="eyebrow">dev-flow · 7-review · 審查介面</p>
  <h1>%s</h1>
  <p class="sub">正本是 md。截圖槽分組 + 定名檔 + lightbox + e2e 掛點。</p>
  %s
</header>
%s
<div class="lightbox" id="lightbox"><img alt=""></div>
%s
<p class="src">由 <code>scripts/build-stage7-html.py</code> 從 md ## 截圖槽解析產生,不包 html-shell。</p>
</div>
<script>%s</script>
<script>%s</script>
</body>
</html>
""" % (
        esc(slug),
        CSS,
        esc(slug),
        dash,
        "\n".join(render_slot(s) for s in slots),
        verdict_footer(slug),
        SCRIPT_LIGHTBOX,
        SCRIPT_VERDICT,
    )
    if "未掛" in page:
        die(1, "不得留過期未掛句")
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
