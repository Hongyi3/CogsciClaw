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


def run_slice(tmp_path: Path, validate_mode: str = "never") -> Path:
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

    for name in ("task", "metadata", "psychds", "report"):
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

    manifest = json.loads((output_dir / "report" / "report_bundle.json").read_text(encoding="utf-8"))
    assert manifest["report"] == "report/report.md"
    assert manifest["methods"] == "report/methods.md"
    assert manifest["validation"]["psychds"] == "report/validation/psychds-validator.json"

    methods = (output_dir / "report" / "methods.md").read_text(encoding="utf-8")
    assert "jsPsych 8.2.2" in methods
    assert "160 trials" in methods
    assert "model_report, preregistration" in methods
    assert "Cognitive Atlas" in methods
    assert "HED" in methods

    run_manifest = json.loads(
        (output_dir / "report" / "provenance" / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert run_manifest["trial_schedule"]["mapping_variants"] == ["A", "B"]
    assert run_manifest["validation"]["study_spec"]["status"] == "passed"
    assert run_manifest["validation"]["psychds"]["status"] == "not_run"
    assert run_manifest["validation"]["report_bundle"]["status"] == "passed"


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
