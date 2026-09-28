"""G2R 分流 + G2 誤放行(research/jev-supermemory W9/W10 → main G2 上線版)。

規則正本:docs/dev/readme-contract-extract.md §7「G2 轉人條件」(owner 2026-09-27 定案);
ADR docs/adr/0004-g2-spec-auto-review.md。本檔只放**判定函式與常數**,不碰網路、不寫檔、不寫 verdict。

與 research W9/W10 的差別(G2 上線 PR 明改,其餘逐字沿用):
  - 沒有 Jev(沒 key／沒 opt-in／mode 不是 live／失敗／逾時／breaker open／budget 用完)= no-op(ADR 0004 §2):
    不擋、不放寬,`routed_by: none`,其餘轉人條件照判;risk 改看 spec 的 `- Risk:`(high → 2)。
  - ADR §3 全表:另加「當次修改 Jev runtime/questions/config」(declared paths 命中 JEV_RUNTIME_MARKERS)
    與「缺 authored_by」兩條轉人條件。
  - `spec_risk_of`:`- Risk:` 寫了卻是空值 → JevError(W10 當時回 None)。
  - 分流紀錄從 `g2r-shadow` 改名 `g2r`(live);誤放行／agent 放行紀錄綁的就是它。
從 research 搬過來、語意不動:`RISK_PATHS_DEFAULT`、`Budget`/`Breaker`、`evaluate`/`noop`(no-op 語意)、
`J2_WINDOW_RATIFIED=False`。
"""
import hashlib
import json
import re

from . import JevError
from .transport import TransportError, parse_response

# W6 起的 live 開關:本 PR 不翻。J2 永遠 shadow;沒有旗標能改它。
J2_WINDOW_RATIFIED = False
# 機械 risk ceiling 的清單(research policy.py 原值;只能變寬)。
RISK_PATHS_DEFAULT = ("migrations/", "migration/", "auth/", "payment", "payments/", "billing/",
                      "secrets", ".github/workflows/", "ci/", "Dockerfile", "infra/")
# 當次改到 Jev runtime／questions／config → 當次 HUMAN(research provenance.RUNTIME_PATH_MARKERS;
# 本 PR 放寬成不限 scripts/ 前綴,散發副本 docs/dev/tools/devflow_jev/ 也算)。
JEV_RUNTIME_MARKERS = ("devflow_jev/", "devflow-jev.py", "jev-questions", ".dev-flow/jev.yaml")
G2R_DEADLINE_S = 60.0          # 單次 Jev 呼叫的等待上限;逾時 = no-op(沒有 Jev)
G2R_STATE_MAX_CHARS = 60000    # 4-spec 超過就不送(不裁切):jev_status=packet_too_large = 沒有 Jev
DAILY_ATTEMPTS_CAP = 500       # research 工程候選值(不是 owner 裁決);先到者停 = budget 用完 = 沒有 Jev
DAILY_INPUT_TOKENS_CAP = 500000
BREAKER_THRESHOLD = 3          # 連續失敗 ≥3 → breaker open = 沒有 Jev


def canonical_json(obj):
    """hash 用的正規形式:同內容一定同字串。"""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def runtime_changed(changed_paths, markers=JEV_RUNTIME_MARKERS):
    """當次改到 Jev runtime / questions / config 的路徑(ADR §3「當次修改 Jev runtime」)。"""
    return [p for p in changed_paths if any(m in p for m in markers)]


def risk_ceiling_hit(changed_paths, risk_paths=None):
    """機械 risk ceiling:路徑含任一 risk_paths 標記就算命中。清單只有一份(RISK_PATHS_DEFAULT)。"""
    risk_paths = RISK_PATHS_DEFAULT if risk_paths is None else risk_paths
    hits = []
    for path in changed_paths:
        for marker in risk_paths:
            if marker in path:
                hits.append(path)
                break
    return hits


# ───────────────────────────── privacy(送 Jev 前;fail-closed)─────────────────────────────
# research packet.py 的同一組 pattern。命中 → 不送、jev_status=privacy_blocked → HUMAN。
# 字串拼接是為了不讓 check-no-stale-paths 掃到連續字面。
_ABS_UNIX = re.compile(r"(?<![\w./])/(?:" + "Users" + r"|home|root|tmp|var|etc|opt|private)/[^\s\"'`)]+")
_ABS_WIN = re.compile(r"\b[A-Za-z]:\\[^\s\"'`)]+")
_SECRETS = (
    ("api_key_assignment", re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password|passwd|authorization)\b\s*[:=]\s*\S{6,}")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("typesafe_key_env", re.compile(r"TYPESAFE_API_KEY\s*=\s*\S+")),
)
_PHI = (
    ("tw_national_id", re.compile(r"\b[A-Z][12]\d{8}\b")),
    ("medical_record_no", re.compile(r"(?i)\b(?:病歷號|mrn|medical record (?:no|number))\b\s*[:=#]?\s*\w+")),
)


def _flatten_text(obj, acc):
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            _flatten_text(key, acc)
            _flatten_text(value, acc)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            _flatten_text(value, acc)


def privacy_scan(obj):
    """回 violations list[(kind, snippet)];空 = 通過。"""
    texts = []
    _flatten_text(obj, texts)
    blob = "\n".join(texts)
    hits = []
    for pattern in (_ABS_UNIX, _ABS_WIN):
        for match in pattern.finditer(blob):
            hits.append(("absolute_path", match.group(0)[:60]))
    for kind, pattern in _SECRETS + _PHI:
        for match in pattern.finditer(blob):
            hits.append((kind, match.group(0)[:40]))
    return hits


# ───────────────────────────── budget / breaker / 一次 Jev 呼叫(research 原樣)─────────────────────────────
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
    """per key 連續失敗 ≥ threshold → open;成功歸零。"""

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


def evaluate(transport, request, questions, clock, deadline_s=G2R_DEADLINE_S, est_input_tokens=None,
             budget=None, breaker=None, breaker_key="G2R"):
    """一次 attempt。breaker open／budget 用完／傳輸／逾時／回應格式錯誤 → no-op(對 G2R = 沒有 Jev),絕不 retry。"""
    if breaker is not None and breaker.is_open(breaker_key):
        return noop("breaker_open")
    rid = None
    if budget is not None:
        if not isinstance(est_input_tokens, int) or isinstance(est_input_tokens, bool) or est_input_tokens <= 0:
            raise JevError("evaluate: 有 budget 時 est_input_tokens 必須是正整數上界")
        rid = budget.reserve(est_input_tokens)
        if rid is None:
            return noop("budget_exhausted")

    def fail(reason):
        if breaker is not None:
            breaker.record(breaker_key, False)
        return noop(reason)

    started = clock()
    try:
        raw = transport.send(request)
    except TransportError as exc:
        return fail("transport:" + exc.kind)
    except Exception as exc:  # 任何未預期例外同樣 no-op,不得讓 Jev 例外變成放行
        return fail("unexpected:" + type(exc).__name__)
    elapsed = clock() - started
    if elapsed > deadline_s:
        return fail("deadline_exceeded(%.3fs>%.3fs)" % (elapsed, deadline_s))
    try:
        parsed = parse_response(raw, questions)
    except TransportError as exc:
        return fail("transport:" + exc.kind)
    if budget is not None and rid is not None:
        budget.reconcile(rid, parsed["usage"])       # unknown → 保留上界不退款
    if breaker is not None:
        breaker.record(breaker_key, True)
    return {"status": "ok", "reason": "", "answers": parsed["answers"],
            "model": parsed["model"], "usage": parsed["usage"], "elapsed_s": elapsed}


# ───────────────────────────── G2R 分流(G2 上線)─────────────────────────────
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
