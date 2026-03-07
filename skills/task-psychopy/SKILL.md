---
name: task-psychopy
description: Generate lab-based or hybrid PsychoPy task packages from a structured study specification.
version: 0.1.0
status: scaffold
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
standards:
  - Psych-DS
  - HED
  - Cognitive Atlas
trigger_keywords:
  - psychopy
  - builder
  - lab experiment
  - hybrid task
dependencies:
  python: ">=3.11"
  packages: []
---

# task-psychopy

## Why this exists

Many labs need task packages that can run under tighter timing and hardware constraints than typical browser deployments. This skill should emit PsychoPy-friendly scaffolds while keeping the surrounding metadata interoperable.

## Supported use cases

- Builder-friendly task scaffolds
- common RT / accuracy paradigms
- export of metadata compatible with downstream curation

## Unsupported or deferred cases

- unsupported hardware drivers in generic demos
- custom lab device integration without explicit adapters
- hidden auto-conversion claims for all PsychoPy ↔ web cases

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| study spec | YAML / JSON | yes | structured task specification |
| stimulus manifest | CSV / TSV / JSON | no | optional stimulus table |

## Workflow

1. Parse the study specification.
2. Generate PsychoPy task assets and configuration.
3. Emit event and data-field templates.
4. Package outputs for downstream curation and reporting.

## Validation

- schema validation for the study spec
- output contract checks for emitted metadata fields

## Demo mode

Provide a minimal local demo task that does not require lab-specific hardware.

## Outputs

```text
output/
├── task/
│   ├── task.py
│   ├── task.psyexp
│   └── assets/
├── metadata/
│   ├── trial_schema.json
│   └── data_dictionary.json
└── report.md
```

## Safety

- no implicit claims about timing quality without empirical validation
- make unsupported device paths explicit

## Integration notes

- downstream: `psychds-curator`, `hed-annotator`, `repro-bundle`

## Citations

- cite PsychoPy and any task-specific methods used

