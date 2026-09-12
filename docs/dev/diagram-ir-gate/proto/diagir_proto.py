#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROTOTYPE — not production code. Throwaway Stage 3 shape for diagram-ir-gate.

Proves: typed IR → validate → atomic deliver; DIAGIR_* + repair knob;
last-good survives fail/abort; 5-family lookup route table; Proof Lab thin
index over existing fixtures. Does NOT implement Stage 6 builders.
Does NOT replace check-vbox-fig / check-gate-twin / check-dir-tree.

Usage:
  proto/diagir_proto.py routes
  proto/diagir_proto.py deliver --family <row> --ir FILE --out FILE
  proto/diagir_proto.py deliver --family <row> --ir FILE --out FILE --abort-after-tmp
  proto/diagir_proto.py lab --index proto/proof-lab-index.json
  proto/diagir_proto.py demo --workdir DIR
"""
from __future__ import print_function

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROTO_MARK = "PROTOTYPE — not production code"

# Wave-1 route table (Decision D). Lookup, not auto-detect.
ROUTES = (
    {
        "family": "stage1-scan",
        "use": "第 1 站審頁 #scan-now 直式三框",
        "not": "掃頁 build-scan-html.py；vbox-fig 生命週期四格；gate-twin 五格",
        "builder": "build-stage1-html.py --action",
        "contract": "notes/design/stage1-review-ui-contract.md",
    },
    {
        "family": "stage2-arch",
        "use": "第 2 站審頁 Decision 後直式 [標籤] 標題 SVG",
        "not": "mermaid；橫 ASCII；<pre> 當圖；手包 html-shell",
        "builder": "build-stage2-html.py --action",
        "contract": "notes/design/stage2-review-ui-contract.md + vbox-fig",
    },
    {
        "family": "behavior-flow",
        "use": "gate-twin 行為流程；樹狀改 WARNING+<pre>",
        "not": "樹收成單盒 vbox；mermaid",
        "builder": "build-gate-twin.py / devflow_twin_ui.py",
        "contract": "notes/design/vbox-fig-contract.md (twin 收口)",
    },
    {
        "family": "dir-tree",
        "use": "手寫 YAML why；產品 dir-tree.html",
        "not": "掃 repo 猜 why；收成單盒 vbox；跟第 1 站三框搶槽",
        "builder": "build-dir-tree.py",
        "contract": "notes/design/dir-tree-contract.md",
    },
    {
        "family": "lifecycle",
        "use": "四格固定：新生 → 改行為 → 退役 → 不動",
        "not": "第五格／parked；第 1 站三框；七站三走廊",
        "builder": "build-vbox-fig.py",
        "contract": "notes/design/vbox-fig-contract.md",
    },
)
FAMILY_SET = {row["family"] for row in ROUTES}
VBOX_FAMILIES = {"stage1-scan", "stage2-arch", "behavior-flow", "lifecycle"}
KINDS = ("b", "hl", "wn")
TREE_MARK = re.compile(r"[|├└]|--")
WHY_MIN = 4
KNOBS = {
    "DIAGIR_KIND": "把 kind 改回允許值，或改走路由表上的正確家族",
    "DIAGIR_EMPTY": "補上非空標題／至少一步",
    "DIAGIR_LINES": "收成 1–3 行、刪空行",
    "DIAGIR_FAMILY": "查路由表，改呼叫對的產器",
    "DIAGIR_WHY": "在 YAML 補一句到兩句 why",
    "DIAGIR_ABORT": "last-good 仍在；先修 IR 再重跑",
}


class Fail(Exception):
    def __init__(self, code, detail=""):
        self.code = code
        self.detail = detail
        Exception.__init__(self, code)


def die(code, detail="", rc=1):
    knob = KNOBS.get(code, "")
    sys.stderr.write("%s %s\n" % (code, detail))
    if knob:
        sys.stderr.write("knob: %s\n" % knob)
    sys.exit(rc)


def sha256_file(path):
    if not os.path.isfile(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        digest.update(handle.read())
    return digest.hexdigest()


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


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def looks_like_tree(text):
    return bool(TREE_MARK.search(text or ""))


def wrap_ir(family, payload):
    return {"family": family, "payload": payload}


def adapt_path(path, adapter, family):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if adapter == "vbox-json":
        data = json.loads(text)
        return wrap_ir(family, data)
    if adapter == "tree-ascii":
        return wrap_ir(family, {"raw": text, "tree": True})
    if adapter == "dir-yaml":
        return wrap_ir(family, {"yaml": text})
    if adapter in ("ir-json", "", None):
        data = json.loads(text)
        if "family" in data and "payload" in data:
            return data
        return wrap_ir(family, data)
    raise Fail("DIAGIR_FAMILY", "unknown adapter %s" % adapter)


def validate(family, ir):
    if family not in FAMILY_SET:
        raise Fail("DIAGIR_FAMILY", "route row %s 不在五家族表" % family)
    if not isinstance(ir, dict):
        raise Fail("DIAGIR_FAMILY", "IR 不是物件")
    ir_family = ir.get("family")
    payload = ir.get("payload")
    if ir_family != family:
        raise Fail(
            "DIAGIR_FAMILY",
            "payload 家族 %s ≠ 這次選的路由列 %s" % (ir_family, family),
        )
    if not isinstance(payload, dict):
        raise Fail("DIAGIR_EMPTY", "payload 不是物件")

    raw = payload.get("raw")
    if payload.get("tree") or (isinstance(raw, str) and looks_like_tree(raw)):
        if family != "behavior-flow" or payload.get("tree"):
            # Tree ASCII is not a vbox family. behavior-flow still refuses
            # raw tree-as-vbox (Decision D: 樹收成單盒 vbox).
            raise Fail("DIAGIR_FAMILY", "樹狀 ASCII 不得收成單盒 vbox")

    if family == "dir-tree":
        yaml_text = payload.get("yaml")
        if not isinstance(yaml_text, str):
            raise Fail("DIAGIR_WHY", "dir-tree 缺 YAML 正文")
        whys = re.findall(r"(?m)^\s*why:\s*(.+?)\s*$", yaml_text)
        if not whys:
            raise Fail("DIAGIR_WHY", "dir-tree 缺 why")
        for why in whys:
            why = why.strip().strip("\"'")
            if len(why) < WHY_MIN:
                raise Fail("DIAGIR_WHY", "why 過短: %r" % why)
        return "dir-tree"

    steps = payload.get("steps")
    if family in VBOX_FAMILIES:
        if not steps:
            raise Fail("DIAGIR_EMPTY", "步驟列空")
        if not isinstance(steps, list):
            raise Fail("DIAGIR_EMPTY", "steps 不是陣列")
        for i, item in enumerate(steps):
            if not isinstance(item, dict):
                raise Fail("DIAGIR_EMPTY", "第 %d 步不是物件" % (i + 1))
            kind = item.get("kind")
            title = item.get("title")
            lines = item.get("lines")
            if kind not in KINDS:
                raise Fail(
                    "DIAGIR_KIND",
                    "第 %d 步 kind=%r 只能是 b／hl／wn" % (i + 1, kind),
                )
            if not isinstance(title, str) or not title.strip():
                raise Fail("DIAGIR_EMPTY", "第 %d 步缺標題" % (i + 1))
            if not isinstance(lines, list) or not (1 <= len(lines) <= 3):
                raise Fail("DIAGIR_LINES", "第 %d 步 lines 必須一到三行" % (i + 1))
            for line in lines:
                if not isinstance(line, str) or not line.strip():
                    raise Fail("DIAGIR_LINES", "第 %d 步有空的小字" % (i + 1))
        return "vbox"
    raise Fail("DIAGIR_FAMILY", "未處理家族 %s" % family)


def render_svg(ir):
    """Minimal static vertical SVG. Not mermaid. Not animation. Not Stage 6 builder."""
    payload = ir.get("payload") or {}
    steps = payload.get("steps") or [
        {"kind": "b", "title": ir.get("family", "dir-tree"), "lines": ["why ok"]}
    ]
    box_h = 54
    gap = 22
    top = 10
    height = top + len(steps) * box_h + max(0, len(steps) - 1) * gap + top
    parts = [
        '<!-- %s -->' % PROTO_MARK,
        '<svg viewBox="0 0 280 %d" role="img" aria-label="static-vbox" '
        'style="display:block;max-width:360px;margin:0 auto;height:auto">'
        % height,
    ]
    y = top
    for i, item in enumerate(steps):
        title = (item.get("title") or "")[:24]
        kind = item.get("kind") if item.get("kind") in KINDS else "b"
        fill = {"b": "#ffffff", "hl": "#e8edf8", "wn": "#fbf0dc"}[kind]
        parts.append(
            '<rect class="%s" x="40" y="%d" width="200" height="%d" rx="6" '
            'fill="%s" stroke="#31508f"/>' % (kind, y, box_h, fill)
        )
        parts.append(
            '<text text-anchor="middle" x="140" y="%d" font-size="12">%s</text>'
            % (y + 32, title.replace("&", "&amp;").replace("<", "&lt;"))
        )
        if i < len(steps) - 1:
            parts.append(
                '<path d="M140,%d L140,%d" stroke="#79839a" fill="none"/>'
                % (y + box_h, y + box_h + gap)
            )
        y += box_h + gap
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def cmd_routes(_args):
    print("# family\tuse\tnot\tbuilder\tcontract")
    for row in ROUTES:
        print(
            "%s\t%s\t%s\t%s\t%s"
            % (row["family"], row["use"], row["not"], row["builder"], row["contract"])
        )
    print("count=%d" % len(ROUTES))
    return 0


def deliver(family, ir, out, abort=False):
    validate(family, ir)
    svg = render_svg(ir)
    if "mermaid" in svg or "<animate" in svg:
        raise Fail("DIAGIR_ABORT", "renderer leaked mermaid/animation")
    if abort:
        directory = os.path.dirname(out)
        if directory:
            os.makedirs(directory, exist_ok=True)
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write("PARTIAL")
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise Fail("DIAGIR_ABORT", "寫入未完成；目標未被新內容取代")
    atomic_write(out, svg)
    return svg


def cmd_deliver(args):
    try:
        ir = adapt_path(args.ir, args.adapter, args.family)
        deliver(args.family, ir, args.out, abort=args.abort_after_tmp)
    except Fail as err:
        die(err.code, err.detail)
    print("ok family=%s out=%s" % (args.family, args.out))
    return 0


def run_lab_case(root, case, out_dir):
    family = case["family"]
    path = os.path.join(str(root), case["path"])
    adapter = case.get("adapter") or "ir-json"
    expect = case.get("expect")
    polarity = case["polarity"]
    target = os.path.join(out_dir, family + "-" + polarity + ".svg")
    last_good = os.path.join(out_dir, family + "-last-good.svg")
    if not os.path.isfile(last_good):
        atomic_write(last_good, "LAST-GOOD-%s\n" % family)
        shutil.copy2(last_good, target)
    before = sha256_file(target)
    try:
        ir = adapt_path(path, adapter, family)
        deliver(family, ir, target, abort=False)
        code = None
        rc = 0
    except Fail as err:
        code = err.code
        rc = 1
    after = sha256_file(target)
    if polarity == "pos":
        ok = rc == 0 and after != before and os.path.isfile(target)
        if ok:
            text = pathlib.Path(target).read_text(encoding="utf-8")
            ok = "<svg" in text and "mermaid" not in text and "<animate" not in text
    else:
        ok = rc == 1 and after == before and code == expect
    return {
        "family": family,
        "polarity": polarity,
        "path": case["path"],
        "exit": rc,
        "code": code or "ok",
        "last_good": after == before,
        "ok": ok,
    }


def cmd_lab(args):
    index = load_json(args.index)
    out_dir = args.out_dir or os.path.join(str(HERE), "_lab_out")
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    failed = 0
    for case in index.get("cases", []):
        row = run_lab_case(ROOT, case, out_dir)
        rows.append(row)
        if not row["ok"]:
            failed += 1
        print(
            "%s %s exit=%s code=%s last_good_kept=%s ok=%s path=%s"
            % (
                row["family"],
                row["polarity"],
                row["exit"],
                row["code"],
                row["last_good"],
                row["ok"],
                row["path"],
            )
        )
    print("lab_pass=%s cases=%d fail=%d" % (failed == 0, len(rows), failed))
    return 1 if failed else 0


def write_sample(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def cmd_demo(args):
    work = pathlib.Path(args.workdir)
    if work.exists():
        shutil.rmtree(work)
    samples = work / "samples"
    out = work / "out"
    samples.mkdir(parents=True)
    out.mkdir(parents=True)
    last_good = out / "target.svg"
    last_good.write_text("LAST-GOOD-SEED\n", encoding="utf-8")
    seed_sha = sha256_file(str(last_good))

    good = {
        "family": "lifecycle",
        "payload": load_json(str(ROOT / "scripts/fixtures/vbox-fig/lifecycle.json")),
    }
    bad_kind = {
        "family": "lifecycle",
        "payload": {
            "steps": [{"kind": "parked", "title": "x", "lines": ["one"]}]
        },
    }
    bad_empty = {"family": "lifecycle", "payload": {"steps": []}}
    bad_lines = {
        "family": "lifecycle",
        "payload": {"steps": [{"kind": "b", "title": "x", "lines": []}]},
    }
    bad_family = {
        "family": "lifecycle",
        "payload": {"raw": "[Actor] --> [Page]\n|-- login\n|-- open", "tree": True},
    }
    write_sample(str(samples / "good.json"), good)
    write_sample(str(samples / "bad-kind.json"), bad_kind)
    write_sample(str(samples / "bad-empty.json"), bad_empty)
    write_sample(str(samples / "bad-lines.json"), bad_lines)
    write_sample(str(samples / "bad-family.json"), bad_family)

    rows = []

    def record(name, fn):
        before = sha256_file(str(last_good))
        try:
            fn()
            code, rc = "ok", 0
        except Fail as err:
            code, rc = err.code, 1
        after = sha256_file(str(last_good))
        rows.append(
            {
                "name": name,
                "exit": rc,
                "code": code,
                "sha_before": before,
                "sha_after": after,
                "unchanged": before == after,
            }
        )

    record(
        "AC-2-atomic-good",
        lambda: deliver("lifecycle", good, str(last_good)),
    )
    good_sha = sha256_file(str(last_good))
    record(
        "AC-1-DIAGIR_KIND",
        lambda: deliver("lifecycle", bad_kind, str(last_good)),
    )
    record(
        "AC-1-DIAGIR_EMPTY",
        lambda: deliver("lifecycle", bad_empty, str(last_good)),
    )
    record(
        "AC-1-DIAGIR_LINES",
        lambda: deliver("lifecycle", bad_lines, str(last_good)),
    )
    record(
        "AC-3-DIAGIR_FAMILY",
        lambda: deliver("lifecycle", bad_family, str(last_good)),
    )
    record(
        "AC-2-DIAGIR_ABORT",
        lambda: deliver("lifecycle", good, str(last_good), abort=True),
    )

    why_pos = wrap_ir(
        "dir-tree",
        {"yaml": (ROOT / "scripts/fixtures/dir-tree/good/purpose.yaml").read_text(encoding="utf-8")},
    )
    why_neg = wrap_ir(
        "dir-tree",
        {"yaml": (ROOT / "scripts/fixtures/dir-tree/missing-why/purpose.yaml").read_text(encoding="utf-8")},
    )
    why_out = out / "dir-tree.svg"
    why_out.write_text("LAST-GOOD-DIR\n", encoding="utf-8")

    def record_on(name, path, fn):
        before = sha256_file(str(path))
        try:
            fn()
            code, rc = "ok", 0
        except Fail as err:
            code, rc = err.code, 1
        after = sha256_file(str(path))
        rows.append(
            {
                "name": name,
                "exit": rc,
                "code": code,
                "sha_before": before,
                "sha_after": after,
                "unchanged": before == after,
            }
        )

    record_on("AC-4-dir-pos", why_out, lambda: deliver("dir-tree", why_pos, str(why_out)))
    record_on(
        "AC-4-dir-DIAGIR_WHY",
        why_out,
        lambda: deliver("dir-tree", why_neg, str(why_out)),
    )

    print("seed_sha=%s" % seed_sha)
    print("good_sha=%s" % good_sha)
    print("target=%s" % last_good)
    print("name\texit\tcode\tunchanged\tsha_after")
    for row in rows:
        print(
            "%s\t%s\t%s\t%s\t%s"
            % (row["name"], row["exit"], row["code"], row["unchanged"], row["sha_after"])
        )

    target_text = last_good.read_text(encoding="utf-8")
    static_ok = (
        "<svg" in target_text
        and "mermaid" not in target_text
        and "<animate" not in target_text
        and PROTO_MARK in target_text
    )
    print("AC-5-static-svg=%s" % static_ok)
    print("route_count=%d" % len(ROUTES))
    print("families=%s" % ",".join(row["family"] for row in ROUTES))

    index = HERE / "proof-lab-index.json"
    lab_rc = cmd_lab(
        argparse.Namespace(index=str(index), out_dir=str(work / "lab"))
    )
    fail_kept = all(
        row["unchanged"] and row["exit"] == 1
        for row in rows
        if row["name"] not in ("AC-2-atomic-good", "AC-4-dir-pos")
    )
    good_changed = (
        rows[0]["exit"] == 0
        and not rows[0]["unchanged"]
        and rows[0]["sha_after"] == good_sha
        and rows[0]["sha_after"] != seed_sha
    )
    abort_kept = next(r for r in rows if r["name"] == "AC-2-DIAGIR_ABORT")
    abort_ok = abort_kept["code"] == "DIAGIR_ABORT" and abort_kept["unchanged"]
    print(
        "demo_pass=%s good_changed=%s fail_kept_last_good=%s abort_ok=%s lab_rc=%s"
        % (good_changed and fail_kept and abort_ok and lab_rc == 0 and static_ok,
           good_changed, fail_kept, abort_ok, lab_rc)
    )
    return 0 if good_changed and fail_kept and abort_ok and lab_rc == 0 and static_ok else 1


def main(argv):
    parser = argparse.ArgumentParser(description=PROTO_MARK)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("routes")
    p_del = sub.add_parser("deliver")
    p_del.add_argument("--family", required=True)
    p_del.add_argument("--ir", required=True)
    p_del.add_argument("--out", required=True)
    p_del.add_argument("--adapter", default="ir-json")
    p_del.add_argument("--abort-after-tmp", action="store_true")
    p_lab = sub.add_parser("lab")
    p_lab.add_argument("--index", required=True)
    p_lab.add_argument("--out-dir")
    p_demo = sub.add_parser("demo")
    p_demo.add_argument("--workdir", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "routes":
        return cmd_routes(args)
    if args.cmd == "deliver":
        return cmd_deliver(args)
    if args.cmd == "lab":
        return cmd_lab(args)
    if args.cmd == "demo":
        return cmd_demo(args)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
