#!/bin/bash
# test-selftest-isolation.sh — selftest／doctor 不共用固定暫存檔、doctor 結果必入 exit code 的行為牙。
#
# 起因(2026-10-15 採用現場回報):selftest 結尾偶爾印 doctor INCOMPATIBLE,但整體 exit 0。
# 懷疑「selftest／doctor 共用固定 /tmp 記錄檔,被同時在跑的別的執行混到」。查證結果
# (見 docs/dev/HISTORY.md v3.26.2):hooks/ 與 doctor 呼叫的腳本內沒有任何固定名稱的 /tmp 路徑,
# 4 個 selftest + 3 個 doctor 並行實跑也沒混;selftest 本身沒有「結尾另跑 doctor」的步驟 ——
# doctor 只在 p3／p4 當案例跑,結果進 ck_msg 的 FAIL 計數(INCOMPATIBLE 不可能在 exit 0 下出現),
# 該回報最像是手動路徑吃到系統 python3 3.9(v3.26.2 的「找 3.12+」共用邏輯已修)。
# 這支把「不共用」與「結果必入 exit」釘成常設測試,以後有人加固定 /tmp 檔或讓 doctor 結果不計數就紅。
#
# 咬什麼:
#   ① 靜態:hooks/*.sh、hooks/*.py、doctor 呼叫的腳本(gauntlet／history-append)不得出現固定名稱的
#      /tmp/<名稱> 字面路徑(唯一白名單:selftest 的守衛測資 /tmp/outside.py = 故意的「專案外路徑」);
#      負向:對抗樣本(植入 /tmp/devflow-doctor.log)必須被抓到。
#   ② 靜態:hooks/selftest.sh 每個 p3_doctor 呼叫的下一個指令必是 ck/ck_msg 吃 $P3_RC(doctor 結果計入
#      FAIL → 影響 exit);每個 doctor 呼叫都有擷取(不裸印);最後一個 doctor 呼叫在 `TOTAL=` 結算之前
#      (結尾不會在計數後另跑 doctor 而不計入)。負向:拿掉消費行必須被抓到。
#   ③ 動態:doctor 並行(4 個相容 + 4 個不相容,兩輪)—— 各自結果穩定、不互相混;
#      不變式:rc=0 ⇔ 印 COMPATIBLE 且不印 INCOMPATIBLE;私有 TMPDIR 跑完是空的。
#   ④ 動態:selftest 跑到一半被 SIGTERM,私有暫存根(TMPDIR 底下的 devflow-selftest-root.*)清乾淨
#      (EXIT trap);跑的當下確實有建暫存(非空轉)。
#
# 用法:scripts/test-selftest-isolation.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; }
fi
for f in hooks/selftest.sh hooks/devflow-doctor.sh hooks/_doctor_impl.py hooks/devflow-find-python.sh; do
  [ -f "$ROOT/$f" ] || { echo "FATAL: 找不到 $ROOT/$f" >&2; exit 2; }
done
. "$ROOT/hooks/devflow-find-python.sh"
PY=$(devflow_find_py312) || { echo "FATAL: 找不到 Python 3.12+(設 DEVFLOW_PYTHON)" >&2; exit 2; }

MIN_CASES=21
PASS=0
FAIL=0
TOTAL=0
WORK=$(mktemp -d "${TMPDIR:-/tmp}/devflow-selftest-isolation-test.XXXXXX") || exit 2
trap 'kill $(jobs -p) 2>/dev/null; rm -rf "$WORK"' EXIT

expect() {  # expect <label> <condition-rc>
  TOTAL=$((TOTAL + 1))
  if [ "$2" -eq 0 ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $1" >&2
  fi
}

# ── ① 固定 /tmp 路徑靜態掃描 ────────────────────────────────────────────
# 白名單:/tmp/outside.py(selftest 守衛測資,刻意的專案外路徑,不是寫入目標)
fixed_tmp_hits() {  # fixed_tmp_hits <root>:印違規行(檔:行:內容)
  local r=$1
  ( cd "$r" && grep -rnE '/tmp/[A-Za-z0-9._-]' hooks scripts/devflow-evidence-gauntlet.sh scripts/history-append.sh \
      --include='*.sh' --include='*.py' 2>/dev/null | grep -v '/tmp/outside\.py' ) || true
}
HITS=$(fixed_tmp_hits "$ROOT")
expect "hooks/ 與 doctor 呼叫的腳本沒有固定名稱的 /tmp/<名稱> 路徑(白名單只有 /tmp/outside.py)" \
  "$([ -z "$HITS" ]; echo $?)"
[ -n "$HITS" ] && printf '%s\n' "$HITS" >&2
MUT="$WORK/mut1"; mkdir -p "$MUT/hooks" "$MUT/scripts"
printf '#!/bin/bash\necho x > /tmp/devflow-doctor.log\n' >"$MUT/hooks/evil.sh"
expect "負向:植入 /tmp/devflow-doctor.log 的對抗樣本必須被掃到" \
  "$([ -n "$(fixed_tmp_hits "$MUT")" ]; echo $?)"
printf 'import tempfile\nopen("/tmp/x.json","w")\n' >"$MUT/hooks/evil.py"
expect "負向:py 內 open(\"/tmp/x.json\") 也被掃到" \
  "$(fixed_tmp_hits "$MUT" | grep -q 'evil.py'; echo $?)"

# ── ② selftest.sh 的 doctor 結果必入 FAIL 計數 ───────────────────────────
doctor_accounting() {  # doctor_accounting <selftest.sh>:印問題行;沒問題不印
  "$PY" - "$1" <<'PYEOF'
import re
import sys

lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
problems = []
calls = [i for i, ln in enumerate(lines) if re.match(r"p3_doctor\s", ln)]
if not calls:
    problems.append("找不到任何 p3_doctor 呼叫(案例被整批刪了?)")
for i in calls:
    nxt = next((w for w in lines[i + 1:] if w.strip() and not w.lstrip().startswith("#")), "")
    if not ((nxt.startswith("ck_msg ") or nxt.startswith("ck ")) and "P3_RC" in nxt):
        problems.append("第 %d 行 p3_doctor 的下一個指令不是吃 $P3_RC 的 ck/ck_msg(結果不計入 exit):%s" % (i + 1, lines[i][:80]))
doc_refs = [i for i, ln in enumerate(lines)
            if ("devflow-doctor.sh" in ln or re.search(r'devflow-exec\.sh"\s+doctor', ln))
            and not ln.lstrip().startswith("#")]
for i in doc_refs:
    if "$(" not in lines[i]:
        problems.append("第 %d 行 doctor 呼叫沒有擷取(裸印會出現在輸出卻不計入 exit):%s" % (i + 1, lines[i][:80]))
total = [i for i, ln in enumerate(lines) if ln.startswith("TOTAL=$((PASS+FAIL))")]
if not total:
    problems.append("找不到結算行 TOTAL=$((PASS+FAIL))")
elif doc_refs and max(doc_refs) > total[0]:
    problems.append("結算(第 %d 行)之後還有 doctor 呼叫(第 %d 行)—— 其結果不會進 exit code" % (total[0] + 1, max(doc_refs) + 1))
print("\n".join(problems))
PYEOF
}
PROB=$(doctor_accounting "$ROOT/hooks/selftest.sh")
expect "selftest.sh:每個 p3_doctor 的下一步都是 ck 吃 \$P3_RC、doctor 呼叫皆擷取、結算後不再跑 doctor" "$([ -z "$PROB" ]; echo $?)"
[ -n "$PROB" ] && printf '%s\n' "$PROB" >&2
# 負向 1:拿掉某個 p3_doctor 後的消費行
awk 'BEGIN{d=0} /^p3_doctor "\$P3T\/contract-ok.json" "\$P3T\/caps-ok.json"$/ && !d {print; getline; d=1; next} {print}' \
  "$ROOT/hooks/selftest.sh" >"$WORK/mut-st1.sh"
expect "負向:拿掉 p3_doctor 後的 ck_msg(結果不計入 exit)必須被抓到" \
  "$(doctor_accounting "$WORK/mut-st1.sh" | grep -q 'P3_RC'; echo $?)"
# 負向 2:結算行之後多一個裸跑的 doctor
cp "$ROOT/hooks/selftest.sh" "$WORK/mut-st2.sh"
printf '"$H/devflow-doctor.sh"\n' >>"$WORK/mut-st2.sh"
expect "負向:結尾追加裸跑 doctor(印 INCOMPATIBLE 卻不影響 exit)必須被抓到" \
  "$(doctor_accounting "$WORK/mut-st2.sh" | grep -q '沒有擷取'; echo $?)"
# selftest 自己的結尾:exit 只由 FAIL 決定
expect "selftest.sh 結尾:FAIL=0 → exit 0、否則 exit 1(沒有第三條出口)" \
  "$(tail -n 4 "$ROOT/hooks/selftest.sh" | grep -q 'if \[ "\$FAIL" = 0 \]; then echo "✅' && tail -n 2 "$ROOT/hooks/selftest.sh" | grep -q 'exit 1; fi'; echo $?)"

# ── ③ doctor 並行:結果穩定、不互相混 ────────────────────────────────────
PROJ="$WORK/proj"; mkdir -p "$PROJ" "$WORK/tmp3"
printf '%s\n' '{"devflow_contract_version": "2.0.0",' \
  ' "required_runtime_capabilities": ["attempt_ledger"],' \
  ' "schema_versions": {"agent_event": "1.1", "context_manifest": "1.0", "prompt_registry": "1.0", "exec_state": "exec-v3"}}' >"$PROJ/contract.json"
printf '%s\n' '{"supported_contract_versions": ["2.0.0"], "runtime_version": "2.5.0", "capabilities": ["attempt_ledger"]}' >"$PROJ/caps-ok.json"
printf '%s\n' '{"supported_contract_versions": ["1.2.0"], "runtime_version": "1.9.0", "capabilities": ["attempt_ledger"]}' >"$PROJ/caps-old.json"
run_doctor() {  # run_doctor <caps> <tag>:輸出 → $WORK/d-<tag>.out、rc → $WORK/d-<tag>.rc
  ( cd "$PROJ" && TMPDIR="$WORK/tmp3" DEVFLOW_PYTHON="$PY" DEVFLOW_CONTRACT="$PROJ/contract.json" \
      DEVFLOW_RUNTIME_CAPS="$1" DEVFLOW_GATE_CMD=true "$ROOT/hooks/devflow-doctor.sh" >"$WORK/d-$2.out" 2>&1
    echo $? >"$WORK/d-$2.rc" )
}
for round in 1 2; do
  for n in 1 2 3 4; do
    run_doctor "$PROJ/caps-ok.json" "ok$round$n" &
    run_doctor "$PROJ/caps-old.json" "bad$round$n" &
  done
  wait
done
GOOD_OK=0; BAD_OK=0; INV_OK=0
for round in 1 2; do for n in 1 2 3 4; do
  o="$WORK/d-ok$round$n.out"; r=$(cat "$WORK/d-ok$round$n.rc" 2>/dev/null)
  [ "$r" = 0 ] && grep -q '✅ devflow doctor: COMPATIBLE' "$o" && ! grep -q 'INCOMPATIBLE' "$o" && GOOD_OK=$((GOOD_OK + 1))
  o="$WORK/d-bad$round$n.out"; r=$(cat "$WORK/d-bad$round$n.rc" 2>/dev/null)
  [ "$r" = 1 ] && grep -q '⛔ devflow doctor: INCOMPATIBLE' "$o" && BAD_OK=$((BAD_OK + 1))
done; done
for f in "$WORK"/d-*.out; do
  t=${f%.out}; r=$(cat "$t.rc" 2>/dev/null)
  # 不變式:rc=0 ⇔ 有 COMPATIBLE 結論行且沒有 INCOMPATIBLE;rc≠0 ⇔ 有 INCOMPATIBLE 結論行
  if { [ "$r" = 0 ] && grep -q '✅ devflow doctor: COMPATIBLE' "$f" && ! grep -q 'INCOMPATIBLE' "$f"; } \
     || { [ "$r" != 0 ] && grep -q '⛔ devflow doctor: INCOMPATIBLE' "$f"; }; then INV_OK=$((INV_OK + 1)); fi
done
expect "doctor 並行:8 個相容的全部 rc=0 + COMPATIBLE、不混入 INCOMPATIBLE(實得 $GOOD_OK/8)" "$([ "$GOOD_OK" = 8 ]; echo $?)"
expect "doctor 並行:8 個不相容的全部 rc=1 + INCOMPATIBLE(實得 $BAD_OK/8)" "$([ "$BAD_OK" = 8 ]; echo $?)"
expect "doctor 16 次輸出的不變式成立(rc=0 ⇔ COMPATIBLE 且無 INCOMPATIBLE;rc≠0 ⇔ INCOMPATIBLE;實得 $INV_OK/16)" \
  "$([ "$INV_OK" = 16 ]; echo $?)"
expect "doctor 並行跑完後私有 TMPDIR 是空的(沒留固定檔或暫存)" "$([ -z "$(ls -A "$WORK/tmp3")" ]; echo $?)"

# ── ④ selftest 被中斷:私有暫存根被 EXIT trap 清掉 ──────────────────────
mkdir -p "$WORK/tmp4"
( TMPDIR="$WORK/tmp4" DEVFLOW_PYTHON="$PY" exec "$BASH" "$ROOT/hooks/selftest.sh" >"$WORK/st.out" 2>&1 ) &
SPID=$!
SEEN=1
for _ in $(seq 1 100); do
  if ls "$WORK/tmp4" 2>/dev/null | grep -q '^devflow-selftest-root\.'; then SEEN=0; break; fi
  sleep 0.1
done
sleep 2
INSIDE=$(find "$WORK/tmp4" -mindepth 2 -maxdepth 2 2>/dev/null | head -1)
kill -TERM "$SPID" 2>/dev/null
wait "$SPID" 2>/dev/null
expect "selftest 跑起來後私有暫存根 devflow-selftest-root.* 建在 TMPDIR 底下" "$SEEN"
expect "selftest 跑的當下,各案例的暫存目錄都在私有根裡面(非空轉)" "$([ -n "$INSIDE" ]; echo $?)"
expect "selftest 被 SIGTERM 中斷後,TMPDIR 底下清得乾乾淨淨(EXIT trap)" "$([ -z "$(ls -A "$WORK/tmp4")" ]; echo $?)"

# ── ⑤ PATH 上第一個 bash 是壞的(126,x86 版在 Apple Silicon 上 Bad CPU type)──────
# 起因(採用現場回報):Apple Silicon 上 PATH 的 /usr/local/bin/bash 是 x86 版,selftest 內直接寫
# `bash …` 的地方(g1 history-append 三案、w2 的 W2BASH=$(command -v bash)、p1 plan 的 Python
# subprocess、doctor 內的 gate-consistency／gauntlet／history-append)全以 126 假紅。
# w2 的「TMPDIR 得空字串」根因就是這個:w2() 把 stderr 丟掉、且用壞 bash 跑,輸出為空,
# 看起來像 TMPDIR 正規化算出空值,實際上 TMPDIR 邏輯沒問題(有 /bin/bash 時 env -i 無 TMPDIR 也全過)。
# 重現環境照現場:env -i、PATH=<假 bin>:/usr/bin:/bin、不帶 TMPDIR;假 bin 的 bash 一律 exit 126。
# 負向:同一環境跑「把 SELFTEST_BASH 退回字面 bash」的變體必須紅(證明本測試咬得到)。
FAKEBIN="$WORK/fakebin"; mkdir -p "$FAKEBIN"
printf '#!/bin/sh\necho "Bad CPU type in executable" >&2\nexit 126\n' >"$FAKEBIN/bash"; chmod 755 "$FAKEBIN/bash"
expect "治具:假 bin 的 bash 真的是 exit 126(測試前提)" \
  "$(PATH="$FAKEBIN:/usr/bin:/bin" bash -c true >/dev/null 2>&1; [ $? = 126 ]; echo $?)"
env -i HOME="${HOME:-/nonexistent}" PATH="$FAKEBIN:/usr/bin:/bin" DEVFLOW_PYTHON="$PY" \
  "$BASH" "$ROOT/hooks/selftest.sh" >"$WORK/st5.out" 2>&1; echo $? >"$WORK/st5.rc"
expect "壞 bash 排 PATH 前面:selftest exit 0(實得 $(cat "$WORK/st5.rc"))" "$([ "$(cat "$WORK/st5.rc")" = 0 ]; echo $?)"
expect "壞 bash 排 PATH 前面:結論行「守衛自測 N/N 全過」" "$(grep -Eq '守衛自測 ([0-9]+)/\1 全過' "$WORK/st5.out"; echo $?)"
expect "壞 bash 排 PATH 前面:w2／g1／p1 plan／doctor 相關案例沒有任何一項失敗" \
  "$(! grep -E '^   - (w2|g1|p1 plan|p3 doctor|pw doctor|p4_doctor)' "$WORK/st5.out" | grep -q .; echo $?)"
# doctor 單獨(手動路徑 devflow-doctor.sh):gate-consistency 實跑也得過
( cd "$PROJ" && env -i HOME="${HOME:-/nonexistent}" PATH="$FAKEBIN:/usr/bin:/bin" DEVFLOW_PYTHON="$PY" \
    DEVFLOW_CONTRACT="$PROJ/contract.json" DEVFLOW_RUNTIME_CAPS="$PROJ/caps-ok.json" DEVFLOW_GATE_CMD=true \
    "$BASH" "$ROOT/hooks/devflow-doctor.sh" >"$WORK/d5.out" 2>&1; echo $? >"$WORK/d5.rc" )
expect "壞 bash 排 PATH 前面:手動 devflow-doctor.sh COMPATIBLE、exit 0(gate-consistency 不以 126 死)" \
  "$([ "$(cat "$WORK/d5.rc")" = 0 ] && grep -q '✅ devflow doctor: COMPATIBLE' "$WORK/d5.out"; echo $?)"
# 負向變體:SELFTEST_BASH 退回字面 bash 且不 export DEVFLOW_BASH(= 修法前的行為)
MUTR="$WORK/mutroot"; mkdir -p "$MUTR"
for d in "$ROOT"/* "$ROOT"/.[!.]*; do
  b=$(basename "$d"); [ "$b" = hooks ] || [ "$b" = .git ] || ln -s "$d" "$MUTR/$b"
done
cp -R "$ROOT/hooks" "$MUTR/hooks"
sed -i 's|^SELFTEST_BASH=\$DEVFLOW_BASH$|SELFTEST_BASH=bash; unset DEVFLOW_BASH|; s|^export DEVFLOW_BASH$|:|' "$MUTR/hooks/selftest.sh"
expect "負向前提:變體確實已把 SELFTEST_BASH 改成字面 bash" "$(grep -q '^SELFTEST_BASH=bash; unset DEVFLOW_BASH$' "$MUTR/hooks/selftest.sh"; echo $?)"
env -i HOME="${HOME:-/nonexistent}" PATH="$FAKEBIN:/usr/bin:/bin" DEVFLOW_PYTHON="$PY" \
  "$BASH" "$MUTR/hooks/selftest.sh" >"$WORK/st5m.out" 2>&1; echo $? >"$WORK/st5m.rc"
expect "負向:字面 bash 的變體在同一環境必須紅(exit≠0 且 g1 與 w2 案例失敗;實得 rc=$(cat "$WORK/st5m.rc"))" \
  "$([ "$(cat "$WORK/st5m.rc")" != 0 ] && grep -q '^   - g1 ' "$WORK/st5m.out" && grep -q '^   - w2 ' "$WORK/st5m.out"; echo $?)"

if [ "$TOTAL" -lt "$MIN_CASES" ]; then
  echo "FATAL: 案例數 $TOTAL 低於下限 $MIN_CASES(案例被刪?)" >&2
  exit 2
fi
echo "=== test-selftest-isolation:$PASS/$TOTAL ==="
[ "$FAIL" -eq 0 ]
