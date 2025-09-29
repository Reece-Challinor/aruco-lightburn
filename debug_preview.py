#!/usr/bin/env python3
"""Debug preview generation to find line artifacts issue"""

import json
import requests

# Test the actual preview API endpoint
print("Testing preview API endpoint...")
response = requests.post('http://localhost:5000/api/preview', json={
    'dictionary': '4X4_50',
    'start_id': 0,
    'rows': 1,
    'cols': 1,
    'size_mm': 50,
    'spacing_mm': 0,
    'include_borders': True
})

if response.status_code == 200:
    data = response.json()
    svg = data['svg']
    
    print(f"✓ Preview API responded successfully")
    print(f"SVG length: {len(svg)} bytes")
    
    # Check for marker_placeholder elements
    if 'marker_placeholder' in svg:
        print("✗ ERROR: Using placeholder markers instead of actual rectangles!")
        print("  This is why lines appear in the preview")
        
        # Count placeholder elements
        import re
        placeholders = svg.count('marker_placeholder')
        print(f"  Found {placeholders} placeholder marker(s)")
    else:
        print("✓ Using actual rectangle rendering")
        
        # Count rect elements
        import re
        rect_pattern = r'<rect[^>]*class="cut"'
        rectangles = len(re.findall(rect_pattern, svg))
        print(f"  Found {rectangles} black rectangles")
    
    # Check for checkerboard pattern (indicator of placeholder)
    if 'pattern_size' in svg or any(f'{i * pattern}' in svg for i in range(6) for pattern in [8.333, 16.667]):
        print("✗ ERROR: Checkerboard pattern detected (placeholder rendering)")
    
    # Save SVG for inspection
    with open('debug_preview.svg', 'w') as f:
        f.write(svg)
    print("\nSaved preview to debug_preview.svg for inspection")
    
else:
    print(f"✗ API error: {response.status_code}")
    print(response.text)