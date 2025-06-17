# ArUCO Marker Generator for LightBurn

A Flask web application that generates ArUCO markers and exports them as LightBurn (.lbrn2) files for laser cutting. Features real-time SVG preview and support for multiple ArUCO dictionary types.

## Features

- **Multiple ArUCO Dictionaries**: Support for 16 different dictionary types (4X4, 5X5, 6X6, 7X7 with various marker counts)
- **Grid Generation**: Create single markers or grids with configurable rows, columns, and spacing
- **Real-time Preview**: SVG preview showing marker layout before export
- **LightBurn Export**: Direct export to LightBurn .lbrn2 format with proper layer management
- **Responsive Interface**: Clean, professional web interface with Bootstrap 5
- **Parameter Validation**: Input validation and boundary checking

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, vanilla JavaScript, CSS3, Bootstrap 5
- **Dependencies**: OpenCV-Python, NumPy
- **Output Formats**: SVG (preview), LightBurn .lbrn2 (export)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aruco-lightburn
