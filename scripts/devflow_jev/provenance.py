"""G6 — 防造假 / derived-only。

- `route_recommended` / `route_taken` **只能由 policy 導出**;`verify_evaluation()` 用同一個 policy
  重算,對不上 = tampered。hash 只做完整性,**不假裝 identity / auth**。
- risk_paths 只能變寬;變窄必須留痕(跨 session 可稽核的 change record)且當次一律 HUMAN。
- 修改 Jev runtime / questions / config 的那個 session,route 一律 HUMAN。
- 同 session 的 feedback、時間倒置、reviewer=author、evidence 版本不一致 → suspect,不進 n。
"""
from . import JevError
from .manifest import canonical_json, sha256_hex
from .policy import route_j5, route_taken

RUNTIME_PATH_MARKERS = ("scripts/devflow_jev/", "scripts/devflow-jev.py", "jev-questions.json",
                        ".dev-flow/jev.yaml")
INTEGRITY_FIELDS = ("evaluation_id", "parent_evaluation_id", "case_id", "gate", "slug", "mode",
                    "session_ref", "author_ref", "occurred_at", "variant_id", "questionset_hash",
                    "model_resolved", "packet_hash", "packet_truncated", "packet_consistency_flags",
                    "risk_ceiling_hit", "runtime_changed", "evidence", "answers_summary",
                    "route_recommended", "route_reason", "route_taken", "route_taken_reason", "status")


def integrity_hash(evaluation):
    """完整性 hash(不是簽章):任一受保護欄位改動即對不上。"""
    payload = {k: evaluation.get(k) for k in INTEGRITY_FIELDS}
    return sha256_hex(canonical_json(payload))


def stamp(evaluation):
    evaluation["integrity_hash"] = integrity_hash(evaluation)
    return evaluation


def risk_ceiling_hit(changed_paths, risk_paths=None):
    """機械 risk ceiling(P2-4 的判準函式;G6 監控它的清單)。清單只有一份:policy.RISK_PATHS_DEFAULT
    (進 policy 指紋);呼叫時才讀,不在 def 時綁複本。"""
    from . import policy as _policy
    risk_paths = _policy.RISK_PATHS_DEFAULT if risk_paths is None else risk_paths
    hits = []
    for path in changed_paths:
        for marker in risk_paths:
            if marker in path:
                hits.append(path)
                break
    return hits


def verify_evaluation(evaluation, level, graduated=False, packet_flags=None, truncated=None,
                      risk_ceiling=None, runtime_changed=None):
    """回 problems(list[str]);空 = 一致。

    重算的輸入**預設取自 evaluation 自己記錄的機械欄位**(packet_consistency_flags / packet_truncated /
    risk_ceiling_hit / runtime_changed):這些欄位在 INTEGRITY_FIELDS 內,改了就 hash 對不上;
    呼叫端可以傳更嚴的值覆蓋,不能靠「不傳」讓旗標消失。
    """
    problems = []
    if evaluation.get("integrity_hash") != integrity_hash(evaluation):
        problems.append("integrity_hash_mismatch(欄位被改或 hash 偽造)")
    flags = evaluation.get("packet_consistency_flags") or []
    if packet_flags:
        flags = sorted(set(flags) | set(packet_flags))
    # 三個布林同樣只能加嚴:記錄為 True 的,呼叫端傳 False 也不會放鬆
    trunc = bool(evaluation.get("packet_truncated")) or bool(truncated)
    ceiling = bool(evaluation.get("risk_ceiling_hit")) or bool(risk_ceiling)
    rt_changed = bool(evaluation.get("runtime_changed")) or bool(runtime_changed)
    if evaluation["gate"] == "J5":
        answers = _expand_summary(evaluation["answers_summary"])
        recomputed = route_j5(answers, packet_flags=flags, truncated=trunc,
                              risk_ceiling_hit=ceiling, runtime_changed=rt_changed)
        if evaluation["status"] == "ok" and recomputed["route_recommended"] != evaluation["route_recommended"]:
            problems.append("route_recommended_tampered(記錄 %s,重算 %s)"
                            % (evaluation["route_recommended"], recomputed["route_recommended"]))
        if evaluation["status"] == "ok" and recomputed["route_reason"] != evaluation.get("route_reason"):
            problems.append("route_reason_tampered(記錄 %s,重算 %s)"
                            % (evaluation.get("route_reason"), recomputed["route_reason"]))
        taken, _ = route_taken("J5", level, recomputed["route_recommended"], graduated=graduated)
        if evaluation["status"] == "ok" and taken != evaluation["route_taken"]:
            problems.append("route_taken_invalid(記錄 %s,依 level=%s graduated=%s 應為 %s)"
                            % (evaluation["route_taken"], level, graduated, taken))
    if evaluation.get("status") == "noop" and evaluation.get("route_taken") not in (None, "HUMAN"):
        problems.append("noop 卻記了非 HUMAN 的 route_taken")
    return problems


def _expand_summary(summary):
    """把 answers_summary 還原成 route 函式吃的形狀(只還原 route 需要的欄位)。"""
    answers = {}
    for qid, val in summary.items():
        if "noul" in val:
            answers[qid] = {"noul": val["noul"]}
        elif "choice" in val:
            probs = dict(val.get("probabilities") or {})
            probs[val["choice"]] = val["probability"]          # 被選項的機率以 probability 欄為準(兩欄不一致 = 有人改過)
            answers[qid] = {"choice": val["choice"], "probabilities": probs}
        elif "score" in val:
            answers[qid] = {"score": val["score"]}
    return answers


def risk_paths_change(previous, current):
    prev, cur = set(previous), set(current)
    return {"narrowed": sorted(prev - cur), "widened": sorted(cur - prev)}


def risk_paths_change_record(previous, current, session_ref, approved_by=None):
    """縮窄留痕:回 change record(要進 durable);未經人核的縮窄 → force_human=True。"""
    diff = risk_paths_change(previous, current)
    narrowed = bool(diff["narrowed"])
    return {
        "kind": "jev_risk_paths_change",
        "session_ref": session_ref,
        "narrowed": diff["narrowed"], "widened": diff["widened"],
        "approved_by": approved_by,
        "force_human": narrowed and not approved_by,
        "prev_hash": sha256_hex(canonical_json(sorted(previous))),
        "cur_hash": sha256_hex(canonical_json(sorted(current))),
    }


def runtime_changed(changed_paths, markers=RUNTIME_PATH_MARKERS):
    """本 session 改到 Jev runtime / questions / config → 當次一律 HUMAN。"""
    return [p for p in changed_paths if any(m in p for m in markers)]


def feedback_suspect(evaluation, feedback):
    """回 reasons;空 = 不可疑。可疑的 feedback 不得進 graduation n。"""
    reasons = []
    for key in ("reviewer_ref", "session_ref", "feedback_at"):
        if not feedback.get(key):
            reasons.append(key + "_missing")          # fail-closed:缺 provenance 欄位不得進 n
    for key in ("author_ref", "session_ref", "occurred_at"):
        if not evaluation.get(key):
            reasons.append("evaluation_%s_missing" % key)       # evaluation 側也 fail-closed,否則同 session／時序檢查是空話
    if feedback.get("session_ref") and feedback["session_ref"] == evaluation.get("session_ref"):
        reasons.append("same_session_as_evaluation")
    if feedback.get("feedback_at") and evaluation.get("occurred_at") \
            and feedback["feedback_at"] < evaluation["occurred_at"]:
        reasons.append("feedback_before_evaluation")
    if feedback.get("reviewer_ref") and feedback["reviewer_ref"] == evaluation.get("author_ref"):
        reasons.append("reviewer_equals_author")
    ev = evaluation.get("evidence", {})
    for key in ("artifact_hash", "evidence_hash", "head_sha"):
        if feedback.get(key) != ev.get(key):
            reasons.append("evidence_version_mismatch:" + key)
    if feedback.get("verdict") not in ("agree", "overturn"):
        reasons.append("verdict_not_agree_or_overturn(none != agree)")
    return reasons


def assert_not_hand_edited(evaluation):
    problems = []
    if evaluation.get("integrity_hash") != integrity_hash(evaluation):
        problems.append("integrity_hash_mismatch")
    if problems:
        raise JevError("; ".join(problems))
    return True
