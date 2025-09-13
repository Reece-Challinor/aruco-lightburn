"""API endpoints for log management and frontend logging."""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from backend.core.logging import get_logger

bp = Blueprint('logs', __name__, url_prefix='/logs')
logger = get_logger(__name__)


@bp.route('/batch', methods=['POST'])
def receive_frontend_logs():
    """Receive and process frontend logs in batch.
    
    Returns:
        JSON response with status
    """
    try:
        data = request.get_json()
        
        if not data or 'logs' not in data:
            return jsonify({'error': 'No logs provided'}), 400
        
        logs = data.get('logs', [])
        session_id = data.get('sessionId', 'unknown')
        
        # Process each log entry
        for log_entry in logs:
            level = log_entry.get('level', 'INFO')
            message = f"[Frontend] {log_entry.get('message', 'No message')}"
            context = log_entry.get('context', {})
            
            # Add session ID to context
            context['frontend_session_id'] = session_id
            context['frontend_timestamp'] = log_entry.get('timestamp')
            
            # Log based on level
            if level == 'DEBUG':
                logger.debug(message, **context)
            elif level == 'INFO':
                logger.info(message, **context)
            elif level == 'WARNING':
                logger.warning(message, **context)
            elif level == 'ERROR':
                logger.error(message, **context)
            elif level == 'CRITICAL':
                logger.critical(message, **context)
            else:
                logger.info(message, **context)
        
        logger.info(f"Processed {len(logs)} frontend logs from session {session_id}")
        
        return jsonify({
            'status': 'success',
            'processed': len(logs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing frontend logs: {e}", exc_info=True)
        return jsonify({'error': 'Failed to process logs'}), 500


@bp.route('/query', methods=['GET'])
def query_logs():
    """Query logs with filters.
    
    Query parameters:
        - level: Log level filter
        - start_time: Start timestamp
        - end_time: End timestamp
        - request_id: Specific request ID
        - limit: Maximum number of logs to return
    
    Returns:
        JSON array of matching log entries
    """
    try:
        # Get query parameters
        level = request.args.get('level')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        request_id = request.args.get('request_id')
        limit = int(request.args.get('limit', 100))
        
        # TODO: Implement actual log querying from log files
        # For now, return a message indicating the feature is in development
        
        return jsonify({
            'message': 'Log querying endpoint active',
            'filters': {
                'level': level,
                'start_time': start_time,
                'end_time': end_time,
                'request_id': request_id,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error querying logs: {e}", exc_info=True)
        return jsonify({'error': 'Failed to query logs'}), 500


@bp.route('/levels', methods=['GET'])
def get_log_levels():
    """Get available log levels.
    
    Returns:
        JSON array of log levels
    """
    return jsonify({
        'levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    }), 200