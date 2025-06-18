import numpy as np
from typing import List, Dict, Any

class DrawingContext:
    def __init__(self):
        self.elements = []
        self.bounds = {'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0}
    
    def add_rectangle(self, x: float, y: float, width: float, height: float, 
                     fill: bool = True, layer: int = 0, marker_id: int | None = None):
        """Add rectangle to drawing context"""
        element = {
            'type': 'rect',
            'x': x, 'y': y, 
            'width': width, 
            'height': height,
            'fill': fill, 
            'layer': layer
        }
        if marker_id is not None:
            element['marker_id'] = marker_id
            
        self.elements.append(element)
        self._update_bounds(x, y, width, height)
    
    def add_marker_grid(self, markers: List[Dict[str, Any]], include_borders: bool = True, include_outer_border: bool = False, border_width: float = 2.0):
        """Add ArUCO markers as filled rectangles"""
        for marker in markers:
            image = marker['image']
            size = marker['size']
            x, y = marker['x'], marker['y']
            marker_id = marker['id']
            
            # Add border if requested
            if include_borders:
                self.add_rectangle(x, y, size, size, fill=False, layer=1, marker_id=marker_id)
            
            # Convert ArUCO image to rectangles
            pixel_size = size / image.shape[0]
            
            for row in range(image.shape[0]):
                for col in range(image.shape[1]):
                    if image[row, col] == 0:  # Black pixel in ArUCO
                        px_x = x + col * pixel_size
                        px_y = y + row * pixel_size
                        self.add_rectangle(px_x, px_y, pixel_size, pixel_size, 
                                         fill=True, layer=0, marker_id=marker_id)
        
        # Add outer border around entire grid if requested
        if include_outer_border and markers:
            # Calculate grid bounds
            min_x = min(float(marker['x']) for marker in markers)
            min_y = min(float(marker['y']) for marker in markers)
            max_x = max(float(marker['x'] + marker['size']) for marker in markers)
            max_y = max(float(marker['y'] + marker['size']) for marker in markers)
            
            # Add outer border rectangle
            border_x = min_x - border_width
            border_y = min_y - border_width
            border_w = (max_x - min_x) + (2 * border_width)
            border_h = (max_y - min_y) + (2 * border_width)
            
            self.add_rectangle(border_x, border_y, border_w, border_h, fill=False, layer=1)
    
    def add_text_labels(self, markers: List[Dict[str, Any]], font_size: float = 3.0):
        """Add text labels below each marker"""
        for marker in markers:
            x = marker['x']
            y = marker['y'] + marker['size'] + font_size
            text = f"ID: {marker['id']}"
            
            self.elements.append({
                'type': 'text',
                'x': x,
                'y': y,
                'text': text,
                'font_size': font_size,
                'layer': 2,
                'marker_id': marker['id']
            })
    
    def _update_bounds(self, x: float, y: float, width: float, height: float):
        """Update drawing bounds"""
        self.bounds['min_x'] = min(self.bounds['min_x'], x)
        self.bounds['min_y'] = min(self.bounds['min_y'], y)
        self.bounds['max_x'] = max(self.bounds['max_x'], x + width)
        self.bounds['max_y'] = max(self.bounds['max_y'], y + height)
    
    def get_svg(self) -> str:
        """Generate SVG preview"""
        width = self.bounds['max_x'] - self.bounds['min_x']
        height = self.bounds['max_y'] - self.bounds['min_y']
        
        svg = f'''<svg width="{width:.1f}mm" height="{height:.1f}mm" 
                       viewBox="{self.bounds['min_x']:.1f} {self.bounds['min_y']:.1f} {width:.1f} {height:.1f}" 
                       xmlns="http://www.w3.org/2000/svg">
                  <style>
                    .cut {{ fill: black; stroke: none; }}
                    .mark {{ fill: none; stroke: blue; stroke-width: 0.1; }}
                    .text {{ fill: red; font-family: Arial; font-size: 3px; }}
                  </style>'''
        
        for element in self.elements:
            if element['type'] == 'rect':
                if element['fill']:
                    css_class = 'cut'
                else:
                    css_class = 'mark'
                
                svg += f'''<rect x="{element['x']:.3f}" y="{element['y']:.3f}" 
                               width="{element['width']:.3f}" height="{element['height']:.3f}" 
                               class="{css_class}" />'''
            elif element['type'] == 'text':
                svg += f'''<text x="{element['x']:.3f}" y="{element['y']:.3f}" 
                               class="text">{element['text']}</text>'''
        
        svg += '</svg>'
        return svg
