"""G2 自動放行的機械判定(契約 §7「G2 審查者產生」「G2 轉人條件」「G2 provenance」)。

兩個呼叫端共用同一支判定,不各寫一份:
  - scripts/devflow_gate.py write-g2-auto   agent reviewer 放行的唯一寫入路徑(寫前全驗)
  - scripts/check-verdict-attestation.sh    事後掃 docs/dev/*/4-spec.md(手改頂欄繞過寫入器也會紅)

G2 放行要**同時**成立:
  (a) fresh-context agent reviewer 給 PASS(verdict_source: fresh_agent_reviewer、attested_by: agent:<id>);
  (b) 機械檢查全過(check-spec-gate.sh、_stage3_impl.py);
  (c) 沒有命中任何轉人條件(policy.route_g2 判 AUTO)。
Jev 只分流,不是 verdict source。沒有 Jev(沒 key／沒 opt-in／失敗／逾時／breaker open／budget 用完)= no-op
(ADR 0004 §2):不擋、不放寬,`routed_by: none`,只靠 (a)+(b),其餘轉人條件照判。
author ≠ approver:attested_by ≠ authored_by ≠ owner。格式比對是 tripwire,不是身份驗證。
"""
import os
import re
import subprocess
import sys

from . import JevError
from . import attestation, policy

# 全域退回人審開關:改成 False → write-g2-auto 一律拒寫,G2 全部回人審(已放行的 4-spec 不回頭打紅)。
# 不吃環境變數、不吃 CLI 旗標:要關就改這行(= 一個 commit,看得到誰關的)。
# 注意:拿掉 Jev key／opt-in 不會退回人審 —— 沒有 Jev 是 no-op(ADR 0004 §2),只少了分流。
G2_AUTO_LIVE = True
AUTO_SOURCE = "fresh_agent_reviewer"
HUMAN_SOURCES = ("human_attested", "owner_self_review")
G2_MODES = ("auto", "human")
G2R_LOG = os.path.join(".devflow", "jev", "g2r.jsonl")      # .devflow/ 已 gitignored
G2R_SCHEMA = "devflow-g2r/1"
_ACTOR_RE = re.compile(r"^(human|agent):(\S{1,64})$")
_ROUTED_BY_RE = re.compile(r"^jev:(g2r-[A-Za-z0-9._-]{1,80})$")
ROUTED_BY_NONE = "none"
_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_JEV_SNAPSHOT_RE = re.compile(r"^(AUTO_PASS|HUMAN_REVIEW|REQUEST_CHANGES) p=([0-9]*\.?[0-9]+) risk=([0-3])$")
_PATHS_LINE_RE = re.compile(r"^\s*-\s*Paths\s*[:：](.*)$")
_OC_ROW_RE = re.compile(r"^\|\s*OC-\d+\s*\|")


# ───────────────────────────── 讀 4-spec / 2-decision ─────────────────────────────
def _strip_fenced_and_comments(text):
    """``` 區塊與 <!-- --> 註解裡的字不算宣告(模板說明文字不能被當成真的欄位)。"""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return "\n".join(out)


def declared_paths(spec_text):
    """4-spec Diff Budget 的 `- Paths:` 行(逗號／頓號分隔)。沒有這行、空值、模板占位 `<…>` → []。"""
    for line in _strip_fenced_and_comments(spec_text).splitlines():
        m = _PATHS_LINE_RE.match(line)
        if not m:
            continue
        value = m.group(1)
        if re.search(r"<[^>]*>", value):     # 模板占位(整行還留著 <…>)= 沒宣告,不拆
            return []
        out = []
        for raw in re.split(r"[,，、]", value):
            item = raw.strip().strip("`").strip()
            if not item or "<" in item or item in ("—", "-", "n-a", "無"):
                continue
            out.append(item)
        return out
    return []


def owner_calls_unresolved(decision_text):
    """2-decision「## Owner Calls」節裡狀態欄沒有 ✅／✗(或含「待」)的 OC 列數。沒有 2-decision → 0。
    整列除了 OC 編號全空 = 模板占位,不算。"""
    if not decision_text:
        return 0
    body = re.search(r"^##\s*Owner Calls.*?\n(.*?)(?=^##\s|\Z)", decision_text, re.M | re.S)
    if not body:
        return 0
    count = 0
    for line in _strip_fenced_and_comments(body.group(1)).splitlines():
        if not _OC_ROW_RE.match(line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not any(cells[1:]):
            continue
        status = cells[-1]
        if not status or "待" in status or not re.search(r"✅|✗", status):
            count += 1
    return count


def _read(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def spec_path(root, slug):
    return os.path.join(root, "docs", "dev", slug, "4-spec.md")


# ───────────────────────────── 機械檢查(check-spec-gate + stage3)─────────────────────────────
def plugin_root(environ=None):
    """找 check-spec-gate.sh 與 hooks/_stage3_impl.py 所在的方法論根。找不到 → None(呼叫端 fail-closed)。"""
    environ = os.environ if environ is None else environ
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [environ.get(k, "") for k in ("DEVFLOW_PLUGIN", "DEVFLOW_ROOT", "CLAUDE_PLUGIN_ROOT")]
    cands.append(os.path.dirname(os.path.dirname(here)))       # scripts/devflow_jev/ → repo root
    for cand in cands:
        if cand and os.path.isfile(os.path.join(cand, "scripts", "check-spec-gate.sh")) \
                and os.path.isfile(os.path.join(cand, "hooks", "_stage3_impl.py")):
            return cand
    return None


def _run(argv, cwd):
    try:
        run = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, "", "%s: %s" % (type(exc).__name__, exc)
    return run.returncode, run.stdout, run.stderr


def stage3_state(root, slug, environ=None):
    """回 {"exit", "trigger", "g2_demo", "demo_verdict_required"}。跑不起來 → 視同需要 Demo verdict(fail-closed)。"""
    import json
    base = plugin_root(environ)
    if base is None:
        return {"exit": 2, "trigger": None, "g2_demo": None, "demo_verdict_required": True,
                "error": "找不到 hooks/_stage3_impl.py(設 DEVFLOW_PLUGIN)"}
    code, out, err = _run([sys.executable, os.path.join(base, "hooks", "_stage3_impl.py"), slug, "--root", root], root)
    try:
        data = json.loads(out) if out.strip() else {}
    except ValueError:
        data = {}
    trigger = data.get("trigger")
    required = code != 0 or trigger is True or data.get("g2_demo") != "PASS"
    return {"exit": code, "trigger": trigger, "g2_demo": data.get("g2_demo"), "demo_verdict_required": required,
            "error": (err.strip().splitlines() or [""])[-1] if code != 0 else ""}


def mechanical_checks(root, slug, environ=None):
    """跑 G2 機械檢查。回 {"ok", "results": [...], "digest": sha256:…}。任何一支跑不起來 = 不過。"""
    base = plugin_root(environ)
    results = []
    if base is None:
        results.append({"check": "plugin_root", "exit": 2, "ok": False,
                        "detail": "找不到 scripts/check-spec-gate.sh 與 hooks/_stage3_impl.py(設 DEVFLOW_PLUGIN)"})
    else:
        spec = spec_path(root, slug)
        code, out, err = _run(["bash", os.path.join(base, "scripts", "check-spec-gate.sh"), spec], root)
        results.append({"check": "check-spec-gate", "exit": code, "ok": code == 0,
                        "digest": policy.sha256_hex(out), "detail": "" if code == 0 else (out + err)[-400:]})
        st = stage3_state(root, slug, environ)
        results.append({"check": "stage3", "exit": st["exit"], "ok": st["exit"] == 0,
                        "g2_demo": st["g2_demo"], "trigger": st["trigger"], "detail": st.get("error", "")})
    digest = policy.sha256_hex(policy.canonical_json([{k: r.get(k) for k in ("check", "exit", "digest", "g2_demo")}
                                                      for r in results]))
    return {"ok": bool(results) and all(r["ok"] for r in results), "results": results, "digest": digest}


# ───────────────────────────── G2R case ─────────────────────────────
def jev_minimal(answers):
    """Jev answers → case 用的最小形狀(只留 route_g2 讀的欄位;頂欄快照可完整重建)。"""
    if answers is None:
        return None
    g2 = answers.get("g2_route") or {}
    probs = g2.get("probabilities") or {}
    risk = answers.get("risk") or {}
    return {"g2_route": {"choice": g2.get("choice"), "probabilities": {"AUTO_PASS": probs.get("AUTO_PASS")}},
            "risk": {"score": risk.get("score")}}


def build_case(root, slug, jev=None, environ=None, stage3=None):
    """從 docs/dev/<slug>/ 組 G2R case。spec 的 `- Risk:` 非法／空值 → JevError(不猜)。"""
    spec_text = _read(spec_path(root, slug))
    if spec_text is None:
        raise JevError("找不到 %s" % os.path.relpath(spec_path(root, slug), root))
    decision_text = _read(os.path.join(root, "docs", "dev", slug, "2-decision.md"))
    st = stage3 if stage3 is not None else stage3_state(root, slug, environ)
    authored = (attestation.parse_frontmatter(spec_text).get("authored_by") or "").strip()
    return {"slug": slug, "declared_paths": declared_paths(spec_text), "spec_risk": policy.spec_risk_of(spec_text),
            "owner_calls_unresolved": owner_calls_unresolved(decision_text),
            "demo_verdict_required": bool(st["demo_verdict_required"]),
            "authored_by_present": _actor(authored) is not None,
            "jev": jev_minimal(jev), "jev_status": "ok" if jev is not None else policy.G2R_NO_JEV}


def jev_snapshot(jev_min):
    """頂欄 g2r_jev 欄位值:`AUTO_PASS p=0.91 risk=1`。"""
    g2 = jev_min["g2_route"]
    return "%s p=%s risk=%s" % (g2["choice"], repr(float(g2["probabilities"]["AUTO_PASS"])), jev_min["risk"]["score"])


def parse_jev_snapshot(value):
    """`AUTO_PASS p=0.91 risk=1` → jev 最小形狀;空／`none` → None(沒有 Jev);形狀不對 → False。"""
    value = (value or "").strip()
    if value in ("", ROUTED_BY_NONE):
        return None
    m = _JEV_SNAPSHOT_RE.match(value)
    if not m:
        return False
    return {"g2_route": {"choice": m.group(1), "probabilities": {"AUTO_PASS": float(m.group(2))}},
            "risk": {"score": int(m.group(3))}}


def read_g2r_records(root):
    """`.devflow/jev/g2r.jsonl` 全部紀錄(不存在 → [];壞行略過但回報)。"""
    import json
    path = os.path.join(root, G2R_LOG)
    rows, corrupt = [], []
    if not os.path.isfile(path):
        return rows, corrupt
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                corrupt.append(n)
                continue
            if isinstance(row, dict) and row.get("schema") == G2R_SCHEMA:
                rows.append(row)
            else:
                corrupt.append(n)
    return rows, corrupt


def latest_g2r_record(root, slug):
    rows, _ = read_g2r_records(root)
    mine = [r for r in rows if r.get("slug") == slug]
    return mine[-1] if mine else None


# ───────────────────────────── 判定 ─────────────────────────────
def _actor(value):
    m = _ACTOR_RE.match((value or "").strip())
    return (m.group(1), m.group(2)) if m else None


def _same_actor(a, b):
    return bool(a) and bool(b) and a.strip().lower() == b.strip().lower()


def auto_release_problems(root, slug, fm, environ=None, g2r_record=None, require_record=False, mechanical=None):
    """G2 auto 放行不成立的理由(list[str]);空 = 可放行。fm = 4-spec 頂欄(attestation.parse_frontmatter)。

    - require_record=True(寫入器):一定要有 `.devflow/jev/g2r.jsonl` 對得上的 AUTO 紀錄。
    - require_record=False(事後掃描,.devflow 不進版控):由頂欄 g2r_jev 快照重建 case 重判;
      本機有紀錄檔時仍交叉比對。"""
    problems = []
    if require_record and not G2_AUTO_LIVE:
        problems.append("G2_AUTO_LIVE=False:G2 自動放行已全域關閉,交給人審")
    if (fm.get("verdict") or "").strip() != "PASS":
        problems.append("verdict 不是 PASS")
    source = (fm.get("verdict_source") or "").strip()
    if source != AUTO_SOURCE:
        problems.append("verdict_source=%r(agent 放行只收 %s)" % (source or None, AUTO_SOURCE))
    attested = (fm.get("attested_by") or "").strip()
    who = _actor(attested)
    if who is None or who[0] != "agent":
        problems.append("attested_by=%r 不是 agent:<id>" % (attested or None))
    elif who[1].lower().startswith("jev"):
        problems.append("attested_by 是 Jev —— Jev 只分流,不得當 reviewer")
    authored = (fm.get("authored_by") or "").strip()
    if _actor(authored) is None:
        problems.append("缺 authored_by(agent:<id> 或 human:<名>)—— 無法證明 author ≠ approver")
    elif _same_actor(authored, attested):
        problems.append("author == approver(authored_by = attested_by = %s)" % attested)
    owner = (fm.get("owner") or "").strip()
    if owner and who is not None and (_same_actor(owner, attested) or _same_actor(owner, who[1])):
        problems.append("approver 是本檔 owner(%s)" % owner)
    if (fm.get("g2_mode") or "").strip() != "auto":
        problems.append("g2_mode 不是 auto")
    routed = (fm.get("routed_by") or "").strip()
    m = _ROUTED_BY_RE.match(routed)
    evaluation_id = m.group(1) if m else None
    if not m and routed != ROUTED_BY_NONE:
        problems.append("routed_by=%r 不是 jev:<evaluation_id> 或 none" % (routed or None))
    if not _HASH_RE.match((fm.get("mechanical") or "").strip()):
        problems.append("mechanical 不是 sha256:<hex>(機械檢查摘要)")
    fm_case = (fm.get("g2r_case") or "").strip()
    if not _HASH_RE.match(fm_case):
        problems.append("g2r_case 不是 sha256:<hex>")
    jev_min = parse_jev_snapshot(fm.get("g2r_jev"))
    if jev_min is False:
        problems.append("g2r_jev 快照形狀不對(AUTO_PASS p=<0..1> risk=<0-3> 或 none)")
        jev_min = None
    if evaluation_id and jev_min is None:
        problems.append("routed_by 是 jev:… 卻沒有 g2r_jev 快照 —— Jev 分流結果無從重算")
    if routed == ROUTED_BY_NONE and jev_min is not None:
        problems.append("routed_by: none 卻帶 g2r_jev 快照 —— 分流來源自相矛盾")
    # 本機分流紀錄(有就交叉比對;寫入器一定要有)
    record = g2r_record
    if record is None:
        rows, _ = read_g2r_records(root)
        hits = [r for r in rows if r.get("slug") == slug and r.get("case_hash") == fm_case]
        record = hits[-1] if hits else None
    # 轉人條件:用現在的 spec／2-decision／stage3 + Jev 快照重算,不信頂欄自己寫的 route
    try:
        case = build_case(root, slug, jev=jev_min, environ=environ)
    except JevError as exc:
        problems.append("組 G2R case 失敗:%s" % exc)
        case = None
    if case is not None:
        routed_now = policy.route_g2(case)
        if routed_now["route"] != "AUTO":
            problems.append("命中交給人審條件:%s" % ";".join(routed_now["reasons"]))
        if fm_case and policy.g2r_case_hash(case) != fm_case:
            problems.append("g2r_case 與現在的 spec 重算結果不同(分流後 spec 改過 → 重跑 G2R)")
    if record is None:
        if require_record:
            problems.append("%s 找不到 slug=%s case_hash=%s 的分流紀錄 —— 先跑 devflow-jev.py g2r"
                            % (G2R_LOG.replace(os.sep, "/"), slug, fm_case or "?"))
    else:
        if record.get("route") != "AUTO":
            problems.append("G2R 紀錄判 %s(%s)" % (record.get("route"), ";".join(record.get("reasons") or [])))
        if record.get("routed_by") != routed:
            problems.append("routed_by=%r 與 G2R 紀錄的 %r 不符" % (routed or None, record.get("routed_by")))
    mech = mechanical if mechanical is not None else mechanical_checks(root, slug, environ)
    for r in mech["results"]:
        if not r["ok"]:
            problems.append("機械檢查 %s 沒過(exit %s)" % (r["check"], r["exit"]))
    return problems


def classify_gate_doc(stage, fm):
    """所有 gate 文件共用的出處規則。回 (kind, problems)。kind ∈ none|legacy|human|auto|bad。
    G1(2-decision)／G3(7-review)只收人寫的 verdict;g2_mode 只准出現在 4-spec。"""
    cls = attestation.classify(fm)
    if cls["label"] == "none":
        return "none", []
    src = (fm.get("verdict_source") or "").strip()
    by = (fm.get("attested_by") or "").strip()
    mode = (fm.get("g2_mode") or "").strip()
    problems = []
    if not src and not by and not mode:
        return "legacy", []
    if src not in attestation.SOURCES:
        return "bad", ["verdict_source=%r 不在 %s" % (src or None, "/".join(attestation.SOURCES))]
    if by.lower().startswith(("agent:jev", "jev")):
        return "bad", ["attested_by 指向 Jev —— Jev 不得寫 verdict"]
    if cls["label"] == "unverified":
        return "bad", cls["notes"][:1]
    if stage != "4-spec":
        if src == AUTO_SOURCE:
            problems.append("%s 只收人寫的 verdict(G1/G3 維持人審)—— verdict_source 不得是 %s" % (stage, AUTO_SOURCE))
        if mode:
            problems.append("g2_mode 只准出現在 4-spec(%s 有 g2_mode: %s)" % (stage, mode))
        return ("bad" if problems else "human"), problems
    if mode and mode not in G2_MODES:
        return "bad", ["g2_mode=%r 不在 auto|human" % mode]
    if src == AUTO_SOURCE or mode == "auto":
        return "auto", []          # 呼叫端再跑 auto_release_problems
    return "human", []
