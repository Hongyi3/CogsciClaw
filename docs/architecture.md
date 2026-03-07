# Architecture

## Architectural summary

This project adapts the ClawBio pattern to cognitive science:

- modular skills centered on `SKILL.md`
- an orchestrator for routing and assembly
- local-first execution
- reproducibility bundles
- agent-facing repository metadata

## High-level flow

```text
request or study spec
        │
        ▼
cogsci orchestrator
        │
        ├── task generation
        ├── data curation
        ├── event annotation
        ├── modeling
        └── reproducibility assembly
                │
                ▼
standards + validators
                │
                ▼
report / bundle / preregistration / provenance
```

## Key components

### 1. Study specification layer

A structured study spec captures:

- research question
- modality
- task structure
- sampling plan
- outputs requested
- preregistration and ethics flags

This is the bridge between natural-language intent and deterministic workflow execution.

### 2. Skill layer

Each skill encapsulates one scientific job.

Examples:

- `task-jspsych`
- `psychds-curator`
- `hed-annotator`
- `ddm-bayes`
- `eeg-meg-pipeline`

### 3. Standards layer

This is where the project earns trust.

The repo should prefer community standards for:

- behavioral organization
- event semantics
- neuroimaging structure
- questionnaires / assessments
- provenance packaging
- software citation

### 4. Output layer

Every successful run should emit a research object bundle, not just terminal text.

## Agent-facing metadata

Root-level agent docs make the repo legible to coding agents:

- `AGENTS.md`
- `llms.txt`
- `skills/catalog.json`

## Public-doc drift prevention

Public capability listings must be generated from `skills/catalog.json`.

The included script:

```bash
python scripts/render_skill_catalog.py
```

updates generated skill tables and README sections.

