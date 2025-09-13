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
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging - using our enhanced logging system
try:
    from backend.core.logging import setup_logging, get_logger
    # Will setup logging after app creation
except ImportError:
    # Fallback to basic logging if new system not available
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)

# Load configuration
try:
    from backend.core import get_config
    config = get_config()
    app.config.from_object(config)
except ImportError:
    # Fallback configuration if new modules not available
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///aruco_generator.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database
db.init_app(app)

# Setup enhanced logging system
try:
    from backend.core.logging import setup_logging, get_logger
    setup_logging(app, log_level='DEBUG' if app.debug else 'INFO')
    logger = get_logger(__name__)
    logger.info("Enhanced logging system initialized")
except ImportError:
    print("Enhanced logging system not available, using basic logging")
except Exception as e:
    print(f"Enhanced logging initialization failed: {e}")

# Initialize enhanced logging middleware
try:
    from backend.core.middleware.logging_middleware import LoggingMiddleware
    LoggingMiddleware(app)
    print("Enhanced logging middleware initialized")
except ImportError:
    print("Enhanced logging middleware not available")
except Exception as e:
    print(f"Enhanced logging middleware initialization failed: {e}")

# Initialize cache
try:
    from backend.core import init_cache
    cache = init_cache(app)
    print("Cache initialized successfully")
except ImportError:
    print("Cache module not available")
except Exception as e:
    print(f"Cache initialization failed: {e}")

# Initialize monitoring
try:
    from backend.core import PerformanceMonitor
    monitor = PerformanceMonitor(app)
    print("Performance monitoring initialized")
except ImportError:
    print("Monitoring module not available")
except Exception as e:
    print(f"Monitoring initialization failed: {e}")

# Initialize middleware
try:
    from backend.core import RequestMiddleware, CompressionMiddleware
    RequestMiddleware(app)
    CompressionMiddleware(app)
    print("Middleware initialized")
except ImportError:
    print("Middleware modules not available")
except Exception as e:
    print(f"Middleware initialization failed: {e}")

# Register error handlers
try:
    from backend.core import register_error_handlers
    register_error_handlers(app)
    print("Error handlers registered")
except ImportError:
    print("Error handler module not available")
except Exception as e:
    print(f"Error handler registration failed: {e}")

# Import and register routes
from aruco_generator.web import *
from aruco_generator.validation_web import *

# Fix marshmallow version compatibility
try:
    import marshmallow
    if not hasattr(marshmallow, '__version__'):
        marshmallow.__version__ = '4.0.0'  # Set a default version for compatibility
except ImportError:
    pass  # marshmallow not installed

# Register new API v1 blueprint with simple fallback
try:
    # Try to import the main API v1 blueprint
    from backend.api.v1 import api_v1
    app.register_blueprint(api_v1)
    print("API v1 registered successfully at /api/v1")
except Exception as e:
    print(f"Warning: Could not register full API v1: {e}")
    # Fallback to register individual endpoints directly
    try:
        from flask import Blueprint
        api_v1_fallback = Blueprint('api_v1', __name__, url_prefix='/api/v1')
        
        # Register logs endpoint
        from backend.api.v1.endpoints.logs import bp as logs_bp
        api_v1_fallback.register_blueprint(logs_bp)
        
        # Register simple markers endpoint
        from backend.api.v1.endpoints.markers_simple import bp as markers_bp
        api_v1_fallback.register_blueprint(markers_bp)
        
        # Register health endpoint
        from backend.api.v1.endpoints.health import bp as health_bp
        api_v1_fallback.register_blueprint(health_bp)
        
        app.register_blueprint(api_v1_fallback)
        print("API v1 fallback registered successfully at /api/v1")
    except Exception as fallback_error:
        print(f"Warning: Could not register API v1 fallback: {fallback_error}")

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