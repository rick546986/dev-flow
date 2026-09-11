# Knowledge-index call-path fixture (#155 Pilot-3)

Prove **記得到、叫得到** without waiting for P2's production
`docs/knowledge/index.yaml`.

| Path | Role |
|---|---|
| `index.yaml` | Minimal topic → `active_adr` short index |
| `docs/adr/0003-*.md` | Target file the index must resolve to |

## Retrieve (叫得到)

Prefer production index when present; else this fixture:

```bash
# Resolve topic → active ADR path → file must exist (exit 0)
python3 scripts/proof-knowledge-index-call-path.py
python3 scripts/proof-knowledge-index-call-path.py --topic agent-memory
echo exit:$?
```

Force fixture (even if P2 later lands `docs/knowledge/index.yaml`):

```bash
python3 scripts/proof-knowledge-index-call-path.py \
  --index scripts/fixtures/knowledge-index/index.yaml \
  --root scripts/fixtures/knowledge-index \
  --topic agent-memory
```

Agent Q&A entry (existing memory CLI — do **not** preload all ADRs):

```bash
python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" ask "<問題>"
# Optional orientation (no full dump):
python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" context
```

Skill/guide rule: **專案問答先短索引 / `dev-memory.py ask`;禁預載全部 `docs/adr/` 與全量 specs;再按回傳 path 載單檔。**

## Record (記得到) — point at existing paths; do not reimplement

Discussion semantics (only `talk end` writes durable):

```bash
python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" talk start "<主題>"
# … turn / propose / confirm|reject|correct …
python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" talk end "$MEMORY_SESSION_ID"
```

Stage 6 checkpoint → memory commit (see `skills/dev-run/SKILL.md`):

```bash
python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" session start \
  --mode implementation --slug <slug>
# … observe / W6 inventory …
python3 "${DEVFLOW_ROOT}/memory/dev-memory.py" checkpoint "$MEMORY_SESSION_ID" --end
# then memory commit + push + durable-check
```

## Knife-2 ask wiring (landed)

`dev-memory.py ask` now routes CURRENT / topic-like questions through
`docs/knowledge/index.yaml` (see `memory/agentmem/knowledge_index.py`).

```bash
PYTHONPATH=memory python3 memory/dev-memory.py ask "目前 agent-memory 決策指向哪份 ADR?" --json
# knowledge_index.status=hit → docs/adr/0003-*.md (+ durable pointers)
```

Still open beyond this knife item:

- `dev-setup` bootstrap / conflict queue for adopting repos
- Ban/enforce preload via gate (policy text + ask routing; gate teeth deferred)
