# ArUCO Marker Generator for LightBurn

A streamlined Flask web application designed for computer vision engineers to quickly generate ArUCO markers and export them as LightBurn (.lbrn2) files for laser cutting on acrylic sheets.

## Golden Path: Quick ArUCO Generation

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

## Design Philosophy

**Simplicity First**: The landing page focuses on the most common use case - generating ArUCO markers for computer vision applications. Advanced features are tucked away in an "Advanced" tab to reduce cognitive load.

**Golden Path Optimization**: 
- Default: Single ArUCO marker generation
- One-click: 2x2 grid generation
- Quick test: Immediate laser cutting validation

## Technology Stack

- **Backend**: Python Flask with OpenCV
- **Frontend**: HTML5, JavaScript, CSS3, Bootstrap 5
- **Export**: LightBurn .lbrn2 format with material presets
- **Deployment**: Optimized for Replit with automatic port configuration

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aruco-lightburn
