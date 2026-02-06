"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>utils.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for shared utilities (moved to aruco_generator.core)</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .core.utils import handle_api_errors, validate_generation_params  # noqa: F401

__all__ = ["handle_api_errors", "validate_generation_params"]
