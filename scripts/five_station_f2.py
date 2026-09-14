#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F2 coordinator: slug store + route gate + hop eval + dual-path battery.

Key names are implementer-local (OPEN). This file does not lock a schema.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

HOPS = ("Intake", "Decide", "Spec", "Build", "Ship")
STEM_HOP = {
    "1-discussion.md": "Intake",
    "2-decision.md": "Decide",
    "3-prototype.md": "Spec",
    "4-spec.md": "Spec",
    "5-tasks.md": "Build",
    "6-implementation-notes.md": "Build",
    "7-review.md": "Ship",
}
STAGE_MD = tuple(STEM_HOP)
OFFICIAL = (
    "NEW5-HOP-OK", "NEW5-PRED-STOP", "NEW5-CAP-3", "NEW5-DECIDE-2",
    "NEW5-GOAL-2", "NEW5-MK-RED", "NEW5-SHIP-MECH", "NEW5-WAIT-RED",
    "NEW5-RUN2", "OLD7-NO-FIVE", "OLD7-FOLD-RED", "OLD7-TOKEN",
    "OLD7-SELF", "NEW5-STORE-READ", "NEW5-SEVEN-STEM", "NEW5-SPEC-SHARE",
    "NEW5-BUILD-SHARE", "NEW5-Q12-ZERO",
)
NEW5_CASES = tuple(n for n in OFFICIAL if n.startswith("NEW5-"))
OLD7_CASES = tuple(n for n in OFFICIAL if n.startswith("OLD7-"))
HOP_ALIAS = {
    "I": ("Intake", "Decide"),
    "D": ("Decide", "Spec"),
    "Sp": ("Spec", "Build"),
    "Bu": ("Build", "Ship"),
    "Sp5b": ("Spec", "Build"),
}
PLEASE = re.compile(r"要不要繼續|請人審|確認一下")
HUMAN_ATTEST = re.compile(r"Verdict attestation:\s*human:\S")
SID_NAME = re.compile(r"(?i)s[_-]\d")
OBS_FIELD = re.compile(r"(?m)^[-*]\s*觀測:")
T_BLOCK = re.compile(r"^##\s+(T-\S+)\s*(.*?)(?=^##\s|\Z)", re.M | re.S)
PROTO_HOPS = frozenset({"proto", "Stage3", "Stage 3", "Prototype"})


def fix_new5(root):
    return Path(root) / "scripts" / "fixtures" / "five-station-f2" / "new5"


def fix_old7(root):
    return Path(root) / "scripts" / "fixtures" / "five-station-f2" / "old7"


def live_slug(root):
    return Path(root) / "docs" / "dev" / "five-station-f2"


def store_path(repo_root, slug):
    return Path(repo_root) / "docs" / "dev" / slug / ".five-station" / "store"


def empty_store():
    return {
        "hop": {},
        "decide_reopen": 0,
        "goal_reopen": 0,
        "tokens": [],
        "persists": [],
        "events": [],
        "t_tries": {},
        "station": "Intake",
        "status": "",
        "seven_stem": False,
        "ask_human": False,
        "ship_done": False,
    }


def load_store(path):
    path = Path(path)
    if path.is_dir():
        path = path / "state"
    if not path.is_file():
        return empty_store(), path
    raw = json.loads(path.read_text(encoding="utf-8"))
    base = empty_store()
    base.update(raw)
    if not isinstance(base.get("hop"), dict):
        base["hop"] = {}
    return base, path


def save_store(path, data):
    path = Path(path)
    if path.suffix == "" and path.exists() and path.is_dir():
        path = path / "state"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    tmp.replace(path)
    return path


def find_store(start):
    cur = Path(start).resolve()
    if cur.is_file():
        cur = cur.parent
    for _ in range(12):
        cand = cur / ".five-station" / "store"
        if cand.is_file() or (cand.is_dir() and (cand / "state").is_file()):
            return cand if cand.is_file() else cand / "state"
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def caps_near(path):
    found = find_store(path)
    if not found:
        return None
    data, _ = load_store(found)
    hops = data.get("hop") or {}
    nums = [int(v) for v in hops.values() if str(v).isdigit() or isinstance(v, int)]
    return {
        "hop_max": max(nums) if nums else 0,
        "decide_reopen": int(data.get("decide_reopen") or 0),
        "goal_reopen": int(data.get("goal_reopen") or 0),
        "path": str(found),
        "data": data,
    }


def add_event(data, kind, who="coordinator", src="", dst="", pred="", cap="",
              escalated=False):
    data.setdefault("events", []).append({
        "kind": kind,
        "who": who,
        "from": src,
        "to": dst,
        "pred": pred,
        "cap": cap,
        "escalated": bool(escalated),
    })


def persist(repo_root, slug, hop_id, token=None, run_id="r1"):
    if hop_id in PROTO_HOPS:
        return None, "no-proto-bucket"
    if hop_id not in HOPS:
        return None, "invalid-hop"
    path = store_path(repo_root, slug)
    if ".devflow/runs/" in str(path).replace("\\", "/"):
        return None, "run-level-forbidden"
    data, path = load_store(path)
    hops = data["hop"]
    if token and token in data["tokens"]:
        return hops.get(hop_id, 0), "idempotent"
    if hop_id not in hops:
        hops[hop_id] = 0
        if token:
            data["tokens"].append(token)
        data["persists"].append({"hop": hop_id, "n": 0, "run": run_id})
        add_event(data, "persist", src=hop_id, dst=hop_id, pred="first=0",
                  cap="hop")
        save_store(path, data)
        return 0, "ok"
    current = int(hops[hop_id])
    if current >= 2:
        data["status"] = "Escalated"
        add_event(data, "cap", src=hop_id, dst=hop_id, pred="hop<=2",
                  cap="hop", escalated=True)
        save_store(path, data)
        return current, "refused"
    hops[hop_id] = current + 1
    if token:
        data["tokens"].append(token)
    data["persists"].append({"hop": hop_id, "n": hops[hop_id], "run": run_id})
    add_event(data, "persist", src=hop_id, dst=hop_id, pred="+1", cap="hop")
    save_store(path, data)
    return hops[hop_id], "ok"


def persist_stem(repo_root, slug, stem, seven_stem=False, token=None, run_id="r1"):
    if seven_stem:
        path = store_path(repo_root, slug)
        data, path = load_store(path)
        data["seven_stem"] = True
        data.setdefault("stem_buckets", {})
        data["stem_buckets"][stem] = 0
        save_store(path, data)
        return 0, "injected-seven"
    hop = STEM_HOP.get(stem)
    if hop is None:
        return None, "unknown-stem"
    if hop in PROTO_HOPS:
        return None, "no-proto-bucket"
    return persist(repo_root, slug, hop, token=token, run_id=run_id)


def record_t_retry(repo_root, slug, task_id):
    path = store_path(repo_root, slug)
    data, path = load_store(path)
    tries = data.setdefault("t_tries", {})
    tries[task_id] = int(tries.get(task_id) or 0) + 1
    save_store(path, data)
    return int(data["hop"].get("Build", 0) if "Build" in data["hop"] else -1), tries[task_id]


def decide_reopen(repo_root, slug, run_id="r1"):
    path = store_path(repo_root, slug)
    data, path = load_store(path)
    current = int(data.get("decide_reopen") or 0)
    if current >= 1:
        data["status"] = "Escalated"
        add_event(data, "cap", src="Decide", dst="Decide", pred="decide<=1",
                  cap="decide_reopen", escalated=True)
        save_store(path, data)
        return current, "refused"
    data["decide_reopen"] = current + 1
    add_event(data, "persist", src="Decide", dst="Decide", pred="reopen",
              cap="decide_reopen")
    save_store(path, data)
    return data["decide_reopen"], "ok"


def goal_reopen(repo_root, slug, run_id="r1"):
    """Goal + Decide counters in one mutation (S-1.9)."""
    path = store_path(repo_root, slug)
    data, path = load_store(path)
    g = int(data.get("goal_reopen") or 0)
    if g >= 1:
        data["status"] = "Escalated"
        add_event(data, "cap", src="Intake", dst="Decide", pred="goal<=1",
                  cap="goal_reopen", escalated=True)
        save_store(path, data)
        return (g, int(data.get("decide_reopen") or 0)), "refused"
    data["goal_reopen"] = g + 1
    d = int(data.get("decide_reopen") or 0)
    if d < 1:
        data["decide_reopen"] = d + 1
    add_event(data, "persist", src="Intake", dst="Decide", pred="goal+decide",
              cap="goal_reopen+decide_reopen")
    save_store(path, data)
    return (data["goal_reopen"], data["decide_reopen"]), "ok"


def contract_version(project_root):
    p = Path(project_root) / "devflow-contract.json"
    if not p.is_file():
        return ""
    try:
        blob = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    return str(blob.get("version") or blob.get("contract_version") or "")


def has_old7(slug_dir):
    d = Path(slug_dir)
    return any((d / name).is_file() for name in STAGE_MD)


def f3_cut_happened(project_root):
    # F2 never cuts. Reading the tree is allowed; we do not invent a cut.
    return False


def allow_legacy(project_root, slug_dir, doctor_green=False,
                 marketplace_updated=False, cache_has_hops=False,
                 synthetic_new5=False):
    if synthetic_new5:
        return False, "new5-fixture"
    declared = contract_version(project_root).startswith("2.1")
    flying = has_old7(slug_dir)
    cut = f3_cut_happened(project_root)
    # doctor / marketplace / cache are constraints, never a ticket
    _ = (doctor_green, marketplace_updated, cache_has_hops)
    if declared and (not flying) and cut:
        return False, "five"
    return True, "legacy"


def refuse_hop_reason(project_root, slug_dir, doctor_green=False):
    legacy, why = allow_legacy(project_root, slug_dir, doctor_green=doctor_green)
    if not legacy:
        return None
    # S-3.1: reason is route, never “doctor 已綠所以可 hop”
    if why == "legacy":
        ver = contract_version(project_root)
        if not ver.startswith("2.1"):
            return "路線未宣告 仍舊 7"
        if has_old7(slug_dir):
            return "仍舊 7 in-flight"
        return "仍舊 7 F3 cut 未發生"
    return "仍舊 7"


def read_text(path):
    p = Path(path)
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8")


def parse_tasks(text):
    out = []
    for match in T_BLOCK.finditer(text):
        body = match.group(2)

        def field(key):
            found = re.search(r"^-\s*%s:\s*(.*)$" % key, body, re.M)
            return found.group(1).strip() if found else None

        out.append({
            "name": match.group(1),
            "covers": field("Covers"),
            "files": field("Files"),
            "verify": field("Verify"),
            "blocked": field("Blocked-by"),
            "reviewer": (re.search(r"reviewer:\s*(\S+)", body) or type(
                "m", (), {"group": lambda _s, _i: None})()).group(1)
            if re.search(r"reviewer:\s*(\S+)", body) else None,
            "implementer": (re.search(r"implementer:\s*(\S+)", body).group(1)
                            if re.search(r"implementer:\s*(\S+)", body) else None),
            "body": body,
        })
    return out


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    raw = text[3:end]
    body = text[end + 4:]
    if body.startswith("\n"):
        body = body[1:]
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, body


def materialize_must_keep(hop_repo, dest_repo, fixture_path):
    """Copy hop-ok slug and overlay one real M defect into that tree."""
    src = Path(hop_repo) / "docs" / "dev" / "hop"
    dest = Path(dest_repo) / "docs" / "dev" / "hop"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    store = dest / ".five-station"
    if store.exists():
        shutil.rmtree(store)
    meta, body = parse_frontmatter(Path(fixture_path).read_text(encoding="utf-8"))
    overlay = meta.get("overlay")
    mid = meta.get("must-keep")
    if overlay:
        (dest / overlay).write_text(body, encoding="utf-8")
    return mid, dest


def missing_must_keep(slug_dir, extra_text=""):
    """Return first red M-id or None from slug-tree content (not sidecar tags)."""
    d = Path(slug_dir)
    blob = extra_text
    for name in STAGE_MD:
        blob += "\n" + read_text(d / name)
    tasks_txt = read_text(d / "5-tasks.md")
    notes_txt = read_text(d / "6-implementation-notes.md")
    spec_txt = read_text(d / "4-spec.md")
    tasks = parse_tasks(tasks_txt)
    if tasks_txt:
        for task in tasks:
            if task["verify"] is None:
                return "M11"
            if task["covers"] is None or task["files"] is None or task["blocked"] is None:
                return "M11"
            if task["implementer"] and task["reviewer"] and task["implementer"] == task["reviewer"]:
                return "M12"
        for match in re.finditer(r"\btest_[A-Za-z0-9_]+\b", tasks_txt + notes_txt):
            if not SID_NAME.search(match.group(0)):
                return "M1"
    if spec_txt:
        if not OBS_FIELD.search(spec_txt):
            return "M3"
        if "TBD" in spec_txt or "之後再說" in spec_txt or "實作再定" in spec_txt:
            return "M3"
        if "- lane:" not in spec_txt or "- Risk:" not in spec_txt:
            return "M7"
        if "Design Boundary Contract" not in spec_txt and "DBC" not in spec_txt:
            return "M8"
        if "f2-no-oc" in spec_txt:
            return "M4"
    if re.search(r"實作者.*1-discussion|讀了 1-discussion", blob):
        return "M2"
    if re.search(r"Human verdict:\s*ACCEPTED", blob) and not HUMAN_ATTEST.search(blob):
        if "f2-agent-accepted" in blob:
            return "M5"
    if "f2-no-g3-evidence" in blob:
        return "M6"
    if notes_txt and "verdict: PASS" in notes_txt and "原始輸出" not in notes_txt:
        return "M10"
    if "html-not-rebuilt" in blob:
        return "M13"
    if "irreversible-no-quiz" in blob:
        return "M14"
    if "token-deleted" in blob:
        return "M15"
    if "files-outside-union" in blob:
        return "M9"
    if "graph-edited" in blob or "f2-graph-touched" in blob:
        return "M16"
    return None


def pred_false(slug_dir, hop_key):
    d = Path(slug_dir)
    disc = read_text(d / "1-discussion.md")
    dec = read_text(d / "2-decision.md")
    spec = read_text(d / "4-spec.md")
    proto = read_text(d / "3-prototype.md")
    tasks = read_text(d / "5-tasks.md")
    notes = read_text(d / "6-implementation-notes.md")
    if hop_key == "I":
        if not (d / "1-discussion.md").is_file():
            return "I1"
        if "Open Questions" in disc and re.search(
                r"Open Questions[\s\S]{0,400}(?=\n## |\Z)", disc
        ):
            chunk = disc
            if "未解" in chunk and "[Assumption]" not in chunk:
                return "I2"
        if "## Real-world Context" not in disc and "legacy" not in disc.lower():
            return "I3"
        return None
    if hop_key == "D":
        if not (d / "2-decision.md").is_file():
            return "D1"
        if "## Decision" not in dec:
            return "D2"
        if "待裁決" in dec:
            return "D3"
        return None
    if hop_key == "Sp":
        if not (d / "4-spec.md").is_file():
            return "Sp1"
        if not OBS_FIELD.search(spec):
            return "Sp2"
        if "- lane:" not in spec or "- Risk:" not in spec:
            return "Sp2"
        if "待裁決" in spec:
            return "Sp3"
        if (d / "3-prototype.md").is_file() and "f2-trigger: hit" in proto:
            if not (re.search(r"Human verdict:\s*ACCEPTED", proto)
                    and HUMAN_ATTEST.search(proto)):
                return "Sp5b"
        return None
    if hop_key == "Sp5b":
        if not (d / "3-prototype.md").is_file():
            return "Sp5b"
        if not (re.search(r"Human verdict:\s*ACCEPTED", proto)
                and HUMAN_ATTEST.search(proto)):
            return "Sp5b"
        return None
    if hop_key == "Bu":
        mk = missing_must_keep(d)
        if mk:
            return mk
        if not (d / "5-tasks.md").is_file():
            return "Bu1"
        parsed = parse_tasks(tasks)
        if not parsed:
            return "Bu1"
        for task in parsed:
            if None in (task["covers"], task["files"], task["verify"], task["blocked"]):
                return "Bu1"
        if not (d / "6-implementation-notes.md").is_file():
            return "Bu2"
        if "reviewer:" in notes and "implementer:" in notes:
            impl = re.search(r"implementer:\s*(\S+)", notes)
            rev = re.search(r"reviewer:\s*(\S+)", notes)
            if impl and rev and impl.group(1) == rev.group(1):
                return "Bu2"
        return None
    return "unknown-hop"


def evaluate_hop(repo_root, slug, hop_key, inject=None):
    slug_dir = Path(repo_root) / "docs" / "dev" / slug
    data, path = load_store(store_path(repo_root, slug))
    if inject == "wait":
        data["ask_human"] = True
        add_event(data, "latch", src="Decide", dst="Spec", pred="injected-wait")
        save_store(path, data)
        return False, "injected-wait", data
    if inject == "mk-hop":
        data["station"] = "Ship"
        add_event(data, "hop", src="Build", dst="Ship", pred="injected-mk")
        save_store(path, data)
        return True, "injected-mk", data
    if inject == "ship-done":
        data["ship_done"] = True
        data["status"] = "Done"
        save_store(path, data)
        return True, "injected-done", data
    if hop_key == "Sp5b":
        false = pred_false(slug_dir, "Sp5b")
        if false:
            data["status"] = "HumanWait"
            add_event(data, "latch", src="Spec", dst="Build", pred="Sp5b",
                      cap="demo")
            save_store(path, data)
            return False, false, data
    false = pred_false(slug_dir, hop_key)
    if false:
        add_event(data, "latch", pred=false, src=HOP_ALIAS.get(hop_key, ("", ""))[0],
                  dst=HOP_ALIAS.get(hop_key, ("", ""))[1])
        save_store(path, data)
        return False, false, data
    mk = missing_must_keep(slug_dir)
    if mk:
        add_event(data, "latch", pred=mk, cap="must-keep")
        save_store(path, data)
        return False, mk, data
    src, dst = HOP_ALIAS[hop_key]
    data["station"] = dst
    add_event(data, "hop", src=src, dst=dst, pred=hop_key, cap="hop")
    save_store(path, data)
    return True, None, data


def string_only_cap_red(text):
    reds = []
    if re.search(r"第\s*3\s*次|重寫第 3", text):
        reds.append("RP-9")
    if re.search(r"Decide 重開第\s*2|第\s*2\s*次.*Decide", text):
        reds.append("RP-10")
    if re.search(r"Goal 重開第\s*2|第\s*2\s*次.*Goal", text):
        reds.append("RP-11")
    return reds


def publish_store_for_f1(repo_root, slug):
    """Copy slug store to <repo>/.five-station/store so F1 can walk up to it."""
    src = store_path(repo_root, slug)
    data, src = load_store(src)
    dest = Path(repo_root) / ".five-station" / "store"
    save_store(dest, data)
    return dest


def f1_check(path, root, caps_from_store=True):
    sys.path.insert(0, str(Path(root) / "scripts"))
    import five_station_f1 as f1
    text = Path(path).read_text(encoding="utf-8")
    result = f1.evaluate(text, path=str(path), root=str(root),
                         caps_from_store=caps_from_store)
    return result


# ---------------------------------------------------------------------------
# Battery
# ---------------------------------------------------------------------------

class Battery:
    def __init__(self, root, verbose=False):
        self.root = Path(root)
        self.verbose = verbose
        self.failures = []
        self.printed = []

    def log(self, msg):
        if self.verbose:
            print(msg)

    def case(self, name):
        if name not in OFFICIAL:
            raise SystemExit("FATAL: invented CASE name %s" % name)
        print("=== CASE %s" % name)
        self.printed.append(name)

    def check(self, ok, label):
        if ok:
            print("[ok] " + label)
            return True
        print("[FAIL] " + label)
        self.failures.append(label)
        return False

    def new5_root(self, name="synth"):
        return fix_new5(self.root) / "q12-first-persist"

    def run_q12(self):
        self.case("NEW5-Q12-ZERO")
        repo = self.new5_root()
        slug = "q12"
        store = store_path(repo, slug)
        if store.exists():
            if store.is_dir():
                for child in store.iterdir():
                    child.unlink()
            else:
                store.unlink()
        n, st = persist(repo, slug, "Spec", token="first", run_id="run-a")
        self.check(n == 0 and st == "ok", "S-1.1 first persist=0")
        n2, st2 = persist(repo, slug, "Spec", token="first", run_id="run-a")
        self.check(st2 == "idempotent" and n2 == 0, "S-1.1 retry same first write")
        n3, st3 = persist(repo, slug, "Spec", token="rewrite-1", run_id="run-a")
        self.check(n3 == 1 and st3 == "ok", "S-1.2 second persist=1")
        # first write does not consume hop<=2: one more rewrite still allowed
        n4, st4 = persist(repo, slug, "Spec", token="rewrite-2", run_id="run-a")
        self.check(n4 == 2 and st4 == "ok", "S-1.3 two rewrites after first")
        data, path = load_store(store_path(repo, slug))
        self.check(".devflow/runs/" not in str(path), "S-1.11 store not run-level")
        self.check(int(data["hop"]["Spec"]) == 2, "S-4.12 Q12 then rewrites")

        self.case("NEW5-RUN2")
        env = os.environ.copy()
        code = (
            "import sys; sys.path.insert(0, %r); import five_station_f2 as f2; "
            "d,p=f2.load_store(f2.store_path(%r, 'q12')); "
            "print(d['hop'].get('Spec'), d.get('decide_reopen'), d.get('goal_reopen')); "
            "print(p)"
        ) % (str(HERE), str(repo))
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        self.check(proc.returncode == 0 and lines and lines[0].startswith("2"),
                   "S-1.4 new process still 2/0/0")
        self.check(lines and ".devflow/runs/" not in lines[-1],
                   "S-1.11 reread slug store")

    def run_cap(self):
        repo = fix_new5(self.root)
        slug = "cap3"
        store = store_path(repo, slug)
        if store.exists() and store.is_file():
            store.unlink()
        persist(repo, slug, "Spec", token="a")
        persist(repo, slug, "Spec", token="b")
        persist(repo, slug, "Spec", token="c")
        n, st = persist(repo, slug, "Spec", token="d")
        self.case("NEW5-CAP-3")
        data, _ = load_store(store)
        fx = repo / "rp-09-store-cap3.md"
        self.check(fx.is_file() and "第 3 次" not in fx.read_text(encoding="utf-8")
                   and "第3次" not in fx.read_text(encoding="utf-8"),
                   "S-1.5 fixture has no 第 3 次")
        self.check(st == "refused" and n == 2, "S-1.5 third rewrite refused")
        self.check(data.get("status") == "Escalated", "S-1.5 Escalated")
        self.check(int(data["hop"]["Spec"]) == 2, "S-1.8 still 2")
        n2, st2 = persist(repo, slug, "Spec", token="reset")
        self.check(st2 == "refused" and n2 == 2, "S-1.8 no reset hop")
        publish_store_for_f1(repo, slug)
        result = f1_check(fx, self.root, caps_from_store=True)
        self.check(result.is_red and "RP-9" in result.red_codes,
                   "S-1.5 RP-9 reads store")

        self.case("NEW5-STORE-READ")
        fx2 = repo / "store-read-text-only.md"
        text = fx2.read_text(encoding="utf-8")
        string_red = string_only_cap_red(text)
        result_str = f1_check(fx2, self.root, caps_from_store=False)
        # injected: string teeth only, store=2, no 第 3 次 → string path green
        injected_miss = (not string_red) and (not result_str.is_red)
        self.check(injected_miss, "S-1.12/S-4.11 string-only miss is the red cell")
        self.check("第 3 次" not in text, "STORE-READ fixture has no 第 3 次")

    def run_reopen(self):
        repo = fix_new5(self.root)
        slug = "reopen"
        store = store_path(repo, slug)
        if store.exists() and store.is_file():
            store.unlink()
        persist(repo, slug, "Decide", token="d0")
        decide_reopen(repo, slug)
        n, st = decide_reopen(repo, slug)
        self.case("NEW5-DECIDE-2")
        fx = repo / "rp-10-decide-2.md"
        self.check("Decide 重開第 2" not in fx.read_text(encoding="utf-8"),
                   "S-1.6 fixture has no Decide 重開第 2")
        self.check(st == "refused" and n == 1, "S-1.6 second Decide reopen refused")
        publish_store_for_f1(repo, slug)
        result = f1_check(fx, self.root, caps_from_store=True)
        self.check(result.is_red and "RP-10" in result.red_codes,
                   "S-1.6 RP-10 reads store")

        self.case("NEW5-GOAL-2")
        slug2 = "goal"
        store2 = store_path(repo, slug2)
        if store2.exists() and store2.is_file():
            store2.unlink()
        persist(repo, slug2, "Intake", token="i0")
        persist(repo, slug2, "Decide", token="d0")
        pair, stg = goal_reopen(repo, slug2)
        self.check(stg == "ok" and pair == (1, 1),
                   "S-1.9 Goal+Decide same mutation")
        pair2, stg2 = goal_reopen(repo, slug2)
        fxg = repo / "rp-11-goal-2.md"
        self.check("Goal 重開第 2" not in fxg.read_text(encoding="utf-8"),
                   "S-1.7 fixture has no Goal 重開第 2")
        self.check(stg2 == "refused" and pair2[0] == 1, "S-1.7 second Goal refused")
        publish_store_for_f1(repo, slug2)
        result = f1_check(fxg, self.root, caps_from_store=True)
        self.check(result.is_red and "RP-11" in result.red_codes,
                   "S-1.7 RP-11 reads store")
        before = load_store(store2)[0]["hop"].get("Build")
        record_t_retry(repo, slug2, "T-1")
        after = load_store(store2)[0]
        self.check(after["t_tries"].get("T-1") == 1, "S-1.10 T retry counted")
        self.check(after["hop"].get("Build") == before, "S-1.10 T retry ≠ hop")

    def run_share(self):
        repo = fix_new5(self.root) / "spec-share"
        slug = "share"
        store = store_path(repo, slug)
        if store.exists() and store.is_file():
            store.unlink()
        persist_stem(repo, slug, "3-prototype.md", token="p")
        persist_stem(repo, slug, "4-spec.md", token="s")
        data, _ = load_store(store)
        self.case("NEW5-SPEC-SHARE")
        self.check(data["hop"].get("Spec") == 1, "S-2.2/S-4.13 same Spec bucket")
        self.check(set(data["hop"]) <= set(HOPS), "S-2.1 only five hop_id")
        self.check("N7-g1" not in data["hop"] and "N6-g2" not in data["hop"],
                   "S-2.6 old graph nodes are not hop_id")

        slug_n = "noproto"
        store_n = store_path(repo, slug_n)
        if store_n.exists() and store_n.is_file():
            store_n.unlink()
        persist_stem(repo, slug_n, "4-spec.md", token="s-only")
        data_n, _ = load_store(store_n)
        proto_file = Path(repo) / "docs" / "dev" / slug_n / "3-prototype.md"
        self.check(not proto_file.is_file(), "S-2.5 no 3-prototype.md created")
        self.check(set(data_n["hop"].keys()) == {"Spec"},
                   "S-2.5 Spec from 4-spec only; no proto/Stage3 bucket")
        n_bad, why_bad = persist(repo, slug_n, "Stage3", token="proto-bad")
        self.check(n_bad is None and why_bad == "no-proto-bucket",
                   "S-2.5 persist refuses Stage3 bucket")
        data_after, _ = load_store(store_n)
        self.check("Stage3" not in data_after["hop"] and "proto" not in data_after["hop"],
                   "S-2.5 still no proto bucket after refused persist")

        repo_b = fix_new5(self.root) / "build-share"
        store_b = store_path(repo_b, slug)
        if store_b.exists() and store_b.is_file():
            store_b.unlink()
        persist_stem(repo_b, slug, "5-tasks.md", token="t")
        persist_stem(repo_b, slug, "6-implementation-notes.md", token="n")
        data_b, _ = load_store(store_b)
        self.case("NEW5-BUILD-SHARE")
        self.check(data_b["hop"].get("Build") == 1, "S-2.3/S-4.14 same Build bucket")

        self.case("NEW5-SEVEN-STEM")
        repo_s = fix_new5(self.root)
        slug_s = "seven"
        store_s = store_path(repo_s, slug_s)
        if store_s.exists() and store_s.is_file():
            store_s.unlink()
        for stem in ("3-prototype.md", "4-spec.md", "5-tasks.md",
                     "6-implementation-notes.md"):
            persist_stem(repo_s, slug_s, stem, seven_stem=True, token=stem)
        data_s, _ = load_store(store_s)
        injected = bool(data_s.get("seven_stem")) and len(data_s.get("stem_buckets") or {}) >= 4
        self.check(injected, "S-2.4 seven-stem injection is the red cell")
        fx = repo_s / "seven-stem-inject.md"
        self.check(fx.is_file(), "seven-stem fixture present")

    def run_doctor(self):
        fx = fix_new5(self.root) / "doctor-compatible-still-old7.md"
        live = live_slug(self.root)
        reason = refuse_hop_reason(self.root, live, doctor_green=True)
        self.case("OLD7-NO-FIVE")
        self.check(reason is not None, "S-3.1 refuse hop while doctor green")
        self.check(reason and ("路線未宣告" in reason or "仍舊 7" in reason),
                   "S-3.1 reason is route")
        self.check(reason and "doctor 已綠所以可 hop" not in reason,
                   "S-3.1 reason is not doctor-green ticket")
        self.check(fx.is_file(), "SC-DOCTOR fixture present")

        self.case("OLD7-SELF")
        self.check(allow_legacy(self.root, live, doctor_green=True,
                                marketplace_updated=True, cache_has_hops=True)[0],
                   "S-3.2/S-3.6 marketplace+cache ≠ ticket")
        self.check(not f3_cut_happened(self.root), "S-3.2 F3 cut has not happened")

        self.case("OLD7-TOKEN")
        self.check(contract_version(self.root).startswith("2.0")
                   or not contract_version(self.root).startswith("2.1"),
                   "S-3.3 contract still 2.0.x")

        self.case("NEW5-Q12-ZERO")
        self.check(allow_legacy(self.root, live, cache_has_hops=True)[0],
                   "S-3.6 cache is not a fourth precondition")

    def hop_fixture(self, kind):
        return fix_new5(self.root) / {
            "I": "hop-ok",
            "D": "hop-ok",
            "Sp": "hop-ok",
            "Bu": "hop-ok",
            "Sp5b": "hop-sp5b",
            "stop": "pred-stop",
        }[kind]

    def run_hop(self, which=None):
        wanted = which or ("I", "D", "Sp", "Bu", "Sp5b", "stop")
        if "I" in wanted:
            self.case("NEW5-HOP-OK")
            repo = self.hop_fixture("I")
            slug = "hop"
            store = store_path(repo, slug)
            if store.exists() and store.is_file():
                store.unlink()
            ok, why, data = evaluate_hop(repo, slug, "I")
            self.check(ok and why is None, "S-4.15 Intake→Decide hop I1–I4")
            ev = data["events"][-1]
            self.check(ev.get("from") == "Intake" and ev.get("to") == "Decide",
                       "S-4.15 from-to")
            self.check(not data.get("ask_human") and not PLEASE.search(
                json.dumps(data, ensure_ascii=False)), "S-6.2 no please-review")
        if "D" in wanted:
            if which:
                self.case("NEW5-HOP-OK")
            repo = self.hop_fixture("D")
            slug = "hop"
            ok, why, data = evaluate_hop(repo, slug, "D")
            self.check(ok, "S-4.16 Decide→Spec hop D1–D4")
            self.check("請填 G1" not in json.dumps(data, ensure_ascii=False),
                       "S-4.16 no wait for G1")
        if "Sp" in wanted:
            if which:
                self.case("NEW5-HOP-OK")
            repo = self.hop_fixture("Sp")
            slug = "hop"
            ok, why, data = evaluate_hop(repo, slug, "Sp")
            self.check(ok, "S-4.17 Spec→Build no trigger")
            self.check(not (Path(repo) / "docs" / "dev" / slug / "3-prototype.md").is_file()
                       or "f2-trigger: hit" not in read_text(
                           Path(repo) / "docs" / "dev" / slug / "3-prototype.md"),
                       "S-4.17 no 3-prototype created")
        if "Bu" in wanted:
            if which:
                self.case("NEW5-HOP-OK")
            repo = self.hop_fixture("Bu")
            slug = "hop"
            ok, why, data = evaluate_hop(repo, slug, "Bu")
            self.check(ok, "S-4.19 Build→Ship Bu1–Bu4")
        if "stop" in wanted:
            self.case("NEW5-PRED-STOP")
            repo = self.hop_fixture("stop")
            slug = "stop"
            store = store_path(repo, slug)
            if store.exists() and store.is_file():
                store.unlink()
            ok, why, data = evaluate_hop(repo, slug, "Sp")
            blob = json.dumps(data, ensure_ascii=False)
            self.check((not ok) and why == "Sp2",
                       "S-4.3 predicate false → no hop (got %s)" % why)
            self.check(not str(why).startswith("M"),
                       "S-4.3 reason is predicate-false not Must-keep")
            self.check(data.get("station") != "Build",
                       "S-4.3 did not hop Spec→Build")
            self.check(not PLEASE.search(blob), "S-4.3 no 要不要繼續")
        if "Sp5b" in wanted:
            if which and "I" not in which:
                self.case("NEW5-HOP-OK")
            repo = self.hop_fixture("Sp5b")
            slug = "sp5b"
            store = store_path(repo, slug)
            if store.exists() and store.is_file():
                store.unlink()
            ok, why, data = evaluate_hop(repo, slug, "Sp5b")
            self.check((not ok) and data.get("status") == "HumanWait",
                       "S-4.18 Sp5b no attestation → HumanWait")

    def run_events(self):
        # three official names, hop / latch / cap
        self.case("NEW5-HOP-OK")
        repo = self.hop_fixture("I")
        _ok, _why, data = evaluate_hop(repo, "hop", "I")
        hops = [e for e in data.get("events", []) if e.get("kind") == "hop"]
        self.check(hops and hops[-1].get("who") and hops[-1].get("from"),
                   "S-5.1 hop record answers who/from/to")

        self.case("NEW5-PRED-STOP")
        repo_s = self.hop_fixture("stop")
        _ok, _why, data_s = evaluate_hop(repo_s, "stop", "Sp")
        latches = [e for e in data_s.get("events", []) if e.get("kind") == "latch"]
        self.check(latches and latches[-1].get("pred"),
                   "S-5.1 latch record has predicate")

        self.case("NEW5-CAP-3")
        repo_c = fix_new5(self.root)
        slug = "evt-cap"
        store = store_path(repo_c, slug)
        if store.exists() and store.is_file():
            store.unlink()
        persist(repo_c, slug, "Spec", token="a")
        persist(repo_c, slug, "Spec", token="b")
        persist(repo_c, slug, "Spec", token="c")
        persist(repo_c, slug, "Spec", token="d")
        data_c, path = load_store(store)
        caps = [e for e in data_c.get("events", []) if e.get("kind") == "cap"]
        self.check(caps and caps[-1].get("escalated"),
                   "S-5.1 cap record Escalated")
        self.check("STATUS.md" not in str(path) and "attempt_completed" not in str(path),
                   "S-5.2 original is slug ledger")

    def run_inject(self):
        repo = fix_new5(self.root)
        self.case("NEW5-MK-RED")
        fx = repo / "inject-mk-red.md"
        repo_h = self.hop_fixture("Bu")
        ok, why, data = evaluate_hop(repo_h, "hop", "Bu", inject="mk-hop")
        self.check(ok and why == "injected-mk",
                   "S-4.4 inject MK-red still hop is the red cell")
        self.check(fx.is_file() and "M11" in fx.read_text(encoding="utf-8"),
                   "MK-RED fixture names M11")

        self.case("NEW5-SHIP-MECH")
        fx = repo / "inject-ship-mech.md"
        ok, why, data = evaluate_hop(repo_h, "hop", "Bu", inject="ship-done")
        self.check(data.get("ship_done") and data.get("status") == "Done",
                   "S-4.5 inject mechanical Done is the red cell")
        self.check(fx.is_file(), "SHIP-MECH fixture present")

        self.case("NEW5-WAIT-RED")
        fx = repo / "inject-wait-red.md"
        ok, why, data = evaluate_hop(repo_h, "hop", "D", inject="wait")
        self.check(data.get("ask_human") or why == "injected-wait",
                   "S-4.6 inject 要不要繼續 is the red cell")
        self.check(fx.is_file(), "WAIT-RED fixture present")

        self.case("OLD7-FOLD-RED")
        old = fix_old7(self.root)
        fx = old / "inject-fold-red.md"
        slug = "folded"
        persist(old, slug, "Intake", token="fold")
        store = store_path(old, slug)
        self.check(store.is_file(), "S-4.7 inject five-station write on OLD7")
        self.check(fx.is_file(), "FOLD-RED fixture present")

    def run_must_keep(self):
        mk = fix_new5(self.root) / "must-keep"
        self.check(mk.is_dir(), "must-keep dir")
        files = sorted(p for p in mk.iterdir() if p.suffix == ".md")
        self.check(len(files) >= 16, "S-6.5 16 fixtures")
        hop_repo = self.hop_fixture("Bu")
        for path in files[:16]:
            self.case("NEW5-HOP-OK")
            dest_root = Path(tempfile.mkdtemp(prefix="f2-mk-"))
            try:
                mid, _slug_dir = materialize_must_keep(hop_repo, dest_root, path)
                if not mid:
                    stem = re.search(r"m(\d+)", path.stem, re.I)
                    mid = "M" + stem.group(1) if stem else None
                ok, why, data = evaluate_hop(dest_root, "hop", "Bu")
                self.check(ok is False,
                           "S-6.5 %s evaluate_hop refuses (ok=%s why=%s)"
                           % (path.name, ok, why))
                self.check(why and mid and mid in str(why),
                           "S-6.5 %s reason has %s (got %s)" % (path.name, mid, why))
                self.check(data.get("station") != "Ship",
                           "S-6.5 %s did not hop to Ship" % path.name)
            finally:
                shutil.rmtree(dest_root, ignore_errors=True)

    def run_old7(self):
        old = fix_old7(self.root)
        self.case("OLD7-NO-FIVE")
        self.check(old.is_dir(), "OLD7 root")
        present = [n for n in STAGE_MD if (old / n).is_file()]
        self.check(len(present) >= 7, "S-7.4 has 1–7 md")
        # legal path: do not create five-station for OLD7
        live_store = old / "docs" / "dev" / "old7" / ".five-station" / "store"
        self.check(not live_store.exists(), "S-7.4 no five-station machine")
        self.check(allow_legacy(self.root, old)[0], "S-7.1 in-flight → legacy")

        self.case("OLD7-TOKEN")
        tok = subprocess.run(
            ["bash", str(self.root / "scripts" / "check-gate-tokens.sh"),
             str(self.root)],
            capture_output=True, text=True,
        )
        self.check(tok.returncode == 0, "S-7.5 tokens still present")
        f1 = subprocess.run(
            ["bash", str(self.root / "scripts" / "test-five-station-f1.sh")],
            capture_output=True, text=True,
        )
        self.check(f1.returncode == 0, "S-7.5 F1 battery still green")

        self.case("OLD7-SELF")
        live = live_slug(self.root)
        reason = refuse_hop_reason(self.root, live)
        self.check(reason is not None, "S-7.6 this slug cannot auto-advance")
        self.check((live / "4-spec.md").is_file() and (live / "5-tasks.md").is_file(),
                   "S-7.6 still old-7 files")
        new5p = str(fix_new5(self.root).resolve())
        self.check("/docs/dev/five-station-f2" not in new5p,
                   "S-7.7 NEW5 is synthetic fixture")
        self.check("/docs/dev/five-station-simplify" not in new5p,
                   "S-7.7 not simplify slug")

    def run_selected(self, cases, hop=None, group=None):
        mapping = {
            "NEW5-Q12-ZERO": self.run_q12,
            "NEW5-RUN2": self.run_q12,
            "NEW5-CAP-3": self.run_cap,
            "NEW5-STORE-READ": self.run_cap,
            "NEW5-DECIDE-2": self.run_reopen,
            "NEW5-GOAL-2": self.run_reopen,
            "NEW5-SPEC-SHARE": self.run_share,
            "NEW5-BUILD-SHARE": self.run_share,
            "NEW5-SEVEN-STEM": self.run_share,
            "NEW5-HOP-OK": lambda: self.run_hop(which=tuple(hop) if hop else None),
            "NEW5-PRED-STOP": lambda: self.run_hop(which=("stop",)),
            "NEW5-MK-RED": self.run_inject,
            "NEW5-SHIP-MECH": self.run_inject,
            "NEW5-WAIT-RED": self.run_inject,
            "OLD7-FOLD-RED": self.run_inject,
            "OLD7-NO-FIVE": self.run_old7,
            "OLD7-TOKEN": self.run_old7,
            "OLD7-SELF": self.run_old7,
        }
        if group == "doctor-route":
            self.run_doctor()
            return
        if group == "must-keep":
            self.run_must_keep()
            return
        if group == "events":
            self.run_events()
            return
        if hop and not cases:
            self.run_hop(which=tuple(hop))
            return
        if not cases and not group:
            self.run_q12()
            self.run_cap()
            self.run_reopen()
            self.run_share()
            self.run_hop()
            self.run_inject()
            self.run_old7()
            return
        seen = set()
        for name in cases:
            fn = mapping.get(name)
            if fn is None:
                self.check(False, "unknown official case %s" % name)
                continue
            key = fn.__name__ if hasattr(fn, "__name__") else name
            if key in seen and name not in ("NEW5-HOP-OK", "NEW5-PRED-STOP"):
                continue
            seen.add(key)
            if name == "NEW5-HOP-OK":
                self.run_hop(which=tuple(hop) if hop else ("I", "D", "Sp", "Bu"))
            else:
                fn()


def build_parser():
    p = argparse.ArgumentParser(
        description="F2 five-station coordinator + dual-path battery"
    )
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--case", action="append", default=[], dest="cases",
                   help="official CASE name (repeatable)")
    p.add_argument("--group", default="",
                   help="doctor-route | must-keep | events")
    p.add_argument("--hop", action="append", default=[],
                   help="NEW5-HOP-OK slice: I D Sp Bu Sp5b")
    p.add_argument("--only", choices=("new5", "old7", "f1"),
                   help="hollow probe (exit 3); first-class flag")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv):
    # manual unknown-flag → exit 2 before argparse (argparse uses 2 anyway)
    known_prefixes = (
        "--root", "--case", "--group", "--hop", "--only", "-v", "--verbose",
        "--help", "-h",
    )
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            break
        if a.startswith("-") and a.split("=")[0] not in known_prefixes:
            print("FATAL: 未知旗標 %s" % a, file=sys.stderr)
            return 2
        i += 1
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return 2 if code not in (0, None) else 0

    for name in args.cases:
        if name not in OFFICIAL:
            print("FATAL: 未知 CASE %s" % name, file=sys.stderr)
            return 2
    for hop in args.hop:
        if hop not in HOP_ALIAS:
            print("FATAL: 未知 --hop %s" % hop, file=sys.stderr)
            return 2

    bat = Battery(args.root, verbose=args.verbose)
    if args.only == "f1":
        print("=== CASE OLD7-TOKEN")
        print("[ok] hollow: F1-only is not F2 complete")
        return 3
    if args.only == "new5":
        bat.run_q12()
        bat.run_cap()
        bat.run_reopen()
        bat.run_share()
        bat.run_hop()
        bat.run_inject()
        print("hollow --only new5")
        return 3
    if args.only == "old7":
        bat.run_old7()
        print("hollow --only old7")
        return 3

    bat.run_selected(args.cases, hop=args.hop, group=args.group or None)
    if bat.failures:
        print("failed=%d" % len(bat.failures))
        return 1
    print("failed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
