<!--
<ai_agent_documentation>
  <file_meta>
    <name>PHASE_0_PLAN.md</name>
    <version>1.0.0</version>
    <type>phase_plan</type>
    <purpose>Approved Phase 0 operational plan: discovery, baseline, readiness audit, and exit criteria preceding implementation Phase 1 (bridge M0).</purpose>
    <last_updated>2026-06-12</last_updated>
    <maintainer>Solo founder + Claude Code</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Phase 0 Plan — Discovery, Readiness, and Execution Sequencing

**Status:** APPROVED, in execution. **Companions:** `docs/ai/PRODUCT_ROADMAP.md`
(intent), `docs/ai/IMPLEMENTATION_BRIDGE.md` (sequence). Phase 0 produces
knowledge, decisions, and planning artifacts only; the only code it runs is the
existing validation suite (baseline) and the OpenCV.js investigation spike on a
throwaway branch.

## Task sequence

| Task | Content | Depends | Output |
|---|---|---|---|
| T0.1 | Commit this plan + bridge to PR #11; record baseline SHA; founder decision D-α | D-α | Docs on base branch; SHA recorded |
| T0.2 | Baseline: timed `make validate` on tree clean of WIP edits; pre-existing failures dispositioned | T0.1 | `BASELINE_REPORT.md` (D-4) |
| T0.3 | Tier-1 doc sweep: AGENTS.md, ERROR_HANDLING.md, task.md, walkthrough.md, NAVIGATION.md, deployment_checklist.md, CHANGELOG.md, scripts/release.py | ∥ T0.2 | KNOWLEDGE_BASE §Protocols; DECISION_LOG entries |
| T0.4 | Backend sweep: app.py full (CSP → U-7), engine/web contracts + idioms + config inventory | T0.3 | KNOWLEDGE_BASE §Contracts/§Idioms; ARCHITECTURE_NOTES |
| T0.5 | Frontend + tests + CI sweep: seams table, snapshot mechanics, workflows (U-8) | T0.3 ∥ T0.4 | KNOWLEDGE_BASE §Seams/§Tests/§CI |
| T0.6 | AI_NAVIGATION.xml reconciliation: diff vs reality, one correction commit, surprises + bridge patches | T0.4, T0.5 | Updated map (D-3) |
| T0.7 | Spike (bridge P-0.S): opencv.js API availability (U-1), perf (U-2), js-yaml opencv-matrix pre-check (U-4) | T0.1 ∥ others | `SPIKE_OPENCVJS.md` (D-8) verdict |
| T0.8 | Readiness closure: checklist w/ evidence, assumption register, founder decision packet D-α…D-ε, re-estimates | all | D-5/D-6/D-7; exit review |

## Unknowns to resolve (blocking gates noted)

U-1 opencv.js aruco/charuco APIs (blocks M1+) · U-2 wasm calibrateCameraCharuco
perf (blocks M2) · U-4 js-yaml `!!opencv-matrix` (F-04 estimate) · U-7 CSP vs
workers/wasm · U-8 Node in CI · snapshot-blessing mechanics · release.py
versioning semantics · live tasks in docs/ai/task.md · unmerged-branch
divergence (`codex/*`, `feat/phase-*`).

## Founder decisions required

D-α base branch + PR #11 merge timing · D-β branch/PR cadence (proposed:
branch+PR per prompt, no self-merge) · D-γ sandbox allowlist (github.com,
pre-commit cache) · D-δ checkpoint autonomy (proposed: stop-and-wait at CP-n) ·
D-ε scheduling of physical calibration frame capture (needed by M2).

## Conflict-resolution protocol (binding)

1. Code reality wins over all documentation for "what exists".
2. CLAUDE.md + AGENTS.md win for "how to work"; AGENTS.md (more specific) wins
   between them; conflicts logged.
3. AI_NAVIGATION.xml conflicts resolve in code's favor + map-correction entry.
4. Roadmap wins on intent; bridge wins on sequence; fix whichever was wrong in
   the discovering commit.
5. Every conflict → DECISION_LOG.md entry.

## Deliverables

D-1 this plan · D-2 `KNOWLEDGE_BASE.md` (Protocols/Contracts/Idioms/Seams/
Tests/CI, evidence-stamped) · D-3 `ARCHITECTURE_NOTES.md` + corrected
AI_NAVIGATION.xml · D-4 `BASELINE_REPORT.md` · D-5 `DECISION_LOG.md` ·
D-6 assumption register (in D-2) · D-7 completed readiness checklist (in D-5) ·
D-8 `docs/ai/SPIKE_OPENCVJS.md` · D-9 bridge/roadmap patch commits.

## Exit criteria

1. Every readiness-checklist item checked with an evidence link.
2. Baseline green or failures dispositioned in D-4.
3. U-1/U-2 measured; spike verdict GO or GO-WITH-CUSTOM-BUILD (NO-GO →
   founder replan of camera track; M0 may proceed only by explicit decision).
4. U-4/U-7/U-8 answered; affected bridge estimates updated.
5. AI_NAVIGATION.xml matches code at baseline SHA.
6. D-α…D-ε recorded as decided.
7. Zero open blocking-for-M0 assumptions.
8. Bridge reflects every discovery-driven change (Phase 1 needs no Phase 0
   reading).

## Handoff

Phase 1 starts at bridge prompt P-0.0 on a fresh branch from the recorded base
SHA, per the bridge standing footer. Phase 0 artifacts are evidence, not
required reading — everything load-bearing is patched into roadmap/bridge.
