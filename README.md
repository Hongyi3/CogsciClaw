# cogsci-skilllib

**Standards-first cognitive-science agent skills with one implemented behavioral demo slice, one narrow oddball BIDS-intake demo, and scaffolded expansion paths.**

This repository started as a prework scaffold for a ClawBio-style project adapted to cognitive science. It now includes one real end-to-end behavioral vertical slice for the canonical Flanker example plus one narrow validator-aware oddball BIDS intake slice while keeping the broader roadmap explicit and narrow. The aim is not to ship a generic “AI for psychology” assistant. The aim is to build a **cognitive-science-native workflow system** that turns well-scoped research requests into reproducible research objects: task code, standards-compliant data structure, validator outputs, analysis code, figures, tables, methods text, and provenance.

## North star

> Every task, figure, and model in a cognitive-science paper should be one command away from reproduction.

## Principles

- **Standards-first**: adopt existing community standards before inventing new formats.
- **Local-first**: participant data stays under the lab’s control.
- **Reproducible by default**: every workflow emits a report bundle with commands, environment, checksums, and validation records.
- **Skill-first**: each scientific capability lives in a `SKILL.md`-centered module.
- **No guessing**: methods text, results, and claims must trace to code, runtime metadata, validators, or cited sources.

## Recommended v1 scope

Ship one narrow, excellent vertical slice first:

1. browser or lab behavioral tasks (`jsPsych`, `PsychoPy`)
2. behavioral curation (`Psych-DS`)
3. event semantics (`HED`)
4. Bayesian / drift-diffusion modeling (`PyMC`, `HDDM`, `ArviZ`)
5. report + preregistration + provenance bundle
6. EEG/MEG expansion after the behavioral slice is trusted

## Repository map

```text
cogsci-skilllib/
├── MASTER_PLAN.md
├── VISION.md
├── ROADMAP.md
├── METHODS_POLICY.md
├── GOVERNANCE.md
├── THREAT_MODEL.md
├── EVALUATION.md
├── AGENTS.md
├── llms.txt
├── docs/
├── skills/
├── templates/
├── schemas/
├── examples/
├── benchmarks/
├── scripts/
├── src/
└── .github/
```

## Implemented now

The repository currently supports two deterministic demo paths:

```bash
python3 scripts/run_flanker_behavioral_slice.py \
  --study-spec examples/flanker-behavioral/study_spec.yaml \
  --output-dir output/flanker-behavioral \
  --validate-psychds auto \
  --validate-hed auto \
  --fit-bayes auto \
  --fit-ddm auto
```

Use a Python >=3.11 environment with the `behavior` and `modeling` extras installed to exercise the supported Bayesian path. Unsupported interpreters still run the slice, but they record a structured `not_run` model status instead of claiming a fit.

That command generates:

- a real offline-capable jsPsych Flanker task package using local vendored assets
- deterministic HED event artifacts for the canonical Flanker demo
- deterministic synthetic demo trial tables for two response-mapping variants
- deterministic model inputs plus Bayesian/DDM status artifacts for the canonical Flanker demo
- a Psych-DS-aligned curated dataset for the demo path
- a reproducibility bundle with manifest, methods, commands, environment, checksums, validation artifacts, deterministic preregistration export, and machine-readable provenance packaging

It also supports a narrow oddball EEG intake path:

```bash
python3 scripts/run_oddball_bids_slice.py \
  --study-spec examples/eeg-oddball/study_spec.yaml \
  --output-dir output/eeg-oddball-bids-intake \
  --validate-bids auto
```

That command generates:

- a deterministic BIDS-aligned intake tree for the checked-in auditory oddball demo
- `dataset_description.json`, `README.md`, participant summary files, and 24 placeholder participant artifacts under `bids-intake/`
- a truthful BIDS validator artifact with `passed`, `failed`, or structured `not_run` status
- a reproducibility bundle with report, methods, commands, environment, checksums, preregistration export, run manifest, and RO-Crate / PROV metadata

## Implemented Flanker bundle

```text
output/
├── events/
│   ├── flanker_events.json
│   └── participant-*_events.tsv
├── task/
│   ├── index.html
│   ├── task.js
│   ├── trials.json
│   ├── task_metadata.json
│   └── jspsych/
├── metadata/
│   ├── normalized_study_spec.json
│   ├── demo_profile.json
│   ├── trial_schedule.json
│   ├── trial_schedule_summary.json
│   ├── column_definitions.json
│   └── participant-*_trials.csv
├── model/
│   ├── model_input.csv
│   ├── model_manifest.json
│   ├── bayesian-condition-effects.json
│   ├── bayesian-diagnostics.json
│   └── ddm-status.json
├── psychds/
│   ├── dataset_description.json
│   └── data/
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
        ├── hed-validator.json
        ├── psychds-validator.json
        ├── report-bundle-validation.json
        └── study-spec-validation.json
```

The current model contract is honest-by-default: on healthy local Python >=3.11 environments with PyMC / ArviZ installed, the bundle includes a real Bayesian baseline fit and diagnostics for the canonical synthetic Flanker demo. When local PyMC / ArviZ or HDDM tooling is unavailable, the bundle records structured `not_run` model artifacts instead of claiming a fit. The reproducibility bundle now also includes a local preregistration export plus machine-readable RO-Crate / PROV packaging for the canonical Flanker slice.

Deferred from the current slice: drift-diffusion fitting beyond runtime probing, registry or API preregistration submission, validator-backed RO-Crate / PROV conformance claims, figures, and tables.

## Implemented Oddball Intake Bundle

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
        ├── bids-validator.json
        ├── report-bundle-validation.json
        └── study-spec-validation.json
```

The oddball contract is intentionally narrow. It supports only the checked-in auditory oddball study spec, emits placeholder-only intake metadata, and records validator-aware BIDS status honestly. It does not claim empirical EEG conversion, HED annotation, MNE-BIDS ingestion, MNE preprocessing, or ERP analysis.

## How to use this repository

1. Read `MASTER_PLAN.md`.
2. Read `VISION.md` and `METHODS_POLICY.md`.
3. Read `AGENTS.md` before assigning work to Codex.
4. Use `skills/catalog.json` as the source of truth for public skill listings.
5. Run `python scripts/render_skill_catalog.py` after changing skill metadata.

## Skill catalog

<!-- SKILL_TABLE_START -->
<!-- generated by scripts/render_skill_catalog.py -->

| Skill | Status | Phase | Lane | Standards | Description |
|---|---|---|---|---|---|
| `task-jspsych` | supported-demo | v1 | behavior | jsPsych | Generate the canonical Flanker jsPsych task package from a structured study specification using local vendored assets. |
| `task-psychopy` | scaffold | v1 | behavior | Psych-DS, HED, Cognitive Atlas | Generate lab-based or hybrid PsychoPy task packages from a structured study specification. |
| `psychds-curator` | supported-demo | v1 | curation | Psych-DS | Curate the deterministic Flanker demo trial tables into a Psych-DS-aligned dataset with optional official validator output. |
| `bids-curator` | supported-demo | v1 | curation | BIDS | Emit the canonical auditory oddball EEG BIDS-aligned intake tree with truthful local validator status artifacts. |
| `hed-annotator` | supported-demo | v1 | annotation | HED | Generate deterministic HED event tables and optional local hedtools validation artifacts for the canonical Flanker behavioral demo. |
| `ddm-bayes` | supported-demo | v1 | modeling | PyMC, HDDM, ArviZ | Emit deterministic model artifacts, fit a supported Bayesian baseline with diagnostics on healthy local runtimes, and record honest DDM runtime-probe status for the canonical Flanker demo. |
| `eeg-meg-pipeline` | scaffold | v1.1 | neuro | BIDS, MNE-BIDS, MNE, HED | Orchestrate EEG/MEG intake and preprocessing with MNE-BIDS and MNE-Python. |
| `repro-bundle` | supported-demo | v1 | reproducibility | JSON Schema, RO-Crate, PROV | Assemble the deterministic Flanker demo reproducibility bundle with preregistration export, RO-Crate / PROV packaging, manifest, methods, commands, environment, checksums, and validation artifacts. |
<!-- SKILL_TABLE_END -->

## What is already scaffolded here

- a strategic master plan
- agent instructions for Codex and other coding agents
- governance, methods, security, evaluation, and publication docs
- a starter `skills/catalog.json`
- `SKILL.md` files for the first core skills, including a supported-demo behavioral slice
- examples for a behavioral Flanker study and an EEG oddball study
- a doc-generation script to keep public skill listings in sync with the source catalog
- a CI workflow and a Codex GitHub Action workflow

## Current status

This repository is still early-stage, but it is no longer scaffold-only. The canonical Flanker behavioral slice is implemented as a supported demo for `task-jspsych`, `hed-annotator`, `psychds-curator`, `ddm-bayes`, and `repro-bundle`. The canonical oddball BIDS intake slice is now implemented as a supported demo for `bids-curator`, with explicit placeholder-only labeling and truthful validator-aware status artifacts. The `ddm-bayes` support claim remains narrow: a verified Bayesian baseline exists for the canonical synthetic Flanker slice on healthy Python >=3.11 runtimes, while fitted DDM results remain deferred and continue to surface as honest runtime-probe status artifacts. The `repro-bundle` support claim is also narrow: it emits deterministic preregistration plus machine-readable RO-Crate / PROV exports for supported demo slices without claiming registry submission or validator-backed provenance conformance.
