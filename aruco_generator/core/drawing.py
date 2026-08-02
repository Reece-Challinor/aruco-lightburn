"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>drawing.py</name>
    <version>1.2.0</version>
    <type>core_drawing_module</type>
    <purpose>SVG drawing, shared vector geometry, and print-scale ruler rendering</purpose>
    <last_updated>2026-08-01</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
{
  "file_type": "svg_drawing_context",
  "purpose": "SVG drawing, shared vector geometry, and print-scale ruler rendering",
  "last_updated": "2026-08-01",
  "dependencies": ["numpy"],
  "main_class": "DrawingContext",
  "key_functions": {
    "find_merged_rectangles": "Merge binary-image pixels into compact vector rectangles",
    "scale_ruler_fits": "Apply the shared 100mm ruler placement rule"
  },
  "key_methods": {
    "add_rectangle": "Add rectangle shapes to drawing context",
    "add_marker_grid": "Add ArUCO markers as filled rectangles",
    "add_scale_ruler": "Add a print-only 100mm verification ruler",
    "add_text": "Add a text element at a specific position",
    "add_text_labels": "Add text labels below markers",
    "get_svg": "Generate SVG preview output"
  },
  "ai_navigation": {
    "modify_for": "Adding new drawing elements or SVG features",
    "used_by": ["web.py", "lightburn.py"],
    "output_format": "SVG strings for web preview"
  }
}
"""

from typing import Any, Dict, List

import numpy as np

SCALE_RULER_LENGTH_MM = 100.0
SCALE_RULER_MIN_MARGIN_MM = 15.0
SCALE_RULER_SIDE_CLEARANCE_MM = 1.0
SCALE_RULER_CAPTION = (
    "Verify: this bar must measure exactly 100 mm / 'fit to page' breaks scale"
)


def scale_ruler_fits(
    content_width_mm: float,
    clear_margin_mm: float,
    length_mm: float = SCALE_RULER_LENGTH_MM,
) -> bool:
    """Return whether a ruler fits without overhanging or touching content."""
    return (
        content_width_mm + 1e-9 >= length_mm + (2 * SCALE_RULER_SIDE_CLEARANCE_MM)
        and clear_margin_mm + 1e-9 >= SCALE_RULER_MIN_MARGIN_MM
    )


def find_merged_rectangles(image: np.ndarray) -> List[Dict[str, int]]:
    """Merge contiguous black pixels of a binary image into rectangles.

    The shared implementation keeps SVG, LightBurn, and PDF vector geometry
    compact. In particular, PDF exports no longer emit one rectangle for each
    pixel in the marker raster.
    """
    rectangles = []
    visited = np.zeros_like(image, dtype=bool)

    for row in range(image.shape[0]):
        for col in range(image.shape[1]):
            if image[row, col] == 0 and not visited[row, col]:
                max_width = image.shape[1] - col
                max_height = image.shape[0] - row

                width = 0
                while (
                    width < max_width
                    and image[row, col + width] == 0
                    and not visited[row, col + width]
                ):
                    width += 1

                height = 1
                while height < max_height:
                    row_valid = True
                    for offset in range(width):
                        if (
                            image[row + height, col + offset] != 0
                            or visited[row + height, col + offset]
                        ):
                            row_valid = False
                            break
                    if not row_valid:
                        break
                    height += 1

                visited[row : row + height, col : col + width] = True
                rectangles.append(
                    {"row": row, "col": col, "width": width, "height": height}
                )

    return rectangles


class DrawingContext:
    def __init__(self):
        self.elements = []
        self.bounds = {
            "min_x": float("inf"),
            "min_y": float("inf"),
            "max_x": float("-inf"),
            "max_y": float("-inf"),
        }

    def add_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: bool = True,
        layer: int = 0,
        marker_id: int | None = None,
    ):
        """Add rectangle to drawing context"""
        element = {
            "type": "rect",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "fill": fill,
            "layer": layer,
        }
        if marker_id is not None:
            element["marker_id"] = marker_id

        self.elements.append(element)
        self._update_bounds(x, y, width, height)

    def add_marker_grid(
        self,
        markers: List[Dict[str, Any]],
        include_borders: bool = True,
        include_outer_border: bool = False,
        border_width: float = 2.0,
    ):
        """Add ArUCO markers as filled rectangles with 2D optimization"""
        self._add_marker_grid_internal(
            markers=markers,
            include_borders=include_borders,
            include_outer_border=include_outer_border,
            border_width=border_width,
            allow_placeholder=True,
        )

    def add_marker_grid_preview(
        self,
        markers: List[Dict[str, Any]],
        include_borders: bool = True,
        include_outer_border: bool = False,
        border_width: float = 2.0,
    ):
        """Add ArUCO markers with optimized preview rendering"""
        self._add_marker_grid_internal(
            markers=markers,
            include_borders=include_borders,
            include_outer_border=include_outer_border,
            border_width=border_width,
            allow_placeholder=True,
        )

    def _add_marker_grid_internal(
        self,
        markers: List[Dict[str, Any]],
        include_borders: bool,
        include_outer_border: bool,
        border_width: float,
        allow_placeholder: bool,
    ):
        for marker in markers:
            size = marker["size"]
            x, y = marker["x"], marker["y"]
            marker_id = marker["id"]

            if include_borders:
                self.add_rectangle(
                    x, y, size, size, fill=False, layer=1, marker_id=marker_id
                )

            image = marker.get("image")
            if image is not None:
                self._add_marker_rectangles(image, x, y, size, marker_id)
            elif allow_placeholder:
                self.elements.append(
                    {
                        "type": "marker_placeholder",
                        "x": x,
                        "y": y,
                        "width": size,
                        "height": size,
                        "marker_id": marker_id,
                        "layer": 0,
                    }
                )

            self._update_bounds(x, y, size, size)

        if include_outer_border and markers:
            self._add_outer_border(markers, border_width)

    def _add_marker_rectangles(
        self, image: np.ndarray, x: float, y: float, size: float, marker_id: int
    ):
        pixel_size = size / image.shape[0]
        rectangles = self._find_merged_rectangles(image)

        for rect in rectangles:
            px_x = x + rect["col"] * pixel_size
            px_y = y + rect["row"] * pixel_size
            width = rect["width"] * pixel_size
            height = rect["height"] * pixel_size

            overlap = min(0.05, max(width * 0.005, height * 0.005))
            self.add_rectangle(
                px_x,
                px_y,
                width + overlap,
                height + overlap,
                fill=True,
                layer=0,
                marker_id=marker_id,
            )

    def _add_outer_border(self, markers: List[Dict[str, Any]], border_width: float):
        min_x = min(float(marker["x"]) for marker in markers)
        min_y = min(float(marker["y"]) for marker in markers)
        max_x = max(float(marker["x"] + marker["size"]) for marker in markers)
        max_y = max(float(marker["y"] + marker["size"]) for marker in markers)

        border_x = min_x - border_width
        border_y = min_y - border_width
        border_w = (max_x - min_x) + (2 * border_width)
        border_h = (max_y - min_y) + (2 * border_width)

        self.add_rectangle(border_x, border_y, border_w, border_h, fill=False, layer=1)

    def add_text_labels(self, markers: List[Dict[str, Any]], font_size: float = 3.0):
        """Add text labels below each marker"""
        import html

        for marker in markers:
            x = marker["x"]
            y = marker["y"] + marker["size"] + font_size
            # Escape HTML/XML special characters to prevent XSS
            text = f"ID: {html.escape(str(marker['id']))}"

            self.elements.append(
                {
                    "type": "text",
                    "x": x,
                    "y": y,
                    "text": text,
                    "font_size": font_size,
                    "layer": 2,
                    "marker_id": marker["id"],
                }
            )

    def add_text(
        self,
        text: str,
        x: float,
        y: float,
        font_size: float = 3.0,
        layer: int = 2,
    ):
        """Add a text element at an arbitrary position."""
        import html

        self.elements.append(
            {
                "type": "text",
                "x": x,
                "y": y,
                "text": html.escape(str(text)),
                "font_size": font_size,
                "layer": layer,
            }
        )

    def add_scale_ruler(
        self,
        clear_margin_mm: float = SCALE_RULER_MIN_MARGIN_MM,
        length_mm: float = SCALE_RULER_LENGTH_MM,
    ) -> bool:
        """Add a calibrated print-only ruler below the current content.

        A ruler is added only when both the content width and the clear margin
        meet the shared placement rule. The dedicated element type is rendered
        by SVG only; LightBurn ignores it, so reference geometry cannot leak
        into a cut path.
        """
        if self.bounds["min_x"] == float("inf"):
            return False

        content_width = self.bounds["max_x"] - self.bounds["min_x"]
        if not scale_ruler_fits(content_width, clear_margin_mm, length_mm):
            return False

        x = self.bounds["min_x"] + (content_width - length_mm) / 2
        y = self.bounds["max_y"]
        self.elements.append(
            {
                "type": "scale_ruler",
                "x": x,
                "y": y,
                "length": length_mm,
                "caption": SCALE_RULER_CAPTION,
            }
        )
        self._update_bounds(x, y, length_mm, clear_margin_mm)
        return True

    def _update_bounds(self, x: float, y: float, width: float, height: float):
        """Update drawing bounds"""
        self.bounds["min_x"] = min(self.bounds["min_x"], x)
        self.bounds["min_y"] = min(self.bounds["min_y"], y)
        self.bounds["max_x"] = max(self.bounds["max_x"], x + width)
        self.bounds["max_y"] = max(self.bounds["max_y"], y + height)

    def _find_merged_rectangles(self, image: np.ndarray) -> List[Dict[str, int]]:
        """Find merged rectangles in binary image using 2D merging"""
        return find_merged_rectangles(image)

    def get_svg(self) -> str:
        """Generate SVG preview"""
        # Handle case where no elements have been added
        if self.bounds["min_x"] == float("inf"):
            return '<svg width="100mm" height="100mm" xmlns="http://www.w3.org/2000/svg"><text x="50" y="50" text-anchor="middle">No markers</text></svg>\n'

        width = self.bounds["max_x"] - self.bounds["min_x"]
        height = self.bounds["max_y"] - self.bounds["min_y"]

        svg = f"""<svg width="{width:.1f}mm" height="{height:.1f}mm"
                       viewBox="{self.bounds['min_x']:.1f} {self.bounds['min_y']:.1f} {width:.1f} {height:.1f}"
                       xmlns="http://www.w3.org/2000/svg">
                  <style>
                    .cut {{ fill: black; stroke: none; }}
                    .mark {{ fill: none; stroke: blue; stroke-width: 0.1; }}
                    .text {{ fill: red; font-family: Arial; font-size: 3px; }}
                    .marker {{ fill: black; stroke: none; }}
                    .marker-bg {{ fill: white; stroke: black; stroke-width: 0.1; }}
                  </style>"""

        for element in self.elements:
            if element["type"] == "rect":
                if element["fill"]:
                    css_class = "cut"
                else:
                    css_class = "mark"

                svg += f"""<rect x="{element['x']:.3f}" y="{element['y']:.3f}"
                               width="{element['width']:.3f}" height="{element['height']:.3f}"
                               class="{css_class}" />"""
            elif element["type"] == "marker_placeholder":
                # Render a simplified representation of the ArUCO marker
                x, y = element["x"], element["y"]
                size = element["width"]
                marker_id = element["marker_id"]

                # Add white background
                svg += f"""<rect x="{x:.3f}" y="{y:.3f}"
                               width="{size:.3f}" height="{size:.3f}"
                               class="marker-bg" />"""

                # Add simplified pattern to represent ArUCO marker
                pattern_size = size / 6
                for i in range(6):
                    for j in range(6):
                        if (i + j) % 2 == 0:  # Checkerboard pattern
                            px = x + i * pattern_size
                            py = y + j * pattern_size
                            svg += f"""<rect x="{px:.3f}" y="{py:.3f}"
                                           width="{pattern_size:.3f}" height="{pattern_size:.3f}"
                                           class="marker" />"""

                # Add ID text in center
                center_x = x + size / 2
                center_y = y + size / 2
                svg += f"""<text x="{center_x:.3f}" y="{center_y:.3f}"
                               text-anchor="middle" dominant-baseline="central"
                               style="fill: red; font-family: Arial; font-size: {size / 10:.1f}px; font-weight: bold;">{marker_id}</text>"""

            elif element["type"] == "scale_ruler":
                import html

                x = element["x"]
                y = element["y"]
                length = element["length"]
                bar_y = y + 6.0
                caption_y = y + 13.0
                tick_path = " ".join(
                    f"M {x + tick:.3f} {bar_y:.3f} V {bar_y + 3.0:.3f}"
                    for tick in range(0, int(length) + 1, 10)
                )
                caption = html.escape(str(element["caption"]))

                svg += f"""<path d="M {x:.3f} {bar_y:.3f} H {x + length:.3f}"
                               class="scale-ruler-bar" fill="none" stroke="black"
                               stroke-width="0.8" stroke-linecap="butt" />"""
                svg += f"""<path d="{tick_path}"
                               class="scale-ruler-ticks" fill="none" stroke="black"
                               stroke-width="0.3" />"""
                svg += f"""<text x="{x + length / 2:.3f}" y="{caption_y:.3f}"
                               class="scale-ruler-caption" text-anchor="middle"
                               style="fill: #333333; font-family: Arial; font-size: 3px;">{caption}</text>"""

            elif element["type"] == "text":
                svg += f"""<text x="{element['x']:.3f}" y="{element['y']:.3f}"
                               class="text">{element['text']}</text>"""

        svg += "</svg>\n"
        return svg
