# Current Stage

- Current phase: Phase 2 — EEG/MEG expansion
- Project maturity: pre-v1, supported-demo behavioral slice with verified Bayesian artifacts, deterministic preregistration export, and machine-readable provenance packaging; beginning narrow EEG/MEG intake expansion
- Current milestone: M2A — BIDS-curated EEG/MEG oddball intake slice
- Status: in progress; Phase 1 behavioral work is complete for the canonical Flanker slice, and the immediate remaining work is a validator-aware BIDS intake slice for the checked-in EEG oddball demo
- Last completed milestone: M1D — preregistration and provenance packaging for the Flanker slice
- Immediate next milestone: M2A — BIDS-curated EEG/MEG oddball intake slice
- Blockers: none for M2A start. Operational note: bare `python3` on this machine still resolves to Python 3.9.13, so supported local runs should continue to use a Python >=3.11 environment such as `.venv/bin/python`.
- Last updated: 2026-03-07

## Evidence for current status

- `src/cogsci_skilllib/study_spec.py` now treats `preregistration` as a supported requested output for the canonical Flanker slice while continuing to mark `Cognitive Atlas` as unsupported.
- `src/cogsci_skilllib/repro_bundle.py` now emits deterministic `report/preregistration/preregistration.json`, `report/provenance/ro-crate-metadata.json`, and `report/provenance/prov.jsonld` derived from normalized study-spec content and runtime metadata.
- `src/cogsci_skilllib/repro_bundle.py` now records preregistration and provenance artifact references in `report/report_bundle.json`, `report/provenance/run_manifest.json`, `report/report.md`, and `report/methods.md` while keeping unsupported capabilities and required human-review points explicit.
- `scripts/run_flanker_behavioral_slice.py` now writes preregistration and provenance artifacts before final checksum generation so the full bundle inventory is represented in machine-readable outputs and `report/checksums.sha256`.
- `schemas/report-bundle.schema.json` now requires non-null preregistration and provenance references plus the run-manifest path for the implemented Flanker bundle contract.
- `tests/test_flanker_behavioral_slice.py` now covers deterministic preregistration content, RO-Crate structure, PROV structure, updated manifest references, and the continued runtime-sensitive Bayesian / DDM semantics.
- `skills/repro-bundle/SKILL.md`, `skills/catalog.json`, `README.md`, `docs/reproducibility-bundle.md`, `ROADMAP.md`, and generated skill-table outputs now promote the narrow supported-demo preregistration / provenance contract without claiming registry submission or validator-backed provenance conformance.
- `pytest -q` passed on 2026-03-07 with `16 passed, 1 skipped`.
- `.venv/bin/python -m pytest -q` passed on 2026-03-07 with `16 passed, 1 skipped`.
- `.venv/bin/python scripts/run_flanker_behavioral_slice.py --study-spec examples/flanker-behavioral/study_spec.yaml --output-dir <temp-dir> --validate-psychds auto --validate-hed auto --fit-bayes auto --fit-ddm auto` passed on 2026-03-07 and emitted `report/preregistration/preregistration.json`, `report/provenance/ro-crate-metadata.json`, and `report/provenance/prov.jsonld` with `unsupported_requested_outputs = []`, `unsupported_requested_standards = ["Cognitive Atlas"]`, `validation.report_bundle.status = passed`, and `modeling.bayesian.status = passed`.
- `python3 scripts/render_skill_catalog.py` and `python3 scripts/render_skill_catalog.py --check` both passed on 2026-03-07 after the `repro-bundle` catalog metadata was updated.
- The implemented behavioral slice still defers drift-diffusion fitting beyond runtime probing, registry or API preregistration submission, validator-backed RO-Crate / PROV conformance claims, figures, tables, and EEG/MEG preprocessing or analysis.
