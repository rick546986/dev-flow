#!/bin/bash
# status-update.sh —— `docs/dev/STATUS.md` 表列(Active / Backlog)的唯一寫入口。
#
# 為什麼要有這支腳本,而不是直接編輯 STATUS.md:
#   同一個 checkout 可能同時有多個 session 在跑。兩邊都「讀整檔 → 改自己那一列
#   → 寫整檔」時,後寫的會把先寫的那一列蓋掉(lost update),而且**不會有任何
#   錯誤訊息** —— 這種丟失只有事後翻 git 才看得出來。v3.8.0 把寫入窗口縮到
#   「只改自己那一列 → 立刻落地 → 立刻推」,那是機率問題,沒消滅同 checkout
#   的靜默互蓋。HISTORY.md 用 history-append.sh 的目錄鎖解同一個問題;
#   STATUS 是改既有的列不是追加,所以鎖必須包住整段 read-modify-write
#   (先取鎖再讀,不是讀完才鎖 —— 讀在鎖外就還是 last-write-wins)。
#
# 兩層防護:
#   ①目錄鎖(`mkdir` 在 POSIX 上是原子操作),取不到就等待重試,預設三次。
#   ②蓋章(`<!-- status-writer-rev:<sha256> -->`):章是 Active+Backlog 表列
#     的指紋,只由本腳本在鎖內重算。手改表列不走本腳本 → 章對不上 →
#     `--verify-stamp` / check-status-policy.sh 紅。這就是「手改可被偵測」。
#
# 母版的表列仍只在整合分支維護:對本 repo 的 `docs/dev/STATUS.md` 做表列
# 變更或 `--refresh-stamp` 時,目前 branch 必須是 `main`。fixture(`--file`
# 指向別處)不查 branch,但 `--refresh-stamp` 仍要表列對得上 `--base-file`。
# `--verify-stamp` / `--check-tables` 不改檔。`--refresh-stamp` 只准在表列
# 已與基準相同時補章(缺章/殘章);不准替手改過的表列補一顆「合法」章。
#
# 用法:
#   scripts/status-update.sh --section active|backlog --match <唯一針> \
#                            --set <欄>=<值> [--set ...] [--file PATH]
#   scripts/status-update.sh --section active|backlog --upsert --row '| … |' \
#                            [--match <針,有則改無則加>] [--file PATH]
#   scripts/status-update.sh --section active|backlog --remove --match <針> \
#                            [--file PATH]
#   scripts/status-update.sh --verify-stamp [--file PATH]
#   scripts/status-update.sh --refresh-stamp [--file PATH] [--base-file PATH]
#   scripts/status-update.sh --check-tables [--file PATH] [--base-file PATH]
#   scripts/status-update.sh --print-overlap-ref --match <針> [--file PATH] \
#                            [--tasks-file PATH]
#   scripts/status-update.sh --print-root
#
#   --file      不給就用 <repo>/docs/dev/STATUS.md
#   --retries   取鎖重試次數,預設 3
#   --dry-run   只印將寫入的列,不動檔、不取鎖
#   --base-file --check-tables / --refresh-stamp 的基準
#               (不給且目標是本 repo 正本 → git show origin/main:docs/dev/STATUS.md;
#                --refresh-stamp 找不到基準就拒,不准無基準蓋章)
#   --print-overlap-ref
#               印出該列「直接補修」用的單一座標 OverlapRef。sequential 時這個
#               座標就是 Branch;parallel 必須已寫入可解析的 OverlapRef(發布的
#               integration/<slug> tip,或合回並 push 後的 Branch)。解不出來就
#               fail-closed,不猜 Lane,也不在 feature tip 與 integration tip
#               之間自行挑選。mode 只讀 5-tasks frontmatter execution.mode。
#   --tasks-file --print-overlap-ref 用來讀 execution.mode 的 5-tasks.md;
#               不給就依 Feature 欄連結推 docs/dev/<slug>/5-tasks.md
#
# exit:
#   0 = 成功
#   1 = 取不到鎖
#   2 = 用法錯誤 / 對不上章 / 表列與基準不同 / 解析不到根且未帶 --file
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(git -C "$SELF_DIR" rev-parse --show-toplevel 2>/dev/null || true)

DATE=""
SECTION="" MATCH="" ROW="" ACTION=""
TARGET="" BASE_FILE="" RETRIES=3 DRY_RUN=0
VERIFY_STAMP=0 REFRESH_STAMP=0 CHECK_TABLES=0
PRINT_OVERLAP_REF=0
TASKS_FILE=""
SETS=()

die() { echo "$1" >&2; exit "${2:-2}"; }

need_value() {
  [ -n "${2:-}" ] || die "拒絕:$1 需要一個值"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --section)    need_value "$1" "${2:-}"; SECTION=$2; shift 2 ;;
    --match)      need_value "$1" "${2:-}"; MATCH=$2; shift 2 ;;
    --row)        need_value "$1" "${2:-}"; ROW=$2; shift 2 ;;
    --set)        need_value "$1" "${2:-}"; SETS+=("$2"); shift 2 ;;
    --file)       need_value "$1" "${2:-}"; TARGET=$2; shift 2 ;;
    --base-file)  need_value "$1" "${2:-}"; BASE_FILE=$2; shift 2 ;;
    --retries)    need_value "$1" "${2:-}"; RETRIES=$2; shift 2 ;;
    --upsert)     ACTION=upsert; shift ;;
    --remove)     ACTION=remove; shift ;;
    --dry-run)    DRY_RUN=1; shift ;;
    --verify-stamp)  VERIFY_STAMP=1; shift ;;
    --refresh-stamp) REFRESH_STAMP=1; shift ;;
    --check-tables)  CHECK_TABLES=1; shift ;;
    --print-overlap-ref) PRINT_OVERLAP_REF=1; shift ;;
    --tasks-file) need_value "$1" "${2:-}"; TASKS_FILE=$2; shift 2 ;;
    --print-root)
      if [ -n "$REPO_ROOT" ]; then printf '%s\n' "$REPO_ROOT"; exit 0
      else echo "(unresolved)"; exit 2; fi ;;
    -h|--help) sed -n '2,52p' "$0"; exit 0 ;;
    *) die "拒絕:未知參數 $1(可用:--section --match --set --row --upsert --remove --file --base-file --retries --dry-run --verify-stamp --refresh-stamp --check-tables --print-overlap-ref --tasks-file --print-root)" ;;
  esac
done

case "$RETRIES" in
  ''|*[!0-9]*) die "拒絕:--retries 需非負整數,得「$RETRIES」" ;;
esac

if [ -z "$TARGET" ]; then
  [ -n "$REPO_ROOT" ] || die "拒絕:解析不到專案根。請明帶 --file <STATUS.md 路徑>"
  TARGET="$REPO_ROOT/docs/dev/STATUS.md"
fi

# 相對路徑依呼叫當下的 cwd 解(測試常從 tmp 指 fixture)
case "$TARGET" in
  /*) ;;
  *) TARGET="$(pwd)/$TARGET" ;;
esac

if [ -n "$BASE_FILE" ]; then
  case "$BASE_FILE" in
    /*) ;;
    *) BASE_FILE="$(pwd)/$BASE_FILE" ;;
  esac
fi

# 唯讀動作不取鎖
if [ "$VERIFY_STAMP" = "1" ]; then
  python3 - "$TARGET" verify <<'PY'
import hashlib, re, sys

path, mode = sys.argv[1], sys.argv[2]
STAMP_RE = re.compile(r"<!-- status-writer-rev:([0-9a-f]{64}) -->")


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def section_body(text, title):
    m = re.search(r"(?m)^## " + re.escape(title) + r"\s*$", text)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"(?m)^## ", rest)
    return rest if n is None else rest[:n.start()]


def table_fingerprint(text):
    chunks = []
    for title in ("Active", "Backlog"):
        body = section_body(text, title)
        lines = [ln.rstrip("\n") for ln in body.splitlines() if ln.startswith("|")]
        chunks.append("\n".join(lines))
    return hashlib.sha256(("\n---\n".join(chunks) + "\n").encode("utf-8")).hexdigest()


try:
    raw = open(path, encoding="utf-8").read()
except OSError as err:
    fail("拒絕:讀不到 %s(%s)" % (path, err))

got = STAMP_RE.search(raw)
if not got:
    fail("拒絕:找不到 status-writer-rev 蓋章(手改或尚未走 status-update.sh)")
want = table_fingerprint(raw)
if got.group(1) != want:
    fail("拒絕:蓋章對不上表列(手改表列、或兩個 session 靜默互蓋後的殘章)")
print("status-writer-rev:" + want)
sys.exit(0)
PY
  exit $?
fi

if [ "$CHECK_TABLES" = "1" ]; then
  python3 - "$TARGET" "$BASE_FILE" "$REPO_ROOT" <<'PY'
import re, subprocess, sys

path, base_file, root = sys.argv[1], sys.argv[2], sys.argv[3]


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def section_rows(text, title):
    m = re.search(r"(?m)^## " + re.escape(title) + r"\s*$", text)
    if not m:
        return []
    rest = text[m.end():]
    n = re.search(r"(?m)^## ", rest)
    body = rest if n is None else rest[:n.start()]
    return [ln.rstrip("\n") for ln in body.splitlines() if ln.startswith("|")]


try:
    raw = open(path, encoding="utf-8").read()
except OSError as err:
    fail("拒絕:讀不到 %s(%s)" % (path, err))

if base_file:
    try:
        base = open(base_file, encoding="utf-8").read()
    except OSError as err:
        fail("拒絕:讀不到基準 %s(%s)" % (base_file, err))
else:
    shown = subprocess.run(
        ["git", "-C", root, "show", "origin/main:docs/dev/STATUS.md"],
        capture_output=True, text=True,
    )
    if shown.returncode != 0:
        shown = subprocess.run(
            ["git", "-C", root, "show", "main:docs/dev/STATUS.md"],
            capture_output=True, text=True,
        )
    if shown.returncode != 0:
        print("status-tables: no-base")
        sys.exit(0)
    base = shown.stdout

for title in ("Active", "Backlog"):
    if section_rows(raw, title) != section_rows(base, title):
        fail("拒絕:%s 表列與整合分支基準不同(feature branch 不准改 Active/Backlog)"
             % title, 2)
print("status-tables: match")
sys.exit(0)
PY
  exit $?
fi

# 唯讀:印出該列直接補修用的單一座標 OverlapRef。不取鎖、不改檔。
if [ "$PRINT_OVERLAP_REF" = "1" ]; then
  [ -n "$MATCH" ] || die "拒絕:--print-overlap-ref 需要 --match"
  if [ -n "$TASKS_FILE" ]; then
    case "$TASKS_FILE" in
      /*) ;;
      *) TASKS_FILE="$(pwd)/$TASKS_FILE" ;;
    esac
  fi
  python3 - "$TARGET" "$MATCH" "$TASKS_FILE" "$REPO_ROOT" <<'PY'
import os, re, sys

path, needle, tasks_file, repo_root = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
SENTINEL = "n-a:尚未建立 branch"


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def section_span(text, title):
    m = re.search(r"(?m)^## " + re.escape(title) + r"\s*$", text)
    if not m:
        return None
    start = m.end()
    n = re.search(r"(?m)^## ", text[start:])
    end = len(text) if n is None else start + n.start()
    return start, end


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_resolved_ref(val):
    v = (val or "").strip()
    return bool(v) and v != SENTINEL


def parse_execution_mode(text):
    """mode 唯一資料源 = 5-tasks frontmatter execution.mode。
    不是 STATUS Lane。整塊缺省 = sequential。解不出來就 None。"""
    if text is None:
        return None
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S | re.M)
    if not m:
        return "sequential"
    fm = m.group(1)
    if not re.search(r"(?m)^execution:\s*(#.*)?$", fm):
        return "sequential"
    mm = re.search(r"(?m)^  mode:\s*(\S+)", fm)
    if not mm:
        return "sequential"
    value = mm.group(1).split("#", 1)[0].strip()
    if value not in ("sequential", "parallel"):
        return None
    return value


def derive_tasks_path(feature_cell):
    m = re.search(r"\]\(\./([^)/]+)/?\)", feature_cell)
    if not m:
        return None
    slug = m.group(1)
    candidates = []
    status_dir = os.path.dirname(path)
    candidates.append(os.path.join(status_dir, slug, "5-tasks.md"))
    if repo_root:
        candidates.append(os.path.join(repo_root, "docs", "dev", slug, "5-tasks.md"))
    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    return None


def resolve_overlap_ref(branch, overlap, mode):
    """直接補修只讀這一個回傳值。
    sequential:座標就是 Branch。
    parallel:必須已寫入可解析的 OverlapRef;解不出來 fail-closed。
    本函式不讀 Lane,也不會從 slug 拼 origin/integration/<slug>。"""
    if is_resolved_ref(overlap):
        return overlap.strip()
    if mode is None:
        fail("拒絕:execution.mode 解不出來,OverlapRef 不准猜")
    if mode == "parallel":
        fail("拒絕:parallel feature 的 OverlapRef 解不出來"
             "(不得猜 Lane,也不得自行挑選 integration/<slug>)")
    if is_resolved_ref(branch):
        return branch.strip()
    fail("拒絕:OverlapRef 解不出來(sequential 的座標就是 Branch,"
         "但 Branch 也不是可解析座標)")


try:
    raw = open(path, encoding="utf-8").read()
except OSError as err:
    fail("拒絕:讀不到 %s(%s)" % (path, err))

span = section_span(raw, "Active")
if span is None:
    fail("拒絕:找不到 ## Active")
start, end = span
lines = [ln for ln in raw[start:end].splitlines() if ln.startswith("|")]
if len(lines) < 2:
    fail("拒絕:## Active 沒有表")
header, data = lines[0], lines[2:]
heads = cells(header)
hits = [ln for ln in data if needle in ln]
if not hits:
    fail("拒絕:Active 找不到含「%s」的列" % needle)
if len(hits) > 1:
    fail("拒絕:Active 「%s」對上 %d 列,fail-closed 不猜" % (needle, len(hits)))
vals = cells(hits[0])
if len(vals) != len(heads):
    fail("拒絕:列欄數 %d ≠ 表頭 %d" % (len(vals), len(heads)))

def cell(name):
    if name not in heads:
        return ""
    return vals[heads.index(name)]

# 刻意不讀 Lane。mode 只來自 5-tasks execution.mode。
lane_unused = cell("Lane")
del lane_unused
branch = cell("Branch")
overlap = cell("OverlapRef")

if is_resolved_ref(overlap):
    print(overlap.strip())
    sys.exit(0)

tasks_path = tasks_file or derive_tasks_path(cell("Feature"))
tasks_text = None
if tasks_path:
    try:
        tasks_text = open(tasks_path, encoding="utf-8").read()
    except OSError as err:
        fail("拒絕:讀不到 5-tasks %s(%s)" % (tasks_path, err))
mode = parse_execution_mode(tasks_text)
print(resolve_overlap_ref(branch, overlap, mode))
sys.exit(0)
PY
  exit $?
fi

MUTATE=0
if [ "$REFRESH_STAMP" = "1" ]; then
  MUTATE=1
  ACTION=refresh-stamp
elif [ -n "$ACTION" ] || [ ${#SETS[@]} -gt 0 ]; then
  MUTATE=1
  if [ -z "$ACTION" ]; then
    ACTION=set
  fi
fi

[ "$MUTATE" = "1" ] || [ "$PRINT_OVERLAP_REF" = "1" ] \
  || die "拒絕:請指定 --set / --upsert / --remove / --verify-stamp / --refresh-stamp / --check-tables / --print-overlap-ref"

if [ "$ACTION" != "refresh-stamp" ]; then
  case "$SECTION" in
    active|backlog) ;;
    *) die "拒絕:--section 必須是 active 或 backlog,得「$SECTION」" ;;
  esac
fi

if [ "$ACTION" = "set" ]; then
  [ -n "$MATCH" ] || die "拒絕:--set 需要 --match( uniquely 指出那一列 )"
  [ ${#SETS[@]} -gt 0 ] || die "拒絕:--set 至少要有一個 欄=值"
fi
if [ "$ACTION" = "remove" ]; then
  [ -n "$MATCH" ] || die "拒絕:--remove 需要 --match"
fi
if [ "$ACTION" = "upsert" ]; then
  [ -n "$ROW" ] || die "拒絕:--upsert 需要 --row"
fi

# 對本 repo 正本做表列變更或補章 → 必須在 main。
# --refresh-stamp 也查:否則 feature branch 手改表列再補章,verify 會假綠。
if [ -n "$REPO_ROOT" ]; then
  REAL="$REPO_ROOT/docs/dev/STATUS.md"
  if [ "$TARGET" = "$REAL" ]; then
    BRANCH=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
    if [ "$BRANCH" != "main" ]; then
      die "拒絕:docs/dev/STATUS.md 表列與 --refresh-stamp 只能在整合分支 main 上改(現在是 $BRANCH)。feature branch 不准改 Active/Backlog,也不准替手改表列補章。"
    fi
  fi
fi

if [ "$DRY_RUN" = "1" ]; then
  python3 - "$TARGET" "$ACTION" "$SECTION" "$MATCH" "$ROW" "${SETS[@]+"${SETS[@]}"}" <<'PY'
import sys
print("dry-run: action=%s section=%s match=%s row=%s sets=%s file=%s"
      % (sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
         sys.argv[6:], sys.argv[1]))
sys.exit(0)
PY
  exit $?
fi

TARGET_DIR=$(dirname "$TARGET")
[ -d "$TARGET_DIR" ] || die "拒絕:目錄不存在 $TARGET_DIR"

# ── 取鎖(mkdir 原子;與 history-append.sh 同一套)──
LOCK="$TARGET.lock"

try_lock_within() {
  local loops=$(( ${1} * 10 ))
  local i=0
  while [ "$i" -lt "$loops" ]; do
    if mkdir "$LOCK" 2>/dev/null; then
      return 0
    fi
    sleep 0.1
    i=$((i + 1))
  done
  return 1
}

got_lock=0
if mkdir "$LOCK" 2>/dev/null; then
  got_lock=1
else
  attempt=1
  while [ "$attempt" -le "$RETRIES" ]; do
    echo "⏳ 有別的 session 正在寫 $(basename "$TARGET"),等待後重試(第 $attempt/$RETRIES 次)" >&2
    if try_lock_within "$attempt"; then
      got_lock=1
      break
    fi
    attempt=$((attempt + 1))
  done
fi

if [ "$got_lock" != "1" ]; then
  echo "⛔ 取不到寫入鎖(已重試 $RETRIES 次):$LOCK" >&2
  echo "   若確定沒有其他 session 在寫,手動移除該目錄後重跑:" >&2
  echo "   rmdir '$LOCK'" >&2
  exit 1
fi

cleanup() { rmdir "$LOCK" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

# 鎖內才讀、改、寫、蓋章 —— 讀在鎖外就是 last-write-wins
# --refresh-stamp 的基準走環境變數(不是跳過開關;沒基準就拒)
DEVFLOW_STATUS_BASE_FILE="$BASE_FILE" \
DEVFLOW_STATUS_REPO_ROOT="$REPO_ROOT" \
python3 - "$TARGET" "$ACTION" "$SECTION" "$MATCH" "$ROW" "${SETS[@]+"${SETS[@]}"}" <<'PY'
import hashlib
import os
import re
import sys
import tempfile

path = sys.argv[1]
action = sys.argv[2]
section = sys.argv[3]
match = sys.argv[4]
row_arg = sys.argv[5]
sets = sys.argv[6:]

STAMP_RE = re.compile(r"<!-- status-writer-rev:[0-9a-f]{64} -->")
EMPTY_ACTIVE = "目前無進行中的改版軌。"
ACTIVE_HEADER = (
    "| Feature | Lane | Stage | Owner | Branch | OverlapRef | Gates | Updated |\n"
    "|---|---|---|---|---|---|---|---|"
)
BACKLOG_HEADER = "| 級 | 一句 | 來源 |\n|---|---|---|"


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def section_span(text, title):
    m = re.search(r"(?m)^## " + re.escape(title) + r"\s*$", text)
    if not m:
        return None
    start = m.end()
    n = re.search(r"(?m)^## ", text[start:])
    end = len(text) if n is None else start + n.start()
    return m.start(), start, end


def pipe_lines(body):
    return [ln for ln in body.splitlines() if ln.startswith("|")]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_fingerprint(text):
    chunks = []
    for title in ("Active", "Backlog"):
        span = section_span(text, title)
        if span is None:
            chunks.append("")
            continue
        _, start, end = span
        lines = [ln.rstrip("\n") for ln in text[start:end].splitlines() if ln.startswith("|")]
        chunks.append("\n".join(lines))
    return hashlib.sha256(("\n---\n".join(chunks) + "\n").encode("utf-8")).hexdigest()


def apply_stamp(text):
    stamp = "<!-- status-writer-rev:%s -->" % table_fingerprint(text)
    if STAMP_RE.search(text):
        return STAMP_RE.sub(stamp, text, count=1)
    m = re.search(r"(?m)^## ", text)
    insert = stamp + "\n\n"
    if m is None:
        if text and not text.endswith("\n"):
            text += "\n"
        return text + insert
    return text[:m.start()] + insert + text[m.start():]


def parse_sets(items):
    out = []
    for item in items:
        if "=" not in item:
            fail("拒絕:--set 要 欄=值,得「%s」" % item)
        name, value = item.split("=", 1)
        name = name.strip()
        if not name:
            fail("拒絕:--set 欄名是空的")
        out.append((name, value))
    return out


def find_data_rows(lines):
    if len(lines) < 2:
        return [], None, None
    header, sep, data = lines[0], lines[1], lines[2:]
    return data, header, sep


def replace_section_body(text, title, new_body):
    span = section_span(text, title)
    if span is None:
        fail("拒絕:找不到 ## %s" % title)
    head_start, start, end = span
    heading = text[head_start:start]
    # 保留 heading 行後的單一換行;new_body 自己帶結尾換行
    prefix = text[:start]
    suffix = text[end:]
    body = new_body
    if body and not body.endswith("\n"):
        body += "\n"
    if suffix and not body.endswith("\n\n") and not suffix.startswith("\n"):
        body += "\n"
    return prefix + body + suffix


def ensure_table(body, title):
    lines = pipe_lines(body)
    if lines:
        return body, lines
    if title == "Active":
        # 空看板散文 → 建表
        return "\n" + ACTIVE_HEADER + "\n", ACTIVE_HEADER.splitlines()
    return "\n" + BACKLOG_HEADER + "\n", BACKLOG_HEADER.splitlines()


def unique_row(data, needle, where):
    hits = [i for i, ln in enumerate(data) if needle in ln]
    if not hits:
        fail("拒絕:%s 找不到含「%s」的列" % (where, needle))
    if len(hits) > 1:
        fail("拒絕:%s 「%s」對上 %d 列,fail-closed 不猜" % (where, needle, len(hits)))
    return hits[0]


def set_cell(line, header, name, value):
    heads = cells(header)
    if name not in heads:
        fail("拒絕:表頭沒有欄「%s」(實得 %s)" % (name, heads))
    vals = cells(line)
    if len(vals) != len(heads):
        fail("拒絕:列欄數 %d ≠ 表頭 %d" % (len(vals), len(heads)))
    vals[heads.index(name)] = value
    return "| " + " | ".join(vals) + " |"


def empty_active_body():
    return "\n" + EMPTY_ACTIVE + "\n"


try:
    raw = open(path, encoding="utf-8").read()
except OSError as err:
    fail("拒絕:讀不到 %s(%s)" % (path, err))

if action == "refresh-stamp":
    # refresh-stamp 需要基準:表列必須已與基準相同,才准補章。
    # 沒有基準不准蓋章 —— 否則手改表列再 --refresh-stamp 會把假座標變成合法章。
    def section_rows(text, title):
        sp = section_span(text, title)
        if sp is None:
            return []
        _, st, en = sp
        return [ln.rstrip("\n") for ln in text[st:en].splitlines() if ln.startswith("|")]

    def load_baseline():
        base_path = os.environ.get("DEVFLOW_STATUS_BASE_FILE") or ""
        root = os.environ.get("DEVFLOW_STATUS_REPO_ROOT") or ""
        if base_path:
            try:
                return open(base_path, encoding="utf-8").read()
            except OSError as err:
                fail("拒絕:讀不到基準 %s(%s)" % (base_path, err))
        if root:
            import subprocess
            shown = subprocess.run(
                ["git", "-C", root, "show", "origin/main:docs/dev/STATUS.md"],
                capture_output=True, text=True,
            )
            if shown.returncode != 0:
                shown = subprocess.run(
                    ["git", "-C", root, "show", "main:docs/dev/STATUS.md"],
                    capture_output=True, text=True,
                )
            if shown.returncode == 0:
                return shown.stdout
        fail("拒絕:--refresh-stamp 需要基準(--base-file 或本 repo 正本的 origin/main)。沒有基準不准蓋章")

    base_text = load_baseline()
    for title in ("Active", "Backlog"):
        if section_rows(raw, title) != section_rows(base_text, title):
            fail("拒絕:--refresh-stamp 表列與基準不同,不准替手改表列補章(%s)" % title)
    new = apply_stamp(raw)
    # 原子寫
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix="status-update-", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(new)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print("✅ 已蓋章 %s" % path)
    print("status-writer-rev:" + table_fingerprint(new))
    sys.exit(0)

title = "Active" if section == "active" else "Backlog"
span = section_span(raw, title)
if span is None:
    fail("拒絕:找不到 ## %s" % title)
_, start, end = span
body = raw[start:end]
body, lines = ensure_table(body, title)
data, header, sep = find_data_rows(lines)
if header is None:
    fail("拒絕:## %s 沒有表" % title)

if action == "set":
    idx = unique_row(data, match, title)
    line = data[idx]
    for name, value in parse_sets(sets):
        line = set_cell(line, header, name, value)
    data[idx] = line
    result_line = line
elif action == "remove":
    idx = unique_row(data, match, title)
    result_line = data[idx]
    del data[idx]
elif action == "upsert":
    row = row_arg.strip()
    if not row.startswith("|"):
        row = "| " + row
    if not row.endswith("|"):
        row = row + " |"
    if match:
        hits = [i for i, ln in enumerate(data) if match in ln]
        if len(hits) > 1:
            fail("拒絕:--match 「%s」對上 %d 列,fail-closed 不猜" % (match, len(hits)))
        if hits:
            data[hits[0]] = row
        else:
            data.append(row)
    else:
        data.append(row)
    result_line = row
else:
    fail("拒絕:未知 action %s" % action)

if section == "active" and not data:
    new_body = empty_active_body()
else:
    new_body = "\n" + "\n".join([header, sep] + data) + "\n"

# ensure_table 可能把 body 換成標準表,但 raw 裡還是舊散文 —— 用 replace_section_body
new = replace_section_body(raw, title, new_body)
new = apply_stamp(new)

d = os.path.dirname(path) or "."
fd, tmp = tempfile.mkstemp(prefix="status-update-", dir=d)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(new)
    os.replace(tmp, path)
except Exception:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise

print("✅ 已更新 %s 的 %s" % (path, title))
print(result_line)
print("status-writer-rev:" + table_fingerprint(new))
sys.exit(0)
PY
