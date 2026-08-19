#!/bin/bash
# check-model-tiering — 模型分層稽核(掃 observability ledger 的 attempt 事件)。
#
# 背景:先低階再高階的分層規則(haiku 寫碼 → sonnet 審 → 錯誤才升 opus)目前只住在
# dev-run SKILL 與 owner doctrine 裡,全是 prompt 級紀律。prompt 紀律失效是**靜默的**——
# 沒照做不會有紅字,跟「守衛沒武裝」同一種病。observability ledger 其實每次派工都記了
# model 欄(見 observability/fixtures/runs/*/attempts/*/events.jsonl),但在本檢查之前
# 沒有任何機械檢查在讀它。本腳本補的就是這一層:不管 prompt 有沒有照規矩寫,
# 事後從事件流上看得出來有沒有違反。
#
# ⚠️ 稽核邊界(誠實寫明,不是漏洞):**只稽核 agent_role == "worker" 的 attempt_started
# 事件**。reviewer 首次評審派 sonnet、adviser/仲裁首次介入派 opus,兩者都是制度內
# 合法的起手式(reviewer/adviser 的職責本來就需要較高階模型),不在本檢查的紅線範圍。
# 這條邊界只管「worker 寫碼這條線」有沒有先低階再升階,不判斷 reviewer/adviser 該用
# 哪一階。
#
# 兩條紅線(只對同一 (run_id, task_id) 底下、agent_role=="worker" 的 attempt_started
# 事件,依 timestamp 排序後檢查):
#   ① 首派即最高階:序列中第一筆 worker attempt 的 model 就是最高層級(opus/fable)。
#   ② 跳級:序列中出現連續兩筆 attempt,前一筆是最低層級(haiku)、後一筆直接跳到
#      最高層級(opus/fable),中間完全沒有出現過中間層級(sonnet)的 attempt_started。
#
# 層級判斷對 model 字串做**子字串**比對(haiku=0 < sonnet=1 < opus/fable=2),
# 因為實際 model 欄位可能帶版本後綴(如 "claude-3-5-haiku-20241022")。比對不到任何
# 已知層級關鍵字的 model 字串,不判級、只印 NOTE(不擋 exit,因為新模型名稱上線本來
# 就會暫時不在字典裡,這不是分層違規)。
#
# 用法:
#   scripts/check-model-tiering.sh                   # 自測模式:掃
#                                                     #   scripts/fixtures/model-tiering/。
#                                                     #   good-* 期望零違規;bad-* 前綴目錄
#                                                     #   是負向教材,自測邏輯內建對它們
#                                                     #   斷言「必須抓到違規」(不是額外的
#                                                     #   CLI flag,是自測模式本身的一部分,
#                                                     #   正常真實模式不會去掃 bad-* 目錄)。
#                                                     #   另外若 .devflow/runs/ 存在則一併
#                                                     #   稽核(真實資料)。
#   scripts/check-model-tiering.sh <runs-root> [...]  # 真實模式:對每個給定的 runs 根目錄
#                                                     #   (內含 run_*/attempts/*/events.jsonl)
#                                                     #   做稽核,任何違規 exit 1 並點名。
#                                                     #   參數必須是目錄路徑,不接受
#                                                     #   `--xxx` 這種選項(會被當成不存在
#                                                     #   的路徑,以 usage 錯誤 exit 2)。
#
# 家規(先印計數再看 exit code):每次掃描一律先印
# `runs=N attempts=N worker-tasks=N`。**不論真實模式或自測模式**,一個被掃的目錄
# 存在但解析到 0 筆 attempt_started 事件 → 一律 exit 2 並印 NOT-PARSED(掃描沒咬到
# 東西不等於沒有問題,不可以跟「掃到了、抓到違規」的 exit 1 混在一起);自測模式的
# fixture 永遠要有資料,同樣的規則對自己的 fixture 也適用。
#
# 2026-08-19 派工單 §6.1:上面那條地板抓的是「attempts=0」;**真實模式**另補一條
# 「worker-tasks=0」地板 —— attempts 不是 0(有 reviewer/adviser 起手式)但一筆
# agent_role=="worker" 的都沒有,一樣 exit 2(稽核範圍是空的,不是零違規)。
# 只補在真實模式:自測模式的 good-*/bad-* fixture 全部設計成至少一筆 worker
# attempt,不需要這條;`.devflow/runs` 那條自測分支目前也不重複補,留給下一輪視需要
# 再擴。
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
FIXTURE_DIR="$ROOT/scripts/fixtures/model-tiering"

python3 - "$ROOT" "$FIXTURE_DIR" "$@" <<'PY'
import json
import os
import sys

root = sys.argv[1]
fixture_dir = sys.argv[2]
extra_roots = sys.argv[3:]

TIER_HAIKU, TIER_SONNET, TIER_TOP = 0, 1, 2
TIER_NAMES = {TIER_HAIKU: "haiku", TIER_SONNET: "sonnet", TIER_TOP: "opus/fable"}

# X-5a MED:先前 agent_role != "worker" 一律靜默跳過稽核——reviewer/adviser 首次
# 用高階模型是制度內合法的起手式,跳過是對的;但這個判斷式分不出「合法的
# reviewer/adviser」跟「role 字串打錯字(如 worker 誤植成 wroker)」,兩者都會被
# 同一行 `if event.get("agent_role") != "worker": continue` 靜默吃掉,錯字角色的
# 違規因此永遠不會被稽核到,而且沒有任何輸出讓人發現。已知集合外的 role 現在改成
# 計數 + 顯性列出(不稽核,只是讓「有沒有東西被吃掉」對人可見)。
KNOWN_ROLES = {"worker", "reviewer", "adviser"}


def unknown_role_notes(all_started_events):
    """回傳 (count, 逐筆說明字串 list) —— agent_role 不在 KNOWN_ROLES 集合的
    attempt_started 事件。這些事件本來就不參與稽核(只有 worker 才稽核),但打錯字的
    role 跟合法的 reviewer/adviser 對現行程式碼而言完全無法區分,因此顯性列出來,
    避免「role 拼錯 → 靜默逃逸稽核」(假綠型⑤:斷言/檢查被繞過卻沒人知道)。"""
    unknown = [e for e in all_started_events if e.get("agent_role") not in KNOWN_ROLES]
    lines = [
        f"role={e.get('agent_role')!r} run={e.get('run_id')} task={e.get('task_id')} "
        f"attempt={e.get('attempt_id')}"
        for e in unknown
    ]
    return len(unknown), lines


def tier_of(model):
    if not model:
        return None
    m = model.lower()
    if "haiku" in m:
        return TIER_HAIKU
    if "sonnet" in m:
        return TIER_SONNET
    if "opus" in m or "fable" in m:
        return TIER_TOP
    return None


def load_events(runs_root):
    """回傳 (runs_root 下所有 attempt_started 事件, 統計數字)。
    只收 event_type == attempt_started 且 agent_role == worker 的事件,
    但統計數字(runs/attempts)不分角色,讓「先印計數」反映掃描本身有沒有咬到東西,
    不會被「這批剛好都是 reviewer」誤判成 NOT-PARSED。
    """
    all_runs = set()
    all_attempt_ids = set()
    worker_started = []
    if not os.path.isdir(runs_root):
        return worker_started, all_runs, all_attempt_ids
    for dirpath, _dirnames, filenames in os.walk(runs_root):
        for name in sorted(filenames):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as stream:
                    lines = stream.readlines()
            except OSError:
                continue
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("event_type") != "attempt_started":
                    continue
                run_id = event.get("run_id")
                attempt_id = event.get("attempt_id")
                if run_id:
                    all_runs.add(run_id)
                if attempt_id:
                    all_attempt_ids.add(attempt_id)
                if event.get("agent_role") != "worker":
                    continue
                worker_started.append(event)
    return worker_started, all_runs, all_attempt_ids


def load_all_started(runs_root):
    """回傳 runs_root 下**所有**(不分角色)attempt_started 事件——供邊界樁自測用,
    確認 fixture corpus 裡真的存在 agent_role != worker 的樣本(不然 worker-only
    過濾器沒被驗證過,拿掉也不會有任何測試變紅)。"""
    events = []
    if not os.path.isdir(runs_root):
        return events
    for dirpath, _dirnames, filenames in os.walk(runs_root):
        for name in sorted(filenames):
            if not name.endswith(".jsonl"):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8") as stream:
                    lines = stream.readlines()
            except OSError:
                continue
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("event_type") == "attempt_started":
                    events.append(event)
    return events


def audit(worker_started):
    """對 worker attempt_started 事件跑兩條紅線,回傳 violations 清單(每筆為描述字串)
    與 notes 清單(未知 model 字串)。"""
    groups = {}
    for event in worker_started:
        key = (event.get("run_id"), event.get("task_id"))
        groups.setdefault(key, []).append(event)

    violations = []
    notes = []
    worker_task_keys = set(groups.keys())

    for (run_id, task_id), events in groups.items():
        events = sorted(events, key=lambda e: (e.get("timestamp") or "", e.get("seq") or 0))
        tiers = []
        for event in events:
            model = event.get("model")
            tier = tier_of(model)
            if tier is None:
                notes.append(
                    f"NOTE run={run_id} task={task_id} attempt={event.get('attempt_id')} "
                    f"model={model!r} 不在已知層級字典,不判級")
            tiers.append((event, tier))

        # 規則①:首派即最高階
        first_event, first_tier = tiers[0]
        if first_tier == TIER_TOP:
            violations.append(
                f"first-top: run={run_id} task={task_id} "
                f"attempt={first_event.get('attempt_id')} model={first_event.get('model')} "
                f"— worker 第一筆 attempt_started 就是最高層級({TIER_NAMES[TIER_TOP]})")

        # 規則②:跳級(連續兩筆已知層級的 attempt 之間,haiku 直跳最高階)
        known = [(e, t) for e, t in tiers if t is not None]
        for (prev_e, prev_t), (curr_e, curr_t) in zip(known, known[1:]):
            if prev_t == TIER_HAIKU and curr_t == TIER_TOP:
                violations.append(
                    f"skip-level: run={run_id} task={task_id} "
                    f"attempt={prev_e.get('attempt_id')}(model={prev_e.get('model')}) → "
                    f"attempt={curr_e.get('attempt_id')}(model={curr_e.get('model')}) "
                    f"— 中間無任何 {TIER_NAMES[TIER_SONNET]} 的 attempt_started,haiku 直跳最高階")

    return violations, notes, worker_task_keys


def report_counts(label, worker_started, all_runs, all_attempt_ids, worker_task_keys):
    print(f"  [{label}] runs={len(all_runs)} attempts={len(all_attempt_ids)} "
          f"worker-tasks={len(worker_task_keys)}")


def report_unknown_roles(runs_root):
    """印出 unknown_role_notes() 的結果(若有);回傳 True 表示這次掃描確實
    看到至少一筆未知 role(供自測模式驗證這個機制自己有沒有被觸發過)。"""
    count, lines = unknown_role_notes(load_all_started(runs_root))
    if count == 0:
        return False
    print(f"  NOTE 未知 agent_role 共 {count} 筆(不稽核,顯性化避免打錯字的 role 靜默"
          f"逃逸稽核):")
    for line in lines:
        print(f"    - {line}")
    return True


exit_code = 0

if extra_roots:
    # 真實模式:對每個給定的 runs 根目錄各自稽核
    print("model-tiering:真實模式")
    bad_flags = [a for a in extra_roots if a.startswith("--")]
    if bad_flags:
        print(f"❌ usage:不接受選項參數 {bad_flags}(只吃 0..N 個 runs 根目錄路徑)")
        sys.exit(2)
    any_violation = False
    for runs_root in extra_roots:
        abs_root = runs_root if os.path.isabs(runs_root) else os.path.join(os.getcwd(), runs_root)
        if not os.path.isdir(abs_root):
            print(f"  ❌ 指定的 runs 根目錄不存在:{runs_root}")
            exit_code = max(exit_code, 2)
            continue
        worker_started, all_runs, all_attempt_ids = load_events(abs_root)
        violations, notes, worker_task_keys = audit(worker_started)
        report_counts(runs_root, worker_started, all_runs, all_attempt_ids, worker_task_keys)
        if len(all_attempt_ids) == 0:
            print(f"  ❌ NOT-PARSED:{runs_root} 存在但解析到 0 筆 attempt_started 事件"
                  f"(掃描沒咬到東西,不是沒有違規)")
            exit_code = max(exit_code, 2)
            continue
        # 2026-08-19 派工單 §6.1 地板:上面那條只抓「整批 attempt 都是 0」;
        # 但 all_attempt_ids 不分角色(load_events 的 docstring 講得很清楚),
        # 一個目錄可能有 attempt(例如全是 reviewer/adviser 的起手式)、卻一筆
        # agent_role=="worker" 的都沒有 —— worker_started 因此是空 list,
        # audit([]) 對空輸入永遠回傳零違規,不是「稽核過確定沒事」,是「根本沒東西
        # 可稽核」,兩者混在一起會讓這種 ledger 靜默拿到 PASS(假陽性通過)。
        # 自測模式不需要這條地板(good-*/bad-* fixture 全部設計成至少一筆 worker
        # attempt;真的要驗證這條地板本身有牙齒,靠下面 MT-3 的破壞實驗:餵一個
        # 只有 adviser attempt、沒有任何 worker attempt 的真實 runs 根目錄)。
        if len(worker_task_keys) == 0:
            print(f"  ❌ NOT-PARSED:{runs_root} 有 attempt_started 但沒有任何 "
                  f"agent_role==\"worker\" 的事件(worker-tasks=0,稽核範圍是空的,"
                  f"不是零違規)")
            exit_code = max(exit_code, 2)
            continue
        report_unknown_roles(abs_root)
        for note in notes:
            print(f"  {note}")
        if violations:
            any_violation = True
            for v in violations:
                print(f"  ❌ {v}")
    if exit_code:
        sys.exit(exit_code)
    if any_violation:
        print("❌ model tiering audit: 違反模型分層紅線")
        sys.exit(1)
    print("✅ model tiering audit: 全過")
    sys.exit(0)

# 自測模式:掃 scripts/fixtures/model-tiering/ 下的 good-*/bad-* 兩類 fixture,
# 另外若 repo 內有 .devflow/runs/ 也一併稽核(這是「真的有事件可看」的 repo 場景)。
print("model-tiering:自測模式")

if not os.path.isdir(fixture_dir):
    print(f"❌ fixture 目錄不存在:{fixture_dir}")
    sys.exit(2)

case_dirs = sorted(
    name for name in os.listdir(fixture_dir)
    if os.path.isdir(os.path.join(fixture_dir, name))
)
good_cases = [c for c in case_dirs if not c.startswith("bad-")]
bad_cases = [c for c in case_dirs if c.startswith("bad-")]

if not good_cases:
    print("❌ 自測 fixture 缺 good-* 案例")
    sys.exit(2)
if not bad_cases:
    print("❌ 自測 fixture 缺 bad-* 案例(負向教材缺席,無法驗證守衛真的抓得到)")
    sys.exit(2)

self_test_failed = False   # 自測邏輯錯了(good 誤紅 / bad 沒抓到紅)→ exit 1
not_parsed_failed = False  # 掃描沒咬到東西 → exit 2,跟上面兩種是不同性質的失敗
non_worker_top_pin_seen = False  # X-5a 邊界樁:fixture corpus 裡至少一筆非 worker
                                  # 的最高層級 attempt_started,證明「worker-only」
                                  # 過濾器真的在過濾東西,不是巧合沒撞到
unknown_role_seen = False        # X-5a MED 邊界樁:fixture corpus 裡至少一筆
                                  # agent_role 不在 KNOWN_ROLES 的 attempt_started,
                                  # 證明 unknown-role NOTE 機制真的被觸發過,不是
                                  # 死碼(見假綠型⑤)

for case in good_cases:
    case_root = os.path.join(fixture_dir, case)
    worker_started, all_runs, all_attempt_ids = load_events(case_root)
    violations, notes, worker_task_keys = audit(worker_started)
    report_counts(f"good:{case}", worker_started, all_runs, all_attempt_ids, worker_task_keys)
    if len(all_attempt_ids) == 0:
        print(f"  ❌ NOT-PARSED: fixture {case} 解析到 0 筆 attempt_started 事件")
        not_parsed_failed = True
        continue
    for note in notes:
        print(f"  {note}")
    if violations:
        print(f"  ❌ 自測失敗:good fixture {case} 不該有違規,卻抓到:")
        for v in violations:
            print(f"    - {v}")
        self_test_failed = True
    all_started = load_all_started(case_root)
    if any(tier_of(e.get("model")) == TIER_TOP and e.get("agent_role") != "worker"
           for e in all_started):
        non_worker_top_pin_seen = True
    if report_unknown_roles(case_root):
        unknown_role_seen = True

for case in bad_cases:
    case_root = os.path.join(fixture_dir, case)
    worker_started, all_runs, all_attempt_ids = load_events(case_root)
    violations, notes, worker_task_keys = audit(worker_started)
    report_counts(f"bad:{case}", worker_started, all_runs, all_attempt_ids, worker_task_keys)
    if len(all_attempt_ids) == 0:
        print(f"  ❌ NOT-PARSED: fixture {case} 解析到 0 筆 attempt_started 事件")
        not_parsed_failed = True
        continue
    if not violations:
        print(f"  ❌ 自測失敗:負向教材 {case} 應該被抓到違規,守衛沒有牙齒")
        self_test_failed = True
    else:
        for v in violations:
            print(f"  (預期紅字,已抓到) {v}")
    if report_unknown_roles(case_root):
        unknown_role_seen = True

if not non_worker_top_pin_seen:
    print("  ❌ 自測失敗:fixture corpus 內找不到「非 worker、最高層級」的 attempt_started"
          "(邊界樁不見了 —— worker-only 過濾器可能被人拿掉卻沒人發現,見假綠型⑤)")
    self_test_failed = True

if not unknown_role_seen:
    print("  ❌ 自測失敗:fixture corpus 內找不到 agent_role 不在 KNOWN_ROLES 的"
          "attempt_started(未知 role 的 NOTE 機制沒被觸發過,可能是死碼,見假綠型⑤)")
    self_test_failed = True

devflow_runs = os.path.join(root, ".devflow", "runs")
if os.path.isdir(devflow_runs):
    worker_started, all_runs, all_attempt_ids = load_events(devflow_runs)
    violations, notes, worker_task_keys = audit(worker_started)
    report_counts(".devflow/runs", worker_started, all_runs, all_attempt_ids, worker_task_keys)
    if len(all_attempt_ids) == 0:
        print("  ❌ NOT-PARSED: .devflow/runs 存在但解析到 0 筆 attempt_started 事件")
        not_parsed_failed = True
    else:
        for note in notes:
            print(f"  {note}")
        if violations:
            print("  ❌ .devflow/runs 內發現真實違規:")
            for v in violations:
                print(f"    - {v}")
            self_test_failed = True
else:
    print("  NOTE: repo 內無 .devflow/runs/,只跑 fixture 自測")

if not_parsed_failed:
    print("❌ model tiering self-test: NOT-PARSED(掃描沒咬到東西)")
    sys.exit(2)
if self_test_failed:
    print("❌ model tiering self-test: 未全過")
    sys.exit(1)
print(f"✅ model tiering self-test: 全過(good={len(good_cases)} bad={len(bad_cases)})")
sys.exit(0)
PY
