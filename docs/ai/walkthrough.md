<!--
<ai_agent_documentation>
  <file_meta>
    <name>walkthrough.md</name>
    <version>2.1.0</version>
    <type>delivery_report</type>
    <purpose>Summarize the P-0.7 delivery, validation evidence, and next gates</purpose>
    <last_updated>2026-08-01</last_updated>
    <maintainer>Claude (Senior Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Walkthrough

Date: 2026-08-01

## Summary
- Completed bridge P-0.7 (F-07a) in the shared `feat/m0-foundation`
  worktree. Eligible PDF and SVG downloads now include a calibrated 100 mm
  ruler plus the warning that print-to-page scaling breaks dimensional
  accuracy.
- PDF and SVG use the same placement contract: 15 mm of clear margin and 1 mm
  side clearance around the 100 mm bar. Small content and custom PDF pages with
  only 10 mm margin skip the ruler instead of overlapping marker geometry.
- LightBurn and DXF remain manufacturing-only outputs. Regression tests prove
  the SVG ruler element is ignored by lbrn2 and that DXF contains no ruler text
  or geometry.
- Fixed the production PDF route: ReportLab moved from the dev dependency group
  to runtime dependencies, with `uv.lock` and Vercel's hash-pinned
  `requirements.txt` regenerated.
- Replaced the PDF exporter's per-pixel renderer with the shared rectangle
  merger used by vector output. The representative one-marker PDF dropped from
  roughly 128 KB to about 1.8 KB while retaining exact vector geometry.

## Changes
- `aruco_generator/core/drawing.py`: shared merged-rectangle primitive,
  placement predicate, and SVG scale-ruler element/path renderer.
- `aruco_generator/export/exporters.py`: compact PDF marker rendering and the
  calibrated PDF ruler in the content's clear bottom margin.
- `aruco_generator/core/utils.py`, `aruco_generator/web/web.py`: ruler enabled
  by default for print-export routes, with explicit opt-out support.
- `pyproject.toml`, `uv.lock`, `requirements.txt`: ReportLab promoted to the
  production dependency set and manifests synchronized.
- `tests/test_export_formats.py`, `tests/test_export_snapshots.py`,
  `tests/snapshots/scale_ruler*`: exact-dimension, placement-skip, route,
  compactness, cut-isolation, and snapshot coverage.
- `docs/ai/implementation_plan.md`, `docs/ai/IMPLEMENTATION_BRIDGE.md`,
  `docs/ai/task.md`, `docs/CHANGELOG.md`, and `AI_NAVIGATION.xml`: P-0.7 status,
  next sequence, blockers, user-facing changes, and symbol locations updated.
- `.gitignore`: local `.claude/` agent worktrees are ignored so isolated work
  does not leave the shared branch dirty; the worktrees themselves are intact.

## Tests
- `make test-export` — **27 passed, 1 intentional skip**.
- `make check-requirements` — green.
- `make validate` — green: formatting, lint, mypy, 49 unit tests, 34 API
  integration tests, 7 UI smoke tests, 8 Node tests, 9 generation-quality
  tests, and 27 passing export/snapshot tests. The one skip is the documented
  intentional SVG-overlap case. `make validate` exercised both `make test` and
  `make integration` through its dependency graph.

## Next steps and blockers

- Integrate the isolated P-0.8 commit (`d1e4725`), resolve any overlap, validate,
  and push the shared branch. Then continue P-0.9 → P-0.10 → P-0.11.
- P-0.11 must close the known P-0.3 IA gap: redirects, `/learn`, and keyboard
  navigation before the M0 gate can pass.
- M1 remains blocked on the P-0.S OpenCV.js spike rerun. No blocker remains for
  P-0.7 itself.

## Handoff stopping point

Stop after the P-0.7 commit. Do not redo P-0.1 through P-0.7. The next agent
should begin by integrating P-0.8 commit `d1e4725` into `feat/m0-foundation`,
then run the full validation gate before starting P-0.9.

## Previous cycle (2026-02-23, release 2.5.x)
Archived — see git history of this file.
