"""
Simplified middleware for request/response processing
"""
from flask import request, g
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestMiddleware:
    """Simple request processing middleware"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Process before each request"""
        # Generate request ID for tracking
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        # Simple request logging
        logger.debug(f"Request: {request.method} {request.path} [{g.request_id}]")
    
    def after_request(self, response):
        """Process after each request"""
        if hasattr(g, 'start_time'):
            # Calculate duration
            duration = time.time() - g.start_time
            
            # Add simple headers
            response.headers['X-Request-ID'] = g.request_id
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            
            # Simple response logging
            if duration > 1.0:  # Only log slow requests
                logger.warning(f"Slow request: {request.path} took {duration:.3f}s")
        
        # CORS headers only for specific public API endpoints
        # Public endpoints that need CORS access
        public_endpoints = [
            '/api/v1/markers',
            '/api/v1/detection',
            '/api/v1/calibration',
            '/api/v1/export',
            '/api/v1/health'
        ]
        
        # Check if the current path is a public endpoint
        is_public = any(request.path.startswith(endpoint) for endpoint in public_endpoints)
        
        if is_public:
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        # Sensitive endpoints like auth, admin, and logs should NOT have wildcard CORS
        
        return response

class CompressionMiddleware:
    """Simple response compression middleware"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize compression"""
        # Flask has built-in compression support, just enable it
        app.config['COMPRESS_MIMETYPES'] = [
            'text/html', 'text/css', 'text/xml', 'application/json',
            'application/javascript', 'image/svg+xml'
        ]