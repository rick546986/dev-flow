# Knowledge index (machine routing)

> **正本** = [`index.yaml`](./index.yaml)（機器可讀）  
> **人讀** = [`index.md`](./index.md) —— **只**由產生器從 yaml 同輪產出，禁止手維第二份真相。

## Regenerate

```bash
python3 scripts/build-knowledge-index.py --write
# freshness (CI / local):
scripts/check-knowledge-index.sh
```

## Schema (`index.yaml`)

```yaml
schema_version: 1
generated_from: [...]
notes: []               # generator warnings (legacy meta, mixed forms, …)
topics:
  <topic-key>:
    glossary: []      # → .dev-flow/knowledge/domain/<key> (pointers only)
    active_adr: []    # accepted ADR ids only; proposed never enters
    active_spec: []   # → docs/specs/<domain>.md paths
    durable:
      decisions: []   # decision keys (not DEC-* filenames)
      knowledge: []   # invariant/intent keys
    supersedes:
      - from: "0001"
        to: "0003"
        mode: full    # full | partial
        scopes: []    # non-empty iff mode=partial
    conflicts: []     # e.g. multi-active-adr — queue only; do not auto-pick
unscoped:
  decisions: []       # durable keys with no topic token match
  knowledge: []
```

Pointers only — no ADR / DEC / spec / knowledge bodies.

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

After ADR meta changes, re-run `--write` so the index stays fresh.

## Sample topic lookup (this repo)

```bash
python3 scripts/build-knowledge-index.py --check
# then open docs/knowledge/index.yaml and search e.g.
#   agent-memory: → active_adr: ["0003"]
```

## Non-goals (this slice)

- Full agent ask / Q&A routing
- Auto-resolving conflicts
- Inlining durable knowledge bodies
