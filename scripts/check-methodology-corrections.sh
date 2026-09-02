#!/bin/bash
# Batch-specific validation for the 2026-07-31 methodology-correction derivatives.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
python3 - "$ROOT" <<'PY'
import html
import os
import re
import subprocess
import sys
import unicodedata
from html.parser import HTMLParser

root = sys.argv[1]
checks = 0
failures = []


def check(condition, label, detail=""):
    global checks
    checks += 1
    if not condition:
        failures.append(label + (f": {detail}" if detail else ""))


def read(rel):
    with open(os.path.join(root, rel), encoding="utf-8") as stream:
        return stream.read()


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0
        self.lists = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.hidden += 1
        elif tag == "ol":
            values = dict(attrs)
            self.lists.append(["ol", int(values.get("start", "1"))])
        elif tag == "ul":
            self.lists.append(["ul", None])
        elif tag == "li" and self.lists and self.lists[-1][0] == "ol":
            self.parts.append(f"{self.lists[-1][1]}.")
            self.lists[-1][1] += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self.hidden:
            self.hidden -= 1
        elif tag in ("ol", "ul") and self.lists:
            self.lists.pop()

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def visible(fragment):
    parser = VisibleText()
    parser.feed(fragment)
    return " ".join(parser.parts)


def markdown_visible(source):
    source = re.sub(r"<!--.*?-->", "", source, flags=re.S)
    table_lines = []
    for line in source.splitlines():
        if re.match(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$", line):
            continue
        if line.lstrip().startswith("|"):
            line = line.strip().strip("|").replace("|", "")
        table_lines.append(line)
    source = "\n".join(table_lines)
    source = re.sub(r"^\s*>\s?", "", source, flags=re.M)
    source = re.sub(r"^\s*[-*+]\s+", "", source, flags=re.M)
    source = re.sub(r"^\s*```[^\n]*$", "", source, flags=re.M)
    source = re.sub(r"`([^`]*)`", r"\1", source)
    source = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", source)
    source = source.replace("**", "").replace("__", "")
    return html.unescape(source)


def norm(source):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", source))


def marker_fragment(rel, marker):
    source = read(rel)
    pattern = re.compile(
        rf"<!-- parity:start {re.escape(marker)} -->\s*(.*?)\s*"
        rf"<!-- parity:end {re.escape(marker)} -->", re.S)
    matches = pattern.findall(source)
    check(len(matches) == 1, f"{rel}:{marker} marker 唯一", f"found {len(matches)}")
    return matches[0] if len(matches) == 1 else ""


def quote_region(rel, start, stop=None):
    lines = read(rel).splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(">") and start in line]
    if len(starts) != 1:
        return ""
    selected = []
    for line in lines[starts[0]:]:
        if not line.startswith(">"):
            break
        if stop and stop in line:
            break
        selected.append(line)
    while selected and selected[-1].strip() == ">":
        selected.pop()
    return "\n".join(selected) + "\n"


def markdown_table(rel, heading, first_cell):
    lines = read(rel).splitlines()
    section = False
    selected = []
    for line in lines:
        if line.startswith("## "):
            section = line.startswith(heading)
        if section and line.startswith("|"):
            if selected or first_cell in line:
                selected.append(line)
        elif selected:
            break
    return "\n".join(selected) + "\n"


def bullet(rel, anchor):
    lines = read(rel).splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("- ") and anchor in line]
    if len(starts) != 1:
        return ""
    selected = [lines[starts[0]]]
    for line in lines[starts[0] + 1:]:
        if line.startswith("- ") or line.startswith("## "):
            break
        if not line.strip():
            break
        selected.append(line)
    return "\n".join(selected) + "\n"


def fenced_seam():
    source = read("docs/dev/readme-contract-extract.md")
    matches = re.findall(r"```text\n(RED → GREEN.*?review evidence)\n```", source, re.S)
    return ("```text\n" + matches[0] + "\n```\n") if len(matches) == 1 else ""


def exit_checklist():
    # 抽整個 `## Exit Checklist` 區段(支援多行項目的續行)。舊版只吃連續單行,
    # 遇到第一個多行項目就停 —— 會讓 quickstart 靜默只剩第一項而 parity 仍綠。
    source = read("_templates/7-review.md")
    section = re.search(r"^## Exit Checklist[^\n]*\n(.*?)(?=^## |\Z)", source, re.M | re.S)
    if not section:
        return ""
    body = section.group(1)
    first = re.search(r"^- \[ \]", body, re.M)
    return body[first.start():].rstrip("\n") + "\n" if first else ""


def exit_checklist_items():
    """模板 Exit Checklist 的**頂層**項目(行首 `- [ ]`,不含續行)。"""
    return re.findall(r"^- \[ \] (.*)$", exit_checklist(), re.M)


parity = {
    ("guides/guide-dev-flow.html", "template2-checklist"):
        quote_region("_templates/2-decision.md", "執行清單("),
    ("guides/guide-dev-flow.html", "template3-checklist"):
        quote_region("_templates/3-prototype.md", "執行清單("),
    ("guides/guide-dev-flow.html", "template4-laws"):
        quote_region("_templates/4-spec.md", "反模糊三律(", "執行清單("),
    ("guides/guide-dev-flow.html", "template4-checklist"):
        quote_region("_templates/4-spec.md", "執行清單(", "起草前估"),
    ("guides/guide-dev-flow.html", "template5-checklist"):
        quote_region("_templates/5-tasks.md", "執行清單("),
    ("guides/guide-dev-flow.html", "template6-checklist"):
        quote_region("_templates/6-implementation-notes.md", "執行清單(", "實作期規則("),
    ("guides/guide-dev-flow.html", "template6-rules"):
        quote_region("_templates/6-implementation-notes.md", "實作期規則("),
    ("guides/guide-dev-flow.html", "template7-checklist"):
        quote_region("_templates/7-review.md", "執行清單("),
    ("guides/guide-dev-flow.html", "readme-reviewer-selection-flow"):
        bullet("docs/dev/readme-contract-extract.md", "審查者產生"),
    ("guides/guide-dev-flow.html", "readme-stage6-seam-quickstart"): fenced_seam(),
    ("guides/guide-dev-flow.html", "readme-reviewer-selection-quickstart"):
        bullet("docs/dev/readme-contract-extract.md", "審查者產生"),
    ("guides/guide-dev-flow.html", "readme-gate-model-quickstart"):
        bullet("docs/dev/readme-contract-extract.md", "G1/G2/G3 審查與 verdict"),
    ("guides/guide-dev-flow.html", "template7-exit-quickstart"): exit_checklist(),
}

for (rel, marker), source in parity.items():
    check(bool(source), f"{marker} canonical source 可抽取")
    target = marker_fragment(rel, marker)
    check(norm(markdown_visible(source)) == norm(visible(target)),
          f"{rel}:{marker} normalized source parity")

# ── Exit Checklist 截斷回歸(2026-08 實測缺陷)──────────────────────────────
# 缺陷長相:模板新增一個**多行**項目 → 舊的單行 regex 只抽到第一項 →
# 主指南靜默掉了其餘 7 項,而 renderer fixed point 與上面的 parity
# 兩邊一起截斷、互相自洽,全綠通過。下面三條讓它不可能再靜默發生。
_exit_items = exit_checklist_items()
_exit_fragment = marker_fragment("guides/guide-dev-flow.html", "template7-exit-quickstart")
check(len(_exit_items) >= 2,
      "7-review Exit Checklist 至少有 2 個頂層項目(抽取沒被截斷)",
      f"實得 {len(_exit_items)}")
# ①每個頂層項目都必須出現在主指南(比對正規化後的可見文字)
_exit_visible = norm(visible(_exit_fragment))
for _item in _exit_items:
    _head = norm(markdown_visible(_item))[:24]
    check(_head in _exit_visible,
          f"Exit Checklist 項目「{_item[:28]}」有進主指南(多行項目不得吞掉後續項目)")
# ②模板頂層項目數 = 生成 HTML 的 <li> 數
_li_count = len(re.findall(r"<li>", _exit_fragment))
check(_li_count == len(_exit_items),
      "主指南 Exit Checklist 的 <li> 數 = 模板頂層 `- [ ]` 項目數",
      f"<li>={_li_count} 模板={len(_exit_items)}")

stub = read("guides/guide-quickstart.html")
check("guide-dev-flow.html#start" in stub, "quickstart stub 轉去主指南 #start")
check(len(stub.splitlines()) < 20, "quickstart 是 stub 不是第二份正文",
      f"{len(stub.splitlines())} 行")
check('id="start"' in read("guides/guide-dev-flow.html"), "主指南有 #start")

guide_text = norm(visible(read("guides/guide-dev-flow.html")))
for stale in (
    "每T五小步",
    "Verify綠→一commit",
    "完成=五答落檔",
    "本資料夾各檔frontmatterstatus:shipped",
    "G1/G2/G3審查verdict",
    "fresh-contextrevieweragent(opus",
    "全S綠(reviewer親跑Verify",
):
    check(norm(stale) not in guide_text, f"active guides 移除舊語意: {stale}")

readme_stage_rows = {}
for line in markdown_table("docs/dev/readme-contract-extract.md", "## 3.", "| # |").splitlines()[2:]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if cells and cells[0].isdigit():
        readme_stage_rows[cells[0]] = cells
# README §3 用途是一句摘要;細節住 guide。不再要求用途欄與 guide 表逐字相同。
# 只釘 # / 檔 / Gate,讓 gate-consistency 抽得到的粗體 token 兩邊仍對得上。
_stage_html = marker_fragment("guides/guide-dev-flow.html", "readme-stage-table")
_guide_stage_rows = {}
for _row in re.findall(r"<tr>(.*?)</tr>", _stage_html, re.S):
    _cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", _row, re.S)
    if _cells:
        _stage = re.match(r"\s*([1-7])\b", visible(_cells[0]))
        if _stage:
            _guide_stage_rows[_stage.group(1)] = _cells
check(set(readme_stage_rows) == set("1234567"),
      "README §3 表有 1–7 列")
check(set(_guide_stage_rows) == set("1234567"),
      "guide readme-stage-table 有 1–7 列")
for _stage in "1234567":
    _rm = readme_stage_rows.get(_stage, ["", "", "", ""])
    _gd = _guide_stage_rows.get(_stage, ["", "", "", ""])
    check(norm(markdown_visible(_rm[1])) == norm(visible(_gd[1])),
          f"README §3 / guide 第 {_stage} 列檔名一致")
    check(norm(markdown_visible(_rm[3])) == norm(visible(_gd[3])),
          f"README §3 / guide 第 {_stage} 列 Gate 一致(用途欄不比)")
walkthrough = re.search(
    r'<h[23] id="walkthrough".*?<table>(.*?)</table>', read("guides/guide-dev-flow.html"), re.S)
walkthrough_rows = {}
if walkthrough:
    for row in re.findall(r"<tr>(.*?)</tr>", walkthrough.group(1), re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        if cells:
            stage = re.match(r"\s*([1-7])\b", visible(cells[0]))
            if stage:
                walkthrough_rows[stage.group(1)] = cells
for stage in ("5", "6", "7"):
    canonical_gate = norm(markdown_visible(readme_stage_rows.get(stage, ["", "", "", ""])[3]))
    guide_gate = norm(visible(walkthrough_rows.get(stage, ["", "", "", "", ""])[4]))
    check(bool(canonical_gate) and canonical_gate in guide_gate,
          f"主指南 Stage {stage} gate 包含 README §3 canonical summary")

tasks = read("example/contract-expiry-reminder/5-tasks.md")
task_blocks = re.split(r"(?=^## T-\d+)", tasks, flags=re.M)[1:]
expected_pairs = set()
for block in task_blocks:
    task_id = re.match(r"## (T-\d+)", block).group(1)
    covers = re.search(r"^- Covers:\s*(.*)$", block, re.M)
    if covers:
        expected_pairs.update((task_id, scenario) for scenario in re.findall(r"S-\d+", covers.group(1)))

# 追溯鏈頂端:expected_pairs 由 5-tasks 自建,S 若整條沒被任何 Covers 承接,期望集合
# 會跟著縮小 → 下方 evidence_pairs 對稱比對仍全綠(恆綠漏洞)。用 4-spec 的 S 全集當
# 獨立上界,封住頂端。本檢查只保護 repo 內範例,實案追溯由 runtime/CI 或人工承接。
spec_scenarios = set(re.findall(
    r"^#### (S-\d+)", read("example/contract-expiry-reminder/4-spec.md"), re.M))
# 抽取本身要能失敗:S 全集若抽成空集合,`set() <= 任何集合` 恆真,下面那條會靜默變成
# no-op 卻照樣報綠 —— 正是 P1 要消滅的恆綠家族。先斷言抽得到東西。
check(bool(spec_scenarios), "4-spec S 清單可抽取(空集合會讓下面的子集合檢查恆真)")
covered_scenarios = {scenario for _task, scenario in expected_pairs}
check(spec_scenarios <= covered_scenarios,
      "4-spec 每個 S 都被至少一個 T 的 Covers 覆蓋",
      f"uncovered={sorted(spec_scenarios - covered_scenarios)}")

notes = read("example/contract-expiry-reminder/6-implementation-notes.md")
evidence_pairs = set(re.findall(r"^### (T-\d+) / (S-\d+)\b", notes, re.M))
check(evidence_pairs == expected_pairs, "每個 T × Covers S 有獨立 TDD evidence",
      f"missing={sorted(expected_pairs - evidence_pairs)} extra={sorted(evidence_pairs - expected_pairs)}")
for task_id, scenario in sorted(evidence_pairs):
    match = re.search(
        rf"^### {task_id} / {scenario}\b(.*?)(?=^### |^## |\Z)", notes, re.M | re.S)
    body = match.group(1) if match else ""
    check("- RED:" in body and "- GREEN:" in body,
          f"{task_id}/{scenario} 有 RED 與 GREEN")

for task_id, scenarios in sorted({task: sorted(s for t, s in expected_pairs if t == task)
                                  for task, _ in expected_pairs}.items()):
    review = re.search(rf"^### {task_id}\n(.*?)(?=^### T-|^## |\Z)", notes, re.M | re.S)
    review_text = review.group(1) if review else ""
    check(all(f"{task_id} / {scenario}" in review_text for scenario in scenarios),
          f"{task_id} review finding 指向每筆 RED→GREEN evidence")

# Reliability triage(輕量欄位存在檢查:模板有三問、範例三問各有結論與非空理由;
# 不做語意判斷,理由「寫得對不對」仍是 G2 reviewer 的責任)
spec_template = read("_templates/4-spec.md")
spec_example = read("example/contract-expiry-reminder/4-spec.md")
check("- Reliability triage:" in spec_template, "template 4-spec 有 Reliability triage 欄")
for field in ("Concurrency", "Idempotency", "Timeout/retry"):
    check(re.search(rf"^\s*- {re.escape(field)}: applicable \| n-a —", spec_template, re.M) is not None,
          f"template Reliability triage 含「{field}」二選一欄")
    filled = re.search(rf"^\s*- {re.escape(field)}: (applicable|n-a) — (\S.*)$", spec_example, re.M)
    check(filled is not None and len(filled.group(2).strip()) >= 20,
          f"example Reliability triage「{field}」有結論與非空理由",
          "缺欄或格式不符" if filled is None else f"理由過短:{filled.group(2)[:30]}")

review_md = read("example/contract-expiry-reminder/7-review.md")
check("reviewer 以擁有合約 C 的 `<owner>` 登入" in review_md,
      "S-1 現象證據 actor 是 <owner>")
check("## 變更架構圖" in review_md, "7-review Markdown 含變更架構圖")
check(len(re.findall(r"^<details>", review_md, re.M)) >= 6,
      "7-review Markdown 含逐檔 diff folds")
check(len(re.findall(r"^<details>", notes, re.M)) >= 6,
      "6-notes Markdown 含逐檔 diff folds")

for rel, min_tables, min_details in (
    ("example/contract-expiry-reminder/6-implementation-notes.html", 0, 6),
    ("example/contract-expiry-reminder/7-review.html", 2, 6),
):
    rendered = read(rel)
    check(len(re.findall(r"<table(?:\s|>)", rendered)) >= min_tables,
          f"{rel} real table count >= {min_tables}")
    check(len(re.findall(r"<details(?:\s|>)", rendered)) >= min_details,
          f"{rel} real details count >= {min_details}")
    check('class="add"' in rendered and 'class="del"' in rendered,
          f"{rel} diff additions/deletions are colored")
check("變更架構圖" in read("example/contract-expiry-reminder/7-review.html"),
      "7-review HTML 含變更架構內容")

serena_tracked = subprocess.run(["git", "ls-files", ".serena"], cwd=root,
                                capture_output=True, text=True).stdout.strip()
check(serena_tracked == "", ".serena/ 本機快取不得進版本庫", serena_tracked)
check(".serena/" in read(".gitignore"), ".gitignore 含 .serena/ 防再犯條目")

renderer = os.path.join(root, "scripts", "render-methodology-corrections.sh")
check(os.path.isfile(renderer) and os.access(renderer, os.X_OK),
      "tracked batch renderer exists and is executable")
if os.path.isfile(renderer) and os.access(renderer, os.X_OK):
    # 顯式帶 bash(派工單 §2.2):Windows 沒有 shebang 機制,直接 exec 一支 .sh
    # 會噴 OSError WinError 193「不是有效的 Win32 應用程式」而整支檢查崩掉。
    result = subprocess.run(["bash", renderer, "--check"], cwd=root,
                            capture_output=True, text=True)
    check(result.returncode == 0, "renderer byte-identical fixed point",
          (result.stdout + result.stderr).strip())

if failures:
    print(f"❌ methodology correction checks: {checks - len(failures)}/{checks} passed")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print(f"✅ methodology correction checks: {checks}/{checks} passed")
PY
