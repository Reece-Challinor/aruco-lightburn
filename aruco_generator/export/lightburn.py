"""
{
  "file_type": "lightburn_exporter",
  "purpose": "Export ArUCO markers to LightBurn .lbrn2 format for laser cutting",
  "last_updated": "2026-02-06",
  "dependencies": ["xml.etree.ElementTree", "drawing.py"],
  "main_class": "LightBurnExporter",
  "key_methods": {
    "export": "Export drawing context to LightBurn format with material settings",
    "get_material_info": "Return material configuration for UI",
    "_add_material_cut_settings": "Add laser cutting parameters",
    "_add_enhanced_notes": "Add metadata and material info"
  },
  "material_presets": {
    "1_16_cast_acrylic": "Default 1/16 inch cast acrylic settings",
    "cut_layer": "Layer 1 - cutting operations",
    "engrave_layer": "Layer 0 - engraving operations",
    "mark_layer": "Layer 30 - marking operations"
  },
  "ai_navigation": {
    "modify_for": "Adding new materials or laser settings",
    "used_by": ["web.py"],
    "output_format": "LightBurn .lbrn2 XML files"
  }
}
"""

import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Any, Dict

from ..core.drawing import DrawingContext


class LightBurnExporter:
    def __init__(self):
        self.materials_file = "materials.json"

        # Default settings
        self.material_settings = {
            "1_16_cast_acrylic": {
                "name": '1/16" Cast Acrylic (Default)',
                "description": "White/Black 2-Ply Cast Acrylic",
                "cut_speed": 150,  # mm/min
                "cut_power": 75,  # %
                "cut_passes": 1,
                "engrave_speed": 800,  # mm/min
                "engrave_power": 45,  # %
                "mark_speed": 1000,  # mm/min
                "mark_power": 20,  # %
            }
        }

        # Try to load custom settings
        self._load_materials()

    def _load_materials(self):
        """Load material settings from JSON file if available matches"""
        import json
        import os

        if os.path.exists(self.materials_file):
            try:
                with open(self.materials_file, "r") as f:
                    custom_settings = json.load(f)
                    self.material_settings.update(custom_settings)
            except Exception as e:
                print(f"Warning: Failed to load {self.materials_file}: {e}")

        # Layer configuration with material-specific settings
        self.layer_settings = {
            0: {
                "index": "0",
                "name": "ArUCO Fill",
                "type": "Cut",
                "priority": "2",
                "operation": "engrave",
            },
            1: {
                "index": "1",
                "name": "ArUCO Border",
                "type": "Cut",
                "priority": "1",
                "operation": "cut",
            },
            2: {
                "index": "30",
                "name": "ArUCO Labels",
                "type": "Tool",
                "priority": "0",
                "operation": "mark",
            },
        }

    def export(
        self,
        context: DrawingContext,
        metadata: Dict[str, Any] | None = None,
        material: str = "1_16_cast_acrylic",
    ) -> BytesIO:
        """Export drawing context to LightBurn .lbrn2 format with material settings"""

        # Create root element
        root = ET.Element(
            "LightBurnProject",
            {
                "AppVersion": "1.0.06",
                "FormatVersion": "1",
                "MaterialHeight": "1.5875",  # 1/16" in mm
                "MirrorX": "False",
                "MirrorY": "False",
            },
        )
        root.text = "\n"

        # Add material-specific cut settings
        self._add_material_cut_settings(root, material)

        # Create main shape group
        main_group = ET.SubElement(root, "Shape", Type="Group")
        main_group.text = "\n "
        main_group.tail = "\n"

        children = ET.SubElement(main_group, "Children")
        children.text = "\n "
        children.tail = "\n"

        # Add all drawing elements
        for element in context.elements:
            if element["type"] == "rect":
                self._add_rectangle(children, element)
            elif element["type"] == "text":
                self._add_text(children, element)

        # Add enhanced metadata with material info
        if metadata:
            self._add_enhanced_notes(root, metadata, material)

        # Generate XML output
        tree = ET.ElementTree(root)
        output = BytesIO()
        tree.write(output, encoding="utf-8", xml_declaration=True, method="xml")
        output.write(b"\n")
        output.seek(0)
        return output

    def _add_material_cut_settings(self, root, material: str):
        """Add material-specific cut settings for different layers"""
        material_config = self.material_settings.get(
            material, self.material_settings["1_16_cast_acrylic"]
        )

        for layer_id, layer_config in self.layer_settings.items():
            operation = layer_config["operation"]

            # Create cut setting element
            cs = ET.SubElement(root, "CutSetting", Type=layer_config["type"])
            ET.SubElement(cs, "index", Value=layer_config["index"])
            ET.SubElement(cs, "name", Value=layer_config["name"])
            ET.SubElement(cs, "priority", Value=layer_config["priority"])

            # Add operation-specific settings
            if operation == "cut":
                ET.SubElement(cs, "runBlower", Value="1")
                ET.SubElement(cs, "speed", Value=str(material_config["cut_speed"]))
                ET.SubElement(cs, "maxPower", Value=str(material_config["cut_power"]))
                ET.SubElement(cs, "minPower", Value=str(material_config["cut_power"]))
                ET.SubElement(cs, "numPasses", Value=str(material_config["cut_passes"]))
                ET.SubElement(cs, "zOffset", Value="0")
                ET.SubElement(cs, "perforate", Value="0")
                ET.SubElement(cs, "overcut", Value="0")
                ET.SubElement(cs, "tabsEnabled", Value="0")

            elif operation == "engrave":
                ET.SubElement(cs, "runBlower", Value="1")
                ET.SubElement(cs, "speed", Value=str(material_config["engrave_speed"]))
                ET.SubElement(
                    cs, "maxPower", Value=str(material_config["engrave_power"])
                )
                ET.SubElement(
                    cs, "minPower", Value=str(material_config["engrave_power"])
                )
                ET.SubElement(cs, "perforate", Value="0")
                ET.SubElement(cs, "overcut", Value="0")
                ET.SubElement(cs, "priority", Value=layer_config["priority"])

            elif operation == "mark":
                ET.SubElement(cs, "speed", Value=str(material_config["mark_speed"]))
                ET.SubElement(cs, "maxPower", Value=str(material_config["mark_power"]))
                ET.SubElement(cs, "minPower", Value=str(material_config["mark_power"]))
                ET.SubElement(cs, "perforate", Value="0")

    def _add_rectangle(self, parent, element):
        """Add rectangle shape to LightBurn XML"""
        layer_idx = str(self.layer_settings[element["layer"]]["index"])

        shape = ET.SubElement(parent, "Shape", Type="Path", CutIndex=layer_idx)
        shape.text = "\n "
        shape.tail = "\n "

        # Create rectangle vertices
        x, y = element["x"], element["y"]
        w, h = element["width"], element["height"]

        vertices = [
            f"V{x:.3f} {y:.3f}c0x1c1x1",
            f"V{x + w:.3f} {y:.3f}c0x1c1x1",
            f"V{x + w:.3f} {y + h:.3f}c0x1c1x1",
            f"V{x:.3f} {y + h:.3f}c0x1c1x1",
        ]

        vl = ET.SubElement(shape, "VertList")
        vl.text = "".join(vertices)
        vl.tail = "\n "

        pl = ET.SubElement(shape, "PrimList")
        pl.text = "LineClosed"
        pl.tail = "\n "

    def _add_text(self, parent, element):
        """Add text shape to LightBurn XML"""
        layer_idx = str(self.layer_settings[element["layer"]]["index"])

        shape = ET.SubElement(parent, "Shape", Type="Text", CutIndex=layer_idx)
        shape.text = "\n "
        shape.tail = "\n "

        # Text properties
        ET.SubElement(shape, "Text", LText=element["text"])
        ET.SubElement(
            shape, "Font", Size=str(element["font_size"]), Bold="False", Italic="False"
        )
        ET.SubElement(shape, "Pos", x=str(element["x"]), y=str(element["y"]))

    def _add_enhanced_notes(self, root, metadata, material: str):
        """Add enhanced metadata with material and settings info"""
        material_config = self.material_settings.get(
            material, self.material_settings["1_16_cast_acrylic"]
        )

        notes_text = "ArUCO Marker Generator - Optimized for Laser Cutting\n\n"
        notes_text += "=== GENERATION SETTINGS ===\n"
        for key, value in metadata.items():
            notes_text += f"{key}: {value}\n"

        notes_text += "\n=== MATERIAL SETTINGS ===\n"
        notes_text += f"Material: {material_config['name']}\n"
        notes_text += f"Description: {material_config['description']}\n"
        notes_text += 'Thickness: 1/16" (1.5875mm)\n\n'

        notes_text += "=== RECOMMENDED LASER SETTINGS ===\n"
        notes_text += f"Border Cut: {material_config['cut_speed']}mm/min @ {material_config['cut_power']}% power\n"
        notes_text += f"Fill Engrave: {material_config['engrave_speed']}mm/min @ {material_config['engrave_power']}% power\n"
        notes_text += f"Label Mark: {material_config['mark_speed']}mm/min @ {material_config['mark_power']}% power\n\n"

        notes_text += "=== LAYER INFORMATION ===\n"
        notes_text += "Layer 00 (Black): ArUCO marker fill areas - ENGRAVE\n"
        notes_text += "Layer 01 (Blue): Border outlines - CUT\n"
        notes_text += "Layer T1 (Red): ID labels - MARK/ENGRAVE\n\n"

        notes_text += "=== USAGE INSTRUCTIONS ===\n"
        notes_text += "1. Load material and set focus height\n"
        notes_text += "2. Review and adjust laser settings if needed\n"
        notes_text += "3. Run test cuts on scrap material first\n"
        notes_text += "4. Process layers in order: Fill (engrave) → Borders (cut) → Labels (mark)\n"
        notes_text += "5. Use air assist for clean cuts and prevent charring"

        notes = ET.SubElement(root, "Notes", ShowOnLoad="1", Notes=notes_text)
        notes.text = ""
        notes.tail = "\n"

    def get_material_info(self) -> Dict[str, Any]:
        """Return material configuration info for UI"""
        return self.material_settings

    def create_lightburn_file(
        self,
        markers,
        size_mm,
        border_bits=1,
        include_labels=False,
        include_alignment=False,
        include_rulers=False,
    ):
        """Create LightBurn file from markers (backward compatibility wrapper)"""
        from ..core.drawing import DrawingContext

        # Create drawing context
        context = DrawingContext()

        # Add markers to context
        for marker in markers:
            # Add marker rectangles
            x = marker.get("x", 0)
            y = marker.get("y", 0)

            # Add filled rectangle for marker
            context.add_rectangle(x, y, size_mm, size_mm, fill=True, layer=0)

            # Add border if requested
            if border_bits > 0:
                border_width = size_mm * 0.1  # 10% of size for border
                context.add_rectangle(
                    x - border_width,
                    y - border_width,
                    size_mm + 2 * border_width,
                    size_mm + 2 * border_width,
                    fill=False,
                    layer=1,
                )

            # Add labels if requested
            if include_labels:
                # Text labels are added as elements directly
                context.elements.append(
                    {
                        "type": "text",
                        "x": x + size_mm / 2,
                        "y": y - 2,
                        "text": f"ID: {marker.get('id', '?')}",
                        "layer": 2,
                        "font_size": 8,
                        "anchor": "middle",
                    }
                )

        # Create metadata
        metadata = {
            "marker_count": len(markers),
            "size_mm": size_mm,
            "border_bits": border_bits,
            "include_labels": include_labels,
        }

        # Export to BytesIO
        output = self.export(context, metadata)

        # Return as string for compatibility
        return output.getvalue().decode("utf-8")
