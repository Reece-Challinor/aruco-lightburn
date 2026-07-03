"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_api.py</name>
    <version>1.5.0</version>
    <type>integration_test</type>
    <purpose>Verify API endpoints and export routes</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Test suite for API endpoints
"""

import io
import json
from concurrent.futures import ThreadPoolExecutor

import pytest


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
    payload = data.get("data", data)
    assert "svg" in payload
    assert "dimensions" in payload
    assert payload["dimensions"]["width"] > 0
    assert payload["dimensions"]["height"] > 0


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
    assert "svg" in data["data"]
    assert "dimensions" in data["data"]


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
    assert data["success"] is True
    assert "hamming_distance" in data["data"]
    assert data["data"]["hamming_distance"] >= 0

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


def test_validation_error_schema(client):
    """Test validation error schema for invalid dictionary."""
    response = client.post(
        "/api/validation/hamming_distance",
        data=json.dumps({"dictionary": "INVALID", "id1": 0, "id2": 1}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "error" in data
    assert "message" in data["error"]
    assert data["error"]["type"] == "validation_error"


def test_metrics_endpoints_removed(client):
    """DB metrics endpoints are intentionally removed (roadmap F-10).

    Persisted metrics were misleading in serverless production (the DB is
    per-invocation in-memory). These 404s document the removal.
    """
    assert client.get("/api/validation/metrics").status_code == 404
    assert client.post("/api/calibration/metrics", json={}).status_code == 404


def test_detection_report_has_no_persistence(client):
    """detection_report computes per request; nothing is stored (F-10)."""
    response = client.post(
        "/api/validation/detection_report",
        data=json.dumps({"test_results": [], "pattern_metadata": {}}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "metric_id" not in data["data"]["report"]


def test_upload_invalid_image(client):
    """Test invalid image upload returns validation error."""
    response = client.post(
        "/api/validation/detect",
        data={"file": (io.BytesIO(b"not-an-image"), "bad.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "error" in data


def test_export_svg_empty_grid(client):
    """Test export rejects empty grid requests."""
    response = client.post(
        "/api/export/svg",
        json={
            "dictionary": "4X4_50",
            "rows": 0,
            "cols": 1,
            "size_mm": 20,
            "spacing_mm": 5,
        },
    )
    assert response.status_code == 400


def _preview_request(app):
    with app.test_client() as thread_client:
        response = thread_client.post(
            "/api/preview",
            json={
                "dictionary": "4X4_50",
                "rows": 1,
                "cols": 1,
                "size_mm": 20,
                "spacing_mm": 5,
                "start_id": 0,
            },
        )
        return response.status_code


def test_concurrent_preview_requests(app):
    """Test concurrent preview requests complete successfully."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda _: _preview_request(app), range(4)))
    assert all(code == 200 for code in results)


def test_upload_too_large(client):
    """Test oversized upload returns 413 payload."""
    original_max = client.application.config.get("MAX_CONTENT_LENGTH")
    client.application.config["MAX_CONTENT_LENGTH"] = 1024
    try:
        response = client.post(
            "/api/validation/detect",
            data={"file": (io.BytesIO(b"a" * 2048), "big.png")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 413
        data = response.get_json()
        assert data["success"] is False
        assert data["error"]["type"] == "payload_too_large"
    finally:
        client.application.config["MAX_CONTENT_LENGTH"] = original_max


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


def test_calibration_import_endpoint(client):
    """Test calibration import endpoint with JSON payload."""
    calibration_payload = {
        "pattern_type": "charuco",
        "board_size": [5, 7],
        "square_size_mm": 30,
        "marker_size_mm": 22,
        "dictionary": "4X4_50",
    }
    file_data = io.BytesIO(json.dumps(calibration_payload).encode("utf-8"))
    response = client.post(
        "/api/calibration/import",
        data={"file": (file_data, "calibration.json")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["calibration_data"]["pattern_type"] == "charuco"


def test_detection_endpoint(client):
    """Test detection endpoint with generated marker."""
    try:
        import cv2
        import numpy as np  # noqa: F401
    except Exception:
        pytest.skip("OpenCV not available")

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(dictionary, 0, 200)
    marker = cv2.copyMakeBorder(marker, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
    success, buffer = cv2.imencode(".png", marker)
    assert success

    response = client.post(
        "/api/validation/detect",
        data={
            "file": (io.BytesIO(buffer.tobytes()), "marker.png"),
            "dictionary": "4X4_50",
            "expected_markers": "1",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["detection"]["detected_markers"] >= 1
