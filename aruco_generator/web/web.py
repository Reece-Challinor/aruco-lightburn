"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>web.py</name>
    <version>3.1.0</version>
    <type>flask_web_module</type>
    <purpose>Main Flask API endpoints for ArUCO marker generation and management</purpose>
    <last_updated>2026-02-06</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>

  <golden_path>
    <description>Primary workflow for marker generation through web interface</description>
    <steps>
      <step id="1">User visits / (index) → home.html template</step>
      <step id="2">User navigates to /generate → generate.html with marker creation interface</step>
      <step id="3">Frontend calls GET /api/dictionaries → returns available ArUCO dictionaries</step>
      <step id="4">User configures parameters → Frontend calls POST /api/preview → returns SVG preview</step>
      <step id="5">User downloads → Frontend calls POST /api/download → returns .lbrn2 LightBurn file</step>
    </steps>
    <fallback_paths>
      <fallback condition="preview_fails">Return detailed error message with parameter guidance</fallback>
      <fallback condition="invalid_dictionary">Return list of available dictionaries</fallback>
      <fallback condition="opencv_unavailable">Use ArUCO fallback pattern generation</fallback>
    </fallback_paths>
  </golden_path>

  <api_endpoints>
    <page_routes>
      <route path="/" method="GET" function="index" returns="home.html template" description="Landing page with navigation"/>
      <route path="/generate" method="GET" function="generate_page" returns="generate.html template" description="Marker generation interface"/>
      <route path="/validation" method="GET" function="validation_page" returns="validation.html template" description="Quality validation tools"/>
      <route path="/documentation" method="GET" function="documentation_page" returns="documentation.html template" description="Help and documentation"/>
    </page_routes>

    <api_routes>
      <route path="/api/dictionaries" method="GET" function="get_dictionaries" returns="JSON dictionary info" description="Available ArUCO dictionaries with metadata"/>
      <route path="/api/preview" method="POST" function="generate_preview" returns="JSON with SVG" description="Generate SVG preview of marker grid">
        <parameters>
          <param name="dictionary" type="string" required="true" description="ArUCO dictionary name"/>
          <param name="start_id" type="integer" default="0" description="Starting marker ID"/>
          <param name="rows" type="integer" default="1" description="Number of rows in grid"/>
          <param name="cols" type="integer" default="1" description="Number of columns in grid"/>
          <param name="size_mm" type="float" default="20" description="Marker size in millimeters"/>
          <param name="spacing_mm" type="float" default="5" description="Spacing between markers"/>
          <param name="include_labels" type="boolean" default="false" description="Include ID labels"/>
          <param name="include_outer_border" type="boolean" default="false" description="Include outer border"/>
          <param name="border_width" type="float" default="2.0" description="Border width in mm"/>
        </parameters>
        <validation>
          <rule field="start_id" condition=">=0" error="Start ID must be non-negative"/>
          <rule field="rows" condition=">0" error="Rows must be positive integers"/>
          <rule field="cols" condition=">0" error="Columns must be positive integers"/>
          <rule field="size_mm" condition=">0" error="Marker size must be positive (in millimeters)"/>
          <rule field="spacing_mm" condition=">=0" error="Spacing must be non-negative (in millimeters)"/>
          <rule field="dictionary" condition="in_dictionaries" error="Invalid dictionary, see available options"/>
        </validation>
      </route>
      <route path="/api/download" method="POST" function="download_lightburn" returns="LightBurn .lbrn2 file" description="Generate and download LightBurn laser cutting file"/>
      <route path="/api/advanced_preview" method="POST" function="generate_advanced_preview" returns="JSON with advanced SVG" description="Advanced preview with additional features"/>
      <route path="/api/batch_generate" method="POST" function="batch_generate" returns="JSON with multiple marker sets" description="Generate multiple sets of markers"/>
      <route path="/api/presets" method="GET" function="get_presets" returns="JSON preset configurations" description="Predefined marker configurations"/>
      <route path="/api/export/svg" method="POST" function="export_svg" returns="SVG file download" description="Export markers as SVG file"/>
      <route path="/api/export/pdf" method="POST" function="export_pdf" returns="Error (not implemented)" description="PDF export placeholder"/>
      <route path="/api/quick-test" method="GET" function="quick_test" returns="JSON test results" description="API health check endpoint"/>
    </api_routes>

    <debug_routes>
      <route path="/api/debug/status" method="GET" function="debug_status" returns="JSON system status" description="System status and version info"/>
      <route path="/api/log-error" method="POST" function="log_error" returns="JSON confirmation" description="Frontend error logging"/>
    </debug_routes>
  </api_endpoints>

  <data_structures>
    <marker_object>
      <field name="id" type="integer" description="Unique marker identifier"/>
      <field name="x" type="float" description="X position in millimeters"/>
      <field name="y" type="float" description="Y position in millimeters"/>
      <field name="size" type="float" description="Marker size in millimeters"/>
      <field name="dict" type="string" description="Dictionary name used"/>
      <field name="image" type="numpy.ndarray" description="Generated marker image (optional)"/>
    </marker_object>

    <api_response>
      <success_response>
        <field name="svg" type="string" description="Generated SVG content"/>
        <field name="dimensions" type="object" description="Width and height in mm"/>
        <field name="marker_count" type="integer" description="Total markers generated"/>
        <field name="success" type="boolean" description="Operation success flag"/>
      </success_response>
      <error_response>
        <field name="error" type="string" description="Human-readable error message"/>
        <field name="details" type="string" description="Technical details (optional)"/>
      </error_response>
    </api_response>

    <preset_configuration>
      <field name="name" type="string" description="Human-readable preset name"/>
      <field name="dictionary" type="string" description="ArUCO dictionary to use"/>
      <field name="size_mm" type="float" description="Marker size in millimeters"/>
      <field name="spacing_mm" type="float" description="Spacing between markers"/>
      <field name="rows" type="integer" description="Number of rows"/>
      <field name="cols" type="integer" description="Number of columns"/>
      <field name="description" type="string" description="Use case description"/>
    </preset_configuration>
  </data_structures>

  <error_handling>
    <validation_errors>
      <error code="400" type="invalid_dictionary" message="Invalid dictionary with available options"/>
      <error code="400" type="invalid_parameters" message="Specific parameter validation messages"/>
      <error code="400" type="negative_values" message="Size and position must be positive"/>
    </validation_errors>
    <system_errors>
      <error code="500" type="generation_failure" message="Marker generation failed"/>
      <error code="500" type="export_failure" message="File export failed"/>
      <error code="501" type="not_implemented" message="Feature not yet available"/>
    </system_errors>
    <fallback_strategies>
      <strategy name="opencv_fallback" trigger="cv2_import_error" action="Use ArUCO fallback patterns"/>
      <strategy name="graceful_degradation" trigger="generation_error" action="Return detailed error with recovery steps"/>
      <strategy name="parameter_guidance" trigger="validation_error" action="Provide specific correction guidance"/>
    </fallback_strategies>
  </error_handling>

  <logging_and_alerts>
    <log_levels>
      <level name="INFO" events="successful_generation, api_calls, file_downloads"/>
      <level name="WARNING" events="parameter_validation_failures, opencv_fallback_usage"/>
      <level name="ERROR" events="generation_failures, export_failures, system_errors"/>
      <level name="DEBUG" events="detailed_parameter_info, internal_state_changes"/>
    </log_levels>
    <alert_conditions>
      <alert name="high_error_rate" condition="error_rate > 10%" action="Log warning"/>
      <alert name="opencv_unavailable" condition="cv2_import_fails" action="Log warning with fallback notice"/>
      <alert name="invalid_dictionary_spike" condition="invalid_dict_requests > 5/min" action="Log info"/>
    </alert_conditions>
    <monitoring_endpoints>
      <endpoint path="/api/debug/status" metrics="opencv_version, dictionary_count, timestamp"/>
      <endpoint path="/api/quick-test" metrics="generation_success, performance_timing"/>
    </monitoring_endpoints>
  </logging_and_alerts>

  <dependencies>
    <external_modules>
      <module name="flask" purpose="Web framework and routing" critical="true"/>
      <module name="io" purpose="File handling and BytesIO operations" critical="true"/>
      <module name="logging" purpose="Error and event logging" critical="true"/>
      <module name="datetime" purpose="Timestamp generation" critical="false"/>
    </external_modules>
    <internal_modules>
      <module name="app" purpose="Flask application instance" critical="true"/>
      <module name="ArUCOGenerator" purpose="Core marker generation logic" critical="true"/>
      <module name="LightBurnExporter" purpose="LightBurn file generation" critical="true"/>
      <module name="DrawingContext" purpose="SVG rendering and drawing" critical="true"/>
    </internal_modules>
  </dependencies>

  <performance_considerations>
    <bottlenecks>
      <bottleneck location="marker_generation" description="OpenCV marker generation can be slow for large grids"/>
      <bottleneck location="svg_rendering" description="Complex SVG generation for many markers"/>
      <bottleneck location="file_exports" description="Large file generation and transfer"/>
    </bottlenecks>
    <optimizations>
      <optimization name="batch_processing" description="Generate multiple markers efficiently"/>
      <optimization name="caching" description="Cache dictionary info and common patterns"/>
      <optimization name="streaming" description="Stream large file downloads"/>
    </optimizations>
  </performance_considerations>

  <security_considerations>
    <input_validation>
      <validation name="parameter_sanitization" description="All user inputs validated and sanitized"/>
      <validation name="file_size_limits" description="Generated files have reasonable size limits"/>
      <validation name="rate_limiting" description="API endpoints should be rate limited"/>
    </input_validation>
    <data_protection>
      <protection name="no_sensitive_data" description="No sensitive data in logs or responses"/>
      <protection name="safe_file_names" description="Generated filenames are safe and predictable"/>
    </data_protection>
  </security_considerations>
</ai_agent_documentation>
-->

Flask Web Routes for ArUCO Marker Generation
=============================================

This module provides the main web interface and API endpoints for the ArUCO marker
generator application. It handles user requests for marker generation, preview,
and file exports through a clean REST API.

Architecture Overview:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Flask Routes  │───▶│   ArUCO Core    │
│   (JavaScript)  │    │   (this file)   │    │   (aruco.py)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   Error         │    │   File Export   │
│   (Jinja2)      │    │   Handling      │    │   (LightBurn)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Primary Workflow:
1. User visits web interface → Flask serves HTML templates
2. JavaScript makes API calls → Flask validates and processes requests
3. Core ArUCO generation → Returns structured data or files
4. Error handling → Provides specific guidance for failures

Key API Patterns:
- GET /api/* → Information endpoints (dictionaries, presets, status)
- POST /api/* → Generation endpoints (preview, download, export)
- All endpoints return JSON except file downloads
- Comprehensive input validation with specific error messages
- Graceful fallback when OpenCV is unavailable
"""

import io
import logging
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request, send_file

from ..core.aruco import ArUCOGenerator
from ..core.drawing import DrawingContext
from ..core.utils import handle_api_errors, validate_generation_params
from ..export.lightburn import LightBurnExporter

# Create Blueprint
web_bp = Blueprint("web", __name__)

# Initialize core components
aruco_gen = ArUCOGenerator()
lightburn_exporter = LightBurnExporter()
logger = logging.getLogger(__name__)


# Page routes
@web_bp.route("/")
def index():
    """Landing page"""
    return render_template("home.html")


@web_bp.route("/generate")
def generate_page():
    """Generate markers page"""
    return render_template("generate.html", dictionaries={})


# Calibration route is defined in calibration_web.py


@web_bp.route("/validation")
def validation_page():
    """Validation page"""
    return render_template("validation.html")


@web_bp.route("/documentation")
def documentation_page():
    """Documentation page"""
    return render_template("documentation.html")


# API endpoints - simplified without service layer
@web_bp.route("/api/dictionaries")
def get_dictionaries():
    """Get available ArUCO dictionaries"""
    return jsonify(aruco_gen.get_dictionary_info())


@web_bp.route("/api/preview", methods=["POST"])
@handle_api_errors
def generate_preview():
    """Generate SVG preview of markers"""
    data = request.get_json()
    params = validate_generation_params(data, list(aruco_gen.dictionaries.keys()))

    # Generate markers
    markers = aruco_gen.generate_grid(
        start_id=params["start_id"],
        dict_name=params["dictionary"],
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    # Prepare markers for drawing
    marker_data = []
    for marker_info in markers:
        marker_data.append(
            {
                "x": marker_info["x"],
                "y": marker_info["y"],
                "size": marker_info["size"],
                "id": marker_info["id"],
                "image": marker_info.get("image"),
            }
        )

    # Create drawing context and generate SVG
    ctx = DrawingContext()
    ctx.add_marker_grid_preview(
        marker_data,
        include_borders=True,
        include_outer_border=params["include_outer_border"],
        border_width=params["border_width"],
    )

    # Add labels if requested
    if params["include_labels"]:
        ctx.add_text_labels(marker_data)

    svg_content = ctx.get_svg()

    # Calculate dimensions
    total_width, total_height = aruco_gen.calculate_total_size(
        params["rows"], params["cols"], params["size_mm"], params["spacing_mm"]
    )

    if params["include_labels"]:
        total_height += 6

    if params["include_outer_border"]:
        total_width += 2 * params["border_width"]
        total_height += 2 * params["border_width"]

    return jsonify(
        {
            "svg": svg_content,
            "dimensions": {
                "width": round(total_width, 2),
                "height": round(total_height, 2),
            },
            "total_width": total_width,
            "total_height": total_height,
            "marker_count": params["rows"] * params["cols"],
            "success": True,
        }
    )


@web_bp.route("/api/download", methods=["POST"])
@handle_api_errors
def download_lightburn():
    """Generate and download LightBurn file"""
    data = request.get_json()
    params = validate_generation_params(data, list(aruco_gen.dictionaries.keys()))

    # Generate markers
    markers = aruco_gen.generate_grid(
        start_id=params["start_id"],
        dict_name=params["dictionary"],
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    # Create drawing context with actual marker pixels for accurate export
    ctx = DrawingContext()
    ctx.add_marker_grid(
        markers,
        include_borders=params["include_borders"],
        include_outer_border=params["include_outer_border"],
        border_width=params["border_width"],
    )

    if params["include_labels"]:
        ctx.add_text_labels(markers)

    metadata = {
        "dictionary": params["dictionary"],
        "start_id": params["start_id"],
        "rows": params["rows"],
        "cols": params["cols"],
        "size_mm": params["size_mm"],
        "spacing_mm": params["spacing_mm"],
        "border_bits": params["border_bits"],
        "include_labels": params["include_labels"],
        "include_outer_border": params["include_outer_border"],
        "include_alignment": params["include_alignment"],
        "include_rulers": params["include_rulers"],
    }

    # Generate LightBurn file
    output = lightburn_exporter.export(ctx, metadata)
    lightburn_content = output.getvalue()

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aruco_{params['dictionary']}_{params['rows']}x{params['cols']}_{timestamp}.lbrn2"

    return send_file(
        io.BytesIO(lightburn_content),
        as_attachment=True,
        download_name=filename,
        mimetype="application/octet-stream",
    )


@web_bp.route("/api/advanced_preview", methods=["POST"])
@handle_api_errors
def generate_advanced_preview():
    """Generate advanced preview with additional options"""
    data = request.get_json()
    # reuse basic validation but extract specific advanced flag manually if strictly needed,
    # or rely on the dict returned. validate_generation_params passes through unknown keys?
    # Actually validate_generation_params extracts specific keys.
    # But advanced_preview uses 'include_borders' which we added to the utils return.
    params = validate_generation_params(data, list(aruco_gen.dictionaries.keys()))

    # Generate markers
    markers = aruco_gen.generate_grid(
        start_id=params["start_id"],
        dict_name=params["dictionary"],
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    # Create drawing context and generate SVG with advanced options
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

    return jsonify(
        {
            "svg": svg_content,
            "count": len(markers),
            "dimensions": {"width": total_width, "height": total_height},
        }
    )


@web_bp.route("/api/batch_generate", methods=["POST"])
def batch_generate():
    """Generate multiple sets of markers"""
    try:
        data = request.get_json()

        # Batch specific validation (keeping it simple here for now or could refactor too)
        sets = int(data.get("sets", 1))
        markers_per_set = int(data.get("markers_per_set", 5))
        start_id = int(data.get("start_id", 0))
        dictionary = data.get("dictionary", "4X4_250")
        size_mm = float(data.get("size_mm", 30))
        spacing_mm = float(data.get("spacing_mm", 5))

        if dictionary not in aruco_gen.dictionaries:
            # Just reusing the logic for now as it's slightly different structure
            raise ValueError(f"Invalid dictionary: {dictionary}")

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
                generate_images=False,  # Don't generate images for batch
            )

            all_markers.append(
                {
                    "set_index": set_idx,
                    "markers": markers,
                    "start_id": set_start_id,
                    "end_id": set_start_id + markers_per_set - 1,
                }
            )

        return jsonify(
            {
                "success": True,
                "results": all_markers,
                "sets": all_markers,
                "total_markers": sets * markers_per_set,
                "dictionary": dictionary,
            }
        )

    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        return jsonify({"error": str(e)}), 500


@web_bp.route("/api/presets")
def get_presets():
    """Get predefined marker configuration presets"""
    presets = {
        "business_cards": {
            "name": "Business Card Size",
            "dictionary": "4X4_50",
            "size_mm": 15,
            "spacing_mm": 5,
            "rows": 2,
            "cols": 3,
            "description": "Fits on standard business card",
        },
        "inventory_tags": {
            "name": "Inventory Tags",
            "dictionary": "6X6_250",
            "size_mm": 25,
            "spacing_mm": 10,
            "rows": 4,
            "cols": 4,
            "description": "For warehouse inventory tracking",
        },
        "drone_landing": {
            "name": "Drone Landing Pad",
            "dictionary": "7X7_50",
            "size_mm": 100,
            "spacing_mm": 20,
            "rows": 3,
            "cols": 3,
            "description": "Large markers for drone navigation",
        },
        "camera_calibration": {
            "name": "Camera Calibration",
            "dictionary": "4X4_100",
            "size_mm": 40,
            "spacing_mm": 10,
            "rows": 5,
            "cols": 7,
            "description": "Standard camera calibration grid",
        },
    }

    return jsonify(presets)


@web_bp.route("/api/export/svg", methods=["POST"])
@handle_api_errors
def export_svg():
    """Export markers as SVG file"""
    data = request.get_json()
    params = validate_generation_params(data, list(aruco_gen.dictionaries.keys()))

    # Generate markers with actual images
    markers = aruco_gen.generate_grid(
        start_id=params["start_id"],
        dict_name=params["dictionary"],
        rows=params["rows"],
        cols=params["cols"],
        size_mm=params["size_mm"],
        spacing_mm=params["spacing_mm"],
    )

    # Create drawing context and generate SVG with merged rectangles
    ctx = DrawingContext()
    ctx.add_marker_grid(
        markers,
        include_borders=params["include_borders"],
        include_outer_border=params["include_outer_border"],
    )

    if params["include_labels"]:
        ctx.add_text_labels(markers)

    svg_content = ctx.get_svg()

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aruco_{params['dictionary']}_{params['rows']}x{params['cols']}_{timestamp}.svg"

    return send_file(
        io.BytesIO(svg_content.encode("utf-8")),
        as_attachment=True,
        download_name=filename,
        mimetype="image/svg+xml",
    )


@web_bp.route("/api/export/pdf", methods=["POST"])
@handle_api_errors
def export_pdf():
    """Export markers as PDF file"""
    try:
        from .exporters import PDFExporter

        pdf_exporter = PDFExporter()

        data = request.get_json()
        params = validate_generation_params(data, list(aruco_gen.dictionaries.keys()))

        # Generate markers with actual images
        markers = aruco_gen.generate_grid(
            start_id=params["start_id"],
            dict_name=params["dictionary"],
            rows=params["rows"],
            cols=params["cols"],
            size_mm=params["size_mm"],
            spacing_mm=params["spacing_mm"],
        )

        # Generate PDF
        pdf_content = pdf_exporter.generate_pdf(
            markers=markers,
            size_mm=params["size_mm"],
            include_labels=params["include_labels"],
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aruco_{params['dictionary']}_{params['rows']}x{params['cols']}_{timestamp}.pdf"

        return send_file(
            io.BytesIO(pdf_content),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
    except ImportError:
        return (
            jsonify(
                {
                    "error": "PDF export libraries not installed. Please install reportlab."
                }
            ),
            501,
        )
    except Exception as e:
        logger.error(f"PDF Export failed: {e}")
        raise e


@web_bp.route("/api/quick-test")
def quick_test():
    """Quick test endpoint to verify API is working"""
    try:
        # Generate a simple test marker - fixed argument order
        test_marker = aruco_gen.generate_marker(0, "4X4_50", 200)
        return jsonify(
            {
                "status": "success",
                "message": "API is working",
                "test_marker_shape": (
                    test_marker.shape if hasattr(test_marker, "shape") else "Generated"
                ),
                "available_dictionaries": len(aruco_gen.dictionaries),
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Quick test failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# Debug endpoints (can be removed in production)
@web_bp.route("/api/debug/status")
def debug_status():
    """Debug status endpoint"""
    try:
        import cv2

        opencv_version = cv2.__version__
    except Exception:
        opencv_version = "Not available"

    return jsonify(
        {
            "status": "operational",
            "opencv": opencv_version,
            "dictionaries": len(aruco_gen.dictionaries),
            "timestamp": datetime.now().isoformat(),
        }
    )


@web_bp.route("/api/log-error", methods=["POST"])
def log_error():
    """Log frontend errors"""
    try:
        error_data = request.get_json()
        logger.error(f"Frontend error: {error_data}")
        return jsonify({"status": "logged"}), 200
    except Exception as e:
        logger.error(f"Failed to log frontend error: {e}")
        return jsonify({"status": "failed"}), 500
