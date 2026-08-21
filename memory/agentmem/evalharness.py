"""Memory evaluation harness(§32)。

回答「這次改動讓記憶變好還是變壞」需要可重複的量測,不是逐次手動抽查。

**刻意做成小而確定性的 fixture**,不需要大型 benchmark 才能 merge:
dataset 自帶 seed(記憶內容)與 cases(查詢與期望),harness 在**隔離的
in-memory store + 暫存檔案樹**裡跑,所以同一份 dataset 每次跑結果相同 ——
它量的是**檢索引擎**,不是某個專案剛好累積了什麼記憶。
(`seed` 設為 null 的 dataset 則對 live memory 跑,用於現場診斷。)

九個指標:
  recall_at_5             期望命中落在前 5 名的比例(愈高愈好)
  mrr                     第一個期望命中的倒數排名平均(愈高愈好)
  current_truth_accuracy  CURRENT 題答對現值的比例(愈高愈好)
  stale_hit_rate          **已失效的值被當成當前真相回答的比例(愈低愈好)**
  wrong_branch_rate       回了不屬於當前 branch 的記憶的比例(愈低愈好)
  no_hit_precision        該回 NO_RELIABLE_MATCH 時真的回了的比例(愈高愈好)
  status_accuracy         retrieval_status 與期望相符的比例(愈高愈好;P0-4 契約)
  evidence_coverage       有答案的題目裡帶得出證據的比例(愈高愈好)
  context_size            startup context 字元數(愈小愈好,有上限)
  retrieval_latency_ms    平均延遲
"""
import json
import os
import shutil
import tempfile

from . import (context as context_mod, embedding, identity, query, retrieval,
               store as store_mod, sync, truth)

DEFAULT_DATASET = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "fixtures", "eval", "dataset.json")

LOWER_IS_BETTER = ("stale_hit_rate", "wrong_branch_rate", "context_size",
                   "retrieval_latency_ms")


def load_dataset(path=None):
    with open(path or DEFAULT_DATASET, encoding="utf-8") as stream:
        return json.load(stream)


def run(store=None, repo_root=None, workspace_id=None, snapshot=None,
        dataset_path=None):
    """跑一次評測。dataset 有 seed → 用隔離環境(確定性);否則對 live memory 跑。"""
    dataset = load_dataset(dataset_path)
    if dataset.get("seed"):
        return _run_isolated(dataset)
    if store is None:
        raise ValueError("dataset 無 seed 時必須提供 live store")
    return _score(dataset, store, repo_root, workspace_id, snapshot)


def _run_isolated(dataset):
    work = tempfile.mkdtemp(prefix="agentmem-eval-")
    try:
        root = os.path.join(work, "repo")
        os.makedirs(root)
        for rel, content in (dataset["seed"].get("files") or {}).items():
            target = os.path.join(root, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        project_id = dataset["seed"].get("project_id",
                                        "prj_" + "0" * 25 + "1")
        store = store_mod.Store.open(project_id, ":memory:")
        try:
            refs = _seed(store, root, dataset["seed"])
            snapshot = {"local_path": root, "os": "eval",
                        "branch": dataset["seed"].get("branch", "main"),
                        "head_sha": "0" * 40, "worktree": "main",
                        "dirty_files": dataset["seed"].get("dirty_files", [])}
            workspace_id = "wsp_" + "e" * 32
            store.register_workspace(workspace_id, snapshot)
            for rel, content in (dataset["seed"].get("mutate_files") or {}).items():
                target = os.path.join(root, rel)
                with open(target, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(content)
            return _score(dataset, store, root, workspace_id, snapshot, refs)
        finally:
            store.close()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _seed(store, root, seed):
    """把 seed 寫進 store,並回傳 ref → item_uid 的對照。"""
    refs = {}
    for record in seed.get("events") or []:
        event_id = store.add_event(
            record["kind"], record["title"], record.get("body", ""),
            occurred_at=record["occurred_at"], branch=record.get("branch"),
            signal=record.get("signal", "high"),
            file_paths=record.get("paths") or [])
        refs[record["ref"]] = "event:" + event_id
    for record in seed.get("facts") or []:
        fact_id = truth.record_fact(
            store, root, record["entity_type"], record["entity_key"],
            record["fact_key"], record["value"],
            dependencies=record.get("dependencies") or [],
            status=record.get("status", truth.VERIFIED),
            confidence=record.get("confidence", 0.95))
        refs[record["ref"]] = "fact:" + fact_id
    for record in seed.get("knowledge") or []:
        knowledge_id = store.upsert_knowledge({
            "kind": record["kind"], "key": record["key"],
            "title": record["title"], "body": record.get("body", ""),
            "authority": record["authority"],
            "status": record.get("status", "CONFIRMED"),
            "confidence": record.get("confidence", 0.9),
            "implemented": record.get("implemented")})
        refs[record["ref"]] = "knowledge:" + knowledge_id
    for record in seed.get("decisions") or []:
        decision_id = store.upsert_decision({
            "key": record["key"], "title": record["title"],
            "decision": record.get("decision", ""),
            "reason": record.get("reason", ""),
            "alternatives": record.get("alternatives", ""),
            "tradeoff": record.get("tradeoff", ""),
            "status": record.get("status", "ACCEPTED"),
            "evidence": record.get("evidence") or []})
        refs[record["ref"]] = "decision:" + decision_id
    for record in seed.get("skills") or []:
        skill_id = store.upsert_skill({
            "key": record["key"], "title": record["title"],
            "steps": record.get("steps") or [],
            "verification": record.get("verification", ""),
            "status": record.get("status", "VERIFIED")})
        refs[record["ref"]] = "skill:" + skill_id
    embedding.Embedder().reindex(store)
    # 評測直接把知識寫進 SQLite,不是 durable 鏡射。顯式蓋上「當前樹」的
    # 世代,不要靠 production 的 stamp-without-proof 逃生口。
    store.set_meta(sync.DURABLE_GENERATION_META, sync.durable_generation(root))
    return refs


def _score(dataset, store, root, workspace_id, snapshot, refs=None):
    refs = refs or {}
    embedder = embedding.Embedder()
    snapshot = snapshot or identity.workspace_snapshot(root)
    cases = []
    recall_hits = recall_total = 0
    rr_sum = rr_total = 0
    ct_hits = ct_total = 0
    stale_served = stale_total = 0
    wrong_branch = branch_total = 0
    nohit_hits = nohit_total = 0
    status_hits = status_total = 0
    evidence_hits = evidence_total = 0
    latencies = []

    for case in dataset["cases"]:
        answer = query.execute(store, root, case["query"], workspace_id,
                               snapshot, embedder, limit=5,
                               branch=case.get("branch"))
        latencies.append(answer.get("latency_ms", 0.0))
        record = {"id": case["id"], "query": case["query"],
                  "language": case.get("language", "en"),
                  "expect_kind": case.get("expect_kind"),
                  "got_kind": answer["primary_intent"],
                  "expect_status": case.get("expect_status"),
                  "got_status": answer["retrieval_status"],
                  "status": answer["retrieval_status"], "problems": []}

        if case.get("expect_kind") and \
                answer["primary_intent"] != case["expect_kind"]:
            record["problems"].append("意圖分類:期望 {0} 實得 {1}".format(
                case["expect_kind"], answer["primary_intent"]))

        expected = [refs.get(r, r) for r in (case.get("expect_refs") or [])]
        if expected:
            recall_total += 1
            rr_total += 1
            got = [_uid_of(hit) for hit in answer["results"]]
            rank = next((i + 1 for i, uid in enumerate(got) if uid in expected),
                        None)
            if rank is not None and rank <= 5:
                recall_hits += 1
            if rank:
                rr_sum += 1.0 / rank
            else:
                record["problems"].append("期望命中不在前 5")
            record["rank"] = rank

        if case.get("expect_value") is not None:
            ct_total += 1
            current = answer.get("current_truth")
            if current and current["value"] == case["expect_value"]:
                ct_hits += 1
            else:
                record["problems"].append("current truth 值不符")

        if case.get("expect_stale"):
            stale_total += 1
            current = answer.get("current_truth")
            if current and current.get("fast_path"):
                stale_served += 1
                record["problems"].append("失效的值被當成當前真相回答")

        if case.get("expect_branch_absent"):
            branch_total += 1
            titles = " ".join(str(hit.get("title", "")) for hit in answer["results"])
            if case["expect_branch_absent"] in titles:
                wrong_branch += 1
                record["problems"].append("回了不屬於當前 branch 的記憶")

        expected_status = case.get("expect_status")
        if expected_status:
            if expected_status not in query.RETRIEVAL_STATUSES:
                record["problems"].append(
                    "dataset 寫了不存在的 status:{0}".format(expected_status))
            status_total += 1
            if answer["retrieval_status"] == expected_status:
                status_hits += 1
            else:
                record["problems"].append(
                    "status 期望 {0} 實得 {1}".format(
                        expected_status, answer["retrieval_status"]))

        if expected_status == retrieval.NO_RELIABLE_MATCH:
            nohit_total += 1
            if answer["retrieval_status"] == retrieval.NO_RELIABLE_MATCH:
                nohit_hits += 1
            else:
                record["problems"].append("該回 NO_RELIABLE_MATCH 卻給了答案")

        if answer["retrieval_status"] == retrieval.OK:
            evidence_total += 1
            has_evidence = bool(answer["evidence"]) or any(
                hit.get("paths") or hit.get("evidence") or hit.get("channels")
                for hit in answer["results"])
            if has_evidence:
                evidence_hits += 1
            else:
                record["problems"].append("有答案但沒有任何證據")

        record["passed"] = not record["problems"]
        cases.append(record)

    built = context_mod.build(store, root, workspace_id, snapshot)
    metrics = {
        "recall_at_5": _ratio(recall_hits, recall_total),
        "mrr": round(rr_sum / rr_total, 4) if rr_total else 1.0,
        "current_truth_accuracy": _ratio(ct_hits, ct_total),
        "stale_hit_rate": _ratio(stale_served, stale_total, default=0.0),
        "wrong_branch_rate": _ratio(wrong_branch, branch_total, default=0.0),
        "no_hit_precision": _ratio(nohit_hits, nohit_total),
        "status_accuracy": _ratio(status_hits, status_total),
        "evidence_coverage": _ratio(evidence_hits, evidence_total),
        "context_size": built["size"],
        "retrieval_latency_ms": round(
            sum(latencies) / len(latencies), 3) if latencies else 0.0,
    }
    thresholds = dataset.get("thresholds") or {}
    violations = []
    for name, bound in sorted(thresholds.items()):
        value = metrics.get(name)
        if value is None:
            violations.append("threshold {0} 沒有對應指標".format(name))
        elif name in LOWER_IS_BETTER:
            if value > bound:
                violations.append("{0}={1} > 上限 {2}".format(name, value, bound))
        elif value < bound:
            violations.append("{0}={1} < 下限 {2}".format(name, value, bound))

    by_language = {}
    for record in cases:
        bucket = by_language.setdefault(record["language"],
                                        {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += 1 if record["passed"] else 0

    return {
        "dataset": dataset.get("name", "unnamed"),
        "cases": cases,
        "case_count": len(cases),
        "cases_passed": sum(1 for c in cases if c["passed"]),
        "by_language": by_language,
        "metrics": metrics,
        "thresholds": thresholds,
        "violations": violations,
        "passed": not violations and all(c["passed"] for c in cases),
    }


def _uid_of(hit):
    item_type = hit.get("item_type")
    item_id = hit.get("item_id")
    if item_type and item_id:
        return "{0}:{1}".format(item_type, item_id)
    return None


def _ratio(hits, total, default=1.0):
    return round(hits / float(total), 4) if total else default


def render(report):
    print("dataset: {0}  cases: {1}/{2} passed".format(
        report["dataset"], report["cases_passed"], report["case_count"]))
    for language, bucket in sorted(report["by_language"].items()):
        print("  語言 {0}:{1}/{2}".format(language, bucket["passed"],
                                          bucket["total"]))
    print("  ── metrics ──")
    for name, value in sorted(report["metrics"].items()):
        direction = "↓" if name in LOWER_IS_BETTER else "↑"
        bound = report["thresholds"].get(name)
        suffix = "  (門檻 {0})".format(bound) if bound is not None else ""
        print("  {0} {1}: {2}{3}".format(direction, name, value, suffix))
    for record in report["cases"]:
        if not record["passed"]:
            print("  ✗ {0}:{1}".format(record["id"],
                                       "; ".join(record["problems"])))
    for violation in report["violations"]:
        print("  ⛔ " + violation)
    print("  verdict: {0}".format("PASS" if report["passed"] else "FAIL"))
