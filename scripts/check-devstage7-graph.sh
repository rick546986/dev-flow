#!/bin/bash
# check-devstage7-graph.sh — Stage 7 第三刀的機械契約
#
# 為什麼需要:把第 7 站切成可單獨重跑的節點之後,有幾件事不能只靠散文 —
#   1. 沒有 stage7/graph.yaml 必須紅:舊實作(單一 SKILL、沒有 graph)無法證明
#      下一跳與重跑契約。
#   2. 真節點缺「進條件」或「完成條件」必須紅:節點不能單獨當入口。
#   3. 同 slug 第二份 7-review*.md 必須紅:產物仍是一份。
#   4. write_mode≠overwrite 必須紅:重跑寫檔節點覆寫同一檔,不另存。
#   5. 缺 N4-author 必須紅:必須有寫檔節點,不要只做 handoff。
#   6. 未過 G2(4-spec 不是 approved)卻 write_review(寫 7-review.md)必須紅:
#      第 4 站還沒核准不准搶跑第 7 站。
#   7. N0／N1／N3／N5／S2-* 做 read_notes(讀 6-notes)必須紅:N4 才准讀
#      (對應 review-unlock)。S2 禁讀 Self-Review。
#   8. 7-self-review.md／7-review-*.md 必須紅:產物只有一份 7-review.md。
#   9. owner 自審無限制聲明節視同未審。
#  10. 第二刀:乘客步 2／2b／2c／2d／2e 必須是真節點檔。kind: skill-legacy
#      團塊必須紅 —— 第一刀的暫留 hop 到這一刀就沒有存在理由了。
#      每個真節點「做什麼」必須 --write-cursor <本節點 id>。
#      S2-run／S2b-phenomena／S2c-integration／S2d-fresh／S2e-walkthrough
#      與 N4-author 才 allow write_review(同一份 7-review.md,overwrite);
#      不要放寬 N0-role／N1-matrix／N3-axes／N5-verdict。
#      S2c 必須點名現有 devflow-integration-regression.sh,且在 Final Fresh 之前。
#      S2d 必須點名現有 devflow-evidence-gauntlet.sh,且綁 SHA。不准重寫那些工具。
#      write_notes 一律 deny。有 via 必須紅。
#  11. 第三刀:--action 必須接到 prebash,不能只活在 test fixture。
#      guide 第 7 站開頭必須對上十節點鏈。出現「Stage 7 還在單一 SKILL」必須紅。
#      不改第 1–6 站的編成。不改鬆圍欄③。不重開 hardening。
#
# graph.yaml 是下一跳的唯一正本。分叉與暫留一律用 next 指到的真節點,禁止 via
# (第 1 站 0030 的假綠就是 via 字串當 hop 換來的)。
# 本機游標 .devstage7-cursor.json 不進 Git。
# 不改 check-devtalk-graph.sh / check-devstage2-graph.sh / check-devstage3-graph.sh /
# check-devstage4-graph.sh / check-devstage5-graph.sh / check-devstage6-graph.sh。
# 不改 _templates/7-review.md 正文(乘客清單正本是它的頂註 0–5)。
# 不改 Gauntlet、Evidence 契約、空欄擋、層名全等、「出貨樹=審過的樹」、Final Fresh 綁 SHA。
#
# 用法:
#   scripts/check-devstage7-graph.sh [root]
#   scripts/check-devstage7-graph.sh --action FILE [root]
#       FILE 是一份 JSON:{cursor:{node,slug},action,slug?}
#       deny → exit 1;allow → exit 0;契約缺失 → exit 2。
#   scripts/check-devstage7-graph.sh --write-cursor NODE [SLUG] [root]
#       把 .devstage7-cursor.json 寫成 {node, slug}。不改 .dev-flow。
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
    dest = os.path.join(root, ".devstage7-cursor.json")
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

STAGE7 = os.path.join(root, "skills", "dev-flow", "stage7")
GRAPH_PATH = os.path.join(STAGE7, "graph.yaml")
SKILL_PATH = os.path.join(root, "skills", "dev-flow", "SKILL.md")
DOCS_DEV = os.path.join(root, "docs", "dev")
GUIDE_PATH = os.path.join(root, "guides", "guide-dev-flow.html")
STALE_GUIDE = "Stage 7 還在單一 SKILL"

ENTRY_NODE = "N0-role"
WRITE_REVIEW_NODE = "N4-author"
INTEGRATION_NODE = "S2c-integration"
FRESH_NODE = "S2d-fresh"
INTEGRATION_SCRIPT = "devflow-integration-regression.sh"
GAUNTLET_SCRIPT = "devflow-evidence-gauntlet.sh"
# 第二刀:十個真節點檔,沒有 skill-legacy 團塊。
CHAIN = (
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
REQUIRED_NODES = CHAIN
EXPECTED_NEXT = {
    "N0-role": "N1-matrix",
    "N1-matrix": "S2-run",
    "S2-run": "S2b-phenomena",
    "S2b-phenomena": "S2c-integration",
    "S2c-integration": "S2d-fresh",
    "S2d-fresh": "S2e-walkthrough",
    "S2e-walkthrough": "N3-axes",
    "N3-axes": "N4-author",
    "N4-author": "N5-verdict",
    "N5-verdict": "",
}
REQUIRED_HEADINGS = ("進條件", "讀什麼", "寫哪裡", "做什麼", "完成條件", "下一跳")
CANONICAL_MD = "docs/dev/<slug>/7-review.md"
LOCKED_ACTIONS = ("write_review", "read_notes", "write_notes")
# S2-* 與 N4 共寫同一份 7-review.md。read_notes 只有 N4。write_notes 一律不得 allow。
REVIEW_ALLOWED_NODES = (
    "S2-run",
    "S2b-phenomena",
    "S2c-integration",
    "S2d-fresh",
    "S2e-walkthrough",
    "N4-author",
)
REVIEW_FORBIDDEN_NODES = ("N0-role", "N1-matrix", "N3-axes", "N5-verdict")

NEXT_ID_RE = re.compile(
    r"(?:S\d+[a-z]?-[A-Za-z0-9-]+|N(?:\d+)?-[A-Za-z0-9-]+|skill-legacy-\d+(?:-\d+)?)"
)
BAD_REVIEW_RE = re.compile(r"7-review(?:-[A-Za-z0-9]+)+\.md")
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
            "缺 skills/dev-flow/stage7/graph.yaml —— 舊實作(單一 SKILL、沒有 graph)"
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
    return os.path.join(STAGE7, rel.replace("/", os.sep))


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
            f"審查期不准改寫第 6 站筆記"
        )
    if action == "write_review":
        if node_id not in REVIEW_ALLOWED_NODES:
            return "deny", (
                f"{node_id} 未允許 write_review（寫 7-review.md）—— "
                f"只有 {'／'.join(REVIEW_ALLOWED_NODES)} 可寫"
            )
        if not spec_approved(slug):
            return "deny", (
                f"{node_id} 未過 G2(4-spec 不是 approved)卻 write_review"
                f"（寫 7-review.md）"
            )
    if action == "read_notes":
        if node_id != WRITE_REVIEW_NODE:
            return "deny", (
                f"{node_id} 不得 read_notes(讀 6-notes)—— "
                f"只有 {WRITE_REVIEW_NODE} 准讀(對應 review-unlock)"
            )
    allow = set(as_list(spec.get("allow")))
    forbid = set(as_list(spec.get("forbid")))
    if action in forbid:
        return "deny", f"{node_id} 禁止 {action}"
    if action in LOCKED_ACTIONS and action not in allow:
        return "deny", f"{node_id} 未允許 {action}"
    return "allow", f"{node_id} 允許 {action}"


def simulate_n4_rerun(write_paths, write_mode):
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="devstage7-n4-") as tmp:
        slug = Path(tmp) / "docs" / "dev" / "sim-slug"
        slug.mkdir(parents=True)
        (slug / "7-review.md").write_text("first\n", encoding="utf-8")
        for _ in range(2):
            for spec in write_paths:
                rel = spec.replace("<slug>", "sim-slug")
                dest = Path(tmp) / rel
                if write_mode != "overwrite":
                    dest = dest.with_name(f"{dest.stem}-rerun{dest.suffix}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("rerun\n", encoding="utf-8")
        return sorted(p.name for p in slug.glob("7-review*.md"))


def scan_live_review_dupes():
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for dirpath, dirnames, filenames in os.walk(DOCS_DEV):
        dirnames[:] = [d for d in dirnames if d not in (".git",)]
        extras = [
            f for f in filenames
            if re.fullmatch(r"7-self-review\.md", f)
            or re.fullmatch(r"7-review-.+\.md", f)
        ]
        reviews = [f for f in filenames if re.fullmatch(r"7-review.*\.md", f)]
        rel = os.path.relpath(dirpath, root)
        if extras:
            failures.append(
                f"P0 {rel}/ 禁止 7-self-review.md／7-review-*.md:{sorted(extras)}"
            )
        elif len(reviews) > 1:
            failures.append(
                f"P0 {rel}/ 有 {len(reviews)} 份 7-review*.md:{sorted(reviews)}"
            )
    return failures


def scan_g2_entry_block():
    """掃 live 樹:已有 7-review.md 卻沒過 G2 的 slug,N0 不得當入口。"""
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    for name in sorted(os.listdir(DOCS_DEV)):
        slug_dir = os.path.join(DOCS_DEV, name)
        if not os.path.isdir(slug_dir):
            continue
        if not os.path.isfile(os.path.join(slug_dir, "7-review.md")):
            continue
        # 歷史 slug 可能只有 7-review、沒有 4-spec;那不是本契約的 graph 產物。
        # 只在 4-spec.md 存在卻未 approved 時,才禁止 N0 當入口。
        if not os.path.isfile(os.path.join(slug_dir, "4-spec.md")):
            continue
        if not spec_approved(name):
            failures.append(
                f"P0 docs/dev/{name}/ 已有 7-review.md 卻沒過 G2"
                f"(4-spec 不是 approved)—— N0-role 不是入口,退回第 4 站"
            )
    return failures


def scan_owner_self_review():
    """owner 自審卻沒有限制聲明節 → 視同未審。"""
    failures = []
    if not os.path.isdir(DOCS_DEV):
        return failures
    marker = re.compile(r"owner 自審|審查者\s*=\s*實作者")
    for name in sorted(os.listdir(DOCS_DEV)):
        path = os.path.join(DOCS_DEV, name, "7-review.md")
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        if marker.search(text) and "限制聲明" not in text:
            failures.append(
                f"P0 docs/dev/{name}/7-review.md owner 自審無限制聲明節"
                f"—— 視同未審"
            )
    return failures


def check_chain(nodes, failures):
    for node_id, expected in EXPECTED_NEXT.items():
        spec = nodes.get(node_id) if isinstance(nodes, dict) else None
        if not isinstance(spec, dict):
            if node_id == WRITE_REVIEW_NODE:
                failures.append(
                    "P0 graph.yaml 缺節點 N4-author —— 必須有寫檔節點,"
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
            if BAD_REVIEW_RE.search(line) and not re.search(r"禁止|不得|禁", line):
                failures.append(
                    f"P0 {rel} 寫哪裡把非正本 7-review*.md 當寫入目標"
                )
                break
        do_body = sections.get("做什麼", "")
        token = f"--write-cursor {node_id}"
        if token not in do_body:
            failures.append(f"P0 {rel} 做什麼必須呼叫 --write-cursor {node_id}")
        read_body = sections.get("讀什麼", "")
        if node_id == "N0-role":
            if "Self-Review" not in read_body or not re.search(r"禁", read_body):
                failures.append(
                    f"P0 {rel} 讀什麼必須禁讀 6-notes Self-Review"
                )
            if "限制聲明" not in text:
                failures.append(
                    f"P0 {rel} 必須寫明 owner 自審無限制聲明節視同未審"
                )
        if node_id in REVIEW_ALLOWED_NODES:
            if "7-review.md" not in write_body:
                failures.append(f"P0 {rel} 寫哪裡必須點名 7-review.md")
            if not re.search(r"覆寫|不另存", write_body):
                failures.append(f"P0 {rel} 寫哪裡必須宣告覆寫同一檔、不另存")
            if re.search(r"7-review\*\.md|第二份", write_body):
                if not re.search(r"禁止|不得|禁", write_body):
                    failures.append(f"P0 {rel} 必須禁止第二份 7-review*.md")
        if node_id == WRITE_REVIEW_NODE:
            if "6-implementation-notes" not in read_body and "6-notes" not in read_body:
                failures.append(f"P0 {rel} 讀什麼必須點名 6-notes(步 4 才准讀)")
            if "review-unlock" not in read_body:
                failures.append(f"P0 {rel} 讀什麼必須點名 review-unlock")
        if node_id.startswith("S2"):
            if "Self-Review" not in read_body or not re.search(r"禁", read_body):
                failures.append(
                    f"P0 {rel} 讀什麼必須禁讀 6-notes Self-Review"
                )
        if node_id == INTEGRATION_NODE:
            if INTEGRATION_SCRIPT not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須點名現有 {INTEGRATION_SCRIPT},"
                    f"不准另寫整合回歸工具"
                )
            if "Final Fresh" not in do_body or "前" not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須寫明整合回歸在 Final Fresh 之前"
                )
        if node_id == FRESH_NODE:
            if GAUNTLET_SCRIPT not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須點名現有 {GAUNTLET_SCRIPT},"
                    f"不准另寫 Gauntlet"
                )
            if "SHA" not in do_body and "HEAD" not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須寫明 Final Fresh 綁 SHA／HEAD"
                )
        if node_id == "N5-verdict":
            if "G3" not in do_body:
                failures.append(
                    f"P0 {rel} 做什麼必須點名現有 G3,不准另寫通過條件"
                )

    if graph is None:
        failures.append(
            "P0 舊實作缺 N4-author —— 第一刀必須有寫檔節點,不要只做 handoff"
        )
        failures.append(
            "P0 舊實作無法證明同 slug 第二份 7-review*.md 會被擋"
        )
        failures.append(
            "P0 舊實作沒有 N4 覆寫契約,無法證明 write_mode≠overwrite 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明未過 G2(4-spec 不是 approved)卻 write_review"
            "（寫 7-review.md）會被擋"
        )
        failures.append(
            "P0 舊實作無法證明審查期 write_notes(改寫 6-notes)會被擋"
        )
        failures.append(
            "P0 舊實作無法證明 7-self-review.md／7-review-*.md 會被擋"
        )
        failures.append(
            "P0 舊實作無法證明 N0 讀 6-notes Self-Review 會被擋"
        )
        failures.extend(scan_live_review_dupes())
        failures.extend(scan_g2_entry_block())
        failures.extend(scan_owner_self_review())
        return failures

    for node_id in REVIEW_ALLOWED_NODES:
        spec = nodes.get(node_id) or {}
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
        if found != ["7-review.md"]:
            failures.append(
                f"P0 模擬重跑 {node_id} 後 7-review*.md = {found},"
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
        allow = set(as_list(spec.get("allow")))
        if node_id in REVIEW_ALLOWED_NODES:
            if "write_review" not in allow:
                failures.append(
                    f"P0 {node_id} 必須 allow write_review"
                    "(同一份 7-review.md,overwrite)"
                )
        elif "write_review" in allow:
            failures.append(f"P0 {node_id} 不得 allow write_review")
        if node_id == WRITE_REVIEW_NODE:
            if "read_notes" not in allow:
                failures.append(
                    "P0 N4-author 必須 allow read_notes"
                    "(N4 才准讀 6-notes,對應 review-unlock)"
                )
        elif "read_notes" in allow:
            failures.append(f"P0 {node_id} 不得 allow read_notes")
        if node_id in REVIEW_FORBIDDEN_NODES and "write_review" in allow:
            failures.append(f"P0 {node_id} 不得放寬 write_review")
        if "write_notes" in allow:
            failures.append(
                f"P0 {node_id} 不得 allow write_notes —— "
                f"審查期不准改寫 6-implementation-notes.md"
            )

    unknown = [n for n in nodes if n not in CHAIN]
    if unknown:
        failures.append(
            f"P0 graph.yaml 有鏈外節點:{sorted(unknown)} —— 鏈必須剛好是 "
            + " → ".join(CHAIN)
        )
    check_chain(nodes, failures)
    failures.extend(scan_live_review_dupes())
    failures.extend(scan_g2_entry_block())
    failures.extend(scan_owner_self_review())
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
            if "check-devstage7-graph" in code and "--action" in code:
                return []
    return [
        "P0 --action 沒接到 runtime:hooks 沒有呼叫 check-devstage7-graph.sh --action"
    ]


def check_guide():
    """第 7 站開頭對上十節點鏈;舊句「還在單一 SKILL」必須紅。"""
    if not os.path.isfile(GUIDE_PATH):
        return []
    text = open(GUIDE_PATH, encoding="utf-8").read()
    failures = []
    if STALE_GUIDE in text:
        failures.append(f"P0 guide 出現「{STALE_GUIDE}」")
    match = re.search(r'<h3 id="stage7">.*?(?=<h3 |\Z)', text, re.S)
    if not match:
        failures.append('P0 guide 找不到第 7 站 <h3 id="stage7">')
        return failures
    head = match.group(0)[:2500]
    missing = [node_id for node_id in CHAIN if node_id not in head]
    if missing:
        failures.append("P0 guide 第 7 站開頭缺節點:" + ",".join(missing))
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

print("✅ PASS:Stage 7 graph 十真節點 / 無 skill-legacy 團塊 / 單產物 7-review.md / 覆寫 / 整合回歸在 Fresh 前 / N4 才讀 6-notes / prebash / guide 全過")
sys.exit(0)
PY
