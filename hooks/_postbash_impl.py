import json
import os
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
            sid = h.get("session_id", "")   # h = 模組層已解析的 hook payload(呼叫時已存在)
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
# F2 同型對齊:讀掉 stdin 的 payload(舊殼層 `cat >/dev/null` 直接丟棄,session_ref
# 永遠帶不上 obs 事件)。本 impl 不依賴 payload 內容,解析失敗照樣掃描 —— 只影響記帳。
h = L.read_hook_input() or {}
state, armed, err = L.load_state(root)
if err:
    L.die(err)
if state is None:
    sys.exit(0)

# 0) shadow-hash 竄改偵測(MAJOR-C):.devflow/{exec,parallel}.json 只准 CLI 寫。
#    heredoc/python 直寫繞得過 prebash regex(蓄意軍備競賽不跟),這裡以 git-dir
#    shadow hash 比對抓 out-of-band 竄改 —— fail-closed alarm,指明被改的檔。
for _name in L.GUARDED_STATE_FILES:
    _msg = L.shadow_mismatch(root, _name)
    if _msg:
        L.die(f"⛔ 偵測網(tamper alarm):{_msg}。守衛狀態與驗收帳只准 devflow-exec.sh 寫;"
              f"復原:exec.json → 重新 start;parallel.json → parallel-init <slug> --reset"
              f"(或還原檔案)。")

slug = state.get("slug", "")
task = state.get("task") or ""          # exec-v2 task-scoped 模式(§7)
feat = f"docs/dev/{slug}/"
# A-11(exec-v3)圍欄③鏡像:review 子命令寫 phase="review"(見 _guard_impl.py 同名
# 註解 —— 該鍵不可疊在 "mode" 上,已被 parallel/task 模式佔用)。缺鍵 = 舊
# exec.json,phase 預設空字串 = 非 review,行為與升版前完全一致。
phase = state.get("phase") or ""
review_unlocked = bool(state.get("review_unlocked"))
review_gate = phase == "review" and not review_unlocked
review_gate_prefixes = (feat + "5-tasks", feat + "6-implementation-notes")
if task:
    # 單寫者原則(§12):task 模式下 5-tasks/6-notes 移出恆許,shell 改動一樣抓
    allowed_prefix = (".devflow/",)
else:
    allowed_prefix = (feat + "5-tasks", feat + "6-implementation-notes", ".devflow/")
baseline = state.get("baseline", {})
if isinstance(baseline, list):                       # 舊格式相容
    baseline = {p: "" for p in baseline}

bad, tampered = [], []

# 1) 契約檔內容或路徑集合變動(即使已 commit 仍抓得到)
contract_hashes = state.get("contract_hashes", {})
if state.get("contract_hash_scope") == "repo-wide-v1":
    actual_contracts = L.protected_contract_hashes(root)
    tampered.extend(sorted(
        name for name in set(contract_hashes) | set(actual_contracts)
        if contract_hashes.get(name) != actual_contracts.get(name)))
else:  # 舊旗標相容:舊版只釘當前 slug,不可把其他既有 feature 誤判成新增
    for name, want in contract_hashes.items():
        if L.sha(os.path.join(root, name)) != want:
            tampered.append(name)

# 2) .gitignore 是守衛控制檔：直接驗 hash，commit 後 status 乾淨也不能繞過
gitignore_hash = baseline.get(".gitignore", "")
if not gitignore_hash or L.sha(os.path.join(root, ".gitignore")) != gitignore_hash:
    bad.append(".gitignore(守衛控制檔內容被改)")

# 3) 工作樹掃描(含 ignored,堵 .gitignore 遮蔽；rename 的來源與目標都驗)
try:
    dirty_paths = L.git_dirty_paths(root)
except RuntimeError as e:
    L.die(f"⛔ 偵測網:無法掃描工作樹({e})。守衛 fail-closed 擋下動作。")
for rel in dirty_paths:
    if rel.startswith(".git/") or L.is_ambient_path(rel):
        continue
    # 圍欄③收緊:review 期間(未 unlock)這兩前綴的「shell 改動恆許」不適用 ——
    # 與 _guard_impl.py 圍欄③(Write 限縮到 {feat}7-review*/evidence/)同源,堵
    # shell 側繞過寫入限縮。git status 本就只回報真異動(不含未改動的已提交檔),
    # 故「Stage 6 遺留未提交」與「review 期間又被 shell 動」不會混淆 —— 前者理應
    # 已隨 Stage 6 收工提交,若進 review 後 git status 仍顯示這兩檔有異動,代表
    # review 期間又被寫。unlock 後 / 非 review 完全不變(下方既有 allowed_prefix
    # 邏輯照舊生效,恢復恆許)。
    if not task and review_gate and rel.startswith(review_gate_prefixes):
        bad.append(f"{rel}(圍欄③:review 期間 shell 改動這兩檔亦禁 —— 恆許暫停,"
                   f"unlock 後 devflow-exec.sh review-unlock {slug or '<slug>'} 恢復)")
        continue
    # 圍欄③寫入白名單鏡像(Backlog D-4,第 6 型「同一條白名單只加在一側」的實例):
    # guard 側(_guard_impl.py)在 review 期間放行 {feat}7-review* 與 {feat}evidence/
    # 的寫入,偵測網也必須同樣放行 —— 修前 review 期間產 7-review.md 會被本迴圈當
    # scope 外改動(採用現場實測撞到,當時以 L1 allow 應急)。與 unlock 無關,
    # 同 guard 側語意(unlock 只放行 Read,寫入限縮/放行範圍不變)。
    # 邊界(審查 MED,裁決 = 保持與 guard 對稱不單邊收緊):`7-review` 是寬前綴,
    # `7-reviewer-x.md` 這類撞名檔也會被放行 —— guard 側同字面同語意(要涵蓋
    # 7-review.md/.html twin),單邊改窄正是本檔在治的第 6 型;撞名產物會在 G3
    # 的 git diff 現形,且窗口只存在於武裝中的 review phase。
    if not task and phase == "review" and rel.startswith((feat + "7-review", feat + "evidence/")):
        continue
    if rel.startswith(allowed_prefix):
        continue
    if rel == ".gitignore":
        continue
    if rel in baseline:
        # baseline 內的髒檔:比內容 hash,變了才算(堵「預埋髒檔再改寫」)
        if baseline[rel] and L.sha(os.path.join(root, rel)) != baseline[rel] \
                and not L.in_pool(rel, state):
            bad.append(rel + "(開跑前既有檔,內容被改)")
        continue
    if L.in_pool(rel, state):
        continue
    bad.append(rel)

if tampered:
    print("⛔ 契約檔內容在執行期被改(經 shell 或外部工具):", file=sys.stderr)
    for t in tampered:
        print("  " + t, file=sys.stderr)
    print("這是 L2:devflow-exec.sh stop → 修 spec → 重審 → 重新 start。", file=sys.stderr)
if bad:
    print(L.scope_violation_message(
        "⛔ 偵測網:scope 外改動出現(可能經 shell 寫入):",
        bad[:20],
        "處置:L1 → devflow-exec.sh allow <file> --reason 並記 D-n;誤寫 → 還原;L2 → stop。"),
        file=sys.stderr)
if tampered:
    _obs_deny("postbash-detect", "contract", tampered[0])
if bad:
    _obs_deny("postbash-detect", "scope", bad[0])
sys.exit(2 if (bad or tampered) else 0)
