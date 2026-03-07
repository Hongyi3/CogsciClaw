---
name: bids-curator
description: Prepare BIDS-compatible dataset structure and metadata for EEG/MEG-focused workflows.
version: 0.1.0
status: scaffold
tags:
  - cognitive-science
  - reproducibility
modality:
  - eeg
  - meg
standards:
  - BIDS
trigger_keywords:
  - bids
  - eeg bids
  - meg bids
  - dataset_description
dependencies:
  python: ">=3.11"
  packages: []
---

# bids-curator

## Why this exists

EEG/MEG workflows become brittle when file organization and metadata are inconsistent. This skill should prepare a BIDS-aligned intake layer so downstream pipelines can rely on stable structure and validation.

## Supported use cases

- EEG/MEG-focused BIDS intake
- dataset metadata and sidecar scaffolding
- validator-oriented file organization

## Unsupported or deferred cases

- unsupported modality-specific edge cases without explicit implementation
- claims of preprocessing or analysis on its own

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| raw modality data | format-specific | yes | EEG/MEG source data |
| acquisition metadata | JSON / TSV / notes | yes | subject/session/task metadata |

## Workflow

1. Parse intake metadata.
2. Organize files into BIDS-compatible layout.
3. Generate required metadata sidecars and dataset description fields.
4. Emit validator outputs or readiness reports.

## Validation

- BIDS validator path required before claiming support

## Demo mode

Provide a minimal BIDS-ready demo tree or synthetic metadata pathway for CI.

## Outputs

```text
output/
├── bids_dataset/
│   ├── dataset_description.json
│   ├── participants.tsv
│   └── sub-*/
├── validation/
│   └── bids-validator.json
└── report.md
```

## Safety

- never claim BIDS compliance without a validator step
- treat source acquisition metadata as sensitive

## Integration notes

- downstream: `hed-annotator`, `eeg-meg-pipeline`, `repro-bundle`

## Citations

- cite BIDS and any modality-specific BIDS references used

