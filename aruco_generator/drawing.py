"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>drawing.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for drawing context (moved to aruco_generator.core)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .core.drawing import DrawingContext  # noqa: F401

__all__ = ["DrawingContext"]
