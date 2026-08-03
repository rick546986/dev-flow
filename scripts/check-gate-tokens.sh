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
        die("README §7 找不到區段終點(§7 之後的第一個 `### ` 子標題,目前是"
            "「### 強制力對照(誰在擋)」)。這個錯誤幾乎都不是 gate 條件出問題,"
            "而是有人把該子標題改名/刪掉/升成 `## `,或在 §7 前面新增了一個 `## 7.`。"
            "修法:恢復 §7 底下至少有一個 `### ` 子標題,或同步更新本守衛的區段規則。"
            "不得靜默吃到檔尾 —— 那會讓 §8 之後的粗體字被誤當成 gate token。")
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

# ── Gate 標籤集合釘死(fresh review F-3)─────────────────────────────────────
# 上面的迴圈只逐一比對 ORDER 裡的 G1/G2/G3,對「憑空多出來的標籤」完全不看:
# 實測在 §7 插一行 `- G4 = 設計邊界對不對(…未過不得進入 Stage 5)。` → 本守衛與
# devflow-check all 都 exit 0。既不改名也不刪除,卻**重新解釋**了整個 gate 體系,
# 而檔頭 :12-14 宣告要防的正是「改名、刪除或重新解釋」。
# 因此在這裡斷言 §7 出現的 gate 標籤集合**恰為** {G1, G2, G3}。
if section:
    declared = sorted(set(re.findall(r"G(\d+)\s*=", section)), key=int)
    expected_labels = ["1", "2", "3"]
    if declared != expected_labels:
        die(f"§7 的 gate 標籤集合不是 G1/G2/G3:實得 G{'/G'.join(declared) or '(無)'} —— "
            "要**刻意**新增或移除一道 gate:改本守衛的 ORDER/EXPECTED、"
            "同步 §7 三處摘要(plugin SKILL.md / README §3 表 / 對應模板頂註)、"
            "並更新外部 gate-consistency 的 GATE_TABLE。DevFlow 只有三道 gate 是 hard invariant。")
    else:
        print(f"  ✓ gate 標籤集合恰為 G1/G2/G3(無第四道 gate)")

# ── G3「Evidence 契約全過」八點的本體守衛 ──────────────────────────────────
# 為什麼加(2026-08 fresh review C-7 / A-L3):粗體錨只釘住「Evidence 契約全過」這幾個字,
# 錨底下那八點的**內容**沒有任何守衛。本輪把 notes/design/vnext-shared-contract.md 裡
# 唯一的第二份副本收斂掉之後,README §7 成了八點的唯一存放處 —— 少一點、被改寫、
# 或整段消失都不會有任何測試變紅。所以在這裡補一道結構斷言:條數 + 每點的關鍵詞。
#
# 2026-08 fresh review F-4:原本每點只比一個寬鬆關鍵詞,**不含極性**。實測把第 8 點的
# 「Gauntlet PASS **不**取代 Standards Axis」刪掉一個「不」→ 編號仍 1-8、關鍵詞
# `Standards Axis` 仍在 → 守衛 exit 0,規則語意整個反過來。第 5/6/7 點同型。
# 這正是註解自稱要防的「被改寫」。改成每點一組**必含片語(含極性詞)**,
# 比對前兩邊都做 norm()(去空白),讓跨行折行不造成假警報但字面極性一字不能少。
#
# 已知限制(2026-08 fresh review F-4 LOW,明列不修):片語是在**整個八點 body** 內搜尋,
# 不是逐編號區塊驗證。因此「把第 5 點的片語搬到第 6 點」這種區塊間位移不會被抓到。
# 判定為 LOW 且刻意不擴大守衛:真正的危害是片語**消失或極性反轉**,那兩種已被涵蓋;
# 為位移再蓋一層逐區塊解析,成本高於收益。
G3_POINTS = [
    ("1", ("Final Fresh Run",)),
    ("2", ("Required Layer = pass",)),
    ("3", ("Conditional Layer", "pass")),
    ("4", ("不得存在任何 fail",)),
    ("5", ("Required Layer 不得為 unverified",)),          # 極性:不得為
    ("6", ("Explicitly Excluded", "必須附理由")),           # 極性:必須
    ("7", ("Optional Layer", "必須誠實標示")),              # 極性:必須
    ("8", ("不取代 Standards Axis",)),                      # 極性:不取代
]

# ── 守衛自身清單的釘死(fresh review F-2)──────────────────────────────────
# EXPECTED 與 G3_POINTS 是本守衛的唯一正本。若它們自己被縮小 —— 例如把 G3 的一個
# token 從 EXPECTED 刪掉、同時把 README 的該 token 也刪掉 —— 兩邊互相自洽,
# 舊版守衛照樣全綠。這裡把長度釘死,讓「縮小必填集合」不再是一行安靜的刪除。
# 誠實界線:同時改釘死值仍能繞過 —— 買到的是「必須動到這個一眼看得見的數字」,
# 以及 scripts/test-architecture-guards.sh 的 GS 系列會實際變異本檔來覆蓋這件事。
PINNED_SIZES = {"G1": 2, "G2": 3, "G3": 4}
for _label, _want in PINNED_SIZES.items():
    if len(EXPECTED.get(_label, [])) != _want:
        die(f"EXPECTED[{_label}] 長度 {len(EXPECTED.get(_label, []))} ≠ 釘死值 {_want} —— "
            "要**刻意**增減 gate token:同步改 EXPECTED、這裡的釘死值、§7 三處摘要,"
            "並在 test-architecture-guards.sh 補負向案")
if sorted(EXPECTED) != sorted(PINNED_SIZES):
    die(f"EXPECTED 的 gate 標籤集合 {sorted(EXPECTED)} ≠ {sorted(PINNED_SIZES)}")
if len(G3_POINTS) != 8:
    die(f"G3_POINTS 長度 {len(G3_POINTS)} ≠ 8(G3 錨定義固定八點,少一點即代表守衛被改弱)")

if section:
    anchor = re.search(r"G3 錨定義", section)
    if not anchor:
        die("§7 找不到「G3 錨定義」段落(八點的唯一存放處)")
    else:
        tail_text = section[anchor.end():]
        stop = re.search(r"^\s*八點中的", tail_text, re.M)
        body = tail_text[:stop.start()] if stop else tail_text
        points = re.findall(r"^\s*(\d+)\.\s", body, re.M)
        if points != [str(i) for i in range(1, 9)]:
            die(f"§7「G3 錨定義」的編號點不是 1–8:實得 {points}")
        else:
            print(f"  ✓ G3 錨定義:8 點齊(1–8)")
        body_norm = norm(body)
        missing = [f"第 {n} 點「{phrase}」"
                   for n, phrases in G3_POINTS
                   for phrase in phrases
                   if norm(phrase) not in body_norm]
        if missing:
            die("§7「G3 錨定義」八點缺必含片語(被改寫、刪除或極性被反轉):"
                + "、".join(missing))
        else:
            print(f"  ✓ G3 錨定義:八點必含片語全在(含極性詞)")

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
