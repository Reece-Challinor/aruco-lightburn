"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>core/__init__.py</name>
    <version>1.0.0</version>
    <type>python_package_init</type>
    <purpose>Core generation package exports</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from .aruco import ArUCOGenerator  # noqa: F401
from .drawing import DrawingContext  # noqa: F401
from .utils import handle_api_errors, validate_generation_params  # noqa: F401

__all__ = [
    "ArUCOGenerator",
    "DrawingContext",
    "handle_api_errors",
    "validate_generation_params",
]
