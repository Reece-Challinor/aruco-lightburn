"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_ui_pages.py</name>
    <version>1.2.0</version>
    <type>ui_test</type>
    <purpose>Smoke-test rendered HTML for key UI affordances</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402


class TestUIPages(unittest.TestCase):
    """UI smoke tests for rendered templates."""

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_generate_page_has_advanced_exports(self):
        response = self.client.get("/generate")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("advancedExportBtn", html)
        self.assertIn('export-option" href="#" data-format="dxf"', html)
        self.assertIn('export-option" href="#" data-format="stl"', html)
        self.assertIn('advanced-export-option" href="#" data-format="dxf"', html)
        self.assertIn('advanced-export-option" href="#" data-format="stl"', html)

    def test_calibration_page_has_pattern_cards(self):
        response = self.client.get("/calibration")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn('data-pattern="charuco"', html)
        self.assertIn('data-pattern="aruco_board"', html)
        self.assertIn('data-pattern="apriltag"', html)
        self.assertIn('data-pattern="apriltag_grid"', html)
        self.assertNotIn('onclick="selectPattern', html)

    def test_validation_page_has_metrics_placeholders(self):
        response = self.client.get("/validation")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn('id="avgDetectionRate"', html)
        self.assertIn('id="avgPoseError"', html)
        self.assertIn('id="avgProcessingTime"', html)
        self.assertIn('id="recentTestsList"', html)
