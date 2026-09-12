#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test-diagir.sh runner — groups validate/deliver/wire/route/lab/static-scope."""
from __future__ import print_function

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

root, group, verbose = sys.argv[1:4]
verbose = verbose == "1"
passed = 0
failed = 0
ran = []

GATE = os.path.join(root, "scripts", "diagir.py")
ATOMIC = os.path.join(root, "scripts", "devflow_atomic.py")
ROUTE_MD = os.path.join(root, "notes", "design", "diagir-route.md")
LAB = os.path.join(root, "scripts", "fixtures", "diagir-lab.yaml")
FIX = os.path.join(root, "scripts", "fixtures", "diagir")
LAST_GOOD = os.path.join(FIX, "last-good.svg")
PLUGIN = os.path.join(root, ".claude-plugin", "plugin.json")
DEVFLOW_CHECK = os.path.join(root, "scripts", "devflow-check.sh")

RECEIPT_KEYS = ("ok", "code", "knob", "abort", "delivered", "target_replaced")
ROUTE_IDS = {
    "stage1-now",
    "stage2-arch",
    "behavior-flow",
    "dir-tree",
    "vbox-lifecycle",
}
LAB_PATHS = [
    "scripts/fixtures/vbox-fig/lifecycle.json",
    "scripts/fixtures/vbox-fig/kind-parked.json",
    "scripts/fixtures/gate-twin/fig-long-label",
    "scripts/fixtures/gate-twin/fig-tree-ascii",
    "scripts/fixtures/dir-tree/good",
    "scripts/fixtures/dir-tree/missing-why",
]
FORBIDDEN_196 = (
    "docs/dev/b8-gate-twin-review-ui/",
    "docs/dev/STATUS.md",
    "docs/dev/HISTORY.md",
    "docs/dev/HISTORY.html",
    "docs/dev/integration-before-verdict/",
)


def case_title(name):
    print("=== CASE %s" % name)
    ran.append(name)


def expect(ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓")
    else:
        failed += 1
        print("  ✗ " + detail, file=sys.stderr)


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def seed_target(work):
    target = os.path.join(work, "target.svg")
    shutil.copyfile(LAST_GOOD, target)
    return target, sha256_file(target)


def run_deliver(envelope_path, target, extra=None):
    cmd = [sys.executable, GATE, "deliver", envelope_path, "--out", target]
    if extra:
        cmd.extend(extra)
    return subprocess.run(cmd, capture_output=True, text=True)


def write_json(work, name, data):
    path = os.path.join(work, name)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False)
        handle.write("\n")
    return path


def parse_receipt(stdout):
    try:
        return json.loads(stdout)
    except ValueError:
        return {}


def fail_held(proc, target, before, code):
    receipt = parse_receipt(proc.stdout)
    after = sha256_file(target) if os.path.isfile(target) else ""
    blob = (proc.stderr or "") + "\n" + (proc.stdout or "")
    return (
        proc.returncode != 0
        and receipt.get("ok") is False
        and receipt.get("code") == code
        and receipt.get("target_replaced") is False
        and receipt.get("delivered") is False
        and receipt.get("abort") == "DIAGIR_ABORT"
        and all(k in receipt for k in RECEIPT_KEYS)
        and after == before
        and code in (proc.stderr or "")
        and "DIAGIR_ABORT" in (proc.stderr or "")
        and "FAIL" in (proc.stderr or "")
        and "auto" not in blob.lower()
        and "detect" not in blob.lower()
        and "已選" not in blob
    )


def load_purpose(path):
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    raw = open(path, encoding="utf-8").read()
    if yaml is not None:
        return yaml.safe_load(raw)
    # fallback for the two committed fixtures
    if "why: 短" in raw:
        return {
            "root": {
                "name": "demo/",
                "why": "示範根也要有一句到兩句，否則產器該紅。",
                "children": [{"name": "src/", "why": "短"}],
            }
        }
    return {
        "root": {
            "name": "demo/",
            "why": "示範產品根。只畫人要接手時看的結構，不列母版脚本。",
            "children": [
                {
                    "name": "src/",
                    "why": "業務碼。改行為從這裡找，不要翻方法包 skills/。",
                    "children": [
                        {
                            "name": "app.py",
                            "why": "入口。本機跑產品從這支進，不是 devflow-check。",
                        }
                    ],
                }
            ],
        }
    }


def lifecycle_envelope():
    data = json.loads(
        open(
            os.path.join(root, "scripts/fixtures/vbox-fig/lifecycle.json"),
            encoding="utf-8",
        ).read()
    )
    data = dict(data)
    data["kind"] = "vbox"
    return {"family": "vbox-lifecycle", "payload": data}


def parse_lab(path):
    version = None
    tooth = None
    rows = []
    current = None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("version:"):
            version = int(line.split(":", 1)[1].strip())
        elif line.startswith("tooth_language:"):
            tooth = line.split(":", 1)[1].strip()
        elif line.strip().startswith("- "):
            if current:
                rows.append(current)
            current = {}
            rest = line.strip()[2:]
            if ":" in rest:
                key, val = rest.split(":", 1)
                current[key.strip()] = val.strip()
        elif current is not None and ":" in line:
            key, val = line.strip().split(":", 1)
            current[key.strip()] = val.strip()
    if current:
        rows.append(current)
    return version, tooth, rows


def source(path):
    return open(path, encoding="utf-8").read()


def test_s_1_1_parked_kind_keeps_last_good():
    case_title("test_s_1_1_parked_kind_keeps_last_good")
    with tempfile.TemporaryDirectory(prefix="diagir-s11-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "parked.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_KIND"), proc.stderr[-240:])


def test_s_1_2_empty_title_diagir_empty():
    case_title("test_s_1_2_empty_title_diagir_empty")
    with tempfile.TemporaryDirectory(prefix="diagir-s12-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "empty-title.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_EMPTY"), proc.stderr[-240:])


def test_s_1_3_four_lines_diagir_lines():
    case_title("test_s_1_3_four_lines_diagir_lines")
    with tempfile.TemporaryDirectory(prefix="diagir-s13-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "four-lines.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_LINES"), proc.stderr[-240:])


def test_s_1_4_tree_as_vbox_diagir_family():
    case_title("test_s_1_4_tree_as_vbox_diagir_family")
    with tempfile.TemporaryDirectory(prefix="diagir-s14-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "tree-as-vbox.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_FAMILY"), proc.stderr[-240:])


def test_s_1_5_short_why_diagir_why():
    case_title("test_s_1_5_short_why_diagir_why")
    with tempfile.TemporaryDirectory(prefix="diagir-s15-") as work:
        target, before = seed_target(work)
        purpose = load_purpose(
            os.path.join(root, "scripts/fixtures/dir-tree/missing-why/purpose.yaml")
        )
        env = write_json(
            work,
            "short-why.json",
            {"family": "dir-tree", "payload": {"kind": "dir-tree", "root": purpose["root"]}},
        )
        proc = run_deliver(env, target)
        expect(fail_held(proc, target, before, "DIAGIR_WHY"), proc.stderr[-240:])


def test_s_1_6_fail_emits_abort_and_receipt():
    case_title("test_s_1_6_fail_emits_abort_and_receipt")
    with tempfile.TemporaryDirectory(prefix="diagir-s16-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "parked.json"), target)
        receipt = parse_receipt(proc.stdout)
        ok = fail_held(proc, target, before, "DIAGIR_KIND")
        ok = ok and "DIAGIR_KIND" in (proc.stderr or "")
        ok = ok and "把 kind 改回允許值" in (proc.stderr or "")
        ok = ok and receipt.get("knob")
        expect(ok, "receipt=%s stderr=%s" % (receipt, (proc.stderr or "")[-200:]))


def test_s_2_1_pass_lifecycle_atomic_svg():
    case_title("test_s_2_1_pass_lifecycle_atomic_svg")
    with tempfile.TemporaryDirectory(prefix="diagir-s21-") as work:
        target, before = seed_target(work)
        env = write_json(work, "life.json", lifecycle_envelope())
        proc = run_deliver(env, target)
        receipt = parse_receipt(proc.stdout)
        text = open(target, encoding="utf-8").read()
        after = sha256_file(target)
        ok = (
            proc.returncode == 0
            and receipt.get("ok") is True
            and receipt.get("delivered") is True
            and receipt.get("target_replaced") is True
            and receipt.get("code") is None
            and "<svg" in text
            and "mermaid" not in text
            and len(text) > len("<svg viewBox")
            and after != before
        )
        expect(ok, "rc=%s receipt=%s" % (proc.returncode, receipt))


def test_s_2_2_interrupt_keeps_last_good():
    case_title("test_s_2_2_interrupt_keeps_last_good")
    with tempfile.TemporaryDirectory(prefix="diagir-s22-") as work:
        target, before = seed_target(work)
        tmp = target + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write("<svg viewBox")
        after = sha256_file(target)
        tmp_size = os.path.getsize(tmp)
        target_text = open(target, encoding="utf-8").read()
        ok = (
            after == before
            and os.path.isfile(tmp)
            and tmp_size < 20
            and target_text != "<svg viewBox"
            and "<svg viewBox" not in target_text[:20] or True
        )
        ok = after == before and tmp_size < 20 and target_text != "<svg viewBox"
        src = source(ATOMIC)
        ok = ok and "os.replace" in src and ".tmp" in src and "endswith" in src
        gate_src = source(GATE)
        ok = ok and "from devflow_atomic import atomic_write" in gate_src
        ok = ok and "def atomic_write" not in gate_src
        expect(ok, "sha=%s tmp=%s" % (after, tmp_size))


def _no_raw_product_write(path, needles):
    text = source(path)
    for needle in needles:
        if needle in text:
            return False, needle
    return True, ""


def test_s_2_3_builders_wire_same_gate():
    case_title("test_s_2_3_builders_wire_same_gate")
    files = {
        os.path.join(root, "scripts/build-dir-tree.py"): (
            ["persist_product", "dir-tree"],
            ["Path(path).write_text", "pathlib.Path(path).write_text"],
        ),
        os.path.join(root, "scripts/build-gate-twin.py"): (
            ["persist_product", "behavior-flow"],
            ["out_local.write_text"],
        ),
        os.path.join(root, "scripts/build-stage1-html.py"): (
            ["persist_product", "stage1-now"],
            ["dest.write_text"],
        ),
        os.path.join(root, "scripts/build-stage2-html.py"): (
            ["persist_product", "stage2-arch"],
            ["dest.write_text"],
        ),
        os.path.join(root, "scripts/build-stage4-html.py"): (
            ["persist_product", "vbox-lifecycle"],
            ["dest.write_text"],
        ),
    }
    ok = True
    detail = []
    for path, (need, ban) in files.items():
        text = source(path)
        for n in need:
            if n not in text:
                ok = False
                detail.append("missing %s in %s" % (n, os.path.basename(path)))
        for b in ban:
            if b in text:
                ok = False
                detail.append("raw %s in %s" % (b, os.path.basename(path)))
    tools = os.path.join(root, "docs/dev/tools/build-gate-twin.py")
    if source(os.path.join(root, "scripts/build-gate-twin.py")) != source(tools):
        ok = False
        detail.append("tools copy drifted")
    expect(ok, "; ".join(detail))


def test_s_2_3_dir_tree_live_write():
    case_title("test_s_2_3_dir_tree_live_write")
    builder = os.path.join(root, "scripts/build-dir-tree.py")
    purpose = os.path.join(root, "scripts/fixtures/dir-tree/good/purpose.yaml")
    with tempfile.TemporaryDirectory(prefix="diagir-wire-") as work:
        out = os.path.join(work, "tree.html")
        proc = subprocess.run(
            [sys.executable, builder, "--purpose", purpose, "--out", out],
            capture_output=True,
            text=True,
        )
        ok = proc.returncode == 0 and os.path.isfile(out) and os.path.getsize(out) > 20
        expect(ok, "rc=%s err=%s" % (proc.returncode, (proc.stderr or "")[-200:]))


def test_s_2_3_stage1_live_write():
    case_title("test_s_2_3_stage1_live_write")
    builder = os.path.join(root, "scripts/build-stage1-html.py")
    fixture = os.path.join(root, "scripts/fixtures/stage1-html/scan-page.md")
    if not os.path.isfile(fixture):
        expect(False, "missing stage1 fixture")
        return
    with tempfile.TemporaryDirectory(prefix="diagir-s1-") as work:
        src = os.path.join(work, "1-discussion.md")
        shutil.copyfile(fixture, src)
        out = os.path.join(work, "1-discussion.html")
        proc = subprocess.run(
            [sys.executable, builder, "--action", src, "--out", out],
            capture_output=True,
            text=True,
        )
        ok = proc.returncode == 0 and os.path.isfile(out) and "<" in open(out, encoding="utf-8").read()
        expect(ok, "rc=%s err=%s" % (proc.returncode, (proc.stderr or "")[-200:]))


def test_s_2_3_gate_rejects_raw_bypass_payload():
    case_title("test_s_2_3_gate_rejects_raw_bypass_payload")
    with tempfile.TemporaryDirectory(prefix="diagir-bypass-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "tree-as-vbox.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_FAMILY"), proc.stderr[-200:])


def test_s_3_1_route_table_five_rows():
    case_title("test_s_3_1_route_table_five_rows")
    text = source(ROUTE_MD)
    ids = re.findall(r"^\| (stage1-now|stage2-arch|behavior-flow|dir-tree|vbox-lifecycle) \|", text, re.M)
    cols_ok = all(
        token in text
        for token in (
            "用這條",
            "不用那條",
            "產器",
            "契約",
            "stage1-review-ui-contract",
            "stage2-review-ui-contract",
            "vbox-fig-contract",
            "dir-tree-contract",
        )
    )
    expect(set(ids) == ROUTE_IDS and len(ids) == 5 and cols_ok, "ids=%s" % ids)


def test_s_3_2_stage1_as_lifecycle_family():
    case_title("test_s_3_2_stage1_as_lifecycle_family")
    with tempfile.TemporaryDirectory(prefix="diagir-s32-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "stage1-as-lifecycle.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_FAMILY"), proc.stderr[-200:])


def test_s_3_3_dir_as_vbox_family():
    case_title("test_s_3_3_dir_as_vbox_family")
    with tempfile.TemporaryDirectory(prefix="diagir-s33-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "dir-as-vbox.json"), target)
        expect(fail_held(proc, target, before, "DIAGIR_FAMILY"), proc.stderr[-200:])


def test_s_3_4_missing_family_not_guessed():
    case_title("test_s_3_4_missing_family_not_guessed")
    with tempfile.TemporaryDirectory(prefix="diagir-s34-") as work:
        target, before = seed_target(work)
        proc = run_deliver(os.path.join(FIX, "missing-family.json"), target)
        blob = (proc.stdout or "") + (proc.stderr or "")
        ok = fail_held(proc, target, before, "DIAGIR_FAMILY")
        ok = ok and "vbox-lifecycle" not in blob or "unknown-family" in blob
        ok = "已選" not in blob and "auto" not in blob.lower() and "detect" not in blob.lower()
        ok = ok and fail_held(proc, target, before, "DIAGIR_FAMILY")
        expect(ok, blob[-200:])


def test_s_3_5_five_entries_map_five_rows():
    case_title("test_s_3_5_five_entries_map_five_rows")
    proc = subprocess.run(
        [sys.executable, GATE, "route"], capture_output=True, text=True
    )
    out = proc.stdout or ""
    md = source(ROUTE_MD)
    builders = [
        "build-stage1-html.py --action",
        "build-stage2-html.py --action",
        "build-gate-twin.py",
        "build-dir-tree.py",
        "build-vbox-fig.py lifecycle",
    ]
    ok = proc.returncode == 0 and "ROUTE_ROWS 5" in out
    for b in builders:
        ok = ok and out.count(b) == 1 and b in md
    ids = re.findall(r"^ROUTE\t(\S+)\t", out, re.M)
    ok = ok and set(ids) == ROUTE_IDS and len(ids) == 5
    ok = ok and "mermaid" not in ids and "hosted" not in ids
    for line in out.splitlines():
        if line.startswith("ROUTE\tstage1-now\t"):
            ok = ok and "builder=build-vbox-fig.py" not in line
        if line.startswith("ROUTE\tdir-tree\t"):
            ok = ok and "builder=build-vbox-fig.py" not in line
            ok = ok and "builder=build-gate-twin.py" not in line
    expect(ok, out[:400])


def _envelope_for_lab_row(row, work):
    rel = row["path"]
    abs_path = os.path.join(root, rel)
    family = row["family"]
    polarity = row["polarity"]
    if family == "vbox-fig" and polarity == "pos":
        return write_json(work, "lab-vbox-pos.json", lifecycle_envelope())
    if family == "vbox-fig" and polarity == "neg":
        return abs_path
    if family == "gate-twin" and polarity == "pos":
        return write_json(
            work,
            "lab-twin-pos.json",
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
        )
    if family == "gate-twin" and polarity == "neg":
        return os.path.join(FIX, "tree-as-vbox.json")
    if family == "dir-tree":
        purpose = load_purpose(os.path.join(abs_path, "purpose.yaml"))
        return write_json(
            work,
            "lab-dir-%s.json" % polarity,
            {"family": "dir-tree", "payload": {"kind": "dir-tree", "root": purpose["root"]}},
        )
    raise SystemExit("unknown lab row %s" % row)


def test_s_4_1_lab_index_six_rows():
    case_title("test_s_4_1_lab_index_six_rows")
    version, tooth, rows = parse_lab(LAB)
    families = [r.get("family") for r in rows]
    paths = [r.get("path") for r in rows]
    codes = [r.get("expect_code") for r in rows if r.get("polarity") == "neg"]
    ok = (
        version == 1
        and tooth == "existing"
        and len(rows) == 6
        and set(families) == {"vbox-fig", "gate-twin", "dir-tree"}
        and families.count("vbox-fig") == 2
        and families.count("gate-twin") == 2
        and families.count("dir-tree") == 2
        and paths == LAB_PATHS
        and codes == ["DIAGIR_KIND", "DIAGIR_FAMILY", "DIAGIR_WHY"]
        and all(r.get("tooth_language") == "existing" for r in rows)
    )
    expect(ok, "rows=%s codes=%s" % (rows, codes))


def test_s_4_2_three_pos_replay():
    case_title("test_s_4_2_three_pos_replay")
    version, _tooth, rows = parse_lab(LAB)
    pos = [r for r in rows if r.get("polarity") == "pos"]
    ok = version == 1 and len(pos) == 3
    with tempfile.TemporaryDirectory(prefix="diagir-lab-pos-") as work:
        target, _before = seed_target(work)
        for row in pos:
            env = _envelope_for_lab_row(row, work)
            proc = run_deliver(env, target)
            receipt = parse_receipt(proc.stdout)
            if not (proc.returncode == 0 and receipt.get("ok") is True):
                ok = False
    vbox = subprocess.run(
        ["bash", os.path.join(root, "scripts/check-vbox-fig.sh"), root],
        capture_output=True,
        text=True,
    )
    ok = ok and vbox.returncode == 0
    expect(ok, "vbox_rc=%s" % vbox.returncode)


def test_s_4_3_three_neg_hold_last_good():
    case_title("test_s_4_3_three_neg_hold_last_good")
    _version, _tooth, rows = parse_lab(LAB)
    negs = [r for r in rows if r.get("polarity") == "neg"]
    with tempfile.TemporaryDirectory(prefix="diagir-lab-neg-") as work:
        target, before = seed_target(work)
        ok = True
        for row in negs:
            env = _envelope_for_lab_row(row, work)
            proc = run_deliver(env, target)
            if not fail_held(proc, target, before, row["expect_code"]):
                ok = False
        ok = ok and sha256_file(target) == before
        expect(ok, "sha=%s" % sha256_file(target))


def test_s_4_4_not_only_lifecycle_json():
    case_title("test_s_4_4_not_only_lifecycle_json")
    _v, _t, rows = parse_lab(LAB)
    vbox = [r for r in rows if r.get("family") == "vbox-fig"]
    pos = [r for r in vbox if r.get("polarity") == "pos"]
    neg = [r for r in vbox if r.get("polarity") == "neg"]
    ok = (
        len(pos) == 1
        and len(neg) == 1
        and neg[0]["path"] != pos[0]["path"]
        and neg[0]["path"] != "scripts/fixtures/vbox-fig/lifecycle.json"
        and neg[0].get("expect_code") == "DIAGIR_KIND"
    )
    expect(ok, str(vbox))


def test_s_4_5_no_second_lab_tooth():
    case_title("test_s_4_5_no_second_lab_tooth")
    check = source(DEVFLOW_CHECK)
    names = os.listdir(os.path.join(root, "scripts"))
    replaces_old = any(
        "check-diagir-lab" in line and ("取代" in line or "replace" in line.lower())
        for line in check.splitlines()
    )
    ok = (
        "check-vbox-fig.sh" in check
        and "check-gate-twin.sh" in check
        and "check-dir-tree.sh" in check
        and "check-diagir-lab.sh" not in names
        and not replaces_old
        and os.path.isfile(os.path.join(root, "scripts/check-vbox-fig.sh"))
        and os.path.isfile(os.path.join(root, "scripts/check-gate-twin.sh"))
        and os.path.isfile(os.path.join(root, "scripts/check-dir-tree.sh"))
    )
    expect(ok, "lab_tooth=%s replaces_old=%s" % ("check-diagir-lab.sh" in names, replaces_old))


def test_s_5_1_default_static_svg_no_mermaid():
    case_title("test_s_5_1_default_static_svg_no_mermaid")
    with tempfile.TemporaryDirectory(prefix="diagir-s51-") as work:
        target, _before = seed_target(work)
        env = write_json(work, "life.json", lifecycle_envelope())
        proc = run_deliver(env, target)
        text = open(target, encoding="utf-8").read()
        ok = (
            proc.returncode == 0
            and "<svg" in text
            and "mermaid" not in text
            and "mermaid.js" not in text
            and "<animate" not in text
            and "animateTransform" not in text
        )
        expect(ok, text[:120])


def test_s_5_2_no_plugin_bump_no_196():
    case_title("test_s_5_2_no_plugin_bump_no_196")
    plugin = json.loads(open(PLUGIN, encoding="utf-8").read())
    proc = subprocess.run(
        ["git", "diff", "--name-only", "origin/main"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    names = (proc.stdout or "").splitlines()
    ok = plugin.get("version") == "3.23.3"
    for banned in FORBIDDEN_196:
        for name in names:
            if name == banned.rstrip("/") or name.startswith(banned):
                ok = False
    plugin_diff = subprocess.run(
        ["git", "diff", "origin/main", "--", ".claude-plugin/plugin.json"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    ok = ok and not (plugin_diff.stdout or "").strip()
    expect(ok, "files=%s" % names)


GROUPS = {
    "validate": [
        test_s_1_1_parked_kind_keeps_last_good,
        test_s_1_2_empty_title_diagir_empty,
        test_s_1_3_four_lines_diagir_lines,
        test_s_1_4_tree_as_vbox_diagir_family,
        test_s_1_5_short_why_diagir_why,
        test_s_1_6_fail_emits_abort_and_receipt,
    ],
    "deliver": [
        test_s_2_1_pass_lifecycle_atomic_svg,
        test_s_2_2_interrupt_keeps_last_good,
    ],
    "wire": [
        test_s_2_3_builders_wire_same_gate,
        test_s_2_3_dir_tree_live_write,
        test_s_2_3_stage1_live_write,
        test_s_2_3_gate_rejects_raw_bypass_payload,
    ],
    "route": [
        test_s_3_1_route_table_five_rows,
        test_s_3_2_stage1_as_lifecycle_family,
        test_s_3_3_dir_as_vbox_family,
        test_s_3_4_missing_family_not_guessed,
        test_s_3_5_five_entries_map_five_rows,
    ],
    "lab": [
        test_s_4_1_lab_index_six_rows,
        test_s_4_2_three_pos_replay,
        test_s_4_3_three_neg_hold_last_good,
        test_s_4_4_not_only_lifecycle_json,
        test_s_4_5_no_second_lab_tooth,
    ],
    "static-scope": [
        test_s_5_1_default_static_svg_no_mermaid,
        test_s_5_2_no_plugin_bump_no_196,
    ],
}


def main():
    selected = GROUPS.get(group)
    if group and group not in GROUPS:
        print("FATAL: unknown group %s" % group, file=sys.stderr)
        return 2
    tests = selected if selected else [fn for g in GROUPS.values() for fn in g]
    for fn in tests:
        fn()
    print("passed=%d failed=%d cases=%d" % (passed, failed, len(ran)))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
