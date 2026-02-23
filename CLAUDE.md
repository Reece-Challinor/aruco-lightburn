# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ArUCO Generator (v2.4.0) — Flask web app for generating ArUCO markers, ChArUco calibration boards, and AprilTags with native LightBurn (.lbrn2) laser cutting export. Supports multiple export formats (SVG, PDF, DXF, STL, YAML).

## Commands

```bash
# Development
make install-dev      # Install dev dependencies (pytest, black, flake8, etc.)
make dev              # Start dev server (Gunicorn with auto-reload, port 5000)
make format           # Auto-format with Black + isort

# Testing
make test             # Unit + integration + UI tests
make unit-test        # Core logic tests only
make test-api         # API endpoint tests
make test-ui          # UI smoke tests
make test-qa          # Quality assurance (generation quality + export snapshots)
make coverage         # Full suite with HTML/XML coverage

# Run a single test file or test
python3 -m pytest tests/test_aruco_generator.py -v
python3 -m pytest tests/test_aruco_generator.py::TestClassName::test_method -xvs

# Filter tests by keyword
python3 -m pytest tests/ -k "health" -v

# Validation (REQUIRED before commits)
make validate         # format-check + lint + test + test-qa
make ci               # Full CI: clean + install-dev + validate + coverage

# Linting
make lint             # flake8 (max-line-length=88, ignores E501,W503,E203)
make format-check     # Black + isort check (no changes)
```

## Architecture

### Application Factory

`app.py:213` defines `create_app()` which returns a Flask app. The module-level `app = create_app()` at line 319 is the WSGI entry point used by Gunicorn (`app:app`).

### Blueprint Registration (Critical Gotcha)

Three Flask blueprints are registered in `create_app()` at `app.py:306-312`:
- `web_bp` — core endpoints (preview, download, health)
- `calibration_bp` — calibration pattern endpoints
- `advanced_bp` — 3D coordinates, validation, exports

**NEVER import `app` in modules imported by `app.py`** — this causes circular imports. Blueprints are imported inside `create_app()` specifically to avoid this.

### OpenCV Fallback Strategy

`aruco_generator/core/aruco.py` uses a strategy pattern: OpenCV generates markers when available (~0.1ms), otherwise a pure-Python fallback dictionary is used (~1ms). This means the app works without OpenCV installed.

### Key Modules

- `aruco_generator/core/aruco.py` — `ArUCOGenerator` class, marker generation logic
- `aruco_generator/core/drawing.py` — `DrawingContext` for SVG rendering, rectangle merging optimization (O(n²))
- `aruco_generator/export/lightburn.py` — LightBurn .lbrn2 XML exporter
- `aruco_generator/export/exporters.py` — SVG, PDF, YAML, DXF, STL exporters
- `aruco_generator/calibration/calibration.py` — ChArUco boards, ArUco boards, AprilTags
- `aruco_generator/core/observability.py` — Request tracing, health metrics
- `static/js/core/api.js` — Frontend API client (`ArUCOAPI` class)

### Database

Runs in three modes depending on environment:
- `DATABASE_URL` set → PostgreSQL (production)
- `USE_SQLITE` set → SQLite file
- Neither → In-memory SQLite (stateless, default for dev)

App works without database persistence (graceful degradation).

## Project Conventions

### AI Navigation Map

`AI_NAVIGATION.xml` is the authoritative source of truth for code structure with exact line references. **Update it immediately** when code structure or key line numbers change.

### Documentation Headers

Every file maintains an `<ai_agent_documentation>` XML header with name, version, type, purpose, and last_updated. Increment version on significant changes.

### Error Messages

Use specific validation messages: `"Marker size must be positive (in millimeters)"` not `"Invalid input"`. See `docs/ai/ERROR_HANDLING.md`.

### Versioning (Release Checklist)

When releasing, update all four locations:
1. `pyproject.toml` — `version` field
2. `aruco_generator/__init__.py` — `__version__`
3. `docs/CHANGELOG.md` — release notes
4. `AI_NAVIGATION.xml` — version attribute

### Formatting Rules

- Black with line-length 88
- isort with `--profile black`
- flake8 ignores: E501, W503, E203

## Key References

- `AGENTS.md` — Operational protocols, validation gates, deployment workflow
- `AI_NAVIGATION.xml` — Code structure with line references (source of truth)
- `docs/ai/task.md` — Active task tracking
- `docs/ai/walkthrough.md` — Delivery summaries
- `docs/deployment_checklist.md` — Pre-release steps
