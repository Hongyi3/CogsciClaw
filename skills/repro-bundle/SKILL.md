---
name: repro-bundle
description: Assemble the deterministic Flanker demo reproducibility bundle with preregistration export, RO-Crate / PROV packaging, manifest, methods, commands, environment, checksums, and validation artifacts.
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
  - RO-Crate
  - PROV
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
- deterministic preregistration export for the canonical Flanker demo slice
- machine-readable RO-Crate and PROV packaging for the emitted bundle

## Unsupported or deferred cases

- claims of perfect reproducibility when upstream steps are stochastic and not controlled
- registry or API preregistration submission
- validator-backed RO-Crate / PROV conformance claims
- figures and tables
- multi-skill assembly beyond the canonical Flanker demo slice

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| task outputs | directory | yes | jsPsych package and deterministic task metadata |
| Psych-DS outputs | directory | yes | curated demo dataset and validator output |
| run metadata | JSON / YAML | yes | commands, versions, assumptions, validation status |

## Workflow

1. Collect the generated task, metadata, model, and Psych-DS demo outputs.
2. Build a machine-readable report bundle manifest, a machine-readable run manifest, and a deterministic preregistration export.
3. Emit runtime-derived `report.md`, `methods.md`, `commands.sh`, `environment.lock.yml`, `checksums.sha256`, and machine-readable RO-Crate / PROV metadata.
4. Record explicit unsupported capabilities and required human review points instead of silently omitting them.

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
  --validate-psychds auto \
  --validate-hed auto \
  --fit-bayes auto \
  --fit-ddm auto
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
    ├── preregistration/
    │   └── preregistration.json
    ├── provenance/
    │   ├── ro-crate-metadata.json
    │   ├── prov.jsonld
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
- cite the RO-Crate and PROV references used for the emitted machine-readable packaging
- note explicitly that validator-backed RO-Crate / PROV conformance claims and registry submission remain deferred in this milestone
