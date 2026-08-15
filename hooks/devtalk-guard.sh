#!/bin/bash
# devtalk-guard.sh — dev-flow plugin 內建:dev-talk 盲原則守衛(PostToolUse hook)
# 單一正本(隨 plugin 走,兩帳號共用同一 local plugin 目錄)。
# 行為:非 skills/dev-talk/ 路徑靜默放行;dev-talk 檔案寫入後跑洩漏掃描,
#       命中 → exit 2(stderr 回饋給模型要求立即修正),並 best-effort 記一筆
#       observability 事件(P3 hook-event,通道與 _guard/_prebash/_postbash 的
#       _obs_deny 相同 —— 都是呼叫 _obs_impl.py hook-event)。這裡是 bash 不是
#       python,故直接用小段 inline python3 組 payload 餵同一支 CLI。
#       ⚠️ obs 寫入失敗(例如 runs 目錄不可寫、守衛未武裝)絕不得動到 deny/放行
#       判定 —— 整段包 || true 且吞掉 stdout/stderr,之後照樣 exit 2。
INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | /usr/bin/python3 -c "import json,sys
try: print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))
except Exception: pass" 2>/dev/null)
case "$FILE" in
  */skills/dev-talk/*) : ;;
  *) exit 0 ;;
esac
[ -f "$FILE" ] || exit 0
LEAK=$(grep -nE "dev-flow|2-decision|4-spec|5-tasks|7-review|G1|G2|G3|gate|twin|pipeline|規劃|plan" "$FILE" 2>/dev/null)
if [ -n "$LEAK" ]; then
  {
    echo "⛔ devtalk-guard:盲原則洩漏 —— 剛寫入的 dev-talk 檔案含下游階段字眼(不得出現):"
    echo "$LEAK"
    echo "請立即修正該檔(移除相關字眼);若判定為誤報,回報使用者裁決。"
  } >&2
  HOOK_INPUT="$INPUT" DEVTALK_TARGET="$FILE" /usr/bin/python3 - \
    "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" "$(dirname "$0")" \
    <<'PYEOF' >/dev/null 2>&1 || true
import json, os, subprocess, sys
root, here = sys.argv[1], sys.argv[2]
target = os.environ.get("DEVTALK_TARGET", "")
try:
    target = os.path.relpath(os.path.realpath(target), os.path.realpath(root))
except Exception:
    pass
payload = {"event_type": "mechanical_gate_completed", "gate": "devtalk-guard",
           "result": "FAIL", "violation": "other"}
if target:
    payload["target"] = target
try:
    sid = json.loads(os.environ.get("HOOK_INPUT", "{}")).get("session_id", "")
except Exception:
    sid = ""
if sid:
    payload["session_ref"] = sid
try:
    subprocess.run(
        ["/usr/bin/python3", os.path.join(here, "_obs_impl.py"), "hook-event", root],
        input=json.dumps(payload), text=True, capture_output=True, timeout=5)
except Exception:
    pass
PYEOF
  exit 2
fi
exit 0
