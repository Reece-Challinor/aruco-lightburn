"""
Custom middleware for request/response processing
"""
from flask import request, g
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestMiddleware:
    """Request processing middleware"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """Process before each request"""
        # Generate request ID
        g.request_id = str(uuid.uuid4())
        
        # Start timing
        g.start_time = time.time()
        
        # Log request
        logger.info(f"Request started: {request.method} {request.path} [{g.request_id}]")
    
    def after_request(self, response):
        """Process after each request"""
        if hasattr(g, 'start_time'):
            # Calculate duration
            duration = time.time() - g.start_time
            
            # Add headers
            response.headers['X-Request-ID'] = g.request_id
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"[{response.status_code}] [{duration:.3f}s] [{g.request_id}]"
            )
        
        # CORS headers for API
        if request.path.startswith('/api/'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    def teardown_request(self, exception=None):
        """Clean up after request"""
        if exception:
            logger.error(f"Request failed: {exception} [{g.get('request_id', 'unknown')}]")

class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, app=None, default_limit='100/hour'):
        self.default_limit = default_limit
        self.limits = {}
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize rate limiting"""
        app.before_request(self.check_rate_limit)
    
    def check_rate_limit(self):
        """Check rate limit for request"""
        # For now, just log - would implement actual rate limiting with Redis
        if request.path.startswith('/api/'):
            client_id = request.remote_addr
            logger.debug(f"Rate limit check for {client_id}: {request.path}")

class CompressionMiddleware:
    """Response compression middleware"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize compression"""
        app.after_request(self.compress_response)
    
    def compress_response(self, response):
        """Compress response if applicable"""
        # Check if response should be compressed
        if (response.status_code < 200 or 
            response.status_code >= 300 or
            'Content-Encoding' in response.headers or
            response.content_length < 500):
            return response
        
        # Check Accept-Encoding
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' not in accept_encoding.lower():
            return response
        
        # Would implement actual gzip compression here
        # For now, just add header to indicate support
        response.headers['X-Compression-Available'] = 'gzip'
        
        return response