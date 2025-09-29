"""
Simplified marker generation services combining core functionality
"""
import logging
import io
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MarkerService:
    """Simplified service for marker generation and management"""
    
    def __init__(self, aruco_generator, lightburn_exporter=None):
        self.aruco_gen = aruco_generator
        self.lightburn_exporter = lightburn_exporter
        
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
            return errors
        
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
    
    def generate_preview(self, data: Dict) -> str:
        """Generate SVG preview of markers"""
        from aruco_generator.drawing import DrawingContext
        
        # Extract parameters
        dictionary = data.get('dictionary')
        start_id = int(data.get('start_id', 0))
        rows = int(data.get('rows', 1))
        cols = int(data.get('cols', 1))
        size_mm = float(data.get('size_mm', 20))
        spacing_mm = float(data.get('spacing_mm', 5))
        border_bits = int(data.get('border_bits', 1))
        
        # Generate markers
        markers = self.aruco_gen.generate_grid(
            dictionary=dictionary,
            start_id=start_id,
            rows=rows,
            cols=cols,
            size=size_mm,
            spacing=spacing_mm,
            border_bits=border_bits
        )
        
        # Create SVG
        total_width, total_height = self.aruco_gen.calculate_total_size(
            rows, cols, size_mm, spacing_mm
        )
        
        # Add space for labels if requested
        if data.get('include_labels'):
            total_height += 6
            
        # Add outer border if requested
        if data.get('include_outer_border'):
            border_width = float(data.get('border_width', 2.0))
            total_width += 2 * border_width
            total_height += 2 * border_width
        
        # Create drawing context
        ctx = DrawingContext(total_width, total_height)
        
        # Draw outer border if requested
        if data.get('include_outer_border'):
            border_width = float(data.get('border_width', 2.0))
            ctx.add_rect(
                x=border_width / 2,
                y=border_width / 2,
                width=total_width - border_width,
                height=total_height - border_width,
                fill='none',
                stroke='black',
                stroke_width=border_width / 2
            )
            # Adjust markers position
            offset = border_width
        else:
            offset = 0
        
        # Draw markers
        for marker_info in markers:
            marker_data = marker_info['marker']
            pos = marker_info['position']
            marker_id = marker_info['id']
            
            x = pos[0] + offset
            y = pos[1] + offset
            
            # Draw white background
            ctx.add_rect(x, y, size_mm, size_mm, fill='white', stroke='black', stroke_width=0.1)
            
            # Draw black border
            if border_bits > 0:
                border_size = size_mm / (marker_data.shape[0] / border_bits)
                ctx.add_rect(
                    x + border_size,
                    y + border_size,
                    size_mm - 2 * border_size,
                    size_mm - 2 * border_size,
                    fill='white',
                    stroke='black',
                    stroke_width=0.1
                )
            
            # Draw marker pixels
            pixel_size = size_mm / marker_data.shape[0]
            for i in range(marker_data.shape[0]):
                for j in range(marker_data.shape[1]):
                    if marker_data[i, j] == 0:  # Black pixel
                        ctx.add_rect(
                            x + j * pixel_size,
                            y + i * pixel_size,
                            pixel_size,
                            pixel_size,
                            fill='black'
                        )
            
            # Add label if requested
            if data.get('include_labels'):
                ctx.add_text(
                    x + size_mm / 2,
                    y + size_mm + 4,
                    f"ID: {marker_id}",
                    font_size=3,
                    text_anchor='middle'
                )
        
        return ctx.to_svg()
    
    def export_markers(self, data: Dict, format: str = 'lightburn') -> Dict:
        """Export markers to specified format"""
        if format == 'lightburn' and self.lightburn_exporter:
            # Generate markers
            dictionary = data.get('dictionary')
            start_id = int(data.get('start_id', 0))
            rows = int(data.get('rows', 1))
            cols = int(data.get('cols', 1))
            size_mm = float(data.get('size_mm', 20))
            spacing_mm = float(data.get('spacing_mm', 5))
            border_bits = int(data.get('border_bits', 1))
            
            markers = self.aruco_gen.generate_grid(
                dictionary=dictionary,
                start_id=start_id,
                rows=rows,
                cols=cols,
                size=size_mm,
                spacing=spacing_mm,
                border_bits=border_bits
            )
            
            # Generate LightBurn file
            content = self.lightburn_exporter.create_lightburn_file(
                markers=markers,
                size_mm=size_mm,
                border_bits=border_bits,
                include_labels=data.get('include_labels', False),
                include_alignment=data.get('include_alignment', False),
                include_rulers=data.get('include_rulers', False)
            )
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"aruco_{dictionary}_{rows}x{cols}_{timestamp}.lbrn2"
            
            return {
                'content': content.encode('utf-8'),
                'filename': filename,
                'mimetype': 'application/octet-stream'
            }
        
        raise ValueError(f"Unsupported export format: {format}")


class CalibrationService:
    """Simplified calibration pattern generation service"""
    
    def __init__(self, calibration_generator):
        self.cal_gen = calibration_generator
    
    def generate_charuco_board(self, data: Dict) -> Dict:
        """Generate ChArUco board for calibration"""
        result = self.cal_gen.generate_charuco_board(
            squares_x=int(data.get('squares_x', 8)),
            squares_y=int(data.get('squares_y', 6)),
            square_size_mm=float(data.get('square_size_mm', 30.0)),
            marker_size_mm=float(data.get('marker_size_mm', 22.5)),
            dictionary=data.get('dictionary', '4X4_50'),
            start_id=int(data.get('start_id', 0))
        )
        return result
    
    def generate_calibration_grid(self, data: Dict) -> Dict:
        """Generate calibration grid pattern"""
        result = self.cal_gen.generate_calibration_grid(
            pattern_type=data.get('pattern_type', 'checkerboard'),
            grid_x=int(data.get('grid_x', 9)),
            grid_y=int(data.get('grid_y', 6)),
            square_size_mm=float(data.get('square_size_mm', 25.0))
        )
        return result
    
    def export_calibration_data(self, data: Dict, format: str) -> str:
        """Export calibration data to specified format"""
        if format == 'opencv_yaml':
            return self.cal_gen.export_calibration_yaml(data)
        elif format == 'ros_json':
            return self.cal_gen.export_calibration_json(data)
        else:
            raise ValueError(f"Unsupported export format: {format}")