"""Custom log formatters for structured logging."""

import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process': record.process,
            'thread': record.thread
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add custom fields from extra
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'method'):
            log_obj['method'] = record.method
        if hasattr(record, 'path'):
            log_obj['path'] = record.path
        if hasattr(record, 'remote_addr'):
            log_obj['remote_addr'] = record.remote_addr
        if hasattr(record, 'status_code'):
            log_obj['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_obj['duration_ms'] = record.duration_ms
        if hasattr(record, 'query_params'):
            log_obj['query_params'] = record.query_params
        if hasattr(record, 'operation'):
            log_obj['operation'] = record.operation
        if hasattr(record, 'api_endpoint'):
            log_obj['api_endpoint'] = record.api_endpoint
        if hasattr(record, 'performance_log'):
            log_obj['performance_log'] = record.performance_log
        if hasattr(record, 'api_log'):
            log_obj['api_log'] = record.api_log
            
        # Add any other extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                if key not in log_obj:
                    log_obj[key] = value
        
        return json.dumps(log_obj, default=str)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def __init__(self):
        """Initialize formatter with custom format."""
        fmt = '%(asctime)s - %(levelname)-8s - %(name)-25s - %(message)s'
        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.
        
        Args:
            record: Log record to format
            
        Returns:
            Colored formatted log string
        """
        # Get base formatted string
        log_str = super().format(record)
        
        # Apply color based on level
        color = self.COLORS.get(record.levelname, '')
        if color:
            # Color the level name
            log_str = log_str.replace(
                record.levelname,
                f"{color}{self.BOLD}{record.levelname}{self.RESET}",
                1
            )
            
            # Color the message for errors and warnings
            if record.levelname in ['ERROR', 'CRITICAL']:
                parts = log_str.split(' - ')
                if len(parts) >= 4:
                    parts[-1] = f"{color}{parts[-1]}{self.RESET}"
                    log_str = ' - '.join(parts)
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_str += f" [{record.request_id[:8]}]"
        
        # Add performance metrics if available
        if hasattr(record, 'duration_ms'):
            log_str += f" ({record.duration_ms}ms)"
        
        return log_str