<!--
<ai_agent_documentation>
  <file_meta>
    <name>deployment_checklist.md</name>
    <version>1.0.0</version>
    <type>checklist</type>
    <purpose>Release and deployment checklist for CI/CD and manual validation</purpose>
    <last_updated>2026-02-07</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Deployment Checklist

## Pre-Release
1. Update version in `pyproject.toml`, `aruco_generator/__init__.py`, `CHANGELOG.md`, and `AI_NAVIGATION.xml`.
2. Ensure `AGENTS.md` and `implementation_plan.md` reflect current workflow.
3. Run local validation:
   - `make format`
   - `make lint`
   - `make test`
   - `make test-qa`
   - `make validate`
4. Verify UI smoke tests pass (`make test-ui`).
5. Run the app locally and confirm `/`, `/generate`, `/calibration` load.

## CI Gate
1. CI `make validate` must pass.
2. Coverage runs via `make coverage`.
3. Check Codecov upload (optional).

## Release
1. Create a branch with the `codex/` prefix.
2. Commit changes and tag the release (e.g., `v2.2.0`).
3. Open PR with summary + test results from `walkthrough.md`.
4. Merge PR after review and ensure CI passes.

## Post-Release
1. Verify staging/production deployments (if enabled).
2. Monitor logs and error rates.
3. Update release notes if needed.
