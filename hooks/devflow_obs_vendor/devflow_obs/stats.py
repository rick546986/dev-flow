"""跨 Feature 統計聚合(九節)+ Prompt 優化 Recommendation(十節)。

原則:
- 每個指標都帶 {"value","n","insufficient_sample"};n < min_n 一律標
  insufficient_sample,禁止拿 1~2 次失敗宣稱某 Prompt 較差。
- 「成功率」以 attempt_completed.result 為準(= 經 review 裁決後 coordinator
  記錄的結果),不以 FAIL 次數當模型錯誤率的唯一依據 —— rework/escalation/
  failure_category 分開呈現(八節)。
- 統計輸出**只提出 Recommendation,不自動改 Prompt**;改版走 registry 的
  人類核准(approved_by)流程。
- legacy Markdown 列只進 task 級指標,不冒充 attempt 級樣本。
"""
from . import ledger, legacy_md

CONFOUND_NOTE = ("解讀時必須區分七個混淆維度:模型能力 / Prompt 品質 / "
                 "Context Packet 品質 / Spec 品質 / 環境問題(ENV 分類)/ "
                 "Reviewer 嚴格度(見 reviewer_strictness_by_model)/ "
                 "Task 風險。單一維度的差異不足以歸因。")


def _metric(value, n, min_n):
    return {"value": value, "n": n, "insufficient_sample": n < min_n}


def _rate(num, n, min_n):
    return _metric((num / n) if n else None, n, min_n)


def _task_records_from_events(events):
    """單一 run 的事件 → per-task record + attempt 級樣本。"""
    tasks = {}
    attempts_meta = {}

    def task(task_id):
        return tasks.setdefault(task_id, {
            "attempts": [], "accepted": False, "rework_count": 0,
            "escalation_count": 0, "scope_violation": False,
            "test_integrity_violation": False, "source": "ledger"})

    for e in events:
        etype = e.get("event_type")
        tid = e.get("task_id")
        att = e.get("attempt_id")
        if etype in ("attempt_started", "attempt_completed") and att:
            meta = attempts_meta.setdefault(att, {
                "task_id": tid, "model": None, "prompt_key": None,
                "task_tags": [], "result": None})
            if tid:
                meta["task_id"] = tid
            if e.get("model"):
                meta["model"] = e["model"]
            if isinstance(e.get("prompt"), dict):
                p = e["prompt"]
                meta["prompt_key"] = f"{p.get('id')}@{p.get('version')}"
            # 6.3:task_tags(受控 enum,多選)為正式欄;舊檔 x_task_type
            # 僅讀取相容(1.x 遷移),新寫入不再產生
            if isinstance(e.get("task_tags"), list) and e["task_tags"]:
                meta["task_tags"] = list(e["task_tags"])
            elif e.get("x_task_type") and not meta["task_tags"]:
                meta["task_tags"] = [e["x_task_type"]]
            if etype == "attempt_completed":
                meta["result"] = e.get("result")
        if not tid:
            continue
        t = task(tid)
        if etype == "attempt_started" and att and att not in t["attempts"]:
            t["attempts"].append(att)
        elif etype == "task_accepted":
            t["accepted"] = True
        elif etype == "task_rework_requested":
            t["rework_count"] += 1
        elif etype == "task_escalated":
            t["escalation_count"] += 1
        elif etype == "mechanical_gate_completed" and e.get("result") == "FAIL":
            if e.get("violation") == "scope":
                t["scope_violation"] = True
            elif e.get("violation") == "test_integrity":
                t["test_integrity_violation"] = True
    for t in tasks.values():
        completed = [attempts_meta[a] for a in t["attempts"]
                     if attempts_meta.get(a, {}).get("result")]
        t["attempts_n"] = len(t["attempts"])
        t["first_pass"] = (t["accepted"] and len(t["attempts"]) == 1
                           and t["rework_count"] == 0
                           and t["escalation_count"] == 0
                           and all(m["result"] == "PASS" for m in completed))
    return tasks, attempts_meta


def _legacy_task_record(row):
    esc = max(len(row.get("escalations") or []) - 1, 0)
    rounds = row.get("rounds") or 1
    has_failure = row.get("failure_category") is not None
    return {
        "attempts_n": rounds, "accepted": True,
        "rework_count": max(rounds - 1 - esc, 0),
        "escalation_count": esc,
        "scope_violation": False, "test_integrity_violation": False,
        "first_pass": rounds == 1 and not has_failure,
        "source": row.get("source", "markdown-legacy"),
    }


def aggregate_events(events_by_run, legacy_rows=(), min_n=5):
    """events_by_run:{run_id: [event, ...]};legacy_rows:legacy_md 產出列。"""
    all_tasks, all_attempts = [], []
    failure_counts = {"SPEC": 0, "ENV": 0, "IMPL": 0, "UNKNOWN": 0}
    unattributed = {"scope": 0, "test_integrity": 0, "other": 0}
    runs_stage6_pass, runs_stage7_blocker = set(), set()
    layer_stats = {}
    reviewer_findings = {}

    for run_id, events in events_by_run.items():
        tasks, attempts_meta = _task_records_from_events(events)
        all_tasks.extend(tasks.values())
        all_attempts.extend(attempts_meta.values())
        for e in events:
            etype = e.get("event_type")
            # 分佈只數 attempt_completed 的分類(rework/escalated 事件重複攜帶
            # 同一次失敗的分類,不重複計)
            if etype == "attempt_completed" and e.get("failure_category"):
                failure_counts[e["failure_category"]] += 1
            elif etype == "mechanical_gate_completed" \
                    and e.get("result") == "FAIL" and not e.get("task_id"):
                v = e.get("violation") or "other"
                unattributed[v if v in unattributed else "other"] += 1
            elif etype == "stage_completed":
                if str(e.get("stage", "")).startswith("6-") \
                        and e.get("verdict") == "PASS":
                    runs_stage6_pass.add(run_id)
            elif etype == "finding_created" \
                    and str(e.get("stage", "")).startswith("7-") \
                    and e.get("severity") == "blocker":
                runs_stage7_blocker.add(run_id)
            elif etype == "verification_layer_completed":
                s = layer_stats.setdefault(e.get("layer", "unknown"),
                                           {"n": 0, "fail": 0,
                                            "status_counts": {}})
                # ID-10:status 為正式欄;舊 result(PASS|FAIL)為相容別名
                status = e.get("status")
                if status is None and e.get("result") in ("PASS", "FAIL"):
                    status = {"PASS": "pass", "FAIL": "fail"}[e["result"]]
                if status:
                    s["status_counts"][status] = \
                        s["status_counts"].get(status, 0) + 1
                if status in ("pass", "fail"):
                    s["n"] += 1
                    if status == "fail":
                        s["fail"] += 1
            elif etype == "review_completed" and e.get("model") \
                    and isinstance(e.get("findings_count"), int):
                r = reviewer_findings.setdefault(e["model"],
                                                 {"n": 0, "findings": 0})
                r["n"] += 1
                r["findings"] += e["findings_count"]

    legacy_tasks = [_legacy_task_record(r) for r in legacy_rows]
    tasks = all_tasks + legacy_tasks
    tasks_n = len(tasks)
    accepted = [t for t in tasks if t["accepted"]]

    def group_success(key_fn):
        """key_fn 回傳 None(跳過)、單一 key、或 key list(多選 tag =
        一 attempt 進多組)。"""
        groups = {}
        for m in all_attempts:
            if m["result"] not in ("PASS", "FAIL"):
                continue                                 # incomplete 不算樣本
            keys = key_fn(m)
            if keys is None:
                continue
            if isinstance(keys, str):
                keys = [keys]
            for key in keys:
                g = groups.setdefault(key, {"n": 0, "ok": 0})
                g["n"] += 1
                if m["result"] == "PASS":
                    g["ok"] += 1
        return {k: _rate(g["ok"], g["n"], min_n)
                for k, g in sorted(groups.items())}

    completed_attempts = [m for m in all_attempts
                          if m["result"] in ("PASS", "FAIL")]
    agg = {
        "meta": {
            "runs_n": len(events_by_run),
            "tasks_n": tasks_n,
            "attempts_n": len(completed_attempts),
            "legacy_tasks_n": len(legacy_tasks),
            "min_n": min_n,
            "unattributed_violations": unattributed,
        },
        "first_pass_success_rate": _rate(
            sum(1 for t in tasks if t["first_pass"]), tasks_n, min_n),
        "mean_attempts_to_acceptance": _metric(
            (sum(t["attempts_n"] for t in accepted) / len(accepted))
            if accepted else None, len(accepted), min_n),
        "rework_rate": _rate(
            sum(1 for t in tasks if t["rework_count"] > 0), tasks_n, min_n),
        "escalation_rate": _rate(
            sum(1 for t in tasks if t["escalation_count"] > 0), tasks_n, min_n),
        "failure_category_distribution": {
            "counts": failure_counts, "n": sum(failure_counts.values())},
        "scope_violation_rate": _rate(
            sum(1 for t in tasks if t["scope_violation"]), tasks_n, min_n),
        "test_integrity_violation_rate": _rate(
            sum(1 for t in tasks if t["test_integrity_violation"]),
            tasks_n, min_n),
        "success_by_model": group_success(lambda m: m["model"]),
        "success_by_prompt_version": group_success(lambda m: m["prompt_key"]),
        "success_by_model_task_tag": group_success(
            lambda m: [f"{m['model']}@{tag}"
                       for tag in (m["task_tags"] or ["unspecified"])]
            if m["model"] else None),
        "stage6_pass_stage7_blocker_rate": _rate(
            len(runs_stage6_pass & runs_stage7_blocker),
            len(runs_stage6_pass), min_n),
        "failure_rate_by_gauntlet_layer": {
            layer: dict(_rate(s["fail"], s["n"], min_n),
                        status_counts=dict(sorted(s["status_counts"].items())))
            for layer, s in sorted(layer_stats.items())},
        "reviewer_strictness_by_model": {
            model: {"mean_findings_per_review": r["findings"] / r["n"],
                    "n": r["n"]}
            for model, r in sorted(reviewer_findings.items())},
        "confound_note": CONFOUND_NOTE,
    }
    return agg


def aggregate_runs(run_dirs, legacy_paths=(), min_n=5):
    events_by_run = {}
    for rd in run_dirs:
        events = ledger.iter_run_events(rd)
        run_id = None
        for e in events:
            if e.get("run_id"):
                run_id = e["run_id"]
                break
        events_by_run[run_id or rd] = events
    legacy_rows = []
    for p in legacy_paths:
        legacy_rows.extend(legacy_md.parse_file(p))
    return aggregate_events(events_by_run, legacy_rows=legacy_rows, min_n=min_n)


def recommendations(agg, success_threshold=0.6):
    """十節閉環的機械部分:只挑「樣本足夠且成功率低於門檻」的 Prompt 組合出
    Recommendation;樣本不足一律列 skipped_insufficient_sample,不做主張。
    本函式**不寫任何檔案、不改任何 Prompt**;後續為人類流程:
    讀代表性 Attempts/Findings → 草擬改版 → 人類核准 → registry 升版 → A/B。"""
    recs, skipped = [], []
    for key, m in agg.get("success_by_prompt_version", {}).items():
        if m["value"] is None or m["value"] >= success_threshold:
            continue
        if m["insufficient_sample"]:
            skipped.append({"prompt": key, "n": m["n"],
                            "success_rate": m["value"],
                            "reason": "insufficient sample"})
        else:
            recs.append({
                "kind": "prompt_review",
                "prompt": key,
                "success_rate": m["value"],
                "n": m["n"],
                "action": "propose_revision",
                "requires_human_approval": True,
                "next_steps": "讀代表性 Attempts/Findings → 草擬改版 → "
                              "人類核准 → registry 升版(semver)→ A/B 比較",
            })
    return {"recommendations": recs,
            "skipped_insufficient_sample": skipped,
            "success_threshold": success_threshold,
            "note": "統計輸出只提出 Recommendation,不自動改 Prompt(十節)。"}
