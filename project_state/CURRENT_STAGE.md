# Current Stage

- Current phase: Phase 2 — EEG/MEG expansion
- Project maturity: pre-v1, supported-demo behavioral slice with verified Bayesian artifacts, deterministic preregistration export, machine-readable provenance packaging, and a narrow validator-aware oddball BIDS intake slice
- Current milestone: M2B — EEG/MEG preprocessing, QC, and report integration
- Status: in progress; M2A is complete, and the immediate remaining work is a truthful preprocessing/QC contract that consumes only the canonical oddball intake tree without overstating MNE execution
- Last completed milestone: M2A — BIDS-curated EEG/MEG oddball intake slice
- Immediate next milestone: M2B — EEG/MEG preprocessing, QC, and report integration
- Blockers: none for M2B start. Operational note: the canonical oddball intake tree is placeholder-only, so M2B must preserve explicit `not_run` semantics whenever empirical EEG files are absent. Operational note: bare `python3` on this machine still resolves to Python 3.9.13, so supported local runs should continue to use a Python >=3.11 environment such as `.venv/bin/python`.
- Last updated: 2026-03-08

## Evidence for current status

- `src/cogsci_skilllib/study_spec.py` now validates two explicit supported profiles: the canonical Flanker behavioral demo and the canonical auditory oddball BIDS-intake demo, with truthful per-profile unsupported requested standards.
- `src/cogsci_skilllib/bids_curator.py` now emits a deterministic `bids-intake/` tree for the checked-in oddball study spec with `dataset_description.json`, `README.md`, `participants.tsv`, `participants.json`, `intake_manifest.json`, and 24 placeholder participant artifacts labeled `contains_empirical_data = false`.
- `src/cogsci_skilllib/bids_curator.py` now records local-only `bids-validator` execution as `passed`, `failed`, or structured `not_run` artifacts without bootstrapping network-dependent tooling.
- `scripts/run_oddball_bids_slice.py` now validates the canonical oddball study spec, writes BIDS intake artifacts, emits `report/validation/bids-validator.json`, and assembles `report/report_bundle.json`, `report/preregistration/preregistration.json`, `report/provenance/run_manifest.json`, `report/provenance/ro-crate-metadata.json`, and `report/provenance/prov.jsonld`.
- `src/cogsci_skilllib/repro_bundle.py` and `schemas/report-bundle.schema.json` now expose an oddball-specific `bids_intake` bundle contract while preserving the existing Flanker behavioral path.
- `tests/test_oddball_bids_slice.py` now covers deterministic oddball output structure, privacy propagation, truthful unsupported requested standards, validator `not_run` behavior, and local validator `passed` / `failed` semantics with a fake `bids-validator` binary.
- `skills/bids-curator/SKILL.md`, `skills/catalog.json`, `README.md`, `ROADMAP.md`, and generated skill-table outputs now promote `bids-curator` to `supported-demo` only for the canonical oddball intake slice and continue to defer preprocessing or analysis claims.
- `pytest -q` passed on 2026-03-08 with `20 passed, 1 skipped`.
- `.venv/bin/python -m pytest -q` passed on 2026-03-08 with `20 passed, 1 skipped`.
- `.venv/bin/python scripts/run_oddball_bids_slice.py --study-spec examples/eeg-oddball/study_spec.yaml --output-dir /tmp/cogsci-oddball-3UpVCF --validate-bids auto` passed on 2026-03-08 and emitted a deterministic `bids-intake/` tree, `validation.bids.status = not_run`, `unsupported_requested_standards = ["HED", "MNE", "MNE-BIDS"]`, and `validation.report_bundle.status = passed`.
- `python3 scripts/render_skill_catalog.py` and `python3 scripts/render_skill_catalog.py --check` both passed on 2026-03-08 after the `bids-curator` catalog metadata was updated.
- The implemented oddball slice still defers empirical EEG conversion, `events.tsv` / channel / electrode metadata generation, HED annotation, MNE-BIDS ingestion, MNE preprocessing, QC dashboards, ERP analysis, participant-level interpretation, registry submission, and validator-backed RO-Crate / PROV conformance claims.
