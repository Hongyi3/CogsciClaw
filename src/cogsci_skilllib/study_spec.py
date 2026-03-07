from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator
import yaml

from .paths import SCHEMAS_DIR


SUPPORTED_OUTPUTS = {
    "task_package",
    "curated_dataset",
    "reproducibility_bundle",
}
SUPPORTED_STANDARDS = {"Psych-DS"}


@dataclass(frozen=True)
class StudySpecContext:
    spec_path: Path
    normalized_spec: Dict[str, Any]
    spec_sha256: str
    schema_validation: Dict[str, Any]
    unsupported_outputs: List[str]
    unsupported_standards: List[str]
    supported_profile_errors: List[str]


def load_yaml(path: Path) -> Dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Study spec must be a YAML mapping.")
    return payload


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Round-trip through JSON to normalize ordering-sensitive types.
    return json.loads(json.dumps(payload, sort_keys=True))


def _load_schema() -> Dict[str, Any]:
    schema_path = SCHEMAS_DIR / "study-spec.schema.yaml"
    return load_yaml(schema_path)


def _schema_validation(payload: Dict[str, Any]) -> Dict[str, Any]:
    schema_path = SCHEMAS_DIR / "study-spec.schema.yaml"
    validator = Draft202012Validator(_load_schema())
    errors = [
        {
            "message": error.message,
            "path": list(error.path),
        }
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    ]
    return {
        "schema": str(schema_path.relative_to(schema_path.parents[1])),
        "valid": not errors,
        "errors": errors,
    }


def _supported_profile_errors(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    modality = payload.get("modality")
    if modality != "behavioral":
        errors.append("Only modality='behavioral' is supported in this milestone.")

    design = payload.get("design", {})
    if design.get("task_name") != "flanker":
        errors.append("Only design.task_name='flanker' is supported in this milestone.")

    conditions = design.get("conditions")
    if conditions != ["congruent", "incongruent"]:
        errors.append(
            "Only the canonical Flanker condition order ['congruent', 'incongruent'] is supported."
        )

    if design.get("trial_count") != 160:
        errors.append("Only design.trial_count=160 is supported in this milestone.")

    return errors


def _unsupported_outputs(payload: Dict[str, Any]) -> List[str]:
    outputs = payload.get("outputs", {})
    requested = [name for name, enabled in outputs.items() if enabled]
    return sorted(name for name in requested if name not in SUPPORTED_OUTPUTS)


def _unsupported_standards(payload: Dict[str, Any]) -> List[str]:
    requested = payload.get("standards", [])
    return sorted(item for item in requested if item not in SUPPORTED_STANDARDS)


def validate_study_spec(path: Path) -> StudySpecContext:
    payload = load_yaml(path)
    normalized = _normalize_payload(payload)
    validation = _schema_validation(normalized)

    if not validation["valid"]:
        raise ValueError(
            "Study spec failed schema validation: "
            + "; ".join(error["message"] for error in validation["errors"])
        )

    profile_errors = _supported_profile_errors(normalized)
    if profile_errors:
        raise ValueError("Unsupported study spec: " + "; ".join(profile_errors))

    spec_digest = sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return StudySpecContext(
        spec_path=path,
        normalized_spec=normalized,
        spec_sha256=spec_digest,
        schema_validation=validation,
        unsupported_outputs=_unsupported_outputs(normalized),
        unsupported_standards=_unsupported_standards(normalized),
        supported_profile_errors=profile_errors,
    )


def build_validation_artifact(context: StudySpecContext) -> Dict[str, Any]:
    return {
        "schema": context.schema_validation["schema"],
        "valid": context.schema_validation["valid"],
        "errors": context.schema_validation["errors"],
        "supported_profile": {
            "valid": not context.supported_profile_errors,
            "errors": context.supported_profile_errors,
        },
        "unsupported_requested_outputs": context.unsupported_outputs,
        "unsupported_requested_standards": context.unsupported_standards,
        "study_spec_sha256": context.spec_sha256,
    }
