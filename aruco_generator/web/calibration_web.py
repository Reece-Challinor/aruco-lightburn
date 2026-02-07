"""
Web routes for calibration pattern generation.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>calibration_web.py</name>
    <version>2.1.0</version>
    <type>flask_blueprint</type>
    <purpose>Calibration pattern routes for ChArUco, ARUCO boards, and AprilTags</purpose>
    <last_updated>2026-02-07</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
  <route_summary>
    <route path="/calibration" method="GET" purpose="Render calibration UI"/>
    <route path="/api/calibration/charuco" method="POST" purpose="Generate ChArUco board"/>
    <route path="/api/calibration/aruco_board" method="POST" purpose="Generate ARUCO board"/>
    <route path="/api/calibration/apriltag" method="POST" purpose="Generate AprilTag marker"/>
    <route path="/api/calibration/apriltag_grid" method="POST" purpose="Generate AprilTag grid"/>
    <route path="/api/calibration/export/<id>" method="GET" purpose="Export calibration data"/>
  </route_summary>
</ai_agent_documentation>
-->
"""

import base64
import json
from io import BytesIO

import cv2
from flask import Blueprint, jsonify, render_template, request, send_file

from ..calibration.calibration import CalibrationPatternGenerator
from ..db.extensions import db
from ..db.models import CalibrationPattern, DetectionMetric

# Create Blueprint
calibration_bp = Blueprint("calibration", __name__)

# Initialize calibration generator
calibration_gen = CalibrationPatternGenerator()


@calibration_bp.route("/calibration")
def calibration_page():
    """Render calibration patterns page."""
    return render_template("calibration.html")


@calibration_bp.route("/api/calibration/charuco", methods=["POST"])
def generate_charuco():
    """Generate ChArUco board for camera calibration."""
    try:
        data = request.get_json()

        # Get parameters with defaults
        squares_x = int(data.get("squares_x", 8))
        squares_y = int(data.get("squares_y", 6))
        square_size_mm = float(data.get("square_size_mm", 30.0))
        marker_size_mm = float(data.get("marker_size_mm", 22.5))
        dictionary = data.get("dictionary", "4X4_50")
        paper_size = data.get("paper_size", "A4")
        save_to_db = data.get("save_to_db", False)
        pattern_name = data.get("pattern_name", f"ChArUco_{squares_x}x{squares_y}")

        # Validate marker size
        if marker_size_mm >= square_size_mm:
            return (
                jsonify({"error": "Marker size must be smaller than square size"}),
                400,
            )

        # Generate ChArUco board
        result = calibration_gen.generate_charuco_board(
            squares_x=squares_x,
            squares_y=squares_y,
            square_size_mm=square_size_mm,
            marker_size_mm=marker_size_mm,
            dictionary=dictionary,
            paper_size=paper_size,
        )

        # Convert image to base64 for preview
        _, buffer = cv2.imencode(".png", result["image"])
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Save to database if requested
        pattern_id = None
        if save_to_db:
            try:
                pattern = CalibrationPattern(
                    pattern_type="charuco",
                    pattern_name=pattern_name,
                    physical_width_mm=result["dimensions_mm"][0],
                    physical_height_mm=result["dimensions_mm"][1],
                    marker_size_mm=marker_size_mm,
                    grid_size_x=squares_x,
                    grid_size_y=squares_y,
                    dictionary_type=dictionary,
                    total_markers=result["calibration_data"]["total_markers"],
                    calibration_data=result["calibration_data"],
                    image_checksum=result["calibration_data"]["checksum"],
                )
                db.session.add(pattern)
                db.session.commit()
                pattern_id = pattern.id
            except Exception:
                # Database save failed, continue without persistence
                pass

        return jsonify(
            {
                "success": True,
                "image_base64": image_base64,
                "calibration_data": result["calibration_data"],
                "dimensions_mm": result["dimensions_mm"],
                "pattern_id": pattern_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calibration_bp.route("/api/calibration/aruco_board", methods=["POST"])
def generate_aruco_board():
    """Generate ARUCO board with fixed grid."""
    try:
        data = request.get_json()

        # Get parameters
        markers_x = int(data.get("markers_x", 4))
        markers_y = int(data.get("markers_y", 3))
        marker_size_mm = float(data.get("marker_size_mm", 50.0))
        separation_mm = float(data.get("separation_mm", 10.0))
        dictionary = data.get("dictionary", "4X4_50")
        first_marker_id = int(data.get("first_marker_id", 0))
        save_to_db = data.get("save_to_db", False)
        pattern_name = data.get("pattern_name", f"ARUCO_Board_{markers_x}x{markers_y}")

        # Generate ARUCO board
        result = calibration_gen.generate_aruco_board(
            markers_x=markers_x,
            markers_y=markers_y,
            marker_size_mm=marker_size_mm,
            separation_mm=separation_mm,
            dictionary=dictionary,
            first_marker_id=first_marker_id,
        )

        # Convert image to base64
        _, buffer = cv2.imencode(".png", result["image"])
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Save to database if requested
        pattern_id = None
        if save_to_db:
            try:
                pattern = CalibrationPattern(
                    pattern_type="aruco_board",
                    pattern_name=pattern_name,
                    physical_width_mm=result["dimensions_mm"][0],
                    physical_height_mm=result["dimensions_mm"][1],
                    marker_size_mm=marker_size_mm,
                    marker_separation_mm=separation_mm,
                    grid_size_x=markers_x,
                    grid_size_y=markers_y,
                    dictionary_type=dictionary,
                    total_markers=markers_x * markers_y,
                    first_marker_id=first_marker_id,
                    calibration_data=result["calibration_data"],
                    image_checksum=result["calibration_data"]["checksum"],
                )
                db.session.add(pattern)
                db.session.commit()
                pattern_id = pattern.id
            except Exception:
                # Database save failed, continue without persistence
                pass

        return jsonify(
            {
                "success": True,
                "image_base64": image_base64,
                "calibration_data": result["calibration_data"],
                "dimensions_mm": result["dimensions_mm"],
                "pattern_id": pattern_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calibration_bp.route("/api/calibration/apriltag", methods=["POST"])
def generate_apriltag():
    """Generate single AprilTag marker."""
    try:
        data = request.get_json()

        # Get parameters
        tag_family = data.get("tag_family", "tag36h11")
        tag_id = int(data.get("tag_id", 0))
        tag_size_mm = float(data.get("tag_size_mm", 50.0))
        save_to_db = data.get("save_to_db", False)
        pattern_name = data.get("pattern_name", f"AprilTag_{tag_family}_{tag_id}")

        # Generate AprilTag
        result = calibration_gen.generate_apriltag(
            tag_family=tag_family, tag_id=tag_id, tag_size_mm=tag_size_mm
        )

        # Convert image to base64
        _, buffer = cv2.imencode(".png", result["image"])
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Save to database if requested
        pattern_id = None
        if save_to_db:
            try:
                pattern = CalibrationPattern(
                    pattern_type="apriltag",
                    pattern_name=pattern_name,
                    physical_width_mm=result["dimensions_mm"][0],
                    physical_height_mm=result["dimensions_mm"][1],
                    marker_size_mm=tag_size_mm,
                    grid_size_x=1,
                    grid_size_y=1,
                    dictionary_type=tag_family,
                    total_markers=1,
                    first_marker_id=tag_id,
                    calibration_data=result["metadata"],
                    image_checksum=result["metadata"].get("checksum"),
                )
                db.session.add(pattern)
                db.session.commit()
                pattern_id = pattern.id
            except Exception:
                # Database save failed, continue without persistence
                pass

        return jsonify(
            {
                "success": True,
                "image_base64": image_base64,
                "calibration_data": result["metadata"],
                "metadata": result["metadata"],
                "dimensions_mm": result["dimensions_mm"],
                "pattern_id": pattern_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calibration_bp.route("/api/calibration/apriltag_grid", methods=["POST"])
def generate_apriltag_grid():
    """Generate grid of AprilTags."""
    try:
        data = request.get_json()

        # Get parameters
        grid_x = int(data.get("grid_x", 3))
        grid_y = int(data.get("grid_y", 3))
        tag_family = data.get("tag_family", "tag36h11")
        tag_size_mm = float(data.get("tag_size_mm", 40.0))
        spacing_mm = float(data.get("spacing_mm", 20.0))
        first_tag_id = int(data.get("first_tag_id", 0))
        save_to_db = data.get("save_to_db", False)
        pattern_name = data.get("pattern_name", f"AprilTag_Grid_{grid_x}x{grid_y}")

        # Generate AprilTag grid
        result = calibration_gen.generate_apriltag_grid(
            grid_x=grid_x,
            grid_y=grid_y,
            tag_family=tag_family,
            tag_size_mm=tag_size_mm,
            spacing_mm=spacing_mm,
            first_tag_id=first_tag_id,
        )

        # Convert image to base64
        _, buffer = cv2.imencode(".png", result["image"])
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Save to database if requested
        pattern_id = None
        if save_to_db:
            try:
                pattern = CalibrationPattern(
                    pattern_type="apriltag_grid",
                    pattern_name=pattern_name,
                    physical_width_mm=result["dimensions_mm"][0],
                    physical_height_mm=result["dimensions_mm"][1],
                    marker_size_mm=tag_size_mm,
                    marker_separation_mm=spacing_mm,
                    grid_size_x=grid_x,
                    grid_size_y=grid_y,
                    dictionary_type=tag_family,
                    total_markers=grid_x * grid_y,
                    first_marker_id=first_tag_id,
                    calibration_data=result["metadata"],
                )
                db.session.add(pattern)
                db.session.commit()
                pattern_id = pattern.id
            except Exception:
                # Database save failed, continue without persistence
                pass

        return jsonify(
            {
                "success": True,
                "image_base64": image_base64,
                "calibration_data": result["metadata"],
                "metadata": result["metadata"],
                "dimensions_mm": result["dimensions_mm"],
                "pattern_id": pattern_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calibration_bp.route("/api/calibration/export/<int:pattern_id>", methods=["GET"])
def export_calibration_data(pattern_id):
    """Export calibration data in various formats."""
    try:
        # Get pattern from database
        try:
            pattern = CalibrationPattern.query.get_or_404(pattern_id)
        except Exception:
            return jsonify({"error": "Pattern not found or database unavailable"}), 404

        # Get export format
        export_format = request.args.get("format", "yaml")

        if export_format == "yaml":
            # Export as YAML
            yaml_data = calibration_gen.export_calibration_yaml(
                pattern.calibration_data
            )
            buffer = BytesIO(yaml_data.encode("utf-8"))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype="text/yaml",
                as_attachment=True,
                download_name=f"calibration_{pattern_id}.yaml",
            )

        elif export_format == "json":
            # Export as JSON
            json_data = calibration_gen.export_calibration_json(
                pattern.calibration_data
            )
            buffer = BytesIO(json_data.encode("utf-8"))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype="application/json",
                as_attachment=True,
                download_name=f"calibration_{pattern_id}.json",
            )

        elif export_format == "ros":
            # Export in ROS format
            ros_data = calibration_gen.export_ros_format(pattern.calibration_data)
            json_data = json.dumps(ros_data, indent=2)
            buffer = BytesIO(json_data.encode("utf-8"))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype="application/json",
                as_attachment=True,
                download_name=f"calibration_{pattern_id}_ros.json",
            )

        else:
            return jsonify({"error": "Invalid export format"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calibration_bp.route("/api/calibration/patterns", methods=["GET"])
def list_calibration_patterns():
    """List all saved calibration patterns."""
    try:
        patterns = CalibrationPattern.query.order_by(
            CalibrationPattern.created_at.desc()
        ).all()
        return jsonify(
            {"patterns": [p.to_dict() for p in patterns], "total": len(patterns)}
        )
    except Exception:
        # Return empty list if database unavailable
        return jsonify(
            {
                "patterns": [],
                "total": 0,
                "message": "Database unavailable - patterns not persisted",
            }
        )


@calibration_bp.route("/api/calibration/metrics", methods=["POST"])
def save_detection_metrics():
    """Save detection performance metrics."""
    try:
        data = request.get_json()

        try:
            detected_markers = int(data.get("detected_markers", 0))
            expected_markers = int(data.get("expected_markers", detected_markers))

            metric = DetectionMetric(
                pattern_id=data["pattern_id"],
                detected_markers=detected_markers,
                expected_markers=expected_markers,
                detection_rate=data.get("detection_rate"),
                avg_corner_error=data.get("avg_corner_error"),
                avg_pose_error=data.get("pose_error_mm") or data.get("avg_pose_error"),
                avg_detection_time=data.get("avg_detection_time"),
                lighting_condition=data.get("lighting_conditions")
                or data.get("lighting_condition"),
                distance_mm=data.get("distance_mm"),
                viewing_angle=data.get("viewing_angle"),
            )

            db.session.add(metric)
            db.session.commit()

            return jsonify({"success": True, "metric_id": metric.id})
        except Exception:
            # Database save failed, return success without ID
            return jsonify(
                {
                    "success": True,
                    "metric_id": None,
                    "message": "Metrics not persisted - database unavailable",
                }
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
