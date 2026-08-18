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
            sid = h.get("session_id", "")   # h = 模組層已解析的 hook payload(呼叫時已存在)
        except Exception:
            sid = ""
        if sid:
            payload["session_ref"] = sid
        subprocess.run(
            # sys.executable = 正在跑本檔的直譯器;不重新解析路徑,避免兩次解析在
            # 特殊環境(pyenv/conda/Windows Git Bash)下拿到不同直譯器。
            [sys.executable,
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "_obs_impl.py"),
             "hook-event", root],
            input=json.dumps(payload), text=True, capture_output=True, timeout=5)
    except Exception:
        pass


root = sys.argv[1]
# F2:payload 從 stdin 讀(正本 devflow-lib.read_hook_input),不再經環境變數 ——
# export 大 payload 會讓殼層 exec 撞 ARG_MAX,守衛以 rc=126 靜默自壞。
h = L.read_hook_input()
if h is None:
    sys.exit(0)
tool = h.get("tool_name", "")
fp = h.get("tool_input", {}).get("file_path", "")
if not fp:
    sys.exit(0)

state, armed, err = L.load_state(root)
if err:
    L.die(err)
if state is None:
    # ── A1:守衛沉睡的**一次性**可見提醒(2026-08 order-intake 事故)────────────
    #
    # 背景:`.devflow/exec.json` 不存在時本守衛直接放行(load_state 的「沉睡」路徑)。
    # 這對非 dev-flow 工作是正確的,但它讓「dev-flow 執行中但守衛沒武裝」與
    # 「根本沒在跑 dev-flow」**在系統裡長得一模一樣** —— order-intake 那次
    # devflow-exec.sh 因母版 bug 啟動不了(D-9),26 個 T 全程三道守衛(圍欄②/
    # 契約防篡改/scope)一次都沒觸發,而每一份產出看起來都完整,沒有人在當下發現。
    #
    # 觸發條件刻意極窄:**只有**在寫 `docs/dev/<slug>/{5-tasks,6-implementation-notes}.md`
    # 時才響 —— 那兩個檔按定義就是 Stage 6 執行中,不可能是「順手記個筆記」。
    #
    # ⚠️ 為什麼是 exit 2(擋一次)而不是 exit 0 + stderr:PreToolUse 在 exit 0 時
    # stderr **不保證送到模型或使用者眼前**。一個看不見的警告比沒有警告更糟
    # (它讓人以為有守衛)。故採「軟擋一次」:第一次擋下並說明,寫一個 session
    # sentinel,之後同一個 repo 不再打擾。要完全靜音就去武裝,那正是本提醒的目的。
    _fp_rel = L.rel_of(root, fp)
    if tool in ("Write", "Edit") and _fp_rel:
        _parts = _fp_rel.split("/")
        _is_exec_doc = (len(_parts) >= 4 and _parts[0] == "docs" and _parts[1] == "dev"
                        and _parts[3].startswith(("5-tasks", "6-implementation-notes")))
        if _is_exec_doc:
            _once = os.path.join(L.git_dir(root), "devflow-unarmed-notified")
            if not os.path.exists(_once):
                try:
                    open(_once, "w").write(_fp_rel + "\n")
                except Exception:
                    pass          # 寫不進去就每次都提醒,寧可吵不可靜默
                L.die(
                    f"⚠️ devflow-guard **未武裝**,但你正在寫 {_fp_rel}(Stage 6 執行文件)。\n"
                    f"   `.devflow/exec.json` 不存在 → 圍欄②(禁讀上游)、契約防篡改、\n"
                    f"   scope 守衛(Files 聯集)**三道全部不會觸發**,而產出看起來一樣完整。\n"
                    f"   → 要武裝:devflow-exec.sh start <slug>\n"
                    f"   → 確認狀態:devflow-exec.sh status\n"
                    f"   → 就是要無守衛執行(例:只補記帳):**再執行一次同樣的動作即放行**,\n"
                    f"     本提醒每個 repo 只響一次。但請在 6-notes 記一行「本輪守衛未武裝」,\n"
                    f"     否則 7-review 會把人工守 scope 誤當成守衛守出來的。")
    sys.exit(0)

rel = L.rel_of(root, fp)
if rel is None:
    sys.exit(0)
if L.is_ambient_path(rel):
    sys.exit(0)
slug = state.get("slug", "")
task = state.get("task") or ""          # exec-v2 task-scoped 模式(§7)
feat = f"docs/dev/{slug}/"
# A-11(exec-v3):Stage 7 self-review 圍欄③。"review" 子命令寫 phase="review"
# (絕不可疊在 "mode" 上 —— 該 key 已被 parallel/task 模式佔用,見
# notes/adoption-findings-2026-08-04.md 的地雷段);缺鍵 = 舊 exec.json,
# phase 預設空字串 = 非 review,行為與升版前完全一致。
phase = state.get("phase") or ""
review_unlocked = bool(state.get("review_unlocked"))

if tool == "Read":
    # 圍欄③:Stage 7 review 期間禁讀本 slug 的 6-notes(含 .html twin),直到
    # review-unlock —— 7-review.md 步 0 明文「此刻禁讀」、步 4 才准讀,這是防
    # 錨定的核心機制;圍欄②是散文轉機械的既有先例,本條是它在 Stage 7 的鏡像。
    if phase == "review" and not review_unlocked \
            and rel.startswith(feat + "6-implementation-notes"):
        _obs_deny("guard-read", "review_self_notes", rel)
        L.die(f"⛔ 圍欄③:Stage 7 review 期間禁讀 {rel} —— "
              f"7-review.md 步 4 才准讀 Self-Review(防錨定:先自建矩陣、後讀作者主張)。"
              f"要解鎖:devflow-exec.sh review-unlock {slug or '<slug>'}。")
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

# 圍欄③(續):Stage 7 review 期間,本 slug 的 dev-flow 文檔寫入限縮到
# 7-review*/evidence/ —— 蓋過下面 5-tasks/6-notes 的「恆許」。與 unlock 無關
# (unlock 只放行 Read,Write 限縮維持,見 7-review.md 步 0)。刻意只管
# docs/dev/<slug>/ 底下的東西:非 dev-flow 檔(程式碼、其他路徑)一律不擋 ——
# reviewer 可能要跑測試產生暫存,誤傷比不擋更糟(這裡不判斷,交回下方既有
# scope/in_pool 邏輯處理)。
if phase == "review" and rel.startswith(feat):
    if rel.startswith(feat + "7-review") or rel.startswith(feat + "evidence/"):
        sys.exit(0)
    _obs_deny("guard-write", "review_scope", rel)
    L.die(f"⛔ 圍欄③:Stage 7 review 期間寫入限縮到 {feat}7-review* 與 {feat}evidence/;"
          f"{rel} 屬其他 dev-flow 文檔,禁寫(unlock 不解除本限制)。"
          f"真要改 → devflow-exec.sh stop 後處理。")

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
