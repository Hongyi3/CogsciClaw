---
name: example-skill
description: Explain exactly when this skill should and should not trigger.
version: 0.1.0
status: scaffold
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
standards:
  - Psych-DS
trigger_keywords:
  - example
dependencies:
  python: ">=3.11"
  packages: []
---

# example-skill

## Why this exists

Describe the scientific or workflow problem this skill solves.

## Supported use cases

- use case 1
- use case 2

## Unsupported or high-risk cases

- unsupported case 1
- unsupported case 2

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| study spec | YAML / JSON | yes | structured specification |
| raw data | CSV / TSV / modality-specific | no | optional depending on the skill |

## Workflow

1. Parse the study specification or inputs.
2. Validate assumptions and required fields.
3. Run the core scientific workflow.
4. Emit machine-readable outputs.
5. Emit validator outputs where applicable.
6. Emit provenance and methods metadata.

## Validation

List validators, schema checks, or diagnostics used by this skill.

## Demo mode

Describe a deterministic demo pathway that runs without private data.

## Outputs

```text
output/
├── report.md
├── results.json
└── logs/
```

## Safety

- local-first by default
- no destructive actions without explicit permission
- no unverifiable scientific claims

## Integration notes

List likely upstream and downstream skills.

## Citations

List the methods papers, databases, or standards that justify this skill.

