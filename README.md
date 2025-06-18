# ArUCO Marker Generator for LightBurn

A streamlined Flask web application designed for computer vision engineers to quickly generate ArUCO markers and export them as LightBurn (.lbrn2) files for laser cutting on acrylic sheets.

## 🎯 Golden Path: Quick ArUCO Generation

**Primary Use Case**: Generate 2x2 ArUCO grids (1 column, 2 rows) for computer vision localization on laser-cut 1/16" acrylic sheets.

### Quick Start Features

- **One-Click Generation**: Instant 2x2 ArUCO grid with optimal defaults
- **Computer Vision Ready**: Configurable marker IDs for shelf localization
- **Laser-Optimized**: Pre-configured for 1/16" cast acrylic cutting
- **LightBurn Export**: Direct .lbrn2 export with material settings

### Advanced Features

- **Multiple ArUCO Dictionaries**: 16 dictionary types (4X4, 5X5, 6X6, 7X7)
- **Custom Grid Layouts**: Configurable rows, columns, and spacing
- **Batch Generation**: Multiple files with sequential IDs
- **Real-time Preview**: SVG preview with dimension calculations
- **Professional UI**: Clean, responsive interface with purple gradient theme

## 📁 Repository Structure & AI Navigation Map

```
aruco-lightburn/
├── 🔧 Core Configuration
│   ├── app.py                 # Flask app config & database setup
│   ├── main.py               # Application entry point
│   ├── pyproject.toml        # Python dependencies
│   ├── .replit              # Deployment configuration
│   └── uv.lock              # Dependency lock file
│
├── 🧠 ArUCO Generation Engine
│   └── aruco_generator/
│       ├── __init__.py       # Package initialization with module map
│       ├── aruco.py         # Core ArUCO generation (OpenCV)
│       ├── drawing.py       # SVG rendering & drawing context
│       ├── lightburn.py     # LightBurn .lbrn2 export engine
│       ├── batch.py         # Batch processing for multiple files
│       └── web.py           # Flask routes & API endpoints
│
├── 🎨 Frontend Interface
│   ├── templates/
│   │   └── index.html       # Main UI template (Simple/Advanced tabs)
│   └── static/
│       ├── app.js          # Frontend JavaScript controller
│       └── style.css       # UI styling with purple gradient theme
│
└── 📋 Documentation
    └── README.md           # This file - comprehensive guide
```

## 🔄 AI Agent Navigation Guide

### Primary Entry Points for Modifications

| **Task Type** | **Primary File** | **Related Files** | **Purpose** |
|---------------|------------------|-------------------|-------------|
| **Add New Routes** | `aruco_generator/web.py` | `static/app.js`, `templates/index.html` | API endpoints & UI integration |
| **ArUCO Logic** | `aruco_generator/aruco.py` | `aruco_generator/drawing.py` | Core marker generation |
| **UI Changes** | `templates/index.html` | `static/style.css`, `static/app.js` | Interface modifications |
| **Export Formats** | `aruco_generator/lightburn.py` | `aruco_generator/drawing.py` | New output formats |
| **Batch Processing** | `aruco_generator/batch.py` | `aruco_generator/web.py` | Multiple file operations |
| **App Configuration** | `app.py` | `main.py`, `.replit` | Flask setup & deployment |

### File Header JSON Schema

Each file contains a JSON header with:
- `file_type`: Classification of the file's role
- `purpose`: Brief description of functionality
- `dependencies`: Required imports/files
- `key_methods/routes`: Main functions or endpoints
- `ai_navigation`: Guidance for AI agents on when/how to modify

### Golden Path Architecture

The application is designed around a **golden path** user experience:
1. **Simple Tab**: One-click generation for common computer vision use cases
2. **Advanced Tab**: Full parameter control for specialized requirements
3. **Preview System**: Real-time SVG rendering with material settings
4. **Download Integration**: Direct LightBurn export with laser parameters

## 🚀 Technology Stack

- **Backend**: Python Flask with OpenCV for ArUCO generation
- **Frontend**: HTML5, JavaScript ES6, CSS3 with Bootstrap 5
- **Export**: LightBurn .lbrn2 format with material presets
- **Deployment**: Optimized for Replit with automatic port configuration
- **Database**: SQLAlchemy ORM (ready for future features)

## 🛠 Development Workflow

### For AI Agents & Developers

1. **Read File Headers**: Each file contains JSON metadata for navigation
2. **Follow Architecture**: Simple/Advanced tab separation for UX
3. **Maintain Documentation**: Update this README when adding features
4. **Use Golden Path**: Prioritize common use cases in UI design
5. **Test Integration**: Ensure frontend/backend API consistency

### Adding New Features

1. **Backend**: Add routes in `aruco_generator/web.py`
2. **Frontend**: Update `static/app.js` with new API calls
3. **UI**: Modify `templates/index.html` for new controls
4. **Styling**: Enhance `static/style.css` with consistent theming
5. **Documentation**: Update this README with new capabilities

## 📖 API Endpoints

| **Endpoint** | **Method** | **Purpose** | **Frontend Integration** |
|--------------|------------|-------------|-------------------------|
| `/` | GET | Main application page | Templates render |
| `/api/dictionaries` | GET | Available ArUCO dictionaries | Dropdown population |
| `/api/preview` | POST | Generate SVG preview | Real-time preview |
| `/api/download` | POST | Download LightBurn file | File download |
| `/api/quick-test` | POST | Quick test generation | One-click testing |
| `/api/quick-test/download` | POST | Download test file | Test file download |

## 🎨 Design Philosophy

**Simplicity First**: The landing page focuses on the most common use case - generating ArUCO markers for computer vision applications. Advanced features are accessible but not overwhelming.

**Golden Path Optimization**: 
- Default: Single ArUCO marker generation
- One-click: 2x2 grid generation  
- Quick test: Immediate laser cutting validation

**AI-Friendly Architecture**: JSON headers in files provide clear navigation for AI agents, reducing context switching and enabling autonomous development.

## 🔧 Material Presets

**Default Material**: 1/16" White/Black 2-Ply Cast Acrylic
- **Cut**: 150mm/min @ 75% power
- **Engrave**: 800mm/min @ 45% power  
- **Mark**: 1000mm/min @ 20% power

**Tip**: Engrave black side up for white markers

## 🚀 Quick Start

1. Open the application
2. Use **Simple** tab for quick generation
3. Click **"Generate Single"** for one marker
4. Click **"Generate 2x2 Grid"** for the golden path
5. Download LightBurn file and laser cut!

## 🔮 Future Development

This repository is designed for:
- **Rapid Feature Addition**: Clear file structure and AI navigation
- **UI Enhancement**: Modular frontend with consistent theming
- **Export Format Expansion**: Plugin architecture for new formats
- **Batch Processing**: Scalable generation for large projects
- **Material Library**: Expandable laser cutting presets

---

**Built for Computer Vision Engineers** | **Optimized for AI Agent Development** | **Streamlined for Production Use**