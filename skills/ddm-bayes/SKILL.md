---
name: ddm-bayes
description: Emit deterministic model artifacts and optionally fit a supported Bayesian baseline with diagnostics when local modeling tooling is available.
version: 0.1.0
status: supported-demo
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
standards:
  - PyMC
  - HDDM
  - ArviZ
trigger_keywords:
  - ddm
  - bayesian
  - pymc
  - hddm
  - reaction time
dependencies:
  python: ">=3.11"
  packages:
    - numpy
    - scipy
    - arviz
    - pymc
---

# ddm-bayes

## Why this exists

Behavioral tasks often stop at summary statistics even when the scientific question is about latent decision processes. This skill should emit deterministic model inputs, honest runtime status artifacts, and reproducible Bayesian outputs when the local modeling stack is actually available.

## Supported use cases

- deterministic model-input artifacts for the canonical Flanker synthetic demo
- a trial-level Bayesian baseline for RT/accuracy on healthy local Python >=3.11 environments where PyMC / ArviZ imports succeed
- structured diagnostics artifacts for the Bayesian path when it runs
- explicit HDDM runtime probing with a structured `not_run` artifact when DDM fitting is unavailable

## Unsupported or deferred cases

- claiming a Bayesian fit when local PyMC / ArviZ execution failed or was skipped
- hierarchical or fitted DDM results in the current supported-demo slice
- automatic scientific interpretation beyond fitted outputs
- unsupported bespoke cognitive models without explicit implementation

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| curated behavioral data | CSV / TSV | yes | Psych-DS-aligned or equivalent data |
| model spec | YAML / JSON | no | optional model configuration |

## Workflow

1. Read curated task data.
2. Validate required columns and coding assumptions.
3. Write deterministic `model_input.csv` for the canonical Flanker demo.
4. Fit the supported Bayesian baseline only if local PyMC / ArviZ runtime loading succeeds.
5. Emit machine-readable summaries, diagnostics, and structured `not_run` or `failed` status artifacts as needed.
6. Probe HDDM availability and record an explicit DDM status artifact instead of inventing a fallback fit.
7. Prepare methods metadata for the report bundle.

## Validation

- convergence diagnostics when the Bayesian model actually runs
- required-column checks before fitting
- explicit `not_run` artifacts when the local Bayesian or HDDM runtime is unavailable or disabled

## Demo mode

Write deterministic model artifacts for the public synthetic Flanker demo. On healthy local Python >=3.11 environments with PyMC / ArviZ installed, the demo also fits the supported Bayesian baseline; otherwise it records a truthful `not_run` status.

## Outputs

```text
output/
├── model/
│   ├── model_input.csv
│   ├── model_manifest.json
│   ├── bayesian-condition-effects.json
│   ├── bayesian-diagnostics.json
│   └── ddm-status.json
└── report/
    ├── report.md
    └── methods.md
```

## Safety

- do not hide convergence failures
- do not hide runtime failures behind a claimed Bayesian or DDM fit
- do not oversell psychological interpretation of latent parameters

## Integration notes

- upstream: `psychds-curator`
- downstream: `repro-bundle`

## Citations

- cite PyMC / HDDM / ArviZ and the task-modeling literature used
