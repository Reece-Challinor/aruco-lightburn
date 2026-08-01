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


def test_debug_page_has_no_metrics_panel(client):
    """The DB-backed performance-metrics panel was removed (roadmap F-10)."""
    response = client.get("/debug")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'id="avgDetectionRate"' not in html
    assert 'id="recentTestsList"' not in html
    # The page's real features remain
    assert 'id="uploadZone"' in html


def test_design_tokens_stylesheet_served(client):
    """Ensure tokens.css and theme.js are injected into the base template."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "tokens.css" in html
    assert "theme.js" in html

def test_dev_components_gallery(client, app):
    """Ensure /dev/components renders when debug is true."""
    app.debug = True
    response = client.get("/dev/components")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Components Gallery" in html
    
    app.debug = False
    response = client.get("/dev/components")
    assert response.status_code == 404

def test_marker_size_calculator_page(client):
    """Ensure the marker size calculator page renders correctly."""
    response = client.get("/learn/marker-size-calculator")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Marker Size Calculator" in html
    assert "app-shell" in html
