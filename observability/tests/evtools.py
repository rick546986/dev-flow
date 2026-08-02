"""測試共用:事件建構 helper(非測試檔)。"""
import datetime

SHA256 = "sha256:" + "a" * 64
PROMPT = {"id": "stage6-worker", "version": "3.1.0", "hash": SHA256}
REVIEW_PROMPT = {"id": "stage6-reviewer", "version": "2.0.0", "hash": SHA256}

_BASE = datetime.datetime.fromisoformat("2026-08-02T01:00:00+08:00")


def mkid(kind_prefix, n):
    body = "01JG8C4V2M" + str(n).zfill(16)
    return f"{kind_prefix}_{body}"


def ts(i):
    return (_BASE + datetime.timedelta(seconds=i)).isoformat()


class EventFactory:
    """按時間序生產合法事件;seq 由呼叫端/writer 決定,這裡只給 timestamp。"""

    def __init__(self, run_id):
        self.run_id = run_id
        self.i = 0
        self.seq = 0

    def ev(self, event_type, writer="coordinator", **fields):
        self.i += 1
        self.seq += 1
        e = {
            "schema": "devflow-agent-event/1.1",
            "seq": self.seq,
            "timestamp": ts(self.i),
            "run_id": self.run_id,
            "event_type": event_type,
            "writer": writer,
        }
        e.update(fields)
        return e


def task_flow(fac, task_id, attempts, att_start_n, rev_start_n,
              prompt=None, task_tags=None):
    """產生一個 T 的完整事件流。

    attempts:[(model, result, failure_category|None), ...]
    規則:FAIL 後下一攻若換模型 → task_escalated;同模型 → task_rework_requested。
    最後一攻 PASS → task_accepted。
    回傳 (events, attempt_ids)。
    """
    prompt = prompt or PROMPT
    events, att_ids = [], []
    stage = "6-implementation"
    for j, (model, result, category) in enumerate(attempts):
        att = mkid("att", att_start_n + j)
        rev = mkid("rev", rev_start_n + j)
        att_ids.append(att)
        started = {"stage": stage, "task_id": task_id, "attempt_id": att,
                   "agent_role": "worker", "model": model,
                   "prompt": dict(prompt), "base_sha": "abc1234"}
        if j > 0:
            started["parent_attempt_id"] = att_ids[j - 1]
        if task_tags:
            started["task_tags"] = list(task_tags)
        events.append(fac.ev("attempt_started", **started))
        completed = {"stage": stage, "task_id": task_id, "attempt_id": att,
                     "agent_role": "worker", "model": model,
                     "prompt": dict(prompt), "result": result}
        if result == "FAIL":
            completed["failure_category"] = category
        events.append(fac.ev("attempt_completed", **completed))
        events.append(fac.ev("review_started", stage=stage, task_id=task_id,
                             review_id=rev, attempt_id=att, agent_role="reviewer",
                             model="sonnet", prompt=dict(REVIEW_PROMPT)))
        verdict = "PASS" if result == "PASS" else "FAIL"
        events.append(fac.ev("review_completed", stage=stage, task_id=task_id,
                             review_id=rev, attempt_id=att,
                             review_verdict=verdict, model="sonnet",
                             findings_count=0 if verdict == "PASS" else 2))
        if result == "FAIL" and j + 1 < len(attempts):
            next_model = attempts[j + 1][0]
            if next_model != model:
                events.append(fac.ev("task_escalated", stage=stage,
                                     task_id=task_id, attempt_id=att,
                                     from_model=model, to_model=next_model,
                                     failure_category=category))
            else:
                events.append(fac.ev("task_rework_requested", stage=stage,
                                     task_id=task_id, attempt_id=att,
                                     failure_category=category))
        if result == "PASS":
            events.append(fac.ev("task_accepted", stage=stage, task_id=task_id,
                                 attempt_id=att))
    return events, att_ids
