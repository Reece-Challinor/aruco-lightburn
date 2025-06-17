import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Dict, Any
from .drawing import DrawingContext

class LightBurnExporter:
    def __init__(self):
        self.layer_settings = {
            0: {"index": "0", "name": "ArUCO Fill", "type": "Cut", "priority": "2"},      # Black fill
            1: {"index": "1", "name": "ArUCO Border", "type": "Cut", "priority": "1"},   # Blue borders  
            2: {"index": "30", "name": "ArUCO Labels", "type": "Tool", "priority": "0"}  # Red text
        }
    
    def export(self, context: DrawingContext, metadata: Dict[str, Any] = None) -> BytesIO:
        """Export drawing context to LightBurn .lbrn2 format"""
        
        # Create root element
        root = ET.Element('LightBurnProject', {
            'AppVersion': "1.0.06",
            'FormatVersion': "1",
            'MaterialHeight': "0",
            'MirrorX': "False", 
            'MirrorY': "False"
        })
        root.text = "\n"
        
        # Add layer cut settings
        self._add_cut_settings(root)
        
        # Create main shape group
        main_group = ET.SubElement(root, "Shape", Type="Group")
        main_group.text = "\n "
        main_group.tail = "\n"
        
        children = ET.SubElement(main_group, "Children")
        children.text = "\n "
        children.tail = "\n"
        
        # Add all drawing elements
        for element in context.elements:
            if element['type'] == 'rect':
                self._add_rectangle(children, element)
            elif element['type'] == 'text':
                self._add_text(children, element)
        
        # Add metadata as notes if provided
        if metadata:
            self._add_notes(root, metadata)
        
        # Generate XML output
        tree = ET.ElementTree(root)
        output = BytesIO()
        tree.write(output, encoding="utf-8", xml_declaration=True, method="xml")
        output.seek(0)
        return output
    
    def _add_cut_settings(self, root):
        """Add cut settings for different layers"""
        for layer_id, settings in self.layer_settings.items():
            cs = ET.SubElement(root, "CutSetting", Type=settings["type"])
            ET.SubElement(cs, "index", Value=settings["index"])
            ET.SubElement(cs, "name", Value=settings["name"])
            ET.SubElement(cs, "priority", Value=settings["priority"])
    
    def _add_rectangle(self, parent, element):
        """Add rectangle shape to LightBurn XML"""
        layer_idx = str(self.layer_settings[element['layer']]['index'])
        
        shape = ET.SubElement(parent, "Shape", Type="Path", CutIndex=layer_idx)
        shape.text = "\n "
        shape.tail = "\n "
        
        # Create rectangle vertices
        x, y = element['x'], element['y']
        w, h = element['width'], element['height']
        
        vertices = [
            f"V{x:.3f} {y:.3f}c0x1c1x1",
            f"V{x+w:.3f} {y:.3f}c0x1c1x1",
            f"V{x+w:.3f} {y+h:.3f}c0x1c1x1", 
            f"V{x:.3f} {y+h:.3f}c0x1c1x1"
        ]
        
        vl = ET.SubElement(shape, "VertList")
        vl.text = "".join(vertices)
        vl.tail = "\n "
        
        pl = ET.SubElement(shape, "PrimList")
        pl.text = "LineClosed"
        pl.tail = "\n "
    
    def _add_text(self, parent, element):
        """Add text shape to LightBurn XML"""
        layer_idx = str(self.layer_settings[element['layer']]['index'])
        
        shape = ET.SubElement(parent, "Shape", Type="Text", CutIndex=layer_idx)
        shape.text = "\n "
        shape.tail = "\n "
        
        # Text properties
        ET.SubElement(shape, "Text", LText=element['text'])
        ET.SubElement(shape, "Font", Size=str(element['font_size']), Bold="False", Italic="False")
        ET.SubElement(shape, "Pos", x=str(element['x']), y=str(element['y']))
    
    def _add_notes(self, root, metadata):
        """Add project notes with generation metadata"""
        notes_text = f"""ArUCO Marker Generation Report
Generated: {metadata.get('timestamp', 'Unknown')}
Dictionary: {metadata.get('dictionary', 'Unknown')}
Grid Size: {metadata.get('rows', 'N/A')} x {metadata.get('cols', 'N/A')}
Marker Size: {metadata.get('size_mm', 'N/A')} mm
Spacing: {metadata.get('spacing_mm', 'N/A')} mm
Total Markers: {metadata.get('total_markers', 'N/A')}
Start ID: {metadata.get('start_id', 'N/A')}"""
        
        notes = ET.SubElement(root, "Notes")
        notes.text = notes_text
        notes.tail = "\n"
