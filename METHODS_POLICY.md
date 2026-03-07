# Methods policy

## Prime directive

Do not guess.

No skill may fabricate:

- preprocessing steps
- statistical results
- task details
- event semantics
- reporting language
- standards compliance

All claims must be traceable to one of:

- executable code
- runtime metadata
- validator output
- explicitly cited source material
- a clearly labeled human-authored assumption

## Required method behavior

### 1. Standards first

If a community standard exists, use it or explain why it is not applicable.

### 2. Runtime-derived reporting

Methods prose must be synthesized from actual run metadata, parameter files, and validator outputs—not from model memory.

### 3. Explicit confirmatory vs exploratory distinction

If a workflow contains preregistered analyses and exploratory analyses, the report must label them separately.

### 4. Reproducibility is part of the result

A workflow is incomplete until it emits:

- commands
- environment snapshot
- checksums
- run manifest
- validation artifacts
- output inventory

### 5. Human review remains mandatory where needed

The system must clearly identify decisions that still require human judgment, including:

- ethics / consent constraints
- task validity
- interpretation of cognitive constructs
- inclusion/exclusion rules
- manuscript-level scientific claims

## Required sections for every SKILL.md

- purpose
- supported use cases
- unsupported use cases
- inputs
- workflow
- outputs
- validation
- demo mode
- safety
- citations
- integration notes

## Minimum release gate for a supported skill

A supported skill must have:

- deterministic demo
- one canonical test case
- machine-readable output contract
- validator pathway where relevant
- provenance emission
- cited methods note
- failure modes note

## Disallowed patterns

- “supports BIDS” with no validator step
- “Bayesian model” with no diagnostics output
- “publication-ready methods” not derived from actual metadata
- silent fallbacks that change scientific meaning
- hidden remote calls in a supposedly local-first workflow

