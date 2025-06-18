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

# Test preview generation
curl -X POST http://localhost:5000/api/preview \
  -H "Content-Type: application/json" \
  -d '{"dictionary": "6X6_250", "rows": 1, "cols": 1, "start_id": 0, "size_mm": 50, "spacing_mm": 10}'

# Test download
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{"dictionary": "6X6_250", "rows": 1, "cols": 1, "start_id": 0, "size_mm": 50, "spacing_mm": 10}'

# Check application status
curl http://localhost:5000/api/debug/status
```

## Code Structure for AI Agents

### Entry Points
- `main.py` - Application entry point
- `app.py` - Flask configuration
- `aruco_generator/web.py` - All routes and API endpoints

### Core Functionality
- `aruco_generator/aruco.py` - ArUCO marker generation with OpenCV
- `aruco_generator/drawing.py` - SVG rendering system
- `aruco_generator/lightburn.py` - LightBurn export with material settings

### Frontend
- `static/app.js` - Enhanced with comprehensive error handling
- `templates/index.html` - Advanced mode with OpenCV standards

### Configuration
- Environment variables optional
- Database optional (PostgreSQL or SQLite)
- All dependencies in standard Python packages