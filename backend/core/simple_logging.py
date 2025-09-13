"""Simple logging configuration for ArUCO Generator."""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app=None, log_level='INFO'):
    """Setup simple logging configuration.
    
    Args:
        app: Flask application instance (optional)
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if needed
    os.makedirs('logs', exist_ok=True)
    
    # Configure basic logging format
    log_format = '%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Setup root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers and add new ones
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(error_handler)
    
    # Configure Flask app logging if provided
    if app:
        app.logger.handlers = []
        app.logger.propagate = True
        
        # Reduce Werkzeug verbosity
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Reduce verbosity of common libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized with level: {log_level}")

def get_logger(name):
    """Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)