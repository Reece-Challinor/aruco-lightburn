"""
Marker generation endpoints
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import logging
import io
from aruco_generator.aruco import ArUCOGenerator
from aruco_generator.drawing import DrawingContext
from aruco_generator.lightburn import LightBurnExporter
from backend.services.marker_service import MarkerService
from backend.repositories.marker_repository import MarkerRepository

bp = Blueprint('markers', __name__, url_prefix='/markers')
logger = logging.getLogger(__name__)

# Initialize services
aruco_gen = ArUCOGenerator()
lightburn_exporter = LightBurnExporter()
marker_repository = MarkerRepository()
marker_service = MarkerService(aruco_gen, lightburn_exporter, marker_repository)

@bp.route('/dictionaries', methods=['GET'])
def get_dictionaries():
    """Get available ArUCO dictionaries"""
    try:
        dictionaries = marker_service.get_dictionary_info()
        return jsonify(dictionaries), 200
    except Exception as e:
        logger.error(f"Error fetching dictionaries: {e}")
        return jsonify({'error': 'Failed to fetch dictionaries'}), 500

@bp.route('/generate', methods=['POST'])
def generate_markers():
    """Generate ArUCO markers"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate markers
        result = marker_service.generate_markers(data)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': 'Failed to generate markers'}), 500

@bp.route('/preview', methods=['POST'])
def preview_markers():
    """Generate SVG preview of markers"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate preview
        svg_content = marker_service.generate_preview(data)
        
        return jsonify({
            'svg': svg_content,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return jsonify({'error': 'Failed to generate preview'}), 500

@bp.route('/export/<format>', methods=['POST'])
def export_markers(format):
    """Export markers in specified format"""
    try:
        if format not in ['svg', 'lightburn', 'pdf']:
            return jsonify({'error': 'Invalid export format'}), 400
        
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate export
        file_data, filename, mimetype = marker_service.export_markers(data, format)
        
        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': f'Failed to export markers: {str(e)}'}), 500

@bp.route('/batch', methods=['POST'])
def batch_generate():
    """Generate batch of markers"""
    try:
        data = request.get_json()
        
        # Validate batch parameters
        batch_config = data.get('batch_config', [])
        if not batch_config:
            return jsonify({'error': 'No batch configuration provided'}), 400
        
        # Process batch
        results = marker_service.generate_batch(batch_config)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({'error': 'Failed to generate batch'}), 500

@bp.route('/validate', methods=['POST'])
def validate_markers():
    """Validate marker parameters"""
    try:
        data = request.get_json()
        errors = marker_service.validate_marker_params(data)
        
        if errors:
            return jsonify({'valid': False, 'errors': errors}), 400
        
        return jsonify({'valid': True}), 200
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': 'Validation failed'}), 500