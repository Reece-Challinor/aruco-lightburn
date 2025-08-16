# ArUCO Generator

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9-red.svg)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()

<!--
AI AGENT NOTES:
- Full error logging system in place with debug_logs.txt and ai_debug_logs.txt
- Comprehensive frontend error handling with /api/log-error endpoint
- Debug monitor script at debug_monitor.sh for system diagnostics
- All API endpoints tested and working: /api/preview, /api/download, /api/quick-test
- Enhanced advanced mode with OpenCV ArUCO standards compliance
- Real-time validation and form feedback implemented
- Size presets and dictionary categorization following OpenCV standards
- FIXED: JSON parsing errors in preview generation - optimized ArUCO rendering
- Preview now shows actual ArUCO QR codes with efficient pixel sampling
- Download exports use full-resolution ArUCO markers for laser cutting precision
-->

**Professional ArUCO marker generator for computer vision, calibration, and laser cutting**

Generate precise ArUCO markers, ChArUco boards, and AprilTags with enhanced navigation, real-time preview, coordinate systems, and export to multiple professional formats including LightBurn, ROS, OpenCV YAML, DXF, and STL. Built for computer vision applications with OpenCV standard compliance.

## What's New in Version 4.0

• **Enhanced Navigation** - Global navbar with breadcrumbs and keyboard shortcuts  
• **Unified UI** - Consistent base template with purple gradient theme throughout  
• **Dedicated Pages** - Separate pages for Generate, Calibration, Validation, Documentation  
• **Improved Routing** - URL-based tab navigation with state persistence  
• **Responsive Design** - Mobile-optimized with touch-friendly controls  
• **Modular JavaScript** - Separated core navigation, API client, state management  
• **Comprehensive Testing** - Added test suites for navigation and API endpoints

## Features

• **Enhanced Navigation** - Global navigation bar with breadcrumbs and keyboard shortcuts (Alt+H, Alt+G, Alt+C, Alt+V)  
• **Multiple Pattern Types** - ArUCO markers, ChArUco boards, AprilTags for calibration  
• **3D Coordinate Systems** - World coordinates with physical dimensions in mm  
• **Professional Export Formats** - LightBurn, ROS, OpenCV YAML, DXF (CNC), STL (3D printing)  
• **Validation Center** - Dedicated page for marker testing, Hamming distance calculation, quality metrics  
• **Documentation Hub** - Comprehensive built-in documentation with best practices  
• **Real-time Preview** - Optimized SVG preview showing actual patterns  
• **Database Tracking** - PostgreSQL backend for calibration patterns and detection metrics  
• **Responsive Design** - Mobile-first design with touch-optimized controls  
• **Production Ready** - Comprehensive error handling, validation, and testing  

## Quick Start

```bash
# Clone and run
git clone https://github.com/yourusername/aruco-generator.git
cd aruco-generator
python main.py
```

Open `http://localhost:5000` - Generate markers instantly.

## Requirements

- Python 3.11+
- OpenCV Python
- Flask
- PostgreSQL (optional)

## Navigation

### Pages
- **Home** (`/`) - Landing page with feature overview and quick start guide
- **Generate** (`/generate`) - Main marker generation with Quick, Advanced, and Batch tabs
- **Calibration** (`/calibration`) - ChArUco boards, AprilTags, and calibration patterns
- **Validation** (`/validation`) - Test detection quality, calculate Hamming distances
- **Documentation** (`/documentation`) - Built-in help and API reference

### Keyboard Shortcuts
- `Alt + H` - Go to Home
- `Alt + G` - Go to Generate
- `Alt + C` - Go to Calibration  
- `Alt + V` - Go to Validation
- `?` - Show keyboard shortcuts

## Usage

1. **Quick Generate** - One-click generation for common use cases
2. **Advanced Mode** - Full parameter control with OpenCV standards
3. **Batch Generation** - Generate multiple marker sets with presets
4. **Validation Testing** - Upload images to test detection quality

## API Endpoints

### Core Generation
- `GET /api/dictionaries` - Available ArUCO dictionaries
- `POST /api/preview` - Generate optimized SVG preview
- `POST /api/download` - Download full-resolution LightBurn file
- `POST /api/batch_generate` - Batch marker generation

### Calibration Patterns
- `POST /api/calibration/charuco` - ChArUco board generation
- `POST /api/calibration/aruco_board` - ArUCO board with fixed grid
- `POST /api/calibration/apriltag` - Single AprilTag markers
- `POST /api/calibration/apriltag_grid` - AprilTag grids

### Advanced Features
- `POST /api/advanced/generate_with_coordinates` - Markers with 3D coordinates
- `POST /api/advanced/pose_estimation_board` - Optimized for pose estimation

### Professional Export
- `POST /api/export/opencv_yaml` - OpenCV calibration format
- `POST /api/export/ros` - ROS calibration messages
- `POST /api/export/dxf` - DXF for CNC/laser cutting
- `POST /api/export/stl` - STL for 3D printing landing pads

### Validation & Testing
- `POST /api/validation/test_pattern` - Multi-scale test patterns
- `POST /api/validation/hamming_distance` - Marker confusion metrics
- `POST /api/validation/verify_quality` - Quality verification
- `POST /api/validation/detection_report` - Detection performance reports

## Performance Features

**Preview Optimization**: ArUCO preview generation uses pixel sampling (every 2nd pixel) with 10px base resolution to prevent JSON parsing timeouts while maintaining visual accuracy.

**Export Quality**: File downloads use full-resolution ArUCO generation (200px default) for precise laser cutting requirements.

**Error Prevention**: Comprehensive validation prevents "unexpected end of data" JSON errors through optimized rendering pipelines.

## License

MIT License - Use freely for any purpose.

## Architecture

### Backend
- **Flask** - Web framework with modular route organization
- **OpenCV** - ArUCO marker generation and computer vision
- **PostgreSQL** - Database for calibration patterns and metrics
- **SQLAlchemy** - ORM for database operations

### Modules
- `aruco_generator/aruco.py` - Core ArUCO generation with coordinate systems
- `aruco_generator/calibration.py` - ChArUco and AprilTag generation
- `aruco_generator/exporters.py` - Professional format exports (ROS, DXF, STL)
- `aruco_generator/validation.py` - Detection quality and testing tools
- `aruco_generator/drawing.py` - SVG rendering and visualization
- `aruco_generator/lightburn.py` - LightBurn laser cutting export

### Database Schema
- `calibration_patterns` - Pattern metadata and configurations
- `detection_metrics` - Performance tracking (detection rate, pose error)
- `calibration_sessions` - Camera calibration results
- `drone_landing_patterns` - Specialized drone landing pads