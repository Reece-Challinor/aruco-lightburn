# ArUCO Generator - Computer Vision Calibration Suite

## Overview

A professional ArUCO marker generator designed for computer vision applications, camera calibration, and laser cutting. The application provides a streamlined interface for generating precise ArUCO markers, ChArUco boards, and AprilTags with real-time preview and export to multiple professional formats including LightBurn, OpenCV YAML, ROS JSON, DXF, and STL.

The system follows a golden path UX design with simple one-click generation for common use cases and advanced parameter control for professional applications. Built with Flask backend and vanilla JavaScript frontend, optimized for performance with comprehensive error handling and validation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: Vanilla JavaScript ES6+ with Bootstrap 5 dark theme
- **UI Design Pattern**: Golden path UX with Simple/Advanced tab navigation
- **Error Handling**: Comprehensive client-side error logging with automatic backend reporting via `/api/log-error` endpoint
- **Preview System**: Real-time SVG rendering with optimized pixel sampling (10px base resolution for preview, 200px for export)
- **Responsive Design**: Mobile-first approach with Bootstrap grid system and custom purple gradient theme

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
- **LightBurn Integration**: Native .lbrn2 XML export with laser cutting parameters for 1/16" cast acrylic
- **Professional Formats**: OpenCV YAML, ROS JSON, DXF (CNC), STL (3D printing), PDF export capabilities
- **Coordinate Systems**: 3D world coordinates with millimeter precision for robotics applications
- **Batch Processing**: ZIP file generation for multiple markers with sequential ID ranges

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