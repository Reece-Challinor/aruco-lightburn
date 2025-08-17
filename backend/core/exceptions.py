"""
Custom exceptions and error handling
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """Base API exception"""
    status_code = 500
    message = 'Internal server error'
    
    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert exception to dictionary"""
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv

class ValidationError(APIException):
    """Validation error exception"""
    status_code = 400
    message = 'Validation failed'

class NotFoundError(APIException):
    """Resource not found exception"""
    status_code = 404
    message = 'Resource not found'

class AuthenticationError(APIException):
    """Authentication error exception"""
    status_code = 401
    message = 'Authentication required'

class PermissionError(APIException):
    """Permission denied exception"""
    status_code = 403
    message = 'Permission denied'

class RateLimitError(APIException):
    """Rate limit exceeded exception"""
    status_code = 429
    message = 'Rate limit exceeded'

class ConflictError(APIException):
    """Resource conflict exception"""
    status_code = 409
    message = 'Resource conflict'

def handle_api_exception(error):
    """Handle API exceptions"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    
    # Log error
    if error.status_code >= 500:
        logger.error(f"API Exception: {error.message}", exc_info=True)
    else:
        logger.warning(f"API Exception: {error.message}")
    
    return response

def handle_http_exception(error):
    """Handle HTTP exceptions"""
    response = jsonify({
        'error': error.description,
        'status_code': error.code
    })
    response.status_code = error.code
    
    if error.code >= 500:
        logger.error(f"HTTP Exception: {error.description}", exc_info=True)
    
    return response

def handle_general_exception(error):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    
    response = jsonify({
        'error': 'An unexpected error occurred',
        'status_code': 500
    })
    response.status_code = 500
    
    return response

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    app.errorhandler(APIException)(handle_api_exception)
    app.errorhandler(HTTPException)(handle_http_exception)
    app.errorhandler(Exception)(handle_general_exception)