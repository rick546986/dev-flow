#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave-1 diagram IR gate — validate then atomic deliver.

Formal entry (not the Stage 3 proto):
  python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET
  python3 scripts/diagir.py route

Request keys: family + payload only.
Receipt keys: ok / code / knob / abort / delivered / target_replaced.
"""
from __future__ import print_function

import html
import json
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from devflow_atomic import atomic_write  # noqa: E402

CODES = {
    "DIAGIR_KIND": "把 kind 改回允許值，或改走路由表上的正確家族",
    "DIAGIR_EMPTY": "補上非空標題／至少一步",
    "DIAGIR_LINES": "收成 1–3 行、刪空行",
    "DIAGIR_FAMILY": "查路由表，改呼叫對的產器",
    "DIAGIR_WHY": "在 YAML 補一句到兩句 why",
    "DIAGIR_ABORT": "last-good 仍在；先修 IR 再重跑",
}

VBOX_KINDS = ("b", "hl", "wn")
WHY_MIN = 12

ROUTE = [
    {
        "id": "stage1-now",
        "family": "Stage1 現況三框",
        "use": "第 1 站審頁 #scan-now 直式三框",
        "dont": "掃頁 build-scan-html.py；vbox-fig 生命週期四格；gate-twin 五格",
        "builder": "build-stage1-html.py --action",
        "contract": "notes/design/stage1-review-ui-contract.md",
    },
    {
        "id": "stage2-arch",
        "family": "Stage2 方案架構",
        "use": "第 2 站審頁 Decision 後直式 [標籤] 標題 SVG",
        "dont": "mermaid；橫 ASCII；<pre> 當圖；手包 html-shell",
        "builder": "build-stage2-html.py --action",
        "contract": "notes/design/stage2-review-ui-contract.md + vbox 母版",
    },
    {
        "id": "behavior-flow",
        "family": "行為流",
        "use": "gate-twin 行為流程；樹狀改 WARNING+<pre>",
        "dont": "樹收成單盒 vbox；mermaid",
        "builder": "build-gate-twin.py",
        "contract": "vbox-fig-contract（twin 收口）",
    },
    {
        "id": "dir-tree",
        "family": "目錄樹",
        "use": "手寫 YAML why；產品 dir-tree.html",
        "dont": "掃 repo 猜 why；收成單盒 vbox；跟第 1 站三框搶槽",
        "builder": "build-dir-tree.py",
        "contract": "notes/design/dir-tree-contract.md",
    },
    {
        "id": "vbox-lifecycle",
        "family": "模組生命週期",
        "use": "四格固定：新生 → 改行為 → 退役 → 不動",
        "dont": "第五格／parked；第 1 站三框；七站三走廊",
        "builder": "build-vbox-fig.py lifecycle",
        "contract": "notes/design/vbox-fig-contract.md",
    },
]
ROUTE_IDS = set(row["id"] for row in ROUTE)


def eprint(*parts):
    sys.stderr.write(" ".join(str(p) for p in parts) + "\n")


def fail(code, extra=""):
    knob = CODES[code]
    receipt = {
        "ok": False,
        "code": code,
        "knob": knob,
        "abort": "DIAGIR_ABORT",
        "delivered": False,
        "target_replaced": False,
    }
    if extra:
        receipt["detail"] = extra
    eprint("FAIL", code, "| knob:", knob)
    eprint("FAIL", "DIAGIR_ABORT", "| knob:", CODES["DIAGIR_ABORT"])
    return receipt


def payload_kind(payload):
    if not isinstance(payload, dict):
        return None
    return payload.get("kind") or payload.get("shape")


def looks_like_tree(payload):
    kind = payload_kind(payload)
    if kind in ("tree", "tree-ascii", "dir-tree"):
        return True
    text = payload.get("text") if isinstance(payload, dict) else ""
    if isinstance(text, str) and ("|--" in text or "├" in text or "└" in text):
        return True
    return False


def looks_like_stage1(payload):
    kind = payload_kind(payload)
    if kind in ("stage1-now", "scan-now", "three-box"):
        return True
    boxes = payload.get("boxes") if isinstance(payload, dict) else None
    return boxes == 3 or payload.get("scan_now") is True


def why_ok(why):
    return isinstance(why, str) and len(why.strip()) >= WHY_MIN


def walk_dir_whys(node, problems):
    if not isinstance(node, dict):
        problems.append("node-not-object")
        return
    name = node.get("name", "?")
    if not why_ok(node.get("why")):
        problems.append(name)
    for child in node.get("children") or []:
        walk_dir_whys(child, problems)


def validate_vbox_steps(steps, family):
    for i, item in enumerate(steps):
        if not isinstance(item, dict):
            return fail("DIAGIR_EMPTY", "step-%d-not-object" % (i + 1))
        kind = item.get("kind")
        title = item.get("title")
        lines = item.get("lines")
        if kind not in VBOX_KINDS:
            return fail("DIAGIR_KIND", "step-%d-kind=%s" % (i + 1, kind))
        if not isinstance(title, str) or not title.strip():
            return fail("DIAGIR_EMPTY", "step-%d-empty-title" % (i + 1))
        if not isinstance(lines, list) or not (1 <= len(lines) <= 3):
            return fail("DIAGIR_LINES", "step-%d-lines-count" % (i + 1))
        for line in lines:
            if not isinstance(line, str) or not line.strip():
                return fail("DIAGIR_LINES", "step-%d-empty-line" % (i + 1))
    return {"ok": True, "family": family, "code": None}


def validate(envelope):
    if not isinstance(envelope, dict):
        return fail("DIAGIR_FAMILY", "envelope-not-object")
    family = envelope.get("family")
    payload = envelope.get("payload")
    if family not in ROUTE_IDS:
        return fail("DIAGIR_FAMILY", "unknown-family:%s" % family)
    if not isinstance(payload, dict):
        return fail("DIAGIR_EMPTY", "payload-not-object")

    if family == "dir-tree":
        if looks_like_stage1(payload) or payload_kind(payload) in ("vbox", "lifecycle"):
            return fail("DIAGIR_FAMILY", "dir-tree-payload-is-vbox-or-stage1")
        if payload_kind(payload) not in (None, "dir-tree"):
            if looks_like_tree(payload) and payload_kind(payload) != "dir-tree":
                return fail("DIAGIR_FAMILY", "tree-sent-as-%s" % payload_kind(payload))
        root = payload.get("root") or payload
        problems = []
        walk_dir_whys(root, problems)
        if problems:
            return fail("DIAGIR_WHY", "short-or-missing-why:" + ",".join(problems))
        return {"ok": True, "family": family, "code": None}

    if family == "stage1-now":
        if looks_like_tree(payload):
            return fail("DIAGIR_FAMILY", "tree-as-stage1")
        if payload_kind(payload) in ("lifecycle", "vbox") and payload.get("steps"):
            if len(payload.get("steps") or []) == 4:
                return fail("DIAGIR_FAMILY", "lifecycle-as-stage1")
        if not looks_like_stage1(payload) and payload_kind(payload) not in (
            None,
            "stage1-now",
        ):
            return fail("DIAGIR_FAMILY", "stage1-kind-mismatch")
        return {"ok": True, "family": family, "code": None}

    if family == "vbox-lifecycle":
        if looks_like_tree(payload):
            return fail("DIAGIR_FAMILY", "tree-as-vbox")
        if looks_like_stage1(payload):
            return fail("DIAGIR_FAMILY", "stage1-as-lifecycle")
        steps = payload.get("steps")
        if not steps:
            return fail("DIAGIR_EMPTY", "empty-steps")
        if len(steps) != 4:
            return fail("DIAGIR_FAMILY", "lifecycle-must-be-four-cells")
        return validate_vbox_steps(steps, family)

    if looks_like_tree(payload):
        return fail("DIAGIR_FAMILY", "tree-as-%s" % family)
    if looks_like_stage1(payload):
        return fail("DIAGIR_FAMILY", "stage1-as-%s" % family)
    steps = payload.get("steps")
    if not steps:
        return fail("DIAGIR_EMPTY", "empty-steps")
    return validate_vbox_steps(steps, family)


def render_static_svg(payload):
    steps = payload.get("steps") if isinstance(payload, dict) else None
    titles = []
    for item in steps or []:
        if isinstance(item, dict) and item.get("title"):
            titles.append(str(item.get("title")))
    label = html.escape(" / ".join(titles) or "IR OK static", quote=True)
    return (
        '<svg viewBox="0 0 280 80" role="img" aria-label="diagir static">'
        '<rect x="40" y="10" width="200" height="60" rx="6" fill="#e8edf8"/>'
        '<text x="140" y="46" text-anchor="middle" font-size="14">%s</text>'
        "</svg>\n" % label
    )


def deliver(envelope, out_path, content=None):
    result = validate(envelope)
    if not result.get("ok"):
        return result
    text = content if content is not None else render_static_svg(
        envelope.get("payload") if isinstance(envelope, dict) else {}
    )
    atomic_write(out_path, text)
    result["ok"] = True
    result["code"] = None
    result["knob"] = None
    result["abort"] = None
    result["delivered"] = True
    result["target_replaced"] = True
    return result


def persist_product(path, text, family, payload):
    return deliver({"family": family, "payload": payload}, str(path), content=text)


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.loads(handle.read())


def print_route():
    print("ROUTE_ROWS %d" % len(ROUTE))
    for row in ROUTE:
        print(
            "ROUTE\t%(id)s\t%(family)s\tuse=%(use)s\tdont=%(dont)s\t"
            "builder=%(builder)s\tcontract=%(contract)s" % row
        )


def usage():
    eprint(__doc__)
    return 2


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        return usage()
    cmd = argv[0]
    if cmd == "route":
        print_route()
        return 0
    if cmd == "validate":
        env = load_json(argv[1])
        result = validate(env)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    if cmd == "deliver":
        out = None
        path = None
        content_path = None
        i = 1
        while i < len(argv):
            if argv[i] == "--out" and i + 1 < len(argv):
                out = argv[i + 1]
                i += 2
                continue
            if argv[i] == "--content" and i + 1 < len(argv):
                content_path = argv[i + 1]
                i += 2
                continue
            path = argv[i]
            i += 1
        if not path or not out:
            return usage()
        content = None
        if content_path:
            with open(content_path, encoding="utf-8") as handle:
                content = handle.read()
        result = deliver(load_json(path), out, content=content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    return usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
