"""Signal Gate 與敏感內容守衛(durable 寫入的最後一道閘)。

兩個獨立的判斷,不要混成一個:

  ①**Signal Gate**:這件事值得留成長期記憶嗎?
     低訊號(讀檔、grep、列目錄、一般成功指令)→ local only,不進 Git。
     高訊號(架構變更、schema 變更、bug root cause、業務規則、重要決策、
     已驗證流程、domain 釐清、breaking config)→ 可以 durable。
     理由:每個 tool 事件都 durable persist,`.dev-flow/` 會在一週內變成
     一份沒人讀得完、且每次 pull 都衝突的雜訊檔。
  ②**敏感內容守衛**:這段內容可以被 push 出去嗎?
     durable memory 會進 Git,而 Git 會被 push、被 fork、被 mirror。
     一旦 secret 進了 commit,砍檔案不等於砍歷史。
     命中敏感 pattern → **拒絕 durable persist**(降級 local only),不是遮罩後照存 ——
     遮罩靠 pattern 完整性,而 pattern 永遠不完整;拒絕才是安全的預設。

第三道(§4):durable 內容不得含絕對路徑。這條由 paths.scan_absolute_paths 提供,
本檔把它併進同一個 verdict,呼叫端只需要看一個結果。
"""
import re

from . import paths

HIGH = "high"
LOW = "low"

# 高訊號事件種類(durable 候選;仍要過敏感守衛)
HIGH_SIGNAL_KINDS = {
    "architecture_change",
    "schema_change",
    "migration",
    "bug_root_cause",
    "business_rule",
    "domain_clarification",
    "design_decision",
    "verified_workflow",
    "breaking_config_change",
    "api_migration",
    "table_rename",
    "deployment_issue",
    "important_discovery",
    "conflict_detected",
    # 修正歷史(P0-3):「以前理解成什麼、後來為什麼改」是 durable memory
    # 最有價值的一類 —— 它正是現況視圖留不下來的東西。
    "knowledge_corrected",
    "fact_superseded",
    "decision_superseded",
}

# 低訊號:一律 local only(即使有人手動標高訊號也先降級,見 gate() 的 reasons)
LOW_SIGNAL_KINDS = {
    "file_read",
    "grep",
    "list_directory",
    "command_ok",
    "tool_noise",
    "navigation",
}

_SENSITIVE = (
    ("private_key_block", re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\."
                       r"[A-Za-z0-9_-]{10,}\b")),
    ("bearer_header", re.compile(r"\b[Aa]uthorization\s*:\s*Bearer\s+\S+")),
    ("dsn_with_password", re.compile(
        r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:@]+:[^\s/@]+@")),
    # `SOMETHING_SECRET = "value"` 這一族:key 名帶敏感字 + 有實際賦值
    #
    # 中文「密碼是／金鑰是」不能只看後接 6 個非空白字元 —— 敘述句(「密碼是否
    # 要定期更換」「密碼是公司規定」「金鑰是由 KMS 管理」)一樣會後接一串非
    # 空白中文字,誤殺(#95 回歸,PR #110 審查 finding C)。改成兩條路都要求
    # 「後面看起來像憑證,不是像句子」:
    #   ①有明確賦值記號(引號、半形/全形冒號、等號)—— 但記號後第一個字元仍要
    #     求是 ASCII 可見字元,擋掉「密碼是:需要定期更換的」這種「有冒號但接
    #     的還是中文敘述」的假陽性。
    #   ②沒有賦值記號的裸 token(中文書寫 ASCII 值常不留空白,如
    #     「密碼是hunter2000」)—— 純 ASCII/數字/`-_./`、長度 ≥ 8、且含數字或
    #     連字號底線斜線或大小寫混合。首字元允許字母數字或 `-` `_`,讓
    #     「密碼是 -abc-1234-」「金鑰是 _Abc12345」這類 token 不被排除。
    # 兩條路都刻意排除 CJK 字元:敘述句的接續文字幾乎不可能撞上。
    #
    # ReDoS(#95 R2 finding 1):裸 token 的形狀 lookahead 曾用兩個獨立、不定長
    # 的 `[A-Za-z0-9._-]*` 夾住必須字元(混合大小寫那支)。輸入「密碼是」後接
    # 一長段同大小寫 ASCII 字母時,兩個 `*` 在同一段字元集上互相重疊,每個
    # split 點都要重新掃到底才判定失敗,退化成對輸入長度平方的災難性回溯。
    # 修法只動第二個(形狀判定)lookahead 的量詞,改成有界 `{0,64}`:單一起點
    # 的工作量封頂,不再隨輸入長度增長 —— 判別特徵(數字/連字號底線斜線/
    # 大小寫轉換)在真實憑證裡幾乎必然落在前 64 字元內,封頂不影響可偵測性。
    # 第一個(存在性/邊界)lookahead 刻意維持不設上限(`{7,}`)——它只有單一
    # quantifier 後接一次性邊界判定,是線性回溯,不是 ReDoS 來源;設上限反而
    # 會讓 65 字元以上的裸 token(邊界卡在上限內側、永遠等不到非 token 字元
    # 或字串結尾)整支失配,是新的假陰性。
    ("assigned_secret", re.compile(
        r"(?i)(?:"
        r"\b[\w.-]*(?:password|passwd|secret|api[_-]?key|apikey|token|"
        r"credential|private[_-]?key|access[_-]?key)[\w.-]*\s*[:=]\s*"
        r"|(?:密碼是|金鑰是)\s*(?:[:：=]\s*(?=[!-~])|(?=[\"'][!-~]))"
        r"|(?:密碼是|金鑰是)\s*"
        r"(?=[A-Za-z0-9_-][A-Za-z0-9._/-]{7,}(?:[^\w./-]|$))"
        r"(?=[A-Za-z0-9._/-]{0,64}[0-9]|[A-Za-z0-9._/-]{0,64}[-_/]|"
        r"(?-i:[A-Za-z0-9._/-]{0,64}[a-z][A-Za-z0-9._/-]{0,64}[A-Z]"
        r"|[A-Za-z0-9._/-]{0,64}[A-Z][A-Za-z0-9._/-]{0,64}[a-z]))"
        r")"
        r"(?!(?:<|\{|\$|\(|null\b|none\b|redacted\b|xxx+\b|\*+\s*$))"
        r"[\"']?[^\s\"',;]{6,}")),
)


def scan_sensitive(text):
    """回傳命中的敏感 pattern 名稱清單(不回傳命中內容 —— 回傳等於再抄一份)。"""
    if not isinstance(text, str) or not text:
        return []
    hits = []
    for name, pattern in _SENSITIVE:
        if pattern.search(text):
            hits.append(name)
    return hits


def classify(kind, title="", body="", explicit=None):
    """判定訊號等級。explicit 只能**降級**,不能把低訊號種類升級。

    為什麼不允許升級:呼叫端(agent)最容易的錯誤就是把每件事都標成重要。
    高訊號的定義住這裡,不住呼叫端。
    """
    if explicit == LOW:
        return LOW
    if kind in LOW_SIGNAL_KINDS:
        return LOW
    if kind in HIGH_SIGNAL_KINDS:
        return HIGH
    # 未知種類:預設低訊號(保守)。要 durable 就得先把種類納入 HIGH_SIGNAL_KINDS,
    # 那是一次要被 review 的改動,不是 runtime 可以自己決定的事。
    return LOW


def gate(kind, title="", body="", explicit=None, extra_texts=()):
    """durable 閘門的單一入口。

    回傳 dict:
      signal            high | low
      durable_allowed   bool —— 三道全過才 True
      sensitive         命中的敏感 pattern 名稱
      absolute_paths    命中的疑似絕對路徑
      reasons           人看得懂的拒絕理由(空 = 允許)
    """
    signal = classify(kind, title, body, explicit)
    blob = "\n".join([title or "", body or ""] + [t for t in extra_texts if t])
    sensitive = scan_sensitive(blob)
    absolutes = paths.scan_absolute_paths(blob)
    reasons = []
    if signal != HIGH:
        reasons.append(
            "低訊號({0})—— 只留 local runtime,不進 durable memory".format(kind))
    if sensitive:
        reasons.append(
            "疑似敏感內容({0})—— durable memory 會被 push,拒絕固化(不做遮罩後放行)"
            .format(",".join(sensitive)))
    if absolutes:
        reasons.append(
            "內容含絕對路徑({0} 處)—— durable memory 只收 repo-relative 路徑"
            .format(len(absolutes)))
    return {
        "signal": signal,
        "durable_allowed": not reasons,
        "sensitive": sensitive,
        "absolute_paths": absolutes,
        "reasons": reasons,
    }
