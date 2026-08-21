"""受限 YAML 子集的 deterministic emitter / parser(durable 檔案專用)。

為什麼自己寫而不是 PyYAML:本 repo 的 runtime 面明文「python3 標準庫,無第三方
依賴」—— durable memory 的讀寫是 dev-setup 與 hooks 會走的路,不能引入採用專案
不一定裝得起來的相依(唯一例外是 gate twin 產生器的 markdown-it-py,那支不在
runtime 路徑上)。

支援的子集(**刻意窄**,不在子集內的一律 fail-loud,不猜):
- block 風格的 mapping / sequence,2 空格縮排
- scalar:str / int / float / bool(true|false)/ null(空值或 `null`)
- 巢狀:map of map、map of list、list of map、list of scalar
- 整行註解(縮排 + `#`)—— 只在 parse 時略過,emitter 只寫檔頭註解

**明確不支援**(遇到直接丟 `YamlMiniError`):flow 風格(`{}` / `[]`)、anchor/alias
(`&` / `*`)、多文件(`---` 分隔)、block scalar(`|` / `>`)、tab 縮排。
理由:一個手寫 parser 最大的風險是「看起來讀懂了,其實讀錯」——把不支援的形狀
靜默讀成別的東西,會讓 durable memory 的內容在跨機器讀回時默默變形。窄且吵,
比寬且靜默安全。

deterministic 的定義(§30 Git conflict 設計要求):同一份資料 dump 兩次逐 byte
相同、key 順序固定(`key_order` 指定的先按指定序、其餘字典序)、一律 LF 結尾、
不輸出尾隨空白。
"""
import json
import re

_PLAIN_SAFE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./@+-]*$")
_RESERVED_PLAIN = {"true", "false", "null", "yes", "no", "on", "off", "~", ""}
_INT = re.compile(r"^-?[0-9]+$")
_FLOAT = re.compile(r"^-?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$")


class YamlMiniError(ValueError):
    """不在支援子集內、或格式不合法 —— 一律 fail-loud,不做寬鬆解讀。"""


# ─────────────────────────────── emit ────────────────────────────────────────
def _emit_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        # repr 保證 round-trip;避免 str() 在舊版本上截位
        return repr(value)
    if isinstance(value, str):
        if _PLAIN_SAFE.match(value) and value.lower() not in _RESERVED_PLAIN \
                and not _INT.match(value) and not _FLOAT.match(value):
            return value
        return json.dumps(value, ensure_ascii=False)
    raise YamlMiniError("不支援的 scalar 型別:{0!r}".format(type(value)))


def _ordered_keys(mapping, key_order):
    keys = list(mapping.keys())
    for k in keys:
        if not isinstance(k, str) or not _PLAIN_SAFE.match(k):
            raise YamlMiniError("mapping key 必須是簡單識別字:{0!r}".format(k))
    head = [k for k in (key_order or []) if k in mapping]
    tail = sorted(k for k in keys if k not in head)
    return head + tail


def _emit(value, indent, key_order, lines):
    pad = "  " * indent
    if isinstance(value, dict):
        if not value:
            raise YamlMiniError("空 mapping 無法用 block 風格表示;請省略該 key")
        for k in _ordered_keys(value, key_order):
            v = value[k]
            if isinstance(v, dict) and v:
                lines.append("{0}{1}:".format(pad, k))
                _emit(v, indent + 1, key_order, lines)
            elif isinstance(v, list) and v:
                lines.append("{0}{1}:".format(pad, k))
                _emit(v, indent + 1, key_order, lines)
            elif isinstance(v, (dict, list)):
                lines.append("{0}{1}: []".format(pad, k) if isinstance(v, list)
                             else "{0}{1}: null".format(pad, k))
            else:
                lines.append("{0}{1}: {2}".format(pad, k, _emit_scalar(v)))
        return
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item:
                keys = _ordered_keys(item, key_order)
                first = keys[0]
                fv = item[first]
                if isinstance(fv, (dict, list)) and fv:
                    lines.append("{0}- {1}:".format(pad, first))
                    _emit(fv, indent + 2, key_order, lines)
                else:
                    lines.append("{0}- {1}: {2}".format(
                        pad, first,
                        "[]" if isinstance(fv, list) else
                        ("null" if isinstance(fv, dict) else _emit_scalar(fv))))
                rest = {k: item[k] for k in keys[1:]}
                if rest:
                    _emit(rest, indent + 1, keys[1:], lines)
            elif isinstance(item, (dict, list)):
                raise YamlMiniError("sequence 內不支援空 mapping / 巢狀 sequence")
            else:
                lines.append("{0}- {1}".format(pad, _emit_scalar(item)))
        return
    raise YamlMiniError("頂層只能是 mapping 或 sequence")


def dump(data, key_order=None, header=None):
    """序列化成受限 YAML 字串(deterministic;結尾一定有且只有一個 LF)。"""
    lines = []
    if header:
        for line in header.splitlines():
            lines.append(("# " + line).rstrip())
    _emit(data, 0, key_order, lines)
    return "\n".join(line.rstrip() for line in lines) + "\n"


# ─────────────────────────────── parse ───────────────────────────────────────
def _parse_scalar(token, lineno):
    token = token.strip()
    if token == "" or token == "null" or token == "~":
        return None
    if token == "true":
        return True
    if token == "false":
        return False
    if token == "[]":
        return []
    if token.startswith('"'):
        try:
            return json.loads(token)
        except ValueError as exc:
            raise YamlMiniError("第 {0} 行:引號字串解析失敗:{1}".format(lineno, exc))
    if token[0] in "{[&*|>":
        raise YamlMiniError(
            "第 {0} 行:不支援 flow 風格 / anchor / block scalar:{1!r}".format(
                lineno, token))
    if _INT.match(token):
        return int(token)
    if _FLOAT.match(token):
        return float(token)
    if token.startswith("'"):
        raise YamlMiniError(
            "第 {0} 行:單引號字串不在支援子集內(請用雙引號)".format(lineno))
    return token


def _tokenize(text):
    """(indent, content, lineno) 序列;略過空行與整行註解,拒絕 tab 縮排。"""
    out = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if raw.startswith("---"):
            raise YamlMiniError("第 {0} 行:不支援多文件 `---` 分隔".format(lineno))
        if not raw.strip():
            continue
        stripped = raw.lstrip(" ")
        if stripped.startswith("#"):
            continue
        indent = len(raw) - len(stripped)
        if "\t" in raw[:indent] or raw.startswith("\t"):
            raise YamlMiniError("第 {0} 行:縮排不得用 tab".format(lineno))
        if indent % 2 != 0:
            raise YamlMiniError(
                "第 {0} 行:縮排必須是 2 的倍數(實得 {1})".format(lineno, indent))
        out.append((indent // 2, stripped.rstrip(), lineno))
    return out


def _split_key(content, lineno):
    """`key: value` → (key, value_token)。value 可為空(代表巢狀區塊)。"""
    m = re.match(r"^([A-Za-z0-9_][A-Za-z0-9_./@+-]*):(?:\s+(.*))?$", content)
    if not m:
        raise YamlMiniError(
            "第 {0} 行:不是合法的 `key: value`:{1!r}".format(lineno, content))
    return m.group(1), (m.group(2) or "")


def _parse_block(tokens, pos, level):
    """回傳 (value, next_pos)。level = 期望縮排層。"""
    if pos >= len(tokens):
        return None, pos
    _, content, _ = tokens[pos]
    if content.startswith("- "):
        items = []
        while pos < len(tokens):
            ind, content, lineno = tokens[pos]
            if ind != level or not content.startswith("- "):
                break
            body = content[2:].strip()
            if re.match(r"^[A-Za-z0-9_][A-Za-z0-9_./@+-]*:(\s|$)", body):
                key, token = _split_key(body, lineno)
                if token:
                    item = {key: _parse_scalar(token, lineno)}
                    pos += 1
                else:
                    nested, pos = _parse_block(tokens, pos + 1, level + 2)
                    item = {key: nested}
                # 同一 item 的其餘 key 縮排在 `- ` 之後一層
                while pos < len(tokens) and tokens[pos][0] == level + 1 \
                        and not tokens[pos][1].startswith("- "):
                    ind2, content2, lineno2 = tokens[pos]
                    key2, token2 = _split_key(content2, lineno2)
                    if token2:
                        item[key2] = _parse_scalar(token2, lineno2)
                        pos += 1
                    else:
                        nested2, pos = _parse_block(tokens, pos + 1, level + 2)
                        item[key2] = nested2
                items.append(item)
            else:
                items.append(_parse_scalar(body, lineno))
                pos += 1
        return items, pos
    mapping = {}
    while pos < len(tokens):
        ind, content, lineno = tokens[pos]
        if ind != level:
            break
        if content.startswith("- "):
            break
        key, token = _split_key(content, lineno)
        if key in mapping:
            raise YamlMiniError("第 {0} 行:重複 key `{1}`".format(lineno, key))
        if token:
            mapping[key] = _parse_scalar(token, lineno)
            pos += 1
        else:
            nested, pos = _parse_block(tokens, pos + 1, level + 1)
            mapping[key] = nested
    return mapping, pos


def load(text):
    """解析受限 YAML 字串;不在子集內丟 YamlMiniError(不做寬鬆解讀)。"""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    if tokens[0][0] != 0:
        raise YamlMiniError("第 {0} 行:頂層不得縮排".format(tokens[0][2]))
    value, pos = _parse_block(tokens, 0, 0)
    if pos != len(tokens):
        raise YamlMiniError(
            "第 {0} 行:縮排結構不連續(解析停在此處)".format(tokens[pos][2]))
    return value
