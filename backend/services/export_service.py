"""
Export service for various file formats
"""
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting markers in various formats"""
    
    def __init__(self):
        self.formats = {
            'lightburn': {
                'name': 'LightBurn',
                'extension': '.lbrn2',
                'mimetype': 'application/xml',
                'description': 'LightBurn laser software format'
            },
            'svg': {
                'name': 'SVG',
                'extension': '.svg',
                'mimetype': 'image/svg+xml',
                'description': 'Scalable Vector Graphics'
            },
            'pdf': {
                'name': 'PDF',
                'extension': '.pdf',
                'mimetype': 'application/pdf',
                'description': 'Portable Document Format'
            },
            'dxf': {
                'name': 'DXF',
                'extension': '.dxf',
                'mimetype': 'application/dxf',
                'description': 'AutoCAD Drawing Exchange Format'
            }
        }
    
    def get_available_formats(self) -> Dict:
        """Get available export formats"""
        return self.formats
    
    def export_lightburn(self, data: Dict) -> Tuple[bytes, str]:
        """Export to LightBurn format"""
        try:
            from aruco_generator.aruco import ArUCOGenerator
            from aruco_generator.drawing import DrawingContext
            from aruco_generator.lightburn import LightBurnExporter
            
            aruco_gen = ArUCOGenerator()
            lightburn_exporter = LightBurnExporter()
            
            # Generate markers
            markers = aruco_gen.generate_grid(
                int(data.get('start_id', 0)),
                data.get('dictionary'),
                int(data.get('rows', 1)),
                int(data.get('cols', 1)),
                float(data.get('size_mm', 20)),
                float(data.get('spacing_mm', 5)),
                generate_images=True
            )
            
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
            lbrn_file = lightburn_exporter.export(context, metadata)
            
            # Read file data
            lbrn_file.seek(0)
            file_data = lbrn_file.read()
            
            filename = f"aruco_{data.get('dictionary')}_{data.get('rows')}x{data.get('cols')}_id{data.get('start_id')}.lbrn2"
            
            return file_data, filename
            
        except Exception as e:
            logger.error(f"LightBurn export error: {e}")
            raise
    
    def export_svg(self, data: Dict) -> Tuple[str, str]:
        """Export to SVG format"""
        try:
            from backend.services.marker_service import MarkerService
            from aruco_generator.aruco import ArUCOGenerator
            from aruco_generator.lightburn import LightBurnExporter
            from backend.repositories.marker_repository import MarkerRepository
            
            aruco_gen = ArUCOGenerator()
            lightburn_exporter = LightBurnExporter()
            marker_repository = MarkerRepository()
            marker_service = MarkerService(aruco_gen, lightburn_exporter, marker_repository)
            
            # Generate SVG
            svg_content = marker_service.generate_preview(data)
            
            filename = f"aruco_{data.get('dictionary')}_{data.get('rows')}x{data.get('cols')}_id{data.get('start_id')}.svg"
            
            return svg_content, filename
            
        except Exception as e:
            logger.error(f"SVG export error: {e}")
            raise
    
    def export_pdf(self, data: Dict) -> Tuple[bytes, str]:
        """Export to PDF format"""
        try:
            # For now, return a placeholder
            # In production, would use reportlab or similar library
            pdf_content = b"PDF export not yet fully implemented"
            
            filename = f"aruco_{data.get('dictionary')}_{data.get('rows')}x{data.get('cols')}_id{data.get('start_id')}.pdf"
            
            return pdf_content, filename
            
        except Exception as e:
            logger.error(f"PDF export error: {e}")
            raise
    
    def export_dxf(self, data: Dict) -> Tuple[bytes, str]:
        """Export to DXF format"""
        try:
            # For now, return a placeholder
            # In production, would use ezdxf or similar library
            dxf_content = b"DXF export not yet fully implemented"
            
            filename = f"aruco_{data.get('dictionary')}_{data.get('rows')}x{data.get('cols')}_id{data.get('start_id')}.dxf"
            
            return dxf_content, filename
            
        except Exception as e:
            logger.error(f"DXF export error: {e}")
            raise
    
    def batch_export(self, data: Dict, formats: List[str]) -> List[Dict]:
        """Export in multiple formats"""
        results = []
        
        for format_name in formats:
            try:
                if format_name == 'lightburn':
                    file_data, filename = self.export_lightburn(data)
                elif format_name == 'svg':
                    file_data, filename = self.export_svg(data)
                elif format_name == 'pdf':
                    file_data, filename = self.export_pdf(data)
                elif format_name == 'dxf':
                    file_data, filename = self.export_dxf(data)
                else:
                    continue
                
                results.append({
                    'format': format_name,
                    'filename': filename,
                    'size': len(file_data) if isinstance(file_data, (bytes, str)) else 0,
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'format': format_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def generate_preview(self, data: Dict, format: str) -> str:
        """Generate preview for export"""
        try:
            if format == 'svg':
                svg_data, _ = self.export_svg(data)
                return svg_data
            else:
                # For other formats, return a description
                return f"Preview for {format} format: {data.get('rows', 1)}x{data.get('cols', 1)} markers"
            
        except Exception as e:
            logger.error(f"Preview generation error: {e}")
            raise