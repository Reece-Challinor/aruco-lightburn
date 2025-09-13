"""Logging handlers and setup utilities."""

import logging
import os
from flask import Flask
from typing import Optional

from .structured_logger import get_logger


def setup_logging(app: Optional[Flask] = None, log_level: str = 'INFO'):
    """Setup application-wide logging configuration.
    
    Args:
        app: Flask application instance
        log_level: Default logging level
    """
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Set root logger level
    logging.root.setLevel(getattr(logging, log_level.upper()))
    
    # Configure Flask app logging if provided
    if app:
        # Disable default Flask logger
        app.logger.handlers = []
        
        # Use our structured logger
        logger = get_logger('flask.app')
        app.logger = logger.logger
        
        # Set Werkzeug logging level
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Configure other library loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Log startup
    logger = get_logger(__name__)
    logger.info(f"Logging system initialized with level: {log_level}")