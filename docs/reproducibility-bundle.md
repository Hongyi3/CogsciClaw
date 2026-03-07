# Reproducibility bundle

## Philosophy

A run is not complete until it can be rerun.

## Implemented Flanker demo bundle

```text
output/
├── events/
│   ├── flanker_events.json
│   └── participant-*_events.tsv
├── task/
├── metadata/
├── model/
│   ├── model_input.csv
│   ├── model_manifest.json
│   ├── bayesian-condition-effects.json
│   ├── bayesian-diagnostics.json
│   └── ddm-status.json
├── psychds/
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
        ├── study-spec-validation.json
        ├── report-bundle-validation.json
        └── psychds-validator.json
```

This is the currently implemented public contract for the deterministic Flanker slice. The bundle intentionally records unsupported items rather than pretending they ran.

On healthy local Python >=3.11 environments with PyMC / ArviZ installed, the canonical synthetic Flanker slice now includes a real Bayesian baseline fit plus convergence diagnostics. Unsupported runtimes still emit a structured `not_run` status instead of a false pass.
The bundle also emits a deterministic local preregistration artifact plus machine-readable RO-Crate and PROV exports for the canonical synthetic Flanker slice.

## Required properties for the implemented slice

- each file has a defined purpose
- commands are executable or close to executable
- environment is specific enough to recreate the run
- validation outputs reflect the actual run
- methods text is derived from run metadata
- HED validation artifacts record `passed`, `failed`, or `not_run` honestly
- Bayesian and DDM artifacts record `passed`, `failed`, or `not_run` honestly
- preregistration artifacts remain labeled synthetic-demo and include explicit human-review points
- provenance artifacts describe the emitted bundle without claiming external validation
- outputs missing due to unsupported steps are explicitly noted
- model inputs remain labeled synthetic-demo throughout the bundle

## Deferred or experimental bundle items

- drift-diffusion fitting beyond runtime probing
- registry or API preregistration submission
- validator-backed RO-Crate / PROV conformance claims
- figures and tables
- BIDS validation artifacts

## Nice-to-have additions later

- container recipe
- DataLad dataset linkage
- rendered HTML report
- workflow provenance graph
