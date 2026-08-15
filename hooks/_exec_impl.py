import datetime
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__

from importlib.machinery import SourceFileLoader
L = SourceFileLoader("devflow_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "devflow-lib.py")).load_module()

cmd, root = sys.argv[1], sys.argv[2]
DF = os.path.join(root, ".devflow")
EXECP = os.path.join(DF, "exec.json")
PARP = os.path.join(DF, "parallel.json")
SENT = os.path.join(L.git_dir(root), "devflow-armed")

SAFE_STATES = ("INTEGRATED", "IN_REVIEW", "ACCEPTED")   # 設計 §4.2:Blocked-by 的「可開始」門檻
# exec-v3(A-11):新武裝一律寫 exec-v3;讀取兩版都收 —— 舊 worktree 留著的
# "exec-v2" 字面值不因這次升版斷線(candidate/status 兩處都要認得舊字面值,
# 零回歸鐵則)。
EXEC_SCHEMAS = ("exec-v2", "exec-v3")


def die(msg, code=1):
    print(msg)
    sys.exit(code)


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def git_out(*args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def head_sha():
    sha = git_out("rev-parse", "HEAD")
    if not sha:
        die("拒絕:無法取得 HEAD SHA(不在 git repo 或無 commit)")
    return sha


def spec_gate(slug):
    """4-spec 存在 + approved + OC-4 fast+high 拒絕(start/parallel-init 共用)。"""
    spec = os.path.join(root, "docs", "dev", slug, "4-spec.md")
    if not os.path.exists(spec):
        die(f"拒絕:找不到 {spec}")
    text = open(spec).read()
    st = ""
    for line in text.splitlines(keepends=True):
        if line.startswith("status:"):
            st = line.split(":", 1)[1].strip().split()[0]
            break
    if st != "approved":
        die(f"拒絕:4-spec status={st or '(空)'}(需 approved,先過審)。")
    prof = L.spec_profile(text)
    if prof["lane"] == "fast" and prof["risk"] == "high" and not prof["owner_call_fast_high"]:
        die("⛔ 拒絕啟動:4-spec Verification Profile 為 lane: fast + Risk: high —— "
            "OC-4 規定 Runtime 一律拒絕(fast lane 命中 high 必須自動升 full)。\n"
            "→ 改 4-spec 為 lane: full 並補完整 Profile;或 Owner Call 明示例外:"
            "在 4-spec Profile 區塊加專用欄「- Owner Call 例外:<理由>」(理由必填,"
            "雜訊行不算裁決)。")
    return text


def tasks_path_of(slug):
    return os.path.join(root, "docs", "dev", slug, "5-tasks.md")


def parse_tasks_file(slug):
    path = tasks_path_of(slug)
    if not os.path.exists(path):
        die(f"拒絕:找不到 {path}")
    return L.parse_5_tasks(open(path).read())


def require_clean_parse(slug):
    parsed = parse_tasks_file(slug)
    if parsed["errors"]:
        die("拒絕:5-tasks 驗證失敗(fail-closed):\n  " + "\n  ".join(parsed["errors"]))
    return parsed


def load_parallel(slug=None):
    if not os.path.exists(PARP):
        die("拒絕:找不到 .devflow/parallel.json —— 先跑 devflow-exec.sh parallel-init <slug>")
    try:
        p = json.load(open(PARP))
    except Exception as e:
        die(f"拒絕:.devflow/parallel.json 損壞({e})")
    if slug and p.get("slug") != slug:
        die(f"拒絕:parallel.json 屬於 {p.get('slug')},非 {slug}")
    msg = L.shadow_mismatch(root, "parallel.json")
    if msg:
        die(f"⛔ 拒絕:{msg} —— 疑遭竄改(MAJOR-C),CLI 不在其上繼續記帳;"
            f"還原檔案或 devflow-exec.sh parallel-init {p.get('slug')} --reset 重建。")
    return p


def save_parallel(p):
    os.makedirs(DF, exist_ok=True)
    json.dump(p, open(PARP, "w"), ensure_ascii=False, indent=1)
    L.update_shadow(root)


def record_transition(p, tid, src, dst, note=""):
    p.setdefault("transitions", []).append(
        {"task": tid, "from": src, "to": dst, "at": now(), "note": note})


def transition(p, tid, dst, note=""):
    rec = p["tasks"][tid]
    src = rec["state"]
    if not L.is_legal_transition(src, dst):
        die(f"⛔ 非法轉移:{tid} {src}→{dst}(合法全集見 parallel-stage6 設計 §10)")
    rec["state"] = dst
    record_transition(p, tid, src, dst, note)


def integrated_set(p):
    return {e["task"] for e in p.get("integration_log", [])}


def descendants(parsed, tid):
    """integration DAG 的可達後代(cascade invalidation 用)。"""
    succ = {}
    for a, b in L.integration_edges(parsed):
        succ.setdefault(a, set()).add(b)
    seen, stack = set(), [tid]
    while stack:
        for nxt in succ.get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def dirty_scan_and_baseline(slug, scope, extra_skip_shared):
    """start 前置髒檔掃描 + baseline(legacy 與 task 模式共用;僅恆許前綴不同)。"""
    try:
        dirty_entries = L.git_dirty_paths(root, with_codes=True)
    except RuntimeError as e:
        die(f"拒絕:無法掃描工作樹({e})")
    baseline, outside = {}, []
    feat = f"docs/dev/{slug}/"
    skip = (".devflow/",)
    if extra_skip_shared:
        skip = (".devflow/", feat + "5-tasks", feat + "6-implementation-notes")
    for code, rel in dirty_entries:
        if rel.startswith(".git/") or L.is_ambient_path(rel):
            continue
        if rel.startswith(skip):
            continue
        if rel == ".gitignore":
            # 唯一差異是 start 自己 append 的 ".devflow/" 行 → 良性(否則 stop/start
            # 循環與同 slug re-arm 會被自己的上一次 start 卡死);其他差異照舊拒啟
            head = subprocess.run(["git", "show", "HEAD:.gitignore"], cwd=root,
                                  capture_output=True, text=True)
            head_lines = head.stdout.splitlines() if head.returncode == 0 else []
            try:
                cur_lines = open(os.path.join(root, rel)).read().splitlines()
            except OSError:
                cur_lines = None
            if cur_lines is not None and \
                    [l for l in cur_lines if l.strip() != ".devflow/"] == \
                    [l for l in head_lines if l.strip() != ".devflow/"]:
                continue
            outside.append(rel)
            continue
        if code == L.IGNORED_CODE:
            # A-13:被 .gitignore 忽略的檔(本機環境切換檔、IDE 產物、快取、本機
            # 建置產物)不是「未提交改動」,不該擋開工 —— 否則有本機開發目錄的專案
            # 一律 start 不了。但仍收進 baseline:postbash 偵測網照舊掃 ignored,
            # 靠 baseline 的內容 hash 判「開跑前既有 / 執行期新增或被改」,
            # .gitignore 遮蔽漏洞不因本條放寬。
            baseline[rel] = L.sha(os.path.join(root, rel))
            continue
        if L.in_pool(rel, {"scope": scope, "extra": []}):
            baseline[rel] = L.sha(os.path.join(root, rel))
        else:
            outside.append(rel)
    if outside:
        die(L.scope_violation_message(
            f"⛔ 拒絕啟動:工作樹已有 {len(outside)} 個 scope 外未提交改動(前 10):",
            outside[:10],
            "→ 請先 commit、還原或使用乾淨 worktree，再重新 start。"))
    return baseline


def arm_common(scope):
    """.devflow 建立 + .gitignore 保證 + 契約 hash(start 兩模式共用)。"""
    os.makedirs(DF, exist_ok=True)
    gi = os.path.join(root, ".gitignore")
    if ".devflow/" not in (open(gi).read() if os.path.exists(gi) else ""):
        with open(gi, "a") as f:
            f.write(".devflow/\n")
    return gi


def warn_wide(scope):
    wide = [s for s in scope if s.strip("/") in ("", ".", "docs", "src", "app", "lib")]
    if wide:
        print(f"⚠️  scope 過寬警告:{wide} —— 這等於放行整個目錄,scope guard 幾乎失效。"
              f"建議回 5-tasks 收斂 Files 後重跑。")


if cmd == "start":
    args = sys.argv[3:]
    slug = args[0] if args and not args[0].startswith("--") else ""
    task = ""
    wave_no = 1
    base_flag = feature_base_flag = ""
    i = 1
    while i < len(args):
        if args[i] == "--task" and i + 1 < len(args):
            task = args[i + 1]; i += 2
        elif args[i] == "--wave" and i + 1 < len(args):
            wave_no_raw = args[i + 1]; i += 2
            if not wave_no_raw.isdigit() or int(wave_no_raw) < 1:
                die(f"拒絕:--wave 需正整數,得 {wave_no_raw}")
            wave_no = int(wave_no_raw)
        elif args[i] == "--base" and i + 1 < len(args):
            base_flag = args[i + 1]; i += 2
        elif args[i] == "--feature-base" and i + 1 < len(args):
            feature_base_flag = args[i + 1]; i += 2
        else:
            die(f"拒絕:start 未知參數 {args[i]}(可用:--task T-n / --wave N / --base <sha> / --feature-base <sha>)")
    if not slug:
        die("用法: devflow-exec.sh start <slug>")
    if task and not re.fullmatch(r"T-\d+", task):
        die(f"拒絕:--task 格式需 T-n,得 {task}")

    if os.path.exists(EXECP) or os.path.exists(SENT):
        prev_slug, prev_task = "", ""
        if os.path.exists(EXECP):
            try:
                prev = json.load(open(EXECP))
                prev_slug = prev.get("slug", "")
                prev_task = prev.get("task") or ""
            except Exception:
                prev_slug, prev_task = "", ""
        if not prev_slug and os.path.exists(SENT):
            try:
                sent_parts = open(SENT).read().strip().split()
                prev_slug = sent_parts[0] if sent_parts else ""
                prev_task = sent_parts[1] if len(sent_parts) > 1 else ""
            except Exception:
                prev_slug, prev_task = "", ""
        if prev_slug == slug and prev_task != task:
            die(f"⛔ 拒絕啟動:模組 {prev_slug}"
                f"({'task ' + prev_task if prev_task else 'feature-scope'})仍武裝中,"
                f"本次要求 {'task ' + task if task else 'feature-scope'}。\n"
                f"→ 同 slug 異 task 屬不同 worktree(一樹一武裝);請在該 task 的 worktree start;\n"
                f"→ 若要改本樹武裝身分,先跑 devflow-exec.sh stop 再 start。")
        if prev_slug != slug:
            # 異 slug 或狀態不可讀:一律拒絕,絕不靜默覆寫既有守衛
            who = f"模組 {prev_slug}" if prev_slug else "身分不明的守衛狀態(exec.json/sentinel 損壞)"
            die(f"⛔ 拒絕啟動:{who} 仍武裝中。\n"
                f"→ 同 repo 並行做多個模組,請各開 git worktree(state 天然隔離);\n"
                f"→ 若那個模組已收尾,先跑 devflow-exec.sh stop 再 start。")
        # 同 slug 同 task re-arm:允許(5-tasks 改動後重釘 scope 的正常路徑),往下重建 state
    spec_gate(slug)
    tasks = tasks_path_of(slug)
    if not os.path.exists(tasks):
        die(f"拒絕:找不到 {tasks}")

    tasks_text = open(tasks).read()
    vnext = task or L.has_vnext_fields(tasks_text)

    if not vnext:
        # ---- legacy 路徑:與 v1 行為 byte-identical(零回歸鐵則)----
        task_blocks, current = [], None
        for line in tasks_text.splitlines(keepends=True):
            heading = re.match(r"^##\s+(T-\d+)\b", line)
            if heading:
                if current:
                    task_blocks.append(current)
                current = {"id": heading.group(1), "fields": {}}
                continue
            if re.match(r"^##\s+", line):
                if current:
                    task_blocks.append(current)
                    current = None
                continue
            if current:
                field = re.match(r"\s*-\s*(Covers|Files|Verify|Blocked-by):\s*(.*?)\s*$", line)
                if field:
                    # 同一 T 的保留欄不得出現兩次(理由與 devflow-lib.parse_5_tasks 同)。
                    # 這條 legacy 路徑直接決定 scope,必須 fail-closed 而非 last-write-wins。
                    if field.group(1) in current["fields"]:
                        die(f"拒絕:{current['id']} 重複保留欄「{field.group(1)}」——"
                            f"同一 T 不得出現兩次,後筆不得覆蓋前筆"
                            f"(常見成因:`Boundaries:`／`Intent:` 續行寫成"
                            f" `- {field.group(1)}:` 子項)")
                    current["fields"][field.group(1)] = field.group(2).strip()
        if current:
            task_blocks.append(current)
        if not task_blocks:
            die("拒絕:5-tasks 找不到 ## T-n 區塊")

        scope = set()
        for task_block in task_blocks:
            fields = task_block["fields"]
            for name in ("Covers", "Files", "Verify", "Blocked-by"):
                if not fields.get(name):
                    die(f"拒絕:{task_block['id']} 缺 {name}")
            for raw in fields["Files"].split(","):
                raw = raw.strip().strip("`")
                try:
                    scope.add(L.canonical_scope_path(raw))
                except ValueError as e:
                    die(f"拒絕:{task_block['id']} Files {e}")
        warn_wide(scope)
        baseline = dirty_scan_and_baseline(slug, scope, extra_skip_shared=True)
        gi = arm_common(scope)
        baseline[".gitignore"] = L.sha(gi)
        contract = L.protected_contract_hashes(root)
        data = {"slug": slug,
                "started": now(),
                "scope": sorted(scope), "extra": [],
                "baseline": baseline, "contract_hashes": contract,
                "contract_hash_scope": "repo-wide-v1"}
        json.dump(data, open(EXECP, "w"), ensure_ascii=False, indent=1)
        open(SENT, "w").write(slug + "\n")
        L.update_shadow(root)
        print(f"✅ 執行守衛啟動:{slug}")
        print(f"scope({len(scope)} 項):")
        for s in sorted(scope):
            print("  " + s)
        print(f"契約 hash 已釘住 {len(contract)} 檔;baseline 記錄 {len(baseline)} 個 scope 內既有髒檔(含內容 hash)")
        print("恆許:本 slug 的 5-tasks / 6-implementation-notes;收尾或 L2 → devflow-exec.sh stop")
        sys.exit(0)

    # ---- VNext 路徑(--task 或 5-tasks 含新欄位):完整契約解析,fail-closed ----
    parsed = L.parse_5_tasks(tasks_text)
    if parsed["errors"]:
        die("拒絕:5-tasks 驗證失敗(fail-closed):\n  " + "\n  ".join(parsed["errors"]))

    if not task:
        # feature-scope(v1 語意)武裝:scope = 全 T Files 聯集
        scope = set()
        for t in parsed["tasks"]:
            scope.update(t["files"])
        warn_wide(scope)
        baseline = dirty_scan_and_baseline(slug, scope, extra_skip_shared=True)
        gi = arm_common(scope)
        baseline[".gitignore"] = L.sha(gi)
        contract = L.protected_contract_hashes(root)
        data = {"slug": slug,
                "started": now(),
                "scope": sorted(scope), "extra": [],
                "baseline": baseline, "contract_hashes": contract,
                "contract_hash_scope": "repo-wide-v1"}
        json.dump(data, open(EXECP, "w"), ensure_ascii=False, indent=1)
        open(SENT, "w").write(slug + "\n")
        L.update_shadow(root)
        print(f"✅ 執行守衛啟動:{slug}")
        print(f"scope({len(scope)} 項):")
        for s in sorted(scope):
            print("  " + s)
        if parsed["execution"]["mode"] == "parallel":
            print("ℹ️  execution.mode=parallel:本次為 feature-scope(v1)武裝;"
                  "wave 派工請在各 task worktree 用 start <slug> --task T-n")
        print(f"契約 hash 已釘住 {len(contract)} 檔;baseline 記錄 {len(baseline)} 個 scope 內既有髒檔(含內容 hash)")
        print("恆許:本 slug 的 5-tasks / 6-implementation-notes;收尾或 L2 → devflow-exec.sh stop")
        sys.exit(0)

    # ---- task-scoped 武裝(§7:單寫者 = 派工者)----
    if parsed["execution"]["mode"] != "parallel":
        die("拒絕:--task 需 execution.mode: parallel(sequential 照舊整 feature scope start)")
    tdef = next((t for t in parsed["tasks"] if t["id"] == task), None)
    if tdef is None:
        die(f"拒絕:5-tasks 找不到 {task}(--task 指到不存在的 T)")
    scope = set(tdef["files"])
    warn_wide(scope)
    baseline = dirty_scan_and_baseline(slug, scope, extra_skip_shared=False)
    wave_base = head_sha()
    if base_flag and base_flag != wave_base:
        die(f"⛔ 拒絕啟動:--base {base_flag} 與本 worktree HEAD {wave_base} 不符 —— "
            f"task worktree 必須建立在該 wave 的 wave_base_sha 上(同 Wave 同 Base)。")
    gi = arm_common(scope)
    baseline[".gitignore"] = L.sha(gi)
    contract = L.protected_contract_hashes(root)
    run_id = L.new_run_id()
    data = {"slug": slug,
            "started": now(),
            "scope": sorted(scope), "extra": [],
            "baseline": baseline, "contract_hashes": contract,
            "contract_hash_scope": "repo-wide-v1",
            "schema": "exec-v3",
            "run_id": run_id,
            "mode": parsed["execution"]["mode"],
            "task": task,
            # A-6:task-scoped 武裝的 exec.json 就是這個 T 的守衛狀態,派工者
            # 讀這份物件即可拿到 boundaries/intent(不必回頭重讀 5-tasks)。
            "boundaries": tdef["boundaries"],
            "intent": tdef["intent"],
            "owner": tdef["owner"],
            "wave": {"number": wave_no, "wave_base_sha": wave_base},
            "candidate_sha": None,
            "state": "RUNNING",
            "attempt": 0,
            "feature_initial_base": feature_base_flag or wave_base}
    json.dump(data, open(EXECP, "w"), ensure_ascii=False, indent=1)
    open(SENT, "w").write(f"{slug} {task}\n")
    L.update_shadow(root)
    print(f"✅ 執行守衛啟動:{slug} --task {task}(task-scoped)")
    print(f"scope({len(scope)} 項):")
    for s in sorted(scope):
        print("  " + s)
    print(f"wave={wave_no} wave_base={wave_base} run_id={run_id}")
    print(f"契約 hash 已釘住 {len(contract)} 檔;baseline 記錄 {len(baseline)} 個 scope 內既有髒檔(含內容 hash)")
    print(f"恆許:.devflow/task/{task}/(evidence 專區);5-tasks/6-notes 已移出恆許"
          f"(單寫者=派工者);收尾 → devflow-exec.sh stop")

elif cmd == "stop":
    for p in (EXECP, SENT):
        if os.path.exists(p):
            os.remove(p)
    L.update_shadow(root)
    print("🛑 執行守衛已停(旗標與 sentinel 皆撤)。")

elif cmd == "status":
    if os.path.exists(EXECP):
        try:
            d = json.load(open(EXECP))
        except Exception as e:
            print(f"⚠️ 旗標損壞({e}) —— hooks 現在 fail-closed 擋一切。跑 stop 後重新 start。")
            sys.exit(1)
        if d.get("schema") in EXEC_SCHEMAS and d.get("task"):
            wave = d.get("wave") or {}
            agg = L.contract_agg_hash(d.get("contract_hashes", {}))
            print(f"feature={d.get('slug')} task={d.get('task')} mode={d.get('mode')} "
                  f"worktree={root}")
            print(f"scope={len(d.get('scope', []))} base_sha={wave.get('wave_base_sha', '—')} "
                  f"contract_hash={agg} candidate_sha={d.get('candidate_sha') or '—'} "
                  f"state={d.get('state', '—')}")
            print(f"run_id={d.get('run_id', '—')} wave={wave.get('number', '—')} "
                  f"extra={len(d.get('extra', []))} "
                  f"sentinel={'在' if os.path.exists(SENT) else '缺(異常!)'}")
            sys.exit(0)
        started = d.get("started", "?")
        print(f"slug={d.get('slug')} started={started} scope={len(d.get('scope', []))} "
              f"extra={len(d.get('extra', []))} sentinel={'在' if os.path.exists(SENT) else '缺(異常!)'}")
        try:
            age = datetime.datetime.now() - datetime.datetime.fromisoformat(started)
            if age.total_seconds() > 86400:
                print(f"⚠️  旗標已存在 {age.days} 天 —— 若非執行中,跑 stop 清掉。")
        except Exception:
            pass
    elif os.path.exists(SENT):
        print("⚠️ 異常:sentinel 在但 exec.json 不見 —— hooks 現在 fail-closed 擋一切。跑 stop 復原。")
    else:
        print("無執行旗標(守衛沉睡)")

elif cmd == "allow":
    f = sys.argv[3] if len(sys.argv) > 3 else ""
    reason = sys.argv[4] if len(sys.argv) > 4 else ""
    if not f:
        die('用法: devflow-exec.sh allow <file> --reason "..."')
    if not reason.strip():
        die('拒絕:allow 必須帶 --reason "..."(L1 偏差要留痕,理由會進 D-n)')
    try:
        f = L.canonical_scope_path(f)
    except ValueError as e:
        die(f"拒絕:allow Files {e}")
    if L.is_ambient_path(f):
        print(f"ℹ️  {f} 是 ambient metadata，不需 allow，也不記 D-n。")
        sys.exit(0)
    if not os.path.exists(EXECP):
        die("無旗標,先 start")
    msg = L.shadow_mismatch(root, "exec.json")
    if msg:
        die(f"⛔ 拒絕:{msg} —— 疑遭竄改(MAJOR-C),不在其上擴 scope;"
            f"還原檔案或重新 devflow-exec.sh start 重建。")
    d = json.load(open(EXECP))
    d.setdefault("extra", []).append(
        {"file": f, "reason": reason,
         "at": datetime.datetime.now().isoformat(timespec="seconds")})
    json.dump(d, open(EXECP, "w"), ensure_ascii=False, indent=1)
    L.update_shadow(root)
    print(f"✅ 已擴 scope:{f}(理由:{reason})")
    print("立即在 6-notes Deviations 記 D-n(現象/保守選擇/理由/影響)。")

elif cmd == "candidate":
    # task worktree 內:candidate commit 落 task branch 後,登記到本樹 exec.json(v2)
    sha = sys.argv[3] if len(sys.argv) > 3 else ""
    if not sha:
        die("用法: devflow-exec.sh candidate <sha>")
    if not os.path.exists(EXECP):
        die("無旗標,先 start")
    msg = L.shadow_mismatch(root, "exec.json")
    if msg:
        die(f"⛔ 拒絕:{msg} —— 疑遭竄改(MAJOR-C),不在其上登記 candidate;"
            f"還原檔案或重新 devflow-exec.sh start 重建。")
    d = json.load(open(EXECP))
    if d.get("schema") not in EXEC_SCHEMAS or not d.get("task"):
        die("拒絕:candidate 只用於 task-scoped 守衛(start <slug> --task T-n)")
    full = git_out("rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}")
    if not full:
        die(f"拒絕:candidate SHA {sha} 不是本 repo 的 commit")
    st = d.get("state")
    if st == "RUNNING":
        if not L.is_legal_transition("RUNNING", "CANDIDATE"):
            die("內部錯誤:RUNNING→CANDIDATE 應合法")
        d["state"] = "CANDIDATE"
    elif st == "CANDIDATE":
        pass  # rework 後同 branch 新 candidate(新 attempt),不 amend 舊的
    else:
        die(f"⛔ 非法轉移:{d.get('task')} {st}→CANDIDATE(candidate 只能自 RUNNING 或"
            f" rework 後的 CANDIDATE 重登)")
    d["candidate_sha"] = full
    d["attempt"] = int(d.get("attempt") or 0) + 1
    json.dump(d, open(EXECP, "w"), ensure_ascii=False, indent=1)
    L.update_shadow(root)
    print(f"✅ candidate 已登記:{d['task']} attempt={d['attempt']} sha={full}")
    print(f"下一步:Mechanical Gate —— devflow-exec.sh gate --slug {d['slug']} "
          f"--task {d['task']} --candidate-json .devflow/task/{d['task']}/candidate.json")

elif cmd == "parallel-init":
    args = sys.argv[3:]
    slug = args[0] if args and not args[0].startswith("--") else ""
    if not slug:
        die("用法: devflow-exec.sh parallel-init <slug> [--reset]")
    reset = "--reset" in args
    spec_gate(slug)
    parsed = require_clean_parse(slug)
    if parsed["execution"]["mode"] != "parallel":
        die("拒絕:execution.mode=sequential —— parallel-init 只用於 mode: parallel")
    if os.path.exists(PARP) and not reset:
        die("拒絕:.devflow/parallel.json 已存在(不靜默覆寫);要重來 → parallel-init <slug> --reset")
    base = head_sha()
    p = {"schema": "devflow-parallel.v1",
         "slug": slug,
         "created": now(),
         "feature_initial_base": base,
         "integration_branch": f"integration/{slug}",
         "contract_hash": L.contract_agg_hash(L.protected_contract_hashes(root)),
         "execution": parsed["execution"],
         "wave_number": 0,
         "current_wave": None,
         "tasks": {t["id"]: {"state": "PENDING", "risk": t["risk"],
                             "review_mode": t["review_mode"], "wave": None,
                             "wave_base_sha": None, "candidate_sha": None,
                             "candidate_base_sha": None, "candidate_status": None,
                             "attempt": 0}
                   for t in parsed["tasks"]},
         "integration_log": [],
         "transitions": []}
    save_parallel(p)
    waves = L.compute_waves(parsed)
    print(f"✅ parallel-init:{slug} tasks={len(parsed['tasks'])} "
          f"max_parallel={parsed['execution']['max_parallel_tasks']} "
          f"feature_initial_base={base}")
    print(f"integration branch(由派工者建立):integration/{slug}(自 {base[:12]} 起)")
    print("預估 waves(以目前 done=∅ 推算,實際以每次 wave-open 為準):")
    for i, w in enumerate(waves, 1):
        print(f"  wave {i}: {', '.join(w)}")

elif cmd == "plan":
    args = sys.argv[3:]
    slug = args[0] if args else ""
    if not slug:
        die("用法: devflow-exec.sh plan <slug>")
    parsed = require_clean_parse(slug)
    if parsed["execution"]["mode"] != "parallel":
        print("mode=sequential(照 Blocked-by 拓撲序逐 T,不派生 wave)")
        sys.exit(0)
    done = set()
    if os.path.exists(PARP):
        p = load_parallel(slug)
        done = {tid for tid, rec in p["tasks"].items() if rec["state"] in SAFE_STATES}
    waves = L.compute_waves(parsed, done=done)
    out = {"mode": "parallel",
           "max_parallel_tasks": parsed["execution"]["max_parallel_tasks"],
           "rebuild_integration_on_rework": parsed["execution"]["rebuild_integration_on_rework"],
           "done": sorted(done, key=L._tnum),
           "waves": waves,
           "execution_edges": sorted([a, b] for a, b in L.execution_edges(parsed)),
           "integration_edges": sorted([a, b] for a, b in L.integration_edges(parsed)),
           # A-6:plan 是派工者(人/主模型)拿 5-tasks 派工 Packet 資訊的入口之一
           # —— boundaries/intent/owner 現在真的露出來,不再解析後就丟棄。
           "tasks": {t["id"]: {"risk": t["risk"], "review_mode": t["review_mode"],
                               "files": t["files"], "verify": t["verify"],
                               "boundaries": t["boundaries"], "intent": t["intent"],
                               "owner": t["owner"]}
                     for t in parsed["tasks"]}}
    print(json.dumps(out, ensure_ascii=False, indent=1))

elif cmd == "wave-open":
    args = sys.argv[3:]
    slug = args[0] if args else ""
    if not slug:
        die("用法: devflow-exec.sh wave-open <slug>")
    parsed = require_clean_parse(slug)
    p = load_parallel(slug)
    if p.get("current_wave"):
        die(f"拒絕:wave {p['current_wave']['number']} 尚未 wave-close,不得再開")
    done = {tid for tid, rec in p["tasks"].items() if rec["state"] in SAFE_STATES}
    remaining = [t["id"] for t in parsed["tasks"] if t["id"] not in done]
    if not remaining:
        die("全部 T 已達安全狀態,無 wave 可開(收尾走 dev-run 收尾流程)", 0)
    waves = L.compute_waves(parsed, done=done)
    members = waves[0]
    number = int(p.get("wave_number") or 0) + 1
    base = git_out("rev-parse", "--verify", "--quiet", p["integration_branch"]) or head_sha()
    for tid in members:
        rec = p["tasks"][tid]
        if rec["state"] == "PENDING":
            transition(p, tid, "READY", f"wave {number} open")
        elif rec["state"] == "BLOCKED":
            transition(p, tid, "READY", f"wave {number} open(前置已安全)")
        elif rec["state"] == "REWORK":
            record_transition(p, tid, "REWORK", "REWORK",
                              f"wave {number} 重排(新 Wave Base 重建)")
        else:
            die(f"⛔ 內部不一致:{tid} state={rec['state']} 不應入新 wave")
        rec["wave"] = number
        rec["wave_base_sha"] = base
        rec["candidate_sha"] = None
        rec["candidate_base_sha"] = None
        rec["candidate_status"] = None
    p["wave_number"] = number
    p["current_wave"] = {"number": number, "wave_base_sha": base, "tasks": members}
    save_parallel(p)
    print(f"✅ wave {number} 開啟:{', '.join(members)}")
    print(f"wave_base_sha={base}(同 Wave 同 Base;task worktree 必須自此 SHA 建立)")
    print(f"派工:每 T 開 worktree → devflow-exec.sh start {slug} --task <T-n> "
          f"--wave {number} --base {base}")

elif cmd == "wave-close":
    args = sys.argv[3:]
    slug = args[0] if args else ""
    if not slug:
        die("用法: devflow-exec.sh wave-close <slug>")
    p = load_parallel(slug)
    cw = p.get("current_wave")
    if not cw:
        die("拒絕:目前沒有開啟中的 wave")
    pending = [t for t in cw["tasks"] if p["tasks"][t]["state"] not in ("ACCEPTED", "REWORK")]
    if pending:
        die("拒絕:wave 內尚有未收斂的 T(需 ACCEPTED,或 REWORK 順延下一 wave):\n  "
            + "\n  ".join(f"{t}={p['tasks'][t]['state']}" for t in pending))
    deferred = [t for t in cw["tasks"] if p["tasks"][t]["state"] == "REWORK"]
    p["current_wave"] = None
    save_parallel(p)
    print(f"✅ wave {cw['number']} 關閉。")
    if deferred:
        print(f"⚠️  順延至下一 wave(自新 Wave Base 重建):{', '.join(deferred)}")

elif cmd == "task-candidate":
    args = sys.argv[3:]
    if len(args) < 3:
        die("用法: devflow-exec.sh task-candidate <slug> <T-n> <sha>")
    slug, tid, sha = args[0], args[1], args[2]
    p = load_parallel(slug)
    if tid not in p["tasks"]:
        die(f"拒絕:找不到 {tid}")
    cw = p.get("current_wave")
    if not cw or tid not in cw["tasks"]:
        die(f"拒絕:{tid} 不在開啟中的 wave(candidate 只能在所屬 wave 內登記)")
    rec = p["tasks"][tid]
    if rec.get("candidate_status") == "INVALIDATED_BY_UPSTREAM":
        die(f"⛔ {tid} candidate 已 INVALIDATED_BY_UPSTREAM,必須 task-rework 後自新 Wave Base 重建")
    if rec["state"] not in ("RUNNING", "CANDIDATE"):
        die(f"⛔ 非法轉移:{tid} {rec['state']}→CANDIDATE(candidate 只能自 RUNNING 登記,"
            f"或 rework 後重登)")
    if rec["state"] == "RUNNING":
        transition(p, tid, "CANDIDATE", f"candidate {sha[:12]}")
    else:
        record_transition(p, tid, "CANDIDATE", "CANDIDATE", f"新 attempt candidate {sha[:12]}")
    rec["candidate_sha"] = sha
    rec["candidate_base_sha"] = rec.get("wave_base_sha") or cw["wave_base_sha"]
    rec["candidate_status"] = "VALID"
    rec["attempt"] = int(rec.get("attempt") or 0) + 1
    save_parallel(p)
    print(f"✅ {tid} candidate 登記:sha={sha} candidate_base_sha={rec['candidate_base_sha']} "
          f"attempt={rec['attempt']}")

elif cmd == "task-state":
    args = sys.argv[3:]
    if len(args) < 3:
        die("用法: devflow-exec.sh task-state <slug> <T-n> <STATE>")
    slug, tid, dst = args[0], args[1], args[2]
    if dst not in L.STATES:
        die(f"拒絕:未知狀態 {dst}(全集:{', '.join(L.STATES)})")
    p = load_parallel(slug)
    if tid not in p["tasks"]:
        die(f"拒絕:找不到 {tid}")
    rec = p["tasks"][tid]
    src = rec["state"]
    if dst == "CANDIDATE":
        die("拒絕:進 CANDIDATE 請用 task-candidate <slug> <T-n> <sha>(要登記 candidate SHA)")
    if dst == "INTEGRATED":
        die("拒絕:進 INTEGRATED 請用 task-integrate <slug> <T-n>(要驗 integration DAG 順序)")
    if dst == "REWORK":
        die("拒絕:打回請用 task-rework <slug> <T-n>(要處理 candidate 失效與 rebuild 語意)")
    if rec.get("candidate_status") == "INVALIDATED_BY_UPSTREAM" and \
            dst in ("MECHANICAL_PASS", "QUEUED_FOR_INTEGRATION", "IN_REVIEW", "ACCEPTED"):
        die(f"⛔ {tid} candidate 已 INVALIDATED_BY_UPSTREAM,不得續審/整合 —— "
            f"task-rework 後自新 Wave Base 重建")
    if dst == "RUNNING":
        cw = p.get("current_wave")
        if not cw or tid not in cw["tasks"]:
            die(f"拒絕:{tid} 不在開啟中的 wave,不得進 RUNNING(先 wave-open)")
    if src == "MECHANICAL_PASS" and dst == "IN_REVIEW" and rec["review_mode"] != "dedicated":
        die(f"拒絕:{tid} Review-mode=wave:MECHANICAL_PASS 後走 QUEUED_FOR_INTEGRATION,"
            f"wave review 在整合後(dedicated 才在整合前 IN_REVIEW)")
    if src == "MECHANICAL_PASS" and dst == "QUEUED_FOR_INTEGRATION" and rec["review_mode"] != "wave":
        die(f"拒絕:{tid} Review-mode=dedicated:MECHANICAL_PASS 後必先 IN_REVIEW,"
            f"dedicated review PASS 才准進 integration")
    if src == "IN_REVIEW" and dst == "QUEUED_FOR_INTEGRATION":
        if rec["review_mode"] != "dedicated":
            die(f"拒絕:{tid} Review-mode=wave 不走 IN_REVIEW→QUEUED_FOR_INTEGRATION")
        if tid in integrated_set(p):
            die(f"拒絕:{tid} 已整合,IN_REVIEW 只能收斂為 ACCEPTED 或 task-rework")
    if dst == "ACCEPTED":
        if tid not in integrated_set(p):
            die(f"⛔ 拒絕:{tid} 尚未整合(integration_log 無此 T),不得 ACCEPTED —— "
                f"未整合的 candidate 不得標完成")
        if rec.get("candidate_status") != "VALID":
            die(f"⛔ 拒絕:{tid} 無有效 candidate,不得 ACCEPTED")
        # F2(E2E 加固):review 沒過關不得標完成 —— 該 T 所屬 wave 的 review 必須
        # 已由 `review <slug> --file` 驗證+登記,且該 T verdict=PASS、
        # integration_verdict=PASS(dedicated 成員同受 wave review 覆蓋,同一道閘)
        rv = (p.get("reviews") or {}).get(str(rec.get("wave")))
        if not rv:
            die(f"⛔ 拒絕:wave {rec.get('wave')} 的 review 尚未登記"
                f"(devflow-exec.sh review {slug} --file <review.json> 驗證通過才登記),"
                f"不得 ACCEPTED")
        verdict = (rv.get("tasks") or {}).get(tid)
        if verdict != "PASS":
            die(f"⛔ 拒絕:{tid} 於 wave {rec.get('wave')} review 的 verdict="
                f"{verdict or '(無)'}(需 PASS),不得 ACCEPTED —— FAIL 走 task-rework")
        if rv.get("integration_verdict") != "PASS":
            die(f"⛔ 拒絕:wave {rec.get('wave')} 的 integration_verdict="
                f"{rv.get('integration_verdict')}(需 PASS),不得 ACCEPTED")
    transition(p, tid, dst)
    save_parallel(p)
    print(f"✅ {tid} {src}→{dst}")
    if dst == "ACCEPTED":
        print(f"記帳提醒:只有 ACCEPTED 才勾 5-tasks checkbox(勾的人=派工者)。")

elif cmd == "task-integrate":
    args = sys.argv[3:]
    if len(args) < 2:
        die("用法: devflow-exec.sh task-integrate <slug> <T-n>")
    slug, tid = args[0], args[1]
    parsed = require_clean_parse(slug)
    p = load_parallel(slug)
    if tid not in p["tasks"]:
        die(f"拒絕:找不到 {tid}")
    rec = p["tasks"][tid]
    if rec.get("candidate_status") != "VALID":
        die(f"⛔ 拒絕整合:{tid} candidate 狀態 = {rec.get('candidate_status') or '(無)'}"
            f"(INVALIDATED_BY_UPSTREAM / 未登記皆不得整合)")
    preds = sorted({a for a, b in L.integration_edges(parsed) if b == tid})
    not_ready = [a for a in preds
                 if p["tasks"].get(a, {}).get("state") not in ("INTEGRATED", "ACCEPTED")]
    if not_ready:
        die(f"⛔ 拒絕整合:{tid} 的 integration DAG 前置未整合:"
            + ", ".join(f"{a}={p['tasks'].get(a, {}).get('state')}" for a in not_ready))
    # F1(E2E 加固):candidate 變更必須真的已在目前 branch —— cherry-pick 沒跑/沒生效
    # 不得記 INTEGRATED。機械驗法:candidate commit 的每個變更路徑,HEAD blob 必須
    # 等於 candidate blob(刪除檔則 HEAD 必須不存在);cherry-pick 產物 commit 不同
    # 但 blob 相同,故以 blob 比對而非 commit ancestry。
    cand_sha = rec.get("candidate_sha") or ""
    full = git_out("rev-parse", "--verify", "--quiet", f"{cand_sha}^{{commit}}")
    if not full:
        die(f"⛔ 拒絕整合:{tid} candidate SHA {cand_sha} 不是本 repo 的 commit —— "
            f"先在 integration branch cherry-pick 該 candidate(跑該 T Verify),"
            f"再 task-integrate。")
    dt = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-status", "-r", full],
                        cwd=root, capture_output=True, text=True)
    if dt.returncode:
        die(f"⛔ 拒絕整合:無法讀取 candidate {full[:12]} 的變更清單"
            f"({dt.stderr.strip() or 'git diff-tree failed'})—— fail-closed。")
    mismatch = []
    for line in dt.stdout.splitlines():
        if "\t" not in line:
            continue
        status, path = line.split("\t", 1)
        head_blob = git_out("rev-parse", "--verify", "--quiet", f"HEAD:{path}")
        if status[:1] == "D":
            if head_blob:
                mismatch.append(f"{path}(candidate 刪除但 HEAD 仍存在)")
        else:
            cand_blob = git_out("rev-parse", "--verify", "--quiet", f"{full}:{path}")
            if not head_blob or head_blob != cand_blob:
                mismatch.append(path)
    if mismatch:
        die(f"⛔ 拒絕整合:{tid} candidate 變更未在目前 branch(cherry-pick 未執行"
            f"或未生效):\n  " + "\n  ".join(mismatch[:10]) +
            f"\n→ 在 integration branch 跑 git cherry-pick {full[:12]} 並跑該 T Verify,"
            f"通過後再 task-integrate。")
    transition(p, tid, "INTEGRATED", f"candidate {rec.get('candidate_sha', '')[:12]}")
    p.setdefault("integration_log", []).append(
        {"task": tid, "candidate_sha": rec.get("candidate_sha"),
         "wave": rec.get("wave"), "at": now()})
    save_parallel(p)
    print(f"✅ {tid} INTEGRATED(candidate {rec.get('candidate_sha')})")
    print(f"整合後必跑該 T Verify:{next(t['verify'] for t in parsed['tasks'] if t['id'] == tid)}")

elif cmd == "task-rework":
    args = sys.argv[3:]
    if len(args) < 2:
        die("用法: devflow-exec.sh task-rework <slug> <T-n> [--reason \"...\"] [--owner-call \"...\"]")
    slug, tid = args[0], args[1]
    reason = owner_call = ""
    i = 2
    while i < len(args):
        if args[i] == "--reason" and i + 1 < len(args):
            reason = args[i + 1]; i += 2
        elif args[i] == "--owner-call" and i + 1 < len(args):
            owner_call = args[i + 1]; i += 2
        else:
            i += 1
    parsed = require_clean_parse(slug)
    p = load_parallel(slug)
    if tid not in p["tasks"]:
        die(f"拒絕:找不到 {tid}")
    rec = p["tasks"][tid]
    src = rec["state"]
    was_integrated = tid in integrated_set(p)
    if src == "REWORK":
        die(f"{tid} 已在 REWORK")
    if src == "ACCEPTED":
        if not owner_call.strip():
            die(f"⛔ 拒絕:{tid} 已 ACCEPTED,狀態機無 ACCEPTED→REWORK 邊 —— 推翻已接受的"
                f" T 屬 Owner 裁決,需 --owner-call \"理由\" 留痕")
        rec["state"] = "REWORK"
        record_transition(p, tid, "ACCEPTED", "REWORK",
                          f"owner-call 例外(狀態機全集外):{owner_call}")
    elif src == "MECHANICAL_PASS":
        transition(p, tid, "QUEUED_FOR_INTEGRATION", "組合轉移(MECHANICAL_PASS 無直接 REWORK 邊)")
        transition(p, tid, "REWORK", reason or "打回")
    elif L.is_legal_transition(src, "REWORK"):
        transition(p, tid, "REWORK", reason or "打回")
    else:
        die(f"⛔ 非法轉移:{tid} {src}→REWORK(合法起點:CANDIDATE/QUEUED_FOR_INTEGRATION/"
            f"INTEGRATED/IN_REVIEW;ACCEPTED 需 --owner-call)")
    old_candidate = rec.get("candidate_sha")
    rec["candidate_sha"] = None
    rec["candidate_base_sha"] = None
    rec["candidate_status"] = None
    invalidated = []
    if was_integrated or src == "ACCEPTED":
        # 上游(已整合/已接受)的 candidate 被替換 → 下游未整合 candidate 全失效(OC-3)
        integrated = integrated_set(p)
        for d in sorted(descendants(parsed, tid), key=L._tnum):
            drec = p["tasks"].get(d)
            if not drec:
                continue
            if drec.get("candidate_sha") and d not in integrated \
                    and drec["state"] not in ("INTEGRATED", "ACCEPTED"):
                drec["candidate_status"] = "INVALIDATED_BY_UPSTREAM"
                invalidated.append(d)
        p["integration_log"] = [e for e in p.get("integration_log", []) if e["task"] != tid]
    save_parallel(p)
    print(f"✅ {tid} {src}→REWORK(原 candidate {old_candidate or '—'} 作廢;"
          f"rework 回原 task branch 出新 candidate)")
    if src not in ("ACCEPTED",) and not was_integrated:
        print(f"Wave Base 不變:上游未變,rework 仍用原 wave_base_sha "
              f"{p['tasks'][tid].get('wave_base_sha') or '(依 current wave)'}")
    if invalidated:
        print("⛔ 下游未整合 candidate 標 INVALIDATED_BY_UPSTREAM(不得續審/整合,"
              "必須自新 Wave Base 重建):" + ", ".join(invalidated))
    if was_integrated:
        if p.get("execution", {}).get("rebuild_integration_on_rework", True):
            print("integration rebuild 必要(rebuild_integration_on_rework=true):"
                  "跑 devflow-exec.sh rebuild-plan " + slug)
        else:
            print(f"rebuild_integration_on_rework=false:只 revert {tid} 的整合 commit"
                  f"(快速路徑,風險自負)")

elif cmd == "rebuild-plan":
    args = sys.argv[3:]
    slug = args[0] if args else ""
    if not slug:
        die("用法: devflow-exec.sh rebuild-plan <slug>")
    require_clean_parse(slug)
    p = load_parallel(slug)
    # integration replay = integration_log 現存順序(= 整合當時的 integration DAG 拓撲序)
    entries = [{"task": e["task"], "candidate_sha": e["candidate_sha"], "wave": e.get("wave")}
               for e in p.get("integration_log", [])]
    out = {"schema": "devflow-rebuild-plan.v1",
           "slug": slug,
           "integration_branch": p["integration_branch"],
           "base_sha": p["feature_initial_base"],
           "rebuild_integration_on_rework": p.get("execution", {})
               .get("rebuild_integration_on_rework", True),
           "ordered_candidates": entries,
           "note": "integration branch 必須可由 base_sha + ordered candidate SHA list 完整重現"
                   "(cherry-pick 依序重放;每放一個跑該 T Verify)"}
    print(json.dumps(out, ensure_ascii=False, indent=1))

elif cmd == "review":
    args = sys.argv[3:]
    slug = ""
    bundle_path = file_path = ""
    saw_flag = False   # 任何 --xxx token(不論是否被吃掉)都算,堵「掉字」誤觸發新分支
    i = 0
    while i < len(args):
        if args[i] == "--bundle" and i + 1 < len(args):
            bundle_path = args[i + 1]; saw_flag = True; i += 2
        elif args[i] == "--file" and i + 1 < len(args):
            file_path = args[i + 1]; saw_flag = True; i += 2
        elif not args[i].startswith("--"):
            slug = args[i]; i += 1
        else:
            saw_flag = True; i += 1
    if slug and not file_path and not bundle_path and not saw_flag:
        feat_disp = f"docs/dev/{slug}/"
        # ── A-11:Stage 7 self-review 圍欄③武裝 ──────────────────────────
        # ⚠️ 這不是上面 wave review(--file/--bundle)的變體,是完全不同的用途,
        # 借同一個 "review" 子命令名安全共用:bare `review <slug>`(無任何 --flag)
        # 在舊碼從未被使用過 —— 舊碼下這個呼叫形狀只會落到下面的 usage die,
        # 故挪用不衝突(見 notes/adoption-findings-2026-08-04.md A-11)。
        # ⚠️ 絕不可用 "mode" key(parallel/task 模式已佔用,四處閘門會被污染);
        # 新開 "phase" key,值 "review"。
        if os.path.exists(EXECP):
            msg = L.shadow_mismatch(root, "exec.json")
            if msg:
                die(f"⛔ 拒絕:{msg} —— 疑遭竄改(MAJOR-C),不在其上武裝 review;"
                    f"還原檔案或重新 devflow-exec.sh start 重建。")
            d = json.load(open(EXECP))
            if d.get("slug") != slug:
                die(f"拒絕:.devflow/exec.json 屬於 {d.get('slug')},非 {slug}"
                    f"(review 需與現行武裝的 slug 相符)。")
            d["phase"] = "review"
            d["review_unlocked"] = False
            json.dump(d, open(EXECP, "w"), ensure_ascii=False, indent=1)
            L.update_shadow(root)
            print(f"✅ Stage 7 review 圍欄已武裝:{slug}(沿用既有 Stage 6 exec.json)")
        else:
            # 事後補審場景(無 Stage 6 state):自建最小 exec.json。刻意不要求
            # 4-spec approved(補審可能發生在核准之前);slug 對應的 feature 目錄
            # 至少要存在,免得打錯字憑空造狀態。baseline 收全部現有髒檔,避免
            # 一武裝就被 postbash 誤判既有 WIP 為新增違規;scope 留空 —— 圍欄③
            # 本身只管 docs/dev/<slug>/ 底下的 7-review*/evidence 限縮,不額外
            # 放寬程式碼寫入範圍,真要動別的檔走既有 L1 allow 出口。
            if not os.path.isdir(os.path.join(root, "docs", "dev", slug)):
                die(f"拒絕:找不到 docs/dev/{slug}/(slug 打錯或功能目錄不存在)。")
            try:
                dirty_entries = L.git_dirty_paths(root, with_codes=True)
            except RuntimeError as e:
                die(f"拒絕:無法掃描工作樹({e})")
            baseline = {}
            for _code, _rel in dirty_entries:
                if _rel.startswith(".git/") or L.is_ambient_path(_rel):
                    continue
                baseline[_rel] = L.sha(os.path.join(root, _rel))
            gi = arm_common([])
            baseline[".gitignore"] = L.sha(gi)
            contract = L.protected_contract_hashes(root)
            data = {"slug": slug,
                    "started": now(),
                    "scope": [], "extra": [],
                    "baseline": baseline, "contract_hashes": contract,
                    "contract_hash_scope": "repo-wide-v1",
                    "phase": "review", "review_unlocked": False}
            json.dump(data, open(EXECP, "w"), ensure_ascii=False, indent=1)
            open(SENT, "w").write(slug + "\n")
            L.update_shadow(root)
            print(f"✅ Stage 7 review 圍欄已武裝:{slug}(事後補審 —— 無 Stage 6 state,"
                  f"自建最小 exec.json;baseline 記錄 {len(baseline)} 個既有髒檔)")
        print(f"Read {feat_disp}6-implementation-notes.md 現在禁讀(7-review.md 步 4 才解鎖);"
              f"Write/Edit 限縮到 {feat_disp}7-review* 與 {feat_disp}evidence/。")
        sys.exit(0)
    if bundle_path:
        try:
            bundle = json.load(open(bundle_path))
        except Exception as e:
            die(f"拒絕:review bundle 讀取失敗({e})")
        review, wave_tasks = bundle.get("review", {}), bundle.get("wave_tasks", [])
    elif slug and file_path:
        p = load_parallel(slug)
        cw = p.get("current_wave")
        if not cw:
            die("拒絕:目前沒有開啟中的 wave,無 wave review 對象")
        try:
            review = json.load(open(file_path))
        except Exception as e:
            die(f"拒絕:review 檔讀取失敗({e})")
        wave_tasks = cw["tasks"]
    else:
        die("用法: devflow-exec.sh review <slug> --file <review.json> | review --bundle <bundle.json> | review <slug>")
    errors = L.validate_wave_review(review, wave_tasks)
    if errors:
        print("⛔ wave review 無效(缺一 = 不得推進狀態):")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    if not bundle_path:
        # live 模式:驗過才登記(F2 —— ACCEPTED 的前置);wave 編號必須對上
        if review.get("wave") != cw["number"]:
            die(f"⛔ wave review 無效:review.wave={review.get('wave')} 與開啟中的 "
                f"wave {cw['number']} 不符,拒絕登記")
        p.setdefault("reviews", {})[str(cw["number"])] = {
            "tasks": {e.get("task"): e.get("verdict") for e in review.get("tasks", [])},
            "integration_verdict": review.get("integration_verdict"),
            "registered_at": now()}
        save_parallel(p)
        print(f"✅ wave review 結構合法({len(wave_tasks)} tasks,integration_verdict="
              f"{review.get('integration_verdict')})— 已登記 wave {cw['number']}"
              f"(ACCEPTED 前置條件)")
        sys.exit(0)
    print(f"✅ wave review 結構合法({len(wave_tasks)} tasks,integration_verdict="
          f"{review.get('integration_verdict')})")

elif cmd == "review-unlock":
    # A-11:7-review.md 步 4「此刻才讀 6-notes」的解鎖動作。Write 限縮不受影響
    # (7-review.md:「unlock 後 Read 放行,Write 限縮維持」)。
    args = sys.argv[3:]
    slug = args[0] if args and not args[0].startswith("--") else ""
    if not slug:
        die("用法: devflow-exec.sh review-unlock <slug>")
    if not os.path.exists(EXECP):
        die(f"拒絕:無 .devflow/exec.json —— 先跑 devflow-exec.sh review {slug} 武裝 Stage 7 圍欄。")
    msg = L.shadow_mismatch(root, "exec.json")
    if msg:
        die(f"⛔ 拒絕:{msg} —— 疑遭竄改(MAJOR-C),不在其上解鎖;"
            f"還原檔案或重新 devflow-exec.sh review {slug} 重建。")
    d = json.load(open(EXECP))
    if d.get("slug") != slug:
        die(f"拒絕:.devflow/exec.json 屬於 {d.get('slug')},非 {slug}。")
    if d.get("phase") != "review":
        die(f"拒絕:目前 phase={d.get('phase') or '(無)'},不是 review —— "
            f"先跑 devflow-exec.sh review {slug} 武裝 Stage 7 圍欄。")
    d["review_unlocked"] = True
    json.dump(d, open(EXECP, "w"), ensure_ascii=False, indent=1)
    L.update_shadow(root)
    print(f"✅ review-unlock:{slug} —— docs/dev/{slug}/6-implementation-notes.md 現在可讀"
          f"(7-review.md 步 4);Write/Edit 仍限縮於 7-review*/evidence/。")

else:
    die(f"未知子命令:{cmd}")
