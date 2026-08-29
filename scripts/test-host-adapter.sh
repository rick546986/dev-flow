#!/bin/bash
# test-host-adapter.sh — check-host-adapter.sh 的負向牙
# 第一刀:DEVFLOW_ROOT + 薄殼 + 節點可讀
# 第二刀:採用專案掛整棵(setup 宣稱 / AGENTS.md / 技能連結 / 乘客清單)
# 第三刀:主機探測 + 誰跑 --action(非 Claude 不當唯一進條件;既有 deny 仍紅)
# 第四刀:Grok／Codex 沒技能樹必須紅;--probe 印一句掛載句
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
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

root, check, fix = sys.argv[1], sys.argv[2], sys.argv[3]
passed = 0
failed = 0
MIN_CASES = 54


def run_check(tree, extra_env=None, drop=None, probe=False, cwd=None):
    env = os.environ.copy()
    env.pop("DEVFLOW_ROOT", None)
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    if drop:
        for name in drop:
            env.pop(name, None)
    if extra_env:
        env.update(extra_env)
    cmd = ["bash", check]
    if probe:
        cmd.append("--probe")
    if tree:
        cmd.append(tree)
    return subprocess.run(
        cmd, capture_output=True, text=True, env=env, cwd=cwd
    )


def seed(tmp):
    shutil.copytree(os.path.join(fix, "good"), tmp, dirs_exist_ok=True)


def expect(
    label,
    tree,
    want_rc,
    needle=None,
    extra_env=None,
    probe=False,
    cwd=None,
    forbid=None,
):
    global passed, failed
    proc = run_check(tree, extra_env=extra_env, probe=probe, cwd=cwd)
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == want_rc
    if ok and needle and needle not in blob:
        ok = False
        blob += f"\n[test] 期望輸出含 {needle!r}"
    if ok and forbid:
        # 整行比對:FAIL 句提到「不得 probe: ok」不算成功狀態行
        lines = [ln.strip() for ln in blob.splitlines()]
        if forbid in lines:
            ok = False
            blob += f"\n[test] 不該出現整行 {forbid!r}"
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


def write_host(tree, name):
    open(os.path.join(tree, ".devflow-host"), "w", encoding="utf-8").write(
        name + "\n"
    )


def link_dv(tree, pack, hosts):
    for host in hosts:
        base = os.path.join(tree, host)
        os.makedirs(base, exist_ok=True)
        for name in ("dev-setup", "dev-talk", "dev-flow", "dev-run"):
            dest = os.path.join(base, name)
            if os.path.lexists(dest):
                continue
            os.symlink(os.path.join(pack, "skills", name), dest)


def write_cursor_rules(tree):
    rules = os.path.join(tree, ".cursor", "rules")
    os.makedirs(rules, exist_ok=True)
    open(os.path.join(rules, "devflow-arch.mdc"), "w", encoding="utf-8").write(
        "架構不變量見方法包 `_templates/arch-invariants.md`。"
        "不要把流程規則貼進本檔。\n"
    )


def write_agents_pointer(tree):
    open(os.path.join(tree, "AGENTS.md"), "w", encoding="utf-8").write(
        "這專案用 DevFlow。技能在方法包 skills/。開工讀該技能 SKILL.md，"
        "下一跳看 graph.yaml。不要把流程規則貼進本檔。\n"
    )


def expect_stage_deny(label, script_rel, fixture_rel, action_rel, needle):
    global passed, failed
    script = os.path.join(root, script_rel)
    src = os.path.join(root, fixture_rel)
    action = os.path.join(root, action_rel)
    if not (
        os.path.isfile(script) and os.path.isdir(src) and os.path.isfile(action)
    ):
        failed += 1
        print(f"  ✗ {label} (治具缺檔)", file=sys.stderr)
        return
    tree = os.path.join(
        tmpbase, "deny-" + re.sub(r"[^A-Za-z0-9]+", "-", label)
    )
    if os.path.exists(tree):
        shutil.rmtree(tree)
    shutil.copytree(src, tree)
    proc = subprocess.run(
        ["bash", script, "--action", action, tree],
        capture_output=True,
        text=True,
    )
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    ok = proc.returncode == 1
    if ok and needle and needle not in blob:
        ok = False
        blob += f"\n[test] 期望輸出含 {needle!r}"
    if ok:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        print(
            f"  ✗ {label} (rc={proc.returncode} want=1)",
            file=sys.stderr,
        )
        print(blob[-1200:], file=sys.stderr)


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
    write_agents_pointer(linked)
    link_dv(
        linked,
        good,
        (".cursor/skills", ".agents/skills"),
    )
    write_cursor_rules(linked)
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

    case = os.path.join(tmpbase, "non-claude-gates")
    seed(case)
    setup = os.path.join(case, "skills", "dev-setup", "SKILL.md")
    open(setup, "a", encoding="utf-8").write(
        "\n## 主機探測\n"
        "所有主機健檢都必須 AskUserQuestion 與 enabledPlugins。"
        "hooks.json 是唯一進條件。不先探測主機。\n"
    )
    write_host(case, "cursor")
    expect(
        "R-non-claude-gates 非 Claude 仍把 AskUserQuestion／enabledPlugins 當唯一進條件必須紅",
        case,
        1,
        "AskUserQuestion",
    )

    case = os.path.join(tmpbase, "guide-no-host")
    seed(case)
    gdir = os.path.join(case, "guides")
    os.makedirs(gdir)
    open(os.path.join(gdir, "guide-dev-flow.html"), "w", encoding="utf-8").write(
        "<html><h2 id=\"filemap\">檔案地圖</h2><p>沒有主機節。</p></html>\n"
    )
    expect(
        "R-guide-no-host guide 沒有 #host 必須紅",
        case,
        1,
        "#host",
    )

    case = os.path.join(tmpbase, "readme-dump")
    seed(case)
    open(os.path.join(case, "README.md"), "w", encoding="utf-8").write(
        "# 流程刀序\n"
        "第一刀 第二刀 第三刀。Cursor 與 Codex。\n"
        "AskUserQuestion。`.cursor/skills` 與 `.agents/skills`。\n"
    )
    expect(
        "R-readme-dump README 灌進流程／刀序必須紅",
        case,
        1,
        "刀序",
    )

    claude = os.path.join(tmpbase, "host-claude")
    shutil.copytree(os.path.join(fix, "no-root"), claude)
    write_host(claude, "claude")
    os.makedirs(os.path.join(claude, ".claude"), exist_ok=True)
    open(
        os.path.join(claude, ".claude", "settings.json"),
        "w",
        encoding="utf-8",
    ).write('{"enabledPlugins":{"dev-flow@dev-flow":true}}\n')
    expect(
        "G-claude Claude fixture 舊檢查仍可走必須綠",
        claude,
        0,
        "old-checks: ok",
        extra_env={"DEVFLOW_ROOT": root},
    )

    cursor = os.path.join(tmpbase, "host-cursor")
    shutil.copytree(os.path.join(fix, "no-root"), cursor)
    write_host(cursor, "cursor")
    link_dv(cursor, good, (".cursor/skills",))
    expect(
        "G-cursor Cursor fixture 只靠技能目錄 + DEVFLOW_ROOT 必須綠",
        cursor,
        0,
        "setup-health: skill-dirs+DEVFLOW_ROOT",
        extra_env={"DEVFLOW_ROOT": root},
    )

    codex = os.path.join(tmpbase, "host-codex")
    shutil.copytree(os.path.join(fix, "no-root"), codex)
    write_host(codex, "codex")
    link_dv(codex, good, (".agents/skills",))
    expect(
        "G-codex Codex fixture 只靠技能目錄 + DEVFLOW_ROOT 必須綠",
        codex,
        0,
        "host=codex",
        extra_env={"DEVFLOW_ROOT": root},
    )

    grok_bare = os.path.join(tmpbase, "host-grok-bare")
    shutil.copytree(os.path.join(fix, "no-root"), grok_bare)
    write_host(grok_bare, "grok")
    os.makedirs(os.path.join(grok_bare, ".grok"), exist_ok=True)
    expect(
        "R-grok-no-tree Grok 開工沒掛 .grok/skills 整棵必須紅",
        grok_bare,
        1,
        "Grok 把",
        extra_env={"DEVFLOW_ROOT": root},
    )
    expect(
        "R-probe-grok-hang --probe 在 Grok 沒技能樹時印一句掛載句",
        grok_bare,
        1,
        "hang: Grok 把",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
    )

    grok = os.path.join(tmpbase, "host-grok")
    shutil.copytree(os.path.join(fix, "no-root"), grok)
    write_host(grok, "grok")
    link_dv(grok, good, (".grok/skills",))
    expect(
        "G-grok Grok fixture 技能目錄整棵 + DEVFLOW_ROOT 必須綠",
        grok,
        0,
        "host=grok",
        extra_env={"DEVFLOW_ROOT": root},
    )
    expect(
        "G-probe-grok-ok --probe 在 Grok 已掛整棵時必須綠",
        grok,
        0,
        "不要發明 Grok marketplace",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
    )

    expect(
        "G-probe-cursor-ok --probe 不改 Cursor 薄殼（整棵連結）必須綠",
        cursor,
        0,
        "已匯入的 rick546986/dev-flow",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
    )

    expect(
        "G-probe-claude-ok --probe 不改 Claude 舊路必須綠",
        claude,
        0,
        "/plugin marketplace add rick546986/dev-flow",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
    )

    codex_bare = os.path.join(tmpbase, "host-codex-bare")
    shutil.copytree(os.path.join(fix, "no-root"), codex_bare)
    write_host(codex_bare, "codex")
    os.makedirs(os.path.join(codex_bare, ".codex"), exist_ok=True)
    expect(
        "R-codex-no-tree Codex 開工沒掛 .agents/skills 整棵必須紅",
        codex_bare,
        1,
        "Codex 把",
        extra_env={"DEVFLOW_ROOT": root},
    )

    codex_legacy = os.path.join(tmpbase, "host-codex-legacy")
    shutil.copytree(os.path.join(fix, "no-root"), codex_legacy)
    write_host(codex_legacy, "codex")
    link_dv(codex_legacy, good, (".codex/skills",))
    expect(
        "R-codex-legacy-only 只掛 .codex/skills、沒有 .agents/skills 必須紅",
        codex_legacy,
        1,
        "hang: Codex 把",
        extra_env={"DEVFLOW_ROOT": root},
    )

    codex_split = os.path.join(tmpbase, "host-codex-split")
    shutil.copytree(os.path.join(fix, "no-root"), codex_split)
    write_host(codex_split, "codex")
    link_dv(codex_split, good, (".agents/skills",))
    thin = os.path.join(codex_split, ".codex", "skills", "dev-talk")
    os.makedirs(thin)
    open(os.path.join(thin, "SKILL.md"), "w", encoding="utf-8").write("# talk\n")
    expect(
        "R-codex-dual-split .codex/skills 薄殼與 .agents/skills 不是同一包必須紅",
        codex_split,
        1,
        "同一包",
        extra_env={"DEVFLOW_ROOT": root},
    )

    codex_dual = os.path.join(tmpbase, "host-codex-dual")
    shutil.copytree(os.path.join(fix, "no-root"), codex_dual)
    write_host(codex_dual, "codex")
    link_dv(codex_dual, good, (".agents/skills", ".codex/skills"))
    expect(
        "G-codex-dual .agents/skills 與 .codex/skills 掛同一棵必須綠",
        codex_dual,
        0,
        "host=codex",
        extra_env={"DEVFLOW_ROOT": root},
    )

    bad_root = os.path.join(tmpbase, "not-pack")
    os.makedirs(bad_root)
    open(os.path.join(bad_root, "README.md"), "w", encoding="utf-8").write(
        "not a pack\n"
    )
    expect(
        "R-probe-bad-root --probe 遇上錯的 DEVFLOW_ROOT 必須紅且印 hang",
        grok_bare,
        1,
        "hang: DEVFLOW_ROOT 不對",
        extra_env={"DEVFLOW_ROOT": bad_root},
        probe=True,
    )

    # 第 4 型假綠牙齒:今日 main 無參數 --probe 的 tree="" → missing=[] →
    # probe: ok / exit 0,與被檢查專案無關。採用樹／空樹必須紅或印未檢查;
    # 方法包 repo 無參數是自檢,不准共用 probe: ok。
    probe_adopter = os.path.join(tmpbase, "probe-no-root-adopter")
    shutil.copytree(os.path.join(fix, "no-root"), probe_adopter)
    os.makedirs(os.path.join(probe_adopter, ".cursor"), exist_ok=True)
    os.makedirs(os.path.join(probe_adopter, "docs", "dev"), exist_ok=True)
    expect(
        "R-probe-no-root-adopter 採用樹無參數 --probe 不得 probe: ok（空樹假綠）",
        "",
        1,
        "缺專案根",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
        cwd=probe_adopter,
        forbid="probe: ok",
    )

    empty_cwd = os.path.join(tmpbase, "probe-empty-cwd")
    os.makedirs(empty_cwd)
    expect(
        "R-probe-empty-tree 空樹 cwd 無參數 --probe 不得 probe: ok",
        "",
        1,
        "未檢查",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
        cwd=empty_cwd,
        forbid="probe: ok",
    )

    expect(
        "G-probe-pack-self 方法包 repo 無參數 --probe 是自檢不是採用探測",
        "",
        0,
        "probe: pack-self-check",
        extra_env={"DEVFLOW_ROOT": root},
        probe=True,
        cwd=root,
        forbid="probe: ok",
    )

    expect_stage_deny(
        "R-action-s2 第 2 站既有 deny（N1 write_decision）必須仍紅",
        "scripts/check-devstage2-graph.sh",
        "scripts/fixtures/devstage2-graph/good",
        "scripts/fixtures/devstage2-graph/actions/n1-write-decision.json",
        "N1-handoff",
    )
    expect_stage_deny(
        "R-action-s3 第 3 站既有 deny（N1 write_prototype）必須仍紅",
        "scripts/check-devstage3-graph.sh",
        "scripts/fixtures/devstage3-graph/good",
        "scripts/fixtures/devstage3-graph/actions/n1-write-prototype.json",
        "N1-trigger",
    )
    expect_stage_deny(
        "R-action-s4 第 4 站既有 deny（N1 write_spec）必須仍紅",
        "scripts/check-devstage4-graph.sh",
        "scripts/fixtures/devstage4-graph/good",
        "scripts/fixtures/devstage4-graph/actions/n1-write-spec.json",
        "N1-handoff",
    )
    expect_stage_deny(
        "R-action-s5 第 5 站既有 deny（N1 write_tasks）必須仍紅",
        "scripts/check-devstage5-graph.sh",
        "scripts/fixtures/devstage5-graph/good",
        "scripts/fixtures/devstage5-graph/actions/n1-write-tasks.json",
        "N1-handoff",
    )
    expect_stage_deny(
        "R-action-s6 第 6 站既有 deny（N2 write_notes）必須仍紅",
        "scripts/check-devstage6-graph.sh",
        "scripts/fixtures/devstage6-graph/good",
        "scripts/fixtures/devstage6-graph/actions/n2-write-notes.json",
        "N2-handoff",
    )
    expect_stage_deny(
        "R-action-s7 第 7 站既有 deny（N0 write_review）必須仍紅",
        "scripts/check-devstage7-graph.sh",
        "scripts/fixtures/devstage7-graph/good",
        "scripts/fixtures/devstage7-graph/actions/n0-write-review.json",
        "N0-role",
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
