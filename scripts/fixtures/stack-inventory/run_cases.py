import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

root, writer, fix, group, verbose = sys.argv[1:6]
verbose = verbose == "1"
passed = 0
failed = 0
ran = []

SCHEMA = "devflow-stack-inventory/v1"
TOP = {
    "schema",
    "written_by",
    "written_at",
    "project_kind",
    "languages",
    "declared_pins",
    "direct_deps",
    "gaps",
}
LANG = {"language", "runtime_version", "runtime_cmd"}
PIN = {"name", "version", "source"}
GAP = {"local_runtime", "requirement", "pin", "source"}


def case_title(name):
    print(f"=== CASE {name}")
    ran.append(name)


def expect(ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓")
    else:
        failed += 1
        print("  ✗ " + detail, file=sys.stderr)


def run_writer(tree, extra=None):
    cmd = ["python3", writer, "--root", tree]
    if extra:
        cmd.extend(extra)
    return subprocess.run(cmd, capture_output=True, text=True)


def seed(tmp, name):
    shutil.copytree(os.path.join(fix, name), tmp, dirs_exist_ok=True)
    os.makedirs(os.path.join(tmp, "docs", "dev"), exist_ok=True)


def load_i2(tree):
    path = os.path.join(tree, "docs", "dev", "0-inventory.json")
    return json.loads(open(path, encoding="utf-8").read()), path


def test_s_3_1_i2_path_and_required_fields():
    case_title("test_s_3_1_i2_path_and_required_fields")
    with tempfile.TemporaryDirectory(prefix="i2-s31-") as tmp:
        seed(tmp, "pack")
        proc = run_writer(tmp, ["--runtime-version", "3.9.6"])
        ok = proc.returncode == 0
        if ok:
            data, _ = load_i2(tmp)
            ok = (
                set(data.keys()) == TOP
                and data["schema"] == SCHEMA
                and data["written_by"] == "dev-setup"
                and data["written_at"].endswith("Z")
                and "T" in data["written_at"]
                and data["project_kind"] == "methodology-pack"
                and data["languages"]
                and all(set(x.keys()) == LANG for x in data["languages"])
                and all(set(x.keys()) == PIN for x in data["declared_pins"])
                and all(set(x.keys()) == PIN for x in data["direct_deps"])
                and all(set(x.keys()) == GAP for x in data["gaps"])
            )
        expect(ok, f"rc={proc.returncode} err={(proc.stderr or '')[-200:]}")


def test_s_3_2_pack_pins_markdown_it_py():
    case_title("test_s_3_2_pack_pins_markdown_it_py")
    with tempfile.TemporaryDirectory(prefix="i2-s32-") as tmp:
        seed(tmp, "pack")
        proc = run_writer(tmp, ["--runtime-version", "3.12.3"])
        data, _ = load_i2(tmp)
        pins = data["declared_pins"]
        deps = data["direct_deps"]
        hit = any(
            p["name"] == "markdown-it-py"
            and p["version"] == "4.0.0"
            and p["source"] == "scripts/requirements-methodology-render.txt"
            for p in pins
        )
        dep_hit = any(
            p["name"] == "markdown-it-py" and p["version"] == "4.0.0" for p in deps
        )
        lockish = any("lock" in (p.get("source") or "") for p in pins + deps)
        py = any(x["language"] == "Python" for x in data["languages"])
        expect(
            proc.returncode == 0 and hit and dep_hit and py and not lockish,
            f"hit={hit} dep={dep_hit} lockish={lockish}",
        )


def test_s_3_3_gap_39_vs_312_before_stage4():
    case_title("test_s_3_3_gap_39_vs_312_before_stage4")
    with tempfile.TemporaryDirectory(prefix="i2-s33-") as tmp:
        seed(tmp, "pack")
        proc = run_writer(tmp, ["--runtime-version", "3.9.6"])
        data, _ = load_i2(tmp)
        ok = False
        for gap in data.get("gaps") or []:
            if (
                str(gap.get("local_runtime", "")).startswith("3.9")
                and "3.12" in str(gap.get("requirement", ""))
                and gap.get("pin") == "markdown-it-py==4.0.0"
            ):
                ok = True
        expect(proc.returncode == 0 and ok, f"gaps={data.get('gaps')}")


def test_s_3_4_check_rewrites_stale_i2():
    case_title("test_s_3_4_check_rewrites_stale_i2")
    with tempfile.TemporaryDirectory(prefix="i2-s34-") as tmp:
        seed(tmp, "pack")
        first = run_writer(tmp, ["--runtime-version", "3.9.6"])
        data1, path = load_i2(tmp)
        time.sleep(1.1)
        pin = os.path.join(tmp, "scripts", "requirements-methodology-render.txt")
        os.utime(pin, None)
        second = run_writer(tmp, ["--check", "--runtime-version", "3.9.6"])
        data2, _ = load_i2(tmp)
        expect(
            first.returncode == 0
            and second.returncode == 0
            and data2["written_at"] >= data1["written_at"]
            and os.path.isfile(path),
            f"t1={data1.get('written_at')} t2={data2.get('written_at')}",
        )


def test_s_3_4_guidance_says_rerun():
    case_title("test_s_3_4_guidance_says_rerun")
    skill = open(
        os.path.join(root, "skills", "dev-setup", "SKILL.md"), encoding="utf-8"
    ).read()
    expect("依賴變了要重跑" in skill, "SKILL 缺「依賴變了要重跑」")


def test_s_3_5_missing_i2_check_not_success():
    case_title("test_s_3_5_missing_i2_check_not_success")
    with tempfile.TemporaryDirectory(prefix="i2-s35-") as tmp:
        seed(tmp, "pack")
        proc = run_writer(tmp, ["--check", "--runtime-version", "3.9.6"])
        blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
        expect(
            proc.returncode != 0
            and "docs/dev/0-inventory.json" in blob
            and ("broken" in blob or "stale" in blob),
            f"rc={proc.returncode} err={(proc.stderr or '')[-200:]}",
        )


def test_s_5_1_pack_and_product_same_keys():
    case_title("test_s_5_1_pack_and_product_same_keys")
    with tempfile.TemporaryDirectory(prefix="i2-s51-") as tmp:
        pack = os.path.join(tmp, "pack")
        prod = os.path.join(tmp, "prod")
        seed(pack, "pack")
        seed(prod, "product")
        run_writer(pack, ["--kind", "methodology-pack", "--runtime-version", "3.12.3"])
        run_writer(prod, ["--kind", "product", "--runtime-version", "3.12.3"])
        a, _ = load_i2(pack)
        b, _ = load_i2(prod)
        ok = (
            set(a.keys()) == set(b.keys()) == TOP
            and a["schema"] == b["schema"] == SCHEMA
            and a["project_kind"] == "methodology-pack"
            and b["project_kind"] == "product"
            and (not a["languages"] or set(a["languages"][0].keys()) == set(b["languages"][0].keys()))
            and (not a["declared_pins"] or set(a["declared_pins"][0].keys()) == PIN)
            and (not b["declared_pins"] or set(b["declared_pins"][0].keys()) == PIN)
        )
        expect(ok, f"pack={sorted(a.keys())} prod={sorted(b.keys())}")


def test_s_4_1_setup_does_not_require_i4():
    case_title("test_s_4_1_setup_does_not_require_i4")
    with tempfile.TemporaryDirectory(prefix="i4-s41-") as tmp:
        seed(tmp, "pack")
        proc = run_writer(tmp, ["--runtime-version", "3.12.3"])
        i2 = os.path.join(tmp, "docs", "dev", "0-inventory.json")
        i4 = os.path.join(tmp, "docs", "dev", "0-stack.md")
        expect(
            proc.returncode == 0 and os.path.isfile(i2) and not os.path.isfile(i4),
            f"rc={proc.returncode} i4={os.path.isfile(i4)}",
        )


def test_s_4_2_i4_content_when_asked():
    case_title("test_s_4_2_i4_content_when_asked")
    with tempfile.TemporaryDirectory(prefix="i4-s42-") as tmp:
        seed(tmp, "pack")
        proc = run_writer(
            tmp,
            [
                "--runtime-version",
                "3.12.3",
                "--write-stack",
                "--digest",
                "scripts/requirements-methodology-render.txt",
            ],
        )
        i2, _ = load_i2(tmp)
        text = open(os.path.join(tmp, "docs", "dev", "0-stack.md"), encoding="utf-8").read()
        pins_ok = all(
            (p["name"] in text and p["version"] in text) for p in i2["declared_pins"]
        )
        langs_ok = all(
            (x["language"] in text and x["runtime_version"] in text)
            for x in i2["languages"]
        )
        digest_ok = "sha256:" in text and "scripts/requirements-methodology-render.txt" in text
        expect(
            proc.returncode == 0
            and pins_ok
            and langs_ok
            and "盤點正本是 `docs/dev/0-inventory.json`" in text
            and "digest 不是 lock 正本" in text
            and digest_ok,
            f"rc={proc.returncode} pins={pins_ok} digest={digest_ok}",
        )


def test_s_4_3_no_per_slug_stack_and_lock_wins():
    case_title("test_s_4_3_no_per_slug_stack_and_lock_wins")
    with tempfile.TemporaryDirectory(prefix="i4-s43-") as tmp:
        seed(tmp, "pack")
        run_writer(tmp, ["--runtime-version", "3.12.3", "--write-stack"])
        slug_i4 = os.path.join(tmp, "docs", "dev", "host-stack-fit", "0-stack.md")
        skill = open(
            os.path.join(root, "skills", "dev-setup", "SKILL.md"), encoding="utf-8"
        ).read()
        text = open(os.path.join(tmp, "docs", "dev", "0-stack.md"), encoding="utf-8").read()
        expect(
            not os.path.isfile(slug_i4)
            and "digest 不是 lock 正本" in text
            and ("lock／pin" in text or "lock/pin" in text or "lock／pin" in skill or "pin 檔為準" in text),
            f"slug_i4={os.path.isfile(slug_i4)}",
        )


GROUPS = {
    "i2": [
        test_s_3_1_i2_path_and_required_fields,
        test_s_3_2_pack_pins_markdown_it_py,
        test_s_3_3_gap_39_vs_312_before_stage4,
        test_s_3_4_check_rewrites_stale_i2,
        test_s_3_4_guidance_says_rerun,
        test_s_3_5_missing_i2_check_not_success,
        test_s_5_1_pack_and_product_same_keys,
    ],
    "i4": [
        test_s_4_1_setup_does_not_require_i4,
        test_s_4_2_i4_content_when_asked,
        test_s_4_3_no_per_slug_stack_and_lock_wins,
    ],
}

if group:
    if group not in GROUPS:
        print(f"FATAL: 未知 --group {group}", file=sys.stderr)
        sys.exit(2)
    selected = GROUPS[group]
else:
    selected = [fn for cases in GROUPS.values() for fn in cases]

if not selected:
    print("FATAL: 沒有可跑案例", file=sys.stderr)
    sys.exit(2)

for fn in selected:
    fn()

print(f"[stack-inventory] passed={passed} failed={failed} cases={len(ran)}")
sys.exit(1 if failed else 0)
