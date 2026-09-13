#!/bin/bash
# devtalk-guard.sh — dev-flow plugin 內建:dev-talk 盲原則守衛(PostToolUse hook)
# 單一正本(隨 plugin 走,兩帳號共用同一 local plugin 目錄)。
# 行為:非 skills/dev-talk/ 路徑靜默放行(talk 游標不在時);dev-talk 檔案寫入後跑洩漏掃描。
#       talk 游標在時加 Read 分支:放行 Evidence manifest 核准=是;仍禁 2–7 方案檔;
#       未核／空白不得當已授權。核准格不能覆寫 2–7 禁令。不另開 check-evidence-allow.sh。
#       命中 → exit 2(stderr 回饋給模型要求立即修正),並 best-effort 記一筆
#       observability 事件(P3 hook-event,通道與 _guard/_prebash/_postbash 的
#       _obs_deny 相同 —— 都是呼叫 _obs_impl.py hook-event)。這裡是 bash 不是
#       python,故直接用小段 inline python3 組 payload 餵同一支 CLI。
#       ⚠️ obs 寫入失敗(例如 runs 目錄不可寫、守衛未武裝)絕不得動到 deny/放行
#       判定 —— 整段包 || true 且吞掉 stdout/stderr,之後照樣 exit 2。
. "$(dirname "$0")/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | "$DEVFLOW_PY" -c "import json,sys
try: print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))
except Exception: pass" 2>/dev/null)
TOOL=$(printf '%s' "$INPUT" | "$DEVFLOW_PY" -c "import json,sys
try: print(json.load(sys.stdin).get('tool_name',''))
except Exception: pass" 2>/dev/null)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [ -f "$REPO_ROOT/.devtalk-cursor.json" ] && [ "$TOOL" = "Read" ]; then
  MANIFEST="${DEVTALK_MANIFEST:-}"
  export DEVTALK_READ_FILE="$FILE"
  export DEVTALK_MANIFEST_PATH="$MANIFEST"
  export DEVTALK_REPO_ROOT="$REPO_ROOT"
  "$DEVFLOW_PY" - <<'PY'
import os, re, sys

file_path = os.environ.get("DEVTALK_READ_FILE", "")
root = os.environ.get("DEVTALK_REPO_ROOT", "")
manifest_path = os.environ.get("DEVTALK_MANIFEST_PATH", "")

def rel(path):
    try:
        return os.path.relpath(os.path.realpath(path), os.path.realpath(root)).replace("\\", "/")
    except Exception:
        return path.replace("\\", "/")

rel_file = rel(file_path)
base = os.path.basename(rel_file)
# 2–7 方案檔硬擋（含 html twin）；核准=是不能覆寫
solution = (
    "2-decision", "3-prototype", "4-spec", "5-tasks",
    "6-implementation-notes", "7-review",
)
stem = base.replace(".html", "").replace(".md", "")
if stem in solution or any(name in rel_file for name in solution):
    print(f"⛔ devtalk-guard:方案檔仍禁 —— Read {rel_file}（2-decision／4-spec／2–7 不得當事實）", file=sys.stderr)
    raise SystemExit(2)

if not manifest_path or not os.path.isfile(manifest_path):
    print("⛔ devtalk-guard:未核路徑不得當已授權（無 Evidence manifest）", file=sys.stderr)
    raise SystemExit(2)

text = open(manifest_path, encoding="utf-8").read()
sec = re.search(r"^## Evidence manifest.*?(?=^## |\Z)", text, re.M | re.S)
if not sec:
    print("⛔ devtalk-guard:未核路徑不得當已授權（無 ## Evidence manifest）", file=sys.stderr)
    raise SystemExit(2)

approved = False
for line in sec.group(0).splitlines():
    if not line.lstrip().startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4 or cells[0].startswith("想找") or re.match(r"^:?-+:?$", cells[0] or ""):
        continue
    planned = cells[2] if len(cells) > 2 else ""
    approval = cells[3] if len(cells) > 3 else ""
    planned_norm = planned.replace("\\", "/").lstrip("./")
    if planned_norm and (rel_file == planned_norm or rel_file.endswith(planned_norm) or planned_norm.endswith(rel_file)):
        if approval == "是":
            approved = True
        else:
            print(f"⛔ devtalk-guard:未核路徑不得當已授權 —— {planned}（核准={approval or '空白'}）", file=sys.stderr)
            raise SystemExit(2)

if not approved:
    print(f"⛔ devtalk-guard:未核路徑不得當已授權 —— {rel_file}", file=sys.stderr)
    raise SystemExit(2)
raise SystemExit(0)
PY
  rc=$?
  exit "$rc"
fi
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
  # F2 同型:不把整包 $INPUT 塞進單次環境變數(HOOK_INPUT="$INPUT" cmd 也是 exec,
  # 大 payload 一樣撞 ARG_MAX → obs 靜默丟失)。printf 是 builtin 不經 exec,先在
  # shell 內抽出小小的 session_id 再傳,環境變數只載幾十 bytes。
  SID=$(printf '%s' "$INPUT" | "$DEVFLOW_PY" -c "import json,sys
try: print(json.load(sys.stdin).get('session_id',''))
except Exception: pass" 2>/dev/null)
  DEVTALK_SID="$SID" DEVTALK_TARGET="$FILE" "$DEVFLOW_PY" - \
    "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" "$(dirname "$0")" \
    <<'PYEOF' >/dev/null 2>&1 || true
import json, os, subprocess, sys
root, here = sys.argv[1], sys.argv[2]
target = os.environ.get("DEVTALK_TARGET", "")
try:
    # 正斜線化(issue #7):這欄只進 obs payload,不參與判定,但事件資料的形狀
    # 不該隨平台而異 —— 否則同一份查詢在 Windows 產出的事件上對不起來。
    target = os.path.relpath(os.path.realpath(target), os.path.realpath(root)).replace("\\", "/")
except Exception:
    pass
payload = {"event_type": "mechanical_gate_completed", "gate": "devtalk-guard",
           "result": "FAIL", "violation": "other"}
if target:
    payload["target"] = target
sid = os.environ.get("DEVTALK_SID", "")
if sid:
    payload["session_ref"] = sid
try:
    subprocess.run(
        # sys.executable = 正在跑本段的直譯器(外層殼已解析過);不重新解析,避免兩次
        # 解析在特殊環境下拿到不同直譯器。
        [sys.executable, os.path.join(here, "_obs_impl.py"), "hook-event", root],
        input=json.dumps(payload), text=True, capture_output=True, timeout=5)
except Exception:
    pass
PYEOF
  exit 2
fi
exit 0
