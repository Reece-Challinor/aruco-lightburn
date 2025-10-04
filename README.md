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

**Version 3.0.0** - This repository includes comprehensive documentation optimized for developers and AI agents:

### 📁 Core Navigation Files
- **[NAVIGATION.md](NAVIGATION.md)** - ASCII tree structure with method navigation and quick file location references
- **[AI_NAVIGATION.xml](AI_NAVIGATION.xml)** - Structured XML descriptors for AI agent navigation with line references
- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error patterns, anti-patterns, and self-referential message analysis

### 📚 Development Documentation
- **[AI_IMPROVEMENT_OBJECTIVES.md](AI_IMPROVEMENT_OBJECTIVES.md)** - AI development guidelines and objectives (v3.0.0)
- **[IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md)** - Detailed implementation roadmap and progress tracking (v3.0.0)
- **[docs/GENERATION_QUALITY.md](docs/GENERATION_QUALITY.md)** - Quality standards and validation criteria
- **[replit.md](replit.md)** - Replit-specific setup and configuration

### 🎯 Quick AI Navigation (Enhanced v3.0.0)
For AI agents working with this codebase:
- **Core Logic**: `aruco_generator/aruco.py` (ArUCOGenerator class with comprehensive XML documentation)
- **API Endpoints**: `aruco_generator/web.py` (Flask routes with golden path documentation)
- **Frontend API**: `static/js/core/api.js` (API client with complete method documentation)
- **Error Patterns**: Comprehensive documentation in ERROR_HANDLING.md

### 🔧 XML Documentation System
All major files now include comprehensive XML-based AI-friendly headers containing:
- **Golden Path Workflows**: Step-by-step primary usage patterns
- **API Specifications**: Complete parameter and response documentation
- **Data Structures**: Detailed field descriptions and types
- **Error Handling**: Validation rules and fallback strategies
- **Performance Notes**: Bottlenecks and optimization guidance
- **Security Considerations**: Input validation and protection measures

## Testing

**Current Status**: 59 passed, 7 skipped (100% pass rate for running tests)

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
