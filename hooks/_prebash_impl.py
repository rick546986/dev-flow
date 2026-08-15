import json
import os
import re
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__

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
cmd = h.get("tool_input", {}).get("command", "")
if not cmd:
    sys.exit(0)

state, armed, err = L.load_state(root)
if err:
    L.die(err)
if state is None:
    sys.exit(0)

# ① 守衛狀態破壞:rm/mv/直寫 .devflow 或 sentinel
if "devflow-armed" in cmd:
    _obs_deny("prebash", "guard_state")
    L.die("⛔ 禁止經 shell 破壞守衛狀態(.devflow/ 或 sentinel)。"
          "正常收工:devflow-exec.sh stop;擴 scope:devflow-exec.sh allow。")
if re.search(r"(rm|mv|truncate|:>|>\s*)\s*[^|;&]*\.devflow/", cmd):
    # task-scoped 模式(exec-v2 §7):.devflow/task/<T-id>/ 是 evidence 專區,
    # 寫自己的 RED/GREEN log(redirect)合法;其餘 .devflow 仍禁
    task = state.get("task") or ""
    refs = re.findall(r"\.devflow/[^\s'\";|&)]*", cmd)
    if not (task and refs and all(r.startswith(f".devflow/task/{task}/") for r in refs)):
        _obs_deny("prebash", "guard_state")
        L.die("⛔ 禁止經 shell 破壞守衛狀態(.devflow/ 或 sentinel)。"
              "正常收工:devflow-exec.sh stop;擴 scope:devflow-exec.sh allow。")

# ② 圍欄②:shell 讀上游討論檔(cat/head/less/grep/open…)
if re.search(r"docs/dev/[^\s'\"]*/(1-discussion|2-decision|3-prototype)", cmd):
    _obs_deny("prebash", "upstream_read")
    L.die("⛔ 圍欄②:執行期禁讀上游討論文件(shell 亦同)。"
          "要翻上游 = spec 不完整 → devflow-exec.sh stop → 補 spec → 重審。")

# ③ 圍欄③鏡像(A-11):review 期間 shell 讀本 slug 的 6-notes(cat/head/less/grep/open…)。
# 與 _guard_impl.py 的 Read 圍欄③同源 —— phase=="review" 且未 review_unlocked 才擋;
# 缺 phase 鍵(舊 exec.json)時 phase 預設空字串,本段恆不觸發,行為與升版前一致。
phase = state.get("phase") or ""
review_unlocked = bool(state.get("review_unlocked"))
slug = state.get("slug") or ""
if phase == "review" and not review_unlocked and slug:
    m = re.search(r"docs/dev/" + re.escape(slug) + r"/6-implementation-notes[^\s'\"]*", cmd)
    if m:
        _obs_deny("prebash", "review_self_notes")
        L.die(f"⛔ 圍欄③:Stage 7 review 期間禁讀 {m.group(0)}(shell 亦同)—— "
              f"7-review.md 步 4 才准讀 Self-Review(防錨定:先自建矩陣、後讀作者主張)。"
              f"要解鎖:devflow-exec.sh review-unlock {slug}。")

sys.exit(0)
