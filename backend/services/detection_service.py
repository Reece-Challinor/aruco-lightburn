"""
Detection service for ArUCO markers
"""
import logging
import cv2
import numpy as np
from typing import List, Dict, Optional, Any
import uuid
import base64

logger = logging.getLogger(__name__)

class DetectionService:
    """Service for ArUCO marker detection"""
    
    def __init__(self):
        self.active_sessions = {}
        self.aruco_dicts = {
            'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
            'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
            'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
            'DICT_4X4_1000': cv2.aruco.DICT_4X4_1000,
            'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
            'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
            'DICT_5X5_250': cv2.aruco.DICT_5X5_250,
            'DICT_5X5_1000': cv2.aruco.DICT_5X5_1000,
            'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
            'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
            'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
            'DICT_6X6_1000': cv2.aruco.DICT_6X6_1000,
            'DICT_7X7_50': cv2.aruco.DICT_7X7_50,
            'DICT_7X7_100': cv2.aruco.DICT_7X7_100,
            'DICT_7X7_250': cv2.aruco.DICT_7X7_250,
            'DICT_7X7_1000': cv2.aruco.DICT_7X7_1000,
        }
    
    def detect_markers(self, image: np.ndarray, dictionary: str = 'DICT_4X4_50') -> List[Dict]:
        """Detect ArUCO markers in an image"""
        try:
            # Get ArUCO dictionary
            if dictionary not in self.aruco_dicts:
                raise ValueError(f"Invalid dictionary: {dictionary}")
            
            aruco_dict = cv2.aruco.Dictionary_get(self.aruco_dicts[dictionary])
            aruco_params = cv2.aruco.DetectorParameters_create()
            
            # Detect markers
            corners, ids, rejected = cv2.aruco.detectMarkers(
                image, aruco_dict, parameters=aruco_params
            )
            
            detections = []
            if ids is not None:
                for i, marker_id in enumerate(ids.flatten()):
                    # Get corner coordinates
                    corner_points = corners[i][0]
                    
                    # Calculate center
                    center_x = np.mean(corner_points[:, 0])
                    center_y = np.mean(corner_points[:, 1])
                    
                    # Calculate area
                    area = cv2.contourArea(corner_points)
                    
                    # Calculate perimeter
                    perimeter = cv2.arcLength(corner_points, True)
                    
                    detections.append({
                        'id': int(marker_id),
                        'corners': corner_points.tolist(),
                        'center': [float(center_x), float(center_y)],
                        'area': float(area),
                        'perimeter': float(perimeter),
                        'dictionary': dictionary
                    })
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            raise
    
    def start_stream_session(self, config: Dict) -> str:
        """Start a real-time detection stream session"""
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            'config': config,
            'status': 'active',
            'frame_count': 0,
            'detections': []
        }
        
        return session_id
    
    def stop_stream_session(self, session_id: str) -> None:
        """Stop a stream session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['status'] = 'stopped'
            # Clean up after a delay
            # In production, this would be handled by a background task
    
    def analyze_detection_quality(self, image_data: str, detections: List[Dict]) -> Dict:
        """Analyze detection quality"""
        try:
            # Decode image
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            analysis = {
                'image_quality': self._analyze_image_quality(gray),
                'detection_quality': self._analyze_detections(detections),
                'lighting': self._analyze_lighting(gray),
                'focus': self._analyze_focus(gray),
                'noise': self._analyze_noise(gray)
            }
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(analysis)
            analysis['overall_score'] = quality_score
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise
    
    def get_recommendations(self, analysis: Dict) -> List[str]:
        """Get recommendations based on analysis"""
        recommendations = []
        
        if analysis.get('overall_score', 0) < 0.5:
            recommendations.append("Overall detection quality is low")
        
        if analysis.get('image_quality', {}).get('brightness', 0) < 50:
            recommendations.append("Increase lighting - image is too dark")
        elif analysis.get('image_quality', {}).get('brightness', 0) > 200:
            recommendations.append("Reduce lighting - image is too bright")
        
        if analysis.get('focus', {}).get('score', 0) < 0.5:
            recommendations.append("Improve camera focus for better detection")
        
        if analysis.get('noise', {}).get('level', 0) > 0.3:
            recommendations.append("Reduce image noise - consider better lighting or camera")
        
        if not analysis.get('detection_quality', {}).get('markers_found', False):
            recommendations.append("No markers detected - check marker visibility and dictionary")
        
        return recommendations
    
    def calibrate_detection(self, config: Dict) -> Dict:
        """Calibrate detection parameters"""
        calibration = {
            'adaptiveThresholdWinSizeMin': config.get('winSizeMin', 3),
            'adaptiveThresholdWinSizeMax': config.get('winSizeMax', 23),
            'adaptiveThresholdWinSizeStep': config.get('winSizeStep', 10),
            'adaptiveThresholdConstant': config.get('constant', 7),
            'minMarkerPerimeterRate': config.get('minPerimeterRate', 0.03),
            'maxMarkerPerimeterRate': config.get('maxPerimeterRate', 4.0),
            'polygonalApproxAccuracyRate': config.get('approxAccuracy', 0.03),
            'minCornerDistanceRate': config.get('minCornerDistance', 0.05),
            'minDistanceToBorder': config.get('minBorderDistance', 3),
            'minMarkerDistanceRate': config.get('minMarkerDistance', 0.05),
            'cornerRefinementMethod': config.get('cornerRefinement', 'CORNER_REFINE_SUBPIX'),
            'cornerRefinementWinSize': config.get('refinementWinSize', 5),
            'cornerRefinementMaxIterations': config.get('refinementIterations', 30),
            'cornerRefinementMinAccuracy': config.get('refinementAccuracy', 0.1),
            'markerBorderBits': config.get('borderBits', 1)
        }
        
        return calibration
    
    def _analyze_image_quality(self, gray_image: np.ndarray) -> Dict:
        """Analyze basic image quality metrics"""
        return {
            'brightness': float(np.mean(gray_image)),
            'contrast': float(np.std(gray_image)),
            'histogram_spread': float(np.ptp(gray_image))
        }
    
    def _analyze_detections(self, detections: List[Dict]) -> Dict:
        """Analyze detection results"""
        if not detections:
            return {
                'markers_found': False,
                'count': 0
            }
        
        areas = [d['area'] for d in detections]
        perimeters = [d['perimeter'] for d in detections]
        
        return {
            'markers_found': True,
            'count': len(detections),
            'avg_area': float(np.mean(areas)),
            'area_variance': float(np.var(areas)),
            'avg_perimeter': float(np.mean(perimeters)),
            'perimeter_variance': float(np.var(perimeters))
        }
    
    def _analyze_lighting(self, gray_image: np.ndarray) -> Dict:
        """Analyze lighting conditions"""
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        
        # Check for over/under exposure
        underexposed = np.sum(hist[:50])
        overexposed = np.sum(hist[206:])
        
        return {
            'underexposed_ratio': float(underexposed),
            'overexposed_ratio': float(overexposed),
            'balanced': bool(underexposed < 0.3 and overexposed < 0.3)
        }
    
    def _analyze_focus(self, gray_image: np.ndarray) -> Dict:
        """Analyze image focus using Laplacian variance"""
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalized focus score (higher is better)
        focus_score = min(1.0, variance / 1000.0)
        
        return {
            'variance': float(variance),
            'score': float(focus_score),
            'is_sharp': bool(focus_score > 0.5)
        }
    
    def _analyze_noise(self, gray_image: np.ndarray) -> Dict:
        """Analyze image noise"""
        # Apply Gaussian blur and calculate difference
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
        noise = cv2.absdiff(gray_image, blurred)
        noise_level = np.mean(noise) / 255.0
        
        return {
            'level': float(noise_level),
            'is_noisy': bool(noise_level > 0.1)
        }
    
    def _calculate_quality_score(self, analysis: Dict) -> float:
        """Calculate overall quality score from analysis"""
        score = 0.0
        weights = {
            'image_quality': 0.2,
            'detection_quality': 0.3,
            'lighting': 0.2,
            'focus': 0.2,
            'noise': 0.1
        }
        
        # Image quality contribution
        if 'image_quality' in analysis:
            brightness = analysis['image_quality'].get('brightness', 0)
            if 50 <= brightness <= 200:
                score += weights['image_quality']
        
        # Detection quality contribution
        if analysis.get('detection_quality', {}).get('markers_found', False):
            score += weights['detection_quality']
        
        # Lighting contribution
        if analysis.get('lighting', {}).get('balanced', False):
            score += weights['lighting']
        
        # Focus contribution
        if analysis.get('focus', {}).get('is_sharp', False):
            score += weights['focus']
        
        # Noise contribution
        if not analysis.get('noise', {}).get('is_noisy', True):
            score += weights['noise']
        
        return score