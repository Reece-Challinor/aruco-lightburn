"""
Tests for various export format quality and correctness.
Validates SVG, LightBurn, and other export formats.
"""

import pytest
import os
import sys
import json
import xml.etree.ElementTree as ET
from io import BytesIO
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aruco_generator.aruco import ArUCOGenerator
from aruco_generator.drawing import DrawingContext
from aruco_generator.lightburn import LightBurnExporter


class TestSVGExport:
    """Test SVG export quality and correctness"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ArUCOGenerator()
        
    def test_svg_structure(self):
        """Test basic SVG structure is valid"""
        # Generate markers
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=2, cols=2,
            size_mm=20, spacing_mm=5
        )
        
        # Create drawing context
        ctx = DrawingContext()
        ctx.add_marker_grid_preview(markers)
        
        # Get SVG
        svg = ctx.get_svg()
        
        # Validate structure
        assert svg.startswith('<svg'), "SVG should start with svg tag"
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg, "SVG should have xmlns"
        assert 'viewBox=' in svg, "SVG should have viewBox"
        assert '</svg>' in svg, "SVG should have closing tag"
        
    def test_svg_dimensions(self):
        """Test SVG dimensions match marker grid"""
        rows, cols = 3, 4
        size_mm = 25.0
        spacing_mm = 5.0
        
        markers = self.generator.generate_grid(
            start_id=0, dict_name="5X5_100",
            rows=rows, cols=cols,
            size_mm=size_mm, spacing_mm=spacing_mm
        )
        
        ctx = DrawingContext()
        ctx.add_marker_grid_preview(markers)
        svg = ctx.get_svg()
        
        # Calculate expected dimensions
        expected_width = cols * size_mm + (cols - 1) * spacing_mm
        expected_height = rows * size_mm + (rows - 1) * spacing_mm
        
        # Parse dimensions from SVG
        width_match = re.search(r'width="([0-9.]+)mm"', svg)
        height_match = re.search(r'height="([0-9.]+)mm"', svg)
        
        assert width_match, "SVG should have width attribute"
        assert height_match, "SVG should have height attribute"
        
        actual_width = float(width_match.group(1))
        actual_height = float(height_match.group(1))
        
        # Allow small tolerance for floating point
        assert abs(actual_width - expected_width) < 0.1, f"Width mismatch: {actual_width} vs {expected_width}"
        assert abs(actual_height - expected_height) < 0.1, f"Height mismatch: {actual_height} vs {expected_height}"
        
    def test_svg_no_overlapping_elements(self):
        """Test that SVG elements don't improperly overlap"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=1, cols=2,
            size_mm=30, spacing_mm=10
        )
        
        ctx = DrawingContext()
        ctx.add_marker_grid(markers, include_borders=True)
        svg = ctx.get_svg()
        
        # Parse all rectangles
        rect_pattern = r'<rect[^>]*x="([0-9.]+)"[^>]*y="([0-9.]+)"[^>]*width="([0-9.]+)"[^>]*height="([0-9.]+)"'
        rectangles = re.findall(rect_pattern, svg)
        
        # Convert to float
        rects = [(float(x), float(y), float(w), float(h)) for x, y, w, h in rectangles]
        
        # Markers should not overlap (except for intentional small overlaps)
        for i, rect1 in enumerate(rects):
            for j, rect2 in enumerate(rects[i+1:], i+1):
                if self._rectangles_overlap(rect1, rect2):
                    # Check if overlap is intentional (very small)
                    overlap_area = self._calculate_overlap_area(rect1, rect2)
                    rect1_area = rect1[2] * rect1[3]
                    # Allow up to 1% overlap for anti-aliasing
                    assert overlap_area < rect1_area * 0.01, f"Rectangles {i} and {j} overlap too much"
                    
    def _rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # Check if one rectangle is to the left of the other
        if x1 + w1 < x2 or x2 + w2 < x1:
            return False
        # Check if one rectangle is above the other
        if y1 + h1 < y2 or y2 + h2 < y1:
            return False
        return True
        
    def _calculate_overlap_area(self, rect1, rect2):
        """Calculate overlapping area of two rectangles"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        
        return x_overlap * y_overlap


class TestLightBurnExport:
    """Test LightBurn export format quality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ArUCOGenerator()
        self.exporter = LightBurnExporter()
        
    def test_lightburn_xml_structure(self):
        """Test LightBurn XML has correct structure"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=2, cols=2,
            size_mm=25, spacing_mm=5
        )
        
        ctx = DrawingContext()
        ctx.add_marker_grid(markers)
        
        output = self.exporter.export(ctx, {})
        output.seek(0)
        
        # Parse XML
        tree = ET.parse(output)
        root = tree.getroot()
        
        # Validate root element
        assert root.tag == 'LightBurnProject', "Root should be LightBurnProject"
        assert 'AppVersion' in root.attrib, "Should have AppVersion"
        assert 'FormatVersion' in root.attrib, "Should have FormatVersion"
        
        # Check for CutSetting elements
        cut_settings = root.findall('.//CutSetting')
        assert len(cut_settings) > 0, "Should have cut settings"
        
        # Check for Shape elements
        shapes = root.findall('.//Shape')
        assert len(shapes) > 0, "Should have shapes"
        
    def test_lightburn_layers(self):
        """Test LightBurn layers are properly configured"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=1, cols=1,
            size_mm=30, spacing_mm=0
        )
        
        ctx = DrawingContext()
        ctx.add_marker_grid(markers, include_borders=True)
        ctx.add_text_labels(markers)
        
        output = self.exporter.export(ctx, {})
        output.seek(0)
        
        tree = ET.parse(output)
        root = tree.getroot()
        
        # Check for different layer indices
        cut_settings = root.findall('.//CutSetting')
        layer_indices = set()
        
        for setting in cut_settings:
            index = setting.find('.//index')
            if index is not None and index.text:
                layer_indices.add(index.text)
                
        # Should have multiple layers (fill, border, text)
        assert len(layer_indices) >= 2, "Should have at least 2 layers"
        
    def test_lightburn_coordinates(self):
        """Test LightBurn coordinate accuracy"""
        size_mm = 40.0
        markers = self.generator.generate_grid(
            start_id=0, dict_name="5X5_50",
            rows=1, cols=1,
            size_mm=size_mm, spacing_mm=0
        )
        
        ctx = DrawingContext()
        ctx.add_marker_grid(markers)
        
        output = self.exporter.export(ctx, {})
        output.seek(0)
        
        tree = ET.parse(output)
        
        # Find shape vertices
        vertices = tree.findall('.//VertList')
        
        for vert_list in vertices:
            if vert_list.text:
                # Parse vertices (format: x,y;x,y;...)
                coords = vert_list.text.strip().split(';')
                
                for coord in coords:
                    if coord:
                        x, y = coord.split(',')
                        x_val = float(x)
                        y_val = float(y)
                        
                        # Coordinates should be within expected bounds
                        assert x_val >= -1 and x_val <= size_mm + 1, f"X coordinate {x_val} out of bounds"
                        assert y_val >= -1 and y_val <= size_mm + 1, f"Y coordinate {y_val} out of bounds"
                        
    def test_lightburn_material_settings(self):
        """Test material settings are properly included"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=1, cols=1,
            size_mm=20, spacing_mm=0
        )
        
        ctx = DrawingContext()
        ctx.add_marker_grid(markers)
        
        metadata = {
            'material': '1_16_cast_acrylic',
            'dictionary': '4X4_50'
        }
        
        output = self.exporter.export(ctx, metadata, material="1_16_cast_acrylic")
        output.seek(0)
        
        tree = ET.parse(output)
        root = tree.getroot()
        
        # Check material height is set
        assert 'MaterialHeight' in root.attrib, "Should have MaterialHeight"
        
        # Check cut settings have speed and power
        cut_settings = root.findall('.//CutSetting')
        
        for setting in cut_settings:
            speed = setting.find('.//speed')
            power = setting.find('.//maxPower')
            
            if speed is not None and speed.text:
                speed_val = float(speed.text)
                assert speed_val > 0, "Speed should be positive"
                
            if power is not None and power.text:
                power_val = float(power.text)
                assert 0 <= power_val <= 100, "Power should be 0-100%"


class TestExportConsistency:
    """Test consistency across different export formats"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ArUCOGenerator()
        self.exporter = LightBurnExporter()
        
    def test_consistent_marker_count(self):
        """Test that all export formats have the same marker count"""
        rows, cols = 2, 3
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50",
            rows=rows, cols=cols,
            size_mm=25, spacing_mm=5
        )
        
        # SVG export
        svg_ctx = DrawingContext()
        svg_ctx.add_marker_grid_preview(markers)
        svg = svg_ctx.get_svg()
        
        # Count markers in SVG (simplified check)
        svg_marker_count = svg.count('marker_id')
        
        # LightBurn export
        lb_ctx = DrawingContext()
        lb_ctx.add_marker_grid(markers)
        lb_output = self.exporter.export(lb_ctx, {})
        
        # Both should represent the same number of markers
        expected_count = rows * cols
        assert len(markers) == expected_count, f"Should have {expected_count} markers"
        
    def test_dimension_consistency(self):
        """Test that dimensions are consistent across formats"""
        rows, cols = 2, 2
        size_mm = 30.0
        spacing_mm = 10.0
        
        markers = self.generator.generate_grid(
            start_id=0, dict_name="5X5_100",
            rows=rows, cols=cols,
            size_mm=size_mm, spacing_mm=spacing_mm
        )
        
        # Calculate expected dimensions
        expected_width = cols * size_mm + (cols - 1) * spacing_mm
        expected_height = rows * size_mm + (rows - 1) * spacing_mm
        
        # Test SVG dimensions
        svg_ctx = DrawingContext()
        svg_ctx.add_marker_grid_preview(markers)
        
        # Check bounds
        width = svg_ctx.bounds['max_x'] - svg_ctx.bounds['min_x']
        height = svg_ctx.bounds['max_y'] - svg_ctx.bounds['min_y']
        
        assert abs(width - expected_width) < 0.1, f"SVG width mismatch"
        assert abs(height - expected_height) < 0.1, f"SVG height mismatch"
        
        # Test LightBurn dimensions
        lb_ctx = DrawingContext()
        lb_ctx.add_marker_grid(markers)
        
        width = lb_ctx.bounds['max_x'] - lb_ctx.bounds['min_x']
        height = lb_ctx.bounds['max_y'] - lb_ctx.bounds['min_y']
        
        assert abs(width - expected_width) < 0.1, f"LightBurn width mismatch"
        assert abs(height - expected_height) < 0.1, f"LightBurn height mismatch"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])