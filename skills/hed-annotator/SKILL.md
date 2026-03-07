---
name: hed-annotator
description: Generate deterministic HED event tables and optional local hedtools validation artifacts for the canonical Flanker behavioral demo.
version: 0.1.0
status: supported-demo
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
standards:
  - HED
trigger_keywords:
  - hed
  - event annotation
  - events.tsv
  - events.json
dependencies:
  python: ">=3.11"
  packages:
    - hedtools
---

# hed-annotator

## Why this exists

Event semantics are often described informally, which blocks machine-actionable reuse. This skill turns the canonical Flanker demo's deterministic task/runtime metadata into explicit HED event tables and an honest validation artifact.

## Supported use cases

- the canonical behavioral Flanker demo at `examples/flanker-behavioral/study_spec.yaml`
- deterministic `events/` artifacts with one shared sidecar and participant-local event TSVs
- row-level HED strings derived from checked-in mapping rules in `schemas/hed/flanker-demo-events.json`
- local-first HED validation with vendored schema `schemas/hed/HED8.4.0.xml` when `hedtools` is installed
- structured `not_run` validation artifacts when `hedtools` is unavailable locally

## Unsupported or deferred cases

- arbitrary task/event schemas beyond the canonical Flanker demo
- BIDS event-file generation or any implied BIDS dataset support
- EEG/MEG event annotation workflows
- ontology inference from sparse or ambiguous event labels without review
- silent generation of unverifiable HED tags
- automatic schema downloads or hidden remote validation calls

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| synthetic trial tables | in-memory row dicts | yes | deterministic Flanker rows from `flanker_demo.py` |
| demo profile | JSON-like dict | yes | fixed timing metadata for onset/duration derivation |
| validation mode | CLI flag | no | `auto`, `always`, or `never` |

## Workflow

1. Load the checked-in Flanker HED mapping rules and vendored HED schema reference.
2. Derive deterministic stimulus/response event rows from the synthetic Flanker trial tables.
3. Emit `events/flanker_events.json` plus one participant event TSV per synthetic participant/session.
4. If `hedtools` is available locally, validate the sidecar and TSVs against the vendored schema.
5. Otherwise emit a structured `not_run` artifact instead of claiming validation support.

## Validation

- row-count contract: two event rows per trial for the supported demo
- deterministic output checks in CI for the sidecar and participant TSVs
- local `hedtools` validation path when installed
- explicit `not_run` status when `hedtools` is unavailable or disabled

## Demo mode

Run:

```bash
python3 scripts/run_flanker_behavioral_slice.py \
  --study-spec examples/flanker-behavioral/study_spec.yaml \
  --output-dir output/flanker-behavioral \
  --validate-psychds auto \
  --validate-hed auto
```

## Outputs

```text
output/
├── events/
│   ├── flanker_events.json
│   ├── participant-demo001_session-1_events.tsv
│   └── participant-demo002_session-1_events.tsv
└── report/
    └── validation/
        └── hed-validator.json
```

## Safety

- ambiguous event semantics must be surfaced, not hidden
- do not generate unsupported ontology claims
- do not imply BIDS support from these artifacts
- do not treat a missing local validator as a pass

## Integration notes

- upstream: `task-jspsych`, deterministic Flanker demo metadata
- downstream: `repro-bundle`

## Citations

- cite HED and the vendored schema version used for validation
- note that this supported-demo path is restricted to the canonical Flanker behavioral slice
