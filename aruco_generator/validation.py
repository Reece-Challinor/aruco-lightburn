"""
Detection validation and quality assurance tools for ArUCO markers.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import hashlib
import json

class DetectionValidator:
    """Validation tools for ArUCO marker detection quality and performance."""
    
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
        """Generate multi-scale test pattern for detection validation.
        
        Args:
            pattern_config: Configuration containing:
                - dictionary: ArUCO dictionary name
                - scales: List of marker sizes in mm [10, 20, 50, 100]
                - marker_ids: List of marker IDs to test
                - canvas_size_mm: (width, height) of test pattern
                - include_distortions: Add simulated distortions
                - include_occlusions: Add partial occlusions
        
        Returns:
            Dictionary containing test pattern image and metadata
        """
        dictionary = pattern_config.get('dictionary', '4X4_50')
        scales = pattern_config.get('scales', [10, 20, 50, 100])
        marker_ids = pattern_config.get('marker_ids', list(range(len(scales))))
        canvas_size_mm = pattern_config.get('canvas_size_mm', (300, 200))
        include_distortions = pattern_config.get('include_distortions', False)
        include_occlusions = pattern_config.get('include_occlusions', False)
        
        # Create canvas (10 pixels per mm)
        pixels_per_mm = 10
        canvas_width = int(canvas_size_mm[0] * pixels_per_mm)
        canvas_height = int(canvas_size_mm[1] * pixels_per_mm)
        canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255
        
        # Get ArUCO dictionary
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])
        
        # Place markers at different scales
        test_markers = []
        margin = 20  # mm margin from edges
        current_x = margin
        current_y = margin
        
        for i, (scale, marker_id) in enumerate(zip(scales, marker_ids)):
            if marker_id >= aruco_dict.bytesList.shape[0]:
                continue
                
            # Generate marker
            marker_size_px = int(scale * pixels_per_mm)
            marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
            
            # Apply distortions if requested
            if include_distortions:
                marker_img = self._apply_distortions(marker_img, i)
            
            # Find position for marker
            if current_x + scale > canvas_size_mm[0] - margin:
                current_x = margin
                current_y += max(scales[:i+1]) + 10  # Move to next row
            
            x_px = int(current_x * pixels_per_mm)
            y_px = int(current_y * pixels_per_mm)
            
            # Place marker on canvas
            if (y_px + marker_size_px <= canvas_height and 
                x_px + marker_size_px <= canvas_width):
                canvas[y_px:y_px+marker_size_px, x_px:x_px+marker_size_px] = marker_img
                
                # Add occlusion if requested
                if include_occlusions and i % 2 == 0:
                    self._add_occlusion(canvas, x_px, y_px, marker_size_px)
                
                test_markers.append({
                    'id': marker_id,
                    'scale_mm': scale,
                    'position_mm': (current_x, current_y),
                    'position_px': (x_px, y_px),
                    'size_px': marker_size_px,
                    'distorted': include_distortions,
                    'occluded': include_occlusions and i % 2 == 0
                })
            
            current_x += scale + 10  # Move to next position
        
        # Add test pattern metadata
        metadata = {
            'pattern_type': 'multi_scale_test',
            'dictionary': dictionary,
            'scales_mm': scales,
            'canvas_size_mm': canvas_size_mm,
            'canvas_size_px': (canvas_width, canvas_height),
            'test_markers': test_markers,
            'include_distortions': include_distortions,
            'include_occlusions': include_occlusions,
            'pixels_per_mm': pixels_per_mm,
            'generation_timestamp': datetime.now().isoformat()
        }
        
        # Add quality metrics
        metadata['quality_metrics'] = self._calculate_quality_metrics(canvas, test_markers)
        
        return {
            'image': canvas,
            'metadata': metadata,
            'test_markers': test_markers
        }
    
    def verify_marker_quality(self, marker_image: np.ndarray,
                            expected_id: int,
                            dictionary: str = '4X4_50') -> Dict[str, Any]:
        """Verify quality of a printed/displayed marker.
        
        Args:
            marker_image: Image containing the marker
            expected_id: Expected marker ID
            dictionary: ArUCO dictionary name
        
        Returns:
            Quality assessment report
        """
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        
        # Detect markers
        corners, ids, rejected = detector.detectMarkers(marker_image)
        
        quality_report = {
            'expected_id': expected_id,
            'detected': False,
            'detected_id': None,
            'corner_quality': 0.0,
            'contrast_ratio': 0.0,
            'sharpness_score': 0.0,
            'detection_confidence': 0.0,
            'errors': []
        }
        
        if ids is not None and len(ids) > 0:
            detected_id = ids[0][0]
            quality_report['detected'] = True
            quality_report['detected_id'] = detected_id
            
            if detected_id == expected_id:
                # Calculate quality metrics
                quality_report['corner_quality'] = self._assess_corner_quality(corners[0])
                quality_report['contrast_ratio'] = self._calculate_contrast(marker_image)
                quality_report['sharpness_score'] = self._calculate_sharpness(marker_image)
                quality_report['detection_confidence'] = 1.0
            else:
                quality_report['errors'].append(f"ID mismatch: expected {expected_id}, got {detected_id}")
                quality_report['detection_confidence'] = 0.5
        else:
            quality_report['errors'].append("No marker detected")
            
            # Try to analyze why detection failed
            if len(rejected) > 0:
                quality_report['errors'].append(f"Found {len(rejected)} rejected candidates")
            
            # Check image properties
            if marker_image.mean() > 240:
                quality_report['errors'].append("Image too bright")
            elif marker_image.mean() < 15:
                quality_report['errors'].append("Image too dark")
            
            contrast = self._calculate_contrast(marker_image)
            if contrast < 0.3:
                quality_report['errors'].append("Low contrast")
            quality_report['contrast_ratio'] = contrast
        
        return quality_report
    
    def calculate_hamming_distance(self, id1: int, id2: int, 
                                  dictionary: str = '4X4_50') -> int:
        """Calculate Hamming distance between two marker IDs.
        
        Args:
            id1: First marker ID
            id2: Second marker ID
            dictionary: ArUCO dictionary name
        
        Returns:
            Hamming distance between the two markers
        """
        aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dictionary])
        
        # Get marker bytes
        if id1 >= aruco_dict.bytesList.shape[0] or id2 >= aruco_dict.bytesList.shape[0]:
            return -1
        
        marker1_bytes = aruco_dict.bytesList[id1].flatten()
        marker2_bytes = aruco_dict.bytesList[id2].flatten()
        
        # Calculate Hamming distance
        hamming = np.sum(marker1_bytes != marker2_bytes)
        
        return int(hamming)
    
    def generate_detection_report(self, test_results: List[Dict[str, Any]],
                                 pattern_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive detection quality report.
        
        Args:
            test_results: List of test result dictionaries
            pattern_metadata: Metadata about the test pattern
        
        Returns:
            Comprehensive detection report
        """
        report = {
            'report_id': hashlib.md5(
                json.dumps(pattern_metadata, sort_keys=True).encode()
            ).hexdigest()[:8],
            'generation_timestamp': datetime.now().isoformat(),
            'pattern_metadata': pattern_metadata,
            'test_summary': {
                'total_tests': len(test_results),
                'successful_detections': 0,
                'failed_detections': 0,
                'average_detection_rate': 0.0,
                'average_pose_error': 0.0,
                'average_processing_time': 0.0
            },
            'detailed_results': [],
            'recommendations': []
        }
        
        # Analyze test results
        successful = 0
        total_pose_error = 0.0
        total_time = 0.0
        
        for result in test_results:
            if result.get('detected', False):
                successful += 1
                total_pose_error += result.get('pose_error_mm', 0.0)
            total_time += result.get('processing_time_ms', 0.0)
            
            report['detailed_results'].append({
                'marker_id': result.get('marker_id'),
                'detected': result.get('detected', False),
                'detection_confidence': result.get('confidence', 0.0),
                'pose_error_mm': result.get('pose_error_mm', None),
                'processing_time_ms': result.get('processing_time_ms', 0.0),
                'lighting_conditions': result.get('lighting_conditions', 'unknown'),
                'distance_m': result.get('distance_m', None)
            })
        
        # Update summary
        report['test_summary']['successful_detections'] = successful
        report['test_summary']['failed_detections'] = len(test_results) - successful
        report['test_summary']['average_detection_rate'] = (successful / len(test_results)) * 100 if test_results else 0
        report['test_summary']['average_pose_error'] = total_pose_error / successful if successful > 0 else 0
        report['test_summary']['average_processing_time'] = total_time / len(test_results) if test_results else 0
        
        # Generate recommendations
        detection_rate = report['test_summary']['average_detection_rate']
        
        if detection_rate < 50:
            report['recommendations'].append("Critical: Detection rate below 50%. Check marker quality and lighting.")
        elif detection_rate < 80:
            report['recommendations'].append("Warning: Detection rate below 80%. Consider improving contrast or marker size.")
        
        if report['test_summary']['average_pose_error'] > 5.0:
            report['recommendations'].append("High pose estimation error. Verify camera calibration.")
        
        if report['test_summary']['average_processing_time'] > 50:
            report['recommendations'].append("Processing time is high. Consider optimizing detection parameters.")
        
        # Add marker confusion analysis
        if 'dictionary' in pattern_metadata:
            confusion_analysis = self._analyze_marker_confusion(
                pattern_metadata.get('marker_ids', []),
                pattern_metadata['dictionary']
            )
            report['marker_confusion'] = confusion_analysis
            
            if confusion_analysis['min_hamming_distance'] < 3:
                report['recommendations'].append(
                    f"Warning: Minimum Hamming distance is {confusion_analysis['min_hamming_distance']}. "
                    "Consider using markers with greater separation."
                )
        
        return report
    
    def _apply_distortions(self, marker_img: np.ndarray, distortion_type: int) -> np.ndarray:
        """Apply simulated distortions to marker image."""
        if distortion_type % 3 == 0:
            # Add Gaussian blur
            marker_img = cv2.GaussianBlur(marker_img, (3, 3), 0.5)
        elif distortion_type % 3 == 1:
            # Add slight rotation
            center = (marker_img.shape[1] // 2, marker_img.shape[0] // 2)
            angle = 5.0 * (distortion_type % 2 * 2 - 1)  # ±5 degrees
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            marker_img = cv2.warpAffine(marker_img, M, marker_img.shape[:2][::-1],
                                       borderValue=255)
        else:
            # Add perspective distortion
            h, w = marker_img.shape[:2]
            pts1 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
            pts2 = np.float32([[5, 5], [w-5, 10], [w-10, h-5], [10, h-10]])
            M = cv2.getPerspectiveTransform(pts1, pts2)
            marker_img = cv2.warpPerspective(marker_img, M, (w, h), borderValue=255)
        
        return marker_img
    
    def _add_occlusion(self, canvas: np.ndarray, x: int, y: int, size: int):
        """Add partial occlusion to marker."""
        # Add a gray rectangle covering part of the marker
        occlusion_height = size // 3
        occlusion_y = y + size - occlusion_height
        canvas[occlusion_y:y+size, x:x+size] = 128
    
    def _calculate_quality_metrics(self, image: np.ndarray, 
                                  markers: List[Dict]) -> Dict[str, float]:
        """Calculate overall quality metrics for test pattern."""
        metrics = {
            'overall_contrast': self._calculate_contrast(image),
            'overall_sharpness': self._calculate_sharpness(image),
            'marker_density': len(markers) / (image.shape[0] * image.shape[1]) * 1000000,  # markers per megapixel
            'size_variation': np.std([m['scale_mm'] for m in markers]) if markers else 0
        }
        return metrics
    
    def _assess_corner_quality(self, corners: np.ndarray) -> float:
        """Assess quality of detected corners."""
        corners = corners[0]
        
        # Check if corners form a proper quadrilateral
        # Calculate angles between consecutive edges
        angles = []
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i+1)%4]
            p3 = corners[(i+2)%4]
            
            v1 = p2 - p1
            v2 = p3 - p2
            
            angle = np.arccos(np.dot(v1[0], v2[0]) / 
                            (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angles.append(np.degrees(angle))
        
        # Good corners should have angles close to 90 degrees
        angle_error = sum(abs(angle - 90) for angle in angles) / 4
        quality = max(0, 1.0 - angle_error / 45)  # Normalize to 0-1
        
        return quality
    
    def _calculate_contrast(self, image: np.ndarray) -> float:
        """Calculate contrast ratio of image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Use Weber contrast
        min_val = gray.min()
        max_val = gray.max()
        
        if max_val == min_val:
            return 0.0
        
        contrast = (max_val - min_val) / (max_val + min_val)
        return float(contrast)
    
    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """Calculate sharpness score using Laplacian variance."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Normalize to 0-1 range (empirically determined)
        normalized = min(1.0, sharpness / 1000.0)
        return float(normalized)
    
    def _analyze_marker_confusion(self, marker_ids: List[int], 
                                 dictionary: str) -> Dict[str, Any]:
        """Analyze potential confusion between markers."""
        confusion_matrix = {}
        min_distance = float('inf')
        max_distance = 0
        
        for i, id1 in enumerate(marker_ids):
            for id2 in marker_ids[i+1:]:
                distance = self.calculate_hamming_distance(id1, id2, dictionary)
                if distance >= 0:
                    confusion_matrix[f"{id1}-{id2}"] = distance
                    min_distance = min(min_distance, distance)
                    max_distance = max(max_distance, distance)
        
        return {
            'confusion_matrix': confusion_matrix,
            'min_hamming_distance': min_distance if min_distance != float('inf') else 0,
            'max_hamming_distance': max_distance,
            'average_hamming_distance': sum(confusion_matrix.values()) / len(confusion_matrix) if confusion_matrix else 0
        }