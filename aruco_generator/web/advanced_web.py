"""
Advanced web routes for coordinate systems, professional exports, and validation.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>advanced_web.py</name>
    <version>2.4.0</version>
    <type>flask_blueprint</type>
    <purpose>Advanced previews, calibration exports, and validation utilities</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
  <route_summary>
    <route path="/api/advanced/preview" method="POST" purpose="Advanced marker preview"/>
    <route path="/api/export/opencv_yaml" method="POST" purpose="OpenCV YAML export"/>
    <route path="/api/export/ros" method="POST" purpose="ROS JSON export"/>
    <route path="/api/export/dxf" method="POST" purpose="DXF export"/>
    <route path="/api/export/stl" method="POST" purpose="STL export"/>
    <route path="/api/validation/detect" method="POST" purpose="Detect markers in uploaded image"/>
  </route_summary>
</ai_agent_documentation>
-->
"""

import base64
from io import BytesIO

import cv2
import numpy as np
from flask import Blueprint, current_app, jsonify, request, send_file

from ..core.aruco import ArUCOGenerator
from ..core.utils import handle_api_errors, validate_generation_params
from ..db.extensions import db
from ..db.models import DetectionMetric
from ..export.exporters import ProfessionalExporter
from ..validation.validation import DetectionValidator

# Create Blueprint
advanced_bp = Blueprint("advanced", __name__)

# Initialize components
aruco_gen = ArUCOGenerator()
exporter = ProfessionalExporter()
validator = DetectionValidator()


def _get_request_json():
    return request.get_json(silent=True) or {}


def _validate_dictionary(dictionary: str):
    if dictionary not in validator.aruco_dicts:
        available = ", ".join(sorted(validator.aruco_dicts.keys()))
        raise ValueError(
            f'Unknown ArUCO dictionary "{dictionary}". Available: {available}'
        )


def _extract_upload_image():
    file = request.files.get("file") or request.files.get("image")
    if not file:
        raise ValueError("No image provided")
    image_bytes = file.read()
    if not image_bytes:
        raise ValueError("Uploaded image is empty")
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image file")
    return image


def _decode_base64_image(image_base64: str):
    if not image_base64:
        raise ValueError("Image payload is empty")
    try:
        payload = base64.b64decode(image_base64)
    except Exception as exc:
        raise ValueError("Invalid base64 image payload") from exc
    nparr = np.frombuffer(payload, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode base64 image")
    return image


def build_advanced_preview(params):
    """Build advanced preview response from validated params."""
    from ..core.drawing import DrawingContext

    markers = aruco_gen.generate_grid(
        start_id=params["start_id"],
        dict_name=params["dictionary"],
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    ctx = DrawingContext()
    ctx.add_marker_grid_preview(
        markers=markers,
        include_borders=params["include_borders"],
        include_outer_border=params["include_outer_border"],
        border_width=params["border_width"],
    )

    if params["include_labels"]:
        for marker in markers:
            ctx.add_text(
                text=f"ID: {marker['id']}",
                x=marker["x"] + params["size_mm"] / 2,
                y=marker["y"] - 2,
            )

    svg_content = ctx.get_svg()
    total_width, total_height = aruco_gen.calculate_total_size(
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    if params["include_outer_border"]:
        total_width += 2 * params["border_width"]
        total_height += 2 * params["border_width"]

    return {
        "svg": svg_content,
        "count": len(markers),
        "dimensions": {"width": total_width, "height": total_height},
    }


def build_calibration_data_from_generation(params):
    """Build calibration data payload from generation params."""
    markers = aruco_gen.generate_grid(
        start_id=params["start_id"],
        dict_name=params["dictionary"],
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
        generate_images=False,
    )

    marker_entries = []
    marker_ids = []
    border_offset = params["border_width"] if params["include_outer_border"] else 0.0
    for marker in markers:
        x = float(marker["x"]) + border_offset
        y = float(marker["y"]) + border_offset
        size = float(marker["size"])
        marker_id = int(marker["id"])
        marker_ids.append(marker_id)

        marker_entries.append(
            {
                "id": marker_id,
                "position": [x + size / 2, y + size / 2, 0.0],
                "corners": [
                    [x, y, 0.0],
                    [x + size, y, 0.0],
                    [x + size, y + size, 0.0],
                    [x, y + size, 0.0],
                ],
            }
        )

    width, height = aruco_gen.calculate_total_size(
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    if params["include_outer_border"]:
        width += 2 * params["border_width"]
        height += 2 * params["border_width"]

    return {
        "pattern_type": "aruco_grid",
        "dictionary": params["dictionary"],
        "marker_size_mm": params["size_mm"],
        "grid_size": [params["rows"], params["cols"]],
        "spacing_mm": params["spacing_mm"],
        "marker_ids": marker_ids,
        "markers": marker_entries,
        "physical_width_mm": width,
        "physical_height_mm": height,
    }


@advanced_bp.route("/api/advanced/preview", methods=["POST"])
@handle_api_errors
def advanced_preview():
    """Generate advanced preview with additional features."""
    data = request.get_json() or {}
    params = validate_generation_params(data, list(aruco_gen.dictionaries.keys()))
    return jsonify(build_advanced_preview(params))


@advanced_bp.route("/api/advanced/generate_with_coordinates", methods=["POST"])
def generate_with_coordinates():
    """Generate markers with full 3D coordinate system data."""
    try:
        data = request.get_json()

        # Build marker configuration
        marker_config = {
            "dictionary": data.get("dictionary", "4X4_50"),
            "marker_ids": data.get("marker_ids", [0, 1, 2, 3]),
            "size_mm": float(data.get("size_mm", 50.0)),
            "positions": data.get("positions", []),
            "orientations": data.get("orientations", []),
            "reference_frame": data.get("reference_frame", "world"),
        }

        # Generate markers with coordinates
        result = aruco_gen.generate_with_coordinates(marker_config)

        # Convert images to base64 for response
        for marker in result["markers"]:
            if "image" in marker:
                _, buffer = cv2.imencode(".png", marker["image"])
                marker["image_base64"] = base64.b64encode(buffer).decode("utf-8")
                del marker["image"]  # Remove numpy array from response

        return jsonify(
            {
                "success": True,
                "markers": result["markers"],
                "calibration_data": result["calibration_data"],
                "coordinate_frame": result["coordinate_frame"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@advanced_bp.route("/api/advanced/pose_estimation_board", methods=["POST"])
def generate_pose_board():
    """Generate board optimized for pose estimation."""
    try:
        data = request.get_json()

        board_config = {
            "rows": int(data.get("rows", 3)),
            "cols": int(data.get("cols", 3)),
            "marker_size_mm": float(data.get("marker_size_mm", 50.0)),
            "spacing_mm": float(data.get("spacing_mm", 10.0)),
            "dictionary": data.get("dictionary", "4X4_50"),
            "start_id": int(data.get("start_id", 0)),
        }

        # Generate pose estimation board
        result = aruco_gen.generate_pose_estimation_board(board_config)

        # Convert marker images to base64
        for marker in result["markers"]:
            if "image" in marker:
                _, buffer = cv2.imencode(".png", marker["image"])
                marker["image_base64"] = base64.b64encode(buffer).decode("utf-8")
                del marker["image"]

        return jsonify(
            {
                "success": True,
                "board_config": result["board_config"],
                "calibration_data": result["calibration_data"],
                "coordinate_frame": result["coordinate_frame"],
                "markers": result["markers"][:10],  # Limit response size
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@advanced_bp.route("/api/export/opencv_yaml", methods=["POST"])
def export_opencv_yaml():
    """Export calibration data in OpenCV YAML format."""
    try:
        data = request.get_json()
        calibration_data = data.get("calibration_data", {})
        camera_params = data.get("camera_params", None)

        yaml_content = exporter.export_opencv_yaml(calibration_data, camera_params)

        buffer = BytesIO(yaml_content.encode("utf-8"))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="text/yaml",
            as_attachment=True,
            download_name="opencv_calibration.yaml",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@advanced_bp.route("/api/export/ros", methods=["POST"])
def export_ros():
    """Export calibration data in ROS format."""
    try:
        data = request.get_json()
        calibration_data = data.get("calibration_data", {})
        frame_id = data.get("frame_id", "camera_optical_frame")

        ros_json = exporter.export_ros_format(calibration_data, frame_id)

        buffer = BytesIO(ros_json.encode("utf-8"))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/json",
            as_attachment=True,
            download_name="ros_calibration.json",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@advanced_bp.route("/api/export/dxf", methods=["POST"])
def export_dxf():
    """Export pattern as DXF for CNC/laser cutting."""
    try:
        data = request.get_json() or {}
        calibration_data = data.get("calibration_data")
        if not calibration_data:
            params = validate_generation_params(
                data, list(aruco_gen.dictionaries.keys())
            )
            calibration_data = build_calibration_data_from_generation(params)

        dxf_buffer = exporter.export_dxf(calibration_data)

        return send_file(
            dxf_buffer,
            mimetype="application/dxf",
            as_attachment=True,
            download_name="aruco_pattern.dxf",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@advanced_bp.route("/api/export/stl", methods=["POST"])
def export_stl():
    """Export pattern as STL for 3D printing."""
    try:
        data = request.get_json() or {}
        calibration_data = data.get("calibration_data")
        if not calibration_data:
            params = validate_generation_params(
                data, list(aruco_gen.dictionaries.keys())
            )
            calibration_data = build_calibration_data_from_generation(params)
        thickness_mm = float(data.get("thickness_mm", 3.0))

        stl_buffer = exporter.export_stl_3d(calibration_data, thickness_mm)

        return send_file(
            stl_buffer,
            mimetype="application/sla",
            as_attachment=True,
            download_name="landing_pad.stl",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@advanced_bp.route("/api/validation/test_pattern", methods=["POST"])
@handle_api_errors
def generate_test_pattern():
    """Generate multi-scale test pattern for validation."""
    data = _get_request_json()

    dictionary = data.get("dictionary", "4X4_50")
    _validate_dictionary(dictionary)

    pattern_config = {
        "dictionary": dictionary,
        "scales": data.get("scales", [10, 20, 50, 100]),
        "marker_ids": data.get("marker_ids", [0, 1, 2, 3]),
        "canvas_size_mm": tuple(data.get("canvas_size_mm", [300, 200])),
        "include_distortions": data.get("include_distortions", False),
        "include_occlusions": data.get("include_occlusions", False),
    }

    # Generate test pattern
    result = validator.generate_test_pattern(pattern_config)

    # Convert image to base64
    _, buffer = cv2.imencode(".png", result["image"])
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return jsonify(
        {
            "success": True,
            "image_base64": image_base64,
            "metadata": result["metadata"],
            "test_markers": result["test_markers"],
        }
    )


@advanced_bp.route("/api/validation/verify_quality", methods=["POST"])
@handle_api_errors
def verify_marker_quality():
    """Verify quality of uploaded marker image."""
    image = _extract_upload_image()
    expected_id = int(request.form.get("expected_id", 0))
    dictionary = request.form.get("dictionary", "4X4_50")
    _validate_dictionary(dictionary)

    # Verify quality
    quality_report = validator.verify_marker_quality(image, expected_id, dictionary)

    return jsonify({"success": True, "quality_report": quality_report})


@advanced_bp.route("/api/validation/detect", methods=["POST"])
@handle_api_errors
def detect_markers():
    """Detect ArUCO markers in an uploaded image."""
    image = _extract_upload_image()
    dictionary = request.form.get("dictionary", "4X4_50")
    expected_markers = request.form.get("expected_markers")
    expected_count = int(expected_markers) if expected_markers else None
    _validate_dictionary(dictionary)

    detection = validator.detect_markers(
        image, dictionary=dictionary, expected_count=expected_count
    )

    return jsonify({"success": True, "detection": detection})


@advanced_bp.route("/api/validation/hamming_distance", methods=["POST"])
@handle_api_errors
def calculate_hamming():
    """Calculate Hamming distance between two markers."""
    data = _get_request_json()

    id1 = int(data.get("id1", 0))
    id2 = int(data.get("id2", 1))
    dictionary = data.get("dictionary", "4X4_50")
    _validate_dictionary(dictionary)

    distance = validator.calculate_hamming_distance(id1, id2, dictionary)
    if distance < 0:
        raise ValueError("Marker IDs out of range for selected dictionary")

    # Determine safety level
    safety_level = "Safe"
    if distance < 3:
        safety_level = "Critical - High confusion risk"
    elif distance < 5:
        safety_level = "Warning - Moderate confusion risk"

    return jsonify(
        {
            "success": True,
            "id1": id1,
            "id2": id2,
            "hamming_distance": distance,
            "safety_level": safety_level,
            "dictionary": dictionary,
        }
    )


@advanced_bp.route("/api/validation/detection_report", methods=["POST"])
@handle_api_errors
def generate_report():
    """Generate detection quality report."""
    data = _get_request_json()

    test_results = data.get("test_results", [])
    pattern_metadata = data.get("pattern_metadata", {})

    # Generate report
    report = validator.generate_detection_report(test_results, pattern_metadata)

    # Save metrics to database if pattern_id provided
    if "pattern_id" in data:
        if current_app.config.get("USE_DB"):
            # Calculate summary metrics from report/test results
            summary = report.get("summary", {})
            total_tests = summary.get("total_tests", len(test_results))
            successful = summary.get(
                "successful_detections",
                sum(1 for r in test_results if r.get("detected")),
            )

            pose_errors = [
                r.get("pose_error_mm")
                for r in test_results
                if r.get("pose_error_mm") is not None
            ]
            avg_pose_error = (
                sum(pose_errors) / len(pose_errors) if pose_errors else None
            )

            corner_errors = [
                r.get("corner_error")
                for r in test_results
                if r.get("corner_error") is not None
            ]
            avg_corner_error = (
                sum(corner_errors) / len(corner_errors) if corner_errors else None
            )

            perf = report.get("performance", {})
            avg_detection_time = perf.get("avg_detection_time")

            metric = DetectionMetric(
                pattern_id=data["pattern_id"],
                detected_markers=successful,
                expected_markers=total_tests,
                detection_rate=summary.get("detection_rate"),
                avg_corner_error=avg_corner_error,
                avg_pose_error=avg_pose_error,
                avg_detection_time=avg_detection_time,
                lighting_condition=data.get("lighting_conditions", "unknown"),
                distance_mm=data.get("distance_mm"),
                viewing_angle=data.get("viewing_angle"),
            )
            db.session.add(metric)
            db.session.commit()

            report["metric_id"] = metric.id
        else:
            report["metric_id"] = None
            report["metric_message"] = "Database disabled - metrics not persisted"

    return jsonify({"success": True, "report": report})


@advanced_bp.route("/api/validation/batch_test", methods=["POST"])
@handle_api_errors
def batch_validation_test():
    """Run batch validation tests on multiple patterns."""
    data = _get_request_json()

    tests = data.get("tests", [])
    if not tests:
        raise ValueError("No tests provided for batch validation")

    results = []
    for test in tests:
        image_base64 = test.get("image_base64")
        image = _decode_base64_image(image_base64)
        dictionary = test.get("dictionary", "4X4_50")
        _validate_dictionary(dictionary)
        expected_markers = test.get("expected_markers")
        expected_count = int(expected_markers) if expected_markers else None

        detection = validator.detect_markers(
            image, dictionary=dictionary, expected_count=expected_count
        )
        results.append(
            {
                "pattern_id": test.get("pattern_id"),
                "config": test.get("config", {}),
                "detected": detection["detected_markers"] > 0,
                "detected_markers": detection["detected_markers"],
                "expected_markers": detection["expected_markers"],
                "detection_rate": detection["detection_rate"],
                "confidence": detection["avg_confidence"],
                "processing_time_ms": detection["detection_time_ms"],
            }
        )

    pattern_metadata = data.get("pattern_metadata", {})
    if not pattern_metadata:
        pattern_metadata = {
            "total_tests": len(tests),
            "dictionary": tests[0].get("dictionary", "4X4_50"),
        }

    report = validator.generate_detection_report(results, pattern_metadata)

    return jsonify(
        {"success": True, "batch_results": results, "overall_report": report}
    )
