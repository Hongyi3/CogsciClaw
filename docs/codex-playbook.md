# Codex playbook

This repository is structured so Codex can contribute effectively.

## First-run prompt

Use a prompt like:

```text
Read AGENTS.md, VISION.md, METHODS_POLICY.md, MASTER_PLAN.md, and ROADMAP.md.
Then summarize the repository goals, identify the first implementation milestone,
and propose a file-level execution plan without changing code yet.
```

## First implementation prompt

```text
Read AGENTS.md and the target SKILL.md.
Implement the smallest end-to-end vertical slice for examples/flanker-behavioral/study_spec.yaml.
Do not add unsupported features.
Update tests and generated skill docs before finishing.
```

## Review prompt

```text
Review this PR for:
- standards overclaims
- missing validation paths
- missing diagnostics
- doc drift against skills/catalog.json
- PII logging or unsafe defaults
Treat any of those as high priority.
```

## Long-horizon prompt

```text
Read AGENTS.md and PLANS.md.
Create or update the execution plan, then implement only the first milestone.
Keep changes narrow and leave the repo in a runnable state.
```

## GitHub workflow usage

The included Codex GitHub Action can be used for:

- PR review
- release readiness checks
- repeated documentation audits

## Rules for best results

- keep tasks narrow
- point Codex to exact files
- ask for a definition of done
- use deterministic examples
- ask Codex to regenerate derived docs

