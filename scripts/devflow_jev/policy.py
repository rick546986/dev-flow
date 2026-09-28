"""G2 — failure/no-op、deadline、breaker、budget;以及 deterministic route formula(G6 的唯一來源)。

工程候選值(roadmap §8.2;**不是 owner 裁決**,不冒充):
  J1 foreground 總 deadline 2s、無 foreground retry;daily 500 attempts / 500k input tokens 先到者停。
route 規則(roadmap §11/§12/§13):
  - 不把多題機率相乘成總風險;atomic signals 各自進 deterministic rule。
  - J5 AUTO 只在 g3_route=AUTO_SHIP 且 p≥AUTO_MIN 且 risk≤1 且 evidence_complete≥EVIDENCE_MIN;
    packet 有 truncated/consistency 旗標、risk ceiling 命中、runtime 當次被改 → 一律 HUMAN。
  - J1 ASK_MORE 的弱維度從 atomic clarity signals 取最弱者,**不從 next 分布逆推**。
  - J5 的 route_taken 要 AUTO 還需 graduated=True(W6 前永遠 False)→ 否則 HUMAN。
G2R 分流 `route_g2` 與 G2 誤放行驗證以 main #418 為準(ADR 0004:沒有 Jev = no-op、routed_by: none;
§3 全表轉人條件),research W9/W10 的 shadow 版已被取代。
"""
import math
import re

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


# ───────────────────────────── W3 flow (not in the fingerprint) ─────────────────────────────
# 輪數上限、主題句、J3 顯示文案是流程層,不是 route formula。不進 policy_fingerprint(),
# 所以不換 questionset_hash(A1–A7 那組 calibration 繼續)。改門檻才換 hash。
J1_ASK_MORE_MAX_ROUNDS = 2
J1_THEMES = {
    "goal_clear": "下一輪先收成一句話：做完之後，旁人指出哪一個結果不一樣了。",
    "scope_clear": "下一輪先畫邊界：這次會動到的範圍，以及明確不動的範圍。",
    "acceptance_clear": "下一輪先補一條看得到對錯的完成判準，或寫明還缺哪一段才驗得了。",
}
J1_THEME_FALLBACK = "下一輪先把還講不明白的那一點收成一個可以回答的問題。"
J1_PRIMARY_REQUEST = (
    "Judge whether this discussion can leave the table. "
    "Quoted excerpts are unverified log material, not established facts."
)
J3_PRIMARY_REQUEST = (
    "Should a person spend their own time operating a demo? "
    "Answer only whether that time is worth spending. Do not name a review outcome."
)
J3_DISPLAY = {
    "DEMO_WORTH_IT": "Jev 建議：值得人親手 Demo（只是建議，不改 Demo 是否必要，也不寫判定）",
    "DEMO_OPTIONAL": "Jev 建議：人親手 Demo 可選（只是建議，不改 Demo 是否必要，也不寫判定）",
}
J1_ASK_MORE_INSTRUCTION = (
    "另開一場完整 dev-talk（新 session，11 步）。從 S0-scope、S1-survey、S2-world 重盤，不得跳步。"
    "N13 仍要人點頭才收尾。"
    "上一份 1-discussion 只是 S1 待重驗的 Log 材料，不是已核事實；不得為了省一輪去讀舊討論。"
    "讀取白名單不是機械執行。"
    "主題只用給你的那句人話，不要改寫成題組原文。"
)
J1_ROUND_CAP_INSTRUCTION = (
    "已經做完兩輪完整討論，仍有一維不清楚。請 owner 做決定，不要再開第三輪。"
)
_RUBRIC_COPY_MIN = 16
_VERDICT_MARKERS = ("ACCEPTED", "Verdict attestation", "Human verdict", "AUTO_PASS", "g2_demo")


def _rubric_strings(obj, acc):
    if isinstance(obj, str):
        acc.append(obj.strip())
    elif isinstance(obj, dict):
        for key, value in obj.items():
            _rubric_strings(key, acc)
            _rubric_strings(value, acc)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            _rubric_strings(value, acc)


def assert_no_rubric_copy(text, gate):
    """主題句／請求句不得包含題組原文(roadmap §11:不抄 rubric)。"""
    if not isinstance(text, str) or not text.strip():
        raise JevError("assert_no_rubric_copy: 空字串")
    from .manifest import load_questions
    questions = load_questions()[gate]
    strings = []
    _rubric_strings(questions, strings)
    for rubric in strings:
        if len(rubric) >= _RUBRIC_COPY_MIN and (rubric in text or text in rubric):
            raise JevError("文字抄了 %s 題組原文" % gate)
    return text


def j1_theme(weakest_dimension):
    """人話主題。weakest_dimension 必須已由 atomic clarity signals 決定,本函式不看 next 機率。"""
    theme = J1_THEMES.get(weakest_dimension, J1_THEME_FALLBACK)
    return assert_no_rubric_copy(theme, "J1")


def j1_effect(next_step, weakest_dimension, rounds_completed):
    """把 route_j1 的 next 收成流程指令。rounds_completed 含本輪。

    不接收 next 的 probabilities:弱維度只走參數 weakest_dimension(由 route_j1 從 clarity noul 取出)。
    第 2 輪仍是 ASK_MORE → NEEDS_OWNER_DECISION,不再開第三輪。
    """
    if next_step not in ("START_DECIDE", "ASK_MORE", "NEEDS_OWNER_DECISION"):
        return None
    if not isinstance(rounds_completed, int) or isinstance(rounds_completed, bool) or rounds_completed < 1:
        raise JevError("j1_effect: rounds_completed 必須是正整數")
    capped = next_step == "ASK_MORE" and rounds_completed >= J1_ASK_MORE_MAX_ROUNDS
    step = "NEEDS_OWNER_DECISION" if capped else next_step
    effect = {"START_DECIDE": "start_decide", "ASK_MORE": "ask_more",
              "NEEDS_OWNER_DECISION": "needs_owner_decision"}[step]
    out = {
        "effect": effect,
        "next": step,
        "model_next": next_step,
        "weakest_dimension": weakest_dimension,
        "rounds_completed": rounds_completed,
        "ask_more_max_rounds": J1_ASK_MORE_MAX_ROUNDS,
        "round_capped": capped,
        "writes_verdict": False,
        "writes_g2_verdict": False,
        "writes_g3_verdict": False,
        "skip_redundant_clarity_question": effect == "start_decide",
        "stop_before_decide": effect == "needs_owner_decision",
        "theme": j1_theme(weakest_dimension) if effect == "ask_more" else None,
        "restart": None,
        "instruction": None,
    }
    if effect == "ask_more":
        out["restart"] = {
            "new_session": True,
            "restart_nodes": ["S0-scope", "S1-survey", "S2-world"],
            "full_11_steps": True,
            "n13_human_nod_required": True,
            "read_whitelist_is_not_mechanical_execution": True,
            "prior_discussion_is_not_established_fact": True,
            "do_not_read_old_discussion_to_skip_a_round": True,
        }
        out["instruction"] = assert_no_rubric_copy(J1_ASK_MORE_INSTRUCTION, "J1")
    elif effect == "needs_owner_decision" and capped:
        out["instruction"] = assert_no_rubric_copy(J1_ROUND_CAP_INSTRUCTION, "J1")
    return out


def sanitize_j3(rec):
    """模型或被替換的 route_j3 只要跑出封閉集合外,整筆作廢。signals 不夾自由文字。"""
    if not isinstance(rec, dict):
        return None
    recommendation = rec.get("recommendation")
    if recommendation not in J3_DISPLAY or rec.get("writes_verdict") is not False:
        return None
    return {"recommendation": recommendation, "demo_worth_it": rec.get("demo_worth_it"), "writes_verdict": False}


def j3_effect(recommendation):
    """封閉的兩句顯示文案。不接收模型自由文字。"""
    if recommendation not in J3_DISPLAY:
        return None
    advice = {
        "effect": "show_recommendation",
        "recommendation": recommendation,
        "display": J3_DISPLAY[recommendation],
        "writes_verdict": False,
        "writes_attestation": False,
        "writes_g2_verdict": False,
        "writes_g3_verdict": False,
        "changes_demo_requirement": False,
        "polarity_unchanged": True,
    }
    _assert_no_verdict_markers(advice)
    return advice


def _assert_no_verdict_markers(obj):
    import json
    blob = json.dumps(obj, ensure_ascii=False)
    for marker in _VERDICT_MARKERS:
        if marker in blob:
            raise JevError("Jev 輸出含禁止標記 %s" % marker)
    return obj


def refuse_j3_write(prototype_text, advice):
    """任何 Jev 回應的唯一「寫入」路徑:不寫。

    不是封閉建議(顯示文案被改、writes_verdict 不是 false、recommendation 跑出兩句之外)
    一律拒絕。封閉建議回傳原型原文,呼叫端不得落盤。
    """
    if not isinstance(prototype_text, str):
        raise JevError("refuse_j3_write: 原型必須是字串")
    if not isinstance(advice, dict):
        raise JevError("J3 回應不是封閉建議物件,拒絕寫入")
    if advice.get("writes_verdict") is not False or advice.get("writes_attestation") is not False:
        raise JevError("J3 不得寫 verdict 或 attestation")
    if advice.get("writes_g2_verdict") is not False or advice.get("writes_g3_verdict") is not False:
        raise JevError("J3 不得寫 G2/G3 verdict")
    if advice.get("changes_demo_requirement") is not False:
        raise JevError("J3 不得改 Demo 是否必要")
    recommendation = advice.get("recommendation")
    if recommendation not in J3_DISPLAY or advice.get("display") != J3_DISPLAY[recommendation]:
        raise JevError("J3 display 不在封閉集合,拒絕寫入")
    if advice.get("effect") != "show_recommendation":
        raise JevError("J3 effect 不是 show_recommendation,拒絕寫入")
    _assert_no_verdict_markers(advice)
    return prototype_text


def route_taken(gate, level, route_recommended, graduated=False):
    """把 recommendation 轉成實際採取的 route。shadow 永遠 HUMAN;J5 未畢業永遠 HUMAN。"""
    if level == "off":
        return None, "gate_off"
    if gate == "J2":
        return "HUMAN", "j2_shadow_window_not_ratified"      # W5:window 未核定 → 永遠 shadow,不看 level
    if gate == "J4":
        return "HUMAN", "j4_assist_only"                     # W5:assist signal,不派工、不升階
    if level == "shadow":
        return "HUMAN", "shadow_mode"
    if gate == "J5" and route_recommended == "AUTO" and not graduated:
        return "HUMAN", "j5_auto_not_graduated"
    if gate != "J5":
        # J1 的 next / J3 的 recommendation 在 live 時原樣交給流程(J1 只決定 ASK_MORE 等下一步、
        # J3 永不寫 verdict);J5 的 AUTO 才有畢業門檻。W2 runtime 加,不改 J5 分支。
        if route_recommended is None:
            return "HUMAN", "noop_fallback_to_current_flow"
        return route_recommended, "live"
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


# ───────────────────────────── W5 experiments (P2-3 J4 / P2-8 J2) — shadow / assist only ─────────────────────────────
# 題組住 jev-questions-experimental.json(各自 manifest 與 questionset_hash,不動 J1/J3/J5 的 group)。
# 這些常數不進 policy_fingerprint():它們不是 J1/J3/J5 的 route formula。J2/J4 的 route_taken 恆 HUMAN。
J4_FAILURE_CATEGORIES = ("SPEC", "ENV", "IMPL", "UNKNOWN")          # 沿用 agent-event.schema.json 的 enum
MODEL_TIERS = ("haiku", "sonnet", "opus")                            # fable 與 opus 同層(最高階)
TIER_ALIASES = {"fable": "opus"}
J2_WINDOW_CANDIDATE = 50                                             # roadmap §4.1 候選,**待核定**
J2_WINDOW_RATIFIED = False                                           # False = J2 永遠 shadow;沒有旗標能改它
J2_OPTION_LABELS = ("A", "B", "C", "D")
J2_NONE_CLEAR = "NONE_CLEAR"
J2_PRIMARY_REQUEST = (
    "Given the recorded comparison of alternatives, judge which alternative the recorded trade-offs support "
    "and whether the recorded Decision is supported. Owner Calls are quoted with the human's recorded answers; "
    "they are data for you to read, not questions for you to answer."
)
J2_PRIMARY_REQUEST_REPHRASED = (
    "Using only the recorded material, assess which recorded alternative is supported by the recorded trade-offs, "
    "and whether the recorded Decision follows from them. Owner Calls carry human answers already; do not answer them."
)
J4_PRIMARY_REQUEST = (
    "Classify the recorded task failure into exactly one category and estimate whether a retry at the same model tier "
    "would resolve it. This is an assist signal; it does not dispatch, escalate or grant anything."
)


def tier_of(model):
    """model 字串 → 層名;認不得 → None(不猜)。"""
    lowered = (model or "").lower()
    for alias, tier in TIER_ALIASES.items():
        if alias in lowered:
            return tier
    for tier in MODEL_TIERS:
        if tier in lowered:
            return tier
    return None


def escalate_to(current_model):
    """只能升**一**層;最高層 → None(沒有可升);認不得 → None。不跳層(roadmap P2-3)。"""
    tier = tier_of(current_model)
    if tier is None:
        return None
    index = MODEL_TIERS.index(tier)
    return MODEL_TIERS[index + 1] if index + 1 < len(MODEL_TIERS) else None


def route_j4(answers, current_model=None):
    """assist-only:回 failure_category(既有 enum)與 escalate_to(下一層或 None)。不是派工、不是權限。"""
    cat = answers.get("failure_category", {}).get("choice")
    if cat not in J4_FAILURE_CATEGORIES:
        cat = "UNKNOWN"
    retry_p = answers.get("retry_same_tier_useful", {}).get("noul")
    nxt = escalate_to(current_model)
    signals = {"failure_category": cat, "retry_same_tier_useful": retry_p, "current_tier": tier_of(current_model)}
    if cat == "UNKNOWN":
        suggestion = "human_triage"
    elif retry_p is not None and retry_p >= 0.5:
        suggestion = "retry_same_tier"
    elif nxt is None:
        suggestion = "human_triage"           # 已在最高層或認不得層 → 不能再升
    else:
        suggestion = "escalate_one_tier"
    return {"route_recommended": suggestion, "route_reason": "j4_assist:%s" % cat, "failure_category": cat,
            "escalate_to": nxt if suggestion == "escalate_one_tier" else None, "assist_only": True,
            "writes_dispatch": False, "signals": signals}


def route_j2(answers, option_identities):
    """option_identities: {"A": "<原方案名>", ...}(順序擾動後的對照)。回 shadow 建議;永不 AUTO_PASS。"""
    choice = answers.get("preferred_option", {}).get("choice")
    supported = answers.get("decision_supported", {}).get("noul")
    resolved = answers.get("owner_calls_resolved", {}).get("noul")
    completeness = answers.get("tradeoff_completeness", {}).get("score")
    identity = option_identities.get(choice) if choice in option_identities else None
    return {"route_recommended": choice if choice in J2_OPTION_LABELS or choice == J2_NONE_CLEAR else J2_NONE_CLEAR,
            "preferred_identity": identity, "route_reason": "j2_shadow:%s" % (choice or "-"),
            "decision_supported": supported, "owner_calls_resolved": resolved, "tradeoff_completeness": completeness,
            "auto_pass": False, "window_ratified": J2_WINDOW_RATIFIED, "signals": {"choice": choice}}


def j2_stability(variant_routes):
    """order／phrasing variants 的一致性。只做 evaluation:不穩定 → unstable=True、不得畢業;不灌 n(同 case_id)。"""
    identities = [r.get("preferred_identity") for r in variant_routes if r.get("route_recommended") != J2_NONE_CLEAR]
    none_clear = sum(1 for r in variant_routes if r.get("route_recommended") == J2_NONE_CLEAR)
    distinct = sorted(set(i for i in identities if i is not None))
    stable = len(variant_routes) >= 2 and none_clear == 0 and len(distinct) == 1
    return {"variants": len(variant_routes), "distinct_identities": distinct, "none_clear": none_clear,
            "stable": stable, "unstable": not stable, "graduation_eligible": False,
            "note": "stability study only; J2 window not ratified; n unaffected"}


# ───────────────────────────── G2R 分流 + G2 誤放行(main #418,G2 自動審查上線;ADR 0004)─────────────────────────────
# research W9 `g2r-shadow`／W10 版本已由 main #418 取代(沒有 Jev = no-op、routed_by: none;ADR §3 全表轉人條件)。
# 本段以 #418 為準;budget／breaker／noop／evaluate 共用上方 research 原版(evaluate 以關鍵字呼叫)。
from .manifest import canonical_json, sha256_hex  # noqa: E402  (manifest 不 import policy,無循環)
from .packet import privacy_scan  # noqa: E402,F401  (送 Jev 前 privacy 掃描;同一組 pattern)

# 當次改到 Jev runtime／questions／config → 當次 HUMAN(同 provenance.RUNTIME_PATH_MARKERS 的意圖;
# G2R 版不限 scripts/ 前綴,散發副本 docs/dev/tools/devflow_jev/ 也算)。
JEV_RUNTIME_MARKERS = ("devflow_jev/", "devflow-jev.py", "jev-questions", ".dev-flow/jev.yaml")
G2R_DEADLINE_S = 60.0          # 單次 Jev 呼叫的等待上限;逾時 = no-op(沒有 Jev)
G2R_STATE_MAX_CHARS = 60000    # 4-spec 超過就不送(不裁切):jev_status=packet_too_large = 沒有 Jev


def runtime_changed(changed_paths, markers=JEV_RUNTIME_MARKERS):
    """當次改到 Jev runtime / questions / config 的路徑(ADR §3「當次修改 Jev runtime」)。"""
    return [p for p in changed_paths if any(m in p for m in markers)]


def risk_ceiling_hit(changed_paths, risk_paths=None):
    """機械 risk ceiling:路徑含任一 risk_paths 標記就算命中(與 provenance.risk_ceiling_hit 同規則、同一份清單)。"""
    risk_paths = RISK_PATHS_DEFAULT if risk_paths is None else risk_paths
    hits = []
    for path in changed_paths:
        for marker in risk_paths:
            if marker in path:
                hits.append(path)
                break
    return hits


# route_g2 只**分流**:
#   - AUTO  = 「可以交給 fresh-context agent reviewer + 機械檢查」,**不是通過**、不是 verdict。
#   - HUMAN = G2 回人審。任一轉人條件命中即 HUMAN;reasons 列出**全部**命中的條件(不是第一個)。
#   - Jev 只分流、不當 reviewer、不寫 verdict。沒有 Jev = no-op:不擋、不放寬,其餘條件照判(ADR 0004 §2)。
G2R_THRESHOLDS = {"auto_pass_min": 0.85,   # p(AUTO_PASS) ≥ 0.85 才走 agent;< 0.85 → HUMAN(剛好 0.85 = 交給 agent)
                  "risk_human_min": 2}      # risk ≥ 2 → HUMAN
G2R_JEV_CHOICES = ("AUTO_PASS", "HUMAN_REVIEW", "REQUEST_CHANGES")
# 4-spec `- Risk:` 映射(只在沒有 Jev 時用;有 Jev 時只看 Jev 的 risk 分數)。
# 模板的 Risk 是 normal|high(缺省 normal);另收 medium/low(policy 與 hooks 同一集合)。
G2R_SPEC_RISK_SCORE = {"high": 2, "medium": 1, "normal": 0, "low": 0}
G2R_ROUTES = ("AUTO", "HUMAN")
G2R_NO_JEV = "no_jev"          # case.jev_status 只有 ok|no_jev;沒有 Jev 的細部原因記在分流紀錄 jev_reason(不進 case hash)
G2R_AUTO_MEANS = "handoff_to_fresh_agent_reviewer_and_mechanical_checks_not_a_pass"
G2R_CASE_KEYS = ("slug", "declared_paths", "spec_risk", "owner_calls_unresolved", "demo_verdict_required",
                 "authored_by_present", "jev", "jev_status")
# 送 Jev 的題組(G2R 自己的一組;不進任何 J1–J5 題組)。score criteria 位置 = level。
G2R_QUESTIONS = {
    "g2_route": {
        "type": "choice",
        "text": "Given only this change spec (4-spec) and its declared paths, which G2 handling does it support? "
                "You are routing only; you are not the reviewer and your answer is not a verdict.",
        "criteria": {
            "AUTO_PASS": "Every requirement has scenarios with concrete inputs and assertable outputs, all drafting "
                         "decisions are resolved, the verification profile matches the lane, and nothing needs a "
                         "human judgement before a fresh reviewer agent checks it.",
            "HUMAN_REVIEW": "The spec is complete enough to review, but at least one item needs a human judgement "
                            "(product value, irreversible change, unclear ownership).",
            "REQUEST_CHANGES": "The spec is missing scenarios, contradicts itself, or leaves decisions open.",
        },
    },
    "risk": {
        "type": "score",
        "text": "What kind of change does this spec describe?",
        "criteria": [
            "cosmetic: Only presentation or wording changes; no persisted data, no external call, no permission.",
            "contained: Logic changes behind an existing interface; no schema, permission or external contract change.",
            "sensitive: Changes persisted data shape, a public or cross-module interface, or an external call.",
            "critical: Touches money, authentication, authorization, secrets, data loss or an irreversible migration.",
        ],
    },
}


def g2r_fingerprint():
    payload = {"g2r_thresholds": G2R_THRESHOLDS, "g2r_jev_choices": list(G2R_JEV_CHOICES),
               "g2r_spec_risk_score": G2R_SPEC_RISK_SCORE, "risk_paths_default": list(RISK_PATHS_DEFAULT),
               "g2r_questions": G2R_QUESTIONS, "jev_absent": "noop",
               "jev_runtime_markers": list(JEV_RUNTIME_MARKERS)}
    return sha256_hex(canonical_json(payload))[7:19]


# `- Risk:` 讀法:第一條 `- Risk:` 行就是答案;值不分大小寫,正規化成小寫。
# 同一規則在 hooks/devflow-lib.py `spec_risk_value()`(OC-4 / check-spec-gate C2 用);
# 兩邊由 scripts/devflow_jev/test_g2.py 同一組案例釘住一致。
SPEC_RISK_VALUES = tuple(sorted(G2R_SPEC_RISK_SCORE))
_SPEC_RISK_LINE_RE = re.compile(r"^\s*-\s*Risk:(.*)$")
_SPEC_RISK_EMPTY = ("", "—", "-", "－")


def spec_risk_of(spec_text):
    """4-spec `- Risk:` 首值,正規化成小寫(`High`／`HIGH` → `high`)。

    - 整份沒有 `- Risk:` 行 → None(check-spec-gate C2 另外會紅)。
    - 寫了 `- Risk:` 但值是空的(含 `—`)→ JevError(不當成低風險)。
    - 首字不是 high|medium|normal|low(大小寫不拘)→ JevError(`hgih`／`critical`／`高` 都擋)。"""
    for line in spec_text.splitlines():
        m = _SPEC_RISK_LINE_RE.match(line)
        if not m:
            continue
        value = m.group(1).strip()
        if value in _SPEC_RISK_EMPTY:
            raise JevError("4-spec `- Risk:` 是空值 —— 必須寫 %s 其中之一(大小寫不拘),不當成低風險"
                           % "|".join(SPEC_RISK_VALUES))
        word = re.match(r"([A-Za-z]+)\b", value)
        risk = word.group(1).lower() if word else None
        if risk not in G2R_SPEC_RISK_SCORE:
            raise JevError("4-spec `- Risk: %s` 不認得(只收 %s,大小寫不拘)—— 不當成低風險"
                           % (value, "|".join(SPEC_RISK_VALUES)))
        return risk
    return None


def _validate_g2r_case(case):
    if not isinstance(case, dict):
        raise JevError("G2R case 必須是 dict")
    missing = [k for k in G2R_CASE_KEYS if k not in case]
    if missing:
        raise JevError("G2R case 缺欄 %s(缺欄不猜,fail-loud)" % ",".join(missing))
    extra = sorted(set(case) - set(G2R_CASE_KEYS))
    if extra:
        raise JevError("G2R case 有未知欄 %s" % ",".join(extra))
    if not isinstance(case["slug"], str) or not case["slug"]:
        raise JevError("G2R case.slug 必須是非空字串")
    paths = case["declared_paths"]
    if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        raise JevError("G2R case.declared_paths 必須是字串 list(沒宣告 = [])")
    risk = case["spec_risk"]
    if risk is not None and risk not in G2R_SPEC_RISK_SCORE:
        raise JevError("G2R case.spec_risk=%r 不認得(只收 %s 或 null;先過 spec_risk_of)"
                       % (risk, "|".join(SPEC_RISK_VALUES)))
    oc = case["owner_calls_unresolved"]
    if isinstance(oc, bool) or not isinstance(oc, int) or oc < 0:
        raise JevError("G2R case.owner_calls_unresolved 必須是 ≥0 的整數")
    if not isinstance(case["demo_verdict_required"], bool):
        raise JevError("G2R case.demo_verdict_required 必須是 bool")
    if not isinstance(case["authored_by_present"], bool):
        raise JevError("G2R case.authored_by_present 必須是 bool")
    jev, status = case["jev"], case["jev_status"]
    if jev is not None and not isinstance(jev, dict):
        raise JevError("G2R case.jev 必須是 null(沒有 Jev)或 answers dict")
    if status not in ("ok", G2R_NO_JEV):
        raise JevError("G2R case.jev_status 必須是 ok 或 %s" % G2R_NO_JEV)
    if (jev is not None) != (status == "ok"):
        raise JevError("G2R case.jev_status=%r 與 jev 不一致(有 answers ⇔ ok)" % status)


def route_g2(case):
    """G2R 分流(deterministic)。回 {"route": AUTO|HUMAN, "reasons": [...], "signals": {...}, ...}。

    case 欄位(全必填;缺欄 → JevError):
      slug                   feature slug
      declared_paths         4-spec 宣告的檔案路徑 list;[] = 沒宣告 → HUMAN(fail-closed,不當成「沒命中」)
      spec_risk              spec_risk_of() 的結果(high|medium|normal|low)或 None(沒寫)
      owner_calls_unresolved 未裁決 Owner Call 條數;>0 → HUMAN
      demo_verdict_required  需要 Demo verdict(human-only)→ HUMAN
      authored_by_present    4-spec 頂欄有合法 authored_by;沒有 → HUMAN(無法證明四眼)
      jev                    None = 沒有 Jev(no-op);否則 {"g2_route": {"choice", "probabilities"}, "risk": {"score"}}
      jev_status             "ok"(有 answers)或 "no_jev"(細部原因在分流紀錄 jev_reason)
    """
    _validate_g2r_case(case)
    t = G2R_THRESHOLDS
    jev = case["jev"]
    reasons = []
    signals = {"jev_present": jev is not None, "jev_status": case["jev_status"],
               "declared_paths": len([p for p in case["declared_paths"] if p.strip()]),
               "spec_risk": case["spec_risk"], "owner_calls_unresolved": case["owner_calls_unresolved"],
               "demo_verdict_required": case["demo_verdict_required"],
               "authored_by_present": case["authored_by_present"]}
    # ① 有 Jev:判的不是 AUTO_PASS 或 p < 0.85 → HUMAN。沒有 Jev = no-op:這條不存在,不擋也不放寬。
    if jev is not None:
        g2 = jev.get("g2_route") if isinstance(jev.get("g2_route"), dict) else {}
        choice = g2.get("choice")
        probs = g2.get("probabilities") if isinstance(g2.get("probabilities"), dict) else {}
        p_auto = probs.get("AUTO_PASS")
        signals.update({"jev_choice": choice, "jev_p_auto_pass": p_auto})
        if choice != "AUTO_PASS":
            reasons.append("jev_g2_route=%s" % choice)
        # 寫成 not (p >= 門檻):NaN 比較恆 False,也要落到 HUMAN(fail-closed)
        if not isinstance(p_auto, (int, float)) or isinstance(p_auto, bool) or not p_auto >= t["auto_pass_min"]:
            reasons.append("jev_p_auto_pass_below_threshold(%s<%s)" % (p_auto, t["auto_pass_min"]))
    # ② 命中 risk_paths;spec 沒宣告任何 path 也算(全是空白字串 = 沒宣告)
    paths = [p.strip() for p in case["declared_paths"] if p.strip()]
    if not paths:
        reasons.append("spec_declares_no_paths")
    else:
        hits = risk_ceiling_hit(paths)
        signals["risk_path_hits"] = hits
        if hits:
            reasons.append("risk_paths_hit:%s" % ",".join(hits))
        rt = runtime_changed(paths)
        if rt:
            reasons.append("jev_runtime_changed:%s" % ",".join(rt))
    # ③ risk ≥ 2:有 Jev 只看 Jev 的 risk 分數(spec 的 Risk: high 不算);沒有 Jev 用 4-spec Risk 映射
    if jev is not None:
        risk_obj = jev.get("risk") if isinstance(jev.get("risk"), dict) else {}
        score = risk_obj.get("score")
        signals.update({"risk_source": "jev", "risk_score": score})
        if not isinstance(score, int) or isinstance(score, bool):
            reasons.append("jev_risk_missing")               # 有 Jev 卻沒給 risk → 無從判 <2,fail-closed
        elif score >= t["risk_human_min"]:
            reasons.append("risk>=%s(jev=%s)" % (t["risk_human_min"], score))
    else:
        score = G2R_SPEC_RISK_SCORE[case["spec_risk"] or "normal"]
        signals.update({"risk_source": "spec", "risk_score": score})
        if score >= t["risk_human_min"]:
            reasons.append("risk>=%s(spec_risk=%s)" % (t["risk_human_min"], case["spec_risk"]))
    # ④ 有沒解決的 Owner Call
    if case["owner_calls_unresolved"] > 0:
        reasons.append("owner_calls_unresolved=%d" % case["owner_calls_unresolved"])
    # ⑤ 需要 Demo verdict
    if case["demo_verdict_required"]:
        reasons.append("demo_verdict_required")
    # ⑥ 缺 authored_by → 無法證明 author ≠ approver
    if not case["authored_by_present"]:
        reasons.append("authored_by_missing")
    route = "HUMAN" if reasons else "AUTO"
    return {"route": route, "reasons": reasons or ["no_human_condition_hit"], "signals": signals,
            "auto_means": G2R_AUTO_MEANS if route == "AUTO" else None,
            "is_pass": False, "writes_verdict": False, "jev_role": "router_only",
            "g2r_policy": "g2r+%s" % g2r_fingerprint()}


def g2r_case_hash(case):
    return sha256_hex(canonical_json(case))


# ───────────────────────────── G2 誤放行(只記錄;research W10 原樣)─────────────────────────────
# 定義:G2R 判 AUTO、G2 由 fresh agent reviewer + 機械檢查放行,之後在 G3 人審或實作階段發現 spec 本身有問題。
# 這裡只驗欄位、算率;不抽查、不自動 revert、不改任何 gate 判定、不動 G2R_THRESHOLDS。率只進 report,不接任何阻擋。
G2M_STAGES = {  # 發現階段 → 准用的發現來源(事件)
    "G3": ("g3_request_changes", "g3_hold"),                               # G3 人審退件,且 7-review 人勾 root_cause: spec
    "implementation": ("spec_amended", "spec_returned", "reverted"),       # 實作中回頭改 spec／spec 被退回 Stage 4／被 revert
}
G2M_RELEASED_BY = ("fresh_agent_reviewer", "human")   # 當初 G2 實際由誰放行;只有前者算「誤放行」
G2M_RECORD_KEYS = ("slug", "case_hash", "g2r_reasons", "discovered_stage", "discovered_via", "evidence_ref",
                   "g2_released_by", "reported_by", "recorded_at")
G2M_RELEASE_KEYS = ("slug", "case_hash", "g2r_reasons", "evidence_ref", "reported_by", "recorded_at")  # agent 放行紀錄
_G2M_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_G2M_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_G2M_ACTOR_RE = re.compile(r"^(human|agent):\S{1,64}$")
_G2M_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
G2M_EVIDENCE_MAX = 200


def _g2m_check_common(rec, keys, what):
    if not isinstance(rec, dict):
        raise JevError("%s 紀錄必須是 dict" % what)
    missing = [k for k in keys if k not in rec]
    if missing:
        raise JevError("%s 缺欄 %s" % (what, ",".join(missing)))
    if not isinstance(rec["slug"], str) or not _G2M_SLUG_RE.match(rec["slug"]):
        raise JevError("slug 只准 [A-Za-z0-9._-]")
    if not isinstance(rec["case_hash"], str) or not _G2M_HASH_RE.match(rec["case_hash"]):
        raise JevError("case_hash 必須是 sha256:<64 小寫 hex>(g2r 紀錄裡的那個)")
    reasons = rec["g2r_reasons"]
    if not isinstance(reasons, list) or not reasons or not all(isinstance(r, str) and r for r in reasons):
        raise JevError("g2r_reasons 必須是非空字串 list(抄自 g2r 紀錄)")
    ev = rec["evidence_ref"]
    if not isinstance(ev, str) or not ev.strip() or ev != ev.strip() or len(ev) > G2M_EVIDENCE_MAX or "\n" in ev:
        raise JevError("evidence_ref 必須是單行非空字串、無前後空白、≤%d 字(7-review 路徑／commit sha／PR 連結)"
                       % G2M_EVIDENCE_MAX)
    if not isinstance(rec["reported_by"], str) or not _G2M_ACTOR_RE.match(rec["reported_by"]):
        raise JevError("reported_by 必須是 human:<名> 或 agent:<id>")
    if not isinstance(rec["recorded_at"], str) or not _G2M_TS_RE.match(rec["recorded_at"]):
        raise JevError("recorded_at 必須是 YYYY-MM-DDTHH:MM:SSZ")


def validate_g2_misrelease(rec):
    """誤放行紀錄的欄位驗證(record 寫入前、report 讀回時都跑同一支)。不合 → JevError。"""
    _g2m_check_common(rec, G2M_RECORD_KEYS, "g2_misrelease")
    stage = rec["discovered_stage"]
    if stage not in G2M_STAGES:
        raise JevError("discovered_stage=%r 不認得(只收 %s)" % (stage, "|".join(G2M_STAGES)))
    if rec["discovered_via"] not in G2M_STAGES[stage]:
        raise JevError("discovered_via=%r 不屬於 %s 階段(只收 %s)"
                       % (rec["discovered_via"], stage, "|".join(G2M_STAGES[stage])))
    if rec["g2_released_by"] not in G2M_RELEASED_BY:
        raise JevError("g2_released_by=%r 不認得(只收 %s)" % (rec["g2_released_by"], "|".join(G2M_RELEASED_BY)))
    if stage == "G3" and not rec["reported_by"].startswith("human:"):
        raise JevError("G3 階段的 root_cause: spec 只准人勾 —— reported_by 必須是 human:<名>")


def validate_g2_agent_release(rec):
    """「G2 真的由 fresh agent reviewer 放行」紀錄的欄位驗證(release 寫入前、report 讀回時都跑同一支)。"""
    _g2m_check_common(rec, G2M_RELEASE_KEYS, "g2_agent_release")


G2M_NO_AGENT_RELEASE_NOTE = "目前沒有任何由 fresh agent reviewer 放行的紀錄,不是 0%"


def _g2m_counts(numerator, denominator, num_name, den_name):
    for name, v in ((num_name, numerator), (den_name, denominator)):
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise JevError("%s 必須是 ≥0 的整數" % name)
    if numerator > denominator:
        raise JevError("%s %d > %s %d —— 資料不一致,不算率" % (num_name, numerator, den_name, denominator))


def g2_misrelease_rate(misreleased, agent_released):
    """誤放行率 = 誤放行數 ÷ 真的由 fresh agent reviewer 放行的 G2R AUTO case 數。
    分母 0 → rate=None、status=insufficient_data(**不是 0%**)。只記錄:沒有門檻、不自動退回人審。"""
    _g2m_counts(misreleased, agent_released, "誤放行數", "agent 放行數")
    if agent_released == 0:
        return {"rate": None, "status": "insufficient_data", "note": G2M_NO_AGENT_RELEASE_NOTE}
    return {"rate": misreleased / agent_released, "status": "ok",
            "note": "n=%d(agent 放行數;不設門檻;率只進 report,不接任何阻擋或回滾)" % agent_released}


def g2_human_counterfactual_rate(human_released_spec_issue, auto_total):
    """反事實率 = G2R 判 AUTO 但實際由人放行、後來發現 spec 有問題的 case 數 ÷ AUTO 總數。不是誤放行率。"""
    _g2m_counts(human_released_spec_issue, auto_total, "人放行後發現 spec 問題數", "AUTO 總數")
    if auto_total == 0:
        return {"rate": None, "status": "insufficient_data",
                "note": "AUTO 總數 = 0:沒有分母,反事實率無法計算(不是 0%)"}
    return {"rate": human_released_spec_issue / auto_total, "status": "counterfactual",
            "note": "反事實:這些 case 實際由人放行,不是誤放行率;n=%d(AUTO 總數)" % auto_total}


# ───────────────────────────── W11 MR 記憶重排序(P2-11) — research / offline ─────────────────────────────
# 定義正本:docs/dev/jev-gate/w11-mr-rerank.md。MR 接在既有 `memory/dev-memory.py ask`(query.py/retrieval.py)
# **之後**:只重排原檢索的前 MR_POOL_SIZE 筆、回前 MR_TOP_K 筆;不換掉原檢索、不寫記憶、不改 retrieval_status、
# 不接任何 gate、不寫 verdict。這裡全是 pure function(零網路);Jev 打分的出境只在 devflow-jev.py 過雙閘門後。
MR_POOL_SIZE = 20                     # C6:原檢索前 20 筆
MR_TOP_K = 5                          # C6:回前 5 筆
MR_RECALL_DELTA_MIN = 0.0             # C5:Recall@5 不降
MR_MRR_DELTA_MIN = 0.05               # C5:MRR 至少 +0.05
MR_MANDATORY_RETENTION_MIN = 1.0      # C5:必留記憶 100% 保留(硬約束)
# 資料量地板:**未校準的暫定值**(W11 研究分支自訂,owner 沒給數字;不是統計推導)。可設定:
# `mr-eval --min-queries N`、`mr-gate --min-queries N` 或 `.dev-flow/jev.yaml` 的 `gates.MR.min_queries`;
# 沒設 = 這個預設。校準方法見 docs/dev/jev-gate/w11-mr-rerank.md §4.6(需要 locked eval set 的真資料)。
MR_EVAL_MIN_QUERIES = 20              # 不足 → insufficient_data,不算通過
MR_EPS = 1e-9                         # 門檻比較的浮點容忍(0.1+0.2 那種誤差不該決定過或不過)
MR_MANDATORY_FIELD = "mandatory"      # 必留標記:候選列上的 `mandatory: true`(本 PR 定義;見 w11 §3)
MR_MANDATORY_REASONS = ("explicit", "current_truth", "invariant", "conflict", "exact_hit")
MR_SCORE_CRITERIA = [
    {"level": 0, "label": "unrelated", "description": "The candidate memory does not mention the subject of the query."},
    {"level": 1, "label": "topical", "description": "The candidate memory mentions the subject but does not help answer the query."},
    {"level": 2, "label": "partial", "description": "The candidate memory answers part of the query or points to where the answer is."},
    {"level": 3, "label": "direct", "description": "The candidate memory directly states the answer to the query."},
]
MR_SUMMARY_MAX = 280                  # 每筆候選送出的去識別摘要上限(字元)
MR_EVAL_SCHEMA = "devflow-jev-mr-eval/1"
MR_SCORE_SOURCES = ("synthetic", "stored_jev")


def mr_fingerprint():
    """C5/C6 常數 + 題目刻度的指紋;改任一個 → 指紋變(同 roadmap §3.4:C5/C6 進 manifest 會換 questionset_hash)。"""
    from .manifest import canonical_json, sha256_hex
    payload = {"pool": MR_POOL_SIZE, "top_k": MR_TOP_K, "recall_delta_min": MR_RECALL_DELTA_MIN,
               "mrr_delta_min": MR_MRR_DELTA_MIN, "mandatory_retention_min": MR_MANDATORY_RETENTION_MIN,
               "eval_min_queries": MR_EVAL_MIN_QUERIES, "criteria": MR_SCORE_CRITERIA,
               "mandatory_reasons": list(MR_MANDATORY_REASONS), "summary_max": MR_SUMMARY_MAX}
    return sha256_hex(canonical_json(payload))[7:19]


def mr_level(has_key, optin):
    """MR 的雙閘門:沿用 gate.py 的兩個輸入(key 有無 × `.dev-flow/jev.yaml` 解析結果)。

    - 沒寫 `gates: MR:` → W11 原行為:只看 `mode:`;mode=off → off;shadow/live → shadow。
    - 有寫 `gates: MR:` → gate.mr_effective_level:min(mode, gates.MR.level),live cap 成 shadow
      (`gate.MR_LIVE_RATIFIED = False`)。回 (level, reason)。"""
    if not has_key:
        return "off", "no_api_key"
    if optin is None:
        return "off", "no_project_optin"
    mode = optin.get("mode") if isinstance(optin, dict) else None
    if mode not in ("off", "shadow", "live"):
        raise JevError("jev.yaml mode %r 不認得" % (mode,))
    if optin.get("mr") is not None:
        from . import gate as _gate
        return _gate.mr_effective_level(has_key, optin)
    if mode == "off":
        return "off", "mode=off"
    return "shadow", "mode=%s(MR 研究分支只到 shadow:不接任何 gate)" % mode


def mr_min_queries(value):
    """驗證可設定的資料量地板(正整數;bool／0／負數／非整數 → JevError)。None → 預設 MR_EVAL_MIN_QUERIES。"""
    if value is None:
        return MR_EVAL_MIN_QUERIES
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise JevError("min_queries 必須是正整數,實得 %r" % (value,))
    return value


MR_GATE_RESULTS = ("pass", "fail", "insufficient_data", "off")


def mr_gate_result(report):
    """mr_eval 報表 → gate 結果(pass|fail|insufficient_data)+ 沒過的條件名。判定完全沿用 mr_eval 的 verdict。"""
    verdict = report["verdict"]
    if verdict not in ("pass", "fail", "insufficient_data"):
        raise JevError("mr_eval verdict %r 不認得" % (verdict,))
    failed = [c["name"] for c in report["conditions"] if not c["pass"]]
    return {"gate_result": verdict, "failed_conditions": failed if verdict == "fail" else [],
            "insufficient": list(report["insufficient"]) if verdict == "insufficient_data" else []}


def mr_candidate_id(row):
    """候選的穩定 id:fixture 的 `id` → retrieval 的 `item_uid` → knowledge_index 的 `path` →
    knowledge 的 `key` → CURRENT fast path 的 `title`。都沒有 → JevError(不猜)。"""
    if not isinstance(row, dict):
        raise JevError("MR 候選必須是 dict")
    for field, prefix in (("id", ""), ("item_uid", ""), ("path", "path:"), ("key", "knowledge:")):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return prefix + value.strip()
    if row.get("fast_path") is True and isinstance(row.get("title"), str) and row["title"].strip():
        return "fact:" + row["title"].strip()
    raise JevError("MR 候選沒有 id/item_uid/path/key 可當穩定 id:%s" % sorted(row)[:8])


def mr_mandatory_reasons(row):
    """必留理由(空 list = 不是必留)。

    - explicit:候選列 `mandatory: true`(本 PR 定義的欄位;值必須是 bool,其它型別 fail-loud)
    - 其餘由既有欄位推得(roadmap P2-11 / v5 §6 列的不可移除類別,只取會出現在 ask results 裡的):
      current_truth(`fast_path: true`)、invariant(knowledge `kind: invariant`)、conflict(`status: CONFLICT`)、
      exact_hit(retrieval `channels` 含 `exact_symbol`)。"""
    reasons = []
    if MR_MANDATORY_FIELD in row:
        flag = row[MR_MANDATORY_FIELD]
        if not isinstance(flag, bool):
            raise JevError("候選 `mandatory` 必須是 true/false,實得 %r" % (flag,))
        if flag:
            reasons.append("explicit")
    if row.get("fast_path") is True:
        reasons.append("current_truth")
    if row.get("item_type") == "knowledge" and row.get("kind") == "invariant":
        reasons.append("invariant")
    if row.get("status") == "CONFLICT":
        reasons.append("conflict")
    channels = row.get("channels")
    if isinstance(channels, dict) and "exact_symbol" in channels:
        reasons.append("exact_hit")
    return reasons


def mr_pool(candidates):
    """原檢索順序的前 MR_POOL_SIZE 筆 → [{"id","orig_rank","mandatory_reasons","row"}]。id 重複 → JevError。"""
    if not isinstance(candidates, list):
        raise JevError("MR candidates 必須是 list(原檢索順序)")
    pool = []
    seen = set()
    for rank, row in enumerate(candidates[:MR_POOL_SIZE], 1):
        cid = mr_candidate_id(row)
        if cid in seen:
            raise JevError("MR 候選 id 重複:%s(同一筆記憶不該出現兩次)" % cid)
        seen.add(cid)
        pool.append({"id": cid, "orig_rank": rank, "mandatory_reasons": mr_mandatory_reasons(row), "row": row})
    return pool


def _mr_valid_score(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value))


def mr_rerank(candidates, scores=None, fallback_reason=None, top_k=MR_TOP_K):
    """確定性重排。同輸入 → 同輸出;tie-break = (分數高 → 原排名前 → id 字典序)。

    - scores=None(雙閘門沒開／打分失敗/沒給分數)→ fallback:**照原本的順序**回前 top_k 筆;
      只有當必留項排在第 top_k 名之後時,才擠掉排最後的非必留項,輸出仍按原排名排。
    - scores={id: 數字}:必留項不參與打分,依原排名釘在最前面;其餘依分數排。
      非必留項缺分數、或分數不是有限數字 → 整批 fallback(`scores_invalid:…`),不 crash、不部分採用。
    - 必留 > top_k:輸出前 top_k 筆必留(依原排名),其餘列在 mandatory_dropped,status=mandatory_overflow。
    """
    pool = mr_pool(candidates)
    mandatory = [c for c in pool if c["mandatory_reasons"]]
    others = [c for c in pool if not c["mandatory_reasons"]]
    mode = "scored"
    reason = None
    if scores is None:
        mode, reason = "fallback", fallback_reason or "no_scores"
    elif not isinstance(scores, dict):
        mode, reason = "fallback", "scores_invalid:not_a_dict"
    else:
        missing = [c["id"] for c in others if c["id"] not in scores]
        bad = [c["id"] for c in others if c["id"] in scores and not _mr_valid_score(scores[c["id"]])]
        if missing:
            mode, reason = "fallback", "scores_invalid:missing=%s" % ",".join(missing[:5])
        elif bad:
            mode, reason = "fallback", "scores_invalid:non_numeric=%s" % ",".join(bad[:5])
    kept = mandatory[:top_k]
    dropped = mandatory[top_k:]
    room = top_k - len(kept)
    if mode == "scored":
        ranked = sorted(others, key=lambda c: (-float(scores[c["id"]]), c["orig_rank"], c["id"]))
        top = kept + ranked[:room]
    else:
        top = sorted(kept + others[:room], key=lambda c: c["orig_rank"])
    return {
        "mode": mode, "fallback_reason": reason,
        "status": "mandatory_overflow" if dropped else "ok",
        "top": [c["id"] for c in top],
        "results": [c["row"] for c in top],
        "original_top": [c["id"] for c in pool[:top_k]],
        "pool_size": len(pool), "top_k": top_k,
        "scores_used": ({c["id"]: float(scores[c["id"]]) for c in others} if mode == "scored" else None),
        "mandatory": {"in_pool": [c["id"] for c in mandatory], "kept": [c["id"] for c in kept],
                      "dropped": [c["id"] for c in dropped],
                      "reasons": {c["id"]: c["mandatory_reasons"] for c in mandatory}},
        "mr_policy": "mr+%s" % mr_fingerprint(),
    }


def mr_query_metrics(ranked_ids, relevant, k=MR_TOP_K):
    """單一查詢:recall@k = |relevant ∩ 前 k| ÷ |relevant|;rr = 1 ÷ 前 k 內第一筆 relevant 的名次(沒有 → 0)。"""
    rel = set(relevant)
    if not rel:
        raise JevError("relevant 不得為空(沒有標準答案的查詢不能算 recall/MRR)")
    top = list(ranked_ids)[:k]
    hits = len(rel.intersection(top))
    rr = 0.0
    for rank, cid in enumerate(top, 1):
        if cid in rel:
            rr = 1.0 / rank
            break
    return {"recall": hits / len(rel), "rr": rr}


def _mr_validate_query(q, index):
    if not isinstance(q, dict):
        raise JevError("queries[%d] 必須是物件" % index)
    for key in ("id", "candidates", "relevant"):
        if key not in q:
            raise JevError("queries[%d] 缺欄 %s" % (index, key))
    if not isinstance(q["id"], str) or not q["id"].strip():
        raise JevError("queries[%d].id 必須是非空字串" % index)
    rel = q["relevant"]
    if not isinstance(rel, list) or not rel or not all(isinstance(r, str) and r for r in rel):
        raise JevError("queries[%d](%s).relevant 必須是非空字串 list" % (index, q["id"]))
    if len(set(rel)) != len(rel):
        raise JevError("queries[%d](%s).relevant 有重複" % (index, q["id"]))
    if "scores" in q and q["scores"] is not None and not isinstance(q["scores"], dict):
        raise JevError("queries[%d](%s).scores 必須是 {id: 數字} 或省略" % (index, q["id"]))


def _mr_mean(values):
    return sum(values) / len(values) if values else 0.0


def mr_eval(fixture, min_queries=None):
    """離線評測:同一組有標準答案的查詢,比「原本順序的前 5 筆」vs「MR 的前 5 筆」。

    通過 = 三條同時成立(C5):Recall@5 差值 ≥ 0、MRR 差值 ≥ +0.05、必留保留率 = 100%。
    查詢數 < min_queries → verdict=insufficient_data(數字照列,不當通過);整組沒有任何必留項 →
    保留率無從證明,同樣 insufficient_data。回 report dict;fixture 形狀不對 → JevError。"""
    min_queries = mr_min_queries(min_queries)
    if not isinstance(fixture, dict) or fixture.get("schema") != MR_EVAL_SCHEMA:
        raise JevError("fixture schema 必須是 %s" % MR_EVAL_SCHEMA)
    source = fixture.get("score_source")
    if source not in MR_SCORE_SOURCES:
        raise JevError("fixture score_source 必須是 %s" % "|".join(MR_SCORE_SOURCES))
    queries = fixture.get("queries")
    if not isinstance(queries, list):
        raise JevError("fixture queries 必須是 list")
    ids = set()
    rows = []
    base_recall, base_rr, mr_recall, mr_rr = [], [], [], []
    mand_total = mand_kept = base_mand_kept = 0
    for index, q in enumerate(queries):
        _mr_validate_query(q, index)
        if q["id"] in ids:
            raise JevError("query id 重複:%s" % q["id"])
        ids.add(q["id"])
        out = mr_rerank(q["candidates"], scores=q.get("scores"))
        pool_ids = [c["id"] for c in mr_pool(q["candidates"])]
        base_top = pool_ids[:MR_TOP_K]
        b = mr_query_metrics(base_top, q["relevant"])
        m = mr_query_metrics(out["top"], q["relevant"])
        in_pool = out["mandatory"]["in_pool"]
        mand_total += len(in_pool)
        mand_kept += len([c for c in in_pool if c in out["top"]])
        base_mand_kept += len([c for c in in_pool if c in base_top])
        base_recall.append(b["recall"])
        base_rr.append(b["rr"])
        mr_recall.append(m["recall"])
        mr_rr.append(m["rr"])
        rows.append({"id": q["id"], "baseline_top": base_top, "mr_top": out["top"], "mr_mode": out["mode"],
                     "mr_fallback_reason": out["fallback_reason"], "mr_status": out["status"],
                     "relevant": list(q["relevant"]),
                     "relevant_outside_pool": sorted(set(q["relevant"]) - set(pool_ids)),
                     "baseline_recall_at_5": round(b["recall"], 6), "mr_recall_at_5": round(m["recall"], 6),
                     "baseline_rr": round(b["rr"], 6), "mr_rr": round(m["rr"], 6),
                     "mandatory_in_pool": in_pool, "mandatory_dropped": out["mandatory"]["dropped"]})
    n = len(rows)
    b_recall, m_recall = _mr_mean(base_recall), _mr_mean(mr_recall)
    b_mrr, m_mrr = _mr_mean(base_rr), _mr_mean(mr_rr)
    recall_delta, mrr_delta = m_recall - b_recall, m_mrr - b_mrr
    retention = (mand_kept / mand_total) if mand_total else None
    conditions = [
        {"name": "recall_at_5_not_lower", "actual": round(recall_delta, 6), "threshold": ">= %s" % MR_RECALL_DELTA_MIN,
         "pass": n > 0 and recall_delta + MR_EPS >= MR_RECALL_DELTA_MIN},
        {"name": "mrr_gain_at_least_0.05", "actual": round(mrr_delta, 6), "threshold": ">= %s" % MR_MRR_DELTA_MIN,
         "pass": n > 0 and mrr_delta + MR_EPS >= MR_MRR_DELTA_MIN},
        {"name": "mandatory_retention_100pct", "actual": None if retention is None else round(retention, 6),
         "threshold": "== %s" % MR_MANDATORY_RETENTION_MIN,
         "pass": retention is not None and retention + MR_EPS >= MR_MANDATORY_RETENTION_MIN},
    ]
    insufficient = []
    if n < min_queries:
        insufficient.append("queries=%d < min_queries=%d:資料不足,不能當成通過" % (n, min_queries))
    if not mand_total:
        insufficient.append("整組沒有任何必留項在候選池裡:必留 100%% 保留無從證明")
    if insufficient:
        verdict = "insufficient_data"
    else:
        verdict = "pass" if all(c["pass"] for c in conditions) else "fail"
    return {
        "schema": "devflow-jev-mr-eval-report/1", "gate": "MR", "fixture": fixture.get("name"),
        "score_source": source, "queries": n, "min_queries": min_queries,
        "min_queries_calibrated": False,
        "pool_size": MR_POOL_SIZE, "top_k": MR_TOP_K,
        "baseline": {"recall_at_5": round(b_recall, 6), "mrr": round(b_mrr, 6),
                     "mandatory_retention": None if not mand_total else round(base_mand_kept / mand_total, 6)},
        "mr": {"recall_at_5": round(m_recall, 6), "mrr": round(m_mrr, 6),
               "mandatory_retention": None if retention is None else round(retention, 6)},
        "delta": {"recall_at_5": round(recall_delta, 6), "mrr": round(mrr_delta, 6)},
        "mandatory": {"in_pool": mand_total, "kept": mand_kept},
        "conditions": conditions, "verdict": verdict, "insufficient": insufficient,
        "per_query": rows, "mr_policy": "mr+%s" % mr_fingerprint(),
        "live_eligible": False,
        "note": ("fixture 分數來源 %s;通過 ≠ MR 可以 live(C5 要在 dev-memory.py eval 的 locked set 上成立,"
                 "MR gate 只到 shadow(gate.MR_LIVE_RATIFIED=False);min_queries 是未校準暫定值)" % source),
    }
