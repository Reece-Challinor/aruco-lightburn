<!--
<ai_agent_documentation>
  <file_meta>
    <name>task.md</name>
    <version>2.0.0</version>
    <type>task_tracker</type>
    <purpose>Track immediate engineering tasks for the production launch program</purpose>
    <last_updated>2026-06-12</last_updated>
    <maintainer>Claude (Senior Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Task Status

Status: ACTIVE — Production Launch Program (see docs/ai/implementation_plan.md)

## Done (2026-06-12)
- Full production-readiness audit + scorecard (baseline recorded in plan).
- Fixed Docker HEALTHCHECK (stdlib urllib → /api/healthz; `requests` was not a dependency).
- Deprecated Replit entirely (deleted .replit; no references remain).
- Created + linked Vercel project `reece-challinors-projects/aruco-lightburn`.
- Vercel redesign: api/index.py entry, modern vercel.json (legacy 15MB cap removed),
  .vercelignore, pinned requirements.txt exported from uv.lock.
- Validated live deploy: /api/health (opencv 4.11.0 available) and /api/preview
  (full generation pipeline) working on Vercel.

## Done (2026-06-12, Phase 2 — security)
- XSS purge: escaped all API-derived innerHTML interpolations; added window.escapeHtml.
- Vendored Bootstrap 5.3.3 + icons locally; removed cdn.replit.com and jsdelivr.
- CSP, HSTS, Referrer-Policy, Permissions-Policy headers; dropped deprecated X-XSS-Protection.
- SESSION_SECRET fail-fast in production (VERCEL_ENV/FLASK_ENV).
- Flask-Limiter rate limits on preview/download/batch/export/detect/log-error; JSON 429 envelope.
- Removed /api/debug/status; health no longer fingerprints host.
- New tests/test_security.py (headers, CSP, secrets, disclosure, 429s); bandit scope widened.

## Done (2026-06-12, Phase 3 — CI/CD + uv everywhere)
- uv is the single dependency tool: Makefile, pre-commit hooks, CI, release.yml.
- Dev deps moved to [dependency-groups]; mypy/pip-audit/bandit/isort declared.
- New: make audit, typecheck, requirements, check-requirements, release,
  deploy-preview/deploy-prod targets.
- CI matrix (3.11 + 3.12) with uv cache + lockfile sync gate; CodeQL + Dependabot.
- scripts/release.py bumps all version locations atomically.
- Dockerfile installs from hash-verified requirements.txt (reproducible).
- pip-audit found + fixed 4 CVEs (Flask 3.1.3, Werkzeug 3.1.8).

## Done (2026-06-12, Phase 4 — code quality)
- Removed all five legacy shim modules; app.py + web.py import subpackages directly.
- mypy green on core/ + export/, wired into make validate.
- MAX_MARKER_PIXELS 5000→2000 (bounds rectangle-merge worst case).

## Next up
- [ ] aruco.tools DNS at Namecheap (PM action — see plan).
- [ ] Disable Deployment Protection for production (PM action).
- [ ] Phase 5: testing (coverage floor, calibration_web tests).

## Previous cycle (2026-02-23, complete)
Archived — see git history of this file and docs/ai/walkthrough.md.
