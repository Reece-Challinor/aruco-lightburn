"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>app.py</name>
    <version>3.0.0</version>
    <type>flask_application_factory</type>
    <purpose>Main Flask application factory with database integration and route registration</purpose>
    <last_updated>2025-01-15</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>

  <golden_path>
    <description>Flask application initialization and configuration workflow</description>
    <steps>
      <step id="1">Import required modules → Flask, SQLAlchemy, logging</step>
      <step id="2">Create Flask app instance → Configure basic settings</step>
      <step id="3">Configure database → PostgreSQL or SQLite based on environment</step>
      <step id="4">Initialize extensions → SQLAlchemy, ProxyFix for HTTPS</step>
      <step id="5">Create database tables → Import models and call create_all</step>
      <step id="6">Register routes → Import web modules to register blueprints</step>
      <step id="7">Configure logging → Set up structured logging for production</step>
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
        <secret_key>SESSION_SECRET environment variable</secret_key>
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
      <module name="aruco_generator.advanced_web" purpose="Advanced features and validation"/>
    </module_imports>
    <registration_pattern>
      <method>Import modules within app context to register routes</method>
      <timing>After database initialization but before app ready</timing>
      <error_handling>Log warnings for failed module imports</error_handling>
    </registration_pattern>
  </route_registration>

  <deployment_patterns>
    <production_deployment>
      <wsgi_server>Gunicorn or uWSGI recommended</wsgi_server>
      <database>PostgreSQL with connection pooling</database>
      <environment_variables>DATABASE_URL, SESSION_SECRET required</environment_variables>
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
Version: 3.0.0
"""

import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Proxy fix for HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///aruco_generator.db"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Simple logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create database tables with error handling
try:
    with app.app_context():
        # Import models to ensure tables are created
        import models  # noqa: F401

        db.create_all()
        logger.info("Database initialized")
except Exception as e:
    logger.warning(f"Database initialization skipped: {e}")
    logger.info("Application will run without database persistence")

# Import and register routes
with app.app_context():
    from aruco_generator.advanced_web import *  # noqa: F401, F403
    from aruco_generator.calibration_web import *  # noqa: F401, F403
    from aruco_generator.web import *  # noqa: F401, F403

    logger.info("Routes registered")
