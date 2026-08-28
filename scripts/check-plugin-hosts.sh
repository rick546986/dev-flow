#!/bin/bash
# check-plugin-hosts.sh — 三邊 plugin 薄殼 + 整棵 skills + 安裝指令牙
#
# 為什麼需要:Owner 要 Claude／Cursor／Codex 各自用官方 plugin install 裝同一份
# 方法包。正本仍是 repo 根的 skills／hooks／_templates,三邊 manifest 只准薄殼。
# Claude 的 `.claude-plugin/` 與 `/plugin marketplace add` 語意不准改。
# Cursor／Codex 拿掉 manifest、或改成只掛 SKILL.md,開工會沒有 graph／nodes。
# Grok 沒有獨立 marketplace,文件不准寫「能從產品 repo 自動灌進 Grok」。
#
# 驗什麼:
#   ①三邊 manifest 在,且 JSON 可解析
#   ②Cursor／Codex 的 skills 欄是目錄 `./skills/`,不是 SKILL.md
#   ③skills/ 本身是真目錄(不是 symlink),每棵技能是整棵
#   ④三邊 version 與 Claude plugin.json 互釘
#   ⑤Cursor marketplace source 指本 repo 根;Claude marketplace source 仍是 ./
#   ⑥薄殼:`.cursor-plugin/`／`.codex-plugin/` 不准抄 skills／hooks／_templates
#   ⑦docs/PLUGIN.md 仍有 Claude 舊指令;Codex 寫的是實測動詞(add／upgrade)
#   ⑧guide #host 四邊都寫了怎麼裝／怎麼更新
#   ⑨Grok 牙:必須有「不要假裝能從產品 repo 自動灌進 Grok」;正面宣稱自動灌就紅
#   ⑩README 第一屏不准變安裝手冊;details 要有 PLUGIN.md 入口
#
# 用法:scripts/check-plugin-hosts.sh [root]
# exit:0 = 全過 / 1 = 真違規 / 2 = 檢查自身故障
#
# 不改 1–7 產器、scan、twin、Pages、#60 verdict。
# 本檔不用 check() 當斷言入口,避免 check(True) 這種恆真斷言。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" "$SELF_DIR/check-plugin-hosts.sh" <<'PY'
import json
import os
import re
import sys

root = sys.argv[1]
self_path = sys.argv[2]
fails = []

SKILL_ONLY_OK = {"dev-setup", "dev-run", "dev-release", "dev-report"}
FLOW_STAGES = ("stage2", "stage3", "stage4", "stage5", "stage6", "stage7")
GRAPH_SKILLS = {"dev-talk"}
CLAUDE_ADD = "/plugin marketplace add rick546986/dev-flow"
CLAUDE_INSTALL = "/plugin install dev-flow@dev-flow"
CODEX_MKT_ADD = "codex plugin marketplace add rick546986/dev-flow"
CODEX_ADD = "codex plugin add dev-flow@dev-flow"
CODEX_UPGRADE = "codex plugin marketplace upgrade"
GROK_LOCK = "不要假裝能從產品 repo 自動灌進 Grok"
SKILLS_OK = {"./skills", "./skills/"}
SOURCE_OK = {"./", "."}


def fail(msg):
    fails.append(msg)


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        fail(f"找不到 {rel}")
        return None
    return open(path, encoding="utf-8").read()


def load_json(rel):
    text = read(rel)
    if text is None:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"{rel} 不是合法 JSON:{exc}")
        return None
    if not isinstance(data, dict):
        fail(f"{rel} 根必須是物件")
        return None
    return data


def skills_field_ok(value, label):
    if isinstance(value, list):
        if len(value) != 1:
            fail(f"{label} skills 必須是單一目錄路徑,不能是清單亂掛")
            return False
        value = value[0]
    if not isinstance(value, str):
        fail(f"{label} skills 必須是字串路徑")
        return False
    if value.endswith(".md") or "SKILL.md" in value.replace("\\", "/"):
        fail(f"{label} skills 只掛 SKILL.md（必須是整棵 ./skills/）")
        return False
    norm = value.replace("\\", "/")
    if norm not in SKILLS_OK:
        fail(f"{label} skills 必須是 ./skills/（實得 {value!r}）")
        return False
    return True


def source_is_repo_root(value, label):
    if isinstance(value, dict):
        value = value.get("path") or value.get("source")
    if not isinstance(value, str) or value not in SOURCE_OK:
        fail(f"{label} source 必須指本 repo 根（./ 或 .）,實得 {value!r}")
        return False
    return True


def skill_tree_ok(skills_root, name):
    path = os.path.join(skills_root, name)
    if os.path.islink(path):
        return f"{name} 是 symlink（Codex 安裝會跳過 symlink,必須是真目錄）"
    if not os.path.isdir(path):
        return f"{name} 不是目錄"
    if not os.path.isfile(os.path.join(path, "SKILL.md")):
        return f"{name} 沒有 SKILL.md"
    if name in SKILL_ONLY_OK:
        return ""
    if name == "dev-flow":
        missing = []
        for stage in FLOW_STAGES:
            stage_dir = os.path.join(path, stage)
            if not (
                os.path.isdir(stage_dir)
                and os.path.isfile(os.path.join(stage_dir, "graph.yaml"))
                and os.path.isdir(os.path.join(stage_dir, "nodes"))
            ):
                missing.append(stage)
        if missing:
            return f"dev-flow 不是整棵（缺 {','.join(missing)} 的 graph.yaml／nodes）"
        return ""
    if name in GRAPH_SKILLS or os.path.isdir(os.path.join(path, "nodes")):
        if not (
            os.path.isfile(os.path.join(path, "graph.yaml"))
            and os.path.isdir(os.path.join(path, "nodes"))
        ):
            return f"{name} 只有 SKILL.md、沒有 graph.yaml／nodes"
    return ""


def thin_shell(rel, allowed):
    path = os.path.join(root, rel)
    if not os.path.isdir(path):
        fail(f"找不到薄殼目錄 {rel}/")
        return
    try:
        names = set(os.listdir(path))
    except OSError as exc:
        fail(f"讀不到 {rel}/:{exc}")
        return
    extra = sorted(names - allowed)
    if extra:
        fail(f"{rel}/ 不是薄殼,多了 {extra}")
    for banned in ("skills", "hooks", "_templates"):
        if banned in names:
            fail(f"{rel}/ 抄了正本 {banned}/（正本只准一份,在 repo 根）")


def host_section(html):
    m = re.search(r'<h2 id="host">.*?(?=<h2 |\Z)', html, re.S)
    return m.group(0) if m else ""


def grok_claim_ok(text, label):
    if GROK_LOCK not in text:
        fail(f"{label} 少了 Grok 牙「{GROK_LOCK}」")
        return
    for i, line in enumerate(text.splitlines(), 1):
        if "自動灌進 Grok" not in line:
            continue
        if any(n in line for n in ("不要", "不准", "不假裝", "不要假裝")):
            continue
        fail(f"{label}:{i} 寫了能從產品 repo 自動灌進 Grok")


# ── 自身不得出現恆真斷言 ──────────────────────────────────────────────
own = open(self_path, encoding="utf-8").read()
if re.search(r"^\s*check\(\s*(?:True|1\s*==\s*1|not\s+False)\b", own, re.M):
    print("FATAL: 本守衛出現 check(True)／恆真斷言", file=sys.stderr)
    sys.exit(2)

# ── ①三邊 manifest ────────────────────────────────────────────────────
claude_plugin = load_json(".claude-plugin/plugin.json")
claude_market = load_json(".claude-plugin/marketplace.json")
cursor_plugin = load_json(".cursor-plugin/plugin.json")
cursor_market = load_json(".cursor-plugin/marketplace.json")
codex_plugin = load_json(".codex-plugin/plugin.json")

if claude_plugin and claude_plugin.get("name") != "dev-flow":
    fail(".claude-plugin/plugin.json name 必須是 dev-flow")
if cursor_plugin and cursor_plugin.get("name") != "dev-flow":
    fail(".cursor-plugin/plugin.json name 必須是 dev-flow")
if codex_plugin and codex_plugin.get("name") != "dev-flow":
    fail(".codex-plugin/plugin.json name 必須是 dev-flow")

# ── ② skills 欄是整棵目錄 ─────────────────────────────────────────────
if cursor_plugin is not None:
    skills_field_ok(cursor_plugin.get("skills"), ".cursor-plugin/plugin.json")
if codex_plugin is not None:
    skills_field_ok(codex_plugin.get("skills"), ".codex-plugin/plugin.json")

# ── ③ skills/ 真目錄 + 整棵 ───────────────────────────────────────────
skills_root = os.path.join(root, "skills")
if os.path.islink(skills_root):
    fail("skills/ 是 symlink（Codex 安裝會跳過,必須拷整棵真目錄）")
elif not os.path.isdir(skills_root):
    fail("找不到 skills/ 真目錄")
else:
    try:
        names = sorted(
            n for n in os.listdir(skills_root)
            if os.path.isdir(os.path.join(skills_root, n))
        )
    except OSError as exc:
        names = []
        fail(f"讀不到 skills/:{exc}")
    if "dev-flow" not in names or "dev-talk" not in names:
        fail("skills/ 少了 dev-flow 或 dev-talk")
    for name in names:
        err = skill_tree_ok(skills_root, name)
        if err:
            fail(err)
        else:
            print(f"skill-tree: {name}")

# ── ④ version 互釘 ────────────────────────────────────────────────────
versions = {}
for label, data in (
    (".claude-plugin/plugin.json", claude_plugin),
    (".cursor-plugin/plugin.json", cursor_plugin),
    (".codex-plugin/plugin.json", codex_plugin),
):
    if data is None:
        continue
    ver = data.get("version")
    if not isinstance(ver, str) or not re.fullmatch(r"\d+\.\d+\.\d+", ver):
        fail(f"{label} version 必須是 semver,實得 {ver!r}")
    else:
        versions[label] = ver
uniq = set(versions.values())
if len(versions) == 3 and len(uniq) != 1:
    fail("三邊 plugin.json version 必須互釘,實得 " + str(versions))
elif len(versions) == 3:
    print(f"version-pin: {next(iter(uniq))}")

# ── ⑤ marketplace source 指 repo 根 ───────────────────────────────────
if claude_market:
    plugins = claude_market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail(".claude-plugin/marketplace.json 必須有 plugins[]")
    else:
        source_is_repo_root(plugins[0].get("source"), ".claude-plugin/marketplace.json")
if cursor_market:
    plugins = cursor_market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail(".cursor-plugin/marketplace.json 必須有 plugins[]")
    else:
        source_is_repo_root(plugins[0].get("source"), ".cursor-plugin/marketplace.json")
        if plugins[0].get("name") != "dev-flow":
            fail(".cursor-plugin/marketplace.json plugin name 必須是 dev-flow")

# ── ⑥ 薄殼 ────────────────────────────────────────────────────────────
thin_shell(".cursor-plugin", {"plugin.json", "marketplace.json"})
thin_shell(".codex-plugin", {"plugin.json"})
thin_shell(".claude-plugin", {"plugin.json", "marketplace.json"})

# ── ⑦⑧⑨ 文件 ────────────────────────────────────────────────────────
plugin_md = read("docs/PLUGIN.md") or ""
guide = read("guides/guide-dev-flow.html") or ""
readme = read("README.md") or ""
host = host_section(guide) if guide else ""

if plugin_md:
    for needle, label in (
        (CLAUDE_ADD, "Claude 加市集"),
        (CLAUDE_INSTALL, "Claude 安裝"),
        (CODEX_MKT_ADD, "Codex 加市集"),
        (CODEX_ADD, "Codex 安裝"),
        (CODEX_UPGRADE, "Codex 更新市集"),
        (".cursor-plugin/plugin.json", "Cursor manifest"),
        (".codex-plugin/plugin.json", "Codex manifest"),
        ("Customize", "Cursor 官方安裝面"),
    ):
        if needle not in plugin_md:
            fail(f"docs/PLUGIN.md 少了{label}指令／路徑:{needle}")
    grok_claim_ok(plugin_md, "docs/PLUGIN.md")
    if "Grok marketplace" in plugin_md and "不要發明" not in plugin_md:
        fail("docs/PLUGIN.md 發明了 Grok marketplace")

if not host:
    fail("guide 沒有 #host")
else:
    for needle, label in (
        (CLAUDE_ADD, "Claude 加市集"),
        (CLAUDE_INSTALL, "Claude 安裝"),
        (CODEX_MKT_ADD, "Codex 加市集"),
        (CODEX_ADD, "Codex 安裝"),
        (".cursor-plugin/plugin.json", "Cursor manifest"),
        (".codex-plugin/plugin.json", "Codex manifest"),
        ("Customize", "Cursor 官方安裝面"),
        ("Cursor", "Cursor"),
        ("Grok", "Grok"),
        ("Codex", "Codex"),
    ):
        if needle not in host:
            fail(f"guide #host 少了{label}:{needle}")
    grok_claim_ok(host, "guide #host")

if readme:
    pre, sep, post = readme.partition("<details>")
    if not sep:
        fail("README 沒有 details（契約句必須留在 details,第一屏不准變手冊）")
    else:
        dumped = [
            n for n in (CLAUDE_ADD, CODEX_MKT_ADD, "codex plugin add", "/plugin install")
            if n in pre
        ]
        if dumped:
            fail("README 第一屏灌進安裝手冊:" + "、".join(dumped))
        if "PLUGIN.md" not in post:
            fail("README details 沒有 docs/PLUGIN.md 入口")
        print("readme-first-screen: ok")

if fails:
    print(f"FAIL: plugin-hosts {len(fails)} 項", file=sys.stderr)
    for item in fails:
        print(f"  - {item}", file=sys.stderr)
    sys.exit(1)
print(
    "PASS: plugin-hosts 三邊 manifest／整棵 skills／Claude 舊指令／"
    "Codex 實測動詞／Grok 牙"
)
sys.exit(0)
PY
