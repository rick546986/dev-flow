"""十三節測試對應:restart 恢復、incomplete attempt、多 worktree/多 attempt 併發、
derived ledger 可重建、parent attempt 關聯(交叉驗證)。"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
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
        with open(path) as f:
            lines = f.read().splitlines()
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
        with open(path) as f:
            lines = f.read().splitlines()
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
        with open(p1, "rb") as f:
            first = f.read()
        os.remove(p1)
        p2 = ledger.derive(self.run_dir)
        with open(p2, "rb") as f:
            self.assertEqual(f.read(), first)


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


class TestRepair(unittest.TestCase):
    """#103:壞 run 有出口。「非截尾＝損壞」語義不變 —— scan_corruption 的
    判定必須與 writer._read_complete_events 是否 raise 完全一致(否則 repair
    修的跟 reader 判的是兩套標準,drift 沒人抓得到)。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _write(self, *lines_bytes):
        """把給定的 bytes 片段依序寫進一個 attempts/att_x/events.jsonl,
        回傳 (run_dir, path)。片段本身已含換行與否,由呼叫端控制。"""
        run_dir = os.path.join(self.tmp.name, "run_r")
        d = os.path.join(run_dir, "attempts", "att_x")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "events.jsonl")
        with open(path, "wb") as f:
            for chunk in lines_bytes:
                f.write(chunk)
        return run_dir, path

    def test_scan_agrees_with_reader_raising_mid_file_bad_line(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        with self.assertRaises(ValueError):
            writer._read_complete_events(path)
        found = ledger.scan_corruption(run_dir)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["bad_line_no"], 2)
        self.assertEqual(found[0]["clean_events"], 1)

    def test_scan_agrees_with_reader_tolerating_last_line_truncated(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{"event_type":"attempt_comple')   # 截尾,無結尾換行
        events, partial = writer._read_complete_events(path)
        self.assertTrue(partial)
        self.assertEqual(len(events), 1)
        self.assertEqual(ledger.scan_corruption(run_dir), [])

    def test_scan_agrees_with_reader_tolerating_last_line_bad_json_no_newline(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{this is not json at all, no trailing newline')
        events, partial = writer._read_complete_events(path)
        self.assertTrue(partial)
        self.assertEqual(ledger.scan_corruption(run_dir), [])

    def test_scan_agrees_with_reader_single_bad_line_file_is_not_corrupt(self):
        # 只有一行、還壞掉:reader 判斷不出「只有一行的截尾」跟「唯一一行就是
        # 壞的」有什麼差別,一律當截尾容忍(i>=len(lines)-2 對單行檔恆成立)。
        # scan_corruption 用同一套規則,必須跟著不判為損壞 —— 這正是「非截尾
        # ＝損壞」語義在最短檔案上的邊界,兩邊標準不一致才是真正該抓的 drift。
        run_dir, path = self._write(b'{not valid\n')
        events, partial = writer._read_complete_events(path)
        self.assertTrue(partial)
        self.assertEqual(ledger.scan_corruption(run_dir), [])

    def test_bad_line_first_zero_clean_events(self):
        run_dir, path = self._write(
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        found = ledger.scan_corruption(run_dir)
        self.assertEqual(found[0]["clean_events"], 0)
        self.assertEqual(found[0]["corrupt_offset"], 0)
        result = ledger.repair_run(run_dir, apply=True)
        self.assertEqual(result["items"][0]["clean_events_kept"], 0)
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"")

    def test_dry_run_does_not_touch_files(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        with open(path, "rb") as f:
            before = f.read()
        result = ledger.repair_run(run_dir, apply=False)
        self.assertFalse(result["apply"])
        self.assertTrue(result["corrupt_found"])
        self.assertEqual(result["items"][0]["code"], "would_repair")
        with open(path, "rb") as f:
            self.assertEqual(f.read(), before)   # 完全沒動檔案
        self.assertEqual(sorted(os.listdir(os.path.dirname(path))),
                         ["events.jsonl"])         # 沒有隔離檔、沒有 tmp 殘留

    def test_apply_quarantines_full_bytes_and_keeps_clean_prefix(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        with open(path, "rb") as f:
            original = f.read()
        result = ledger.repair_run(run_dir, apply=True)
        self.assertTrue(result["apply"])
        item = result["items"][0]
        self.assertEqual(item["code"], "repaired")
        quarantine = item["quarantined_to"]
        self.assertTrue(os.path.basename(quarantine)
                        .startswith("events.jsonl.corrupt-"))
        with open(quarantine, "rb") as f:
            self.assertEqual(f.read(), original)   # 隔離檔含原始全部 bytes
        with open(path, "rb") as f:
            clean = f.read()
        self.assertEqual(clean, b'{"event_type":"attempt_started","seq":1}\n')
        events, partial = writer._read_complete_events(path)
        self.assertFalse(partial)
        self.assertEqual(len(events), 1)

    def test_apply_then_eventwriter_can_reopen_and_append(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        ledger.repair_run(run_dir, apply=True)
        d = os.path.dirname(path)
        w = writer.EventWriter(d)
        rec = w.append({"event_type": "tool_invoked"})
        w.close()
        self.assertEqual(rec["seq"], 2)   # 續號自壞行前的乾淨事件之後
        events, partial = writer._read_complete_events(path)
        self.assertFalse(partial)
        self.assertEqual([e["seq"] for e in events], [1, 2])

    def test_apply_skips_locked_file(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        lock = path + ".lock"
        open(lock, "w").close()
        with open(path, "rb") as f:
            before = f.read()
        result = ledger.repair_run(run_dir, apply=True)
        self.assertEqual(result["items"][0]["code"], "locked_skip")
        with open(path, "rb") as f:
            self.assertEqual(f.read(), before)     # 有鎖:原檔完全不動
        self.assertTrue(os.path.exists(lock))

    def test_dry_run_reports_locked_flag(self):
        run_dir, path = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{not valid\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        open(path + ".lock", "w").close()
        result = ledger.repair_run(run_dir, apply=False)
        self.assertTrue(result["items"][0]["locked"])

    def test_no_corruption_reports_clean_rc_style(self):
        run_dir, _ = self._write(
            b'{"event_type":"attempt_started","seq":1}\n',
            b'{"event_type":"attempt_completed","seq":2}\n')
        result = ledger.repair_run(run_dir, apply=False)
        self.assertFalse(result["corrupt_found"])
        self.assertEqual(result["items"], [])
        result2 = ledger.repair_run(run_dir, apply=True)
        self.assertFalse(result2["corrupt_found"])

    def test_nonexistent_run_dir_raises(self):
        with self.assertRaises(FileNotFoundError):
            ledger.repair_run(os.path.join(self.tmp.name, "no-such-run"))

    def test_repair_then_validate_clean_on_full_run_fixture(self):
        # 用完整合法 run(build_run)驗證 repair 不會誤傷別的檔案、修完後
        # validate_run 對整個 run 目錄乾淨(不只是被修的那一檔本身)。
        # ledger.validate_run 本身對中間壞行不是 exception-safe(那層 try/except
        # 是 CLI 層的事,#103 PR #110 已加在 devflow-obs.py/cmd_validate),
        # 這裡直接呼叫 validate_run 預期會 raise —— 這正是 repair 存在的理由。
        run_dir, t1_atts, att3 = build_run(self.tmp.name)
        self.assertEqual(ledger.validate_run(run_dir), [])
        path = os.path.join(run_dir, "attempts", t1_atts[0], "events.jsonl")
        with open(path, "rb") as f:
            raw = f.read()
        lines = raw.split(b"\n")
        # 在第一、二行之間插入一行壞 JSON(非截尾)
        broken = lines[0] + b"\n" + b"{not valid\n" + b"\n".join(lines[1:])
        with open(path, "wb") as f:
            f.write(broken)
        with self.assertRaises(ValueError):
            ledger.validate_run(run_dir)
        result = ledger.repair_run(run_dir, apply=True)
        self.assertEqual(result["items"][0]["code"], "repaired")
        self.assertEqual(ledger.validate_run(run_dir), [])
        w = writer.EventWriter(os.path.dirname(path))
        w.append({"event_type": "tool_invoked"})
        w.close()



class TestRepairConcurrentApply(unittest.TestCase):
    """r3-#103 minor:repair_run 的 --apply 原本沒有互斥,兩個行程同時 apply
    同一檔會用各自讀到的舊內容互踩——B 的 os.replace(path, quarantine) 蓋掉
    A 剛搬進去的隔離檔(quarantine 檔名靠微秒時戳,仍可能撞名),兩邊都回報
    repaired,但隔離檔最後只剩一份、內容不保證是「全部原始 bytes」。加上
    <file>.repair.lock(O_EXCL,同 events.jsonl.lock 同型)後,應恰一個
    repaired、另一個 concurrent_repair_skip。

    #103 fix-forward:原本用一個檔案柵欄讓兩邊「幾乎同時」進 repair_run,
    賭真的搶到同一個 O_EXCL syscall——這只是提高機率,不是保證。GitHub
    ubuntu runner 排程抖動夠大時,A 行程可能整個 repair_run(含 scan →
    拿鎖 → os.replace 兩次 → 還鎖)都跑完了,B 行程最上層、鎖外那次
    scan_corruption(run_dir) 才真正執行——此時檔案早已被 A 修好,B 看到
    的 plan 是空的,repair_run 對「從沒壞過」與「壞過但被別人搶先修好」
    回傳同一種 {"corrupt_found": False, "items": []},於是測試那行
    `r["items"][0]` 對 B 的結果 IndexError(這是回報粒度的落差,不是資料
    安全問題——O_EXCL 鎖 + 拿鎖後 fresh rescan 保證任何交錯下都恰好一份
    隔離檔、內容為原始全部 bytes,repair_run 本體不用修)。

    現在改用行程 A 自己的一次性 os.replace monkeypatch 卡住:A 進了
    repair_run、真的透過 O_EXCL 拿到 <file>.repair.lock、讀完待搬的乾淨
    內容之後,在第一次 os.replace(path, quarantine) 前卡住等父行程訊號
    (此時鎖仍握在 A 手上、磁碟上的檔案仍是原始壞內容未動)。父行程確認
    A 已卡住持鎖後才放行 B——B 這時最上層 scan_corruption 一定還看得到
    損壞(檔案尚未被 A 動過),進迴圈嘗試拿同一把鎖必定 FileExistsError,
    確定性拿到 concurrent_repair_skip;B 跑完後父行程才放行 A 完成剩下
    兩次 os.replace 並還鎖,確定性拿到 repaired。兩個真行程(不是
    threading)、真鎖、真檔案 I/O 全程保留,只是把「誰先誰後」從賭運氣
    改成明確排程,消除原本的 flaky 視窗。"""

    def test_two_processes_apply_concurrently_exactly_one_wins(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run_dir = os.path.join(tmp.name, "run_r")
        d = os.path.join(run_dir, "attempts", "att_x")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "events.jsonl")
        with open(path, "wb") as f:
            f.write(b'{"event_type":"attempt_started","seq":1}\n')
            f.write(b'{not valid\n')
            f.write(b'{"event_type":"attempt_completed","seq":2}\n')
        with open(path, "rb") as f:
            original = f.read()

        pkg_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        alive_a = os.path.join(tmp.name, "alive_a")
        alive_b = os.path.join(tmp.name, "alive_b")
        go_a = os.path.join(tmp.name, "go_a")
        go_b = os.path.join(tmp.name, "go_b")
        hold_a = os.path.join(tmp.name, "hold_a")     # A 已拿鎖、卡在 os.replace 前
        release_a = os.path.join(tmp.name, "release_a")  # 父行程確認 B 跑完後才放行 A
        out_a = os.path.join(tmp.name, "out_a.json")
        out_b = os.path.join(tmp.name, "out_b.json")

        script_a = (
            "import sys, os, json, time\n"
            f"sys.path.insert(0, {pkg_root!r})\n"
            "from devflow_obs import ledger\n"
            "_orig_replace = os.replace\n"
            "_paused = []\n"
            "def _paced_replace(src, dst):\n"
            f"    if src == {path!r} and not _paused:\n"
            "        _paused.append(1)\n"
            f"        open({hold_a!r}, 'w').close()\n"
            "        deadline = time.time() + 10\n"
            f"        while not os.path.exists({release_a!r}):\n"
            "            if time.time() > deadline:\n"
            "                raise RuntimeError('release_a 逾時未出現')\n"
            "            time.sleep(0.001)\n"
            "    return _orig_replace(src, dst)\n"
            "os.replace = _paced_replace\n"
            f"open({alive_a!r}, 'w').close()\n"
            f"while not os.path.exists({go_a!r}): time.sleep(0.001)\n"
            f"r = ledger.repair_run({run_dir!r}, apply=True)\n"
            f"with open({out_a!r}, 'w') as f: json.dump(r, f)\n"
        )
        script_b = (
            "import sys, os, json, time\n"
            f"sys.path.insert(0, {pkg_root!r})\n"
            "from devflow_obs import ledger\n"
            f"open({alive_b!r}, 'w').close()\n"
            f"while not os.path.exists({go_b!r}): time.sleep(0.001)\n"
            f"r = ledger.repair_run({run_dir!r}, apply=True)\n"
            f"with open({out_b!r}, 'w') as f: json.dump(r, f)\n"
        )

        pa = subprocess.Popen([sys.executable, "-c", script_a],
                              stderr=subprocess.PIPE, text=True)
        pb = subprocess.Popen([sys.executable, "-c", script_b],
                              stderr=subprocess.PIPE, text=True)

        def wait_or_fail(predicate, timeout, msg):
            deadline = time.time() + timeout
            while not predicate():
                if time.time() > deadline:
                    pa.kill()
                    pb.kill()
                    self.fail(msg)
                time.sleep(0.002)

        wait_or_fail(lambda: os.path.exists(alive_a) and os.path.exists(alive_b),
                     10, "子行程未能在時限內就緒(柵欄逾時)")
        open(go_a, "w").close()        # 只放行 A:A 先進 repair_run 真的拿到鎖
        wait_or_fail(lambda: os.path.exists(hold_a),
                     10, "A 未能在時限內拿鎖並卡在 os.replace 前")
        open(go_b, "w").close()        # A 卡住持鎖中才放行 B:B 必定搶輸
        wait_or_fail(lambda: os.path.exists(out_b),
                     10, "B 未能在時限內完成 repair_run(此時鎖應仍握在 A 手上)")
        open(release_a, "w").close()   # B 已確定拿到結果,才放行 A 完成搬檔
        _, err_a = pa.communicate(timeout=15)
        _, err_b = pb.communicate(timeout=15)
        self.assertEqual(pa.returncode, 0, err_a)
        self.assertEqual(pb.returncode, 0, err_b)

        with open(out_a) as f:
            ra = json.load(f)
        with open(out_b) as f:
            rb = json.load(f)
        codes = sorted(r["items"][0]["code"] for r in (ra, rb))
        self.assertEqual(codes, ["concurrent_repair_skip", "repaired"])

        quarantines = [n for n in os.listdir(d) if ".corrupt-" in n]
        self.assertEqual(len(quarantines), 1)
        with open(os.path.join(d, quarantines[0]), "rb") as f:
            self.assertEqual(f.read(), original)   # 隔離檔含原始全部 bytes

        events, partial = writer._read_complete_events(path)
        self.assertFalse(partial)
        self.assertEqual(len(events), 1)


if __name__ == "__main__":
    unittest.main()
