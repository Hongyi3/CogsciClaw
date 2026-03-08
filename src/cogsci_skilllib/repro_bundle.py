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


PREREGISTRATION_ARTIFACT = "report/preregistration/preregistration.json"
RUN_MANIFEST_ARTIFACT = "report/provenance/run_manifest.json"
RO_CRATE_ARTIFACT = "report/provenance/ro-crate-metadata.json"
PROV_ARTIFACT = "report/provenance/prov.jsonld"
CHECKSUMS_ARTIFACT = "report/checksums.sha256"
BIDS_VALIDATION_ARTIFACT = "report/validation/bids-validator.json"

BASE_UNSUPPORTED_CAPABILITIES = [
    "Cognitive Atlas mappings",
    "drift-diffusion model fitting beyond runtime probing",
    "registry or API preregistration submission",
    "validator-backed RO-Crate / PROV conformance claims",
    "figures and tables",
    "arbitrary behavioral study specifications beyond the canonical Flanker demo",
]
ODDBALL_UNSUPPORTED_CAPABILITIES = [
    "empirical EEG or MEG signal conversion",
    "events.tsv timing generation",
    "channels.tsv or electrodes.tsv metadata",
    "HED annotation",
    "MNE-BIDS ingestion",
    "MNE preprocessing, QC dashboards, or ERP analysis",
    "participant-level scientific interpretation",
    "registry or API preregistration submission",
    "validator-backed RO-Crate / PROV conformance claims",
    "figures and tables",
    "arbitrary EEG/MEG study specifications beyond the canonical oddball demo",
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
            "arviz": package_version("arviz"),
            "cogsci-skilllib": __version__,
            "hedtools": package_version("hedtools"),
            "hddm": package_version("hddm"),
            "jsonschema": package_version("jsonschema"),
            "mne": package_version("mne"),
            "mne-bids": package_version("mne-bids"),
            "numpy": package_version("numpy"),
            "pandas": package_version("pandas"),
            "PyYAML": package_version("PyYAML"),
            "pymc": package_version("pymc"),
            "scipy": package_version("scipy"),
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
  --validate-psychds auto \
  --validate-hed auto \
  --fit-bayes auto \
  --fit-ddm auto

if command -v validate >/dev/null 2>&1; then
  validate "${OUTPUT_DIR}/psychds" --json > "${OUTPUT_DIR}/report/validation/psychds-validator.json"
fi
"""


def oddball_commands_script() -> str:
    return """#!/usr/bin/env sh
set -eu

PYTHON_BIN="${PYTHON_BIN:-python3}"
OUTPUT_DIR="${OUTPUT_DIR:-output/eeg-oddball-bids-intake}"
VALIDATE_BIDS="${VALIDATE_BIDS:-auto}"

"${PYTHON_BIN}" scripts/run_oddball_bids_slice.py \
  --study-spec examples/eeg-oddball/study_spec.yaml \
  --output-dir "${OUTPUT_DIR}" \
  --validate-bids "${VALIDATE_BIDS}"

if command -v bids-validator >/dev/null 2>&1; then
  bids-validator "${OUTPUT_DIR}/bids-intake" --json > "${OUTPUT_DIR}/report/validation/bids-validator.json"
fi
"""


def _status_line(summary: Dict[str, Any]) -> str:
    line = summary["status"]
    if summary.get("reason"):
        line = f"{line} ({summary['reason']})"
    return line


def _unsupported_capabilities(modeling_metadata: Dict[str, Any]) -> List[str]:
    capabilities = list(BASE_UNSUPPORTED_CAPABILITIES)
    if modeling_metadata["bayesian"]["status"] != "passed":
        capabilities.insert(
            1,
            "Bayesian model execution on machines without a working PyMC / ArviZ runtime",
        )
    return capabilities


def _source_ref(path: str, field: str) -> Dict[str, str]:
    return {
        "path": path,
        "field": field,
    }


def _human_review_points(study_spec_reference: str) -> List[Dict[str, Any]]:
    return [
        {
            "id": "ethics_privacy_review",
            "reason": (
                "Real study deployment still requires local ethics and privacy review even though "
                "this bundle contains only deterministic synthetic-demo data."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "ethics.notes"),
                _source_ref("METHODS_POLICY.md", "Human review remains mandatory where needed"),
            ],
        },
        {
            "id": "task_validity_timing_review",
            "reason": (
                "Task validity, timing, and response-mapping assumptions still require human "
                "methods review before non-demo use."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "design"),
                _source_ref("METHODS_POLICY.md", "Human review remains mandatory where needed"),
            ],
        },
        {
            "id": "participant_eligibility_exclusion_review",
            "reason": (
                "Eligibility and exclusion procedures remain human decisions; this demo bundle "
                "records target enrollment and inclusion criteria but does not operationalize "
                "screening or exclusion handling."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "participants"),
                _source_ref("METHODS_POLICY.md", "Human review remains mandatory where needed"),
            ],
        },
        {
            "id": "construct_mapping_review",
            "reason": (
                "Construct mapping still requires human review because `Cognitive Atlas` remains "
                "an unsupported requested standard in this milestone."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "standards"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_requested_standards"),
            ],
        },
        {
            "id": "empirical_registration_completion",
            "reason": (
                "This artifact is a local synthetic-demo preregistration export, not a completed "
                "registry submission for an empirical study."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "outputs.preregistration"),
                _source_ref("METHODS_POLICY.md", "Human review remains mandatory where needed"),
            ],
        },
    ]


def build_run_manifest(
    study_spec_reference: str,
    study_spec_sha256: str,
    study_title: str,
    supported_profile_name: str,
    demo_profile: Dict[str, Any],
    schedule_summary: Dict[str, Any],
    task_metadata: Dict[str, Any],
    hed_metadata: Dict[str, Any],
    psychds_metadata: Dict[str, Any],
    modeling_metadata: Dict[str, Any],
    study_validation: Dict[str, Any],
    hed_validation_summary: Dict[str, Any],
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
            "name": supported_profile_name,
            "hed_annotation": True,
            "model_artifacts": True,
            "preregistration_export": True,
            "ro_crate_export": True,
            "prov_export": True,
            "task_generation": True,
            "psychds_curation": True,
            "reproducibility_bundle": True,
            "synthetic_demo_data": True,
        },
        "demo_profile": demo_profile,
        "trial_schedule": schedule_summary,
        "task_artifact": task_metadata,
        "hed": hed_metadata,
        "psychds": psychds_metadata,
        "modeling": modeling_metadata,
        "preregistration": {
            "artifact": PREREGISTRATION_ARTIFACT,
        },
        "provenance": {
            "run_manifest": RUN_MANIFEST_ARTIFACT,
            "ro_crate": RO_CRATE_ARTIFACT,
            "prov": PROV_ARTIFACT,
        },
        "validation": {
            "study_spec": {
                "status": "passed" if study_validation["valid"] else "failed",
                "schema": study_validation["schema"],
            },
            "hed": hed_validation_summary,
            "psychds": psychds_validation_summary,
            "report_bundle": {
                "status": "pending",
                "schema": "schemas/report-bundle.schema.json",
            },
        },
        "unsupported_requested_outputs": study_validation["unsupported_requested_outputs"],
        "unsupported_requested_standards": study_validation["unsupported_requested_standards"],
        "unsupported_capabilities": _unsupported_capabilities(modeling_metadata),
    }


def _oddball_human_review_points(study_spec_reference: str) -> List[Dict[str, Any]]:
    return [
        {
            "id": "ethics_privacy_review",
            "reason": (
                "The oddball study spec marks contains_sensitive_data=true, so local privacy and "
                "ethics review remain mandatory before any empirical data handling."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "ethics.contains_sensitive_data"),
                _source_ref(study_spec_reference, "ethics.notes"),
                _source_ref("METHODS_POLICY.md", "Human review remains mandatory where needed"),
            ],
        },
        {
            "id": "acquisition_metadata_completion",
            "reason": (
                "The emitted intake tree is placeholder-only; acquisition metadata still requires "
                "human completion before BIDS EEG files can be generated truthfully."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "modality"),
                _source_ref("bids-intake/intake_manifest.json", "unsupported_artifacts"),
            ],
        },
        {
            "id": "event_timing_completion",
            "reason": (
                "Event timing files were not generated because the checked-in demo inputs do not "
                "provide empirical onset or duration metadata."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "design"),
                _source_ref("bids-intake/intake_manifest.json", "unsupported_artifacts"),
            ],
        },
        {
            "id": "participant_consent_review",
            "reason": (
                "Participant handling, consent, and screening procedures remain human decisions; "
                "the intake tree contains deterministic placeholder participant identifiers only."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "participants"),
                _source_ref("METHODS_POLICY.md", "Human review remains mandatory where needed"),
            ],
        },
        {
            "id": "empirical_registration_completion",
            "reason": (
                "This artifact is a local placeholder-demo preregistration export, not a completed "
                "registry submission for an empirical EEG study."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "outputs.preregistration"),
                _source_ref(PREREGISTRATION_ARTIFACT, "artifact_type"),
            ],
        },
    ]


def build_oddball_run_manifest(
    study_spec_reference: str,
    study_spec_sha256: str,
    study_title: str,
    supported_profile_name: str,
    normalized_spec: Dict[str, Any],
    bids_metadata: Dict[str, Any],
    study_validation: Dict[str, Any],
    bids_validation_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "runner": "scripts/run_oddball_bids_slice.py",
        "version": __version__,
        "study_spec": {
            "path": study_spec_reference,
            "sha256": study_spec_sha256,
            "title": study_title,
            "modality": normalized_spec["modality"],
        },
        "supported_slice": {
            "name": supported_profile_name,
            "bids_intake": True,
            "bids_validator_artifact": True,
            "preregistration_export": True,
            "ro_crate_export": True,
            "prov_export": True,
            "reproducibility_bundle": True,
            "placeholder_metadata_only": True,
        },
        "bids_intake": bids_metadata,
        "ethics": {
            "contains_sensitive_data": normalized_spec.get("ethics", {}).get("contains_sensitive_data", False),
            "notes": normalized_spec.get("ethics", {}).get("notes", ""),
        },
        "preregistration": {
            "artifact": PREREGISTRATION_ARTIFACT,
        },
        "provenance": {
            "run_manifest": RUN_MANIFEST_ARTIFACT,
            "ro_crate": RO_CRATE_ARTIFACT,
            "prov": PROV_ARTIFACT,
        },
        "validation": {
            "study_spec": {
                "status": "passed" if study_validation["valid"] else "failed",
                "schema": study_validation["schema"],
            },
            "bids": bids_validation_summary,
            "report_bundle": {
                "status": "pending",
                "schema": "schemas/report-bundle.schema.json",
            },
        },
        "unsupported_requested_outputs": study_validation["unsupported_requested_outputs"],
        "unsupported_requested_standards": study_validation["unsupported_requested_standards"],
        "unsupported_capabilities": list(ODDBALL_UNSUPPORTED_CAPABILITIES),
    }


def build_oddball_preregistration_artifact(
    normalized_spec: Dict[str, Any],
    study_spec_reference: str,
    study_spec_sha256: str,
    run_manifest: Dict[str, Any],
) -> Dict[str, Any]:
    requested_outputs = normalized_spec.get("outputs", {})
    participants = normalized_spec.get("participants", {})
    bids_validation = run_manifest["validation"]["bids"]

    supported_claims = [
        {
            "id": "canonical_oddball_placeholder_scope",
            "claim": (
                "This artifact covers only the canonical auditory oddball EEG intake demo with "
                "placeholder metadata, not empirical EEG recordings."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "study.title"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "supported_slice.name"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "bids_intake.placeholder_only"),
            ],
        },
        {
            "id": "bids_aligned_intake_emitted",
            "claim": (
                "A deterministic BIDS-aligned intake tree was emitted with dataset metadata, "
                "participant summary files, and placeholder participant artifacts."
            ),
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "bids_intake.dataset_description"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "bids_intake.placeholder_files"),
            ],
        },
        {
            "id": "truthful_bids_validator_status_emitted",
            "claim": "A validator-aware BIDS status artifact was emitted without claiming compliance blindly.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "validation.bids.status"),
                _source_ref(BIDS_VALIDATION_ARTIFACT, "status"),
            ],
        },
        {
            "id": "machine_readable_provenance_exports_emitted",
            "claim": "Machine-readable RO-Crate and PROV provenance exports were emitted in the bundle.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "provenance.ro_crate"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "provenance.prov"),
            ],
        },
    ]
    if bids_validation["status"] == "passed":
        supported_claims.append(
            {
                "id": "local_bids_validator_passed_on_this_runtime",
                "claim": "The local BIDS validator passed on this runtime for the emitted intake tree.",
                "source_refs": [
                    _source_ref(RUN_MANIFEST_ARTIFACT, "validation.bids.status"),
                    _source_ref(BIDS_VALIDATION_ARTIFACT, "validator_output"),
                ],
            }
        )

    unsupported_claims = [
        {
            "id": "empirical_eeg_conversion_not_supported",
            "claim": "Empirical EEG conversion is not supported in this milestone.",
            "reason": "The emitted intake tree is placeholder-only and contains no raw EEG signal files.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "bids_intake.contains_empirical_data"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
        {
            "id": "hed_annotation_not_supported",
            "claim": "HED annotation is not supported in this milestone for the oddball slice.",
            "reason": "Event timing files were not generated, so no HED event contract is claimed.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_requested_standards"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
        {
            "id": "mne_pipeline_not_supported",
            "claim": "MNE-BIDS ingestion and MNE preprocessing are not supported in this milestone.",
            "reason": "This milestone stops at intake and validator-aware metadata packaging.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_requested_standards"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
        {
            "id": "erp_interpretation_not_supported",
            "claim": "ERP analysis and participant-level interpretation are not supported in this milestone.",
            "reason": "No preprocessing, epoching, or inference outputs are emitted.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
                _source_ref(study_spec_reference, "study.hypotheses"),
            ],
        },
        {
            "id": "registry_submission_not_supported",
            "claim": "Registry or API preregistration submission is not supported in this milestone.",
            "reason": "The bundle emits only a local deterministic export.",
            "source_refs": [
                _source_ref(PREREGISTRATION_ARTIFACT, "artifact_type"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
        {
            "id": "provenance_validation_not_supported",
            "claim": "Validator-backed RO-Crate or PROV conformance claims are not supported in this milestone.",
            "reason": "The bundle emits machine-readable provenance files without claiming external validation.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "provenance"),
            ],
        },
        {
            "id": "arbitrary_study_specs_not_supported",
            "claim": "Arbitrary EEG/MEG study specifications are not supported in this milestone.",
            "reason": "The supported profile remains the canonical auditory oddball intake demo only.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "supported_slice.name"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
    ]
    if bids_validation["status"] == "failed":
        unsupported_claims.append(
            {
                "id": "local_bids_validator_failed_on_this_runtime",
                "claim": "The local BIDS validator did not pass on this runtime.",
                "reason": "The emitted artifact records the validator result rather than claiming compliance.",
                "source_refs": [
                    _source_ref(RUN_MANIFEST_ARTIFACT, "validation.bids.status"),
                    _source_ref(BIDS_VALIDATION_ARTIFACT, "validator_output"),
                ],
            }
        )
    if bids_validation["status"] == "not_run":
        unsupported_claims.append(
            {
                "id": "bids_validation_not_run_on_this_runtime",
                "claim": "BIDS validation was not executed on this runtime.",
                "reason": bids_validation.get("reason", "No local bids-validator binary was available."),
                "source_refs": [
                    _source_ref(RUN_MANIFEST_ARTIFACT, "validation.bids.status"),
                    _source_ref(BIDS_VALIDATION_ARTIFACT, "reason"),
                ],
            }
        )

    return {
        "artifact_type": "cogsci-skilllib-preregistration-demo",
        "supported_profile": run_manifest["supported_slice"]["name"],
        "placeholder_demo": True,
        "study_spec": {
            "path": study_spec_reference,
            "sha256": study_spec_sha256,
            "schema": run_manifest["validation"]["study_spec"]["schema"],
        },
        "study": {
            "title": normalized_spec["study"]["title"],
            "research_question": normalized_spec["study"]["research_question"],
            "hypotheses": normalized_spec["study"].get("hypotheses", []),
            "modality": normalized_spec["modality"],
        },
        "design": {
            "task_name": normalized_spec["design"]["task_name"],
            "conditions": normalized_spec["design"]["conditions"],
            "trial_count": normalized_spec["design"]["trial_count"],
            "randomization": normalized_spec["design"]["randomization"],
            "counterbalancing": normalized_spec["design"]["counterbalancing"],
        },
        "participants": {
            "target_n": participants.get("target_n"),
            "placeholder_subject_ids": run_manifest["bids_intake"]["placeholder_subject_ids"],
            "contains_empirical_data": False,
        },
        "ethics": run_manifest["ethics"],
        "requested_outputs": {
            "requested": requested_outputs,
            "unsupported_requested_outputs": run_manifest["unsupported_requested_outputs"],
            "unsupported_requested_standards": run_manifest["unsupported_requested_standards"],
        },
        "intake_contract": {
            "dataset_root": run_manifest["bids_intake"]["intake_root"],
            "dataset_description": run_manifest["bids_intake"]["dataset_description"],
            "participants_tsv": run_manifest["bids_intake"]["participants_tsv"],
            "participants_json": run_manifest["bids_intake"]["participants_json"],
            "intake_manifest": run_manifest["bids_intake"]["intake_manifest"],
            "placeholder_files": run_manifest["bids_intake"]["placeholder_files"],
            "placeholder_only": run_manifest["bids_intake"]["placeholder_only"],
            "contains_empirical_data": run_manifest["bids_intake"]["contains_empirical_data"],
            "bids_version": run_manifest["bids_intake"]["bids_version"],
            "dataset_type": run_manifest["bids_intake"]["dataset_type"],
            "validator_status": bids_validation["status"],
            "validator_artifact": BIDS_VALIDATION_ARTIFACT,
        },
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "required_human_review": _oddball_human_review_points(study_spec_reference),
    }


def build_preregistration_artifact(
    normalized_spec: Dict[str, Any],
    study_spec_reference: str,
    study_spec_sha256: str,
    run_manifest: Dict[str, Any],
) -> Dict[str, Any]:
    requested_outputs = normalized_spec.get("outputs", {})
    participants = normalized_spec.get("participants", {})
    modeling = run_manifest["modeling"]

    supported_claims = [
        {
            "id": "canonical_synthetic_demo_scope",
            "claim": (
                "This artifact covers only the canonical synthetic-demo Flanker behavioral slice "
                "implemented in this repository."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "study.title"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "supported_slice.name"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "demo_profile.synthetic_data"),
            ],
        },
        {
            "id": "local_preregistration_export_emitted",
            "claim": (
                "A deterministic local preregistration export was emitted from the normalized "
                "study specification plus runtime metadata."
            ),
            "source_refs": [
                _source_ref(study_spec_reference, "outputs.preregistration"),
                _source_ref(PREREGISTRATION_ARTIFACT, "artifact_type"),
            ],
        },
        {
            "id": "machine_readable_provenance_exports_emitted",
            "claim": "Machine-readable RO-Crate and PROV provenance exports were emitted in the bundle.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "provenance.ro_crate"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "provenance.prov"),
            ],
        },
        {
            "id": "truthful_model_artifacts_emitted",
            "claim": (
                "Bayesian and DDM artifact files are emitted with runtime-derived status metadata "
                "instead of silent scientific fallbacks."
            ),
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.bayesian.status"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.ddm.status"),
            ],
        },
    ]
    if modeling["bayesian"]["status"] == "passed":
        supported_claims.append(
            {
                "id": "bayesian_baseline_executed_on_this_runtime",
                "claim": (
                    "A real Bayesian baseline fit with diagnostics was executed on this runtime "
                    "for the canonical synthetic Flanker slice."
                ),
                "source_refs": [
                    _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.bayesian.status"),
                    _source_ref(
                        RUN_MANIFEST_ARTIFACT,
                        "modeling.bayesian.diagnostics_artifact",
                    ),
                ],
            }
        )

    unsupported_claims = [
        {
            "id": "cognitive_atlas_mappings_unsupported",
            "claim": "Cognitive Atlas construct mappings are not supported in this milestone.",
            "reason": "The requested `Cognitive Atlas` standard is still outside the implemented slice.",
            "source_refs": [
                _source_ref(study_spec_reference, "standards"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_requested_standards"),
            ],
        },
        {
            "id": "ddm_fitting_not_supported",
            "claim": "Drift-diffusion fitting beyond runtime probing is not supported in this milestone.",
            "reason": "The DDM artifact remains a truthful runtime probe rather than a fitted model.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.ddm.status"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.ddm.reason"),
            ],
        },
        {
            "id": "registry_submission_not_supported",
            "claim": "Registry or API preregistration submission is not supported in this milestone.",
            "reason": "The bundle emits only a local deterministic export.",
            "source_refs": [
                _source_ref(PREREGISTRATION_ARTIFACT, "artifact_type"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
        {
            "id": "provenance_validation_not_supported",
            "claim": "Validator-backed RO-Crate or PROV conformance claims are not supported in this milestone.",
            "reason": "The bundle emits machine-readable provenance files without claiming external validation.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "provenance"),
            ],
        },
        {
            "id": "figures_tables_not_emitted",
            "claim": "Figures and tables are not emitted in this milestone.",
            "reason": "The current bundle contract remains limited to task, curation, modeling, report, preregistration, and provenance outputs.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
                _source_ref(study_spec_reference, "outputs"),
            ],
        },
        {
            "id": "arbitrary_study_specs_not_supported",
            "claim": "Arbitrary behavioral study specifications are not supported in this milestone.",
            "reason": "The supported profile remains the canonical Flanker behavioral demo only.",
            "source_refs": [
                _source_ref(RUN_MANIFEST_ARTIFACT, "supported_slice.name"),
                _source_ref(RUN_MANIFEST_ARTIFACT, "unsupported_capabilities"),
            ],
        },
    ]
    if modeling["bayesian"]["status"] != "passed":
        unsupported_claims.append(
            {
                "id": "bayesian_execution_runtime_limited",
                "claim": "Bayesian execution did not complete successfully on this runtime.",
                "reason": (
                    "Bayesian support remains runtime-sensitive and requires a healthy local "
                    "PyMC / ArviZ environment."
                ),
                "source_refs": [
                    _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.bayesian.status"),
                    _source_ref(RUN_MANIFEST_ARTIFACT, "modeling.bayesian.reason"),
                ],
            }
        )

    return {
        "artifact_type": "cogsci-skilllib-preregistration-demo",
        "supported_profile": run_manifest["supported_slice"]["name"],
        "synthetic_demo": True,
        "study_spec": {
            "path": study_spec_reference,
            "sha256": study_spec_sha256,
            "schema": run_manifest["validation"]["study_spec"]["schema"],
        },
        "study": {
            "title": normalized_spec["study"]["title"],
            "research_question": normalized_spec["study"]["research_question"],
            "hypotheses": normalized_spec["study"].get("hypotheses", []),
            "modality": normalized_spec["modality"],
        },
        "design": {
            "task_name": normalized_spec["design"]["task_name"],
            "conditions": normalized_spec["design"]["conditions"],
            "trial_count": normalized_spec["design"]["trial_count"],
            "randomization": normalized_spec["design"]["randomization"],
            "counterbalancing": normalized_spec["design"]["counterbalancing"],
            "implemented_trial_schedule": run_manifest["trial_schedule"],
        },
        "participants": {
            "target_n": participants.get("target_n"),
            "inclusion_criteria": participants.get("inclusion_criteria", []),
            "synthetic_demo_participants": run_manifest["demo_profile"]["participants"],
        },
        "requested_outputs": {
            "requested": requested_outputs,
            "unsupported_requested_outputs": run_manifest["unsupported_requested_outputs"],
            "unsupported_requested_standards": run_manifest["unsupported_requested_standards"],
        },
        "implemented_analysis_contract": {
            "synthetic_demo_only": True,
            "confirmatory_hypotheses": normalized_spec["study"].get("hypotheses", []),
            "bayesian_baseline": {
                "status": modeling["bayesian"]["status"],
                "models": modeling["bayesian"].get("models", []),
                "condition_effects_artifact": modeling["bayesian"]["condition_effects_artifact"],
                "diagnostics_artifact": modeling["bayesian"]["diagnostics_artifact"],
            },
            "ddm_runtime_probe": {
                "status": modeling["ddm"]["status"],
                "artifact": modeling["ddm"]["artifact"],
                "reason": modeling["ddm"].get("reason"),
            },
        },
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "required_human_review": _human_review_points(study_spec_reference),
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
    hed_metadata = run_manifest["hed"]
    modeling = run_manifest["modeling"]
    preregistration_artifact = run_manifest["preregistration"]["artifact"]
    provenance = run_manifest["provenance"]

    return """# Methods

## Input and scope

This run used the study specification `{study_spec_reference}` (SHA-256 `{study_spec_sha256}`) for the study "{study_title}".
The implemented slice supports only the canonical behavioral Flanker demo path: jsPsych task generation, deterministic synthetic demo data generation, HED event annotation, Psych-DS-aligned curation, deterministic model artifacts, and reproducibility bundle assembly.

## Task generation

The browser artifact was generated with jsPsych {jspsych_version} and `@jspsych/plugin-html-keyboard-response` {plugin_version}.
Each participant completed {trial_count} trials with balanced condition counts ({condition_counts}) and the fixed stimulus set {stimuli}.
The task used fixation {fixation} ms, response deadline {deadline} ms, and inter-trial interval {iti} ms.

## Synthetic demo data

The curated dataset is synthetic and deterministic; it is present only to exercise curation and reproducibility paths in CI and local demo runs.
Two synthetic participants were generated: {participants}.
No practice block, feedback block, adaptive logic, empirical recruitment, or empirical participant-data interpretation was run in this milestone.

## Event annotation

HED-oriented event artifacts were written under `events/` as one shared sidecar and two participant event tables with two rows per trial (stimulus and response).
The event annotations were derived from deterministic runtime metadata plus the checked-in Flanker mapping rules in `{hed_mapping_rules}` and targeted the vendored HED schema `{hed_schema_path}` (version {hed_schema_version}).

## Modeling

Deterministic model input rows were written to `{model_input}` from the synthetic trial tables.
The supported Bayesian analysis contract targets two trial-level models with participant intercepts and a condition effect: a Bernoulli-logit model for accuracy and a Normal model on `log_rt_seconds` for correct trials only.
Bayesian fitting status: {bayesian_status}.
Bayesian diagnostics artifact: `{bayesian_diagnostics}`.
DDM status: {ddm_status}.
DDM status artifact: `{ddm_artifact}`.

## Curation and validation

Trial tables were written into a Psych-DS-aligned dataset under `psychds/data/` with matching sidecar metadata and a global `dataset_description.json`.
Study-spec validation status: {study_status}.
HED validation status: {hed_status}.
Psych-DS validator status: {psychds_status}.

## Unsupported requests and standards

Unsupported requested outputs for this study spec: {unsupported_outputs}.
Unsupported requested standards for this study spec: {unsupported_standards}.
Unsupported capabilities still deferred in this milestone: {unsupported_capabilities}.
Required human review points remain explicit in `{preregistration_artifact}`: ethics/privacy review, task validity/timing review, participant eligibility/exclusion confirmation, construct mapping review, and empirical-registration completion before non-demo use.

## Reproducibility artifacts

The bundle includes a machine-readable manifest, commands script, environment snapshot, checksums, study-spec validation, report-bundle validation, run manifest, preregistration export `{preregistration_artifact}`, RO-Crate metadata `{ro_crate}`, and PROV JSON-LD metadata `{prov}`.
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
        hed_mapping_rules=hed_metadata["mapping_rules"],
        hed_schema_path=hed_metadata["schema_path"],
        hed_schema_version=hed_metadata["schema_version"],
        model_input=modeling["input_file"],
        bayesian_status=_status_line(modeling["bayesian"]),
        bayesian_diagnostics=modeling["bayesian"]["diagnostics_artifact"],
        ddm_status=_status_line(modeling["ddm"]),
        ddm_artifact=modeling["ddm"]["artifact"],
        study_status=run_manifest["validation"]["study_spec"]["status"],
        hed_status=_status_line(run_manifest["validation"]["hed"]),
        psychds_status=_status_line(run_manifest["validation"]["psychds"]),
        unsupported_outputs=unsupported_outputs,
        unsupported_standards=unsupported_standards,
        unsupported_capabilities=", ".join(run_manifest["unsupported_capabilities"]),
        preregistration_artifact=preregistration_artifact,
        ro_crate=provenance["ro_crate"],
        prov=provenance["prov"],
    )


def report_markdown(
    study_spec_reference: str,
    run_manifest: Dict[str, Any],
) -> str:
    unsupported_outputs = run_manifest["unsupported_requested_outputs"]
    unsupported_standards = run_manifest["unsupported_requested_standards"]
    modeling = run_manifest["modeling"]
    return """# Flanker Behavioral Slice Report

- Study spec: `{study_spec_reference}`
- Supported path executed: jsPsych task package, deterministic synthetic demo data, HED event annotation, Psych-DS-aligned curation, deterministic model artifacts, preregistration export, provenance packaging, reproducibility bundle
- Trial count per participant: {trial_count}
- Condition counts: {condition_counts}
- HED event sidecar: {hed_sidecar}
- HED participant event tables: {hed_event_tables}
- HED validation status: {hed_status}
- Model input artifact: {model_input}
- Bayesian condition-effects artifact: {bayesian_condition_effects}
- Bayesian diagnostics status: {bayesian_status}
- DDM status: {ddm_status}
- Preregistration artifact: {preregistration_artifact}
- RO-Crate metadata: {ro_crate}
- PROV JSON-LD: {prov}
- Required human review points: ethics/privacy review, task validity/timing review, participant eligibility/exclusion confirmation, construct mapping review, empirical-registration completion
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
        hed_sidecar=run_manifest["hed"]["sidecar"],
        hed_event_tables=", ".join(run_manifest["hed"]["participant_event_files"]),
        hed_status=_status_line(run_manifest["validation"]["hed"]),
        model_input=modeling["input_file"],
        bayesian_condition_effects=modeling["bayesian"]["condition_effects_artifact"],
        bayesian_status=_status_line(modeling["bayesian"]),
        ddm_status=_status_line(modeling["ddm"]),
        preregistration_artifact=run_manifest["preregistration"]["artifact"],
        ro_crate=run_manifest["provenance"]["ro_crate"],
        prov=run_manifest["provenance"]["prov"],
        psychds_status=_status_line(run_manifest["validation"]["psychds"]),
        unsupported_outputs=", ".join(unsupported_outputs) or "none",
        unsupported_standards=", ".join(unsupported_standards) or "none",
        unsupported_capabilities=", ".join(run_manifest["unsupported_capabilities"]),
    )


def oddball_methods_markdown(
    study_title: str,
    study_spec_reference: str,
    study_spec_sha256: str,
    run_manifest: Dict[str, Any],
) -> str:
    bids_intake = run_manifest["bids_intake"]
    validator = run_manifest["validation"]["bids"]
    placeholder_ids = ", ".join(bids_intake["placeholder_subject_ids"])
    unsupported_standards = ", ".join(run_manifest["unsupported_requested_standards"]) or "none"

    return """# Methods

## Input and scope

This run used the study specification `{study_spec_reference}` (SHA-256 `{study_spec_sha256}`) for the study "{study_title}".
The implemented slice supports only the canonical auditory oddball EEG intake demo path: BIDS-aligned intake metadata emission, validator-aware status recording, preregistration export, and provenance-aware reproducibility packaging.

## BIDS intake emission

The intake tree was written under `{intake_root}` with `dataset_description.json`, `README.md`, `participants.tsv`, `participants.json`, `intake_manifest.json`, and deterministic placeholder participant artifacts.
The emitted intake contract targets BIDS version {bids_version} with dataset type `{dataset_type}` while labeling every participant artifact as placeholder-only metadata.
The placeholder participant identifiers were derived deterministically from `participants.target_n`: {placeholder_ids}.

## Explicitly unimplemented metadata

No empirical EEG signal files, `events.tsv` timing files, `channels.tsv`, `electrodes.tsv`, HED annotations, MNE-BIDS conversion outputs, or MNE preprocessing outputs were emitted.
Those artifacts remain intentionally absent because the checked-in demo inputs do not specify empirical acquisition files, channel layouts, or event timing.

## Validation and privacy

Study-spec validation status: {study_status}.
BIDS validator status: {bids_status}.
Unsupported requested standards for this study spec: {unsupported_standards}.
The study spec marks `contains_sensitive_data = true`, so privacy review remains mandatory before any empirical data handling.

## Reproducibility artifacts

The bundle includes a machine-readable manifest, commands script, environment snapshot, checksums, study-spec validation, BIDS validator artifact `{bids_validation_artifact}`, run manifest, preregistration export `{preregistration_artifact}`, RO-Crate metadata `{ro_crate}`, and PROV JSON-LD metadata `{prov}`.
Required human review points remain explicit in `{preregistration_artifact}`: ethics/privacy review, acquisition-metadata completion, event-timing completion, participant/consent review, and empirical-registration completion before non-demo use.
""".format(
        study_spec_reference=study_spec_reference,
        study_spec_sha256=study_spec_sha256,
        study_title=study_title,
        intake_root=bids_intake["intake_root"],
        bids_version=bids_intake["bids_version"],
        dataset_type=bids_intake["dataset_type"],
        placeholder_ids=placeholder_ids,
        study_status=run_manifest["validation"]["study_spec"]["status"],
        bids_status=_status_line(validator),
        unsupported_standards=unsupported_standards,
        bids_validation_artifact=BIDS_VALIDATION_ARTIFACT,
        preregistration_artifact=run_manifest["preregistration"]["artifact"],
        ro_crate=run_manifest["provenance"]["ro_crate"],
        prov=run_manifest["provenance"]["prov"],
    )


def oddball_report_markdown(
    study_spec_reference: str,
    run_manifest: Dict[str, Any],
) -> str:
    bids_intake = run_manifest["bids_intake"]
    return """# Oddball BIDS Intake Report

- Study spec: `{study_spec_reference}`
- Supported path executed: BIDS-aligned intake metadata, validator-aware BIDS status artifact, preregistration export, provenance packaging, reproducibility bundle
- Intake root: {intake_root}
- Dataset description: {dataset_description}
- Participants TSV: {participants_tsv}
- Placeholder participant count: {participant_count}
- Placeholder participant artifacts: {placeholder_files}
- BIDS validator status: {bids_status}
- Required human review points: ethics/privacy review, acquisition-metadata completion, event-timing completion, participant/consent review, empirical-registration completion
- Unsupported requested outputs: {unsupported_outputs}
- Unsupported requested standards: {unsupported_standards}
- Deferred capabilities: {unsupported_capabilities}

This report summarizes what actually ran. The emitted intake tree is placeholder-only metadata and must not be interpreted as an empirical EEG dataset.
""".format(
        study_spec_reference=study_spec_reference,
        intake_root=bids_intake["intake_root"],
        dataset_description=bids_intake["dataset_description"],
        participants_tsv=bids_intake["participants_tsv"],
        participant_count=bids_intake["participant_count"],
        placeholder_files=", ".join(bids_intake["placeholder_files"]),
        bids_status=_status_line(run_manifest["validation"]["bids"]),
        unsupported_outputs=", ".join(run_manifest["unsupported_requested_outputs"]) or "none",
        unsupported_standards=", ".join(run_manifest["unsupported_requested_standards"]) or "none",
        unsupported_capabilities=", ".join(run_manifest["unsupported_capabilities"]),
    )


def oddball_report_bundle_manifest(bids_metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report": "report/report.md",
        "methods": "report/methods.md",
        "commands": "report/commands.sh",
        "environment": "report/environment.lock.yml",
        "checksums": "report/checksums.sha256",
        "validation": {
            "psychds": None,
            "bids": BIDS_VALIDATION_ARTIFACT,
            "hed": None,
        },
        "bids_intake": {
            "root": bids_metadata["intake_root"],
            "dataset_description": bids_metadata["dataset_description"],
            "readme": bids_metadata["readme"],
            "participants_tsv": bids_metadata["participants_tsv"],
            "participants_json": bids_metadata["participants_json"],
            "intake_manifest": bids_metadata["intake_manifest"],
            "placeholder_files": bids_metadata["placeholder_files"],
            "validator_artifact": BIDS_VALIDATION_ARTIFACT,
        },
        "provenance": {
            "ro_crate": RO_CRATE_ARTIFACT,
            "prov": PROV_ARTIFACT,
        },
        "preregistration": {
            "artifact": PREREGISTRATION_ARTIFACT,
        },
        "run_manifest": RUN_MANIFEST_ARTIFACT,
    }


def report_bundle_manifest(
    hed_metadata: Dict[str, Any],
    modeling_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "report": "report/report.md",
        "methods": "report/methods.md",
        "commands": "report/commands.sh",
        "environment": "report/environment.lock.yml",
        "checksums": "report/checksums.sha256",
        "events": {
            "sidecar": hed_metadata["sidecar"],
            "tables": hed_metadata["participant_event_files"],
        },
        "model": {
            "input": modeling_metadata["input_file"],
            "manifest": modeling_metadata["manifest"],
            "bayesian_condition_effects": modeling_metadata["bayesian_condition_effects"],
            "bayesian_diagnostics": modeling_metadata["bayesian_diagnostics"],
            "ddm_status": modeling_metadata["ddm_status"],
        },
        "validation": {
            "psychds": "report/validation/psychds-validator.json",
            "bids": None,
            "hed": "report/validation/hed-validator.json",
        },
        "provenance": {
            "ro_crate": RO_CRATE_ARTIFACT,
            "prov": PROV_ARTIFACT,
        },
        "preregistration": {
            "artifact": PREREGISTRATION_ARTIFACT,
        },
        "run_manifest": RUN_MANIFEST_ARTIFACT,
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


def expected_bundle_artifacts(output_root: Path) -> List[str]:
    artifacts = {file_path.relative_to(output_root).as_posix() for file_path in iter_output_files(output_root)}
    artifacts.update({CHECKSUMS_ARTIFACT, RO_CRATE_ARTIFACT, PROV_ARTIFACT})
    return sorted(artifacts)


def _encoding_format(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".css": "text/css",
        ".csv": "text/csv",
        ".html": "text/html",
        ".json": "application/json",
        ".jsonld": "application/ld+json",
        ".js": "text/javascript",
        ".md": "text/markdown",
        ".sh": "text/x-shellscript",
        ".tsv": "text/tab-separated-values",
        ".xml": "application/xml",
        ".yml": "application/yaml",
        ".yaml": "application/yaml",
    }.get(suffix, "application/octet-stream")


def _relation_id(prefix: str, value: str) -> str:
    return "#{prefix}-{value}".format(
        prefix=prefix,
        value=value.replace("/", "-").replace(".", "-").replace("_", "-"),
    )


def build_ro_crate_metadata(
    study_title: str,
    study_spec_reference: str,
    study_spec_sha256: str,
    expected_files: List[str],
    metadata_name: str = "RO-Crate metadata descriptor for the canonical Flanker behavioral demo bundle",
    dataset_description: str = (
        "Deterministic synthetic-demo Flanker behavioral slice bundle with local "
        "preregistration and machine-readable provenance exports."
    ),
    runner_script: str = "scripts/run_flanker_behavioral_slice.py",
) -> Dict[str, Any]:
    graph: List[Dict[str, Any]] = [
        {
            "@id": RO_CRATE_ARTIFACT,
            "@type": "CreativeWork",
            "name": metadata_name,
            "about": {"@id": "./"},
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.2"},
            "encodingFormat": "application/ld+json",
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": "{title} reproducibility bundle".format(title=study_title),
            "description": dataset_description,
            "hasPart": [{"@id": path} for path in expected_files],
            "isBasedOn": {"@id": "#study-spec"},
            "mentions": [{"@id": "#runner-software"}, {"@id": "#runner-script"}],
        },
        {
            "@id": "https://w3id.org/ro/crate/1.2",
            "@type": "CreativeWork",
            "name": "RO-Crate 1.2",
        },
        {
            "@id": "#study-spec",
            "@type": "File",
            "name": study_spec_reference,
            "description": "Checked-in study specification used to generate this bundle.",
            "encodingFormat": "application/yaml",
            "sha256": study_spec_sha256,
        },
        {
            "@id": "#runner-software",
            "@type": "SoftwareApplication",
            "name": "cogsci-skilllib",
            "version": __version__,
        },
        {
            "@id": "#runner-script",
            "@type": "SoftwareSourceCode",
            "name": runner_script,
            "programmingLanguage": "Python",
            "isPartOf": {"@id": "#runner-software"},
        },
    ]

    for path in expected_files:
        if path == RO_CRATE_ARTIFACT:
            continue
        graph.append(
            {
                "@id": path,
                "@type": "File",
                "name": path,
                "encodingFormat": _encoding_format(path),
            }
        )

    return {
        "@context": "https://w3id.org/ro/crate/1.2/context",
        "@graph": graph,
    }


def build_prov_jsonld(
    study_spec_reference: str,
    study_spec_sha256: str,
    expected_files: List[str],
    activity_name: str = "Canonical Flanker behavioral demo bundle assembly",
) -> Dict[str, Any]:
    entities: Dict[str, Dict[str, Any]] = {
        "#study-spec": {
            "prov:type": "Entity",
            "name": study_spec_reference,
            "encodingFormat": "application/yaml",
            "sha256": study_spec_sha256,
        }
    }
    was_generated_by: Dict[str, Dict[str, str]] = {}
    was_attributed_to: Dict[str, Dict[str, str]] = {}

    for path in expected_files:
        entities[path] = {
            "prov:type": "Entity",
            "path": path,
            "encodingFormat": _encoding_format(path),
        }
        was_generated_by[_relation_id("wasGeneratedBy", path)] = {
            "prov:entity": path,
            "prov:activity": "#bundle-run",
        }
        was_attributed_to[_relation_id("wasAttributedTo", path)] = {
            "prov:entity": path,
            "prov:agent": "#cogsci-skilllib-agent",
        }

    return {
        "@context": [
            "https://openprovenance.org/prov-jsonld/context.jsonld",
            {
                "name": "https://schema.org/name",
                "path": "https://schema.org/path",
                "encodingFormat": "https://schema.org/encodingFormat",
                "sha256": "https://w3id.org/ro/terms#sha256",
            },
        ],
        "entity": entities,
        "activity": {
            "#bundle-run": {
                "prov:type": "Activity",
                "name": activity_name,
            }
        },
        "agent": {
            "#cogsci-skilllib-agent": {
                "prov:type": "SoftwareAgent",
                "name": "cogsci-skilllib",
                "version": __version__,
            }
        },
        "used": {
            "#used-study-spec": {
                "prov:activity": "#bundle-run",
                "prov:entity": "#study-spec",
            }
        },
        "wasGeneratedBy": was_generated_by,
        "wasAttributedTo": was_attributed_to,
        "wasAssociatedWith": {
            "#bundle-association": {
                "prov:activity": "#bundle-run",
                "prov:agent": "#cogsci-skilllib-agent",
            }
        },
    }


def write_checksums(output_root: Path, checksums_path: Path) -> None:
    lines: List[str] = []
    for file_path in iter_output_files(output_root):
        relative_path = file_path.relative_to(output_root)
        if relative_path == Path(CHECKSUMS_ARTIFACT):
            continue
        digest = sha256(file_path.read_bytes()).hexdigest()
        lines.append("{digest}  {path}".format(digest=digest, path=relative_path.as_posix()))
    checksums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
