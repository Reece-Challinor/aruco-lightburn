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

**Professional ArUCO marker generator for computer vision and laser cutting**

Generate precise ArUCO markers with real-time preview and export to LightBurn format for laser cutting. Built for computer vision applications with OpenCV standard compliance.

## Features

• **Multiple ArUCO Dictionaries** - 4x4, 5x5, 6x6, 7x7 with proper OpenCV categorization  
• **Real-time Preview** - Optimized SVG preview showing actual ArUCO QR codes  
• **Laser Cut Ready** - Direct export to LightBurn (.lbrn2) format with full resolution  
• **Advanced Configuration** - Grid layouts, custom sizing, spacing control  
• **Performance Optimized** - Efficient rendering prevents JSON parsing errors  
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
- `POST /api/preview` - Generate optimized SVG preview with actual ArUCO patterns
- `POST /api/download` - Download full-resolution LightBurn file
- `POST /api/quick-test` - Quick test generation

## Performance Features

**Preview Optimization**: ArUCO preview generation uses pixel sampling (every 2nd pixel) with 10px base resolution to prevent JSON parsing timeouts while maintaining visual accuracy.

**Export Quality**: File downloads use full-resolution ArUCO generation (200px default) for precise laser cutting requirements.

**Error Prevention**: Comprehensive validation prevents "unexpected end of data" JSON errors through optimized rendering pipelines.

## License

MIT License - Use freely for any purpose.

## Architecture

Built with Flask backend, vanilla JavaScript frontend, and comprehensive error logging for AI agent debugging.