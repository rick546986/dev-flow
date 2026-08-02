#!/bin/bash
# Gate Token 釘死守衛(Repo-local)。
#
# 為什麼需要這支(2026-08-02 實測發現的守備空窗):
#   外部 plugin 的 gate-consistency.sh 是**動態抽取** —— 它從 README §7 抽出 G1/G2/G3
#   的粗體 token,再去比對三處摘要有沒有跟上。這個設計抓得到「摘要漂移」,
#   但抓不到「正本自己少了一個 token」:把 §7 的某個粗體 token 整段刪掉(或只是去掉粗體),
#   抽取結果就少一項,沒東西可比,gate-consistency 照樣 exit 0。
#   實測:刪掉 G3 的「**+ 既有測試套件全綠**(回歸義務)」→ gate-consistency 仍全綠 14/14。
#   (G1 只有一個 token,刪掉會變成零 token 才會 fail-loud;多 token 的 G2/G3 有這個洞。)
#
#   README §7 的 Gate Token「不得改名、刪除或重新解釋」是 hard invariant,
#   而等價簡化正是最可能不小心刪到它的作業。所以本守衛把 token 集合**釘死**:
#   任何增/刪/改名都會紅。
#
# 這是 pin,不是禁止修改 gate 條件:
#   要**刻意**改 gate 條件時,更新下方 EXPECTED 常數 → 同步 §7 三處摘要
#   (plugin SKILL.md 階段表 / README §3 七份文檔表 / 對應模板頂註)→ 重跑
#   外部 gate-consistency.sh。改動因此變成一個**需要被 review 的顯性 diff**,而不是靜默流失。
#
# 抽取規則刻意與外部 gate-consistency 的 slice_gate_clause 同形(§7 → 「Gn =」子句 →
# 粗體 span),避免出現第二套會漂移的解析器。
#
# 用法:
#   scripts/check-gate-tokens.sh [root]   # 缺省 root = repo root

set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi

python3 - "$ROOT" <<'PY'
import os
import re
import sys

root = sys.argv[1]

# ── 釘死的期望值。改 gate 條件 = 改這裡 + 同步三處摘要 + 重跑外部 gate-consistency ──
# 比對時兩邊都做「去掉所有空白」正規化(與外部 gate-consistency 的 norm() 同規則),
# 這樣跨行折行、縮排、半形空白差異不會造成假警報,但**字面內容**一字不能變。
EXPECTED = {
    "G1": [
        "Owner Calls 全裁決",
        "須抽查下層清單有無該上未上的誤放",
    ],
    "G2": [
        "R/S 全審 + Drafting Decisions 全裁決",
        "Verification Profile",
        "Demo verdict",
    ],
    "G3": [
        "本次 S 全綠",
        "+ 既有測試套件全綠",
        "+ 現象證據逐 S 相符",
        "Evidence 契約全過",
    ],
}
ORDER = ["G1", "G2", "G3"]


def norm(text):
    return re.sub(r"\s+", "", text)

path = os.path.join(root, "README.md")
if not os.path.isfile(path):
    print(f"  ✗ 讀不到 {path}")
    raise SystemExit(1)
with open(path, encoding="utf-8") as stream:
    readme = stream.read()

problems = []


def die(message):
    problems.append(message)


# §7 區段:`## 7.` 到下一個 `### `(強制力對照)。起點必須恰好一次,否則 anchor 不穩。
starts = list(re.finditer(r"^## 7\.", readme, re.M))
if len(starts) != 1:
    die(f"README「## 7.」出現 {len(starts)} 次,anchor 不唯一/不存在")
    section = ""
else:
    tail = readme[starts[0].start():]
    end = re.search(r"^### ", tail, re.M)
    if not end:
        die("README §7 找不到區段終點(下一個 ### 子標題);不得靜默吃到檔尾")
        section = ""
    else:
        section = tail[:end.start()]

found = {}
if section:
    for label in ORDER:
        hits = list(re.finditer(re.escape(label) + r"\s*=", section))
        if len(hits) != 1:
            die(f"§7「{label} =」出現 {len(hits)} 次,必須恰好一次")
            continue
        start = hits[0].start()
        next_label = ORDER[ORDER.index(label) + 1] if label != ORDER[-1] else None
        if next_label is not None:
            nxt = re.search(re.escape(next_label) + r"\s*=", section[start:])
            if not nxt:
                die(f"§7 找不到「{label}」定義的結尾(缺 {next_label} = 標記)")
                continue
            clause = section[start:start + nxt.start()]
        else:
            nxt = re.search(r"\n-\s", section[start:])
            clause = section[start:] if not nxt else section[start:start + nxt.start()]
        found[label] = re.findall(r"\*\*(.+?)\*\*", clause, re.S)

print("=== README §7 Gate Token 釘死守衛 ===")
for label in ORDER:
    raw = found.get(label)
    expected = EXPECTED[label]
    if raw is None:
        print(f"  ✗ {label}: 抽取失敗")
        continue
    actual_norm = [norm(span) for span in raw]
    expected_norm = [norm(span) for span in expected]
    if actual_norm == expected_norm:
        print(f"  ✓ {label}: {len(raw)} 個 token 與釘死值一致")
        for span in expected:
            print(f"      · {span}")
    else:
        missing = [e for e, n in zip(expected, expected_norm) if n not in actual_norm]
        added = [r for r, n in zip(raw, actual_norm) if n not in expected_norm]
        print(f"  ✗ {label}: token 集合變動")
        print(f"      期望 = {expected}")
        print(f"      實得 = {[norm(s) for s in raw]}")
        if missing:
            die(f"{label} 少了 token(可能被簡化刪掉或去掉粗體):{missing}")
        if added:
            die(f"{label} 多了 token:{added}")
        if not missing and not added:
            die(f"{label} token 順序變動:期望 {expected_norm},實得 {actual_norm}")

if problems:
    print()
    for problem in problems:
        print(f"  ✗ {problem}")
    print()
    print("⛔ Gate Token 釘死守衛:FAILED")
    print("   若這是**刻意**修改 gate 條件:更新 scripts/check-gate-tokens.sh 的 EXPECTED、")
    print("   同步 §7 三處摘要(plugin SKILL.md / README §3 表 / 對應模板頂註),")
    print("   再跑外部 gate-consistency.sh 確認三處未漂。")
    raise SystemExit(1)

print()
print("✅ Gate Token 釘死守衛:全過(G1/G2/G3 粗體 token 未增刪改名)")
PY
