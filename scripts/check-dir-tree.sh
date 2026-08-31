#!/bin/bash
# check-dir-tree.sh — 可摺疊目錄樹產器的小牙
#
# 咬什麼:scripts/build-dir-tree.py 本身壞了、吐 mermaid／<pre>／svg、
# 或母版 guides/guide-dir-map.html 跟產器產出漂了。
# 契約在 notes/design/dir-tree-contract.md。
#
# 不塞 hop graph、不改 vbox-fig／scan-now／七站三走廊圖、
# 不進 ship-manifest。
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
purpose = os.path.join(root, "guides", "dir-tree-purpose.json")
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


if not os.path.isfile(builder):
    print("FATAL:找不到 " + builder, file=sys.stderr)
    sys.exit(2)
if not os.path.isfile(contract):
    print("FATAL:找不到契約 notes/design/dir-tree-contract.md", file=sys.stderr)
    sys.exit(2)
if not os.path.isfile(purpose):
    print("FATAL:找不到用途表 guides/dir-tree-purpose.json", file=sys.stderr)
    sys.exit(2)
if not os.path.isfile(guide):
    print("FATAL:找不到 guides/guide-dir-map.html", file=sys.stderr)
    sys.exit(2)

empty = run_builder([])
check(empty.returncode == 2, "無參數 exit 2")
check("用法" in (empty.stdout + empty.stderr), "無參數印用法")

help_run = run_builder(["--help"])
check(help_run.returncode == 2, "--help exit 2")
check("用法" in (help_run.stdout + help_run.stderr), "--help 印用法")

checked = run_builder(["--check"])
check(checked.returncode == 0, "--check 母版頁對得上產器")

good = run_builder(["--fixture", "good"])
check(good.returncode == 0, "good fixture exit 0")
ok, detail = judge(good.stdout, "fixture 形狀")
check(ok, detail)
check("app.py" in good.stdout and "readme.md" in good.stdout, "fixture 含產品檔")
check("devflow-check.sh" not in good.stdout, "產品樹不灌母版脚本")
check("<details open" not in good.stdout, "fixture 預設摺疊")
guide_text = open(guide, encoding="utf-8").read()
check("全盲下游" in guide_text and "何時用" in guide_text, "母版 why 有脈絡句")

missing = run_builder([
    "--purpose", os.path.join(root, "scripts", "fixtures", "dir-tree", "missing-why", "purpose.json"),
    "--root", os.path.join(root, "scripts", "fixtures", "dir-tree", "good", "repo"),
])
check(missing.returncode == 1, "短 why 必須紅")

# 牙自己咬壞輸出
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
check("dir-tree-contract.md" in text, "母版樹列了畫法契約")
check('id="skills"' in text, "母版仍有 skills 摺疊")

tmpl = open(template, encoding="utf-8").read()
check("build-dir-tree.py" in tmpl, "第 1 站模板有可選目錄樹")
check("dir-tree.html" in tmpl, "模板指定落 docs/dev/<slug>/dir-tree.html")
check("不進 gate" in tmpl or "不是每案必跑" in tmpl, "模板寫明不是必跑")

canon = open(contract, encoding="utf-8").read()
check("├─" in canon and "預設" in canon and "L1" in canon, "契約鎖 L1 摺疊")
check("mermaid" in canon.lower() and "vbox" in canon.lower(), "契約點名禁 mermaid／vbox")
check("ship-manifest" in canon, "契約寫明不進散發清單")

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:dir-tree 產器 + 牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
