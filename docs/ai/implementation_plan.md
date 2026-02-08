<!--
<ai_agent_documentation>
  <file_meta>
    <name>implementation_plan.md</name>
    <version>1.1.0</version>
    <type>plan_document</type>
    <purpose>Approved refactor execution plan and validation gates</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>Codex (Senior CV Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Implementation Plan - ArUCO Generator Refactor

Status: Updated on 2026-02-07 for calibration + advanced UX refactor

## Scope
Implement phases 0-4 from the audit plan while preserving working behavior, with compatibility shims where needed.
Extend scope to refactor calibration and advanced generation workflows for export-ready persistence and UX consistency.

## Phases

### Phase 0: Safety Rails
- Add export snapshots/golden-file tests (SVG + LightBurn + advanced exports).
- Add smoke tests for advanced endpoints.
- Establish validation gates via `make validate`.

### Phase 1: Cleanup
- Remove tracked logs, pid files, caches, and generated artifacts.
- Extend `.gitignore` for pid files.

### Phase 2: Structure
- Introduce subpackages: core, export, web, calibration, validation, db.
- Move canonical implementations to new locations.
- Keep legacy module shims for compatibility.
- Align entrypoints (Makefile/Docker/Vercel).

### Phase 3: Export + Advanced + Calibration Fixes
- Route LightBurn export through `DrawingContext.add_marker_grid` to preserve marker bit patterns.
- Fix/alias advanced preview endpoint and remove broken calls (`to_svg`).
- Add DB-safe guards for advanced metrics when running in stateless mode.

### Phase 4: Packaging + Release Hygiene
- Single source of truth for version (pyproject.toml).
- Sync README, __init__, and AI_NAVIGATION metadata.
- Add missing docs referenced in AI_NAVIGATION (`docs/ai/NAVIGATION.md`, `docs/ai/ERROR_HANDLING.md`, etc.).

### Phase 5: Calibration + Advanced UX Refactor
- Persist AprilTag single patterns in the database for export parity.
- Normalize calibration API response shape across pattern types.
- Replace inline handlers on calibration page with managed UI controller.
- Add advanced export controls with isolated state from simple generation.
- Deduplicate advanced preview logic and validation across endpoints.
- Support DXF/STL exports from generation parameters for advanced flows.
- Add PDF outer-border rendering option for advanced exports.
- Move calibration-specific styles to a dedicated stylesheet.

### Phase 6: Continuous Testing + CI Hygiene
- Expand UI smoke coverage and wire into CI and pre-commit hooks.
- Update Makefile targets to align local + CI workflows.
- Add deployment checklist and release hygiene updates.
- Expand unit-test coverage for calibration, utility, and navigation suites.
- Add API smoke pre-commit hook and XML coverage output for CI uploads.

### Phase 7: Validation + Import/Export Consolidation
- Replace simulated detection with real marker detection service.
- Add calibration data import workflow with preview + persistence support.
- Provide consolidated calibration export bundles (image + YAML/JSON/ROS).
- Add lightweight DB schema guardrails for legacy columns.

## Documentation Deliverables
- Update AI_NAVIGATION line references impacted by refactor.
- Refresh file-level `<ai_agent_documentation>` headers for modified files.
- Create `docs/ai/walkthrough.md` with change summary, tests, and commit log.

## Validation Gates
- `make validate` after structural changes.
- Targeted pytest for export endpoints and advanced routes.

## Rollback Strategy
- Each phase is isolated by commit; revert the specific phase commit if needed.
