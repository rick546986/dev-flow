#!/bin/bash
# probe-p0-5-run-lifecycle.sh — W0 P0-5:Stage6→Stage7 與 bare Stage7 的 run lifecycle 實測。
# 在暫存假 repo 上跑真 hooks/devflow-exec.sh + hooks/devflow-obs.sh,逐步 dump
# .devflow/exec.json 的 run_id/schema/phase/review_unlocked 與 .devflow/runs/ 內容。
# 只讀 repo 內 runtime,不改 runtime;輸出 JSON 到 stdout(evidence 檔由呼叫端重導)。
# 用法:bash probe-p0-5-run-lifecycle.sh <dev-flow pack root>
set -u
PACK=$(cd "${1:-.}" && pwd)
H="$PACK/hooks"
T=$(mktemp -d "${TMPDIR:-/tmp}/p05-lifecycle.XXXXXX")
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/docs/dev/f1" "$T/docs/dev/bare" "$T/src"
cd "$T" || exit 2
git init -q . && git config user.email p@p && git config user.name p
printf -- "---\nstatus: approved\n---\n" > docs/dev/f1/4-spec.md
printf -- "---\nstatus: approved\n---\n" > docs/dev/bare/4-spec.md
printf '%s\n' '## T-1 probe' '- Covers: R-1' '- Files: src/a.py' '- Verify: `true`' '- Blocked-by: —' > docs/dev/f1/5-tasks.md
echo "notes" > docs/dev/f1/6-implementation-notes.md
echo "a" > src/a.py
git add -A >/dev/null && git commit -qm init

snap() { # snap <label> <rc> <stdout-tail>
  "$PACK/hooks/../scripts/../hooks/devflow-python-lib.sh" >/dev/null 2>&1 || true
  python3 - "$1" "$2" "$3" <<'PY'
import json, os, sys, glob
label, rc, out = sys.argv[1], sys.argv[2], sys.argv[3]
st = None
if os.path.exists(".devflow/exec.json"):
    d = json.load(open(".devflow/exec.json"))
    st = {k: d.get(k) for k in ("slug","schema","run_id","phase","review_unlocked","task","mode")}
    st["scope"] = d.get("scope"); st["baseline_n"] = len(d.get("baseline", {}))
runs = sorted(os.path.relpath(p, ".devflow/runs") for p in glob.glob(".devflow/runs/*/**", recursive=True) if os.path.isfile(p))
sentinel = os.path.exists(".git/devflow-armed")
print(json.dumps({"step": label, "rc": int(rc), "exec_json": st, "sentinel": sentinel,
                  "runs_files": runs, "stdout_tail": out[-400:]}, ensure_ascii=False))
PY
}
X() { OUT=$("$H/devflow-exec.sh" "$@" 2>&1); RC=$?; }
OBS() { OUT=$(printf '%s' "$1" | "$H/devflow-obs.sh" event 2>&1); RC=$?; }
ULID() { python3 -c 'import sys,os,time;E="0123456789ABCDEFGHJKMNPQRSTVWXYZ";n=(int(time.time()*1000)<<80)|int.from_bytes(os.urandom(10),"big");print(sys.argv[1]+"_"+"".join(E[(n>>(5*(25-i)))&31] for i in range(26)))' "$1"; }
HASH="sha256:$(printf 'probe' | sha256sum | cut -c1-64)"
ATT=$(ULID att); REV=$(ULID rev); REVB=$(ULID rev)
BASE=$(git rev-parse HEAD)
ATT_EV() { printf '{"event_type":"attempt_started","attempt_id":"%s","agent_role":"worker","model":"haiku","prompt":{"id":"probe","version":"1.0.0","hash":"%s"},"base_sha":"%s"}' "$ATT" "$HASH" "$BASE"; }
REV_EV() { printf '{"event_type":"review_started","review_id":"%s","agent_role":"reviewer","model":"opus"}' "$1"; }
REVC_EV() { printf '{"event_type":"review_completed","review_id":"%s","review_verdict":"PASS"}' "$1"; }

echo "["
snap "00-unarmed" 0 ""; echo ","
X status;                          snap "01-status-unarmed" $RC "$OUT"; echo ","
# obs 事件在未武裝時必須拒絕(run_id 由 start 生成)
OBS '{"event_type":"attempt_started","attempt_id":"att-x","agent_role":"worker","model":"haiku"}'
snap "02-obs-before-start(expect deny)" $RC "$OUT"; echo ","
# ── Stage 6 start(legacy sequential;5-tasks 無 execution 欄)──
X start f1;                        snap "10-stage6-start" $RC "$OUT"; echo ","
RUN6=$(python3 -c 'import json;print(json.load(open(".devflow/exec.json"))["run_id"])')
OBS "$(ATT_EV)"
snap "11-obs-attempt-started(stage6)" $RC "$OUT"; echo ","
# start 疊 start:應拒絕(同 run 不得重生 run_id)
X start f1;                        snap "12-start-while-armed-same-slug(re-arm allowed?)" $RC "$OUT"; echo ","
RUN6B=$(python3 -c 'import json;print(json.load(open(".devflow/exec.json"))["run_id"])')
OBS "$(ATT_EV)"; snap "13-obs-attempt-after-rearm(new run dir?)" $RC "$OUT"; echo ","
# schema fail-closed 對照:agent_role 不在 enum、prompt.version 非 x.y.z → 必須被拒、不落盤
OBS "$(ATT_EV | sed 's/"worker"/"implementer"/; s/"1.0.0"/"1"/')"; snap "14-obs-bad-role-and-version(expect schema deny)" $RC "$OUT"; echo ","
# Stage 6 → Stage 7:review 沿用同一份 exec.json
X review f1;                       snap "20-review-after-stage6" $RC "$OUT"; echo ","
RUN7=$(python3 -c 'import json;print(json.load(open(".devflow/exec.json"))["run_id"])')
OBS "$(REV_EV "$REV")"
snap "21-obs-review-started(same run)" $RC "$OUT"; echo ","
X review bare;                     snap "22-review-other-slug-while-armed(expect refuse)" $RC "$OUT"; echo ","
X review-unlock f1;                snap "23-review-unlock" $RC "$OUT"; echo ","
X status;                          snap "24-status-review-phase" $RC "$OUT"; echo ","
X stop;                            snap "30-stop" $RC "$OUT"; echo ","
OBS "$(REVC_EV "$REV")"
snap "31-obs-after-stop(expect deny)" $RC "$OUT"; echo ","
# ── bare Stage 7(無 Stage 6 state;runs/ 目錄仍留著上一 run 的檔)──
X review-unlock bare;              snap "40-unlock-without-review(expect refuse)" $RC "$OUT"; echo ","
X review nosuchslug;               snap "41-review-missing-feature-dir(expect refuse)" $RC "$OUT"; echo ","
X review bare;                     snap "42-bare-review-arm" $RC "$OUT"; echo ","
RUNB=$(python3 -c 'import json;print(json.load(open(".devflow/exec.json"))["run_id"])')
OBS "$(REV_EV "$REVB")"
snap "43-obs-review-started(bare run)" $RC "$OUT"; echo ","
X review bare;                     snap "44-review-again-same-slug(re-arm on existing)" $RC "$OUT"; echo ","
X review-unlock bare;              snap "45-bare-unlock" $RC "$OUT"; echo ","
X stop;                            snap "50-bare-stop" $RC "$OUT"; echo ","
X review bare;                     snap "51-bare-review-after-stop(new run_id?)" $RC "$OUT"; echo ","
RUNB2=$(python3 -c 'import json;print(json.load(open(".devflow/exec.json"))["run_id"])')
X stop;                            snap "52-final-stop" $RC "$OUT"; echo ","
python3 - "$RUN6" "$RUN6B" "$RUN7" "$RUNB" "$RUNB2" <<'PY'
import json, sys
r6, r6b, r7, rb, rb2 = sys.argv[1:6]
print(json.dumps({"step": "99-run-id-summary",
  "stage6_run_id": r6, "stage6_same_slug_restart_run_id": r6b, "restart_regenerates_run_id": r6 != r6b,
  "stage7_after_stage6_run_id": r7, "same_run_stage6_to_7": r6b == r7,
  "bare_stage7_run_id": rb, "bare_stage7_rearmed_after_stop_run_id": rb2,
  "bare_new_run_per_arm": len({r6, r6b, rb, rb2}) == 4}, ensure_ascii=False))
PY
echo "]"
