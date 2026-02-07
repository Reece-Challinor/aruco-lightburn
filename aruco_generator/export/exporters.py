"""
Professional export formats for calibration and manufacturing.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>exporters.py</name>
    <version>2.2.0</version>
    <type>export_module</type>
    <purpose>Provide export pipelines for calibration and manufacturing outputs</purpose>
    <last_updated>2026-02-07</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

import json
import math
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional

import numpy as np
import yaml


class ProfessionalExporter:
    """Export calibration patterns to various professional formats."""

    def __init__(self):
        self.supported_formats = ["opencv_yaml", "ros_json", "dxf", "pdf", "stl"]

    def export_opencv_yaml(
        self, calibration_data: Dict[str, Any], camera_params: Optional[Dict] = None
    ) -> str:
        """Export to OpenCV calibration YAML format."""
        # Default camera parameters if not provided
        if not camera_params:
            camera_params = {
                "image_width": 1920,
                "image_height": 1080,
                "camera_matrix": [
                    [1000.0, 0.0, 960.0],
                    [0.0, 1000.0, 540.0],
                    [0.0, 0.0, 1.0],
                ],
                "distortion_coefficients": [0.0, 0.0, 0.0, 0.0, 0.0],
            }

        opencv_data = {
            "%YAML:1.0": None,
            "calibration_time": calibration_data.get(
                "generation_timestamp", datetime.now().isoformat()
            ),
            "image_width": camera_params["image_width"],
            "image_height": camera_params["image_height"],
            "flags": 0,
            "camera_name": "camera",
            "camera_matrix": {
                "rows": 3,
                "cols": 3,
                "dt": "d",
                "data": [
                    item for row in camera_params["camera_matrix"] for item in row
                ],
            },
            "distortion_model": "plumb_bob",
            "distortion_coefficients": {
                "rows": 1,
                "cols": 5,
                "dt": "d",
                "data": camera_params["distortion_coefficients"],
            },
        }

        # Add pattern-specific data
        if "pattern_type" in calibration_data:
            pattern_type = calibration_data["pattern_type"]

            if pattern_type == "charuco":
                opencv_data["charuco_board"] = {
                    "squares_x": calibration_data.get("board_size", [8, 6])[0],
                    "squares_y": calibration_data.get("board_size", [8, 6])[1],
                    "square_length": calibration_data.get("square_size_mm", 30.0),
                    "marker_length": calibration_data.get("marker_size_mm", 22.5),
                    "dictionary_id": self._get_opencv_dict_id(
                        calibration_data.get("dictionary", "4X4_50")
                    ),
                }

            elif pattern_type == "aruco_board":
                opencv_data["aruco_board"] = {
                    "markers_x": calibration_data.get("grid_size", [4, 3])[0],
                    "markers_y": calibration_data.get("grid_size", [4, 3])[1],
                    "marker_length": calibration_data.get("marker_size_mm", 50.0),
                    "marker_separation": calibration_data.get("separation_mm", 10.0),
                    "dictionary_id": self._get_opencv_dict_id(
                        calibration_data.get("dictionary", "4X4_50")
                    ),
                    "ids": calibration_data.get("marker_ids", []),
                }

        # Add marker coordinates if available
        if "markers" in calibration_data:
            marker_coords = []
            for marker in calibration_data["markers"]:
                if "corners" in marker:
                    for corner in marker["corners"]:
                        marker_coords.extend(corner)

            if marker_coords:
                opencv_data["object_points"] = {
                    "rows": len(calibration_data["markers"]) * 4,
                    "cols": 3,
                    "dt": "d",
                    "data": marker_coords,
                }

        # Convert to YAML
        yaml_str = yaml.dump(opencv_data, default_flow_style=False, sort_keys=False)
        # Fix YAML header
        yaml_str = "%YAML:1.0\n---\n" + yaml_str.replace("'%YAML:1.0': null\n", "")

        return yaml_str

    def export_ros_format(
        self, calibration_data: Dict[str, Any], frame_id: str = "camera_optical_frame"
    ) -> str:
        """Export to ROS calibration format (JSON)."""
        ros_data = {
            "header": {
                "seq": 0,
                "stamp": {
                    "secs": int(datetime.now().timestamp()),
                    "nsecs": int((datetime.now().timestamp() % 1) * 1e9),
                },
                "frame_id": frame_id,
            },
            "pattern_type": calibration_data.get("pattern_type", "aruco"),
            "pattern_parameters": {},
        }

        # Convert dimensions from mm to meters for ROS
        if "physical_width_mm" in calibration_data:
            ros_data["pattern_parameters"]["width"] = (
                calibration_data["physical_width_mm"] / 1000.0
            )
        if "physical_height_mm" in calibration_data:
            ros_data["pattern_parameters"]["height"] = (
                calibration_data["physical_height_mm"] / 1000.0
            )

        # Add marker information
        if "markers" in calibration_data:
            ros_data["markers"] = []
            for marker in calibration_data["markers"]:
                ros_marker = {
                    "id": marker.get("id", 0),
                    "size": marker.get("size_mm", 50) / 1000.0,  # Convert to meters
                    "pose": {
                        "position": {
                            "x": marker.get("position", [0, 0, 0])[0] / 1000.0,
                            "y": marker.get("position", [0, 0, 0])[1] / 1000.0,
                            "z": marker.get("position", [0, 0, 0])[2] / 1000.0,
                        },
                        "orientation": self._euler_to_quaternion(
                            marker.get("orientation", [0, 0, 0])
                        ),
                    },
                }

                # Add corners in ROS format
                if "corners" in marker:
                    ros_marker["corners"] = [
                        {"x": c[0] / 1000.0, "y": c[1] / 1000.0, "z": c[2] / 1000.0}
                        for c in marker["corners"]
                    ]

                ros_data["markers"].append(ros_marker)

        # Add coordinate frame information
        if "coordinate_system" in calibration_data:
            ros_data["coordinate_frame"] = {
                "reference_frame": calibration_data["coordinate_system"].get(
                    "reference_frame", "world"
                ),
                "origin": calibration_data["coordinate_system"].get(
                    "origin", [0, 0, 0]
                ),
            }

        return json.dumps(ros_data, indent=2)

    def export_dxf(
        self, calibration_data: Dict[str, Any], markers_data: List[Dict] = None
    ) -> BytesIO:
        """Export to DXF format for CNC/laser cutting."""
        dxf_content = []

        # DXF Header
        dxf_content.append("0\nSECTION\n2\nHEADER\n")
        dxf_content.append("9\n$ACADVER\n1\nAC1014\n")  # AutoCAD 2000 format
        dxf_content.append("9\n$INSUNITS\n70\n4\n")  # Millimeters
        dxf_content.append("0\nENDSEC\n")

        # Tables section
        dxf_content.append("0\nSECTION\n2\nTABLES\n")
        dxf_content.append("0\nTABLE\n2\nLTYPE\n70\n1\n")
        dxf_content.append(
            "0\nLTYPE\n2\nCONTINUOUS\n70\n0\n3\nSolid line\n72\n65\n73\n0\n40\n0.0\n"
        )
        dxf_content.append("0\nENDTAB\n")

        # Layers
        dxf_content.append("0\nTABLE\n2\nLAYER\n70\n3\n")
        dxf_content.append(
            "0\nLAYER\n2\n0\n70\n0\n62\n7\n6\nCONTINUOUS\n"
        )  # Default layer
        dxf_content.append(
            "0\nLAYER\n2\nCUT\n70\n0\n62\n1\n6\nCONTINUOUS\n"
        )  # Cut layer (red)
        dxf_content.append(
            "0\nLAYER\n2\nENGRAVE\n70\n0\n62\n5\n6\nCONTINUOUS\n"
        )  # Engrave layer (blue)
        dxf_content.append("0\nENDTAB\n")
        dxf_content.append("0\nENDSEC\n")

        # Entities section
        dxf_content.append("0\nSECTION\n2\nENTITIES\n")

        # Add markers as rectangles and filled areas
        if "markers" in calibration_data:
            for marker in calibration_data["markers"]:
                if "corners" in marker:
                    # Draw marker outline on CUT layer
                    corners = marker["corners"]
                    for i in range(4):
                        next_i = (i + 1) % 4
                        dxf_content.append(
                            f"0\nLINE\n8\nCUT\n"
                            f"10\n{corners[i][0]:.3f}\n"
                            f"20\n{corners[i][1]:.3f}\n"
                            f"30\n{corners[i][2]:.3f}\n"
                            f"11\n{corners[next_i][0]:.3f}\n"
                            f"21\n{corners[next_i][1]:.3f}\n"
                            f"31\n{corners[next_i][2]:.3f}\n"
                        )

                # Add marker ID as text
                if "position" in marker:
                    pos = marker["position"]
                    dxf_content.append(
                        f"0\nTEXT\n8\nENGRAVE\n"
                        f"10\n{pos[0]:.3f}\n"
                        f"20\n{pos[1]:.3f}\n"
                        f"30\n{pos[2]:.3f}\n"
                        f"40\n3.0\n"  # Text height
                        f"1\nID:{marker.get('id', 0)}\n"
                    )

        # Add pattern boundary if available
        if (
            "physical_width_mm" in calibration_data
            and "physical_height_mm" in calibration_data
        ):
            width = calibration_data["physical_width_mm"]
            height = calibration_data["physical_height_mm"]

            # Outer boundary rectangle
            dxf_content.append("0\nPOLYLINE\n8\nCUT\n66\n1\n70\n1\n")  # Closed polyline
            corners = [[0, 0], [width, 0], [width, height], [0, height]]
            for corner in corners:
                dxf_content.append(
                    f"0\nVERTEX\n8\nCUT\n10\n{corner[0]:.3f}\n20\n{corner[1]:.3f}\n30\n0.0\n"
                )
            dxf_content.append("0\nSEQEND\n")

        dxf_content.append("0\nENDSEC\n")
        dxf_content.append("0\nEOF\n")

        # Create BytesIO object
        dxf_bytes = BytesIO()
        dxf_bytes.write("".join(dxf_content).encode("utf-8"))
        dxf_bytes.seek(0)

        return dxf_bytes

    def export_stl_3d(
        self, calibration_data: Dict[str, Any], thickness_mm: float = 3.0
    ) -> BytesIO:
        """Export to STL format for 3D printing landing pads."""
        stl_content = []

        # STL ASCII format header
        stl_content.append("solid landing_pad\n")

        # Create a base plate
        width = calibration_data.get("physical_width_mm", 200)
        height = calibration_data.get("physical_height_mm", 200)

        # Define base vertices
        vertices = [
            [0, 0, 0],  # Bottom face
            [width, 0, 0],
            [width, height, 0],
            [0, height, 0],
            [0, 0, thickness_mm],  # Top face
            [width, 0, thickness_mm],
            [width, height, thickness_mm],
            [0, height, thickness_mm],
        ]

        # Define faces (triangles)
        faces = [
            # Bottom face
            [0, 2, 1],
            [0, 3, 2],
            # Top face
            [4, 5, 6],
            [4, 6, 7],
            # Front face
            [0, 1, 5],
            [0, 5, 4],
            # Back face
            [2, 3, 7],
            [2, 7, 6],
            # Left face
            [0, 4, 7],
            [0, 7, 3],
            # Right face
            [1, 2, 6],
            [1, 6, 5],
        ]

        # Write faces to STL
        for face in faces:
            # Calculate normal (simplified - assumes proper winding)
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]

            # Cross product for normal
            edge1 = [v2[i] - v1[i] for i in range(3)]
            edge2 = [v3[i] - v1[i] for i in range(3)]
            normal = [
                edge1[1] * edge2[2] - edge1[2] * edge2[1],
                edge1[2] * edge2[0] - edge1[0] * edge2[2],
                edge1[0] * edge2[1] - edge1[1] * edge2[0],
            ]

            # Normalize
            length = math.sqrt(sum(n * n for n in normal))
            if length > 0:
                normal = [n / length for n in normal]

            stl_content.append(
                f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n"
            )
            stl_content.append("    outer loop\n")
            for vertex_idx in face:
                v = vertices[vertex_idx]
                stl_content.append(f"      vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            stl_content.append("    endloop\n")
            stl_content.append("  endfacet\n")

        # Add raised markers if needed (simplified)
        if "markers" in calibration_data:
            for marker in calibration_data["markers"][:5]:  # Limit for demo
                if "corners" in marker:
                    # Add a raised square for each marker
                    corners = marker["corners"]
                    marker_height = thickness_mm + 0.5  # Raised 0.5mm

                    # Create raised marker vertices
                    marker_vertices = []
                    for corner in corners:
                        marker_vertices.append([corner[0], corner[1], thickness_mm])
                        marker_vertices.append([corner[0], corner[1], marker_height])

                    # Add top face of raised marker
                    stl_content.append("  facet normal 0 0 1\n")
                    stl_content.append("    outer loop\n")
                    for i in [1, 3, 5]:  # Top vertices
                        v = marker_vertices[i]
                        stl_content.append(
                            f"      vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n"
                        )
                    stl_content.append("    endloop\n")
                    stl_content.append("  endfacet\n")

        stl_content.append("endsolid landing_pad\n")

        # Create BytesIO object
        stl_bytes = BytesIO()
        stl_bytes.write("".join(stl_content).encode("utf-8"))
        stl_bytes.seek(0)

        return stl_bytes

    def _get_opencv_dict_id(self, dict_name: str) -> int:
        """Convert dictionary name to OpenCV dictionary ID."""
        dict_map = {
            "4X4_50": 0,
            "4X4_100": 1,
            "4X4_250": 2,
            "4X4_1000": 3,
            "5X5_50": 4,
            "5X5_100": 5,
            "5X5_250": 6,
            "5X5_1000": 7,
            "6X6_50": 8,
            "6X6_100": 9,
            "6X6_250": 10,
            "6X6_1000": 11,
            "7X7_50": 12,
            "7X7_100": 13,
            "7X7_250": 14,
            "7X7_1000": 15,
            "ARUCO_ORIGINAL": 16,
            "tag16h5": 17,
            "tag25h9": 18,
            "tag36h10": 19,
            "tag36h11": 20,
        }
        return dict_map.get(dict_name, 0)

    def _euler_to_quaternion(self, euler_deg: List[float]) -> Dict[str, float]:
        """Convert Euler angles (degrees) to quaternion."""
        # Convert to radians
        roll = math.radians(euler_deg[0])
        pitch = math.radians(euler_deg[1])
        yaw = math.radians(euler_deg[2])

        # Calculate quaternion
        qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(
            roll / 2
        ) * math.sin(pitch / 2) * math.sin(yaw / 2)
        qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(
            roll / 2
        ) * math.cos(pitch / 2) * math.sin(yaw / 2)
        qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(
            roll / 2
        ) * math.sin(pitch / 2) * math.cos(yaw / 2)
        qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(
            roll / 2
        ) * math.sin(pitch / 2) * math.sin(yaw / 2)

        return {"x": qx, "y": qy, "z": qz, "w": qw}


class PDFExporter:
    """Export patterns as PDF using ReportLab."""

    def __init__(self):
        try:
            import reportlab  # noqa: F401

            self.available = True
        except ImportError:
            self.available = False

    def generate_pdf(
        self,
        markers: List[Dict[str, Any]],
        size_mm: float,
        include_labels: bool = True,
        include_outer_border: bool = False,
        border_width: float = 2.0,
    ) -> bytes:
        """
        Generate PDF with marker grid.

        Args:
            markers: List of marker data (including images)
            size_mm: Size of each marker in mm
            include_labels: Whether to include ID labels
            include_outer_border: Whether to render an outer border around the grid
            border_width: Width of the outer border margin in mm

        Returns:
            bytes: PDF file content

        Raises:
            ImportError: If reportlab is not installed
        """
        if not self.available:
            raise ImportError("ReportLab is not installed")

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mms
        from reportlab.pdfgen import canvas

        # Calculate grid bounds to center on page
        # Note: we are receiving absolute positions in 'markers', assuming they start from 0,0
        # If we want to center them on A4, we need to find bounding box.

        if not markers:
            return b""

        max_x = max(m["x"] for m in markers) + size_mm
        max_y = max(m["y"] for m in markers) + size_mm
        border_offset = border_width if include_outer_border else 0.0

        # Center on A4 (or adjust page size if too big)
        page_w, page_h = A4

        content_w = (max_x + 2 * border_offset) * mms
        content_h = (max_y + 2 * border_offset) * mms

        if content_w > page_w or content_h > page_h:
            # Create custom pagesize
            page_size = (content_w + 20 * mms, content_h + 20 * mms)
        else:
            page_size = A4

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=page_size)

        # Calculate offset to center
        margin_x = (page_size[0] - content_w) / 2
        margin_y = (page_size[1] - content_h) / 2

        # In PDF, origin is bottom-left. In our system, origin is top-left usually or handled by logic.
        # Let's assume our Y is from top-down logic (SVG style), so we need to flip it for PDF.
        # But wait, our 'y' values in markers are 0-based from top-left.
        # So marker at y=0 should be at page_height - margin_y - size_mm

        for marker in markers:
            # Position
            x = margin_x + (marker["x"] + border_offset) * mms
            # Flip Y coordinate system: page_height - top_margin - y_offset - height of marker
            y = (
                page_size[1]
                - margin_y
                - (marker["y"] + border_offset) * mms
                - size_mm * mms
            )

            w = size_mm * mms
            h = size_mm * mms

            # Draw Marker
            if "image" in marker and marker["image"] is not None:
                self._draw_marker_vector(c, marker["image"], x, y, w)
            else:
                # Fallback placeholder
                c.rect(x, y, w, h)

            # Draw Label
            if include_labels:
                c.setFont("Helvetica", 10)
                text = f"ID: {marker['id']}"
                text_w = c.stringWidth(text, "Helvetica", 10)
                # Text below marker
                c.drawString(x + (w - text_w) / 2, y - 12, text)

        if include_outer_border:
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(0.5)
            border_x = margin_x
            border_y = page_size[1] - margin_y - content_h
            c.rect(border_x, border_y, content_w, content_h, stroke=1, fill=0)

        c.showPage()
        c.save()

        return buffer.getvalue()

    def _draw_marker_vector(
        self, c, image: np.ndarray, x: float, y: float, size: float
    ):
        """Draw marker using vector rectangles for sharpness."""
        # Image is a binary numpy array (0=white, 255=black) or similar
        # If it's pure black/white, we only draw black (255?) squares?
        # Usually ArUCO: 0=black, 255=white. Let's check `aruco.py` generate_marker docstring:
        # "0=white, 255=black" based on standard image conventions?
        # Wait, cv2.aruco.generateImageMarker returns 0 for black and 255 for white usually.
        # Let's verify standard assumption: Markers have black borders.
        # If I look at `aruco.py` fallback: "final_pattern[i, j] = 255 if value > 127 else 0"
        # And it says "Create border (always black)".
        # Let's assume convention: 0 is black, 255 is white.
        # Actually in `aruco.py` fallback: "pattern[i + 1, j + 1] = 255 if bit_value else 0". border is 0.
        # So 0 is BLACK, 255 is WHITE.

        rows, cols = image.shape
        pixel_size = size / cols

        c.setFillColorRGB(0, 0, 0)

        for r in range(rows):
            for col in range(cols):
                val = image[r, col]
                if val < 127:  # Black pixel
                    # PDF Y is bottom-left, so row 0 is at top (y + size - pixel_size)
                    px = x + col * pixel_size
                    py = y + size - (r + 1) * pixel_size
                    c.rect(px, py, pixel_size, pixel_size, fill=1, stroke=0)
