#!/bin/bash
# test-host-receipt.sh — host-stack-fit 收據鑄／核對牙
#
# 群組:
#   mint-stage4        T-1  S-1.1(stage4)／S-1.2／S-1.3／S-1.4
#   mint-rest          T-2  其餘六站 allow 鑄檔
#   verify-receipt     T-3  verify_receipt:true
#   fail-closed-claim  T-4  start-only 與主機文案
#
# 用法:
#   scripts/test-host-receipt.sh [--group NAME] [-v] [root]
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

STAGE4="$SELF_DIR/check-devstage4-graph.sh"
PROBE="$SELF_DIR/check-host-adapter.sh"
SCOPE="$SELF_DIR/check-write-scope.sh"
EXEC="$ROOT/hooks/devflow-exec.sh"
FIX="$SELF_DIR/fixtures/host-receipt"
GOOD4="$SELF_DIR/fixtures/devstage4-graph/good"
[ -x "$STAGE4" ] || chmod +x "$STAGE4"
[ -f "$STAGE4" ] || { echo "FATAL: 找不到 $STAGE4" >&2; exit 2; }
[ -d "$FIX/actions" ] || { echo "FATAL: 找不到 $FIX/actions" >&2; exit 2; }
[ -d "$GOOD4" ] || { echo "FATAL: 找不到 $GOOD4" >&2; exit 2; }

python3 - "$ROOT" "$STAGE4" "$PROBE" "$SCOPE" "$EXEC" "$FIX" "$GOOD4" "$GROUP" "$VERBOSE" <<'PY'
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

(
    root,
    stage4,
    probe,
    scope,
    exec_sh,
    fix,
    good4,
    group,
    verbose,
) = sys.argv[1:10]
verbose = verbose == "1"

SCHEMA = "devflow-host-receipt/v1"
STATION = "stage4"
SLUG = "host-stack-fit"
SCRIPT = "scripts/check-devstage4-graph.sh"
KEYS = {
    "schema",
    "station",
    "slug",
    "node",
    "script",
    "argv",
    "action_result",
    "minted_at",
    "root",
    "payload_sha256",
    "DONE",
    "stamp",
}

passed = 0
failed = 0
ran = []


def vprint(msg):
    if verbose:
        print(msg)


def case_title(name):
    line = f"=== CASE {name}"
    print(line)
    ran.append(name)


def receipt_jsons(tree):
    base = os.path.join(tree, ".devflow", "host-receipt")
    found = []
    if not os.path.isdir(base):
        return found
    for dirpath, _, filenames in os.walk(base):
        for name in filenames:
            if name.endswith(".json"):
                found.append(os.path.join(dirpath, name))
    return found


def seed_stage4(tmp):
    shutil.copytree(good4, tmp, dirs_exist_ok=True)
    dest = os.path.join(tmp, "docs", "dev", SLUG)
    os.makedirs(dest, exist_ok=True)
    src = os.path.join(fix, "docs", "dev", SLUG, "2-decision.md")
    shutil.copy2(src, os.path.join(dest, "2-decision.md"))


def run_cmd(cmd, cwd=None, env=None):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=merged)


def expect(ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓")
    else:
        failed += 1
        print("  ✗ " + detail, file=sys.stderr)


def stamp_of(data):
    raw = "|".join(
        [
            SCHEMA,
            data["station"],
            data["slug"],
            data["node"],
            data["script"],
            data["root"],
            data["action_result"],
            data["minted_at"],
            data["payload_sha256"],
            "true",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def read_json(path):
    return json.loads(open(path, encoding="utf-8").read())


def plant_receipt(tree, minted_at="2020-01-01T00:00:00Z", payload_sha="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"):
    dest = os.path.join(tree, ".devflow", "host-receipt", SLUG, "stage4.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    node = "S5-gate"
    data = {
        "schema": SCHEMA,
        "station": STATION,
        "slug": SLUG,
        "node": node,
        "script": SCRIPT,
        "argv": ["--action"],
        "action_result": "allow",
        "minted_at": minted_at,
        "root": os.path.abspath(tree),
        "payload_sha256": payload_sha,
        "DONE": True,
        "stamp": "",
    }
    data["stamp"] = stamp_of(data)
    tmp = dest + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False)
        handle.write("\n")
    os.replace(tmp, dest)
    return dest, data


def test_s_1_1_station_action_mints_receipt():
    case_title("test_s_1_1_station_action_mints_receipt")
    with tempfile.TemporaryDirectory(prefix="hr-s11-") as tmp:
        seed_stage4(tmp)
        action = os.path.join(fix, "actions", "stage4-allow.json")
        proc = run_cmd(["bash", stage4, "--action", action, tmp])
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
        ok = proc.returncode == 0 and os.path.isfile(dest)
        if ok:
            data = read_json(dest)
            ok = (
                isinstance(data, dict)
                and data.get("schema") == SCHEMA
            )
        expect(
            ok,
            f"rc={proc.returncode} dest={os.path.isfile(dest)} "
            f"out={(proc.stdout or '')[-200:]} err={(proc.stderr or '')[-200:]}",
        )


def test_s_1_2_receipt_fields_and_stamp():
    case_title("test_s_1_2_receipt_fields_and_stamp")
    with tempfile.TemporaryDirectory(prefix="hr-s12-") as tmp:
        seed_stage4(tmp)
        action = os.path.join(fix, "actions", "stage4-allow.json")
        raw = open(action, "rb").read()
        proc = run_cmd(["bash", stage4, "--action", action, tmp])
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
        ok = proc.returncode == 0 and os.path.isfile(dest)
        detail = f"rc={proc.returncode}"
        if ok:
            data = read_json(dest)
            root_abs = os.path.abspath(tmp)
            want_sha = hashlib.sha256(raw).hexdigest()
            ok = (
                set(data.keys()) == KEYS
                and data["schema"] == SCHEMA
                and data["station"] == STATION
                and data["slug"] == SLUG
                and data["node"] == "S5-gate"
                and data["script"] == SCRIPT
                and isinstance(data["argv"], list)
                and data["argv"]
                and data["argv"][0] == "--action"
                and data["action_result"] == "allow"
                and isinstance(data["minted_at"], str)
                and "T" in data["minted_at"]
                and data["minted_at"].endswith("Z")
                and data["root"] == root_abs
                and data["payload_sha256"] == want_sha
                and data["DONE"] is True
                and type(data["DONE"]) is bool
                and data["stamp"] == stamp_of(data)
                and len(data["stamp"]) == 64
                and data["stamp"].islower()
                and all(c in "0123456789abcdef" for c in data["stamp"])
            )
            detail = f"keys={sorted(data.keys())} DONE={data.get('DONE')!r} root={data.get('root')!r}"
        expect(ok, detail)


def test_s_1_3_probe_does_not_mint():
    case_title("test_s_1_3_probe_does_not_mint")
    with tempfile.TemporaryDirectory(prefix="hr-s13p-") as tmp:
        seed_stage4(tmp)
        proc = run_cmd(["bash", probe, "--probe", tmp])
        found = receipt_jsons(tmp)
        expect(
            not found,
            f"probe rc={proc.returncode} receipts={found}",
        )


def test_s_1_3_start_does_not_mint():
    case_title("test_s_1_3_start_does_not_mint")
    with tempfile.TemporaryDirectory(prefix="hr-s13s-") as tmp:
        seed_stage4(tmp)
        subprocess.run(["git", "init"], cwd=tmp, capture_output=True, check=False)
        if os.path.isfile(exec_sh):
            run_cmd(["bash", exec_sh, "start", SLUG], cwd=tmp)
        found = receipt_jsons(tmp)
        expect(not found, f"start minted {found}")


def test_s_1_3_write_cursor_does_not_mint():
    case_title("test_s_1_3_write_cursor_does_not_mint")
    with tempfile.TemporaryDirectory(prefix="hr-s13c-") as tmp:
        seed_stage4(tmp)
        proc = run_cmd(["bash", stage4, "--write-cursor", "S5-gate", SLUG, tmp])
        found = receipt_jsons(tmp)
        cursor = os.path.join(tmp, ".devstage4-cursor.json")
        expect(
            proc.returncode == 0 and os.path.isfile(cursor) and not found,
            f"rc={proc.returncode} cursor={os.path.isfile(cursor)} receipts={found}",
        )


def test_s_1_3_write_scope_does_not_mint():
    case_title("test_s_1_3_write_scope_does_not_mint")
    with tempfile.TemporaryDirectory(prefix="hr-s13w-") as tmp:
        seed_stage4(tmp)
        action = os.path.join(fix, "actions", "write-scope.json")
        run_cmd(["bash", scope, "--action", action, tmp])
        found = receipt_jsons(tmp)
        expect(not found, f"write-scope minted {found}")


def test_s_1_4_deny_does_not_change_receipt():
    case_title("test_s_1_4_deny_does_not_change_receipt")
    with tempfile.TemporaryDirectory(prefix="hr-s14d-") as tmp:
        seed_stage4(tmp)
        dest, before = plant_receipt(tmp)
        before_raw = open(dest, "rb").read()
        action = os.path.join(fix, "actions", "stage4-deny.json")
        proc = run_cmd(["bash", stage4, "--action", action, tmp])
        after_raw = open(dest, "rb").read()
        expect(
            proc.returncode == 1 and after_raw == before_raw,
            f"rc={proc.returncode} changed={after_raw != before_raw} err={(proc.stderr or '')[-200:]}",
        )


def test_s_1_4_exit2_does_not_change_receipt():
    case_title("test_s_1_4_exit2_does_not_change_receipt")
    with tempfile.TemporaryDirectory(prefix="hr-s14e-") as tmp:
        seed_stage4(tmp)
        dest, _before = plant_receipt(tmp, minted_at="2021-02-02T00:00:00Z")
        before_raw = open(dest, "rb").read()
        action = os.path.join(fix, "actions", "stage4-error.json")
        proc = run_cmd(["bash", stage4, "--action", action, tmp])
        after_raw = open(dest, "rb").read()
        expect(
            proc.returncode == 2 and after_raw == before_raw,
            f"rc={proc.returncode} changed={after_raw != before_raw}",
        )


def test_s_1_4_allow_overwrites_same_path():
    case_title("test_s_1_4_allow_overwrites_same_path")
    with tempfile.TemporaryDirectory(prefix="hr-s14a-") as tmp:
        seed_stage4(tmp)
        dest, before = plant_receipt(tmp)
        action = os.path.join(fix, "actions", "stage4-allow.json")
        proc = run_cmd(["bash", stage4, "--action", action, tmp])
        ok = proc.returncode == 0 and os.path.isfile(dest)
        if ok:
            after = read_json(dest)
            only = receipt_jsons(tmp)
            ok = (
                after["minted_at"] != before["minted_at"]
                and after["payload_sha256"] != before["payload_sha256"]
                and after["DONE"] is True
                and len(only) == 1
                and os.path.abspath(only[0]) == os.path.abspath(dest)
            )
        expect(ok, f"rc={proc.returncode} dest={dest}")


REST = (
    (
        "talk",
        "check-devtalk-graph.sh",
        "talk-allow.json",
        "devtalk-graph",
        "talk.json",
    ),
    (
        "stage2",
        "check-devstage2-graph.sh",
        "stage2-allow.json",
        "devstage2-graph",
        "stage2.json",
    ),
    (
        "stage3",
        "check-devstage3-graph.sh",
        "stage3-allow.json",
        "devstage3-graph",
        "stage3.json",
    ),
    (
        "stage5",
        "check-devstage5-graph.sh",
        "stage5-allow.json",
        "devstage5-graph",
        "stage5.json",
    ),
    (
        "stage6",
        "check-devstage6-graph.sh",
        "stage6-allow.json",
        "devstage6-graph",
        "stage6.json",
    ),
    (
        "stage7",
        "check-devstage7-graph.sh",
        "stage7-allow.json",
        "devstage7-graph",
        "stage7.json",
    ),
)


def seed_station(tmp, fixture_name):
    src = os.path.join(root, "scripts", "fixtures", fixture_name, "good")
    shutil.copytree(src, tmp, dirs_exist_ok=True)
    src_docs = os.path.join(tmp, "docs", "dev", "fixture-slug")
    dest_docs = os.path.join(tmp, "docs", "dev", SLUG)
    if os.path.isdir(src_docs) and not os.path.isdir(dest_docs):
        shutil.copytree(src_docs, dest_docs)


def mint_rest_station(station, script_name, action_name, fixture_name, dest_name):
    case_title(f"test_s_1_1_{station}_action_mints_receipt")
    script = os.path.join(root, "scripts", script_name)
    action = os.path.join(fix, "actions", action_name)
    with tempfile.TemporaryDirectory(prefix=f"hr-{station}-") as tmp:
        seed_station(tmp, fixture_name)
        proc = run_cmd(["bash", script, "--action", action, tmp])
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, dest_name)
        ok = proc.returncode == 0 and os.path.isfile(dest)
        if ok:
            data = read_json(dest)
            ok = (
                data.get("schema") == SCHEMA
                and data.get("station") == station
                and data.get("slug") == SLUG
                and data.get("script") == f"scripts/{script_name}"
                and data.get("DONE") is True
                and data.get("stamp") == stamp_of(data)
            )
        expect(
            ok,
            f"{station} rc={proc.returncode} dest={os.path.isfile(dest)} "
            f"out={(proc.stdout or '')[-180:]} err={(proc.stderr or '')[-180:]}",
        )


def test_s_1_1_talk_action_mints_receipt():
    mint_rest_station(*REST[0])


def test_s_1_1_stage2_action_mints_receipt():
    mint_rest_station(*REST[1])


def test_s_1_1_stage3_action_mints_receipt():
    mint_rest_station(*REST[2])


def test_s_1_1_stage5_action_mints_receipt():
    mint_rest_station(*REST[3])


def test_s_1_1_stage6_action_mints_receipt():
    mint_rest_station(*REST[4])


def test_s_1_1_stage7_action_mints_receipt():
    mint_rest_station(*REST[5])


MISSING = "未跑 --action"
ARMED = "已與 Claude 同等武裝"
VERIFY = os.path.join(fix, "actions", "stage4-verify.json")


def run_verify(tmp, action_path=None):
    return run_cmd(
        ["bash", stage4, "--action", action_path or VERIFY, tmp]
    )


def verify_fail_ok(proc, extra=""):
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return (
        proc.returncode != 0
        and MISSING in (proc.stderr or "")
        and ARMED not in blob
    ), f"rc={proc.returncode} extra={extra} err={(proc.stderr or '')[-200:]}"


def mint_then(tmp):
    seed_stage4(tmp)
    allow = os.path.join(fix, "actions", "stage4-allow.json")
    proc = run_cmd(["bash", stage4, "--action", allow, tmp])
    dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
    return dest, proc


def test_s_2_1_valid_receipt_verify_exit_0():
    case_title("test_s_2_1_valid_receipt_verify_exit_0")
    with tempfile.TemporaryDirectory(prefix="hr-s21-") as tmp:
        dest, minted = mint_then(tmp)
        before = open(dest, "rb").read()
        before_json = read_json(dest)
        proc = run_verify(tmp)
        after = open(dest, "rb").read()
        after_json = read_json(dest)
        ok = (
            minted.returncode == 0
            and proc.returncode == 0
            and after == before
            and after_json["stamp"] == before_json["stamp"]
            and after_json["slug"] == SLUG
            and after_json["station"] == STATION
            and after_json["script"] == SCRIPT
            and after_json["root"] == os.path.abspath(tmp)
        )
        expect(ok, f"mint={minted.returncode} verify={proc.returncode}")


def test_s_2_2_missing_receipt_fails():
    case_title("test_s_2_2_missing_receipt_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s22m-") as tmp:
        seed_stage4(tmp)
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "missing")
        expect(ok, detail)


def test_s_2_2_empty_receipt_fails():
    case_title("test_s_2_2_empty_receipt_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s22e-") as tmp:
        seed_stage4(tmp)
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").close()
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "empty")
        expect(ok, detail)


def test_s_2_2_blank_receipt_fails():
    case_title("test_s_2_2_blank_receipt_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s22b-") as tmp:
        seed_stage4(tmp)
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(" \t\n")
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "blank")
        expect(ok, detail)


def test_s_2_3_handfilled_md_fails():
    case_title("test_s_2_3_handfilled_md_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s23m-") as tmp:
        seed_stage4(tmp)
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write("- DONE\n- --action\n")
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "md")
        expect(ok, detail)


def test_s_2_3_missing_stamp_fails():
    case_title("test_s_2_3_missing_stamp_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s23s-") as tmp:
        dest, _ = mint_then(tmp)
        data = read_json(dest)
        del data["stamp"]
        open(dest, "w", encoding="utf-8").write(json.dumps(data))
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "no-stamp")
        expect(ok, detail)


def test_s_2_3_done_string_fails():
    case_title("test_s_2_3_done_string_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s23d-") as tmp:
        dest, _ = mint_then(tmp)
        data = read_json(dest)
        data["DONE"] = "true"
        open(dest, "w", encoding="utf-8").write(json.dumps(data))
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "done-str")
        expect(ok, detail)


def test_s_2_3_done_false_fails():
    case_title("test_s_2_3_done_false_fails")
    with tempfile.TemporaryDirectory(prefix="hr-s23f-") as tmp:
        dest, _ = mint_then(tmp)
        data = read_json(dest)
        data["DONE"] = False
        data["stamp"] = stamp_of({**data, "DONE": True})
        open(dest, "w", encoding="utf-8").write(json.dumps(data))
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "done-false")
        expect(ok, detail)


def _mutate_and_verify(label, mutator):
    case_title(label)
    with tempfile.TemporaryDirectory(prefix="hr-s24-") as tmp:
        dest, _ = mint_then(tmp)
        data = read_json(dest)
        mutator(data)
        open(dest, "w", encoding="utf-8").write(json.dumps(data))
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, label)
        expect(ok, detail)


def test_s_2_4_stamp_mismatch_fails():
    _mutate_and_verify(
        "test_s_2_4_stamp_mismatch_fails",
        lambda d: d.update(stamp="0" * 64),
    )


def test_s_2_4_station_mismatch_fails():
    def mut(d):
        d["station"] = "stage7"
        d["stamp"] = stamp_of(d)

    _mutate_and_verify("test_s_2_4_station_mismatch_fails", mut)


def test_s_2_4_script_mismatch_fails():
    def mut(d):
        d["script"] = "scripts/check-host-adapter.sh"
        d["stamp"] = stamp_of(d)

    _mutate_and_verify("test_s_2_4_script_mismatch_fails", mut)


def test_s_2_4_slug_mismatch_fails():
    def mut(d):
        d["slug"] = "other-slug"
        d["stamp"] = stamp_of(d)

    _mutate_and_verify("test_s_2_4_slug_mismatch_fails", mut)


def test_s_2_4_root_mismatch_fails():
    def mut(d):
        d["root"] = "/other/absolute/root"
        d["stamp"] = stamp_of(d)

    _mutate_and_verify("test_s_2_4_root_mismatch_fails", mut)


def test_s_2_5_start_only_not_armed():
    case_title("test_s_2_5_start_only_not_armed")
    with tempfile.TemporaryDirectory(prefix="hr-s25-") as tmp:
        seed_stage4(tmp)
        subprocess.run(["git", "init"], cwd=tmp, capture_output=True, check=False)
        if os.path.isfile(exec_sh):
            run_cmd(["bash", exec_sh, "start", SLUG], cwd=tmp)
        exec_json = os.path.join(tmp, ".devflow", "exec.json")
        if not os.path.isfile(exec_json):
            os.makedirs(os.path.dirname(exec_json), exist_ok=True)
            open(exec_json, "w", encoding="utf-8").write("{}\n")
        found = receipt_jsons(tmp)
        proc = run_verify(tmp)
        ok, detail = verify_fail_ok(proc, "start-only")
        expect(ok and not found, detail + f" receipts={found}")


def test_s_2_6_fail_closed_before_first_write():
    case_title("test_s_2_6_fail_closed_before_first_write")
    with tempfile.TemporaryDirectory(prefix="hr-s26-") as tmp:
        seed_stage4(tmp)
        before = run_verify(tmp)
        dest, minted = mint_then(tmp)
        after = run_verify(tmp)
        ok_before, detail_b = verify_fail_ok(before, "before")
        ok = (
            ok_before
            and minted.returncode == 0
            and after.returncode == 0
            and os.path.isfile(dest)
        )
        expect(ok, f"before={detail_b} mint={minted.returncode} after={after.returncode}")


def test_s_2_5_host_copy_has_pretooluse_and_action():
    case_title("test_s_2_5_host_copy_has_pretooluse_and_action")
    guide = open(
        os.path.join(root, "guides", "guide-dev-flow.html"), encoding="utf-8"
    ).read()
    m = re.search(r'<h2 id="host">.*?(?=<h2 |\Z)', guide, re.S)
    host = m.group(0) if m else ""
    plugin = open(os.path.join(root, "docs", "PLUGIN.md"), encoding="utf-8").read()
    skill = open(
        os.path.join(root, "skills", "dev-setup", "SKILL.md"), encoding="utf-8"
    ).read()
    ok = True
    missing = []
    for label, text in (("guide#host", host), ("PLUGIN", plugin), ("dev-setup", skill)):
        has_pt = ("無 PreToolUse" in text) or ("沒有 PreToolUse" in text)
        has_action = "--action" in text
        if not (has_pt and has_action):
            ok = False
            missing.append(f"{label} pt={has_pt} action={has_action}")
    expect(ok, ",".join(missing))


def test_s_2_7_action_verify_receipt_is_not_a_switch():
    case_title("test_s_2_7_action_verify_receipt_is_not_a_switch")
    with tempfile.TemporaryDirectory(prefix="hr-s27-") as tmp:
        seed_stage4(tmp)
        dest = os.path.join(tmp, ".devflow", "host-receipt", SLUG, "stage4.json")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").close()
        action = os.path.join(fix, "actions", "stage4-action-verify-receipt.json")
        proc = run_verify(tmp, action)
        blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
        # 空檔 + 無布林:舊 graph(stage4 未知動詞仍 allow)應鑄檔。
        # 若誤把 action 當核對開關會 verify-only 紅且含「未跑 --action」。
        minted = os.path.isfile(dest) and os.path.getsize(dest) > 0
        ok = (
            proc.returncode == 0
            and minted
            and MISSING not in (proc.stderr or "")
            and ARMED not in blob
        )
        expect(
            ok,
            f"rc={proc.returncode} minted={minted} err={(proc.stderr or '')[-160:]}",
        )


GROUPS = {
    "mint-stage4": [
        test_s_1_1_station_action_mints_receipt,
        test_s_1_2_receipt_fields_and_stamp,
        test_s_1_3_probe_does_not_mint,
        test_s_1_3_start_does_not_mint,
        test_s_1_3_write_cursor_does_not_mint,
        test_s_1_3_write_scope_does_not_mint,
        test_s_1_4_deny_does_not_change_receipt,
        test_s_1_4_exit2_does_not_change_receipt,
        test_s_1_4_allow_overwrites_same_path,
    ],
    "mint-rest": [
        test_s_1_1_talk_action_mints_receipt,
        test_s_1_1_stage2_action_mints_receipt,
        test_s_1_1_stage3_action_mints_receipt,
        test_s_1_1_stage5_action_mints_receipt,
        test_s_1_1_stage6_action_mints_receipt,
        test_s_1_1_stage7_action_mints_receipt,
    ],
    "verify-receipt": [
        test_s_2_1_valid_receipt_verify_exit_0,
        test_s_2_2_missing_receipt_fails,
        test_s_2_2_empty_receipt_fails,
        test_s_2_2_blank_receipt_fails,
        test_s_2_3_handfilled_md_fails,
        test_s_2_3_missing_stamp_fails,
        test_s_2_3_done_string_fails,
        test_s_2_3_done_false_fails,
        test_s_2_4_stamp_mismatch_fails,
        test_s_2_4_station_mismatch_fails,
        test_s_2_4_script_mismatch_fails,
        test_s_2_4_slug_mismatch_fails,
        test_s_2_4_root_mismatch_fails,
        test_s_2_7_action_verify_receipt_is_not_a_switch,
    ],
    "fail-closed-claim": [
        test_s_2_5_start_only_not_armed,
        test_s_2_6_fail_closed_before_first_write,
        test_s_2_5_host_copy_has_pretooluse_and_action,
    ],
}

if group:
    if group not in GROUPS:
        print(f"FATAL: 未知 --group {group}", file=sys.stderr)
        sys.exit(2)
    selected = GROUPS[group]
    if not selected:
        print(f"FATAL: 群組 {group} 尚無案例", file=sys.stderr)
        sys.exit(2)
else:
    selected = []
    for name, cases in GROUPS.items():
        selected.extend(cases)
    if not selected:
        print("FATAL: 沒有可跑案例", file=sys.stderr)
        sys.exit(2)

for fn in selected:
    fn()

total = passed + failed
print(f"[host-receipt] passed={passed} failed={failed} cases={len(ran)}")
if failed:
    sys.exit(1)
sys.exit(0)
PY
