"""
{
  "file_type": "calibration_pattern_generator",
  "purpose": "Generate calibration patterns for computer vision: ChArUco, ARUCO boards, AprilTags",
  "dependencies": ["opencv-python", "numpy"],
  "main_class": "CalibrationPatternGenerator",
  "key_methods": {
    "generate_charuco_board": "ChArUco board for camera calibration",
    "generate_aruco_board": "Fixed grid ARUCO pattern with known dimensions",
    "generate_apriltag": "AprilTag markers for robotics applications",
    "export_calibration_data": "Export calibration data in various formats"
  },
  "ai_navigation": {
    "modify_for": "Adding new calibration patterns or export formats",
    "used_by": ["web.py for calibration endpoints"],
    "output_format": "Calibration patterns with metadata"
  }
}
"""

try:
    import cv2
    import numpy as np

    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None  # type: ignore
    import numpy as np

    OPENCV_AVAILABLE = False

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import yaml


class CalibrationPatternGenerator:
    def __init__(self):
        if OPENCV_AVAILABLE and cv2 is not None:
            # Standard ARUCO dictionaries for calibration
            self.aruco_dicts = {
                "4X4_50": cv2.aruco.DICT_4X4_50,
                "4X4_100": cv2.aruco.DICT_4X4_100,
                "4X4_250": cv2.aruco.DICT_4X4_250,
                "4X4_1000": cv2.aruco.DICT_4X4_1000,
                "5X5_50": cv2.aruco.DICT_5X5_50,
                "5X5_100": cv2.aruco.DICT_5X5_100,
                "5X5_250": cv2.aruco.DICT_5X5_250,
                "5X5_1000": cv2.aruco.DICT_5X5_1000,
                "6X6_50": cv2.aruco.DICT_6X6_50,
                "6X6_100": cv2.aruco.DICT_6X6_100,
                "6X6_250": cv2.aruco.DICT_6X6_250,
                "6X6_1000": cv2.aruco.DICT_6X6_1000,
            }

            # AprilTag families
            self.apriltag_families = {
                "tag16h5": cv2.aruco.DICT_APRILTAG_16h5,
                "tag25h9": cv2.aruco.DICT_APRILTAG_25h9,
                "tag36h10": cv2.aruco.DICT_APRILTAG_36h10,
                "tag36h11": cv2.aruco.DICT_APRILTAG_36h11,
            }

    def generate_charuco_board(
        self,
        squares_x: int = 8,
        squares_y: int = 6,
        square_size_mm: float = 30.0,
        marker_size_mm: float = 22.5,
        dictionary: str = "4X4_50",
        paper_size: str = "A4",
    ) -> Dict[str, Any]:
        """
        Generate ChArUco board for camera calibration.

        Args:
            squares_x: Number of chessboard squares in X direction
            squares_y: Number of chessboard squares in Y direction
            square_size_mm: Size of each chess square in mm
            marker_size_mm: Size of ArUco markers in mm (should be < square_size)
            dictionary: ArUco dictionary to use
            paper_size: Target paper size (A4, A3, Letter, etc.)

        Returns:
            Dictionary containing board image, calibration data, and metadata
        """
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for ChArUco board generation")

        # Validate marker size
        if marker_size_mm >= square_size_mm:
            marker_size_mm = square_size_mm * 0.75

        # Get dictionary
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])

        # Create ChArUco board
        board = cv2.aruco.CharucoBoard(
            (squares_x, squares_y), square_size_mm, marker_size_mm, aruco_dict
        )

        # Calculate board size in mm
        board_width_mm = squares_x * square_size_mm
        board_height_mm = squares_y * square_size_mm

        # Generate board image at high resolution (10 pixels per mm)
        pixels_per_mm = 10
        board_width_px = int(board_width_mm * pixels_per_mm)
        board_height_px = int(board_height_mm * pixels_per_mm)

        board_image = board.generateImage((board_width_px, board_height_px))

        # Add white border for printing
        border_px = int(10 * pixels_per_mm)  # 10mm border
        bordered_image = cv2.copyMakeBorder(
            board_image,
            border_px,
            border_px,
            border_px,
            border_px,
            cv2.BORDER_CONSTANT,
            value=(255,),
        )

        # Generate calibration metadata
        calibration_data = {
            "pattern_type": "charuco",
            "board_size": [squares_x, squares_y],
            "square_size_mm": square_size_mm,
            "marker_size_mm": marker_size_mm,
            "dictionary": dictionary,
            "physical_width_mm": board_width_mm,
            "physical_height_mm": board_height_mm,
            "total_markers": (squares_x - 1) * (squares_y - 1) // 2,
            "corner_positions": self._get_charuco_corners(
                squares_x, squares_y, square_size_mm
            ),
            "marker_ids": list(range((squares_x - 1) * (squares_y - 1) // 2)),
            "generation_date": datetime.now().isoformat(),
            "checksum": hashlib.md5(board_image.tobytes()).hexdigest(),
        }

        return {
            "image": bordered_image,
            "calibration_data": calibration_data,
            "board_object": board,
            "dimensions_mm": (board_width_mm, board_height_mm),
        }

    def generate_aruco_board(
        self,
        markers_x: int = 4,
        markers_y: int = 3,
        marker_size_mm: float = 50.0,
        separation_mm: float = 10.0,
        dictionary: str = "4X4_50",
        first_marker_id: int = 0,
    ) -> Dict[str, Any]:
        """
        Generate ARUCO board with fixed grid of markers.

        Args:
            markers_x: Number of markers in X direction
            markers_y: Number of markers in Y direction
            marker_size_mm: Size of each marker in mm
            separation_mm: Separation between markers in mm
            dictionary: ArUco dictionary to use
            first_marker_id: ID of first marker (top-left)

        Returns:
            Dictionary containing board image, calibration data, and metadata
        """
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for ARUCO board generation")

        # Get dictionary
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])

        # Create marker IDs array
        total_markers = markers_x * markers_y
        marker_ids = np.arange(first_marker_id, first_marker_id + total_markers)

        # Create GridBoard
        board = cv2.aruco.GridBoard(
            (markers_x, markers_y),
            marker_size_mm,
            separation_mm,
            aruco_dict,
            marker_ids,
        )

        # Calculate board size
        board_width_mm = markers_x * marker_size_mm + (markers_x - 1) * separation_mm
        board_height_mm = markers_y * marker_size_mm + (markers_y - 1) * separation_mm

        # Generate board image
        pixels_per_mm = 10
        board_width_px = int(board_width_mm * pixels_per_mm)
        board_height_px = int(board_height_mm * pixels_per_mm)

        board_image = board.generateImage((board_width_px, board_height_px))

        # Add white border
        border_px = int(10 * pixels_per_mm)
        bordered_image = cv2.copyMakeBorder(
            board_image,
            border_px,
            border_px,
            border_px,
            border_px,
            cv2.BORDER_CONSTANT,
            value=(255,),
        )

        # Generate world coordinates for each marker
        marker_corners = []
        for row in range(markers_y):
            for col in range(markers_x):
                x = col * (marker_size_mm + separation_mm)
                y = row * (marker_size_mm + separation_mm)
                corners = [
                    [x, y, 0],
                    [x + marker_size_mm, y, 0],
                    [x + marker_size_mm, y + marker_size_mm, 0],
                    [x, y + marker_size_mm, 0],
                ]
                marker_corners.append(corners)

        # Calibration metadata
        calibration_data = {
            "pattern_type": "aruco_board",
            "grid_size": [markers_x, markers_y],
            "marker_size_mm": marker_size_mm,
            "separation_mm": separation_mm,
            "dictionary": dictionary,
            "physical_width_mm": board_width_mm,
            "physical_height_mm": board_height_mm,
            "total_markers": total_markers,
            "marker_ids": marker_ids.tolist(),
            "first_marker_id": first_marker_id,
            "marker_corners_3d": marker_corners,
            "generation_date": datetime.now().isoformat(),
            "checksum": hashlib.md5(board_image.tobytes()).hexdigest(),
        }

        return {
            "image": bordered_image,
            "calibration_data": calibration_data,
            "board_object": board,
            "dimensions_mm": (board_width_mm, board_height_mm),
        }

    def generate_apriltag(
        self,
        tag_family: str = "tag36h11",
        tag_id: int = 0,
        tag_size_mm: float = 50.0,
        border_bits: int = 1,
    ) -> Dict[str, Any]:
        """
        Generate AprilTag marker for robotics applications.

        Args:
            tag_family: AprilTag family (tag16h5, tag25h9, tag36h10, tag36h11)
            tag_id: Tag ID number
            tag_size_mm: Physical size of tag in mm
            border_bits: Number of border bits (usually 1)

        Returns:
            Dictionary containing tag image and metadata
        """
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for AprilTag generation")

        if tag_family not in self.apriltag_families:
            raise ValueError(f"Unknown AprilTag family: {tag_family}")

        # Get AprilTag dictionary
        apriltag_dict = cv2.aruco.getPredefinedDictionary(
            self.apriltag_families[tag_family]
        )

        # Generate tag image
        pixels_per_mm = 10
        tag_size_px = int(tag_size_mm * pixels_per_mm)

        tag_image = cv2.aruco.generateImageMarker(apriltag_dict, tag_id, tag_size_px)

        # Add white border for printing
        border_px = int(10 * pixels_per_mm)
        bordered_image = cv2.copyMakeBorder(
            tag_image,
            border_px,
            border_px,
            border_px,
            border_px,
            cv2.BORDER_CONSTANT,
            value=(255,),
        )

        # Get tag bits from family name
        if "16h5" in tag_family:
            tag_bits = 4
            hamming_distance = 5
        elif "25h9" in tag_family:
            tag_bits = 5
            hamming_distance = 9
        elif "36h10" in tag_family:
            tag_bits = 6
            hamming_distance = 10
        elif "36h11" in tag_family:
            tag_bits = 6
            hamming_distance = 11
        else:
            tag_bits = 6
            hamming_distance = 11

        # Generate metadata
        metadata = {
            "pattern_type": "apriltag",
            "tag_family": tag_family,
            "tag_id": tag_id,
            "tag_size_mm": tag_size_mm,
            "tag_bits": tag_bits,
            "hamming_distance": hamming_distance,
            "border_bits": border_bits,
            "corner_positions_3d": [
                [0, 0, 0],
                [tag_size_mm, 0, 0],
                [tag_size_mm, tag_size_mm, 0],
                [0, tag_size_mm, 0],
            ],
            "generation_date": datetime.now().isoformat(),
            "checksum": hashlib.md5(tag_image.tobytes()).hexdigest(),
        }

        return {
            "image": bordered_image,
            "metadata": metadata,
            "dimensions_mm": (tag_size_mm, tag_size_mm),
        }

    def generate_apriltag_grid(
        self,
        grid_x: int = 3,
        grid_y: int = 3,
        tag_family: str = "tag36h11",
        tag_size_mm: float = 40.0,
        spacing_mm: float = 20.0,
        first_tag_id: int = 0,
    ) -> Dict[str, Any]:
        """
        Generate grid of AprilTags for larger tracking areas.
        """
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for AprilTag generation")

        # Calculate grid dimensions
        grid_width_mm = grid_x * tag_size_mm + (grid_x - 1) * spacing_mm
        grid_height_mm = grid_y * tag_size_mm + (grid_y - 1) * spacing_mm

        # Create blank canvas
        pixels_per_mm = 10
        canvas_width = int((grid_width_mm + 20) * pixels_per_mm)  # 20mm border
        canvas_height = int((grid_height_mm + 20) * pixels_per_mm)
        canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255

        # Get AprilTag dictionary
        apriltag_dict = cv2.aruco.getPredefinedDictionary(
            self.apriltag_families[tag_family]
        )

        # Place tags on canvas
        tag_positions = []
        for row in range(grid_y):
            for col in range(grid_x):
                tag_id = first_tag_id + row * grid_x + col

                # Generate tag
                tag_size_px = int(tag_size_mm * pixels_per_mm)
                tag_image = cv2.aruco.generateImageMarker(
                    apriltag_dict, tag_id, tag_size_px
                )

                # Calculate position
                x_mm = col * (tag_size_mm + spacing_mm)
                y_mm = row * (tag_size_mm + spacing_mm)
                x_px = int((x_mm + 10) * pixels_per_mm)  # 10mm border offset
                y_px = int((y_mm + 10) * pixels_per_mm)

                # Place tag on canvas
                canvas[y_px : y_px + tag_size_px, x_px : x_px + tag_size_px] = tag_image

                # Store position data
                tag_positions.append(
                    {
                        "tag_id": tag_id,
                        "position_mm": [x_mm, y_mm, 0],
                        "corners_3d": [
                            [x_mm, y_mm, 0],
                            [x_mm + tag_size_mm, y_mm, 0],
                            [x_mm + tag_size_mm, y_mm + tag_size_mm, 0],
                            [x_mm, y_mm + tag_size_mm, 0],
                        ],
                    }
                )

        metadata = {
            "pattern_type": "apriltag_grid",
            "tag_family": tag_family,
            "grid_size": [grid_x, grid_y],
            "tag_size_mm": tag_size_mm,
            "spacing_mm": spacing_mm,
            "physical_width_mm": grid_width_mm,
            "physical_height_mm": grid_height_mm,
            "total_tags": grid_x * grid_y,
            "first_tag_id": first_tag_id,
            "tag_positions": tag_positions,
            "generation_date": datetime.now().isoformat(),
        }

        return {
            "image": canvas,
            "metadata": metadata,
            "dimensions_mm": (grid_width_mm, grid_height_mm),
        }

    def export_calibration_yaml(
        self, calibration_data: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Export calibration data as YAML (OpenCV format)."""
        yaml_data = {
            "calibration_time": calibration_data.get(
                "generation_date", datetime.now().isoformat()
            ),
            "pattern_type": calibration_data.get("pattern_type"),
            "image_width": 1920,  # Default camera resolution
            "image_height": 1080,
            "flags": 0,
            "camera_matrix": {
                "rows": 3,
                "cols": 3,
                "data": [
                    1000.0,
                    0.0,
                    960.0,
                    0.0,
                    1000.0,
                    540.0,
                    0.0,
                    0.0,
                    1.0,
                ],  # Default intrinsics
            },
            "distortion_coefficients": {
                "rows": 1,
                "cols": 5,
                "data": [0.0, 0.0, 0.0, 0.0, 0.0],  # Zero distortion
            },
        }

        # Add pattern-specific data
        if calibration_data["pattern_type"] == "charuco":
            yaml_data["charuco_board"] = {
                "squares_x": calibration_data["board_size"][0],
                "squares_y": calibration_data["board_size"][1],
                "square_size": calibration_data["square_size_mm"],
                "marker_size": calibration_data["marker_size_mm"],
                "dictionary": calibration_data["dictionary"],
            }
        elif calibration_data["pattern_type"] == "aruco_board":
            yaml_data["aruco_board"] = {
                "markers_x": calibration_data["grid_size"][0],
                "markers_y": calibration_data["grid_size"][1],
                "marker_size": calibration_data["marker_size_mm"],
                "marker_separation": calibration_data["separation_mm"],
                "dictionary": calibration_data["dictionary"],
            }

        if filename:
            with open(filename, "w") as f:
                yaml.dump(yaml_data, f, default_flow_style=False)

        return yaml.dump(yaml_data, default_flow_style=False)

    def export_calibration_json(
        self, calibration_data: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Export calibration data as JSON."""
        if filename:
            with open(filename, "w") as f:
                json.dump(calibration_data, f, indent=2)

        return json.dumps(calibration_data, indent=2)

    def export_ros_format(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export calibration data in ROS-compatible format."""
        ros_data = {
            "header": {
                "stamp": datetime.now().isoformat(),
                "frame_id": "camera_optical_frame",
            },
            "pattern": {
                "type": calibration_data.get("pattern_type"),
                "physical_dimensions": {
                    "width": calibration_data.get("physical_width_mm", 0)
                    / 1000.0,  # Convert to meters
                    "height": calibration_data.get("physical_height_mm", 0) / 1000.0,
                },
            },
        }

        if "marker_corners_3d" in calibration_data:
            # Convert mm to meters for ROS
            ros_data["pattern"]["markers"] = []
            for i, corners in enumerate(calibration_data["marker_corners_3d"]):
                ros_data["pattern"]["markers"].append(
                    {
                        "id": calibration_data["marker_ids"][i],
                        "corners": [
                            [c[0] / 1000.0, c[1] / 1000.0, c[2] / 1000.0]
                            for c in corners
                        ],
                    }
                )

        return ros_data

    def _get_charuco_corners(
        self, squares_x: int, squares_y: int, square_size: float
    ) -> List[List[float]]:
        """Calculate 3D positions of ChArUco board corners."""
        corners = []
        for y in range(squares_y):
            for x in range(squares_x):
                corners.append([x * square_size, y * square_size, 0])
        return corners
