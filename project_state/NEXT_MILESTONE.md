# M2A — BIDS-curated EEG/MEG oddball intake slice

## Why this milestone is next

The canonical Flanker behavioral slice now closes Phase 1 with deterministic preregistration and machine-readable provenance packaging. Phase 2 should begin with the narrowest credible EEG/MEG expansion step: a validator-aware BIDS intake layer for the checked-in auditory oddball study spec, without overstating preprocessing or analysis support.

## Read first

1. `AGENTS.md`
2. `project_state/CURRENT_STAGE.md`
3. `project_state/NEXT_MILESTONE.md`
4. `METHODS_POLICY.md`
5. `THREAT_MODEL.md`
6. `docs/standards-stack.md`
7. `examples/eeg-oddball/study_spec.yaml`
8. `src/cogsci_skilllib/study_spec.py`
9. `skills/bids-curator/SKILL.md`
10. `skills/eeg-meg-pipeline/SKILL.md`
11. `README.md`
12. `skills/catalog.json`

## Remaining in-scope work to finish M2A

- Implement a deterministic, local `bids-curator` demo path for the checked-in auditory oddball EEG study spec only.
- Emit a BIDS-aligned intake tree for the canonical oddball demo with the required machine-readable metadata, explicit synthetic or placeholder labeling, and no hidden assumptions about empirical acquisition files.
- Add truthful BIDS-validator integration for the demo slice: emit `passed`, `failed`, or structured `not_run` output instead of claiming compliance without a validator result.
- Surface the BIDS intake outputs and validator status in machine-readable runtime artifacts and human-readable bundle text only as needed to make the slice reviewable.
- Update tests, docs, `skills/bids-curator/SKILL.md`, `skills/catalog.json`, and generated skill docs only as needed to match the real emitted contract.

## Explicitly out of scope

- MNE preprocessing, ERP analysis, QC dashboards, or any `eeg-meg-pipeline` execution
- Claims of BIDS compliance without a real validator output or truthful `not_run` artifact
- Raw EEG/MEG signal conversion beyond the narrow deterministic intake slice
- Participant-level scientific interpretation, model fitting, or manuscript-level EEG results
- Expansion beyond the checked-in auditory oddball study spec

## Completion criteria for this milestone

- Running the canonical oddball intake slice under a supported Python >=3.11 environment emits a deterministic BIDS-aligned intake tree plus validator-aware status artifacts.
- Sensitive-data and privacy review requirements remain explicit because the oddball study spec marks `contains_sensitive_data: true`.
- Public support claims for `bids-curator` remain narrow and truthful: canonical oddball intake only, no preprocessing or analysis support.
- Tests and docs cover the emitted BIDS intake contract, and generated skill-table outputs remain synchronized with `skills/catalog.json`.

## Verification commands

- `pytest -q`
- `.venv/bin/python -m pytest -q`
- `.venv/bin/python scripts/run_oddball_bids_slice.py --study-spec examples/eeg-oddball/study_spec.yaml --output-dir <temp-dir> --validate-bids auto`
- Inspect the resulting BIDS intake tree, validator artifact, and any report/run-manifest references for truthful support boundaries.
- `python3 scripts/render_skill_catalog.py` and `python3 scripts/render_skill_catalog.py --check` if catalog-driven docs change

## Standards / scientific constraints

- Do not claim BIDS support unless a real BIDS-shaped artifact is emitted and paired with a validator result or a truthful `not_run` artifact.
- Keep all demo inputs and outputs explicit about synthetic or placeholder status; do not imply empirical EEG/MEG data were processed.
- Respect the threat model: no PII in logs or examples, no private paths, and no hidden network dependence.
- Do not imply HED, MNE-BIDS, MNE, preprocessing, or ERP support unless a real emitted artifact justifies each claim.
- Do not silently invent channel layouts, recording parameters, event timing, or subject metadata that are not present in checked-in demo inputs.

## Required docs to revisit before completion

- `project_state/CURRENT_STAGE.md`
- `project_state/MILESTONE_HISTORY.md`
- `project_state/NEXT_MILESTONE.md`
- `project_state/BACKLOG.md`
- `skills/bids-curator/SKILL.md`
- `README.md` if public capability claims change
- `skills/catalog.json` and generated skill-table outputs if skill metadata changes
