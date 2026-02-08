"""
Calibration pattern generator for computer vision.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>calibration.py</name>
    <version>2.5.0</version>
    <type>calibration_engine</type>
    <purpose>Generate calibration patterns and export metadata for ChArUco, ARUCO boards, and AprilTags</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->

{
  "file_type": "calibration_pattern_generator",
  "purpose": "Generate calibration patterns for computer vision: ChArUco, ARUCO boards, AprilTags",
  "dependencies": ["opencv-python", "numpy"],
  "main_class": "CalibrationPatternGenerator",
  "last_updated": "2026-02-08",
  "key_methods": {
    "generate_charuco_board": "ChArUco board for camera calibration",
    "generate_aruco_board": "Fixed grid ARUCO pattern with known dimensions",
    "generate_apriltag": "AprilTag markers for robotics applications",
    "generate_apriltag_grid": "AprilTag grid for wide-area tracking",
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

from aruco_generator import __version__ as app_version

DEFAULT_PIXELS_PER_MM = 10
DEFAULT_BORDER_MM = 10
CALIBRATION_SCHEMA_VERSION = "1.1"


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
        self.pixels_per_mm = DEFAULT_PIXELS_PER_MM
        self.border_mm = DEFAULT_BORDER_MM

    def _get_aruco_dictionary(self, dictionary: str):
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for ArUco dictionary access")
        if not dictionary or dictionary not in self.aruco_dicts:
            available = ", ".join(sorted(self.aruco_dicts.keys()))
            raise ValueError(
                f'Unknown ArUco dictionary "{dictionary}". Available: {available}'
            )
        return cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])

    def _get_apriltag_dictionary(self, tag_family: str):
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for AprilTag dictionary access")
        if not tag_family or tag_family not in self.apriltag_families:
            available = ", ".join(sorted(self.apriltag_families.keys()))
            raise ValueError(
                f'Unknown AprilTag family "{tag_family}". Available: {available}'
            )
        return cv2.aruco.getPredefinedDictionary(self.apriltag_families[tag_family])

    @staticmethod
    def _checksum_image(image) -> str:
        return hashlib.sha256(image.tobytes()).hexdigest()

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

        if squares_x < 2 or squares_y < 2:
            raise ValueError("Squares X and Y must be at least 2")
        if square_size_mm <= 0:
            raise ValueError("Square size must be positive (in millimeters)")
        if marker_size_mm <= 0:
            raise ValueError("Marker size must be positive (in millimeters)")
        if marker_size_mm >= square_size_mm:
            raise ValueError("Marker size must be smaller than square size")

        # Get dictionary
        aruco_dict = self._get_aruco_dictionary(dictionary)

        # Create ChArUco board
        board = cv2.aruco.CharucoBoard(
            (squares_x, squares_y), square_size_mm, marker_size_mm, aruco_dict
        )

        # Calculate board size in mm
        board_width_mm = squares_x * square_size_mm
        board_height_mm = squares_y * square_size_mm

        # Generate board image at high resolution (10 pixels per mm)
        pixels_per_mm = self.pixels_per_mm
        board_width_px = int(board_width_mm * pixels_per_mm)
        board_height_px = int(board_height_mm * pixels_per_mm)

        board_image = board.generateImage((board_width_px, board_height_px))

        # Add white border for printing
        border_px = int(self.border_mm * pixels_per_mm)
        bordered_image = cv2.copyMakeBorder(
            board_image,
            border_px,
            border_px,
            border_px,
            border_px,
            cv2.BORDER_CONSTANT,
            value=(255,),
        )

        marker_ids, total_markers, corner_positions = self._extract_charuco_metadata(
            board, squares_x, squares_y, square_size_mm
        )

        # Generate calibration metadata
        calibration_data = {
            "pattern_type": "charuco",
            "schema_version": CALIBRATION_SCHEMA_VERSION,
            "api_version": app_version,
            "board_size": [squares_x, squares_y],
            "square_size_mm": square_size_mm,
            "marker_size_mm": marker_size_mm,
            "dictionary": dictionary,
            "paper_size": paper_size,
            "physical_width_mm": board_width_mm,
            "physical_height_mm": board_height_mm,
            "total_markers": total_markers,
            "corner_positions": corner_positions,
            "marker_ids": marker_ids,
            "generation_date": datetime.now().isoformat(),
            "pixels_per_mm": pixels_per_mm,
            "border_mm": self.border_mm,
            "checksum": self._checksum_image(bordered_image),
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

        if markers_x < 1 or markers_y < 1:
            raise ValueError("Markers X and Y must be at least 1")
        if marker_size_mm <= 0:
            raise ValueError("Marker size must be positive (in millimeters)")
        if separation_mm < 0:
            raise ValueError("Separation must be non-negative (in millimeters)")
        if first_marker_id < 0:
            raise ValueError("First marker ID must be non-negative")

        # Get dictionary
        aruco_dict = self._get_aruco_dictionary(dictionary)

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
        pixels_per_mm = self.pixels_per_mm
        board_width_px = int(board_width_mm * pixels_per_mm)
        board_height_px = int(board_height_mm * pixels_per_mm)

        board_image = board.generateImage((board_width_px, board_height_px))

        # Add white border
        border_px = int(self.border_mm * pixels_per_mm)
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
            "schema_version": CALIBRATION_SCHEMA_VERSION,
            "api_version": app_version,
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
            "pixels_per_mm": pixels_per_mm,
            "border_mm": self.border_mm,
            "checksum": self._checksum_image(bordered_image),
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

        if tag_id < 0:
            raise ValueError("Tag ID must be non-negative")
        if tag_size_mm <= 0:
            raise ValueError("Tag size must be positive (in millimeters)")
        if border_bits < 0:
            raise ValueError("Border bits must be non-negative")

        # Get AprilTag dictionary
        apriltag_dict = self._get_apriltag_dictionary(tag_family)

        # Generate tag image
        pixels_per_mm = self.pixels_per_mm
        tag_size_px = int(tag_size_mm * pixels_per_mm)

        tag_image = cv2.aruco.generateImageMarker(apriltag_dict, tag_id, tag_size_px)

        # Add white border for printing
        border_px = int(self.border_mm * pixels_per_mm)
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
            "schema_version": CALIBRATION_SCHEMA_VERSION,
            "api_version": app_version,
            "tag_family": tag_family,
            "tag_id": tag_id,
            "tag_size_mm": tag_size_mm,
            "physical_width_mm": tag_size_mm,
            "physical_height_mm": tag_size_mm,
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
            "pixels_per_mm": pixels_per_mm,
            "border_mm": self.border_mm,
            "checksum": self._checksum_image(bordered_image),
        }

        return {
            "image": bordered_image,
            "calibration_data": metadata,
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

        if grid_x < 1 or grid_y < 1:
            raise ValueError("Grid X and Y must be at least 1")
        if tag_size_mm <= 0:
            raise ValueError("Tag size must be positive (in millimeters)")
        if spacing_mm < 0:
            raise ValueError("Spacing must be non-negative (in millimeters)")
        if first_tag_id < 0:
            raise ValueError("First tag ID must be non-negative")

        # Calculate grid dimensions
        grid_width_mm = grid_x * tag_size_mm + (grid_x - 1) * spacing_mm
        grid_height_mm = grid_y * tag_size_mm + (grid_y - 1) * spacing_mm

        # Create blank canvas
        pixels_per_mm = self.pixels_per_mm
        border_mm = self.border_mm
        canvas_width = int((grid_width_mm + 2 * border_mm) * pixels_per_mm)
        canvas_height = int((grid_height_mm + 2 * border_mm) * pixels_per_mm)
        canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255

        # Get AprilTag dictionary
        apriltag_dict = self._get_apriltag_dictionary(tag_family)

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
                x_px = int((x_mm + border_mm) * pixels_per_mm)
                y_px = int((y_mm + border_mm) * pixels_per_mm)

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
            "schema_version": CALIBRATION_SCHEMA_VERSION,
            "api_version": app_version,
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
            "pixels_per_mm": pixels_per_mm,
            "border_mm": self.border_mm,
            "checksum": self._checksum_image(canvas),
        }

        return {
            "image": canvas,
            "calibration_data": metadata,
            "dimensions_mm": (grid_width_mm, grid_height_mm),
        }

    def calibrate_camera(
        self,
        images: List[np.ndarray],
        pattern_size: Tuple[int, int],
        square_size_mm: float = 25.0,
    ) -> Dict[str, Any]:
        """
        Calibrate camera using a set of checkerboard images.

        Args:
            images: List of images containing the checkerboard pattern
            pattern_size: Tuple of (rows, cols) of inner corners (e.g., (9, 6))
            square_size_mm: Size of one square side in mm

        Returns:
            Dictionary containing calibration results (matrix, distortion, error)
        """
        if not OPENCV_AVAILABLE or cv2 is None:
            raise RuntimeError("OpenCV required for camera calibration")

        # Prepare object points (0,0,0), (1,0,0), (2,0,0) ...
        # pattern_size is (columns, rows) of internal corners
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0 : pattern_size[0], 0 : pattern_size[1]].T.reshape(
            -1, 2
        )
        objp = objp * square_size_mm

        # Arrays to store object points and image points from all the images
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane

        valid_images = 0
        image_size = None

        for img in images:
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            if image_size is None:
                image_size = gray.shape[::-1]
            elif gray.shape[::-1] != image_size:
                continue  # Skip images with inconsistent sizes

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

            if ret:
                objpoints.append(objp)
                # Refine corner locations
                corners2 = cv2.cornerSubPix(
                    gray,
                    corners,
                    (11, 11),
                    (-1, -1),
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                )
                imgpoints.append(corners2)
                valid_images += 1

        if valid_images < 3:
            return {
                "calibrated": False,
                "error": "Insufficient valid frames for calibration (minimum 3 required)",
            }

        # Perform calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None
        )

        # Calculate re-projection error
        mean_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(
                objpoints[i], rvecs[i], tvecs[i], mtx, dist
            )
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        total_error = mean_error / len(objpoints)

        return {
            "calibrated": True,
            "camera_matrix": mtx.tolist(),
            "distortion_coefficients": dist.tolist(),
            "rms_error": ret,
            "reprojection_error": total_error,
            "images_used": valid_images,
            "image_size": image_size,
        }

    def export_calibration_yaml(
        self, calibration_data: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Export calibration data as YAML (OpenCV format)."""
        yaml_data = {
            "schema_version": calibration_data.get(
                "schema_version", CALIBRATION_SCHEMA_VERSION
            ),
            "api_version": calibration_data.get("api_version", app_version),
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
        elif calibration_data["pattern_type"] == "apriltag":
            yaml_data["apriltag"] = {
                "tag_family": calibration_data.get("tag_family"),
                "tag_id": calibration_data.get("tag_id"),
                "tag_size_mm": calibration_data.get("tag_size_mm"),
                "border_bits": calibration_data.get("border_bits", 1),
            }
        elif calibration_data["pattern_type"] == "apriltag_grid":
            grid_size = calibration_data.get("grid_size", [0, 0])
            yaml_data["apriltag_grid"] = {
                "grid_x": grid_size[0],
                "grid_y": grid_size[1],
                "tag_family": calibration_data.get("tag_family"),
                "tag_size_mm": calibration_data.get("tag_size_mm"),
                "spacing_mm": calibration_data.get("spacing_mm"),
                "first_tag_id": calibration_data.get("first_tag_id", 0),
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

    def _extract_charuco_metadata(
        self, board, squares_x: int, squares_y: int, square_size: float
    ) -> Tuple[List[int], int, List[List[float]]]:
        """Extract marker IDs and corner positions from a ChArUco board."""
        marker_ids = None
        if hasattr(board, "getIds"):
            marker_ids = board.getIds()
        elif hasattr(board, "ids"):
            marker_ids = board.ids

        if marker_ids is None:
            total_markers = (squares_x * squares_y + 1) // 2
            marker_id_list = list(range(total_markers))
        else:
            marker_id_list = [int(x) for x in np.array(marker_ids).flatten().tolist()]
            total_markers = len(marker_id_list)

        corners = None
        if hasattr(board, "getChessboardCorners"):
            corners = board.getChessboardCorners()
        elif hasattr(board, "chessboardCorners"):
            corners = board.chessboardCorners

        if corners is None or len(corners) == 0:
            corner_positions = self._get_charuco_corners(
                squares_x, squares_y, square_size
            )
        else:
            corner_positions = [
                [float(c[0]), float(c[1]), float(c[2])] for c in np.array(corners)
            ]

        return marker_id_list, total_markers, corner_positions

    def _get_charuco_corners(
        self, squares_x: int, squares_y: int, square_size: float
    ) -> List[List[float]]:
        """Calculate 3D positions of ChArUco board corners."""
        corners = []
        for y in range(squares_y - 1):
            for x in range(squares_x - 1):
                corners.append([x * square_size, y * square_size, 0])
        return corners
