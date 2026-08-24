#!/bin/bash
# test-host-adapter.sh — check-host-adapter.sh 的負向牙
# 第一刀:DEVFLOW_ROOT + 薄殼 + 節點可讀
# 第二刀:採用專案掛整棵(setup 宣稱 / AGENTS.md / 技能連結 / 乘客清單)
#
# 對照組是一份最小合法方法包(DEVFLOW_ROOT 形狀齊、talk/flow 掛整棵)。
# 每個案例把對照組改壞一次,確認檢查真的紅。
# 另有「只有 SKILL.md」與「推不到根」fixture —— 這就是「先寫測試、舊實作先紅」
# 的永久牙齒,不是散文。
#
# 用法:scripts/test-host-adapter.sh [root]
# exit:0 = 全過 / 1 = 案例未依預期 / 2 = 治具故障

set -uo pipefail

SELF_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

CHECK="$SELF_DIR/check-host-adapter.sh"
FIX="$SELF_DIR/fixtures/host-adapter"
[ -x "$CHECK" ] || chmod +x "$CHECK"
[ -f "$CHECK" ] || { echo "FATAL: 找不到 $CHECK" >&2; exit 2; }
[ -d "$FIX/good" ] || { echo "FATAL: 找不到 $FIX/good" >&2; exit 2; }
[ -d "$FIX/skill-only" ] || { echo "FATAL: 找不到 $FIX/skill-only" >&2; exit 2; }
[ -d "$FIX/no-root" ] || { echo "FATAL: 找不到 $FIX/no-root" >&2; exit 2; }
[ -d "$FIX/setup-claimed" ] || { echo "FATAL: 找不到 $FIX/setup-claimed" >&2; exit 2; }

python3 - "$ROOT" "$CHECK" "$FIX" <<'PY'
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
MIN_CASES = 24


def run_check(tree, extra_env=None, drop=None):
    env = os.environ.copy()
    env.pop("DEVFLOW_ROOT", None)
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    if drop:
        for name in drop:
            env.pop(name, None)
    if extra_env:
        env.update(extra_env)
    cmd = ["bash", check]
    if tree:
        cmd.append(tree)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def seed(tmp):
    shutil.copytree(os.path.join(fix, "good"), tmp, dirs_exist_ok=True)


def expect(label, tree, want_rc, needle=None, extra_env=None):
    global passed, failed
    proc = run_check(tree, extra_env=extra_env)
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
        print(blob[-1200:], file=sys.stderr)


def patch(path, old, new):
    text = open(path, encoding="utf-8").read()
    if old not in text:
        print(f"FATAL: 治具找不到待改字串 {old!r} in {path}", file=sys.stderr)
        sys.exit(2)
    open(path, "w", encoding="utf-8").write(text.replace(old, new, 1))


with tempfile.TemporaryDirectory(prefix="host-adapter-test-") as tmpbase:
    good = os.path.join(tmpbase, "good")
    shutil.copytree(os.path.join(fix, "good"), good)
    expect("G-0 對照組(方法包形狀齊、節點可讀)必須綠", good, 0)

    expect(
        "G-devflow-only 不設 CLAUDE_PLUGIN_ROOT、只設 DEVFLOW_ROOT 必須綠",
        good,
        0,
        "N1-start.md",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-memory 只設 DEVFLOW_ROOT 時記憶指令組得出 memory/dev-memory.py",
        good,
        0,
        "memory/dev-memory.py",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-stage4 STATUS 在第 4 站 → 讀得到 stage4/graph.yaml",
        good,
        0,
        "stage4/graph.yaml",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-stage4-node 讀得到 N1-handoff.md",
        good,
        0,
        "N1-handoff.md",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-stage6 第 6 站鏈每個真節點檔在",
        good,
        0,
        "N1-arm.md",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-stage7 第 7 站鏈每個真節點檔在",
        good,
        0,
        "N0-role.md",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-alias 只設 CLAUDE_PLUGIN_ROOT 舊名必須綠",
        good,
        0,
        "DEVFLOW_ROOT=",
        extra_env={"CLAUDE_PLUGIN_ROOT": good},
    )

    old = os.path.join(tmpbase, "skill-only")
    shutil.copytree(os.path.join(fix, "skill-only"), old)
    expect(
        "R-skill-only 技能目錄只有 SKILL.md、沒有 graph.yaml 或 nodes 必須紅",
        old,
        1,
        "SKILL.md",
    )

    no_root = os.path.join(tmpbase, "no-root")
    shutil.copytree(os.path.join(fix, "no-root"), no_root)
    expect(
        "R-no-root 不設 DEVFLOW_ROOT 也不設 CLAUDE_PLUGIN_ROOT、推不到根必須紅",
        no_root,
        1,
        "方法包沒掛上",
    )

    adopter = os.path.join(tmpbase, "adopter")
    shutil.copytree(os.path.join(fix, "no-root"), adopter)
    expect(
        "G-adopter 產品 repo 沒有 skills/、DEVFLOW_ROOT 指向方法包必須綠",
        adopter,
        0,
        "N1-start.md",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-adopter-s4 產品沒 skills/、DEVFLOW_ROOT 指向方法包 → 讀得到第 4 站 N1-handoff.md",
        adopter,
        0,
        "stage4/nodes/N1-handoff.md",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "R-adopter-silent 沒有 DEVFLOW_ROOT、產品也沒方法包必須大聲失敗",
        adopter,
        1,
        "方法包沒掛上",
    )

    claimed = os.path.join(tmpbase, "setup-claimed")
    shutil.copytree(os.path.join(fix, "setup-claimed"), claimed)
    expect(
        "R-setup-claimed setup 宣稱成功但 DEVFLOW_ROOT 推不到、產品也沒方法包必須紅",
        claimed,
        1,
        "setup 宣稱成功",
    )

    case = os.path.join(tmpbase, "cursor-thin")
    shutil.copytree(os.path.join(fix, "no-root"), case)
    thin = os.path.join(case, ".cursor", "skills", "dev-talk")
    os.makedirs(thin)
    open(os.path.join(thin, "SKILL.md"), "w", encoding="utf-8").write("# talk\n")
    expect(
        "R-cursor-thin .cursor/skills/dev-talk 只有 SKILL.md、沒有 graph.yaml／nodes 必須紅",
        case,
        1,
        "SKILL.md",
        extra_env={"DEVFLOW_ROOT": good},
    )

    case = os.path.join(tmpbase, "agents-thin")
    shutil.copytree(os.path.join(fix, "no-root"), case)
    thin = os.path.join(case, ".agents", "skills", "dev-talk")
    os.makedirs(thin)
    open(os.path.join(thin, "SKILL.md"), "w", encoding="utf-8").write("# talk\n")
    expect(
        "R-agents-thin .agents/skills/dev-talk 只有 SKILL.md、沒有 graph.yaml／nodes 必須紅",
        case,
        1,
        "SKILL.md",
        extra_env={"DEVFLOW_ROOT": good},
    )

    case = os.path.join(tmpbase, "agents-dump")
    seed(case)
    open(os.path.join(case, "AGENTS.md"), "w", encoding="utf-8").write(
        "# 流程規則\n\n"
        "這專案用 DevFlow。技能在方法包 skills/。開工讀該技能 SKILL.md，"
        "下一跳看 graph.yaml。不要把流程規則貼進本檔。\n\n"
        "## G1\n盲原則。AskUserQuestion。enabledPlugins。執行清單 0-11。\n"
        "skill-legacy 團塊。G2 G3。\n"
    )
    expect(
        "R-agents-md-dump AGENTS.md 被灌進流程規則必須紅",
        case,
        1,
        "AGENTS.md",
    )

    case = os.path.join(tmpbase, "passenger")
    seed(case)
    n1 = os.path.join(
        case, "skills", "dev-flow", "stage4", "nodes", "N1-handoff.md"
    )
    open(n1, "w", encoding="utf-8").write(
        "# N1-handoff\n"
        "乘客清單正本是 `docs/dev/_templates/4-spec.md` 頂註 0–6。\n"
    )
    expect(
        "R-passenger 節點把乘客清單寫成只找產品 docs/dev/_templates/ 必須紅",
        case,
        1,
        "docs/dev/_templates",
    )

    case = os.path.join(tmpbase, "setup-skip")
    seed(case)
    setup = os.path.join(case, "skills", "dev-setup", "SKILL.md")
    open(setup, "a", encoding="utf-8").write(
        "\n## install\n只散發 docs/dev/ 就算成功。不解析 DEVFLOW_ROOT。\n"
    )
    expect(
        "R-setup-skill-skip setup ## install 不寫解析失敗要大聲停必須紅",
        case,
        1,
        "大聲停",
    )

    case = os.path.join(tmpbase, "setup-done-no-links")
    shutil.copytree(os.path.join(fix, "setup-claimed"), case)
    expect(
        "R-setup-done-no-links setup 宣稱成功（有 DEVFLOW_ROOT）但沒掛整棵必須紅",
        case,
        1,
        "不是整棵目錄",
        extra_env={"DEVFLOW_ROOT": good},
    )

    linked = os.path.join(tmpbase, "adopter-linked")
    shutil.copytree(os.path.join(fix, "setup-claimed"), linked)
    open(os.path.join(linked, "AGENTS.md"), "w", encoding="utf-8").write(
        "這專案用 DevFlow。技能在方法包 skills/。開工讀該技能 SKILL.md，"
        "下一跳看 graph.yaml。不要把流程規則貼進本檔。\n"
    )
    for host in (".cursor/skills", ".agents/skills"):
        base = os.path.join(linked, host)
        os.makedirs(base, exist_ok=True)
        for name in ("dev-setup", "dev-talk", "dev-flow", "dev-run"):
            os.symlink(
                os.path.join(good, "skills", name),
                os.path.join(base, name),
            )
    expect(
        "G-dv-links 四個 DV 的連結目標都是整棵目錄必須綠",
        linked,
        0,
        "link-whole: .cursor/skills/dev-flow",
        extra_env={"DEVFLOW_ROOT": good},
    )
    expect(
        "G-agents-pointer 採用專案 AGENTS.md 一行指標必須綠",
        linked,
        0,
        "agents-pointer: ok",
        extra_env={"DEVFLOW_ROOT": good},
    )

    case = os.path.join(tmpbase, "missing-file")
    seed(case)
    patch(
        os.path.join(case, "skills", "dev-talk", "graph.yaml"),
        "file: nodes/N1-start.md",
        "file: nodes/N1-missing.md",
    )
    expect(
        "R-file graph.yaml 的 file: 相對技能目錄打不開必須紅",
        case,
        1,
        "file:",
    )

    case = os.path.join(tmpbase, "legacy-entry")
    seed(case)
    graph = os.path.join(case, "skills", "dev-talk", "graph.yaml")
    open(graph, "a", encoding="utf-8").write(
        "  leftover:\n"
        "    kind: skill-legacy\n"
        "    entry: skills/does-not-exist/SKILL.md\n"
    )
    expect(
        "R-legacy kind: skill-legacy 的 entry 相對 DEVFLOW_ROOT 打不開必須紅",
        case,
        1,
        "skill-legacy",
    )

    case = os.path.join(tmpbase, "plugin-root")
    seed(case)
    n1 = os.path.join(case, "skills", "dev-talk", "nodes", "N1-start.md")
    open(n1, "w", encoding="utf-8").write(
        "# N1-start\n"
        "跑 `${CLAUDE_PLUGIN_ROOT}/memory/dev-memory.py talk start \"x\"`。\n"
    )
    expect(
        "R-alias N1-start 寫死 ${CLAUDE_PLUGIN_ROOT} 且沒宣告別名必須紅",
        case,
        1,
        "CLAUDE_PLUGIN_ROOT",
    )

    case = os.path.join(tmpbase, "skill-tool")
    seed(case)
    flow = os.path.join(case, "skills", "dev-flow", "SKILL.md")
    open(flow, "w", encoding="utf-8").write(
        "# dev-flow\n"
        "方法包根目錄叫 `DEVFLOW_ROOT`（舊名 `CLAUDE_PLUGIN_ROOT` 當別名）。\n"
        "- stage = 6 → 用 Skill tool 自動載入 `dev-run` 引擎\n"
    )
    expect(
        "R-skill-tool Skill tool 載入 dev-run 不寫讀哪份 MD 必須紅",
        case,
        1,
        "dev-run",
    )

    case = os.path.join(tmpbase, "subagent")
    seed(case)
    run_skill = os.path.join(case, "skills", "dev-run", "SKILL.md")
    open(run_skill, "w", encoding="utf-8").write(
        "# dev-run\n"
        "方法包根目錄叫 `DEVFLOW_ROOT`（舊名 `CLAUDE_PLUGIN_ROOT` 當別名）。\n"
        "以 `subagent_type=dev-flow:devflow-reviewer` 派出。\n"
    )
    expect(
        "R-subagent subagent_type=dev-flow:devflow-reviewer 不寫讀哪份 MD 必須紅",
        case,
        1,
        "devflow-reviewer",
    )

    expect(
        "G-live 本 repo 只設 DEVFLOW_ROOT 必須綠(產品)",
        root,
        0,
        "N1-start.md",
        extra_env={"DEVFLOW_ROOT": root},
    )

total = passed + failed
print(f"=== test-host-adapter:{passed}/{total} ===")
if failed:
    print(f"⛔ {failed} 案未依預期", file=sys.stderr)
    sys.exit(1)
if total < MIN_CASES:
    print(f"⛔ 案例數 {total} < {MIN_CASES},牙齒沒跑齊", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
PY
