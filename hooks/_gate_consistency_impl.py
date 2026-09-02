"""_gate_consistency_impl.py — gate 條件摘要 vs 契約檔 §7 正本一致性檢查實作。

設計原則(核心約束,見 dev-setup SKILL.md check 第 8 項):token 一律從母版
docs/dev/readme-contract-extract.md §7(G1/G2/G3 唯一正本)動態抽取,不把 gate 條件字串寫死在本檔 ——
寫死等於讓本檔自己變成第四份會漂移的複本,必須每次重新抽取才驗得住漂移。
gate 條件 token 的唯一寫死內容是下面 SYNONYMS 同義詞映射表(小且穩定,映射本身
不是 gate 條件)。reviewer-selection 則是契約檔 §7 已定義、跨 G1/G2/G3 不可反轉的
角色順序；下方以順序、否定、留痕與最後手段等行為特徵驗證，而非比對一段脆弱的逐字
複本。

抽取管線(每一步都是通用規則,非本文內容特例):
  1. 從 §7 原文(保留換行,供步驟 2 找列點邊界)切出 G1/G2/G3 各自的定義子句。
  2. 子句內攤平空白,抓所有 **粗體** 片語;只留「第一個」或「以 + 串接」的片語 ——
     §7 開頭聲明摘要只寫「關鍵條件」,而非條件之後的補充說明(如 G1 條件後半的
     reviewer 抽查職責是補充說明,不是摘要三處需要覆誦的條件),+ 則是文件自己
     用來串接多條件的記號。串接寫法兩種皆收:`**+ 條件**`(+ 在粗體內;現行 G3
     格式)與 `+ **條件**`(+ 在粗體外;VNext 共享契約 §1/§2 引用新錨
     「**Evidence 契約全過**」「**Verification Profile**」「**Demo verdict**」的
     寫法)—— 只認前者會讓後者被靜默丟棄,新錨缺席也驗不出來。
  3. 每個留下的片語再以 + 切成更細的「條件詞組」。
  4. 條件詞組若含「逐 <大寫字母>」(如「逐 S」)之類的 per-ID 修飾語,截斷、只留
     修飾語之前的核心詞(修飾語是「怎麼驗」的說明,不是條件本身);截斷後若變空字串
     則整條回退用原詞組,不允許因為截斷而把 token 弄丟。
  5. 每個條件詞組再依「英數/CJK 分界」拆成最終 token(如「Owner Calls 全裁決」→
     ["Owner Calls","全裁決"]),讓同義詞映射可以只作用在英文縮寫那一半。

失敗一律 fail-loud(exit 2):抽不到 §7 段落、抓不到某 gate 定義、token 清單為空、
摘要位置的 **Gn** anchor 找不到或找到超過一次、儲存格切分異常 —— 都視為「本檢查
本身失效」,不可以「token 清單剛好是空的所以沒發現漂移」蒙混過關。
exit 0 = 三處摘要皆一致;exit 1 = 發現漂移(非本檔失效,是真的抓到不一致)。

G3 的「本次 S 全綠」是機械錨點之一，須如其他 G3 條件一樣以 **粗體** 留在 §7 正本；
因此會隨動態 token 抽取出現在每處摘要的比對中。
"""
import os
import re
import sys

sys.dont_write_bytecode = True   # 對齊 _obs/_doctor:不落 __pycache__
from typing import NoReturn

MASTER = os.environ.get("DEVFLOW_MASTER") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PLUGIN 預設由本檔位置推導(hooks/ 的上一層 = plugin root),不寫死安裝路徑 ——
# plugin 改由 marketplace 安裝後,實際 root 是
# ~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/,寫死的舊路徑會讀不到檔。
# 2026-08 單一 repo 合併後,母版子目錄層消失,MASTER 與 PLUGIN 兩個 fallback
# 指向同一個 repo root(各自保留環境變數做第一順位,selftest 靠它們注入假 repo)。
PLUGIN = os.environ.get("DEVFLOW_PLUGIN") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTRACT = os.path.join(MASTER, "docs", "dev", "readme-contract-extract.md")
SKILL = os.path.join(PLUGIN, "skills", "dev-flow", "SKILL.md")

# ---- 比對表(表驅動;共享契約「同步位置」清單的機械化身)----
# 每列 = (gate 標籤, 該 gate 的模板檔名)。順序即 §7 內 G1→G2→G3 的定義順序,
# slice_gate_clause 以「下一列的標籤」當子句終點。每個 gate 的 token 檢查位置固定
# 三處:plugin dev-flow SKILL.md 階段表格、契約檔 §3 表格、該 gate 模板頂註;
# reviewer-selection 檢查位置 = 契約檔 §7 + SKILL + 三份模板頂註。
# VNext 新錨(G2「Verification Profile」「Demo verdict」、G3「Evidence 契約全過」)
# 不寫死在此 —— 條文落入 §7 正本後由動態抽取自動涵蓋(selftest p4_ 案為證)。
GATE_TABLE = (
    ("G1", "2-decision.md"),
    ("G2", "4-spec.md"),
    ("G3", "7-review.md"),
)
TEMPLATES = {gate: os.path.join(MASTER, "_templates", fname) for gate, fname in GATE_TABLE}

# ---- 唯一允許寫死的內容:同義詞映射表(小且穩定;映射的是「詞的異寫」不是「gate 條件」) ----
SYNONYMS = [
    (re.compile(r'Owner Calls|(?<![A-Za-z])OC(?![A-Za-z])'), 'OC'),
    (re.compile(r'Drafting Decisions|(?<![A-Za-z])DD(?![A-Za-z])'), 'DD'),
    (re.compile(r'既有[^,。;、\n]{0,8}全綠|回歸[^,。;、\n]{0,4}綠'), 'REGR'),
]

TOKEN_TRUNC = re.compile(r'逐\s*[A-Z]\b.*$')
SCRIPT_RUN = re.compile(r'[A-Za-z0-9/]+(?:\s[A-Za-z0-9/]+)*|[一-鿿]+')
REVIEWER_SELECTION_CLAUSE = re.compile(r'審查者(?:產生|依序)[^。！？]*', re.IGNORECASE)
REVIEWER_SELECTION_STEPS = (
    ("適格人類 reviewer", re.compile(r'適格人類(?:第二人|reviewer)?', re.IGNORECASE)),
    ("fresh-context reviewer Agent", re.compile(r'fresh-contextrevieweragent', re.IGNORECASE)),
    ("owner 自審", re.compile(r'owner自審', re.IGNORECASE)),
)
REVIEWER_NEGATED_STEPS = (
    ("適格人類 reviewer", re.compile(
        r'(?:不|未|勿|禁止|不得|無需)(?:使用|選擇|選用|派|由|找|安排)?'
        r'適格人類(?:第二人|reviewer)?', re.IGNORECASE)),
    ("fresh-context reviewer Agent", re.compile(
        r'(?:不|未|勿|禁止|不得|無需)(?:派|使用|選擇|選用|找|安排|由)?'
        r'fresh-contextrevieweragent', re.IGNORECASE)),
    ("owner 自審", re.compile(
        r'(?:不|未|勿|禁止|不得|無需)(?:准|可|能|得)?owner自審', re.IGNORECASE)),
)
REVIEWER_RECORD = re.compile(r'留痕|記錄')
REVIEWER_LAST_RESORT = re.compile(r'最後手段')
REVIEWER_NEGATED_RECORD = re.compile(
    r'(?:不|未|勿|禁止|不得|無需)(?:需|需要|要|必須|用)?(?:記錄|留痕)')
REVIEWER_NEGATED_LAST_RESORT = re.compile(
    r'(?:不|未|非|勿|禁止|不得|無需)(?:是|屬於)?最後手段')


def die(msg: str) -> NoReturn:
    print(f"⛔ gate-consistency:{msg}", file=sys.stderr)
    sys.exit(2)


def canon(text):
    for pat, tag in SYNONYMS:
        text = pat.sub(tag, text)
    return text


def norm(text):
    return re.sub(r'\s+', '', canon(text))


def read(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        die(f"讀不到 {path}({e})")


def slice_section(text, start_pat, end_pat, label):
    """切出兩個標題間的區段文字(保留換行)。start_pat 必須恰好出現一次,否則視為
    anchor 不穩定,fail-loud。"""
    starts = list(re.finditer(start_pat, text))
    if len(starts) == 0:
        die(f"找不到區段起點 {label}(pattern={start_pat})")
    if len(starts) > 1:
        die(f"{label} 的起點 pattern 命中 {len(starts)} 次,anchor 不唯一")
    tail = text[starts[0].start():]
    m2 = re.search(end_pat, tail)
    if not m2:
        die(f"{label}:找不到區段終點(pattern={end_pat}),不可靜默吃到檔尾"
            f"(下一個同級標題若被重排/刪除也必須現形,不能悄悄併入本區段)")
    return tail[:m2.start()]


def assert_gate_labels_unique(g7_raw):
    """補 slice_gate_clause 既有 re.search 的洞:re.search 只找第一個,§7 切片內若
    「Gn =」重複出現,既有邏輯會靜默取第一個當定義、忽略後面的重複定義。這裡在切每個
    gate 之前先驗每個 Gn = 標記恰好出現一次,不唯一就報出是哪個 gate 重複並 fail-loud;
    只加這道防護,不動 slice_gate_clause 本身的抽取邏輯。"""
    for label, _ in GATE_TABLE:
        hits = list(re.finditer(re.escape(label) + r'\s*=', g7_raw))
        if len(hits) > 1:
            die(f"§7「{label} =」重複出現 {len(hits)} 次,anchor 不唯一(必須恰好一次;"
                f"重複的 gate = {label})")


def slice_gate_clause(g7_raw, label, next_label):
    """從 §7 原文(換行保留)切出單一 gate 的定義子句,邊界用下一個 gate 的
    「<next_label> =」標記(GATE_TABLE 順序決定),表尾 gate(next_label=None)則用
    下一個列點(換行+ '- ')。"""
    m = re.search(re.escape(label) + r'\s*=', g7_raw)
    if not m:
        die(f"§7 找不到「{label} =」定義")
    start = m.start()
    if next_label is not None:
        m2 = re.search(re.escape(next_label) + r'\s*=', g7_raw[start:])
        if not m2:
            die(f"§7 找不到「{label}」定義的結尾(下一個 {next_label} = 標記缺失)")
        return g7_raw[start:start + m2.start()]
    m2 = re.search(r'\n-\s', g7_raw[start:])
    return g7_raw[start:] if not m2 else g7_raw[start:start + m2.start()]


def extract_tokens(raw_clause, gate_label):
    clause = re.sub(r'\s+', ' ', raw_clause).strip()
    kept = []
    for i, m in enumerate(re.finditer(r'\*\*(.+?)\*\*', clause)):
        span = m.group(1).strip()
        # + 串接兩種寫法皆收:span 自帶 + 前綴(**+ 條件**),或粗體外前一個非空白
        # 字元是 +(+ **條件**;VNext 共享契約引用新錨的寫法)。
        joined_by_plus = span.startswith('+') or clause[:m.start()].rstrip().endswith('+')
        if i == 0 or joined_by_plus:
            kept.append(span)
    if not kept:
        die(f"{gate_label}:§7 抽不到任何 **粗體** 條件片語,§7 格式可能已變,需要人工檢查")
    phrases = []
    for span in kept:
        span = span.lstrip('+').strip()
        phrases.extend(p.strip() for p in span.split('+') if p.strip())
    tokens = []
    for phrase in phrases:
        truncated = TOKEN_TRUNC.sub('', phrase).strip()
        use = truncated if truncated else phrase  # 截斷成空 → 回退用原詞組,不許把 token 弄丟
        tokens.extend(m.group(0) for m in SCRIPT_RUN.finditer(use))
    if not tokens:
        die(f"{gate_label}:條件詞組切完後 token 清單為空,抽取規則可能與正本格式不符")
    return tokens


def find_table_cell(text, gate_label, file_label):
    """找出含 **Gn** 的表格列,回傳該列被 | 切開後、真正含 **Gn** 的那一格 ——
    不可用整列/整檔比對,否則其他欄位(如「產出」欄提過 Drafting Decisions)會
    造成漏抓(cross-column false negative)。"""
    marker = f"**{gate_label}**"
    lines = [ln for ln in text.splitlines() if marker in ln]
    if len(lines) == 0:
        die(f"{file_label}:找不到 {marker} 標記列(anchor 遺失或格式已變)")
    if len(lines) > 1:
        die(f"{file_label}:{marker} 標記列出現 {len(lines)} 次,anchor 不唯一,無法安全定位")
    cells = [c for c in lines[0].split('|') if marker in c]
    if len(cells) != 1:
        die(f"{file_label}:{marker} 所在儲存格切分異常({len(cells)} 格含 marker)")
    return cells[0]


def find_template_header(text, file_label):
    """模板頂註 = frontmatter 之後、第一個 `## ` 章節標題之前的區塊(執行清單所在)。"""
    m = re.search(r'\n##[ \t]', text)
    if not m:
        die(f"{file_label}:找不到第一個 ## 標題,無法界定模板頂註範圍")
    return text[:m.start()]


def check(tokens, location_text):
    nl = norm(location_text)
    return [t for t in tokens if norm(t) not in nl]


def reviewer_selection_error(location_text):
    """驗一個正向、完整的 reviewer-selection 子句，而非在整段找 token。"""
    flattened = re.sub(r'\s+', '', location_text)
    clauses = REVIEWER_SELECTION_CLAUSE.findall(flattened)
    if len(clauses) == 0:
        return "缺少以「審查者產生」或「審查者依序」開始的正向選擇子句"
    if len(clauses) > 1:
        return "reviewer-selection 子句不唯一,無法安全判定唯一的 fallback 順序"
    clause = clauses[0]

    for label, negation in REVIEWER_NEGATED_STEPS:
        if negation.search(clause):
            return f"不得否定「{label}」步驟"

    matches = [(label, pattern.search(clause)) for label, pattern in REVIEWER_SELECTION_STEPS]
    absent = [label for label, match in matches if match is None]
    if absent:
        return f"缺步驟「{'、'.join(absent)}」"

    positions = [match.start() for _, match in matches]
    if positions != sorted(positions):
        return "順序必須是適格人類 reviewer → fresh-context reviewer Agent → owner 自審"

    owner_start = matches[-1][1].start()
    owner_tail = clause[owner_start:]
    if REVIEWER_NEGATED_RECORD.search(owner_tail):
        return "不得否定 owner 自審的記錄要求"
    if REVIEWER_NEGATED_LAST_RESORT.search(owner_tail):
        return "不得否定 owner 自審的最後手段限制"
    if not REVIEWER_RECORD.search(owner_tail) or not REVIEWER_LAST_RESORT.search(owner_tail):
        return "owner 自審必須明示為有記錄的最後手段"
    return None


def main():
    extract_text = read(EXTRACT)
    g7_raw = slice_section(extract_text, r'##\s*7\.', r'\n##\s*8\.', "契約檔 §7")
    assert_gate_labels_unique(g7_raw)
    g3_table_text = slice_section(extract_text, r'##\s*3\.', r'\n##\s*5\.', "契約檔 §3")
    skill_text = read(SKILL)

    lines_out = []
    all_ok = True
    n_checks = 0
    n_bad = 0

    reviewer_locations = [
        ("契約檔 §7", g7_raw),
        ("plugin dev-flow SKILL.md", skill_text),
    ]

    for idx, (gate, _) in enumerate(GATE_TABLE):
        next_gate = GATE_TABLE[idx + 1][0] if idx + 1 < len(GATE_TABLE) else None
        raw_clause = slice_gate_clause(g7_raw, gate, next_gate)
        tokens = extract_tokens(raw_clause, gate)
        lines_out.append(f"[{gate}] 正本 tokens(契約檔 §7 動態抽取):{' / '.join(tokens)}")

        locations = [
            ("plugin dev-flow SKILL.md 階段表", find_table_cell(skill_text, gate, "plugin dev-flow SKILL.md")),
            ("契約檔 §3 七份文檔表", find_table_cell(g3_table_text, gate, "契約檔 §3 表")),
        ]
        tpl_path = TEMPLATES[gate]
        tpl_text = read(tpl_path)
        tpl_header = find_template_header(tpl_text, os.path.basename(tpl_path))
        locations.append((f"_templates/{os.path.basename(tpl_path)} 頂註", tpl_header))
        reviewer_locations.append((f"_templates/{os.path.basename(tpl_path)} 頂註", tpl_header))

        for loc_label, loc_text in locations:
            n_checks += 1
            missing = check(tokens, loc_text)
            if missing:
                all_ok = False
                n_bad += 1
                lines_out.append(f"  ✗ {loc_label}:缺 token「{'、'.join(missing)}」")
            else:
                lines_out.append(f"  ✓ {loc_label}")

    lines_out.append("[reviewer-selection] 契約檔 §7 與 G1/G2/G3 模板的角色順序")
    for loc_label, loc_text in reviewer_locations:
        n_checks += 1
        error = reviewer_selection_error(loc_text)
        if error:
            all_ok = False
            n_bad += 1
            lines_out.append(f"  ✗ {loc_label}:reviewer-selection {error}")
        else:
            lines_out.append(f"  ✓ {loc_label}")

    print(f"=== gate-consistency:契約檔 §7 正本 vs 三處摘要({n_checks} 格)===")
    print(f"正本:{EXTRACT} §7")
    print()
    print("\n".join(lines_out))
    print()
    if all_ok:
        print(f"✅ 全部一致({n_checks}/{n_checks} 通過)")
        sys.exit(0)
    else:
        print(f"❌ 發現 {n_bad}/{n_checks} 處漂移(見上方 ✗ 列)")
        sys.exit(1)


if __name__ == "__main__":
    main()
