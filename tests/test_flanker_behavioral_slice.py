from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_flanker_behavioral_slice.py"
STUDY_SPEC = ROOT / "examples" / "flanker-behavioral" / "study_spec.yaml"


def run_slice(
    tmp_path: Path,
    validate_mode: str = "never",
    validate_hed: str = "auto",
    fit_bayes: str = "auto",
    fit_ddm: str = "auto",
) -> Path:
    output_dir = tmp_path / "flanker-output"
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--study-spec",
            str(STUDY_SPEC),
            "--output-dir",
            str(output_dir),
            "--validate-psychds",
            validate_mode,
            "--validate-hed",
            validate_hed,
            "--fit-bayes",
            fit_bayes,
            "--fit-ddm",
            fit_ddm,
        ],
        check=False,
        capture_output=True,
        cwd=ROOT,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    return output_dir


def file_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == "report/checksums.sha256":
            continue
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def test_flanker_slice_generates_expected_outputs(tmp_path: Path) -> None:
    output_dir = run_slice(tmp_path)

    for name in ("events", "task", "metadata", "model", "psychds", "report"):
        assert (output_dir / name).is_dir()

    trials = json.loads((output_dir / "metadata" / "trial_schedule.json").read_text(encoding="utf-8"))[
        "trials"
    ]
    assert len(trials) == 160
    condition_counts = {"congruent": 0, "incongruent": 0}
    for trial in trials:
        condition_counts[trial["condition"]] += 1
    assert condition_counts == {"congruent": 80, "incongruent": 80}

    participant_one = (output_dir / "metadata" / "participant-demo001_session-1_trials.csv").read_text(
        encoding="utf-8"
    )
    participant_two = (output_dir / "metadata" / "participant-demo002_session-1_trials.csv").read_text(
        encoding="utf-8"
    )
    assert participant_one.count("\n") == 161
    assert participant_two.count("\n") == 161
    assert "demo001" in participant_one
    assert "demo002" in participant_two

    sidecar = json.loads((output_dir / "events" / "flanker_events.json").read_text(encoding="utf-8"))
    assert "HED" in sidecar
    assert "event_type" in sidecar

    participant_events = (output_dir / "events" / "participant-demo001_session-1_events.tsv").read_text(
        encoding="utf-8"
    )
    assert participant_events.count("\n") == 321
    assert "\tstimulus\t" in participant_events
    assert "\tresponse\t" in participant_events

    model_manifest = json.loads((output_dir / "model" / "model_manifest.json").read_text(encoding="utf-8"))
    assert model_manifest["input_file"] == "model/model_input.csv"
    assert model_manifest["row_count"] == 320
    assert model_manifest["rt_model_rows"] == 300
    assert model_manifest["bayesian"]["condition_effects_artifact"] == "model/bayesian-condition-effects.json"
    assert model_manifest["bayesian"]["diagnostics_artifact"] == "model/bayesian-diagnostics.json"
    assert model_manifest["ddm"]["artifact"] == "model/ddm-status.json"

    manifest = json.loads((output_dir / "report" / "report_bundle.json").read_text(encoding="utf-8"))
    assert manifest["report"] == "report/report.md"
    assert manifest["methods"] == "report/methods.md"
    assert manifest["events"]["sidecar"] == "events/flanker_events.json"
    assert len(manifest["events"]["tables"]) == 2
    assert manifest["model"]["input"] == "model/model_input.csv"
    assert manifest["model"]["manifest"] == "model/model_manifest.json"
    assert manifest["model"]["ddm_status"] == "model/ddm-status.json"
    assert manifest["preregistration"]["artifact"] == "report/preregistration/preregistration.json"
    assert manifest["provenance"]["ro_crate"] == "report/provenance/ro-crate-metadata.json"
    assert manifest["provenance"]["prov"] == "report/provenance/prov.jsonld"
    assert manifest["run_manifest"] == "report/provenance/run_manifest.json"
    assert manifest["validation"]["hed"] == "report/validation/hed-validator.json"
    assert manifest["validation"]["psychds"] == "report/validation/psychds-validator.json"

    methods = (output_dir / "report" / "methods.md").read_text(encoding="utf-8")
    assert "jsPsych 8.2.2" in methods
    assert "160 trials" in methods
    assert "Bayesian fitting status:" in methods
    assert "DDM status:" in methods
    assert "Unsupported requested outputs for this study spec: none." in methods
    assert "Cognitive Atlas" in methods
    assert "HED-oriented event artifacts were written under `events/`" in methods
    assert "HED validation status:" in methods
    assert "Required human review points remain explicit in `report/preregistration/preregistration.json`" in methods
    assert "RO-Crate metadata `report/provenance/ro-crate-metadata.json`" in methods
    assert "PROV JSON-LD metadata `report/provenance/prov.jsonld`" in methods

    report_text = (output_dir / "report" / "report.md").read_text(encoding="utf-8")
    assert "Bayesian condition-effects artifact:" in report_text
    assert "DDM status:" in report_text
    assert "Preregistration artifact: report/preregistration/preregistration.json" in report_text
    assert "RO-Crate metadata: report/provenance/ro-crate-metadata.json" in report_text
    assert "PROV JSON-LD: report/provenance/prov.jsonld" in report_text

    checksums_text = (output_dir / "report" / "checksums.sha256").read_text(encoding="utf-8")
    assert "report/preregistration/preregistration.json" in checksums_text
    assert "report/provenance/ro-crate-metadata.json" in checksums_text
    assert "report/provenance/prov.jsonld" in checksums_text

    run_manifest = json.loads(
        (output_dir / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert run_manifest["trial_schedule"]["mapping_variants"] == ["A", "B"]
    assert run_manifest["supported_slice"]["hed_annotation"] is True
    assert run_manifest["supported_slice"]["model_artifacts"] is True
    assert run_manifest["supported_slice"]["preregistration_export"] is True
    assert run_manifest["supported_slice"]["ro_crate_export"] is True
    assert run_manifest["supported_slice"]["prov_export"] is True
    assert run_manifest["hed"]["sidecar"] == "events/flanker_events.json"
    assert len(run_manifest["hed"]["participant_event_files"]) == 2
    assert run_manifest["modeling"]["input_file"] == "model/model_input.csv"
    assert run_manifest["modeling"]["bayesian"]["condition_effects_artifact"] == "model/bayesian-condition-effects.json"
    assert run_manifest["modeling"]["ddm"]["artifact"] == "model/ddm-status.json"
    assert run_manifest["preregistration"]["artifact"] == "report/preregistration/preregistration.json"
    assert run_manifest["provenance"]["run_manifest"] == "report/provenance/run_manifest.json"
    assert run_manifest["provenance"]["ro_crate"] == "report/provenance/ro-crate-metadata.json"
    assert run_manifest["provenance"]["prov"] == "report/provenance/prov.jsonld"
    assert run_manifest["validation"]["study_spec"]["status"] == "passed"
    assert run_manifest["validation"]["hed"]["status"] in {"passed", "failed", "not_run"}
    assert run_manifest["validation"]["psychds"]["status"] == "not_run"
    assert run_manifest["validation"]["report_bundle"]["status"] == "passed"
    assert run_manifest["unsupported_requested_outputs"] == []
    assert run_manifest["unsupported_requested_standards"] == ["Cognitive Atlas"]
    assert "registry or API preregistration submission" in run_manifest["unsupported_capabilities"]
    assert "validator-backed RO-Crate / PROV conformance claims" in run_manifest["unsupported_capabilities"]
    assert "preregistration exports" not in run_manifest["unsupported_capabilities"]
    assert "RO-Crate packaging" not in run_manifest["unsupported_capabilities"]
    assert "PROV packaging" not in run_manifest["unsupported_capabilities"]

    preregistration = json.loads(
        (output_dir / "report" / "preregistration" / "preregistration.json").read_text(encoding="utf-8")
    )
    assert preregistration["artifact_type"] == "cogsci-skilllib-preregistration-demo"
    assert preregistration["supported_profile"] == "canonical-flanker-behavioral-demo"
    assert preregistration["synthetic_demo"] is True
    assert preregistration["study_spec"]["path"] == "examples/flanker-behavioral/study_spec.yaml"
    assert preregistration["study_spec"]["schema"] == "schemas/study-spec.schema.yaml"
    assert preregistration["requested_outputs"]["requested"]["preregistration"] is True
    assert preregistration["requested_outputs"]["unsupported_requested_outputs"] == []
    assert preregistration["requested_outputs"]["unsupported_requested_standards"] == ["Cognitive Atlas"]
    assert preregistration["implemented_analysis_contract"]["synthetic_demo_only"] is True
    assert preregistration["implemented_analysis_contract"]["ddm_runtime_probe"]["artifact"] == "model/ddm-status.json"
    assert {
        item["id"] for item in preregistration["required_human_review"]
    } == {
        "ethics_privacy_review",
        "task_validity_timing_review",
        "participant_eligibility_exclusion_review",
        "construct_mapping_review",
        "empirical_registration_completion",
    }
    supported_claim_ids = {item["id"] for item in preregistration["supported_claims"]}
    assert "local_preregistration_export_emitted" in supported_claim_ids
    assert "machine_readable_provenance_exports_emitted" in supported_claim_ids
    unsupported_claim_ids = {item["id"] for item in preregistration["unsupported_claims"]}
    assert "cognitive_atlas_mappings_unsupported" in unsupported_claim_ids
    assert "ddm_fitting_not_supported" in unsupported_claim_ids
    assert "registry_submission_not_supported" in unsupported_claim_ids
    assert "provenance_validation_not_supported" in unsupported_claim_ids
    if run_manifest["modeling"]["bayesian"]["status"] == "passed":
        assert "bayesian_baseline_executed_on_this_runtime" in supported_claim_ids
    else:
        assert "bayesian_execution_runtime_limited" in unsupported_claim_ids

    ro_crate = json.loads(
        (output_dir / "report" / "provenance" / "ro-crate-metadata.json").read_text(encoding="utf-8")
    )
    assert ro_crate["@context"] == "https://w3id.org/ro/crate/1.2/context"
    graph = {item["@id"]: item for item in ro_crate["@graph"]}
    assert graph["report/provenance/ro-crate-metadata.json"]["@type"] == "CreativeWork"
    assert graph["./"]["@type"] == "Dataset"
    assert graph["#study-spec"]["@type"] == "File"
    assert graph["#runner-software"]["@type"] == "SoftwareApplication"
    assert graph["#runner-script"]["@type"] == "SoftwareSourceCode"
    has_part_ids = {entry["@id"] for entry in graph["./"]["hasPart"]}
    assert "report/preregistration/preregistration.json" in has_part_ids
    assert "report/provenance/prov.jsonld" in has_part_ids
    assert "report/checksums.sha256" in has_part_ids
    assert graph["report/report.md"]["@type"] == "File"

    prov = json.loads((output_dir / "report" / "provenance" / "prov.jsonld").read_text(encoding="utf-8"))
    assert len(prov["activity"]) == 1
    assert len(prov["agent"]) == 1
    assert "#bundle-run" in prov["activity"]
    assert "#cogsci-skilllib-agent" in prov["agent"]
    assert "#study-spec" in prov["entity"]
    assert "report/preregistration/preregistration.json" in prov["entity"]
    assert prov["used"]["#used-study-spec"]["prov:entity"] == "#study-spec"
    assert prov["used"]["#used-study-spec"]["prov:activity"] == "#bundle-run"
    assert any(
        relation["prov:entity"] == "report/report.md" and relation["prov:activity"] == "#bundle-run"
        for relation in prov["wasGeneratedBy"].values()
    )
    assert any(
        relation["prov:entity"] == "report/report.md"
        and relation["prov:agent"] == "#cogsci-skilllib-agent"
        for relation in prov["wasAttributedTo"].values()
    )

    hed_validation = json.loads(
        (output_dir / "report" / "validation" / "hed-validator.json").read_text(encoding="utf-8")
    )
    assert hed_validation["status"] in {"passed", "failed", "not_run"}
    if run_manifest["validation"]["hed"]["tool_available"]:
        assert hed_validation["status"] in {"passed", "failed"}
    else:
        assert hed_validation["status"] == "not_run"
        assert hed_validation["reason"] == "hedtools package not installed."

    bayesian_effects = json.loads(
        (output_dir / "model" / "bayesian-condition-effects.json").read_text(encoding="utf-8")
    )
    bayesian_diagnostics = json.loads(
        (output_dir / "model" / "bayesian-diagnostics.json").read_text(encoding="utf-8")
    )
    ddm_status = json.loads((output_dir / "model" / "ddm-status.json").read_text(encoding="utf-8"))
    assert bayesian_effects["status"] in {"passed", "failed", "not_run"}
    assert bayesian_diagnostics["status"] in {"passed", "failed", "not_run"}
    assert ddm_status["status"] == "not_run"
    if run_manifest["modeling"]["bayesian"]["tool_available"]:
        assert bayesian_effects["status"] in {"passed", "failed"}
    else:
        assert bayesian_effects["status"] == "not_run"
        assert "PyMC / ArviZ runtime unavailable:" in bayesian_effects["reason"]
    if run_manifest["modeling"]["ddm"]["tool_available"]:
        assert ddm_status["reason"] == "DDM fitting is not implemented in this milestone; runtime probe only."
    else:
        assert ddm_status["reason"] == "hddm package not installed."


def test_flanker_slice_is_deterministic(tmp_path: Path) -> None:
    first_output = run_slice(tmp_path / "first")
    second_output = run_slice(tmp_path / "second")

    assert file_hashes(first_output) == file_hashes(second_output)


@pytest.mark.skipif(shutil.which("validate") is None, reason="psychds-validator not installed")
def test_flanker_slice_runs_official_psychds_validator(tmp_path: Path) -> None:
    output_dir = run_slice(tmp_path, validate_mode="always")
    run_manifest = json.loads(
        (output_dir / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert run_manifest["validation"]["psychds"]["status"] == "passed"

    validator_output = json.loads(
        (output_dir / "report" / "validation" / "psychds-validator.json").read_text(encoding="utf-8")
    )
    assert isinstance(validator_output, dict)
