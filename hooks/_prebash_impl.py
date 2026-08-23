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
cmd = h.get("tool_input", {}).get("command", "")
if not cmd:
    sys.exit(0)


def _open_talk_session_id():
    """唯讀:已有 OPEN session 就回 session_id。不改 .dev-flow、不改 schema。

    session list 失敗(缺套件 / 尚未 setup)→ None,新場 talk start 仍放行。
    """
    cli = os.path.join(root, "memory", "dev-memory.py")
    if not os.path.isfile(cli):
        return None
    try:
        proc = subprocess.run(
            [sys.executable, cli, "session", "list"],
            cwd=root, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    for row in data.get("open") or []:
        if not isinstance(row, dict):
            continue
        sid = row.get("session_id")
        if not sid:
            continue
        if row.get("mode") in (None, "", "understanding"):
            return sid
    return None


def _python_script_writes(command):
    """python3 script.py / python script.py:腳本裡有 open( 或 .write( 才算寫檔。

    不是 -c。旗標在 .py 前也算(python3 -u / python -B)。
    檔不存在就不編(沒東西可讀)。只讀腳本(只有 print)不編。
    """
    match = re.search(
        r"\bpython3?(?:\s+-[A-Za-z0-9]+)*\s+([^\s-]\S*\.py)\b",
        command,
    )
    if not match:
        return False
    path = match.group(1).strip("'\"")
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    if not os.path.isfile(path):
        return False
    try:
        text = open(path, encoding="utf-8").read(1 << 20)
    except OSError:
        return False
    return "open(" in text or ".write(" in text


def _copy_like_writes(command):
    """cp / mv / install:開頭附近、看得到來源+目標兩個 operand 才編成。

    不掃 rsync / ln / install -d 建目錄。
    cp --help / mv --version / install --help、只有一個 operand 不編。
    """
    match = re.search(
        r"(?:^|[;&|\n]\s*)(cp|mv|install)\b((?:\s+-\S+)*)\s*(.*)$",
        command,
    )
    if not match:
        return False
    verb, flags, rest = match.group(1), match.group(2) or "", match.group(3)
    blob = flags + " " + rest
    if re.search(r"--help|--version", blob):
        return False
    if verb == "install" and re.search(r"(?:^|\s)-d\b", flags):
        return False
    operands = [tok for tok in rest.split() if not tok.startswith("-")]
    return len(operands) >= 2


def _looks_like_write_code(command):
    """最小編成:會改檔的 shell → write_code。不是沙盒、不是黑名單劇場。

    只認這幾種字面(負向測真跑指令字串):
    - python3 -c / python -c 裡有 open( 或 .write(
    - python3 - << / python - <<(stdin 餵)同一字串有 open( 或 .write(
    - python3 script.py / python script.py,腳本裡有 open( 或 .write(
      (旗標在 .py 前也算:python3 -u / python -B)
    - > / >> 寫到檔(/dev/null 與 2>&1 這類 fd 複製除外)
    - heredoc 寫檔(cat > file <<EOF;有 > 的那種已被上一條咬到)
    - tee 寫到檔(/dev/null 除外)
    - sed -i / sed --in-place 改檔
    - cp / mv / install 有來源+目標兩個 operand(不含 --help/--version、install -d)
    只讀(cat / rg / ls)與 talk turn/propose 不會進這裡。
    不掃整段 shell 的任意 python+open((會誤咬 rg "open(" && python3 read.py)。
    """
    if re.search(r"\bpython3?\s+-c\b", command):
        if "open(" in command or ".write(" in command:
            return True
    if re.search(r"\bpython3?(?:\s+-)?\s*<<", command):
        if "open(" in command or ".write(" in command:
            return True
    if _python_script_writes(command):
        return True
    if re.search(r"(?:>>|>)\s*(?!/dev/null\b)(?!\&)[A-Za-z0-9_./~-]+", command):
        return True
    if re.search(r"\btee\b(?:\s+-[a-zA-Z]+)*\s+(?!/dev/null\b)\S+", command):
        return True
    if re.search(r"\bsed\s+(?:-i(?:[.\s=']|$)|--in-place\b)", command):
        return True
    if _copy_like_writes(command):
        return True
    return False


def _devtalk_graph_action(command):
    """Stage 1 graph:把 talk start/end / 知識目錄寫入 / 會改檔的 shell 接到 --action。

    /dev-talk 通常未武裝,必須在 load_state 早退之前跑,否則 --action 永遠只活在測試。
    沒有本機游標 = 新場 talk start 仍放行;已有 OPEN session 再 talk start 仍擋。
    沒游標檔時 talk_end / write_knowledge / write_code 仍送 --action,必須 deny。
    write_code 只在本機有游標檔或已有 OPEN talk session 時才編成 —— 未開場的
    普通寫檔不要誤咬。Stage 6 武裝期對 .devflow 偽造的 X-5b 信任邊界不動。
    """
    action = None
    if re.search(r"dev-memory\.py\s+talk\s+start\b", command):
        action = "talk_start"
    elif re.search(r"dev-memory\.py\s+talk\s+end\b", command):
        action = "talk_end"
    elif re.search(r"\.dev-flow/.+knowledge", command):
        action = "write_knowledge"
    elif _looks_like_write_code(command):
        cursor_path = os.path.join(root, ".devtalk-cursor.json")
        if os.path.isfile(cursor_path) or _open_talk_session_id():
            action = "write_code"
    if not action:
        return
    cursor_path = os.path.join(root, ".devtalk-cursor.json")
    cursor = None
    if os.path.isfile(cursor_path):
        try:
            cursor = json.load(open(cursor_path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cursor = None
        if cursor and not cursor.get("node"):
            cursor = None
    if cursor is None:
        if action == "talk_start":
            sid = _open_talk_session_id()
            if not sid:
                return
            cursor = {"MEMORY_SESSION_ID": sid}
        elif action in ("talk_end", "write_knowledge", "write_code"):
            cursor = {}
        else:
            return
    check = os.path.join(root, "scripts", "check-devtalk-graph.sh")
    if not os.path.isfile(check):
        return
    import tempfile
    payload_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as handle:
            json.dump({"cursor": cursor, "action": action}, handle)
            payload_path = handle.name
        proc = subprocess.run(
            ["bash", check, "--action", payload_path, root],
            capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return
    finally:
        if payload_path:
            try:
                os.unlink(payload_path)
            except OSError:
                pass
    if proc.returncode != 0:
        reason = (proc.stdout or proc.stderr or "action denied").strip()
        _obs_deny("devtalk-graph", action)
        L.die("⛔ dev-talk graph --action deny:" + reason)


def _writes_named_md(command, name):
    """最小編成:指令像在寫這個檔名才算。不是沙盒、不重做 write_code 黑名單。"""
    if name not in command:
        return False
    escaped = re.escape(name)
    if re.search(rf"(?:>>?|tee\b)\s+\S*{escaped}", command):
        return True
    if re.search(rf"open\([^)]*{escaped}", command):
        return True
    return False


def _devstage2_graph_action(command):
    """Stage 2 graph:本機有 .devstage2-cursor.json 才編成 2-decision / 4-spec。

    必須在 load_state 早退之前跑。沒游標檔不攔截 —— 不是沙盒。
    不重做第 1 站 write_code 編成。
    """
    import tempfile

    cursor_path = os.path.join(root, ".devstage2-cursor.json")
    if not os.path.isfile(cursor_path):
        return
    action = None
    if _writes_named_md(command, "2-decision.md"):
        action = "write_decision"
    elif _writes_named_md(command, "4-spec.md"):
        action = "write_spec"
    if not action:
        return
    try:
        cursor = json.load(open(cursor_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        cursor = {}
    if not isinstance(cursor, dict):
        cursor = {}
    check = os.path.join(root, "scripts", "check-devstage2-graph.sh")
    if not os.path.isfile(check):
        return
    payload_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as handle:
            json.dump(
                {
                    "cursor": cursor,
                    "action": action,
                    "slug": cursor.get("slug") or "",
                },
                handle,
            )
            payload_path = handle.name
        proc = subprocess.run(
            ["bash", check, "--action", payload_path, root],
            capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return
    finally:
        if payload_path:
            try:
                os.unlink(payload_path)
            except OSError:
                pass
    if proc.returncode != 0:
        reason = (proc.stdout or proc.stderr or "action denied").strip()
        _obs_deny("devstage2-graph", action)
        L.die("⛔ Stage 2 graph --action deny:" + reason)


_devtalk_graph_action(cmd)
_devstage2_graph_action(cmd)

state, armed, err = L.load_state(root)
if err:
    L.die(err)
if state is None:
    sys.exit(0)

# 信任模型(2026-08-17 fresh 審查 X-5b,裁決=記錄邊界不修):以下字面圍欄防手滑
# 與紀律漂移,不防蓄意偽造 —— agent 可用不含 shell 重導向字面的直譯器(如
# python3 -c "open(...).write(...)")寫檔繞過本圍欄,偽造豁免卡或假
# attempt_started 事件;這與 _dispatch_impl.py 的「首派即最高階」守衛同一個
# 信任邊界(見該檔檔頭同段落),接受並明文化,不做黑名單擴充的防禦劇場。
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
# MED-1(第二批獨立審查):比對故意用**裸檔名**(不要求與 docs/dev/<slug>/ 連續出現於
# 指令字串)。原本要求路徑連續出現會被 shell 技巧繞過 —— 例如 `cd docs/dev/<slug> &&
# cat 6-implementation-notes.md`(cd 把路徑拆開)、`cat docs/dev/*/6-implementation-
# notes.md`(萬用字元代換 slug),這兩種寫法字面上都不含完整連續路徑,嚴格路徑正則
# 抓不到。裸檔名比對換來的取捨:review 期間任何 shell 指令只要**字面**出現這個檔名
# 就會被擋,即使只是 `echo` 這個詞、跟真正讀檔無關(過度攔截)——這是可接受的取捨:
# 命中窗口窄(僅 phase=="review" 且未 unlock 這段期間)、擋下訊息清楚說明原因,且隨時
# 可用 `devflow-exec.sh review-unlock <slug>` 解鎖,不構成長期阻塞。
phase = state.get("phase") or ""
review_unlocked = bool(state.get("review_unlocked"))
slug = state.get("slug") or ""
if phase == "review" and not review_unlocked and slug:
    if re.search(r"6-implementation-notes", cmd):
        _obs_deny("prebash", "review_self_notes")
        L.die("⛔ 圍欄③:Stage 7 review 期間禁讀 6-implementation-notes"
              "(shell 亦同,含 cd/glob 等繞路寫法)—— "
              "7-review.md 步 4 才准讀 Self-Review(防錨定:先自建矩陣、後讀作者主張)。"
              f"要解鎖:devflow-exec.sh review-unlock {slug}。")

sys.exit(0)
