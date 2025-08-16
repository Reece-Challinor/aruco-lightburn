"""
Database models for ArUCO Generator with calibration pattern tracking.
"""

from app import db
from datetime import datetime
from sqlalchemy import JSON

class CalibrationPattern(db.Model):
    """Track calibration patterns generated for computer vision applications."""
    __tablename__ = 'calibration_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(50), nullable=False)  # 'charuco', 'aruco_board', 'apriltag', 'apriltag_grid'
    pattern_name = db.Column(db.String(200))  # User-defined name for the pattern
    
    # Physical dimensions
    physical_width_mm = db.Column(db.Float, nullable=False)
    physical_height_mm = db.Column(db.Float, nullable=False)
    marker_size_mm = db.Column(db.Float)
    marker_separation_mm = db.Column(db.Float)
    
    # Pattern-specific parameters
    grid_size_x = db.Column(db.Integer)  # Number of markers/squares in X
    grid_size_y = db.Column(db.Integer)  # Number of markers/squares in Y
    dictionary_type = db.Column(db.String(50))  # ARUCO dictionary or AprilTag family
    total_markers = db.Column(db.Integer)
    first_marker_id = db.Column(db.Integer, default=0)
    
    # Calibration data stored as JSON
    calibration_data = db.Column(JSON, nullable=False)
    
    # File references
    image_checksum = db.Column(db.String(64))  # MD5 hash of generated image
    export_format = db.Column(db.String(20))  # 'yaml', 'json', 'ros', 'opencv'
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    detection_metrics = db.relationship('DetectionMetric', backref='pattern', lazy='dynamic', cascade='all, delete-orphan')
    calibration_sessions = db.relationship('CalibrationSession', backref='pattern', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CalibrationPattern {self.id}: {self.pattern_type} - {self.pattern_name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'pattern_type': self.pattern_type,
            'pattern_name': self.pattern_name,
            'physical_width_mm': self.physical_width_mm,
            'physical_height_mm': self.physical_height_mm,
            'marker_size_mm': self.marker_size_mm,
            'grid_size': [self.grid_size_x, self.grid_size_y],
            'dictionary_type': self.dictionary_type,
            'total_markers': self.total_markers,
            'calibration_data': self.calibration_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DetectionMetric(db.Model):
    """Track detection performance metrics for calibration patterns."""
    __tablename__ = 'detection_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.Integer, db.ForeignKey('calibration_patterns.id'), nullable=False)
    detection_rate = db.Column(db.Float)  # Percentage of markers detected (0-100)
    pose_error_mm = db.Column(db.Float)  # Average pose estimation error in mm
    lighting_conditions = db.Column(db.String(100))  # 'bright', 'normal', 'low', 'mixed'
    tested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<DetectionMetric {self.id}: Pattern {self.pattern_id} - {self.detection_rate}% detection>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'pattern_id': self.pattern_id,
            'detection_rate': self.detection_rate,
            'pose_error_mm': self.pose_error_mm,
            'lighting_conditions': self.lighting_conditions,
            'tested_at': self.tested_at.isoformat() if self.tested_at else None
        }


class CalibrationSession(db.Model):
    """Track camera calibration sessions using patterns."""
    __tablename__ = 'calibration_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.Integer, db.ForeignKey('calibration_patterns.id'), nullable=False)
    session_name = db.Column(db.String(200))
    
    # Camera information
    camera_model = db.Column(db.String(100))
    camera_resolution = db.Column(db.String(20))  # e.g., '1920x1080'
    camera_fps = db.Column(db.Integer)
    
    # Calibration results
    calibration_successful = db.Column(db.Boolean, default=False)
    rms_error = db.Column(db.Float)  # Root mean square reprojection error
    
    # Camera intrinsics (stored as JSON)
    camera_matrix = db.Column(JSON)  # 3x3 camera matrix
    distortion_coefficients = db.Column(JSON)  # Distortion coefficients
    
    # Calibration parameters
    num_images_used = db.Column(db.Integer)
    num_corners_detected = db.Column(db.Integer)
    calibration_flags = db.Column(db.Integer)  # OpenCV calibration flags
    
    # Extrinsics for fixed installations
    rotation_vector = db.Column(JSON)  # Rotation vector
    translation_vector = db.Column(JSON)  # Translation vector
    
    # Metadata
    calibrated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    calibration_software = db.Column(db.String(50))  # 'opencv', 'ros', 'matlab'
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CalibrationSession {self.id}: {self.session_name} - RMS: {self.rms_error}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'pattern_id': self.pattern_id,
            'session_name': self.session_name,
            'camera_model': self.camera_model,
            'calibration_successful': self.calibration_successful,
            'rms_error': self.rms_error,
            'camera_matrix': self.camera_matrix,
            'distortion_coefficients': self.distortion_coefficients,
            'calibrated_at': self.calibrated_at.isoformat() if self.calibrated_at else None
        }


class DroneLandingPattern(db.Model):
    """Specialized patterns for drone landing pads."""
    __tablename__ = 'drone_landing_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.Integer, db.ForeignKey('calibration_patterns.id'))
    
    # Landing pad specifications
    pad_size_m = db.Column(db.Float)  # Landing pad size in meters
    center_marker_size_mm = db.Column(db.Float)  # Center marker size
    outer_marker_size_mm = db.Column(db.Float)  # Outer ring markers
    
    # GPS coordinates for fixed installations
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude_m = db.Column(db.Float)
    
    # Pattern configuration
    num_concentric_rings = db.Column(db.Integer, default=1)
    markers_per_ring = db.Column(JSON)  # Array of marker counts per ring
    ring_radii_mm = db.Column(JSON)  # Array of ring radii
    
    # Environmental specifications
    material = db.Column(db.String(100))  # 'vinyl', 'painted_concrete', 'metal'
    weather_resistant = db.Column(db.Boolean, default=False)
    ir_reflective = db.Column(db.Boolean, default=False)
    
    # Detection ranges
    min_detection_altitude_m = db.Column(db.Float)
    max_detection_altitude_m = db.Column(db.Float)
    optimal_detection_altitude_m = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    installation_date = db.Column(db.Date)
    last_maintenance = db.Column(db.Date)
    
    def __repr__(self):
        return f'<DroneLandingPattern {self.id}: {self.pad_size_m}m pad>'