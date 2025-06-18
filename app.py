"""
ArUCO Generator - Flask Application Configuration
================================================

AI AGENT DOCUMENTATION:
- Entry point: main.py imports this module
- Database: PostgreSQL with SQLAlchemy ORM (optional, falls back to SQLite)
- Error handling: Comprehensive logging to debug_logs.txt
- Routes: All defined in aruco_generator/web.py
- Static files: static/ directory (app.js with full error logging)
- Templates: templates/ directory (index.html with advanced mode)

DEBUGGING FOR AI AGENTS:
- Error logs: debug_logs.txt (auto-created)
- Status endpoint: GET /api/debug/status
- Frontend errors: POST /api/log-error
- Monitor script: ./debug_monitor.sh
- All API endpoints tested and working

ARCHITECTURE:
- Flask backend with modular ArUCO generation
- Vanilla JavaScript frontend with real-time validation
- SVG preview with LightBurn export
- OpenCV ArUCO standards compliance
- Production-ready error handling
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///aruco_generator.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Import and register routes
from aruco_generator.web import *

# Initialize database tables
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print("Database tables initialized successfully")
    except Exception as e:
        print(f"Database initialization warning: {e}")

# Initialize database after app context is available
if __name__ != "__main__":
    init_db()