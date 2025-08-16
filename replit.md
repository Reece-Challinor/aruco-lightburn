# ArUCO Generator - Professional Computer Vision Marker Creation Suite

## Overview

A comprehensive ArUCO marker generator designed for computer vision engineers, researchers, and robotics professionals. The application provides a three-tab interface for generating precise ArUCO markers, calibration patterns, and AprilTags with real-time preview and export to multiple industry-standard formats.

**Version 3.0** - Released August 16, 2025
- Three-tab architecture: Configuration, ArUco, and Advanced
- Support for all standard ArUco dictionaries (4x4, 5x5, 6x6, 7x7)
- Multiple export formats: LightBurn (.lbrn2), PDF, SVG, OpenCV YAML, ROS JSON
- Computer vision focused with industry-standard parameters
- Clean, streamlined interface with preserved purple gradient theme

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: Vanilla JavaScript ES6+ with Bootstrap 5 dark theme
- **UI Design Pattern**: Three-tab architecture (Configuration, ArUco, Advanced)
- **Tab Structure**:
  - **Configuration Tab**: ChArUco boards, AprilTag generation, detection validation
  - **ArUco Tab**: Quick ArUco marker generation with standard dictionaries
  - **Advanced Tab**: Full parameter control and customization
- **Error Handling**: Comprehensive client-side error logging with automatic backend reporting
- **Preview System**: Real-time SVG rendering with multi-format export support
- **Responsive Design**: Mobile-first with Bootstrap grid and purple gradient theme

### Backend Architecture
- **Framework**: Flask 3.0 with modular route organization across multiple files
- **Core Modules**: 
  - `aruco.py`: OpenCV-based marker generation with fallback support
  - `drawing.py`: SVG drawing context and rendering system
  - `lightburn.py`: LightBurn .lbrn2 XML export with material presets
  - `calibration.py`: ChArUco boards and AprilTag generation
  - `validation.py`: Detection quality assurance and metrics
- **API Design**: RESTful endpoints with JSON responses and comprehensive validation
- **Error Management**: Automatic logging to `debug_logs.txt` with stack traces and monitoring script

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