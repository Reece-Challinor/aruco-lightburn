"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>validate_imports.py</name>
    <version>1.1.0</version>
    <type>tooling_script</type>
    <purpose>Validate critical module imports for pre-commit checks</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

MODULES: Iterable[str] = (
    "app",
    "aruco_generator.core.aruco",
    "aruco_generator.core.drawing",
    "aruco_generator.core.utils",
    "aruco_generator.export.lightburn",
    "aruco_generator.web.web",
    "aruco_generator.web.advanced_web",
    "aruco_generator.web.calibration_web",
)


def main() -> int:
    failures = []
    for module_name in MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append((module_name, exc))

    if failures:
        for module_name, exc in failures:
            print(f"Import failed: {module_name} -> {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
