#!/bin/bash
# history-append.sh —— 往 `docs/dev/HISTORY.md` 追加一筆改版紀錄(唯一寫入口)。
#
# 為什麼要有這支腳本,而不是直接編輯 HISTORY.md:
#   同一個專案可能同時有多個 session 在跑(例:一個在做 feature A、一個在收尾 B)。
#   兩邊都「讀整檔 → 改 → 寫整檔」時,後寫的會把先寫的整段蓋掉(lost update),
#   而且**不會有任何錯誤訊息** —— 這種丟失只有事後翻 git 才看得出來。
#   本腳本用兩層防護:
#     ①目錄鎖(`mkdir` 在 POSIX 上是原子操作,Linux/macOS/Windows-gitbash 都成立),
#       取不到鎖就等待重試,預設三次;三次都拿不到才放棄並回報。
#     ②追加寫入(`>>`),不重寫既有內容 —— 就算鎖失效也只會多一筆,不會少一筆。
#
# 為什麼最新的在最下面:`>>` 只能往檔尾追加,那是唯一不需要重寫全檔的寫法;
#   要「最新在最上面」就得整檔重寫,那正是 lost update 的來源。
#   本專案的教訓帳(`~/.claude/doctrine/06-lessons.md`)也是同一個方向。
#
# 用法:
#   scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> \
#                             --where <落在哪> [--date YYYY-MM-DD] [--version vX.Y.Z] \
#                             [--adr NNNN[,NNNN]] [--detail <連結或檔案路徑>] \
#                             [--file <HISTORY.md 路徑>] [--retries N] [--dry-run]
#
#   --date    不給就用今天(本機時區)。
#   --file    不給就用 `<repo root>/docs/dev/HISTORY.md`;檔案不存在會先建出檔頭。
#   --dry-run 只把要追加的內容印到 stdout,不動檔案、不取鎖。
#
# exit code:
#   0 = 已追加(或 --dry-run 成功產出)
#   1 = 取不到鎖(有別的 session 正在寫,已重試指定次數)
#   2 = 用法錯誤 / 缺必填欄位 / 目標路徑不可寫
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SELF_DIR/.." && pwd)

DATE="" SLUG="" WHAT="" WHY="" WHERE="" VERSION="" ADR="" DETAIL=""
TARGET="" RETRIES=3 DRY_RUN=0

die() { echo "$1" >&2; exit "${2:-2}"; }

need_value() {
  # $1 = 旗標名, $2 = 值(可能不存在)
  [ -n "${2:-}" ] || die "拒絕:$1 需要一個值"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --slug)    need_value "$1" "${2:-}"; SLUG=$2; shift 2 ;;
    --what)    need_value "$1" "${2:-}"; WHAT=$2; shift 2 ;;
    --why)     need_value "$1" "${2:-}"; WHY=$2; shift 2 ;;
    --where)   need_value "$1" "${2:-}"; WHERE=$2; shift 2 ;;
    --date)    need_value "$1" "${2:-}"; DATE=$2; shift 2 ;;
    --version) need_value "$1" "${2:-}"; VERSION=$2; shift 2 ;;
    --adr)     need_value "$1" "${2:-}"; ADR=$2; shift 2 ;;
    --detail)  need_value "$1" "${2:-}"; DETAIL=$2; shift 2 ;;
    --file)    need_value "$1" "${2:-}"; TARGET=$2; shift 2 ;;
    --retries) need_value "$1" "${2:-}"; RETRIES=$2; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) sed -n '2,32p' "$0"; exit 0 ;;
    *) die "拒絕:未知參數 $1(可用:--slug --what --why --where --date --version --adr --detail --file --retries --dry-run)" ;;
  esac
done

[ -n "$SLUG" ]  || die "拒絕:缺 --slug(這筆紀錄的代號,例:guides-visual-rewrite)"
[ -n "$WHAT" ]  || die "拒絕:缺 --what(做了什麼,一句話)"
[ -n "$WHY" ]   || die "拒絕:缺 --why(為什麼要做,一句話 —— 半年後只有這句救得了你)"
[ -n "$WHERE" ] || die "拒絕:缺 --where(改動落在哪些檔/目錄)"

case "$SLUG" in
  *[!a-z0-9-]*) die "拒絕:--slug 只接受小寫英數與連字號,得「$SLUG」" ;;
esac

if [ -z "$DATE" ]; then
  DATE=$(date +%Y-%m-%d)
fi
case "$DATE" in
  [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) : ;;
  *) die "拒絕:--date 需 YYYY-MM-DD,得「$DATE」" ;;
esac

case "$RETRIES" in
  ''|*[!0-9]*) die "拒絕:--retries 需非負整數,得「$RETRIES」" ;;
esac

[ -n "$TARGET" ] || TARGET="$REPO_ROOT/docs/dev/HISTORY.md"

# ── 組出這一筆(格式正本;改格式請同步 _templates/HISTORY.md 與 README §1)──
ENTRY="## $DATE · $SLUG"
[ -n "$VERSION" ] && ENTRY="$ENTRY · $VERSION"
ENTRY="$ENTRY
- 做了什麼:$WHAT
- 為什麼:$WHY
- 落在哪:$WHERE"
[ -n "$ADR" ]    && ENTRY="$ENTRY
- 長期決策:$ADR"
[ -n "$DETAIL" ] && ENTRY="$ENTRY
- 詳細:$DETAIL"

if [ "$DRY_RUN" = "1" ]; then
  printf '%s\n' "$ENTRY"
  exit 0
fi

TARGET_DIR=$(dirname "$TARGET")
[ -d "$TARGET_DIR" ] || mkdir -p "$TARGET_DIR" || die "拒絕:建不出目錄 $TARGET_DIR"

# ── 取鎖(mkdir 原子;取不到就等,預設重試 3 次)──
# 每一「次」不是只試一下就睡飽,而是在該次的時間預算內每 0.1 秒輪詢一遍 ——
# 前一個 session 通常在幾十毫秒內就寫完放鎖,睡整秒才試會白白錯過空窗。
LOCK="$TARGET.lock"

try_lock_within() {  # $1 = 這一次最多等幾秒
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
  echo "   若確定沒有其他 session 在寫(例如上一次被強制中斷),手動移除該目錄後重跑:" >&2
  echo "   rmdir '$LOCK'" >&2
  exit 1
fi

cleanup() { rmdir "$LOCK" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

# 檔頭只在第一次建立時寫(之後一律純追加,不重寫既有內容)
if [ ! -f "$TARGET" ]; then
  cat > "$TARGET" <<'HEADER'
# 改版歷史索引

> **只增不改(append-only),最新的在最下面。**
> 本檔是**索引**,不是內容:每筆三到五行講清楚「做了什麼/為什麼/落在哪」,
> 細節住個別檔 —— 長期決策 `docs/adr/NNNN-slug.md`、
> 過程文檔 `docs/dev/<slug>/`、執行報告與稽核紀錄各自留在原地。
> 同一件事之後又變了,**不要改舊條目**,追加新的一筆並在該筆註明推翻了哪一筆。
>
> ⚠️ **不要直接編輯本檔。**用:
> ```
> scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> --where <落在哪>
> ```
> 理由:同一個專案可能同時有多個 session 在寫,直接編輯會讓後寫的把先寫的蓋掉,
> 而且不會報錯。上面那支腳本有目錄鎖 + 重試,並且只做追加。

HEADER
fi

printf '%s\n\n' "$ENTRY" >> "$TARGET" || die "拒絕:寫不進 $TARGET"

echo "✅ 已追加到 $TARGET"
printf '%s\n' "$ENTRY"
