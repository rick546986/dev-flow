"""最小 report helper(P2-2 之前;G6/G7 驗收需要能「重算」與「分層」)。

- Wilson 95% lower bound;graduation floor:lower ≥ 0.85 且 n ≥ 30(owner 已裁);第一次有效 overturn → freeze。
- n 只數 unique case_id、label 為 graduation-eligible、same-evidence 綁定、feedback 不可疑者。
- `.85/30` 是工程接受門檻,不得翻譯成「95% 準確」。
"""
import math

from .attestation import graduation_eligible
from .provenance import feedback_suspect, verify_evaluation

WILSON_FLOOR = 0.85
N_FLOOR = 30


def wilson_lower(successes, n, z=1.959964):
    if n <= 0:
        return 0.0
    p = successes / float(n)
    denom = 1.0 + z * z / n
    centre = p + z * z / (2.0 * n)
    margin = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return max(0.0, (centre - margin) / denom)


def graduation(evaluations, feedbacks, level="shadow", primary_source=None):
    """evaluations: list[evaluation];feedbacks: {evaluation_id: feedback}。

    - 每層(human_attested / fresh_agent_reviewer)各自算 n / agree / overturn / Wilson / floor / frozen;
      **沒有合併主率**。`primary_source=None`(預設)→ 頂層 `floor_met=None`、`frozen=None`:哪一層當 primary
      待 formal spec 核定,不在這裡偷決定。指定 primary_source 才把那一層抬成頂層數字。
    - 同 case_id 的多筆 feedback 先分組:任一 overturn → 該 case 記 overturn(fail-closed,不看列表順序)。
    """
    if primary_source is not None and not graduation_eligible(primary_source):
        raise ValueError("primary_source 必須是 graduation-eligible 的層")
    excluded = []
    per_case = {}      # case_id -> {"source": str, "verdicts": set, "ids": [...]}
    for ev in evaluations:
        fb = feedbacks.get(ev["evaluation_id"])
        if fb is None:
            excluded.append((ev["evaluation_id"], "no_feedback"))
            continue
        if verify_evaluation(ev, ev.get("mode") or level):     # 用該筆記錄的 mode 重算,不是報表級單一 level
            excluded.append((ev["evaluation_id"], "evaluation_inconsistent"))
            continue
        if not graduation_eligible(fb.get("source")):
            excluded.append((ev["evaluation_id"], "label_%s" % (fb.get("source") or "unverified")))
            continue
        suspect = feedback_suspect(ev, fb)
        if suspect:
            excluded.append((ev["evaluation_id"], "suspect:" + ",".join(suspect)))
            continue
        bucket = per_case.setdefault(ev["case_id"], {"sources": set(), "verdicts": set(), "ids": []})
        if bucket["ids"]:
            excluded.append((ev["evaluation_id"], "duplicate_case"))
        bucket["ids"].append(ev["evaluation_id"])
        bucket["sources"].add(fb["source"])
        bucket["verdicts"].add(fb["verdict"])
    layers = {}
    for source in ("human_attested", "fresh_agent_reviewer"):
        layers[source] = {"n": 0, "n_agree": 0, "n_overturn": 0}
    conflicting = []
    for cid, bucket in per_case.items():
        overturn = "overturn" in bucket["verdicts"]        # 任一 overturn 即 overturn,不由順序決定
        if len(bucket["verdicts"]) > 1:
            conflicting.append(cid)
        # 一個 case 可能被兩層各看過一次;各層自己數,不合併
        for source in bucket["sources"]:
            layers[source]["n"] += 1
            if overturn:
                layers[source]["n_overturn"] += 1
            else:
                layers[source]["n_agree"] += 1
    for source, row in layers.items():
        row["wilson_lower_95"] = round(wilson_lower(row["n_agree"], row["n"]), 4)
        row["floor_met"] = row["n"] >= N_FLOOR and row["wilson_lower_95"] >= WILSON_FLOOR
        row["frozen"] = row["n_overturn"] > 0
    primary = layers[primary_source] if primary_source else None
    return {
        "n_unique_valid": len(per_case),
        "layers": layers,                                   # 分層;沒有 combined 主率
        "primary_source": primary_source,
        "floor_met": primary["floor_met"] if primary else None,
        "frozen": primary["frozen"] if primary else None,
        "wilson_lower_95": primary["wilson_lower_95"] if primary else None,
        "conflicting_label_cases": sorted(conflicting),
        "excluded": excluded,
        "note": "engineering acceptance threshold; not a proof of accuracy; primary layer pending formal spec",
    }


# ───────────────────────────── W5 P2-2 eval metrics(計算器;真實 report 路徑由 runtime 餵資料)─────────────────────────────
# mechanical override(truncated／header-body conflict／risk ceiling／runtime changed)與純 model route **分開**:
# override 的 evaluation 不進 graduation denominator(roadmap §5.1 第 7 條),另列計數。
MECHANICAL_OVERRIDE_PREFIXES = ("runtime_modified_this_session", "risk_ceiling_override", "packet_truncated",
                                "header_body_conflict")


def route_class(evaluation):
    if evaluation.get("status") != "ok":
        return "noop"
    reason = evaluation.get("route_reason") or ""
    if reason.startswith(MECHANICAL_OVERRIDE_PREFIXES):
        return "mechanical_override"
    return "model_route"


def _chosen_probability(evaluation):
    summary = evaluation.get("answers_summary") or {}
    g3 = summary.get("g3_route") or {}
    return g3.get("probability")


def brier(pairs):
    """pairs: [(p, y)];y ∈ {0,1}。空 → None(不填 0 冒充)。"""
    pairs = [(p, y) for p, y in pairs if isinstance(p, (int, float))]
    if not pairs:
        return None
    return sum((float(p) - float(y)) ** 2 for p, y in pairs) / len(pairs)


def question_metrics(evaluations):
    """逐題結構化指標(只用 answers_summary,沒有 raw):noul 平均、score 直方、choice 分布。"""
    acc = {}
    for ev in evaluations:
        if ev.get("status") != "ok":
            continue
        for qid, val in (ev.get("answers_summary") or {}).items():
            slot = acc.setdefault(qid, {"n": 0, "noul_sum": 0.0, "scores": {}, "choices": {}})
            slot["n"] += 1
            if "noul" in val:
                slot["noul_sum"] += float(val["noul"])
            elif "score" in val:
                slot["scores"][str(val["score"])] = slot["scores"].get(str(val["score"]), 0) + 1
            elif "choice" in val:
                slot["choices"][val["choice"]] = slot["choices"].get(val["choice"], 0) + 1
    out = {}
    for qid, slot in acc.items():
        row = {"n": slot["n"]}
        if slot["noul_sum"] or any("noul" in (ev.get("answers_summary") or {}).get(qid, {}) for ev in evaluations):
            row["noul_mean"] = round(slot["noul_sum"] / slot["n"], 4) if slot["n"] else None
        if slot["scores"]:
            row["score_histogram"] = slot["scores"]
        if slot["choices"]:
            row["choice_distribution"] = slot["choices"]
        out[qid] = row
    return out


def eval_metrics(evaluations, feedbacks_by_layer, breaker_failures=None):
    """P2-2 報表:unique cases、分層 n/agree/overturn/Wilson/floor/frozen、labeled_fraction、truncation_rate、
    Brier(以被選 route 的機率對 agree=1/overturn=0)、逐題 metrics、route_reason 分層、breaker/freeze 狀態。
    evaluations 應是**真實 replay store** 的 evaluation;合成 ledger 只拿來驗計算器。"""
    total = len(evaluations)
    classes = {"model_route": [], "mechanical_override": [], "noop": []}
    for ev in evaluations:
        classes[route_class(ev)].append(ev)
    truncated = sum(1 for ev in evaluations if ev.get("packet_truncated"))
    unique_all = len({ev["case_id"] for ev in evaluations})
    unique_model = len({ev["case_id"] for ev in classes["model_route"]})
    unique_override = len({ev["case_id"] for ev in classes["mechanical_override"]})
    reason_counts = {}
    for ev in evaluations:
        key = (ev.get("route_reason") or ("noop:" + str(ev.get("noop_reason")))).split("(")[0]
        reason_counts[key] = reason_counts.get(key, 0) + 1
    layers = {}
    any_frozen = False
    for source in ("human_attested", "fresh_agent_reviewer"):
        fbs = feedbacks_by_layer.get(source) or {}
        grad = graduation(classes["model_route"], fbs, level="shadow", primary_source=source)
        row = dict(grad["layers"][source])
        row["labeled_fraction"] = round(row["n"] / float(unique_model), 4) if unique_model else None
        pairs = []
        for ev in classes["model_route"]:
            fb = fbs.get(ev["evaluation_id"])
            if not fb or fb.get("verdict") not in ("agree", "overturn"):
                continue
            if feedback_suspect(ev, fb) or not graduation_eligible(fb.get("source")):
                continue
            if ev.get("route_recommended") in ("AUTO", "REQUEST_CHANGES"):
                pairs.append((_chosen_probability(ev), 1 if fb["verdict"] == "agree" else 0))
        row["brier_chosen_route"] = brier(pairs)
        row["brier_n"] = len([p for p in pairs if isinstance(p[0], (int, float))])
        row["excluded"] = grad["excluded"]
        layers[source] = row
        any_frozen = any_frozen or row["frozen"]
    return {
        "evaluations_total": total,
        "unique_cases_all": unique_all,
        "unique_cases_model_route": unique_model,          # graduation denominator 候選(仍要 label 才進 n)
        "unique_cases_mechanical_override": unique_override,
        "route_class_counts": {k: len(v) for k, v in classes.items()},
        "route_reason_counts": reason_counts,
        "truncation_rate": round(truncated / float(total), 4) if total else None,
        "layers": layers,
        "question_metrics": question_metrics(classes["model_route"]),
        "circuit_breaker_state": "frozen" if any_frozen else "closed",
        "transport_breaker_failures": dict(breaker_failures or {}),
        "floors": {"wilson_lower_95": WILSON_FLOOR, "n": N_FLOOR},
        "note": "engineering acceptance threshold; not accuracy; mechanical overrides excluded from denominator; "
                "synthetic/smoke/audit evaluations never enter this store",
    }
