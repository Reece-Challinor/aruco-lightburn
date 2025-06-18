"""
{
  "file_type": "flask_routes",
  "purpose": "All Flask routes and API endpoints for ArUCO generator",
  "routes": {
    "/": "Main application page with streamlined UI",
    "/api/dictionaries": "Get available ArUCO dictionaries",
    "/api/preview": "Generate SVG preview",
    "/api/download": "Download LightBurn file",
    "/api/quick-test": "Quick test generation",
    "/api/quick-test/download": "Download quick test file"
  },
  "dependencies": ["aruco.py", "drawing.py", "lightburn.py", "batch.py"],
  "ai_navigation": {
    "modify_for": "Adding new routes or API endpoints",
    "frontend_integration": "static/app.js calls these endpoints",
    "ui_templates": "templates/index.html"
  }
}
"""

import os
import logging
import traceback
from datetime import datetime
from flask import render_template, request, jsonify, send_file
from .aruco import ArUCOGenerator
from .drawing import DrawingContext
from .lightburn import LightBurnExporter
from .batch import BatchGenerator

# Get Flask app from main app.py
from app import app

# Initialize generators
aruco_gen = ArUCOGenerator()
lightburn_exporter = LightBurnExporter()

@app.route('/')
def index():
    """Main application page"""
    dictionaries = aruco_gen.get_dictionary_info()
    return render_template('index.html', dictionaries=dictionaries)

@app.route('/api/dictionaries')
def get_dictionaries():
    """API endpoint to get available ArUCO dictionaries"""
    return jsonify(aruco_gen.get_dictionary_info())

@app.route('/api/preview', methods=['POST'])
def generate_preview():
    """Generate SVG preview of markers"""
    try:
        data = request.get_json()
        
        # Validate input parameters
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        include_borders = data.get('include_borders', True)
        include_labels = data.get('include_labels', True)
        include_outer_border = data.get('include_outer_border', False)
        border_width = float(data.get('border_width', 2.0))
        
        # Validate dictionary
        if dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': f'Invalid dictionary: {dictionary}'}), 400
        
        # Validate marker count
        dict_info = aruco_gen.get_dictionary_info()[dictionary]
        total_markers = rows * cols
        if start_id + total_markers > dict_info['max_markers']:
            return jsonify({
                'error': f'Too many markers. Dictionary {dictionary} supports max {dict_info["max_markers"]} markers.'
            }), 400
        
        # Validate dimensions
        if size_mm <= 0 or spacing_mm < 0:
            return jsonify({'error': 'Invalid dimensions. Size must be positive, spacing non-negative.'}), 400
        
        if rows <= 0 or cols <= 0:
            return jsonify({'error': 'Grid dimensions must be positive.'}), 400
        
        # Generate markers
        markers = aruco_gen.generate_grid(start_id, dictionary, rows, cols, size_mm, spacing_mm)
        
        # Create drawing context
        context = DrawingContext()
        context.add_marker_grid(markers, include_borders, include_outer_border, border_width)
        
        if include_labels:
            context.add_text_labels(markers)
        
        # Generate SVG
        svg_content = context.get_svg()
        
        # Calculate total dimensions
        total_width, total_height = aruco_gen.calculate_total_size(rows, cols, size_mm, spacing_mm)
        
        # Add border width to dimensions if outer border is included
        if include_outer_border:
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
            'marker_count': len(markers),
            'success': True
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_lightburn():
    """Generate and download LightBurn file"""
    try:
        data = request.get_json()
        
        # Validate input (same as preview)
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        include_borders = data.get('include_borders', True)
        include_labels = data.get('include_labels', True)
        include_outer_border = data.get('include_outer_border', False)
        border_width = float(data.get('border_width', 2.0))
        
        # Validate dictionary
        if dictionary not in aruco_gen.dictionaries:
            return jsonify({'error': f'Invalid dictionary: {dictionary}'}), 400
        
        # Generate markers
        markers = aruco_gen.generate_grid(start_id, dictionary, rows, cols, size_mm, spacing_mm)
        
        # Create drawing context
        context = DrawingContext()
        context.add_marker_grid(markers, include_borders, include_outer_border, border_width)
        
        if include_labels:
            context.add_text_labels(markers)
        
        # Create metadata
        metadata = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dictionary': dictionary,
            'rows': rows,
            'cols': cols,
            'size_mm': size_mm,
            'spacing_mm': spacing_mm,
            'total_markers': len(markers),
            'start_id': start_id
        }
        
        # Export to LightBurn format
        lbrn_file = lightburn_exporter.export(context, metadata)
        
        # Generate filename
        filename = f"aruco_{dictionary}_{rows}x{cols}_id{start_id}.lbrn2"
        
        return send_file(
            lbrn_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/xml'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/presets')
def get_presets():
    """Get common preset configurations"""
    return jsonify({
        "business_cards": {
            "name": "Business Cards",
            "description": "Small markers for business cards",
            "dictionary": "4X4_50",
            "rows": 2,
            "cols": 5,
            "size_mm": 15,
            "spacing_mm": 3,
            "include_borders": True,
            "include_labels": False
        },
        "inventory_tags": {
            "name": "Inventory Tags", 
            "description": "Medium markers for inventory management",
            "dictionary": "4X4_100",
            "rows": 5,
            "cols": 10,
            "size_mm": 10,
            "spacing_mm": 2,
            "include_borders": True,
            "include_labels": True
        },
        "large_markers": {
            "name": "Large Display Markers",
            "description": "Large markers for wall displays",
            "dictionary": "6X6_50",
            "rows": 1,
            "cols": 1,
            "size_mm": 50,
            "spacing_mm": 10,
            "include_borders": True,
            "include_labels": True
        },
        "test_sheet": {
            "name": "Test Sheet",
            "description": "Standard test grid",
            "dictionary": "4X4_50",
            "rows": 3,
            "cols": 3,
            "size_mm": 20,
            "spacing_mm": 5,
            "include_borders": True,
            "include_labels": True
        },
        "production_run": {
            "name": "Production Run",
            "description": "Large batch for production",
            "dictionary": "5X5_250",
            "rows": 10,
            "cols": 10,
            "size_mm": 8,
            "spacing_mm": 1,
            "include_borders": False,
            "include_labels": False
        }
    })

@app.route('/api/apply_preset/<preset_name>')
def apply_preset(preset_name):
    """Apply a specific preset configuration"""
    presets_response = get_presets()
    presets = presets_response.get_json()
    if preset_name in presets:
        return jsonify({"success": True, "preset": presets[preset_name]})
    return jsonify({"success": False, "error": "Preset not found"}), 404

@app.route('/api/material_info')
def get_material_info():
    """Get material configuration information"""
    return jsonify(lightburn_exporter.get_material_info())

@app.route('/api/quick-test', methods=['POST'])
def generate_quick_test():
    """Generate quick test: 2 ArUCO codes (2" x 2") stacked vertically with outer border"""
    try:
        # Fixed parameters for quick test
        dictionary = "6X6_250"  # Good balance of reliability and marker count
        start_id = 0
        rows = 2
        cols = 1
        size_mm = 50.8  # 2 inches = 50.8mm
        spacing_mm = 5.0  # Small spacing between markers
        include_borders = True
        include_labels = True
        include_outer_border = True
        border_width = 2.5  # 2.5mm border around the whole thing
        
        # Generate markers
        markers = aruco_gen.generate_grid(start_id, dictionary, rows, cols, size_mm, spacing_mm)
        
        # Create drawing context
        context = DrawingContext()
        context.add_marker_grid(markers, include_borders, include_outer_border, border_width)
        
        if include_labels:
            context.add_text_labels(markers)
        
        # Calculate total dimensions including border
        total_width, total_height = aruco_gen.calculate_total_size(rows, cols, size_mm, spacing_mm)
        total_width_with_border = total_width + (2 * border_width)
        total_height_with_border = total_height + (2 * border_width)
        
        # Generate SVG
        svg_content = context.get_svg()
        
        return jsonify({
            'svg': svg_content,
            'dimensions': {
                'width': round(total_width_with_border, 2),
                'height': round(total_height_with_border, 2)
            },
            'total_width': total_width_with_border,
            'total_height': total_height_with_border,
            'marker_count': len(markers),
            'success': True,
            'test_config': {
                'dictionary': dictionary,
                'start_id': start_id,
                'rows': rows,
                'cols': cols,
                'size_mm': size_mm,
                'spacing_mm': spacing_mm,
                'include_borders': include_borders,
                'include_labels': include_labels,
                'include_outer_border': include_outer_border,
                'border_width': border_width
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/quick-test-download', methods=['POST'])
def download_quick_test():
    """Download LightBurn file for quick test configuration"""
    try:
        # Same fixed parameters as quick test preview
        dictionary = "6X6_250"
        start_id = 0
        rows = 2
        cols = 1
        size_mm = 50.8  # 2 inches
        spacing_mm = 5.0
        include_borders = True
        include_labels = True
        include_outer_border = True
        border_width = 2.5
        
        # Generate markers
        markers = aruco_gen.generate_grid(start_id, dictionary, rows, cols, size_mm, spacing_mm)
        
        # Create drawing context
        context = DrawingContext()
        context.add_marker_grid(markers, include_borders, include_outer_border, border_width)
        
        if include_labels:
            context.add_text_labels(markers)
        
        # Create metadata
        metadata = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dictionary': dictionary,
            'rows': rows,
            'cols': cols,
            'size_mm': size_mm,
            'spacing_mm': spacing_mm,
            'total_markers': len(markers),
            'start_id': start_id,
            'test_type': 'Quick Test - 2x2 inch markers'
        }
        
        # Export to LightBurn format
        lbrn_file = lightburn_exporter.export(context, metadata)
        
        # Generate filename for quick test
        filename = f"aruco_quick_test_{rows}x{cols}_2inch.lbrn2"
        
        return send_file(
            lbrn_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/xml'
        )
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/batch_generate', methods=['POST'])
def batch_generate():
    """Generate batch of ArUCO files with sequential IDs"""
    try:
        data = request.get_json()
        
        # Extract batch parameters
        batch_size = int(data.get('batch_size', 5))
        markers_per_file = int(data.get('markers_per_file', 10))
        
        # Validate batch parameters
        if batch_size < 1 or batch_size > 50:
            return jsonify({'error': 'Batch size must be between 1 and 50'}), 400
        if markers_per_file < 1 or markers_per_file > 100:
            return jsonify({'error': 'Markers per file must be between 1 and 100'}), 400
        
        # Generate batch
        batch_generator = BatchGenerator()
        zip_file = batch_generator.generate_batch_files(data, batch_size, markers_per_file)
        
        # Generate filename for batch
        total_markers = batch_size * markers_per_file
        filename = f"aruco_batch_{batch_size}files_{total_markers}markers.zip"
        
        return send_file(
            zip_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# Error logging and debugging endpoints
@app.route('/api/log-error', methods=['POST'])
def log_error():
    """Log frontend errors for debugging"""
    try:
        error_data = request.get_json()
        
        # Log to console
        print(f"[FRONTEND ERROR] {error_data.get('context', 'Unknown')}: {error_data.get('message', 'No message')}")
        
        # Log to file for AI debugging
        with open('debug_logs.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - FRONTEND ERROR\n")
            f.write(f"Context: {error_data.get('context', 'Unknown')}\n")
            f.write(f"Message: {error_data.get('message', 'No message')}\n")
            f.write(f"Stack: {error_data.get('stack', 'No stack trace')}\n")
            f.write(f"URL: {error_data.get('url', 'Unknown')}\n")
            f.write("-" * 80 + "\n")
        
        return jsonify({'status': 'logged'}), 200
    except Exception as e:
        print(f"Failed to log frontend error: {e}")
        return jsonify({'error': 'Failed to log error'}), 500

@app.route('/api/debug/status')
def debug_status():
    """Get application debug status"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'app_running': True,
            'aruco_generator': bool(aruco_gen),
            'lightburn_exporter': bool(lightburn_exporter),
            'dictionaries_loaded': len(aruco_gen.get_dictionary_info()) > 0,
            'debug_mode': app.debug,
            'environment': os.environ.get('FLASK_ENV', 'production')
        }
        
        # Log status for AI debugging
        with open('debug_logs.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - STATUS CHECK\n")
            f.write(f"Status: {status}\n")
            f.write("-" * 80 + "\n")
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e), 'app_running': False}), 500

@app.errorhandler(404)
def not_found_error(error):
    # Log 404 errors for debugging
    with open('debug_logs.txt', 'a') as f:
        f.write(f"{datetime.now().isoformat()} - 404 ERROR\n")
        f.write(f"Path: {request.path}\n")
        f.write(f"Method: {request.method}\n")
        f.write("-" * 80 + "\n")
    
    return render_template('index.html', dictionaries=aruco_gen.get_dictionary_info()), 404

@app.errorhandler(500)
def internal_error(error):
    # Log 500 errors with full traceback
    with open('debug_logs.txt', 'a') as f:
        f.write(f"{datetime.now().isoformat()} - 500 ERROR\n")
        f.write(f"Path: {request.path}\n")
        f.write(f"Method: {request.method}\n")
        f.write(f"Error: {str(error)}\n")
        f.write(f"Traceback: {traceback.format_exc()}\n")
        f.write("-" * 80 + "\n")
    
    return jsonify({'error': 'Internal server error'}), 500

# Enhanced logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_logs.txt'),
        logging.StreamHandler()
    ]
)

# Log application startup
with open('debug_logs.txt', 'a') as f:
    f.write(f"{datetime.now().isoformat()} - APPLICATION STARTUP\n")
    f.write(f"ArUCO Generator initialized: {bool(aruco_gen)}\n")
    f.write(f"LightBurn Exporter initialized: {bool(lightburn_exporter)}\n")
    f.write("-" * 80 + "\n")
