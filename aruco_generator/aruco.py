"""
{
  "file_type": "core_aruco_generator",
  "purpose": "Core ArUCO marker generation using OpenCV",
  "dependencies": ["opencv-python", "numpy"],
  "main_class": "ArUCOGenerator",
  "key_methods": {
    "get_dictionary_info": "Returns available ArUCO dictionaries",
    "generate_marker": "Creates single ArUCO marker as numpy array",
    "generate_grid": "Creates grid of markers with positions",
    "calculate_total_size": "Calculates grid dimensions"
  },
  "ai_navigation": {
    "modify_for": "Adding new dictionary types or marker generation logic",
    "used_by": ["web.py", "drawing.py"],
    "output_format": "numpy arrays for OpenCV processing"
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

from typing import Tuple, List, Dict, Any, Union
from datetime import datetime

class ArUCOGenerator:
    def __init__(self):
        self.dictionaries: Dict[str, Union[int, Dict[str, int]]] = {}
        
        if OPENCV_AVAILABLE and cv2 is not None:
            self.dictionaries = {
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
        else:
            # Fallback mode - basic ArUCO dictionary info
            self.dictionaries = {
                "4X4_50": {"size": 4, "max_ids": 50},
                "4X4_100": {"size": 4, "max_ids": 100},
                "4X4_250": {"size": 4, "max_ids": 250},
                "4X4_1000": {"size": 4, "max_ids": 1000},
                "5X5_50": {"size": 5, "max_ids": 50},
                "5X5_100": {"size": 5, "max_ids": 100},
                "5X5_250": {"size": 5, "max_ids": 250},
                "5X5_1000": {"size": 5, "max_ids": 1000},
                "6X6_50": {"size": 6, "max_ids": 50},
                "6X6_100": {"size": 6, "max_ids": 100},
                "6X6_250": {"size": 6, "max_ids": 250},
                "6X6_1000": {"size": 6, "max_ids": 1000},
                "7X7_50": {"size": 7, "max_ids": 50},
                "7X7_100": {"size": 7, "max_ids": 100},
                "7X7_250": {"size": 7, "max_ids": 250},
                "7X7_1000": {"size": 7, "max_ids": 1000},
            }
    
    def get_dictionary_info(self) -> Dict[str, Dict[str, Any]]:
        """Return dictionary information for UI"""
        info = {}
        for name, dict_data in self.dictionaries.items():
            if OPENCV_AVAILABLE and cv2 is not None and isinstance(dict_data, int):
                dictionary = cv2.aruco.getPredefinedDictionary(dict_data)
                bits, max_markers = name.split('_')
                info[name] = {
                    'bits': bits,
                    'max_markers': int(max_markers),
                    'description': f"{bits} bits, {max_markers} unique markers"
                }
            elif isinstance(dict_data, dict):
                # Fallback mode - use dictionary data directly
                bits_per_side = dict_data["size"]
                max_markers = dict_data["max_ids"]
                info[name] = {
                    'bits': f"{bits_per_side}X{bits_per_side}",
                    'max_markers': max_markers,
                    'description': f"{bits_per_side}x{bits_per_side} bits, {max_markers} unique markers"
                }
        return info
    
    def generate_marker(self, marker_id: int, dict_name: str, size_pixels: int = 200) -> np.ndarray:
        """Generate single ArUCO marker as numpy array"""
        if dict_name not in self.dictionaries:
            raise ValueError(f"Unknown dictionary: {dict_name}")
        
        dict_data = self.dictionaries[dict_name]
        if OPENCV_AVAILABLE and cv2 is not None and isinstance(dict_data, int):
            dictionary = cv2.aruco.getPredefinedDictionary(dict_data)
            marker_image = cv2.aruco.generateImageMarker(dictionary, marker_id, size_pixels)
            return marker_image
        else:
            # Fallback mode - generate simple pattern
            return self._create_fallback_pattern(marker_id, dict_name, size_pixels)
    
    def _create_fallback_pattern(self, marker_id: int, dict_name: str, size_pixels: int) -> np.ndarray:
        """Create a simplified ArUCO-like pattern for fallback mode with proper scaling"""
        dict_data = self.dictionaries[dict_name]
        if not isinstance(dict_data, dict):
            # Should not happen, but handle for type safety
            size = 4  # Default size
        else:
            size = dict_data["size"]
        
        # Create border (always black)
        pattern = np.zeros((size + 2, size + 2), dtype=np.uint8)
        
        # Generate inner pattern based on marker ID
        for i in range(size):
            for j in range(size):
                bit_position = i * size + j
                bit_value = (marker_id >> (bit_position % 16)) & 1
                pattern[i + 1, j + 1] = 255 if bit_value else 0
        
        # Use nearest neighbor scaling to preserve sharp edges
        # Calculate exact scale factor
        scale_factor = size_pixels / pattern.shape[0]
        
        # Create output array
        final_pattern = np.zeros((size_pixels, size_pixels), dtype=np.uint8)
        
        # Use nearest neighbor interpolation to prevent artifacts
        for i in range(size_pixels):
            for j in range(size_pixels):
                # Find source pixel using nearest neighbor
                src_i = min(int(i / scale_factor), pattern.shape[0] - 1)
                src_j = min(int(j / scale_factor), pattern.shape[1] - 1)
                
                # Copy the value (ensure crisp black/white)
                value = pattern[src_i, src_j]
                # Force to pure black or white
                final_pattern[i, j] = 255 if value > 127 else 0
        
        return final_pattern
    
    def generate_grid(self, start_id: int, dict_name: str, rows: int, cols: int, 
                     size_mm: float, spacing_mm: float, generate_images: bool = True) -> List[Dict[str, Any]]:
        """Generate grid of markers with positions"""
        if rows * cols + start_id > self.get_dictionary_info()[dict_name]['max_markers']:
            raise ValueError(f"Too many markers requested for dictionary {dict_name}")
        
        markers = []
        for row in range(rows):
            for col in range(cols):
                marker_id = start_id + (row * cols + col)
                
                x = col * (size_mm + spacing_mm)
                y = row * (size_mm + spacing_mm)
                
                marker_data = {
                    'id': marker_id,
                    'x': x,
                    'y': y,
                    'size': size_mm,
                    'dict': dict_name
                }
                
                # Only generate actual images when needed (for file export)
                if generate_images:
                    marker_data['image'] = self.generate_marker(marker_id, dict_name)
                
                markers.append(marker_data)
        return markers
    
    def calculate_total_size(self, rows: int, cols: int, size_mm: float, spacing_mm: float) -> Tuple[float, float]:
        """Calculate total dimensions of marker grid"""
        width = cols * size_mm + (cols - 1) * spacing_mm
        height = rows * size_mm + (rows - 1) * spacing_mm
        return width, height
    
    def generate_with_coordinates(self, marker_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate markers with world coordinate metadata for calibration.
        
        Args:
            marker_config: Configuration dict containing:
                - dictionary: ArUCO dictionary name
                - marker_ids: List of marker IDs or single ID
                - size_mm: Physical marker size in mm
                - positions: List of (x, y, z) positions in mm (optional)
                - orientations: List of (roll, pitch, yaw) in degrees (optional)
                - reference_frame: Coordinate frame name (default: 'world')
        
        Returns:
            Dictionary containing:
                - markers: List of marker data with coordinates
                - calibration_data: Full calibration metadata
                - coordinate_frame: Reference frame information
        """
        dictionary = marker_config.get('dictionary', '4X4_50')
        marker_ids = marker_config.get('marker_ids', [0])
        if isinstance(marker_ids, int):
            marker_ids = [marker_ids]
        
        size_mm = marker_config.get('size_mm', 50.0)
        positions = marker_config.get('positions', [])
        orientations = marker_config.get('orientations', [])
        reference_frame = marker_config.get('reference_frame', 'world')
        
        # Generate default positions if not provided
        if not positions:
            positions = [[i * (size_mm + 10), 0, 0] for i in range(len(marker_ids))]
        
        # Default orientations (no rotation)
        if not orientations:
            orientations = [[0, 0, 0] for _ in marker_ids]
        
        markers_data = []
        for idx, marker_id in enumerate(marker_ids):
            # Generate marker image
            marker_image = self.generate_marker(marker_id, dictionary, size_pixels=200)
            
            # Get position and orientation
            pos = positions[idx] if idx < len(positions) else [0, 0, 0]
            orient = orientations[idx] if idx < len(orientations) else [0, 0, 0]
            
            # Calculate corner coordinates in 3D space
            half_size = size_mm / 2.0
            corners_3d = [
                [pos[0] - half_size, pos[1] - half_size, pos[2]],  # Top-left
                [pos[0] + half_size, pos[1] - half_size, pos[2]],  # Top-right
                [pos[0] + half_size, pos[1] + half_size, pos[2]],  # Bottom-right
                [pos[0] - half_size, pos[1] + half_size, pos[2]]   # Bottom-left
            ]
            
            # Apply rotation if needed (simplified - for full rotation use rotation matrices)
            if any(orient):
                import math
                # Convert degrees to radians
                roll, pitch, yaw = [math.radians(angle) for angle in orient]
                # Note: Full rotation implementation would use rotation matrices
                # This is simplified for demonstration
            
            marker_data = {
                'id': marker_id,
                'dictionary': dictionary,
                'size_mm': size_mm,
                'position_mm': pos,
                'orientation_deg': orient,
                'corners_3d': corners_3d,
                'center_3d': pos,
                'normal_vector': [0, 0, 1],  # Default pointing up
                'image': marker_image
            }
            markers_data.append(marker_data)
        
        # Create calibration metadata
        calibration_data = {
            'pattern_type': 'aruco_markers',
            'coordinate_system': {
                'reference_frame': reference_frame,
                'units': 'millimeters',
                'origin': [0, 0, 0],
                'axes': {
                    'x': [1, 0, 0],
                    'y': [0, 1, 0],
                    'z': [0, 0, 1]
                }
            },
            'markers': [
                {
                    'id': m['id'],
                    'position': m['position_mm'],
                    'orientation': m['orientation_deg'],
                    'corners': m['corners_3d'],
                    'size_mm': m['size_mm']
                }
                for m in markers_data
            ],
            'dictionary': dictionary,
            'total_markers': len(markers_data),
            'generation_timestamp': datetime.now().isoformat()
        }
        
        return {
            'markers': markers_data,
            'calibration_data': calibration_data,
            'coordinate_frame': {
                'reference': reference_frame,
                'units': 'mm',
                'origin': [0, 0, 0]
            }
        }
    
    def generate_pose_estimation_board(self, board_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate board optimized for pose estimation with coordinate data.
        
        Args:
            board_config: Configuration for pose estimation board
        
        Returns:
            Board data with full 3D coordinate information
        """
        rows = board_config.get('rows', 3)
        cols = board_config.get('cols', 3)
        marker_size = board_config.get('marker_size_mm', 50.0)
        spacing = board_config.get('spacing_mm', 10.0)
        dictionary = board_config.get('dictionary', '4X4_50')
        start_id = board_config.get('start_id', 0)
        
        # Generate marker positions
        markers = []
        marker_ids = []
        positions = []
        
        for row in range(rows):
            for col in range(cols):
                marker_id = start_id + row * cols + col
                x = col * (marker_size + spacing)
                y = row * (marker_size + spacing)
                z = 0  # Planar board
                
                marker_ids.append(marker_id)
                positions.append([x, y, z])
        
        # Use generate_with_coordinates for full coordinate data
        result = self.generate_with_coordinates({
            'dictionary': dictionary,
            'marker_ids': marker_ids,
            'size_mm': marker_size,
            'positions': positions,
            'reference_frame': 'board'
        })
        
        # Add board-specific metadata
        result['board_config'] = {
            'grid_size': [cols, rows],
            'marker_size_mm': marker_size,
            'spacing_mm': spacing,
            'board_width_mm': cols * marker_size + (cols - 1) * spacing,
            'board_height_mm': rows * marker_size + (rows - 1) * spacing,
            'planar': True,
            'use_case': 'pose_estimation'
        }
        
        return result
