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
import ast
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
# 地板=實得數不留餘裕(家規):這個數字必須等於當下的實際 checks 總數,不是隨手抓的
# 下限,否則就是形同虛設的鬆散 backstop(2026-08-17 F-2 MED 裁決,同 check-realworld.sh
# 的 N-2 慣例)。改動任何 check()/迴圈次數後,重跑本檔取得實際 checks 數並同步這裡。
# ⚠️ 差一算法(本檔特有,check-realworld.sh 沒有這個坑):這條地板本身是用
# `check(checks >= MIN_CHECKS, …)` 表達,而 check() 的 condition 在呼叫當下就已求值
# ——也就是「呼叫這條地板檢查之前累積的 checks 數」在跟 MIN_CHECKS 比,這條地板檢查
# 自己執行完才會讓 checks 再 +1,變成最終印出的總數。所以「地板=實得數」在這裡的
# 實得數是**最終印出總數 − 1**,不是最終印出總數本身(若把 MIN_CHECKS 設成最終印出
# 的那個數字,這條地板檢查永遠會自己讓自己失敗一格)。同步時:先跑
# `scripts/check-design-contract.sh` 看輸出「結構檢查 N/N 全過」,MIN_CHECKS 填 N-1。
MIN_CHECKS = 164

# check_skip( 呼叫點零圍堵(2026-08-17 F-2 HIGH-2):scripts/*.sh 全體(不含定義行)
# 允許存在的 check_skip( 呼叫點總數上限。check_skip 是「顯性跳過仍計入 checks」的
# 合法逃生門(見 check-realworld.sh 的 check_skip 定義與其唯一呼叫點),但逃生門
# 一多就形同讓真斷言全面下崗卻沒人管制。新增顯性跳過必須同步調高這個數字,並在
# 呼叫處註明理由 —— 這裡的常數本身也被 guard-selfpin 釘死,不能悄悄改大。
EXPECTED_CHECK_SKIP_CALLS = 1

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
extract_text = read("docs/dev/readme-contract-extract.md")

check(template_text is not None, f"{TEMPLATE} 存在")
check(example_text is not None, f"{EXAMPLE} 存在")
check(extract_text is not None, "docs/dev/readme-contract-extract.md 存在")
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
# ── 7. 契約檔只保留摘要與正本連結(不得重抄表格) ───────────────────────────
if extract_text is not None:
    for heading in TABLE_HEADINGS:
        # Software Design 是通用詞,只擋「表頭形式」(出現在 markdown 表格列裡)
        leaked = [line for line in extract_text.splitlines()
                  if line.strip().startswith("|") and heading in line]
        check(not leaked, f"契約檔未重抄「{heading}」表頭(正本在 {TEMPLATE})",
              f"洩漏於={leaked[:1]}")
    for column in ("Forbidden dependencies", "Transaction / Consistency boundary", "Test seam"):
        check(column not in extract_text,
              f"契約檔未重抄欄位「{column}」(正本在 {TEMPLATE})")
    check(SECTION in extract_text, f"契約檔有 {SECTION} 摘要")
    check(CANON in extract_text, f"契約檔連到語意正本 {CANON}")

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
    if extract_text is not None:
        leaked = [mark for mark in ("⑨", "⑩", "⑪") if mark in extract_text]
        check(not leaked,
              "契約檔未出現第三份觸發條件枚舉(11 條清單的尾號 ⑨⑩⑪)",
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

        # ── 內容檢查(2026-08 final verdict M-3)──────────────────────────────
        # 舊版只比行數。實測(fresh reviewer 重現):把七筆全改成
        # `- Design boundary finding:n-a` → 行數仍相等 → exit 0、141/141 全過。
        # example 的 Design Boundary Contract 是釘死的 applicable,所以每一筆都必須是
        # 實際作答:非空、非佔位、且五問①～⑤齊 —— 只填一個籠統結論不算。
        # 這不是語意判斷,是「有沒有逐問作答」的結構檢查(同檔 na_reason_ok 已是同型做法)。
        PLACEHOLDERS = ("n-a", "n/a", "na", "none", "-", "—", "todo", "tbd",
                        "<待填>", "待填", "pending", "n-a(略)")
        for index, raw in enumerate(
                re.findall(r"^- Design boundary finding:(.*)$", example_notes, re.M), start=1):
            value = raw.strip()
            label = f"example Stage 6 第 {index} 筆 T Review Log 的 Design boundary finding"
            check(bool(value), f"{label} 非空", "冒號後是空的")
            check(value.lower().strip("。.") not in PLACEHOLDERS,
                  f"{label} 不是佔位值(契約為 applicable,不得記 n-a)", f"實得={value[:40]!r}")
            missing_marks = [m for m in "①②③④⑤" if m not in value]
            check(not missing_marks,
                  f"{label} 五問①～⑤齊(逐問作答,不得只給籠統結論)",
                  f"缺 {''.join(missing_marks)};實得={value[:60]!r}")

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
check(MIN_CHECKS == 164, "MIN_CHECKS 未被調低(釘死 164;地板=實得數)", f"實得 {MIN_CHECKS}")
check(EXPECTED_CHECK_SKIP_CALLS == 1,
      "EXPECTED_CHECK_SKIP_CALLS 未被調整(釘死 1;check_skip 零圍堵的常數本身不得被悄悄改大)",
      f"實得 {EXPECTED_CHECK_SKIP_CALLS}")

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
    # (d) 斷言不得被改成恆真。2026-08 驗收實測抓到的殘留:把
    #     `check(rows >= 1, …)` 改成 `check(True, …)` —— 檢查數不變、群組還在、
    #     長度釘死也全過,整條斷言卻已解除武裝。長度類的釘死本質上防不到這一類,
    #     這裡用最直接的方式擋:原始碼裡不得出現 `check(True`(2026-08-17 擴成三變體
    #     `check(True` / `check(1 == 1` / `check(not False`——獨立審查實測 `check(1 == 1`
    #     繞得過只認字面 `True` 的舊正則,見 test-architecture-guards.sh 對應案例)。
    #     `check(False, …)` 是刻意的顯性失敗(例如下面的 else 分支),允許保留。
    #     只掃**敘述開頭**的呼叫(`^\s*check(…`),不掃註解與字串裡的字面 ——
    #     否則本段自己的註解與標籤文字就會被誤判成命中。
    always_true = re.findall(r"^\s*check\(\s*(?:True|1\s*==\s*1|not\s+False)\b", own_source, re.M)
    check(not always_true,
          "沒有任何斷言被改成恆真(原始碼不得出現 `check(True`/`check(1 == 1`/`check(not False`)",
          f"命中 {len(always_true)} 處 —— 恆真斷言等於該檢查被靜默解除武裝")
else:
    check(False, "取得本守衛自身路徑以做清單自我檢查", f"self_path={self_path!r}")

# (e) 跨檔恆真斷言掃描(2026-08-17,推廣自(d))——(d) 只掃本檔自己的原始碼,
#     scripts/*.sh 底下其他檢查腳本裡的 `check(True…)` 完全沒人看(既有實例:
#     check-realworld.sh:191,已改用 check_skip 顯性標記;此掃描是防再有下一個)。
#     這裡改掃全體:glob root/scripts/*.sh,逐檔逐行套同一組三變體正則。
#     防禦邊界(誠實承認,同 GS-9 的邊界寫法):這份模式清單防的是**單點手滑**——
#     手殘把一條真斷言改成 check(True) 之類,不防**蓄意構造**的恆真式
#     (例如 check(2 > 1, …)、check(len(x) >= 0, …)這類邏輯上恆真但語法上正常的
#     斷言,列不完,也不是本掃描宣稱能擋的範圍)。
#     check_skip(...) 是合法的顯性跳過(印「↷ 跳過」且仍計入 checks),呼叫字面是
#     `check_skip(` 不是 `check(`,不落在上面兩組恆真正則的命中範圍內,不屬於恆真
#     掃描的對象 —— 但它本身另外被下面的「零圍堵」計數盯著。
#
# 2026-08-17 F-2 HIGH-1 修法(獨立審查抓到的不對稱):舊版跨檔掃描是「逐行讀、
# 逐行 re.match」,而(d)的自掃是「整檔讀入、re.M 對整份原始碼跑 re.findall」——
# 同一套正則,兩種完全不同的用法。差別要命:正則本體的 `\s*` 涵蓋換行,能配到
# 多行排版的 `check(\n    True,\n    "...")`,但逐行版一次只喂一行給 .match(),
# `check(` 那一行單獨看不到 `True` 在下一行,永遠配不上 —— 多行排版的恆真斷言對
# 別的檔案(跨檔)完全隱形,對本檔自己(d)卻抓得到,是同一份防線裡的不對稱實作。
# 修法:跨檔掃描比照(d)整檔讀入、同一顆正則用 re.finditer 找出所有相符起點,
# 命中行號用 `match.start()` 之前的換行數回推(而不是逐行讀取判斷)。
CURRENT_GROUP = "guard-selfpin"
ALWAYS_TRUE_RE = re.compile(r"^\s*check\(\s*(?:True|1\s*==\s*1|not\s+False)\b", re.M)
# check_skip( 呼叫點計數用的正則:只認**敘述開頭**的呼叫(同 ALWAYS_TRUE_RE 的寫法),
# 不掃註解裡提到「check_skip(」字樣的文字(本檔上面的說明段落就有,若不鎖行首會
# 誤把自己的註解算成呼叫點)。`def check_skip(` 開頭是 `def `,不落在 `^\s*check_skip\(`
# 命中範圍內,天生排除定義行,不需要另外過濾。
CHECK_SKIP_CALL_RE = re.compile(r"^\s*check_skip\(", re.M)
_scan_dir = os.path.join(root, "scripts")
_scan_files = sorted(f for f in os.listdir(_scan_dir) if f.endswith(".sh")) if os.path.isdir(_scan_dir) else []
print(f"掃 {len(_scan_files)} 檔(scripts/*.sh 恆真斷言跨檔掃描)")
if len(_scan_files) == 0:
    print("FATAL: 掃到 0 支 scripts/*.sh,跨檔掃描沒有真的跑——不是「沒有恆真斷言」",
          file=sys.stderr)
    sys.exit(2)

# 掃描清單哨兵(2026-08-17 F-2 MED):跨檔掃描的「掃到誰」完全交給 glob 結果決定,
# 若掃描目錄/pattern 被悄悄改窄(例如改成只掃某個子集、副檔名判斷被弱化),
# 上面「len == 0」的防線擋不住 —— 目錄裡還有其他 .sh 檔,glob 不會回傳 0。
# 這裡改成白名單式哨兵:check-realworld.sh(check_skip 的定義與唯一呼叫點所在)
# 與 check-gate-twin.sh(另一支帶自己 check() 系列 helper 的常駐檢查腳本)兩支
# 一定要出現在掃描清單裡,少一支就代表掃描來源被縮小,顯性 exit 2(不是靜默略過
# 這批檢查,也不是留給 check() 記一筆失敗后繼續跑其他檢查 —— 掃描清單本身失格,
# 後面所有基於這份清單算出來的統計都不可信,沒有「部分可信」這回事)。
_required_scan_targets = ["check-realworld.sh", "check-gate-twin.sh"]
_missing_scan_targets = [f for f in _required_scan_targets if f not in _scan_files]
if _missing_scan_targets:
    print(f"FATAL: 跨檔掃描清單缺 {_missing_scan_targets}(掃到 {_scan_files})"
          " —— 掃描來源被縮小,不是這幾支檔案不存在就該悄悄跳過", file=sys.stderr)
    sys.exit(2)

_cross_hits = []
_check_skip_hits = []
_file_texts = {}
for _fname in _scan_files:
    _fpath = os.path.join(_scan_dir, _fname)
    with open(_fpath, encoding="utf-8") as _stream:
        _ftext = _stream.read()
    _file_texts[_fname] = _ftext
    for _m in ALWAYS_TRUE_RE.finditer(_ftext):
        _lineno = _ftext.count("\n", 0, _m.start()) + 1
        _cross_hits.append(f"scripts/{_fname}:{_lineno}")
    for _m in CHECK_SKIP_CALL_RE.finditer(_ftext):
        _lineno = _ftext.count("\n", 0, _m.start()) + 1
        _check_skip_hits.append(f"scripts/{_fname}:{_lineno}")
check(not _cross_hits,
      "跨檔掃描:scripts/*.sh 無恆真斷言(check(True / check(1 == 1 / check(not False 三變體,"
      "含多行排版如 check(\\n    True,\\n    ...))",
      ("無命中" if not _cross_hits else "命中 " + ", ".join(_cross_hits)))

# (f) F3(2026-08-17 獨立審查):恆真偵測從「可枚舉黑名單」升級成 AST 常數運算式
# 判定。上面 (d)/(e) 的三變體字面黑名單擋不住 check(2 > 1, "poison")、
# check("a" != "b", …) 這類「邏輯恆真但不在字面清單」的斷言 ——:546 的邊界宣告
# 自己承認清單列不完。這裡對每個敘述開頭的 check( 呼叫點抽出第一個參數,
# ast.parse 後全樹只含常數節點 = 常數運算式;求值為**真** → 紅。求值為**假**
# 不紅:check(False, …) 是刻意的顯性失敗(如 else 分支),(d) 已明文允許保留。
# 邊界(誠實承認,接續 :546 的寫法):len("x") > 0、max(1,2) >= 1 這類**含呼叫**
# 的恆真式仍不在偵測範圍 —— 判定它們要執行任意程式碼,不做;本層擋的是
# 「不查表也寫得出來」的常數比較式,黑名單三變體照舊保留當第一層。
_CONST_NODES = (ast.Expression, ast.Constant, ast.Tuple, ast.List,
                ast.UnaryOp, ast.BinOp, ast.BoolOp, ast.Compare,
                ast.unaryop, ast.operator, ast.boolop, ast.cmpop, ast.Load)
CHECK_CALL_RE = re.compile(r"^[ \t]*check\(", re.M)


def _check_first_arg(text, start):
    """start = 'check(' 的 '(' 之後;回傳第一個頂層參數原文,抽不出來回 None。"""
    depth, i, quote, esc, buf = 0, start, None, False, []
    while i < len(text) and i - start <= 2000:
        ch = text[i]
        if quote:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "([{":
            depth += 1
            buf.append(ch)
        elif ch in ")]}":
            if depth == 0 and ch == ")":
                return "".join(buf)
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            return "".join(buf)
        else:
            buf.append(ch)
        i += 1
    return None


def _const_truthy(src):
    """src 是不是「全常數節點且求值為真」的運算式;解析不了/含名稱或呼叫 → False。

    裸字串/bytes 常數**不算**:scripts/ 裡存在第一參數是 ID 字串的不同簽名
    check() 家族(devflow-evidence-gauntlet.sh 的 check("E13", cond, …)),
    對它們而言字串是識別碼不是斷言 —— 這是本判定的明文邊界;要毒化那種簽名
    得改第二參數,那是運算式,照樣落在本判定範圍內。"""
    try:
        tree = ast.parse(src.strip(), mode="eval")
    except (SyntaxError, ValueError):
        return False
    if not all(isinstance(n, _CONST_NODES) for n in ast.walk(tree)):
        return False
    if isinstance(tree.body, ast.Constant) and isinstance(tree.body.value, (str, bytes)):
        return False
    try:
        return bool(eval(compile(tree, "<const-check>", "eval"), {"__builtins__": {}}, {}))
    except Exception:
        return False


_const_hits = []
for _fname, _ftext in _file_texts.items():
    for _m in CHECK_CALL_RE.finditer(_ftext):
        _arg = _check_first_arg(_ftext, _m.end())
        if _arg is not None and _const_truthy(_arg):
            _lineno = _ftext.count("\n", 0, _m.start()) + 1
            _const_hits.append(f"scripts/{_fname}:{_lineno} check({_arg.strip()[:40]}…)")
check(not _const_hits,
      "跨檔掃描:check() 第一參數無「常數運算式且恆真」(AST 判定,補黑名單的洞;"
      "check(False,…) 顯性失敗合法)",
      ("無命中" if not _const_hits else "命中 " + ", ".join(_const_hits)))

# check_skip( 零圍堵(2026-08-17 F-2 HIGH-2):顯性跳過是合法逃生門,但逃生門一多
# 就等於「該有真斷言的地方全面改成不驗」卻沒人管制。呼叫點總數(不含定義行)
# 必須恰等於釘死值 EXPECTED_CHECK_SKIP_CALLS —— 多出來(新增顯性跳過卻沒同步這個
# 常數)顯性失敗,並要求在呼叫處註明理由。
check(len(_check_skip_hits) == EXPECTED_CHECK_SKIP_CALLS,
      f"跨檔掃描:scripts/*.sh 的 check_skip( 呼叫點總數(不含定義行)= "
      f"{EXPECTED_CHECK_SKIP_CALLS}(新增顯性跳過需同步此常數,並在呼叫處註明理由)",
      f"實得 {len(_check_skip_hits)} 處:{', '.join(_check_skip_hits) or '無'}")

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
