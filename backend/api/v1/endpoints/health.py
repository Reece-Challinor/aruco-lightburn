"""
Health check endpoints
"""
from flask import Blueprint, jsonify
import logging
import psutil
import os
from datetime import datetime
from app import db

bp = Blueprint('health', __name__, url_prefix='/health')
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'ArUCO Generator API'
    }), 200

@bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check - verifies all dependencies are available"""
    try:
        checks = {
            'database': check_database(),
            'opencv': check_opencv(),
            'filesystem': check_filesystem(),
        }
        
        all_ready = all(checks.values())
        status_code = 200 if all_ready else 503
        
        return jsonify({
            'ready': all_ready,
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), status_code
        
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        return jsonify({
            'ready': False,
            'error': str(e)
        }), 503

@bp.route('/live', methods=['GET'])
def liveness_check():
    """Liveness check - simple ping to verify service is running"""
    return jsonify({
        'alive': True,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        
        metrics = {
            'cpu': {
                'usage_percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'process': {
                'pid': os.getpid(),
                'threads': psutil.Process().num_threads()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@bp.route('/status', methods=['GET'])
def detailed_status():
    """Get detailed service status"""
    try:
        status = {
            'service': 'ArUCO Generator API',
            'version': '1.0.0',
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'uptime': get_uptime(),
            'database': {
                'connected': check_database(),
                'type': 'postgresql'
            },
            'features': {
                'marker_generation': True,
                'detection': True,
                'calibration': True,
                'export': True,
                'batch_processing': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'error': 'Failed to fetch status'}), 500

def check_database():
    """Check database connectivity"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

def check_opencv():
    """Check OpenCV availability"""
    try:
        import cv2
        return cv2.__version__ is not None
    except Exception:
        return False

def check_filesystem():
    """Check filesystem write permissions"""
    try:
        test_file = '/tmp/health_check_test.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception:
        return False

def get_uptime():
    """Get service uptime"""
    try:
        process = psutil.Process(os.getpid())
        create_time = datetime.fromtimestamp(process.create_time())
        uptime = datetime.now() - create_time
        return str(uptime)
    except Exception:
        return "unknown"