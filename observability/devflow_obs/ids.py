"""執行追溯鏈 ID 生成(二節)。

- Prefixed ULID:`<kind>_<26 字 Crockford base32>`(48-bit ms timestamp + 80-bit entropy)。
- 由 Coordinator/runtime 呼叫生成,**不依賴 LLM 自己隨意生成**;LLM 只轉抄。
- 同 process 內單調遞增(同 ms 進位 entropy)→ 字典序 = 生成序。
- ID 是純字串、住檔案系統(目錄名/事件欄位),跨 restart 以檔案為準恢復。
- 業務鏈 ID(R-n/S-n/T-n/D-n/F-n)不在此生成 —— 兩條鏈分離,不混用。
- 不將段落當 span:kind 只有 run/attempt/review/finding 四種。
"""
import os
import re
import threading
import time

_ENC = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"          # Crockford base32
KINDS = {"run": "run", "attempt": "att", "review": "rev", "finding": "fnd"}
_BODY = r"[0-9A-HJKMNP-TV-Z]{26}"
_PATTERNS = {k: re.compile(r"^" + p + "_" + _BODY + r"$") for k, p in KINDS.items()}

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
    """生成一個 `<kind>_<ULID>`。kind ∈ run|attempt|review|finding。"""
    global _last_ts, _last_rand
    if kind not in KINDS:
        raise ValueError(f"unknown id kind: {kind!r}(執行鏈只有 {sorted(KINDS)};"
                         f"段落/token span 不是追蹤單位)")
    with _lock:
        ts = int(time.time() * 1000)
        if ts <= _last_ts:
            ts = _last_ts
            rand = _last_rand + 1
            if rand >= 1 << 80:                     # 同 ms 進位溢位 → 借下一 ms
                ts += 1
                rand = int.from_bytes(os.urandom(10), "big") >> 1
        else:
            # 保留最高位為 0,留同 ms 進位空間
            rand = int.from_bytes(os.urandom(10), "big") >> 1
        _last_ts, _last_rand = ts, rand
        return KINDS[kind] + "_" + _encode(ts, rand)


def is_valid_id(kind, value):
    """驗證字串是否為指定 kind 的合法 ID(跨 restart 讀回時用)。"""
    if kind not in KINDS or not isinstance(value, str):
        return False
    return bool(_PATTERNS[kind].match(value))


def timestamp_of(value):
    """從 ID 取回生成時間(epoch 秒)—— retention 依此判齡,不需另存欄位。"""
    body = value.split("_", 1)[1]
    return (_decode_body(body) >> 80) / 1000.0
