#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""圖表 IR 閘 — wave-1 正式入口。

驗證信封 → 收據 → 通過後才 atomic_write。
正式 CLI:`python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET`
`python3 scripts/diagir.py route` 印五列查找表。

docs/dev/diagram-ir-gate/proto/diagir_gate.py 只對照形狀,不是 ship。
不得 import Archify／mermaid／Node;不得猜 family。
"""
from __future__ import print_function

import importlib.util
import json
import os
import sys

from devflow_atomic import atomic_write

# Q6 旋鈕句(與 Stage 3 proto 對照形狀;碼名鎖定 DIAGIR_*)
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
RECEIPT_KEYS = ("ok", "code", "knob", "abort", "delivered", "target_replaced")

ROUTE = [
    {
        "id": "stage1-now",
        "use": "第 1 站審頁 #scan-now 直式三框",
        "dont": "掃頁 build-scan-html.py；vbox-fig 生命週期四格；gate-twin 五格",
        "builder": "build-stage1-html.py --action",
        "contract": "notes/design/stage1-review-ui-contract.md",
    },
    {
        "id": "stage2-arch",
        "use": "第 2 站審頁 Decision 後直式 [標籤] 標題 SVG",
        "dont": "橫 ASCII；<pre> 當圖；手包 html-shell；生命週期四格",
        "builder": "build-stage2-html.py --action",
        "contract": "notes/design/stage2-review-ui-contract.md + vbox 母版",
    },
    {
        "id": "behavior-flow",
        "use": "gate-twin 行為流程；樹狀改 WARNING+<pre>",
        "dont": "樹收成單盒 vbox；生命週期四格充行為流",
        "builder": "build-gate-twin.py",
        "contract": "vbox-fig-contract（twin 收口）",
    },
    {
        "id": "dir-tree",
        "use": "手寫 YAML why；產品 dir-tree.html",
        "dont": "掃 repo 猜 why；收成單盒 vbox；跟第 1 站三框搶槽",
        "builder": "build-dir-tree.py",
        "contract": "notes/design/dir-tree-contract.md",
    },
    {
        "id": "vbox-lifecycle",
        "use": "四格固定：新生 → 改行為 → 退役 → 不動",
        "dont": "第五格／parked；第 1 站三框；七站三走廊",
        "builder": "build-vbox-fig.py lifecycle",
        "contract": "notes/design/vbox-fig-contract.md",
    },
]
ROUTE_IDS = set(row["id"] for row in ROUTE)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def eprint(*parts):
    sys.stderr.write(" ".join(str(p) for p in parts) + "\n")


def public_receipt(result):
    out = {}
    for key in RECEIPT_KEYS:
        out[key] = result.get(key)
    return out


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
    if isinstance(text, str) and ("|--" in text or "|---" in text or "├" in text or "└" in text):
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
    if "family" not in envelope:
        return fail("DIAGIR_FAMILY", "missing-family")
    family = envelope.get("family")
    payload = envelope.get("payload")
    if family not in ROUTE_IDS:
        return fail("DIAGIR_FAMILY", "unknown-family")
    if not isinstance(payload, dict):
        return fail("DIAGIR_EMPTY", "payload-not-object")

    if family == "dir-tree":
        if looks_like_stage1(payload) or payload_kind(payload) in ("vbox", "lifecycle"):
            return fail("DIAGIR_FAMILY", "dir-tree-payload-is-vbox-or-stage1")
        root = payload.get("root") or payload
        problems = []
        walk_dir_whys(root, problems)
        if problems:
            return fail("DIAGIR_WHY", "short-or-missing-why:" + ",".join(problems))
        return {"ok": True, "family": family, "code": None}

    if family == "stage1-now":
        if looks_like_tree(payload):
            return fail("DIAGIR_FAMILY", "tree-as-stage1")
        if payload_kind(payload) in ("lifecycle", "vbox") and len(payload.get("steps") or []) == 4:
            return fail("DIAGIR_FAMILY", "lifecycle-as-stage1")
        if not looks_like_stage1(payload) and payload_kind(payload) not in (None, "stage1-now"):
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


def _vbox_mod():
    path = os.path.join(_SCRIPT_DIR, "build-vbox-fig.py")
    spec = importlib.util.spec_from_file_location("_diagir_vbox_fig", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render_payload(family, payload):
    steps = payload.get("steps") if isinstance(payload, dict) else None
    if steps and family in ("vbox-lifecycle", "stage2-arch", "behavior-flow"):
        mod = _vbox_mod()
        aria = payload.get("aria") or ""
        return mod.render_svg(aria, mod.normalize(steps))
    # 其餘家族 CLI 交付仍是靜態直式 SVG,不含 mermaid／動畫
    label = family or "diagir"
    return (
        '<svg viewBox="0 0 280 80" role="img" aria-label="%s">'
        '<rect x="40" y="10" width="200" height="60" rx="6" fill="#e8edf8"/>'
        '<text x="140" y="46" text-anchor="middle" '
        'font-size="14">IR OK static</text></svg>\n' % label
    )


def deliver(envelope, out_path, rendered=None):
    existed = os.path.isfile(out_path)
    before = None
    if existed:
        with open(out_path, "rb") as handle:
            before = handle.read()
    result = validate(envelope)
    if not result.get("ok"):
        after = None
        if os.path.isfile(out_path):
            with open(out_path, "rb") as handle:
                after = handle.read()
        result["target_unchanged"] = before == after
        return result
    text = rendered if rendered is not None else render_payload(
        envelope.get("family"), envelope.get("payload") or {}
    )
    atomic_write(out_path, text)
    result["ok"] = True
    result["code"] = None
    result["knob"] = None
    result["abort"] = None
    result["delivered"] = True
    result["target_replaced"] = True
    return result


def write_via_gate(path, text, family, payload):
    """產器接線:先 validate,通過才 atomic_write。失敗不覆寫。"""
    result = deliver({"family": family, "payload": payload}, str(path), rendered=text)
    if not result.get("ok"):
        raise SystemExit(1)
    return result


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.loads(handle.read())


def print_route():
    print("ROUTE_ROWS %d" % len(ROUTE))
    for row in ROUTE:
        print(
            "ROUTE\t%(id)s\tuse=%(use)s\tdont=%(dont)s\t"
            "builder=%(builder)s\tcontract=%(contract)s" % row
        )


def usage():
    eprint(
        "用法: python3 scripts/diagir.py deliver ENVELOPE.json --out TARGET\n"
        "     python3 scripts/diagir.py route\n"
        "     python3 scripts/diagir.py validate ENVELOPE.json"
    )
    return 2


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        return usage()
    cmd = argv[0]
    if cmd == "route":
        print_route()
        return 0
    if cmd == "validate":
        if len(argv) < 2:
            return usage()
        result = validate(load_json(argv[1]))
        print(json.dumps(public_receipt(result), ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    if cmd == "deliver":
        out = None
        path = None
        i = 1
        while i < len(argv):
            if argv[i] == "--out" and i + 1 < len(argv):
                out = argv[i + 1]
                i += 2
                continue
            path = argv[i]
            i += 1
        if not path or not out:
            return usage()
        result = deliver(load_json(path), out)
        print(json.dumps(public_receipt(result), ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    return usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
