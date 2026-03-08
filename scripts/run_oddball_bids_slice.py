#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cogsci_skilllib.bids_curator import (  # noqa: E402
    run_bids_validator,
    write_bids_intake,
)
from cogsci_skilllib.repro_bundle import (  # noqa: E402
    build_oddball_preregistration_artifact,
    build_oddball_run_manifest,
    build_prov_jsonld,
    build_ro_crate_metadata,
    expected_bundle_artifacts,
    oddball_commands_script,
    oddball_methods_markdown,
    oddball_report_bundle_manifest,
    oddball_report_markdown,
    environment_lock,
    validate_report_bundle,
    write_checksums,
    write_environment_lock,
    write_json,
)
from cogsci_skilllib.study_spec import (  # noqa: E402
    build_validation_artifact,
    validate_study_spec,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--validate-bids",
        choices=("auto", "always", "never"),
        default="auto",
    )
    return parser.parse_args()


def ensure_empty_output_dir(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit("Refusing to write into a non-empty output directory.")
    output_dir.mkdir(parents=True, exist_ok=True)


def relative_reference(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def main() -> int:
    args = parse_args()
    study_spec_path = Path(args.study_spec)
    output_dir = Path(args.output_dir)
    ensure_empty_output_dir(output_dir)

    bids_root = output_dir / "bids-intake"
    report_dir = output_dir / "report"
    preregistration_dir = report_dir / "preregistration"
    validation_dir = report_dir / "validation"
    provenance_dir = report_dir / "provenance"
    preregistration_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)
    provenance_dir.mkdir(parents=True, exist_ok=True)

    context = validate_study_spec(study_spec_path)
    study_validation = build_validation_artifact(context)
    study_title = context.normalized_spec["study"]["title"]
    study_spec_reference = relative_reference(study_spec_path)

    bids_metadata = write_bids_intake(
        bids_root=bids_root,
        normalized_spec=context.normalized_spec,
        study_spec_reference=study_spec_reference,
        study_spec_sha256=context.spec_sha256,
    )
    bids_validation_artifact, bids_validation_summary = run_bids_validator(
        bids_root=bids_root,
        mode=args.validate_bids,
    )

    write_json(validation_dir / "study-spec-validation.json", study_validation)
    write_json(validation_dir / "bids-validator.json", bids_validation_artifact)

    run_manifest = build_oddball_run_manifest(
        study_spec_reference=study_spec_reference,
        study_spec_sha256=context.spec_sha256,
        study_title=study_title,
        supported_profile_name=context.supported_profile["id"],
        normalized_spec=context.normalized_spec,
        bids_metadata=bids_metadata,
        study_validation=study_validation,
        bids_validation_summary=bids_validation_summary,
    )

    manifest = oddball_report_bundle_manifest(bids_metadata)
    report_bundle_validation = validate_report_bundle(manifest)
    run_manifest["validation"]["report_bundle"]["status"] = (
        "passed" if report_bundle_validation["valid"] else "failed"
    )

    write_json(report_dir / "report_bundle.json", manifest)
    write_json(validation_dir / "report-bundle-validation.json", report_bundle_validation)
    write_json(provenance_dir / "run_manifest.json", run_manifest)

    preregistration = build_oddball_preregistration_artifact(
        normalized_spec=context.normalized_spec,
        study_spec_reference=study_spec_reference,
        study_spec_sha256=context.spec_sha256,
        run_manifest=run_manifest,
    )
    write_json(preregistration_dir / "preregistration.json", preregistration)

    (report_dir / "report.md").write_text(
        oddball_report_markdown(study_spec_reference, run_manifest),
        encoding="utf-8",
    )
    (report_dir / "methods.md").write_text(
        oddball_methods_markdown(
            study_title=study_title,
            study_spec_reference=study_spec_reference,
            study_spec_sha256=context.spec_sha256,
            run_manifest=run_manifest,
        ),
        encoding="utf-8",
    )
    commands_path = report_dir / "commands.sh"
    commands_path.write_text(oddball_commands_script(), encoding="utf-8")
    commands_path.chmod(0o755)
    write_environment_lock(report_dir / "environment.lock.yml", environment_lock())

    bundle_artifacts = expected_bundle_artifacts(output_dir)
    write_json(
        provenance_dir / "ro-crate-metadata.json",
        build_ro_crate_metadata(
            study_title=study_title,
            study_spec_reference=study_spec_reference,
            study_spec_sha256=context.spec_sha256,
            expected_files=bundle_artifacts,
            metadata_name="RO-Crate metadata descriptor for the canonical oddball BIDS intake bundle",
            dataset_description=(
                "Deterministic placeholder-only auditory oddball EEG intake bundle with "
                "validator-aware status, preregistration export, and machine-readable provenance exports."
            ),
            runner_script="scripts/run_oddball_bids_slice.py",
        ),
    )
    write_json(
        provenance_dir / "prov.jsonld",
        build_prov_jsonld(
            study_spec_reference=study_spec_reference,
            study_spec_sha256=context.spec_sha256,
            expected_files=bundle_artifacts,
            activity_name="Canonical oddball BIDS intake bundle assembly",
        ),
    )
    write_checksums(output_dir, report_dir / "checksums.sha256")

    print(json.dumps({"output_dir": output_dir.as_posix(), "status": "ok"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
