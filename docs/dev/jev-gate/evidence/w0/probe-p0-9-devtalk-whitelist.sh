#!/bin/bash
# probe-p0-9-devtalk-whitelist.sh — W0 P0-9:dev-talk「讀取白名單」對舊 1-discussion.md 路徑
# 有沒有任何機械執行點;以及 dev-flow 武裝期對 1-discussion 的 Read 禁令(圍欄②)。
# 用法:bash probe-p0-9-devtalk-whitelist.sh <dev-flow pack root>
set -u
PACK=$(cd "${1:-.}" && pwd); H="$PACK/hooks"
T=$(mktemp -d "${TMPDIR:-/tmp}/p09-devtalk.XXXXXX"); trap 'rm -rf "$T"' EXIT
J() { python3 -c 'import json,sys;print(json.dumps(dict(step=sys.argv[1], rc=int(sys.argv[2]), out=sys.argv[3][-600:]), ensure_ascii=False))' "$1" "$2" "$3"; }
mkdir -p "$T/docs/dev/old-slug" "$T/docs/dev/f1" "$T/src"; cd "$T" || exit 2
git init -q . && git config user.email p@p && git config user.name p
printf -- '---\nfeature: old-slug  stage: 1-discussion  status: approved\n---\n# old discussion\n' > docs/dev/old-slug/1-discussion.md
printf -- "---\nstatus: approved\n---\n" > docs/dev/f1/4-spec.md
printf '%s\n' '## T-1 p' '- Covers: R-1' '- Files: src/a.py' '- Verify: `true`' '- Blocked-by: —' > docs/dev/f1/5-tasks.md
echo a > src/a.py; git add -A >/dev/null; git commit -qm init
RD() { printf '{"tool_name":"Read","tool_input":{"file_path":"%s"}}' "$T/$1"; }

# ① hooks.json:devtalk-guard 掛在哪個 matcher?(Read 分支能不能被觸發)
OUT=$(python3 - "$H/hooks.json" <<'PY'
import json,sys
h=json.load(open(sys.argv[1]))["hooks"]
rows=[]
for phase, entries in h.items():
    for e in entries:
        for hk in e["hooks"]:
            if "devtalk-guard" in hk["command"] or "devflow-guard" in hk["command"]:
                rows.append({"phase": phase, "matcher": e["matcher"], "hook": hk["command"].split("/")[-1]})
print(json.dumps(rows, ensure_ascii=False))
PY
); J "10-hooks.json wiring of devtalk-guard / devflow-guard" $? "$OUT"

# ② graph.yaml 的 action 詞彙表:有沒有任何 read_* action?
OUT=$(python3 - "$PACK/skills/dev-talk/graph.yaml" <<'PY'
import re,sys
acts=sorted(set(re.findall(r"^\s+-\s+([a-z_]+)\s*$", open(sys.argv[1]).read(), re.M)))
print({"actions": acts, "any_read_action": any(a.startswith("read") for a in acts)})
PY
); J "11-graph.yaml action vocabulary (mechanical --action set)" $? "$OUT"

# ③ 未武裝 + talk 游標在:直接餵 devtalk-guard 一個 Read 舊 1-discussion → 判定?
echo '{"node":"S1-survey","MEMORY_SESSION_ID":"ses_probe"}' > .devtalk-cursor.json
OUT=$(RD docs/dev/old-slug/1-discussion.md | "$H/devtalk-guard.sh" 2>&1); J "20-devtalk-guard(direct) Read old 1-discussion with cursor → silent allow?" $? "$OUT"
OUT=$(RD docs/dev/old-slug/2-decision.md | "$H/devtalk-guard.sh" 2>&1); J "21-devtalk-guard(direct) Read 2-decision with cursor → deny (contrast)" $? "$OUT"
OUT=$(RD docs/dev/old-slug/1-discussion.md | "$H/devflow-guard.sh" 2>&1); J "22-devflow-guard Read old 1-discussion, unarmed → silent" $? "$OUT"
rm -f .devtalk-cursor.json
OUT=$(RD docs/dev/old-slug/1-discussion.md | "$H/devtalk-guard.sh" 2>&1); J "23-devtalk-guard(direct) Read old 1-discussion, no cursor → silent" $? "$OUT"

# ④ dev-flow 武裝(Stage 6)後:任何 slug 的 1-discussion Read 都被圍欄②擋
"$H/devflow-exec.sh" start f1 >/dev/null 2>&1
OUT=$(RD docs/dev/old-slug/1-discussion.md | "$H/devflow-guard.sh" 2>&1); J "30-devflow-guard Read other-slug 1-discussion while armed → deny(圍欄②)" $? "$OUT"
OUT=$(printf '{"tool_name":"Bash","tool_input":{"command":"cat docs/dev/old-slug/1-discussion.md"}}' | "$H/devflow-prebash.sh" 2>&1); J "31-prebash shell read 1-discussion while armed → deny" $? "$OUT"
"$H/devflow-exec.sh" stop >/dev/null 2>&1

# ⑤ 白名單原文與「主動指名」出處行號
OUT=$(cd "$PACK" && grep -n "讀取白名單\|使用者主動指名\|不讀其他 \`docs/dev/<slug>/\`\|同 slug 另開 dev-talk\|一律新 session\|可改已有的" skills/dev-talk/SKILL.md skills/dev-talk/nodes/*.md skills/dev-flow/SKILL.md | head -12); J "40-source lines: whitelist / user-named / same-slug rerun" $? "$OUT"
OUT=$(cd "$PACK" && grep -rn "1-discussion" skills/dev-flow/SKILL.md | grep -c "dev-talk"; cd "$PACK" && grep -n "請他改跑" skills/dev-flow/SKILL.md | head -2); J "41-router(dev-flow SKILL Intake row) hands over no path, only redirects to /dev-talk" $? "$OUT"
