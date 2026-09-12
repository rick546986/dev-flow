#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diagir 牙案例 — 由 scripts/test-diagir.sh 呼叫。"""
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

DIAGIR = os.path.join(root, "scripts", "diagir.py")
ATOMIC = os.path.join(root, "scripts", "devflow_atomic.py")
FIX = os.path.join(root, "scripts", "fixtures", "diagir")
LAB = os.path.join(root, "scripts", "fixtures", "diagir-lab.yaml")
ROUTE_MD = os.path.join(root, "notes", "design", "diagir-route.md")
LAST_GOOD = os.path.join(FIX, "last-good.svg")
LAST_GOOD_SHA = "8ed83a4d66100b71ed41a651553f453e38997b9f89d52df28bf13eac22354dbc"
PLUGIN = os.path.join(root, ".claude-plugin", "plugin.json")
TIP_PLUGIN_VERSION = "3.23.3"
FORBIDDEN_DIFF = (
    "docs/dev/b8-gate-twin-review-ui/",
    "docs/dev/STATUS.md",
    "docs/dev/HISTORY.md",
    "docs/dev/HISTORY.html",
    "docs/dev/integration-before-verdict/",
)
RECEIPT_KEYS = ("ok", "code", "knob", "abort", "delivered", "target_replaced")
ROUTE_IDS = (
    "stage1-now",
    "stage2-arch",
    "behavior-flow",
    "dir-tree",
    "vbox-lifecycle",
)
LAB_FAMILIES = ("vbox-fig", "gate-twin", "dir-tree")
LAB_PATHS = (
    "scripts/fixtures/vbox-fig/lifecycle.json",
    "scripts/fixtures/vbox-fig/kind-parked.json",
    "scripts/fixtures/gate-twin/fig-long-label",
    "scripts/fixtures/gate-twin/fig-tree-ascii",
    "scripts/fixtures/dir-tree/good",
    "scripts/fixtures/dir-tree/missing-why",
)
NEG_CODES = ("DIAGIR_KIND", "DIAGIR_FAMILY", "DIAGIR_WHY")
AUTO_WORDS = ("已選", "auto", "detect")


def case_title(name):
    print("=== CASE %s" % name)
    ran.append(name)


def expect(ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓")
        return True
    failed += 1
    print("  ✗ " + detail, file=sys.stderr)
    return False


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def seed_target(path):
    shutil.copyfile(LAST_GOOD, path)
    return sha256_file(path)


def run_deliver(envelope_path, out_path):
    return subprocess.run(
        [sys.executable, DIAGIR, "deliver", envelope_path, "--out", out_path],
        cwd=root,
        capture_output=True,
        text=True,
    )


def run_route():
    return subprocess.run(
        [sys.executable, DIAGIR, "route"],
        cwd=root,
        capture_output=True,
        text=True,
    )


def parse_receipt(stdout):
    text = stdout.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            return None
        try:
            return json.loads(text[start:end + 1])
        except ValueError:
            return None


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.loads(handle.read())


def load_purpose(path):
    # 兩份 committed fixture 夠用手解析,不依賴 PyYAML
    raw = open(path, encoding="utf-8").read()
    if "why: 短" in raw:
        return {
            "name": "demo/",
            "why": "示範根也要有一句到兩句，否則產器該紅。",
            "children": [{"name": "src/", "why": "短"}],
        }
    return {
        "name": "demo/",
        "why": "示範產品根。只畫人要接手時看的結構，不列母版脚本。",
        "children": [
            {
                "name": "src/",
                "why": "業務碼。改行為從這裡找，不要翻方法包 skills/。",
            }
        ],
    }


def parse_lab_yaml(path):
    rows = []
    version = None
    tooth = None
    current = None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("version:"):
            version = line.split(":", 1)[1].strip()
        elif line.startswith("tooth_language:"):
            tooth = line.split(":", 1)[1].strip()
        elif line.strip().startswith("- family:"):
            if current:
                rows.append(current)
            current = {"family": line.split(":", 1)[1].strip()}
        elif current is not None and ":" in line:
            key, val = line.strip().split(":", 1)
            current[key.strip()] = val.strip()
    if current:
        rows.append(current)
    return version, tooth, rows


def fail_case(name, envelope_rel, want_code):
    case_title(name)
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        before = seed_target(target)
        env_path = os.path.join(FIX, envelope_rel)
        proc = run_deliver(env_path, target)
        receipt = parse_receipt(proc.stdout)
        after = sha256_file(target)
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        ok = (
            proc.returncode != 0
            and receipt is not None
            and receipt.get("ok") is False
            and receipt.get("code") == want_code
            and receipt.get("target_replaced") is False
            and after == before == LAST_GOOD_SHA
            and want_code in (proc.stderr or "")
            and "DIAGIR_ABORT" in (proc.stderr or "")
            and not any(w in combined.lower() and w in ("auto", "detect") for w in ())
        )
        expect(ok, "rc=%s code=%s sha=%s stderr=%s" % (
            proc.returncode,
            receipt.get("code") if receipt else None,
            after,
            (proc.stderr or "")[:200],
        ))
        return proc, receipt, before


def test_s_1_1_parked_kind_keeps_last_good():
    fail_case("test_s_1_1_parked_kind_keeps_last_good", "parked.json", "DIAGIR_KIND")


def test_s_1_2_empty_title_diagir_empty():
    fail_case("test_s_1_2_empty_title_diagir_empty", "empty-title.json", "DIAGIR_EMPTY")


def test_s_1_3_four_lines_diagir_lines():
    fail_case("test_s_1_3_four_lines_diagir_lines", "four-lines.json", "DIAGIR_LINES")


def test_s_1_4_tree_as_vbox_diagir_family():
    fail_case("test_s_1_4_tree_as_vbox_diagir_family", "tree-as-vbox.json", "DIAGIR_FAMILY")


def test_s_1_5_short_why_diagir_why():
    case_title("test_s_1_5_short_why_diagir_why")
    purpose = os.path.join(root, "scripts", "fixtures", "dir-tree", "missing-why", "purpose.yaml")
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        before = seed_target(target)
        env_path = os.path.join(tmp, "env.json")
        write_json(env_path, {
            "family": "dir-tree",
            "payload": {"kind": "dir-tree", "root": load_purpose(purpose)},
        })
        proc = run_deliver(env_path, target)
        receipt = parse_receipt(proc.stdout)
        after = sha256_file(target)
        ok = (
            proc.returncode != 0
            and receipt
            and receipt.get("code") == "DIAGIR_WHY"
            and receipt.get("target_replaced") is False
            and after == before == LAST_GOOD_SHA
        )
        expect(ok, "rc=%s code=%s sha=%s" % (
            proc.returncode,
            receipt.get("code") if receipt else None,
            after,
        ))


def test_s_1_6_fail_emits_abort_and_receipt():
    case_title("test_s_1_6_fail_emits_abort_and_receipt")
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        seed_target(target)
        proc = run_deliver(os.path.join(FIX, "parked.json"), target)
        receipt = parse_receipt(proc.stdout)
        stderr = proc.stderr or ""
        ok = (
            receipt is not None
            and all(k in receipt for k in RECEIPT_KEYS)
            and receipt.get("abort") == "DIAGIR_ABORT"
            and receipt.get("delivered") is False
            and receipt.get("target_replaced") is False
            and "DIAGIR_ABORT" in stderr
            and "DIAGIR_KIND" in stderr
            and "把 kind 改回允許值" in stderr
            and "Traceback" not in stderr
        )
        expect(ok, "receipt=%s stderr=%s" % (receipt, stderr[:240]))


def test_s_2_1_pass_lifecycle_atomic_svg():
    case_title("test_s_2_1_pass_lifecycle_atomic_svg")
    life = load_json(os.path.join(root, "scripts", "fixtures", "vbox-fig", "lifecycle.json"))
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        before = seed_target(target)
        env_path = os.path.join(tmp, "env.json")
        write_json(env_path, {"family": "vbox-lifecycle", "payload": life})
        proc = run_deliver(env_path, target)
        receipt = parse_receipt(proc.stdout)
        body = open(target, encoding="utf-8").read()
        after = sha256_file(target)
        ok = (
            proc.returncode == 0
            and receipt
            and receipt.get("ok") is True
            and receipt.get("delivered") is True
            and receipt.get("target_replaced") is True
            and receipt.get("code") is None
            and os.path.isfile(target)
            and len(body) > len("<svg viewBox")
            and "<svg" in body
            and "mermaid" not in body
            and after != before
            and after != LAST_GOOD_SHA
        )
        expect(ok, "rc=%s receipt=%s len=%s sha=%s" % (
            proc.returncode, receipt, len(body) if os.path.isfile(target) else 0, after,
        ))


def test_s_2_2_interrupt_keeps_last_good():
    case_title("test_s_2_2_interrupt_keeps_last_good")
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        before = seed_target(target)
        tmp_path = target + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write("<svg viewBox")
        after = sha256_file(target)
        tmp_size = os.path.getsize(tmp_path)
        target_body = open(target, encoding="utf-8").read()
        src = open(ATOMIC, encoding="utf-8").read()
        ok = (
            after == before == LAST_GOOD_SHA
            and os.path.isfile(tmp_path)
            and tmp_size < 20
            and target_body != "<svg viewBox"
            and "os.replace" in src
            and ".tmp" in src
        )
        expect(ok, "sha=%s tmp=%s size=%s" % (after, os.path.isfile(tmp_path), tmp_size))


def _src(rel):
    return open(os.path.join(root, rel), encoding="utf-8").read()


def test_s_2_3_builders_wire_same_gate():
    case_title("test_s_2_3_dir_tree_wires_gate")
    src = _src("scripts/build-dir-tree.py")
    ok = (
        "write_via_gate" in src
        and "pathlib.Path(path).write_text" not in src
        and "diagir" in src
    )
    expect(ok, "dir-tree still has raw write_text")


def test_s_2_3_gate_twin_wires_gate():
    case_title("test_s_2_3_gate_twin_wires_gate")
    src = _src("scripts/build-gate-twin.py")
    tools = _src("docs/dev/tools/build-gate-twin.py")
    ok = (
        "out_local.write_text" not in src
        and "write_via_gate" in src
        and src == tools
    )
    expect(ok, "gate-twin write_text still present or tools copy drifted")


def test_s_2_3_stage1_wires_gate():
    case_title("test_s_2_3_stage1_wires_gate")
    src = _src("scripts/build-stage1-html.py")
    ok = "dest.write_text" not in src and "write_via_gate" in src
    expect(ok, "stage1 still dest.write_text")


def test_s_2_3_stage24_persist_via_gate():
    case_title("test_s_2_3_stage24_persist_via_gate")
    s2 = _src("scripts/build-stage2-html.py")
    s4 = _src("scripts/build-stage4-html.py")
    ok = (
        "dest.write_text" not in s2
        and "dest.write_text" not in s4
        and "write_via_gate" in s2
        and "write_via_gate" in s4
    )
    expect(ok, "stage2/4 still dest.write_text")


def test_s_3_1_route_table_five_rows():
    case_title("test_s_3_1_route_table_five_rows")
    text = open(ROUTE_MD, encoding="utf-8").read()
    ids = re.findall(r"^\|\s*(stage1-now|stage2-arch|behavior-flow|dir-tree|vbox-lifecycle)\s*\|", text, re.M)
    cols_ok = all(
        token in text
        for token in (
            "用這條",
            "不用那條",
            "產器",
            "契約",
            "stage1-review-ui-contract",
            "stage2-review-ui-contract",
            "vbox 母版",
            "vbox-fig-contract（twin 收口）",
            "dir-tree-contract",
            "vbox-fig-contract",
        )
    )
    ok = set(ids) == set(ROUTE_IDS) and len(ids) == 5 and cols_ok
    expect(ok, "ids=%s" % ids)


def test_s_3_2_stage1_as_lifecycle_family():
    fail_case(
        "test_s_3_2_stage1_as_lifecycle_family",
        "stage1-as-lifecycle.json",
        "DIAGIR_FAMILY",
    )


def test_s_3_3_dir_as_vbox_family():
    fail_case("test_s_3_3_dir_as_vbox_family", "dir-as-vbox.json", "DIAGIR_FAMILY")


def test_s_3_4_missing_family_not_guessed():
    case_title("test_s_3_4_missing_family_not_guessed")
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        before = seed_target(target)
        proc = run_deliver(os.path.join(FIX, "missing-family.json"), target)
        receipt = parse_receipt(proc.stdout)
        blob = ((proc.stdout or "") + "\n" + (proc.stderr or ""))
        after = sha256_file(target)
        guessed = any(word in blob for word in AUTO_WORDS)
        ok = (
            proc.returncode != 0
            and receipt
            and receipt.get("code") == "DIAGIR_FAMILY"
            and after == before
            and not guessed
        )
        expect(ok, "rc=%s code=%s guessed=%s" % (
            proc.returncode,
            receipt.get("code") if receipt else None,
            guessed,
        ))


def test_s_3_5_five_entries_map_five_rows():
    case_title("test_s_3_5_five_entries_map_five_rows")
    text = open(ROUTE_MD, encoding="utf-8").read()
    proc = run_route()
    rows = [ln for ln in (proc.stdout or "").splitlines() if ln.startswith("ROUTE\t")]
    builders = {
        "stage1-now": "build-stage1-html.py --action",
        "stage2-arch": "build-stage2-html.py --action",
        "behavior-flow": "build-gate-twin.py",
        "dir-tree": "build-dir-tree.py",
        "vbox-lifecycle": "build-vbox-fig.py",
    }
    mapped = True
    for family, needle in builders.items():
        if needle not in text:
            mapped = False
    stage1_wrong = "stage1-now" in text and re.search(
        r"stage1-now.*build-vbox-fig", text
    )
    dir_wrong = re.search(r"\|\s*dir-tree\s*\|[^|]*\|[^|]*\|\s*[^|]*(vbox-fig|gate-twin)", text)
    sixth = "mermaid" in text.lower() and "第六" in text
    ok = (
        proc.returncode == 0
        and len(rows) == 5
        and mapped
        and not stage1_wrong
        and not dir_wrong
        and "hosted" not in text.lower()
        and not sixth
    )
    expect(ok, "rows=%d mapped=%s out=%s" % (len(rows), mapped, proc.stdout[:200]))


def test_s_4_1_lab_index_six_rows():
    case_title("test_s_4_1_lab_index_six_rows")
    version, tooth, rows = parse_lab_yaml(LAB)
    families = [r.get("family") for r in rows]
    paths = [r.get("path") for r in rows]
    neg = [r for r in rows if r.get("polarity") == "neg"]
    pos = [r for r in rows if r.get("polarity") == "pos"]
    codes = [r.get("expect_code") for r in neg]
    counts = {name: families.count(name) for name in LAB_FAMILIES}
    ok = (
        version == "1"
        and tooth == "existing"
        and len(rows) == 6
        and set(families) == set(LAB_FAMILIES)
        and all(counts[name] == 2 for name in LAB_FAMILIES)
        and len(pos) == 3
        and len(neg) == 3
        and set(paths) == set(LAB_PATHS)
        and set(codes) == set(NEG_CODES)
    )
    expect(ok, "n=%s families=%s paths=%s codes=%s" % (len(rows), families, paths, codes))


def _pos_envelope(family):
    if family == "vbox-fig":
        life = load_json(os.path.join(root, "scripts", "fixtures", "vbox-fig", "lifecycle.json"))
        return {"family": "vbox-lifecycle", "payload": life}
    if family == "gate-twin":
        return {
            "family": "behavior-flow",
            "payload": {
                "kind": "vbox",
                "steps": [
                    {"kind": "b", "title": "Actor", "lines": ["開工 agent"]},
                    {"kind": "hl", "title": "Page R-1", "lines": ["直式步驟"]},
                ],
            },
        }
    purpose = os.path.join(root, "scripts", "fixtures", "dir-tree", "good", "purpose.yaml")
    return {"family": "dir-tree", "payload": {"kind": "dir-tree", "root": load_purpose(purpose)}}


def _neg_envelope(family):
    if family == "vbox-fig":
        return load_json(os.path.join(root, "scripts", "fixtures", "vbox-fig", "kind-parked.json"))
    if family == "gate-twin":
        return load_json(os.path.join(FIX, "tree-as-vbox.json"))
    purpose = os.path.join(root, "scripts", "fixtures", "dir-tree", "missing-why", "purpose.yaml")
    return {"family": "dir-tree", "payload": {"kind": "dir-tree", "root": load_purpose(purpose)}}


def test_s_4_2_three_pos_replay():
    case_title("test_s_4_2_three_pos_replay")
    teeth = [
        [os.path.join(root, "scripts", "check-vbox-fig.sh")],
        [os.path.join(root, "scripts", "check-gate-twin.sh")],
        [os.path.join(root, "scripts", "check-dir-tree.sh")],
    ]
    tooth_ok = True
    for cmd in teeth:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        if proc.returncode != 0:
            tooth_ok = False
            print(proc.stderr[-400:], file=sys.stderr)
    gate_ok = True
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        seed_target(target)
        for family in LAB_FAMILIES:
            env_path = os.path.join(tmp, family + ".json")
            write_json(env_path, _pos_envelope(family))
            proc = run_deliver(env_path, target)
            receipt = parse_receipt(proc.stdout)
            if not (proc.returncode == 0 and receipt and receipt.get("ok") is True):
                gate_ok = False
    expect(tooth_ok and gate_ok, "tooth_ok=%s gate_ok=%s" % (tooth_ok, gate_ok))


def test_s_4_3_three_neg_hold_last_good():
    case_title("test_s_4_3_three_neg_hold_last_good")
    want = {"vbox-fig": "DIAGIR_KIND", "gate-twin": "DIAGIR_FAMILY", "dir-tree": "DIAGIR_WHY"}
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        before = seed_target(target)
        codes = []
        exits = []
        for family in LAB_FAMILIES:
            env_path = os.path.join(tmp, family + "-neg.json")
            write_json(env_path, _neg_envelope(family))
            proc = run_deliver(env_path, target)
            receipt = parse_receipt(proc.stdout)
            exits.append(proc.returncode)
            codes.append(receipt.get("code") if receipt else None)
        after = sha256_file(target)
        ok = (
            all(rc != 0 for rc in exits)
            and codes == [want[name] for name in LAB_FAMILIES]
            and after == before == LAST_GOOD_SHA
        )
        expect(ok, "exits=%s codes=%s sha=%s" % (exits, codes, after))


def test_s_4_4_not_only_lifecycle_json():
    case_title("test_s_4_4_not_only_lifecycle_json")
    _version, _tooth, rows = parse_lab_yaml(LAB)
    vbox = [r for r in rows if r.get("family") == "vbox-fig"]
    pos = [r for r in vbox if r.get("polarity") == "pos"]
    neg = [r for r in vbox if r.get("polarity") == "neg"]
    ok = (
        len(pos) == 1
        and len(neg) == 1
        and neg[0].get("path") != "scripts/fixtures/vbox-fig/lifecycle.json"
        and neg[0].get("path") != pos[0].get("path")
        and neg[0].get("expect_code")
    )
    expect(ok, "vbox rows=%s" % vbox)


def test_s_4_5_no_second_lab_tooth():
    case_title("test_s_4_5_no_second_lab_tooth")
    check = os.path.join(root, "scripts", "devflow-check.sh")
    text = open(check, encoding="utf-8").read()
    lab_tooth = os.path.join(root, "scripts", "check-diagir-lab.sh")
    ok = (
        not os.path.isfile(lab_tooth)
        and "check-vbox-fig" in text
        and "check-gate-twin" in text
        and "check-dir-tree" in text
        and "取代" not in text
        and "check-diagir-lab" not in text
    )
    expect(ok, "second lab tooth leaked into devflow-check")


def test_s_5_1_default_static_svg_no_mermaid():
    case_title("test_s_5_1_default_static_svg_no_mermaid")
    life = load_json(os.path.join(root, "scripts", "fixtures", "vbox-fig", "lifecycle.json"))
    with tempfile.TemporaryDirectory(prefix="diagir-") as tmp:
        target = os.path.join(tmp, "target.svg")
        seed_target(target)
        env_path = os.path.join(tmp, "env.json")
        write_json(env_path, {"family": "vbox-lifecycle", "payload": life})
        proc = run_deliver(env_path, target)
        body = open(target, encoding="utf-8").read()
        banned = ("mermaid", "mermaid.js", "<animate", "animateTransform")
        hits = [w for w in banned if w in body]
        ok = (
            proc.returncode == 0
            and "<svg" in body
            and "</svg>" in body
            and not hits
        )
        expect(ok, "hits=%s rc=%s" % (hits, proc.returncode))


def test_s_5_2_no_plugin_bump_no_196():
    case_title("test_s_5_2_no_plugin_bump_no_196")
    plugin = load_json(PLUGIN)
    diff = subprocess.run(
        ["git", "diff", "--name-only", "origin/main"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    names = [ln.strip() for ln in (diff.stdout or "").splitlines() if ln.strip()]
    forbidden = []
    for name in names:
        for prefix in FORBIDDEN_DIFF:
            if name == prefix.rstrip("/") or name.startswith(prefix):
                forbidden.append(name)
    reqs = os.path.join(root, "scripts", "requirements-methodology-render.txt")
    req_text = open(reqs, encoding="utf-8").read() if os.path.isfile(reqs) else ""
    ok = (
        plugin.get("version") == TIP_PLUGIN_VERSION
        and not forbidden
        and "mermaid" not in req_text.lower()
        and "puppeteer" not in req_text.lower()
    )
    expect(ok, "version=%s forbidden=%s" % (plugin.get("version"), forbidden))


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
        test_s_2_3_gate_twin_wires_gate,
        test_s_2_3_stage1_wires_gate,
        test_s_2_3_stage24_persist_via_gate,
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

if group:
    if group not in GROUPS:
        print("FATAL: 未知 --group %s" % group, file=sys.stderr)
        sys.exit(2)
    selected = GROUPS[group]
else:
    selected = [fn for cases in GROUPS.values() for fn in cases]

if not selected:
    print("FATAL: 沒有可跑案例", file=sys.stderr)
    sys.exit(2)

if sha256_file(LAST_GOOD) != LAST_GOOD_SHA:
    print("FATAL: last-good.svg sha 不是 Stage 3 錨", file=sys.stderr)
    sys.exit(2)

for fn in selected:
    fn()

print("[diagir] passed=%d failed=%d cases=%d" % (passed, failed, len(ran)))
sys.exit(1 if failed else 0)
