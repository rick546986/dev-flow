#!/usr/bin/env python3
"""probe-p0-6-durable-events.py — W0 P0-6:append_events(kind=jev) 的 durable → sync/index →
read 全程 roundtrip,加多 writer lost-update 實測。

隔離:暫存 git repo + AGENTMEM_HOME 指到暫存目錄,不碰真實 ~/.agentmem。
只 import memory/agentmem 現有模組,不改 runtime。輸出 JSON 到 stdout。
用法:python3 probe-p0-6-durable-events.py <dev-flow pack root>
"""
import json, os, sqlite3, subprocess, sys, tempfile, time, shutil, hashlib

PACK = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
sys.path.insert(0, os.path.join(PACK, "memory"))
from agentmem import durable, ids, sync, store as store_mod, identity  # noqa: E402

CLI = os.path.join(PACK, "memory", "dev-memory.py")
T = tempfile.mkdtemp(prefix="p06-durable.")
HOME = tempfile.mkdtemp(prefix="p06-agentmem-home.")
os.environ["AGENTMEM_HOME"] = HOME   # in-process store 路徑也要隔離
ENV = dict(os.environ)
OUT = {"pack": PACK, "steps": []}


def step(name, **kw):
    kw["step"] = name
    OUT["steps"].append(kw)


def sh(*args, cwd=T, inp=None):
    r = subprocess.run(list(args), cwd=cwd, env=ENV, capture_output=True, text=True, input=inp)
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def cli(*args):
    return sh(sys.executable, CLI, *args)


def db_events(project_id):
    p = store_mod.runtime_db_path(project_id, T)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    cols = [r[1] for r in con.execute("PRAGMA table_info(events)")]
    rows = [dict(r) for r in con.execute("SELECT * FROM events ORDER BY occurred_at, event_id")]
    items = [dict(r) for r in con.execute("SELECT item_uid,item_type,item_id,title,text,status FROM items WHERE item_type='event'")]
    con.close()
    return cols, rows, items


# ── 0. fixture repo + dev-memory setup ───────────────────────────────────────
subprocess.run(["git", "init", "-q", "."], cwd=T, check=True)
subprocess.run(["git", "config", "user.email", "p@p"], cwd=T, check=True)
subprocess.run(["git", "config", "user.name", "p"], cwd=T, check=True)
open(os.path.join(T, "README.md"), "w").write("probe\n")
subprocess.run(["git", "add", "-A"], cwd=T, check=True)
subprocess.run(["git", "commit", "-qm", "init"], cwd=T, check=True)
rc, out, err = cli("setup", "--no-embeddings", "--name", "p06")
setup = json.loads(out) if rc == 0 else {}
project_id = setup.get("project_id")
step("00-setup", rc=rc, project_id=project_id, durable_dir=setup.get("durable_dir"),
     rebuilt=setup.get("rebuilt"), err=err[-300:])

# ── 1. append kind=jev with custom metadata(valid evt_ id)+ 一筆非法 id ────
good_id = ids.new_id("event")
custom = {"gate": "J5", "route": "HUMAN", "evidence_hash": "sha256:" + "a" * 64,
          "questionset_hash": "sha256:" + "b" * 64, "artifact_hash": "sha256:" + "c" * 64,
          "head": "0123456abcdef", "confidence": 0.42, "n_counted": False}
rec_good = {"event_id": good_id, "kind": "jev", "title": "J5 shadow evaluation feature-x",
            "body": "route=HUMAN confidence=0.42 (shadow, not counted)",
            "occurred_at": "2026-09-22T14:00:00Z", "session_id": "jev-shadow",
            "signal": "high", "paths": ["docs/dev/feature-x/7-review.md"],
            "source_type": "jev", "source_ref": "J5:feature-x",
            "jev": custom}
rec_badid = dict(rec_good, event_id="jev-feature-x-J5-0001", title="J5 shadow evaluation feature-y",
                 source_ref="J5:feature-y", occurred_at="2026-09-22T14:05:00Z")
try:
    written = durable.append_events(T, "jev-shadow", [rec_good, rec_badid])
    step("10-append-kind-jev", ok=True, written=[os.path.relpath(w, T) for w in written],
         good_id=good_id, bad_id=rec_badid["event_id"])
except Exception as e:
    step("10-append-kind-jev", ok=False, error=repr(e))
# 重跑冪等 + 同 id 不同內容拒收
try:
    w2 = durable.append_events(T, "jev-shadow", [rec_good])
    step("11-append-same-id-same-content", ok=True, written=[os.path.relpath(w, T) for w in w2])
except Exception as e:
    step("11-append-same-id-same-content", ok=False, error=repr(e))
try:
    durable.append_events(T, "jev-shadow", [dict(rec_good, body="different body")])
    step("12-append-same-id-diff-content", ok=True, note="ACCEPTED (unexpected)")
except Exception as e:
    step("12-append-same-id-diff-content", ok=False, error=str(e)[:200], note="rejected as designed")
# writer 邊界:body 含絕對路徑 / 秘密 → 應拒
for label, body in (("abs-path", "see /Users/rick/dev/proj/x.py"), ("secret", "token=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")):
    try:
        durable.append_events(T, "jev-shadow", [dict(rec_good, event_id=ids.new_id("event"), body=body)])
        step("13-writer-boundary-" + label, rejected=False)
    except Exception as e:
        step("13-writer-boundary-" + label, rejected=True, error=str(e)[:160])
# 敏感內容藏在 custom 欄位(非 title/body)→ writer 是否掃到?
try:
    durable.append_events(T, "jev-shadow", [dict(rec_good, event_id=ids.new_id("event"),
                          title="custom-field-leak", jev=dict(custom, raw="/Users/rick/secret token=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))])
    step("14-writer-boundary-custom-field", rejected=False, note="custom dict NOT scanned by writer")
except Exception as e:
    step("14-writer-boundary-custom-field", rejected=True, error=str(e)[:160])

files = sorted(os.path.relpath(os.path.join(dp, f), T) for dp, _, fs in os.walk(os.path.join(T, ".dev-flow", "events")) for f in fs)
lines = []
for f in files:
    lines += [json.loads(l) for l in open(os.path.join(T, f)) if l.strip()]
step("15-durable-file-state", files=files, n_lines=len(lines),
     custom_preserved_in_file=all("jev" in l for l in lines if l.get("kind") == "jev"))

# ── 2. full sync:CLI status 觸發 ensure_durable_mirror → rebuild_local ───────
rc, out, err = cli("status")
st = json.loads(out) if rc == 0 else {}
cols, rows, items = db_events(project_id)
jev_rows = [r for r in rows if r["kind"] == "jev"]
step("20-rebuild-via-status", rc=rc, indexed_items=st.get("indexed_items"), events_cols=cols,
     n_events=len(rows), n_jev=len(jev_rows),
     jev_rows=[{k: r[k] for k in ("event_id", "kind", "title", "source_type", "source_ref", "durable", "signal", "paths_json", "session_id")} for r in jev_rows],
     custom_column_exists=("jev" in cols or "metadata" in cols or "payload_json" in cols),
     index_text_for_jev=[i["text"] for i in items if i["item_id"] in {r["event_id"] for r in jev_rows}])
ids_after_first = sorted(r["event_id"] for r in jev_rows)
# 第二次 rebuild(強迫:改 durable 樹 → generation 變)→ 非法 id 那筆的 local id 穩定嗎?
durable.append_events(T, "jev-shadow-2", [dict(rec_good, event_id=ids.new_id("event"), title="third", session_id="jev-shadow-2")])
rc, out, err = cli("status")
cols, rows, items = db_events(project_id)
ids_after_second = sorted(r["event_id"] for r in rows if r["kind"] == "jev")
step("21-second-rebuild-id-stability", rc=rc, ids_first=ids_after_first, ids_second=ids_after_second,
     valid_id_stable=good_id in ids_after_first and good_id in ids_after_second,
     invalid_id_row_ids=[i for i in ids_after_second if i not in ids_after_first and i != good_id],
     n_jev_rows_after=len(ids_after_second))

# ── 3. read path:ask / context 能不能撈到 kind=jev ───────────────────────────
rc, out, err = cli("ask", "之前 J5 shadow evaluation 改過什麼", "--json")
ask = json.loads(out) if rc == 0 else {"raw": out[-300:], "err": err[-300:]}
hits = [r for r in ask.get("results", []) if r.get("item_type") == "event"] if isinstance(ask, dict) else []
step("30-ask-history", rc=rc, retrieval_status=ask.get("retrieval_status") if isinstance(ask, dict) else None,
     query_kind=ask.get("query_kind") if isinstance(ask, dict) else None,
     n_event_hits=len(hits), hit_titles=[h.get("title") for h in hits][:5],
     hit_keys=sorted(hits[0].keys()) if hits else [])
rc, out, err = cli("context", "--json")
ctx = json.loads(out) if rc == 0 else {}
ctx_text = ctx.get("text", "")
step("31-context-recent-events", rc=rc, jev_in_context=("J5 shadow evaluation" in ctx_text),
     snippet=[l for l in ctx_text.splitlines() if "J5" in l][:3])

# ── 4. durable-check:未 commit 的 durable 應被點名 ───────────────────────────
rc, out, err = cli("durable-check", "--local-only")
step("40-durable-check-uncommitted", rc=rc, out=out[-500:], err=err[-200:])

# ── 5. multiwriter ───────────────────────────────────────────────────────────
WRITER = r'''
import sys, json, os, time
sys.path.insert(0, sys.argv[1])
from agentmem import durable, ids
root, session, n, tag, barrier, hold = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6], sys.argv[7]
if hold != "-":
    orig = durable._existing_events
    def slow(path):
        text, seen = orig(path)
        # 讀完既有內容後停住,等另一個 writer 寫完再繼續(重現 read-modify-replace 視窗)
        while not os.path.exists(hold):
            time.sleep(0.01)
        return text, seen
    durable._existing_events = slow
while not os.path.exists(barrier):
    time.sleep(0.001)
recs = [{"event_id": ids.new_id("event"), "kind": "jev", "title": "mw " + tag + " " + str(i),
         "body": "b", "occurred_at": "2026-09-22T15:00:00Z", "session_id": session, "signal": "high"} for i in range(n)]
w = durable.append_events(root, session, recs)
print(json.dumps({"tag": tag, "written": [os.path.relpath(x, root) for x in w], "ids": [r["event_id"] for r in recs]}))
'''
def run_writers(session_a, session_b, n, deterministic):
    tag = "det" if deterministic else "race"
    barrier = os.path.join(HOME, f"barrier-{tag}-{session_a}-{session_b}")
    hold = os.path.join(HOME, f"hold-{tag}-{session_a}-{session_b}") if deterministic else "-"
    pa = subprocess.Popen([sys.executable, "-c", WRITER, os.path.join(PACK, "memory"), T, session_a, str(n), "A", barrier, hold], stdout=subprocess.PIPE, text=True, env=ENV)
    pb = subprocess.Popen([sys.executable, "-c", WRITER, os.path.join(PACK, "memory"), T, session_b, str(n), "B", barrier, "-"], stdout=subprocess.PIPE, text=True, env=ENV)
    time.sleep(0.3); open(barrier, "w").close()
    ob = json.loads(pb.communicate()[0]); 
    if deterministic:
        open(hold, "w").close()   # B 已寫完 → 放 A 續寫(A 手上仍是舊快照)
    oa = json.loads(pa.communicate()[0])
    expected = set(oa["ids"]) | set(ob["ids"])
    present = set()
    for dp, _, fs in os.walk(os.path.join(T, ".dev-flow", "events")):
        for f in fs:
            for l in open(os.path.join(dp, f)):
                if l.strip():
                    present.add(json.loads(l)["event_id"])
    lost = sorted(expected - present)
    return {"expected": len(expected), "present": len(expected & present), "lost": len(lost),
            "lost_from": sorted({("A" if i in oa["ids"] else "B") for i in lost}), "files": sorted(set(oa["written"]) | set(ob["written"]))}

step("50-multiwriter-same-session-file-race", **run_writers("shared", "shared", 40, False))
step("51-multiwriter-same-session-file-deterministic-interleave", **run_writers("shared2", "shared2", 5, True))
step("52-multiwriter-different-session-files", **run_writers("sess-a", "sess-b", 40, True))

# 檔案 lock 有嗎?
src = open(os.path.join(PACK, "memory", "agentmem", "durable.py")).read()
step("60-source-lock-scan", has_fcntl="fcntl" in src, has_flock="flock" in src or "lockf" in src,
     has_o_excl="O_EXCL" in src, note="O_EXCL 只出現在 atomic write 的 tmp 檔建立,不是跨 writer 的檔級互斥")

shutil.rmtree(T, ignore_errors=True); shutil.rmtree(HOME, ignore_errors=True)
print(json.dumps(OUT, ensure_ascii=False, indent=1))
