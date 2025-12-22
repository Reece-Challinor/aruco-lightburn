"""
{
  "file_type": "svg_drawing_context",
  "purpose": "SVG drawing and rendering system for ArUCO markers",
  "dependencies": ["numpy"],
  "main_class": "DrawingContext",
  "key_methods": {
    "add_rectangle": "Add rectangle shapes to drawing context",
    "add_marker_grid": "Add ArUCO markers as filled rectangles",
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
        for marker in markers:
            size = marker["size"]
            x, y = marker["x"], marker["y"]
            marker_id = marker["id"]

            # Add border if requested
            if include_borders:
                self.add_rectangle(
                    x, y, size, size, fill=False, layer=1, marker_id=marker_id
                )

            # Check if we have actual image data or just placeholder
            if "image" in marker:
                # Use 2D rectangle merging for optimal XML size
                image = marker["image"]
                pixel_size = size / image.shape[0]

                # Find all black rectangles using 2D merging
                rectangles = self._find_merged_rectangles(image)

                # Add merged rectangles with overlap to prevent gaps
                for rect in rectangles:
                    # Calculate positions with proper precision
                    px_x = x + rect["col"] * pixel_size
                    px_y = y + rect["row"] * pixel_size
                    width = rect["width"] * pixel_size
                    height = rect["height"] * pixel_size

                    # Add small overlap to prevent gaps but maintain dimensions
                    # Use 0.5% of the rectangle size or 0.05mm, whichever is smaller
                    overlap = min(
                        0.05, max(width * 0.005, height * 0.005)
                    )  # Max 0.05mm, or 0.5% of size
                    self.add_rectangle(
                        px_x,
                        px_y,
                        width + overlap,
                        height + overlap,
                        fill=True,
                        layer=0,
                        marker_id=marker_id,
                    )
            else:
                # For preview, use simplified representation
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

            # Update bounds
            self._update_bounds(x, y, size, size)

        # Add outer border around entire grid if requested
        if include_outer_border and markers:
            # Calculate grid bounds
            min_x = min(float(marker["x"]) for marker in markers)
            min_y = min(float(marker["y"]) for marker in markers)
            max_x = max(float(marker["x"] + marker["size"]) for marker in markers)
            max_y = max(float(marker["y"] + marker["size"]) for marker in markers)

            # Add outer border rectangle
            border_x = min_x - border_width
            border_y = min_y - border_width
            border_w = (max_x - min_x) + (2 * border_width)
            border_h = (max_y - min_y) + (2 * border_width)

            self.add_rectangle(
                border_x, border_y, border_w, border_h, fill=False, layer=1
            )

    def add_marker_grid_preview(
        self,
        markers: List[Dict[str, Any]],
        include_borders: bool = True,
        include_outer_border: bool = False,
        border_width: float = 2.0,
    ):
        """Add ArUCO markers with optimized preview rendering"""
        for marker in markers:
            image = marker["image"]
            size = marker["size"]
            x, y = marker["x"], marker["y"]
            marker_id = marker["id"]

            # Add border if requested
            if include_borders:
                self.add_rectangle(
                    x, y, size, size, fill=False, layer=1, marker_id=marker_id
                )

            # Convert ArUCO image to rectangles - use merged rectangles for better quality
            pixel_size = size / image.shape[0]

            # Use rectangle merging algorithm for preview as well to prevent artifacts
            rectangles = self._find_merged_rectangles(image)

            # Add merged rectangles with overlap to prevent gaps
            for rect in rectangles:
                # Calculate positions
                px_x = x + rect["col"] * pixel_size
                px_y = y + rect["row"] * pixel_size
                width = rect["width"] * pixel_size
                height = rect["height"] * pixel_size

                # Add small overlap to prevent gaps but maintain dimensions
                # Use 0.5% of the rectangle size or 0.05mm, whichever is smaller
                overlap = min(
                    0.05, max(width * 0.005, height * 0.005)
                )  # Max 0.05mm, or 0.5% of size
                self.add_rectangle(
                    px_x,
                    px_y,
                    width + overlap,
                    height + overlap,
                    fill=True,
                    layer=0,
                    marker_id=marker_id,
                )

            # Update bounds
            self._update_bounds(x, y, size, size)

        # Add outer border around entire grid if requested
        if include_outer_border and markers:
            # Calculate grid bounds
            min_x = min(float(marker["x"]) for marker in markers)
            min_y = min(float(marker["y"]) for marker in markers)
            max_x = max(float(marker["x"] + marker["size"]) for marker in markers)
            max_y = max(float(marker["y"] + marker["size"]) for marker in markers)

            # Add outer border rectangle
            border_x = min_x - border_width
            border_y = min_y - border_width
            border_w = (max_x - min_x) + (2 * border_width)
            border_h = (max_y - min_y) + (2 * border_width)

            self.add_rectangle(
                border_x, border_y, border_w, border_h, fill=False, layer=1
            )

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

    def _update_bounds(self, x: float, y: float, width: float, height: float):
        """Update drawing bounds"""
        self.bounds["min_x"] = min(self.bounds["min_x"], x)
        self.bounds["min_y"] = min(self.bounds["min_y"], y)
        self.bounds["max_x"] = max(self.bounds["max_x"], x + width)
        self.bounds["max_y"] = max(self.bounds["max_y"], y + height)

    def _find_merged_rectangles(self, image: np.ndarray) -> List[Dict[str, int]]:
        """Find merged rectangles in binary image using 2D merging"""
        rectangles = []
        visited = np.zeros_like(image, dtype=bool)

        for row in range(image.shape[0]):
            for col in range(image.shape[1]):
                if (
                    image[row, col] == 0 and not visited[row, col]
                ):  # Black and unvisited
                    # Find the largest rectangle starting from this point
                    max_width = image.shape[1] - col
                    max_height = image.shape[0] - row

                    # Find maximum width for this row
                    width = 0
                    while (
                        width < max_width
                        and image[row, col + width] == 0
                        and not visited[row, col + width]
                    ):
                        width += 1

                    # Find maximum height maintaining this width
                    height = 1
                    while height < max_height:
                        # Check if the entire row at this height is black
                        row_valid = True
                        for w in range(width):
                            if (
                                image[row + height, col + w] != 0
                                or visited[row + height, col + w]
                            ):
                                row_valid = False
                                break
                        if not row_valid:
                            break
                        height += 1

                    # Mark all pixels in this rectangle as visited
                    for r in range(height):
                        for c in range(width):
                            visited[row + r, col + c] = True

                    # Add the rectangle
                    rectangles.append(
                        {"row": row, "col": col, "width": width, "height": height}
                    )

        return rectangles

    def get_svg(self) -> str:
        """Generate SVG preview"""
        # Handle case where no elements have been added
        if self.bounds["min_x"] == float("inf"):
            return '<svg width="100mm" height="100mm" xmlns="http://www.w3.org/2000/svg"><text x="50" y="50" text-anchor="middle">No markers</text></svg>'

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

            elif element["type"] == "text":
                svg += f"""<text x="{element['x']:.3f}" y="{element['y']:.3f}"
                               class="text">{element['text']}</text>"""

        svg += "</svg>"
        return svg
