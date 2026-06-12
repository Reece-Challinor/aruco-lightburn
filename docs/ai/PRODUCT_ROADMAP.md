<!--
<ai_agent_documentation>
  <file_meta>
    <name>PRODUCT_ROADMAP.md</name>
    <version>3.0.0</version>
    <type>unified_product_specification</type>
    <purpose>Single source of truth: UX strategy + product design specification + implementation roadmap + engineering plan + BRD. A Claude coding agent reading only this document understands why the product behaves as it does, what to build, in what order, how success is measured, and under what constraints.</purpose>
    <last_updated>2026-06-12</last_updated>
    <maintainer>Solo founder + Claude Code</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# ArUco Toolbox — Unified Product Specification
## Roadmap · Product Experience Architecture · Business Requirements

**Status:** Approved planning baseline v3 (unified) · **Audience:** Solo founder + AI coding agents · **Horizon:** 90 days + strategic outlook

---

## 0. How to Use This Document (AI Session Protocol)

This document is both the UX strategy and the engineering roadmap. It uses four ID
systems; **every future feature, PR, and design decision must cite them.** They are
the shared vocabulary that keeps hundreds of independent agent sessions building one
coherent product instead of forty standalone tools.

| ID system | Meaning | Defined in |
|---|---|---|
| `PX-n` | Experience first principles (binding rules) | §2.2 |
| `A-n` | User archetypes and their experience loops | §4 |
| `C-nn` | Universal components (the only UI building blocks) | §7 |
| `F-nn` | Roadmap features | §9 |

**Session protocol.** Before implementing any feature:
1. Read the §2.2 principles and §17 checklists.
2. Find the feature's full specification (§10) and its PXA mapping row (§9.5).
3. Build UI only from §7 components — if a needed component doesn't exist, extend §7
   first (update this document in the same PR).
4. The §17 conformance rule is part of Definition of Done.

**Standing assumptions (explicit):**

- **A1 — Solo founder, AI-agent dev team.** Estimates are in *agent-sessions* (one
  focused Claude Code session ≈ half a founder-day including review). Anything > 10
  sessions must be split into independently shippable milestones.
- **A2 — Vercel serverless stays.** No long-running server compute. Heavy interactive
  CV work (webcam, calibration solve, detection) moves **client-side via OpenCV.js
  (WASM)**. Flask remains for generation/export (reportlab, ezdxf, lbrn2).
- **A3 — No accounts, no uploads-by-default.** Privacy is a feature: camera frames
  and calibration images never leave the browser. This is simultaneously a marketing
  claim, an architecture constraint, a cost-control measure, and (per PX-6) the
  product's cheapest trust mechanism.
- **A4 — Niche is fiducial markers + camera calibration**, not general CV. We compete
  with chev.me/arucogen, calib.io's pattern generator, and "clone kalibr and suffer" —
  not with Roboflow, CVAT, or FiftyOne.
- **A5 — Revenue is out of scope for 90 days.** The goal is daily-use adoption and
  defensible utility. (Obvious future paths: laser-cut marker fulfillment, pro
  calibration reports, API keys. Spec'd as F-21, not designed here.)

---

## 1. Executive Summary

### 1.1 Current state

The product (v2.4.0) is a **marker fabrication tool**: best-in-class at generating
ArUco/ChArUco/AprilTag patterns and exporting them in physically accurate,
manufacturable formats — uniquely including LightBurn `.lbrn2` for laser cutting,
plus SVG/PDF/DXF/STL/OpenCV-YAML/ROS. The codebase is clean, tested,
blueprint-structured, and deploys to Vercel.

### 1.2 Key strengths already built

1. **Fabrication moat.** No competitor produces laser-ready, dimensionally accurate
   marker files. `aruco_generator/export/lightburn.py` + DXF export is the product's
   unique asset.
2. **Generation breadth.** All 16 ArUco dictionaries, ChArUco boards, ArUco grid
   boards, AprilTags/grids (`aruco_generator/calibration/calibration.py`), with an
   OpenCV-optional fallback.
3. **A sophisticated but buried validation engine.**
   `aruco_generator/validation/validation.py` already does detection, quiet-zone
   checks, contrast/sharpness scoring, bit-error counting, failure analysis, and
   synthetic multi-scale test patterns. Most of it has no UI.
4. **Half-built calibration.** `calibrate_camera()` at
   `aruco_generator/calibration/calibration.py:526` computes intrinsics + reprojection
   error — and is unreachable from any route.
5. **Solid engineering hygiene.** App factory, rate limiting, observability, snapshot
   tests, `make validate` gate — AI agents can ship here safely. This is the most
   important asset for AI-driven development velocity.

### 1.3 Major gaps

The engineer's loop is **generate → fabricate → verify print → calibrate camera →
detect → tune → integrate → debug**. The product covers steps 1–2 deeply and abandons
the user afterward. Specifically missing: any webcam experience, any exposed
calibration flow, any detector-tuning tool, any pose/distance math, any calibration
file conversion, any print verification. The DB metrics persistence
(`aruco_generator/web/calibration_web.py:1014`) is dead weight.

And — the gap this unified document exists to close — **no experience system**: the
current app is a set of disconnected pages, which is exactly what every competitor
is. Features alone won't differentiate; competitors can copy a calculator. They
cannot easily copy a coherent experience.

### 1.4 Vision

> **The browser workbench robotics engineers keep open during integration week.**
> Print a marker, point your webcam at it, watch it detect live, calibrate your
> camera in five minutes with feedback that tells you *why* the calibration is good
> or bad, convert the result to ROS `camera_info`, copy the runtime config — without
> installing anything, without a single image leaving the machine, and **without
> ever wondering what to do next.**

Two foundational bets, equal in rank:

1. **Engineering bet:** OpenCV.js client-side compute (`vision-core/`, F-00) — fits
   Vercel (A2), enables privacy (A3), costs nothing per user, and turns five roadmap
   features (live detection, calibration studio, parameter playground, print
   verification, confidence scoring) into one shared platform investment (§13).
2. **Experience bet:** the Product Experience Architecture (§2–§7) — a single
   experience system (principles, archetypes, IA, design system, components) that
   every feature plugs into, making the product feel like one instrument rather than
   a drawer of utilities. **This is the primary competitive advantage.** The marker
   niche is full of tools that work; it has zero tools that feel engineered.

---

## 2. Product Experience Architecture (PXA)

This section governs everything below it. No feature ships unless it conforms.

### 2.1 Product experience vision

The product should feel like a **precision instrument on a clean workbench** — closer
to a good oscilloscope than to a SaaS dashboard. An instrument: shows its state on
its face at all times; gives one reading at a time, confidently; has a calibrated,
trustworthy relationship with physical reality; rewards expertise without demanding
it; and never makes you wonder whether it's working.

The emotional target, in order: **trust → relief → momentum.** Trust ("this tool is
correct and honest"), relief ("this used to take a day with kalibr"), momentum ("it
already set up my next step"). Every design decision is tested against these three.

The experience metaphor for the mental model (§5.9): **stations on a workbench.** You
move work *between stations* (Generate → Live → Calibrate → Debug → Convert); the
work itself — your board, your camera, your calibration — travels with you and is
always visible on the bench (status chips, C-02).

### 2.2 UX first principles (PX-1 … PX-12)

Each principle states **why it exists**, **how it affects implementation**, and **the
conformance rule** future features must satisfy. These are binding; deviations
require a written exception in the PR description.

---

**PX-1 — One instruction at a time.**
*Why:* Camera/calibration setup fails when users face simultaneous demands ("tilt,
also move closer, also fix lighting"). Industry pain research (kalibr/OpenCV flows)
shows abandoned setups come from instruction overload, not difficulty.
*Implementation:* Every guided flow has exactly one active instruction, rendered in
the GuidanceBar (C-05). Multiple deficiencies are *prioritized internally*
(instruction fusion, §11.7) and surfaced serially. Checklists may show overall
progress, but the imperative voice ("Move the board to the right edge") appears in
one place only.
*Conformance:* A feature with live guidance must implement an instruction-priority
function and render via C-05. PRs adding a second simultaneous imperative are
rejected.

**PX-2 — Verdict first, numbers behind.**
*Why:* "RMS 0.42 px" is meaningless to 70% of the audience and *insufficient* to the
other 30%. Both groups are served by layering: plain-language verdict on top, full
numerics one gesture away.
*Implementation:* Every analytical output renders as a VerdictCard (C-09): tiered
verdict ("Production-ready") + one-sentence dominant cause + expandable numerics.
Raw values are never the headline outside Expert mode.
*Conformance:* Any feature producing a quality/accuracy/confidence result must define
its verdict tiers, thresholds, and dominant-cause strings in its spec before
implementation.

**PX-3 — State lives on the bench, not in your head.**
*Why:* Desktop CV tooling's chronic failure: invisible state (which camera? which
intrinsics? which board spec?) causes silent wrong results.
*Implementation:* Cross-workspace state (active camera, active calibration profile,
active board spec) is rendered permanently as StatusChips (C-02) in the app bar, in
every workspace, with health indication. Any workspace consuming that state
references the chip, never a buried setting.
*Conformance:* A feature that reads cross-workspace state must visibly indicate which
state it is using and degrade explicitly ("No calibration loaded — pose disabled,
[Calibrate]") rather than silently changing behavior.

**PX-4 — Never dead-end.**
*Why:* Error screens without exits are where single-visit users are created.
*Implementation:* Every error, empty, and failure state is a FixItPanel (C-13): what
happened (plain language) + why (one sentence) + 1–3 ranked actions, at least one of
which is always available (e.g., "Upload images instead", "Open in Debug"). The
§12.5 troubleshooting tree enumerates camera dead-ends; every feature spec must
enumerate its own.
*Conformance:* Feature specs must include an edge-case table where every row ends in
a user action, not a message. "Show error toast" alone is non-conforming.

**PX-5 — The loop is the product.**
*Why:* Retention comes from workflow continuity, not feature count. A user who
generates a marker and leaves was served a commodity; a user who generates →
verifies → calibrates was served a system.
*Implementation:* Every success state (C-11) includes exactly one primary
**next-step handoff** carrying full context (PX-8): Generate → "Verify live",
Live → "Calibrate this camera", Calibrate → "Export for ROS", Debug → "Apply to
Live". Handoffs are buttons that move work between stations, never bare links to
empty pages.
*Conformance:* Every feature spec declares its upstream handoffs (what arrives
pre-filled) and downstream handoff (the one next step it offers). A feature with no
loop position doesn't ship (§17 rule 2).

**PX-6 — Local-first trust, stated and provable.**
*Why:* The audience includes engineers contractually barred from uploading imagery.
Privacy here is not a policy page; it is a product capability and the cheapest trust
signal available.
*Implementation:* The line "Processed locally in your browser — nothing is uploaded"
appears at every camera/upload touchpoint (C-04, C-08), with a "How this works" link.
CI asserts network silence during camera sessions (NFR-1). Diagnostics drawer (C-16)
shows live network activity = none.
*Conformance:* Any feature touching user imagery must process client-side or, if
server-side is unavoidable (legacy upload validation), label it explicitly *before*
upload: "This image is sent to the server for analysis."

**PX-7 — Three-layer disclosure: Guided / Detailed / Expert.**
*Why:* The same screen must serve a student and a JPL-grade calibration engineer.
Forking the product (a "simple mode") fails both; layering serves both.
*Implementation:* Layer 1 (default): verdicts, single instructions, sane defaults,
zero jargon. Layer 2 (one gesture: expand a C-09 card, open an accordion): full
numerics, per-item breakdowns, methodology notes. Layer 3 (Expert mode, global
toggle, persisted): raw parameters, thresholds editable, JSON state, model selection,
API previews. Expert mode *adds* density; it never relocates Layer-1 functions.
*Conformance:* Every feature spec assigns each piece of information to a layer. New
settings default to Layer 3 unless argued otherwise — the default surface only grows
by exception.

**PX-8 — Respect prior context; never ask twice.**
*Why:* Re-entering a board spec three times (generate, calibrate, debug) is the kind
of friction engineers silently rage-quit over.
*Implementation:* Shared state objects (BoardSpec, MarkerConfig, CalibrationProfile —
§13.4) are the single source of truth; handoffs (PX-5) copy slices of state;
workspaces restore their last state from localStorage on return; capture sessions
auto-resume (§12.6).
*Conformance:* If a feature's form contains a field whose value plausibly exists in
shared state, it must pre-fill from it and indicate the source ("from your last
generated board · edit").

**PX-9 — Honest by default.**
*Why:* This audience detects overclaiming instantly, and trust, once lost to one
wrong number, never returns. Honesty is also differentiation: competitors' tools
state results without assumptions.
*Implementation:* Every computed claim carries its assumptions inline at Layer 2:
calculator results state "assumes ideal focus/lighting; halve for harsh conditions";
confidence scores link their methodology; heuristics are labeled heuristic (F-05
rejection-stage attribution); tolerances are explicit (±1% print verification).
*Conformance:* Specs must include a "stated assumptions" list for every computed
output. Unqualified precision ("detection range: 4.27 m") is non-conforming;
qualified precision ("~4.3 m under good conditions ⓘ") is the house style.

**PX-10 — Latency budgets are UX requirements.**
*Why:* An instrument that lags feels broken; feedback loops only teach when they feel
causal.
*Implementation:* Input echo < 100 ms; parameter-change → recompute < 300 ms (F-05);
camera start → first overlay < 5 s; any operation > 1 s shows determinate progress
(C-15); any operation > 5 s is cancellable. Tiered LoadingStates (C-12) distinguish
"instant-ish" (skeleton), "working" (progress + label), "long" (progress + label +
cancel + time honesty: "~10 s").
*Conformance:* Every feature spec declares its latency tier per interaction; budgets
appear as acceptance criteria and are measured in the diagnostics drawer.

**PX-11 — Confidence is a first-class output.**
*Why:* The core industry pain ("is this calibration good? is this detection
reliable?") is an *epistemic* problem. The product's deepest value is converting raw
CV output into justified confidence.
*Implementation:* A single ConfidenceMeter component (C-10) and a single semantic
color ramp (§6.2, reserved exclusively for confidence) render all confidence:
calibration confidence (§11.8), detection reliability (F-02 verdicts), print
accuracy (F-07), advisor certainty (F-08). Same visual = same meaning everywhere.
Every confidence score decomposes into named contributing factors on expansion
(PX-2) and every factor maps to an actionable improvement (PX-4).
*Conformance:* Features expressing certainty must use C-10 + the confidence ramp; ad
hoc stars/percentages/colored dots are non-conforming.

**PX-12 — Teach in the work, not beside it.**
*Why:* The audience won't read docs, but they will absorb one sentence at the moment
of relevance. Learnability is retention: users return to tools that made them
smarter.
*Implementation:* EducationalCallouts (C-14): one to two sentences of *why*, placed
at decision points ("Tilted views decouple focal length from distance — that's why
we require them"), dismissible per-callout, never modal, never blocking. The Learn
section holds long-form; callouts deep-link into it.
*Conformance:* Each guided flow includes ≥ 1 and ≤ 4 callouts; any rule the UI
enforces on the user (quota, gate, rejection) must have a callout or tooltip
explaining the *reason*, not just the requirement.

### 2.3 Experience strategies (how the principles operationalize)

Each strategy names its mechanisms and the principles it serves. Future features pick
mechanisms from this menu rather than inventing new ones.

**Cognitive load reduction** *(serves PX-1, PX-2, PX-7).* Mechanisms: single-
instruction fusion (C-05); verdict layering (C-09); choice reduction via smart
defaults + presets (every form ships with a defensible default and a "why this
default" tooltip); progressive forms (advanced fields collapsed); one primary action
per workspace (§5.4); recognition over recall (recently-used boards/profiles surfaced
as picks, not searches). Hard rule: a first-run user on any workspace faces ≤ 5
visible decisions before the primary action is available.

**Progressive disclosure** *(PX-7).* The three layers are implemented by exactly
three mechanisms — expandable C-09 cards, collapsed "Advanced" accordions, and the
global Expert toggle — so disclosure always *feels* identical. Anti-pattern ban:
disclosure must never hide the existence of a capability (collapsed ≠
undiscoverable; accordions show labels), per §5.8 discoverability.

**Expert-user acceleration** *(PX-7, PX-10).* Mechanisms: Expert mode (raw
DetectorParameters everywhere, gate-threshold editing, model selection, JSON state
view/edit, API request preview "this UI action = this curl"); keyboard map (global:
`g` then workspace key for navigation, `Space` manual capture, `E` expert toggle,
`.` opens diagnostics — documented in `?` overlay); copy-as-code on every result
(every exportable object offers "Copy Python"); URL state sharing (F-17). Experts
are also the community amplifiers — acceleration features are marketing.

**Learnability** *(PX-12, PX-9).* Mechanisms: educational callouts at decision
points; "why" tooltips on every enforced rule; empty states that teach (C-12 empty
variant shows what the tool does + sample data button: "Try with a sample image");
the Learn section as the canonical home of methodology (calculator math, confidence
scoring methodology, calibration theory) — which doubles as the SEO surface; first
detection / first calibration moments celebrated with a one-time "what just
happened" explainer (dismissed forever after).

**Error recovery philosophy** *(PX-4, PX-8).* Three commitments: (1) **No lost
work** — capture sessions, form state, and profiles persist to localStorage
continuously; worker crashes and device unplugs recover with data intact (§12.6);
(2) **Diagnose, don't describe** — error surfaces name the probable cause ranked by
likelihood, not the exception ("All frames rejected as blurry — clean the lens, add
light, or lock focus" not "Frame quality check failed"); (3) **Always a lateral
exit** — every blocked path offers an alternative route to the goal (camera fails →
upload; detection fails → Debug playground with this exact frame).

**Trust-building mechanisms** *(PX-6, PX-9, PX-11).* Layered: *architectural* (local
processing + CI-asserted network silence); *epistemic* (methodology pages, stated
assumptions, reference cross-validation against OpenCV Python published in Learn);
*behavioral* (deterministic results, visible versioning of OpenCV.js in diagnostics,
golden-file-tested exports); *social* (later: community links, "used by" — out of
90-day scope). Trust compounds across features because confidence visuals are
uniform (PX-11).

**Feedback systems** *(PX-10, PX-1).* Taxonomy with fixed channels: *ambient*
(status chips C-02 — continuous, glanceable); *guidance* (C-05 — imperative,
serial); *evaluative* (quality chips C-06 and verdicts C-09 — judgmental, tiered);
*event* (toasts C-17 — transient, max 1 concurrent, never for information the user
must act on); *celebration* (success confirmations C-11 — used sparingly: first
detection, completed calibration, verified print). A given message type always uses
the same channel.

**User confidence systems** *(PX-11).* The product's signature. Confidence is
always: (a) scored on one 0–100 scale, (b) tiered into exactly three verdict bands
(Production-ready ≥ 90 / Usable 70–89 / Recapture-or-fix < 70 — bands may rename per
domain but never renumber), (c) decomposed into factors, (d) paired with the single
highest-leverage improvement action. This four-part contract is identical for
calibration, detection, and print verification — learn it once, trust it everywhere.

**Visibility of system status** *(PX-3, PX-10).* Always-on: status chips (camera
health, calibration profile, board spec context); per-workspace ambient indicators
(processing FPS during camera work, worker/wasm readiness); diagnostics drawer
(C-16) as the full-depth status surface. Rule: any background process that can
affect results (frame dropping, auto-downscaling, fallback paths) must surface its
status — silent degradation is the cardinal instrument sin.

**Context preservation** *(PX-8).* State architecture (§13.3–13.4) exists primarily
to serve this strategy: schema-versioned, JSON-serializable workspace state enabling
persistence, restoration, handoffs, sharing, and expert editing — five UX features
from one engineering pattern.

**Workflow continuity** *(PX-5).* The handoff graph is closed and explicit:

```
Generate ──verify live──▶ Live ──this camera──▶ Calibrate ──export──▶ Convert
   │                       │  ▲                     │
   └──calibrate w/ board──▶│  └──apply params───────┤
                           ▼                        ▼
                         Debug ◀──open this frame── (any camera view)
                           └──runtime config──▶ Convert/Export
```

Every node's success state points along an edge (PX-5). No workspace is a leaf.

---

## 3. Current Capability Assessment

### 3.1 Functional inventory

| Area | Capability | Surface | Quality |
|---|---|---|---|
| Generation | ArUco markers, 16 dicts (4×4→7×7, 50→1000), OpenCV + pure-Python fallback | UI + API | Strong |
| Generation | ChArUco boards, ArUco grid boards | UI + API | Strong |
| Generation | AprilTags + grids (16h5/25h9/36h10/36h11) | UI + API | Strong |
| Generation | Batch/grid generation, 4 presets (drone landing, inventory, calibration, business card) | UI + API | Good |
| Export | LightBurn .lbrn2, SVG, PDF, DXF, STL | UI + API | Strong (moat) |
| Export | OpenCV YAML, ROS format (pattern metadata) | API | Adequate |
| Validation | Upload-image detection, quality report (quiet zone, contrast, sharpness, bit errors, corner quality), Hamming, failure analysis | API mostly; thin UI | Engine strong, surface weak |
| Validation | Synthetic test patterns (multi-scale, distortion, occlusion) | API | Good, undiscovered |
| Calibration | `calibrate_camera()` (checkerboard, subpixel refinement, reprojection error) | **None — dead code** | Incomplete (no ChArUco) |
| Persistence | Pattern storage, detection metrics (Postgres/SQLite) | API | Low value, cut (F-10) |
| Infra | Health, observability, rate limiting, CSP, tests | — | Strong |

### 3.2 What is working well

- The generate→export path: parameter form → live SVG preview → download in 7
  formats.
- Engineering infrastructure: an AI agent can modify code and `make validate`
  catches regressions.

### 3.3 Incomplete user workflows

1. **"Did my print work?"** — User downloads a PDF, prints it, and has no way to
   check scale accuracy or detectability without writing Python.
2. **"Calibrate my camera"** — The app generates calibration boards but cannot
   consume the photos the user takes of them. The core promise of a "calibration"
   page is unfulfilled.
3. **"Why isn't my marker detecting?"** — The validation engine could answer this;
   the UI gives no path into it from the generate flow.
4. **"Give me the config for my robot"** — ROS export emits pattern metadata, not
   the `camera_info` YAML or `aruco_ros`-shaped board config an engineer actually
   pastes into a launch file.

### 3.4 Technical limitations

- **No client-side CV.** Everything round-trips to Flask; webcam workflows are
  impossible without OpenCV.js.
- **Serverless statelessness** makes the DB-backed pattern/metrics features
  unreliable and pointless in production (in-memory SQLite resets per invocation).
- **`calibrate_camera()` is checkerboard-only**; ChArUco (which the app generates!)
  is the modern standard and tolerates partial views.
- **Rate limits (15/min) on validation endpoints** would strangle any interactive
  tuning loop — another argument for client-side compute.

### 3.5 UX limitations (the PXA audit)

| PXA element | Current state |
|---|---|
| PX-1 single instruction | No guided flows exist at all |
| PX-2 verdicts | Raw JSON-ish outputs; no verdict layer |
| PX-3 visible state | No cross-page state, no chips; pages are amnesiac |
| PX-4 dead-ends | Validation failures return messages without actions |
| PX-5 loop | Zero handoffs; every page is a leaf — the core IA failure |
| PX-6 trust | No privacy claims (nothing client-side yet to claim) |
| PX-7 layers | One flat layer; no expert mode, no disclosure system |
| PX-8 context | Board specs re-entered per page; no shared state |
| IA (§5) | 5 pages ≈ wrong cut: pattern creation split across Generate + Calibration pages |
| Design system (§6) | Bootstrap defaults; no tokens; light-only |
| Components (§7) | Page-specific JS (`static/js/pages/*`), no shared components |

Additional concrete frictions: navigation is page-based with no shared state (a
board generated on one page can't be "sent" to validation); no persistent user
context (no saved calibration profile, no recent configs); validation requires file
uploads with no live camera option; no status feedback layer.

Conclusion: the experience layer is **greenfield**, which is an advantage — M0
builds the shell and tokens before the flagship needs them, with no legacy design
debt worth preserving beyond the existing form logic.

---

## 4. User Archetypes, Experience Loops, and the Primary Journey

### 4.1 A-1 First-time visitor (evaluator)

- **Goals:** Decide in < 30 s whether this beats chev.me/arucogen; ideally
  experience one "oh, it does *that*" moment.
- **Entry points:** Organic search ("aruco generator", "online camera calibration",
  conversion queries), community links.
- **Core workflow:** Land → scan hero → take one low-commitment action.
- **Success state:** Performed any core action (downloaded, detected, converted) —
  and *saw a handoff* hinting at the loop.
- **Retention loop:** The on-screen-marker demo ("point your phone camera at this
  screen") delivers a detection success in < 60 s with nothing printed; the success
  confirmation (C-11) offers "Print this marker for real" → A-2 loop.
- **Friction points:** 8 MB wasm load (mitigate: never load on homepage; lazy +
  size-honest C-12); skepticism (mitigate: PX-6 line above the fold); choice
  paralysis (mitigate: hero = the three-step loop, one CTA).
- **UX requirements:** Homepage demonstrates rather than describes (§5.5); zero
  permission prompts until explicit user action; first-visit success must not
  require a printer.
- **Served by:** F-02 (demo mode), F-03/F-04 (search-intent landings that convert),
  homepage spec §5.5.

### 4.2 A-2 Marker creator (maker)

- **Goals:** Correct dictionary/ID/size; dimensionally accurate physical output
  (print or laser); confidence it will detect in their application.
- **Entry points:** Homepage CTA, search, returning bookmark.
- **Core workflow:** Generate (advisor strip guides size/dict) → download (format
  remembered) → print/cut → verify (ruler check, then live webcam check).
- **Success state:** A physical marker verified detecting, with measured scale
  within tolerance (C-11 with confidence C-10).
- **Retention loop:** Verification success hands off to "Calibrate with this camera"
  (A-3) or "Get runtime config" (A-6); saved MarkerConfigs make repeat generation a
  two-click task.
- **Friction points:** Wrong size discovered late (→ F-03 inline strip, PX-9
  qualified ranges); printer scaling silently wrong (→ F-07a ruler + F-07b measure);
  dictionary confusion (→ F-08 advisor, PX-12 callouts).
- **UX requirements:** Advisor guidance inline, not on a separate page (PX-8);
  download is a split-button remembering last format; every export's success state
  includes the verify handoff (PX-5).
- **Served by:** F-03, F-07a/b, F-08, F-11, F-12, existing generation.

### 4.3 A-3 Calibration user (robotics engineer)

- **Goals:** Trustworthy intrinsics + distortion in minutes; *know* whether to trust
  them; output in their stack's format.
- **Entry points:** Search ("online camera calibration charuco"), handoff from Live,
  Learn articles.
- **Core workflow:** Board step (pre-filled from Generate, PX-8) → guided capture
  (C-04 + C-05 + quotas C-15) → solve (C-12 long tier) → results (C-09 verdict +
  C-10 confidence + factor breakdown) → outlier cleanup (≤ 2 clicks) → export
  (C-18) → save profile (chip C-02 updates).
- **Success state:** Exported calibration with confidence ≥ 70 and an understood
  reason for the score.
- **Retention loop:** Saved profile powers pose in Live and configs in Convert — the
  profile chip is a standing reminder; lens/camera changes trigger return visits
  ("Recalibrate" action on stale profiles, age shown).
- **Friction points:** Not knowing what good input data is (→ entire §11 gate
  system, PX-1); solve anxiety during 15 s wait (→ C-15 with stage labels); result
  distrust (→ PX-9 methodology link, held-out validation §11.8).
- **UX requirements:** Capture quotas visible as progress, never as rejection spam;
  one instruction at a time (PX-1); confidence contract (§2.3) honored exactly;
  upload path is first-class peer to webcam (PX-4 lateral exit).
- **Served by:** F-01 (flagship), F-00, F-04, F-06.

### 4.4 A-4 Validation user (debugger)

- **Goals:** Answer "why isn't my marker detecting?" in their own pipeline; leave
  with concrete parameter or physical changes.
- **Entry points:** Search ("aruco not detecting"), handoff from Live
  troubleshooting (PX-4 lateral exit), community links to the playground.
- **Core workflow:** Bring evidence (upload / webcam still / handoff frame, PX-8) →
  see detected *and rejected* candidates → adjust parameters, < 300 ms feedback
  (PX-10) → identify cause (verdict C-09 names the dominant rejection stage, labeled
  heuristic per PX-9) → export fixed parameters as code.
- **Success state:** Copied parameter export, or identified physical fix (quiet
  zone, size, lighting) via quality report.
- **Retention loop:** The playground becomes the canonical link they share when
  *others* ask "why isn't my marker detecting" — community amplification is the
  loop.
- **Friction points:** 30 cryptic parameters (→ grouped + plain-language tooltips +
  diff-from-default badges); not knowing if image or params are at fault (→ quality
  report runs alongside, C-09 separates "image problems" from "parameter problems").
- **UX requirements:** Rejected candidates visually distinct (§6.2 detection overlay
  tokens); reset-to-defaults always one click; pathological-parameter freeze
  auto-reverts with toast (PX-4).
- **Served by:** F-05, F-09, F-02 handoff.

### 4.5 A-5 Production operator (technician)

- **Goals:** Run a known-good check without understanding CV: "is this camera/marker
  station still working?"; follow a procedure someone else set up.
- **Entry points:** A shared URL (F-17) or bookmarked workspace configured by an
  engineer (A-6); kiosk-ish usage on the floor or in the field (drone pre-flight).
- **Core workflow:** Open shared link (state pre-loaded, PX-8) → Live workspace →
  point camera → read the verdict chip (C-06): green or not green → if not green,
  follow FixItPanel steps written in plain language (PX-4).
- **Success state:** Green verdict logged (manually for now); anomaly escalated with
  a copied diagnostics report (C-16) instead of a vague phone call.
- **Retention loop:** Recurring procedure = recurring visits; the diagnostics report
  becomes the escalation artifact between A-5 and A-6 personas.
- **Friction points:** Any CV jargon (→ Layer 1 must be jargon-free, PX-7); camera
  permission re-prompts (→ persisted device choice, §12.2); ambiguity (→ binary
  verdict presentation at Layer 1; "Marginal" tier includes the plain next action).
- **UX requirements:** Layer 1 of Live must be operable with zero training; shared
  URLs must restore the full checking context; verdicts never require numeric
  interpretation (PX-2).
- **Served by:** F-02, F-17, F-07b; validates the three-layer system end-to-end.

### 4.6 A-6 Advanced technical user (expert)

- **Goals:** Full parameter control, raw numbers, model choice, scriptability;
  verify the tool's math before trusting it.
- **Entry points:** Skeptical arrival via community discussion; often evaluates the
  methodology pages before touching the tool.
- **Core workflow:** Expert mode on (persisted) → works at Layer 3 everywhere: raw
  DetectorParameters in any camera view, calibration model selection (OPENCV4/8/12,
  fisheye) with per-coefficient σ, gate-threshold editing, JSON state editing, API
  previews → exports configs/code into their own pipeline.
- **Success state:** The tool's outputs cross-checked against their own pipeline and
  adopted; parameters/configs embedded in their deployed system (F-06).
- **Retention loop:** Their deployed configs reference the tool; they amplify in
  communities (the playground and converter are their share-objects); their feature
  feedback (diagnostics drawer link) steers Phase 3.
- **Friction points:** Anything hidden ("where's the raw matrix?") (→ Expert mode
  adds density without relocating anything, PX-7); unstated assumptions (→ PX-9 is
  largely for them); UI-only workflows (→ copy-as-code everywhere, F-15 CLI later).
- **UX requirements:** Expert mode is one global toggle, persisted, discoverable in
  the diagnostics drawer and keyboard map; numbers use mono type with full precision
  on hover/copy (§6.3); nothing Expert-only is required for Layer-1 success.
- **Served by:** Expert mode (cross-cutting), F-05, F-04, F-06, F-15, F-18.

### 4.7 A-7 Returning user (habit loop)

- **Goals:** Resume exactly where they left off; repeat a past task with new inputs
  in minimal clicks.
- **Entry points:** Bookmark, browser history, chip-driven memory ("my calibration
  is in that tool").
- **Core workflow:** Land on last-used workspace (restored state, PX-8) → recent
  items surfaced (recent boards, profiles, conversions) → repeat or continue.
- **Success state:** Time-to-repeat-task < 25% of first-time duration.
- **Retention loop:** This *is* the retention loop — the product's O1 metric.
  Mechanisms: profile shelf, recent configs, resume-session prompts, stale-profile
  recalibration nudges (age-based, gentle, dismissible).
- **Friction points:** State loss (→ continuous localStorage persistence, versioned
  schemas surviving deploys); changed UI between visits (→ design-system stability;
  §17 consistency checklist exists substantially for this archetype).
- **UX requirements:** "Clear local data" must show what's stored and its size
  (§5.7); restored state must be visibly labeled ("Resumed from June 10 · start
  fresh") so restoration never feels like a bug.
- **Served by:** Profile shelf, session resume (§12.6), F-17, all chips.

### 4.8 Primary user journey walkthrough (step-by-step)

The reference journey: **Riya, robotics engineer**, integrating marker localization
on an AMR. Secondary journeys (drone precision landing; manufacturing fixture tags)
share ~80% of these steps. Each step: what the user sees, what they're trying to
accomplish, current friction, and the recommended improvement.

**Step 1 — Arrival** (search: "aruco marker generator mm accurate")
- *Sees:* Home page, feature cards. *Goal:* Decide in 10 seconds whether this beats
  chev.me/arucogen.
- *Current friction:* Home page describes features; it doesn't *demonstrate* the
  loop. The fabrication advantage (the actual differentiator) isn't shown visually.
- *Improvement:* Hero = three-step visual loop "Generate → Print/Cut → Verify live
  with your webcam." A "Try detection now" button that opens the live validator with
  a marker rendered on screen (detectable by pointing a phone at the monitor) is the
  single best first-touch demo and requires zero printing. Full homepage spec §5.5.

**Step 2 — Generate**
- *Sees:* Parameter form, preview, download buttons. *Goal:* Correct dictionary, ID,
  physical size.
- *Current friction:* No guidance on dictionary choice or size-for-distance.
  Engineers routinely guess wrong (4×4 at 10 m, 7×7 where 4×4 would detect farther).
- *Improvement:* Inline **advisor strip** (C-14 + F-03): "At 30 mm, a 4×4 marker is
  reliably detectable to ~1.9 m on a 1080p camera with 70° HFOV. [Adjust]".
  Dictionary dropdown gains "help me choose" (F-08).

**Step 3 — Fabricate**
- *Sees:* Downloaded file. *Goal:* A print/cut at exact physical scale.
- *Current friction:* Printer scaling ("fit to page") silently breaks dimensional
  accuracy; user has no check.
- *Improvement:* Every PDF/SVG gets a **calibrated ruler + checkbox text** ("This
  bar must measure exactly 100 mm") — F-07a. Post-print, the live validator measures
  marker size via webcam (F-07b).

**Step 4 — Verify**
- *Sees:* Today: nothing. Must write a Python script. *Goal:* "Does my printed/cut
  marker detect?"
- *Current friction:* Total. This is where users leave and never return.
- *Improvement:* **Live Detection workspace** (F-02): point webcam, see overlay, ID,
  FPS, corner stability, quality verdict (C-06). This converts a one-visit user into
  a returning one.

**Step 5 — Calibrate camera**
- *Sees:* Today: a board generator and nothing else. *Goal:* Intrinsics +
  distortion they can trust.
- *Current friction:* Total. Alternatives are OpenCV samples (clunky), ROS GUI
  (ROS-bound), kalibr/mrcal (heavyweight). The known industry pain is *not knowing
  whether a calibration is good* ("real bugs written off as bad cal").
- *Improvement:* **Calibration Studio** (F-01) — guided webcam/upload capture,
  coverage heatmap, per-image reprojection errors, plain-language verdicts, export
  to OpenCV YAML / ROS camera_info / JSON. Flagship; full spec §10.1 + §11.

**Step 6 — Tune detection**
- *Sees:* Today: nothing. *Goal:* Fix "marker not detected" in their own pipeline.
- *Current friction:* `cv2.aruco.DetectorParameters` has ~30 undocumented-in-practice
  knobs; tuning is blind trial-and-error.
- *Improvement:* **Detector Parameter Playground** (F-05): load a failing image,
  adjust parameters with live re-detection, *visualize rejected candidates* (the key
  diagnostic OpenCV computes but no tool shows), export params as Python/C++/ROS
  YAML.

**Step 7 — Integrate**
- *Sees:* Today: a YAML of pattern metadata. *Goal:* Paste-ready config + code for
  their runtime.
- *Improvement:* **Runtime Config Exporter** (F-06): board geometry as
  `aruco_ros`/`apriltag_ros`/Isaac-style YAML + matched Python/C++ detection snippet
  with the user's exact dictionary, size, and (if present) calibration profile baked
  in.

**Step 8 — Return visits**
- *Goal:* Re-check after lens change, new camera, new print.
- *Improvement:* localStorage **profile shelf**: saved calibrations and marker
  configs, visible in the toolbar status chips (C-02). Zero-account persistence
  (A-7 loop).

---

## 5. Information Architecture, Toolbar, and Application Layout

### 5.1 Global navigation model

Six top-level **workspaces** (stations on the bench, §2.1), flat, no dropdowns in
primary nav, rendered in the AppShell (C-01):

| Workspace | Mandate | Primary action |
|---|---|---|
| **Generate** | Create any pattern: markers, boards, grids, AprilTags, diamonds, landing pads | Download ▾ (split, remembers format) |
| **Calibrate** | Calibration Studio + profile shelf | Stage-dependent (Capture / Solve) |
| **Live** | Webcam detection, print verification, demo mode | Start camera |
| **Debug** | Parameter playground, upload quality reports, Hamming/dictionary analyzer | Run detection |
| **Convert** | Calibration file converter + runtime config exporter | Convert |
| **Learn** | Methodology, guides, calculator, troubleshooting articles | (content) |

Rationale per workspace: workspaces map one-to-one to user *intents* ("I need a
marker" / "I need to calibrate" / "is it working?" / "why isn't it working?" /
"give me the file" / "explain this to me"), which is how IA earns instant
comprehension. The previous Generate-vs-Calibration-patterns split (pattern
*creation* scattered across two pages) is dissolved: creation always lives in
Generate; *using* patterns lives in Calibrate/Live/Debug. Convert earns a top-level
slot despite being "small" because it is daily-use and SEO-critical; habit formation
needs a stable address. Learn holds long-form methodology and doubles as the SEO
surface.

Workflow handoffs are explicit buttons, not navigation: Generate → "Calibrate with
this board", Live → "Open in Debug" (PX-5).

### 5.2 Application shell layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ ◇ ArUco Toolbox   Generate  Calibrate  Live  Debug  Convert  Learn   │ ← top bar (C-01)
│                   ────────                                           │
│                          [📷 FaceTime HD ●] [🎯 Cal: HD-Pro ✓] [⚙][?]│ ← status chips (C-02)
├────────────┬─────────────────────────────────────────┬───────────────┤
│ Parameters │                                         │ Inspector     │
│ (left      │           Canvas / preview              │ (right panel: │
│  panel,    │   (marker SVG, live video, results)     │  metrics,     │
│  workspace-│                                         │  verdicts,    │
│  specific) │                                         │  exports)     │
├────────────┴─────────────────────────────────────────┴───────────────┤
│ ▸ Diagnostics                                    Expert mode [off]  │ ← drawer (C-16)
└──────────────────────────────────────────────────────────────────────┘
```

Dimensions and responsive behavior in §6.4/§6.11. The three-panel structure
(Parameters / Canvas / Inspector) is C-03 and identical across workspaces — that
constancy is the mental model (§5.9).

### 5.3 Primary areas vs secondary tools vs utilities

- **Primary areas** (workspaces above): own nav slots, own URL roots (`/generate`,
  `/calibrate`, `/live`, `/debug`, `/convert`, `/learn`).
- **Secondary tools** live *inside* workspaces as modes, selected by a segmented
  control (C-03 header), never by sub-navigation pages: Generate modes = Marker |
  Board | AprilTag | Diamond | Landing pad; Live modes = Detect | Verify print |
  Demo; Debug modes = Playground | Quality report | Dictionary analyzer; Convert
  modes = Calibration files | Runtime configs.
- **Utilities** (calculator F-03) are dual-homed by design: canonical standalone
  page under Learn (`/learn/marker-size-calculator`, for SEO + direct intent) *and*
  embedded inline where decisions happen (advisor strip in Generate). Utilities
  never get top-level nav slots — six is the cap.

### 5.4 Primary and secondary action architecture

Exactly one primary action per workspace (table 5.1), top-right of the canvas area,
accent-colored (§6.6), keyboard-accessible (`Enter` from form context). Secondary
actions (Save profile, Copy link, Reset, handoffs) render as quiet buttons in the
Inspector panel or results screens — never competing visually with the primary.
Handoff buttons (PX-5) are visually distinct (chevron suffix "Verify live ›")
because they change workspace context.

### 5.5 Homepage specification

The homepage is a **demonstration, not a description** (A-1). Contents, in order:
1. Hero: the three-step loop visual (Generate → Print/Cut → Verify) with the PX-6
   privacy line.
2. One CTA: "Generate a marker" + secondary "Try live detection" (demo mode, marker
   rendered on screen, detectable via phone camera — no printer needed).
3. The bench strip: six workspace cards, one sentence each, mapping the IA to intent
   ("Why isn't my marker detecting? → Debug").
4. Credibility row: privacy claim, accuracy methodology link, open formats list.

Explicitly banned from the homepage: feature grids longer than six items,
testimonials (we have none — PX-9), any wasm loading, any camera permission request.

### 5.6 Workflow hierarchy: tasks, flows, loops

Three workflow tiers with distinct UI containers, so users always know "how deep"
they are:
- **Tasks** (single screen, immediate result: convert a file, compute a size) live
  in a single C-03 panel set. Anything completable in < 60 s with zero prior state.
- **Flows** (multi-step with state: calibration capture, landing-pad design) use the
  Stepper (C-07) and own the workspace canvas until completed or abandoned — with
  state preserved either way (PX-8). Only state-accumulating work gets a stepper
  (a stepper on a two-field task is cognitive theater).
- **Loops** (cross-workspace journeys, §2.3 graph) are never containers; they are
  the handoff edges between tasks and flows.

Implementation rule: no modals for workflow steps — modals are reserved for
destructive confirmation and the permission primer (§12.1) only.

**Advanced placement litmus (PX-7):** "would removing this from the default surface
block any A-2/A-3/A-5 success state?" If no → Layer 3.

### 5.7 Settings architecture

Settings are deliberately starved (most "settings" are workspace state, which lives
in workspaces per PX-3). Gear popover, three groups, ≤ 12 items total:
- **Units & formats:** mm/in, default YAML dialect, default code-snippet language.
- **Camera:** preferred device, processing resolution, mirror preview, capture
  sounds.
- **Application:** theme light/dark, Expert mode, keyboard map link, clear local
  data — with itemized size readout ("3 calibration profiles · 2 sessions ·
  2.1 MB").

Anything proposed for settings must first fail the test "is this actually workspace
state or a Layer-3 control?"

### 5.8 Feature discoverability strategy

Layered, so disclosure (PX-7) never becomes burial:
1. **Handoffs** are the primary discovery engine — users discover Calibrate because
   Live success offers it (PX-5).
2. **Mode controls** (5.3) keep secondary tools visible as labeled segments even
   when unused.
3. **Empty states teach** — an empty Debug workspace shows what it does with a
   sample-image button.
4. **Contextual cross-links** in callouts (C-14) and FixItPanels (C-13) route users
   laterally at the moment of need.
5. **The keyboard overlay** (`?`) doubles as a capability map for A-6.

Measured by the §16 activation metric: % of sessions touching ≥ 2 workspaces.

### 5.9 Content hierarchy and the user's mental model

The sentence the product must teach in the first session: **"My work moves between
stations, and the bench remembers it."** Content hierarchy enforces it:
- Level 1 = the bench (AppShell: nav + chips — global, persistent).
- Level 2 = the station (workspace: params left, canvas center, inspector right).
- Level 3 = the work (the board/frame/profile in the canvas, always the visual
  center).
- Level 4 = the verdict (C-09/C-10 attached to the work, never floating free).

Every screen renders all four levels in the same positions; that constancy *is* the
mental model.

### 5.10 Diagnostics panel and Expert mode

**Diagnostics drawer (C-16, bottom, collapsed by default):** processing FPS vs
camera FPS, frame latency ms, OpenCV.js version + wasm status, worker memory trend
(leak counter), live network activity (= none — PX-6 proof), detection counts
(accepted/rejected candidates), active DetectorParameters summary, last error with
stack, Expert-mode toggle, feedback link, [Copy diagnostics report] for bug
reports/GitHub issues. Collapsed 36 px strip shows three vitals (fps · latency ·
wasm ●); `.` toggles.

**Expert mode (toggle in drawer; persists):** off by default; flips the product
from guided to professional without forking the UI: raw `DetectorParameters`
editing everywhere (not just Playground), calibration model selection
(OPENCV4/8/12, fisheye) + per-coefficient display with standard deviations,
frame-gate threshold editing (§11.6), JSON state view/edit per workspace, rejected
frame inspection in Studio, API request preview ("this UI action = this curl").

---

## 6. Design System Foundation — "Workbench"

Implementation-ready standards. Tokens are CSS custom properties in
`static/css/tokens.css`; components (§7) consume tokens only — **no raw hex/px
values in component CSS**. This section is the single source of truth for visual
language; agents must not introduce colors, sizes, or motion outside it.

### 6.1 Color philosophy

Dark-first (default), light theme supported via token swap. Rationale: camera work —
a dark UI reduces screen glare contaminating webcam frames during calibration
(functional, not aesthetic); plus audience convention (IDEs, Foxglove, scopes). The
palette is deliberately austere — near-monochrome slate + one accent — so that
**semantic color is always signal, never decoration.** If something is green, it
passed; if orange, it was rejected; if violet, it's a measurement. No marketing
gradients inside workspaces.

### 6.2 Color tokens

```css
/* Neutral bench (dark theme values) */
--bench-bg: #0f1117;          /* app background */
--bench-surface: #161a22;     /* panels, cards */
--bench-surface-2: #1e2430;   /* nested surfaces, hover */
--bench-border: #2a3140;
--bench-text: #e6e9ef;        /* 13.9:1 on surface */
--bench-text-dim: #9aa3b2;    /* 5.2:1 — minimum for body text */
--bench-text-faint: #6b7383;  /* large/disabled text only */

/* Accent — one only */
--accent: #4d9fff;            /* primary actions, focus, active nav */
--accent-pressed: #3a86e0;
--accent-surface: #14283f;    /* selected/active backgrounds */

/* Semantic status (UI states) */
--ok: #3ecf8e;      --ok-surface: #0f2b20;
--warn: #f5b83d;    --warn-surface: #2e2410;
--error: #f0564a;   --error-surface: #2e1513;
--info: #4d9fff;    --info-surface: #14283f;   /* shares accent hue */

/* Confidence ramp — RESERVED: only C-10 and verdict tiers may use these */
--conf-high: #3ecf8e;   /* ≥90 Production-ready */
--conf-mid:  #f5b83d;   /* 70–89 Usable */
--conf-low:  #f0564a;   /* <70 Fix/recapture */

/* Detection overlay (canvas only — chosen for visibility over live video) */
--det-accepted: #00e676;   /* detected marker outlines/corners */
--det-rejected: #ff9100;   /* rejected candidates (F-05's hero color) */
--det-id-label: #ffffff on rgba(0,0,0,.65);
--det-measure: #b388ff;    /* measurements, distances, pose distance */
/* pose axes follow CV convention: X #ff5252, Y #69f0ae, Z #448aff */
```

Rules: semantic colors never appear without an icon + text label (color-blind
safety, §6.10); `--det-*` tokens are canvas-only (never UI chrome); the confidence
ramp is exclusive to confidence (PX-11) — a green button uses `--ok`, never
`--conf-high`, even though values may coincide; values may be retuned for contrast,
but token *names* are the stable API.

### 6.3 Typography

```css
--font-ui: Inter, -apple-system, "Segoe UI", sans-serif;
--font-data: "JetBrains Mono", "SF Mono", Consolas, monospace;

--text-xs: 12px/16px;   /* captions, chip labels, axis labels */
--text-sm: 14px/20px;   /* body, controls (UI default) */
--text-md: 16px/24px;   /* Learn prose, callouts */
--text-lg: 20px/28px;   /* panel titles, verdict lines */
--text-xl: 24px/32px;   /* workspace titles */
--text-hero: 32px/40px; /* confidence score number, homepage h1 */
```

**The data rule (house signature):** every number a user might trust, copy, or
compare — matrices, coefficients, RMS, distances, IDs, sizes — renders in
`--font-data`, right-aligned in tables, with display precision per PX-9 (qualified)
and full precision on hover-tooltip and copy. UI chrome never uses mono; data never
uses UI font. This single rule does more for "precision instrument" feel than any
visual flourish.

### 6.4 Spacing and grid

4 px base: `--s1:4 --s2:8 --s3:12 --s4:16 --s5:24 --s6:32 --s7:48 --s8:64`.
Component internals use s1–s4; panel padding s5; section gaps s6–s8.

Workspace grid (C-03): left Parameters panel fixed 300 px; center Canvas flexible
(min 480 px); right Inspector fixed 340 px; app bar 48 px; diagnostics drawer 36 px
collapsed / 280 px open. Breakpoints: < 1100 px Inspector collapses to tabs behind
the canvas; < 800 px single column, panels become accordion sections above/below
canvas (§6.11).

### 6.5 Elevation and surfaces

Three levels only: bg → surface → surface-2. Borders (`--bench-border`) delineate;
shadows minimal (popovers/drawers only: `0 8px 24px rgba(0,0,0,.4)`). Radius:
`--r-sm:4px` (chips, inputs), `--r-md:8px` (cards, panels), `--r-lg:12px` (modals).
No glassmorphism, no decorative borders — bench austerity (§6.1).

### 6.6 Action states (implementation-exact)

| State | Spec |
|---|---|
| **Primary action** | Solid `--accent`, white text, `--r-sm`, height 36 px, weight 600. Exactly one visible per workspace (§5.4). Disabled: 40% opacity + tooltip stating *what's missing* (PX-4: "Need 4 more tilted views"). Busy: spinner replaces label, width locked (no layout shift). |
| **Secondary action** | Transparent, 1 px `--bench-border`, `--bench-text`; hover → `--bench-surface-2`. |
| **Handoff action** | Secondary style + `--accent` text + "›" suffix. Always full context transfer (PX-5/PX-8). |
| **Destructive** | Secondary style, `--error` text/border. Confirmation modal only when irreversible (clear data, delete profile). |
| **Quiet/icon action** | No border, `--bench-text-dim`, hover surface; 32 px hit target minimum; aria-label mandatory. |

### 6.7 Feedback states (validation, success, warning, error)

| State | Spec |
|---|---|
| **Field validation** | Inline, on blur (never on keystroke), `--error` border + 12 px message below stating the constraint, not "invalid" ("Size must be positive, in millimeters" — existing repo convention, now a token of house style). |
| **Warning** | `--warn-surface` band with ⚠ icon + text; inline above affected control or in Inspector; never a toast (warnings need permanence). |
| **Success (event)** | Toast (C-17), `--ok`, auto-dismiss 4 s, max one concurrent. |
| **Success (milestone)** | Success confirmation (C-11) inline in canvas/inspector — not a toast — with handoff (PX-5). |
| **Error** | FixItPanel (C-13) inline; toasts never carry errors requiring action (PX-4). |

### 6.8 Detection and calibration confidence states

| State | Visual contract |
|---|---|
| **Detection: reliable** | C-06 chip: `--ok` dot + "Detects reliably" + (Layer 2) corner-jitter px, margin metrics |
| **Detection: marginal** | `--warn` dot + "Marginal — low contrast" (dominant cause named, PX-2) |
| **Detection: failing** | `--error` dot + "Not detecting — [reason]" + FixIt actions (PX-4) |
| **Candidates (canvas)** | accepted `--det-accepted` solid 2 px; rejected `--det-rejected` dashed 1.5 px + stage tag on hover (F-05) |
| **Calibration ≥ 90** | C-10 full ramp green + "Production-ready" + factor list |
| **Calibration 70–89** | ramp amber + "Usable — [dominant factor]" + one improvement action |
| **Calibration < 70** | ramp red + "Recapture recommended — [cause]" + targeted re-capture action (e.g., "Capture 5 frames near image corners") |

Tier thresholds live in one constants module (`vision-core/confidence.js`) — UI
never hardcodes them.

### 6.9 Iconography and motion

Icons: Lucide, outline, 1.5 px stroke, 16/20 px sizes, always paired with text in
status contexts (§6.2 rule); domain glyphs (marker, board, axes) drawn in the same
stroke style, kept in `static/icons/`.

Motion: 150 ms ease-out for state changes, 250 ms for panel/drawer transitions;
**no decorative animation inside workspaces**; permitted celebratory moments (C-11
milestone, capture shutter flash 120 ms) are the deliberate exceptions that make
the rest feel calm; `prefers-reduced-motion` disables all non-essential motion and
replaces the capture sound+flash with a static counter increment.

### 6.10 Accessibility standards (binding, in §17 checklist)

WCAG 2.2 AA. Contrast ≥ 4.5:1 body, ≥ 3:1 large text and UI parts (tokens §6.2
pre-verified; changing them requires re-verification). Never color-only meaning
(icon+label always). Full keyboard operability incl. stepper navigation and manual
capture (`Space`); visible focus ring (2 px `--accent`, 2 px offset) never
suppressed. Live camera guidance (C-05) mirrors to `aria-live="polite"`; capture
audio cues have visual equivalents. Canvas overlays get text alternatives in the
Inspector (detected IDs/positions as a list — which doubles as A-6's copyable data;
accessibility and expert needs converging). Hit targets ≥ 32 px. Reduced-motion
honored (§6.9).

### 6.11 Responsive behavior

Desktop-first (audience reality), with two committed mobile scenarios: **Live on a
phone** (A-1 demo + A-5 field checks — full support, simplified single-column:
camera canvas + verdict chip + guidance bar only) and **Learn/calculator/converter
on any device** (full support). Calibration Studio on mobile: capture is supported
(phones are cameras), solve+results best-effort; the Studio detects small viewports
and offers "Capture here, review on desktop" via session continuity
(F-17/localStorage — honest scoping per PX-9 rather than a degraded pretense).

---

## 7. Universal Component Architecture

The complete UI vocabulary. Every screen is composed from these components; specs
(§10) reference them by ID. Each entry: purpose · layout rules · behavior rules ·
state rules · accessibility (a11y). Implementation: vanilla ES modules in
`static/js/components/`, one file per component, JSDoc-typed, consuming §6 tokens
only.

**C-01 AppShell** — *Purpose:* the bench (§5.9 L1): top bar (logo, six workspace
links, status chips, gear, help) + content slot + diagnostics drawer. *Layout:*
48 px bar; active workspace underlined `--accent`. *Behavior:* workspace switch
preserves outgoing state (PX-8); keyboard `g`+key navigation. *States:* per-chip
states delegate to C-02. *A11y:* `<nav>` landmark, skip-link to canvas.

**C-02 StatusChip** — *Purpose:* ambient cross-workspace state (PX-3): camera,
calibration profile, board context. *Layout:* icon + label + health dot, max
160 px, ellipsized. *Behavior:* click → popover (device picker / profile shelf /
board summary); chips are the *only* UI for global state. *States:* ok (`--ok` dot)
/ degraded (`--warn`, reason in tooltip) / absent (muted, label = invitation: "No
calibration"). *A11y:* button role, state in accessible name ("Camera: FaceTime HD,
healthy").

**C-03 WorkspacePanel set** — *Purpose:* the station (§5.9 L2): Parameters (left) /
Canvas (center) / Inspector (right) + mode segmented-control header. *Layout:* §6.4
grid. *Behavior:* panel collapse persisted per workspace; mode switches preserve
field values across modes where fields overlap (PX-8). *States:* Inspector empty
state = teaching content (§5.8). *A11y:* panels are labeled regions; mode control
is `radiogroup`.

**C-04 CameraView** — *Purpose:* all live video: preview + overlay canvas + camera
controls strip. *Layout:* 16:9 letterboxed canvas, controls strip below (device/res
selects, mirror toggle), PX-6 privacy line directly under strip. *Behavior:*
display may mirror; processing never does (§12.3); overlay renders via `--det-*`
tokens; auto-pauses when tab hidden, auto-resumes with toast. *States:*
pre-permission (primer, §12.1) / starting (C-12) / live / degraded (fps warning
chip) / failed (C-13 with §12.5 tree). *A11y:* overlay data mirrored as Inspector
text list (§6.10); controls fully keyboard operable.

**C-05 GuidanceBar** — *Purpose:* PX-1's instrument: the single active instruction.
*Layout:* one line under the canvas, icon + imperative text, optional mini-progress
("Coverage 6/9"). *Behavior:* instruction-fusion fed (§11.7); updates throttled to
≥ 1.5 s display time per instruction (no flicker); disappears when quotas complete
("All set — keep steady" → auto-advance). *States:* instructing / acknowledging
(brief `--ok` flash on quota progress) / complete. *A11y:* `aria-live="polite"`,
politeness throttled to instruction changes only.

**C-06 QualityChip** — *Purpose:* evaluative traffic-light for a live/loaded subject
(frame quality, detection verdict). *Layout:* dot + ≤ 3-word verdict + (Layer 2)
expandable cause. *Behavior:* shows dominant cause only (PX-2); updates ≤ 2 Hz
(readable, not strobing). *States:* §6.8 detection states. *A11y:* `role="status"`,
text always present (never dot-only).

**C-07 Stepper (multi-step flow)** — *Purpose:* flows (§5.6): Board → Capture →
Solve → Results. *Layout:* horizontal steps across canvas top; current step bold
`--accent`; completed steps get ✓ and are clickable (back-navigation never loses
state, PX-8). *Behavior:* forward-gating with stated reasons on the disabled
primary action (§6.6); abandon-and-resume via session persistence. *States:* future
steps muted, never hidden (PX-7 anti-burial). *A11y:* `aria-current="step"`; step
list navigable.

**C-08 UploadZone** — *Purpose:* first-class peer to camera input (PX-4): images,
calibration files, configs. *Layout:* dashed `--r-md` zone, icon + "Drop or browse"
+ accepted formats + PX-6 line (or explicit server-upload disclosure where
applicable). *Behavior:* multi-file with per-file validation; rejects state *which*
constraint failed per file ("IMG_011.png: resolution differs from set — all frames
must match"); paste support for configs (Convert). *States:* idle / dragover
(`--accent` border) / validating / partial-error (file list with per-row status).
*A11y:* zone is a button; file list errors associated via `aria-describedby`.

**C-09 VerdictCard** — *Purpose:* PX-2's instrument: layered analytical result.
*Layout:* verdict line (`--text-lg`) + one-sentence dominant cause + expand
affordance → Layer 2 numerics table (mono, §6.3) + methodology link (PX-9).
*Behavior:* expansion state remembered per card type; copy icon on numerics.
*States:* verdict tier drives left border color (semantic or confidence tokens per
context). *A11y:* expansion is `aria-expanded` disclosure; tier conveyed in text.

**C-10 ConfidenceMeter** — *Purpose:* PX-11's single confidence visual. *Layout:*
hero number (`--text-hero`, mono) + tier label + horizontal ramp bar with threshold
ticks at 70/90 + factor rows on expansion (factor name, contribution bar, action
link). *Behavior:* factors sorted by improvement leverage; each factor's action is
a real fix-it (PX-4: "Capture 5 frames near corners" → returns to capture with that
quota highlighted). *States:* three tiers (§6.8) — never more, never fewer.
*A11y:* meter as `role="meter"` with valuetext ("82 of 100, Usable").

**C-11 SuccessConfirmation** — *Purpose:* milestone completion + loop continuation
(PX-5). *Layout:* inline card: ✓ + what was accomplished (specific: "Calibration
exported — HD-Pro, confidence 91") + ONE primary handoff + minor secondary actions.
*Behavior:* milestone-only (first detection, solve complete, print verified, export
done) — routine events use toasts; celebration motion per §6.9. *A11y:* focus moves
to the card heading on appearance.

**C-12 Loading/Empty states** — *Purpose:* PX-10 tiers + teaching empty states.
*Layout/Behavior:* **instant** (< 1 s): content-shaped skeleton, no text;
**working** (1–5 s): determinate progress + stage label ("Detecting corners — frame
12/23"); **long** (> 5 s): progress + label + cancel + honest estimate ("~10 s");
**byte-honest loads**: wasm shows "Loading vision engine (~8 MB, cached after first
use)"; **empty**: what this tool does (1 sentence) + sample-data action + relevant
handoff in (§5.8). *A11y:* progress as `role="progressbar"` with label; cancel
reachable first in tab order.

**C-13 FixItPanel (error state)** — *Purpose:* PX-4's instrument. *Layout:* what
happened (plain) + probable cause (ranked, one line) + 1–3 action buttons (first =
most likely fix, last = lateral exit) + "Copy diagnostics" quiet action. *Behavior:*
causes ranked by detected signals (§12.5), not generic lists; lateral exit always
present. *States:* `--error-surface` band; warning variant uses `--warn-surface`.
*A11y:* `role="alert"` on appearance; actions are real buttons.

**C-14 EducationalCallout** — *Purpose:* PX-12 in-context teaching. *Layout:* ⓘ +
1–2 sentences + optional "Learn more ›" deep link; `--info-surface`; placed at the
decision point it explains. *Behavior:* dismissible per-callout (persisted); ≤ 4
per flow; never modal/blocking. *States:* default/dismissed. *A11y:* not
`aria-live` (ambient, not interruptive).

**C-15 ProgressQuota** — *Purpose:* multi-dimension capture progress (coverage,
poses, frames) as motivation, not rejection. *Layout:* coverage = 3×3 mini-grid
overlay + sidebar; pose buckets = 6-icon checklist; frames = simple count. Each
fills toward complete; completed dimension gets ✓ and stops demanding (PX-1 feeds
off the incomplete ones). *Behavior:* progress only ever increases visibly (frame
*rejection* is communicated by C-06 quality chip, never as quota regression —
psychological asymmetry by design). *A11y:* summarized textually ("Coverage 6 of 9
zones").

**C-16 DiagnosticsDrawer** — *Purpose:* full-depth system status (PX-3) + A-6 entry
point + support artifact. *Layout/contents:* §5.10. *Behavior:* collapsed 36 px
strip shows three vitals (fps · latency · wasm ●); `.` toggles. *A11y:* drawer is a
labeled region; vitals have text labels.

**C-17 Toast** — *Purpose:* transient event feedback only (§2.3 feedback taxonomy).
*Layout:* bottom-right, icon + ≤ 1 line, 4 s. *Behavior:* max 1 concurrent (queue
drops oldest); **never** errors-requiring-action (PX-4), never milestones (C-11's
job). *A11y:* `role="status"`; never steals focus.

**C-18 ExportRow** — *Purpose:* uniform "get it out" pattern: format buttons +
copy-as-code. *Layout:* row of secondary buttons `[OpenCV YAML] [ROS1] [ROS2]
[JSON]` + `[Copy Python]` + split-button download memory. *Behavior:* every export
fires a C-17 success toast + updates "last format"; code copies include the PX-9
assumption header as comments. *A11y:* buttons labeled with format + target
("Export as ROS 2 camera_info YAML").

**C-19 ThumbnailStrip** — *Purpose:* captured-frame management (Studio) / result
galleries. *Layout:* horizontal scroll, 72 px thumbs, per-thumb status glyph (✓ /
outlier ⚠ from per-image error). *Behavior:* click → detail (frame's corners + its
reprojection error); delete with single-level undo (toast with Undo); outlier
thumbs surface C-10's "remove & re-solve" action. *A11y:* listbox semantics;
per-thumb accessible name ("Frame 7, error 1.4 px, flagged outlier").

**C-20 ComparisonTable** — *Purpose:* Convert previews, advisor recommendations,
model comparisons (F-18). *Layout:* mono data right-aligned (§6.3), differing
values highlighted `--accent-surface` in comparisons; one recommended column
flagged with reasoning line (PX-2). *A11y:* proper `<th>` scoping; highlight
conveyed in text ("(differs)").

---

## 8. Computer Vision Tooling Landscape (Context for Prioritization)

What engineers actually use, and where this product can and cannot compete:

- **Calibration:** OpenCV's CLI samples (clunky), ROS2 `camera_calibration` (GUI,
  ROS-bound), kalibr (multi-cam+IMU, notoriously slow — hours-long optimizations
  reported), mrcal (JPL-grade, best-in-class diagnostics, steep learning curve;
  WPILib now recommends mrcal over OpenCV for accuracy). The shared pain point per
  practitioners: "flaky calibrations… real bugs written off as 'bad cal'" —
  engineers lack fast feedback on *whether their calibration is any good*. **No
  good lightweight web tool exists for "upload 20 photos → intrinsics + quality
  diagnosis."**
- **Marker generation:** chev.me/arucogen, arucosheetgen, calib.io's pattern
  generator. All weaker than this repo on fabrication; none do validation.
- **Detection/tuning:** nothing but trial-and-error against
  `cv2.aruco.DetectorParameters` (~30 cryptic knobs documented but with no
  interactive tool anywhere).
- **Dataset/annotation/training:** Roboflow, CVAT, FiftyOne, Lightly — crowded,
  capital-intensive, correctly declared out of scope (A4).
- **Visualization/debugging:** Rerun, Foxglove for robotics streams — out of scope,
  but their popularity confirms engineers pay for debugging tools.
- **Emerging:** foundation models (SAM/Grounding DINO) made AI-assisted labeling
  table stakes in the dataset world — but matter little for the fiducial niche,
  one of the few CV areas where classical methods dominate and will for years
  (markers are used precisely *because* they're deterministic). Fiducials remain
  the bridge between VLM scene understanding and metric control — content angle,
  not product pivot.

**Strategic read:** the marker/calibration niche is defensible. Too small for
Roboflow to care, too "solved" for researchers, yet full of daily friction. The
competition is a handful of static single-page generators and intimidating academic
toolchains — nothing in between. That in-between is this product.

---

## 9. Prioritized Product Roadmap

Priority score = (Impact × Confidence) / Effort, normalized to 10. Effort in
agent-sessions (A1). UX work is *included in* each feature's effort — experience is
not a separate line item. Full specifications with user stories, acceptance
criteria, and edge cases in §10.

### 9.1 Phase 1 — High Impact / Low Effort (ship all within 30 days)

| ID | Feature | Problem being solved | User value | Business value | Technical implementation approach | Depends on | Effort | Score |
|---|---|---|---|---|---|---|---|---|
| F-90 | **Workbench foundation** | No tokens/shell/components for anything to plug into; IA is the wrong cut | One coherent product instead of disconnected pages | The experience moat's substrate; prevents design drift across agent sessions | `tokens.css` (§6), C-01 shell + chips slots, C-03 panels, C-09/C-12/C-13/C-14/C-17 component core; IA cutover to six workspaces with redirects; dark theme | None | 4 | (enabler) |
| F-03 | Marker size/distance/accuracy calculator | "How big must my marker be at X meters?" — the most-asked ArUco question | Instant, correct sizing decisions | SEO magnet; inline advisor differentiates the generator | Pure client JS. `min_size_mm ≈ (distance · (bits_per_side+2) · px_per_bit_required) / (resolution_h / (2·tan(HFOV/2)))`. Learn page + inline strip on Generate (dual-homed §5.3) | F-90 | 2 | 9.5 |
| F-04 | Calibration file converter | Engineers hand-translate OpenCV YAML ↔ ROS camera_info ↔ kalibr daily | 30 s instead of 20 min of error-prone editing | Daily-use bookmark; SEO ("opencv yaml to camera_info") | Client JS: js-yaml with custom schema for `%YAML:1.0` + `!!opencv-matrix`; adapters for OpenCV FileStorage YAML, ROS1/ROS2 CameraInfo, kalibr camchain, plain JSON; round-trip property tests | F-90 | 2 | 9.0 |
| F-08 | Dictionary advisor | Wrong dictionary choice (too dense / too small library) discovered late | Confident selection with stated trade-offs | Upgrades generator from form to expert tool | UI over existing Hamming endpoint (`/api/validation/hamming_distance`); decision table (marker count, distance, occlusion tolerance → recommendation + reasoning) rendered as C-20 | F-03 math | 2 | 8.0 |
| F-07a | Print-scale ruler on exports | Silent printer scaling breaks mm accuracy | Trustworthy prints | Protects the "dimensionally accurate" brand promise | 100 mm verification bar + instruction text in PDF (`exporters.py` PDFExporter) and SVG; **outside cut paths** in .lbrn2/DXF; snapshot tests | None | 1 | 8.5 |
| F-09 | Surface validation engine in UI | Powerful detect/quality/report APIs are invisible | Upload → full quality report without reading API docs | Existing investment finally pays | Wire Debug workspace to `verify_quality`, `detection_report`, `batch_test`; render failure-analysis as C-09 verdicts | F-90 | 2 | 7.5 |
| F-10 | Cut DB metrics; freeze pattern persistence | Dead weight, misleading in serverless | — | Less code for agents to maintain/misunderstand | Remove `/api/calibration/metrics` write path + `DetectionMetric` model usage; keep schema file; update `AI_NAVIGATION.xml` | None | 1 | 7.0 |
| F-11 | ChArUco diamond markers | Diamond markers absent; cheap completeness | Niche but real (multi-scale ID'd pose targets) | Catalog completeness vs chev.me | `cv2.aruco.drawCharucoDiamond` path in `calibration.py` + route + Generate mode segment | None | 2 | 6.0 |

F-90 is the experience twin of F-00: Phase 1 features ship *inside* it, which is how
the IA cutover happens early and cheaply, before camera features raise the stakes.

### 9.2 Phase 2 — Medium Complexity (days 30–90)

| ID | Feature | Problem being solved | User value | Business value | Technical implementation approach | Depends on | Effort | Score |
|---|---|---|---|---|---|---|---|---|
| F-00 | **OpenCV.js platform layer** | No client-side CV ⇒ no webcam features | (enabler) | Unlocks F-01/02/05/07b at zero marginal server cost | `static/js/vision/`: lazy-loaded opencv.js (pinned 4.x build, ~8 MB, `/static/vendor/`, `Cache-Control: immutable`), Web Worker wrapper, Mat lifecycle helpers, camera manager (getUserMedia), frame gates, confidence constants. Full detail §13 | None | 4 | (enabler) |
| F-02 | **Live Detection Validator** | No way to verify a printed marker without code | 10-second print→verify loop | The demo that sells the product; first webcam beachhead; A-1 acquisition via demo mode | Workspace using F-00: per-frame `detectMarkers` ≤ 15 fps, overlay canvas, ID/corner-jitter/FPS metrics, quality verdict reusing validation thresholds; demo mode renders an on-screen marker | F-00, F-90 | 4 | 9.0 |
| F-01 | **Calibration Studio** | No usable lightweight calibration tool exists anywhere | Trustworthy intrinsics in 5 min, with *why* | Category-defining feature; the reason to bookmark | Full spec §10.1 + §11. ChArUco capture (webcam + upload), quality gates, coverage map, worker-side `calibrateCameraCharuco`, confidence scoring with held-out check, diagnostics, export via F-04 adapters | F-00, F-04, F-90 | 8 | 9.5 |
| F-05 | Detector Parameter Playground | Blind tuning of ~30 DetectorParameters | See *rejected candidates*; fix detection failures in minutes | Genuinely novel; community shareability | Image (upload/webcam still/handoff) + parameter sidebar + live re-detect in worker; rejected-candidate overlay (OpenCV returns `rejectedImgPoints`); staged re-run for rejection attribution; export params Python/C++/YAML | F-00, F-90 | 5 | 8.5 |
| F-06 | Runtime Config Exporter | Generated board ≠ paste-ready runtime config | Copy-paste `aruco_ros`/`apriltag_ros`/Isaac YAML + code snippet | Embeds product into users' deployed systems (retention) | Server-side: board-geometry serializers + Jinja code-snippet templates bound to exact user params + active calibration profile; emitted-code execution tests in CI | F-01 (optional), F-90 | 3 | 8.0 |
| F-07b | Print verification via webcam | Is the printed marker the right physical size? | Closes fabricate→verify loop | Completes the brand promise | Live mode: detect marker + printed ruler bar, compute px/mm from known marker bits, report measured vs nominal size with ±1% tolerance verdict via C-10 | F-02 | 2 | 7.0 |
| F-12 | Nested landing-pad designer | Drones need detectable markers across altitude range | One artifact valid from 30 m to 0.3 m | Drone vertical wedge; pairs with laser-cut moat | Recursive layout (large outer marker, small inner in white cell), preset sizes, altitude-coverage chart from F-03 math, exports incl. tiled PDF + .lbrn2/DXF; PX4/ArduPilot precision-landing config snippet via F-06 | F-06, F-03 | 3 | 7.5 |

### 9.3 Phase 3 — Strategic Platform Features (3–9 months)

| ID | Feature | Problem / value | Approach | Depends | Effort | Score |
|---|---|---|---|---|---|---|
| F-13 | Stereo calibration | Stereo rigs are common (depth); web tooling nonexistent | Extend Studio: paired capture, `stereoCalibrate` in worker, rectification preview | F-01 | 8 | 7.0 |
| F-14 | Synthetic detection benchmark | "Will 5×5_100 at 40 mm survive my lighting?" | Server or client renders pose/blur/noise/light sweeps (extends `validation.py` distortion code); robustness report card via C-09/C-20 | F-09 | 6 | 6.5 |
| F-15 | CLI / pip package | Markers + configs in CI pipelines; A-6 scriptability | Extract `aruco_generator` core as installable package + `aruco-toolbox` CLI mirroring API | F-06 | 5 | 6.0 |
| F-16 | PWA / offline mode | Field engineers (drones!) have no connectivity | Service worker, precache wasm + app shell; all client-side tools work offline | F-00–F-05 | 4 | 6.0 |
| F-17 | Shareable state URLs | "Send your exact config/calibration to a teammate"; A-5 procedures | Compress workspace state → URL fragment (no server storage; respects A3) | Workspaces | 3 | 6.5 |

### 9.4 Phase 4 — Long-Term Differentiators (9+ months, revisit before committing)

| ID | Feature | Why it could matter | Effort | Score |
|---|---|---|---|---|
| F-18 | mrcal-lite calibration diagnostics (uncertainty quantification, cross-validation splits, model comparison OPENCV4 vs OPENCV8 vs fisheye via C-20) | Becomes the *trustworthy* calibration verdict tool; nearest thing to a defensible technical moat; the deepest PX-11 expression | 10+ | 7.0 |
| F-19 | Hand-eye calibration assistant (guided pose capture checklist + `calibrateHandEye` on uploaded robot/camera pose pairs) | Every arm team suffers this; tooling is dire | 8 | 6.5 |
| F-20 | Ground-truth rig designer (marker cubes/wands with known geometry for robot-learning data collection) | Rides the imitation-learning wave; fabrication moat applies (laser-cut cubes) | 6 | 6.0 |
| F-21 | Marker fulfillment (order laser-cut markers) | First obvious revenue; validates with zero code via manual fulfillment pilot | n/a | spec-only |

### 9.5 Feature-to-Experience Mapping (mandatory table — §17 rule 1)

Every feature's place in the experience system. New features must add a row here
**before implementation**.

| ID | UX purpose | IA location (§5) | Archetypes | Key components (§7) | Principles exercised | Confidence mechanism (PX-11) | Loop position (PX-5) |
|---|---|---|---|---|---|---|---|
| F-90 | The bench itself — coherence substrate | Global | All | C-01/02/03/09/12/13/14/17 | PX-3,7,8 | — | Carries all loops |
| F-00 | Invisible; enables instrument feel (latency, privacy) | Global (camera workspaces) | A-1,3,4,5 | C-04, C-16 | PX-6,10 | Powers all scoring | Enables Live/Calibrate/Debug nodes |
| F-01 | The flagship trust experience; full PXA showcase | Calibrate | A-3 (primary), A-6 | C-04/05/06/07/10/15/18/19 | All twelve | Calibration confidence (§11.8) | Live→**Calibrate**→Convert |
| F-02 | First magic moment; loop's verification node | Live · Detect/Demo modes | A-1,2,5 | C-04/05/06/11/13 | PX-1,3,4,5,6,10 | Detection verdict (§6.8) | Generate→**Live**→Calibrate/Debug |
| F-03 | Decision support at the moment of sizing | Learn page + Generate inline strip | A-2,1 | C-14, C-20 | PX-8,9,12 | Qualified ranges (PX-9) | Feeds Generate; entry from search |
| F-04 | Daily-utility trust beachhead | Convert · Calibration files | A-3,6,1 | C-08 (paste), C-20, C-18 | PX-4,9,10 | Lossless round-trip claim, tested | Calibrate→**Convert**; standalone entry |
| F-05 | Diagnostic superpower; "finally I can *see* it" | Debug · Playground | A-4 (primary), A-6 | C-08, C-06, C-09, C-18 | PX-2,4,9,10 | Rejection-stage attribution (labeled heuristic) | Live→**Debug**→Live (apply params) |
| F-06 | Integration finish line; embeds product in user systems | Convert · Runtime configs | A-3,6 | C-18, C-20, C-14 | PX-5,8,9 | Execution-tested snippets (trust by proof) | Calibrate/Generate→**Convert**→user's repo |
| F-07a | Passive trust in physical accuracy | Generate (all exports) | A-2 | (export artifact) | PX-9 | The ruler is a self-check affordance | Fabricate→verify bridge |
| F-07b | Active closure of the physical loop | Live · Verify print mode | A-2,5 | C-04/06/10/11 | PX-1,4,11 | Print accuracy ±1% via C-10 | Generate→Live(**verify**)→done/recut |
| F-08 | Confidence before commitment | Generate (advisor entry) + Debug analyzer | A-2,1 | C-20, C-14 | PX-2,9,12 | Recommendation w/ stated rationale | Entry→Generate |
| F-09 | Resurrects buried value as verdicts | Debug · Quality report | A-4,2 | C-08, C-09 | PX-2,4 | Quality report verdicts | Upload→Debug→fix→re-test |
| F-10 | Removes misleading surface (negative space is UX) | — | — | — | PX-9 | — | — |
| F-11 | Catalog completeness | Generate · Diamond mode | A-2,6 | existing Generate set | PX-8 | — | Generate loop |
| F-12 | Domain-specific guided design | Generate · Landing pad mode | A-2 (drone) | C-07, C-20, C-14, C-18 | PX-1,5,9,12 | Altitude-coverage chart w/ gap warnings | Generate→Live→field |
| F-13–F-21 | (Phase 3/4 — rows added when promoted to active) | | | | | | |

### 9.6 Redundant / low-value features (be honest about these)

- **Database persistence of patterns and detection metrics**
  (`calibration_web.py:1014`) — a stateless utility tool has no reason to store
  metrics rows; no engineer will POST their detection rates here. Cut (F-10).
- **STL landing-pad export** — niche; 3D-printed markers warp and lose flatness.
  Keep but don't invest.
- **Quick-test/observability endpoints** — fine as infra, zero user value; stop
  expanding.
- **Pure-Python fallback dictionary** — elegant engineering, but in 2026 OpenCV
  wheels install everywhere; maintenance cost should stay near zero.

---

## 10. Feature Specification Catalog

Detailed specifications. Format: user story · acceptance criteria (AC — each AC is
a test) · edge cases (EC — every row ends in a user action, PX-4) · success metric
(SM) · stated assumptions where computed outputs exist (PX-9).

### 10.1 F-01 Calibration Studio

> As a robotics engineer, I want to calibrate my camera in the browser with quality
> feedback, so that I get trustworthy intrinsics without installing kalibr.

- **AC1:** With a printed 7×5 ChArUco board and a 720p+ webcam, a first-time user
  reaches an exported OpenCV YAML in ≤ 7 minutes without external docs
  (usability-tested with 2 external engineers before launch).
- **AC2:** Capture cannot proceed to Solve until coverage ≥ 7/9 cells, ≥ 4/6 pose
  buckets, ≥ 12 accepted frames; the disabled Solve button states the missing quota
  (§6.6: "Need 4 more tilted views").
- **AC3:** Results show RMS, per-image errors, coverage heatmap, confidence score
  per the C-10 contract (§11.8); removing an outlier frame and re-solving takes
  ≤ 2 clicks via C-19.
- **AC4:** Exports (OpenCV YAML, ROS1 camera_info, ROS2 YAML, JSON) round-trip
  through the F-04 converter losslessly and load in `cv2.FileStorage` (fixture
  test).
- **AC5:** All frame processing in a Web Worker; UI stays ≥ 30 fps during capture;
  no image data leaves the browser (automated test asserts no POST bodies during a
  session — NFR-1/PX-6).
- **AC6:** Upload path: 15–40 images (JPEG/PNG; mixed resolution rejected per-file
  with clear message via C-08) produces identical results pipeline.
- **EC:** board spec mismatch (detects markers but wrong squaresX/Y → explicit
  C-13 error naming the mismatch, not silent failure); rolling-shutter motion blur
  (sharpness gate catches → guidance); fisheye lens (RMS high → suggest fisheye
  model, Expert mode); duplicate frames (near-identical pose rejected as adding no
  quota value — communicated via C-06, not quota regression); 4K camera on slow
  laptop (auto-downscale processing, full-res capture, status surfaced per §2.3
  visibility rule).
- **SM:** ≥ 60% of started capture sessions reach Solve; ≥ 40% of solves exported.
- **Assumptions stated in UI:** pinhole model validity range; held-out methodology
  linked (§11.8).

### 10.2 F-02 Live Detection Validator

> As an engineer who just printed a marker, I want to point my webcam at it and see
> it detect, so that I know the print works before integrating.

- **AC1:** From the Live tab, camera start → first detection overlay in ≤ 5 s on a
  valid marker; dictionary selectable; "auto-try-all" scan mode cycles dictionaries
  and locks onto the first hit.
- **AC2:** Overlay: corner polygon, ID label, per-marker corner-jitter (px std over
  rolling 30 frames), processing FPS.
- **AC3:** With a calibration profile loaded (C-02 chip), show pose axes + distance
  (using marker size input); without one, show a muted "Load calibration for pose
  ›" hint referencing the chip (PX-3 degradation).
- **AC4:** Verdict chip (C-06) reuses validation thresholds (`validation.py`
  contrast/sharpness/quiet-zone logic ported to JS or approximated): "Detects
  reliably" / "Marginal — [reason]" / "Not detecting — [reason]".
- **AC5:** Demo mode renders an on-screen marker detectable by a second device's
  camera; delivers a detection success with nothing printed (A-1).
- **EC:** marker on a monitor (moiré — works; note in help); multiple markers (all
  overlaid, count badge); upside-down marker (detects; show orientation); no
  detection 5 s → §12.5 troubleshooting FixItPanel with "Open this frame in Debug ›"
  lateral exit.
- **SM:** Median time from page load to first successful detection < 30 s; Live
  becomes the #2 entry page after Generate within 90 days; ≥ 50% of demo starts
  reach detection.

### 10.3 F-03 Size/Distance Calculator

> As a developer, I want to know the maximum reliable detection distance for a
> marker size and camera, so that I size markers correctly the first time.

- **AC1:** Inputs: marker size (mm), dictionary, camera preset (1080p/720p/4K +
  custom res/HFOV); outputs: max distance for reliable detection (≥ 2 px/bit) and
  comfortable detection (≥ 4 px/bit), px-per-bit at user-specified distance;
  inverse mode (distance → required size).
- **AC2:** Inline strip on Generate updates live with the size field; "Fix it"
  adjusts size to meet a user-entered distance.
- **AC3:** Methodology disclosure per PX-9: "assumes ideal focus/lighting; halve
  for harsh conditions" — credibility requires stating assumptions; full math on
  the Learn page.
- **EC:** absurd inputs clamp with explanation; fisheye HFOV > 120° warns the
  pinhole model is invalid at edges and links the Learn explainer.
- **SM:** Calculator page ranks for "aruco marker size distance" within 6 months;
  ≥ 20% of Generate sessions interact with the strip.

### 10.4 F-04 Calibration File Converter

> As a ROS developer, I want to convert OpenCV YAML to camera_info format, so that
> I don't hand-edit matrices at 2 a.m.

- **AC1:** Paste/drop any of {OpenCV FileStorage YAML, ROS1 camera_info YAML, ROS2
  YAML, kalibr camchain (single cam), plain JSON} → auto-detected, parsed, preview
  as C-20 (fx fy cx cy, dist coeffs, resolution).
- **AC2:** Export to any other format; round-trip property tests (parse∘emit = id)
  for all pairs; kalibr import handles radtan + equidistant.
- **AC3:** Fully client-side; works offline once loaded.
- **EC:** OpenCV YAML `%YAML:1.0` directive + `!!opencv-matrix` tags (js-yaml needs
  custom schema — known gotcha, test it against a fixture corpus collected from
  real OpenCV/ROS/kalibr outputs *before* writing the parser); missing resolution
  (prompt inline); 5 vs 8 vs 12 dist coeffs; P-matrix vs K-matrix confusion in
  camera_info (document the difference inline via C-14 — this is a daily Stack
  Overflow question; answering it in-UI is free SEO).
- **SM:** ≥ 500 conversions/month by day 90; top-3 Google for two conversion
  queries.

### 10.5 F-05 Detector Parameter Playground

> As an engineer with a failing detection, I want to tune DetectorParameters
> against my actual image and see why candidates are rejected, so that I can fix
> detection in minutes instead of days.

- **AC1:** Image via upload (C-08), webcam still, or handoff from Live (PX-8);
  detection re-runs ≤ 300 ms after any parameter change (720p-downscaled
  processing, worker; PX-10).
- **AC2:** Overlays toggleable: detected (`--det-accepted`), **rejected candidates
  (`--det-rejected`)** — the feature's raison d'être — with per-candidate
  rejection-stage hint where derivable (size filter, polygonal approx, bit
  extraction fail / Hamming fail — staged pipeline re-run to attribute; labeled
  heuristic per PX-9).
- **AC3:** Parameters grouped (Thresholding / Contour filtering / Corner refinement
  / Bit extraction) with plain-language tooltips + sane-range sliders; [Reset to
  defaults]; diff-from-default badge per group.
- **AC4:** Export current params via C-18: Python (cv2), C++, `aruco_ros` YAML —
  copy-paste runnable, with PX-9 assumption header comments.
- **EC:** huge images (auto-downscale, banner with scale factor — parameter values
  like `minMarkerPerimeterRate` are relative so remain valid); zero candidates at
  any setting (C-13: "image likely has no quad structures — check dictionary/print"
  + [Run quality report]); pathological params freezing detection (worker timeout
  2 s → auto-revert + C-17 toast).
- **SM:** ≥ 30% of sessions export parameters; becomes the canonical community
  answer link for "aruco not detecting".

### 10.6 F-06 Runtime Config Exporter

> As a ROS engineer, I want board geometry + detection config in my runtime's
> format, so that integration is paste-paste-run.

- **AC1:** For any generated board/marker: emit `aruco_ros` marker config,
  `apriltag_ros` tags.yaml (for AprilTag families), generic JSON board geometry
  (object points per ID), and a Python snippet (cv2) with the exact dict/size/
  params, embedding the active calibration profile if loaded (PX-3/PX-8).
- **AC2:** Snippets are tested: CI runs the emitted Python against a rendered image
  of the same board and asserts detection — **the product tests its own outputs.**
- **EC:** AprilTag family naming differences (16h5 vs tag16h5) handled per
  consumer; ChArUco boards exported with both charuco and plain-aruco
  interpretations documented via C-14.
- **SM:** ≥ 25% of board downloads accompanied by a config export.

### 10.7 F-07 Print Verification (a: ruler, b: webcam measure)

> As a user, I want to confirm my printed marker is dimensionally accurate, so that
> pose estimates aren't silently scaled.

- **AC1 (a):** Every PDF/SVG includes a 100 mm bar + text; snapshot tests updated;
  bar lies **outside cut paths** in .lbrn2/DXF (must not get cut!).
- **AC2 (b):** In Live, "Verify print size" mode: user enters nominal size, holds
  print flat and frontal; tool computes measured size via marker-relative geometry
  + calibration profile (required for absolute measure; without it, offers ratio
  check against the printed ruler bar in the same view, per PX-3 explicit
  degradation), reports measured vs nominal with tolerance verdict (±1%) via C-10.
- **EC:** curved paper (detect via corner non-planarity → "Flatten the sheet");
  oblique view > 20° (reject with C-05 guidance: "Hold the print facing the camera
  squarely").
- **SM:** Print-verification used in ≥ 15% of Live sessions in week 1 after launch.

### 10.8 F-08 Dictionary Advisor

> As a newcomer, I want a recommendation for which dictionary to use, so that I
> don't discover at 8 m range that 7×7 was wrong.

- **AC1:** Three inputs (how many unique markers, max distance + camera preset,
  occlusion/error tolerance) → ranked recommendation as C-20 with one-paragraph
  rationale (inter-marker Hamming min distance via existing endpoint, bits/size
  trade-off via F-03 math).
- **AC2:** "Apply" sets the Generate form (PX-8 handoff).
- **EC:** > 1000 markers (recommend custom dictionary, link to future feature;
  honest "not supported yet" per PX-9 + [Tell us you need this] feedback action).
- **SM:** ≥ 15% of generator sessions touch the advisor.

### 10.9 F-12 Nested Landing-Pad Designer

> As a drone engineer, I want a landing pad detectable from 30 m down to 0.3 m, so
> that precision landing never loses lock during descent.

- **AC1:** Configurator (C-07 flow): outer marker size, inner marker (placed in a
  white cell or center cutout per recursive-marker convention), dictionary/IDs
  distinct; live altitude-coverage chart (from F-03 math) showing detection
  envelope of each marker with overlap highlighted; warn on coverage gap with the
  specific altitude band named (PX-2).
- **AC2:** Exports via C-18: PDF (tiled multi-page for large pads, ≥ 10 mm overlap
  + alignment marks), SVG, .lbrn2, DXF; config snippet for PX4 precision landing /
  ArUco-based ROS landers with both IDs + sizes (via F-06).
- **EC:** pads larger than printable (tiling with assembly marks + C-14 assembly
  note); inner marker too small to fabricate (warn vs printer DPI / laser kerf with
  [Resize] action).
- **SM:** Becomes the top "drone landing pad aruco" search result; ≥ 50
  downloads/month.

---

## 11. Calibration and Validation System (Deep Dive)

The flagship (F-01) and the fullest expression of the PXA: every §2.2 principle has
a concrete instrument here. Scope verdict: build all nine subsystems below — but
recognize they are not nine features. They are one feature (Calibration Studio)
with a real-time feedback layer (frame gates, instruction fusion, quotas) that F-02
and F-05 reuse. Build the feedback layer once.

### 11.1 Initial calibration flow

- **Why it matters:** The #1 documented calibration failure is bad input data,
  discovered only after the solve (or worse, in the field). A guided flow
  front-loads data quality.
- **How it works:** Wizard (C-07): (1) choose/print a ChArUco board — deep-linked
  from Generate with board params auto-filled (PX-8, source-labeled), [Print board]
  button, implausibility warning if board spec doesn't suit camera FOV (PX-9);
  (2) choose source — webcam or upload (first-class peers, PX-4); (3) guided
  capture to fill quality quotas; (4) solve; (5) diagnose; (6) export.
- **UX flow:** Stepper across the canvas top (`Board → Capture → Solve → Results`).
  User can never reach Solve with insufficient data; the Solve button states what's
  missing ("Need 4 more tilted views").
- **Technical implementation:** Board spec object `{dict, squaresX, squaresY,
  squareMm, markerMm}` shared with generator state. Per-frame: `detectMarkers` →
  `interpolateCornersCharuco` in worker; accepted frames store corner arrays +
  board pose — **not full images** (memory + privacy), unless the user opts into
  downloading a capture bundle. Solve: `calibrateCameraCharuco` in worker
  (O(seconds) for ≤ 40 frames at 1080p — acceptable with C-12 long-tier progress).

### 11.2 Camera positioning validation

- **Why:** Distortion coefficients are unconstrained unless corners visit image
  edges/corners; pose diversity (tilt) is required to decouple focal length from
  distance. Engineers don't know this; the tool must enforce it — and teach the
  reason via C-14 (PX-12).
- **How:** Maintain a **3×3 coverage grid** (count of accepted corner observations
  per cell) and a **pose-diversity score** (bucketed board rotations: left/right/
  up/down tilt ≥ 20°, near, far). Capture completes only when all buckets ≥
  threshold.
- **UX:** Semi-transparent 3×3 overlay on live preview; cells fill as covered
  (C-15). A pose checklist sidebar with six icons (↖ tilt-left ✓, near ✓, far …)
  that check off. Prompt text via C-05: "Move the board to the top-right corner of
  the frame."
- **Technical:** Coverage = histogram of charuco corner pixel coords. Tilt from
  board rvec (Rodrigues → Euler); near/far from tvec.z relative to board size.

### 11.3 Webcam orientation guidance

- **Why:** Users point cameras at steep angles or upside-down boards and get
  garbage or mirrored confusion.
- **How:** Live readout of board normal vs optical axis; warn > 60° via C-06 ("Too
  oblique — corner accuracy degrades"); detect front cameras and un-mirror the
  *processing* path while keeping the mirrored *display* (users expect mirror
  view).
- **Technical:** Angle from rvec. Mirroring: render preview with CSS `scaleX(-1)`
  only; feed raw frames to the worker. C-05 instructions are *flipped to match the
  displayed view* so "move right" means the user's right — instruction-frame
  correctness is a PX-1 detail that separates instruments from demos.

### 11.4 Marker visibility validation

- **Why:** Partially detected boards (glare, occlusion by hands, cropped board)
  yield few corners and skew the solve.
- **How:** Per-frame metric: detected charuco corners / total. Accept frame only if
  ≥ 60% (configurable in Expert mode). Show live count "31/44 corners".
- **UX:** Detected corners drawn as green dots; the *undetected* board region
  subtly red-tinted so the user literally sees the glare patch or their thumb —
  show, don't tell (PX-2 applied to space).

### 11.5 Distance validation

- **Why:** All-near frames → distortion overfit; all-far frames → noisy corners.
- **How:** Require frames in ≥ 2 distance buckets (board height 25–50% and 50–80%
  of frame height). Reject frames where board < 15% of frame ("Move closer —
  corners too small for subpixel accuracy" via C-05).
- **Technical:** Board apparent size from corner bounding box; thresholds in
  board-relative units so they generalize across cameras.

### 11.6 Lighting validation

- **Why:** Blur and glare are the silent killers; OpenCV detects *something* and
  the user assumes it's fine — the PX-9 anti-pattern this product exists to end.
- **How:** Per-frame gates before acceptance: sharpness (variance of Laplacian over
  board ROI > threshold, auto-baselined from the best recent frame), exposure
  (histogram clipping < 2% pixels at 0/255 within board ROI), glare (saturated blob
  inside board ROI → "Tilt the board away from the light").
- **UX:** Single traffic-light "Frame quality" chip (C-06) with the failing reason
  as plain text. Never show raw numbers outside Expert mode (PX-7).

### 11.7 Real-time setup feedback (instruction fusion)

- **Why:** This is the product's answer to kalibr's "capture a bag, wait, despair"
  loop. Feedback latency must be < 200 ms to feel live (PX-10).
- **How:** All §11.2–11.6 signals computed per processed frame (~10–15 fps at
  960×540 processing resolution; display stays native), fused into one **current
  instruction** rendered by C-05 (PX-1). Priority order (stability > quality >
  positioning): stream health → frame quality (can't use bad frames anywhere) →
  visibility → distance → coverage → pose diversity. One instruction at a time —
  never a list. Display-time throttle ≥ 1.5 s per instruction prevents flicker;
  quota progress acknowledges via C-15 fills, not verbal praise.
- **Technical:** requestAnimationFrame-driven pipeline with frame dropping (process
  latest, skip backlog — §13.2); full-resolution frames captured only on
  acceptance.

### 11.8 Confidence scoring

- **Why:** "RMS 0.42 px" means nothing to most users; the industry pain is *not
  knowing if a calibration is trustworthy* (PX-11).
- **How:** Composite **Calibration Confidence (0–100)** via C-10 from: RMS
  reprojection error (scaled by resolution), coverage completeness, pose diversity,
  frame count, per-image error consistency (flag outlier frames), and a **held-out
  check** (solve on 80% of frames, report reprojection on the remaining 20% — a
  poor man's cross-validation that catches overfitting; the methodology's
  credibility anchor, published in Learn per PX-9). Display tiers per §6.8: ≥ 90
  "Production-ready", 70–89 "Good — usable, see suggestions", < 70 "Recapture
  recommended" with the dominant cause named.
- **How it should work (UX):** Score is the results hero (`--text-hero`, mono).
  Per-image reprojection bar chart; clicking an outlier frame shows its thumbnail
  (C-19) + "Remove & re-solve" — one-click data cleaning that makes users *feel*
  the score respond, which is how trust in the score itself forms. Every factor row
  carries its fix-it action (PX-4): low coverage → "Capture 5 frames near image
  corners" returns to Capture with that C-15 cell highlighted.
- **Technical:** All inputs already exist post-solve; held-out split is one extra
  solve call. Tier thresholds in `vision-core/confidence.js` (§6.8).

### 11.9 Automated setup checks (pre-flight)

- **Why:** Eliminate the five minutes of "why is nothing happening" (PX-4 applied
  preemptively).
- **How:** On entering any camera workspace, run: camera permission granted? stream
  alive? resolution ≥ 720p? frame rate ≥ 15? OpenCV.js loaded? board spec selected?
  Each failing item renders as a C-13 row with a fix-it action (e.g., resolution
  low → "Switch camera" dropdown). Passes silently in < 1 s when healthy — checks
  that pass are not news (instrument calm).
- **Technical:** `navigator.permissions.query`, MediaStreamTrack
  settings/capabilities, wasm-ready promise. Reused verbatim by F-02 and F-05.

---

## 12. Webcam and Camera Experience

One shared **CameraManager** module + C-04 powers Calibration Studio, Live
Validator, and Playground stills. Screens below are wireframe-level specs annotated
with component IDs.

### 12.1 First-time onboarding (permission priming)

```
┌─ C-04 pre-permission state ──────────────────┐
│  📷  This tool uses your camera — locally.   │
│                                              │
│  Frames are processed in your browser with   │
│  OpenCV (WebAssembly). Nothing is uploaded.  │
│  [How this works]                ← PX-6 link │
│                                              │
│     [ Enable camera ]   [ Upload images      │
│           ↑ primary       instead ] ← C-08   │
└──────────────────────────────────────────────┘
```

- Request `getUserMedia` only on button click (browsers punish on-load prompts).
- The privacy line is load-bearing (A3/PX-6) — engineers in industrial settings
  often *cannot* upload imagery; say it everywhere a camera appears.
- "Upload instead" is a first-class path, not a fallback link: CI cameras, GigE
  rigs, and drones can't be a webcam; their users upload frame sets.

### 12.2 Camera selection

```
┌ Camera: [ FaceTime HD ▾ ]  Res: [1920×1080 ▾]  ● Live │
```

- Dropdown from `enumerateDevices` (labels appear post-permission; re-enumerate
  then).
- Resolution picker shows actual **negotiated** values from track settings, not
  requested ones (PX-9 — never display requested as actual). Persist last
  device+res per workspace in localStorage (PX-8); camera StatusChip (C-02)
  reflects selection globally.
- External/UVC cameras are the common real case for robotics users — explicit
  test-matrix item.

### 12.3 Orientation guidance and live preview (capture screen)

```
┌ C-03 canvas ───────────────────────────────────┐
│ ┌ C-04 video + overlay ─────────────────────┐  │
│ │   ┌grid┬────┬────┐   31/44 corners        │  │
│ │   │ ✓  │ ✓  │    │   [green dots on       │  │
│ │   ├────┼────┼────┤    detected corners;   │  │
│ │   │ ✓  │ ●  │    │    red tint on         │  │
│ │   └────┴────┴────┘    undetected region]  │  │
│ │                       proc 14 fps         │  │
│ └───────────────────────────────────────────┘  │
│  C-05 ▶ "Move the board to the right edge"     │
│  C-06 ● Frame quality: Good                    │
│  C-15 Captured 14 · Coverage 6/9 · Poses 4/6   │
│  C-19 [▣][▣][▣][▣]…           [Capture ⎵]      │
└────────────────────────────────────────────────┘
```

- Mirrored display for front cameras, raw frames to processing, instructions
  flipped to match the displayed view (§11.3).
- Exactly one instruction line; quality chip; three progress counters.

### 12.4 Setup wizard (Calibration Studio stepper, C-07)

1. **Board** — pick recently generated board (auto-filled, source-labeled per PX-8)
   or enter spec; [Print board] button; warning if board spec implausible vs camera
   FOV (PX-9).
2. **Capture** — screen 12.3 with auto-capture: when a frame passes all gates *and*
   adds new coverage/pose value, capture fires with shutter flash (120 ms) + tick
   sound (toggleable; reduced-motion swaps both for a counter increment, §6.9).
   Manual capture button + `Space` always available. C-19 thumbnail strip of
   accepted frames with per-frame delete (single-level undo).
3. **Solve** — C-12 long tier: determinate progress with stage labels ("Optimizing
   23 views…"), runs in worker, cancellable.
4. **Results** — confidence score hero (C-10: number, tier, factors with fix-its),
   coverage heatmap, per-image error bars, distortion visualization (warped grid),
   camera matrix table (C-20: mono, copy icon, full precision on copy), C-19 with
   outlier flags, C-18 export row `[OpenCV YAML] [ROS camera_info] [ROS2] [JSON]
   [Copy Python]`, [Save profile] → calibration StatusChip (C-02) visibly updates —
   the PX-3 moment: the bench remembers. C-11 success confirmation with handoff
   "Export for ROS ›".

### 12.5 Troubleshooting flow (auto-detected decision tree, rendered as C-13)

| Symptom (auto-detected) | FixItPanel content (cause-ranked; lateral exit last) |
|---|---|
| Permission denied | Browser-specific re-enable steps (detect UA) · [Upload instead] |
| No devices | "No camera found." Plug in a UVC webcam · [Upload instead] |
| Stream alive but black frames | "Camera in use by another app?" (common on Windows) · [Retry] · [Switch camera] |
| No board detected > 5 s while stream healthy | Checklist: right dictionary? whole board visible? enough light? · [Open this frame in Debug ›] |
| Detection works but frames always rejected | Names the persistently failing gate: "All frames blurry — clean lens / add light / lock focus" |
| iOS Safari quirks (stream pause on tab switch, constraint failures) | Auto-resume handler + reduced default constraints on iOS; toast on resume |

### 12.6 Error recovery (no lost work — §2.3 commitments)

- Capture session state (accepted corner sets + board spec) autosaves to
  localStorage on every capture; reload offers "Resume session (14 frames, today
  14:32) · [Start fresh]" — restoration labeled so it never feels like a bug (A-7).
- Worker crash (wasm OOM): auto-restart worker; dataset intact (corners live on
  main thread); C-17 toast "Recovered — continue capturing."
- Device unplug mid-capture: pause, offer device re-pick via C-02 popover, dataset
  intact.

---

## 13. Technical Architecture

### 13.1 Core services (target state)

```
Browser (compute platform + experience platform)
├── static/css/tokens.css          §6 design tokens (single source of visual truth)
├── static/js/components/          §7 C-01…C-20, vanilla ES modules, JSDoc-typed
├── static/js/vision/  (vision-core — the platform investment)
│   ├── opencv-loader.js     lazy wasm load, version-pinned, integrity hash,
│   │                        byte-honest C-12 loading state
│   ├── vision.worker.js     all cv ops; message protocol below
│   ├── camera-manager.js    getUserMedia, device enum, health, iOS quirks
│   ├── frame-gates.js       §11 gates (sharpness/exposure/coverage/pose)
│   ├── confidence.js        §6.8 tier thresholds + §11.8 scoring
│   │                        (UI never hardcodes either)
│   └── formats/             F-04 calibration file adapters (shared by F-01/F-06)
├── static/js/workspaces/    one module per §5.1 workspace
└── localStorage: profiles, sessions, settings (versioned schemas, §13.4)

Flask (unchanged role: generation & fabrication)
├── web_bp / calibration_bp / advanced_bp  (existing)
├── exporters + lightburn (existing; + ruler F-07a; + runtime configs F-06)
└── NO new stateful features; DB pattern-storage frozen, metrics removed (F-10)
```

**Opinionated calls (binding; push back in a PR description if context changes):**

1. Do **not** adopt React/Vue. The existing vanilla-JS module pattern
   (`static/js/pages/*.js`, `core/state.js`) is working, agents navigate it well,
   and a framework migration is a multi-week zero-user-value risk. Add JSDoc types
   + `// @ts-check` for agent safety instead. §7 components are deliberately
   framework-agnostic.
2. Do **not** port generation to the client. Server generation feeds the export
   moat (reportlab/ezdxf can't run in-browser) and is already done.
3. **Do** treat `vision-core/` and `components/` as libraries with their own unit
   tests (vision-core under Node with a wasm-capable harness) — five features and
   every screen, respectively, depend on them.

### 13.2 Processing pipeline (camera workspaces)

```
camera → <video> → rAF tick → (drop if worker busy) → downscale to ≤960px
  → transferable ImageBitmap → worker: cvt gray → detect/interpolate
  → gates (§11) → result msg {corners, ids, pose, gateReport, timings}
  → main: overlay canvas draw + instruction fusion (§11.7)
  → C-05/C-06/C-15 updates + (auto)capture decision
```

- **Worker protocol:** request/response with monotonic frame ids; worker processes
  *latest only* (explicit backpressure — never queue frames).
- **Mat hygiene:** every OpenCV.js Mat allocation paired with `.delete()` in
  try/finally; helper `withMats()` wrapper enforced by convention + a leak counter
  in the diagnostics drawer (wasm heap size trend, C-16).
- Solve operations (`calibrateCameraCharuco`, `stereoCalibrate`) run in the same
  worker with progress messages; cancellable by worker termination + restart
  (state lives on main thread — §12.6).

### 13.3 State management

- Per-workspace state object (plain JS, JSON-serializable, versioned
  `schemaVersion`) registered with a tiny global store (extend existing
  `state.js`). One pattern, five UX features (PX-8): (a) localStorage persistence,
  (b) restoration with "Resumed from…" labeling, (c) handoff slices ("Calibrate
  with this board" = copy board slice from generate state to calibrate state),
  (d) URL sharing (F-17) by compressing the same object, (e) Expert-mode JSON
  editing.
- Cross-cutting state (active camera, active calibration profile, active board)
  lives in the global store; status chips (C-02) are its only UI (PX-3).

### 13.4 Data model (client-side)

```js
CalibrationProfile {
  schemaVersion, id, name, createdAt,
  camera: { deviceLabel, resolution },
  model: "OPENCV4"|"OPENCV8"|"FISHEYE",
  K: number[9], dist: number[], rms, perImageErrors: number[],
  confidence: { score, coverage, poseDiversity, heldOutError },
  boardSpec: { dict, squaresX, squaresY, squareMm, markerMm }
}
CaptureSession { schemaVersion, boardSpec,
                 frames: [{cornerIds, corners, pose, gateReport}] }
BoardSpec / MarkerConfig — shared with Generate forms (single source of truth)
```

Server-side: no new tables. Remove `DetectionMetric` writes (F-10). Pattern storage
stays read-only-frozen until a real need appears.

### 13.5 Performance budgets (PX-10 made testable; enforced as ACs)

- OpenCV.js: lazy-load only on camera/debug workspaces; byte-honest loading state
  ("Loading vision engine, ~8 MB, cached after first use"); cache immutable.
  Investigate the custom-build path (opencv.js built with only
  aruco+calib3d+imgproc, roughly halving size) as a fast-follow, not a blocker.
- Live processing ≥ 10 fps at 960 px on a 2020 mid-range laptop; UI thread ≥ 30 fps
  always (worker isolation guarantees this if respected).
- Parameter-change recompute < 300 ms (F-05). Calibration solve ≤ 15 s for 40
  frames; progress feedback ≤ 1 s granularity.
- Server endpoints unchanged: p95 < 2 s on Vercel.
- All measured live in the diagnostics drawer (C-16).

### 13.6 Extensibility strategy (built for AI agents)

- **Tool registry:** each workspace/mode = one manifest (`route, navLabel, module,
  requiredCapabilities: ["camera","wasm"]`) + one ES module + one optional Flask
  blueprint. Adding a tool touches zero shared files except the registry. This is
  the highest-leverage decision for AI-agent development: it makes "add tool X" a
  parallel-safe, low-context task.
- **Experience registry parallel:** new tools compose §7 components and §6 tokens
  only; the §17 checklists are the enforcement mechanism.
- Keep `AI_NAVIGATION.xml` + per-file headers current (existing convention) — they
  are the agent context budget.
- Golden-file tests for every export format (exists — extend to F-06 configs);
  emitted-code execution tests (F-06 AC2) as the flagship QA pattern.

---

## 14. Development Plan

Sequencing principles: (1) ship user value while the platform layers (F-90
experience, F-00 vision) land in parallel; (2) the flagship (Calibration Studio)
arrives only after its riskiest dependency (OpenCV.js viability) is proven by a
smaller feature (Live Validator); (3) **every milestone ends with a PXA gate** —
the §17 checklists run against everything shipped in that milestone.

### M0 — Foundation & quick wins (weeks 1–2)

- **Features:** F-90, F-10, F-07a, F-03, F-04, F-08, F-09, F-11.
- **Order of implementation:** F-10 first (less code = cleaner agent context for
  everything after) → F-90 tokens + shell + IA cutover → F-03 and F-04 in parallel
  sessions (independent; built as the first consumers of C-03/C-09/C-20, which
  pressure-tests the components) → F-08 (needs F-03 math) → F-09, F-07a, F-11 in
  any order.
- **Reasoning behind sequencing:** all are independent of the risky wasm work; the
  IA cutover (§5.1) and design system must precede camera features; quick wins make
  the new shell immediately useful rather than a re-skin; converter/calculator
  create the SEO beachhead and restore trust that "Validation"/"Calibration"
  surfaces do something.
- **Risks:** OpenCV YAML parsing quirks in F-04 (mitigate: fixture corpus from real
  OpenCV/ROS/kalibr outputs *before* writing the parser); IA cutover breaking
  existing `test_ui_pages`/`test_navigation` (mitigate: update tests in the same
  PRs; redirects from old routes).
- **Validation criteria / Definition of done:** `make validate` green; §17 PXA gate
  passed on all shipped screens; F-04 round-trip property tests; F-03 math
  cross-checked against 3 hand-computed cases; old URLs redirect; CHANGELOG +
  AI_NAVIGATION.xml updated; deployed to Vercel.

### M1 — Vision platform spike + Live Validator (weeks 2–4)

- **Features:** F-00, F-02 (incl. demo mode), §12 camera experience (CameraManager,
  permission primer, troubleshooting tree), C-02 chips live, C-04/C-05/C-06/C-16
  implemented, homepage v2 (§5.5).
- **Order:** opencv-loader + worker echo test → **session-1 verification:
  aruco/charuco APIs present in the stock opencv.js build** (the single biggest
  unknown in the entire plan; if absent, the custom build pipeline moves from
  fast-follow to M1 task) → camera-manager (browser/device test matrix:
  Chrome/Edge/Firefox/Safari × macOS/Windows + iOS Safari + Android Chrome + one
  external UVC camera) → detect-in-worker → C-04 overlay → gates subset (sharpness
  + exposure only) → C-06 verdicts → troubleshooting flows → demo mode → homepage.
- **Reasoning:** F-02 is the smallest feature that exercises every risky component
  of F-00 (wasm load, worker protocol, camera quirks, overlay perf). If OpenCV.js
  underperforms, we learn it at week 3, not inside the 8-session flagship. Demo
  mode + homepage convert the platform work into A-1 acquisition immediately.
- **Risks:** wasm size/perf on low-end devices (budget gate §13.5; fallback = lower
  processing resolution, surfaced per §2.3 visibility rule); browser camera API
  fragmentation (fixed test matrix; C-08 upload as universal lateral exit per
  PX-4); aruco module availability (above).
- **Validation / DoD:** F-02 ACs as manual test script + automated unit tests for
  vision-core; **network-silence automated test** (NFR-1/PX-6); §17 gate including
  accessibility pass on camera screens (aria-live guidance, keyboard capture); demo
  video recorded (doubles as launch content).

### M2 — Calibration Studio (weeks 4–8)

- **Features:** F-01 complete (§11 all nine subsystems), profile shelf +
  calibration chip, C-07/C-10/C-15/C-19 implemented, F-04 integration for exports,
  Learn methodology page for confidence scoring (PX-9).
- **Order:** BoardSpec handoff from Generate → **upload path first** (no camera
  variability; validates solver + §11.8 against golden image sets with known-good
  intrinsics from a real camera, asserting K within tolerance) → webcam capture
  with gates → coverage/pose quotas + instruction fusion → auto-capture →
  confidence scoring (held-out split last) → results UI → exports → session
  resume.
- **Reasoning (upload-first):** decouples solver correctness from capture UX;
  yields a testable milestone (ΔK < 1% vs OpenCV Python on identical frames) before
  the experience layer's variability enters the picture.
- **Risks:** `calibrateCameraCharuco` availability/perf in opencv.js (mitigation:
  proven during M1 spike scope by calling it on canned data); UX overwhelm
  (mitigation: PX-1 enforcement + usability test with 2 external engineers before
  launch — calendar this at week 6).
- **Validation / DoD:** F-01 AC1–AC6; calibration of a real webcam cross-checked
  against OpenCV Python on the same frame set (ΔK < 1%, Δdist coeffs sane); §17
  gate; confidence methodology published in Learn; Show-HN-ready.

### M3 — Debug & integrate (weeks 8–12)

- **Features:** F-05 (playground), F-06 (runtime configs + emitted-code execution
  tests), F-07b (print measure), F-12 (landing pads), F-17 if time (share links).
- **Order:** F-05 (reuses M1 infra most heavily) → F-06 → F-12 → F-07b.
- **Risks:** rejection-stage attribution in F-05 may be approximate (acceptable —
  labeled heuristic per PX-9); F-06 snippet matrix grows combinatorially
  (constrain: Python + aruco_ros + apriltag_ros only at launch).
- **Validation / DoD:** all ACs; §17 gate; launch checklist executed (below).

### Launch checklist (end of M3)

Demo video per flagship feature · Show HN + r/robotics + r/computervision posts ·
3 SEO articles (marker size guide; camera_info P-vs-K explainer; "marker not
detecting" guide linking the playground) · privacy-friendly analytics
(plausible/umami) for the §16 metrics · feedback link in the diagnostics drawer
(C-16).

---

## 15. Emerging Opportunities (Strategic Watchlist)

- **WASM-first compute** is the architectural unlock already exploited (F-00); the
  custom-build path and threads/SIMD builds are the follow-on performance levers.
- **Markers in robot-learning pipelines:** imitation-learning and sim2real teams
  use ArUco for ground-truth poses on grippers/objects. F-20 (ground-truth rig
  designer: marker cubes/wands with known geometry + pose-recovery config) targets
  a fast-growing audience, and the fabrication moat applies (laser-cut cubes).
- **Synthetic detection benchmarking** (F-14): the existing `validation.py`
  distortion/occlusion synthesis extends to rendered pose/blur/noise/lighting
  sweeps → a "detection robustness report" for a chosen dictionary/size.
  Lightweight, unique, citable.
- **VLM-era positioning:** foundation models are eating open-vocabulary detection,
  but they cannot do millimeter-accurate metric pose — fiducials remain the bridge
  between VLM scene understanding and metric control. A "when do you still need
  markers in 2026" Learn article is cheap content marketing this audience would
  genuinely share.
- **Hand-eye calibration** (F-19): guided capture checklist + `cv2.calibrateHandEye`
  on uploaded pose pairs. Every robot-arm team does this; tooling is dire.

---

## 16. Business Requirements Document

### 16.1 Objectives

| # | Objective | Measure (day 90) |
|---|---|---|
| O1 | Become a recurring-use tool, not a one-shot generator | ≥ 25% of weekly actives are returning users (A-7 loop) |
| O2 | Own the "browser camera calibration" category | ≥ 100 completed calibration solves/week; top-5 ranking for "online camera calibration charuco" |
| O3 | Close the generate→verify loop | ≥ 30% of marker-download sessions also use Live or Debug (PX-5 efficacy) |
| O4 | Coherent experience, measurably | ≥ 2-workspace sessions ≥ 35%; handoff-button CTR ≥ 20% on success states |
| O5 | Maintain AI-agent development velocity | `make validate` < 5 min; every feature lands with tests + §17 gate; zero regressions shipped to the four export moat formats |
| O6 | Zero marginal serving cost growth | Server compute flat as camera-tool usage grows (all client-side) |

### 16.2 Stakeholders

Solo founder (product/review/deploy) · AI coding agents (implementation — this
document is their spec) · End users A-1…A-7 (§4): robotics/ROS engineers, drone
developers, manufacturing automation engineers, researchers/students, production
operators · Indirect: laser-cutting community (LightBurn forums — existing
distribution channel worth nurturing).

### 16.3 Functional requirements

- **FR-1** Generate markers/boards/tags in all current formats (existing —
  protected by regression tests).
- **FR-2** Browser camera calibration with guided capture, quality gates,
  confidence scoring per the §2.3 contract, multi-format export (F-01, §11).
- **FR-3** Live webcam marker detection with quality verdicts and optional pose
  (F-02).
- **FR-4** Marker size/distance computation, standalone + inline (F-03).
- **FR-5** Calibration file conversion across OpenCV/ROS1/ROS2/kalibr/JSON (F-04).
- **FR-6** Interactive detector parameter tuning with rejected-candidate
  visualization and parameter export (F-05).
- **FR-7** Runtime configuration + code snippet export, execution-tested (F-06).
- **FR-8** Print dimensional verification, passive (ruler) + active (webcam)
  (F-07).
- **FR-9** Dictionary advisory (F-08).
- **FR-10** Validation engine surfaced in UI (F-09).
- **FR-11** Local profile persistence + status chips (no accounts).
- **FR-12** Nested landing-pad design + tiled export (F-12).
- **FR-13** The PXA itself: shell, chips, handoff graph, three-layer disclosure,
  Expert mode, diagnostics drawer (F-90 + cross-cutting).

### 16.4 Non-functional requirements

- **NFR-1 Privacy:** camera frames and calibration imagery never transmitted;
  asserted by automated test; stated in UI at every camera touchpoint (PX-6).
- **NFR-2 Performance:** budgets of §13.5 are acceptance criteria (PX-10).
- **NFR-3 Compatibility:** Chrome/Edge/Firefox/Safari current-2; iOS Safari +
  Android Chrome for Live (Studio: best-effort mobile per §6.11, desktop-first).
- **NFR-4 Offline-tolerant:** client tools survive connection loss mid-session
  (full PWA is Phase 3, F-16).
- **NFR-5 Accuracy:** calibration results within 1% of OpenCV Python reference on
  identical inputs; exports load in target tools (cv2, ROS) verified by fixture
  tests.
- **NFR-6 Accessibility:** WCAG 2.2 AA per §6.10, gated by §17.6.
- **NFR-7 Maintainability:** repo conventions (AI_NAVIGATION.xml, file headers,
  `make validate`) upheld; vision-core and components unit-tested independently of
  UI; token/component discipline (§17.2).
- **NFR-8 Cost:** Vercel hobby/pro tier sufficient at 10× current traffic.

### 16.5 Success metrics (instrument at M1 with privacy-friendly analytics)

Activation: % of new visitors completing one core action
(download/detect/convert/solve) ≥ 40% · Loop closure: O3 + O4 · Calibration funnel:
start→solve ≥ 60%, solve→export ≥ 40% · A-1 demo funnel: ≥ 50% of demo starts reach
detection · Retention: O1 · Reach: organic search impressions for 8 target queries,
trend ↑.

### 16.6 Risks and assumptions

| Risk | L | I | Mitigation |
|---|---|---|---|
| Stock opencv.js build lacks aruco/charuco APIs needed | M | H | Verify in M1 session 1; custom build pipeline as contingency (documented, scripted, cached) |
| Browser/camera fragmentation burns schedule | H | M | Fixed test matrix; upload path (C-08) as universal fallback for every camera feature (PX-4) |
| Solo-founder review bottleneck | M | M | Tool-registry isolation (§13.6) keeps changes small and parallel; ACs-as-tests reduce review surface |
| Calibration accuracy doubts ("toy tool") | M | H | Publish the Python cross-validation methodology + reference comparisons (PX-9); Expert-mode transparency |
| Scope creep toward platform (datasets, training) | M | H | A4 written down; any feature outside the marker/calibration loop requires explicit founder decision against this doc; §17 rule: no §9.5 row, no feature |
| Experience system slows early velocity | M | M | F-90 is deliberately small (core components only in M0); components pay back by M2; §17 checklists are fast to run |
| Design drift across agent sessions | M | H | §6 tokens-only rule + §7 components-only rule + §17.7 consistency checklist — this risk is *why the PXA exists* |
| SEO competitors (calib.io content) | M | L | Tools-as-content (calculator/converter/playground) outrank articles for tool-intent queries |

**Assumptions:** A1–A5 (§0); ChArUco remains the calibration standard (safe:
OpenCV-official guidance); engineers will trust browser-local compute once privacy
is demonstrated (PX-6 mechanisms; validated by similar local-first dev tools);
dark-first is acceptable to the audience (light theme exists as escape hatch).

---

## 17. Meta-System for Future AI Development

Addressed directly to future Claude Code sessions. This is the enforcement layer
that keeps independent sessions building one product.

### 17.1 The conformance rule (binding)

> **Any feature added to this roadmap must map to:**
> 1. a user archetype (§4) — who is this for, in which loop step;
> 2. a workflow (§5.6) — task, flow, or loop edge, and its handoffs (PX-5/PX-8);
> 3. a navigation location (§5.1–5.3) — workspace + mode; new top-level nav is
>    forbidden without founder sign-off (six is the cap);
> 4. a design-system pattern (§6–§7) — composed from existing components, or this
>    document gains the new component first, in the same PR;
> 5. a success metric (§16.5) — measurable, named before implementation;
> 6. a confidence-building mechanism (PX-11/PX-9) — how does this feature increase
>    the user's *justified* confidence; if it outputs certainty, it uses C-10/C-09.
>
> Concretely: **add the §9.5 mapping row and the §10 spec before writing code.**
> No row, no feature.

### 17.2 UX implementation standards

- UI is composed exclusively from §7 components; styling exclusively from §6
  tokens. No raw hex/px in feature code; no one-off variants ("like C-09 but…" =
  extend C-09 in `components/`, update §7 in the same PR).
- Every guided experience routes its imperative through C-05 (PX-1); every
  analytical output through C-09 (PX-2); every certainty claim through C-10
  (PX-11); every failure through C-13 (PX-4); every milestone through C-11 with
  one handoff (PX-5).
- Layer assignment (PX-7) happens at spec time: list which information is Layer
  1/2/3 before implementation. New settings default to Layer 3.
- Copy style: imperative for instructions ("Move the board…"), specific for
  validation ("Size must be positive, in millimeters"), qualified for computed
  claims ("~4.3 m under good conditions"). No exclamation marks in workspaces.
- Numbers users might trust/copy → `--font-data`, right-aligned, qualified display
  precision, full precision on copy (§6.3).

### 17.3 Design review checklist (run per screen before PR)

☐ Tokens only (grep feature CSS for `#`/`px` literals outside tokens.css) ·
☐ One primary action, correct placement (§5.4) · ☐ Semantic color never without
icon+label · ☐ Confidence ramp used only by C-10/verdict tiers · ☐ Mono/UI font
split per §6.3 · ☐ Loading states tiered per C-12 incl. byte-honesty · ☐ Motion
within §6.9 limits + reduced-motion path · ☐ Dark and light themes both render
correctly.

### 17.4 Feature review checklist (run per feature before merge)

☐ §9.5 row exists and is accurate · ☐ §10-style spec exists (user story, ACs, ECs,
SM) · ☐ Conformance rule 1–6 satisfied · ☐ Upstream pre-fills + downstream handoff
implemented and context-complete (PX-8) · ☐ Edge-case table: every row ends in a
user action (PX-4) · ☐ Stated-assumptions list rendered at Layer 2 for computed
outputs (PX-9) · ☐ Latency tiers declared and met (PX-10, verify in C-16) ·
☐ ≥ 1 educational callout if the feature enforces any rule on the user (PX-12) ·
☐ ACs implemented as tests · ☐ AI_NAVIGATION.xml + file headers updated.

### 17.5 Navigation review checklist (run when routes/IA change)

☐ Still six workspaces (new tools = modes, §5.3) · ☐ Old URLs redirect ·
☐ Workspace switch preserves state (PX-8) · ☐ Mode segments visible even when
unused (§5.8 anti-burial) · ☐ Keyboard nav (`g`+key) covers new surface ·
☐ Homepage bench strip still maps intents accurately (§5.5).

### 17.6 Accessibility review checklist (run per screen)

☐ Contrast AA at both themes (automated where possible) · ☐ Keyboard-complete
incl. capture/stepper/drawer · ☐ Focus visible, never suppressed · ☐ C-05 mirrored
to throttled `aria-live` · ☐ Canvas overlays mirrored as Inspector text (§6.10) ·
☐ Audio cues have visual equivalents · ☐ Hit targets ≥ 32 px · ☐ Reduced-motion
honored.

### 17.7 Consistency review checklist (run at each milestone PXA gate)

☐ Same message types use same channels (feedback taxonomy §2.3) · ☐ Verdict tiers
everywhere are exactly three, thresholds from `confidence.js` · ☐ All chips reflect
all state they claim to (PX-3 audit) · ☐ Handoff graph (§2.3) edges all functional;
no workspace has become a leaf · ☐ Identical concepts use identical words across
workspaces (board/profile/frame/verdict glossary — if it drifts, fix the screens,
then record the term here) · ☐ Expert mode adds without relocating (PX-7 audit).

---

## 18. Final Recommendation

**The single most important feature to build next:** the **Calibration Studio
(F-01)** — built *after* the Live Detection Validator proves the OpenCV.js
platform, and built *as the showcase of the PXA*. Calibration is where the market
gap is widest (toys on one side, kalibr/mrcal on the other, nothing in between),
where the existing codebase already has a head start
(`calibrate_camera()` dead code → live flagship), and where "quality feedback in
plain language" is a genuine product insight competitors lack. A calibration tool
that merely computes intrinsics is matchable; a calibration *instrument* that
guides, explains, and justifies confidence is category-defining.

**Top 5 highest-ROI improvements:**
1. **F-90 + F-00** — the twin platforms (experience + vision); everything else
   compounds on them.
2. **F-01 Calibration Studio** — category-defining flagship trust experience.
3. **F-02 Live Detection Validator** — closes the loop, demos the product in 10
   seconds, de-risks the platform, and (via demo mode) is the A-1 acquisition
   engine.
4. **F-05 Detector Parameter Playground** — genuinely novel, the community's
   missing diagnostic tool and its share-object.
5. **F-04 + F-03 (converter + calculator)** — two agent-days for two daily-use
   bookmarks and the SEO beachhead.

**Fastest path to a best-in-class user experience** is codified, not aspirational:
the twelve principles (§2.2), four of which do most of the work — one instruction
at a time (PX-1), verdict-first layering (PX-2), state on the bench (PX-3), and the
confidence contract (PX-11) — enforced by the §17 checklists at every milestone
gate. Consistency, not polish, is what will make this feel like one instrument.

**The roadmap to execute — 30 / 60 / 90 days:**

- **Day 30:** M0 shipped — Workbench shell + IA cutover + dark theme live;
  calculator, converter, advisor, ruler, surfaced validation, diamonds, metrics
  cut. M1 underway: opencv.js viability verified (**decision gate:** perf
  acceptable? aruco APIs present? If not, custom build before proceeding), camera
  manager working, Live Validator in internal use. PXA gate #1 passed.
- **Day 60:** M1 launched publicly (Live Validator + demo mode + homepage v2 +
  status chips). M2 in progress: upload-path calibration solving with accuracy
  verified against the OpenCV Python reference; webcam capture with gates in
  testing; external usability test scheduled. PXA gate #2 passed.
- **Day 90:** Calibration Studio launched with the full confidence contract and
  exports; playground + runtime configs + landing pads landed or in final test
  (M3); Show HN + community launch executed; metrics dashboard live; next-quarter
  decision on Phase 3 (stereo vs PWA vs CLI) made from real usage data. PXA gate
  #3 passed.

**Is the current product sufficient? No — and the gap is now precisely named on
both axes.** Functionally, it is two features away from being the only tool of its
kind: the fabrication moat is real, the calibration gap is real, and the
client-side architecture makes serving it nearly free. Experientially, it is a set
of disconnected pages in a niche full of disconnected pages — and the PXA is the
plan for making twenty tools feel like one instrument. Execute M0–M3 as sequenced,
run the §17 gates without mercy, refuse every feature that lacks a §9.5 row and a
§10 spec, and by day 90 this is not the best marker generator with extra features —
it is the bookmark a robotics engineer opens every integration week, and the only
*instrument* in a niche full of utilities.
