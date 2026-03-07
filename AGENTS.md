# AGENTS.md

## Prime directive

This repository is for **standards-first cognitive-science infrastructure**.

Do not invent methods.  
Do not overclaim support.  
Do not treat placeholder scaffolding as finished capability.

Every material scientific claim must trace to code, runtime metadata, validator output, or a cited source.

## Required reading order

Before changing anything substantial, read:

1. `VISION.md`
2. `METHODS_POLICY.md`
3. `MASTER_PLAN.md`
4. `ROADMAP.md`
5. `docs/standards-stack.md`
6. the target `SKILL.md`
7. `THREAT_MODEL.md` if the work touches execution, files, network, or secrets

## Next Milestone

Before starting any multi-file, scientific, architectural, or milestone-scale task, read:

- `project_state/CURRENT_STAGE.md`
- `project_state/NEXT_MILESTONE.md`

Treat `project_state/CURRENT_STAGE.md` as the source of truth for the current phase, project maturity, active milestone, status, last completed milestone, blockers, and status evidence.

Treat `project_state/NEXT_MILESTONE.md` as the executable brief for the immediate next milestone only.

When a milestone is completed, update `project_state/CURRENT_STAGE.md`, `project_state/MILESTONE_HISTORY.md`, and `project_state/NEXT_MILESTONE.md` together.

If work needs to go outside the declared next milestone, update the project-state files honestly first and explain why.

Never mark a milestone complete unless implementation, tests, docs, and artifacts justify the status.

## How to work in this repo

### 1. Preserve the source of truth

`skills/catalog.json` is the source of truth for public skill listings.

If you change skill metadata:

```bash
python3 scripts/render_skill_catalog.py
```

Do not edit generated listings by hand.

### 2. Use planning documents for multi-step work

If the task will touch multiple files, take longer than a quick fix, or change scientific behavior:

- create or update `PLANS.md`
- write a short execution plan
- keep it current as work changes

### 3. Treat each skill as a scientific contract

Every supported skill must include:

- purpose
- supported / unsupported cases
- deterministic demo
- validation path
- outputs
- safety notes
- citations
- integration notes

### 4. Prefer narrow, complete vertical slices

When choosing between breadth and completeness, prefer completeness.

### 5. Guard scientific meaning

Treat the following as **P1** review issues:

- missing validator step for a claimed standard
- generated methods text not derived from runtime metadata
- undocumented scientific assumption
- missing diagnostics for Bayesian modeling
- doc drift between catalog and public docs
- silent behavior changes in study timing, event labeling, or model structure

### 6. Push completed changes

If Codex changes any repo-tracked file for a task, the task is not complete until the task's changes are verified, committed, and pushed to the GitHub remote for the current branch.

Push once per completed task, not after every intermediate edit.

Do not include unrelated local changes.

Never force-push or rewrite history unless explicitly requested.

If authentication, network, branch protection, or unrelated dirty-worktree state prevents a safe push, report the blocker explicitly instead of claiming completion.

## Review guidelines

When reviewing code or docs, check for:

- standards alignment
- reproducibility bundle completeness
- absence of PII in logs or examples
- deterministic demo behavior
- catalog / generated-doc synchronization
- clear supported vs experimental labeling

## Commands

```bash
python3 scripts/render_skill_catalog.py
pytest -q
```

## Style rules

- prefer explicitness over cleverness
- keep public docs precise and non-marketing
- keep examples deterministic and public
- do not hardcode private paths
- do not log sensitive identifiers
- do not add network-dependent demo steps without documenting them clearly

## Files to update when capability changes

At minimum, check whether you must update:

- target `skills/*/SKILL.md`
- `skills/catalog.json`
- generated skill table
- `README.md`
- `MASTER_PLAN.md` or `ROADMAP.md`
- examples and tests

## Definition of done

A change is not done until:

- tests pass
- generated docs are current
- new or changed scientific behavior is documented
- supported/unsupported cases are explicit
- any new public claim is backed by a real implementation path
