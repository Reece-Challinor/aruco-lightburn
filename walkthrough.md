<!--
<ai_agent_documentation>
  <file_meta>
    <name>walkthrough.md</name>
    <version>1.1.0</version>
    <type>delivery_report</type>
    <purpose>Summarize completed work, tests, and recommended commits</purpose>
    <last_updated>2026-02-07</last_updated>
    <maintainer>Codex (Senior CV Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Walkthrough

Date: 2026-02-07

## Summary
- Persisted AprilTag single patterns for export and normalized calibration responses.
- Refactored calibration page interactions into a managed controller with accessible selection.
- Added advanced export controls (DXF/STL) with isolated state from simple generation.
- Deduplicated advanced preview logic and aligned validation.
- Added PDF outer-border rendering support for advanced exports.
- Extracted calibration-specific styling and introduced UI smoke tests.

## Changes
- `aruco_generator/calibration/calibration.py`: Added physical dimensions for AprilTag metadata and YAML export support for AprilTag patterns.
- `aruco_generator/web/calibration_web.py`: Persist AprilTag singles, normalize responses, and add metadata headers.
- `aruco_generator/web/advanced_web.py`: Shared advanced preview builder, centralized validation, and added generation-parameter exports for DXF/STL.
- `aruco_generator/web/web.py`: Reused advanced preview builder and added PDF outer-border rendering params.
- `aruco_generator/export/exporters.py`: Added PDF outer-border render option.
- `static/js/pages/generate.js`: Separate simple/advanced export state and add advanced export controls (DXF/STL).
- `templates/generate.html`: Added advanced export dropdown options.
- `templates/calibration.html`: Removed inline handlers/styles and added metadata header.
- `static/js/pages/calibration.js`: Replaced globals with `CalibrationManager`.
- `static/css/calibration.css`: New calibration styles.
- `tests/test_ui_pages.py`: New UI smoke tests.
- `tests/test_api.py`: Added advanced export coverage for DXF/STL generation params.
- `AI_NAVIGATION.xml`: Updated line references and metadata version.
- `CHANGELOG.md`, `pyproject.toml`, `aruco_generator/__init__.py`: Bumped version to 2.1.0.
- `.github/workflows/deploy.yml`: Added UI smoke tests to CI.
- `implementation_plan.md`: Extended Phase 5 with advanced exports and PDF border.
- `AGENTS.md`: Fully rewritten to match current workflow and versioning.

## Tests
- `make format` (passed)
- `make lint` (passed)
- `make unit-test` (passed; pytest-asyncio deprecation warnings)
- `make integration` (passed; pytest-asyncio deprecation warnings)
- `make test` (passed; pytest-asyncio deprecation warnings)
- `make test-qa` (passed; pytest-asyncio deprecation warnings)
- `make coverage` (failed: pytest-cov not installed)
- `make validate` (passed; pytest-asyncio deprecation warnings)
- Local smoke run: `gunicorn` on `127.0.0.1:5050` with `curl` checks for `/`, `/generate`, `/calibration` (passed)

## Commit Plan
- `Release 2.1.0: advanced exports, calibration UI refactor, and UI tests`
