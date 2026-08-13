"""_gate_impl.py — Mechanical Gate(設計 §9;14 項機械檢查,無語意判斷)。

輸出 schema = devflow-gate-result.v1;verdict PASS ⟺ 14 項全 PASS。
兩種輸入模式:
- --bundle <file>:fixture bundle(candidate/task/pinned + 外部 git 事實布林),
  行為與方法論可執行契約 contract_ref.run_gate 完全一致(對拍面)。
- live(--slug/--task/--candidate-json):runtime 自組 bundle —— task 定義讀
  5-tasks、pinned 讀 .devflow/parallel.json、git 事實現場計算(candidate_exists/
  diff_applies),結果落 candidate.json 同目錄 gate-result.json。

exit:0 = PASS、1 = FAIL、2 = 輸入/環境錯誤(fail-closed)。
"""
import datetime
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__

from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "devflow-lib.py")).load_module()

GATE_CHECK_IDS = ["candidate_exists", "base_sha_match", "files_within_scope",
                  "protected_untouched", "red_present_failing", "green_present_passing",
                  "red_before_green", "verify_command_match", "verify_exit_zero",
                  "s_id_present", "contract_hash_unchanged", "diff_applies",
                  "result_schema_complete", "shared_docs_untouched"]

CANDIDATE_REQUIRED_KEYS = ("schema", "feature", "task", "attempt", "branch",
                           "base_sha", "candidate_sha", "prompt_id", "prompt_version",
                           "contract_hash", "verify", "red", "green", "test_names",
                           "changed_files", "created_at")

_SHARED_PREFIXES = ("5-tasks", "6-implementation-notes")


def _is_shared_doc(rel):
    """共享文件單寫者保護(設計 §12/§14):5-tasks、6-notes、STATUS、HTML twin。"""
    if rel == "docs/dev/STATUS.md":
        return True
    parts = rel.split("/")
    if len(parts) >= 4 and parts[0] == "docs" and parts[1] == "dev":
        if any(parts[3].startswith(k) for k in _SHARED_PREFIXES):
            return True
        if rel.endswith(".html"):
            return True
    return False


def _sid_matched(sid, names):
    num = sid.split("-", 1)[1]
    pattern = re.compile(rf"S-?0*{num}(?!\d)")
    return any(pattern.search(name) for name in names)


def run_gate(bundle, checked_at=""):
    """輸入 bundle,輸出 devflow-gate-result.v1(與 contract_ref 行為一致)。"""
    cand = bundle.get("candidate") or {}
    task = bundle.get("task") or {}
    pinned = bundle.get("pinned") or {}
    scope = [L.canonical_scope_path(f) for f in task.get("files", [])]
    scope += [L.canonical_scope_path(f) for f in bundle.get("extra_allowed", [])]
    changed = cand.get("changed_files") or []
    red, green, verify = cand.get("red"), cand.get("green"), cand.get("verify")
    names = cand.get("test_names") or []

    def in_scope(f):
        return any(s == f or (s.endswith("/") and f.startswith(s)) for s in scope)

    results = {
        "candidate_exists": bundle.get("candidate_exists") is True and bool(cand.get("candidate_sha")),
        "base_sha_match": bool(cand.get("base_sha")) and cand.get("base_sha") == pinned.get("base_sha"),
        "files_within_scope": all(in_scope(f) for f in changed),
        "protected_untouched": not any(L.is_contract_path(f) for f in changed),
        "red_present_failing": isinstance(red, dict) and red.get("exit_code") not in (0, None),
        "green_present_passing": isinstance(green, dict) and green.get("exit_code") == 0,
        "red_before_green": (isinstance(red, dict) and isinstance(green, dict)
                             and bool(red.get("at")) and bool(green.get("at"))
                             and red["at"] < green["at"]),
        "verify_command_match": (isinstance(verify, dict)
                                 and verify.get("command") == task.get("verify")),
        "verify_exit_zero": isinstance(verify, dict) and verify.get("exit_code") == 0,
        "s_id_present": bool(names) and all(_sid_matched(sid, names) for sid in task.get("s_ids", [])),
        "contract_hash_unchanged": (bool(cand.get("contract_hash"))
                                    and cand.get("contract_hash") == pinned.get("contract_hash")),
        "diff_applies": bundle.get("diff_applies") is True,
        "result_schema_complete": all(k in cand for k in CANDIDATE_REQUIRED_KEYS),
        "shared_docs_untouched": not any(_is_shared_doc(f) for f in changed),
    }
    checks = [{"id": cid, "status": "PASS" if results[cid] else "FAIL", "detail": ""}
              for cid in GATE_CHECK_IDS]
    return {
        "schema": "devflow-gate-result.v1",
        "feature": cand.get("feature", ""), "task": cand.get("task", ""),
        "candidate_sha": cand.get("candidate_sha", ""),
        "verdict": "PASS" if all(results.values()) else "FAIL",
        "checks": checks,
        "checked_at": checked_at,
    }


# ---------- live 模式:runtime 自組 bundle ----------

def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def _candidate_exists(root, sha, branch):
    if not sha:
        return False
    if _git(root, "cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return False
    if branch:
        return _git(root, "merge-base", "--is-ancestor", sha, branch).returncode == 0
    return True


def _diff_applies(root, tip, sha):
    """candidate 可乾淨套上 integration tip(dry-run;git merge-tree)。"""
    if not sha or not tip:
        return False
    r = _git(root, "merge-tree", "--write-tree", "--no-messages", tip, sha)
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False          # 有 conflict
    return False              # merge-tree 不可用等環境問題 → fail-closed


def _s_ids_of(covers):
    return re.findall(r"S-\d+", covers)


def _die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def main(argv):
    if not argv:
        _die("用法: _gate_impl.py <root> --bundle <file> | "
             "<root> --slug <slug> --task T-n --candidate-json <path> "
             "[--integration-tip <ref>] [--extra f1,f2] [--out <path>]")
    root = argv[0]
    opts = {}
    i = 1
    while i < len(argv):
        if argv[i].startswith("--"):
            opts[argv[i][2:]] = argv[i + 1] if i + 1 < len(argv) else ""
            i += 2
        else:
            i += 1

    if "bundle" in opts:
        try:
            bundle = json.load(open(opts["bundle"]))
        except Exception as e:
            _die(f"⛔ gate:bundle 讀取失敗({e})")
        result = run_gate(bundle, checked_at=opts.get("checked-at", ""))
    else:
        slug, task_id = opts.get("slug", ""), opts.get("task", "")
        cand_path = opts.get("candidate-json", "")
        if not (slug and task_id and cand_path):
            _die("⛔ gate:live 模式需 --slug --task --candidate-json")
        try:
            cand = json.load(open(cand_path))
        except Exception as e:
            _die(f"⛔ gate:candidate.json 讀取失敗({e})")
        tasks_path = os.path.join(root, "docs", "dev", slug, "5-tasks.md")
        try:
            parsed = L.parse_5_tasks(open(tasks_path).read())
        except OSError as e:
            _die(f"⛔ gate:5-tasks 讀取失敗({e})")
        if parsed["errors"]:
            _die("⛔ gate:5-tasks 有錯,不執行 gate:\n  " + "\n  ".join(parsed["errors"]))
        tdef = next((t for t in parsed["tasks"] if t["id"] == task_id), None)
        if tdef is None:
            _die(f"⛔ gate:5-tasks 找不到 {task_id}")
        pstate_path = os.path.join(root, ".devflow", "parallel.json")
        msg = L.shadow_mismatch(root, "parallel.json")
        if msg:
            _die(f"⛔ gate:{msg} —— 疑遭竄改(MAJOR-C),先還原或 parallel-init --reset 再 gate。")
        try:
            pstate = json.load(open(pstate_path))
        except Exception as e:
            _die(f"⛔ gate:.devflow/parallel.json 讀取失敗({e})—— 先 parallel-init/wave-open")
        trec = pstate.get("tasks", {}).get(task_id) or {}
        if trec.get("candidate_status") == "INVALIDATED_BY_UPSTREAM":
            _die(f"⛔ gate:{task_id} candidate 已標 INVALIDATED_BY_UPSTREAM,"
                 f"不得續審/整合 —— 必須從新 Wave Base 重建(等下一次 wave-open)。")
        pinned = {"base_sha": trec.get("wave_base_sha") or "",
                  "contract_hash": pstate.get("contract_hash") or ""}
        tip_ref = opts.get("integration-tip") or pstate.get("integration_branch") or "HEAD"
        tip = _git(root, "rev-parse", "--verify", "--quiet", tip_ref).stdout.strip()
        if not tip:
            tip = _git(root, "rev-parse", "HEAD").stdout.strip()
        bundle = {
            "task": {"files": tdef["files"], "verify": tdef["verify"],
                     "s_ids": _s_ids_of(tdef["covers"])},
            "pinned": pinned,
            "extra_allowed": [f for f in opts.get("extra", "").split(",") if f.strip()],
            "candidate_exists": _candidate_exists(root, cand.get("candidate_sha", ""),
                                                  cand.get("branch", "")),
            "diff_applies": _diff_applies(root, tip, cand.get("candidate_sha", "")),
            "candidate": cand,
        }
        result = run_gate(
            bundle, checked_at=datetime.datetime.now().isoformat(timespec="seconds"))
        out = opts.get("out") or os.path.join(os.path.dirname(cand_path), "gate-result.json")
        try:
            json.dump(result, open(out, "w"), ensure_ascii=False, indent=1)
        except OSError as e:
            _die(f"⛔ gate:結果寫入失敗({e})")

    print(json.dumps(result, ensure_ascii=False, indent=1))
    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
