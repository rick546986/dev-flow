"""legacy 記憶載體的遷移(§1/§29)。

三個 legacy 載體,三種處理方式 —— **刻意不一致**,因為它們的性質不同:

  ①`CONTEXT.md`(repo root 的人工維護詞彙表)
     它就是舊架構的 domain knowledge:人工維護、開場整份注入、沒有 authority、
     沒有 status、沒有證據、腐化時沒有任何機制會發現。
     → 遷移到 `knowledge/domain/`,但**一律以 CANDIDATE + documentation authority
       落地**,證據指回原檔。不得直接標成 CONFIRMED:沒有人在遷移的那一刻重新
       確認過那些詞條還成立,把它們寫成已確認就是「把猜測 promotion 成 verified」。

  ②`docs/dev/HISTORY.md`(改版歷史索引)
     它是**人的變更紀錄**,住 `docs/dev/`(人的文檔區),而且有唯一寫入口、
     append-only 守衛、發版流程在用。它不是 agent memory 的載體。
     → **不搬進 `.dev-flow/`**(那會變成同一份內容的兩個 durable 正本,
       而兩個正本必然漂移)。改成**索引進 local memory**(legacy 標記),
       讓「之前發生過什麼」查得到它;HISTORY.md 本身留在原地繼續給人看。

  ③legacy 以 `project_path` 為鍵的 local 資料
     → 建 `project_path → project_id` 對照(store.map_legacy_path),
       既有資料一列都不刪。

預設是 **dry-run**:先回報「會做什麼」,由 dev-setup 決定要不要套用。
"""
import os
import re

from . import paths, store as store_mod

CONTEXT_FILE = "CONTEXT.md"
HISTORY_FILE = os.path.join("docs", "dev", "HISTORY.md")

LEGACY_AUTHORITY = "documentation"
LEGACY_STATUS = "CANDIDATE"

# `**Contract(合約)**:客戶與本公司簽署的服務協議,一筆 = contracts 表一列。`
_TERM = re.compile(r"^\*\*(?P<term>[^*]+)\*\*\s*[::]\s*(?P<body>.+)$")
_AVOID = re.compile(r"^_Avoid_\s*[::]\s*(?P<avoid>.+)$")
_PLACEHOLDER = re.compile(r"^<.*>$")

# `## 2026-07-31 · methodology-corrections [· v3.0.0]`
_HISTORY_HEAD = re.compile(
    r"^##\s+(?P<date>\d{4}-\d{2}-\d{2})\s+·\s+(?P<slug>[^·\n]+?)"
    r"(?:\s+·\s+(?P<version>v[\d.]+))?\s*$")
_HISTORY_FIELD = re.compile(r"^-\s*(?P<label>[^::]+)\s*[::]\s*(?P<value>.+)$")


def parse_context_md(text):
    """解析詞彙表。回傳 [{key, title, body, avoid, proposed}]。

    只認舊模板明文規定的形狀(`**詞**:定義` + 選填 `_Avoid_:`)。
    認不出來的行**原樣回報成 unparsed**,不猜 —— 猜錯會把散文塞成詞條。
    """
    terms = []
    unparsed = []
    current = None
    in_language = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            in_language = "Language" in line or "語言" in line or "詞彙" in line
            continue
        if not in_language or not line or line.startswith(">") \
                or line.startswith("<!--"):
            continue
        match = _TERM.match(line)
        if match:
            term = match.group("term").strip()
            if _PLACEHOLDER.match(term):
                continue                      # 模板佔位符,不是真詞條
            key = re.split(r"[((]", term)[0].strip()
            current = {
                "key": key, "title": term,
                "body": match.group("body").strip(), "avoid": "",
                "proposed": "提案中" in term or "尚未實作" in match.group("body"),
            }
            terms.append(current)
            continue
        avoid = _AVOID.match(line)
        if avoid and current is not None:
            value = avoid.group("avoid").strip()
            if not _PLACEHOLDER.match(value):
                current["avoid"] = value
            continue
        unparsed.append(line)
    return terms, unparsed


def parse_history_md(text):
    """解析改版歷史索引。回傳 [{date, slug, version, fields}]。"""
    entries = []
    current = None
    for raw in text.splitlines():
        head = _HISTORY_HEAD.match(raw.strip())
        if head:
            current = {"date": head.group("date"),
                       "slug": head.group("slug").strip(),
                       "version": head.group("version") or "",
                       "fields": {}}
            entries.append(current)
            continue
        if current is None:
            continue
        field = _HISTORY_FIELD.match(raw.strip())
        if field:
            current["fields"][field.group("label").strip()] = \
                field.group("value").strip()
    return entries


def migrate(repo_root, store, apply_changes=False, promote=False, now=None):
    """遷移 legacy 載體。

    apply_changes=False(預設)→ 只回報會做什麼,不寫任何東西。
    apply_changes=True        → 寫進 local memory(legacy 標記)。
    promote=True              → 額外把詞彙表寫進 `.dev-flow/knowledge/domain/`,
                                狀態一律 CANDIDATE(可見、進 Git、但明確標未確認)。
    """
    now = now or store_mod.utc_now()
    report = {"context_md": None, "history_md": None, "applied": apply_changes,
              "promoted": promote, "written": []}

    context_path = os.path.join(repo_root, CONTEXT_FILE)
    if os.path.isfile(context_path):
        with open(context_path, encoding="utf-8") as stream:
            terms, unparsed = parse_context_md(stream.read())
        report["context_md"] = {
            "path": CONTEXT_FILE, "terms": len(terms),
            "unparsed_lines": len(unparsed),
            "keys": [t["key"] for t in terms],
            "target": "knowledge/domain/(status={0}, authority={1})".format(
                LEGACY_STATUS, LEGACY_AUTHORITY),
            "note": "遷移後不重新產生 CONTEXT.md;內容的正本改為 durable memory",
        }
        if apply_changes:
            for term in terms:
                body = term["body"]
                if term["avoid"]:
                    body += "\n禁用同義詞:" + term["avoid"]
                store.upsert_knowledge({
                    "kind": "domain", "key": term["key"], "title": term["title"],
                    "body": body, "authority": LEGACY_AUTHORITY,
                    "status": LEGACY_STATUS, "confidence": 0.4,
                    "recorded_at": now, "legacy": True,
                    "evidence": [{"type": "file", "ref": CONTEXT_FILE,
                                  "stance": "legacy_import"}]})
            if promote:
                from . import durable
                for term in terms:
                    body = term["body"]
                    if term["avoid"]:
                        body += "\n禁用同義詞:" + term["avoid"]
                    report["written"].append(durable.write_knowledge(
                        repo_root, {
                            "kind": "domain", "key": term["key"],
                            "title": term["title"], "body": body,
                            "authority": LEGACY_AUTHORITY,
                            "status": LEGACY_STATUS, "confidence": 0.4,
                            "recorded_at": now,
                            "evidence": [{"type": "file", "ref": CONTEXT_FILE,
                                          "stance": "legacy_import"}]}))

    history_path = os.path.join(repo_root, HISTORY_FILE)
    if os.path.isfile(history_path):
        with open(history_path, encoding="utf-8") as stream:
            entries = parse_history_md(stream.read())
        report["history_md"] = {
            "path": paths.to_posix(HISTORY_FILE), "entries": len(entries),
            "target": "local events(legacy 標記;**不**複製進 .dev-flow/events/)",
            "note": "HISTORY.md 留在 docs/dev/ 給人看;memory 只索引它,"
                    "不建立第二份 durable 正本",
        }
        if apply_changes:
            for entry in entries:
                fields = entry["fields"]
                body_parts = [
                    "{0}:{1}".format(label, value)
                    for label, value in sorted(fields.items())]
                store.add_event(
                    "important_discovery",
                    "{0} · {1}{2}".format(
                        entry["date"], entry["slug"],
                        " · " + entry["version"] if entry["version"] else ""),
                    "\n".join(body_parts),
                    occurred_at=entry["date"] + "T00:00:00Z",
                    signal="high", source_type="documentation",
                    source_ref=paths.to_posix(HISTORY_FILE),
                    durable=False, legacy=True)
    return report
