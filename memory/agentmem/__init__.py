"""agentmem — dev-flow Agent Memory v3(python3 標準庫,無第三方依賴)。

兩層分離是本套件的第一原則,任何模組都不得混用:

  ①**durable memory**(`.dev-flow/`,進 Git)—— 高訊號、可攜、路徑無關。
    只放結構化知識:project identity / implementation truth / domain knowledge /
    intent / historical event / decision / procedural skill。
  ②**local runtime memory**
    (`~/.agentmem/projects/<project_id>/worktrees/<worktree_key>/`,不進 Git)——
    SQLite 索引、FTS、embedding、原始 transcript、候選知識、本機失效 overlay。
    **per-worktree**:兩個 worktree 不共用這份可變檔。可以整包刪掉再從 ①重建,
    刪掉不損失 durable 記憶。

模組:
- ids          ULID(project/session/event/fact… 前綴分類;path-independent identity)
- paths        repo root 解析 + repo-relative POSIX 正規化 + 絕對路徑守衛
- yamlmini     受限 YAML 子集的 deterministic emitter/parser(durable 檔用)
- identity     `.dev-flow/project.yaml` 與 local workspace 註冊
- schema       local SQLite schema + 版本化 migration
- store        local runtime store(events/facts/knowledge/candidates/embeddings/FTS)
- durable      `.dev-flow/` 讀寫(唯一 durable 寫入口)+ rebuild 來源
- signal       Signal Gate(高/低訊號分流)+ 敏感內容守衛
- textnorm     Unicode-aware tokenization + code symbol 抽取
- embedding    versioned embedding provider(model/dimension/version 都記)
- retrieval    multi-channel retrieval + RRF fusion
- truth        LVP-inspired Current Truth Resolver + invalidation
- query        Query Planner / Execution Engine(CURRENT/HISTORY/WHY/HOW/DOMAIN/INTENT)
- context      Startup Context Builder(小、結構化、不讀 CONTEXT.md)
- devtalk      Project Understanding Mode 的候選知識生命週期
- consolidate  candidate → durable 的固化(唯一 durable 寫入時機)
- lineage      修正歷史(knowledge/fact/decision 的 append-only revision)
- legacy       legacy 資料遷移(project_path → project_id、CONTEXT.md 詞彙表)
- evalharness  memory evaluation(Recall@5/MRR/Current Truth Accuracy/…)
"""

LOCAL_SCHEMA_VERSION = 2
"""local SQLite schema 版本(migration 的目標版本;見 schema.py)。

刻意與「Agent Memory v3 架構」的 3 分開編號:架構代號是對外的敘述,
schema 版本是 migration 的機械依據,兩者同步只會在下次架構命名時互相誤導。"""

DURABLE_SCHEMA_VERSION = 1
"""`.dev-flow/` durable 檔案格式版本(project.yaml 的 schema_version)。"""
