#!/bin/bash
# check-devtalk-graph.sh — Stage 1 節點鏈的機械契約
#
# 為什麼需要:把 /dev-talk 切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   P0-1 產物仍是一份:graph 跑完或重跑 N9,docs/dev/<slug>/ 不得長出第二份
#        1-discussion*.md;禁止每個節點再生討論檔。
#   P0-2 每個 hop 必須有節點檔、可單獨當入口:缺「進條件 / 做什麼 / 完成條件 /
#        下一跳」→ 紅;graph.yaml 的 next 不得跳過;SKILL.md 只留入口與摘要,
#        正本只准一處。
#   P0-3 重跑不得重開 session:游標已在 N3 且 MEMORY_SESSION_ID 已在 → 不得
#        talk start;游標在 N9 → 不得寫程式碼、不得 talk end;N13 之前任何
#        節點直接寫入知識目錄 → 紅。
#   P0-4 本機游標:N1 / SKILL 必須呼叫 --write-cursor;沒游標檔時 write_code /
#        talk_end / write_knowledge 走 --action 必須 deny。檔不進 Git。
#
# graph.yaml 是下一跳的唯一正本。本機游標不進 Git。
#
# 用法:
#   scripts/check-devtalk-graph.sh [root]          # 驗該 root 的 skills/dev-talk
#   scripts/check-devtalk-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node,MEMORY_SESSION_ID},action}
#       依 graph.yaml 的 allow/forbid 判定 allow 或 deny(stdout 一行)。
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devtalk-graph.sh --write-cursor NODE SESSION [root]
#       把 .devtalk-cursor.json 寫成 {node, MEMORY_SESSION_ID}。不改 .dev-flow。
#
# exit:0 = 全過 / 1 = 真違規 / 2 = 檢查自身故障(NOT-PARSED)

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
ACTION_FILE=""
WRITE_NODE=""
WRITE_SESSION=""
if [ "${1:-}" = "--action" ]; then
  ACTION_FILE=${2:-}
  [ -n "$ACTION_FILE" ] || { echo "FATAL: --action 需要 JSON 路徑" >&2; exit 2; }
  if [ -n "${3:-}" ]; then
    ROOT=$(cd "$3" && pwd) || exit 2
  fi
elif [ "${1:-}" = "--write-cursor" ]; then
  WRITE_NODE=${2:-}
  WRITE_SESSION=${3:-}
  [ -n "$WRITE_NODE" ] && [ -n "$WRITE_SESSION" ] || {
    echo "FATAL: --write-cursor 需要 NODE 與 SESSION" >&2
    exit 2
  }
  if [ -n "${4:-}" ]; then
    ROOT=$(cd "$4" && pwd) || exit 2
  fi
elif [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" "$ACTION_FILE" "$WRITE_NODE" "$WRITE_SESSION" <<'PY'
import json
import os
import re
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root = sys.argv[1]
action_file = sys.argv[2]
write_node = sys.argv[3] if len(sys.argv) > 3 else ""
write_session = sys.argv[4] if len(sys.argv) > 4 else ""

if write_node:
    dest = os.path.join(root, ".devtalk-cursor.json")
    tmp = dest + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(
            {"node": write_node, "MEMORY_SESSION_ID": write_session},
            handle,
            ensure_ascii=False,
        )
        handle.write("\n")
    os.replace(tmp, dest)
    print(f"wrote {dest} node={write_node}")
    sys.exit(0)

TALK = os.path.join(root, "skills", "dev-talk")
GRAPH_PATH = os.path.join(TALK, "graph.yaml")
SKILL_PATH = os.path.join(TALK, "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")

REQUIRED_NODES = (
    "N1-start",
    "S0-scope",
    "S1-survey",
    "S2-world",
    "N3-probe",
    "S4-accept",
    "S5-diverge",
    "S6-blind",
    "N9-write-md",
    "S8-review",
    "S9-terms",
    "S10-html",
    "N13-end",
)
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
N3_MARKERS = ("每輪三律", "3a. 前提被推翻", "3b. 發現實為多題")
LEFTOVER_DUAL = (
    ("S0-scope", ("不放鬆查證與必問",)),
    ("S1-survey", ("認可後的清單 = 本次「已核事實」",)),
    ("S2-world", ("系統外角色也要列",)),
    ("S4-accept", ("問現象不問做法",)),
    ("S5-diverge", ("純發散、不收斂",)),
    ("S6-blind", ("沉默不算",)),
    ("S8-review", ("嚴格審視者視角重讀全檔",)),
    ("S9-terms", ("同名異義分立互註",)),
    ("S10-html", ("html 要改,先改 md 再重生",)),
)
CANONICAL_MD = "docs/dev/<slug>/1-discussion.md"
LOCKED_ACTIONS = (
    "talk_start",
    "talk_end",
    "write_code",
    "write_knowledge",
    "write_discussion_md",
)
NEXT_ID_RE = re.compile(
    r"(?:S\d+-[A-Za-z0-9-]+|N\d+-[A-Za-z0-9-]+|skill-legacy-\d+(?:-\d+)?)"
)
BAD_DISCUSSION_RE = re.compile(
    r"1-discussion(?:-[A-Za-z0-9]+)+\.md"
)
REQUIRED_CHAIN = (
    "N1-start",
    "S0-scope",
    "S1-survey",
    "S2-world",
    "N3-probe",
    "S4-accept",
    "S5-diverge",
    "S6-blind",
    "N9-write-md",
    "S8-review",
    "S9-terms",
    "S10-html",
    "N13-end",
)


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
        return None, ["缺 skills/dev-talk/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
                      "無法證明下一跳與重跑契約"]
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
    return os.path.join(TALK, rel.replace("/", os.sep))


def split_sections(text):
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    out = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[match.group(1).strip()] = text[match.end():end]
    return out


def first_next_id(section_text):
    stripped = section_text.strip()
    if re.search(r"^(無|結束|（無）|\(none\))$", stripped.splitlines()[0].strip()
                 if stripped else ""):
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


def evaluate_action(graph, payload):
    cursor = payload.get("cursor") or {}
    node_id = cursor.get("node")
    session = cursor.get("MEMORY_SESSION_ID")
    action = payload.get("action")
    if not action:
        return "error", "action JSON 缺 action"
    if not node_id:
        if action in ("write_code", "talk_end", "write_knowledge"):
            return "deny", f"沒有游標檔,不得 {action}"
        if action == "talk_start" and session:
            return "deny", "沒有游標但已有 MEMORY_SESSION_ID,不得 talk start"
        return "error", "action JSON 缺 cursor.node"
    spec = (graph.get("nodes") or {}).get(node_id)
    if not isinstance(spec, dict):
        return "error", f"graph.yaml 沒有節點 {node_id}"
    allow = set(as_list(spec.get("allow")))
    forbid = set(as_list(spec.get("forbid")))
    if action == "talk_start" and session and (
        "talk_start_if_session" in forbid or "talk_start" in forbid
    ):
        return "deny", f"{node_id} 已有 MEMORY_SESSION_ID,不得 talk start"
    if action in forbid:
        return "deny", f"{node_id} 禁止 {action}"
    if action == "write_knowledge" and node_id != "N13-end":
        return "deny", f"{node_id} 在 N13 之前不得寫入知識目錄"
    if action in LOCKED_ACTIONS and action not in allow:
        return "deny", f"{node_id} 未允許 {action}"
    return "allow", f"{node_id} 允許 {action}"


def simulate_n9_rerun(write_paths, write_mode):
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="devtalk-n9-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "1-discussion.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("1-discussion*.md"))


def scan_live_discussion_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        hits = [f for f in filenames if re.fullmatch(r"1-discussion.*\.md", f)]
        if len(hits) > 1:
            rel = os.path.relpath(dirpath, root)
            failures.append(
                f"P0-1 {rel}/ 有 {len(hits)} 份 1-discussion*.md:{sorted(hits)}"
            )
    return failures


def check_action_runtime_wired():
    """P1:--action 必須接到 hook,不能只活在 test fixture。"""
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
            if "check-devtalk-graph" in code and "--action" in code:
                return []
    return ["P1 --action 沒接到 runtime:hooks 沒有呼叫 check-devtalk-graph.sh --action"]


def check_legacy_hops(nodes, failures):
    """P0:next 不得跳過任何 hop。舊 skill-legacy 團塊不再算真節點。"""
    if not isinstance(nodes, dict):
        return
    for node_id, spec in nodes.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("kind") == "skill-legacy":
            failures.append(
                f"P0 {node_id} 仍是 skill-legacy 團塊,必須拆成有節點檔的 hop"
            )
        via = spec.get("via")
        if via and via not in nodes:
            failures.append(
                f"P0 {node_id} via={via!r} 只是字串,不是真節點 —— 暫留步會被跳過"
            )
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
    skill_text = ""
    if os.path.isfile(SKILL_PATH):
        skill_text = open(SKILL_PATH, encoding="utf-8").read()
    else:
        failures.append("缺 skills/dev-talk/SKILL.md")

    nodes = graph.get("nodes") if graph else {}
    if graph is not None:
        entry = graph.get("entry")
        if entry != "N1-start":
            failures.append(f"graph.yaml entry 必須是 N1-start,實際是 {entry!r}")

    for node_id in REQUIRED_NODES:
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        path = node_path(node_id, spec or {})
        rel = os.path.relpath(path, root)
        if not os.path.isfile(path):
            failures.append(f"P0-2 缺 {rel} —— 節點不能單獨當入口")
            continue
        text = open(path, encoding="utf-8").read()
        sections = split_sections(text)
        for heading in REQUIRED_HEADINGS:
            body = sections.get(heading, "")
            if heading not in sections or not body.strip():
                failures.append(f"P0-2 {rel} 缺「{heading}」或該節為空")
        if spec is None:
            failures.append(f"P0-2 graph.yaml 沒有節點 {node_id}")
            continue
        expected_next = spec.get("next", "")
        if expected_next is None:
            expected_next = ""
        actual_next = first_next_id(sections.get("下一跳", ""))
        if actual_next is None:
            failures.append(f"P0-2 {rel} 下一跳讀不到節點 id 或「無」")
        elif actual_next != expected_next:
            failures.append(
                f"P0-2 {rel} 下一跳是 {actual_next!r},graph.yaml next 是 "
                f"{expected_next!r}"
            )
        write_body = sections.get("寫哪裡", "")
        for line in write_body.splitlines():
            if BAD_DISCUSSION_RE.search(line) and not re.search(
                r"禁止|不得|禁", line
            ):
                failures.append(
                    f"P0-1 {rel} 寫哪裡把非正本 1-discussion*.md 當寫入目標"
                )
                break
        if node_id == "N9-write-md":
            if "1-discussion.md" not in write_body:
                failures.append(f"P0-1 {rel} 寫哪裡必須點名 1-discussion.md")
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0-1 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"talk\s+end", write_body, re.I) or "talk end" in text:
                if "不得 talk end" not in text and "禁 talk end" not in text:
                    failures.append(f"P0-3 {rel} 必須禁止 talk end")
            if "程式碼" in text and not re.search(r"不得寫程式碼|禁.*程式碼", text):
                failures.append(f"P0-3 {rel} 必須禁止寫程式碼")

    if skill_text and os.path.isfile(node_path("N3-probe", nodes.get("N3-probe") or {})):
        n3_text = open(node_path("N3-probe", nodes.get("N3-probe") or {}),
                       encoding="utf-8").read()
        skill_has = all(m in skill_text for m in N3_MARKERS)
        node_has = all(m in n3_text for m in N3_MARKERS)
        if skill_has and node_has:
            failures.append(
                "P0-2 SKILL.md 仍複製 N3 完整步驟正文,與 nodes/N3-probe.md 雙正本"
            )

    for node_id, markers in LEFTOVER_DUAL:
        path = node_path(node_id, nodes.get(node_id) or {})
        if not (skill_text and os.path.isfile(path)):
            continue
        node_text = open(path, encoding="utf-8").read()
        if all(m in skill_text for m in markers) and all(
            m in node_text for m in markers
        ):
            failures.append(
                f"P0-2 SKILL.md 仍複製 {node_id} 完整步驟正文,與 {os.path.relpath(path, root)} 雙正本"
            )

    if skill_text and "--write-cursor" not in skill_text:
        failures.append("P0 SKILL.md 必須呼叫 --write-cursor(N1 寫本機游標)")
    n1_path = node_path("N1-start", nodes.get("N1-start") or {})
    if os.path.isfile(n1_path):
        n1_text = open(n1_path, encoding="utf-8").read()
        if "--write-cursor" not in n1_text:
            failures.append("P0 nodes/N1-start.md 必須呼叫 --write-cursor")

    if graph is None:
        failures.append(
            "P0-1 舊實作沒有 N9 覆寫契約,無法證明重跑落檔不會另存"
        )
        failures.append(
            "P0-3 舊實作沒有游標契約,無法證明重跑 N3 不會重開 talk start"
        )
        failures.extend(scan_live_discussion_dupes())
        return failures

    n9 = nodes.get("N9-write-md") or {}
    write_paths = as_list(n9.get("write"))
    write_mode = n9.get("write_mode") or ""
    if write_paths != [CANONICAL_MD]:
        failures.append(
            f"P0-1 graph.yaml N9 write 必須剛好是 {[CANONICAL_MD]},"
            f"實際是 {write_paths}"
        )
    if write_mode != "overwrite":
        failures.append(
            f"P0-1 graph.yaml N9 write_mode 必須是 overwrite,實際是 {write_mode!r}"
        )
    found = simulate_n9_rerun(write_paths or [CANONICAL_MD], write_mode)
    if found != ["1-discussion.md"]:
        failures.append(
            f"P0-1 模擬重跑 N9 後 1-discussion*.md = {found},必須只剩正本一份"
        )

    for node_id, spec in nodes.items():
        if not isinstance(spec, dict):
            continue
        allow = set(as_list(spec.get("allow")))
        forbid = set(as_list(spec.get("forbid")))
        if node_id == "N1-start" and "talk_start_if_session" not in forbid:
            failures.append("P0-3 graph.yaml N1-start 必須 forbid talk_start_if_session")
        if node_id == "N3-probe" and "talk_start_if_session" not in forbid:
            failures.append("P0-3 graph.yaml N3-probe 必須 forbid talk_start_if_session")
        if node_id == "N9-write-md":
            for item in ("write_code", "talk_end", "write_knowledge"):
                if item not in forbid:
                    failures.append(f"P0-3 graph.yaml N9-write-md 必須 forbid {item}")
        if node_id != "N13-end" and "write_knowledge" not in forbid:
            failures.append(f"P0-3 graph.yaml {node_id} 必須 forbid write_knowledge")
        if node_id == "N1-start" and "talk_start" not in allow:
            failures.append("P0-3 graph.yaml N1-start 必須 allow talk_start")
        if node_id == "N13-end" and "talk_end" not in allow:
            failures.append("P0-3 graph.yaml N13-end 必須 allow talk_end")
        if "write_discussion_md" in allow and node_id != "N9-write-md":
            failures.append(f"P0-1 {node_id} 不得 allow write_discussion_md")

    check_legacy_hops(nodes, failures)
    failures.extend(check_action_runtime_wired())
    failures.extend(scan_live_discussion_dupes())
    return failures


graph, graph_fail = load_graph()
if action_file:
    if graph is None:
        print("error\t" + (graph_fail[0] if graph_fail else "缺 graph.yaml"),
              file=sys.stderr)
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

print("✅ PASS:dev-talk graph 節點鏈 / 單產物 / 游標寫入 / 重跑不重開 session 全過")
sys.exit(0)
PY
