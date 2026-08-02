"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_export_snapshots.py</name>
    <version>1.1.0</version>
    <type>test_suite</type>
    <purpose>Snapshot SVG, PDF ruler, and LightBurn export output</purpose>
    <last_updated>2026-08-01</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Snapshot tests for export outputs to prevent regressions.
"""

import base64
import os
import re
import zlib

from aruco_generator.core.aruco import ArUCOGenerator
from aruco_generator.core.drawing import DrawingContext
from aruco_generator.export.exporters import PDFExporter
from aruco_generator.export.lightburn import LightBurnExporter

SNAP_DIR = os.path.join(os.path.dirname(__file__), "snapshots")


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _pdf_ruler_block(pdf_bytes: bytes) -> str:
    """Extract the final saved-state block containing ruler geometry."""
    streams = []
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.DOTALL):
        data = match.group(1).strip()
        if data.endswith(b"~>"):
            data = base64.a85decode(data[:-2])
        try:
            data = zlib.decompress(data)
        except zlib.error:
            pass
        streams.append(data.decode("latin1"))

    blocks = re.findall(r"(?:^|\n)(q\n.*?\nQ)(?:\n|$)", "\n".join(streams), re.DOTALL)
    assert blocks, "PDF snapshot must contain a saved ruler block"
    return blocks[-1] + "\n"


def test_svg_preview_snapshot():
    aruco = ArUCOGenerator()
    markers = aruco.generate_grid(
        start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=20, spacing_mm=5
    )

    ctx = DrawingContext()
    ctx.add_marker_grid_preview(markers, include_borders=True)
    svg = ctx.get_svg()

    expected = _read_text(os.path.join(SNAP_DIR, "preview_basic.svg"))
    assert svg == expected


def test_svg_scale_ruler_snapshot():
    aruco = ArUCOGenerator()
    markers = aruco.generate_grid(
        start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=110, spacing_mm=0
    )

    ctx = DrawingContext()
    ctx.add_marker_grid(markers, include_borders=True)
    assert ctx.add_scale_ruler() is True

    expected = _read_text(os.path.join(SNAP_DIR, "scale_ruler.svg"))
    assert ctx.get_svg() == expected


def test_pdf_scale_ruler_snapshot():
    aruco = ArUCOGenerator()
    markers = aruco.generate_grid(
        start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=110, spacing_mm=0
    )

    pdf = PDFExporter().generate_pdf(markers, 110)

    expected = _read_text(os.path.join(SNAP_DIR, "scale_ruler_pdf.txt"))
    assert _pdf_ruler_block(pdf) == expected


def test_lightburn_snapshot():
    aruco = ArUCOGenerator()
    markers = aruco.generate_grid(
        start_id=0, dict_name="4X4_50", rows=1, cols=1, size_mm=20, spacing_mm=5
    )

    ctx = DrawingContext()
    ctx.add_marker_grid(markers, include_borders=True)

    exporter = LightBurnExporter()
    output = exporter.export(
        ctx,
        {
            "dictionary": "4X4_50",
            "start_id": 0,
            "rows": 1,
            "cols": 1,
            "size_mm": 20,
            "spacing_mm": 5,
        },
    )

    expected = _read_bytes(os.path.join(SNAP_DIR, "lightburn_basic.lbrn2"))
    assert output.getvalue() == expected
