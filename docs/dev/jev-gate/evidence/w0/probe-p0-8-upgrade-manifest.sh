#!/bin/bash
# probe-p0-8-upgrade-manifest.sh — W0 P0-8:既有採用專案在 ship-manifest 新增一列
# (例:scripts/devflow-jev.py)之後,有哪些「機械」路徑會察覺缺件、哪些只靠 dev-setup 散文。
# 做法:
#   ① 用目前 pack 的 ship-manifest 照 install 步 0/8 語意,種一棵「已安裝」採用樹 + baseline;
#   ② 複製一份 pack 到暫存,往 ship-manifest 加一列 devflow-jev.py(source 也一併造出來);
#   ③ 在採用樹上跑:doctor(hooks/devflow-exec.sh doctor)、devflow-upgrade-leftovers --dry-run、
#      devflow_ship_manifest.py --validate(對 pack 副本)、check-ship-manifest.sh(對 pack 副本);
#   ④ 記錄誰紅、誰綠、誰根本不看採用樹。
# 用法:bash probe-p0-8-upgrade-manifest.sh <dev-flow pack root>
set -u
PACK=$(cd "${1:-.}" && pwd)
T=$(mktemp -d "${TMPDIR:-/tmp}/p08-adopt.XXXXXX")
P2=$(mktemp -d "${TMPDIR:-/tmp}/p08-pack.XXXXXX")
trap 'rm -rf "$T" "$P2"' EXIT
J() { python3 -c 'import json,sys;print(json.dumps(dict(step=sys.argv[1], rc=int(sys.argv[2]), out=sys.argv[3][-3000:]), ensure_ascii=False))' "$1" "$2" "$3"; }

# ① 採用樹
mkdir -p "$T/docs/dev/tools" "$T/docs/dev/.devflow-baseline" "$T/docs/adr"
( cd "$T" && git init -q . && git config user.email p@p && git config user.name p )
python3 - "$PACK" "$T" <<'PY'
import json, os, shutil, sys
pack, root = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(pack, "docs/dev/ship-manifest.json")))
for row in m["files"]:
    src = os.path.join(pack, row["source"]); dst = os.path.join(root, row["destination"])
    os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst); os.chmod(dst, int(row["mode"], 8))
    b = os.path.join(root, "docs/dev/.devflow-baseline", os.path.relpath(row["destination"], "docs/dev"))
    os.makedirs(os.path.dirname(b), exist_ok=True); shutil.copy2(src, b)
shutil.copytree(os.path.join(pack, "_templates"), os.path.join(root, "docs/dev/_templates"))
shutil.copytree(os.path.join(pack, "_templates"), os.path.join(root, "docs/dev/.devflow-baseline/_templates"))
open(os.path.join(root, "docs/dev/README.md"), "w").write("stripped readme\n")
open(os.path.join(root, "docs/dev/.devflow-baseline/README.md"), "w").write("stripped readme\n")
print(json.dumps({"step": "01-adopted-tree-seeded", "manifest_rows": len(m["files"]),
                  "tools": sorted(os.listdir(os.path.join(root, "docs/dev/tools"))),
                  "adopted_tree_has_manifest_copy": os.path.exists(os.path.join(root, "docs/dev/ship-manifest.json")),
                  "contract_has_ship_manifest_version": any(k for k in json.dumps(json.load(open(os.path.join(pack, "devflow-contract.json")))).split('"') if "ship" in k.lower() or "manifest_version" in k.lower())}, ensure_ascii=False))
PY
( cd "$T" && git add -A >/dev/null && git commit -qm installed )

# ② pack 副本 + 新列
cp -r "$PACK/scripts" "$PACK/hooks" "$PACK/docs" "$PACK/_templates" "$PACK/skills" "$PACK/guides" "$PACK/devflow-contract.json" "$P2/" 2>/dev/null
cp "$PACK/README.md" "$P2/" 2>/dev/null; rm -rf "$P2/docs/dev/jev-gate"
printf '#!/usr/bin/env python3\n# placeholder for probe only — NOT the real runtime (W1 gate: seven guards first)\nraise SystemExit(0)\n' > "$P2/scripts/devflow-jev.py"; chmod 755 "$P2/scripts/devflow-jev.py"
python3 - "$P2" <<'PY'
import json, sys, os
p = os.path.join(sys.argv[1], "docs/dev/ship-manifest.json"); m = json.load(open(p))
m["files"].append({"source": "scripts/devflow-jev.py", "destination": "docs/dev/tools/devflow-jev.py", "mode": "755"})
json.dump(m, open(p, "w"), ensure_ascii=False, indent=2)
print(json.dumps({"step": "02-pack-copy-manifest-plus-row", "rows": len(m["files"])}))
PY

# ③ 機械路徑逐一問:採用樹缺 docs/dev/tools/devflow-jev.py,誰看得到?
RUNJ() { # RUNJ <label> <filter-regex|-> <cmd...>:真實 exit code 取自指令本身,不是 grep/head
  local label="$1" flt="$2"; shift 2; local tmp; tmp=$(mktemp)
  ( "$@" ) >"$tmp" 2>&1; local rc=$?
  if [ "$flt" = "-" ]; then OUT=$(cat "$tmp"); else OUT=$(grep -E "$flt" "$tmp" | head -12); fi
  rm -f "$tmp"; J "$label" "$rc" "$OUT"; }
RUNJ "10-pack-side:devflow_ship_manifest --validate (pack copy, tools/ copy absent)" - bash -c 'cd "$1" && python3 scripts/devflow_ship_manifest.py --validate "$1"' _ "$P2"
RUNJ "11-pack-side:check-ship-manifest.sh (pack copy)" "✗|⛔|FAIL|全過|失敗" bash "$P2/scripts/check-ship-manifest.sh" "$P2"
cp "$P2/scripts/devflow-jev.py" "$P2/docs/dev/tools/devflow-jev.py"; chmod 755 "$P2/docs/dev/tools/devflow-jev.py"
RUNJ "12-pack-side:check-ship-manifest.sh after adding pack-side tools/ copy (filemap row still missing?)" "✗|⛔|FAIL|全過|失敗|檔案地圖" bash "$P2/scripts/check-ship-manifest.sh" "$P2"
# doctor:完整輸出不過濾(✗ 行必須保留;本環境 python 3.11 會讓 printer-python 紅,與 manifest 無關)
RUNJ "20-adopted:doctor (contract from new pack; full output, real exit code)" - bash -c 'cd "$1" && DEVFLOW_CONTRACT="$2/devflow-contract.json" bash "$2/hooks/devflow-exec.sh" doctor' _ "$T" "$P2"
RUNJ "20b-adopted:doctor ✗ lines only" "^✗" bash -c 'cd "$1" && DEVFLOW_CONTRACT="$2/devflow-contract.json" bash "$2/hooks/devflow-exec.sh" doctor' _ "$T" "$P2"
RUNJ "21-adopted:upgrade-leftovers dry-run (only _templates/, never tools/)" - bash "$P2/scripts/devflow-upgrade-leftovers.sh" --root "$T" --pack "$P2"
RUNJ "22-pack-side:check-dev-setup-discipline (prose needles only)" "✅|⛔|❌" bash "$P2/scripts/check-dev-setup-discipline.sh" "$P2"
# 採用樹側:三方比對對「新列、本地不存在、baseline 不存在」怎麼判 —— 用 SKILL.md 判別法原文機械化
python3 - "$P2" "$T" <<'PY'
import json, os, sys
pack, root = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(pack, "docs/dev/ship-manifest.json")))
rows = []
for row in m["files"]:
    dst = os.path.join(root, row["destination"]); base = os.path.join(root, "docs/dev/.devflow-baseline", os.path.relpath(row["destination"], "docs/dev"))
    rows.append({"destination": row["destination"], "local_exists": os.path.exists(dst), "baseline_exists": os.path.exists(base),
                 "three_way_class": ("①母版改寫/新增(本地缺、baseline 缺)" if not os.path.exists(dst) and not os.path.exists(base)
                                     else "②本地客製?" if os.path.exists(dst) and (not os.path.exists(base) or open(dst,'rb').read()!=open(base,'rb').read())
                                     else "①同上游舊")})
missing = [r for r in rows if not r["local_exists"]]
print(json.dumps({"step": "30-adopted:three-way-classification-of-new-row", "missing_destinations": [r["destination"] for r in missing],
                  "rows": missing, "n_rows_total": len(rows),
                  "skill_prose_line": "skills/dev-setup/SKILL.md ## upgrade(stale) 首條:只覆蓋 …ship-manifest.json 每一列的 destination"}, ensure_ascii=False))
PY
