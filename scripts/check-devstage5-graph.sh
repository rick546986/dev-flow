#!/bin/bash
# check-devstage5-graph.sh — Stage 5 第三刀的機械契約
#
# 為什麼需要:把第 5 站切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   1. 沒有 stage5/graph.yaml 必須紅:舊實作(單一 SKILL、沒有 graph)無法證明
#      下一跳與重跑契約。
#   2. 真節點缺「進條件」或「完成條件」必須紅:節點不能單獨當入口。
#   3. 同 slug 第二份 5-tasks*.md 必須紅:產物仍是一份。
#   4. write_mode≠overwrite 必須紅:重跑寫檔節點覆寫同一檔,不另存。
#   5. 缺 N4-write-md 必須紅:必須有寫檔節點,不要只做 handoff。
#   6. 未過 G2(4-spec 不是 approved)卻 write_tasks(寫 5-tasks.md)必須紅:
#      第 4 站還沒核准不准搶跑第 5 站。
#   7. 5-tasks 未 approved 卻 write_notes(寫 6-implementation-notes.md)必須紅:
#      第 6 站還沒開始。
#   8. 第二刀:乘客步 1／2／3／4 必須是真節點檔。kind: skill-legacy 團塊必須紅 ——
#      第一刀的暫留 hop 到這一刀就沒有存在理由了。
#      每個真節點「做什麼」必須 --write-cursor <本節點 id>。
#      S1-slice／S2-fields／S3-deps／S4-selfcheck 與 N4-write-md 才 allow
#      write_tasks(同一份 5-tasks.md,overwrite);不要放寬 N1-handoff／
#      N5-twin／N6-end。
#   9. 第二刀:四必填欄(Covers／Files／Verify／Blocked-by)缺一必須紅 —— 判準呼叫
#      現有 parser 的 parse_5_tasks,本檔不再寫第二套解析,也不改那支 parser。
#      S4-selfcheck 的「做什麼」必須點名它。
#  10. 第三刀:--action 必須接到 prebash,不能只活在 test fixture。guide 第 5 站
#      開頭必須對上八節點鏈。出現「Stage 5 還在單一 SKILL」必須紅。
#      不改第 1／2／3／4 站的編成。
#
# 本檔唯讀:探測既有 parser 是 import,而 import 預設寫 __pycache__,那份 .pyc
# 會落在 hooks/ 與 tests/parallel-stage6/ —— 正好在 test-architecture-guards 收尾
# 比對的檔案指紋範圍內,檢查於是自己成了污染源(2026-08-24 CI 實證)。load_parser
# 因此關掉位元碼寫入;test-devstage5-graph.sh 的 G-readonly 用整棵樹的 sha256 釘死。
#
# graph.yaml 是下一跳的唯一正本。分叉與暫留一律用 next 指到的真節點,禁止 via
# (第 1 站 0030 的假綠就是 via 字串當 hop 換來的)。
# 本機游標 .devstage5-cursor.json 不進 Git。
# 不改 check-devtalk-graph.sh / check-devstage2-graph.sh / check-devstage3-graph.sh /
# check-devstage4-graph.sh。
# 不改 _templates/5-tasks.md 正文(乘客清單正本是它的頂註 0–6)。
# 不改 contract_ref.py / hooks/devflow-lib.py 的 parse_5_tasks、不把
# scripts/check-task-slicing.sh 改成 exit 1、不改 scripts/build-gate-twin.py
# (一律只呼叫)。
# 不改 hooks/devflow-exec.sh 的 start:未過 G2 拒啟是它本來就有的行為,
# test-devstage5-graph.sh 只把它釘住,不在這裡重寫一套。
#
# 用法:
#   scripts/check-devstage5-graph.sh [root]
#   scripts/check-devstage5-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node,slug},action,slug?}
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devstage5-graph.sh --write-cursor NODE [SLUG] [root]
#       把 .devstage5-cursor.json 寫成 {node, slug}。不改 .dev-flow。
#
# exit:0 = 全過 / 1 = 真違規 / 2 = 檢查自身故障(NOT-PARSED)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
ACTION_FILE=""
WRITE_NODE=""
WRITE_SLUG=""
if [ "${1:-}" = "--action" ]; then
  ACTION_FILE=${2:-}
  [ -n "$ACTION_FILE" ] || { echo "FATAL: --action 需要 JSON 路徑" >&2; exit 2; }
  if [ -n "${3:-}" ]; then
    ROOT=$(cd "$3" && pwd) || exit 2
  fi
elif [ "${1:-}" = "--write-cursor" ]; then
  WRITE_NODE=${2:-}
  [ -n "$WRITE_NODE" ] || {
    echo "FATAL: --write-cursor 需要 NODE" >&2
    exit 2
  }
  if [ -n "${3:-}" ]; then
    if [ -d "${3:-}" ]; then
      ROOT=$(cd "$3" && pwd) || exit 2
    else
      WRITE_SLUG=$3
      if [ -n "${4:-}" ]; then
        ROOT=$(cd "$4" && pwd) || exit 2
      fi
    fi
  fi
elif [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" "$ACTION_FILE" "$WRITE_NODE" "$WRITE_SLUG" <<'PY'
import json
import os
import re
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]
action_file = sys.argv[2]
write_node = sys.argv[3] if len(sys.argv) > 3 else ""
write_slug = sys.argv[4] if len(sys.argv) > 4 else ""

if write_node:
    dest = os.path.join(root, ".devstage5-cursor.json")
    tmp = dest + ".tmp"
    payload = {"node": write_node}
    if write_slug:
        payload["slug"] = write_slug
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")
    os.replace(tmp, dest)
    print(f"wrote {dest} node={write_node}")
    sys.exit(0)

STAGE5 = os.path.join(root, "skills", "dev-flow", "stage5")
GRAPH_PATH = os.path.join(STAGE5, "graph.yaml")
SKILL_PATH = os.path.join(root, "skills", "dev-flow", "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")

ENTRY_NODE = "N1-handoff"
WRITE_TASKS_NODE = "N4-write-md"
SELFCHECK_NODE = "S4-selfcheck"
# 第二刀:八個真節點檔,沒有 skill-legacy 團塊。
CHAIN = (
    "N1-handoff",
    "S1-slice",
    "S2-fields",
    "S3-deps",
    "N4-write-md",
    "S4-selfcheck",
    "N5-twin",
    "N6-end",
)
REQUIRED_NODES = CHAIN
EXPECTED_NEXT = {
    "N1-handoff": "S1-slice",
    "S1-slice": "S2-fields",
    "S2-fields": "S3-deps",
    "S3-deps": "N4-write-md",
    "N4-write-md": "S4-selfcheck",
    "S4-selfcheck": "N5-twin",
    "N5-twin": "N6-end",
    "N6-end": "",
}
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
CANONICAL_MD = "docs/dev/<slug>/5-tasks.md"
LOCKED_ACTIONS = ("write_tasks", "write_notes")
# 乘客步 1／2／3／4 與定稿節點共寫同一份 5-tasks.md(overwrite)。
# write_notes 本刀任何節點都不得 allow。
TASKS_ALLOWED_NODES = (
    "S1-slice",
    "S2-fields",
    "S3-deps",
    "N4-write-md",
    "S4-selfcheck",
)
TASKS_FORBIDDEN_NODES = ("N1-handoff", "N5-twin", "N6-end")
# 四必填欄的機器判準:現有 parser,不在本檔另寫一套解析。
PARSER_PATHS = (
    os.path.join("hooks", "devflow-lib.py"),
    os.path.join("tests", "parallel-stage6", "contract_ref.py"),
)
PARSER_REF = "contract_ref.py"
PARSER_FUNC = "parse_5_tasks"
GUIDE_PATH = os.path.join(root, "guides", "guide-dev-flow.html")
STALE_GUIDE = "Stage 5 還在單一 SKILL"
REQUIRED_FIELDS = ("Covers", "Files", "Verify", "Blocked-by")
PROBE_TASKS = """---
feature: probe-slug
stage: 5-tasks
status: approved
---

## T-1 建 probe 用的最小 T
- [ ] 完成
- Covers: R-1 / S-1
- Files: src/probe.py, src/probe_test.py
- Verify: `pytest -q tests/probe`
- Blocked-by: —
"""

NEXT_ID_RE = re.compile(
    r"(?:S\d+-[A-Za-z0-9-]+|N(?:\d+)?-[A-Za-z0-9-]+|skill-legacy-\d+(?:-\d+)?)"
)
BAD_TASKS_RE = re.compile(r"5-tasks(?:-[A-Za-z0-9]+)+\.md")
STATUS_RE = re.compile(r"^status:\s*(\S+)", re.M)


class GraphError(Exception):
    pass


def parse_simple_yaml(text):
    """受限 YAML:對應本檔契約所需的 map / list / 純量,不引入外部套件。"""
    lines = []
    for raw in text.splitlines():
        if (not raw.strip()) or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise GraphError("graph.yaml 縮排必須是 2 的倍數")
        lines.append((indent, raw.lstrip(" ")))

    def parse_scalar(raw):
        raw = raw.strip()
        if raw in ("", "null", "~", '""', "''"):
            return ""
        if (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            return raw[1:-1]
        if raw == "[]":
            return []
        return raw

    def parse_block(index, indent):
        mapping = {}
        sequence = []
        mode = None
        while index < len(lines):
            current_indent, content = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise GraphError(f"graph.yaml 縮排跳動:{content}")
            if content.startswith("- "):
                if mode == "map":
                    raise GraphError("graph.yaml 同一層不能混用 map 與 list")
                mode = "list"
                item = content[2:].strip()
                if item and ":" in item and not item.startswith("{"):
                    key, _, rest = item.partition(":")
                    nested, index = parse_block(index + 1, indent + 2)
                    value = parse_scalar(rest) if rest.strip() else {}
                    if nested:
                        if not isinstance(value, dict):
                            value = {}
                        value.update(nested)
                    sequence.append({key.strip(): value})
                elif item:
                    sequence.append(parse_scalar(item))
                    index += 1
                else:
                    nested, index = parse_block(index + 1, indent + 2)
                    sequence.append(nested)
                continue
            if ":" not in content:
                raise GraphError(f"graph.yaml 讀不懂:{content}")
            if mode == "list":
                raise GraphError("graph.yaml 同一層不能混用 map 與 list")
            mode = "map"
            key, _, rest = content.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest:
                mapping[key] = parse_scalar(rest)
                index += 1
            else:
                nested, index = parse_block(index + 1, indent + 2)
                mapping[key] = nested
        if mode == "list":
            return sequence, index
        return mapping, index

    data, consumed = parse_block(0, 0)
    if consumed != len(lines):
        raise GraphError("graph.yaml 有未消化的行")
    if not isinstance(data, dict):
        raise GraphError("graph.yaml 根必須是 map")
    return data


def load_graph():
    if not os.path.isfile(GRAPH_PATH):
        return None, [
            "缺 skills/dev-flow/stage5/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
            "無法證明下一跳與重跑契約"
        ]
    try:
        data = parse_simple_yaml(open(GRAPH_PATH, encoding="utf-8").read())
    except GraphError as exc:
        return None, [f"graph.yaml 不是可解析的契約:{exc}"]
    nodes = data.get("nodes")
    if not isinstance(nodes, dict) or not nodes:
        return None, ["graph.yaml 缺 nodes map"]
    return data, []


def node_path(node_id, spec):
    rel = spec.get("file") if isinstance(spec, dict) else ""
    if not rel:
        rel = f"nodes/{node_id}.md"
    return os.path.join(STAGE5, rel.replace("/", os.sep))


def split_sections(text):
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    out = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[match.group(1).strip()] = text[match.end():end]
    return out


def first_next_id(section_text):
    stripped = section_text.strip()
    if re.search(
        r"^(無|結束|（無）|\(none\))$",
        stripped.splitlines()[0].strip() if stripped else "",
    ):
        return ""
    match = NEXT_ID_RE.search(stripped)
    return match.group(0) if match else None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if value == "":
        return []
    return [str(value)]


def frontmatter_status(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    block = text[:end] if end != -1 else text
    match = STATUS_RE.search(block)
    return match.group(1).strip() if match else ""


def doc_status(slug, name):
    if not slug:
        return ""
    path = os.path.join(DOCS_DEV, slug, name)
    if not os.path.isfile(path):
        return ""
    return frontmatter_status(open(path, encoding="utf-8").read())


def spec_approved(slug):
    return doc_status(slug, "4-spec.md") == "approved"


def tasks_approved(slug):
    return doc_status(slug, "5-tasks.md") == "approved"


def evaluate_action(graph, payload):
    cursor = payload.get("cursor") or {}
    node_id = cursor.get("node")
    action = payload.get("action")
    slug = payload.get("slug") or cursor.get("slug") or ""
    if not action:
        return "error", "action JSON 缺 action"
    if not node_id:
        return "error", "action JSON 缺 cursor.node"
    spec = (graph.get("nodes") or {}).get(node_id)
    if not isinstance(spec, dict):
        return "error", f"graph.yaml 沒有節點 {node_id}"
    if action == "write_notes":
        return "deny", (
            f"{node_id} 不得 write_notes(寫 6-implementation-notes.md)—— "
            f"5-tasks 未定案不准開第 6 站"
        )
    if action == "write_tasks":
        if node_id not in TASKS_ALLOWED_NODES:
            return "deny", (
                f"{node_id} 未允許 write_tasks（寫 5-tasks.md）—— "
                f"只有 {'／'.join(TASKS_ALLOWED_NODES)} 可寫"
            )
        if not spec_approved(slug):
            return "deny", (
                f"{node_id} 未過 G2(4-spec 不是 approved)卻 write_tasks"
                f"（寫 5-tasks.md）"
            )
    allow = set(as_list(spec.get("allow")))
    forbid = set(as_list(spec.get("forbid")))
    if action in forbid:
        return "deny", f"{node_id} 禁止 {action}"
    if action in LOCKED_ACTIONS and action not in allow:
        return "deny", f"{node_id} 未允許 {action}"
    return "allow", f"{node_id} 允許 {action}"


def load_parser(path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("devstage5_parser_probe", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    # import 預設會寫 __pycache__。那份 .pyc 會落在 hooks/ 與
    # tests/parallel-stage6/ —— 正好在 test-architecture-guards 收尾比對的檔案
    # 指紋範圍內,於是這支唯讀檢查自己變成污染源(2026-08-24 CI 實證)。
    # 探測既有 parser 只要它的行為,不要它的位元碼快取。
    saved = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = saved
    return module


def drop_field(text, field):
    return "\n".join(
        line for line in text.splitlines() if not line.startswith(f"- {field}:")
    )


def check_required_fields_parser():
    """第二刀:四必填欄缺一必須紅 —— 判準是現有 parser,本檔只呼叫、不重寫。"""
    failures = []
    for rel in PARSER_PATHS:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        try:
            module = load_parser(path)
        except Exception as exc:  # noqa: BLE001 — parser 壞了就是紅,不吞
            failures.append(f"P0 既有 parser {rel} 載不起來:{exc}")
            continue
        parse = getattr(module, PARSER_FUNC, None) if module else None
        if parse is None:
            failures.append(f"P0 既有 parser {rel} 沒有 {PARSER_FUNC}()")
            continue
        try:
            baseline = parse(PROBE_TASKS).get("errors") or []
        except Exception as exc:  # noqa: BLE001
            failures.append(f"P0 {rel} {PARSER_FUNC}() 對四欄齊備的 T 就爆:{exc}")
            continue
        if baseline:
            failures.append(
                f"P0 {rel} 對四欄齊備的 T 仍報錯:{baseline} —— 判準失真"
            )
        for field in REQUIRED_FIELDS:
            try:
                errors = parse(drop_field(PROBE_TASKS, field)).get("errors") or []
            except Exception as exc:  # noqa: BLE001
                failures.append(f"P0 {rel} 缺 {field} 時 {PARSER_FUNC}() 爆掉:{exc}")
                continue
            if not any(field in str(item) for item in errors):
                failures.append(
                    f"P0 {rel} 缺必填欄 {field} 卻沒判紅 —— 四必填欄缺一必須紅"
                    f"(S4-selfcheck 的機器判準)"
                )
    return failures


def simulate_n4_rerun(write_paths, write_mode):
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="devstage5-n4-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "5-tasks.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("5-tasks*.md"))


def scan_live_tasks_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        hits = [f for f in filenames if re.fullmatch(r"5-tasks.*\.md", f)]
        if len(hits) > 1:
            rel = os.path.relpath(dirpath, root)
            failures.append(
                f"P0 {rel}/ 有 {len(hits)} 份 5-tasks*.md:{sorted(hits)}"
            )
    return failures


def scan_g2_entry_block():
    """掃 live 樹:已有 5-tasks.md 卻沒過 G2 的 slug,N1 不得當入口。"""
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for name in sorted(os.listdir(DOCS_DEV)):
        slug_dir = os.path.join(DOCS_DEV, name)
        if not os.path.isdir(slug_dir):
            continue
        if not os.path.isfile(os.path.join(slug_dir, "5-tasks.md")):
            continue
        if not spec_approved(name):
            failures.append(
                f"P0 docs/dev/{name}/ 已有 5-tasks.md 卻沒過 G2"
                f"(4-spec 不是 approved)—— N1-handoff 不是入口,退回第 4 站"
            )
    return failures


def check_chain(nodes, failures):
    for node_id, expected in EXPECTED_NEXT.items():
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        if not isinstance(spec, dict):
            if node_id == WRITE_TASKS_NODE:
                failures.append(
                    "P0 graph.yaml 缺節點 N4-write-md —— 必須有寫檔節點,"
                    "不要只做 handoff"
                )
            else:
                failures.append(f"P0 graph.yaml 缺節點 {node_id}")
            continue
        actual = spec.get("next") or ""
        if actual != expected:
            failures.append(
                f"P0 {node_id} next 必須是 {expected!r},實際是 {actual!r}"
            )


def check_live(graph):
    failures = []
    if not os.path.isfile(SKILL_PATH):
        failures.append("缺 skills/dev-flow/SKILL.md")

    nodes = graph.get("nodes") if graph else {}
    if graph is not None:
        entry = graph.get("entry")
        if entry != ENTRY_NODE:
            failures.append(
                f"graph.yaml entry 必須是 {ENTRY_NODE},實際是 {entry!r}"
            )

    for node_id in REQUIRED_NODES:
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        path = node_path(node_id, spec or {})
        rel = os.path.relpath(path, root)
        if not os.path.isfile(path):
            failures.append(
                f"P0 缺 {rel} —— 真節點缺「進條件」或「完成條件」,不能單獨當入口"
            )
            continue
        text = open(path, encoding="utf-8").read()
        sections = split_sections(text)
        for heading in REQUIRED_HEADINGS:
            body = sections.get(heading, "")
            if heading not in sections or not body.strip():
                failures.append(f"P0 {rel} 缺「{heading}」或該節為空")
        if spec is None:
            failures.append(f"P0 graph.yaml 沒有節點 {node_id}")
            continue
        expected_next = spec.get("next", "")
        if expected_next is None:
            expected_next = ""
        actual_next = first_next_id(sections.get("下一跳", ""))
        if actual_next is None:
            failures.append(f"P0 {rel} 下一跳讀不到節點 id 或「無」")
        elif actual_next != expected_next:
            failures.append(
                f"P0 {rel} 下一跳是 {actual_next!r},graph.yaml next 是 "
                f"{expected_next!r}"
            )
        write_body = sections.get("寫哪裡", "")
        for line in write_body.splitlines():
            if BAD_TASKS_RE.search(line) and not re.search(r"禁止|不得|禁", line):
                failures.append(
                    f"P0 {rel} 寫哪裡把非正本 5-tasks*.md 當寫入目標"
                )
                break
        do_body = sections.get("做什麼", "")
        token = f"--write-cursor {node_id}"
        if token not in do_body:
            failures.append(f"P0 {rel} 做什麼必須呼叫 --write-cursor {node_id}")
        if node_id == SELFCHECK_NODE and (
            PARSER_REF not in do_body or PARSER_FUNC not in do_body
        ):
            failures.append(
                f"P0 {rel} 做什麼必須呼叫既有 {PARSER_REF} 的 {PARSER_FUNC}"
                f"(四必填欄的機器判準,不改那支 parser)"
            )
        if node_id == WRITE_TASKS_NODE:
            if "5-tasks.md" not in write_body:
                failures.append(f"P0 {rel} 寫哪裡必須點名 5-tasks.md")
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"5-tasks\*\.md|第二份", write_body):
                if not re.search(r"禁止|不得|禁", write_body):
                    failures.append(f"P0 {rel} 必須禁止第二份 5-tasks*.md")

    if graph is None:
        failures.append(
            "P0 舊實作缺 N4-write-md —— 必須有寫檔節點,不要只做 handoff"
        )
        failures.append(
            "P0 舊實作把乘客步 1／2／3／4 留在單一 SKILL —— 必須是真節點檔,"
            "不是 skill-legacy 團塊"
        )
        failures.append(
            "P0 舊實作無法證明同 slug 第二份 5-tasks*.md 會被擋"
        )
        failures.append(
            "P0 舊實作沒有 N4 覆寫契約,無法證明 write_mode≠overwrite 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明未過 G2(4-spec 不是 approved)卻 write_tasks"
            "（寫 5-tasks.md）會被擋"
        )
        failures.append(
            "P0 舊實作無法證明 5-tasks 未定案卻寫 6-implementation-notes.md"
            "(write_notes)會被擋"
        )
        failures.extend(scan_live_tasks_dupes())
        failures.extend(scan_g2_entry_block())
        failures.extend(check_required_fields_parser())
        return failures

    for node_id in TASKS_ALLOWED_NODES:
        spec = nodes.get(node_id)
        if not isinstance(spec, dict):
            continue
        write_paths = as_list(spec.get("write"))
        write_mode = spec.get("write_mode") or ""
        if write_paths != [CANONICAL_MD]:
            failures.append(
                f"P0 graph.yaml {node_id} write 必須剛好是 {[CANONICAL_MD]},"
                f"實際是 {write_paths}"
            )
        if write_mode != "overwrite":
            failures.append(
                f"P0 graph.yaml {node_id} write_mode 必須是 overwrite,"
                f"實際是 {write_mode!r}"
            )
        found = simulate_n4_rerun(write_paths or [CANONICAL_MD], write_mode)
        if found != ["5-tasks.md"]:
            failures.append(
                f"P0 模擬重跑 {node_id} 後 5-tasks*.md = {found},必須只剩正本一份"
            )

    for node_id, spec in nodes.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("via"):
            failures.append(
                f"P0 {node_id} 用 via 當 hop,必須是 next 指到的真節點"
            )
        if spec.get("kind") == "skill-legacy":
            failures.append(
                f"P0 {node_id} 仍是 skill-legacy 團塊,必須拆成有節點檔的 hop"
            )
        allow = set(as_list(spec.get("allow")))
        if node_id in TASKS_ALLOWED_NODES:
            if "write_tasks" not in allow:
                failures.append(
                    f"P0 {node_id} 必須 allow write_tasks"
                    "(同一份 5-tasks.md,overwrite)"
                )
        elif "write_tasks" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_tasks")
        if node_id in TASKS_FORBIDDEN_NODES and "write_tasks" in allow:
            failures.append(f"P0 {node_id} 不得放寬 write_tasks")
        if "write_notes" in allow:
            failures.append(
                f"P0 {node_id} 不得 allow write_notes —— "
                f"5-tasks 未定案不准寫 6-implementation-notes.md"
            )

    unknown = [n for n in nodes if n not in CHAIN]
    if unknown:
        failures.append(
            f"P0 graph.yaml 有鏈外節點:{sorted(unknown)} —— 鏈必須剛好是 "
            + " → ".join(CHAIN)
        )
    check_chain(nodes, failures)
    failures.extend(scan_live_tasks_dupes())
    failures.extend(scan_g2_entry_block())
    failures.extend(check_required_fields_parser())
    failures.extend(check_action_runtime_wired())
    failures.extend(check_guide())
    return failures


def check_action_runtime_wired():
    """第三刀:--action 必須接到 prebash,不能只活在 test fixture。"""
    hooks = os.path.join(root, "hooks")
    if not os.path.isdir(hooks):
        return []
    for dirpath, dirnames, filenames in os.walk(hooks):
        dirnames[:] = [d for d in dirnames if d != "devflow_obs_vendor"]
        for name in filenames:
            if not name.endswith((".py", ".sh")):
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8").read()
            except OSError:
                continue
            code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
            if "check-devstage5-graph" in code and "--action" in code:
                return []
    return [
        "P0 --action 沒接到 runtime:hooks 沒有呼叫 check-devstage5-graph.sh --action"
    ]


def check_guide():
    """第 5 站開頭對上八節點鏈;舊句「還在單一 SKILL」必須紅。"""
    if not os.path.isfile(GUIDE_PATH):
        return ["P0 指南檔缺席:找不到 guides/guide-dev-flow.html"]
    text = open(GUIDE_PATH, encoding="utf-8").read()
    failures = []
    if STALE_GUIDE in text:
        failures.append(f"P0 guide 出現「{STALE_GUIDE}」")
    match = re.search(r'<h3 id="stage5">.*?(?=<h3 |\Z)', text, re.S)
    if not match:
        failures.append('P0 guide 找不到第 5 站 <h3 id="stage5">')
        return failures
    head = match.group(0)[:2500]
    missing = [node_id for node_id in CHAIN if node_id not in head]
    if missing:
        failures.append("P0 guide 第 5 站開頭缺節點:" + ",".join(missing))
    return failures


graph, graph_fail = load_graph()
if action_file:
    if graph is None:
        print(
            "error\t" + (graph_fail[0] if graph_fail else "缺 graph.yaml"),
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        payload = json.load(open(action_file, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FATAL: 讀不了 action JSON:{exc}", file=sys.stderr)
        sys.exit(2)
    verdict, reason = evaluate_action(graph, payload)
    print(f"{verdict}\t{reason}")
    if verdict == "error":
        sys.exit(2)
    sys.exit(0 if verdict == "allow" else 1)

failures = []
failures.extend(graph_fail)
failures.extend(check_live(graph))

print(f"[graph] nodes_required={len(REQUIRED_NODES)} failures={len(failures)}")
if failures:
    print(f"❌ FAIL:{len(failures)} 項", file=sys.stderr)
    for item in failures:
        print(f"  - {item}", file=sys.stderr)
    sys.exit(1)

print(
    "✅ PASS:Stage 5 graph 八真節點 / 無 skill-legacy 團塊 / 單產物 / 覆寫 / "
    "四必填欄缺一即紅 / G2 前不搶跑 / 未定案不寫 6-notes / prebash / guide 全過"
)
sys.exit(0)
PY
