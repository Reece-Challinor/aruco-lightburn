"""
Calibration tools endpoints
"""
from flask import Blueprint, request, jsonify, send_file
import logging
import io
from backend.services.calibration_service import CalibrationService

bp = Blueprint('calibration', __name__, url_prefix='/calibration')
logger = logging.getLogger(__name__)

# Initialize calibration service
calibration_service = CalibrationService()

@bp.route('/patterns', methods=['GET'])
def get_calibration_patterns():
    """Get available calibration patterns"""
    try:
        patterns = calibration_service.get_available_patterns()
        return jsonify(patterns), 200
    except Exception as e:
        logger.error(f"Error fetching patterns: {e}")
        return jsonify({'error': 'Failed to fetch patterns'}), 500

@bp.route('/generate', methods=['POST'])
def generate_calibration_pattern():
    """Generate calibration pattern"""
    try:
        data = request.get_json()
        
        pattern_type = data.get('pattern_type', 'chessboard')
        rows = data.get('rows', 9)
        cols = data.get('cols', 6)
        square_size = data.get('square_size', 30)  # in mm
        
        # Generate pattern
        pattern_data, filename = calibration_service.generate_pattern(
            pattern_type, rows, cols, square_size
        )
        
        return send_file(
            io.BytesIO(pattern_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Pattern generation error: {e}")
        return jsonify({'error': 'Failed to generate pattern'}), 500

@bp.route('/calibrate', methods=['POST'])
def calibrate_camera():
    """Calibrate camera from images"""
    try:
        data = request.get_json()
        images = data.get('images', [])
        
        if not images:
            return jsonify({'error': 'No calibration images provided'}), 400
        
        # Perform calibration
        calibration_result = calibration_service.calibrate_camera(images, data)
        
        return jsonify({
            'calibration': calibration_result,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Calibration error: {e}")
        return jsonify({'error': f'Calibration failed: {str(e)}'}), 500

@bp.route('/validate', methods=['POST'])
def validate_calibration():
    """Validate calibration results"""
    try:
        data = request.get_json()
        calibration_data = data.get('calibration')
        
        if not calibration_data:
            return jsonify({'error': 'No calibration data provided'}), 400
        
        # Validate calibration
        validation = calibration_service.validate_calibration(calibration_data)
        
        return jsonify({
            'validation': validation,
            'is_valid': validation['is_valid'],
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': 'Validation failed'}), 500

@bp.route('/save', methods=['POST'])
def save_calibration():
    """Save calibration data"""
    try:
        data = request.get_json()
        calibration_data = data.get('calibration')
        name = data.get('name', 'default')
        
        if not calibration_data:
            return jsonify({'error': 'No calibration data provided'}), 400
        
        # Save calibration
        saved_id = calibration_service.save_calibration(calibration_data, name)
        
        return jsonify({
            'id': saved_id,
            'message': 'Calibration saved successfully',
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Save error: {e}")
        return jsonify({'error': 'Failed to save calibration'}), 500

@bp.route('/load/<calibration_id>', methods=['GET'])
def load_calibration(calibration_id):
    """Load saved calibration"""
    try:
        calibration = calibration_service.load_calibration(calibration_id)
        
        if not calibration:
            return jsonify({'error': 'Calibration not found'}), 404
        
        return jsonify({
            'calibration': calibration,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Load error: {e}")
        return jsonify({'error': 'Failed to load calibration'}), 500