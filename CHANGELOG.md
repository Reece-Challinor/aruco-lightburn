<!--
<ai_agent_documentation>
  <file_meta>
    <name>CHANGELOG.md</name>
    <version>1.0.0</version>
    <type>changelog</type>
    <purpose>Track user-facing changes and releases</purpose>
    <last_updated>2026-02-07</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]
### Added
- TBD

### Changed
- TBD

### Removed
- TBD

## [2.1.0] - 2026-02-07
### Added
- Snapshot tests for SVG preview and LightBurn exports.
- Advanced export endpoint tests for YAML/ROS/DXF/STL.
- Documentation files referenced by AI_NAVIGATION.xml.
- UI smoke tests for key generation and calibration affordances.
- Advanced export dropdown with DXF/STL options and isolated state.
- AprilTag single persistence for export parity.
- Calibration page controller and dedicated styling.

### Changed
- Modularized backend into `core`, `export`, `web`, `calibration`, `validation`, and `db` packages.
- LightBurn download now uses marker pixel data to preserve bit patterns.
- App factory (`create_app`) is the canonical initialization entrypoint.
- Advanced preview uses shared validation and rendering helpers.
- PDF export supports optional outer border rendering.

### Removed
- Tracked runtime artifacts (pid files, sqlite db) from the repo.

## [2.0.0] - 2025-01-13
### Added
- Unified ArUCO generator release.
