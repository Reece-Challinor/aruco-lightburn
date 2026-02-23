"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>app.py</name>
    <version>3.6.0</version>
    <type>flask_application_factory</type>
    <purpose>Main Flask application factory with database integration and route registration</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>

  <golden_path>
    <description>Flask application initialization and configuration workflow</description>
    <steps>
      <step id="1">Import required modules → Flask, logging</step>
      <step id="2">Import extensions → from aruco_generator.extensions import db</step>
      <step id="3">Create Flask app instance → Configure basic settings</step>
      <step id="4">Configure database → PostgreSQL or SQLite based on environment</step>
      <step id="5">Initialize extensions → db.init_app(app)</step>
      <step id="6">Create database tables → Import aruco_generator.models and call create_all</step>
      <step id="7">Register routes → Import web modules to register blueprints</step>
      <step id="8">Configure logging → Set up structured logging for production</step>
    </steps>
    <fallback_paths>
      <fallback condition="database_unavailable">Log warning and continue without persistence</fallback>
      <fallback condition="import_error">Skip optional module registration</fallback>
      <fallback condition="configuration_error">Use default settings with warnings</fallback>
    </fallback_paths>
  </golden_path>

  <application_configuration>
    <database_settings>
      <primary_config>
        <url>DATABASE_URL environment variable or default SQLite</url>
        <engine_options>pool_recycle=300, pool_pre_ping=True</engine_options>
        <fallback>sqlite:///aruco_generator.db for development</fallback>
      </primary_config>
      <connection_handling>
        <strategy name="connection_pooling">Automatic connection pool management</strategy>
        <strategy name="health_checks">Pre-ping to validate connections</strategy>
        <strategy name="error_recovery">Graceful degradation when database unavailable</strategy>
      </connection_handling>
    </database_settings>

    <security_configuration>
      <session_management>
        <secret_key>SESSION_SECRET environment variable (fallback for local dev)</secret_key>
        <security_headers>ProxyFix middleware for reverse proxy deployment</security_headers>
      </session_management>
      <middleware_stack>
        <middleware name="ProxyFix" purpose="Handle X-Forwarded-* headers for HTTPS"/>
      </middleware_stack>
    </security_configuration>

    <logging_configuration>
      <format>%(asctime)s - %(name)s - %(levelname)s - %(message)s</format>
      <level>INFO for production, DEBUG for development</level>
      <handlers>Console handler with structured formatting</handlers>
    </logging_configuration>
  </application_configuration>

  <route_registration>
    <module_imports>
      <module name="aruco_generator.web" purpose="Main API endpoints and page routes"/>
      <module name="aruco_generator.calibration_web" purpose="Camera calibration endpoints"/>
      <module name="aruco_generator.web.advanced_web" purpose="Advanced features and validation"/>
    </module_imports>
    <registration_pattern>
      <method>Import modules within app context to register routes</method>
      <timing>After database initialization but before app ready</timing>
      <error_handling>Log warnings for failed module imports</error_handling>
    </registration_pattern>
  </route_registration>

  <deployment_patterns>
    <production_deployment>
      <wsgi_server>Gunicorn (app:app)</wsgi_server>
      <database>PostgreSQL with connection pooling</database>
      <environment_variables>DATABASE_URL, SESSION_SECRET required for production</environment_variables>
      <reverse_proxy>Nginx with HTTPS termination</reverse_proxy>
    </production_deployment>
    <development_deployment>
      <server>Flask development server</server>
      <database>SQLite for simplicity</database>
      <configuration>Default settings with auto-reload</configuration>
    </development_deployment>
  </deployment_patterns>

  <error_handling>
    <database_errors>
      <connection_failure>Log warning and continue without persistence</connection_failure>
      <table_creation_failure>Log error but allow app to start</table_creation_failure>
      <migration_issues>Handle gracefully with clear error messages</migration_issues>
    </database_errors>
    <import_errors>
      <missing_modules>Log warnings for optional dependencies</missing_modules>
      <route_registration_failure>Log errors but continue startup</route_registration_failure>
    </import_errors>
  </error_handling>

  <performance_considerations>
    <database_optimization>
      <connection_pooling>SQLAlchemy engine with pool settings</connection_pooling>
      <health_checks>Pre-ping to avoid stale connections</health_checks>
      <pool_recycling>300 second connection lifecycle</pool_recycling>
    </database_optimization>
    <application_startup>
      <lazy_loading>Routes registered on demand</lazy_loading>
      <error_tolerance>Continue startup even with some failures</error_tolerance>
    </application_startup>
  </performance_considerations>

  <monitoring_and_observability>
    <logging_strategy>
      <structured_logging>Consistent format across all modules</structured_logging>
      <log_levels>Appropriate levels for different event types</log_levels>
      <error_context>Include relevant context in error messages</error_context>
    </logging_strategy>
    <health_checks>
      <database_connectivity>Automatic pre-ping validation</database_connectivity>
      <route_availability>All routes registered and accessible</route_availability>
    </health_checks>
  </monitoring_and_observability>

  <version_history>
    <version number="3.1.0" date="2025-01-15">
      <changes>
        <change>Refactored DB to extensions.py module</change>
        <change>Moved models to aruco_generator package</change>
        <change>Cleaned up root directory topology</change>
      </changes>
    </version>
    <version number="3.0.0" date="2025-01-15">
      <changes>
        <change>Enhanced XML documentation system</change>
        <change>Comprehensive deployment and configuration documentation</change>
        <change>Improved error handling and fallback strategies</change>
      </changes>
    </version>
    <version number="2.0.0" date="2025-01-13">
      <changes>
        <change>Enhanced application factory pattern</change>
        <change>Improved database configuration and error handling</change>
        <change>Better logging and monitoring setup</change>
      </changes>
    </version>
  </version_history>
</ai_agent_documentation>
-->

ArUCO Generator - Flask Application Factory
===========================================

Purpose: Main application factory with database integration and comprehensive route registration
Pattern: Factory pattern for Flask app initialization with graceful error handling

Responsibilities:
- Flask application configuration and initialization
- Database connection setup (PostgreSQL/SQLite) with fallback
- Extension registration (SQLAlchemy, middleware)
- Modular route registration from web components
- Structured logging and error handling configuration

Architecture Overview:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   App Factory   │───▶│   Database      │───▶│   Route         │
│   (this file)   │    │   Setup         │    │   Registration  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Middleware    │    │   Error         │    │   Logging       │
│   Configuration │    │   Handling      │    │   Setup         │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Golden Path Usage:
1. Import app → from app import app, db
2. Configure environment → Set DATABASE_URL, SESSION_SECRET
3. Run application → app.run() or WSGI server
4. Routes auto-registered → All web modules loaded
5. Database ready → Tables created, connections pooled

Deployment Patterns:
- Production: Gunicorn + PostgreSQL + Nginx
- Development: Flask dev server + SQLite
- Docker: Environment variables for configuration

Author: ArUCO Generator Team
Version: 1.0.0
"""

import logging
import os
import time

from flask import Flask, request
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
from werkzeug.middleware.proxy_fix import ProxyFix

from aruco_generator import __version__ as app_version
from aruco_generator.core.observability import init_observability
from aruco_generator.core.utils import build_error_payload
from aruco_generator.extensions import db

# Simple logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    session_secret = os.environ.get("SESSION_SECRET")
    if not session_secret:
        session_secret = "dev-insecure-key-change-me"
        logger.warning(
            "SESSION_SECRET not set; using insecure default. "
            "Set SESSION_SECRET for production."
        )
    app.secret_key = session_secret
    app.config["APP_START_TIME"] = time.time()
    app.config["APP_VERSION"] = app_version

    # Proxy fix for HTTPS
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Observability tuning
    app.config.setdefault("METRICS_WINDOW_SECONDS", 300)
    app.config.setdefault("ERROR_RATE_WARN_THRESHOLD", 0.1)
    app.config.setdefault("ERROR_RATE_MIN_REQUESTS", 20)
    app.config.setdefault("ERROR_RATE_WARN_COOLDOWN", 60)
    app.config.setdefault("SLOW_REQUEST_MS", 2000)
    app.config.setdefault("INCLUDE_ERROR_DETAILS", False)
    app.config.setdefault("MAX_CONTENT_LENGTH", 12 * 1024 * 1024)
    app.config.setdefault("MAX_UPLOAD_IMAGE_BYTES", 10 * 1024 * 1024)
    app.config.setdefault("MAX_IMPORT_BYTES", 2 * 1024 * 1024)
    app.config.setdefault("MAX_IMAGE_PIXELS", 20_000_000)
    app.config.setdefault("MAX_IMAGE_DIMENSION", 8000)

    USE_DB = False
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        USE_DB = True
    elif os.environ.get("USE_SQLITE"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aruco_generator.db"
        USE_DB = True
    else:
        # Stateless mode
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        USE_DB = False

    app.config["USE_DB"] = USE_DB
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        return response

    # Attach request tracing and metrics
    init_observability(app)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_request(error):  # type: ignore[override]
        if request.path.startswith("/api/"):
            payload = build_error_payload(
                "Upload exceeds maximum allowed size.",
                413,
                "payload_too_large",
                fields={"file": "File too large"},
            )
            return payload, 413
        return error

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):  # type: ignore[override]
        if request.path.startswith("/api/"):
            payload = build_error_payload(
                "Malformed request payload.",
                400,
                "bad_request",
            )
            return payload, 400
        return error

    # Initialize database extension only if we intend to use it, or always init with safe fallback
    db.init_app(app)

    # Create database tables only if we are using persistence
    if USE_DB:
        try:
            with app.app_context():
                # Import models to ensure tables are created
                from aruco_generator import models  # noqa: F401
                from aruco_generator.db.schema import ensure_schema

                db.create_all()
                ensure_schema(db)
                logger.info("Database initialized")
        except Exception as e:
            logger.warning(f"Database initialization skipped: {e}")
            logger.info("Application will run without database persistence")
    else:
        logger.info("Running in Stateless Mode (No Database Persistence)")

    # Import and register blueprints
    from aruco_generator.calibration_web import calibration_bp
    from aruco_generator.web import web_bp
    from aruco_generator.web.advanced_web import advanced_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(calibration_bp)
    app.register_blueprint(advanced_bp)

    logger.info("Routes registered via Blueprints")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
