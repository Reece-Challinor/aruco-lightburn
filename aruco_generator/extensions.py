"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>extensions.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for db extensions (moved to aruco_generator.db)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .db.extensions import db  # noqa: F401

__all__ = ["db"]
