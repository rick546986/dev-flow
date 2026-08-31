#!/bin/bash
# check-dir-tree.sh — 可摺疊目錄包含樹產器的小牙
#
# 咬什麼:產器壞了、吐 mermaid／<pre>／svg、掃 repo 猜 why、
# 或母版 guides/guide-dir-map.html 跟產器產出漂了。
# 契約在 notes/design/dir-tree-contract.md(短冊,對齊 vbox-fig-contract)。
#
# 用法:
#   scripts/check-dir-tree.sh [root]
# exit:0 = 全過 / 1 = 腳本壞或吐了禁物 / 2 = 環境或用法失敗

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import subprocess
import sys

root = sys.argv[1]
builder = os.path.join(root, "scripts", "build-dir-tree.py")
contract = os.path.join(root, "notes", "design", "dir-tree-contract.md")
purpose = os.path.join(root, "guides", "dir-tree-purpose.yaml")
guide = os.path.join(root, "guides", "guide-dir-map.html")
template = os.path.join(root, "_templates", "1-discussion.md")

failures = []
checks = 0


def check(ok, label):
    global checks
    checks += 1
    if ok:
        print("[ok] " + label)
        return
    print("[FAIL] " + label)
    failures.append(label)


def run_builder(args):
    return subprocess.run(
        [sys.executable, builder] + args,
        cwd=root, capture_output=True, text=True,
    )


def judge(html, label):
    issues = []
    low = html.lower()
    if "```mermaid" in low or "mermaid.js" in low or 'class="mermaid"' in low:
        issues.append("吐 mermaid")
    if "<pre" in low:
        issues.append("吐 <pre>")
    if "<svg" in low:
        issues.append("吐 svg")
    if "<details open" in low:
        issues.append("預設展開")
    if 'class="tline"' not in html and "class='tline'" not in html:
        issues.append("沒有 .tline")
    if "├─" not in html or "└─" not in html:
        issues.append("沒有樹線")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


for path, label in (
    (builder, "scripts/build-dir-tree.py"),
    (contract, "notes/design/dir-tree-contract.md"),
    (purpose, "guides/dir-tree-purpose.yaml"),
    (guide, "guides/guide-dir-map.html"),
):
    if not os.path.isfile(path):
        print("FATAL:找不到 " + label, file=sys.stderr)
        sys.exit(2)

empty = run_builder([])
check(empty.returncode == 2, "無參數 exit 2")
check("用法" in (empty.stdout + empty.stderr), "無參數印用法")

help_run = run_builder(["--help"])
check(help_run.returncode == 2, "--help exit 2")

walk = run_builder(["--walk"])
check(walk.returncode == 2, "--walk 必須紅(不准掃 repo 猜 why)")

checked = run_builder(["--check"])
check(checked.returncode == 0, "--check 母版頁對得上產器")

good = run_builder(["--fixture", "good"])
check(good.returncode == 0, "good fixture exit 0")
ok, detail = judge(good.stdout, "fixture 形狀")
check(ok, detail)
check("app.py" in good.stdout and "其餘見盤點" in good.stdout, "fixture 含產品檔與 ellipsis")
check("devflow-check.sh" not in good.stdout, "產品樹不灌母版脚本")
leaf = [ln for ln in good.stdout.splitlines() if 'class="name">app.py</span>' in ln]
check(leaf and leaf[0].strip().startswith("<div class=\"tline\">"), "葉子不是 summary")
folder = [ln for ln in good.stdout.splitlines() if 'class="name">src/</span>' in ln]
check(folder and "<summary" in folder[0], "有子列的夾才是 summary")

frag = run_builder(["--fixture", "good", "--fragment"])
check(frag.returncode == 0 and "<!DOCTYPE" not in frag.stdout, "--fragment 只吐樹")
ok, detail = judge(frag.stdout, "fragment 形狀")
check(ok, detail)

missing = run_builder([
    "--purpose", os.path.join(root, "scripts", "fixtures", "dir-tree", "missing-why", "purpose.yaml"),
    "--root", os.path.join(root, "scripts", "fixtures", "dir-tree", "good", "repo"),
])
check(missing.returncode == 1, "短 why 必須紅")

bad_cases = [
    ("mermaid", "```mermaid\ngraph TD\nA-->B\n```"),
    ("pre", "<pre>├─ src/</pre>"),
    ("svg", '<svg viewBox="0 0 280 80"></svg>'),
    ("open", '<div class="tline">├─ <details open>'),
]
for name, payload in bad_cases:
    ok, _detail = judge(payload, name)
    check(not ok, "牙咬 %s" % name)

text = open(guide, encoding="utf-8").read()
ok, detail = judge(text, "母版頁形狀")
check(ok, detail)
check("dir-tree-purpose.yaml" in text, "母版樹列了 YAML 用途表")
check('id="skills"' in text, "母版仍有 skills 摺疊")
check("summary .name" in open(builder, encoding="utf-8").read()
      or "summary .name{color:var(--acc)}" in text, "可點夾名用 accent")

tmpl = open(template, encoding="utf-8").read()
check("build-dir-tree.py" in tmpl and "dir-tree.html" in tmpl, "第 1 站模板有可選目錄樹")
check("不進 gate" in tmpl or "不是每案必跑" in tmpl, "模板寫明不是必跑")

canon = open(contract, encoding="utf-8").read()
check(len(canon.splitlines()) <= 80, "契約是短冊(≤80 行)")
check("```yaml" in canon and "ellipsis:" in canon, "契約鎖 YAML + ellipsis")
check("不要掃整棵 repo" in canon or "不要掃整棵 repo 自動猜 why" in canon, "契約禁掃 repo 猜 why")
check("scan-now" in canon and "vbox-fig" in canon and "#filemap" in canon
      and "fig-lifecycle" in canon, "契約點名何時不用")
check("2.0.0" in canon, "契約寫明不改 2.0.0")

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:dir-tree 產器 + 牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
