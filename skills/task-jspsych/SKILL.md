---
name: task-jspsych
description: Generate the canonical Flanker jsPsych task package from a structured study specification using local vendored assets.
version: 0.1.0
status: supported-demo
tags:
  - cognitive-science
  - reproducibility
modality:
  - behavioral
standards:
  - jsPsych
trigger_keywords:
  - jspsych
  - behavioral task
  - browser experiment
  - flanker
  - stroop
dependencies:
  python: ">=3.11"
  packages:
    - PyYAML
    - jsonschema
---

# task-jspsych

## Why this exists

Researchers often rebuild common tasks from scratch, creating inconsistent data fields, event labels, and metadata. This skill should generate a deterministic jsPsych package from a study spec so the downstream curation and analysis layers can rely on stable structure.

## Supported use cases

- the canonical Flanker behavioral demo at `examples/flanker-behavioral/study_spec.yaml`
- offline-capable browser tasks rendered with local vendored jsPsych assets
- deterministic 160-trial schedules with fixed stimulus templates and explicit response mappings
- task metadata outputs designed for downstream Psych-DS curation in this repository

## Unsupported or deferred cases

- arbitrary behavioral study specifications
- Cognitive Atlas mappings
- adaptive tasks with complex online optimization
- hardware-timed paradigms requiring lab-specific devices
- claims of psychometric validation beyond the study specification
- live browser-run data ingestion into the curated dataset path
- standalone HED annotation without the downstream `hed-annotator` step

## Inputs

| Input | Format | Required | Notes |
|---|---|---:|---|
| study spec | YAML / JSON | yes | structured task specification |
| validate mode | CLI flag | no | affects downstream validator behavior only |

## Workflow

1. Parse the study specification.
2. Validate it against `schemas/study-spec.schema.yaml` and the canonical Flanker profile for this milestone.
3. Generate a deterministic 160-trial Flanker schedule and task metadata.
4. Render `index.html`, `task.js`, `trials.json`, and local jsPsych assets into an offline-capable task package.
5. Emit metadata for downstream HED annotation and Psych-DS curation.

## Validation

- schema validation for the study spec
- deterministic trial-count and condition-count checks
- task artifact file-contract checks in CI
- downstream HED validation is available for the canonical Flanker slice through `hed-annotator`

## Demo mode

Run:

```bash
python3 scripts/run_flanker_behavioral_slice.py \
  --study-spec examples/flanker-behavioral/study_spec.yaml \
  --output-dir output/flanker-behavioral \
  --validate-psychds auto \
  --validate-hed auto
```

## Outputs

```text
output/
├── task/
│   ├── index.html
│   ├── task.js
│   ├── trials.json
│   ├── task_metadata.json
│   └── jspsych/
└── metadata/
    ├── trial_schedule.json
    ├── trial_schedule_summary.json
    └── column_definitions.json
```

## Safety

- do not claim the generated task is scientifically validated on its own
- do not add remote telemetry by default
- keep demos offline-compatible
- keep synthetic demo data clearly separate from empirical browser-run data

## Integration notes

- upstream: study spec
- downstream: `hed-annotator`, `psychds-curator`, `repro-bundle`

## Citations

- cite jsPsych and the html-keyboard-response plugin
- note that Cognitive Atlas support remains deferred in this milestone
