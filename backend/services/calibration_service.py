"""
Calibration service for camera calibration
"""
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class CalibrationService:
    """Service for camera calibration"""
    
    def __init__(self):
        self.calibrations = {}  # In-memory storage for calibrations
        self.patterns = {
            'chessboard': {
                'name': 'Chessboard',
                'description': 'Traditional chessboard pattern for calibration',
                'default_rows': 9,
                'default_cols': 6
            },
            'circles_grid': {
                'name': 'Circles Grid',
                'description': 'Grid of circles for calibration',
                'default_rows': 7,
                'default_cols': 5
            },
            'asymmetric_circles': {
                'name': 'Asymmetric Circles',
                'description': 'Asymmetric pattern of circles',
                'default_rows': 5,
                'default_cols': 4
            }
        }
    
    def get_available_patterns(self) -> Dict:
        """Get available calibration patterns"""
        return self.patterns
    
    def generate_pattern(self, pattern_type: str, rows: int, cols: int, 
                        square_size: float) -> Tuple[bytes, str]:
        """Generate calibration pattern"""
        try:
            # Create pattern image
            if pattern_type == 'chessboard':
                pattern_image = self._generate_chessboard(rows, cols, square_size)
            elif pattern_type == 'circles_grid':
                pattern_image = self._generate_circles_grid(rows, cols, square_size)
            elif pattern_type == 'asymmetric_circles':
                pattern_image = self._generate_asymmetric_circles(rows, cols, square_size)
            else:
                raise ValueError(f"Unknown pattern type: {pattern_type}")
            
            # Convert to bytes (would normally generate PDF)
            _, buffer = cv2.imencode('.png', pattern_image)
            pattern_data = buffer.tobytes()
            
            filename = f"calibration_{pattern_type}_{rows}x{cols}_{square_size}mm.png"
            
            return pattern_data, filename
            
        except Exception as e:
            logger.error(f"Pattern generation error: {e}")
            raise
    
    def calibrate_camera(self, images: List[str], config: Dict) -> Dict:
        """Calibrate camera from calibration images"""
        try:
            pattern_type = config.get('pattern_type', 'chessboard')
            pattern_size = (config.get('cols', 6), config.get('rows', 9))
            square_size = config.get('square_size', 30)
            
            # Prepare calibration
            obj_points = []  # 3D points in real world space
            img_points = []  # 2D points in image plane
            
            # Create object points
            objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
            objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
            objp *= square_size
            
            image_size = None
            
            for image_data in images:
                # Decode base64 image
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                if image_size is None:
                    image_size = gray.shape[::-1]
                
                # Find pattern corners
                if pattern_type == 'chessboard':
                    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
                else:
                    # For other patterns, would use different detection methods
                    ret = False
                    corners = None
                
                if ret:
                    # Refine corners
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    
                    obj_points.append(objp)
                    img_points.append(corners)
            
            if len(obj_points) < 3:
                raise ValueError("Not enough valid calibration images")
            
            # Calibrate camera
            ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
                obj_points, img_points, image_size, None, None
            )
            
            # Calculate reprojection error
            total_error = 0
            for i in range(len(obj_points)):
                img_points2, _ = cv2.projectPoints(
                    obj_points[i], rvecs[i], tvecs[i], 
                    camera_matrix, dist_coeffs
                )
                error = cv2.norm(img_points[i], img_points2, cv2.NORM_L2) / len(img_points2)
                total_error += error
            
            mean_error = total_error / len(obj_points)
            
            calibration_result = {
                'camera_matrix': camera_matrix.tolist(),
                'distortion_coefficients': dist_coeffs.tolist(),
                'rotation_vectors': [r.tolist() for r in rvecs],
                'translation_vectors': [t.tolist() for t in tvecs],
                'reprojection_error': float(mean_error),
                'image_size': image_size,
                'calibration_date': datetime.utcnow().isoformat(),
                'pattern_type': pattern_type,
                'pattern_size': pattern_size,
                'square_size': square_size,
                'num_images': len(obj_points)
            }
            
            return calibration_result
            
        except Exception as e:
            logger.error(f"Calibration error: {e}")
            raise
    
    def validate_calibration(self, calibration_data: Dict) -> Dict:
        """Validate calibration results"""
        try:
            validation = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required fields
            required_fields = ['camera_matrix', 'distortion_coefficients']
            for field in required_fields:
                if field not in calibration_data:
                    validation['errors'].append(f"Missing required field: {field}")
                    validation['is_valid'] = False
            
            # Check reprojection error
            if 'reprojection_error' in calibration_data:
                error = calibration_data['reprojection_error']
                if error > 1.0:
                    validation['warnings'].append(f"High reprojection error: {error:.3f}")
                if error > 2.0:
                    validation['errors'].append(f"Reprojection error too high: {error:.3f}")
                    validation['is_valid'] = False
            
            # Check number of images
            if 'num_images' in calibration_data:
                num_images = calibration_data['num_images']
                if num_images < 3:
                    validation['errors'].append(f"Too few calibration images: {num_images}")
                    validation['is_valid'] = False
                elif num_images < 10:
                    validation['warnings'].append(f"Consider using more images for better calibration")
            
            # Validate camera matrix
            if 'camera_matrix' in calibration_data:
                try:
                    matrix = np.array(calibration_data['camera_matrix'])
                    if matrix.shape != (3, 3):
                        validation['errors'].append("Invalid camera matrix shape")
                        validation['is_valid'] = False
                except Exception:
                    validation['errors'].append("Invalid camera matrix format")
                    validation['is_valid'] = False
            
            return validation
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise
    
    def save_calibration(self, calibration_data: Dict, name: str) -> str:
        """Save calibration data"""
        try:
            calibration_id = f"calib_{name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            self.calibrations[calibration_id] = {
                **calibration_data,
                'id': calibration_id,
                'name': name,
                'saved_at': datetime.utcnow().isoformat()
            }
            
            return calibration_id
            
        except Exception as e:
            logger.error(f"Save error: {e}")
            raise
    
    def load_calibration(self, calibration_id: str) -> Optional[Dict]:
        """Load saved calibration"""
        return self.calibrations.get(calibration_id)
    
    def _generate_chessboard(self, rows: int, cols: int, square_size: float) -> np.ndarray:
        """Generate chessboard pattern image"""
        # Convert mm to pixels (assuming 10 pixels per mm for display)
        pixels_per_mm = 10
        square_pixels = int(square_size * pixels_per_mm)
        
        width = cols * square_pixels
        height = rows * square_pixels
        
        # Create chessboard
        pattern = np.zeros((height, width), dtype=np.uint8)
        
        for row in range(rows):
            for col in range(cols):
                if (row + col) % 2 == 0:
                    y1 = row * square_pixels
                    y2 = (row + 1) * square_pixels
                    x1 = col * square_pixels
                    x2 = (col + 1) * square_pixels
                    pattern[y1:y2, x1:x2] = 255
        
        return pattern
    
    def _generate_circles_grid(self, rows: int, cols: int, square_size: float) -> np.ndarray:
        """Generate circles grid pattern"""
        pixels_per_mm = 10
        square_pixels = int(square_size * pixels_per_mm)
        circle_radius = int(square_pixels * 0.3)
        
        width = cols * square_pixels
        height = rows * square_pixels
        
        pattern = np.ones((height, width), dtype=np.uint8) * 255
        
        for row in range(rows):
            for col in range(cols):
                center_x = int((col + 0.5) * square_pixels)
                center_y = int((row + 0.5) * square_pixels)
                cv2.circle(pattern, (center_x, center_y), circle_radius, 0, -1)
        
        return pattern
    
    def _generate_asymmetric_circles(self, rows: int, cols: int, square_size: float) -> np.ndarray:
        """Generate asymmetric circles pattern"""
        pixels_per_mm = 10
        square_pixels = int(square_size * pixels_per_mm)
        circle_radius = int(square_pixels * 0.3)
        
        width = (cols * 2 - 1) * square_pixels // 2
        height = rows * square_pixels
        
        pattern = np.ones((height, width), dtype=np.uint8) * 255
        
        for row in range(rows):
            for col in range(cols):
                if row % 2 == 0:
                    center_x = int(col * square_pixels)
                else:
                    center_x = int((col + 0.5) * square_pixels)
                center_y = int((row + 0.5) * square_pixels)
                cv2.circle(pattern, (center_x, center_y), circle_radius, 0, -1)
        
        return pattern