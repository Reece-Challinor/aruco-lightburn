import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from .aruco import ArUCOGenerator
from .drawing import DrawingContext
from .lightburn import LightBurnExporter

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

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
        
        return jsonify({
            'svg': svg_content,
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', dictionaries=aruco_gen.get_dictionary_info()), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
