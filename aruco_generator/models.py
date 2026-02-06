"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>models.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for db models (moved to aruco_generator.db)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .db.models import CalibrationPattern, DetectionMetric, User  # noqa: F401

__all__ = ["CalibrationPattern", "DetectionMetric", "User"]
