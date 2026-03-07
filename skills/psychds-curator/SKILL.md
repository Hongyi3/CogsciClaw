---
name: psychds-curator
description: Curate the deterministic Flanker demo trial tables into a Psych-DS-aligned dataset with optional official validator output.
version: 0.1.0
status: supported-demo
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
standards:
  - Psych-DS
trigger_keywords:
  - psych-ds
  - behavioral dataset
  - data curation
dependencies:
  python: ">=3.11"
  packages:
    - PyYAML
    - jsonschema
---

# psychds-curator

## Why this exists

Behavioral datasets are often shareable in principle but not in a form that is easy to validate, understand, or reuse. This skill should convert stable task outputs into a documented, validator-friendly behavioral dataset layout.

## Supported use cases

- deterministic trial-level Flanker demo data generated in this repository
- participant/session filename normalization using Psych-DS keyword formatting
- global and file-level JSON-LD metadata for the curated demo dataset
- optional invocation of the official Psych-DS validator via the `validate` CLI

## Unsupported or deferred cases

- arbitrary empirical behavioral datasets
- ingestion of browser-run data files from outside this repository
- claims of full interoperability without validator output
- arbitrary proprietary binary formats without adapters
- downstream modeling, HED annotation, or preregistration packaging

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| synthetic trial tables | CSV | yes | deterministic demo trial tables generated from the Flanker schedule |
| study metadata | JSON / YAML | yes | title, study-spec hash, and curation notes |
| validator mode | CLI flag | no | `auto`, `always`, or `never` for the official Psych-DS validator |

## Workflow

1. Parse the deterministic Flanker demo trial tables and study metadata.
2. Write a Psych-DS-aligned dataset root with `dataset_description.json` and `data/*_data.csv` files.
3. Write matching sidecar metadata for each curated data file.
4. Invoke the official Psych-DS validator when available, or emit a structured `not_run` artifact when it is unavailable by design.

## Validation

- official `validate <dataset_dir> --json` output when the validator is available
- column-to-metadata consistency via `variableMeasured`
- explicit `not_run` status when official validation is unavailable in local environments

## Demo mode

Run:

```bash
python3 scripts/run_flanker_behavioral_slice.py \
  --study-spec examples/flanker-behavioral/study_spec.yaml \
  --output-dir output/flanker-behavioral \
  --validate-psychds auto
```

## Outputs

```text
output/
├── psychds/
│   ├── dataset_description.json
│   └── data/
└── report/
    └── validation/
        └── psychds-validator.json
```

## Safety

- demo data must remain explicitly synthetic
- do not represent curated demo rows as empirical participant observations
- treat future empirical participant metadata as potentially sensitive

## Integration notes

- upstream: `task-jspsych`
- downstream: `repro-bundle`

## Citations

- cite Psych-DS in documentation and outputs
- cite the official `psychds-validator` when reporting validator-backed results
