"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_ui_pages.py</name>
    <version>1.3.0</version>
    <type>ui_test</type>
    <purpose>Smoke-test rendered HTML for key UI affordances</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""


def test_generate_page_has_advanced_exports(client):
    response = client.get("/generate")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "advancedExportBtn" in html
    assert 'export-option" href="#" data-format="dxf"' in html
    assert 'export-option" href="#" data-format="stl"' in html
    assert 'advanced-export-option" href="#" data-format="dxf"' in html
    assert 'advanced-export-option" href="#" data-format="stl"' in html


def test_calibration_page_has_pattern_cards(client):
    response = client.get("/calibration")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'data-pattern="charuco"' in html
    assert 'data-pattern="aruco_board"' in html
    assert 'data-pattern="apriltag"' in html
    assert 'data-pattern="apriltag_grid"' in html
    assert 'onclick="selectPattern' not in html


def test_validation_page_has_metrics_placeholders(client):
    response = client.get("/validation")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'id="avgDetectionRate"' in html
    assert 'id="avgPoseError"' in html
    assert 'id="avgProcessingTime"' in html
    assert 'id="recentTestsList"' in html
