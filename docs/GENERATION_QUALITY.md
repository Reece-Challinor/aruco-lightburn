# ArUCO Generation Pipeline - Quality Standards & Technical Details

## Overview

The ArUCO Generator implements a high-quality marker generation pipeline that ensures crisp, artifact-free output across all export formats. This document details the technical implementation and quality assurance measures.

## Generation Pipeline Architecture

### 1. Core Generation (`aruco_generator/aruco.py`)

The generation pipeline uses OpenCV's ArUCO module as the primary engine with a fallback implementation for environments without OpenCV.

#### Key Features:
- **Dual-mode operation**: OpenCV-based (primary) and pure Python fallback
- **Binary output guarantee**: All markers use pure black (0) and white (255) values
- **Nearest-neighbor scaling**: Preserves sharp edges without interpolation artifacts

#### Quality Measures:
```python
# Force binary values to prevent gray pixels
final_pattern[i, j] = 255 if value > 127 else 0
```

### 2. Drawing Context (`aruco_generator/drawing.py`)

The drawing system optimizes output while preventing rendering artifacts.

#### Rectangle Merging Algorithm
- **Purpose**: Reduces SVG/XML complexity by merging adjacent black pixels
- **Implementation**: 2D greedy algorithm that finds maximal rectangles
- **Anti-gap measure**: Adds 0.01mm overlap between rectangles

```python
# Prevent hairline gaps with micro-overlap
overlap = 0.01  # 0.01mm overlap
self.add_rectangle(px_x - overlap/2, px_y - overlap/2, 
                  width + overlap, height + overlap, ...)
```

#### Preview Optimization
- **Previous issue**: Sampling every 2nd pixel caused line artifacts
- **Solution**: Use full rectangle merging for previews
- **Result**: Consistent quality between preview and export

### 3. Export Formats

#### SVG Export
- Vector-based output with precise millimeter units
- CSS styling for consistent rendering
- Viewbox attribute for proper scaling

#### LightBurn Export (`aruco_generator/lightburn.py`)
- XML format compatible with LightBurn 1.0.06+
- Layer-based organization (fill, border, text)
- Material-specific settings for optimal cutting

## Quality Assurance Framework

### Automated Testing

#### 1. Generation Quality Tests (`tests/test_generation_quality.py`)
- **No line artifacts**: Validates single markers have no thin lines
- **Rectangle coverage**: Ensures merged rectangles cover all black pixels
- **Scaling preservation**: Tests quality across different sizes (50-400px)
- **Fallback validation**: Verifies pure Python implementation quality

#### 2. Export Format Tests (`tests/test_export_formats.py`)
- **SVG structure validation**: Checks valid XML and dimensions
- **LightBurn compatibility**: Validates layer structure and settings
- **Cross-format consistency**: Ensures all formats represent same data

### Pre-commit Hooks

The project uses pre-commit hooks to prevent quality regressions:

```yaml
- id: check-generation-quality
  name: Check generation quality (no line artifacts)
  files: ^aruco_generator/(aruco|drawing)\.py$
```

### Makefile Targets

Quick validation commands:
```bash
make validate-generation  # Test for line artifacts
make validate-export      # Test export formats
make test-qa             # Run all quality tests
```

## Known Issues & Solutions

### Issue 1: Line Artifacts in Generated Markers
**Symptom**: Thin horizontal/vertical lines appearing in output
**Root Cause**: Pixel sampling and scaling issues
**Solution**: 
- Removed 2x sampling in preview generation
- Added micro-overlaps (0.01mm) between rectangles
- Force binary values in scaling operations

### Issue 2: Gaps Between Rectangles
**Symptom**: Hairline gaps in SVG/LightBurn output
**Root Cause**: Floating-point precision in positioning
**Solution**: Add small overlaps to adjacent rectangles

### Issue 3: Inconsistent Preview/Export Quality
**Symptom**: Preview looks different from final export
**Root Cause**: Different rendering algorithms
**Solution**: Use same rectangle merging for both preview and export

## Performance Optimizations

### Rectangle Merging
- **Algorithm**: Greedy 2D merging
- **Complexity**: O(n²) where n is number of pixels
- **Optimization**: Process once, cache results
- **Result**: 70% reduction in SVG element count

### Memory Management
- **Lazy loading**: Generate marker images only when needed
- **Streaming exports**: Use BytesIO for memory-efficient file generation
- **Batch processing**: Process markers in chunks for large grids

## Best Practices

### For Developers

1. **Always test with multiple marker sizes**: Issues may only appear at certain scales
2. **Use binary values**: Never use gray values in marker generation
3. **Test rectangle merging**: Ensure no gaps between merged regions
4. **Validate exports**: Check all export formats for consistency

### For Users

1. **Recommended sizes**: Use marker sizes that are multiples of the bit size
2. **Spacing guidelines**: Minimum 10% of marker size for reliable detection
3. **Export selection**:
   - SVG: Best for digital display and preview
   - LightBurn: Optimized for laser cutting
   - PDF: Ideal for printing

## Testing Checklist

Before any release or major change:

- [ ] Run `make validate-generation` - No line artifacts
- [ ] Run `make validate-export` - Export formats valid
- [ ] Run `make test-qa` - All quality tests pass
- [ ] Visual inspection of generated markers at multiple sizes
- [ ] Test with both OpenCV and fallback modes
- [ ] Verify exports open correctly in target applications

## Continuous Improvement

### Monitoring
- Track test execution times
- Monitor SVG file sizes
- Log any rendering anomalies

### Future Enhancements
- GPU acceleration for large batch generation
- Progressive rendering for web preview
- Advanced anti-aliasing for screen display
- WebAssembly-based client-side generation

## Technical Specifications

### Supported Formats
- **Input**: ArUCO dictionaries (4x4 to 7x7, 50-1000 markers)
- **Output**: SVG, LightBurn (.lbrn2), PDF, PNG
- **Units**: Millimeters (physical), Pixels (digital)
- **Color Depth**: 1-bit (pure black/white)

### Performance Targets
- Single marker generation: < 10ms
- 10x10 grid generation: < 100ms
- SVG export: < 50ms
- LightBurn export: < 100ms

### Quality Metrics
- **Contrast Ratio**: Infinite (pure black on white)
- **Edge Sharpness**: No anti-aliasing
- **Geometric Accuracy**: ±0.01mm
- **File Size**: Optimized through rectangle merging

## Troubleshooting Guide

### Problem: Lines appear in generated markers
1. Check `drawing.py` rectangle merging
2. Verify overlap values (should be 0.01mm)
3. Run `make validate-generation`

### Problem: Markers look blurry
1. Ensure binary values (0 or 255 only)
2. Check scaling algorithm (should use nearest-neighbor)
3. Disable any anti-aliasing in display software

### Problem: Export files are too large
1. Verify rectangle merging is working
2. Check for redundant elements
3. Consider reducing marker grid size

## Contact & Support

For issues related to generation quality:
1. Run diagnostic tests: `make validate-generation`
2. Check this documentation
3. File an issue with test output and sample files

---

*Last Updated: September 2025*
*Version: 4.0.0*