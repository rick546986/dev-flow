#!/usr/bin/env python3
"""devflow-jev.py — jev-gate stdlib runtime(roadmap W2 / P1-F1;Python 3.9+,零第三方套件)。

七組守衛(scripts/devflow_jev/)是它唯一的判斷來源;本檔只做「讀輸入 → 過雙閘門 → 送一次 →
policy 導出 route → 雙層 ledger 落盤」的膠水,不含任何門檻、不含 retry、不寫任何 verdict。

子命令
  status      各 gate 生效等級(key 有無 × .dev-flow/jev.yaml opt-in)、今日 budget、breaker、replay 數。零網路。
  pack        由 JSON 輸入組 evidence packet(G1;privacy 命中 = 拒絕組包)。零網路。
  handoff     W3:J1 在 Decide 前、J3 在 Demo 前。內部只呼叫本檔的 ask(不另寫 HTTP client)。
  enqueue     W4:Stage 7 evidence 固定後,把 J5 shadow evaluation 序列化進 queue;零網路、不擋 G3。
  drain       W4:worker,逐筆經 ask 送 J5 shadow;失敗只記 shadow failure;不寫 G3 verdict。
  label       W4:same-evidence label binding;HEAD/evidence 變了就拒絕,不誤標舊 evaluation。
  enqueue-bench  W4:實測 enqueue p50/p95。
  note        W5 P2-7:封閉五欄附註(gate/qhash prefix/model/route_recommended/eval id),無 answers/probabilities。
  j4-assist   W5 P2-3(實驗):失敗分類 + 升一層建議;assist-only,不派工、不動 dispatch guard。
  j2-shadow   W5 P2-8(實驗):J2 厚包 shadow + order/phrasing stability;window 未核定 → 永遠 shadow。
  eligibility W6 P3-1:J5 資格計算(§5.1 八條、floor、freeze);只展示。runtime 沒有 live 開關(gate.J5_LIVE_RATIFIED=False)。
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
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GRADUATED = False            # W6 前恆 False;沒有 CLI 旗標、沒有環境變數能改它
SHADOW_DEADLINE_S = 60.0     # 非 J1 的單次 HTTP 等待上限(J1 用 policy.J1_DEADLINE_S)
EXPERIMENTAL_GATES = ("J2", "J4")   # W5:題組在 jev-questions-experimental.json,各自 manifest/hash;永遠 shadow/assist
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
EXPERIMENTAL_QUESTIONS_PATH = os.path.join(_package_parent(), "devflow_jev", "jev-questions-experimental.json")
from devflow_jev import GATES, MODEL_PINNED, JevError  # noqa: E402
from devflow_jev import gate as gate_mod  # noqa: E402
from devflow_jev import ledger, manifest as manifest_mod, packet as packet_mod, policy, provenance  # noqa: E402
from devflow_jev import report as report_mod  # noqa: E402
from devflow_jev import attestation  # noqa: E402
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
    if gate == "J4":
        return policy.route_j4(answers, current_model=(packet.get("header") or {}).get("current_model"))
    if gate == "J2":
        identities = (packet.get("header") or {}).get("option_identities") or ""
        identities = dict(item.split("=", 1) for item in identities.split("|") if "=" in item)
        return policy.route_j2(answers, identities)
    raise JevError("gate %s 沒有 route formula" % gate)


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
        if gate == "J4":
            return policy.route_j4(answers, current_model=None)
        if gate == "J2":
            return policy.route_j2(answers, {})
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
            clock=time.monotonic, changed_paths=(), deadline_s=None, run_id=None, memory_dir=None, day=None,
            questions_path=None):
    """回 dict(可直接 json.dumps)。off → 什麼都不寫、transport_factory 不會被呼叫。
    J2/J4(實驗)用 jev-questions-experimental.json 自己的 manifest/hash;J1/J3/J5 用正式題組。"""
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

    if questions_path is None and gate in EXPERIMENTAL_GATES:
        questions_path = EXPERIMENTAL_QUESTIONS_PATH
    questions = manifest_mod.load_questions(questions_path)
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
    # P2-2 / §5.1 第 7 條:mechanical override 不進 graduation denominator;純 model route 才算
    model_route_evals = [ev for ev in evaluations if report_mod.route_class(ev) == "model_route"]
    layers, excluded, conflicting, primary = {}, {}, set(), None
    for source, fbs in by_layer.items():
        one = report_mod.graduation(model_route_evals, fbs, level="shadow", primary_source=source)
        layers[source] = one["layers"][source]
        excluded[source] = one["excluded"]
        conflicting.update(one["conflicting_label_cases"])
        if source == primary_source:
            primary = one
    metrics = report_mod.eval_metrics(evaluations, by_layer, breaker_failures=StateStore(root).load_breaker().failures)
    out = {
        "gate": gate, "graduated": GRADUATED, "auto_allowed": False, "network": False,
        "metrics": metrics,                                   # P2-2:labeled_fraction／truncation_rate／Brier／逐題／route_reason 分層
        "circuit_breaker_state": metrics["circuit_breaker_state"],
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
            "levels": levels, "graduated": GRADUATED, "j5_live_ratified": gate_mod.J5_LIVE_RATIFIED,
            "j2_window_ratified": policy.J2_WINDOW_RATIFIED, "model_pinned": MODEL_PINNED,
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



# ───────────────────────────── W4 J5 shadow: bind / enqueue / drain / label ─────────────────────────────
# roadmap P1-F4:evidence 固定後 enqueue,現有 G3 立刻照走;worker(drain)另跑,失敗只記 shadow failure。
# 本段沒有第二個 HTTP client:drain 呼叫本檔的 run_ask(→ devflow_jev.http_transport)。
# 本段沒有任何寫 docs/dev/<slug>/ 的程式;J5 只讀已產生的 evidence,不產 evidence、不寫 G3 verdict。
QUEUE_DIRNAME = os.path.join(".devflow", "jev", "queue")             # .devflow/ 已 gitignored
QUEUE_DONE_DIRNAME = os.path.join(QUEUE_DIRNAME, "done")
QUEUE_SCHEMA = "devflow-jev-queue/1"
GAUNTLET_REPORT_DEFAULT = os.path.join("evidence", "gauntlet-report.md")   # 相對 docs/dev/<slug>/
J5_PRIMARY_REQUEST = "Given only the mechanical evidence facts in this packet, assess whether the recorded evidence supports shipping this feature."
# label --from-review:人類 G3 verdict 對 Jev route_recommended 的 agree/overturn 映射。HUMAN 建議不是預測,不進 n。
REVIEW_LABEL_MAP = {
    ("AUTO", "PASS"): "agree", ("AUTO", "REQUEST_CHANGES"): "overturn", ("AUTO", "HOLD"): "overturn",
    ("REQUEST_CHANGES", "REQUEST_CHANGES"): "agree", ("REQUEST_CHANGES", "PASS"): "overturn",
}


def _git(root, *args):
    try:
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise JevError("git %s 失敗:%s" % (" ".join(args), exc))
    if proc.returncode != 0:
        raise JevError("git %s 失敗:%s" % (" ".join(args), (proc.stderr or proc.stdout).strip()[:200]))
    return proc.stdout


def _sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _parse_kv_report(text):
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\s*-\s*([A-Za-z][A-Za-z0-9-]*)\s*:\s*(.*)$", line)
        if m and m.group(1) not in out:
            out[m.group(1)] = m.group(2).strip()
    return out


def _e2e_entry_point(spec_path):
    if not os.path.isfile(spec_path):
        return "spec_missing"
    with open(spec_path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\s*-\s*E2E entry point\s*[:：]\s*(.*)$", line, re.I)
            if m:
                return (m.group(1).strip() or "declared_empty")[:200]
    return "not_declared"


def bind_evidence(root, slug, gauntlet_report=None, now=None):
    """自動 evidence binding(P1-F4):同一份 evidence 版本 → 同一組 hash → 同一 case_id。
    artifact_hash = HEAD tree 全表(git ls-tree -r HEAD)的 sha256;evidence_hash = 逐檔 sha256 清單的 sha256
    (7-review.md 必在、6-implementation-notes.md 若在、gauntlet report 必在);head_sha = HEAD。
    任何一項缺 = evidence 未固定 → JevError(呼叫端 enqueue 轉 noop,不擋流程)。
    **不讀** 7-review.md 的 `verdict:` 進 packet(那是人的 G3 判定,不能給預測者看)。"""
    if not isinstance(slug, str) or not _SLUG_RE.match(slug):
        raise JevError("slug 形狀不合法")
    feature_dir = os.path.join(root, "docs", "dev", slug)
    review_path = os.path.join(feature_dir, "7-review.md")
    if not os.path.isfile(review_path):
        raise JevError("evidence 未固定:找不到 docs/dev/%s/7-review.md" % slug)
    report_path = gauntlet_report or os.path.join(feature_dir, GAUNTLET_REPORT_DEFAULT)
    if not os.path.isfile(report_path):
        raise JevError("evidence 未固定:找不到 gauntlet report %s(S2d-fresh 先跑 devflow-evidence-gauntlet.sh --report)" % report_path)
    with open(report_path, encoding="utf-8") as fh:
        report = _parse_kv_report(fh.read())
    gauntlet_verdict = report.get("verdict") or ""
    if not gauntlet_verdict:
        raise JevError("gauntlet report 缺 `- verdict:`")
    head_sha = _git(root, "rev-parse", "HEAD").strip()
    if not _HEAD_RE.match(head_sha):
        raise JevError("HEAD 形狀不對:%r" % head_sha)
    tree = _git(root, "ls-tree", "-r", "HEAD")
    artifact_hash = manifest_mod.sha256_hex(tree)
    files = [("7-review.md", review_path)]
    notes_path = os.path.join(feature_dir, "6-implementation-notes.md")
    if os.path.isfile(notes_path):
        files.append(("6-implementation-notes.md", notes_path))
    files.append((os.path.relpath(report_path, feature_dir).replace(os.sep, "/"), report_path))
    digests = [{"file": name, "sha256": _sha256_file(path)} for name, path in files]
    evidence_hash = manifest_mod.sha256_hex(manifest_mod.canonical_json(digests))
    with open(review_path, encoding="utf-8") as fh:
        review_fm = attestation.parse_frontmatter(fh.read())
    evaluated_at = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    evidence = {"feature": slug, "gate": "J5", "artifact_hash": artifact_hash, "evidence_hash": evidence_hash,
                "head_sha": head_sha, "evaluated_at": evaluated_at}
    header = {
        "slug": slug, "head_sha": head_sha, "artifact_hash": artifact_hash, "evidence_hash": evidence_hash,
        "gauntlet_verdict": gauntlet_verdict,
        "required_layers_status": "gauntlet:%s;checks:%s;violations:%s" % (
            gauntlet_verdict, report.get("checks", "?"), report.get("violations", "?")),
        "e2e_summary": _e2e_entry_point(os.path.join(feature_dir, "4-spec.md")),
        "final_fresh_run_id": report.get("run-id") or "missing",
    }
    facts = ["gauntlet verdict: %s" % gauntlet_verdict,
             "gauntlet checks: %s; violations: %s" % (report.get("checks", "?"), report.get("violations", "?")),
             "gauntlet declared-source-sha: %s; HEAD: %s" % (report.get("declared-source-sha", "?"), head_sha),
             "e2e entry point: %s" % header["e2e_summary"],
             "evidence files: %s" % ", ".join(d["file"] for d in digests)]
    return {"evidence": evidence, "header": header, "source_facts": facts, "files": digests,
            "review_frontmatter": {k: v for k, v in review_fm.items() if k in ("status", "verdict", "verdict_source", "attested_by")},
            "case_id": ledger.case_id(slug, "J5", artifact_hash, evidence_hash, head_sha)}


def build_j5_packet(binding, variant_id="v0"):
    return packet_mod.build_packet(
        "J5", binding["header"], J5_PRIMARY_REQUEST, source_facts=binding["source_facts"],
        evidence_summary_claims_pass=(binding["header"]["gauntlet_verdict"].upper() == "PASS"), variant_id=variant_id)


def _queue_dirs(root):
    return os.path.join(root, QUEUE_DIRNAME), os.path.join(root, QUEUE_DONE_DIRNAME)


def derive_changed_paths(root, base_ref=None):
    """P2-4:沒明給 --changed-paths 時,從 git 推(merge-base(<base>, HEAD)..HEAD;找不到 base → HEAD 那個 commit)。
    回 (paths, source)。推不出 → ([], "unavailable"),不猜。"""
    candidates = [base_ref] if base_ref else []
    candidates += ["develop", "main", "master", "origin/develop", "origin/main"]
    for ref in candidates:
        try:
            _git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
            base = _git(root, "merge-base", ref, "HEAD").strip()
            head = _git(root, "rev-parse", "HEAD").strip()
        except JevError:
            continue
        if base and base != head:
            out = _git(root, "diff", "--name-only", base, "HEAD")
            return sorted(p for p in out.splitlines() if p.strip()), "merge-base(%s)" % ref
    try:
        out = _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
        return sorted(p for p in out.splitlines() if p.strip()), "head_commit"
    except JevError:
        return [], "unavailable"


def run_enqueue(root, slug, author_ref, session_ref, environ=None, gauntlet_report=None, variant_id="v0",
                clock=time.perf_counter, changed_paths=(), run_id=None, now=None, base_ref=None):
    """前景:雙閘門 → 綁 evidence → 組包 → 序列化到 queue。零網路;失敗一律 noop、不擋 G3。
    latency 是實測(clock 差),不宣稱 0ms。"""
    environ = os.environ if environ is None else environ
    base = {"gate": "J5", "slug": slug, "network": False, "g3_blocked": False, "writes_g3_verdict": False,
            "effect": "continue_existing_flow", "graduated": GRADUATED, "written": []}
    level, level_reason = gate_level(root, "J5", environ)
    base.update({"level": level, "level_reason": level_reason})
    if not gate_mod.may_call(level):
        base.update({"status": "noop", "noop_reason": level_reason})
        return base
    try:
        binding = bind_evidence(root, slug, gauntlet_report=gauntlet_report, now=now)
        packet = build_j5_packet(binding, variant_id=variant_id)
        validate_packet(packet, "J5", binding["evidence"])
    except JevError as exc:
        base.update({"status": "noop", "noop_reason": "evidence_not_fixed:" + str(exc)[:160]})
        return base
    changed_paths = list(changed_paths)
    changed_source = "explicit"
    if not changed_paths:
        changed_paths, changed_source = derive_changed_paths(root, base_ref)     # P2-4:risk ceiling 要看到改了什麼
    started = clock()
    qdir, _ = _queue_dirs(root)
    os.makedirs(qdir, exist_ok=True)
    queue_id = ledger.new_ulid("q")
    item = {"schema": QUEUE_SCHEMA, "queue_id": queue_id, "gate": "J5", "slug": slug,
            "enqueued_at": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "author_ref": author_ref, "session_ref": session_ref,
            "run_id": run_id if run_id is not None else read_run_id(root),
            "changed_paths": changed_paths, "changed_paths_source": changed_source, "variant_id": variant_id,
            "risk_ceiling_hit": provenance.risk_ceiling_hit(changed_paths),
            "packet": packet, "evidence": binding["evidence"], "case_id": binding["case_id"],
            "evidence_files": binding["files"]}
    payload = json.dumps(item, ensure_ascii=False, sort_keys=True)
    path = os.path.join(qdir, queue_id + ".json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(payload)
    os.replace(tmp, path)
    latency = clock() - started
    base.update({"status": "enqueued", "queue_id": queue_id, "case_id": binding["case_id"],
                 "packet_hash": packet["packet_hash"], "enqueue_latency_s": latency,
                 "payload_bytes": len(payload.encode("utf-8")), "written": [path],
                 "changed_paths": changed_paths, "changed_paths_source": changed_source,
                 "risk_ceiling_hit": item["risk_ceiling_hit"],
                 "evidence": binding["evidence"], "note": "G3 continues now; evaluation happens in drain"})
    return base


def list_queue(root):
    qdir, _ = _queue_dirs(root)
    if not os.path.isdir(qdir):
        return []
    return sorted(os.path.join(qdir, n) for n in os.listdir(qdir) if n.startswith("q_") and n.endswith(".json"))


def _finish_item(root, path, item, result):
    _, done = _queue_dirs(root)
    os.makedirs(done, exist_ok=True)
    item = dict(item)
    item["drain_result"] = result
    item["drained_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    target = os.path.join(done, os.path.basename(path))
    with open(target + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(item, fh, ensure_ascii=False, sort_keys=True)
    os.replace(target + ".tmp", target)
    os.unlink(path)
    return target


def run_drain(root, environ=None, transport_factory=None, clock=time.monotonic, max_items=None, memory_dir=None):
    """worker:逐筆送 J5 shadow evaluation(經 run_ask)。任何失敗 = shadow failure,只記帳;
    exit 0;不碰 docs/dev/<slug>/。drain 時再查一次雙閘門:off → 跳過、零網路。"""
    environ = os.environ if environ is None else environ
    results, network = [], False
    for path in list_queue(root)[: max_items or None]:
        with open(path, encoding="utf-8") as fh:
            item = json.load(fh)
        if item.get("schema") != QUEUE_SCHEMA or item.get("gate") != "J5":
            res = {"status": "failed", "noop_reason": "queue_item_schema", "network": False}
            results.append(dict(res, queue_id=item.get("queue_id"), done_path=_finish_item(root, path, item, res)))
            continue
        level, level_reason = gate_level(root, "J5", environ)
        if not gate_mod.may_call(level):
            res = {"status": "skipped_gate_off", "noop_reason": level_reason, "network": False}
            results.append(dict(res, queue_id=item["queue_id"], done_path=_finish_item(root, path, item, res)))
            continue
        try:
            out = run_ask(root, "J5", item["slug"], item["packet"], item["evidence"], item["author_ref"],
                          item["session_ref"], environ=environ, transport_factory=transport_factory, clock=clock,
                          changed_paths=item.get("changed_paths") or (), run_id=item.get("run_id"), memory_dir=memory_dir)
            network = network or bool(out.get("network"))
            res = {k: out.get(k) for k in ("status", "noop_reason", "evaluation_id", "case_id", "route_recommended",
                                            "route_reason", "route_taken", "route_taken_reason", "replay_status", "network")}
            res["shadow_failure"] = out.get("status") != "ok"
        except JevError as exc:
            res = {"status": "failed", "noop_reason": "shadow_failure:" + str(exc)[:160], "network": False,
                   "shadow_failure": True}
        if res.get("route_taken") == "AUTO":
            raise JevError("tripwire: drain 得到 route_taken=AUTO —— shadow 下不可能,拒絕落盤")
        results.append(dict(res, queue_id=item["queue_id"], done_path=_finish_item(root, path, item, res)))
    return {"drained": len(results), "results": results, "network": network, "writes_g3_verdict": False,
            "g3_blocked": False, "graduated": GRADUATED, "remaining": len(list_queue(root))}


def _case_evaluations(root, case_id):
    store = ledger.ReplayStore(root)
    out = []
    if not os.path.isdir(store.dir):
        return out
    for name in sorted(os.listdir(store.dir)):
        if name.startswith("eval_") and name.endswith(".json"):
            ev = store.read(name[:-5])["evaluation"]
            if ev.get("case_id") == case_id and ev.get("gate") == "J5":
                out.append(ev)
    return out


def run_label(root, slug, reviewer_ref, session_ref, verdict=None, source=None, from_review=False,
              environ=None, memory_dir=None, gauntlet_report=None, feedback_at=None):
    """same-evidence label binding:用**現在**的 evidence 版本重算 case_id,只配得上同版本的 evaluation。
    HEAD／evidence 一變 → 沒有可配對的 evaluation → refused(不誤標舊 evaluation)。
    同 case 多筆 evaluation(variants／retry／reevaluate)→ label 落在最新一筆,其餘由 report 當 duplicate_case,n 仍 1。"""
    environ = os.environ if environ is None else environ
    binding = bind_evidence(root, slug, gauntlet_report=gauntlet_report)
    cid = binding["case_id"]
    evals = [ev for ev in _case_evaluations(root, cid) if ev.get("status") == "ok"]
    base = {"slug": slug, "gate": "J5", "case_id": cid, "network": False, "writes_g3_verdict": False,
            "current_binding": {k: binding["evidence"][k] for k in ("artifact_hash", "evidence_hash", "head_sha")}}
    if not evals:
        base.update({"status": "refused", "reason": "no_evaluation_for_this_evidence_version",
                     "hint": "HEAD 或 evidence 檔在 evaluation 之後變了,或 evaluation 尚未 drain;舊 evaluation 不得被新 verdict 標記"})
        return base
    evals.sort(key=lambda ev: ev.get("occurred_at") or "")
    target = evals[-1]
    duplicates = [ev["evaluation_id"] for ev in evals[:-1]]
    if from_review:
        cls = attestation.classify(binding["review_frontmatter"])
        if cls["label"] in ("none", "unverified"):
            base.update({"status": "refused", "reason": "review_%s" % cls["label"], "classification": cls,
                         "evaluation_id": target["evaluation_id"]})
            return base
        source = cls["label"]
        mapped = REVIEW_LABEL_MAP.get((target.get("route_recommended"), cls["verdict"]))
        if mapped is None:
            base.update({"status": "not_labelable", "reason": "route_recommended=%s vs review verdict=%s is not a prediction pair"
                         % (target.get("route_recommended"), cls["verdict"]), "classification": cls,
                         "evaluation_id": target["evaluation_id"], "duplicates_same_case": duplicates})
            return base
        verdict = mapped
    if verdict not in ledger.FEEDBACK_VERDICTS or not source:
        raise JevError("label 需要 --from-review,或明示 --verdict agree|overturn 與 --source")
    fb = run_feedback(root, target["evaluation_id"], verdict, source, reviewer_ref, session_ref,
                      binding["evidence"]["artifact_hash"], binding["evidence"]["evidence_hash"],
                      binding["evidence"]["head_sha"], feedback_at=feedback_at, environ=environ, memory_dir=memory_dir)
    base.update({"status": "labelled", "evaluation_id": target["evaluation_id"], "duplicates_same_case": duplicates,
                 "verdict": verdict, "source": source, "suspect": fb["suspect"], "counts_toward_n": fb["counts_toward_n"],
                 "written": fb["written"], "route_recommended": target.get("route_recommended")})
    return base


def run_enqueue_bench(n=200, payload_bytes=20000):
    """實測 enqueue 成本(p50/p95):記憶體序列化(policy.measure_enqueue_latency)+ 真寫檔到暫存 queue。"""
    import tempfile
    mem = policy.measure_enqueue_latency(n=n, payload_bytes=payload_bytes)
    tmp = tempfile.mkdtemp(prefix="jev-enqueue-bench.")
    samples = []
    item = {"schema": QUEUE_SCHEMA, "packet": {"body": "x" * payload_bytes}, "gate": "J5"}
    try:
        for i in range(n):
            started = time.perf_counter()
            payload = json.dumps(item, ensure_ascii=False, sort_keys=True)
            path = os.path.join(tmp, "q_%06d.json" % i)
            with open(path + ".tmp", "w", encoding="utf-8") as fh:
                fh.write(payload)
            os.replace(path + ".tmp", path)
            samples.append(time.perf_counter() - started)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    samples.sort()
    disk = {"n": n, "p50_s": samples[len(samples) // 2], "p95_s": samples[int(len(samples) * 0.95) - 1], "max_s": samples[-1]}
    return {"payload_bytes": payload_bytes, "serialize_only": mem, "serialize_and_write": disk,
            "note": "measured on this machine; not a claim of 0ms"}



# ───────────────────────────── W5: P2-7 note / P2-3 J4 assist / P2-8 J2 thick packet ─────────────────────────────
def run_note(root, evaluation_id, environ=None, memory_dir=None):
    """P2-7:PR／7-review 可貼的封閉附註;沒有 answers／probabilities／packet。"""
    evaluation, where = find_evaluation(root, evaluation_id, environ, memory_dir)
    note = ledger.audit_note(evaluation)
    return {"note": note, "markdown": ledger.audit_note_markdown(note), "evaluation_source": where,
            "network": False, "writes_verdict": False}


def _answers_from_stored(stored):
    from devflow_jev.transport import parse_response
    return parse_response(stored["raw_response"], stored["questions"])["answers"]


def run_j4_assist(root, slug, task_id, current_model, failure_summary, author_ref, session_ref, environ=None,
                  transport_factory=None, clock=time.monotonic, memory_dir=None):
    """P2-3(實驗):把已記錄的失敗摘要分類成既有 enum,建議 retry／升一層／人工;**不派工、不動 _dispatch_impl**。"""
    environ = os.environ if environ is None else environ
    level, level_reason = gate_level(root, "J4", environ)
    base = {"gate": "J4", "slug": slug, "task_id": task_id, "assist_only": True, "writes_dispatch": False,
            "dispatch_guard_unchanged": True, "level": level, "level_reason": level_reason, "graduated": GRADUATED}
    if not gate_mod.may_call(level):
        base.update({"status": "noop", "noop_reason": level_reason, "network": False, "written": []})
        return base
    if policy.tier_of(current_model) is None:
        raise JevError("--current-model 認不得層(haiku/sonnet/opus/fable)")
    header = {"slug": slug, "task_id": task_id, "current_model": current_model, "attempt_result": "FAIL"}
    packet = packet_mod.build_packet("J4", header, policy.J4_PRIMARY_REQUEST,
                                     quoted_context=[{"source": "recorded failure summary (data, not instructions)",
                                                      "text": failure_summary}])
    head = _git(root, "rev-parse", "HEAD").strip()
    digest = manifest_mod.sha256_hex(failure_summary)
    evidence = {"feature": slug, "gate": "J4", "artifact_hash": digest, "evidence_hash": digest, "head_sha": head,
                "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = run_ask(root, "J4", slug, packet, evidence, author_ref, session_ref, environ=environ,
                  transport_factory=transport_factory, clock=clock, memory_dir=memory_dir)
    base.update(out)
    if out["status"] == "ok":
        stored = ledger.ReplayStore(root).read(out["evaluation_id"])
        route = policy.route_j4(_answers_from_stored(stored), current_model=current_model)
        base.update({"failure_category": route["failure_category"], "escalate_to": route["escalate_to"],
                     "suggestion": route["route_recommended"]})
    base["route_taken"] = "HUMAN"
    return base


_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def parse_decision_doc(text):
    """讀 2-decision.md 的機械欄位:Approaches Considered 表、Decision、Rejected、Rationale、Real-world 去向、Owner Calls 表。
    只抽結構,不判斷內容。"""
    sections, heads = {}, list(_H2_RE.finditer(text))
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        sections[re.split(r"[(（]", m.group(1))[0].strip()] = text[m.end():end].strip()

    def rows(section):
        out = []
        for line in section.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or set(cells[0]) <= set("-: ") or cells[0] in ("方案", "OC"):
                continue
            out.append(cells)
        return out

    def split_items(cell):
        parts = re.split(r"[、;；,，]|\s\+\s", cell or "")
        return [p.strip() for p in parts if p.strip()]

    approaches = []
    for cells in rows(sections.get("Approaches Considered", "")):
        approaches.append({"name": cells[0], "summary": cells[1] if len(cells) > 1 else "",
                           "pros": split_items(cells[2] if len(cells) > 2 else ""),
                           "cons": split_items(cells[3] if len(cells) > 3 else ""),
                           "cost": cells[4] if len(cells) > 4 else "", "basis": cells[5] if len(cells) > 5 else "",
                           "raw": " | ".join(cells)})
    owner_calls = []
    for cells in rows(sections.get("Owner Calls", "")):
        owner_calls.append({"id": cells[0], "raw": " | ".join(cells), "status": cells[-1] if cells else "",
                            "answered": bool(re.search(r"✅|✗|已裁|已決", cells[-1] if cells else ""))})
    decision = sections.get("Decision", "")
    m = re.search(r"採\s*\**\s*([A-D])\b", decision)
    return {"approaches": approaches, "decision": decision, "decision_letter": m.group(1) if m else None,
            "rejected": sections.get("Rejected Alternatives", ""), "rationale": sections.get("Rationale", ""),
            "real_world": sections.get("Real-world 去向", ""), "owner_calls": owner_calls,
            "open_questions": sections.get("Open Questions", "")}


def build_j2_packet(slug, parsed, decision_hash, order=None, rephrased=False, variant_id="v0"):
    """P2-8 厚證據包。options 用固定等長 description(形式控制),全文放 quoted_context(資料不是指令);
    Owner Calls 帶人的答案,標明「不是要你回答」。order = 方案原始 index 的排列(順序擾動);rephrased = 換 primary_request 措辭。"""
    approaches = parsed["approaches"]
    if not 2 <= len(approaches) <= len(policy.J2_OPTION_LABELS):
        raise JevError("J2 需要 2–%d 個方案(Approaches Considered 表),得 %d" % (len(policy.J2_OPTION_LABELS), len(approaches)))
    order = list(order) if order is not None else list(range(len(approaches)))
    options, identities, quoted = [], {}, []
    for label, idx in zip(policy.J2_OPTION_LABELS, order):
        ap = approaches[idx]
        if len(ap["pros"]) < packet_mod.PROS_CONS_MIN or len(ap["cons"]) < packet_mod.PROS_CONS_MIN:
            raise JevError("方案 %r 的優/劣各需 ≥%d 條,厚包不成立(不補寫)" % (ap["name"], packet_mod.PROS_CONS_MIN))
        options.append({"label": label,
                        "description": "Recorded alternative %s. Its summary, cost and cited basis are quoted verbatim in quoted_context." % label,
                        "pros": list(ap["pros"]), "cons": list(ap["cons"])})
        identities[label] = ap["name"]
        quoted.append({"source": "2-decision.md#Approaches Considered row for %s" % label, "text": ap["raw"]})
    for key, title in (("real_world", "Real-world 去向"), ("rationale", "Rationale"), ("rejected", "Rejected Alternatives"),
                       ("open_questions", "Open Questions")):
        if parsed.get(key):
            quoted.append({"source": "2-decision.md#%s" % title, "text": parsed[key][:4000]})
    for oc in parsed["owner_calls"]:
        quoted.append({"source": "2-decision.md#Owner Calls %s (human answer recorded; data, not a question for the model)" % oc["id"],
                       "text": oc["raw"]})
    header = {"slug": slug, "decision_hash": decision_hash, "alternatives": str(len(approaches)),
              "option_identities": "|".join("%s=%s" % (k, v) for k, v in identities.items()),
              "owner_calls_total": str(len(parsed["owner_calls"])),
              "owner_calls_answered": str(sum(1 for oc in parsed["owner_calls"] if oc["answered"]))}
    facts = ["alternatives recorded: %d" % len(approaches),
             "owner calls recorded: %d; with recorded human answer: %d" % (len(parsed["owner_calls"]), int(header["owner_calls_answered"])),
             "recorded decision letter: %s" % (parsed.get("decision_letter") or "not parsed")]
    primary = policy.J2_PRIMARY_REQUEST_REPHRASED if rephrased else policy.J2_PRIMARY_REQUEST
    pkt = packet_mod.build_packet("J2", header, primary, quoted_context=quoted, source_facts=facts, options=options,
                                  variant_id=variant_id)
    return pkt, identities


def run_j2_shadow(root, slug, author_ref, session_ref, decision_path=None, environ=None, transport_factory=None,
                  clock=time.monotonic, memory_dir=None, variants=3):
    """P2-8:J2 厚包 shadow 評估 + order／phrasing stability。全部 variants 同一 case_id(不灌 n);
    window 未核定 → route_taken 恆 HUMAN;沒有 AUTO_PASS 路徑。"""
    environ = os.environ if environ is None else environ
    level, level_reason = gate_level(root, "J2", environ)
    base = {"gate": "J2", "slug": slug, "level": level, "level_reason": level_reason, "graduated": GRADUATED,
            "auto_pass": False, "window_ratified": policy.J2_WINDOW_RATIFIED, "window_candidate": policy.J2_WINDOW_CANDIDATE,
            "writes_decision": False, "answers_owner_calls": False}
    if not gate_mod.may_call(level):
        base.update({"status": "noop", "noop_reason": level_reason, "network": False, "written": []})
        return base
    decision_path = decision_path or os.path.join(root, "docs", "dev", slug, "2-decision.md")
    if not os.path.isfile(decision_path):
        base.update({"status": "noop", "noop_reason": "decision_missing", "network": False, "written": []})
        return base
    with open(decision_path, encoding="utf-8") as fh:
        text = fh.read()
    parsed = parse_decision_doc(text)
    decision_hash = manifest_mod.sha256_hex(text)
    head = _git(root, "rev-parse", "HEAD").strip()
    evidence = {"feature": slug, "gate": "J2", "artifact_hash": decision_hash, "evidence_hash": decision_hash,
                "head_sha": head, "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    n = len(parsed["approaches"])
    plans = [("v0", list(range(n)), False), ("v1", list(reversed(range(n))), False), ("v2", list(range(n)), True)][:max(1, variants)]
    results, routes = [], []
    for variant_id, order, rephrased in plans:
        try:
            pkt, identities = build_j2_packet(slug, parsed, decision_hash, order=order, rephrased=rephrased, variant_id=variant_id)
        except JevError as exc:
            base.update({"status": "noop", "noop_reason": "packet_unbuildable:" + str(exc)[:160], "network": False, "written": []})
            return base
        out = run_ask(root, "J2", slug, pkt, evidence, author_ref, session_ref, environ=environ,
                      transport_factory=transport_factory, clock=clock, memory_dir=memory_dir)
        entry = {k: out.get(k) for k in ("status", "noop_reason", "evaluation_id", "case_id", "route_recommended",
                                          "route_taken", "route_taken_reason")}
        entry["variant_id"] = variant_id
        if out["status"] == "ok":
            stored = ledger.ReplayStore(root).read(out["evaluation_id"])
            route = policy.route_j2(_answers_from_stored(stored), identities)
            recorded = identities.get(parsed["decision_letter"]) if (parsed.get("decision_letter") and order == list(range(n))) else None
            entry.update({"preferred_identity": route["preferred_identity"], "decision_supported": route["decision_supported"],
                          "matches_recorded_decision": (route["preferred_identity"] == recorded) if recorded else None})
            routes.append(route)
        results.append(entry)
    stability = policy.j2_stability(routes)
    base.update({"status": "ok" if routes else "noop",
                 "noop_reason": None if routes else (results[0].get("noop_reason") if results else "no_variants"),
                 "results": results, "stability": stability,
                 "case_id": results[0]["case_id"] if results else None, "network": True,
                 "route_taken": "HUMAN", "recorded_decision_letter": parsed.get("decision_letter")})
    return base



# ───────────────────────────── W6 P3-1 eligibility(只計算、只展示;沒有 live 開關)─────────────────────────────
def run_eligibility(root, gate="J5", primary_source=None, environ=None, memory_dir=None):
    """report → report_mod.eligibility。eligible=True 也不會開任何東西:runtime 沒有 live 路徑,
    gate.J5_LIVE_RATIFIED=False、GRADUATED=False 都是常數。"""
    rep = run_report(root, gate, primary_source=primary_source, environ=environ, memory_dir=memory_dir)
    store = ledger.ReplayStore(root)
    evaluations = []
    if os.path.isdir(store.dir):
        for name in sorted(os.listdir(store.dir)):
            if name.startswith("eval_") and name.endswith(".json"):
                ev = store.read(name[:-5])["evaluation"]
                if ev["gate"] == gate:
                    evaluations.append(ev)
    out = report_mod.eligibility(evaluations, rep["metrics"], primary_source=primary_source)
    if gate == "J2" and not any(b.startswith("j2_window_not_ratified") for b in out["blockers"]):
        out["blockers"].append("j2_window_not_ratified(candidate=%d; formal rolling window pending; J2 stays shadow)"
                               % policy.J2_WINDOW_CANDIDATE)
        out["eligible"] = False
    out.update({"gate": gate, "graduated": GRADUATED, "j5_live_ratified": gate_mod.J5_LIVE_RATIFIED,
                "j2_window_ratified": policy.J2_WINDOW_RATIFIED,
                "auto_allowed": False, "network": False,
                "layers": rep["layers"], "evaluations_not_replayable": rep["evaluations_not_replayable"]})
    return out

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
    sq5 = sub.add_parser("enqueue", help="W4:evidence 固定後把 J5 shadow evaluation 排進 queue;零網路、不擋 G3")
    sq5.add_argument("--slug", required=True)
    sq5.add_argument("--author-ref", required=True)
    sq5.add_argument("--session-ref", required=True)
    sq5.add_argument("--gauntlet-report", default=None, help="預設 docs/dev/<slug>/evidence/gauntlet-report.md")
    sq5.add_argument("--variant-id", default="v0")
    sq5.add_argument("--changed-paths", default=None)
    sq5.add_argument("--run-id", default=None)
    sd = sub.add_parser("drain", help="W4:worker;逐筆送 J5 shadow(經 ask),失敗只記 shadow failure;不寫 G3")
    sd.add_argument("--max", type=int, default=None)
    sl = sub.add_parser("label", help="W4:same-evidence label binding;HEAD/evidence 變了就拒絕")
    sl.add_argument("--slug", required=True)
    sl.add_argument("--reviewer-ref", required=True)
    sl.add_argument("--session-ref", required=True)
    sl.add_argument("--from-review", action="store_true", help="從 7-review.md frontmatter(verdict/verdict_source/attested_by)推 label")
    sl.add_argument("--verdict", default=None, choices=ledger.FEEDBACK_VERDICTS)
    sl.add_argument("--source", default=None, choices=("human_attested", "fresh_agent_reviewer", "owner_self_review"))
    sl.add_argument("--gauntlet-report", default=None)
    sl.add_argument("--feedback-at", default=None)
    sb = sub.add_parser("enqueue-bench", help="W4:實測 enqueue p50/p95(序列化 + 寫檔)")
    sb.add_argument("--n", type=int, default=200)
    sq5.add_argument("--base-ref", default=None, help="P2-4:推 changed_paths 的 merge-base 對象(預設 develop/main/master)")
    sn = sub.add_parser("note", help="W5 P2-7:PR/7-review 可貼的封閉附註(五欄;無 answers/probabilities/packet)")
    sn.add_argument("--evaluation-id", required=True)
    s4 = sub.add_parser("j4-assist", help="W5 P2-3(實驗):失敗分類 + 升一層建議;assist-only,不派工")
    s4.add_argument("--slug", required=True)
    s4.add_argument("--task-id", required=True)
    s4.add_argument("--current-model", required=True)
    s4.add_argument("--failure-summary", required=True, help="文字檔:已記錄的失敗摘要(不要貼 log 全文)")
    s4.add_argument("--author-ref", required=True)
    s4.add_argument("--session-ref", required=True)
    s2 = sub.add_parser("j2-shadow", help="W5 P2-8(實驗):J2 厚包 shadow + order/phrasing stability;永遠 shadow")
    s2.add_argument("--slug", required=True)
    s2.add_argument("--author-ref", required=True)
    s2.add_argument("--session-ref", required=True)
    s2.add_argument("--decision", default=None, help="預設 docs/dev/<slug>/2-decision.md")
    s2.add_argument("--variants", type=int, default=3)
    sel = sub.add_parser("eligibility", help="W6 P3-1:J5 資格計算(§5.1 八條 + floor + freeze);只展示,沒有 live 開關")
    sel.add_argument("--gate", default="J5", choices=GATES)
    sel.add_argument("--primary-source", default=None, choices=("human_attested", "fresh_agent_reviewer"))
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
        if args.cmd == "enqueue":
            _emit(run_enqueue(root, args.slug, args.author_ref, args.session_ref, gauntlet_report=args.gauntlet_report,
                              variant_id=args.variant_id, changed_paths=read_lines(args.changed_paths), run_id=args.run_id,
                              base_ref=args.base_ref))
            return EXIT_OK
        if args.cmd == "note":
            _emit(run_note(root, args.evaluation_id))
            return EXIT_OK
        if args.cmd == "j4-assist":
            with open(args.failure_summary, encoding="utf-8") as fh:
                summary = fh.read()
            _emit(run_j4_assist(root, args.slug, args.task_id, args.current_model, summary, args.author_ref, args.session_ref))
            return EXIT_OK
        if args.cmd == "j2-shadow":
            _emit(run_j2_shadow(root, args.slug, args.author_ref, args.session_ref, decision_path=args.decision,
                                variants=args.variants))
            return EXIT_OK
        if args.cmd == "eligibility":
            _emit(run_eligibility(root, args.gate, args.primary_source))
            return EXIT_OK
        if args.cmd == "drain":
            _emit(run_drain(root, max_items=args.max))
            return EXIT_OK
        if args.cmd == "label":
            out = run_label(root, args.slug, args.reviewer_ref, args.session_ref, verdict=args.verdict, source=args.source,
                            from_review=args.from_review, gauntlet_report=args.gauntlet_report, feedback_at=args.feedback_at)
            _emit(out)
            return EXIT_OK if out["status"] == "labelled" else EXIT_INCONSISTENT
        if args.cmd == "enqueue-bench":
            _emit(run_enqueue_bench(n=args.n))
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
