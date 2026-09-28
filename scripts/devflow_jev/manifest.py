"""G5 — Question / evaluation manifest 治理。

- `jev-questions.json` 是題組正本;本模組驗其形狀(不驗題目寫得好不好)。
- `questionset_hash` 不是 questions 的 hash,是**完整 evaluation manifest** 的 hash:
  questions + rubric_schema_version + packet_builder_version + policy_version +
  route_formula_version + normalization_version(roadmap §3.4)。任一欄改變 → 新 hash。
- Score criteria 可以是 object `{level,label,description}`,但 API 的 score index 由**陣列位置**
  決定,`level` 不控制 index:`level != index` 一律拒絕,**不排序**(排序會改變 rubric 語義與 hash)。
- group key 固定三欄 `(gate, questionset_hash, model_resolved)`,不加第四欄。
"""
import hashlib
import json
import os

from . import (GATES, JevError, NORMALIZATION_VERSION, PACKET_BUILDER_VERSION,
               POLICY_VERSION, ROUTE_FORMULA_VERSION, RUBRIC_SCHEMA_VERSION)

QUESTION_TYPES = ("noul", "choice", "score")
SCORE_MIN, SCORE_MAX = 2, 10
DEFAULT_QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "jev-questions.json")
_ID_OK = set("abcdefghijklmnopqrstuvwxyz0123456789_")


def canonical_json(obj):
    """去重比對 / hash 用的正規形式:同內容一定同字串。"""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


QID_MAX = 64


def _is_ident(value):
    """question id:小寫識別字、≤64 字(durable ledger 的鍵名上限同一條規則,G5 收的 G4 一定寫得進)。"""
    return (isinstance(value, str) and 0 < len(value) <= QID_MAX and set(value) <= _ID_OK
            and not value[0].isdigit())


def validate_score_criteria(entries, where="score"):
    """回傳 problems(list[str])。object entry 必須 level == index;不一致直接拒絕、不排序。"""
    problems = []
    if not isinstance(entries, list):
        return ["%s: criteria 必須是有序陣列" % where]
    if not SCORE_MIN <= len(entries) <= SCORE_MAX:
        problems.append("%s: criteria 長度 %d 不在 %d–%d" % (where, len(entries), SCORE_MIN, SCORE_MAX))
    for index, entry in enumerate(entries):
        if isinstance(entry, str):
            if not entry.strip():
                problems.append("%s[%d]: 空字串" % (where, index))
            continue
        if not isinstance(entry, dict):
            problems.append("%s[%d]: 只能是字串或 {level,label,description} 物件" % (where, index))
            continue
        level = entry.get("level")
        if not isinstance(level, int) or isinstance(level, bool):
            problems.append("%s[%d]: level 必須是整數" % (where, index))
        elif level != index:
            problems.append("%s[%d]: level=%d != index=%d —— API score index 由陣列位置決定,"
                            "拒絕,不自動排序" % (where, index, level, index))
        if not isinstance(entry.get("label"), str) or not entry["label"].strip():
            problems.append("%s[%d]: label 必填" % (where, index))
        if not isinstance(entry.get("description"), str) or not entry["description"].strip():
            problems.append("%s[%d]: description 必填(可驗證的句子,不是「好／不好」)" % (where, index))
    return problems


def score_criteria_for_api(entries):
    """把 object entries 轉成 API 用的有序字串陣列(位置 = index)。不合法先拒。"""
    problems = validate_score_criteria(entries)
    if problems:
        raise JevError("; ".join(problems))
    out = []
    for entry in entries:
        if isinstance(entry, str):
            out.append(entry)
        else:
            out.append("%s: %s" % (entry["label"], entry["description"]))
    return out


def validate_questions(questions):
    """驗 questions 形狀:{gate: {question_id: {type, text, criteria?}}}。回傳 problems。"""
    problems = []
    if not isinstance(questions, dict) or not questions:
        return ["questions 必須是非空物件 {gate: {...}}"]
    for gate, qset in questions.items():
        if gate not in GATES:
            problems.append("未知 gate %r(只有 %s)" % (gate, "/".join(GATES)))
            continue
        if not isinstance(qset, dict) or not qset:
            problems.append("%s: 題組必須是非空物件" % gate)
            continue
        for qid, q in qset.items():
            where = "%s.%s" % (gate, qid)
            if not _is_ident(qid):
                problems.append("%s: question id 只能是小寫識別字" % where)
            if not isinstance(q, dict):
                problems.append("%s: 題目必須是物件" % where)
                continue
            qtype = q.get("type")
            if qtype not in QUESTION_TYPES:
                problems.append("%s: type %r 不在 %s" % (where, qtype, "/".join(QUESTION_TYPES)))
                continue
            if not isinstance(q.get("text"), str) or not q["text"].strip():
                problems.append("%s: text 必填" % where)
            extra = set(q) - {"type", "text", "criteria", "note"}
            if extra:
                problems.append("%s: 多餘欄位 %s" % (where, sorted(extra)))
            if qtype == "noul":
                if "criteria" in q:
                    problems.append("%s: noul 不得帶 criteria" % where)
            elif qtype == "choice":
                crit = q.get("criteria")
                if not isinstance(crit, dict) or len(crit) < 2:
                    problems.append("%s: choice criteria 必須是 ≥2 個選項的 {選項: 說明}" % where)
                else:
                    for key, desc in crit.items():
                        if not isinstance(key, str) or not key.strip():
                            problems.append("%s: choice 選項名不得為空" % where)
                        if not isinstance(desc, str) or not desc.strip():
                            problems.append("%s: 選項 %r 說明必填" % (where, key))
            elif qtype == "score":
                problems.extend(validate_score_criteria(q.get("criteria"), where))
    return problems


def load_questions(path=None):
    path = path or DEFAULT_QUESTIONS_PATH
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or data.get("schema") != "devflow-jev-questions/1":
        raise JevError("%s: schema 必須是 devflow-jev-questions/1" % path)
    questions = data.get("questions")
    problems = validate_questions(questions)
    if problems:
        raise JevError("%s: %s" % (path, "; ".join(problems)))
    return questions


def effective_versions():
    """六欄中三欄綁機械指紋:`<semver>+<sha256[:12]>`。版本字串不是自由填的標籤 ——
    policy／packet builder 的常數改了,即使沒人 bump semver,questionset_hash 也會變。"""
    from . import packet as _packet, policy as _policy
    fp = _policy.policy_fingerprint()
    return {
        "packet_builder_version": "%s+%s" % (PACKET_BUILDER_VERSION, _packet.builder_fingerprint()),
        "policy_version": "%s+%s" % (POLICY_VERSION, fp),
        "route_formula_version": "%s+%s" % (ROUTE_FORMULA_VERSION, fp),
    }


def build_manifest(questions, rubric_schema_version=RUBRIC_SCHEMA_VERSION,
                   packet_builder_version=None, policy_version=None,
                   route_formula_version=None,
                   normalization_version=NORMALIZATION_VERSION):
    """完整 evaluation manifest(roadmap §3.4 六欄)。未指定的三欄用 effective_versions()(含指紋)。"""
    problems = validate_questions(questions)
    if problems:
        raise JevError("; ".join(problems))
    eff = effective_versions()
    packet_builder_version = packet_builder_version or eff["packet_builder_version"]
    policy_version = policy_version or eff["policy_version"]
    route_formula_version = route_formula_version or eff["route_formula_version"]
    return {
        "questions": questions,
        "rubric_schema_version": rubric_schema_version,
        "packet_builder_version": packet_builder_version,
        "policy_version": policy_version,
        "route_formula_version": route_formula_version,
        "normalization_version": normalization_version,
    }


MANIFEST_KEYS = ("questions", "rubric_schema_version", "packet_builder_version",
                 "policy_version", "route_formula_version", "normalization_version")


def questionset_hash(manifest):
    """hash 完整 manifest;缺任一欄 fail-loud(缺欄的 hash 會和舊 group 撞號)。"""
    missing = [k for k in MANIFEST_KEYS if k not in manifest]
    if missing:
        raise JevError("manifest 缺欄 %s —— questionset_hash 必須涵蓋六欄" % missing)
    return sha256_hex(canonical_json({k: manifest[k] for k in MANIFEST_KEYS}))


def gate_questions_for_api(manifest, gate):
    """把某 gate 的題組轉成 API `questions` 形狀(score criteria 轉有序字串)。"""
    qset = manifest["questions"].get(gate)
    if not qset:
        raise JevError("manifest 沒有 %s 題組" % gate)
    out = {}
    for qid, q in qset.items():
        entry = {"type": q["type"], "text": q["text"]}
        if q["type"] == "choice":
            entry["criteria"] = dict(q["criteria"])
        elif q["type"] == "score":
            entry["criteria"] = score_criteria_for_api(q["criteria"])
        out[qid] = entry
    return out


def group_key(gate, qhash, model_resolved):
    """owner 保留三欄 grouping;不加第四欄。"""
    if gate not in GATES:
        raise JevError("group_key: 未知 gate %r" % gate)
    if not (isinstance(qhash, str) and qhash.startswith("sha256:") and len(qhash) == 71):
        raise JevError("group_key: questionset_hash 形狀不對")
    if not isinstance(model_resolved, str) or not model_resolved:
        raise JevError("group_key: model_resolved 必填(用 response.model,不是 requested)")
    return (gate, qhash, model_resolved)
