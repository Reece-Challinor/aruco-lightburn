"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>aruco.py</name>
    <version>2.1.0</version>
    <type>compatibility_shim</type>
    <purpose>Compatibility wrapper for core ArUCO generator (moved to aruco_generator.core)</purpose>
    <last_updated>2026-02-06</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>

  <compatibility>
    <reexport>aruco_generator.core.aruco.ArUCOGenerator</reexport>
    <notes>Use aruco_generator.core.aruco for canonical implementation</notes>
  </compatibility>
</ai_agent_documentation>
-->
"""

from .core.aruco import OPENCV_AVAILABLE, ArUCOGenerator, cv2, np  # noqa: F401

__all__ = ["ArUCOGenerator", "OPENCV_AVAILABLE", "cv2", "np"]
