"""_doctor_impl.py — devflow doctor(P3;薄殼 = devflow-doctor.sh)。

版本握手(共享契約 §9):比對方法論 devflow-contract.json vs plugin
runtime-capabilities.json + vendored schema versions + gate-consistency 實跑結果。
不相容 → **fail-closed** 且明示(不靜默退回舊行為);sequential 舊專案(exec.json
v1)標 legacy compatibility mode(允許但必須明示)。

契約檔解析順序:--contract / $DEVFLOW_CONTRACT / <受測專案>/docs/dev/
devflow-contract.json(dev-setup 散發副本);找不到 → 明確報,fail-closed。
"""
import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import sysconfig

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(HERE, "devflow_obs_vendor", "schema")
# 執行 .sh 用的 bash:外殼(devflow-doctor.sh / selftest.sh)已用 devflow_find_bash 或 $BASH
# 選出「跑得起來的」並 export DEVFLOW_BASH。沒設就維持字面 bash(舊行為)。
# 不直接寫 PATH 上的 bash:Apple Silicon 上 /usr/local/bin/bash 常是 x86 版,exit 126。
BASH = os.environ.get("DEVFLOW_BASH") or "bash"

# 方法論 schema_versions key → vendored schema 檔
VENDORED_SCHEMAS = {
    "agent_event": "agent-event.schema.json",
    "context_manifest": "context-manifest.schema.json",
    "prompt_registry": "prompt-registry.schema.json",
}


def _load_json(path):
    with open(path) as f:
        return json.load(f)


def _mm(version):
    """major.minor 正規化("1.0.0"→"1.0","1.1"→"1.1")。"""
    parts = str(version).split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else str(version)


def _find_contract(root, cli_path):
    # 明示指定(--contract / $DEVFLOW_CONTRACT)優先且**不 fallback**:
    # 指了但缺檔 = 明確失敗,不靜默改用專案副本(fail-closed)。
    explicit = []
    if cli_path:
        explicit.append(cli_path)
    env = os.environ.get("DEVFLOW_CONTRACT")
    if env:
        explicit.append(env)
    if explicit:
        for c in explicit:
            if os.path.exists(c):
                return c, explicit
        return None, explicit
    candidates = [os.path.join(root, "docs", "dev", "devflow-contract.json")]
    for c in candidates:
        if os.path.exists(c):
            return c, candidates
    return None, candidates


PRINTER_PY_FLOOR = (3, 12)


# 指紋不含內容的兩列:manifest 自己(指紋存在它裡面)與契約(契約內存著指紋),雜湊會自我循環。
SHIP_HASH_EXCLUDED_DESTS = frozenset({"docs/dev/ship-manifest.json", "docs/dev/devflow-contract.json"})


def _ship_content_digest(path):
    """檔案內容 sha256。CRLF 先正規化成 LF(Windows autocrlf 簽出的同內容不得被判過期)。
    與 scripts/devflow_ship_manifest.py::content_digest 同一算法。"""
    import hashlib
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def _ship_row_path(root, row):
    """逐列驗證／指紋要看的檔 = destination(採用樹 root 底下)。例外(與 scripts/devflow_ship_manifest.py::_row_file
    同一定義):方法包自己當專案跑 doctor 時(root = 方法包根),`_templates/X` → `docs/dev/_templates/X` 的模板列
    母版沒有 destination 副本,改看 source。只在 root 就是方法包時才退到 source —— 採用樹就算有自己的 `_templates/`
    也不會遮住 docs/dev/_templates/ 缺檔。"""
    dest = row.get("destination")
    path = os.path.join(root, *dest.split("/"))
    src = row.get("source")
    if (not os.path.isfile(path) and isinstance(src, str) and src.startswith("_templates/")
            and dest.startswith("docs/dev/_templates/") and src[len("_templates/"):] == dest[len("docs/dev/_templates/"):]
            and os.path.realpath(root) == os.path.realpath(os.path.dirname(HERE))):
        alt = os.path.join(root, *src.split("/"))
        if os.path.isfile(alt):
            return alt
    return path


def _ship_manifest_version_v1(rows):
    """舊指紋(v1-):只算列清單(source/destination/mode canonical JSON 的 sha256 前 16 hex)。
    不含檔案內容 —— 3.26.1 改了 build-gate-twin.py 內容、指紋卻沒變,看不出採用專案工具過期。
    保留給舊契約(v1)的採用專案相容比對。"""
    import hashlib
    canon_rows = [{"source": r.get("source"), "destination": r.get("destination"), "mode": r.get("mode")}
                  for r in rows if isinstance(r, dict)]
    canon = json.dumps(canon_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "v1-" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def _ship_manifest_version_v2(rows, root):
    """與 scripts/devflow_ship_manifest.py::compute_version 同一算法(hooks/ 不 import scripts/):
    每列 source/destination/mode 加上 **destination 檔(在採用樹 root 底下)的內容雜湊**,前綴 v2-。
    排除列記 "-"、檔不存在記 "missing"、路徑不合法記 "bad-path"。回傳 (版本, 缺檔 destination list)。
    兩邊字面同步由 check-ship-manifest.sh(母版側)與 selftest p3(doctor 側)各自釘。"""
    import hashlib
    out, missing = [], []
    for r in rows:
        if not isinstance(r, dict):
            continue
        dest = r.get("destination")
        segs = dest.split("/") if isinstance(dest, str) else []
        if dest in SHIP_HASH_EXCLUDED_DESTS:
            digest = "-"
        elif (not isinstance(dest, str) or not dest or dest.startswith(("/", "\\")) or "\\" in dest
              or any(seg in ("", ".", "..") for seg in segs)):
            digest = "bad-path"
        else:
            path = _ship_row_path(root, r)
            if os.path.isfile(path):
                try:
                    digest = _ship_content_digest(path)
                except OSError:
                    digest = "unreadable"
            else:
                digest = "missing"
                missing.append(dest)
        out.append({"source": r.get("source"), "destination": dest, "mode": r.get("mode"), "sha256": digest})
    canon = json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "v2-" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16], missing


# 已散發 .py 的 import 對帳(ship-deps)。manifest 逐列只驗「列出來的 destination 在不在」,
# 驗不到「列出來的工具 import 了一支沒列出來的檔」—— build-gate-twin.py import diagir,
# manifest 卻沒散發 diagir.py,採用專案跑它直接 ImportError,而逐列驗證照樣全綠
# (2026-10-15 採用現場)。這裡靜態掃每支已散發 .py 的 import,不在標準函式庫、也不在
# 下面兩份白名單的,必須能在散發樹裡解析得到;解析不到 = 缺件,fail-closed。
# 不看 `sys.path` 的退路(例如 build-gate-twin 的 _scripts_dir() 會往上找母版 scripts/):
# 採用專案沒有母版 scripts/,把退路算進去就是在冒充已驗。
SHIP_DEPS_THIRD_PARTY_OK = frozenset({"markdown_it"})  # ADR 0002 唯一核准的第三方;缺/版本由 printer-python 項報
SHIP_DEPS_DYNAMIC_OK = frozenset({"agentmem"})         # devflow-jev 自己找 memory/agentmem、缺了 fail-closed 報錯


def _is_stdlib(name):
    names = getattr(sys, "stdlib_module_names", None)       # 3.10+
    if names is not None:
        return name in names or name in sys.builtin_module_names
    if name in sys.builtin_module_names:                     # 3.9 地板:沒有上面那份名單,退回探測
        return True
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError, AttributeError):
        return False
    if spec is None:
        return False
    origin = spec.origin or ""
    if origin in ("built-in", "frozen"):
        return True
    return origin.startswith(sysconfig.get_paths()["stdlib"]) and "site-packages" not in origin


def _py_imports(tree):
    """回傳 [(level, module, lineno)]。包在 `try: … except ImportError/Exception/裸 except` 內的
    是選配相依(呼叫端自己處理缺件),略過。"""
    found = []

    def catches_import_error(handler):
        t = handler.type
        if t is None:
            return True
        names = [n.id for n in (t.elts if isinstance(t, ast.Tuple) else [t]) if isinstance(n, ast.Name)]
        return any(n in ("ImportError", "ModuleNotFoundError", "Exception", "BaseException") for n in names)

    def walk(nodes, guarded):
        for n in nodes:
            if isinstance(n, ast.Import):
                if not guarded:
                    found.extend((0, a.name, n.lineno) for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                if not guarded:
                    found.append((n.level, n.module or "", n.lineno))
            elif isinstance(n, ast.Try):
                walk(n.body, guarded or any(catches_import_error(h) for h in n.handlers))
                for h in n.handlers:
                    walk(h.body, guarded)
                walk(n.orelse, guarded)
                walk(n.finalbody, guarded)
            else:
                walk(ast.iter_child_nodes(n), guarded)

    walk([tree], False)
    return found


def _resolves_in(base, dotted):
    """dotted(a 或 a.b.c)能否在目錄 base 下以 .py 或套件目錄解析。逐層檢查,不看 sys.path。"""
    cur = base
    for part in dotted.split("."):
        if os.path.isfile(os.path.join(cur, part + ".py")):
            return True            # 後面是這個模組內的屬性,不再往下查
        cur = os.path.join(cur, part)
        if not os.path.isdir(cur):
            return False
    return True


def _ship_dep_problems(root, sm_rows):
    """掃 manifest 每個已散發的 .py destination 的 import,回傳 [說明字串]。"""
    problems = []
    for row in sm_rows:
        dest = row.get("destination") if isinstance(row, dict) else None
        if not isinstance(dest, str) or not dest.endswith(".py"):
            continue
        path = os.path.join(root, *dest.split("/"))
        if not os.path.isfile(path):
            continue                # 缺檔本身由逐列驗證報
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=path)
        except (OSError, SyntaxError, ValueError) as e:
            problems.append(f"{dest} 無法解析({type(e).__name__}),不能核對它的 import")
            continue
        here = os.path.dirname(path)
        search = [here]             # 絕對 import 的根:自己所在目錄,以及所屬套件的上一層
        top = here
        while os.path.isfile(os.path.join(top, "__init__.py")) and os.path.dirname(top) != top:
            top = os.path.dirname(top)
            search.append(top)
        for level, mod, lineno in _py_imports(tree):
            if level:
                if not mod:
                    continue        # `from . import x`:x 可能是屬性也可能是子模組,不誤判
                base = here
                for _ in range(level - 1):
                    base = os.path.dirname(base)
                if not _resolves_in(base, mod):
                    problems.append(f"{dest}:{lineno} 相對 import {'.' * level}{mod},散發樹裡沒有對應檔")
                continue
            head = mod.split(".")[0]
            if (_is_stdlib(head) or head in SHIP_DEPS_THIRD_PARTY_OK
                    or head in SHIP_DEPS_DYNAMIC_OK):
                continue
            if not any(_resolves_in(b, mod) for b in search):
                problems.append(
                    f"{dest}:{lineno} import {mod},但 manifest 沒散發它"
                    f"(找不到 {head}.py 或 {head}/)")
    return problems


def _python_version(exe):
    try:
        r = subprocess.run(
            [exe, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return tuple(int(x) for x in r.stdout.strip().split("."))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return None


def resolve_printer_python(root):
    """產圖／gate-twin 直譯器:DEVFLOW_PYTHON → 專案 venv → 系統 python3 → 自動找到的 3.12+。

    hook 仍走 devflow-python-lib(系統 python3 優先)。這裡管的是
    markdown-it-py==4.0.0 要的 3.12+,不准默默用掉 macOS 3.9。
    自動找到的 3.12+ 是 devflow-doctor.sh 用共用的 hooks/devflow-find-python.sh 找、經
    DEVFLOW_FOUND_PYTHON 傳進來的(手動跑 doctor 沒設 DEVFLOW_PYTHON 時,系統 python3 是 3.9
    就不該直接判 INCOMPATIBLE);只在系統 python3 不夠用時才採用,不搶走夠用的系統／venv。
    回傳 (exe, ver, kind),kind ∈ env|venv|system|auto。
    """
    env = os.environ.get("DEVFLOW_PYTHON", "").strip()
    if env:
        ver = _python_version(env)
        if ver:
            return env, ver, "env"
    for rel in (".venv/bin/python", ".venv/bin/python3"):
        cand = os.path.join(root, rel)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            ver = _python_version(cand)
            if ver:
                return cand, ver, "venv"
    candidates = []
    # 系統優先,但不寫死路徑字串 —— runtime-selftest 禁 hooks/ 出現
    # 那串(只准留在 python-lib)。Windows 沒這條路,isfile 會略過。
    sys_py = os.path.join(os.sep, "usr", "bin", "python3")
    if os.path.isfile(sys_py):
        candidates.append(sys_py)
    which = shutil.which("python3")
    if which:
        candidates.append(which)
    seen = set()
    system = (None, None, None)
    for cand in candidates:
        if not cand or cand in seen:
            continue
        seen.add(cand)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            ver = _python_version(cand)
            if ver:
                system = (cand, ver, "system")
                break
    if system[1] is not None and system[1] >= PRINTER_PY_FLOOR:
        return system
    found = os.environ.get("DEVFLOW_FOUND_PYTHON", "").strip()
    if found:
        ver = _python_version(found)
        if ver and ver >= PRINTER_PY_FLOOR:
            return found, ver, "auto"
    return system


def _is_project_printer(exe, kind):
    """只有專案 venv、或 DEVFLOW_PYTHON 指到非系統直譯器,leftover mdit 才 fail-closed。

    CI／selftest 常把 DEVFLOW_PYTHON 指到系統 python3;那仍是系統 leftover,
    不准連坐握手,也不准叫人覆寫系統套件。
    """
    if not exe:
        return False
    norm = exe.replace("\\", "/")
    if "/.venv/" in norm:
        return True
    if kind != "env":
        return False
    real = os.path.realpath(exe)
    sys_py = os.path.join(os.sep, "usr", "bin", "python3")
    if os.path.isfile(sys_py) and os.path.realpath(sys_py) == real:
        return False
    which = shutil.which("python3")
    if which and os.path.realpath(which) == real:
        return False
    return True


def _mdit_version(exe):
    try:
        r = subprocess.run(
            [exe, "-c", "import markdown_it;print(markdown_it.__version__)"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    return None


def run_doctor(root, contract_path="", gate_cmd=""):
    """回傳 (lines, ok)。lines = 逐檢查輸出;ok=False → fail-closed。"""
    lines, ok = [], True

    def check(passed, name, detail):
        nonlocal ok
        mark = "✓" if passed else "✗"
        if not passed:
            ok = False
        lines.append(f"{mark} {name}: {detail}")

    def info(name, detail):
        lines.append(f"• {name}: {detail}")

    # 1. 方法論契約
    found, candidates = _find_contract(root, contract_path)
    if not found:
        check(False, "devflow-contract",
              "找不到 devflow-contract.json(找過:" + "、".join(candidates) + ")。"
              "dev-setup 散發副本應在受測專案 docs/dev/,或以 DEVFLOW_CONTRACT/"
              "--contract 指定。無契約 = 無法握手,fail-closed。")
        return lines, False
    try:
        contract = _load_json(found)
    except Exception as e:
        check(False, "devflow-contract", f"{found} 解析失敗({e}),fail-closed。")
        return lines, False
    info("devflow-contract", found)

    # 2. plugin 聲明
    caps_path = os.environ.get("DEVFLOW_RUNTIME_CAPS") \
        or os.path.join(HERE, "runtime-capabilities.json")
    try:
        caps = _load_json(caps_path)
    except Exception as e:
        check(False, "runtime-capabilities",
              f"讀不到 plugin 聲明 {caps_path}({e}),fail-closed。")
        return lines, False
    info("runtime-capabilities",
         f"{caps_path}(runtime_version={caps.get('runtime_version')})")

    # 3. 契約版本
    need = contract.get("devflow_contract_version", "")
    supported = caps.get("supported_contract_versions", [])
    if need in supported:
        check(True, "contract-version", f"{need} ∈ supported {supported}")
    else:
        check(False, "contract-version",
              f"Methodology requires contract {need} / "
              f"Runtime supports only {', '.join(supported) or '(無)'} / "
              f"Parallel execution is unavailable(fail-closed,不靜默退回舊行為)")

    # 4. 必要 capabilities
    required = contract.get("required_runtime_capabilities", [])
    declared = set(caps.get("capabilities", []))
    missing = [c for c in required if c not in declared]
    if not missing:
        check(True, "capabilities", f"required {required} 全數聲明")
    else:
        extra = ";Parallel execution is unavailable" \
            if "parallel_wave_execution" in missing else ""
        check(False, "capabilities",
              f"缺 {missing}(runtime 未聲明{extra};fail-closed)")

    # 5. schema versions(vendored 檔 vs 契約;major.minor 比對)
    contract_schemas = contract.get("schema_versions", {})
    for key, filename in VENDORED_SCHEMAS.items():
        if key not in contract_schemas:
            continue
        want = contract_schemas[key]
        try:
            have = _load_json(os.path.join(SCHEMA_DIR, filename)).get(
                "schema_version", "?")
        except Exception as e:
            check(False, f"schema:{key}", f"vendored schema 讀取失敗({e})")
            continue
        if _mm(want) == _mm(have):
            check(True, f"schema:{key}", f"contract {want} ≈ runtime {have}")
        else:
            check(False, f"schema:{key}",
                  f"contract {want} / runtime {have} —— 事件互通不可保證"
                  f"(fail-closed;re-vendor 或同步方法論 schema)")

    # 6. exec state(sequential 舊專案 → legacy compatibility mode,允許但明示)
    want_exec = contract_schemas.get("exec_state")
    execp = os.path.join(root, ".devflow", "exec.json")
    if want_exec:
        if os.path.exists(execp):
            try:
                have_exec = _load_json(execp).get("schema")
            except Exception:
                have_exec = None
            if have_exec == want_exec:
                check(True, "exec-state", f"{have_exec}(已武裝)")
            elif have_exec is None:
                # 真的沒有 schema 欄 = 升版前武裝的舊狀態(v1)。
                info("exec-state",
                     f"legacy compatibility mode —— exec.json 為 v1"
                     f"(無 schema 欄,契約要 {want_exec});sequential "
                     f"舊專案可續用,但 parallel/run_id 事件鏈不可用,須明示")
            else:
                # 有 schema 欄但值與契約不同 —— **不是 v1**,也不代表 run_id 不可用。
                # 2026-08-19 §7 前置修復之後,sequential 三條武裝路徑寫的是 exec-v4,
                # 而契約的 exec_state 仍是 exec-v3(task-scoped 那條),雙軌並存是常態。
                # 舊訊息在這種情況會印「為 v1」「run_id 不可用」,兩句都與事實相反 ——
                # 那是誤導,不是相容性問題,所以分開講。
                info("exec-state",
                     f"exec.json 的 schema 是 {have_exec!r},契約 exec_state 寫 "
                     f"{want_exec} —— 兩邊不同但都帶 schema 欄,不是 v1 舊格式。"
                     f"可能是 runtime 比契約新(或反之);武裝本身有效,"
                     f"是否要讓契約反映雙軌由人判斷")
        else:
            info("exec-state",
                 f"未武裝(無 exec.json);start 後須為 {want_exec}")
    for key in ("gate_result", "candidate"):
        if key in contract_schemas:
            info(f"schema:{key}",
                 f"{contract_schemas[key]}(由 execution/gauntlet 軌檔案提供,"
                 f"本 doctor 不在此驗;integration 後由該軌 selftest 覆蓋)")

    # 6b. gauntlet version(M3:受測專案散發副本 --version 實跑 vs 契約)
    want_gauntlet = contract_schemas.get("gauntlet")
    if want_gauntlet:
        gpath = os.path.join(root, "docs", "dev", "tools",
                             "devflow-evidence-gauntlet.sh")
        if not os.path.exists(gpath):
            check(False, "gauntlet",
                  f"散發副本缺:{gpath} 不存在(契約要 gauntlet "
                  f"{want_gauntlet});fail-closed —— 跑 dev-setup 重散發 tools/。")
        else:
            have_g, detail = None, ""
            try:
                r = subprocess.run([BASH, gpath, "--version"],
                                   capture_output=True, text=True, timeout=30)
                out = (r.stdout or "").strip()
                if r.returncode == 0 and out:
                    have_g = out.split()[-1]
                else:
                    detail = (r.stderr or out or "無輸出").strip().splitlines()[0]
            except Exception as e:
                detail = str(e)
            if have_g is None:
                check(False, "gauntlet",
                      f"散發副本不支援 --version 或不可執行({detail});"
                      f"舊版腳本,fail-closed —— 跑 dev-setup 重散發 tools/。")
            elif have_g == want_gauntlet:
                check(True, "gauntlet",
                      f"contract {want_gauntlet} = 散發副本 {have_g}"
                      f"(--version 實跑)")
            else:
                check(False, "gauntlet",
                      f"contract {want_gauntlet} / 散發副本 {have_g} 不一致;"
                      f"fail-closed —— 跑 dev-setup 重散發 tools/。")

            # 6b'. B-4:ROOT 解析探測 —— 只比對 --version 字串測不出散發副本因
            # 目錄深度不同(母版 scripts/ 對散發 docs/dev/tools/)造成的 ROOT
            # 計算差異。只在 --version 有回應(have_g is not None)時才跑,避免
            # 同一支壞掉的散發副本疊報兩條錯誤(那條已由上面的 gauntlet 檢查涵蓋)。
            if have_g is not None:
                root_out, root_detail = None, ""
                try:
                    rr = subprocess.run([BASH, gpath, "--print-root"],
                                       capture_output=True, text=True, timeout=30)
                    rout = (rr.stdout or "").strip()
                    if rr.returncode == 0 and rout:
                        root_out = rout
                    else:
                        root_detail = (rr.stderr or rout or "無輸出").strip().splitlines()[0]
                except Exception as e:
                    root_detail = str(e)
                want_root = os.path.realpath(os.path.join(root, "docs", "dev")).rstrip("/")
                if root_out is None:
                    check(False, "gauntlet-root",
                          f"散發副本不支援 --print-root 或不可執行({root_detail});"
                          f"舊版腳本,fail-closed —— 跑 dev-setup 重散發 tools/。")
                else:
                    got_root = os.path.realpath(root_out).rstrip("/")
                    if got_root == want_root:
                        check(True, "gauntlet-root",
                              f"散發副本解析根 {got_root} = 受測專案 docs/dev"
                              f"(--print-root 實跑)")
                    else:
                        check(False, "gauntlet-root",
                              f"散發副本解析根 {got_root} ≠ 受測專案 docs/dev "
                              f"{want_root} —— ROOT 解析可能因目錄深度或散發位置跑掉;"
                              f"fail-closed —— 跑 dev-setup 重散發 tools/。")

    # 6b''. G1(2026-08-17):history-append 散發副本的專案根解析探測 —— 比照 6b' 的
    # gauntlet-root(第 6 型:同類保護一起長)。該腳本曾用「自身位置/..」推根,
    # 散發到 docs/dev/tools/ 後預設輸出靜默寫到 docs/dev/docs/dev/HISTORY.md。
    # 期望值與 gauntlet 不同:history-append 的根 = **專案根**(它要在根下掛
    # docs/dev/HISTORY.md),gauntlet 的根 = docs/dev(它只找相依)。
    hpath = os.path.join(root, "docs", "dev", "tools", "history-append.sh")
    if os.path.exists(hpath):
        h_out, h_detail = None, ""
        try:
            hr = subprocess.run([BASH, hpath, "--print-root"],
                                capture_output=True, text=True, timeout=30)
            hout = (hr.stdout or "").strip()
            if hr.returncode == 0 and hout:
                h_out = hout
            else:
                h_detail = (hr.stderr or hout or "無輸出").strip().splitlines()[0]
        except Exception as e:
            h_detail = str(e)
        want_h = os.path.realpath(root).rstrip("/")
        if h_out is None:
            check(False, "history-append-root",
                  f"散發副本不支援 --print-root 或解析不到根({h_detail});"
                  f"舊版腳本(G1 巢狀路徑缺陷未修)—— 跑 dev-setup 重散發 tools/。")
        elif os.path.realpath(h_out).rstrip("/") == want_h:
            check(True, "history-append-root",
                  f"散發副本解析根 {h_out} = 專案根(--print-root 實跑;"
                  f"預設輸出 docs/dev/HISTORY.md 不會巢狀)")
        else:
            check(False, "history-append-root",
                  f"散發副本解析根 {h_out} ≠ 專案根 {want_h} —— 預設輸出會寫錯位置"
                  f"(G1:曾巢狀成 docs/dev/docs/dev/HISTORY.md);跑 dev-setup 重散發。")
    else:
        info("history-append-root",
             "docs/dev/tools/history-append.sh 不存在 —— 未散發(舊安裝);"
             "HISTORY 唯一寫入口建議跑 dev-setup 散發後使用。")

    # 6d. 產圖／gate-twin 直譯器:markdown-it-py==4.0.0 要 Python 3.12+。
    # macOS 系統 python3 常是 3.9,pip 會靜默停在 3.x。不准叫人覆寫系統 Python。
    # 系統 leftover mdit 3.x 不擋握手(CI runner／selftest 把 DEVFLOW_PYTHON
    # 指到系統 python3 也算系統);專案 venv 或非系統 DEVFLOW_PYTHON 帶 3.x
    # 才 fail-closed。
    exe, ver, kind = resolve_printer_python(root)
    if not exe:
        check(False, "printer-python",
              "找不到產圖／gate-twin 直譯器。建專案 venv 或設 DEVFLOW_PYTHON"
              "指向 3.12+,不要覆寫系統 python3。")
    elif ver < PRINTER_PY_FLOOR:
        check(False, "printer-python",
              f"{exe} 是 Python {ver[0]}.{ver[1]}。markdown-it-py==4.0.0 要 "
              f"{PRINTER_PY_FLOOR[0]}.{PRINTER_PY_FLOOR[1]}+。"
              "建專案 venv 或設 DEVFLOW_PYTHON 指向 3.12+,"
              "不要覆寫 Apple／系統 Python。"
              "(經 devflow-doctor.sh 跑時,已用共用的 hooks/devflow-find-python.sh 在 PATH、"
              "/opt/homebrew/bin、/usr/local/bin、~/.local/bin 找過 python3.12–3.15,"
              "跑不起來的(例如 x86 版 Bad CPU type)會跳過;仍找不到 = 本機沒有可用的 3.12+,"
              "例:brew install python@3.12 後設 DEVFLOW_PYTHON=/opt/homebrew/bin/python3.12。)")
    else:
        mdit = _mdit_version(exe)
        if mdit and not mdit.startswith("4.") and _is_project_printer(exe, kind):
            check(False, "printer-python",
                  f"{exe} 已是 Python {ver[0]}.{ver[1]},但 markdown-it-py 是 "
                  f"{mdit}(要 4.0.0)。不要靜默留 3.x;在這個 venv 重裝 "
                  f"`pip install 'markdown-it-py==4.0.0'`。")
        elif mdit and not mdit.startswith("4."):
            info("printer-python",
                 f"系統 {exe} 有 leftover markdown-it-py {mdit};"
                 "產圖請用專案 venv 或 DEVFLOW_PYTHON 裝 4.0.0,"
                 "不要覆寫系統套件。")
            check(True, "printer-python",
                  f"{exe} Python {ver[0]}.{ver[1]} ≥ "
                  f"{PRINTER_PY_FLOOR[0]}.{PRINTER_PY_FLOOR[1]}"
                  f"(系統 leftover mdit {mdit} 不擋握手)")
        else:
            extra = (f",markdown-it-py {mdit}" if mdit
                     else ",markdown-it-py 未裝(gate-twin 會自己 exit 3)")
            check(True, "printer-python",
                  f"{exe} Python {ver[0]}.{ver[1]} ≥ "
                  f"{PRINTER_PY_FLOOR[0]}.{PRINTER_PY_FLOOR[1]}{extra}")

    info("host-install",
         "四邊下一指令見 docs/PLUGIN.md；本機探針 "
         "scripts/check-host-adapter.sh --probe")

    # 6e. ship-manifest 逐列(2026-09-23 W2 C1;W0 P0-8 結論:採用側零牙 —— 上游 manifest 新增列
    #     時,採用專案沒有任何本地資料能說「少了一支」。契約帶 ship_manifest_version(列內容指紋),
    #     manifest 自己也是散發列之一;doctor 讀採用樹 docs/dev/ship-manifest.json 逐列驗 destination
    #     存在與 mode,並比對三個值:契約寫的 / manifest 自稱的 / 依列內容重算的)。
    #     契約沒有這個欄 = 2026-09-23 前的舊契約 → 明示略過(不擋;升級契約後才生效,不冒充已驗)。
    want_sm = contract.get("ship_manifest_version")
    if not want_sm:
        info("ship-manifest",
             "契約無 ship_manifest_version(2026-09-23 前契約)—— 散發面逐列驗證略過;"
             "跑 dev-setup upgrade 取得新契約後生效,不得視為已驗")
    else:
        sm_path = os.path.join(root, "docs", "dev", "ship-manifest.json")
        if not os.path.exists(sm_path):
            check(False, "ship-manifest",
                  f"契約要 ship_manifest_version {want_sm},但採用樹缺 {sm_path}"
                  f"(manifest 本身是散發列之一);fail-closed —— 跑 dev-setup upgrade 重散發。")
        else:
            try:
                sm = _load_json(sm_path)
                sm_rows = sm.get("files") or []
                have_sm = sm.get("version")
                # v2(含各檔內容雜湊)與 v1(只含列清單,舊契約)並存:看契約記的前綴決定怎麼重算。
                is_v2 = str(want_sm).startswith("v2-")
                if is_v2:
                    calc_sm, missing_sm = _ship_manifest_version_v2(sm_rows, root)
                else:
                    calc_sm, missing_sm = _ship_manifest_version_v1(sm_rows), []
            except Exception as e:
                sm, sm_rows, have_sm, calc_sm, is_v2, missing_sm = None, [], None, None, False, []
                check(False, "ship-manifest", f"{sm_path} 解析失敗({e});fail-closed。")
            if sm is not None:
                # v1:三值(契約/自稱/依列重算)必須一致。v2:契約 = 自稱 是結構關;「依內容重算」不在這裡擋,
                # 留到逐列與 ship-deps 之後單獨判(缺檔由逐列點名,內容過期不能蓋掉其他具體錯誤)。
                three_ok = (want_sm == have_sm) if is_v2 else (want_sm == have_sm == calc_sm)
                if not three_ok:
                    check(False, "ship-manifest",
                          f"版本三值不一致:契約 {want_sm} / manifest 自稱 {have_sm} / 依列內容重算 {calc_sm}"
                          f" —— 契約與 manifest 副本不是同一批散發,或 manifest 被手改;fail-closed —— 跑 dev-setup upgrade。")
                else:
                    problems, drift = [], []
                    for row in sm_rows:
                        dest = row.get("destination") if isinstance(row, dict) else None
                        if not isinstance(dest, str) or not dest:
                            problems.append(f"列形狀壞:{row!r}")
                            continue
                        segs = dest.split("/")
                        if dest.startswith(("/", "\\")) or "\\" in dest or any(seg in ("", ".", "..") for seg in segs):
                            problems.append(f"destination 路徑不合法(絕對/穿越/反斜線):{dest}")
                            continue
                        path = _ship_row_path(root, row)
                        if not os.path.isfile(path):
                            problems.append(f"缺 {dest}")
                            continue
                        mode = row.get("mode")
                        if os.name == "nt":
                            continue          # Windows 的 st_mode 不代表 mode 位元(.exe/.bat 才有 x);只驗存在
                        is_exec = bool(os.stat(path).st_mode & 0o111)
                        if mode == "755" and not is_exec:
                            problems.append(f"{dest} 清單 755 但無可執行位元")
                        elif mode == "644" and is_exec:
                            drift.append(dest)     # 多了 x 位元多半是 FAT/DrvFs 掛載;留 info,不 fail-closed
                    if drift:
                        info("ship-manifest",
                             f"{len(drift)} 列清單 644 但檔有可執行位元(常見於 FAT/DrvFs 掛載;不擋):"
                             + ",".join(drift[:5]))
                    if problems:
                        check(False, "ship-manifest",
                              f"版本 {want_sm} 一致,但逐列驗證 {len(problems)} 項不符:"
                              + ";".join(problems[:8]) + (" …" if len(problems) > 8 else "")
                              + " —— fail-closed,跑 dev-setup upgrade 逐列重散發。")
                    elif is_v2 and not missing_sm and calc_sm != want_sm:
                        check(False, "ship-manifest",
                              f"版本 {want_sm}(契約與 manifest 一致)但依採用樹實際檔案內容重算得 {calc_sm} —— "
                              "有受管檔(docs/dev/tools/、docs/dev/_templates/ 等)的內容與當次散發不同:過期、被本地改過、或漏更新;"
                              "fail-closed。預覽哪幾支:python3 <方法包>/scripts/devflow-upgrade-manifest.py "
                              "--root <專案根>(dry-run,標「變更」的就是);確認後跑 dev-setup upgrade。")
                    else:
                        extra_v = (";含各檔內容雜湊(v2),受管檔內容與當次散發一致" if is_v2 else "")
                        check(True, "ship-manifest",
                              f"版本 {want_sm} 三值一致;{len(sm_rows)} 列 destination 齊全、mode 一致{extra_v}")
                        if not is_v2:
                            info("ship-manifest-v1",
                                 f"指紋 {want_sm} 是 v1:只算檔案清單、不含檔案內容 —— 看不出 docs/dev/tools/ 內"
                                 "工具檔是否過期(例:3.26.1 改了 build-gate-twin.py,指紋沒變)。"
                                 "不擋;跑 dev-setup upgrade 取得 v2 契約後,內容過期會被這項抓到。")
                    # 逐列驗證只證明「清單列的檔在」;已散發 .py 依賴的檔沒列進清單時它照樣全綠,
                    # 所以另掃 import(缺件在採用專案是跑工具時才 ImportError)。
                    dep_problems = _ship_dep_problems(root, sm_rows)
                    if dep_problems:
                        check(False, "ship-deps",
                              f"已散發工具 import 了沒散發的檔,{len(dep_problems)} 項:"
                              + ";".join(dep_problems[:6]) + (" …" if len(dep_problems) > 6 else "")
                              + " —— fail-closed:這支工具在本專案跑會 ImportError。"
                              "跑 dev-setup upgrade 取新版散發清單與缺的檔(/plugin update 只更新 plugin,不會補 docs/dev/tools/)。")
                    else:
                        check(True, "ship-deps", "已散發 .py 的 import 在散發樹內全部解析得到")

    # 6e'. 採用專案的散發指紋 vs plugin 這版的現行指紋(info,不擋):專案與 plugin 不是同一批散發 = 專案的
    #      docs/dev/tools 等可能過期。v1 指紋看不出內容變動,所以 plugin 升版後 v1 專案至少在這裡看得見差異。
    #      plugin 契約 = <plugin root>/devflow-contract.json(hooks/ 的上一層);讀不到/沒欄位就不比。
    if want_sm:
        try:
            plug = _load_json(os.path.join(os.path.dirname(HERE), "devflow-contract.json")).get("ship_manifest_version")
        except Exception:
            plug = None
        if plug and plug != want_sm:
            info("ship-manifest-upstream",
                 f"plugin 現行散發指紋 {plug},本專案契約記 {want_sm} —— 不是同一批散發,專案的 docs/dev/tools、docs/dev/_templates 等"
                 "可能比 plugin 舊。不擋;預覽差異:python3 <方法包>/scripts/devflow-upgrade-manifest.py "
                 "--root <專案根>(dry-run),確認後 dev-setup upgrade。")

    # 6c. wave_review schema(M3:契約 vs runtime-capabilities 聲明;
    #     runtime 實際字串 = devflow-lib wave review 驗證所認 schema)
    want_wr = contract_schemas.get("wave_review")
    if want_wr:
        have_wr = (caps.get("schema_versions") or {}).get("wave_review")
        if have_wr == want_wr:
            check(True, "wave_review",
                  f"contract {want_wr} = runtime 聲明 {have_wr}")
        else:
            check(False, "wave_review",
                  f"contract {want_wr} / runtime 聲明 {have_wr!r} —— "
                  f"wave review 產物互通不可保證(fail-closed;更新 "
                  f"runtime-capabilities.json schema_versions 或同步 runtime)")

    # 6c2. memory_local / memory_durable(Agent Memory v3 的本機 DB / durable 檔 schema 版本)。
    #      正式欄位:契約與 runtime-capabilities.json 都宣告,值與 memory/agentmem/__init__.py 的
    #      LOCAL_SCHEMA_VERSION / DURABLE_SCHEMA_VERSION 同值(母版由 check-memory-architecture.sh
    #      對帳)。採用專案端沒有 agentmem 原始碼可比,所以這裡比「契約 vs runtime 聲明」,與
    #      wave_review 同形;不比對會讓 6d 每次都報「memory_* 未比對」的假警報。
    for key in ("memory_local", "memory_durable"):
        if key not in contract_schemas:
            continue
        want_mem = contract_schemas[key]
        have_mem = (caps.get("schema_versions") or {}).get(key)
        if str(have_mem) == str(want_mem):
            check(True, f"schema:{key}", f"contract {want_mem} = runtime 聲明 {have_mem}")
        else:
            check(False, f"schema:{key}",
                  f"contract {want_mem} / runtime 聲明 {have_mem!r} —— "
                  f"記憶庫 schema 版本不一致(fail-closed;跑 dev-setup 遷移或更新 "
                  f"runtime-capabilities.json schema_versions)")

    # 6d. 契約 schema_versions 出現本 doctor 不認識的 key → 明示未比對(不擋),
    #     防「修法只補已知 key」盲區:新 key 落地時至少看得見。
    known_keys = set(VENDORED_SCHEMAS) | {"exec_state", "gate_result",
                                          "candidate", "gauntlet", "wave_review",
                                          "memory_local", "memory_durable"}
    unknown_keys = sorted(set(contract_schemas) - known_keys)
    if unknown_keys:
        info("schema:unknown-keys",
             f"契約 schema_versions 含本 doctor 不認識的 key {unknown_keys} —— "
             f"未比對(升級 doctor 以覆蓋;不擋,但不得視為已驗)")

    # 7. gate-consistency 實跑
    cmd = gate_cmd or os.environ.get("DEVFLOW_GATE_CMD") \
        or os.path.join(HERE, "gate-consistency.sh")
    # issue #5:cmd 是實際存在的腳本檔時直接當參數帶給 bash,不要走 `bash -c`——
    # Windows 路徑(D:\dev-flow\hooks\gate-consistency.sh)交給 -c 會被當成一整句
    # 命令,反斜線被 shell 當轉義字元吃掉 → `D:dev-flowhooksgate-consistency.sh:
    # command not found`(exit 127)。非檔案(例:selftest 用的 `true`、帶參數的
    # 自訂命令)照舊走 -c,保持既有語意。
    argv = [BASH, cmd] if os.path.isfile(cmd) else [BASH, "-c", cmd]
    try:
        r = subprocess.run(argv, capture_output=True,
                           text=True, timeout=120)
        tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
        check(r.returncode == 0, "gate-consistency",
              f"exit {r.returncode}({tail[0]})")
    except Exception as e:
        check(False, "gate-consistency", f"執行失敗({e})")

    # 8. prompt registry
    reg_path = os.path.join(HERE, "prompt-registry.json")
    try:
        sys.path.insert(0, os.path.join(HERE, "devflow_obs_vendor"))
        from devflow_obs import event_validate
        errors = event_validate.validate_prompt_registry(_load_json(reg_path))
        check(not errors, "prompt-registry",
              "schema 綠" if not errors else f"{len(errors)} 項錯誤:{errors[:3]}")
    except Exception as e:
        check(False, "prompt-registry", f"讀取/驗證失敗({e})")

    return lines, ok


def main():
    if len(sys.argv) < 2:
        print("用法: _doctor_impl.py <root> [--contract PATH] [--gate-cmd CMD]",
              file=sys.stderr)
        return 1
    root = sys.argv[1]
    args = sys.argv[2:]
    contract_path, gate_cmd = "", ""
    i = 0
    while i < len(args):
        if args[i] == "--contract" and i + 1 < len(args):
            i += 1
            contract_path = args[i]
        elif args[i] == "--gate-cmd" and i + 1 < len(args):
            i += 1
            gate_cmd = args[i]
        i += 1
    lines, ok = run_doctor(root, contract_path, gate_cmd)
    print("=== devflow doctor(版本握手,共享契約 §9)===")
    for line in lines:
        print(line)
    if ok:
        print("✅ devflow doctor: COMPATIBLE")
        return 0
    print("⛔ devflow doctor: INCOMPATIBLE(fail-closed —— 不靜默退回舊行為;"
          "修復不相容項或升級 runtime/方法論後重跑)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
