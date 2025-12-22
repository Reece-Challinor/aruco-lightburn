#!/usr/bin/env python3
"""
Quick validation script to test ArUCO generation quality improvements.
This ensures no line artifacts are present in generated markers.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aruco_generator.aruco import ArUCOGenerator  # noqa: E402
from aruco_generator.drawing import DrawingContext  # noqa: E402


def test_single_marker_quality():
    """Test single marker generation has no artifacts"""
    print("Testing single marker generation...")

    generator = ArUCOGenerator()
    marker = generator.generate_marker(marker_id=0, dict_name="4X4_50", size_pixels=200)

    # Check for binary values only
    unique = np.unique(marker)
    assert len(unique) == 2, f"Marker should have exactly 2 colors, found {len(unique)}"
    assert (
        0 in unique and 255 in unique
    ), "Marker should have pure black (0) and white (255)"

    print("✓ Single marker has proper binary contrast (no gray values)")

    # Check for thin lines (artifacts)
    for row in range(1, marker.shape[0] - 1):
        if not np.array_equal(marker[row], marker[row - 1]) and not np.array_equal(
            marker[row], marker[row + 1]
        ):
            line_pixels = np.sum(marker[row] != marker[row - 1])
            if line_pixels < marker.shape[1] * 0.1:
                print(f"✗ Warning: Potential thin line at row {row}")
                return False

    print("✓ No horizontal line artifacts detected")

    for col in range(1, marker.shape[1] - 1):
        column = marker[:, col]
        prev_column = marker[:, col - 1]
        next_column = marker[:, col + 1]

        if not np.array_equal(column, prev_column) and not np.array_equal(
            column, next_column
        ):
            line_pixels = np.sum(column != prev_column)
            if line_pixels < marker.shape[0] * 0.1:
                print(f"✗ Warning: Potential thin line at column {col}")
                return False

    print("✓ No vertical line artifacts detected")
    return True


def test_rectangle_merging():
    """Test rectangle merging doesn't create gaps"""
    print("\nTesting rectangle merging algorithm...")

    # Create a test pattern
    test_pattern = np.ones((10, 10), dtype=np.uint8) * 255  # White background
    test_pattern[0:2, :] = 0  # Black top border
    test_pattern[8:10, :] = 0  # Black bottom border
    test_pattern[:, 0:2] = 0  # Black left border
    test_pattern[:, 8:10] = 0  # Black right border
    test_pattern[4:6, 4:6] = 0  # Black center

    ctx = DrawingContext()
    rectangles = ctx._find_merged_rectangles(test_pattern)

    # Verify coverage
    coverage = np.ones_like(test_pattern) * 255
    for rect in rectangles:
        r, c = rect["row"], rect["col"]
        h, w = rect["height"], rect["width"]
        coverage[r : r + h, c : c + w] = 0

    if np.array_equal(coverage, test_pattern):
        print("✓ Rectangle merging covers all black pixels without gaps")
        return True
    else:
        print("✗ Rectangle merging has gaps or missing coverage")
        return False


def test_svg_generation():
    """Test SVG generation quality"""
    print("\nTesting SVG generation...")

    generator = ArUCOGenerator()
    markers = generator.generate_grid(
        start_id=0, dict_name="4X4_50", rows=2, cols=2, size_mm=20, spacing_mm=5
    )

    ctx = DrawingContext()
    ctx.add_marker_grid_preview(markers, include_borders=True)

    svg = ctx.get_svg()

    # Basic validation
    if not svg.startswith("<svg"):
        print("✗ Invalid SVG structure")
        return False

    if "</svg>" not in svg:
        print("✗ SVG missing closing tag")
        return False

    # Check for rectangles (should have many due to marker patterns)
    rect_count = svg.count("<rect")
    if rect_count > 0:
        print(f"✓ SVG contains {rect_count} rectangles")
    else:
        print("✗ SVG has no rectangles")
        return False

    print("✓ SVG generation successful")
    return True


def test_scaling_quality():
    """Test that different sizes maintain quality"""
    print("\nTesting scaling quality...")

    generator = ArUCOGenerator()
    sizes = [50, 100, 200, 400]

    for size in sizes:
        marker = generator.generate_marker(
            marker_id=5, dict_name="5X5_100", size_pixels=size
        )

        # Check dimensions
        if marker.shape != (size, size):
            print(f"✗ Size {size}: Wrong dimensions {marker.shape}")
            return False

        # Check binary values
        unique = np.unique(marker)
        if len(unique) != 2:
            print(f"✗ Size {size}: Non-binary values found")
            return False

        print(f"✓ Size {size}px: Correct dimensions and binary values")

    print("✓ All sizes maintain quality")
    return True


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("ArUCO Generation Quality Validation")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Single Marker Quality", test_single_marker_quality()))
    results.append(("Rectangle Merging", test_rectangle_merging()))
    results.append(("SVG Generation", test_svg_generation()))
    results.append(("Scaling Quality", test_scaling_quality()))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 SUCCESS: All quality checks passed!")
        print("The generation pipeline is working correctly with no artifacts.")
        return 0
    else:
        print("\n⚠️ WARNING: Some quality checks failed.")
        print("Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
