# M2B — EEG/MEG preprocessing, QC, and report integration

## Why this milestone is next

The canonical oddball intake slice now emits a deterministic BIDS-aligned intake tree plus truthful validator-aware status artifacts. The next credible step is to define the narrowest preprocessing and QC contract that consumes that intake tree without inventing empirical signal processing when placeholder-only input blocks execution.

## Read first

1. `AGENTS.md`
2. `project_state/CURRENT_STAGE.md`
3. `project_state/NEXT_MILESTONE.md`
4. `METHODS_POLICY.md`
5. `THREAT_MODEL.md`
6. `docs/standards-stack.md`
7. `examples/eeg-oddball/study_spec.yaml`
8. `src/cogsci_skilllib/study_spec.py`
9. `src/cogsci_skilllib/bids_curator.py`
10. `src/cogsci_skilllib/repro_bundle.py`
11. `scripts/run_oddball_bids_slice.py`
12. `skills/eeg-meg-pipeline/SKILL.md`
13. `README.md`
14. `skills/catalog.json`

## Remaining in-scope work to finish M2B

- Add a deterministic local `eeg-meg-pipeline` runner that consumes only the canonical oddball `bids-intake/` tree emitted by M2A.
- Emit machine-readable preprocessing and QC contract artifacts derived from runtime metadata, including explicit `passed`, `failed`, or structured `not_run` status for MNE-BIDS / MNE steps.
- Preserve truthful `not_run` behavior whenever the input tree remains placeholder-only or lacks empirical EEG signal files required for real preprocessing.
- Surface preprocessing/QC status in the reproducibility bundle, methods text, run manifest, and report text only as far as the emitted runtime artifacts justify.
- Update tests, docs, `skills/eeg-meg-pipeline/SKILL.md`, `skills/catalog.json`, and generated skill docs only as needed to match the real emitted contract.

## Explicitly out of scope

- Claims of completed preprocessing, QC, or ERP analysis without real runtime artifacts
- Expansion beyond the canonical oddball intake tree as the supported input contract
- Participant-level scientific interpretation or manuscript-level EEG conclusions
- Hidden network dependence, silent fallbacks, or inferred channel/event metadata not present in checked-in inputs
- Promotion of `eeg-meg-pipeline` to supported-demo unless the emitted artifacts justify that status honestly

## Completion criteria for this milestone

- Running the canonical oddball neuro slice under a supported Python >=3.11 environment consumes the `bids-intake/` tree and emits truthful preprocessing/QC status artifacts plus report-bundle references.
- Placeholder-only input remains labeled explicitly, and any blocked MNE-BIDS / MNE steps emit structured `not_run` artifacts rather than pretending preprocessing occurred.
- Sensitive-data and privacy review requirements remain explicit because the oddball study spec marks `contains_sensitive_data: true`.
- Tests and docs cover the preprocessing/QC contract, and generated skill-table outputs remain synchronized with `skills/catalog.json`.

## Verification commands

- `pytest -q`
- `.venv/bin/python -m pytest -q`
- `.venv/bin/python scripts/run_oddball_bids_slice.py --study-spec examples/eeg-oddball/study_spec.yaml --output-dir <temp-dir> --validate-bids auto`
- `.venv/bin/python scripts/run_oddball_eeg_pipeline_slice.py --input-dir <temp-dir>/bids-intake --output-dir <temp-pipeline-dir> --run-mne-bids auto --run-mne auto`
- Inspect the emitted preprocessing/QC artifacts, run manifest, and report text for truthful support boundaries.
- `python3 scripts/render_skill_catalog.py` and `python3 scripts/render_skill_catalog.py --check` if catalog-driven docs change

## Standards / scientific constraints

- Do not claim MNE-BIDS or MNE support unless a real emitted runtime artifact justifies each claim.
- Keep placeholder-only inputs and blocked execution states explicit; do not imply empirical EEG files were processed when they were not.
- Respect the threat model: no PII in logs or examples, no private paths, and no hidden network dependence.
- Do not silently invent channel layouts, reference schemes, event timing, filter settings, or QC thresholds that are not present in checked-in inputs or runtime configuration.
- Methods prose must remain derived from runtime metadata and emitted status artifacts, not from model memory.

## Required docs to revisit before completion

- `project_state/CURRENT_STAGE.md`
- `project_state/MILESTONE_HISTORY.md`
- `project_state/NEXT_MILESTONE.md`
- `project_state/BACKLOG.md`
- `skills/eeg-meg-pipeline/SKILL.md`
- `README.md` if public capability claims change
- `skills/catalog.json` and generated skill-table outputs if skill metadata changes
