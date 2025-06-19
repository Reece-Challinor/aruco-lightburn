"""
Fallback ArUCO generator using pure Python when OpenCV is not available
This provides basic ArUCO marker generation functionality without system dependencies
"""

import numpy as np
from typing import Tuple, List, Dict, Any

class ArUCOGenerator:
    def __init__(self):
        # ArUCO dictionary patterns (simplified for fallback mode)
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
        
        # Simplified ArUCO patterns for basic functionality
        self._aruco_patterns = self._generate_basic_patterns()
    
    def _generate_basic_patterns(self) -> Dict[str, Dict[int, np.ndarray]]:
        """Generate basic ArUCO-like patterns for fallback mode"""
        patterns = {}
        
        for dict_name, info in self.dictionaries.items():
            size = info["size"]
            max_ids = info["max_ids"]
            patterns[dict_name] = {}
            
            # Generate simplified patterns based on marker ID
            for marker_id in range(min(max_ids, 100)):  # Limit for fallback
                pattern = self._create_pattern(marker_id, size)
                patterns[dict_name][marker_id] = pattern
                
        return patterns
    
    def _create_pattern(self, marker_id: int, size: int) -> np.ndarray:
        """Create a simplified ArUCO-like pattern"""
        # Create border (always black)
        pattern = np.zeros((size + 2, size + 2), dtype=np.uint8)
        
        # Generate inner pattern based on marker ID
        for i in range(size):
            for j in range(size):
                # Simple pattern generation using marker_id and position
                bit_position = i * size + j
                bit_value = (marker_id >> (bit_position % 16)) & 1
                pattern[i + 1, j + 1] = 255 if bit_value else 0
        
        return pattern
    
    def get_dictionary_info(self) -> Dict[str, Dict[str, Any]]:
        """Return dictionary information for UI"""
        info = {}
        for name, dict_info in self.dictionaries.items():
            size = dict_info["size"]
            max_ids = dict_info["max_ids"]
            
            info[name] = {
                "name": name,
                "marker_size": f"{size}x{size}",
                "max_markers": max_ids,
                "description": f"{size}x{size} bits, up to {max_ids} unique markers",
                "bits_per_side": size,
                "total_bits": size * size,
                "border_bits": 1,
                "data_bits": size * size
            }
        return info
    
    def generate_marker(self, marker_id: int, dict_name: str, size_pixels: int = 200) -> np.ndarray:
        """Generate single ArUCO marker as numpy array"""
        if dict_name not in self.dictionaries:
            raise ValueError(f"Unknown dictionary: {dict_name}")
        
        dict_info = self.dictionaries[dict_name]
        if marker_id >= dict_info["max_ids"]:
            raise ValueError(f"Marker ID {marker_id} exceeds maximum for {dict_name} ({dict_info['max_ids']})")
        
        # Get base pattern
        if dict_name in self._aruco_patterns and marker_id in self._aruco_patterns[dict_name]:
            base_pattern = self._aruco_patterns[dict_name][marker_id]
        else:
            # Generate pattern on demand
            base_pattern = self._create_pattern(marker_id, dict_info["size"])
        
        # Scale to requested size
        scale_factor = size_pixels // base_pattern.shape[0]
        if scale_factor < 1:
            scale_factor = 1
        
        scaled_pattern = np.repeat(np.repeat(base_pattern, scale_factor, axis=0), scale_factor, axis=1)
        
        # Ensure exact size
        if scaled_pattern.shape[0] != size_pixels:
            # Resize to exact dimensions
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
        markers = []
        marker_count = 0
        
        for row in range(rows):
            for col in range(cols):
                marker_id = start_id + marker_count
                
                # Calculate position
                x = col * (size_mm + spacing_mm)
                y = row * (size_mm + spacing_mm)
                
                marker_data = {
                    'id': marker_id,
                    'x': x,
                    'y': y,
                    'size': size_mm,
                    'row': row,
                    'col': col
                }
                
                if generate_images:
                    try:
                        marker_data['image'] = self.generate_marker(marker_id, dict_name, 200)
                    except ValueError as e:
                        # Skip invalid marker IDs
                        continue
                
                markers.append(marker_data)
                marker_count += 1
        
        return markers
    
    def calculate_total_size(self, rows: int, cols: int, size_mm: float, spacing_mm: float) -> Tuple[float, float]:
        """Calculate total dimensions of marker grid"""
        width = cols * size_mm + (cols - 1) * spacing_mm
        height = rows * size_mm + (rows - 1) * spacing_mm
        return width, height