# PLANS.md

Use this file for the current multi-step run only.

Persistent cross-run milestone state lives in `project_state/`.

## Current execution plan

### Task
Complete `M1D — preregistration and provenance packaging for the Flanker slice` by emitting deterministic preregistration and machine-readable provenance artifacts for the canonical Flanker demo, then close the milestone honestly.

### Scope
- `PLANS.md`
- `project_state/CURRENT_STAGE.md`
- `project_state/NEXT_MILESTONE.md`
- `project_state/MILESTONE_HISTORY.md`
- `project_state/BACKLOG.md`
- `src/cogsci_skilllib/study_spec.py`
- `src/cogsci_skilllib/repro_bundle.py`
- `scripts/run_flanker_behavioral_slice.py`
- `schemas/report-bundle.schema.json`
- `tests/test_flanker_behavioral_slice.py`
- `skills/repro-bundle/SKILL.md`
- `skills/catalog.json`
- `README.md`
- `docs/reproducibility-bundle.md`
- `ROADMAP.md`
- `docs/generated/skills-table.md`

### Constraints
- Keep the implementation limited to the canonical deterministic Flanker demo slice.
- Emit real preregistration and provenance artifacts derived from normalized study-spec content and runtime metadata; do not add prose-only placeholders.
- Keep synthetic-demo labeling explicit throughout preregistration, provenance, report, and methods outputs.
- Do not claim registry/API preregistration submission, validator-backed RO-Crate / PROV conformance, DDM fitting, figures, tables, or arbitrary study-spec support.
- Preserve truthful runtime-sensitive Bayesian semantics: supported runtimes may pass, unsupported runtimes must still record structured `not_run` or `failed` artifacts.
- Preserve the existing honest `Cognitive Atlas` unsupported-standard behavior.
- Regenerate catalog-driven docs only from `skills/catalog.json`.

### Steps
1. Replace the stale M1C plan in this file with the M1D execution plan before any other repo edits.
2. Extend the study-spec support contract so the canonical Flanker slice truthfully supports `preregistration` output while leaving unsupported standards explicit.
3. Add deterministic preregistration, RO-Crate, and PROV builders to the reproducibility bundle code and wire their artifact paths into the run manifest, report bundle manifest, methods text, and report text.
4. Update the Flanker runner to emit `report/preregistration/preregistration.json`, `report/provenance/ro-crate-metadata.json`, and `report/provenance/prov.jsonld` before final checksum generation.
5. Tighten the report-bundle schema and integration test expectations around the new artifact contract.
6. Update `repro-bundle` skill metadata and public docs to reflect the actual supported-demo contract, then regenerate derived skill-table outputs.
7. Run the required verification commands, inspect the emitted artifacts, and only then mark M1D complete in the project-state files.
8. If all checks pass, advance project state to `M2A — BIDS-curated EEG/MEG oddball intake slice`; otherwise keep M1D open with precise blockers and next actions.

### Verification
- `pytest -q`
- `.venv/bin/python -m pytest -q`
- `.venv/bin/python scripts/run_flanker_behavioral_slice.py --study-spec examples/flanker-behavioral/study_spec.yaml --output-dir <temp-dir> --validate-psychds auto --validate-hed auto --fit-bayes auto --fit-ddm auto`
- Inspect `report/preregistration/preregistration.json`, `report/provenance/ro-crate-metadata.json`, `report/provenance/prov.jsonld`, `report/report_bundle.json`, `report/provenance/run_manifest.json`, `report/report.md`, and `report/methods.md`.
- `python3 scripts/render_skill_catalog.py`
- `python3 scripts/render_skill_catalog.py --check`

### Notes / risks
- `python3` on this machine still resolves to Python 3.9.13, so the supported Bayesian verification path must continue to use `.venv/bin/python`.
- The repo worktree is already dirty; only milestone-relevant files should be edited, staged, committed, and pushed.
- Provenance exports should follow minimal RO-Crate / PROV structures without overstating validator-backed conformance.
- Checksums must remain deterministic and must not recurse through self-hashing provenance content.
