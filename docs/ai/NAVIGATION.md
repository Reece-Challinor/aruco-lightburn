<!--
<ai_agent_documentation>
  <file_meta>
    <name>NAVIGATION.md</name>
    <version>1.0.0</version>
    <type>navigation_map</type>
    <purpose>High-level directory map and entrypoints</purpose>
    <last_updated>2026-02-07</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Navigation

## Entry Points
- `app.py` (Flask app factory + blueprint registration)

## Core Packages
- `aruco_generator/core/` (ArUCO generation, drawing, shared utils)
- `aruco_generator/export/` (LightBurn + professional exports + batch)
- `aruco_generator/web/` (Flask blueprints and endpoints)
- `aruco_generator/calibration/` (ChArUco / ArUCO board / AprilTag generators)
- `aruco_generator/validation/` (Detection validation + QA utilities)
- `aruco_generator/db/` (SQLAlchemy extensions + models)

## Frontend
- `static/js/core/api.js` (API client)
- `static/js/pages/` (page controllers)
- `static/css/main.css` (styles)
- `templates/` (Jinja templates)

## Tests
- `tests/` (unit + integration + export/quality tests)

## Docs
- `docs/ai/` (agent guidance, plans, and task tracking)
- `docs/CHANGELOG.md` (release history)
- `docs/deployment_checklist.md` (release checklist)
- `docs/GENERATION_QUALITY.md` (quality standards)

## Compatibility Shims
- Legacy module paths in `aruco_generator/*.py` re-export the new package locations.
