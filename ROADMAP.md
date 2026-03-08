# Roadmap

## Phase 0 — charter and repository foundation (weeks 1–4)

### Goals

- freeze v1 scope
- finalize standards stack
- publish governance, methods, security, and evaluation docs
- establish catalog-driven documentation generation
- set up CI and Codex workflow

### Exit criteria

- top-level docs are present and internally consistent
- `skills/catalog.json` exists
- `scripts/render_skill_catalog.py` works
- CI runs tests and catalog drift checks
- Codex workflow exists in `.github/workflows/`

## Phase 1 — behavioral vertical slice (weeks 4–12)

### Milestone 1 status

- implemented: canonical Flanker jsPsych task package with local assets
- implemented: deterministic synthetic demo data and Psych-DS-aligned curation
- implemented: report bundle manifest, methods, commands, environment, checksums, validation artifacts, deterministic preregistration export, and machine-readable provenance packaging
- implemented: HED annotation plus truthful local validation artifacts for the canonical Flanker demo
- implemented: verified Bayesian baseline artifacts with diagnostics on healthy Python >=3.11 runtimes and honest DDM runtime probing
- deferred within the completed behavioral slice: drift-diffusion fitting beyond runtime probing, registry or API preregistration submission, validator-backed RO-Crate / PROV conformance claims, and figures / tables

### Goals

- implement `task-jspsych`
- implement `psychds-curator`
- implement `hed-annotator`
- implement `ddm-bayes`
- implement `repro-bundle`
- ship Flanker demo end to end

### Exit criteria

- Flanker study spec → task package → Psych-DS dataset → HED annotations → Bayesian / DDM analysis → report bundle
- demo runs from clean environment
- methods text generated from run metadata
- validator outputs bundled

## Phase 2 — EEG/MEG expansion (months 3–6)

### Milestone 2 status

- implemented: canonical auditory oddball EEG BIDS-aligned intake tree with deterministic placeholder participant artifacts, machine-readable intake metadata, and truthful local `bids-validator` status artifacts
- deferred within the current neuro slice: empirical EEG conversion, `events.tsv` / channel / electrode metadata generation, HED annotation, MNE-BIDS ingestion, MNE preprocessing, QC dashboards, ERP analysis, and participant-level interpretation

### Goals

- implement `bids-curator`
- implement `eeg-meg-pipeline`
- ship oddball / ERP demo
- add QC dashboard and reporting checklist

### Exit criteria

- EEG demo produces BIDS-aligned intake, preprocessing outputs, QC summaries, report bundle
- MNE-based pipeline documented and reproducible
- BIDS / HED validation artifacts included

## Phase 3 — publication and design partners (months 6–9)

### Goals

- preregister benchmark protocol
- archive first public release with DOI
- onboard 2–3 design-partner labs
- collect reproducibility and usability feedback
- prepare preprint and JOSS materials

### Exit criteria

- public release archived
- benchmarks documented
- external feedback incorporated
- submission drafts underway

## Phase 4 — neuro expansion and ecosystem maturation (months 9–12)

### Goals

- evaluate `questionnaire-reproschema`
- plan `fmri-prep-wrapper`
- plan `nwb-curator`
- harden contributor review process
- consider additional curated skills

### Exit criteria

- contribution model is stable
- external contributors can add skills safely
- roadmap for v1.1 is explicit and realistic
