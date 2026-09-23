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
