#!/bin/bash
# devflow-upgrade-leftovers.sh — 刪掉目前 pack 不再出貨的受管殘件
#
# 為什麼需要:agent-memory-v3 把 _templates/CONTEXT.md 移出方法包,但 upgrade
# 只覆蓋受管檔、從不刪 pack 已停出的檔。採用樹因此留下
# docs/dev/_templates/CONTEXT.md(有時還有 .devflow-baseline/_templates/CONTEXT.md)。
# 這支腳本是 upgrade 的殘件刪除入口,不是「掃到不在 pack 的就全刪」。
#
# 准刪:
#   ①已知退役模板名(目前只有 CONTEXT.md)且路徑落在
#     docs/dev/_templates/ 或 docs/dev/.devflow-baseline/_templates/
#   ②有 baseline 時:舊 baseline/_templates/ 有、目前 pack/_templates/ 沒有的檔
#     (含採用樹 _templates/ 上同一相對路徑)
# 不准刪:
#   專案根 CONTEXT.md
#   採用專案正在用的 docs/dev/CONTEXT.md
#   上述兩個受管目錄以外的任何路徑
#
# 沒 baseline 時只走①。先列殘件再換 baseline,否則退役檔會被看成「本地客製」。
# 預設 dry-run;upgrade 帶 --apply 才真刪。
#
# 用法:
#   scripts/devflow-upgrade-leftovers.sh --root <專案根> --pack <方法包根> [--apply]
# exit:0 = 乾淨或已刪 / 1 = 真刪失敗 / 2 = 用法或邊界違規
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
APPLY=0
ROOT=""
PACK=""

die() { echo "$1" >&2; exit "${2:-2}"; }

need_value() {
  [ -n "${2:-}" ] || die "拒絕:$1 需要一個值"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --root)  need_value "$1" "${2:-}"; ROOT=$2; shift 2 ;;
    --pack)  need_value "$1" "${2:-}"; PACK=$2; shift 2 ;;
    --apply) APPLY=1; shift ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) die "拒絕:未知參數 $1(可用:--root --pack --apply)" ;;
  esac
done

[ -n "$ROOT" ] || die "拒絕:缺 --root(採用專案根)"
[ -n "$PACK" ] || die "拒絕:缺 --pack(方法包根,用來對目前出貨清單)"
ROOT=$(cd "$ROOT" && pwd) || die "拒絕:--root 不是目錄"
PACK=$(cd "$PACK" && pwd) || die "拒絕:--pack 不是目錄"

python3 - "$ROOT" "$PACK" "$APPLY" <<'PY'
import os
import sys

root, pack, apply = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
KNOWN_RETIRED = ("CONTEXT.md",)
MANAGED_REL = (
    os.path.join("docs", "dev", "_templates"),
    os.path.join("docs", "dev", ".devflow-baseline", "_templates"),
)
PROTECTED = (
    os.path.join(root, "CONTEXT.md"),
    os.path.join(root, "docs", "dev", "CONTEXT.md"),
)


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def real(path):
    return os.path.realpath(path)


def is_under(path, parent):
    path_r = real(path)
    parent_r = real(parent)
    return path_r == parent_r or path_r.startswith(parent_r + os.sep)


def list_files(base):
    out = set()
    if not os.path.isdir(base):
        return out
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            full = os.path.join(dirpath, name)
            out.add(os.path.relpath(full, base))
    return out


def managed_ok(path):
    return any(is_under(path, os.path.join(root, rel)) for rel in MANAGED_REL)


protected_real = {real(p) for p in PROTECTED}
pack_templates = os.path.join(pack, "_templates")
if not os.path.isdir(pack_templates):
    fail("拒絕:方法包沒有 _templates/(--pack 不是方法包根)")

pack_set = list_files(pack_templates)
baseline_templates = os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates")
have_baseline = os.path.isdir(baseline_templates)
candidates = []

for name in KNOWN_RETIRED:
    if name in pack_set:
        continue
    for rel in MANAGED_REL:
        path = os.path.join(root, rel, name)
        if os.path.isfile(path):
            candidates.append(path)

if have_baseline:
    for rel in list_files(baseline_templates) - pack_set:
        for base in (
            os.path.join(root, "docs", "dev", "_templates"),
            baseline_templates,
        ):
            path = os.path.join(base, rel)
            if os.path.isfile(path):
                candidates.append(path)

# 去重且穩定排序
seen = set()
unique = []
for path in candidates:
    key = real(path)
    if key in seen:
        continue
    seen.add(key)
    unique.append(path)

blocked = []
allowed = []
for path in unique:
    key = real(path)
    if key in protected_real or not managed_ok(path):
        blocked.append(path)
    else:
        allowed.append(path)

if blocked:
    fail(
        "拒絕:殘件清單碰到受保護路徑,fail-closed 不刪:\n  "
        + "\n  ".join(blocked)
    )

if not allowed:
    print("leftover: none")
    sys.exit(0)

print("leftover:")
for path in allowed:
    print("  " + os.path.relpath(path, root))

if not apply:
    print("dry-run: 帶 --apply 才刪")
    sys.exit(0)

failed = []
for path in allowed:
    try:
        os.remove(path)
    except OSError as err:
        failed.append("%s (%s)" % (path, err))
if failed:
    print("⛔ 刪不掉:\n  " + "\n  ".join(failed), file=sys.stderr)
    sys.exit(1)
print("deleted: %d" % len(allowed))
sys.exit(0)
PY
