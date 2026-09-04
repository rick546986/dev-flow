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
    # 空白中文字,誤殺(#95 回歸,PR #110 審查 finding C)。改成三條路都要求
    # 「後面看起來像憑證,不是像句子」:
    #   ①英文 key 名(password/secret/api_key/…)+ 賦值記號(冒號/等號)——
    #     純正則判定,不做形狀檢查。
    #   ②中文「密碼是／金鑰是」+ 明確賦值記號(引號、半形/全形冒號、等號)——
    #     記號後第一個字元仍要求是 ASCII 可見字元,擋掉「密碼是:需要定期更換
    #     的」這種「有冒號但接的還是中文敘述」的假陽性。純正則判定。
    #   ③中文「密碼是／金鑰是」+ 沒有賦值記號的裸 token(中文書寫 ASCII 值
    #     常不留空白,如「密碼是hunter2000」)—— 正則只抓候選(named group
    #     `tok`:首字元 `[A-Za-z0-9_-]`(不含 `.`/`/`,同 R2 基準,讓
    #     「密碼是 -abc-1234-」「金鑰是 _Abc12345」不被排除,同時不讓
    #     「金鑰是 /path/to/keyfile」這種路徑誤判成裸 token)接續 7 個以上
    #     `[A-Za-z0-9._/-]`,單一量詞、線性時間,前面保留 placeholder 排除
    #     lookahead(`<`/`{`/`$`/`(`/null/none/redacted/xxx…,同①②)。形狀
    #     判斷(是否含數字/連字號底線斜線,或英文大小寫混合)搬出正則,由
    #     scan_sensitive 用 Python 對 tok 字串判定 —— 原因見下方 ReDoS 段。
    # 三條路都刻意排除 CJK 字元:敘述句的接續文字幾乎不可能撞上。
    #
    # ReDoS:這顆函式踩過兩次,病灶同一類——用不定長 regex 結構夾住/跟著
    # 必須條件,讓回溯量隨輸入長度變成平方成長。下面誠實記兩次各自的病灶與
    # 修法,不是宣稱「ReDoS 已處理」這種對未來所有輸入都成立的保證:
    #   R2 finding 1(裸 token 形狀判斷,③):曾用兩個獨立、不定長的
    #     `[A-Za-z0-9._-]*` 夾住必須字元(混合大小寫那支)。輸入「密碼是」後
    #     接一長段同大小寫 ASCII 字母時,兩個 `*` 在同一段字元集上互相重疊,
    #     每個 split 點都要重新掃到底才判定失敗,退化成平方時間。本輪(R3)
    #     把形狀判斷整段搬出正則(見③),規則本身不再存在,不只是設界。
    #   R3 finding 1(英文 key 名分支,①):`\b[\w.-]*(?:password|…)…`
    #     兩側各一個不定長 `[\w.-]*` 夾住必須字面(keyword 群組)。對一段
    #     無空白的 `[A-Za-z0-9_.-]` 長串(例如 60KB base64url blob、或
    #     `x.-_` 重複),`.`/`-` 不是 \w 字元,`\b` 在這種輸入裡幾乎每個字元
    #     都是一個邊界起點;每個起點都要對兩側 `*` 各自回溯到底才判定失敗,
    #     退化成對輸入長度平方的回溯 —— 即使全文完全不含任何敏感關鍵字。
    #     修法:兩側量詞都改成有界 `{0,64}`,單一起點的工作量封頂,不再隨
    #     輸入長度增長;真實 key 名前後綴幾乎不會超過 64 字元,封頂不影響
    #     可偵測性。
    # 兩次修法後,「存在性」量詞(③裸 token 最短 8 字元、①②的關鍵字/中文
    # 詞本身)都維持不設上限的單一量詞 —— 那不是回溯的來源,設上限反而會
    # 製造新的假陰性(65 字元以上的裸 token,若邊界判斷式本身設界,會卡在
    # 界內、永遠等不到終止條件而整支失配)。這正是③把形狀判斷整段搬出正則
    # 的原因:單一量詞的存在性判定留在正則(線性),形狀判定挪到 Python 端
    # 對已擷取的 tok 字串做,不受任何長度上限影響。
    ("assigned_secret", re.compile(
        r"(?i)(?:"
        r"\b[\w.-]{0,64}(?:password|passwd|secret|api[_-]?key|apikey|token|"
        r"credential|private[_-]?key|access[_-]?key)[\w.-]{0,64}\s*[:=]\s*"
        r"(?!(?:<|\{|\$|\(|null\b|none\b|redacted\b|xxx+\b|\*+\s*$))"
        r"[\"']?[^\s\"',;]{6,}"
        r"|(?:密碼是|金鑰是)\s*(?:[:：=]\s*(?=[!-~])|(?=[\"'][!-~]))"
        r"(?!(?:<|\{|\$|\(|null\b|none\b|redacted\b|xxx+\b|\*+\s*$))"
        r"[\"']?[^\s\"',;]{6,}"
        r"|(?:密碼是|金鑰是)\s*[:：=]?"
        r"(?!(?:<|\{|\$|\(|null\b|none\b|redacted\b|xxx+\b|\*+\s*$))"
        r"[\"']?(?P<tok>[A-Za-z0-9_-][A-Za-z0-9._/-]{7,})"
        r")")),
)


def _looks_like_credential(tok):
    """裸 token 候選(assigned_secret 第③支)是否長得像憑證。

    正則只負責抓出候選字串(見上方 _SENSITIVE 定義處註解);形狀判斷放在
    這裡用 Python 對已擷取的 tok 做,不放回正則,長度不受任何上限影響。
    """
    has_digit = False
    has_symbol = False
    has_lower = False
    has_upper = False
    for ch in tok:
        if ch.isdigit():
            has_digit = True
        elif ch in "-_/":
            has_symbol = True
        elif ch.islower():
            has_lower = True
        elif ch.isupper():
            has_upper = True
    return has_digit or has_symbol or (has_lower and has_upper)


def scan_sensitive(text):
    """回傳命中的敏感 pattern 名稱清單(不回傳命中內容 —— 回傳等於再抄一份)。

    assigned_secret 的裸 token 分支(③)只用正則抓候選,形狀判斷交給
    `_looks_like_credential`,所以這一個 pattern 要逐一檢查每個候選
    (finditer),候選不像憑證就跳過、繼續找下一個。其餘 pattern 沒有這種
    「候選 vs 判定」的兩段式,維持原本 search 一次即算。
    """
    if not isinstance(text, str) or not text:
        return []
    hits = []
    for name, pattern in _SENSITIVE:
        if name != "assigned_secret":
            if pattern.search(text):
                hits.append(name)
            continue
        for m in pattern.finditer(text):
            tok = m.groupdict().get("tok")
            if tok is None or _looks_like_credential(tok):
                hits.append(name)
                break
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
