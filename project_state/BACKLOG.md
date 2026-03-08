# Backlog

This queue records milestone order, current status, dependency notes, and why the sequence supports the most rigorous path to v1.

| Order | Milestone | Title | Phase | Status | Dependencies | Rationale for sequencing |
|---|---|---|---|---|---|---|
| 1 | P0 | charter and repository foundation | Phase 0 | completed | none | Establish the repo policies, catalog generation, and CI needed to review later scientific claims. |
| 2 | M1A | deterministic Flanker behavioral slice | Phase 1 | completed | P0 | Deliver one narrow implemented slice before broader standards and analysis work. |
| 3 | M1B | HED annotation and validation for Flanker | Phase 1 | completed | M1A | Closed the immediate HED standards gap in the canonical behavioral slice before moving into modeling. |
| 4 | M1C | Bayesian / DDM analysis with diagnostics and methods text | Phase 1 | completed | M1A, M1B | Closed after verifying the supported Bayesian baseline and diagnostics on a healthy local Python >=3.11 runtime while keeping DDM runtime probing honest. |
| 5 | M1D | preregistration and provenance packaging for the Flanker slice | Phase 1 | completed | M1C | Finished the behavioral vertical slice with deterministic preregistration output and machine-readable provenance packaging after the supported analysis path became real. |
| 6 | M2A | BIDS-curated EEG/MEG oddball intake slice | Phase 2 | completed | M1D | Started EEG/MEG expansion with the narrowest credible intake slice after the Phase 1 behavioral work became reviewable and reproducible. |
| 7 | M2B | EEG/MEG preprocessing, QC, and report integration | Phase 2 | in progress | M2A | Extend the neuro slice after BIDS intake exists, while keeping placeholder-aware `not_run` semantics explicit until empirical signal files are available. |
| 8 | M3A | benchmark preregistration and first archived public release | Phase 3 | planned | M1D, M2B | Move to public benchmark and release work only after both the behavioral and neuro slices justify external claims. |
