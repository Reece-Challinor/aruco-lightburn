"""
Simplified database models for ArUCO Generator
"""

from app import db
from datetime import datetime
from sqlalchemy import JSON
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model for authentication (if needed in future)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CalibrationPattern(db.Model):
    """Store generated calibration patterns and ArUCO markers"""
    __tablename__ = 'calibration_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(50), nullable=False)  # 'aruco_marker', 'charuco', 'aruco_board'
    pattern_name = db.Column(db.String(200))  # User-defined name
    
    # Physical dimensions
    physical_width_mm = db.Column(db.Float, nullable=False)
    physical_height_mm = db.Column(db.Float, nullable=False)
    marker_size_mm = db.Column(db.Float)
    
    # Pattern parameters
    grid_size_x = db.Column(db.Integer)  # Number of markers in X
    grid_size_y = db.Column(db.Integer)  # Number of markers in Y
    dictionary_type = db.Column(db.String(50))  # ARUCO dictionary type
    total_markers = db.Column(db.Integer)
    first_marker_id = db.Column(db.Integer, default=0)
    
    # Store generation parameters as JSON
    calibration_data = db.Column(JSON, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text)
    
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