"""parallel-stage6 可執行契約(executable spec)。

定位:文檔校驗器(與 scripts/ 兩支同類),**不是執行引擎** —— 不派工、不碰 git、
不長駐。plugin runtime(~/.claude/plugins/local/dev-flow/)落地
parallel 模式時,其 parser/scheduler/gate 行為必須與本檔在
tests/parallel-stage6/fixtures/ 上完全一致(驗收方式見 notes/change-manifests/execution.md)。

規則正本:notes/design/parallel-stage6.md(§2 資料契約、§3 DAG、§4 wave、
§9 gate、§10 狀態機、§11 review schema)。本檔是其機械形。

外部輸入邊界:gate 檢查 1(candidate_exists)與 12(diff_applies)需要 git 事實,
由 runtime 以布林輸入提供(fixture bundle 的同名鍵);本檔只驗其餘純資料判準。
"""
import re


class ContractError(Exception):
    pass


# ---------- 路徑(鏡射 plugin devflow-lib.canonical_scope_path 規則) ----------

def canonical_scope_path(raw):
    import os
    path = raw.strip()
    if not path:
        raise ValueError("空路徑")
    if os.path.isabs(path):
        raise ValueError("不可用絕對路徑")
    if any(part == ".." for part in path.split("/")):
        raise ValueError("不可含 .. traversal")
    is_dir = path.endswith("/")
    canonical = os.path.normpath(path)
    if canonical in ("", "."):
        raise ValueError("不可為空或含糊的 repository-root 條目")
    if canonical.startswith("../"):
        raise ValueError("不可離開 Git repository root")
    if is_dir:
        canonical += "/"
    return canonical


def files_overlap(a, b):
    """相等,或一方為目錄前綴蓋住另一方(§4.3)。"""
    if a == b:
        return True
    if a.endswith("/") and b.startswith(a):
        return True
    if b.endswith("/") and a.startswith(b):
        return True
    return False


# ---------- 解析(§2) ----------

EXEC_KEYS = ("mode", "max_parallel_tasks", "rebuild_integration_on_rework")
FIELD_RE = re.compile(
    r"\s*-\s*(Covers|Files|Verify|Blocked-by|Integrate-after|Risk|Review-mode|"
    r"Semantic-conflicts-with|Intent|Boundaries|Owner):\s*(.*?)\s*$")
HEAD_RE = re.compile(r"^##\s+(T-\d+)\b\s*(.*)$")
EMPTY_MARKS = ("", "—", "-", "－", "—(選配)")


def _extract_ids(value):
    if value.strip() in EMPTY_MARKS:
        return []
    return re.findall(r"T-\d+", value)


def _parse_execution(fm_lines, errors):
    conf = {"mode": "sequential", "max_parallel_tasks": 3,
            "rebuild_integration_on_rework": True}
    i = 0
    while i < len(fm_lines):
        if re.match(r"^execution:\s*(#.*)?$", fm_lines[i]):
            i += 1
            while i < len(fm_lines) and re.match(r"^\s{2,}\S", fm_lines[i]):
                m = re.match(r"^\s{2,}([A-Za-z_]+):\s*([^#]*)", fm_lines[i])
                i += 1
                if not m:
                    continue
                key, value = m.group(1), m.group(2).strip()
                if key not in EXEC_KEYS:
                    errors.append(f"execution 未知 key:{key}(fail-closed 拒收)")
                    continue
                if key == "mode":
                    if value not in ("sequential", "parallel"):
                        errors.append(f"execution.mode 非法值:{value}(需 sequential|parallel)")
                    else:
                        conf["mode"] = value
                elif key == "max_parallel_tasks":
                    if not value.isdigit() or int(value) < 1:
                        errors.append(f"execution.max_parallel_tasks 非正整數:{value}")
                    else:
                        conf["max_parallel_tasks"] = int(value)
                else:
                    if value not in ("true", "false"):
                        errors.append(f"execution.rebuild_integration_on_rework 非 true|false:{value}")
                    else:
                        conf["rebuild_integration_on_rework"] = value == "true"
            continue
        i += 1
    return conf


def parse_5_tasks(text):
    """回傳 {"execution": conf, "tasks": [...], "errors": [...]}。
    errors 非空 = start 必須拒啟(fail-closed)。"""
    errors = []
    lines = text.splitlines()

    fm_lines = []
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            fm_lines.append(line)
    execution = _parse_execution(fm_lines, errors)

    blocks, current = [], None
    for line in lines:
        head = HEAD_RE.match(line)
        if head:
            if current:
                blocks.append(current)
            current = {"id": head.group(1), "title": head.group(2).strip(), "fields": {}}
            continue
        if re.match(r"^##\s+", line):
            if current:
                blocks.append(current)
                current = None
            continue
        if current:
            m = FIELD_RE.match(line)
            if m:
                key = m.group(1)
                # 同一 T 的保留欄不得出現兩次。FIELD_RE 前綴是 `\s*`(容許任意縮排),
                # 所以 `Boundaries:`／`Intent:` 的續行若寫成 `  - Files: …` 子項,
                # 會被當成該 T 的 Files 欄。舊行為是 last-write-wins:真正的 Files 被
                # 靜默換掉、errors 為空,而 Files 正是 task_scope() 與 gate 的
                # files_within_scope 的唯一依據 —— scope 就這樣被無聲放寬。
                # 改為 fail-closed:記 error(errors 非空 = start 必須拒啟)並保留首筆。
                if key in current["fields"]:
                    errors.append(
                        f"{current['id']} 重複保留欄「{key}」:同一 T 不得出現兩次,"
                        f"後筆不得覆蓋前筆(常見成因:`Boundaries:`／`Intent:` 續行"
                        f"寫成 `- {key}:` 子項;續行禁令見 _templates/5-tasks.md)")
                    continue
                current["fields"][key] = m.group(2).strip()
    if current:
        blocks.append(current)
    if not blocks:
        errors.append("5-tasks 找不到 ## T-n 區塊")

    tasks = []
    for block in blocks:
        tid, fields = block["id"], block["fields"]
        for name in ("Covers", "Files", "Verify", "Blocked-by"):
            if not fields.get(name):
                errors.append(f"{tid} 缺 {name}")
        files = []
        for raw in fields.get("Files", "").split(","):
            raw = raw.strip().strip("`")
            if not raw:
                continue
            try:
                files.append(canonical_scope_path(raw))
            except ValueError as e:
                errors.append(f"{tid} Files {e}")
        # Risk 欄 = Task Risk(scope 限單一 T;判準沿用 4-spec Verification Profile
        # 的 Feature Risk 同一正本,不另設分級):Task high → dedicated review 必要;
        # Feature Risk high 不強制全部 T dedicated(vnext-shared-contract §3)。
        risk = fields.get("Risk", "").strip() or "normal"
        if risk not in ("normal", "high"):
            errors.append(f"{tid} Risk 非法值:{risk}(需 normal|high)")
            risk = "normal"
        explicit_rm = fields.get("Review-mode", "").strip()
        if explicit_rm and explicit_rm not in ("wave", "dedicated"):
            errors.append(f"{tid} Review-mode 非法值:{explicit_rm}(需 wave|dedicated)")
            explicit_rm = ""
        if risk == "high" and explicit_rm == "wave":
            errors.append(f"{tid} Risk: high 不得配 Review-mode: wave(high 一律 dedicated review)")
        review_mode = explicit_rm or ("dedicated" if risk == "high" else "wave")
        tasks.append({
            "id": tid, "title": block["title"],
            "covers": fields.get("Covers", ""),
            "files": files,
            "verify": fields.get("Verify", "").strip("`"),
            "blocked_by": _extract_ids(fields.get("Blocked-by", "")),
            "integrate_after": _extract_ids(fields.get("Integrate-after", "")),
            "semantic_conflicts": _extract_ids(fields.get("Semantic-conflicts-with", "")),
            "risk": risk, "review_mode": review_mode,
        })

    ids = {t["id"] for t in tasks}
    for t in tasks:
        for field in ("blocked_by", "integrate_after", "semantic_conflicts"):
            for ref in t[field]:
                if ref == t["id"]:
                    errors.append(f"{t['id']} {field} 自我引用")
                elif ref not in ids:
                    errors.append(f"{t['id']} 引用不存在的 {ref}({field})")

    parsed = {"execution": execution, "tasks": tasks, "errors": errors}
    if not errors:
        for name, edges in (("execution", execution_edges(parsed)),
                            ("integration", integration_edges(parsed))):
            cycle = _find_cycle(ids, edges)
            if cycle:
                errors.append(f"{name} DAG 有環:{' → '.join(cycle)}")
    return parsed


# ---------- DAG(§3) ----------

def execution_edges(parsed):
    return {(p, t["id"]) for t in parsed["tasks"] for p in t["blocked_by"]}


def integration_edges(parsed):
    edges = set(execution_edges(parsed))
    edges |= {(p, t["id"]) for t in parsed["tasks"] for p in t["integrate_after"]}
    return edges


def _find_cycle(ids, edges):
    succ = {}
    for a, b in edges:
        succ.setdefault(a, []).append(b)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in ids}
    stack = []

    def dfs(node):
        color[node] = GRAY
        stack.append(node)
        for nxt in sorted(succ.get(node, [])):
            if color[nxt] == GRAY:
                return stack[stack.index(nxt):] + [nxt]
            if color[nxt] == WHITE:
                found = dfs(nxt)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for node in sorted(ids):
        if color[node] == WHITE:
            found = dfs(node)
            if found:
                return found
    return None


# ---------- Wave(§4;派生資料,不回寫) ----------

def _tnum(tid):
    return int(tid.split("-")[1])


def compute_waves(parsed, done=frozenset(), max_parallel=None):
    if parsed["errors"]:
        raise ContractError(f"5-tasks 有錯,不派生 wave:{parsed['errors']}")
    if parsed["execution"]["mode"] != "parallel":
        raise ContractError("sequential 模式不派生 wave(照 Blocked-by 拓撲序逐 T)")
    max_p = max_parallel or parsed["execution"]["max_parallel_tasks"]
    tasks = {t["id"]: t for t in parsed["tasks"]}
    conflicts = {tid: set() for tid in tasks}
    for t in parsed["tasks"]:
        for other in t["semantic_conflicts"]:
            conflicts[t["id"]].add(other)
            conflicts[other].add(t["id"])

    done = set(done)
    waves = []
    remaining = [tid for tid in sorted(tasks, key=_tnum) if tid not in done]
    while remaining:
        ready = [tid for tid in remaining
                 if all(p in done for p in tasks[tid]["blocked_by"])]
        if not ready:
            raise ContractError("無 ready task(不應發生:環已在解析期擋掉)")
        wave = []
        for tid in ready:
            if len(wave) >= max_p:
                break
            overlap = any(files_overlap(fa, fb)
                          for member in wave
                          for fa in tasks[tid]["files"] for fb in tasks[member]["files"])
            conflict = any(member in conflicts[tid] for member in wave)
            if not overlap and not conflict:
                wave.append(tid)
        waves.append(wave)
        done |= set(wave)
        remaining = [tid for tid in remaining if tid not in done]
    return waves


def task_scope(parsed, task_id):
    """task-scoped guard 契約:start --task 的 scope = 該 T 自己的 Files。"""
    for t in parsed["tasks"]:
        if t["id"] == task_id:
            return sorted(t["files"])
    raise ContractError(f"找不到 {task_id}")


# ---------- 狀態機(§10) ----------

STATES = ["PENDING", "READY", "RUNNING", "CANDIDATE", "MECHANICAL_PASS",
          "QUEUED_FOR_INTEGRATION", "INTEGRATED", "IN_REVIEW", "REWORK",
          "ACCEPTED", "BLOCKED"]

ALLOWED_TRANSITIONS = {
    ("PENDING", "READY"), ("PENDING", "BLOCKED"), ("BLOCKED", "READY"),
    ("READY", "RUNNING"), ("READY", "BLOCKED"),
    ("RUNNING", "CANDIDATE"), ("RUNNING", "BLOCKED"),
    ("CANDIDATE", "MECHANICAL_PASS"), ("CANDIDATE", "REWORK"),
    ("MECHANICAL_PASS", "QUEUED_FOR_INTEGRATION"), ("MECHANICAL_PASS", "IN_REVIEW"),
    ("QUEUED_FOR_INTEGRATION", "INTEGRATED"), ("QUEUED_FOR_INTEGRATION", "REWORK"),
    ("INTEGRATED", "IN_REVIEW"), ("INTEGRATED", "REWORK"),
    ("IN_REVIEW", "ACCEPTED"), ("IN_REVIEW", "REWORK"),
    ("IN_REVIEW", "QUEUED_FOR_INTEGRATION"),
    ("REWORK", "RUNNING"),
}


def is_legal_transition(src, dst):
    return (src, dst) in ALLOWED_TRANSITIONS


def can_tick(state):
    """只有 ACCEPTED 才能勾 5-tasks checkbox(未 Review 不可完成)。"""
    return state == "ACCEPTED"


# ---------- Mechanical Gate(§9) ----------

GATE_CHECK_IDS = ["candidate_exists", "base_sha_match", "files_within_scope",
                  "protected_untouched", "red_present_failing", "green_present_passing",
                  "red_before_green", "verify_command_match", "verify_exit_zero",
                  "s_id_present", "contract_hash_unchanged", "diff_applies",
                  "result_schema_complete", "shared_docs_untouched"]

CANDIDATE_REQUIRED_KEYS = ("schema", "feature", "task", "attempt", "branch",
                           "base_sha", "candidate_sha", "prompt_id", "prompt_version",
                           "contract_hash", "verify", "red", "green", "test_names",
                           "changed_files", "created_at")

_CONTRACT_PREFIXES = ("1-discussion", "2-decision", "3-prototype", "4-spec")
_SHARED_PREFIXES = ("5-tasks", "6-implementation-notes")


def _is_contract_path(rel):
    parts = rel.split("/")
    return (len(parts) >= 4 and parts[0] == "docs" and parts[1] == "dev"
            and any(parts[3].startswith(k) for k in _CONTRACT_PREFIXES))


def _is_shared_doc(rel):
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
    """輸入 fixture bundle(candidate/task/pinned/外部 git 事實),輸出 gate-result.v1。

    checked_at = gate 執行檢查的時刻,由呼叫端(runtime)顯式傳入;
    本檔為保決定論不自取時鐘,未傳 → 空字串(語意見設計文件 §9)。"""
    cand = bundle.get("candidate") or {}
    task = bundle.get("task") or {}
    pinned = bundle.get("pinned") or {}
    scope = [canonical_scope_path(f) for f in task.get("files", [])]
    scope += [canonical_scope_path(f) for f in bundle.get("extra_allowed", [])]
    changed = cand.get("changed_files") or []
    red, green, verify = cand.get("red"), cand.get("green"), cand.get("verify")
    names = cand.get("test_names") or []

    def in_scope(f):
        return any(s == f or (s.endswith("/") and f.startswith(s)) for s in scope)

    results = {
        "candidate_exists": bundle.get("candidate_exists") is True and bool(cand.get("candidate_sha")),
        "base_sha_match": bool(cand.get("base_sha")) and cand.get("base_sha") == pinned.get("base_sha"),
        "files_within_scope": all(in_scope(f) for f in changed),
        "protected_untouched": not any(_is_contract_path(f) for f in changed),
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


# ---------- Wave review schema(§11) ----------

def validate_wave_review(review, wave_tasks):
    errors = []
    if review.get("schema") != "devflow-wave-review.v1":
        errors.append(f"schema 非 devflow-wave-review.v1:{review.get('schema')}")
    seen = set()
    for e in review.get("tasks", []):
        tid = e.get("task")
        if tid in seen:
            errors.append(f"{tid} 重複 entry(同一 T 多筆 verdict;後筆不得覆蓋前筆,"
                          f"先 FAIL 後 PASS 必須整份退回重審)")
        seen.add(tid)
    entries = {e.get("task"): e for e in review.get("tasks", [])}
    for wt in wave_tasks:
        if wt not in entries:
            errors.append(f"缺 {wt} 的獨立 verdict")
        elif entries[wt].get("verdict") not in ("PASS", "FAIL"):
            errors.append(f"{wt} verdict 非法:{entries[wt].get('verdict')}")
    for tid in entries:
        if tid not in wave_tasks:
            errors.append(f"{tid} 不在本 wave,不得出現於 wave review")
    for entry in review.get("tasks", []):
        for finding in entry.get("findings", []):
            owner = finding.get("task")
            if not owner or owner not in wave_tasks:
                errors.append(f"finding {finding.get('id', '?')} 缺 task 歸屬或歸屬不在本 wave")
    if review.get("integration_verdict") not in ("PASS", "FAIL"):
        errors.append("缺 integration_verdict(或值非法)")
    return errors
