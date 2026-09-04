#!/bin/bash
# test-upgrade-leftovers.sh — upgrade 殘件刪除的行為牙
#
# 種一棵假採用樹:退役 _templates/CONTEXT.md + baseline 複本 + 專案正在用的
# docs/dev/CONTEXT.md + 專案根 CONTEXT.md。upgrade 殘件腳本必須刪掉前兩者,
# 不准動後兩者。dry-run 不准刪。pack 仍出貨的模板不准被當殘件。
#
# 另外釘住 KNOWN_RETIRED 分支的雜湊安全網(#96 enhancement):跟 baseline
# 內容相同才直刪;客製過(內容不同)或 baseline 沒有對應檔可比(無法比對)
# 一律搬到 docs/dev/.devflow-upgrade-trash/<時間戳記>/ 而不是無備份直刪。
#
# 用法:scripts/test-upgrade-leftovers.sh [pack]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障
set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
PACK=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  PACK=$(cd "$1" && pwd) || exit 2
fi

TOOL="$SELF_DIR/devflow-upgrade-leftovers.sh"
[ -f "$TOOL" ] || { echo "FATAL: 找不到 $TOOL" >&2; exit 2; }
chmod +x "$TOOL"

python3 - "$PACK" "$TOOL" <<'PY'
import os
import shutil
import subprocess
import sys
import tempfile

pack, tool = sys.argv[1], sys.argv[2]
passed = 0
failed = 0
MIN_CASES = 13


def run(root, *args, stamp=None):
    env = os.environ.copy()
    if stamp is not None:
        env["DEVFLOW_UPGRADE_LEFTOVERS_STAMP"] = stamp
    else:
        env.pop("DEVFLOW_UPGRADE_LEFTOVERS_STAMP", None)
    return subprocess.run(
        ["bash", tool, "--root", root, "--pack", pack, *args],
        capture_output=True,
        text=True,
        env=env,
    )


def expect(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  ✓ " + label)
        return
    failed += 1
    print("  ✗ " + label, file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)


def plant(tmp):
    root = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(root, "docs", "dev", "_templates"))
    os.makedirs(os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates"))
    leftovers = (
        os.path.join(root, "docs", "dev", "_templates", "CONTEXT.md"),
        os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates", "CONTEXT.md"),
    )
    live = os.path.join(root, "docs", "dev", "CONTEXT.md")
    top = os.path.join(root, "CONTEXT.md")
    kept = os.path.join(root, "docs", "dev", "_templates", "HISTORY.md")
    # leftovers[0]/[1] 內容故意相同——代表典型情境:live 複本沒被使用者動過,
    # 跟 baseline 一致,雜湊安全網要直刪不搬 trash(搬 trash 的案例見下面
    # 「客製過」「baseline 缺對應檔」兩案,那邊才要故意讓內容不同)。
    for path, body in (
        (leftovers[0], "retired template leftover\n"),
        (leftovers[1], "retired template leftover\n"),
        (live, "live project context\n"),
        (top, "root context\n"),
        (kept, "still-shipped template\n"),
    ):
        open(path, "w", encoding="utf-8").write(body)
    return root, leftovers, live, top, kept


def trash_root(root):
    return os.path.join(root, "docs", "dev", ".devflow-upgrade-trash")


def find_trash_files(root):
    base = trash_root(root)
    if not os.path.isdir(base):
        return []
    out = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            out.append(os.path.join(dirpath, name))
    return out


with tempfile.TemporaryDirectory(prefix="upgrade-leftovers-") as tmp:
    root, leftovers, live, top, kept = plant(tmp)
    dry = run(root)
    expect(
        "dry-run 列出殘件且 exit 0",
        dry.returncode == 0 and "leftover:" in dry.stdout,
        (dry.stdout or "") + (dry.stderr or ""),
    )
    expect(
        "dry-run 不准刪檔",
        all(os.path.isfile(p) for p in leftovers + (live, top, kept)),
        "dry-run 後有檔消失",
    )

    applied = run(root, "--apply")
    expect(
        "apply 直刪 _templates/CONTEXT.md 與 baseline 複本(內容與 baseline 一致,不搬 trash)",
        applied.returncode == 0
        and not os.path.isfile(leftovers[0])
        and not os.path.isfile(leftovers[1])
        and not os.path.isdir(trash_root(root)),
        (applied.stdout or "") + (applied.stderr or ""),
    )
    expect(
        "apply 保留專案根 CONTEXT.md、live docs/dev/CONTEXT.md、仍出貨的 HISTORY.md",
        os.path.isfile(live)
        and os.path.isfile(top)
        and os.path.isfile(kept)
        and open(live, encoding="utf-8").read() == "live project context\n"
        and open(top, encoding="utf-8").read() == "root context\n",
        "受保護檔被動到",
    )

# ── KNOWN_RETIRED 雜湊安全網 案 1:未修改(跟 baseline 一致)—— --apply 直刪 ──
with tempfile.TemporaryDirectory(prefix="upgrade-leftovers-unmodified-") as tmp:
    root = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(root, "docs", "dev", "_templates"))
    os.makedirs(os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates"))
    live_leftover = os.path.join(root, "docs", "dev", "_templates", "CONTEXT.md")
    baseline_leftover = os.path.join(
        root, "docs", "dev", ".devflow-baseline", "_templates", "CONTEXT.md"
    )
    same_body = "unmodified retired template\n"
    open(live_leftover, "w", encoding="utf-8").write(same_body)
    open(baseline_leftover, "w", encoding="utf-8").write(same_body)

    applied = run(root, "--apply")
    expect(
        "未修改的退役檔:--apply 直刪(不搬 trash)",
        applied.returncode == 0
        and not os.path.isfile(live_leftover)
        and not os.path.isfile(baseline_leftover)
        and not os.path.isdir(trash_root(root)),
        (applied.stdout or "") + (applied.stderr or ""),
    )

# ── KNOWN_RETIRED 雜湊安全網 案 2:客製過(跟 baseline 不同)—— --apply 搬 trash ──
with tempfile.TemporaryDirectory(prefix="upgrade-leftovers-customized-") as tmp:
    root = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(root, "docs", "dev", "_templates"))
    os.makedirs(os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates"))
    live_leftover = os.path.join(root, "docs", "dev", "_templates", "CONTEXT.md")
    baseline_leftover = os.path.join(
        root, "docs", "dev", ".devflow-baseline", "_templates", "CONTEXT.md"
    )
    customized_body = "使用者客製過的內容,不是出廠版\n"
    open(live_leftover, "w", encoding="utf-8").write(customized_body)
    open(baseline_leftover, "w", encoding="utf-8").write("出廠原版\n")

    applied = run(root, "--apply")
    expect(
        "客製過的退役檔:--apply 後原位置消失",
        applied.returncode == 0 and not os.path.isfile(live_leftover),
        (applied.stdout or "") + (applied.stderr or ""),
    )
    trashed_files = [
        p for p in find_trash_files(root) if os.path.basename(p) == "CONTEXT.md"
    ]
    expect(
        "客製過的退役檔:搬進 trash 且內容等於客製版",
        len(trashed_files) == 1
        and open(trashed_files[0], encoding="utf-8").read() == customized_body,
        "trash 內容:%r" % [
            open(p, encoding="utf-8").read() for p in trashed_files
        ],
    )
    expect(
        "客製過的退役檔:stdout 含搬移提示",
        "已搬移" in applied.stdout and "請自行檢視後刪除" in applied.stdout,
        applied.stdout,
    )

# ── KNOWN_RETIRED 雜湊安全網 案 3:baseline 缺對應檔(無法比對)—— --apply 搬 trash ──
with tempfile.TemporaryDirectory(prefix="upgrade-leftovers-nobaseline-") as tmp:
    root = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(root, "docs", "dev", "_templates"))
    # 刻意不建 .devflow-baseline/_templates/ —— 沒有 baseline 可比對。
    live_leftover = os.path.join(root, "docs", "dev", "_templates", "CONTEXT.md")
    orphan_body = "沒有 baseline 可比對的退役檔\n"
    open(live_leftover, "w", encoding="utf-8").write(orphan_body)

    applied = run(root, "--apply")
    expect(
        "baseline 缺對應檔:--apply 後原位置消失、exit 0",
        applied.returncode == 0 and not os.path.isfile(live_leftover),
        (applied.stdout or "") + (applied.stderr or ""),
    )
    trashed_files = find_trash_files(root)
    expect(
        "baseline 缺對應檔:搬進 trash 且內容保留",
        len(trashed_files) == 1
        and open(trashed_files[0], encoding="utf-8").read() == orphan_body,
        "trash 檔案:%r" % trashed_files,
    )

# ── KNOWN_RETIRED 雜湊安全網 案 4:同一秒內第二次 --apply 撞名 —— 不准覆蓋 ──
# 用 DEVFLOW_UPGRADE_LEFTOVERS_STAMP 強迫兩次 run 落在同一個 stamp 目錄,
# 決定性地觸發撞名分支,不必賭兩次呼叫剛好落在同一個真實秒內。
with tempfile.TemporaryDirectory(prefix="upgrade-leftovers-collide-") as tmp:
    root = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(root, "docs", "dev", "_templates"))
    os.makedirs(os.path.join(root, "docs", "dev", ".devflow-baseline", "_templates"))
    live_leftover = os.path.join(root, "docs", "dev", "_templates", "CONTEXT.md")
    baseline_leftover = os.path.join(
        root, "docs", "dev", ".devflow-baseline", "_templates", "CONTEXT.md"
    )
    fixed_stamp = "20990101-000000"
    first_body = "FIRST custom version\n"
    baseline_body = "出廠原版\n"

    open(live_leftover, "w", encoding="utf-8").write(first_body)
    open(baseline_leftover, "w", encoding="utf-8").write(baseline_body)
    first_applied = run(root, "--apply", stamp=fixed_stamp)
    expect(
        "撞名案 run 1:--apply 成功搬第一份客製版",
        first_applied.returncode == 0
        and len(find_trash_files(root)) == 1,
        (first_applied.stdout or "") + (first_applied.stderr or ""),
    )

    # 第二次退役:同一相對路徑,重新種一份不同內容的客製檔,強迫同一 stamp。
    second_body = "SECOND custom version\n"
    open(live_leftover, "w", encoding="utf-8").write(second_body)
    open(baseline_leftover, "w", encoding="utf-8").write(baseline_body)
    second_applied = run(root, "--apply", stamp=fixed_stamp)

    trashed_files = sorted(find_trash_files(root))
    trashed_bodies = sorted(
        open(p, encoding="utf-8").read() for p in trashed_files
    )
    expect(
        "撞名案:run 2 exit 0 且沒有靜默吞掉第一份",
        second_applied.returncode == 0
        and len(trashed_files) == 2
        and trashed_bodies == sorted([first_body, second_body]),
        "trash 檔案:%r\n內容:%r\nstdout:%s" % (
            trashed_files,
            trashed_bodies,
            second_applied.stdout,
        ),
    )
    original_dest = os.path.join(
        root, "docs", "dev", ".devflow-upgrade-trash", fixed_stamp,
        "docs", "dev", "_templates", "CONTEXT.md",
    )
    uniquified = [p for p in trashed_files if p != original_dest]
    expect(
        "撞名案:第二份改用唯一化後綴落點,且 stdout 印出該實際落點",
        len(uniquified) == 1
        and os.path.relpath(uniquified[0], root) in second_applied.stdout,
        "trash 檔案:%r\nstdout:%s" % (trashed_files, second_applied.stdout),
    )

if passed < MIN_CASES:
    print(
        "⛔ 實際只跑了 %d 案(地板 %d)" % (passed + failed, MIN_CASES),
        file=sys.stderr,
    )
    sys.exit(1)
if failed:
    print("⛔ test-upgrade-leftovers: %d 案失敗" % failed, file=sys.stderr)
    sys.exit(1)
print("✅ test-upgrade-leftovers: %d 案全過" % passed)
sys.exit(0)
PY
