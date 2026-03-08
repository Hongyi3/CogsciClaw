from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any, Dict, List, Tuple


BIDS_VERSION = "1.11.1"
BIDS_VALIDATOR_TOOL_NAME = "bids-validator"
PLACEHOLDER_ARTIFACT_TYPE = "cogsci-skilllib-bids-intake-placeholder"
INTAKE_ARTIFACT_TYPE = "cogsci-skilllib-bids-intake-demo"
UNSUPPORTED_INTAKE_ARTIFACTS = [
    "empirical EEG acquisition files",
    "events.tsv timing files",
    "channels.tsv metadata",
    "electrodes.tsv metadata",
    "HED annotations",
    "MNE-BIDS conversion artifacts",
    "MNE preprocessing outputs",
]


def _json_dump(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _task_label(task_name: str) -> str:
    return task_name.replace("_", "")


def _placeholder_subject_ids(target_n: int) -> List[str]:
    return [f"sub-placeholder{index:02d}" for index in range(1, target_n + 1)]


def _dataset_description(
    study_spec_reference: str,
    study_spec_sha256: str,
) -> Dict[str, Any]:
    return {
        "Name": "Auditory oddball EEG intake placeholder dataset",
        "BIDSVersion": BIDS_VERSION,
        "DatasetType": "study",
        "License": "CC0-1.0",
        "Authors": ["cogsci-skilllib"],
        "Acknowledgements": (
            "Deterministic placeholder-only BIDS intake tree generated for the canonical auditory "
            "oddball EEG demo. No empirical EEG recordings are included."
        ),
        "HowToAcknowledge": (
            "Review the checked-in oddball study spec, the emitted validation artifact, and local "
            "privacy requirements before using this intake pattern outside the demo."
        ),
        "ReferencesAndLinks": [
            "Source study spec: {reference} (SHA-256 {digest})".format(
                reference=study_spec_reference,
                digest=study_spec_sha256,
            ),
        ],
        "Funding": [
            "No funding metadata is attached to this deterministic demo artifact.",
        ],
        "EthicsApprovals": [
            "Not applicable for the placeholder demo tree; real studies require local ethics review.",
        ],
    }


def _participants_metadata() -> Dict[str, Any]:
    return {
        "participant_id": {
            "Description": "Deterministic placeholder participant identifier for the canonical oddball demo intake.",
        },
        "placeholder_status": {
            "Description": "Whether the participant row is a placeholder-only metadata stub.",
            "Levels": {
                "placeholder_metadata_only": "No empirical participant recording is present in the intake tree.",
            },
        },
        "contains_empirical_data": {
            "Description": "Whether the intake tree contains empirical EEG data for this participant.",
            "Levels": {
                "false": "The participant path contains placeholder metadata only.",
            },
        },
    }


def _placeholder_file_payload(
    participant_id: str,
    study_title: str,
    task_name: str,
    study_spec_reference: str,
    study_spec_sha256: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": PLACEHOLDER_ARTIFACT_TYPE,
        "participant_id": participant_id,
        "study_title": study_title,
        "task": _task_label(task_name),
        "modality": "eeg",
        "placeholder_only": True,
        "contains_empirical_data": False,
        "requires_human_completion": True,
        "source_study_spec": {
            "path": study_spec_reference,
            "sha256": study_spec_sha256,
        },
        "notes": [
            "No empirical acquisition file is present in this placeholder artifact.",
            "Channel layouts, recording parameters, and event timing remain unspecified in the checked-in demo inputs.",
            "Local privacy review is required before substituting real participant data.",
        ],
    }


def _intake_readme(study_title: str, participant_count: int) -> str:
    return """# Canonical Oddball BIDS Intake

Study: {study_title}
Participants represented: {participant_count}

This tree is a deterministic BIDS-aligned intake demo for the canonical auditory oddball EEG study spec.
Every participant artifact in this tree is placeholder-only metadata.
No empirical EEG recordings, channel metadata, electrode locations, or event timing files are included.
Real studies still require local privacy review, acquisition metadata completion, and validator review.
""".format(
        study_title=study_title,
        participant_count=participant_count,
    )


def _intake_manifest(
    study_title: str,
    study_spec_reference: str,
    study_spec_sha256: str,
    placeholder_subject_ids: List[str],
    placeholder_files: List[str],
) -> Dict[str, Any]:
    return {
        "artifact_type": INTAKE_ARTIFACT_TYPE,
        "supported_profile": "canonical-auditory-oddball-bids-intake-demo",
        "intake_root": "bids-intake",
        "study": {
            "title": study_title,
            "task_name": "auditory_oddball",
            "modality": "eeg",
        },
        "study_spec": {
            "path": study_spec_reference,
            "sha256": study_spec_sha256,
        },
        "participants": {
            "target_n": len(placeholder_subject_ids),
            "placeholder_subject_ids": placeholder_subject_ids,
        },
        "placeholder_policy": {
            "placeholder_only": True,
            "contains_empirical_data": False,
            "requires_human_completion": True,
        },
        "files": {
            "dataset_description": "bids-intake/dataset_description.json",
            "readme": "bids-intake/README.md",
            "participants_tsv": "bids-intake/participants.tsv",
            "participants_json": "bids-intake/participants.json",
            "placeholder_files": placeholder_files,
        },
        "unsupported_artifacts": UNSUPPORTED_INTAKE_ARTIFACTS,
    }


def write_bids_intake(
    bids_root: Path,
    normalized_spec: Dict[str, Any],
    study_spec_reference: str,
    study_spec_sha256: str,
) -> Dict[str, Any]:
    bids_root.mkdir(parents=True, exist_ok=True)
    study_title = normalized_spec["study"]["title"]
    task_name = normalized_spec["design"]["task_name"]
    participant_count = normalized_spec["participants"]["target_n"]
    participant_ids = _placeholder_subject_ids(participant_count)

    _json_dump(
        bids_root / "dataset_description.json",
        _dataset_description(study_spec_reference, study_spec_sha256),
    )
    (bids_root / "README.md").write_text(
        _intake_readme(study_title, participant_count),
        encoding="utf-8",
    )

    participant_rows = [
        {
            "participant_id": participant_id,
            "placeholder_status": "placeholder_metadata_only",
            "contains_empirical_data": "false",
        }
        for participant_id in participant_ids
    ]
    _write_tsv(
        bids_root / "participants.tsv",
        participant_rows,
        ["participant_id", "placeholder_status", "contains_empirical_data"],
    )
    _json_dump(bids_root / "participants.json", _participants_metadata())

    placeholder_files: List[str] = []
    for participant_id in participant_ids:
        relative_file = (
            f"bids-intake/{participant_id}/eeg/{participant_id}_task-{_task_label(task_name)}_intake-placeholder.json"
        )
        file_path = bids_root.parent / relative_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        _json_dump(
            file_path,
            _placeholder_file_payload(
                participant_id=participant_id,
                study_title=study_title,
                task_name=task_name,
                study_spec_reference=study_spec_reference,
                study_spec_sha256=study_spec_sha256,
            ),
        )
        placeholder_files.append(relative_file)

    intake_manifest = _intake_manifest(
        study_title=study_title,
        study_spec_reference=study_spec_reference,
        study_spec_sha256=study_spec_sha256,
        placeholder_subject_ids=participant_ids,
        placeholder_files=placeholder_files,
    )
    _json_dump(bids_root / "intake_manifest.json", intake_manifest)

    return {
        "intake_root": "bids-intake",
        "dataset_description": "bids-intake/dataset_description.json",
        "readme": "bids-intake/README.md",
        "participants_tsv": "bids-intake/participants.tsv",
        "participants_json": "bids-intake/participants.json",
        "intake_manifest": "bids-intake/intake_manifest.json",
        "placeholder_files": sorted(placeholder_files),
        "placeholder_subject_ids": participant_ids,
        "task_name": _task_label(task_name),
        "participant_count": participant_count,
        "placeholder_only": True,
        "contains_empirical_data": False,
        "bids_version": BIDS_VERSION,
        "dataset_type": "study",
        "unsupported_artifacts": UNSUPPORTED_INTAKE_ARTIFACTS,
    }


def run_bids_validator(
    bids_root: Path,
    mode: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    validator_binary = shutil.which(BIDS_VALIDATOR_TOOL_NAME)
    dataset_root = "bids-intake"
    command = [validator_binary, str(bids_root), "--json"] if validator_binary else None
    base_summary = {
        "status": "not_run",
        "tool": BIDS_VALIDATOR_TOOL_NAME,
        "requested_mode": mode,
        "command_available": bool(validator_binary),
        "dataset_root": dataset_root,
    }

    if mode == "never":
        reason = "Validation disabled by --validate-bids never."
        return (
            {
                **base_summary,
                "reason": reason,
                "validator_output": None,
            },
            {
                **base_summary,
                "reason": reason,
            },
        )

    if validator_binary is None:
        if mode == "always":
            raise RuntimeError(
                "bids-validator command not found but --validate-bids always was requested."
            )
        reason = "bids-validator command not found on PATH."
        return (
            {
                **base_summary,
                "reason": reason,
                "validator_output": None,
            },
            {
                **base_summary,
                "reason": reason,
            },
        )

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    parsed_output = None
    output_format = "none"
    if stdout:
        try:
            parsed_output = json.loads(stdout)
            output_format = "json"
        except json.JSONDecodeError:
            output_format = "invalid_json"

    status = "passed" if completed.returncode == 0 else "failed"
    artifact = {
        "status": status,
        "tool": BIDS_VALIDATOR_TOOL_NAME,
        "requested_mode": mode,
        "command_available": True,
        "dataset_root": dataset_root,
        "command": command,
        "returncode": completed.returncode,
        "output_format": output_format,
        "validator_output": parsed_output,
    }
    if stdout:
        artifact["stdout"] = stdout
    if stderr:
        artifact["stderr"] = stderr

    summary = {
        "status": status,
        "tool": BIDS_VALIDATOR_TOOL_NAME,
        "requested_mode": mode,
        "command_available": True,
        "dataset_root": dataset_root,
        "returncode": completed.returncode,
    }
    return artifact, summary
