#!/bin/bash
# test-devstage3-graph.sh — check-devstage3-graph.sh 的負向牙
#
# 對照組是一份最小合法 graph(九真節點 + 分叉 S0-question)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有一份「舊實作(單一 SKILL、沒有 graph)」fixture,必須紅 ——
# 這就是「先寫測試、舊實作先紅」的永久牙齒,不是散文。
# 第二刀:skill-legacy 團塊必須紅;S3 才准 write_decision。
#
# 用法:scripts/test-devstage3-graph.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-devstage3-graph.sh"
FIX="$SELF_DIR/fixtures/devstage3-graph"
[ -x "$CHECK" ] || chmod +x "$CHECK"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }
[ -d "$FIX/good" ] || { echo "FATAL: 找不到 $FIX/good" >&2; exit 2; }
[ -d "$FIX/old-skill" ] || { echo "FATAL: 找不到 $FIX/old-skill" >&2; exit 2; }

python3 - "$ROOT" "$CHECK" "$FIX" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root, check, fix = sys.argv[1], sys.argv[2], sys.argv[3]
passed = 0
failed = 0


def run_check(tree, extra=None):
    cmd = ["bash", check]
    if extra:
        cmd.extend(extra)
    cmd.append(tree)
    return subprocess.run(cmd, capture_output=True, text=True)


def seed(tmp):
    shutil.copytree(os.path.join(fix, "good"), tmp, dirs_exist_ok=True)


def expect(label, tree, want_rc, needle=None, extra=None):
    global passed, failed
    proc = run_check(tree, extra)
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == want_rc
    if ok and needle and needle not in blob:
        ok = False
        blob += f"\n[test] 期望輸出含 {needle!r}"
    if ok:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        print(f"  ✗ {label} (rc={proc.returncode} want={want_rc})", file=sys.stderr)
        print(blob[-800:], file=sys.stderr)


ZERO_HIT = """---
feature: fixture-slug
stage: 3-prototype
status: draft
---

# 3. 原型 — fixture

## Stage 3 觸發判定(條件式必要)
- [ ] 有新的前端流程
- [ ] 改變使用者下一步
- [ ] 涉及角色交接
- [ ] 涉及人工核准
- [ ] 涉及等待/退回/逾時
- [ ] 涉及權限差異
- [ ] 涉及系統外動作
- [ ] 涉及多種可行互動設計
- [ ] Stage 1 尚有操作流程不確定性
"""


with tempfile.TemporaryDirectory(prefix="devstage3-graph-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(九真節點)必須綠", good, 0)

    old = os.path.join(tmpbase, "old")
    shutil.copytree(os.path.join(fix, "old-skill"), old)
    expect(
        "G-old 舊實作(單一 SKILL、沒有 graph)必須紅",
        old,
        1,
        "沒有 graph",
    )

    case = os.path.join(tmpbase, "missing-entry")
    seed(case)
    n1 = os.path.join(case, "skills", "dev-flow", "stage3", "nodes", "N1-trigger.md")
    text = open(n1, encoding="utf-8").read().replace("## 進條件", "## 入口備註")
    open(n1, "w", encoding="utf-8").write(text)
    expect("P0 真節點缺進條件必須紅", case, 1, "進條件")

    case = os.path.join(tmpbase, "missing-done")
    seed(case)
    n1 = os.path.join(case, "skills", "dev-flow", "stage3", "nodes", "N1-trigger.md")
    text = open(n1, encoding="utf-8").read().replace("## 完成條件", "## 收尾備註")
    open(n1, "w", encoding="utf-8").write(text)
    expect("P0 真節點缺完成條件必須紅", case, 1, "完成條件")

    case = os.path.join(tmpbase, "second-md")
    seed(case)
    slug = os.path.join(case, "docs", "dev", "fixture-slug")
    open(os.path.join(slug, "3-prototype-rerun.md"), "w", encoding="utf-8").write("x\n")
    expect("P0 同 slug 第二份 3-prototype*.md 必須紅", case, 1, "3-prototype")

    case = os.path.join(tmpbase, "save-as")
    seed(case)
    graph = os.path.join(case, "skills", "dev-flow", "stage3", "graph.yaml")
    text = open(graph, encoding="utf-8").read().replace(
        "write_mode: overwrite", "write_mode: save_as"
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0 write_mode≠overwrite 必須紅", case, 1, "overwrite")

    case = os.path.join(tmpbase, "zero-hit")
    seed(case)
    proto = os.path.join(case, "docs", "dev", "fixture-slug", "3-prototype.md")
    open(proto, "w", encoding="utf-8").write(ZERO_HIT)
    expect(
        "P0 九條觸發全未命中，卻存在 3-prototype.md 必須紅",
        case,
        1,
        "全未命中",
    )

    actions = os.path.join(fix, "actions")
    expect(
        "P0 N1 已做判定(有命中)仍寫 4-spec 必須紅",
        good,
        1,
        "write_spec",
        extra=["--action", os.path.join(actions, "n1-write-spec.json")],
    )

    expect(
        "P0 N1-trigger 做 write_prototype 必須紅",
        good,
        1,
        "N1-trigger",
        extra=["--action", os.path.join(actions, "n1-write-prototype.json")],
    )

    expect(
        "P0 N-skip 做 write_prototype 必須紅",
        good,
        1,
        "N-skip",
        extra=["--action", os.path.join(actions, "n-skip-write-prototype.json")],
    )

    expect(
        "G-action N3-write-md + 有命中 → write_prototype 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "n3-write-prototype-ok.json")],
    )

    wrote = os.path.join(tmpbase, "cursor")
    os.makedirs(wrote)
    proc = subprocess.run(
        ["bash", check, "--write-cursor", "N1-trigger", "fixture-slug", wrote],
        capture_output=True,
        text=True,
    )
    cursor_path = os.path.join(wrote, ".devstage3-cursor.json")
    ok = proc.returncode == 0 and os.path.isfile(cursor_path)
    data = {}
    if ok:
        data = json.loads(open(cursor_path, encoding="utf-8").read())
        ok = data.get("node") == "N1-trigger"
    if ok:
        passed += 1
        print("  ✓ G-cursor --write-cursor N1-trigger 寫出 .devstage3-cursor.json")
    else:
        failed += 1
        print("  ✗ G-cursor --write-cursor 沒寫出游標檔", file=sys.stderr)
        print((proc.stdout or "") + (proc.stderr or ""), file=sys.stderr)

    case = os.path.join(tmpbase, "s0-no-cursor-call")
    seed(case)
    s0 = os.path.join(
        case, "skills", "dev-flow", "stage3", "nodes", "S0-question.md"
    )
    text = open(s0, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(s0, "w", encoding="utf-8").write(text)
    expect("P0 S0 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "s3-no-cursor-call")
    seed(case)
    s3 = os.path.join(
        case, "skills", "dev-flow", "stage3", "nodes", "S3-writeback.md"
    )
    text = open(s3, encoding="utf-8").read().replace("--write-cursor", "--no-cursor-call")
    open(s3, "w", encoding="utf-8").write(text)
    expect("P0 S3 缺 --write-cursor 必須紅", case, 1, "--write-cursor")

    case = os.path.join(tmpbase, "missing-s0")
    seed(case)
    os.remove(
        os.path.join(case, "skills", "dev-flow", "stage3", "nodes", "S0-question.md")
    )
    expect("P0 缺 S0-question 節點檔必須紅", case, 1, "S0-question")

    case = os.path.join(tmpbase, "legacy-blob")
    seed(case)
    graph = os.path.join(case, "skills", "dev-flow", "stage3", "graph.yaml")
    text = open(graph, encoding="utf-8").read()
    text = text.replace(
        "    fork_required: S0-question\n",
        "    fork_required: skill-legacy-0-2\n",
    )
    text = text.replace(
        "  S0-question:\n    file: nodes/S0-question.md\n    next: S1-experiment\n"
        "    forbid:\n      - write_prototype\n      - write_decision\n",
        "  skill-legacy-0-2:\n    kind: skill-legacy\n    next: S1-experiment\n"
        "    forbid:\n      - write_prototype\n",
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0 skill-legacy 團塊仍在必須紅", case, 1, "skill-legacy")

    expect(
        "P0 S3 + 有命中 → write_decision 必須綠",
        good,
        0,
        "allow",
        extra=["--action", os.path.join(actions, "s3-write-decision-ok.json")],
    )
    expect(
        "P0 N1 不得 write_decision",
        good,
        1,
        "N1-trigger",
        extra=["--action", os.path.join(actions, "n1-write-decision.json")],
    )
    expect(
        "P0 N3 不得 write_decision",
        good,
        1,
        "N3-write-md",
        extra=["--action", os.path.join(actions, "n3-write-decision.json")],
    )
    expect(
        "P0 S0 不得 write_decision",
        good,
        1,
        "S0-question",
        extra=["--action", os.path.join(actions, "s0-write-decision.json")],
    )

    case = os.path.join(tmpbase, "s3-no-allow")
    seed(case)
    graph = os.path.join(case, "skills", "dev-flow", "stage3", "graph.yaml")
    text = open(graph, encoding="utf-8").read()
    text = text.replace(
        "  S3-writeback:\n    file: nodes/S3-writeback.md\n    next: S4-close\n"
        "    write:\n      - docs/dev/<slug>/2-decision.md\n"
        "    write_mode: overwrite\n    allow:\n      - write_decision\n"
        "    forbid:\n      - write_prototype\n",
        "  S3-writeback:\n    file: nodes/S3-writeback.md\n    next: S4-close\n"
        "    forbid:\n      - write_decision\n",
    )
    open(graph, "w", encoding="utf-8").write(text)
    expect("P0 S3 缺 allow write_decision 必須紅", case, 1, "S3-writeback")

total = passed + failed
print(f"=== test-devstage3-graph:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < 16:
    print(f"⛔ 案例數 {total} < 16,牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
