from __future__ import annotations

from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import platform
import sys
from typing import Any, Dict, Iterable, List

from jsonschema import Draft202012Validator
import yaml

from .flanker_demo import TRIAL_TYPES
from .paths import SCHEMAS_DIR
from .version import __version__


UNSUPPORTED_CAPABILITIES = [
    "HED annotation and HED validation",
    "Cognitive Atlas mappings",
    "Bayesian and drift-diffusion modeling",
    "preregistration exports",
    "RO-Crate packaging",
    "PROV packaging",
    "arbitrary behavioral study specifications beyond the canonical Flanker demo",
]


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def environment_lock() -> Dict[str, Any]:
    return {
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable_name": Path(sys.executable).name,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "packages": {
            "cogsci-skilllib": __version__,
            "jsonschema": package_version("jsonschema"),
            "PyYAML": package_version("PyYAML"),
        },
    }


def commands_script() -> str:
    return """#!/usr/bin/env sh
set -eu

PYTHON_BIN="${PYTHON_BIN:-python3}"
OUTPUT_DIR="${OUTPUT_DIR:-output/flanker-behavioral}"

"${PYTHON_BIN}" scripts/run_flanker_behavioral_slice.py \
  --study-spec examples/flanker-behavioral/study_spec.yaml \
  --output-dir "${OUTPUT_DIR}" \
  --validate-psychds auto

if command -v validate >/dev/null 2>&1; then
  validate "${OUTPUT_DIR}/psychds" --json > "${OUTPUT_DIR}/report/validation/psychds-validator.json"
fi
"""


def build_run_manifest(
    study_spec_reference: str,
    study_spec_sha256: str,
    study_title: str,
    demo_profile: Dict[str, Any],
    schedule_summary: Dict[str, Any],
    task_metadata: Dict[str, Any],
    psychds_metadata: Dict[str, Any],
    study_validation: Dict[str, Any],
    psychds_validation_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "runner": "scripts/run_flanker_behavioral_slice.py",
        "version": __version__,
        "study_spec": {
            "path": study_spec_reference,
            "sha256": study_spec_sha256,
            "title": study_title,
        },
        "supported_slice": {
            "name": "canonical-flanker-behavioral-demo",
            "task_generation": True,
            "psychds_curation": True,
            "reproducibility_bundle": True,
            "synthetic_demo_data": True,
        },
        "demo_profile": demo_profile,
        "trial_schedule": schedule_summary,
        "task_artifact": task_metadata,
        "psychds": psychds_metadata,
        "validation": {
            "study_spec": {
                "status": "passed" if study_validation["valid"] else "failed",
                "schema": study_validation["schema"],
            },
            "psychds": psychds_validation_summary,
            "report_bundle": {
                "status": "pending",
                "schema": "schemas/report-bundle.schema.json",
            },
        },
        "unsupported_requested_outputs": study_validation["unsupported_requested_outputs"],
        "unsupported_requested_standards": study_validation["unsupported_requested_standards"],
        "unsupported_capabilities": UNSUPPORTED_CAPABILITIES,
    }


def methods_markdown(
    study_title: str,
    study_spec_reference: str,
    study_spec_sha256: str,
    run_manifest: Dict[str, Any],
) -> str:
    schedule = run_manifest["trial_schedule"]
    participants = ", ".join(
        "{participant_id} ({mapping_variant})".format(**participant)
        for participant in run_manifest["demo_profile"]["participants"]
    )
    stimuli = ", ".join(trial_type["stimulus"] for trial_type in TRIAL_TYPES)
    timings = run_manifest["demo_profile"]["timing_ms"]
    unsupported_outputs = ", ".join(run_manifest["unsupported_requested_outputs"]) or "none"
    unsupported_standards = ", ".join(run_manifest["unsupported_requested_standards"]) or "none"

    return """# Methods

## Input and scope

This run used the study specification `{study_spec_reference}` (SHA-256 `{study_spec_sha256}`) for the study "{study_title}".
The implemented slice supports only the canonical behavioral Flanker demo path: jsPsych task generation, deterministic synthetic demo data generation, Psych-DS-aligned curation, and reproducibility bundle assembly.

## Task generation

The browser artifact was generated with jsPsych {jspsych_version} and `@jspsych/plugin-html-keyboard-response` {plugin_version}.
Each participant completed {trial_count} trials with balanced condition counts ({condition_counts}) and the fixed stimulus set {stimuli}.
The task used fixation {fixation} ms, response deadline {deadline} ms, and inter-trial interval {iti} ms.

## Synthetic demo data

The curated dataset is synthetic and deterministic; it is present only to exercise curation and reproducibility paths in CI and local demo runs.
Two synthetic participants were generated: {participants}.
No practice block, feedback block, adaptive logic, empirical recruitment, or inferential modeling was run in this milestone.

## Curation and validation

Trial tables were written into a Psych-DS-aligned dataset under `psychds/data/` with matching sidecar metadata and a global `dataset_description.json`.
Study-spec validation status: {study_status}.
Psych-DS validator status: {psychds_status}.

## Unsupported requests and standards

Unsupported requested outputs for this study spec: {unsupported_outputs}.
Unsupported requested standards for this study spec: {unsupported_standards}.
Unsupported capabilities still deferred in this milestone: {unsupported_capabilities}.

## Reproducibility artifacts

The bundle includes a machine-readable manifest, commands script, environment snapshot, checksums, study-spec validation, report-bundle validation, and a run manifest derived from runtime metadata.
""".format(
        study_spec_reference=study_spec_reference,
        study_spec_sha256=study_spec_sha256,
        study_title=study_title,
        jspsych_version=run_manifest["task_artifact"]["jspsych_assets"]["jspsych"],
        plugin_version=run_manifest["task_artifact"]["jspsych_assets"]["plugin_html_keyboard_response"],
        trial_count=schedule["trial_count"],
        condition_counts=", ".join(
            "{0}={1}".format(key, value) for key, value in schedule["condition_counts"].items()
        ),
        stimuli=stimuli,
        fixation=timings["fixation"],
        deadline=timings["response_deadline"],
        iti=timings["inter_trial_interval"],
        participants=participants,
        study_status=run_manifest["validation"]["study_spec"]["status"],
        psychds_status=run_manifest["validation"]["psychds"]["status"],
        unsupported_outputs=unsupported_outputs,
        unsupported_standards=unsupported_standards,
        unsupported_capabilities=", ".join(run_manifest["unsupported_capabilities"]),
    )


def report_markdown(
    study_spec_reference: str,
    run_manifest: Dict[str, Any],
) -> str:
    unsupported_outputs = run_manifest["unsupported_requested_outputs"]
    unsupported_standards = run_manifest["unsupported_requested_standards"]
    return """# Flanker Behavioral Slice Report

- Study spec: `{study_spec_reference}`
- Supported path executed: jsPsych task package, deterministic synthetic demo data, Psych-DS-aligned curation, reproducibility bundle
- Trial count per participant: {trial_count}
- Condition counts: {condition_counts}
- Psych-DS validation status: {psychds_status}
- Unsupported requested outputs: {unsupported_outputs}
- Unsupported requested standards: {unsupported_standards}
- Deferred capabilities: {unsupported_capabilities}

This report summarizes what actually ran. Synthetic data is labeled synthetic throughout the bundle and must not be interpreted as empirical participant data.
""".format(
        study_spec_reference=study_spec_reference,
        trial_count=run_manifest["trial_schedule"]["trial_count"],
        condition_counts=", ".join(
            "{0}={1}".format(key, value)
            for key, value in run_manifest["trial_schedule"]["condition_counts"].items()
        ),
        psychds_status=run_manifest["validation"]["psychds"]["status"],
        unsupported_outputs=", ".join(unsupported_outputs) or "none",
        unsupported_standards=", ".join(unsupported_standards) or "none",
        unsupported_capabilities=", ".join(run_manifest["unsupported_capabilities"]),
    )


def report_bundle_manifest() -> Dict[str, Any]:
    return {
        "report": "report/report.md",
        "methods": "report/methods.md",
        "commands": "report/commands.sh",
        "environment": "report/environment.lock.yml",
        "checksums": "report/checksums.sha256",
        "validation": {
            "psychds": "report/validation/psychds-validator.json",
            "bids": None,
            "hed": None,
        },
        "provenance": {
            "ro_crate": None,
            "prov": None,
        },
        "preregistration": None,
        "run_manifest": "report/provenance/run_manifest.json",
    }


def validate_report_bundle(manifest: Dict[str, Any]) -> Dict[str, Any]:
    schema_path = SCHEMAS_DIR / "report-bundle.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = [
        {
            "message": error.message,
            "path": list(error.path),
        }
        for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path))
    ]
    return {
        "schema": str(schema_path.relative_to(schema_path.parents[1])),
        "valid": not errors,
        "errors": errors,
    }


def write_environment_lock(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")


def iter_output_files(output_root: Path) -> Iterable[Path]:
    for file_path in sorted(output_root.rglob("*")):
        if file_path.is_file():
            yield file_path


def write_checksums(output_root: Path, checksums_path: Path) -> None:
    lines: List[str] = []
    for file_path in iter_output_files(output_root):
        relative_path = file_path.relative_to(output_root)
        if relative_path == Path("report/checksums.sha256"):
            continue
        digest = sha256(file_path.read_bytes()).hexdigest()
        lines.append("{digest}  {path}".format(digest=digest, path=relative_path.as_posix()))
    checksums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
