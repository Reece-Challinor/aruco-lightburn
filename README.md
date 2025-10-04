# ArUCO Generator

Professional ArUCO marker generator for computer vision, calibration, and laser cutting.

## Features

- **Multiple Pattern Types** - ArUCO markers, ChArUco boards for camera calibration
- **Export Formats** - LightBurn (.lbrn2), SVG, PDF (planned), DXF, STL
- **Real-time Preview** - Interactive SVG preview with optimized rendering
- **Professional Quality** - Merged rectangle generation for minimal laser cuts
- **Calibration Tools** - Generate calibration patterns for camera systems
- **Validation Center** - Test marker quality and Hamming distances
- **Batch Generation** - Create multiple marker sets efficiently
- **Material Presets** - Pre-configured settings for common materials

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

## Documentation & Navigation

This repository includes comprehensive documentation for developers and AI agents:

### 📁 Core Navigation Files
- **[NAVIGATION.md](NAVIGATION.md)** - ASCII tree structure with method navigation and quick file location references
- **[AI_NAVIGATION.xml](AI_NAVIGATION.xml)** - Structured XML descriptors for AI agent navigation with line references
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error patterns, anti-patterns, and self-referential message analysis

### 📚 Development Documentation
- **[AI_IMPROVEMENT_OBJECTIVES.md](AI_IMPROVEMENT_OBJECTIVES.md)** - AI development guidelines and objectives
- **[IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md)** - Detailed implementation roadmap and progress tracking
- **[docs/GENERATION_QUALITY.md](docs/GENERATION_QUALITY.md)** - Quality standards and validation criteria
- **[replit.md](replit.md)** - Replit-specific setup and configuration

### 🎯 Quick AI Navigation
For AI agents working with this codebase:
- **Core Logic**: `aruco_generator/aruco.py:39` (ArUCOGenerator class)
- **API Endpoints**: `aruco_generator/web.py:55` (generate_preview)
- **Error Patterns**: Search `return jsonify.*error` across web modules
- **Frontend API**: `static/js/core/api.js:20` (API communication)

## Testing

**Current Status**: 65/66 tests passing (98.5% success rate)

```bash
# Run all tests
make test

# Run unit tests only
make unit-test

# Run integration tests only
make integration

# Run tests with coverage report
make coverage

# Run specific test groups
python3 -m pytest tests/test_api.py -v        # API endpoint tests
python3 -m pytest tests/test_aruco_generator.py -v  # Core generation tests
python3 -m pytest tests/test_export_formats.py -v   # Export format tests
```

### Quality Assurance
- **Pre-commit hooks** configured for code quality (black, isort, flake8, bandit)
- **Automated testing** validates marker generation quality
- **Export consistency** checks ensure reliable file output
- **Input validation** prevents invalid parameter combinations

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

### Core Generation
- `GET /api/dictionaries` - Get available ArUCO dictionaries
- `POST /api/preview` - Generate SVG preview with marker grid
- `POST /api/advanced_preview` - Generate advanced preview with additional options
- `POST /api/download` - Download LightBurn (.lbrn2) file

### Batch Operations
- `POST /api/batch_generate` - Generate multiple marker sets
- `GET /api/presets` - Get predefined marker configuration presets

### Export Formats
- `POST /api/export/svg` - Export markers as SVG file
- `POST /api/export/pdf` - Export markers as PDF (planned)

### Calibration
- `POST /api/calibration/charuco` - Generate ChArUco calibration boards
- `POST /api/calibration/save_pattern` - Save calibration pattern to database

### Validation & Testing
- `GET /api/quick-test` - Test API functionality
- `POST /api/validation/test_pattern` - Generate validation test patterns
- `POST /api/validation/verify_quality` - Verify marker quality
- `POST /api/validation/hamming_distance` - Calculate Hamming distances

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
