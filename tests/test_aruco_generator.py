"""
Unit tests for ArUCO marker generation - Fixed for updated API
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aruco_generator.aruco import ArUCOGenerator


class TestArUCOGenerator(unittest.TestCase):
    """Test ArUCO marker generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = ArUCOGenerator()
    
    def test_dictionary_initialization(self):
        """Test that dictionaries are properly initialized"""
        self.assertIsNotNone(self.generator.dictionaries)
        self.assertIn('4X4_50', self.generator.dictionaries)
        self.assertIn('6X6_250', self.generator.dictionaries)
    
    def test_get_dictionary_info(self):
        """Test dictionary info retrieval"""
        info = self.generator.get_dictionary_info()
        self.assertIsInstance(info, dict)
        
        # Check structure of dictionary info
        for dict_name, dict_info in info.items():
            self.assertIn('size', dict_info)
            self.assertIn('max_markers', dict_info)
            self.assertIn('recommended_use', dict_info)
            self.assertIsInstance(dict_info['size'], int)
            self.assertIsInstance(dict_info['max_markers'], int)
    
    def test_generate_single_marker(self):
        """Test single marker generation"""
        marker = self.generator.generate_marker(
            marker_id=0,
            dict_name='4X4_50',
            size_pixels=200
        )
        
        # Check marker is a numpy array
        self.assertIsInstance(marker, np.ndarray)
        
        # Check marker dimensions
        self.assertEqual(len(marker.shape), 2)  # 2D array
        self.assertGreater(marker.shape[0], 0)
        self.assertGreater(marker.shape[1], 0)
    
    def test_invalid_marker_id(self):
        """Test that invalid marker ID raises error"""
        with self.assertRaises(ValueError):
            self.generator.generate_marker(
                marker_id=51,  # Max ID for 4X4_50 is 50
                dict_name='4X4_50',
                size_pixels=200
            )
    
    def test_generate_grid(self):
        """Test grid generation with multiple markers"""
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name='4X4_50',
            rows=2,
            cols=3,
            size_mm=20,
            spacing_mm=5
        )
        
        # Check we get correct number of markers
        self.assertEqual(len(markers), 6)  # 2 rows × 3 cols
        
        # Check each marker has required fields
        for marker in markers:
            self.assertIn('id', marker)
            self.assertIn('x', marker)
            self.assertIn('y', marker)
            self.assertIn('size', marker)
            self.assertIn('dict', marker)
    
    def test_calculate_total_size(self):
        """Test total size calculation for grid"""
        width, height = self.generator.calculate_total_size(
            rows=2,
            cols=3,
            size_mm=20,
            spacing_mm=5
        )
        
        # Expected: 3 markers of 20mm + 2 spaces of 5mm = 70mm width
        # Expected: 2 markers of 20mm + 1 space of 5mm = 45mm height
        self.assertEqual(width, 70)
        self.assertEqual(height, 45)
    
    def test_generate_charuco_board(self):
        """Test ChArUco board generation"""
        result = self.generator.generate_charuco_board(
            cols=5,
            rows=7,
            square_size_mm=30,
            marker_size_mm=22,
            dictionary='4X4_50',
            start_id=0
        )
        
        self.assertIn('board_image', result)
        self.assertIn('corners_3d', result)
        self.assertIn('marker_ids', result)
        self.assertIn('board_config', result)
        
        # Check board configuration
        config = result['board_config']
        self.assertEqual(config['grid_size'], [5, 7])
        self.assertEqual(config['marker_size_mm'], 22)
    
    def test_invalid_dictionary(self):
        """Test that invalid dictionary raises error"""
        with self.assertRaises(ValueError):
            self.generator.generate_marker(
                marker_id=0,
                dict_name='INVALID_DICT',
                size_pixels=200
            )
    
    def test_negative_size(self):
        """Test that negative size raises error"""
        with self.assertRaises(ValueError):
            self.generator.generate_marker(
                marker_id=0,
                dict_name='4X4_50',
                size_pixels=-200
            )
    
    def test_zero_border_bits(self):
        """Test marker generation with default size"""
        marker = self.generator.generate_marker(
            marker_id=0,
            dict_name='4X4_50'
        )
        
        self.assertIsInstance(marker, np.ndarray)
        # With default size
        self.assertGreater(marker.shape[0], 0)


class TestArUCOGeneratorFallback(unittest.TestCase):
    """Test ArUCO generator in fallback mode (no OpenCV)"""
    
    @patch('aruco_generator.aruco.OPENCV_AVAILABLE', False)
    @patch('aruco_generator.aruco.cv2', None)
    def test_fallback_mode(self):
        """Test that generator works without OpenCV"""
        from aruco_generator.aruco import ArUCOGenerator
        
        generator = ArUCOGenerator()
        
        # Should still have dictionary info
        info = generator.get_dictionary_info()
        self.assertIsInstance(info, dict)
        self.assertIn('4X4_50', info)
        
        # Should be able to generate placeholder
        marker = generator.generate_marker(
            marker_id=0,
            dict_name='4X4_50',
            size_pixels=200
        )
        self.assertIsInstance(marker, np.ndarray)


if __name__ == '__main__':
    unittest.main()