"""
ArUCO Generator - Flask Application Entry Point
==============================================

Purpose: Main application setup and configuration for the ArUCO marker generator
Pattern: Factory pattern for Flask app initialization with database support

Responsibilities:
- Flask application configuration and initialization
- Database connection setup (PostgreSQL/SQLite)
- Extension registration (SQLAlchemy)
- Route registration from modular components
- Error handling and logging configuration

Usage: This module is imported by main.py for deployment
Author: ArUCO Generator Team
Version: 2.0.0
"""

import os
import logging
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
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///aruco_generator.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    from aruco_generator.web import *  # noqa: F401, F403
    from aruco_generator.calibration_web import *  # noqa: F401, F403
    from aruco_generator.advanced_web import *  # noqa: F401, F403
    logger.info("Routes registered")