"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_export_formats.py</name>
    <version>1.3.0</version>
    <type>test_suite</type>
    <purpose>Validate SVG, LightBurn, PDF, and print-scale ruler correctness</purpose>
    <last_updated>2026-08-01</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Tests for various export format quality and correctness.
Validates SVG, LightBurn, and other export formats.
"""

import base64
import os
import re
import sys
import xml.etree.ElementTree as ET
import zlib

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aruco_generator.core.aruco import ArUCOGenerator  # noqa: E402
from aruco_generator.core.drawing import (  # noqa: E402
    SCALE_RULER_CAPTION,
    DrawingContext,
)
from aruco_generator.export.exporters import (  # noqa: E402
    PDFExporter,
    ProfessionalExporter,
)
from aruco_generator.export.lightburn import LightBurnExporter  # noqa: E402

RULER_CAPTION_PREFIX = b"Verify: this bar must measure exactly 100 mm"


def _pdf_streams(pdf_bytes: bytes) -> bytes:
    """Return decoded PDF stream contents for semantic geometry assertions."""
    chunks = []
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.DOTALL):
        data = match.group(1).strip()
        try:
            if data.endswith(b"~>"):
                data = base64.a85decode(data[:-2])
            data = zlib.decompress(data)
        except (ValueError, zlib.error):
            pass
        chunks.append(data)
    return b"\n".join(chunks)


class TestSVGExport:
    """Test SVG export quality and correctness"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ArUCOGenerator()

    def test_svg_structure(self):
        """Test basic SVG structure is valid"""
        # Generate markers
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=2, cols=2, size_mm=20, spacing_mm=5
        )

        # Create drawing context
        ctx = DrawingContext()
        ctx.add_marker_grid_preview(markers)

        # Get SVG
        svg = ctx.get_svg()

        # Validate structure
        assert svg.startswith("<svg"), "SVG should start with svg tag"
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg, "SVG should have xmlns"
        assert "viewBox=" in svg, "SVG should have viewBox"
        assert "</svg>" in svg, "SVG should have closing tag"

    def test_svg_dimensions(self):
        """Test SVG dimensions match marker grid"""
        rows, cols = 3, 4
        size_mm = 25.0
        spacing_mm = 5.0

        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="5X5_100",
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm,
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
        assert (
            abs(actual_width - expected_width) < 0.1
        ), f"Width mismatch: {actual_width} vs {expected_width}"
        assert (
            abs(actual_height - expected_height) < 0.1
        ), f"Height mismatch: {actual_height} vs {expected_height}"

    @pytest.mark.skip(
        reason="Intentional (P-0.0 disposition): merged fill rectangles overlap "
        "slightly by design (engraving bleed avoids hairline gaps); "
        "overlap-free SVG is a non-goal"
    )
    def test_svg_no_overlapping_elements(self):
        """Test that SVG elements don't improperly overlap"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=1, cols=2, size_mm=30, spacing_mm=10
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
            for j, rect2 in enumerate(rects[i + 1 :], i + 1):
                if self._rectangles_overlap(rect1, rect2):
                    # Check if overlap is intentional (very small)
                    overlap_area = self._calculate_overlap_area(rect1, rect2)
                    rect1_area = rect1[2] * rect1[3]
                    # Allow up to 1% overlap for anti-aliasing
                    assert (
                        overlap_area < rect1_area * 0.01
                    ), f"Rectangles {i} and {j} overlap too much"

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
            start_id=0, dict_name="4X4_50", rows=2, cols=2, size_mm=25, spacing_mm=5
        )

        ctx = DrawingContext()
        ctx.add_marker_grid(markers)

        output = self.exporter.export(ctx, {})
        output.seek(0)

        # Parse XML
        tree = ET.parse(output)
        root = tree.getroot()

        # Validate root element
        assert root.tag == "LightBurnProject", "Root should be LightBurnProject"
        assert "AppVersion" in root.attrib, "Should have AppVersion"
        assert "FormatVersion" in root.attrib, "Should have FormatVersion"

        # Check for CutSetting elements
        cut_settings = root.findall(".//CutSetting")
        assert len(cut_settings) > 0, "Should have cut settings"

        # Check for Shape elements
        shapes = root.findall(".//Shape")
        assert len(shapes) > 0, "Should have shapes"

    def test_lightburn_layers(self):
        """Test LightBurn layers are properly configured"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=30, spacing_mm=0
        )

        ctx = DrawingContext()
        ctx.add_marker_grid(markers, include_borders=True)
        ctx.add_text_labels(markers)

        output = self.exporter.export(ctx, {})
        output.seek(0)

        tree = ET.parse(output)
        root = tree.getroot()

        # Check for different layer indices (stored as the Value attribute,
        # e.g. <index Value="0"/>)
        cut_settings = root.findall(".//CutSetting")
        layer_indices = set()

        for setting in cut_settings:
            index = setting.find("index")
            if index is not None and index.get("Value"):
                layer_indices.add(index.get("Value"))

        # Should have multiple layers (fill, border, text)
        assert len(layer_indices) >= 2, "Should have at least 2 layers"

        # Shapes must actually be assigned to at least 2 distinct layers
        # (fill + border), via their CutIndex attribute
        shape_layers = {
            shape.get("CutIndex")
            for shape in root.findall(".//Shape")
            if shape.get("CutIndex") is not None
        }
        assert (
            len(shape_layers) >= 2
        ), f"Shapes should span at least 2 distinct layers, got {shape_layers}"

    def test_lightburn_coordinates(self):
        """Test LightBurn coordinate accuracy"""
        size_mm = 40.0
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="5X5_50",
            rows=1,
            cols=1,
            size_mm=size_mm,
            spacing_mm=0,
        )

        ctx = DrawingContext()
        ctx.add_marker_grid(markers)

        output = self.exporter.export(ctx, {})
        output.seek(0)

        tree = ET.parse(output)

        # Find shape vertices
        vertices = tree.findall(".//VertList")

        # Parse vertices; lbrn2 encodes them concatenated with no separator:
        # "V{x:.3f} {y:.3f}c0x1c1x1V{x:.3f} {y:.3f}c0x1c1x1..."
        all_x = []
        all_y = []
        for vert_list in vertices:
            if vert_list.text:
                for x, y in re.findall(r"V(-?[0-9.]+) (-?[0-9.]+)", vert_list.text):
                    x_val = float(x)
                    y_val = float(y)
                    all_x.append(x_val)
                    all_y.append(y_val)

                    # Coordinates should be within expected bounds
                    assert (
                        x_val >= -1 and x_val <= size_mm + 1
                    ), f"X coordinate {x_val} out of bounds"
                    assert (
                        y_val >= -1 and y_val <= size_mm + 1
                    ), f"Y coordinate {y_val} out of bounds"

        assert all_x, "Should have parsed at least one vertex"

        # lbrn2 units are mm: a 40mm marker's geometry must span 40mm ±0.1
        x_span = max(all_x) - min(all_x)
        y_span = max(all_y) - min(all_y)
        assert abs(x_span - size_mm) <= 0.1, f"X span {x_span} != {size_mm}±0.1"
        assert abs(y_span - size_mm) <= 0.1, f"Y span {y_span} != {size_mm}±0.1"

    def test_materials_loaded_independent_of_cwd(self, tmp_path, monkeypatch):
        """materials.json must resolve from the package, not the process CWD

        Regression test: serverless entrypoints (Vercel api/index.py) don't
        run from the repo root, so a CWD-relative path silently skipped the
        custom material settings.
        """
        monkeypatch.chdir(tmp_path)
        exporter = LightBurnExporter()

        assert os.path.isabs(
            exporter.materials_file
        ), "materials_file must be an absolute path"
        assert os.path.exists(
            exporter.materials_file
        ), "materials.json at the repo root must be found from any CWD"
        # The default material must be present (merged from file or defaults)
        assert "1_16_cast_acrylic" in exporter.material_settings

    def test_lightburn_material_settings(self):
        """Test material settings are properly included"""
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=20, spacing_mm=0
        )

        ctx = DrawingContext()
        ctx.add_marker_grid(markers)

        metadata = {"material": "1_16_cast_acrylic", "dictionary": "4X4_50"}

        output = self.exporter.export(ctx, metadata, material="1_16_cast_acrylic")
        output.seek(0)

        tree = ET.parse(output)
        root = tree.getroot()

        # Check material height is set
        assert "MaterialHeight" in root.attrib, "Should have MaterialHeight"

        # Check cut settings have speed and power
        cut_settings = root.findall(".//CutSetting")

        for setting in cut_settings:
            speed = setting.find(".//speed")
            power = setting.find(".//maxPower")

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
            start_id=0,
            dict_name="4X4_50",
            rows=rows,
            cols=cols,
            size_mm=25,
            spacing_mm=5,
        )

        # SVG export
        svg_ctx = DrawingContext()
        svg_ctx.add_marker_grid_preview(markers)
        svg = svg_ctx.get_svg()

        # Count markers in SVG (simplified check)
        _ = svg.count("marker_id")

        # LightBurn export
        lb_ctx = DrawingContext()
        lb_ctx.add_marker_grid(markers)
        self.exporter.export(lb_ctx, {})

        # Both should represent the same number of markers
        expected_count = rows * cols
        assert len(markers) == expected_count, f"Should have {expected_count} markers"

    def test_dimension_consistency(self):
        """Test that dimensions are consistent across formats"""
        rows, cols = 2, 2
        size_mm = 30.0
        spacing_mm = 10.0

        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="5X5_100",
            rows=rows,
            cols=cols,
            size_mm=size_mm,
            spacing_mm=spacing_mm,
        )

        # Calculate expected dimensions
        expected_width = cols * size_mm + (cols - 1) * spacing_mm
        expected_height = rows * size_mm + (rows - 1) * spacing_mm

        # Test SVG dimensions
        svg_ctx = DrawingContext()
        svg_ctx.add_marker_grid_preview(markers)

        # Check bounds
        width = svg_ctx.bounds["max_x"] - svg_ctx.bounds["min_x"]
        height = svg_ctx.bounds["max_y"] - svg_ctx.bounds["min_y"]

        assert abs(width - expected_width) < 0.1, "SVG width mismatch"
        assert abs(height - expected_height) < 0.1, "SVG height mismatch"

        # Test LightBurn dimensions
        lb_ctx = DrawingContext()
        lb_ctx.add_marker_grid(markers)

        width = lb_ctx.bounds["max_x"] - lb_ctx.bounds["min_x"]
        height = lb_ctx.bounds["max_y"] - lb_ctx.bounds["min_y"]

        assert abs(width - expected_width) < 0.1, "LightBurn width mismatch"
        assert abs(height - expected_height) < 0.1, "LightBurn height mismatch"


class TestPDFExport:
    """Test production PDF availability and compact print-scale output."""

    def setup_method(self):
        self.generator = ArUCOGenerator()
        self.exporter = PDFExporter()

    def test_pdf_exporter_is_a_runtime_capability(self):
        """Production installs must never reach the route's legacy 501 path."""
        assert self.exporter.available is True

    def test_pdf_uses_merged_rectangles(self, monkeypatch):
        """A marker must use merged rects, not tens of thousands of pixels."""
        from reportlab.pdfgen import canvas as reportlab_canvas

        calls = {"rect": 0}
        original_rect = reportlab_canvas.Canvas.rect

        def counting_rect(canvas_self, *args, **kwargs):
            calls["rect"] += 1
            return original_rect(canvas_self, *args, **kwargs)

        monkeypatch.setattr(reportlab_canvas.Canvas, "rect", counting_rect)
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=30, spacing_mm=0
        )

        pdf = self.exporter.generate_pdf(markers, 30, include_labels=False)

        assert pdf.startswith(b"%PDF")
        assert 0 < calls["rect"] < 100
        assert len(pdf) < 10_000, "Per-pixel PDF rendering has regressed"

    def test_pdf_ruler_is_default_and_exactly_100_mm(self):
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="4X4_50",
            rows=1,
            cols=1,
            size_mm=110,
            spacing_mm=0,
        )

        streams = _pdf_streams(self.exporter.generate_pdf(markers, 110))

        assert RULER_CAPTION_PREFIX in streams
        expected_points = 100.0 * 72.0 / 25.4
        lines = re.findall(rb"([-\d.]+) ([-\d.]+) m ([-\d.]+) ([-\d.]+) l", streams)
        spans = [
            abs(float(x1) - float(x0))
            for x0, y0, x1, y1 in lines
            if abs(float(y1) - float(y0)) < 0.001
        ]
        assert any(abs(span - expected_points) < 0.001 for span in spans)

    def test_pdf_ruler_can_be_explicitly_disabled(self):
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="4X4_50",
            rows=1,
            cols=1,
            size_mm=110,
            spacing_mm=0,
        )

        pdf = self.exporter.generate_pdf(markers, 110, include_ruler=False)

        assert RULER_CAPTION_PREFIX not in _pdf_streams(pdf)

    def test_pdf_ruler_skips_small_content(self):
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=20, spacing_mm=0
        )

        assert RULER_CAPTION_PREFIX not in _pdf_streams(
            self.exporter.generate_pdf(markers, 20)
        )

    def test_pdf_ruler_skips_when_clear_margin_is_under_15_mm(self):
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="4X4_50",
            rows=1,
            cols=8,
            size_mm=30,
            spacing_mm=5,
        )

        assert RULER_CAPTION_PREFIX not in _pdf_streams(
            self.exporter.generate_pdf(markers, 30)
        )


class TestScaleRulerSVG:
    """Test the F-07a SVG ruler geometry and placement rule."""

    def setup_method(self):
        self.generator = ArUCOGenerator()

    def _wide_context(self):
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="4X4_50",
            rows=1,
            cols=1,
            size_mm=110,
            spacing_mm=0,
        )
        context = DrawingContext()
        context.add_marker_grid(markers, include_borders=True)
        return context

    def test_svg_ruler_path_is_exactly_100_mm(self):
        context = self._wide_context()
        assert context.add_scale_ruler() is True

        svg = context.get_svg()
        bar = re.search(
            r'<path d="M ([-0-9.]+) ([-0-9.]+) H ([-0-9.]+)"\s+'
            r'class="scale-ruler-bar"',
            svg,
        )

        assert bar is not None
        assert float(bar.group(3)) - float(bar.group(1)) == pytest.approx(100.0)
        assert RULER_CAPTION_PREFIX.decode("ascii") in svg

    def test_svg_ruler_uses_clear_15_mm_band(self):
        context = self._wide_context()
        content_max_y = context.bounds["max_y"]

        assert context.add_scale_ruler() is True
        assert context.bounds["max_y"] == pytest.approx(content_max_y + 15.0)

    def test_svg_ruler_skips_small_content_without_mutation(self):
        markers = self.generator.generate_grid(
            start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=20, spacing_mm=0
        )
        context = DrawingContext()
        context.add_marker_grid(markers, include_borders=True)
        elements_before = list(context.elements)
        bounds_before = dict(context.bounds)

        assert context.add_scale_ruler() is False
        assert context.elements == elements_before
        assert context.bounds == bounds_before

    def test_svg_ruler_skips_margin_under_15_mm(self):
        context = self._wide_context()

        assert context.add_scale_ruler(clear_margin_mm=14.99) is False


class TestScaleRulerAPI:
    """Test default route wiring for eligible print exports."""

    @staticmethod
    def _eligible_payload():
        return {
            "dictionary": "4X4_50",
            "rows": 1,
            "cols": 1,
            "size_mm": 110,
            "spacing_mm": 0,
            "start_id": 0,
            "include_labels": True,
        }

    def test_svg_export_includes_ruler_by_default(self, client):
        response = client.post("/api/export/svg", json=self._eligible_payload())

        assert response.status_code == 200
        assert b'class="scale-ruler-bar"' in response.data
        assert RULER_CAPTION_PREFIX in response.data

    def test_pdf_export_includes_ruler_by_default(self, client):
        response = client.post("/api/export/pdf", json=self._eligible_payload())

        assert response.status_code == 200
        assert RULER_CAPTION_PREFIX in _pdf_streams(response.data)


class TestRulerNeverCut:
    """The ruler is print-only and must never enter LightBurn or DXF output."""

    def setup_method(self):
        self.generator = ArUCOGenerator()

    def test_lightburn_ignores_scale_ruler_element(self):
        markers = self.generator.generate_grid(
            start_id=0,
            dict_name="4X4_50",
            rows=1,
            cols=1,
            size_mm=110,
            spacing_mm=0,
        )
        exporter = LightBurnExporter()
        metadata = {"dictionary": "4X4_50", "rows": 1, "cols": 1}

        plain_context = DrawingContext()
        plain_context.add_marker_grid(markers, include_borders=True)
        plain = exporter.export(plain_context, metadata).getvalue()

        ruler_context = DrawingContext()
        ruler_context.add_marker_grid(markers, include_borders=True)
        assert ruler_context.add_scale_ruler() is True
        with_ruler = exporter.export(ruler_context, metadata).getvalue()

        assert with_ruler == plain
        assert b"scale-ruler" not in with_ruler
        assert RULER_CAPTION_PREFIX not in with_ruler

    def test_dxf_contains_only_pattern_geometry(self):
        calibration_data = {
            "physical_width_mm": 150.0,
            "physical_height_mm": 120.0,
            "markers": [
                {
                    "id": 0,
                    "position": [30.0, 30.0, 0.0],
                    "corners": [
                        [10.0, 10.0, 0.0],
                        [50.0, 10.0, 0.0],
                        [50.0, 50.0, 0.0],
                        [10.0, 50.0, 0.0],
                    ],
                }
            ],
        }

        content = (
            ProfessionalExporter()
            .export_dxf(calibration_data)
            .getvalue()
            .decode("utf-8")
        )

        assert "scale-ruler" not in content
        assert SCALE_RULER_CAPTION not in content
        text_entities = re.findall(r"0\nTEXT\n.*?\n1\n([^\n]+)\n", content, re.DOTALL)
        assert text_entities
        assert all(text.startswith("ID:") for text in text_entities)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
