#!/bin/bash
# devflow-exec.sh — dev-flow 執行守衛 CLI:start <slug> [--task T-n] / stop / status / allow <file> --reason "..."
# parallel(Stage 6):parallel-init / plan / wave-open / wave-close / task-candidate /
#   task-state / task-integrate / task-rework / rebuild-plan / review / candidate / gate
# Stage 7(A-11):review <slug>(武裝 self-review 圍欄③,exec.json 加 phase="review")/
#   review-unlock <slug>(步 4 解鎖讀 6-notes;Write 限縮维持)
# tier-exempt --reason "..."(X-5b):PreToolUse 派工分層守衛(devflow-dispatch-guard.sh)
#   「首派即最高階」擋下時的一次性豁免,核發 .devflow/tier-exempt.json(used=false),
#   guard 消耗後轉 used=true+used_at,留痕不可重複用。
# 狀態:.devflow/exec.json(scope/baseline+hash/契約 hash;task 模式 schema = exec-v3,讀取仍收 exec-v2)+
#   .devflow/parallel.json(feature 級 wave/狀態機帳)+ <git-dir>/devflow-armed(sentinel,
# 讓旗標被刪時 hooks 能 fail-closed 而非靜默棄守)。
set -u
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
CMD="${1:-status}"
case "$CMD" in
  start)   shift; /usr/bin/python3 "$HERE/_exec_impl.py" start "$ROOT" "$@";;
  stop)    /usr/bin/python3 "$HERE/_exec_impl.py" stop "$ROOT";;
  status)  /usr/bin/python3 "$HERE/_exec_impl.py" status "$ROOT";;
  allow)   /usr/bin/python3 "$HERE/_exec_impl.py" allow "$ROOT" "${2:-}" "${4:-}";;
  candidate|parallel-init|plan|wave-open|wave-close|task-candidate|task-state|task-integrate|task-rework|rebuild-plan|review|review-unlock|tier-exempt)
           shift; /usr/bin/python3 "$HERE/_exec_impl.py" "$CMD" "$ROOT" "$@";;
  gate)    shift; /usr/bin/python3 "$HERE/_gate_impl.py" "$ROOT" "$@";;
  event)   "$HERE/devflow-obs.sh" event "${2:-}";;
  doctor)  shift; "$HERE/devflow-doctor.sh" "$@";;
  stage3)  shift; exec /usr/bin/python3 "$HERE/_stage3_impl.py" "$@";;
  *) echo "用法: devflow-exec.sh start <slug> | stop | status | allow <file> --reason \"...\""
     echo "parallel: start <slug> --task T-n [--wave N --base <sha>] | parallel-init <slug> | plan <slug>"
     echo "          wave-open|wave-close <slug> | task-candidate|task-state|task-integrate|task-rework <slug> <T-n> ..."
     echo "          candidate <sha> | gate --bundle <f>|--slug <slug> --task T-n --candidate-json <f> | review ... | rebuild-plan <slug>"
     echo "Stage 7: review <slug>(武裝 self-review 圍欄③)| review-unlock <slug>(步 4 解鎖讀 6-notes)"
     echo "派工分層: tier-exempt --reason \"...\"(首派最高階模型的一次性豁免)";;
esac
