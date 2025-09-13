"""
Simplified Flask routes for ArUCO generator - delegates to unified API services
"""

import os
import logging
from datetime import datetime
from flask import render_template, request, jsonify, send_file
from .aruco import ArUCOGenerator
from .lightburn import LightBurnExporter
from backend.services.marker_service import MarkerService
from backend.repositories.marker_repository import MarkerRepository
from app import app
import io

# Initialize core components
aruco_gen = ArUCOGenerator()
lightburn_exporter = LightBurnExporter()
marker_repository = MarkerRepository()
marker_service = MarkerService(aruco_gen, lightburn_exporter, marker_repository)

logger = logging.getLogger(__name__)

# Page routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('home.html')

@app.route('/generate')
def generate_page():
    """Generate markers page"""
    # Pass empty dictionaries since they're loaded via JavaScript
    return render_template('generate.html', dictionaries={})

@app.route('/calibration')
def calibration_page():
    """Calibration patterns page"""
    return render_template('calibration.html')

@app.route('/validation')
def validation_page():
    """Validation page"""
    return render_template('validation.html')

@app.route('/documentation')
def documentation_page():
    """Documentation page"""
    return render_template('documentation.html')

# API endpoints - delegate to unified service
@app.route('/api/dictionaries')
def get_dictionaries():
    """Get available ArUCO dictionaries"""
    return jsonify(marker_service.get_dictionary_info())

@app.route('/api/preview', methods=['POST'])
def generate_preview():
    """Generate SVG preview of markers"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate preview using service
        svg_content = marker_service.generate_preview(data)
        
        # Calculate dimensions for response
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        
        total_width, total_height = aruco_gen.calculate_total_size(rows, cols, size_mm, spacing_mm)
        
        if data.get('include_labels'):
            total_height += 6
        
        if data.get('include_outer_border'):
            border_width = float(data.get('border_width', 2.0))
            total_width += 2 * border_width
            total_height += 2 * border_width
        
        return jsonify({
            'svg': svg_content,
            'dimensions': {
                'width': round(total_width, 2),
                'height': round(total_height, 2)
            },
            'total_width': total_width,
            'total_height': total_height,
            'marker_count': rows * cols,
            'success': True
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Preview generation error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_lightburn():
    """Generate and download LightBurn file"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate export using service
        export_data = marker_service.export_markers(data, 'lightburn')
        
        return send_file(
            io.BytesIO(export_data['content']),
            as_attachment=True,
            download_name=export_data['filename'],
            mimetype=export_data['mimetype']
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# Quick test endpoints
@app.route('/api/quick-test', methods=['GET'])
def quick_test():
    """Generate a quick test marker"""
    try:
        # Use default test parameters
        test_data = {
            'dictionary': '4X4_50',
            'start_id': 0,
            'rows': 1,
            'cols': 1,
            'size_mm': 50,
            'spacing_mm': 0,
            'include_borders': True,
            'include_labels': True
        }
        
        # Generate using service
        result = marker_service.generate_markers(test_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Quick test marker generated',
            'marker': result
        })
        
    except Exception as e:
        logger.error(f"Quick test error: {e}")
        return jsonify({'error': f'Quick test failed: {str(e)}'}), 500

@app.route('/api/quick-test/download', methods=['GET'])
def download_quick_test():
    """Download a quick test LightBurn file"""
    try:
        # Use default test parameters
        test_data = {
            'dictionary': '4X4_50',
            'start_id': 0,
            'rows': 3,
            'cols': 3,
            'size_mm': 30,
            'spacing_mm': 5,
            'include_borders': True,
            'include_labels': True
        }
        
        # Generate export
        export_data = marker_service.export_markers(test_data, 'lightburn')
        
        return send_file(
            io.BytesIO(export_data['content']),
            as_attachment=True,
            download_name='quick_test.lbrn2',
            mimetype='application/xml'
        )
        
    except Exception as e:
        logger.error(f"Quick test download error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# Presets endpoint
@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get marker generation presets"""
    presets = {
        'test_sheet': {
            'name': 'Test Sheet',
            'description': 'Standard test grid',
            'dictionary': '4X4_50',
            'rows': 3,
            'cols': 3,
            'size_mm': 30,
            'spacing_mm': 5,
            'include_borders': True,
            'include_labels': True
        },
        'business_cards': {
            'name': 'Business Cards',
            'description': 'Small markers for business cards',
            'dictionary': '4X4_50',
            'rows': 2,
            'cols': 5,
            'size_mm': 15,
            'spacing_mm': 3,
            'include_borders': True,
            'include_labels': False
        },
        'inventory_tags': {
            'name': 'Inventory Tags',
            'description': 'Medium markers for inventory management',
            'dictionary': '4X4_100',
            'rows': 5,
            'cols': 10,
            'size_mm': 10,
            'spacing_mm': 2,
            'include_borders': True,
            'include_labels': True
        },
        'large_markers': {
            'name': 'Large Display Markers',
            'description': 'Large markers for wall displays',
            'dictionary': '6X6_50',
            'rows': 1,
            'cols': 1,
            'size_mm': 50,
            'spacing_mm': 10,
            'include_borders': True,
            'include_labels': True
        },
        'production_run': {
            'name': 'Production Run',
            'description': 'Large batch for production',
            'dictionary': '5X5_250',
            'rows': 10,
            'cols': 10,
            'size_mm': 8,
            'spacing_mm': 1,
            'include_borders': False,
            'include_labels': False
        }
    }
    return jsonify(presets)

# Batch generation endpoint
@app.route('/api/batch_generate', methods=['POST'])
def batch_generate():
    """Generate batch of markers"""
    try:
        data = request.get_json()
        batch_config = data.get('batch_config', [])
        
        if not batch_config:
            return jsonify({'error': 'No batch configuration provided'}), 400
        
        # Use service for batch generation
        results = marker_service.generate_batch(batch_config)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r.get('status') == 'success'])
        })
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({'error': f'Batch generation failed: {str(e)}'}), 500

# Export endpoints for different formats
@app.route('/api/export/<format>', methods=['POST'])
def export_format(format):
    """Export markers in specified format"""
    try:
        if format not in ['svg', 'lightburn', 'json', 'yaml', 'dxf', 'stl']:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
        
        data = request.get_json()
        
        # Validate input
        errors = marker_service.validate_marker_params(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Handle special export formats not in marker_service
        if format == 'yaml':
            # Export as YAML calibration data
            import yaml
            markers = marker_service.generate_markers(data)
            yaml_data = yaml.dump(markers, default_flow_style=False)
            
            return send_file(
                io.BytesIO(yaml_data.encode()),
                as_attachment=True,
                download_name=f"aruco_{data.get('dictionary')}_{data.get('rows')}x{data.get('cols')}.yaml",
                mimetype='text/yaml'
            )
        
        elif format == 'dxf':
            # DXF export placeholder
            return jsonify({'error': 'DXF export not yet implemented'}), 501
        
        elif format == 'stl':
            # STL export placeholder
            return jsonify({'error': 'STL export not yet implemented'}), 501
        
        else:
            # Use service for standard formats
            export_data = marker_service.export_markers(data, format)
            
            return send_file(
                io.BytesIO(export_data['content']),
                as_attachment=True,
                download_name=export_data['filename'],
                mimetype=export_data['mimetype']
            )
        
    except Exception as e:
        logger.error(f"Export error for format {format}: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500