"""
Performance monitoring and metrics
"""
from prometheus_flask_exporter import PrometheusMetrics
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self, app=None):
        self.metrics = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize monitoring with Flask app"""
        # Configure Prometheus metrics
        self.metrics = PrometheusMetrics(app)
        
        # Define custom metrics
        self.metrics.info('aruco_generator_info', 'Application info', 
                         version='1.0.0', environment=app.config.get('ENV', 'development'))
        
        # Counter for API calls
        self.api_calls = self.metrics.counter(
            'api_calls', 'Number of API calls',
            labels={'endpoint': lambda: request.endpoint, 'method': lambda: request.method}
        )
        
        # Histogram for response times
        self.response_time = self.metrics.histogram(
            'response_time_seconds', 'Response time in seconds',
            labels={'endpoint': lambda: request.endpoint}
        )
        
        # Gauge for active tasks
        self.active_tasks = self.metrics.gauge(
            'active_tasks', 'Number of active background tasks'
        )
        
        # Counter for errors
        self.error_counter = self.metrics.counter(
            'errors', 'Number of errors',
            labels={'type': lambda: 'unknown'}
        )
        
        return self.metrics

def track_performance(metric_name='operation'):
    """Decorator to track function performance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Log performance
                duration = time.time() - start_time
                logger.info(f"{metric_name} completed in {duration:.3f}s")
                
                return result
                
            except Exception as e:
                # Log error
                duration = time.time() - start_time
                logger.error(f"{metric_name} failed after {duration:.3f}s: {e}")
                raise
                
        return decorated_function
    return decorator

class RequestTimer:
    """Context manager for timing requests"""
    
    def __init__(self, name='request'):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.info(f"{self.name} completed in {duration:.3f}s")
        else:
            logger.error(f"{self.name} failed after {duration:.3f}s")

def log_slow_request(threshold=1.0):
    """Log requests that exceed threshold"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            result = f(*args, **kwargs)
            
            duration = time.time() - start_time
            if duration > threshold:
                logger.warning(f"Slow request: {f.__name__} took {duration:.3f}s (threshold: {threshold}s)")
            
            return result
            
        return decorated_function
    return decorator