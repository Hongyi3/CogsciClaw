# Master plan

## 1. Product definition

Build a **cognitive-science-native research workflow system** that preserves the strengths of ClawBio’s architecture—modular skills, orchestration, local-first execution, reproducibility bundles, and agent-facing repository metadata—while replacing the domain layer with the standards and tools cognitive science already trusts.

This project should be positioned as:

> An open-source skill library that converts structured or natural-language research requests into standards-compliant, reproducible, publication-ready cognitive-science workflows.

The unit of value is **not** a chat response.  
The unit of value is a **research object**.

A successful run should generate:

- task code or study materials
- standards-compliant dataset structure
- event annotations and metadata
- validation records
- analysis code
- figures and tables
- methods text generated from runtime metadata
- preregistration-ready materials
- provenance and citation metadata

## 2. Scope strategy

### Recommended v1 wedge

Start with:

- behavioral experiments
- structured questionnaires / assessments
- event annotation
- Bayesian and drift-diffusion modeling
- reproducibility packaging

Then expand to:

- EEG / MEG
- broader BIDS-native neuroimaging orchestration
- later: fMRI wrappers, neurophysiology/NWB, meta-analysis

### Why this scope wins

This wedge has the best balance of:

- strong existing standards
- broad relevance across cognitive science
- tractable open-source implementation
- clear academic differentiation
- realistic path to external adoption

### Non-goals for v1

Do **not** try to ship all of cognitive science in the first release.

Avoid:

- custom data standards
- a public third-party skill marketplace
- bespoke fMRI preprocessing
- unsupported “AI interpretation” features that cannot be traced to code, validators, or citations

## 3. System architecture

```text
User request / structured study spec
                │
                ▼
      CogSci Orchestrator
  (routing + planning + assembly)
                │
    ┌───────────┼───────────────────────┐
    │           │           │           │
    ▼           ▼           ▼           ▼
 task-*     curator-*   model-*    repro-bundle
    │           │           │           │
    └───────────┼───────────┼───────────┘
                ▼
       Standards / validation layer
 (Psych-DS, BIDS, HED, ReproSchema, NWB)
                ▼
          Output / publication layer
 (report, methods, figures, checksums,
  RO-Crate, preregistration, citations)
```

### Architectural rules

1. Every skill does one scientific job well.
2. Every skill can run standalone.
3. The orchestrator composes skills but never hides what ran.
4. Every public capability must map to a real validator or executable pathway.
5. Public docs must be generated from a single source of truth where possible.

## 4. Initial skill lineup

### Core v1 skills

1. `task-jspsych`
   - generate browser-based behavioral tasks
   - enforce deterministic trial structure
   - export data dictionaries and event logs

2. `task-psychopy`
   - generate lab-based or hybrid tasks
   - support Builder-first authoring where possible
   - export experiment assets and settings

3. `psychds-curator`
   - normalize behavioral data into Psych-DS
   - generate dictionaries and validator outputs

4. `bids-curator`
   - prepare BIDS-compatible intake for EEG/MEG and other BIDS-native modalities
   - generate sidecars and dataset metadata

5. `hed-annotator`
   - translate event semantics into machine-actionable HED strings
   - validate event annotations

6. `ddm-bayes`
   - fit Bayesian models for RT/accuracy data
   - support hierarchical DDM and simpler Bayesian baselines
   - emit diagnostics and model-comparison outputs

7. `eeg-meg-pipeline`
   - orchestrate MNE-BIDS ingestion and MNE-based preprocessing
   - produce QC summaries and reporting metadata

8. `repro-bundle`
   - assemble the final report bundle
   - emit checksums, environments, provenance, citations, and preregistration exports

### Later-phase skills

- `questionnaire-reproschema`
- `fmri-prep-wrapper`
- `nwb-curator`
- `nimare-meta`
- `meta-analytic-decoder`
- `registered-report-packager`

## 5. Quality bar

Every skill must satisfy all of the following before it can be called “supported”:

### 5.1 Methods

- a concise, citable method description
- explicit assumptions
- supported and unsupported use cases
- named standards and validators

### 5.2 Demo mode

- deterministic demo input
- no private data required
- small enough to run in CI

### 5.3 Golden tests

- at least one canonical input
- expected machine-readable outputs
- validator results where applicable

### 5.4 Provenance

- exact command invocation
- software versions
- environment snapshot
- checksums
- run manifest
- structured provenance metadata

### 5.5 Failure transparency

- what ran
- what did not run
- which assumptions were made
- what still requires human judgment

## 6. Research positioning

The project should be positioned as:

- infrastructure for reproducible cognitive science
- a reference implementation of open-science workflows
- a bridge between agentic coding and community standards
- a platform for generating citable, rerunnable research objects

This makes the project legible to:

- labs
- methods reviewers
- software reviewers
- JOSS
- open-science communities
- design-partner institutions

## 7. Evaluation program

Evaluation should be preregistered before major public claims.

### Core evaluation dimensions

1. standards compliance
   - Psych-DS / BIDS / HED validator pass rates

2. rerun fidelity
   - whether the report bundle reproduces the same outputs from a clean environment

3. task fidelity
   - whether generated task structure matches the study specification

4. model reliability
   - parameter recovery, convergence, diagnostics, posterior predictive performance

5. reporting completeness
   - methods + QC + provenance coverage

6. user effort
   - time to first successful demo
   - time from study spec to usable report

### Minimum benchmark pool

- one behavioral-only study
- one questionnaire-heavy study
- one EEG oddball or ERP study
- one public BIDS example
- one public Psych-DS example
- one open neurophysiology example for future NWB work

## 8. Governance and trust

### Core policy

Start with a **reviewed core repository**, not an open marketplace.

### Maintainership

Create a small steering group:

- one behavioral methods lead
- one EEG/MEG lead
- one Bayesian modeling lead
- one open-science / reproducibility lead
- one research software engineering lead

### Required top-level policies

- governance
- contributing
- code of conduct
- methods policy
- threat model
- security policy
- authorship and credit policy
- review policy

## 9. Publication and visibility

### Required infrastructure from the first public release

- `CITATION.cff`
- `codemeta.json`
- Zenodo integration
- clear release notes
- benchmark docs
- examples that run on public data
- docs site or GitHub Pages
- issue templates, PR template, and Discussions

### Scholarly outputs

1. preprint describing architecture, benchmarks, and rationale
2. JOSS software paper
3. downstream methods or domain demonstration papers
4. workshop/tutorial material for conference adoption

## 10. Codex execution strategy

This repo is scaffolded so Codex can contribute effectively.

### Codex should always start by reading

- `AGENTS.md`
- `VISION.md`
- `METHODS_POLICY.md`
- `MASTER_PLAN.md`
- `ROADMAP.md`
- target `SKILL.md`

### Codex’s first implementation sequence

1. make the repo internally consistent
2. finalize the catalog + doc generation path
3. implement the study spec schema
4. implement the reproducibility bundle schema
5. build `task-jspsych` demo for the Flanker example
6. build `psychds-curator` for the Flanker output
7. build `hed-annotator`
8. build `ddm-bayes`
9. generate report + prereg bundle
10. only then expand to EEG/MEG

### Definition of done for v1.0

- one behavioral vertical slice runs end to end
- one EEG/MEG slice runs end to end
- validator outputs are bundled
- methods text is metadata-derived
- demos are reproducible on clean machines
- CI is green
- public docs are generated from catalog metadata
- repository is ready for external contributors and JOSS review

## 11. Strongest recommendation

Do not optimize for breadth first.

Optimize for becoming the **reference implementation for AI-native, standards-first, reproducible cognitive-science workflows**.

That is the path to academic credibility, durable influence, and high-quality open-source adoption.

