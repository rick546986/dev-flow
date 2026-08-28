#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 7 站審頁產生器 —— 從 7-review.md 的 ## 截圖槽產出分組槽／lightbox／掛點。

契約:notes/design/stage7-review-ui-contract.md
牙:scripts/check-stage7-shot-contract.sh

這支只產第 7 站給人審的截圖槽頁。不進 build-gate-twin.py STAGES
(那支是 G3 五格卡)。不包 markdown-it + html-shell。
Human verdict 接 #60:正本是同目錄 md 頂欄 verdict:,只「提交判定」才寫。
不准發明編輯 URL。缺檔顯示佔位,不得留過期「未掛」句。不發明產品規則。
補助手樣常常沒有 ## 截圖槽、也沒有 ![]:md 內圖若有就用,沒有就掃同目錄
shots/ 七個定名收成五組。吐 .lb lightbox 與 .e2e 掛點,不要只認字面 hang-point。

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
    r"^[-*][ \t]+(data-shot|src|caption|進場|hang-point|e2e)[ \t]*[:：][ \t]*(.+)$",
    re.M,
)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
SHOT_PATH_RE = re.compile(r"(shots/[A-Za-z0-9._-]+\.(?:png|jpe?g|webp))", re.I)
DATA_SHOT_HTML_RE = re.compile(
    r'data-shot="([^"]+)"[^>]*data-full="([^"]+)"|'
    r'data-shot="([^"]+)"[\s\S]{0,240}?src="(shots/[^"]+)"',
    re.I,
)
E2E_LINE_RE = re.compile(
    r"(?:e2e|hang-point)[ \t]*[:：][ \t]*(\S+)|"
    r"`(e2e/[^`]+)`|"
    r"\b(e2e/[A-Za-z0-9._/-]+\.ts)\b",
    re.I,
)

# 契約鎖死的七個定名,收成五組。標題是輸出,不是契約句。
LOCKED_SHOTS = (
    "plus-two-cells",
    "v30-two-cells",
    "manual-keep",
    "age-lock",
    "opu-note",
    "plan-split-c",
    "plan-split-def",
)
LOCKED_GROUPS = (
    ("PLUS／3.0 兩格", ("plus-two-cells", "v30-two-cells")),
    ("手改不蓋", ("manual-keep",)),
    ("年齡鎖", ("age-lock",)),
    ("OPU 小字", ("opu-note",)),
    ("方案拆", ("plan-split-c", "plan-split-def")),
)
HARVEST_ENTRY = "進場:附表六 → 已生成附表五。不准新增。不准發明編輯 URL。"

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
.hang-point,.e2e{font-size:.82rem;color:var(--ink-2);margin:6px 0 0}
.lb,.lightbox{position:fixed;inset:0;background:rgba(16,20,28,.72);display:none;
  align-items:center;justify-content:center;z-index:40;padding:24px}
.lb.open,.lightbox.open{display:flex}
.lb img,.lightbox img{max-width:min(960px,100%);max-height:90vh;border-radius:8px}
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
  var box = document.querySelector('.lb') || document.getElementById('lightbox');
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


def _norm_src(src):
    src = (src or "").strip().strip("<>")
    if src.startswith("./"):
        src = src[2:]
    if src and not src.startswith("shots/") and "/" not in src:
        src = "shots/" + src
    if src and "/edit" in src.lower():
        die(1, "不准發明編輯 URL")
    return src


def _hang_in(block):
    match = E2E_LINE_RE.search(block or "")
    if not match:
        return ""
    return next((g for g in match.groups() if g), "")


def parse_field_slots(body):
    slots = []
    found = list(H3_RE.finditer(body or ""))
    for i, match in enumerate(found):
        title = match.group(1).strip()
        stop = found[i + 1].start() if i + 1 < len(found) else len(body)
        block = body[match.end():stop]
        fields = {key: val.strip() for key, val in FIELD_RE.findall(block)}
        src = _norm_src(fields.get("src") or "")
        shot = fields.get("data-shot") or ""
        if not src and not shot:
            continue
        slots.append({
            "title": title,
            "shot": shot or title,
            "src": src,
            "caption": fields.get("caption") or title,
            "entry": fields.get("進場") or "",
            "hang": fields.get("hang-point") or fields.get("e2e") or _hang_in(block),
        })
    return slots


def parse_image_slots(body):
    slots = []
    found = list(H3_RE.finditer(body or ""))
    if not found:
        found = list(H2_RE.finditer(body or ""))
    groups = []
    for i, match in enumerate(found):
        title = match.group(1).strip()
        if title in ("截圖槽", "Verdict", "Exit Checklist"):
            continue
        stop = found[i + 1].start() if i + 1 < len(found) else len(body)
        groups.append((title, body[match.end():stop]))
    if not groups:
        groups = [("截圖", body or "")]
    for title, block in groups:
        images = IMG_RE.findall(block)
        if not images:
            paths = SHOT_PATH_RE.findall(block)
            images = [("", path) for path in paths]
        if not images:
            continue
        hang = _hang_in(block)
        entry = ""
        for line in block.splitlines():
            if "進場" in line or "已存在" in line or "不准新增" in line:
                entry = line.strip(" -*")
                break
        for caption, src in images:
            src = _norm_src(src)
            if not src.startswith("shots/"):
                continue
            stem = pathlib.Path(src).stem
            slots.append({
                "title": title,
                "shot": stem,
                "src": src,
                "caption": caption or title,
                "entry": entry,
                "hang": hang,
            })
    return slots


def harvest_sibling_shots(md_path):
    if md_path is None:
        return []
    shots_dir = pathlib.Path(md_path).parent / "shots"
    if not shots_dir.is_dir():
        return []
    found = {}
    for stem in LOCKED_SHOTS:
        path = shots_dir / ("%s.png" % stem)
        if path.is_file():
            found[stem] = "shots/%s.png" % stem
    if len(found) != len(LOCKED_SHOTS):
        return []
    slots = []
    for title, stems in LOCKED_GROUPS:
        for stem in stems:
            slots.append({
                "title": title,
                "shot": stem,
                "src": found[stem],
                "caption": title,
                "entry": HARVEST_ENTRY,
                "hang": "e2e/%s.spec.ts" % stem,
            })
    return slots


def harvest_sibling_html(md_path):
    if md_path is None:
        return []
    html_path = pathlib.Path(md_path).with_suffix(".html")
    if not html_path.is_file():
        return []
    try:
        text = html_path.read_text(encoding="utf-8")
    except OSError:
        return []
    slots = []
    seen = set()
    for match in DATA_SHOT_HTML_RE.finditer(text):
        shot = match.group(1) or match.group(3)
        src = match.group(2) or match.group(4)
        src = _norm_src(src)
        if not shot or shot in seen:
            continue
        seen.add(shot)
        slots.append({
            "title": shot,
            "shot": shot,
            "src": src,
            "caption": shot,
            "entry": "",
            "hang": "",
        })
    return slots


def parse_slots(body, md_path=None):
    _, shot_body = section_named(body, ("截圖槽",))
    slots = parse_field_slots(shot_body) if shot_body else []
    if not slots:
        slots = parse_image_slots(body)
    if not slots:
        slots = harvest_sibling_shots(md_path)
    if not slots:
        slots = harvest_sibling_html(md_path)
    if not slots:
        die(1, "解析不到截圖槽(md 沒有 ## 截圖槽 與 ![] 時改掃同目錄 shots/ 七個定名)")
    return slots


def render_figure(slot):
    src = slot["src"] or ("shots/%s.png" % re.sub(r"[^a-z0-9-]+", "-", slot["shot"].lower()))
    return "".join([
        '<figure class="shot" data-shot="%s" data-full="%s">'
        % (esc(slot["shot"]), esc(src)),
        '<img src="%s" alt="%s" onerror="this.hidden=true;this.nextElementSibling.hidden=false">'
        % (esc(src), esc(slot["caption"])),
        '<div class="shot-ph" hidden>佔位</div>',
        "<figcaption>%s</figcaption>" % esc(slot["caption"]),
        "</figure>",
    ])


def render_groups(slots):
    grouped = []
    index = {}
    for slot in slots:
        key = slot["title"]
        if key not in index:
            index[key] = len(grouped)
            grouped.append({"title": key, "slots": []})
        grouped[index[key]]["slots"].append(slot)
    blocks = []
    for group in grouped:
        bits = [render_figure(slot) for slot in group["slots"]]
        entry = next((s["entry"] for s in group["slots"] if s.get("entry")), "")
        hang = next((s["hang"] for s in group["slots"] if s.get("hang")), "")
        if entry:
            bits.append("<p>%s</p>" % esc(entry))
        if hang:
            bits.append(
                '<p class="e2e hang-point" data-hang="%s">e2e: %s</p>'
                % (esc(hang), esc(hang))
            )
        anchor = group["slots"][0]["shot"]
        blocks.append(
            '<section class="r-block" id="%s">'
            '<div class="r-head"><span class="r-name">%s</span></div>'
            '<div class="r-body">%s</div></section>'
            % (esc(anchor), esc(group["title"]), "".join(bits))
        )
    return "\n".join(blocks)


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


def build_html(text, md_path=None):
    meta, body = parse_frontmatter(text)
    slug = meta.get("feature") or "7-review"
    verdict = meta.get("verdict") or ""
    slots = parse_slots(body, md_path=md_path)
    dash = (
        '<div class="dash">'
        '<div class="cell"><span class="k">verdict</span><span class="v">%s</span></div>'
        '<div class="cell"><span class="k">分組</span><span class="v">%d</span></div>'
        '<div class="cell"><span class="k">槽</span><span class="v">%d</span></div>'
        "</div>"
    ) % (
        esc(verdict or "PRE-REVIEW"),
        len({s["title"] for s in slots}),
        len(slots),
    )
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
<div class="lb lightbox" id="lightbox"><img alt=""></div>
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
        render_groups(slots),
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
        sys.stdout.write(build_html(text, md_path=path))
        return
    path = pathlib.Path(src)
    if not path.is_file():
        die(2, "讀不到 md:%s" % path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        die(2, "讀不到 md:%s" % err)
    html_out = build_html(text, md_path=path)
    dest = pathlib.Path(out) if out else path.with_suffix(".html")
    try:
        dest.write_text(html_out, encoding="utf-8")
    except OSError as err:
        die(2, "寫不出 html:%s" % err)
    print("wrote %s" % dest)


if __name__ == "__main__":
    main(sys.argv[1:])
