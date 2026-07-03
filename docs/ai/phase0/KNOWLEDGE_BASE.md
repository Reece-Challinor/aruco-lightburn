<!--
<ai_agent_documentation>
  <file_meta>
    <name>KNOWLEDGE_BASE.md</name>
    <version>0.9.0</version>
    <type>phase0_knowledge_base</type>
    <purpose>Evidence-stamped extraction of protocols, contracts, idioms, seams, test infrastructure, and CI gates. Phase 0 deliverable D-2 (+D-6 assumption register).</purpose>
    <last_updated>2026-06-12</last_updated>
    <maintainer>Solo founder + Claude Code</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Phase 0 Knowledge Base (D-2)

All entries stamped `verified: ca6dc1f` (branch) / `eb8ba3f` (main) unless noted.
Sections still being populated are marked PARTIAL.

## Protocols (from Tier-1 docs — COMPLETE)

- **AGENTS.md v1.2.0 absorbed.** Deltas vs the bridge standing footer (now
  patched into the bridge):
  - Per-change documentation: update `docs/ai/walkthrough.md` (delivery report:
    Summary/Changes/Tests/Commit Plan format) and `docs/ai/task.md` per change —
    not just CHANGELOG.
  - Complex changes: plan in `docs/ai/implementation_plan.md` first. NOTE: that
    file currently hosts the LIVE "Production Launch Program" — see
    DECISION_LOG D-ζ for reconciliation.
  - Trunk-based: `main` is production (Vercel auto-deploys it); previews per
    PR; `staging` branch → staging.aruco.tools. Branch protection on main
    requires CI.
  - Releases: annotated tags `vX.Y.Z` on main trigger GitHub Releases + Docker
    builds; `scripts/release.py X.Y.Z` bumps all 4 version locations atomically
    (release-level only — per-PR version bumps NOT required; answers a
    readiness question).
  - Deployment checklist (docs/deployment_checklist.md) governs releases; notes
    a `codex/` branch-prefix convention for release branches.
- **Error envelope (docs/ai/ERROR_HANDLING.md):** all calibration/validation
  endpoints return `{success, data|error, warnings[], request_id, timestamp,
  version}`; errors carry `{message, type, status, fields{}, suggestions[]}`.
  Client-side code (F-02/F-09 rendering, future fetches) MUST parse this
  envelope. DB-optional writes return success+warning (pattern retained for
  frozen pattern storage).
- **Live program:** `docs/ai/task.md` (updated today) — Phases 1–4 of the
  Production Launch Program complete (Vercel deploy, security, CI/uv, code
  quality); Phase 5 (testing: coverage floor, calibration_web tests) ACTIVE =
  the `feat/phase-5-testing` branch; pending PM actions: aruco.tools DNS,
  deployment protection. Phases 6 (observability) / 7 (docs) / 8 (product
  polish) not started → D-ζ reconciliation with the roadmap program.

## Contracts (PARTIAL — backend shapes; full inventory in T0.4 completion)

- Production stack: Vercel project `reece-challinors-projects/aruco-lightburn`,
  domains aruco.tools / staging.aruco.tools (DNS pending), stateless default
  (in-memory SQLite, USE_DB=False locked as the serverless decision).
- CSP (app.py:272-283): `default-src 'self'; script-src 'self'; style-src
  'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self';
  object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors
  'none'` — **no `wasm-unsafe-eval`, no worker-src** (workers fall back to
  script-src 'self' = OK for same-origin worker files; wasm compile NOT OK).
- Permissions-Policy (app.py:297): `camera=(), microphone=(), geolocation=()`
  — **camera globally disabled**. See U-7 finding below.
- Upload caps (app.py): MAX_CONTENT_LENGTH 12 MB, MAX_UPLOAD_IMAGE_BYTES 10 MB,
  MAX_IMPORT_BYTES 2 MB, MAX_IMAGE_PIXELS 20 MP, MAX_IMAGE_DIMENSION 8000.
  F-01 upload path (15–40 images) is per-request per-image — client must
  upload-process locally anyway (A3); caps only affect legacy server
  validation endpoints.
- Rate limiting: memory storage, per-instance on serverless (per-worker under
  Gunicorn) — i.e., limits are approximate in production; tests disable via
  RATELIMIT_ENABLED=0 (conftest.py).

## Idioms (PARTIAL)

- Route validation: `_get_request_json` / `_validate_dictionary` /
  `handle_api_errors` decorators (advanced_web.py) — new endpoints must reuse.
- cv2-absent guard: raise `APIServiceUnavailableError("OpenCV required …")`
  (advanced_web.py) / `RuntimeError` in engine (calibration.py:543) — copy this
  pattern in new cv2-requiring code.
- Image checksum: `_checksum_image` (calibration.py:113) included in
  generation metadata — keep for new pattern types (F-11).

## Seams (frontend — PARTIAL; absorb/replace table due in T0.5 completion)

- `static/js/core/state.js` StateManager: localStorage, dot-path get/set —
  EXTEND (per bridge P-1.2), do not replace.
- `static/js/core/notifications.js` + `window.escapeHtml` (XSS-hardened
  2026-06-12): the existing toast seed — C-17 either wraps or replaces it;
  decide at P-0.4 implementation, log the choice.
- Bootstrap 5.3.3 vendored locally (no CDN) — CSP-compatible; F-90 tokens
  layer on top initially, Bootstrap removed per-workspace as each migrates.
- 11 innerHTML sinks were purged for XSS (Phase 2) — new components must not
  reintroduce; use the established escapeHtml/createElement patterns.

## Test infrastructure (COMPLETE for current needs)

- `make validate` = format-check + lint + typecheck (mypy on core/+export/) +
  test + test-qa. **Measured: 9 s wall** (BASELINE_REPORT) — per-PR full
  validation is free; no fast/slow split needed.
- `make coverage`: pytest --cov, **--cov-fail-under=65** (Makefile:116). CI
  runs it; JS additions don't count against it (Python-only cov) but new
  Python must not dilute below 65%.
- Snapshots: literal files in `tests/snapshots/` (preview_basic.svg,
  lightburn_basic.lbrn2), compared by test_export_snapshots.py; **blessing =
  regenerate the files** (no tool; do deliberately, justify in commit).
- Pre-commit runs targeted pytest subsets (UI smoke, API smoke, export
  consistency, generation quality) via uv — commits are self-validating
  beyond lint.
- conftest.py: session-scoped app/client fixtures; RATELIMIT_ENABLED=0 set
  before app import.

## CI gates (COMPLETE)

- ci.yml: matrix Python 3.11+3.12; `uv sync --locked` → `make
  check-requirements` (requirements.txt ↔ uv.lock sync gate) → `make validate`
  → `make coverage`; Codecov upload on 3.12. **No Node toolchain** (U-8
  answer). codeql.yml, docker.yml, release.yml also present; release.yml runs
  `make validate` on tags.
- Implication recorded in bridge: first JS-test prompt (P-0.5) must add
  `actions/setup-node` to ci.yml and a `make test-js` target wired into
  `make test`.

## Assumption & unknown register (D-6)

| ID | Item | Status | Evidence / resolution |
|---|---|---|---|
| U-1 | aruco/charuco APIs in stock opencv.js | **OPEN** | Spike T0.7 (blocks M1+, not M0) |
| U-2 | wasm calibrateCameraCharuco perf | **OPEN** | Spike T0.7 (blocks M2) |
| U-4 | js-yaml + `!!opencv-matrix` | **OPEN** | T0.7 pre-check (F-04 estimate only) |
| U-7 | CSP/Permissions vs wasm+camera | **CONFIRMED BLOCKING, delta known** | app.py:272-297. Required deltas: `script-src 'self' 'wasm-unsafe-eval'`; `camera=(self)`. Patched into bridge P-1.1/P-1.3 prompts |
| U-8 | Node in CI | **ANSWERED: absent** | ci.yml; setup-node step required at P-0.5 |
| — | release.py semantics | **ANSWERED** | Release-level bumps only; not per-PR |
| — | Snapshot blessing | **ANSWERED** | Regenerate files in tests/snapshots/ |
| — | task.md live-task conflict | **ANSWERED: conflict exists** | Production Launch Program ↔ roadmap; D-ζ |
| — | validate <5 min (O5) | **CONFIRMED** | 9 s measured |
| — | main == origin/main, branch delta docs-only | **CONFIRMED** | T0.1 SHAs |
| — | Unmerged-branch divergence (codex/*, feat/phase-2..4) | **OPEN (low risk)** | Phase-2..4 branches appear merged (commit log); verify in T0.6 |
| — | exporters dependency-light | **CONFIRMED** | pyproject deps; no reportlab/ezdxf |
