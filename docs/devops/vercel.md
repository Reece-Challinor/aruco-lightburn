<!--
<ai_agent_documentation>
  <file_meta>
    <name>vercel.md</name>
    <version>1.0.0</version>
    <type>devops_guide</type>
    <purpose>Vercel deployment configuration, environments, and domain mapping</purpose>
    <last_updated>2026-02-09</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Vercel Deployment Guide

## Environments
- **Production**: `aruco.tools` (Vercel production branch = `main`).
- **Staging**: `staging.aruco.tools` mapped to the active `release/vX.Y` branch.
- **Preview**: Auto-generated per-branch preview URLs.

## GitHub Integration
Use Vercel’s GitHub integration for all deployments.
- Preview deployments for every PR/branch.
- Production deployments on merges to `main`.

## Build Runtime
The project uses the Vercel Python runtime with Flask.
- Entry point: `app.py` (exports `app = create_app()`).
- Static assets are served from `static/`.
- Routing and cache headers are defined in `vercel.json`.

## Required Environment Variables
- `DATABASE_URL`
- `SESSION_SECRET`
- `FLASK_APP=app.py`
- `FLASK_ENV=production`
- `PYTHONUNBUFFERED=1`

## Local Sync
When needed, pull environment variables into `.env.local`:
```
vercel env pull
```

## Repo Hygiene
The `.vercel/` folder is local-only and must not be committed.
