<!--
<ai_agent_documentation>
  <file_meta>
    <name>walkthrough.md</name>
    <version>1.6.0</version>
    <type>delivery_report</type>
    <purpose>Summarize completed work, tests, and recommended commits</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>Codex (Senior CV Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Walkthrough

Date: 2026-02-08

## Summary
- Fixed ChArUco metadata using board-derived marker IDs and corrected corner positions.
- Replaced simulated validation with real detection service + upload UI wiring.
- Added calibration import flow and consolidated export bundle generation.
- Added DB schema guardrails with legacy column backfill to prevent schema drift.

## Changes
- `aruco_generator/calibration/calibration.py`: derive ChArUco marker IDs/corners from the board API.
- `aruco_generator/validation/validation.py`: add real marker detection pipeline + confidence scoring.
- `aruco_generator/web/advanced_web.py`: new detection endpoint with standardized error handling.
- `aruco_generator/web/calibration_web.py`: import endpoint + export bundle + import normalization helpers.
- `aruco_generator/db/schema.py`, `app.py`: schema guardrail + legacy backfill hooks.
- `static/js/pages/validation.js`, `templates/validation.html`: live detection upload flow + inputs.
- `static/js/pages/calibration.js`, `templates/calibration.html`: import controls + bundle export wiring.
- `static/js/core/api.js`, `templates/documentation.html`: API client + docs updates.
- `tests/test_api.py`: import + detection coverage.

## Tests
- `make validate`
- `make integration`
- `make test`

Warnings:
- `pytest_asyncio` deprecation warning about unset `asyncio_default_fixture_loop_scope` (from pytest runs).

## Commit Plan
- `Fix calibration metadata, detection service, import/export bundle, and DB schema guardrails`
