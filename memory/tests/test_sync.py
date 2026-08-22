"""rebuild(durable → local)與 consolidate(local → durable)(§5/§13/§17/§29)。"""
import json
import os
import shutil
import subprocess
import sys
import unittest

from memtools import MEMORY_DIR, MemoryCase, commit_all, git, write
from agentmem import durable, embedding, identity, ids, query, retrieval, sync, truth
from agentmem.store import _uid


class RebuildTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        durable.write_state(self.repo, "database", "memory-store", [{
            "fact_key": "backend", "value": "sqlite-wasm", "status": "VERIFIED",
            "confidence": 0.99, "recorded_at": "2026-08-20T00:00:00Z",
            "dependencies": ["src/services/db.ts"],
            "fingerprints": {"src/services/db.ts": "sha256:aaa"}}])
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "registration",
            "title": "registration = customer-level 送檢紀錄",
            "body": "一個客戶在 submission 內的送檢紀錄",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})
        durable.write_decision(self.repo, {
            "key": "memory-backend", "title": "用 sqlite-wasm",
            "status": "ACCEPTED", "decided_at": "2026-08-20",
            "decision": "選 sqlite-wasm", "reason": "跨平台"})
        durable.write_skill(self.repo, {"key": "deploy", "title": "部署流程",
                                        "steps": ["build"],
                                        "recorded_at": "2026-08-20T00:00:00Z"})
        durable.append_events(self.repo, "ses_a", [{
            "event_id": ids.new_id("event"),
            "kind": "schema_change", "title": "改名 pgs_intake → lab_order",
            "occurred_at": "2026-08-20T01:00:00Z", "branch": "main",
            "paths": ["migrations/001.sql"]}])

    def test_rebuild_from_durable_populates_everything(self):
        store = self.store_for(self.project_id)
        counts = sync.rebuild_local(self.repo, store)
        self.assertEqual(counts["facts"], 1)
        self.assertEqual(counts["knowledge"], 1)
        self.assertEqual(counts["decisions"], 1)
        self.assertEqual(counts["skills"], 1)
        self.assertEqual(counts["events"], 1)
        self.assertGreaterEqual(store.item_count(), 5)

    def test_rebuild_is_idempotent(self):
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        first = (len(store.facts()), len(store.knowledge()), store.item_count())
        sync.rebuild_local(self.repo, store)
        self.assertEqual(
            (len(store.facts()), len(store.knowledge()), store.item_count()),
            first)

    def test_deleting_local_db_loses_nothing_durable(self):
        """§13 的核心測試:砍掉 local DB → rebuild → 記憶內容一致。"""
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        before = {
            "facts": [(f["entity_key"], f["fact_key"], f["value"], f["status"])
                      for f in store.facts()],
            "knowledge": [(k["kind"], k["key"], k["status"])
                          for k in store.knowledge()],
        }
        store.close()
        shutil.rmtree(os.path.join(self.home, "projects", self.project_id))
        fresh = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, fresh)
        after = {
            "facts": [(f["entity_key"], f["fact_key"], f["value"], f["status"])
                      for f in fresh.facts()],
            "knowledge": [(k["kind"], k["key"], k["status"])
                          for k in fresh.knowledge()],
        }
        self.assertEqual(before, after)

    def test_rebuild_preserves_local_only_and_legacy_rows(self):
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        legacy = store.add_event("important_discovery", "legacy 觀察",
                                 signal="high", legacy=True)
        local_session = store.start_session("local 對話")
        store.add_turn(local_session, "user", "只住 local 的一句話")
        sync.rebuild_local(self.repo, store)
        self.assertIn(legacy, {e["event_id"] for e in store.events(limit=50)})
        self.assertEqual(len(store.turns(local_session)), 1)

    def test_clone_to_another_path_yields_same_memory(self):
        """Mac/Windows/Linux 路徑不同、project_id 相同、記憶內容相同(§13)。"""
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        clone = self.new_repo("D-dev-project")
        shutil.copytree(durable.root(self.repo), durable.root(clone))
        cloned_id = identity.ensure_project(clone)[0]["project_id"]
        self.assertEqual(cloned_id, self.project_id)
        counts = sync.rebuild_local(clone, store)
        self.assertEqual(counts["facts"], 1)
        self.assertEqual(counts["knowledge"], 1)


class DurableMirrorFreshnessTest(MemoryCase):
    """GPT-P0-STALE-SQLITE:durable 樹變了之後,不得繼續用舊鏡射當 VERIFIED。"""

    QUESTION = "目前 lab-order 的 current_table 是什麼?"

    def _seed_source(self):
        write(self.repo, "src/services/db.ts",
              "export const table = 'lab_order'\n")
        return commit_all(self.repo, "seed src")

    def _write_state(self, value):
        fps = truth.fingerprints_for(self.repo, ["src/services/db.ts"])
        durable.write_state(self.repo, "database", "lab-order", [{
            "fact_key": "current_table", "value": value,
            "status": "VERIFIED", "confidence": 0.99,
            "recorded_at": "2026-08-20T00:00:00Z",
            "dependencies": ["src/services/db.ts"],
            "fingerprints": fps}])

    def _ask(self, store):
        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        return query.execute(store, self.repo, self.QUESTION, workspace,
                             snapshot, embedding.Embedder())

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self._seed_source()

    def _after_ensure(self, hook):
        """在 freshness 檢查剛結束時注入。舊實作沒有讀後驗證,hook 一跑就會露餡。"""
        original = sync.ensure_durable_mirror

        def wrapped(repo_root, store, embedder=None):
            rebuilt = original(repo_root, store, embedder)
            hook(repo_root)
            return rebuilt

        sync.ensure_durable_mirror = wrapped
        self.addCleanup(lambda: setattr(sync, "ensure_durable_mirror", original))

    def test_ask_does_not_return_stale_ok_when_source_changes_after_freshness_check(self):
        """freshness 檢查後、答案離開行程前,durable 樹換成 B 不得把 A 當 OK。"""
        self._write_state("old-A")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        flipped = {"n": 0}

        def mutate(_repo):
            if flipped["n"] == 0:
                flipped["n"] += 1
                self._write_state("new-B")

        self._after_ensure(mutate)
        answer = self._ask(store)
        self.assertGreaterEqual(flipped["n"], 1)
        self.assertNotEqual(answer.get("current_truth", {}).get("value"), "old-A")
        self.assertEqual(answer["current_truth"]["value"], "new-B")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)

    def test_ask_fails_closed_when_durable_never_stabilizes_during_read(self):
        """讀取期間來源一直在變 → 不得把任一中間快照當 OK。"""
        self._write_state("old-A")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        flipped = {"n": 0}

        def always_mutate(_repo):
            flipped["n"] += 1
            self._write_state("drift-{0}".format(flipped["n"]))

        self._after_ensure(always_mutate)
        with self.assertRaises(sync.DurableMirrorDrift):
            self._ask(store)
        self.assertGreaterEqual(flipped["n"], 2)

    def test_context_does_not_expose_stale_snapshot_when_source_changes_after_check(self):
        """startup context 同樣不得在 freshness 檢查後洩漏世代 A 的 VERIFIED 值。"""
        from agentmem import context as context_mod
        self._write_state("old-A")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        flipped = {"n": 0}

        def mutate(_repo):
            if flipped["n"] == 0:
                flipped["n"] += 1
                self._write_state("new-B")

        self._after_ensure(mutate)
        workspace = identity.workspace_key(self.project_id, self.repo)
        payload = context_mod.build(
            store, self.repo, workspace, identity.workspace_snapshot(self.repo))
        text = payload["text"]
        self.assertGreaterEqual(flipped["n"], 1)
        self.assertNotIn("old-A", text)
        self.assertIn("new-B", text)

    def test_ask_never_returns_stale_verified_after_durable_changes(self):
        self._write_state("old")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        first = self._ask(store)
        self.assertEqual(first["current_truth"]["value"], "old")
        self.assertEqual(first["retrieval_status"], retrieval.OK)

        self._write_state("new")
        commit_all(self.repo, "durable pulled new value")
        answer = self._ask(store)
        self.assertNotEqual(answer.get("current_truth", {}).get("value"), "old")
        self.assertEqual(answer["current_truth"]["value"], "new")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)

    def test_dirty_uncommitted_durable_is_detected(self):
        self._write_state("old")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        self._write_state("dirty-new")
        answer = self._ask(store)
        self.assertEqual(answer["current_truth"]["value"], "dirty-new")
        self.assertNotEqual(answer["current_truth"]["value"], "old")

    def test_unrelated_commit_does_not_force_wrong_invalidation(self):
        self._write_state("old")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        write(self.repo, "README.unrelated", "not durable\n")
        commit_all(self.repo, "unrelated file")
        answer = self._ask(store)
        self.assertEqual(answer["current_truth"]["value"], "old")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)

    def test_refresh_preserves_local_only_candidates_and_sessions(self):
        self._write_state("old")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        session_id = store.start_session("local only")
        store.add_turn(session_id, "user", "只住 local 的一句話")
        candidate = store.add_candidate(
            session_id, "domain",
            {"key": "local-only", "title": "未固化候選"}, "domain_expert")
        self._write_state("new")
        self._ask(store)
        self.assertEqual(len(store.turns(session_id)), 1)
        self.assertEqual(
            store.candidates(session_id)[0]["candidate_id"], candidate)
        self.assertEqual(self._ask(store)["current_truth"]["value"], "new")

    def test_two_worktrees_detect_freshness_independently(self):
        self._write_state("old")
        commit_all(self.repo, "shared old")
        git(self.repo, "branch", "other-wt")
        wt_b = os.path.join(self.work, "freshness-b")
        git(self.repo, "worktree", "add", "-q", wt_b, "other-wt")
        store_a = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store_a)
        store_b = self.store_for(self.project_id, root=wt_b)
        sync.rebuild_local(wt_b, store_b)

        self._write_state("new-in-a")
        workspace_a = identity.workspace_key(self.project_id, self.repo)
        answer_a = query.execute(
            store_a, self.repo, self.QUESTION, workspace_a,
            identity.workspace_snapshot(self.repo), embedding.Embedder())
        self.assertEqual(answer_a["current_truth"]["value"], "new-in-a")

        workspace_b = identity.workspace_key(self.project_id, wt_b)
        answer_b = query.execute(
            store_b, wt_b, self.QUESTION, workspace_b,
            identity.workspace_snapshot(wt_b), embedding.Embedder())
        self.assertEqual(answer_b["current_truth"]["value"], "old",
                         "B 的 checkout 沒變,不得被 A 的本機改寫牽連")

    def _drop_generation(self, store):
        """模擬升級前的 runtime DB:有鏡射列、沒有 durable_generation。"""
        with store.conn:
            store.conn.execute(
                "DELETE FROM meta WHERE key=?",
                (sync.DURABLE_GENERATION_META,))
        self.assertIsNone(store.get_meta(sync.DURABLE_GENERATION_META))

    def test_absent_generation_on_old_mirror_does_not_bless_stale_value(self):
        """升級路徑:舊 DB 無世代章 + git pull 新樹 → 不得把 old 當 VERIFIED。"""
        self._write_state("old")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        first = self._ask(store)
        self.assertEqual(first["current_truth"]["value"], "old")
        self.assertEqual(first["retrieval_status"], retrieval.OK)

        self._drop_generation(store)
        self._write_state("new")
        commit_all(self.repo, "durable pulled new value after upgrade")
        answer = self._ask(store)
        self.assertNotEqual(answer.get("current_truth", {}).get("value"), "old")
        self.assertEqual(answer["current_truth"]["value"], "new")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertEqual(
            store.get_meta(sync.DURABLE_GENERATION_META),
            sync.durable_generation(self.repo))

    def test_absent_generation_empty_mirror_may_stamp_without_rebuild(self):
        """沒有 durable 鏡射列時,缺世代可以只蓋章,不得清掉 local-only。"""
        store = self.store_for(self.project_id)
        session_id = store.start_session("local only seed")
        store.add_turn(session_id, "user", "只住 local 的一句話")
        rebuilt = sync.ensure_durable_mirror(self.repo, store)
        self.assertFalse(rebuilt)
        self.assertEqual(len(store.turns(session_id)), 1)
        self.assertIsNotNone(store.get_meta(sync.DURABLE_GENERATION_META))

    def test_rebuild_does_not_certify_torn_generation(self):
        """讀鏡射與蓋章之間樹變了 → 第一次不得蓋章,穩定後值與世代同一快照。"""
        self._write_state("A")
        store = self.store_for(self.project_id)
        flipped = {"n": 0}

        def mutate(_repo):
            if flipped["n"] == 0:
                flipped["n"] += 1
                self._write_state("B")

        sync._after_rebuild_read = mutate
        try:
            sync.rebuild_local(self.repo, store)
        finally:
            sync._after_rebuild_read = None

        self.assertEqual(flipped["n"], 1)
        rows = store.facts(entity_type="database", entity_key="lab-order",
                           fact_key="current_table")
        self.assertEqual(rows[0]["value"], "B")
        self.assertEqual(
            store.get_meta(sync.DURABLE_GENERATION_META),
            sync.durable_generation(self.repo))
        self.assertEqual(self._ask(store)["current_truth"]["value"], "B")
        self.assertNotEqual(self._ask(store)["current_truth"]["value"], "A")

    def test_rebuild_does_not_certify_aba_mixed_snapshot(self):
        """讀檔途中 A→B→A:不得把混鏡射蓋成世代 A。

        既有撕裂測試只覆蓋單向 A→B,以及 generation_before != after。
        ABA 是兩端雜湊相同、中間讀到的位元組卻不屬於任一端。
        """
        self._write_knowledge("aaa-one", "title-A1", "body-A1")
        self._write_knowledge("zzz-two", "title-A2", "body-A2")
        store = self.store_for(self.project_id)
        original = durable.iter_knowledge
        seen = {"n": 0}

        def mutating_iter(repo_root):
            for record in original(repo_root):
                yield record
                seen["n"] += 1
                if seen["n"] == 1:
                    self._write_knowledge("aaa-one", "title-B1", "body-B1")
                    self._write_knowledge("zzz-two", "title-B2", "body-B2")

        def restore_a(_repo):
            self._write_knowledge("aaa-one", "title-A1", "body-A1")
            self._write_knowledge("zzz-two", "title-A2", "body-A2")

        durable.iter_knowledge = mutating_iter
        sync._after_rebuild_read = restore_a
        try:
            drifted = False
            try:
                sync.rebuild_local(self.repo, store)
            except sync.DurableMirrorDrift:
                drifted = True
            titles = {row["key"]: row["title"] for row in store.knowledge()}
            mixed = (titles.get("aaa-one") == "title-A1"
                     and titles.get("zzz-two") == "title-B2")
            stamped = store.get_meta(sync.DURABLE_GENERATION_META)
            live = sync.durable_generation(self.repo)
            self.assertFalse(
                mixed and stamped == live,
                "mixed A1+B2 stamped as generation A")
            if not drifted:
                pair = (titles.get("aaa-one"), titles.get("zzz-two"))
                self.assertIn(pair, (("title-A1", "title-A2"),
                                     ("title-B1", "title-B2")))
                self.assertEqual(stamped, live)
        finally:
            durable.iter_knowledge = original
            sync._after_rebuild_read = None

    def test_rebuild_fails_closed_when_snapshot_never_stabilizes(self):
        """重試耗盡仍撕開 → 不得蓋一個對不上的世代。"""
        self._write_state("A")
        store = self.store_for(self.project_id)
        toggle = {"v": "A"}

        def always_mutate(_repo):
            toggle["v"] = "B" if toggle["v"] == "A" else "A"
            self._write_state(toggle["v"])

        sync._after_rebuild_read = always_mutate
        try:
            with self.assertRaises(sync.DurableMirrorDrift):
                sync.rebuild_local(self.repo, store)
        finally:
            sync._after_rebuild_read = None
        stamped = store.get_meta(sync.DURABLE_GENERATION_META)
        self.assertNotEqual(stamped, sync.durable_generation(self.repo))
        self.assertIn(stamped, (None, sync.UNCERTIFIED_GENERATION))

    def _write_knowledge(self, key, title, body=""):
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": key, "title": title, "body": body,
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})

    def _ask_domain(self, store, question):
        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        return query.execute(store, self.repo, question, workspace,
                             snapshot, embedding.Embedder())

    def _cli_ask(self, question):
        """公開 CLI ask 路徑(經 _resolve,不是直接 query.execute)。"""
        out = subprocess.run(
            [sys.executable, os.path.join(MEMORY_DIR, "dev-memory.py"),
             "--path", self.repo, "ask", question, "--json"],
            capture_output=True, text=True, env=dict(os.environ))
        self.assertEqual(out.returncode, 0,
                         "stdout={0}\nstderr={1}".format(out.stdout, out.stderr))
        return json.loads(out.stdout)

    def test_absent_generation_empty_db_does_not_bless_nonempty_knowledge(self):
        """升級路徑:舊 DB 無世代、零 durable 列,但樹已有 knowledge → 必須 rebuild。"""
        store = self.store_for(self.project_id)
        self.assertIsNone(store.get_meta(sync.DURABLE_GENERATION_META))
        self.assertFalse(store.has_durable_mirror())
        self._write_knowledge(
            "registration",
            "registration = customer-level 送檢紀錄",
            "一個客戶在 submission 內的送檢紀錄")
        answer = self._ask_domain(store, "registration 是什麼意思?")
        keys = [row.get("key") for row in answer.get("results") or []]
        self.assertIn("registration", keys)
        rows = store.knowledge(kind="domain", key="registration")
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["durable"])
        self.assertEqual(
            store.get_meta(sync.DURABLE_GENERATION_META),
            sync.durable_generation(self.repo))

    def test_absent_generation_empty_db_does_not_bless_nonempty_fact(self):
        """同一升級路徑,樹裡是 fact 而不是 knowledge。"""
        store = self.store_for(self.project_id)
        self.assertFalse(store.has_durable_mirror())
        self._write_state("pulled-after-upgrade")
        answer = self._ask(store)
        self.assertNotEqual(answer.get("retrieval_status"), retrieval.NO_RELIABLE_MATCH)
        self.assertEqual(answer.get("current_truth", {}).get("value"),
                         "pulled-after-upgrade")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        self.assertTrue(store.has_durable_mirror())
        self.assertEqual(
            store.get_meta(sync.DURABLE_GENERATION_META),
            sync.durable_generation(self.repo))

    def test_refresh_preserves_local_only_knowledge_retrieval(self):
        """durable 刷新不得讓已入索引的 local-only knowledge 從檢索消失。"""
        self._write_state("old")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        kid = store.upsert_knowledge({
            "kind": "domain", "key": "local-only-rule",
            "title": "local-only 檢索可見規則",
            "body": "這筆只住 SQLite,還沒進 .dev-flow",
            "authority": "domain_expert", "status": "CONFIRMED",
            "durable": False})
        uid = _uid("knowledge", kid)
        before = retrieval.search(
            store, "local-only 檢索可見規則", item_types=("knowledge",),
            embedder=embedding.Embedder())
        self.assertTrue(any(hit["item_id"] == kid for hit in before["results"]))
        self.assertIsNotNone(store.item(uid))
        row_before = store.knowledge_row(kid)
        self.assertFalse(row_before["durable"])

        self._write_state("new")
        self._ask(store)

        row_after = store.knowledge_row(kid)
        self.assertIsNotNone(row_after)
        self.assertFalse(row_after["durable"])
        self.assertEqual(row_after["status"], "CONFIRMED")
        self.assertEqual(row_after["authority"], "domain_expert")
        self.assertIsNotNone(store.item(uid))
        after = retrieval.search(
            store, "local-only 檢索可見規則", item_types=("knowledge",),
            embedder=embedding.Embedder())
        self.assertTrue(any(hit["item_id"] == kid for hit in after["results"]),
                        "local-only 列還在,但 retrieval index 沒了")

    def test_rebuild_fails_closed_on_unreadable_durable_file(self):
        """不可讀的 durable 檔不得被當成「檔案不存在」來蓋章。

        舊實作把 OSError 收成 data=None、世代雜湊 b"unreadable"、物化時略過,
        活樹同一檔仍不可讀 → 兩端雜湊對得上,缺那一檔的鏡射被蓋成新鮮。
        """
        self._write_knowledge(
            "keep-me", "title-keep", "body-keep-visible")
        self._write_knowledge(
            "must-remain", "title-remain", "UNIQUE-BODY-MUST-NOT-LEAK")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        stamped = store.get_meta(sync.DURABLE_GENERATION_META)
        self.assertIsNotNone(stamped)
        self.assertEqual(
            {row["key"] for row in store.knowledge()},
            {"keep-me", "must-remain"})

        target = durable.knowledge_file(self.repo, "domain", "must-remain")
        rel = os.path.relpath(target, durable.root(self.repo))
        rel = rel.replace(os.sep, "/")
        self._write_knowledge("keep-me", "title-keep-B", "body-keep-B")
        sync._unreadable_durable_rels = {rel}
        try:
            with self.assertRaises(durable.DurableError) as ctx:
                sync.rebuild_local(self.repo, store)
            msg = str(ctx.exception)
            self.assertIn(rel, msg)
            self.assertNotIn("UNIQUE-BODY-MUST-NOT-LEAK", msg)
        finally:
            sync._unreadable_durable_rels = None

        self.assertEqual(store.get_meta(sync.DURABLE_GENERATION_META), stamped)
        titles = {row["key"]: row["title"] for row in store.knowledge()}
        self.assertEqual(titles.get("keep-me"), "title-keep")
        self.assertEqual(titles.get("must-remain"), "title-remain")

        sync.rebuild_local(self.repo, store)
        self.assertEqual(
            store.get_meta(sync.DURABLE_GENERATION_META),
            sync.durable_generation(self.repo))
        recovered = {row["key"]: row["title"] for row in store.knowledge()}
        self.assertEqual(recovered.get("keep-me"), "title-keep-B")
        self.assertEqual(recovered.get("must-remain"), "title-remain")

    def test_failed_rebuild_does_not_keep_old_generation_stamp(self):
        """破壞性 rebuild 中途失敗後,舊世代章不得繼續證明那份鏡射。

        舊實作先清再蓋章:例外發生在蓋章前,章還是 A;來源退回 A 之後
        ensure_durable_mirror 看見章對得上就跳過,半殘 / 錯代的 DB 被當新鮮。
        """
        self._write_state("A")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        gen_a = store.get_meta(sync.DURABLE_GENERATION_META)
        self.assertEqual(gen_a, sync.durable_generation(self.repo))
        self.assertEqual(
            store.facts(entity_type="database", entity_key="lab-order",
                        fact_key="current_table")[0]["value"], "A")

        self._write_state("B")

        def boom(_repo):
            raise RuntimeError("injected failure after rebuild read")

        sync._after_rebuild_read = boom
        try:
            with self.assertRaises(RuntimeError):
                sync.rebuild_local(self.repo, store)
        finally:
            sync._after_rebuild_read = None

        store.close()
        store2 = self.store_for(self.project_id)
        self._write_state("A")
        rebuilt = sync.ensure_durable_mirror(self.repo, store2)
        self.assertTrue(
            rebuilt,
            "old A stamp must not bless a DB that was already destroyed")
        self.assertEqual(
            store2.facts(entity_type="database", entity_key="lab-order",
                         fact_key="current_table")[0]["value"], "A")
        self.assertEqual(
            store2.get_meta(sync.DURABLE_GENERATION_META),
            sync.durable_generation(self.repo))
        self.assertNotEqual(
            store2.get_meta(sync.DURABLE_GENERATION_META),
            getattr(sync, "UNCERTIFIED_GENERATION", "uncertified"))

    def test_cli_ask_embeds_new_durable_item_without_explicit_reindex(self):
        """公開 CLI ask 必須在第一次查詢前補上新 durable 項的 embedding。"""
        self._write_state("old")
        store = self.store_for(self.project_id)
        embedder = embedding.Embedder()
        sync.rebuild_local(self.repo, store, embedder=embedder)
        old_facts = store.facts(entity_type="database", entity_key="lab-order",
                                fact_key="current_table")
        old_uid = _uid("fact", old_facts[0]["fact_id"])
        self.assertIsNotNone(store.conn.execute(
            "SELECT 1 FROM embeddings WHERE item_uid=?", (old_uid,)).fetchone())

        self._write_knowledge(
            "registration",
            "registration = customer-level 送檢紀錄",
            "一個客戶在 submission 內的送檢紀錄")
        answer = self._cli_ask("registration 是什麼意思?")
        keys = [row.get("key") for row in answer.get("results") or []]
        self.assertIn("registration", keys)

        rows = store.knowledge(kind="domain", key="registration")
        self.assertEqual(len(rows), 1)
        new_uid = _uid("knowledge", rows[0]["knowledge_id"])
        self.assertIsNotNone(
            store.conn.execute(
                "SELECT 1 FROM embeddings WHERE item_uid=?", (new_uid,)
            ).fetchone(),
            "CLI ask 之後新 durable 項仍沒有 embedding")
        embedded = {row["item_uid"] for row in store.conn.execute(
            "SELECT item_uid FROM embeddings")}
        self.assertIn(new_uid, embedded)
        self.assertNotIn("knowledge:removed-durable-uid", embedded)
        hits, _skipped = embedder.search(store, "registration 是什麼意思?")
        self.assertIn(new_uid, [uid for uid, _score in hits])


class ContinuationProvenanceTest(unittest.TestCase):
    """接續紀錄不得宣稱 durable-check 覆蓋了它自己尚未存在的 commit。"""

    def test_differing_heads_without_uncovered_marker_are_dishonest(self):
        text = (
            "head == remote_head == 0e35766d338a0249937a2df407c5c87f3aefd568\n"
            "durable-check -> PASS\n"
        )
        self.assertFalse(sync.continuation_claim_is_honest(
            text,
            checked_head="0e35766d338a0249937a2df407c5c87f3aefd568",
            file_commit="e6cca58d34ee0a97d914cafc863e1a5ea9c6f43f"))

    def test_explicit_uncovered_report_commit_is_honest(self):
        text = (
            "實作 commit: 929e5781dae664f01a7b3eb8d1d941c49244ee07\n"
            "本檔 commit 不在該次檢查範圍\n"
        )
        self.assertTrue(sync.continuation_claim_is_honest(
            text,
            checked_head="929e5781dae664f01a7b3eb8d1d941c49244ee07",
            file_commit="e6cca58d338a0249937a2df407c5c87f3aefd568"))

    def test_matching_heads_are_honest_without_marker(self):
        sha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.assertTrue(sync.continuation_claim_is_honest(
            "durable-check -> PASS\n",
            checked_head=sha, file_commit=sha))


class ConsolidateTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.session = self.store.start_session("PGS 真實送檢流程")

    def test_only_confirmed_candidates_are_written(self):
        pending = self.store.add_candidate(
            self.session, "domain",
            {"key": "specimen", "title": "specimen = 單一 embryo"},
            "domain_expert")
        confirmed = self.store.add_candidate(
            self.session, "domain",
            {"key": "registration", "title": "registration = customer-level"},
            "domain_expert")
        self.store.set_candidate_status(confirmed, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertEqual(result["promoted"], 1)
        keys = [k["key"] for k in durable.iter_knowledge(self.repo)]
        self.assertEqual(keys, ["registration"])
        self.assertEqual(
            self.store.candidates(self.session, statuses=("PENDING",))[0][
                "candidate_id"], pending)

    def test_sensitive_candidate_is_kept_local_with_reason(self):
        candidate = self.store.add_candidate(
            self.session, "domain",
            {"key": "creds", "title": "連線設定",
             "body": 'DB_PASSWORD = "hunter2000"'}, "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(len(result["rejected"]), 1)
        self.assertFalse(os.path.isdir(
            os.path.join(durable.root(self.repo), "knowledge")))
        row = self.store.candidates(self.session, statuses=("LOCAL_ONLY",))[0]
        self.assertIn("敏感", row["note"])

    def test_raw_transcript_never_reaches_durable(self):
        self.store.add_turn(self.session, "user",
                            "我今天想聊聊 PGS 在真實世界的送檢流程")
        self.store.add_turn(self.session, "agent", "submission 是院所批次嗎?")
        candidate = self.store.add_candidate(
            self.session, "domain",
            {"key": "submission", "title": "submission = 院所批次送檢"},
            "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)
        blob = []
        for dirpath, _dirs, files in os.walk(durable.root(self.repo)):
            for name in files:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    blob.append(f.read())
        joined = "\n".join(blob)
        self.assertIn("submission = 院所批次送檢", joined)
        self.assertNotIn("我今天想聊聊", joined)
        self.assertNotIn("submission 是院所批次嗎?", joined)

    def test_fact_candidate_promotes_whole_entity_file(self):
        candidate = self.store.add_candidate(
            self.session, "fact",
            {"entity_type": "database", "entity_key": "memory-store",
             "fact_key": "backend", "value": "sqlite-wasm", "status": "VERIFIED",
             "title": "backend = sqlite-wasm",
             "dependencies": ["src/services/db.ts"]}, "code_inference")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertTrue(result["written"])
        data = durable.read_state(self.repo, "database", "memory-store")
        self.assertEqual(data["facts"][0]["value"], "sqlite-wasm")

    def test_event_candidate_lands_in_session_scoped_file(self):
        candidate = self.store.add_candidate(
            self.session, "event",
            {"kind": "table_rename", "title": "pgs_intake → lab_order",
             "occurred_at": "2026-08-20T05:00:00Z",
             "paths": ["migrations/001.sql"]}, "code_inference")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)
        events = list(durable.iter_events(self.repo))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "table_rename")
        self.assertIn(self.session, os.listdir(
            os.path.join(durable.root(self.repo), "events", "2026", "08"))[0])

    def test_unknown_target_kind_is_refused_not_guessed(self):
        candidate = self.store.add_candidate(
            self.session, "nonsense", {"key": "x", "title": "y"}, "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, self.session)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(result["rejected"][0]["target_kind"], "nonsense")


class FactConsolidationTest(MemoryCase):
    """fact 候選只宣告依賴、沒帶指紋時,固化當下要對當前 checkout 現算。

    這條是實際踩到的缺陷:少了現算,fact 會以「VERIFIED 但沒有任何指紋」落地,
    查詢時只能降級成 CANDIDATE(無從驗證)—— 宣告了依賴卻等於沒宣告,
    而且 durable 檔看起來完全正常。
    """

    def setUp(self):
        super().setUp()
        from memtools import commit_all, write
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/services/db.ts", "export const t = 'lab_order'\n")
        commit_all(self.repo, "seed src")
        self.session = self.store.start_session("記錄現況事實")

    def test_fingerprints_are_computed_at_consolidation(self):
        import json
        from agentmem import identity, truth
        candidate = self.store.add_candidate(
            self.session, "fact",
            {"entity_type": "database", "entity_key": "lab-order",
             "fact_key": "current_table", "value": "lab_order",
             "title": "current_table = lab_order", "status": "VERIFIED",
             "confidence": 0.99, "dependencies": ["src/services/db.ts"]},
            "current_code")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)

        row = self.store.facts(entity_type="database", entity_key="lab-order",
                               fact_key="current_table", limit=1)[0]
        fingerprints = json.loads(row["fingerprints_json"])
        self.assertEqual(sorted(fingerprints), ["src/services/db.ts"])
        self.assertTrue(fingerprints["src/services/db.ts"].startswith("sha256:"))

        # 有指紋才拿得到 fast path(沒有指紋會被降級成 CANDIDATE)
        workspace = identity.workspace_key(self.project_id, self.repo)
        resolved = truth.resolve_current(
            self.store, self.repo, "database", "lab-order", "current_table",
            workspace, identity.workspace_snapshot(self.repo))
        self.assertEqual(resolved["status"], truth.VERIFIED)
        self.assertTrue(resolved["fast_path"])

        # durable 檔也帶著指紋(換一台機器 rebuild 回來才驗得住)
        data = durable.read_state(self.repo, "database", "lab-order")
        self.assertIn("fingerprints", data["facts"][0])

    def test_explicit_fingerprints_are_not_overwritten(self):
        import json
        candidate = self.store.add_candidate(
            self.session, "fact",
            {"entity_type": "database", "entity_key": "lab-order",
             "fact_key": "current_table", "value": "lab_order",
             "title": "t", "status": "VERIFIED",
             "dependencies": ["src/services/db.ts"],
             "fingerprints": {"src/services/db.ts": "sha256:supplied"}},
            "current_code")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        sync.consolidate(self.repo, self.store, self.session)
        row = self.store.facts(fact_key="current_table", limit=1)[0]
        self.assertEqual(json.loads(row["fingerprints_json"]),
                         {"src/services/db.ts": "sha256:supplied"})


class OrphanCandidateTest(MemoryCase):
    """候選必須掛在真實存在的 session 上 —— durable writer 是最後一道防線。

    devtalk/session 層已經擋過「沒有 start 就 propose」,但 store 是內部 API,
    直接呼叫它塞候選會繞過那一層。durable 寫入不可逆(進了 commit 就在歷史裡),
    所以最後有機會攔下來的地方一定要攔。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)

    def test_candidate_with_unknown_session_is_not_consolidated(self):
        orphan = "ses_0000000000000000000000000X"
        candidate = self.store.add_candidate(
            orphan, "domain", {"key": "smuggled", "title": "偷渡的知識"},
            "domain_expert")
        self.store.set_candidate_status(candidate, "CONFIRMED")
        result = sync.consolidate(self.repo, self.store, orphan)
        self.assertEqual(result["promoted"], 0)
        self.assertEqual(len(result["rejected"]), 1)
        self.assertEqual(list(durable.iter_knowledge(self.repo)), [])
        row = self.store.candidates(orphan, statuses=("LOCAL_ONLY",))[0]
        self.assertIn("session", row["note"])

    def test_orphan_candidate_does_not_block_valid_ones(self):
        orphan = "ses_0000000000000000000000000X"
        bad = self.store.add_candidate(
            orphan, "domain", {"key": "smuggled", "title": "偷渡"},
            "domain_expert")
        self.store.set_candidate_status(bad, "CONFIRMED")
        real = self.store.start_session("真的 session")
        good = self.store.add_candidate(
            real, "domain", {"key": "legit", "title": "正常的知識"},
            "domain_expert")
        self.store.set_candidate_status(good, "CONFIRMED")
        self.assertEqual(sync.consolidate(self.repo, self.store, real)["promoted"], 1)
        self.assertEqual([k["key"] for k in durable.iter_knowledge(self.repo)],
                         ["legit"])


class DurableSymlinkRejectionTest(MemoryCase):
    """snapshot 不得跟隨 symlink 把 .dev-flow/ 外的位元組蓋進世代章。"""

    SECRET = "SMUGGLED-EXTERNAL-BYTES-MUST-NOT-BECOME-DURABLE"

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]

    def _can_symlink(self):
        probe = os.path.join(self.work, "symlink-probe-src")
        dest = os.path.join(self.work, "symlink-probe-dst")
        with open(probe, "w", encoding="utf-8") as stream:
            stream.write("x")
        try:
            os.symlink(probe, dest)
        except (OSError, NotImplementedError, AttributeError):
            return False
        return True

    def _write_regular_knowledge(self, key, title):
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": key, "title": title,
            "body": "regular-file-positive-control",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})

    def _plant_symlink(self, key):
        outside = os.path.join(self.work, "local-memory.yaml")
        with open(outside, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(
                "schema_version: 1\n"
                "kind: domain\n"
                "key: {0}\n"
                "title: smuggled = {1}\n"
                "body: {1}\n"
                "authority: domain_expert\n"
                "status: CONFIRMED\n"
                "recorded_at: 2026-08-20T00:00:00Z\n".format(key, self.SECRET))
        dest = durable.knowledge_file(self.repo, "domain", key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # 目標用絕對路徑:相對路徑在不同 cwd 下會指錯,那不是這條要測的。
        os.symlink(os.path.realpath(outside), dest)
        return dest, outside

    def test_symlink_durable_file_fails_closed_and_cannot_import_external_bytes(self):
        if not self._can_symlink():
            self.skipTest("this platform cannot create symlinks")
        self._write_regular_knowledge("keep-me", "keep-me = regular")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        stamped = store.get_meta(sync.DURABLE_GENERATION_META)
        dest, outside = self._plant_symlink("smuggled")
        rel = os.path.relpath(dest, durable.root(self.repo)).replace(os.sep, "/")

        with self.assertRaises(durable.DurableError) as ctx:
            sync.durable_generation(self.repo)
        msg = str(ctx.exception)
        self.assertIn(rel, msg)
        self.assertNotIn(self.SECRET, msg)

        with self.assertRaises(durable.DurableError):
            sync.rebuild_local(self.repo, store)
        self.assertEqual(store.get_meta(sync.DURABLE_GENERATION_META), stamped)
        keys = {row["key"] for row in store.knowledge()}
        self.assertNotIn("smuggled", keys)
        self.assertNotIn(self.SECRET, json.dumps(
            [row["title"] + row["body"] for row in store.knowledge()]))

        with open(outside, "w", encoding="utf-8") as stream:
            stream.write("schema_version: 1\nkind: domain\nkey: smuggled\n"
                         "title: mutated-target\nauthority: domain_expert\n"
                         "status: CONFIRMED\nrecorded_at: 2026-08-20T00:00:00Z\n")
        with self.assertRaises(durable.DurableError):
            sync.ensure_durable_mirror(self.repo, store)
        self.assertNotIn(
            "mutated-target",
            " ".join(row["title"] for row in store.knowledge()))

    def test_regular_durable_file_still_rebuilds(self):
        self._write_regular_knowledge("keep-me", "keep-me = regular")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        rows = store.knowledge(kind="domain", key="keep-me")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "keep-me = regular")
        self.assertTrue(rows[0]["durable"])


class DurableRootSymlinkRejectionTest(MemoryCase):
    """`.dev-flow` 自己是 symlink 時,讀取/健康路徑不得把樹外當正本。"""

    SECRET = "EXTERNAL-BRAIN-MUST-NOT-BE-IMPORTED"

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]

    def _can_symlink(self):
        probe = os.path.join(self.work, "root-symlink-probe-src")
        dest = os.path.join(self.work, "root-symlink-probe-dst")
        with open(probe, "w", encoding="utf-8") as stream:
            stream.write("x")
        try:
            os.symlink(probe, dest)
        except (OSError, NotImplementedError, AttributeError):
            return False
        return True

    def _write_regular(self, key, title):
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": key, "title": title,
            "body": "regular-root-positive-control",
            "authority": "domain_expert", "status": "CONFIRMED",
            "recorded_at": "2026-08-20T00:00:00Z"})

    def _plant_root_symlink(self):
        outside_repo = os.path.join(self.work, "fake-repo")
        os.makedirs(outside_repo, exist_ok=True)
        durable.write_knowledge(outside_repo, {
            "kind": "domain", "key": "smuggled",
            "title": "smuggled = {0}".format(self.SECRET),
            "body": self.SECRET, "authority": "domain_expert",
            "status": "CONFIRMED", "recorded_at": "2026-08-20T00:00:00Z"})
        identity.ensure_project(outside_repo, name="fake")
        real = durable.root(self.repo)
        parked = real + ".parked"
        os.rename(real, parked)
        os.symlink(os.path.realpath(durable.root(outside_repo)), real)
        return durable.root(outside_repo)

    def test_symlinked_devflow_root_fails_closed_and_cannot_import(self):
        if not self._can_symlink():
            self.skipTest("this platform cannot create symlinks")
        self._write_regular("keep-me", "keep-me = regular")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        stamped = store.get_meta(sync.DURABLE_GENERATION_META)
        self._plant_root_symlink()

        with self.assertRaises(durable.DurableError):
            sync.durable_generation(self.repo)
        with self.assertRaises(durable.DurableError):
            sync.rebuild_local(self.repo, store)
        with self.assertRaises(durable.DurableError):
            durable.has_mirrorable_content(self.repo)
        self.assertEqual(store.get_meta(sync.DURABLE_GENERATION_META), stamped)
        keys = {row["key"] for row in store.knowledge()}
        self.assertNotIn("smuggled", keys)
        self.assertNotIn(self.SECRET, json.dumps(
            [row["title"] + row["body"] for row in store.knowledge()]))

        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        with self.assertRaises(durable.DurableError):
            query.execute(store, self.repo, "smuggled 是什麼意思",
                          workspace, snapshot)
        with self.assertRaises(durable.DurableError):
            from agentmem import context
            context.build(store, self.repo, workspace, snapshot)

        from agentmem import setup
        report = setup.doctor(self.repo)
        self.assertEqual(report["verdict"], "FAIL")
        readable = [row for row in report["findings"]
                    if row["check"] == "durable-source-readable"]
        self.assertEqual(len(readable), 1, report["findings"])
        self.assertEqual(readable[0]["level"], "error")
        blob = json.dumps(report, ensure_ascii=False)
        self.assertNotIn(self.SECRET, blob)

    def test_regular_devflow_root_still_rebuilds(self):
        self._write_regular("keep-me", "keep-me = regular")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        rows = store.knowledge(kind="domain", key="keep-me")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "keep-me = regular")

    def test_absent_devflow_keeps_absent_semantics(self):
        empty = self.new_repo("no-devflow")
        kind, entries = sync._snapshot_durable_files(empty)
        self.assertEqual(kind, "absent")
        self.assertEqual(entries, [])
        self.assertFalse(durable.has_mirrorable_content(empty))
        self.assertEqual(
            sync.durable_generation(empty),
            sync._generation_of("absent", []))


class MirrorRevisionCertificationTest(MemoryCase):
    """讀取認證必須綁 per-worktree 單調 mirror revision,否則 ABA 會過。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]

    def _write(self, key, title):
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": key, "title": title,
            "body": title, "authority": "domain_expert",
            "status": "CONFIRMED", "recorded_at": "2026-08-20T00:00:00Z"})

    def _second_store(self):
        from agentmem import store as store_mod
        opened = store_mod.open_for_root(self.project_id, self.repo)
        self.addCleanup(opened.close)
        return opened

    def test_same_worktree_rebuild_aba_rejects_stale_read_token(self):
        self._write("topic", "title-A")
        store1 = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store1)
        _rebuilt, certified, revision = sync.observe_certified_generation(
            self.repo, store1)
        token_gen = certified
        token_rev = revision

        store2 = self._second_store()
        self._write("topic", "title-B")
        sync.rebuild_local(self.repo, store2)
        self._write("topic", "title-A")

        self.assertEqual(sync.durable_generation(self.repo), token_gen)
        self.assertFalse(sync.generation_still_certified(
            self.repo, token_gen, store1, token_rev))

    def test_aba_two_completed_rebuilds_invalidates_original_token(self):
        self._write("topic", "title-A")
        store1 = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store1)
        _rebuilt, certified, revision = sync.observe_certified_generation(
            self.repo, store1)

        store2 = self._second_store()
        self._write("topic", "title-B")
        sync.rebuild_local(self.repo, store2)
        self._write("topic", "title-A")
        sync.rebuild_local(self.repo, store2)

        self.assertEqual(
            store2.get_meta(sync.DURABLE_GENERATION_META), certified)
        self.assertEqual(sync.durable_generation(self.repo), certified)
        self.assertFalse(sync.generation_still_certified(
            self.repo, certified, store1, revision))

    def test_ask_does_not_return_foreign_mirror_after_aba_rebuild(self):
        self._write("registration", "title-A")
        store = self.store_for(self.project_id)
        sync.rebuild_local(self.repo, store)
        flipped = {"n": 0}

        def hijack(_repo):
            if flipped["n"] != 0:
                return
            flipped["n"] += 1
            other = self._second_store()
            self._write("registration", "title-B")
            sync.rebuild_local(self.repo, other)
            self._write("registration", "title-A")

        original = sync.observe_certified_generation

        def wrapped(repo_root, store_obj, embedder=None):
            result = original(repo_root, store_obj, embedder)
            hijack(repo_root)
            return result

        sync.observe_certified_generation = wrapped
        self.addCleanup(lambda: setattr(
            sync, "observe_certified_generation", original))

        workspace = identity.workspace_key(self.project_id, self.repo)
        snapshot = identity.workspace_snapshot(self.repo)
        answer = query.execute(
            store, self.repo, "registration 是什麼意思", workspace, snapshot)
        self.assertGreaterEqual(flipped["n"], 1)
        blob = json.dumps(answer, ensure_ascii=False)
        self.assertNotIn("title-B", blob)
        self.assertIn("title-A", blob)
