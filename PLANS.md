# PLANS.md

Use this file for multi-step implementation work.

## When to update this file

Update this file when a task:

- changes scientific behavior
- touches multiple files
- adds a new skill
- changes validation or provenance logic
- is expected to take more than a quick patch

## Current execution plan template

### Task
Describe the task in one sentence.

### Scope
List the files or subsystems expected to change.

### Constraints
List standards, policies, or docs that govern the work.

### Steps
1. …
2. …
3. …

### Verification
- tests to run
- docs to regenerate
- demo commands to verify

### Notes / risks
Record unresolved questions or follow-up items.

---

## Milestone 1: Deterministic Flanker Behavioral Slice

### Task
Implement the first production-quality behavioral vertical slice for `examples/flanker-behavioral/study_spec.yaml`: study spec validation, deterministic jsPsych task artifact generation, Psych-DS-aligned demo curation, and reproducibility bundle assembly.

### Current maturity
- Strategic docs, schemas, and skill contracts are present.
- There is no real runner, skill implementation, or Flanker pipeline yet.
- CI currently checks only catalog synchronization and a smoke test.

### File-level execution plan
1. Update `PLANS.md` first and keep it aligned with the actual work.
2. Add the Flanker runner entrypoint at `scripts/run_flanker_behavioral_slice.py`.
3. Add source modules under `src/cogsci_skilllib/` for study-spec validation, deterministic Flanker generation, jsPsych artifact rendering, Psych-DS curation, and report bundle assembly.
4. Vendor the pinned jsPsych browser assets under `src/cogsci_skilllib/vendor/jspsych/` and document their provenance.
5. Add an end-to-end integration test and determinism coverage in `tests/`.
6. Update skill metadata and public docs: `skills/catalog.json`, the three target `SKILL.md` files, `README.md`, `docs/reproducibility-bundle.md`, `ROADMAP.md`, and `benchmarks/registry.json`.
7. Regenerate derived docs with `scripts/render_skill_catalog.py`.
8. Run the available local checks and record any environment-specific limits.

### Assumptions
- This milestone supports only the canonical Flanker behavioral demo path, not arbitrary behavioral study specs.
- Study-spec handling stays aligned with `schemas/study-spec.schema.yaml`; missing task-timing details are emitted as explicit runtime demo assumptions rather than silently inferred as general capability.
- The implemented demo uses four fixed stimuli: `<<<<<`, `>>>>>`, `>><>>`, and `<<><<`.
- The implemented demo uses two deterministic synthetic participants: `demo001` with mapping A (`f` = left, `j` = right) and `demo002` with mapping B (`j` = left, `f` = right).
- The implemented demo timings are fixation `500 ms`, response deadline `1500 ms`, and inter-trial interval `750 ms`.
- Synthetic data is used only to exercise curation and bundle assembly and must be labeled synthetic in all outputs.

### Risks
- Psych-DS structure may still need iteration if the external validator surfaces issues once installed in CI.
- Local development uses `python3` 3.9 in this environment while CI targets Python 3.11, so implementation must avoid unnecessary interpreter-version assumptions.
- The repo currently has no Node runtime locally, so validator execution may need to fall back to a structured `not_run` artifact outside CI.
- Vendoring browser assets introduces provenance and maintenance obligations that must be documented explicitly.

### Acceptance criteria
- Running the Flanker entrypoint from the repo root produces a self-contained output directory with `task/`, `metadata/`, `psychds/`, and `report/`.
- The task artifact is a real offline-capable jsPsych package that uses only local assets.
- The curated output is explicitly Psych-DS-aligned for the demo path and includes machine-readable dataset metadata.
- The reproducibility bundle includes a machine-readable manifest aligned to `schemas/report-bundle.schema.json`, methods text derived from runtime metadata, commands, environment, checksums, and validation artifacts.
- Unsupported outputs and standards are explicit in machine-readable runtime artifacts and in public docs.
- Tests exercise the entrypoint in CI, and generated skill docs are regenerated from `skills/catalog.json`.

### Definition of done for this run
- `examples/flanker-behavioral/study_spec.yaml` runs end to end through the implemented slice.
- `pytest -q` passes.
- `scripts/render_skill_catalog.py` has been run and generated docs are current.
- Public claims in `README.md`, `skills/catalog.json`, and the target `SKILL.md` files match the real implementation.
- Remaining unsupported or experimental items are called out explicitly and truthfully.
