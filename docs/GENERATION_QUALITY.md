<!--
<ai_agent_documentation>
  <file_meta>
    <name>docs/GENERATION_QUALITY.md</name>
    <version>1.0.0</version>
    <type>quality_guidelines</type>
    <purpose>Marker generation quality standards and validation steps</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Generation Quality Standards

## Core Requirements
- Generated markers must be strictly binary (0/255) with no gray artifacts.
- SVG exports should not introduce gaps between merged rectangles.
- LightBurn exports must preserve marker bit patterns.

## Validation
- Run `make validate` for full CI coverage.
- Use `scripts/validate_quality.py` for local quality checks.
- Export tests in `tests/test_export_formats.py` must pass.
