"""local SQLite:migration 可重跑、filter 下推、legacy 資料不被毀(§29/§33)。"""
import os
import sqlite3

from memtools import MemoryCase
from agentmem import LOCAL_SCHEMA_VERSION, identity, schema, store


class MigrationTest(MemoryCase):
    def test_fresh_db_migrates_and_is_idempotent(self):
        conn = sqlite3.connect(":memory:")
        self.assertEqual(schema.current_version(conn), 0)
        self.assertEqual(schema.migrate(conn),
                         list(range(1, LOCAL_SCHEMA_VERSION + 1)))
        self.assertEqual(schema.current_version(conn), LOCAL_SCHEMA_VERSION)
        self.assertEqual(schema.migrate(conn), [])
        conn.close()

    def test_stepwise_migration_from_older_version(self):
        """v1 → v2 要能單獨走完(不是只有「從零建到最新」那條路)。

        既有安裝的 DB 停在舊版本,升級時走的是這一條;只測 fresh install
        等於從來沒驗過 migration 本身。"""
        conn = sqlite3.connect(":memory:")
        # 真的只建到 v1(不是建完再 DROP —— 那造不出「沒有 ALTER 過的欄位」)
        self.assertEqual(schema.migrate(conn, target=1), [1])
        self.assertEqual(schema.current_version(conn), 1)
        self.assertEqual(schema.migrate(conn), [2])
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("revisions", tables)
        conn.close()

    def test_v2_preserves_v1_rows(self):
        """升級不得毀掉既有資料(§29)。"""
        conn = sqlite3.connect(":memory:")
        schema.migrate(conn, target=1)
        conn.execute(
            "INSERT INTO events(event_id, project_id, kind, title,"
            " occurred_at, recorded_at, signal) VALUES"
            " ('evt_x','prj_x','schema_change','舊事件','2026-01-01','2026-01-01','high')")
        conn.commit()
        schema.migrate(conn)
        self.assertEqual(
            conn.execute("SELECT COUNT(*) FROM events").fetchone()[0], 1)
        conn.close()

    def test_future_schema_fails_loud_instead_of_downgrading(self):
        conn = sqlite3.connect(":memory:")
        schema.migrate(conn)
        conn.execute("UPDATE meta SET value='999' WHERE key='schema_version'")
        conn.commit()
        with self.assertRaises(schema.SchemaError):
            schema.migrate(conn)
        conn.close()

    def test_capabilities_recorded_in_meta(self):
        conn = sqlite3.connect(":memory:")
        caps = schema.detect_capabilities(conn)
        schema.migrate(conn, caps)
        for cap, enabled in caps.items():
            row = conn.execute("SELECT value FROM meta WHERE key=?",
                               ("cap_" + cap,)).fetchone()
            self.assertEqual(row[0], "1" if enabled else "0", cap)
        conn.close()

    def test_missing_fts5_still_migrates(self):
        """FTS5 缺席不得讓 migration 失敗 —— retrieval 少一個通道,不是壞掉。"""
        conn = sqlite3.connect(":memory:")
        schema.migrate(conn, {schema.CAP_FTS5: False, schema.CAP_TRIGRAM: False})
        self.assertEqual(schema.current_version(conn), LOCAL_SCHEMA_VERSION)
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("item_tokens", tables)
        self.assertNotIn("items_fts", tables)
        conn.close()


class StoreTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)

    def test_db_lives_under_project_id_not_path(self):
        expected = os.path.join(self.home, "projects", self.project_id,
                                store.DB_NAME)
        self.assertEqual(store.db_path(self.project_id), expected)
        self.assertTrue(os.path.isfile(expected))

    def test_workspace_registration_holds_local_path(self):
        snapshot = identity.workspace_snapshot(self.repo)
        key = identity.workspace_key(self.project_id, self.repo)
        self.store.register_workspace(key, snapshot)
        rows = self.store.workspaces()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["local_path"], os.path.realpath(self.repo))
        self.assertEqual(rows[0]["project_id"], self.project_id)
        # 重跑不新增一列(idempotent)
        self.store.register_workspace(key, snapshot)
        self.assertEqual(len(self.store.workspaces()), 1)

    def test_events_filters_are_pushed_down(self):
        self.store.add_event("schema_change", "a", occurred_at="2026-08-01T00:00:00Z",
                             branch="main", signal="high")
        self.store.add_event("bug_root_cause", "b", occurred_at="2026-08-05T00:00:00Z",
                             branch="feature/x", signal="high")
        self.assertEqual(len(self.store.events(limit=10)), 2)
        self.assertEqual(len(self.store.events(branch="feature/x")), 1)
        self.assertEqual(len(self.store.events(kind="schema_change")), 1)
        self.assertEqual(len(self.store.events(since="2026-08-03T00:00:00Z")), 1)
        self.assertEqual(len(self.store.events(limit=1)), 1)

    def test_absolute_path_rejected_on_write(self):
        from agentmem import paths
        with self.assertRaises(paths.NonPortablePath):
            self.store.add_event("schema_change", "x",
                                 file_paths=["/Users/rick/x.ts"])
        with self.assertRaises(paths.NonPortablePath):
            self.store.upsert_fact({"entity_type": "db", "entity_key": "k",
                                    "fact_key": "f", "value": "v",
                                    "dependencies": ["C:\\x.ts"]})

    def test_rebuild_keeps_local_only_rows(self):
        """clear_durable_mirror 只刪 durable=1,legacy/local 資料留著(§29)。"""
        durable_id = self.store.add_event("schema_change", "durable",
                                          signal="high", durable=True)
        legacy_id = self.store.add_event("important_discovery", "legacy",
                                         signal="high", legacy=True)
        self.store.clear_durable_mirror()
        remaining = {row["event_id"] for row in self.store.events(limit=10)}
        self.assertNotIn(durable_id, remaining)
        self.assertIn(legacy_id, remaining)

    def test_embedding_version_mismatch_is_countable(self):
        uid = self.store.index_item("event", "evt_x", "t", "body")
        self.store.put_embedding(uid, "hashing", "m1", 64, "1", b"\x00" * 8)
        self.assertEqual(self.store.embedding_mismatch("hashing", "m1", "1", 64), 0)
        self.assertEqual(self.store.embedding_mismatch("hashing", "m2", "1", 64), 1)
        self.assertEqual(
            self.store.drop_mismatched_embeddings("hashing", "m2", "1", 64), 1)

    def test_legacy_path_mapping_recorded(self):
        self.store.map_legacy_path(self.repo, note="pre-v3 observations")
        rows = self.store.legacy_paths()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["project_id"], self.project_id)

    def test_transcripts_are_sequenced_per_session(self):
        session = self.store.start_session("PGS 送檢流程")
        self.assertEqual(self.store.add_turn(session, "user", "第一句"), 1)
        self.assertEqual(self.store.add_turn(session, "agent", "第二句"), 2)
        self.assertEqual([t["seq"] for t in self.store.turns(session)], [1, 2])
