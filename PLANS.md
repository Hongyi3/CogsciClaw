# PLANS.md

Use this file for the current multi-step run only.

Persistent cross-run milestone state lives in `project_state/`.

## Current execution plan

### Task
Complete `M2A — BIDS-curated EEG/MEG oddball intake slice` by implementing a deterministic, validator-aware BIDS intake path for the checked-in auditory oddball study spec, then close the milestone honestly if verification justifies it.

### Scope
- `PLANS.md`
- `project_state/CURRENT_STAGE.md`
- `project_state/NEXT_MILESTONE.md`
- `project_state/MILESTONE_HISTORY.md`
- `project_state/BACKLOG.md`
- `src/cogsci_skilllib/study_spec.py`
- `src/cogsci_skilllib/bids_curator.py`
- `src/cogsci_skilllib/repro_bundle.py`
- `scripts/run_oddball_bids_slice.py`
- `schemas/report-bundle.schema.json`
- `tests/test_oddball_bids_slice.py`
- `tests/test_flanker_behavioral_slice.py`
- `skills/bids-curator/SKILL.md`
- `skills/catalog.json`
- `README.md`
- `ROADMAP.md`
- `docs/generated/skills-table.md`

### Constraints
- Keep the implementation limited to the canonical auditory oddball EEG study spec in `examples/eeg-oddball/study_spec.yaml`.
- Emit a real BIDS-aligned intake tree with explicit placeholder labeling and no invented empirical acquisition metadata.
- Do not emit EEG raw files, events, channels, electrodes, HED artifacts, MNE-BIDS outputs, preprocessing outputs, ERP analyses, or participant-level interpretations.
- Use only a preinstalled local `bids-validator` binary for validation; otherwise emit structured `not_run` artifacts with no network bootstrap.
- Preserve the existing Flanker behavioral slice unchanged except where shared schema or bundle code must expand to support the oddball intake contract.
- Keep privacy review explicit because the oddball study spec marks `contains_sensitive_data: true`.
- Regenerate catalog-driven docs only from `skills/catalog.json`.

### Steps
1. Replace the stale M1D plan in this file with the M2A execution plan before any other repo edits.
2. Refactor study-spec validation into profile-aware logic so both the canonical Flanker demo and the canonical oddball BIDS-intake demo are supported explicitly and truthfully.
3. Implement `src/cogsci_skilllib/bids_curator.py` for the canonical oddball intake tree plus local-only BIDS-validator integration.
4. Add `scripts/run_oddball_bids_slice.py` to validate the oddball study spec, emit the intake tree, write validation artifacts, and assemble the full reproducibility bundle.
5. Extend the report-bundle schema and bundle code to surface oddball intake metadata, validator status, preregistration, and provenance without weakening the Flanker path.
6. Add deterministic oddball tests and keep the Flanker suite green.
7. Update `skills/bids-curator/SKILL.md`, `skills/catalog.json`, `README.md`, `ROADMAP.md`, and generated skill-table outputs to match the real supported-demo oddball intake contract.
8. Run milestone verification commands, inspect the emitted oddball artifacts, and only then update the project-state files to close M2A and record M2B as the next milestone.
9. Stage only milestone files, commit once, and push to `origin` on the current branch unless a safe push is blocked.

### Verification
- `pytest -q`
- `.venv/bin/python -m pytest -q`
- `.venv/bin/python scripts/run_oddball_bids_slice.py --study-spec examples/eeg-oddball/study_spec.yaml --output-dir <temp-dir> --validate-bids auto`
- Inspect `bids-intake/`, `report/validation/bids-validator.json`, `report/report_bundle.json`, `report/provenance/run_manifest.json`, and `report/preregistration/preregistration.json`
- `python3 scripts/render_skill_catalog.py`
- `python3 scripts/render_skill_catalog.py --check`

### Notes / risks
- `python3` on this machine still resolves to Python 3.9.13; supported implementation and verification should continue to use `.venv/bin/python` where Python >=3.11 is required.
- The machine currently has no `bids-validator`, `node`, `npm`, `npx`, or `deno` on `PATH`, so the expected validator result in this environment is `not_run`.
- The worktree is already dirty in unrelated files; do not stage or revert `docs/codex-playbook.md` or `.github/codex/prompts/*`.
- Project-state files should only advance to M2B if the oddball slice, tests, docs, generated outputs, commit, and push all succeed.
