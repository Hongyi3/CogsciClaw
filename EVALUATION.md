# Evaluation plan

## Purpose

This project should be evaluated as research infrastructure, not as a demo.

The evaluation program should answer:

1. does the system produce standards-compliant artifacts?
2. can others rerun the outputs?
3. do the generated tasks and analyses match the study specification?
4. are model diagnostics and reports adequate for scientific review?
5. does the workflow reduce effort without sacrificing rigor?

## Benchmark dimensions

### A. Standards compliance

Metrics:

- Psych-DS validator pass rate
- BIDS validator pass rate
- HED validation pass rate

### B. Reproducibility

Metrics:

- rerun success from clean environment
- checksum stability where deterministic
- bundle completeness

### C. Task fidelity

Metrics:

- condition counts match specification
- timing and randomization constraints preserved
- event labels mapped correctly

### D. Modeling reliability

Metrics:

- convergence diagnostics
- posterior predictive checks
- parameter recovery on synthetic data
- model-comparison output availability

### E. Reporting completeness

Metrics:

- methods coverage
- provenance coverage
- validator outputs attached
- confirmatory/exploratory distinction preserved

### F. Usability

Metrics:

- time to first successful demo
- setup failure rate
- number of manual edits required

## Candidate benchmark sources

- public Psych-DS examples
- BIDS example datasets
- OpenNeuro-compatible public datasets
- MNE sample datasets
- future DANDI examples for NWB work

## Evaluation policy

Before making strong public claims:

- preregister benchmark criteria
- freeze benchmark datasets / versions
- specify success thresholds
- distinguish qualitative demos from quantitative benchmarks

## Minimum public benchmark package

- benchmark registry
- exact dataset references
- commands used
- expected outputs
- scoring rubric
- limitations

