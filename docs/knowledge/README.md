# Knowledge index (machine routing)

> **正本** = [`index.yaml`](./index.yaml)（機器可讀）  
> **人讀** = [`index.md`](./index.md) —— **只**由產生器從 yaml 同輪產出，禁止手維第二份真相。  
> **衝突佇列** = [`conflicts-queue.yaml`](./conflicts-queue.yaml) —— 人工裁決；**永不**自動挑 winner。

## Regenerate / bootstrap (adopting repos)

```bash
# Preferred for already-installed projects (dry-run default):
python3 scripts/bootstrap-knowledge-index.py --root <project>           # report
python3 scripts/bootstrap-knowledge-index.py --root <project> --apply   # write index + twin + queue

# Generator only (no queue file):
python3 scripts/build-knowledge-index.py --write

# freshness (CI / local) — index + human twin + queue:
scripts/check-knowledge-index.sh
```

`dev-setup` install／upgrade／fix 會跑 bootstrap `--apply`；check 跑 `--check`（見 `skills/dev-setup/SKILL.md`）。

## Schema (`index.yaml`)

```yaml
schema_version: 1
generated_from: [...]
notes: []               # generator warnings (legacy meta, mixed forms, …)
topics:
  <topic-key>:
    glossary: []      # → .dev-flow/knowledge/domain/<key> (pointers only)
    active_adr: []    # accepted ADR ids only; proposed never enters
                      # multi-active → [] + conflicts (never auto-pick)
    active_spec: []   # → docs/specs/<domain>.md paths
    durable:
      decisions: []   # decision keys (not DEC-* filenames)
      knowledge: []   # invariant/intent keys
    supersedes:
      - from: "0001"
        to: "0003"
        mode: full    # full | partial
        scopes: []    # non-empty iff mode=partial
    conflicts: []     # multi-active / bad-status / dangling / unparseable tags
unscoped:
  decisions: []       # durable keys with no topic token match
  knowledge: []
```

Pointers only — no ADR / DEC / spec / knowledge bodies.

## Conflict queue (`conflicts-queue.yaml`)

```yaml
schema_version: 1
context:
  path: null                 # or CONTEXT.md / docs/dev/CONTEXT.md
  status: absent             # or warn-candidate-only
notes: []
items:
  - kind: multi-active       # | bad-status | dangling | unparseable | context-warn
    path: docs/adr/0001-….md
    reason: multiple-accepted-same-topic
    adr_ids: ["0001", "0002"]
    topic: payments
    detail: do-not-auto-pick; human must choose winner or supersede
```

`CONTEXT.md`：只進 queue 當 **warn-candidate-only**（走既有 `migrate-legacy` → CANDIDATE）；**不**把內文灌進 index 當 routing 真相。

## ADR frontmatter (Pilot-1 landed)

```yaml
---
status: accepted          # proposed | accepted | deprecated | superseded
topics: [agent-memory]
supersedes: []
superseded_by: null
# optional (beyond MVP full-supersede):
# supersedes_partial:
#   - id: "0001"
#     scopes: [handshake-semantics]
---
```

This generator:

1. Prefers YAML frontmatter when present (`topics` / `supersedes` from meta).
2. Otherwise parses legacy `- Status: …` bullets and uses the filename slug as the sole topic (adopting repos mid-migration).
3. Does **not** rewrite ADR files (Pilot-1 owns migration / gate teeth).

After ADR meta changes, re-run bootstrap `--apply` (or generator `--write`) so the index stays fresh.

## Sample topic lookup (this repo)

```bash
python3 scripts/bootstrap-knowledge-index.py --check
# then open docs/knowledge/index.yaml and search e.g.
#   agent-memory: → active_adr: ["0003"]
```

## Ask wiring (#155 knife-2)

`dev-memory.py ask` consults this index when the query is **CURRENT** or
**topic-like** (content looks like a topic key after frame-stripping):

1. Match `topics.<key>` against the question.
2. Resolve only that topic’s `active_adr` / `active_spec` / durable pointers →
   repo-relative paths (no preload of all `docs/adr/` or specs).
3. Envelope field `knowledge_index`: `status` ∈
   `hit` | `unknown_topic` | `missing_index` | `unreadable` | `skipped`.

**Missing / unreadable index:** degrade — keep existing store retrieval and
status contract (`OK` / `NEEDS_VERIFICATION` / `CONFLICT` / `NO_RELIABLE_MATCH`);
`knowledge_index.note` explains the degrade. Ask never fails closed solely
because the index file is absent.

```bash
PYTHONPATH=memory python3 memory/dev-memory.py ask "目前 agent-memory 決策指向哪份 ADR?" --json
# → knowledge_index.status=hit, paths include docs/adr/0003-*.md
```

## Non-goals (remaining)

- Auto-resolving conflicts (queue only; human picks)
- Inlining durable knowledge bodies

## Preload ban tooth (#155 knife-2.3)

```bash
scripts/check-preload-ban.sh
```

CI via `devflow-check.sh` architecture. Pins ask-first one-liner, scans positive
preload anti-patterns, re-runs `proof-knowledge-index-call-path.py`.
**Limit:** Cursor/Grok have no PreToolUse bulk-Read block — portable tooth is
script+CI only.
