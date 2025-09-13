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
        # Cache for generated markers to avoid regeneration
        self._marker_cache = {}
        self._cache_key = None
    
    def get_dictionary_info(self) -> Dict:
        """Get information about available ArUCO dictionaries"""
        return self.aruco_gen.get_dictionary_info()
    
    def validate_marker_params(self, data: Dict) -> List[str]:
        """Validate marker generation parameters"""
        errors = []
        
        # Dictionary validation
        dictionary = data.get('dictionary')
        if not dictionary:
            errors.append('Dictionary is required')
        elif dictionary not in self.aruco_gen.dictionaries:
            errors.append(f'Invalid dictionary: {dictionary}')
            return errors  # No point continuing if dictionary is invalid
        
        # Get parameter values with defaults
        try:
            start_id = int(data.get('start_id', 0))
            rows = int(data.get('rows', 1))
            cols = int(data.get('cols', 1))
            size_mm = float(data.get('size_mm', 20))
            spacing_mm = float(data.get('spacing_mm', 5))
        except (ValueError, TypeError):
            errors.append('Invalid numeric parameters')
            return errors
        
        # Basic range validation
        if start_id < 0:
            errors.append('Start ID must be non-negative')
        if rows <= 0 or cols <= 0:
            errors.append('Rows and columns must be positive')
        if size_mm <= 0:
            errors.append('Size must be positive')
        if spacing_mm < 0:
            errors.append('Spacing must be non-negative')
        
        # Check marker count limits
        if dictionary and not errors:
            dict_info = self.aruco_gen.get_dictionary_info()[dictionary]
            total_markers = rows * cols
            if start_id + total_markers > dict_info['max_markers']:
                errors.append(f'Too many markers for dictionary {dictionary}')
        
        return errors
    
    def generate_markers(self, data: Dict) -> Dict:
        """Generate ArUCO markers with caching"""
        # Extract parameters
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        
        # Create cache key from parameters
        cache_key = f"{dictionary}_{start_id}_{rows}_{cols}_{size_mm}_{spacing_mm}"
        
        # Check if we have cached markers
        if cache_key != self._cache_key or not self._marker_cache:
            # Generate markers only if not cached
            markers = self.aruco_gen.generate_grid(
                start_id, dictionary, rows, cols, 
                size_mm, spacing_mm, generate_images=True
            )
            # Update cache
            self._marker_cache = markers
            self._cache_key = cache_key
        else:
            # Use cached markers
            markers = self._marker_cache
        
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
        """Generate SVG preview of markers using DrawingContext"""
        from aruco_generator.drawing import DrawingContext
        
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
        
        # Create drawing context
        ctx = DrawingContext()
        
        # Build markers list for drawing context
        markers = []
        for row in range(rows):
            for col in range(cols):
                marker_id = start_id + (row * cols + col)
                x = col * (size_mm + spacing_mm)
                y = row * (size_mm + spacing_mm)
                
                # Generate marker image for preview
                marker_image = self.aruco_gen.generate_marker(
                    marker_id, dictionary, size_pixels=10
                )
                
                markers.append({
                    'id': marker_id,
                    'x': x,
                    'y': y,
                    'size': size_mm,
                    'image': marker_image
                })
        
        # Add markers to drawing context with preview optimization
        ctx.add_marker_grid_preview(
            markers, 
            include_borders=include_borders,
            include_outer_border=include_outer_border,
            border_width=border_width
        )
        
        # Add labels if requested
        if include_labels:
            ctx.add_text_labels(markers)
        
        # Generate and return SVG
        return ctx.get_svg()
    
    def export_markers(self, data: Dict, format: str) -> Dict[str, Any]:
        """Export markers in specified format with caching"""
        from aruco_generator.drawing import DrawingContext
        
        # Extract parameters
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        
        # Create cache key
        cache_key = f"{dictionary}_{start_id}_{rows}_{cols}_{size_mm}_{spacing_mm}"
        
        # Check if we need to regenerate markers
        if cache_key != self._cache_key or not self._marker_cache:
            # Generate markers only if not cached
            markers = self.aruco_gen.generate_grid(
                start_id, dictionary, rows, cols,
                size_mm, spacing_mm, generate_images=True
            )
            # Update cache
            self._marker_cache = markers
            self._cache_key = cache_key
        else:
            # Use cached markers
            markers = self._marker_cache
        
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
            
            return {
                'content': file_data,
                'filename': f"{filename_base}.lbrn2",
                'mimetype': 'application/xml'
            }
        
        elif format == 'svg':
            svg_content = self.generate_preview(data)
            return {
                'content': svg_content.encode(),
                'filename': f"{filename_base}.svg",
                'mimetype': 'image/svg+xml'
            }
        
        elif format == 'pdf':
            # PDF export would be implemented here
            # For now, return a placeholder
            return {
                'content': b'PDF export not yet implemented',
                'filename': f"{filename_base}.pdf",
                'mimetype': 'application/pdf'
            }
        
        elif format == 'json':
            # Export marker data as JSON
            json_data = {
                'markers': [self._marker_to_dict(m) for m in markers],
                'metadata': {
                    'dictionary': dictionary,
                    'rows': rows,
                    'cols': cols,
                    'size_mm': size_mm,
                    'spacing_mm': spacing_mm,
                    'total_markers': len(markers),
                    'start_id': start_id,
                    'timestamp': datetime.now().isoformat()
                }
            }
            import json
            return {
                'content': json.dumps(json_data, indent=2).encode(),
                'filename': f"{filename_base}.json",
                'mimetype': 'application/json'
            }
        
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