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
-->

**Professional ArUCO marker generator for computer vision and laser cutting**

Generate precise ArUCO markers with real-time preview and export to LightBurn format for laser cutting. Built for computer vision applications with OpenCV standard compliance.

## Features

• **Multiple ArUCO Dictionaries** - 4x4, 5x5, 6x6, 7x7 with proper OpenCV categorization  
• **Real-time Preview** - SVG preview with dimension calculations  
• **Laser Cut Ready** - Direct export to LightBurn (.lbrn2) format  
• **Advanced Configuration** - Grid layouts, custom sizing, spacing control  
• **Production Ready** - Comprehensive error handling and validation  

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

## Usage

1. **Simple Mode** - One-click generation for common use cases
2. **Advanced Mode** - Full parameter control with OpenCV standards
3. **Quick Test** - Instant 2x2 inch markers for laser testing

## API Endpoints

- `GET /api/dictionaries` - Available ArUCO dictionaries
- `POST /api/preview` - Generate SVG preview
- `POST /api/download` - Download LightBurn file
- `POST /api/quick-test` - Quick test generation

## License

MIT License - Use freely for any purpose.

## Architecture

Built with Flask backend, vanilla JavaScript frontend, and comprehensive error logging for AI agent debugging.