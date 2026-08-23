#!/bin/bash
# check-devstage3-graph.sh — Stage 3 第二刀的機械契約
#
# 為什麼需要:把第 3 站切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   1. 沒有 stage3/graph.yaml 必須紅:舊實作(單一 SKILL、沒有 graph)無法證明
#      下一跳、分叉與重跑契約。
#   2. 真節點缺「進條件」或「完成條件」必須紅:節點不能單獨當入口。
#   3. 同 slug 第二份 3-prototype*.md 必須紅:產物仍是一份。
#   4. write_mode≠overwrite 必須紅:重跑 N3 覆寫同一檔,不另存。
#   5. 九條觸發全未命中,卻存在 3-prototype.md 必須紅:0 命中走 N-skip,不准建檔。
#   6. 有命中、無 skip OC、游標不在第 3 站允許節點,卻 write_spec(寫 4-spec.md)
#      必須紅:第 3 站還沒結束不准搶跑第 4 站。
#      --action 先只活在本腳本;prebash 第三刀再接。
#   7. 第二刀:legacy 0／1／2／3／4 必須是真節點檔。skill-legacy 團塊必須紅。
#      每個真節點「做什麼」必須 --write-cursor <本節點 id>。
#      fork_required 必須是 S0-question。S3-writeback 才 allow write_decision
#      (同一份 2-decision.md,overwrite)。不要放寬 N1／N-skip／S0／S1／S2／N3／N5。
#
# graph.yaml 是下一跳的唯一正本。分叉用 next + fork_required,禁止 via。
# 本機游標 .devstage3-cursor.json 不進 Git。
# 不改 check-devtalk-graph.sh / check-devstage2-graph.sh。
# 不改 _templates/3-prototype.md 正文。本刀不掃 prebash、不掃 guide #stage3。
#
# 用法:
#   scripts/check-devstage3-graph.sh [root]
#   scripts/check-devstage3-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node},action,slug?}
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devstage3-graph.sh --write-cursor NODE [SLUG] [root]
#       把 .devstage3-cursor.json 寫成 {node, slug}。不改 .dev-flow。
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
    dest = os.path.join(root, ".devstage3-cursor.json")
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

STAGE3 = os.path.join(root, "skills", "dev-flow", "stage3")
GRAPH_PATH = os.path.join(STAGE3, "graph.yaml")
SKILL_PATH = os.path.join(root, "skills", "dev-flow", "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")

REQUIRED_NODES = (
    "N1-trigger",
    "N-skip",
    "S0-question",
    "S1-experiment",
    "S2-evidence",
    "N3-write-md",
    "S3-writeback",
    "S4-close",
    "N5-end",
)
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
TEETH_HEADINGS = ("進條件", "完成條件")
CANONICAL_MD = "docs/dev/<slug>/3-prototype.md"
CANONICAL_DECISION_MD = "docs/dev/<slug>/2-decision.md"
LOCKED_ACTIONS = ("write_prototype", "write_spec", "write_decision")
WRITE_PROTOTYPE_NODE = "N3-write-md"
WRITE_DECISION_NODE = "S3-writeback"
WRITE_DECISION_FORBIDDEN = (
    "N1-trigger",
    "N-skip",
    "S0-question",
    "S1-experiment",
    "S2-evidence",
    "N3-write-md",
    "N5-end",
)
N1_NEXT = "N-skip"
N1_FORK = "S0-question"
EXPECTED_NEXT = {
    "N-skip": "",
    "S0-question": "S1-experiment",
    "S1-experiment": "S2-evidence",
    "S2-evidence": "N3-write-md",
    "N3-write-md": "S3-writeback",
    "S3-writeback": "S4-close",
    "S4-close": "N5-end",
    "N5-end": "",
}
# 第 3 站允許 write_spec 的節點:本刀空集合(第 4 站還沒開始)
SPEC_ALLOWED_NODES = frozenset()
NEXT_ID_RE = re.compile(
    r"(?:S\d+-[A-Za-z0-9-]+|N(?:\d+)?-[A-Za-z0-9-]+|skill-legacy-\d+(?:-\d+)?)"
)
BAD_PROTO_RE = re.compile(r"3-prototype(?:-[A-Za-z0-9]+)+\.md")
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
            "缺 skills/dev-flow/stage3/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
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
    return os.path.join(STAGE3, rel.replace("/", os.sep))


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


def trigger_section(text):
    sections = split_sections(text)
    for key, body in sections.items():
        if "觸發判定" in key:
            return body
    return ""


def trigger_hit_count(text):
    body = trigger_section(text)
    return sum(1 for mark in CHECKBOX_RE.findall(body) if mark == "x")


def slug_has_hits(slug):
    if not slug:
        return False
    path = os.path.join(DOCS_DEV, slug, "3-prototype.md")
    if not os.path.isfile(path):
        return False
    return trigger_hit_count(open(path, encoding="utf-8").read()) > 0


def has_skip_oc(slug):
    if not slug:
        return False
    path = os.path.join(DOCS_DEV, slug, "2-decision.md")
    if not os.path.isfile(path):
        return False
    for line in open(path, encoding="utf-8"):
        if "Stage 3" in line and "跳過" in line:
            return True
    return False


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
    if action == "write_spec":
        hits = slug_has_hits(slug)
        skip = has_skip_oc(slug)
        if hits and not skip and node_id not in SPEC_ALLOWED_NODES:
            return "deny", (
                f"{node_id} 有命中、無 skip OC、游標不在第 3 站允許節點,"
                f"卻 write_spec（寫 4-spec.md）"
            )
        return "deny", f"{node_id} 未允許 write_spec（寫 4-spec.md）"
    if action == "write_prototype" and node_id in ("N1-trigger", "N-skip"):
        return "deny", f"{node_id} 禁止 write_prototype"
    if action == "write_decision" and node_id != WRITE_DECISION_NODE:
        return "deny", f"{node_id} 不得 write_decision(回寫在 S3)"
    allow = set(as_list(spec.get("allow")))
    forbid = set(as_list(spec.get("forbid")))
    if action in forbid:
        return "deny", f"{node_id} 禁止 {action}"
    if action in LOCKED_ACTIONS and action not in allow:
        return "deny", f"{node_id} 未允許 {action}"
    return "allow", f"{node_id} 允許 {action}"


def simulate_n3_rerun(write_paths, write_mode):
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="devstage3-n3-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "3-prototype.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("3-prototype*.md"))


def scan_live_prototype_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        hits = [f for f in filenames if re.fullmatch(r"3-prototype.*\.md", f)]
        if len(hits) > 1:
            rel = os.path.relpath(dirpath, root)
            failures.append(
                f"P0 {rel}/ 有 {len(hits)} 份 3-prototype*.md:{sorted(hits)}"
            )
    return failures


def scan_zero_hit_prototypes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        protos = [f for f in filenames if re.fullmatch(r"3-prototype.*\.md", f)]
        for name in protos:
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8").read()
            except OSError:
                continue
            if trigger_hit_count(text) == 0:
                rel = os.path.relpath(path, root)
                failures.append(
                    f"P0 九條觸發全未命中，卻存在 3-prototype.md:{rel}"
                )
    return failures


def check_fork_and_next(nodes, failures):
    if not isinstance(nodes, dict):
        return
    n1 = nodes.get("N1-trigger")
    if not isinstance(n1, dict):
        failures.append("P0 graph.yaml 缺節點 N1-trigger")
    else:
        actual_next = n1.get("next")
        if actual_next is None or actual_next == "":
            if "next" not in n1:
                failures.append("P0 N1-trigger 缺 next")
            elif actual_next != N1_NEXT:
                failures.append(
                    f"P0 N1-trigger next 必須是 {N1_NEXT},實際是 {actual_next!r}"
                )
        elif actual_next != N1_NEXT:
            failures.append(
                f"P0 N1-trigger next 必須是 {N1_NEXT},實際是 {actual_next!r}"
            )
        if "fork_required" not in n1:
            failures.append("P0 N1-trigger 缺 fork_required")
        elif n1.get("fork_required") != N1_FORK:
            failures.append(
                f"P0 N1-trigger fork_required 必須是 {N1_FORK},"
                f"實際是 {n1.get('fork_required')!r}"
            )
    for node_id, expected in EXPECTED_NEXT.items():
        spec = nodes.get(node_id)
        if not isinstance(spec, dict):
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
        if entry != "N1-trigger":
            failures.append(
                f"graph.yaml entry 必須是 N1-trigger,實際是 {entry!r}"
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
        next_body = sections.get("下一跳", "")
        if node_id == "N1-trigger":
            found = set(NEXT_ID_RE.findall(next_body))
            if N1_NEXT not in found or N1_FORK not in found:
                failures.append(
                    f"P0 {rel} 下一跳必須同時出現 {N1_NEXT} 與 {N1_FORK}"
                )
        else:
            actual_next = first_next_id(next_body)
            if actual_next is None:
                failures.append(f"P0 {rel} 下一跳讀不到節點 id 或「無」")
            elif actual_next != expected_next:
                failures.append(
                    f"P0 {rel} 下一跳是 {actual_next!r},graph.yaml next 是 "
                    f"{expected_next!r}"
                )
        write_body = sections.get("寫哪裡", "")
        for line in write_body.splitlines():
            if BAD_PROTO_RE.search(line) and not re.search(
                r"禁止|不得|禁", line
            ):
                failures.append(
                    f"P0 {rel} 寫哪裡把非正本 3-prototype*.md 當寫入目標"
                )
                break
        do_body = sections.get("做什麼", "")
        token = f"--write-cursor {node_id}"
        if token not in do_body:
            failures.append(f"P0 {rel} 做什麼必須呼叫 --write-cursor {node_id}")
        if node_id == "N3-write-md":
            if "3-prototype.md" not in write_body:
                failures.append(f"P0 {rel} 寫哪裡必須點名 3-prototype.md")
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"3-prototype\*\.md|第二份", write_body):
                if not re.search(r"禁止|不得|禁", write_body):
                    failures.append(f"P0 {rel} 必須禁止第二份 3-prototype*.md")

    if graph is None:
        failures.append(
            "P0 舊實作無法證明同 slug 第二份 3-prototype*.md 會被擋"
        )
        failures.append(
            "P0 舊實作沒有 N3 覆寫契約,無法證明 write_mode≠overwrite 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明九條觸發全未命中，卻存在 3-prototype.md 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明有命中、無 skip OC、游標不在第 3 站允許節點"
            "卻 write_spec（寫 4-spec.md）會被擋"
        )
        failures.extend(scan_live_prototype_dupes())
        failures.extend(scan_zero_hit_prototypes())
        return failures

    n3 = nodes.get("N3-write-md") or {}
    write_paths = as_list(n3.get("write"))
    write_mode = n3.get("write_mode") or ""
    if write_paths != [CANONICAL_MD]:
        failures.append(
            f"P0 graph.yaml N3 write 必須剛好是 {[CANONICAL_MD]},"
            f"實際是 {write_paths}"
        )
    if write_mode != "overwrite":
        failures.append(
            f"P0 graph.yaml N3 write_mode 必須是 overwrite,實際是 {write_mode!r}"
        )
    found = simulate_n3_rerun(write_paths or [CANONICAL_MD], write_mode)
    if found != ["3-prototype.md"]:
        failures.append(
            f"P0 模擬重跑 N3 後 3-prototype*.md = {found},必須只剩正本一份"
        )

    for node_id, spec in nodes.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("via"):
            failures.append(
                f"P0 {node_id} 用 via 當 hop,必須是 next / fork_required 真節點"
            )
        if spec.get("kind") == "skill-legacy":
            failures.append(
                f"P0 {node_id} 仍是 skill-legacy 團塊,必須拆成有節點檔的 hop"
            )
        allow = set(as_list(spec.get("allow")))
        if node_id == WRITE_PROTOTYPE_NODE:
            if "write_prototype" not in allow:
                failures.append("P0 N3-write-md 必須 allow write_prototype")
        elif "write_prototype" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_prototype")
        if node_id == WRITE_DECISION_NODE:
            if "write_decision" not in allow:
                failures.append(
                    "P0 S3-writeback 必須 allow write_decision"
                    "(同一份 2-decision.md,overwrite)"
                )
            if spec.get("write_mode") != "overwrite":
                failures.append(
                    "P0 S3-writeback allow write_decision 時 write_mode "
                    "必須是 overwrite"
                )
            write_dec = as_list(spec.get("write"))
            if write_dec != [CANONICAL_DECISION_MD]:
                failures.append(
                    f"P0 graph.yaml S3 write 必須剛好是 "
                    f"{[CANONICAL_DECISION_MD]},實際是 {write_dec}"
                )
        elif "write_decision" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_decision")
        if node_id in WRITE_DECISION_FORBIDDEN and "write_decision" in allow:
            failures.append(f"P0 {node_id} 不得放寬 write_decision")
        if "write_spec" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_spec")

    check_fork_and_next(nodes, failures)
    failures.extend(scan_live_prototype_dupes())
    failures.extend(scan_zero_hit_prototypes())
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

print("✅ PASS:Stage 3 graph 九真節點 / 觸發分叉 / 單產物 / 覆寫 / S3 回寫 / 第 4 站不准搶跑 全過")
sys.exit(0)
PY
