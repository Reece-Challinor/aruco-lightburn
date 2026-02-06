"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>calibration_web.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for calibration routes (moved to aruco_generator.web.calibration_web)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .web.calibration_web import calibration_bp  # noqa: F401

__all__ = ["calibration_bp"]
