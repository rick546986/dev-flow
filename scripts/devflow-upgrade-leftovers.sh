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
# ①的檔案真刪前另跟 baseline 做雜湊比對(不改①②列候選的規格,只改刪除動作):
# 內容與 baseline 相同才直刪;不同(使用者客製過)或 baseline 沒有對應檔可比
# (無法比對)就搬到 docs/dev/.devflow-upgrade-trash/<時間戳記>/ 並印 diff 摘要,
# 不無備份直刪。落點撞名(同一秒內第二次 --apply 同一相對路徑)絕不靜默覆蓋前一
# 份,自動加 .1 .2 … 唯一化後綴,stdout 印實際落點。
#
# 測試專用環境變數 DEVFLOW_UPGRADE_LEFTOVERS_STAMP:覆寫 trash 子目錄的時間戳記,
# 只給治具決定性重現撞名;正常使用不要設它,設了會改變 trash 落點。
#
# 用法:
#   scripts/devflow-upgrade-leftovers.sh --root <專案根> --pack <方法包根> [--apply]
# exit:0 = 乾淨或已刪(含搬 trash)/ 1 = 真刪或搬移失敗 / 2 = 用法或邊界違規
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
    -h|--help) sed -n '2,33p' "$0"; exit 0 ;;
    *) die "拒絕:未知參數 $1(可用:--root --pack --apply)" ;;
  esac
done

[ -n "$ROOT" ] || die "拒絕:缺 --root(採用專案根)"
[ -n "$PACK" ] || die "拒絕:缺 --pack(方法包根,用來對目前出貨清單)"
ROOT=$(cd "$ROOT" && pwd) || die "拒絕:--root 不是目錄"
PACK=$(cd "$PACK" && pwd) || die "拒絕:--pack 不是目錄"

python3 - "$ROOT" "$PACK" "$APPLY" <<'PY'
import datetime
import difflib
import hashlib
import os
import shutil
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
TRASH_ROOT = os.path.join(root, "docs", "dev", ".devflow-upgrade-trash")
# 測試專用覆寫:讓治具能強迫兩次 --apply 落在同一個 stamp 目錄,決定性地
# 觸發撞名分支,不必賭兩次呼叫剛好落在同一秒內。正常執行不設這個環境變數,
# 行為不變(仍取當下時間)。
STAMP_OVERRIDE = os.environ.get("DEVFLOW_UPGRADE_LEFTOVERS_STAMP", "")


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


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_dest(dest):
    # dest 若已存在(同一秒內第二次 --apply 同一相對路徑撞名),絕不能靜默覆蓋
    # 前一次搬進 trash 的檔——遞增 .1 .2 ... 直到找到空位。
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(dest)
    n = 1
    while True:
        candidate = "%s.%d%s" % (base, n, ext)
        if not os.path.exists(candidate):
            return candidate
        n += 1


def rel_within_managed(path):
    # 這個候選路徑相對它所在的受管目錄(MANAGED_REL 其中之一)的相對路徑,
    # 用來在 baseline 側找對應檔——同一相對路徑,不管候選是落在
    # docs/dev/_templates/ 還是 docs/dev/.devflow-baseline/_templates/。
    for rel in MANAGED_REL:
        base = os.path.join(root, rel)
        if is_under(path, base):
            return os.path.relpath(real(path), real(base))
    return None


def diff_summary(baseline_path, live_path, limit=10):
    def read_lines(p):
        try:
            with open(p, encoding="utf-8", errors="strict") as fh:
                return fh.readlines()
        except (UnicodeDecodeError, OSError):
            return None

    old = read_lines(baseline_path)
    new = read_lines(live_path)
    if old is None or new is None:
        return ["    (二進位或非文字內容,略過逐行 diff)"]
    lines = list(
        difflib.unified_diff(old, new, fromfile="baseline", tofile="現況", lineterm="")
    )
    if not lines:
        return ["    (雜湊不同但逐行 diff 無輸出,可能是行尾符差異)"]
    out = ["    " + line.rstrip("\n") for line in lines[:limit]]
    if len(lines) > limit:
        out.append("    ...(還有 %d 行差異未顯示)" % (len(lines) - limit))
    return out


protected_real = {real(p) for p in PROTECTED}
pack_templates = os.path.join(pack, "_templates")
if not os.path.isdir(pack_templates):
    fail("拒絕:方法包沒有 _templates/(--pack 不是方法包根)")

pack_set = list_files(pack_templates)
baseline_templates = os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates")
have_baseline = os.path.isdir(baseline_templates)

# ①已知退役模板名——這批候選在 --apply 真刪前要跟 baseline 做雜湊比對
# (見下方 apply 段),路徑差集列候選的規格不變。
known_retired_candidates = []
for name in KNOWN_RETIRED:
    if name in pack_set:
        continue
    for rel in MANAGED_REL:
        path = os.path.join(root, rel, name)
        if os.path.isfile(path):
            known_retired_candidates.append(path)

candidates = list(known_retired_candidates)

# ②有 baseline 時:舊 baseline 有、新 pack 沒有的檔——候選列法不變。
if have_baseline:
    for rel in list_files(baseline_templates) - pack_set:
        for base in (
            os.path.join(root, "docs", "dev", "_templates"),
            baseline_templates,
        ):
            path = os.path.join(base, rel)
            if os.path.isfile(path):
                candidates.append(path)

known_retired_real = {real(p) for p in known_retired_candidates}

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
deleted = 0
trashed = []  # [(原路徑, trash 內路徑, diff 摘要行清單), ...]
stamp = None

for path in allowed:
    key = real(path)
    if key in known_retired_real:
        # KNOWN_RETIRED 分支:真刪前跟 baseline 做雜湊比對,內容相同才直刪;
        # 不同(客製過)或 baseline 無對應檔(無法比對)一律搬 trash,不無備份直刪。
        rel = rel_within_managed(path)
        baseline_ref = os.path.join(baseline_templates, rel) if rel is not None else None
        if baseline_ref is not None and real(baseline_ref) == key:
            same = True  # 候選本身就是 baseline 複本,對自己比對必然相同
        elif baseline_ref is not None and os.path.isfile(baseline_ref):
            try:
                same = sha256_of(path) == sha256_of(baseline_ref)
            except OSError as err:
                failed.append("%s (讀取失敗,無法比對:%s)" % (path, err))
                continue
        else:
            same = False  # baseline 沒有對應檔可比——無法比對,當作客製處理

        if not same:
            if stamp is None:
                stamp = STAMP_OVERRIDE or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            rel_root = os.path.relpath(path, root)
            dest = os.path.join(TRASH_ROOT, stamp, rel_root)
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                dest = unique_dest(dest)  # 撞名絕不覆蓋,遞增 .1 .2 找空位
                shutil.move(path, dest)
            except OSError as err:
                failed.append("%s (搬移失敗:%s)" % (path, err))
                continue
            # diff 摘要就地算好存文字——不能留到迴圈跑完再算,同一批候選裡
            # baseline 複本本身也可能在後續疊代被直刪,屆時 baseline_ref 已不在。
            if baseline_ref and os.path.isfile(baseline_ref):
                summary_lines = diff_summary(baseline_ref, dest)
            else:
                summary_lines = ["    (baseline 沒有對應檔,無法比對,一律搬移)"]
            trashed.append((path, dest, summary_lines))
            continue

    try:
        os.remove(path)
        deleted += 1
    except OSError as err:
        failed.append("%s (%s)" % (path, err))

if failed:
    print("⛔ 刪不掉:\n  " + "\n  ".join(failed), file=sys.stderr)
    sys.exit(1)

if trashed:
    print("客製過的退役檔(內容跟 baseline 不同,已搬離不直刪):")
    for orig, dest, summary_lines in trashed:
        print(
            "  "
            + os.path.relpath(orig, root)
            + " -> "
            + os.path.relpath(dest, root)
        )
        for line in summary_lines:
            print(line)
    print(
        "已搬移 %d 個客製過的退役檔到 %s,請自行檢視後刪除"
        % (len(trashed), os.path.relpath(os.path.join(TRASH_ROOT, stamp), root))
    )

print("deleted: %d" % deleted)
sys.exit(0)
PY
