"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_security.py</name>
    <type>security_tests</type>
    <purpose>Regression tests for security headers, secrets, info disclosure, rate limits</purpose>
  </file_meta>
</ai_agent_documentation>
-->
"""

import json

import pytest

from app import create_app


class TestSecurityHeaders:
    def test_security_headers_on_pages(self, client):
        response = client.get("/")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "Content-Security-Policy" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers

    def test_csp_blocks_external_scripts(self, client):
        csp = client.get("/").headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "object-src 'none'" in csp

    def test_security_headers_on_api(self, client):
        response = client.get("/api/healthz")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "Content-Security-Policy" in response.headers

    def test_no_cdn_dependencies_in_pages(self, client):
        """All frontend assets must be self-hosted (CSP + supply chain)."""
        for path in ("/", "/generate", "/calibration", "/validation"):
            html = client.get(path).get_data(as_text=True)
            assert "cdn.replit.com" not in html
            assert "cdn.jsdelivr.net" not in html


class TestInformationDisclosure:
    def test_debug_endpoint_removed(self, client):
        assert client.get("/api/debug/status").status_code == 404

    def test_health_does_not_fingerprint_host(self, client):
        data = json.loads(client.get("/api/health").data)
        assert "platform" not in data
        assert "python" not in data


class TestSessionSecret:
    def test_production_requires_session_secret(self, monkeypatch):
        monkeypatch.setenv("VERCEL_ENV", "production")
        monkeypatch.delenv("SESSION_SECRET", raising=False)
        with pytest.raises(RuntimeError, match="SESSION_SECRET"):
            create_app()

    def test_dev_falls_back_with_warning(self, monkeypatch):
        monkeypatch.delenv("VERCEL_ENV", raising=False)
        monkeypatch.delenv("FLASK_ENV", raising=False)
        monkeypatch.delenv("SESSION_SECRET", raising=False)
        app = create_app()
        assert app.secret_key  # falls back, app still boots for local dev


class TestRateLimiting:
    """Each test uses a fresh app with limits enabled and a unique client IP
    so counters never collide with other tests (the memory storage is shared
    across app instances)."""

    @pytest.fixture()
    def limited_client(self, monkeypatch):
        from aruco_generator.core.rate_limit import limiter

        monkeypatch.delenv("VERCEL_ENV", raising=False)
        monkeypatch.setenv("RATELIMIT_ENABLED", "1")
        app = create_app()
        app.config.update(TESTING=True)
        yield app.test_client()
        limiter.reset()

    def test_log_error_rate_limited(self, limited_client):
        statuses = [
            limited_client.post(
                "/api/log-error",
                json={"message": "x"},
                environ_base={"REMOTE_ADDR": "10.9.9.1"},
            ).status_code
            for _ in range(11)
        ]
        assert statuses[:10] == [200] * 10
        assert statuses[10] == 429

    def test_rate_limit_error_is_json_envelope(self, limited_client):
        for _ in range(11):
            response = limited_client.post(
                "/api/log-error",
                json={"message": "x"},
                environ_base={"REMOTE_ADDR": "10.9.9.2"},
            )
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"]["type"] == "rate_limited"
