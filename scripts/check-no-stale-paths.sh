#!/bin/bash
# 過期外掛路徑守衛(Repo-local,相容性守衛,不判斷文件內容好壞,只驗兩類禁字)。
#
# 背景:dev-talk 已併入 dev-flow 單一 plugin(見 docs/PLUGIN.md、
# docs/adr/0001-merge-plugin-into-methodology-repo.md),散發方式也從「local
# marketplace 目錄」改成「github marketplace → cache 安裝」,安裝後實際路徑為
# ~/.claude/plugins/cache/dev-flow/dev-flow/<version>/。活文件不得再寫死已不存在
# 的舊 local marketplace 路徑,也不得寫死開發者個人的 /Users/<本機使用者> 絕對路徑。
#
# 規則(只驗這兩條):
#   ①活文件不得出現舊版拆分 plugin 時代的 local marketplace 路徑(dev-flow、
#     dev-talk 各一種寫法)。
#   ②活文件不得出現本機開發者的個人 /Users/<name> 絕對路徑。
#
# ── 掃描設計(2026-08-15 N-5 改版:fail-closed,取代舊版 fail-open)──────────────
# 舊版是「明確列入 ACTIVE_TARGETS 才掃」——example/、observability/、manifests/ 等
# 約 75 個活檔完全不在 ACTIVE_TARGETS 也不在可見豁免清單,塞禁字 exit 0、守衛看不到。
# 這是「補清單」治不好的病:下一個新目錄一樣會漏。
#
# 新版倒過來:掃描來源改成 `git ls-files`(repo 全部追蹤檔),**預設全部要掃**,
# 只有在下面 ALLOWLIST 裡逐條列名、附理由的路徑才豁免。新增目錄/新增檔案不用被
# 加進任何清單就會自動進入掃描——要豁免才需要動這份清單,而清單本身逐條列印
# (透明豁免),不是靜默跳過。
#
# ALLOWLIST 只豁免這些(理由見腳本內對照表):
#   docs/prompts、docs/dev/4cap-remediation、docs/dev/HISTORY.md、
#   docs/dev/b8-gate-twin-review-ui、docs/dev/vnext-runtime(feature 過程目錄,
#   逐一列名不用萬用字元,新增 feature 過程目錄需手動加入 —— 這是刻意設計,
#   讓「忘了加」的後果是「被掃到」而不是「消失不見」,方向與舊版的漏洞相反)、
#   notes(歷史紀錄)、scripts/fixtures/stale-paths(負向教材,只透過 --scan 驗證)、
#   scripts/check-no-stale-paths.sh(本腳本自身;下面禁字用字串相加組出,不留連續
#   字面給自己的掃描咬到,額外豁免防未來註解不慎誤植連續字面)。
#
# 二進位檔:掃描一律經 `grep -I`,二進位檔自然被跳過,不需要另外偵測副檔名。
#
# 用法:
#   scripts/check-no-stale-paths.sh             # 掃 repo root(缺省)
#   scripts/check-no-stale-paths.sh <root>       # 掃指定 root(供 mutation 測試用 root 覆寫;
#                                                 # <root> 必須是 git working tree ——
#                                                 # 掃描來源是 `git -C <root> ls-files`)
#   scripts/check-no-stale-paths.sh --scan <dir> # 只掃 <dir> 這一個目錄本身(遞迴全部檔案,
#                                                 # 不套 git ls-files/ALLOWLIST;供負向 fixture 直接驗證,
#                                                 # 寫法對齊 check-adr-integrity.sh 的 --scan 模式)

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)

SCAN_ONLY=""
if [ "${1:-}" = "--scan" ]; then
  if [ -z "${2:-}" ]; then
    echo "usage: $0 --scan <dir>" >&2
    exit 2
  fi
  SCAN_ONLY="$2"
elif [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

# scan_dir_raw <dir> —— 遞迴掃 <dir> 底下每個檔案,不套 git ls-files/ALLOWLIST。
# 供 --scan 模式(fixture 直接驗證)使用。
scan_dir_raw() {
  python3 - "$1" <<'PY'
import os
import sys

root = sys.argv[1]
banned = [
    "plugins/local/dev-" + "flow",
    "plugins/local/dev-" + "talk",
    "/Users/" + "asheng",
]

if not os.path.isdir(root):
    print(f"  • {root} absent — 0 檔掃描")
    raise SystemExit(2)

count = 0
hits = []
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".serena"}
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for name in filenames:
        if name.endswith((".pyc", ".pyo")):
            continue
        path = os.path.join(dirpath, name)
        count += 1
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, 1):
                    for pat in banned:
                        if pat in line:
                            hits.append(f"{path}:{lineno}: 命中「{pat}」")
        except OSError:
            continue

print(f"  • {root}: {count} 個檔案掃描")
for h in hits:
    print(f"  ✗ {h}")
if hits:
    raise SystemExit(1)
if count == 0:
    print("  ⚠ 0 檔 scanned — 沒解析到 ≠ 沒問題")
    raise SystemExit(2)
print("  ✓ 零命中")
PY
}

# scan_targets <root> —— fail-closed:git ls-files 全量追蹤檔 − 印出來的 ALLOWLIST。
scan_targets() {
  python3 - "$1" <<'PY'
import os
import subprocess
import sys

root = sys.argv[1]

# (規則說明, 禁字字面) —— 每條各自一個獨立檢查(見下方 check_pattern),供 N-2
# 檢查數地板使用:地板釘的是「有幾條禁字規則」,不是「掃了幾個檔案」——後者會隨
# repo 成長自然變動(不該因為新增一份無關文件就要調地板),前者只在有人刻意
# 增刪禁字規則時才變。
banned = [
    ("舊版 dev-flow local marketplace 路徑", "plugins/local/dev-" + "flow"),
    ("舊版 dev-talk local marketplace 路徑", "plugins/local/dev-" + "talk"),
    ("開發者個人絕對路徑", "/Users/" + "asheng"),
]

# ALLOWLIST(逐條列印,每條附理由)。新增目錄/新增檔案預設落入下面的真掃描——
# 要豁免必須在這裡加一行,這行本身就是會被 review 到的 diff(fail-closed 的核心)。
ALLOWLIST = [
    ("docs/prompts",
     "歷史 prompt 存檔(會議/決策移轉紀錄,原樣保留,不因路徑改名回頭校正)"),
    ("docs/dev/4cap-remediation",
     "4cap 補救過程紀錄"),
    ("docs/dev/HISTORY.md",
     "只能用 scripts/history-append.sh 追加的歷史紀錄"),
    ("docs/dev/b8-gate-twin-review-ui",
     "feature 過程目錄(1-discussion~7-review 系列),紀錄不回頭校正"),
    ("docs/dev/vnext-runtime",
     "feature 過程目錄,紀錄不回頭校正"),
    ("notes",
     "歷史紀錄(會議/決策/派工/change-manifests/design/patches 全歸此類)"),
    ("scripts/fixtures/stale-paths",
     "負向教材,故意含禁字,只透過 --scan 模式驗證,不得進真掃描"),
    ("scripts/check-no-stale-paths.sh",
     "本腳本自身;禁字以字串相加組出不留連續字面,額外豁免防未來註解誤植連續字面"),
]
ALLOW_ENTRIES = [e for e, _ in ALLOWLIST]


def allowlist_match(rel):
    for entry in ALLOW_ENTRIES:
        if rel == entry or rel.startswith(entry + "/"):
            return entry
    return None


def tracked_files(root):
    result = subprocess.run(
        ["git", "-C", root, "ls-files", "-z"],
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", "replace").strip()
        print(f"  ⚠ git ls-files 失敗(root 必須是 git working tree):{stderr}")
        raise SystemExit(2)
    raw = result.stdout.decode("utf-8", "replace")
    return sorted(p for p in raw.split("\0") if p)


all_files = tracked_files(root)

allow_counts = {entry: 0 for entry in ALLOW_ENTRIES}
candidates = []
for rel in all_files:
    hit_entry = allowlist_match(rel)
    if hit_entry:
        allow_counts[hit_entry] += 1
        continue
    candidates.append(rel)

print(f"  • git ls-files 全量追蹤檔:{len(all_files)} 個")
print("  • ALLOWLIST(逐條印出,新增目錄/檔案預設不在此列 = 會被掃到):")
for entry, reason in ALLOWLIST:
    print(f"      - {entry}({allow_counts[entry]} 檔)— {reason}")
skipped_total = len(all_files) - len(candidates)
print(f"  • 活文件掃描:{len(candidates)} 個檔案"
      f"(= 全量 {len(all_files)} − 允許清單命中 {skipped_total})")

checks = 0
hits = []


def check_pattern(label, pat):
    """對全部 candidates 跑一次這條禁字規則;checks 計數與規則呼叫綁在一起
    (同一次呼叫同時算數、同時查),整條規則被刪掉,checks 跟著掉,地板才咬得住。"""
    global checks
    checks += 1
    if not candidates:
        return
    full_paths = [os.path.join(root, rel) for rel in candidates]
    result = subprocess.run(
        ["grep", "-I", "-n", "-H", "-F", pat, *full_paths],
        capture_output=True, text=True, errors="ignore",
    )
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            parts = line.split(":", 2)
            if len(parts) == 3:
                fp, lineno, content = parts
            else:
                fp, lineno, content = line, "?", ""
            rel = os.path.relpath(fp, root)
            hits.append(f"{rel}:{lineno}: 命中「{label}」— {content.strip()}")
    elif result.returncode not in (0, 1):
        print(f"  ⚠ grep 執行錯誤(rc={result.returncode}):{result.stderr.strip()}")
        raise SystemExit(2)


for label, pat in banned:
    check_pattern(label, pat)

# ── 檢查數地板(N-2,2026-08-15)──────────────────────────────────────────────
# ⚠️ 這個數字必須**等於當下的實際禁字規則數**,不是「大概抓個下限」——地板留餘裕=
# 沒有牙齒(同 repo 慣例:scripts/check-stage67-enforcement.sh:232、
# scripts/test-architecture-guards.sh 的 EXPECTED_TOTAL)。實測:把上面的
# `for label, pat in banned: check_pattern(...)` 整段刪掉,candidates 的檔案數
# 不受影響(掃描範圍地板抓不到這種「掃了但沒真的查」),沒有這條地板會直接印
# 「✓ 零命中」全過。新增/刪除禁字規則時把這個數字一起調。
MIN_CHECKS = 3
if checks < MIN_CHECKS:
    hits.append(f"⛔ 實際只跑了 {checks} 條禁字規則檢查(地板 {MIN_CHECKS})—— "
                f"檢查本身被刪掉或迴圈跑了零圈,這比條款失效更嚴重")

# ── ALLOWLIST 內容地板(同一輪補,防「悄悄擴大豁免範圍」的假綠)────────────────
# 舊版只釘條目**數**(EXPECTED_ALLOWLIST_LEN),抓不到「條數不變、內容被換掉」
#(2026-08-16 獨立審查 finding 3 實測:把 "docs/dev/4cap-remediation" 換成 "docs"
# ——條目數仍是 8、禁字規則一樣零命中,但 "docs" 這個字首豁免會多蓋掉 13 個真檔案
# 的掃描,守衛照樣印「✅ 全過」)。改成**逐條釘死字面清單**:排序後與 ALLOWLIST
# 的條目逐一比對,不只比對長度——多一條或少一條、或任何一條字面被換掉都要現形。
# 新增/刪除/改名豁免項目時把下面這份清單跟著同步改。
EXPECTED_ALLOWLIST_ENTRIES = sorted([
    "docs/prompts",
    "docs/dev/4cap-remediation",
    "docs/dev/HISTORY.md",
    "docs/dev/b8-gate-twin-review-ui",
    "docs/dev/vnext-runtime",
    "notes",
    "scripts/fixtures/stale-paths",
    "scripts/check-no-stale-paths.sh",
])
_actual_allowlist_entries = sorted(e for e, _ in ALLOWLIST)
if _actual_allowlist_entries != EXPECTED_ALLOWLIST_ENTRIES:
    hits.append(
        f"⛔ ALLOWLIST 條目內容與釘死清單不符(不只比對條數)—— "
        f"多:{sorted(set(_actual_allowlist_entries) - set(EXPECTED_ALLOWLIST_ENTRIES))} "
        f"少:{sorted(set(EXPECTED_ALLOWLIST_ENTRIES) - set(_actual_allowlist_entries))}"
        f"(新增/刪除/改名豁免項目時要同步調 EXPECTED_ALLOWLIST_ENTRIES;只釘條數會被"
        f"「內容換掉但條數不變」繞過)")

for h in hits:
    print(f"  ✗ {h}")
if hits:
    raise SystemExit(1)
if not candidates:
    print("  ⚠ 0 檔 scanned — 沒解析到 ≠ 沒問題")
    raise SystemExit(2)
print(f"  ✓ 零命中(禁字規則檢查數 {checks}/{MIN_CHECKS})")
PY
}

if [ -n "$SCAN_ONLY" ]; then
  scan_dir_raw "$SCAN_ONLY"
  exit $?
fi

echo "=== 過期外掛路徑守衛 ==="
scan_targets "$ROOT"
STATUS=$?

echo
if [ "$STATUS" -ne 0 ]; then
  echo "⛔ 過期外掛路徑守衛:FAILED"
  exit "$STATUS"
fi
echo "✅ 過期外掛路徑守衛:全過"
exit 0
