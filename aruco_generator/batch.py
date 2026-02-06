"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>batch.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for batch generation (moved to aruco_generator.export)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .export.batch import BatchGenerator  # noqa: F401

__all__ = ["BatchGenerator"]
