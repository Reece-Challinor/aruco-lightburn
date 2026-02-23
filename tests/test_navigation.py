"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_navigation.py</name>
    <version>1.2.0</version>
    <type>integration_test</type>
    <purpose>Validate navigation routes and rendered UI affordances</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Test suite for navigation and routing improvements
"""


def test_home_page(client):
    """Test home page renders correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"ArUCO Generator" in response.data
    assert b"Professional Computer Vision" in response.data


def test_generate_page(client):
    """Test generate page renders correctly"""
    response = client.get("/generate")
    assert response.status_code == 200
    assert b"Marker Generation" in response.data
    assert b"Quick Generate" in response.data


def test_calibration_page(client):
    """Test calibration page renders correctly"""
    response = client.get("/calibration")
    assert response.status_code == 200
    assert b"Calibration Patterns" in response.data
    assert b"ChArUco" in response.data


def test_validation_page(client):
    """Test validation page renders correctly"""
    response = client.get("/validation")
    assert response.status_code == 200
    assert b"Validation Center" in response.data
    assert b"Hamming Distance" in response.data


def test_documentation_page(client):
    """Test documentation page renders correctly"""
    response = client.get("/documentation")
    assert response.status_code == 200
    assert b"Documentation" in response.data
    assert b"Getting Started" in response.data


def test_navigation_links(client):
    """Test all navigation links are present"""
    response = client.get("/")
    assert response.status_code == 200

    # Check for navigation links
    assert b'href="/generate"' in response.data
    assert b'href="/calibration"' in response.data
    assert b'href="/validation"' in response.data
    assert b'href="/documentation"' in response.data


def test_api_dictionaries(client):
    """Test API endpoint for dictionaries"""
    response = client.get("/api/dictionaries")
    assert response.status_code == 200
    data = response.get_json()
    assert "4X4_250" in data
    assert "max_markers" in data["4X4_250"]


def test_api_preview(client):
    """Test API preview endpoint"""
    response = client.post(
        "/api/preview",
        json={
            "dictionary": "4X4_250",
            "rows": 1,
            "cols": 1,
            "size_mm": 50,
            "spacing_mm": 10,
            "start_id": 0,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "svg" in data
    assert "dimensions" in data


def test_api_calibration_charuco(client):
    """Test ChArUco generation endpoint"""
    response = client.post(
        "/api/calibration/charuco",
        json={
            "squares_x": 8,
            "squares_y": 6,
            "square_size_mm": 30,
            "marker_size_mm": 22.5,
            "dictionary": "4X4_50",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "image_base64" in data["data"]


def test_api_validation_hamming(client):
    """Test Hamming distance calculation"""
    response = client.post(
        "/api/validation/hamming_distance",
        json={"dictionary": "4X4_250", "id1": 0, "id2": 1},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "hamming_distance" in data["data"]
    assert "safety_level" in data["data"]


def test_breadcrumb_navigation(client):
    """Test breadcrumb navigation is present"""
    response = client.get("/generate")
    assert response.status_code == 200
    assert b"breadcrumb" in response.data
    assert b"Home" in response.data
    assert b"Generate" in response.data


def test_responsive_design(client):
    """Test responsive design elements are present"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"navbar-toggler" in response.data  # Mobile menu toggle
    assert b"container-fluid" in response.data  # Responsive container


def test_404_error_handling(client):
    """Test 404 error handling"""
    response = client.get("/nonexistent-page")
    assert response.status_code == 404


def test_tab_navigation_urls(client):
    """Test tab navigation with URL parameters"""
    response = client.get("/generate?tab=advanced")
    assert response.status_code == 200
    # The JavaScript will handle tab activation


def test_base_template_inheritance(client):
    """Test all pages inherit from base template"""
    pages = ["/", "/generate", "/calibration", "/validation", "/documentation"]

    for page in pages:
        response = client.get(page)
        assert response.status_code == 200
        # Check for base template elements
        assert b"navbar" in response.data
        assert b"ArUCO Generator" in response.data
        assert b"footer" in response.data
