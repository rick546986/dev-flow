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
# 「活文件」候選清單見下方 SCAN_TARGETS,其中歷史紀錄類(docs/prompts/、
# docs/dev/4cap-remediation/、docs/dev/HISTORY.md、docs/dev/<feature 過程目錄>、notes/)
# 預設列在 ALLOWLIST、不實際掃描 —— 這些是已成事實的會議/決策/移轉紀錄,原樣保留,
# 不因路徑改名回頭校正。
# ALLOWLIST 只是「候選但豁免」,不是「路徑不存在」:移除其中任一條目,對應目錄就會
# 併入真掃描(見 test-architecture-guards.sh 的負向案,以及本檔驗收步驟的破壞實驗——
# 拿掉 notes/ 後對真 repo 重跑必紅,證明守衛真的在掃、不是空轉)。
#
# docs/dev/ 底下的分類原則(2026-08-15 補,第三批獨立審查 P1 —— 此前 docs/dev/tools/、
# docs/dev/STATUS.md、docs/dev/devflow-contract.json、docs/adr/ 完全不在掃描目標也不在
# 可見豁免清單,對這些路徑塞禁字守衛仍零命中,違反上一段「ALLOWLIST=候選但豁免」的語意):
#   ①基建與看板(tools/、STATUS.md、devflow-contract.json、README.md 若存在)= 活文件,必掃。
#   ②feature 過程檔(docs/dev/<feature>/ 各自的 1-discussion~7-review 系列)與
#     docs/dev/HISTORY.md = 紀錄,豁免且**印出來**(見 scan_targets() 的 HISTORY_CANDIDATES,
#     豁免到的目錄名逐一列名,不用萬用字元蓋掉,新增 feature 過程目錄需手動加入清單)。
#
# 本守衛腳本自己也落在 scripts/ 掃描範圍內,因此全篇**不得出現禁字的連續字面**——
# 下面用字串相加組出禁字來解釋自己,不留給 grep/本守衛咬到的連續子字串。
#
# 用法:
#   scripts/check-no-stale-paths.sh             # 掃 repo root(缺省)
#   scripts/check-no-stale-paths.sh <root>       # 掃指定 root(供 mutation 測試用 root 覆寫;
#                                                 # SCAN_TARGETS/ALLOWLIST 邏輯不變,只是相對於 root)
#   scripts/check-no-stale-paths.sh --scan <dir> # 只掃 <dir> 這一個目錄本身(遞迴全部檔案,
#                                                 # 不套 SCAN_TARGETS/ALLOWLIST;供負向 fixture 直接驗證,
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

# scan_dir_raw <dir> —— 遞迴掃 <dir> 底下每個檔案,不套 SCAN_TARGETS/ALLOWLIST。
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

# scan_targets <root> —— 依 SCAN_TARGETS/ALLOWLIST 掃「活文件」候選清單。
scan_targets() {
  python3 - "$1" <<'PY'
import os
import sys

root = sys.argv[1]

banned = [
    "plugins/local/dev-" + "flow",
    "plugins/local/dev-" + "talk",
    "/Users/" + "asheng",
]

# 現行「活文件」目標(README/docs/PLUGIN.md/guides/skills/hooks/scripts/tests/
# _templates/devflow-contract.json)。
# docs/dev/tools、docs/dev/STATUS.md、docs/dev/devflow-contract.json、docs/adr、
# docs/dev/README.md(2026-08-15 補,第三批獨立審查 P1)—— docs/dev 底下的「基建與
# 看板」類,是活文件,必掃(docs/dev/README.md 目前尚不存在,若存在 ≠ 不掃)。
ACTIVE_TARGETS = [
    "README.md",
    "docs/PLUGIN.md",
    "guides",
    "skills",
    "hooks",
    "scripts",
    "tests",
    "_templates",
    "devflow-contract.json",
    "docs/dev/tools",
    "docs/dev/STATUS.md",
    "docs/dev/devflow-contract.json",
    "docs/adr",
    "docs/dev/README.md",
]

# 歷史紀錄候選(不是「不存在的路徑」,是「候選但預設豁免」——見 ALLOWLIST)。
# docs/dev/<feature>/ 的過程目錄逐一列名(1-discussion~7-review 系列是紀錄,不因
# 併入/改名回頭校正);新增 feature 過程目錄要手動加進本清單,否則會落入
# ACTIVE_TARGETS 之外、也不在 ALLOWLIST 之內 —— 回到本次要修的「完全不可見」問題,
# 所以刻意不用萬用字元,逼每次新增都留下這行 diff。
HISTORY_CANDIDATES = [
    "docs/prompts",
    "docs/dev/4cap-remediation",
    "docs/dev/HISTORY.md",
    "docs/dev/b8-gate-twin-review-ui",
    "docs/dev/vnext-runtime",
    "notes",
]

# 允許清單:預設把 HISTORY_CANDIDATES 全部豁免、不掃。
# ⚠️ 移除其中任一條目就會讓對應目錄併入下面的真掃描——這是刻意設計,
# 用來讓「守衛真的在掃 vs. 允許清單根本沒東西可掃」可被破壞實驗驗證。
ALLOWLIST = set(HISTORY_CANDIDATES)

SCAN_TARGETS = ACTIVE_TARGETS + HISTORY_CANDIDATES

# 特定子路徑豁免(不是歷史紀錄,是本守衛自己的負向 fixture)——這份 fixture 故意含
# 禁字,只透過 `--scan` 模式驗證(見 scan_dir_raw),不得進入下面這條「活文件」真掃描,
# 否則負向 fixture 會讓本 repo 的真實掃描永遠紅(同 check-adr-integrity.sh 的 fixture
# 隔離考量)。
EXEMPT_RELPATHS = {
    "scripts/fixtures/stale-paths",
}


def check_file(path, hits):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                for pat in banned:
                    if pat in line:
                        hits.append(f"{path}:{lineno}: 命中「{pat}」")
    except OSError:
        pass


total = 0
hits = []
skipped = []
for rel in SCAN_TARGETS:
    if rel in ALLOWLIST:
        skipped.append(rel)
        continue
    full = os.path.join(root, rel)
    if not os.path.exists(full):
        continue
    if os.path.isfile(full):
        total += 1
        check_file(full, hits)
    else:
        SKIP_DIRS = {".git", "__pycache__", "node_modules", ".serena"}
        for dirpath, dirnames, filenames in os.walk(full):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            rel_dirpath = os.path.relpath(dirpath, root)
            if rel_dirpath in EXEMPT_RELPATHS or any(
                rel_dirpath == e or rel_dirpath.startswith(e + os.sep)
                for e in EXEMPT_RELPATHS
            ):
                dirnames[:] = []
                continue
            for name in filenames:
                if name.endswith((".pyc", ".pyo")):
                    continue
                path = os.path.join(dirpath, name)
                total += 1
                check_file(path, hits)

skip_label = "、".join(skipped) if skipped else "(無)"
print(f"  • 活文件掃描:{total} 個檔案(允許清單略過:{skip_label})")
for h in hits:
    print(f"  ✗ {h}")
if hits:
    raise SystemExit(1)
if total == 0:
    print("  ⚠ 0 檔 scanned — 沒解析到 ≠ 沒問題")
    raise SystemExit(2)
print("  ✓ 零命中")
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
