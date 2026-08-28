"""_doctor_impl.py — devflow doctor(P3;薄殼 = devflow-doctor.sh)。

版本握手(共享契約 §9):比對方法論 devflow-contract.json vs plugin
runtime-capabilities.json + vendored schema versions + gate-consistency 實跑結果。
不相容 → **fail-closed** 且明示(不靜默退回舊行為);sequential 舊專案(exec.json
v1)標 legacy compatibility mode(允許但必須明示)。

契約檔解析順序:--contract / $DEVFLOW_CONTRACT / <受測專案>/docs/dev/
devflow-contract.json(dev-setup 散發副本);找不到 → 明確報,fail-closed。
"""
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(HERE, "devflow_obs_vendor", "schema")

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
    """產圖／gate-twin 直譯器:DEVFLOW_PYTHON → 專案 venv → 系統 python3。

    hook 仍走 devflow-python-lib(系統 python3 優先)。這裡管的是
    markdown-it-py==4.0.0 要的 3.12+,不准默默用掉 macOS 3.9。
    """
    candidates = []
    env = os.environ.get("DEVFLOW_PYTHON", "").strip()
    if env:
        candidates.append(env)
    candidates.extend((
        os.path.join(root, ".venv", "bin", "python"),
        os.path.join(root, ".venv", "bin", "python3"),
    ))
    if os.path.isfile("/usr/bin/python3"):
        candidates.append("/usr/bin/python3")
    which = shutil.which("python3")
    if which:
        candidates.append(which)
    seen = set()
    for cand in candidates:
        if not cand or cand in seen:
            continue
        seen.add(cand)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            ver = _python_version(cand)
            if ver:
                return cand, ver
    return None, None


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
                r = subprocess.run(["bash", gpath, "--version"],
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
                    rr = subprocess.run(["bash", gpath, "--print-root"],
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
            hr = subprocess.run(["bash", hpath, "--print-root"],
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
    # macOS /usr/bin/python3 常是 3.9,pip 會靜默停在 3.x。不准叫人覆寫系統 Python。
    exe, ver = resolve_printer_python(root)
    if not exe:
        check(False, "printer-python",
              "找不到產圖／gate-twin 直譯器。建專案 venv 或設 DEVFLOW_PYTHON"
              "指向 3.12+,不要覆寫系統 /usr/bin/python3。")
    elif ver < PRINTER_PY_FLOOR:
        check(False, "printer-python",
              f"{exe} 是 Python {ver[0]}.{ver[1]}。markdown-it-py==4.0.0 要 "
              f"{PRINTER_PY_FLOOR[0]}.{PRINTER_PY_FLOOR[1]}+。"
              "建專案 venv 或設 DEVFLOW_PYTHON 指向 3.12+,"
              "不要覆寫 Apple／系統 Python。")
    else:
        mdit = _mdit_version(exe)
        if mdit and not mdit.startswith("4."):
            check(False, "printer-python",
                  f"{exe} 已是 Python {ver[0]}.{ver[1]},但 markdown-it-py 是 "
                  f"{mdit}(要 4.0.0)。不要靜默留 3.x;在這個 venv 重裝 "
                  f"`pip install 'markdown-it-py==4.0.0'`。")
        else:
            extra = (f",markdown-it-py {mdit}" if mdit
                     else ",markdown-it-py 未裝(gate-twin 會自己 exit 2)")
            check(True, "printer-python",
                  f"{exe} Python {ver[0]}.{ver[1]} ≥ "
                  f"{PRINTER_PY_FLOOR[0]}.{PRINTER_PY_FLOOR[1]}{extra}")

    info("host-install",
         "四邊下一指令見 docs/PLUGIN.md；本機探針 "
         "scripts/check-host-adapter.sh --probe")

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

    # 6d. 契約 schema_versions 出現本 doctor 不認識的 key → 明示未比對(不擋),
    #     防「修法只補已知 key」盲區:新 key 落地時至少看得見。
    known_keys = set(VENDORED_SCHEMAS) | {"exec_state", "gate_result",
                                          "candidate", "gauntlet", "wave_review"}
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
    argv = ["bash", cmd] if os.path.isfile(cmd) else ["bash", "-c", cmd]
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
