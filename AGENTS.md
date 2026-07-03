<!--
<ai_agent_documentation>
  <file_meta>
    <name>AGENTS.md</name>
    <version>1.2.0</version>
    <type>engineering_guide</type>
    <purpose>Operational rules, workflows, and quality gates for contributors</purpose>
    <last_updated>2026-02-09</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
<INSTRUCTIONS>
# AGENTS.md - Engineering Guide

**Current Implementation**: `v2.6.0`
**Last Updated**: 2026-07-03

---

## Prime Directive
You are an expert software engineer working on a premium, high-performance web application.
Your work must be **Dynamic**, **Robust**, and **Aesthetically Pleasing**.

---

## Critical Protocols
1. **Map Discipline**: `AI_NAVIGATION.xml` is the authoritative map. If code structure or key line numbers change, **update the XML** immediately.
2. **Documentation First**: Every modified file must keep its `<ai_agent_documentation>` header accurate (version, last_updated, purpose). If the header is missing, add it.
3. **Blueprint Rule**: All route modules must be Flask Blueprints. Never import `app` in modules imported by `app.py`.
4. **Validation Gate**: Run `make validate` after every significant change. For refactors touching UI + backend, also run `make integration` and `make test`.
5. **Versioning**: On release-level changes, update `pyproject.toml`, `aruco_generator/__init__.py`, `docs/CHANGELOG.md`, and `AI_NAVIGATION.xml`.
6. **Deployment Checklist**: Follow `docs/deployment_checklist.md` before any release or deployment.
7. **Observability First**: Use `/api/health` and `/api/healthz` to verify readiness and capture request IDs in error reports.
8. **Trunk-Based Delivery**: `main` is the production branch. Use short-lived feature branches and merge via PR after CI passes.
9. **Vercel GitHub Integration**: Deployments are handled by Vercel (preview + production). GitHub Actions runs CI and release validation only.
10. **Release Tags**: Production releases are annotated tags (`vX.Y.Z`) on `main`. Tags trigger GitHub Releases and Docker builds.

---

## Navigation Map
Start with `AI_NAVIGATION.xml` for exact file locations and line references.

### Entry Points
- `app.py` - Flask application factory
- `aruco_generator/core/aruco.py` - Core ArUCO generation

### Key UI + API Files
- `templates/generate.html` - Generation UI (simple/advanced/batch)
- `templates/calibration.html` - Calibration UI
- `static/js/pages/generate.js` - Generate page controller
- `static/js/pages/calibration.js` - Calibration page controller
- `static/css/calibration.css` - Calibration-specific styling
- `static/js/core/api.js` - Frontend API client
- `aruco_generator/web/web.py` - Primary API endpoints
- `aruco_generator/web/advanced_web.py` - Advanced preview + exports + validation
- `aruco_generator/web/calibration_web.py` - Calibration endpoints

---

## Development Workflow
1. **READ**: Locate relevant files in `AI_NAVIGATION.xml`.
2. **PLAN**: For complex changes, update `docs/ai/implementation_plan.md`.
3. **EDIT**: Make focused changes with stable API contracts.
4. **VALIDATE**: Run `make validate` and any additional required targets.
5. **DOCUMENT**: Update `docs/ai/walkthrough.md` and `docs/ai/task.md`.

---

## Testing
- Unit: `make unit-test`
- Integration: `make integration`
- UI smoke tests: `make test-ui`
- API integration: `make test-api`
- Health checks: `make test-health`
- Quality gates: `make test-qa`
- Full validation: `make validate`

---

## Deployment & Environments
- **Production**: `aruco.tools` (Vercel production branch = `main`)
- **Staging**: `staging.aruco.tools` (active `release/vX.Y` branch)
- **Preview**: Per-PR preview deployments from Vercel
- **Local env sync**: `vercel env pull` for `.env.local` when needed
- **Repo hygiene**: `.vercel/` is local-only and must not be committed

---

## Release + PR Checklist
- Update version and changelog for new releases.
- Ensure AI navigation line references are correct.
- Create a branch using the `codex/` prefix.
- Commit and tag releases with an annotated tag.
- Prepare a PR summary in `docs/ai/walkthrough.md`.
 - For releases: cut `release/vX.Y`, validate on staging, then tag `main` with `vX.Y.Z`.

---

## Artifacts
- `docs/ai/task.md` - Active work tracker
- `docs/ai/implementation_plan.md` - Approved refactor plan
- `docs/ai/walkthrough.md` - Delivery summary and test logs

Go forth and code brilliantly.
</INSTRUCTIONS>
