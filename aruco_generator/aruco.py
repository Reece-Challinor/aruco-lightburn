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
    import numpy as np
    OPENCV_AVAILABLE = False

from typing import Tuple, List, Dict, Any

class ArUCOGenerator:
    def __init__(self):
        if OPENCV_AVAILABLE:
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
            if OPENCV_AVAILABLE:
                dictionary = cv2.aruco.getPredefinedDictionary(dict_data)
                bits, max_markers = name.split('_')
                info[name] = {
                    'bits': bits,
                    'max_markers': int(max_markers),
                    'description': f"{bits} bits, {max_markers} unique markers"
                }
            else:
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
        
        if OPENCV_AVAILABLE:
            dictionary = cv2.aruco.getPredefinedDictionary(self.dictionaries[dict_name])
            marker_image = cv2.aruco.generateImageMarker(dictionary, marker_id, size_pixels)
            return marker_image
        else:
            # Fallback mode - generate simple pattern
            return self._create_fallback_pattern(marker_id, dict_name, size_pixels)
    
    def _create_fallback_pattern(self, marker_id: int, dict_name: str, size_pixels: int) -> np.ndarray:
        """Create a simplified ArUCO-like pattern for fallback mode"""
        dict_info = self.dictionaries[dict_name]
        size = dict_info["size"]
        
        # Create border (always black)
        pattern = np.zeros((size + 2, size + 2), dtype=np.uint8)
        
        # Generate inner pattern based on marker ID
        for i in range(size):
            for j in range(size):
                bit_position = i * size + j
                bit_value = (marker_id >> (bit_position % 16)) & 1
                pattern[i + 1, j + 1] = 255 if bit_value else 0
        
        # Scale to requested size
        scale_factor = size_pixels // pattern.shape[0]
        if scale_factor < 1:
            scale_factor = 1
        
        scaled_pattern = np.repeat(np.repeat(pattern, scale_factor, axis=0), scale_factor, axis=1)
        
        # Ensure exact size
        if scaled_pattern.shape[0] != size_pixels:
            final_pattern = np.zeros((size_pixels, size_pixels), dtype=np.uint8)
            y_scale = size_pixels / scaled_pattern.shape[0]
            x_scale = size_pixels / scaled_pattern.shape[1]
            
            for i in range(size_pixels):
                for j in range(size_pixels):
                    src_i = int(i / y_scale)
                    src_j = int(j / x_scale)
                    if src_i < scaled_pattern.shape[0] and src_j < scaled_pattern.shape[1]:
                        final_pattern[i, j] = scaled_pattern[src_i, src_j]
            
            scaled_pattern = final_pattern
        
        return scaled_pattern
    
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
