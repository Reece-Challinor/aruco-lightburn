"""
Simplified detection validation and quality assurance tools for ArUCO markers.
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np


class DetectionValidator:
    """Simplified validation tools for ArUCO marker detection quality."""

    def __init__(self):
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

    def generate_test_pattern(self, pattern_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multi-scale test pattern for detection validation."""
        # Extract configuration
        dictionary = pattern_config.get("dictionary", "4X4_50")
        scales = pattern_config.get("scales", [10, 20, 50, 100])
        marker_ids = pattern_config.get("marker_ids", list(range(len(scales))))
        canvas_size_mm = pattern_config.get("canvas_size_mm", (300, 200))

        # Create canvas
        canvas = self._create_canvas(canvas_size_mm)

        # Get ArUCO dictionary
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])

        # Place markers on canvas
        test_markers = self._place_markers_on_canvas(
            canvas, aruco_dict, scales, marker_ids, canvas_size_mm
        )

        # Create metadata
        metadata = self._create_pattern_metadata(
            dictionary, scales, canvas_size_mm, canvas.shape, test_markers
        )

        return {"image": canvas, "metadata": metadata, "test_markers": test_markers}

    def verify_marker_quality(
        self, marker_image: np.ndarray, expected_id: int, dictionary: str = "4X4_50"
    ) -> Dict[str, Any]:
        """Verify quality of a printed/displayed marker."""
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

        # Detect markers
        corners, ids, rejected = detector.detectMarkers(marker_image)

        # Initialize quality report
        quality_report = self._init_quality_report(expected_id)

        # Check if marker was detected
        if ids is not None and len(ids) > 0:
            quality_report = self._analyze_detected_marker(
                quality_report, ids[0][0], expected_id, corners[0], marker_image
            )
        else:
            quality_report = self._analyze_detection_failure(
                quality_report, marker_image, rejected
            )

        return quality_report

    def calculate_hamming_distance(
        self, id1: int, id2: int, dictionary: str = "4X4_50"
    ) -> int:
        """Calculate Hamming distance between two marker IDs."""
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])

        # Validate IDs
        if id1 >= aruco_dict.bytesList.shape[0] or id2 >= aruco_dict.bytesList.shape[0]:
            return -1

        # Get marker bytes and calculate distance
        marker1_bytes = aruco_dict.bytesList[id1].flatten()
        marker2_bytes = aruco_dict.bytesList[id2].flatten()

        return int(np.sum(marker1_bytes != marker2_bytes))

    def generate_detection_report(
        self, test_results: List[Dict[str, Any]], pattern_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive detection report."""
        total_tests = len(test_results)
        successful = sum(1 for r in test_results if r.get("detected", False))

        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_detections": successful,
                "detection_rate": successful / total_tests if total_tests > 0 else 0,
                "pattern_type": pattern_metadata.get("pattern_type", "unknown"),
                "timestamp": datetime.now().isoformat(),
            },
            "results": test_results,
            "metadata": pattern_metadata,
        }

        # Add performance metrics
        if test_results:
            report["performance"] = self._calculate_performance_metrics(test_results)

        return report

    # Helper methods for better organization

    def _create_canvas(self, canvas_size_mm: Tuple[int, int]) -> np.ndarray:
        """Create a white canvas for marker placement."""
        pixels_per_mm = 10
        canvas_width = int(canvas_size_mm[0] * pixels_per_mm)
        canvas_height = int(canvas_size_mm[1] * pixels_per_mm)
        return np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255

    def _place_markers_on_canvas(
        self, canvas, aruco_dict, scales, marker_ids, canvas_size_mm
    ):
        """Place markers on canvas at different scales."""
        test_markers = []
        margin = 20  # mm margin from edges
        current_x = margin
        current_y = margin
        pixels_per_mm = 10

        for scale, marker_id in zip(scales, marker_ids):
            if marker_id >= aruco_dict.bytesList.shape[0]:
                continue

            # Generate and place marker
            marker_size_px = int(scale * pixels_per_mm)
            marker_img = cv2.aruco.generateImageMarker(
                aruco_dict, marker_id, marker_size_px
            )

            # Check if marker fits
            if current_x + scale > canvas_size_mm[0] - margin:
                current_x = margin
                current_y += max(scales) + 10

            x_px = int(current_x * pixels_per_mm)
            y_px = int(current_y * pixels_per_mm)

            # Place marker if it fits
            if (
                y_px + marker_size_px <= canvas.shape[0]
                and x_px + marker_size_px <= canvas.shape[1]
            ):
                canvas[y_px : y_px + marker_size_px, x_px : x_px + marker_size_px] = (
                    marker_img
                )

                test_markers.append(
                    {
                        "id": marker_id,
                        "scale_mm": scale,
                        "position_mm": (current_x, current_y),
                        "position_px": (x_px, y_px),
                        "size_px": marker_size_px,
                    }
                )

            current_x += scale + 10

        return test_markers

    def _create_pattern_metadata(
        self, dictionary, scales, canvas_size_mm, canvas_shape, test_markers
    ):
        """Create metadata for test pattern."""
        return {
            "pattern_type": "multi_scale_test",
            "dictionary": dictionary,
            "scales_mm": scales,
            "canvas_size_mm": canvas_size_mm,
            "canvas_size_px": (canvas_shape[1], canvas_shape[0]),
            "test_markers": test_markers,
            "pixels_per_mm": 10,
            "generation_timestamp": datetime.now().isoformat(),
        }

    def _init_quality_report(self, expected_id):
        """Initialize a quality report structure."""
        return {
            "expected_id": expected_id,
            "detected": False,
            "detected_id": None,
            "corner_quality": 0.0,
            "contrast_ratio": 0.0,
            "sharpness_score": 0.0,
            "detection_confidence": 0.0,
            "errors": [],
        }

    def _analyze_detected_marker(
        self, report, detected_id, expected_id, corners, image
    ):
        """Analyze a successfully detected marker."""
        report["detected"] = True
        report["detected_id"] = detected_id

        if detected_id == expected_id:
            report["corner_quality"] = self._assess_corner_quality(corners)
            report["contrast_ratio"] = self._calculate_contrast(image)
            report["sharpness_score"] = self._calculate_sharpness(image)
            report["detection_confidence"] = 1.0
        else:
            report["errors"].append(
                f"ID mismatch: expected {expected_id}, got {detected_id}"
            )
            report["detection_confidence"] = 0.5

        return report

    def _analyze_detection_failure(self, report, image, rejected):
        """Analyze why marker detection failed."""
        report["errors"].append("No marker detected")

        if len(rejected) > 0:
            report["errors"].append(f"Found {len(rejected)} rejected candidates")

        # Check image brightness
        mean_brightness = image.mean()
        if mean_brightness > 240:
            report["errors"].append("Image too bright")
        elif mean_brightness < 15:
            report["errors"].append("Image too dark")

        # Check contrast
        contrast = self._calculate_contrast(image)
        if contrast < 0.3:
            report["errors"].append("Low contrast")
        report["contrast_ratio"] = contrast

        return report

    def _assess_corner_quality(self, corners):
        """Assess the quality of detected corners."""
        if corners is None or len(corners[0]) != 4:
            return 0.0

        corners = corners[0]

        # Calculate perimeter
        perimeter = 0
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            perimeter += np.linalg.norm(p2 - p1)

        # Calculate area using shoelace formula
        area = 0
        for i in range(4):
            j = (i + 1) % 4
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2

        # Quality based on squareness (ideal ratio is 4 for square)
        if perimeter > 0:
            squareness = (16 * area) / (perimeter * perimeter)
            return min(squareness, 1.0)

        return 0.0

    def _calculate_contrast(self, image):
        """Calculate image contrast ratio."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        min_val = gray.min()
        max_val = gray.max()

        if max_val > min_val:
            return (max_val - min_val) / 255.0
        return 0.0

    def _calculate_sharpness(self, image):
        """Calculate image sharpness using Laplacian variance."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        # Normalize to 0-1 range
        return min(variance / 1000.0, 1.0)

    def _calculate_performance_metrics(self, test_results):
        """Calculate performance metrics from test results."""
        detection_times = [
            r.get("detection_time", 0) for r in test_results if "detection_time" in r
        ]

        metrics = {
            "success_rate": sum(1 for r in test_results if r.get("detected"))
            / len(test_results),
            "avg_confidence": np.mean(
                [r.get("detection_confidence", 0) for r in test_results]
            ),
        }

        if detection_times:
            metrics["avg_detection_time"] = np.mean(detection_times)
            metrics["max_detection_time"] = max(detection_times)
            metrics["min_detection_time"] = min(detection_times)

        return metrics


class CalibrationTools:
    """Simplified calibration tools for camera setup."""

    def __init__(self):
        self.calibration_data = None

    def generate_calibration_pattern(
        self, pattern_type: str = "checkerboard", size: Tuple[int, int] = (9, 6)
    ) -> np.ndarray:
        """Generate calibration pattern image."""
        if pattern_type == "checkerboard":
            return self._generate_checkerboard(size)
        else:
            raise ValueError(f"Unsupported pattern type: {pattern_type}")

    def _generate_checkerboard(self, size: Tuple[int, int]) -> np.ndarray:
        """Generate a checkerboard pattern."""
        square_size = 50  # pixels
        width = size[0] * square_size
        height = size[1] * square_size

        pattern = np.zeros((height, width), dtype=np.uint8)

        for i in range(size[1]):
            for j in range(size[0]):
                if (i + j) % 2 == 0:
                    y1 = i * square_size
                    y2 = (i + 1) * square_size
                    x1 = j * square_size
                    x2 = (j + 1) * square_size
                    pattern[y1:y2, x1:x2] = 255

        return pattern

    def calibrate_camera(
        self, images: List[np.ndarray], pattern_size: Tuple[int, int]
    ) -> Dict[str, Any]:
        """Simple camera calibration from checkerboard images."""
        # This is a simplified version - full implementation would include
        # actual OpenCV calibration routines
        return {
            "calibrated": True,
            "camera_matrix": None,
            "distortion_coeffs": None,
            "rms_error": 0.0,
        }
