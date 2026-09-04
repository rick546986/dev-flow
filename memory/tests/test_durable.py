"""`.dev-flow/` durable 檔案:deterministic、路徑可攜、conflict fail-loud(§6/§30)。"""
import errno
import os
from unittest import mock

from memtools import MemoryCase, read_file, write
from agentmem import durable, identity, ids, paths


def sample_fact(**over):
    record = {"fact_key": "backend", "value": "sqlite-wasm", "status": "VERIFIED",
              "confidence": 0.99, "recorded_at": "2026-08-20T00:00:00Z",
              "dependencies": ["src/services/db.ts", "package.json"],
              "fingerprints": {"src/services/db.ts": "sha256:aaa",
                               "package.json": "sha256:bbb"},
              "verified_commit": "abc123"}
    record.update(over)
    return record


class LayoutTest(MemoryCase):
    def test_lazy_create_only_requested_dirs(self):
        created = durable.ensure_layout(self.repo, [durable.STATE_DIR])
        self.assertEqual(len(created), 1)
        root = durable.root(self.repo)
        self.assertTrue(os.path.isdir(os.path.join(root, "state", "implementation")))
        self.assertFalse(os.path.isdir(os.path.join(root, "skills")))

    def test_slug_is_filename_safe_and_collision_free(self):
        a = durable.slug("registration 送檢紀錄")
        b = durable.slug("registration 送檢批次")
        self.assertNotEqual(a, b)
        for value in (a, b):
            self.assertTrue(value.isascii(), value)
            self.assertNotIn("/", value)
            self.assertNotIn(" ", value)
        self.assertEqual(a, durable.slug("registration 送檢紀錄"))

    def test_slug_rejects_empty_key(self):
        with self.assertRaises(durable.DurableError):
            durable.slug("   ")


class StateFileTest(MemoryCase):
    def test_write_and_read_round_trip(self):
        durable.write_state(self.repo, "database", "memory-store", [sample_fact()])
        data = durable.read_state(self.repo, "database", "memory-store")
        self.assertEqual(data["entity_type"], "database")
        self.assertEqual(data["facts"][0]["value"], "sqlite-wasm")
        self.assertEqual(data["facts"][0]["fingerprints"]["package.json"],
                         "sha256:bbb")

    def test_serialization_is_deterministic(self):
        path = durable.write_state(self.repo, "database", "memory-store",
                                   [sample_fact(), sample_fact(fact_key="port",
                                                               value="38888")])
        first = read_file(path)
        durable.write_state(self.repo, "database", "memory-store",
                            [sample_fact(fact_key="port", value="38888"),
                             sample_fact()])
        self.assertEqual(read_file(path), first)
        self.assertNotIn("\r", first)

    def test_absolute_dependency_is_rejected(self):
        with self.assertRaises(paths.NonPortablePath):
            durable.write_state(self.repo, "database", "memory-store",
                                [sample_fact(dependencies=["/Users/rick/db.ts"])])

    def test_no_absolute_path_leaks_into_durable_tree(self):
        durable.write_state(self.repo, "database", "memory-store", [sample_fact()])
        for dirpath, _dirs, files in os.walk(durable.root(self.repo)):
            for name in files:
                text = read_file(os.path.join(dirpath, name))
                self.assertEqual(paths.scan_absolute_paths(text), [],
                                 os.path.join(dirpath, name))

    def test_git_conflict_marker_fails_loud(self):
        durable.write_state(self.repo, "database", "memory-store", [sample_fact()])
        path = durable.state_file(self.repo, "database", "memory-store")
        with open(path, "a", encoding="utf-8") as stream:
            stream.write("<<<<<<< HEAD\n")
        with self.assertRaises(durable.DurableError):
            durable.read_state(self.repo, "database", "memory-store")


class KnowledgeFileTest(MemoryCase):
    def test_domain_knowledge_round_trip(self):
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "registration",
            "title": "registration = customer-level 送檢紀錄",
            "body": "一個客戶在 submission 內的送檢紀錄,不是 embryo",
            "authority": "domain_expert", "status": "CONFIRMED",
            "confidence": 0.95, "recorded_at": "2026-08-20T00:00:00Z",
            "evidence": [{"type": "user_confirmation", "ref": "ses_x"}]})
        records = list(durable.iter_knowledge(self.repo))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["authority"], "domain_expert")
        self.assertEqual(records[0]["status"], "CONFIRMED")

    def test_intent_records_implemented_flag(self):
        durable.write_knowledge(self.repo, {
            "kind": "intent", "key": "shared-lab-order",
            "title": "未來共用 lab order 架構", "authority": "product_decision",
            "status": "CONFIRMED", "implemented": False,
            "recorded_at": "2026-08-20T00:00:00Z"})
        record = list(durable.iter_knowledge(self.repo))[0]
        self.assertIs(record["implemented"], False)

    def test_unknown_kind_rejected(self):
        with self.assertRaises(durable.DurableError):
            durable.knowledge_file(self.repo, "nonsense", "k")

    def test_file_evidence_must_be_relative(self):
        with self.assertRaises(paths.NonPortablePath):
            durable.write_knowledge(self.repo, {
                "kind": "domain", "key": "k", "title": "t",
                "authority": "domain_expert",
                "evidence": [{"type": "file", "ref": "/Users/rick/x.ts"}]})


class DecisionFileTest(MemoryCase):
    RECORD = {"key": "memory-backend", "title": "用 sqlite-wasm 當 backend",
              "status": "ACCEPTED", "decided_at": "2026-08-20",
              "decision": "選 sqlite-wasm", "alternatives": "indexeddb / 純記憶體",
              "reason": "跨平台一致", "tradeoff": "包體積變大"}

    def test_round_trip_keeps_prose_and_machine_fields(self):
        path = durable.write_decision(self.repo, self.RECORD)
        self.assertTrue(os.path.basename(path).startswith("DEC-"))
        record = list(durable.iter_decisions(self.repo))[0]
        self.assertEqual(record["status"], "ACCEPTED")
        self.assertEqual(record["reason"], "跨平台一致")
        self.assertEqual(record["title"], "用 sqlite-wasm 當 backend")

    def test_decision_without_machine_block_fails_loud(self):
        with self.assertRaises(durable.DurableError):
            durable.parse_decision("# DEC-x — t\n\n## Decision\n\n只有散文\n")


class EventFileTest(MemoryCase):
    def test_events_are_split_per_session_and_month(self):
        durable.append_events(self.repo, "ses_mac", [
            {"event_id": "evt_1", "kind": "schema_change", "title": "a",
             "occurred_at": "2026-08-20T01:00:00Z"}])
        durable.append_events(self.repo, "ses_windows", [
            {"event_id": "evt_2", "kind": "schema_change", "title": "b",
             "occurred_at": "2026-08-20T02:00:00Z"}])
        durable.append_events(self.repo, "ses_mac", [
            {"event_id": "evt_3", "kind": "schema_change", "title": "c",
             "occurred_at": "2026-09-01T00:00:00Z"}])
        found = []
        for dirpath, _dirs, files in os.walk(
                os.path.join(durable.root(self.repo), "events")):
            for name in files:
                found.append(os.path.relpath(os.path.join(dirpath, name),
                                             durable.root(self.repo)))
        # 兩個 session × 同月 = 兩檔;跨月再多一檔 → Mac 與 Windows 不會 append 同一檔
        self.assertEqual(len(found), 3, found)
        self.assertEqual(len(list(durable.iter_events(self.repo))), 3)

    def test_append_is_additive(self):
        for i in range(3):
            durable.append_events(self.repo, "ses_a", [
                {"event_id": "evt_%d" % i, "kind": "schema_change",
                 "title": "t%d" % i, "occurred_at": "2026-08-20T0%d:00:00Z" % i}])
        self.assertEqual(len(list(durable.iter_events(self.repo))), 3)

    def test_appending_the_same_event_id_twice_writes_one_line(self):
        """去重是 append-only writer 的重跑安全網(見 append_events 的註解)。"""
        record = {"event_id": "evt_dupe", "kind": "schema_change",
                  "title": "a", "occurred_at": "2026-08-20T01:00:00Z"}
        durable.append_events(self.repo, "ses_a", [record])
        written = durable.append_events(self.repo, "ses_a", [dict(record)])
        self.assertEqual(written, [], "整批都已在檔裡時不得再動檔案")
        self.assertEqual(len(list(durable.iter_events(self.repo))), 1)

    def test_same_event_id_with_different_content_fails_loud(self):
        """同 id 不同內容不是重跑,是兩件事共用一個身分 —— 不得靜默丟掉後者。

        去重把「id 已經在檔裡」當成「這筆已經寫過了」。那個推論只有在 id 真的
        決定內容時成立。推導 id 的來源(candidate_id / revision_id)撞號、或
        推導規則有瑕疵時,第二筆的內容會被靜默丟棄 —— 而它是**不同**的事實。
        寧可讓 checkpoint 紅掉由人裁決,不要留一筆看起來成功的假紀錄。
        """
        record = {"event_id": "evt_clash", "kind": "schema_change",
                  "title": "改名 a → b", "occurred_at": "2026-08-20T01:00:00Z"}
        durable.append_events(self.repo, "ses_a", [record])
        clash = dict(record, title="其實是改名 c → d")
        with self.assertRaises(durable.DurableError):
            durable.append_events(self.repo, "ses_a", [clash])
        events = list(durable.iter_events(self.repo))
        self.assertEqual([e["title"] for e in events], ["改名 a → b"],
                         "拒收之後檔案內容不得被動過")

    def test_same_event_id_twice_in_one_batch_with_different_content(self):
        """同一批裡撞號也一樣 —— 檔裡還沒有它,不代表可以只寫第一筆。"""
        base = {"event_id": "evt_batch", "kind": "schema_change",
                "occurred_at": "2026-08-20T01:00:00Z"}
        with self.assertRaises(durable.DurableError):
            durable.append_events(self.repo, "ses_a",
                                  [dict(base, title="a"), dict(base, title="b")])

    def test_event_without_event_id_is_rejected(self):
        """認不出身分的事件無法去重 —— 寫下去就是重跑必然變兩筆的紀錄。"""
        with self.assertRaises(durable.DurableError):
            durable.append_events(self.repo, "ses_a", [
                {"title": "x", "occurred_at": "2026-08-20T00:00:00Z"}])

    def test_bad_timestamp_fails_loud(self):
        with self.assertRaises(durable.DurableError):
            durable.append_events(self.repo, "ses_a",
                                  [{"title": "x", "occurred_at": "not-a-date"}])

    def test_absolute_path_in_event_rejected(self):
        with self.assertRaises(paths.NonPortablePath):
            durable.append_events(self.repo, "ses_a", [
                {"event_id": "evt_x", "title": "x",
                 "occurred_at": "2026-08-20T00:00:00Z",
                 "paths": ["/Users/rick/x.ts"]}])

    def test_corrupt_jsonl_fails_loud(self):
        durable.append_events(self.repo, "ses_a", [
            {"event_id": ids.new_id("event"), "title": "x",
             "occurred_at": "2026-08-20T00:00:00Z"}])
        path = durable.event_file(self.repo, "ses_a", "2026-08-20T00:00:00Z")
        with open(path, "a", encoding="utf-8") as stream:
            stream.write("{not json}\n")
        with self.assertRaises(durable.DurableError):
            list(durable.iter_events(self.repo))


class InventoryTest(MemoryCase):
    def test_inventory_counts_every_kind(self):
        durable.write_state(self.repo, "database", "memory-store", [sample_fact()])
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "k", "title": "t",
            "authority": "domain_expert", "recorded_at": "2026-08-20T00:00:00Z"})
        durable.write_decision(self.repo, DecisionFileTest.RECORD)
        durable.write_skill(self.repo, {"key": "deploy", "title": "部署",
                                        "steps": ["build", "push"],
                                        "recorded_at": "2026-08-20T00:00:00Z"})
        durable.append_events(self.repo, "ses_a", [
            {"event_id": ids.new_id("event"), "title": "x",
             "occurred_at": "2026-08-20T00:00:00Z"}])
        self.assertEqual(durable.inventory(self.repo),
                         {"facts": 1, "knowledge": 1, "decisions": 1,
                          "skills": 1, "events": 1, "entities": 1})


class SensitiveContentGateTest(MemoryCase):
    """四個耐久寫入函式各自要對自己落盤的內容欄位重掃敏感內容(issue #107)。

    刻意繞過 `sync.consolidate()`/`signal.gate()`,直接呼叫 writer ——
    模擬「呼叫端沒有先過閘」的情境;writer 自己必須是最後一道閘,
    縱深防禦就是要重掃已經被掃過的內容,不是只信任呼叫端。
    """

    def test_write_state_rejects_secret_in_value(self):
        with self.assertRaises(durable.DurableError):
            durable.write_state(self.repo, "database", "memory-store",
                                [sample_fact(value="AKIAIOSFODNN7EXAMPLE")])
        self.assertIsNone(
            durable.read_state(self.repo, "database", "memory-store"),
            "被拒絕的內容不得落盤")

    def test_write_state_allows_benign_value(self):
        durable.write_state(self.repo, "database", "memory-store",
                            [sample_fact()])
        data = durable.read_state(self.repo, "database", "memory-store")
        self.assertEqual(data["facts"][0]["value"], "sqlite-wasm")

    def test_write_knowledge_rejects_secret_in_body(self):
        with self.assertRaises(durable.DurableError):
            durable.write_knowledge(self.repo, {
                "kind": "domain", "key": "k", "title": "t",
                "body": "password=hunter2secret", "authority": "domain_expert",
                "recorded_at": "2026-08-20T00:00:00Z"})
        self.assertEqual(list(durable.iter_knowledge(self.repo)), [])

    def test_write_knowledge_allows_benign_body(self):
        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "k", "title": "t",
            "body": "一段不含敏感內容的說明", "authority": "domain_expert",
            "recorded_at": "2026-08-20T00:00:00Z"})
        self.assertEqual(len(list(durable.iter_knowledge(self.repo))), 1)

    def test_write_decision_rejects_secret_in_reason(self):
        record = dict(DecisionFileTest.RECORD,
                      reason="外洩憑證 AKIAIOSFODNN7EXAMPLE 留在這裡")
        with self.assertRaises(durable.DurableError):
            durable.write_decision(self.repo, record)
        self.assertEqual(list(durable.iter_decisions(self.repo)), [])

    def test_write_decision_allows_benign_content(self):
        durable.write_decision(self.repo, DecisionFileTest.RECORD)
        self.assertEqual(len(list(durable.iter_decisions(self.repo))), 1)

    def test_write_skill_rejects_secret_in_step(self):
        with self.assertRaises(durable.DurableError):
            durable.write_skill(self.repo, {
                "key": "deploy", "title": "部署",
                "steps": ["build", "password=hunter2secret"],
                "recorded_at": "2026-08-20T00:00:00Z"})
        self.assertEqual(list(durable.iter_skills(self.repo)), [])

    def test_write_skill_allows_benign_steps(self):
        durable.write_skill(self.repo, {
            "key": "deploy", "title": "部署", "steps": ["build", "push"],
            "recorded_at": "2026-08-20T00:00:00Z"})
        self.assertEqual(len(list(durable.iter_skills(self.repo))), 1)

    def test_rejection_message_names_pattern_not_value(self):
        """拒絕訊息只能講中槍的 pattern 名稱,不能把值本身抄一份進錯誤訊息。"""
        try:
            durable.write_state(self.repo, "database", "memory-store",
                                [sample_fact(value="AKIAIOSFODNN7EXAMPLE")])
            self.fail("應該要被拒絕")
        except durable.DurableError as exc:
            message = str(exc)
            self.assertIn("aws_access_key", message)
            self.assertNotIn("AKIAIOSFODNN7EXAMPLE", message)


class DirectoryFsyncTest(MemoryCase):
    """`os.replace` 落地後,目錄項本身也要盡快 fsync(issue #107)。"""

    def _requires_dirfd_path(self):
        if not (hasattr(os, "O_DIRECTORY") and hasattr(os, "O_NOFOLLOW")):
            self.skipTest("this platform has no O_NOFOLLOW dirfd write path")

    def test_fsync_called_on_directory_fd_after_replace(self):
        self._requires_dirfd_path()
        events = []
        original_fsync = os.fsync
        original_replace = os.replace

        replace_dirfds = []

        def spy_fsync(fd):
            events.append(("fsync", fd))
            return original_fsync(fd)

        def spy_replace(*args, **kwargs):
            replace_dirfds.append(kwargs.get("dst_dir_fd"))
            events.append(("replace",))
            return original_replace(*args, **kwargs)

        with mock.patch("os.fsync", side_effect=spy_fsync), \
             mock.patch("os.replace", side_effect=spy_replace):
            durable.write_knowledge(self.repo, {
                "kind": "domain", "key": "fsync-k", "title": "t", "body": "b",
                "authority": "domain_expert",
                "recorded_at": "2026-08-20T00:00:00Z"})

        replace_positions = [i for i, e in enumerate(events)
                             if e[0] == "replace"]
        self.assertEqual(len(replace_positions), 1, events)
        self.assertEqual(len(replace_dirfds), 1, replace_dirfds)
        target_dirfd = replace_dirfds[0]
        self.assertIsNotNone(target_dirfd, "os.replace 必須帶 dst_dir_fd")
        after_replace = events[replace_positions[0] + 1:]
        self.assertIn(
            ("fsync", target_dirfd), after_replace,
            "os.replace 之後必須對*同一個*目錄 fd 呼叫過一次 os.fsync,"
            "不能只是隨便哪個 fd;events={0}".format(events))

    def test_directory_fsync_einval_does_not_fail_the_write(self):
        """macOS 部分檔案系統對目錄 fd 的 fsync 回 EINVAL;寫入仍須成功。"""
        self._requires_dirfd_path()
        original_fsync = os.fsync
        original_replace = os.replace
        state = {"replaced": False}

        def picky_fsync(fd):
            if state["replaced"]:
                raise OSError(errno.EINVAL, "Invalid argument")
            return original_fsync(fd)

        def spy_replace(*args, **kwargs):
            result = original_replace(*args, **kwargs)
            state["replaced"] = True
            return result

        with mock.patch("os.fsync", side_effect=picky_fsync), \
             mock.patch("os.replace", side_effect=spy_replace):
            path = durable.write_knowledge(self.repo, {
                "kind": "domain", "key": "fsync-einval", "title": "t",
                "body": "b", "authority": "domain_expert",
                "recorded_at": "2026-08-20T00:00:00Z"})
        self.assertTrue(
            os.path.isfile(path),
            "目錄 fd 的 fsync 回 EINVAL 時,寫入仍必須成功")
        record = list(durable.iter_knowledge(self.repo))
        self.assertEqual(len(record), 1)


def _can_symlink(work):
    probe = os.path.join(work, "symlink-probe-src")
    dest = os.path.join(work, "symlink-probe-dst")
    with open(probe, "w", encoding="utf-8") as stream:
        stream.write("x")
    try:
        os.symlink(probe, dest)
    except (OSError, NotImplementedError, AttributeError):
        return False
    return True


class DurableWriterConfinementTest(MemoryCase):
    """durable writer 不得跟隨 symlink 把檔寫出 repo 邊界。"""

    def _outside(self, name):
        path = os.path.join(self.work, name)
        os.makedirs(path, exist_ok=True)
        marker = os.path.join(path, "UNCHANGED-MARKER")
        with open(marker, "w", encoding="utf-8") as stream:
            stream.write("keep")
        return path

    def _outside_names(self, path):
        return set(os.listdir(path))

    def _knowledge(self, key="confine-k"):
        return {
            "kind": "domain", "key": key, "title": "confine title",
            "body": "benign-domain-body", "authority": "domain_expert",
            "status": "CONFIRMED", "recorded_at": "2026-08-20T00:00:00Z"}

    def test_write_knowledge_refuses_symlinked_domain_dir(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        outside = self._outside("outside-domain")
        before = self._outside_names(outside)
        dest = os.path.join(durable.root(self.repo), "knowledge", "domain")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.symlink(os.path.realpath(outside), dest)
        with self.assertRaises(durable.DurableError):
            durable.write_knowledge(self.repo, self._knowledge())
        self.assertEqual(self._outside_names(outside), before)

    def test_write_state_refuses_symlinked_state_dir(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        outside = self._outside("outside-state")
        before = self._outside_names(outside)
        dest = os.path.join(durable.root(self.repo), "state", "implementation")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.symlink(os.path.realpath(outside), dest)
        with self.assertRaises(durable.DurableError):
            durable.write_state(self.repo, "database", "memory-store",
                                [sample_fact()])
        self.assertEqual(self._outside_names(outside), before)

    def test_write_decision_refuses_symlinked_decisions_dir(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        outside = self._outside("outside-decisions")
        before = self._outside_names(outside)
        dest = os.path.join(durable.root(self.repo), "decisions")
        os.makedirs(durable.root(self.repo), exist_ok=True)
        os.symlink(os.path.realpath(outside), dest)
        with self.assertRaises(durable.DurableError):
            durable.write_decision(self.repo, DecisionFileTest.RECORD)
        self.assertEqual(self._outside_names(outside), before)

    def test_write_skill_refuses_symlinked_skills_dir(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        outside = self._outside("outside-skills")
        before = self._outside_names(outside)
        dest = os.path.join(durable.root(self.repo), "skills")
        os.makedirs(durable.root(self.repo), exist_ok=True)
        os.symlink(os.path.realpath(outside), dest)
        with self.assertRaises(durable.DurableError):
            durable.write_skill(self.repo, {
                "key": "deploy", "title": "部署", "steps": ["build"],
                "recorded_at": "2026-08-20T00:00:00Z"})
        self.assertEqual(self._outside_names(outside), before)

    def test_append_events_refuses_symlinked_events_dir(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        outside = self._outside("outside-events")
        before = self._outside_names(outside)
        dest = os.path.join(durable.root(self.repo), "events")
        os.makedirs(durable.root(self.repo), exist_ok=True)
        os.symlink(os.path.realpath(outside), dest)
        with self.assertRaises(durable.DurableError):
            durable.append_events(self.repo, "ses_a", [{
                "event_id": ids.new_id("event"), "title": "x",
                "occurred_at": "2026-08-20T00:00:00Z"}])
        self.assertEqual(self._outside_names(outside), before)

    def test_every_writer_refuses_symlinked_devflow_root(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        data, _created = identity.ensure_project(self.repo, name="fixture")
        outside = self._outside("outside-root")
        before = self._outside_names(outside)
        real = durable.root(self.repo)
        os.rename(real, real + ".bak")
        os.symlink(os.path.realpath(outside), real)
        writers = [
            lambda: durable.write_knowledge(self.repo, self._knowledge("root-k")),
            lambda: durable.write_state(
                self.repo, "database", "memory-store", [sample_fact()]),
            lambda: durable.write_decision(self.repo, DecisionFileTest.RECORD),
            lambda: durable.write_skill(self.repo, {
                "key": "deploy", "title": "部署", "steps": ["build"],
                "recorded_at": "2026-08-20T00:00:00Z"}),
            lambda: durable.append_events(self.repo, "ses_a", [{
                "event_id": ids.new_id("event"), "title": "x",
                "occurred_at": "2026-08-20T00:00:00Z"}]),
            lambda: identity.write_project(self.repo, data),
        ]
        for writer in writers:
            with self.assertRaises(durable.DurableError):
                writer()
        self.assertEqual(self._outside_names(outside), before)

    def test_regular_directories_still_write(self):
        identity.ensure_project(self.repo, name="fixture")
        path = durable.write_knowledge(self.repo, self._knowledge("regular-k"))
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(os.path.realpath(path).startswith(
            os.path.realpath(durable.root(self.repo))))

    def test_ancestor_swapped_to_symlink_between_check_and_write_cannot_escape(self):
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        durable.write_knowledge(self.repo, self._knowledge("first"))
        outside = self._outside("outside-swapped")
        before = self._outside_names(outside)
        domain = os.path.join(durable.root(self.repo), "knowledge", "domain")

        def swap(_repo, _path):
            parked = domain + ".parked"
            if os.path.isdir(domain) and not os.path.islink(domain):
                os.rename(domain, parked)
                os.symlink(os.path.realpath(outside), domain)

        durable._after_write_confine = swap
        try:
            with self.assertRaises(durable.DurableError):
                durable.write_knowledge(self.repo, self._knowledge("second"))
        finally:
            durable._after_write_confine = None
        self.assertEqual(self._outside_names(outside), before)

    def _yaml_under(self, path):
        found = []
        for dirpath, _dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".yaml"):
                    found.append(os.path.relpath(
                        os.path.join(dirpath, name), path).replace(os.sep, "/"))
        return found

    def test_late_ancestor_swap_of_knowledge_cannot_escape(self):
        """最終 realpath 之後把中間祖先換成 symlink:O_NOFOLLOW 只守最後一段。"""
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        durable.write_knowledge(self.repo, self._knowledge("first"))
        outside = self._outside("outside-late-knowledge")
        os.makedirs(os.path.join(outside, "domain"), exist_ok=True)
        before = self._yaml_under(outside)
        knowledge = os.path.join(durable.root(self.repo), "knowledge")

        def swap(_repo, _path):
            if os.path.isdir(knowledge) and not os.path.islink(knowledge):
                os.rename(knowledge, knowledge + ".parked")
                os.symlink(os.path.realpath(outside), knowledge)

        durable._after_write_validate = swap
        try:
            with self.assertRaises(durable.DurableError):
                durable.write_knowledge(self.repo, self._knowledge("late-k"))
        finally:
            durable._after_write_validate = None
        self.assertEqual(self._yaml_under(outside), before)

    def test_late_ancestor_swap_two_levels_above_parent_cannot_escape(self):
        """最終 realpath 之後把 .dev-flow 根換成 symlink(parent 的上兩層)。"""
        if not _can_symlink(self.work):
            self.skipTest("this platform cannot create symlinks")
        identity.ensure_project(self.repo, name="fixture")
        durable.write_knowledge(self.repo, self._knowledge("first"))
        outside = self._outside("outside-late-root")
        os.makedirs(os.path.join(outside, "knowledge", "domain"), exist_ok=True)
        before = self._yaml_under(outside)
        real = durable.root(self.repo)

        def swap(_repo, _path):
            if os.path.isdir(real) and not os.path.islink(real):
                os.rename(real, real + ".parked")
                os.symlink(os.path.realpath(outside), real)

        durable._after_write_validate = swap
        try:
            with self.assertRaises(durable.DurableError):
                durable.write_knowledge(self.repo, self._knowledge("late-root"))
        finally:
            durable._after_write_validate = None
        self.assertEqual(self._yaml_under(outside), before)
