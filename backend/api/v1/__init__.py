"""
API v1 module initialization
"""
from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import and register all endpoint blueprints
from .endpoints import (
    auth,
    markers_simple,
    detection,
    calibration,
    export,
    admin,
    health,
    logs
)

# Register sub-blueprints
api_v1.register_blueprint(auth.bp)
api_v1.register_blueprint(markers_simple.bp)
api_v1.register_blueprint(detection.bp)
api_v1.register_blueprint(calibration.bp)
api_v1.register_blueprint(export.bp)
api_v1.register_blueprint(admin.bp)
api_v1.register_blueprint(health.bp)
api_v1.register_blueprint(logs.bp)