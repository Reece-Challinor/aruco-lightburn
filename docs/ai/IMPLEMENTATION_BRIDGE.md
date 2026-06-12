<!--
<ai_agent_documentation>
  <file_meta>
    <name>IMPLEMENTATION_BRIDGE.md</name>
    <version>1.0.0</version>
    <type>gap_analysis_execution_plan</type>
    <purpose>Bridge between the current codebase and the target state in PRODUCT_ROADMAP.md: current-state assessment, roadmap-to-code gap analysis, phased implementation bridge, and copy-paste execution prompts for AI coding agents.</purpose>
    <last_updated>2026-06-12</last_updated>
    <maintainer>Solo founder + Claude Code</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Implementation Bridge — From Current Codebase to Roadmap Target State

**Companion to:** `docs/ai/PRODUCT_ROADMAP.md` v3.0.0 (the *what* and *why*; this
document is the *how* and *in what order*). This document does not restate roadmap
rationale — it cites it (`F-nn`, `PX-n`, `C-nn`, `§n` references resolve there).

**How to use this document:**
- §1–§2 are the audit: what exists, what's missing, what must change.
- §3 is the dependency-ordered plan.
- §4 contains **execution prompts (P-x.y)** written to be pasted directly into a
  Claude Code session. Each is scoped to one implementation cycle (one session,
  occasionally two). Run them in the stated order unless marked parallelizable
  (∥). Every prompt ends with the same standing footer (§4.0) — apply it even when
  pasting prompts individually.
- §6 defines checkpoints (CP-n) where you stop and re-plan before continuing.

All file references verified against the codebase as of 2026-06-12
(main + `feat/phase-5-testing`, which differ only by `docs/ai/PRODUCT_ROADMAP.md`).

---

## 1. Current State Assessment

### 1.1 Architecture summary (as built)

**Backend — Flask application factory.**
- `app.py:213` `create_app()`; module-level `app = create_app()` (~line 319) is the
  WSGI entry. Vercel entry: `api/index.py` adds repo root to `sys.path` and imports
  `app`; `vercel.json` rewrites **all** routes to `/api/index` and serves
  `/static/*` with `Cache-Control: public, max-age=31536000, immutable` (already
  ideal for the future wasm asset).
- Three blueprints registered inside `create_app()` (`app.py:306-312`) to avoid
  circular imports: `web_bp` (`aruco_generator/web/web.py` — pages, preview,
  download, batch, presets, SVG/PDF export, health), `calibration_bp`
  (`aruco_generator/web/calibration_web.py` — charuco/aruco_board/apriltag/
  apriltag_grid generation, pattern export/import, metrics), `advanced_bp`
  (`aruco_generator/web/advanced_web.py` — 3D coords, pose board, YAML/ROS/DXF/STL
  export, validation endpoints).
- Hardening already present: rate limiting (`flask-limiter`, e.g. `15 per minute`
  on validation endpoints), CSP/security headers, upload size/pixel caps
  (`MAX_UPLOAD_IMAGE_BYTES` 10 MB, `MAX_IMAGE_PIXELS` 20 MP in `app.py`),
  observability (`aruco_generator/core/observability.py`), structured error
  payloads (`build_error_payload`).

**Core engine.**
- `aruco_generator/core/aruco.py` (896 lines): `ArUCOGenerator`, strategy pattern —
  OpenCV when available, pure-Python fallback dict otherwise. All 16 standard
  dictionaries mapped (`4X4_50` … `7X7_1000`).
- `aruco_generator/core/drawing.py`: `DrawingContext` SVG renderer with O(n²)
  rectangle merging (laser-path optimization).
- `aruco_generator/calibration/calibration.py` (783 lines):
  `CalibrationPatternGenerator` — ChArUco boards (line 116), ArUco boards (214),
  AprilTags (330), AprilTag grids (428), **`calibrate_camera()` (526 — checkerboard
  only, subpixel refinement, reprojection error, NO ROUTE CALLS IT)**, calibration
  YAML/JSON/ROS export (619/698/708).
- `aruco_generator/validation/validation.py` (619 lines): `DetectionValidator` —
  test patterns w/ synthetic distortion+occlusion, `detect_markers`,
  `verify_marker_quality` (quiet zone 445, bit errors 498, corner quality 516,
  contrast 545, sharpness 559), Hamming distance (219), detection report (242),
  failure analysis (423).
- `aruco_generator/export/exporters.py` (600 lines): `ProfessionalExporter`
  (OpenCV YAML 34, ROS 127, DXF 195, STL 291) + `PDFExporter` (454). Note:
  exporters are dependency-light (no reportlab/ezdxf in `pyproject.toml` deps —
  PDF/DXF are generated directly), which is why they run on Vercel.
- `aruco_generator/export/lightburn.py` (354 lines): .lbrn2 XML — **the moat**.

**Database.** Three modes (DATABASE_URL → Postgres; USE_SQLITE → file; neither →
in-memory SQLite). Models in `aruco_generator/db/models.py` incl. `DetectionMetric`;
pattern persistence + `/api/calibration/metrics` POST (`calibration_web.py:1014`).
In serverless production this is effectively nonfunctional (per-invocation
in-memory DB) — confirmed roadmap decision F-10: remove metrics writes, freeze
patterns.

**Frontend.** Server-rendered Jinja: `templates/base.html` (Bootstrap 5 vendored,
dark navbar, breadcrumbs, skip-nav — some a11y groundwork exists) + 5 pages
(`home`, `generate`, `calibration`, `validation`, `documentation`). JS: vanilla
classes — `static/js/core/api.js` (`ArUCOAPI` client), `state.js` (`StateManager`
with localStorage + dot-path get/set — a real, extendable seed for §13.3 roadmap
state), `notifications.js`, `navigation-simple.js`; one module per page in
`static/js/pages/`. CSS: `static/css/{main,navigation,calibration,validation,workflow}.css`
— Bootstrap-default light look, no token system.

**Quality infrastructure.** Pytest suite (~19 files incl. API, UI smoke, snapshot
exports, generation quality, security, navigation); `tests/conftest.py` provides
`app`/`client` fixtures with `RATELIMIT_ENABLED=0`; pre-commit (black, isort,
flake8, bandit, custom import/quality/export checks); `make validate` / `make ci`;
`AI_NAVIGATION.xml` v2.6.2 as the structure map; per-file
`<ai_agent_documentation>` headers.

### 1.2 Roadmap requirement status matrix

| Roadmap item | Status | Evidence |
|---|---|---|
| FR-1 Generation (markers/boards/tags, 7 export formats) | ✅ Exists | §1.1 engine + exporters; protected by snapshot tests |
| F-07a print ruler | ❌ Missing | `PDFExporter` (exporters.py:454) has no scale bar |
| F-11 ChArUco diamonds | ❌ Missing | No `drawCharucoDiamond` usage in calibration.py |
| F-03 calculator | ❌ Missing | No size/distance math anywhere |
| F-04 converter | ❌ Missing | Calibration *export* exists (calibration.py:619-740) — reusable as format reference; no import/convert UI or client adapters |
| F-08 advisor | ◐ Partial | Hamming endpoint exists (`/api/validation/hamming_distance`, advanced_web.py:604); no decision logic or UI |
| F-09 surface validation engine | ◐ Partial | Engine complete (validation.py); endpoints exist (detect/verify_quality/detection_report/batch_test); `templates/validation.html` + `pages/validation.js` expose only a fraction |
| F-90 Workbench (tokens/shell/components/IA) | ❌ Missing | Bootstrap defaults; 5-page IA (Home/Generate/Calibration/Validation/Documentation) vs target six workspaces; zero shared components |
| F-00 vision-core (OpenCV.js/worker/camera) | ❌ Missing | No wasm, no worker, no getUserMedia anywhere in static/ |
| F-02 Live Detection Validator | ❌ Missing | Server-side detect exists for uploads only (15/min rate limit makes it unusable for live) |
| F-01 Calibration Studio | ◐ Partial (backend seed) | `calibrate_camera()` (calibration.py:526) — checkerboard-only, unrouted; calibration export formats done; zero capture/gates/confidence/UI |
| F-05 Parameter Playground | ❌ Missing | No DetectorParameters surface anywhere |
| F-06 Runtime Config Exporter | ◐ Partial | ROS export (exporters.py:127) emits pattern metadata — wrong shape vs aruco_ros/apriltag_ros configs; no code snippets |
| F-07b print verification (webcam) | ❌ Missing | Depends on F-00/F-02 |
| F-12 landing pads | ◐ Partial | `drone_landing` preset (web.py:505) is a flat grid — not nested/recursive, no altitude chart |
| F-10 cut DB metrics | ❌ Not done | `/api/calibration/metrics` + `DetectionMetric` live |
| FR-11 profiles + status chips | ❌ Missing | `StateManager` seed exists; no profiles, no chips, no cross-page state |
| PXA (PX-1…12, C-01…20, tokens) | ❌ Missing | §3.5 of roadmap: experience layer is greenfield |
| F-13…F-21 (Phase 3/4) | ❌ Missing (by design) | Deferred |

### 1.3 Constraints, technical debt, and delivery risks

**Architectural constraints (work with, not against):**
1. **Vercel serverless**: no websockets/long compute server-side → interactive CV
   must be client-side (already the roadmap's F-00 bet). The catch-all rewrite to
   `api/index` means *new client-heavy pages still render through Flask* — fine,
   but route additions must go through blueprints, and old-URL redirects (IA
   cutover) are Flask redirects, not vercel.json rules.
2. **Blueprint import discipline** (CLAUDE.md): never import `app` from modules
   imported by `app.py`. New routes follow the existing in-factory registration.
3. **Rate limits** on validation endpoints are correct for server protection and
   *wrong* for interactive loops — confirms client-side detection; do not "fix" by
   raising limits.
4. **`numpy==1.26.4` pin + opencv-python-headless**: server-side cv2 features must
   stay compatible; OpenCV.js version (client) should be chosen near the server's
   4.x for behavioral consistency of detection results.

**Technical debt relevant to the plan:**
- Dead `calibrate_camera()` (checkerboard-only) — extend to ChArUco
  (`calibrateCameraCharuco` equivalent) but note the *production* solver will be
  client-side; the Python path becomes the **accuracy reference harness** (M2),
  not the product. This reframes "debt" into the cross-validation asset NFR-5
  needs.
- DB persistence (patterns/metrics) — F-10 removes the misleading half.
- `tests/test_export_formats.py` working-tree edit un-skips 2 LightBurn tests that
  **currently fail** (test helper splits lbrn2 `VertList` coords on `,`
  incorrectly — see test line 253). Resolve before M0 starts (P-0.0).
- Five separate page CSS files with overlapping rules — superseded by tokens.css +
  components; plan absorbs rather than refactors them (old pages keep old CSS
  until each workspace migrates).
- `static/js/core/api.js` (`ArUCOAPI`) is generation-API-shaped; vision-core is a
  *separate* module family — don't force-fit.

**UX gaps:** full audit in roadmap §3.5 (no handoffs, no verdicts, no chips, flat
disclosure, wrong IA cut). The bridge treats roadmap §3.5 as the authoritative UX
gap list; §2 below maps each to code.

**External dependencies/unknowns (drive §6 spikes):**
U-1 aruco/charuco API availability in stock opencv.js builds (biggest unknown,
gates everything camera);
U-2 `calibrateCameraCharuco` performance in wasm (40 frames × 1080p);
U-3 browser/camera matrix behavior (iOS Safari, Windows camera-in-use, UVC);
U-4 js-yaml handling of OpenCV `%YAML:1.0` + `!!opencv-matrix` (custom schema);
U-5 wasm bundle size vs. Vercel static serving (fine technically; UX cost only).

---

## 2. Roadmap-to-Code Gap Analysis

Per feature: **Target** (desired end state, cites roadmap spec) → **Current** →
**Gap** → **Changes** (files/systems/APIs/UI/infra). Ordered by build order, not ID.

### F-10 — Remove DB metrics, freeze pattern persistence
- **Target:** No misleading persistence surface (roadmap §9.6, PX-9).
- **Current:** `POST /api/calibration/metrics` (calibration_web.py:1014-1069)
  writes `DetectionMetric`; pattern CRUD persists when USE_DB.
- **Gap:** Delete the metrics write path; freeze (don't extend) pattern storage.
- **Changes:** `calibration_web.py` (remove route + imports), `db/models.py`
  (remove `DetectionMetric` usage; keep table def commented or drop), tests
  referencing metrics (grep `detection_metric`/`metrics` in tests/),
  `AI_NAVIGATION.xml`, `static/js/core/api.js` if it has a metrics method.

### F-90 — Workbench foundation (tokens, shell, components, IA cutover)
- **Target:** Roadmap §5 (six workspaces, shell layout), §6 (tokens), §7 (C-01…20
  subset: C-01/02/03/09/12/13/14/17), dark-first.
- **Current:** Bootstrap-default light theme; 5-page IA; `base.html` navbar with
  Home/Generate/Calibration/Validation/Documentation; no components; page-scoped
  CSS/JS; breadcrumbs + skip-nav exist.
- **Gap:** Entire experience substrate.
- **Changes:** NEW `static/css/tokens.css`; NEW `static/js/components/` (8 modules
  M0); rewrite `templates/base.html` → C-01 shell (keep skip-nav; drop
  breadcrumbs — workspaces are flat); route changes in `web.py` +
  `calibration_web.py` (page routes: add `/live`, `/debug`, `/convert`, `/learn`;
  `/calibration`→`/calibrate`; 301s from `/validation`→`/debug`,
  `/documentation`→`/learn`); templates renamed/added per workspace; update
  `tests/test_navigation.py`, `tests/test_ui_pages.py`; `navigation.css` absorbed
  into tokens+shell.

### F-03 — Size/distance calculator
- **Target:** Roadmap §10.3 (standalone Learn page + inline Generate strip;
  qualified outputs per PX-9).
- **Current:** Nothing.
- **Gap:** Pure-JS math module + two surfaces.
- **Changes:** NEW `static/js/lib/marker-math.js` (+ Node-runnable unit tests);
  NEW `templates/learn/calculator.html` route under Learn; `templates/generate.html`
  + `pages/generate.js` gain the advisor strip (C-14 + live recompute on the
  existing size field).

### F-04 — Calibration file converter
- **Target:** Roadmap §10.4: client-side, 5 formats, auto-detect, round-trip
  tested, C-20 preview.
- **Current:** Server has *emit-only* knowledge of OpenCV YAML/ROS/JSON
  (calibration.py:619-740, exporters.py:34-194) — use as format ground truth and
  to generate fixtures. No import, no kalibr, no UI.
- **Gap:** Client adapter library + Convert workspace UI + fixture corpus.
- **Changes:** NEW `static/js/vision/formats/` ({opencv-yaml,ros1,ros2,kalibr,
  json}.js + `detect.js`), vendored js-yaml (`static/vendor/`), custom schema for
  `!!opencv-matrix`; NEW `templates/convert.html` + `static/js/workspaces/convert.js`
  (C-08 paste/drop, C-20 preview, C-18 export); NEW `tests/fixtures/calibration_formats/`
  (real files from cv2, ROS1/2, kalibr); Node round-trip property tests wired into
  `make test` (add an npm-less node test runner or simple `node --test`).

### F-08 — Dictionary advisor
- **Target:** Roadmap §10.8: 3 inputs → ranked C-20 recommendation + rationale;
  "Apply" pre-fills Generate (PX-8).
- **Current:** Hamming endpoint (`advanced_web.py:604`) computes distances; no
  recommendation logic, no UI.
- **Gap:** Decision module + UI panel.
- **Changes:** NEW `static/js/lib/dictionary-advisor.js` (uses marker-math F-03 +
  fetches Hamming stats; static per-dictionary min-distance table can be
  precomputed server-side once and shipped as JSON to avoid runtime API calls);
  Generate workspace "Help me choose" panel; Debug workspace analyzer mode reuses
  the same module.

### F-07a — Print-scale ruler
- **Target:** 100 mm bar + instruction on PDF/SVG; outside cut paths in lbrn2/DXF
  (roadmap §10.7 AC1).
- **Current:** `PDFExporter.generate_pdf` (exporters.py:465),
  `_draw_marker_vector` (572); SVG via `DrawingContext`; snapshot tests in
  `tests/test_export_snapshots.py`.
- **Gap:** Ruler drawing + placement rules + snapshot updates.
- **Changes:** `exporters.py` (PDF), `core/drawing.py` (SVG ruler primitive),
  verify `lightburn.py`/DXF untouched by ruler (assert absence), update snapshots.

### F-09 — Surface validation engine
- **Target:** Debug workspace renders quality/detection reports as C-09 verdicts
  (roadmap §10.5 context, F-09 row).
- **Current:** Endpoints live: `/api/validation/detect`, `verify_quality`,
  `detection_report`, `batch_test` (advanced_web.py:446-744). `validation.html`
  exposes a subset.
- **Gap:** UI that consumes the full report shape; verdict mapping (raw report →
  tier + dominant cause strings); server-upload disclosure per PX-6 (these are
  server-side endpoints).
- **Changes:** `templates/debug.html` (Quality report mode), `workspaces/debug.js`,
  verdict-mapping table in JS (thresholds from the Python report fields),
  explicit "sent to server for analysis" label on C-08.

### F-11 — ChArUco diamonds
- **Target:** Generate · Diamond mode.
- **Current:** None.
- **Gap:** One generator method + route + mode segment.
- **Changes:** `calibration/calibration.py` (new `generate_charuco_diamond` using
  `cv2.aruco.drawCharucoDiamond`, fallback-aware), `calibration_web.py` route,
  Generate UI mode, tests mirroring `tests/test_charuco.py` style.

### F-00 — vision-core platform
- **Target:** Roadmap §13.1-13.2: loader, worker protocol (latest-frame
  backpressure), camera-manager, frame-gates, confidence constants, Mat hygiene.
- **Current:** Nothing client-side; `vercel.json` static caching already correct
  for the wasm asset.
- **Gap:** The entire module family + its test harness.
- **Changes:** NEW `static/js/vision/{opencv-loader,vision.worker,camera-manager,
  frame-gates,confidence}.js`; vendored pinned `opencv.js`+wasm under
  `static/vendor/opencv/<version>/`; Node unit tests for protocol/gates (wasm
  loadable in Node for math-level tests); diagnostics counters exposed for C-16.

### F-02 — Live Detection Validator
- **Target:** Roadmap §10.2 AC1-AC5 (≤5 s first overlay, jitter, auto-try-all,
  pose w/ profile, demo mode).
- **Current:** Server detect for uploads only.
- **Gap:** Live workspace end-to-end on F-00.
- **Changes:** NEW `templates/live.html` + `workspaces/live.js`; C-04/05/06
  components; verdict thresholds ported from `validation.py` (_calculate_contrast
  545 / _calculate_sharpness 559 / quiet zone 445 → JS equivalents in
  frame-gates.js); demo mode (renders an SVG marker from the existing
  `/api/preview` or client-side bitmap); homepage v2 (§5.5) linking it.

### F-01 — Calibration Studio
- **Target:** Roadmap §10.1 AC1-6 + §11 (nine subsystems) + §12.4 wizard.
- **Current:** Python `calibrate_camera()` checkerboard-only, unrouted; ChArUco
  *generation* solid; export formats done server-side; F-04 adapters (client) by
  then.
- **Gap:** Client capture flow (gates/quotas/fusion), client ChArUco solve,
  confidence scoring + held-out check, results UI, profiles, **plus** a Python
  accuracy-reference harness (extend `calibrate_camera` to ChArUco for
  cross-validation only — NFR-5).
- **Changes:** NEW `templates/calibrate.html` + `workspaces/calibrate.js`;
  C-07/10/15/19 components; `vision.worker.js` gains
  `interpolateCornersCharuco` + `calibrateCameraCharuco` ops; `confidence.js`
  scoring; profile store in extended `state.js`; Python: `calibration.py` new
  `calibrate_camera_charuco()` + offline harness script
  `scripts/calibration_reference_check.py` + golden frame sets in
  `tests/fixtures/calibration_frames/`; Learn methodology page.

### F-05 — Parameter Playground
- **Target:** Roadmap §10.5 AC1-AC4 (<300 ms re-detect, rejected candidates,
  grouped params, code export).
- **Current:** None (server `detect_markers` doesn't expose DetectorParameters).
- **Gap:** Debug · Playground mode on F-00; staged-pipeline attribution.
- **Changes:** `workspaces/debug.js` playground mode; worker op
  `detectWithParams` returning `rejectedImgPoints`; parameter schema module
  (groups/ranges/tooltips/defaults) `static/js/lib/detector-params.js`; C-18
  exports (Python/C++/aruco_ros templates client-side).

### F-06 — Runtime Config Exporter
- **Target:** Roadmap §10.6: aruco_ros/apriltag_ros/JSON geometry + executable
  Python snippet; CI executes emitted snippets.
- **Current:** `export_ros_format` (exporters.py:127) — wrong shape; board object
  points computable from existing generators.
- **Gap:** Correct serializers + snippet templates + execution-test harness.
- **Changes:** NEW `aruco_generator/export/runtime_configs.py` (geometry
  serializers + Jinja snippet templates), routes on `advanced_bp`, Convert
  workspace UI mode; NEW `tests/test_runtime_configs.py` that renders a board
  image (existing generators), executes the emitted Python in a subprocess, and
  asserts detection.

### F-07b / F-12 — Print verification (webcam) / Landing pads
- **F-07b changes:** Live workspace "Verify print" mode; measurement math in
  `frame-gates.js`/`marker-math.js`; C-10 verdict (±1%); requires profile (PX-3
  degradation to ruler-ratio mode).
- **F-12 changes:** Generate · Landing pad mode (C-07 mini-flow);
  `calibration.py` or new `aruco_generator/core/landing_pad.py` nested layout
  generator; altitude-coverage chart (marker-math); tiled PDF in `exporters.py`
  (multi-page + alignment marks); PX4/ArduPilot snippet via F-06 templates.

### Cross-cutting: state, chips, handoffs (FR-11 / PX-3 / PX-5 / PX-8)
- **Target:** Roadmap §13.3-13.4 (versioned state, global store, chips as only
  global-state UI, handoff slices).
- **Current:** `StateManager` (state.js) — localStorage + dot-path; no schema
  versioning, no subscribers, no cross-page contracts.
- **Gap:** Extend (not replace): `schemaVersion` per namespace, subscribe(),
  `BoardSpec`/`MarkerConfig`/`CalibrationProfile` typed (JSDoc) shapes, handoff
  helper (`handoff.send('calibrate', {boardSpec})` → target workspace pre-fill).
- **Changes:** `static/js/core/state.js` (extend), NEW
  `static/js/core/models.js` (shapes + migrations), C-02 chips consume store.

---

## 3. Implementation Bridge (Phases, Dependencies, Sequencing)

### 3.1 Dependency graph (what unlocks what)

```
P-0.0 test repair ─┐
F-10 cleanup ──────┤
                   ├─► F-90 tokens+shell+IA ──► all UI work
                   │        │
                   │        ├─∥─ F-03 calc ──► F-08 advisor ─► (F-12 chart)
                   │        ├─∥─ F-04 converter ─────────────► F-01 exports
                   │        ├─∥─ F-07a ruler   ├─∥─ F-09 validation UI
                   │        └─∥─ F-11 diamonds
                   │
SPIKE U-1/U-2 ─────┴─► F-00 vision-core ──► F-02 Live ──► F-01 Studio ──► F-07b
                                              │                │
                                              └──► F-05 Playground
state.js extension (cross-cutting) ──► chips ──► F-01 profiles, F-02 pose, F-06
F-06 configs ◄── F-01 (optional profile embed); F-12 ◄── F-06 snippets
```

**Foundational work that unlocks multiple items (build first, keep small):**
1. **F-90 tokens + shell + core components** — every screen thereafter.
2. **state.js extension + models** — chips, handoffs, profiles, resume (5
   features).
3. **F-00 vision-core** — F-01/02/05/07b.
4. **F-04 format adapters** — Convert UI now, Studio exports later (write once).
5. **The U-1 spike** — go/no-go information for the entire camera track; cheapest
   risk retirement available.

### 3.2 Phase structure (mirrors roadmap M0–M3; adds explicit pre-phase)

| Phase | Content | Sessions (est) | Parallelizable |
|---|---|---|---|
| **Pre** | P-0.0 repair failing LightBurn tests; run U-1 spike early (can run during M0) | 1–2 | Spike ∥ with all of M0 |
| **M0** | F-10 → F-90 (tokens→shell→IA→components) → F-03 ∥ F-04 ∥ F-07a ∥ F-11 → F-08 → F-09 → gate | 14–16 | F-03/F-04/F-07a/F-11 mutually ∥ after F-90 |
| **M1** | F-00 (loader→worker→camera) → state/chips → F-02 core → gates+verdicts → troubleshooting → demo+homepage → gate | 12–14 | state/chips ∥ with F-00 worker work |
| **M2** | Python ChArUco reference harness → upload-path solve → capture+gates+quotas → confidence → results/profiles/exports → resume → usability → gate | 14–16 | Reference harness ∥ with capture UI |
| **M3** | F-05 → F-06 → F-12 → F-07b → launch | 10–12 | F-06 ∥ F-05 after worker op lands |

**Deferred (do not start before CP-4):** F-13 stereo, F-14 benchmark, F-15 CLI,
F-16 PWA, F-17 share URLs (unless trivially needed for A-5 earlier), all Phase 4.

---

## 4. Execution Prompts

### 4.0 Standing footer (applies to every prompt below)

> **Standing requirements for this task:**
> - Read `docs/ai/PRODUCT_ROADMAP.md` §2.2 (PX principles) and §17 (checklists)
>   first; this task must pass the §17.3/§17.4 checks relevant to it.
> - Follow CLAUDE.md: never import `app` from modules imported by `app.py`;
>   Black/isort/flake8 clean; update `AI_NAVIGATION.xml` and the touched files'
>   `<ai_agent_documentation>` headers; update `docs/CHANGELOG.md`.
> - Run `make validate` before declaring done; add/adjust tests so every
>   acceptance criterion below is covered by an automated test where feasible.
> - UI work: tokens from `static/css/tokens.css` only; components from
>   `static/js/components/` only; if a needed component/token is missing, extend
>   it in this PR and update `PRODUCT_ROADMAP.md` §6/§7 accordingly.
> - Do not widen scope; if you discover adjacent work, note it in the PR
>   description instead of doing it.

### Phase Pre

---

**P-0.0 — Repair the un-skipped LightBurn tests** *(1 session)*

> In `tests/test_export_formats.py`, two tests were un-skipped and currently fail:
> `TestLightBurnExport::test_lightburn_layers` and `test_lightburn_coordinates`
> (ValueError at line ~253: the test splits lbrn2 vertex coordinates on `,` but
> the `.lbrn2` `VertList`/`V` encoding produced by
> `aruco_generator/export/lightburn.py` doesn't match that assumption).
> **Objective:** make both tests meaningful and green. First read
> `lightburn.py` to learn the actual XML shape (Shape/VertList/Prim encoding),
> then fix the *tests'* parsing to match reality. If parsing reveals a genuine
> exporter bug (coordinates not in mm where they should be, layers missing),
> fix the exporter instead and update `tests/test_export_snapshots.py` snapshots
> deliberately (justify in the commit message).
> **AC:** both tests pass without `skip` markers; layer test asserts ≥2 distinct
> layer indices (fill/border); coordinate test asserts a 40 mm marker's geometry
> spans 40±0.1 mm in lbrn2 units. **Testing:** `make test-export` and full
> `make validate` green.

---

**P-0.S — SPIKE: OpenCV.js aruco/charuco viability (U-1, U-2)** *(1 session;
run ∥ with M0; produces a written verdict, minimal code)*

> **Objective:** determine go/no-go facts for the camera track. In a throwaway
> branch: (1) obtain the latest stable opencv.js 4.x build; verify at runtime
> which of these exist: `cv.aruco_ArucoDetector` / `cv.detectMarkers` (API shape
> varies by version), `interpolateCornersCharuco` or `cv.aruco_CharucoDetector`,
> `calibrateCameraCharuco`, and access to rejected candidates. (2) If absent from
> the stock build, document the custom-build route (opencv.js build with
> `aruco,calib3d,imgproc,objdetect` modules; record exact build flags and output
> size). (3) Benchmark: detectMarkers on a 960×540 frame (target ≥10 fps capable)
> and calibrateCameraCharuco with ~20 synthetic frames (target ≤15 s) on this
> machine, in a Web Worker. (4) Measure delivered wasm+js size.
> **Deliverable:** `docs/ai/SPIKE_OPENCVJS.md` recording: API availability matrix,
> chosen version + source (stock vs custom + scripted build steps), benchmark
> numbers, bundle size, and a GO / GO-WITH-CUSTOM-BUILD / NO-GO recommendation.
> **AC:** every U-1/U-2 question in IMPLEMENTATION_BRIDGE.md §1.3 has a measured
> answer. No production code merged from this spike.

---

### Phase M0 — Foundation & quick wins

---

**P-0.1 — F-10: remove DB metrics, freeze pattern persistence** *(1 session)*

> **Objective:** remove the misleading persistence surface per roadmap F-10.
> Delete the `POST /api/calibration/metrics` route
> (`aruco_generator/web/calibration_web.py:1014-1069`) and all `DetectionMetric`
> usage (`aruco_generator/db/models.py`); grep tests and `static/js/core/api.js`
> for references and remove. Pattern storage endpoints
> (`/api/calibration/patterns`, export/import) remain but add a module-level
> comment marking them frozen (no new capabilities).
> **AC:** route returns 404; no `DetectionMetric` imports remain;
> `make validate` green; `AI_NAVIGATION.xml` updated.
> **Testing:** remove/adjust metric tests; add a test asserting 404 on the old
> route (documents intentional removal).

---

**P-0.2 — F-90a: design tokens + dark-first theme base** *(1 session)*

> **Objective:** create `static/css/tokens.css` implementing roadmap §6.2–§6.5
> exactly (color tokens incl. confidence ramp + detection overlay tokens,
> typography scale + `--font-ui`/`--font-data`, spacing scale, radii, elevation),
> with dark as `:root` defaults and a `[data-theme="light"]` override block
> (light values: derive sensible inversions, keep semantic hues). Add a
> `theme.js` toggle persisting via the existing
> `static/js/core/state.js` StateManager. Wire `tokens.css` into
> `templates/base.html` *before* Bootstrap-dependent page CSS so tokens are
> available everywhere; do NOT restyle existing pages yet.
> **AC:** tokens load on every page; theme toggle works and persists; contrast of
> token pairs verified ≥4.5:1 (body) in both themes (include a small script or
> documented check); no visual regression on existing pages beyond background of
> new test page. **Testing:** extend `tests/test_ui_pages.py` smoke to assert the
> stylesheet is served; manual screenshot pass both themes.

---

**P-0.3 — F-90b: AppShell + six-workspace IA cutover** *(2 sessions)*

> **Objective:** implement roadmap §5.1–§5.2. Rewrite `templates/base.html` into
> the C-01 AppShell: 48 px top bar (logo; nav: Generate, Calibrate, Live, Debug,
> Convert, Learn; chip slots — render empty placeholders for now; gear + help
> buttons), content slot, collapsed diagnostics-drawer strip placeholder. Keep
> the existing skip-nav; drop breadcrumbs. Routes (in
> `aruco_generator/web/web.py` + `calibration_web.py`): `/generate` stays;
> `/calibration` → `/calibrate` (301); `/validation` → `/debug` (301);
> `/documentation` → `/learn` (301); add `/live` and `/convert` rendering
> placeholder workspace templates (C-03 three-panel skeleton with a teaching
> empty state per roadmap C-12). Home (`/`) keeps current content for now
> (homepage v2 is M1). Keyboard nav `g`+key per roadmap §2.3 expert
> acceleration. Existing page templates render inside the new shell (Bootstrap
> components inside may look transitional — acceptable; they migrate
> per-workspace later).
> **AC:** six nav items, active state correct; all old URLs 301 to new ones; all
> pages render inside the shell in both themes; keyboard navigation works;
> `tests/test_navigation.py` + `tests/test_ui_pages.py` updated and green
> (including redirect assertions). **PXA:** §17.5 navigation checklist passes.

---

**P-0.4 — F-90c: core component library (C-03, C-09, C-12, C-13, C-14, C-17)**
*(2 sessions)*

> **Objective:** create `static/js/components/` with JSDoc-typed (`// @ts-check`)
> vanilla ES modules implementing roadmap §7 specs for: C-03 WorkspacePanel set
> (+ mode segmented control), C-09 VerdictCard, C-12 Loading/Empty states (all
> four tiers + empty variant), C-13 FixItPanel, C-14 EducationalCallout (with
> persisted dismissal via StateManager), C-17 Toast (max-1-concurrent queue).
> Each component: one file, factory function returning an element, tokens-only
> CSS in a co-located `components.css`, and the a11y requirements from §7
> (roles, aria, focus). Build a hidden `/dev/components` gallery route
> (dev-only, behind `app.debug`) rendering every component in every state — this
> is the visual test surface.
> **AC:** all six components render in the gallery in both themes; toast queue
> drops oldest beyond 1; FixItPanel always renders ≥1 action; C-12 byte-honest
> variant takes a size string; axe-style manual audit notes recorded.
> **Testing:** Node unit tests for logic (toast queue, callout persistence);
> gallery smoke test asserts 200 in debug app.

---

**P-0.5 ∥ — F-03: marker size/distance calculator** *(1 session)*

> **Objective:** implement roadmap §10.3. Create
> `static/js/lib/marker-math.js`: given {resolution_h, hfov_deg, marker_mm,
> dict_bits}, compute px-per-bit at distance, max reliable distance (≥2 px/bit)
> and comfortable distance (≥4 px/bit), plus inverse (distance → required size);
> document formula and assumptions in JSDoc. Surfaces: (1) `/learn/marker-size-
> calculator` page (Learn workspace) with camera presets (1080p/720p/4K + custom)
> and C-20-style results incl. the PX-9 qualifier line; (2) advisor strip on
> Generate: live line under the size field ("At 30 mm … ~1.9 m ⓘ") with a
> "Fix it" action that back-solves size from a target distance.
> **AC (tests):** three hand-computed reference cases assert within 1%
> (document the hand calculations in the test file); strip updates on size input
> < 100 ms; qualifier text present (PX-9); fisheye HFOV > 120° shows the warning.
> **Testing:** Node unit tests for marker-math; UI smoke for both surfaces.

---

**P-0.6 ∥ — F-04: calibration file converter** *(2 sessions)*

> **Objective:** implement roadmap §10.4. Session 1 — fixture corpus + adapters:
> collect real fixture files into `tests/fixtures/calibration_formats/`
> (generate OpenCV YAML via a tiny cv2 script with known values; ROS1/ROS2
> camera_info samples; a kalibr camchain sample; document provenance in a
> README). Build `static/js/vision/formats/` adapters + `detect.js`
> (auto-detection), vendoring js-yaml with a custom schema handling `%YAML:1.0`
> and `!!opencv-matrix`. Node round-trip property tests: for every ordered pair
> of formats, parse→emit→parse equals parse (within float tolerance); K vs P
> matrix semantics preserved per camera_info spec. Session 2 — Convert
> workspace UI: C-08 zone with paste support, auto-detect badge, C-20 preview
> (fx/fy/cx/cy, dist coeffs, resolution, mono right-aligned), C-18 export row,
> inline C-14 explaining P-vs-K. Fully client-side (assert: no network calls in
> the convert flow).
> **AC:** roadmap §10.4 AC1–AC3 + EC rows each covered by a test or explicit UI
> behavior; missing-resolution prompts inline; 5/8/12-coeff inputs all parse.
> **Testing:** Node tests in CI via `make test` extension; UI smoke.

---

**P-0.7 ∥ — F-07a: print-scale ruler on exports** *(1 session)*

> **Objective:** roadmap §10.7 AC1. Add a 100 mm calibrated bar + caption
> ("Verify: this bar must measure exactly 100 mm / 'fit to page' breaks scale")
> to PDF output (`aruco_generator/export/exporters.py` PDFExporter, placed in
> the margin clear of markers) and SVG output (`aruco_generator/core/drawing.py`
> ruler primitive, same placement rule). Assert lbrn2 and DXF outputs contain NO
> ruler geometry (it must never be cut) — add explicit tests. Skip ruler when
> canvas margin < 15 mm (small single markers) rather than overlapping content.
> **AC:** ruler present in PDF+SVG snapshots at exactly 100 mm in document
> units; absent from lbrn2/DXF; small-margin skip works.
> **Testing:** update `tests/test_export_snapshots.py` deliberately; add
> dimension-assert test parsing the SVG ruler path.

---

**P-0.8 ∥ — F-11: ChArUco diamond markers** *(1 session)*

> **Objective:** add diamond generation. In
> `aruco_generator/calibration/calibration.py`, add
> `generate_charuco_diamond(square_mm, marker_mm, ids[4], dictionary)` using
> `cv2.aruco.drawCharucoDiamond` (raise the standard OpenCV-required
> ServiceUnavailable pattern used elsewhere when cv2 absent — see
> `calibrate_camera`'s guard). Route on `calibration_bp`
> (`/api/calibration/charuco_diamond`, mirroring `/api/calibration/charuco`
> validation style at calibration_web.py:633). Generate workspace gains a
> "Diamond" mode segment with the four-ID input and preview/download (SVG/PDF/
> PNG paths consistent with existing patterns).
> **AC:** valid request returns image + metadata incl. checksum (match existing
> `_checksum_image` pattern); invalid IDs (dupes, out-of-range for dict) return
> specific 400 messages per house error style; UI mode renders.
> **Testing:** new tests modeled on `tests/test_charuco.py`.

---

**P-0.9 — F-08: dictionary advisor (after P-0.5)** *(1 session)*

> **Objective:** roadmap §10.8. Precompute per-dictionary inter-marker minimum
> Hamming distances once (small Python script using the existing validator logic
> at `aruco_generator/validation/validation.py:219`; commit results as
> `static/data/dictionary-stats.json` with a regeneration script reference).
> Build `static/js/lib/dictionary-advisor.js`: inputs {count, distance+camera,
> robustness} → ranked recommendations with one-paragraph rationale strings
> (template: capacity check → bits-vs-range via marker-math → Hamming margin).
> UI: "Help me choose" panel in Generate (C-20 + Apply that sets dictionary/size
> fields via the shared form state, PX-8); same module surfaces in Debug ·
> analyzer mode (table of all dicts).
> **AC:** the three roadmap input scenarios produce defensible, explained
> rankings (snapshot the rationale strings in tests); >1000 markers shows the
> honest "not supported yet" path with feedback action; Apply pre-fills
> correctly. **Testing:** Node tests on advisor logic; UI smoke.

---

**P-0.10 — F-09: surface the validation engine in Debug** *(1 session)*

> **Objective:** make the existing server validation visible. In the Debug
> workspace add "Quality report" mode: C-08 upload (with explicit PX-6
> disclosure "This image is sent to the server for analysis" — these endpoints
> are server-side), calling `/api/validation/detect` and
> `/api/validation/verify_quality` (advanced_web.py:524/539), rendering results
> as C-09 VerdictCards: map report fields (quiet_zone, contrast, sharpness,
> bit_errors, corner quality, failure analysis from validation.py:423) to
> three-tier verdicts + dominant-cause line, full numerics in the expansion.
> Keep `templates/validation.html`'s useful pieces; the old page already 301s to
> /debug (P-0.3).
> **AC:** upload → verdict ≤ 4 s p95 locally; every failure mode in
> `_analyze_detection_failure` maps to a C-13 with a concrete action; rate-limit
> 429 renders as friendly C-13 ("wait a minute" + why), not raw error.
> **Testing:** UI smoke with fixture images (good marker / blurry / no quiet
> zone) asserting verdict tiers.

---

**P-0.11 — M0 PXA gate + checkpoint CP-1** *(1 session)*

> **Objective:** run roadmap §17.3 (design) on every M0 screen, §17.4 (feature)
> on F-03/04/07a/08/09/10/11, §17.5 (navigation), §17.6 (accessibility) on the
> shell + Convert + Debug; fix violations found (timebox: fix-in-place if <30
> min each, else file as TODO list in the PR). Produce
> `docs/ai/gates/PXA_GATE_M0.md` recording each checklist item pass/fail/fixed.
> Then update `IMPLEMENTATION_BRIDGE.md` §6 checkpoint CP-1 with actuals
> (sessions spent vs estimate, surprises) and adjust M1 estimates if needed.
> **AC:** gate document committed; `make validate` green; CP-1 notes written.

---

### Phase M1 — Vision platform + Live Validator

---

**P-1.1 — F-00a: opencv-loader + worker skeleton** *(1–2 sessions; requires
P-0.S verdict)*

> **Objective:** per the SPIKE_OPENCVJS.md decision, vendor the chosen
> opencv.js build under `static/vendor/opencv/<version>/` (immutable-cached via
> existing vercel.json rule). Build `static/js/vision/opencv-loader.js`:
> lazy-load only when a camera/debug workspace requests it; integrity hash;
> exposes a wasm-ready promise; reports load progress to a C-12 byte-honest
> loading state ("Loading vision engine (~N MB, cached after first use)").
> Build `static/js/vision/vision.worker.js` with the roadmap §13.2 protocol:
> monotonic frame ids, latest-frame-only backpressure (drop, never queue), a
> `withMats()` helper ensuring `.delete()` in finally, heap-size reporting
> message for the future diagnostics drawer, and a `ping`/`echo` op. Ops in
> this prompt: `detectMarkers(imageBitmap, dict, params?)` returning corners/
> ids/rejected + timings.
> **AC:** loader never runs on Generate/Convert/Learn; echo round-trip works;
> detectMarkers returns correct ids on a canned test image (commit a small
> fixture PNG of a known 4X4_50 id-0 marker, generated by the existing server
> engine for cross-consistency); leak test: 500 sequential detect calls grow
> wasm heap < 10%. **Testing:** Node-side protocol unit tests; browser smoke
> documented as a manual script in the PR.

---

**P-1.2 ∥ — state.js extension + models + status chips (C-02)** *(1 session)*

> **Objective:** extend `static/js/core/state.js` (do not replace): per-
> namespace `schemaVersion` + migration hook, `subscribe(key, cb)`, and typed
> JSDoc shapes in new `static/js/core/models.js` per roadmap §13.4
> (CalibrationProfile, CaptureSession, BoardSpec, MarkerConfig). Implement C-02
> StatusChips in the shell's chip slots: camera chip (absent state for now —
> "No camera" muted) and calibration chip ("No calibration" muted; popover
> listing profiles from the store — empty-state teaching copy). Add the handoff
> helper `static/js/core/handoff.js`: `send(workspace, slice)` →
> store-mediated pre-fill + navigation, used by every later "›" button.
> **AC:** chips render on every workspace; store survives reload with versioned
> namespaces; a demo handoff (Generate "Calibrate with this board ›" button
> appearing when a board mode is active) pre-fills a placeholder on /calibrate
> (PX-8 source-labeled: "from your last generated board · edit").
> **Testing:** Node tests for migrations + subscribe; UI smoke for chip render
> + handoff.

---

**P-1.3 — F-00b: camera-manager + C-04 CameraView + pre-flight checks**
*(2 sessions)*

> **Objective:** `static/js/vision/camera-manager.js` per roadmap §12:
> getUserMedia on explicit action only; device enumeration (re-enumerate after
> permission for labels); negotiated-settings reporting (PX-9 — display actual,
> not requested); per-workspace device/res persistence; mirroring policy
> (display mirrored for user-facing, processing raw); pause/resume on
> visibilitychange with iOS Safari auto-resume; health states feeding the
> camera C-02 chip. C-04 CameraView component: permission primer (§12.1 layout
> incl. PX-6 line + "Upload images instead" first-class path), controls strip
> (§12.2), overlay canvas, the §11.9 pre-flight checklist (permission/stream/
> ≥720p/≥15fps/wasm-ready) rendered as C-13 rows only on failure. Implement the
> §12.5 troubleshooting tree rows that don't require detection (permission
> denied / no devices / black frames / iOS pause).
> **AC:** primer → camera ≤ 2 clicks; denial path shows browser-specific
> recovery + upload exit (PX-4); chip reflects live/degraded/error; processing
> path receives unmirrored frames (test with an asymmetric pattern); settings
> persist per workspace.
> **Testing:** unit tests for state machine; manual matrix doc
> (`docs/ai/CAMERA_TEST_MATRIX.md`): Chrome/Firefox/Safari/Edge on macOS +
> Windows notes + iOS Safari + Android Chrome + one UVC camera, with results
> table to be filled across M1.

---

**P-1.4 — F-02a: Live detection core (overlay, metrics, verdict)** *(2 sessions)*

> **Objective:** the Live workspace detect mode per roadmap §10.2 AC1–AC4.
> Wire C-04 → worker detectMarkers loop (rAF + backpressure; process at ≤960px);
> overlay: corner polygons (`--det-accepted`), id labels (`--det-id-label`),
> per-marker corner jitter (rolling 30-frame std, px), processing fps. C-05
> GuidanceBar + C-06 QualityChip components (build now per roadmap §7 specs —
> they're needed here first): port verdict thresholds from
> `aruco_generator/validation/validation.py` `_calculate_contrast` (line 545),
> `_calculate_sharpness` (559), quiet-zone check (445) into
> `static/js/vision/frame-gates.js` (document any approximation deltas in
> JSDoc, PX-9). Dictionary select + auto-try-all scan mode (cycle dicts ~300 ms
> each, lock on first hit, show locked dict). Pose: when a calibration profile
> exists in the store, solvePnP per marker with user-entered size → axes
> (CV-convention colors) + distance (`--det-measure`); otherwise muted "Load
> calibration for pose ›" referencing the chip (PX-3). Inspector lists detected
> ids/corners as copyable text (§6.10 — a11y + A-6 dual purpose).
> **AC:** roadmap §10.2 AC1–AC4 each demonstrated (AC1 timed ≤5 s on dev
> machine); no-detection-for-5 s triggers the §12.5 detection-troubleshooting
> C-13 incl. "Open this frame in Debug ›" handoff stub (target lands P-3.1 —
> button can deep-link with frame in store now).
> **AC (perf):** UI thread ≥30 fps while processing ≥10 fps at 960px.
> **Testing:** frame-gates Node tests against fixture images shared with the
> Python suite (same files → comparable scores within tolerance).

---

**P-1.5 — F-02b: demo mode + homepage v2 + network-silence test** *(1–2 sessions)*

> **Objective:** (1) Demo mode (Live third segment): renders a large known
> marker on screen (client-side bitmap from dict tables or `/api/preview`) with
> instruction "Point your phone camera at this screen — or open this page on
> your phone and point it at your monitor"; success → C-11 with "Print this
> marker for real ›" handoff to Generate (A-1 loop). (2) Homepage v2 per
> roadmap §5.5: three-step loop hero + PX-6 line, two CTAs, six workspace-card
> bench strip, credibility row; no wasm/camera on homepage (assert). (3) The
> NFR-1 automated test: a Playwright (or equivalent headless) test that runs a
> Live session against a fixture video/canvas stream and asserts zero
> non-static-asset POST/upload requests occur (PX-6 made provable). If
> Playwright is too heavy for CI today, implement as `scripts/privacy_check.py`
> + documented manual run, and file CI integration as a TODO.
> **AC:** demo reaches detection with a phone in informal test; homepage passes
> §17.5 intent-mapping review; privacy assertion runs and passes.
> **Testing:** homepage smoke tests updated; privacy test committed.

---

**P-1.6 — M1 PXA gate + diagnostics drawer (C-16) + CP-2** *(1 session)*

> **Objective:** implement C-16 DiagnosticsDrawer (collapsed vitals strip: proc
> fps · latency · wasm ●; expanded: §5.10 contents incl. wasm heap trend from
> the worker's reporting, network-activity indicator, last error, Expert-mode
> toggle [persisted; only effect so far: reveals raw negotiated camera
> constraints + frame-gate values], copy-diagnostics-report). Then run §17
> checklists across Live + camera flows (esp. §17.6 on C-04/C-05: aria-live
> throttling, keyboard capture); record `docs/ai/gates/PXA_GATE_M1.md`; write
> CP-2 notes (spike-vs-reality on perf, camera matrix findings, M2 estimate
> adjustments).
> **AC:** drawer functional on all camera workspaces; gate doc committed; CP-2
> decision recorded (GO for M2 / adjustments).

---

### Phase M2 — Calibration Studio

---

**P-2.1 ∥ — Python ChArUco reference harness (accuracy ground truth)** *(1–2
sessions; parallel with P-2.2+)*

> **Objective:** turn the dead `calibrate_camera()` into the NFR-5 reference.
> In `aruco_generator/calibration/calibration.py` add
> `calibrate_camera_charuco(images, board_spec)` using cv2's ChArUco pipeline
> (detector + interpolate + calibrateCameraCharuco), returning the same result
> shape as `calibrate_camera` (line 526) plus per-image errors. Create
> `tests/fixtures/calibration_frames/`: capture (or source) a real 15–25 frame
> ChArUco set from one physical camera with a documented board spec; store
> expected K/dist from a cv2 run in a JSON sidecar. Add
> `scripts/calibration_reference_check.py`: given a frames dir + a JSON of
> client-produced results, reports ΔK%, Δdist, ΔRMS (this is the M2 exit
> criterion tool). No new public routes (the product solver is client-side).
> **AC:** harness reproduces its own sidecar within float noise; script
> produces a clear pass/fail at the 1% K threshold; fixture provenance
> documented. **Testing:** pytest covering the new function on the fixture set.

---

**P-2.2 — F-01a: Studio skeleton + upload-path solve** *(2 sessions)*

> **Objective:** /calibrate becomes the C-07 stepper (Board → Capture → Solve →
> Results). Board step: BoardSpec form pre-filled via handoff (P-1.2) with
> source label; [Print board ›] handoff to Generate; FOV-implausibility warning
> (marker-math). Capture step, upload variant first: C-08 multi-file (15–40
> images; per-file resolution-mismatch rejection per roadmap §10.1 AC6) →
> worker ops `interpolateCharuco(frame, boardSpec)` per image → per-image
> corner counts listed (C-19 thumbnails with counts). Solve step: worker
> `calibrateCharuco(cornerSets, boardSpec, imageSize)` with C-12 long-tier
> progress (stage labels, cancellable via worker restart). Results step v1:
> RMS, K/dist as C-20 (mono, copy), per-image error bar list, C-18 export row
> using F-04 adapters (OpenCV YAML / ROS1 / ROS2 / JSON) + Copy Python.
> Validate output against P-2.1: run the fixture frames through the browser
> path (manual or scripted headless), feed results JSON to
> `calibration_reference_check.py`.
> **AC:** fixture set solves in ≤15 s; ΔK < 1% vs Python reference; exports
> round-trip through F-04 tests; roadmap §10.1 AC4+AC6 demonstrably covered.
> **Testing:** worker-op unit tests on canned corner data; reference-check run
> recorded in PR.

---

**P-2.3 — F-01b: webcam capture with gates, quotas, instruction fusion**
*(2–3 sessions)*

> **Objective:** the §11 feedback layer. Extend `frame-gates.js` with the full
> gate set: sharpness (Laplacian variance over board ROI, auto-baselined),
> exposure clipping <2% in ROI, glare blob, visibility ≥60% corners, distance
> buckets (board height 25–50% / 50–80% of frame; reject <15%), tilt buckets
> (L/R/U/D ≥20° from rvec), coverage 3×3 histogram. Implement C-15
> ProgressQuota (grid overlay + pose checklist + frame count; progress never
> regresses visibly) and the §11.7 instruction-fusion priority function
> (stream → quality → visibility → distance → coverage → pose) feeding C-05
> (≥1.5 s display throttle; instructions flipped to match mirrored display per
> §11.3). Auto-capture when gates pass AND frame adds quota value (shutter
> flash 120 ms + optional tick; reduced-motion: counter increment); manual
> capture (`Space`). Capture-session autosave to store after every capture;
> resume prompt on reload (§12.6, labeled). Solve gating per roadmap §10.1 AC2
> with stated-reason disabled button.
> **AC:** roadmap §10.1 AC2 + AC5 (worker isolation, UI ≥30 fps); each gate
> individually demonstrable (test harness: synthetic frames violating one gate
> each — blur, clipped, partial board — assert correct single instruction);
> quota completion auto-advances; resume restores 14-frame session intact.
> **Testing:** gate unit tests on synthetic fixtures; fusion priority unit
> tests; manual capture-flow script in PR.

---

**P-2.4 — F-01c: confidence scoring + results diagnostics** *(2 sessions)*

> **Objective:** §11.8 + C-10. Implement `static/js/vision/confidence.js`:
> factors (resolution-scaled RMS, coverage completeness, pose diversity, frame
> count, per-image consistency w/ outlier flagging, held-out 80/20 re-solve) →
> 0–100 score + tier thresholds (70/90) exported as the single constants
> source. C-10 ConfidenceMeter component per roadmap §7 (hero number, ramp,
> ticks, factor rows each with a working fix-it action that returns to Capture
> with the relevant C-15 dimension highlighted). Results additions: coverage
> heatmap, distortion-grid visualization, C-19 outlier flags with one-click
> "Remove & re-solve" (≤2 clicks total, AC3). Write the Learn methodology page
> (how the score works, held-out rationale, reference-validation claim) and
> link from the meter (PX-9).
> **AC:** roadmap §10.1 AC3; tiers render per §6.8 contract; degrading the
> fixture set (drop edge-coverage frames) measurably drops the coverage factor
> and the score; methodology page live.
> **Testing:** confidence unit tests with constructed factor scenarios;
> held-out split determinism test.

---

**P-2.5 — F-01d: profiles, chip integration, save/export flow** *(1 session)*

> **Objective:** persist results as CalibrationProfile (models.js shape) via
> the store; profile shelf in the calibration C-02 chip popover (load/delete/
> export, age display, stale-recalibrate nudge ≥90 days); saving updates the
> chip visibly (the PX-3 moment); C-11 success confirmation with "Export for
> ROS ›" handoff into Convert pre-filled with the profile (PX-5/PX-8); Live
> pose mode consumes the active profile automatically.
> **AC:** save → chip updates without reload; profile survives reload; Live
> shows pose with the saved profile; Convert opens pre-filled; deleting the
> active profile degrades Live explicitly (PX-3).
> **Testing:** store round-trip tests; cross-workspace smoke (calibrate → live
> → convert chain).

---

**P-2.6 — M2 usability test, PXA gate, CP-3** *(1 session + external test)*

> **Objective:** run the §10.1 AC1 usability test (2 external engineers, printed
> board, ≤7 min to exported YAML, no docs; record where they stall); fix
> top-3 stalls if <1 session total, else file. Run §17 checklists on the Studio
> end-to-end (esp. §17.7 consistency: verdict tiers, chip truthfulness, handoff
> graph). Produce `docs/ai/gates/PXA_GATE_M2.md` + CP-3 notes (launch
> readiness; Show-HN go/no-go; M3 adjustments).
> **AC:** AC1 pass (or failures fixed + retested); gate doc committed; CP-3
> decision recorded.

---

### Phase M3 — Debug & integrate

---

**P-3.1 — F-05: Detector Parameter Playground** *(2–3 sessions)*

> **Objective:** roadmap §10.5. Debug · Playground mode: image via C-08 /
> webcam still (camera-manager) / handoff frame from Live (P-1.4 stored it).
> NEW `static/js/lib/detector-params.js`: full DetectorParameters schema —
> groups (Thresholding / Contour filtering / Corner refinement / Bit
> extraction), per-param {default, range, step, plain-language tooltip}.
> Worker op `detectWithParams` returns accepted + `rejectedImgPoints`. Overlay:
> accepted solid `--det-accepted`, rejected dashed `--det-rejected` with
> hover stage-tags from a staged re-run attribution (perimeter/approx/bits —
> label "heuristic" per PX-9). Re-detect <300 ms at ≤960px (debounce sliders
> 100 ms); 2 s worker timeout → auto-revert + C-17. Diff-from-default badges +
> per-group reset. C-18 export: runnable Python (cv2), C++, aruco_ros YAML with
> assumption-header comments. "Apply to Live ›" handoff stores params for the
> Live loop.
> **AC:** roadmap §10.5 AC1–AC4 + all EC rows; an intentionally hard fixture
> (small blurry marker) becomes detectable by a documented parameter change —
> include as a guided example in the empty state.
> **Testing:** params-schema unit tests; timing assertion in a perf note;
> export snippets compile/run (Python one executed in CI against a fixture —
> pattern shared with P-3.2).

---

**P-3.2 ∥ — F-06: Runtime Config Exporter + emitted-code execution tests**
*(2 sessions)*

> **Objective:** roadmap §10.6. NEW `aruco_generator/export/runtime_configs.py`:
> serializers — aruco_ros marker/board config, apriltag_ros tags.yaml (handle
> 16h5-vs-tag16h5 naming per consumer), generic JSON board geometry (object
> points per id from existing board generators); Jinja snippet templates —
> Python (cv2) detection script bound to exact dict/size/params and optional
> embedded CalibrationProfile. Routes on `advanced_bp`
> (`/api/export/runtime_config?format=`). Convert workspace · "Runtime configs"
> mode: pick source (current board via handoff / paste spec), C-20 preview,
> C-18 row. **The flagship QA pattern:** `tests/test_runtime_configs.py`
> renders the same board to an image via the existing generator, writes the
> emitted Python snippet to a temp file, executes it in a subprocess against
> the rendered image, asserts detection of expected ids — for ≥3 board types.
> **AC:** roadmap §10.6 AC1–AC2 + ECs; ChArUco dual-interpretation documented
> via C-14. **Testing:** execution tests in CI (`make test` integration tier);
> golden-file tests for each emitted format.

---

**P-3.3 — F-12: nested landing-pad designer** *(2 sessions)*

> **Objective:** roadmap §10.9. NEW `aruco_generator/core/landing_pad.py`:
> nested layout (outer marker; inner marker in a white cell / center cutout;
> distinct ids; geometry math documented). Generate · "Landing pad" mode as a
> small C-07 flow: configure → coverage chart (marker-math altitude envelopes
> per marker, overlap highlighted, gap warning naming the altitude band, PX-2)
> → export. Exports: tiled multi-page PDF (`exporters.py`: ≥10 mm overlap +
> alignment marks + assembly C-14 note), SVG, lbrn2, DXF (ruler rules from
> P-0.7 apply); PX4/ArduPilot precision-landing snippet via P-3.2 templates
> (both ids + sizes). Inner-marker fabricability warning vs printer DPI/laser
> kerf with [Resize] action.
> **AC:** roadmap §10.9 AC1–AC2 + ECs; lbrn2 of a nested pad opens correctly
> (manual LightBurn check noted in PR); altitude chart matches marker-math unit
> values. **Testing:** geometry unit tests; export snapshots; tiling
> page-count/overlap tests.

---

**P-3.4 — F-07b: print verification via webcam** *(1–2 sessions)*

> **Objective:** roadmap §10.7 AC2. Live · "Verify print" mode: nominal-size
> input (pre-filled from last generated MarkerConfig, PX-8); with active
> profile → absolute measure via solvePnP-scaled geometry; without → ratio
> check against the printed F-07a ruler bar detected in-frame (explicit mode
> label per PX-3). Frontality gate (reject >20° with C-05 guidance);
> flatness check via corner planarity ("Flatten the sheet"). Verdict via C-10
> (±1% tolerance) + C-11 on pass with "Get runtime config ›" handoff.
> **AC:** known-good print measures within ±1% on dev hardware; oblique/curved
> cases produce the specified guidance, not wrong numbers (PX-9: refuse to
> measure rather than mis-measure).
> **Testing:** measurement math unit tests with synthetic geometry; manual
> verification script.

---

**P-3.5 — M3 PXA gate + launch checklist + CP-4** *(1–2 sessions)*

> **Objective:** full §17 sweep across all workspaces (esp. §17.7: handoff
> graph edges all functional — walk Generate→Live→Calibrate→Convert and
> Live→Debug→Live end-to-end); `docs/ai/gates/PXA_GATE_M3.md`. Execute roadmap
> M3 launch checklist: demo videos (Live, Studio, Playground), Show HN +
> r/robotics + r/computervision drafts, 3 SEO articles in Learn (size guide /
> P-vs-K explainer / "marker not detecting" → playground), privacy-friendly
> analytics wired to §16.5 metrics (events: core actions, handoff CTR,
> calibration funnel), C-16 feedback link. CP-4: review real usage data
> framework; Phase-3 (F-13/16/15/17) decision matrix prepared for the founder.
> **AC:** gate doc + launch artifacts committed; analytics events verified
> firing; CP-4 document with the Phase-3 recommendation.

---

## 5. UX Alignment per Phase

- **Pre/M0** — *From "five disconnected pages" to "one bench."* The IA cutover +
  shell + tokens deliver PX-3's substrate (chips have a home), PX-7's container
  (modes/accordions exist), and the first PX-5 handoff. User outcome: a visitor
  can finally *see* the product's shape; the calculator/converter/advisor turn
  two daily frustrations (sizing, format translation) into 30-second tasks with
  PX-9-qualified answers. F-10 is UX too: removing a lying surface is honesty
  (PX-9) expressed in code deletion.
- **M1** — *The first magic moment.* Live detection closes the loop the product
  has never closed (generate → verify) and operationalizes PX-1/2/4/6/10 in one
  screen: a single instruction, a verdict not a number, a fix-it on every
  failure, a privacy line that is provably true, and latency budgets enforced
  by architecture (worker isolation). Demo mode gives A-1 a success with zero
  printing — the activation metric's main lever.
- **M2** — *Justified confidence as a product.* The Studio is where PX-11's
  contract (score → tier → factors → fix-it) becomes the differentiator no
  competitor has: the user doesn't just get intrinsics, they get *reasons* —
  and the reference harness (P-2.1) makes the trust claim auditable (PX-9).
  Profiles + chips make the bench remember (PX-3/PX-8), converting one-time
  calibrators into A-7 returners.
- **M3** — *From tool to instrument set.* The playground turns the community's
  most-asked debugging question into a visual answer (PX-2 applied to rejected
  candidates); runtime configs end the journey inside the user's own repo
  (PX-5's final edge); print verification completes the physical-trust story
  started by the M0 ruler. Each M3 feature is the downstream handoff target
  earlier phases promised — shipping them makes earlier success states honest.

---

## 6. Delivery Plan: Complexity, Risk, Unknowns, Checkpoints

### 6.1 Complexity & risk per phase

| Phase | Sessions (est) | Complexity | Top risks | Mitigations in plan |
|---|---|---|---|---|
| Pre | 1–2 (+1 spike) | Low | Spike reveals NO-GO on stock wasm | Custom-build route documented in P-0.S; decision before M1 spends |
| M0 | 14–16 | Medium (breadth, not depth) | IA cutover breaks tests/SEO; YAML parsing quirks | Redirect tests in P-0.3; fixture-corpus-first in P-0.6 |
| M1 | 12–14 | **High** (new platform, browser variance) | Camera API fragmentation; wasm perf on low-end | Test-matrix doc (P-1.3); perf budgets as ACs; upload path as universal exit |
| M2 | 14–16 | **High** (accuracy + UX both) | Solver accuracy disputes; capture-UX overwhelm | Reference harness before UI (P-2.1→P-2.2); PX-1 fusion + external usability test (P-2.6) |
| M3 | 10–12 | Medium | Attribution heuristics overpromise; snippet matrix creep | "Heuristic" labeling (PX-9); formats constrained to 3 at launch |

Estimate honesty (PX-9 applied to ourselves): totals (~55–62 sessions) exceed the
roadmap's 90-day sketch if sessions average <0.7/day. Levers, in preference
order: defer F-12 and/or F-07b to a fast-follow (saves 3–4); ship M1 without
demo-mode polish (1); reduce M0 component gallery scope (1). Do **not** cut
P-2.1 (accuracy reference), P-0.S (spike), or the PXA gates — they are the
cheapest insurance in the plan.

### 6.2 Unknowns requiring investigation (tracked)

| ID | Unknown | Resolved by | Blocking |
|---|---|---|---|
| U-1 | aruco/charuco APIs in stock opencv.js | P-0.S | M1+ |
| U-2 | wasm calibrateCameraCharuco perf | P-0.S (bench) → P-2.2 (real) | M2 |
| U-3 | Browser/camera matrix behavior | P-1.3 matrix doc, filled through M1 | M1 polish |
| U-4 | js-yaml + `!!opencv-matrix` | P-0.6 session 1 | F-04 only |
| U-5 | JS-vs-Python verdict-threshold parity | P-1.4 shared fixtures | F-02 verdict trust |
| U-6 | Headless CI for browser tests (Playwright?) | P-1.5 decision | NFR-1 automation |

### 6.3 Checkpoints (stop, review, adjust — do not skip)

- **CP-1 (end M0, P-0.11):** Actual vs estimated velocity; component-library
  ergonomics verdict (are agents composing C-nn smoothly? if not, fix the
  library before M1 multiplies the pain); SEO indexing of calculator/converter
  begun?
- **CP-2 (end M1, P-1.6):** Wasm perf reality vs budgets; camera matrix
  findings → adjust M2 capture defaults; Live activation signal (if demo mode
  flops with real users, M2 marketing assumptions change). **Gate:** M2 starts
  only on GO.
- **CP-3 (end M2, P-2.6):** Usability AC1 result; reference-accuracy result
  (ΔK); Show-HN go/no-go; decide F-12/F-07b deferral per 6.1 levers.
- **CP-4 (end M3, P-3.5):** 30 days of §16.5 metrics → Phase-3 selection
  (stereo vs PWA vs CLI vs share-URLs) with real data; roadmap v3 → v3.1
  revision pass (the roadmap document itself gets updated with learnings — it
  is a living spec, §17.1 keeps it enforceable only if it stays true).

---

*End of bridge. The roadmap says where and why; this document says how and in
what order. When they disagree, the roadmap wins on intent, this document wins
on sequence — and the conflict gets fixed in whichever document was wrong, in
the same PR that discovered it.*
