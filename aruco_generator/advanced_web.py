"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>advanced_web.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for advanced routes (moved to aruco_generator.web.advanced_web)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .web.advanced_web import advanced_bp  # noqa: F401

__all__ = ["advanced_bp"]
