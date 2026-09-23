#!/usr/bin/env python3
"""devflow-jev.py — jev-gate stdlib runtime(roadmap W2 / P1-F1;Python 3.9+,零第三方套件)。

七組守衛(scripts/devflow_jev/)是它唯一的判斷來源;本檔只做「讀輸入 → 過雙閘門 → 送一次 →
policy 導出 route → 雙層 ledger 落盤」的膠水,不含任何門檻、不含 retry、不寫任何 verdict。

子命令
  status      各 gate 生效等級(key 有無 × .dev-flow/jev.yaml opt-in)、今日 budget、breaker、replay 數。零網路。
  pack        由 JSON 輸入組 evidence packet(G1;privacy 命中 = 拒絕組包)。零網路。
  handoff     W3:J1 在 Decide 前、J3 在 Demo 前。內部只呼叫本檔的 ask(不另寫 HTTP client)。
              off／失敗／逾時 → exit 0、effect=continue_existing_flow。J3 只回顯示文案,不寫 verdict。
  ask         一次 evaluation:雙閘門 off → exit 0、什麼都不寫、零網路;shadow/live → 送一次,
              失敗 no-op(G2),route 由 policy 導出(G6),replay store + durable(G4)。
  replay      stored-response deterministic replay(零網路)+ 完整性重算;對不上 exit 1。
  reevaluate  remote reevaluation:同 sanitized packet 再送一次;新 evaluation_id、保 lineage、同 case_id。
  feedback    人／fresh agent 的 agree/overturn label 落 durable;可疑(同 session、reviewer=author、
              evidence 版本不一致…)一律留痕但不進 n。
  report      分層 graduation 報表(human_attested / fresh_agent_reviewer 各算各的;Wilson 95% 下界)。零網路。

硬約束(owner 2026-09-23):
  - 沒有正式 AUTO:`GRADUATED = False` 寫死、沒有旗標;`route_taken == "AUTO"` 在寫盤前有 tripwire。
  - 雙閘門:`TYPESAFE_API_KEY` × `.dev-flow/jev.yaml`,少一個 = off = 不建 transport、不 enqueue、不落盤。
  - 七守衛行為不鬆:本檔不覆寫 policy/packet/ledger/provenance 任何常數。
  - J3 永不寫 G2 verdict、J5 永不寫 G3 verdict;本檔沒有任何寫 docs/dev/<slug>/ 的程式。

退出碼:0 = ok 或 no-op(Jev 從不阻塞既有流程) / 1 = replay 完整性對不上 / 2 = 輸入或安裝錯誤(fail-loud)。
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GRADUATED = False            # W6 前恆 False;沒有 CLI 旗標、沒有環境變數能改它
SHADOW_DEADLINE_S = 60.0     # 非 J1 的單次 HTTP 等待上限(J1 用 policy.J1_DEADLINE_S)
EXIT_OK, EXIT_INCONSISTENT, EXIT_USAGE = 0, 1, 2


def _package_parent():
    """套件與本檔並排(scripts/ 或散發後的 docs/dev/tools/);`DEVFLOW_JEV_LIB` 可明示。"""
    explicit = os.environ.get("DEVFLOW_JEV_LIB", "").strip()
    candidates = ([explicit] if explicit else []) + [HERE]
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, "devflow_jev", "__init__.py")):
            return cand
    raise SystemExit("⛔ 找不到 devflow_jev 套件(找過 %s);runtime 與套件必須一起散發" % candidates)


sys.path.insert(0, _package_parent())
from devflow_jev import GATES, MODEL_PINNED, JevError  # noqa: E402
from devflow_jev import gate as gate_mod  # noqa: E402
from devflow_jev import ledger, manifest as manifest_mod, packet as packet_mod, policy, provenance  # noqa: E402
from devflow_jev import report as report_mod  # noqa: E402
from devflow_jev.attestation import graduation_eligible  # noqa: E402
from devflow_jev.state import StateStore, _atomic_write, utc_day  # noqa: E402
from devflow_jev.transport import build_request  # noqa: E402


# ───────────────────────────── helpers ─────────────────────────────
def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_memory_dir(root, environ=None):
    """memory/agentmem 所在:受測專案自帶 → $DEVFLOW_MEMORY_LIB → $DEVFLOW_ROOT/memory → 本檔上一層 memory/。"""
    environ = os.environ if environ is None else environ
    candidates = [os.path.join(root, "memory")]
    if environ.get("DEVFLOW_MEMORY_LIB"):
        candidates.append(environ["DEVFLOW_MEMORY_LIB"])
    if environ.get("DEVFLOW_ROOT"):
        candidates.append(os.path.join(environ["DEVFLOW_ROOT"], "memory"))
    candidates.append(os.path.join(os.path.dirname(HERE), "memory"))
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, "agentmem", "durable.py")):
            return cand
    raise JevError("找不到 memory/agentmem(找過 %s)—— durable ledger 是正本,缺它不落盤;設 DEVFLOW_ROOT 或 DEVFLOW_MEMORY_LIB" % candidates)


def _require_memory_dir(root, environ, memory_dir):
    if memory_dir is not None:
        if not os.path.isfile(os.path.join(memory_dir, "agentmem", "durable.py")):
            raise JevError("memory_dir %s 沒有 agentmem/durable.py" % memory_dir)
        return memory_dir
    return resolve_memory_dir(root, environ)


def read_run_id(root):
    """`.devflow/exec.json` 的 run_id 只作 provenance(P0-5:同 slug re-arm 會換 run_id,不作 case identity)。"""
    path = os.path.join(root, ".devflow", "exec.json")
    if not os.path.isfile(path):
        return None
    try:
        return load_json(path).get("run_id")
    except (ValueError, OSError):
        return None


def read_lines(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def gate_level(root, gate, environ=None):
    environ = os.environ if environ is None else environ
    return gate_mod.effective_level(gate, gate_mod.has_api_key(environ), gate_mod.load_optin(root))


def make_transport_factory(environ=None):
    """只在雙閘門通過後才被呼叫;這是整支 runtime 唯一會 import 網路模組的地方。"""
    environ = os.environ if environ is None else environ

    def factory(timeout_s=None):
        from devflow_jev import http_transport   # 延遲 import:off 路徑連 urllib 都不載入
        endpoint = environ.get(http_transport.ENDPOINT_ENV) or http_transport.ENDPOINT_DEFAULT
        kwargs = {"endpoint": endpoint}
        if timeout_s is not None:
            kwargs["timeout_s"] = timeout_s          # socket 層等待 = policy deadline;J1 不會在線上卡 30s
        return http_transport.HttpTransport(environ.get(gate_mod.KEY_ENV, ""), **kwargs)
    return factory


def _build_transport(factory, deadline_s):
    try:
        return factory(deadline_s)
    except TypeError:
        return factory()                              # 測試注入的無參 factory


def _deadline(gate, deadline_s):
    """policy 的 deadline 只能被 argv 收緊,不能放寬(G2 常數不在 runtime 覆寫)。"""
    base = policy.J1_DEADLINE_S if gate == "J1" else SHADOW_DEADLINE_S
    if deadline_s is None:
        return base
    if not isinstance(deadline_s, (int, float)) or deadline_s <= 0:
        raise JevError("--deadline 必須是正數")
    return min(base, float(deadline_s))


_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_HEAD_RE = re.compile(r"^[0-9a-f]{7,40}$")
_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
PACKET_SCHEMA = "devflow-jev-packet/1"


def validate_evidence(evidence, gate, slug):
    """六欄全必填、形狀嚴格(小寫 hex、無空白):case_id 直接 hash 這些字串,大小寫／尾空白不同就會裂成兩個 case。"""
    if not isinstance(evidence, dict):
        raise JevError("evidence 必須是 JSON 物件")
    for key in sorted(ledger.EVIDENCE_ALLOWED_KEYS):
        if not isinstance(evidence.get(key), str) or not evidence[key] or evidence[key] != evidence[key].strip():
            raise JevError("evidence.%s 必填且不得有前後空白(六欄:%s)" % (key, sorted(ledger.EVIDENCE_ALLOWED_KEYS)))
    extra = set(evidence) - ledger.EVIDENCE_ALLOWED_KEYS
    if extra:
        raise JevError("evidence 多了白名單外的欄 %s" % sorted(extra))
    if evidence["gate"] != gate or evidence["feature"] != slug:
        raise JevError("evidence.gate/feature 必須等於 --gate/--slug(%s/%s)" % (gate, slug))
    if not _SLUG_RE.match(slug):
        raise JevError("--slug 只准 [A-Za-z0-9._-](無空白、無分號)")
    for key in ("artifact_hash", "evidence_hash"):
        if not _SHA256_RE.match(evidence[key]):
            raise JevError("evidence.%s 必須是 sha256:<64 小寫 hex>" % key)
    if not _HEAD_RE.match(evidence["head_sha"]):
        raise JevError("evidence.head_sha 必須是 7–40 位小寫 hex")
    return dict(evidence)


def validate_packet(packet, gate, evidence):
    """送出前的 caller 端檢查(不是 G1 本體;G1 在 pack 時已跑,這裡防 pack 之後被改):
    schema／gate 對得上、packet_hash 重算一致、privacy 零命中、self_check 全過、header 的機械事實與 evidence 同值。
    任一不符 → fail-loud,**在建 transport／寫任何檔之前**。"""
    if not isinstance(packet, dict) or packet.get("schema") != PACKET_SCHEMA:
        raise JevError("packet.schema 必須是 %s(用 pack 子命令產出)" % PACKET_SCHEMA)
    if packet.get("gate") != gate:
        raise JevError("packet.gate=%r 與 --gate=%s 不符" % (packet.get("gate"), gate))
    for key in ("header", "body", "packet_hash", "truncated", "consistency_flags"):
        if key not in packet:
            raise JevError("packet 缺 %s" % key)
    if packet_mod.packet_hash(packet) != packet["packet_hash"]:
        raise JevError("packet_hash 對不上 —— packet 在 pack 之後被改過,拒送")
    hits = packet_mod.privacy_scan(packet)
    if hits:
        raise JevError("packet privacy 命中 %s —— 拒送(不遮罩後放行)" % hits[:3])
    failed = [c for c, ok, _ in packet_mod.self_check(packet) if not ok]
    if failed:
        raise JevError("packet self_check 未過:%s" % failed)
    header = packet["header"]
    for hkey, ekey in (("slug", "feature"), ("head_sha", "head_sha"), ("artifact_hash", "artifact_hash"),
                       ("evidence_hash", "evidence_hash")):
        if hkey in header and header[hkey] != evidence[ekey]:
            raise JevError("packet.header.%s=%r 與 evidence.%s=%r 不符 —— 同一 case 的 header 與 evidence 必須同值"
                           % (hkey, header[hkey], ekey, evidence[ekey]))
    return packet


def route_for(gate, answers, packet, risk_hit, runtime_changed):
    flags = packet.get("consistency_flags") or []
    truncated = bool(packet.get("truncated"))
    if gate == "J5":
        return policy.route_j5(answers, packet_flags=flags, truncated=truncated,
                               risk_ceiling_hit=bool(risk_hit), runtime_changed=bool(runtime_changed))
    if gate == "J1":
        route = policy.route_j1(answers, truncated=truncated, packet_flags=flags)
        route["route_recommended"] = route["next"]
        return route
    if gate == "J3":
        safe = policy.sanitize_j3(policy.route_j3(answers))
        if safe is None:
            return {"route_recommended": None, "route_reason": "j3_route_rejected",
                    "signals": {"writes_verdict": False}}
        return {"route_recommended": safe["recommendation"],
                "route_reason": "demo_worth_it=%s(writes_verdict=false)" % safe["demo_worth_it"],
                "signals": safe}
    raise JevError("gate %s 沒有 route formula(J2/J4 保留,不在 MVP)" % gate)


def replay_route_fn(evaluation):
    gate = evaluation["gate"]

    def fn(answers, packet_flags=(), truncated=False):
        if gate == "J5":
            return policy.route_j5(answers, packet_flags=packet_flags, truncated=truncated,
                                   risk_ceiling_hit=bool(evaluation.get("risk_ceiling_hit")),
                                   runtime_changed=bool(evaluation.get("runtime_changed")))
        if gate == "J1":
            route = policy.route_j1(answers, truncated=truncated, packet_flags=packet_flags)
            route["route_recommended"] = route["next"]
            return route
        safe = policy.sanitize_j3(policy.route_j3(answers))
        if safe is None:
            return {"route_recommended": None, "signals": {"writes_verdict": False}}
        return {"route_recommended": safe["recommendation"], "signals": safe}
    return fn


def _taken(gate, level, outcome, route):
    if outcome["status"] != "ok":
        return "HUMAN", "noop_fallback_to_current_flow"
    taken, reason = policy.route_taken(gate, level, route.get("route_recommended"), graduated=GRADUATED)
    if taken == "AUTO":
        # G6 tripwire:W6 前不可能走到;真走到 = policy 被改,拒寫、fail-loud。
        raise JevError("tripwire: route_taken=AUTO 在 graduated=False 下不應出現 —— 拒絕落盤")
    return taken, reason


# ───────────────────────────── core operations ─────────────────────────────
def run_ask(root, gate, slug, packet, evidence, author_ref, session_ref, environ=None, transport_factory=None,
            clock=time.monotonic, changed_paths=(), deadline_s=None, run_id=None, memory_dir=None, day=None):
    """回 dict(可直接 json.dumps)。off → 什麼都不寫、transport_factory 不會被呼叫。"""
    environ = os.environ if environ is None else environ
    if gate not in GATES:
        raise JevError("未知 gate %r" % gate)
    if not isinstance(slug, str) or not slug.strip():
        raise JevError("--slug 必填")
    level, level_reason = gate_level(root, gate, environ)       # 雙閘門最先:off 路徑不驗、不讀、不寫
    result = {"gate": gate, "slug": slug, "level": level, "level_reason": level_reason,
              "model_requested": MODEL_PINNED, "graduated": GRADUATED}
    if not gate_mod.may_call(level):
        result.update({"status": "noop", "noop_reason": level_reason, "network": False, "written": []})
        return result
    evidence = validate_evidence(evidence, gate, slug)
    packet = validate_packet(packet, gate, evidence)
    memory_dir = _require_memory_dir(root, environ, memory_dir)   # durable writer 缺 → 在送出／寫檔前就 fail-loud
    deadline = _deadline(gate, deadline_s)

    questions = manifest_mod.load_questions()
    manifest = manifest_mod.build_manifest(questions)
    qhash = manifest_mod.questionset_hash(manifest)
    api_questions = manifest_mod.gate_questions_for_api(manifest, gate)
    request = build_request(packet_mod.to_state(packet), api_questions)
    est = packet_mod.estimate_input_tokens(packet, api_questions)

    state = StateStore(root)
    day = day or utc_day()
    budget = state.load_budget(day)
    breaker = state.load_breaker()
    transport = _build_transport(transport_factory or make_transport_factory(environ), deadline)
    outcome = policy.evaluate(transport, request, api_questions, clock, est, deadline_s=deadline,
                              budget=budget, breaker=breaker, breaker_key=gate)
    state.save_budget(budget, day)
    state.save_breaker(breaker)

    changed_paths = list(changed_paths)
    risk_hit = provenance.risk_ceiling_hit(changed_paths)
    rt_changed = provenance.runtime_changed(changed_paths)
    if outcome["status"] == "ok":
        route = route_for(gate, outcome["answers"], packet, risk_hit, rt_changed)
    else:
        route = {"route_recommended": None, "route_reason": "noop:" + outcome["reason"]}
    taken, taken_reason = _taken(gate, level, outcome, route)

    evaluation = ledger.build_evaluation(
        gate, slug, level, packet, qhash, route, taken, taken_reason, outcome, evidence, author_ref,
        run_id=run_id if run_id is not None else read_run_id(root), session_ref=session_ref,
        risk_ceiling_hit=bool(risk_hit), runtime_changed=bool(rt_changed))
    provenance.stamp(evaluation)

    replay = ledger.ReplayStore(root)
    replay_status, replay_path = "not_replayable", None
    if outcome["status"] == "ok":
        replay_path = replay.write(evaluation, packet, api_questions, outcome["raw"], manifest)
        replay_status = "available"
    record = ledger.build_durable_record(evaluation, replay_status)
    written = ledger.write_durable(root, record, memory_dir=memory_dir)
    result.update({
        "status": outcome["status"], "noop_reason": outcome.get("reason") or None, "network": True,
        "evaluation_id": evaluation["evaluation_id"], "case_id": evaluation["case_id"],
        "questionset_hash": qhash, "model_resolved": evaluation["model_resolved"],
        "route_recommended": evaluation["route_recommended"], "route_reason": evaluation["route_reason"],
        "route_taken": taken, "route_taken_reason": taken_reason,
        "risk_ceiling_hit": risk_hit, "runtime_changed": rt_changed,
        "replay_status": replay_status, "replay_path": replay_path, "written": list(written),
        "usage": outcome.get("usage"), "budget_remaining": budget.remaining(),
        "breaker_failures": breaker.failures.get(gate, 0),
        "weakest_dimension": route.get("weakest_dimension") if gate == "J1" else None,
    })
    return result


def run_replay(root, evaluation_id):
    store = ledger.ReplayStore(root)
    stored = store.read(evaluation_id)
    evaluation = stored["evaluation"]
    out = store.replay(evaluation_id, replay_route_fn(evaluation))
    problems = provenance.verify_evaluation(evaluation, evaluation["mode"], graduated=GRADUATED)
    replayed = out["route"].get("route_recommended")
    if evaluation["status"] == "ok" and replayed != evaluation["route_recommended"]:
        problems.append("replay_route_mismatch(記錄 %s,重放 %s)" % (evaluation["route_recommended"], replayed))
    if stored.get("manifest") is not None:
        recomputed = manifest_mod.questionset_hash(stored["manifest"])
        if recomputed != evaluation["questionset_hash"]:
            problems.append("questionset_hash_mismatch(記錄 %s,重算 %s)" % (evaluation["questionset_hash"][:23], recomputed[:23]))
    return {"evaluation_id": evaluation_id, "gate": evaluation["gate"], "network": False,
            "route_recorded": evaluation["route_recommended"], "route_replayed": replayed,
            "route_taken_recorded": evaluation["route_taken"], "problems": problems, "consistent": not problems}


def run_reevaluate(root, evaluation_id, author_ref, session_ref, environ=None, transport_factory=None,
                   clock=time.monotonic, memory_dir=None, day=None):
    environ = os.environ if environ is None else environ
    store = ledger.ReplayStore(root)
    parent = store.read(evaluation_id)["evaluation"]
    gate = parent["gate"]
    level, level_reason = gate_level(root, gate, environ)
    if not gate_mod.may_call(level):
        return {"status": "noop", "noop_reason": level_reason, "level": level, "network": False,
                "parent_evaluation_id": evaluation_id, "written": []}
    memory_dir = _require_memory_dir(root, environ, memory_dir)   # 送出前先確認 durable writer 在
    state = StateStore(root)
    day = day or utc_day()
    budget, breaker = state.load_budget(day), state.load_breaker()
    transport = _build_transport(transport_factory or make_transport_factory(environ), SHADOW_DEADLINE_S)

    def builder(parent_eval, packet, outcome):
        if outcome["status"] == "ok":
            route = route_for(gate, outcome["answers"], packet, parent_eval.get("risk_ceiling_hit"),
                              parent_eval.get("runtime_changed"))
        else:
            route = {"route_recommended": None, "route_reason": "noop:" + outcome["reason"]}
        taken, reason = _taken(gate, level, outcome, route)
        return ledger.build_evaluation(
            gate, parent_eval["slug"], level, packet, parent_eval["questionset_hash"], route, taken, reason,
            outcome, parent_eval["evidence"], author_ref, run_id=parent_eval.get("run_id"), session_ref=session_ref,
            risk_ceiling_hit=bool(parent_eval.get("risk_ceiling_hit")), runtime_changed=bool(parent_eval.get("runtime_changed")))

    child = store.reevaluate(evaluation_id, transport, clock, replay_route_fn(parent), builder,
                             budget=budget, breaker=breaker)
    state.save_budget(budget, day)
    state.save_breaker(breaker)
    replay_status = child.pop("replay_status", "not_replayable")
    record = ledger.build_durable_record(child, replay_status)
    written = ledger.write_durable(root, record, memory_dir=memory_dir)
    return {"status": child["status"], "noop_reason": child.get("noop_reason"), "level": level, "network": True,
            "parent_evaluation_id": evaluation_id, "evaluation_id": child["evaluation_id"], "case_id": child["case_id"],
            "route_recommended": child["route_recommended"], "route_taken": child["route_taken"],
            "replay_status": replay_status, "written": list(written), "graduation_n_effect": 0}


def _agentmem(root, environ=None, memory_dir=None):
    memory_dir = memory_dir or resolve_memory_dir(root, environ)
    if memory_dir not in sys.path:
        sys.path.insert(0, memory_dir)
    from agentmem import durable  # noqa: E402  pylint: disable=import-error
    return durable


def _evaluation_from_durable(record):
    """durable 沒有完整 evaluation(無 probabilities、無 packet),只還原 feedback_suspect 需要的欄位。"""
    jev = record["jev"]
    parts = record.get("title", "").split()
    slug = parts[3] if len(parts) > 3 else None
    body = dict(kv.split("=", 1) for kv in record.get("body", "").split(";") if "=" in kv)
    return {"evaluation_id": jev["evaluation_id"], "case_id": jev["case_id"], "gate": body.get("gate"),
            "slug": slug, "mode": body.get("mode"), "author_ref": jev.get("author_ref"),
            "session_ref": jev.get("session_ref"), "occurred_at": jev.get("occurred_at"),
            "evidence": dict(jev.get("evidence") or {}), "status": body.get("status"), "from_durable_only": True}


def find_evaluation(root, evaluation_id, environ=None, memory_dir=None):
    store = ledger.ReplayStore(root)
    if store.status(evaluation_id) == "available":
        return store.read(evaluation_id)["evaluation"], "replay"
    durable = _agentmem(root, environ, memory_dir)
    for record in durable.iter_events(root):
        jev = record.get("jev") or {}
        if record.get("kind") == "jev" and jev.get("record_type") != "feedback" and jev.get("evaluation_id") == evaluation_id:
            return _evaluation_from_durable(record), "durable"
    raise JevError("找不到 evaluation %s(replay store 與 durable 都沒有)" % evaluation_id)


def run_feedback(root, evaluation_id, verdict, source, reviewer_ref, session_ref, artifact_hash, evidence_hash,
                 head_sha, feedback_at=None, environ=None, memory_dir=None):
    environ = os.environ if environ is None else environ
    evaluation, where = find_evaluation(root, evaluation_id, environ, memory_dir)
    feedback = {"verdict": verdict, "source": source, "reviewer_ref": reviewer_ref, "session_ref": session_ref,
                "feedback_at": feedback_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "artifact_hash": artifact_hash, "evidence_hash": evidence_hash, "head_sha": head_sha}
    suspect = provenance.feedback_suspect(evaluation, feedback)
    if not graduation_eligible(source):
        suspect = sorted(set(suspect) | {"source_not_graduation_eligible:%s" % source})
    record = ledger.build_feedback_record(evaluation, feedback, suspect)
    written = ledger.write_durable(root, record, memory_dir=memory_dir or resolve_memory_dir(root, environ))
    return {"evaluation_id": evaluation_id, "case_id": evaluation["case_id"], "evaluation_source": where,
            "verdict": verdict, "source": source, "suspect": suspect, "counts_toward_n": not suspect,
            "written": list(written), "network": False}


def _pick_feedback(existing, candidate):
    """同一 evaluation 多筆 feedback:任一 overturn 就取 overturn(fail-closed);否則取最晚。"""
    if existing is None:
        return candidate
    if candidate["verdict"] == "overturn" and existing["verdict"] != "overturn":
        return candidate
    if existing["verdict"] == "overturn" and candidate["verdict"] != "overturn":
        return existing
    return candidate if candidate.get("feedback_at", "") >= existing.get("feedback_at", "") else existing


def run_report(root, gate="J5", primary_source=None, environ=None, memory_dir=None):
    store = ledger.ReplayStore(root)
    evaluations, replay_ids = [], set()
    if os.path.isdir(store.dir):
        for name in sorted(os.listdir(store.dir)):
            if name.startswith("eval_") and name.endswith(".json"):
                ev = store.read(name[:-5])["evaluation"]
                if ev["gate"] == gate:
                    evaluations.append(ev)
                    replay_ids.add(ev["evaluation_id"])
    # feedback 依 (source 層, evaluation_id) 分桶:兩層各看各的,不互相蓋掉;落盤時已標 suspect 的先剔除
    # (report.graduation 之後還會再用 feedback_suspect 重算一次,這裡剔除只是不讓可疑票蓋掉同層有效票)。
    by_layer = {"human_attested": {}, "fresh_agent_reviewer": {}}
    skipped_suspect, not_replayable, feedback_total = 0, [], 0
    durable = _agentmem(root, environ, memory_dir)
    for record in durable.iter_events(root):
        if record.get("kind") != "jev":
            continue
        jev = record.get("jev") or {}
        if jev.get("record_type") == "feedback":
            if jev.get("gate") != gate:
                continue
            feedback_total += 1
            if jev.get("suspect"):
                skipped_suspect += 1
                continue
            layer = by_layer.get(jev.get("source"))
            if layer is None:
                continue                                      # owner_self_review 等不進 graduation 的層
            layer[jev["evaluation_id"]] = _pick_feedback(layer.get(jev["evaluation_id"]), jev)
        elif jev.get("evaluation_id") and jev["evaluation_id"] not in replay_ids:
            body = dict(kv.split("=", 1) for kv in record.get("body", "").split(";") if "=" in kv)
            if body.get("gate") == gate:
                not_replayable.append(jev["evaluation_id"])
    layers, excluded, conflicting, primary = {}, {}, set(), None
    for source, fbs in by_layer.items():
        one = report_mod.graduation(evaluations, fbs, level="shadow", primary_source=source)
        layers[source] = one["layers"][source]
        excluded[source] = one["excluded"]
        conflicting.update(one["conflicting_label_cases"])
        if source == primary_source:
            primary = one
    out = {
        "gate": gate, "graduated": GRADUATED, "auto_allowed": False, "network": False,
        "layers": layers,                                     # 分層;沒有 combined 主率
        "primary_source": primary_source,
        "floor_met": primary["floor_met"] if primary else None,
        "frozen": primary["frozen"] if primary else None,
        "wilson_lower_95": primary["wilson_lower_95"] if primary else None,
        "n_unique_valid_by_layer": {k: v["n"] for k, v in layers.items()},
        "conflicting_label_cases": sorted(conflicting),
        "excluded_by_layer": excluded,
        "evaluations_replayable": len(evaluations), "evaluations_not_replayable": sorted(not_replayable),
        "feedbacks": feedback_total, "feedbacks_skipped_suspect": skipped_suspect,
        "note": "engineering acceptance threshold; not a proof of accuracy; primary layer pending formal spec (B3 leave_unset)",
    }
    return out


def run_status(root, environ=None):
    environ = os.environ if environ is None else environ
    has_key = gate_mod.has_api_key(environ)
    try:
        optin = gate_mod.load_optin(root)
        optin_state = "absent" if optin is None else "present"
        optin_error = None
    except JevError as exc:
        optin, optin_state, optin_error = None, "invalid", str(exc)
    levels = {}
    for g in GATES:
        if optin_error:
            levels[g] = {"level": "off", "reason": "optin_invalid"}
        else:
            level, reason = gate_mod.effective_level(g, has_key, optin)
            levels[g] = {"level": level, "reason": reason}
    questions = manifest_mod.load_questions()
    manifest = manifest_mod.build_manifest(questions)
    state = StateStore(root)
    budget = state.load_budget()
    breaker = state.load_breaker()
    replay_dir = ledger.ReplayStore(root).dir
    replay_count = len([n for n in os.listdir(replay_dir) if n.endswith(".json")]) if os.path.isdir(replay_dir) else 0
    try:
        memory_dir = resolve_memory_dir(root, environ)
    except JevError as exc:
        memory_dir = None
    return {"root": root, "api_key_present": has_key, "optin": optin_state, "optin_error": optin_error,
            "levels": levels, "graduated": GRADUATED, "model_pinned": MODEL_PINNED,
            "questionset_hash": manifest_mod.questionset_hash(manifest),
            "versions": {k: manifest[k] for k in manifest_mod.MANIFEST_KEYS if k != "questions"},
            "budget_today": {"day": utc_day(), "remaining": budget.remaining(), "attempts_used": budget.attempts},
            "breaker_failures": dict(breaker.failures), "replay_store": {"dir": replay_dir, "count": replay_count},
            "memory_lib": memory_dir, "network": False}


def run_pack(gate, spec, out_path=None):
    packet = packet_mod.build_packet(
        gate, spec.get("header") or {}, spec.get("primary_request", ""),
        quoted_context=spec.get("quoted_context") or (), source_facts=spec.get("source_facts") or (),
        options=spec.get("options"), verify_tails=spec.get("verify_tails") or (),
        evidence_summary_claims_pass=bool(spec.get("evidence_summary_claims_pass", False)),
        variant_id=spec.get("variant_id", "v0"))
    checks = packet_mod.self_check(packet)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(packet, fh, ensure_ascii=False, sort_keys=True, indent=1)
    return {"packet_hash": packet["packet_hash"], "truncated": packet["truncated"],
            "consistency_flags": packet["consistency_flags"], "route_forced": packet["route_forced"],
            "self_check": [{"check": c, "ok": ok, "detail": d} for c, ok, d in checks],
            "all_ok": all(ok for _, ok, _ in checks), "out": out_path,
            "note": "self-check is a formal control, not prompt-injection immunity"}


# ───────────────────────────── W3 handoff (J1 / J3) ─────────────────────────────
_H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
_FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
_OQ = re.compile(r"^\s*[-*]\s+\[(.)\]", re.M)
_STATUS = re.compile(r"^status:\s*(\S+)", re.M)
J1_UNVERIFIED_SOURCE = "S1 待重驗的 Log 材料，不是已核事實"
J1_SOURCE_FACT = "quoted excerpts are log material pending S1 re-check, not established facts; read whitelist is not mechanical execution"


def _continue_flow(reason, gate, level=None, level_reason=None):
    return {
        "gate": gate, "status": "noop", "noop_reason": reason, "level": level, "level_reason": level_reason,
        "effect": "continue_existing_flow", "steers_flow": False, "network": False, "written": [],
        "writes_verdict": False, "writes_g2_verdict": False, "writes_g3_verdict": False,
        "graduated": GRADUATED, "idempotent": False,
    }


def _split_sections(text):
    matches = list(_H2.finditer(text))
    out = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group(1).split("(")[0].strip()
        out[title] = text[match.end():end].strip()
    return out


def _frontmatter_status(text):
    match = _FM.match(text)
    if not match:
        return None
    found = _STATUS.search(match.group(1))
    return found.group(1) if found else None


def _open_questions_state(body):
    if body is None:
        return "section_missing"
    marks = _OQ.findall(body)
    if not marks:
        return "none_listed"
    if any(mark == ">" for mark in marks):
        return "has_handoff"
    if any(mark in (" ", "~") for mark in marks):
        return "has_open"
    if all(mark in ("x", "X") for mark in marks):
        return "none_open"
    return "has_open"


def _clip(text, limit=600):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + " …"


def _read_optional(root, path):
    if not path:
        return None
    full = path if os.path.isabs(path) else os.path.join(root, path)
    if not os.path.isfile(full):
        return None
    with open(full, encoding="utf-8") as fh:
        return fh.read()


def _head_sha(root):
    import subprocess
    try:
        out = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    sha = out.strip()
    if _HEAD_RE.match(sha):
        return sha
    return None


def _sha_text(text):
    return manifest_mod.sha256_hex(text if isinstance(text, str) else "")


def _load_json_dict(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_json_dict(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _atomic_write(path, payload)


def _j1_packet(slug, discussion, discussion_hash):
    sections = _split_sections(discussion)
    quoted = []
    for title in ("Goals", "Non-Goals", "驗收雛形", "Open Questions", "Real-world Context"):
        body = sections.get(title)
        if not body:
            continue
        quoted.append({
            "source": "1-discussion.md#%s | %s" % (title, J1_UNVERIFIED_SOURCE),
            "text": _clip(body),
        })
    present = [title for title in ("Goals", "Non-Goals", "驗收雛形", "Open Questions", "Real-world Context")
               if sections.get(title)]
    header = {
        "slug": slug,
        "discussion_hash": discussion_hash,
        "open_questions_state": _open_questions_state(sections.get("Open Questions")),
    }
    facts = [
        J1_SOURCE_FACT,
        "sections_present=%s" % ",".join(present),
        "open_questions_state=%s" % header["open_questions_state"],
    ]
    policy.assert_no_rubric_copy(policy.J1_PRIMARY_REQUEST, "J1")
    return packet_mod.build_packet("J1", header, policy.J1_PRIMARY_REQUEST,
                                   quoted_context=quoted, source_facts=facts)


def _evidence_for(gate, slug, artifact_text, bundle_text, head):
    return {
        "feature": slug, "gate": gate,
        "artifact_hash": _sha_text(artifact_text),
        "evidence_hash": _sha_text(bundle_text),
        "head_sha": head,
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _classify_failure(exc):
    msg = str(exc)
    if "privacy" in msg:
        return "prepare_privacy_reject"
    if "memory" in msg or "agentmem" in msg:
        return "memory_lib_missing"
    if "discussion" in msg:
        return "prepare_discussion_rejected"
    return "prepare_or_ask_failed"


def _attach_j1(base, effect):
    kept = ("effect", "next", "model_next", "weakest_dimension", "rounds_completed", "ask_more_max_rounds",
            "round_capped", "skip_redundant_clarity_question", "stop_before_decide", "theme", "restart", "instruction")
    for key in kept:
        base[key] = effect[key]
    base["steers_flow"] = effect["effect"] != "continue_existing_flow"
    policy._assert_no_verdict_markers(base)
    return base


def run_handoff_j1(root, slug, author_ref, session_ref, discussion_path=None, environ=None,
                   transport_factory=None, clock=None, memory_dir=None):
    environ = os.environ if environ is None else environ
    level, level_reason = gate_level(root, "J1", environ)
    if not gate_mod.may_call(level):
        return _continue_flow(level_reason, "J1", level, level_reason)
    path = discussion_path or os.path.join("docs", "dev", slug, "1-discussion.md")
    text = _read_optional(root, path)
    if text is None:
        return _continue_flow("missing_discussion", "J1", level, level_reason)
    if _frontmatter_status(text) != "approved":
        return _continue_flow("discussion_not_approved", "J1", level, level_reason)
    discussion_hash = _sha_text(text)
    cache_path = os.path.join(root, ".devflow", "jev", "state", "j1-rounds.json")
    cache = _load_json_dict(cache_path)
    by_slug = cache.get(slug) if isinstance(cache.get(slug), dict) else {"talks": [], "by_hash": {}}
    talks = [item for item in by_slug.get("talks") or [] if isinstance(item, str)]
    by_hash = by_slug.get("by_hash") if isinstance(by_slug.get("by_hash"), dict) else {}
    cached = by_hash.get(discussion_hash)
    if isinstance(cached, dict) and cached.get("status") == "ok":
        again = dict(cached)
        again["idempotent"] = True
        again["network"] = False
        return again
    head = _head_sha(root)
    if head is None:
        return _continue_flow("no_head_sha", "J1", level, level_reason)
    try:
        packet = _j1_packet(slug, text, discussion_hash)
        evidence = _evidence_for("J1", slug, text, discussion_hash, head)
        ask = run_ask(root, "J1", slug, packet, evidence, author_ref, session_ref, environ=environ,
                      transport_factory=transport_factory, clock=clock or time.monotonic, memory_dir=memory_dir)
    except JevError as exc:
        return _continue_flow(_classify_failure(exc), "J1", level, level_reason)
    base = {
        "gate": "J1", "slug": slug, "status": ask["status"], "noop_reason": ask.get("noop_reason"),
        "level": ask["level"], "level_reason": ask.get("level_reason"), "network": ask.get("network"),
        "evaluation_id": ask.get("evaluation_id"), "graduated": GRADUATED, "idempotent": False,
        "written": list(ask.get("written") or []), "writes_verdict": False,
        "writes_g2_verdict": False, "writes_g3_verdict": False,
        "discussion_hash": discussion_hash,
    }
    if ask["status"] != "ok" or ask["level"] != "live":
        base.update({"effect": "continue_existing_flow", "steers_flow": False,
                     "model_route_taken": ask.get("route_taken") if ask["status"] != "ok" or ask.get("route_taken") == "HUMAN" else None})
        # shadow 的 route_taken 恆 HUMAN,不拿來指揮流程;失敗也一樣。不把模型自由文字抄出來。
        if ask["level"] == "shadow" and ask["status"] == "ok":
            base["noop_reason"] = "shadow_mode"
        return base
    if discussion_hash not in talks:
        talks.append(discussion_hash)
    try:
        effect = policy.j1_effect(ask.get("route_taken"), ask.get("weakest_dimension"), len(talks))
        if effect is None:
            base.update({"effect": "continue_existing_flow", "steers_flow": False, "noop_reason": "unusable_j1_route"})
            return base
        _attach_j1(base, effect)
    except JevError:
        return _continue_flow("handoff_output_rejected", "J1", level, level_reason)
    by_hash[discussion_hash] = dict(base)
    cache[slug] = {"talks": talks, "by_hash": by_hash}
    _save_json_dict(cache_path, cache)
    return base


def _j3_packet(slug, discussion, spec_text, proto_text, trigger):
    quoted = []
    if discussion:
        quoted.append({"source": "1-discussion.md | %s" % J1_UNVERIFIED_SOURCE, "text": _clip(discussion, 800)})
    if spec_text:
        quoted.append({"source": "4-spec.md | input excerpt, not a verdict", "text": _clip(spec_text, 800)})
    if proto_text:
        quoted.append({"source": "3-prototype.md | trigger excerpt, not a verdict", "text": _clip(proto_text, 800)})
    bundle = "\n".join([trigger, discussion or "", spec_text or "", proto_text or ""])
    header = {"slug": slug, "spec_hash": _sha_text(spec_text or bundle), "stage3_trigger": trigger}
    policy.assert_no_rubric_copy(policy.J3_PRIMARY_REQUEST, "J3")
    packet = packet_mod.build_packet(
        "J3", header, policy.J3_PRIMARY_REQUEST, quoted_context=quoted,
        source_facts=["stage3_trigger=%s" % trigger,
                      "recommendation only; do not write a review outcome",
                      J1_SOURCE_FACT])
    return packet, bundle


def run_handoff_j3(root, slug, author_ref, session_ref, stage3_trigger=None, discussion_path=None,
                   spec_path=None, prototype_path=None, environ=None, transport_factory=None,
                   clock=None, memory_dir=None):
    environ = os.environ if environ is None else environ
    level, level_reason = gate_level(root, "J3", environ)
    if not gate_mod.may_call(level):
        return _continue_flow(level_reason, "J3", level, level_reason)
    trigger = stage3_trigger or "unrecorded"
    if trigger not in ("hit", "none", "unrecorded"):
        return _continue_flow("bad_stage3_trigger", "J3", level, level_reason)
    discussion = _read_optional(root, discussion_path or os.path.join("docs", "dev", slug, "1-discussion.md"))
    spec_text = _read_optional(root, spec_path)
    proto_path = prototype_path or os.path.join("docs", "dev", slug, "3-prototype.md")
    proto_text = _read_optional(root, proto_path)
    # 有 frontmatter 但還沒 approved = 討論還沒走完,不當成 Demo 建議的輸入。
    if discussion is not None and _frontmatter_status(discussion) not in (None, "approved"):
        return _continue_flow("discussion_not_approved", "J3", level, level_reason)
    head = _head_sha(root)
    if head is None:
        return _continue_flow("no_head_sha", "J3", level, level_reason)
    try:
        packet, bundle = _j3_packet(slug, discussion, spec_text, proto_text, trigger)
        evidence = _evidence_for("J3", slug, bundle, trigger + "\n" + (discussion or ""), head)
        ask = run_ask(root, "J3", slug, packet, evidence, author_ref, session_ref, environ=environ,
                      transport_factory=transport_factory, clock=clock or time.monotonic, memory_dir=memory_dir)
    except JevError as exc:
        return _continue_flow(_classify_failure(exc), "J3", level, level_reason)
    base = {
        "gate": "J3", "slug": slug, "status": ask["status"], "noop_reason": ask.get("noop_reason"),
        "level": ask["level"], "level_reason": ask.get("level_reason"), "network": ask.get("network"),
        "evaluation_id": ask.get("evaluation_id"), "graduated": GRADUATED, "idempotent": False,
        "written": list(ask.get("written") or []), "writes_verdict": False, "writes_attestation": False,
        "writes_g2_verdict": False, "writes_g3_verdict": False, "changes_demo_requirement": False,
        "polarity_unchanged": True, "steers_flow": False, "effect": "continue_existing_flow",
    }
    if ask["status"] == "ok" and ask["level"] == "live":
        advice = policy.j3_effect(ask.get("route_taken"))
        if advice is not None:
            if proto_text is not None:
                policy.refuse_j3_write(proto_text, advice)  # 不使用回傳值;不開檔寫
            base.update({
                "effect": advice["effect"], "recommendation": advice["recommendation"],
                "display": advice["display"], "steers_flow": False,
            })
        else:
            base["noop_reason"] = "unusable_j3_route"
    elif ask["level"] == "shadow" and ask["status"] == "ok":
        base["noop_reason"] = "shadow_mode"
    try:
        policy._assert_no_verdict_markers(base)
    except JevError:
        return _continue_flow("handoff_output_rejected", "J3", level, level_reason)
    return base


def run_handoff(root, gate, slug, author_ref, session_ref, **kwargs):
    if gate == "J5":
        raise JevError("handoff 不接 J5(W4);J5 永不寫 G3 verdict")
    if gate == "J1":
        return run_handoff_j1(root, slug, author_ref, session_ref,
                              discussion_path=kwargs.get("discussion_path"), environ=kwargs.get("environ"),
                              transport_factory=kwargs.get("transport_factory"), clock=kwargs.get("clock"),
                              memory_dir=kwargs.get("memory_dir"))
    if gate == "J3":
        return run_handoff_j3(root, slug, author_ref, session_ref,
                              stage3_trigger=kwargs.get("stage3_trigger"),
                              discussion_path=kwargs.get("discussion_path"),
                              spec_path=kwargs.get("spec_path"), prototype_path=kwargs.get("prototype_path"),
                              environ=kwargs.get("environ"), transport_factory=kwargs.get("transport_factory"),
                              clock=kwargs.get("clock"), memory_dir=kwargs.get("memory_dir"))
    raise JevError("handoff 只接 J1 與 J3(J2/J4 保留,J5 是 W4)")


# ───────────────────────────── CLI ─────────────────────────────
def _emit(payload):
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1))


def build_parser():
    p = argparse.ArgumentParser(prog="devflow-jev", description=__doc__.splitlines()[0])
    p.add_argument("--root", default=os.getcwd(), help="受測專案根(預設 cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sp = sub.add_parser("pack")
    sp.add_argument("--gate", required=True, choices=GATES)
    sp.add_argument("--in", dest="spec", required=True, help="JSON:header/primary_request/quoted_context/source_facts/options/verify_tails")
    sp.add_argument("--out", help="寫出 packet JSON 的路徑")
    sa = sub.add_parser("ask")
    sa.add_argument("--gate", required=True, choices=GATES)
    sa.add_argument("--slug", required=True)
    sa.add_argument("--packet", required=True, help="pack 產出的 packet JSON")
    sa.add_argument("--evidence", required=True, help="JSON:feature/gate/artifact_hash/evidence_hash/head_sha/evaluated_at")
    sa.add_argument("--author-ref", required=True)
    sa.add_argument("--session-ref", required=True)
    sa.add_argument("--run-id", default=None)
    sa.add_argument("--changed-paths", default=None, help="一行一個路徑;risk ceiling / runtime_changed 判定用")
    sa.add_argument("--deadline", type=float, default=None, help="只能比 policy deadline 更短(收緊),不能放寬")
    sr = sub.add_parser("replay")
    sr.add_argument("--evaluation-id", required=True)
    se = sub.add_parser("reevaluate")
    se.add_argument("--evaluation-id", required=True)
    se.add_argument("--author-ref", required=True)
    se.add_argument("--session-ref", required=True)
    sf = sub.add_parser("feedback")
    sf.add_argument("--evaluation-id", required=True)
    sf.add_argument("--verdict", required=True, choices=ledger.FEEDBACK_VERDICTS)
    sf.add_argument("--source", required=True, choices=("human_attested", "fresh_agent_reviewer", "owner_self_review"))
    sf.add_argument("--reviewer-ref", required=True)
    sf.add_argument("--session-ref", required=True)
    sf.add_argument("--artifact-hash", required=True)
    sf.add_argument("--evidence-hash", required=True)
    sf.add_argument("--head-sha", required=True)
    sf.add_argument("--feedback-at", default=None)
    sq = sub.add_parser("report")
    sq.add_argument("--gate", default="J5", choices=GATES)
    sq.add_argument("--primary-source", default=None, choices=("human_attested", "fresh_agent_reviewer"))
    sh = sub.add_parser("handoff", help="W3:J1 Decide 前 / J3 Demo 建議。內部呼叫 ask,不另寫 HTTP client")
    sh.add_argument("--gate", required=True, choices=("J1", "J3"))
    sh.add_argument("--slug", required=True)
    sh.add_argument("--author-ref", required=True)
    sh.add_argument("--session-ref", required=True)
    sh.add_argument("--discussion", default=None, help="預設 docs/dev/<slug>/1-discussion.md")
    sh.add_argument("--spec", default=None)
    sh.add_argument("--prototype", default=None)
    sh.add_argument("--stage3-trigger", default=None, choices=("hit", "none", "unrecorded"))
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = os.path.abspath(args.root)
    try:
        if args.cmd == "status":
            _emit(run_status(root))
            return EXIT_OK
        if args.cmd == "pack":
            out = run_pack(args.gate, load_json(args.spec), args.out)
            _emit(out)
            return EXIT_OK if out["all_ok"] else EXIT_INCONSISTENT
        if args.cmd == "ask":
            out = run_ask(root, args.gate, args.slug, load_json(args.packet), load_json(args.evidence),
                          args.author_ref, args.session_ref, changed_paths=read_lines(args.changed_paths),
                          deadline_s=args.deadline, run_id=args.run_id)
            _emit(out)
            return EXIT_OK
        if args.cmd == "replay":
            out = run_replay(root, args.evaluation_id)
            _emit(out)
            return EXIT_OK if out["consistent"] else EXIT_INCONSISTENT
        if args.cmd == "reevaluate":
            _emit(run_reevaluate(root, args.evaluation_id, args.author_ref, args.session_ref))
            return EXIT_OK
        if args.cmd == "feedback":
            _emit(run_feedback(root, args.evaluation_id, args.verdict, args.source, args.reviewer_ref, args.session_ref,
                               args.artifact_hash, args.evidence_hash, args.head_sha, feedback_at=args.feedback_at))
            return EXIT_OK
        if args.cmd == "report":
            _emit(run_report(root, args.gate, args.primary_source))
            return EXIT_OK
        if args.cmd == "handoff":
            _emit(run_handoff(root, args.gate, args.slug, args.author_ref, args.session_ref,
                              discussion_path=args.discussion, spec_path=args.spec,
                              prototype_path=args.prototype, stage3_trigger=args.stage3_trigger))
            return EXIT_OK
    except JevError as exc:
        print("⛔ devflow-jev %s: %s" % (args.cmd, exc), file=sys.stderr)
        return EXIT_USAGE
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("⛔ devflow-jev %s: 輸入/檔案錯誤 %s: %s" % (args.cmd, type(exc).__name__, exc), file=sys.stderr)
        return EXIT_USAGE
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
