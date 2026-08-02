#!/bin/bash
# Design Boundary Contract 結構守衛(Repo-local)。
#
# 本腳本只驗**結構**:欄在不在、表頭齊不齊、n-a 有沒有理由、正本歸屬有沒有漂、
# Stage 5/6/7 有沒有承接規則。
#
# 本腳本**不宣稱**能判斷:模組邊界寫得對不對、Data Owner 合不合理、Interface 設計好不好、
# Transaction Boundary 是否符合領域。**那些永遠是 G2／G3 Reviewer 的判斷**
# (與 README §7「強制力對照」表同一分類:腳本驗欄位存在,人判語意)。
#
# 用法:
#   scripts/check-design-contract.sh [root]   # 缺省 root = repo root
# root 可指向 /private/tmp 下的複本,供 §12 mutation 驗證。

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
checks = 0
failures = []

TEMPLATE = "_templates/4-spec.md"
EXAMPLE = "example/contract-expiry-reminder/4-spec.md"
CANON = "notes/design/design-boundary-contract.md"
SECTION = "Design Boundary Contract"

ARCH_COLUMNS = ["Boundary / Module", "Responsibility", "Data owner",
                "Allowed dependencies", "Forbidden dependencies"]
IFACE_COLUMNS = ["Interface / Flow", "Input / Output", "Errors",
                 "Transaction / Consistency boundary", "Compatibility"]
DESIGN_COLUMNS = ["Component", "Responsibility", "Collaborators",
                  "State / Data flow", "Error handling", "Test seam"]
TABLE_HEADINGS = ["Architecture Boundaries", "Interface & Consistency Contract",
                  "Software Design"]


def check(condition, label, detail=""):
    global checks
    checks += 1
    if not condition:
        failures.append(label + (f" — {detail}" if detail else ""))


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        return stream.read()


def section(text, name):
    """抽 `## <name>` 到下一個 `## ` 之間(含子標題 ###)。找不到回 None。"""
    if text is None:
        return None
    match = re.search(rf"^## {re.escape(name)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def header_cells(block, sub_heading):
    """抽 `### <sub_heading>` 底下第一張表的表頭儲存格。"""
    if block is None:
        return []
    match = re.search(rf"^### {re.escape(sub_heading)}\s*\n(.*?)(?=^### |\Z)",
                      block, re.M | re.S)
    if not match:
        return []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", stripped):
            return [cell.strip() for cell in stripped.strip("|").split("|")]
    return []


def applicability(block):
    if block is None:
        return None
    match = re.search(r"^- Applicability:(.*)$", block, re.M)
    return match.group(1).strip() if match else None


template_text = read(TEMPLATE)
example_text = read(EXAMPLE)
readme_text = read("README.md")

check(template_text is not None, f"{TEMPLATE} 存在")
check(example_text is not None, f"{EXAMPLE} 存在")
check(readme_text is not None, "README.md 存在")
check(read(CANON) is not None, f"語意正本 {CANON} 存在")

# ── 1. Template 有 Design Boundary Contract 章節 ───────────────────────────
template_block = section(template_text, SECTION)
check(template_block is not None, f"{TEMPLATE} 有「## {SECTION}」章節")

# ── 2. Template 的 Applicability / Trigger(s) 欄存在 ───────────────────────
template_applicability = applicability(template_block)
check(template_applicability is not None, f"{TEMPLATE} 有 Applicability 欄")
if template_applicability is not None:
    check("applicable" in template_applicability and "n-a" in template_applicability,
          f"{TEMPLATE} 的 Applicability 欄提供 applicable | n-a 兩個選項",
          template_applicability[:60])
check(template_block is not None and re.search(r"^- Trigger\(s\):", template_block, re.M) is not None,
      f"{TEMPLATE} 有 Trigger(s) 欄")
check(template_block is not None and re.search(r"^- Design source:", template_block, re.M) is not None,
      f"{TEMPLATE} 有 Design source 欄")

# ── 3. Template 三張表的必要欄位存在 ───────────────────────────────────────
for heading, columns in (("Architecture Boundaries", ARCH_COLUMNS),
                         ("Interface & Consistency Contract", IFACE_COLUMNS),
                         ("Software Design", DESIGN_COLUMNS)):
    cells = header_cells(template_block, heading)
    check(bool(cells), f"{TEMPLATE}「{heading}」表存在")
    for column in columns:
        check(column in cells, f"{TEMPLATE}「{heading}」表有「{column}」欄",
              f"實得={cells}")
check(template_block is not None and "Known design limit" in template_block,
      f"{TEMPLATE} Design Constraints 有 Known design limit")

# ── 4. Example 命中觸發條件時必須是 applicable ─────────────────────────────
# 機械判準(只用得到不需語意的訊號):example 的 Verification Profile 寫 `Risk: high`
# → 命中觸發條件⑨ → Applicability 必須是 applicable。
example_block = section(example_text, SECTION)
check(example_block is not None, f"{EXAMPLE} 有「## {SECTION}」章節")
example_risk_high = bool(example_text and re.search(r"^- Risk: high", example_text, re.M))
example_applicability = applicability(example_block)
check(example_applicability is not None, f"{EXAMPLE} 有 Applicability 欄")
if example_risk_high:
    check(example_applicability is not None
          and example_applicability.startswith("applicable")
          and "|" not in example_applicability,
          f"{EXAMPLE} Risk: high 命中觸發條件 → Applicability 必須是 applicable",
          f"實得={example_applicability!r}")

# ── 5. Example 三張表的必要欄位存在 ────────────────────────────────────────
if example_applicability and example_applicability.startswith("applicable"):
    for heading, columns in (("Architecture Boundaries", ARCH_COLUMNS),
                             ("Interface & Consistency Contract", IFACE_COLUMNS),
                             ("Software Design", DESIGN_COLUMNS)):
        cells = header_cells(example_block, heading)
        check(bool(cells), f"{EXAMPLE}「{heading}」表存在")
        for column in columns:
            check(column in cells, f"{EXAMPLE}「{heading}」表有「{column}」欄",
                  f"實得={cells}")
        rows = [line for line in (example_block or "").splitlines()
                if line.strip().startswith("|")]
        check(len(rows) >= 3, f"{EXAMPLE} 三張表至少各有內容列", f"pipe 列數={len(rows)}")
    check("Known design limit" in (example_block or ""),
          f"{EXAMPLE} 有 Known design limit")

# ── 6. n-a 必須有非空、非佔位的理由 ────────────────────────────────────────
def na_reason_ok(value):
    """`n-a` 只有一種合法形式:`n-a — <非空且非佔位理由>`。"""
    match = re.match(r"^n-a\s*—\s*(.+)$", value.strip())
    if not match:
        return False
    reason = match.group(1).strip()
    if not reason or reason.startswith("<"):
        return False
    return len(reason) >= 8


for rel, block in ((TEMPLATE, template_block), (EXAMPLE, example_block)):
    value = applicability(block)
    if value is None:
        continue
    if value.startswith("n-a"):
        check(na_reason_ok(value), f"{rel} 的 n-a 附具體理由(不得只寫「不適用」)",
              f"實得={value!r}")
    else:
        check(value.strip() != "", f"{rel} Applicability 非空值", f"實得={value!r}")

# ── 7. README 只保留摘要與正本連結(不得重抄表格) ───────────────────────────
if readme_text is not None:
    for heading in TABLE_HEADINGS:
        # Software Design 是通用詞,只擋「表頭形式」(出現在 markdown 表格列裡)
        leaked = [line for line in readme_text.splitlines()
                  if line.strip().startswith("|") and heading in line]
        check(not leaked, f"README 未重抄「{heading}」表頭(正本在 {TEMPLATE})",
              f"洩漏於={leaked[:1]}")
    for column in ("Forbidden dependencies", "Transaction / Consistency boundary", "Test seam"):
        check(column not in readme_text,
              f"README 未重抄欄位「{column}」(正本在 {TEMPLATE})")
    check(SECTION in readme_text, f"README 有 {SECTION} 摘要")
    check(CANON in readme_text, f"README 連到語意正本 {CANON}")

# ── 8. Stage 5／6／7 有承接規則 ────────────────────────────────────────────
handoffs = [
    ("_templates/5-tasks.md", ["Design Boundary", "Boundaries:"],
     "Stage 5 用既有 Boundaries: 欄摘錄"),
    ("_templates/6-implementation-notes.md", ["Design Boundary Check"],
     "Stage 6 T Review 有 Design Boundary Check"),
    ("_templates/7-review.md", ["Design Boundary Contract", "Dependency Direction",
                                "Data Ownership", "Interface Stability"],
     "Stage 7 雙軸審承接設計契約"),
]
for rel, needles, label in handoffs:
    text = read(rel)
    check(text is not None, f"{rel} 存在")
    for needle in needles:
        check(text is not None and needle in text, f"{label}:{rel} 含「{needle}」")

print("=== Design Boundary Contract 結構守衛 ===")
print(f"  • root: {root}")
if failures:
    for failure in failures:
        print(f"  ✗ {failure}")
    print()
    print(f"⛔ design contract 結構守衛:{len(failures)}/{checks} 失敗")
    raise SystemExit(1)
print(f"  ✓ 結構檢查 {checks}/{checks} 全過(語意仍由 G2／G3 Reviewer 判斷)")
print()
print("✅ design contract 結構守衛:全過")
PY
