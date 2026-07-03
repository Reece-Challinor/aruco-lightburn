<!--
<ai_agent_documentation>
  <file_meta>
    <name>BASELINE_REPORT.md</name>
    <version>1.0.0</version>
    <type>phase0_baseline</type>
    <purpose>Recorded green baseline for Phase 1+: SHAs, validation results, timings, pre-existing issue dispositions. Phase 0 deliverable D-4.</purpose>
    <last_updated>2026-06-12</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Baseline Report (D-4) — 2026-06-12

## SHAs

- Branch `feat/phase-5-testing` HEAD: `ca6dc1f` (planning docs commit)
- `main` == `origin/main`: `eb8ba3f` ("Merge Phase 4: code quality")
- Branch delta vs main: documentation only (roadmap, bridge, phase0 docs).

## Validation result

`make validate` (format-check + flake8 + mypy[core,export] + test + test-qa),
run with the uncommitted WIP edit to `tests/test_export_formats.py` stashed:

- **Exit 0 — GREEN.**
- **Wall time: 9 seconds.** (Roadmap O5 budget: < 5 min. Per-PR full
  validation is effectively free; no fast/slow test split needed.)
- Test summaries observed: 49 passed (unit) · 33 passed (api) · 3 passed ·
  9 passed (ui) · 8 passed + 3 skipped (qa/export). The 3 skips are
  pre-existing `@pytest.mark.skip` markers unrelated to the WIP edit.

Coverage: `make coverage` enforces `--cov-fail-under=65` (last recorded
65.55% per docs/ai/walkthrough.md). Not re-run in Phase 0 T0.2 (CI runs it
per PR); re-measure when Phase 1 adds Python code.

## Pre-existing issues & dispositions

| Issue | Disposition |
|---|---|
| Uncommitted edit to `tests/test_export_formats.py` un-skips `test_lightburn_layers` + `test_lightburn_coordinates`; both FAIL (test-side lbrn2 coordinate parsing, line ~253) | **Owned by bridge P-0.0** (first Phase 1 prompt). Left in working tree; excluded from baseline. Matches the live program's "Phase 5: testing" task |
| Untracked `.coverage` artifact | Not committed. Recommend adding `.coverage` to `.gitignore` in P-0.0 (one line, same testing-hygiene PR) |
| 3 skipped tests in qa/export subset | Pre-existing, pre-dating this program; inventory during P-0.0 and disposition there |

## Endpoint response capture

Deferred to T0.4 completion (requires running dev server). The error-envelope
contract is already documented from ERROR_HANDLING.md (KNOWLEDGE_BASE
§Protocols); live captures will confirm `data` payload shapes per endpoint.
