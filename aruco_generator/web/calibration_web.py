"""
Web routes for calibration pattern generation.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>calibration_web.py</name>
    <version>2.5.0</version>
    <type>flask_blueprint</type>
    <purpose>Calibration pattern routes for ChArUco, ARUCO boards, and AprilTags</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
  <route_summary>
    <route path="/calibration" method="GET" purpose="Render calibration UI"/>
    <route path="/api/calibration/charuco" method="POST" purpose="Generate ChArUco board"/>
    <route path="/api/calibration/aruco_board" method="POST" purpose="Generate ARUCO board"/>
    <route path="/api/calibration/apriltag" method="POST" purpose="Generate AprilTag marker"/>
    <route path="/api/calibration/apriltag_grid" method="POST" purpose="Generate AprilTag grid"/>
    <route path="/api/calibration/export/<id>" method="GET" purpose="Export calibration data"/>
    <route path="/api/calibration/export/<id>/bundle" method="GET" purpose="Export calibration bundle"/>
    <route path="/api/calibration/import" method="POST" purpose="Import calibration data"/>
  </route_summary>
</ai_agent_documentation>
-->
"""

import base64
import json
import zipfile
from datetime import datetime
from io import BytesIO

try:
    import cv2

    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None  # type: ignore
    OPENCV_AVAILABLE = False

import yaml
from flask import Blueprint, current_app, render_template, request, send_file
from werkzeug.exceptions import NotFound

from ..calibration.calibration import CalibrationPatternGenerator
from ..core.utils import (
    APIServiceUnavailableError,
    APIValidationError,
    api_success,
    handle_api_errors,
)
from ..db.extensions import db
from ..db.models import CalibrationPattern
from ..export.exporters import ProfessionalExporter

# NOTE (roadmap F-10, 2026-07-03): pattern persistence endpoints in this
# module are FROZEN — kept for compatibility, no new capabilities. The
# detection-metrics write path was removed entirely (serverless production
# runs a per-invocation in-memory DB, so persisted metrics were misleading).

# Create Blueprint
calibration_bp = Blueprint("calibration", __name__)

# Initialize calibration generator
calibration_gen = CalibrationPatternGenerator()
exporter = ProfessionalExporter()


def _get_json_payload():
    return request.get_json(silent=True) or {}


def _parse_int(
    data,
    key,
    default,
    label=None,
    min_value=None,
    max_value=None,
    required=False,
):
    label = label or key.replace("_", " ").title()
    raw_value = data.get(key, default)
    if raw_value in (None, "") and default is None and not required:
        return None
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise APIValidationError(
            f"{label} must be an integer", fields={key: "Must be an integer"}
        )
    if min_value is not None and value < min_value:
        raise APIValidationError(
            f"{label} must be at least {min_value}",
            fields={key: f"Must be >= {min_value}"},
        )
    if max_value is not None and value > max_value:
        raise APIValidationError(
            f"{label} must be at most {max_value}",
            fields={key: f"Must be <= {max_value}"},
        )
    return value


def _parse_float(
    data,
    key,
    default,
    label=None,
    min_value=None,
    max_value=None,
    required=False,
):
    label = label or key.replace("_", " ").title()
    raw_value = data.get(key, default)
    if raw_value in (None, "") and default is None and not required:
        return None
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        raise APIValidationError(
            f"{label} must be a number", fields={key: "Must be a number"}
        )
    if min_value is not None and value < min_value:
        raise APIValidationError(
            f"{label} must be at least {min_value}",
            fields={key: f"Must be >= {min_value}"},
        )
    if max_value is not None and value > max_value:
        raise APIValidationError(
            f"{label} must be at most {max_value}",
            fields={key: f"Must be <= {max_value}"},
        )
    return value


def _parse_bool(data, key, default=False):
    raw_value = data.get(key, default)
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, str):
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(raw_value)


def _validate_aruco_dictionary(dictionary, field="dictionary"):
    if not hasattr(calibration_gen, "aruco_dicts") or not calibration_gen.aruco_dicts:
        raise APIServiceUnavailableError("OpenCV required for ArUco dictionary access")
    if not dictionary or dictionary not in calibration_gen.aruco_dicts:
        available = ", ".join(sorted(calibration_gen.aruco_dicts.keys()))
        raise APIValidationError(
            f'Unknown ArUco dictionary "{dictionary}". Available: {available}',
            fields={field: "Select a valid dictionary"},
            suggestions=sorted(calibration_gen.aruco_dicts.keys())[:5],
        )


def _validate_apriltag_family(tag_family, field="tag_family"):
    if not hasattr(calibration_gen, "apriltag_families"):
        raise APIServiceUnavailableError("OpenCV required for AprilTag access")
    if not tag_family:
        raise APIValidationError(
            "AprilTag family is required", fields={field: "Required"}
        )
    if tag_family not in calibration_gen.apriltag_families:
        available = ", ".join(sorted(calibration_gen.apriltag_families.keys()))
        raise APIValidationError(
            f'Unknown AprilTag family "{tag_family}". Available: {available}',
            fields={field: "Select a valid tag family"},
            suggestions=sorted(calibration_gen.apriltag_families.keys())[:5],
        )


def _read_import_file(file):
    if not file or not getattr(file, "filename", ""):
        raise APIValidationError(
            "No calibration file provided", fields={"file": "Required"}
        )

    filename = file.filename or ""
    lower_name = filename.lower()
    if not (
        lower_name.endswith(".json")
        or lower_name.endswith(".yaml")
        or lower_name.endswith(".yml")
    ):
        raise APIValidationError(
            "Unsupported calibration file format",
            fields={"file": "Use .json, .yaml, or .yml"},
        )

    max_bytes = current_app.config.get("MAX_IMPORT_BYTES", 2 * 1024 * 1024)
    file_bytes = file.read()
    if not file_bytes:
        raise APIValidationError(
            "Import file is empty", fields={"file": "File is empty"}
        )
    if len(file_bytes) > max_bytes:
        raise APIValidationError(
            f"Import file exceeds {max_bytes // (1024 * 1024)}MB limit",
            fields={"file": "File too large"},
        )
    return file_bytes, filename


def _encode_image_base64(image):
    if not OPENCV_AVAILABLE or cv2 is None:
        raise APIServiceUnavailableError("OpenCV required for image encoding")
    success, buffer = cv2.imencode(".png", image)
    if not success:
        raise APIValidationError("Unable to encode preview image")
    return base64.b64encode(buffer).decode("utf-8")


def _persist_pattern(pattern):
    if not current_app.config.get("USE_DB", False):
        return (
            None,
            False,
            {
                "code": "db_disabled",
                "message": "Database disabled - pattern not persisted",
            },
        )
    try:
        db.session.add(pattern)
        db.session.commit()
        return pattern.id, True, None
    except Exception:
        db.session.rollback()
        return (
            None,
            False,
            {
                "code": "db_unavailable",
                "message": "Pattern not persisted - database unavailable",
            },
        )


def _build_preview_response(result, pattern_id=None, persisted=False):
    calibration_data = result.get("calibration_data") or result.get("metadata") or {}
    response = {
        "image_base64": _encode_image_base64(result["image"]),
        "calibration_data": calibration_data,
        "metadata": calibration_data,
        "dimensions_mm": result.get("dimensions_mm"),
        "pattern_id": pattern_id,
        "persisted": persisted,
    }
    return response


def _dictionary_name_from_id(dictionary_id):
    if dictionary_id is None:
        return None
    if not hasattr(calibration_gen, "aruco_dicts"):
        return None
    for name, value in calibration_gen.aruco_dicts.items():
        if int(value) == int(dictionary_id):
            return name
    return None


def _parse_import_file(file_bytes, filename):
    if not file_bytes:
        raise APIValidationError(
            "Import file is empty", fields={"file": "File is empty"}
        )
    text = file_bytes.decode("utf-8", errors="ignore")
    if filename and filename.lower().endswith(".json"):
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise APIValidationError(
                "Invalid JSON calibration file", fields={"file": "Invalid JSON"}
            ) from exc
    if text.lstrip().startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise APIValidationError(
                "Invalid JSON calibration file", fields={"file": "Invalid JSON"}
            ) from exc

    sanitized = "\n".join(
        line for line in text.splitlines() if not line.startswith("%YAML")
    )
    try:
        payload = yaml.safe_load(sanitized)
    except yaml.YAMLError as exc:
        raise APIValidationError(
            "Invalid YAML calibration file", fields={"file": "Invalid YAML"}
        ) from exc
    if payload is None:
        raise APIValidationError(
            "Unable to parse YAML calibration data", fields={"file": "Invalid YAML"}
        )
    return payload


def _normalize_import_payload(payload):
    if isinstance(payload, dict) and isinstance(payload.get("calibration_data"), dict):
        data = payload["calibration_data"]
    else:
        data = payload

    if not isinstance(data, dict):
        raise APIValidationError("Calibration import expects a JSON or YAML object")

    pattern_type = data.get("pattern_type")
    if not pattern_type:
        if "charuco_board" in data:
            pattern_type = "charuco"
        elif "aruco_board" in data:
            pattern_type = "aruco_board"
        elif "apriltag_grid" in data:
            pattern_type = "apriltag_grid"
        elif "apriltag" in data:
            pattern_type = "apriltag"

    if not pattern_type:
        raise APIValidationError("Unsupported calibration data format")

    extras = dict(data)
    extras.pop("pattern_type", None)

    if pattern_type == "charuco":
        board = data.get("charuco_board", {})
        board_size = data.get("board_size") or [
            board.get("squares_x"),
            board.get("squares_y"),
        ]
        square_size = (
            data.get("square_size_mm")
            or board.get("square_size")
            or board.get("square_length")
        )
        marker_size = (
            data.get("marker_size_mm")
            or board.get("marker_size")
            or board.get("marker_length")
        )
        dictionary = (
            data.get("dictionary")
            or board.get("dictionary")
            or _dictionary_name_from_id(board.get("dictionary_id"))
        )
        base_data = {
            "pattern_type": "charuco",
            "board_size": board_size,
            "square_size_mm": square_size,
            "marker_size_mm": marker_size,
            "dictionary": dictionary,
            "paper_size": data.get("paper_size", board.get("paper_size", "A4")),
        }
        return base_data, extras

    if pattern_type == "aruco_board":
        board = data.get("aruco_board", {})
        grid_size = data.get("grid_size") or [
            board.get("markers_x"),
            board.get("markers_y"),
        ]
        marker_size = (
            data.get("marker_size_mm")
            or board.get("marker_size")
            or board.get("marker_length")
        )
        separation = data.get("separation_mm") or board.get("marker_separation")
        dictionary = (
            data.get("dictionary")
            or board.get("dictionary")
            or _dictionary_name_from_id(board.get("dictionary_id"))
        )
        base_data = {
            "pattern_type": "aruco_board",
            "grid_size": grid_size,
            "marker_size_mm": marker_size,
            "separation_mm": separation,
            "dictionary": dictionary,
            "first_marker_id": data.get("first_marker_id", 0),
        }
        return base_data, extras

    if pattern_type == "apriltag":
        tag_data = data.get("apriltag", {})
        base_data = {
            "pattern_type": "apriltag",
            "tag_family": data.get("tag_family") or tag_data.get("tag_family"),
            "tag_id": data.get("tag_id") or tag_data.get("tag_id", 0),
            "tag_size_mm": data.get("tag_size_mm") or tag_data.get("tag_size_mm"),
            "border_bits": data.get("border_bits", tag_data.get("border_bits", 1)),
        }
        return base_data, extras

    if pattern_type == "apriltag_grid":
        grid = data.get("apriltag_grid", {})
        grid_size = data.get("grid_size") or [grid.get("grid_x"), grid.get("grid_y")]
        base_data = {
            "pattern_type": "apriltag_grid",
            "grid_size": grid_size,
            "tag_family": data.get("tag_family") or grid.get("tag_family"),
            "tag_size_mm": data.get("tag_size_mm") or grid.get("tag_size_mm"),
            "spacing_mm": data.get("spacing_mm") or grid.get("spacing_mm", 0),
            "first_tag_id": data.get("first_tag_id", grid.get("first_tag_id", 0)),
        }
        return base_data, extras

    raise APIValidationError("Unsupported calibration pattern type")


def _generate_from_calibration_data(calibration_data):
    pattern_type = calibration_data.get("pattern_type")
    if pattern_type == "charuco":
        squares_x, squares_y = calibration_data.get("board_size", [None, None])
        if squares_x is None or squares_y is None:
            raise APIValidationError(
                "ChArUco import requires board_size", fields={"board_size": "Required"}
            )
        if calibration_data.get("square_size_mm") is None:
            raise APIValidationError(
                "ChArUco import requires square_size_mm",
                fields={"square_size_mm": "Required"},
            )
        if calibration_data.get("marker_size_mm") is None:
            raise APIValidationError(
                "ChArUco import requires marker_size_mm",
                fields={"marker_size_mm": "Required"},
            )
        if not calibration_data.get("dictionary"):
            raise APIValidationError(
                "ChArUco import requires dictionary", fields={"dictionary": "Required"}
            )
        return calibration_gen.generate_charuco_board(
            squares_x=int(squares_x),
            squares_y=int(squares_y),
            square_size_mm=float(calibration_data.get("square_size_mm")),
            marker_size_mm=float(calibration_data.get("marker_size_mm")),
            dictionary=calibration_data.get("dictionary", "4X4_50"),
            paper_size=calibration_data.get("paper_size", "A4"),
        )
    if pattern_type == "aruco_board":
        grid_x, grid_y = calibration_data.get("grid_size", [None, None])
        if grid_x is None or grid_y is None:
            raise APIValidationError(
                "ArUco board import requires grid_size",
                fields={"grid_size": "Required"},
            )
        if calibration_data.get("marker_size_mm") is None:
            raise APIValidationError(
                "ArUco board import requires marker_size_mm",
                fields={"marker_size_mm": "Required"},
            )
        if not calibration_data.get("dictionary"):
            raise APIValidationError(
                "ArUco board import requires dictionary",
                fields={"dictionary": "Required"},
            )
        return calibration_gen.generate_aruco_board(
            markers_x=int(grid_x),
            markers_y=int(grid_y),
            marker_size_mm=float(calibration_data.get("marker_size_mm")),
            separation_mm=float(calibration_data.get("separation_mm", 0)),
            dictionary=calibration_data.get("dictionary", "4X4_50"),
            first_marker_id=int(calibration_data.get("first_marker_id", 0)),
        )
    if pattern_type == "apriltag":
        if calibration_data.get("tag_size_mm") is None:
            raise APIValidationError(
                "AprilTag import requires tag_size_mm",
                fields={"tag_size_mm": "Required"},
            )
        if not calibration_data.get("tag_family"):
            raise APIValidationError(
                "AprilTag import requires tag_family", fields={"tag_family": "Required"}
            )
        return calibration_gen.generate_apriltag(
            tag_family=calibration_data.get("tag_family", "tag36h11"),
            tag_id=int(calibration_data.get("tag_id", 0)),
            tag_size_mm=float(calibration_data.get("tag_size_mm")),
            border_bits=int(calibration_data.get("border_bits", 1)),
        )
    if pattern_type == "apriltag_grid":
        grid_x, grid_y = calibration_data.get("grid_size", [None, None])
        if grid_x is None or grid_y is None:
            raise APIValidationError(
                "AprilTag grid import requires grid_size",
                fields={"grid_size": "Required"},
            )
        if calibration_data.get("tag_size_mm") is None:
            raise APIValidationError(
                "AprilTag grid import requires tag_size_mm",
                fields={"tag_size_mm": "Required"},
            )
        if not calibration_data.get("tag_family"):
            raise APIValidationError(
                "AprilTag grid import requires tag_family",
                fields={"tag_family": "Required"},
            )
        return calibration_gen.generate_apriltag_grid(
            grid_x=int(grid_x),
            grid_y=int(grid_y),
            tag_family=calibration_data.get("tag_family", "tag36h11"),
            tag_size_mm=float(calibration_data.get("tag_size_mm")),
            spacing_mm=float(calibration_data.get("spacing_mm", 0)),
            first_tag_id=int(calibration_data.get("first_tag_id", 0)),
        )

    raise APIValidationError("Unsupported calibration pattern type")


def _build_pattern_from_calibration_data(calibration_data, pattern_name):
    pattern_type = calibration_data.get("pattern_type")
    if pattern_type == "charuco":
        squares_x, squares_y = calibration_data.get("board_size", [None, None])
        square_size = calibration_data.get("square_size_mm")
        marker_size = calibration_data.get("marker_size_mm")
        dictionary = calibration_data.get("dictionary")
        if not all([squares_x, squares_y, square_size, marker_size, dictionary]):
            raise APIValidationError("ChArUco import missing required parameters")
        physical_width = calibration_data.get("physical_width_mm") or (
            float(squares_x) * float(square_size)
        )
        physical_height = calibration_data.get("physical_height_mm") or (
            float(squares_y) * float(square_size)
        )
        total_markers = calibration_data.get("total_markers") or (
            (int(squares_x) * int(squares_y) + 1) // 2
        )
        return CalibrationPattern(
            pattern_type="charuco",
            pattern_name=pattern_name,
            physical_width_mm=physical_width,
            physical_height_mm=physical_height,
            marker_size_mm=float(marker_size),
            grid_size_x=int(squares_x),
            grid_size_y=int(squares_y),
            dictionary_type=dictionary,
            total_markers=int(total_markers),
            first_marker_id=int(calibration_data.get("first_marker_id", 0)),
            calibration_data=calibration_data,
            image_checksum=calibration_data.get("checksum"),
        )
    if pattern_type == "aruco_board":
        grid_x, grid_y = calibration_data.get("grid_size", [None, None])
        marker_size = calibration_data.get("marker_size_mm")
        separation = calibration_data.get("separation_mm", 0)
        dictionary = calibration_data.get("dictionary")
        if not all([grid_x, grid_y, marker_size, dictionary]):
            raise APIValidationError("ArUco board import missing required parameters")
        physical_width = calibration_data.get("physical_width_mm") or (
            float(grid_x) * float(marker_size) + (float(grid_x) - 1) * float(separation)
        )
        physical_height = calibration_data.get("physical_height_mm") or (
            float(grid_y) * float(marker_size) + (float(grid_y) - 1) * float(separation)
        )
        total_markers = calibration_data.get("total_markers") or (
            int(grid_x) * int(grid_y)
        )
        return CalibrationPattern(
            pattern_type="aruco_board",
            pattern_name=pattern_name,
            physical_width_mm=physical_width,
            physical_height_mm=physical_height,
            marker_size_mm=float(marker_size),
            grid_size_x=int(grid_x),
            grid_size_y=int(grid_y),
            dictionary_type=dictionary,
            total_markers=int(total_markers),
            first_marker_id=int(calibration_data.get("first_marker_id", 0)),
            calibration_data=calibration_data,
            image_checksum=calibration_data.get("checksum"),
        )
    if pattern_type == "apriltag":
        tag_size = calibration_data.get("tag_size_mm")
        tag_family = calibration_data.get("tag_family")
        tag_id = calibration_data.get("tag_id", 0)
        if not all([tag_size, tag_family]):
            raise APIValidationError("AprilTag import missing required parameters")
        physical_width = calibration_data.get("physical_width_mm") or float(tag_size)
        physical_height = calibration_data.get("physical_height_mm") or float(tag_size)
        return CalibrationPattern(
            pattern_type="apriltag",
            pattern_name=pattern_name,
            physical_width_mm=physical_width,
            physical_height_mm=physical_height,
            marker_size_mm=float(tag_size),
            grid_size_x=1,
            grid_size_y=1,
            dictionary_type=tag_family,
            total_markers=1,
            first_marker_id=int(tag_id),
            calibration_data=calibration_data,
            image_checksum=calibration_data.get("checksum"),
        )
    if pattern_type == "apriltag_grid":
        grid_x, grid_y = calibration_data.get("grid_size", [None, None])
        tag_size = calibration_data.get("tag_size_mm")
        spacing = calibration_data.get("spacing_mm", 0)
        tag_family = calibration_data.get("tag_family")
        if not all([grid_x, grid_y, tag_size, tag_family]):
            raise APIValidationError("AprilTag grid import missing required parameters")
        physical_width = calibration_data.get("physical_width_mm") or (
            float(grid_x) * float(tag_size) + (float(grid_x) - 1) * float(spacing)
        )
        physical_height = calibration_data.get("physical_height_mm") or (
            float(grid_y) * float(tag_size) + (float(grid_y) - 1) * float(spacing)
        )
        total_markers = calibration_data.get("total_markers") or (
            int(grid_x) * int(grid_y)
        )
        return CalibrationPattern(
            pattern_type="apriltag_grid",
            pattern_name=pattern_name,
            physical_width_mm=physical_width,
            physical_height_mm=physical_height,
            marker_size_mm=float(tag_size),
            grid_size_x=int(grid_x),
            grid_size_y=int(grid_y),
            dictionary_type=tag_family,
            total_markers=int(total_markers),
            first_marker_id=int(calibration_data.get("first_tag_id", 0)),
            calibration_data=calibration_data,
            image_checksum=calibration_data.get("checksum"),
        )

    raise APIValidationError("Unsupported calibration pattern type")


@calibration_bp.route("/calibration")
def calibration_page():
    """Render calibration patterns page."""
    return render_template("calibration.html")


@calibration_bp.route("/api/calibration/charuco", methods=["POST"])
@handle_api_errors
def generate_charuco():
    """Generate ChArUco board for camera calibration."""
    data = _get_json_payload()

    squares_x = _parse_int(data, "squares_x", 8, "Squares X", min_value=2, max_value=50)
    squares_y = _parse_int(data, "squares_y", 6, "Squares Y", min_value=2, max_value=50)
    square_size_mm = _parse_float(
        data, "square_size_mm", 30.0, "Square size", min_value=1.0
    )
    marker_size_mm = _parse_float(
        data, "marker_size_mm", 22.5, "Marker size", min_value=1.0
    )
    if marker_size_mm >= square_size_mm:
        raise APIValidationError(
            "Marker size must be smaller than square size",
            fields={"marker_size_mm": "Must be < square size"},
        )

    dictionary = data.get("dictionary", "4X4_50")
    _validate_aruco_dictionary(dictionary)
    paper_size = data.get("paper_size", "A4")
    save_to_db = _parse_bool(data, "save_to_db", False)
    pattern_name = str(data.get("pattern_name") or f"ChArUco_{squares_x}x{squares_y}")

    result = calibration_gen.generate_charuco_board(
        squares_x=squares_x,
        squares_y=squares_y,
        square_size_mm=square_size_mm,
        marker_size_mm=marker_size_mm,
        dictionary=dictionary,
        paper_size=paper_size,
    )

    pattern_id = None
    persisted = False
    warning = None
    if save_to_db:
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
            image_checksum=result["calibration_data"].get("checksum"),
        )
        pattern_id, persisted, warning = _persist_pattern(pattern)

    warnings = [warning] if warning else []
    return api_success(
        _build_preview_response(result, pattern_id, persisted), warnings=warnings
    )


@calibration_bp.route("/api/calibration/aruco_board", methods=["POST"])
@handle_api_errors
def generate_aruco_board():
    """Generate ARUCO board with fixed grid."""
    data = _get_json_payload()

    markers_x = _parse_int(data, "markers_x", 4, "Markers X", min_value=1, max_value=50)
    markers_y = _parse_int(data, "markers_y", 3, "Markers Y", min_value=1, max_value=50)
    marker_size_mm = _parse_float(
        data, "marker_size_mm", 50.0, "Marker size", min_value=1.0
    )
    separation_mm = _parse_float(
        data, "separation_mm", 10.0, "Separation", min_value=0.0
    )
    dictionary = data.get("dictionary", "4X4_50")
    _validate_aruco_dictionary(dictionary)
    first_marker_id = _parse_int(
        data, "first_marker_id", 0, "First marker ID", min_value=0
    )
    save_to_db = _parse_bool(data, "save_to_db", False)
    pattern_name = str(
        data.get("pattern_name") or f"ARUCO_Board_{markers_x}x{markers_y}"
    )

    result = calibration_gen.generate_aruco_board(
        markers_x=markers_x,
        markers_y=markers_y,
        marker_size_mm=marker_size_mm,
        separation_mm=separation_mm,
        dictionary=dictionary,
        first_marker_id=first_marker_id,
    )

    pattern_id = None
    persisted = False
    warning = None
    if save_to_db:
        pattern = CalibrationPattern(
            pattern_type="aruco_board",
            pattern_name=pattern_name,
            physical_width_mm=result["dimensions_mm"][0],
            physical_height_mm=result["dimensions_mm"][1],
            marker_size_mm=marker_size_mm,
            grid_size_x=markers_x,
            grid_size_y=markers_y,
            dictionary_type=dictionary,
            total_markers=markers_x * markers_y,
            first_marker_id=first_marker_id,
            calibration_data=result["calibration_data"],
            image_checksum=result["calibration_data"].get("checksum"),
        )
        pattern_id, persisted, warning = _persist_pattern(pattern)

    warnings = [warning] if warning else []
    return api_success(
        _build_preview_response(result, pattern_id, persisted), warnings=warnings
    )


@calibration_bp.route("/api/calibration/apriltag", methods=["POST"])
@handle_api_errors
def generate_apriltag():
    """Generate single AprilTag marker."""
    data = _get_json_payload()

    tag_family = data.get("tag_family", "tag36h11")
    _validate_apriltag_family(tag_family)
    tag_id = _parse_int(data, "tag_id", 0, "Tag ID", min_value=0)
    tag_size_mm = _parse_float(data, "tag_size_mm", 50.0, "Tag size", min_value=1.0)
    save_to_db = _parse_bool(data, "save_to_db", False)
    pattern_name = str(data.get("pattern_name") or f"AprilTag_{tag_family}_{tag_id}")

    result = calibration_gen.generate_apriltag(
        tag_family=tag_family, tag_id=tag_id, tag_size_mm=tag_size_mm
    )

    pattern_id = None
    persisted = False
    warning = None
    if save_to_db:
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
            calibration_data=result["calibration_data"],
            image_checksum=result["calibration_data"].get("checksum"),
        )
        pattern_id, persisted, warning = _persist_pattern(pattern)

    warnings = [warning] if warning else []
    return api_success(
        _build_preview_response(result, pattern_id, persisted), warnings=warnings
    )


@calibration_bp.route("/api/calibration/apriltag_grid", methods=["POST"])
@handle_api_errors
def generate_apriltag_grid():
    """Generate grid of AprilTags."""
    data = _get_json_payload()

    grid_x = _parse_int(data, "grid_x", 3, "Grid X", min_value=1, max_value=50)
    grid_y = _parse_int(data, "grid_y", 3, "Grid Y", min_value=1, max_value=50)
    tag_family = data.get("tag_family", "tag36h11")
    _validate_apriltag_family(tag_family)
    tag_size_mm = _parse_float(data, "tag_size_mm", 40.0, "Tag size", min_value=1.0)
    spacing_mm = _parse_float(data, "spacing_mm", 20.0, "Spacing", min_value=0.0)
    first_tag_id = _parse_int(data, "first_tag_id", 0, "First tag ID", min_value=0)
    save_to_db = _parse_bool(data, "save_to_db", False)
    pattern_name = str(data.get("pattern_name") or f"AprilTag_Grid_{grid_x}x{grid_y}")

    result = calibration_gen.generate_apriltag_grid(
        grid_x=grid_x,
        grid_y=grid_y,
        tag_family=tag_family,
        tag_size_mm=tag_size_mm,
        spacing_mm=spacing_mm,
        first_tag_id=first_tag_id,
    )

    pattern_id = None
    persisted = False
    warning = None
    if save_to_db:
        pattern = CalibrationPattern(
            pattern_type="apriltag_grid",
            pattern_name=pattern_name,
            physical_width_mm=result["dimensions_mm"][0],
            physical_height_mm=result["dimensions_mm"][1],
            marker_size_mm=tag_size_mm,
            grid_size_x=grid_x,
            grid_size_y=grid_y,
            dictionary_type=tag_family,
            total_markers=grid_x * grid_y,
            first_marker_id=first_tag_id,
            calibration_data=result["calibration_data"],
            image_checksum=result["calibration_data"].get("checksum"),
        )
        pattern_id, persisted, warning = _persist_pattern(pattern)

    warnings = [warning] if warning else []
    return api_success(
        _build_preview_response(result, pattern_id, persisted), warnings=warnings
    )


@calibration_bp.route("/api/calibration/export/<int:pattern_id>", methods=["GET"])
@handle_api_errors
def export_calibration_data(pattern_id):
    """Export calibration data in various formats."""
    if not current_app.config.get("USE_DB", False):
        raise APIValidationError(
            "Calibration export requires database persistence",
            status=409,
            fields={"pattern_id": "Persist a pattern before export"},
        )

    pattern = db.session.get(CalibrationPattern, pattern_id)
    if not pattern:
        raise NotFound(f"Calibration pattern {pattern_id} not found")
    export_format = request.args.get("format", "yaml")

    if export_format == "yaml":
        yaml_data = calibration_gen.export_calibration_yaml(pattern.calibration_data)
        buffer = BytesIO(yaml_data.encode("utf-8"))
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="text/yaml",
            as_attachment=True,
            download_name=f"calibration_{pattern_id}.yaml",
        )
    if export_format == "json":
        json_data = calibration_gen.export_calibration_json(pattern.calibration_data)
        buffer = BytesIO(json_data.encode("utf-8"))
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"calibration_{pattern_id}.json",
        )
    if export_format == "ros":
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

    raise APIValidationError(
        "Invalid export format", fields={"format": "Invalid format"}
    )


@calibration_bp.route(
    "/api/calibration/export/<int:pattern_id>/bundle", methods=["GET"]
)
@handle_api_errors
def export_calibration_bundle(pattern_id):
    """Export calibration data bundle (image + YAML/JSON/ROS)."""
    if not current_app.config.get("USE_DB", False):
        raise APIValidationError(
            "Calibration export requires database persistence",
            status=409,
            fields={"pattern_id": "Persist a pattern before export"},
        )

    pattern = db.session.get(CalibrationPattern, pattern_id)
    if not pattern:
        raise NotFound(f"Calibration pattern {pattern_id} not found")
    calibration_data = pattern.calibration_data or {}

    result = _generate_from_calibration_data(calibration_data)
    result["calibration_data"] = calibration_data

    bundle = BytesIO()
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f"calibration_{pattern_id}.json",
            calibration_gen.export_calibration_json(calibration_data),
        )
        archive.writestr(
            f"calibration_{pattern_id}.yaml",
            calibration_gen.export_calibration_yaml(calibration_data),
        )
        ros_data = calibration_gen.export_ros_format(calibration_data)
        archive.writestr(
            f"calibration_{pattern_id}_ros.json", json.dumps(ros_data, indent=2)
        )
        opencv_yaml = exporter.export_opencv_yaml(calibration_data)
        archive.writestr(f"calibration_{pattern_id}_opencv.yaml", opencv_yaml)

        if not OPENCV_AVAILABLE or cv2 is None:
            raise APIServiceUnavailableError("OpenCV required for image export")
        success, buffer = cv2.imencode(".png", result["image"])
        if success:
            archive.writestr(f"calibration_{pattern_id}.png", buffer.tobytes())

    bundle.seek(0)
    return send_file(
        bundle,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"calibration_{pattern_id}_bundle.zip",
    )


@calibration_bp.route("/api/calibration/import", methods=["POST"])
@handle_api_errors
def import_calibration_data():
    """Import calibration data from JSON/YAML and generate preview."""
    file = request.files.get("file") or request.files.get("pattern")
    file_bytes, filename = _read_import_file(file)
    payload = _parse_import_file(file_bytes, filename or "")
    base_data, extras = _normalize_import_payload(payload)
    result = _generate_from_calibration_data(base_data)

    merged_data = dict(result["calibration_data"])
    for key, value in extras.items():
        if key not in merged_data:
            merged_data[key] = value

    result["calibration_data"] = merged_data

    form_data = request.form.to_dict()
    save_to_db = _parse_bool(form_data, "save_to_db", True)
    pattern_name = (
        form_data.get("pattern_name")
        or payload.get("pattern_name")
        or merged_data.get("pattern_name")
        or f"Imported_{merged_data.get('pattern_type', 'pattern')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    pattern_id = None
    persisted = False
    warning = None
    if save_to_db:
        pattern = _build_pattern_from_calibration_data(merged_data, pattern_name)
        pattern_id, persisted, warning = _persist_pattern(pattern)

    warnings = [warning] if warning else []
    return api_success(
        _build_preview_response(result, pattern_id, persisted), warnings=warnings
    )


@calibration_bp.route("/api/calibration/patterns", methods=["GET"])
@handle_api_errors
def list_calibration_patterns():
    """List all saved calibration patterns."""
    if not current_app.config.get("USE_DB", False):
        return api_success(
            {"patterns": [], "total": 0},
            warnings=[
                {
                    "code": "db_disabled",
                    "message": "Database unavailable - patterns not persisted",
                }
            ],
        )

    patterns = CalibrationPattern.query.order_by(
        CalibrationPattern.created_at.desc()
    ).all()
    return api_success(
        {"patterns": [p.to_dict() for p in patterns], "total": len(patterns)}
    )
