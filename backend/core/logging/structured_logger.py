"""Structured logging implementation."""

import logging
import json
import uuid
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, Any
import os

from .formatters import JSONFormatter, ColoredConsoleFormatter


class StructuredLogger:
    """Structured logging with JSON format and correlation tracking."""
    
    _loggers = {}
    
    def __init__(self, name: str):
        """Initialize structured logger.
        
        Args:
            name: Logger name (typically module name)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Only setup handlers if not already configured
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers with rotation and formatting."""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Console handler with color coding
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredConsoleFormatter())
        
        # Main application log with rotation
        app_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(JSONFormatter())
        
        # Error log handler
        error_handler = RotatingFileHandler(
            'logs/errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        
        # API requests log
        api_handler = TimedRotatingFileHandler(
            'logs/api_requests.log',
            when='midnight',
            interval=1,
            backupCount=7  # Keep 7 days
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(JSONFormatter())
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(app_handler)
        self.logger.addHandler(error_handler)
        
        # Add API handler only for API-related loggers
        if 'api' in self.name.lower() or 'endpoint' in self.name.lower():
            self.logger.addHandler(api_handler)
    
    def _add_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add context information to log entries.
        
        Args:
            extra: Additional context to include
            
        Returns:
            Enhanced context dictionary
        """
        from flask import g, request, has_request_context
        
        context = extra or {}
        
        # Add request context if available
        if has_request_context():
            if hasattr(g, 'request_id'):
                context['request_id'] = g.request_id
            if hasattr(g, 'user_id'):
                context['user_id'] = g.user_id
            
            # Add request details
            context['method'] = request.method
            context['path'] = request.path
            context['remote_addr'] = request.remote_addr
            
            # Add query parameters (excluding sensitive ones)
            if request.args:
                safe_args = {k: v for k, v in request.args.items() 
                           if 'password' not in k.lower() and 'token' not in k.lower()}
                if safe_args:
                    context['query_params'] = safe_args
        
        return context
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        extra = self._add_context(kwargs)
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        extra = self._add_context(kwargs)
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        extra = self._add_context(kwargs)
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exc_info=False, **kwargs):
        """Log error message with context.
        
        Args:
            message: Error message
            exc_info: Include exception traceback
            **kwargs: Additional context
        """
        extra = self._add_context(kwargs)
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def critical(self, message: str, exc_info=False, **kwargs):
        """Log critical message with context."""
        extra = self._add_context(kwargs)
        self.logger.critical(message, exc_info=exc_info, extra=extra)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            **kwargs: Additional metrics
        """
        metrics = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'performance_log': True,
            **kwargs
        }
        extra = self._add_context(metrics)
        self.logger.info(f"Performance: {operation}", extra=extra)
    
    def log_api_call(self, endpoint: str, status_code: int, duration: float, **kwargs):
        """Log API call metrics.
        
        Args:
            endpoint: API endpoint
            status_code: HTTP status code
            duration: Request duration in seconds
            **kwargs: Additional details
        """
        api_data = {
            'api_endpoint': endpoint,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2),
            'api_log': True,
            **kwargs
        }
        extra = self._add_context(api_data)
        
        level = logging.INFO
        if status_code >= 500:
            level = logging.ERROR
        elif status_code >= 400:
            level = logging.WARNING
            
        self.logger.log(level, f"API: {endpoint} [{status_code}]", extra=extra)


def get_logger(name: str) -> StructuredLogger:
    """Get or create a structured logger.
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    if name not in StructuredLogger._loggers:
        StructuredLogger._loggers[name] = StructuredLogger(name)
    return StructuredLogger._loggers[name]