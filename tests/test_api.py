"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_api.py</name>
    <version>1.2.0</version>
    <type>integration_test</type>
    <purpose>Verify API endpoints and export routes</purpose>
    <last_updated>2026-02-07</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Test suite for API endpoints
"""

import json

import pytest

from app import app, db


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_generate_preview(client):
    """Test marker preview generation"""
    params = {
        "dictionary": "4X4_250",
        "rows": 2,
        "cols": 2,
        "size_mm": 50,
        "spacing_mm": 10,
        "start_id": 0,
        "include_borders": True,
        "include_labels": True,
    }

    response = client.post(
        "/api/preview", data=json.dumps(params), content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "svg" in data
    assert "dimensions" in data
    assert data["dimensions"]["width"] > 0
    assert data["dimensions"]["height"] > 0


def test_advanced_preview(client):
    """Test advanced preview generation"""
    params = {
        "dictionary": "4X4_250",
        "rows": 1,
        "cols": 1,
        "size_mm": 100,
        "spacing_mm": 20,
        "start_id": 42,
        "include_borders": True,
        "include_labels": True,
        "include_outer_border": True,
        "border_width": 5,
    }

    response = client.post(
        "/api/advanced/preview",
        data=json.dumps(params),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "svg" in data
    assert "dimensions" in data


def test_batch_generation(client):
    """Test batch marker generation"""
    params = {
        "sets": 3,
        "markers_per_set": 5,
        "start_id": 0,
        "dictionary": "4X4_250",
        "size_mm": 30,
        "spacing_mm": 5,
    }

    response = client.post(
        "/api/batch_generate", data=json.dumps(params), content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "success" in data or "results" in data


def test_calibration_endpoints(client):
    """Test all calibration pattern endpoints"""

    # Test ChArUco
    charuco_params = {
        "squares_x": 8,
        "squares_y": 6,
        "square_size_mm": 30,
        "marker_size_mm": 22.5,
        "dictionary": "4X4_50",
    }
    response = client.post(
        "/api/calibration/charuco",
        data=json.dumps(charuco_params),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Test ArUco Board
    board_params = {
        "markers_x": 4,
        "markers_y": 3,
        "marker_size_mm": 50,
        "separation_mm": 10,
        "dictionary": "4X4_50",
        "first_marker_id": 0,
    }
    response = client.post(
        "/api/calibration/aruco_board",
        data=json.dumps(board_params),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Test AprilTag
    apriltag_params = {"tag_family": "tag36h11", "tag_id": 0, "tag_size_mm": 50}
    response = client.post(
        "/api/calibration/apriltag",
        data=json.dumps(apriltag_params),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_validation_endpoints(client):
    """Test validation endpoints"""

    # Test Hamming distance
    hamming_params = {"dictionary": "4X4_250", "id1": 0, "id2": 10}
    response = client.post(
        "/api/validation/hamming_distance",
        data=json.dumps(hamming_params),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "hamming_distance" in data
    assert data["hamming_distance"] >= 0

    # Test test pattern generation
    test_params = {
        "dictionary": "4X4_50",
        "scales": [10, 20, 50],
        "include_distortions": False,
        "include_occlusions": False,
    }
    response = client.post(
        "/api/validation/test_pattern",
        data=json.dumps(test_params),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_advanced_export_endpoints(client):
    """Test advanced export endpoints return files."""
    payload = {"calibration_data": {"pattern_type": "aruco_markers"}}
    generation_params = {
        "dictionary": "4X4_50",
        "rows": 2,
        "cols": 2,
        "size_mm": 30,
        "spacing_mm": 5,
        "start_id": 0,
        "include_outer_border": True,
        "border_width": 2,
    }

    response = client.post(
        "/api/export/opencv_yaml",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert (
        response.content_type.startswith("text/yaml")
        or response.content_type.startswith("application/yaml")
        or response.content_type.startswith("text/plain")
    )

    response = client.post(
        "/api/export/ros",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"

    response = client.post(
        "/api/export/dxf",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/dxf"

    response = client.post(
        "/api/export/dxf",
        data=json.dumps(generation_params),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/dxf"

    response = client.post(
        "/api/export/stl",
        data=json.dumps(generation_params),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/sla"


def test_pdf_export_outer_border(client):
    """Test PDF export with outer border when reportlab is available."""
    pytest.importorskip("reportlab")
    params = {
        "dictionary": "4X4_50",
        "rows": 2,
        "cols": 2,
        "size_mm": 30,
        "spacing_mm": 5,
        "start_id": 0,
        "include_outer_border": True,
        "border_width": 3,
    }

    response = client.post(
        "/api/export/pdf",
        data=json.dumps(params),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/pdf"


def test_presets_endpoint(client):
    """Test presets endpoint"""
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.get_json()
    assert "business_cards" in data
    assert "inventory_tags" in data


def test_error_handling(client):
    """Test API error handling"""

    # Test invalid dictionary
    params = {
        "dictionary": "INVALID_DICT",
        "rows": 1,
        "cols": 1,
        "size_mm": 50,
        "spacing_mm": 10,
        "start_id": 0,
    }
    response = client.post(
        "/api/preview", data=json.dumps(params), content_type="application/json"
    )
    assert response.status_code in [400, 500]

    # Test invalid parameters
    params = {
        "dictionary": "4X4_250",
        "rows": -1,  # Invalid negative value
        "cols": 1,
        "size_mm": 50,
        "spacing_mm": 10,
        "start_id": 0,
    }
    response = client.post(
        "/api/preview", data=json.dumps(params), content_type="application/json"
    )
    assert response.status_code in [400, 500]


def test_content_types(client):
    """Test API content types"""
    response = client.get("/api/dictionaries")
    assert response.status_code == 200
    assert response.content_type == "application/json"

    # Test preview returns JSON with SVG content
    params = {
        "dictionary": "4X4_250",
        "rows": 1,
        "cols": 1,
        "size_mm": 50,
        "spacing_mm": 10,
        "start_id": 0,
    }
    response = client.post(
        "/api/preview", data=json.dumps(params), content_type="application/json"
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "svg" in data
    assert "<svg" in data["svg"]
