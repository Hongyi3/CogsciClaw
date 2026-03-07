from __future__ import annotations

import json
from pathlib import Path

import pytest

from cogsci_skilllib.flanker_demo import build_trial_schedule, demo_profile, generate_synthetic_tables
from cogsci_skilllib import hed_annotator


def build_hed_fixture(tmp_path: Path) -> dict:
    schedule = build_trial_schedule(160)
    synthetic_tables = generate_synthetic_tables(schedule)
    events_dir = tmp_path / "events"
    return hed_annotator.write_hed_events(events_dir, synthetic_tables, demo_profile())


def test_write_hed_events_outputs_expected_contract(tmp_path: Path) -> None:
    hed_metadata = build_hed_fixture(tmp_path)

    assert hed_metadata["schema_version"] == "8.4.0"
    assert hed_metadata["sidecar"] == "events/flanker_events.json"
    assert hed_metadata["rows_per_trial"] == 2
    assert len(hed_metadata["participant_event_files"]) == 2

    sidecar = json.loads((tmp_path / hed_metadata["sidecar"]).read_text(encoding="utf-8"))
    assert sidecar["event_type"]["Description"].startswith("Whether the row represents")
    assert sidecar["HED"]["Description"].startswith("Row-specific HED string")

    participant_path = tmp_path / hed_metadata["participant_event_files"][0]
    lines = participant_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 321
    assert lines[0].split("\t") == hed_annotator.EVENT_COLUMNS
    assert "Sensory-event" in lines[1]
    assert "Participant-response" in lines[2]


def test_run_hed_validator_never_returns_not_run(tmp_path: Path) -> None:
    hed_metadata = build_hed_fixture(tmp_path)

    artifact, summary = hed_annotator.run_hed_validator(tmp_path, hed_metadata, mode="never")

    assert artifact["status"] == "not_run"
    assert summary["status"] == "not_run"
    assert artifact["reason"] == "Validation disabled by --validate-hed never."


def test_run_hed_validator_auto_without_runtime_returns_not_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    hed_metadata = build_hed_fixture(tmp_path)
    monkeypatch.setattr(hed_annotator, "_load_hed_runtime", lambda: None)

    artifact, summary = hed_annotator.run_hed_validator(tmp_path, hed_metadata, mode="auto")

    assert artifact["status"] == "not_run"
    assert summary["status"] == "not_run"
    assert artifact["reason"] == "hedtools package not installed."
    assert summary["tool_available"] is False


def test_run_hed_validator_simulated_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    hed_metadata = build_hed_fixture(tmp_path)
    calls: list[str] = []

    class FakeSidecar:
        def __init__(self, files: str, name: str | None = None):
            self.files = files
            self.name = name

        def validate(self, schema: object, name: str | None = None) -> list[dict]:
            return []

    class FakeTabularInput:
        def __init__(self, file: str | None = None, sidecar: object | None = None, name: str | None = None):
            self.file = file
            self.sidecar = sidecar
            self.name = name

        def validate(self, schema: object, name: str | None = None) -> list[dict]:
            return []

    monkeypatch.setattr(
        hed_annotator,
        "_load_hed_runtime",
        lambda: {
            "Sidecar": FakeSidecar,
            "TabularInput": FakeTabularInput,
            "load_schema": lambda path: calls.append(path) or object(),
            "version": "0.7.1",
        },
    )

    artifact, summary = hed_annotator.run_hed_validator(tmp_path, hed_metadata, mode="auto")

    assert calls == [hed_annotator.HED_SCHEMA_PATH.as_posix()]
    assert artifact["status"] == "passed"
    assert artifact["issue_count"] == 0
    assert summary["status"] == "passed"
    assert summary["issue_count"] == 0


def test_run_hed_validator_simulated_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    hed_metadata = build_hed_fixture(tmp_path)

    class FakeSidecar:
        def __init__(self, files: str, name: str | None = None):
            self.files = files
            self.name = name

        def validate(self, schema: object, name: str | None = None) -> list[dict]:
            return [{"code": "SIDECAR_ERROR", "message": "bad sidecar"}]

    class FakeTabularInput:
        def __init__(self, file: str | None = None, sidecar: object | None = None, name: str | None = None):
            self.file = file
            self.sidecar = sidecar
            self.name = name

        def validate(self, schema: object, name: str | None = None) -> list[dict]:
            return [{"code": "ROW_ERROR", "message": Path(self.file).name}]

    monkeypatch.setattr(
        hed_annotator,
        "_load_hed_runtime",
        lambda: {
            "Sidecar": FakeSidecar,
            "TabularInput": FakeTabularInput,
            "load_schema": lambda path: object(),
            "version": "0.7.1",
        },
    )

    artifact, summary = hed_annotator.run_hed_validator(tmp_path, hed_metadata, mode="auto")

    assert artifact["status"] == "failed"
    assert artifact["issue_count"] == 3
    assert artifact["sidecar"]["issue_count"] == 1
    assert summary["status"] == "failed"
    assert summary["issue_count"] == 3
