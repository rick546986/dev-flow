"""ULID 生成(memory 專用;與 observability/devflow_obs/ids.py 刻意分開)。

為什麼不共用 observability 的 ids:那支的 docstring 明文宣告「kind 只有
run/attempt/review/finding 四種」,且它服務的是**執行追溯鏈**(run 生命週期)。
memory 的 ID 是**記憶實體 identity**(project/session/event/fact/…),兩條鏈不混用 ——
在那支加 kind 會破壞它的契約宣告,故本檔獨立實作同一套編碼規則。

project_id 的三個硬條件(架構升級的核心約束):
- **path-independent**:不含任何 filesystem path 成分。Mac 的
  `/Users/rick/dev/proj`、Windows 的 `D:\\dev\\proj`、Linux 的 `/home/rick/proj`
  必須解析成同一個 project_id —— 它由 `.dev-flow/project.yaml` 提供,而那個檔進 Git。
- **不依賴 GitHub / remote URL**:remote 只能當 metadata/provenance。沒有 remote、
  remote 改名、fork、鏡像,project_id 都不變。
- **stable**:產生一次就 commit 進 Git,dev-setup 重跑一律 reuse,不重新產生。
"""
import os
import re
import threading
import time

_ENC = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"          # Crockford base32
_BODY = r"[0-9A-HJKMNP-TV-Z]{26}"

KINDS = {
    "project": "prj",
    "workspace": "wsp",
    "session": "ses",
    "event": "evt",
    "fact": "fct",
    "knowledge": "knw",
    "decision": "dec",
    "skill": "skl",
    "candidate": "cnd",
}

_PATTERNS = {k: re.compile("^" + p + "_" + _BODY + "$") for k, p in KINDS.items()}

_lock = threading.Lock()
_last_ts = 0
_last_rand = 0


def _encode(ts_ms, rand80):
    n = (ts_ms << 80) | rand80
    return "".join(_ENC[(n >> (5 * (25 - i))) & 31] for i in range(26))


def _decode_body(body):
    n = 0
    for ch in body:
        n = (n << 5) | _ENC.index(ch)
    return n


def new_id(kind):
    """生成 `<prefix>_<ULID>`。同 process 內單調遞增(字典序 = 生成序)。"""
    global _last_ts, _last_rand
    if kind not in KINDS:
        raise ValueError(
            "unknown id kind: {0!r}(記憶實體只有 {1})".format(kind, sorted(KINDS)))
    with _lock:
        ts = int(time.time() * 1000)
        if ts <= _last_ts:
            ts = _last_ts
            rand = _last_rand + 1
            if rand >= 1 << 80:                     # 同 ms 進位溢位 → 借下一 ms
                ts += 1
                rand = int.from_bytes(os.urandom(10), "big") >> 1
        else:
            rand = int.from_bytes(os.urandom(10), "big") >> 1   # 最高位留 0
        _last_ts, _last_rand = ts, rand
        return KINDS[kind] + "_" + _encode(ts, rand)


def is_valid_id(kind, value):
    """驗證字串是否為指定 kind 的合法 ID(從 Git 讀回 project.yaml 時必驗)。"""
    if kind not in KINDS or not isinstance(value, str):
        return False
    return bool(_PATTERNS[kind].match(value))


def kind_of(value):
    """從 ID 反推 kind;不合法回 None(讀回外部資料時不要 assume)。"""
    if not isinstance(value, str) or "_" not in value:
        return None
    prefix = value.split("_", 1)[0]
    for kind, p in KINDS.items():
        if p == prefix and _PATTERNS[kind].match(value):
            return kind
    return None


def timestamp_of(value):
    """從 ID 取回生成時間(epoch 秒);ID 不合法丟 ValueError。"""
    if kind_of(value) is None:
        raise ValueError("not a valid agentmem id: {0!r}".format(value))
    return (_decode_body(value.split("_", 1)[1]) >> 80) / 1000.0
