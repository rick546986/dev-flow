"""local SQLite schema 與 forward-only migration。

**這個 DB 是可丟棄的**:它住 `~/.agentmem/projects/<project_id>/`,不進 Git。
整包刪掉 → dev-setup → 從 `.dev-flow/` 重建,durable 記憶不損失(§13 的測試案)。
所以這裡的 migration 目標不是「保住資料」,而是:
①**不破壞既有 local 資料**(§29:legacy observation/state 不得被毀)
②**版本可判定**(舊工具遇到新 schema 要吵,不要靜默誤讀)
③**可重跑**(dev-setup idempotent)

migration 規則:forward-only、每步一個版本號、每步在單一 transaction 內完成、
版本記在 `meta.schema_version`。降版不自動處理 —— 遇到「DB 版本 > 工具版本」
直接 fail-loud,因為靜默降級會讓新欄位的資料被舊寫入路徑覆蓋掉。
"""
import sqlite3

from . import LOCAL_SCHEMA_VERSION

# ── 能力偵測:FTS5 / trigram 不是每個 python-sqlite build 都有 ────────────────
# 沒有它們不影響正確性(lexical 主通道是可攜的 inverted index,見 store.py),
# 只影響排序品質與 fuzzy 通道 —— 但**必須被記錄與回報**,不能靜默少一個通道。
CAP_FTS5 = "fts5"
CAP_TRIGRAM = "fts5_trigram"


def detect_capabilities(conn):
    caps = {}
    for cap, ddl in (
        (CAP_FTS5, "CREATE VIRTUAL TABLE temp.__cap_fts USING fts5(x)"),
        (CAP_TRIGRAM,
         "CREATE VIRTUAL TABLE temp.__cap_tri USING fts5(x, tokenize='trigram')"),
    ):
        try:
            conn.execute(ddl)
            caps[cap] = True
        except sqlite3.Error:
            caps[cap] = False
    for name in ("__cap_fts", "__cap_tri"):
        try:
            conn.execute("DROP TABLE IF EXISTS temp." + name)
        except sqlite3.Error:
            pass
    return caps


_V1 = [
    """CREATE TABLE meta (
         key   TEXT PRIMARY KEY,
         value TEXT NOT NULL
       )""",

    # ── local workspace metadata:project_path 住這裡,**不是** identity ──────
    """CREATE TABLE workspaces (
         workspace_id  TEXT PRIMARY KEY,
         project_id    TEXT NOT NULL,
         local_path    TEXT NOT NULL,
         os            TEXT NOT NULL,
         branch        TEXT,
         head_sha      TEXT,
         worktree      TEXT,
         registered_at TEXT NOT NULL,
         last_seen_at  TEXT NOT NULL
       )""",
    "CREATE INDEX workspaces_project ON workspaces(project_id)",

    # ── legacy 遷移對照:舊資料以 project_path 為主鍵時的 mapping(§29)────────
    """CREATE TABLE legacy_project_paths (
         local_path  TEXT PRIMARY KEY,
         project_id  TEXT NOT NULL,
         mapped_at   TEXT NOT NULL,
         note        TEXT
       )""",

    # ── D. HISTORICAL EVENT(append-only episodic ledger)────────────────────
    """CREATE TABLE events (
         event_id    TEXT PRIMARY KEY,
         project_id  TEXT NOT NULL,
         session_id  TEXT,
         kind        TEXT NOT NULL,
         title       TEXT NOT NULL,
         body        TEXT NOT NULL DEFAULT '',
         branch      TEXT,
         commit_sha  TEXT,
         occurred_at TEXT NOT NULL,
         recorded_at TEXT NOT NULL,
         signal      TEXT NOT NULL,
         durable     INTEGER NOT NULL DEFAULT 0,
         durable_ref TEXT,
         paths_json  TEXT NOT NULL DEFAULT '[]',
         source_type TEXT,
         source_ref  TEXT,
         legacy      INTEGER NOT NULL DEFAULT 0
       )""",
    "CREATE INDEX events_time   ON events(project_id, occurred_at DESC)",
    "CREATE INDEX events_branch ON events(project_id, branch, occurred_at DESC)",
    "CREATE INDEX events_kind   ON events(project_id, kind, occurred_at DESC)",

    # ── A. IMPLEMENTATION TRUTH(LVP state facts)────────────────────────────
    """CREATE TABLE facts (
         fact_id             TEXT PRIMARY KEY,
         project_id          TEXT NOT NULL,
         entity_type         TEXT NOT NULL,
         entity_key          TEXT NOT NULL,
         fact_key            TEXT NOT NULL,
         value               TEXT NOT NULL,
         status              TEXT NOT NULL,
         confidence          REAL NOT NULL DEFAULT 0.0,
         effective_at        TEXT,
         recorded_at         TEXT NOT NULL,
         superseded_at       TEXT,
         superseded_by       TEXT,
         source_type         TEXT,
         source_ref          TEXT,
         source_commit       TEXT,
         verified_at         TEXT,
         verified_commit     TEXT,
         verification_count  INTEGER NOT NULL DEFAULT 0,
         contradiction_count INTEGER NOT NULL DEFAULT 0,
         dependencies_json   TEXT NOT NULL DEFAULT '[]',
         fingerprints_json   TEXT NOT NULL DEFAULT '{}',
         durable             INTEGER NOT NULL DEFAULT 0,
         legacy              INTEGER NOT NULL DEFAULT 0
       )""",
    """CREATE INDEX facts_lookup
         ON facts(project_id, entity_type, entity_key, fact_key, status)""",

    # ── LVP local invalidation overlay(per workspace;**絕不進 Git**)────────
    # shared state 說 VERIFIED、本機 workspace 說 STALE,兩者並存才叫 overlay:
    # 直接改 shared state 會把「我這台改了一支檔」變成「所有機器的事實都失效」。
    """CREATE TABLE fact_overlay (
         fact_id            TEXT NOT NULL,
         workspace_id       TEXT NOT NULL,
         status             TEXT NOT NULL,
         reason             TEXT NOT NULL,
         observed_at        TEXT NOT NULL,
         changed_paths_json TEXT NOT NULL DEFAULT '[]',
         PRIMARY KEY (fact_id, workspace_id)
       )""",

    # ── B/C/G. DOMAIN KNOWLEDGE / INTENT / INVARIANT / UNKNOWN ──────────────
    """CREATE TABLE knowledge (
         knowledge_id   TEXT PRIMARY KEY,
         project_id     TEXT NOT NULL,
         kind           TEXT NOT NULL,
         key            TEXT NOT NULL,
         title          TEXT NOT NULL,
         body           TEXT NOT NULL DEFAULT '',
         authority      TEXT NOT NULL,
         status         TEXT NOT NULL,
         confidence     REAL NOT NULL DEFAULT 0.0,
         recorded_at    TEXT NOT NULL,
         superseded_at  TEXT,
         superseded_by  TEXT,
         evidence_json  TEXT NOT NULL DEFAULT '[]',
         conflicts_json TEXT NOT NULL DEFAULT '[]',
         implemented    INTEGER,
         durable        INTEGER NOT NULL DEFAULT 0,
         legacy         INTEGER NOT NULL DEFAULT 0
       )""",
    "CREATE INDEX knowledge_lookup ON knowledge(project_id, kind, key, status)",

    # ── E. DECISION(WHY query 的第一順位)──────────────────────────────────
    """CREATE TABLE decisions (
         decision_id   TEXT PRIMARY KEY,
         project_id    TEXT NOT NULL,
         key           TEXT NOT NULL,
         title         TEXT NOT NULL,
         decision      TEXT NOT NULL,
         alternatives  TEXT NOT NULL DEFAULT '',
         reason        TEXT NOT NULL DEFAULT '',
         tradeoff      TEXT NOT NULL DEFAULT '',
         status        TEXT NOT NULL,
         decided_at    TEXT,
         recorded_at   TEXT NOT NULL,
         supersedes    TEXT,
         evidence_json TEXT NOT NULL DEFAULT '[]',
         durable       INTEGER NOT NULL DEFAULT 0
       )""",
    "CREATE INDEX decisions_lookup ON decisions(project_id, key, status)",

    # ── F. PROCEDURAL SKILL ────────────────────────────────────────────────
    """CREATE TABLE skills (
         skill_id      TEXT PRIMARY KEY,
         project_id    TEXT NOT NULL,
         key           TEXT NOT NULL,
         title         TEXT NOT NULL,
         steps_json    TEXT NOT NULL DEFAULT '[]',
         preconditions TEXT NOT NULL DEFAULT '',
         verification  TEXT NOT NULL DEFAULT '',
         status        TEXT NOT NULL,
         success_count INTEGER NOT NULL DEFAULT 0,
         failure_count INTEGER NOT NULL DEFAULT 0,
         recorded_at   TEXT NOT NULL,
         evidence_json TEXT NOT NULL DEFAULT '[]',
         durable       INTEGER NOT NULL DEFAULT 0
       )""",
    "CREATE INDEX skills_lookup ON skills(project_id, key, status)",

    # ── dev-talk:understanding session / raw transcript / candidate ─────────
    # transcript 與 candidate 都是 **local only**;durable 只收 consolidation 後的結果。
    """CREATE TABLE sessions (
         session_id TEXT PRIMARY KEY,
         project_id TEXT NOT NULL,
         topic      TEXT NOT NULL,
         mode       TEXT NOT NULL,
         branch     TEXT,
         head_sha   TEXT,
         started_at TEXT NOT NULL,
         ended_at   TEXT,
         status     TEXT NOT NULL
       )""",
    """CREATE TABLE transcripts (
         turn_id    INTEGER PRIMARY KEY AUTOINCREMENT,
         project_id TEXT NOT NULL,
         session_id TEXT NOT NULL,
         seq        INTEGER NOT NULL,
         role       TEXT NOT NULL,
         text       TEXT NOT NULL,
         created_at TEXT NOT NULL
       )""",
    "CREATE INDEX transcripts_session ON transcripts(session_id, seq)",
    """CREATE TABLE candidates (
         candidate_id TEXT PRIMARY KEY,
         project_id   TEXT NOT NULL,
         session_id   TEXT NOT NULL,
         target_kind  TEXT NOT NULL,
         payload_json TEXT NOT NULL,
         authority    TEXT NOT NULL,
         status       TEXT NOT NULL,
         created_at   TEXT NOT NULL,
         resolved_at  TEXT,
         sensitive    INTEGER NOT NULL DEFAULT 0,
         note         TEXT NOT NULL DEFAULT ''
       )""",
    "CREATE INDEX candidates_session ON candidates(session_id, status)",

    # ── retrieval index ────────────────────────────────────────────────────
    """CREATE TABLE items (
         item_uid    TEXT PRIMARY KEY,
         project_id  TEXT NOT NULL,
         item_type   TEXT NOT NULL,
         item_id     TEXT NOT NULL,
         title       TEXT NOT NULL,
         text        TEXT NOT NULL,
         branch      TEXT,
         occurred_at TEXT,
         status      TEXT,
         authority   TEXT,
         paths_json  TEXT NOT NULL DEFAULT '[]',
         indexed_at  TEXT NOT NULL
       )""",
    "CREATE INDEX items_type ON items(project_id, item_type)",
    "CREATE INDEX items_time ON items(project_id, occurred_at DESC)",
    # 可攜 lexical 主通道:token → item 的 inverted index。
    # 不依賴 FTS5 是刻意的 —— FTS5 缺席時 retrieval 必須仍然正確,
    # 而且自算分數讓測試在不同 SQLite 版本上結果一致。
    """CREATE TABLE item_tokens (
         item_uid TEXT NOT NULL,
         token    TEXT NOT NULL,
         tf       INTEGER NOT NULL DEFAULT 1,
         PRIMARY KEY (item_uid, token)
       )""",
    "CREATE INDEX item_tokens_token ON item_tokens(token)",
    """CREATE TABLE item_symbols (
         item_uid TEXT NOT NULL,
         symbol   TEXT NOT NULL,
         norm     TEXT NOT NULL,
         PRIMARY KEY (item_uid, symbol)
       )""",
    "CREATE INDEX item_symbols_norm ON item_symbols(norm)",
    # embedding 一律帶版本三件套 + vector;換 model 時偵測 mismatch 再 re-index。
    """CREATE TABLE embeddings (
         item_uid   TEXT PRIMARY KEY,
         provider   TEXT NOT NULL,
         model      TEXT NOT NULL,
         dim        INTEGER NOT NULL,
         version    TEXT NOT NULL,
         vector     BLOB NOT NULL,
         indexed_at TEXT NOT NULL
       )""",
    "CREATE INDEX embeddings_model ON embeddings(provider, model, version)",
    # retrieval metrics(eval harness 與 §33 效能觀測用;local only)
    """CREATE TABLE retrieval_metrics (
         metric_id  INTEGER PRIMARY KEY AUTOINCREMENT,
         project_id TEXT NOT NULL,
         query_kind TEXT NOT NULL,
         status     TEXT NOT NULL,
         latency_ms REAL NOT NULL,
         hits       INTEGER NOT NULL,
         recorded_at TEXT NOT NULL
       )""",
]

# FTS5 / trigram 是**條件式**建立:能力不足時不建,retrieval 自動少一個通道。
_V1_FTS = [
    """CREATE VIRTUAL TABLE items_fts
         USING fts5(item_uid UNINDEXED, tokens, tokenize='unicode61')""",
]
_V1_TRIGRAM = [
    """CREATE VIRTUAL TABLE items_tri
         USING fts5(item_uid UNINDEXED, raw, tokenize='trigram')""",
]

# ── v2:修正歷史(P0-3)────────────────────────────────────────────────────
# current materialized view 只留得下「現在是什麼」;「以前理解成什麼、什麼時候
# 改、為什麼改」需要一條 append-only 的軌。revision 先落這張表(durable=0),
# 由 consolidation 一併刷進 `.dev-flow/events/` —— consolidate 仍是唯一
# durable writer。
_V2 = [
    """CREATE TABLE revisions (
         revision_id  TEXT PRIMARY KEY,
         project_id   TEXT NOT NULL,
         session_id   TEXT,
         kind         TEXT NOT NULL,
         memory_kind  TEXT,
         key          TEXT NOT NULL,
         payload_json TEXT NOT NULL,
         occurred_at  TEXT NOT NULL,
         durable      INTEGER NOT NULL DEFAULT 0,
         durable_ref  TEXT
       )""",
    "CREATE INDEX revisions_pending ON revisions(project_id, durable, occurred_at)",
    "CREATE INDEX revisions_key ON revisions(project_id, kind, key)",
    # session 從「dev-talk 專用」擴成通用(P0-1):implementation 模式要記
    # 這次 session 對應哪個 feature,回報與稽核才對得起來。
    "ALTER TABLE sessions ADD COLUMN feature_slug TEXT",
]

MIGRATIONS = {
    1: (_V1, {CAP_FTS5: _V1_FTS, CAP_TRIGRAM: _V1_TRIGRAM}),
    2: (_V2, {}),
}


class SchemaError(RuntimeError):
    """schema 版本不相容 —— fail-loud,不靜默降級(降級會讓新欄位資料被舊路徑覆蓋)。"""


def current_version(conn):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='meta'"
    ).fetchone()
    if row is None:
        return 0
    row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    return int(row[0]) if row else 0


def migrate(conn, caps=None, target=None):
    """把 DB 推到 `target`(預設 LOCAL_SCHEMA_VERSION)。

    回傳實際套用的版本清單(重跑 → 空清單)。`target` 讓測試能真的造出一個
    「停在舊版本」的 DB —— 用 DROP TABLE 模擬回舊版是造不出 ALTER 過的欄位的,
    那樣測到的是治具而不是 migration。
    """
    caps = caps if caps is not None else detect_capabilities(conn)
    target = LOCAL_SCHEMA_VERSION if target is None else target
    version = current_version(conn)
    if version > LOCAL_SCHEMA_VERSION:
        raise SchemaError(
            "local DB schema v{0} 比本工具支援的 v{1} 新 —— 請升級 dev-flow,"
            "不要用舊版寫入(舊寫入路徑會覆蓋掉新欄位的資料)".format(
                version, LOCAL_SCHEMA_VERSION))
    applied = []
    for step in range(version + 1, target + 1):
        base, conditional = MIGRATIONS[step]
        with conn:
            for ddl in base:
                conn.execute(ddl)
            for cap, statements in conditional.items():
                if caps.get(cap):
                    for ddl in statements:
                        conn.execute(ddl)
            conn.execute(
                "INSERT INTO meta(key, value) VALUES('schema_version', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(step),))
            for cap, enabled in caps.items():
                conn.execute(
                    "INSERT INTO meta(key, value) VALUES(?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    ("cap_" + cap, "1" if enabled else "0"))
        applied.append(step)
    return applied
