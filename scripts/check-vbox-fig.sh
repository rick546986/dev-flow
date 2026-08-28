#!/bin/bash
# check-vbox-fig.sh — 直式置中方塊圖產圖器的小牙
#
# 咬什麼:scripts/build-vbox-fig.py 本身壞了,或吐 mermaid／<pre>／沒有 viewBox／
# 沒置中字。契約在 notes/design/vbox-fig-contract.md。
#
# 不塞 hop graph、不改鬆 --action、不取代 check-devtalk-fig-graph.sh／
# check-devtalk-fig-journey.sh／check-devstage-fig-text.sh／
# check-guides-fig-sync.sh,也不改 build-scan-html.py／build-gate-twin.py。
#
# 用法:
#   scripts/check-vbox-fig.sh [root]
# exit:0 = 全過 / 1 = 腳本壞或吐了禁物 / 2 = 環境或用法失敗

set -uo pipefail

SELF=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import re
import subprocess
import sys

root = sys.argv[1]
builder = os.path.join(root, "scripts", "build-vbox-fig.py")
fixture = os.path.join(root, "scripts", "fixtures", "vbox-fig", "lifecycle.json")
contract = os.path.join(root, "notes", "design", "vbox-fig-contract.md")

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


def judge(svg, label):
    """同一把尺:壞輸出必須紅。"""
    issues = []
    low = svg.lower()
    if "mermaid" in low:
        issues.append("吐 mermaid")
    if "<pre" in low:
        issues.append("吐 <pre>")
    if not re.search(r"<svg\b", svg):
        issues.append("不是 svg")
    if not re.search(r"""viewBox\s*=\s*["']0 0 280\b""", svg):
        issues.append("沒有 280 畫布 viewBox")
    if "max-width:360px" not in svg and "max-width: 360px" not in svg:
        issues.append("沒有 max-width:360px")
    if not re.search(r"""text-anchor\s*=\s*["']middle["']""", svg):
        issues.append("沒置中字")
    if not re.search(r"""class\s*=\s*["']nl["']""", svg):
        issues.append("缺 .nl")
    if not re.search(r"""class\s*=\s*["']sm["']""", svg):
        issues.append("缺 .sm")
    if issues:
        return False, label + ":" + "、".join(issues)
    return True, label


if not os.path.isfile(builder):
    print("FATAL:找不到 " + builder, file=sys.stderr)
    sys.exit(2)
if not os.path.isfile(fixture):
    print("FATAL:找不到 lifecycle fixture", file=sys.stderr)
    sys.exit(2)
if not os.path.isfile(contract):
    print("FATAL:找不到契約 notes/design/vbox-fig-contract.md", file=sys.stderr)
    sys.exit(2)

empty = run_builder([])
check(empty.returncode == 2, "無參數 exit 2")
check("用法" in (empty.stdout + empty.stderr), "無參數印用法")

help_run = run_builder(["--help"])
check(help_run.returncode == 2, "--help exit 2")
check("用法" in (help_run.stdout + help_run.stderr), "--help 印用法")

good = run_builder(["--fixture", "lifecycle"])
check(good.returncode == 0, "lifecycle fixture exit 0")
svg = good.stdout
ok, detail = judge(svg, "fixture 形狀")
check(ok, detail)
check('class="hl"' in svg or "class='hl'" in svg, "fixture 含 .hl")
check("新生" in svg and "改行為" in svg and "退役" in svg and "不動" in svg,
      "fixture 四格:新生／改行為／退役／不動")
check(re.search(r"""width\s*=\s*["']200["']""", svg) is not None, "框寬 200")
check(re.search(r"""x\s*=\s*["']40["']""", svg) is not None, "框 x=40 置中在 280")
check("<line " in svg, "框間直線")
check("```" not in svg, "fixture 不是 fence／ASCII 充圖")

# 牙自己咬壞輸出:同一把 judge,四種禁物必須判紅,否則這支是空殼。
bad_cases = [
    ("mermaid", "```mermaid\ngraph TD\nA-->B\n```"),
    ("pre", '<pre>新生 → 改行為</pre>'),
    ("no-viewBox", '<svg><rect class="hl"/><text class="nl">x</text></svg>'),
    ("no-center",
     '<svg viewBox="0 0 280 80" style="max-width:360px">'
     '<text class="nl" x="10" y="20">改行為</text>'
     '<text class="sm" x="10" y="34">沒置中</text></svg>'),
]
for name, payload in bad_cases:
    ok, _detail = judge(payload, name)
    check(not ok, "牙咬 %s" % name)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
print("✅ PASS:vbox-fig 產圖器 + 牙 %d/%d" % (checks, checks))
sys.exit(0)
PY
