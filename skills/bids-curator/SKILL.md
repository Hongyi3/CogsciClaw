---
name: bids-curator
description: Emit the canonical auditory oddball EEG BIDS-aligned intake tree with truthful local validator status artifacts.
version: 0.1.0
status: supported-demo
tags:
  - cognitive-science
  - reproducibility
  - bids
modality:
  - eeg
standards:
  - BIDS
trigger_keywords:
  - bids
  - eeg bids
  - oddball
  - dataset_description
dependencies:
  python: ">=3.11"
  packages: []
---

# bids-curator

## Purpose

Prepare a deterministic, reviewable BIDS-aligned intake tree for the checked-in auditory oddball EEG demo without inventing empirical acquisition metadata or claiming preprocessing support.

## Supported use cases

- the canonical study spec at `examples/eeg-oddball/study_spec.yaml`
- local emission of `dataset_description.json`, `README.md`, participant summary files, and placeholder participant metadata under `bids-intake/`
- truthful local `bids-validator` execution when a preinstalled `bids-validator` binary is available
- structured `not_run` validator artifacts when the validator binary is unavailable or disabled

## Unsupported use cases

- arbitrary EEG or MEG study specifications
- empirical EEG conversion, raw file import, or signal processing
- `events.tsv`, `channels.tsv`, `electrodes.tsv`, or HED generation from incomplete inputs
- MNE-BIDS ingestion, MNE preprocessing, ERP analysis, QC dashboards, or participant-level interpretation
- claims of BIDS compliance without a real validator result

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| study spec | YAML | yes | must match the checked-in canonical oddball demo profile |
| validator mode | CLI flag | no | `auto`, `always`, or `never` |

## Workflow

1. Validate the study spec against the schema and the supported oddball profile.
2. Emit a BIDS-aligned intake tree with explicit placeholder-only labeling.
3. Run `bids-validator` only if a local binary is already available, otherwise emit a truthful `not_run` artifact.
4. Surface the intake contract, validator status, preregistration export, and provenance references in the reproducibility bundle.

## Outputs

```text
output/
├── bids-intake/
│   ├── dataset_description.json
│   ├── README.md
│   ├── participants.tsv
│   ├── participants.json
│   ├── intake_manifest.json
│   └── sub-placeholder*/eeg/*_intake-placeholder.json
└── report/
    ├── report_bundle.json
    ├── report.md
    ├── methods.md
    ├── preregistration/preregistration.json
    ├── provenance/
    └── validation/bids-validator.json
```

## Validation

- study-spec schema validation is always emitted
- BIDS validation is recorded as `passed`, `failed`, or `not_run`
- `not_run` is the truthful default when no local `bids-validator` binary is present

## Demo mode

Run the canonical slice with:

```bash
python3 scripts/run_oddball_bids_slice.py \
  --study-spec examples/eeg-oddball/study_spec.yaml \
  --output-dir output/eeg-oddball-bids-intake \
  --validate-bids auto
```

Use a Python >=3.11 environment. The demo emits placeholder-only metadata, not empirical EEG data.

## Safety

- do not treat placeholder participant artifacts as empirical recordings
- do not log participant identifiers beyond deterministic placeholder IDs
- do not fetch validator code or other tooling over the network
- keep privacy review explicit because the canonical oddball spec marks `contains_sensitive_data: true`

## Citations

- BIDS specification
- BIDS Validator documentation

## Integration notes

- upstream input: `examples/eeg-oddball/study_spec.yaml`
- downstream consumers: `repro-bundle`, later `eeg-meg-pipeline`
- current support boundary: intake metadata only; no preprocessing or analysis contract
