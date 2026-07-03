<!--
<ai_agent_documentation>
  <file_meta>
    <name>walkthrough.md</name>
    <version>2.0.0</version>
    <type>delivery_report</type>
    <purpose>Summarize completed work, tests, and recommended commits</purpose>
    <last_updated>2026-07-03</last_updated>
    <maintainer>Claude (Senior Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Walkthrough

Date: 2026-07-03

## Summary
- Delivered the **stable base for the v3 roadmap** (release 2.6.0): bridge
  prompt P-0.0 executed, program reconciliation recorded, planning docs
  committed.
- Repaired both previously-skipped LightBurn tests. Root cause was
  test-side parsing: lbrn2 vertices are encoded as `V{x:.3f} {y:.3f}c0x1c1x1`
  concatenated with no separator (not `x,y;x,y;...`), and CutSetting layer
  indices live in the `Value` attribute of `<index>` (not element text). The
  exporter itself was correct — coordinates are in mm; no snapshot changes.
- Strengthened both tests per the bridge acceptance criteria: layers test now
  also asserts shapes span ≥2 distinct `CutIndex` layers; coordinates test
  asserts a 40 mm marker's geometry spans 40±0.1 mm (measured 40.05 mm —
  intentional engraving bleed).
- Fixed a real production bug found during P-0.0: `LightBurnExporter` loaded
  `materials.json` by CWD-relative path at import time, silently falling back
  to defaults on serverless (Vercel CWD ≠ repo root). Now resolved from the
  package location; regression test added.
- Test hygiene: coverage artifacts (`.coverage`, `htmlcov/`, `coverage.xml`)
  gitignored; the one remaining skip (SVG overlap) re-worded as an
  intentional, documented decision.
- Program reconciliation (decision D-ζ): `implementation_plan.md` annotated
  with per-phase dispositions (Phase 5 delivered at minimal stable-base
  scope; 6–7 fold into roadmap M0/M1; 8 superseded); founder decision packet
  D-α…D-ζ recorded as DECIDED in `docs/ai/phase0/DECISION_LOG.md`; Phase 0
  docs committed; stale v2.4.0 references in CLAUDE.md/AGENTS.md corrected.

## Changes
- `tests/test_export_formats.py`: fixed lbrn2 parsing in both repaired tests;
  strengthened assertions per bridge ACs; new
  `test_materials_loaded_independent_of_cwd` regression test; skip reason
  documented as intentional; header 1.1.0 → 1.2.0.
- `aruco_generator/export/lightburn.py`: `materials.json` resolved from the
  package root instead of process CWD; header 1.1.0 → 1.2.0.
- `.gitignore`: coverage artifacts section added.
- `docs/ai/implementation_plan.md`: status → RECONCILED; per-phase
  disposition notes (D-ζ); header 2.0.0 → 2.1.0.
- `docs/ai/phase0/DECISION_LOG.md`: D-α…D-ζ recorded as decided; C-4
  resolved; readiness checklist closed (U-1/U-2 and U-4 remain open, owned
  by bridge P-0.S and P-0.6); header 0.9.0 → 1.0.0.
- `docs/ai/task.md`: stable-base done-list; next-up points at bridge P-0.S /
  P-0.1; header 2.0.0 → 2.1.0.
- `CLAUDE.md`, `AGENTS.md`: stale v2.4.0 → v2.6.0.
- `docs/ai/phase0/{BASELINE_REPORT,KNOWLEDGE_BASE}.md`: committed (previously
  untracked Phase 0 deliverables).
- Version bump 2.5.1 → 2.6.0 via `scripts/release.py` (pyproject,
  `__init__.py`, CHANGELOG, AI_NAVIGATION).

## Tests
- `make validate` (format-check + lint + typecheck + test + test-qa) — green.
- `tests/test_export_formats.py`: 11 passed, 1 intentional skip (was 2
  failing after un-skip).
- `tests/test_export_snapshots.py`: unchanged and green (exporter output
  byte-identical; the path fix does not alter XML).

## Commit Plan
- `Phase 5 stable base (P-0.0): repair LightBurn tests, fix materials.json path, reconcile programs, release 2.6.0`

## Previous cycle (2026-02-23, release 2.5.x)
Archived — see git history of this file.
