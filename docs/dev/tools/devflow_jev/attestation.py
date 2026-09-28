"""G7 — Verdict provenance tripwire。

G1/G2/G3 文件 frontmatter 可附 `verdict_source:` 與 `attested_by:`:
  verdict_source: human_attested | fresh_agent_reviewer | owner_self_review
  attested_by: human:<name> | agent:<model-or-role>
這是 **provenance tripwire,不是 authentication**:`human:<name>` 或換 session 都不能證明真實身份;
它只讓「沒宣告來源就想拿去當 label」機械上不可能。
- 缺 verdict → label "none"(還沒判)。
- 有 verdict 但無 / 非法 verdict_source → "unverified"(P1-G7 前的舊 label 一律如此),不進 graduation。
- report 必須分層顯示 human_attested 與 fresh_agent_reviewer,不得混成同一主率(哪層當 primary 待 formal spec)。
模板本身**不在 W1 改**(那是 P3-2 契約同步);本模組只讀。
"""
import re

VERDICT_VALUES = ("PASS", "REQUEST_CHANGES", "HOLD")
SOURCES = ("human_attested", "fresh_agent_reviewer", "owner_self_review")
GRADUATION_ELIGIBLE = ("human_attested", "fresh_agent_reviewer")
_ATTESTED_BY = re.compile(r"^(human|agent):(\S+)$")


def parse_frontmatter(text):
    """簡單 `key: value` frontmatter;無 frontmatter 回 {}。值去掉行尾註解。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, _, value = line.partition(":")
        value = value.split("#", 1)[0].strip()
        out[key.strip()] = value
    return out


def classify(frontmatter):
    """回 {"label","verdict","source","attested_by","notes"}。label ∈ none|unverified|<SOURCES>。"""
    verdict = (frontmatter.get("verdict") or "").strip()
    notes = []
    if verdict not in VERDICT_VALUES:
        return {"label": "none", "verdict": verdict or None, "source": None, "attested_by": None,
                "notes": ["no human verdict yet" if not verdict else "verdict %r not in %s" % (verdict, VERDICT_VALUES)]}
    source = (frontmatter.get("verdict_source") or "").strip()
    attested = (frontmatter.get("attested_by") or "").strip()
    if source not in SOURCES:
        notes.append("verdict_source missing/illegal → unverified (pre-G7 label)")
        return {"label": "unverified", "verdict": verdict, "source": source or None,
                "attested_by": attested or None, "notes": notes}
    m = _ATTESTED_BY.match(attested)
    if not m:
        notes.append("attested_by missing/illegal (format tripwire) → unverified")
        return {"label": "unverified", "verdict": verdict, "source": source,
                "attested_by": attested or None, "notes": notes}
    kind = m.group(1)
    if source == "human_attested" and kind != "human":
        notes.append("human_attested but attested_by is agent → unverified")
        return {"label": "unverified", "verdict": verdict, "source": source, "attested_by": attested, "notes": notes}
    if source == "fresh_agent_reviewer" and kind != "agent":
        notes.append("fresh_agent_reviewer but attested_by is not agent → unverified")
        return {"label": "unverified", "verdict": verdict, "source": source, "attested_by": attested, "notes": notes}
    if source == "owner_self_review":
        notes.append("owner self-review: not graduation-eligible; needs the limitation section per 7-review 步 0")
    notes.append("format attestation only; not authentication")
    return {"label": source, "verdict": verdict, "source": source, "attested_by": attested, "notes": notes}


def classify_document(text):
    return classify(parse_frontmatter(text))


def graduation_eligible(label):
    return label in GRADUATION_ELIGIBLE


def layered_counts(labels):
    """分層計數;刻意沒有 'combined' 鍵 —— 主率哪一層由 formal spec 核定。"""
    counts = {"human_attested": 0, "fresh_agent_reviewer": 0, "owner_self_review": 0, "unverified": 0, "none": 0}
    for label in labels:
        counts[label if label in counts else "unverified"] += 1
    return counts
