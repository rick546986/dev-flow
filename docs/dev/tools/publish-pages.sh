#!/bin/bash
# publish-pages.sh — 把站審 html + shots + guides 組進 public/,保相對路徑。
#
# 這是 GitLab／Gitea Pages 食譜正文。三邊薄殼只准呼叫本檔,不要再抄複製清單。
# GitHub 母版已用根目錄 Pages,不走這支(超連規則見 notes/design/pages-hosting.md)。
# 本機對應是 `python3 scripts/devflow_gate.py serve --root .`,不要另開伺服器。
#
# 正本 scripts/;dev-setup 散發到 docs/dev/tools/(與 history-append 同一條路)。
# 用 git toplevel 當預設根,散發後 --root 仍指專案根,不會寫到 docs/dev/docs/dev/。
#
# 用法:
#   scripts/publish-pages.sh --root DIR [--out DIR]
#   --root  專案根(不是位置參數)
#   --out   預設 <root>/public
#
# exit:0 = 已組好 / 2 = 用法錯誤

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(git -C "$SELF_DIR" rev-parse --show-toplevel 2>/dev/null || true)

ROOT=""
OUT=""

die() { echo "$1" >&2; exit "${2:-2}"; }

need_value() {
  [ -n "${2:-}" ] || die "拒絕:$1 需要一個值"
}

usage() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --root) need_value "$1" "${2:-}"; ROOT=$2; shift 2 ;;
    --out)  need_value "$1" "${2:-}"; OUT=$2; shift 2 ;;
    -h|--help|help)
      usage
      exit 2 ;;
    *) die "拒絕:未知參數 $1(可用:--root --out)" ;;
  esac
done

if [ -z "$ROOT" ]; then
  if [ -n "$REPO_ROOT" ]; then
    ROOT=$REPO_ROOT
  else
    die "拒絕:缺 --root(專案根;不是位置參數)"
  fi
fi

ROOT=$(cd "$ROOT" && pwd) || die "拒絕:--root 不是目錄:$ROOT"
if [ -z "$OUT" ]; then
  OUT="$ROOT/public"
fi
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd) || die "拒絕:--out 建不起來"

STAGES="1-discussion.html 2-decision.html 5-tasks.html 6-implementation-notes.html 7-review.html"

copy_file() {
  local rel=$1
  local src="$ROOT/$rel"
  local dst="$OUT/$rel"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

copy_shots() {
  local rel_dir=$1
  local src="$ROOT/$rel_dir/shots"
  [ -d "$src" ] || return 0
  mkdir -p "$OUT/$rel_dir/shots"
  cp -R "$src/." "$OUT/$rel_dir/shots/"
}

# 站審 html(docs/dev/<feat>/ 與 example/<feat>/ 同名)＋旁邊的 shots/
for bucket in docs/dev example; do
  [ -d "$ROOT/$bucket" ] || continue
  for feat_dir in "$ROOT/$bucket"/*; do
    [ -d "$feat_dir" ] || continue
    feat_rel="${feat_dir#"$ROOT"/}"
    copied=0
    for name in $STAGES; do
      if [ -f "$feat_dir/$name" ]; then
        copy_file "$feat_rel/$name"
        copied=1
      fi
    done
    if [ "$copied" -eq 1 ]; then
      copy_shots "$feat_rel"
    fi
  done
done

# guides 鏈進同一棵,既有超連才不會斷
if [ -d "$ROOT/guides" ]; then
  mkdir -p "$OUT/guides"
  cp -R "$ROOT/guides/." "$OUT/guides/"
fi

echo "publish-pages: $OUT"
exit 0
