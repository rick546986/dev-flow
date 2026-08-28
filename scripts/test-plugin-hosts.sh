#!/bin/bash
# test-plugin-hosts.sh — check-plugin-hosts.sh 的負向牙
#
# 對照組 = 本 repo 的三邊 manifest + 整棵 skills/ + PLUGIN.md + guide #host + README。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 拿掉 Cursor／Codex manifest、或改成只掛 SKILL.md,必須紅。
# 禁 check(True):本檔用 expect() 比 returncode,不用恆真斷言。
#
# 用法:scripts/test-plugin-hosts.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-plugin-hosts.sh"
[ -x "$CHECK" ] || chmod +x "$CHECK"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }

python3 - "$ROOT" "$CHECK" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile

root, check = sys.argv[1], sys.argv[2]
passed = 0
failed = 0
MIN_CASES = 14

COPY_DIRS = (
    ".claude-plugin",
    ".cursor-plugin",
    ".codex-plugin",
    "skills",
    "docs",
    "guides",
)
COPY_FILES = ("README.md",)


def run_check(tree):
    return subprocess.run(
        ["bash", check, tree], capture_output=True, text=True
    )


def seed(tmp):
    for rel in COPY_DIRS:
        src = os.path.join(root, rel)
        if not os.path.isdir(src):
            print(f"FATAL: 對照組缺 {rel}/", file=sys.stderr)
            sys.exit(2)
        shutil.copytree(src, os.path.join(tmp, rel), symlinks=False)
    for rel in COPY_FILES:
        src = os.path.join(root, rel)
        if not os.path.isfile(src):
            print(f"FATAL: 對照組缺 {rel}", file=sys.stderr)
            sys.exit(2)
        shutil.copy2(src, os.path.join(tmp, rel))


def expect(label, tree, want_rc, needle=None):
    global passed, failed
    proc = run_check(tree)
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == want_rc
    if ok and needle and needle not in blob:
        ok = False
        blob += f"\n[test] 期望輸出含 {needle!r}"
    if ok:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        print(f"  ✗ {label} (rc={proc.returncode} want={want_rc})", file=sys.stderr)
        print(blob[-1500:], file=sys.stderr)


def patch(path, old, new):
    text = open(path, encoding="utf-8").read()
    if old not in text:
        print(f"FATAL: 治具找不到待改字串 {old!r} in {path}", file=sys.stderr)
        sys.exit(2)
    open(path, "w", encoding="utf-8").write(text.replace(old, new, 1))


def load_json(path):
    return json.loads(open(path, encoding="utf-8").read())


def dump_json(path, data):
    open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    )


with tempfile.TemporaryDirectory(prefix="plugin-hosts-") as tmp:
    good = os.path.join(tmp, "good")
    os.makedirs(good)
    seed(good)
    expect("G-good 三邊 manifest + 整棵 skills 必須綠", good, 0, "PASS: plugin-hosts")

    d = os.path.join(tmp, "no-cursor")
    shutil.copytree(good, d)
    os.remove(os.path.join(d, ".cursor-plugin", "plugin.json"))
    expect(
        "R-no-cursor 拿掉 .cursor-plugin/plugin.json 必須紅",
        d,
        1,
        ".cursor-plugin/plugin.json",
    )

    d = os.path.join(tmp, "no-codex")
    shutil.copytree(good, d)
    os.remove(os.path.join(d, ".codex-plugin", "plugin.json"))
    expect(
        "R-no-codex 拿掉 .codex-plugin/plugin.json 必須紅",
        d,
        1,
        ".codex-plugin/plugin.json",
    )

    d = os.path.join(tmp, "no-cursor-market")
    shutil.copytree(good, d)
    os.remove(os.path.join(d, ".cursor-plugin", "marketplace.json"))
    expect(
        "R-no-cursor-market 拿掉 .cursor-plugin/marketplace.json 必須紅",
        d,
        1,
        ".cursor-plugin/marketplace.json",
    )

    d = os.path.join(tmp, "cursor-skill-md")
    shutil.copytree(good, d)
    path = os.path.join(d, ".cursor-plugin", "plugin.json")
    data = load_json(path)
    data["skills"] = "./skills/dev-flow/SKILL.md"
    dump_json(path, data)
    expect(
        "R-cursor-skill-md Cursor skills 改成只掛 SKILL.md 必須紅",
        d,
        1,
        "只掛 SKILL.md",
    )

    d = os.path.join(tmp, "codex-skill-md")
    shutil.copytree(good, d)
    path = os.path.join(d, ".codex-plugin", "plugin.json")
    data = load_json(path)
    data["skills"] = "./skills/dev-talk/SKILL.md"
    dump_json(path, data)
    expect(
        "R-codex-skill-md Codex skills 改成只掛 SKILL.md 必須紅",
        d,
        1,
        "只掛 SKILL.md",
    )

    d = os.path.join(tmp, "thin-talk")
    shutil.copytree(good, d)
    talk = os.path.join(d, "skills", "dev-talk")
    graph = os.path.join(talk, "graph.yaml")
    nodes = os.path.join(talk, "nodes")
    if os.path.isfile(graph):
        os.remove(graph)
    if os.path.isdir(nodes):
        shutil.rmtree(nodes)
    expect(
        "R-thin-talk skills/dev-talk 只留 SKILL.md 必須紅",
        d,
        1,
        "只有 SKILL.md",
    )

    d = os.path.join(tmp, "claude-cmd")
    shutil.copytree(good, d)
    patch(
        os.path.join(d, "docs", "PLUGIN.md"),
        "/plugin marketplace add rick546986/dev-flow",
        "/plugin marketplace add someone/else",
    )
    expect(
        "R-claude-cmd 改掉 Claude 舊加市集指令必須紅",
        d,
        1,
        "Claude 加市集",
    )

    d = os.path.join(tmp, "claude-install")
    shutil.copytree(good, d)
    patch(
        os.path.join(d, "docs", "PLUGIN.md"),
        "/plugin install dev-flow@dev-flow",
        "/plugin install something-else",
    )
    expect(
        "R-claude-install 改掉 Claude 舊安裝指令必須紅",
        d,
        1,
        "Claude 安裝",
    )

    d = os.path.join(tmp, "codex-cmd")
    shutil.copytree(good, d)
    patch(
        os.path.join(d, "docs", "PLUGIN.md"),
        "codex plugin marketplace add rick546986/dev-flow",
        "codex plugin marketplace add someone/else",
    )
    expect(
        "R-codex-cmd 改掉 Codex 實測加市集指令必須紅",
        d,
        1,
        "Codex 加市集",
    )

    d = os.path.join(tmp, "version-drift")
    shutil.copytree(good, d)
    path = os.path.join(d, ".cursor-plugin", "plugin.json")
    data = load_json(path)
    data["version"] = "0.0.1"
    dump_json(path, data)
    expect(
        "R-version 三邊 version 漂了必須紅",
        d,
        1,
        "version 必須互釘",
    )

    d = os.path.join(tmp, "not-thin")
    shutil.copytree(good, d)
    shutil.copytree(
        os.path.join(d, "skills", "dev-setup"),
        os.path.join(d, ".cursor-plugin", "skills", "dev-setup"),
    )
    expect(
        "R-not-thin .cursor-plugin/ 抄了 skills 必須紅",
        d,
        1,
        "不是薄殼",
    )

    d = os.path.join(tmp, "grok-lock")
    shutil.copytree(good, d)
    patch(
        os.path.join(d, "docs", "PLUGIN.md"),
        "不要假裝能從產品 repo 自動灌進 Grok",
        "本機技能庫仍可掛整棵",
    )
    expect(
        "R-grok-lock 拿掉 Grok 牙必須紅",
        d,
        1,
        "Grok 牙",
    )

    d = os.path.join(tmp, "grok-claim")
    shutil.copytree(good, d)
    plugin_md = os.path.join(d, "docs", "PLUGIN.md")
    open(plugin_md, "a", encoding="utf-8").write(
        "\n能從產品 repo 自動灌進 Grok。\n"
    )
    expect(
        "R-grok-claim 寫能從產品 repo 自動灌進 Grok 必須紅",
        d,
        1,
        "自動灌進 Grok",
    )

    d = os.path.join(tmp, "readme-manual")
    shutil.copytree(good, d)
    readme = os.path.join(d, "README.md")
    text = open(readme, encoding="utf-8").read()
    pre, sep, post = text.partition("<details>")
    if not sep:
        print("FATAL: README 沒有 details", file=sys.stderr)
        sys.exit(2)
    open(readme, "w", encoding="utf-8").write(
        pre + "/plugin marketplace add rick546986/dev-flow\n" + sep + post
    )
    expect(
        "R-readme-manual README 第一屏灌進安裝指令必須紅",
        d,
        1,
        "第一屏灌進安裝手冊",
    )

total = passed + failed
print(f"=== test-plugin-hosts:{passed}/{total} ===")
if total < MIN_CASES:
    print(f"⛔ 案例數 {total} < {MIN_CASES},牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
if failed:
    sys.exit(1)
sys.exit(0)
PY
