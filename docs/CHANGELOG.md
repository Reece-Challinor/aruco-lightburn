<!--
<ai_agent_documentation>
  <file_meta>
    <name>CHANGELOG.md</name>
    <version>1.2.0</version>
    <type>changelog</type>
    <purpose>Track user-facing changes and releases</purpose>
    <last_updated>2026-02-23</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]
### Added
- TBD

### Changed
- TBD

### Removed
- TBD

## [2.5.0] - 2026-02-23
### Added
- Security headers and session secret fallback warning.
- Input bounds for marker size and grid limits to prevent excessive allocations.
- Shared pytest fixtures plus new edge case and concurrency tests.
- Coverage and pytest configuration with a baseline threshold.
- Import validation pre-commit hook and Docker Compose env template.

### Changed
- Standardized JSON request handling across core endpoints.
- Sanitized generated download filenames.
- LightBurn exporter now logs material load warnings via logger.
- Docker Compose now uses env-based credentials.

### Removed
- Legacy compatibility shim modules for core/export/web imports.
- No-op validate-imports pre-commit hook.

## [2.4.0] - 2026-02-08
### Added
- Unified API response envelope for calibration and validation endpoints with request IDs.
- Upload and import safeguards (size, MIME, and image dimension limits).
- Validation-specific stylesheet and request metadata display in UI.
- DB resilience warnings for calibration/validation persistence.

### Changed
- Calibration and validation endpoints now return consistent error payloads with field-level details.
- Test-pattern generator supports deterministic distortions and occlusions.
- Detection report metrics now use consistent `*_ms` timing keys.

### Removed
- Inline validation CSS in `templates/validation.html` (moved to stylesheet).

## [2.3.0] - 2026-02-08
### Added
- Real marker detection service with upload workflow (`/api/validation/detect`).
- Calibration data import for JSON/YAML with preview + persistence.
- Calibration export bundle (image + YAML/JSON/ROS/OpenCV).
- DB schema guardrail helpers with legacy column backfill.

### Changed
- ChArUco metadata now uses board-derived marker IDs and corner positions.
- Validation UI now uses server-side detection results.
- Validation endpoints standardized on shared error handling.

## [2.2.0] - 2026-02-07
### Added
- Simple export menu options for DXF and STL.
- Deployment checklist in `docs/deployment_checklist.md`.
- UI smoke tests expanded for simple + advanced export menus.
- PDF export test for outer-border rendering (skips if reportlab missing).

### Changed
- Makefile test targets reorganized and validation now includes format checks.
- CI pipeline now runs `make validate` and `make coverage`.
- Pre-commit hooks updated to include UI smoke checks on template/JS changes.
- PDF export uses shared exporter module and supports outer-border rendering.
- Unit-test target now covers core calibration, utility, and navigation suites.
- Coverage output now includes XML for CI uploads.
- Pre-commit hooks include API smoke tests for backend changes.
- Fixed PDF export unit conversion (reportlab `mm`) to avoid 501 responses.

## [2.1.0] - 2026-02-07
### Added
- Snapshot tests for SVG preview and LightBurn exports.
- Advanced export endpoint tests for YAML/ROS/DXF/STL.
- Documentation files referenced by AI_NAVIGATION.xml.
- UI smoke tests for key generation and calibration affordances.
- Advanced export dropdown with DXF/STL options and isolated state.
- AprilTag single persistence for export parity.
- Calibration page controller and dedicated styling.

### Changed
- Modularized backend into `core`, `export`, `web`, `calibration`, `validation`, and `db` packages.
- LightBurn download now uses marker pixel data to preserve bit patterns.
- App factory (`create_app`) is the canonical initialization entrypoint.
- Advanced preview uses shared validation and rendering helpers.
- PDF export supports optional outer border rendering.

### Removed
- Tracked runtime artifacts (pid files, sqlite db) from the repo.

## [2.0.0] - 2025-01-13
### Added
- Unified ArUCO generator release.
