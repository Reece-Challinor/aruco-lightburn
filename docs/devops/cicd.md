<!--
<ai_agent_documentation>
  <file_meta>
    <name>cicd.md</name>
    <version>1.0.0</version>
    <type>devops_guide</type>
    <purpose>CI/CD workflow overview for trunk-based delivery and release tags</purpose>
    <last_updated>2026-02-09</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# CI/CD Overview

This repository follows trunk-based delivery with short-lived branches, Vercel GitHub integration for deployments, and tag-driven releases.

## Branching Model
- `main`: production branch (Vercel production branch).
- Feature branches: `feat/*`, `fix/*`, `chore/*` merged via PR after CI passes.
- Release branches: `release/vX.Y` for staging and stabilization.
- Hotfix branches: `hotfix/vX.Y.Z` cut from a production tag if needed.

## Workflows

### CI (`.github/workflows/ci.yml`)
Runs on PRs to `main` and pushes to `main`.
- Install dependencies
- `make validate`
- `make coverage`
- Upload coverage to Codecov

### Release (`.github/workflows/release.yml`)
Runs on tags `v*`.
- Verifies tag matches `pyproject.toml` version
- Verifies changelog contains the tagged release section
- Runs `make validate`
- Publishes a GitHub Release with changelog excerpt

### Docker (`.github/workflows/docker.yml`)
Runs on tags `v*`.
- Builds and pushes Docker images to Docker Hub
- Tags: `latest` and the tag name (e.g., `v2.4.0`)

## Deployment Responsibility
Deployments are handled by Vercel’s GitHub integration (not GitHub Actions).
- Preview deployments for all non-production branches.
- Production deployments for `main`.

## Required Secrets (GitHub)
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

## Required Secrets (Vercel)
Managed in Vercel (not in GitHub Actions):
- `DATABASE_URL`
- `SESSION_SECRET`
- `FLASK_APP=app.py`
- `FLASK_ENV=production`
