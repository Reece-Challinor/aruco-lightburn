"""
Snapshot tests for export outputs to prevent regressions.
"""

import os

from aruco_generator.core.aruco import ArUCOGenerator
from aruco_generator.core.drawing import DrawingContext
from aruco_generator.export.lightburn import LightBurnExporter

SNAP_DIR = os.path.join(os.path.dirname(__file__), "snapshots")


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


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
