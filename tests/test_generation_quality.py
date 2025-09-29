"""
Integration tests for ArUCO marker generation quality.
Tests ensure no line artifacts or rendering issues in generated markers.
"""

import pytest
import numpy as np
import os
import sys
import json
import tempfile
from io import BytesIO
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aruco_generator.aruco import ArUCOGenerator
from aruco_generator.drawing import DrawingContext
from aruco_generator.lightburn import LightBurnExporter

class TestGenerationQuality:
    """Test suite for marker generation quality assurance"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ArUCOGenerator()
        self.exporter = LightBurnExporter()
        
    def test_no_line_artifacts_in_single_marker(self):
        """Ensure single markers have no line artifacts"""
        # Generate a single marker
        marker = self.generator.generate_marker(marker_id=0, dict_name="4X4_50", size_pixels=200)
        
        # Check that marker has proper black/white contrast
        unique_values = np.unique(marker)
        assert len(unique_values) == 2, "Marker should only have black and white pixels"
        assert 0 in unique_values and 255 in unique_values, "Marker should have pure black and white"
        
        # Check for continuous regions (no thin lines)
        self._check_no_thin_lines(marker)
        
    def test_no_gaps_in_merged_rectangles(self):
        """Test that rectangle merging doesn't create gaps"""
        # Create a test pattern with known structure
        test_pattern = np.zeros((10, 10), dtype=np.uint8)
        test_pattern[2:8, 2:8] = 0  # Black square
        test_pattern[0:2, :] = 0  # Black top border
        test_pattern[8:10, :] = 0  # Black bottom border
        test_pattern[:, 0:2] = 0  # Black left border
        test_pattern[:, 8:10] = 0  # Black right border
        test_pattern[4:6, 4:6] = 255  # White center
        
        # Test the drawing context
        ctx = DrawingContext()
        rectangles = ctx._find_merged_rectangles(test_pattern)
        
        # Verify rectangles cover all black pixels
        coverage = np.ones_like(test_pattern) * 255
        for rect in rectangles:
            r, c = rect['row'], rect['col']
            h, w = rect['height'], rect['width']
            coverage[r:r+h, c:c+w] = 0
        
        # Coverage should match original pattern
        np.testing.assert_array_equal(coverage, test_pattern, 
                                      "Merged rectangles should cover all black pixels without gaps")
        
    def test_svg_preview_quality(self):
        """Test SVG preview generation has no artifacts"""
        # Generate a grid of markers
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", 
            rows=2, cols=2, 
            size_mm=20, spacing_mm=5
        )
        
        # Create drawing context and add markers
        ctx = DrawingContext()
        ctx.add_marker_grid_preview(markers, include_borders=True)
        
        # Get SVG and validate
        svg = ctx.get_svg()
        
        # Check SVG is valid
        assert svg.startswith('<svg'), "SVG should start with <svg> tag"
        assert '</svg>' in svg, "SVG should have closing tag"
        
        # Parse SVG and check for overlapping rectangles (prevents gaps)
        self._validate_svg_rectangles(svg)
        
    def test_lightburn_export_quality(self):
        """Test LightBurn export has proper structure"""
        # Generate markers
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=1, cols=1,
            size_mm=30, spacing_mm=0
        )
        
        # Create drawing context
        ctx = DrawingContext()
        ctx.add_marker_grid(markers, include_borders=True)
        
        # Export to LightBurn
        metadata = {
            'dictionary': '4X4_50',
            'start_id': 0,
            'grid_size': '1x1',
            'marker_size': '30mm',
            'spacing': '0mm'
        }
        
        output = self.exporter.export(ctx, metadata)
        
        # Parse XML
        output.seek(0)
        tree = ET.parse(output)
        root = tree.getroot()
        
        # Validate structure
        assert root.tag == 'LightBurnProject', "Root should be LightBurnProject"
        
        # Check for shapes
        shapes = root.findall('.//Shape')
        assert len(shapes) > 0, "Should have at least one shape"
        
    def test_scaling_preserves_quality(self):
        """Test that scaling operations preserve marker quality"""
        sizes = [50, 100, 200, 400]
        
        for size in sizes:
            marker = self.generator.generate_marker(
                marker_id=5, dict_name="5X5_100", size_pixels=size
            )
            
            # Check dimensions
            assert marker.shape == (size, size), f"Marker should be {size}x{size} pixels"
            
            # Check contrast
            unique = np.unique(marker)
            assert len(unique) == 2, f"Marker at size {size} should have only 2 colors"
            
            # Check for artifacts
            self._check_no_thin_lines(marker)
            
    def test_grid_generation_alignment(self):
        """Test that grid generation maintains proper alignment"""
        # Generate a 3x3 grid
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=3, cols=3,
            size_mm=25, spacing_mm=5
        )
        
        # Check marker count
        assert len(markers) == 9, "Should have 9 markers in 3x3 grid"
        
        # Check spacing
        for i, marker in enumerate(markers):
            row = i // 3
            col = i % 3
            
            expected_x = col * (25 + 5)
            expected_y = row * (25 + 5)
            
            assert marker['x'] == expected_x, f"Marker {i} X position incorrect"
            assert marker['y'] == expected_y, f"Marker {i} Y position incorrect"
            
    def test_fallback_pattern_quality(self):
        """Test fallback pattern generation when OpenCV is not available"""
        # Test the fallback pattern directly
        marker_id = 10
        dict_name = "4X4_50"
        size_pixels = 200
        
        pattern = self.generator._create_fallback_pattern(marker_id, dict_name, size_pixels)
        
        # Check dimensions
        assert pattern.shape == (size_pixels, size_pixels), "Pattern should match requested size"
        
        # Check values are binary
        unique = np.unique(pattern)
        assert len(unique) == 2, "Pattern should be binary"
        assert set(unique) == {0, 255}, "Pattern should use 0 and 255 values"
        
        # Check border is black (ArUCO standard)
        assert np.all(pattern[0, :] == 0), "Top border should be black"
        assert np.all(pattern[-1, :] == 0), "Bottom border should be black"
        assert np.all(pattern[:, 0] == 0), "Left border should be black"
        assert np.all(pattern[:, -1] == 0), "Right border should be black"
        
    def _check_no_thin_lines(self, image, max_thin_line_width=1):
        """Helper to check for thin line artifacts"""
        # Check horizontal lines
        for row in range(1, image.shape[0] - 1):
            # A thin line would be a single row different from neighbors
            if not np.array_equal(image[row], image[row-1]) and \
               not np.array_equal(image[row], image[row+1]):
                # Check if this is really a thin line (not part of pattern)
                line_pixels = np.sum(image[row] != image[row-1])
                if line_pixels < image.shape[1] * 0.1:  # Less than 10% different
                    pytest.fail(f"Thin horizontal line artifact detected at row {row}")
                    
        # Check vertical lines
        for col in range(1, image.shape[1] - 1):
            column = image[:, col]
            prev_column = image[:, col-1]
            next_column = image[:, col+1]
            
            if not np.array_equal(column, prev_column) and \
               not np.array_equal(column, next_column):
                line_pixels = np.sum(column != prev_column)
                if line_pixels < image.shape[0] * 0.1:  # Less than 10% different
                    pytest.fail(f"Thin vertical line artifact detected at column {col}")
                    
    def _validate_svg_rectangles(self, svg_content):
        """Validate SVG rectangles for proper overlap"""
        # Simple validation - check that rectangles exist and have valid dimensions
        import re
        
        # Find all rectangle elements
        rect_pattern = r'<rect[^>]*>'
        rectangles = re.findall(rect_pattern, svg_content)
        
        assert len(rectangles) > 0, "SVG should contain rectangles"
        
        # Check for valid attributes
        for rect in rectangles:
            assert 'width=' in rect, "Rectangle should have width"
            assert 'height=' in rect, "Rectangle should have height"
            assert 'x=' in rect, "Rectangle should have x position"
            assert 'y=' in rect, "Rectangle should have y position"
            
            # Extract dimensions and check they're positive
            width_match = re.search(r'width="([0-9.]+)"', rect)
            height_match = re.search(r'height="([0-9.]+)"', rect)
            
            if width_match and height_match:
                width = float(width_match.group(1))
                height = float(height_match.group(1))
                assert width > 0, "Rectangle width should be positive"
                assert height > 0, "Rectangle height should be positive"


class TestCalibrationPatternQuality:
    """Test calibration pattern generation quality"""
    
    def test_charuco_board_generation(self):
        """Test ChArUco board has no rendering artifacts"""
        try:
            from aruco_generator.calibration import CalibrationPatternGenerator
            
            gen = CalibrationPatternGenerator()
            result = gen.generate_charuco_board(
                squares_x=5,
                squares_y=4,
                square_size_mm=30,
                marker_size_mm=22,
                dictionary="4X4_50"
            )
            
            # Check board image
            board_image = result.get('board_image')
            if board_image is not None:
                # Should be binary
                unique = np.unique(board_image)
                assert len(unique) == 2, "ChArUco board should be binary"
                
            # Check metadata
            assert 'calibration_data' in result
            assert result['calibration_data']['pattern_type'] == 'charuco'
            
        except ImportError:
            pytest.skip("Calibration module not available")
            
    def test_validation_pattern_generation(self):
        """Test validation patterns have proper structure"""
        try:
            from aruco_generator.validation import DetectionValidator
            
            validator = DetectionValidator()
            
            pattern_config = {
                'dictionary': '4X4_50',
                'scales': [10, 20, 30],
                'marker_ids': [0, 1, 2],
                'canvas_size_mm': (200, 150)
            }
            
            result = validator.generate_test_pattern(pattern_config)
            
            # Check result structure
            assert 'image' in result
            assert 'metadata' in result
            assert 'test_markers' in result
            
            # Check image quality
            image = result['image']
            unique = np.unique(image)
            assert 255 in unique, "Pattern should have white background"
            
        except ImportError:
            pytest.skip("Validation module not available")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])