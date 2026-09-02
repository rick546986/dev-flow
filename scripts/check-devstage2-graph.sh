#!/bin/bash
# check-devstage2-graph.sh — Stage 2 節點鏈的機械契約
#
# 為什麼需要:把第 2 站切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   1. 沒有 stage2/graph.yaml 必須紅:舊實作(單一 SKILL、沒有 graph)無法證明
#      下一跳與重跑契約。
#   2. 真節點缺「進條件」或「完成條件」必須紅:節點不能單獨當入口。
#   3. 同 slug 第二份 2-decision*.md 必須紅:產物仍是一份。
#   4. write_mode≠overwrite 必須紅:重跑 N3 覆寫同一檔,不另存。
#   5. N1 在 1-discussion 未 approved 時寫 2-decision 必須紅。
#      --action 第三刀接到 prebash;不是沙盒,不重做第 1 站 write_code 編成。
#   6. 第二刀:legacy 1／2／4／5／6 必須是真節點檔。skill-legacy 團塊必須紅。
#      每個真節點「做什麼」必須 --write-cursor <本節點 id>。
#      N7／N8／S1 缺這一行必須紅。N1 已核准仍不得寫 2-decision。
#   7. 第三刀:S4／S5／S6 必須 allow write_decision(仍 overwrite、禁止第二份)。
#      不要放寬 N1／S1／S2／N7／N8。寫 4-spec.md 在 N8 過 G1 之前必須紅。
#      guide 第 2 站開頭必須對上九節點鏈。出現「Stage 2 還在單一 SKILL」必須紅。
#
# graph.yaml 是下一跳的唯一正本。本機游標 .devstage2-cursor.json 不進 Git。
# 不改 check-devtalk-graph.sh。不改 _templates/2-decision.md 正文。
#
# 用法:
#   scripts/check-devstage2-graph.sh [root]
#   scripts/check-devstage2-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node},action,slug?}
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devstage2-graph.sh --write-cursor NODE [SLUG] [root]
#       把 .devstage2-cursor.json 寫成 {node, slug}。不改 .dev-flow。
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
    dest = os.path.join(root, ".devstage2-cursor.json")
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

STAGE2 = os.path.join(root, "skills", "dev-flow", "stage2")
GRAPH_PATH = os.path.join(STAGE2, "graph.yaml")
SKILL_PATH = os.path.join(root, "skills", "dev-flow", "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")

REQUIRED_NODES = (
    "N1-handoff",
    "S1-approaches",
    "S2-stress",
    "N3-write-md",
    "S4-oc",
    "S5-adr",
    "S6-selfcheck",
    "N7-g1",
    "N8-end",
)
REQUIRED_CHAIN = (
    "N1-handoff",
    "S1-approaches",
    "S2-stress",
    "N3-write-md",
    "S4-oc",
    "S5-adr",
    "S6-selfcheck",
    "N7-g1",
    "N8-end",
)
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
TEETH_HEADINGS = ("進條件", "完成條件")
# 晚改可見行為鎖:N3 定稿完成條件必須含這些句,缺了 = 圖牙紅。
DONE_NEEDLES = {
    "N3-write-md": ("晚改可見行為", "先改 Decision"),
}
CANONICAL_MD = "docs/dev/<slug>/2-decision.md"
LOCKED_ACTIONS = ("write_decision", "write_spec")
WRITE_DECISION_NODES = (
    "N3-write-md",
    "S4-oc",
    "S5-adr",
    "S6-selfcheck",
)
GUIDE_PATH = os.path.join(root, "guides", "guide-dev-flow.html")
STALE_GUIDE = "Stage 2 還在單一 SKILL"
NEXT_ID_RE = re.compile(
    r"(?:S\d+-[A-Za-z0-9-]+|N\d+-[A-Za-z0-9-]+|skill-legacy-\d+(?:-\d+)?)"
)
BAD_DECISION_RE = re.compile(r"2-decision(?:-[A-Za-z0-9]+)+\.md")
STATUS_RE = re.compile(r"^status:\s*(\S+)", re.M)
OQ_ITEM_RE = re.compile(r"^[-*]\s+\[(.)\]", re.M)
THREE_STATE = set("x~>")


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
            "缺 skills/dev-flow/stage2/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
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
    return os.path.join(STAGE2, rel.replace("/", os.sep))


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


def oq_all_three_state(text):
    sections = split_sections(text)
    body = sections.get("Open Questions", "")
    items = OQ_ITEM_RE.findall(body)
    if not items:
        return False
    return all(mark in THREE_STATE for mark in items)


def discussion_gate(slug):
    if not slug:
        return None, "action JSON 缺 slug,無法核 1-discussion"
    path = os.path.join(DOCS_DEV, slug, "1-discussion.md")
    if not os.path.isfile(path):
        return None, f"缺 docs/dev/{slug}/1-discussion.md"
    text = open(path, encoding="utf-8").read()
    status = frontmatter_status(text)
    if status != "approved":
        return False, (
            f"1-discussion 未 approved(status={status or '缺'}),不得寫 2-decision"
        )
    if not oq_all_three_state(text):
        return False, f"1-discussion Open Questions 未全三態,不得寫 2-decision"
    return True, f"1-discussion status=approved,OQ 全三態"


def evaluate_action(graph, payload):
    cursor = payload.get("cursor") or {}
    node_id = cursor.get("node")
    action = payload.get("action")
    slug = payload.get("slug") or cursor.get("slug") or ""
    if not action:
        return "error", "action JSON 缺 action"
    if action == "write_decision":
        ok, reason = discussion_gate(slug)
        if ok is not True:
            return "deny", reason
        if node_id == "N1-handoff":
            return "deny", "N1-handoff 不得寫 2-decision(寫檔在 N3)"
    if action == "write_spec":
        if node_id != "N8-end":
            return "deny", (
                f"{node_id or '無游標'} 未過 G1(N8),不得寫 4-spec"
            )
    if not node_id:
        return "error", "action JSON 缺 cursor.node"
    spec = (graph.get("nodes") or {}).get(node_id)
    if not isinstance(spec, dict):
        return "error", f"graph.yaml 沒有節點 {node_id}"
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

    with tempfile.TemporaryDirectory(prefix="devstage2-n3-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "2-decision.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("2-decision*.md"))


def scan_live_decision_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        hits = [f for f in filenames if re.fullmatch(r"2-decision.*\.md", f)]
        if len(hits) > 1:
            rel = os.path.relpath(dirpath, root)
            failures.append(
                f"P0 {rel}/ 有 {len(hits)} 份 2-decision*.md:{sorted(hits)}"
            )
    return failures


def check_chain(nodes, failures):
    if not isinstance(nodes, dict):
        return
    for index, src in enumerate(REQUIRED_CHAIN[:-1]):
        dest = REQUIRED_CHAIN[index + 1]
        spec = nodes.get(src)
        if not isinstance(spec, dict):
            failures.append(f"P0 graph.yaml 缺節點 {src}")
            continue
        actual = spec.get("next") or ""
        if actual == dest:
            continue
        later = set(REQUIRED_CHAIN[index + 2:])
        if actual in later:
            failures.append(
                f"P0 {src} next 跨過暫留步 {dest}:直接跳到 {actual},"
                f"必須先經 {dest}"
            )
        else:
            failures.append(
                f"P0 {src} next 必須是 {dest},實際是 {actual!r}"
            )


def check_live(graph):
    failures = []
    if not os.path.isfile(SKILL_PATH):
        failures.append("缺 skills/dev-flow/SKILL.md")

    nodes = graph.get("nodes") if graph else {}
    if graph is not None:
        entry = graph.get("entry")
        if entry != "N1-handoff":
            failures.append(
                f"graph.yaml entry 必須是 N1-handoff,實際是 {entry!r}"
            )

    for node_id in REQUIRED_NODES:
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        path = node_path(node_id, spec or {})
        rel = os.path.relpath(path, root)
        if not os.path.isfile(path):
            failures.append(f"P0 缺 {rel} —— 真節點不能單獨當入口")
            continue
        text = open(path, encoding="utf-8").read()
        sections = split_sections(text)
        for heading in REQUIRED_HEADINGS:
            body = sections.get(heading, "")
            if heading not in sections or not body.strip():
                if heading in TEETH_HEADINGS:
                    failures.append(f"P0 {rel} 缺「{heading}」或該節為空")
                else:
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
            if BAD_DECISION_RE.search(line) and not re.search(
                r"禁止|不得|禁", line
            ):
                failures.append(
                    f"P0 {rel} 寫哪裡把非正本 2-decision*.md 當寫入目標"
                )
                break
        do_body = sections.get("做什麼", "")
        token = f"--write-cursor {node_id}"
        if token not in do_body:
            failures.append(f"P0 {rel} 做什麼必須呼叫 --write-cursor {node_id}")
        if node_id == "N3-write-md":
            if "2-decision.md" not in write_body:
                failures.append(f"P0 {rel} 寫哪裡必須點名 2-decision.md")
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"2-decision\*\.md|第二份", write_body):
                if not re.search(r"禁止|不得|禁", write_body):
                    failures.append(f"P0 {rel} 必須禁止第二份 2-decision*.md")

    if graph is None:
        failures.append(
            "P0 舊實作沒有 N3 覆寫契約,無法證明重跑落檔不會另存"
        )
        failures.extend(scan_live_decision_dupes())
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
    if found != ["2-decision.md"]:
        failures.append(
            f"P0 模擬重跑 N3 後 2-decision*.md = {found},必須只剩正本一份"
        )

    for node_id, spec in nodes.items():
        if not isinstance(spec, dict):
            continue
        allow = set(as_list(spec.get("allow")))
        if node_id in WRITE_DECISION_NODES:
            if "write_decision" not in allow:
                failures.append(
                    f"P0 {node_id} 必須 allow write_decision"
                    "(同一份 2-decision.md,overwrite)"
                )
            if spec.get("write_mode") != "overwrite":
                failures.append(
                    f"P0 {node_id} allow write_decision 時 write_mode 必須是 overwrite"
                )
        elif "write_decision" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_decision")
        if node_id == "N8-end" and "write_spec" not in allow:
            failures.append("P0 N8-end 必須 allow write_spec(過 G1 後才准寫 4-spec)")
        if "write_spec" in allow and node_id != "N8-end":
            failures.append(f"P0 {node_id} 不得 allow write_spec")
        if spec.get("kind") == "skill-legacy":
            failures.append(
                f"P0 {node_id} 仍是 skill-legacy 團塊,必須拆成有節點檔的 hop"
            )

    check_chain(nodes, failures)
    failures.extend(scan_live_decision_dupes())
    failures.extend(check_action_runtime_wired())
    failures.extend(check_guide(graph))
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
            code = "\n".join(
                line.split("#", 1)[0] for line in text.splitlines()
            )
            if "check-devstage2-graph" in code and "--action" in code:
                return []
    return [
        "P0 --action 沒接到 runtime:hooks 沒有呼叫 check-devstage2-graph.sh --action"
    ]


def check_guide(_graph):
    """第 2 站開頭對上九節點鏈;舊句「還在單一 SKILL」必須紅。"""
    if not os.path.isfile(GUIDE_PATH):
        return ["P0 指南檔缺席:找不到 guides/guide-dev-flow.html"]
    text = open(GUIDE_PATH, encoding="utf-8").read()
    failures = []
    if STALE_GUIDE in text:
        failures.append(f"P0 guide 出現「{STALE_GUIDE}」")
    match = re.search(r'<h3 id="stage2">.*?(?=<h3 |\Z)', text, re.S)
    if not match:
        failures.append("P0 guide 找不到第 2 站 <h3 id=\"stage2\">")
        return failures
    head = match.group(0)[:2500]
    missing = [node_id for node_id in REQUIRED_NODES if node_id not in head]
    if missing:
        failures.append(
            "P0 guide 第 2 站開頭缺節點:" + ",".join(missing)
        )
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

print("✅ PASS:Stage 2 graph 九真節點 / 單產物 / 覆寫 / 游標寫入 / N1 不得寫檔 全過")
sys.exit(0)
PY
