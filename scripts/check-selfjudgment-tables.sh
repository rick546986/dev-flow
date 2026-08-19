#!/bin/bash
# 自判表對稱性檢查(2026-08-19)。
#
# 為什麼需要:四份文檔各有一張「模型自己拍板、待人裁決」的表
# (2-decision 的 Approaches Considered 與 Owner Calls、4-spec 的 Drafting Decisions、
# 5-tasks 的 Split Decisions、6-notes 的 Decisions)。原本只有 Owner Calls 一張
# 同時具備「若被推翻會怎樣」與上下兩層分流,其餘三張沒有,也沒有任何一欄能分辨
# 「這格有出處」與「這格是模型猜的」—— 人在 G1/G2 面對的表因此把查證過的與猜的
# 排在一起,看不出差別(README §5「不對稱保護(第 6 型假綠)」明文要求好做法要推廣)。
#
# 本支驗的是**結構**,不判內容對錯:欄在不在、兩層分流在不在、範例每列有沒有填。
# 「依據寫得對不對」永遠是 G1/G2 reviewer 的判斷,機械不判語意。
#
# 可選第一參數:指向隔離複本的 root(同 scripts/check-realworld.sh 慣例)。
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -n "${1:-}" ]; then
  ROOT=$(cd "$1" && pwd) || exit 2
fi
python3 - "$ROOT" <<'PY'
import os
import re
import subprocess
import sys

root = sys.argv[1]
checks = 0
failures = []


def check(condition, label, detail=""):
    global checks
    checks += 1
    if not condition:
        failures.append(label + (f": {detail}" if detail else ""))


def read(rel):
    with open(os.path.join(root, rel), encoding="utf-8") as stream:
        return stream.read()


def section(source, heading):
    """切出 `## <heading>` 到下一個**同級或更高級**標題為止(子節留在本節內)。"""
    pattern = re.compile(
        rf"^##\s*{re.escape(heading)}.*?\n(.*?)(?=^##\s|\Z)", re.M | re.S)
    match = pattern.search(source)
    return match.group(1) if match else ""


def data_rows(body):
    """表格資料列(去掉表頭與分隔列)。"""
    rows = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("|")]
    return [r for r in rows[2:] if not set(r) <= set("|- ")]


def cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


T2 = read("_templates/2-decision.md")
T4 = read("_templates/4-spec.md")
T5 = read("_templates/5-tasks.md")
T6 = read("_templates/6-implementation-notes.md")
E2 = read("example/contract-expiry-reminder/2-decision.md")
E4 = read("example/contract-expiry-reminder/4-spec.md")

# ── 1. 四份模板的自判節都要求標 [Assumption] ────────────────────────────────
for rel, source, heading in (
        ("_templates/2-decision.md", T2, "Approaches Considered"),
        ("_templates/2-decision.md", T2, "Owner Calls"),
        ("_templates/4-spec.md", T4, "Drafting Decisions"),
        ("_templates/5-tasks.md", T5, "Split Decisions"),
        ("_templates/6-implementation-notes.md", T6, "Decisions"),
):
    body = section(source, heading)
    check("[Assumption]" in body,
          f"{rel} 的「{heading}」節要求無出處時標 [Assumption]",
          "節內找不到 [Assumption] —— 沒有這條,模型猜的與查證過的在表上長一樣")

# ── 2. 表頭必含「依據」欄 ──────────────────────────────────────────────────
for rel, source, heading in (
        ("_templates/2-decision.md", T2, "Approaches Considered"),
        ("_templates/2-decision.md", T2, "Owner Calls"),
        ("_templates/4-spec.md", T4, "Drafting Decisions"),
        ("example/contract-expiry-reminder/2-decision.md", E2, "Approaches Considered"),
        ("example/contract-expiry-reminder/2-decision.md", E2, "Owner Calls"),
        ("example/contract-expiry-reminder/4-spec.md", E4, "Drafting Decisions"),
):
    body = section(source, heading)
    header = next((ln for ln in body.splitlines() if ln.strip().startswith("|")), "")
    check("依據" in header, f"{rel}「{heading}」表頭有「依據」欄", f"表頭:{header.strip()[:80]}")

# ── 3. 裁決表要有「若被推翻會怎樣」(代價欄)──────────────────────────────
for rel, source in (("_templates/2-decision.md", T2),
                    ("_templates/4-spec.md", T4),
                    ("example/contract-expiry-reminder/2-decision.md", E2),
                    ("example/contract-expiry-reminder/4-spec.md", E4)):
    heading = "Owner Calls" if "2-decision" in rel else "Drafting Decisions"
    check("若被推翻會怎樣" in section(source, heading),
          f"{rel}「{heading}」有「若被推翻會怎樣」欄",
          "少了代價欄,人只看得到決定本身,判不出打回的成本")

# ── 4. DD 與 OC 一樣分上下兩層 ────────────────────────────────────────────
for rel, source in (("_templates/4-spec.md", T4),
                    ("example/contract-expiry-reminder/4-spec.md", E4),
                    ("_templates/2-decision.md", T2),
                    ("example/contract-expiry-reminder/2-decision.md", E2)):
    heading = "Drafting Decisions" if "4-spec" in rel else "Owner Calls"
    body = section(source, heading)
    check("### 逐條裁決(上層)" in body, f"{rel}「{heading}」有上層逐條裁決子節")
    check("### 內部技術選擇(下層" in body, f"{rel}「{heading}」有下層告知子節")

# ── 5. 範例每一列的「依據」欄都填了 ───────────────────────────────────────
for rel, source, heading in (
        ("example/contract-expiry-reminder/2-decision.md", E2, "Approaches Considered"),
        ("example/contract-expiry-reminder/2-decision.md", E2, "Owner Calls"),
        ("example/contract-expiry-reminder/4-spec.md", E4, "Drafting Decisions"),
):
    body = section(source, heading)
    header_line = next((ln for ln in body.splitlines() if ln.strip().startswith("|")), "")
    idx = next((i for i, c in enumerate(cells(header_line)) if "依據" in c), None)
    rows = data_rows(body)
    check(idx is not None and bool(rows), f"{rel}「{heading}」解析得到依據欄與資料列",
          f"idx={idx} rows={len(rows)}")
    if idx is None:
        continue
    empty = [cells(r)[0] for r in rows if len(cells(r)) <= idx or not cells(r)[idx]]
    check(not empty, f"{rel}「{heading}」每列依據欄非空", f"空的列:{empty}")

# ── 5b. 範例的 html twin 也要帶「依據」欄 ────────────────────────────────
# 為什麼要單獨驗:example 的 twin 是**手寫**的審查介面,不是 md 直轉,renderer 的
# fixed-point 檢查管不到它;md 加了欄、html 沒跟上時,人打開來審的那一份看不到依據,
# 而所有機械檢查照樣全綠(獨立驗收 2026-08-19 實際抓到這個漂移)。
twin = read("example/contract-expiry-reminder/2-decision.html")
check("<h2>Owner Calls" in twin, "範例 2-decision.html 有 Owner Calls 節")
oc_head = next((ln for ln in twin.splitlines()
                if "<th>OC</th>" in ln), "")
check("依據" in oc_head, "範例 2-decision.html 的 Owner Calls 表頭有「依據」欄",
      f"表頭:{oc_head.strip()[:90]}")
check(twin.count("[Assumption]") >= 3,
      "範例 2-decision.html 至少三處標了 [Assumption](沒出處的格子要現形)",
      f"實得 {twin.count('[Assumption]')} 處")
check("<td>依據</td>" in twin, "範例 2-decision.html 的方案比較表有「依據」列")

# ── 6. 負向 fixture:DD 子節裡的殘留必須被 C5 抓到 ────────────────────────
gate = os.path.join(root, "scripts", "check-spec-gate.sh")
bad = os.path.join(root, "scripts", "fixtures", "spec-gate-dd-subsection",
                   "bad-dd-unresolved.md")
proc = subprocess.run(["bash", gate, bad], capture_output=True, text=True)
check(proc.returncode == 1,
      "負向 fixture:DD 上層表殘留待裁決 → check-spec-gate 必須 exit 1",
      f"實得 exit {proc.returncode}(C5 掃描範圍又縮回子標題前了)")
check("C5" in proc.stdout and "❌ C5" in proc.stdout,
      "負向 fixture 是被 C5 擋下的(不是被別條誤擋)",
      proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "無輸出")

good = os.path.join(root, "example", "contract-expiry-reminder", "4-spec.md")
proc_ok = subprocess.run(["bash", gate, good], capture_output=True, text=True)
check(proc_ok.returncode == 0,
      "正向:改成兩層表之後,母版範例仍過 G2 形狀檢查",
      f"實得 exit {proc_ok.returncode}")

# ── 檢查數地板 ─────────────────────────────────────────────────────────────
# ⚠️ 必須等於當下實際檢查數(同 scripts/check-realworld.sh 的 MIN_CHECKS 慣例):
# 留餘裕 = 沒有牙齒,整段被刪掉時仍會印綠。增刪 check() 時一起改這個數字。
MIN_CHECKS = 36
if checks < MIN_CHECKS:
    failures.append(f"⛔ 實際只跑了 {checks} 項檢查(地板 {MIN_CHECKS})—— "
                    f"檢查本身被刪掉或迴圈跑了零圈")

if failures:
    print(f"❌ self-judgment table checks: {checks - len(failures)}/{checks} passed"
          f"(地板 {MIN_CHECKS})")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print(f"✅ self-judgment table checks: {checks}/{checks} passed(地板 {MIN_CHECKS})")
PY
