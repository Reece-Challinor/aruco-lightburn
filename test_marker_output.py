#!/usr/bin/env python3
"""
Generate and save a test marker to verify no line artifacts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aruco_generator.aruco import ArUCOGenerator
from aruco_generator.drawing import DrawingContext

# Generate a single marker
generator = ArUCOGenerator()
markers = generator.generate_grid(
    start_id=0,
    dict_name="4X4_50",
    rows=2,
    cols=2,
    size_mm=50,
    spacing_mm=10
)

# Create drawing context
ctx = DrawingContext()
ctx.add_marker_grid_preview(markers, include_borders=True)

# Get SVG
svg_content = ctx.get_svg()

# Save to file
with open('test_marker.svg', 'w') as f:
    f.write(svg_content)

print("Generated test_marker.svg")
print(f"SVG size: {len(svg_content)} bytes")
print(f"Rectangle count: {svg_content.count('<rect')}")

# Check for potential gaps by looking at rectangle positions
import re
rect_pattern = r'x="([^"]+)"\s+y="([^"]+)"\s+width="([^"]+)"\s+height="([^"]+)"'
rectangles = re.findall(rect_pattern, svg_content)

print(f"\nAnalyzing {len(rectangles)} rectangles for gaps...")

# Check if rectangles have overlaps
has_overlap = False
for rect in rectangles[:10]:  # Check first 10 rectangles
    x, y, w, h = map(float, rect)
    if x < 0 or y < 0:  # Negative coordinates indicate overlap extension
        has_overlap = True
        break

if has_overlap:
    print("✓ Rectangles have overlap to prevent gaps")
else:
    print("⚠ No overlap detected - may have gaps")

print("\nTo view the generated marker, open test_marker.svg in a browser")
print("Look for any thin horizontal or vertical lines in the black areas")