<!--
<ai_agent_documentation>
  <file_meta>
    <name>release.md</name>
    <version>1.0.0</version>
    <type>devops_guide</type>
    <purpose>Release workflow, tagging, and staging promotion steps</purpose>
    <last_updated>2026-02-09</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

# Release Workflow

## Versioning
Semantic Versioning (`MAJOR.MINOR.PATCH`).

Update these files before release:
- `pyproject.toml`
- `aruco_generator/__init__.py`
- `docs/CHANGELOG.md`
- `AI_NAVIGATION.xml`

## Staging Cut
1. Cut `release/vX.Y` from `main`.
2. Deploy to `staging.aruco.tools` (Vercel branch domain mapping).
3. Validate smoke tests and critical workflows.

## Production Release
1. Merge any fixes back to `main`.
2. Create an annotated tag on `main`: `vX.Y.Z`.
3. Push the tag. This triggers:
   - Release validation (`make validate`)
   - GitHub Release publication
   - Docker image build

## Hotfix
1. Create `hotfix/vX.Y.Z` from the production tag.
2. Apply the fix and run validation.
3. Tag and release as `vX.Y.Z+1`.
