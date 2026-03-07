---
name: ddm-bayes
description: Fit Bayesian and hierarchical drift-diffusion models with diagnostics and posterior predictive checks.
version: 0.1.0
status: scaffold
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
  packages: []
---

# ddm-bayes

## Why this exists

Behavioral tasks often stop at summary statistics even when the scientific question is about latent decision processes. This skill should fit reproducible Bayesian models and emit diagnostics that make the modeling workflow inspectable.

## Supported use cases

- Bayesian baseline models for RT/accuracy
- hierarchical DDM workflows where supported
- diagnostics and posterior predictive checks

## Unsupported or deferred cases

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
3. Fit configured Bayesian or DDM model.
4. Emit summaries, diagnostics, and posterior predictive checks.
5. Prepare methods metadata for the report bundle.

## Validation

- convergence diagnostics
- posterior predictive checks
- required-column checks before fitting

## Demo mode

Fit a small deterministic model on public or synthetic Flanker demo data.

## Outputs

```text
output/
├── model/
│   ├── summary.csv
│   ├── diagnostics.json
│   ├── posterior_predictive.nc
│   └── traces.nc
├── figures/
└── report.md
```

## Safety

- do not hide convergence failures
- do not oversell psychological interpretation of latent parameters

## Integration notes

- upstream: `psychds-curator`
- downstream: `repro-bundle`

## Citations

- cite PyMC / HDDM / ArviZ and the task-modeling literature used

