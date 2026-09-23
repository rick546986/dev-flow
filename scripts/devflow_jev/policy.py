"""G2 — failure/no-op、deadline、breaker、budget;以及 deterministic route formula(G6 的唯一來源)。

工程候選值(roadmap §8.2;**不是 owner 裁決**,不冒充):
  J1 foreground 總 deadline 2s、無 foreground retry;daily 500 attempts / 500k input tokens 先到者停。
route 規則(roadmap §11/§12/§13):
  - 不把多題機率相乘成總風險;atomic signals 各自進 deterministic rule。
  - J5 AUTO 只在 g3_route=AUTO_SHIP 且 p≥AUTO_MIN 且 risk≤1 且 evidence_complete≥EVIDENCE_MIN;
    packet 有 truncated/consistency 旗標、risk ceiling 命中、runtime 當次被改 → 一律 HUMAN。
  - J1 ASK_MORE 的弱維度從 atomic clarity signals 取最弱者,**不從 next 分布逆推**。
  - J5 的 route_taken 要 AUTO 還需 graduated=True(W6 前永遠 False)→ 否則 HUMAN。
"""
from . import GATES, JevError, POLICY_VERSION, ROUTE_FORMULA_VERSION
from .transport import TransportError, parse_response

THRESHOLDS = {
    "J5": {"auto_choice_min": 0.85, "evidence_complete_min": 0.90, "risk_max": 1},
    "J1": {"start_min": 0.80, "clarity_min": 0.70, "owner_call_min": 0.50, "ambiguity_max": 1},
    "J3": {"demo_min": 0.60},
}
J1_DEADLINE_S = 2.0
DAILY_ATTEMPTS_CAP = 500
DAILY_INPUT_TOKENS_CAP = 500000
BREAKER_THRESHOLD = 3
J1_CLARITY_DIMS = ("goal_clear", "scope_clear", "acceptance_clear")
# 機械 risk ceiling 的候選清單(P2-4 正式化前;G6 監控它只能變寬)。住這裡是為了進 policy 指紋。
RISK_PATHS_DEFAULT = ("migrations/", "migration/", "auth/", "payment", "payments/", "billing/",
                      "secrets", ".github/workflows/", "ci/", "Dockerfile", "infra/")


def policy_fingerprint():
    """route formula / 門檻 / budget / breaker / risk_paths 的機械指紋;進 manifest 的
    policy_version 與 route_formula_version。改任一常數而不 bump 版本 → questionset_hash 仍會變,
    舊 calibration group 不延續(roadmap §3.4 / P1-G5)。"""
    from .manifest import canonical_json, sha256_hex
    payload = {"thresholds": THRESHOLDS, "j1_deadline_s": J1_DEADLINE_S, "daily_attempts_cap": DAILY_ATTEMPTS_CAP,
               "daily_input_tokens_cap": DAILY_INPUT_TOKENS_CAP, "breaker_threshold": BREAKER_THRESHOLD,
               "risk_paths_default": list(RISK_PATHS_DEFAULT), "j1_clarity_dims": list(J1_CLARITY_DIMS)}
    return sha256_hex(canonical_json(payload))[7:19]


# ───────────────────────────── route formulas ─────────────────────────────
def route_j5(answers, packet_flags=(), truncated=False, risk_ceiling_hit=False, runtime_changed=False):
    """回 {"route_recommended","route_reason","signals"}。deterministic;唯一合法來源。"""
    t = THRESHOLDS["J5"]
    g3 = answers.get("g3_route", {})
    risk = answers.get("risk", {})
    complete = answers.get("evidence_complete", {}).get("noul")
    choice = g3.get("choice")
    p_auto = g3.get("probabilities", {}).get("AUTO_SHIP")
    signals = {"choice": choice, "p_auto_ship": p_auto, "risk_score": risk.get("score"),
               "evidence_complete": complete, "flags": list(packet_flags), "truncated": bool(truncated)}
    if runtime_changed:
        return _route("HUMAN", "runtime_modified_this_session", signals)
    if risk_ceiling_hit:
        return _route("HUMAN", "risk_ceiling_override", signals)
    if truncated:
        return _route("HUMAN", "packet_truncated", signals)
    if packet_flags:
        return _route("HUMAN", "header_body_conflict:" + ",".join(packet_flags), signals)
    if choice == "REQUEST_CHANGES":
        return _route("REQUEST_CHANGES", "g3_route=REQUEST_CHANGES", signals)
    if choice != "AUTO_SHIP":
        return _route("HUMAN", "g3_route=%s" % choice, signals)
    if p_auto is None or p_auto < t["auto_choice_min"]:
        return _route("HUMAN", "auto_probability_below_threshold(%s<%s)" % (p_auto, t["auto_choice_min"]), signals)
    if risk.get("score") is None or risk["score"] > t["risk_max"]:
        return _route("HUMAN", "risk_above_ceiling(%s>%s)" % (risk.get("score"), t["risk_max"]), signals)
    if complete is None or complete < t["evidence_complete_min"]:
        return _route("HUMAN", "evidence_complete_below_threshold(%s<%s)" % (complete, t["evidence_complete_min"]), signals)
    return _route("AUTO", "all_auto_conditions_met", signals)


def route_j1(answers, truncated=False, packet_flags=()):
    """回 {"next","weakest_dimension","route_reason","signals"}。next ∈ START_DECIDE|ASK_MORE|NEEDS_OWNER_DECISION。"""
    t = THRESHOLDS["J1"]
    clarity = {dim: answers.get(dim, {}).get("noul") for dim in J1_CLARITY_DIMS}
    owner = answers.get("owner_call_pending", {}).get("noul")
    ambiguity = answers.get("ambiguity", {}).get("score")
    nxt = answers.get("next", {})
    signals = {"clarity": clarity, "owner_call_pending": owner, "ambiguity": ambiguity,
               "next_choice": nxt.get("choice"), "flags": list(packet_flags), "truncated": bool(truncated)}
    known = {k: v for k, v in clarity.items() if v is not None}
    weakest = min(known, key=known.get) if known else None   # 從 atomic signals 取,不從 next 逆推
    if truncated or packet_flags:
        return {"next": "ASK_MORE", "weakest_dimension": weakest,
                "route_reason": "packet_truncated_or_flagged", "signals": signals}
    if owner is not None and owner >= t["owner_call_min"]:
        return {"next": "NEEDS_OWNER_DECISION", "weakest_dimension": None,
                "route_reason": "owner_call_pending>=%s" % t["owner_call_min"], "signals": signals}
    if len(known) < len(J1_CLARITY_DIMS):
        return {"next": "ASK_MORE", "weakest_dimension": weakest,
                "route_reason": "clarity_signal_missing", "signals": signals}
    if min(known.values()) < t["clarity_min"] or (ambiguity is not None and ambiguity > t["ambiguity_max"]):
        return {"next": "ASK_MORE", "weakest_dimension": weakest,
                "route_reason": "weakest_dimension=%s" % weakest, "signals": signals}
    p_start = nxt.get("probabilities", {}).get("START_DECIDE")
    if nxt.get("choice") == "START_DECIDE" and p_start is not None and p_start >= t["start_min"]:
        return {"next": "START_DECIDE", "weakest_dimension": None,
                "route_reason": "clarity_ok_and_start>=%s" % t["start_min"], "signals": signals}
    return {"next": "ASK_MORE", "weakest_dimension": weakest,
            "route_reason": "start_probability_below_threshold", "signals": signals}


def route_j3(answers):
    """只回 recommendation;永遠不產生 verdict / ACCEPTED。"""
    p = answers.get("demo_worth_it", {}).get("noul")
    worth = p is not None and p >= THRESHOLDS["J3"]["demo_min"]
    return {"recommendation": "DEMO_WORTH_IT" if worth else "DEMO_OPTIONAL",
            "demo_worth_it": p, "writes_verdict": False}


def route_taken(gate, level, route_recommended, graduated=False):
    """把 recommendation 轉成實際採取的 route。shadow 永遠 HUMAN;J5 未畢業永遠 HUMAN。"""
    if level == "off":
        return None, "gate_off"
    if level == "shadow":
        return "HUMAN", "shadow_mode"
    if gate == "J5" and route_recommended == "AUTO" and not graduated:
        return "HUMAN", "j5_auto_not_graduated"
    if route_recommended not in ("AUTO", "HUMAN", "REQUEST_CHANGES"):
        raise JevError("route_taken: 未知 route %r" % route_recommended)
    return route_recommended, "live"


def _route(route, reason, signals):
    fp = policy_fingerprint()
    return {"route_recommended": route, "route_reason": reason, "signals": signals,
            "policy_version": "%s+%s" % (POLICY_VERSION, fp),            # 與 manifest 同一個值
            "route_formula_version": "%s+%s" % (ROUTE_FORMULA_VERSION, fp)}


# ─────────────────────────── budget / breaker / no-op ─────────────────────
class Budget(object):
    """daily cap:attempts 與 input tokens 先到者停。reserve 上界在前、可信 usage 才 reconcile。"""

    def __init__(self, attempts_cap=DAILY_ATTEMPTS_CAP, tokens_cap=DAILY_INPUT_TOKENS_CAP):
        self.attempts_cap = attempts_cap
        self.tokens_cap = tokens_cap
        self.attempts = 0
        self.reserved = {}
        self.settled = 0
        self._next = 1

    def tokens_committed(self):
        return self.settled + sum(self.reserved.values())

    def can_reserve(self, upper_bound):
        if upper_bound is None or upper_bound <= 0:
            raise JevError("reserve 上界必須是正整數(未知用量不得當 0)")
        return (self.attempts + 1 <= self.attempts_cap
                and self.tokens_committed() + upper_bound <= self.tokens_cap)

    def reserve(self, upper_bound):
        """每次 HTTP attempt(含 retry / variant / remote reevaluation)都算一次。"""
        if not self.can_reserve(upper_bound):
            return None
        rid = self._next
        self._next += 1
        self.attempts += 1
        self.reserved[rid] = int(upper_bound)
        return rid

    def reconcile(self, rid, usage):
        """只有 usage_status=known 才把保留額換成實際值;unknown 保留上界,不退款。"""
        if rid not in self.reserved:
            return False
        if not isinstance(usage, dict) or usage.get("usage_status") != "known":
            return False
        actual = usage.get("input_tokens")
        if not isinstance(actual, int) or actual < 0:
            return False
        self.settled += actual
        del self.reserved[rid]
        return True

    def remaining(self):
        return {"attempts": self.attempts_cap - self.attempts,
                "input_tokens": self.tokens_cap - self.tokens_committed()}


class Breaker(object):
    """per key(session / gate)連續失敗 ≥ threshold → open;成功歸零。"""

    def __init__(self, threshold=BREAKER_THRESHOLD):
        self.threshold = threshold
        self.failures = {}

    def is_open(self, key):
        return self.failures.get(key, 0) >= self.threshold

    def record(self, key, ok):
        if ok:
            self.failures[key] = 0
        else:
            self.failures[key] = self.failures.get(key, 0) + 1


def noop(reason, usage=None):
    return {"status": "noop", "reason": reason, "answers": None, "model": None,
            "usage": usage or {"input_tokens": None, "output_tokens": None, "usage_status": "unknown_reserved"}}


def evaluate(transport, request, questions, clock, est_input_tokens, deadline_s=J1_DEADLINE_S,
             budget=None, breaker=None, breaker_key="default"):
    """一次 attempt。任何**傳輸／回應**錯誤 → no-op(回現況),絕不 foreground retry。

    `est_input_tokens` 必填且為正整數(§8.2 規則 1:發送前先 reserve 保守上界;未知用量不得當 0):
    呼叫端組包錯誤是程式錯誤,fail-loud 不 no-op。
    """
    if not isinstance(est_input_tokens, int) or isinstance(est_input_tokens, bool) or est_input_tokens <= 0:
        raise JevError("evaluate: est_input_tokens 必須是正整數上界(用 packet.estimate_input_tokens)")
    if breaker is not None and breaker.is_open(breaker_key):
        return noop("breaker_open")
    rid = None
    if budget is not None:
        rid = budget.reserve(est_input_tokens)
        if rid is None:
            return noop("budget_exhausted")
    started = clock()
    try:
        raw = transport.send(request)
    except TransportError as exc:
        if breaker is not None:
            breaker.record(breaker_key, False)
        return noop("transport:" + exc.kind)
    except Exception as exc:  # 任何未預期例外同樣 no-op,不得讓 Jev 例外打斷原流程
        if breaker is not None:
            breaker.record(breaker_key, False)
        return noop("unexpected:" + type(exc).__name__)
    elapsed = clock() - started
    if elapsed > deadline_s:
        if breaker is not None:
            breaker.record(breaker_key, False)
        return noop("deadline_exceeded(%.3fs>%.3fs)" % (elapsed, deadline_s))
    try:
        parsed = parse_response(raw, questions)
    except TransportError as exc:
        if breaker is not None:
            breaker.record(breaker_key, False)
        return noop("transport:" + exc.kind)
    if budget is not None and rid is not None:
        budget.reconcile(rid, parsed["usage"])       # unknown → 保留上界不退款
    if breaker is not None:
        breaker.record(breaker_key, True)
    return {"status": "ok", "reason": "", "answers": parsed["answers"],
            "model": parsed["model"], "usage": parsed["usage"], "elapsed_s": elapsed,
            "raw": raw}   # raw response 只給 local replay store;durable 層 assert_durable_safe 會拒它


class ShadowQueue(object):
    """J5 shadow:前景只 enqueue(可序列化),不等 HTTP。latency 要量測,不宣稱 0ms。"""

    def __init__(self):
        self.items = []

    def enqueue(self, item, clock):
        import json
        started = clock()
        payload = json.dumps(item, ensure_ascii=False, sort_keys=True)
        self.items.append(payload)
        return clock() - started


def measure_enqueue_latency(n=200, payload_bytes=20000):
    """真實量測 enqueue p50/p95(秒)。回 dict;測試只斷言「有數字、非 0 宣稱」。"""
    import time
    q = ShadowQueue()
    item = {"packet": "x" * payload_bytes, "gate": "J5"}
    samples = []
    for _ in range(n):
        samples.append(q.enqueue(item, time.perf_counter))
    samples.sort()
    return {"n": n, "p50_s": samples[len(samples) // 2], "p95_s": samples[int(len(samples) * 0.95) - 1],
            "max_s": samples[-1]}
