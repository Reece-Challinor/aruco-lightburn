"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>lightburn.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for LightBurn export (moved to aruco_generator.export)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .export.lightburn import LightBurnExporter  # noqa: F401

__all__ = ["LightBurnExporter"]
