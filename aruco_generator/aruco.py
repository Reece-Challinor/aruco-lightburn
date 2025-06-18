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

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any

class ArUCOGenerator:
    def __init__(self):
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
    
    def get_dictionary_info(self) -> Dict[str, Dict[str, Any]]:
        """Return dictionary information for UI"""
        info = {}
        for name, dict_id in self.dictionaries.items():
            dictionary = cv2.aruco.getPredefinedDictionary(dict_id)
            bits, max_markers = name.split('_')
            info[name] = {
                'bits': bits,
                'max_markers': int(max_markers),
                'description': f"{bits} bits, {max_markers} unique markers"
            }
        return info
    
    def generate_marker(self, marker_id: int, dict_name: str, size_pixels: int = 200) -> np.ndarray:
        """Generate single ArUCO marker as numpy array"""
        if dict_name not in self.dictionaries:
            raise ValueError(f"Unknown dictionary: {dict_name}")
        
        dictionary = cv2.aruco.getPredefinedDictionary(self.dictionaries[dict_name])
        marker_image = cv2.aruco.generateImageMarker(dictionary, marker_id, size_pixels)
        return marker_image
    
    def generate_grid(self, start_id: int, dict_name: str, rows: int, cols: int, 
                     size_mm: float, spacing_mm: float) -> List[Dict[str, Any]]:
        """Generate grid of markers with positions"""
        if rows * cols + start_id > self.get_dictionary_info()[dict_name]['max_markers']:
            raise ValueError(f"Too many markers requested for dictionary {dict_name}")
        
        markers = []
        for row in range(rows):
            for col in range(cols):
                marker_id = start_id + (row * cols + col)
                marker_image = self.generate_marker(marker_id, dict_name)
                
                x = col * (size_mm + spacing_mm)
                y = row * (size_mm + spacing_mm)
                
                markers.append({
                    'id': marker_id,
                    'image': marker_image,
                    'x': x,
                    'y': y,
                    'size': size_mm,
                    'dict': dict_name
                })
        return markers
    
    def calculate_total_size(self, rows: int, cols: int, size_mm: float, spacing_mm: float) -> Tuple[float, float]:
        """Calculate total dimensions of marker grid"""
        width = cols * size_mm + (cols - 1) * spacing_mm
        height = rows * size_mm + (rows - 1) * spacing_mm
        return width, height
