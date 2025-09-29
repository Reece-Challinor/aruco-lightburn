# ArUCO Generator - Professional Computer Vision Marker Creation Suite

## Overview

A comprehensive ArUCO marker generator designed for computer vision engineers, researchers, and robotics professionals. The application provides a three-tab interface for generating precise ArUCO markers, calibration patterns, and AprilTags with real-time preview and export to multiple industry-standard formats.

**Version 4.1** - Quality Enhancement Update (September 29, 2025)
- Fixed line artifacts in generated markers through improved rectangle merging
- Enhanced preview generation to use same algorithm as export for consistency
- Added 0.01mm micro-overlaps to prevent gaps between merged regions
- Implemented comprehensive quality assurance test suite
- Added pre-commit hooks for automated quality checks
- Enhanced Makefile with validation targets for generation and export
- Created detailed technical documentation for quality standards

**Version 4.0** - Released August 16, 2025
- Enhanced navigation system with global navbar and breadcrumbs
- Dedicated pages: Home, Generate, Calibration, Validation, Documentation
- URL-based tab navigation with state persistence
- Responsive mobile-first design with touch controls
- Modular JavaScript architecture (navigation, API, state, notifications)
- Comprehensive test coverage for navigation and API endpoints
- Consistent purple gradient theme across all pages
- Keyboard shortcuts for quick navigation

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: Modular JavaScript ES6+ with Bootstrap 5 dark theme
- **Navigation System**: Global navbar with breadcrumbs and URL-based routing
- **Page Structure**:
  - **Home Page**: Landing with feature overview and quick start guide
  - **Generate Page**: Three tabs - Quick Generate, Advanced, Batch Generation
  - **Calibration Page**: ChArUco boards, AprilTag generation, calibration patterns
  - **Validation Page**: Detection testing, Hamming distance calculator, metrics
  - **Documentation Page**: Built-in help, API reference, best practices
- **JavaScript Modules**:
  - `core/navigation.js`: Global navigation and keyboard shortcuts
  - `core/api.js`: Centralized API client with error handling
  - `core/state.js`: Application state management with localStorage
  - `components/notifications.js`: Toast notifications and user feedback
  - `pages/generate.js`: Generation page logic
  - `pages/validation.js`: Validation page logic
- **Error Handling**: Comprehensive client-side error logging with automatic backend reporting
- **Preview System**: Real-time SVG rendering with multi-format export support
- **Responsive Design**: Mobile-first with touch-optimized controls and collapsible navigation

### Backend Architecture (Updated: August 17, 2025)

#### Comprehensive Enterprise-Ready Architecture Overhaul
- **Framework**: Flask 3.0 with modular Flask Blueprint architecture
- **API Structure**: Versioned RESTful API at `/api/v1/` with dedicated endpoints:
  - `/api/v1/auth/` - Authentication and user management
  - `/api/v1/markers/` - ArUCO marker generation and management  
  - `/api/v1/detection/` - Real-time marker detection and analysis
  - `/api/v1/calibration/` - Camera calibration tools and patterns
  - `/api/v1/export/` - Multi-format export (SVG, PDF, LightBurn, DXF)
  - `/api/v1/admin/` - Admin dashboard and user management
  - `/api/v1/health/` - Health checks, metrics, and system status

#### Enhanced Architecture Components
- **Service Layer Pattern**: Business logic separated into services:
  - `MarkerService`: Marker generation and batch processing
  - `DetectionService`: Real-time detection and quality analysis
  - `CalibrationService`: Camera calibration and pattern generation
  - `ExportService`: Multi-format export handling
- **Repository Pattern**: Database abstraction layer for data persistence
  - `MarkerRepository`: Marker CRUD operations and statistics
- **Input Validation**: Marshmallow schemas for automatic request validation
  - `MarkerGenerationSchema`: Validates marker generation parameters
  - `AuthSchema`: User authentication validation
  - All endpoints validate input automatically
- **Caching Layer**: Flask-Caching with Redis support
  - Configurable timeout and key prefixes
  - Cache invalidation strategies
  - Performance optimization for read-heavy operations
- **Async Task Processing**: Celery integration for background jobs
  - Batch marker generation
  - Export to multiple formats
  - Periodic cleanup tasks
- **Performance Monitoring**: Prometheus metrics integration
  - Request/response time tracking
  - API call counters
  - Error rate monitoring
  - Active task gauges
- **Request Middleware**: Comprehensive request processing
  - Request ID generation for tracing
  - Response compression
  - CORS headers for API endpoints
  - Request/response logging
- **Error Handling**: Structured exception handling
  - Custom exception classes
  - Proper HTTP status codes
  - Detailed error logging
  - Client-friendly error messages
- **OpenAPI/Swagger**: Self-documenting API (pending full activation)
  - Auto-generated documentation
  - Interactive API testing
  - Schema validation

#### Success Metrics
- ✅ 100% backwards compatible with existing routes
- ✅ Zero unhandled exceptions
- ✅ Automatic input validation on all API endpoints
- ✅ Predictable response times with caching
- ✅ Background task processing without blocking
- ✅ Comprehensive error handling with proper status codes
- **Legacy Route Modules** (Maintained for compatibility):
  - `web.py`: Main routes and home page
  - `calibration_web.py`: Calibration pattern routes
  - `advanced_web.py`: Advanced features and validation
  - `validation_web.py`: Validation, documentation, and generate pages
- **Core Generation Modules**: 
  - `aruco.py`: OpenCV-based marker generation with fallback support
  - `drawing.py`: SVG drawing context and rendering system
  - `lightburn.py`: LightBurn .lbrn2 XML export with material presets
  - `calibration.py`: ChArUco boards and AprilTag generation
  - `validation.py`: Detection quality assurance and metrics
- **Template System**: Base template inheritance with consistent navigation
- **API Design**: RESTful endpoints with JSON responses and comprehensive validation
- **Error Management**: Automatic logging to `debug_logs.txt` with stack traces and monitoring script
- **Testing**: Comprehensive test suites for navigation and API endpoints

### Data Storage Solutions
- **Primary Database**: PostgreSQL with SQLAlchemy ORM for production environments
- **Fallback Database**: SQLite for development and standalone deployments
- **Schema Design**: 
  - `calibration_patterns`: Store pattern configurations and metadata
  - `detection_metrics`: Track detection performance and quality metrics
  - `calibration_sessions`: Camera calibration results and parameters
- **Data Models**: JSON storage for calibration data with indexed tables for performance

### Authentication and Authorization
- **Security Model**: Session-based with configurable secret key
- **Access Control**: No authentication required for core functionality (open tool)
- **Input Validation**: Comprehensive server-side validation with real-time frontend feedback
- **XSS Protection**: HTML escaping utilities and safe innerHTML operations

### Export and Integration Systems
- **Multi-Format Export**: 
  - LightBurn (.lbrn2) - Laser cutting with material presets
  - PDF - Print-ready documents
  - SVG - Vector graphics for digital display
  - OpenCV YAML - Camera calibration data format
  - ROS JSON - Robot Operating System integration
- **Dictionary Support**: All standard ArUco dictionaries (4x4 through 7x7 with 50, 100, 250, 1000 marker variants)
- **Coordinate Systems**: 3D world coordinates with millimeter precision
- **Batch Processing**: Grid generation with customizable rows, columns, and spacing

## External Dependencies

### Core Computer Vision Libraries
- **OpenCV 4.9**: ArUCO marker generation, ChArUco boards, AprilTag support
- **NumPy**: Mathematical operations and array processing for marker data
- **Fallback System**: Pure Python ArUCO generation when OpenCV unavailable

### Web Framework and Database
- **Flask 3.0**: Web framework with Blueprint organization
- **Flask-SQLAlchemy**: ORM with PostgreSQL and SQLite support
- **Gunicorn**: WSGI server for production deployment
- **psycopg2-binary**: PostgreSQL database adapter

### Frontend Libraries (CDN)
- **Bootstrap 5**: UI framework with dark theme support
- **Bootstrap Icons**: Comprehensive icon library for enhanced UX

### Development and Debugging Tools
- **Debug Monitor Script**: System diagnostics and health checking (`debug_monitor.sh`)
- **Automatic Error Logging**: Frontend error capture with backend aggregation
- **Performance Monitoring**: Resource usage tracking and API endpoint testing

### Optional Production Services
- **PostgreSQL Database**: Recommended for production with connection pooling
- **Replit Hosting**: Optimized for Replit deployment with auto-scaling
- **Environment Variables**: Configurable database URLs and session secrets