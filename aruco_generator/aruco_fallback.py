"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>aruco_fallback.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Deprecated fallback shim; core ArUCO generator handles fallback internally</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
  <deprecation>
    <note>Use aruco_generator.core.aruco.ArUCOGenerator instead.</note>
  </deprecation>
</ai_agent_documentation>
-->
"""

from .core.aruco import ArUCOGenerator  # noqa: F401

__all__ = ["ArUCOGenerator"]
