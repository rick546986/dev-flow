#!/bin/bash
# check-ship-manifest.sh — 散發清單正本的牙齒(Repo-local)。
#
# 正本 docs/dev/ship-manifest.json。本守衛釘四件事:
#   ①結構 fail-closed:缺欄 / 重複 destination / mode 不是 644|755
#   ②parity:expected set 取自正本 tools 列(不掃 docs/dev/tools/)
#     存在性 + 內容 + 清單 mode + 正副本可執行位元,雙向
#   ③檔案地圖「散發面」標註與正本 tools 列同一集合(地圖不是正本,漏記會紅)
#   ④負向 fixture:漏記、正副本同刪、mode 不一致、結構壞掉都必須紅
#
# contract 列在正本,但 destination 不住 tools/;獨立比對不得刪。
#
# 掛載:scripts/devflow-check.sh group_architecture()(必須在 py-floor 之前)。
#
# 用法:scripts/check-ship-manifest.sh [root]
# exit:0 = 全過 / 1 = 任一條不對 / 2 = 環境或用法錯
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  case "$1" in
    -h|--help|help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ROOT=$(cd "$1" 2>/dev/null && pwd) || { echo "找不到 root: $1" >&2; exit 2; } ;;
  esac
fi

command -v python3 >/dev/null 2>&1 || { echo "FATAL: 缺 python3" >&2; exit 2; }
[ -f "$SELF_DIR/devflow_ship_manifest.py" ] || {
  echo "FATAL: 找不到 scripts/devflow_ship_manifest.py" >&2; exit 2; }

python3 - "$ROOT" "$SELF_DIR" <<'PY'
import os
import shutil
import sys
import tempfile

root = sys.argv[1]
sys.path.insert(0, sys.argv[2])
from devflow_ship_manifest import (
    CONTRACT_DEST,
    CONTRACT_SOURCE,
    SCHEMA,
    filemap_sync_failures,
    load,
    load_raw,
    ManifestError,
    parity_failures,
    rows,
    schema_problems,
    tools_rows,
)

FAILED = 0
CHECKS = 0


def check(cond, label, detail=""):
    global FAILED, CHECKS
    CHECKS += 1
    if cond:
        print("  ✓ %s" % label)
    else:
        FAILED += 1
        extra = (" — %s" % detail) if detail else ""
        print("  ✗ %s%s" % (label, extra))


print("-- 正本結構 --")
try:
    data = load(root)
    raw_ok = True
    load_err = ""
except ManifestError as exc:
    data = None
    raw_ok = False
    load_err = "; ".join(exc.problems)
check(raw_ok, "docs/dev/ship-manifest.json 結構合法", load_err)

if data is None:
    try:
        data = load_raw(root)
    except ManifestError:
        data = {"schema": SCHEMA, "files": []}

if data is not None:
    files = rows(data) if "files" in data and isinstance(data.get("files"), list) else []
    contract = [r for r in files
                if r.get("source") == CONTRACT_SOURCE
                and r.get("destination") == CONTRACT_DEST]
    check(len(contract) == 1,
          "contract 列在正本且 destination 是 docs/dev/devflow-contract.json",
          "誤塞進 tools/ 或漏記會讓獨立比對被抄掉")
    tools = tools_rows(data) if raw_ok else []
    check(len(tools) >= 1, "正本至少一列 destination 落在 docs/dev/tools/",
          "tools 列被刪光 = expected set 空")

print("-- 正本/散發副本 parity(expected set 取自 ship-manifest,不掃 tools/)--")
real_fails = parity_failures(root, data if raw_ok else None)
check(not real_fails,
      "parity 全過(存在性+內容+清單 mode+可執行位元,雙向)",
      "; ".join(real_fails))

print("-- 檔案地圖散發面 ↔ 正本 tools 列 --")
map_fails = filemap_sync_failures(root, data if raw_ok else None)
check(not map_fails,
      "檔案地圖散發面與正本 tools 列同一集合",
      "; ".join(map_fails))

print("-- 結構負向(缺欄/重複 destination/非法 mode)--")


def fixture_schema(payload, needle, label):
    problems = schema_problems(payload)
    hit = any(needle in p for p in problems)
    check(hit, label, "實得 %s" % problems)


good_row = {
    "source": "scripts/a.sh",
    "destination": "docs/dev/tools/a.sh",
    "mode": "755",
}
fixture_schema(
    {"schema": SCHEMA, "files": [
        {"destination": "docs/dev/tools/a.sh", "mode": "755"}
    ]},
    "缺欄 source",
    "結構負向:缺 source → 紅",
)
fixture_schema(
    {"schema": SCHEMA, "files": [
        {"source": "scripts/a.sh", "mode": "755"}
    ]},
    "缺欄 destination",
    "結構負向:缺 destination → 紅",
)
fixture_schema(
    {"schema": SCHEMA, "files": [
        {"source": "scripts/a.sh", "destination": "docs/dev/tools/a.sh"}
    ]},
    "缺欄 mode",
    "結構負向:缺 mode → 紅",
)
fixture_schema(
    {"schema": SCHEMA, "files": [
        dict(good_row),
        {"source": "scripts/b.sh",
         "destination": "docs/dev/tools/a.sh",
         "mode": "644"},
    ]},
    "destination 重複",
    "結構負向:重複 destination → 紅",
)
fixture_schema(
    {"schema": SCHEMA, "files": [
        {"source": "scripts/a.sh",
         "destination": "docs/dev/tools/a.sh",
         "mode": "777"},
    ]},
    "不是合法值",
    "結構負向:mode 不是 644|755 → 紅",
)
fixture_schema(
    {"schema": SCHEMA, "files": []},
    "空陣列",
    "結構負向:files 空 → 紅(expected set 空不准綠)",
)

print("-- parity 負向 fixture --")
fixture = tempfile.mkdtemp(prefix="shipparity.")
try:
    os.makedirs(os.path.join(fixture, "guides"))
    os.makedirs(os.path.join(fixture, "scripts"))
    os.makedirs(os.path.join(fixture, "docs", "dev", "tools"))
    man = {
        "schema": SCHEMA,
        "files": [
            {"source": "scripts/tool-x.sh",
             "destination": "docs/dev/tools/tool-x.sh",
             "mode": "755"},
            {"source": "scripts/tool-y.sh",
             "destination": "docs/dev/tools/tool-y.sh",
             "mode": "755"},
            {"source": CONTRACT_SOURCE,
             "destination": CONTRACT_DEST,
             "mode": "644"},
        ],
    }
    import json
    os.makedirs(os.path.join(fixture, "docs", "dev"), exist_ok=True)
    with open(os.path.join(fixture, "docs", "dev", "ship-manifest.json"), "w") as fh:
        json.dump(man, fh)
    rows_html = "".join(
        "<tr><td><code>%s</code></td><td>x</td>"
        "<td>(散發面:<code>docs/dev/tools/</code>)</td></tr>" % n
        for n in ("tool-x.sh", "tool-y.sh"))
    with open(os.path.join(fixture, "guides", "guide-dev-flow.html"), "w") as fh:
        fh.write("<h2 id=\"filemap\">map</h2><table>%s</table>" % rows_html)
    for name in ("tool-x.sh", "tool-y.sh"):
        for rel in (os.path.join("scripts", name),
                    os.path.join("docs", "dev", "tools", name)):
            path = os.path.join(fixture, rel)
            with open(path, "w") as fh:
                fh.write("#!/bin/bash\n")
            os.chmod(path, 0o755)
    with open(os.path.join(fixture, CONTRACT_SOURCE), "w") as fh:
        fh.write("{}\n")
    os.makedirs(os.path.join(fixture, "docs", "dev"), exist_ok=True)
    with open(os.path.join(fixture, CONTRACT_DEST), "w") as fh:
        fh.write("{}\n")
    os.chmod(os.path.join(fixture, CONTRACT_SOURCE), 0o644)
    os.chmod(os.path.join(fixture, CONTRACT_DEST), 0o644)

    check(not parity_failures(fixture),
          "parity 負向 fixture 基線:兩工具齊全 → 綠")
    os.unlink(os.path.join(fixture, "scripts", "tool-y.sh"))
    os.unlink(os.path.join(fixture, "docs", "dev", "tools", "tool-y.sh"))
    gone = parity_failures(fixture)
    check(any("tool-y.sh" in f or "tool-y.sh" in f.replace("\\", "/") for f in gone),
          "parity 負向:正副本同時刪、正本列仍在 → 紅(不是掃目錄式的靜默縮水)",
          "實得 %s" % gone)

    os.chmod(os.path.join(fixture, "scripts", "tool-x.sh"), 0o644)
    mode_fails = parity_failures(fixture)
    check(any("mode" in f or "可執行位元" in f for f in mode_fails),
          "parity 負向:正本 mode 與清單 755 不一致 → 紅",
          "實得 %s" % mode_fails)
    os.chmod(os.path.join(fixture, "scripts", "tool-x.sh"), 0o755)

    with open(os.path.join(fixture, "guides", "guide-dev-flow.html"), "w") as fh:
        fh.write(
            "<h2 id=\"filemap\">map</h2><table>"
            "<tr><td><code>tool-x.sh</code></td><td>x</td>"
            "<td>(散發面:<code>docs/dev/tools/</code>)</td></tr>"
            "</table>")
    map_miss = filemap_sync_failures(fixture)
    check(any("tool-y.sh" in f for f in map_miss),
          "檔案地圖負向:正本有 tool-y、地圖沒散發面 → 紅",
          "實得 %s" % map_miss)
finally:
    shutil.rmtree(fixture, ignore_errors=True)

# ── 檢查數地板 ──────────────────────────────────────────────────────────
MIN_CHECKS = 15
if CHECKS < MIN_CHECKS:
    FAILED += 1
    print("  ✗ 檢查數地板:實際只跑了 %s 項(地板 %s)" % (CHECKS, MIN_CHECKS))

print()
if FAILED:
    print("⛔ 散發清單正本守衛:%s/%s 失敗" % (FAILED, CHECKS))
    sys.exit(1)
print("✅ 散發清單正本守衛:全過(%s 項)" % CHECKS)
PY
