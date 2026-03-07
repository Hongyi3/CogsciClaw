# Contributing

Thank you for helping build standards-first cognitive-science infrastructure.

## Before you open a pull request

Read, in order:

1. `VISION.md`
2. `METHODS_POLICY.md`
3. `AGENTS.md`
4. the target skill’s `SKILL.md`
5. `ROADMAP.md`

## Contribution lanes

We welcome contributions in:

- skills
- tests
- validators / adapters
- examples
- documentation
- benchmark curation
- release / reproducibility tooling

## Adding a skill

1. Copy `templates/SKILL-TEMPLATE.md`
2. Create `skills/<skill-slug>/SKILL.md`
3. Add metadata to `skills/catalog.json`
4. Run `python scripts/render_skill_catalog.py`
5. Add demo data or a deterministic demo pathway
6. Add tests
7. Document supported and unsupported cases
8. Document safety and validation

## Contribution requirements for a supported skill

A supported skill must include:

- `SKILL.md`
- demo mode
- at least one test
- output contract
- citations
- validation path where relevant
- failure notes
- integration notes

## Commands

```bash
python scripts/render_skill_catalog.py
pytest -q
```

## Pull request expectations

Your PR should explain:

- what changed
- why it changed
- whether the change affects scientific behavior
- what tests were run
- whether any catalog / docs were regenerated

## Review priorities

Maintainers review for:

- standards alignment
- scientific correctness
- reproducibility
- clarity
- safety
- public-doc drift

## For coding agents

If you are a coding agent:

- follow `AGENTS.md`
- create or update `PLANS.md` for multi-step work
- do not claim a standard is supported unless a validation path exists
- do not modify public skill listings without updating generated docs

