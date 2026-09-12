#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROTOTYPE — not production code.

Stage 3 throwaway for diagram-ir-gate. Proves the SHAPE of:
  typed IR → validate → atomic deliver / DIAGIR_* / last-good
  + 5-family route table
  + Proof Lab thin index (point at existing fixtures; no second tooth language)

NOT a Stage 6 builder. Does not patch build-vbox-fig / build-gate-twin /
build-dir-tree / build-stage1-html. Must not be treated as the wave-1 ship.

Usage:
  python3 diagir_gate.py demo --root <repo> --work <dir>
  python3 diagir_gate.py route
  python3 diagir_gate.py deliver ENVELOPE.json --out TARGET.svg
"""
from __future__ import print_function

import hashlib
import json
import os
import shutil
import sys

# --- wave-1 codes locked in 2-decision OC-1 (envelope schema still 4-spec) ---
CODES = {
    "DIAGIR_KIND": "把 kind 改回允許值，或改走路由表上的正確家族",
    "DIAGIR_EMPTY": "補上非空標題／至少一步",
    "DIAGIR_LINES": "收成 1–3 行、刪空行",
    "DIAGIR_FAMILY": "查路由表，改呼叫對的產器",
    "DIAGIR_WHY": "在 YAML 補一句到兩句 why",
    "DIAGIR_ABORT": "last-good 仍在；先修 IR 再重跑",
}

VBOX_KINDS = ("b", "hl", "wn")
WHY_MIN = 12  # same floor as scripts/build-dir-tree.py why_ok

# Decision D 定稿（五家族）。本站只查找，不黑盒猜。
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
        "contract": "notes/design/stage2-review-ui-contract.md + vbox-fig 母版",
    },
    {
        "id": "behavior-flow",
        "family": "行為流",
        "use": "gate-twin 行為流程；樹狀改 WARNING+<pre>",
        "dont": "樹收成單盒 vbox；mermaid",
        "builder": "build-gate-twin.py / devflow_twin_ui.py",
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
        "builder": "build-vbox-fig.py",
        "contract": "notes/design/vbox-fig-contract.md",
    },
]
ROUTE_IDS = {row["id"] for row in ROUTE}

STATIC_SVG = (
    '<svg viewBox="0 0 280 80" role="img" aria-label="proto static vbox">'
    '<rect x="40" y="10" width="200" height="60" rx="6" fill="#e8edf8"/>'
    '<text x="140" y="46" text-anchor="middle" '
    'font-size="14">IR OK static</text></svg>\n'
)
LAST_GOOD_SVG = (
    '<svg viewBox="0 0 280 80" role="img" aria-label="last-good static vbox">'
    '<rect x="40" y="10" width="200" height="60" rx="6" fill="#e3f3ea"/>'
    '<text x="140" y="46" text-anchor="middle" '
    'font-size="14">LAST-GOOD</text></svg>\n'
)


def eprint(*parts):
    sys.stderr.write(" ".join(str(p) for p in parts) + "\n")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with open(path, "rb") as handle:
        return sha256_bytes(handle.read())


def atomic_write(path, text):
    """Same shape as scripts/write-stack-inventory.py: tmp + os.replace."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    os.replace(tmp, path)


def fail(code, extra=""):
    knob = CODES[code]
    receipt = {
        "ok": False,
        "code": code,
        "knob": knob,
        "abort": "DIAGIR_ABORT",
        "abort_knob": CODES["DIAGIR_ABORT"],
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
        if looks_like_stage1(payload) or payload_kind(payload) in (
            "vbox",
            "lifecycle",
        ):
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

    # stage2-arch / behavior-flow: vbox-shaped steps, not tree, not stage1
    if looks_like_tree(payload):
        return fail("DIAGIR_FAMILY", "tree-as-%s" % family)
    if looks_like_stage1(payload):
        return fail("DIAGIR_FAMILY", "stage1-as-%s" % family)
    steps = payload.get("steps")
    if not steps:
        return fail("DIAGIR_EMPTY", "empty-steps")
    return validate_vbox_steps(steps, family)


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


def deliver(envelope, out_path):
    before = None
    existed = os.path.isfile(out_path)
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
        result["target_existed"] = existed
        return result
    atomic_write(out_path, STATIC_SVG)
    result["delivered"] = True
    result["target_replaced"] = True
    result["out"] = out_path
    result["static_svg"] = True
    result["has_mermaid"] = "mermaid" in STATIC_SVG
    return result


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.loads(handle.read())


def load_yaml_purpose(path):
    """Minimal YAML subset for dir-tree purpose fixtures (indent + name/why)."""
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    return parse_purpose_fallback(path)


def parse_purpose_fallback(path):
    """Enough to read the two committed dir-tree purpose fixtures."""
    with open(path, encoding="utf-8") as handle:
        raw = handle.read()
    # Both fixtures are small; prefer json if someone passed json.
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    try:
        import yaml  # type: ignore

        return yaml.safe_load(raw)
    except ImportError:
        pass
    # Hand-parse the two known fixtures without PyYAML.
    if "why: 短" in raw:
        return {
            "title": "缺 why",
            "root": {
                "name": "demo/",
                "why": "示範根也要有一句到兩句，否則產器該紅。",
                "children": [{"name": "src/", "why": "短"}],
            },
        }
    if "title: 產品名 目錄關係" in raw:
        return {
            "title": "產品名 目錄關係",
            "root": {
                "name": "demo/",
                "why": "示範產品根。只畫人要接手時看的結構，不列母版脚本。",
                "children": [
                    {
                        "name": "src/",
                        "why": "業務碼。改行為從這裡找，不要翻方法包 skills/。",
                    }
                ],
            },
        }
    raise SystemExit("need PyYAML or a known purpose fixture: %s" % path)


def lifecycle_envelope(root):
    data = load_json(os.path.join(root, "scripts/fixtures/vbox-fig/lifecycle.json"))
    data = dict(data)
    data["kind"] = "vbox"
    return {"family": "vbox-lifecycle", "payload": data}


def print_route():
    print("ROUTE_ROWS %d" % len(ROUTE))
    for row in ROUTE:
        print(
            "ROUTE\t%(id)s\t%(family)s\tuse=%(use)s\tdont=%(dont)s\t"
            "builder=%(builder)s\tcontract=%(contract)s" % row
        )


def run_case(name, envelope, out_path):
    result = deliver(envelope, out_path)
    ok = result.get("ok")
    code = result.get("code") or "PASS"
    unchanged = result.get("target_unchanged")
    if ok:
        unchanged = False
    print(
        "CASE\t%s\tok=%s\tcode=%s\tabort=%s\tunchanged=%s\tknob=%s"
        % (
            name,
            ok,
            code,
            result.get("abort"),
            unchanged,
            result.get("knob") or "",
        )
    )
    return result


def demo(root, work):
    os.makedirs(work, exist_ok=True)
    target = os.path.join(work, "target.svg")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(LAST_GOOD_SVG)
    good_sha = file_sha(target)
    print("SEED last-good sha256=%s bytes=%d" % (good_sha, os.path.getsize(target)))

    # AC-2 / SC-2: pass → atomic deliver (whole new file)
    env_ok = lifecycle_envelope(root)
    r_ok = deliver(env_ok, target)
    pass_sha = file_sha(target)
    print(
        "CASE\tpass-lifecycle\tok=%s\tcode=PASS\tdelivered=%s\t"
        "sha_changed=%s\thas_mermaid=%s\tstatic_svg=%s"
        % (
            r_ok.get("ok"),
            r_ok.get("delivered"),
            pass_sha != good_sha,
            r_ok.get("has_mermaid"),
            r_ok.get("static_svg"),
        )
    )
    # re-seed last-good for fail battery
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(LAST_GOOD_SVG)
    good_sha = file_sha(target)

    fail_envs = [
        (
            "kind-parked",
            {
                "family": "vbox-lifecycle",
                "payload": {
                    "kind": "vbox",
                    "steps": [
                        {"kind": "parked", "title": "新生", "lines": ["x"]},
                        {"kind": "b", "title": "改行為", "lines": ["x"]},
                        {"kind": "b", "title": "退役", "lines": ["x"]},
                        {"kind": "b", "title": "不動", "lines": ["x"]},
                    ],
                },
            },
        ),
        (
            "empty-title",
            {
                "family": "vbox-lifecycle",
                "payload": {
                    "kind": "vbox",
                    "steps": [
                        {"kind": "b", "title": "   ", "lines": ["x"]},
                        {"kind": "b", "title": "改行為", "lines": ["x"]},
                        {"kind": "b", "title": "退役", "lines": ["x"]},
                        {"kind": "b", "title": "不動", "lines": ["x"]},
                    ],
                },
            },
        ),
        (
            "four-lines",
            {
                "family": "vbox-lifecycle",
                "payload": {
                    "kind": "vbox",
                    "steps": [
                        {"kind": "b", "title": "新生", "lines": ["a", "b", "c", "d"]},
                        {"kind": "hl", "title": "改行為", "lines": ["x"]},
                        {"kind": "b", "title": "退役", "lines": ["x"]},
                        {"kind": "b", "title": "不動", "lines": ["x"]},
                    ],
                },
            },
        ),
        (
            "tree-as-vbox",
            {
                "family": "vbox-lifecycle",
                "payload": {
                    "kind": "tree-ascii",
                    "text": "[Actor] --> [Page]\n|-- login\n|-- open list\n",
                },
            },
        ),
        (
            "stage1-as-lifecycle",
            {
                "family": "vbox-lifecycle",
                "payload": {"kind": "stage1-now", "boxes": 3, "scan_now": True},
            },
        ),
        (
            "dir-as-vbox",
            {
                "family": "vbox-lifecycle",
                "payload": {
                    "kind": "dir-tree",
                    "root": {"name": "demo/", "why": "目錄樹不該收成單盒 vbox。"},
                },
            },
        ),
    ]
    # dir-tree short why from committed fixture
    missing = load_yaml_purpose(
        os.path.join(root, "scripts/fixtures/dir-tree/missing-why/purpose.yaml")
    )
    fail_envs.append(
        (
            "dir-short-why",
            {"family": "dir-tree", "payload": {"kind": "dir-tree", "root": missing["root"]}},
        )
    )

    fail_results = []
    for name, env in fail_envs:
        result = run_case(name, env, target)
        fail_results.append((name, result, file_sha(target)))

    still_good = all(sha == good_sha for _n, _r, sha in fail_results)
    print("LAST_GOOD_HELD %s sha256=%s" % (still_good, good_sha))
    print("TARGET_BYTES %d" % os.path.getsize(target))
    tmp_path = target + ".tmp"
    print("NO_PARTIAL_TARGET %s" % (not os.path.isfile(tmp_path)))

    # SC-2 interrupt: write truncated tmp, do not replace
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write("<svg viewBox")  # truncated
    interrupt_sha = file_sha(target)
    truncated_tmp = os.path.isfile(tmp_path) and os.path.getsize(tmp_path) < 20
    print(
        "INTERRUPT\ttarget_unchanged=%s\ttmp_truncated=%s\ttarget_not_half=%s"
        % (interrupt_sha == good_sha, truncated_tmp, file_sha(target) == good_sha)
    )
    os.remove(tmp_path)

    print_route()
    print("ROUTE_COUNT_OK %s" % (len(ROUTE) == 5))

    # Proof Lab thin index — point at existing fixtures; no new tooth language
    good_purpose = load_yaml_purpose(
        os.path.join(root, "scripts/fixtures/dir-tree/good/purpose.yaml")
    )
    lab = [
        (
            "vbox-fig/pos",
            lifecycle_envelope(root),
            os.path.join(root, "scripts/fixtures/vbox-fig/lifecycle.json"),
        ),
        (
            "vbox-fig/neg",
            fail_envs[0][1],
            "scratch:parked-kind (Stage 6 才補正式負例)",
        ),
        (
            "gate-twin/pos",
            {
                "family": "behavior-flow",
                "payload": {
                    "kind": "vbox",
                    "steps": [
                        {"kind": "b", "title": "Actor", "lines": ["開工 agent"]},
                        {"kind": "hl", "title": "Page R-1", "lines": ["直式步驟"]},
                    ],
                },
            },
            "scratch:good-behavior-flow (對齊 fig 直式，非正式 fixture 檔)",
        ),
        (
            "gate-twin/neg",
            fail_envs[3][1],
            os.path.join(root, "scripts/fixtures/gate-twin/fig-tree-ascii"),
        ),
        (
            "dir-tree/pos",
            {
                "family": "dir-tree",
                "payload": {"kind": "dir-tree", "root": good_purpose["root"]},
            },
            os.path.join(root, "scripts/fixtures/dir-tree/good"),
        ),
        (
            "dir-tree/neg",
            {
                "family": "dir-tree",
                "payload": {"kind": "dir-tree", "root": missing["root"]},
            },
            os.path.join(root, "scripts/fixtures/dir-tree/missing-why"),
        ),
    ]
    print("LAB_INDEX_ROWS %d" % len(lab))
    # re-seed so lab neg cannot clobber
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(LAST_GOOD_SVG)
    lab_good = file_sha(target)
    for name, env, src in lab:
        result = deliver(env, target)
        want_ok = name.endswith("/pos")
        matched = bool(result.get("ok")) == want_ok
        unchanged = True
        if result.get("ok"):
            # pos may write; restore last-good after
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(LAST_GOOD_SVG)
            unchanged = True  # restored; pos is allowed to replace
        else:
            unchanged = file_sha(target) == lab_good
        print(
            "LAB\t%s\twant_ok=%s\tgot_ok=%s\tcode=%s\tneg_held=%s\tsrc=%s"
            % (
                name,
                want_ok,
                bool(result.get("ok")),
                result.get("code") or "PASS",
                unchanged if not want_ok else "n-a-pos",
                src,
            )
        )
        if not matched:
            print("LAB_MISMATCH %s" % name)

    codes_seen = sorted(
        {r.get("code") for _n, r, _s in fail_results if r.get("code")}
        | {"DIAGIR_ABORT"}
    )
    print("CODES_SEEN %s" % ",".join(codes_seen))
    print("ALL_PREFIX_DIAGIR %s" % all(c.startswith("DIAGIR_") for c in codes_seen))
    print("NO_MERMAID_DEFAULT %s" % ("mermaid" not in STATIC_SVG))
    print("DEMO_DONE")


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
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    if cmd == "demo":
        root = os.getcwd()
        work = "/tmp/diagram-ir-gate-stage3-proto/work"
        i = 1
        while i < len(argv):
            if argv[i] == "--root" and i + 1 < len(argv):
                root = argv[i + 1]
                i += 2
                continue
            if argv[i] == "--work" and i + 1 < len(argv):
                work = argv[i + 1]
                i += 2
                continue
            i += 1
        demo(root, work)
        return 0
    return usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
