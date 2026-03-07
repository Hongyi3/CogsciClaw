from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = PACKAGE_ROOT.parents[1]
SCHEMAS_DIR = REPO_ROOT / "schemas"
VENDOR_DIR = PACKAGE_ROOT / "vendor" / "jspsych"
