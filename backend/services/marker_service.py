"""
Marker generation service
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class MarkerService:
    """Service for marker generation and management"""
    
    def __init__(self, aruco_generator, lightburn_exporter, marker_repository):
        self.aruco_gen = aruco_generator
        self.lightburn_exporter = lightburn_exporter
        self.repository = marker_repository
    
    def get_dictionary_info(self) -> Dict:
        """Get information about available ArUCO dictionaries"""
        return self.aruco_gen.get_dictionary_info()
    
    def validate_marker_params(self, data: Dict) -> List[str]:
        """Validate marker generation parameters"""
        errors = []
        
        # Required fields
        if not data.get('dictionary'):
            errors.append('Dictionary is required')
        elif data['dictionary'] not in self.aruco_gen.dictionaries:
            errors.append(f'Invalid dictionary: {data["dictionary"]}')
        
        # Numeric validations
        try:
            start_id = int(data.get('start_id', 0))
            if start_id < 0:
                errors.append('Start ID must be non-negative')
        except (ValueError, TypeError):
            errors.append('Invalid start ID')
        
        try:
            rows = int(data.get('rows', 1))
            cols = int(data.get('cols', 1))
            if rows <= 0 or cols <= 0:
                errors.append('Rows and columns must be positive')
        except (ValueError, TypeError):
            errors.append('Invalid rows or columns')
        
        try:
            size_mm = float(data.get('size_mm', 20))
            if size_mm <= 0:
                errors.append('Size must be positive')
        except (ValueError, TypeError):
            errors.append('Invalid size')
        
        try:
            spacing_mm = float(data.get('spacing_mm', 5))
            if spacing_mm < 0:
                errors.append('Spacing must be non-negative')
        except (ValueError, TypeError):
            errors.append('Invalid spacing')
        
        # Check marker count limits
        if data.get('dictionary') in self.aruco_gen.dictionaries:
            dict_info = self.aruco_gen.get_dictionary_info()[data['dictionary']]
            total_markers = rows * cols if 'rows' in data and 'cols' in data else 1
            if start_id + total_markers > dict_info['max_markers']:
                errors.append(f'Too many markers for dictionary {data["dictionary"]}')
        
        return errors
    
    def generate_markers(self, data: Dict) -> Dict:
        """Generate ArUCO markers"""
        # Extract parameters
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        
        # Generate markers
        markers = self.aruco_gen.generate_grid(
            start_id, dictionary, rows, cols, 
            size_mm, spacing_mm, generate_images=True
        )
        
        # Save to repository if needed
        if data.get('save', False):
            for marker in markers:
                self.repository.save_marker(marker)
        
        # Calculate dimensions
        total_width, total_height = self.aruco_gen.calculate_total_size(
            rows, cols, size_mm, spacing_mm
        )
        
        return {
            'markers': [self._marker_to_dict(m) for m in markers],
            'dimensions': {
                'width': round(total_width, 2),
                'height': round(total_height, 2)
            },
            'count': len(markers)
        }
    
    def generate_preview(self, data: Dict) -> str:
        """Generate SVG preview of markers"""
        # Extract parameters
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        include_borders = data.get('include_borders', True)
        include_labels = data.get('include_labels', True)
        include_outer_border = data.get('include_outer_border', False)
        border_width = float(data.get('border_width', 2.0))
        
        # Generate SVG elements
        svg_elements = []
        
        for row in range(rows):
            for col in range(cols):
                marker_id = start_id + (row * cols + col)
                x = col * (size_mm + spacing_mm)
                y = row * (size_mm + spacing_mm)
                
                # Generate marker image
                marker_image = self.aruco_gen.generate_marker(
                    marker_id, dictionary, size_pixels=10
                )
                
                # Add white background
                svg_elements.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" '
                    f'width="{size_mm:.1f}" height="{size_mm:.1f}" fill="white"/>'
                )
                
                # Add border if requested
                if include_borders:
                    svg_elements.append(
                        f'<rect x="{x:.1f}" y="{y:.1f}" '
                        f'width="{size_mm:.1f}" height="{size_mm:.1f}" '
                        f'fill="none" stroke="red" stroke-width="0.2"/>'
                    )
                
                # Convert ArUCO pattern to SVG
                pixel_size = size_mm / marker_image.shape[0]
                for img_row in range(0, marker_image.shape[0], 2):
                    for img_col in range(0, marker_image.shape[1], 2):
                        if marker_image[img_row, img_col] == 0:
                            px_x = x + img_col * pixel_size
                            px_y = y + img_row * pixel_size
                            svg_elements.append(
                                f'<rect x="{px_x:.1f}" y="{px_y:.1f}" '
                                f'width="{pixel_size*2:.1f}" height="{pixel_size*2:.1f}" '
                                f'fill="black"/>'
                            )
                
                # Add labels if requested
                if include_labels:
                    label_x = x + size_mm / 2
                    label_y = y + size_mm + 3
                    svg_elements.append(
                        f'<text x="{label_x:.1f}" y="{label_y:.1f}" '
                        f'text-anchor="middle" font-family="Arial" '
                        f'font-size="3" fill="red">ID: {marker_id}</text>'
                    )
        
        # Calculate dimensions
        total_width, total_height = self.aruco_gen.calculate_total_size(
            rows, cols, size_mm, spacing_mm
        )
        
        if include_labels:
            total_height += 6
        
        if include_outer_border:
            border_x = -border_width
            border_y = -border_width
            border_w = total_width + (2 * border_width)
            border_h = total_height + (2 * border_width)
            svg_elements.insert(
                0,
                f'<rect x="{border_x:.1f}" y="{border_y:.1f}" '
                f'width="{border_w:.1f}" height="{border_h:.1f}" '
                f'fill="none" stroke="red" stroke-width="1"/>'
            )
            total_width += 2 * border_width
            total_height += 2 * border_width
        
        # Create SVG
        svg_content = (
            f'<svg width="{total_width:.1f}mm" height="{total_height:.1f}mm" '
            f'viewBox="0 0 {total_width:.1f} {total_height:.1f}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(svg_elements)}'
            f'</svg>'
        )
        
        return svg_content
    
    def export_markers(self, data: Dict, format: str) -> Tuple[bytes, str, str]:
        """Export markers in specified format"""
        from aruco_generator.drawing import DrawingContext
        
        # Generate markers
        markers = self.aruco_gen.generate_grid(
            int(data.get('start_id', 0)),
            data.get('dictionary'),
            int(data.get('rows', 1)),
            int(data.get('cols', 1)),
            float(data.get('size_mm', 20)),
            float(data.get('spacing_mm', 5)),
            generate_images=True
        )
        
        # Create filename
        filename_base = f"aruco_{data.get('dictionary')}_{data.get('rows')}x{data.get('cols')}_id{data.get('start_id')}"
        
        if format == 'lightburn':
            # Create drawing context
            context = DrawingContext()
            context.add_marker_grid(
                markers,
                data.get('include_borders', True),
                data.get('include_outer_border', False),
                float(data.get('border_width', 2.0))
            )
            
            if data.get('include_labels', True):
                context.add_text_labels(markers)
            
            # Create metadata
            metadata = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dictionary': data.get('dictionary'),
                'rows': data.get('rows'),
                'cols': data.get('cols'),
                'size_mm': data.get('size_mm'),
                'spacing_mm': data.get('spacing_mm'),
                'total_markers': len(markers),
                'start_id': data.get('start_id')
            }
            
            # Export to LightBurn
            lbrn_file = self.lightburn_exporter.export(context, metadata)
            
            # Read file data
            lbrn_file.seek(0)
            file_data = lbrn_file.read()
            
            return file_data, f"{filename_base}.lbrn2", 'application/xml'
        
        elif format == 'svg':
            svg_content = self.generate_preview(data)
            return svg_content.encode(), f"{filename_base}.svg", 'image/svg+xml'
        
        elif format == 'pdf':
            # PDF export would be implemented here
            # For now, return a placeholder
            return b'PDF export not yet implemented', f"{filename_base}.pdf", 'application/pdf'
        
        else:
            raise ValueError(f'Unsupported export format: {format}')
    
    def generate_batch(self, batch_config: List[Dict]) -> List[Dict]:
        """Generate batch of markers"""
        results = []
        
        for config in batch_config:
            try:
                result = self.generate_markers(config)
                result['status'] = 'success'
                results.append(result)
            except Exception as e:
                results.append({
                    'status': 'error',
                    'error': str(e),
                    'config': config
                })
        
        return results
    
    def _marker_to_dict(self, marker) -> Dict:
        """Convert marker object to dictionary"""
        return {
            'id': marker['id'],
            'x': marker['x'],
            'y': marker['y'],
            'size': marker['size'],
            'dictionary': marker['dict']
        }