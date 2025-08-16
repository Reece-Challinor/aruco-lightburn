# AI Agent Debugging Guide

## Error Monitoring System

### Automatic Error Logging
- **Frontend Errors**: Automatically logged to `/api/log-error` endpoint
- **Backend Errors**: Logged to `debug_logs.txt` with full stack traces
- **System Monitoring**: `debug_monitor.sh` provides comprehensive diagnostics

### Log Files
```bash
debug_logs.txt      # Application errors and status
ai_debug_logs.txt   # System diagnostics from monitor script
```

### Debug Endpoints
```bash
GET /api/debug/status           # Application health check
POST /api/log-error            # Frontend error logging
GET /api/dictionaries          # ArUCO dictionary validation
POST /api/preview              # Test marker generation
```

## Common Issues & Solutions

### Frontend Issues
- **JavaScript Errors**: Check browser console, errors auto-logged to backend
- **API Response Issues**: Check `result.dimensions` field presence
- **Form Validation**: Real-time validation with visual feedback

### Backend Issues
- **ArUCO Generation**: All dictionaries tested (4x4, 5x5, 6x6, 7x7)
- **LightBurn Export**: Tested with material settings
- **Database**: Optional PostgreSQL, falls back to SQLite

### Performance Fixes (v2.0.0)
- **JSON Parsing Errors**: Fixed "unexpected end of data" through optimized ArUCO rendering
- **Preview Optimization**: Uses 10px base resolution with 2px sampling for fast preview
- **Export Quality**: Full 200px resolution for laser cutting precision
- **API Timeouts**: Eliminated through efficient SVG generation pipeline
- **Coordinate Systems**: 3D world coordinates with millimeter precision
- **Database Performance**: Indexed tables for fast pattern retrieval

### System Diagnostics
```bash
./debug_monitor.sh status      # Basic health check
./debug_monitor.sh test        # API endpoint testing
./debug_monitor.sh monitor     # Continuous monitoring
```

## API Testing Commands

```bash
# Test dictionary loading
curl http://localhost:5000/api/dictionaries

# Test coordinate generation
curl -X POST http://localhost:5000/api/advanced/generate_with_coordinates \
  -H "Content-Type: application/json" \
  -d '{"dictionary": "4X4_50", "marker_ids": [0, 1], "size_mm": 50}'

# Test ChArUco generation
curl -X POST http://localhost:5000/api/calibration/charuco \
  -H "Content-Type: application/json" \
  -d '{"squares_x": 8, "squares_y": 6, "square_size_mm": 30}'

# Test Hamming distance
curl -X POST http://localhost:5000/api/validation/hamming_distance \
  -H "Content-Type: application/json" \
  -d '{"id1": 0, "id2": 1, "dictionary": "4X4_50"}'

# Test ROS export
curl -X POST http://localhost:5000/api/export/ros \
  -H "Content-Type: application/json" \
  -d '{"calibration_data": {"pattern_type": "aruco"}}'

# Check application status
curl http://localhost:5000/api/debug/status
```

## Code Structure for AI Agents

### Entry Points
- `main.py` - Application entry point
- `app.py` - Flask configuration
- `aruco_generator/web.py` - All routes and API endpoints

### Core Functionality
- `aruco_generator/aruco.py` - ArUCO marker generation with coordinate systems
- `aruco_generator/calibration.py` - ChArUco boards and AprilTag generation
- `aruco_generator/exporters.py` - Professional exports (ROS, OpenCV, DXF, STL)
- `aruco_generator/validation.py` - Detection quality and testing tools
- `aruco_generator/drawing.py` - Efficient SVG rendering system
- `aruco_generator/lightburn.py` - LightBurn export with material settings
- `aruco_generator/batch.py` - Batch processing for multiple patterns

### Frontend
- `static/app.js` - Enhanced with comprehensive error handling
- `templates/index.html` - Advanced mode with OpenCV standards

### Configuration
- Environment variables optional
- Database optional (PostgreSQL or SQLite)
- All dependencies in standard Python packages