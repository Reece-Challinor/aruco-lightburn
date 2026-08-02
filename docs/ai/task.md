<!--
<ai_agent_documentation>
  <file_meta>
    <name>task.md</name>
    <version>2.1.0</version>
    <type>task_tracker</type>
    <purpose>Track immediate engineering tasks for the roadmap program (successor to the production launch program)</purpose>
    <last_updated>2026-07-03</last_updated>
    <maintainer>Claude (Senior Engineer)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Task Status

Status: ACTIVE — Roadmap Program (docs/ai/PRODUCT_ROADMAP.md via
docs/ai/IMPLEMENTATION_BRIDGE.md). The Production Launch Program
(docs/ai/implementation_plan.md) was reconciled into it on 2026-07-03
(decision D-ζ, docs/ai/phase0/DECISION_LOG.md).

## Done (2026-07-03, Phase 5 stable base → v2.6.0)
- Bridge P-0.0: repaired both un-skipped LightBurn tests (test-side lbrn2
  parsing — vertices are "V{x} {y}c0x1c1x1" concatenated; layer index is the
  Value attribute); strengthened them per the bridge ACs (≥2 shape layers;
  40mm marker spans 40±0.1mm).
- Fixed materials.json CWD-relative load in export/lightburn.py (now resolves
  from the package; regression test added).
- Test hygiene: coverage artifacts gitignored; the one remaining skip
  (SVG overlap) documented as an intentional decision.
- Committed Phase 0 planning docs; recorded founder decisions D-α…D-ζ;
  annotated implementation_plan.md with per-phase dispositions.
- Version bump 2.5.1 → 2.6.0 (stable-base release).

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

## Done (2026-07-03, CI repair)
- Stable-base PR #13 merged to main; v2.6.0 tagged.
- Fixed the two chronic CI failures: Codecov upload now non-blocking
  (needs CODECOV_TOKEN secret to actually upload — optional PM action);
  Dependabot switched to the uv ecosystem so uv.lock stays valid, with
  sync-requirements.yml auto-healing the requirements.txt export on main.
- docker.yml no longer fails without Docker Hub secrets (builds without
  pushing; set DOCKER_USERNAME/DOCKER_PASSWORD to enable publishing).

## Done (2026-07-03, P-0.1, P-0.2)
- Bridge P-0.1: Removed DB metrics (F-10) and froze pattern persistence.
- Bridge P-0.2: Implemented tokens.css and theme.js (dark-first theme base).

## Done (2026-08-01, M0 foundation — shared branch feat/m0-foundation)
- P-0.1..P-0.5 verified against bridge ACs (P-0.1 F-10, P-0.2 tokens,
  P-0.3 shell/IA partial, P-0.4 components, P-0.5 calculator + JS CI).
- P-0.6 (F-04) complete: Convert workspace UI finished on top of the
  format-adapters lib; smoke test added; fully client-side.
- Hygiene: node_modules gitignored, package.json normalized, scratch
  test-yaml.js removed.
- KNOWN GAP for P-0.11 gate (deferred, do not lose): P-0.3 301 redirects
  missing (/validation → 404; /calibration not renamed /calibrate; no
  /learn workspace page); keyboard g+key nav not implemented.

## Next up
- [ ] P-0.7 (F-07a print ruler — amend per plan: move reportlab to runtime
      deps first) ∥ P-0.8 (F-11 diamonds) → P-0.9 (F-08 advisor) →
      P-0.10 (F-09) → P-0.11 gate (+ fix the P-0.3 redirect gap there).
- [ ] P-0.S spike rerun (previous attempt hit API limits; partial finding:
      Techstark opencv-js 5.0.0 npm build has the full new-style
      aruco/charuco API — promising GO signal, needs benchmarks).
- [ ] aruco.tools DNS at Namecheap (PM action — see plan).
- [ ] Enable branch protection on main; disable Deployment Protection for
      production (PM actions).
- [ ] Bridge P-0.S: OpenCV.js viability spike (∥ with M0; gates M1).
- [ ] Bridge P-0.3: F-90b AppShell + 6 workspaces.
- [ ] Bridge P-0.4: F-90c core component library.

## Previous cycle (2026-02-23, complete)
Archived — see git history of this file and docs/ai/walkthrough.md.
