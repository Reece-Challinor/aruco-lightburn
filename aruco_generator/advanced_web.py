"""
Advanced web routes for coordinate systems, professional exports, and validation.
"""

from flask import request, jsonify, send_file
from io import BytesIO
import cv2
import base64
import json
from .aruco import ArUCOGenerator
from .exporters import ProfessionalExporter
from .validation import DetectionValidator
from app import app, db
from models import CalibrationPattern, DetectionMetric

# Initialize components
aruco_gen = ArUCOGenerator()
exporter = ProfessionalExporter()
validator = DetectionValidator()

@app.route('/api/advanced/generate_with_coordinates', methods=['POST'])
def generate_with_coordinates():
    """Generate markers with full 3D coordinate system data."""
    try:
        data = request.get_json()
        
        # Build marker configuration
        marker_config = {
            'dictionary': data.get('dictionary', '4X4_50'),
            'marker_ids': data.get('marker_ids', [0, 1, 2, 3]),
            'size_mm': float(data.get('size_mm', 50.0)),
            'positions': data.get('positions', []),
            'orientations': data.get('orientations', []),
            'reference_frame': data.get('reference_frame', 'world')
        }
        
        # Generate markers with coordinates
        result = aruco_gen.generate_with_coordinates(marker_config)
        
        # Convert images to base64 for response
        for marker in result['markers']:
            if 'image' in marker:
                _, buffer = cv2.imencode('.png', marker['image'])
                marker['image_base64'] = base64.b64encode(buffer).decode('utf-8')
                del marker['image']  # Remove numpy array from response
        
        return jsonify({
            'success': True,
            'markers': result['markers'],
            'calibration_data': result['calibration_data'],
            'coordinate_frame': result['coordinate_frame']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced/pose_estimation_board', methods=['POST'])
def generate_pose_board():
    """Generate board optimized for pose estimation."""
    try:
        data = request.get_json()
        
        board_config = {
            'rows': int(data.get('rows', 3)),
            'cols': int(data.get('cols', 3)),
            'marker_size_mm': float(data.get('marker_size_mm', 50.0)),
            'spacing_mm': float(data.get('spacing_mm', 10.0)),
            'dictionary': data.get('dictionary', '4X4_50'),
            'start_id': int(data.get('start_id', 0))
        }
        
        # Generate pose estimation board
        result = aruco_gen.generate_pose_estimation_board(board_config)
        
        # Convert marker images to base64
        for marker in result['markers']:
            if 'image' in marker:
                _, buffer = cv2.imencode('.png', marker['image'])
                marker['image_base64'] = base64.b64encode(buffer).decode('utf-8')
                del marker['image']
        
        return jsonify({
            'success': True,
            'board_config': result['board_config'],
            'calibration_data': result['calibration_data'],
            'coordinate_frame': result['coordinate_frame'],
            'markers': result['markers'][:10]  # Limit response size
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/opencv_yaml', methods=['POST'])
def export_opencv_yaml():
    """Export calibration data in OpenCV YAML format."""
    try:
        data = request.get_json()
        calibration_data = data.get('calibration_data', {})
        camera_params = data.get('camera_params', None)
        
        yaml_content = exporter.export_opencv_yaml(calibration_data, camera_params)
        
        buffer = BytesIO(yaml_content.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='text/yaml',
            as_attachment=True,
            download_name='opencv_calibration.yaml'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/ros', methods=['POST'])
def export_ros():
    """Export calibration data in ROS format."""
    try:
        data = request.get_json()
        calibration_data = data.get('calibration_data', {})
        frame_id = data.get('frame_id', 'camera_optical_frame')
        
        ros_json = exporter.export_ros_format(calibration_data, frame_id)
        
        buffer = BytesIO(ros_json.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name='ros_calibration.json'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/dxf', methods=['POST'])
def export_dxf():
    """Export pattern as DXF for CNC/laser cutting."""
    try:
        data = request.get_json()
        calibration_data = data.get('calibration_data', {})
        
        dxf_buffer = exporter.export_dxf(calibration_data)
        
        return send_file(
            dxf_buffer,
            mimetype='application/dxf',
            as_attachment=True,
            download_name='aruco_pattern.dxf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/stl', methods=['POST'])
def export_stl():
    """Export pattern as STL for 3D printing."""
    try:
        data = request.get_json()
        calibration_data = data.get('calibration_data', {})
        thickness_mm = float(data.get('thickness_mm', 3.0))
        
        stl_buffer = exporter.export_stl_3d(calibration_data, thickness_mm)
        
        return send_file(
            stl_buffer,
            mimetype='application/sla',
            as_attachment=True,
            download_name='landing_pad.stl'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation/test_pattern', methods=['POST'])
def generate_test_pattern():
    """Generate multi-scale test pattern for validation."""
    try:
        data = request.get_json()
        
        pattern_config = {
            'dictionary': data.get('dictionary', '4X4_50'),
            'scales': data.get('scales', [10, 20, 50, 100]),
            'marker_ids': data.get('marker_ids', [0, 1, 2, 3]),
            'canvas_size_mm': tuple(data.get('canvas_size_mm', [300, 200])),
            'include_distortions': data.get('include_distortions', False),
            'include_occlusions': data.get('include_occlusions', False)
        }
        
        # Generate test pattern
        result = validator.generate_test_pattern(pattern_config)
        
        # Convert image to base64
        _, buffer = cv2.imencode('.png', result['image'])
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image_base64': image_base64,
            'metadata': result['metadata'],
            'test_markers': result['test_markers']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation/verify_quality', methods=['POST'])
def verify_marker_quality():
    """Verify quality of uploaded marker image."""
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        expected_id = int(request.form.get('expected_id', 0))
        dictionary = request.form.get('dictionary', '4X4_50')
        
        # Read image
        import numpy as np
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Verify quality
        quality_report = validator.verify_marker_quality(image, expected_id, dictionary)
        
        return jsonify({
            'success': True,
            'quality_report': quality_report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation/hamming_distance', methods=['POST'])
def calculate_hamming():
    """Calculate Hamming distance between two markers."""
    try:
        data = request.get_json()
        
        id1 = int(data.get('id1', 0))
        id2 = int(data.get('id2', 1))
        dictionary = data.get('dictionary', '4X4_50')
        
        distance = validator.calculate_hamming_distance(id1, id2, dictionary)
        
        # Determine safety level
        safety_level = 'Safe'
        if distance < 3:
            safety_level = 'Critical - High confusion risk'
        elif distance < 5:
            safety_level = 'Warning - Moderate confusion risk'
        
        return jsonify({
            'success': True,
            'id1': id1,
            'id2': id2,
            'hamming_distance': distance,
            'safety_level': safety_level,
            'dictionary': dictionary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation/detection_report', methods=['POST'])
def generate_report():
    """Generate detection quality report."""
    try:
        data = request.get_json()
        
        test_results = data.get('test_results', [])
        pattern_metadata = data.get('pattern_metadata', {})
        
        # Generate report
        report = validator.generate_detection_report(test_results, pattern_metadata)
        
        # Save metrics to database if pattern_id provided
        if 'pattern_id' in data:
            # Calculate average metrics
            avg_detection = report['test_summary']['average_detection_rate']
            avg_pose_error = report['test_summary']['average_pose_error']
            
            metric = DetectionMetric(
                pattern_id=data['pattern_id'],
                detection_rate=avg_detection,
                pose_error_mm=avg_pose_error,
                lighting_conditions=data.get('lighting_conditions', 'unknown')
            )
            db.session.add(metric)
            db.session.commit()
            
            report['metric_id'] = metric.id
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation/batch_test', methods=['POST'])
def batch_validation_test():
    """Run batch validation tests on multiple patterns."""
    try:
        data = request.get_json()
        
        patterns = data.get('patterns', [])
        test_configs = data.get('test_configs', [])
        
        results = []
        for pattern in patterns:
            for config in test_configs:
                # Simulate test (in production, this would actually test detection)
                test_result = {
                    'pattern_id': pattern.get('id'),
                    'config': config,
                    'detected': True,  # Placeholder
                    'confidence': 0.95,
                    'pose_error_mm': 2.5,
                    'processing_time_ms': 15.0
                }
                results.append(test_result)
        
        # Generate overall report
        pattern_metadata = {
            'total_patterns': len(patterns),
            'test_configurations': len(test_configs),
            'dictionary': patterns[0].get('dictionary', '4X4_50') if patterns else '4X4_50'
        }
        
        report = validator.generate_detection_report(results, pattern_metadata)
        
        return jsonify({
            'success': True,
            'batch_results': results,
            'overall_report': report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500