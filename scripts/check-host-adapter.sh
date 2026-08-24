#!/bin/bash
# check-host-adapter.sh — 第一刀:DEVFLOW_ROOT + 三邊發現 + 節點可讀
#                       第二刀:採用專案掛整棵(AGENTS.md / 技能連結 / 乘客清單)
#                       第三刀:主機探測 + 誰跑 --action(不改鬆圍欄)
#
# 為什麼需要:方法包要給 Cursor / Grok / Codex 跑,不能只靠 Claude 的
# CLAUDE_PLUGIN_ROOT。薄殼若只掛 SKILL.md,graph 與 nodes 全部讀不到(P0)。
# 採用專案沒有方法包時,正本仍在方法包;setup 必須掛整棵連結,不准只散發
# docs/dev/ 就當成功。非 Claude 主機沒有 AskUserQuestion／enabledPlugins／
# PreToolUse;把這三個當唯一進條件會假紅或卡住(P1)。本檔把這些變成機械
# 契約。不重寫 1–7 站編成,不准為了別的主機改鬆 --action 圍欄。
#
# 根目錄叫 DEVFLOW_ROOT。CLAUDE_PLUGIN_ROOT 當別名,不准刪。找不到就停,不准猜。
# 檢查腳本無參數時 dirname 推本 repo 根;有參數時只看那棵樹 + 環境變數,
# 不准偷偷用腳本位置當根(否則 no-root fixture 永遠假綠)。
#
# 用法:
#   scripts/check-host-adapter.sh [root]
# exit:0 = 全過 / 1 = 真違規 / 2 = 檢查自身故障
#
# 不改 check-devtalk-graph.sh / check-devstage2–7-graph.sh。
# 不改 _templates/ 正文。不改 memory/ 契約、.dev-flow/ 寫入點。

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
GIVEN_ROOT=""
if [ -n "${1:-}" ]; then
  GIVEN_ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$SELF_DIR" "$GIVEN_ROOT" <<'PY'
import os
import re
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

self_dir = sys.argv[1]
given_root = sys.argv[2] or ""
script_repo = os.path.dirname(self_dir)

PACK_MARKERS = ("skills", "hooks", "_templates", "README.md")
SKILL_ONLY_OK = {"dev-setup", "dev-run", "dev-release", "dev-report"}
FLOW_STAGES = ("stage2", "stage3", "stage4", "stage5", "stage6", "stage7")
STAGE6_CHAIN = ("N1-arm", "N2-handoff", "S2-tdd", "N4-selfcheck", "N5-end")
STAGE7_CHAIN = (
    "N0-role",
    "N1-matrix",
    "S2-run",
    "S2b-phenomena",
    "S2c-integration",
    "S2d-fresh",
    "S2e-walkthrough",
    "N3-axes",
    "N4-author",
    "N5-verdict",
)
FAIL_NO_PACK = "方法包沒掛上"
PLUGIN_PATH_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/")
DEVRUN_LOAD_RE = re.compile(
    r"(Skill tool.*dev-run|自動載入\s*`dev-run`|載入 `dev-run` 引擎)",
    re.I | re.S,
)
REVIEWER_TYPE_RE = re.compile(
    r"subagent_type\s*=\s*dev-flow:devflow-reviewer"
)
ADVISER_TYPE_RE = re.compile(
    r"subagent_type\s*=\s*dev-flow:devflow-adviser"
)
HOST_SKILLS = ("dev-setup", "dev-talk", "dev-flow", "dev-run")
HOST_MOUNT_DIRS = (".cursor/skills", ".agents/skills", ".codex/skills")
AGENTS_POINTER = (
    "這專案用 DevFlow。技能在方法包 skills/。"
    "開工讀該技能 SKILL.md，下一跳看 graph.yaml。"
    "不要把流程規則貼進本檔。"
)
AGENTS_DUMP_NEEDLES = (
    "AskUserQuestion",
    "enabledPlugins",
    "skill-legacy",
    "盲原則",
    "G1",
    "G2",
    "G3",
    "執行清單 0-",
)
SETUP_INSTALL_NEEDLES = (
    "DEVFLOW_ROOT 解析失敗",
    "大聲停",
    "不准只散發 docs/dev/",
    "AGENTS.md",
    "不要把流程規則貼進本檔",
    ".cursor/skills/",
    ".agents/skills/",
    ".codex/skills/",
    "技能庫掛整棵",
    "不要假裝能從產品 repo 自動灌進 Grok",
    "不要把節點 MD 複製",
    "相對 DEVFLOW_ROOT",
    "散發副本",
    "stage2",
    "stage7",
)
HOST_PROBE_NEEDLES = (
    "先探測主機",
    "AskUserQuestion",
    "enabledPlugins",
    "hooks.json",
    "不要把這三個當唯一核可",
    "技能目錄",
    "整棵",
    "誰開工誰先跑",
    "--action",
    "不准為了別的主機改鬆",
    ".cursor/rules/",
    "AGENTS.md 一行",
)
README_DUMP_NEEDLES = ("第一刀", "第二刀", "第三刀", "刀序")
HOST_MARKERS = ("claude", "cursor", "codex", "grok")
ACTION_SCRIPTS = (
    "scripts/check-devtalk-graph.sh",
    "scripts/check-devstage2-graph.sh",
    "scripts/check-devstage3-graph.sh",
    "scripts/check-devstage4-graph.sh",
    "scripts/check-devstage5-graph.sh",
    "scripts/check-devstage6-graph.sh",
    "scripts/check-devstage7-graph.sh",
)


class CheckError(Exception):
    pass


def is_pack(path):
    if not path or not os.path.isdir(path):
        return False
    for name in PACK_MARKERS:
        target = os.path.join(path, name)
        if name == "README.md":
            if not os.path.isfile(target):
                return False
        elif not os.path.isdir(target):
            return False
    return True


def walk_up_to_pack(start):
    cur = os.path.abspath(start)
    if os.path.isfile(cur):
        cur = os.path.dirname(cur)
    while True:
        if os.path.isdir(os.path.join(cur, "skills")) and os.path.isdir(
            os.path.join(cur, "hooks")
        ):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return ""
        cur = parent


def env_root(name):
    val = os.environ.get(name, "").strip()
    return os.path.abspath(val) if val else ""


def resolve_pack(tree):
    """順序:DEVFLOW_ROOT → CLAUDE_PLUGIN_ROOT → 從 SKILL.md 往上 → 樹自己是包。

    有參數的樹不准回退到檢查腳本所在 repo(那是猜)。
    環境變數有設但指向的不是方法包 → 停,不准改猜下一層。
    """
    for name in ("DEVFLOW_ROOT", "CLAUDE_PLUGIN_ROOT"):
        val = env_root(name)
        if not val:
            continue
        if is_pack(val):
            return val
        raise CheckError(
            f"{FAIL_NO_PACK}:環境變數 {name}={val} 看不見 "
            "skills/、hooks/、_templates/、README.md"
        )

    if tree:
        skill_hits = []
        skills_dir = os.path.join(tree, "skills")
        if os.path.isdir(skills_dir):
            for root, _dirs, files in os.walk(skills_dir):
                if "SKILL.md" in files:
                    skill_hits.append(os.path.join(root, "SKILL.md"))
                    break
        if skill_hits:
            walked = walk_up_to_pack(skill_hits[0])
            if walked and is_pack(walked):
                return walked
        if is_pack(tree):
            return tree
        raise CheckError(
            f"{FAIL_NO_PACK}:這棵樹推不到同時有 skills/ 與 hooks/ 的方法包根"
        )

    if is_pack(script_repo):
        return script_repo
    raise CheckError(f"{FAIL_NO_PACK}:檢查腳本 dirname 也推不到方法包根")


def parse_graph_nodes(text):
    nodes = {}
    current = None
    for raw in text.splitlines():
        if re.match(r"^  [A-Za-z0-9._-]+:\s*$", raw):
            current = raw.strip()[:-1]
            nodes[current] = {}
            continue
        if current is None:
            continue
        m_file = re.match(r"^    file:\s*(\S+)\s*$", raw)
        if m_file:
            nodes[current]["file"] = m_file.group(1).strip().strip("'\"")
        m_kind = re.match(r"^    kind:\s*(\S+)\s*$", raw)
        if m_kind:
            nodes[current]["kind"] = m_kind.group(1).strip().strip("'\"")
        m_entry = re.match(r"^    entry:\s*(\S+)\s*$", raw)
        if m_entry:
            nodes[current]["entry"] = m_entry.group(1).strip().strip("'\"")
    return nodes


def iter_md(pack, rel_dir):
    base = os.path.join(pack, rel_dir)
    if not os.path.isdir(base):
        return
    for root, _dirs, files in os.walk(base):
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(root, name)


def has_alias_decl(text):
    return ("DEVFLOW_ROOT" in text) and (
        "別名" in text or "舊名" in text or "CLAUDE_PLUGIN_ROOT" in text
    )


def looks_like_setup_done(tree):
    if not tree:
        return False
    docs = os.path.join(tree, "docs", "dev")
    if not os.path.isdir(docs):
        return False
    return any(
        os.path.exists(os.path.join(docs, name))
        for name in ("README.md", "STATUS.md", ".devflow-baseline")
    )


def mount_is_whole_tree(path, name):
    real = os.path.realpath(path)
    if not os.path.isdir(real):
        return False
    if not os.path.isfile(os.path.join(real, "SKILL.md")):
        return False
    if name in SKILL_ONLY_OK:
        return True
    if name == "dev-flow":
        for stage in FLOW_STAGES:
            stage_dir = os.path.join(real, stage)
            if not (
                os.path.isdir(stage_dir)
                and os.path.isfile(os.path.join(stage_dir, "graph.yaml"))
                and os.path.isdir(os.path.join(stage_dir, "nodes"))
            ):
                return False
        return True
    return os.path.isfile(os.path.join(real, "graph.yaml")) and os.path.isdir(
        os.path.join(real, "nodes")
    )


def iter_host_mounts(tree):
    if not tree:
        return
    for host in HOST_MOUNT_DIRS:
        base = os.path.join(tree, host)
        if not os.path.isdir(base):
            continue
        try:
            names = os.listdir(base)
        except OSError:
            continue
        for name in sorted(names):
            path = os.path.join(base, name)
            if os.path.islink(path) or os.path.isdir(path):
                yield host, name, path


def passenger_canon_ok(text):
    if "相對 DEVFLOW_ROOT" in text or "${DEVFLOW_ROOT}/_templates" in text:
        return True
    return False


def detect_host(tree):
    if not tree:
        return ""
    marker = os.path.join(tree, ".devflow-host")
    if os.path.isfile(marker):
        val = open(marker, encoding="utf-8").read().strip().lower()
        if val in HOST_MARKERS:
            return val
    if os.path.isdir(os.path.join(tree, ".cursor")):
        return "cursor"
    if os.path.isdir(os.path.join(tree, ".agents")) or os.path.isdir(
        os.path.join(tree, ".codex")
    ):
        return "codex"
    if os.path.isdir(os.path.join(tree, ".grok")):
        return "grok"
    if os.path.isdir(os.path.join(tree, ".claude")):
        return "claude"
    return ""


def other_hosts_still_require_claude_gates(text):
    """非 Claude 仍把 AskUserQuestion／enabledPlugins 當唯一進條件。"""
    if "AskUserQuestion" not in text or "enabledPlugins" not in text:
        return False
    branched = ("不要把這三個當唯一核可" in text) and ("先探測主機" in text)
    return not branched


def extract_html_section(html, anchor):
    m = re.search(
        rf'<h2 id="{re.escape(anchor)}">.*?(?=<h2\b|\Z)',
        html,
        re.S,
    )
    return m.group(0) if m else ""


def cursor_rules_pointer_ok(tree):
    rules = os.path.join(tree, ".cursor", "rules")
    if not os.path.isdir(rules):
        return False
    try:
        names = os.listdir(rules)
    except OSError:
        return False
    for name in names:
        path = os.path.join(rules, name)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        dumped = any(n in text for n in AGENTS_DUMP_NEEDLES) and (
            "不要把流程" not in text
        )
        if dumped:
            return False
        if "架構不變量" in text or "arch-invariants" in text:
            return True
    return False


def main():
    tree = given_root
    try:
        pack = resolve_pack(tree)
    except CheckError as exc:
        msg = str(exc)
        if tree and looks_like_setup_done(tree):
            msg = (
                "setup 宣稱成功，但 DEVFLOW_ROOT 推不到、產品樹也沒有方法包"
                f"（{msg}）"
            )
        print(f"FAIL: {msg}", file=sys.stderr)
        sys.exit(1)

    print(f"DEVFLOW_ROOT={pack}")
    fails = []

    def fail(msg):
        fails.append(msg)

    # ── 薄殼:該有 graph 的技能必須掛整棵 ──────────────────────────
    skills_root = os.path.join(pack, "skills")
    if not os.path.isdir(skills_root):
        fail(f"{FAIL_NO_PACK}:沒有 skills/")
    else:
        for name in sorted(os.listdir(skills_root)):
            skill_dir = os.path.join(skills_root, name)
            if not os.path.isdir(skill_dir):
                continue
            skill_md = os.path.join(skill_dir, "SKILL.md")
            graph = os.path.join(skill_dir, "graph.yaml")
            nodes = os.path.join(skill_dir, "nodes")
            if name in SKILL_ONLY_OK:
                continue
            if name == "dev-flow":
                if not os.path.isfile(skill_md):
                    fail("skills/dev-flow 缺 SKILL.md")
                for stage in FLOW_STAGES:
                    stage_dir = os.path.join(skill_dir, stage)
                    if not os.path.isdir(stage_dir):
                        fail(f"skills/dev-flow/{stage} 不存在(薄殼必須掛整棵 stage 目錄)")
                        continue
                    if not os.path.isfile(os.path.join(stage_dir, "graph.yaml")):
                        fail(
                            f"skills/dev-flow/{stage} 只有薄殼、沒有 graph.yaml"
                        )
                    if not os.path.isdir(os.path.join(stage_dir, "nodes")):
                        fail(
                            f"skills/dev-flow/{stage} 沒有 nodes/"
                        )
                continue
            if os.path.isfile(skill_md) and not (
                os.path.isfile(graph) and os.path.isdir(nodes)
            ):
                fail(
                    f"技能目錄 {name} 只有 SKILL.md、沒有 graph.yaml 或 nodes/"
                    "(setup／run 除外)"
                )

    # ── graph.yaml file: 相對技能目錄;skill-legacy entry 相對 DEVFLOW_ROOT
    graph_paths = []
    talk_graph = os.path.join(pack, "skills", "dev-talk", "graph.yaml")
    if os.path.isfile(talk_graph):
        graph_paths.append(
            (talk_graph, os.path.join(pack, "skills", "dev-talk"))
        )
    for stage in FLOW_STAGES:
        gp = os.path.join(pack, "skills", "dev-flow", stage, "graph.yaml")
        if os.path.isfile(gp):
            graph_paths.append(
                (gp, os.path.join(pack, "skills", "dev-flow", stage))
            )

    for gp, skill_dir in graph_paths:
        try:
            text = open(gp, encoding="utf-8").read()
        except OSError as exc:
            fail(f"打不開 {gp}:{exc}")
            continue
        nodes = parse_graph_nodes(text)
        for node_id, spec in nodes.items():
            kind = spec.get("kind", "")
            if kind in ("skill-legacy", "skill-legacy"):
                entry = spec.get("entry", "")
                if not entry:
                    fail(f"{node_id} kind: {kind} 缺 entry")
                    continue
                target = entry if os.path.isabs(entry) else os.path.join(pack, entry)
                if not os.path.isfile(target):
                    fail(
                        f"{node_id} kind: {kind} 的 entry 相對 DEVFLOW_ROOT 打不開:{entry}"
                    )
                continue
            rel = spec.get("file", "")
            if not rel:
                continue
            target = rel if os.path.isabs(rel) else os.path.join(skill_dir, rel)
            if not os.path.isfile(target):
                fail(
                    f"graph.yaml 的 file: 相對技能目錄打不開:{rel} ({node_id})"
                )

    # ── 節點／SKILL 不得只寫死 CLAUDE_PLUGIN_ROOT;N1-start 必查
    scan_dirs = [
        os.path.join("skills", "dev-talk"),
        os.path.join("skills", "dev-flow"),
        os.path.join("skills", "dev-run"),
        os.path.join("skills", "dev-setup"),
    ]
    n1 = os.path.join(pack, "skills", "dev-talk", "nodes", "N1-start.md")
    if os.path.isfile(n1):
        n1_text = open(n1, encoding="utf-8").read()
        if PLUGIN_PATH_RE.search(n1_text) and not has_alias_decl(n1_text):
            fail(
                "talk 的 N1-start 還寫死 ${CLAUDE_PLUGIN_ROOT} 且沒宣告別名"
            )
        if not (
            "DEVFLOW_ROOT" in n1_text and "memory/dev-memory.py" in n1_text
        ):
            fail(
                "talk 的 N1-start 記憶指令組不出 ${DEVFLOW_ROOT}/memory/dev-memory.py"
            )
        mem = os.path.join(pack, "memory", "dev-memory.py")
        if not os.path.isfile(mem):
            fail("記憶指令組得出路徑但 DEVFLOW_ROOT/memory/dev-memory.py 打不開")
        print("readable: skills/dev-talk/nodes/N1-start.md")
        print("memory-cmd: memory/dev-memory.py")
    else:
        fail("讀不到 skills/dev-talk/nodes/N1-start.md")

    for rel in scan_dirs:
        for path in iter_md(pack, rel):
            text = open(path, encoding="utf-8").read()
            rel_path = os.path.relpath(path, pack)
            if PLUGIN_PATH_RE.search(text) and not has_alias_decl(text):
                fail(
                    f"{rel_path} 還寫死 ${{CLAUDE_PLUGIN_ROOT}} 且沒宣告別名"
                )
            if DEVRUN_LOAD_RE.search(text) and "skills/dev-run/SKILL.md" not in text:
                fail(
                    f"{rel_path} 用 Claude 專用叫法載入 dev-run,沒寫讀 skills/dev-run/SKILL.md"
                )
            if REVIEWER_TYPE_RE.search(text) and "agents/devflow-reviewer.md" not in text:
                fail(
                    f"{rel_path} 用 subagent_type=dev-flow:devflow-reviewer 當唯一叫法,"
                    "沒寫讀 agents/devflow-reviewer.md"
                )
            if ADVISER_TYPE_RE.search(text) and "agents/devflow-adviser.md" not in text:
                fail(
                    f"{rel_path} 用 subagent_type=dev-flow:devflow-adviser 當唯一叫法,"
                    "沒寫讀 agents/devflow-adviser.md"
                )

    # ── 第 4 站:STATUS 在第 4 站時必須讀得到這兩檔。方法包裡它們永遠要在,
    #    不因本 repo 的 STATUS.md 是改版看板就略過。
    s4_graph = os.path.join(pack, "skills", "dev-flow", "stage4", "graph.yaml")
    s4_node = os.path.join(
        pack, "skills", "dev-flow", "stage4", "nodes", "N1-handoff.md"
    )
    if not os.path.isfile(s4_graph):
        fail("dev-flow 第 4 站讀不到 stage4/graph.yaml")
    else:
        print("readable: skills/dev-flow/stage4/graph.yaml")
    if not os.path.isfile(s4_node):
        fail("dev-flow 第 4 站讀不到 N1-handoff.md")
    else:
        print("readable: skills/dev-flow/stage4/nodes/N1-handoff.md")

    # ── 第 6／7 站鏈每個真節點檔在
    for node_id in STAGE6_CHAIN:
        path = os.path.join(
            pack, "skills", "dev-flow", "stage6", "nodes", f"{node_id}.md"
        )
        if not os.path.isfile(path):
            fail(f"第 6 站鏈缺真節點檔 {node_id}.md")
        else:
            print(f"readable: skills/dev-flow/stage6/nodes/{node_id}.md")
    for node_id in STAGE7_CHAIN:
        path = os.path.join(
            pack, "skills", "dev-flow", "stage7", "nodes", f"{node_id}.md"
        )
        if not os.path.isfile(path):
            fail(f"第 7 站鏈缺真節點檔 {node_id}.md")
        else:
            print(f"readable: skills/dev-flow/stage7/nodes/{node_id}.md")

    # ── 第二刀:setup SKILL 真寫(有 ## install 才驗,迷你 fixture 不灌全文)
    setup_skill = os.path.join(pack, "skills", "dev-setup", "SKILL.md")
    setup_text = ""
    if os.path.isfile(setup_skill):
        setup_text = open(setup_skill, encoding="utf-8").read()
        if "## install" in setup_text:
            for needle in SETUP_INSTALL_NEEDLES:
                if needle not in setup_text:
                    fail(
                        f"skills/dev-setup/SKILL.md ## install 缺「{needle}」"
                        "（DEVFLOW_ROOT 解析失敗要大聲停,不准只散發 docs/dev/ 就當成功）"
                    )
        # 第三刀:有 ## 主機探測或完整 ## check 才驗(迷你 fixture 不灌全文)
        if "## 主機探測" in setup_text or (
            "## check" in setup_text and "enabledPlugins" in setup_text
        ):
            for needle in HOST_PROBE_NEEDLES:
                if needle not in setup_text:
                    fail(
                        f"skills/dev-setup/SKILL.md 主機探測缺「{needle}」"
                        "（先探測主機再選檢查;非 Claude 不要把 AskUserQuestion／"
                        "enabledPlugins 當唯一進條件）"
                    )
            if other_hosts_still_require_claude_gates(setup_text):
                fail(
                    "非 Claude 仍把 AskUserQuestion／enabledPlugins 當唯一進條件"
                )

    # ── 第二刀:節點乘客清單必須相對 DEVFLOW_ROOT,不准只找產品 docs/dev/_templates
    for path in iter_md(pack, os.path.join("skills", "dev-flow")):
        rel_path = os.path.relpath(path, pack).replace("\\", "/")
        if "/nodes/" not in rel_path:
            continue
        text = open(path, encoding="utf-8").read()
        if re.search(
            r"(乘客清單|執行清單|清單)正本[是在都]*\s*`docs/dev/_templates",
            text,
        ) or (
            "docs/dev/_templates" in text
            and "乘客" in text
            and "散發副本" not in text
        ):
            fail(
                f"{rel_path} 把乘客清單寫成只找產品 docs/dev/_templates/、"
                "不經 DEVFLOW_ROOT"
            )
        if "_templates/" in text and not passenger_canon_ok(text):
            fail(
                f"{rel_path} 乘客清單沒寫相對 DEVFLOW_ROOT 的 _templates/"
            )

    # ── 第二刀:AGENTS.md 若在,只准一行指標;灌流程必須紅
    agents_roots = []
    if tree:
        agents_roots.append(tree)
    if pack and pack not in agents_roots:
        agents_roots.append(pack)
    seen_agents = set()
    for root in agents_roots:
        agents_path = os.path.join(root, "AGENTS.md")
        real = os.path.abspath(agents_path)
        if real in seen_agents:
            continue
        seen_agents.add(real)
        if not os.path.isfile(agents_path):
            continue
        text = open(agents_path, encoding="utf-8").read()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if "這專案用 DevFlow" not in text or "不要把流程規則貼進本檔" not in text:
            fail("AGENTS.md 缺少一行指標（這專案用 DevFlow…不要把流程規則貼進本檔）")
        if len(lines) > 3 or any(n in text for n in AGENTS_DUMP_NEEDLES):
            fail(
                "AGENTS.md 被灌進流程規則（超過一行指標 + 必要的「不要把流程貼進本檔」）"
            )
        else:
            print("agents-pointer: ok")

    # ── 第二刀:主機技能連結若在,必須是整棵;setup 宣稱成功還要四個 DV 都掛上
    is_adopter = bool(tree) and os.path.abspath(tree) != os.path.abspath(pack)
    found_mounts = {host: {} for host in HOST_MOUNT_DIRS}
    mount_scan = tree if tree else pack
    for host, name, path in iter_host_mounts(mount_scan):
        ok = mount_is_whole_tree(path, name)
        found_mounts[host][name] = ok
        if not ok:
            fail(
                f"{host}/{name} 只有 SKILL.md、沒有 graph.yaml／nodes/"
                "（setup／run 除外）"
            )
        else:
            print(f"link-whole: {host}/{name}")

    if is_adopter and looks_like_setup_done(tree):
        agents_path = os.path.join(tree, "AGENTS.md")
        if not os.path.isfile(agents_path):
            fail("setup 宣稱成功，但沒有 AGENTS.md 一行指標")
        for host in (".cursor/skills", ".agents/skills"):
            for name in HOST_SKILLS:
                if not found_mounts[host].get(name):
                    fail(
                        f"setup 宣稱成功，但 {host}/{name} 不是整棵目錄"
                    )
        if os.path.isdir(os.path.join(tree, ".codex", "skills")):
            for name in HOST_SKILLS:
                if not found_mounts[".codex/skills"].get(name):
                    fail(
                        f"setup 宣稱成功，探測到 .codex/skills/ 但 {name} 不是整棵"
                    )

    # ── 第三刀:主機探測 + guide #host + README 一行 + 不改鬆 --action
    host = detect_host(tree) if tree else ""
    if host:
        print(f"host={host}")

    if setup_text and other_hosts_still_require_claude_gates(setup_text):
        if host in ("cursor", "codex", "grok"):
            fail(
                "非 Claude fixture 仍把 AskUserQuestion／enabledPlugins 當唯一進條件"
            )

    if host == "claude":
        if setup_text and (
            "AskUserQuestion" in setup_text
            and "enabledPlugins" in setup_text
            and "hooks.json" in setup_text
        ):
            print("old-checks: ok")
        elif setup_text and "## check" in setup_text:
            fail("Claude fixture 舊檢查(AskUserQuestion／enabledPlugins／hooks.json)走不了")
        else:
            print("old-checks: ok")

    if host in ("cursor", "codex", "grok"):
        print("setup-health: skill-dirs+DEVFLOW_ROOT")
        if is_adopter and looks_like_setup_done(tree) and host == "cursor":
            if not cursor_rules_pointer_ok(tree):
                fail(
                    "Cursor setup 宣稱成功，但沒有 .cursor/rules/ 架構不變量指標"
                    "（或指標被灌進流程規則）"
                )

    guide_path = os.path.join(pack, "guides", "guide-dev-flow.html")
    if os.path.isfile(guide_path):
        guide_text = open(guide_path, encoding="utf-8").read()
        host_sec = extract_html_section(guide_text, "host")
        if not host_sec:
            fail("guide 沒有 #host（或同等錨點）說明三邊發現 + 誰跑 --action")
        else:
            missing = []
            for needle in (
                "Cursor",
                "Grok",
                "Codex",
                "--action",
                "誰開工",
                "PreToolUse",
            ):
                if needle not in host_sec:
                    missing.append(needle)
            if missing:
                fail(
                    "guide #host 沒說明三邊發現 + 誰跑 --action:"
                    + "、".join(missing)
                )
            else:
                print("guide-host: ok")

    readme_path = os.path.join(pack, "README.md")
    if os.path.isfile(readme_path):
        readme = open(readme_path, encoding="utf-8").read()
        looks_index = (
            "guide-dev-flow" in readme
            or "#host" in readme
            or ("Cursor" in readme and "Codex" in readme)
        )
        if looks_index:
            if "#host" not in readme:
                fail("README 沒有一行入口指到 guide #host")
            dumped = [n for n in README_DUMP_NEEDLES if n in readme]
            if dumped:
                fail("README 灌進流程／刀序（只准一行入口）:" + "、".join(dumped))
            if ".cursor/skills" in readme and ".agents/skills" in readme:
                fail("README 灌進發現清單（只准一行入口）")
            if "AskUserQuestion" in readme:
                fail("README 灌進流程（AskUserQuestion 不該出現在 README）")
            print("readme-host-entry: ok")

    # 對照組:第 2–7 站（+ talk）既有 --action 入口還在。不准改鬆圍欄。
    # 實際 deny 案例仍紅由 test-host-adapter.sh 跑既有 fixture。
    action_scan_root = pack if os.path.isdir(os.path.join(pack, "scripts")) else ""
    if action_scan_root:
        loosened = []
        for rel in ACTION_SCRIPTS:
            path = os.path.join(action_scan_root, rel)
            if not os.path.isfile(path):
                loosened.append(f"{rel} 不見了")
                continue
            text = open(path, encoding="utf-8").read()
            if '[ "${1:-}" = "--action" ]' not in text:
                loosened.append(f"{rel} 不再接 --action")
        if loosened:
            fail("有人改鬆既有 --action 圍欄:" + "; ".join(loosened))
        else:
            print("action-fence: intact")

    if fails:
        print(f"FAIL: host-adapter {len(fails)} 項", file=sys.stderr)
        for item in fails:
            print(f"  - {item}", file=sys.stderr)
        sys.exit(1)
    print(
        "PASS: host-adapter DEVFLOW_ROOT / 節點可讀 / 別名 / 採用專案掛整棵"
        " / 主機探測 / --action"
    )
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        sys.exit(2)
PY
