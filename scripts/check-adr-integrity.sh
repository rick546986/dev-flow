#!/bin/bash
# ADR 完整性守衛(Repo-local,相容性守衛,不重編號、不改命名方案)。
#
# 規則:
#   ①`docs/adr/NNNN-*.md` 的檔名格式:四位數字 + `-` + kebab-case slug + `.md`。
#   ②同一個 NNNN 不得出現兩次(重複編號 = 引用會指到兩份文件,追溯鏈斷)。
#   ③YAML frontmatter:`status` ∈ {proposed,accepted,deprecated,superseded};
#     `topics` 為非空 list;`supersedes` / `superseded_by` 為 ADR id 清單(可空)。
#   ④Active = status accepted only。同 topic 不得有超過一份 active ADR。
#   ⑤supersedes / superseded_by 不得指向不存在的 NNNN,且須雙向一致;
#     supersedes 邊不得成環。
#
# 本腳本**不重新編號既有 ADR**,也不建知識索引(Pilot-2);只讓 ADR meta 可被
# 機器解析並擋住壞鏈。
#
# 用法:
#   scripts/check-adr-integrity.sh [root]      # 掃 root(缺省 = repo root)+ 跑 fixture battery
#   scripts/check-adr-integrity.sh --scan DIR  # 只掃 DIR 這個 adr 目錄,回傳其 exit code
#                                              # (供 §12 mutation 驗證使用)
#
# Fixture battery(證明負向規則真的被覆蓋;fixture 刻意放在 scripts/fixtures/adr/ 而
# **不是** docs/adr/,否則重複編號 fixture 會讓本 repo 的真實掃描永遠紅):
#   scripts/fixtures/adr/good/               → 必須 PASS
#   scripts/fixtures/adr/duplicate-number/   → 必須 FAIL(重複 0007)
#   scripts/fixtures/adr/bad-filename/       → 必須 FAIL(檔名格式錯)
#   scripts/fixtures/adr/bad-status/         → 必須 FAIL(status 不在 enum)
#   scripts/fixtures/adr/dangling-supersede/ → 必須 FAIL(斷鏈或缺互惠)
#   scripts/fixtures/adr/supersede-cycle/    → 必須 FAIL(取代成環)
#   scripts/fixtures/adr/multi-active-topic/ → 必須 FAIL(同 topic 多份 accepted)

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

SCAN_ONLY=""
if [ "${1:-}" = "--scan" ]; then
  if [ -z "${2:-}" ]; then
    echo "usage: $0 --scan <adr-dir>" >&2
    exit 2
  fi
  SCAN_ONLY="$2"
elif [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

scan() {
  # $1 = adr directory
  python3 - "$1" <<'PY'
import os
import re
import sys

adr_dir = sys.argv[1]
name_re = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ALLOWED_STATUS = frozenset({"proposed", "accepted", "deprecated", "superseded"})
ID_RE = re.compile(r"^\d{4}$")


def strip_comment(raw):
    in_single = False
    in_double = False
    out = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "'" and not in_double:
            in_single = not in_single
            out.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
        elif ch == "#" and not in_single and not in_double:
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out).rstrip()


def unquote(val):
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    return val


def parse_inline_list(text):
    inner = text.strip()[1:-1].strip()
    if not inner:
        return []
    items = []
    buf = []
    in_q = None
    for ch in inner:
        if in_q:
            buf.append(ch)
            if ch == in_q:
                in_q = None
            continue
        if ch in ("'", '"'):
            in_q = ch
            buf.append(ch)
            continue
        if ch == ",":
            items.append(unquote("".join(buf)))
            buf = []
            continue
        buf.append(ch)
    if buf or items:
        items.append(unquote("".join(buf)))
    return [x for x in items if x != ""]


def parse_frontmatter(text):
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    meta = {}
    key = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if re.match(r"^[ \t]+-\s+", raw):
            if key is None:
                return None
            item = unquote(strip_comment(re.sub(r"^[ \t]+-\s+", "", raw)))
            cur = meta.setdefault(key, [])
            if not isinstance(cur, list):
                return None
            cur.append(item)
            continue
        if ":" not in raw:
            return None
        left, right = raw.split(":", 1)
        if left.startswith(" ") or left.startswith("\t"):
            return None
        key = left.strip()
        right = strip_comment(right).strip()
        if right == "" or right == "|" or right == ">":
            meta[key] = []
            continue
        if right in ("null", "~", "NULL"):
            meta[key] = None
            continue
        if right.startswith("[") and right.endswith("]"):
            meta[key] = parse_inline_list(right)
            continue
        meta[key] = unquote(right)
    return meta


def as_id_list(value, field, name, problems):
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        items = [value] if value != "" else []
    else:
        problems.append(f"{name}: {field} 型別不合法")
        return []
    out = []
    for item in items:
        s = str(item).strip()
        if not ID_RE.match(s):
            problems.append(f"{name}: {field} 含非法 ADR id `{s}`(需四位數字)")
            continue
        out.append(s)
    return out


if not os.path.isdir(adr_dir):
    print(f"  • {adr_dir} absent — 0 files scanned(採用專案才有 ADR;母版 repo 無)")
    raise SystemExit(0)

names = sorted(n for n in os.listdir(adr_dir) if n.endswith(".md"))
problems = []
numbers = {}
records = []

for name in names:
    match = name_re.match(name)
    if not match:
        problems.append(f"檔名格式錯:{name}(需 NNNN-kebab-slug.md,四位數字)")
        continue
    number = match.group(1)
    numbers.setdefault(number, []).append(name)
    path = os.path.join(adr_dir, name)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        problems.append(f"{name}: 讀取失敗({exc})")
        continue
    meta = parse_frontmatter(text)
    if meta is None:
        problems.append(f"{name}: 缺 YAML frontmatter(需 --- ... ---)")
        continue
    status = meta.get("status")
    if not isinstance(status, str) or not status:
        problems.append(f"{name}: 缺 status")
    elif status not in ALLOWED_STATUS:
        problems.append(
            f"{name}: status 非法 `{status}`"
            f"(需 {'|'.join(sorted(ALLOWED_STATUS))})"
        )
    topics = meta.get("topics")
    if topics is None:
        problems.append(f"{name}: 缺 topics")
        topic_list = []
    elif isinstance(topics, str):
        topic_list = [topics] if topics else []
    elif isinstance(topics, list):
        topic_list = [str(t).strip() for t in topics if str(t).strip()]
    else:
        problems.append(f"{name}: topics 型別不合法")
        topic_list = []
    if not topic_list:
        problems.append(f"{name}: topics 不得為空")
    for topic in topic_list:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", topic):
            problems.append(f"{name}: topic `{topic}` 需 kebab-case")
    supersedes = as_id_list(meta.get("supersedes"), "supersedes", name, problems)
    superseded_by = as_id_list(meta.get("superseded_by"), "superseded_by", name, problems)
    if status == "superseded" and not superseded_by:
        problems.append(f"{name}: status=superseded 但 superseded_by 為空")
    if superseded_by and status not in (None, "superseded") and status in ALLOWED_STATUS:
        problems.append(f"{name}: 有 superseded_by 但 status=`{status}`(應為 superseded)")
    records.append(
        {
            "name": name,
            "id": number,
            "status": status if isinstance(status, str) else "",
            "topics": topic_list,
            "supersedes": supersedes,
            "superseded_by": superseded_by,
        }
    )

for number, owners in sorted(numbers.items()):
    if len(owners) > 1:
        problems.append(f"編號重複:{number} 出現 {len(owners)} 次 → {owners}")

by_id = {rec["id"]: rec for rec in records}

for rec in records:
    for target in rec["supersedes"]:
        if target not in by_id:
            problems.append(
                f"{rec['name']}: supersedes 指向不存在的 {target}"
            )
            continue
        if rec["id"] not in by_id[target]["superseded_by"]:
            problems.append(
                f"{rec['name']}: supersedes {target},但 {target} 的 "
                f"superseded_by 未回指 {rec['id']}"
            )
    for target in rec["superseded_by"]:
        if target not in by_id:
            problems.append(
                f"{rec['name']}: superseded_by 指向不存在的 {target}"
            )
            continue
        if rec["id"] not in by_id[target]["supersedes"]:
            problems.append(
                f"{rec['name']}: superseded_by {target},但 {target} 的 "
                f"supersedes 未回指 {rec['id']}"
            )

# cycle on supersedes edges (from → superseded target)
graph = {rec["id"]: list(rec["supersedes"]) for rec in records}
WHITE, GRAY, BLACK = 0, 1, 2
color = {node: WHITE for node in graph}
cycle_found = []


def dfs(node, stack):
    color[node] = GRAY
    stack.append(node)
    for nxt in graph.get(node, []):
        if nxt not in color:
            continue
        if color[nxt] == GRAY:
            loop_start = stack.index(nxt)
            cycle_found.append(stack[loop_start:] + [nxt])
            return True
        if color[nxt] == WHITE and dfs(nxt, stack):
            return True
    stack.pop()
    color[node] = BLACK
    return False


for node in list(graph):
    if color[node] == WHITE:
        dfs(node, [])
for loop in cycle_found:
    problems.append("取代成環:" + " → ".join(loop))

# multi-active same topic
active_by_topic = {}
for rec in records:
    if rec["status"] != "accepted":
        continue
    for topic in rec["topics"]:
        active_by_topic.setdefault(topic, []).append(rec["id"])
for topic, owners in sorted(active_by_topic.items()):
    if len(owners) > 1:
        problems.append(
            f"同 topic 多份 active(accepted): `{topic}` → {owners}"
        )

print(f"  • {adr_dir}: {len(names)} 個 .md 掃描")
for problem in problems:
    print(f"  ✗ {problem}")
if problems:
    raise SystemExit(1)
print(
    f"  ✓ 編號/檔名/status/topics/取代鏈合規"
    f"({len(numbers)} 個編號;active=accepted only)"
)
PY
}

if [ -n "$SCAN_ONLY" ]; then
  scan "$SCAN_ONLY"
  exit $?
fi

echo "=== ADR 完整性守衛 ==="
FAILED=0

echo "-- 真實掃描 --"
scan "$ROOT/docs/adr" || FAILED=1

echo "-- fixture battery(證明負向規則有覆蓋)--"
battery() {
  local dir="$1" expect="$2" label="$3"
  local out rc
  out=$(scan "$SELF_DIR/fixtures/adr/$dir" 2>&1)
  rc=$?
  if [ "$expect" = "pass" ] && [ "$rc" -eq 0 ]; then
    echo "  ✓ $label:如預期 PASS"
  elif [ "$expect" = "fail" ] && [ "$rc" -ne 0 ]; then
    echo "  ✓ $label:如預期 FAIL"
  else
    echo "  ✗ $label:預期 $expect,實得 exit $rc"
    echo "$out" | sed 's/^/      /'
    FAILED=1
  fi
}
battery good               pass "good fixture(合法 meta + 雙向取代鏈)"
battery duplicate-number   fail "duplicate-number fixture(0007 出現兩次)"
battery bad-filename       fail "bad-filename fixture(檔名格式錯)"
battery bad-status         fail "bad-status fixture(status 不在 enum)"
battery dangling-supersede fail "dangling-supersede fixture(斷鏈或缺互惠)"
battery supersede-cycle    fail "supersede-cycle fixture(取代成環)"
battery multi-active-topic fail "multi-active-topic fixture(同 topic 多份 accepted)"

echo
if [ "$FAILED" -ne 0 ]; then
  echo "⛔ ADR 完整性守衛:FAILED"
  exit 1
fi
echo "✅ ADR 完整性守衛:全過"
exit 0
