"""local runtime store(SQLite;不進 Git)。

位置:`~/.agentmem/projects/<project_id>/worktrees/<worktree_key>/memory.db`
覆寫:`AGENTMEM_HOME`(整個 home 根)。**project_id 仍是 durable identity**,
但 runtime DB 是 **per-worktree**:同一個 project 在同一台機器上的兩個
clone / linked worktree 各有自己的 SQLite,互不共用 `-wal` / `-shm` /
OPEN session / candidate / overlay。記憶內容的共用走 `.dev-flow/` + git
(owner 裁決 D-1)。branch 切換不是新 worktree —— worktree_key 綁的是
本機路徑,不是分支名。

這個 DB 可以整包刪掉:dev-setup 會從**當前 checkout** 的 `.dev-flow/` 重建
(§13)。所以任何**只**存在這裡而不在 `.dev-flow/` 的東西,定義上就是
「可丟棄的」——raw transcript、embedding、候選知識、本機失效 overlay、
retrieval metrics 都屬於這一類,這是刻意的。

舊佈局 `~/.agentmem/projects/<project_id>/memory.db`(專案級共用檔)不再
被打開。第一次碰到時 archive 成 `memory.db.legacy-shared`,不把舊的
OPEN session / candidate 扇出到各個新 worktree DB。

§33 效能紀律:所有查詢的 project_id / branch / 時間 / limit 都下推到 SQL,
不做「先撈全表再用 Python filter」。
"""
import datetime
import json
import os
import sqlite3

from . import ids, paths, schema, textnorm

HOME_ENV = "AGENTMEM_HOME"
DEFAULT_HOME = os.path.join("~", ".agentmem")
DB_NAME = "memory.db"
WORKTREE_DIR = "worktrees"
LEGACY_SHARED_SUFFIX = ".legacy-shared"


def home_root():
    return os.path.expanduser(os.environ.get(HOME_ENV) or DEFAULT_HOME)


def project_home(project_id):
    if not ids.is_valid_id("project", project_id):
        raise ValueError("project_id 不合法:{0!r}".format(project_id))
    return os.path.join(home_root(), "projects", project_id)


def _require_worktree_key(worktree_key):
    if not isinstance(worktree_key, str) or not worktree_key:
        raise ValueError(
            "worktree_key 必填 —— runtime DB 是 per-worktree,"
            "只給 project_id 會讓兩個 worktree 共用同一份可變 SQLite")
    if "/" in worktree_key or "\\" in worktree_key or worktree_key in (".", ".."):
        raise ValueError("worktree_key 不合法:{0!r}".format(worktree_key))
    return worktree_key


def db_path(project_id, worktree_key):
    return os.path.join(project_home(project_id), WORKTREE_DIR,
                        _require_worktree_key(worktree_key), DB_NAME)


def legacy_shared_db_path(project_id):
    """v3 早期的專案級共用 DB。不再作為 runtime 入口。"""
    return os.path.join(project_home(project_id), DB_NAME)


def archive_legacy_shared_db(project_id):
    """把舊的專案級 `memory.db` 改名封存,不複製進任何 worktree DB。

    回傳封存後的路徑;沒有舊檔回 None。`-wal` / `-shm` 一併改名,
    避免 SQLite 下一次誤把殘留 WAL 當現行檔。
    """
    src = legacy_shared_db_path(project_id)
    if not os.path.isfile(src):
        return None
    dest = src + LEGACY_SHARED_SUFFIX
    suffix = 2
    while os.path.exists(dest):
        dest = "{0}{1}.{2}".format(src, LEGACY_SHARED_SUFFIX, suffix)
        suffix += 1
    os.rename(src, dest)
    for extra in ("-wal", "-shm"):
        leftover = src + extra
        if os.path.isfile(leftover):
            os.rename(leftover, dest + extra)
    return dest


def open_for_root(project_id, repo_root, path=None):
    """依當前 worktree 的本機路徑打開 runtime DB。生產路徑應走這支。"""
    from . import identity
    key = identity.workspace_key(project_id, repo_root)
    return Store.open(project_id, path=path, worktree_key=key)


def runtime_db_path(project_id, repo_root):
    from . import identity
    return db_path(project_id, identity.workspace_key(project_id, repo_root))


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def _uid(item_type, item_id):
    return item_type + ":" + item_id


class Store:
    """local runtime store。open() 會自動 migrate 到最新 schema(idempotent)。"""

    def __init__(self, project_id, connection):
        self.project_id = project_id
        self.conn = connection
        self.caps = {
            k[4:]: v == "1"
            for k, v in self.conn.execute(
                "SELECT key, value FROM meta WHERE key LIKE 'cap_%'")
        }

    # ── lifecycle ────────────────────────────────────────────────────────────
    @classmethod
    def open(cls, project_id, path=None, worktree_key=None):
        if path is None:
            if worktree_key is None:
                raise ValueError(
                    "Store.open 必須給 worktree_key 或 path——"
                    "只給 project_id 會讓兩個 worktree 共用同一份可變 SQLite")
            target = db_path(project_id, worktree_key)
        else:
            target = path
        if target != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
        conn = sqlite3.connect(target)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        caps = schema.detect_capabilities(conn)
        schema.migrate(conn, caps)
        with conn:
            conn.execute(
                "INSERT INTO meta(key, value) VALUES('project_id', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (project_id,))
        return cls(project_id, conn)

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # ── meta ────────────────────────────────────────────────────────────────
    def set_meta(self, key, value):
        with self.conn:
            self.conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value)))

    def get_meta(self, key, default=None):
        row = self.conn.execute(
            "SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def has_durable_mirror(self):
        """是否已有從 `.dev-flow/` 鏡射進來的列。缺世代時用來決定能否只蓋章。"""
        for table in ("events", "facts", "knowledge", "decisions", "skills"):
            row = self.conn.execute(
                "SELECT 1 FROM " + table + " WHERE durable=1 LIMIT 1"
            ).fetchone()
            if row:
                return True
        return False

    # ── workspace(local metadata;project_path 住這裡)──────────────────────
    def register_workspace(self, workspace_id, snapshot, now=None):
        now = now or utc_now()
        with self.conn:
            self.conn.execute(
                "INSERT INTO workspaces(workspace_id, project_id, local_path, os,"
                " branch, head_sha, worktree, registered_at, last_seen_at)"
                " VALUES(?,?,?,?,?,?,?,?,?)"
                " ON CONFLICT(workspace_id) DO UPDATE SET"
                "   local_path=excluded.local_path, os=excluded.os,"
                "   branch=excluded.branch, head_sha=excluded.head_sha,"
                "   worktree=excluded.worktree, last_seen_at=excluded.last_seen_at",
                (workspace_id, self.project_id, snapshot["local_path"],
                 snapshot["os"], snapshot.get("branch"), snapshot.get("head_sha"),
                 snapshot.get("worktree"), now, now))
        return workspace_id

    def workspaces(self):
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM workspaces WHERE project_id=? ORDER BY registered_at",
            (self.project_id,))]

    def map_legacy_path(self, local_path, note="", now=None):
        """legacy 資料的 project_path → project_id 對照(§29;不毀既有資料)。"""
        with self.conn:
            self.conn.execute(
                "INSERT INTO legacy_project_paths(local_path, project_id, mapped_at, note)"
                " VALUES(?,?,?,?) ON CONFLICT(local_path) DO UPDATE SET"
                "   project_id=excluded.project_id, mapped_at=excluded.mapped_at,"
                "   note=excluded.note",
                (paths.to_posix(os.path.realpath(local_path)), self.project_id,
                 now or utc_now(), note))

    def legacy_paths(self):
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM legacy_project_paths WHERE project_id=? ORDER BY local_path",
            (self.project_id,))]

    # ── events(D. historical event;append-only)────────────────────────────
    def add_event(self, kind, title, body="", occurred_at=None, branch=None,
                  commit_sha=None, session_id=None, signal="low",
                  file_paths=(), source_type=None, source_ref=None,
                  durable=False, durable_ref=None, legacy=False, event_id=None):
        now = utc_now()
        rel = [paths.assert_portable(p) for p in file_paths]
        event_id = event_id or ids.new_id("event")
        with self.conn:
            # ON CONFLICT:同一個 event_id 再寫一次 = 把本機事件**升級成 durable**
            # (observe 先落本機、consolidate 再固化)。沒有這一條會撞主鍵,
            # 或被迫產第二筆 —— 那正是同一件事出現兩次的來源。
            self.conn.execute(
                "INSERT INTO events(event_id, project_id, session_id, kind, title,"
                " body, branch, commit_sha, occurred_at, recorded_at, signal,"
                " durable, durable_ref, paths_json, source_type, source_ref, legacy)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                " ON CONFLICT(event_id) DO UPDATE SET"
                "   kind=excluded.kind, title=excluded.title, body=excluded.body,"
                "   branch=excluded.branch, commit_sha=excluded.commit_sha,"
                "   signal=excluded.signal, durable=excluded.durable,"
                "   durable_ref=excluded.durable_ref,"
                "   paths_json=excluded.paths_json,"
                "   source_type=excluded.source_type,"
                "   source_ref=excluded.source_ref",
                (event_id, self.project_id, session_id, kind, title, body, branch,
                 commit_sha, occurred_at or now, now, signal,
                 1 if durable else 0, durable_ref, json.dumps(rel, ensure_ascii=False),
                 source_type, source_ref, 1 if legacy else 0))
        # kind 一併進索引:它是這筆事件**是什麼**的一部分,不是內部欄位。
        # `knowledge_corrected` 會被切成 knowledge / corrected,
        # 於是「這個詞之前被 corrected 過嗎」與「有哪些 schema change」這類
        # 以種類發問的查詢才對得上 —— 這是真的有詞面重疊,不是同義詞表。
        self.index_item("event", event_id, title,
                        "\n".join([kind, title, body]),
                        branch=branch, occurred_at=occurred_at or now,
                        status=signal, file_paths=rel)
        return event_id

    def events(self, limit=20, branch=None, kind=None, since=None, until=None,
               durable_only=False):
        """時間序事件查詢。所有 filter 都下推 SQL(§33)。"""
        sql = ["SELECT * FROM events WHERE project_id=?"]
        args = [self.project_id]
        if branch:
            sql.append("AND (branch=? OR branch IS NULL)")
            args.append(branch)
        if kind:
            sql.append("AND kind=?")
            args.append(kind)
        if since:
            sql.append("AND occurred_at >= ?")
            args.append(since)
        if until:
            sql.append("AND occurred_at <= ?")
            args.append(until)
        if durable_only:
            sql.append("AND durable=1")
        sql.append("ORDER BY occurred_at DESC, event_id DESC LIMIT ?")
        args.append(int(limit))
        return [dict(r) for r in self.conn.execute(" ".join(sql), args)]

    # ── facts(A. implementation truth)─────────────────────────────────────
    def upsert_fact(self, record):
        """寫入一筆 fact。呼叫端負責 status/supersede 的語意(見 truth.py)。"""
        record = dict(record)
        record.setdefault("fact_id", ids.new_id("fact"))
        record.setdefault("recorded_at", utc_now())
        record.setdefault("status", "CANDIDATE")
        record.setdefault("confidence", 0.0)
        deps = [paths.assert_portable(p) for p in record.get("dependencies", [])]
        fingerprints = record.get("fingerprints", {}) or {}
        for dep in fingerprints:
            paths.assert_portable(dep)
        columns = dict(
            fact_id=record["fact_id"], project_id=self.project_id,
            entity_type=record["entity_type"], entity_key=record["entity_key"],
            fact_key=record["fact_key"], value=str(record["value"]),
            status=record["status"], confidence=float(record["confidence"]),
            effective_at=record.get("effective_at"),
            recorded_at=record["recorded_at"],
            superseded_at=record.get("superseded_at"),
            superseded_by=record.get("superseded_by"),
            source_type=record.get("source_type"),
            source_ref=record.get("source_ref"),
            source_commit=record.get("source_commit"),
            verified_at=record.get("verified_at"),
            verified_commit=record.get("verified_commit"),
            verification_count=int(record.get("verification_count", 0)),
            contradiction_count=int(record.get("contradiction_count", 0)),
            dependencies_json=json.dumps(deps, ensure_ascii=False),
            fingerprints_json=json.dumps(fingerprints, ensure_ascii=False,
                                         sort_keys=True),
            durable=1 if record.get("durable") else 0,
            legacy=1 if record.get("legacy") else 0)
        names = sorted(columns)
        with self.conn:
            self.conn.execute(
                "INSERT INTO facts({0}) VALUES({1})"
                " ON CONFLICT(fact_id) DO UPDATE SET {2}".format(
                    ", ".join(names), ", ".join("?" for _ in names),
                    ", ".join("{0}=excluded.{0}".format(n) for n in names
                              if n != "fact_id")),
                [columns[n] for n in names])
        self.index_item(
            "fact", columns["fact_id"],
            "{entity_type}.{entity_key}.{fact_key}".format(**columns),
            " ".join([columns["entity_type"], columns["entity_key"],
                      columns["fact_key"], columns["value"],
                      record.get("note", "") or ""]),
            status=columns["status"], file_paths=deps,
            occurred_at=columns["recorded_at"])
        return columns["fact_id"]

    def fact_row(self, fact_id):
        row = self.conn.execute(
            "SELECT * FROM facts WHERE fact_id=?", (fact_id,)).fetchone()
        return dict(row) if row else None

    def facts(self, entity_type=None, entity_key=None, fact_key=None,
              statuses=None, limit=200):
        sql = ["SELECT * FROM facts WHERE project_id=?"]
        args = [self.project_id]
        for column, value in (("entity_type", entity_type),
                              ("entity_key", entity_key),
                              ("fact_key", fact_key)):
            if value:
                sql.append("AND {0}=?".format(column))
                args.append(value)
        if statuses:
            sql.append("AND status IN ({0})".format(
                ",".join("?" for _ in statuses)))
            args.extend(statuses)
        sql.append("ORDER BY recorded_at DESC, fact_id DESC")
        # limit=None = 不設視窗。整檔取代的 durable writer 需要它:撈前 N 筆
        # 再整檔寫回等於把視窗外的 fact 從檔案裡刪掉,而任何預設值都會在
        # 「記憶夠多」的那天變成靜默資料遺失。要窗口的呼叫端自己傳。
        if limit is not None:
            sql.append("LIMIT ?")
            args.append(int(limit))
        return [dict(r) for r in self.conn.execute(" ".join(sql), args)]

    def entities_pending_durable(self, statuses):
        """還沒落進 `.dev-flow/` 的 fact 屬於哪些 entity(去重、無筆數上限)。

        `durable=1` 的語意是「這一列現在的內容就是 `.dev-flow/` 裡的那份」——
        所以 `durable=0` 的 live fact 就是一個**還沒完成的耐久操作**。

        刻意下推成 SQL 的 DISTINCT 而不是撈前 N 筆再用 Python 過濾:任意
        前綴會讓「第 N+1 筆的 entity 沒被重寫」變成一個只在記憶量大時出現、
        而且靜默的失憶。
        """
        if not statuses:
            return []
        rows = self.conn.execute(
            "SELECT DISTINCT entity_type, entity_key FROM facts"
            " WHERE project_id=? AND durable=0 AND status IN ({0})"
            " ORDER BY entity_type, entity_key".format(
                ",".join("?" for _ in statuses)),
            [self.project_id] + list(statuses))
        return [(r["entity_type"], r["entity_key"]) for r in rows]

    # ── LVP overlay(per workspace;local only)──────────────────────────────
    def set_overlay(self, fact_id, workspace_id, status, reason,
                    changed_paths=(), now=None):
        with self.conn:
            self.conn.execute(
                "INSERT INTO fact_overlay(fact_id, workspace_id, status, reason,"
                " observed_at, changed_paths_json) VALUES(?,?,?,?,?,?)"
                " ON CONFLICT(fact_id, workspace_id) DO UPDATE SET"
                "   status=excluded.status, reason=excluded.reason,"
                "   observed_at=excluded.observed_at,"
                "   changed_paths_json=excluded.changed_paths_json",
                (fact_id, workspace_id, status, reason, now or utc_now(),
                 json.dumps(list(changed_paths), ensure_ascii=False)))

    def clear_overlay(self, fact_id, workspace_id):
        with self.conn:
            self.conn.execute(
                "DELETE FROM fact_overlay WHERE fact_id=? AND workspace_id=?",
                (fact_id, workspace_id))

    def overlay(self, fact_id, workspace_id):
        row = self.conn.execute(
            "SELECT * FROM fact_overlay WHERE fact_id=? AND workspace_id=?",
            (fact_id, workspace_id)).fetchone()
        return dict(row) if row else None

    def overlays(self, workspace_id):
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM fact_overlay WHERE workspace_id=? ORDER BY fact_id",
            (workspace_id,))]

    # ── knowledge(B/C/G)───────────────────────────────────────────────────
    def upsert_knowledge(self, record):
        record = dict(record)
        record.setdefault("knowledge_id", ids.new_id("knowledge"))
        record.setdefault("recorded_at", utc_now())
        columns = dict(
            knowledge_id=record["knowledge_id"], project_id=self.project_id,
            kind=record["kind"], key=record["key"], title=record["title"],
            body=record.get("body", ""), authority=record["authority"],
            status=record.get("status", "CANDIDATE"),
            confidence=float(record.get("confidence", 0.0)),
            recorded_at=record["recorded_at"],
            superseded_at=record.get("superseded_at"),
            superseded_by=record.get("superseded_by"),
            evidence_json=json.dumps(record.get("evidence", []),
                                     ensure_ascii=False, sort_keys=True),
            conflicts_json=json.dumps(record.get("conflicts", []),
                                      ensure_ascii=False, sort_keys=True),
            implemented=(None if record.get("implemented") is None
                         else (1 if record["implemented"] else 0)),
            durable=1 if record.get("durable") else 0,
            legacy=1 if record.get("legacy") else 0)
        names = sorted(columns)
        with self.conn:
            self.conn.execute(
                "INSERT INTO knowledge({0}) VALUES({1})"
                " ON CONFLICT(knowledge_id) DO UPDATE SET {2}".format(
                    ", ".join(names), ", ".join("?" for _ in names),
                    ", ".join("{0}=excluded.{0}".format(n) for n in names
                              if n != "knowledge_id")),
                [columns[n] for n in names])
        self.index_item(
            "knowledge", columns["knowledge_id"], columns["title"],
            " ".join([columns["kind"], columns["key"], columns["title"],
                      columns["body"]]),
            status=columns["status"], authority=columns["authority"],
            occurred_at=columns["recorded_at"])
        return columns["knowledge_id"]

    def knowledge(self, kind=None, key=None, statuses=None, limit=200):
        sql = ["SELECT * FROM knowledge WHERE project_id=?"]
        args = [self.project_id]
        if kind:
            sql.append("AND kind=?")
            args.append(kind)
        if key:
            sql.append("AND key=?")
            args.append(key)
        if statuses:
            sql.append("AND status IN ({0})".format(
                ",".join("?" for _ in statuses)))
            args.extend(statuses)
        sql.append("ORDER BY recorded_at DESC, knowledge_id DESC LIMIT ?")
        args.append(int(limit))
        return [dict(r) for r in self.conn.execute(" ".join(sql), args)]

    def knowledge_row(self, knowledge_id):
        row = self.conn.execute(
            "SELECT * FROM knowledge WHERE knowledge_id=?",
            (knowledge_id,)).fetchone()
        return dict(row) if row else None

    # ── decisions(E)───────────────────────────────────────────────────────
    def upsert_decision(self, record):
        record = dict(record)
        record.setdefault("decision_id", ids.new_id("decision"))
        record.setdefault("recorded_at", utc_now())
        columns = dict(
            decision_id=record["decision_id"], project_id=self.project_id,
            key=record["key"], title=record["title"],
            decision=record["decision"],
            alternatives=record.get("alternatives", ""),
            reason=record.get("reason", ""), tradeoff=record.get("tradeoff", ""),
            status=record.get("status", "ACCEPTED"),
            decided_at=record.get("decided_at"),
            recorded_at=record["recorded_at"], supersedes=record.get("supersedes"),
            evidence_json=json.dumps(record.get("evidence", []),
                                     ensure_ascii=False, sort_keys=True),
            durable=1 if record.get("durable") else 0)
        names = sorted(columns)
        with self.conn:
            self.conn.execute(
                "INSERT INTO decisions({0}) VALUES({1})"
                " ON CONFLICT(decision_id) DO UPDATE SET {2}".format(
                    ", ".join(names), ", ".join("?" for _ in names),
                    ", ".join("{0}=excluded.{0}".format(n) for n in names
                              if n != "decision_id")),
                [columns[n] for n in names])
        self.index_item(
            "decision", columns["decision_id"], columns["title"],
            " ".join([columns["key"], columns["title"], columns["decision"],
                      columns["reason"], columns["alternatives"],
                      columns["tradeoff"]]),
            status=columns["status"], occurred_at=columns["recorded_at"])
        return columns["decision_id"]

    def decisions(self, key=None, statuses=None, limit=100):
        sql = ["SELECT * FROM decisions WHERE project_id=?"]
        args = [self.project_id]
        if key:
            sql.append("AND key=?")
            args.append(key)
        if statuses:
            sql.append("AND status IN ({0})".format(
                ",".join("?" for _ in statuses)))
            args.extend(statuses)
        sql.append("ORDER BY recorded_at DESC LIMIT ?")
        args.append(int(limit))
        return [dict(r) for r in self.conn.execute(" ".join(sql), args)]

    def decision_row(self, decision_id):
        """主鍵查詢。檢索命中已知 id 之後要撈內容,一律走這支。

        用 `decisions(limit=N)` 掃已知主鍵是錯的:檢索索引沒有那個視窗,
        於是命中一筆較舊的 decision 時撈不到內容,而呼叫端仍然回 OK ——
        系統聲稱有答案卻沒附上構成答案的欄位。
        """
        row = self.conn.execute(
            "SELECT * FROM decisions WHERE decision_id=?",
            (decision_id,)).fetchone()
        return dict(row) if row else None

    # ── skills(F)──────────────────────────────────────────────────────────
    def upsert_skill(self, record):
        record = dict(record)
        record.setdefault("skill_id", ids.new_id("skill"))
        record.setdefault("recorded_at", utc_now())
        columns = dict(
            skill_id=record["skill_id"], project_id=self.project_id,
            key=record["key"], title=record["title"],
            steps_json=json.dumps(record.get("steps", []), ensure_ascii=False),
            preconditions=record.get("preconditions", ""),
            verification=record.get("verification", ""),
            status=record.get("status", "CANDIDATE"),
            success_count=int(record.get("success_count", 0)),
            failure_count=int(record.get("failure_count", 0)),
            recorded_at=record["recorded_at"],
            evidence_json=json.dumps(record.get("evidence", []),
                                     ensure_ascii=False, sort_keys=True),
            durable=1 if record.get("durable") else 0)
        names = sorted(columns)
        with self.conn:
            self.conn.execute(
                "INSERT INTO skills({0}) VALUES({1})"
                " ON CONFLICT(skill_id) DO UPDATE SET {2}".format(
                    ", ".join(names), ", ".join("?" for _ in names),
                    ", ".join("{0}=excluded.{0}".format(n) for n in names
                              if n != "skill_id")),
                [columns[n] for n in names])
        self.index_item(
            "skill", columns["skill_id"], columns["title"],
            " ".join([columns["key"], columns["title"],
                      " ".join(record.get("steps", [])),
                      columns["preconditions"], columns["verification"]]),
            status=columns["status"], occurred_at=columns["recorded_at"])
        return columns["skill_id"]

    def skills(self, key=None, statuses=None, limit=100):
        sql = ["SELECT * FROM skills WHERE project_id=?"]
        args = [self.project_id]
        if key:
            sql.append("AND key=?")
            args.append(key)
        if statuses:
            sql.append("AND status IN ({0})".format(
                ",".join("?" for _ in statuses)))
            args.extend(statuses)
        sql.append("ORDER BY recorded_at DESC LIMIT ?")
        args.append(int(limit))
        return [dict(r) for r in self.conn.execute(" ".join(sql), args)]

    def skill_row(self, skill_id):
        """主鍵查詢(理由同 decision_row)。"""
        row = self.conn.execute(
            "SELECT * FROM skills WHERE skill_id=?", (skill_id,)).fetchone()
        return dict(row) if row else None

    # ── dev-talk session / transcript / candidate(全部 local only)─────────
    def start_session(self, topic, mode="understanding", branch=None,
                      head_sha=None, session_id=None, now=None,
                      feature_slug=None):
        session_id = session_id or ids.new_id("session")
        with self.conn:
            self.conn.execute(
                "INSERT INTO sessions(session_id, project_id, topic, mode, branch,"
                " head_sha, started_at, status, feature_slug)"
                " VALUES(?,?,?,?,?,?,?,'OPEN',?)",
                (session_id, self.project_id, topic, mode, branch, head_sha,
                 now or utc_now(), feature_slug))
        return session_id

    def end_session(self, session_id, status="CLOSED", now=None):
        """OPEN → status 的 compare-and-set。回傳有沒有真的換到手。

        `WHERE status='OPEN'` 是這支的重點:少了它,abort 之後的 end 會把
        ABORTED 覆寫成 CLOSED,而不存在的 session 會靜默 no-op ——
        兩種都讓「這一輪算不算完成」變成一個沒有憑據的答案。
        """
        with self.conn:
            cursor = self.conn.execute(
                "UPDATE sessions SET ended_at=?, status=?"
                " WHERE session_id=? AND status='OPEN'",
                (now or utc_now(), status, session_id))
        return cursor.rowcount == 1

    def session(self, session_id):
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None

    def sessions(self, status=None, limit=20):
        sql = ["SELECT * FROM sessions WHERE project_id=?"]
        args = [self.project_id]
        if status:
            sql.append("AND status=?")
            args.append(status)
        sql.append("ORDER BY started_at DESC LIMIT ?")
        args.append(int(limit))
        return [dict(r) for r in self.conn.execute(" ".join(sql), args)]

    def add_turn(self, session_id, role, text, now=None):
        """原始對話輪次 —— **只**住 local。durable memory 永遠不收 transcript。"""
        row = self.conn.execute(
            "SELECT COALESCE(MAX(seq), 0) FROM transcripts WHERE session_id=?",
            (session_id,)).fetchone()
        seq = int(row[0]) + 1
        with self.conn:
            self.conn.execute(
                "INSERT INTO transcripts(project_id, session_id, seq, role, text,"
                " created_at) VALUES(?,?,?,?,?,?)",
                (self.project_id, session_id, seq, role, text, now or utc_now()))
        return seq

    def turns(self, session_id, limit=1000):
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM transcripts WHERE session_id=? ORDER BY seq LIMIT ?",
            (session_id, int(limit)))]

    def add_candidate(self, session_id, target_kind, payload, authority,
                      sensitive=False, note="", now=None):
        candidate_id = ids.new_id("candidate")
        with self.conn:
            self.conn.execute(
                "INSERT INTO candidates(candidate_id, project_id, session_id,"
                " target_kind, payload_json, authority, status, created_at,"
                " sensitive, note) VALUES(?,?,?,?,?,?,'PENDING',?,?,?)",
                (candidate_id, self.project_id, session_id, target_kind,
                 json.dumps(payload, ensure_ascii=False, sort_keys=True),
                 authority, now or utc_now(), 1 if sensitive else 0, note))
        return candidate_id

    def set_candidate_status(self, candidate_id, status, note=None, now=None):
        with self.conn:
            if note is None:
                self.conn.execute(
                    "UPDATE candidates SET status=?, resolved_at=?"
                    " WHERE candidate_id=?",
                    (status, now or utc_now(), candidate_id))
            else:
                self.conn.execute(
                    "UPDATE candidates SET status=?, resolved_at=?, note=?"
                    " WHERE candidate_id=?",
                    (status, now or utc_now(), note, candidate_id))

    def candidates(self, session_id=None, statuses=("PENDING",), limit=200):
        sql = ["SELECT * FROM candidates WHERE project_id=?"]
        args = [self.project_id]
        if session_id:
            sql.append("AND session_id=?")
            args.append(session_id)
        if statuses:
            sql.append("AND status IN ({0})".format(
                ",".join("?" for _ in statuses)))
            args.extend(statuses)
        sql.append("ORDER BY created_at, candidate_id LIMIT ?")
        args.append(int(limit))
        out = []
        for row in self.conn.execute(" ".join(sql), args):
            record = dict(row)
            record["payload"] = json.loads(record["payload_json"])
            out.append(record)
        return out

    # ── retrieval index ─────────────────────────────────────────────────────
    def index_item(self, item_type, item_id, title, text, branch=None,
                   occurred_at=None, status=None, authority=None, file_paths=()):
        """把一筆記憶登記進 retrieval index(lexical + symbol + 可選 FTS)。"""
        uid = _uid(item_type, item_id)
        now = utc_now()
        blob = " ".join(t for t in (title, text) if t)
        toks = textnorm.tokens(blob)
        counted = {}
        for token in toks:
            counted[token] = counted.get(token, 0) + 1
        syms = textnorm.symbols(blob)
        with self.conn:
            self.conn.execute(
                "INSERT INTO items(item_uid, project_id, item_type, item_id, title,"
                " text, branch, occurred_at, status, authority, paths_json, indexed_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"
                " ON CONFLICT(item_uid) DO UPDATE SET title=excluded.title,"
                "   text=excluded.text, branch=excluded.branch,"
                "   occurred_at=excluded.occurred_at, status=excluded.status,"
                "   authority=excluded.authority, paths_json=excluded.paths_json,"
                "   indexed_at=excluded.indexed_at",
                (uid, self.project_id, item_type, item_id, title, text, branch,
                 occurred_at, status, authority,
                 json.dumps(list(file_paths), ensure_ascii=False), now))
            self.conn.execute("DELETE FROM item_tokens WHERE item_uid=?", (uid,))
            self.conn.executemany(
                "INSERT INTO item_tokens(item_uid, token, tf) VALUES(?,?,?)",
                [(uid, token, tf) for token, tf in counted.items()])
            self.conn.execute("DELETE FROM item_symbols WHERE item_uid=?", (uid,))
            self.conn.executemany(
                "INSERT INTO item_symbols(item_uid, symbol, norm) VALUES(?,?,?)",
                [(uid, s, textnorm.normalize_symbol(s))
                 for s in dict.fromkeys(syms)])
            for p in file_paths:
                # 檔案路徑本身就是使用者會拿來查的 symbol(「db.ts 那條規則是什麼」)
                self.conn.execute(
                    "INSERT OR REPLACE INTO item_symbols(item_uid, symbol, norm)"
                    " VALUES(?,?,?)", (uid, p, textnorm.normalize_symbol(p)))
            if self.caps.get(schema.CAP_FTS5):
                self.conn.execute(
                    "DELETE FROM items_fts WHERE item_uid=?", (uid,))
                self.conn.execute(
                    "INSERT INTO items_fts(item_uid, tokens) VALUES(?,?)",
                    (uid, " ".join(toks)))
            if self.caps.get(schema.CAP_TRIGRAM):
                self.conn.execute(
                    "DELETE FROM items_tri WHERE item_uid=?", (uid,))
                self.conn.execute(
                    "INSERT INTO items_tri(item_uid, raw) VALUES(?,?)", (uid, blob))
        return uid

    def item(self, uid):
        row = self.conn.execute(
            "SELECT * FROM items WHERE item_uid=?", (uid,)).fetchone()
        return dict(row) if row else None

    def item_count(self, item_type=None):
        if item_type:
            return self.conn.execute(
                "SELECT COUNT(*) FROM items WHERE project_id=? AND item_type=?",
                (self.project_id, item_type)).fetchone()[0]
        return self.conn.execute(
            "SELECT COUNT(*) FROM items WHERE project_id=?",
            (self.project_id,)).fetchone()[0]

    def clear_index(self):
        """重建 index 前清空(rebuild 路徑用;不動 durable 來源)。"""
        with self.conn:
            for table in ("item_tokens", "item_symbols", "items", "embeddings"):
                self.conn.execute("DELETE FROM " + table)
            if self.caps.get(schema.CAP_FTS5):
                self.conn.execute("DELETE FROM items_fts")
            if self.caps.get(schema.CAP_TRIGRAM):
                self.conn.execute("DELETE FROM items_tri")

    def clear_durable_mirror(self):
        """清掉「從 .dev-flow 鏡射進來的」列,保留 local-only 資料(§29)。

        rebuild 的語意是「durable 是正本,local 鏡射重建」——所以只刪 durable=1,
        legacy/local-only 的 observation 與候選知識一律留著,不得被 rebuild 毀掉。
        """
        with self.conn:
            for table in ("events", "facts", "knowledge", "decisions", "skills"):
                self.conn.execute("DELETE FROM " + table + " WHERE durable=1")

    def reindex_local_rows(self):
        """把 durable=0 / legacy 列重新登記進 retrieval index。

        rebuild 會 `clear_index()`;只重載 `.dev-flow/` 的話,留下的
        local-only 列還在表裡,但 DOMAIN/DISCOVERY 已經找不到它們。
        這支補回檢索可見性,不把列升級成 durable。
        """
        for row in self.conn.execute(
                "SELECT * FROM facts WHERE project_id=? AND durable=0",
                (self.project_id,)):
            row = dict(row)
            deps = json.loads(row["dependencies_json"] or "[]")
            self.index_item(
                "fact", row["fact_id"],
                "{entity_type}.{entity_key}.{fact_key}".format(**row),
                " ".join([row["entity_type"], row["entity_key"],
                          row["fact_key"], row["value"]]),
                status=row["status"], file_paths=deps,
                occurred_at=row["recorded_at"])
        for row in self.conn.execute(
                "SELECT * FROM knowledge WHERE project_id=? AND durable=0",
                (self.project_id,)):
            row = dict(row)
            self.index_item(
                "knowledge", row["knowledge_id"], row["title"],
                " ".join([row["kind"], row["key"], row["title"],
                          row["body"] or ""]),
                status=row["status"], authority=row["authority"],
                occurred_at=row["recorded_at"])
        for row in self.conn.execute(
                "SELECT * FROM decisions WHERE project_id=? AND durable=0",
                (self.project_id,)):
            row = dict(row)
            self.index_item(
                "decision", row["decision_id"], row["title"],
                " ".join([row["key"], row["title"], row["decision"],
                          row["reason"], row["alternatives"],
                          row["tradeoff"]]),
                status=row["status"], occurred_at=row["recorded_at"])
        for row in self.conn.execute(
                "SELECT * FROM skills WHERE project_id=? AND durable=0",
                (self.project_id,)):
            row = dict(row)
            steps = json.loads(row["steps_json"] or "[]")
            self.index_item(
                "skill", row["skill_id"], row["title"],
                " ".join([row["key"], row["title"], " ".join(steps),
                          row["preconditions"] or "",
                          row["verification"] or ""]),
                status=row["status"], occurred_at=row["recorded_at"])
        for row in self.conn.execute(
                "SELECT * FROM events WHERE project_id=? AND durable=0",
                (self.project_id,)):
            row = dict(row)
            rel = json.loads(row["paths_json"] or "[]")
            self.index_item(
                "event", row["event_id"], row["title"],
                "\n".join([row["kind"] or "", row["title"] or "",
                           row["body"] or ""]),
                branch=row["branch"], occurred_at=row["occurred_at"],
                status=row["signal"], file_paths=rel)

    # ── embeddings(§24 版本三件套)──────────────────────────────────────────
    def put_embedding(self, uid, provider, model, dim, version, vector_bytes,
                      now=None):
        with self.conn:
            self.conn.execute(
                "INSERT INTO embeddings(item_uid, provider, model, dim, version,"
                " vector, indexed_at) VALUES(?,?,?,?,?,?,?)"
                " ON CONFLICT(item_uid) DO UPDATE SET provider=excluded.provider,"
                "   model=excluded.model, dim=excluded.dim,"
                "   version=excluded.version, vector=excluded.vector,"
                "   indexed_at=excluded.indexed_at",
                (uid, provider, model, int(dim), version,
                 sqlite3.Binary(vector_bytes), now or utc_now()))

    def embedding_rows(self, provider, model, version):
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM embeddings WHERE provider=? AND model=? AND version=?",
            (provider, model, version))]

    def embedding_mismatch(self, provider, model, version, dim):
        """回傳與目前 provider/model/version/dim 不符的 embedding 數量。

        §24 的核心:換 model 不能讓舊 vector 的 similarity 靜默變成 0 —— 要先被
        「數得出來」,才有辦法決定 re-index。
        """
        return self.conn.execute(
            "SELECT COUNT(*) FROM embeddings WHERE NOT"
            " (provider=? AND model=? AND version=? AND dim=?)",
            (provider, model, version, int(dim))).fetchone()[0]

    def embedding_missing(self, provider, model, version, dim):
        """現行 items 裡,沒有「當前 signature」那一列 embedding 的筆數。

        與 `embedding_mismatch` 正交:mismatch 數的是**已存在但簽章錯**的
        向量;missing 數的是**這個 item 根本沒有可用向量**。只看前者會把
        「向量通道不完整」說成健康。
        """
        return self.conn.execute(
            "SELECT COUNT(*) FROM items i LEFT JOIN embeddings e"
            " ON e.item_uid = i.item_uid"
            " AND e.provider=? AND e.model=? AND e.version=? AND e.dim=?"
            " WHERE e.item_uid IS NULL",
            (provider, model, version, int(dim))).fetchone()[0]

    def embedding_orphaned(self, provider, model, version, dim):
        """有當前 signature 的 embedding、但 items 列已經不在的筆數。"""
        return self.conn.execute(
            "SELECT COUNT(*) FROM embeddings e LEFT JOIN items i"
            " ON i.item_uid = e.item_uid"
            " WHERE i.item_uid IS NULL"
            " AND e.provider=? AND e.model=? AND e.version=? AND e.dim=?",
            (provider, model, version, int(dim))).fetchone()[0]

    def drop_mismatched_embeddings(self, provider, model, version, dim):
        with self.conn:
            cur = self.conn.execute(
                "DELETE FROM embeddings WHERE NOT"
                " (provider=? AND model=? AND version=? AND dim=?)",
                (provider, model, version, int(dim)))
        return cur.rowcount

    # ── metrics ─────────────────────────────────────────────────────────────
    def record_metric(self, query_kind, status, latency_ms, hits, now=None):
        with self.conn:
            self.conn.execute(
                "INSERT INTO retrieval_metrics(project_id, query_kind, status,"
                " latency_ms, hits, recorded_at) VALUES(?,?,?,?,?,?)",
                (self.project_id, query_kind, status, float(latency_ms),
                 int(hits), now or utc_now()))
