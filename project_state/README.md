# Project State

This folder stores persistent milestone governance for the repository.

Use it so future Codex runs can determine the current phase, current milestone, next milestone, and project maturity from files instead of conversational memory.

## Files

- `CURRENT_STAGE.md`: source of truth for the current phase, project maturity, active milestone, status, last completed milestone, blockers, and evidence.
- `NEXT_MILESTONE.md`: executable brief for the immediate next milestone only.
- `MILESTONE_HISTORY.md`: append-only record of milestones advanced honestly.
- `BACKLOG.md`: ordered milestone queue, dependency notes, and sequencing rationale.

## Operating rules

1. Before any multi-file, scientific, architectural, or milestone-scale task, read `CURRENT_STAGE.md` and `NEXT_MILESTONE.md`.
2. Treat `PLANS.md` as run-specific only. Do not use it as persistent project state.
3. When a milestone is completed, update `CURRENT_STAGE.md`, `MILESTONE_HISTORY.md`, `NEXT_MILESTONE.md`, and `BACKLOG.md` together.
4. If a milestone is blocked, record the blocker in `CURRENT_STAGE.md` and keep the same milestone in `NEXT_MILESTONE.md` until the state files are honestly rescoped.
5. Never mark a milestone complete unless implementation, tests, docs, and artifacts justify the status.
