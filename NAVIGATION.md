# ArUCO Generator - Central Navigation Tree

## Repository Structure

```
ArUCO-LightBurn/
├── Core Application
│   ├── app.py                    # Flask app entry point
│   ├── models.py                 # SQLAlchemy database models
│   └── main.py                   # Production entry point
│
├── ArUCO Generator Package/
│   ├── __init__.py               # Package initialization with AI navigation
│   ├── aruco.py                  # Core marker generation (OpenCV)
│   ├── drawing.py                # SVG rendering and visualization
│   ├── web.py                    # Main API endpoints
│   ├── advanced_web.py           # Advanced features and coordinates
│   ├── calibration.py            # Camera calibration algorithms
│   ├── calibration_web.py        # Calibration API endpoints
│   ├── validation.py             # Quality validation and testing
│   ├── validation_web.py         # Validation API endpoints
│   ├── lightburn.py              # LightBurn export functionality
│   ├── exporters.py              # Multiple export format handlers
│   ├── aruco_fallback.py         # Fallback when OpenCV unavailable
│   └── batch.py                  # Batch processing utilities
│
├── Frontend Assets/
│   ├── templates/
│   │   ├── base.html             # Base template with navigation
│   │   ├── home.html             # Landing page
│   │   ├── generate.html         # Marker generation interface
│   │   ├── calibration.html      # Camera calibration UI
│   │   ├── validation.html       # Quality validation interface
│   │   └── documentation.html    # Help and documentation
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css          # Core styling
│   │   │   ├── navigation.css    # Navigation components
│   │   │   └── workflow.css      # Workflow-specific styles
│   │   └── js/
│   │       ├── core/
│   │       │   ├── api.js        # API communication layer
│   │       │   ├── state.js      # Application state management
│   │       │   ├── notifications.js # User feedback system
│   │       │   └── navigation-simple.js # Navigation utilities
│   │       └── pages/
│   │           ├── generate.js   # Generation page logic
│   │           └── validation.js # Validation page logic
│   └── app.js                    # Legacy main application JS
│
├── Testing Infrastructure/
│   ├── test_api.py               # API endpoint tests
│   ├── test_aruco_generator.py   # Core generation tests
│   ├── test_export_formats.py    # Export format validation
│   ├── test_generation_quality.py # Quality assurance tests
│   └── test_navigation.py        # Navigation and routing tests
│
├── Documentation/
│   ├── README.md                 # Main project documentation
│   ├── AI_IMPROVEMENT_OBJECTIVES.md # AI development guidelines
│   ├── IMPROVEMENT_PLAN.md       # Implementation roadmap
│   ├── replit.md                 # Replit-specific setup
│   └── docs/
│       └── GENERATION_QUALITY.md # Quality standards
│
├── Configuration/
│   ├── pyproject.toml            # Python project configuration
│   ├── uv.lock                   # Dependency lock file
│   ├── .replit                   # Replit environment config
│   ├── .pre-commit-config.yaml   # Pre-commit hooks
│   └── Makefile                  # Build and test automation
│
└── Artifacts/
    ├── instance/                 # Database files
    ├── export_lightburn.lbrn2    # Example LightBurn export
    ├── validate_quality.py       # Quality validation script
    └── *.png                     # Preview images
```

## Method and Class Navigation

### Core Python Classes

#### ArUCOGenerator (aruco.py)
```
ArUCOGenerator
├── __init__()                   # Initialize dictionaries and OpenCV
├── get_dictionary_info()        # Return available ArUCO dictionaries
├── generate_marker()            # Create single marker as numpy array
├── generate_grid()              # Create grid of markers with positions
├── calculate_total_size()       # Calculate grid dimensions
├── generate_with_coordinates()  # Generate with 3D coordinate metadata
├── generate_pose_estimation_board() # Optimized board for pose estimation
└── generate_charuco_board()     # ChArUco board for calibration
```

#### DrawingContext (drawing.py)
```
DrawingContext
├── __init__()                   # Initialize drawing elements and bounds
├── add_rectangle()              # Add rectangle shapes
├── add_marker_grid()            # Add ArUCO markers as filled rectangles
├── add_marker_grid_preview()    # Add markers with preview optimization
├── add_text_labels()            # Add text labels below markers
├── add_text()                   # Add text element
├── to_svg()                     # Alias for get_svg()
├── get_svg()                    # Generate SVG output
├── _update_bounds()             # Update drawing bounds
└── _find_merged_rectangles()    # Find merged rectangles for optimization
```

### API Endpoints Navigation

#### Main API Routes (web.py)
```
Flask Routes
├── /                           # Landing page
├── /generate                   # Generate markers page
├── /validation                 # Validation page
├── /documentation              # Documentation page
├── /api/dictionaries           # GET: Available ArUCO dictionaries
├── /api/preview               # POST: Generate SVG preview
├── /api/download              # POST: Generate and download LightBurn
├── /api/advanced_preview      # POST: Advanced preview with options
├── /api/batch_generate        # POST: Generate multiple sets
├── /api/presets               # GET: Predefined configurations
├── /api/export/svg            # POST: Export as SVG file
├── /api/export/pdf            # POST: Export as PDF (not implemented)
├── /api/quick-test            # GET: Quick API test
├── /api/debug/status          # GET: Debug status information
└── /api/log-error             # POST: Log frontend errors
```

#### Advanced API Routes (advanced_web.py)
```
Advanced Flask Routes
├── /api/advanced/preview                    # POST: Advanced preview features
├── /api/advanced/generate_with_coordinates  # POST: Generate with 3D coordinates
├── /api/advanced/pose_estimation_board      # POST: Pose estimation board
├── /api/export/opencv_yaml                  # POST: Export OpenCV YAML
├── /api/export/ros                          # POST: Export ROS format
├── /api/export/dxf                          # POST: Export DXF for CNC
├── /api/export/stl                          # POST: Export STL for 3D printing
├── /api/validation/test_pattern             # POST: Generate test pattern
├── /api/validation/verify_quality          # POST: Verify marker quality
├── /api/validation/hamming_distance         # POST: Calculate Hamming distance
├── /api/validation/detection_report         # POST: Generate detection report
└── /api/validation/batch_test               # POST: Batch validation tests
```

### Error Handling Patterns

#### Consistent Error Response Format
```json
{
  "error": "Error description",
  "details": "Optional additional details"
}
```

#### HTTP Status Codes Used
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource not found)
- `500` - Internal Server Error (unexpected errors)
- `501` - Not Implemented (features not yet available)

#### Self-Referential Error Messages
- "Please check your parameters and try again"
- "Failed to generate preview. Please check your parameters and try again"
- "Failed to export SVG file. Please check your parameters and try again"

### Database Models (models.py)

#### CalibrationPattern
```
CalibrationPattern
├── id                          # Primary key
├── name                        # Pattern name
├── dictionary                  # ArUCO dictionary used
├── marker_size_mm              # Physical marker size
├── grid_size                   # Grid dimensions
├── created_at                  # Creation timestamp
└── pattern_data                # JSON pattern configuration
```

#### DetectionMetric
```
DetectionMetric
├── id                          # Primary key
├── pattern_id                  # Foreign key to CalibrationPattern
├── detection_rate              # Success rate percentage
├── pose_error_mm               # Pose estimation error
├── lighting_conditions         # Test lighting conditions
└── timestamp                   # Measurement timestamp
```

## XML Navigation Descriptors

### Core Module Descriptors
```xml
<module name="aruco_generator" type="python_package">
  <description>Core ArUCO marker generation and processing</description>
  <entry_points>
    <primary>aruco.py</primary>
    <web_interface>web.py</web_interface>
    <advanced_features>advanced_web.py</advanced_features>
  </entry_points>
  <dependencies>
    <required>opencv-python, numpy, flask</required>
    <optional>postgresql, sqlalchemy</optional>
  </dependencies>
</module>
```

### API Navigation Descriptor
```xml
<api_structure type="rest">
  <base_url>/api</base_url>
  <endpoints>
    <group name="core">
      <endpoint path="/dictionaries" method="GET" purpose="list_dictionaries"/>
      <endpoint path="/preview" method="POST" purpose="generate_preview"/>
      <endpoint path="/download" method="POST" purpose="export_lightburn"/>
    </group>
    <group name="advanced">
      <endpoint path="/advanced/preview" method="POST" purpose="advanced_preview"/>
      <endpoint path="/export/opencv_yaml" method="POST" purpose="opencv_export"/>
      <endpoint path="/validation/test_pattern" method="POST" purpose="validation"/>
    </group>
  </endpoints>
</api_structure>
```

## AI Agent Navigation Guide

### Quick File Location Reference
- **Core Logic**: `aruco_generator/aruco.py` (line 100: generate_marker)
- **API Endpoints**: `aruco_generator/web.py` (line 55: generate_preview)
- **Error Handling**: Search for `return jsonify.*error` across web modules
- **Database Models**: `models.py` (line 15: CalibrationPattern class)
- **Frontend API**: `static/js/core/api.js` (line 20: API communication)

### Common Modification Patterns
1. **Adding New API Endpoint**: Add route in appropriate web module
2. **New ArUCO Feature**: Extend ArUCOGenerator class in aruco.py
3. **Frontend Enhancement**: Modify page-specific JS in static/js/pages/
4. **Test Addition**: Add test in appropriate test_*.py file
5. **Documentation Update**: Update this NAVIGATION.md and README.md

### Performance Optimization Areas
- **Empty Files**: backend/__init__.py (3 lines) - candidate for removal
- **Redundant Modules**: Consider consolidating validation_web.py into advanced_web.py
- **Frontend**: Legacy app.js could be refactored into modular core/ structure

---

*This navigation tree is maintained automatically. Last updated: v2.0.0-unified*
