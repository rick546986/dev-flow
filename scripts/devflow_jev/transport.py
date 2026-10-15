"""Fake transport + response schema 驗證。**沒有真 HTTP**(W1 禁止;runtime 是 P1-F1)。

API 形狀(roadmap §10 P0-1 與 0-draft §3 實測):
  request  {"model": "jev-1.13.0", "state": <json>, "questions": {qid: {type,text,criteria?}}}
  response {"model": "jev-1.13.0", "usage": {"input_tokens": n, "output_tokens": n},
            "answers": {qid: {"noul": p} | {"choice": k, "probabilities": {...}, "confidence": c}
                            | {"score": x, "legend": ..., "probabilities": {...}, "confidence": c}}}
`noul` 無 confidence。任何欄位對不上 = schema error → 呼叫端 no-op(policy.evaluate)。

score 是 **0 ≤ x ≤ len(criteria)-1 的有限數字(int 或 float)**:真實 Jev 服務回的是期望值小數
(例如 2.92、2.13),不是整數等級。bool、字串、null、NaN、±Infinity、超出範圍一律 schema error。
解析不改值、不取整(int 仍是 int、float 仍是 float,只把 -0.0 正規成 0.0);下游要整數等級時一律走
`score_level()`(round-half-up),不得自行 int()／截斷。
"""
import math

from . import JevError, MODEL_PINNED

ERROR_KINDS = ("http_400", "http_401", "http_422", "http_429", "http_529",
               "timeout", "network", "malformed_json", "schema")
PROB_TOLERANCE = 0.02


class TransportError(JevError):
    def __init__(self, kind, detail=""):
        if kind not in ERROR_KINDS:
            raise ValueError("unknown transport error kind %r" % kind)
        self.kind = kind
        self.detail = detail
        JevError.__init__(self, "%s%s" % (kind, (": " + detail) if detail else ""))


def build_request(state, questions, model=MODEL_PINNED):
    if not isinstance(state, (dict, str, list)):
        raise JevError("state 必須是 JSON 物件 / 字串 / 字串陣列")
    if not isinstance(questions, dict) or not questions:
        raise JevError("questions 必填")
    return {"model": model, "state": state, "questions": questions}


def _num(value, lo=0.0, hi=1.0):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and lo <= value <= hi


SCORE_LEVEL_MAX = 3      # 目前題組的 score 都是 4 級(0..3);valid_score 預設上界


def valid_score(value, hi=SCORE_LEVEL_MAX):
    """score 值合法 ⇔ int／float(非 bool)、有限、0 ≤ value ≤ hi。NaN／±inf／字串／None／bool 都不合法。"""
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and 0 <= value <= hi)


def score_level(value):
    """score(期望值小數)→ 整數等級:**round-half-up**(2.5 → 3、2.49 → 2、2.92 → 3、2.13 → 2、3.0 → 3)。
    只給「必須是整數」的地方用(直方圖分組等);**門檻比較不用它**,門檻直接拿 score 本身比(見 policy.py)。
    不合法 → None。用 floor＋小數部分比 0.5,不用 floor(x+0.5)(後者在 0.49999999999999994 會誤進位)。"""
    if not valid_score(value):
        return None
    base = math.floor(value)
    return int(base + 1) if value - base >= 0.5 else int(base)


def _count(value):
    """usage 的 token 數:非負 int,或有限、整數值的 float(→ int)。其餘 → None(不當成已知用量)。"""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and math.isfinite(value) and value >= 0 and value == math.floor(value):
        return int(value)
    return None


def parse_response(raw, questions):
    """驗 response 形狀並回傳 {"model","usage","answers"};不合 → TransportError("schema")。"""
    if not isinstance(raw, dict):
        raise TransportError("schema", "response 不是物件")
    model = raw.get("model")
    if not isinstance(model, str) or not model:
        raise TransportError("schema", "缺 model")
    answers = raw.get("answers")
    if not isinstance(answers, dict):
        raise TransportError("schema", "缺 answers")
    parsed = {}
    for qid, q in questions.items():
        ans = answers.get(qid)
        if not isinstance(ans, dict):
            raise TransportError("schema", "缺題 %s 的答案" % qid)
        qtype = q["type"]
        if qtype == "noul":
            if not _num(ans.get("noul")):
                raise TransportError("schema", "%s.noul 不在 [0,1]" % qid)
            if "confidence" in ans:
                raise TransportError("schema", "%s: noul 不帶 confidence" % qid)
            parsed[qid] = {"noul": float(ans["noul"])}
        elif qtype == "choice":
            choice = ans.get("choice")
            probs = ans.get("probabilities")
            if not isinstance(choice, str) or choice not in q["criteria"]:     # 非字串(list／dict)不可雜湊,不能丟給 in
                raise TransportError("schema", "%s.choice %r 不在 criteria" % (qid, choice))
            if not isinstance(probs, dict) or set(probs) != set(q["criteria"]):
                raise TransportError("schema", "%s.probabilities 的鍵與 criteria 不一致" % qid)
            if not all(_num(p) for p in probs.values()) or abs(sum(probs.values()) - 1.0) > PROB_TOLERANCE:
                raise TransportError("schema", "%s.probabilities 不是合法分布" % qid)
            if not _num(ans.get("confidence")):
                raise TransportError("schema", "%s.confidence 不在 [0,1]" % qid)
            parsed[qid] = {"choice": choice, "probabilities": {k: float(v) for k, v in probs.items()},
                           "confidence": float(ans["confidence"])}
        elif qtype == "score":
            n = len(q["criteria"])
            score = ans.get("score")
            if not valid_score(score, n - 1):
                raise TransportError("schema", "%s.score %r 不是 0..%d 的有限數字(整數或小數期望值)" % (qid, score, n - 1))
            if isinstance(score, float):
                score += 0.0                      # -0.0 → 0.0;其餘值原樣(不取整)
            probs = ans.get("probabilities")
            if isinstance(probs, list):
                probs = {str(i): p for i, p in enumerate(probs)}
            if not isinstance(probs, dict) or len(probs) != n:
                raise TransportError("schema", "%s.probabilities 長度 != criteria" % qid)
            if set(probs) != set(str(i) for i in range(n)):       # 鍵必須是等級 "0".."n-1"(MR 的期望值用 int(key))
                raise TransportError("schema", "%s.probabilities 的鍵不是 0..%d 等級" % (qid, n - 1))
            vals = list(probs.values())
            if not all(_num(p) for p in vals) or abs(sum(vals) - 1.0) > PROB_TOLERANCE:
                raise TransportError("schema", "%s.probabilities 不是合法分布" % qid)
            if not _num(ans.get("confidence")):
                raise TransportError("schema", "%s.confidence 不在 [0,1]" % qid)
            parsed[qid] = {"score": score, "probabilities": {str(k): float(v) for k, v in probs.items()},
                           "confidence": float(ans["confidence"])}
        else:
            raise TransportError("schema", "未知題型 %r" % qtype)
    usage = raw.get("usage")
    usage_out = {"input_tokens": None, "output_tokens": None, "usage_status": "unknown_reserved"}
    if isinstance(usage, dict) and _count(usage.get("input_tokens")) is not None:
        usage_out = {"input_tokens": _count(usage["input_tokens"]),
                     "output_tokens": _count(usage.get("output_tokens")), "usage_status": "known"}
    return {"model": model, "usage": usage_out, "answers": parsed}


class FakeTransport(object):
    """腳本化傳輸:每次 send 依序取一筆 script 項目。

    script item 形狀:
      {"response": <raw dict>, "latency_s": 0.4}      → 回 raw(policy 會 parse)
      {"error": "http_429", "latency_s": 0.1}          → raise TransportError
      {"raw_text": "not json"}                          → raise TransportError("malformed_json")
    `clock` 由呼叫端注入(policy.evaluate 用同一個 clock 量 deadline),不真的 sleep。
    """

    def __init__(self, script, clock=None):
        self.script = list(script)
        self.calls = []
        self.clock = clock

    def send(self, request):
        self.calls.append(request)
        if not self.script:
            raise TransportError("network", "fake transport script 用盡")
        item = self.script.pop(0)
        if self.clock is not None:
            self.clock.advance(float(item.get("latency_s", 0.0)))
        if "error" in item:
            raise TransportError(item["error"], item.get("detail", "simulated"))
        if "raw_text" in item:
            raise TransportError("malformed_json", "simulated non-JSON body")
        return item["response"]


class FakeClock(object):
    """可注入的單調時鐘(deadline 測試不靠真實 sleep)。"""

    def __init__(self, start=0.0):
        self.now = float(start)

    def advance(self, seconds):
        self.now += float(seconds)

    def __call__(self):
        return self.now


def _level_distribution(score, n):
    """測試便利:整數 score → one-hot;小數 score → 只在相鄰兩級配比(期望值 = score)。"""
    if not valid_score(score, n - 1):
        return {str(i): (1.0 if i == score else 0.0) for i in range(n)}     # 壞 score 原樣進去,讓 parse 去擋
    lo = int(math.floor(score))
    frac = score - lo
    probs = {str(i): 0.0 for i in range(n)}
    probs[str(lo)] = 1.0 - frac
    if frac:
        probs[str(lo + 1)] = frac
    return probs


def canned_response(questions, answers, model=MODEL_PINNED, input_tokens=1000, output_tokens=80):
    """測試便利:依 questions 補齊合法形狀;answers 給部分值即可。"""
    out = {}
    for qid, q in questions.items():
        given = answers.get(qid, {})
        if q["type"] == "noul":
            out[qid] = {"noul": given.get("noul", 0.5)}
        elif q["type"] == "choice":
            keys = list(q["criteria"])
            choice = given.get("choice", keys[0])
            probs = given.get("probabilities")
            if probs is None:
                probs = {k: (1.0 if k == choice else 0.0) for k in keys}
            out[qid] = {"choice": choice, "probabilities": probs, "confidence": given.get("confidence", 0.9)}
        else:
            n = len(q["criteria"])
            score = given.get("score", 0)
            probs = given.get("probabilities") or _level_distribution(score, n)
            out[qid] = {"score": score, "probabilities": probs, "confidence": given.get("confidence", 0.9)}
    return {"model": model, "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            "answers": out}
