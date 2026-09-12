#!/bin/bash
# test-diagir.sh — diagram-ir-gate wave-1 牙
#
# 群組:
#   validate      T-1  S-1.1～S-1.6
#   deliver       T-2  S-2.1／S-2.2
#   wire          T-3  S-2.3
#   route         T-4  S-3.1～S-3.5
#   lab           T-5  S-4.1～S-4.5
#   static-scope  T-6  S-5.1／S-5.2
#
# 用法:
#   scripts/test-diagir.sh [--group NAME] [-v] [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
GROUP=""
VERBOSE=0
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --group)
      GROUP=${2:-}
      [ -n "$GROUP" ] || { echo "FATAL: --group 需要名稱" >&2; exit 2; }
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    --)
      shift
      POSITIONAL+=("$@")
      break
      ;;
    -*)
      echo "FATAL: 未知旗標 $1" >&2
      exit 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
if [ "${#POSITIONAL[@]}" -gt 0 ]; then
  ROOT=$(cd "${POSITIONAL[0]}" && pwd) || exit 2
fi

python3 - "$ROOT" "$GROUP" "$VERBOSE" <<'PY'
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

root = sys.argv[1]
group = sys.argv[2]
verbose = sys.argv[3] == "1"
diagir = os.path.join(root, "scripts", "diagir.py")
fix = os.path.join(root, "scripts", "fixtures", "diagir")
last_good = os.path.join(fix, "last-good.svg")
lab_yaml = os.path.join(root, "scripts", "fixtures", "diagir-lab.yaml")
route_md = os.path.join(root, "notes", "design", "diagir-route.md")
plugin = os.path.join(root, ".claude-plugin", "plugin.json")
failures = []
checks = 0


def log(msg):
    if verbose:
        print(msg)


def case(name):
    print("=== CASE %s" % name)


def check(ok, label):
    global checks
    checks += 1
    if ok:
        print("[ok] " + label)
        return True
    print("[FAIL] " + label)
    failures.append(label)
    return False


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def run_deliver(envelope_path, out_path):
    return subprocess.run(
        [sys.executable, diagir, "deliver", envelope_path, "--out", out_path],
        cwd=root, capture_output=True, text=True,
    )


def parse_receipt(stdout):
    return json.loads(stdout)


def seed_target(work):
    target = os.path.join(work, "target.svg")
    shutil.copyfile(last_good, target)
    return target, sha256_file(target)


def want_fail(name, envelope, expect_code, work):
    case(name)
    target, before = seed_target(work)
    proc = run_deliver(envelope, target)
    receipt = parse_receipt(proc.stdout)
    after = sha256_file(target)
    ok = (
        proc.returncode != 0
        and receipt.get("ok") is False
        and receipt.get("code") == expect_code
        and receipt.get("target_replaced") is False
        and after == before
        and expect_code in proc.stderr
        and "DIAGIR_ABORT" in proc.stderr
    )
    check(ok, "%s → %s last-good held" % (name, expect_code))
    return proc, receipt, before


def want_group(name):
    return group in ("", name)


work = tempfile.mkdtemp(prefix="test-diagir-")
try:
    if want_group("validate"):
        parked = want_fail(
            "S-1.1_parked_kind_keeps_last_good",
            os.path.join(fix, "parked.json"),
            "DIAGIR_KIND",
            work,
        )
        want_fail(
            "S-1.2_empty_title_diagir_empty",
            os.path.join(fix, "empty-title.json"),
            "DIAGIR_EMPTY",
            work,
        )
        want_fail(
            "S-1.3_four_lines_diagir_lines",
            os.path.join(fix, "four-lines.json"),
            "DIAGIR_LINES",
            work,
        )
        want_fail(
            "S-1.4_tree_as_vbox_diagir_family",
            os.path.join(fix, "tree-as-vbox.json"),
            "DIAGIR_FAMILY",
            work,
        )
        want_fail(
            "S-1.5_short_why_diagir_why",
            os.path.join(fix, "dir-short-why.json"),
            "DIAGIR_WHY",
            work,
        )
        case("S-1.6_fail_emits_abort_and_receipt")
        proc, receipt, _before = parked
        keys = {"ok", "code", "knob", "abort", "delivered", "target_replaced"}
        knob = "把 kind 改回允許值，或改走路由表上的正確家族"
        check(
            keys.issubset(receipt.keys())
            and receipt.get("abort") == "DIAGIR_ABORT"
            and receipt.get("delivered") is False
            and receipt.get("target_replaced") is False
            and "DIAGIR_ABORT" in proc.stderr
            and knob in proc.stderr
            and "Traceback" not in proc.stderr,
            "S-1.6 six keys + ABORT + knob, not traceback-only",
        )

    if want_group("deliver"):
        case("S-2.1_pass_lifecycle_atomic_svg")
        target, before = seed_target(work)
        env = os.path.join(fix, "lifecycle-envelope.json")
        proc = run_deliver(env, target)
        receipt = parse_receipt(proc.stdout)
        text = open(target, encoding="utf-8").read()
        after = sha256_file(target)
        check(
            proc.returncode == 0
            and receipt.get("ok") is True
            and receipt.get("delivered") is True
            and receipt.get("target_replaced") is True
            and receipt.get("code") is None
            and os.path.isfile(target)
            and len(text) > len("<svg viewBox")
            and "<svg" in text
            and "mermaid" not in text
            and after != before
            and "</svg>" in text,
            "S-2.1 green lifecycle replaces with static SVG",
        )
        case("S-2.2_interrupt_keeps_last_good")
        target, before = seed_target(work)
        tmp = target + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write("<svg viewBox")
        after = sha256_file(target)
        tmp_txt = open(tmp, encoding="utf-8").read()
        target_txt = open(target, encoding="utf-8").read()
        check(
            after == before
            and os.path.isfile(tmp)
            and os.path.getsize(tmp) < 20
            and tmp_txt == "<svg viewBox"
            and target_txt != tmp_txt,
            "S-2.2 interrupt leaves last-good + truncated tmp",
        )
        os.remove(tmp)

    if want_group("wire"):
        builders = {
            "dir-tree": os.path.join(root, "scripts", "build-dir-tree.py"),
            "gate-twin": os.path.join(root, "scripts", "build-gate-twin.py"),
            "stage1": os.path.join(root, "scripts", "build-stage1-html.py"),
            "stage2": os.path.join(root, "scripts", "build-stage2-html.py"),
            "stage4": os.path.join(root, "scripts", "build-stage4-html.py"),
        }
        texts = {k: open(p, encoding="utf-8").read() for k, p in builders.items()}
        case("S-2.3_dir_tree_wires_gate")
        dt = texts["dir-tree"]
        check(
            "import diagir" in dt
            and "require_write" in dt
            and "pathlib.Path(path).write_text" not in dt,
            "build-dir-tree.py product write goes through diagir",
        )
        case("S-2.3_gate_twin_wires_gate")
        gt = texts["gate-twin"]
        tools = open(
            os.path.join(root, "docs", "dev", "tools", "build-gate-twin.py"),
            encoding="utf-8",
        ).read()
        check(
            "require_write" in gt
            and "out_local.write_text" not in gt
            and gt == tools,
            "build-gate-twin.py + tools copy use same gate write",
        )
        case("S-2.3_stage1_wires_gate")
        s1 = texts["stage1"]
        check(
            "import diagir" in s1
            and "require_write" in s1
            and "dest.write_text" not in s1,
            "build-stage1-html.py dest write goes through diagir",
        )
        case("S-2.3_stage2_stage4_vbox_callers_wire_gate")
        s2, s4 = texts["stage2"], texts["stage4"]
        check(
            "import diagir" in s2
            and "import diagir" in s4
            and "require_write" in s2
            and "require_write" in s4
            and "dest.write_text" not in s2
            and "dest.write_text" not in s4,
            "stage2/stage4 persist SVG/html via same gate",
        )

    if want_group("route"):
        case("S-3.1_route_table_five_rows")
        md = open(route_md, encoding="utf-8").read()
        ids = ["stage1-now", "stage2-arch", "behavior-flow", "dir-tree", "vbox-lifecycle"]
        rows = [
            ln for ln in md.splitlines()
            if ln.startswith("| ") and not ln.startswith("|---") and " id " not in ln
        ]
        # header row starts with "| id |"
        data_rows = [ln for ln in rows if not ln.startswith("| id ")]
        have = set()
        cols_ok = True
        for ln in data_rows:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) < 5 or any(not c for c in cells[:5]):
                cols_ok = False
            if cells:
                have.add(cells[0])
        check(
            have == set(ids) and len(data_rows) == 5 and cols_ok
            and "stage1-review-ui-contract" in md
            and "stage2-review-ui-contract" in md
            and "vbox-fig-contract" in md
            and "dir-tree-contract" in md,
            "route table five rows + four columns + contracts",
        )
        want_fail(
            "S-3.2_stage1_as_lifecycle_family",
            os.path.join(fix, "stage1-as-lifecycle.json"),
            "DIAGIR_FAMILY",
            work,
        )
        want_fail(
            "S-3.3_dir_as_vbox_family",
            os.path.join(fix, "dir-as-vbox.json"),
            "DIAGIR_FAMILY",
            work,
        )
        proc, receipt, _b = want_fail(
            "S-3.4_missing_family_not_guessed",
            os.path.join(fix, "missing-family.json"),
            "DIAGIR_FAMILY",
            work,
        )
        blob = (proc.stdout + proc.stderr).lower()
        check(
            "已選" not in proc.stdout + proc.stderr
            and "auto" not in blob
            and "detect" not in blob,
            "S-3.4 no auto/detect/已選 guess",
        )
        case("S-3.5_five_entries_map_five_rows")
        route_run = subprocess.run(
            [sys.executable, diagir, "route"],
            cwd=root, capture_output=True, text=True,
        )
        out = route_run.stdout
        entries = [
            "build-stage1-html.py --action",
            "build-stage2-html.py --action",
            "build-gate-twin.py",
            "build-dir-tree.py",
            "build-vbox-fig.py",
        ]
        mapped = all(md.count(e) >= 1 and out.count(e.split()[0]) >= 1 for e in entries)
        md_ok = all(md.count(e) == 1 for e in (
            "build-stage1-html.py --action",
            "build-stage2-html.py --action",
            "build-dir-tree.py",
        ))
        row_by_id = {}
        for ln in md.splitlines():
            if not ln.startswith("| "):
                continue
            cells = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
            if cells and cells[0] in ids:
                row_by_id[cells[0]] = cells
        stage1_not_vbox = "build-vbox-fig.py" not in row_by_id.get("stage1-now", [])
        dir_row = row_by_id.get("dir-tree", [])
        dir_not_vbox = (
            dir_row
            and not any("build-vbox-fig" in c or "build-gate-twin" in c for c in dir_row)
        )
        extra_ids = have - set(ids)
        check(
            route_run.returncode == 0
            and "ROUTE_ROWS 5" in out
            and extra_ids == set()
            and len(row_by_id) == 5
            and stage1_not_vbox
            and dir_not_vbox
            and "hosted" not in md.lower()
            and md_ok
            and mapped,
            "S-3.5 five entries map; no sixth family",
        )

    if want_group("lab"):
        case("S-4.1_lab_index_six_rows")
        raw = open(lab_yaml, encoding="utf-8").read()
        paths = [
            "scripts/fixtures/vbox-fig/lifecycle.json",
            "scripts/fixtures/vbox-fig/kind-parked.json",
            "scripts/fixtures/gate-twin/fig-long-label",
            "scripts/fixtures/gate-twin/fig-tree-ascii",
            "scripts/fixtures/dir-tree/good",
            "scripts/fixtures/dir-tree/missing-why",
        ]
        fams = re.findall(r"family:\s*(\S+)", raw)
        pols = re.findall(r"polarity:\s*(\S+)", raw)
        codes = re.findall(r"expect_code:\s*(\S+)", raw)
        check(
            "version: 1" in raw
            and raw.count("tooth_language: existing") >= 1
            and set(fams) == {"vbox-fig", "gate-twin", "dir-tree"}
            and fams.count("vbox-fig") == 2
            and fams.count("gate-twin") == 2
            and fams.count("dir-tree") == 2
            and pols.count("pos") == 3
            and pols.count("neg") == 3
            and set(codes) == {"DIAGIR_KIND", "DIAGIR_FAMILY", "DIAGIR_WHY"}
            and all(p in raw for p in paths),
            "S-4.1 six rows / three families / expect_code",
        )
        case("S-4.2_three_pos_replay")
        vbox = subprocess.run(
            [sys.executable, os.path.join(root, "scripts", "build-vbox-fig.py"),
             "--fixture", "lifecycle"],
            cwd=root, capture_output=True, text=True,
        )
        dtree = subprocess.run(
            [sys.executable, os.path.join(root, "scripts", "build-dir-tree.py"),
             "--fixture", "good"],
            cwd=root, capture_output=True, text=True,
        )
        # gate-twin tooth already covers fig-long-label; replay builder on that fixture
        long_label = os.path.join(
            root, "scripts", "fixtures", "gate-twin", "fig-long-label",
            "docs", "dev", "demo", "4-spec.md",
        )
        twin_ok = os.path.isfile(long_label)
        pos_ok = True
        for env_name in ("lifecycle-envelope.json", "behavior-flow-pos.json",
                         "dir-tree-pos.json"):
            t, _b = seed_target(work)
            p = run_deliver(os.path.join(fix, env_name), t)
            rec = parse_receipt(p.stdout)
            if not (p.returncode == 0 and rec.get("ok") is True):
                pos_ok = False
        check(
            vbox.returncode == 0
            and dtree.returncode == 0
            and twin_ok
            and pos_ok,
            "S-4.2 three pos teeth/gate replay",
        )
        case("S-4.3_three_neg_hold_last_good")
        target, before = seed_target(work)
        neg = [
            (os.path.join(root, "scripts", "fixtures", "vbox-fig", "kind-parked.json"),
             "DIAGIR_KIND"),
            (os.path.join(fix, "tree-as-vbox.json"), "DIAGIR_FAMILY"),
            (os.path.join(fix, "dir-short-why.json"), "DIAGIR_WHY"),
        ]
        held = True
        codes_ok = True
        for path, code in neg:
            p = run_deliver(path, target)
            rec = parse_receipt(p.stdout)
            if p.returncode == 0 or rec.get("code") != code:
                codes_ok = False
            if sha256_file(target) != before:
                held = False
        check(codes_ok and held, "S-4.3 three neg hold last-good")
        case("S-4.4_not_only_lifecycle_json")
        check(
            "scripts/fixtures/vbox-fig/kind-parked.json" in raw
            and raw.find("kind-parked.json") != raw.find("lifecycle.json")
            and "DIAGIR_KIND" in raw,
            "S-4.4 vbox neg ≠ lifecycle.json",
        )
        case("S-4.5_no_second_lab_tooth")
        lab_sh = os.path.join(root, "scripts", "check-diagir-lab.sh")
        check_sh = open(
            os.path.join(root, "scripts", "devflow-check.sh"), encoding="utf-8"
        ).read()
        scripts = os.listdir(os.path.join(root, "scripts"))
        extra = [n for n in scripts if n.startswith("check-diagir")]
        replaces_lab = (
            "check-diagir-lab" in check_sh
            or "diagir-lab.yaml" in check_sh
        )
        check(
            not os.path.isfile(lab_sh)
            and extra == []
            and "check-vbox-fig.sh" in check_sh
            and "check-gate-twin.sh" in check_sh
            and "check-dir-tree.sh" in check_sh
            and not replaces_lab,
            "S-4.5 no second lab tooth; existing three remain",
        )

    if want_group("static-scope"):
        case("S-5.1_default_static_svg_no_mermaid")
        target, _b = seed_target(work)
        proc = run_deliver(os.path.join(fix, "lifecycle-envelope.json"), target)
        text = open(target, encoding="utf-8").read()
        banned = ("mermaid", "mermaid.js", "<animate", "animateTransform")
        check(
            proc.returncode == 0
            and "<svg" in text
            and "</svg>" in text
            and all(tok not in text for tok in banned),
            "S-5.1 static SVG, no mermaid/animate",
        )
        case("S-5.2_no_plugin_bump_no_196")
        ver = json.loads(open(plugin, encoding="utf-8").read()).get("version")
        fork = "origin/main"
        base_run = subprocess.run(
            ["git", "merge-base", fork, "HEAD"],
            cwd=root, capture_output=True, text=True,
        )
        scope = base_run.stdout.strip() or fork
        plugin_diff = subprocess.run(
            ["git", "diff", scope, "--", ".claude-plugin/plugin.json"],
            cwd=root, capture_output=True, text=True,
        )
        tracked = subprocess.run(
            ["git", "diff", "--name-only", scope],
            cwd=root, capture_output=True, text=True,
        ).stdout.splitlines()
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=root, capture_output=True, text=True,
        ).stdout.splitlines()
        names = tracked + untracked
        banned_paths = (
            "docs/dev/b8-gate-twin-review-ui/",
            "docs/dev/STATUS.md",
            "docs/dev/HISTORY.md",
            "docs/dev/HISTORY.html",
            "docs/dev/integration-before-verdict/",
        )
        hit = [n for n in names if any(n == b.rstrip("/") or n.startswith(b) for b in banned_paths)]
        check(
            ver == "3.23.3"
            and plugin_diff.stdout.strip() == ""
            and hit == [],
            "S-5.2 plugin version unchanged; no #196 / IBV / STATUS files",
        )
finally:
    shutil.rmtree(work, ignore_errors=True)

print("checks=%d" % checks)
if failures:
    print("❌ FAIL:%d/%d" % (len(failures), checks))
    for item in failures:
        print("  - " + item)
    sys.exit(1)
if checks == 0:
    print("FATAL: no cases in group %r" % group, file=sys.stderr)
    sys.exit(2)
print("✅ PASS:diagir %s %d/%d" % (group or "all", checks, checks))
sys.exit(0)
PY
