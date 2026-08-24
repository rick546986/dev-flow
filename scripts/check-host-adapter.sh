#!/bin/bash
# check-host-adapter.sh — 第一刀:DEVFLOW_ROOT + 三邊發現 + 節點可讀
#
# 為什麼需要:方法包要給 Cursor / Grok / Codex 跑,不能只靠 Claude 的
# CLAUDE_PLUGIN_ROOT。薄殼若只掛 SKILL.md,graph 與 nodes 全部讀不到(P0)。
# 本檔把「根目錄怎麼定、節點檔打不打得開、Claude 專用叫法有沒有寫讀哪份 MD」
# 變成機械契約。不重寫 1–7 站編成,不碰 --action 圍欄。
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


def main():
    tree = given_root
    try:
        pack = resolve_pack(tree)
    except CheckError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
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

    if fails:
        print(f"FAIL: host-adapter {len(fails)} 項", file=sys.stderr)
        for item in fails:
            print(f"  - {item}", file=sys.stderr)
        sys.exit(1)
    print("PASS: host-adapter DEVFLOW_ROOT / 節點可讀 / 別名")
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
