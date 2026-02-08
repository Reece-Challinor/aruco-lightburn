# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ArUCO Generator v2.2.0** - Professional computer vision marker generation suite with native LightBurn laser cutting integration. Flask-based web application for generating ArUCO markers, ChArUco calibration boards, and AprilTags with multi-format export capabilities.

## Essential Reading

**CRITICAL**: Before modifying this codebase, read these files in order:

1. **[AGENTS.md](AGENTS.md)** - Prime Directive, operational protocols, validation gates, and quality standards
2. **[AI_NAVIGATION.xml](AI_NAVIGATION.xml)** - Authoritative source of truth for code structure with exact line references
3. **[README.md](README.md)** - Project architecture, quick start, and module overview
4. **[docs/ai/](docs/ai/)** - Active task tracking, implementation plans, and delivery summaries

## Common Development Commands

### Development Lifecycle
```bash
make install-dev      # Install all dependencies (pytest, black, flake8, etc.)
make dev              # Start Flask dev server with auto-reload on port 5000
make format           # Auto-format code with Black + isort
make lint             # Run flake8 linting
```

### Testing
```bash
make test             # Run unit + integration + UI tests
make unit-test        # Core generation, utils, calibration tests only
make test-api         # REST API endpoint integration tests
make test-ui          # UI smoke tests (templates + JavaScript)
make test-qa          # Quality assurance (generation quality + export snapshots)
make test-health      # Health endpoint checks
make coverage         # Full test suite with HTML/XML coverage reports
```

### Validation (REQUIRED before commits)
```bash
make validate         # Full validation: format-check + lint + test + test-qa
make ci               # Full CI simulation: clean + format-check + lint + test + coverage
```

### Production
```bash
make install          # Install production dependencies only
make run              # Start Gunicorn production server on port 5000
make db-init          # Initialize SQLAlchemy database
```

### Docker
```bash
docker-compose up     # Start app + PostgreSQL + nginx
docker-compose down   # Stop all services
```

## Architecture Overview

### Core Entry Points
- **`app.py:210`** - Flask application factory (`create_app()`)
- **`aruco_generator/core/aruco.py:298`** - `ArUCOGenerator` class initialization

### Module Structure
```
aruco_generator/
├── core/                    # Core generation logic
│   ├── aruco.py            # ArUCOGenerator class (OpenCV + fallback)
│   ├── drawing.py          # DrawingContext (SVG rendering)
│   ├── observability.py    # Request tracing, health metrics
│   └── utils.py            # Shared utilities
│
├── web/                     # Flask API blueprints
│   ├── web.py              # Main endpoints (preview, download, health)
│   ├── advanced_web.py     # 3D coordinates, validation, exports
│   └── calibration_web.py  # Camera calibration patterns
│
├── export/                  # Export formatters
│   ├── lightburn.py        # LightBurn .lbrn2 exporter
│   ├── exporters.py        # SVG, PDF, YAML, DXF, STL
│   └── batch.py            # Batch export processing
│
├── calibration/            # Camera calibration
│   └── calibration.py      # ChArUco, ArUco boards, AprilTags
│
├── validation/             # Quality assurance
│   └── validation.py       # Hamming distance, quality checks
│
└── db/                      # Database layer
    ├── extensions.py       # Shared SQLAlchemy instance
    └── models.py           # CalibrationPattern, DetectionMetric
```

### Frontend Structure
```
static/
├── js/
│   ├── core/
│   │   ├── api.js          # APIClient, ArUCOAPI classes
│   │   ├── state.js        # Frontend state management
│   │   └── notifications.js # Toast notifications
│   └── pages/
│       ├── generate.js     # GenerateManager (simple/advanced/batch)
│       ├── calibration.js  # CalibrationManager
│       └── validation.js   # ValidationManager
└── css/
    └── calibration.css     # Calibration-specific styling
```

## Key Architectural Patterns

### OpenCV Integration with Graceful Fallback
- **Location**: `aruco_generator/core/aruco.py:283-293`
- **Pattern**: Strategy pattern with OpenCV or fallback dictionary generation
- **Rationale**: Ensures marker generation works even without OpenCV installed

### Modular Flask Blueprints
- **Pattern**: Three separate blueprints (web, advanced_web, calibration_web)
- **Rationale**: Separation of concerns, prevents circular imports
- **CRITICAL**: Never import `app` in modules imported by `app.py`

### Error Handling Strategy
- **Documentation**: See `docs/ai/ERROR_HANDLING.md`
- **Pattern**: Specific validation messages over generic errors
- **Example**: `"Marker size must be positive (in millimeters)"` not `"Invalid input"`
- **Anti-pattern**: Self-referential "check your parameters" messages

### Rectangle Merging Optimization
- **Location**: `aruco_generator/core/drawing.py`
- **Pattern**: 2D rectangle optimization for efficient SVG rendering
- **Performance**: O(n²) complexity in `_find_merged_rectangles()`

## Critical Protocols

### 1. Navigation Map Discipline
- **`AI_NAVIGATION.xml`** is the authoritative source of truth
- When code structure or key line numbers change, **update the XML immediately**
- Line references must remain accurate for AI agent navigation

### 2. Documentation Headers
Every file must maintain its `<ai_agent_documentation>` header with:
- `<name>` - Filename
- `<version>` - File version (increment on significant changes)
- `<type>` - File type (e.g., core_logic, api_endpoint)
- `<purpose>` - Brief description
- `<last_updated>` - ISO date (YYYY-MM-DD)

### 3. Validation Gate (MANDATORY)
Run `make validate` after every significant change. This runs:
- Format checking (Black + isort)
- Linting (flake8)
- Full test suite
- Quality assurance tests

For refactors touching UI + backend, also run: `make integration`

### 4. Release Workflow
When releasing new versions, update:
- `pyproject.toml` - version field
- `aruco_generator/__init__.py` - `__version__`
- `docs/CHANGELOG.md` - release notes (Keep a Changelog format)
- `AI_NAVIGATION.xml` - version attribute

Follow the deployment checklist: `docs/deployment_checklist.md`

## API Endpoints Quick Reference

### Core Generation (`web.py`)
- `GET /api/dictionaries` - Available ArUCO dictionaries
- `POST /api/preview` - Generate SVG preview
- `POST /api/download` - Download LightBurn .lbrn2 file
- `GET /api/health` - Comprehensive health check with dependency status
- `GET /api/healthz` - Lightweight health probe

### Advanced Features (`advanced_web.py`)
- `POST /api/advanced/generate_with_coordinates` - 3D coordinate generation
- `POST /api/validation/test_pattern` - Multi-scale test patterns
- Export endpoints: `/api/export/yaml`, `/api/export/pdf`, `/api/export/dxf`, `/api/export/stl`

### Calibration (`calibration_web.py`)
- `POST /calibration/charuco` - ChArUco board generation
- `POST /calibration/aruco_board` - ArUco calibration boards
- `POST /calibration/apriltag` - AprilTag generation

## Database Configuration

- **Production**: PostgreSQL via `DATABASE_URL` environment variable
- **Development**: SQLite (fallback if PostgreSQL unavailable)
- **Models**: `CalibrationPattern`, `DetectionMetric`, `User`
- **Initialization**: `make db-init`
- **Graceful degradation**: App works without database

## Testing Strategy

### Test Categories
- **Unit**: Generator logic, utilities, calibration algorithms (`make unit-test`)
- **Integration**: API endpoints, database queries (`make test-api`)
- **UI Smoke**: Template rendering, JavaScript controllers (`make test-ui`)
- **Quality Assurance**: Generation artifacts, export validation (`make test-qa`)
- **Snapshot**: Export output consistency (`test_export_snapshots.py`)

### Test Files
- `test_aruco_generator.py` - Core ArUCOGenerator tests
- `test_api_endpoints.py` - REST API integration
- `test_ui_pages.py` - UI smoke tests
- `test_generation_quality.py` - Quality metrics (no line artifacts, proper scaling)
- `test_export_formats.py` - Export format validation
- `test_export_snapshots.py` - Snapshot testing for exports

### Coverage Target
- **Target**: 70%+ (currently ~68%)
- **Report**: `make coverage` generates HTML, terminal, and XML reports

## Development Workflow

### Standard Workflow
1. **READ**: Locate files in `AI_NAVIGATION.xml`
2. **PLAN**: For complex changes, update `docs/ai/implementation_plan.md`
3. **EDIT**: Make focused changes maintaining stable API contracts
4. **VALIDATE**: Run `make validate` (REQUIRED)
5. **DOCUMENT**: Update `docs/ai/walkthrough.md` and `docs/ai/task.md`

### Common Tasks

#### Adding a New API Endpoint
1. Add route in appropriate blueprint (`web/web.py` or `web/advanced_web.py`)
2. Follow error handling patterns from `docs/ai/ERROR_HANDLING.md`
3. Add tests in `tests/test_api*.py`
4. Update `AI_NAVIGATION.xml` with new endpoint details

#### Extending ArUCO Functionality
1. Modify `ArUCOGenerator` class in `core/aruco.py:298`
2. Add comprehensive docstring with ASCII diagrams (project convention)
3. Update `get_dictionary_info()` if new dictionaries added
4. Add tests in `tests/test_aruco_generator.py`

#### Adding Export Format
1. Extend `export/exporters.py` with new exporter class
2. Add API endpoint in appropriate blueprint
3. Add tests in `tests/test_export_formats.py`
4. Add snapshot test in `tests/test_export_snapshots.py`

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- Trailing whitespace, EOF fixes
- YAML/JSON validation
- Black + isort formatting
- flake8 linting
- Bandit security checks
- Custom quality hooks:
  - Generation quality validation (no line artifacts)
  - Export format consistency
  - Marker scaling quality
  - UI/API smoke tests

**Install**: `make pre-commit-install`

## Performance Hotspots

1. **Marker Generation** (`aruco_generator/core/aruco.py:generate_marker`)
   - OpenCV: ~0.1ms, Fallback: ~1ms
   - Optimize for batch operations

2. **Rectangle Merging** (`aruco_generator/core/drawing.py:_find_merged_rectangles`)
   - O(n²) complexity
   - Consider optimization for large grids

3. **Frontend API Calls** (`static/js/core/api.js`)
   - Consider caching dictionary info to reduce API calls

## Observability

### Request Tracing
- Request IDs propagated through `observability.py`
- Error heuristics and latency tracking
- Health metrics aggregation

### Health Endpoints
- `/api/health` - Comprehensive status (OpenCV, database, dependencies)
- `/api/healthz` - Lightweight probe for container orchestration

### Monitoring
- Capture request IDs in error reports for debugging
- Error rate warnings in health endpoint
- Latency tracking for performance monitoring

## Dependencies

### Core
- Flask 3.1.1+ (web framework)
- SQLAlchemy 2.0.41+ (ORM)
- OpenCV 4.11.0+ (computer vision, headless)
- NumPy 1.26.4 (numerical operations)
- Gunicorn 23.0.0+ (production server)

### Development
- pytest 8.0.0+ (testing framework)
- pytest-cov 4.1.0+ (coverage)
- Black 24.0.0+ (formatting)
- flake8 7.0.0+ (linting)
- isort (import sorting)
- pre-commit (git hooks)

### Optional
- PostgreSQL 15+ (production database)
- reportlab (PDF export)

## Branching & PR Strategy

- **Feature branches**: Use `codex/` prefix (e.g., `codex/new-export-format`)
- **Commits**: Follow conventional commit format
- **PRs**: Create summary in `docs/ai/walkthrough.md` before submission
- **Tags**: Annotated tags for releases (e.g., `v2.2.0`)

## CI/CD Pipeline

**GitHub Actions** (`.github/workflows/deploy.yml`):
1. **Quality Gate** - Format check, lint, tests, coverage (always runs)
2. **Deploy to Staging** - Vercel deployment (on develop branch)
3. **Deploy to Production** - Vercel deployment (on main branch)
4. **Docker Build** - Multi-platform build, push to Docker Hub

## Docker Configuration

### Multi-stage Build
- Base: Python 3.11-slim
- Runtime user: aruco:1000 (non-root)
- Port: 5000
- Server: Gunicorn (2 workers, 2 threads)
- Health check: Built-in HTTP probe

### Docker Compose Services
- **app**: Flask application
- **db**: PostgreSQL 15-alpine
- **nginx**: Reverse proxy (optional, production profile)

## Project Versioning

**Current Version**: 2.2.0

Version scheme: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, minor improvements

See `docs/CHANGELOG.md` for full release history.

## Additional Resources

- **Active Tasks**: `docs/ai/task.md`
- **Implementation Plans**: `docs/ai/implementation_plan.md`
- **Delivery Summaries**: `docs/ai/walkthrough.md`
- **Quality Standards**: `docs/GENERATION_QUALITY.md`
- **Error Handling Guide**: `docs/ai/ERROR_HANDLING.md`
- **Navigation Tree**: `docs/ai/NAVIGATION.md`

## Quick Productivity Tips

1. **Use AI_NAVIGATION.xml** for exact file locations and line references
2. **Run `make validate`** before every commit
3. **Check AGENTS.md** for operational protocols and quality gates
4. **Update documentation headers** when modifying files
5. **Follow error handling patterns** from `docs/ai/ERROR_HANDLING.md`
6. **Use `make dev`** for fast iteration with auto-reload
7. **Reference existing tests** when adding new functionality
8. **Keep line references accurate** in AI_NAVIGATION.xml

## Support

For issues or questions:
- Check existing documentation in `docs/` directory
- Review test files for usage examples
- Consult `AGENTS.md` for development protocols
- See `AI_NAVIGATION.xml` for code structure navigation
