"""
Real-time detection endpoints
"""
from flask import Blueprint, request, jsonify
import logging
import base64
import cv2
import numpy as np
from backend.services.detection_service import DetectionService

bp = Blueprint('detection', __name__, url_prefix='/detection')
logger = logging.getLogger(__name__)

# Initialize detection service
detection_service = DetectionService()

@bp.route('/detect', methods=['POST'])
def detect_markers():
    """Detect ArUCO markers in uploaded image"""
    try:
        data = request.get_json()
        
        # Get image data
        image_data = data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Detect markers
        dictionary = data.get('dictionary', 'DICT_4X4_50')
        detections = detection_service.detect_markers(image, dictionary)
        
        return jsonify({
            'detections': detections,
            'count': len(detections),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({'error': f'Detection failed: {str(e)}'}), 500

@bp.route('/stream/start', methods=['POST'])
def start_stream():
    """Start real-time detection stream"""
    try:
        data = request.get_json()
        session_id = detection_service.start_stream_session(data)
        
        return jsonify({
            'session_id': session_id,
            'status': 'started'
        }), 200
        
    except Exception as e:
        logger.error(f"Stream start error: {e}")
        return jsonify({'error': 'Failed to start stream'}), 500

@bp.route('/stream/stop/<session_id>', methods=['POST'])
def stop_stream(session_id):
    """Stop real-time detection stream"""
    try:
        detection_service.stop_stream_session(session_id)
        
        return jsonify({
            'session_id': session_id,
            'status': 'stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"Stream stop error: {e}")
        return jsonify({'error': 'Failed to stop stream'}), 500

@bp.route('/analyze', methods=['POST'])
def analyze_detection():
    """Analyze detection quality and provide feedback"""
    try:
        data = request.get_json()
        
        # Get image and detection data
        image_data = data.get('image')
        detections = data.get('detections', [])
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Analyze detection quality
        analysis = detection_service.analyze_detection_quality(image_data, detections)
        
        return jsonify({
            'analysis': analysis,
            'recommendations': detection_service.get_recommendations(analysis),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@bp.route('/calibrate', methods=['POST'])
def calibrate_detection():
    """Calibrate detection parameters"""
    try:
        data = request.get_json()
        
        # Calibrate detection parameters
        calibration = detection_service.calibrate_detection(data)
        
        return jsonify({
            'calibration': calibration,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Calibration error: {e}")
        return jsonify({'error': 'Calibration failed'}), 500