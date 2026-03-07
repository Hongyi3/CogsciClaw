---
name: repro-bundle
description: Assemble the deterministic Flanker demo reproducibility bundle with manifest, methods, commands, environment, checksums, and validation artifacts.
version: 0.1.0
status: supported-demo
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
  - eeg
  - meg
  - fmri
  - questionnaire
  - neurophysiology
standards:
  - JSON Schema
trigger_keywords:
  - reproducibility bundle
  - report bundle
  - ro-crate
  - provenance
dependencies:
  python: ">=3.11"
  packages:
    - PyYAML
    - jsonschema
---

# repro-bundle

## Why this exists

A workflow is not reproducible merely because it ran once. This skill should convert upstream outputs into a complete, inspectable, archivally useful bundle.

## Supported use cases

- machine-readable report bundle manifest aligned to `schemas/report-bundle.schema.json`
- runtime-derived methods text for the canonical Flanker demo slice
- command capture, environment capture, checksum generation, and validation artifact collection
- machine-readable run manifest for the implemented demo slice

## Unsupported or deferred cases

- claims of perfect reproducibility when upstream steps are stochastic and not controlled
- RO-Crate packaging
- PROV packaging
- preregistration exports
- figures and tables
- multi-skill assembly beyond the canonical Flanker demo slice

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| task outputs | directory | yes | jsPsych package and deterministic task metadata |
| Psych-DS outputs | directory | yes | curated demo dataset and validator output |
| run metadata | JSON / YAML | yes | commands, versions, assumptions, validation status |

## Workflow

1. Collect the generated task, metadata, and Psych-DS demo outputs.
2. Build a machine-readable report bundle manifest and a machine-readable run manifest.
3. Emit runtime-derived `report.md`, `methods.md`, `commands.sh`, `environment.lock.yml`, and `checksums.sha256`.
4. Record explicit unsupported capabilities instead of silently omitting them.

## Validation

- bundle completeness checks
- checksum generation
- schema check against `schemas/report-bundle.schema.json`

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
└── report/
    ├── report_bundle.json
    ├── report.md
    ├── methods.md
    ├── commands.sh
    ├── environment.lock.yml
    ├── checksums.sha256
    ├── provenance/
    │   └── run_manifest.json
    └── validation/
```

## Safety

- redact secrets and sensitive paths
- do not package private raw data into public demo bundles by default
- keep synthetic demo data explicitly labeled as synthetic in bundle outputs

## Integration notes

- downstream of the implemented Flanker `task-jspsych` and `psychds-curator` demo path
- used by release and benchmark workflows for the behavioral slice

## Citations

- cite the report bundle schema in this repository
- note explicitly that RO-Crate and PROV packaging remain deferred in this milestone
