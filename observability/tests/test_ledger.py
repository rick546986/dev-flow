"""十三節測試對應:restart 恢復、incomplete attempt、多 worktree/多 attempt 併發、
derived ledger 可重建、parent attempt 關聯(交叉驗證)。"""
import json
import os
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import evtools  # noqa: E402
from devflow_obs import ledger, writer  # noqa: E402

RUN = evtools.mkid("run", 1)


def build_run(root):
    """建一個 run:T-1 兩攻(haiku FAIL IMPL → 升 sonnet PASS),
    T-2 一攻 crash(attempt_started 後無下文)。回傳 run_dir 與 attempt ids。"""
    run_dir = os.path.join(root, ".devflow", "runs", RUN)
    fac = evtools.EventFactory(RUN)

    coord = [fac.ev("run_started", feature_slug="contract-expiry-reminder",
                    base_sha="abc1234", workspace="wt-a"),
             fac.ev("stage_started", stage="6-implementation")]
    t1_events, t1_atts = evtools.task_flow(fac, "T-1",
                                           [("haiku", "FAIL", "IMPL"),
                                            ("sonnet", "PASS", None)],
                                           att_start_n=1, rev_start_n=1)
    att3 = evtools.mkid("att", 3)
    t2_started = fac.ev("attempt_started", stage="6-implementation",
                        task_id="T-2", attempt_id=att3, agent_role="worker",
                        model="haiku", prompt=dict(evtools.PROMPT),
                        base_sha="abc1234")

    # coordinator 事件檔(run/stage/task lifecycle 由 coordinator 單獨寫)
    cw = writer.EventWriter(os.path.join(run_dir, "coordinator"))
    for e in coord:
        cw.append({k: v for k, v in e.items() if k != "seq"})
    # attempt 各寫自己的事件檔(四節:每個 Attempt 只寫自己的檔)
    per_attempt = {t1_atts[0]: [], t1_atts[1]: [], att3: [t2_started]}
    for e in t1_events:
        target = e.get("attempt_id")
        if e["event_type"].startswith(("attempt_", "candidate_")):
            per_attempt[target].append(e)
        elif e["event_type"].startswith("review_"):
            pass  # 下面寫進 review 檔
        else:
            cw.append({k: v for k, v in e.items() if k != "seq"})
    cw.close()
    for att, evs in per_attempt.items():
        aw = writer.EventWriter(os.path.join(run_dir, "attempts", att))
        for e in evs:
            aw.append({k: v for k, v in e.items() if k != "seq"})
        aw.close()
    # reviews
    rev_events = [e for e in t1_events if e["event_type"].startswith("review_")]
    by_rev = {}
    for e in rev_events:
        by_rev.setdefault(e["review_id"], []).append(e)
    for rev, evs in by_rev.items():
        rw = writer.EventWriter(os.path.join(run_dir, "reviews", rev))
        for e in evs:
            rw.append({k: v for k, v in e.items() if k != "seq"})
        rw.close()
    # 完成的 attempt 有 result.json(atomic finalize 標記);att3 沒有 → incomplete
    writer.atomic_write_json(os.path.join(run_dir, "attempts", t1_atts[0],
                                          "result.json"),
                             {"result": "FAIL", "failure_category": "IMPL"})
    writer.atomic_write_json(os.path.join(run_dir, "attempts", t1_atts[1],
                                          "result.json"), {"result": "PASS"})
    writer.atomic_write_json(os.path.join(run_dir, "manifest.json"),
                             {"schema": "devflow-run-manifest/1", "run_id": RUN,
                              "feature_slug": "contract-expiry-reminder",
                              "base_sha": "abc1234", "workspace": "wt-a",
                              "started": evtools.ts(0)})
    return run_dir, t1_atts, att3


class TestLoadAndIncomplete(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir, self.t1_atts, self.att3 = build_run(self.tmp.name)

    def test_incomplete_attempt_detected(self):
        self.assertEqual(ledger.incomplete_attempts(self.run_dir), [self.att3])

    def test_completed_attempts_not_flagged(self):
        incomplete = ledger.incomplete_attempts(self.run_dir)
        for att in self.t1_atts:
            self.assertNotIn(att, incomplete)

    def test_resume_state_survives_restart(self):
        # 全新 process 視角:只靠檔案系統重建進度(ID 皆可跨 restart)
        state = ledger.resume_state(self.run_dir)
        self.assertTrue(state["tasks"]["T-1"]["accepted"])
        self.assertEqual(state["tasks"]["T-1"]["attempt_count"], 2)
        self.assertIsNone(state["tasks"]["T-1"]["open_attempt"])
        self.assertFalse(state["tasks"]["T-2"]["accepted"])
        self.assertEqual(state["tasks"]["T-2"]["open_attempt"], self.att3)
        self.assertEqual(state["incomplete_attempts"], [self.att3])

    def test_partial_tail_tolerated(self):
        # 模擬 crash 截尾:最後一行寫到一半
        path = os.path.join(self.run_dir, "attempts", self.att3, "events.jsonl")
        with open(path, "a") as f:
            f.write('{"schema": "devflow-agent-ev')
        view = ledger.load_run(self.run_dir)
        self.assertTrue(view["attempts"][self.att3]["partial_tail"])
        self.assertEqual(len(view["attempts"][self.att3]["events"]), 1)

    def test_validate_run_clean(self):
        self.assertEqual(ledger.validate_run(self.run_dir), [])

    def test_validate_run_catches_broken_parent_ref(self):
        att2_dir = os.path.join(self.run_dir, "attempts", self.t1_atts[1])
        path = os.path.join(att2_dir, "events.jsonl")
        lines = open(path).read().splitlines()
        events = [json.loads(l) for l in lines]
        ghost = evtools.mkid("att", 99)
        for e in events:
            if "parent_attempt_id" in e:
                e["parent_attempt_id"] = ghost
        with open(path, "w") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
        errors = ledger.validate_run(self.run_dir)
        self.assertTrue(any(err["code"] == "broken_ref" for err in errors))


class TestDerive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir, self.t1_atts, self.att3 = build_run(self.tmp.name)

    def test_derive_merges_all_sources(self):
        path = ledger.derive(self.run_dir)
        lines = open(path).read().splitlines()
        view = ledger.load_run(self.run_dir)
        total = len(view["coordinator_events"])
        total += sum(len(a["events"]) for a in view["attempts"].values())
        total += sum(len(r["events"]) for r in view["reviews"].values())
        total += len(view["hook_events"])
        self.assertEqual(len(lines), total)
        # 時間序遞增
        stamps = [json.loads(l)["timestamp"] for l in lines]
        self.assertEqual(stamps, sorted(stamps))

    def test_derived_is_rebuildable_and_deterministic(self):
        p1 = ledger.derive(self.run_dir)
        first = open(p1, "rb").read()
        os.remove(p1)
        p2 = ledger.derive(self.run_dir)
        self.assertEqual(open(p2, "rb").read(), first)


class TestConcurrency(unittest.TestCase):
    """四節:多寫入者 = 各寫自己的檔;derive 合併後不掉事件、不壞檔。"""

    def test_two_attempts_append_concurrently(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run_dir, _, _ = build_run(tmp.name)
        n = 200
        atts = [evtools.mkid("att", 50), evtools.mkid("att", 51)]

        def work(att):
            fac = evtools.EventFactory(RUN)
            w = writer.EventWriter(os.path.join(run_dir, "attempts", att))
            for _ in range(n):
                w.append({k: v for k, v in fac.ev(
                    "tool_completed", stage="6-implementation",
                    attempt_id=att, tool_name="Bash", exit_code=0).items()
                    if k != "seq"})
            w.close()

        threads = [threading.Thread(target=work, args=(a,)) for a in atts]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        view = ledger.load_run(run_dir)
        for att in atts:
            self.assertEqual(len(view["attempts"][att]["events"]), n)
            self.assertEqual([e["seq"] for e in view["attempts"][att]["events"]],
                             list(range(1, n + 1)))
        ledger.derive(run_dir)  # 合併不炸

    def test_separate_worktrees_have_separate_run_dirs(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        wt_a = os.path.join(tmp.name, "wt-a")
        wt_b = os.path.join(tmp.name, "wt-b")
        run_a, _, _ = build_run(wt_a)
        run_b, _, _ = build_run(wt_b)
        self.assertNotEqual(run_a, run_b)
        self.assertEqual(ledger.validate_run(run_a), [])
        self.assertEqual(ledger.validate_run(run_b), [])


if __name__ == "__main__":
    unittest.main()
