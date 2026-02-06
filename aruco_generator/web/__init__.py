"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>web/__init__.py</name>
    <version>1.0.0</version>
    <type>python_package_init</type>
    <purpose>Web blueprint package exports</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .advanced_web import advanced_bp  # noqa: F401
from .calibration_web import calibration_bp  # noqa: F401
from .web import web_bp  # noqa: F401

__all__ = ["web_bp", "calibration_bp", "advanced_bp"]
