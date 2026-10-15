#!/bin/bash
# test-adopter-ship.sh — 採用專案「散發完整性」的行為牙(Repo-local)。
#
# 起因(2026-10-15 採用現場):ship-manifest 散發了 docs/dev/tools/build-gate-twin.py,卻沒散發它
# import 的 scripts/diagir.py(及 diagir 再 import 的 devflow_atomic.py)。採用專案不帶參數跑它,
# 該印用法並 exit 2,實際是 ImportError、exit 1;而 doctor 的 ship-manifest 逐列驗證只看「清單列的
# 檔在不在」,照樣報 COMPATIBLE。check-ship-manifest.sh 只驗母版內清單與正副本一致,看不到
# 「清單本身漏了依賴」。本檔補這一格:真的依 manifest 把檔複製到臨時目錄(模擬採用專案、身邊沒有
# 母版 scripts/),在裡面跑工具與 doctor。
#
# 咬什麼:
#   ① 依 manifest 完整散發的採用樹:build-gate-twin.py 不帶參數 → exit 2 且印用法、不見 ImportError;
#      對母版 4-spec 模板實跑 → exit 0 產出 html;doctor ship-manifest 與 ship-deps 皆 ✓。
#   ② 舊清單(沒列 diagir.py/devflow_atomic.py,版本指紋與契約同步重算 = 舊版母版散發出去的樣子):
#      不帶參數 → exit 1 並含 diagir(重現現場,證明本測試能抓到);doctor → ship-manifest 仍 ✓
#      (逐列驗證本來就看不到)但 ship-deps ✗ 點名 diagir、整體 INCOMPATIBLE exit 1。
#   ③ 只缺 devflow_atomic.py(傳遞相依:diagir import 它)→ ship-deps ✗ 點名。
#   ④ ship-deps 判準:try/except ImportError 內的選配 import 不誤報;相對 import 的缺件、套件
#      內缺件要報;標準函式庫在 3.9 地板的探測退路(沒有 sys.stdlib_module_names)判對。
#   ⑤ 母版自己:每支已散發 .py 的 import 在散發樹內全部解析得到(新增散發 .py 卻漏依賴 → 紅)。
#
# build-gate-twin.py 的 render 路徑要 3.12+ 且 markdown-it-py==4.0.0(ADR 0002),直譯器取
# DEVFLOW_RENDER_PYTHON(同 check-gate-twin.sh),缺相依 → exit 2(治具故障,不是靜默跳過)。
#
# 用法:scripts/test-adopter-ship.sh [root]
# exit:0 = 全過 / 1 = 任一案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; }
fi
RENDER_PY=${DEVFLOW_RENDER_PYTHON:-python3}
command -v "$RENDER_PY" >/dev/null 2>&1 || { echo "FATAL: 找不到 $RENDER_PY(DEVFLOW_RENDER_PYTHON)" >&2; exit 2; }
"$RENDER_PY" -c "import markdown_it, sys; sys.exit(0 if markdown_it.__version__ == '4.0.0' else 3)" 2>/dev/null || {
  echo "FATAL: $RENDER_PY 沒有 markdown-it-py==4.0.0(build-gate-twin.py 的相依;設 DEVFLOW_RENDER_PYTHON 指向 3.12+ venv)" >&2
  exit 2
}
for f in docs/dev/ship-manifest.json hooks/_doctor_impl.py scripts/devflow_ship_manifest.py _templates/4-spec.md; do
  [ -f "$ROOT/$f" ] || { echo "FATAL: 找不到 $ROOT/$f" >&2; exit 2; }
done

python3 - "$ROOT" "$RENDER_PY" <<'PY'
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

root, render_py = sys.argv[1], sys.argv[2]
MIN_CASES = 21
passed = failed = 0


def check(cond, label, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  ✓ %s" % label)
    else:
        failed += 1
        print("  ✗ %s%s" % (label, (" — " + detail) if detail else ""))


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# 以母版正本版本函式重算指紋(同 devflow_ship_manifest.compute_version)
spec = importlib.util.spec_from_file_location(
    "devflow_ship_manifest", os.path.join(root, "scripts", "devflow_ship_manifest.py"))
sm_mod = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(sm_mod)

# 載入 doctor 實作(hooks/ 不是套件,直接以路徑載)
spec = importlib.util.spec_from_file_location("_doctor_impl", os.path.join(root, "hooks", "_doctor_impl.py"))
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)

CLEAN_ENV = {k: v for k, v in os.environ.items()
             if not k.startswith("DEVFLOW_") and k not in ("PYTHONPATH", "PYTHONHOME")}
CLEAN_ENV["PYTHONDONTWRITEBYTECODE"] = "1"

work = tempfile.mkdtemp(prefix="test-adopter-ship-")


def install(dest_root):
    """依 manifest 逐列 source → destination 複製(= dev-setup 散發;身邊不放母版 scripts/)。"""
    rows = load_json(os.path.join(root, "docs", "dev", "ship-manifest.json"))["files"]
    for row in rows:
        dst = os.path.join(dest_root, *row["destination"].split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(root, *row["source"].split("/")), dst)
        os.chmod(dst, int(row["mode"], 8))
    return rows


def rewrite_manifest(adopter, drop_destinations=(), extra_rows=()):
    """改採用樹的 manifest 列並重算指紋、同步契約(模擬另一批散發)。"""
    mpath = os.path.join(adopter, "docs", "dev", "ship-manifest.json")
    data = load_json(mpath)
    data["files"] = [r for r in data["files"] if r["destination"] not in drop_destinations] + list(extra_rows)
    data["version"] = sm_mod.compute_version(data)
    dump_json(mpath, data)
    cpath = os.path.join(adopter, "docs", "dev", "devflow-contract.json")
    contract = load_json(cpath)
    contract["ship_manifest_version"] = data["version"]
    dump_json(cpath, contract)


def gate_twin(adopter, *args):
    return subprocess.run(
        [render_py, os.path.join(adopter, "docs", "dev", "tools", "build-gate-twin.py"), *args],
        cwd=adopter, env=CLEAN_ENV, capture_output=True, text=True, timeout=120)


def run_doctor(adopter):
    r = subprocess.run(
        [sys.executable, os.path.join(root, "hooks", "_doctor_impl.py"), adopter],
        cwd=adopter, env=CLEAN_ENV, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def line_with(text, needle):
    return next((ln for ln in text.splitlines() if needle in ln), "")


try:
    # ── ① 完整散發的採用樹 ──────────────────────────────────────────────
    print("-- ① 依 manifest 完整散發的採用樹 --")
    good = os.path.join(work, "good")
    install(good)
    check(not os.path.exists(os.path.join(good, "scripts")), "採用樹裡沒有母版 scripts/(後面不會靠母版退路蒙混)")
    r = gate_twin(good)
    check(r.returncode == 2 and "用法" in r.stderr and "ImportError" not in r.stderr,
          "build-gate-twin.py 不帶參數 → exit 2 且印用法(不是 ImportError)",
          "rc=%s stderr=%s" % (r.returncode, r.stderr.strip()[-200:]))
    os.makedirs(os.path.join(good, "docs", "dev", "demo"))
    shutil.copyfile(os.path.join(root, "_templates", "4-spec.md"), os.path.join(good, "docs", "dev", "demo", "4-spec.md"))
    r = gate_twin(good, good, "demo", "4-spec")
    out_html = os.path.join(good, "docs", "dev", "demo", "4-spec.html")
    check(r.returncode == 0 and os.path.isfile(out_html),
          "對母版 4-spec 模板實跑 → exit 0 且寫出 html(走完 diagir.require_write → atomic_write)",
          "rc=%s stderr=%s" % (r.returncode, r.stderr.strip()[-200:]))
    rc, out = run_doctor(good)
    check("✓ ship-manifest" in out, "doctor:ship-manifest 逐列 ✓", line_with(out, "ship-manifest"))
    check("✓ ship-deps" in out and "✗ ship-deps" not in out, "doctor:ship-deps ✓(依賴都在散發樹內)",
          line_with(out, "ship-deps"))

    # ── ② 舊清單:沒列 diagir.py / devflow_atomic.py ──────────────────────
    print("-- ② 舊清單採用樹(現場重現)--")
    old = os.path.join(work, "old")
    install(old)
    for name in ("diagir.py", "devflow_atomic.py"):
        os.remove(os.path.join(old, "docs", "dev", "tools", name))
    rewrite_manifest(old, drop_destinations=("docs/dev/tools/diagir.py", "docs/dev/tools/devflow_atomic.py"))
    r = gate_twin(old)
    check(r.returncode == 1 and "diagir" in r.stderr,
          "重現現場:不帶參數 → exit 1 且 ImportError 點名 diagir(測試抓得到這個缺件)",
          "rc=%s stderr=%s" % (r.returncode, r.stderr.strip()[-200:]))
    rc, out = run_doctor(old)
    check("✓ ship-manifest" in out,
          "doctor:ship-manifest 逐列仍 ✓(證明逐列驗證本來就看不到缺依賴,這就是舊版誤報 COMPATIBLE 的原因)",
          line_with(out, "ship-manifest"))
    check("✗ ship-deps" in out and "diagir" in line_with(out, "ship-deps") and "build-gate-twin.py" in line_with(out, "ship-deps"),
          "doctor:ship-deps ✗ 且點名 build-gate-twin.py import diagir", line_with(out, "ship-deps"))
    check(rc == 1 and "INCOMPATIBLE" in out and "COMPATIBLE\n" not in out.replace("INCOMPATIBLE", ""),
          "doctor:整體 INCOMPATIBLE、exit 1(不再誤報 COMPATIBLE)", "rc=%s" % rc)
    check("dev-setup upgrade" in line_with(out, "ship-deps"), "doctor:訊息指向 dev-setup upgrade 補散發")

    # ── ③ 只缺 devflow_atomic.py(傳遞相依)────────────────────────────────
    print("-- ③ 傳遞相依 --")
    trans = os.path.join(work, "trans")
    install(trans)
    os.remove(os.path.join(trans, "docs", "dev", "tools", "devflow_atomic.py"))
    rewrite_manifest(trans, drop_destinations=("docs/dev/tools/devflow_atomic.py",))
    rc, out = run_doctor(trans)
    check("✗ ship-deps" in out and "devflow_atomic" in line_with(out, "ship-deps")
          and "diagir.py" in line_with(out, "ship-deps"),
          "doctor:diagir.py import devflow_atomic 但沒散發 → ship-deps ✗ 點名", line_with(out, "ship-deps"))

    # ── ④ ship-deps 判準 ───────────────────────────────────────────────────
    print("-- ④ ship-deps 判準 --")

    def probe(body, name="zz_probe.py", sub=""):
        """在完整採用樹複本加一支散發 .py(列進 manifest),回傳 (doctor 輸出, ship-deps 行)。"""
        d = os.path.join(work, "probe-%d" % probe.n)
        probe.n += 1
        install(d)
        dest = "docs/dev/tools/%s%s" % (sub, name)
        with open(os.path.join(d, *dest.split("/")), "w", encoding="utf-8") as f:
            f.write(body)
        rewrite_manifest(d, extra_rows=[{"source": "scripts/" + sub + name, "destination": dest, "mode": "644"}])
        _, text = run_doctor(d)
        return text, line_with(text, "ship-deps")
    probe.n = 0

    _, ln = probe("try:\n    import no_such_optional_mod\nexcept ImportError:\n    no_such_optional_mod = None\nimport json\n")
    check(ln.startswith("✓ ship-deps"), "try/except ImportError 內的選配 import 不誤報", ln)
    _, ln = probe("def f():\n    import no_such_lazy_mod\n    return no_such_lazy_mod\n")
    check(ln.startswith("✗ ship-deps") and "no_such_lazy_mod" in ln, "函式內的 import 一樣要在散發樹解析得到(缺 → ✗)", ln)
    _, ln = probe("from devflow_jev import state\nimport devflow_jev.policy\nimport diagir\nimport markdown_it\nimport agentmem\n")
    check(ln.startswith("✓ ship-deps"), "散發套件／散發模組／白名單內的第三方(markdown_it、agentmem)不誤報", ln)
    _, ln = probe("from .no_such_sibling import x\n", name="zz_probe.py", sub="devflow_jev/")
    check(ln.startswith("✗ ship-deps") and "no_such_sibling" in ln, "套件內相對 import 缺 sibling → ✗", ln)
    _, ln = probe("from . import state\nfrom .policy import X\n", name="zz_probe.py", sub="devflow_jev/")
    check(ln.startswith("✓ ship-deps"), "套件內相對 import 對得到 sibling → ✓", ln)
    _, ln = probe("import requests\n")
    check(ln.startswith("✗ ship-deps") and "requests" in ln, "沒核准的第三方(ADR 0002:零第三方)→ ✗", ln)

    saved = getattr(sys, "stdlib_module_names", None)
    if saved is not None:
        del sys.stdlib_module_names          # 模擬 3.9 地板(沒有這份名單):走 find_spec 退路
    try:
        check(doctor._is_stdlib("json") and doctor._is_stdlib("os") and doctor._is_stdlib("hashlib"),
              "3.9 退路:標準函式庫(json/os/hashlib)判為 stdlib")
        check(not doctor._is_stdlib("diagir") and not doctor._is_stdlib("devflow_atomic")
              and not doctor._is_stdlib("markdown_it"),
              "3.9 退路:diagir／devflow_atomic／markdown_it 不是 stdlib")
    finally:
        if saved is not None:
            sys.stdlib_module_names = saved

    # ── ⑤ 母版自己 ────────────────────────────────────────────────────────
    print("-- ⑤ 母版散發樹 --")
    rows = load_json(os.path.join(root, "docs", "dev", "ship-manifest.json"))["files"]
    problems = doctor._ship_dep_problems(root, rows)
    check(problems == [], "母版 docs/dev/tools/ 每支已散發 .py 的 import 都在散發樹內", "; ".join(problems[:3]))
    dests = {r["destination"] for r in rows}
    check({"docs/dev/tools/diagir.py", "docs/dev/tools/devflow_atomic.py"} <= dests,
          "manifest 列了 diagir.py 與 devflow_atomic.py")
finally:
    shutil.rmtree(work, ignore_errors=True)

total = passed + failed
if total < MIN_CASES:
    print("FATAL: 案例數 %d 低於下限 %d(案例被刪?)" % (total, MIN_CASES), file=sys.stderr)
    sys.exit(2)
print("=== test-adopter-ship:%d/%d ===" % (passed, total))
sys.exit(1 if failed else 0)
PY
