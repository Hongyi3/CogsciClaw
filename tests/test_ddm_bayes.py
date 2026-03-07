from __future__ import annotations

import json
from pathlib import Path

import pytest

from cogsci_skilllib import ddm_bayes
from cogsci_skilllib.flanker_demo import build_trial_schedule, generate_synthetic_tables


def build_model_fixture(tmp_path: Path) -> dict[str, object]:
    schedule = build_trial_schedule(160)
    synthetic_tables = generate_synthetic_tables(schedule)
    model_dir = tmp_path / "model"
    input_metadata = ddm_bayes.write_model_input(model_dir, synthetic_tables)
    return {
        "model_dir": model_dir,
        "input_metadata": input_metadata,
        "input_path": model_dir / "model_input.csv",
    }


def test_write_model_input_outputs_expected_contract(tmp_path: Path) -> None:
    fixture = build_model_fixture(tmp_path)
    input_metadata = fixture["input_metadata"]
    input_path = fixture["input_path"]

    assert input_metadata["input_file"] == "model/model_input.csv"
    assert input_metadata["row_count"] == 320
    assert input_metadata["participant_count"] == 2
    assert input_metadata["rt_model_rows"] == 300
    assert input_metadata["columns"] == ddm_bayes.MODEL_INPUT_COLUMNS

    lines = input_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 321
    assert lines[0].split(",") == ddm_bayes.MODEL_INPUT_COLUMNS
    assert "demo001" in lines[1]
    assert ",0," in lines[1] or ",1," in lines[1]


def test_run_bayesian_models_never_returns_not_run(tmp_path: Path) -> None:
    fixture = build_model_fixture(tmp_path)

    effects, diagnostics, summary = ddm_bayes.run_bayesian_models(
        fixture["input_path"],
        mode="never",
    )

    assert effects["status"] == "not_run"
    assert diagnostics["status"] == "not_run"
    assert summary["status"] == "not_run"
    assert effects["reason"] == "Bayesian fitting disabled by --fit-bayes never."


def test_run_bayesian_models_auto_without_runtime_returns_not_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fixture = build_model_fixture(tmp_path)
    monkeypatch.setattr(
        ddm_bayes,
        "_load_bayesian_runtime",
        lambda: (None, "PyMC / ArviZ runtime unavailable: broken runtime"),
    )

    effects, diagnostics, summary = ddm_bayes.run_bayesian_models(
        fixture["input_path"],
        mode="auto",
    )

    assert effects["status"] == "not_run"
    assert diagnostics["status"] == "not_run"
    assert summary["status"] == "not_run"
    assert effects["reason"] == "PyMC / ArviZ runtime unavailable: broken runtime"
    assert summary["reason"] == "PyMC / ArviZ runtime unavailable: broken runtime"


def test_run_bayesian_models_simulated_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fixture = build_model_fixture(tmp_path)
    monkeypatch.setattr(
        ddm_bayes,
        "_load_bayesian_runtime",
        lambda: (
            {
                "versions": {
                    "arviz": "0.23.0",
                    "numpy": "2.0.0",
                    "pymc": "5.9.0",
                }
            },
            None,
        ),
    )
    monkeypatch.setattr(
        ddm_bayes,
        "_fit_bayesian_models",
        lambda rows, runtime: (
            {
                "status": "passed",
                "tool": "pymc",
                "tool_versions": runtime["versions"],
                "synthetic_demo": True,
                "models": {
                    "accuracy": {
                        "condition_effect": {"mean": -0.1},
                    },
                    "log_rt_seconds": {
                        "condition_effect": {"mean": 0.2},
                    },
                },
            },
            {
                "status": "passed",
                "tool": "pymc",
                "tool_versions": runtime["versions"],
                "synthetic_demo": True,
                "models": {
                    "accuracy": {"rhat_max": 1.01},
                    "log_rt_seconds": {"rhat_max": 1.0},
                },
            },
        ),
    )

    effects, diagnostics, summary = ddm_bayes.run_bayesian_models(
        fixture["input_path"],
        mode="auto",
    )

    assert effects["status"] == "passed"
    assert diagnostics["status"] == "passed"
    assert summary["status"] == "passed"
    assert summary["tool_versions"]["pymc"] == "5.9.0"
    assert effects["input_file"] == "model/model_input.csv"
    assert diagnostics["input_file"] == "model/model_input.csv"


def test_run_bayesian_models_simulated_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fixture = build_model_fixture(tmp_path)
    monkeypatch.setattr(
        ddm_bayes,
        "_load_bayesian_runtime",
        lambda: (
            {
                "versions": {
                    "arviz": "0.23.0",
                    "numpy": "2.0.0",
                    "pymc": "5.9.0",
                }
            },
            None,
        ),
    )
    monkeypatch.setattr(
        ddm_bayes,
        "_fit_bayesian_models",
        lambda rows, runtime: (_ for _ in ()).throw(RuntimeError("sampling failed")),
    )

    effects, diagnostics, summary = ddm_bayes.run_bayesian_models(
        fixture["input_path"],
        mode="auto",
    )

    assert effects["status"] == "failed"
    assert diagnostics["status"] == "failed"
    assert summary["status"] == "failed"
    assert effects["reason"] == "sampling failed"
    assert summary["reason"] == "sampling failed"


def test_run_ddm_model_auto_without_runtime_returns_not_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fixture = build_model_fixture(tmp_path)
    monkeypatch.setattr(ddm_bayes, "_load_ddm_runtime", lambda: (None, "hddm package not installed."))

    artifact, summary = ddm_bayes.run_ddm_model(
        fixture["input_path"],
        mode="auto",
    )

    assert artifact["status"] == "not_run"
    assert summary["status"] == "not_run"
    assert artifact["reason"] == "hddm package not installed."


def test_write_model_artifacts_writes_manifest_and_status_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    schedule = build_trial_schedule(160)
    synthetic_tables = generate_synthetic_tables(schedule)
    monkeypatch.setattr(
        ddm_bayes,
        "_load_bayesian_runtime",
        lambda: (None, "PyMC / ArviZ runtime unavailable: broken runtime"),
    )
    monkeypatch.setattr(ddm_bayes, "_load_ddm_runtime", lambda: (None, "hddm package not installed."))

    manifest = ddm_bayes.write_model_artifacts(
        tmp_path / "model",
        synthetic_tables,
        bayesian_mode="auto",
        ddm_mode="auto",
    )

    assert manifest["input_file"] == "model/model_input.csv"
    assert manifest["bayesian"]["status"] == "not_run"
    assert manifest["ddm"]["status"] == "not_run"
    assert manifest["bayesian_diagnostics"] == "model/bayesian-diagnostics.json"

    manifest_payload = json.loads((tmp_path / "model" / "model_manifest.json").read_text(encoding="utf-8"))
    assert manifest_payload["row_count"] == 320
    assert manifest_payload["bayesian"]["reason"] == "PyMC / ArviZ runtime unavailable: broken runtime"
