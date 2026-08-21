"""dev-setup 的 memory 階段(**不是**新的 init 指令)。

本檔刻意不提供任何面向使用者的 `init`。專案的 setup / repair / rebuild 入口
**只有一個**:既有的 `dev-setup` skill。這裡是它呼叫的實作,行為必須:

  1. 找 repository root
  2. 檢查 `.dev-flow/project.yaml`;不存在 → 建 project_id + 最低限度結構
  3. 存在 → **reuse** project_id(重跑不得產生新的)
  4. 註冊當前 local workspace(path / OS / branch / HEAD / worktree)
  5. initialize / migrate local DB
  6. 從 `.dev-flow` 重建 local index、FTS
  7. 需要時 re-index embeddings
  8. 掛既有 legacy 資料的 project_path → project_id 對照
  9. 全程 idempotent

回報一律結構化(dev-setup 的回報格式固定四段,它需要可直接鋪成表格的資料)。
"""
import os

from . import (LOCAL_SCHEMA_VERSION, durable, embedding, identity, legacy,
               paths, schema, signal, store as store_mod, sync, truth)


class SetupError(RuntimeError):
    """setup 前置條件不成立(不在 git repo / project.yaml 壞掉)。"""


def run(start_path=None, rebuild=True, reindex_embeddings=True,
        migrate_legacy=True, name=None):
    """執行 memory 階段。回傳結構化報告(dev-setup 直接鋪表用)。"""
    root = paths.repo_root(start_path)
    if root is None:
        raise SetupError(
            "找不到 repository root —— memory 的 identity 住在 Git 裡,"
            "不在 Git 裡的目錄沒有可攜的 project identity")

    project, created = identity.ensure_project(root, name=name)
    snapshot = identity.workspace_snapshot(root)
    workspace_id = identity.workspace_key(project["project_id"],
                                          snapshot["local_path"])

    created_dirs = durable.ensure_layout(root, [durable.STATE_DIR])
    archived_legacy = store_mod.archive_legacy_shared_db(project["project_id"])
    store = store_mod.open_for_root(project["project_id"], root)
    try:
        store.register_workspace(workspace_id, snapshot)
        if migrate_legacy:
            store.map_legacy_path(
                snapshot["local_path"],
                note="dev-setup 註冊:legacy 資料以 project_path 為鍵時的對照")
        legacy_report = (legacy.migrate(root, store, apply_changes=False)
                         if migrate_legacy else None)

        counts = sync.rebuild_local(root, store) if rebuild else {}
        embedder = embedding.Embedder()
        embedding_report = embedder.mismatch_report(store)
        reindexed = embedder.reindex(store) if reindex_embeddings else 0

        # 重建之後立刻做一次失效掃描:當前 checkout 與 durable 側的 VERIFIED
        # 對不上時,使用者第一個查詢就該看到 STALE,而不是拿到 main 的舊答案。
        stale = truth.invalidate_from_snapshot(store, root, workspace_id,
                                              snapshot)
        report = {
            "project_id": project["project_id"],
            "project_name": project.get("name"),
            "project_created": created,
            "durable_dir": identity.memory_dir_name(),
            "durable_created_dirs": [os.path.relpath(d, root).replace("\\", "/")
                                     for d in created_dirs],
            "workspace_id": workspace_id,
            "workspace": snapshot,
            "local_db": store_mod.runtime_db_path(project["project_id"], root),
            "legacy_shared_db_archived": archived_legacy,
            "schema_version": LOCAL_SCHEMA_VERSION,
            "capabilities": {k: bool(v) for k, v in store.caps.items()},
            "durable_inventory": durable.inventory(root),
            "rebuilt": counts,
            "embedding": embedding_report,
            "embeddings_reindexed": reindexed,
            "stale_after_rebuild": len(stale),
            "legacy": legacy_report,
            "indexed_items": store.item_count(),
        }
    finally:
        store.close()
    return report


def doctor(start_path=None):
    """健檢:回報**可判定**的事實與明確的修法,不猜、不自動修。"""
    findings = []
    root = paths.repo_root(start_path)
    if root is None:
        return {"verdict": "FAIL", "findings": [
            {"level": "error", "check": "repo-root",
             "detail": "不在 git repository 內",
             "fix": "在 repo 內執行,或先 git init"}]}

    project_path = identity.project_file(root)
    if not os.path.isfile(project_path):
        findings.append({
            "level": "error", "check": "project-identity",
            "detail": "{0} 不存在".format(
                os.path.relpath(project_path, root).replace("\\", "/")),
            "fix": "跑 dev-setup(唯一 setup 入口)"})
        return {"verdict": "FAIL", "findings": findings}

    project = identity.read_project(root)
    findings.append({"level": "ok", "check": "project-identity",
                     "detail": "project_id={0}".format(project["project_id"]),
                     "fix": ""})
    if project.get("schema_version_mismatch"):
        findings.append({
            "level": "warn", "check": "durable-schema",
            "detail": "project.yaml 的 schema_version 與本工具不同",
            "fix": "升級 dev-flow 後重跑 dev-setup"})

    leftover = store_mod.legacy_shared_db_path(project["project_id"])
    if os.path.isfile(leftover):
        findings.append({
            "level": "warn", "check": "legacy-shared-db",
            "detail": "發現舊的專案級共用 DB,不會再被打開:{0}".format(leftover),
            "fix": "跑 dev-setup:會把它改名封存,不把舊 OPEN session 扇出到各 worktree"})

    db = store_mod.runtime_db_path(project["project_id"], root)
    if not os.path.isfile(db):
        findings.append({
            "level": "warn", "check": "local-db",
            "detail": "local index 不存在(這不是資料遺失 —— durable 側是正本)",
            "fix": "跑 dev-setup 重建"})
        return {"verdict": "WARN", "findings": findings,
                "project_id": project["project_id"]}

    store = store_mod.open_for_root(project["project_id"], root)
    try:
        version = schema.current_version(store.conn)
        findings.append({
            "level": "ok" if version == LOCAL_SCHEMA_VERSION else "warn",
            "check": "local-schema",
            "detail": "local schema v{0}(工具支援 v{1})".format(
                version, LOCAL_SCHEMA_VERSION),
            "fix": "" if version == LOCAL_SCHEMA_VERSION else "跑 dev-setup 遷移"})
        for cap, enabled in sorted(store.caps.items()):
            findings.append({
                "level": "ok" if enabled else "warn",
                "check": "capability/" + cap,
                "detail": "可用" if enabled else "不可用(retrieval 少一個通道)",
                "fix": "" if enabled else
                       "換一個帶 FTS5 的 python3(不影響正確性,只影響排序品質)"})
        report = embedding.Embedder().mismatch_report(store)
        embedding_ok = (not report["mismatched"] and not report["missing"]
                        and not report["orphaned"])
        findings.append({
            "level": "ok" if embedding_ok else "warn",
            "check": "embedding-version",
            "detail": "{0} 筆 signature 不符,{1} 筆缺向量,{2} 筆孤兒向量".format(
                report["mismatched"], report["missing"], report["orphaned"]),
            "fix": "" if embedding_ok else report["action"]})
        try:
            current = sync.durable_generation(root)
        except (OSError, durable.DurableError, ValueError) as exc:
            findings.append({
                "level": "error", "check": "durable-source-readable",
                "detail": str(exc),
                "fix": "修復 .dev-flow/ 內不可讀或非一般檔後重跑 doctor"})
            current = None
        stored = store.get_meta(sync.DURABLE_GENERATION_META)
        if current is None:
            freshness_level, freshness_detail, freshness_fix = (
                "warn",
                "durable source is unreadable; freshness not certified",
                "先排除 durable-source-readable")
        elif stored == current:
            freshness_level, freshness_detail, freshness_fix = (
                "ok", "local mirror generation matches .dev-flow/", "")
        elif stored is None:
            has_rows = store.has_durable_mirror()
            try:
                has_content = durable.has_mirrorable_content(root)
            except (OSError, durable.DurableError, ValueError):
                has_content = True
            if not has_content and not has_rows:
                freshness_level, freshness_detail, freshness_fix = (
                    "ok", "empty project, no durable mirror to certify", "")
            else:
                freshness_level, freshness_detail, freshness_fix = (
                    "warn",
                    "missing durable-generation stamp while durable content or "
                    "mirror rows exist — local mirror is uncertified",
                    "跑 dev-setup 重建鏡射")
        else:
            freshness_level, freshness_detail, freshness_fix = (
                "warn",
                "durable source changed; local mirror needs refresh "
                "(stored generation != current .dev-flow/)",
                "跑 dev-setup 或一次 ask 重建鏡射")
        findings.append({
            "level": freshness_level, "check": "durable-mirror-freshness",
            "detail": freshness_detail, "fix": freshness_fix})
        leaks = _absolute_path_leaks(root)
        findings.append({
            "level": "ok" if not leaks else "error",
            "check": "durable-relative-paths",
            "detail": "durable 樹內絕對路徑 {0} 處".format(len(leaks)),
            "fix": "" if not leaks else
                   "人工修掉 {0};durable memory 只收 repo-relative 路徑".format(
                       ", ".join(leaks[:3]))})
        secrets = _secret_leaks(root)
        findings.append({
            "level": "ok" if not secrets else "error",
            "check": "durable-secrets",
            "detail": (
                "durable 樹內疑似敏感內容 0 處" if not secrets else
                "durable 樹內疑似敏感內容 {0} 處({1})".format(
                    len(secrets),
                    "; ".join("{0}@{1}".format(",".join(names), rel)
                              for rel, names in secrets[:3]))),
            "fix": "" if not secrets else
                   "人工移出 {0};durable memory 拒絕固化敏感內容".format(
                       ", ".join(rel for rel, _names in secrets[:3]))})
        snapshot = identity.workspace_snapshot(root)
        workspace_id = identity.workspace_key(project["project_id"],
                                              snapshot["local_path"])
        overlays = store.overlays(workspace_id)
        findings.append({
            "level": "ok" if not overlays else "warn",
            "check": "current-truth-overlay",
            "detail": "本機有 {0} 筆 fact 處於 STALE/CONFLICT".format(len(overlays)),
            "fix": "" if not overlays else
                   "查詢時會要求重新 inspect;這是預期行為,不是故障"})
    finally:
        store.close()

    levels = {f["level"] for f in findings}
    verdict = "FAIL" if "error" in levels else ("WARN" if "warn" in levels
                                                else "PASS")
    return {"verdict": verdict, "findings": findings,
            "project_id": project["project_id"]}


def _absolute_path_leaks(root):
    leaks = []
    durable_root = durable.root(root)
    if not os.path.isdir(durable_root):
        return leaks
    for dirpath, _dirs, files in os.walk(durable_root):
        for name in files:
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as stream:
                    text = stream.read()
            except (OSError, UnicodeDecodeError):
                continue
            if paths.scan_absolute_paths(text):
                leaks.append(os.path.relpath(path, root).replace("\\", "/"))
    return leaks


def _secret_leaks(root):
    """掃 durable 樹的敏感 pattern。只回檔名與 pattern 名,不回命中原文。"""
    leaks = []
    durable_root = durable.root(root)
    if not os.path.isdir(durable_root):
        return leaks
    for dirpath, _dirs, files in os.walk(durable_root):
        for name in files:
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as stream:
                    text = stream.read()
            except (OSError, UnicodeDecodeError):
                continue
            hits = signal.scan_sensitive(text)
            if hits:
                leaks.append((os.path.relpath(path, root).replace("\\", "/"),
                              hits))
    return leaks
