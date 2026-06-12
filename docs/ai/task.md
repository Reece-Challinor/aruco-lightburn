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

## Next up (Phase 1 remainder → Phase 2)
- [ ] aruco.tools DNS at Namecheap (PM action — see plan).
- [ ] Disable Deployment Protection for production (PM action).
- [ ] Set SESSION_SECRET in Vercel envs.
- [ ] Phase 2 security: XSS purge, CSP/HSTS, secret fail-fast, rate limiting,
      remove /api/debug/status.

## Previous cycle (2026-02-23, complete)
Archived — see git history of this file and docs/ai/walkthrough.md.
