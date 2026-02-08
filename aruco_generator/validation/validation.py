"""
Simplified detection validation and quality assurance tools for ArUCO markers.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>validation.py</name>
    <version>2.2.0</version>
    <type>validation_module</type>
    <purpose>Detection validation helpers, quality scoring, and marker analysis utilities</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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
            "7X7_50": cv2.aruco.DICT_7X7_50,
            "7X7_100": cv2.aruco.DICT_7X7_100,
            "7X7_250": cv2.aruco.DICT_7X7_250,
            "7X7_1000": cv2.aruco.DICT_7X7_1000,
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
        if marker_image is None:
            raise ValueError("Marker image is required")
        if marker_image.ndim == 3:
            marker_image = cv2.cvtColor(marker_image, cv2.COLOR_BGR2GRAY)
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

    def detect_markers(
        self,
        image: np.ndarray,
        dictionary: str = "4X4_50",
        expected_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Detect ArUCO markers in an image and return detection metrics."""
        if image is None:
            raise ValueError("Image data is required for detection")
        if dictionary not in self.aruco_dicts:
            available = ", ".join(sorted(self.aruco_dicts.keys()))
            raise ValueError(
                f'Unknown ArUCO dictionary "{dictionary}". Available: {available}'
            )

        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

        start_time = time.monotonic()
        corners, ids, rejected = detector.detectMarkers(image)
        detection_time_ms = (time.monotonic() - start_time) * 1000.0

        image_area = float(image.shape[0] * image.shape[1])
        markers = []
        if ids is not None and len(ids) > 0:
            for marker_id, marker_corners in zip(ids.flatten(), corners):
                contour = marker_corners.reshape(4, 2)
                area = float(cv2.contourArea(contour))
                perimeter = float(cv2.arcLength(contour, True))
                confidence = self._estimate_confidence(area, image_area)

                markers.append(
                    {
                        "id": int(marker_id),
                        "confidence": round(confidence * 100, 1),
                        "area_px": round(area, 2),
                        "perimeter_px": round(perimeter, 2),
                        "corners": contour.tolist(),
                    }
                )

        detected_count = len(markers)
        detection_rate = detected_count / expected_count if expected_count else None
        avg_confidence = (
            sum(m["confidence"] for m in markers) / detected_count / 100.0
            if detected_count
            else 0.0
        )
        detection_quality = (
            round(detection_rate * 100, 1)
            if detection_rate is not None
            else round(avg_confidence * 100, 1)
        )

        return {
            "dictionary": dictionary,
            "image_size": {"width": image.shape[1], "height": image.shape[0]},
            "detected_markers": detected_count,
            "expected_markers": expected_count,
            "detection_rate": detection_rate,
            "detection_quality": detection_quality,
            "avg_confidence": round(avg_confidence * 100, 1) if detected_count else 0.0,
            "rejected_candidates": len(rejected) if rejected is not None else 0,
            "detection_time_ms": round(detection_time_ms, 2),
            "markers": markers,
        }

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
        report["detected_id"] = int(detected_id)

        # Basic metrics
        report["corner_quality"] = self._assess_corner_quality(corners)
        report["contrast_ratio"] = self._calculate_contrast(image)
        report["sharpness_score"] = self._calculate_sharpness(image)

        # Advanced checks
        report["quiet_zone_score"] = self._check_quiet_zone(image, corners)

        if detected_id == expected_id:
            report["bit_errors"] = 0
            report["detection_confidence"] = 1.0
        else:
            # Calculate bit errors if ID doesn't match
            # This requires recreating the bit matrix from the image
            report["bit_errors"] = self._count_bit_errors(image, corners, expected_id)
            report["errors"].append(
                f"ID mismatch: expected {expected_id}, got {detected_id} ({report['bit_errors']} bit errors)"
            )
            report["detection_confidence"] = max(
                0.0, 1.0 - (report["bit_errors"] * 0.1)
            )

        return report

    @staticmethod
    def _estimate_confidence(area_px: float, image_area: float) -> float:
        """Estimate confidence from marker area relative to image size."""
        if image_area <= 0 or area_px <= 0:
            return 0.0
        area_ratio = area_px / image_area
        score = 0.3 + 0.7 * min(1.0, (area_ratio**0.5) * 5.0)
        return max(0.0, min(1.0, score))

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

    def _check_quiet_zone(self, image, corners):
        """Check the integrity of the quiet zone (black border)."""
        # Warp perspective to get a square view of the marker including border
        size = 100
        margin = 20  # Include some margin around the marker

        # Define destination points
        dst_pts = np.float32(
            [
                [margin, margin],
                [size - margin, margin],
                [size - margin, size - margin],
                [margin, size - margin],
            ]
        )

        # Get transform matrix
        M = cv2.getPerspectiveTransform(corners, dst_pts)
        warped = cv2.warpPerspective(image, M, (size, size))

        if len(warped.shape) == 3:
            gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        else:
            gray = warped

        # Refine margins
        # The marker is now centered in 'gray' from 20 to 80.
        # The border is roughly from 15 to 25, 75 to 85, etc.
        # But simpler: sample the area that should be the black border.
        # In a standard ArUco, the black border is the outer ring of the grid.
        # Use simple thresholding check on the border region.

        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Sample border pixels (approximate)
        # Check a 1-pixel wide line around the marker content
        # If marker is 4x4, it has 6x6 grid. Border is the outer ring.

        border_mask = np.zeros_like(thresh)
        cv2.rectangle(
            border_mask, (margin, margin), (size - margin, size - margin), 255, 1
        )

        border_pixels = thresh[border_mask == 255]
        non_black_pixels = np.count_nonzero(border_pixels)
        total_pixels = len(border_pixels)

        if total_pixels == 0:
            return 0.0

        score = 1.0 - (non_black_pixels / total_pixels)
        return score

    def _count_bit_errors(self, image, corners, expected_id, dict_name="4X4_50"):
        """Estimate number of incorrect bits."""
        # This is a complex operation requiring precise grid sampling.
        # Simplified version returning Hamming distance between IDs if possible.
        try:
            return self.calculate_hamming_distance(
                int(expected_id),
                int(self._get_detected_id_from_image(image, corners)),
                dict_name,
            )
        except Exception:
            return -1

    def _get_detected_id_from_image(self, image, corners):
        """Helper to re-detect ID from image patches if needed."""
        # Placeholder - relying on ArucoDetector's result usually sufficient
        return 0

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
