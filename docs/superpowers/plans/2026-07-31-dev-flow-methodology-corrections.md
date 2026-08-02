# dev-flow Methodology Corrections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove dev-flow's official dependency on harness, make large-work slicing self-contained, and give manual Stage 6 work the same per-task independent review obligation as `dev-run`.

**Architecture:** dev-flow remains a self-contained 4→7 execution method. Large work is handled through legal spec slices rather than an official external-engine escape hatch. Stage 6 owns a shared T acceptance seam; human reviewers and fresh-context reviewer Agents are adapters, while `dev-run` is one implementation of the same rule.

**Tech Stack:** Markdown SOP and templates, Claude Code plugin skills, Bash/Python guard scripts, static HTML guides.

## Global Constraints

- dev-flow must not depend on or officially route work to harness.
- Projects may privately use external orchestration; that choice is outside the dev-flow method.
- Large-work signals trigger a slicing feasibility assessment, not mandatory mechanical slicing.
- A slice is legal only when later slices depend solely on earlier slices' externally visible output.
- If no legal slicing seam exists, a feature may remain a single 4→7 pipeline.
- Stage 6 T review happens after GREEN, scope check, and Verify, but before commit.
- Stage 7 remains the feature-level G3 gate and is not replaced or duplicated by T review.
- Core rules describe reviewer capabilities, not a specific model, vendor, or Agent implementation.
- Do not modify `_retired-skills-20260726/`; it is historical material.
- Do not include the existing untracked `.serena/` directory in commits.

---

## 1. Remove the official harness dependency

### Files

- Modify: `README.md`
- Modify: `guide-dev-flow.html`
- Modify: `guide-quickstart.html`
- Modify: `dev-setup-record.html`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/skills/dev-flow/SKILL.md`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/skills/dev-setup/SKILL.md`

### README changes

- [ ] Change the repository overview from “slicing and engine routing” to “slicing and large-work rules.”
- [ ] Rewrite §13 as “Large work and slicing.”
- [ ] Delete the harness escape-hatch wording, the three automatic routing thresholds, and the dev-flow→harness conversion table.
- [ ] Convert these conditions into slicing feasibility signals:
  - three or more independent phases;
  - Diff Budget over 15 files;
  - work spanning multiple repositories.
- [ ] State that these signals do not prove a legal slicing seam exists.
- [ ] State that a large feature may remain one 4→7 pipeline when it cannot be split without leaking internal design between slices.
- [ ] State that long-running work resumes from `STATUS.md`, `5-tasks.md`, and `6-implementation-notes.md`; a new session does not require a second execution system.
- [ ] State that unattended multi-phase orchestration is outside the dev-flow method.

Suggested §13 core wording:

> 大案先評估切片可行性（見 §14）。≥3 個可獨立 phase、Diff Budget >15 檔、跨 repo，都是「可能需要切片」的訊號，不是強制切片條件。切片仍必須存在合法接縫；若沒有，保留單一 4→7 管線。跨 session 以 STATUS、5-tasks、6-notes 接力。外部 orchestration 是專案層選擇，dev-flow 不依賴也不規範它。

### §14 changes

- [ ] Delete the claim that §13 and §14 solve different problems and must coexist.
- [ ] Delete “each slice may choose its own engine” and “one engine per slice.”
- [ ] Preserve the soft `~40 scenarios` threshold and reviewer “too large to review once” judgment.
- [ ] Preserve the architectural seam requirement; do not permit splitting by count alone.
- [ ] Preserve per-slice 4→5→6→7, G2/G3, `parent`, unique IDs, slice ordering, and impact review.
- [ ] Clarify that repository separation is not automatically a slice seam.

### Active guide and setup changes

- [ ] Replace the harness engine-routing section in `guide-dev-flow.html` with the new large-work slicing flow.
- [ ] Replace named harness compatibility language in `guide-quickstart.html` with vendor-neutral “existing external workflow artifacts.”
- [ ] Update `dev-setup-record.html` so setup preserves unknown external artifacts without naming an official alternative engine.
- [ ] Remove the harness routing sentence from the live `dev-flow/SKILL.md`.
- [ ] In the live `dev-setup/SKILL.md`, preserve existing external directories generically and remove the instruction to convert through README §13.
- [ ] Leave retired skills unchanged and ensure no active file points users to them.

### Verification

- [ ] Run `git grep -n -i harness -- README.md guide-dev-flow.html guide-quickstart.html dev-setup-record.html` and confirm no official dependency or routing remains.
- [ ] Run `rg -n -i harness /Users/asheng/.claude/plugins/local/dev-flow/skills` and confirm active skills contain no official dependency or routing.

---

## 2. Establish the Stage 6 T acceptance seam

### Files

- Modify: `README.md`
- Modify: `_templates/6-implementation-notes.md`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/skills/dev-flow/SKILL.md`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/skills/dev-run/SKILL.md`

### Core rule

Every task follows this order:

```text
RED → GREEN → scope check → Verify
→ independent T review
→ PASS
→ commit
→ Progress Log + checkbox + review evidence
```

- [ ] Update README §5 so a T is incomplete until independent review passes.
- [ ] Require the reviewer to be different from the T implementer.
- [ ] Prefer an eligible human reviewer; otherwise use a fresh-context reviewer Agent.
- [ ] Require the reviewer to run the T's Verify command personally.
- [ ] Require checks for the T's Covers, RED→GREEN evidence, and its own Files scope.
- [ ] Require FAIL to return to the same T for correction and re-review.
- [ ] Permit a second reviewer for high-risk or disputed findings.
- [ ] Keep the core rule model- and vendor-neutral.

### `6-implementation-notes` changes

- [ ] Insert T review after Verify and before commit in the Stage 6 checklist.
- [ ] Add a `T Review Log` section with one record per task:
  - T-id;
  - reviewer identity;
  - human or fresh-context Agent;
  - Verify command and observed result;
  - Covers, Files, and RED→GREEN findings;
  - PASS or FAIL;
  - correction and re-review evidence after FAIL.
- [ ] Keep Progress Log as the record of commits made only after PASS.
- [ ] Add Self-Review checks that every T has a verdict, the verdict predates its commit, and every FAIL has a later PASS or remains incomplete.
- [ ] Keep model escalation history optional and specific to `dev-run`; manual work must not invent model history.

### Plugin changes

- [ ] Make the live `dev-flow/SKILL.md` state that manual work and `dev-run` share the same T acceptance seam.
- [ ] Keep `dev-run`'s existing fresh reviewer behavior.
- [ ] Change `dev-run/SKILL.md` to reference the README/6-notes core rule instead of owning a second copy of the policy.
- [ ] Record `dev-run` reviewer results in the new `T Review Log`.
- [ ] Preserve `review PASS → commit`; implementers still do not commit before review.

### Files intentionally unchanged

- `_templates/5-tasks.md`: Covers, Files, and Verify already provide the required review inputs.
- `_templates/7-review.md`: G3 already covers independent feature-level review, coverage, regression, and observable evidence.

---

## 2.5. Harden the Stage 6 execution guard without weakening scope control

### Intent

Keep the original protection—contract immutability, declared Files scope, shell-bypass detection, dirty-user-work protection, and fail-closed state—but remove ambient operating-system noise and move preventable failures to `start`.

The intended interface is:

```text
classify ambient metadata
→ validate every T and canonicalize scope
→ reject meaningful scope-external dirty state before arming
→ during execution, block only real contract/scope violations
```

### Files

- Modify: `README.md`
- Modify: `_templates/5-tasks.md`
- Modify: `guide-quickstart.html`
- Modify: `dev-setup-record.html` only if its guard behavior summary requires synchronization.
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/devflow-lib.py`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/_exec_impl.py`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/_postbash_impl.py`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/_guard_impl.py` only if it must consume the shared canonical-path decision.
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/selftest.sh`

### Ambient metadata policy

- [ ] Add one shared predicate in `devflow-lib.py`; start and post-Bash adapters must use the same policy.
- [ ] Treat these as ambient metadata rather than feature changes:
  - `.DS_Store` at any depth;
  - AppleDouble files whose basename starts with `._`;
  - `Thumbs.db` at any depth;
  - existing `__pycache__/` and `*.pyc` exclusions.
- [ ] Ambient metadata must not enter the baseline, trigger scope violations, require `allow`, or produce D-n records.
- [ ] Do not use `.gitignore` as the policy interface: post-Bash intentionally scans ignored paths to prevent source changes from being hidden.
- [ ] Do not add broad cache/build-directory exclusions in this batch; every ignored class must be an unambiguous environment artifact.

### Clean-start policy

- [ ] After excluding ambient metadata and guard-owned state, reject `start` when any meaningful scope-external tracked, untracked, or ignored dirty path exists.
- [ ] The rejection must list the first paths and tell the caller to commit, restore, or use a clean worktree before retrying.
- [ ] Continue to permit dirty paths already inside the declared scope.
- [ ] Do not silently baseline meaningful scope-external dirty paths and defer the failure until a later Bash command.
- [ ] Preserve fail-closed behavior for a missing/corrupt armed state and preserve post-Bash detection of new scope-external changes.

### Per-task validation and canonical paths

- [ ] Parse every `## T-n` block at `start`; each task must contain non-empty Covers, Files, Verify, and Blocked-by fields.
- [ ] Reject the whole start when any task is incomplete; report the exact T-id and missing field.
- [ ] Define Files as Git-repository-root-relative paths.
- [ ] Normalize `./src/a.py` to `src/a.py` before storing scope.
- [ ] Reject absolute paths, `..` traversal, empty normalized paths, and ambiguous repository-root entries.
- [ ] Permit planned new files that do not exist yet; existence is not a start requirement.
- [ ] Ensure guard diagnostics print the canonical repo-root-relative path and explicitly remind callers that `internal/...` and `backend-go/internal/...` are different scopes in a monorepo.
- [ ] Keep undeclared implementation and test files blocked. A genuinely omitted TDD test file remains L1 when R/S do not change: update 5-tasks, use `allow` or restart, and record D-n.

### Documentation changes

- [ ] State in `_templates/5-tasks.md` that every T requires Covers, Files, Verify, and Blocked-by and that Files are repo-root-relative.
- [ ] Update README §5 guard behavior from “warn and baseline scope-external dirty files” to the clean-start rule.
- [ ] Update the quickstart scope FAQ with the canonical monorepo-path example.
- [ ] Keep the distinction explicit: ambient metadata is ignored; meaningful scope-external changes remain blocked.

### Regression tests

- [ ] Pre-existing `.DS_Store` modified after start does not block post-Bash.
- [ ] Newly created nested `.DS_Store`, `._*`, and `Thumbs.db` do not block post-Bash.
- [ ] A meaningful scope-external dirty file present before start rejects start.
- [ ] A new meaningful scope-external file created after start still blocks post-Bash.
- [ ] A T missing Covers, Files, Verify, or Blocked-by rejects start with its T-id.
- [ ] Absolute paths and `..` paths reject start.
- [ ] `./src/a.py` is stored and matched as `src/a.py`.
- [ ] A monorepo edit using `backend-go/internal/x_test.go` remains blocked when only `internal/x_test.go` was declared, and the diagnostic explains repo-root-relative scope.
- [ ] Existing contract hashing, `allow`, sentinel fail-closed, upstream-read blocking, and shell-bypass cases remain green.
- [ ] Self-test headings and summaries derive their total dynamically; no fixed `20` or `33` count remains.

---

## 3. Repair the Fast lane scope contradiction

### Files

- Modify: `README.md`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/skills/dev-flow/SKILL.md`
- Modify: active quickstart and flow guides wherever the Fast lane artifact list appears.

### Changes

- [ ] Change the Fast lane artifact sequence from `4 → 6 → 7` to `4 → 5 mini → 6 → 7`.
- [ ] Permit a one-task `5-tasks.md`, but require Covers, Files, Verify, and Blocked-by.
- [ ] Keep Stages 1–3 omitted for qualifying Fast lane work.
- [ ] Use the same `5-tasks.md` template rather than creating a second Fast-lane template.
- [ ] Confirm `devflow-exec.sh start <slug>` can parse scope for Fast lane work.
- [ ] Confirm Fast lane tasks can pass the new T acceptance seam.

---

## 4. Align reviewer fallback semantics

### Files

- Modify: `_templates/2-decision.md`
- Modify: `_templates/4-spec.md` if its fallback order is not explicit.
- Modify: `_templates/7-review.md`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/_gate_consistency_impl.py`
- Modify: `/Users/asheng/.claude/plugins/local/dev-flow/hooks/selftest.sh`

### Changes

- [ ] Make G1/G2/G3 reviewer selection consistent with README §7:
  1. eligible human reviewer;
  2. fresh-context reviewer Agent;
  3. owner self-review only as a recorded last resort.
- [ ] Extend consistency validation beyond selected gate tokens to reviewer-selection semantics.
- [ ] Include “current S all green” in the G3 consistency conditions.
- [ ] Add fixtures that catch negated or semantically reversed sentences containing the correct tokens.
- [ ] Change the self-test heading from “20 cases” to the actual 33 cases, or derive it from the final total.

---

## 5. Refresh the canonical example

### Files

- Modify: `example/contract-expiry-reminder/1-discussion.md`
- Modify: `example/contract-expiry-reminder/4-spec.md`
- Modify: `example/contract-expiry-reminder/5-tasks.md`
- Modify: `example/contract-expiry-reminder/6-implementation-notes.md`
- Modify: `example/contract-expiry-reminder/7-review.md`
- Regenerate: related `example/contract-expiry-reminder/*.html`

### Changes

- [ ] Add “where to observe / expected observation / test data” to every acceptance sketch in `1-discussion.md`.
- [ ] Add an observation field to S-1, S-2, and S-3 in `4-spec.md`.
- [ ] Add the e2e test file to T-4 Files in `5-tasks.md`.
- [ ] Make the task Files union match the six changed files claimed in `6-implementation-notes.md`.
- [ ] Add independent T review evidence for every task in `6-implementation-notes.md`.
- [ ] Add per-scenario observable evidence to `7-review.md`.
- [ ] Resolve the final status rule consistently:
  - either all feature artifacts become `shipped` at Exit;
  - or README/template rules explicitly permit upstream artifacts to remain `approved` while only Stage 7 becomes `shipped`.
- [ ] Regenerate HTML twins exclusively from the corrected Markdown.

---

## 6. Verification and independent acceptance

- [ ] Run the live guard suite:

```bash
/Users/asheng/.claude/plugins/local/dev-flow/hooks/selftest.sh
```

Expected: all dynamically counted cases pass, with heading and summary totals matching.

- [ ] Run gate consistency:

```bash
/Users/asheng/.claude/plugins/local/dev-flow/hooks/gate-consistency.sh
```

Expected: all checks pass, including the newly covered reviewer semantics.

- [ ] Search active files for official harness dependency:

```bash
git grep -n -i harness -- README.md guide-dev-flow.html guide-quickstart.html dev-setup-record.html
rg -n -i harness /Users/asheng/.claude/plugins/local/dev-flow/skills
```

Expected: no method-level dependency, engine routing, or conversion instruction. Historical archives are excluded.

- [ ] Validate the canonical example against current templates:
  - every S has an observation;
  - every T has Covers, Files, Verify, and review verdict;
  - Files scope matches the implementation record;
  - G3 has per-S observable evidence;
  - final statuses follow one documented rule.
- [ ] Ask a fresh-context reviewer Agent to inspect the final diff without author conclusions.
- [ ] Confirm the reviewer does not call or depend on harness.
- [ ] Confirm `git status --short` contains no accidental `.serena/`, generated cache, or unrelated changes.

---

## Recommended Delivery Sequence

### Batch 1: Method consistency

- Remove the harness dependency.
- Rewrite §13/§14.
- Repair Fast lane by restoring a mini Stage 5.

### Batch 2: Stage 6 review seam

- Add the shared T acceptance rule.
- Update `6-implementation-notes`.
- Align `dev-flow` and `dev-run` adapters.

### Batch 2.5: Execution guard hardening

- Ignore only unambiguous ambient metadata.
- Enforce clean-start for meaningful scope-external dirty state.
- Validate every T and canonicalize repo-root-relative Files before arming.
- Add regression coverage without weakening real scope violations.

### Batch 3: Derived content and checks

- Align reviewer fallback semantics.
- Strengthen gate consistency tests.
- Refresh the canonical example and HTML guides.

Each batch should receive its own fresh-context review and remain independently revertible.

---

## Deferred Architecture Improvements

These are valuable but should not be mixed into the methodology-correction batches:

1. Build a Workflow Artifact module for frontmatter, stage state, R/S/T/D/F, scope, and gate validation.
2. Move the live plugin source into this repository under one release manifest.
3. Deepen `devflow-lib.py` into an Execution Policy module shared by all hook adapters.
4. Build an HTML twin renderer with escaping, diff truncation, and snapshot fixtures.
5. Build a deterministic Full/Fast routing module after collecting real misrouting examples.
