<!--
<ai_agent_documentation>
  <file_meta>
    <name>CHANGELOG.md</name>
    <version>1.3.0</version>
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
### Security
- Escaped all API-derived values interpolated into `innerHTML` (XSS) and added a
  shared `window.escapeHtml` helper.
- Strict Content-Security-Policy, HSTS, Referrer-Policy, and Permissions-Policy
  headers on every response (deprecated `X-XSS-Protection` removed).
- Vendored Bootstrap 5.3.3 + Bootstrap Icons locally (`static/vendor/`) —
  removes cdn.replit.com and cdn.jsdelivr.net dependencies entirely.
- App now refuses to start in production without `SESSION_SECRET`.
- Rate limiting (Flask-Limiter) on generation, export, upload, and log
  endpoints with JSON 429 envelope.
- Removed unauthenticated `/api/debug/status`; `/api/health` no longer reports
  host platform or Python version.
- Bandit pre-commit hook now also scans `app.py` and `api/`.

### Added
- CodeQL (Python + JS) and Dependabot workflows; `make audit` (bandit + pip-audit).
- `make release VERSION=x.y.z` — bumps every version location atomically
  (`scripts/release.py`), ending multi-file version drift.
- CI gate ensuring `requirements.txt` stays in sync with `uv.lock`
  (`make check-requirements`).
- Vercel serverless entry point (`api/index.py`) with modern `vercel.json` rewrites.
- Pinned `requirements.txt` exported from `uv.lock` for the Vercel build.
- `.vercelignore` to slim deployment uploads.
- Production launch program plan (`docs/ai/implementation_plan.md`).

### Changed
- All tooling now runs through uv (`uv.lock` is the single source of dependency
  truth): Makefile, CI, pre-commit hooks, and Docker (installs from the pinned
  hash-verified `requirements.txt` export).
- CI tests Python 3.11 and 3.12; dev tools (mypy, pip-audit, bandit, isort,
  pre-commit, reportlab) are declared in `[dependency-groups]`.
- Upgraded Flask 3.1.1→3.1.3 and Werkzeug 3.1.3→3.1.8 (4 known CVEs fixed,
  found by the new pip-audit gate).
- Docker HEALTHCHECK now uses stdlib `urllib` against `/api/healthz` (previous
  check imported `requests`, which is not a dependency, so containers always
  reported unhealthy).
- Replaced legacy Vercel config (15 MB `maxLambdaSize` made deploys impossible).

### Removed
- Replit support (`.replit`) — deployment is Vercel-first with Docker for self-hosting.

## [2.5.1] - 2026-02-23
### Changed
- Pre-commit now uses system Python to avoid local 3.11 dependency.
- Pytest-asyncio loop scope configured to silence deprecation warnings.
- Import validation hook now adds repo root to Python path.

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
