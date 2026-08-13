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
                check(True, "exec-state", f"{have_exec}(exec-v2 已武裝)")
            else:
                info("exec-state",
                     f"legacy compatibility mode —— exec.json 為 v1"
                     f"(schema={have_exec!r},契約要 {want_exec});sequential "
                     f"舊專案可續用,但 parallel/run_id 事件鏈不可用,須明示")
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
    try:
        r = subprocess.run(["bash", "-c", cmd], capture_output=True,
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
