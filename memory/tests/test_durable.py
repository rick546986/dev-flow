"""`.dev-flow/` durable 檔案:deterministic、路徑可攜、conflict fail-loud(§6/§30)。"""
import os

from memtools import MemoryCase, read_file, write
from agentmem import durable, paths


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

    def test_bad_timestamp_fails_loud(self):
        with self.assertRaises(durable.DurableError):
            durable.append_events(self.repo, "ses_a",
                                  [{"title": "x", "occurred_at": "not-a-date"}])

    def test_absolute_path_in_event_rejected(self):
        with self.assertRaises(paths.NonPortablePath):
            durable.append_events(self.repo, "ses_a", [
                {"title": "x", "occurred_at": "2026-08-20T00:00:00Z",
                 "paths": ["/Users/rick/x.ts"]}])

    def test_corrupt_jsonl_fails_loud(self):
        durable.append_events(self.repo, "ses_a", [
            {"title": "x", "occurred_at": "2026-08-20T00:00:00Z"}])
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
            {"title": "x", "occurred_at": "2026-08-20T00:00:00Z"}])
        self.assertEqual(durable.inventory(self.repo),
                         {"facts": 1, "knowledge": 1, "decisions": 1,
                          "skills": 1, "events": 1, "entities": 1})
