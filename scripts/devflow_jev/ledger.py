"""G4 — 雙層 ledger / replay。

durable(進 Git,經 `memory/agentmem/durable.append_events()`)只存 **ID / hash / 結構化指標**;
完整 sanitized packet、exact questions、raw response 只進 gitignored local replay store。

P0-6 四條硬邊界(w0-source-closure.md §P0-6)在這裡落實:
1. canonical 欄位承載可查資訊:`title` 固定前綴、`body` 一行 `k=v;` 字串、hash 進 `source_ref`;
   `jev{}` 結構化 dict 仍寫(檔面保存),但不當 local 查詢依據。
2. `event_id` 一律 `evt_<ULID>`(與 memory/agentmem/ids 同編碼),evaluation identity 另欄。
3. 每個 writer 自己的 `session_id`(= 自己的 JSONL 檔):`jev-<gate>-<evaluation_id>`。
4. 直接 `append_events` 前先過 `signal.gate(<HIGH kind>, …, extra_texts=[json.dumps(record)])`
   —— 借 `important_discovery` 當 gate 的 kind 參數(record 的 kind 仍是 `jev`)。
replay 兩種(roadmap §3.3):stored-response deterministic replay(零網路)與 remote reevaluation
(新 evaluation_id、保 lineage、不覆蓋、同 case_id 不增 n)。缺檔 → `not_replayable`,不假重建。
"""
import json
import os
import time

from . import JevError, MODEL_PINNED
from .manifest import canonical_json, sha256_hex
from .packet import privacy_scan

_ULID_ENC = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
TITLE_PREFIX = "[jev]"
REPLAY_DIRNAME = os.path.join(".devflow", "jev", "replay")   # .devflow/ 已 gitignored
FORBIDDEN_DURABLE_KEYS = ("packet", "state", "raw_response", "questions", "quoted_context",
                          "primary_request", "source_facts", "answers_raw")
MAX_DURABLE_TEXT = 600            # title/body 上限;body 是 k=v 摘要,reason 另限 80 字
MAX_KEY_TEXT = 64


def new_ulid(prefix):
    ts = int(time.time() * 1000) & ((1 << 48) - 1)
    rand = int.from_bytes(os.urandom(10), "big") >> 1
    n = (ts << 80) | rand
    body = "".join(_ULID_ENC[(n >> (5 * (25 - i))) & 31] for i in range(26))
    return prefix + "_" + body


def case_id(feature, gate, artifact_hash, evidence_hash, head_sha):
    """unique semantic Ship decision 的 id:同 evidence version 的 retry / variants / reevaluation 共用。"""
    for name, value in (("feature", feature), ("gate", gate), ("artifact_hash", artifact_hash),
                        ("evidence_hash", evidence_hash), ("head_sha", head_sha)):
        if not isinstance(value, str) or not value:
            raise JevError("case_id 缺 %s" % name)
    return "case_" + sha256_hex(canonical_json([feature, gate, artifact_hash, evidence_hash, head_sha]))[7:39]


def _kv(body_fields):
    return ";".join("%s=%s" % (k, body_fields[k]) for k in sorted(body_fields))


def build_evaluation(gate, slug, mode, packet, manifest_hash, route, taken, taken_reason,
                     outcome, evidence, author_ref, run_id=None, session_ref=None,
                     parent_evaluation_id=None, evaluation_id=None, occurred_at=None,
                     risk_ceiling_hit=False, runtime_changed=False):
    """組一筆 evaluation(記憶體物件;durable/replay 兩層由它導出)。

    G6 的重算輸入(packet 旗標／truncated／risk ceiling／runtime changed)全部記在這裡並進 integrity hash;
    policy 的 route_reason 與 route_taken 的 reason 分兩欄,不互相覆蓋。`author_ref` 必填(author≠approver 判定要用)。
    """
    if not isinstance(author_ref, str) or not author_ref.strip():
        raise JevError("build_evaluation: author_ref 必填(feedback 的 reviewer≠author 檢查依賴它)")
    eid = evaluation_id or new_ulid("eval")
    cid = case_id(slug, gate, evidence["artifact_hash"], evidence["evidence_hash"], evidence["head_sha"])
    return {
        "evaluation_id": eid,
        "parent_evaluation_id": parent_evaluation_id,
        "case_id": cid,
        "gate": gate, "slug": slug, "mode": mode,
        "run_id": run_id, "session_ref": session_ref, "author_ref": author_ref,
        "questionset_hash": manifest_hash,
        "model_requested": MODEL_PINNED,
        "model_resolved": outcome.get("model"),
        "packet_hash": packet["packet_hash"],
        "packet_truncated": bool(packet["truncated"]),
        "packet_consistency_flags": sorted(packet.get("consistency_flags") or []),
        "risk_ceiling_hit": bool(risk_ceiling_hit),
        "runtime_changed": bool(runtime_changed),
        "variant_id": packet.get("variant_id", "v0"),
        "evidence": dict(evidence),
        "answers_summary": _summarize(outcome.get("answers") or {}),
        "route_recommended": route.get("route_recommended") or route.get("next"),
        "route_reason": route.get("route_reason"),          # policy 的理由,永不被 taken_reason 蓋掉
        "route_taken": taken,
        "route_taken_reason": taken_reason,
        "status": outcome["status"],
        "noop_reason": outcome.get("reason") or None,
        "usage": outcome.get("usage"),
        "n_counted": False,            # graduation n 只在 label 綁定時由 report 決定
        "occurred_at": occurred_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _summarize(answers):
    out = {}
    for qid, ans in answers.items():
        if "noul" in ans:
            out[qid] = {"noul": ans["noul"]}
        elif "choice" in ans:
            # 不四捨五入:G6 用它重算 route,精度必須與 policy 比對時相同(0.8496 不得變 0.85)
            out[qid] = {"choice": ans["choice"], "probability": ans["probabilities"][ans["choice"]],
                        "probabilities": dict(ans["probabilities"])}
        elif "score" in ans:
            out[qid] = {"score": ans["score"]}
    return out


def build_durable_record(evaluation, replay_status):
    """durable event(canonical 欄位 + 保存用 jev{});不含 packet/raw/questions。"""
    ev = evaluation
    fields = {
        "gate": ev["gate"], "eval": ev["evaluation_id"], "case": ev["case_id"],
        "mode": ev["mode"], "qhash": ev["questionset_hash"][7:23],
        "model": ev["model_resolved"] or "-", "packet": (ev["packet_hash"] or "sha256:-")[7:23],
        "artifact": ev["evidence"]["artifact_hash"][7:23], "evidence": ev["evidence"]["evidence_hash"][7:23],
        "head": ev["evidence"]["head_sha"][:12],
        "route_rec": ev["route_recommended"] or "-", "route_taken": ev["route_taken"] or "-",
        "reason": (ev["route_reason"] or "-").replace(";", ",")[:80],
        "taken_reason": (ev.get("route_taken_reason") or "-").replace(";", ",")[:40],
        "flags": (",".join(ev.get("packet_consistency_flags") or []) or "-")[:80],
        "replay": replay_status, "status": ev["status"], "usage": (ev.get("usage") or {}).get("usage_status", "-"),
        "n_counted": str(ev["n_counted"]).lower(),
    }
    record = {
        "event_id": new_ulid("evt"),
        "kind": "jev",
        "title": "%s %s %s %s route=%s/%s" % (TITLE_PREFIX, ev["gate"], ev["mode"], ev["slug"],
                                              fields["route_rec"], fields["route_taken"]),
        "body": _kv(fields),
        "occurred_at": ev["occurred_at"],
        "session_id": "jev-%s-%s" % (ev["gate"], ev["evaluation_id"]),     # 每 writer 自己的檔
        "signal": "high",
        "paths": [],
        "source_type": "jev",
        "source_ref": "%s:%s:%s" % (ev["gate"], ev["slug"], ev["evaluation_id"]),
        "jev": {
            "evaluation_id": ev["evaluation_id"], "parent_evaluation_id": ev["parent_evaluation_id"],
            "case_id": ev["case_id"], "questionset_hash": ev["questionset_hash"],
            "model_requested": ev["model_requested"], "model_resolved": ev["model_resolved"],
            "packet_hash": ev["packet_hash"], "packet_truncated": ev["packet_truncated"],
            "packet_consistency_flags": list(ev.get("packet_consistency_flags") or []),   # 複本
            "risk_ceiling_hit": ev.get("risk_ceiling_hit", False), "runtime_changed": ev.get("runtime_changed", False),
            "variant_id": ev["variant_id"], "evidence": dict(ev["evidence"]),      # 複本:不與 evaluation 共用引用
            "answers_summary": _durable_answers(ev["answers_summary"]), "route_recommended": ev["route_recommended"],
            "route_taken": ev["route_taken"], "route_reason": ev["route_reason"],
            "route_taken_reason": ev.get("route_taken_reason"),
            "session_ref": ev.get("session_ref"), "author_ref": ev.get("author_ref"),
            "occurred_at": ev["occurred_at"], "integrity_hash": ev.get("integrity_hash"),
            "replay_status": replay_status, "run_id": ev["run_id"],
            "usage": dict(ev["usage"]) if isinstance(ev.get("usage"), dict) else ev.get("usage"),   # 複本
            "n_counted": ev["n_counted"],
        },
    }
    assert_durable_safe(record)
    return record


JEV_ALLOWED_KEYS = {
    "evaluation_id", "parent_evaluation_id", "case_id", "questionset_hash", "model_requested", "model_resolved",
    "packet_hash", "packet_truncated", "packet_consistency_flags", "risk_ceiling_hit", "runtime_changed",
    "variant_id", "evidence", "answers_summary", "route_recommended", "route_taken", "route_reason",
    "route_taken_reason", "replay_status", "run_id", "usage", "n_counted", "session_ref", "author_ref",
    "occurred_at", "integrity_hash",
}
EVIDENCE_ALLOWED_KEYS = {"feature", "gate", "artifact_hash", "evidence_hash", "head_sha", "evaluated_at"}
ANSWER_ALLOWED_KEYS = {"noul", "choice", "probability", "score"}   # durable 不放整個分布(P2-7:不外露 probabilities)
USAGE_ALLOWED_KEYS = {"input_tokens", "output_tokens", "usage_status"}
MAX_LEAF_TEXT = 200


def _durable_answers(summary):
    """durable 只放結構化指標:noul / choice+probability(+分布,數字)/ score。"""
    out = {}
    for qid, val in summary.items():
        out[qid] = {k: v for k, v in val.items() if k in ANSWER_ALLOWED_KEYS}
    return out


_QID_RE = __import__("re").compile(r"^[a-z_][a-z0-9_]{0,63}$")   # 與 manifest._is_ident 同一條規則


def _walk_leaves(obj, path, problems):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in FORBIDDEN_DURABLE_KEYS:
                problems.append("durable record 任一層不得含 %s(在 %s)" % (key, path or "<root>"))
            if not isinstance(key, str) or len(key) > MAX_KEY_TEXT:
                problems.append("%s 的鍵長 > %d(鍵也不得塞文字)" % (path or "<root>", MAX_KEY_TEXT))
            _walk_leaves(value, path + "." + str(key), problems)
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            _walk_leaves(value, "%s[%d]" % (path, i), problems)
    elif isinstance(obj, str) and len(obj) > MAX_LEAF_TEXT and path not in (".title", ".body"):
        problems.append("%s 字串 %d 字元 > %d(像是塞了全文)" % (path, len(obj), MAX_LEAF_TEXT))


def assert_durable_safe(record):
    """Git durable 不得含 raw packet / 醫療資料 / log。fail-loud;白名單 + 逐層掃,不是只看頂層鍵名。"""
    problems = []
    _walk_leaves(record, "", problems)
    for key in ("title", "body"):
        if len(record.get(key, "")) > MAX_DURABLE_TEXT:
            problems.append("%s 超過 %d 字元(像是塞了全文)" % (key, MAX_DURABLE_TEXT))
    jev = record.get("jev", {})
    extra = set(jev) - JEV_ALLOWED_KEYS
    if extra:
        problems.append("jev{} 出現白名單外的鍵 %s" % sorted(extra))
    ev_extra = set(jev.get("evidence") or {}) - EVIDENCE_ALLOWED_KEYS
    if ev_extra:
        problems.append("jev.evidence 出現白名單外的鍵 %s" % sorted(ev_extra))
    for qid, val in (jev.get("answers_summary") or {}).items():
        if not isinstance(qid, str) or not _QID_RE.match(qid):
            problems.append("jev.answers_summary 的 qid %r 不是題目識別字" % (qid,))
        if not isinstance(val, dict) or set(val) - ANSWER_ALLOWED_KEYS:
            problems.append("jev.answers_summary.%s 只准 %s" % (qid, sorted(ANSWER_ALLOWED_KEYS)))
    if jev.get("usage") is not None and set(jev["usage"]) - USAGE_ALLOWED_KEYS:
        problems.append("jev.usage 只准 %s" % sorted(USAGE_ALLOWED_KEYS))
    if not record.get("event_id", "").startswith("evt_") or len(record["event_id"]) != 30:
        problems.append("event_id 必須是 evt_<26 字 ULID>(否則 sync 每次重生 id)")
    if not record.get("session_id", "").startswith("jev-"):
        problems.append("session_id 必須是本 writer 專屬(jev-<gate>-<evaluation_id>)")
    if len(json.dumps(record, ensure_ascii=False).encode("utf-8")) > 8000:
        problems.append("durable record 超過 8000 bytes")
    hits = privacy_scan(record)
    if hits:
        problems.append("privacy 命中 %s" % hits[:3])
    if problems:
        raise JevError("; ".join(problems))
    return True


class ReplayStore(object):
    """gitignored local store:<root>/.devflow/jev/replay/<evaluation_id>.json。"""

    def __init__(self, repo_root, dirname=REPLAY_DIRNAME):
        self.dir = os.path.join(repo_root, dirname)

    def path(self, evaluation_id):
        if not evaluation_id.startswith("eval_") or "/" in evaluation_id or ".." in evaluation_id:
            raise JevError("非法 evaluation_id %r" % evaluation_id)
        return os.path.join(self.dir, evaluation_id + ".json")

    def write(self, evaluation, packet, questions, raw_response, manifest):
        """sanitized 全文只進這裡;仍過 privacy(不因不進 Git 就無限制收 PHI/secret)。"""
        payload = {"schema": "devflow-jev-replay/1", "evaluation": evaluation, "packet": packet,
                   "questions": questions, "raw_response": raw_response, "manifest": manifest}
        hits = privacy_scan(payload)
        if hits:
            raise JevError("replay store privacy 命中 %s" % hits[:3])
        os.makedirs(self.dir, exist_ok=True)
        target = self.path(evaluation["evaluation_id"])
        if os.path.exists(target):
            raise JevError("replay %s 已存在 —— 不覆蓋原 observation(reevaluation 要新 id)" % target)
        tmp = target + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, sort_keys=True, indent=1)
        os.replace(tmp, target)
        return target

    def status(self, evaluation_id):
        return "available" if os.path.isfile(self.path(evaluation_id)) else "not_replayable"

    def read(self, evaluation_id):
        if self.status(evaluation_id) != "available":
            raise JevError("%s not_replayable —— 不得用現在 repo 狀態重建 packet 冒充原輸入" % evaluation_id)
        with open(self.path(evaluation_id), encoding="utf-8") as fh:
            return json.load(fh)

    def replay(self, evaluation_id, route_fn):
        """stored-response deterministic replay:零網路,原 raw response + 原 manifest 重算 route。"""
        from .transport import parse_response
        stored = self.read(evaluation_id)
        questions = stored["questions"]
        parsed = parse_response(stored["raw_response"], questions)
        packet = stored["packet"]
        route = route_fn(parsed["answers"], packet_flags=packet["consistency_flags"],
                         truncated=packet["truncated"])
        return {"evaluation_id": evaluation_id, "route": route, "answers": parsed["answers"],
                "manifest_hash_used": stored["evaluation"]["questionset_hash"], "network": False}

    def reevaluate(self, evaluation_id, transport, clock, route_fn, new_outcome_builder, budget=None, breaker=None):
        """remote reevaluation:用已保存 sanitized packet/questions 再呼叫;新 evaluation_id、保 lineage、不覆蓋。
        同樣扣 budget／受 breaker(§8.2:reevaluation 算 attempt);子代 replay 用子代自己的 raw response。"""
        from .policy import evaluate
        from .transport import build_request
        from .packet import estimate_input_tokens, to_state
        stored = self.read(evaluation_id)
        packet = stored["packet"]
        questions = stored["questions"]
        request = build_request(to_state(packet), questions, model=stored["evaluation"]["model_requested"])
        outcome = evaluate(transport, request, questions, clock, estimate_input_tokens(packet, questions),
                           deadline_s=60.0, budget=budget, breaker=breaker, breaker_key="reevaluate")
        from .provenance import stamp
        child = new_outcome_builder(stored["evaluation"], packet, outcome)
        child["parent_evaluation_id"] = evaluation_id
        child["case_id"] = stored["evaluation"]["case_id"]          # 同 semantic case;不增 n
        raw = outcome.get("raw") if outcome["status"] == "ok" else None
        child["replay_status"] = "available" if raw is not None else "not_replayable"   # 沒有真的 raw 就不寫,不假重建
        stamp(child)                                                 # lineage 欄位在 INTEGRITY_FIELDS,設完才蓋章
        if raw is not None:
            self.write(child, packet, questions, raw, stored["manifest"])   # 子代自己的 raw;絕不借父代的
        return child


def write_durable(repo_root, record, memory_dir=None):
    """經 memory/agentmem 正規 writer 落盤(不自建 raw ledger)。呼叫端要先 assert_durable_safe。"""
    import sys
    memory_dir = memory_dir or os.path.join(repo_root, "memory")
    if memory_dir not in sys.path:
        sys.path.insert(0, memory_dir)
    from agentmem import durable, signal  # noqa: E402  pylint: disable=import-error
    assert_durable_safe(record)
    verdict = signal.gate("important_discovery", record["title"], record["body"],
                          extra_texts=[json.dumps(record, ensure_ascii=False)])
    if not verdict["durable_allowed"]:
        raise JevError("signal.gate 拒絕:" + "; ".join(verdict["reasons"]))
    return durable.append_events(repo_root, record["session_id"], [record])
