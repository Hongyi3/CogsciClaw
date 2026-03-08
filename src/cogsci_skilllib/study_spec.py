from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from jsonschema import Draft202012Validator
import yaml

from .paths import SCHEMAS_DIR


ValidationRule = Tuple[str, Any, str]


@dataclass(frozen=True)
class SupportedProfile:
    id: str
    label: str
    runner: str
    supported_outputs: Tuple[str, ...]
    supported_standards: Tuple[str, ...]
    validation_rules: Tuple[ValidationRule, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "runner": self.runner,
            "supported_outputs": list(self.supported_outputs),
            "supported_standards": list(self.supported_standards),
        }


FLANKER_PROFILE = SupportedProfile(
    id="canonical-flanker-behavioral-demo",
    label="canonical Flanker behavioral demo",
    runner="scripts/run_flanker_behavioral_slice.py",
    supported_outputs=(
        "task_package",
        "curated_dataset",
        "model_report",
        "preregistration",
        "reproducibility_bundle",
    ),
    supported_standards=("Psych-DS", "HED"),
    validation_rules=(
        ("modality", "behavioral", "Only modality='behavioral' is supported in this milestone."),
        ("design.task_name", "flanker", "Only design.task_name='flanker' is supported in this milestone."),
        (
            "design.conditions",
            ["congruent", "incongruent"],
            "Only the canonical Flanker condition order ['congruent', 'incongruent'] is supported.",
        ),
        ("design.trial_count", 160, "Only design.trial_count=160 is supported in this milestone."),
        ("outputs.task_package", True, "Only outputs.task_package=true is supported in this milestone."),
        (
            "outputs.curated_dataset",
            True,
            "Only outputs.curated_dataset=true is supported in this milestone.",
        ),
        ("outputs.model_report", True, "Only outputs.model_report=true is supported in this milestone."),
        (
            "outputs.preregistration",
            True,
            "Only outputs.preregistration=true is supported in this milestone.",
        ),
        (
            "outputs.reproducibility_bundle",
            True,
            "Only outputs.reproducibility_bundle=true is supported in this milestone.",
        ),
    ),
)

ODDBALL_PROFILE = SupportedProfile(
    id="canonical-auditory-oddball-bids-intake-demo",
    label="canonical auditory oddball BIDS intake demo",
    runner="scripts/run_oddball_bids_slice.py",
    supported_outputs=(
        "curated_dataset",
        "preregistration",
        "reproducibility_bundle",
    ),
    supported_standards=("BIDS",),
    validation_rules=(
        ("modality", "eeg", "Only modality='eeg' is supported in this milestone."),
        (
            "design.task_name",
            "auditory_oddball",
            "Only design.task_name='auditory_oddball' is supported in this milestone.",
        ),
        (
            "design.conditions",
            ["standard", "target"],
            "Only the canonical oddball condition order ['standard', 'target'] is supported.",
        ),
        ("design.trial_count", 300, "Only design.trial_count=300 is supported in this milestone."),
        ("participants.target_n", 24, "Only participants.target_n=24 is supported in this milestone."),
        (
            "outputs.task_package",
            False,
            "Only outputs.task_package=false is supported in this milestone.",
        ),
        (
            "outputs.curated_dataset",
            True,
            "Only outputs.curated_dataset=true is supported in this milestone.",
        ),
        (
            "outputs.model_report",
            False,
            "Only outputs.model_report=false is supported in this milestone.",
        ),
        (
            "outputs.preregistration",
            True,
            "Only outputs.preregistration=true is supported in this milestone.",
        ),
        (
            "outputs.reproducibility_bundle",
            True,
            "Only outputs.reproducibility_bundle=true is supported in this milestone.",
        ),
        (
            "ethics.contains_sensitive_data",
            True,
            "Only ethics.contains_sensitive_data=true is supported in this milestone.",
        ),
    ),
)

SUPPORTED_PROFILES = {
    FLANKER_PROFILE.id: FLANKER_PROFILE,
    ODDBALL_PROFILE.id: ODDBALL_PROFILE,
}


@dataclass(frozen=True)
class StudySpecContext:
    spec_path: Path
    normalized_spec: Dict[str, Any]
    spec_sha256: str
    schema_validation: Dict[str, Any]
    supported_profile: Dict[str, Any]
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


def _nested_value(payload: Dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for key in dotted_path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _supported_profile_errors(payload: Dict[str, Any], profile: SupportedProfile) -> List[str]:
    errors: List[str] = []
    for dotted_path, expected, message in profile.validation_rules:
        if _nested_value(payload, dotted_path) != expected:
            errors.append(message)
    return errors


def _candidate_profiles(payload: Dict[str, Any]) -> Iterable[SupportedProfile]:
    task_name = _nested_value(payload, "design.task_name")
    if task_name == "flanker":
        return (FLANKER_PROFILE,)
    if task_name == "auditory_oddball":
        return (ODDBALL_PROFILE,)
    return SUPPORTED_PROFILES.values()


def _select_profile(payload: Dict[str, Any]) -> tuple[SupportedProfile, List[str]]:
    candidate_profiles = list(_candidate_profiles(payload))
    profile_errors = {
        profile.id: _supported_profile_errors(payload, profile) for profile in candidate_profiles
    }
    for profile in candidate_profiles:
        if not profile_errors[profile.id]:
            return profile, []

    if len(candidate_profiles) == 1:
        profile = candidate_profiles[0]
        return profile, profile_errors[profile.id]

    combined_errors = []
    for profile in candidate_profiles:
        combined_errors.append(
            "{label}: {errors}".format(
                label=profile.label,
                errors="; ".join(profile_errors[profile.id]),
            )
        )
    raise ValueError("Unsupported study spec: " + " | ".join(combined_errors))


def _unsupported_outputs(payload: Dict[str, Any], profile: SupportedProfile) -> List[str]:
    outputs = payload.get("outputs", {})
    requested = [name for name, enabled in outputs.items() if enabled]
    return sorted(name for name in requested if name not in profile.supported_outputs)


def _unsupported_standards(payload: Dict[str, Any], profile: SupportedProfile) -> List[str]:
    requested = payload.get("standards", [])
    return sorted(item for item in requested if item not in profile.supported_standards)


def validate_study_spec(path: Path) -> StudySpecContext:
    payload = load_yaml(path)
    normalized = _normalize_payload(payload)
    validation = _schema_validation(normalized)

    if not validation["valid"]:
        raise ValueError(
            "Study spec failed schema validation: "
            + "; ".join(error["message"] for error in validation["errors"])
        )

    profile, profile_errors = _select_profile(normalized)
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
        supported_profile=profile.as_dict(),
        unsupported_outputs=_unsupported_outputs(normalized, profile),
        unsupported_standards=_unsupported_standards(normalized, profile),
        supported_profile_errors=profile_errors,
    )


def build_validation_artifact(context: StudySpecContext) -> Dict[str, Any]:
    return {
        "schema": context.schema_validation["schema"],
        "valid": context.schema_validation["valid"],
        "errors": context.schema_validation["errors"],
        "supported_profile": {
            "valid": not context.supported_profile_errors,
            "id": context.supported_profile["id"],
            "label": context.supported_profile["label"],
            "runner": context.supported_profile["runner"],
            "supported_outputs": context.supported_profile["supported_outputs"],
            "supported_standards": context.supported_profile["supported_standards"],
            "errors": context.supported_profile_errors,
        },
        "unsupported_requested_outputs": context.unsupported_outputs,
        "unsupported_requested_standards": context.unsupported_standards,
        "study_spec_sha256": context.spec_sha256,
    }
