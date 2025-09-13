"""Enhanced logging middleware with request tracking and performance monitoring."""

import uuid
import time
from datetime import datetime
from flask import Flask, g, request, Response
from typing import Optional

from backend.core.logging import get_logger


class LoggingMiddleware:
    """Middleware for comprehensive request tracking and logging."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize logging middleware.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.logger = get_logger(__name__)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self._setup_hooks()
        self.logger.info("Logging middleware initialized")
    
    def _setup_hooks(self):
        """Setup Flask request hooks for logging."""
        
        @self.app.before_request
        def before_request():
            """Log request start and setup tracking."""
            # Generate request ID
            g.request_id = str(uuid.uuid4())
            g.request_start = time.time()
            
            # Extract user info if available
            g.user_id = None
            if hasattr(request, 'user') and hasattr(request.user, 'id'):
                g.user_id = request.user.id
            
            # Log request details
            self.logger.info(
                f"Request started: {request.method} {request.path}",
                request_id=g.request_id,
                method=request.method,
                path=request.path,
                remote_addr=request.remote_addr,
                user_agent=request.headers.get('User-Agent', 'Unknown'),
                referrer=request.headers.get('Referer', 'Direct'),
                content_type=request.content_type,
                content_length=request.content_length
            )
            
            # Log request body for debugging (excluding sensitive endpoints)
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not any(sensitive in request.path.lower() 
                          for sensitive in ['login', 'password', 'auth', 'token']):
                    if request.is_json:
                        try:
                            body = request.get_json()
                            # Remove sensitive fields
                            safe_body = self._sanitize_body(body)
                            if safe_body:
                                self.logger.debug(
                                    "Request body",
                                    request_id=g.request_id,
                                    body=safe_body
                                )
                        except Exception:
                            pass
        
        @self.app.after_request
        def after_request(response: Response) -> Response:
            """Log request completion and metrics."""
            # Calculate duration
            duration = time.time() - g.request_start if hasattr(g, 'request_start') else 0
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_func = self.logger.error
            elif response.status_code >= 400:
                log_func = self.logger.warning
            else:
                log_func = self.logger.info
            
            # Log response
            log_func(
                f"Request completed: {request.method} {request.path} [{response.status_code}]",
                request_id=getattr(g, 'request_id', 'unknown'),
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                content_type=response.content_type,
                content_length=response.content_length or 0
            )
            
            # Add request ID to response headers
            if hasattr(g, 'request_id'):
                response.headers['X-Request-ID'] = g.request_id
            
            # Add timing header
            response.headers['X-Response-Time'] = f"{round(duration * 1000, 2)}ms"
            
            # Log slow requests
            if duration > 1.0:  # Requests taking more than 1 second
                self.logger.warning(
                    f"Slow request detected: {request.path}",
                    request_id=getattr(g, 'request_id', 'unknown'),
                    duration_seconds=round(duration, 2),
                    slow_request=True
                )
            
            return response
        
        @self.app.errorhandler(Exception)
        def handle_exception(error: Exception) -> tuple:
            """Log unhandled exceptions."""
            request_id = getattr(g, 'request_id', 'unknown')
            
            self.logger.error(
                f"Unhandled exception in {request.method} {request.path}",
                exc_info=True,
                request_id=request_id,
                error_type=type(error).__name__,
                error_message=str(error)
            )
            
            # Return generic error response
            return {
                'error': 'An unexpected error occurred',
                'request_id': request_id
            }, 500
        
        @self.app.errorhandler(404)
        def handle_404(error) -> tuple:
            """Log 404 errors."""
            request_id = getattr(g, 'request_id', 'unknown')
            
            self.logger.warning(
                f"Route not found: {request.method} {request.path}",
                request_id=request_id,
                referrer=request.headers.get('Referer', 'Direct')
            )
            
            return {
                'error': 'Resource not found',
                'request_id': request_id
            }, 404
        
        @self.app.errorhandler(405)
        def handle_405(error) -> tuple:
            """Log method not allowed errors."""
            request_id = getattr(g, 'request_id', 'unknown')
            
            self.logger.warning(
                f"Method not allowed: {request.method} {request.path}",
                request_id=request_id
            )
            
            return {
                'error': 'Method not allowed',
                'request_id': request_id
            }, 405
    
    def _sanitize_body(self, body: dict) -> dict:
        """Remove sensitive fields from request body.
        
        Args:
            body: Request body dictionary
            
        Returns:
            Sanitized body dictionary
        """
        if not isinstance(body, dict):
            return body
        
        sensitive_fields = [
            'password', 'token', 'secret', 'api_key', 'apikey',
            'authorization', 'credit_card', 'cvv', 'ssn'
        ]
        
        sanitized = {}
        for key, value in body.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_body(value)
            else:
                sanitized[key] = value
        
        return sanitized