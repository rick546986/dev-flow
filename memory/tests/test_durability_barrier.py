"""耐久性屏障:**不得在耐久性真正建立之前宣稱它已經建立**。

三個缺陷同一個病灶 —— 有人在「還沒真的寫進 `.dev-flow/`」的時候就把狀態
推進到「已經寫進去了」。它們都不會讓任何測試變紅,因為 local DB 自己是
自洽的;要到**另一台機器 clone 後 rebuild** 才會發現記憶不見了。

    ① devtalk.correct()  舊知識在 consolidation 成功**之前**就被標 SUPERSEDED。
       更正被守衛拒絕、或 session 被 abort 時,舊值已經不是現況了,新值又從來
       沒進 Git —— 這個 key 在 local 變成「沒有現況」,但 durable 側還是舊值。
       同一個問題答什麼,取決於這台機器有沒有 rebuild 過。

    ② revision 的 mark_durable  在 `durable.append_events()` **之前**執行,
       而且不分「這筆到底有沒有被寫出去」。被敏感守衛擋掉的 revision 也一樣
       被標成 durable=1 —— 它從此不再是 pending,永遠不會再被嘗試,
       而 `.dev-flow/` 裡從來沒有它。這是**靜默且永久**的失憶。

    ③ 寫檔失敗(磁碟滿、conflict 標記、路徑守衛)時,②的順序讓 revision
       先被標 durable 才去寫檔 —— 寫檔拋出例外,狀態卻已經前進了。

驗的方式一律是「破壞性重建」:刪掉 local,只從 `.dev-flow/` 重建,
看還記不記得。local DB 自己說什麼不算證據。
"""
import json
import os
import shutil
from unittest import mock

from memtools import MemoryCase
from agentmem import (devtalk, durable, identity, lineage, query,
                      session as session_mod, store as store_mod, sync,
                      truth)


class CorrectionDoesNotSupersedeBeforeConsolidationTest(MemoryCase):
    """①`correct()` 不得在 consolidation 成功前動到現況。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("registration 語意")
        first = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "registration", "title": "registration = embryo-level",
             "body": "每個 embryo 一筆"}, "domain_expert")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)

    def current_rows(self, statuses=("CANDIDATE", "CONFIRMED", "CONFLICT")):
        return self.store.knowledge(kind="domain", key="registration",
                                    statuses=statuses, limit=10)

    def test_old_knowledge_is_still_current_until_checkpoint(self):
        """correct() 之後、checkpoint 之前,現況仍然是舊值。

        新值此刻只是候選 —— 候選不是現況。如果 correct() 就把舊值下架,
        中間這段時間這個 key 沒有任何現況可回答,而使用者根本沒被告知
        「你的更正還沒生效」。
        """
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level",
                        reason="使用者更正")
        rows = self.current_rows()
        self.assertEqual(len(rows), 1, "更正尚未固化,現況應該只有舊值一筆")
        self.assertIn("embryo-level", rows[0]["title"])
        self.assertEqual(rows[0]["status"], "CONFIRMED",
                         "consolidation 還沒成功,舊值不得被標 SUPERSEDED")

    def test_rejected_correction_does_not_erase_the_previous_truth(self):
        """更正被敏感守衛擋掉時,舊值必須還在 —— 不能兩邊都沒有。"""
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level",
                        body='連線用 DB_PASSWORD = "hunter2000"',
                        reason="順手補連線資訊")
        result = devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(result["promoted"], 0, "含 secret 的候選不得固化")

        rows = self.current_rows()
        self.assertEqual(len(rows), 1,
                         "更正沒有成功,現況必須維持舊值一筆(不得變成 0 筆)")
        self.assertEqual(rows[0]["status"], "CONFIRMED")
        self.assertIn("embryo-level", rows[0]["title"])

    def test_rejected_correction_keeps_local_and_durable_in_agreement(self):
        """被拒絕的更正之後,local 與 durable 必須回答同一件事。

        這是①最惡性的後果:durable 側還是舊值,local 側卻沒有現況 ——
        「這個詞現在是什麼意思」的答案取決於你這台機器有沒有 rebuild 過。
        """
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level",
                        body='API_KEY = "sk-live-abcdefghijklmnopqrst"',
                        reason="更正")
        devtalk.checkpoint(self.store, self.repo, self.session)

        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        self.store.register_workspace(workspace, snapshot)
        before = query.execute(self.store, self.repo, "registration 是什麼",
                               workspace, snapshot=snapshot)
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        fresh.register_workspace(workspace, snapshot)
        after = query.execute(fresh, self.repo, "registration 是什麼",
                              workspace, snapshot=snapshot)

        titles_before = [r["title"] for r in before["results"]]
        titles_after = [r["title"] for r in after["results"]]
        self.assertTrue(
            any("embryo-level" in t for t in titles_before),
            "更正失敗後,local 仍應答得出舊值(不是兩邊都空 —— 那樣這條斷言"
            "會**空過**,測不到任何東西)")
        self.assertEqual(
            titles_before, titles_after,
            "rebuild 前後答案不同 = local 與 durable 對同一個 key 說法不一致")

    def test_aborted_session_leaves_the_previous_truth_intact(self):
        """使用者反悔(abort)時,舊值必須完好無損。"""
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level", reason="也許吧")
        devtalk.abort(self.store, self.session, reason="使用者說先不要改")

        rows = self.current_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "CONFIRMED")
        self.assertIn("embryo-level", rows[0]["title"])

    def test_successful_correction_still_supersedes(self):
        """回歸:成功固化時,supersede 與 lineage 一切照舊。"""
        devtalk.correct(self.store, self.session, "domain", "registration",
                        "registration = customer-level",
                        body="一個客戶在 submission 內的送檢紀錄",
                        reason="使用者更正:永遠代表一個客戶")
        result = devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(result["promoted"], 1)

        current = self.current_rows(statuses=("CONFIRMED",))
        self.assertEqual(len(current), 1)
        self.assertIn("customer-level", current[0]["title"])
        superseded = self.current_rows(statuses=("SUPERSEDED",))
        self.assertEqual(len(superseded), 1)
        self.assertIn("embryo-level", superseded[0]["title"])

        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == lineage.KNOWLEDGE_CORRECTED]
        self.assertEqual(len(revisions), 1)
        self.assertIn("embryo-level", revisions[0]["previous_title"])
        self.assertIn("customer-level", revisions[0]["new_title"])
        self.assertEqual(revisions[0]["previous_status"], "SUPERSEDED")


class RevisionMarkedDurableOnlyWhenWrittenTest(MemoryCase):
    """②③只有**真的寫進 `.dev-flow/`** 的 revision 才能標 durable。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.store.register_workspace(
            self.workspace, identity.workspace_snapshot(self.repo))

    def seed_fact(self, value):
        from memtools import commit_all, write
        write(self.repo, "src/app.py", "VALUE = 1\n")
        commit_all(self.repo, "seed fact dep")
        fact_id = self.store.upsert_fact({
            "entity_type": "module", "entity_key": "app",
            "fact_key": "value", "value": value, "status": truth.VERIFIED,
            "confidence": 0.9, "recorded_at": store_mod.utc_now(),
            "verified_at": store_mod.utc_now(), "verification_count": 1,
            "source_type": "code", "dependencies": ["src/app.py"],
            "fingerprints": truth.fingerprints_for(self.repo, ["src/app.py"]),
            "durable": True})
        sync.promote_entity_facts(self.repo, self.store, "module", "app")
        return fact_id

    def pending_ids(self):
        return [row["revision_id"] for row in lineage.pending(self.store)]

    def test_gate_rejected_revision_stays_pending(self):
        """被敏感守衛擋掉的 revision **不得**被標 durable。

        標了就再也不是 pending:它永遠不會被重試,而 `.dev-flow/` 裡從來沒有
        它。內容修好之後也救不回來 —— 這是靜默且永久的失憶。
        """
        fact_id = self.seed_fact('token = "ghp_0123456789abcdefghijABCDEFGHIJ01234567"')
        truth.reverify(self.store, self.repo, fact_id, self.workspace,
                       "token 已改為由 env 注入", reason="移除硬編碼")
        pending_before = self.pending_ids()
        self.assertEqual(len(pending_before), 1, "reverify 應留下一筆 pending")

        result = sync.consolidate(self.repo, self.store)

        blob = "\n".join(json.dumps(e, ensure_ascii=False)
                         for e in durable.iter_events(self.repo))
        self.assertNotIn("ghp_0123456789", blob, "secret 不得寫進 Git")
        self.assertEqual(result["revisions"], 0)
        self.assertEqual(
            self.pending_ids(), pending_before,
            "沒寫進 .dev-flow 的 revision 必須留在 pending,不得標 durable")

    def test_write_failure_leaves_every_revision_pending(self):
        """`append_events` 失敗時,一筆都不准標 durable。"""
        fact_id = self.seed_fact("value = 1")
        truth.reverify(self.store, self.repo, fact_id, self.workspace,
                       "value = 2", reason="改了預設值")
        pending_before = self.pending_ids()
        self.assertEqual(len(pending_before), 1)

        original = durable.append_events

        def boom(*args, **kwargs):
            raise IOError("模擬寫檔失敗(磁碟滿 / 路徑守衛)")

        durable.append_events = boom
        try:
            with self.assertRaises(IOError):
                sync.consolidate(self.repo, self.store)
        finally:
            durable.append_events = original

        self.assertEqual(
            self.pending_ids(), pending_before,
            "寫檔失敗後 revision 必須還是 pending,才有機會重試")

    def test_retry_after_failure_actually_writes_it(self):
        """失敗後重跑必須真的補寫進去 —— pending 不是墳墓。"""
        fact_id = self.seed_fact("value = 1")
        truth.reverify(self.store, self.repo, fact_id, self.workspace,
                       "value = 2", reason="改了預設值")

        original = durable.append_events
        durable.append_events = lambda *a, **k: (_ for _ in ()).throw(
            IOError("第一次失敗"))
        try:
            with self.assertRaises(IOError):
                sync.consolidate(self.repo, self.store)
        finally:
            durable.append_events = original

        result = sync.consolidate(self.repo, self.store)
        self.assertEqual(result["revisions"], 1)
        self.assertEqual(self.pending_ids(), [], "補寫成功後才清 pending")
        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == lineage.FACT_SUPERSEDED]
        self.assertEqual(len(revisions), 1)
        self.assertIn("value = 1", revisions[0]["previous_value"])

    def test_durable_ref_points_at_the_file_that_holds_it(self):
        """標 durable 時要記下**落在哪個檔** —— 「已耐久」必須可稽核。"""
        fact_id = self.seed_fact("value = 1")
        truth.reverify(self.store, self.repo, fact_id, self.workspace,
                       "value = 2", reason="改了預設值")
        sync.consolidate(self.repo, self.store)

        rows = list(self.store.conn.execute(
            "SELECT durable, durable_ref FROM revisions WHERE project_id=?",
            (self.project_id,)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["durable"], 1)
        ref = rows[0]["durable_ref"]
        self.assertTrue(ref, "durable_ref 不得為空")
        self.assertTrue(ref.startswith(".dev-flow/events/"), ref)
        self.assertFalse(os.path.isabs(ref), "durable_ref 不得是絕對路徑")
        self.assertTrue(os.path.isfile(os.path.join(self.repo, ref)),
                        "durable_ref 指的檔案必須真的存在")

    def test_rejected_revision_is_visible_not_silent(self):
        """被拒絕的 revision 要**看得到理由**,不是無聲消失。"""
        fact_id = self.seed_fact('password = "hunter2000-not-a-placeholder"')
        truth.reverify(self.store, self.repo, fact_id, self.workspace,
                       "改為由 secret manager 提供", reason="移除硬編碼")
        result = sync.consolidate(self.repo, self.store)
        kinds = [r["target_kind"] for r in result["rejected"]]
        self.assertIn(lineage.FACT_SUPERSEDED, kinds)
        reasons = [r for entry in result["rejected"]
                   for r in entry["reasons"]]
        self.assertTrue(reasons, "拒絕必須帶理由")


class InLoopRevisionIsRetriableTest(MemoryCase):
    """consolidate 當下才產生的 revision,也要走同一條 pending → 寫檔 → 標記。

    否則「用哪條路更正」會決定失敗時救不救得回來:`truth.reverify()` 產生的
    revision 有 pending 表撐著,`correct()` 產生的卻只活在記憶體裡。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("registration 語意")

    def test_knowledge_revision_survives_a_write_failure(self):
        first = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "registration", "title": "v1 embryo-level"},
            "domain_expert")
        devtalk.confirm(self.store, first)
        devtalk.checkpoint(self.store, self.repo, self.session)

        devtalk.correct(self.store, self.session, "domain", "registration",
                        "v2 customer-level", reason="使用者更正")

        original = durable.append_events
        durable.append_events = lambda *a, **k: (_ for _ in ()).throw(
            IOError("寫檔失敗"))
        try:
            with self.assertRaises(IOError):
                devtalk.checkpoint(self.store, self.repo, self.session)
        finally:
            durable.append_events = original

        # 重跑要補得回來:lineage 不能因為一次寫檔失敗就永久消失。
        devtalk.checkpoint(self.store, self.repo, self.session)
        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == lineage.KNOWLEDGE_CORRECTED]
        self.assertEqual(len(revisions), 1,
                         "重跑後應補寫且只有一筆(不得重複)")
        self.assertIn("embryo-level", revisions[0]["previous_title"])


class DurableWriteHappensBeforeStateAdvancesTest(MemoryCase):
    """consolidate 內部同樣不得「先動狀態、再寫檔」。

    這是①的一個更窄的窗口:`correct()` 已經不再提早 supersede,但
    consolidate 自己原本是「supersede → upsert → 寫檔」。寫檔失敗時留下的狀態
    **比沒寫更糟**:
        local    已經是新值
        durable  還是舊值
    而下一次重跑會把「新值 supersede 新值」記成 lineage —— 真正的 v1 → v2
    那一段就永久消失,歷史被寫成假的而不只是缺的。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("k 語意")

    def seed(self, title):
        candidate = devtalk.propose(self.store, self.session, "domain",
                                    {"key": "k", "title": title},
                                    "domain_expert")
        devtalk.confirm(self.store, candidate)
        devtalk.checkpoint(self.store, self.repo, self.session)

    def fail_once(self, attr):
        original = getattr(durable, attr)
        setattr(durable, attr, lambda *a, **k: (_ for _ in ()).throw(
            IOError("模擬寫檔失敗")))
        try:
            with self.assertRaises(IOError):
                devtalk.checkpoint(self.store, self.repo, self.session)
        finally:
            setattr(durable, attr, original)

    def test_knowledge_write_failure_leaves_local_and_durable_agreeing(self):
        self.seed("v1")
        devtalk.correct(self.store, self.session, "domain", "k", "v2",
                        reason="使用者更正")
        self.fail_once("write_knowledge")

        local = self.store.knowledge(kind="domain", key="k",
                                     statuses=("CANDIDATE", "CONFIRMED",
                                               "CONFLICT"), limit=10)
        durable_rows = [r for r in durable.iter_knowledge(self.repo)
                        if r["key"] == "k"]
        self.assertEqual([r["title"] for r in local], ["v1"],
                         "寫檔失敗 = consolidation 沒成功,local 必須還是舊值")
        self.assertEqual([r["title"] for r in durable_rows], ["v1"])

    def test_retry_after_write_failure_records_the_real_transition(self):
        self.seed("v1")
        devtalk.correct(self.store, self.session, "domain", "k", "v2",
                        reason="使用者更正")
        self.fail_once("write_knowledge")
        devtalk.checkpoint(self.store, self.repo, self.session)

        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == lineage.KNOWLEDGE_CORRECTED]
        self.assertEqual(len(revisions), 1)
        self.assertEqual(revisions[0]["previous_title"], "v1",
                         "重跑不得把「v2 → v2」記成歷史 —— 那會讓真正的"
                         " v1 → v2 永久消失,歷史從缺變成假")
        self.assertEqual(revisions[0]["new_title"], "v2")
        current = [r for r in durable.iter_knowledge(self.repo)
                   if r["key"] == "k"]
        self.assertEqual([r["title"] for r in current], ["v2"])

    def test_decision_write_failure_does_not_supersede(self):
        candidate = devtalk.propose(
            self.store, self.session, "decision",
            {"key": "storage", "title": "用 SQLite", "decision": "SQLite"},
            "design_decision")
        devtalk.confirm(self.store, candidate)
        devtalk.checkpoint(self.store, self.repo, self.session)

        second = devtalk.propose(
            self.store, self.session, "decision",
            {"key": "storage", "title": "改用 Postgres",
             "decision": "Postgres"}, "design_decision")
        devtalk.confirm(self.store, second)
        self.fail_once("write_decision")

        rows = self.store.decisions(key="storage", statuses=("ACCEPTED",),
                                    limit=5)
        self.assertEqual([r["title"] for r in rows], ["用 SQLite"],
                         "寫檔失敗後舊決定必須還是 ACCEPTED")


class DurableCheckCase(MemoryCase):
    """`durable_check` 的共用治具(本身不含測試案)。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)

    def write_some_memory(self):
        session = self.store.start_session("t")
        candidate = devtalk.propose(
            self.store, session, "domain",
            {"key": "registration", "title": "一個客戶的送檢紀錄"},
            "domain_expert")
        devtalk.confirm(self.store, candidate)
        devtalk.end(self.store, self.repo, session)

    def check(self):
        return sync.durable_check(self.repo, self.store)

    def add_remote(self, off_machine=True):
        """建一個本機 bare repo 當 upstream 並 push 上去。

        `off_machine=True` 時額外讓 URL 解析回報一個網路 remote。理由:
        `durable-check` 現在會拒絕**本機** remote 當「記憶離開這台機器」的
        證據(見 RemoteMustBeOffMachineTest),而一個真的網路 remote 沒辦法
        在 CI 裡不連外地建起來。這裡只替換「這個 remote 的 URL 是什麼」
        這一個問句 —— push、`ls-remote` 問到的 SHA、與 HEAD 的比對全部是真的。
        `off_machine=False` 則完全不替換,用來驗本機 remote 真的被拒。
        """
        from memtools import git
        bare = os.path.join(self.work, "origin.git")
        os.makedirs(bare, exist_ok=True)
        git(bare, "init", "-q", "--bare")
        git(self.repo, "remote", "add", "origin", bare)
        branch = git(self.repo, "rev-parse", "--abbrev-ref", "HEAD")
        git(self.repo, "push", "-q", "-u", "origin", branch)
        if off_machine:
            patcher = mock.patch.object(
                sync, "_remote_url",
                return_value="ssh://git@git.example.com/dev-flow.git")
            patcher.start()
            self.addCleanup(patcher.stop)
        return bare


class DurableCheckTest(DurableCheckCase):
    """Stage 6 收尾的最後一道:記憶真的離開這台機器了嗎?

    `checkpoint` 回 `promoted: 3` 只代表檔案寫進**工作樹**。工作樹不是耐久性
    —— 沒 commit 會被 checkout 掉,沒 push 就只有這台機器有。收尾順序
    (萃取 → checkpoint → memory commit → 最終 push → remote HEAD 驗證)
    每一步都可能「看起來做完了」,所以要有一支能複驗的判定。
    """

    def test_checkpoint_alone_is_not_durable(self):
        """checkpoint 成功但沒 commit → FAIL。這是最容易發生的一種假完成。"""
        self.write_some_memory()
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertTrue(any(sync.UNCOMMITTED in p for p in result["problems"]),
                        result["problems"])
        self.assertTrue(result["uncommitted"], "應列出未 commit 的 durable 檔")

    def test_uncommitted_paths_are_repo_relative(self):
        """輸出不得外洩絕對路徑(durable 側與 CLI 輸出同一條紀律)。"""
        self.write_some_memory()
        for rel in self.check()["uncommitted"]:
            self.assertFalse(os.path.isabs(rel), rel)
            self.assertNotIn("\\", rel, "路徑分隔符一律 /")
            self.assertTrue(rel.startswith(".dev-flow/"), rel)

    def test_committed_but_unpushed_still_fails(self):
        """commit 了但沒有 upstream → 記憶還沒離開本機,不得判 PASS。"""
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertTrue(any(sync.UNPUSHED in p for p in result["problems"]),
                        result["problems"])
        self.assertFalse(result["pushed"])

    def test_passes_only_after_commit_and_push(self):
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote()
        result = self.check()
        self.assertEqual(result["verdict"], "PASS", result["problems"])
        self.assertTrue(result["pushed"])
        self.assertEqual(result["head"], result["remote_head"])
        self.assertTrue(result["upstream"])

    def test_new_commit_after_push_fails_again(self):
        """push 之後又 commit(例如補了記憶)→ 必須重新變成 FAIL。"""
        from memtools import commit_all, write
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote()
        write(self.repo, "later.md", "又改了一次\n")
        commit_all(self.repo, "後來的 commit")
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertTrue(any(sync.UNPUSHED in p for p in result["problems"]))

    def test_open_session_fails(self):
        """還開著的 session = 這一輪的記憶懸在半空,不算收尾完成。"""
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote()
        self.store.start_session("忘了收的 session")
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertTrue(any(sync.OPEN_SESSION in p for p in result["problems"]),
                        result["problems"])

    def test_pending_revision_fails(self):
        """修正歷史還留在 local = 它還不存在,不得判 PASS。"""
        from memtools import commit_all
        commit_all(self.repo, "base", allow_empty=True)
        self.add_remote()
        lineage.record_pending(self.store, lineage.build_knowledge_revision(
            "domain", "k", {"title": "v1"}, {"title": "v2"}, reason="更正"))
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertTrue(
            any(sync.PENDING_REVISION in p for p in result["problems"]),
            result["problems"])

    def test_unrelated_dirty_files_do_not_fail_it(self):
        """只看 durable 樹 —— 手上還在改別的檔不是這一關要管的事。"""
        from memtools import commit_all, write
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote()
        write(self.repo, "src/wip.py", "# 還在寫\n")
        result = self.check()
        self.assertEqual(result["verdict"], "PASS", result["problems"])

    # ── 遠端要真的被觀察到 ──────────────────────────────────────────────────
    def test_stale_tracking_ref_cannot_prove_remote_durability(self):
        """`origin/<branch>` 是本機快取。遠端被改掉時它還是舊值 —— 不得判 PASS。

        「記憶離開這台機器了嗎」這個問句的答案只能來自遠端本身。另一台機器
        force-push 或刪掉那個 branch 之後,本機的追蹤 ref 仍然指著我的 commit,
        於是這一關會替一個伺服器上已經不存在的 commit 背書。
        """
        from memtools import commit_all, git
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        bare = self.add_remote()
        branch = git(self.repo, "rev-parse", "--abbrev-ref", "HEAD")
        self.assertEqual(self.check()["verdict"], "PASS")

        # 另一台機器把遠端 branch 換掉;本機刻意不 fetch。
        other = git(self.repo, "rev-parse", "HEAD~1")
        git(bare, "update-ref", "refs/heads/" + branch, other)
        self.assertEqual(
            identity._git(self.repo, "rev-parse", "origin/" + branch),
            git(self.repo, "rev-parse", "HEAD"),
            "前置條件:追蹤 ref 必須還是舊值,否則這個測試沒在測東西")

        result = self.check()
        self.assertEqual(result["verdict"], "FAIL", result)
        self.assertTrue(any(sync.UNPUSHED in p for p in result["problems"]),
                        result["problems"])

    def test_unreachable_remote_fails_closed(self):
        """問不到遠端就是沒有證據 —— 不得因為問不到而放行。"""
        from memtools import commit_all, git
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        bare = self.add_remote()
        shutil.rmtree(bare)
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL", result)
        self.assertTrue(
            any(sync.REMOTE_UNVERIFIED in p for p in result["problems"]),
            result["problems"])
        self.assertFalse(result["remote_observed"],
                         "沒觀察到遠端就不得聲稱觀察過")

    def test_local_only_is_explicit_and_says_so(self):
        """離線時要能明說「這一關只驗到本機」—— 而不是假裝驗過遠端。"""
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        bare = self.add_remote()
        shutil.rmtree(bare)
        result = sync.durable_check(self.repo, self.store, local_only=True)
        self.assertEqual(result["verdict"], "PASS", result["problems"])
        self.assertFalse(result["remote_observed"],
                         "local_only 不得聲稱觀察過遠端")

    def test_remote_observed_is_recorded_on_a_real_pass(self):
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote()
        result = self.check()
        self.assertEqual(result["verdict"], "PASS", result["problems"])
        self.assertTrue(result["remote_observed"])
        self.assertEqual(result["remote_head"], result["head"])


class RemoteMustBeOffMachineTest(DurableCheckCase):
    """一個 git remote 不必然在別台機器上 —— 而這一關問的正是那件事。

    `durable-check` 的問句是「記憶離開這台機器了嗎」。`ls-remote` 成功只證明
    「設定的 upstream 連得上而且有這個 commit」,那是**嚴格較弱**的一句話:

        origin = /Volumes/backup/mirror.git
        origin = file:///Users/rick/mirror.git
        origin = ssh://git@localhost/repo.git

    這三個都會讓 `ls-remote` 回報正確的 SHA,於是 verdict=PASS、
    remote_observed=true。而硬碟壞掉時它們跟工作樹一起消失 —— 判定聲稱了
    一件它沒有驗證的事,這正是本專案在修的同一個錯:**在耐久性真正建立之前
    就把狀態往前推**。

    離線要放行請用 `--local-only`:它會 PASS 但 `remote_observed=False`,
    也就是**明說**這一關只驗到本機。「不得聲稱」與「不得放行」不是同一件事。
    """

    def test_local_bare_remote_is_not_off_machine_proof(self):
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote(off_machine=False)
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL", result)
        self.assertTrue(
            any(sync.REMOTE_LOCAL in p for p in result["problems"]),
            result["problems"])
        self.assertFalse(result["remote_observed"],
                         "本機 remote 不得算成觀察到遠端")

    def test_file_url_remote_is_not_off_machine_proof(self):
        from memtools import commit_all, git
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        bare = self.add_remote(off_machine=False)
        git(self.repo, "remote", "set-url", "origin",
            "file://" + bare.replace(os.sep, "/"))
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL", result)
        self.assertTrue(
            any(sync.REMOTE_LOCAL in p for p in result["problems"]),
            result["problems"])

    def test_insteadof_rewrite_to_a_local_path_is_still_local(self):
        """判定要看 git **實際會連上去**的 URL,不是設定檔裡好看的那個。

        `url.<path>.insteadOf` 會把一個網路形狀的 URL 改寫成本機路徑。只看
        `remote.origin.url` 的話,一個實際只寫到本機目錄的 remote 會通過。
        """
        from memtools import commit_all, git
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        bare = self.add_remote(off_machine=False)
        fake = "ssh://git@git.example.com/dev-flow.git"
        git(self.repo, "config", "url.{0}.insteadOf".format(bare), fake)
        git(self.repo, "remote", "set-url", "origin", fake)
        self.assertEqual(
            identity._git(self.repo, "config", "remote.origin.url"), fake,
            "前置條件:設定值必須是網路形狀的,否則這個測試沒在測東西")
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL", result)
        self.assertTrue(
            any(sync.REMOTE_LOCAL in p for p in result["problems"]),
            result["problems"])

    def test_problems_never_leak_the_remote_url(self):
        """輸出只提 remote **名字**:URL 可能帶 token,而這段會被貼進紀錄。"""
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        bare = self.add_remote(off_machine=False)
        result = self.check()
        blob = json.dumps(result, ensure_ascii=False)
        self.assertNotIn(bare, blob)
        self.assertNotIn(self.work, blob)

    def test_off_machine_remote_still_passes(self):
        """正向路徑不得被這一條擋掉 —— 真的網路 remote 要 PASS。"""
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote(off_machine=True)
        result = self.check()
        self.assertEqual(result["verdict"], "PASS", result["problems"])
        self.assertTrue(result["remote_observed"])

    def test_local_only_still_passes_without_claiming_remote(self):
        """本機 remote + `--local-only` → 放行,但不得聲稱驗過遠端。"""
        from memtools import commit_all
        self.write_some_memory()
        commit_all(self.repo, "memory commit")
        self.add_remote(off_machine=False)
        result = sync.durable_check(self.repo, self.store, local_only=True)
        self.assertEqual(result["verdict"], "PASS", result["problems"])
        self.assertFalse(result["remote_observed"])


class DurableWriterGatesEveryFactTest(MemoryCase):
    """durable writer 是**最後**一道防線,不是最後一個沒人看的出口。

    `promote_entity_facts()` 整檔寫回一個 entity 的所有 facts(supersede 語意住
    在整組上)。它原本不過 Signal Gate —— 而 fact 進 local DB 的路不只有「過了
    gate 的候選」一條:`truth.reverify()`(公開 CLI `verify --observed`)直接
    寫值。於是這條完全走公開 CLI 的路會把 secret 寫進 Git:

        verify --observed "<含憑證的觀察值>"     # 直接進 DB,沒有 gate
        → 之後任何一個**乾淨**的 fact 候選碰到同一個 entity
        → consolidate 把該 entity 加進 entities_touched
        → promote_entity_facts 整檔寫回 = 連旁邊那筆 secret 一起進 Git

    候選的 gate 檢查的是**那一筆候選**的內容,擋不住同一個 entity 裡的鄰居。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.store.register_workspace(
            self.workspace, identity.workspace_snapshot(self.repo))
        from memtools import commit_all, write
        write(self.repo, "src/db.py", "URL = 'x'\n")
        commit_all(self.repo, "dep")

    def add_fact(self, fact_key, value, status=None):
        from agentmem import truth as truth_mod
        return self.store.upsert_fact({
            "entity_type": "database", "entity_key": "main",
            "fact_key": fact_key, "value": value,
            "status": status or truth_mod.VERIFIED, "confidence": 0.9,
            "recorded_at": store_mod.utc_now(),
            "verified_at": store_mod.utc_now(), "verification_count": 1,
            "source_type": "code", "dependencies": ["src/db.py"],
            "fingerprints": truth.fingerprints_for(self.repo, ["src/db.py"]),
            "durable": False})

    def durable_blob(self):
        return "\n".join(
            json.dumps(s, ensure_ascii=False) for s in durable.iter_states(
                self.repo))

    def test_secret_bearing_fact_is_not_written_to_git(self):
        self.add_fact("url",
                      "postgres://admin:S3cr3tPassw0rd@prod.example.com/app")
        sync.promote_entity_facts(self.repo, self.store, "database", "main")
        self.assertNotIn("S3cr3tPassw0rd", self.durable_blob(),
                         "durable writer 必須擋下含憑證的 fact")

    def test_clean_siblings_are_still_written(self):
        """只擋那一筆,不連坐 —— 其餘 fact 照樣要固化。"""
        self.add_fact("pool", "20")
        self.add_fact("url", 'password = "hunter2000-real-not-placeholder"')
        sync.promote_entity_facts(self.repo, self.store, "database", "main")
        blob = self.durable_blob()
        self.assertIn("pool", blob, "乾淨的 fact 不得被連坐擋掉")
        self.assertNotIn("hunter2000", blob)

    def test_rejected_fact_is_not_marked_durable(self):
        """沒寫進去的 fact 不得被標 durable(本輪的同一條紀律)。"""
        fact_id = self.add_fact(
            "url", "postgres://admin:S3cr3tPassw0rd@prod.example.com/app")
        sync.promote_entity_facts(self.repo, self.store, "database", "main")
        row = self.store.fact_row(fact_id)
        self.assertEqual(row["durable"], 0,
                         "沒寫進 .dev-flow 的 fact 被標成已耐久 = 靜默失憶")

    def test_leak_is_unreachable_through_the_public_cli_path(self):
        """端對端走真實路徑:reverify 塞值 → 乾淨候選碰同一 entity → checkpoint。"""
        fact_id = self.add_fact("url", "postgres://localhost/app")
        sync.promote_entity_facts(self.repo, self.store, "database", "main")
        truth.reverify(
            self.store, self.repo, fact_id, self.workspace,
            "postgres://admin:S3cr3tPassw0rd@prod.example.com/app",
            reason="觀察到正式環境設定")

        session = self.store.start_session("x")
        candidate = devtalk.propose(
            self.store, session, "fact",
            {"entity_type": "database", "entity_key": "main",
             "fact_key": "pool", "value": "20", "status": truth.VERIFIED,
             "dependencies": ["src/db.py"], "title": "pool size"},
            "current_code")
        devtalk.confirm(self.store, candidate)
        devtalk.end(self.store, self.repo, session)

        self.assertNotIn("S3cr3tPassw0rd", self.durable_blob())
        events = "\n".join(json.dumps(e, ensure_ascii=False)
                           for e in durable.iter_events(self.repo))
        self.assertNotIn("S3cr3tPassw0rd", events,
                         "revision(舊值→新值)也不得帶著 secret 落地")


class FactAndEventCandidateBarrierTest(MemoryCase):
    """fact / event 的候選狀態不得在 durable 寫入成功之前前進。

    knowledge / decision / skill 三類在 `consolidate()` 裡是「寫檔 → 動 local」,
    fact 與 event 卻不是:

        fact   upsert_fact → candidate=CONSOLIDATED → (迴圈外) write_state
        event  add_event(durable=True) → candidate=CONSOLIDATED → append_events

    兩條都在「還沒寫進 `.dev-flow/`」的時候就把狀態推進到「已經寫進去了」——
    這正是本檔①②③同一個病灶,只是換了兩個 kind:

        ①寫檔失敗後 candidate 已是 CONSOLIDATED → 重跑不再看到它 →
          `.dev-flow/` 永遠缺這一筆,而 local 自洽、沒有任何測試會紅。
        ②event 的 local 列在 `append_events()` 之前就 durable=1 ——
          明確的 false durability claim(「已耐久」指向一個不存在的檔)。
        ③失敗後重跑若每次新產 id,補寫會變成第二筆 —— 歷史從缺變成重複。
    """

    def setUp(self):
        super().setUp()
        from memtools import commit_all, write
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/db.py", "URL = 'x'\n")
        commit_all(self.repo, "dep")
        self.session = self.store.start_session("實作一輪",
                                                mode="implementation")

    def observe_fact(self, fact_key="pool", value="20"):
        return session_mod.observe(
            self.store, self.session, "architecture_change",
            "資料庫連線池大小", "從 config 讀到的值",
            fact={"entity_type": "database", "entity_key": "main",
                  "fact_key": fact_key, "value": value,
                  "status": truth.VERIFIED, "dependencies": ["src/db.py"]},
            file_paths=["src/db.py"], repo_root=self.repo)

    def observe_event(self):
        return session_mod.observe(
            self.store, self.session, "schema_change",
            "registrations 加了 customer_id 欄位",
            "migration 0007 已套用", file_paths=["src/db.py"],
            repo_root=self.repo)

    def fail_once(self, attr):
        original = getattr(durable, attr)
        setattr(durable, attr, lambda *a, **k: (_ for _ in ()).throw(
            IOError("模擬寫檔失敗")))
        try:
            with self.assertRaises(IOError):
                session_mod.checkpoint(self.store, self.repo, self.session)
        finally:
            setattr(durable, attr, original)

    def candidate_status(self, candidate_id):
        row = self.store.conn.execute(
            "SELECT status FROM candidates WHERE candidate_id=?",
            (candidate_id,)).fetchone()
        return row["status"]

    def durable_facts(self):
        out = []
        for state in durable.iter_states(self.repo):
            for fact in state.get("facts") or []:
                out.append(fact)
        return out

    # ── fact ────────────────────────────────────────────────────────────────
    def test_fact_write_state_failure_keeps_candidate_retryable(self):
        """write_state 失敗 → 候選必須還是 CONFIRMED(否則重跑看不到它)。"""
        result = self.observe_fact()
        self.fail_once("write_state")
        self.assertEqual(
            self.candidate_status(result["candidate_id"]), "CONFIRMED",
            "durable 寫入失敗,候選卻已 CONSOLIDATED —— 重跑不再看到它,"
            "`.dev-flow/` 永遠缺這一筆")
        self.assertEqual(self.durable_facts(), [],
                         "寫檔失敗後 durable 側不得有任何 fact")

    def test_fact_retry_after_failure_writes_exactly_one(self):
        """失敗 → 重跑 → durable 側剛好一筆(不得 0 筆也不得 2 筆)。"""
        self.observe_fact()
        self.fail_once("write_state")
        session_mod.checkpoint(self.store, self.repo, self.session)
        facts = self.durable_facts()
        self.assertEqual([f["fact_key"] for f in facts], ["pool"],
                         "重跑要補得回來,而且只補一筆")
        self.assertEqual(len(self.store.facts(entity_type="database",
                                              entity_key="main", limit=50)), 1,
                         "重跑不得在 local 產生第二筆同義 fact")

    def test_fact_write_failure_survives_destructive_rebuild(self):
        """砍掉 local → 只從 `.dev-flow/` 重建:失敗那一輪不得留下半個 fact。"""
        self.observe_fact()
        self.fail_once("write_state")
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        counts = sync.rebuild_local(self.repo, fresh)
        self.assertEqual(counts["facts"], 0,
                         "durable 側沒有的東西,rebuild 後不得憑空出現")

    # ── event ───────────────────────────────────────────────────────────────
    def test_event_append_failure_never_marks_event_durable(self):
        """append_events 失敗 → local event 列不得帶 durable=1。"""
        result = self.observe_event()
        self.fail_once("append_events")
        row = self.store.conn.execute(
            "SELECT durable FROM events WHERE event_id=?",
            (result["event_id"],)).fetchone()
        self.assertEqual(
            row["durable"], 0,
            "`.dev-flow/` 裡從來沒有這筆事件,local 卻宣稱它已耐久 —— "
            "這是 false durability claim,而且是靜默的")
        self.assertEqual(list(durable.iter_events(self.repo)), [])

    def test_event_append_failure_keeps_candidate_retryable(self):
        result = self.observe_event()
        self.fail_once("append_events")
        self.assertEqual(
            self.candidate_status(result["candidate_id"]), "CONFIRMED",
            "寫檔失敗後候選必須留在 CONFIRMED 等重試")

    def test_event_retry_after_failure_writes_exactly_one(self):
        result = self.observe_event()
        self.fail_once("append_events")
        session_mod.checkpoint(self.store, self.repo, self.session)
        events = [e for e in durable.iter_events(self.repo)
                  if e.get("kind") == "schema_change"]
        self.assertEqual(len(events), 1,
                         "重跑要補得回來且只有一筆(id 每次新產就會變兩筆)")
        self.assertEqual(events[0]["event_id"], result["event_id"],
                         "補寫的必須是同一筆事件,不是它的複製品")
        row = self.store.conn.execute(
            "SELECT durable FROM events WHERE event_id=?",
            (result["event_id"],)).fetchone()
        self.assertEqual(row["durable"], 1, "真的寫進去之後才標 durable")

    # ── gate 擋掉的 fact ─────────────────────────────────────────────────────
    def test_gate_rejected_fact_candidate_is_not_consolidated(self):
        """被 durable writer 擋下的 fact,候選不得被記成已固化。

        `promote_entity_facts()` 逐筆過 gate。被擋的那一筆從來沒進 `.dev-flow/`,
        它的候選標成 CONSOLIDATED 就等於「已固化」指向一個不存在的東西。
        """
        result = self.observe_fact(
            "url", "postgres://admin:S3cr3tPassw0rd@prod.example.com/app")
        outcome = session_mod.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(
            self.candidate_status(result["candidate_id"]), "LOCAL_ONLY",
            "沒寫進 Git 的候選不得是 CONSOLIDATED —— 要留下「為什麼沒進去」")
        self.assertEqual(outcome["promoted"], 0,
                         "什麼都沒固化,promoted 不得回 1")
        self.assertEqual(self.durable_facts(), [])


class EventAppendIsIdempotentAcrossCrashWindowTest(MemoryCase):
    """「先寫檔、才動 local」對 **append-only writer** 還不夠。

    `write_state()` 是 deterministic 整檔取代:寫檔成功後行程死掉,重跑寫的是
    同一份內容取代同一個檔 —— 它會收斂。`append_events()` 不是:它以 append
    模式寫進 JSONL,而 JSONL **不是 keyed storage**。所以這個視窗是不對稱的:

        append_events 成功
        ↓  ← 行程死在這裡 / SQLite 失敗
        store.add_event(durable=True)
        store.set_candidate_status(CONSOLIDATED)

    候選留在 CONFIRMED(這是對的,重跑才補得回來),但重跑會把同一個
    `event_id` **再 append 一次**。deterministic id 擋不住它 —— 那是去重的
    *依據*,不是去重的*機制*。歷史從「缺」變成「重複」,而重複比缺更難發現:
    兩行都是合法 JSON、都長得像真的,rebuild 之後同一件事被記得兩次。

    既有的三案把失敗注入在 **durable writer 自己**(`append_events` 拋),
    所以它們證明的是「寫檔失敗後救得回來」。這一組把失敗注入在
    **append 成功之後、local 狀態前進之前** —— 那是真正無法避免的視窗,
    因為檔案系統與 SQLite 沒有共同的 transaction。
    """

    def setUp(self):
        super().setUp()
        from memtools import commit_all, write
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/db.py", "URL = 'x'\n")
        commit_all(self.repo, "dep")
        self.session = self.store.start_session("實作一輪",
                                                mode="implementation")

    def observe_event(self, title="registrations 加了 customer_id 欄位"):
        return session_mod.observe(
            self.store, self.session, "schema_change", title,
            "migration 0007 已套用", file_paths=["src/db.py"],
            repo_root=self.repo)

    def crash_after_append(self, method):
        """append_events 成功之後、`store.<method>` 之前注入一次失敗。"""
        original = getattr(self.store, method)
        calls = {"n": 0}

        def boom(*args, **kwargs):
            calls["n"] += 1
            raise IOError("模擬行程/SQLite 在 durable append 之後死掉")

        setattr(self.store, method, boom)
        try:
            with self.assertRaises(IOError):
                session_mod.checkpoint(self.store, self.repo, self.session)
        finally:
            try:
                delattr(self.store, method)
            except AttributeError:
                setattr(self.store, method, original)
        self.assertGreater(calls["n"], 0,
                           "失敗沒有被注入到 —— 這一案沒有測到那個視窗")

    def durable_event_ids(self):
        return [e.get("event_id") for e in durable.iter_events(self.repo)]

    def durable_lines(self):
        base = os.path.join(durable.root(self.repo), "events")
        out = []
        for dirpath, _dirs, files in os.walk(base):
            for name in sorted(files):
                if not name.endswith(".jsonl"):
                    continue
                with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                    out.extend(line for line in fh.read().splitlines()
                               if line.strip())
        return out

    def test_append_already_happened_before_the_crash(self):
        """先確立前提:這個視窗真的存在(append 成功了,local 還沒前進)。"""
        result = self.observe_event()
        self.crash_after_append("add_event")
        self.assertEqual(self.durable_event_ids(), [result["event_id"]],
                         "前提不成立:append 沒有先發生,這一組測的不是那個視窗")
        row = self.store.conn.execute(
            "SELECT durable FROM events WHERE event_id=?",
            (result["event_id"],)).fetchone()
        self.assertEqual(row["durable"], 0,
                         "local 還沒前進 —— 這正是重跑必須補完的狀態")

    def test_crash_before_local_event_then_retry_writes_exactly_one(self):
        result = self.observe_event()
        self.crash_after_append("add_event")
        session_mod.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(
            self.durable_event_ids().count(result["event_id"]), 1,
            "同一個 event_id 在 `.dev-flow/` 出現兩次 —— append-only writer "
            "的重跑必須以 event_id 去重,否則歷史從缺變成重複")

    def test_crash_before_candidate_status_then_retry_writes_exactly_one(self):
        result = self.observe_event()
        self.crash_after_append("set_candidate_status")
        session_mod.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(
            self.durable_event_ids().count(result["event_id"]), 1,
            "候選狀態沒前進 → 重跑 → 同一筆事件被 append 第二次")

    def test_crash_with_many_events_keeps_each_id_once(self):
        ids_seen = [self.observe_event("schema 變更 %d" % i)["event_id"]
                    for i in range(3)]
        self.crash_after_append("add_event")
        session_mod.checkpoint(self.store, self.repo, self.session)
        written = self.durable_event_ids()
        for event_id in ids_seen:
            self.assertEqual(written.count(event_id), 1,
                             "多筆一起重跑時每個 event_id 仍必須剛好一次")
        self.assertEqual(len(written), len(set(written)),
                         "durable 事件流出現重複 id")

    def test_every_durable_line_still_parses_as_json(self):
        self.observe_event()
        self.crash_after_append("add_event")
        session_mod.checkpoint(self.store, self.repo, self.session)
        for line in self.durable_lines():
            json.loads(line)  # 去重改寫不得留下半行或壞行

    def test_destructive_rebuild_sees_exactly_one_logical_event(self):
        result = self.observe_event()
        self.crash_after_append("add_event")
        session_mod.checkpoint(self.store, self.repo, self.session)
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        rows = fresh.conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE event_id=?",
            (result["event_id"],)).fetchone()
        self.assertEqual(rows["n"], 1,
                         "另一台機器只從 `.dev-flow/` 重建時,同一件事被記兩次")

    def test_revision_event_id_is_stable_across_retry(self):
        """revision 的 event_id 是 `ids.new_id()` —— 每次重跑都是新的一筆。

        去重靠 event_id,而隨機 id 讓去重永遠對不上:同一筆 lineage 會在
        `.dev-flow/events/` 累積成 N 筆,每一筆都聲稱同一次 supersede。
        """
        from memtools import write
        result = session_mod.observe(
            self.store, self.session, "architecture_change",
            "資料庫連線池大小", "從 config 讀到的值",
            fact={"entity_type": "database", "entity_key": "main",
                  "fact_key": "pool", "value": "20",
                  "status": truth.VERIFIED, "dependencies": ["src/db.py"]},
            file_paths=["src/db.py"], repo_root=self.repo)
        session_mod.checkpoint(self.store, self.repo, self.session)
        fact_id = self.store.facts(entity_type="database", entity_key="main",
                                   limit=5)[0]["fact_id"]
        write(self.repo, "src/db.py", "URL = 'y'\n")
        workspace = identity.workspace_key(self.project_id, self.repo)
        self.store.register_workspace(
            workspace, identity.workspace_snapshot(self.repo))
        truth.reverify(self.store, self.repo, fact_id, workspace, "50",
                       session_id=self.session, reason="config 改了")
        self.crash_after_append("add_event")
        session_mod.checkpoint(self.store, self.repo, self.session)
        revisions = [e for e in durable.iter_events(self.repo)
                     if e.get("kind") == "fact_superseded"]
        self.assertEqual(
            len(revisions), 1,
            "同一次 supersede 在 durable 事件流裡出現 {0} 筆 —— revision 的 "
            "event_id 必須由 revision_id 推導,不能每次重跑都新產"
            .format(len(revisions)))
        self.assertNotEqual(result["candidate_id"], None)


class SessionLifecycleFailsClosedTest(MemoryCase):
    """finalization 一律要求 session == OPEN,否則零 durable 副作用 + 報錯。

    `observe()` 有 `require_open()`,`checkpoint()` 沒有 —— 它只呼叫
    `store.session(session_id)` 而**丟掉回傳值**,而那支對不存在的 session
    回 None、不丟例外。於是這條路是通的:

        start → propose → confirm → abort → checkpoint → 候選照樣進 Git

    abort 的語意是「這一輪不算」。它之後還能把候選固化進 Git,等於
    「中止」只是一個沒有效力的標籤。`end_session()` 也不是 compare-and-set:
    abort 之後再 end 會把 ABORTED 覆寫成 CLOSED,回顧時看不出這一輪沒收斂。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("registration 語意")
        candidate = devtalk.propose(
            self.store, self.session, "domain",
            {"key": "registration", "title": "registration = customer-level"},
            "domain_expert")
        devtalk.confirm(self.store, candidate)

    def durable_domain(self):
        return [r for r in durable.iter_knowledge(self.repo)
                if r["key"] == "registration"]

    def test_aborted_session_cannot_checkpoint(self):
        session_mod.abort(self.store, self.session, reason="使用者說先不要")
        with self.assertRaises(session_mod.SessionError):
            session_mod.checkpoint(self.store, self.repo, self.session)

    def test_aborted_session_checkpoint_has_zero_durable_side_effect(self):
        session_mod.abort(self.store, self.session, reason="使用者說先不要")
        with self.assertRaises(session_mod.SessionError):
            session_mod.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(self.durable_domain(), [],
                         "abort 之後 checkpoint 仍把候選寫進 Git = "
                         "「中止」是一個沒有效力的標籤")

    def test_closed_session_cannot_checkpoint(self):
        session_mod.end(self.store, self.repo, self.session)
        with self.assertRaises(session_mod.SessionError):
            session_mod.checkpoint(self.store, self.repo, self.session)

    def test_nonexistent_session_cannot_checkpoint(self):
        with self.assertRaises(session_mod.SessionError):
            session_mod.checkpoint(self.store, self.repo,
                                   "ses_00000000000000000000000000")

    def test_end_after_abort_does_not_overwrite_aborted(self):
        session_mod.abort(self.store, self.session, reason="使用者說先不要")
        with self.assertRaises(session_mod.SessionError):
            session_mod.end(self.store, self.repo, self.session)
        self.assertEqual(self.store.session(self.session)["status"],
                         session_mod.ABORTED,
                         "ABORTED 被覆寫成 CLOSED = 回顧時看不出這一輪沒收斂")

    def test_abort_after_close_is_rejected(self):
        session_mod.end(self.store, self.repo, self.session)
        with self.assertRaises(session_mod.SessionError):
            session_mod.abort(self.store, self.session, reason="反悔")
        self.assertEqual(self.store.session(self.session)["status"],
                         session_mod.CLOSED)

    def test_devtalk_checkpoint_is_the_same_gate(self):
        """dev-talk 不得有第二套較鬆的收尾 —— 兩條路共用同一個 state machine。"""
        session_mod.abort(self.store, self.session, reason="先不要")
        with self.assertRaises(session_mod.SessionError):
            devtalk.checkpoint(self.store, self.repo, self.session)
        self.assertEqual(self.durable_domain(), [])

    def test_consolidate_refuses_candidates_of_a_non_open_session(self):
        """durable writer 自己也要驗 —— store 是內部 API,繞得過上面那層。

        `consolidate()` 原本只驗 session **存在**。ABORTED 的 session 存在,
        於是走 `session_id=None`(全專案掃)這條路時它的候選照樣進 Git。
        """
        session_mod.abort(self.store, self.session, reason="先不要")
        result = sync.consolidate(self.repo, self.store)
        self.assertEqual(result["promoted"], 0,
                         "非 OPEN session 的候選不得被固化")
        self.assertEqual(self.durable_domain(), [])


class DurableStateIsCompleteTest(MemoryCase):
    """整檔取代的 writer 只有「全部」一種正確結果 —— 寫一部分就是把現況檔改小。

    `promote_entity_facts()` 用整檔取代,因為 supersede 語意住在整組 fact 上。
    整檔取代與「撈前 N 筆」放在一起會變成刪除:視窗外的 fact 上一輪可能已經
    在檔裡、也已經 `durable=1`,這一輪的取代把它從檔案裡拿掉,而 local 那一列
    仍然聲稱「我就是 `.dev-flow/` 裡的那份」。於是 `durable-check` 判 PASS,
    砍掉 local 重建之後那些 fact 永遠回不來 —— 靜默且不可逆。

    視窗還套在 status 過濾**之前**,所以連「現行 fact 只有 1 筆」都不安全:
    夠多的 SUPERSEDED 鄰居就能把唯一的現況擠出去。
    """

    OVER_WINDOW = 1250

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.store.register_workspace(
            self.workspace, identity.workspace_snapshot(self.repo))
        from memtools import commit_all, write
        write(self.repo, "src/db.py", "URL = 'x'\n")
        commit_all(self.repo, "dep")
        self.prints = truth.fingerprints_for(self.repo, ["src/db.py"])

    def add_facts(self, count, status=None, stamp="2026-08-20T00:00:00Z",
                  prefix="k"):
        status = status or truth.VERIFIED
        rows = []
        for index in range(count):
            rows.append(self.store.upsert_fact({
                "entity_type": "database", "entity_key": "main",
                "fact_key": "{0}{1:05d}".format(prefix, index),
                "value": str(index), "status": status, "confidence": 0.9,
                "recorded_at": stamp, "verified_at": stamp,
                "verification_count": 1, "source_type": "code",
                "dependencies": ["src/db.py"], "fingerprints": self.prints,
                "durable": False}))
        return rows

    def durable_fact_keys(self):
        return {fact["fact_key"]
                for state in durable.iter_states(self.repo)
                for fact in state["facts"]}

    def promote(self):
        return sync.promote_entity_facts(self.repo, self.store,
                                         "database", "main")

    def test_every_current_fact_reaches_the_durable_state_file(self):
        """現行 fact 比視窗多 → 整檔取代不得只寫視窗內那些。"""
        self.add_facts(self.OVER_WINDOW)
        self.promote()
        self.assertEqual(len(self.durable_fact_keys()), self.OVER_WINDOW,
                         "現況檔漏掉了現行 fact —— 整檔取代把它們刪掉了")

    def test_no_fact_is_marked_durable_without_being_in_the_file(self):
        """`durable=1` 的語意是「檔裡就是我」。整檔取代把它刪掉 = 假宣稱。

        分兩輪寫才看得到這件事:第一輪全部進檔也全部標 durable=1;第二輪加了
        更新的 fact 之後,取代掉的那份少了第一輪最舊的那些,而它們在 local
        仍然自稱已耐久 —— `durable-check` 從此判 PASS 在一個不完整的鏡射上。
        """
        self.add_facts(900, stamp="2026-08-01T00:00:00Z", prefix="first")
        self.promote()
        self.add_facts(400, stamp="2026-08-20T00:00:00Z", prefix="later")
        self.promote()
        written = self.durable_fact_keys()
        marked = [row["fact_key"] for row in self.store.conn.execute(
            "SELECT fact_key FROM facts WHERE project_id=? AND durable=1",
            (self.project_id,))]
        self.assertEqual(sorted(set(marked) - written), [],
                         "有 fact 被標成已耐久,但 `.dev-flow/` 裡沒有它")

    def test_superseded_neighbours_cannot_push_a_current_fact_out(self):
        """視窗套在 status 過濾之前 → 舊帳把唯一的現況擠掉。"""
        self.add_facts(1, stamp="2020-01-01T00:00:00Z", prefix="live")
        self.add_facts(1200, status=truth.SUPERSEDED,
                       stamp="2026-08-20T00:00:00Z", prefix="old")
        self.promote()
        self.assertIn("live00000", self.durable_fact_keys(),
                      "唯一的現行 fact 被 SUPERSEDED 鄰居擠出視窗")

    def test_destructive_rebuild_returns_every_current_fact(self):
        """砍掉 local、只從 `.dev-flow/` 重建 —— local 自己說什麼不算證據。"""
        self.add_facts(self.OVER_WINDOW)
        self.promote()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        counts = sync.rebuild_local(self.repo, fresh)
        self.assertEqual(counts["facts"], self.OVER_WINDOW,
                         "重建後少了 fact —— 記憶真的不見了")
