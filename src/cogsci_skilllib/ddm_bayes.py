from __future__ import annotations

import csv
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


MODEL_INPUT_COLUMNS = [
    "participant_id",
    "session_id",
    "mapping_variant",
    "participant_index",
    "trial_index",
    "condition",
    "condition_code",
    "trial_type",
    "accuracy",
    "rt_ms",
    "rt_seconds",
    "log_rt_seconds",
    "include_rt_model",
    "synthetic",
]

BAYESIAN_TOOL_NAME = "pymc"
DDM_TOOL_NAME = "hddm"
MODELING_SEED = 314159
BAYESIAN_SAMPLE_CONFIG = {
    "chains": 2,
    "cores": 1,
    "draws": 300,
    "tune": 300,
    "target_accept": 0.9,
    "random_seed": MODELING_SEED,
    "progressbar": False,
    "compute_convergence_checks": False,
}


def _json_dump(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MODEL_INPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def _relative_model_path(path: Path) -> str:
    return f"model/{path.name}"


def _condition_code(condition: str) -> str:
    return "1" if condition == "incongruent" else "0"


def _rt_seconds(value: str | int) -> float:
    return float(value) / 1000.0


def _format_float(value: float) -> str:
    return f"{value:.6f}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return value
    if math.isfinite(converted):
        return converted
    return None


def build_model_input_rows(synthetic_tables: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    participant_lookup = {
        table["participant_id"]: str(index)
        for index, table in enumerate(
            sorted(
                synthetic_tables,
                key=lambda item: (
                    item["participant_id"],
                    item["session_id"],
                    item["mapping_variant"],
                ),
            ),
            start=0,
        )
    }
    rows: List[Dict[str, str]] = []
    for table in sorted(
        synthetic_tables,
        key=lambda item: (item["participant_id"], item["session_id"], item["mapping_variant"]),
    ):
        participant_index = participant_lookup[table["participant_id"]]
        for row in sorted(table["rows"], key=lambda item: int(item["trial_index"])):
            rt_seconds = _rt_seconds(row["rt_ms"])
            rows.append(
                {
                    "participant_id": str(row["participant_id"]),
                    "session_id": str(row["session_id"]),
                    "mapping_variant": str(row["mapping_variant"]),
                    "participant_index": participant_index,
                    "trial_index": str(row["trial_index"]),
                    "condition": str(row["condition"]),
                    "condition_code": _condition_code(str(row["condition"])),
                    "trial_type": str(row["trial_type"]),
                    "accuracy": str(row["accuracy"]),
                    "rt_ms": str(row["rt_ms"]),
                    "rt_seconds": _format_float(rt_seconds),
                    "log_rt_seconds": _format_float(math.log(rt_seconds)),
                    "include_rt_model": "true" if int(row["accuracy"]) == 1 else "false",
                    "synthetic": str(row["synthetic"]),
                }
            )
    return rows


def write_model_input(
    model_dir: Path,
    synthetic_tables: List[Dict[str, Any]],
) -> Dict[str, Any]:
    model_dir.mkdir(parents=True, exist_ok=True)
    input_path = model_dir / "model_input.csv"
    rows = build_model_input_rows(synthetic_tables)
    _write_csv(input_path, rows)
    participant_ids = sorted({row["participant_id"] for row in rows})
    return {
        "input_file": _relative_model_path(input_path),
        "row_count": len(rows),
        "participant_count": len(participant_ids),
        "participants": participant_ids,
        "columns": MODEL_INPUT_COLUMNS,
        "rt_model_rows": sum(1 for row in rows if row["include_rt_model"] == "true"),
        "synthetic_demo": True,
    }


def _load_bayesian_runtime() -> Tuple[Dict[str, Any] | None, str | None]:
    try:
        import arviz as az
        import numpy as np
        import pymc as pm
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, f"PyMC / ArviZ runtime unavailable: {exc}"

    return (
        {
            "az": az,
            "np": np,
            "pm": pm,
            "versions": {
                "arviz": getattr(az, "__version__", _package_version("arviz")),
                "numpy": getattr(np, "__version__", _package_version("numpy")),
                "pymc": getattr(pm, "__version__", _package_version("pymc")),
            },
        },
        None,
    )


def _load_ddm_runtime() -> Tuple[Dict[str, Any] | None, str | None]:
    try:
        import hddm
    except ModuleNotFoundError:
        return None, "hddm package not installed."
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, f"HDDM runtime unavailable: {exc}"

    return (
        {
            "hddm": hddm,
            "versions": {
                "hddm": getattr(hddm, "__version__", _package_version("hddm")),
            },
        },
        None,
    )


def _summary_frame_to_dict(frame: Any) -> Dict[str, Dict[str, Any]]:
    if hasattr(frame, "to_dict"):
        payload = frame.to_dict(orient="index")
    else:  # pragma: no cover - defensive guard
        payload = dict(frame)
    return {
        str(row_name): {str(key): _json_safe(value) for key, value in row.items()}
        for row_name, row in payload.items()
    }


def _summary_column(frame: Any, *candidates: str) -> List[float]:
    for candidate in candidates:
        if candidate in frame.columns:
            return [_json_safe(value) for value in frame[candidate].tolist() if _json_safe(value) is not None]
    return []


def _idata_posterior_sizes(inference_data: Any) -> Tuple[int, int]:
    posterior = getattr(inference_data, "posterior", None)
    if posterior is None:
        return 0, 0
    sizes = getattr(posterior, "sizes", {})
    return int(sizes.get("chain", 0)), int(sizes.get("draw", 0))


def _idata_divergences(inference_data: Any, np_module: Any) -> int | None:
    sample_stats = getattr(inference_data, "sample_stats", None)
    if sample_stats is None or "diverging" not in sample_stats:
        return None
    return int(np_module.asarray(sample_stats["diverging"]).sum())


def _effect_summary(az: Any, inference_data: Any, np_module: Any, parameter: str) -> Dict[str, Any]:
    frame = az.summary(inference_data, var_names=[parameter], hdi_prob=0.95)
    rows = _summary_frame_to_dict(frame)
    parameter_row = rows[parameter]
    posterior = np_module.asarray(inference_data.posterior[parameter]).reshape(-1)
    return {
        **parameter_row,
        "posterior_probability_positive": float((posterior > 0).mean()),
    }


def _diagnostics_summary(
    az: Any,
    inference_data: Any,
    np_module: Any,
    *,
    family: str,
    outcome: str,
    observation_count: int,
) -> Dict[str, Any]:
    frame = az.summary(inference_data, hdi_prob=0.95)
    chains, draws = _idata_posterior_sizes(inference_data)
    rhat_values = _summary_column(frame, "r_hat", "rhat")
    ess_bulk_values = _summary_column(frame, "ess_bulk")
    ess_tail_values = _summary_column(frame, "ess_tail")
    return {
        "family": family,
        "outcome": outcome,
        "observations": observation_count,
        "chains": chains,
        "draws_per_chain": draws,
        "divergences": _idata_divergences(inference_data, np_module),
        "rhat_max": max(rhat_values) if rhat_values else None,
        "ess_bulk_min": min(ess_bulk_values) if ess_bulk_values else None,
        "ess_tail_min": min(ess_tail_values) if ess_tail_values else None,
        "parameter_summary": _summary_frame_to_dict(frame),
    }


def _fit_bayesian_models(
    rows: List[Dict[str, str]],
    runtime: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    az = runtime["az"]
    np_module = runtime["np"]
    pm = runtime["pm"]
    participant_ids = sorted({row["participant_id"] for row in rows})
    participant_lookup = {participant_id: index for index, participant_id in enumerate(participant_ids)}
    accuracy_condition = np_module.asarray([int(row["condition_code"]) for row in rows], dtype="int64")
    accuracy_participant = np_module.asarray(
        [participant_lookup[row["participant_id"]] for row in rows],
        dtype="int64",
    )
    accuracy_outcome = np_module.asarray([int(row["accuracy"]) for row in rows], dtype="int64")

    rt_rows = [row for row in rows if row["include_rt_model"] == "true"]
    if not rt_rows:
        raise RuntimeError("No rows were eligible for the RT model.")
    rt_condition = np_module.asarray([int(row["condition_code"]) for row in rt_rows], dtype="int64")
    rt_participant = np_module.asarray(
        [participant_lookup[row["participant_id"]] for row in rt_rows],
        dtype="int64",
    )
    rt_outcome = np_module.asarray([float(row["log_rt_seconds"]) for row in rt_rows], dtype="float64")

    with pm.Model():
        alpha_participant = pm.Normal("alpha_participant", mu=0.0, sigma=1.5, shape=len(participant_ids))
        beta_condition = pm.Normal("beta_condition", mu=0.0, sigma=1.0)
        pm.Bernoulli(
            "accuracy_observed",
            logit_p=alpha_participant[accuracy_participant] + beta_condition * accuracy_condition,
            observed=accuracy_outcome,
        )
        accuracy_inference = pm.sample(return_inferencedata=True, **BAYESIAN_SAMPLE_CONFIG)

    with pm.Model():
        alpha_participant = pm.Normal(
            "alpha_participant",
            mu=float(rt_outcome.mean()),
            sigma=0.5,
            shape=len(participant_ids),
        )
        beta_condition = pm.Normal("beta_condition", mu=0.0, sigma=0.25)
        sigma = pm.HalfNormal("sigma", sigma=0.25)
        pm.Normal(
            "log_rt_seconds_observed",
            mu=alpha_participant[rt_participant] + beta_condition * rt_condition,
            sigma=sigma,
            observed=rt_outcome,
        )
        rt_inference = pm.sample(return_inferencedata=True, **BAYESIAN_SAMPLE_CONFIG)

    effects_artifact = {
        "status": "passed",
        "tool": BAYESIAN_TOOL_NAME,
        "tool_versions": runtime["versions"],
        "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
        "synthetic_demo": True,
        "models": {
            "accuracy": {
                "family": "bernoulli_logit",
                "outcome": "accuracy",
                "condition_effect_parameter": "beta_condition",
                "condition_effect": _effect_summary(
                    az,
                    accuracy_inference,
                    np_module,
                    "beta_condition",
                ),
                "observations": len(rows),
                "participant_count": len(participant_ids),
            },
            "log_rt_seconds": {
                "family": "normal",
                "outcome": "log_rt_seconds",
                "condition_effect_parameter": "beta_condition",
                "condition_effect": _effect_summary(
                    az,
                    rt_inference,
                    np_module,
                    "beta_condition",
                ),
                "observations": len(rt_rows),
                "participant_count": len(participant_ids),
                "subset": "correct trials only",
            },
        },
    }
    diagnostics_artifact = {
        "status": "passed",
        "tool": BAYESIAN_TOOL_NAME,
        "tool_versions": runtime["versions"],
        "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
        "synthetic_demo": True,
        "models": {
            "accuracy": _diagnostics_summary(
                az,
                accuracy_inference,
                np_module,
                family="bernoulli_logit",
                outcome="accuracy",
                observation_count=len(rows),
            ),
            "log_rt_seconds": _diagnostics_summary(
                az,
                rt_inference,
                np_module,
                family="normal",
                outcome="log_rt_seconds",
                observation_count=len(rt_rows),
            ),
        },
    }
    return effects_artifact, diagnostics_artifact


def run_bayesian_models(
    model_input_path: Path,
    mode: str,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    rows = _read_csv(model_input_path)
    checked_models = ["accuracy", "log_rt_seconds"]
    base_summary = {
        "status": "pending",
        "tool": BAYESIAN_TOOL_NAME,
        "requested_mode": mode,
        "tool_available": False,
        "models": checked_models,
        "input_file": _relative_model_path(model_input_path),
        "condition_effects_artifact": "model/bayesian-condition-effects.json",
        "diagnostics_artifact": "model/bayesian-diagnostics.json",
        "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
    }
    if mode == "never":
        reason = "Bayesian fitting disabled by --fit-bayes never."
        tool_versions = {
            "arviz": _package_version("arviz"),
            "numpy": _package_version("numpy"),
            "pymc": _package_version("pymc"),
        }
        artifact = {
            "status": "not_run",
            "tool": BAYESIAN_TOOL_NAME,
            "reason": reason,
            "input_file": _relative_model_path(model_input_path),
            "models": checked_models,
            "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
            "synthetic_demo": True,
            "tool_versions": tool_versions,
        }
        diagnostics = {
            "status": "not_run",
            "tool": BAYESIAN_TOOL_NAME,
            "reason": reason,
            "input_file": _relative_model_path(model_input_path),
            "models": checked_models,
            "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
            "synthetic_demo": True,
            "tool_versions": tool_versions,
        }
        return artifact, diagnostics, {
            **base_summary,
            "status": "not_run",
            "reason": reason,
            "tool_versions": tool_versions,
        }

    runtime, reason = _load_bayesian_runtime()
    if runtime is None:
        tool_versions = {
            "arviz": _package_version("arviz"),
            "numpy": _package_version("numpy"),
            "pymc": _package_version("pymc"),
        }
        if mode == "always":
            raise RuntimeError(reason or "PyMC / ArviZ runtime unavailable.")
        artifact = {
            "status": "not_run",
            "tool": BAYESIAN_TOOL_NAME,
            "reason": reason,
            "input_file": _relative_model_path(model_input_path),
            "models": checked_models,
            "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
            "synthetic_demo": True,
            "tool_versions": tool_versions,
        }
        diagnostics = {
            "status": "not_run",
            "tool": BAYESIAN_TOOL_NAME,
            "reason": reason,
            "input_file": _relative_model_path(model_input_path),
            "models": checked_models,
            "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
            "synthetic_demo": True,
            "tool_versions": tool_versions,
        }
        return artifact, diagnostics, {
            **base_summary,
            "status": "not_run",
            "reason": reason,
            "tool_versions": tool_versions,
        }

    try:
        effects_artifact, diagnostics_artifact = _fit_bayesian_models(rows, runtime)
        effects_artifact["input_file"] = _relative_model_path(model_input_path)
        diagnostics_artifact["input_file"] = _relative_model_path(model_input_path)
        effects_artifact["status"] = "passed"
        diagnostics_artifact["status"] = "passed"
        summary = {
            **base_summary,
            "status": "passed",
            "tool_available": True,
            "tool_versions": runtime["versions"],
        }
        return effects_artifact, diagnostics_artifact, summary
    except Exception as exc:  # pragma: no cover - defensive integration guard
        failure_reason = str(exc)
        artifact = {
            "status": "failed",
            "tool": BAYESIAN_TOOL_NAME,
            "reason": failure_reason,
            "input_file": _relative_model_path(model_input_path),
            "models": checked_models,
            "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
            "synthetic_demo": True,
            "tool_versions": runtime["versions"],
        }
        diagnostics = {
            "status": "failed",
            "tool": BAYESIAN_TOOL_NAME,
            "reason": failure_reason,
            "input_file": _relative_model_path(model_input_path),
            "models": checked_models,
            "sampling": dict(BAYESIAN_SAMPLE_CONFIG),
            "synthetic_demo": True,
            "tool_versions": runtime["versions"],
        }
        return artifact, diagnostics, {
            **base_summary,
            "status": "failed",
            "tool_available": True,
            "tool_versions": runtime["versions"],
            "reason": failure_reason,
        }


def run_ddm_model(
    model_input_path: Path,
    mode: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    base_summary = {
        "status": "pending",
        "tool": DDM_TOOL_NAME,
        "requested_mode": mode,
        "tool_available": False,
        "input_file": _relative_model_path(model_input_path),
        "artifact": "model/ddm-status.json",
    }
    if mode == "never":
        reason = "DDM fitting disabled by --fit-ddm never."
        tool_versions = {"hddm": _package_version("hddm")}
        artifact = {
            "status": "not_run",
            "tool": DDM_TOOL_NAME,
            "reason": reason,
            "input_file": _relative_model_path(model_input_path),
            "tool_versions": tool_versions,
            "synthetic_demo": True,
        }
        return artifact, {
            **base_summary,
            "status": "not_run",
            "reason": reason,
            "tool_versions": tool_versions,
        }

    runtime, reason = _load_ddm_runtime()
    if runtime is None:
        tool_versions = {"hddm": _package_version("hddm")}
        if mode == "always":
            raise RuntimeError(reason or "HDDM runtime unavailable.")
        artifact = {
            "status": "not_run",
            "tool": DDM_TOOL_NAME,
            "reason": reason,
            "input_file": _relative_model_path(model_input_path),
            "tool_versions": tool_versions,
            "synthetic_demo": True,
        }
        return artifact, {
            **base_summary,
            "status": "not_run",
            "reason": reason,
            "tool_versions": tool_versions,
        }

    reason = "DDM fitting is not implemented in this milestone; runtime probe only."
    if mode == "always":
        raise RuntimeError(reason)
    artifact = {
        "status": "not_run",
        "tool": DDM_TOOL_NAME,
        "reason": reason,
        "input_file": _relative_model_path(model_input_path),
        "tool_versions": runtime["versions"],
        "synthetic_demo": True,
    }
    return artifact, {
        **base_summary,
        "status": "not_run",
        "reason": reason,
        "tool_available": True,
        "tool_versions": runtime["versions"],
    }


def write_model_artifacts(
    model_dir: Path,
    synthetic_tables: List[Dict[str, Any]],
    *,
    bayesian_mode: str,
    ddm_mode: str,
) -> Dict[str, Any]:
    input_metadata = write_model_input(model_dir, synthetic_tables)
    model_input_path = model_dir / "model_input.csv"
    bayesian_artifact, diagnostics_artifact, bayesian_summary = run_bayesian_models(
        model_input_path,
        bayesian_mode,
    )
    ddm_artifact, ddm_summary = run_ddm_model(model_input_path, ddm_mode)

    condition_effects_path = model_dir / "bayesian-condition-effects.json"
    diagnostics_path = model_dir / "bayesian-diagnostics.json"
    ddm_status_path = model_dir / "ddm-status.json"
    manifest_path = model_dir / "model_manifest.json"
    _json_dump(condition_effects_path, bayesian_artifact)
    _json_dump(diagnostics_path, diagnostics_artifact)
    _json_dump(ddm_status_path, ddm_artifact)

    manifest = {
        "model_root": "model",
        "synthetic_demo": True,
        "input_file": input_metadata["input_file"],
        "manifest": _relative_model_path(manifest_path),
        "bayesian_condition_effects": _relative_model_path(condition_effects_path),
        "bayesian_diagnostics": _relative_model_path(diagnostics_path),
        "ddm_status": _relative_model_path(ddm_status_path),
        "row_count": input_metadata["row_count"],
        "participant_count": input_metadata["participant_count"],
        "rt_model_rows": input_metadata["rt_model_rows"],
        "bayesian": bayesian_summary,
        "ddm": ddm_summary,
    }
    _json_dump(manifest_path, manifest)
    return manifest
