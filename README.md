# ArUCO Generator

Professional ArUCO marker generator for computer vision, calibration, and laser cutting.

## Features

- **Multiple Pattern Types** - ArUCO markers, ChArUco boards, AprilTags
- **Export Formats** - LightBurn (.lbrn2), SVG, PDF, DXF, STL
- **Real-time Preview** - Interactive SVG preview with customization
- **Calibration Tools** - Generate calibration patterns for camera systems
- **Validation Center** - Test marker quality and Hamming distances  

## Quick Start

### Installation

```bash
# Install dependencies
make install

# Install development dependencies (for testing)
make install-dev
```

### Running the Application

```bash
# Production server
make run

# Development server with auto-reload
make dev
```

The application will be available at `http://localhost:5000`

## Testing

```bash
# Run all tests
make test

# Run unit tests only
make unit-test

# Run integration tests only
make integration

# Run tests with coverage report
make coverage
```

## Project Structure

```
aruco_generator/
├── aruco_generator/     # Core marker generation logic
│   ├── aruco.py         # ArUCO marker generation
│   ├── drawing.py       # SVG drawing context
│   ├── lightburn.py     # LightBurn export
│   └── web.py           # Flask routes
├── static/              # Frontend assets
├── templates/           # HTML templates
├── tests/               # Unit and integration tests
├── app.py               # Flask application setup
└── Makefile             # Automation commands
```

## API Endpoints

- `GET /api/dictionaries` - Get available ArUCO dictionaries
- `POST /api/preview` - Generate SVG preview
- `POST /api/download` - Download LightBurn file
- `GET /api/quick-test` - Test API functionality

## Development

```bash
# Check code style
make lint

# Format code
make format

# Clean cache and temporary files
make clean

# Run full CI pipeline simulation
make ci
```

## Technologies

- **Backend**: Flask, OpenCV, NumPy
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Database**: PostgreSQL/SQLite (optional)
- **Testing**: pytest, pytest-cov

## License

MIT License - See LICENSE file for details