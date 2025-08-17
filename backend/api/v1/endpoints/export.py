"""
Export format endpoints
"""
from flask import Blueprint, request, jsonify, send_file
import logging
import io
from backend.services.export_service import ExportService

bp = Blueprint('export', __name__, url_prefix='/export')
logger = logging.getLogger(__name__)

# Initialize export service
export_service = ExportService()

@bp.route('/formats', methods=['GET'])
def get_export_formats():
    """Get available export formats"""
    try:
        formats = export_service.get_available_formats()
        return jsonify(formats), 200
    except Exception as e:
        logger.error(f"Error fetching formats: {e}")
        return jsonify({'error': 'Failed to fetch formats'}), 500

@bp.route('/lightburn', methods=['POST'])
def export_lightburn():
    """Export to LightBurn format"""
    try:
        data = request.get_json()
        
        # Generate LightBurn file
        file_data, filename = export_service.export_lightburn(data)
        
        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/xml'
        )
        
    except Exception as e:
        logger.error(f"LightBurn export error: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@bp.route('/svg', methods=['POST'])
def export_svg():
    """Export to SVG format"""
    try:
        data = request.get_json()
        
        # Generate SVG
        svg_data, filename = export_service.export_svg(data)
        
        return send_file(
            io.BytesIO(svg_data.encode()),
            as_attachment=True,
            download_name=filename,
            mimetype='image/svg+xml'
        )
        
    except Exception as e:
        logger.error(f"SVG export error: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@bp.route('/pdf', methods=['POST'])
def export_pdf():
    """Export to PDF format"""
    try:
        data = request.get_json()
        
        # Generate PDF
        pdf_data, filename = export_service.export_pdf(data)
        
        return send_file(
            io.BytesIO(pdf_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@bp.route('/dxf', methods=['POST'])
def export_dxf():
    """Export to DXF format"""
    try:
        data = request.get_json()
        
        # Generate DXF
        dxf_data, filename = export_service.export_dxf(data)
        
        return send_file(
            io.BytesIO(dxf_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/dxf'
        )
        
    except Exception as e:
        logger.error(f"DXF export error: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@bp.route('/batch', methods=['POST'])
def batch_export():
    """Batch export in multiple formats"""
    try:
        data = request.get_json()
        formats = data.get('formats', ['svg', 'pdf'])
        
        # Generate batch export
        results = export_service.batch_export(data, formats)
        
        return jsonify({
            'exports': results,
            'count': len(results),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Batch export error: {e}")
        return jsonify({'error': 'Batch export failed'}), 500

@bp.route('/preview', methods=['POST'])
def preview_export():
    """Preview export result"""
    try:
        data = request.get_json()
        format = data.get('format', 'svg')
        
        # Generate preview
        preview_data = export_service.generate_preview(data, format)
        
        return jsonify({
            'preview': preview_data,
            'format': format,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return jsonify({'error': 'Preview generation failed'}), 500