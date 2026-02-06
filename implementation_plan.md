<!--
<ai_agent_documentation>
  <file_meta>
    <name>implementation_plan.md</name>
    <version>1.0.0</version>
    <type>plan_document</type>
    <purpose>Approved refactor execution plan and validation gates</purpose>
    <last_updated>2026-02-06</last_updated>
    <maintainer>Codex (Senior CV Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Implementation Plan - ArUCO Generator Refactor

Status: Approved by maintainer on 2026-02-06

## Scope
Implement phases 0-4 from the audit plan while preserving working behavior, with compatibility shims where needed.

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
- Add missing docs referenced in AI_NAVIGATION (NAVIGATION.md, ERROR_HANDLING.md, etc.).

## Validation Gates
- `make validate` after structural changes.
- Targeted pytest for export endpoints and advanced routes.

## Rollback Strategy
- Each phase is isolated by commit; revert the specific phase commit if needed.
