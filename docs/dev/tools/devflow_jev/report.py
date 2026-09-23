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
