"""
{
  "file_type": "python_package_init",
  "purpose": "ArUCO generator package initialization",
  "package_structure": {
    "aruco.py": "Core ArUCO marker generation with OpenCV",
    "drawing.py": "SVG drawing context and rendering",
    "lightburn.py": "LightBurn .lbrn2 file export functionality",
    "web.py": "Flask routes and API endpoints",
    "batch.py": "Batch processing for multiple markers"
  },
  "ai_navigation": {
    "entry_point": "web.py for routes, aruco.py for core functionality",
    "modify_for": "Adding new modules to the package"
  }
}
"""

__version__ = "1.0.0"
__author__ = "ArUCO Generator Team"