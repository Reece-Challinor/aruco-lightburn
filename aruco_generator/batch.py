"""
{
  "file_type": "batch_processor",
  "purpose": "Batch processing for generating multiple ArUCO marker files",
  "dependencies": ["aruco.py", "drawing.py", "lightburn.py"],
  "main_class": "BatchGenerator",
  "key_methods": {
    "generate_batch_files": "Generate multiple LightBurn files with sequential IDs",
    "generate_id_sequence_files": "Generate files with specific ID ranges",
    "_calculate_optimal_grid": "Calculate optimal grid layout for marker count",
    "_generate_batch_summary": "Create documentation for batch operations"
  },
  "ai_navigation": {
    "modify_for": "Adding new batch processing patterns or optimization",
    "used_by": ["web.py for advanced batch operations"],
    "output_format": "ZIP files containing multiple .lbrn2 files"
  }
}
"""

import zipfile
from io import BytesIO
from typing import List, Dict, Any
from datetime import datetime
from .aruco import ArUCOGenerator
from .drawing import DrawingContext
from .lightburn import LightBurnExporter

class BatchGenerator:
    def __init__(self):
        self.generator = ArUCOGenerator()
        self.exporter = LightBurnExporter()
    
    def generate_batch_files(self, base_config: Dict[str, Any], 
                           batch_size: int, markers_per_file: int) -> BytesIO:
        """Generate multiple LightBurn files with sequential ID ranges"""
        
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            start_id = int(base_config.get('start_id', 0))
            
            for batch_num in range(batch_size):
                # Calculate ID range for this file
                file_start_id = start_id + (batch_num * markers_per_file)
                file_end_id = file_start_id + markers_per_file - 1
                
                # Create file configuration
                file_config = base_config.copy()
                file_config['start_id'] = file_start_id
                
                # Calculate grid dimensions for markers_per_file
                rows, cols = self._calculate_optimal_grid(markers_per_file)
                file_config['rows'] = rows
                file_config['cols'] = cols
                
                # Generate markers for this file
                markers = self.generator.generate_grid(
                    file_start_id,
                    file_config['dictionary'],
                    rows, cols,
                    float(file_config['size_mm']),
                    float(file_config['spacing_mm'])
                )
                
                # Create drawing context
                context = DrawingContext()
                context.add_marker_grid(markers, 
                                      include_borders=file_config.get('include_borders', True),
                                      include_outer_border=file_config.get('include_outer_border', False),
                                      border_width=float(file_config.get('border_width', 2.0)))
                
                if file_config.get('include_labels', True):
                    context.add_text_labels(markers)
                
                # Generate metadata
                metadata = {
                    'Batch Number': f"{batch_num + 1} of {batch_size}",
                    'Dictionary': file_config['dictionary'],
                    'ID Range': f"{file_start_id}-{file_end_id}",
                    'Grid Size': f"{rows}x{cols}",
                    'Marker Size': f"{file_config['size_mm']}mm",
                    'Spacing': f"{file_config['spacing_mm']}mm",
                    'Total Markers': len(markers),
                    'File Purpose': 'Batch Production',
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Export to LightBurn
                lbrn_file = self.exporter.export(context, metadata)
                
                # Add to ZIP with descriptive filename
                filename = f"aruco_batch_{batch_num+1:03d}_ids_{file_start_id}-{file_end_id}_{rows}x{cols}.lbrn2"
                zip_file.writestr(filename, lbrn_file.getvalue())
            
            # Add batch summary file
            summary = self._generate_batch_summary(base_config, batch_size, markers_per_file)
            zip_file.writestr("BATCH_SUMMARY.txt", summary)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def generate_id_sequence_files(self, base_config: Dict[str, Any], 
                                 id_ranges: List[Dict[str, int]]) -> BytesIO:
        """Generate files with specific ID ranges"""
        
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, id_range in enumerate(id_ranges):
                start_id = id_range['start']
                end_id = id_range['end']
                markers_count = end_id - start_id + 1
                
                # Calculate optimal grid
                rows, cols = self._calculate_optimal_grid(markers_count)
                
                # Generate markers
                markers = self.generator.generate_grid(
                    start_id,
                    base_config['dictionary'],
                    rows, cols,
                    float(base_config['size_mm']),
                    float(base_config['spacing_mm'])
                )
                
                # Trim markers to exact count needed
                markers = markers[:markers_count]
                
                # Create drawing context
                context = DrawingContext()
                context.add_marker_grid(markers,
                                      include_borders=base_config.get('include_borders', True),
                                      include_outer_border=base_config.get('include_outer_border', False),
                                      border_width=float(base_config.get('border_width', 2.0)))
                
                if base_config.get('include_labels', True):
                    context.add_text_labels(markers)
                
                # Generate metadata
                metadata = {
                    'File Number': f"{i + 1} of {len(id_ranges)}",
                    'Dictionary': base_config['dictionary'],
                    'ID Range': f"{start_id}-{end_id}",
                    'Grid Size': f"{rows}x{cols}",
                    'Marker Size': f"{base_config['size_mm']}mm",
                    'Spacing': f"{base_config['spacing_mm']}mm",
                    'Total Markers': len(markers),
                    'File Purpose': 'Custom ID Range',
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Export to LightBurn
                lbrn_file = self.exporter.export(context, metadata)
                
                # Add to ZIP
                filename = f"aruco_range_{start_id}-{end_id}_{rows}x{cols}.lbrn2"
                zip_file.writestr(filename, lbrn_file.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def _calculate_optimal_grid(self, marker_count: int) -> tuple[int, int]:
        """Calculate optimal rows/cols for given marker count"""
        if marker_count == 1:
            return 1, 1
        
        # Try to make as square as possible
        rows = int(marker_count ** 0.5)
        while marker_count % rows != 0:
            rows -= 1
        cols = marker_count // rows
        
        # Prefer landscape orientation
        if rows > cols:
            rows, cols = cols, rows
            
        return rows, cols
    
    def _generate_batch_summary(self, config: Dict[str, Any], 
                              batch_size: int, markers_per_file: int) -> str:
        """Generate batch summary documentation"""
        total_markers = batch_size * markers_per_file
        start_id = int(config.get('start_id', 0))
        end_id = start_id + total_markers - 1
        
        summary = f"""ArUCO BATCH GENERATION SUMMARY
==============================

Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generated by: ArUCO LightBurn Generator v1.0

BATCH CONFIGURATION:
- Dictionary: {config['dictionary']}
- Total Files: {batch_size}
- Markers per File: {markers_per_file}
- Total Markers: {total_markers}
- ID Range: {start_id} to {end_id}
- Marker Size: {config['size_mm']}mm
- Spacing: {config['spacing_mm']}mm
- Include Borders: {config.get('include_borders', True)}
- Include Labels: {config.get('include_labels', True)}

FILE LIST:
"""
        
        for i in range(batch_size):
            file_start = start_id + (i * markers_per_file)
            file_end = file_start + markers_per_file - 1
            rows, cols = self._calculate_optimal_grid(markers_per_file)
            
            summary += f"  {i+1:3d}. aruco_batch_{i+1:03d}_ids_{file_start}-{file_end}_{rows}x{cols}.lbrn2\n"
        
        summary += f"""
MATERIAL SETTINGS:
- Optimized for 1/16" White/Black 2-Ply Cast Acrylic
- Cut: 150mm/min @ 75% power
- Engrave: 800mm/min @ 45% power
- Mark: 1000mm/min @ 20% power

PRODUCTION NOTES:
- Test settings on scrap material first
- Engrave black side up for white markers
- Clean laser optics before production run
- Verify ArUCO detection with test scan
- Store completed markers in anti-static bags

For support: ArUCO LightBurn Generator Documentation
"""
        return summary