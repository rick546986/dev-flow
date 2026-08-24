#!/bin/bash
# check-devstage6-graph.sh — Stage 6 第二刀的機械契約
#
# 為什麼需要:把第 6 站切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   1. 沒有 stage6/graph.yaml 必須紅:舊實作(單一 SKILL、沒有 graph)無法證明
#      下一跳與重跑契約。
#   2. 真節點缺「進條件」或「完成條件」必須紅:節點不能單獨當入口。
#   3. 同 slug 第二份 6-implementation-notes*.md 必須紅:產物仍是一份。
#   4. write_mode≠overwrite 必須紅:重跑 N1-arm／S2-tdd 覆寫同一檔,不另存。
#   5. 缺 N1-arm 必須紅:必須有寫檔節點,不要只做 handoff。
#   6. 5-tasks 不是 approved 卻 write_notes(寫 6-implementation-notes.md)必須紅:
#      第 5 站還沒定案不准搶跑第 6 站。
#   7. 沒武裝卻 write_notes 必須紅;6-notes 已落檔卻 FORK_INTEGRATION_SHA 缺或
#      被改寫必須紅。錨點一旦寫入不准更新。N1-arm 是落錨點的那一筆;
#      S2-tdd 寫 TDD 證據之前必須已經武裝。
#   8. 第二刀:乘客步 2(逐 T)必須是真節點檔 S2-tdd。kind: skill-legacy 團塊
#      必須紅 —— 第一刀的暫留 hop 到這一刀就沒有存在理由了。
#      每個真節點「做什麼」必須 --write-cursor <本節點 id>。
#      N1-arm 與 S2-tdd 才 allow write_notes(同一份 6-implementation-notes.md,
#      overwrite);不要放寬 N2-handoff／N4-selfcheck／N5-end。
#      S2-tdd 是一顆 hop,不是一 T 一 hop —— 逐 T 仍走 README §5 動線 / 引擎。
#      做什麼必須點名 README §5,且寫明「不是一 T 一 hop」。
#
# graph.yaml 是下一跳的唯一正本。分叉與暫留一律用 next 指到的真節點,禁止 via
# (第 1 站 0030 的假綠就是 via 字串當 hop 換來的)。
# 本機游標 .devstage6-cursor.json 不進 Git。
# 不改 check-devtalk-graph.sh / check-devstage2-graph.sh / check-devstage3-graph.sh /
# check-devstage4-graph.sh / check-devstage5-graph.sh。
# 不改 _templates/6-implementation-notes.md 正文(乘客清單正本是它的頂註 0–4)。
# 不改 hooks/devflow-exec.sh、hooks/_guard_impl.py、Gauntlet、平行引擎。
# 圍欄②一個字不改鬆。
# 本刀不掃 prebash、不掃 guide #stage6 節點鏈 —— 那是第三刀。
#
# 用法:
#   scripts/check-devstage6-graph.sh [root]
#   scripts/check-devstage6-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node,slug},action,slug?}
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devstage6-graph.sh --write-cursor NODE [SLUG] [root]
#       把 .devstage6-cursor.json 寫成 {node, slug}。不改 .dev-flow。
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
    dest = os.path.join(root, ".devstage6-cursor.json")
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

STAGE6 = os.path.join(root, "skills", "dev-flow", "stage6")
GRAPH_PATH = os.path.join(STAGE6, "graph.yaml")
SKILL_PATH = os.path.join(root, "skills", "dev-flow", "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")

ENTRY_NODE = "N1-arm"
WRITE_NOTES_NODE = "N1-arm"
TDD_NODE = "S2-tdd"
# 第二刀:五個真節點檔,沒有 skill-legacy 團塊。逐 T 仍是一顆 hop。
CHAIN = (
    "N1-arm",
    "N2-handoff",
    "S2-tdd",
    "N4-selfcheck",
    "N5-end",
)
REQUIRED_NODES = CHAIN
EXPECTED_NEXT = {
    "N1-arm": "N2-handoff",
    "N2-handoff": "S2-tdd",
    "S2-tdd": "N4-selfcheck",
    "N4-selfcheck": "N5-end",
    "N5-end": "",
}
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
CANONICAL_MD = "docs/dev/<slug>/6-implementation-notes.md"
LOCKED_ACTIONS = ("write_notes",)
# 落錨點(N1)與逐 T 證據(S2)共寫同一份 6-notes(overwrite)。
# N2／N4／N5 不放寬。
NOTES_ALLOWED_NODES = (
    "N1-arm",
    "S2-tdd",
)
NOTES_FORBIDDEN_NODES = ("N2-handoff", "N4-selfcheck", "N5-end")
PER_T_HOP_RE = re.compile(r"^T-?\d+$")
STAGE_KEY = "6-implementation"
SHA_LINE_RE = re.compile(
    r"^FORK_INTEGRATION_SHA:\s*([0-9a-f]{40})\s*$", re.M
)
SHA_ANY_RE = re.compile(r"^FORK_INTEGRATION_SHA:\s*(\S*)", re.M)

NEXT_ID_RE = re.compile(
    r"(?:S\d+-[A-Za-z0-9-]+|N(?:\d+)?-[A-Za-z0-9-]+|skill-legacy-[A-Za-z0-9-]+)"
)
BAD_NOTES_RE = re.compile(r"6-implementation-notes(?:-[A-Za-z0-9]+)+\.md")
STATUS_RE = re.compile(r"^status:\s*(\S+)", re.M)
STAGE_RE = re.compile(r"^stage:\s*(\S+)", re.M)


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
            "缺 skills/dev-flow/stage6/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
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
    return os.path.join(STAGE6, rel.replace("/", os.sep))


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


def frontmatter_block(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[:end] if end != -1 else text


def frontmatter_status(text):
    match = STATUS_RE.search(frontmatter_block(text))
    return match.group(1).strip() if match else ""


def frontmatter_stage(text):
    match = STAGE_RE.search(frontmatter_block(text))
    return match.group(1).strip() if match else ""


def doc_status(slug, name):
    if not slug:
        return ""
    path = os.path.join(DOCS_DEV, slug, name)
    if not os.path.isfile(path):
        return ""
    return frontmatter_status(open(path, encoding="utf-8").read())


def tasks_approved(slug):
    return doc_status(slug, "5-tasks.md") == "approved"


def notes_text(slug):
    if not slug:
        return ""
    path = os.path.join(DOCS_DEV, slug, "6-implementation-notes.md")
    if not os.path.isfile(path):
        return ""
    return open(path, encoding="utf-8").read()


def is_armed(slug):
    return bool(SHA_LINE_RE.search(notes_text(slug)))


def is_graph_notes(text):
    return frontmatter_stage(text) == STAGE_KEY


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
        if node_id not in NOTES_ALLOWED_NODES:
            return "deny", (
                f"{node_id} 未允許 write_notes(寫 6-implementation-notes.md)—— "
                f"只有 {'／'.join(NOTES_ALLOWED_NODES)} 可寫"
            )
        if not tasks_approved(slug):
            return "deny", (
                f"{node_id} 5-tasks 不是 approved 卻 write_notes"
                f"(寫 6-implementation-notes.md)—— 退回第 5 站"
            )
        if node_id != WRITE_NOTES_NODE and not is_armed(slug):
            return "deny", (
                f"{node_id} 沒武裝不得 write_notes(寫 6-implementation-notes.md)"
                f"—— 缺 FORK_INTEGRATION_SHA,退回 {WRITE_NOTES_NODE}"
            )
    allow = set(as_list(spec.get("allow")))
    forbid = set(as_list(spec.get("forbid")))
    if action in forbid:
        return "deny", f"{node_id} 禁止 {action}"
    if action in LOCKED_ACTIONS and action not in allow:
        return "deny", f"{node_id} 未允許 {action}"
    return "allow", f"{node_id} 允許 {action}"


def simulate_notes_rerun(write_paths, write_mode):
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="devstage6-notes-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "6-implementation-notes.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("6-implementation-notes*.md"))


def scan_live_notes_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        hits = [
            f for f in filenames if re.fullmatch(r"6-implementation-notes.*\.md", f)
        ]
        if len(hits) > 1:
            rel = os.path.relpath(dirpath, root)
            failures.append(
                f"P0 {rel}/ 有 {len(hits)} 份 6-implementation-notes*.md:{sorted(hits)}"
            )
    return failures


def scan_tasks_entry_block():
    """已有 graph 契約下的 6-notes,卻 5-tasks 不是 approved → N1-arm 不是入口。"""
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for name in sorted(os.listdir(DOCS_DEV)):
        slug_dir = os.path.join(DOCS_DEV, name)
        if not os.path.isdir(slug_dir):
            continue
        notes = os.path.join(slug_dir, "6-implementation-notes.md")
        if not os.path.isfile(notes):
            continue
        text = open(notes, encoding="utf-8").read()
        if not is_graph_notes(text):
            continue
        if not tasks_approved(name):
            failures.append(
                f"P0 docs/dev/{name}/ 已有 6-implementation-notes.md 卻 5-tasks "
                f"不是 approved—— N1-arm 不是入口,退回第 5 站"
            )
    return failures


def scan_sha():
    """只審 stage: 6-implementation 的 6-notes(新 graph 產物)。
    歷史 docs/dev 案例的 stage 鍵是 6-implementation-notes,不在本契約範圍。
    """
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for name in sorted(os.listdir(DOCS_DEV)):
        slug_dir = os.path.join(DOCS_DEV, name)
        if not os.path.isdir(slug_dir):
            continue
        notes = os.path.join(slug_dir, "6-implementation-notes.md")
        if not os.path.isfile(notes):
            continue
        text = open(notes, encoding="utf-8").read()
        if not is_graph_notes(text):
            continue
        valid = SHA_LINE_RE.findall(text)
        any_vals = SHA_ANY_RE.findall(text)
        if not any_vals:
            failures.append(
                f"P0 docs/dev/{name}/6-implementation-notes.md 缺 FORK_INTEGRATION_SHA"
                f"(40 碼)—— 沒武裝不准開工"
            )
            continue
        bad = [v for v in any_vals if not re.fullmatch(r"[0-9a-f]{40}", v)]
        if bad:
            failures.append(
                f"P0 docs/dev/{name}/6-implementation-notes.md FORK_INTEGRATION_SHA "
                f"不是 40 碼小寫 hex:{bad}"
            )
        unique = list(dict.fromkeys(valid))
        if len(unique) > 1:
            failures.append(
                f"P0 docs/dev/{name}/6-implementation-notes.md FORK_INTEGRATION_SHA "
                f"被改寫:{unique} —— 寫了不准改"
            )
    return failures


def check_chain(nodes, failures):
    for node_id, expected in EXPECTED_NEXT.items():
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        if not isinstance(spec, dict):
            if node_id == WRITE_NOTES_NODE:
                failures.append(
                    "P0 graph.yaml 缺節點 N1-arm —— 必須有寫檔節點,"
                    "不要只做 handoff"
                )
            elif node_id == TDD_NODE:
                failures.append(
                    "P0 graph.yaml 缺節點 S2-tdd —— 第二刀必須把 "
                    "skill-legacy-T 拆成真節點,逐 T 不是一 T 一 hop"
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
            if BAD_NOTES_RE.search(line) and not re.search(r"禁止|不得|禁", line):
                failures.append(
                    f"P0 {rel} 寫哪裡把非正本 6-implementation-notes*.md 當寫入目標"
                )
                break
        do_body = sections.get("做什麼", "")
        token = f"--write-cursor {node_id}"
        if token not in do_body:
            failures.append(f"P0 {rel} 做什麼必須呼叫 --write-cursor {node_id}")
        if node_id == TDD_NODE:
            if "README §5" not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須點名 README §5"
                    "(逐 T 動線正本,不抄原文、不另寫引擎)"
                )
            if "不是一 T 一 hop" not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須寫明「不是一 T 一 hop」"
                    "—— 逐 T 仍走現有引擎,不准每個 T 一顆 hop"
                )
        if node_id in NOTES_ALLOWED_NODES:
            if "6-implementation-notes.md" not in write_body:
                failures.append(
                    f"P0 {rel} 寫哪裡必須點名 6-implementation-notes.md"
                )
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"6-implementation-notes\*\.md|第二份", write_body):
                if not re.search(r"禁止|不得|禁", write_body):
                    failures.append(
                        f"P0 {rel} 必須禁止第二份 6-implementation-notes*.md"
                    )
        if node_id == WRITE_NOTES_NODE:
            if "FORK_INTEGRATION_SHA" not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須點名 FORK_INTEGRATION_SHA(40 碼錨點)"
                )

    if graph is None:
        failures.append(
            "P0 舊實作缺 N1-arm —— 第一刀必須有寫檔節點,不要只做 handoff"
        )
        failures.append(
            "P0 舊實作把乘客步 2(逐 T)留在單一 SKILL —— 必須是真節點檔 S2-tdd,"
            "不是 skill-legacy 團塊;逐 T 不是一 T 一 hop"
        )
        failures.append(
            "P0 舊實作無法證明同 slug 第二份 6-implementation-notes*.md 會被擋"
        )
        failures.append(
            "P0 舊實作沒有 N1 覆寫契約,無法證明 write_mode≠overwrite 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明 5-tasks 不是 approved 卻 write_notes"
            "(寫 6-implementation-notes.md)會被擋"
        )
        failures.append(
            "P0 舊實作無法證明沒武裝寫 6-implementation-notes.md 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明 FORK_INTEGRATION_SHA 缺或被改寫會被擋"
        )
        failures.extend(scan_live_notes_dupes())
        return failures

    for node_id in NOTES_ALLOWED_NODES:
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
        found = simulate_notes_rerun(write_paths or [CANONICAL_MD], write_mode)
        if found != ["6-implementation-notes.md"]:
            failures.append(
                f"P0 模擬重跑 {node_id} 後 6-implementation-notes*.md = {found},"
                f"必須只剩正本一份"
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
        if PER_T_HOP_RE.match(str(node_id)):
            failures.append(
                f"P0 {node_id} 是一 T 一 hop,逐 T 必須仍走 README §5 動線 / "
                f"引擎,不准每個 T 一顆 hop"
            )
        allow = set(as_list(spec.get("allow")))
        if node_id in NOTES_ALLOWED_NODES:
            if "write_notes" not in allow:
                failures.append(
                    f"P0 {node_id} 必須 allow write_notes"
                    "(同一份 6-implementation-notes.md,overwrite)"
                )
        elif "write_notes" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_notes")
        if node_id in NOTES_FORBIDDEN_NODES and "write_notes" in allow:
            failures.append(f"P0 {node_id} 不得放寬 write_notes")

    unknown = [n for n in nodes if n not in CHAIN]
    if unknown:
        failures.append(
            f"P0 graph.yaml 有鏈外節點:{sorted(unknown)} —— 鏈必須剛好是 "
            + " → ".join(CHAIN)
        )
    check_chain(nodes, failures)
    failures.extend(scan_live_notes_dupes())
    failures.extend(scan_tasks_entry_block())
    failures.extend(scan_sha())
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
    "✅ PASS:Stage 6 graph 五真節點 / 無 skill-legacy / 單產物 / 覆寫 / "
    "未定案不寫 6-notes / 沒武裝不寫 / SHA 錨點 / 逐 T 不是一 T 一 hop 全過"
)
sys.exit(0)
PY
