<!--
<ai_agent_documentation>
  <file_meta>
    <name>DECISION_LOG.md</name>
    <version>1.0.0</version>
    <type>phase0_decision_log</type>
    <purpose>Conflicts found during discovery with their resolutions, plus the founder decision packet (D-alpha..D-zeta) — all decided 2026-07-03. Phase 0 deliverables D-5 + D-7.</purpose>
    <last_updated>2026-07-03</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Phase 0 Decision Log (D-5)

## Conflicts found & resolutions

| # | Conflict | Resolution | Status |
|---|---|---|---|
| C-1 | `Permissions-Policy: camera=()` (app.py:297) globally disables the camera the roadmap's flagship features require | Code change required: `camera=(self)`. Patched into bridge P-1.3 prompt as an explicit step. Security note: still denies microphone/geolocation; camera granted to same-origin only | Resolved (delta pre-written) |
| C-2 | CSP `script-src 'self'` (app.py:272) blocks wasm compilation needed by OpenCV.js | Code change required: add `'wasm-unsafe-eval'` to script-src (narrowest directive that permits wasm; full 'unsafe-eval' NOT needed). Patched into bridge P-1.1 prompt. No worker-src change needed (same-origin worker files pass script-src 'self') | Resolved (delta pre-written) |
| C-3 | CI has no Node toolchain; bridge P-0.5/P-0.6 wire Node tests into `make test` | ci.yml gains `actions/setup-node` + `make test-js` target in the first JS-test PR (P-0.5). Patched into bridge | Resolved (delta pre-written) |
| C-4 | Two active programs: "Production Launch Program" (docs/ai/implementation_plan.md, phases 1–8, Phase 5 testing ACTIVE) vs roadmap program (M0–M3) | Proposed: finish launch-Phase 5 via bridge P-0.0 (same work); launch-Phases 6–7 (observability, docs) fold into roadmap M0/M1 deliverables; launch-Phase 8 (product polish) is SUPERSEDED by the roadmap; implementation_plan.md gets a pointer to the roadmap as the successor program | **Resolved 2026-07-03 (D-ζ signed off as proposed; implementation_plan.md annotated)** |
| C-5 | AGENTS.md requires per-change walkthrough.md + task.md updates; bridge standing footer didn't include them | Standing footer amended (bridge patch, this commit) | Resolved |
| C-6 | AGENTS.md: plan complex changes in implementation_plan.md; that file hosts the live launch program | Roadmap/bridge/phase0 docs are the planning surface for this program; implementation_plan.md remains the launch program's record until D-ζ merges them | Resolved pending D-ζ |

## Founder decision packet (D-7) — **DECIDED 2026-07-03**

Recorded from the founder's planning session (2026-07-03). The same session
also fixed the overall program shape: adopt & sequence the existing
roadmap/bridge as authoritative; stable base = minimal "green + tagged
release" (bridge P-0.0 + hygiene + merge + tag — deeper testing folds into
roadmap execution); version mapping v2.6.0 = stable base, v2.7/2.8/2.9 at
M0/M1/M2 gates, v3.0.0 = M3 launch. See the approved stable-base plan for
the code-health fold-in table.

| ID | Decision | Outcome |
|---|---|---|
| D-α | Base branch + PR #11 merge timing | **DECIDED:** merge the docs+stable-base branch to main now; roadmap branches cut from main. The WIP test edit was repaired in this same change (P-0.0 complete) |
| D-β | Branch/PR cadence | **DECIDED (as recommended):** one branch + PR per bridge prompt; Claude never self-merges; founder reviews every PR via Vercel previews |
| D-γ | Sandbox allowlist | **DECIDED (as recommended):** allowlist github.com + `~/.cache/pre-commit` + `~/.cache/uv` (configure via `/sandbox` when friction appears) |
| D-δ | Checkpoint autonomy | **DECIDED (as recommended):** stop-and-wait at CP-1..4 and at NO-GO spike verdicts; otherwise proceed prompt by prompt |
| D-ε | Physical calibration frame capture (needed by M2 start) | **DECIDED (as recommended):** founder captures 15–25 frames of a printed ChArUco board with one real camera when M1 starts; agent provides exact capture instructions then |
| D-ζ | Program reconciliation (C-4) | **DECIDED (as recommended):** per C-4 proposed resolution; implementation_plan.md annotated with per-phase dispositions |

## Readiness checklist (from PHASE_0_PLAN §4.1) — live status

- [x] AGENTS.md protocols absorbed (C-5 amendment)
- [x] PR merged / D-α decided (2026-07-03: stable-base branch merges to main, tags v2.6.0)
- [x] LightBurn WIP test fate decided → P-0.0 (BASELINE_REPORT) — **executed 2026-07-03: both tests repaired and green**
- [x] Versioning interpretation confirmed (release-level; release.py)
- [x] CI gates enumerated; local validate ≡ CI validate (same target; CI adds coverage + lockfile sync)
- [x] Baseline green (9 s; BASELINE_REPORT)
- [ ] U-1/U-2 spike verdict (T0.7) — **remains open; owned by bridge P-0.S (runs ∥ with M0, gates M1)**
- [ ] U-4 yaml pre-check (T0.7) — **remains open; owned by bridge P-0.6 session 1 (blocks F-04 only)**
- [x] U-7 answered (C-1/C-2 deltas pre-written)
- [x] U-8 answered (C-3 delta pre-written)
- [x] Test-suite runtime measured (9 s)
- [x] D-α…D-ζ recorded as decided (2026-07-03, this document)
