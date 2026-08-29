#!/bin/bash
# check-devstage4-graph.sh — Stage 4 第三刀的機械契約
#
# 為什麼需要:把第 4 站切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   1. 沒有 stage4/graph.yaml 必須紅:舊實作(單一 SKILL、沒有 graph)無法證明
#      下一跳與重跑契約。
#   2. 真節點缺「進條件」或「完成條件」必須紅:節點不能單獨當入口。
#   3. 同 slug 第二份 4-spec*.md 必須紅:產物仍是一份。
#   4. write_mode≠overwrite 必須紅:重跑寫檔節點覆寫同一檔,不另存。
#   5. 缺 N5-write-md 必須紅:必須有寫檔節點,不要只做 handoff。
#   6. 未過 G1(2-decision 不是 approved)卻 write_spec(寫 4-spec.md)必須紅:
#      第 2 站還沒核准不准搶跑第 4 站。
#   7. G2 前寫 5-tasks.md(write_tasks)必須紅:第 5 站還沒開始。
#   8. 第二刀:乘客步 1／2／3a-c／4／5 必須是真節點檔。kind: skill-legacy 團塊
#      必須紅 —— 第一刀的暫留 hop 到這一刀就沒有存在理由了。
#      每個真節點「做什麼」必須 --write-cursor <本節點 id>。
#      S1–S5 與 N5-write-md 才 allow write_spec(同一份 4-spec.md,overwrite);
#      不要放寬 N1-handoff／N6-g2／N7-end。S5-gate 只呼叫既有
#      scripts/check-spec-gate.sh,不改那支腳本。
#   9. 第三刀:--action 必須接到 prebash,不能只活在 test fixture。guide 第 4 站
#      開頭必須對上十一節點鏈。出現「Stage 4 還在單一 SKILL」必須紅。
#      不改第 1／2／3 站的編成。
#
# graph.yaml 是下一跳的唯一正本。分叉與暫留一律用 next 指到的真節點,禁止 via
# (第 1 站 0030 的假綠就是 via 字串當 hop 換來的)。
# 本機游標 .devstage4-cursor.json 不進 Git。
# 不改 check-devtalk-graph.sh / check-devstage2-graph.sh / check-devstage3-graph.sh。
# 不改 _templates/4-spec.md 正文(乘客清單正本是它的頂註 0–6)。
# 不改 scripts/check-spec-gate.sh / scripts/build-gate-twin.py(呼叫即可)。
#
# 用法:
#   scripts/check-devstage4-graph.sh [root]
#   scripts/check-devstage4-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node,slug},action,slug?}
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devstage4-graph.sh --write-cursor NODE [SLUG] [root]
#       把 .devstage4-cursor.json 寫成 {node, slug}。不改 .dev-flow。
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
    dest = os.path.join(root, ".devstage4-cursor.json")
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

STAGE4 = os.path.join(root, "skills", "dev-flow", "stage4")
GRAPH_PATH = os.path.join(STAGE4, "graph.yaml")
SKILL_PATH = os.path.join(root, "skills", "dev-flow", "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")

ENTRY_NODE = "N1-handoff"
WRITE_SPEC_NODE = "N5-write-md"
GATE_NODE = "S5-gate"
GATE_SCRIPT = "check-spec-gate.sh"
# 晚改可見行為鎖:完成條件必須含這些句,缺了 = 圖牙紅。
DONE_NEEDLES = {
    "N1-handoff": ("晚改可見行為", "禁只改 4-spec"),
    "S4-dd": ("推翻已核 Decision 不是合法 DD",),
}
# 第二刀:十一個真節點檔,沒有 skill-legacy 團塊。
CHAIN = (
    "N1-handoff",
    "S1-requirements",
    "S2-scenarios",
    "S3a-close",
    "S3b-profile",
    "S3c-stage3",
    "S4-dd",
    "N5-write-md",
    "S5-gate",
    "N6-g2",
    "N7-end",
)
REQUIRED_NODES = CHAIN
EXPECTED_NEXT = {
    "N1-handoff": "S1-requirements",
    "S1-requirements": "S2-scenarios",
    "S2-scenarios": "S3a-close",
    "S3a-close": "S3b-profile",
    "S3b-profile": "S3c-stage3",
    "S3c-stage3": "S4-dd",
    "S4-dd": "N5-write-md",
    "N5-write-md": "S5-gate",
    "S5-gate": "N6-g2",
    "N6-g2": "N7-end",
    "N7-end": "",
}
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
CANONICAL_MD = "docs/dev/<slug>/4-spec.md"
LOCKED_ACTIONS = ("write_spec", "write_tasks")
# 乘客步 1／2／3a-c／4／5 與定稿節點共寫同一份 4-spec.md(overwrite)。
# write_tasks 本刀任何節點都不得 allow。
SPEC_ALLOWED_NODES = (
    "S1-requirements",
    "S2-scenarios",
    "S3a-close",
    "S3b-profile",
    "S3c-stage3",
    "S4-dd",
    "N5-write-md",
    "S5-gate",
)
SPEC_FORBIDDEN_NODES = ("N1-handoff", "N6-g2", "N7-end")
GUIDE_PATH = os.path.join(root, "guides", "guide-dev-flow.html")
STALE_GUIDE = "Stage 4 還在單一 SKILL"

NEXT_ID_RE = re.compile(
    r"(?:S\d+[a-z]?-[A-Za-z0-9-]+|N(?:\d+)?-[A-Za-z0-9-]+|skill-legacy-\d+(?:-\d+)?)"
)
BAD_SPEC_RE = re.compile(r"4-spec(?:-[A-Za-z0-9]+)+\.md")
STATUS_RE = re.compile(r"^status:\s*(\S+)", re.M)
CHECKBOX_RE = re.compile(r"^[-*]\s+\[(.)\]", re.M)


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
            "缺 skills/dev-flow/stage4/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
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
    return os.path.join(STAGE4, rel.replace("/", os.sep))


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


def decision_approved(slug):
    return doc_status(slug, "2-decision.md") == "approved"


def trigger_hit_count(text):
    """第 3 站觸發判定的命中數。條文正本在 _templates/3-prototype.md,本檔不重抄。"""
    body = ""
    for key, section in split_sections(text).items():
        if "觸發判定" in key:
            body = section
            break
    return sum(1 for mark in CHECKBOX_RE.findall(body) if mark == "x")


def stage3_hits(slug):
    if not slug:
        return False
    path = os.path.join(DOCS_DEV, slug, "3-prototype.md")
    if not os.path.isfile(path):
        return False
    return trigger_hit_count(open(path, encoding="utf-8").read()) > 0


def stage3_approved(slug):
    return doc_status(slug, "3-prototype.md") == "approved"


def has_skip_oc(slug):
    """2-decision 同一行同時寫 Stage 3 與「跳過」= owner 明記的跳過 OC。"""
    if not slug:
        return False
    path = os.path.join(DOCS_DEV, slug, "2-decision.md")
    if not os.path.isfile(path):
        return False
    for line in open(path, encoding="utf-8"):
        if "Stage 3" in line and "跳過" in line:
            return True
    return False


def stage3_blocks_entry(slug):
    """第 3 站必要(有命中)卻缺 approved、又無 skip OC → N1 不是入口。"""
    return stage3_hits(slug) and not stage3_approved(slug) and not has_skip_oc(slug)


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
    if action == "write_tasks":
        return "deny", (
            f"{node_id} 不得 write_tasks(寫 5-tasks.md)—— G2 前不准開第 5 站"
        )
    if action == "write_spec":
        if node_id not in SPEC_ALLOWED_NODES:
            return "deny", (
                f"{node_id} 未允許 write_spec（寫 4-spec.md）—— "
                f"只有 {'／'.join(SPEC_ALLOWED_NODES)} 可寫"
            )
        if not decision_approved(slug):
            return "deny", (
                f"{node_id} 未過 G1(2-decision 不是 approved)卻 write_spec"
                f"（寫 4-spec.md）"
            )
        if stage3_blocks_entry(slug):
            return "deny", (
                f"{node_id} 第 3 站必要卻缺 approved 的 3-prototype、又無 skip OC,"
                f"不得 write_spec（寫 4-spec.md）"
            )
    allow = set(as_list(spec.get("allow")))
    forbid = set(as_list(spec.get("forbid")))
    if action in forbid:
        return "deny", f"{node_id} 禁止 {action}"
    if action in LOCKED_ACTIONS and action not in allow:
        return "deny", f"{node_id} 未允許 {action}"
    return "allow", f"{node_id} 允許 {action}"


def simulate_write_rerun(write_paths, write_mode):
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="devstage4-n5-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "4-spec.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("4-spec*.md"))


def scan_live_spec_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        hits = [f for f in filenames if re.fullmatch(r"4-spec.*\.md", f)]
        if len(hits) > 1:
            rel = os.path.relpath(dirpath, root)
            failures.append(
                f"P0 {rel}/ 有 {len(hits)} 份 4-spec*.md:{sorted(hits)}"
            )
    return failures


def scan_stage3_entry_block():
    """掃 live 樹:第 3 站必要卻沒收尾的 slug,N1 不得當入口。"""
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for name in sorted(os.listdir(DOCS_DEV)):
        slug_dir = os.path.join(DOCS_DEV, name)
        if not os.path.isdir(slug_dir):
            continue
        if stage3_blocks_entry(name):
            failures.append(
                f"P0 docs/dev/{name}/ 第 3 站必要(3-prototype 有命中)卻缺 approved、"
                f"又無 skip OC —— N1-handoff 不是入口,退回第 3 站"
            )
    return failures


def check_chain(nodes, failures):
    for node_id, expected in EXPECTED_NEXT.items():
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        if not isinstance(spec, dict):
            if node_id == WRITE_SPEC_NODE:
                failures.append(
                    "P0 graph.yaml 缺節點 N5-write-md —— 必須有寫檔節點,"
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
        done_body = sections.get("完成條件", "")
        for needle in DONE_NEEDLES.get(node_id, ()):
            if needle not in done_body:
                failures.append(f"P0 {rel} 完成條件必須含「{needle}」")
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
            if BAD_SPEC_RE.search(line) and not re.search(r"禁止|不得|禁", line):
                failures.append(
                    f"P0 {rel} 寫哪裡把非正本 4-spec*.md 當寫入目標"
                )
                break
        do_body = sections.get("做什麼", "")
        token = f"--write-cursor {node_id}"
        if token not in do_body:
            failures.append(f"P0 {rel} 做什麼必須呼叫 --write-cursor {node_id}")
        if node_id == GATE_NODE and GATE_SCRIPT not in do_body:
            failures.append(
                f"P0 {rel} 做什麼必須呼叫既有 {GATE_SCRIPT}(步 5 機械關卡,不改那支腳本)"
            )
        if node_id == WRITE_SPEC_NODE:
            if "4-spec.md" not in write_body:
                failures.append(f"P0 {rel} 寫哪裡必須點名 4-spec.md")
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"4-spec\*\.md|第二份", write_body):
                if not re.search(r"禁止|不得|禁", write_body):
                    failures.append(f"P0 {rel} 必須禁止第二份 4-spec*.md")

    if graph is None:
        failures.append(
            "P0 舊實作缺 N5-write-md —— 必須有寫檔節點,不要只做 handoff"
        )
        failures.append(
            "P0 舊實作無法證明同 slug 第二份 4-spec*.md 會被擋"
        )
        failures.append(
            "P0 舊實作沒有 N5 覆寫契約,無法證明 write_mode≠overwrite 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明未過 G1(2-decision 不是 approved)卻 write_spec"
            "（寫 4-spec.md）會被擋"
        )
        failures.append(
            "P0 舊實作無法證明 G2 前寫 5-tasks.md(write_tasks)會被擋"
        )
        failures.extend(scan_live_spec_dupes())
        failures.extend(scan_stage3_entry_block())
        return failures

    for node_id in SPEC_ALLOWED_NODES:
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
        found = simulate_write_rerun(write_paths or [CANONICAL_MD], write_mode)
        if found != ["4-spec.md"]:
            failures.append(
                f"P0 模擬重跑 {node_id} 後 4-spec*.md = {found},必須只剩正本一份"
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
        if node_id in SPEC_ALLOWED_NODES:
            if "write_spec" not in allow:
                failures.append(
                    f"P0 {node_id} 必須 allow write_spec"
                    "(同一份 4-spec.md,overwrite)"
                )
        elif "write_spec" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_spec")
        if node_id in SPEC_FORBIDDEN_NODES and "write_spec" in allow:
            failures.append(f"P0 {node_id} 不得放寬 write_spec")
        if "write_tasks" in allow:
            failures.append(
                f"P0 {node_id} 不得 allow write_tasks —— G2 前不准寫 5-tasks.md"
            )

    unknown = [n for n in nodes if n not in CHAIN]
    if unknown:
        failures.append(
            f"P0 graph.yaml 有鏈外節點:{sorted(unknown)} —— 鏈必須剛好是 "
            + " → ".join(CHAIN)
        )
    check_chain(nodes, failures)
    failures.extend(scan_live_spec_dupes())
    failures.extend(scan_stage3_entry_block())
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
            if "check-devstage4-graph" in code and "--action" in code:
                return []
    return [
        "P0 --action 沒接到 runtime:hooks 沒有呼叫 check-devstage4-graph.sh --action"
    ]


def check_guide():
    """第 4 站開頭對上十一節點鏈;舊句「還在單一 SKILL」必須紅。"""
    if not os.path.isfile(GUIDE_PATH):
        return []
    text = open(GUIDE_PATH, encoding="utf-8").read()
    failures = []
    if STALE_GUIDE in text:
        failures.append(f"P0 guide 出現「{STALE_GUIDE}」")
    match = re.search(r'<h3 id="stage4">.*?(?=<h3 |\Z)', text, re.S)
    if not match:
        failures.append('P0 guide 找不到第 4 站 <h3 id="stage4">')
        return failures
    head = match.group(0)[:2500]
    missing = [node_id for node_id in CHAIN if node_id not in head]
    if missing:
        failures.append("P0 guide 第 4 站開頭缺節點:" + ",".join(missing))
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
    "✅ PASS:Stage 4 graph 十一真節點 / 無 skill-legacy 團塊 / 單產物 / 覆寫 / "
    "G1 前不搶跑 / G2 前不寫 5-tasks / prebash / guide 全過"
)
sys.exit(0)
PY
