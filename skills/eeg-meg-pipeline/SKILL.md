---
name: eeg-meg-pipeline
description: Orchestrate EEG/MEG intake and preprocessing with MNE-BIDS and MNE-Python.
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
  - MNE-BIDS
  - MNE
  - HED
trigger_keywords:
  - eeg
  - meg
  - erp
  - mne
  - mne-bids
  - oddball
dependencies:
  python: ">=3.11"
  packages: []
---

# eeg-meg-pipeline

## Why this exists

EEG/MEG workflows often break because intake, event annotation, and preprocessing live in disconnected scripts. This skill should compose BIDS intake, event semantics, and MNE-based preprocessing with transparent QC and reporting.

## Supported use cases

- standard EEG/MEG preprocessing pathways that can be documented clearly
- event-related analysis scaffolding
- QC summaries and methods metadata

## Unsupported or deferred cases

- all possible acquisition systems and preprocessing philosophies
- unsupported source modeling or inverse pipelines without explicit implementation

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| BIDS-curated dataset | directory | yes | BIDS-compatible EEG/MEG dataset |
| preprocessing config | YAML / JSON | no | pipeline parameters |

## Workflow

1. Read a BIDS-curated dataset.
2. Confirm event metadata and validation readiness.
3. Run documented MNE-based preprocessing steps.
4. Emit QC artifacts, analysis-ready outputs, and methods metadata.

## Validation

- BIDS validation record should be available
- event metadata consistency checks
- QC metrics must be emitted and attached

## Demo mode

Use a small oddball-style public or synthetic demo dataset.

## Outputs

```text
output/
├── derivatives/
│   ├── qc/
│   ├── cleaned/
│   └── epochs/
├── figures/
└── report.md
```

## Safety

- preprocessing choices must be explicit
- unsupported steps must be surfaced clearly

## Integration notes

- upstream: `bids-curator`, `hed-annotator`
- downstream: `repro-bundle`

## Citations

- cite MNE-BIDS, MNE, BIDS, and reporting guidance used

