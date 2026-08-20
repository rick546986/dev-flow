"""查詢意圖線索詞與問句框架詞(query 與 retrieval 共用的單一正本)。

**為什麼獨立一檔**:同一組詞被兩邊用,但用途不同 ——

  query.py     用它**判斷意圖**(「為什麼」→ WHY)
  retrieval.py 用它**剝掉問句框架**再算 coverage

如果兩邊各留一份,改了一邊沒改另一邊會出現最難察覺的失敗:意圖分類對了、
coverage 卻把框架詞算進分母,於是中文問句永遠達不到相關性門檻、
retrieval 對每一句中文都回 NO_RELIABLE_MATCH,而所有單元測試都是綠的。

「框架詞」的定義:對「問的是什麼」有貢獻、對「答案內容」沒有貢獻的詞。
「之前為什麼修改 registration」的內容只有 `registration` 一個詞;
前面那七個字是問法,不是主題。
"""
import re

WHY = "WHY"
HISTORY = "HISTORY"
CURRENT = "CURRENT"
HOW = "HOW"
DOMAIN = "DOMAIN"
INTENT = "INTENT"
DISCOVERY = "DISCOVERY"

# (pattern, weight);中文與英文各自獨立列 —— 中文問句的線索常是語法結構
# (「為什麼…改」)而不是單一詞,不能靠翻譯英文詞表得到。
INTENT_CUES = {
    WHY: ((r"為什麼", 3), (r"為何", 3), (r"什麼原因", 3), (r"憑什麼", 2),
          (r"\bwhy\b", 3), (r"\brationale\b", 2), (r"理由", 2), (r"權衡", 2),
          (r"當初", 2), (r"\btrade-?off\b", 2)),
    HISTORY: ((r"之前", 3), (r"以前", 3), (r"過去", 2), (r"曾經", 2),
              (r"當時", 2), (r"歷史", 2), (r"改過", 2),
              (r"\bpreviously\b", 3), (r"\bhistory\b", 2),
              (r"\bwhat happened\b", 3), (r"\bused to\b", 2)),
    CURRENT: ((r"現在", 3), (r"目前", 3), (r"當前", 3), (r"現行", 3),
              (r"哪一?張", 2), (r"哪一?個", 2), (r"用的是", 2),
              (r"\bcurrent(?:ly)?\b", 3), (r"\bnow\b", 2),
              (r"\bwhich\b", 2), (r"\bwhat is\b", 1)),
    HOW: ((r"怎麼做", 3), (r"如何", 3), (r"步驟", 3), (r"怎麼跑", 3),
          (r"怎麼部署", 3), (r"操作流程", 2),
          (r"\bhow (?:to|do)\b", 3), (r"\bsteps?\b", 2),
          (r"\brunbook\b", 3), (r"\bprocedure\b", 2)),
    DOMAIN: ((r"是什麼意思", 3), (r"代表什麼", 3), (r"定義", 3), (r"術語", 3),
             (r"業務規則", 3), (r"真實世界", 2), (r"語意", 2),
             (r"\bmean(?:s|ing)?\b", 3), (r"\bdefinition\b", 3),
             (r"\bglossary\b", 3), (r"\bbusiness rule\b", 3),
             (r"\bdomain\b", 2)),
    INTENT: ((r"打算", 3), (r"計畫", 3), (r"未來", 3), (r"將來", 3),
             (r"想往", 2), (r"方向", 2), (r"藍圖", 3), (r"預計", 3),
             (r"\bintend(?:ed|s)?\b", 3), (r"\broadmap\b", 3),
             (r"\bplanned\b", 3), (r"\bgoing to\b", 2), (r"\bfuture\b", 2)),
    DISCOVERY: ((r"有哪些", 3), (r"列出", 3), (r"盤點", 3), (r"全部", 2),
                (r"\blist\b", 3), (r"\ball\b", 2), (r"\benumerate\b", 3)),
}

# ── 剝除用的 pattern:與分類用的 INTENT_CUES **不是同一份** ──────────────────
# 分類可以用「怎麼部署」當線索(它明確指向 HOW);但剝除**不能**用它 ——
# 「部署」是內容詞,連著問法一起剝掉,coverage 的分子就跟著消失,
# 「怎麼部署?」會查不到 deploy skill。所以這裡只列**純問法**的線索,
# 帶內容的線索(怎麼部署 / 步驟 / 業務規則 / 藍圖 / 歷史 / 改過…)刻意不列。
PURE_FRAME_CUES = (
    r"為什麼", r"為何", r"什麼原因", r"憑什麼", r"\bwhy\b",
    r"之前", r"以前", r"過去", r"曾經", r"當時", r"當初",
    r"\bpreviously\b", r"\bwhat happened\b", r"\bused to\b",
    r"現在", r"目前", r"當前", r"現行", r"哪一?張", r"哪一?個",
    r"\bcurrent(?:ly)?\b", r"\bnow\b", r"\bwhich\b", r"\bwhat is\b",
    r"怎麼做", r"如何", r"\bhow (?:to|do)\b",
    r"是什麼意思", r"代表什麼", r"\bmean(?:s|ing)?\b", r"\bdefinition\b",
    r"打算", r"預計", r"\bintend(?:ed|s)?\b", r"\bgoing to\b",
    r"有哪些", r"列出", r"盤點", r"\blist\b", r"\benumerate\b",
    # 「記憶種類」的後設詞:它們說的是「你要問哪一層記憶」,不是主題本身。
    # 「submission 的業務規則定義是什麼」的主題是 submission,
    # 「業務規則」「定義」是在指定要查 DOMAIN 層 —— 留在內容詞裡會把 coverage
    # 的分母撐大到永遠達不到門檻。
    r"定義", r"術語", r"業務規則", r"語意", r"真實世界",
    r"\bdomain\b", r"\bglossary\b", r"\bdefinition\b",
    r"\bbusiness rule\b", r"\bmean(?:s|ing)?\b",
    r"步驟", r"\bsteps?\b", r"\brunbook\b", r"\bprocedure\b",
    r"藍圖", r"\broadmap\b", r"\bplanned\b", r"未來", r"將來", r"\bfuture\b",
    r"歷史", r"\bhistory\b", r"理由", r"\brationale\b",
    r"權衡", r"\btrade-?off\b", r"架構上", r"\barchitecture of\b",
)

# 額外的通用框架詞:單獨出現時對答案內容零貢獻。
# 刻意**不含**業務詞彙候選(例如「紀錄」「批次」「送檢」),那些是內容不是框架。
FRAME_WORDS = (
    r"我們", r"我", r"你", r"請問", r"想聊", r"聊聊", r"到底", r"究竟",
    r"是不是", r"有沒有", r"可不可以", r"能不能", r"什麼", r"哪裡", r"哪",
    r"怎麼", r"的", r"了", r"嗎", r"呢", r"吧", r"喔", r"啊",
    r"一下", r"一張", r"一個", r"這個", r"那個", r"這", r"那",
    r"\bthe\b", r"\ba\b", r"\ban\b", r"\bof\b", r"\bis\b", r"\bare\b",
    r"\bwas\b", r"\bwere\b", r"\bdo\b", r"\bdoes\b", r"\bdid\b",
    r"\bwhat\b", r"\bwhere\b", r"\bwhen\b", r"\bwho\b", r"\bhow\b",
    r"\bplease\b", r"\btell me\b", r"\bwe\b", r"\bi\b", r"\byou\b",
    r"\bin\b", r"\bon\b", r"\bfor\b", r"\bto\b", r"\bat\b", r"\bby\b",
)

# 長的先剝(「是什麼意思」要在「什麼」之前),否則短詞會把長詞切碎、
# 剩下的殘塊又變成新的假 token。
_FRAME_RE = re.compile(
    "|".join(sorted(PURE_FRAME_CUES + FRAME_WORDS, key=len, reverse=True)),
    re.I)


def strip_frame(text):
    """剝掉問句框架,只留內容詞。回傳字串(保留空白當邊界)。"""
    if not text:
        return ""
    return _FRAME_RE.sub(" ", text)
