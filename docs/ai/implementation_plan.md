<!--
<ai_agent_documentation>
  <file_meta>
    <name>implementation_plan.md</name>
    <version>2.2.0</version>
    <type>plan_document</type>
    <purpose>Reconciled production-launch plan with current roadmap execution status</purpose>
    <last_updated>2026-08-01</last_updated>
    <maintainer>Claude (Senior Engineer) + Reece (PM)</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Production Launch Program — ArUCO.tools

Status: **RECONCILED into the roadmap program (2026-07-03, decision D-ζ)**.
Phases 1–4 delivered; Phase 5 delivered at minimal "stable base" scope
(v2.6.0). **Successor program:** `docs/ai/PRODUCT_ROADMAP.md` (v3.0.0 unified
spec) executed via `docs/ai/IMPLEMENTATION_BRIDGE.md` (phases Pre, M0–M3).
Residual scope from Phases 5–8 folds into the roadmap as annotated per phase
below (decision record: `docs/ai/phase0/DECISION_LOG.md`).

Started 2026-06-12. Supersedes the 2026-02 audit-remediation plan
(see git history for the completed phases 1-11 of the previous refactor).

## Roadmap execution update — 2026-08-01

- The shared `feat/m0-foundation` branch is implemented through bridge P-0.7.
  P-0.7 restores PDF export in production by moving ReportLab into runtime
  dependencies, replaces the per-pixel PDF renderer with shared merged-vector
  geometry, and adds the calibrated 100 mm print ruler to eligible PDF/SVG
  exports. Focused format, route, placement, cut-isolation, and snapshot tests
  are green.
- P-0.8 has an isolated implementation commit (`d1e4725`) but is not integrated
  into the shared branch in this cycle. Integrate and validate it next, then run
  P-0.9 → P-0.10 → P-0.11.
- M0 exit remains gated by the deferred P-0.3 IA corrections: redirects for
  `/validation` and `/calibration`, the `/learn` workspace, and keyboard
  navigation. P-0.11 owns that closure.
- The OpenCV.js P-0.S spike still needs its benchmark rerun. It blocks M1, not
  P-0.7 or the remaining M0 implementation prompts.

## Mission

Launch this repo as a free, public demo product at **https://aruco.tools** —
a portfolio-grade example of computer-vision product tooling (ArUCO markers,
ChArUco calibration boards, AprilTags, laser-cutter export). No accounts, no
payments. Team: Reece (PM) + Claude (engineering).

Goal: every category in the production-readiness scorecard at **A− or better**.

| Category | Was | Target | Phase |
|---|---|---|---|
| Deployment | D | A | 1 (largely done) |
| Security | C | A− | 2 |
| CI/CD | B | A | 3 |
| Dependencies | C+ | A | 3 |
| Code quality | B+ | A | 4 |
| Testing | B+ | A− | 5 |
| Observability | C+ | A− | 6 |
| Documentation / AI tooling | B / B− | A− | 7 |
| Product polish | — | launch-ready | 8 |

## Architecture decision (locked)

- **Primary target: Vercel** — project `reece-challinors-projects/aruco-lightburn`,
  GitHub repo connected. Python functions (500 MB bundle limit) hold full
  OpenCV; validated live on 2026-06-12 (`/api/health` → opencv 4.11.0,
  `/api/preview` → working SVG).
- **Entry**: `api/index.py` re-exports the Flask `app`; `vercel.json` rewrites
  all routes to it. Pinned `requirements.txt` exported from `uv.lock`.
- **Default runtime mode**: stateless (in-memory SQLite, `USE_DB=False`) —
  perfect fit for serverless. Postgres (Neon/Vercel Postgres) only if a
  persistence feature ever justifies it.
- **Docker stays** as the self-host distribution path only (healthcheck fixed
  2026-06-12). docker-compose remains for local Postgres testing.
- **Replit: removed** (2026-06-12). Never reference it again.

## Phase 1 — Deployment foundation (mostly DONE 2026-06-12)

Done:
- [x] Fixed Docker HEALTHCHECK (stdlib urllib → `/api/healthz`).
- [x] Deleted `.replit`; zero Replit references remain.
- [x] Created + linked Vercel project; GitHub repo connected.
- [x] Modern `vercel.json` (rewrites, static cache headers, iad1); removed
      legacy 15 MB `maxLambdaSize` config that made deploys impossible.
- [x] `api/index.py` serverless entry; `.vercelignore`.
- [x] `requirements.txt` pinned+hashed via `uv export` (kept in sync with
      `uv.lock` — see Phase 3 automation).
- [x] First deploy validated end-to-end (health + generation pipeline).

Remaining:
- [ ] **Domain: aruco.tools** (owned at Namecheap). Recommended setup:
      delegate nameservers to Vercel (`ns1.vercel-dns.com`, `ns2.vercel-dns.com`)
      in the Namecheap dashboard — simplest apex handling, lets Vercel manage
      all records. Alternative (keep Namecheap DNS): add the A/CNAME records
      shown by `vercel domains inspect aruco.tools` after
      `vercel domains add aruco.tools`. Then:
      - `aruco.tools` → production deployments
      - `www.aruco.tools` → redirect to apex (Vercel automatic)
      - `staging.aruco.tools` → branch domain mapped to `staging` branch
      SSL: automatic Let's Encrypt issuance + renewal by Vercel; HSTS header
      added in Phase 2. DNS propagation: allow up to 48h after NS change.
- [ ] Disable Vercel Deployment Protection for production (free public tool);
      keep it on preview deployments (Project → Settings → Deployment Protection).
- [ ] Set `SESSION_SECRET` in Vercel env (production + preview):
      `openssl rand -hex 32 | vercel env add SESSION_SECRET production`.

## Environments & promotion model

Trunk-based, two-person team:

| Env | Trigger | URL | Purpose |
|---|---|---|---|
| Preview | every PR / branch push | `aruco-lightburn-<hash>...vercel.app` | dev review, protected |
| Staging | push to `staging` branch | `staging.aruco.tools` | PM demo / pre-release validation |
| Production | push to `main` | `aruco.tools` | public |

- Vercel Git integration performs the deploys (no deploy keys in CI).
- GitHub branch protection on `main` (Reece enables in repo settings):
  require the CI workflow check + up-to-date branch before merge. This is
  the gate that keeps unvetted code off production.
- Rollback: `vercel rollback` (or promote a previous deployment in the
  dashboard) — instant, immutable deployments.
- Staging promotion: `git push origin main:staging` to rehearse, or open a
  PR `main → staging` for visible diffs. For most changes, PR previews are
  enough; staging is for release-candidate sign-off.

## Phase 2 — Security to A− (~1 day)

1. **XSS purge**: replace the 11 `innerHTML` sinks in
   `static/js/pages/{generate,calibration,validation}.js` and
   `static/js/core/notifications.js` with `textContent`/`createElement`
   builders; add `escapeHtml()` helper in `core/api.js` for the few places
   markup is genuinely needed (SVG preview injection stays — it is
   server-generated, but sanitize the error-message paths).
2. **Headers** (in `app.py` `add_security_headers`): add
   `Content-Security-Policy` (self + cdn.jsdelivr.net with SRI, or vendor
   Bootstrap locally — preferred for a stricter CSP),
   `Strict-Transport-Security` (aruco.tools is HTTPS-only),
   `Referrer-Policy: strict-origin-when-cross-origin`,
   `Permissions-Policy` minimal.
3. **Secret hardening**: in `create_app()`, raise `RuntimeError` if
   `SESSION_SECRET` is unset when running on Vercel (`VERCEL_ENV` set) or
   `FLASK_ENV=production`. Keep the warning fallback for local dev only.
4. **Surface reduction**: delete `/api/debug/status`; drop
   `platform.platform()` + Python version from unauthenticated `/api/health`.
5. **Rate limiting**: Flask-Limiter (memory storage — per-instance is
   acceptable for a free demo) on `/api/preview`, `/api/download`,
   `/api/batch_generate`, `/api/validation/detect`, `/api/log-error`.
   Document Vercel WAF as the escalation path.
6. **Supply chain**: SRI hashes on any remaining CDN tags; widen bandit to
   `app.py` + medium severity; add `pip-audit` to CI and pre-commit.

## Phase 3 — CI/CD + dependencies to A (~1 day)

1. **uv everywhere**: Makefile `install`/`install-dev` use
   `uv sync` / `uv sync --group dev`; CI uses `astral-sh/setup-uv` with cache;
   Dockerfile builder stage uses `uv sync --locked --no-dev`. Commit `uv.lock`
   as the single source of dependency truth.
2. **pyproject**: move dev tools (isort, pre-commit, bandit, mypy, pip-audit)
   into `[dependency-groups] dev`; pin `flask-login>=0.6.3` (or remove it + the
   vestigial `User` model — decision: remove, no auth in a free demo).
   ReportLab was initially grouped as dev tooling, then correctly promoted to
   runtime by bridge P-0.7 because production serves `/api/export/pdf`.
3. **ci.yml**: Python 3.11 + 3.12 matrix, uv-cached installs, `make validate`,
   coverage gate, `concurrency: cancel-in-progress`, junit artifact upload.
4. **requirements.txt sync gate**: CI step fails if
   `uv export --no-dev --no-emit-project` differs from the committed
   `requirements.txt` (keeps the Vercel manifest honest).
5. **New workflows**: `codeql.yml` (python + javascript), `dependabot.yml`
   (pip + github-actions, weekly).
6. **Release automation**: `scripts/release.py` + `make release VERSION=x.y.z`
   bumps pyproject, CHANGELOG scaffold, AI_NAVIGATION version, tags — kills
   the multi-file version-drift problem permanently. `release.yml` keeps
   validating tag == pyproject version.
7. **Makefile/pre-commit refresh**: targets for `audit` (pip-audit + bandit),
   `typecheck` (mypy), `deploy-preview` (`vercel deploy`), `deploy-prod`
   (`vercel deploy --prod`, normally unused — Git integration deploys);
   pre-commit gains mypy (changed files), pip-audit (weekly via CI not
   pre-commit), and drops nothing existing.

## Phase 4 — Code quality to A (~0.5 day)

1. Finish the shim migration: `app.py` imports from `aruco_generator.db.*`
   and `aruco_generator.web.calibration_web` directly; delete all five shim
   modules (`exporters.py`, `models.py`, `extensions.py`, `calibration_web.py`,
   `validation_web.py`).
2. `mypy` (gradual): strict on `core/` + `export/`, permissive elsewhere;
   wire into `make validate`.
3. Replace `debug=True` in `app.py` `__main__` with
   `debug=os.environ.get("FLASK_DEBUG") == "1"`.
4. Cap preview render resolution in `DrawingContext` to bound the
   rectangle-merge hotspot (`drawing.py:234`).

## Phase 5 — Testing to A− (~1 day)

> **Disposition (2026-07-03, D-ζ):** delivered at minimal "stable base" scope
> in the v2.6.0 release — item 4 done (both tests repaired and passing, plus
> the materials.json CWD fix; the one remaining SVG-overlap skip is documented
> as an intentional decision). Items 1–3 and 5 fold into roadmap execution:
> coverage rises ride along bridge prompts touching each module, with the
> floor ratcheted at each milestone release (65 → 70 at v2.7.0 → 75 at
> v2.8/2.9 → 80 at v3.0.0); envelope contract tests land with the
> `/api/batch_generate` error-handling fix (M0 parallel window).

1. Raise coverage floor 65 → 75 (then 80 after #2): pyproject + Makefile.
2. Target the gap: `web/calibration_web.py` (1,068 lines, thinnest coverage).
3. Security regression tests: header presence, escaping helpers, upload
   abuse (wrong MIME, oversized, decompression bomb dims), rate-limit 429s.
4. Resolve the two skipped "LightBurn coordinate/layer refinement" tests:
   fix or convert to `xfail` with linked GitHub issues — no silent skips.
5. Response-envelope contract tests (jsonschema) for `/api/*`.

## Phase 6 — Observability to A− (~0.5 day)

> **Disposition (2026-07-03, D-ζ):** folds into roadmap M1 — items 1–3 ride
> the P-1.6 diagnostics-drawer session; items 4–5 are PM actions (unchanged).

1. Structured JSON logging when `VERCEL_ENV`/`LOG_FORMAT=json` (request_id,
   path, status, duration) — greppable in Vercel log viewer; add a Log Drain
   later if needed.
2. Make `/api/health` serverless-aware (per-instance metrics labeled as such;
   drop uptime claims on Vercel).
3. Optional Sentry (free tier) via `SENTRY_DSN` env — error tracking with
   request IDs; no-op when unset.
4. Uptime check on `https://aruco.tools/api/healthz` (UptimeRobot free).
5. Enable Vercel Web Analytics (free, privacy-friendly) for PM usage insight.

## Phase 7 — Documentation & AI tooling to A− (~1 day)

> **Disposition (2026-07-03, D-ζ):** folds into roadmap M0 — item 1 as an M0
> micro-PR (version single-sourcing), item 2 into the P-0.11 M0 gate
> (`scripts/validate_docs.py` + CI check); items 3–6 land with P-3.5 launch
> prep.

1. **Version single-sourcing**: `__init__.py` reads
   `importlib.metadata.version("aruco-generator")`; remove version claims
   from CLAUDE.md, AGENTS.md, README badge; release script owns the rest.
2. **Symbol anchors**: AI_NAVIGATION.xml drops line numbers for
   `symbol="Class.method"` references; add `scripts/validate_docs.py` to CI:
   every referenced file/symbol exists, endpoint list matches `app.url_map`.
3. **Consolidate**: CLAUDE.md + AGENTS.md become thin protocol files pointing
   at one navigation map; merge docs/ai/NAVIGATION.md into it; archive
   completed task.md/walkthrough.md cycles to docs/ai/archive/.
4. **Trim per-file XML headers** to ≤8 lines (name, purpose, gotchas); drop
   per-file version fields (git is the history). `app.py` header: 190 → ~8.
5. **Product docs**: README rewritten as product front door (live URL, what
   it does, screenshots, "built by a CV PM with Claude" story); docs page
   gets an API reference (endpoints, params, envelope schema); CONTRIBUTING.md.
6. Update AGENTS.md deployment section: Vercel-only, aruco.tools, staging
   model above; delete Vercel-legacy/Replit references in docs/devops/.

## Phase 8 — Product launch polish (~0.5 day + PM input)

> **Disposition (2026-07-03, D-ζ):** SUPERSEDED by the roadmap — homepage v2
> is bridge P-1.5; the launch checklist, SEO/OG work, and feedback channel
> are bridge P-3.5.

- Home page copy + OG/meta tags + favicon; "free & open source" positioning.
- GitHub repo: description, topics, social card, link to aruco.tools.
- Feedback channel: GitHub Issues link in footer.
- Launch checklist: domain live, SSL valid, analytics on, uptime monitor on,
  README badges green, `vercel rollback` rehearsed once.

## Sequencing & effort

Total ≈ 5-6 focused days. Order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8.
Phases 2+3 are the gate for making aruco.tools public (don't point the domain
at production until the XSS/CSP/secret work lands). Phases 4-7 can land as
independent PRs, each through the preview→main pipeline.

## Reece's (PM) action items — things only you can do

1. Namecheap: switch aruco.tools nameservers to Vercel (or add the records
   `vercel domains add aruco.tools` prints).
2. GitHub repo settings: enable branch protection on `main` (require CI).
3. Vercel dashboard: disable Deployment Protection for production; confirm
   Web Analytics on.
4. Decide: keep `staging.aruco.tools` branch domain, or live with PR previews
   only (recommendation: add staging later, previews suffice for now).
