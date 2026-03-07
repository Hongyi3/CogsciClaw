---
name: hed-annotator
description: Map task events to HED strings and emit validation outputs for event semantics.
version: 0.1.0
status: scaffold
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
  - eeg
  - meg
standards:
  - HED
  - BIDS
trigger_keywords:
  - hed
  - event annotation
  - events.tsv
  - events.json
dependencies:
  python: ">=3.11"
  packages: []
---

# hed-annotator

## Why this exists

Event semantics are often described informally, which blocks machine-actionable reuse. This skill should translate structured task and event information into explicit HED annotations with validation output.

## Supported use cases

- mapping known event structures to HED strings
- generation of event metadata files
- validation-ready annotation outputs

## Unsupported or deferred cases

- ontology inference from sparse or ambiguous event labels without review
- silent generation of unverifiable HED tags

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| event table | TSV / CSV | yes | event onsets and labels |
| event mapping spec | YAML / JSON | yes | semantic mapping rules |

## Workflow

1. Read event data and mapping rules.
2. Generate HED strings and event metadata fields.
3. Emit annotated event files.
4. Run HED validation and capture issues.

## Validation

- HED validation required
- if used inside a BIDS dataset, capture relationship to BIDS validation

## Demo mode

Use a small event table from the Flanker or oddball example.

## Outputs

```text
output/
├── events/
│   ├── events.tsv
│   └── events.json
├── validation/
│   └── hed-validation.json
└── report.md
```

## Safety

- ambiguous event semantics must be surfaced, not hidden
- do not generate unsupported ontology claims

## Integration notes

- upstream: task generators or BIDS curation
- downstream: `eeg-meg-pipeline`, `repro-bundle`

## Citations

- cite HED and any task/event-specific conventions used

