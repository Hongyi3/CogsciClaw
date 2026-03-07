from __future__ import annotations

import csv
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .paths import SCHEMAS_DIR


HED_SCHEMA_VERSION = "8.4.0"
HED_SCHEMA_PATH = SCHEMAS_DIR / "hed" / "HED8.4.0.xml"
HED_MAPPING_RULES_PATH = SCHEMAS_DIR / "hed" / "flanker-demo-events.json"
HED_TOOL_NAME = "hedtools-python"
EVENT_COLUMNS = [
    "onset",
    "duration",
    "trial_index",
    "event_type",
    "condition",
    "trial_type",
    "stimulus",
    "target_direction",
    "flanker_direction",
    "correct_direction",
    "response_direction",
    "correct_response_key",
    "response_key",
    "accuracy",
    "accuracy_label",
    "mapping_variant",
    "synthetic",
    "HED",
]


def _json_dump(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVENT_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _seconds(milliseconds: int | float) -> float:
    return float(milliseconds) / 1000.0


def _format_seconds(value: float) -> str:
    return f"{value:.3f}"


def _relative_output_path(path: str) -> str:
    return f"events/{path}"


def _load_mapping_rules(mapping_path: Path = HED_MAPPING_RULES_PATH) -> Dict[str, Any]:
    return json.loads(mapping_path.read_text(encoding="utf-8"))


def _opposite_direction(direction: str) -> str:
    return "right" if direction == "left" else "left"


def _response_direction(row: Dict[str, Any]) -> str:
    if row["response_key"] == row["correct_response_key"]:
        return str(row["correct_direction"])
    return _opposite_direction(str(row["correct_direction"]))


def _accuracy_label(row: Dict[str, Any]) -> str:
    return "correct" if int(row["accuracy"]) == 1 else "incorrect"


def _stimulus_hed(row: Dict[str, Any], rules: Dict[str, Any]) -> str:
    return ", ".join(
        [
            rules["event_types"]["stimulus"]["hed_prefix"],
            rules["trial_type_tags"][row["trial_type"]],
        ]
    )


def _response_hed(row: Dict[str, Any], response_direction: str, rules: Dict[str, Any]) -> str:
    return ", ".join(
        [
            rules["event_types"]["response"]["hed_prefix"],
            rules["accuracy_tags"][_accuracy_label(row)],
            rules["direction_tags"][response_direction],
        ]
    )


def build_hed_sidecar(mapping_rules: Dict[str, Any]) -> Dict[str, Any]:
    return dict(mapping_rules["sidecar"])


def build_participant_event_rows(
    participant_table: Dict[str, Any],
    mapping_rules: Dict[str, Any],
    demo_profile: Dict[str, Any],
) -> List[Dict[str, Any]]:
    fixation_seconds = _seconds(demo_profile["timing_ms"]["fixation"])
    inter_trial_interval_seconds = _seconds(demo_profile["timing_ms"]["inter_trial_interval"])
    rows: List[Dict[str, Any]] = []
    current_time = 0.0

    for trial_row in participant_table["rows"]:
        rt_seconds = _seconds(int(trial_row["rt_ms"]))
        stimulus_onset = current_time + fixation_seconds
        response_onset = stimulus_onset + rt_seconds
        response_direction = _response_direction(trial_row)
        accuracy_label = _accuracy_label(trial_row)
        shared = {
            "trial_index": str(trial_row["trial_index"]),
            "condition": str(trial_row["condition"]),
            "trial_type": str(trial_row["trial_type"]),
            "stimulus": str(trial_row["stimulus"]),
            "target_direction": str(trial_row["target_direction"]),
            "flanker_direction": str(trial_row["flanker_direction"]),
            "correct_direction": str(trial_row["correct_direction"]),
            "correct_response_key": str(trial_row["correct_response_key"]),
            "mapping_variant": str(trial_row["mapping_variant"]),
            "synthetic": str(trial_row["synthetic"]),
        }

        rows.append(
            {
                **shared,
                "onset": _format_seconds(stimulus_onset),
                "duration": _format_seconds(rt_seconds),
                "event_type": "stimulus",
                "response_direction": "",
                "response_key": "",
                "accuracy": "",
                "accuracy_label": "",
                "HED": _stimulus_hed(trial_row, mapping_rules),
            }
        )
        rows.append(
            {
                **shared,
                "onset": _format_seconds(response_onset),
                "duration": _format_seconds(0.0),
                "event_type": "response",
                "response_direction": response_direction,
                "response_key": str(trial_row["response_key"]),
                "accuracy": str(trial_row["accuracy"]),
                "accuracy_label": accuracy_label,
                "HED": _response_hed(trial_row, response_direction, mapping_rules),
            }
        )
        current_time = response_onset + inter_trial_interval_seconds

    return rows


def write_hed_events(
    events_dir: Path,
    synthetic_tables: List[Dict[str, Any]],
    demo_profile: Dict[str, Any],
) -> Dict[str, Any]:
    events_dir.mkdir(parents=True, exist_ok=True)
    mapping_rules = _load_mapping_rules()
    sidecar_filename = "flanker_events.json"
    sidecar_path = events_dir / sidecar_filename
    _json_dump(sidecar_path, build_hed_sidecar(mapping_rules))

    participant_event_files: List[str] = []
    event_rows_per_file: Dict[str, int] = {}
    for table in synthetic_tables:
        filename = "participant-{participant}_session-{session}_events.tsv".format(
            participant=table["participant_id"],
            session=table["session_id"],
        )
        event_rows = build_participant_event_rows(
            participant_table=table,
            mapping_rules=mapping_rules,
            demo_profile=demo_profile,
        )
        _write_tsv(events_dir / filename, event_rows)
        relative_path = _relative_output_path(filename)
        participant_event_files.append(relative_path)
        event_rows_per_file[relative_path] = len(event_rows)

    return {
        "events_root": "events",
        "mapping_rules": "schemas/hed/flanker-demo-events.json",
        "schema_path": "schemas/hed/HED8.4.0.xml",
        "schema_version": HED_SCHEMA_VERSION,
        "sidecar": _relative_output_path(sidecar_filename),
        "participant_event_files": sorted(participant_event_files),
        "event_rows_per_file": dict(sorted(event_rows_per_file.items())),
        "rows_per_trial": 2,
    }


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def _load_hed_runtime() -> Dict[str, Any] | None:
    try:
        from hed import Sidecar, TabularInput, load_schema
    except ImportError:
        return None

    return {
        "Sidecar": Sidecar,
        "TabularInput": TabularInput,
        "load_schema": load_schema,
        "version": _package_version("hedtools"),
    }


def run_hed_validator(
    output_dir: Path,
    hed_metadata: Dict[str, Any],
    mode: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    runtime = _load_hed_runtime()
    checked_files = [hed_metadata["sidecar"], *hed_metadata["participant_event_files"]]
    base_summary = {
        "tool": HED_TOOL_NAME,
        "requested_mode": mode,
        "tool_available": bool(runtime),
        "schema_path": hed_metadata["schema_path"],
        "schema_version": hed_metadata["schema_version"],
        "checked_files": checked_files,
    }

    if mode == "never":
        artifact = {
            "status": "not_run",
            "tool": HED_TOOL_NAME,
            "schema_path": hed_metadata["schema_path"],
            "schema_version": hed_metadata["schema_version"],
            "reason": "Validation disabled by --validate-hed never.",
            "checked_files": checked_files,
        }
        return artifact, {**base_summary, "status": "not_run", "reason": artifact["reason"]}

    if runtime is None:
        if mode == "always":
            raise RuntimeError("hedtools package not found but --validate-hed always was requested.")
        artifact = {
            "status": "not_run",
            "tool": HED_TOOL_NAME,
            "schema_path": hed_metadata["schema_path"],
            "schema_version": hed_metadata["schema_version"],
            "reason": "hedtools package not installed.",
            "checked_files": checked_files,
        }
        return artifact, {**base_summary, "status": "not_run", "reason": artifact["reason"]}

    try:
        sidecar_path = output_dir / hed_metadata["sidecar"]
        schema = runtime["load_schema"](HED_SCHEMA_PATH.as_posix())
        sidecar = runtime["Sidecar"](sidecar_path.as_posix(), name=sidecar_path.name)
        sidecar_issues = sidecar.validate(schema, name=sidecar_path.name)

        file_results = []
        total_issues = len(sidecar_issues)
        for relative_path in hed_metadata["participant_event_files"]:
            event_path = output_dir / relative_path
            tabular_input = runtime["TabularInput"](
                file=event_path.as_posix(),
                sidecar=sidecar,
                name=event_path.name,
            )
            issues = tabular_input.validate(schema, name=event_path.name)
            total_issues += len(issues)
            file_results.append(
                {
                    "file": relative_path,
                    "issue_count": len(issues),
                    "issues": issues,
                }
            )

        status = "passed" if total_issues == 0 else "failed"
        artifact = {
            "status": status,
            "tool": HED_TOOL_NAME,
            "tool_version": runtime["version"],
            "schema_path": hed_metadata["schema_path"],
            "schema_version": hed_metadata["schema_version"],
            "sidecar": {
                "file": hed_metadata["sidecar"],
                "issue_count": len(sidecar_issues),
                "issues": sidecar_issues,
            },
            "files": file_results,
            "issue_count": total_issues,
        }
        summary = {
            **base_summary,
            "status": status,
            "tool_version": runtime["version"],
            "issue_count": total_issues,
        }
        return artifact, summary
    except Exception as exc:  # pragma: no cover - defensive integration guard
        artifact = {
            "status": "failed",
            "tool": HED_TOOL_NAME,
            "tool_version": runtime["version"],
            "schema_path": hed_metadata["schema_path"],
            "schema_version": hed_metadata["schema_version"],
            "reason": str(exc),
            "checked_files": checked_files,
        }
        summary = {
            **base_summary,
            "status": "failed",
            "tool_version": runtime["version"],
            "reason": str(exc),
        }
        return artifact, summary
