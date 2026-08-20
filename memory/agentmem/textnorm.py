"""Unicode-aware tokenization 與 code symbol 抽取。

**這一檔在修一個具體缺陷**:retrieval 前處理若用 ASCII-only 的
`\\b\\w+\\b` / `[a-zA-Z0-9]+` 之類 pattern 切詞,中文查詢會被整段 strip 成空 ——
「之前 PGS registration 為什麼改?」只剩 `PGS registration`,
「目前使用哪一張資料表?」剩下空字串,retrieval 直接查不到任何東西,
而且**不會報錯**(查不到與沒有記憶長得一樣)。

本檔的切詞規則:
- **CJK**:逐字 unigram + 相鄰 bigram(中文沒有詞間空格,bigram 是最小可用的
  詞近似;不引入分詞相依)
- **拉丁 / 數字 / 底線 / 連字號**:整段保留,並額外拆 camelCase、snake_case、
  dotted path 的子詞(`pgs_intake_registration` 同時命中整體與 `pgs`/`intake`/
  `registration`)
- **其他 Unicode 字母**(日文假名、韓文、希臘…):與拉丁同樣按「連續字母段」處理

symbols() 另外抽 coding agent 真正會查的東西:class / function / table / column /
API route / file path / env key / commit SHA。這些要走 **exact match** 通道,
不能只靠語意相似度 —— `pgs_intake_registration` 與 `pgs_intake_specimen`
在 embedding 空間裡幾乎一樣近,但答錯一個就是答錯一張表。
"""
import re
import unicodedata

# CJK 統一漢字(含擴展 A)、CJK 相容、假名、諺文 —— 逐字切的字元集
_CJK_RANGES = (
    (0x3040, 0x30FF),      # 平假名 / 片假名
    (0x3400, 0x4DBF),      # CJK 擴展 A
    (0x4E00, 0x9FFF),      # CJK 統一漢字
    (0xAC00, 0xD7AF),      # 諺文音節
    (0xF900, 0xFAFF),      # CJK 相容漢字
    (0x20000, 0x2FA1F),    # CJK 擴展 B+
)

_WORD_CHARS = set("_-")

_SYMBOL_PATTERNS = (
    # 1) dotted / 命名空間限定:module.func、table.column、a::b
    r"[A-Za-z_][A-Za-z0-9_]*(?:[.:]{1,2}[A-Za-z_][A-Za-z0-9_]+)+",
    # 2) 檔案路徑(repo-relative POSIX;副檔名 1-10 字)
    r"[A-Za-z0-9_][A-Za-z0-9_./-]*\.[A-Za-z][A-Za-z0-9]{0,9}",
    # 3) API route
    r"/[A-Za-z0-9_][A-Za-z0-9_/{}:-]*",
    # 4) SCREAMING_SNAKE(env key / 常數)
    r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+",
    # 5) snake_case(table / column / function)
    r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+",
    # 6) camelCase / PascalCase(class / method)
    r"[A-Za-z]+(?:[A-Z][a-z0-9]+)+",
    # 7) commit SHA(7-40 hex;純數字排除)
    r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b",
)
_SYMBOL_RE = re.compile("|".join("(?:%s)" % p for p in _SYMBOL_PATTERNS))

_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SUBWORD_SPLIT = re.compile(r"[_\-./:]+")


def _is_cjk(ch):
    cp = ord(ch)
    for lo, hi in _CJK_RANGES:
        if lo <= cp <= hi:
            return True
    return False


def _is_word_char(ch):
    if ch in _WORD_CHARS:
        return True
    cat = unicodedata.category(ch)
    return cat.startswith("L") or cat.startswith("N") or cat == "Mn"


def segments(text):
    """把文字切成 (kind, value) 段:kind ∈ cjk | word。標點/空白當邊界丟掉。

    先切段再切詞,是為了讓「中英混合」不必走兩套前處理:
    「之前 PGS registration 為什麼改」→ cjk('之前') word('PGS') word('registration') cjk('為什麼改')
    """
    out = []
    buf = []
    buf_kind = None
    for ch in text or "":
        if _is_cjk(ch):
            kind = "cjk"
        elif _is_word_char(ch):
            kind = "word"
        else:
            kind = None
        if kind is None:
            if buf:
                out.append((buf_kind, "".join(buf)))
                buf, buf_kind = [], None
            continue
        if buf_kind is not None and kind != buf_kind:
            out.append((buf_kind, "".join(buf)))
            buf = []
        buf_kind = kind
        buf.append(ch)
    if buf:
        out.append((buf_kind, "".join(buf)))
    return out


def tokens(text, cjk_bigrams=True):
    """回傳 lexical retrieval 用的 token 清單(小寫;保序;不去重)。

    中文不被 strip 是本函式存在的理由 —— 對「現在使用哪一張資料表?」必須產出
    非空 token 集,否則 FTS 查詢會退化成「查不到」而不是「找不到相關記憶」。
    """
    out = []
    for kind, value in segments(text):
        if kind == "cjk":
            chars = list(value)
            out.extend(chars)
            if cjk_bigrams:
                out.extend(chars[i] + chars[i + 1] for i in range(len(chars) - 1))
        else:
            lowered = value.casefold()
            out.append(lowered)
            for part in _SUBWORD_SPLIT.split(lowered):
                if part and part != lowered:
                    out.append(part)
            for part in _CAMEL_SPLIT.split(value):
                lowered_part = part.casefold()
                if lowered_part and lowered_part != lowered:
                    out.append(lowered_part)
    # 純分隔符段(`---`、`__`)不是 token:`-`/`_` 只有夾在字母數字之間時才是
    # identifier 的一部分,單獨成段時是排版符號。留著會讓 `---` 之類的分隔線
    # 變成一個高頻 token,污染 lexical 通道的 IDF。
    return [t for t in out if t and t.strip("_-")]


def normalize_query(text):
    """FTS 查詢字串:token 以空白連接,每個 token 加引號避免 FTS 語法字元誤用。

    不做「找不到就放寬」的降級 —— 放寬會製造 §25 禁止的 arbitrary fallback。
    """
    toks = tokens(text)
    if not toks:
        return ""
    escaped = ['"' + t.replace('"', '""') + '"' for t in dict.fromkeys(toks)]
    return " OR ".join(escaped)


def symbols(text):
    """抽出 code symbol(原樣保留大小寫;保序去重)。"""
    seen = {}
    for m in _SYMBOL_RE.finditer(text or ""):
        value = m.group(0)
        if len(value) < 3:
            continue
        seen.setdefault(value, None)
    return list(seen.keys())


def normalize_symbol(value):
    """symbol 的比對正規化:小寫 + 去分隔符。

    讓 `pgs_intake_registration` / `pgsIntakeRegistration` / `PGS.intake.registration`
    互相命中,但**不與** `pgs_intake_specimen` 混淆(去分隔符不等於去語意)。
    """
    if not isinstance(value, str):
        return ""
    return re.sub(r"[_\-./:\s]+", "", value).casefold()


def trigrams(text, lowercase=True):
    """字元 trigram(給 fuzzy / 部分字串通道用;中文也適用)。"""
    cleaned = "".join(ch for ch in (text or "") if not ch.isspace())
    if lowercase:
        cleaned = cleaned.casefold()
    return [cleaned[i:i + 3] for i in range(len(cleaned) - 2)]
