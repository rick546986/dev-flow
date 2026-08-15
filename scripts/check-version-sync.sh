#!/bin/bash
# 版本同步守衛:Gauntlet 版本在五處必須是**同一個值**。
#
# 五處(缺一或值不同即 FAIL;不是只 grep「版本字串存在」,是逐處抽值後比較):
#   ①scripts/devflow-evidence-gauntlet.sh    GAUNTLET_VERSION="X"
#   ②devflow-contract.json                   schema_versions.gauntlet
#   ③README.md                               §7 的 `devflow-evidence-gauntlet.sh`(X,E1–E13
#   ④notes/design/evidence-gauntlet.md       **現行 Gauntlet 版本:X**
#   ⑤docs/dev/tools/devflow-evidence-gauntlet.sh  GAUNTLET_VERSION="X"(採用專案散發副本;
#     2026-08-15 補,devflow-4cap-remediation-2026-08.md §7 第 4 點:母版與散發副本的版本
#     字串本身也可能各自漂移,先前只驗四處未涵蓋散發面)
#
# 每處都必須**恰好抽到一個值**:0 個 = 錨消失(可能被簡化刪掉)→ FAIL;
# 2 個以上 = 錨不唯一,無法安全定位 → FAIL。兩種都 fail-closed,不猜。
#
# 用法:
#   scripts/check-version-sync.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供 §12 mutation 驗證(把其中一處改成 9.9.9 → 必須 FAIL)。

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import json
import os
import re
import sys

root = sys.argv[1]
problems = []
found = {}

SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+"


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        problems.append(f"檔案不存在:{rel}")
        return None
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def single(label, rel, pattern):
    """恰好一個匹配才算抽到值;0 或 >1 都 fail-closed(不猜、不取第一個)。"""
    text = read(rel)
    if text is None:
        return
    hits = re.findall(pattern, text, re.M)
    if len(hits) == 0:
        problems.append(f"{label}({rel}):版本錨消失,抽不到值")
    elif len(hits) > 1:
        problems.append(f"{label}({rel}):版本錨出現 {len(hits)} 次,不唯一 → {hits}")
    else:
        found[label] = hits[0]


LABELS = ("gauntlet-script", "contract-json", "readme", "design-doc", "docs-tools-copy")

single("gauntlet-script", "scripts/devflow-evidence-gauntlet.sh",
       rf'^GAUNTLET_VERSION="({SEMVER})"')

single("docs-tools-copy", "docs/dev/tools/devflow-evidence-gauntlet.sh",
       rf'^GAUNTLET_VERSION="({SEMVER})"')

contract_rel = "devflow-contract.json"
contract_text = read(contract_rel)
if contract_text is not None:
    try:
        value = str(json.loads(contract_text)["schema_versions"]["gauntlet"])
    except (ValueError, KeyError, TypeError) as error:
        problems.append(f"contract-json({contract_rel}):讀不到 schema_versions.gauntlet — {error}")
    else:
        if re.fullmatch(SEMVER, value):
            found["contract-json"] = value
        else:
            problems.append(
                f"contract-json({contract_rel}):schema_versions.gauntlet 非三段版本號:{value!r}")

single("readme", "README.md",
       rf'devflow-evidence-gauntlet\.sh`?\(({SEMVER}),')

single("design-doc", "notes/design/evidence-gauntlet.md",
       rf'\*\*現行 Gauntlet 版本:({SEMVER})\*\*')

print("=== Gauntlet 版本同步守衛 ===")
for label in LABELS:
    print(f"  • {label}: {found.get(label, '(抽不到)')}")

# 用 len(LABELS) 而非硬編 4/5:漏加新 label 到比對集合時,found 恰好等於舊硬編數字會
# 讓下面的交叉比對整段變 no-op(找到 4 個就自認齊了,第 5 個沒人比對)——這正是
# check-methodology-corrections.sh 對 P1 恆綠漏洞的同類陷阱,此處同理避免。
if len(found) == len(LABELS):
    values = set(found.values())
    if len(values) == 1:
        print(f"  ✓ {len(LABELS)} 處一致:{next(iter(values))}")
    else:
        problems.append(f"{len(LABELS)} 處版本不一致:{found}")

if problems:
    print()
    for problem in problems:
        print(f"  ✗ {problem}")
    print()
    print("⛔ 版本同步守衛:FAILED")
    raise SystemExit(1)

print()
print("✅ 版本同步守衛:全過")
PY
