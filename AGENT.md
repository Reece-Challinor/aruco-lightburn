# AGENT.md - ArUCO Generator Project Documentation

**AI Assistant Reference Guide**
*Single source of truth for project structure, routes, and architecture*

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [Routes & Endpoints](#routes--endpoints)
5. [Database Models](#database-models)
6. [Frontend Architecture](#frontend-architecture)
7. [Testing](#testing)
8. [Development Workflow](#development-workflow)
9. [Deployment](#deployment)
10. [Code Standards](#code-standards)

---

## Project Overview

**ArUCO LightBurn Generator** v2.0.0
Professional computer vision marker generation suite with LightBurn export.

**Tech Stack:**
- **Backend**: Flask 3.1+ (Python 3.11+)
- **Frontend**: Vanilla JavaScript ES6+ with Bootstrap 5
- **Database**: SQLAlchemy (PostgreSQL/SQLite)
- **Computer Vision**: OpenCV 4.11+
- **Template Engine**: Jinja2
- **Server**: Gunicorn
- **Containerization**: Docker + docker-compose

**Key Features:**
- ArUCO marker generation (single/grid layouts)
- ChArUco calibration board generation
- AprilTag support
- Multi-format export (LightBurn, SVG, PDF, YAML, JSON)
- Batch generation with presets
- Validation and quality checking
- Responsive web interface

---

## Architecture

### Application Entry Points

```
app.py (main)           # Flask app initialization
└── main.py             # Gunicorn entry point (imports from app.py)
```

### Module Structure

```
aruco_generator/
├── __init__.py         # Package initialization
├── aruco.py            # Core ArUCO generation logic (38KB)
├── aruco_fallback.py   # Fallback for missing OpenCV contrib
├── web.py              # Main web routes (32KB)
├── advanced_web.py     # Advanced generation routes
├── calibration.py      # ChArUco/calibration logic (19KB)
├── calibration_web.py  # Calibration web routes
├── validation.py       # Marker validation logic (13KB)
├── validation_web.py   # Validation web routes
├── batch.py            # Batch generation logic (9.1KB)
├── drawing.py          # SVG/drawing utilities (14KB)
├── exporters.py        # Export format handlers (18KB)
└── lightburn.py        # LightBurn XML generation (12KB)
```

### Design Patterns

- **Modular Architecture**: Separate modules for web, logic, and export
- **Template Inheritance**: All pages extend `base.html`
- **API-First**: RESTful JSON API with web UI on top
- **Dependency Injection**: `window.arucoAPI` for JS modules

---

## File Structure

### Root Directory

```
/
├── app.py                          # Main Flask application
├── main.py                         # Gunicorn entry (imports app)
├── pyproject.toml                  # Python dependencies
├── Makefile                        # Dev/test automation
├── Dockerfile                      # Production container
├── docker-compose.yml              # Multi-service orchestration
├── .dockerignore                   # Docker build exclusions
├── .pre-commit-config.yaml         # Git hooks
├── .gitignore                      # Git exclusions
├── README.md                       # User documentation
└── AGENT.md                        # This file
```

### Documentation Files

```
/
├── README.md                       # Main user documentation
├── AGENT.md                        # AI assistant reference (this file)
├── AI_IMPROVEMENT_OBJECTIVES.md    # AI guidance for improvements
├── ERROR_HANDLING.md               # Error handling patterns
├── NAVIGATION.md                   # Navigation structure
├── IMPROVEMENT_PLAN.md             # Development roadmap
├── replit.md                       # Replit deployment guide
└── docs/
    └── GENERATION_QUALITY.md       # Quality assurance guide
```

### Python Modules

```
aruco_generator/
├── __init__.py         # Package init, exports main classes
├── aruco.py            # ArUCOGenerator class (core logic)
├── aruco_fallback.py   # ArUCOGeneratorFallback (no contrib)
├── web.py              # Flask routes (/api/*, /generate, etc.)
├── advanced_web.py     # /api/advanced/* routes
├── calibration.py      # ChArUco/AprilTag generation
├── calibration_web.py  # /calibration, /api/calibration/* routes
├── validation.py       # Marker quality validation
├── validation_web.py   # /validation routes
├── batch.py            # Batch generation with presets
├── drawing.py          # SVG primitives, coordinate transforms
├── exporters.py        # PDF, YAML, JSON export logic
└── lightburn.py        # LightBurn XML format
```

### Templates (Jinja2)

```
templates/
├── base.html           # Base template (nav, footer, core JS)
├── index.html          # Homepage (extends base)
├── home.html           # Alternative landing (if used)
├── generate.html       # Marker generation UI (extends base)
├── calibration.html    # Calibration patterns (extends base)
├── validation.html     # Marker validation (extends base)
└── documentation.html  # API/user docs (extends base)
```

**Template Inheritance:**
```
base.html
├── index.html          (loads: home.js)
├── generate.html       (loads: generate.js, WorkflowManager.js)
├── calibration.html    (loads: calibration.js)
├── validation.html     (loads: validation.js)
└── documentation.html  (loads: documentation.js)
```

### Static Assets

```
static/
├── css/
│   ├── main.css        # Global styles (11KB)
│   ├── navigation.css  # Nav/breadcrumb styles
│   └── workflow.css    # Generate page workflow
├── style.css           # Legacy/page-specific (7.4KB)
├── js/
│   ├── core/
│   │   ├── api.js              # window.arucoAPI (fetch wrapper)
│   │   ├── state.js            # window.appState (state mgmt)
│   │   ├── notifications.js    # Toast notifications
│   │   └── navigation-simple.js # Navigation progress
│   ├── pages/
│   │   ├── home.js             # index.html logic (339 lines)
│   │   ├── generate.js         # generate.html logic
│   │   ├── calibration.js      # calibration.html logic
│   │   └── validation.js       # validation.html logic
│   └── workflow/
│       └── WorkflowManager.js  # Multi-step generation
└── images/ (if any)
```

**JavaScript Module Pattern:**
- `base.html` loads core modules (api, state, notifications, navigation)
- Page templates load page-specific modules in `extra_js` block
- All modules use `window.*` globals for cross-module communication

### Tests

```
tests/
├── test_api.py                 # API endpoint tests
├── test_api_endpoints.py       # Detailed API tests
├── test_aruco_generator.py     # Core generation tests
├── test_export_formats.py      # Export format tests
├── test_generation_quality.py  # Quality assurance tests
└── test_navigation.py          # UI/navigation tests
```

**Test Categories:**
- **Unit Tests**: Core logic (ArUCOGenerator, exporters)
- **Integration Tests**: API endpoints, database
- **Quality Tests**: Generation artifacts, export consistency

### Database

```
instance/
└── aruco.db            # SQLite database (dev/production)
```

**Models** (defined in modules):
- `CalibrationPattern` (calibration.py)
- `ValidationResult` (validation.py)
- Other models as needed

---

## Routes & Endpoints

### Web Pages (HTML)

| Route | Template | Purpose | JS Module |
|-------|----------|---------|-----------|
| `/` | `index.html` | Homepage | `home.js` |
| `/generate` | `generate.html` | Marker generation | `generate.js` |
| `/calibration` | `calibration.html` | Calibration patterns | `calibration.js` |
| `/validation` | `validation.html` | Marker validation | `validation.js` |
| `/documentation` | `documentation.html` | API docs | `documentation.js` |

### API Endpoints (JSON)

#### Marker Generation

```python
# web.py
POST   /api/generate              # Generate markers (preview or download)
GET    /api/dictionaries           # List available ArUCO dictionaries
POST   /api/preview                # Generate SVG preview
GET    /api/download/<format>      # Download in specific format

# advanced_web.py
POST   /api/advanced/generate      # Advanced generation options
POST   /api/advanced/batch         # Batch generation
```

#### Calibration

```python
# calibration_web.py
GET    /calibration                # Calibration page
POST   /api/calibration/charuco    # Generate ChArUco board
POST   /api/calibration/apriltag   # Generate AprilTag
GET    /api/calibration/presets    # Get calibration presets
```

#### Validation

```python
# validation_web.py
GET    /validation                 # Validation page
POST   /api/validation/hamming     # Check Hamming distance
POST   /api/validation/quality     # Validate marker quality
```

#### Batch & Presets

```python
# web.py or batch routes
GET    /api/presets                # Get batch generation presets
POST   /api/batch/generate         # Generate multiple marker sets
```

#### Utility

```python
# web.py
GET    /api/debug/status           # System status
POST   /api/log-error              # Client error logging
GET    /api/quick-test             # Quick health check
```

### Route Parameters

**Common Parameters:**
```python
{
  "dictionary": str,          # e.g., "6X6_250"
  "start_id": int,            # First marker ID (0-based)
  "rows": int,                # Grid rows
  "cols": int,                # Grid columns
  "size_mm": float,           # Marker size in mm
  "spacing_mm": float,        # Gap between markers
  "include_borders": bool,    # White borders
  "include_labels": bool,     # ID labels
  "include_outer_border": bool, # Outer frame
  "border_width": float,      # Border thickness (mm)
  "format": str               # "lbrn2", "svg", "pdf", "yaml", "json"
}
```

**Response Format:**
```python
{
  "status": "success" | "error",
  "data": {
    "svg": str,              # SVG markup
    "dimensions": {
      "width": float,        # mm
      "height": float        # mm
    },
    "markers": int,          # Count
    "format": str
  },
  "error": str | null        # Error message if status="error"
}
```

---

## Database Models

### CalibrationPattern (calibration.py)

```python
class CalibrationPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(50))      # "charuco", "apriltag"
    board_size = db.Column(db.String(20))         # "7x5", etc.
    square_size_mm = db.Column(db.Float)
    marker_size_mm = db.Column(db.Float)
    dictionary = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    checksum = db.Column(db.String(32))           # MD5 for deduplication
    data = db.Column(db.Text)                     # JSON blob
```

### ValidationResult (validation.py)

```python
class ValidationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marker_id = db.Column(db.Integer)
    dictionary = db.Column(db.String(50))
    hamming_distance = db.Column(db.Integer)
    is_valid = db.Column(db.Boolean)
    quality_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime)
```

**Database Configuration:**
```python
# Development
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/aruco.db"

# Production (Docker)
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@db:5432/aruco_db"
```

---

## Frontend Architecture

### Page Load Sequence

1. Browser requests page (e.g., `/generate`)
2. Flask renders template extending `base.html`
3. `base.html` loads:
   - Bootstrap CSS
   - Custom CSS (main.css, navigation.css)
   - Bootstrap JS
   - Core JS modules (api, state, notifications, navigation)
4. Page template loads page-specific JS in `extra_js` block
5. Page JS initializes (e.g., `new GenerateManager()`)
6. JS uses `window.arucoAPI` to call backend

### JavaScript Modules

#### Core Modules (loaded by base.html)

**api.js**
```javascript
window.arucoAPI = {
  getDictionaries: async () => {...},
  generateMarkers: async (params) => {...},
  downloadMarkers: async (params, format) => {...}
}
```

**state.js**
```javascript
window.appState = {
  currentTab: null,
  formData: {},
  generationHistory: []
}
```

**notifications.js**
```javascript
window.showToast = (message, type) => {...}
```

#### Page Modules

**home.js (index.html)**
- `HomeManager` class
- Handles quick generation, dictionary selection
- Uses `window.arucoAPI` for backend calls

**generate.js (generate.html)**
- `GenerateManager` class
- Multi-step workflow
- Advanced parameter handling

**calibration.js (calibration.html)**
- ChArUco/AprilTag generation
- Camera calibration presets

**validation.js (validation.html)**
- Marker quality checking
- Hamming distance calculation

### State Management

**Client-Side State:**
```javascript
{
  currentGenerationData: {...},
  dictionaries: {...},
  presets: {...}
}
```

**Server-Side State:**
- Session-based (Flask sessions)
- Database persistence for patterns/results

---

## Testing

### Test Structure

```
tests/
├── test_api.py                 # API integration tests
├── test_api_endpoints.py       # Endpoint-specific tests
├── test_aruco_generator.py     # Unit tests for core logic
├── test_export_formats.py      # Export format validation
├── test_generation_quality.py  # Quality assurance tests
└── test_navigation.py          # UI/template tests
```

### Running Tests

```bash
# All tests
make test                # Lint + unit + integration
pytest tests/ -v         # Verbose output

# Specific test suites
make unit-test           # Unit tests only
make integration         # Integration tests only
make test-quality        # Quality tests
make test-export         # Export format tests

# Coverage
make coverage            # HTML + terminal report
pytest --cov=aruco_generator --cov-report=html
```

### Test Categories

**Unit Tests:**
- Core ArUCO generation
- Export format logic
- Drawing utilities
- Validation algorithms

**Integration Tests:**
- API endpoints
- Database operations
- Full generation workflows

**Quality Tests:**
- No line artifacts
- No gaps in merged rectangles
- Scaling preserves quality
- Grid alignment
- Export consistency

### Test Status

**Current:** 59 passing, 7 skipped (100% pass rate)

**Skipped Tests:**
- Advanced preview (requires specific setup)
- ChArUco board generation (OpenCV contrib)
- Negative validation tests (boundary conditions)
- Some LightBurn export tests (XML validation)

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd aruco-lightburn

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt  # or use Makefile

# Install pre-commit hooks
pre-commit install

# Initialize database
make db-init
```

### Development Server

```bash
# Flask development server (auto-reload)
flask run --debug

# Or Gunicorn with reload
make dev                 # Port 5000

# Production mode
make run                 # Gunicorn workers
```

### Code Quality

```bash
# Lint (flake8)
make lint

# Format (black)
make format

# Pre-commit checks
pre-commit run --all-files

# Full validation
make validate            # Lint + tests + quality
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes, commit often
git add .
git commit -m "feat: your feature"

# Run tests before push
make test

# Push and create PR
git push -u origin feature/your-feature
```

### Making Changes

**Backend (Python):**
1. Edit module in `aruco_generator/`
2. Run `make format` (black)
3. Run `make lint` (flake8)
4. Add/update tests in `tests/`
5. Run `make test`

**Frontend (JS/Templates):**
1. Edit template in `templates/`
2. Edit JS in `static/js/pages/`
3. Test in browser (dev server)
4. Check console for errors
5. Verify responsive design

**Database Changes:**
1. Update model definition
2. Create migration (if using Alembic)
3. Test migration up/down
4. Update tests

---

## Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t aruco-generator .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

**Services:**
- `app`: Flask application (port 5000)
- `db`: PostgreSQL database (port 5432)
- `nginx`: Reverse proxy (ports 80, 443) - optional

### Environment Variables

```bash
# Flask
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=<random-secret>

# Database
DATABASE_URL=postgresql://user:pass@db:5432/aruco_db
SQLALCHEMY_DATABASE_URI=<same-as-above>

# Server
PORT=5000
WORKERS=2
THREADS=2
```

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production database
- [ ] Enable HTTPS (nginx + cert)
- [ ] Set up monitoring (health checks)
- [ ] Configure logging (stderr/file)
- [ ] Enable firewall (restrict ports)
- [ ] Regular backups (database)
- [ ] Update dependencies (security patches)

### Deployment Platforms

**Supported:**
- Docker (any host)
- Vercel (Flask serverless)
- Railway (Docker)
- Render (Docker)
- Heroku (Docker/buildpack)
- AWS ECS/EKS (Docker)
- Google Cloud Run (Docker)

---

## Code Standards

### Python

**Style:**
- PEP 8 compliance
- **Line length**: 88 characters (Black default)
- Type hints encouraged
- Docstrings for public functions

**Tools:**
- **Formatter**: Black (88 chars)
- **Linter**: Flake8 (88 chars, ignore E501, W503)
- **Security**: Bandit (pre-commit hook)

**Example:**
```python
def generate_marker(
    dictionary: str,
    marker_id: int,
    size_mm: float = 50.0
) -> dict:
    """
    Generate ArUCO marker.

    Args:
        dictionary: ArUCO dictionary name
        marker_id: Marker ID (0-based)
        size_mm: Marker size in millimeters

    Returns:
        dict with 'svg', 'dimensions', 'format'
    """
    # Implementation...
```

### JavaScript

**Style:**
- ES6+ features (const, arrow functions, classes)
- **No build step** (vanilla JS, no webpack/babel)
- Bootstrap 5 components
- Module pattern (window globals)

**Example:**
```javascript
class HomeManager {
    constructor() {
        this.state = {};
        this.init();
    }

    async init() {
        await this.loadDictionaries();
        this.attachEventListeners();
    }

    async generateMarker(params) {
        const result = await window.arucoAPI.generateMarkers(params);
        return result;
    }
}
```

### Templates (Jinja2)

**Structure:**
```jinja
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block extra_css %}
<link href="{{ url_for('static', filename='css/page.css') }}" ...>
{% endblock %}

{% block content %}
<!-- Page content -->
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/page.js') }}">
</script>
{% endblock %}
```

### API Design

**RESTful Endpoints:**
- GET: Retrieve data (idempotent)
- POST: Create/generate (non-idempotent)
- JSON request/response
- Consistent error format

**Response Format:**
```json
{
  "status": "success",
  "data": {...},
  "error": null
}
```

**Error Response:**
```json
{
  "status": "error",
  "data": null,
  "error": "Description of error"
}
```

---

## Key Principles

### DRY (Don't Repeat Yourself)
- ✅ Eliminated 1,058 lines of duplicate code (static/app.js)
- ✅ Modular JS architecture (core + pages)
- ✅ Template inheritance (base.html)

### KISS (Keep It Simple, Stupid)
- ✅ Vanilla JavaScript (no complex framework)
- ✅ Flask (minimal, not Django)
- ✅ SQLite for dev, PostgreSQL for prod

### YAGNI (You Aren't Gonna Need It)
- ✅ No unnecessary features
- ✅ No premature optimization
- ✅ Simple architecture that scales

### Separation of Concerns
- ✅ Backend: Python modules by function
- ✅ Frontend: JS modules by page
- ✅ Templates: Inheritance hierarchy
- ✅ API: RESTful JSON interface

---

## Quick Reference

### Common Commands

```bash
# Development
make dev                 # Start dev server
make test                # Run tests
make format              # Format code
make lint                # Check style

# Docker
docker-compose up        # Start all services
docker-compose logs -f   # View logs
docker-compose down      # Stop services

# Database
make db-init             # Initialize database
python -c "from app import db; db.create_all()"

# Git
git checkout -b feature/name  # New branch
git commit -m "type: msg"     # Conventional commit
```

### File Locations

| What | Where |
|------|-------|
| Routes | `aruco_generator/web.py` |
| Core logic | `aruco_generator/aruco.py` |
| Templates | `templates/` |
| JavaScript | `static/js/` |
| CSS | `static/css/` |
| Tests | `tests/` |
| Docs | `docs/`, `*.md` |
| Config | `pyproject.toml`, `Makefile` |

### Port Numbers

| Service | Port |
|---------|------|
| Flask dev | 5000 |
| PostgreSQL | 5432 |
| Nginx HTTP | 80 |
| Nginx HTTPS | 443 |

---

**Last Updated**: 2025-11-18
**Version**: 2.0.0
**Python**: 3.11+
**Flask**: 3.1+

**For AI Assistants**: This file is the authoritative reference for project
structure. Always consult this file before making architectural changes.
