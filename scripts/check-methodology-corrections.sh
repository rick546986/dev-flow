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
    source = read("README.md")
    matches = re.findall(r"```text\n(RED → GREEN.*?review evidence)\n```", source, re.S)
    return ("```text\n" + matches[0] + "\n```\n") if len(matches) == 1 else ""


def exit_checklist():
    source = read("_templates/7-review.md")
    match = re.search(r"^## Exit Checklist[^\n]*\n((?:- \[ \].*\n)+)", source, re.M)
    return match.group(1) if match else ""


parity = {
    ("guide-dev-flow.html", "readme-stage-table"):
        markdown_table("README.md", "## 3.", "| # |"),
    ("guide-dev-flow.html", "template2-checklist"):
        quote_region("_templates/2-decision.md", "執行清單("),
    ("guide-dev-flow.html", "template3-checklist"):
        quote_region("_templates/3-prototype.md", "執行清單("),
    ("guide-dev-flow.html", "template4-laws"):
        quote_region("_templates/4-spec.md", "反模糊三律(", "執行清單("),
    ("guide-dev-flow.html", "template4-checklist"):
        quote_region("_templates/4-spec.md", "執行清單(", "起草前估"),
    ("guide-dev-flow.html", "template6-checklist"):
        quote_region("_templates/6-implementation-notes.md", "執行清單(", "實作期規則("),
    ("guide-dev-flow.html", "template6-rules"):
        quote_region("_templates/6-implementation-notes.md", "實作期規則("),
    ("guide-dev-flow.html", "template7-checklist"):
        quote_region("_templates/7-review.md", "執行清單("),
    ("guide-dev-flow.html", "readme-reviewer-selection-flow"):
        bullet("README.md", "審查者產生"),
    ("guide-quickstart.html", "readme-stage6-seam-quickstart"): fenced_seam(),
    ("guide-quickstart.html", "readme-reviewer-selection-quickstart"):
        bullet("README.md", "審查者產生"),
    ("guide-quickstart.html", "readme-gate-model-quickstart"):
        bullet("README.md", "G1/G2/G3 審查與 verdict"),
    ("guide-quickstart.html", "template7-exit-quickstart"): exit_checklist(),
}

for (rel, marker), source in parity.items():
    check(bool(source), f"{marker} canonical source 可抽取")
    target = marker_fragment(rel, marker)
    check(norm(markdown_visible(source)) == norm(visible(target)),
          f"{rel}:{marker} normalized source parity")

guide_text = norm(visible(read("guide-dev-flow.html") + read("guide-quickstart.html")))
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
for line in markdown_table("README.md", "## 3.", "| # |").splitlines()[2:]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if cells and cells[0].isdigit():
        readme_stage_rows[cells[0]] = cells
walkthrough = re.search(
    r'<h2 id="walkthrough".*?<table>(.*?)</table>', read("guide-quickstart.html"), re.S)
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
          f"quickstart Stage {stage} gate 包含 README §3 canonical summary")

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
    result = subprocess.run([renderer, "--check"], cwd=root, capture_output=True, text=True)
    check(result.returncode == 0, "renderer byte-identical fixed point",
          (result.stdout + result.stderr).strip())

if failures:
    print(f"❌ methodology correction checks: {checks - len(failures)}/{checks} passed")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print(f"✅ methodology correction checks: {checks}/{checks} passed")
PY
