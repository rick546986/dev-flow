import json
import os
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "devflow-lib.py")).load_module()

import subprocess


def _obs_deny(gate, violation, target=""):
    """deny 時 best-effort 記機械事件(P3 hook-event);失敗不影響守衛裁決。"""
    try:
        payload = {"event_type": "mechanical_gate_completed", "gate": gate,
                   "result": "FAIL", "violation": violation}
        if target:
            payload["target"] = target
        try:
            sid = json.loads(os.environ.get("HOOK_INPUT", "{}")).get("session_id", "")
        except Exception:
            sid = ""
        if sid:
            payload["session_ref"] = sid
        subprocess.run(
            ["/usr/bin/python3",
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "_obs_impl.py"),
             "hook-event", root],
            input=json.dumps(payload), text=True, capture_output=True, timeout=5)
    except Exception:
        pass


root = sys.argv[1]
try:
    h = json.loads(os.environ.get("HOOK_INPUT", "{}"))
except Exception:
    sys.exit(0)
tool = h.get("tool_name", "")
fp = h.get("tool_input", {}).get("file_path", "")
if not fp:
    sys.exit(0)

state, armed, err = L.load_state(root)
if err:
    L.die(err)
if state is None:
    sys.exit(0)

rel = L.rel_of(root, fp)
if rel is None:
    sys.exit(0)
if L.is_ambient_path(rel):
    sys.exit(0)
slug = state.get("slug", "")
task = state.get("task") or ""          # exec-v2 task-scoped 模式(§7)
feat = f"docs/dev/{slug}/"

if tool == "Read":
    # 圍欄②:任何 feature 的上游討論文件都禁讀(不只當前 slug)
    if L.is_contract_path(rel, L.UPSTREAM):
        _obs_deny("guard-read", "upstream_read", rel)
        L.die(f"⛔ 圍欄②:執行期禁讀 {rel} —— 要翻上游 = spec 不完整。"
              f"停:devflow-exec.sh stop → 補 spec → 重審。")
    sys.exit(0)

# 契約防篡改:任何 feature 的 1/2/3/4 檔(含 .html)一律禁改
if L.is_contract_path(rel):
    _obs_deny("guard-write", "contract", rel)
    L.die(f"⛔ 契約防篡改:執行期禁改 {rel}(跨 feature 一律保護)。"
          f"改本 feature 的 spec = L2:devflow-exec.sh stop → 修 → 重審 → 重新 start。")
# 旗標與忽略規則只准 CLI 動,agent 側禁寫;task 模式恆許自己的 evidence 專區
if rel.startswith(".devflow/"):
    if task and rel.startswith(f".devflow/task/{task}/"):
        sys.exit(0)
    _obs_deny("guard-write", "guard_state", rel)
    L.die("⛔ 禁止直接編輯守衛狀態(.devflow/)。擴 scope 走 devflow-exec.sh allow <file> --reason \"...\"。")
if rel == ".gitignore":
    _obs_deny("guard-write", "guard_state", rel)
    L.die("⛔ 執行期禁改 .gitignore(改忽略規則會讓偵測網失明)。確有需要 → 停下回報使用者。")

if rel.startswith((feat + "5-tasks", feat + "6-implementation-notes")):
    if task:
        # 單寫者原則(§12):task 模式下共享文件移出恆許,記帳由派工者於 ACCEPTED 後執行
        L.die(f"⛔ task-scoped 守衛:{rel} 是共享文件(單寫者=派工者)。"
              f"Worker 只寫 .devflow/task/{task}/ 的 evidence;"
              f"5-tasks/6-notes 記帳由派工者在 ACCEPTED 後執行。")
    sys.exit(0)
if L.in_pool(rel, state):
    sys.exit(0)
_obs_deny("guard-write", "scope", rel)
L.die(L.scope_violation_message(
    f"⛔ scope 外寫入:{rel} 不在 5-tasks Files 聯集。",
    resolution=(f"L1(不動 R/S)→ devflow-exec.sh allow '{rel}' --reason \"...\" "
                f"並記 D-n;L2 → stop。")))
