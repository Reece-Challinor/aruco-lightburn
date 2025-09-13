"""
Simplified marker generation endpoints
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
        if format not in ['svg', 'lightburn', 'pdf', 'json']:
            return jsonify({'error': 'Invalid export format'}), 400
        
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate export
        export_data = marker_service.export_markers(data, format)
        
        return send_file(
            io.BytesIO(export_data['content']),
            as_attachment=True,
            download_name=export_data['filename'],
            mimetype=export_data['mimetype']
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
        
        # Generate batch
        results = marker_service.generate_batch(batch_config)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r.get('status') == 'success'])
        }), 200
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({'error': f'Failed to generate batch: {str(e)}'}), 500

# Add health check
@bp.route('/health', methods=['GET'])
def health_check():
    """Check markers API health"""
    return jsonify({
        'status': 'healthy',
        'service': 'markers',
        'timestamp': datetime.utcnow().isoformat()
    }), 200