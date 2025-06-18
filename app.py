"""
{
  "file_type": "flask_app_main",
  "purpose": "Main Flask application configuration and database setup",
  "dependencies": ["flask", "flask_sqlalchemy", "werkzeug", "os"],
  "routes": "Defined in aruco_generator/web.py",
  "database": "PostgreSQL with SQLAlchemy ORM",
  "architecture": "MVC pattern with modular design",
  "ai_navigation": {
    "primary_config": "Database and app initialization",
    "modify_for": "Adding new extensions or middleware",
    "related_files": ["main.py", "aruco_generator/web.py"]
  }
}
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

with app.app_context():
    db.create_all()