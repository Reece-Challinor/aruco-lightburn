"""
Simplified Flask routes for ArUCO generator
"""

import io
import logging
from datetime import datetime
from flask import render_template, request, jsonify, send_file
from app import app
from .aruco import ArUCOGenerator
from .lightburn import LightBurnExporter
from .drawing import DrawingContext

# Initialize core components
aruco_gen = ArUCOGenerator()
lightburn_exporter = LightBurnExporter()
logger = logging.getLogger(__name__)


# Page routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('home.html')


@app.route('/generate')
def generate_page():
    """Generate markers page"""
    return render_template('generate.html', dictionaries={})


# Calibration route is defined in calibration_web.py


@app.route('/validation')
def validation_page():
    """Validation page"""
    return render_template('validation.html')


@app.route('/documentation')
def documentation_page():
    """Documentation page"""
    return render_template('documentation.html')


# API endpoints - simplified without service layer
@app.route('/api/dictionaries')
def get_dictionaries():
    """Get available ArUCO dictionaries"""
    return jsonify(aruco_gen.get_dictionary_info())


@app.route('/api/preview', methods=['POST'])
def generate_preview():
    """Generate SVG preview of markers"""
    try:
        data = request.get_json()
        
        # Extract and validate parameters
        dictionary = data.get('dictionary')
        if not dictionary or dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': 'Invalid dictionary'}), 400
            
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        border_bits = int(data.get('border_bits', 1))
        
        # Validate ranges
        if start_id < 0 or rows <= 0 or cols <= 0 or size_mm <= 0:
            return jsonify({'error': 'Invalid parameters'}), 400
        
        # Generate markers - fixed parameter order
        markers = aruco_gen.generate_grid(
            start_id=start_id,
            dict_name=dictionary,
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm
        )
        
        # Prepare markers for drawing
        marker_data = []
        for marker_info in markers:
            marker_data.append({
                'x': marker_info['x'],
                'y': marker_info['y'],
                'size': marker_info['size'],
                'id': marker_info['id'],
                'image': marker_info.get('image')
            })
        
        # Create drawing context and generate SVG
        ctx = DrawingContext()
        ctx.add_marker_grid_preview(
            marker_data,
            include_borders=True,
            include_outer_border=data.get('include_outer_border', False),
            border_width=float(data.get('border_width', 2.0))
        )
        
        # Add labels if requested
        if data.get('include_labels'):
            ctx.add_text_labels(marker_data)
        
        svg_content = ctx.get_svg()
        
        # Calculate dimensions
        total_width, total_height = aruco_gen.calculate_total_size(
            rows, cols, size_mm, spacing_mm
        )
        
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
        
        # Extract and validate parameters
        dictionary = data.get('dictionary')
        if not dictionary or dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': 'Invalid dictionary'}), 400
            
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        border_bits = int(data.get('border_bits', 1))
        
        # Generate markers - fixed parameter order
        markers = aruco_gen.generate_grid(
            start_id=start_id,
            dict_name=dictionary,
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm
        )
        
        # Generate LightBurn file
        lightburn_content = lightburn_exporter.create_lightburn_file(
            markers=markers,
            size_mm=size_mm,
            border_bits=border_bits,
            include_labels=data.get('include_labels', False),
            include_alignment=data.get('include_alignment', False),
            include_rulers=data.get('include_rulers', False)
        )
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"aruco_{dictionary}_{rows}x{cols}_{timestamp}.lbrn2"
        
        return send_file(
            io.BytesIO(lightburn_content.encode('utf-8')),
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/advanced_preview', methods=['POST'])
def generate_advanced_preview():
    """Generate advanced preview with additional options"""
    try:
        data = request.get_json()

        # Extract parameters (similar to regular preview)
        dictionary = data.get('dictionary')
        if not dictionary or dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': 'Invalid dictionary'}), 400

        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        border_bits = int(data.get('border_bits', 1))
        include_borders = data.get('include_borders', False)
        include_labels = data.get('include_labels', False)

        # Generate markers
        markers = aruco_gen.generate_grid(
            start_id=start_id,
            dict_name=dictionary,
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm
        )

        # Create drawing context and generate SVG with advanced options
        ctx = DrawingContext()
        ctx.add_marker_grid_preview(
            markers=markers,
            size_mm=size_mm,
            spacing_mm=spacing_mm,
            include_borders=include_borders
        )

        if include_labels:
            for marker in markers:
                ctx.add_text(
                    text=f"ID: {marker['id']}",
                    x=marker['x'] + size_mm / 2,
                    y=marker['y'] - 2
                )

        svg_content = ctx.to_svg()
        total_width, total_height = aruco_gen.calculate_total_size(
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm
        )

        return jsonify({
            'svg': svg_content,
            'count': len(markers),
            'dimensions': {
                'width': total_width,
                'height': total_height
            }
        })

    except Exception as e:
        logger.error(f"Advanced preview error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch_generate', methods=['POST'])
def batch_generate():
    """Generate multiple sets of markers"""
    try:
        data = request.get_json()

        sets = int(data.get('sets', 1))
        markers_per_set = int(data.get('markers_per_set', 5))
        start_id = int(data.get('start_id', 0))
        dictionary = data.get('dictionary', '4X4_250')
        size_mm = float(data.get('size_mm', 30))
        spacing_mm = float(data.get('spacing_mm', 5))

        if dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': 'Invalid dictionary'}), 400

        all_markers = []
        for set_idx in range(sets):
            set_start_id = start_id + (set_idx * markers_per_set)

            # Calculate grid dimensions for this set
            cols = min(markers_per_set, 5)
            rows = (markers_per_set + cols - 1) // cols

            markers = aruco_gen.generate_grid(
                start_id=set_start_id,
                dict_name=dictionary,
                rows=rows,
                cols=cols,
                size_mm=size_mm,
                spacing_mm=spacing_mm,
                generate_images=False  # Don't generate images for batch
            )

            all_markers.append({
                'set_index': set_idx,
                'markers': markers,
                'start_id': set_start_id,
                'end_id': set_start_id + markers_per_set - 1
            })

        return jsonify({
            'sets': all_markers,
            'total_markers': sets * markers_per_set,
            'dictionary': dictionary
        })

    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/presets')
def get_presets():
    """Get predefined marker configuration presets"""
    presets = {
        'business_cards': {
            'name': 'Business Card Size',
            'dictionary': '4X4_50',
            'size_mm': 15,
            'spacing_mm': 5,
            'rows': 2,
            'cols': 3,
            'description': 'Fits on standard business card'
        },
        'inventory_tags': {
            'name': 'Inventory Tags',
            'dictionary': '6X6_250',
            'size_mm': 25,
            'spacing_mm': 10,
            'rows': 4,
            'cols': 4,
            'description': 'For warehouse inventory tracking'
        },
        'drone_landing': {
            'name': 'Drone Landing Pad',
            'dictionary': '7X7_50',
            'size_mm': 100,
            'spacing_mm': 20,
            'rows': 3,
            'cols': 3,
            'description': 'Large markers for drone navigation'
        },
        'camera_calibration': {
            'name': 'Camera Calibration',
            'dictionary': '4X4_100',
            'size_mm': 40,
            'spacing_mm': 10,
            'rows': 5,
            'cols': 7,
            'description': 'Standard camera calibration grid'
        }
    }

    return jsonify(presets)


@app.route('/api/export/svg', methods=['POST'])
def export_svg():
    """Export markers as SVG file"""
    try:
        data = request.get_json()
        
        # Extract and validate parameters (same as preview)
        dictionary = data.get('dictionary')
        if not dictionary or dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': 'Invalid dictionary'}), 400
            
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        
        # Generate markers with actual images
        markers = aruco_gen.generate_grid(
            start_id=start_id,
            dict_name=dictionary,
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm
        )
        
        # Create drawing context and generate SVG with merged rectangles
        ctx = DrawingContext()
        ctx.add_marker_grid(markers, 
                          include_borders=data.get('include_borders', True),
                          include_outer_border=data.get('include_outer_border', False))
        
        if data.get('include_labels'):
            ctx.add_text_labels(markers)
        
        svg_content = ctx.get_svg()
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"aruco_{dictionary}_{rows}x{cols}_{timestamp}.svg"
        
        return send_file(
            io.BytesIO(svg_content.encode('utf-8')),
            as_attachment=True,
            download_name=filename,
            mimetype='image/svg+xml'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"SVG export error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Export markers as PDF file (placeholder for now)"""
    try:
        # For now, return a JSON response indicating PDF export is not yet implemented
        return jsonify({'error': 'PDF export is not yet implemented'}), 501
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/quick-test')
def quick_test():
    """Quick test endpoint to verify API is working"""
    try:
        # Generate a simple test marker - fixed argument order
        test_marker = aruco_gen.generate_marker(0, "4X4_50", 200)
        return jsonify({
            'status': 'success',
            'message': 'API is working',
            'test_marker_shape': test_marker.shape if hasattr(test_marker, 'shape') else 'Generated',
            'available_dictionaries': len(aruco_gen.dictionaries),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Quick test failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Debug endpoints (can be removed in production)
@app.route('/api/debug/status')
def debug_status():
    """Debug status endpoint"""
    try:
        import cv2
        opencv_version = cv2.__version__
    except:
        opencv_version = 'Not available'
    
    return jsonify({
        'status': 'operational',
        'opencv': opencv_version,
        'dictionaries': len(aruco_gen.dictionaries),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/log-error', methods=['POST'])
def log_error():
    """Log frontend errors"""
    try:
        error_data = request.get_json()
        logger.error(f"Frontend error: {error_data}")
        return jsonify({'status': 'logged'}), 200
    except Exception as e:
        logger.error(f"Failed to log frontend error: {e}")
        return jsonify({'status': 'failed'}), 500