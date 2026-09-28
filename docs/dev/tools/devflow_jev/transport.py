"""Fake transport + response schema 驗證。**沒有真 HTTP**(W1 禁止;runtime 是 P1-F1)。

API 形狀(roadmap §10 P0-1 與 0-draft §3 實測):
  request  {"model": "jev-1.13.0", "state": <json>, "questions": {qid: {type,text,criteria?}}}
  response {"model": "jev-1.13.0", "usage": {"input_tokens": n, "output_tokens": n},
            "answers": {qid: {"noul": p} | {"choice": k, "probabilities": {...}, "confidence": c}
                            | {"score": i, "legend": [...], "probabilities": {...}, "confidence": c}}}
`noul` 無 confidence。任何欄位對不上 = schema error → 呼叫端 no-op(policy.evaluate)。
"""
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
            if choice not in q["criteria"]:
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
            if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score < n:
                raise TransportError("schema", "%s.score %r 不是 0..%d 的整數" % (qid, score, n - 1))
            probs = ans.get("probabilities")
            if isinstance(probs, list):
                probs = {str(i): p for i, p in enumerate(probs)}
            if not isinstance(probs, dict) or len(probs) != n:
                raise TransportError("schema", "%s.probabilities 長度 != criteria" % qid)
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
    if isinstance(usage, dict) and isinstance(usage.get("input_tokens"), int) \
            and not isinstance(usage["input_tokens"], bool) and usage["input_tokens"] >= 0:
        usage_out = {"input_tokens": usage["input_tokens"],
                     "output_tokens": usage.get("output_tokens"), "usage_status": "known"}
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
            probs = given.get("probabilities") or {str(i): (1.0 if i == score else 0.0) for i in range(n)}
            out[qid] = {"score": score, "probabilities": probs, "confidence": given.get("confidence", 0.9)}
    return {"model": model, "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            "answers": out}
