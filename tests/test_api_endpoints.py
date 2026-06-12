"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_api_endpoints.py</name>
    <version>1.2.0</version>
    <type>test_suite</type>
    <purpose>Integration coverage for core API endpoints and health checks</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Integration tests for API endpoints
"""

import json


def test_home_page(client):
    """Test home page loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"ArUCO" in response.data


def test_generate_page(client):
    """Test generate page loads"""
    response = client.get("/generate")
    assert response.status_code == 200


def test_calibration_page(client):
    """Test calibration page loads"""
    response = client.get("/calibration")
    assert response.status_code == 200


def test_validation_page(client):
    """Test validation page loads"""
    response = client.get("/validation")
    assert response.status_code == 200


def test_documentation_page(client):
    """Test documentation page loads"""
    response = client.get("/documentation")
    assert response.status_code == 200


def test_get_dictionaries(client):
    """Test dictionary list API"""
    response = client.get("/api/dictionaries")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert "4X4_50" in data

    dict_info = data["4X4_50"]
    assert "size" in dict_info
    assert "max_markers" in dict_info
    assert "recommended_use" in dict_info


def test_preview_generation(client):
    """Test SVG preview generation"""
    test_data = {
        "dictionary": "4X4_50",
        "start_id": 0,
        "rows": 2,
        "cols": 2,
        "size_mm": 20,
        "spacing_mm": 5,
        "border_bits": 1,
        "include_labels": True,
        "include_outer_border": False,
    }

    response = client.post(
        "/api/preview", data=json.dumps(test_data), content_type="application/json"
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert "svg" in data
    assert "dimensions" in data
    assert "marker_count" in data
    assert data["marker_count"] == 4
    assert data["success"]


def test_preview_invalid_dictionary(client):
    """Test preview with invalid dictionary"""
    test_data = {
        "dictionary": "INVALID",
        "start_id": 0,
        "rows": 1,
        "cols": 1,
        "size_mm": 20,
        "spacing_mm": 5,
        "border_bits": 1,
    }

    response = client.post(
        "/api/preview", data=json.dumps(test_data), content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_preview_invalid_params(client):
    """Test preview with invalid parameters"""
    test_data = {
        "dictionary": "4X4_50",
        "start_id": -1,
        "rows": 0,
        "cols": 1,
        "size_mm": 20,
        "spacing_mm": 5,
        "border_bits": 1,
    }

    response = client.post(
        "/api/preview", data=json.dumps(test_data), content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_download_lightburn(client):
    """Test LightBurn file download"""
    test_data = {
        "dictionary": "4X4_50",
        "start_id": 0,
        "rows": 1,
        "cols": 1,
        "size_mm": 20,
        "spacing_mm": 5,
        "border_bits": 1,
        "include_labels": False,
    }

    response = client.post(
        "/api/download", data=json.dumps(test_data), content_type="application/json"
    )

    assert response.status_code == 200
    assert "application/octet-stream" in response.content_type
    assert "attachment" in response.headers.get("Content-Disposition", "")


def test_quick_test_endpoint(client):
    """Test quick test API endpoint"""
    response = client.get("/api/quick-test")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "message" in data
    assert "available_dictionaries" in data
    assert "timestamp" in data


def test_debug_status_endpoint_removed(client):
    """The unauthenticated debug endpoint must not exist (security)."""
    response = client.get("/api/debug/status")
    assert response.status_code == 404


def test_health_endpoint(client):
    """Test comprehensive health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "status" in data
    assert "metrics" in data
    assert "dependencies" in data
    assert "database" in data
    assert "request_id" in data


def test_healthz_endpoint(client):
    """Test lightweight health endpoint"""
    response = client.get("/api/healthz")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "request_id" in data


def test_log_error_endpoint(client):
    """Test error logging endpoint"""
    error_data = {
        "timestamp": "2024-01-01T00:00:00Z",
        "context": "Test",
        "message": "Test error",
        "stack": "Test stack trace",
        "url": "http://test.com",
    }

    response = client.post(
        "/api/log-error", data=json.dumps(error_data), content_type="application/json"
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "logged"
