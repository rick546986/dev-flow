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


def table_of(block, sub_heading):
    """抽 `### <sub_heading>` 底下第一張表,回 (表頭儲存格, 資料列數)。

    資料列 = 分隔列之後、仍以 `|` 開頭的行。分開回傳是為了讓「表頭在不在」與
    「表有沒有被填」兩件事各自可判 —— 只數整節的 pipe 行會讓三張表互相頂替。
    """
    if block is None:
        return [], 0
    match = re.search(rf"^### {re.escape(sub_heading)}\s*\n(.*?)(?=^### |\Z)",
                      block, re.M | re.S)
    if not match:
        return [], 0
    header = []
    data_rows = 0
    seen_separator = False
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header:
                break
            continue
        if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", stripped):
            seen_separator = True
            continue
        if not header:
            header = [cell.strip() for cell in stripped.strip("|").split("|")]
        elif seen_separator:
            data_rows += 1
    return header, data_rows


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
    cells, _rows = table_of(template_block, heading)
    check(bool(cells), f"{TEMPLATE}「{heading}」表存在")
    for column in columns:
        check(column in cells, f"{TEMPLATE}「{heading}」表有「{column}」欄",
              f"實得={cells}")
check(template_block is not None and "Known design limit" in template_block,
      f"{TEMPLATE} Design Constraints 有 Known design limit")

# ── 4. Example 必須是 applicable(**無條件釘死**,不掛在任何可被單行編輯翻轉的條件上)──
# 2026-08 單一編輯解除武裝實測(scratchpad/single-edit-disarm-test.sh):
#   舊寫法把「必須 applicable」掛在 `^- Risk: high` 之下,結果只要把 example 的
#   `- Risk: high` 改成 `- Risk: normal`(一行、看似無關的編輯),下面整組三張表檢查、
#   Known design limit、Stage 5/6/7 example 承接**全部靜默略過**,腳本照樣 exit 0
#   (檢查數 110 → 109,沒有任何一行輸出提醒你少跑了 8 組)。這正是 fresh review A-M1
#   指的「可被一處無關編輯靜默解除武裝」。
# 修法:example 是本 repo 的**唯一參考範例**,任務規格本來就要求它命中多條觸發條件
#   (公開 API / schema migration / 權限 / Transaction / Concurrency / Risk high),
#   所以它是不是 applicable 不該是「推導出來的」,而是**釘死的 fixture 前提**。
#   Risk: high 另外單獨驗,讓「範例被降級」本身也會紅,而不是安靜地讓檢查消失。
example_block = section(example_text, SECTION)
check(example_block is not None, f"{EXAMPLE} 有「## {SECTION}」章節")
example_applicability = applicability(example_block)
check(example_applicability is not None, f"{EXAMPLE} 有 Applicability 欄")
check(example_applicability is not None
      and example_applicability.startswith("applicable")
      and "|" not in example_applicability,
      f"{EXAMPLE} Applicability 必須是 applicable(釘死;範例命中多條觸發條件)",
      f"實得={example_applicability!r}")
check(bool(example_text and re.search(r"^- Risk: high", example_text, re.M)),
      f"{EXAMPLE} 仍是 Risk: high(範例被降級 → 觸發條件⑨消失,必須顯性失敗而非靜默跳過)")

# ── 5. Example 三張表的必要欄位存在 ────────────────────────────────────────
if example_applicability and example_applicability.startswith("applicable"):
    for heading, columns in (("Architecture Boundaries", ARCH_COLUMNS),
                             ("Interface & Consistency Contract", IFACE_COLUMNS),
                             ("Software Design", DESIGN_COLUMNS)):
        cells, rows = table_of(example_block, heading)
        check(bool(cells), f"{EXAMPLE}「{heading}」表存在")
        for column in columns:
            check(column in cells, f"{EXAMPLE}「{heading}」表有「{column}」欄",
                  f"實得={cells}")
        # 逐表各自數資料列:只數整節的 pipe 行會讓三張表互相頂替(填滿一張就過關)
        check(rows >= 1, f"{EXAMPLE}「{heading}」表至少一列已填內容", f"資料列數={rows}")
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

# ── 5b. Example 不得填成 canon 自己白紙黑字列出的「壞例」 ──────────────────
# 界線宣告(重要,免得被誤讀成腳本會評分):這**不是**品質判斷,是**字面比對**。
# canon 的 §6「好例與壞例」與 §2.4 直接寫出了幾個不合格寫法的原文;
# 4-spec 的反模糊三律也已禁模糊詞。把這幾個**已經被文件點名**的字串擋掉,
# 純粹是字串比對,不需要任何語意能力 —— 腳本仍然**不判斷**邊界劃得對不對。
# 起因:2026-08 fresh review A-M1 第二組 mutation 實測 —— example 三張表填成
# canon 自己的壞例(Forbidden 寫「無」、Test seam 寫「加測試」、
# Known design limit 抄壞例原文「併發情況可能有問題,後續評估。」)仍 112/112 全過。
if example_block is not None and example_applicability \
        and example_applicability.startswith("applicable"):
    arch_header, _ = table_of(example_block, "Architecture Boundaries")
    design_header, _ = table_of(example_block, "Software Design")

    def cells_in_column(heading, column):
        """抽某張表某一欄的所有資料列儲存格(用來做字面壞例比對)。"""
        match = re.search(rf"^### {re.escape(heading)}\s*\n(.*?)(?=^### |\Z)",
                          example_block, re.M | re.S)
        if not match:
            return []
        header = None
        values = []
        for line in match.group(1).splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", stripped):
                continue
            parts = [c.strip() for c in stripped.strip("|").split("|")]
            if header is None:
                header = parts
                continue
            if column in header:
                index = header.index(column)
                if index < len(parts):
                    values.append(parts[index])
        return values

    # canon §2.2:Forbidden dependencies 沒有時寫 `—`,不是「無」(壞例原文見 canon §6)
    for value in cells_in_column("Architecture Boundaries", "Forbidden dependencies"):
        check(value != "無",
              "example Forbidden dependencies 未使用 canon 明列的壞例寫法「無」(無則寫 —)",
              f"實得={value!r}")
    # canon §2.4:Test seam 寫「加測試」不合格
    for value in cells_in_column("Software Design", "Test seam"):
        check(value not in ("加測試", "寫單元測試", "加單元測試"),
              "example Test seam 未使用 canon 明列的不合格寫法(要指到可注入點/可觀測點)",
              f"實得={value!r}")
    # 4-spec 反模糊三律 + canon §6 壞例:Known design limit 不得用模糊詞打發
    constraints = re.search(r"- Known design limit:(.*?)(?=\n## |\Z)",
                            example_block, re.S)
    if constraints:
        body = constraints.group(1)
        for vague in ("可能有問題", "後續評估", "再看看", "視情況"):
            check(vague not in body,
                  f"example Known design limit 未用模糊詞「{vague}」打發(反模糊三律)",
                  "canon §6 已把這個寫法列為壞例")

# ── 7b. 觸發條件兩份清單不得單邊漂移 ───────────────────────────────────────
# 教訓來源:本輪 fresh review(A-L2 / C-4)指出「觸發條件同時存在多份無人比對的副本」
# 正是這次剛從 notes/design/vnext-shared-contract.md 拔掉的失效模式。
# 因此兩份保留的清單(4-spec 頂註的操作用 ①–⑪、語意正本的判準表)必須機械對帳:
#   ①條數相同且為 11;②每條的關鍵詞在兩邊都出現。README 不得再有第三份枚舉。
TRIGGER_KEYWORDS = [
    "跨模組", "公開 API", "Interface", "migration", "資料所有權",
    "Queue", "Event", "Scheduler", "Background job",
    "外部服務", "Transaction", "Concurrency", "Lock", "Idempotency",
    "Network", "Filesystem", "Subprocess", "Credential",
    "Risk = high", "三個以上", "狀態機",
]

canon_text = read(CANON)
if template_block is not None and canon_text is not None:
    numbered = re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪]", template_block)
    check(len(set(numbered)) == 11,
          f"{TEMPLATE} 的觸發條件是 11 條(①–⑪)", f"實得 {len(set(numbered))} 個不同編號")
    canon_rows = re.findall(r"^\| (\d+) \| ", canon_text, re.M)
    check(len(canon_rows) >= 11 and canon_rows[:11] == [str(i) for i in range(1, 12)],
          f"{CANON} 的觸發條件表是 11 列且編號 1–11", f"實得 {canon_rows[:12]}")
    for keyword in TRIGGER_KEYWORDS:
        in_template = keyword.lower() in template_block.lower()
        in_canon = keyword.lower() in canon_text.lower()
        check(in_template and in_canon,
              f"觸發條件關鍵詞「{keyword}」兩份清單都有(防單邊漂移)",
              f"4-spec={in_template} canon={in_canon}")
    # README 只准摘要,不准第三份枚舉。README 本來就用圈號做各種小列舉(§3 四原則、
    # §7 三處摘要…),所以不能一律禁圈號;改盯「11 條清單才會用到的尾號」——
    # 出現 ⑨/⑩/⑪ 就代表有人在 README 又抄了一份十一條觸發條件。
    if readme_text is not None:
        leaked = [mark for mark in ("⑨", "⑩", "⑪") if mark in readme_text]
        check(not leaked,
              "README 未出現第三份觸發條件枚舉(11 條清單的尾號 ⑨⑩⑪)",
              f"出現={leaked}")

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

# example 端:契約為 applicable 時,Stage 5／6／7 三個下游必須**齊頭**回填。
# (fresh review C-1 + A-M1:承接檢查只打 _templates,唯一參考範例可以自相矛盾卻全綠。
#  兩位對抗查核者都指出「只補 Stage 5」會讓範例更不自洽 —— 上游宣告 applicable 且已摘錄,
#  下游卻查無此檢查。因此三個下游一起驗,不留半邊。
#  注意 needle 不能照抄 _templates 的規則字串:範例裡是**填好的實例**,不是規則條文。)
if example_applicability and example_applicability.startswith("applicable"):
    example_tasks = read("example/contract-expiry-reminder/5-tasks.md")
    check(example_tasks is not None, "example 5-tasks 存在")
    if example_tasks is not None:
        blocks = re.split(r"(?=^## T-\d+)", example_tasks, flags=re.M)[1:]
        check(bool(blocks), "example 5-tasks 可解析出 T 區塊")
        excerpted = [b for b in blocks if "Design Boundary" in b]
        check(len(excerpted) == len(blocks),
              "example Stage 5:每個 T 的 Boundaries 都摘錄了設計邊界",
              f"{len(excerpted)}/{len(blocks)} 個 T 有摘錄")

    example_notes = read("example/contract-expiry-reminder/6-implementation-notes.md")
    check(example_notes is not None, "example 6-notes 存在")
    if example_notes is not None:
        reviews = re.findall(r"^- Test Integrity finding:", example_notes, re.M)
        boundary = re.findall(r"^- Design boundary finding:", example_notes, re.M)
        check(len(boundary) == len(reviews) and bool(reviews),
              "example Stage 6:每筆 T Review Log 都有 Design boundary finding",
              f"T Review Log {len(reviews)} 筆,Design boundary finding {len(boundary)} 筆")

    example_review = read("example/contract-expiry-reminder/7-review.md")
    check(example_review is not None, "example 7-review 存在")
    if example_review is not None:
        for axis_needle in ("Dependency Direction", "Boundary Leakage",
                            "Data Ownership", "Interface Stability"):
            check(axis_needle in example_review,
                  f"example Stage 7 Standards Axis 有查「{axis_needle}」")
        check("Design Boundary Contract 逐條對照 diff" in example_review,
              "example Stage 7 Spec Axis 有逐條對照 Design Boundary Contract")

# 檢查數地板:防「條件式 gating 讓整組檢查靜默不跑卻照樣 exit 0」再度發生。
# 數字是實測下限(目前 110);合法新增檢查只會讓它變大,不會變小。
MIN_CHECKS = 100
check(checks >= MIN_CHECKS,
      f"執行的結構檢查數 ≥ {MIN_CHECKS}(防條件式 gating 靜默跳過整組)",
      f"實得 {checks} —— 有檢查沒跑到,先查是不是某個 if 把整段擋掉了")

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
