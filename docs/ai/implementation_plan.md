<!--
<ai_agent_documentation>
  <file_meta>
    <name>implementation_plan.md</name>
    <version>1.3.0</version>
    <type>plan_document</type>
    <purpose>Approved refactor execution plan and validation gates</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>Codex (Senior CV Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Implementation Plan - ArUCO Generator Refactor

Status: Updated on 2026-02-23 for audit remediation phases (1-5)

## 2026-02-23 Audit Remediation (Phases 1-5)
- Phase 1: Critical fixes (dependency cleanup, secret fallback warnings, logging updates).
- Phase 2: Input validation + safety (bounds checks, JSON handling, filename sanitization, security headers).
- Phase 3: Test infrastructure (shared fixtures, unskipped edge tests, baseline coverage gates).
- Phase 4: Cleanup (remove compatibility shims, dedupe drawing logic, tighten exception handling).
- Phase 5: CI/CD hardening (coverage enforcement, Makefile fixes, pre-commit alignment, Docker env hygiene).

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
- Remove legacy module shims once imports are updated (2026-02-23).
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

### Phase 8: Calibration + Validation Production Hardening
- Unify API response envelope for calibration + validation endpoints (`success`, `data`, `errors`, `warnings`, `request_id`, `timestamp`, `version`).
- Standardize error handling for all advanced/validation endpoints (use shared decorator, preserve HTTPException codes).
- Add explicit OpenCV availability checks and return 503 with actionable guidance.
- Enforce request validation with per-field error feedback and consistent unit handling.
- Introduce file upload limits, MIME/type validation, and image dimension safeguards.
- Normalize detection/quality metrics schema (rate vs percent, time units, consistent keys across report + batch).
- Implement or remove unused request flags (`include_distortions`, `include_occlusions`) to keep API honest.
- Improve DB resilience: add indexes, constraints, and persistence status messaging for stateless mode.
- Add request/response tracing metadata in JSON responses to mirror header request IDs.
- Build API warnings for partial persistence (DB disabled) and export limitations.

### Phase 9: Validation + Calibration UX Upgrade
- Move validation inline CSS into a dedicated stylesheet with shared tokens.
- Add per-field error display and inline validation hints on calibration form.
- Surface API warnings and request IDs in UI for supportability.
- Render real metrics from API instead of static placeholders.
- Add export states and guidance when DB persistence is disabled.

### Phase 10: Test + QA Expansion
- Add API tests for error schema, 404 handling, and file upload limits.
- Add unit tests for detection report aggregation and metric normalization.
- Add UI smoke tests for new validation controls and error surfacing.
- Add integration tests for upload error paths (invalid images, oversized files).

### Phase 11: Documentation + Release Hygiene
- Update `docs/ai/ERROR_HANDLING.md` with the new API error schema and examples.
- Refresh `docs/ai/NAVIGATION.md` and AI_NAVIGATION references if endpoints shift.
- Update `docs/ai/walkthrough.md` with summaries and test logs after implementation.

## Documentation Deliverables
- Update AI_NAVIGATION line references impacted by refactor.
- Refresh file-level `<ai_agent_documentation>` headers for modified files.
- Create `docs/ai/walkthrough.md` with change summary, tests, and commit log.

## Validation Gates
- `make validate` after structural changes.
- Targeted pytest for export endpoints and advanced routes.

## Rollback Strategy
- Each phase is isolated by commit; revert the specific phase commit if needed.
