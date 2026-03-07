from __future__ import annotations

import json
from pathlib import Path

from cogsci_skilllib import __version__


def test_version_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_catalog_has_unique_slugs() -> None:
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "skills" / "catalog.json").read_text(encoding="utf-8"))
    slugs = [skill["slug"] for skill in data["skills"]]
    assert len(slugs) == len(set(slugs))
