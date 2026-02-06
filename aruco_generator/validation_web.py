"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>validation_web.py</name>
    <version>2.1.0</version>
    <type>deprecated_module</type>
    <purpose>Legacy validation routes retained for compatibility; use aruco_generator.web.web instead</purpose>
    <last_updated>2026-02-06</last_updated>
  </file_meta>
</ai_agent_documentation>
-->
"""

from flask import render_template


def validation_page_old():
    """Legacy validation page (deprecated)."""
    return render_template("validation.html")


def documentation_page_old():
    """Legacy documentation page (deprecated)."""
    return render_template("documentation.html")


def generate_page_old():
    """Legacy generate page (deprecated)."""
    return render_template("generate.html")
