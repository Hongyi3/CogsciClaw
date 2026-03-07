#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cogsci_skilllib.flanker_demo import (  # noqa: E402
    COLUMN_DEFINITIONS,
    TRIAL_COLUMN_ORDER,
    build_trial_schedule,
    demo_profile,
    generate_synthetic_tables,
    summarize_schedule,
)
from cogsci_skilllib.psychds_curator import (  # noqa: E402
    run_psychds_validator,
    write_psychds_dataset,
)
from cogsci_skilllib.repro_bundle import (  # noqa: E402
    build_run_manifest,
    commands_script,
    environment_lock,
    methods_markdown,
    report_bundle_manifest,
    report_markdown,
    validate_report_bundle,
    write_checksums,
    write_environment_lock,
    write_json,
)
from cogsci_skilllib.study_spec import (  # noqa: E402
    build_validation_artifact,
    validate_study_spec,
)
from cogsci_skilllib.task_jspsych import write_task_artifact  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--validate-psychds",
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


def write_metadata_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRIAL_COLUMN_ORDER)
        writer.writeheader()
        writer.writerows(rows)


def write_metadata_artifacts(
    metadata_dir: Path,
    context_spec: Dict[str, Any],
    profile: Dict[str, Any],
    schedule: List[Dict[str, Any]],
    schedule_summary: Dict[str, Any],
    tables: List[Dict[str, Any]],
) -> None:
    metadata_dir.mkdir(parents=True, exist_ok=True)
    write_json(metadata_dir / "normalized_study_spec.json", context_spec)
    write_json(metadata_dir / "demo_profile.json", profile)
    write_json(metadata_dir / "trial_schedule.json", {"trials": schedule})
    write_json(metadata_dir / "trial_schedule_summary.json", schedule_summary)
    write_json(metadata_dir / "column_definitions.json", COLUMN_DEFINITIONS)

    for table in tables:
        csv_name = "participant-{participant}_session-{session}_trials.csv".format(
            participant=table["participant_id"],
            session=table["session_id"],
        )
        write_metadata_csv(metadata_dir / csv_name, table["rows"])


def main() -> int:
    args = parse_args()
    study_spec_path = Path(args.study_spec)
    output_dir = Path(args.output_dir)
    ensure_empty_output_dir(output_dir)

    task_dir = output_dir / "task"
    metadata_dir = output_dir / "metadata"
    psychds_dir = output_dir / "psychds"
    report_dir = output_dir / "report"
    validation_dir = report_dir / "validation"
    provenance_dir = report_dir / "provenance"
    validation_dir.mkdir(parents=True, exist_ok=True)
    provenance_dir.mkdir(parents=True, exist_ok=True)

    context = validate_study_spec(study_spec_path)
    study_validation = build_validation_artifact(context)
    study_title = context.normalized_spec["study"]["title"]
    study_spec_reference = relative_reference(study_spec_path)
    profile = demo_profile()
    schedule = build_trial_schedule(context.normalized_spec["design"]["trial_count"])
    schedule_summary = summarize_schedule(schedule)
    synthetic_tables = generate_synthetic_tables(schedule)

    write_metadata_artifacts(
        metadata_dir=metadata_dir,
        context_spec=context.normalized_spec,
        profile=profile,
        schedule=schedule,
        schedule_summary=schedule_summary,
        tables=synthetic_tables,
    )

    task_metadata = write_task_artifact(
        task_dir=task_dir,
        study_title=study_title,
        schedule=schedule,
        profile=profile,
        study_spec_sha256=context.spec_sha256,
    )
    psychds_metadata = write_psychds_dataset(
        psychds_dir=psychds_dir,
        study_title=study_title,
        study_spec_reference=study_spec_reference,
        study_spec_sha256=context.spec_sha256,
        synthetic_tables=synthetic_tables,
    )

    psychds_validation_artifact, psychds_validation_summary = run_psychds_validator(
        psychds_dir, args.validate_psychds
    )
    write_json(validation_dir / "study-spec-validation.json", study_validation)
    write_json(validation_dir / "psychds-validator.json", psychds_validation_artifact)

    run_manifest = build_run_manifest(
        study_spec_reference=study_spec_reference,
        study_spec_sha256=context.spec_sha256,
        study_title=study_title,
        demo_profile=profile,
        schedule_summary=schedule_summary,
        task_metadata=task_metadata,
        psychds_metadata=psychds_metadata,
        study_validation=study_validation,
        psychds_validation_summary=psychds_validation_summary,
    )

    manifest = report_bundle_manifest()
    report_bundle_validation = validate_report_bundle(manifest)
    run_manifest["validation"]["report_bundle"]["status"] = (
        "passed" if report_bundle_validation["valid"] else "failed"
    )

    write_json(report_dir / "report_bundle.json", manifest)
    write_json(validation_dir / "report-bundle-validation.json", report_bundle_validation)
    write_json(provenance_dir / "run_manifest.json", run_manifest)

    report_text = report_markdown(study_spec_reference, run_manifest)
    methods_text = methods_markdown(
        study_title=study_title,
        study_spec_reference=study_spec_reference,
        study_spec_sha256=context.spec_sha256,
        run_manifest=run_manifest,
    )
    (report_dir / "report.md").write_text(report_text, encoding="utf-8")
    (report_dir / "methods.md").write_text(methods_text, encoding="utf-8")
    commands_path = report_dir / "commands.sh"
    commands_path.write_text(commands_script(), encoding="utf-8")
    commands_path.chmod(0o755)
    write_environment_lock(report_dir / "environment.lock.yml", environment_lock())
    write_checksums(output_dir, report_dir / "checksums.sha256")

    print(json.dumps({"output_dir": output_dir.as_posix(), "status": "ok"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
