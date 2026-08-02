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

python3 - "$ROOT" "$0" <<'PY'
import os
import re
import sys

root = sys.argv[1]
# argv[2] = 本守衛自己的路徑。用來自我檢查「必填清單有沒有被偷偷縮小」(見 guard-selfpin 群組)。
# 跑在 /private/tmp 複本上時指到的就是那份複本 —— 負向 mutation 測的正是複本。
self_path = sys.argv[2] if len(sys.argv) > 2 else ""
checks = 0
failures = []

# 檢查數地板:**次級 backstop**,只用來偵測「大幅縮水」。定義提前到這裡,
# 好讓 guard-selfpin 群組能把它一起釘死(否則改小一行就繞過)。
MIN_CHECKS = 100

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


# ── 必跑檢查群組(heartbeat)────────────────────────────────────────────────
# 為什麼是「群組心跳」而不是只有一個檢查數地板:
#   檢查數地板只能偵測「大幅縮水」,無法偵測「某一個群組整組沒跑但別的群組變多」。
#   heartbeat 逐群組斷言「這一群至少跑過一條」,任何群組被條件式擋掉都會顯性失敗。
REQUIRED_GROUPS = [
    "files-exist",
    "template-section",
    "template-fields",
    "template-tables",
    "example-applicability",
    "example-tables",
    "example-antipattern",
    "na-reason",
    "readme-canonical",
    "trigger-parity",
    "handoff-templates",
    "handoff-example",
    "guard-selfpin",
]
CURRENT_GROUP = "files-exist"
groups_seen = {}


def check(condition, label, detail=""):
    global checks
    checks += 1
    groups_seen[CURRENT_GROUP] = groups_seen.get(CURRENT_GROUP, 0) + 1
    if not condition:
        failures.append(f"[{CURRENT_GROUP}] " + label + (f" — {detail}" if detail else ""))


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

CURRENT_GROUP = "template-section"
# ── 1. Template 有 Design Boundary Contract 章節 ───────────────────────────
template_block = section(template_text, SECTION)
check(template_block is not None, f"{TEMPLATE} 有「## {SECTION}」章節")

CURRENT_GROUP = "template-fields"
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

CURRENT_GROUP = "template-tables"
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

CURRENT_GROUP = "example-applicability"
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

CURRENT_GROUP = "example-tables"
# ── 5. Example 三張表的必要欄位存在 ────────────────────────────────────────
# **無條件執行**:example 的 applicable 已在群組 example-applicability 釘死,
# 再把表檢查掛在它之下只會製造「翻掉上游就整組消失」的第二道靜默閘門。
if True:
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

CURRENT_GROUP = "na-reason"
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

CURRENT_GROUP = "readme-canonical"
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

CURRENT_GROUP = "example-antipattern"
# ── 5b. Example 不得填成 canon 自己白紙黑字列出的「壞例」 ──────────────────
# 界線宣告(重要,免得被誤讀成腳本會評分):這**不是**品質判斷,是**字面比對**。
# canon 的 §6「好例與壞例」與 §2.4 直接寫出了幾個不合格寫法的原文;
# 4-spec 的反模糊三律也已禁模糊詞。把這幾個**已經被文件點名**的字串擋掉,
# 純粹是字串比對,不需要任何語意能力 —— 腳本仍然**不判斷**邊界劃得對不對。
# 起因:2026-08 fresh review A-M1 第二組 mutation 實測 —— example 三張表填成
# canon 自己的壞例(Forbidden 寫「無」、Test seam 寫「加測試」、
# Known design limit 抄壞例原文「併發情況可能有問題,後續評估。」)仍 112/112 全過。
# **無條件執行**(理由同上;example_block 為 None 時下列抽取自然得到空清單,
# 而「章節不存在」已由 example-applicability 群組顯性報錯)
if True:
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

CURRENT_GROUP = "trigger-parity"
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

CURRENT_GROUP = "handoff-templates"
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
CURRENT_GROUP = "handoff-example"
# **無條件執行**(理由同上)
if True:
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

CURRENT_GROUP = "guard-selfpin"
# ── 守衛自身必填清單的釘死(fresh review F-2)──────────────────────────────
# 為什麼要有這一組:heartbeat 只斷言「這一群跑過幾條」,MIN_CHECKS 只偵測大幅縮水。
# 兩者都抓不到「清單被縮小」。實測(修正前):
#   ①單行把 TRIGGER_KEYWORDS 由 21 條砍成 1 條 → 檢查數 127→107,heartbeat 仍報
#     trigger-parity=4(>0),MIN_CHECKS=100 也還在,devflow-check all exit 0。
#   ②兩行(停掉 handoff-example 群組 + 刪它的 REQUIRED_GROUPS 條目)→ 116/116 全綠。
# 而常設 mutation suite(test-architecture-guards.sh)明文只變異**資料檔**,
# 守衛本體從不被變異 —— 「守衛被改弱」整類零覆蓋。
#
# 兩層防法:
#   (a) 數量釘死:單一編輯縮小任何一個必填清單即紅。
#   (b) canon 交叉核對:三張表的欄名不是憑空寫死在 Python 裡,而是必須與語意正本
#       notes/design/design-boundary-contract.md §2.2/2.3/2.4 的欄位表**逐字相同**。
#       要改必填欄位,就必須同時改語意正本 —— 那是一個有意義、看得見的 diff,
#       不是守衛原始碼裡一行安靜的刪除。
# 誠實界線:守衛終究無法完全守住自己。這裡買到的是「單一編輯不再夠用,
# 而兩處編輯必須包含 canon 或釘死數字」,不是「不可能被繞過」。
PINNED_SIZES = {
    "ARCH_COLUMNS": (len(ARCH_COLUMNS), 5),
    "IFACE_COLUMNS": (len(IFACE_COLUMNS), 5),
    "DESIGN_COLUMNS": (len(DESIGN_COLUMNS), 6),
    "TABLE_HEADINGS": (len(TABLE_HEADINGS), 3),
    "TRIGGER_KEYWORDS": (len(TRIGGER_KEYWORDS), 21),
    "REQUIRED_GROUPS": (len(REQUIRED_GROUPS), 13),
    "handoffs": (len(handoffs), 3),
    "handoff needles": (sum(len(n) for _rel, n, _label in handoffs), 7),
}
for _name, (_actual, _want) in PINNED_SIZES.items():
    check(_actual == _want,
          f"守衛自身清單「{_name}」長度未被縮小(釘死 {_want})",
          f"實得 {_actual} —— 要**刻意**增減必填項:同步改這裡的釘死值、"
          f"改語意正本 notes/design/design-boundary-contract.md、"
          f"並在 scripts/test-architecture-guards.sh 補對應負向案")
check(MIN_CHECKS == 100, "MIN_CHECKS 未被調低(釘死 100)", f"實得 {MIN_CHECKS}")

# (b) 三張表的欄名必須與 canon §2.2/2.3/2.4 的欄位表逐字相同
def canon_column_names(text, start_heading, end_heading):
    """抽 canon `### <start>` 到 `### <end>` 之間那張表的首欄資料列。"""
    if text is None:
        return []
    match = re.search(rf"^### {re.escape(start_heading)}[^\n]*\n(.*?)(?=^### {re.escape(end_heading)})",
                      text, re.M | re.S)
    if not match:
        return []
    names, seen_separator = [], False
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", stripped):
            seen_separator = True
            continue
        if seen_separator:
            names.append(stripped.strip("|").split("|")[0].strip())
    return names


for _heading_pair, _columns, _label in (
        (("2.2 ", "2.3 "), ARCH_COLUMNS, "Architecture Boundaries"),
        (("2.3 ", "2.4 "), IFACE_COLUMNS, "Interface & Consistency Contract"),
        (("2.4 ", "2.5 "), DESIGN_COLUMNS, "Software Design")):
    _canon_names = canon_column_names(canon_text, *_heading_pair)
    check(_canon_names == _columns,
          f"守衛的「{_label}」必填欄與 canon §{_heading_pair[0].strip()} 欄位表逐字相同",
          f"canon={_canon_names} guard={_columns}")

# (c) 自我檢查:原始碼裡出現的每個 CURRENT_GROUP 都必須登記在 REQUIRED_GROUPS,
#     反之亦然 —— 防「新增一組卻忘了註冊」(那樣 heartbeat 就看不到它)。
if self_path and os.path.isfile(self_path):
    with open(self_path, encoding="utf-8") as stream:
        own_source = stream.read()
    assigned = set(re.findall(r'^CURRENT_GROUP = "([a-z-]+)"', own_source, re.M))
    check(assigned == set(REQUIRED_GROUPS),
          "原始碼中的 CURRENT_GROUP 集合 = REQUIRED_GROUPS(無未註冊/已註冊但不存在的群組)",
          f"只在原始碼={sorted(assigned - set(REQUIRED_GROUPS))} "
          f"只在 REQUIRED_GROUPS={sorted(set(REQUIRED_GROUPS) - assigned)}")
else:
    check(False, "取得本守衛自身路徑以做清單自我檢查", f"self_path={self_path!r}")

# ── 群組心跳(**主要**防線)────────────────────────────────────────────────
# 逐群組斷言「這一群至少跑過一條」。任何群組被條件式、例外、早退擋掉都會顯性失敗,
# 而且錯誤訊息直接點名是哪一群 —— 這才是防「整組靜默略過」的正解。
CURRENT_GROUP = "files-exist"
missing_groups = [g for g in REQUIRED_GROUPS if groups_seen.get(g, 0) == 0]
if missing_groups:
    failures.append("[heartbeat] 必跑檢查群組完全沒執行:" + ", ".join(missing_groups)
                    + " —— 幾乎都是某個 if 把整段擋掉了")
    checks += 1
else:
    checks += 1

# 檢查數地板:**次級 backstop**,只用來偵測「大幅縮水」(值定義在檔頭,並由
# guard-selfpin 群組釘死,免得「把地板改小」變成一行就能做到的事)。
# 明確不宣稱能防止所有群組被略過 —— 那是上面 heartbeat 的職責;
# 地板抓不到「A 群組消失但 B 群組變多」這種總數持平的情況;
# 「清單被縮小」則由 guard-selfpin 負責。
check(checks >= MIN_CHECKS,
      f"(次級 backstop)結構檢查總數 ≥ {MIN_CHECKS} —— 只偵測大幅縮水,"
      f"完整的群組覆蓋由 heartbeat 負責",
      f"實得 {checks}")

print("=== Design Boundary Contract 結構守衛 ===")
print(f"  • root: {root}")
if failures:
    for failure in failures:
        print(f"  ✗ {failure}")
    print()
    print(f"⛔ design contract 結構守衛:{len(failures)}/{checks} 失敗")
    raise SystemExit(1)
print(f"  ✓ 結構檢查 {checks}/{checks} 全過(語意仍由 G2／G3 Reviewer 判斷)")
print(f"  ✓ heartbeat:{len(REQUIRED_GROUPS)} 個必跑群組全部有執行 "
      f"({', '.join(f'{g}={groups_seen.get(g, 0)}' for g in REQUIRED_GROUPS)})")
print()
print("✅ design contract 結構守衛:全過")
PY
