"""
Simple marker generation endpoints without enhanced features
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import logging
import io
from aruco_generator.aruco import ArUCOGenerator
from aruco_generator.drawing import DrawingContext
from backend.services.marker_service import MarkerService
from backend.repositories.marker_repository import MarkerRepository

bp = Blueprint('markers', __name__, url_prefix='/markers')
logger = logging.getLogger(__name__)

# Initialize services
from aruco_generator.lightburn import LightBurnExporter

generator = ArUCOGenerator()
repository = MarkerRepository()
lightburn_exporter = LightBurnExporter()
marker_service = MarkerService(generator, lightburn_exporter, repository)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'markers'}), 200

@bp.route('/generate', methods=['POST'])
def generate_markers():
    """Generate ArUCO markers"""
    try:
        data = request.get_json()
        
        # Basic validation
        if not data or 'dictionary' not in data:
            return jsonify({'error': 'Dictionary type is required'}), 400
        
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
        
        # Basic validation
        if not data or 'dictionary' not in data:
            return jsonify({'error': 'Dictionary type is required'}), 400
        
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
        data = request.get_json()
        
        if format not in ['svg', 'pdf', 'png', 'yaml', 'json', 'lightburn']:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
        
        # Generate export
        export_data = marker_service.export_markers(data, format)
        
        # Return file
        return send_file(
            io.BytesIO(export_data['content']),
            mimetype=export_data['mimetype'],
            as_attachment=True,
            download_name=export_data['filename']
        )
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': f'Failed to export as {format}'}), 500