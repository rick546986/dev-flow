#!/usr/bin/env python3
"""devflow-jev.py — G2R 分流 + G2 誤放行紀錄(G2 自動審查上線;Python 3.9+,stdlib only)。

從 research/jev-supermemory 只搬 G2 上線要的兩塊(W9 G2R 分流、W10 g2-misrelease);J1–J5 runtime 不在 main。
Jev **只分流**:決定這個 G2 案子交給 fresh-context agent reviewer 還是交給人。Jev 不 review、不寫 verdict、
不填 attested_by;本檔沒有任何寫 docs/dev/<slug>/ 的程式(verdict 由 scripts/devflow_gate.py 寫)。

子命令
  status      G2R 生效等級(key 有無 × .dev-flow/jev.yaml mode)與三個 live 開關(恆 False)。零網路。
  g2r         對 docs/dev/<slug>/4-spec.md 跑一次 G2R 分流 → append `.devflow/jev/g2r.jsonl`。
              雙閘門(TYPESAFE_API_KEY + jev.yaml mode: live)通過才送 Jev 一次;沒 key／沒 opt-in／失敗／逾時／
              breaker open／budget 用完 = 沒有 Jev(no-op,ADR 0004 §2):不擋、不放寬,routed_by=none,其餘轉人條件照判。
              AUTO 不是通過:還要 agent reviewer PASS + 機械檢查(devflow_gate.py write-g2-auto)。
  g2-misrelease record|release|report
              G2 誤放行只記錄。release = agent 放行時記一筆(devflow_gate.py write-g2-auto 會呼叫);
              record = 之後在 G3／實作發現 spec 有問題;report = 誤放行率(不設門檻、不自動回滾、不擋任何東西)。

硬約束:
  - `GRADUATED = False`、`gate.J5_LIVE_RATIFIED = False`、`policy.J2_WINDOW_RATIFIED = False` 寫死,沒有旗標。
  - 雙閘門沿用 gate.py(不改):少一個 = off = 不建 transport、零網路。G2R 不在 jev.yaml `gates:`,只看 `mode:`。

退出碼:0 = ok(g2r 判 HUMAN 也是 0)/ 1 = report 資料不一致 / 2 = 輸入或安裝錯誤(fail-loud)。
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GRADUATED = False            # 沒有 CLI 旗標、沒有環境變數能改它
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
from devflow_jev import JevError  # noqa: E402
from devflow_jev import gate as gate_mod  # noqa: E402
from devflow_jev import g2auto, policy  # noqa: E402
from devflow_jev.state import StateStore, utc_day  # noqa: E402
from devflow_jev.transport import build_request  # noqa: E402

G2R_LOG = g2auto.G2R_LOG
G2R_SCHEMA = g2auto.G2R_SCHEMA
G2M_LOG = os.path.join(".devflow", "jev", "g2-misrelease.jsonl")      # .devflow/ 已 gitignored
G2M_SCHEMA = "devflow-g2-misrelease/1"
G2M_REPORT_SCHEMA = "devflow-g2-misrelease-report/1"
G2M_RELEASE_LOG = os.path.join(".devflow", "jev", "g2-agent-release.jsonl")  # 誤放行率分母
G2M_RELEASE_SCHEMA = "devflow-g2-agent-release/1"


def _flags():
    return {"graduated": GRADUATED, "j5_live_ratified": gate_mod.J5_LIVE_RATIFIED,
            "j2_window_ratified": policy.J2_WINDOW_RATIFIED}


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _append_jsonl(root, rel, entry):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return rel.replace(os.sep, "/")


def _read_jsonl(path):
    """回 (rows, corrupt_line_numbers);檔不存在 → (None, [])。"""
    if not os.path.exists(path):
        return None, []
    rows, corrupt = [], []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                corrupt.append(n)
                continue
            if isinstance(row, dict):
                rows.append((n, row))
            else:
                corrupt.append(n)
    return rows, corrupt


# ───────────────────────────── 雙閘門(G2R)─────────────────────────────
def g2r_level(has_key, optin):
    """G2R 的雙閘門:沿用 gate.py 的兩個輸入(key 有無 × `.dev-flow/jev.yaml` 解析結果),**不改 gate.py**。
    G2R 不是 J1–J5,`gates:` 列不到它,所以只看 `mode:`。只有 mode: live 時 Jev 的分流才算數;
    shadow = 呼叫、記錄,但分流上視同沒有 Jev;off／沒 key／沒 opt-in = 不呼叫、沒有 Jev(no-op)。回 (level, reason)。"""
    if not has_key:
        return "off", "no_api_key"
    if optin is None:
        return "off", "no_project_optin"
    mode = optin.get("mode") if isinstance(optin, dict) else None
    if mode not in ("off", "shadow", "live"):
        raise JevError("jev.yaml mode %r 不認得" % (mode,))
    return mode, "mode=%s" % mode


def make_transport_factory(environ=None):
    """只在雙閘門通過後才被呼叫;這是整支 runtime 唯一會 import 網路模組的地方。"""
    environ = os.environ if environ is None else environ

    def factory(timeout_s=None):
        from devflow_jev import http_transport   # 延遲 import:off 路徑連 urllib 都不載入
        endpoint = environ.get(http_transport.ENDPOINT_ENV) or http_transport.ENDPOINT_DEFAULT
        kwargs = {"endpoint": endpoint}
        if timeout_s is not None:
            kwargs["timeout_s"] = timeout_s
        return http_transport.HttpTransport(environ.get(gate_mod.KEY_ENV, ""), **kwargs)
    return factory


def run_status(root, environ=None):
    environ = os.environ if environ is None else environ
    has_key = gate_mod.has_api_key(environ)
    optin_error = None
    try:
        optin = gate_mod.load_optin(root)
        level, reason = g2r_level(has_key, optin)
    except JevError as exc:
        optin, level, reason, optin_error = None, "off", "optin_error", str(exc)
    out = {"gate": "G2R", "has_api_key": has_key, "optin_present": optin is not None,
           "level": level, "level_reason": reason, "auto_possible": level == "live", "network": False}
    if optin_error:
        out["optin_error"] = optin_error
    out.update(_flags())
    return out


# ───────────────────────────── G2R 分流 ─────────────────────────────
def _evaluation_id(case_hash, now):
    return "g2r-%s-%s" % (now.replace("-", "").replace(":", ""), case_hash[7:15])


def _ask_jev(root, slug, environ, transport_factory, clock, deadline_s):
    """回 (answers|None, jev_reason, level, level_reason, extra)。任何失敗 → answers=None(= 沒有 Jev,no-op)。"""
    environ = os.environ if environ is None else environ
    try:
        level, level_reason = g2r_level(gate_mod.has_api_key(environ), gate_mod.load_optin(root))
    except JevError as exc:          # opt-in 檔壞了:不猜成 live;視同沒有 Jev
        return None, "optin_error", "off", "optin_error:%s" % exc, {"network": False}
    if not gate_mod.may_call(level):
        return None, level_reason, level, level_reason, {"network": False}
    spec_text = g2auto._read(g2auto.spec_path(root, slug)) or ""
    try:
        risk = policy.spec_risk_of(spec_text)
    except JevError:
        risk = None
    state = {"slug": slug, "declared_paths": g2auto.declared_paths(spec_text), "spec_risk": risk, "spec": spec_text}
    if len(spec_text) > policy.G2R_STATE_MAX_CHARS:
        return None, "packet_too_large", level, level_reason, {"network": False}
    hits = policy.privacy_scan(state)
    if hits:
        return None, "privacy_blocked", level, level_reason, {"network": False,
                                                             "privacy_hits": sorted({k for k, _ in hits})}
    request = build_request(state, policy.G2R_QUESTIONS)
    est = (len(json.dumps(request, ensure_ascii=False).encode("utf-8")) + 1) // 2 + 1
    store = StateStore(root)
    day = utc_day()
    budget = store.load_budget(day)
    breaker = store.load_breaker()
    try:
        factory = transport_factory or make_transport_factory(environ)
        try:
            transport = factory(deadline_s)
        except TypeError:
            transport = factory()
        outcome = policy.evaluate(transport, request, policy.G2R_QUESTIONS, clock, deadline_s=deadline_s,
                                  est_input_tokens=est, budget=budget, breaker=breaker, breaker_key="G2R")
    except Exception as exc:          # transport 建構失敗等:一律 no-op = 沒有 Jev
        outcome = policy.noop("unexpected:" + type(exc).__name__)
    store.save_budget(budget, day)
    store.save_breaker(breaker)
    extra = {"network": True, "jev_model": outcome.get("model"), "usage": outcome.get("usage")}
    if outcome["status"] != "ok":
        return None, outcome["reason"], level, level_reason, extra
    if level != "live":
        extra["jev_shadow_answers"] = g2auto.jev_minimal(outcome["answers"])
        return None, "level=%s(G2R 只在 mode: live 交給 agent)" % level, level, level_reason, extra
    return outcome["answers"], "ok", level, level_reason, extra


def run_g2r(root, slug, environ=None, transport_factory=None, clock=time.monotonic, deadline_s=None,
            record=True, now=None):
    """一次 G2R 分流。結果 append `.devflow/jev/g2r.jsonl`;gate 判定只在 devflow_gate.py write-g2-auto。"""
    deadline = policy.G2R_DEADLINE_S if deadline_s is None else min(policy.G2R_DEADLINE_S, float(deadline_s))
    now = now or _now()
    stage3 = g2auto.stage3_state(root, slug, environ)
    answers, jev_reason, level, level_reason, extra = _ask_jev(root, slug, environ, transport_factory, clock, deadline)
    case = g2auto.build_case(root, slug, jev=answers, environ=environ, stage3=stage3)
    routed = policy.route_g2(case)
    case_hash = policy.g2r_case_hash(case)
    evaluation_id = _evaluation_id(case_hash, now)
    entry = {"schema": G2R_SCHEMA, "gate": "G2R", "slug": slug, "recorded_at": now,
             "evaluation_id": evaluation_id, "level": level, "level_reason": level_reason,
             "jev_reason": jev_reason,
             "routed_by": ("jev:%s" % evaluation_id) if case["jev"] else g2auto.ROUTED_BY_NONE,
             "case": case, "case_hash": case_hash, "route": routed["route"], "reasons": routed["reasons"],
             "signals": routed["signals"], "auto_means": routed["auto_means"], "g2r_policy": routed["g2r_policy"],
             "jev_snapshot": g2auto.jev_snapshot(case["jev"]) if case["jev"] else None,
             "is_pass": False, "writes_verdict": False, "jev_role": "router_only"}
    entry.update(extra)
    entry.update(_flags())
    written = [_append_jsonl(root, G2R_LOG, entry)] if record else []
    return dict(entry, written=written)


# ───────────────────────────── G2 誤放行(只記錄)─────────────────────────────
def _g2r_auto_index(root):
    """g2r.jsonl 裡 route=AUTO 的 (slug, case_hash) → 最早那筆紀錄。"""
    rows, corrupt = _read_jsonl(os.path.join(root, G2R_LOG))
    index = {}
    for _, row in rows or []:
        if row.get("schema") == G2R_SCHEMA and row.get("route") == "AUTO":
            index.setdefault((row.get("slug"), row.get("case_hash")), row)
    return index, rows is not None, corrupt


def run_g2_misrelease_record(root, slug, case_hash, discovered_stage, discovered_via, evidence_ref,
                             g2_released_by, reported_by, now=None):
    """記一筆誤放行。case_hash 必須對到 g2r 的 AUTO 紀錄(reasons 從那筆抄,不收呼叫端給的)。"""
    index, _, _ = _g2r_auto_index(root)
    routed = index.get((slug, case_hash))
    if routed is None:
        raise JevError("g2r.jsonl 找不到 slug=%s case_hash=%s 的 AUTO 紀錄 —— 綁不到 G2R AUTO 的不算誤放行,不落盤"
                       % (slug, case_hash))
    rec = {"slug": slug, "case_hash": case_hash, "g2r_reasons": routed.get("reasons"),
           "discovered_stage": discovered_stage, "discovered_via": discovered_via, "evidence_ref": evidence_ref,
           "g2_released_by": g2_released_by, "reported_by": reported_by, "recorded_at": now or _now()}
    policy.validate_g2_misrelease(rec)
    existing, _ = _read_jsonl(os.path.join(root, G2M_LOG))
    key = (slug, case_hash, discovered_stage, discovered_via, evidence_ref)
    for _, row in existing or []:
        if (row.get("slug"), row.get("case_hash"), row.get("discovered_stage"), row.get("discovered_via"),
                row.get("evidence_ref")) == key:
            raise JevError("同一事件已記過(slug/case_hash/stage/via/evidence_ref 相同)—— 不重複落盤")
    entry = dict(rec, schema=G2M_SCHEMA, event="g2_misrelease", g2r_policy=routed.get("g2r_policy"),
                 counts_as_misrelease=g2_released_by == "fresh_agent_reviewer",
                 gate_effect="none", writes_verdict=False, auto_revert=False, spot_check=False, network=False,
                 **_flags())
    return dict(entry, written=[_append_jsonl(root, G2M_LOG, entry)])


def run_g2_agent_release(root, slug, case_hash, evidence_ref, reported_by, now=None):
    """記一筆「G2 由 fresh agent reviewer 放行」(誤放行率的分母)。只記錄,本身不放行任何東西。
    case_hash 必須對到 g2r 的 AUTO 紀錄;同一 (slug, case_hash) 只准記一次。"""
    index, _, _ = _g2r_auto_index(root)
    routed = index.get((slug, case_hash))
    if routed is None:
        raise JevError("g2r.jsonl 找不到 slug=%s case_hash=%s 的 AUTO 紀錄 —— 不是 G2R AUTO 的 case 不算 agent 放行,不落盤"
                       % (slug, case_hash))
    rec = {"slug": slug, "case_hash": case_hash, "g2r_reasons": routed.get("reasons"), "evidence_ref": evidence_ref,
           "reported_by": reported_by, "recorded_at": now or _now()}
    policy.validate_g2_agent_release(rec)
    existing, _ = _read_jsonl(os.path.join(root, G2M_RELEASE_LOG))
    for _, row in existing or []:
        if (row.get("slug"), row.get("case_hash")) == (slug, case_hash):
            raise JevError("slug=%s case_hash=%s 已記過 agent 放行 —— 不重複落盤" % (slug, case_hash))
    entry = dict(rec, schema=G2M_RELEASE_SCHEMA, event="g2_agent_release", g2_released_by="fresh_agent_reviewer",
                 evaluation_id=routed.get("evaluation_id"), routed_by=routed.get("routed_by"),
                 g2r_policy=routed.get("g2r_policy"), gate_effect="none",
                 writes_verdict=False, auto_revert=False, spot_check=False, network=False, **_flags())
    return dict(entry, written=[_append_jsonl(root, G2M_RELEASE_LOG, entry)])


def run_g2_misrelease_report(root):
    """誤放行率 = 誤放行數 ÷ agent 放行數(皆以相異 (slug, case_hash) 計)。放行數 0 → null + insufficient_data。
    不設門檻、不自動回滾、不擋任何東西。consistent=False → CLI exit 1。"""
    auto_index, routed_present, routed_corrupt = _g2r_auto_index(root)
    release_rows, release_corrupt = _read_jsonl(os.path.join(root, G2M_RELEASE_LOG))
    rows, corrupt = _read_jsonl(os.path.join(root, G2M_LOG))
    invalid_releases, orphan_releases, released = [], [], set()
    routed_of = {k: ("jev" if str(v.get("routed_by") or "").startswith("jev:") else "none")
                 for k, v in auto_index.items()}
    for n, row in release_rows or []:
        try:
            policy.validate_g2_agent_release({k: row.get(k) for k in policy.G2M_RELEASE_KEYS if k in row})
        except JevError as exc:
            invalid_releases.append({"line": n, "error": str(exc)})
            continue
        key = (row["slug"], row["case_hash"])
        if key not in auto_index:
            orphan_releases.append({"line": n, "slug": row["slug"], "case_hash": row["case_hash"]})
            continue
        released.add(key)
    invalid, orphans, unreleased, conflicts = [], [], [], []
    misreleased, counterfactual, by_stage = set(), set(), {s: 0 for s in policy.G2M_STAGES}
    for n, row in rows or []:
        try:
            policy.validate_g2_misrelease({k: row.get(k) for k in policy.G2M_RECORD_KEYS if k in row})
        except JevError as exc:
            invalid.append({"line": n, "error": str(exc)})
            continue
        key = (row["slug"], row["case_hash"])
        ref = {"line": n, "slug": row["slug"], "case_hash": row["case_hash"]}
        if key not in auto_index:
            orphans.append(ref)
            continue
        if row["g2_released_by"] == "fresh_agent_reviewer":
            if key not in released:                             # 說是 agent 放行的,卻沒有放行紀錄
                unreleased.append(ref)
                continue
            if key not in misreleased:
                by_stage[row["discovered_stage"]] += 1          # 以該 case 第一筆的發現階段計
            misreleased.add(key)
        elif key in released:                                   # 有 agent 放行紀錄,卻記成人放行
            conflicts.append(ref)
        else:
            counterfactual.add(key)
    problems = []
    if not routed_present:
        problems.append("沒有 .devflow/jev/g2r.jsonl:沒有任何 G2R 分流紀錄")
    if routed_corrupt:
        problems.append("g2r.jsonl 有壞行 %s" % routed_corrupt)
    if release_corrupt:
        problems.append("g2-agent-release.jsonl 有壞行 %s" % release_corrupt)
    if invalid_releases:
        problems.append("g2-agent-release.jsonl 有 %d 筆欄位不合法" % len(invalid_releases))
    if orphan_releases:
        problems.append("g2-agent-release.jsonl 有 %d 筆對不到 g2r AUTO 紀錄" % len(orphan_releases))
    if corrupt:
        problems.append("g2-misrelease.jsonl 有壞行 %s" % corrupt)
    if invalid:
        problems.append("g2-misrelease.jsonl 有 %d 筆欄位不合法" % len(invalid))
    if orphans:
        problems.append("g2-misrelease.jsonl 有 %d 筆對不到 g2r AUTO 紀錄" % len(orphans))
    if unreleased:
        problems.append("g2-misrelease.jsonl 有 %d 筆 g2_released_by=fresh_agent_reviewer 卻對不到 agent 放行紀錄"
                        % len(unreleased))
    if conflicts:
        problems.append("g2-misrelease.jsonl 有 %d 筆 g2_released_by=human,但該 case 有 agent 放行紀錄" % len(conflicts))
    auto_total = len(auto_index)
    layers = ("jev", "none")
    released_by_routed = {r: sum(1 for k in released if routed_of.get(k) == r) for r in layers}
    misreleased_by_routed = {r: sum(1 for k in misreleased if routed_of.get(k) == r) for r in layers}
    consistent = not (routed_corrupt or release_corrupt or invalid_releases or orphan_releases or corrupt or invalid
                      or orphans or unreleased or conflicts)
    if not consistent:
        withheld = "資料不一致,不計算(不是 0%):" + ";".join(problems)
        rate = {"rate": None, "status": "insufficient_data", "note": withheld}
        cf = {"rate": None, "status": "insufficient_data", "note": withheld}
    else:
        rate = policy.g2_misrelease_rate(len(misreleased), len(released))
        if release_rows is None:
            rate["note"] += "(沒有 .devflow/jev/g2-agent-release.jsonl)"
        cf = policy.g2_human_counterfactual_rate(len(counterfactual), auto_total)
        if not routed_present:
            cf["note"] += ";" + problems[0]
    out = {"schema": G2M_REPORT_SCHEMA, "gate": "G2R",
           "auto_total": auto_total, "agent_released": len(released),
           "misreleased": len(misreleased), "misreleased_by_stage": by_stage,
           "agent_released_by_routed": released_by_routed, "misreleased_by_routed": misreleased_by_routed,
           "misrelease_rate": rate["rate"], "rate_status": rate["status"], "rate_note": rate["note"],
           "human_counterfactual": len(counterfactual), "human_counterfactual_rate": cf["rate"],
           "human_counterfactual_status": cf["status"], "human_counterfactual_note": cf["note"],
           "problems": problems, "invalid_records": invalid, "orphan_records": orphans,
           "unreleased_agent_records": unreleased, "released_by_conflicts": conflicts,
           "invalid_releases": invalid_releases, "orphan_releases": orphan_releases, "consistent": consistent,
           "gate_effect": "none", "blocks_anything": False, "threshold": None, "auto_revert": False,
           "spot_check": False, "network": False}
    out.update(_flags())
    return out


# ───────────────────────────── CLI ─────────────────────────────
def _emit(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser():
    p = argparse.ArgumentParser(prog="devflow-jev.py", description="G2R 分流 + G2 誤放行紀錄")
    p.add_argument("--root", default=".", help="專案根(預設 .)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sg = sub.add_parser("g2r", help="G2R 分流(AUTO|HUMAN + 全部理由)→ .devflow/jev/g2r.jsonl;AUTO 不是通過")
    sg.add_argument("--slug", required=True)
    sg.add_argument("--deadline", type=float, default=None, help="秒;只能收緊 policy.G2R_DEADLINE_S")
    sg.add_argument("--no-record", action="store_true", help="只印結果,不 append g2r.jsonl")
    sm = sub.add_parser("g2-misrelease", help="G2 誤放行只記錄 + 誤放行率;不設門檻、不回滾、不擋")
    smsub = sm.add_subparsers(dest="g2m_cmd", required=True)
    smr = smsub.add_parser("record", help="append 一筆到 .devflow/jev/g2-misrelease.jsonl(綁 g2r AUTO 的 case_hash)")
    smr.add_argument("--slug", required=True)
    smr.add_argument("--case-hash", required=True, help="g2r 紀錄的 case_hash(sha256:…)")
    smr.add_argument("--stage", required=True, choices=tuple(policy.G2M_STAGES), help="發現階段")
    smr.add_argument("--via", required=True, choices=sorted({v for vs in policy.G2M_STAGES.values() for v in vs}),
                     help="發現來源事件(須屬於 --stage)")
    smr.add_argument("--evidence-ref", required=True, help="7-review 路徑／commit sha／PR 連結")
    smr.add_argument("--released-by", required=True, choices=policy.G2M_RELEASED_BY, help="當初 G2 實際由誰放行")
    smr.add_argument("--reported-by", required=True, help="human:<名> 或 agent:<id>;G3 階段只准 human")
    sma = smsub.add_parser("release", help="append 一筆「G2 由 fresh agent reviewer 放行」到 "
                           ".devflow/jev/g2-agent-release.jsonl(誤放行率分母;只記錄)")
    sma.add_argument("--slug", required=True)
    sma.add_argument("--case-hash", required=True, help="g2r AUTO 紀錄的 case_hash(sha256:…)")
    sma.add_argument("--evidence-ref", required=True, help="agent reviewer 報告路徑／PR 連結")
    sma.add_argument("--reported-by", required=True, help="human:<名> 或 agent:<id>")
    smsub.add_parser("report", help="誤放行率(分母 = agent 放行數);資料不足明講(不算成 0%%)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = os.path.abspath(args.root)
    try:
        if args.cmd == "status":
            _emit(run_status(root))
            return EXIT_OK
        if args.cmd == "g2r":
            _emit(run_g2r(root, args.slug, deadline_s=args.deadline, record=not args.no_record))
            return EXIT_OK
        if args.cmd == "g2-misrelease":
            if args.g2m_cmd == "record":
                _emit(run_g2_misrelease_record(root, args.slug, args.case_hash, args.stage, args.via, args.evidence_ref,
                                               args.released_by, args.reported_by))
                return EXIT_OK
            if args.g2m_cmd == "release":
                _emit(run_g2_agent_release(root, args.slug, args.case_hash, args.evidence_ref, args.reported_by))
                return EXIT_OK
            out = run_g2_misrelease_report(root)
            _emit(out)
            return EXIT_OK if out["consistent"] else EXIT_INCONSISTENT
    except JevError as exc:
        print("⛔ devflow-jev %s: %s" % (args.cmd, exc), file=sys.stderr)
        return EXIT_USAGE
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("⛔ devflow-jev %s: 輸入/檔案錯誤 %s: %s" % (args.cmd, type(exc).__name__, exc), file=sys.stderr)
        return EXIT_USAGE
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
