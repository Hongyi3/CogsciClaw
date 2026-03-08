from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_oddball_bids_slice.py"
STUDY_SPEC = ROOT / "examples" / "eeg-oddball" / "study_spec.yaml"


def run_slice(
    tmp_path: Path,
    validate_bids: str = "auto",
    env_override: dict[str, str] | None = None,
) -> Path:
    output_dir = tmp_path / "oddball-output"
    env = dict(os.environ)
    if env_override:
        env.update(env_override)
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--study-spec",
            str(STUDY_SPEC),
            "--output-dir",
            str(output_dir),
            "--validate-bids",
            validate_bids,
        ],
        check=False,
        capture_output=True,
        cwd=ROOT,
        env=env,
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


def _write_fake_validator(bin_dir: Path, returncode: int) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "bids-validator"
    script.write_text(
        """#!/bin/sh
printf '%s\\n' '{{"issues":{{"errors":[],"warnings":[]}},"summary":{{"sessions":0}}}}'
exit {returncode}
""".format(returncode=returncode),
        encoding="utf-8",
    )
    script.chmod(0o755)


def test_oddball_slice_generates_expected_outputs(tmp_path: Path) -> None:
    output_dir = run_slice(tmp_path)

    assert (output_dir / "bids-intake").is_dir()
    assert (output_dir / "report").is_dir()
    assert not list((output_dir / "bids-intake").rglob("*_eeg.json"))
    assert not list((output_dir / "bids-intake").rglob("*_channels.tsv"))
    assert not list((output_dir / "bids-intake").rglob("*_electrodes.tsv"))
    assert not list((output_dir / "bids-intake").rglob("*_events.tsv"))

    dataset_description = json.loads(
        (output_dir / "bids-intake" / "dataset_description.json").read_text(encoding="utf-8")
    )
    assert dataset_description["BIDSVersion"] == "1.11.1"
    assert dataset_description["DatasetType"] == "study"
    assert dataset_description["Name"] == "Auditory oddball EEG intake placeholder dataset"

    participants_tsv = (output_dir / "bids-intake" / "participants.tsv").read_text(encoding="utf-8")
    assert participants_tsv.count("\n") == 25
    assert "sub-placeholder01" in participants_tsv
    assert "sub-placeholder24" in participants_tsv
    participants_json = json.loads(
        (output_dir / "bids-intake" / "participants.json").read_text(encoding="utf-8")
    )
    assert "placeholder_status" in participants_json
    assert "contains_empirical_data" in participants_json

    intake_manifest = json.loads(
        (output_dir / "bids-intake" / "intake_manifest.json").read_text(encoding="utf-8")
    )
    assert intake_manifest["supported_profile"] == "canonical-auditory-oddball-bids-intake-demo"
    assert intake_manifest["participants"]["target_n"] == 24
    assert len(intake_manifest["files"]["placeholder_files"]) == 24

    sample_placeholder = json.loads(
        (
            output_dir
            / "bids-intake"
            / "sub-placeholder01"
            / "eeg"
            / "sub-placeholder01_task-auditoryoddball_intake-placeholder.json"
        ).read_text(encoding="utf-8")
    )
    assert sample_placeholder["artifact_type"] == "cogsci-skilllib-bids-intake-placeholder"
    assert sample_placeholder["placeholder_only"] is True
    assert sample_placeholder["contains_empirical_data"] is False

    manifest = json.loads((output_dir / "report" / "report_bundle.json").read_text(encoding="utf-8"))
    assert manifest["report"] == "report/report.md"
    assert manifest["methods"] == "report/methods.md"
    assert manifest["validation"]["bids"] == "report/validation/bids-validator.json"
    assert manifest["validation"]["psychds"] is None
    assert manifest["validation"]["hed"] is None
    assert manifest["bids_intake"]["root"] == "bids-intake"
    assert manifest["bids_intake"]["dataset_description"] == "bids-intake/dataset_description.json"
    assert manifest["bids_intake"]["participants_tsv"] == "bids-intake/participants.tsv"
    assert manifest["bids_intake"]["participants_json"] == "bids-intake/participants.json"
    assert manifest["bids_intake"]["intake_manifest"] == "bids-intake/intake_manifest.json"
    assert len(manifest["bids_intake"]["placeholder_files"]) == 24
    assert manifest["run_manifest"] == "report/provenance/run_manifest.json"

    methods = (output_dir / "report" / "methods.md").read_text(encoding="utf-8")
    assert "contains_sensitive_data = true" in methods
    assert "placeholder-only metadata" in methods
    assert "BIDS validator status:" in methods
    assert "RO-Crate metadata `report/provenance/ro-crate-metadata.json`" in methods

    report_text = (output_dir / "report" / "report.md").read_text(encoding="utf-8")
    assert "placeholder-only metadata" in report_text
    assert "BIDS validator status:" in report_text

    checksums_text = (output_dir / "report" / "checksums.sha256").read_text(encoding="utf-8")
    assert "bids-intake/dataset_description.json" in checksums_text
    assert "bids-intake/intake_manifest.json" in checksums_text
    assert "report/validation/bids-validator.json" in checksums_text

    run_manifest = json.loads(
        (output_dir / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert run_manifest["supported_slice"]["name"] == "canonical-auditory-oddball-bids-intake-demo"
    assert run_manifest["supported_slice"]["bids_intake"] is True
    assert run_manifest["supported_slice"]["placeholder_metadata_only"] is True
    assert run_manifest["bids_intake"]["participant_count"] == 24
    assert run_manifest["ethics"]["contains_sensitive_data"] is True
    assert run_manifest["validation"]["study_spec"]["status"] == "passed"
    assert run_manifest["validation"]["report_bundle"]["status"] == "passed"
    assert run_manifest["validation"]["bids"]["status"] in {"passed", "failed", "not_run"}
    assert run_manifest["unsupported_requested_outputs"] == []
    assert run_manifest["unsupported_requested_standards"] == ["HED", "MNE", "MNE-BIDS"]
    assert "empirical EEG or MEG signal conversion" in run_manifest["unsupported_capabilities"]
    assert "MNE preprocessing, QC dashboards, or ERP analysis" in run_manifest["unsupported_capabilities"]

    preregistration = json.loads(
        (output_dir / "report" / "preregistration" / "preregistration.json").read_text(encoding="utf-8")
    )
    assert preregistration["supported_profile"] == "canonical-auditory-oddball-bids-intake-demo"
    assert preregistration["placeholder_demo"] is True
    assert preregistration["ethics"]["contains_sensitive_data"] is True
    assert preregistration["intake_contract"]["dataset_root"] == "bids-intake"
    assert preregistration["intake_contract"]["validator_artifact"] == "report/validation/bids-validator.json"
    assert len(preregistration["participants"]["placeholder_subject_ids"]) == 24
    assert {
        item["id"] for item in preregistration["required_human_review"]
    } == {
        "ethics_privacy_review",
        "acquisition_metadata_completion",
        "event_timing_completion",
        "participant_consent_review",
        "empirical_registration_completion",
    }

    bids_validation = json.loads(
        (output_dir / "report" / "validation" / "bids-validator.json").read_text(encoding="utf-8")
    )
    assert bids_validation["status"] in {"passed", "failed", "not_run"}
    if run_manifest["validation"]["bids"]["command_available"]:
        assert bids_validation["status"] in {"passed", "failed"}
    else:
        assert bids_validation["status"] == "not_run"
        assert bids_validation["reason"] == "bids-validator command not found on PATH."


def test_oddball_slice_is_deterministic(tmp_path: Path) -> None:
    first_output = run_slice(tmp_path / "first")
    second_output = run_slice(tmp_path / "second")
    assert file_hashes(first_output) == file_hashes(second_output)


def test_oddball_slice_reports_not_run_without_bids_validator(tmp_path: Path) -> None:
    output_dir = run_slice(tmp_path, env_override={"PATH": ""})
    validator_output = json.loads(
        (output_dir / "report" / "validation" / "bids-validator.json").read_text(encoding="utf-8")
    )
    run_manifest = json.loads(
        (output_dir / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert validator_output["status"] == "not_run"
    assert validator_output["reason"] == "bids-validator command not found on PATH."
    assert run_manifest["validation"]["bids"]["status"] == "not_run"
    assert run_manifest["validation"]["bids"]["command_available"] is False


def test_oddball_slice_uses_local_bids_validator_binary(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin-pass"
    _write_fake_validator(fake_bin, returncode=0)
    output_dir = run_slice(tmp_path / "pass", env_override={"PATH": str(fake_bin)})
    validator_output = json.loads(
        (output_dir / "report" / "validation" / "bids-validator.json").read_text(encoding="utf-8")
    )
    run_manifest = json.loads(
        (output_dir / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert validator_output["status"] == "passed"
    assert validator_output["command_available"] is True
    assert validator_output["validator_output"]["issues"]["errors"] == []
    assert run_manifest["validation"]["bids"]["status"] == "passed"

    fake_bin_fail = tmp_path / "bin-fail"
    _write_fake_validator(fake_bin_fail, returncode=1)
    failed_output = run_slice(tmp_path / "fail", env_override={"PATH": str(fake_bin_fail)})
    failed_validator_output = json.loads(
        (failed_output / "report" / "validation" / "bids-validator.json").read_text(encoding="utf-8")
    )
    failed_manifest = json.loads(
        (failed_output / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert failed_validator_output["status"] == "failed"
    assert failed_validator_output["command_available"] is True
    assert failed_manifest["validation"]["bids"]["status"] == "failed"
