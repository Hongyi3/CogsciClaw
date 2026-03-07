# Reproducibility bundle

## Philosophy

A run is not complete until it can be rerun.

## Implemented Flanker demo bundle

```text
output/
├── task/
├── metadata/
├── psychds/
└── report/
    ├── report_bundle.json
    ├── report.md
    ├── methods.md
    ├── commands.sh
    ├── environment.lock.yml
    ├── checksums.sha256
    ├── provenance/
    │   └── run_manifest.json
    └── validation/
        ├── study-spec-validation.json
        ├── report-bundle-validation.json
        └── psychds-validator.json
```

This is the currently implemented public contract for the deterministic Flanker slice. The bundle intentionally records unsupported items rather than pretending they ran.

## Required properties for the implemented slice

- each file has a defined purpose
- commands are executable or close to executable
- environment is specific enough to recreate the run
- validation outputs reflect the actual run
- methods text is derived from run metadata
- outputs missing due to unsupported steps are explicitly noted

## Deferred or experimental bundle items

- RO-Crate metadata
- PROV metadata
- preregistration exports
- figures and tables
- HED validation artifacts
- BIDS validation artifacts

## Nice-to-have additions later

- container recipe
- DataLad dataset linkage
- rendered HTML report
- workflow provenance graph
