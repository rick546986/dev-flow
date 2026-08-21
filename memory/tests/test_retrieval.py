"""Retrieval v3:多通道 + RRF + 中文 + exact symbol + NO_RELIABLE_MATCH(§21-25)。"""
from memtools import MemoryCase
from agentmem import embedding, retrieval, schema


class RetrievalCase(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.embedder = embedding.Embedder()
        self.seed()
        self.embedder.reindex(self.store)

    def seed(self):
        self.store.add_event(
            "table_rename", "pgs_intake_registration 改名成 lab_order",
            "為了讓 PGS 與 ECS 共用同一張 lab order 表",
            occurred_at="2026-07-01T00:00:00Z", branch="main", signal="high",
            file_paths=["migrations/20260701_rename.sql"])
        self.store.add_event(
            "bug_root_cause", "registration 欄位語意不符造成重複送檢",
            "root cause 是 registration 被當成 specimen-level 使用",
            occurred_at="2026-06-01T00:00:00Z", branch="main", signal="high")
        self.store.upsert_knowledge({
            "kind": "domain", "key": "registration",
            "title": "registration = 一個客戶在 submission 內的送檢紀錄",
            "body": "customer-level,不是 embryo-level",
            "authority": "domain_expert", "status": "CONFIRMED",
            "confidence": 0.95})
        self.store.upsert_fact({
            "entity_type": "database", "entity_key": "lab-order",
            "fact_key": "current_table", "value": "lab_order",
            "status": "VERIFIED", "confidence": 0.99,
            "note": "目前使用的資料表是 lab_order"})
        self.store.upsert_decision({
            "key": "share-lab-order", "title": "PGS/ECS 共用 lab order 表",
            "decision": "合併成 lab_order", "reason": "兩邊欄位重疊九成",
            "alternatives": "各自維護一張表", "status": "ACCEPTED"})
        self.store.upsert_skill({
            "key": "deploy", "title": "部署流程",
            "steps": ["跑 migration", "重啟 worker"], "status": "VERIFIED"})


class ChannelTest(RetrievalCase):
    def test_exact_symbol_channel_hits_table_name(self):
        result = retrieval.search(self.store, "pgs_intake_registration 是什麼",
                                  embedder=self.embedder)
        self.assertEqual(result["status"], retrieval.OK)
        self.assertIn("exact_symbol", result["results"][0]["channels"])

    def test_exact_symbol_does_not_confuse_sibling_tables(self):
        self.store.add_event("table_rename", "pgs_intake_specimen 保留不動",
                             occurred_at="2026-07-02T00:00:00Z", signal="high")
        self.embedder.reindex(self.store)
        result = retrieval.search(self.store, "pgs_intake_registration",
                                  embedder=self.embedder, limit=1)
        self.assertIn("registration", result["results"][0]["title"])

    def test_chinese_query_retrieves(self):
        for query in ("之前為什麼修改 registration?",
                      "目前使用的資料表是哪一張?",
                      "registration 代表什麼?"):
            result = retrieval.search(self.store, query, embedder=self.embedder)
            self.assertEqual(result["status"], retrieval.OK, query)
            self.assertTrue(result["results"], query)

    def test_no_reliable_match_for_unrelated_query(self):
        for query in ("完全不存在的東西 zzzz",
                      "kubernetes ingress 的憑證輪替怎麼設",
                      "咖啡機壞了要找誰修"):
            result = retrieval.search(self.store, query, embedder=self.embedder)
            self.assertEqual(result["status"], retrieval.NO_RELIABLE_MATCH, query)
            self.assertEqual(result["results"], [], query)

    def test_punctuation_only_query_is_no_match(self):
        result = retrieval.search(self.store, "???", embedder=self.embedder)
        self.assertEqual(result["status"], retrieval.NO_RELIABLE_MATCH)

    def test_rrf_fuses_multiple_channels(self):
        result = retrieval.search(self.store, "lab_order 資料表",
                                  embedder=self.embedder)
        channels = set()
        for hit in result["results"]:
            channels.update(hit["channels"])
        self.assertGreaterEqual(len(channels), 2, channels)

    def test_item_type_filter_is_pushed_down(self):
        result = retrieval.search(self.store, "lab order",
                                  item_types=("decision",),
                                  embedder=self.embedder)
        for hit in result["results"]:
            self.assertEqual(hit["item_type"], "decision")

    def test_branch_filter_keeps_branch_agnostic_items(self):
        result = retrieval.search(self.store, "registration",
                                  branch="feature/x", embedder=self.embedder)
        # main 的事件被過掉,但沒有 branch 標記的 knowledge/fact 仍應保留
        types = {hit["item_type"] for hit in result["results"]}
        self.assertIn("knowledge", types)
        self.assertNotIn("event", types)

    def test_time_filter_excludes_later_items(self):
        result = retrieval.search(self.store, "registration",
                                  item_types=("event",),
                                  until="2026-06-15T00:00:00Z",
                                  embedder=self.embedder)
        for hit in result["results"]:
            self.assertLessEqual(hit["occurred_at"], "2026-06-15T00:00:00Z")

    def test_works_without_fts5(self):
        """FTS5 缺席只該少一個通道 —— 中文查詢仍要查得到。"""
        self.store.caps[schema.CAP_FTS5] = False
        self.store.caps[schema.CAP_TRIGRAM] = False
        result = retrieval.search(self.store, "之前為什麼修改 registration?",
                                  embedder=self.embedder)
        self.assertEqual(result["status"], retrieval.OK)
        self.assertNotIn("fts", result["channels_active"])
        self.assertIn("lexical", result["channels_active"])

    def test_works_without_embedder(self):
        result = retrieval.search(self.store, "registration", embedder=None)
        self.assertEqual(result["status"], retrieval.OK)
        self.assertNotIn("vector", result["channels_active"])

    def test_latency_is_reported(self):
        result = retrieval.search(self.store, "registration",
                                  embedder=self.embedder)
        self.assertGreaterEqual(result["latency_ms"], 0.0)


class EmbeddingVersionTest(RetrievalCase):
    def test_signature_recorded_in_meta(self):
        self.assertEqual(self.store.get_meta("embedding_provider"), "hashing")
        self.assertEqual(self.store.get_meta("embedding_model"), "bow-sha256")
        self.assertEqual(self.store.get_meta("embedding_dimension"),
                         str(embedding.DEFAULT_DIM))
        self.assertEqual(self.store.get_meta("embedding_version"), "1")

    def test_model_change_is_detected_not_silently_zero(self):
        class OtherProvider(embedding.HashingProvider):
            name = "hashing"
            model = "bow-sha256"
            version = "2"

        newer = embedding.Embedder(OtherProvider())
        report = newer.mismatch_report(self.store)
        self.assertGreater(report["mismatched"], 0)
        self.assertIn("missing", report)
        self.assertIn("orphaned", report)
        self.assertIn("re-index", report["action"])

    def test_reindex_after_model_change_restores_vector_channel(self):
        class OtherProvider(embedding.HashingProvider):
            version = "2"

        newer = embedding.Embedder(OtherProvider())
        self.assertGreater(newer.reindex(self.store), 0)
        repaired = newer.mismatch_report(self.store)
        self.assertEqual(repaired["mismatched"], 0)
        self.assertEqual(repaired["missing"], 0)
        result = retrieval.search(self.store, "registration", embedder=newer)
        self.assertIn("vector", result["channels_active"])

    def test_dimension_mismatch_rows_are_skipped_not_scored_zero(self):
        uid = self.store.index_item("event", "evt_bad", "bad vector", "x")
        self.store.put_embedding(uid, "hashing", "bow-sha256",
                                 embedding.DEFAULT_DIM, "1", b"\x00" * 8)
        _hits, skipped = self.embedder.search(self.store, "registration")
        self.assertEqual(skipped, 1)

    def test_unpack_length_mismatch_fails_loud(self):
        with self.assertRaises(ValueError):
            embedding.unpack(b"\x00" * 8, 64)

    def test_unregistered_provider_fails_loud(self):
        with self.assertRaises(ValueError):
            embedding.get_provider("nope")

    def test_hashing_embedding_is_deterministic(self):
        provider = embedding.HashingProvider()
        self.assertEqual(provider.embed("registration 送檢紀錄"),
                         provider.embed("registration 送檢紀錄"))
