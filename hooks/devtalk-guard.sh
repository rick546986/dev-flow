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
. "$(dirname "$0")/devflow-python-lib.sh"  # 直譯器解析;缺直譯器 fail-open(理由見該檔)
INPUT=$(cat)
# Read 分支:talk 游標在時才發動。放行 Evidence manifest 核准=是;
# 仍禁 2–7 方案檔(核准格不能覆寫)。游標不在 → 維持只掃 skills/dev-talk 寫入洩漏。
_HOOK_JSON=$(mktemp "${TMPDIR:-/tmp}/devtalk-guard-read.XXXXXX")
printf '%s' "$INPUT" > "$_HOOK_JSON"
"$DEVFLOW_PY" - "$PWD" "$_HOOK_JSON" <<'READ'
import json, os, re, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
try:
    data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8") or "{}")
except Exception:
    raise SystemExit(0)
if data.get("tool_name") != "Read":
    raise SystemExit(0)
path = str((data.get("tool_input") or {}).get("file_path") or "")
if not path:
    raise SystemExit(0)
if not (root / ".devtalk-cursor.json").is_file():
    raise SystemExit(0)
posix = path.replace("\\", "/")
sol = re.compile(
    r"(?:^|/)(?:2-decision|3-prototype|4-spec|5-tasks|"
    r"6-implementation-notes|7-review)(?:\.(?:md|html))?$"
)
if sol.search(posix):
    print("⛔ devtalk-guard:方案檔仍禁讀(2-decision／4-spec／2–7;核准格不能覆寫)",
          file=sys.stderr)
    raise SystemExit(2)
def _manifest_texts():
    seen = set()
    env = os.environ.get("DEVTALK_MANIFEST")
    if env:
        p = Path(env)
        if p.is_file():
            try:
                yield p.read_text(encoding="utf-8")
                seen.add(p.resolve())
            except Exception:
                pass
    docs = root / "docs" / "dev"
    if docs.is_dir():
        for p in docs.glob("*/1-discussion.md"):
            try:
                rp = p.resolve()
                if rp in seen:
                    continue
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if "## Evidence manifest" in text:
                yield text

matched_deny = False
for text in _manifest_texts():
    idx = text.find("## Evidence manifest")
    if idx < 0:
        continue
    for line in text[idx:].splitlines():
        raw = line.strip()
        if not raw.startswith("|") or set(raw.replace("|", "").replace(":", "").strip()) <= {"-"}:
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if len(cells) < 4 or "擬路徑" in cells[2] or "owner 核准" in cells[3]:
            continue
        proposed, approved = cells[2], cells[3]
        if proposed and proposed in posix:
            if approved == "是":
                raise SystemExit(0)
            matched_deny = True
if matched_deny:
    print("⛔ devtalk-guard:未核路徑不得當已授權 evidence", file=sys.stderr)
    raise SystemExit(2)
raise SystemExit(0)
READ
READ_ST=$?
rm -f "$_HOOK_JSON"
if [ "$READ_ST" -eq 2 ]; then
  exit 2
fi
FILE=$(printf '%s' "$INPUT" | "$DEVFLOW_PY" -c "import json,sys
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
